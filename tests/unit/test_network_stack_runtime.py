from __future__ import annotations

from leo_twin.models.network import (
    LinkBudgetCalculator,
    NetworkStackRuntime,
    RainFadeProfile,
    RadioTerminalProfile,
    RoutingRuntime,
    build_default_leo_protocol_stack,
    default_data_link_runtime,
    default_transport_runtime,
)
from leo_twin.schema import (
    AntennaProfile,
    ApplicationProtocol,
    ChannelProfile,
    DataLinkProtocol,
    FlowRequest,
    LinkMedium,
    NetworkLayer,
    Route,
    RoutingProtocol,
    TransportProtocol,
)


def _flow() -> FlowRequest:
    return FlowRequest(
        flow_id="flow-001",
        source_id="user-001",
        target_id="compute-001",
        demand_capacity=20.0,
    )


def _route(available: bool = True) -> Route:
    return Route(
        route_id="route-flow-001",
        flow_id="flow-001",
        path=("user-001", "sat-001", "sat-002", "compute-001"),
        latency=42.5,
        capacity=25.0,
        available=available,
    )


def test_default_stack_contains_required_layers_and_protocols() -> None:
    stack = build_default_leo_protocol_stack(
        application_protocol=ApplicationProtocol.HTTP,
        transport_protocol=TransportProtocol.UDP,
        routing_protocol=RoutingProtocol.LINK_STATE,
        data_link_protocol=DataLinkProtocol.CSMA_CA,
    )

    assert tuple(layer.layer for layer in stack.layers) == (
        NetworkLayer.APPLICATION,
        NetworkLayer.TRANSPORT,
        NetworkLayer.NETWORK,
        NetworkLayer.DATA_LINK,
        NetworkLayer.PHYSICAL,
        NetworkLayer.CHANNEL,
    )
    assert stack.layers[0].protocol_name == "HTTP"
    assert stack.layers[0].inputs == ("HttpRequest",)
    assert stack.layers[1].protocol_name == "UDP"
    assert stack.layers[2].protocol_name == "LINK_STATE"
    assert stack.layers[3].protocol_name == "CSMA_CA"


def test_stack_runtime_records_application_profile_attributes() -> None:
    runtime = NetworkStackRuntime(
        build_default_leo_protocol_stack(application_protocol=ApplicationProtocol.MQTT)
    )

    trace = runtime.process_flow(_flow(), _route())
    attributes = dict(trace.layers[0].attributes)

    assert trace.application_protocol == "MQTT"
    assert attributes["application"] == "MQTT"
    assert attributes["application_profile"] == "publish_subscribe"
    assert attributes["interaction_model"] == "brokered_message"
    assert attributes["session_model"] == "persistent_topic"


def test_stack_runtime_records_data_link_mac_profile_attributes() -> None:
    data_link = default_data_link_runtime(DataLinkProtocol.SLOTTED_ALOHA)
    runtime = NetworkStackRuntime(
        build_default_leo_protocol_stack(data_link_protocol=DataLinkProtocol.SLOTTED_ALOHA),
        data_link_profile=data_link.profile,
    )

    trace = runtime.process_flow(_flow(), _route())
    attributes = dict(trace.layers[3].attributes)

    assert attributes["hop_count"] == "3"
    assert attributes["mac_profile"] == "SLOTTED_ALOHA"
    assert attributes["frame_model"] == "fixed_slot"
    assert attributes["medium_access"] == "contention_slot"
    assert attributes["retransmission_policy"] == "deterministic_backoff_trace"
    assert attributes["medium_access_efficiency"] == "0.620000"
    assert attributes["collision_loss_rate"] == "0.080000"
    assert attributes["contention_backoff_slots"] == "2"
    assert attributes["contention_delay_s"] == "0.004000"


def test_stack_runtime_is_deterministic_for_same_flow_and_route() -> None:
    runtime = NetworkStackRuntime(build_default_leo_protocol_stack())

    first = runtime.process_flow(_flow(), _route())
    second = runtime.process_flow(_flow(), _route())

    assert first == second
    assert first.available is True
    assert first.application_protocol == "TASK_OFFLOAD_FLOW"
    assert first.transport_protocol == "TCP"
    assert first.layers[2].status == "OK"


