from __future__ import annotations

from leo_twin.sees import (
    RuntimeTaskScheduler,
    RuntimeTaskStatus,
    SystemRuntimeState,
    TaskModule,
    build_full_system_task_graph,
    build_full_system_task_specs,
)


def test_full_system_task_specs_are_deterministic() -> None:
    first = build_full_system_task_specs()
    second = build_full_system_task_specs()

    assert first == second
    assert [task.task_id for task in first] == [
        "FS-000",
        "FS-010",
        "FS-020",
        "FS-030",
        "FS-040",
        "FS-050",
        "FS-060",
        "FS-070",
        "FS-080",
        "FS-090",
        "FS-100",
    ]


def test_full_system_task_graph_is_a_dag() -> None:
    graph = build_full_system_task_graph()

    assert graph.topological_order() == (
        "FS-000",
        "FS-010",
        "FS-020",
        "FS-030",
        "FS-040",
        "FS-050",
        "FS-060",
        "FS-070",
        "FS-080",
        "FS-090",
        "FS-100",
    )


def test_full_system_task_graph_exposes_parallel_domain_work() -> None:
    graph = build_full_system_task_graph()
    graph.mark_status("FS-000", RuntimeTaskStatus.COMPLETED)
    graph.mark_status("FS-010", RuntimeTaskStatus.COMPLETED)

    ready = graph.ready_tasks()

    assert {task.module for task in ready} == {
        TaskModule.ORBIT,
        TaskModule.NETWORK,
        TaskModule.COMPUTE,
        TaskModule.FRONTEND,
        TaskModule.METRICS,
    }
    assert {task.task_id for task in ready} == {
        "FS-020",
        "FS-030",
        "FS-040",
        "FS-050",
        "FS-060",
        "FS-070",
    }


def test_full_system_scheduler_groups_independent_modules() -> None:
    graph = build_full_system_task_graph()
    graph.mark_status("FS-000", RuntimeTaskStatus.COMPLETED)
    graph.mark_status("FS-010", RuntimeTaskStatus.COMPLETED)
    scheduler = RuntimeTaskScheduler(graph)

    result = scheduler.run_cycle(SystemRuntimeState())

    assert result.parallel_groups == (
        ("FS-020", "FS-030", "FS-040", "FS-050", "FS-070"),
        ("FS-060",),
    )
