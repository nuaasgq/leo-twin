from __future__ import annotations

from leo_twin.models.network import (
    LinkBudgetCalculator,
    NetworkStackRuntime,
    RadioTerminalProfile,
    build_default_leo_protocol_stack,
)
from leo_twin.schema import (
    AntennaProfile,
    ChannelProfile,
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
        transport_protocol=TransportProtocol.UDP,
        routing_protocol=RoutingProtocol.LINK_STATE,
    )

    assert tuple(layer.layer for layer in stack.layers) == (
        NetworkLayer.APPLICATION,
        NetworkLayer.TRANSPORT,
        NetworkLayer.NETWORK,
        NetworkLayer.DATA_LINK,
        NetworkLayer.PHYSICAL,
        NetworkLayer.CHANNEL,
    )
    assert stack.layers[1].protocol_name == "UDP"
    assert stack.layers[2].protocol_name == "LINK_STATE"


def test_stack_runtime_is_deterministic_for_same_flow_and_route() -> None:
    runtime = NetworkStackRuntime(build_default_leo_protocol_stack())

    first = runtime.process_flow(_flow(), _route())
    second = runtime.process_flow(_flow(), _route())

    assert first == second
    assert first.available is True
    assert first.transport_protocol == "TCP"
    assert first.layers[2].status == "OK"


def test_route_availability_changes_network_layer_status() -> None:
    runtime = NetworkStackRuntime(build_default_leo_protocol_stack())

    trace = runtime.process_flow(_flow(), _route(available=False))

    assert trace.available is False
    assert trace.layers[2].layer == NetworkLayer.NETWORK
    assert trace.layers[2].status == "UNAVAILABLE"


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
    ).evaluate(1000.0)
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
    assert channel_attributes["medium"] == LinkMedium.SPACE_SPACE.value
    assert channel_attributes["range_km"] == "1000.000000"
    assert "snr_db" in channel_attributes
    assert "capacity_mbps" in channel_attributes
