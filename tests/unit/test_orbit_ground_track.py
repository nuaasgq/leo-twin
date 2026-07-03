from __future__ import annotations

import pytest

from leo_twin.models.orbit import GroundTrackPoint, ground_track_point, ground_track_points
from leo_twin.schema import SatelliteState


def _state(
    satellite_id: str,
    position: tuple[float, float, float],
    sim_time: float = 0.0,
) -> SatelliteState:
    return SatelliteState(
        satellite_id=satellite_id,
        sim_time=sim_time,
        position=position,
        velocity=(0.0, 0.0, 0.0),
        status="ACTIVE",
    )


def test_ground_track_point_projects_equatorial_state() -> None:
    point = ground_track_point(_state("sat-a", (7000.0, 0.0, 0.0)))

    assert point == GroundTrackPoint(
        satellite_id="sat-a",
        sim_time=0.0,
        latitude_deg=0.0,
        longitude_deg=0.0,
        altitude_km=629.0,
        radius_km=7000.0,
    )


def test_ground_track_point_normalizes_longitude_and_latitude() -> None:
    east = ground_track_point(_state("east", (0.0, 6371.0, 0.0)))
    west = ground_track_point(_state("west", (0.0, -6371.0, 0.0)))
    north = ground_track_point(_state("north", (0.0, 0.0, 7000.0)))

    assert east.longitude_deg == pytest.approx(90.0)
    assert west.longitude_deg == pytest.approx(-90.0)
    assert north.latitude_deg == pytest.approx(90.0)
    assert north.longitude_deg == pytest.approx(0.0)


def test_ground_track_points_are_sorted_deterministically() -> None:
    points = ground_track_points(
        (
            _state("sat-b", (7000.0, 0.0, 0.0), sim_time=10.0),
            _state("sat-a", (7000.0, 0.0, 0.0), sim_time=10.0),
            _state("sat-c", (7000.0, 0.0, 0.0), sim_time=5.0),
        )
    )

    assert [(point.sim_time, point.satellite_id) for point in points] == [
        (5.0, "sat-c"),
        (10.0, "sat-a"),
        (10.0, "sat-b"),
    ]


def test_ground_track_rejects_invalid_inputs() -> None:
    with pytest.raises(ValueError, match="zero vector"):
        ground_track_point(_state("bad", (0.0, 0.0, 0.0)))

    with pytest.raises(ValueError, match="reference_radius_km"):
        ground_track_point(_state("sat", (7000.0, 0.0, 0.0)), reference_radius_km=0.0)
