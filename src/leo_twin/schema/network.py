"""Network runtime data structures."""

from dataclasses import dataclass
from math import isfinite


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
        _require_finite_non_negative(self.link_latency, "link_latency")
        _require_finite_non_negative(self.link_capacity, "link_capacity")


@dataclass(frozen=True)
class GroundUserProfile:
    """Configuration-driven ground user placement."""

    user_id: str
    cell_id: str

    def __post_init__(self) -> None:
        _require_non_empty_str(self.user_id, "user_id")
        _require_non_empty_str(self.cell_id, "cell_id")


@dataclass(frozen=True)
class LinkState:
    """Flow-level logical link abstraction."""

    source_id: str
    target_id: str
    latency: float
    capacity: float
    availability: bool

    def __post_init__(self) -> None:
        _require_non_empty_str(self.source_id, "source_id")
        _require_non_empty_str(self.target_id, "target_id")
        _require_finite_non_negative(self.latency, "latency")
        _require_finite_non_negative(self.capacity, "capacity")
        if not isinstance(self.availability, bool):
            raise TypeError("availability must be a bool")


@dataclass(frozen=True)
class FlowRequest:
    """Flow-level route request consumed by the network engine."""

    flow_id: str
    source_id: str
    target_id: str
    demand_capacity: float

    def __post_init__(self) -> None:
        _require_non_empty_str(self.flow_id, "flow_id")
        _require_non_empty_str(self.source_id, "source_id")
        _require_non_empty_str(self.target_id, "target_id")
        _require_finite_non_negative(self.demand_capacity, "demand_capacity")


@dataclass(frozen=True)
class Route:
    """Deterministic route output for one flow request."""

    route_id: str
    flow_id: str
    path: tuple[str, ...]
    latency: float
    capacity: float
    available: bool

    def __post_init__(self) -> None:
        _require_non_empty_str(self.route_id, "route_id")
        _require_non_empty_str(self.flow_id, "flow_id")
        _require_finite_non_negative(self.latency, "latency")
        _require_finite_non_negative(self.capacity, "capacity")
        if not isinstance(self.available, bool):
            raise TypeError("available must be a bool")


def _require_non_empty_str(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value:
        raise TypeError(f"{field_name} must be a non-empty str")


def _require_finite_non_negative(value: float, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field_name} must be an int or float")
    if not isfinite(value) or value < 0:
        raise ValueError(f"{field_name} must be finite and non-negative")
