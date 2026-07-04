"""Scale-safe fidelity policy for orbit publication granularity."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from math import ceil
from typing import Any


class OrbitUpdateMode(StrEnum):
    """Supported orbit event publication granularities."""

    PER_SATELLITE = "PER_SATELLITE"
    BATCH = "BATCH"


class MetricsMode(StrEnum):
    """Supported metrics observation granularities for scale policy."""

    DETAILED = "DETAILED"
    AGGREGATED = "AGGREGATED"


SAFE_PER_SATELLITE_ORBIT_EVENT_THRESHOLD = 100_000


@dataclass(frozen=True)
class SimulationFidelityPolicy:
    """Small policy object that selects safe event granularity only."""

    satellite_count: int
    orbit_update_mode: OrbitUpdateMode
    metrics_mode: MetricsMode

    @classmethod
    def for_satellite_count(
        cls,
        satellite_count: int,
        *,
        forced_orbit_update_mode: OrbitUpdateMode | str | None = None,
    ) -> "SimulationFidelityPolicy":
        _require_positive_int(satellite_count, "satellite_count")
        if forced_orbit_update_mode is not None:
            orbit_mode = _coerce_orbit_update_mode(forced_orbit_update_mode)
        elif satellite_count < 300:
            orbit_mode = OrbitUpdateMode.PER_SATELLITE
        else:
            orbit_mode = OrbitUpdateMode.BATCH

        metrics_mode = (
            MetricsMode.AGGREGATED
            if satellite_count >= 1000
            else MetricsMode.DETAILED
        )
        return cls(
            satellite_count=satellite_count,
            orbit_update_mode=orbit_mode,
            metrics_mode=metrics_mode,
        )


def resolve_orbit_update_mode(
    satellite_count: int,
    forced_orbit_update_mode: OrbitUpdateMode | str | None = None,
) -> OrbitUpdateMode:
    """Return deterministic orbit update mode for one scenario."""

    return SimulationFidelityPolicy.for_satellite_count(
        satellite_count,
        forced_orbit_update_mode=forced_orbit_update_mode,
    ).orbit_update_mode


def estimate_orbit_event_volume(
    *,
    satellite_count: int,
    update_target_count: int,
    orbit_tick_count: int,
) -> int:
    """Estimate event volume for per-satellite orbit publication."""

    _require_positive_int(satellite_count, "satellite_count")
    _require_positive_int(update_target_count, "update_target_count")
    _require_positive_int(orbit_tick_count, "orbit_tick_count")
    return satellite_count * update_target_count * orbit_tick_count


def orbit_tick_count(duration: float, interval_seconds: int, *, include_final: bool = True) -> int:
    """Return deterministic count of scheduled orbit ticks for a scenario."""

    if duration <= 0.0:
        raise ValueError("duration must be positive")
    _require_positive_int(interval_seconds, "interval_seconds")
    count = ceil(duration / float(interval_seconds))
    if include_final and duration % float(interval_seconds) == 0.0:
        return count + 1
    return count


def _coerce_orbit_update_mode(value: OrbitUpdateMode | str) -> OrbitUpdateMode:
    if isinstance(value, OrbitUpdateMode):
        return value
    return OrbitUpdateMode(str(value))


def _require_positive_int(value: Any, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field_name} must be an int")
    if value <= 0:
        raise ValueError(f"{field_name} must be positive")
