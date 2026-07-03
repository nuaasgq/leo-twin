from leo_twin.sees.ci_gate import CIGate
from leo_twin.sees.evolution_controller import EvolutionController
from leo_twin.sees.task_dag import EngineeringTask, TaskDAG


def test_ci_gate_maps_pass_to_zero_and_fail_to_one():
    gate = CIGate()

    assert gate.evaluate_report({"decision": "PASS"}) == 0
    assert gate.evaluate_report({"decision": "REJECT"}) == 1


def test_evolution_controller_splits_failed_task_and_rewires_dag():
    root = EngineeringTask(
        task_id="task-1",
        title="Root",
        description="Root task.",
        issue_id="T1",
    )
    dependent = EngineeringTask(
        task_id="task-2",
        title="Dependent",
        description="Depends on root.",
        issue_id="T2",
        dependencies=("task-1",),
    )
    dag = TaskDAG((root, dependent))
    report = {
        "required_fixes": ["Fix A", "Fix B"],
        "violations": [],
    }

    subtasks = EvolutionController().evolve_failed_task(dag, "task-1", report)

    assert [task.task_id for task in subtasks] == [
        "task-1.fix01",
        "task-1.fix02",
    ]
    assert dag.get_task("task-2").dependencies == ("task-1.fix02",)
    assert dag.topological_order() == (
        "task-1",
        "task-1.fix01",
        "task-1.fix02",
        "task-2",
    )
