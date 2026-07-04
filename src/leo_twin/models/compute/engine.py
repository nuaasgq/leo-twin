"""Deterministic event-driven compute task scheduler."""

from dataclasses import dataclass
from typing import Iterable

from leo_twin.core import SimulationKernel, SimulationModule
from leo_twin.models.compute.contracts import COMPUTE_NODE_UPDATE, ComputeNode
from leo_twin.schema import (
    ComputeNodeState,
    EventType,
    FlowState,
    SimEvent,
    TaskRequest,
    TaskState,
)


@dataclass(frozen=True)
class _TaskPlan:
    task: TaskRequest
    node_id: str
    start_time: float
    finish_time: float


class ComputeEngine(SimulationModule):
    """Schedule tasks on compute nodes using a deterministic service model."""

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

        ordered_nodes = tuple(sorted(nodes, key=lambda node: node.node_id))
        if not ordered_nodes:
            raise ValueError("at least one compute node is required")
        node_ids = tuple(node.node_id for node in ordered_nodes)
        if len(set(node_ids)) != len(node_ids):
            raise ValueError("compute node ids must be unique")

        self._module_name = module_name
        self._metrics_target = metrics_target
        self._nodes = ordered_nodes
        self._available_at = {node.node_id: 0.0 for node in self._nodes}
        self._tasks: dict[str, _TaskPlan] = {}
        self._completed_flows: dict[str, FlowState] = {}
        self._event_sequence = 0

    def name(self) -> str:
        return self._module_name

    def on_event(self, event: SimEvent, kernel: SimulationKernel) -> None:
        if event.event_type == EventType.TASK_ARRIVAL:
            self._schedule_task(self._coerce_task_request(event.payload), event, kernel)
            return

        if event.event_type == EventType.FLOW_COMPLETE:
            flow = self._coerce_flow_state(event.payload)
            self._completed_flows[flow.flow_id] = flow

    def scheduled_tasks(self) -> tuple[tuple[str, str, float, float], ...]:
        """Return task plans ordered by task id for deterministic inspection."""

        return tuple(
            (
                plan.task.task_id,
                plan.node_id,
                plan.start_time,
                plan.finish_time,
            )
            for plan in (self._tasks[task_id] for task_id in sorted(self._tasks))
        )

    def completed_flows(self) -> tuple[FlowState, ...]:
        """Return FLOW_COMPLETE inputs consumed by this module."""

        return tuple(
            self._completed_flows[flow_id]
            for flow_id in sorted(self._completed_flows)
        )

    def _schedule_task(
        self,
        task: TaskRequest,
        event: SimEvent,
        kernel: SimulationKernel,
    ) -> None:
        if task.task_id in self._tasks:
            raise ValueError(f"task already scheduled: {task.task_id!r}")

        ready_time = max(float(event.sim_time), float(task.submit_time))
        node, start_time, finish_time = self._select_node(task, ready_time)
        self._available_at[node.node_id] = finish_time
        self._tasks[task.task_id] = _TaskPlan(
            task=task,
            node_id=node.node_id,
            start_time=start_time,
            finish_time=finish_time,
        )

        kernel.schedule_event(
            self._event(
                sim_time=start_time,
                event_type=EventType.TASK_START.value,
                payload=TaskState(
                    task_id=task.task_id,
                    node_id=node.node_id,
                    sim_time=start_time,
                    progress=0.0,
                    status="RUNNING",
                ),
            )
        )
        kernel.schedule_event(
            self._event(
                sim_time=start_time,
                event_type=COMPUTE_NODE_UPDATE,
                payload=_compute_node_state(node, start_time, 0.0, "BUSY"),
            )
        )
        kernel.schedule_event(
            self._event(
                sim_time=finish_time,
                event_type=EventType.TASK_FINISH.value,
                payload=TaskState(
                    task_id=task.task_id,
                    node_id=node.node_id,
                    sim_time=finish_time,
                    progress=1.0,
                    status="FINISHED",
                ),
            )
        )
        kernel.schedule_event(
            self._event(
                sim_time=finish_time,
                event_type=COMPUTE_NODE_UPDATE,
                payload=_compute_node_state(node, finish_time, node.capacity, "IDLE"),
            )
        )

    def _select_node(
        self,
        task: TaskRequest,
        ready_time: float,
    ) -> tuple[ComputeNode, float, float]:
        candidates: list[tuple[float, float, str, ComputeNode]] = []
        for node in self._nodes:
            start_time = max(self._available_at[node.node_id], ready_time)
            finish_time = start_time + (task.compute_demand / node.capacity)
            candidates.append((finish_time, start_time, node.node_id, node))

        finish_time, start_time, _, node = min(candidates)
        return node, start_time, finish_time

    def _event(
        self,
        sim_time: float,
        event_type: str,
        payload: object,
    ) -> SimEvent:
        self._event_sequence += 1
        return SimEvent(
            event_id=f"{self._module_name}:{self._event_sequence:08d}",
            sim_time=sim_time,
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
    def _coerce_flow_state(payload: object) -> FlowState:
        if isinstance(payload, FlowState):
            return payload
        if isinstance(payload, dict):
            return FlowState(
                flow_id=str(payload["flow_id"]),
                route_id=str(payload["route_id"]),
                source_id=str(payload["source_id"]),
                target_id=str(payload["target_id"]),
                status=str(payload["status"]),
            )
        raise TypeError("FLOW_COMPLETE payload must be FlowState or dict")


def _compute_node_state(
    node: ComputeNode,
    sim_time: float,
    available_capacity: float,
    status: str,
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
    )
