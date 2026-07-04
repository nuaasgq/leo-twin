"""Pre-run scale safety checks for deterministic execution."""

from __future__ import annotations

import ast
from collections.abc import Iterable
from dataclasses import dataclass
from math import ceil, isfinite
from pathlib import Path


_EVENT_MEMORY_BYTES = 512
_SATELLITE_STATE_BYTES = 256
_USER_INDEX_BYTES = 128


@dataclass(frozen=True)
class ScaleConfig:
    """Logical scale configuration used by pre-run validation."""

    satellite_count: int
    user_count: int
    simulation_duration: float
    compute_node_count: int = 1
    tick_interval: float = 1.0
    average_events_per_entity_per_tick: float = 0.1
    partition_count: int = 100
    indexed_topology: bool = True
    incremental_updates: bool = True
    queue_based_compute: bool = True
    partitioned_execution: bool = True
    compression_enabled: bool = True
    frontend_batch_size: int = 1000
    snapshot_interval_events: int = 10_000
    scheduled_event_count: int = 0
    max_queue_depth: int = 100_000
    max_event_count: int = 1_000_000
    max_memory_bytes: int = 512 * 1024 * 1024
    event_log_limit: int = 100_000

    def __post_init__(self) -> None:
        _require_positive_int(self.satellite_count, "satellite_count")
        _require_positive_int(self.user_count, "user_count")
        _require_positive_int(self.compute_node_count, "compute_node_count")
        _require_positive_float(self.simulation_duration, "simulation_duration")
        _require_positive_float(self.tick_interval, "tick_interval")
        _require_non_negative_float(
            self.average_events_per_entity_per_tick,
            "average_events_per_entity_per_tick",
        )
        _require_positive_int(self.partition_count, "partition_count")
        _require_positive_int(self.frontend_batch_size, "frontend_batch_size")
        _require_positive_int(
            self.snapshot_interval_events,
            "snapshot_interval_events",
        )
        _require_non_negative_int(self.scheduled_event_count, "scheduled_event_count")
        _require_positive_int(self.max_queue_depth, "max_queue_depth")
        _require_positive_int(self.max_event_count, "max_event_count")
        _require_positive_int(self.max_memory_bytes, "max_memory_bytes")
        _require_positive_int(self.event_log_limit, "event_log_limit")


@dataclass(frozen=True)
class ScaleSafetyReport:
    """Deterministic result produced by the scale safety checker."""

    allowed: bool
    estimated_events: int
    estimated_memory_bytes: int
    estimated_interactions_per_tick: int
    estimated_queue_depth: int
    estimated_computation_per_tick: int
    violations: tuple[str, ...]
    risks: tuple[str, ...]


