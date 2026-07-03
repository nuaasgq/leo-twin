"""Replay and state reconstruction for integration demo event logs."""

from __future__ import annotations

from dataclasses import dataclass

from leo_twin.schema import (
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
        elif event_type == EventType.METRIC_SAMPLE.value:
            metric = _payload(event, MetricRecord)
            self._metrics[(metric.metric_name, metric.entity_id)] = metric

        if self._event_count % self._snapshot_interval_events == 0:
            self._timeline.append(self.snapshot())

    def snapshot(self) -> dict[str, JsonValue]:
        return {
            "satellites": [
                {
                    "satellite_id": state.satellite_id,
                    "sim_time": state.sim_time,
                    "position": list(state.position),
                    "velocity": list(state.velocity),
                    "status": state.status,
                }
                for state in (self._satellites[key] for key in sorted(self._satellites))
            ],
            "ground_users": [
                {
                    "user_id": user.user_id,
                    "cell_id": user.cell_id,
                    "position": list(user.position),
                    "status": user.status,
                }
                for user in self._ground_users
            ],
            "links": [
                {
                    "source_id": link.source_id,
                    "target_id": link.target_id,
                    "latency": link.latency,
                    "capacity": link.capacity,
                    "availability": link.availability,
                }
                for link in (self._links[key] for key in sorted(self._links))
            ],
            "routes": [
                {
                    "route_id": route.route_id,
                    "flow_id": route.flow_id,
                    "path": list(route.path),
                    "latency": route.latency,
                    "capacity": route.capacity,
                    "available": route.available,
                }
                for route in (self._routes[key] for key in sorted(self._routes))
            ],
            "tasks": [
                {
                    "task_id": task.task_id,
                    "node_id": task.node_id,
                    "sim_time": task.sim_time,
                    "progress": task.progress,
                    "status": task.status,
                }
                for task in (self._tasks[key] for key in sorted(self._tasks))
            ],
            "metrics": [
                {
                    "metric_name": metric.metric_name,
                    "sim_time": metric.sim_time,
                    "entity_id": metric.entity_id,
                    "value": metric.value,
                    "tags": [list(tag) for tag in metric.tags],
                }
                for metric in (
                    self._metrics[key]
                    for key in sorted(self._metrics)
                )
            ],
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


def _payload(event: SimEvent, expected_type: type[object]) -> object:
    if isinstance(event.payload, expected_type):
        return event.payload
    raise TypeError(
        f"{event.event_type} payload must be {expected_type.__name__} for replay"
    )
