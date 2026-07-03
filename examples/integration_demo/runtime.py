"""Full-system integration demo runner."""

from __future__ import annotations

from dataclasses import dataclass

from leo_twin.core import SimulationKernel, SimulationModule
from leo_twin.models.compute import RouteAwareComputeEngine
from leo_twin.models.network import (
    ChannelBudgetSelector,
    LinkBudgetCalculator,
    NetworkStackRuntime,
    NetworkStackTrace,
    PositionDrivenNetworkEngine,
    RadioTerminalProfile,
    RainFadeProfile,
    build_default_leo_protocol_stack,
    default_transport_runtime,
)
from leo_twin.models.orbit import KeplerianOrbitEngine
from leo_twin.schema import (
    AntennaProfile,
    ChannelProfile,
    LinkMedium,
    RoutingProtocol,
    SimEvent,
    TransportProtocol,
)
from leo_twin.services.metrics import MetricsCollector

from examples.integration_demo.config import DemoConfig
from examples.integration_demo.replay import DemoStateProjector, ReplayResult, replay_events
from examples.integration_demo.scenario import DemoScenario, build_demo_scenario
from examples.integration_demo.serialization import JsonValue, events_jsonl


@dataclass(frozen=True)
class DemoRunResult:
    config: DemoConfig
    scenario: DemoScenario
    processed_events: tuple[SimEvent, ...]
    frontend_events: tuple[SimEvent, ...]
    final_snapshot: dict[str, JsonValue]
    state_timeline: tuple[dict[str, JsonValue], ...]
    metrics_summary: dict[str, str | float | int | bool]
    network_stack_traces: tuple[NetworkStackTrace, ...]
    replay: ReplayResult

    def event_log_jsonl(self) -> str:
        return events_jsonl(self.processed_events)


class FrontendEventSink(SimulationModule):
    """Receive frontend-bound events through the kernel for demo logging."""

    def __init__(self, module_name: str = "frontend") -> None:
        self._module_name = module_name
        self._events: list[SimEvent] = []

    def name(self) -> str:
        return self._module_name

    def on_event(self, event: SimEvent, kernel: SimulationKernel) -> None:
        self._events.append(event)

    def events(self) -> tuple[SimEvent, ...]:
        return tuple(self._events)


def run_integration_demo(config: DemoConfig) -> DemoRunResult:
    scenario = build_demo_scenario(config)
    kernel = SimulationKernel()
    frontend_sink = FrontendEventSink()
    metrics = MetricsCollector(
        emit_metric_events=True,
        metric_target=frontend_sink.name(),
        record_limit=100_000,
        event_log_limit=100_000,
        metric_sample_interval=config.metric_sample_interval,
        event_log_sample_interval=1,
        event_log_segment_size=10_000,
        satellite_position_scale_to_km=0.001,
    )
    space_ground_budget = _space_ground_budget(config)
    space_space_budget = _space_space_budget(config)
    transport_protocol = TransportProtocol(str(config.transport_protocol))
    routing_protocol = RoutingProtocol(str(config.routing_protocol))
    network = PositionDrivenNetworkEngine(
        endpoints=scenario.ground_endpoints,
        compute_node_ids=tuple(node.node_id for node in scenario.compute_nodes),
        route_targets=("compute", "metrics"),
        link_capacity=500.0,
        propagation_speed_km_s=299792.458,
        cell_size_km=1000.0,
        link_budget_selector=ChannelBudgetSelector(
            calculators=(space_ground_budget, space_space_budget)
        ),
        position_scale_to_km=0.001,
        space_link_max_range_km=2500.0,
        space_link_capacity=500.0,
        space_link_cell_size_km=2500.0,
        space_link_update_latency_epsilon_s=0.0005,
        space_link_update_capacity_epsilon=1.0,
        transport_runtime=default_transport_runtime(transport_protocol),
        stack_runtime=NetworkStackRuntime(
            build_default_leo_protocol_stack(
                transport_protocol=transport_protocol,
                routing_protocol=routing_protocol,
            ),
            antenna=space_ground_budget.transmit_terminal.antenna,
            channel=space_ground_budget.channel,
        ),
    )

    modules: tuple[SimulationModule, ...] = (
        KeplerianOrbitEngine(
            elements=scenario.orbit_elements,
            update_targets=("network", "metrics"),
            earth_rotation_rate_rad_s=0.000072921159,
            state_vector_scale=1000.0,
        ),
        network,
        RouteAwareComputeEngine(nodes=scenario.compute_nodes),
        metrics,
        frontend_sink,
    )
    for module in modules:
        kernel.register_module(module)

    for event in scenario.initial_events:
        kernel.schedule_event(event)

    processed_events = kernel.run()
    projector = DemoStateProjector(
        scenario.ground_user_render_states,
        config.state_snapshot_interval_events,
    )
    for event in processed_events:
        projector.apply(event)

    replay = replay_events(
        processed_events,
        scenario.ground_user_render_states,
        config.state_snapshot_interval_events,
    )
    return DemoRunResult(
        config=config,
        scenario=scenario,
        processed_events=processed_events,
        frontend_events=frontend_sink.events(),
        final_snapshot=projector.snapshot(),
        state_timeline=projector.timeline(),
        metrics_summary=metrics.summary(),
        network_stack_traces=network.stack_traces(),
        replay=replay,
    )


def _space_ground_budget(config: DemoConfig) -> LinkBudgetCalculator:
    antenna = AntennaProfile(
        antenna_id="integration-demo-ka-terminal",
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
            terminal_id="integration-demo-sat-terminal",
            antenna=antenna,
            transmit_power_dbw=20.0,
            system_loss_db=1.0,
        ),
        receive_terminal=RadioTerminalProfile(
            terminal_id="integration-demo-ground-terminal",
            antenna=antenna,
            transmit_power_dbw=0.0,
            system_loss_db=1.0,
            noise_temperature_k=290.0,
        ),
        channel=ChannelProfile(
            channel_id="integration-demo-space-ground",
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


def _space_space_budget(config: DemoConfig) -> LinkBudgetCalculator:
    antenna = AntennaProfile(
        antenna_id="integration-demo-isl-terminal",
        gain_dbi=42.0,
        beam_width_deg=2.5,
        steering_mode="electronic",
    )
    return LinkBudgetCalculator(
        transmit_terminal=RadioTerminalProfile(
            terminal_id="integration-demo-isl-transmit",
            antenna=antenna,
            transmit_power_dbw=18.0,
            system_loss_db=1.0,
        ),
        receive_terminal=RadioTerminalProfile(
            terminal_id="integration-demo-isl-receive",
            antenna=antenna,
            transmit_power_dbw=0.0,
            system_loss_db=1.0,
            noise_temperature_k=260.0,
        ),
        channel=ChannelProfile(
            channel_id="integration-demo-space-space",
            medium=LinkMedium.SPACE_SPACE,
            carrier_frequency_hz=config.carrier_frequency_hz,
            bandwidth_hz=config.channel_bandwidth_hz,
            loss_model_name="free_space_budget",
        ),
        atmospheric_loss_db=0.0,
        polarization_loss_db=0.2,
        implementation_loss_db=1.0,
    )
