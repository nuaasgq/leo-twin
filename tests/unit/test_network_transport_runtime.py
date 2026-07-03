from __future__ import annotations

import pytest

from leo_twin.models.network import (
    TransportProfile,
    TransportRuntime,
    default_transport_runtime,
)
from leo_twin.schema import FlowRequest, Route, TransportProtocol


def _request(demand: float = 1.0) -> FlowRequest:
    return FlowRequest("flow-001", "user-a", "node-a", demand)


def _route() -> Route:
    return Route(
        route_id="route:flow-001",
        flow_id="flow-001",
        path=("user-a", "sat-a", "node-a"),
        latency=2.0,
        capacity=100.0,
        available=True,
    )


def test_tcp_transport_runtime_applies_handshake_and_overhead() -> None:
    runtime = default_transport_runtime(TransportProtocol.TCP)

    route = runtime.apply(_request(), _route())

    assert route.latency == 4.0
    assert route.capacity == pytest.approx(89.546667)
    assert route.available is True


def test_udp_transport_runtime_has_lower_latency_and_higher_capacity_than_tcp() -> None:
    tcp = default_transport_runtime(TransportProtocol.TCP).apply(_request(), _route())
    udp = default_transport_runtime(TransportProtocol.UDP).apply(_request(), _route())

    assert udp.latency < tcp.latency
    assert udp.capacity > tcp.capacity


def test_transport_runtime_marks_route_unavailable_when_effective_capacity_is_too_low() -> None:
    runtime = default_transport_runtime(TransportProtocol.TCP)

    route = runtime.apply(_request(demand=95.0), _route())

    assert route.available is False
    assert route.capacity == pytest.approx(89.546667)


def test_transport_profile_loss_rate_reduces_effective_capacity() -> None:
    runtime = TransportRuntime(
        TransportProfile(
            protocol=TransportProtocol.UDP,
            payload_unit_bytes=1000,
            header_bytes=0,
            efficiency=1.0,
            loss_rate=0.25,
        )
    )

    route = runtime.apply(_request(demand=70.0), _route())

    assert route.capacity == pytest.approx(75.0)
    assert route.available is True


def test_transport_profile_congestion_window_limits_capacity() -> None:
    runtime = TransportRuntime(
        TransportProfile(
            protocol=TransportProtocol.TCP,
            payload_unit_bytes=1000,
            header_bytes=0,
            efficiency=1.0,
            congestion_window_segments=10,
        )
    )
    route = Route(
        route_id="route:flow-001",
        flow_id="flow-001",
        path=("user-a", "sat-a", "node-a"),
        latency=0.1,
        capacity=1000.0,
        available=True,
    )

    applied = runtime.apply(_request(demand=1.0), route)
    decision = runtime.decision(route)

    assert decision.window_capacity_mbps == pytest.approx(0.8)
    assert applied.capacity == pytest.approx(0.8)
    assert applied.available is False


def test_transport_profile_rejects_invalid_efficiency() -> None:
    with pytest.raises(ValueError, match="efficiency"):
        TransportProfile(
            protocol=TransportProtocol.UDP,
            payload_unit_bytes=1472,
            header_bytes=28,
            efficiency=0.0,
        )


def test_transport_profile_rejects_invalid_loss_rate() -> None:
    with pytest.raises(ValueError, match="loss_rate"):
        TransportProfile(
            protocol=TransportProtocol.UDP,
            payload_unit_bytes=1472,
            header_bytes=28,
            efficiency=1.0,
            loss_rate=1.0,
        )
