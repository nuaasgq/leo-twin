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
from leo_twin.models.compute.placement import (
    ServicePlacementCandidate,
    ServicePlacementDecision as ComputeServicePlacementDecision,
    ServicePlacementQueueState,
    place_compute_service,
)
from leo_twin.models.compute.resources import (
    compute_node_resource_usage_fields,
)
from leo_twin.models.traffic import ComputeOutputFlowMetadata
from leo_twin.schema import (
    ComputeNodeState,
    EventType,
    MetricRecord,
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
    placement_status: str = "PLACED"
    placement_policy: str = "MIN_ESTIMATED_FINISH_TIME"
    queue_delay: float = 0.0
    bottleneck_resource: str = "none"
    candidate_count: int = 0
    capable_candidate_count: int = 0
    candidate_queue_label: str = ""
    rejection_reason: str = ""


@dataclass(frozen=True)
class _ScheduledTask:
    task: TaskRequest
    decision: TaskPlacementDecision


@dataclass(frozen=True)
class _TransferringTask:
    task: TaskRequest
    route: Route
    ready_time: float


@dataclass(frozen=True)
class _OutputFlowState:
    metadata: ComputeOutputFlowMetadata
    decision: TaskPlacementDecision


class RouteAwareComputeEngine(SimulationModule):
    """Schedule compute tasks only after a matching route is available."""

    def __init__(
        self,
        nodes: Iterable[ComputeNode],
        module_name: str = "compute",
        metrics_target: str = "metrics",
        network_target: str = "network",
        scheduling_runtime: ComputeSchedulingRuntime | None = None,
        state_update_targets: Iterable[str] = (),
        output_flow_metadata: Iterable[ComputeOutputFlowMetadata] = (),
    ) -> None:
        if not module_name:
            raise ValueError("module_name must be non-empty")
        if not metrics_target:
            raise ValueError("metrics_target must be non-empty")
        if not network_target:
            raise ValueError("network_target must be non-empty")
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
        ordered_output_flows = tuple(
            sorted(output_flow_metadata, key=lambda item: (item.task_id, item.flow_id))
        )
        if any(not isinstance(item, ComputeOutputFlowMetadata) for item in ordered_output_flows):
            raise TypeError("output_flow_metadata must contain ComputeOutputFlowMetadata")
        if len({item.task_id for item in ordered_output_flows}) != len(ordered_output_flows):
            raise ValueError("output_flow_metadata task ids must be unique")
        if len({item.flow_id for item in ordered_output_flows}) != len(ordered_output_flows):
            raise ValueError("output flow ids must be unique")

        self._module_name = module_name
        self._metrics_target = metrics_target
        self._network_target = network_target
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
        self._output_flows_by_task = {
            item.task_id: item for item in ordered_output_flows
        }
        self._output_flow_to_task = {
            item.flow_id: item.task_id for item in ordered_output_flows
        }
        self._output_flow_states: dict[str, _OutputFlowState] = {}
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
            self._emit_output_route_metrics(route, event.sim_time, kernel)
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

        for transfer_key in sorted(self._transferring_tasks):
            transfer = self._transferring_tasks[transfer_key]
            task_id = transfer.task.task_id
            if transfer.ready_time > dispatch_time:
                continue
            route = self._routes_by_flow.get(_input_flow_id(transfer.task))
            if route is None or not route.available or route.capacity <= 0:
                self._pending_tasks[task_id] = transfer.task
                self._transferring_tasks.pop(transfer_key, None)
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
            route = self._routes_by_flow.get(_input_flow_id(task))
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
        transfer_key = route.flow_id
        transfer = self._transferring_tasks.get(transfer_key)
        if transfer is None:
            for key, item in self._transferring_tasks.items():
                if _input_flow_id(item.task) == route.flow_id:
                    transfer_key = key
                    transfer = item
                    break
        if transfer is None:
            return
        task_id = transfer.task.task_id
        if not route.available or route.capacity <= 0:
            self._pending_tasks[task_id] = transfer.task
            self._transferring_tasks.pop(transfer_key, None)
            self._transferring_tasks.pop(task_id, None)
            return
        if transfer.route == route:
            if transfer_key != task_id:
                self._transferring_tasks.pop(transfer_key, None)
                self._transferring_tasks[task_id] = transfer
            return
        ready_time = self._ready_time(transfer.task, route, dispatch_time)
        self._transferring_tasks.pop(transfer_key, None)
        self._transferring_tasks.pop(task_id, None)
        self._transferring_tasks[task_id] = _TransferringTask(
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
        placement = self._select_node(
            task,
            route,
            ready_time,
        )
        if (
            placement.selected_node_id is None
            or placement.start_time is None
            or placement.finish_time is None
            or placement.execution_delay is None
        ):
            raise ValueError(
                f"no capable compute node for task {task.task_id}: "
                f"{placement.rejection_reason}"
            )
        return TaskPlacementDecision(
            task_id=task.task_id,
            node_id=placement.selected_node_id,
            route_id=route.route_id,
            ready_time=ready_time,
            start_time=placement.start_time,
            finish_time=placement.finish_time,
            transfer_time=_transfer_time(task, route),
            compute_time=placement.execution_delay,
            status=_decision_status(task, placement.finish_time),
            placement_status=placement.status.value,
            placement_policy=placement.policy.value,
            queue_delay=float(placement.queue_delay or 0.0),
            bottleneck_resource=placement.bottleneck_resource or "none",
            candidate_count=placement.candidate_count,
            capable_candidate_count=placement.capable_candidate_count,
            candidate_queue_label=_placement_candidate_queue_label(
                placement.candidates
            ),
            rejection_reason=(
                "" if placement.rejection_reason is None else placement.rejection_reason.value
            ),
        )

    def _select_node(
        self,
        task: TaskRequest,
        route: Route,
        ready_time: float,
    ) -> ComputeServicePlacementDecision:
        candidates = self._candidate_nodes(route)
        queue_states = tuple(
            ServicePlacementQueueState(
                node_id=compute_node.node_id,
                available_at=self._available_at[compute_node.node_id],
            )
            for compute_node in candidates
        )
        return place_compute_service(
            task,
            candidates,
            queue_states=queue_states,
            ready_time=ready_time,
        )

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
                    flow_id=task.flow_id,
                ),
            )
        )
        kernel.schedule_event(
            self._event(
                dispatch_time=decision.start_time,
                event_type=COMPUTE_NODE_UPDATE,
                payload=_compute_node_state(
                    node,
                    decision.start_time,
                    0.0,
                    "BUSY",
                    task,
                ),
            )
        )
        for target in self._state_update_targets:
            kernel.schedule_event(
                self._event(
                    dispatch_time=decision.start_time,
                    event_type=COMPUTE_NODE_UPDATE,
                    payload=_compute_node_state(
                        node,
                        decision.start_time,
                        0.0,
                        "BUSY",
                        task,
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
                    flow_id=task.flow_id,
                ),
            )
        )
        kernel.schedule_event(
            self._event(
                dispatch_time=decision.finish_time,
                event_type=COMPUTE_NODE_UPDATE,
                payload=_compute_node_state(
                    node,
                    decision.finish_time,
                    node.capacity,
                    "IDLE",
                ),
            )
        )
        for target in self._state_update_targets:
            kernel.schedule_event(
                self._event(
                    dispatch_time=decision.finish_time,
                    event_type=COMPUTE_NODE_UPDATE,
                    payload=_compute_node_state(
                        node,
                        decision.finish_time,
                        node.capacity,
                        "IDLE",
                    ),
                    target=target,
                )
            )
        self._emit_service_component_metrics(task, decision, kernel)
        self._emit_output_flow_arrival(task, decision, kernel)

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
                flow_id=(
                    None
                    if payload.get("flow_id") is None
                    else str(payload.get("flow_id"))
                ),
                priority=int(payload.get("priority", 0)),
                cpu_ops=float(payload.get("cpu_ops", 0.0)),
                fp32_ops=float(payload.get("fp32_ops", 0.0)),
                fp16_ops=float(payload.get("fp16_ops", 0.0)),
                int8_ops=float(payload.get("int8_ops", 0.0)),
                memory_gb=float(payload.get("memory_gb", 0.0)),
                input_data_mb=float(payload.get("input_data_mb", 0.0)),
                output_data_mb=float(payload.get("output_data_mb", 0.0)),
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
                demand_capacity=(
                    None
                    if payload.get("demand_capacity") is None
                    else float(payload["demand_capacity"])
                ),
                loss_rate=(
                    None
                    if payload.get("loss_rate") is None
                    else float(payload["loss_rate"])
                ),
            )
        raise TypeError("ROUTE_UPDATE payload must be Route or dict")

    def _emit_service_component_metrics(
        self,
        task: TaskRequest,
        decision: TaskPlacementDecision,
        kernel: SimulationKernel,
    ) -> None:
        if task.flow_id is None:
            return
        tags = (
            ("task_id", task.task_id),
            ("input_flow_id", _input_flow_id(task)),
            ("route_id", decision.route_id),
        ) + _service_placement_tags(decision)
        records = (
            MetricRecord(
                metric_name="service.input_network_latency",
                sim_time=decision.finish_time,
                entity_id=task.task_id,
                value=decision.transfer_time,
                tags=tags,
            ),
            MetricRecord(
                metric_name="service.compute_queue_delay",
                sim_time=decision.finish_time,
                entity_id=task.task_id,
                value=decision.queue_delay,
                tags=tags,
            ),
            MetricRecord(
                metric_name="service.compute_execution_delay",
                sim_time=decision.finish_time,
                entity_id=task.task_id,
                value=decision.compute_time,
                tags=tags,
            ),
        )
        for record in records:
            kernel.schedule_event(
                self._event(
                    dispatch_time=decision.finish_time,
                    event_type=EventType.METRIC_SAMPLE.value,
                    payload=record,
                )
            )

    def _emit_output_flow_arrival(
        self,
        task: TaskRequest,
        decision: TaskPlacementDecision,
        kernel: SimulationKernel,
    ) -> None:
        metadata = self._output_flows_by_task.get(task.task_id)
        if metadata is None:
            return
        self._output_flow_states[metadata.flow_id] = _OutputFlowState(
            metadata=metadata,
            decision=decision,
        )
        kernel.schedule_event(
            self._event(
                dispatch_time=decision.finish_time,
                event_type=EventType.FLOW_ARRIVAL.value,
                payload=metadata.to_flow_request(),
                target=self._network_target,
            )
        )

    def _emit_output_route_metrics(
        self,
        route: Route,
        dispatch_time: float,
        kernel: SimulationKernel,
    ) -> None:
        state = self._output_flow_states.get(route.flow_id)
        if state is None or not route.available or route.capacity <= 0:
            return
        output_latency = route.latency + state.metadata.data_size / route.capacity
        decision = state.decision
        total_latency = (
            decision.transfer_time
            + decision.queue_delay
            + decision.compute_time
            + output_latency
        )
        tags = (
            ("task_id", state.metadata.task_id),
            ("input_flow_id", state.metadata.input_flow_id),
            ("output_flow_id", state.metadata.flow_id),
            ("route_id", route.route_id),
        ) + _service_placement_tags(decision)
        records = (
            MetricRecord(
                metric_name="service.output_network_latency",
                sim_time=dispatch_time,
                entity_id=state.metadata.task_id,
                value=output_latency,
                tags=tags,
            ),
            MetricRecord(
                metric_name="service.total_latency",
                sim_time=dispatch_time,
                entity_id=state.metadata.task_id,
                value=total_latency,
                tags=tags,
            ),
        )
        for record in records:
            kernel.schedule_event(
                self._event(
                    dispatch_time=dispatch_time,
                    event_type=EventType.METRIC_SAMPLE.value,
                    payload=record,
                )
            )


