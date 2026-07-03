"""Replay and state reconstruction for integration demo event logs."""

from __future__ import annotations

from dataclasses import dataclass

from leo_twin.schema import (
    ComputeNodeState,
    EventType,
    LinkState,
    MetricRecord,
    Route,
    SatelliteState,
    SimEvent,
    TaskState,
)

from examples.integration_demo.scenario import GroundUserRenderState
from examples.integration_demo.serialization import JsonValue, event_to_json, stable_json


@dataclass(frozen=True)
class ReplayResult:
    final_snapshot: dict[str, JsonValue]
    timeline: tuple[dict[str, JsonValue], ...]
    replay_signature: str


class DemoStateProjector:
    """Reconstruct frontend state strictly from observed SimEvent records."""

    def __init__(
        self,
        ground_users: tuple[GroundUserRenderState, ...],
        snapshot_interval_events: int,
    ) -> None:
        self._ground_users = tuple(sorted(ground_users, key=lambda user: user.user_id))
        self._snapshot_interval_events = snapshot_interval_events
        self._satellites: dict[str, SatelliteState] = {}
        self._links: dict[tuple[str, str], LinkState] = {}
        self._routes: dict[str, Route] = {}
        self._tasks: dict[str, TaskState] = {}
        self._compute_nodes: dict[str, ComputeNodeState] = {}
        self._metrics: dict[tuple[str, str], MetricRecord] = {}
        self._event_count = 0
        self._last_sim_time = 0.0
        self._timeline: list[dict[str, JsonValue]] = []

    def apply(self, event: SimEvent) -> None:
        self._event_count += 1
        self._last_sim_time = max(self._last_sim_time, event.sim_time)
        event_type = str(event.event_type)
        if event_type == EventType.ORBIT_UPDATE.value:
            state = _payload(event, SatelliteState)
            self._satellites[state.satellite_id] = state
        elif event_type in {
            EventType.ACCESS_START.value,
            EventType.ACCESS_END.value,
            EventType.LINK_UPDATE.value,
        }:
            link = _payload(event, LinkState)
            key = (link.source_id, link.target_id)
            if link.availability:
                self._links[key] = link
            else:
                self._links.pop(key, None)
        elif event_type == EventType.ROUTE_UPDATE.value:
            route = _payload(event, Route)
            self._routes[route.route_id] = route
        elif event_type in {EventType.TASK_START.value, EventType.TASK_FINISH.value}:
            task = _payload(event, TaskState)
            self._tasks[task.task_id] = task
        elif event_type == "COMPUTE_NODE_UPDATE":
            node = _payload(event, ComputeNodeState)
            self._compute_nodes[node.node_id] = node
        elif event_type == EventType.METRIC_SAMPLE.value:
            metric = _payload(event, MetricRecord)
            self._metrics[(metric.metric_name, metric.entity_id)] = metric

        if self._event_count % self._snapshot_interval_events == 0:
            self._timeline.append(self.snapshot())

    def snapshot(self) -> dict[str, JsonValue]:
        return {
            "satellites": _satellite_rows(self._satellites),
            "ground_users": _ground_user_rows(self._ground_users),
            "links": _link_rows(self._links),
            "routes": _route_rows(self._routes),
            "tasks": _task_rows(self._tasks),
            "compute_nodes": _compute_node_rows(self._compute_nodes),
            "metrics": _metric_rows(self._metrics),
            "event_count": self._event_count,
            "last_sim_time": self._last_sim_time,
        }

    def timeline(self) -> tuple[dict[str, JsonValue], ...]:
        if not self._timeline or self._timeline[-1] != self.snapshot():
            self._timeline.append(self.snapshot())
        return tuple(self._timeline)


