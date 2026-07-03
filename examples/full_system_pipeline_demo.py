"""Runnable full-system pipeline demo for orbit-network-compute coupling."""

from __future__ import annotations

import sys
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "src"))

from leo_twin.core import SimulationKernel, SimulationModule
from examples.full_system_pipeline_config import load_full_system_pipeline_config
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

    config = load_full_system_pipeline_config()
    kernel = SimulationKernel()
    orbit = KeplerianOrbitEngine(
        elements=(
            OrbitalElementSet(
                satellite_id=str(config.orbit["satellite_id"]),
                epoch=float(config.orbit["epoch"]),
                semi_major_axis_km=float(config.orbit["semi_major_axis_km"]),
                eccentricity=float(config.orbit["eccentricity"]),
                inclination_deg=float(config.orbit["inclination_deg"]),
                raan_deg=float(config.orbit["raan_deg"]),
                argument_of_perigee_deg=float(config.orbit["argument_of_perigee_deg"]),
                mean_anomaly_deg=float(config.orbit["mean_anomaly_deg"]),
            ),
        ),
        update_targets=("metrics", "network"),
    )
    flow_request = FlowRequest(
        flow_id=str(config.flow["flow_id"]),
        source_id=str(config.flow["source_id"]),
        target_id=str(config.flow["target_id"]),
        demand_capacity=float(config.flow["demand_capacity"]),
    )
    network = PositionDrivenNetworkEngine(
        endpoints=(
            GroundEndpoint(
                endpoint_id=str(config.ground_endpoint["endpoint_id"]),
                position=_vector3(config.ground_endpoint["position"]),
                min_elevation_deg=float(config.ground_endpoint["min_elevation_deg"]),
                max_range_km=float(config.ground_endpoint["max_range_km"]),
            ),
        ),
        compute_node_ids=(str(config.compute["node_id"]),),
        route_targets=("compute", "metrics", "trace"),
        link_capacity=float(config.network["link_capacity"]),
        propagation_speed_km_s=float(config.network["propagation_speed_km_s"]),
        base_latency_s=float(config.network["base_latency_s"]),
        cell_size_km=float(config.network["cell_size_km"]),
    )
    trace_observer = NetworkStackObserver(
        stack_runtime=NetworkStackRuntime(build_default_leo_protocol_stack()),
        flow_request=flow_request,
    )
    compute = RouteAwareComputeEngine(
        nodes=(
            ComputeNode(
                str(config.compute["node_id"]),
                capacity=float(config.compute["capacity"]),
            ),
        )
    )
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
                task_id=str(config.task["task_id"]),
                source_id=str(config.task["source_id"]),
                submit_time=float(config.task["submit_time"]),
                compute_demand=float(config.task["compute_demand"]),
                data_size=float(config.task["data_size"]),
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


def _vector3(value: object) -> tuple[float, float, float]:
    if not isinstance(value, (list, tuple)) or len(value) != 3:
        raise TypeError("position must contain three numeric values")
    return (float(value[0]), float(value[1]), float(value[2]))


if __name__ == "__main__":
    main()
