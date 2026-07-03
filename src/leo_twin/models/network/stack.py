"""Deterministic flow-level network protocol stack runtime."""

from __future__ import annotations

from dataclasses import dataclass

from leo_twin.models.network.channel import LinkBudgetResult
from leo_twin.models.network.routing import RoutingCostProfile
from leo_twin.models.network.transport import TransportProfile
from leo_twin.schema import (
    AntennaProfile,
    ChannelProfile,
    DataLinkProtocol,
    FlowRequest,
    NetworkLayer,
    ProtocolLayerContract,
    ProtocolStackContract,
    Route,
    RoutingProtocol,
    TransportProtocol,
)


@dataclass(frozen=True)
class LayerTrace:
    """Deterministic output trace for one network stack layer."""

    layer: NetworkLayer
    protocol_name: str
    input_ref: str
    output_ref: str
    status: str
    attributes: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "attributes", tuple(sorted(self.attributes)))


@dataclass(frozen=True)
class NetworkStackTrace:
    """Flow-level trace produced by a protocol stack run."""

    flow_id: str
    stack_id: str
    route_id: str
    transport_protocol: str
    available: bool
    layers: tuple[LayerTrace, ...]


class NetworkStackRuntime:
    """Run deterministic flow-level processing over a configured protocol stack."""

    def __init__(
        self,
        stack: ProtocolStackContract,
        antenna: AntennaProfile | None = None,
        channel: ChannelProfile | None = None,
        link_budget: LinkBudgetResult | None = None,
        transport_profile: TransportProfile | None = None,
        routing_cost_profile: RoutingCostProfile | None = None,
    ) -> None:
        self._stack = stack
        self._antenna = antenna
        self._channel = channel
        self._link_budget = link_budget
        self._transport_profile = transport_profile
        self._routing_cost_profile = routing_cost_profile

    def process_flow(
        self,
        request: FlowRequest,
        route: Route | None = None,
    ) -> NetworkStackTrace:
        """Return a deterministic layer trace for one flow request."""

        route_id = "route:pending" if route is None else route.route_id
        available = False if route is None else route.available
        current_ref = f"flow:{request.flow_id}"
        traces: list[LayerTrace] = []
        for layer in self._stack.layers:
            trace = self._process_layer(
                layer=layer,
                request=request,
                route=route,
                current_ref=current_ref,
            )
            traces.append(trace)
            current_ref = trace.output_ref
        return NetworkStackTrace(
            flow_id=request.flow_id,
            stack_id=self._stack.stack_id,
            route_id=route_id,
            transport_protocol=_transport_protocol_name(self._stack),
            available=available,
            layers=tuple(traces),
        )

    def _process_layer(
        self,
        layer: ProtocolLayerContract,
        request: FlowRequest,
        route: Route | None,
        current_ref: str,
    ) -> LayerTrace:
        attributes = _base_attributes(layer)
        status = "OK"
        if layer.layer == NetworkLayer.APPLICATION:
            output_ref = f"application:{request.flow_id}"
            attributes += (("demand_capacity", f"{request.demand_capacity:.6f}"),)
        elif layer.layer == NetworkLayer.TRANSPORT:
            output_ref = f"transport:{request.flow_id}:{layer.protocol_name}"
            attributes += (("transport", layer.protocol_name),)
            attributes += _transport_profile_attributes(self._transport_profile)
        elif layer.layer == NetworkLayer.NETWORK:
            route_id = "pending" if route is None else route.route_id
            output_ref = f"route:{route_id}"
            status = _route_status(route)
            attributes += _route_attributes(route)
            attributes += _routing_cost_profile_attributes(self._routing_cost_profile)
        elif layer.layer == NetworkLayer.DATA_LINK:
            output_ref = f"link:{request.flow_id}"
            attributes += (("hop_count", str(_hop_count(route))),)
            attributes += _data_link_profile_attributes(layer.protocol_name)
        elif layer.layer == NetworkLayer.PHYSICAL:
            output_ref = f"physical:{request.flow_id}"
            attributes += _antenna_attributes(self._antenna)
            attributes += _physical_budget_attributes(self._link_budget)
        else:
            output_ref = f"channel:{request.flow_id}"
            attributes += _channel_attributes(self._channel)
            attributes += _channel_budget_attributes(self._link_budget, self._channel)
        return LayerTrace(
            layer=layer.layer,
            protocol_name=layer.protocol_name,
            input_ref=current_ref,
            output_ref=output_ref,
            status=status,
            attributes=attributes,
        )


