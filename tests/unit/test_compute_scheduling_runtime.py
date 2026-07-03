from __future__ import annotations

from leo_twin.models.compute import (
    ComputeNode,
    ComputeSchedulingPolicy,
    ComputeSchedulingRuntime,
    ComputeWorkloadItem,
)
from leo_twin.schema import TaskRequest


def _task(
    task_id: str,
    demand: float,
    submit_time: float = 0.0,
    deadline: float | None = None,
) -> TaskRequest:
    return TaskRequest(
        task_id=task_id,
        source_id="user-a",
        submit_time=submit_time,
        compute_demand=demand,
        data_size=1.0,
        deadline=deadline,
    )


def _nodes() -> tuple[ComputeNode, ...]:
    return (
        ComputeNode("node-b", capacity=20.0),
        ComputeNode("node-a", capacity=10.0),
    )


def test_fifo_policy_orders_by_ready_submit_and_task_id() -> None:
    runtime = ComputeSchedulingRuntime(ComputeSchedulingPolicy.FIFO)
    workloads = (
        ComputeWorkloadItem(_task("task-c", 10.0, submit_time=2.0), ready_time=0.0),
        ComputeWorkloadItem(_task("task-a", 10.0, submit_time=0.0), ready_time=0.0),
        ComputeWorkloadItem(_task("task-b", 10.0, submit_time=1.0), ready_time=0.0),
    )

    decisions = runtime.schedule(workloads, _nodes())

    assert [decision.task_id for decision in decisions] == ["task-a", "task-b", "task-c"]


def test_shortest_job_first_policy_prioritizes_small_compute_demand() -> None:
    runtime = ComputeSchedulingRuntime(ComputeSchedulingPolicy.SHORTEST_JOB_FIRST)
    workloads = (
        ComputeWorkloadItem(_task("large", 30.0), ready_time=0.0),
        ComputeWorkloadItem(_task("small", 5.0), ready_time=0.0),
        ComputeWorkloadItem(_task("medium", 10.0), ready_time=0.0),
    )

    decisions = runtime.schedule(workloads, _nodes())

    assert [decision.task_id for decision in decisions] == ["small", "medium", "large"]


def test_earliest_deadline_first_policy_prioritizes_deadline() -> None:
    runtime = ComputeSchedulingRuntime(ComputeSchedulingPolicy.EARLIEST_DEADLINE_FIRST)
    workloads = (
        ComputeWorkloadItem(_task("later", 10.0, deadline=20.0), ready_time=0.0),
        ComputeWorkloadItem(_task("none", 10.0), ready_time=0.0),
        ComputeWorkloadItem(_task("soon", 10.0, deadline=5.0), ready_time=0.0),
    )

    decisions = runtime.schedule(workloads, _nodes())

    assert [decision.task_id for decision in decisions] == ["soon", "later", "none"]


def test_compute_scheduling_runtime_is_deterministic() -> None:
    runtime = ComputeSchedulingRuntime(ComputeSchedulingPolicy.SHORTEST_JOB_FIRST)
    workloads = (
        ComputeWorkloadItem(_task("task-b", 20.0), ready_time=1.0),
        ComputeWorkloadItem(_task("task-a", 10.0), ready_time=1.0),
    )

    assert runtime.schedule(workloads, _nodes()) == runtime.schedule(tuple(reversed(workloads)), _nodes())
