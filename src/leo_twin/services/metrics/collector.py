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
from threading import RLock
from typing import Any, Protocol

from leo_twin.models.network.pressure import (
    NETWORK_TIME_PRESSURE_PERIOD_S,
    time_varying_pressure_delay_variation,
    time_varying_pressure_factor,
    time_varying_pressure_loss_rate,
    time_varying_pressure_phase,
)
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
KpiSample = dict[str, str | float]
SatelliteKpiSlice = dict[str, str | float | int]
SatelliteKpiHistorySample = dict[str, float]
RoutePressureEvidenceItem = dict[str, str | float | int | bool]
RoutePressureEdgeEvidenceItem = dict[str, str | float | int | bool]
ReplayPayload = str | int | float | bool | None | list["ReplayPayload"] | dict[str, "ReplayPayload"]
ReplayEvent = dict[str, ReplayPayload]

_CSV_FIELDS = ("sim_time", "metric_name", "entity_id", "value", "tags")
_RECENT_FLOW_KPI_WINDOW_S = 60.0
_NETWORK_TIME_PRESSURE_PERIOD_S = NETWORK_TIME_PRESSURE_PERIOD_S


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
        satellite_kpi_history_limit: int = 32,
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
        _require_positive_int(satellite_kpi_history_limit, "satellite_kpi_history_limit")
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
        self._kpi_sample_limit = kpi_sample_limit
        self._satellite_kpi_history_limit = satellite_kpi_history_limit
        self._satellite_position_scale_to_km = float(satellite_position_scale_to_km)
        self._records: deque[MetricRecord] = deque(maxlen=record_limit)
        self._event_log: deque[ReplayEvent] = deque(maxlen=event_log_limit)
        self._kpi_samples: deque[KpiSample] = deque(maxlen=kpi_sample_limit)
        self._satellite_kpi_history: dict[
            str,
            deque[SatelliteKpiHistorySample],
        ] = {}
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
        self._active_flow_routes: dict[str, Route] = {}
        self._flow_route_start_times: dict[str, float] = {}
        self._completed_flows: dict[str, FlowState] = {}
        self._completed_flow_times: dict[str, float] = {}
        self._compute_nodes: dict[str, ComputeNodeState] = {}
        self._running_tasks: set[str] = set()
        self._task_node_ids: dict[str, str] = {}
        self._running_tasks_by_node: Counter[str] = Counter()
        self._finished_tasks_by_node: Counter[str] = Counter()
        self._task_start_times: dict[str, float] = {}
        self._task_durations: dict[str, float] = {}
        self._finished_tasks: dict[str, str] = {}
        self._service_latency_components_by_task: dict[str, dict[str, float]] = {}
        self._service_latency_metadata_by_task: dict[str, dict[str, str]] = {}
        self._service_latency_times_by_task: dict[str, dict[str, float]] = {}
        self._service_latency_timeline_by_task: dict[
            str,
            dict[str, dict[str, str | float]],
        ] = {}
        self._last_sim_time = 0.0
        self._metric_event_sequence = 0
        self._lock = RLock()

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

        with self._lock:
            return self._observe_unlocked(event)

    def _observe_unlocked(self, event: SimEvent) -> tuple[MetricRecord, ...]:
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
        records.extend(self._derived_metric_records(event.sim_time, event_type))
        self._append_kpi_sample(event.sim_time, event_type)
        self._records.extend(records)
        return tuple(records)

    def records(self) -> tuple[MetricRecord, ...]:
        with self._lock:
            return tuple(self._records)

    def event_log(self) -> tuple[ReplayEvent, ...]:
        with self._lock:
            return tuple(dict(event) for event in self._event_log)

    def summary(self) -> MetricSummary:
        with self._lock:
            return self._summary_unlocked()

    def _summary_unlocked(self) -> MetricSummary:
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
        summary.update(
            self._network_quality_summary(
                active_links,
                available_routes,
                sim_time=self._last_sim_time,
            )
        )
        summary.update(self._network_constraint_summary(active_links, available_routes))
        summary.update(self._network_flow_lifecycle_summary(sim_time=self._last_sim_time))
        summary.update(self._compute_resource_summary())
        summary.update(self._service_latency_summary())
        for event_type, count in sorted(self._event_counts.items()):
            summary[f"events.{event_type}.count"] = count
        return summary

    def metrics_csv(self) -> str:
        with self._lock:
            return self._metrics_csv_unlocked()

    def _metrics_csv_unlocked(self) -> str:
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

    def kpi_time_series(
        self,
        sim_time: float | None = None,
    ) -> dict[str, str | int | list[KpiSample]]:
        with self._lock:
            return self._kpi_time_series_unlocked(sim_time)

    def _kpi_time_series_unlocked(
        self,
        sim_time: float | None = None,
    ) -> dict[str, str | int | list[KpiSample]]:
        samples = [dict(sample) for sample in self._kpi_samples]
        current_sample_time = (
            self._last_sim_time
            if sim_time is None
            else max(self._last_sim_time, float(sim_time))
        )
        current_sample = self._current_kpi_sample(current_sample_time)
        if not samples:
            samples = (
                [_baseline_kpi_sample(0.0), current_sample]
                if current_sample_time > 0.0
                else [current_sample]
            )[-self._kpi_sample_limit :]
        elif samples[-1]["sim_time"] == current_sample["sim_time"]:
            samples[-1] = current_sample
        elif samples[-1]["sim_time"] < current_sample["sim_time"]:
            samples.append(current_sample)
            samples = samples[-self._kpi_sample_limit :]
        else:
            samples = [current_sample]
        if (
            len(samples) == 1
            and samples[0]["sim_time"] > 0.0
            and self._kpi_sample_limit > 1
        ):
            samples = [_baseline_kpi_sample(0.0), samples[0]]
        return {
            "version": "v1",
            "sample_count": len(samples),
            "tail_sample_source": "CURRENT_METRICS_SUMMARY",
            "tail_sample_source_label": "当前指标摘要同步",
            "samples": samples,
        }

    def satellite_kpi_slices(
        self,
        limit: int = 64,
    ) -> dict[str, str | int | list[SatelliteKpiSlice]]:
        with self._lock:
            return self._satellite_kpi_slices_unlocked(limit)

    def _satellite_kpi_slices_unlocked(
        self,
        limit: int = 64,
    ) -> dict[str, str | int | list[SatelliteKpiSlice]]:
        _require_positive_int(limit, "limit")
        satellite_ids = self._satellite_ids_for_kpi_slices()
        slices = [self._satellite_kpi_slice(satellite_id) for satellite_id in satellite_ids]
        selected = sorted(slices, key=_satellite_kpi_slice_sort_key)[:limit]
        selected = sorted(selected, key=lambda item: str(item["satellite_id"]))
        return {
            "version": "v1",
            "mode": "TOP_ACTIVITY_LIMITED",
            "slice_limit": limit,
            "satellite_count": len(satellite_ids),
            "slice_count": len(selected),
            "slices": selected,
        }

    def satellite_kpi_history(
        self,
        limit: int = 64,
        sample_limit: int | None = None,
    ) -> dict[str, Any]:
        with self._lock:
            return self._satellite_kpi_history_unlocked(limit, sample_limit)

    def _satellite_kpi_history_unlocked(
        self,
        limit: int = 64,
        sample_limit: int | None = None,
    ) -> dict[str, Any]:
        _require_positive_int(limit, "limit")
        if sample_limit is None:
            sample_limit = self._satellite_kpi_history_limit
        _require_positive_int(sample_limit, "sample_limit")
        selected_ids = sorted(
            self._satellite_kpi_history,
            key=lambda satellite_id: _satellite_kpi_history_sort_key(
                satellite_id,
                self._satellite_kpi_history[satellite_id],
            ),
        )[:limit]
        series = []
        for satellite_id in selected_ids:
            samples = [
                dict(sample)
                for sample in self._satellite_kpi_history[satellite_id]
            ][-sample_limit:]
            series.append(
                {
                    "satellite_id": satellite_id,
                    "sample_count": len(samples),
                    "samples": samples,
                }
            )
        return {
            "version": "v1",
            "mode": "RECENT_COMPUTE_LIMITED",
            "slice_limit": limit,
            "sample_limit": sample_limit,
            "satellite_count": len(self._satellite_kpi_history),
            "series_count": len(series),
            "series": series,
        }

    def service_latency_history(self, limit: int = 32) -> dict[str, Any]:
        with self._lock:
            return self._service_latency_history_unlocked(limit)

    def route_pressure_evidence(self, limit: int = 64) -> dict[str, Any]:
        with self._lock:
            return self._route_pressure_evidence_unlocked(limit)

    def _route_pressure_evidence_unlocked(self, limit: int = 64) -> dict[str, Any]:
        _require_positive_int(limit, "limit")
        routes = tuple(self._routes[route_id] for route_id in sorted(self._routes))
        evidence_items = tuple(_route_pressure_evidence_item(route) for route in routes)
        selected = tuple(sorted(evidence_items, key=_route_pressure_evidence_sort_key)[:limit])
        edge_evidence_items = tuple(
            item
            for route in routes
            for item in _route_pressure_edge_evidence_items(route)
        )
        selected_edges = tuple(
            sorted(edge_evidence_items, key=_route_pressure_edge_evidence_sort_key)[
                : limit * 2
            ]
        )
        pressure_rejected_count = sum(
            1 for item in evidence_items if item["pressure_state"] == "ADMISSION_REJECTED"
        )
        topology_blocked_count = sum(
            1 for item in evidence_items if item["pressure_state"] == "TOPOLOGY_BLOCKED"
        )
        queued_count = sum(
            1 for item in evidence_items if item["pressure_state"] == "QUEUED"
        )
        saturated_count = sum(
            1 for item in evidence_items if item["pressure_state"] == "SATURATED"
        )
        edge_rejected_count = sum(
            1 for item in edge_evidence_items if item["pressure_state"] == "ADMISSION_REJECTED"
        )
        edge_queued_count = sum(
            1 for item in edge_evidence_items if item["pressure_state"] == "QUEUED"
        )
        edge_saturated_count = sum(
            1 for item in edge_evidence_items if item["pressure_state"] == "SATURATED"
        )
        return {
            "version": "v1",
            "source": "BACKEND_METRICS_COLLECTOR",
            "evidence_id": "leo_twin.route_pressure_evidence.v1",
            "pressure_model": "FLOW_PRESSURE_ADMISSION_V1",
            "route_source": "ROUTE_UPDATE",
            "packet_level_simulation": False,
            "route_count": len(routes),
            "item_limit": limit,
            "item_count": len(selected),
            "hidden_route_count": max(0, len(routes) - len(selected)),
            "pressure_admission_rejected_count": pressure_rejected_count,
            "topology_blocked_count": topology_blocked_count,
            "queued_route_count": queued_count,
            "saturated_route_count": saturated_count,
            "pressure_edge_count": len(edge_evidence_items),
            "edge_item_limit": limit * 2,
            "edge_item_count": len(selected_edges),
            "hidden_edge_count": max(0, len(edge_evidence_items) - len(selected_edges)),
            "pressure_admission_rejected_edge_count": edge_rejected_count,
            "queued_edge_count": edge_queued_count,
            "saturated_edge_count": edge_saturated_count,
            "max_edge_projected_utilization": max(
                (float(item["projected_utilization"]) for item in edge_evidence_items),
                default=0.0,
            ),
            "max_edge_queue_delay_s": max(
                (float(item["queue_delay_s"]) for item in edge_evidence_items),
                default=0.0,
            ),
            "max_edge_loss_proxy_rate": max(
                (float(item["loss_proxy_rate"]) for item in edge_evidence_items),
                default=0.0,
            ),
            "items": selected,
            "edge_items": selected_edges,
        }

    def _service_latency_history_unlocked(self, limit: int = 32) -> dict[str, Any]:
        _require_positive_int(limit, "limit")
        selected = sorted(
            self._service_latency_components_by_task.items(),
            key=_service_latency_history_sort_key,
        )[:limit]
        services = [
            _service_latency_history_item(
                task_id,
                components,
                self._service_latency_metadata_by_task.get(task_id, {}),
                self._service_latency_times_by_task.get(task_id, {}),
                self._service_latency_timeline_by_task.get(task_id, {}),
            )
            for task_id, components in selected
        ]
        return {
            "version": "v1",
            "mode": "RECENT_SERVICE_LIMITED",
            "service_count": len(self._service_latency_components_by_task),
            "service_limit": limit,
            "item_count": len(services),
            "items": services,
        }

    def events_jsonl(self) -> str:
        with self._lock:
            return _events_jsonl(tuple(self._event_log))

    def events_jsonl_segments(
        self,
        events_per_segment: int | None = None,
    ) -> tuple[str, ...]:
        with self._lock:
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
            record = _require_payload(event.payload, MetricRecord, "METRIC_SAMPLE")
            self._observe_metric_sample_record(record)
            return (record,)
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
                sim_time=sim_time,
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
            fields = (
                ("compute.resource.used_gflops_fp32", "compute_resource_used_gflops_fp32"),
                ("compute.resource.used_gflops_fp64", "compute_resource_used_gflops_fp64"),
                (
                    "compute.resource.used_gpu_tflops_fp32",
                    "compute_resource_used_gpu_tflops_fp32",
                ),
                (
                    "compute.resource.used_gpu_tflops_fp16",
                    "compute_resource_used_gpu_tflops_fp16",
                ),
                (
                    "compute.resource.used_npu_tops_int8",
                    "compute_resource_used_npu_tops_int8",
                ),
                ("compute.resource.used_memory_gb", "compute_resource_used_memory_gb"),
                ("compute.resource.used_storage_gb", "compute_resource_used_storage_gb"),
            )
            records.extend(
                MetricRecord(
                    metric_name=metric_name,
                    sim_time=sim_time,
                    entity_id="system",
                    value=float(compute_summary[summary_key]),
                    tags=(("source", "metrics_summary"),),
                )
                for metric_name, summary_key in fields
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
            sim_time=sim_time,
        )
        recent_flow_quality = self._recent_flow_quality(sim_time)
        recent_flow_count = int(
            recent_flow_quality["successful_count"]
            + recent_flow_quality["failed_count"]
        )
        recent_flow_loss_proxy_rate = (
            0.0
            if recent_flow_count == 0
            else float(recent_flow_quality["failed_count"]) / recent_flow_count
        )
        recent_flow_delay_variation_s = _standard_deviation(
            recent_flow_quality["latencies"]
        )
        recent_loss_zero_reason = _network_recent_loss_zero_reason(
            recent_flow_loss_proxy_rate,
            recent_flow_count=recent_flow_count,
        )
        recent_delay_variation_zero_reason = (
            _network_recent_delay_variation_zero_reason(
                recent_flow_delay_variation_s,
                recent_flow_count=recent_flow_count,
                recent_latency_count=len(recent_flow_quality["latencies"]),
            )
        )
        lifetime_effective_throughput = float(
            network_summary["network_quality_effective_throughput_mbps"]
        )
        runtime_effective_throughput, runtime_throughput_source = (
            _runtime_window_effective_throughput(
                network_summary,
                recent_flow_count=recent_flow_count,
                recent_delivered_capacity=float(recent_flow_quality["capacity_sum"]),
            )
        )
        compute_summary = self._compute_resource_summary()
        return {
            "sim_time": float(sim_time),
            "network_effective_throughput_mbps": runtime_effective_throughput,
            "network_effective_throughput_source": runtime_throughput_source,
            "network_effective_throughput_source_label": (
                _runtime_window_throughput_source_label(runtime_throughput_source)
            ),
            "network_lifetime_effective_throughput_mbps": lifetime_effective_throughput,
            "network_requested_route_demand_mbps": float(
                network_summary["network_quality_requested_route_demand_mbps"]
            ),
            "network_offered_route_capacity_mbps": float(
                network_summary["network_quality_offered_route_capacity_mbps"]
            ),
            "network_available_route_demand_mbps": float(
                network_summary["network_quality_available_route_demand_mbps"]
            ),
            "network_demand_pressure_proxy": float(
                network_summary["network_quality_demand_pressure_proxy"]
            ),
            "network_throughput_pressure_proxy": float(
                network_summary["network_quality_throughput_pressure_proxy"]
            ),
            "network_effective_latency_s": float(
                network_summary["network_quality_effective_latency_avg_s"]
            ),
            "network_route_latency_avg_s": float(
                network_summary["network_quality_route_latency_avg_s"]
            ),
            "network_effective_loss_proxy_rate": float(
                network_summary["network_quality_effective_loss_proxy_rate"]
            ),
            "network_route_loss_proxy_rate": float(
                network_summary["network_quality_route_loss_proxy_rate"]
            ),
            "network_route_blocking_ratio": float(
                network_summary["network_quality_route_blocking_ratio"]
            ),
            "network_failed_flow_ratio": float(
                network_summary["network_quality_failed_flow_ratio"]
            ),
            "network_congestion_proxy": float(
                network_summary["network_quality_congestion_proxy"]
            ),
            "network_congestion_loss_proxy_rate": float(
                network_summary["network_quality_congestion_loss_proxy_rate"]
            ),
            "network_demand_loss_proxy_rate": float(
                network_summary["network_quality_demand_loss_proxy_rate"]
            ),
            "network_pressure_loss_proxy_rate": float(
                network_summary["network_quality_pressure_loss_proxy_rate"]
            ),
            "network_effective_delay_variation_s": float(
                network_summary["network_quality_effective_delay_variation_proxy_s"]
            ),
            "network_route_delay_variation_s": float(
                network_summary["network_quality_delay_variation_proxy_s"]
            ),
            "network_flow_delay_variation_s": float(
                network_summary["network_quality_flow_latency_variation_proxy_s"]
            ),
            "network_pressure_delay_variation_s": float(
                network_summary["network_quality_pressure_delay_variation_proxy_s"]
            ),
            "network_effective_available_throughput_mbps": float(
                network_summary["network_quality_effective_available_throughput_mbps"]
            ),
            "network_flow_delivered_capacity_mbps": float(
                network_summary["network_quality_flow_delivered_capacity_mbps"]
            ),
            "network_time_adjusted_delivered_throughput_mbps": float(
                network_summary[
                    "network_quality_time_adjusted_delivered_throughput_mbps"
                ]
            ),
            "network_time_pressure_period_s": float(
                network_summary["network_quality_time_pressure_period_s"]
            ),
            "network_time_pressure_phase": float(
                network_summary["network_quality_time_pressure_phase"]
            ),
            "network_time_pressure_factor": float(
                network_summary["network_quality_time_pressure_factor"]
            ),
            "network_time_pressure_loss_proxy_rate": float(
                network_summary["network_quality_time_pressure_loss_proxy_rate"]
            ),
            "network_time_pressure_delay_variation_s": float(
                network_summary[
                    "network_quality_time_pressure_delay_variation_proxy_s"
                ]
            ),
            "network_recent_window_s": float(_RECENT_FLOW_KPI_WINDOW_S),
            "network_recent_flow_count": float(recent_flow_count),
            "network_recent_delivered_throughput_mbps": float(
                recent_flow_quality["capacity_sum"]
            ),
            "network_recent_latency_s": _average(recent_flow_quality["latencies"]),
            "network_recent_loss_proxy_rate": float(recent_flow_loss_proxy_rate),
            "network_recent_loss_zero_reason": recent_loss_zero_reason,
            "network_recent_loss_zero_reason_label": _network_quality_zero_reason_label(
                recent_loss_zero_reason
            ),
            "network_recent_delay_variation_s": recent_flow_delay_variation_s,
            "network_recent_delay_variation_zero_reason": (
                recent_delay_variation_zero_reason
            ),
            "network_recent_delay_variation_zero_reason_label": (
                _network_quality_zero_reason_label(
                    recent_delay_variation_zero_reason
                )
            ),
            "compute_resource_used_gflops_fp32": float(
                compute_summary["compute_resource_used_gflops_fp32"]
            ),
            "compute_resource_used_gflops_fp64": float(
                compute_summary["compute_resource_used_gflops_fp64"]
            ),
            "compute_resource_used_gpu_tflops_fp32": float(
                compute_summary["compute_resource_used_gpu_tflops_fp32"]
            ),
            "compute_resource_used_gpu_tflops_fp16": float(
                compute_summary["compute_resource_used_gpu_tflops_fp16"]
            ),
            "compute_resource_used_npu_tops_int8": float(
                compute_summary["compute_resource_used_npu_tops_int8"]
            ),
            "compute_resource_used_memory_gb": float(
                compute_summary["compute_resource_used_memory_gb"]
            ),
            "compute_resource_used_storage_gb": float(
                compute_summary["compute_resource_used_storage_gb"]
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
        if route.flow_id not in self._completed_flows:
            self._active_flow_routes[route.flow_id] = route
            self._flow_route_start_times.setdefault(route.flow_id, float(event.sim_time))
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
        self._completed_flow_times[flow.flow_id] = float(event.sim_time)
        self._active_flow_routes.pop(flow.flow_id, None)
        self._flow_route_start_times.pop(flow.flow_id, None)
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
        if _is_satellite_id(node.node_id):
            self._append_satellite_kpi_history_sample(node, event.sim_time)
        return ()

    def _observe_metric_sample_record(self, record: MetricRecord) -> None:
        if not record.metric_name.startswith("service."):
            return
        if not isinstance(record.value, (int, float)) or not isfinite(record.value):
            return
        component = _service_latency_component_name(record.metric_name)
        if component is None:
            return
        latency = max(0.0, float(record.value))
        self._service_latency_components_by_task.setdefault(record.entity_id, {})[
            component
        ] = latency
        metadata = self._service_latency_metadata_by_task.setdefault(record.entity_id, {})
        times = self._service_latency_times_by_task.setdefault(record.entity_id, {})
        times["first_sample_sim_time"] = min(
            float(record.sim_time),
            times.get("first_sample_sim_time", float(record.sim_time)),
        )
        times["last_sample_sim_time"] = max(
            float(record.sim_time),
            times.get("last_sample_sim_time", float(record.sim_time)),
        )
        tags = dict(record.tags)
        sample: dict[str, str | float] = {
            "component": component,
            "metric_name": record.metric_name,
            "sample_sim_time": float(record.sim_time),
            "duration_s": latency,
        }
        for key in ("input_flow_id", "output_flow_id"):
            value = tags.get(key)
            if isinstance(value, str) and value:
                metadata[key] = value
                sample[key] = value
        route_id = tags.get("route_id")
        if isinstance(route_id, str) and route_id:
            sample["route_id"] = route_id
            if component in {"input_network", "compute_queue", "compute_execution"}:
                metadata["input_route_id"] = route_id
            elif component in {"output_network", "total"}:
                metadata["output_route_id"] = route_id
        for key in _SERVICE_PLACEMENT_METADATA_TAGS:
            value = tags.get(key)
            if isinstance(value, str) and value:
                metadata[key] = value
        self._service_latency_timeline_by_task.setdefault(record.entity_id, {})[
            component
        ] = sample

    def _append_satellite_kpi_history_sample(
        self,
        node: ComputeNodeState,
        sim_time: float,
    ) -> None:
        history = self._satellite_kpi_history.setdefault(
            node.node_id,
            deque(maxlen=self._satellite_kpi_history_limit),
        )
        sample = _satellite_kpi_history_sample(node, sim_time)
        if history and history[-1]["sim_time"] == sample["sim_time"]:
            history[-1] = sample
            return
        history.append(sample)

    def _observe_task(self, event: SimEvent, event_type: str) -> tuple[MetricRecord, ...]:
        task = _require_payload(event.payload, TaskState, event_type)
        if event_type == EventType.TASK_START:
            previous_node_id = self._task_node_ids.get(task.task_id)
            if (
                task.task_id in self._running_tasks
                and previous_node_id is not None
                and previous_node_id != task.node_id
            ):
                self._running_tasks_by_node[previous_node_id] -= 1
                self._running_tasks_by_node[task.node_id] += 1
            elif task.task_id not in self._running_tasks:
                self._running_tasks_by_node[task.node_id] += 1
            self._running_tasks.add(task.task_id)
            self._task_node_ids[task.task_id] = task.node_id
            self._task_start_times[task.task_id] = task.sim_time
        else:
            node_id = self._task_node_ids.get(task.task_id, task.node_id)
            if task.task_id in self._running_tasks:
                self._running_tasks_by_node[node_id] -= 1
            self._running_tasks.discard(task.task_id)
            self._task_node_ids[task.task_id] = node_id
            self._finished_tasks_by_node[node_id] += 1
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

    def _satellite_ids_for_kpi_slices(self) -> tuple[str, ...]:
        satellite_ids = set(self._satellite_status)
        satellite_ids.update(
            node_id for node_id in self._compute_nodes if _is_satellite_id(node_id)
        )
        for link in self._links.values():
            if _is_satellite_id(link.source_id):
                satellite_ids.add(link.source_id)
            if _is_satellite_id(link.target_id):
                satellite_ids.add(link.target_id)
        for route in self._routes.values():
            satellite_ids.update(node_id for node_id in route.path if _is_satellite_id(node_id))
        return tuple(sorted(satellite_ids))

    def _satellite_kpi_slice(self, satellite_id: str) -> SatelliteKpiSlice:
        active_links = tuple(
            link
            for link in self._active_link_states()
            if _link_touches_satellite(link, satellite_id)
        )
        active_access_links = tuple(link for link in active_links if _is_access_link(link))
        active_space_links = tuple(link for link in active_links if _is_space_link(link))
        routes = tuple(
            route for route in self._routes.values() if satellite_id in route.path
        )
        available_routes = tuple(route for route in routes if route.available)
        route_latencies = tuple(float(route.latency) for route in available_routes)
        route_loss_values = tuple(
            float(route.loss_rate)
            for route in available_routes
            if route.loss_rate is not None
        )
        route_capacity = float(sum(max(0.0, route.capacity) for route in available_routes))
        route_demand = float(sum(_route_demand_capacity(route) for route in routes))
        node = self._compute_nodes.get(satellite_id)
        compute_capacity = 0.0 if node is None else max(0.0, float(node.capacity))
        compute_used = _compute_node_used_fp32(node)
        compute_load = _compute_node_load_ratio(node, compute_used)
        return {
            "satellite_id": satellite_id,
            "active_link_count": len(active_links),
            "active_access_link_count": len(active_access_links),
            "active_space_link_count": len(active_space_links),
            "route_count": len(routes),
            "available_route_count": len(available_routes),
            "route_capacity_mbps": route_capacity,
            "route_demand_mbps": route_demand,
            "route_latency_avg_s": _average(route_latencies),
            "route_delay_variation_proxy_s": _standard_deviation(route_latencies),
            "route_loss_proxy_rate": _average(route_loss_values),
            "compute_capacity_gflops_fp32": compute_capacity,
            "compute_used_gflops_fp32": compute_used,
            "compute_capacity_gflops_fp64": _compute_node_non_negative_field(
                node,
                "cpu_gflops_fp64",
            ),
            "compute_used_gflops_fp64": _compute_node_non_negative_field(
                node,
                "used_cpu_gflops_fp64",
            ),
            "compute_capacity_gpu_tflops_fp32": _compute_node_non_negative_field(
                node,
                "gpu_tflops_fp32",
            ),
            "compute_used_gpu_tflops_fp32": _compute_node_non_negative_field(
                node,
                "used_gpu_tflops_fp32",
            ),
            "compute_capacity_gpu_tflops_fp16": _compute_node_non_negative_field(
                node,
                "gpu_tflops_fp16",
            ),
            "compute_used_gpu_tflops_fp16": _compute_node_non_negative_field(
                node,
                "used_gpu_tflops_fp16",
            ),
            "compute_capacity_npu_tops_int8": _compute_node_non_negative_field(
                node,
                "npu_tops_int8",
            ),
            "compute_used_npu_tops_int8": _compute_node_non_negative_field(
                node,
                "used_npu_tops_int8",
            ),
            "compute_capacity_memory_gb": _compute_node_non_negative_field(
                node,
                "memory_gb",
            ),
            "compute_used_memory_gb": _compute_node_non_negative_field(
                node,
                "used_memory_gb",
            ),
            "compute_capacity_storage_gb": _compute_node_non_negative_field(
                node,
                "storage_gb",
            ),
            "compute_used_storage_gb": _compute_node_non_negative_field(
                node,
                "used_storage_gb",
            ),
            "compute_load_ratio": compute_load,
            "running_task_count": max(0, int(self._running_tasks_by_node[satellite_id])),
            "finished_task_count": max(0, int(self._finished_tasks_by_node[satellite_id])),
        }

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
        *,
        sim_time: float | None = None,
    ) -> MetricSummary:
        summary_time = self._last_sim_time if sim_time is None else max(0.0, float(sim_time))
        route_latencies = tuple(route.latency for route in available_routes)
        route_latency_avg = _average(route_latencies)
        delay_variation_proxy = max(
            _standard_deviation(route_latencies),
            self._route_latency_delta_average(),
        )
        routes = tuple(self._routes[route_id] for route_id in sorted(self._routes))
        unavailable_routes = max(0, len(routes) - len(available_routes))
        pressure_admission_rejected_routes = tuple(
            route for route in routes if not route.available and len(route.path) > 0
        )
        topology_blocked_routes = tuple(
            route for route in routes if not route.available and len(route.path) == 0
        )
        route_blocking_ratio = (
            0.0 if not routes else unavailable_routes / len(routes)
        )
        pressure_admission_rejection_ratio = (
            0.0 if not routes else len(pressure_admission_rejected_routes) / len(routes)
        )
        failed_flow_ratio = self._failed_flow_ratio()
        congestion_proxy = _average(
            tuple(
                float(link.utilization)
                for link in active_links
                if link.utilization is not None
            )
        )
        route_loss_values = tuple(
            float(route.loss_rate)
            for route in routes
            if route.loss_rate is not None
        )
        route_loss_proxy_rate = _average(route_loss_values)
        max_route_pressure_loss_rate = max(route_loss_values, default=0.0)
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
        queue_pressure_routes = tuple(
            route
            for route in available_routes
            if (route.loss_rate is not None and route.loss_rate > 0.0)
            or _route_demand_capacity(route) > route.capacity
        )
        saturated_routes = tuple(
            route
            for route in available_routes
            if _route_demand_capacity(route) > route.capacity
        )
        queue_pressure_proxy = _clamp_probability(
            max(demand_pressure_proxy, congestion_proxy, max_route_pressure_loss_rate)
        )
        flow_quality = self._completed_flow_quality()
        completed_route_capacity = flow_quality["capacity_sum"]
        throughput_pressure_proxy = _clamp_probability(
            completed_route_capacity / offered_route_capacity
            if offered_route_capacity > 0.0
            else 0.0
        )
        flow_pressure_proxy = (
            throughput_pressure_proxy if flow_quality["successful_count"] > 1 else 0.0
        )
        time_pressure_factor = time_varying_pressure_factor(
            summary_time,
            max(demand_pressure_proxy, flow_pressure_proxy, congestion_proxy),
        )
        time_pressure_loss_proxy_rate = time_varying_pressure_loss_rate(
            time_pressure_factor
        )
        pressure_loss_proxy_rate = (
            _congestion_loss_proxy_rate(throughput_pressure_proxy)
            if flow_quality["successful_count"] > 1
            else 0.0
        )
        pressure_loss_proxy_rate = max(
            pressure_loss_proxy_rate,
            demand_loss_proxy_rate,
            time_pressure_loss_proxy_rate,
        )
        effective_loss_proxy_rate = _clamp_probability(
            max(loss_proxy_rate, pressure_loss_proxy_rate)
        )
        flow_latency_avg = _average(flow_quality["latencies"])
        effective_latency_avg = flow_latency_avg or route_latency_avg
        time_pressure_delay_variation_proxy = time_varying_pressure_delay_variation(
            effective_latency_avg,
            time_pressure_factor,
        )
        pressure_delay_variation_proxy = (
            effective_latency_avg * max(0.0, throughput_pressure_proxy - 0.75) * 0.1
            if flow_quality["successful_count"] > 1
            else 0.0
        )
        pressure_delay_variation_proxy = max(
            pressure_delay_variation_proxy,
            time_pressure_delay_variation_proxy,
        )
        flow_latency_variation_proxy = _standard_deviation(flow_quality["latencies"])
        effective_delay_variation_proxy = max(
            delay_variation_proxy,
            flow_latency_variation_proxy,
            pressure_delay_variation_proxy,
        )
        effective_available_throughput = offered_route_capacity * (
            1.0 - effective_loss_proxy_rate
        )
        time_adjusted_completed_throughput = completed_route_capacity * (
            1.0 - time_pressure_loss_proxy_rate
        )
        effective_throughput = (
            time_adjusted_completed_throughput
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
                ("TIME_PRESSURE_LOSS_PROXY", time_pressure_loss_proxy_rate),
            )
        )
        delay_variation_source = _dominant_proxy_source(
            (
                ("ROUTE_LATENCY_VARIATION", delay_variation_proxy),
                ("FLOW_LATENCY_VARIATION", flow_latency_variation_proxy),
                ("PRESSURE_DELAY_VARIATION", pressure_delay_variation_proxy),
                ("TIME_PRESSURE_DELAY_VARIATION", time_pressure_delay_variation_proxy),
            )
        )
        loss_zero_reason = _network_quality_loss_zero_reason(
            effective_loss_proxy_rate,
            route_count=len(self._routes),
            flow_count=int(flow_quality["successful_count"] + flow_quality["failed_count"]),
        )
        delay_variation_zero_reason = _network_quality_delay_variation_zero_reason(
            effective_delay_variation_proxy,
            route_latency_count=len(route_latencies),
            flow_latency_count=len(flow_quality["latencies"]),
        )

        return {
            "network_quality_metric_model": "FLOW_LEVEL_PROXY",
            "network_quality_loss_metric_semantics": "LOSS_PROXY_RATE_NOT_PACKET_LOSS",
            "network_quality_delay_variation_metric_semantics": (
                "DELAY_VARIATION_PROXY_NOT_PACKET_JITTER"
            ),
            "network_quality_active_link_count": len(active_links),
            "network_quality_available_route_count": len(available_routes),
            "network_quality_route_decision_count": len(routes),
            "network_quality_available_route_decision_count": len(available_routes),
            "network_quality_unavailable_route_decision_count": unavailable_routes,
            "network_quality_topology_blocked_route_count": len(topology_blocked_routes),
            "network_quality_pressure_admission_rejected_route_count": len(
                pressure_admission_rejected_routes
            ),
            "network_quality_pressure_admission_rejection_ratio": float(
                pressure_admission_rejection_ratio
            ),
            "network_quality_queue_pressure_route_count": len(queue_pressure_routes),
            "network_quality_saturated_route_count": len(saturated_routes),
            "network_quality_max_route_pressure_loss_rate": float(
                max_route_pressure_loss_rate
            ),
            "network_quality_queue_pressure_proxy": float(queue_pressure_proxy),
            "network_quality_route_admission_model": "FLOW_PRESSURE_ADMISSION_V1",
            "network_quality_route_admission_source": "ROUTE_UPDATE",
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
            "network_quality_flow_latency_variation_proxy_s": (
                flow_latency_variation_proxy
            ),
            "network_quality_flow_delivered_capacity_mbps": float(
                completed_route_capacity
            ),
            "network_quality_time_adjusted_delivered_throughput_mbps": float(
                time_adjusted_completed_throughput
            ),
            "network_quality_throughput_pressure_proxy": float(
                throughput_pressure_proxy
            ),
            "network_quality_demand_pressure_proxy": float(demand_pressure_proxy),
            "network_quality_time_pressure_period_s": float(
                _NETWORK_TIME_PRESSURE_PERIOD_S
            ),
            "network_quality_time_pressure_phase": float(
                time_varying_pressure_phase(summary_time)
            ),
            "network_quality_time_pressure_factor": float(time_pressure_factor),
            "network_quality_time_pressure_loss_proxy_rate": float(
                time_pressure_loss_proxy_rate
            ),
            "network_quality_demand_loss_proxy_rate": float(demand_loss_proxy_rate),
            "network_quality_pressure_loss_proxy_rate": float(
                pressure_loss_proxy_rate
            ),
            "network_quality_time_pressure_delay_variation_proxy_s": float(
                time_pressure_delay_variation_proxy
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
            "network_quality_loss_zero_reason": loss_zero_reason,
            "network_quality_loss_zero_reason_label": _network_quality_zero_reason_label(
                loss_zero_reason
            ),
            "network_quality_delay_variation_zero_reason": (
                delay_variation_zero_reason
            ),
            "network_quality_delay_variation_zero_reason_label": (
                _network_quality_zero_reason_label(delay_variation_zero_reason)
            ),
        }

    def _network_flow_lifecycle_summary(
        self,
        *,
        sim_time: float | None = None,
    ) -> MetricSummary:
        summary_time = self._last_sim_time if sim_time is None else max(0.0, float(sim_time))
        active_routes = tuple(
            self._active_flow_routes[flow_id]
            for flow_id in sorted(self._active_flow_routes)
        )
        active_available_routes = tuple(route for route in active_routes if route.available)
        active_latencies = tuple(float(route.latency) for route in active_available_routes)
        active_demand = float(sum(_route_demand_capacity(route) for route in active_routes))
        active_capacity = float(
            sum(max(0.0, float(route.capacity)) for route in active_available_routes)
        )
        oldest_active_age = 0.0
        if self._flow_route_start_times:
            oldest_start = min(self._flow_route_start_times.values())
            oldest_active_age = max(0.0, summary_time - oldest_start)
        completed_flows = tuple(
            self._completed_flows[flow_id]
            for flow_id in sorted(self._completed_flows)
        )
        failed_count = sum(1 for flow in completed_flows if _flow_is_failed(flow))
        successful_count = len(completed_flows) - failed_count
        return {
            "network_flow_lifecycle_model": "ROUTE_UPDATE_TO_FLOW_COMPLETE_WINDOW",
            "network_flow_lifecycle_source": "BACKEND_METRICS_COLLECTOR",
            "network_flow_lifecycle_packet_level_simulation": False,
            "network_flow_lifecycle_active_flow_count": len(active_routes),
            "network_flow_lifecycle_active_available_flow_count": len(active_available_routes),
            "network_flow_lifecycle_active_blocked_flow_count": max(
                0,
                len(active_routes) - len(active_available_routes),
            ),
            "network_flow_lifecycle_active_demand_mbps": active_demand,
            "network_flow_lifecycle_active_capacity_mbps": active_capacity,
            "network_flow_lifecycle_active_latency_avg_s": _average(active_latencies),
            "network_flow_lifecycle_oldest_active_age_s": float(oldest_active_age),
            "network_flow_lifecycle_completed_flow_count": len(completed_flows),
            "network_flow_lifecycle_successful_flow_count": successful_count,
            "network_flow_lifecycle_failed_flow_count": failed_count,
        }

    def _network_constraint_summary(
        self,
        active_links: tuple[LinkState, ...],
        available_routes: tuple[Route, ...],
    ) -> MetricSummary:
        routes = tuple(self._routes[route_id] for route_id in sorted(self._routes))
        top_route = _top_constrained_route(routes)
        top_link = _top_constrained_link(active_links)
        unavailable_routes = max(0, len(routes) - len(available_routes))
        over_demand_routes = sum(
            1 for route in routes if _route_demand_capacity(route) > route.capacity
        )
        overloaded_links = sum(
            1
            for link in active_links
            if link.utilization is not None and link.utilization >= 0.9
        )

        return {
            "network_constraint_summary_source": "BACKEND_METRICS_COLLECTOR",
            "network_constraint_route_count": len(routes),
            "network_constraint_available_route_count": len(available_routes),
            "network_constraint_unavailable_route_count": unavailable_routes,
            "network_constraint_over_demand_route_count": over_demand_routes,
            "network_constraint_active_link_count": len(active_links),
            "network_constraint_overloaded_link_count": overloaded_links,
            "network_constraint_top_route_id": "" if top_route is None else top_route.route_id,
            "network_constraint_top_route_flow_id": (
                "" if top_route is None else top_route.flow_id
            ),
            "network_constraint_top_route_available": (
                False if top_route is None else top_route.available
            ),
            "network_constraint_top_route_capacity_mbps": (
                0.0 if top_route is None else float(top_route.capacity)
            ),
            "network_constraint_top_route_latency_s": (
                0.0 if top_route is None else float(top_route.latency)
            ),
            "network_constraint_top_route_hop_count": (
                0 if top_route is None else _route_hop_count(top_route)
            ),
            "network_constraint_top_route_demand_mbps": (
                0.0 if top_route is None else _route_demand_capacity(top_route)
            ),
            "network_constraint_top_route_loss_rate": (
                0.0
                if top_route is None or top_route.loss_rate is None
                else float(top_route.loss_rate)
            ),
            "network_constraint_top_route_pressure_proxy": (
                0.0 if top_route is None else _route_pressure_proxy(top_route)
            ),
            "network_constraint_top_route_path": (
                "" if top_route is None else " -> ".join(top_route.path)
            ),
            "network_constraint_top_link_id": "" if top_link is None else _link_id(top_link),
            "network_constraint_top_link_capacity_mbps": (
                0.0 if top_link is None else float(top_link.capacity)
            ),
            "network_constraint_top_link_latency_s": (
                0.0 if top_link is None else float(top_link.latency)
            ),
            "network_constraint_top_link_utilization": (
                0.0 if top_link is None else _link_utilization_value(top_link)
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

    def _recent_flow_quality(
        self,
        sim_time: float,
        window_seconds: float = _RECENT_FLOW_KPI_WINDOW_S,
    ) -> dict[str, float | int | tuple[float, ...]]:
        cutoff = float(sim_time) - max(0.0, float(window_seconds))
        successful_count = 0
        failed_count = 0
        latencies: list[float] = []
        capacity_sum = 0.0
        for flow_id in sorted(self._completed_flows):
            completion_time = self._completed_flow_times.get(flow_id)
            if completion_time is None or completion_time < cutoff:
                continue
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
        available_cpu_fp32 = _compute_resource_total(
            nodes,
            "available_cpu_gflops_fp32",
        )
        used_cpu_fp32 = _compute_resource_total(
            nodes,
            "used_cpu_gflops_fp32",
        )
        total_fp64 = _compute_resource_total(nodes, "cpu_gflops_fp64")
        available_fp64 = _compute_resource_total(
            nodes,
            "available_cpu_gflops_fp64",
        )
        used_fp64 = _compute_resource_total(nodes, "used_cpu_gflops_fp64")
        total_gpu_fp32 = _compute_resource_total(nodes, "gpu_tflops_fp32")
        available_gpu_fp32 = _compute_resource_total(
            nodes,
            "available_gpu_tflops_fp32",
        )
        used_gpu_fp32 = _compute_resource_total(
            nodes,
            "used_gpu_tflops_fp32",
        )
        total_gpu_fp16 = _compute_resource_total(nodes, "gpu_tflops_fp16")
        available_gpu_fp16 = _compute_resource_total(
            nodes,
            "available_gpu_tflops_fp16",
        )
        used_gpu_fp16 = _compute_resource_total(
            nodes,
            "used_gpu_tflops_fp16",
        )
        total_npu_int8 = _compute_resource_total(nodes, "npu_tops_int8")
        available_npu_int8 = _compute_resource_total(
            nodes,
            "available_npu_tops_int8",
        )
        used_npu_int8 = _compute_resource_total(nodes, "used_npu_tops_int8")
        total_memory = _compute_resource_total(nodes, "memory_gb")
        available_memory = _compute_resource_total(nodes, "available_memory_gb")
        used_memory = _compute_resource_total(nodes, "used_memory_gb")
        total_storage = _compute_resource_total(nodes, "storage_gb")
        available_storage = _compute_resource_total(nodes, "available_storage_gb")
        used_storage = _compute_resource_total(nodes, "used_storage_gb")
        bottleneck = _compute_resource_bottleneck(
            (
                (
                    "cpu_gflops_fp32",
                    "CPU FP32 GFLOPS",
                    total,
                    _compute_cpu_fp32_bottleneck_used(nodes),
                ),
                ("cpu_gflops_fp64", "CPU FP64 GFLOPS", total_fp64, used_fp64),
                (
                    "gpu_tflops_fp32",
                    "GPU FP32 TFLOPS",
                    total_gpu_fp32,
                    used_gpu_fp32,
                ),
                (
                    "gpu_tflops_fp16",
                    "GPU FP16 TFLOPS",
                    total_gpu_fp16,
                    used_gpu_fp16,
                ),
                ("npu_tops_int8", "NPU INT8 TOPS", total_npu_int8, used_npu_int8),
                ("memory_gb", "Memory GB", total_memory, used_memory),
                ("storage_gb", "Storage GB", total_storage, used_storage),
            )
        )
        return {
            "compute_resource_node_count": len(nodes),
            "compute_resource_busy_nodes": busy_nodes,
            "compute_resource_idle_nodes": max(0, len(nodes) - busy_nodes),
            "compute_resource_total_gflops_fp32": total,
            "compute_resource_available_gflops_fp32": available,
            "compute_resource_used_gflops_fp32": used,
            "compute_resource_available_cpu_gflops_fp32": available_cpu_fp32,
            "compute_resource_used_cpu_gflops_fp32": used_cpu_fp32,
            "compute_resource_total_gflops_fp64": total_fp64,
            "compute_resource_available_gflops_fp64": available_fp64,
            "compute_resource_used_gflops_fp64": used_fp64,
            "compute_resource_total_gpu_tflops_fp32": total_gpu_fp32,
            "compute_resource_available_gpu_tflops_fp32": available_gpu_fp32,
            "compute_resource_used_gpu_tflops_fp32": used_gpu_fp32,
            "compute_resource_total_gpu_tflops_fp16": total_gpu_fp16,
            "compute_resource_available_gpu_tflops_fp16": available_gpu_fp16,
            "compute_resource_used_gpu_tflops_fp16": used_gpu_fp16,
            "compute_resource_total_npu_tops_int8": total_npu_int8,
            "compute_resource_available_npu_tops_int8": available_npu_int8,
            "compute_resource_used_npu_tops_int8": used_npu_int8,
            "compute_resource_total_memory_gb": total_memory,
            "compute_resource_available_memory_gb": available_memory,
            "compute_resource_used_memory_gb": used_memory,
            "compute_resource_total_storage_gb": total_storage,
            "compute_resource_available_storage_gb": available_storage,
            "compute_resource_used_storage_gb": used_storage,
            "compute_resource_vector_capacity_reported": True,
            "compute_resource_vector_utilization_mode": (
                "RESOURCE_VECTOR_ESTIMATED"
                if vector_usage_reported
                else "SCALAR_FP32_AVAILABLE_ONLY"
            ),
            "compute_resource_vector_dimension_count": 7,
            "compute_resource_vector_active_dimension_count": bottleneck[
                "active_dimension_count"
            ],
            "compute_resource_bottleneck_resource": bottleneck["resource"],
            "compute_resource_bottleneck_label": bottleneck["label"],
            "compute_resource_bottleneck_utilization": bottleneck["utilization"],
            "compute_resource_bottleneck_used": bottleneck["used"],
            "compute_resource_bottleneck_total": bottleneck["total"],
            "compute_resource_bottleneck_available": bottleneck["available"],
            "compute_resource_bottleneck_status": bottleneck["status"],
            "compute_resource_utilization": float(utilization),
            "compute_resource_unit": "GFLOPS FP32",
            "compute_resource_proxy_note": (
                "Legacy scalar compute capacity maps to FP32 GFLOPS; "
                "resource-vector usage is deterministic estimator output when "
                "ComputeNodeState reports RESOURCE_VECTOR_ESTIMATED."
            ),
        }

    def _service_latency_summary(self) -> MetricSummary:
        components = tuple(self._service_latency_components_by_task.values())
        complete_components = tuple(
            item for item in components if "total" in item
        )
        return {
            "service_latency_summary_source": "METRIC_SAMPLE",
            "service_latency_model": "COMMUNICATION_COMPUTE_COMPONENT_PROXY",
            "service_latency_task_count": len(components),
            "service_latency_complete_count": len(complete_components),
            "service_latency_input_network_avg_s": _average(
                tuple(item["input_network"] for item in components if "input_network" in item)
            ),
            "service_latency_compute_queue_avg_s": _average(
                tuple(item["compute_queue"] for item in components if "compute_queue" in item)
            ),
            "service_latency_compute_execution_avg_s": _average(
                tuple(
                    item["compute_execution"]
                    for item in components
                    if "compute_execution" in item
                )
            ),
            "service_latency_output_network_avg_s": _average(
                tuple(item["output_network"] for item in components if "output_network" in item)
            ),
            "service_latency_total_avg_s": _average(
                tuple(item["total"] for item in complete_components)
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


def _top_constrained_route(routes: tuple[Route, ...]) -> Route | None:
    if not routes:
        return None
    return sorted(routes, key=_route_constraint_sort_key)[0]


def _satellite_kpi_slice_sort_key(
    item: SatelliteKpiSlice,
) -> tuple[float, float, float, float, str]:
    return (
        -float(item["compute_load_ratio"]),
        -float(item["compute_used_gflops_fp32"]),
        -float(item["route_capacity_mbps"]),
        -float(item["active_link_count"]),
        str(item["satellite_id"]),
    )


def _satellite_kpi_history_sort_key(
    satellite_id: str,
    history: deque[SatelliteKpiHistorySample],
) -> tuple[float, float, str]:
    if not history:
        return (0.0, 0.0, satellite_id)
    latest = history[-1]
    return (
        -float(latest["compute_load_ratio"]),
        -float(latest["sim_time"]),
        satellite_id,
    )


def _runtime_window_effective_throughput(
    network_summary: Mapping[str, str | float | int | bool],
    *,
    recent_flow_count: int,
    recent_delivered_capacity: float,
) -> tuple[float, str]:
    lifetime_flow_count = int(
        float(network_summary["network_quality_flow_success_count"])
        + float(network_summary["network_quality_flow_failure_count"])
    )
    if recent_flow_count > 0:
        time_loss = float(network_summary["network_quality_time_pressure_loss_proxy_rate"])
        return (
            max(0.0, float(recent_delivered_capacity) * (1.0 - time_loss)),
            "RECENT_FLOW_WINDOW",
        )
    if lifetime_flow_count > 0:
        return 0.0, "NO_RECENT_FLOW_IN_WINDOW"
    return (
        float(network_summary["network_quality_effective_throughput_mbps"]),
        "AVAILABLE_ROUTE_CAPACITY_AFTER_LOSS",
    )


def _runtime_window_throughput_source_label(source: str) -> str:
    labels = {
        "RECENT_FLOW_WINDOW": "recent completed flow window",
        "NO_RECENT_FLOW_IN_WINDOW": "no completed flow in recent window",
        "AVAILABLE_ROUTE_CAPACITY_AFTER_LOSS": "available route capacity estimate",
    }
    return labels.get(source, source)


def _baseline_kpi_sample(sim_time: float) -> KpiSample:
    return {
        "sim_time": float(sim_time),
        "network_effective_throughput_mbps": 0.0,
        "network_effective_throughput_source": "BASELINE",
        "network_effective_throughput_source_label": "baseline",
        "network_lifetime_effective_throughput_mbps": 0.0,
        "network_requested_route_demand_mbps": 0.0,
        "network_offered_route_capacity_mbps": 0.0,
        "network_available_route_demand_mbps": 0.0,
        "network_demand_pressure_proxy": 0.0,
        "network_throughput_pressure_proxy": 0.0,
        "network_effective_latency_s": 0.0,
        "network_route_latency_avg_s": 0.0,
        "network_effective_loss_proxy_rate": 0.0,
        "network_route_loss_proxy_rate": 0.0,
        "network_route_blocking_ratio": 0.0,
        "network_failed_flow_ratio": 0.0,
        "network_congestion_proxy": 0.0,
        "network_congestion_loss_proxy_rate": 0.0,
        "network_demand_loss_proxy_rate": 0.0,
        "network_pressure_loss_proxy_rate": 0.0,
        "network_effective_delay_variation_s": 0.0,
        "network_route_delay_variation_s": 0.0,
        "network_flow_delay_variation_s": 0.0,
        "network_pressure_delay_variation_s": 0.0,
        "network_effective_available_throughput_mbps": 0.0,
        "network_flow_delivered_capacity_mbps": 0.0,
        "network_time_adjusted_delivered_throughput_mbps": 0.0,
        "network_time_pressure_period_s": float(_NETWORK_TIME_PRESSURE_PERIOD_S),
        "network_time_pressure_phase": 0.0,
        "network_time_pressure_factor": 0.0,
        "network_time_pressure_loss_proxy_rate": 0.0,
        "network_time_pressure_delay_variation_s": 0.0,
        "network_recent_window_s": float(_RECENT_FLOW_KPI_WINDOW_S),
        "network_recent_flow_count": 0.0,
        "network_recent_delivered_throughput_mbps": 0.0,
        "network_recent_latency_s": 0.0,
        "network_recent_loss_proxy_rate": 0.0,
        "network_recent_loss_zero_reason": "NO_RECENT_FLOW_SAMPLE",
        "network_recent_loss_zero_reason_label": _network_quality_zero_reason_label(
            "NO_RECENT_FLOW_SAMPLE"
        ),
        "network_recent_delay_variation_s": 0.0,
        "network_recent_delay_variation_zero_reason": "NO_RECENT_FLOW_SAMPLE",
        "network_recent_delay_variation_zero_reason_label": (
            _network_quality_zero_reason_label("NO_RECENT_FLOW_SAMPLE")
        ),
        "compute_resource_used_gflops_fp32": 0.0,
        "compute_resource_used_gflops_fp64": 0.0,
        "compute_resource_used_gpu_tflops_fp32": 0.0,
        "compute_resource_used_gpu_tflops_fp16": 0.0,
        "compute_resource_used_npu_tops_int8": 0.0,
        "compute_resource_used_memory_gb": 0.0,
        "compute_resource_used_storage_gb": 0.0,
    }


def _satellite_kpi_history_sample(
    node: ComputeNodeState,
    sim_time: float,
) -> SatelliteKpiHistorySample:
    used_fp32 = _compute_node_used_fp32(node)
    return {
        "sim_time": float(sim_time),
        "compute_load_ratio": _compute_node_load_ratio(node, used_fp32),
        "compute_capacity_gflops_fp32": max(0.0, float(node.capacity)),
        "compute_used_gflops_fp32": used_fp32,
        "compute_capacity_gflops_fp64": _compute_node_non_negative_field(
            node,
            "cpu_gflops_fp64",
        ),
        "compute_used_gflops_fp64": _compute_node_non_negative_field(
            node,
            "used_cpu_gflops_fp64",
        ),
        "compute_capacity_gpu_tflops_fp32": _compute_node_non_negative_field(
            node,
            "gpu_tflops_fp32",
        ),
        "compute_used_gpu_tflops_fp32": _compute_node_non_negative_field(
            node,
            "used_gpu_tflops_fp32",
        ),
        "compute_capacity_gpu_tflops_fp16": _compute_node_non_negative_field(
            node,
            "gpu_tflops_fp16",
        ),
        "compute_used_gpu_tflops_fp16": _compute_node_non_negative_field(
            node,
            "used_gpu_tflops_fp16",
        ),
        "compute_capacity_npu_tops_int8": _compute_node_non_negative_field(
            node,
            "npu_tops_int8",
        ),
        "compute_used_npu_tops_int8": _compute_node_non_negative_field(
            node,
            "used_npu_tops_int8",
        ),
        "compute_capacity_memory_gb": _compute_node_non_negative_field(
            node,
            "memory_gb",
        ),
        "compute_used_memory_gb": _compute_node_non_negative_field(
            node,
            "used_memory_gb",
        ),
        "compute_capacity_storage_gb": _compute_node_non_negative_field(
            node,
            "storage_gb",
        ),
        "compute_used_storage_gb": _compute_node_non_negative_field(
            node,
            "used_storage_gb",
        ),
    }


def _service_latency_component_name(metric_name: str) -> str | None:
    components = {
        "service.input_network_latency": "input_network",
        "service.compute_queue_delay": "compute_queue",
        "service.compute_execution_delay": "compute_execution",
        "service.output_network_latency": "output_network",
        "service.total_latency": "total",
    }
    return components.get(metric_name)


_SERVICE_LATENCY_COMPONENT_ORDER = (
    "input_network",
    "compute_queue",
    "compute_execution",
    "output_network",
    "total",
)

_SERVICE_PLACEMENT_METADATA_TAGS = (
    "compute_node_id",
    "service_placement_status",
    "service_placement_policy",
    "service_placement_bottleneck_resource",
    "service_placement_candidate_count",
    "service_placement_capable_candidate_count",
    "service_placement_candidate_queue_label",
)


def _service_latency_component_rank(component: str) -> int:
    try:
        return _SERVICE_LATENCY_COMPONENT_ORDER.index(component)
    except ValueError:
        return len(_SERVICE_LATENCY_COMPONENT_ORDER)


def _service_latency_history_sort_key(
    item: tuple[str, dict[str, float]],
) -> tuple[float, str]:
    task_id, components = item
    return (-float(components.get("total", 0.0)), task_id)


def _service_latency_history_item(
    task_id: str,
    components: dict[str, float],
    metadata: dict[str, str],
    times: dict[str, float],
    timeline: dict[str, dict[str, str | float]],
) -> dict[str, Any]:
    item: dict[str, Any] = {
        "task_id": task_id,
        "input_flow_id": metadata.get("input_flow_id", ""),
        "output_flow_id": metadata.get("output_flow_id", ""),
        "input_route_id": metadata.get("input_route_id", ""),
        "output_route_id": metadata.get("output_route_id", ""),
        "first_sample_sim_time": float(times.get("first_sample_sim_time", 0.0)),
        "last_sample_sim_time": float(times.get("last_sample_sim_time", 0.0)),
        "component_timeline": _service_latency_component_timeline(timeline),
        "complete": "total" in components,
        "input_network_latency_s": float(components.get("input_network", 0.0)),
        "compute_queue_delay_s": float(components.get("compute_queue", 0.0)),
        "compute_execution_delay_s": float(components.get("compute_execution", 0.0)),
        "output_network_latency_s": float(components.get("output_network", 0.0)),
        "total_latency_s": float(components.get("total", 0.0)),
    }
    if any(metadata.get(key) for key in _SERVICE_PLACEMENT_METADATA_TAGS):
        item.update(
            {
                "compute_node_id": metadata.get("compute_node_id", ""),
                "service_placement_status": metadata.get(
                    "service_placement_status",
                    "",
                ),
                "service_placement_policy": metadata.get(
                    "service_placement_policy",
                    "",
                ),
                "service_placement_bottleneck_resource": metadata.get(
                    "service_placement_bottleneck_resource",
                    "",
                ),
                "service_placement_candidate_count": _service_metadata_int(
                    metadata,
                    "service_placement_candidate_count",
                ),
                "service_placement_capable_candidate_count": _service_metadata_int(
                    metadata,
                    "service_placement_capable_candidate_count",
                ),
                "service_placement_candidate_queue_label": metadata.get(
                    "service_placement_candidate_queue_label",
                    "",
                ),
            }
        )
    return item


def _service_metadata_int(metadata: Mapping[str, str], key: str) -> int:
    try:
        return max(0, int(metadata.get(key, "0")))
    except ValueError:
        return 0


def _service_latency_component_timeline(
    timeline: Mapping[str, Mapping[str, str | float]],
) -> list[dict[str, str | float]]:
    return [
        dict(sample)
        for _, sample in sorted(
            timeline.items(),
            key=lambda item: (
                float(item[1].get("sample_sim_time", 0.0)),
                _service_latency_component_rank(item[0]),
                item[0],
            ),
        )
    ]


def _route_constraint_sort_key(route: Route) -> tuple[int, float, float, int, str]:
    return (
        1 if route.available else 0,
        float(route.capacity),
        -float(route.latency),
        -_route_hop_count(route),
        route.route_id,
    )


def _top_constrained_link(links: tuple[LinkState, ...]) -> LinkState | None:
    if not links:
        return None
    return sorted(links, key=_link_constraint_sort_key)[0]


def _link_constraint_sort_key(link: LinkState) -> tuple[float, float, float, str]:
    return (
        -_link_utilization_value(link, missing=-1.0),
        float(link.capacity),
        -float(link.latency),
        _link_id(link),
    )


def _link_utilization_value(link: LinkState, *, missing: float = 0.0) -> float:
    return missing if link.utilization is None else float(link.utilization)


def _route_pressure_proxy(route: Route) -> float:
    demand = _route_demand_capacity(route)
    if route.capacity > 0.0:
        return _clamp_probability(demand / route.capacity)
    return 1.0 if demand > 0.0 else 0.0


def _route_pressure_evidence_item(route: Route) -> RoutePressureEvidenceItem:
    pressure_state = _route_pressure_state(route)
    blocked_reason = _route_pressure_blocked_reason(route, pressure_state)
    demand = _route_demand_capacity(route)
    loss_rate = 0.0 if route.loss_rate is None else float(route.loss_rate)
    return {
        "route_id": route.route_id,
        "flow_id": route.flow_id,
        "available": route.available,
        "pressure_state": pressure_state,
        "blocked_reason": blocked_reason,
        "path_label": " -> ".join(route.path),
        "hop_count": _route_hop_count(route),
        "demand_capacity_mbps": demand,
        "route_capacity_mbps": float(route.capacity),
        "latency_s": float(route.latency),
        "loss_proxy_rate": loss_rate,
        "route_pressure_proxy": _route_pressure_proxy(route),
        "queue_over_demand_mbps": max(0.0, demand - float(route.capacity)),
        "evidence_source": "ROUTE_UPDATE + FLOW_PRESSURE_ADMISSION_V1",
        "packet_level_simulation": False,
    }


def _route_pressure_edge_evidence_items(
    route: Route,
) -> tuple[RoutePressureEdgeEvidenceItem, ...]:
    return tuple(
        _route_pressure_edge_evidence_item(route, item)
        for item in route.pressure_edge_states
    )


def _route_pressure_edge_evidence_item(
    route: Route,
    item: Mapping[str, Any],
) -> RoutePressureEdgeEvidenceItem:
    return {
        "route_id": route.route_id,
        "flow_id": route.flow_id,
        "edge_id": str(item.get("edge_id", "")),
        "source_id": str(item.get("source_id", "")),
        "target_id": str(item.get("target_id", "")),
        "pressure_state": str(item.get("pressure_state", "UNKNOWN")),
        "active_demand_mbps": _float_value(item.get("active_demand_mbps")),
        "incoming_demand_mbps": _float_value(item.get("incoming_demand_mbps")),
        "projected_demand_mbps": _float_value(item.get("projected_demand_mbps")),
        "capacity_mbps": _float_value(item.get("capacity_mbps")),
        "projected_utilization": _float_value(item.get("projected_utilization")),
        "pressure_utilization": _float_value(item.get("pressure_utilization")),
        "queued_demand_mbps": _float_value(item.get("queued_demand_mbps")),
        "queue_delay_s": _float_value(item.get("queue_delay_s")),
        "loss_proxy_rate": _float_value(item.get("loss_proxy_rate")),
        "admission_rejected": item.get("admission_rejected") is True,
        "evidence_source": "ROUTE_UPDATE.pressure_edge_states",
        "packet_level_simulation": False,
    }


def _route_pressure_edge_evidence_sort_key(
    item: RoutePressureEdgeEvidenceItem,
) -> tuple[int, float, float, str, str]:
    state_rank = {
        "ADMISSION_REJECTED": 0,
        "SATURATED": 1,
        "QUEUED": 2,
        "NOMINAL": 3,
    }
    return (
        state_rank.get(str(item["pressure_state"]), 9),
        -float(item["projected_utilization"]),
        -float(item["loss_proxy_rate"]),
        str(item["route_id"]),
        str(item["edge_id"]),
    )


def _float_value(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return 0.0
    if not isfinite(value):
        return 0.0
    return float(value)


def _route_pressure_state(route: Route) -> str:
    if not route.available:
        return "ADMISSION_REJECTED" if route.path else "TOPOLOGY_BLOCKED"
    if _route_demand_capacity(route) > route.capacity:
        return "SATURATED"
    if (route.loss_rate is not None and route.loss_rate > 0.0) or _route_pressure_proxy(route) >= 0.75:
        return "QUEUED"
    return "NOMINAL"


def _route_pressure_blocked_reason(route: Route, pressure_state: str) -> str:
    if pressure_state == "ADMISSION_REJECTED":
        return "flow_pressure_admission_limit"
    if pressure_state == "TOPOLOGY_BLOCKED":
        return "no_available_route"
    if pressure_state == "SATURATED":
        return "demand_exceeds_route_capacity"
    if pressure_state == "QUEUED":
        return "route_pressure_or_loss_proxy"
    return "none"


def _route_pressure_evidence_sort_key(
    item: RoutePressureEvidenceItem,
) -> tuple[int, float, float, str]:
    state_rank = {
        "ADMISSION_REJECTED": 0,
        "TOPOLOGY_BLOCKED": 1,
        "SATURATED": 2,
        "QUEUED": 3,
        "NOMINAL": 4,
    }
    return (
        state_rank.get(str(item["pressure_state"]), 9),
        -float(item["route_pressure_proxy"]),
        -float(item["loss_proxy_rate"]),
        str(item["route_id"]),
    )


def _link_id(link: LinkState) -> str:
    return f"{link.source_id}->{link.target_id}"


def _link_touches_satellite(link: LinkState, satellite_id: str) -> bool:
    return link.source_id == satellite_id or link.target_id == satellite_id


def _is_space_link(link: LinkState) -> bool:
    return _is_satellite_id(link.source_id) and _is_satellite_id(link.target_id)


def _is_access_link(link: LinkState) -> bool:
    return _is_satellite_id(link.source_id) != _is_satellite_id(link.target_id)


def _is_satellite_id(node_id: str) -> bool:
    return node_id.lower().startswith("sat-")


def _route_hop_count(route: Route) -> int:
    return max(0, len(route.path) - 1)


def _compute_node_used_fp32(node: ComputeNodeState | None) -> float:
    if node is None:
        return 0.0
    used = getattr(node, "used_cpu_gflops_fp32", None)
    if isinstance(used, (int, float)) and isfinite(used):
        return max(0.0, float(used))
    return _compute_node_legacy_used_fp32(node)


def _compute_node_legacy_used_fp32(node: ComputeNodeState | None) -> float:
    if node is None:
        return 0.0
    capacity = max(0.0, float(node.capacity))
    available = max(0.0, min(capacity, float(node.available_capacity)))
    return capacity - available


def _compute_cpu_fp32_bottleneck_used(
    nodes: tuple[ComputeNodeState, ...],
) -> float:
    used = 0.0
    for node in nodes:
        if node.resource_usage_mode == "RESOURCE_VECTOR_ESTIMATED":
            used += _compute_node_non_negative_field(node, "used_cpu_gflops_fp32")
        else:
            used += _compute_node_legacy_used_fp32(node)
    return float(used)


def _compute_node_load_ratio(
    node: ComputeNodeState | None,
    used_fp32: float,
) -> float:
    if node is None:
        return 0.0
    load_ratio = getattr(node, "load_ratio", None)
    if isinstance(load_ratio, (int, float)) and isfinite(load_ratio):
        return _clamp_probability(float(load_ratio))
    capacity = max(0.0, float(node.capacity))
    return _clamp_probability(used_fp32 / capacity) if capacity > 0.0 else 0.0


def _compute_node_non_negative_field(
    node: ComputeNodeState | None,
    field_name: str,
) -> float:
    if node is None:
        return 0.0
    value = getattr(node, field_name, 0.0)
    if isinstance(value, (int, float)) and isfinite(value):
        return max(0.0, float(value))
    return 0.0


def _compute_resource_total(
    nodes: tuple[ComputeNodeState, ...],
    field_name: str,
) -> float:
    return float(
        sum(max(0.0, float(getattr(node, field_name))) for node in nodes)
    )


def _compute_resource_bottleneck(
    resources: tuple[tuple[str, str, float, float], ...],
) -> dict[str, str | float | int]:
    active = tuple(
        (
            resource,
            label,
            max(0.0, float(total)),
            max(0.0, float(used)),
        )
        for resource, label, total, used in resources
        if total > 0.0
    )
    if not active:
        return {
            "resource": "none",
            "label": "No compute resource capacity",
            "utilization": 0.0,
            "used": 0.0,
            "total": 0.0,
            "available": 0.0,
            "status": "IDLE",
            "active_dimension_count": 0,
        }

    ranked = tuple(
        (
            min(used, total) / total,
            min(used, total),
            -index,
            resource,
            label,
            total,
        )
        for index, (resource, label, total, used) in enumerate(active)
    )
    utilization, used, _rank, resource, label, total = max(ranked)
    if utilization >= 0.9:
        status = "SATURATED"
    elif utilization >= 0.7:
        status = "PRESSURED"
    elif utilization > 0.0:
        status = "NORMAL"
    else:
        status = "IDLE"
    return {
        "resource": resource,
        "label": label,
        "utilization": float(utilization),
        "used": float(used),
        "total": float(total),
        "available": float(max(0.0, total - used)),
        "status": status,
        "active_dimension_count": len(active),
    }


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
        "TIME_PRESSURE_LOSS_PROXY": "时间窗口压力损耗代理",
        "ROUTE_LATENCY_VARIATION": "路由时延离散度",
        "FLOW_LATENCY_VARIATION": "流完成时延离散度",
        "PRESSURE_DELAY_VARIATION": "业务压力时延扰动",
        "TIME_PRESSURE_DELAY_VARIATION": "时间窗口压力时延扰动",
    }
    return labels.get(source, source)


def _network_quality_loss_zero_reason(
    effective_loss_proxy_rate: float,
    *,
    route_count: int,
    flow_count: int,
) -> str:
    if effective_loss_proxy_rate > 0.0:
        return "POSITIVE_PROXY"
    if route_count == 0 and flow_count == 0:
        return "NO_ROUTE_OR_FLOW_SAMPLE"
    return "NO_LOSS_PROXY_TRIGGERED"


def _network_quality_delay_variation_zero_reason(
    effective_delay_variation_proxy: float,
    *,
    route_latency_count: int,
    flow_latency_count: int,
) -> str:
    if effective_delay_variation_proxy > 0.0:
        return "POSITIVE_PROXY"
    if route_latency_count == 0 and flow_latency_count == 0:
        return "NO_ROUTE_OR_FLOW_SAMPLE"
    if route_latency_count <= 1 and flow_latency_count <= 1:
        return "INSUFFICIENT_VARIATION_SAMPLE"
    return "NO_LATENCY_VARIATION"


def _network_recent_loss_zero_reason(
    recent_loss_proxy_rate: float,
    *,
    recent_flow_count: int,
) -> str:
    if recent_loss_proxy_rate > 0.0:
        return "POSITIVE_PROXY"
    if recent_flow_count == 0:
        return "NO_RECENT_FLOW_SAMPLE"
    return "NO_RECENT_FLOW_LOSS"


def _network_recent_delay_variation_zero_reason(
    recent_delay_variation_proxy: float,
    *,
    recent_flow_count: int,
    recent_latency_count: int,
) -> str:
    if recent_delay_variation_proxy > 0.0:
        return "POSITIVE_PROXY"
    if recent_flow_count == 0 or recent_latency_count == 0:
        return "NO_RECENT_FLOW_SAMPLE"
    if recent_latency_count <= 1:
        return "INSUFFICIENT_RECENT_FLOW_LATENCY_SAMPLE"
    return "NO_RECENT_FLOW_LATENCY_VARIATION"


def _network_quality_zero_reason_label(reason: str) -> str:
    labels = {
        "POSITIVE_PROXY": "当前代理指标为正值",
        "NO_ROUTE_OR_FLOW_SAMPLE": "暂无路由或流样本，零值仅表示代理未触发",
        "NO_LOSS_PROXY_TRIGGERED": (
            "路由阻塞、失败流、链路拥塞和业务压力均未触发损耗代理"
        ),
        "INSUFFICIENT_VARIATION_SAMPLE": "时延样本不足，无法形成离散度代理",
        "NO_LATENCY_VARIATION": "路由/流时延样本未产生变化",
        "NO_RECENT_FLOW_SAMPLE": "最近窗口暂无完成流，零值仅表示窗口未形成样本",
        "NO_RECENT_FLOW_LOSS": "最近窗口完成流均成功，未触发失败流损耗代理",
        "INSUFFICIENT_RECENT_FLOW_LATENCY_SAMPLE": (
            "最近窗口时延样本不足，无法形成抖动代理"
        ),
        "NO_RECENT_FLOW_LATENCY_VARIATION": "最近窗口完成流时延未产生变化",
    }
    return labels.get(reason, reason)


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
