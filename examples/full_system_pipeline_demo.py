"""Runnable full-system pipeline demo for orbit-network-compute coupling."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from leo_twin.core import SimulationKernel, SimulationModule
from leo_twin.models.compute import ComputeNode, RouteAwareComputeEngine, TaskPlacementDecision
from leo_twin.models.network import (
    GroundEndpoint,
    NetworkStackRuntime,
    PositionDrivenAccessModel,
    build_default_leo_protocol_stack,
)
from leo_twin.models.orbit import KeplerianOrbitEngine
from leo_twin.schema import (
    EventType,
    FlowRequest,
    OrbitalElementSet,
    Route,
    SatelliteState,
    SimEvent,
    TaskRequest,
)


EARTH_RADIUS_KM = 6371.0


@dataclass(frozen=True)
class FullSystemPipelineResult:
    """Deterministic output of the full-system pipeline demo."""

    processed_event_types: tuple[str, ...]
    metrics_event_types: tuple[str, ...]
    stack_layer_statuses: tuple[tuple[str, str], ...]
    scheduled_tasks: tuple[TaskPlacementDecision, ...]


class AccessRouteBridge(SimulationModule):
    """Convert satellite state updates into deterministic route updates."""

    def __init__(
        self,
        access_model: PositionDrivenAccessModel,
        stack_runtime: NetworkStackRuntime,
        flow_request: FlowRequest,
        route_target: str = "compute",
    ) -> None:
        self._access_model = access_model
        self._stack_runtime = stack_runtime
        self._flow_request = flow_request
        self._route_target = route_target
        self._event_sequence = 0
        self.stack_layer_statuses: list[tuple[str, str]] = []

    def name(self) -> str:
        return "access"

    def on_event(self, event: SimEvent, kernel: SimulationKernel) -> None:
        if event.event_type != EventType.ORBIT_UPDATE:
            return
        state = event.payload
        if not isinstance(state, SatelliteState):
            raise TypeError("ORBIT_UPDATE payload must be SatelliteState")
        access_candidates = self._access_model.compute_access((state,))
        if not access_candidates:
            return
        candidate = access_candidates[0]
        route = Route(
            route_id=f"route:{candidate.satellite_id}:{candidate.endpoint_id}",
            flow_id=self._flow_request.flow_id,
            path=(candidate.endpoint_id, candidate.satellite_id, "node-a"),
            latency=2.0,
            capacity=5.0,
            available=True,
        )
        trace = self._stack_runtime.process_flow(self._flow_request, route)
        self.stack_layer_statuses.extend(
            (layer.layer.value, layer.status) for layer in trace.layers
        )
        kernel.schedule_event(
            self._route_event(dispatch_time=event.sim_time, route=route)
        )

    def _route_event(self, dispatch_time: float, route: Route) -> SimEvent:
        self._event_sequence += 1
        return SimEvent(
            event_id=f"access:route:{self._event_sequence:08d}",
            sim_time=dispatch_time,
            priority=0,
            source="access",
            target=self._route_target,
            event_type=EventType.ROUTE_UPDATE.value,
            payload=route,
        )


class MetricsSink(SimulationModule):
    """Collect demo metric-facing events."""

    def __init__(self) -> None:
        self.events: list[SimEvent] = []

    def name(self) -> str:
        return "metrics"

    def on_event(self, event: SimEvent, kernel: SimulationKernel) -> None:
        self.events.append(event)


def run_full_system_pipeline_demo() -> FullSystemPipelineResult:
    """Run the deterministic full-system pipeline demo."""

    kernel = SimulationKernel()
    orbit = KeplerianOrbitEngine(
        elements=(
            OrbitalElementSet(
                satellite_id="sat-001",
                epoch=0.0,
                semi_major_axis_km=7000.0,
                eccentricity=0.0,
                inclination_deg=0.0,
                raan_deg=0.0,
                argument_of_perigee_deg=0.0,
                mean_anomaly_deg=0.0,
            ),
        ),
        update_targets=("access", "metrics"),
    )
    flow_request = FlowRequest(
        flow_id="flow-001",
        source_id="user-east",
        target_id="node-a",
        demand_capacity=1.0,
    )
    access = AccessRouteBridge(
        access_model=PositionDrivenAccessModel(
            endpoints=(
                GroundEndpoint(
                    endpoint_id="user-east",
                    position=(EARTH_RADIUS_KM, 0.0, 0.0),
                    min_elevation_deg=10.0,
                    max_range_km=2000.0,
                ),
            ),
            cell_size_km=1000.0,
        ),
        stack_runtime=NetworkStackRuntime(build_default_leo_protocol_stack()),
        flow_request=flow_request,
    )
    compute = RouteAwareComputeEngine(nodes=(ComputeNode("node-a", capacity=10.0),))
    metrics = MetricsSink()
    kernel.register_module(orbit)
    kernel.register_module(access)
    kernel.register_module(compute)
    kernel.register_module(metrics)
    kernel.schedule_event(
        SimEvent(
            event_id="00-task",
            sim_time=0.0,
            priority=0,
            source="scenario",
            target="compute",
            event_type=EventType.TASK_ARRIVAL.value,
            payload=TaskRequest(
                task_id="flow-001",
                source_id="user-east",
                submit_time=0.0,
                compute_demand=20.0,
                data_size=10.0,
            ),
        )
    )
    kernel.schedule_event(
        SimEvent(
            event_id="01-orbit",
            sim_time=0.0,
            priority=0,
            source="scenario",
            target="orbit",
            event_type=EventType.ORBIT_TRIGGER.value,
            payload=None,
        )
    )
    processed_events = kernel.run()
    return FullSystemPipelineResult(
        processed_event_types=tuple(event.event_type for event in processed_events),
        metrics_event_types=tuple(event.event_type for event in metrics.events),
        stack_layer_statuses=tuple(access.stack_layer_statuses),
        scheduled_tasks=compute.scheduled_tasks(),
    )


def main() -> None:
    """Print a compact deterministic demo summary."""

    result = run_full_system_pipeline_demo()
    print("processed_event_types=", ",".join(result.processed_event_types))
    print("metrics_event_types=", ",".join(result.metrics_event_types))
    print(
        "stack_layer_statuses=",
        ",".join(f"{layer}:{status}" for layer, status in result.stack_layer_statuses),
    )
    print("scheduled_tasks=", result.scheduled_tasks)


if __name__ == "__main__":
    main()
