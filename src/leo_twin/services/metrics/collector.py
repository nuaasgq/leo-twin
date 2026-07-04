"""Read-only KPI collection and deterministic metrics output formatting."""

from __future__ import annotations

import csv
import io
import json
from collections import Counter, deque
from collections.abc import Mapping
from dataclasses import fields, is_dataclass
from math import isfinite
from pathlib import Path
from typing import Any, Protocol

from leo_twin.models.orbit import ground_track_point
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
        record_limit: int = 100_000,
        event_log_limit: int = 100_000,
        metric_sample_interval: int = 1,
        event_log_sample_interval: int = 1,
        event_log_segment_size: int | None = None,
        satellite_position_scale_to_km: float = 1.0,
    ) -> None:
        if not module_name:
            raise ValueError("module_name must be non-empty")
        if not metric_target:
            raise ValueError("metric_target must be non-empty")
        _require_positive_int(record_limit, "record_limit")
        _require_positive_int(event_log_limit, "event_log_limit")
        _require_positive_int(metric_sample_interval, "metric_sample_interval")
        _require_positive_int(event_log_sample_interval, "event_log_sample_interval")
        _require_optional_positive_int(
            event_log_segment_size,
            "event_log_segment_size",
        )
        _require_positive_number(
            satellite_position_scale_to_km,
            "satellite_position_scale_to_km",
        )

        self._module_name = module_name
        self._emit_metric_events = emit_metric_events
        self._metric_target = metric_target
        self._metric_sample_interval = metric_sample_interval
        self._event_log_sample_interval = event_log_sample_interval
        self._event_log_segment_size = event_log_segment_size
        self._satellite_position_scale_to_km = float(satellite_position_scale_to_km)
        self._records: deque[MetricRecord] = deque(maxlen=record_limit)
        self._event_log: deque[ReplayEvent] = deque(maxlen=event_log_limit)
        self._event_counts: Counter[str] = Counter()
        self._satellite_status: dict[str, str] = {}
        self._satellite_altitudes_km: dict[str, float] = {}
        self._links: dict[tuple[str, str], LinkState] = {}
        self._active_links: set[tuple[str, str]] = set()
        self._routes: dict[str, Route] = {}
        self._completed_flows: dict[str, str] = {}
        self._running_tasks: set[str] = set()
        self._task_start_times: dict[str, float] = {}
        self._task_durations: dict[str, float] = {}
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
        self._event_counts[event_type] += 1
        event_count = sum(self._event_counts.values())
        if _should_sample(event_count, self._event_log_sample_interval):
            self._event_log.append(_serialize_event(event))
        self._last_sim_time = event.sim_time

        records = [
            MetricRecord(
                metric_name="events.observed.count",
                sim_time=event.sim_time,
                entity_id="system",
                value=float(event_count),
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
        if not _should_sample(event_count, self._metric_sample_interval):
            return ()
        self._records.extend(records)
        return tuple(records)

    def records(self) -> tuple[MetricRecord, ...]:
        return tuple(self._records)

    def event_log(self) -> tuple[ReplayEvent, ...]:
        return tuple(dict(event) for event in self._event_log)

    def summary(self) -> MetricSummary:
        active_links = self._active_link_states()
        available_routes = self._available_routes()
        summary: MetricSummary = {
            "active_link_capacity_avg": _average(tuple(link.capacity for link in active_links)),
            "active_link_capacity_max": max((link.capacity for link in active_links), default=0.0),
            "active_link_capacity_min": min((link.capacity for link in active_links), default=0.0),
            "active_link_latency_avg": _average(tuple(link.latency for link in active_links)),
            "active_links": len(active_links),
            "available_link_capacity": self._available_link_capacity(),
            "completed_flows": len(self._completed_flows),
            "deadline_missed_tasks": self._deadline_missed_task_count(),
            "event_count": sum(self._event_counts.values()),
            "finished_tasks": len(self._finished_tasks),
            "last_sim_time": self._last_sim_time,
            "observed_links": len(self._links),
            "route_capacity_max": max((route.capacity for route in available_routes), default=0.0),
            "route_capacity_min": min((route.capacity for route in available_routes), default=0.0),
            "route_hop_count_avg": _average(
                tuple(float(_route_hop_count(route)) for route in available_routes)
            ),
            "route_hop_count_max": max(
                (_route_hop_count(route) for route in available_routes),
                default=0,
            ),
            "route_hop_count_min": min(
                (_route_hop_count(route) for route in available_routes),
                default=0,
            ),
            "route_latency_avg": _average(tuple(route.latency for route in available_routes)),
            "route_latency_min": min((route.latency for route in available_routes), default=0.0),
            "running_tasks": len(self._running_tasks),
            "routes_available": len(available_routes),
            "routes_total": len(self._routes),
            "satellite_altitude_avg": _average(
                tuple(
                    self._satellite_altitudes_km[satellite_id]
                    for satellite_id in sorted(self._satellite_altitudes_km)
                )
            ),
            "satellite_altitude_max": max(self._satellite_altitudes_km.values(), default=0.0),
            "satellite_altitude_min": min(self._satellite_altitudes_km.values(), default=0.0),
            "task_duration_avg": _average(
                tuple(
                    self._task_durations[task_id]
                    for task_id in sorted(self._task_durations)
                )
            ),
            "task_duration_max": max(self._task_durations.values(), default=0.0),
            "task_duration_min": min(self._task_durations.values(), default=0.0),
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
        return _events_jsonl(tuple(self._event_log))

    def events_jsonl_segments(
        self,
        events_per_segment: int | None = None,
    ) -> tuple[str, ...]:
        segment_size = (
            self._event_log_segment_size
            if events_per_segment is None
            else events_per_segment
        )
        if segment_size is None:
            segment_size = len(self._event_log) or 1
        _require_positive_int(segment_size, "events_per_segment")

        events = tuple(self._event_log)
        return tuple(
            _events_jsonl(events[index : index + segment_size])
            for index in range(0, len(events), segment_size)
        )

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
        if self._event_log_segment_size is not None:
            segment_files = self.write_segmented_event_log(output_path)
            files.update(
                {
                    f"events.segment.{index:06d}": path
                    for index, path in enumerate(segment_files, start=1)
                }
            )
        return files

    def write_segmented_event_log(
        self,
        output_dir: str | Path,
        events_per_segment: int | None = None,
    ) -> tuple[Path, ...]:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        files: list[Path] = []
        for index, segment in enumerate(
            self.events_jsonl_segments(events_per_segment),
            start=1,
        ):
            segment_path = output_path / f"events-{index:06d}.jsonl"
            segment_path.write_text(segment, encoding="utf-8")
            files.append(segment_path)
        return tuple(files)

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
        if event_type == EventType.METRIC_SAMPLE:
            return (_require_payload(event.payload, MetricRecord, "METRIC_SAMPLE"),)
        return ()

    def _observe_satellite(self, event: SimEvent) -> tuple[MetricRecord, ...]:
        state = _require_payload(event.payload, SatelliteState, "ORBIT_UPDATE")
        metric_state = self._satellite_state_for_metrics(state)
        point = ground_track_point(metric_state)
        self._satellite_status[state.satellite_id] = state.status
        self._satellite_altitudes_km[state.satellite_id] = point.altitude_km
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
            MetricRecord(
                metric_name="satellite.latitude_deg",
                sim_time=event.sim_time,
                entity_id=state.satellite_id,
                value=float(point.latitude_deg),
                tags=(("status", state.status),),
            ),
            MetricRecord(
                metric_name="satellite.longitude_deg",
                sim_time=event.sim_time,
                entity_id=state.satellite_id,
                value=float(point.longitude_deg),
                tags=(("status", state.status),),
            ),
            MetricRecord(
                metric_name="satellite.altitude_km",
                sim_time=event.sim_time,
                entity_id=state.satellite_id,
                value=float(point.altitude_km),
                tags=(("status", state.status),),
            ),
        )

    def _satellite_state_for_metrics(self, state: SatelliteState) -> SatelliteState:
        if self._satellite_position_scale_to_km == 1.0:
            return state
        return SatelliteState(
            satellite_id=state.satellite_id,
            sim_time=state.sim_time,
            position=tuple(
                value * self._satellite_position_scale_to_km
                for value in state.position
            ),
            velocity=tuple(
                value * self._satellite_position_scale_to_km
                for value in state.velocity
            ),
            status=state.status,
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
                metric_name="route.hop_count",
                sim_time=event.sim_time,
                entity_id=route.route_id,
                value=float(_route_hop_count(route)),
                tags=(("flow_id", route.flow_id),),
            ),
            MetricRecord(
                metric_name="route.path",
                sim_time=event.sim_time,
                entity_id=route.route_id,
                value=" -> ".join(route.path),
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
            self._task_start_times[task.task_id] = task.sim_time
        else:
            self._running_tasks.discard(task.task_id)
            self._finished_tasks[task.task_id] = task.status
            self._task_durations[task.task_id] = max(
                0.0,
                task.sim_time - self._task_start_times.get(task.task_id, task.sim_time),
            )

        records = [
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
            MetricRecord(
                metric_name="tasks.deadline_missed.count",
                sim_time=event.sim_time,
                entity_id="system",
                value=float(self._deadline_missed_task_count()),
            ),
        ]
        if event_type == EventType.TASK_FINISH:
            records.append(
                MetricRecord(
                    metric_name="task.duration",
                    sim_time=event.sim_time,
                    entity_id=task.task_id,
                    value=float(self._task_durations[task.task_id]),
                    tags=(("node_id", task.node_id), ("status", task.status)),
                )
            )
        return tuple(records)

    def _available_link_capacity(self) -> float:
        return float(
            sum(
                self._links[key].capacity
                for key in sorted(self._active_links)
                if key in self._links and self._links[key].availability
            )
        )

    def _active_link_states(self) -> tuple[LinkState, ...]:
        return tuple(
            self._links[key]
            for key in sorted(self._active_links)
            if key in self._links and self._links[key].availability
        )

    def _available_routes(self) -> tuple[Route, ...]:
        return tuple(
            self._routes[route_id]
            for route_id in sorted(self._routes)
            if self._routes[route_id].available
        )

    def _deadline_missed_task_count(self) -> int:
        return sum(
            1
            for status in self._finished_tasks.values()
            if status.upper() == "DEADLINE_MISSED"
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


def _route_hop_count(route: Route) -> int:
    return max(0, len(route.path) - 1)


def _json_scalar(value: str | int | float | bool) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _events_jsonl(events: tuple[ReplayEvent, ...]) -> str:
    if not events:
        return ""
    lines = [
        json.dumps(event, sort_keys=True, separators=(",", ":"))
        for event in events
    ]
    return "\n".join(lines) + "\n"


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


def _should_sample(count: int, interval: int) -> bool:
    return count == 1 or count % interval == 0


def _average(values: tuple[float, ...]) -> float:
    if not values:
        return 0.0
    return float(sum(values) / len(values))


def _require_optional_positive_int(value: int | None, field_name: str) -> None:
    if value is None:
        return
    _require_positive_int(value, field_name)


def _require_positive_int(value: int, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field_name} must be an int")
    if value <= 0:
        raise ValueError(f"{field_name} must be positive")


def _require_positive_number(value: float, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field_name} must be a number")
    if not isfinite(value) or value <= 0.0:
        raise ValueError(f"{field_name} must be finite and positive")
