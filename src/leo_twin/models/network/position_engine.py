"""Event-driven network engine backed by satellite positions."""

from __future__ import annotations

from collections.abc import Iterable
from math import isfinite
from typing import Any

from leo_twin.core import SimulationKernel, SimulationModule
from leo_twin.models.network.channel import LinkBudgetCalculator
from leo_twin.models.network.geometry import (
    AccessLinkCandidate,
    GroundEndpoint,
    PositionDrivenAccessModel,
)
from leo_twin.models.network.routing import RoutingRuntime
from leo_twin.models.network.transport import TransportRuntime
from leo_twin.schema import (
    AccessAssociation,
    EventType,
    FlowRequest,
    LinkState,
    Route,
    SatelliteState,
    SimEvent,
)


class PositionDrivenNetworkEngine(SimulationModule):
    """Maintain satellite-ground access and route flows from orbit updates."""

    def __init__(
        self,
        endpoints: tuple[GroundEndpoint, ...],
        compute_node_ids: Iterable[str],
        module_name: str = "network",
        metrics_target: str = "metrics",
        route_targets: Iterable[str] = ("compute", "metrics"),
        link_capacity: float = 100.0,
        propagation_speed_km_s: float = 299792.458,
        base_latency_s: float = 0.0,
        cell_size_km: float = 1000.0,
        link_budget_calculator: LinkBudgetCalculator | None = None,
        routing_runtime: RoutingRuntime | None = None,
        transport_runtime: TransportRuntime | None = None,
        static_links: Iterable[LinkState] = (),
    ) -> None:
        _require_non_empty_str(module_name, "module_name")
        _require_non_empty_str(metrics_target, "metrics_target")
        _require_positive_number(link_capacity, "link_capacity")
        _require_positive_number(propagation_speed_km_s, "propagation_speed_km_s")
        _require_non_negative_number(base_latency_s, "base_latency_s")
        compute_nodes = tuple(sorted(str(item) for item in compute_node_ids))
        if not compute_nodes or any(not item for item in compute_nodes):
            raise ValueError("compute_node_ids must contain non-empty ids")
        configured_targets = tuple(sorted(str(item) for item in route_targets))
        if not configured_targets or any(not item for item in configured_targets):
            raise ValueError("route_targets must contain non-empty ids")

        self._module_name = module_name
        self._metrics_target = metrics_target
        self._route_targets = tuple(dict.fromkeys(configured_targets))
        self._compute_node_ids = compute_nodes
        self._access_model = PositionDrivenAccessModel(
            endpoints=endpoints,
            cell_size_km=cell_size_km,
        )
        self._link_capacity = float(link_capacity)
        self._propagation_speed_km_s = float(propagation_speed_km_s)
        self._base_latency_s = float(base_latency_s)
        self._link_budget_calculator = link_budget_calculator
        self._routing_runtime = routing_runtime
        self._transport_runtime = transport_runtime
        self._static_links = tuple(sorted(static_links, key=lambda item: (item.source_id, item.target_id)))
        self._active_links: dict[tuple[str, str], LinkState] = {}
        self._last_links: dict[tuple[str, str], LinkState] = {}
        self._event_sequence = 0

    def name(self) -> str:
        return self._module_name

    def on_event(self, event: SimEvent, kernel: SimulationKernel) -> None:
        if event.event_type == EventType.ORBIT_UPDATE:
            state = self._coerce_satellite_state(event.payload)
            for emitted in self._update_for_state(state, event.sim_time):
                kernel.schedule_event(emitted)
            return

        if event.event_type == EventType.FLOW_ARRIVAL:
            request = self._coerce_flow_request(event.payload)
            route = self.route_flow(request)
            for target in self._route_targets:
                kernel.schedule_event(
                    self._event(
                        dispatch_time=event.sim_time,
                        target=target,
                        event_type=EventType.ROUTE_UPDATE.value,
                        payload=route,
                    )
                )

    def update_topology(self, sim_time: float) -> tuple[SimEvent, ...]:
        """Return no-op topology updates for contract compatibility."""

        _require_finite_number(sim_time, "sim_time")
        return ()

    def compute_access(self) -> tuple[AccessAssociation, ...]:
        """Return currently active access associations."""

        return tuple(
            AccessAssociation(satellite_id=satellite_id, user_id=endpoint_id)
            for satellite_id, endpoint_id in sorted(self._active_links)
        )

    def active_link_states(self) -> tuple[LinkState, ...]:
        """Return active links in deterministic order."""

        return tuple(self._active_links[key] for key in sorted(self._active_links))

    def route_flow(self, request: FlowRequest) -> Route:
        """Route one flow through the best currently active access link."""

        if self._routing_runtime is not None:
            route = self._routing_runtime.route(
                request,
                self.active_link_states() + self._static_links,
            )
            return self._apply_transport(request, route)

        if request.target_id not in self._compute_node_ids:
            return _unavailable_route(request)
        candidates = tuple(
            link
            for key, link in sorted(self._active_links.items())
            if key[1] == request.source_id and link.capacity >= request.demand_capacity
        )
        if not candidates:
            return _unavailable_route(request)
        selected = min(candidates, key=lambda item: (item.latency, item.source_id, item.target_id))
        route = Route(
            route_id=f"route:{request.flow_id}",
            flow_id=request.flow_id,
            path=(request.source_id, selected.source_id, request.target_id),
            latency=selected.latency,
            capacity=selected.capacity,
            available=True,
        )
        return self._apply_transport(request, route)

    def _apply_transport(self, request: FlowRequest, route: Route) -> Route:
        if self._transport_runtime is None:
            return route
        return self._transport_runtime.apply(request, route)

    def _update_for_state(
        self,
        state: SatelliteState,
        dispatch_time: float,
    ) -> tuple[SimEvent, ...]:
        candidates = self._access_model.compute_access((state,))
        next_keys = {
            (candidate.satellite_id, candidate.endpoint_id) for candidate in candidates
        }
        previous_keys = {
            key for key in self._active_links if key[0] == state.satellite_id
        }
        ended_keys = tuple(sorted(previous_keys - next_keys))
        started_candidates = tuple(
            sorted(
                (
                    candidate
                    for candidate in candidates
                    if (candidate.satellite_id, candidate.endpoint_id) not in previous_keys
                ),
                key=lambda item: (item.satellite_id, item.endpoint_id),
            )
        )

        emitted: list[SimEvent] = []
        for key in ended_keys:
            previous = self._active_links.pop(key)
            ended = LinkState(
                source_id=previous.source_id,
                target_id=previous.target_id,
                latency=previous.latency,
                capacity=previous.capacity,
                availability=False,
            )
            self._last_links[key] = ended
            emitted.extend(
                self._link_events(
                    dispatch_time=dispatch_time,
                    access_event_type=EventType.ACCESS_END.value,
                    link=ended,
                )
            )

        for candidate in started_candidates:
            key = (candidate.satellite_id, candidate.endpoint_id)
            link = self._link_from_candidate(candidate, availability=True)
            self._active_links[key] = link
            self._last_links[key] = link
            emitted.extend(
                self._link_events(
                    dispatch_time=dispatch_time,
                    access_event_type=EventType.ACCESS_START.value,
                    link=link,
                )
            )
        return tuple(emitted)

    def _link_from_candidate(
        self,
        candidate: AccessLinkCandidate,
        availability: bool,
    ) -> LinkState:
        if self._link_budget_calculator is None:
            latency = self._base_latency_s + candidate.range_km / self._propagation_speed_km_s
            capacity = self._link_capacity
        else:
            budget = self._link_budget_calculator.evaluate(candidate.range_km)
            latency = self._base_latency_s + budget.propagation_delay_s
            capacity = min(self._link_capacity, budget.capacity_mbps)
        return LinkState(
            source_id=candidate.satellite_id,
            target_id=candidate.endpoint_id,
            latency=latency,
            capacity=capacity,
            availability=availability,
        )

    def _link_events(
        self,
        dispatch_time: float,
        access_event_type: str,
        link: LinkState,
    ) -> tuple[SimEvent, SimEvent]:
        return (
            self._event(
                dispatch_time=dispatch_time,
                target=self._metrics_target,
                event_type=access_event_type,
                payload=link,
            ),
            self._event(
                dispatch_time=dispatch_time,
                target=self._metrics_target,
                event_type=EventType.LINK_UPDATE.value,
                payload=link,
            ),
        )

    def _event(
        self,
        dispatch_time: float,
        target: str,
        event_type: str,
        payload: object,
    ) -> SimEvent:
        self._event_sequence += 1
        return SimEvent(
            event_id=f"{self._module_name}:position:{self._event_sequence:08d}",
            sim_time=dispatch_time,
            priority=0,
            source=self._module_name,
            target=target,
            event_type=event_type,
            payload=payload,
        )

    @staticmethod
    def _coerce_satellite_state(payload: object) -> SatelliteState:
        if isinstance(payload, SatelliteState):
            return payload
        if isinstance(payload, dict):
            return SatelliteState(
                satellite_id=str(payload["satellite_id"]),
                sim_time=float(payload["sim_time"]),
                position=_vector3(payload["position"]),
                velocity=_vector3(payload["velocity"]),
                status=str(payload["status"]),
            )
        raise TypeError("ORBIT_UPDATE payload must be SatelliteState or dict")

    @staticmethod
    def _coerce_flow_request(payload: object) -> FlowRequest:
        if isinstance(payload, FlowRequest):
            return payload
        if isinstance(payload, dict):
            return FlowRequest(
                flow_id=str(payload["flow_id"]),
                source_id=str(payload["source_id"]),
                target_id=str(payload["target_id"]),
                demand_capacity=float(payload["demand_capacity"]),
            )
        raise TypeError("FLOW_ARRIVAL payload must be FlowRequest or dict")


def _unavailable_route(request: FlowRequest) -> Route:
    return Route(
        route_id=f"route:{request.flow_id}",
        flow_id=request.flow_id,
        path=(),
        latency=0.0,
        capacity=0.0,
        available=False,
    )


def _vector3(value: Any) -> tuple[float, float, float]:
    if not isinstance(value, (list, tuple)) or len(value) != 3:
        raise TypeError("vector payload fields must have exactly three values")
    return (float(value[0]), float(value[1]), float(value[2]))


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


def _require_non_negative_number(value: Any, field_name: str) -> None:
    _require_finite_number(value, field_name)
    if value < 0:
        raise ValueError(f"{field_name} must be non-negative")
