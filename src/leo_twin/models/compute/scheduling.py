"""Deterministic compute scheduling policy runtime."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from math import isfinite
from typing import Any

from leo_twin.models.compute.contracts import ComputeNode
from leo_twin.schema import TaskRequest


class ComputeSchedulingPolicy(StrEnum):
    """Supported deterministic compute scheduling policies."""

    FIFO = "FIFO"
    SHORTEST_JOB_FIRST = "SHORTEST_JOB_FIRST"
    EARLIEST_DEADLINE_FIRST = "EARLIEST_DEADLINE_FIRST"


@dataclass(frozen=True)
class ComputeWorkloadItem:
    """A task with an explicit deterministic ready time."""

    task: TaskRequest
    ready_time: float

    def __post_init__(self) -> None:
        _require_finite_number(self.ready_time, "ready_time")


@dataclass(frozen=True)
class ComputeScheduleDecision:
    """Deterministic placement decision emitted by the scheduler."""

    task_id: str
    node_id: str
    start_time: float
    finish_time: float

    def __post_init__(self) -> None:
        if not isinstance(self.task_id, str) or not self.task_id:
            raise TypeError("task_id must be a non-empty str")
        if not isinstance(self.node_id, str) or not self.node_id:
            raise TypeError("node_id must be a non-empty str")
        _require_finite_number(self.start_time, "start_time")
        _require_finite_number(self.finish_time, "finish_time")
        if self.finish_time < self.start_time:
            raise ValueError("finish_time must be >= start_time")


class ComputeSchedulingRuntime:
    """Schedule ready compute workloads over configured compute nodes."""

    def __init__(
        self,
        policy: ComputeSchedulingPolicy = ComputeSchedulingPolicy.FIFO,
    ) -> None:
        if not isinstance(policy, ComputeSchedulingPolicy):
            policy = ComputeSchedulingPolicy(str(policy))
        self._policy = policy

    @property
    def policy(self) -> ComputeSchedulingPolicy:
        return self._policy

    def schedule(
        self,
        workloads: tuple[ComputeWorkloadItem, ...],
        nodes: tuple[ComputeNode, ...],
    ) -> tuple[ComputeScheduleDecision, ...]:
        """Return deterministic schedule decisions for a finite workload batch."""

        ordered_nodes = tuple(sorted(nodes, key=lambda item: item.node_id))
        if not ordered_nodes:
            raise ValueError("nodes must not be empty")
        available_at = {node.node_id: 0.0 for node in ordered_nodes}
        decisions: list[ComputeScheduleDecision] = []

        for item in self.order_workloads(workloads):
            node, start_time, finish_time = _select_node(
                item=item,
                nodes=ordered_nodes,
                available_at=available_at,
            )
            available_at[node.node_id] = finish_time
            decisions.append(
                ComputeScheduleDecision(
                    task_id=item.task.task_id,
                    node_id=node.node_id,
                    start_time=start_time,
                    finish_time=finish_time,
                )
            )
        return tuple(decisions)

    def order_workloads(
        self,
        workloads: tuple[ComputeWorkloadItem, ...],
    ) -> tuple[ComputeWorkloadItem, ...]:
        """Return workload order for the configured deterministic policy."""

        return tuple(sorted(workloads, key=self._workload_key))

    def _workload_key(self, item: ComputeWorkloadItem) -> tuple[float, float, str]:
        if self._policy == ComputeSchedulingPolicy.SHORTEST_JOB_FIRST:
            return (item.ready_time, item.task.compute_demand, item.task.task_id)
        if self._policy == ComputeSchedulingPolicy.EARLIEST_DEADLINE_FIRST:
            deadline = float("inf") if item.task.deadline is None else item.task.deadline
            return (item.ready_time, deadline, item.task.task_id)
        return (item.ready_time, item.task.submit_time, item.task.task_id)


def _select_node(
    item: ComputeWorkloadItem,
    nodes: tuple[ComputeNode, ...],
    available_at: dict[str, float],
) -> tuple[ComputeNode, float, float]:
    candidates: list[tuple[float, float, str, ComputeNode]] = []
    for compute_node in nodes:
        start_time = max(item.ready_time, available_at[compute_node.node_id])
        finish_time = start_time + item.task.compute_demand / compute_node.capacity
        candidates.append((finish_time, start_time, compute_node.node_id, compute_node))
    finish_time, start_time, _, selected = min(candidates)
    return selected, start_time, finish_time


def _require_finite_number(value: Any, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field_name} must be an int or float")
    if not isfinite(value):
        raise ValueError(f"{field_name} must be finite")
