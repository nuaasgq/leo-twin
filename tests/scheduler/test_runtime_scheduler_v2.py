from __future__ import annotations

import pytest

from leo_twin.sees.runtime_scheduler_v2 import (
    FailureType,
    ResourceEstimate,
    RuntimeTask,
    RuntimeTaskGraph,
    RuntimeTaskScheduler,
    RuntimeTaskStatus,
    StabilityController,
    SystemRuntimeState,
    TaskExecutionResult,
    TaskModule,
)


def test_dynamic_task_generation_works() -> None:
    scheduler = RuntimeTaskScheduler()

    result = scheduler.run_cycle(SystemRuntimeState())

    assert [task.task_id for task in scheduler.graph.tasks()] == ["runtime-task-001"]
    assert result.next_batch[0].task_id == "runtime-task-001"
    assert result.parallel_groups == (("runtime-task-001",),)


def test_task_priority_changes_at_runtime() -> None:
    task = RuntimeTask(
        task_id="frontend-observe",
        module=TaskModule.FRONTEND,
        priority=1,
        last_feedback_score=60,
    )
    scheduler = RuntimeTaskScheduler(RuntimeTaskGraph((task,)))

    result = scheduler.run_cycle(
        SystemRuntimeState(
            event_load=200,
            memory_mb=40,
            latency_ms=40,
            resource_capacity=ResourceEstimate(event_load=100, memory_mb=100, latency_ms=100),
        )
    )

    assert scheduler.graph.get("frontend-observe").priority == 4
    assert result.priority_adjustments == (("frontend-observe", 4),)


def test_failed_tasks_are_rescheduled_with_failure_classification() -> None:
    task = RuntimeTask(
        task_id="network-task",
        module=TaskModule.NETWORK,
        priority=3,
    )
    scheduler = RuntimeTaskScheduler(RuntimeTaskGraph((task,)))

    result = scheduler.run_cycle(
        SystemRuntimeState(),
        execution_results=(
            TaskExecutionResult(
                task_id="network-task",
                success=False,
                logs=("pytest assertion failed in route output",),
            ),
        ),
        reviewer_reports={
            "network-task": {
                "total_score": 70,
                "violations": ("test failure in network module",),
            }
        },
    )

    assert scheduler.feedback_engine.evaluate(
        task,
        TaskExecutionResult("network-task", False, ("pytest failure",)),
        {"total_score": 70, "violations": ("test failure",)},
        SystemRuntimeState(),
    ).failure_type == FailureType.TEST_FAILURE
    assert scheduler.graph.get("network-task").status == RuntimeTaskStatus.FAILED
    assert [task.task_id for task in result.regenerated_tasks] == [
        "network-task.repair01.1"
    ]
    assert result.next_batch[0].task_id == "network-task.repair01.1"


def test_failure_classification_covers_required_types() -> None:
    scheduler = RuntimeTaskScheduler()
    engine = scheduler.feedback_engine
    nominal = SystemRuntimeState()
    degraded = SystemRuntimeState(
        event_load=101,
        resource_capacity=ResourceEstimate(event_load=100, memory_mb=100, latency_ms=100),
    )

    assert engine.classify_failure(
        success=False,
        violations=("architecture layer violation",),
        logs=(),
        system_state=nominal,
    ) == FailureType.ARCHITECTURE_VIOLATION
    assert engine.classify_failure(
        success=False,
        violations=("dependency cycle detected",),
        logs=(),
        system_state=nominal,
    ) == FailureType.DEPENDENCY_CONFLICT
    assert engine.classify_failure(
        success=True,
        violations=(),
        logs=(),
        system_state=degraded,
    ) == FailureType.PERFORMANCE_BOTTLENECK
    assert engine.classify_failure(
        success=False,
        violations=("pytest assertion failed",),
        logs=(),
        system_state=nominal,
    ) == FailureType.TEST_FAILURE
    assert engine.classify_failure(
        success=False,
        violations=(),
        logs=("unexpected branch output",),
        system_state=nominal,
    ) == FailureType.LOGIC_ERROR


