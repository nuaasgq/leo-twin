from __future__ import annotations

import pytest

from leo_twin.models.network import (
    DataLinkProfile,
    default_data_link_runtime,
)
from leo_twin.schema import DataLinkProtocol, FlowRequest, Route


def _request(demand_capacity: float = 10.0) -> FlowRequest:
    return FlowRequest(
        flow_id="flow-001",
        source_id="user-001",
        target_id="compute-001",
        demand_capacity=demand_capacity,
    )


def _route(
    capacity: float = 50.0,
    available: bool = True,
    loss_rate: float | None = None,
) -> Route:
    return Route(
        route_id="route-flow-001",
        flow_id="flow-001",
        path=("user-001", "sat-001", "compute-001"),
        latency=0.5,
        capacity=capacity,
        available=available,
        loss_rate=loss_rate,
    )


def test_tdma_data_link_runtime_applies_frame_overhead_and_slot_delay() -> None:
    runtime = default_data_link_runtime(DataLinkProtocol.TDMA)

    updated = runtime.apply(_request(), _route())

    assert updated.latency == pytest.approx(0.501)
    assert updated.capacity == pytest.approx(
        50.0 * 0.96 * (1.0 - 18.0 / 1518.0)
    )
    assert updated.available is True


def test_contention_mac_profiles_reduce_capacity_and_add_backoff_deterministically() -> None:
    tdma = default_data_link_runtime(DataLinkProtocol.TDMA).apply(_request(), _route())
    aloha = default_data_link_runtime(DataLinkProtocol.SLOTTED_ALOHA).apply(
        _request(),
        _route(),
    )
    csma = default_data_link_runtime(DataLinkProtocol.CSMA_CA).apply(
        _request(),
        _route(),
    )

    assert aloha.latency > csma.latency > tdma.latency
    assert aloha.capacity < csma.capacity < tdma.capacity
    assert aloha.loss_rate == pytest.approx(0.08)
    assert csma.loss_rate == pytest.approx(0.03)
    assert aloha == default_data_link_runtime(DataLinkProtocol.SLOTTED_ALOHA).apply(
        _request(),
        _route(),
    )


def test_data_link_runtime_combines_existing_route_loss_rate() -> None:
    updated = default_data_link_runtime(DataLinkProtocol.SLOTTED_ALOHA).apply(
        _request(),
        _route(loss_rate=0.1),
    )

    assert updated.loss_rate == pytest.approx(1.0 - 0.9 * 0.92)


def test_data_link_runtime_marks_route_unavailable_when_effective_capacity_is_too_low() -> None:
    runtime = default_data_link_runtime(DataLinkProtocol.SLOTTED_ALOHA)

    updated = runtime.apply(_request(demand_capacity=40.0), _route(capacity=50.0))

    assert updated.available is False
    assert updated.capacity < 40.0


def test_data_link_profile_rejects_invalid_contention_parameters() -> None:
    with pytest.raises(ValueError, match="collision_loss_rate"):
        DataLinkProfile(
            protocol=DataLinkProtocol.CSMA_CA,
            frame_payload_bytes=1500,
            frame_header_bytes=26,
            medium_access_efficiency=0.8,
            scheduling_delay_s=0.001,
            collision_loss_rate=1.0,
        )

    with pytest.raises(ValueError, match="contention_backoff_slots"):
        DataLinkProfile(
            protocol=DataLinkProtocol.CSMA_CA,
            frame_payload_bytes=1500,
            frame_header_bytes=26,
            medium_access_efficiency=0.8,
            scheduling_delay_s=0.001,
            contention_backoff_slots=-1,
        )
