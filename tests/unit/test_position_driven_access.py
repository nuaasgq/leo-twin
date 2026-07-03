from __future__ import annotations

import pytest

from leo_twin.models.network import (
    GroundEndpoint,
    GroundEndpointIndex,
    PositionDrivenAccessModel,
)
from leo_twin.schema import SatelliteState


EARTH_RADIUS_KM = 6371.0


def _state(satellite_id: str, position: tuple[float, float, float]) -> SatelliteState:
    return SatelliteState(
        satellite_id=satellite_id,
        sim_time=0.0,
        position=position,
        velocity=(0.0, 0.0, 0.0),
        status="ACTIVE",
    )


def test_access_is_available_for_satellite_above_endpoint() -> None:
    model = PositionDrivenAccessModel(
        endpoints=(
            GroundEndpoint(
                endpoint_id="user-east",
                position=(EARTH_RADIUS_KM, 0.0, 0.0),
                min_elevation_deg=10.0,
                max_range_km=2000.0,
            ),
        ),
        cell_size_km=1000.0,
    )

    access = model.compute_access((_state("sat-001", (7000.0, 0.0, 0.0)),))

    assert len(access) == 1
    assert access[0].satellite_id == "sat-001"
    assert access[0].endpoint_id == "user-east"
    assert access[0].range_km == pytest.approx(629.0)
    assert access[0].elevation_deg == pytest.approx(90.0)


def test_access_is_rejected_below_endpoint_horizon() -> None:
    model = PositionDrivenAccessModel(
        endpoints=(
            GroundEndpoint(
                endpoint_id="user-east",
                position=(EARTH_RADIUS_KM, 0.0, 0.0),
                min_elevation_deg=0.0,
                max_range_km=10000.0,
            ),
        ),
        cell_size_km=1000.0,
    )

    access = model.compute_access((_state("sat-001", (0.0, 7000.0, 0.0)),))

    assert access == ()


def test_position_driven_access_is_deterministic_and_sorted() -> None:
    model = PositionDrivenAccessModel(
        endpoints=(
            GroundEndpoint(
                endpoint_id="user-b",
                position=(EARTH_RADIUS_KM, 0.0, 0.0),
                min_elevation_deg=5.0,
                max_range_km=2000.0,
            ),
            GroundEndpoint(
                endpoint_id="user-a",
                position=(EARTH_RADIUS_KM, 0.0, 0.0),
                min_elevation_deg=5.0,
                max_range_km=2000.0,
            ),
        ),
        cell_size_km=1000.0,
    )

    first = model.compute_access(
        (
            _state("sat-b", (7000.0, 0.0, 0.0)),
            _state("sat-a", (7000.0, 0.0, 0.0)),
        )
    )
    second = model.compute_access(
        (
            _state("sat-b", (7000.0, 0.0, 0.0)),
            _state("sat-a", (7000.0, 0.0, 0.0)),
        )
    )

    assert first == second
    assert [(item.satellite_id, item.endpoint_id) for item in first] == [
        ("sat-a", "user-a"),
        ("sat-a", "user-b"),
        ("sat-b", "user-a"),
        ("sat-b", "user-b"),
    ]


def test_ground_endpoint_index_limits_candidates_by_spatial_cell() -> None:
    index = GroundEndpointIndex(
        endpoints=(
            GroundEndpoint(
                endpoint_id="near",
                position=(7000.0, 0.0, 0.0),
                min_elevation_deg=0.0,
                max_range_km=1000.0,
            ),
            GroundEndpoint(
                endpoint_id="far",
                position=(-7000.0, 0.0, 0.0),
                min_elevation_deg=0.0,
                max_range_km=1000.0,
            ),
        ),
        cell_size_km=500.0,
    )

    candidates = index.candidates_near((7000.0, 0.0, 0.0), radius_km=500.0)

    assert [candidate.endpoint_id for candidate in candidates] == ["near"]