class ScaleSafetyChecker:
    """Block unsafe large-scale runs before the kernel is invoked."""

    def validate(
        self,
        config: ScaleConfig,
        source_paths: Iterable[str | Path] = (),
    ) -> ScaleSafetyReport:
        ticks = ceil(config.simulation_duration / config.tick_interval)
        entities = config.satellite_count + config.user_count
        estimated_events = ceil(
            ticks * entities * config.average_events_per_entity_per_tick
        ) + config.scheduled_event_count
        interactions_per_tick = ceil(
            config.satellite_count * (config.user_count / config.partition_count)
        )
        computation_per_tick = interactions_per_tick + config.compute_node_count
        queue_depth = ceil(
            entities
            * config.average_events_per_entity_per_tick
            / max(1, config.partition_count)
        )
        bounded_log_events = min(estimated_events, config.event_log_limit)
        estimated_memory = (
            bounded_log_events * _EVENT_MEMORY_BYTES
            + config.satellite_count * _SATELLITE_STATE_BYTES
            + config.user_count * _USER_INDEX_BYTES
        )

        violations: list[str] = []
        risks: list[str] = []
        if estimated_events > config.max_event_count:
            violations.append(
                "estimated event count exceeds configured max_event_count"
            )
        if estimated_memory > config.max_memory_bytes:
            violations.append(
                "estimated bounded memory exceeds configured max_memory_bytes"
            )
        if not config.indexed_topology:
            violations.append("network topology must be indexed before scale runs")
        if not config.incremental_updates:
            violations.append("scale runs require incremental update policy")
        if not config.queue_based_compute:
            violations.append("compute scheduling must be queue based")
        if not config.partitioned_execution:
            violations.append("scale runs require partitioned event execution")
        if not config.compression_enabled:
            violations.append("scale runs require semantic event compression")
        if config.frontend_batch_size < 500:
            violations.append("frontend websocket batch size is too small for scale runs")
        if config.snapshot_interval_events < 1000:
            violations.append("snapshot interval is too frequent for scale runs")
        if queue_depth > config.max_queue_depth:
            violations.append("estimated partition queue depth exceeds max_queue_depth")

        if interactions_per_tick > entities * 10:
            risks.append("module interaction density is high for one simulation tick")
        if computation_per_tick > config.max_event_count:
            risks.append("estimated computation per tick is near scale guard limits")

        patterns = self.detect_quadratic_patterns(source_paths)
        violations.extend(patterns)
        return ScaleSafetyReport(
            allowed=not violations,
            estimated_events=estimated_events,
            estimated_memory_bytes=estimated_memory,
            estimated_interactions_per_tick=interactions_per_tick,
            estimated_queue_depth=queue_depth,
            estimated_computation_per_tick=computation_per_tick,
            violations=tuple(sorted(violations)),
            risks=tuple(sorted(risks)),
        )

    def raise_if_unsafe(
        self,
        config: ScaleConfig,
        source_paths: Iterable[str | Path] = (),
    ) -> ScaleSafetyReport:
        report = self.validate(config, source_paths)
        if not report.allowed:
            joined = "; ".join(report.violations)
            raise RuntimeError(f"scale safety check failed: {joined}")
        return report

    def detect_quadratic_patterns(
        self,
        source_paths: Iterable[str | Path],
    ) -> tuple[str, ...]:
        findings: list[str] = []
        for source_path in _python_source_files(source_paths):
            tree = ast.parse(source_path.read_text(encoding="utf-8"))
            visitor = _PairwiseLoopVisitor(source_path)
            visitor.visit(tree)
            findings.extend(visitor.findings)
        return tuple(sorted(findings))


class _PairwiseLoopVisitor(ast.NodeVisitor):
    def __init__(self, source_path: Path) -> None:
        self._source_path = source_path
        self._loop_stack: list[str] = []
        self.findings: list[str] = []

    def visit_For(self, node: ast.For) -> None:  # noqa: N802
        iter_name = _iter_name(node.iter)
        if self._loop_stack and _looks_like_pairwise_scan(self._loop_stack[-1], iter_name):
            self.findings.append(
                f"{self._source_path}:{node.lineno}: nested satellite/user scan"
            )
        self._loop_stack.append(iter_name)
        self.generic_visit(node)
        self._loop_stack.pop()


def _iter_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Call):
        return _iter_name(node.func)
    if isinstance(node, ast.Subscript):
        return _iter_name(node.value)
    return type(node).__name__


def _python_source_files(source_paths: Iterable[str | Path]) -> tuple[Path, ...]:
    files: list[Path] = []
    for source_path in sorted(Path(path) for path in source_paths):
        if source_path.is_dir():
            files.extend(sorted(source_path.rglob("*.py")))
            continue
        if source_path.suffix == ".py":
            files.append(source_path)
    return tuple(files)


def _looks_like_pairwise_scan(outer_name: str, inner_name: str) -> bool:
    outer = outer_name.lower()
    inner = inner_name.lower()
    return (
        ("satellite" in outer or outer in {"sats", "satellites"})
        and ("user" in inner or "ground" in inner)
    ) or (
        ("user" in outer or "ground" in outer)
        and ("satellite" in inner or inner in {"sats", "satellites"})
    )


def _require_positive_int(value: int, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field_name} must be an int")
    if value <= 0:
        raise ValueError(f"{field_name} must be positive")


def _require_non_negative_int(value: int, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field_name} must be an int")
    if value < 0:
        raise ValueError(f"{field_name} must be non-negative")


def _require_positive_float(value: float, field_name: str) -> None:
    _require_non_negative_float(value, field_name)
    if value <= 0:
        raise ValueError(f"{field_name} must be positive")


def _require_non_negative_float(value: float, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field_name} must be an int or float")
    if not isfinite(value) or value < 0:
        raise ValueError(f"{field_name} must be finite and non-negative")
