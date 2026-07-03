"""Network-aware deterministic compute scheduling module."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from leo_twin.core import SimulationKernel, SimulationModule
from leo_twin.models.compute.contracts import COMPUTE_NODE_UPDATE, ComputeNode
from leo_twin.schema import (
    ComputeNodeState,
    EventType,
    Route,
    SimEvent,
    TaskRequest,
    TaskState,
)


@dataclass(frozen=True)
class TaskPlacementDecision:
    """Deterministic compute placement decision with network transfer context."""

    task_id: str
    node_id: str
    route_id: str
    ready_time: float
    start_time: float
    finish_time: float
    status: str


@dataclass(frozen=True)
class _ScheduledTask:
    task: TaskRequest
    decision: TaskPlacementDecision


class RouteAwareComputeEngine(SimulationModule):
    """Schedule compute tasks only after a matching route is available."""

    def __init__(
        self,
        nodes: Iterable[ComputeNode],
        module_name: str = "compute",
        metrics_target: str = "metrics",
    ) -> None:
        if not module_name:
            raise ValueError("module_name must be non-empty")
        if not metrics_target:
            raise ValueError("metrics_target must be non-empty")
        ordered_nodes = tuple(sorted(nodes, key=lambda item: item.node_id))
        if not ordered_nodes:
            raise ValueError("at least one compute node is required")
        if len({item.node_id for item in ordered_nodes}) != len(ordered_nodes):
            raise ValueError("compute node ids must be unique")

        self._module_name = module_name
        self._metrics_target = metrics_target
        self._nodes = ordered_nodes
        self._available_at = {item.node_id: 0.0 for item in ordered_nodes}
        self._pending_tasks: dict[str, TaskRequest] = {}
        self._routes_by_flow: dict[str, Route] = {}
        self._scheduled_tasks: dict[str, _ScheduledTask] = {}
        self._event_sequence = 0

    def name(self) -> str:
        return self._module_name

    def on_event(self, event: SimEvent, kernel: SimulationKernel) -> None:
        if event.event_type == EventType.TASK_ARRIVAL:
            task = self._coerce_task_request(event.payload)
            self._pending_tasks[task.task_id] = task
            self._try_schedule(task.task_id, event.sim_time, kernel)
            return

        if event.event_type == EventType.ROUTE_UPDATE:
            route = self._coerce_route(event.payload)
            self._routes_by_flow[route.flow_id] = route
            self._try_schedule(route.flow_id, event.sim_time, kernel)

    def pending_tasks(self) -> tuple[str, ...]:
        """Return pending task ids in deterministic order."""

        return tuple(sorted(self._pending_tasks))

    def scheduled_tasks(self) -> tuple[TaskPlacementDecision, ...]:
        """Return placement decisions in deterministic task order."""

        return tuple(
            self._scheduled_tasks[task_id].decision
            for task_id in sorted(self._scheduled_tasks)
        )

    def _try_schedule(
        self,
        task_id: str,
        dispatch_time: float,
        kernel: SimulationKernel,
    ) -> None:
        if task_id in self._scheduled_tasks:
            return
        task = self._pending_tasks.get(task_id)
        route = self._routes_by_flow.get(task_id)
        if task is None or route is None or not route.available or route.capacity <= 0:
            return

        decision = self._build_decision(task, route, dispatch_time)
        self._scheduled_tasks[task.task_id] = _ScheduledTask(task=task, decision=decision)
        self._pending_tasks.pop(task.task_id, None)
        self._available_at[decision.node_id] = decision.finish_time
        self._emit_task_lifecycle(task, decision, kernel)

    def _build_decision(
        self,
        task: TaskRequest,
        route: Route,
        dispatch_time: float,
    ) -> TaskPlacementDecision:
        transfer_time = route.latency + task.data_size / route.capacity
        ready_time = max(dispatch_time, task.submit_time) + transfer_time
        node, start_time, finish_time = self._select_node(task, route, ready_time)
        return TaskPlacementDecision(
            task_id=task.task_id,
            node_id=node.node_id,
            route_id=route.route_id,
            ready_time=ready_time,
            start_time=start_time,
            finish_time=finish_time,
            status="SCHEDULED",
        )

    def _select_node(
        self,
        task: TaskRequest,
        route: Route,
        ready_time: float,
    ) -> tuple[ComputeNode, float, float]:
        candidates = self._candidate_nodes(route)
        scored: list[tuple[float, float, str, ComputeNode]] = []
        for compute_node in candidates:
            start_time = max(self._available_at[compute_node.node_id], ready_time)
            finish_time = start_time + task.compute_demand / compute_node.capacity
            scored.append((finish_time, start_time, compute_node.node_id, compute_node))
        finish_time, start_time, _, node = min(scored)
        return node, start_time, finish_time

    def _candidate_nodes(self, route: Route) -> tuple[ComputeNode, ...]:
        routed_node_ids = set(route.path)
        candidates = tuple(item for item in self._nodes if item.node_id in routed_node_ids)
        return candidates if candidates else self._nodes

    def _emit_task_lifecycle(
        self,
        task: TaskRequest,
        decision: TaskPlacementDecision,
        kernel: SimulationKernel,
    ) -> None:
        node = self._node_by_id(decision.node_id)
        kernel.schedule_event(
            self._event(
                dispatch_time=decision.start_time,
                event_type=EventType.TASK_START.value,
                payload=TaskState(
                    task_id=task.task_id,
                    node_id=decision.node_id,
                    sim_time=decision.start_time,
                    progress=0.0,
                    status="RUNNING",
                ),
            )
        )
        kernel.schedule_event(
            self._event(
                dispatch_time=decision.start_time,
                event_type=COMPUTE_NODE_UPDATE,
                payload=ComputeNodeState(
                    node_id=decision.node_id,
                    sim_time=decision.start_time,
                    capacity=node.capacity,
                    available_capacity=0.0,
                    status="BUSY",
                ),
            )
        )
        kernel.schedule_event(
            self._event(
                dispatch_time=decision.finish_time,
                event_type=EventType.TASK_FINISH.value,
                payload=TaskState(
                    task_id=task.task_id,
                    node_id=decision.node_id,
                    sim_time=decision.finish_time,
                    progress=1.0,
                    status="FINISHED",
                ),
            )
        )
        kernel.schedule_event(
            self._event(
                dispatch_time=decision.finish_time,
                event_type=COMPUTE_NODE_UPDATE,
                payload=ComputeNodeState(
                    node_id=decision.node_id,
                    sim_time=decision.finish_time,
                    capacity=node.capacity,
                    available_capacity=node.capacity,
                    status="IDLE",
                ),
            )
        )

    def _node_by_id(self, node_id: str) -> ComputeNode:
        for item in self._nodes:
            if item.node_id == node_id:
                return item
        raise KeyError(node_id)

    def _event(
        self,
        dispatch_time: float,
        event_type: str,
        payload: object,
    ) -> SimEvent:
        self._event_sequence += 1
        return SimEvent(
            event_id=f"{self._module_name}:route-aware:{self._event_sequence:08d}",
            sim_time=dispatch_time,
            priority=0,
            source=self._module_name,
            target=self._metrics_target,
            event_type=event_type,
            payload=payload,
        )

    @staticmethod
    def _coerce_task_request(payload: object) -> TaskRequest:
        if isinstance(payload, TaskRequest):
            return payload
        if isinstance(payload, dict):
            deadline = payload.get("deadline")
            return TaskRequest(
                task_id=str(payload["task_id"]),
                source_id=str(payload["source_id"]),
                submit_time=float(payload["submit_time"]),
                compute_demand=float(payload["compute_demand"]),
                data_size=float(payload["data_size"]),
                deadline=None if deadline is None else float(deadline),
            )
        raise TypeError("TASK_ARRIVAL payload must be TaskRequest or dict")

    @staticmethod
    def _coerce_route(payload: object) -> Route:
        if isinstance(payload, Route):
            return payload
        if isinstance(payload, dict):
            return Route(
                route_id=str(payload["route_id"]),
                flow_id=str(payload["flow_id"]),
                path=tuple(str(item) for item in payload["path"]),
                latency=float(payload["latency"]),
                capacity=float(payload["capacity"]),
                available=bool(payload["available"]),
            )
        raise TypeError("ROUTE_UPDATE payload must be Route or dict")
