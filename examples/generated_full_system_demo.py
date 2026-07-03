"""Generated full-system demo assembled from deterministic scenario inputs."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "src"))

from leo_twin.core import SimulationKernel
from leo_twin.models.compute import ComputeNode, RouteAwareComputeEngine, TaskPlacementDecision
from leo_twin.models.network import GroundEndpoint, PositionDrivenNetworkEngine
from leo_twin.models.orbit import KeplerianOrbitEngine
from leo_twin.schema import EventType, SimEvent
from leo_twin.services.metrics import MetricsCollector
from leo_twin.services.scenario_builder import (
    FullSystemScenarioBuilderConfig,
    build_full_system_scenario,
    load_full_system_scenario_builder_config,
)


@dataclass(frozen=True)
class GeneratedFullSystemDemoResult:
    """Deterministic result for a generated full-system demo run."""

    processed_event_types: tuple[str, ...]
    metrics_summary: dict[str, str | float | int | bool]
    scheduled_tasks: tuple[TaskPlacementDecision, ...]
    satellite_count: int
    ground_endpoint_count: int
    compute_node_count: int
    flow_count: int
    active_link_count: int


def run_generated_full_system_demo(
    config: FullSystemScenarioBuilderConfig | None = None,
) -> GeneratedFullSystemDemoResult:
    """Build and run a deterministic generated full-system demo."""

    resolved_config = config or load_full_system_scenario_builder_config()
    scenario = build_full_system_scenario(resolved_config)
    kernel = SimulationKernel()
    orbit = KeplerianOrbitEngine(
        elements=scenario.orbit_elements,
        update_targets=("metrics", "network"),
        earth_rotation_rate_rad_s=resolved_config.earth_rotation_rate_rad_s,
    )
    network = PositionDrivenNetworkEngine(
        endpoints=tuple(
            GroundEndpoint(
                endpoint_id=endpoint.endpoint_id,
                position=endpoint.position,
                min_elevation_deg=endpoint.min_elevation_deg,
                max_range_km=endpoint.max_range_km,
            )
            for endpoint in scenario.ground_endpoints
        ),
        compute_node_ids=tuple(node.node_id for node in scenario.compute_nodes),
        route_targets=("compute", "metrics"),
        link_capacity=100.0,
        propagation_speed_km_s=299792.458,
        cell_size_km=5000.0,
        space_link_max_range_km=(
            resolved_config.space_link_max_range_km
            if resolved_config.space_link_max_range_km > 0.0
            else None
        ),
        space_link_capacity=resolved_config.space_link_capacity,
        space_link_cell_size_km=(
            resolved_config.space_link_cell_size_km
            if resolved_config.space_link_cell_size_km > 0.0
            else None
        ),
    )
    compute = RouteAwareComputeEngine(
        nodes=tuple(
            ComputeNode(node.node_id, capacity=node.capacity)
            for node in scenario.compute_nodes
        )
    )
    metrics = MetricsCollector()

    for module in (orbit, network, compute, metrics):
        kernel.register_module(module)

    for task_index, task in enumerate(scenario.tasks):
        kernel.schedule_event(
            SimEvent(
                event_id=f"00-task:{task_index:05d}",
                sim_time=0.0,
                priority=0,
                source="scenario",
                target="compute",
                event_type=EventType.TASK_ARRIVAL.value,
                payload=task,
            )
        )
    kernel.schedule_event(
        SimEvent(
            event_id="10-orbit:00000",
            sim_time=0.0,
            priority=0,
            source="scenario",
            target="orbit",
            event_type=EventType.ORBIT_TRIGGER.value,
            payload=None,
        )
    )
    for flow_index, flow in enumerate(scenario.flows):
        kernel.schedule_event(
            SimEvent(
                event_id=f"zz-flow:{flow_index:05d}",
                sim_time=0.0,
                priority=0,
                source="scenario",
                target="network",
                event_type=EventType.FLOW_ARRIVAL.value,
                payload=flow,
            )
        )

    processed = kernel.run()
    return GeneratedFullSystemDemoResult(
        processed_event_types=tuple(event.event_type for event in processed),
        metrics_summary=dict(metrics.summary()),
        scheduled_tasks=compute.scheduled_tasks(),
        satellite_count=len(scenario.orbit_elements),
        ground_endpoint_count=len(scenario.ground_endpoints),
        compute_node_count=len(scenario.compute_nodes),
        flow_count=len(scenario.flows),
        active_link_count=len(network.active_link_states()),
    )


def main() -> None:
    """Print a compact generated demo summary."""

    result = run_generated_full_system_demo()
    print("processed_event_count=", len(result.processed_event_types))
    print("metrics_summary=", result.metrics_summary)
    print("scheduled_tasks=", len(result.scheduled_tasks))
    print("active_link_count=", result.active_link_count)


if __name__ == "__main__":
    main()
