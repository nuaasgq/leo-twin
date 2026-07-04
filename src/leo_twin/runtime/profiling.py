"""Lightweight runtime tick profiling helpers."""

from __future__ import annotations

from collections import defaultdict
from time import perf_counter
from typing import Protocol

from leo_twin.core import SimulationKernel, SimulationModule
from leo_twin.models.compute.contracts import COMPUTE_NODE_UPDATE
from leo_twin.schema import EventType, SimEvent


PROFILE_TIMING_FIELDS: tuple[str, ...] = (
    "orbit_batch_update_time_ms",
    "network_batch_ingestion_time_ms",
    "access_update_time_ms",
    "space_space_candidate_update_time_ms",
    "flow_arrival_processing_time_ms",
    "route_update_time_ms",
    "compute_task_arrival_processing_time_ms",
    "compute_queue_update_time_ms",
    "metrics_aggregation_time_ms",
    "snapshot_projection_time_ms",
    "total_tick_time_ms",
)


class RuntimeTickObserver(Protocol):
    """Observation hook used by runtime sessions around one kernel run."""

    def reset(self) -> None:
        ...

    def summary(
        self,
        *,
        snapshot_projection_time_ms: float,
        processed_event_count: int,
    ) -> dict[str, object]:
        ...


class RuntimeTickProfiler:
    """Collect per-module timing for one runtime advance tick."""

    def __init__(self) -> None:
        self._modules: list[SimulationModule] = []
        self.reset()

    def wrap(self, module: SimulationModule) -> SimulationModule:
        self._modules.append(module)
        return ProfiledSimulationModule(module, self)

    def reset(self) -> None:
        self._timings_ms = {field: 0.0 for field in PROFILE_TIMING_FIELDS}
        self._event_type_counts: dict[str, int] = defaultdict(int)
        for module in getattr(self, "_modules", ()):
            reset = getattr(module, "reset_profiling", None)
            if callable(reset):
                reset()

    def record_module_event(
        self,
        *,
        module_name: str,
        event_type: str,
        elapsed_ms: float,
    ) -> None:
        normalized_event_type = str(event_type)
        self._event_type_counts[normalized_event_type] += 1
        component = _component_for(module_name, normalized_event_type)
        if component is not None:
            self._timings_ms[component] += max(0.0, float(elapsed_ms))

    def summary(
        self,
        *,
        snapshot_projection_time_ms: float,
        processed_event_count: int,
    ) -> dict[str, object]:
        timings = dict(self._timings_ms)
        for module in self._modules:
            provider = getattr(module, "profiling_summary", None)
            if not callable(provider):
                continue
            for key, value in provider().items():
                if key in timings:
                    timings[key] += max(0.0, float(value))
        timings["snapshot_projection_time_ms"] = max(
            0.0,
            float(snapshot_projection_time_ms),
        )
        summary: dict[str, object] = {
            key: round(timings.get(key, 0.0), 6) for key in PROFILE_TIMING_FIELDS
        }
        summary["processed_event_count"] = int(processed_event_count)
        summary["event_type_counts"] = {
            key: self._event_type_counts[key] for key in sorted(self._event_type_counts)
        }
        return summary


class ProfiledSimulationModule(SimulationModule):
    """Delegating module wrapper that records handler wall time."""

    def __init__(
        self,
        module: SimulationModule,
        profiler: RuntimeTickProfiler,
    ) -> None:
        self._module = module
        self._profiler = profiler

    def name(self) -> str:
        return self._module.name()

    def on_event(self, event: SimEvent, kernel: SimulationKernel) -> None:
        started = perf_counter()
        try:
            self._module.on_event(event, kernel)
        finally:
            elapsed_ms = (perf_counter() - started) * 1000.0
            self._profiler.record_module_event(
                module_name=self.name(),
                event_type=str(event.event_type),
                elapsed_ms=elapsed_ms,
            )


def empty_profiling_summary(
    *,
    snapshot_projection_time_ms: float = 0.0,
    processed_event_count: int = 0,
) -> dict[str, object]:
    summary: dict[str, object] = {
        key: 0.0 for key in PROFILE_TIMING_FIELDS
    }
    summary["snapshot_projection_time_ms"] = round(
        max(0.0, float(snapshot_projection_time_ms)),
        6,
    )
    summary["processed_event_count"] = int(processed_event_count)
    summary["event_type_counts"] = {}
    return summary


def _component_for(module_name: str, event_type: str) -> str | None:
    if module_name == "orbit" and event_type == EventType.ORBIT_TRIGGER.value:
        return "orbit_batch_update_time_ms"
    if module_name == "network" and event_type == EventType.ORBIT_BATCH_UPDATE.value:
        return "network_batch_ingestion_time_ms"
    if module_name == "network" and event_type == EventType.FLOW_ARRIVAL.value:
        return "flow_arrival_processing_time_ms"
    if event_type == EventType.ROUTE_UPDATE.value:
        return "route_update_time_ms"
    if module_name == "compute" and event_type == EventType.TASK_ARRIVAL.value:
        return "compute_task_arrival_processing_time_ms"
    if module_name == "compute" and event_type in {
        EventType.TASK_START.value,
        EventType.TASK_FINISH.value,
        COMPUTE_NODE_UPDATE,
    }:
        return "compute_queue_update_time_ms"
    if module_name == "metrics":
        return "metrics_aggregation_time_ms"
    return None
