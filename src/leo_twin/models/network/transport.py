"""Deterministic flow-level transport protocol runtime."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any

from leo_twin.schema import FlowRequest, Route, TransportProtocol


@dataclass(frozen=True)
class TransportProfile:
    """Configuration for one flow-level transport protocol profile."""

    protocol: TransportProtocol
    payload_unit_bytes: int
    header_bytes: int
    efficiency: float
    handshake_round_trips: int = 0
    loss_rate: float = 0.0
    congestion_window_segments: int | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.protocol, TransportProtocol):
            object.__setattr__(self, "protocol", TransportProtocol(str(self.protocol)))
        _require_positive_int(self.payload_unit_bytes, "payload_unit_bytes")
        _require_non_negative_int(self.header_bytes, "header_bytes")
        _require_unit_interval(self.efficiency, "efficiency")
        _require_non_negative_int(self.handshake_round_trips, "handshake_round_trips")
        _require_probability(self.loss_rate, "loss_rate")
        if self.congestion_window_segments is not None:
            _require_positive_int(
                self.congestion_window_segments,
                "congestion_window_segments",
            )


@dataclass(frozen=True)
class TransportDecision:
    """Deterministic transport-layer decision for one route."""

    protocol: TransportProtocol
    route_id: str
    effective_latency: float
    effective_capacity: float
    overhead_ratio: float
    loss_rate: float = 0.0
    window_capacity_mbps: float | None = None


class TransportRuntime:
    """Apply a transport profile to route latency and capacity."""

    def __init__(self, profile: TransportProfile) -> None:
        self._profile = profile

    @property
    def profile(self) -> TransportProfile:
        return self._profile

    def decision(self, route: Route) -> TransportDecision:
        """Return the deterministic transport-layer decision for a route."""

        if not route.available:
            return TransportDecision(
                protocol=self._profile.protocol,
                route_id=route.route_id,
                effective_latency=route.latency,
                effective_capacity=0.0,
                overhead_ratio=self._overhead_ratio(),
                loss_rate=self._profile.loss_rate,
                window_capacity_mbps=None,
            )
        effective_latency = route.latency * (1.0 + self._profile.handshake_round_trips)
        base_capacity = route.capacity * self._profile.efficiency * (
            1.0 - self._overhead_ratio()
        ) * (1.0 - self._profile.loss_rate)
        window_capacity = self._window_capacity_mbps(route)
        effective_capacity = (
            base_capacity
            if window_capacity is None
            else min(base_capacity, window_capacity)
        )
        return TransportDecision(
            protocol=self._profile.protocol,
            route_id=route.route_id,
            effective_latency=effective_latency,
            effective_capacity=effective_capacity,
            overhead_ratio=self._overhead_ratio(),
            loss_rate=self._profile.loss_rate,
            window_capacity_mbps=window_capacity,
        )

    def apply(self, request: FlowRequest, route: Route) -> Route:
        """Return a route whose latency/capacity reflect transport behavior."""

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
            loss_rate=_combine_loss_rate(route.loss_rate, decision.loss_rate),
        )

    def _overhead_ratio(self) -> float:
        total_bytes = self._profile.payload_unit_bytes + self._profile.header_bytes
        return self._profile.header_bytes / total_bytes

    def _window_capacity_mbps(self, route: Route) -> float | None:
        if self._profile.congestion_window_segments is None:
            return None
        round_trip_time_s = max(route.latency, 1e-9)
        payload_bits = (
            self._profile.congestion_window_segments
            * self._profile.payload_unit_bytes
            * 8.0
        )
        return payload_bits / round_trip_time_s / 1_000_000.0


def default_transport_runtime(protocol: TransportProtocol) -> TransportRuntime:
    """Return a deterministic default transport runtime."""

    if not isinstance(protocol, TransportProtocol):
        protocol = TransportProtocol(str(protocol))
    if protocol == TransportProtocol.TCP:
        return TransportRuntime(
            TransportProfile(
                protocol=TransportProtocol.TCP,
                payload_unit_bytes=1460,
                header_bytes=40,
                efficiency=0.92,
                handshake_round_trips=1,
            )
        )
    return TransportRuntime(
        TransportProfile(
            protocol=TransportProtocol.UDP,
            payload_unit_bytes=1472,
            header_bytes=28,
            efficiency=0.98,
            handshake_round_trips=0,
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
