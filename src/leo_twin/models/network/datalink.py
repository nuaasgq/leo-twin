"""Deterministic flow-level data-link MAC runtime."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any

from leo_twin.schema import DataLinkProtocol, FlowRequest, Route


@dataclass(frozen=True)
class DataLinkProfile:
    """Configuration for one flow-level data-link MAC profile."""

    protocol: DataLinkProtocol
    frame_payload_bytes: int
    frame_header_bytes: int
    medium_access_efficiency: float
    scheduling_delay_s: float
    collision_loss_rate: float = 0.0
    contention_backoff_slots: int = 0
    slot_duration_s: float = 0.0

    def __post_init__(self) -> None:
        if not isinstance(self.protocol, DataLinkProtocol):
            object.__setattr__(self, "protocol", DataLinkProtocol(str(self.protocol)))
        _require_positive_int(self.frame_payload_bytes, "frame_payload_bytes")
        _require_non_negative_int(self.frame_header_bytes, "frame_header_bytes")
        _require_unit_interval(
            self.medium_access_efficiency,
            "medium_access_efficiency",
        )
        _require_non_negative_number(self.scheduling_delay_s, "scheduling_delay_s")
        _require_probability(self.collision_loss_rate, "collision_loss_rate")
        _require_non_negative_int(
            self.contention_backoff_slots,
            "contention_backoff_slots",
        )
        _require_non_negative_number(self.slot_duration_s, "slot_duration_s")


@dataclass(frozen=True)
class DataLinkDecision:
    """Deterministic data-link layer decision for one route."""

    protocol: DataLinkProtocol
    route_id: str
    effective_latency: float
    effective_capacity: float
    frame_overhead_ratio: float
    collision_loss_rate: float
    contention_delay_s: float


class DataLinkRuntime:
    """Apply a MAC profile to route latency and capacity at flow granularity."""

    def __init__(self, profile: DataLinkProfile) -> None:
        self._profile = profile

    @property
    def profile(self) -> DataLinkProfile:
        return self._profile

    def decision(self, route: Route) -> DataLinkDecision:
        """Return the deterministic data-link decision for a route."""

        overhead_ratio = self._frame_overhead_ratio()
        contention_delay = (
            self._profile.contention_backoff_slots * self._profile.slot_duration_s
        )
        if not route.available:
            return DataLinkDecision(
                protocol=self._profile.protocol,
                route_id=route.route_id,
                effective_latency=route.latency,
                effective_capacity=0.0,
                frame_overhead_ratio=overhead_ratio,
                collision_loss_rate=self._profile.collision_loss_rate,
                contention_delay_s=contention_delay,
            )
        effective_latency = (
            route.latency + self._profile.scheduling_delay_s + contention_delay
        )
        effective_capacity = (
            route.capacity
            * self._profile.medium_access_efficiency
            * (1.0 - overhead_ratio)
            * (1.0 - self._profile.collision_loss_rate)
        )
        return DataLinkDecision(
            protocol=self._profile.protocol,
            route_id=route.route_id,
            effective_latency=effective_latency,
            effective_capacity=effective_capacity,
            frame_overhead_ratio=overhead_ratio,
            collision_loss_rate=self._profile.collision_loss_rate,
            contention_delay_s=contention_delay,
        )

    def apply(self, request: FlowRequest, route: Route) -> Route:
        """Return a route whose latency/capacity reflect MAC behavior."""

        decision = self.decision(route)
        return Route(
            route_id=route.route_id,
            flow_id=request.flow_id,
            path=route.path,
            latency=decision.effective_latency,
            capacity=decision.effective_capacity,
            available=route.available and decision.effective_capacity >= request.demand_capacity,
            demand_capacity=(
                route.demand_capacity
                if route.demand_capacity is not None
                else request.demand_capacity
            ),
            loss_rate=_combine_loss_rate(route.loss_rate, decision.collision_loss_rate),
        )

    def _frame_overhead_ratio(self) -> float:
        total_bytes = self._profile.frame_payload_bytes + self._profile.frame_header_bytes
        return self._profile.frame_header_bytes / total_bytes


def default_data_link_runtime(protocol: DataLinkProtocol) -> DataLinkRuntime:
    """Return a deterministic default data-link runtime."""

    if not isinstance(protocol, DataLinkProtocol):
        protocol = DataLinkProtocol(str(protocol))
    if protocol == DataLinkProtocol.SLOTTED_ALOHA:
        return DataLinkRuntime(
            DataLinkProfile(
                protocol=DataLinkProtocol.SLOTTED_ALOHA,
                frame_payload_bytes=1500,
                frame_header_bytes=22,
                medium_access_efficiency=0.62,
                scheduling_delay_s=0.005,
                collision_loss_rate=0.08,
                contention_backoff_slots=2,
                slot_duration_s=0.002,
            )
        )
    if protocol == DataLinkProtocol.CSMA_CA:
        return DataLinkRuntime(
            DataLinkProfile(
                protocol=DataLinkProtocol.CSMA_CA,
                frame_payload_bytes=1500,
                frame_header_bytes=26,
                medium_access_efficiency=0.78,
                scheduling_delay_s=0.003,
                collision_loss_rate=0.03,
                contention_backoff_slots=1,
                slot_duration_s=0.001,
            )
        )
    return DataLinkRuntime(
        DataLinkProfile(
            protocol=DataLinkProtocol.TDMA,
            frame_payload_bytes=1500,
            frame_header_bytes=18,
            medium_access_efficiency=0.96,
            scheduling_delay_s=0.001,
        )
    )


def _combine_loss_rate(left: float | None, right: float) -> float:
    base = 0.0 if left is None else float(left)
    return 1.0 - (1.0 - base) * (1.0 - float(right))


def _require_positive_int(value: int, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field_name} must be an int")
    if value <= 0:
        raise ValueError(f"{field_name} must be positive")


def _require_non_negative_int(value: int, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field_name} must be an int")
    if value < 0:
        raise ValueError(f"{field_name} must be non-negative")


def _require_non_negative_number(value: Any, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field_name} must be an int or float")
    if not isfinite(float(value)) or value < 0.0:
        raise ValueError(f"{field_name} must be finite and non-negative")


def _require_unit_interval(value: Any, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field_name} must be an int or float")
    if not isfinite(float(value)) or value <= 0.0 or value > 1.0:
        raise ValueError(f"{field_name} must be in (0, 1]")


def _require_probability(value: Any, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field_name} must be an int or float")
    if not isfinite(float(value)) or value < 0.0 or value >= 1.0:
        raise ValueError(f"{field_name} must be in [0, 1)")
