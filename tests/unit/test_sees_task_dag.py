import pytest

from leo_twin.sees.task_dag import (
    TASK_COMPLETE,
    EngineeringTask,
    TaskDAG,
    generate_initial_task,
)


def test_task_dag_ready_tasks_and_topological_order_are_deterministic():
    first = generate_initial_task()
    second = EngineeringTask(
        task_id="task-auto-002",
        title="Second",
        description="Depends on first.",
        issue_id="AUTO-002",
        dependencies=(first.task_id,),
    )
    dag = TaskDAG((first, second))

    assert dag.topological_order() == ("task-auto-001", "task-auto-002")
    assert [task.task_id for task in dag.ready_tasks()] == ["task-auto-001"]

    dag.mark_status(first.task_id, TASK_COMPLETE)

    assert [task.task_id for task in dag.ready_tasks()] == ["task-auto-002"]


def test_task_dag_rejects_duplicate_and_unknown_dependencies():
    task = generate_initial_task()
    dag = TaskDAG((task,))

    with pytest.raises(ValueError, match="duplicate task_id"):
        dag.add_task(task)

    with pytest.raises(ValueError, match="unknown dependencies"):
        dag.add_task(
            EngineeringTask(
                task_id="bad",
                title="Bad",
                description="Missing dependency.",
                issue_id="BAD",
                dependencies=("missing",),
            )
        )
