"""Deterministic network-layer routing protocol runtime."""

from __future__ import annotations

from dataclasses import dataclass
from heapq import heappop, heappush
from math import isfinite
from typing import Any

from leo_twin.schema import FlowRequest, LinkState, Route, RoutingProtocol


@dataclass(frozen=True)
class StaticRouteEntry:
    """Configured static route path for one source-target pair."""

    source_id: str
    target_id: str
    path: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_non_empty_str(self.source_id, "source_id")
        _require_non_empty_str(self.target_id, "target_id")
        if len(self.path) < 2:
            raise ValueError("path must contain at least source and target")
        if self.path[0] != self.source_id or self.path[-1] != self.target_id:
            raise ValueError("path endpoints must match source_id and target_id")
        for endpoint_id in self.path:
            _require_non_empty_str(endpoint_id, "path")


@dataclass(frozen=True)
class RoutingCostProfile:
    """Deterministic route cost weights for path selection."""

    latency_weight: float = 1.0
    inverse_capacity_weight: float = 0.0
    hop_weight: float = 0.0

    def __post_init__(self) -> None:
        _require_non_negative_number(self.latency_weight, "latency_weight")
        _require_non_negative_number(
            self.inverse_capacity_weight,
            "inverse_capacity_weight",
        )
        _require_non_negative_number(self.hop_weight, "hop_weight")
        if (
            self.latency_weight == 0.0
            and self.inverse_capacity_weight == 0.0
            and self.hop_weight == 0.0
        ):
            raise ValueError("at least one routing cost weight must be positive")


class RoutingRuntime:
    """Route flow requests over deterministic logical link states."""

    def __init__(
        self,
        protocol: RoutingProtocol = RoutingProtocol.LINK_STATE,
        static_routes: tuple[StaticRouteEntry, ...] = (),
        cost_profile: RoutingCostProfile | None = None,
    ) -> None:
        if not isinstance(protocol, RoutingProtocol):
            protocol = RoutingProtocol(str(protocol))
        self._protocol = protocol
        self._cost_profile = cost_profile or _default_cost_profile(protocol)
        self._static_routes = {
            (entry.source_id, entry.target_id): entry.path
            for entry in sorted(static_routes, key=lambda item: (item.source_id, item.target_id))
        }

    @property
    def protocol(self) -> RoutingProtocol:
        return self._protocol

    @property
    def cost_profile(self) -> RoutingCostProfile:
        return self._cost_profile

    def route(
        self,
        request: FlowRequest,
        links: tuple[LinkState, ...],
    ) -> Route:
        """Return a deterministic route for one request."""

        if self._protocol == RoutingProtocol.STATIC:
            path = self._static_routes.get((request.source_id, request.target_id), ())
            if not path:
                return _unavailable_route(request)
            return self._route_for_path(request, links, path)

        if self._protocol in {
            RoutingProtocol.SHORTEST_PATH,
            RoutingProtocol.LINK_STATE,
            RoutingProtocol.DISTANCE_VECTOR,
        }:
            path = _shortest_path(request, links, self._cost_profile)
            if not path:
                return _unavailable_route(request)
            return self._route_for_path(request, links, path)

        return _unavailable_route(request)

    def _route_for_path(
        self,
        request: FlowRequest,
        links: tuple[LinkState, ...],
        path: tuple[str, ...],
    ) -> Route:
        link_by_edge = _link_by_edge(links)
        latency = 0.0
        capacity: float | None = None
        for source_id, target_id in zip(path, path[1:]):
            link = link_by_edge.get((source_id, target_id))
            if link is None or not link.availability or link.capacity < request.demand_capacity:
                return _unavailable_route(request)
            latency += link.latency
            capacity = link.capacity if capacity is None else min(capacity, link.capacity)
        route_capacity = 0.0 if capacity is None else capacity
        return Route(
            route_id=f"route:{request.flow_id}",
            flow_id=request.flow_id,
            path=path,
            latency=latency,
            capacity=route_capacity,
            available=route_capacity >= request.demand_capacity,
        )


def _shortest_path(
    request: FlowRequest,
    links: tuple[LinkState, ...],
    cost_profile: RoutingCostProfile,
) -> tuple[str, ...]:
    adjacency = _adjacency(links, request.demand_capacity)
    queue: list[tuple[float, tuple[str, ...], str]] = [
        (0.0, (request.source_id,), request.source_id)
    ]
    best: dict[str, tuple[float, tuple[str, ...]]] = {
        request.source_id: (0.0, (request.source_id,))
    }
    while queue:
        cost, path, current_id = heappop(queue)
        if best.get(current_id) != (cost, path):
            continue
        if current_id == request.target_id:
            return path
        for adjacent_id, edge in adjacency.get(current_id, ()):
            candidate_cost = cost + _edge_cost(edge, cost_profile)
            candidate_path = path + (adjacent_id,)
            current = best.get(adjacent_id)
            candidate = (candidate_cost, candidate_path)
            if current is None or candidate < current:
                best[adjacent_id] = candidate
                heappush(queue, (candidate_cost, candidate_path, adjacent_id))
    return ()


def _default_cost_profile(protocol: RoutingProtocol) -> RoutingCostProfile:
    if protocol == RoutingProtocol.DISTANCE_VECTOR:
        return RoutingCostProfile(latency_weight=0.0, hop_weight=1.0)
    return RoutingCostProfile()


def _edge_cost(edge: LinkState, cost_profile: RoutingCostProfile) -> float:
    return (
        edge.latency * cost_profile.latency_weight
        + cost_profile.inverse_capacity_weight / edge.capacity
        + cost_profile.hop_weight
    )


def _adjacency(
    links: tuple[LinkState, ...],
    demand_capacity: float,
) -> dict[str, tuple[tuple[str, LinkState], ...]]:
    working: dict[str, list[tuple[str, LinkState]]] = {}
    for edge in sorted(links, key=lambda item: (item.source_id, item.target_id)):
        if not edge.availability or edge.capacity < demand_capacity:
            continue
        working.setdefault(edge.source_id, []).append((edge.target_id, edge))
        working.setdefault(edge.target_id, []).append((edge.source_id, edge))
    return {
        endpoint_id: tuple(sorted(neighbors, key=lambda item: item[0]))
        for endpoint_id, neighbors in sorted(working.items())
    }


def _link_by_edge(links: tuple[LinkState, ...]) -> dict[tuple[str, str], LinkState]:
    result: dict[tuple[str, str], LinkState] = {}
    for edge in sorted(links, key=lambda item: (item.source_id, item.target_id)):
        result[(edge.source_id, edge.target_id)] = edge
        result[(edge.target_id, edge.source_id)] = edge
    return result


def _unavailable_route(request: FlowRequest) -> Route:
    return Route(
        route_id=f"route:{request.flow_id}",
        flow_id=request.flow_id,
        path=(),
        latency=0.0,
        capacity=0.0,
        available=False,
    )


def _require_non_empty_str(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value:
        raise TypeError(f"{field_name} must be a non-empty str")


def _require_non_negative_number(value: Any, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field_name} must be an int or float")
    if not isfinite(value) or value < 0:
        raise ValueError(f"{field_name} must be finite and non-negative")
