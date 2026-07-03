"""Event-driven flow-level network runtime module."""

from collections import deque
from collections.abc import Iterable

from leo_twin.core import SimulationKernel, SimulationModule
from leo_twin.schema import (
    FlowRequest,
    GroundUserProfile,
    LinkState,
    Route,
    SatelliteProfile,
    SimEvent,
)


class NetworkEngine(SimulationModule):
    """Maintain access links and produce deterministic flow-level routes."""

    def __init__(
        self,
        satellites: Iterable[SatelliteProfile],
        ground_users: Iterable[GroundUserProfile],
        module_name: str = "network",
        slot_duration: float = 1.0,
    ) -> None:
        if slot_duration <= 0:
            raise ValueError("slot_duration must be positive")
        self._module_name = module_name
        self._slot_duration = slot_duration
        self._space_profiles = tuple(sorted(satellites, key=lambda item: item.satellite_id))
        self._ground_users = tuple(sorted(ground_users, key=lambda item: item.user_id))
        self._coverage_by_slot = {
            profile.satellite_id: {
                slot.slot: slot.cell_ids for slot in sorted(profile.coverage, key=lambda item: item.slot)
            }
            for profile in self._space_profiles
        }
        self._link_defaults = {
            profile.satellite_id: (profile.link_latency, profile.link_capacity)
            for profile in self._space_profiles
        }
        self._endpoints_by_cell = self._build_endpoint_index(self._ground_users)
        self._access_pairs: frozenset[tuple[str, str]] = frozenset()
        self._links: dict[tuple[str, str], LinkState] = {}
        self._current_slot: int | None = None
        self._event_sequence = 0

    def name(self) -> str:
        return self._module_name

    def on_event(self, event: SimEvent, kernel: SimulationKernel) -> None:
        if event.event_type in {"NETWORK_UPDATE", "COVERAGE_UPDATE"}:
            for emitted in self.update_topology(event.sim_time):
                kernel.schedule_event(emitted)
            return

        if event.event_type == "FLOW_ARRIVAL":
            flow = self._coerce_flow_request(event.payload)
            route = self.route_flow(flow)
            kernel.schedule_event(
                self._event(
                    sim_time=event.sim_time,
                    target=event.source,
                    event_type="ROUTE_UPDATE",
                    payload=route,
                )
            )

    def update_topology(self, sim_time: float) -> tuple[SimEvent, ...]:
        slot = int(sim_time // self._slot_duration)
        self._current_slot = slot
        new_access = frozenset(self._access_for_slot(slot))
        previous_access = self._access_pairs
        started = tuple(sorted(new_access - previous_access))
        ended = tuple(sorted(previous_access - new_access))
        emitted: list[SimEvent] = []

        for source_id, target_id in ended:
            link = self._make_link(source_id, target_id, availability=False)
            self._links[(source_id, target_id)] = link
            emitted.append(self._event(sim_time, self._module_name, "ACCESS_END", link))
            emitted.append(self._event(sim_time, self._module_name, "LINK_UPDATE", link))

        for source_id, target_id in started:
            link = self._make_link(source_id, target_id, availability=True)
            self._links[(source_id, target_id)] = link
            emitted.append(self._event(sim_time, self._module_name, "ACCESS_START", link))
            emitted.append(self._event(sim_time, self._module_name, "LINK_UPDATE", link))

        self._access_pairs = new_access
        return tuple(emitted)

    def compute_access(self) -> tuple[tuple[str, str], ...]:
        return tuple(sorted(self._access_pairs))

    def link_states(self) -> tuple[LinkState, ...]:
        return tuple(self._links[key] for key in sorted(self._links))

    def route_flow(self, request: FlowRequest) -> Route:
        path = self._find_path(request.source_id, request.target_id)
        if not path:
            return Route(
                route_id=f"route:{request.flow_id}",
                flow_id=request.flow_id,
                path=(),
                latency=0.0,
                capacity=0.0,
                available=False,
            )

        link_path = tuple(zip(path, path[1:]))
        link_states = tuple(self._link_for_edge(source, target) for source, target in link_path)
        available = all(link.availability for link in link_states)
        capacity = min((link.capacity for link in link_states), default=0.0)
        latency = sum(link.latency for link in link_states)
        if capacity < request.demand_capacity:
            available = False

        return Route(
            route_id=f"route:{request.flow_id}",
            flow_id=request.flow_id,
            path=path,
            latency=latency,
            capacity=capacity,
            available=available,
        )

    def _access_for_slot(self, slot: int) -> tuple[tuple[str, str], ...]:
        access: list[tuple[str, str]] = []
        for profile in self._space_profiles:
            cells = self._coverage_by_slot[profile.satellite_id].get(slot, ())
            for cell_id in cells:
                for endpoint_id in self._endpoints_by_cell.get(cell_id, ()):
                    access.append((profile.satellite_id, endpoint_id))
        return tuple(sorted(access))

    def _find_path(self, source_id: str, target_id: str) -> tuple[str, ...]:
        if source_id == target_id:
            return (source_id,)
        visited = {source_id}
        queue: deque[tuple[str, tuple[str, ...]]] = deque([(source_id, (source_id,))])

        while queue:
            node_id, path = queue.popleft()
            for neighbor_id in self._neighbors(node_id):
                if neighbor_id in visited:
                    continue
                next_path = path + (neighbor_id,)
                if neighbor_id == target_id:
                    return next_path
                visited.add(neighbor_id)
                queue.append((neighbor_id, next_path))
        return ()

    def _neighbors(self, node_id: str) -> tuple[str, ...]:
        neighbors: list[str] = []
        for (source_id, target_id), link in sorted(self._links.items()):
            if not link.availability:
                continue
            if source_id == node_id:
                neighbors.append(target_id)
            elif target_id == node_id:
                neighbors.append(source_id)
        return tuple(sorted(neighbors))

    def _link_for_edge(self, source_id: str, target_id: str) -> LinkState:
        direct = self._links.get((source_id, target_id))
        if direct is not None:
            return direct
        reverse = self._links[(target_id, source_id)]
        return LinkState(
            source_id=source_id,
            target_id=target_id,
            latency=reverse.latency,
            capacity=reverse.capacity,
            availability=reverse.availability,
        )

    def _make_link(
        self,
        source_id: str,
        target_id: str,
        availability: bool,
    ) -> LinkState:
        latency, capacity = self._link_defaults[source_id]
        return LinkState(
            source_id=source_id,
            target_id=target_id,
            latency=latency,
            capacity=capacity,
            availability=availability,
        )

    def _event(
        self,
        sim_time: float,
        target: str,
        event_type: str,
        payload: object,
    ) -> SimEvent:
        self._event_sequence += 1
        return SimEvent(
            event_id=f"{self._module_name}:{self._event_sequence:08d}",
            sim_time=sim_time,
            priority=0,
            source=self._module_name,
            target=target,
            event_type=event_type,
            payload=payload,
        )

    @staticmethod
    def _build_endpoint_index(
        profiles: tuple[GroundUserProfile, ...],
    ) -> dict[str, tuple[str, ...]]:
        working: dict[str, list[str]] = {}
        for profile in profiles:
            working.setdefault(profile.cell_id, []).append(profile.user_id)
        return {
            cell_id: tuple(sorted(endpoint_ids))
            for cell_id, endpoint_ids in sorted(working.items())
        }

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
