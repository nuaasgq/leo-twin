"""Deterministic flow-level network module."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from heapq import heappop, heappush
from math import isfinite
from typing import Any

from leo_twin.core import SimulationKernel, SimulationModule
from leo_twin.schema import (
    AccessAssociation,
    CoverageSlot,
    EventType,
    FlowRequest,
    GroundUserProfile,
    LinkState,
    OrbitBatchState,
    Route,
    SatelliteProfile,
    SatelliteState,
    SimEvent,
)


_INACTIVE_STATUSES = frozenset({"disabled", "down", "failed", "inactive", "offline"})


@dataclass(frozen=True)
class _CoverageProfile:
    satellite_id: str
    coverage_by_slot: dict[int, tuple[str, ...]]
    link_latency: float
    link_capacity: float


class NetworkEngine(SimulationModule):
    """Maintain coverage access links and emit flow-level route decisions.

    The topology is a deterministic time-varying bipartite graph between
    configured satellites and ground users. Coverage lookup is indexed by
    coverage cell, so topology updates visit only covered cells and their users.
    """

    def __init__(
        self,
        satellites: Iterable[SatelliteProfile],
        ground_users: Iterable[GroundUserProfile],
        module_name: str = "network",
        slot_duration: float = 1.0,
        metrics_target: str = "metrics",
        route_targets: Iterable[str] = ("compute", "metrics"),
    ) -> None:
        if not isinstance(module_name, str) or not module_name:
            raise TypeError("module_name must be a non-empty str")
        if (
            isinstance(slot_duration, bool)
            or not isinstance(slot_duration, (int, float))
            or not isfinite(slot_duration)
            or slot_duration <= 0
        ):
            raise ValueError("slot_duration must be a finite positive number")
        if not isinstance(metrics_target, str) or not metrics_target:
            raise TypeError("metrics_target must be a non-empty str")

        self._module_name = module_name
        self._slot_duration = float(slot_duration)
        self._metrics_target = metrics_target
        route_target_values = tuple(route_targets)
        if any(
            not isinstance(target, str) or not target for target in route_target_values
        ):
            raise TypeError("route_targets must contain non-empty strings")
        self._route_targets = tuple(sorted(dict.fromkeys(route_target_values)))

        satellite_profiles = tuple(sorted(satellites, key=lambda item: item.satellite_id))
        ground_profiles = tuple(sorted(ground_users, key=lambda item: item.user_id))
        self._coverage_profiles = tuple(
            _CoverageProfile(
                satellite_id=profile.satellite_id,
                coverage_by_slot=self._coverage_by_slot(profile.coverage),
                link_latency=profile.link_latency,
                link_capacity=profile.link_capacity,
            )
            for profile in satellite_profiles
        )
        self._profile_by_satellite = {
            profile.satellite_id: profile for profile in self._coverage_profiles
        }
        self._users_by_cell = self._index_ground_users(ground_profiles)

        self._satellite_states: dict[str, SatelliteState] = {}
        self._current_slot: int | None = None
        self._access_pairs: frozenset[tuple[str, str]] = frozenset()
        self._active_links: dict[tuple[str, str], LinkState] = {}
        self._last_link_states: dict[tuple[str, str], LinkState] = {}
        self._adjacency: dict[str, tuple[tuple[str, LinkState], ...]] = {}
        self._event_sequence = 0

    def name(self) -> str:
        return self._module_name

    def on_event(self, event: SimEvent, kernel: SimulationKernel) -> None:
        if event.event_type == EventType.ORBIT_UPDATE:
            state = self._coerce_satellite_state(event.payload)
            self._satellite_states[state.satellite_id] = state
            for emitted in self.update_topology(event.sim_time):
                kernel.schedule_event(emitted)
            return

        if event.event_type == EventType.ORBIT_BATCH_UPDATE:
            batch = self._coerce_orbit_batch(event.payload)
            for state in batch.satellite_states:
                self._satellite_states[state.satellite_id] = state
            for emitted in self.update_topology(event.sim_time):
                kernel.schedule_event(emitted)
            return

        if event.event_type == EventType.FLOW_ARRIVAL:
            request = self._coerce_flow_request(event.payload)
            route = self.route_flow(request)
            for target in self._route_targets:
                kernel.schedule_event(
                    self._event(
                        sim_time=event.sim_time,
                        target=target,
                        event_type=EventType.ROUTE_UPDATE,
                        payload=route,
                    )
                )

    def update_topology(self, sim_time: float) -> tuple[SimEvent, ...]:
        """Update the active access graph for ``sim_time`` and return events."""

        slot = self._slot_for_time(sim_time)
        self._current_slot = slot

        next_access = frozenset(self._access_for_slot(slot))
        ended = tuple(sorted(self._access_pairs - next_access))
        started = tuple(sorted(next_access - self._access_pairs))

        emitted: list[SimEvent] = []
        for satellite_id, user_id in ended:
            key = (satellite_id, user_id)
            self._active_links.pop(key, None)
            link = self._make_link(satellite_id, user_id, availability=False)
            self._last_link_states[key] = link
            emitted.extend(
                self._link_events(sim_time, EventType.ACCESS_END, link)
            )

        for satellite_id, user_id in started:
            key = (satellite_id, user_id)
            link = self._make_link(satellite_id, user_id, availability=True)
            self._active_links[key] = link
            self._last_link_states[key] = link
            emitted.extend(
                self._link_events(sim_time, EventType.ACCESS_START, link)
            )

        self._access_pairs = next_access
        if ended or started:
            self._rebuild_adjacency()
        return tuple(emitted)

    def compute_access(self) -> tuple[AccessAssociation, ...]:
        return tuple(
            AccessAssociation(satellite_id=satellite_id, user_id=user_id)
            for satellite_id, user_id in sorted(self._access_pairs)
        )

    def link_states(self) -> tuple[LinkState, ...]:
        """Return the latest emitted link state for each known access pair."""

        return tuple(self._last_link_states[key] for key in sorted(self._last_link_states))

    def active_link_states(self) -> tuple[LinkState, ...]:
        """Return currently available link states."""

        return tuple(self._active_links[key] for key in sorted(self._active_links))

    def route_flow(self, request: FlowRequest) -> Route:
        """Compute a deterministic flow-level route over active links."""

        if request.source_id == request.target_id:
            return Route(
                route_id=f"route:{request.flow_id}",
                flow_id=request.flow_id,
                path=(request.source_id,),
                latency=0.0,
                capacity=0.0,
                available=request.demand_capacity <= 0,
            )

        path = self._shortest_path(
            request.source_id,
            request.target_id,
            minimum_capacity=request.demand_capacity,
        )
        available = bool(path)
        if not path:
            path = self._shortest_path(
                request.source_id,
                request.target_id,
                minimum_capacity=0.0,
            )

        if not path:
            return Route(
                route_id=f"route:{request.flow_id}",
                flow_id=request.flow_id,
                path=(),
                latency=0.0,
                capacity=0.0,
                available=False,
            )

        latency, capacity = self._path_metrics(path)
        return Route(
            route_id=f"route:{request.flow_id}",
            flow_id=request.flow_id,
            path=path,
            latency=latency,
            capacity=capacity,
            available=available and capacity >= request.demand_capacity,
        )

    def _access_for_slot(self, slot: int) -> tuple[tuple[str, str], ...]:
        access: list[tuple[str, str]] = []
        for profile in self._coverage_profiles:
            if not self._satellite_is_available(profile.satellite_id):
                continue
            for cell_id in profile.coverage_by_slot.get(slot, ()):
                for user_id in self._users_by_cell.get(cell_id, ()):
                    access.append((profile.satellite_id, user_id))
        return tuple(sorted(access))

    def _satellite_is_available(self, satellite_id: str) -> bool:
        state = self._satellite_states.get(satellite_id)
        if state is None:
            return True
        return state.status.strip().lower() not in _INACTIVE_STATUSES

    def _make_link(
        self,
        satellite_id: str,
        user_id: str,
        availability: bool,
    ) -> LinkState:
        profile = self._profile_by_satellite[satellite_id]
        return LinkState(
            source_id=satellite_id,
            target_id=user_id,
            latency=profile.link_latency,
            capacity=profile.link_capacity,
            availability=availability,
        )

    def _link_events(
        self,
        sim_time: float,
        access_event_type: EventType,
        link: LinkState,
    ) -> tuple[SimEvent, SimEvent]:
        return (
            self._event(
                sim_time=sim_time,
                target=self._metrics_target,
                event_type=access_event_type,
                payload=link,
            ),
            self._event(
                sim_time=sim_time,
                target=self._metrics_target,
                event_type=EventType.LINK_UPDATE,
                payload=link,
            ),
        )

    def _rebuild_adjacency(self) -> None:
        working: dict[str, list[tuple[str, LinkState]]] = {}
        active_items = sorted(self._active_links.items())
        for (left_id, right_id), state in active_items:
            working.setdefault(left_id, []).append((right_id, state))
            working.setdefault(right_id, []).append((left_id, state))
        self._adjacency = {
            endpoint_id: tuple(sorted(entries, key=lambda item: item[0]))
            for endpoint_id, entries in sorted(working.items())
        }

    def _shortest_path(
        self,
        source_id: str,
        target_id: str,
        minimum_capacity: float,
    ) -> tuple[str, ...]:
        queue: list[tuple[float, tuple[str, ...], str]] = [(0.0, (source_id,), source_id)]
        best: dict[str, tuple[float, tuple[str, ...]]] = {
            source_id: (0.0, (source_id,))
        }

        while queue:
            latency, path, node_id = heappop(queue)
            if best.get(node_id) != (latency, path):
                continue
            if node_id == target_id:
                return path

            for neighbor_id, link in self._adjacency.get(node_id, ()):
                if not link.availability or link.capacity < minimum_capacity:
                    continue
                candidate_latency = latency + link.latency
                candidate_path = path + (neighbor_id,)
                current_best = best.get(neighbor_id)
                candidate_best = (candidate_latency, candidate_path)
                if current_best is None or candidate_best < current_best:
                    best[neighbor_id] = candidate_best
                    heappush(queue, (candidate_latency, candidate_path, neighbor_id))

        return ()

    def _path_metrics(self, path: tuple[str, ...]) -> tuple[float, float]:
        latency = 0.0
        capacity: float | None = None
        for source_id, target_id in zip(path, path[1:]):
            link = self._link_for_edge(source_id, target_id)
            latency += link.latency
            capacity = link.capacity if capacity is None else min(capacity, link.capacity)
        return latency, 0.0 if capacity is None else capacity

    def _link_for_edge(self, source_id: str, target_id: str) -> LinkState:
        direct = self._active_links.get((source_id, target_id))
        if direct is not None:
            return direct
        reverse = self._active_links.get((target_id, source_id))
        if reverse is not None:
            return reverse
        raise KeyError(f"active link not found: {source_id!r} -> {target_id!r}")

    def _event(
        self,
        sim_time: float,
        target: str,
        event_type: EventType,
        payload: object,
    ) -> SimEvent:
        self._event_sequence += 1
        return SimEvent(
            event_id=f"{self._module_name}:{self._event_sequence:08d}",
            sim_time=sim_time,
            priority=0,
            source=self._module_name,
            target=target,
            event_type=event_type.value,
            payload=payload,
        )

    def _slot_for_time(self, sim_time: float) -> int:
        if isinstance(sim_time, bool) or not isinstance(sim_time, (int, float)):
            raise TypeError("sim_time must be an int or float")
        if not isfinite(sim_time):
            raise ValueError("sim_time must be finite")
        return int(sim_time // self._slot_duration)

    @staticmethod
    def _coverage_by_slot(slots: tuple[CoverageSlot, ...]) -> dict[int, tuple[str, ...]]:
        working: dict[int, list[str]] = {}
        for slot in slots:
            working.setdefault(slot.slot, []).extend(slot.cell_ids)
        return {
            slot: tuple(sorted(dict.fromkeys(cell_ids)))
            for slot, cell_ids in sorted(working.items())
        }

    @staticmethod
    def _index_ground_users(
        profiles: tuple[GroundUserProfile, ...],
    ) -> dict[str, tuple[str, ...]]:
        working: dict[str, list[str]] = {}
        for profile in profiles:
            working.setdefault(profile.cell_id, []).append(profile.user_id)
        return {
            cell_id: tuple(sorted(user_ids))
            for cell_id, user_ids in sorted(working.items())
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

    @staticmethod
    def _coerce_satellite_state(payload: object) -> SatelliteState:
        if isinstance(payload, SatelliteState):
            return payload
        if isinstance(payload, dict):
            return SatelliteState(
                satellite_id=str(payload["satellite_id"]),
                sim_time=float(payload["sim_time"]),
                position=NetworkEngine._vector3(payload["position"]),
                velocity=NetworkEngine._vector3(payload["velocity"]),
                status=str(payload["status"]),
            )
        raise TypeError("ORBIT_UPDATE payload must be SatelliteState or dict")

    @staticmethod
    def _coerce_orbit_batch(payload: object) -> OrbitBatchState:
        if isinstance(payload, OrbitBatchState):
            return payload
        if isinstance(payload, dict):
            raw_states = payload.get("satellite_states", payload.get("satellites"))
            if not isinstance(raw_states, (tuple, list)):
                raise TypeError("ORBIT_BATCH_UPDATE satellite_states must be a list or tuple")
            states = tuple(NetworkEngine._coerce_satellite_state(item) for item in raw_states)
            partition_id = payload.get("partition_id")
            return OrbitBatchState(
                sim_time=float(payload["sim_time"]),
                satellite_states=states,
                satellite_count=int(payload.get("satellite_count", len(states))),
                partition_id=None if partition_id is None else str(partition_id),
            )
        raise TypeError("ORBIT_BATCH_UPDATE payload must be OrbitBatchState or dict")

    @staticmethod
    def _vector3(value: Any) -> tuple[float, float, float]:
        if not isinstance(value, (list, tuple)) or len(value) != 3:
            raise TypeError("vector payload fields must have exactly three values")
        return (float(value[0]), float(value[1]), float(value[2]))
