"""Deterministic ground-track projection utilities."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from math import asin, atan2, degrees, isfinite, sqrt
from typing import Any

from leo_twin.schema import SatelliteState


@dataclass(frozen=True)
class GroundTrackPoint:
    """Spherical-Earth ground projection for one satellite state."""

    satellite_id: str
    sim_time: float
    latitude_deg: float
    longitude_deg: float
    altitude_km: float
    radius_km: float


def ground_track_point(
    state: SatelliteState,
    reference_radius_km: float = 6371.0,
) -> GroundTrackPoint:
    """Project one Earth-fixed satellite state to latitude, longitude, altitude."""

    if not isinstance(state, SatelliteState):
        raise TypeError("state must be a SatelliteState")
    _require_positive_number(reference_radius_km, "reference_radius_km")
    x_value, y_value, z_value = state.position
    radius_km = sqrt(x_value * x_value + y_value * y_value + z_value * z_value)
    if radius_km <= 0.0:
        raise ValueError("state.position must not be the zero vector")
    return GroundTrackPoint(
        satellite_id=state.satellite_id,
        sim_time=state.sim_time,
        latitude_deg=degrees(asin(z_value / radius_km)),
        longitude_deg=_normalize_longitude_deg(degrees(atan2(y_value, x_value))),
        altitude_km=radius_km - reference_radius_km,
        radius_km=radius_km,
    )


def ground_track_points(
    states: Iterable[SatelliteState],
    reference_radius_km: float = 6371.0,
) -> tuple[GroundTrackPoint, ...]:
    """Project states to ground-track points in deterministic order."""

    points = tuple(
        ground_track_point(state, reference_radius_km=reference_radius_km)
        for state in states
    )
    return tuple(sorted(points, key=lambda point: (point.sim_time, point.satellite_id)))


def _normalize_longitude_deg(value: float) -> float:
    normalized = ((value + 180.0) % 360.0) - 180.0
    if normalized == -180.0:
        return 180.0
    return normalized


def _require_positive_number(value: Any, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field_name} must be an int or float")
    if not isfinite(value) or value <= 0.0:
        raise ValueError(f"{field_name} must be finite and positive")
