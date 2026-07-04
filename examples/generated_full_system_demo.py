"""Generated full-system demo assembled from deterministic scenario inputs."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "src"))

from leo_twin.core import SimulationKernel
from leo_twin.models.compute import (
    ComputeNode,
    ComputeSchedulingPolicy,
    ComputeSchedulingRuntime,
    RouteAwareComputeEngine,
    TaskPlacementDecision,
)
from leo_twin.models.network import (
    ApertureAntennaSpec,
    ChannelBudgetSelector,
    GroundEndpoint,
    PositionDrivenNetworkEngine,
    LinkBudgetCalculator,
    NetworkStackRuntime,
    RadioTerminalProfile,
    RainFadeProfile,
    RoutingCostProfile,
    RoutingRuntime,
    TransportProfile,
    TransportRuntime,
    NetworkStackTrace,
    build_default_leo_protocol_stack,
    default_application_runtime,
    default_data_link_runtime,
    default_transport_runtime,
)
from leo_twin.models.orbit import J2SecularDriftProfile, KeplerianOrbitEngine
from leo_twin.schema import (
    AntennaProfile,
    ApplicationProtocol,
    ChannelProfile,
    DataLinkProtocol,
    EventType,
    LinkMedium,
    LinkState,
    RoutingProtocol,
    SimEvent,
    TransportProtocol,
)
from leo_twin.services.metrics import MetricsCollector
from leo_twin.services.scenario_builder import (
    GeneratedFullSystemScenario,
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
    active_links: tuple[LinkState, ...]
    network_stack_traces: tuple[NetworkStackTrace, ...]


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
        j2_profile=_j2_profile_for(resolved_config.orbit_propagation_model),
    )
    space_ground_budget = _space_ground_budget(resolved_config)
    space_space_budget = _space_space_budget(resolved_config)
    transport_protocol = TransportProtocol(str(resolved_config.transport_protocol))
    application_protocol = ApplicationProtocol(str(resolved_config.application_protocol))
    data_link_protocol = DataLinkProtocol(str(resolved_config.datalink_mac_protocol))
    application_runtime = default_application_runtime(application_protocol)
    data_link_runtime = default_data_link_runtime(data_link_protocol)
    transport_runtime = _transport_runtime(resolved_config, transport_protocol)
    routing_profile = RoutingCostProfile(
        latency_weight=resolved_config.routing_latency_weight,
        inverse_capacity_weight=resolved_config.routing_inverse_capacity_weight,
        hop_weight=resolved_config.routing_hop_weight,
    )
    routing_runtime = RoutingRuntime(
        RoutingProtocol(str(resolved_config.routing_protocol)),
        cost_profile=routing_profile,
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
        link_budget_selector=ChannelBudgetSelector(
            calculators=(space_ground_budget, space_space_budget)
        ),
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
        application_runtime=application_runtime,
        data_link_runtime=data_link_runtime,
        transport_runtime=transport_runtime,
        routing_runtime=routing_runtime,
        static_links=_compute_gateway_links(scenario, resolved_config),
        stack_runtime=NetworkStackRuntime(
            build_default_leo_protocol_stack(
                application_protocol=application_protocol,
                transport_protocol=transport_protocol,
                routing_protocol=RoutingProtocol(str(resolved_config.routing_protocol)),
                data_link_protocol=data_link_protocol,
            ),
            application_profile=application_runtime.profile,
            antenna=space_ground_budget.transmit_terminal.antenna,
            channel=space_ground_budget.channel,
            data_link_profile=data_link_runtime.profile,
            transport_profile=transport_runtime.profile,
            routing_cost_profile=routing_profile,
        ),
    )
    compute = RouteAwareComputeEngine(
        nodes=tuple(
            ComputeNode(node.node_id, capacity=node.capacity)
            for node in scenario.compute_nodes
        ),
        scheduling_runtime=ComputeSchedulingRuntime(
            ComputeSchedulingPolicy(str(resolved_config.compute_scheduling_policy))
        ),
        state_update_targets=("network",),
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
        active_links=network.active_link_states(),
        network_stack_traces=network.stack_traces(),
    )


def _compute_gateway_links(
    scenario: GeneratedFullSystemScenario,
    config: FullSystemScenarioBuilderConfig,
) -> tuple[LinkState, ...]:
    satellite_ids = tuple(item.satellite_id for item in scenario.orbit_elements)
    if not satellite_ids:
        return ()
    return tuple(
        LinkState(
            source_id=satellite_ids[(index * 7) % len(satellite_ids)],
            target_id=node.node_id,
            latency=0.005,
            capacity=config.space_link_capacity,
            availability=True,
        )
        for index, node in enumerate(scenario.compute_nodes)
    )


def _j2_profile_for(orbit_propagation_model: str) -> J2SecularDriftProfile | None:
    if orbit_propagation_model == "J2_SECULAR":
        return J2SecularDriftProfile()
    return None


def _transport_runtime(
    config: FullSystemScenarioBuilderConfig,
    protocol: TransportProtocol,
) -> TransportRuntime:
    base_profile = default_transport_runtime(protocol).profile
    congestion_window = (
        None
        if config.transport_congestion_window_segments == 0
        else config.transport_congestion_window_segments
    )
    return TransportRuntime(
        TransportProfile(
            protocol=base_profile.protocol,
            payload_unit_bytes=base_profile.payload_unit_bytes,
            header_bytes=base_profile.header_bytes,
            efficiency=base_profile.efficiency,
            handshake_round_trips=base_profile.handshake_round_trips,
            loss_rate=config.transport_loss_rate,
            congestion_window_segments=congestion_window,
        )
    )


def _space_ground_budget(
    config: FullSystemScenarioBuilderConfig,
) -> LinkBudgetCalculator:
    antenna = ApertureAntennaSpec(
        antenna_id="generated-ka-aperture",
        diameter_m=config.antenna_diameter_m,
        carrier_frequency_hz=config.carrier_frequency_hz,
        aperture_efficiency=config.antenna_aperture_efficiency,
        steering_mode="electronic",
    ).to_profile()
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
            transmit_power_dbw=config.transmit_power_dbw,
            system_loss_db=config.system_loss_db,
        ),
        receive_terminal=RadioTerminalProfile(
            terminal_id="generated-ground-terminal",
            antenna=antenna,
            transmit_power_dbw=0.0,
            system_loss_db=config.system_loss_db,
            noise_temperature_k=config.noise_temperature_k,
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


def _space_space_budget(
    config: FullSystemScenarioBuilderConfig,
) -> LinkBudgetCalculator:
    antenna = AntennaProfile(
        antenna_id="generated-isl-terminal",
        gain_dbi=34.0,
        beam_width_deg=2.0,
        steering_mode="electronic",
    )
    return LinkBudgetCalculator(
        transmit_terminal=RadioTerminalProfile(
            terminal_id="generated-isl-tx",
            antenna=antenna,
            transmit_power_dbw=config.transmit_power_dbw,
            system_loss_db=config.system_loss_db,
        ),
        receive_terminal=RadioTerminalProfile(
            terminal_id="generated-isl-rx",
            antenna=antenna,
            transmit_power_dbw=0.0,
            system_loss_db=config.system_loss_db,
            noise_temperature_k=config.noise_temperature_k,
        ),
        channel=ChannelProfile(
            channel_id="generated-space-space-ka",
            medium=LinkMedium.SPACE_SPACE,
            carrier_frequency_hz=config.carrier_frequency_hz,
            bandwidth_hz=config.channel_bandwidth_hz,
            loss_model_name="free_space_budget",
        ),
        atmospheric_loss_db=0.0,
        polarization_loss_db=0.2,
        implementation_loss_db=1.0,
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
