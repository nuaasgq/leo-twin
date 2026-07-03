"""Runnable full-system pipeline demo for orbit-network-compute coupling."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from collections.abc import Mapping

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from leo_twin.core import SimulationKernel, SimulationModule
from leo_twin.models.compute import ComputeNode, RouteAwareComputeEngine, TaskPlacementDecision
from leo_twin.models.network import (
    GroundEndpoint,
    NetworkStackRuntime,
    PositionDrivenNetworkEngine,
    build_default_leo_protocol_stack,
)
from leo_twin.models.orbit import KeplerianOrbitEngine
from leo_twin.services.metrics import MetricsCollector
from leo_twin.schema import (
    EventType,
    FlowRequest,
    OrbitalElementSet,
    Route,
    SimEvent,
    TaskRequest,
)


EARTH_RADIUS_KM = 6371.0


@dataclass(frozen=True)
class FullSystemPipelineResult:
    """Deterministic output of the full-system pipeline demo."""

    processed_event_types: tuple[str, ...]
    metrics_event_types: tuple[str, ...]
    metrics_summary: Mapping[str, str | float | int | bool]
    stack_layer_statuses: tuple[tuple[str, str], ...]
    scheduled_tasks: tuple[TaskPlacementDecision, ...]


class NetworkStackObserver(SimulationModule):
    """Observe route updates and record deterministic stack layer statuses."""

    def __init__(
        self,
        stack_runtime: NetworkStackRuntime,
        flow_request: FlowRequest,
    ) -> None:
        self._stack_runtime = stack_runtime
        self._flow_request = flow_request
        self.stack_layer_statuses: list[tuple[str, str]] = []

    def name(self) -> str:
        return "trace"

    def on_event(self, event: SimEvent, kernel: SimulationKernel) -> None:
        if event.event_type != EventType.ROUTE_UPDATE:
            return
        route = event.payload
        if not isinstance(route, Route):
            raise TypeError("ROUTE_UPDATE payload must be Route")
        trace = self._stack_runtime.process_flow(self._flow_request, route)
        self.stack_layer_statuses.extend(
            (layer.layer.value, layer.status) for layer in trace.layers
        )


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
        update_targets=("metrics", "network"),
    )
    flow_request = FlowRequest(
        flow_id="flow-001",
        source_id="user-east",
        target_id="node-a",
        demand_capacity=1.0,
    )
    network = PositionDrivenNetworkEngine(
        endpoints=(
            GroundEndpoint(
                endpoint_id="user-east",
                position=(EARTH_RADIUS_KM, 0.0, 0.0),
                min_elevation_deg=10.0,
                max_range_km=2000.0,
            ),
        ),
        compute_node_ids=("node-a",),
        route_targets=("compute", "metrics", "trace"),
        link_capacity=5.0,
        propagation_speed_km_s=629.0,
        base_latency_s=1.0,
        cell_size_km=1000.0,
    )
    trace_observer = NetworkStackObserver(
        stack_runtime=NetworkStackRuntime(build_default_leo_protocol_stack()),
        flow_request=flow_request,
    )
    compute = RouteAwareComputeEngine(nodes=(ComputeNode("node-a", capacity=10.0),))
    metrics = MetricsCollector()
    kernel.register_module(orbit)
    kernel.register_module(network)
    kernel.register_module(trace_observer)
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
    kernel.schedule_event(
        SimEvent(
            event_id="zz-flow",
            sim_time=0.0,
            priority=0,
            source="scenario",
            target="network",
            event_type=EventType.FLOW_ARRIVAL.value,
            payload=flow_request,
        )
    )
    processed_events = kernel.run()
    return FullSystemPipelineResult(
        processed_event_types=tuple(event.event_type for event in processed_events),
        metrics_event_types=tuple(str(event["event_type"]) for event in metrics.event_log()),
        metrics_summary=metrics.summary(),
        stack_layer_statuses=tuple(trace_observer.stack_layer_statuses),
        scheduled_tasks=compute.scheduled_tasks(),
    )


def main() -> None:
    """Print a compact deterministic demo summary."""

    result = run_full_system_pipeline_demo()
    print("processed_event_types=", ",".join(result.processed_event_types))
    print("metrics_event_types=", ",".join(result.metrics_event_types))
    print("metrics_summary=", dict(result.metrics_summary))
    print(
        "stack_layer_statuses=",
        ",".join(f"{layer}:{status}" for layer, status in result.stack_layer_statuses),
    )
    print("scheduled_tasks=", result.scheduled_tasks)


if __name__ == "__main__":
    main()
