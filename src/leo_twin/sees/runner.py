"""Closed-loop SEES runner."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from leo_twin.sees.auto_fix import AutoFixEngine
from leo_twin.sees.ci_gate import CIGate
from leo_twin.sees.codex_executor import CodexExecutor, ExecutionResult
from leo_twin.sees.evolution_controller import EvolutionController
from leo_twin.sees.task_dag import (
    TASK_COMPLETE,
    TASK_FAILED,
    TASK_RUNNING,
    EngineeringTask,
    TaskDAG,
    generate_initial_task,
)


@dataclass(frozen=True)
class SEESRunResult:
    task_id: str
    execution: ExecutionResult
    final_report: dict[str, Any]
    ci_exit_code: int
    generated_tasks: tuple[EngineeringTask, ...]


class SEESRunner:
    """Run Task -> Code -> Review -> Fix -> CI -> Evolution once per ready task."""

    def __init__(
        self,
        executor: CodexExecutor | None = None,
        auto_fix: AutoFixEngine | None = None,
        ci_gate: CIGate | None = None,
        evolution: EvolutionController | None = None,
    ) -> None:
        self._executor = executor or CodexExecutor()
        self._auto_fix = auto_fix or AutoFixEngine()
        self._ci_gate = ci_gate or CIGate()
        self._evolution = evolution or EvolutionController()

    def run_once(self, dag: TaskDAG, workspace: str | Path) -> SEESRunResult:
        ready = dag.ready_tasks()
        if not ready:
            generated = self._evolution.generate_next_task(dag)
            dag.add_task(generated)
            ready = (generated,)

        task = ready[0]
        dag.mark_status(task.task_id, TASK_RUNNING)
        execution = self._executor.execute(task, workspace)
        fix_result = self._auto_fix.fix_until_passes(workspace, max_iterations=3)
        ci_exit_code = self._ci_gate.evaluate_report(fix_result.final_report)

        generated_tasks: tuple[EngineeringTask, ...] = ()
        if ci_exit_code == 0:
            dag.mark_status(task.task_id, TASK_COMPLETE)
            next_task = self._evolution.generate_next_task(dag)
            dag.add_task(next_task)
            generated_tasks = (next_task,)
        else:
            dag.mark_status(task.task_id, TASK_FAILED)
            generated_tasks = self._evolution.evolve_failed_task(
                dag,
                task.task_id,
                fix_result.final_report,
            )

        return SEESRunResult(
            task_id=task.task_id,
            execution=execution,
            final_report=fix_result.final_report,
            ci_exit_code=ci_exit_code,
            generated_tasks=generated_tasks,
        )

    def run_generated_task(self, workspace: str | Path) -> SEESRunResult:
        dag = TaskDAG((generate_initial_task(),))
        return self.run_once(dag, workspace)
