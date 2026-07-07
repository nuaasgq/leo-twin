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


@dataclass(frozen=True)
class FlowPressureReservation:
    """A flow-level demand reservation over one or more routed pressure edges."""

    flow_id: str
    edges: tuple[PressureEdge, ...]
    demand_capacity: float


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
