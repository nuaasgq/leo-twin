"""Deterministic full-system task plan for LEO-Twin evolution."""

from __future__ import annotations

from dataclasses import dataclass

from leo_twin.sees.runtime_scheduler_v2 import (
    ResourceEstimate,
    RuntimeTask,
    RuntimeTaskGraph,
    TaskModule,
)


@dataclass(frozen=True)
class FullSystemTaskSpec:
    """Machine-readable full-system development task."""

    task_id: str
    title_zh: str
    module: TaskModule
    dependencies: tuple[str, ...] = ()
    priority: int = 0
    event_load: int = 1
    memory_mb: int = 1
    latency_ms: int = 1

    def to_runtime_task(self) -> RuntimeTask:
        return RuntimeTask(
            task_id=self.task_id,
            module=self.module,
            priority=self.priority,
            dependencies=self.dependencies,
            title=self.title_zh,
            resource_estimate=ResourceEstimate(
                event_load=self.event_load,
                memory_mb=self.memory_mb,
                latency_ms=self.latency_ms,
            ),
        )


def build_full_system_task_specs() -> tuple[FullSystemTaskSpec, ...]:
    """Return the deterministic full-system task DAG specification."""

    return (
        FullSystemTaskSpec(
            task_id="FS-000",
            title_zh="阶段治理升级与完整版边界确认",
            module=TaskModule.SYSTEM,
            priority=100,
        ),
        FullSystemTaskSpec(
            task_id="FS-010",
            title_zh="全域耦合契约冻结",
            module=TaskModule.SYSTEM,
            dependencies=("FS-000",),
            priority=95,
        ),
        FullSystemTaskSpec(
            task_id="FS-020",
            title_zh="轨道精细化模型第一版",
            module=TaskModule.ORBIT,
            dependencies=("FS-010",),
            priority=90,
            event_load=20,
            memory_mb=10,
            latency_ms=5,
        ),
        FullSystemTaskSpec(
            task_id="FS-030",
            title_zh="网络六层协议栈与链路画像第一版",
            module=TaskModule.NETWORK,
            dependencies=("FS-010",),
            priority=90,
            event_load=30,
            memory_mb=12,
            latency_ms=8,
        ),
        FullSystemTaskSpec(
            task_id="FS-040",
            title_zh="算力资源与任务生命周期第一版",
            module=TaskModule.COMPUTE,
            dependencies=("FS-010",),
            priority=88,
            event_load=18,
            memory_mb=10,
            latency_ms=6,
        ),
        FullSystemTaskSpec(
            task_id="FS-050",
            title_zh="三维仿真控制界面中文化与功能完善",
            module=TaskModule.FRONTEND,
            dependencies=("FS-010",),
            priority=85,
            event_load=16,
            memory_mb=16,
            latency_ms=8,
        ),
        FullSystemTaskSpec(
            task_id="FS-060",
            title_zh="独立数据态势面板前端",
            module=TaskModule.FRONTEND,
            dependencies=("FS-010",),
            priority=84,
            event_load=14,
            memory_mb=14,
            latency_ms=8,
        ),
        FullSystemTaskSpec(
            task_id="FS-070",
            title_zh="全域指标体系与数据面板输出",
            module=TaskModule.METRICS,
            dependencies=("FS-010",),
            priority=83,
            event_load=12,
            memory_mb=8,
            latency_ms=4,
        ),
        FullSystemTaskSpec(
            task_id="FS-080",
            title_zh="轨道驱动网络拓扑耦合",
            module=TaskModule.NETWORK,
            dependencies=("FS-020", "FS-030"),
            priority=82,
            event_load=35,
            memory_mb=14,
            latency_ms=8,
        ),
        FullSystemTaskSpec(
            task_id="FS-090",
            title_zh="网络状态驱动算力任务耦合",
            module=TaskModule.COMPUTE,
            dependencies=("FS-030", "FS-040"),
            priority=81,
            event_load=28,
            memory_mb=12,
            latency_ms=7,
        ),
        FullSystemTaskSpec(
            task_id="FS-100",
            title_zh="完整版全链路集成验证",
            module=TaskModule.SYSTEM,
            dependencies=("FS-050", "FS-060", "FS-070", "FS-080", "FS-090"),
            priority=80,
            event_load=40,
            memory_mb=20,
            latency_ms=10,
        ),
    )


def build_full_system_task_graph() -> RuntimeTaskGraph:
    """Build a deterministic runtime task graph for the full-system roadmap."""

    graph = RuntimeTaskGraph()
    for spec in build_full_system_task_specs():
        graph.add_task(spec.to_runtime_task())
    return graph