def build_default_leo_protocol_stack(
    stack_id: str = "leo-default-stack",
    transport_protocol: TransportProtocol = TransportProtocol.TCP,
    routing_protocol: RoutingProtocol = RoutingProtocol.LINK_STATE,
    data_link_protocol: DataLinkProtocol = DataLinkProtocol.TDMA,
) -> ProtocolStackContract:
    """Build the default full-system LEO network stack contract."""

    if not isinstance(data_link_protocol, DataLinkProtocol):
        data_link_protocol = DataLinkProtocol(str(data_link_protocol))
    return ProtocolStackContract(
        stack_id=stack_id,
        layers=(
            ProtocolLayerContract(
                layer=NetworkLayer.APPLICATION,
                protocol_name="TASK_OFFLOAD_FLOW",
                inputs=("TaskRequest",),
                outputs=("FlowRequest",),
            ),
            ProtocolLayerContract(
                layer=NetworkLayer.TRANSPORT,
                protocol_name=transport_protocol.value,
                inputs=("FlowRequest",),
                outputs=("TransportFlow",),
            ),
            ProtocolLayerContract(
                layer=NetworkLayer.NETWORK,
                protocol_name=routing_protocol.value,
                inputs=("TransportFlow",),
                outputs=("Route",),
            ),
            ProtocolLayerContract(
                layer=NetworkLayer.DATA_LINK,
                protocol_name=data_link_protocol.value,
                inputs=("Route",),
                outputs=("LinkState",),
            ),
            ProtocolLayerContract(
                layer=NetworkLayer.PHYSICAL,
                protocol_name="CONFIGURED_TERMINAL_PROFILE",
                inputs=("LinkState",),
                outputs=("PhysicalLinkProfile",),
            ),
            ProtocolLayerContract(
                layer=NetworkLayer.CHANNEL,
                protocol_name="CONFIGURED_CHANNEL_PROFILE",
                inputs=("PhysicalLinkProfile",),
                outputs=("ChannelStateProfile",),
            ),
        ),
    )


def _transport_protocol_name(stack: ProtocolStackContract) -> str:
    for layer in stack.layers:
        if layer.layer == NetworkLayer.TRANSPORT:
            return layer.protocol_name
    return "UNKNOWN"


def _base_attributes(layer: ProtocolLayerContract) -> tuple[tuple[str, str], ...]:
    return layer.parameters + (
        ("input_schema", ",".join(layer.inputs)),
        ("output_schema", ",".join(layer.outputs)),
    )


def _route_status(route: Route | None) -> str:
    if route is None:
        return "PENDING"
    return "OK" if route.available else "UNAVAILABLE"


def _route_attributes(route: Route | None) -> tuple[tuple[str, str], ...]:
    if route is None:
        return (("route_id", "pending"),)
    return (
        ("available", str(route.available)),
        ("capacity", f"{route.capacity:.6f}"),
        ("latency", f"{route.latency:.6f}"),
        ("route_id", route.route_id),
    )


def _routing_cost_profile_attributes(
    profile: RoutingCostProfile | None,
) -> tuple[tuple[str, str], ...]:
    if profile is None:
        return ()
    return (
        ("hop_weight", f"{profile.hop_weight:.6f}"),
        ("inverse_capacity_weight", f"{profile.inverse_capacity_weight:.6f}"),
        ("latency_weight", f"{profile.latency_weight:.6f}"),
    )


