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
from leo_twin.models.network import (
    GroundEndpoint,
    PositionDrivenNetworkEngine,
    LinkBudgetCalculator,
    RadioTerminalProfile,
    RainFadeProfile,
    default_transport_runtime,
)
from leo_twin.models.orbit import KeplerianOrbitEngine
from leo_twin.schema import (
    AntennaProfile,
    ChannelProfile,
    EventType,
    LinkMedium,
    SimEvent,
    TransportProtocol,
)
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
        link_budget_calculator=_space_ground_budget(resolved_config),
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
        transport_runtime=default_transport_runtime(
            TransportProtocol(str(resolved_config.transport_protocol))
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


def _space_ground_budget(
    config: FullSystemScenarioBuilderConfig,
) -> LinkBudgetCalculator:
    antenna = AntennaProfile(
        antenna_id="generated-ka-terminal",
        gain_dbi=36.0,
        beam_width_deg=4.0,
        steering_mode="electronic",
    )
    rain_profile = (
        None
        if config.rain_rate_mm_h == 0.0
        or config.rain_attenuation_coefficient_db_per_km_per_mm_h == 0.0
        or config.rain_effective_path_km == 0.0
        else RainFadeProfile(
            rain_rate_mm_h=config.rain_rate_mm_h,
            attenuation_coefficient_db_per_km_per_mm_h=(
                config.rain_attenuation_coefficient_db_per_km_per_mm_h
            ),
            effective_path_km=config.rain_effective_path_km,
        )
    )
    return LinkBudgetCalculator(
        transmit_terminal=RadioTerminalProfile(
            terminal_id="generated-sat-terminal",
            antenna=antenna,
            transmit_power_dbw=20.0,
            system_loss_db=1.0,
        ),
        receive_terminal=RadioTerminalProfile(
            terminal_id="generated-ground-terminal",
            antenna=antenna,
            transmit_power_dbw=0.0,
            system_loss_db=1.0,
            noise_temperature_k=290.0,
        ),
        channel=ChannelProfile(
            channel_id="generated-space-ground-ka",
            medium=LinkMedium.SPACE_GROUND,
            carrier_frequency_hz=config.carrier_frequency_hz,
            bandwidth_hz=config.channel_bandwidth_hz,
            loss_model_name="free_space_budget",
        ),
        atmospheric_loss_db=2.0,
        polarization_loss_db=0.5,
        implementation_loss_db=1.0,
        rain_fade_profile=rain_profile,
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
