"""Position-driven access evaluation for satellite-ground links."""

from __future__ import annotations

from dataclasses import dataclass
from math import asin, degrees, floor, isfinite, sqrt
from typing import Any

from leo_twin.schema import SatelliteState


Vector3 = tuple[float, float, float]
CellId = tuple[int, int, int]


@dataclass(frozen=True)
class GroundEndpoint:
    """Ground-side endpoint used by position-driven access evaluation."""

    endpoint_id: str
    position: Vector3
    min_elevation_deg: float
    max_range_km: float

    def __post_init__(self) -> None:
        _require_non_empty_str(self.endpoint_id, "endpoint_id")
        _require_vector3(self.position, "position")
        _require_finite_number(self.min_elevation_deg, "min_elevation_deg")
        _require_positive_number(self.max_range_km, "max_range_km")


@dataclass(frozen=True)
class AccessLinkCandidate:
    """Deterministic satellite-ground access candidate."""

    satellite_id: str
    endpoint_id: str
    range_km: float
    elevation_deg: float
    available: bool

    def __post_init__(self) -> None:
        _require_non_empty_str(self.satellite_id, "satellite_id")
        _require_non_empty_str(self.endpoint_id, "endpoint_id")
        _require_finite_number(self.range_km, "range_km")
        _require_finite_number(self.elevation_deg, "elevation_deg")
        if not isinstance(self.available, bool):
            raise TypeError("available must be a bool")


class GroundEndpointIndex:
    """Deterministic spatial index for ground endpoints."""

    def __init__(self, endpoints: tuple[GroundEndpoint, ...], cell_size_km: float) -> None:
        _require_positive_number(cell_size_km, "cell_size_km")
        self._cell_size_km = float(cell_size_km)
        self._endpoints = tuple(sorted(endpoints, key=lambda item: item.endpoint_id))
        self._cells = self._build_cells(self._endpoints)

    def candidates_near(self, position: Vector3, radius_km: float) -> tuple[GroundEndpoint, ...]:
        """Return endpoints in cells near the given position."""

        _require_vector3(position, "position")
        _require_positive_number(radius_km, "radius_km")
        center = self._cell_for(position)
        span = int(radius_km // self._cell_size_km) + 1
        candidates: list[GroundEndpoint] = []
        for x_index in range(center[0] - span, center[0] + span + 1):
            for y_index in range(center[1] - span, center[1] + span + 1):
                for z_index in range(center[2] - span, center[2] + span + 1):
                    cell = (x_index, y_index, z_index)
                    candidates.extend(self._cells.get(cell, ()))
        return tuple(sorted(candidates, key=lambda item: item.endpoint_id))

    def _build_cells(
        self,
        endpoints: tuple[GroundEndpoint, ...],
    ) -> dict[CellId, tuple[GroundEndpoint, ...]]:
        working: dict[CellId, list[GroundEndpoint]] = {}
        for endpoint in endpoints:
            working.setdefault(self._cell_for(endpoint.position), []).append(endpoint)
        return {
            cell: tuple(sorted(values, key=lambda item: item.endpoint_id))
            for cell, values in sorted(working.items())
        }

    def _cell_for(self, position: Vector3) -> CellId:
        return (
            floor(position[0] / self._cell_size_km),
            floor(position[1] / self._cell_size_km),
            floor(position[2] / self._cell_size_km),
        )


class PositionDrivenAccessModel:
    """Evaluate access candidates from satellite state vectors."""

    def __init__(
        self,
        endpoints: tuple[GroundEndpoint, ...],
        cell_size_km: float = 1000.0,
    ) -> None:
        if not endpoints:
            raise ValueError("endpoints must not be empty")
        self._index = GroundEndpointIndex(endpoints, cell_size_km=cell_size_km)
        self._max_range_km = max(endpoint.max_range_km for endpoint in endpoints)

    def compute_access(
        self,
        states: tuple[SatelliteState, ...],
    ) -> tuple[AccessLinkCandidate, ...]:
        """Return all available access candidates for the given states."""

        candidates: list[AccessLinkCandidate] = []
        for state in sorted(states, key=lambda item: item.satellite_id):
            candidates.extend(self._access_for_state(state))
        return tuple(
            sorted(
                candidates,
                key=lambda item: (item.satellite_id, item.endpoint_id),
            )
        )

    def _access_for_state(self, state: SatelliteState) -> tuple[AccessLinkCandidate, ...]:
        evaluated: list[AccessLinkCandidate] = []
        nearby = self._index.candidates_near(state.position, self._max_range_km)
        for endpoint in nearby:
            candidate = _evaluate_access(state, endpoint)
            if candidate.available:
                evaluated.append(candidate)
        return tuple(evaluated)


def _evaluate_access(
    state: SatelliteState,
    endpoint: GroundEndpoint,
) -> AccessLinkCandidate:
    relative = _subtract(state.position, endpoint.position)
    range_km = _norm(relative)
    elevation_deg = _elevation_deg(relative, endpoint.position)
    available = range_km <= endpoint.max_range_km and elevation_deg >= endpoint.min_elevation_deg
    return AccessLinkCandidate(
        satellite_id=state.satellite_id,
        endpoint_id=endpoint.endpoint_id,
        range_km=range_km,
        elevation_deg=elevation_deg,
        available=available,
    )


def _elevation_deg(relative: Vector3, ground_position: Vector3) -> float:
    relative_norm = _norm(relative)
    ground_norm = _norm(ground_position)
    if relative_norm == 0.0 or ground_norm == 0.0:
        return -90.0
    projection = _dot(relative, ground_position) / (relative_norm * ground_norm)
    bounded = max(-1.0, min(1.0, projection))
    return degrees(asin(bounded))


def _subtract(left: Vector3, right: Vector3) -> Vector3:
    return (left[0] - right[0], left[1] - right[1], left[2] - right[2])


def _dot(left: Vector3, right: Vector3) -> float:
    return left[0] * right[0] + left[1] * right[1] + left[2] * right[2]


def _norm(vector: Vector3) -> float:
    return sqrt(_dot(vector, vector))


def _require_non_empty_str(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value:
        raise TypeError(f"{field_name} must be a non-empty str")


def _require_finite_number(value: Any, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field_name} must be an int or float")
    if not isfinite(value):
        raise ValueError(f"{field_name} must be finite")


def _require_positive_number(value: Any, field_name: str) -> None:
    _require_finite_number(value, field_name)
    if value <= 0:
        raise ValueError(f"{field_name} must be positive")


def _require_vector3(value: Any, field_name: str) -> None:
    if not isinstance(value, tuple) or len(value) != 3:
        raise TypeError(f"{field_name} must be a 3-tuple")
    for item in value:
        _require_finite_number(item, field_name)
