"""Event-driven network engine backed by satellite positions."""

from __future__ import annotations

from collections.abc import Iterable
from math import ceil, floor, isfinite
from typing import Any

from leo_twin.core import SimulationKernel, SimulationModule
from leo_twin.models.compute.contracts import COMPUTE_NODE_UPDATE
from leo_twin.models.network.application import ApplicationRuntime
from leo_twin.models.network.channel import ChannelBudgetSelector, LinkBudgetCalculator
from leo_twin.models.network.datalink import DataLinkRuntime
from leo_twin.models.network.geometry import (
    AccessLinkCandidate,
    GroundEndpoint,
    PositionDrivenAccessModel,
)
from leo_twin.models.network.routing import RoutingRuntime
from leo_twin.models.network.stack import NetworkStackRuntime, NetworkStackTrace
from leo_twin.models.network.transport import TransportRuntime
from leo_twin.schema import (
    AccessAssociation,
    AntennaProfile,
    ComputeNodeState,
    EventType,
    FlowRequest,
    LinkMedium,
    LinkState,
    Route,
    SatelliteState,
    SimEvent,
)


SpaceCellId = tuple[int, int, int]


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
        link_budget_selector: ChannelBudgetSelector | None = None,
        application_runtime: ApplicationRuntime | None = None,
        routing_runtime: RoutingRuntime | None = None,
        data_link_runtime: DataLinkRuntime | None = None,
        transport_runtime: TransportRuntime | None = None,
        stack_runtime: NetworkStackRuntime | None = None,
        static_links: Iterable[LinkState] = (),
        space_link_max_range_km: float | None = None,
        space_link_capacity: float | None = None,
        space_link_cell_size_km: float | None = None,
        space_link_update_latency_epsilon_s: float = 0.0,
        space_link_update_capacity_epsilon: float = 0.0,
        position_scale_to_km: float = 1.0,
    ) -> None:
        _require_non_empty_str(module_name, "module_name")
        _require_non_empty_str(metrics_target, "metrics_target")
        _require_positive_number(link_capacity, "link_capacity")
        _require_positive_number(propagation_speed_km_s, "propagation_speed_km_s")
        _require_non_negative_number(base_latency_s, "base_latency_s")
        if space_link_max_range_km is not None:
            _require_positive_number(space_link_max_range_km, "space_link_max_range_km")
        if space_link_capacity is not None:
            _require_positive_number(space_link_capacity, "space_link_capacity")
        if space_link_cell_size_km is not None:
            _require_positive_number(space_link_cell_size_km, "space_link_cell_size_km")
        _require_non_negative_number(
            space_link_update_latency_epsilon_s,
            "space_link_update_latency_epsilon_s",
        )
        _require_non_negative_number(
            space_link_update_capacity_epsilon,
            "space_link_update_capacity_epsilon",
        )
        _require_positive_number(position_scale_to_km, "position_scale_to_km")
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
        self._link_budget_selector = link_budget_selector
        self._application_runtime = application_runtime
        self._routing_runtime = routing_runtime
        self._data_link_runtime = data_link_runtime
        self._transport_runtime = transport_runtime
        self._stack_runtime = stack_runtime
        self._static_links = tuple(
            sorted(static_links, key=lambda item: (item.source_id, item.target_id))
        )
        self._space_link_max_range_km = space_link_max_range_km
        self._space_link_capacity = float(space_link_capacity or link_capacity)
        self._space_link_cell_size_km = float(
            space_link_cell_size_km
            or space_link_max_range_km
            or cell_size_km
        )
        self._space_link_update_latency_epsilon_s = float(space_link_update_latency_epsilon_s)
        self._space_link_update_capacity_epsilon = float(space_link_update_capacity_epsilon)
        self._position_scale_to_km = float(position_scale_to_km)
        self._satellite_states: dict[str, SatelliteState] = {}
        self._satellite_space_cells: dict[str, SpaceCellId] = {}
        self._satellites_by_space_cell: dict[SpaceCellId, set[str]] = {}
        self._active_links: dict[tuple[str, str], LinkState] = {}
        self._active_space_links: dict[tuple[str, str], LinkState] = {}
        self._active_flows: dict[str, FlowRequest] = {}
        self._last_routes: dict[str, Route] = {}
        self._last_stack_traces: dict[str, NetworkStackTrace] = {}
        self._last_links: dict[tuple[str, str], LinkState] = {}
        self._compute_load_by_node: dict[str, float] = {}
        self._event_sequence = 0

    def name(self) -> str:
        return self._module_name

    def on_event(self, event: SimEvent, kernel: SimulationKernel) -> None:
        if event.event_type == EventType.ORBIT_UPDATE:
            state = self._coerce_satellite_state(event.payload)
            geometry_state = self._state_for_geometry(state)
            emitted_events = list(self._update_for_state(geometry_state, event.sim_time))
            if emitted_events:
                emitted_events.extend(self._reroute_active_flows(event.sim_time))
            for emitted in emitted_events:
                kernel.schedule_event(emitted)
            return

        if event.event_type == EventType.FLOW_ARRIVAL:
            request = self._coerce_flow_request(event.payload)
            self._active_flows[request.flow_id] = request
            route = self.route_flow(request)
            self._last_routes[request.flow_id] = route
            for emitted in self._route_events(event.sim_time, route):
                kernel.schedule_event(emitted)
            return

        if event.event_type == COMPUTE_NODE_UPDATE:
            state = self._coerce_compute_node_state(event.payload)
            next_load = _compute_load_factor(state)
            if self._compute_load_by_node.get(state.node_id) == next_load:
                return
            self._compute_load_by_node[state.node_id] = next_load
            for emitted in self._reroute_active_flows(event.sim_time):
                kernel.schedule_event(emitted)

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

        access_links = tuple(self._active_links[key] for key in sorted(self._active_links))
        space_links = tuple(
            self._active_space_links[key] for key in sorted(self._active_space_links)
        )
        return access_links + space_links

    def stack_traces(self) -> tuple[NetworkStackTrace, ...]:
        """Return latest protocol stack traces in deterministic flow order."""

        return tuple(
            self._last_stack_traces[flow_id]
            for flow_id in sorted(self._last_stack_traces)
        )

    def stack_trace_for_flow(self, flow_id: str) -> NetworkStackTrace | None:
        """Return the latest protocol stack trace for one flow, if available."""

        return self._last_stack_traces.get(flow_id)

    def route_flow(self, request: FlowRequest) -> Route:
        """Route one flow through the best currently active access link."""

        request = self._apply_application(request)
        if self._routing_runtime is not None:
            route = self._routing_runtime.route(
                request,
                self._routing_links_for_request(request),
            )
        elif request.target_id not in self._compute_node_ids:
            route = _unavailable_route(request)
        else:
            candidates = tuple(
                link
                for key, link in sorted(self._active_links.items())
                if key[1] == request.source_id and link.capacity >= request.demand_capacity
            )
            if not candidates:
                route = _unavailable_route(request)
            else:
                selected = min(
                    candidates,
                    key=lambda item: (item.latency, item.source_id, item.target_id),
                )
                route = Route(
                    route_id=f"route:{request.flow_id}",
                    flow_id=request.flow_id,
                    path=(request.source_id, selected.source_id, request.target_id),
                    latency=selected.latency,
                    capacity=selected.capacity,
                    available=True,
                )
        linked = self._apply_data_link(request, route)
        routed = self._apply_transport(request, linked)
        self._record_stack_trace(request, routed)
        return routed

    def _apply_application(self, request: FlowRequest) -> FlowRequest:
        if self._application_runtime is None:
            return request
        return self._application_runtime.apply(request)

    def _routing_links_for_request(self, request: FlowRequest) -> tuple[LinkState, ...]:
        access_links = tuple(
            link
            for link in self._active_links.values()
            if link.target_id == request.source_id or link.source_id == request.source_id
        )
        return tuple(
            sorted(
                access_links
                + tuple(self._active_space_links.values())
                + self._static_links_for_routing(),
                key=lambda item: (item.source_id, item.target_id),
            )
        )

    def _static_links_for_routing(self) -> tuple[LinkState, ...]:
        return tuple(
            self._static_link_with_compute_load(link) for link in self._static_links
        )

    def _static_link_with_compute_load(self, link: LinkState) -> LinkState:
        load_factor = self._compute_load_by_node.get(link.target_id)
        if load_factor is None:
            load_factor = self._compute_load_by_node.get(link.source_id)
        if load_factor is None or load_factor <= 0.0:
            return link
        capacity_factor = max(0.1, 1.0 - load_factor)
        return LinkState(
            source_id=link.source_id,
            target_id=link.target_id,
            latency=link.latency,
            capacity=link.capacity * capacity_factor,
            availability=link.availability,
        )

    def _apply_transport(self, request: FlowRequest, route: Route) -> Route:
        if self._transport_runtime is None:
            return route
        return self._transport_runtime.apply(request, route)

    def _apply_data_link(self, request: FlowRequest, route: Route) -> Route:
        if self._data_link_runtime is None:
            return route
        return self._data_link_runtime.apply(request, route)

    def _record_stack_trace(self, request: FlowRequest, route: Route) -> None:
        if self._stack_runtime is None:
            return
        self._last_stack_traces[request.flow_id] = self._stack_runtime.process_flow(
            request,
            route,
        )

    def _reroute_active_flows(self, dispatch_time: float) -> tuple[SimEvent, ...]:
        emitted: list[SimEvent] = []
        for flow_id in sorted(self._active_flows):
            request = self._active_flows[flow_id]
            route = self.route_flow(request)
            if self._last_routes.get(flow_id) == route:
                continue
            self._last_routes[flow_id] = route
            emitted.extend(self._route_events(dispatch_time, route))
        return tuple(emitted)

    def _update_for_state(
        self,
        state: SatelliteState,
        dispatch_time: float,
    ) -> tuple[SimEvent, ...]:
        emitted: list[SimEvent] = []
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
        emitted.extend(self._update_space_links_for_state(state, dispatch_time))
        return tuple(emitted)

    def _update_space_links_for_state(
        self,
        state: SatelliteState,
        dispatch_time: float,
    ) -> tuple[SimEvent, ...]:
        self._satellite_states[state.satellite_id] = state
        self._update_space_index(state)
        if self._space_link_max_range_km is None:
            return ()

        emitted: list[SimEvent] = []
        candidate_ids = self._space_link_candidate_ids(state)
        for other_id in candidate_ids:
            if other_id == state.satellite_id:
                continue
            other_state = self._satellite_states[other_id]
            pair = tuple(sorted((state.satellite_id, other_state.satellite_id)))
            candidate = self._space_link_from_states(
                left=state,
                right=other_state,
                pair=pair,
            )
            previous = self._active_space_links.get(pair)
            if candidate is None:
                if previous is None:
                    continue
                ended = LinkState(
                    source_id=previous.source_id,
                    target_id=previous.target_id,
                    latency=previous.latency,
                    capacity=previous.capacity,
                    availability=False,
                )
                self._active_space_links.pop(pair, None)
                emitted.append(
                    self._event(
                        dispatch_time=dispatch_time,
                        target=self._metrics_target,
                        event_type=EventType.LINK_UPDATE.value,
                        payload=ended,
                    )
                )
                continue

            self._active_space_links[pair] = candidate
            if self._should_emit_space_link_update(previous, candidate):
                emitted.append(
                    self._event(
                        dispatch_time=dispatch_time,
                        target=self._metrics_target,
                        event_type=EventType.LINK_UPDATE.value,
                        payload=candidate,
                    )
                )
        return tuple(emitted)

    def _update_space_index(self, state: SatelliteState) -> None:
        next_cell = _space_cell_for(state.position, self._space_link_cell_size_km)
        previous_cell = self._satellite_space_cells.get(state.satellite_id)
        if previous_cell == next_cell:
            return
        if previous_cell is not None:
            previous_ids = self._satellites_by_space_cell.get(previous_cell)
            if previous_ids is not None:
                previous_ids.discard(state.satellite_id)
            if previous_ids is not None and not previous_ids:
                self._satellites_by_space_cell.pop(previous_cell, None)
        self._satellite_space_cells[state.satellite_id] = next_cell
        self._satellites_by_space_cell.setdefault(next_cell, set()).update(
            (state.satellite_id,)
        )

    def _space_link_candidate_ids(self, state: SatelliteState) -> tuple[str, ...]:
        nearby_ids = set(
            _nearby_satellite_ids(
                position=state.position,
                cell_size_km=self._space_link_cell_size_km,
                radius_km=float(self._space_link_max_range_km),
                satellites_by_cell=self._satellites_by_space_cell,
            )
        )
        active_neighbor_ids = {
            pair[1] if pair[0] == state.satellite_id else pair[0]
            for pair in self._active_space_links
            if state.satellite_id in pair
        }
        return tuple(sorted(nearby_ids | active_neighbor_ids))

    def _space_link_from_states(
        self,
        left: SatelliteState,
        right: SatelliteState,
        pair: tuple[str, str],
    ) -> LinkState | None:
        if left.status != "ACTIVE" or right.status != "ACTIVE":
            return None
        range_km = _distance_km(left.position, right.position)
        if range_km <= 0.0:
            return None
        if range_km > float(self._space_link_max_range_km):
            return None
        budget_calculator = self._budget_calculator_for(LinkMedium.SPACE_SPACE)
        if budget_calculator is None:
            latency = self._base_latency_s + range_km / self._propagation_speed_km_s
            capacity = self._space_link_capacity
        else:
            budget = budget_calculator.evaluate(range_km)
            latency = self._base_latency_s + budget.propagation_delay_s
            capacity = min(self._space_link_capacity, budget.capacity_mbps)
        return LinkState(
            source_id=pair[0],
            target_id=pair[1],
            latency=latency,
            capacity=capacity,
            availability=True,
        )

    def _should_emit_space_link_update(
        self,
        previous: LinkState | None,
        candidate: LinkState,
    ) -> bool:
        if previous is None:
            return True
        if previous.availability != candidate.availability:
            return True
        if abs(previous.latency - candidate.latency) > self._space_link_update_latency_epsilon_s:
            return True
        if abs(previous.capacity - candidate.capacity) > self._space_link_update_capacity_epsilon:
            return True
        return False

    def _link_from_candidate(
        self,
        candidate: AccessLinkCandidate,
        availability: bool,
    ) -> LinkState:
        budget_calculator = self._budget_calculator_for(LinkMedium.SPACE_GROUND)
        if budget_calculator is None:
            latency = self._base_latency_s + candidate.range_km / self._propagation_speed_km_s
            capacity = self._link_capacity
        else:
            budget = budget_calculator.evaluate(
                candidate.range_km,
                transmit_off_boresight_deg=_off_boresight_from_elevation(
                    budget_calculator.transmit_terminal.antenna,
                    candidate.elevation_deg,
                ),
                receive_off_boresight_deg=_off_boresight_from_elevation(
                    budget_calculator.receive_terminal.antenna,
                    candidate.elevation_deg,
                ),
            )
            latency = self._base_latency_s + budget.propagation_delay_s
            capacity = min(self._link_capacity, budget.capacity_mbps)
        return LinkState(
            source_id=candidate.satellite_id,
            target_id=candidate.endpoint_id,
            latency=latency,
            capacity=capacity,
            availability=availability,
        )

    def _budget_calculator_for(
        self,
        medium: LinkMedium,
    ) -> LinkBudgetCalculator | None:
        if self._link_budget_selector is not None:
            return self._link_budget_selector.optional_calculator_for(medium)
        if medium == LinkMedium.SPACE_GROUND:
            return self._link_budget_calculator
        return None

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

    def _route_events(
        self,
        dispatch_time: float,
        route: Route,
    ) -> tuple[SimEvent, ...]:
        return tuple(
            self._event(
                dispatch_time=dispatch_time,
                target=target,
                event_type=EventType.ROUTE_UPDATE.value,
                payload=route,
            )
            for target in self._route_targets
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

    def _state_for_geometry(self, state: SatelliteState) -> SatelliteState:
        if self._position_scale_to_km == 1.0:
            return state
        return SatelliteState(
            satellite_id=state.satellite_id,
            sim_time=state.sim_time,
            position=tuple(value * self._position_scale_to_km for value in state.position),
            velocity=tuple(value * self._position_scale_to_km for value in state.velocity),
            status=state.status,
        )

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

    @staticmethod
    def _coerce_compute_node_state(payload: object) -> ComputeNodeState:
        if isinstance(payload, ComputeNodeState):
            return payload
        if isinstance(payload, dict):
            return ComputeNodeState(
                node_id=str(payload["node_id"]),
                sim_time=float(payload["sim_time"]),
                capacity=float(payload["capacity"]),
                available_capacity=float(payload["available_capacity"]),
                status=str(payload["status"]),
            )
        raise TypeError("COMPUTE_NODE_UPDATE payload must be ComputeNodeState or dict")


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


def _distance_km(
    left: tuple[float, float, float],
    right: tuple[float, float, float],
) -> float:
    delta_x = left[0] - right[0]
    delta_y = left[1] - right[1]
    delta_z = left[2] - right[2]
    return (delta_x * delta_x + delta_y * delta_y + delta_z * delta_z) ** 0.5


def _nearby_satellite_ids(
    position: tuple[float, float, float],
    cell_size_km: float,
    radius_km: float,
    satellites_by_cell: dict[SpaceCellId, set[str]],
) -> tuple[str, ...]:
    center = _space_cell_for(position, cell_size_km)
    span = int(ceil(radius_km / cell_size_km))
    satellite_ids: set[str] = set()
    for x_index in range(center[0] - span, center[0] + span + 1):
        for y_index in range(center[1] - span, center[1] + span + 1):
            for z_index in range(center[2] - span, center[2] + span + 1):
                satellite_ids.update(
                    satellites_by_cell.get((x_index, y_index, z_index), set())
                )
    return tuple(sorted(satellite_ids))


def _space_cell_for(
    position: tuple[float, float, float],
    cell_size_km: float,
) -> SpaceCellId:
    return (
        floor(position[0] / cell_size_km),
        floor(position[1] / cell_size_km),
        floor(position[2] / cell_size_km),
    )


def _off_boresight_from_elevation(
    antenna: AntennaProfile,
    elevation_deg: float,
) -> float:
    _require_finite_number(elevation_deg, "elevation_deg")
    steering_mode = antenna.steering_mode.lower()
    if any(token in steering_mode for token in ("electronic", "tracking", "steerable")):
        return 0.0
    return max(0.0, min(180.0, 90.0 - elevation_deg))


def _compute_load_factor(state: ComputeNodeState) -> float:
    if state.capacity <= 0.0:
        return 1.0
    load = 1.0 - state.available_capacity / state.capacity
    return max(0.0, min(1.0, load))


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
