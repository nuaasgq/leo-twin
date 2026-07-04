"""Deterministic constellation profile and plane allocation helpers."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from math import ceil, isfinite, sqrt
from typing import Any


class ConstellationProfile(StrEnum):
    """Configuration-level constellation profiles.

    STARLINK_SHELL_1_LIKE is an approximate shell-shape preset for product
    demos. It is not an exact Starlink orbital model or fidelity claim.
    """

    CUSTOM_WALKER = "CUSTOM_WALKER"
    STARLINK_SHELL_1_LIKE = "STARLINK_SHELL_1_LIKE"
    CUSTOM_MULTI_SHELL = "CUSTOM_MULTI_SHELL"


@dataclass(frozen=True)
class ConstellationAllocation:
    """Resolved deterministic plane allocation for one simplified shell."""

    profile: ConstellationProfile
    satellite_count: int
    plane_count: int
    satellites_per_plane: int
    total_slots: int
    plane_count_explicit: bool
    model_note: str

    def __post_init__(self) -> None:
        _require_positive_int(self.satellite_count, "satellite_count")
        _require_positive_int(self.plane_count, "plane_count")
        _require_positive_int(self.satellites_per_plane, "satellites_per_plane")
        _require_positive_int(self.total_slots, "total_slots")
        if self.plane_count > self.satellite_count:
            raise ValueError("plane_count must be <= satellite_count")
        if self.total_slots < self.satellite_count:
            raise ValueError("total_slots must cover satellite_count")

    def plane_index(self, satellite_index: int) -> int:
        _require_satellite_index(satellite_index, self.satellite_count)
        return satellite_index % self.plane_count

    def slot_index(self, satellite_index: int) -> int:
        _require_satellite_index(satellite_index, self.satellite_count)
        return satellite_index // self.plane_count

    def to_summary(self) -> dict[str, int | str | bool]:
        return {
            "profile": self.profile.value,
            "satellite_count": self.satellite_count,
            "plane_count": self.plane_count,
            "satellites_per_plane": self.satellites_per_plane,
            "total_slots": self.total_slots,
            "plane_count_explicit": self.plane_count_explicit,
            "model_note": self.model_note,
        }


class AutoPlaneAllocator:
    """Resolve deterministic plane counts from product-level inputs."""

    STARLINK_SHELL_1_PLANES = 72
    STARLINK_SHELL_1_SATELLITES_PER_PLANE = 22

    @classmethod
    def allocate(
        cls,
        *,
        satellite_count: int,
        plane_count: int | None = None,
        profile: ConstellationProfile | str = ConstellationProfile.CUSTOM_WALKER,
    ) -> ConstellationAllocation:
        _require_positive_int(satellite_count, "satellite_count")
        resolved_profile = _constellation_profile(profile)
        if plane_count is not None:
            _require_positive_int(plane_count, "plane_count")
            resolved_plane_count = min(plane_count, satellite_count)
            explicit = True
        else:
            resolved_plane_count = cls._auto_plane_count(satellite_count, resolved_profile)
            explicit = False
        satellites_per_plane = ceil(satellite_count / resolved_plane_count)
        return ConstellationAllocation(
            profile=resolved_profile,
            satellite_count=satellite_count,
            plane_count=resolved_plane_count,
            satellites_per_plane=satellites_per_plane,
            total_slots=resolved_plane_count * satellites_per_plane,
            plane_count_explicit=explicit,
            model_note=_model_note(resolved_profile),
        )

    @classmethod
    def _auto_plane_count(
        cls,
        satellite_count: int,
        profile: ConstellationProfile,
    ) -> int:
        if profile == ConstellationProfile.STARLINK_SHELL_1_LIKE:
            target = sqrt(
                satellite_count
                * cls.STARLINK_SHELL_1_PLANES
                / cls.STARLINK_SHELL_1_SATELLITES_PER_PLANE
            )
            return _nearest_divisor_at_or_below(satellite_count, target)
        if profile == ConstellationProfile.CUSTOM_MULTI_SHELL:
            return _nearest_divisor(satellite_count, sqrt(satellite_count * 2.0))
        return _nearest_divisor(satellite_count, sqrt(satellite_count))


def _nearest_divisor(value: int, target: float) -> int:
    if not isfinite(target) or target <= 0:
        return 1
    divisors = [candidate for candidate in range(1, value + 1) if value % candidate == 0]
    return min(divisors, key=lambda candidate: (abs(candidate - target), candidate))


def _nearest_divisor_at_or_below(value: int, target: float) -> int:
    if not isfinite(target) or target <= 0:
        return 1
    divisors = [candidate for candidate in range(1, value + 1) if value % candidate == 0]
    floor_divisors = [candidate for candidate in divisors if candidate <= target]
    if floor_divisors:
        return max(floor_divisors)
    return min(divisors)


def _constellation_profile(value: ConstellationProfile | str) -> ConstellationProfile:
    if isinstance(value, ConstellationProfile):
        return value
    return ConstellationProfile(str(value))


def _model_note(profile: ConstellationProfile) -> str:
    if profile == ConstellationProfile.STARLINK_SHELL_1_LIKE:
        return "Approximate Starlink Shell 1-like plane allocation; not exact Starlink fidelity."
    if profile == ConstellationProfile.CUSTOM_MULTI_SHELL:
        return "Deterministic multi-shell placeholder summarized as one simplified allocation."
    return "Custom deterministic Walker-style simplified allocation."


def _require_positive_int(value: Any, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field_name} must be an int")
    if value <= 0:
        raise ValueError(f"{field_name} must be positive")


def _require_satellite_index(value: int, satellite_count: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError("satellite_index must be an int")
    if value < 0 or value >= satellite_count:
        raise ValueError("satellite_index must be within satellite_count")
