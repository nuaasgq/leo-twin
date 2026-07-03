"""Read-only KPI collection and deterministic metrics output formatting."""

from __future__ import annotations

import csv
import io
import json
from collections import Counter
from collections.abc import Mapping
from dataclasses import fields, is_dataclass
from pathlib import Path
from typing import Any, Protocol

from leo_twin.schema import (
    EventType,
    FlowState,
    LinkState,
    MetricRecord,
    Route,
    SatelliteState,
    SimEvent,
    TaskState,
)


MetricSummary = dict[str, str | float | int | bool]
ReplayPayload = str | int | float | bool | None | list["ReplayPayload"] | dict[str, "ReplayPayload"]
ReplayEvent = dict[str, ReplayPayload]

_CSV_FIELDS = ("sim_time", "metric_name", "entity_id", "value", "tags")


class _MetricEventScheduler(Protocol):
    def schedule_event(self, event: SimEvent) -> None:
        ...


class MetricsCollector:
    """Collect system-wide KPIs from SimEvent observations.

    The collector is intentionally passive: every state change is limited to
    its own metric and replay buffers. When sample event emission is enabled,
    only METRIC_SAMPLE events are scheduled.
    """

    def __init__(
        self,
        module_name: str = "metrics",
        *,
        emit_metric_events: bool = False,
        metric_target: str = "adapters",
    ) -> None:
        if not module_name:
            raise ValueError("module_name must be non-empty")
        if not metric_target:
            raise ValueError("metric_target must be non-empty")

        self._module_name = module_name
        self._emit_metric_events = emit_metric_events
        self._metric_target = metric_target
        self._records: list[MetricRecord] = []
        self._event_log: list[ReplayEvent] = []
        self._event_counts: Counter[str] = Counter()
        self._satellite_status: dict[str, str] = {}
        self._links: dict[tuple[str, str], LinkState] = {}
        self._active_links: set[tuple[str, str]] = set()
        self._routes: dict[str, Route] = {}
        self._completed_flows: dict[str, str] = {}
        self._running_tasks: set[str] = set()
        self._finished_tasks: dict[str, str] = {}
        self._last_sim_time = 0.0
        self._metric_event_sequence = 0

    def name(self) -> str:
        return self._module_name

    def on_event(self, event: SimEvent, kernel: _MetricEventScheduler) -> None:
        """Observe one event and optionally emit METRIC_SAMPLE records."""

        new_records = self.observe(event)
        if not self._emit_metric_events:
            return

        for record in new_records:
            kernel.schedule_event(self._metric_event(event, record))

    def observe(self, event: SimEvent) -> tuple[MetricRecord, ...]:
        """Observe one event outside the kernel dispatch path."""

        event_type = _event_type_name(event.event_type)
        self._event_log.append(_serialize_event(event))
        self._event_counts[event_type] += 1
        self._last_sim_time = event.sim_time

        records = [
            MetricRecord(
                metric_name="events.observed.count",
                sim_time=event.sim_time,
                entity_id="system",
                value=float(sum(self._event_counts.values())),
                tags=(
                    ("event_type", event_type),
                    ("source", event.source),
                    ("target", event.target),
                ),
            ),
            MetricRecord(
                metric_name=f"events.{event_type}.count",
                sim_time=event.sim_time,
                entity_id="system",
                value=float(self._event_counts[event_type]),
                tags=(("event_type", event_type),),
            ),
        ]
        records.extend(self._payload_records(event, event_type))
        self._records.extend(records)
        return tuple(records)

    def records(self) -> tuple[MetricRecord, ...]:
        return tuple(self._records)

    def event_log(self) -> tuple[ReplayEvent, ...]:
        return tuple(dict(event) for event in self._event_log)

    def summary(self) -> MetricSummary:
        summary: MetricSummary = {
            "active_links": len(self._active_links),
            "available_link_capacity": self._available_link_capacity(),
            "completed_flows": len(self._completed_flows),
            "event_count": sum(self._event_counts.values()),
            "finished_tasks": len(self._finished_tasks),
            "last_sim_time": self._last_sim_time,
            "observed_links": len(self._links),
            "running_tasks": len(self._running_tasks),
            "routes_available": sum(1 for route in self._routes.values() if route.available),
            "routes_total": len(self._routes),
            "unique_satellites": len(self._satellite_status),
        }
        for event_type, count in sorted(self._event_counts.items()):
            summary[f"events.{event_type}.count"] = count
        return summary

    def metrics_csv(self) -> str:
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=_CSV_FIELDS, lineterminator="\n")
        writer.writeheader()
        for record in self._records:
            writer.writerow(
                {
                    "sim_time": _json_scalar(record.sim_time),
                    "metric_name": record.metric_name,
                    "entity_id": record.entity_id,
                    "value": _json_scalar(record.value),
                    "tags": json.dumps(
                        dict(record.tags),
                        sort_keys=True,
                        separators=(",", ":"),
                    ),
                }
            )
        return output.getvalue()

    def summary_json(self) -> str:
        return json.dumps(self.summary(), sort_keys=True, indent=2) + "\n"

    def events_jsonl(self) -> str:
        if not self._event_log:
            return ""
        lines = [
            json.dumps(event, sort_keys=True, separators=(",", ":"))
            for event in self._event_log
        ]
        return "\n".join(lines) + "\n"

    def write_outputs(self, output_dir: str | Path) -> Mapping[str, Path]:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        files = {
            "events": output_path / "events.jsonl",
            "metrics": output_path / "metrics.csv",
            "summary": output_path / "summary.json",
        }
        files["events"].write_text(self.events_jsonl(), encoding="utf-8")
        files["metrics"].write_text(self.metrics_csv(), encoding="utf-8")
        files["summary"].write_text(self.summary_json(), encoding="utf-8")
        return files

    def _payload_records(self, event: SimEvent, event_type: str) -> tuple[MetricRecord, ...]:
        if event_type == EventType.ORBIT_UPDATE:
            return self._observe_satellite(event)
        if event_type in {
            EventType.ACCESS_START,
            EventType.ACCESS_END,
            EventType.LINK_UPDATE,
        }:
            return self._observe_link(event, event_type)
        if event_type == EventType.ROUTE_UPDATE:
            return self._observe_route(event)
        if event_type == EventType.FLOW_COMPLETE:
            return self._observe_flow(event)
        if event_type in {EventType.TASK_START, EventType.TASK_FINISH}:
            return self._observe_task(event, event_type)
        return ()

    def _observe_satellite(self, event: SimEvent) -> tuple[MetricRecord, ...]:
        state = _require_payload(event.payload, SatelliteState, "ORBIT_UPDATE")
        self._satellite_status[state.satellite_id] = state.status
        return (
            MetricRecord(
                metric_name="satellites.observed.count",
                sim_time=event.sim_time,
                entity_id="system",
                value=float(len(self._satellite_status)),
            ),
            MetricRecord(
                metric_name="satellite.status",
                sim_time=event.sim_time,
                entity_id=state.satellite_id,
                value=state.status,
                tags=(("status", state.status),),
            ),
        )

    def _observe_link(self, event: SimEvent, event_type: str) -> tuple[MetricRecord, ...]:
        link = _require_payload(event.payload, LinkState, event_type)
        link_id = _link_id(link)
        link_key = (link.source_id, link.target_id)
        self._links[link_key] = link

        if event_type == EventType.ACCESS_END or not link.availability:
            self._active_links.discard(link_key)
        else:
            self._active_links.add(link_key)

        return (
            MetricRecord(
                metric_name="link.availability",
                sim_time=event.sim_time,
                entity_id=link_id,
                value=link.availability,
            ),
            MetricRecord(
                metric_name="link.capacity",
                sim_time=event.sim_time,
                entity_id=link_id,
                value=float(link.capacity),
            ),
            MetricRecord(
                metric_name="link.latency",
                sim_time=event.sim_time,
                entity_id=link_id,
                value=float(link.latency),
            ),
            MetricRecord(
                metric_name="links.active.count",
                sim_time=event.sim_time,
                entity_id="system",
                value=float(len(self._active_links)),
            ),
            MetricRecord(
                metric_name="links.available_capacity.total",
                sim_time=event.sim_time,
                entity_id="system",
                value=self._available_link_capacity(),
            ),
        )

    def _observe_route(self, event: SimEvent) -> tuple[MetricRecord, ...]:
        route = _require_payload(event.payload, Route, "ROUTE_UPDATE")
        self._routes[route.route_id] = route
        return (
            MetricRecord(
                metric_name="route.available",
                sim_time=event.sim_time,
                entity_id=route.route_id,
                value=route.available,
                tags=(("flow_id", route.flow_id),),
            ),
            MetricRecord(
                metric_name="route.capacity",
                sim_time=event.sim_time,
                entity_id=route.route_id,
                value=float(route.capacity),
                tags=(("flow_id", route.flow_id),),
            ),
            MetricRecord(
                metric_name="route.latency",
                sim_time=event.sim_time,
                entity_id=route.route_id,
                value=float(route.latency),
                tags=(("flow_id", route.flow_id),),
            ),
            MetricRecord(
                metric_name="routes.total.count",
                sim_time=event.sim_time,
                entity_id="system",
                value=float(len(self._routes)),
            ),
            MetricRecord(
                metric_name="routes.available.count",
                sim_time=event.sim_time,
                entity_id="system",
                value=float(sum(1 for item in self._routes.values() if item.available)),
            ),
        )

    def _observe_flow(self, event: SimEvent) -> tuple[MetricRecord, ...]:
        flow = _require_payload(event.payload, FlowState, "FLOW_COMPLETE")
        self._completed_flows[flow.flow_id] = flow.status
        return (
            MetricRecord(
                metric_name="flow.status",
                sim_time=event.sim_time,
                entity_id=flow.flow_id,
                value=flow.status,
                tags=(("route_id", flow.route_id), ("status", flow.status)),
            ),
            MetricRecord(
                metric_name="flows.completed.count",
                sim_time=event.sim_time,
                entity_id="system",
                value=float(len(self._completed_flows)),
            ),
        )

    def _observe_task(self, event: SimEvent, event_type: str) -> tuple[MetricRecord, ...]:
        task = _require_payload(event.payload, TaskState, event_type)
        if event_type == EventType.TASK_START:
            self._running_tasks.add(task.task_id)
        else:
            self._running_tasks.discard(task.task_id)
            self._finished_tasks[task.task_id] = task.status

        return (
            MetricRecord(
                metric_name="task.progress",
                sim_time=event.sim_time,
                entity_id=task.task_id,
                value=float(task.progress),
                tags=(("node_id", task.node_id), ("status", task.status)),
            ),
            MetricRecord(
                metric_name="tasks.running.count",
                sim_time=event.sim_time,
                entity_id="system",
                value=float(len(self._running_tasks)),
            ),
            MetricRecord(
                metric_name="tasks.finished.count",
                sim_time=event.sim_time,
                entity_id="system",
                value=float(len(self._finished_tasks)),
            ),
        )

    def _available_link_capacity(self) -> float:
        return float(
            sum(
                self._links[key].capacity
                for key in sorted(self._active_links)
                if key in self._links and self._links[key].availability
            )
        )

    def _metric_event(self, observed_event: SimEvent, record: MetricRecord) -> SimEvent:
        self._metric_event_sequence += 1
        return SimEvent(
            event_id=f"{self._module_name}:metric:{self._metric_event_sequence:08d}",
            sim_time=observed_event.sim_time,
            priority=observed_event.priority,
            source=self._module_name,
            target=self._metric_target,
            event_type=EventType.METRIC_SAMPLE,
            payload=record,
        )


