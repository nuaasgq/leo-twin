"""Deterministic executor interface for Codex-produced work units."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from leo_twin.sees.task_dag import EngineeringTask


@dataclass(frozen=True)
class FilePatch:
    """A deterministic file replacement patch."""

    path: str
    content: str


@dataclass(frozen=True)
class ExecutionResult:
    task_id: str
    changed_files: tuple[str, ...]
    status: str
    message: str


class CodexExecutor:
    """Apply deterministic patch plans generated outside the simulator."""

    def execute(self, task: EngineeringTask, workspace: str | Path) -> ExecutionResult:
        root = Path(workspace)
        changed_files: list[str] = []
        for patch in sorted(task.patch_plan, key=lambda item: item.path):
            target = _resolve_workspace_path(root, patch.path)
            target.parent.mkdir(parents=True, exist_ok=True)
            existing = target.read_text(encoding="utf-8") if target.exists() else None
            if existing != patch.content:
                target.write_text(patch.content, encoding="utf-8")
                changed_files.append(patch.path.replace("\\", "/"))

        return ExecutionResult(
            task_id=task.task_id,
            changed_files=tuple(changed_files),
            status="complete",
            message="deterministic patch plan applied",
        )


def _resolve_workspace_path(root: Path, path: str) -> Path:
    target = (root / path).resolve()
    root_resolved = root.resolve()
    if not str(target).startswith(str(root_resolved)):
        raise ValueError(f"patch path escapes workspace: {path!r}")
    return target
