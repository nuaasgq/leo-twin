from leo_twin.sees.task_dag import TASK_COMPLETE, EngineeringTask, TaskDAG


def test_task_dag_handles_lightweight_scale_chain_deterministically():
    tasks = []
    for index in range(120):
        dependencies = () if index == 0 else (f"task-{index - 1:03d}",)
        tasks.append(
            EngineeringTask(
                task_id=f"task-{index:03d}",
                title=f"Task {index}",
                description="Scale DAG task.",
                issue_id=f"SCALE-{index:03d}",
                dependencies=dependencies,
            )
        )
    dag = TaskDAG(tuple(tasks))

    assert dag.topological_order()[0] == "task-000"
    assert dag.topological_order()[-1] == "task-119"

    for task in tasks[:-1]:
        dag.mark_status(task.task_id, TASK_COMPLETE)

    assert [task.task_id for task in dag.ready_tasks()] == ["task-119"]