def _transport_profile_attributes(
    profile: TransportProfile | None,
) -> tuple[tuple[str, str], ...]:
    if profile is None:
        return ()
    congestion_window = (
        "none"
        if profile.congestion_window_segments is None
        else str(profile.congestion_window_segments)
    )
    total_bytes = profile.payload_unit_bytes + profile.header_bytes
    overhead_ratio = profile.header_bytes / total_bytes
    return (
        ("congestion_window_segments", congestion_window),
        ("efficiency", f"{profile.efficiency:.6f}"),
        ("handshake_round_trips", str(profile.handshake_round_trips)),
        ("header_bytes", str(profile.header_bytes)),
        ("loss_rate", f"{profile.loss_rate:.6f}"),
        ("overhead_ratio", f"{overhead_ratio:.6f}"),
        ("payload_unit_bytes", str(profile.payload_unit_bytes)),
    )


def _hop_count(route: Route | None) -> int:
    if route is None:
        return 0
    return max(0, len(route.path) - 1)


def _data_link_profile_attributes(protocol_name: str) -> tuple[tuple[str, str], ...]:
    if protocol_name == DataLinkProtocol.SLOTTED_ALOHA.value:
        return (
            ("frame_model", "fixed_slot"),
            ("mac_profile", DataLinkProtocol.SLOTTED_ALOHA.value),
            ("medium_access", "contention_slot"),
            ("retransmission_policy", "deterministic_backoff_trace"),
        )
    if protocol_name == DataLinkProtocol.CSMA_CA.value:
        return (
            ("frame_model", "carrier_sense_frame"),
            ("mac_profile", DataLinkProtocol.CSMA_CA.value),
            ("medium_access", "listen_before_transmit"),
            ("retransmission_policy", "deterministic_backoff_trace"),
        )
    return (
        ("frame_model", "scheduled_slot"),
        ("mac_profile", DataLinkProtocol.TDMA.value),
        ("medium_access", "time_division"),
        ("retransmission_policy", "none"),
    )


def _antenna_attributes(antenna: AntennaProfile | None) -> tuple[tuple[str, str], ...]:
    if antenna is None:
        return (("antenna_id", "none"),)
    return (
        ("antenna_id", antenna.antenna_id),
        ("beam_width_deg", f"{antenna.beam_width_deg:.6f}"),
        ("gain_dbi", f"{antenna.gain_dbi:.6f}"),
        ("steering_mode", antenna.steering_mode),
    )


def _physical_budget_attributes(
    link_budget: LinkBudgetResult | None,
) -> tuple[tuple[str, str], ...]:
    if link_budget is None:
        return ()
    return (
        ("path_loss_db", f"{link_budget.path_loss_db:.6f}"),
        ("receive_pointing_loss_db", f"{link_budget.receive_pointing_loss_db:.6f}"),
        ("received_power_dbw", f"{link_budget.received_power_dbw:.6f}"),
        ("transmit_pointing_loss_db", f"{link_budget.transmit_pointing_loss_db:.6f}"),
    )


def _channel_attributes(channel: ChannelProfile | None) -> tuple[tuple[str, str], ...]:
    if channel is None:
        return (("channel_id", "none"),)
    return (
        ("bandwidth_hz", f"{channel.bandwidth_hz:.6f}"),
        ("carrier_frequency_hz", f"{channel.carrier_frequency_hz:.6f}"),
        ("channel_id", channel.channel_id),
        ("loss_model_name", channel.loss_model_name),
        ("medium", channel.medium.value),
    )


def _channel_budget_attributes(
    link_budget: LinkBudgetResult | None,
    channel: ChannelProfile | None,
) -> tuple[tuple[str, str], ...]:
    if link_budget is None:
        return ()
    attributes = (
        ("capacity_mbps", f"{link_budget.capacity_mbps:.6f}"),
        ("noise_power_dbw", f"{link_budget.noise_power_dbw:.6f}"),
        ("propagation_delay_s", f"{link_budget.propagation_delay_s:.9f}"),
        ("rain_fade_loss_db", f"{link_budget.rain_fade_loss_db:.6f}"),
        ("range_km", f"{link_budget.range_km:.6f}"),
        ("snr_db", f"{link_budget.snr_db:.6f}"),
    )
    if channel is None:
        return attributes
    spectral_efficiency_bps_hz = (
        link_budget.capacity_mbps * 1_000_000.0 / channel.bandwidth_hz
    )
    return attributes + (
        ("spectral_efficiency_bps_hz", f"{spectral_efficiency_bps_hz:.6f}"),
    )
