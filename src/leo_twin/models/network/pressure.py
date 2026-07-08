"""Deterministic flow-level network pressure accounting.

This module is intentionally flow-level. It tracks reserved demand on routed
links and exposes congestion proxy helpers without modelling packets.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping


PressureEdge = tuple[str, str]

QUEUE_UTILIZATION_THRESHOLD = 0.75
LOSS_UTILIZATION_THRESHOLD = 0.80
MAX_PRESSURE_LOSS_RATE = 0.95
ADMISSION_UTILIZATION_LIMIT = 1.20
NETWORK_TIME_PRESSURE_PERIOD_S = 120.0


@dataclass(frozen=True)
class FlowPressureReservation:
    """A flow-level demand reservation over one or more routed pressure edges."""

    flow_id: str
    edges: tuple[PressureEdge, ...]
    demand_capacity: float


@dataclass(frozen=True)
class PressureEdgeQueueState:
    """Projected queue pressure for one edge before admitting a new flow."""

    edge: PressureEdge
    active_demand: float
    incoming_demand: float
    projected_demand: float
    capacity: float
    projected_utilization: float
    pressure_utilization: float
    queued_demand: float
    queue_delay_s: float
    loss_rate: float
    status: str


@dataclass(frozen=True)
class RoutePressureDecision:
    """Flow-level admission and queue decision for one candidate route."""

    admitted: bool
    edge_states: tuple[PressureEdgeQueueState, ...]
    max_projected_utilization: float
    pressure_utilization: float
    queue_delay_s: float
    loss_rate: float
    blocked_reason: str | None = None


class FlowPressureLedger:
    """Track active flow demand per routed edge deterministically."""

    def __init__(self) -> None:
        self._flow_reservations: dict[str, FlowPressureReservation] = {}
        self._edge_active_demand: dict[PressureEdge, float] = {}

    @property
    def reservations(self) -> Mapping[str, FlowPressureReservation]:
        return MappingProxyType(self._flow_reservations)

    @property
    def edge_active_demand(self) -> Mapping[PressureEdge, float]:
        return MappingProxyType(self._edge_active_demand)

    def reserve(
        self,
        flow_id: str,
        edges: tuple[PressureEdge, ...],
        demand_capacity: float,
    ) -> tuple[PressureEdge, ...]:
        """Reserve demand for a flow and return the newly affected edges."""

        self.release(flow_id)
        demand = float(demand_capacity)
        if not edges or demand <= 0.0:
            return ()

        reservation = FlowPressureReservation(
            flow_id=str(flow_id),
            edges=tuple(edges),
            demand_capacity=demand,
        )
        self._flow_reservations[reservation.flow_id] = reservation
        for edge in reservation.edges:
            self._edge_active_demand[edge] = (
                self._edge_active_demand.get(edge, 0.0) + reservation.demand_capacity
            )
        return reservation.edges

    def release(self, flow_id: str) -> tuple[PressureEdge, ...]:
        """Release a flow reservation and return the affected edges."""

        reservation = self._flow_reservations.pop(str(flow_id), None)
        if reservation is None or reservation.demand_capacity <= 0.0:
            return ()

        for edge in reservation.edges:
            next_demand = max(
                0.0,
                self._edge_active_demand.get(edge, 0.0) - reservation.demand_capacity,
            )
            if next_demand == 0.0:
                self._edge_active_demand.pop(edge, None)
            else:
                self._edge_active_demand[edge] = next_demand
        return reservation.edges

    def active_demand(self, edge: PressureEdge) -> float:
        return self._edge_active_demand.get(edge, 0.0)

    def utilization(self, edge: PressureEdge, link_capacity: float) -> float:
        if link_capacity <= 0.0:
            return 1.0
        return min(1.0, self.active_demand(edge) / float(link_capacity))

    def evaluate_route(
        self,
        *,
        edges: tuple[PressureEdge, ...],
        demand_capacity: float,
        edge_capacities: Mapping[PressureEdge, float],
        base_latency_s: float,
        admission_utilization_limit: float = ADMISSION_UTILIZATION_LIMIT,
    ) -> RoutePressureDecision:
        """Project whether a route can admit another flow.

        The decision is deterministic and flow-level: it uses active reserved
        demand plus the incoming flow demand. It does not model packets.
        """

        demand = max(0.0, float(demand_capacity))
        if not edges or demand <= 0.0:
            return RoutePressureDecision(
                admitted=True,
                edge_states=(),
                max_projected_utilization=0.0,
                pressure_utilization=0.0,
                queue_delay_s=0.0,
                loss_rate=0.0,
            )

        states: list[PressureEdgeQueueState] = []
        max_projected_utilization = 0.0
        pressure_utilization = 0.0
        blocked_reason: str | None = None
        for edge in edges:
            capacity = float(edge_capacities.get(edge, 0.0))
            active_demand = self.active_demand(edge)
            projected_demand = active_demand + demand
            if capacity <= 0.0:
                projected_utilization = float("inf")
                next_pressure_utilization = 1.0
                queued_demand = projected_demand
                status = "rejected"
                blocked_reason = blocked_reason or "non_positive_capacity"
            else:
                projected_utilization = projected_demand / capacity
                next_pressure_utilization = min(1.0, projected_utilization)
                queued_demand = max(0.0, projected_demand - capacity)
                if projected_utilization > admission_utilization_limit:
                    status = "rejected"
                    blocked_reason = blocked_reason or "pressure_admission_limit"
                elif projected_utilization > 1.0:
                    status = "saturated"
                elif projected_utilization > QUEUE_UTILIZATION_THRESHOLD:
                    status = "queued"
                else:
                    status = "nominal"

            max_projected_utilization = max(max_projected_utilization, projected_utilization)
            pressure_utilization = max(pressure_utilization, next_pressure_utilization)
            states.append(
                PressureEdgeQueueState(
                    edge=edge,
                    active_demand=active_demand,
                    incoming_demand=demand,
                    projected_demand=projected_demand,
                    capacity=capacity,
                    projected_utilization=projected_utilization,
                    pressure_utilization=next_pressure_utilization,
                    queued_demand=queued_demand,
                    queue_delay_s=pressure_queue_delay(
                        base_latency_s,
                        next_pressure_utilization,
                    ),
                    loss_rate=pressure_loss_rate(next_pressure_utilization),
                    status=status,
                )
            )

        return RoutePressureDecision(
            admitted=blocked_reason is None,
            edge_states=tuple(states),
            max_projected_utilization=max_projected_utilization,
            pressure_utilization=pressure_utilization,
            queue_delay_s=pressure_queue_delay(base_latency_s, pressure_utilization),
            loss_rate=pressure_loss_rate(pressure_utilization),
            blocked_reason=blocked_reason,
        )


def pressure_loss_rate(
    utilization: float,
    *,
    loss_threshold: float = LOSS_UTILIZATION_THRESHOLD,
    max_loss_rate: float = MAX_PRESSURE_LOSS_RATE,
) -> float:
    """Return the deterministic flow-level congestion loss proxy."""

    if utilization <= loss_threshold:
        return 0.0
    return min(max_loss_rate, max(0.0, (utilization - loss_threshold) * 0.5))


def pressure_queue_delay(
    base_latency_s: float,
    utilization: float,
    *,
    queue_threshold: float = QUEUE_UTILIZATION_THRESHOLD,
) -> float:
    """Return the deterministic flow-level queue delay proxy in seconds."""

    return float(base_latency_s) * max(0.0, float(utilization) - queue_threshold)


def time_varying_pressure_phase(
    sim_time: float,
    *,
    period_s: float = NETWORK_TIME_PRESSURE_PERIOD_S,
) -> float:
    """Return the deterministic normalized time-pressure phase for KPI proxies."""

    period = float(period_s)
    if period <= 0.0:
        return 0.0
    return (max(0.0, float(sim_time)) % period) / period


def time_varying_pressure_factor(
    sim_time: float,
    load_pressure: float,
    *,
    period_s: float = NETWORK_TIME_PRESSURE_PERIOD_S,
) -> float:
    """Return a deterministic load-gated temporal pressure factor.

    This is a flow-level proxy for synchronized demand bursts. It is not a
    packet-level model and it never introduces randomness.
    """

    pressure = _clamp_probability(load_pressure)
    if pressure <= 0.0:
        return 0.0
    phase = time_varying_pressure_phase(sim_time, period_s=period_s)
    triangular_wave = 1.0 - abs((2.0 * phase) - 1.0)
    envelope = 0.45 + (0.55 * triangular_wave)
    return _clamp_probability(pressure * envelope)


def time_varying_pressure_loss_rate(time_pressure_factor: float) -> float:
    """Return deterministic loss proxy contributed by temporal pressure."""

    return _clamp_probability(max(0.0, float(time_pressure_factor) - 0.55) * 0.2)


def time_varying_pressure_delay_variation(
    effective_latency_s: float,
    time_pressure_factor: float,
) -> float:
    """Return deterministic delay variation contributed by temporal pressure."""

    latency = max(0.0, float(effective_latency_s))
    if latency <= 0.0:
        return 0.0
    return latency * max(0.0, float(time_pressure_factor) - 0.4) * 0.2


def _clamp_probability(value: float) -> float:
    return min(1.0, max(0.0, float(value)))