def _require_payload(payload: object, expected_type: type[Any], event_type: str) -> Any:
    if isinstance(payload, expected_type):
        return payload
    raise TypeError(f"{event_type} payload must be {expected_type.__name__}")


def _event_type_name(event_type: object) -> str:
    if isinstance(event_type, EventType):
        return event_type.value
    return str(event_type)


def _link_id(link: LinkState) -> str:
    return f"{link.source_id}->{link.target_id}"


def _json_scalar(value: str | int | float | bool) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _serialize_event(event: SimEvent) -> ReplayEvent:
    return {
        "event_id": _json_payload(event.event_id),
        "event_type": _event_type_name(event.event_type),
        "payload": _json_payload(event.payload),
        "payload_type": type(event.payload).__name__ if event.payload is not None else "None",
        "priority": event.priority,
        "sim_time": event.sim_time,
        "source": event.source,
        "target": event.target,
    }


def _json_payload(value: object) -> ReplayPayload:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, EventType):
        return value.value
    if is_dataclass(value) and not isinstance(value, type):
        return {
            field.name: _json_payload(getattr(value, field.name))
            for field in fields(value)
        }
    if isinstance(value, Mapping):
        return {
            str(key): _json_payload(value[key])
            for key in sorted(value, key=lambda item: str(item))
        }
    if isinstance(value, tuple | list):
        return [_json_payload(item) for item in value]
    raise TypeError(f"payload is not deterministic JSON serializable: {type(value).__name__}")
