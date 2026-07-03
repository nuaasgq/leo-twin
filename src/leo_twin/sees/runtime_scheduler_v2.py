"""Runtime adaptive task scheduler for closed-loop SEES execution."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import StrEnum
from typing import Any


class TaskModule(StrEnum):
    """Engineering module ownership used for isolation-aware scheduling."""

    SYSTEM = "system"
    ORBIT = "orbit"
    NETWORK = "network"
    COMPUTE = "compute"
    METRICS = "metrics"
    FRONTEND = "frontend"


class RuntimeTaskStatus(StrEnum):
    """Runtime task lifecycle states."""

    PENDING = "pending"
    RUNNING = "running"
    FAILED = "failed"
    COMPLETED = "completed"


class FailureType(StrEnum):
    """Failure classes consumed by the replanning engine."""

    LOGIC_ERROR = "LOGIC_ERROR"
    ARCHITECTURE_VIOLATION = "ARCHITECTURE_VIOLATION"
    PERFORMANCE_BOTTLENECK = "PERFORMANCE_BOTTLENECK"
    TEST_FAILURE = "TEST_FAILURE"
    DEPENDENCY_CONFLICT = "DEPENDENCY_CONFLICT"


@dataclass(frozen=True)
class ResourceEstimate:
    """Deterministic resource estimate for scheduler admission control."""

    event_load: int = 1
    memory_mb: int = 1
    latency_ms: int = 1

    def __post_init__(self) -> None:
        _require_non_negative_int(self.event_load, "event_load")
        _require_non_negative_int(self.memory_mb, "memory_mb")
        _require_non_negative_int(self.latency_ms, "latency_ms")


@dataclass(frozen=True)
class RuntimeTask:
    """A runtime-evolving engineering task node."""

    task_id: str
    module: TaskModule
    status: RuntimeTaskStatus = RuntimeTaskStatus.PENDING
    priority: int = 0
    dependencies: tuple[str, ...] = ()
    resource_estimate: ResourceEstimate = field(default_factory=ResourceEstimate)
    failure_count: int = 0
    last_feedback_score: int = 100
    title: str = ""
    parent_task_id: str | None = None

    def __post_init__(self) -> None:
        if not self.task_id:
            raise ValueError("task_id must be non-empty")
        if not isinstance(self.module, TaskModule):
            object.__setattr__(self, "module", TaskModule(str(self.module)))
        if not isinstance(self.status, RuntimeTaskStatus):
            object.__setattr__(self, "status", RuntimeTaskStatus(str(self.status)))
        _require_int(self.priority, "priority")
        _require_non_negative_int(self.failure_count, "failure_count")
        _require_score(self.last_feedback_score)
        object.__setattr__(self, "dependencies", tuple(sorted(set(self.dependencies))))

    def with_status(self, status: RuntimeTaskStatus | str) -> "RuntimeTask":
        return replace(self, status=RuntimeTaskStatus(str(status)))

    def with_priority(self, priority: int) -> "RuntimeTask":
        return replace(self, priority=priority)

    def with_feedback(self, score: int, failed: bool) -> "RuntimeTask":
        return replace(
            self,
            last_feedback_score=score,
            failure_count=self.failure_count + (1 if failed else 0),
        )

    def with_dependencies(self, dependencies: tuple[str, ...]) -> "RuntimeTask":
        return replace(self, dependencies=tuple(sorted(set(dependencies))))


@dataclass(frozen=True)
class SystemRuntimeState:
    """Read-only runtime signals consumed by the scheduler."""

    event_load: int = 0
    memory_mb: int = 0
    latency_ms: int = 0
    resource_capacity: ResourceEstimate = field(
        default_factory=lambda: ResourceEstimate(
            event_load=100,
            memory_mb=100,
            latency_ms=100,
        )
    )

    def __post_init__(self) -> None:
        _require_non_negative_int(self.event_load, "event_load")
        _require_non_negative_int(self.memory_mb, "memory_mb")
        _require_non_negative_int(self.latency_ms, "latency_ms")


@dataclass(frozen=True)
class TaskExecutionResult:
    """Executor outcome signal for a runtime task."""

    task_id: str
    success: bool
    logs: tuple[str, ...] = ()


@dataclass(frozen=True)
class FeedbackSignal:
    """Normalized feedback signal used for replanning."""

    task_id: str
    quality_score: int
    failure_type: FailureType | None
    violations: tuple[str, ...]
    dependency_conflicts: tuple[str, ...]
    performance_bottlenecks: tuple[str, ...]


@dataclass(frozen=True)
class SchedulerCycleResult:
    """Output of one closed-loop scheduler cycle."""

    cycle_index: int
    next_batch: tuple[RuntimeTask, ...]
    updated_task_ids: tuple[str, ...]
    priority_adjustments: tuple[tuple[str, int], ...]
    parallel_groups: tuple[tuple[str, ...], ...]
    regenerated_tasks: tuple[RuntimeTask, ...]
    stabilized: bool


class RuntimeTaskGraph:
    """Dynamic DAG that allows runtime task and dependency mutation."""

    def __init__(self, tasks: tuple[RuntimeTask, ...] = ()) -> None:
        self._tasks: dict[str, RuntimeTask] = {}
        for task in tasks:
            self.add_task(task)

    def add_task(self, task: RuntimeTask) -> None:
        if task.task_id in self._tasks:
            raise ValueError(f"duplicate task_id: {task.task_id}")
        unknown = sorted(set(task.dependencies) - set(self._tasks))
        if unknown:
            raise ValueError(f"task {task.task_id} has unknown dependencies: {unknown}")
        self._tasks[task.task_id] = task
        self.validate_acyclic()

    def get(self, task_id: str) -> RuntimeTask:
        return self._tasks[task_id]

    def tasks(self) -> tuple[RuntimeTask, ...]:
        return tuple(self._tasks[task_id] for task_id in sorted(self._tasks))

    def update_task(self, task: RuntimeTask) -> None:
        if task.task_id not in self._tasks:
            raise KeyError(task.task_id)
        unknown = sorted(set(task.dependencies) - set(self._tasks))
        if unknown:
            raise ValueError(f"task {task.task_id} has unknown dependencies: {unknown}")
        previous = self._tasks[task.task_id]
        self._tasks[task.task_id] = task
        try:
            self.validate_acyclic()
        except ValueError:
            self._tasks[task.task_id] = previous
            raise

    def mark_status(self, task_id: str, status: RuntimeTaskStatus | str) -> None:
        self.update_task(self.get(task_id).with_status(status))

    def update_priority(self, task_id: str, priority: int) -> None:
        self.update_task(self.get(task_id).with_priority(priority))

    def update_dependencies(self, task_id: str, dependencies: tuple[str, ...]) -> None:
        self.update_task(self.get(task_id).with_dependencies(dependencies))

    def replace_dependency(self, old_dependency: str, new_dependency: str) -> None:
        for task in self.tasks():
            if old_dependency not in task.dependencies:
                continue
            dependencies = tuple(
                new_dependency if item == old_dependency else item
                for item in task.dependencies
            )
            self.update_dependencies(task.task_id, dependencies)

    def ready_tasks(self) -> tuple[RuntimeTask, ...]:
        ready = [
            task
            for task in self.tasks()
            if task.status == RuntimeTaskStatus.PENDING
            and all(
                self._tasks[dependency].status == RuntimeTaskStatus.COMPLETED
                for dependency in task.dependencies
            )
        ]
        return tuple(sorted(ready, key=_task_sort_key))

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
                raise ValueError("runtime task graph contains a cycle")
            for task_id in ready:
                order.append(task_id)
                del remaining[task_id]
            for dependencies in remaining.values():
                dependencies.difference_update(ready)
        return tuple(order)

    def validate_acyclic(self) -> None:
        self.topological_order()


class FeedbackLoopEngine:
    """Convert reviewer, execution, and metrics input into feedback signals."""

    def evaluate(
        self,
        task: RuntimeTask,
        execution: TaskExecutionResult | None,
        reviewer_report: dict[str, Any] | None,
        system_state: SystemRuntimeState,
    ) -> FeedbackSignal:
        report = reviewer_report or {}
        review_score = int(report.get("total_score", 100))
        violations = tuple(sorted(str(item) for item in report.get("violations", ())))
        logs = () if execution is None else execution.logs
        failure_type = self.classify_failure(
            success=True if execution is None else execution.success,
            violations=violations,
            logs=logs,
            system_state=system_state,
        )
        penalty = 20 if failure_type is not None else 0
        quality_score = max(0, min(100, review_score - penalty))
        return FeedbackSignal(
            task_id=task.task_id,
            quality_score=quality_score,
            failure_type=failure_type,
            violations=violations,
            dependency_conflicts=_matching_items(violations + logs, ("dependency", "cycle")),
            performance_bottlenecks=_performance_items(violations + logs, system_state),
        )

    def classify_failure(
        self,
        success: bool,
        violations: tuple[str, ...],
        logs: tuple[str, ...],
        system_state: SystemRuntimeState,
    ) -> FailureType | None:
        text = " ".join((*violations, *logs)).lower()
        if "architecture" in text or "hard-stop" in text or "layer" in text:
            return FailureType.ARCHITECTURE_VIOLATION
        if "dependency" in text or "cycle" in text:
            return FailureType.DEPENDENCY_CONFLICT
        if _is_degraded(system_state) or "performance" in text or "bottleneck" in text:
            return FailureType.PERFORMANCE_BOTTLENECK
        if "test" in text or "pytest" in text or "assert" in text:
            return FailureType.TEST_FAILURE
        if not success or violations:
            return FailureType.LOGIC_ERROR
        return None


class StabilityController:
    """Bound runtime evolution to prevent scheduler instability."""

    def __init__(self, max_retry_per_task: int = 2, task_budget_limit: int = 64) -> None:
        _require_positive_int(max_retry_per_task, "max_retry_per_task")
        _require_positive_int(task_budget_limit, "task_budget_limit")
        self.max_retry_per_task = max_retry_per_task
        self.task_budget_limit = task_budget_limit

    def can_retry(self, task: RuntimeTask) -> bool:
        return task.failure_count < self.max_retry_per_task

    def can_add_tasks(self, graph: RuntimeTaskGraph, count: int) -> bool:
        return len(graph.tasks()) + count <= self.task_budget_limit

    def stabilized(self, graph: RuntimeTaskGraph) -> bool:
        graph.validate_acyclic()
        tasks = graph.tasks()
        return len(tasks) <= self.task_budget_limit and all(
            task.failure_count <= self.max_retry_per_task for task in tasks
        )


class ReplanningEngine:
    """Apply failure-driven structural graph changes."""

    def __init__(self, stability: StabilityController) -> None:
        self._stability = stability

    def replan(
        self,
        graph: RuntimeTaskGraph,
        task: RuntimeTask,
        feedback: FeedbackSignal,
    ) -> tuple[RuntimeTask, ...]:
        if task.status == RuntimeTaskStatus.FAILED and not self._stability.can_retry(task):
            return ()
        updated = task.with_feedback(feedback.quality_score, failed=True)
        updated = updated.with_status(
            RuntimeTaskStatus.FAILED
            if not self._stability.can_retry(updated)
            else RuntimeTaskStatus.PENDING
        )
        graph.update_task(updated)
        if updated.status == RuntimeTaskStatus.FAILED:
            return ()

        if feedback.failure_type == FailureType.DEPENDENCY_CONFLICT:
            graph.update_dependencies(task.task_id, tuple(sorted(task.dependencies)))
            graph.update_priority(task.task_id, task.priority + 3)
            return ()

        if feedback.failure_type == FailureType.PERFORMANCE_BOTTLENECK:
            graph.update_priority(task.task_id, task.priority + 2)
            return ()

        regenerated = self._split_task(task, feedback)
        if not regenerated or not self._stability.can_add_tasks(graph, len(regenerated)):
            graph.update_priority(task.task_id, task.priority + 1)
            return ()

        graph.mark_status(task.task_id, RuntimeTaskStatus.FAILED)
        previous_dependency = task.dependencies
        added: list[RuntimeTask] = []
        for index, generated in enumerate(regenerated):
            dependencies = previous_dependency if index == 0 else (added[-1].task_id,)
            candidate = generated.with_dependencies(dependencies)
            graph.add_task(candidate)
            added.append(candidate)
        for dependent in graph.tasks():
            if dependent.task_id in {task.task_id, *(item.task_id for item in added)}:
                continue
            if task.task_id in dependent.dependencies:
                graph.replace_dependency(task.task_id, added[-1].task_id)
                break
        return tuple(added)

    def _split_task(
        self,
        task: RuntimeTask,
        feedback: FeedbackSignal,
    ) -> tuple[RuntimeTask, ...]:
        reasons = feedback.violations or (
            feedback.failure_type.value if feedback.failure_type else "failure",
        )
        task_count = min(2, max(1, len(reasons)))
        generated: list[RuntimeTask] = []
        for index in range(1, task_count + 1):
            generated.append(
                RuntimeTask(
                    task_id=f"{task.task_id}.repair{index:02d}.{task.failure_count + 1}",
                    module=task.module,
                    priority=task.priority + 5 - index,
                    resource_estimate=task.resource_estimate,
                    failure_count=0,
                    last_feedback_score=feedback.quality_score,
                    title=f"{task.title or task.task_id} repair {index}",
                    parent_task_id=task.task_id,
                )
            )
        return tuple(generated)


class ParallelScheduler:
    """Compute adaptive parallel task groups each cycle."""

    def build_groups(
        self,
        ready_tasks: tuple[RuntimeTask, ...],
        system_state: SystemRuntimeState,
    ) -> tuple[tuple[str, ...], ...]:
        if not ready_tasks:
            return ()
        capacity = _effective_capacity(system_state)
        groups: list[list[RuntimeTask]] = []
        for task in ready_tasks:
            placed = False
            for group in groups:
                if self._fits(group, task, capacity):
                    group.append(task)
                    placed = True
                    break
            if not placed:
                groups.append([task])
        return tuple(tuple(task.task_id for task in group) for group in groups)

    def _fits(
        self,
        group: list[RuntimeTask],
        task: RuntimeTask,
        capacity: ResourceEstimate,
    ) -> bool:
        if any(existing.module == task.module for existing in group):
            return False
        event_load = sum(item.resource_estimate.event_load for item in group) + task.resource_estimate.event_load
        memory_mb = sum(item.resource_estimate.memory_mb for item in group) + task.resource_estimate.memory_mb
        latency_ms = sum(item.resource_estimate.latency_ms for item in group) + task.resource_estimate.latency_ms
        return (
            event_load <= capacity.event_load
            and memory_mb <= capacity.memory_mb
            and latency_ms <= capacity.latency_ms
        )


class RuntimeTaskScheduler:
    """Closed-loop adaptive runtime scheduler."""

    def __init__(
        self,
        graph: RuntimeTaskGraph | None = None,
        feedback_engine: FeedbackLoopEngine | None = None,
        stability_controller: StabilityController | None = None,
        parallel_scheduler: ParallelScheduler | None = None,
    ) -> None:
        self.graph = RuntimeTaskGraph() if graph is None else graph
        self.feedback_engine = feedback_engine or FeedbackLoopEngine()
        self.stability = stability_controller or StabilityController()
        self.replanner = ReplanningEngine(self.stability)
        self.parallel_scheduler = parallel_scheduler or ParallelScheduler()
        self._cycle_index = 0

    def submit_task(self, task: RuntimeTask) -> None:
        self.graph.add_task(task)

    def generate_task(
        self,
        module: TaskModule | str,
        title: str,
        dependencies: tuple[str, ...] = (),
        priority: int = 0,
        resource_estimate: ResourceEstimate | None = None,
    ) -> RuntimeTask:
        task_number = len(self.graph.tasks()) + 1
        task = RuntimeTask(
            task_id=f"runtime-task-{task_number:03d}",
            module=TaskModule(str(module)),
            priority=priority,
            dependencies=dependencies,
            resource_estimate=resource_estimate or ResourceEstimate(),
            title=title,
        )
        self.graph.add_task(task)
        return task

    def run_cycle(
        self,
        system_state: SystemRuntimeState,
        execution_results: tuple[TaskExecutionResult, ...] = (),
        reviewer_reports: dict[str, dict[str, Any]] | None = None,
    ) -> SchedulerCycleResult:
        self._cycle_index += 1
        reports = reviewer_reports or {}
        updated_task_ids: list[str] = []
        regenerated: list[RuntimeTask] = []
        priority_before = {task.task_id: task.priority for task in self.graph.tasks()}

        for result in sorted(execution_results, key=lambda item: item.task_id):
            task = self.graph.get(result.task_id)
            feedback = self.feedback_engine.evaluate(
                task=task,
                execution=result,
                reviewer_report=reports.get(result.task_id),
                system_state=system_state,
            )
            if result.success and feedback.failure_type is None:
                self.graph.update_task(
                    task.with_feedback(feedback.quality_score, failed=False).with_status(
                        RuntimeTaskStatus.COMPLETED
                    )
                )
                updated_task_ids.append(task.task_id)
                continue
            regenerated_tasks = self.replanner.replan(self.graph, task, feedback)
            regenerated.extend(regenerated_tasks)
            updated_task_ids.extend((task.task_id, *(item.task_id for item in regenerated_tasks)))

        if not self.graph.tasks():
            generated = self.generate_task(
                module=TaskModule.METRICS,
                title="Collect runtime feedback baseline",
                priority=0,
            )
            updated_task_ids.append(generated.task_id)

        self._adapt_priorities(system_state)
        ready = self.graph.ready_tasks()
        parallel_groups = self.parallel_scheduler.build_groups(ready, system_state)
        next_batch = tuple(
            self.graph.get(task_id)
            for group in parallel_groups[:1]
            for task_id in group
        )
        priority_adjustments = tuple(
            (task.task_id, task.priority)
            for task in self.graph.tasks()
            if priority_before.get(task.task_id) != task.priority
        )
        return SchedulerCycleResult(
            cycle_index=self._cycle_index,
            next_batch=next_batch,
            updated_task_ids=tuple(sorted(set(updated_task_ids))),
            priority_adjustments=priority_adjustments,
            parallel_groups=parallel_groups,
            regenerated_tasks=tuple(regenerated),
            stabilized=self.stability.stabilized(self.graph),
        )

    def _adapt_priorities(self, system_state: SystemRuntimeState) -> None:
        degraded = _is_degraded(system_state)
        for task in self.graph.tasks():
            if task.status != RuntimeTaskStatus.PENDING:
                continue
            next_priority = task.priority
            if task.last_feedback_score < 80:
                next_priority += 1
            if degraded and task.module in {TaskModule.METRICS, TaskModule.FRONTEND}:
                next_priority += 2
            if next_priority != task.priority:
                self.graph.update_priority(task.task_id, next_priority)


def _task_sort_key(task: RuntimeTask) -> tuple[int, int, str]:
    return (-task.priority, task.failure_count, task.task_id)


def _effective_capacity(system_state: SystemRuntimeState) -> ResourceEstimate:
    if _is_degraded(system_state):
        return ResourceEstimate(
            event_load=max(1, system_state.resource_capacity.event_load // 2),
            memory_mb=max(1, system_state.resource_capacity.memory_mb // 2),
            latency_ms=max(1, system_state.resource_capacity.latency_ms // 2),
        )
    return system_state.resource_capacity


def _is_degraded(system_state: SystemRuntimeState) -> bool:
    return (
        system_state.event_load > system_state.resource_capacity.event_load
        or system_state.memory_mb > system_state.resource_capacity.memory_mb
        or system_state.latency_ms > system_state.resource_capacity.latency_ms
    )


def _performance_items(items: tuple[str, ...], system_state: SystemRuntimeState) -> tuple[str, ...]:
    matches = list(_matching_items(items, ("performance", "bottleneck", "latency", "memory")))
    if _is_degraded(system_state):
        matches.append("runtime resource usage exceeds configured capacity")
    return tuple(sorted(set(matches)))


def _matching_items(items: tuple[str, ...], needles: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(
        sorted(
            item
            for item in items
            if any(needle in item.lower() for needle in needles)
        )
    )


def _require_int(value: int, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field_name} must be an int")


def _require_positive_int(value: int, field_name: str) -> None:
    _require_int(value, field_name)
    if value <= 0:
        raise ValueError(f"{field_name} must be positive")


def _require_non_negative_int(value: int, field_name: str) -> None:
    _require_int(value, field_name)
    if value < 0:
        raise ValueError(f"{field_name} must be non-negative")


def _require_score(value: int, field_name: str = "score") -> None:
    _require_int(value, field_name)
    if value < 0 or value > 100:
        raise ValueError(f"{field_name} must be in [0, 100]")
