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
    ComputeNodeState,
    EventType,
    FlowState,
    LinkState,
    MetricRecord,
    OrbitBatchState,
    Route,
    SatelliteState,
    SimEvent,
    TaskState,
)
from leo_twin.models.compute.contracts import COMPUTE_NODE_UPDATE


MetricSummary = dict[str, str | float | int | bool]
KpiSample = dict[str, float]
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
        kpi_sample_limit: int = 240,
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
        _require_positive_int(kpi_sample_limit, "kpi_sample_limit")
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
        self._kpi_samples: deque[KpiSample] = deque(maxlen=kpi_sample_limit)
        self._event_counts: Counter[str] = Counter()
        self._satellite_status: dict[str, str] = {}
        self._satellite_altitudes_km: dict[str, float] = {}
        self._satellite_state_updates = 0
        self._orbit_batch_updates = 0
        self._last_orbit_update_time = 0.0
        self._last_orbit_batch_size = 0
        self._orbit_event_reduction_ratio = 1.0
        self._links: dict[tuple[str, str], LinkState] = {}
        self._active_links: set[tuple[str, str]] = set()
        self._routes: dict[str, Route] = {}
        self._route_latency_history: dict[str, deque[float]] = {}
        self._completed_flows: dict[str, FlowState] = {}
        self._compute_nodes: dict[str, ComputeNodeState] = {}
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
        self._append_kpi_sample(event.sim_time, event_type)
        records.extend(self._derived_metric_records(event.sim_time, event_type))
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
            "last_orbit_update_time": self._last_orbit_update_time,
            "observed_links": len(self._links),
            "orbit_batch_updates": self._orbit_batch_updates,
            "orbit_event_reduction_ratio": self._orbit_event_reduction_ratio,
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
            "satellite_count": len(self._satellite_status),
            "satellite_state_updates": self._satellite_state_updates,
            "batch_size": self._last_orbit_batch_size,
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
        summary.update(self._network_quality_summary(active_links, available_routes))
        summary.update(self._compute_resource_summary())
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

    def kpi_time_series(self) -> dict[str, str | int | list[KpiSample]]:
        samples = [dict(sample) for sample in self._kpi_samples]
        if not samples:
            samples = [self._current_kpi_sample(self._last_sim_time)]
        return {
            "version": "v1",
            "sample_count": len(samples),
            "samples": samples,
        }

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
        if event_type == EventType.ORBIT_BATCH_UPDATE:
            return self._observe_satellite_batch(event)
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
        if event_type == COMPUTE_NODE_UPDATE:
            return self._observe_compute_node(event)
        if event_type == EventType.METRIC_SAMPLE:
            return (_require_payload(event.payload, MetricRecord, "METRIC_SAMPLE"),)
        return ()

    def _derived_metric_records(
        self,
        sim_time: float,
        event_type: str,
    ) -> tuple[MetricRecord, ...]:
        records: list[MetricRecord] = []
        if event_type in {
            EventType.ACCESS_START,
            EventType.ACCESS_END,
            EventType.LINK_UPDATE,
            EventType.ROUTE_UPDATE,
            EventType.FLOW_COMPLETE,
        }:
            summary = self._network_quality_summary(
                self._active_link_states(),
                self._available_routes(),
            )
            fields = (
                (
                    "network.quality.effective_throughput_mbps",
                    "network_quality_effective_throughput_mbps",
                ),
                (
                    "network.quality.effective_latency_s",
                    "network_quality_effective_latency_avg_s",
                ),
                (
                    "network.quality.effective_loss_proxy_rate",
                    "network_quality_effective_loss_proxy_rate",
                ),
                (
                    "network.quality.effective_delay_variation_s",
                    "network_quality_effective_delay_variation_proxy_s",
                ),
            )
            records.extend(
                MetricRecord(
                    metric_name=metric_name,
                    sim_time=sim_time,
                    entity_id="system",
                    value=float(summary[summary_key]),
                    tags=(("source", "metrics_summary"),),
                )
                for metric_name, summary_key in fields
            )
        if event_type == COMPUTE_NODE_UPDATE:
            compute_summary = self._compute_resource_summary()
            records.append(
                MetricRecord(
                    metric_name="compute.resource.used_gflops_fp32",
                    sim_time=sim_time,
                    entity_id="system",
                    value=float(compute_summary["compute_resource_used_gflops_fp32"]),
                    tags=(("source", "metrics_summary"),),
                )
            )
        return tuple(records)

    def _append_kpi_sample(self, sim_time: float, event_type: str) -> None:
        if not _is_kpi_sample_event_type(event_type):
            return
        sample = self._current_kpi_sample(sim_time)
        if self._kpi_samples and self._kpi_samples[-1]["sim_time"] == sample["sim_time"]:
            self._kpi_samples[-1] = sample
            return
        self._kpi_samples.append(sample)

    def _current_kpi_sample(self, sim_time: float) -> KpiSample:
        network_summary = self._network_quality_summary(
            self._active_link_states(),
            self._available_routes(),
        )
        compute_summary = self._compute_resource_summary()
        return {
            "sim_time": float(sim_time),
            "network_effective_throughput_mbps": float(
                network_summary["network_quality_effective_throughput_mbps"]
            ),
            "network_requested_route_demand_mbps": float(
                network_summary["network_quality_requested_route_demand_mbps"]
            ),
            "network_demand_pressure_proxy": float(
                network_summary["network_quality_demand_pressure_proxy"]
            ),
            "network_effective_latency_s": float(
                network_summary["network_quality_effective_latency_avg_s"]
            ),
            "network_effective_loss_proxy_rate": float(
                network_summary["network_quality_effective_loss_proxy_rate"]
            ),
            "network_effective_delay_variation_s": float(
                network_summary["network_quality_effective_delay_variation_proxy_s"]
            ),
            "compute_resource_used_gflops_fp32": float(
                compute_summary["compute_resource_used_gflops_fp32"]
            ),
        }

    def _observe_satellite(self, event: SimEvent) -> tuple[MetricRecord, ...]:
        state = _require_payload(event.payload, SatelliteState, "ORBIT_UPDATE")
        metric_state = self._satellite_state_for_metrics(state)
        point = ground_track_point(metric_state)
        self._satellite_status[state.satellite_id] = state.status
        self._satellite_altitudes_km[state.satellite_id] = point.altitude_km
        self._satellite_state_updates += 1
        self._last_orbit_update_time = event.sim_time
        self._last_orbit_batch_size = 1
        self._orbit_event_reduction_ratio = 1.0
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

    def _observe_satellite_batch(self, event: SimEvent) -> tuple[MetricRecord, ...]:
        batch = _require_payload(event.payload, OrbitBatchState, "ORBIT_BATCH_UPDATE")
        for state in batch.satellite_states:
            metric_state = self._satellite_state_for_metrics(state)
            point = ground_track_point(metric_state)
            self._satellite_status[state.satellite_id] = state.status
            self._satellite_altitudes_km[state.satellite_id] = point.altitude_km

        self._satellite_state_updates += batch.satellite_count
        self._orbit_batch_updates += 1
        self._last_orbit_update_time = batch.sim_time
        self._last_orbit_batch_size = batch.satellite_count
        self._orbit_event_reduction_ratio = float(max(1, batch.satellite_count))
        tags = (("event_type", EventType.ORBIT_BATCH_UPDATE.value),)
        return (
            MetricRecord(
                metric_name="satellite_count",
                sim_time=batch.sim_time,
                entity_id="orbit",
                value=float(len(self._satellite_status)),
                tags=tags,
            ),
            MetricRecord(
                metric_name="last_orbit_update_time",
                sim_time=batch.sim_time,
                entity_id="orbit",
                value=float(batch.sim_time),
                tags=tags,
            ),
            MetricRecord(
                metric_name="batch_size",
                sim_time=batch.sim_time,
                entity_id="orbit",
                value=float(batch.satellite_count),
                tags=tags,
            ),
            MetricRecord(
                metric_name="orbit_event_reduction_ratio",
                sim_time=batch.sim_time,
                entity_id="orbit",
                value=self._orbit_event_reduction_ratio,
                tags=tags,
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
        history = self._route_latency_history.setdefault(route.route_id, deque(maxlen=16))
        history.append(float(route.latency))
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
        self._completed_flows[flow.flow_id] = flow
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

    def _observe_compute_node(self, event: SimEvent) -> tuple[MetricRecord, ...]:
        node = _require_payload(event.payload, ComputeNodeState, COMPUTE_NODE_UPDATE)
        self._compute_nodes[node.node_id] = node
        return ()

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

    def _network_quality_summary(
        self,
        active_links: tuple[LinkState, ...],
        available_routes: tuple[Route, ...],
    ) -> MetricSummary:
        route_latencies = tuple(route.latency for route in available_routes)
        route_latency_avg = _average(route_latencies)
        delay_variation_proxy = max(
            _standard_deviation(route_latencies),
            self._route_latency_delta_average(),
        )
        unavailable_routes = max(0, len(self._routes) - len(available_routes))
        route_blocking_ratio = (
            0.0 if not self._routes else unavailable_routes / len(self._routes)
        )
        failed_flow_ratio = self._failed_flow_ratio()
        congestion_proxy = _average(
            tuple(
                float(link.utilization)
                for link in active_links
                if link.utilization is not None
            )
        )
        route_loss_proxy_rate = _average(
            tuple(
                float(route.loss_rate)
                for route in self._routes.values()
                if route.loss_rate is not None
            )
        )
        congestion_loss_proxy_rate = _congestion_loss_proxy_rate(congestion_proxy)
        loss_proxy_rate = _clamp_probability(
            max(
                route_blocking_ratio,
                failed_flow_ratio,
                route_loss_proxy_rate,
                congestion_loss_proxy_rate,
            )
        )
        offered_route_capacity = float(sum(route.capacity for route in available_routes))
        requested_route_demand = float(
            sum(_route_demand_capacity(route) for route in self._routes.values())
        )
        available_route_demand = float(
            sum(_route_demand_capacity(route) for route in available_routes)
        )
        demand_pressure_proxy = _clamp_probability(
            requested_route_demand / offered_route_capacity
            if offered_route_capacity > 0.0
            else 1.0
            if requested_route_demand > 0.0
            else 0.0
        )
        demand_loss_proxy_rate = _congestion_loss_proxy_rate(demand_pressure_proxy)
        flow_quality = self._completed_flow_quality()
        completed_route_capacity = flow_quality["capacity_sum"]
        throughput_pressure_proxy = _clamp_probability(
            completed_route_capacity / offered_route_capacity
            if offered_route_capacity > 0.0
            else 0.0
        )
        pressure_loss_proxy_rate = (
            _congestion_loss_proxy_rate(throughput_pressure_proxy)
            if flow_quality["successful_count"] > 1
            else 0.0
        )
        pressure_loss_proxy_rate = max(
            pressure_loss_proxy_rate,
            demand_loss_proxy_rate,
        )
        effective_loss_proxy_rate = _clamp_probability(
            max(loss_proxy_rate, pressure_loss_proxy_rate)
        )
        flow_latency_avg = _average(flow_quality["latencies"])
        effective_latency_avg = flow_latency_avg or route_latency_avg
        pressure_delay_variation_proxy = (
            effective_latency_avg * max(0.0, throughput_pressure_proxy - 0.75) * 0.1
            if flow_quality["successful_count"] > 1
            else 0.0
        )
        effective_delay_variation_proxy = max(
            delay_variation_proxy,
            _standard_deviation(flow_quality["latencies"]),
            pressure_delay_variation_proxy,
        )
        effective_available_throughput = offered_route_capacity * (
            1.0 - effective_loss_proxy_rate
        )
        effective_throughput = (
            completed_route_capacity
            if completed_route_capacity > 0.0
            else effective_available_throughput
        )
        throughput_source = (
            "COMPLETED_FLOW_CAPACITY"
            if completed_route_capacity > 0.0
            else "AVAILABLE_ROUTE_CAPACITY_AFTER_LOSS"
        )
        latency_source = (
            "COMPLETED_FLOW_LATENCY"
            if flow_latency_avg > 0.0
            else "AVAILABLE_ROUTE_LATENCY"
        )
        loss_source = _dominant_proxy_source(
            (
                ("ROUTE_BLOCKING_RATIO", route_blocking_ratio),
                ("FAILED_FLOW_RATIO", failed_flow_ratio),
                ("ROUTE_LOSS_RATE", route_loss_proxy_rate),
                ("CONGESTION_LOSS_PROXY", congestion_loss_proxy_rate),
                ("PRESSURE_LOSS_PROXY", pressure_loss_proxy_rate),
            )
        )
        delay_variation_source = _dominant_proxy_source(
            (
                ("ROUTE_LATENCY_VARIATION", delay_variation_proxy),
                (
                    "FLOW_LATENCY_VARIATION",
                    _standard_deviation(flow_quality["latencies"]),
                ),
                ("PRESSURE_DELAY_VARIATION", pressure_delay_variation_proxy),
            )
        )

        return {
            "network_quality_active_link_count": len(active_links),
            "network_quality_available_route_count": len(available_routes),
            "network_quality_offered_route_capacity_mbps": offered_route_capacity,
            "network_quality_requested_route_demand_mbps": requested_route_demand,
            "network_quality_available_route_demand_mbps": available_route_demand,
            "network_quality_estimated_delivered_throughput_mbps": float(
                completed_route_capacity
            ),
            "network_quality_estimated_available_throughput_mbps": float(
                offered_route_capacity * (1.0 - loss_proxy_rate)
            ),
            "network_quality_route_latency_avg_s": route_latency_avg,
            "network_quality_route_latency_min_s": min(route_latencies, default=0.0),
            "network_quality_route_latency_max_s": max(route_latencies, default=0.0),
            "network_quality_delay_variation_proxy_s": delay_variation_proxy,
            "network_quality_route_blocking_ratio": float(route_blocking_ratio),
            "network_quality_failed_flow_ratio": float(failed_flow_ratio),
            "network_quality_congestion_proxy": float(congestion_proxy),
            "network_quality_route_loss_proxy_rate": float(route_loss_proxy_rate),
            "network_quality_congestion_loss_proxy_rate": float(
                congestion_loss_proxy_rate
            ),
            "network_quality_loss_proxy_rate": float(loss_proxy_rate),
            "network_quality_flow_success_count": int(
                flow_quality["successful_count"]
            ),
            "network_quality_flow_failure_count": int(flow_quality["failed_count"]),
            "network_quality_flow_success_ratio": float(
                flow_quality["success_ratio"]
            ),
            "network_quality_flow_latency_avg_s": flow_latency_avg,
            "network_quality_flow_latency_variation_proxy_s": _standard_deviation(
                flow_quality["latencies"]
            ),
            "network_quality_flow_delivered_capacity_mbps": float(
                completed_route_capacity
            ),
            "network_quality_throughput_pressure_proxy": float(
                throughput_pressure_proxy
            ),
            "network_quality_demand_pressure_proxy": float(demand_pressure_proxy),
            "network_quality_demand_loss_proxy_rate": float(demand_loss_proxy_rate),
            "network_quality_pressure_loss_proxy_rate": float(
                pressure_loss_proxy_rate
            ),
            "network_quality_pressure_delay_variation_proxy_s": float(
                pressure_delay_variation_proxy
            ),
            "network_quality_effective_latency_avg_s": float(
                effective_latency_avg
            ),
            "network_quality_effective_delay_variation_proxy_s": float(
                effective_delay_variation_proxy
            ),
            "network_quality_effective_loss_proxy_rate": float(
                effective_loss_proxy_rate
            ),
            "network_quality_effective_throughput_mbps": float(
                effective_throughput
            ),
            "network_quality_effective_available_throughput_mbps": float(
                effective_available_throughput
            ),
            "network_quality_proxy_note": (
                "Flow-level proxy only; no packet-level simulation is performed."
            ),
            "network_quality_provenance_note": (
                "Flow-level KPI provenance from route, link, and completed-flow state; "
                "no packet-level samples are used."
            ),
            "network_quality_throughput_source": throughput_source,
            "network_quality_throughput_source_label": _network_quality_source_label(
                throughput_source
            ),
            "network_quality_latency_source": latency_source,
            "network_quality_latency_source_label": _network_quality_source_label(
                latency_source
            ),
            "network_quality_loss_source": loss_source,
            "network_quality_loss_source_label": _network_quality_source_label(
                loss_source
            ),
            "network_quality_delay_variation_source": delay_variation_source,
            "network_quality_delay_variation_source_label": (
                _network_quality_source_label(delay_variation_source)
            ),
        }

    def _completed_flow_quality(self) -> dict[str, float | int | tuple[float, ...]]:
        successful_count = 0
        failed_count = 0
        latencies: list[float] = []
        capacity_sum = 0.0
        for flow_id in sorted(self._completed_flows):
            flow = self._completed_flows[flow_id]
            route = self._routes.get(flow.route_id)
            if _flow_is_failed(flow):
                failed_count += 1
                continue
            successful_count += 1
            if flow.latency is not None:
                latencies.append(float(flow.latency))
            elif route is not None and route.available:
                latencies.append(float(route.latency))

            if flow.capacity is not None:
                capacity_sum += float(flow.capacity)
            elif route is not None and route.available:
                capacity_sum += float(route.capacity)

        total = successful_count + failed_count
        success_ratio = 0.0 if total == 0 else successful_count / total
        return {
            "successful_count": successful_count,
            "failed_count": failed_count,
            "success_ratio": float(success_ratio),
            "latencies": tuple(latencies),
            "capacity_sum": float(capacity_sum),
        }

    def _route_latency_delta_average(self) -> float:
        deltas: list[float] = []
        for route_id in sorted(self._route_latency_history):
            values = tuple(self._route_latency_history[route_id])
            deltas.extend(
                abs(values[index] - values[index - 1])
                for index in range(1, len(values))
            )
        return _average(tuple(deltas))

    def _failed_flow_ratio(self) -> float:
        if not self._completed_flows:
            return 0.0
        failed = sum(
            1
            for flow in self._completed_flows.values()
            if flow.status.upper() in {"FAILED", "DROPPED", "BLOCKED"}
        )
        return failed / len(self._completed_flows)

    def _compute_resource_summary(self) -> MetricSummary:
        nodes = tuple(
            self._compute_nodes[node_id]
            for node_id in sorted(self._compute_nodes)
        )
        total = float(sum(max(0.0, node.capacity) for node in nodes))
        available = float(
            sum(
                min(max(0.0, node.available_capacity), max(0.0, node.capacity))
                for node in nodes
            )
        )
        used = max(0.0, total - available)
        utilization = 0.0 if total <= 0.0 else used / total
        busy_nodes = sum(
            1
            for node in nodes
            if node.status.upper() == "BUSY"
            or (
                node.capacity > 0.0
                and node.available_capacity < node.capacity
            )
        )
        vector_usage_reported = any(
            node.resource_usage_mode == "RESOURCE_VECTOR_ESTIMATED"
            for node in nodes
        )
        return {
            "compute_resource_node_count": len(nodes),
            "compute_resource_busy_nodes": busy_nodes,
            "compute_resource_idle_nodes": max(0, len(nodes) - busy_nodes),
            "compute_resource_total_gflops_fp32": total,
            "compute_resource_available_gflops_fp32": available,
            "compute_resource_used_gflops_fp32": used,
            "compute_resource_available_cpu_gflops_fp32": _compute_resource_total(
                nodes,
                "available_cpu_gflops_fp32",
            ),
            "compute_resource_used_cpu_gflops_fp32": _compute_resource_total(
                nodes,
                "used_cpu_gflops_fp32",
            ),
            "compute_resource_total_gflops_fp64": _compute_resource_total(
                nodes,
                "cpu_gflops_fp64",
            ),
            "compute_resource_available_gflops_fp64": _compute_resource_total(
                nodes,
                "available_cpu_gflops_fp64",
            ),
            "compute_resource_used_gflops_fp64": _compute_resource_total(
                nodes,
                "used_cpu_gflops_fp64",
            ),
            "compute_resource_total_gpu_tflops_fp32": _compute_resource_total(
                nodes,
                "gpu_tflops_fp32",
            ),
            "compute_resource_available_gpu_tflops_fp32": _compute_resource_total(
                nodes,
                "available_gpu_tflops_fp32",
            ),
            "compute_resource_used_gpu_tflops_fp32": _compute_resource_total(
                nodes,
                "used_gpu_tflops_fp32",
            ),
            "compute_resource_total_gpu_tflops_fp16": _compute_resource_total(
                nodes,
                "gpu_tflops_fp16",
            ),
            "compute_resource_available_gpu_tflops_fp16": _compute_resource_total(
                nodes,
                "available_gpu_tflops_fp16",
            ),
            "compute_resource_used_gpu_tflops_fp16": _compute_resource_total(
                nodes,
                "used_gpu_tflops_fp16",
            ),
            "compute_resource_total_npu_tops_int8": _compute_resource_total(
                nodes,
                "npu_tops_int8",
            ),
            "compute_resource_available_npu_tops_int8": _compute_resource_total(
                nodes,
                "available_npu_tops_int8",
            ),
            "compute_resource_used_npu_tops_int8": _compute_resource_total(
                nodes,
                "used_npu_tops_int8",
            ),
            "compute_resource_total_memory_gb": _compute_resource_total(
                nodes,
                "memory_gb",
            ),
            "compute_resource_available_memory_gb": _compute_resource_total(
                nodes,
                "available_memory_gb",
            ),
            "compute_resource_used_memory_gb": _compute_resource_total(
                nodes,
                "used_memory_gb",
            ),
            "compute_resource_total_storage_gb": _compute_resource_total(
                nodes,
                "storage_gb",
            ),
            "compute_resource_available_storage_gb": _compute_resource_total(
                nodes,
                "available_storage_gb",
            ),
            "compute_resource_used_storage_gb": _compute_resource_total(
                nodes,
                "used_storage_gb",
            ),
            "compute_resource_vector_capacity_reported": True,
            "compute_resource_vector_utilization_mode": (
                "RESOURCE_VECTOR_ESTIMATED"
                if vector_usage_reported
                else "SCALAR_FP32_AVAILABLE_ONLY"
            ),
            "compute_resource_utilization": float(utilization),
            "compute_resource_unit": "GFLOPS FP32",
            "compute_resource_proxy_note": (
                "Legacy scalar compute capacity maps to FP32 GFLOPS; "
                "resource-vector usage is deterministic estimator output when "
                "ComputeNodeState reports RESOURCE_VECTOR_ESTIMATED."
            ),
        }

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


def _compute_resource_total(
    nodes: tuple[ComputeNodeState, ...],
    field_name: str,
) -> float:
    return float(
        sum(max(0.0, float(getattr(node, field_name))) for node in nodes)
    )


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


def _standard_deviation(values: tuple[float, ...]) -> float:
    if len(values) <= 1:
        return 0.0
    mean = _average(values)
    variance = _average(tuple((value - mean) ** 2 for value in values))
    return float(variance**0.5)


def _congestion_loss_proxy_rate(utilization: float) -> float:
    if utilization <= 0.8:
        return 0.0
    return _clamp_probability((utilization - 0.8) * 0.5)


def _dominant_proxy_source(sources: tuple[tuple[str, float], ...]) -> str:
    selected_name = ""
    selected_value = -1.0
    for name, value in sources:
        numeric_value = float(value)
        if numeric_value > selected_value:
            selected_name = name
            selected_value = numeric_value
    return selected_name


def _network_quality_source_label(source: str) -> str:
    labels = {
        "COMPLETED_FLOW_CAPACITY": "已完成流容量",
        "AVAILABLE_ROUTE_CAPACITY_AFTER_LOSS": "可用路由容量扣除损耗代理",
        "COMPLETED_FLOW_LATENCY": "已完成流时延",
        "AVAILABLE_ROUTE_LATENCY": "可用路由平均时延",
        "ROUTE_BLOCKING_RATIO": "路由阻塞比例",
        "FAILED_FLOW_RATIO": "失败流比例",
        "ROUTE_LOSS_RATE": "路由损耗率",
        "CONGESTION_LOSS_PROXY": "链路拥塞损耗代理",
        "PRESSURE_LOSS_PROXY": "业务压力损耗代理",
        "ROUTE_LATENCY_VARIATION": "路由时延离散度",
        "FLOW_LATENCY_VARIATION": "流完成时延离散度",
        "PRESSURE_DELAY_VARIATION": "业务压力时延扰动",
    }
    return labels.get(source, source)


def _is_kpi_sample_event_type(event_type: str) -> bool:
    return event_type in {
        EventType.ACCESS_START,
        EventType.ACCESS_END,
        EventType.LINK_UPDATE,
        EventType.ROUTE_UPDATE,
        EventType.FLOW_COMPLETE,
        EventType.TASK_START,
        EventType.TASK_FINISH,
        COMPUTE_NODE_UPDATE,
    }


def _flow_is_failed(flow: FlowState) -> bool:
    return flow.status.upper() in {"FAILED", "DROPPED", "BLOCKED"}


def _route_demand_capacity(route: Route) -> float:
    return 0.0 if route.demand_capacity is None else float(route.demand_capacity)


def _clamp_probability(value: float) -> float:
    if not isfinite(value):
        return 0.0
    return max(0.0, min(1.0, float(value)))


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
