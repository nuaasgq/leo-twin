"""Local configuration contracts for the simplified orbit module."""

from dataclasses import dataclass
from math import isfinite
from typing import Any


@dataclass(frozen=True)
class OrbitSatelliteConfig:
    """Configuration for deterministic circular satellite motion."""

    satellite_id: str
    orbital_radius: float
    angular_velocity: float
    phase: float = 0.0
    inclination: float = 0.0
    status: str = "ACTIVE"

    def __post_init__(self) -> None:
        _require_non_empty_str(self.satellite_id, "satellite_id")
        _require_positive_number(self.orbital_radius, "orbital_radius")
        _require_finite_number(self.angular_velocity, "angular_velocity")
        _require_finite_number(self.phase, "phase")
        _require_finite_number(self.inclination, "inclination")
        _require_non_empty_str(self.status, "status")


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
