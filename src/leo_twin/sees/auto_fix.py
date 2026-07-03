"""Deterministic minimal auto-fix engine."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from leo_twin.reviewer.reviewer_engine import review_path


FORBIDDEN_IMPORT_ROOTS = {
    "stk",
    "exata",
    "glomosim",
    "afsim",
    "dds",
    "threading",
    "multiprocessing",
    "asyncio",
    "socket",
}
RANDOM_REPLACEMENTS = {
    "random.random(": "random.Random(0).random(",
    "random.choice(": "random.Random(0).choice(",
    "random.shuffle(": "random.Random(0).shuffle(",
    "random.randint(": "random.Random(0).randint(",
    "random.randrange(": "random.Random(0).randrange(",
}


@dataclass(frozen=True)
class FixAction:
    path: str
    description: str


@dataclass(frozen=True)
class FixPlan:
    actions: tuple[FixAction, ...]


@dataclass(frozen=True)
class AutoFixResult:
    final_report: dict[str, Any]
    iterations: int
    applied_actions: tuple[FixAction, ...]
    history: tuple[dict[str, Any], ...]


class AutoFixEngine:
    """Apply deterministic safe fixes and re-run review up to a bounded limit."""

    def build_fix_plan(self, workspace: str | Path, report: dict[str, Any]) -> FixPlan:
        root = Path(workspace)
        actions: list[FixAction] = []
        if any("Unseeded randomness" in item for item in report["violations"]):
            for path in _python_files(root):
                text = path.read_text(encoding="utf-8")
                if any(pattern in text for pattern in RANDOM_REPLACEMENTS):
                    actions.append(
                        FixAction(
                            path=_relative_path(root, path),
                            description="replace unseeded random calls with random.Random(0)",
                        )
                    )

        if any("Hard-stop violation" in item for item in report["violations"]):
            for path in _python_files(root):
                text = path.read_text(encoding="utf-8")
                if _contains_forbidden_import_line(text):
                    actions.append(
                        FixAction(
                            path=_relative_path(root, path),
                            description="remove forbidden import lines",
                        )
                    )
        return FixPlan(actions=tuple(_stable_unique_actions(actions)))

    def apply_fix_plan(self, workspace: str | Path, plan: FixPlan) -> tuple[FixAction, ...]:
        root = Path(workspace)
        applied: list[FixAction] = []
        for action in plan.actions:
            target = _resolve_workspace_path(root, action.path)
            original = target.read_text(encoding="utf-8")
            fixed = _apply_text_fixes(original)
            if fixed != original:
                target.write_text(fixed, encoding="utf-8")
                applied.append(action)
        return tuple(applied)

    def fix_until_passes(
        self,
        workspace: str | Path,
        max_iterations: int = 3,
    ) -> AutoFixResult:
        root = Path(workspace)
        history: list[dict[str, Any]] = []
        applied_actions: list[FixAction] = []
        report = review_path(root, repository_root=root)

        for iteration in range(max_iterations):
            history.append(report)
            if report["decision"] == "PASS":
                return AutoFixResult(
                    final_report=report,
                    iterations=iteration,
                    applied_actions=tuple(applied_actions),
                    history=tuple(history),
                )

            plan = self.build_fix_plan(root, report)
            if not plan.actions:
                break
            applied = self.apply_fix_plan(root, plan)
            applied_actions.extend(applied)
            if not applied:
                break
            report = review_path(root, repository_root=root)

        history.append(report)
        return AutoFixResult(
            final_report=report,
            iterations=min(len(history) - 1, max_iterations),
            applied_actions=tuple(applied_actions),
            history=tuple(history),
        )


def _python_files(root: Path) -> tuple[Path, ...]:
    return tuple(
        sorted(
            path
            for path in root.rglob("*.py")
            if ".git" not in path.parts and "__pycache__" not in path.parts
        )
    )


def _contains_forbidden_import_line(text: str) -> bool:
    return any(_is_forbidden_import_line(line) for line in text.splitlines())


def _apply_text_fixes(text: str) -> str:
    lines = [
        line
        for line in text.splitlines()
        if not _is_forbidden_import_line(line)
    ]
    fixed = "\n".join(lines)
    if text.endswith("\n"):
        fixed += "\n"
    for pattern, replacement in RANDOM_REPLACEMENTS.items():
        fixed = fixed.replace(pattern, replacement)
    return fixed


def _is_forbidden_import_line(line: str) -> bool:
    stripped = line.strip()
    match = re.match(r"(from|import)\s+([A-Za-z0-9_\.]+)", stripped)
    if not match:
        return False
    root = match.group(2).split(".", 1)[0].lower()
    return root in FORBIDDEN_IMPORT_ROOTS


def _stable_unique_actions(actions: list[FixAction]) -> list[FixAction]:
    seen: set[tuple[str, str]] = set()
    result: list[FixAction] = []
    for action in actions:
        key = (action.path, action.description)
        if key in seen:
            continue
        seen.add(key)
        result.append(action)
    return result


def _relative_path(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def _resolve_workspace_path(root: Path, path: str) -> Path:
    target = (root / path).resolve()
    root_resolved = root.resolve()
    if not str(target).startswith(str(root_resolved)):
        raise ValueError(f"fix path escapes workspace: {path!r}")
    return target