def test_dependency_graph_updates_correctly_after_replanning() -> None:
    failed = RuntimeTask(
        task_id="orbit-contract",
        module=TaskModule.ORBIT,
        priority=2,
    )
    dependent = RuntimeTask(
        task_id="network-contract",
        module=TaskModule.NETWORK,
        dependencies=("orbit-contract",),
    )
    scheduler = RuntimeTaskScheduler(RuntimeTaskGraph((failed, dependent)))

    result = scheduler.run_cycle(
        SystemRuntimeState(),
        execution_results=(
            TaskExecutionResult(
                task_id="orbit-contract",
                success=False,
                logs=("logic error in generated contract",),
            ),
        ),
        reviewer_reports={
            "orbit-contract": {
                "total_score": 55,
                "violations": ("logic error requires smaller task",),
            }
        },
    )

    repair = result.regenerated_tasks[-1]
    assert scheduler.graph.get("network-contract").dependencies == (repair.task_id,)
    assert scheduler.graph.topological_order() == (
        "orbit-contract",
        "orbit-contract.repair01.1",
        "network-contract",
    )


def test_system_does_not_enter_infinite_loop() -> None:
    task = RuntimeTask(
        task_id="compute-task",
        module=TaskModule.COMPUTE,
    )
    scheduler = RuntimeTaskScheduler(
        RuntimeTaskGraph((task,)),
        stability_controller=StabilityController(max_retry_per_task=1, task_budget_limit=4),
    )

    first = scheduler.run_cycle(
        SystemRuntimeState(),
        execution_results=(TaskExecutionResult("compute-task", False, ("logic error",)),),
    )
    second = scheduler.run_cycle(
        SystemRuntimeState(),
        execution_results=(TaskExecutionResult("compute-task", False, ("logic error",)),),
    )

    assert first.regenerated_tasks == ()
    assert second.regenerated_tasks == ()
    assert scheduler.graph.get("compute-task").failure_count == 1
    assert scheduler.graph.get("compute-task").status == RuntimeTaskStatus.FAILED
    assert second.stabilized is True


def test_parallel_groups_adapt_to_load_changes() -> None:
    tasks = (
        RuntimeTask(
            task_id="orbit",
            module=TaskModule.ORBIT,
            priority=3,
            resource_estimate=ResourceEstimate(event_load=20, memory_mb=20, latency_ms=10),
        ),
        RuntimeTask(
            task_id="network",
            module=TaskModule.NETWORK,
            priority=2,
            resource_estimate=ResourceEstimate(event_load=20, memory_mb=20, latency_ms=10),
        ),
        RuntimeTask(
            task_id="frontend",
            module=TaskModule.FRONTEND,
            priority=1,
            resource_estimate=ResourceEstimate(event_load=20, memory_mb=20, latency_ms=10),
        ),
    )

    normal = RuntimeTaskScheduler(RuntimeTaskGraph(tasks)).run_cycle(
        SystemRuntimeState(resource_capacity=ResourceEstimate(event_load=100, memory_mb=100, latency_ms=100))
    )
    degraded = RuntimeTaskScheduler(RuntimeTaskGraph(tasks)).run_cycle(
        SystemRuntimeState(
            event_load=101,
            memory_mb=50,
            latency_ms=50,
            resource_capacity=ResourceEstimate(event_load=100, memory_mb=100, latency_ms=100),
        )
    )

    assert normal.parallel_groups == (("orbit", "network", "frontend"),)
    assert degraded.parallel_groups == (("frontend", "orbit"), ("network",))


def test_dependency_cycles_are_rejected() -> None:
    first = RuntimeTask(task_id="first", module=TaskModule.METRICS)
    second = RuntimeTask(
        task_id="second",
        module=TaskModule.FRONTEND,
        dependencies=("first",),
    )
    graph = RuntimeTaskGraph((first, second))

    with pytest.raises(ValueError, match="cycle"):
        graph.update_dependencies("first", ("second",))