def _decision_status(task: TaskRequest, finish_time: float) -> str:
    if task.deadline is not None and finish_time > task.deadline:
        return "DEADLINE_MISSED"
    return "SCHEDULED"


def _transfer_time(task: TaskRequest, route: Route) -> float:
    return route.latency + task.data_size / route.capacity


def _input_flow_id(task: TaskRequest) -> str:
    return task.flow_id or task.task_id


def _finish_status(decision: TaskPlacementDecision) -> str:
    if decision.status == "DEADLINE_MISSED":
        return "DEADLINE_MISSED"
    return "FINISHED"


def _service_placement_tags(
    decision: TaskPlacementDecision,
) -> tuple[tuple[str, str], ...]:
    return (
        ("compute_node_id", decision.node_id),
        ("service_placement_status", decision.placement_status),
        ("service_placement_policy", decision.placement_policy),
        ("service_placement_bottleneck_resource", decision.bottleneck_resource),
        ("service_placement_candidate_count", str(decision.candidate_count)),
        (
            "service_placement_capable_candidate_count",
            str(decision.capable_candidate_count),
        ),
        ("service_placement_candidate_queue_label", decision.candidate_queue_label),
    )


def _placement_candidate_queue_label(
    candidates: tuple[ServicePlacementCandidate, ...],
    limit: int = 5,
) -> str:
    ordered = tuple(sorted(candidates, key=lambda candidate: candidate.node_id))
    parts: list[str] = []
    for candidate in ordered[: max(0, limit)]:
        status = candidate.status.value
        queue = f"q={candidate.queued_task_count}"
        available = f"available={_format_seconds(candidate.available_at)}s"
        if candidate.rejection_reason is not None:
            detail = f"reject={candidate.rejection_reason.value}"
        else:
            finish = (
                f"finish={_format_seconds(candidate.finish_time or 0.0)}s"
                if candidate.finish_time is not None
                else "finish=unknown"
            )
            detail = finish
        parts.append(
            f"{candidate.node_id}:{status}/{available}/{queue}/{detail}"
        )
    hidden = max(0, len(ordered) - max(0, limit))
    if hidden > 0:
        parts.append(f"+{hidden} more")
    return "; ".join(parts)


def _format_seconds(value: float) -> str:
    formatted = f"{float(value):.3f}".rstrip("0").rstrip(".")
    return formatted or "0"


def _compute_node_state(
    node: ComputeNode,
    sim_time: float,
    available_capacity: float,
    status: str,
    task: TaskRequest | None = None,
) -> ComputeNodeState:
    return ComputeNodeState(
        node_id=node.node_id,
        sim_time=sim_time,
        capacity=node.capacity,
        available_capacity=available_capacity,
        status=status,
        cpu_gflops_fp64=node.cpu_gflops_fp64,
        gpu_tflops_fp32=node.gpu_tflops_fp32,
        gpu_tflops_fp16=node.gpu_tflops_fp16,
        npu_tops_int8=node.npu_tops_int8,
        memory_gb=node.memory_gb,
        storage_gb=node.storage_gb,
        **compute_node_resource_usage_fields(node, task),
    )