def replay_events(
    events: tuple[SimEvent, ...],
    ground_users: tuple[GroundUserRenderState, ...],
    snapshot_interval_events: int,
) -> ReplayResult:
    projector = DemoStateProjector(ground_users, snapshot_interval_events)
    signature_parts: list[str] = []
    for event in events:
        projector.apply(event)
        signature_parts.append(stable_json(event_to_json(event)))
    final_snapshot = projector.snapshot()
    return ReplayResult(
        final_snapshot=final_snapshot,
        timeline=projector.timeline(),
        replay_signature="\n".join(signature_parts),
    )


def _compute_load_ratio(node: ComputeNodeState) -> float:
    if node.capacity <= 0.0:
        return 1.0
    load = 1.0 - node.available_capacity / node.capacity
    return max(0.0, min(1.0, load))


def _satellite_rows(states: dict[str, SatelliteState]) -> list[JsonValue]:
    return [_satellite_row(states[key]) for key in sorted(states)]


def _satellite_row(state: SatelliteState) -> dict[str, JsonValue]:
    return {
        "satellite_id": state.satellite_id,
        "sim_time": state.sim_time,
        "position": list(state.position),
        "velocity": list(state.velocity),
        "status": state.status,
    }


def _ground_user_rows(users: tuple[GroundUserRenderState, ...]) -> list[JsonValue]:
    return [_ground_user_row(user) for user in users]


def _ground_user_row(user: GroundUserRenderState) -> dict[str, JsonValue]:
    return {
        "user_id": user.user_id,
        "cell_id": user.cell_id,
        "position": list(user.position),
        "status": user.status,
    }


def _link_rows(links: dict[tuple[str, str], LinkState]) -> list[JsonValue]:
    return [_link_row(links[key]) for key in sorted(links)]


def _link_row(link: LinkState) -> dict[str, JsonValue]:
    return {
        "source_id": link.source_id,
        "target_id": link.target_id,
        "latency": link.latency,
        "capacity": link.capacity,
        "availability": link.availability,
    }


def _route_rows(routes: dict[str, Route]) -> list[JsonValue]:
    return [_route_row(routes[key]) for key in sorted(routes)]


def _route_row(route: Route) -> dict[str, JsonValue]:
    return {
        "route_id": route.route_id,
        "flow_id": route.flow_id,
        "path": list(route.path),
        "latency": route.latency,
        "capacity": route.capacity,
        "available": route.available,
    }


def _task_rows(tasks: dict[str, TaskState]) -> list[JsonValue]:
    return [_task_row(tasks[key]) for key in sorted(tasks)]


def _task_row(task: TaskState) -> dict[str, JsonValue]:
    return {
        "task_id": task.task_id,
        "node_id": task.node_id,
        "sim_time": task.sim_time,
        "progress": task.progress,
        "status": task.status,
    }


def _compute_node_rows(nodes: dict[str, ComputeNodeState]) -> list[JsonValue]:
    return [_compute_node_row(nodes[key]) for key in sorted(nodes)]


def _compute_node_row(node: ComputeNodeState) -> dict[str, JsonValue]:
    return {
        "node_id": node.node_id,
        "sim_time": node.sim_time,
        "capacity": node.capacity,
        "available_capacity": node.available_capacity,
        "status": node.status,
        "load_ratio": _compute_load_ratio(node),
    }


def _metric_rows(metrics: dict[tuple[str, str], MetricRecord]) -> list[JsonValue]:
    return [_metric_row(metrics[key]) for key in sorted(metrics)]


def _metric_row(metric: MetricRecord) -> dict[str, JsonValue]:
    return {
        "metric_name": metric.metric_name,
        "sim_time": metric.sim_time,
        "entity_id": metric.entity_id,
        "value": metric.value,
        "tags": [list(tag) for tag in metric.tags],
    }


def _payload(event: SimEvent, expected_type: type[object]) -> object:
    if isinstance(event.payload, expected_type):
        return event.payload
    raise TypeError(
        f"{event.event_type} payload must be {expected_type.__name__} for replay"
    )
