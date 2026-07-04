"""Network runtime data structures."""

from dataclasses import dataclass

from leo_twin.schema.domain import (
    FlowRequest,
    LinkState,
    Route,
    RouteState,
    _require_non_empty_str,
    _require_non_negative_number,
)


@dataclass(frozen=True)
class CoverageSlot:
    """Coverage cells available to one satellite during a time slot."""

    slot: int
    cell_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if isinstance(self.slot, bool) or not isinstance(self.slot, int):
            raise TypeError("slot must be an int")
        normalized = tuple(sorted(str(cell_id) for cell_id in self.cell_ids))
        object.__setattr__(self, "cell_ids", normalized)


@dataclass(frozen=True)
class SatelliteProfile:
    """Configuration-driven satellite access profile."""

    satellite_id: str
    coverage: tuple[CoverageSlot, ...]
    link_latency: float
    link_capacity: float

    def __post_init__(self) -> None:
        _require_non_empty_str(self.satellite_id, "satellite_id")
        _require_non_negative_number(self.link_latency, "link_latency")
        _require_non_negative_number(self.link_capacity, "link_capacity")


@dataclass(frozen=True)
class GroundUserProfile:
    """Configuration-driven ground user placement."""

    user_id: str
    cell_id: str

    def __post_init__(self) -> None:
        _require_non_empty_str(self.user_id, "user_id")
        _require_non_empty_str(self.cell_id, "cell_id")

__all__ = [
    "CoverageSlot",
    "FlowRequest",
    "GroundUserProfile",
    "LinkState",
    "Route",
    "RouteState",
    "SatelliteProfile",
]
