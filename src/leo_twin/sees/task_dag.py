"""Deterministic task DAG engine for engineering work."""

from __future__ import annotations

from dataclasses import dataclass, replace


TASK_PENDING = "pending"
TASK_RUNNING = "running"
TASK_COMPLETE = "complete"
TASK_FAILED = "failed"
TASK_SPLIT = "split"


@dataclass(frozen=True)
class EngineeringTask:
    """A deterministic development task mapped to one Codex issue."""

    task_id: str
    title: str
    description: str
    issue_id: str
    dependencies: tuple[str, ...] = ()
    status: str = TASK_PENDING
    patch_plan: tuple["FilePatchProtocol", ...] = ()

    def with_status(self, status: str) -> "EngineeringTask":
        return replace(self, status=status)

    def with_dependencies(self, dependencies: tuple[str, ...]) -> "EngineeringTask":
        return replace(self, dependencies=dependencies)


class FilePatchProtocol:
    path: str
    content: str


class TaskDAG:
    """Mutable DAG state with deterministic ordering."""

    def __init__(self, tasks: tuple[EngineeringTask, ...] = ()) -> None:
        self._tasks: dict[str, EngineeringTask] = {}
        for task in tasks:
            self.add_task(task)

    def add_task(self, task: EngineeringTask) -> None:
        if task.task_id in self._tasks:
            raise ValueError(f"duplicate task_id: {task.task_id!r}")
        unknown = sorted(set(task.dependencies) - set(self._tasks))
        if unknown:
            raise ValueError(
                f"task {task.task_id!r} has unknown dependencies: {unknown}"
            )
        self._tasks[task.task_id] = task
        self._validate_acyclic()

    def get_task(self, task_id: str) -> EngineeringTask:
        return self._tasks[task_id]

    def tasks(self) -> tuple[EngineeringTask, ...]:
        return tuple(self._tasks[task_id] for task_id in sorted(self._tasks))

    def ready_tasks(self) -> tuple[EngineeringTask, ...]:
        ready: list[EngineeringTask] = []
        for task in self.tasks():
            if task.status != TASK_PENDING:
                continue
            if all(
                self._tasks[dependency].status == TASK_COMPLETE
                for dependency in task.dependencies
            ):
                ready.append(task)
        return tuple(ready)

    def mark_status(self, task_id: str, status: str) -> None:
        self._tasks[task_id] = self._tasks[task_id].with_status(status)

    def replace_dependency(
        self,
        old_dependency: str,
        new_dependency: str,
    ) -> None:
        for task_id in sorted(self._tasks):
            task = self._tasks[task_id]
            if old_dependency not in task.dependencies:
                continue
            dependencies = tuple(
                new_dependency if item == old_dependency else item
                for item in task.dependencies
            )
            self._tasks[task_id] = task.with_dependencies(dependencies)
        self._validate_acyclic()

    def topological_order(self) -> tuple[str, ...]:
        remaining = {task.task_id: set(task.dependencies) for task in self.tasks()}
        order: list[str] = []

        while remaining:
            ready = sorted(
                task_id
                for task_id, dependencies in remaining.items()
                if not dependencies
            )
            if not ready:
                raise ValueError("task graph contains a cycle")
            for task_id in ready:
                order.append(task_id)
                del remaining[task_id]
            for dependencies in remaining.values():
                dependencies.difference_update(ready)
        return tuple(order)

    def _validate_acyclic(self) -> None:
        self.topological_order()


def generate_initial_task(issue_id: str = "AUTO-001") -> EngineeringTask:
    return EngineeringTask(
        task_id="task-auto-001",
        title="Run deterministic engineering review",
        description="Automatically generated task for SEES closed-loop validation.",
        issue_id=issue_id,
    )