def test_route_availability_changes_network_layer_status() -> None:
    runtime = NetworkStackRuntime(build_default_leo_protocol_stack())

    trace = runtime.process_flow(_flow(), _route(available=False))

    assert trace.available is False
    assert trace.layers[2].layer == NetworkLayer.NETWORK
    assert trace.layers[2].status == "UNAVAILABLE"


def test_stack_runtime_records_transport_profile_attributes() -> None:
    transport = default_transport_runtime(TransportProtocol.TCP)
    runtime = NetworkStackRuntime(
        build_default_leo_protocol_stack(),
        transport_profile=transport.profile,
    )

    trace = runtime.process_flow(_flow(), _route())
    attributes = dict(trace.layers[1].attributes)

    assert attributes["transport"] == "TCP"
    assert attributes["payload_unit_bytes"] == "1460"
    assert attributes["header_bytes"] == "40"
    assert attributes["efficiency"] == "0.920000"
    assert attributes["handshake_round_trips"] == "1"
    assert attributes["loss_rate"] == "0.000000"
    assert attributes["congestion_window_segments"] == "none"
    assert attributes["overhead_ratio"] == "0.026667"


def test_stack_runtime_records_routing_cost_profile_attributes() -> None:
    routing = RoutingRuntime(RoutingProtocol.DISTANCE_VECTOR)
    runtime = NetworkStackRuntime(
        build_default_leo_protocol_stack(routing_protocol=RoutingProtocol.DISTANCE_VECTOR),
        routing_cost_profile=routing.cost_profile,
    )

    trace = runtime.process_flow(_flow(), _route())
    attributes = dict(trace.layers[2].attributes)

    assert attributes["latency_weight"] == "0.000000"
    assert attributes["inverse_capacity_weight"] == "0.000000"
    assert attributes["hop_weight"] == "1.000000"


def test_stack_runtime_records_link_physical_and_channel_profiles() -> None:
    antenna = AntennaProfile(
        antenna_id="ANT-001",
        gain_dbi=31.0,
        beam_width_deg=2.5,
        steering_mode="electronic",
    )
    channel = ChannelProfile(
        channel_id="CH-001",
        medium=LinkMedium.SPACE_SPACE,
        carrier_frequency_hz=23_000_000_000.0,
        bandwidth_hz=800_000_000.0,
        loss_model_name="configured_loss_profile",
    )
    budget = LinkBudgetCalculator(
        transmit_terminal=RadioTerminalProfile(
            terminal_id="sat-a",
            antenna=antenna,
            transmit_power_dbw=18.0,
        ),
        receive_terminal=RadioTerminalProfile(
            terminal_id="sat-b",
            antenna=antenna,
            transmit_power_dbw=0.0,
        ),
        channel=channel,
        rain_fade_profile=RainFadeProfile(
            rain_rate_mm_h=10.0,
            attenuation_coefficient_db_per_km_per_mm_h=0.02,
            effective_path_km=6.0,
        ),
    ).evaluate(
        1000.0,
        transmit_off_boresight_deg=0.5,
        receive_off_boresight_deg=0.5,
    )
    runtime = NetworkStackRuntime(
        build_default_leo_protocol_stack(),
        antenna=antenna,
        channel=channel,
        link_budget=budget,
    )

    trace = runtime.process_flow(_flow(), _route())
    data_link_attributes = dict(trace.layers[3].attributes)
    physical_attributes = dict(trace.layers[4].attributes)
    channel_attributes = dict(trace.layers[5].attributes)

    assert data_link_attributes["hop_count"] == "3"
    assert physical_attributes["antenna_id"] == "ANT-001"
    assert "path_loss_db" in physical_attributes
    assert "received_power_dbw" in physical_attributes
    assert physical_attributes["transmit_pointing_loss_db"] == "0.480000"
    assert physical_attributes["receive_pointing_loss_db"] == "0.480000"
    assert channel_attributes["medium"] == LinkMedium.SPACE_SPACE.value
    assert channel_attributes["range_km"] == "1000.000000"
    assert channel_attributes["rain_fade_loss_db"] == "1.200000"
    assert channel_attributes["spectral_efficiency_bps_hz"] == (
        f"{budget.capacity_mbps * 1_000_000.0 / channel.bandwidth_hz:.6f}"
    )
    assert "snr_db" in channel_attributes
    assert "capacity_mbps" in channel_attributes
