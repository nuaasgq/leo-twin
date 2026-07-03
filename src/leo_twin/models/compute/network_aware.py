"""Network-aware deterministic compute scheduling module."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from leo_twin.core import SimulationKernel, SimulationModule
from leo_twin.models.compute.contracts import COMPUTE_NODE_UPDATE, ComputeNode
from leo_twin.models.compute.scheduling import (
    ComputeSchedulingRuntime,
    ComputeWorkloadItem,
)
from leo_twin.schema import (
    ComputeNodeState,
    EventType,
    Route,
    SimEvent,
    TaskRequest,
    TaskState,
)


_COMPUTE_SCHEDULE_TICK = "_COMPUTE_SCHEDULE_TICK"
_SCHEDULE_TICK_PRIORITY = -1000


@dataclass(frozen=True)
class TaskPlacementDecision:
    """Deterministic compute placement decision with network transfer context."""

    task_id: str
    node_id: str
    route_id: str
    ready_time: float
    start_time: float
    finish_time: float
    transfer_time: float
    compute_time: float
    status: str


@dataclass(frozen=True)
class _ScheduledTask:
    task: TaskRequest
    decision: TaskPlacementDecision


@dataclass(frozen=True)
class _TransferringTask:
    task: TaskRequest
    route: Route
    ready_time: float


class RouteAwareComputeEngine(SimulationModule):
    """Schedule compute tasks only after a matching route is available."""

    def __init__(
        self,
        nodes: Iterable[ComputeNode],
        module_name: str = "compute",
        metrics_target: str = "metrics",
        scheduling_runtime: ComputeSchedulingRuntime | None = None,
        state_update_targets: Iterable[str] = (),
    ) -> None:
        if not module_name:
            raise ValueError("module_name must be non-empty")
        if not metrics_target:
            raise ValueError("metrics_target must be non-empty")
        ordered_update_targets = tuple(
            sorted(str(item) for item in state_update_targets)
        )
        if any(not item for item in ordered_update_targets):
            raise ValueError("state_update_targets must contain non-empty ids")
        ordered_nodes = tuple(sorted(nodes, key=lambda item: item.node_id))
        if not ordered_nodes:
            raise ValueError("at least one compute node is required")
        if len({item.node_id for item in ordered_nodes}) != len(ordered_nodes):
            raise ValueError("compute node ids must be unique")

        self._module_name = module_name
        self._metrics_target = metrics_target
        self._state_update_targets = tuple(
            target
            for target in dict.fromkeys(ordered_update_targets)
            if target != metrics_target
        )
        self._nodes = ordered_nodes
        self._scheduling_runtime = scheduling_runtime or ComputeSchedulingRuntime()
        self._available_at = {item.node_id: 0.0 for item in ordered_nodes}
        self._pending_tasks: dict[str, TaskRequest] = {}
        self._transferring_tasks: dict[str, _TransferringTask] = {}
        self._routes_by_flow: dict[str, Route] = {}
        self._scheduled_tasks: dict[str, _ScheduledTask] = {}
        self._scheduled_tick_times: set[float] = set()
        self._event_sequence = 0

    def name(self) -> str:
        return self._module_name

    def on_event(self, event: SimEvent, kernel: SimulationKernel) -> None:
        event_type = str(event.event_type)
        if event_type == _COMPUTE_SCHEDULE_TICK:
            self._scheduled_tick_times.discard(event.sim_time)
            self._schedule_ready_tasks(event.sim_time, kernel)
            return

        if event_type == EventType.TASK_ARRIVAL.value:
            task = self._coerce_task_request(event.payload)
            self._pending_tasks[task.task_id] = task
            self._request_schedule_tick(event.sim_time, kernel)
            return

        if event_type == EventType.ROUTE_UPDATE.value:
            route = self._coerce_route(event.payload)
            self._routes_by_flow[route.flow_id] = route
            self._apply_route_update_to_transfers(route, event.sim_time, kernel)
            self._request_schedule_tick(event.sim_time, kernel)

    def pending_tasks(self) -> tuple[str, ...]:
        """Return pending task ids in deterministic order."""

        return tuple(sorted(self._pending_tasks))

    def scheduled_tasks(self) -> tuple[TaskPlacementDecision, ...]:
        """Return placement decisions in deterministic task order."""

        return tuple(
            self._scheduled_tasks[task_id].decision
            for task_id in sorted(self._scheduled_tasks)
        )

    def _request_schedule_tick(
        self,
        dispatch_time: float,
        kernel: SimulationKernel,
    ) -> None:
        if dispatch_time in self._scheduled_tick_times:
            return
        self._scheduled_tick_times.add(dispatch_time)
        self._event_sequence += 1
        kernel.schedule_event(
            SimEvent(
                event_id=f"{self._module_name}:schedule:{self._event_sequence:08d}",
                sim_time=dispatch_time,
                priority=_SCHEDULE_TICK_PRIORITY,
                source=self._module_name,
                target=self._module_name,
                event_type=_COMPUTE_SCHEDULE_TICK,
                payload=None,
            )
        )

    def _schedule_ready_tasks(
        self,
        dispatch_time: float,
        kernel: SimulationKernel,
    ) -> None:
        ready_workloads: list[ComputeWorkloadItem] = []
        ready_routes: dict[str, Route] = {}

        for task_id in sorted(self._transferring_tasks):
            transfer = self._transferring_tasks[task_id]
            if transfer.ready_time > dispatch_time:
                continue
            route = self._routes_by_flow.get(task_id)
            if route is None or not route.available or route.capacity <= 0:
                self._pending_tasks[task_id] = transfer.task
                self._transferring_tasks.pop(task_id, None)
                continue
            ready_workloads.append(
                ComputeWorkloadItem(task=transfer.task, ready_time=transfer.ready_time)
            )
            ready_routes[task_id] = route

        for task_id in sorted(self._pending_tasks):
            if task_id in self._scheduled_tasks:
                continue
            task = self._pending_tasks[task_id]
            route = self._routes_by_flow.get(task_id)
            if route is None or not route.available or route.capacity <= 0:
                continue
            ready_time = self._ready_time(task, route, dispatch_time)
            if ready_time > dispatch_time:
                self._transferring_tasks[task_id] = _TransferringTask(
                    task=task,
                    route=route,
                    ready_time=ready_time,
                )
                self._pending_tasks.pop(task_id, None)
                self._request_schedule_tick(ready_time, kernel)
                continue
            ready_workloads.append(ComputeWorkloadItem(task=task, ready_time=ready_time))
            ready_routes[task_id] = route

        for item in self._scheduling_runtime.order_workloads(tuple(ready_workloads)):
            route = ready_routes[item.task.task_id]
            decision = self._build_decision(item.task, route, item.ready_time)
            self._scheduled_tasks[item.task.task_id] = _ScheduledTask(
                task=item.task,
                decision=decision,
            )
            self._pending_tasks.pop(item.task.task_id, None)
            self._transferring_tasks.pop(item.task.task_id, None)
            self._available_at[decision.node_id] = decision.finish_time
            self._emit_task_lifecycle(item.task, decision, kernel)

    def _apply_route_update_to_transfers(
        self,
        route: Route,
        dispatch_time: float,
        kernel: SimulationKernel,
    ) -> None:
        transfer = self._transferring_tasks.get(route.flow_id)
        if transfer is None:
            return
        if not route.available or route.capacity <= 0:
            self._pending_tasks[route.flow_id] = transfer.task
            self._transferring_tasks.pop(route.flow_id, None)
            return
        if transfer.route == route:
            return
        ready_time = self._ready_time(transfer.task, route, dispatch_time)
        self._transferring_tasks[route.flow_id] = _TransferringTask(
            task=transfer.task,
            route=route,
            ready_time=ready_time,
        )
        self._request_schedule_tick(ready_time, kernel)

    def _ready_time(
        self,
        task: TaskRequest,
        route: Route,
        dispatch_time: float,
    ) -> float:
        return max(dispatch_time, task.submit_time) + _transfer_time(task, route)

    def _build_decision(
        self,
        task: TaskRequest,
        route: Route,
        ready_time: float,
    ) -> TaskPlacementDecision:
        node, start_time, finish_time, compute_time = self._select_node(
            task,
            route,
            ready_time,
        )
        return TaskPlacementDecision(
            task_id=task.task_id,
            node_id=node.node_id,
            route_id=route.route_id,
            ready_time=ready_time,
            start_time=start_time,
            finish_time=finish_time,
            transfer_time=_transfer_time(task, route),
            compute_time=compute_time,
            status=_decision_status(task, finish_time),
        )

    def _select_node(
        self,
        task: TaskRequest,
        route: Route,
        ready_time: float,
    ) -> tuple[ComputeNode, float, float, float]:
        candidates = self._candidate_nodes(route)
        scored: list[tuple[float, float, str, ComputeNode, float]] = []
        for compute_node in candidates:
            start_time = max(self._available_at[compute_node.node_id], ready_time)
            compute_time = task.compute_demand / compute_node.capacity
            finish_time = start_time + compute_time
            scored.append(
                (finish_time, start_time, compute_node.node_id, compute_node, compute_time)
            )
        finish_time, start_time, _, node, compute_time = min(scored)
        return node, start_time, finish_time, compute_time

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
        for target in self._state_update_targets:
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
                    target=target,
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
                    status=_finish_status(decision),
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
        for target in self._state_update_targets:
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
                    target=target,
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
        target: str | None = None,
    ) -> SimEvent:
        self._event_sequence += 1
        return SimEvent(
            event_id=f"{self._module_name}:route-aware:{self._event_sequence:08d}",
            sim_time=dispatch_time,
            priority=0,
            source=self._module_name,
            target=target or self._metrics_target,
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


def _decision_status(task: TaskRequest, finish_time: float) -> str:
    if task.deadline is not None and finish_time > task.deadline:
        return "DEADLINE_MISSED"
    return "SCHEDULED"


def _transfer_time(task: TaskRequest, route: Route) -> float:
    return route.latency + task.data_size / route.capacity


def _finish_status(decision: TaskPlacementDecision) -> str:
    if decision.status == "DEADLINE_MISSED":
        return "DEADLINE_MISSED"
    return "FINISHED"
