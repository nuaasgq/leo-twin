"""Simulation semantics analyzer."""

import ast
import re
from collections.abc import Mapping
from typing import Any


TIME_SOURCE_PATTERN = re.compile(r"\b(time\.time|time\.sleep|datetime\.now|datetime\.utcnow)\b")


def analyze(context: Mapping[str, Any]) -> dict[str, Any]:
    target_files = context["target_files"]
    files = context["files"]
    score = 20
    violations: list[str] = []
    risks: list[str] = []
    required_fixes: list[str] = []

    if "class SimEvent" not in files.get("src/leo_twin/schema/sim_event.py", ""):
        score -= 5
        violations.append("SimEvent data structure is missing.")
        required_fixes.append("Define SimEvent before adding simulation behavior.")

    module_text = files.get("src/leo_twin/core/simulation_module.py", "")
    if "on_event" not in module_text or "schedule_event" not in _all_target_text(target_files):
        score -= 5
        violations.append("Event-driven module interaction is not structurally detectable.")
        required_fixes.append("Modules must interact through on_event and kernel.schedule_event().")

    for path, text in sorted(target_files.items()):
        if TIME_SOURCE_PATTERN.search(text):
            score -= 4
            violations.append(f"{path} uses wall-clock time.")
            required_fixes.append("Remove wall-clock time from simulation logic.")

        if path != "src/leo_twin/core/kernel.py" and _mutates_time_name(text):
            score -= 5
            violations.append(f"{path} appears to mutate simulation time outside the kernel.")
            required_fixes.append("Keep time mutation inside SimulationKernel only.")

        if _has_top_level_mutable_state(path, text):
            score -= 3
            violations.append(f"{path} defines top-level mutable state.")
            required_fixes.append("Move mutable state into explicit kernel/module instances.")

    if "while not self._event_queue.is_empty()" not in files.get(
        "src/leo_twin/core/kernel.py",
        "",
    ):
        score -= 3
        risks.append("Kernel event loop pattern is not directly recognizable.")

    return {
        "score": max(0, min(20, score)),
        "violations": violations,
        "risks": risks,
        "required_fixes": required_fixes,
        "auto_reject": False,
    }


def _all_target_text(target_files: Mapping[str, str]) -> str:
    return "\n".join(text for _, text in sorted(target_files.items()))


def _has_top_level_mutable_state(path: str, source: str) -> bool:
    if not path.endswith(".py"):
        return False
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return False

    for node in tree.body:
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        target_names = {_target_name(target) for target in targets}
        if "__all__" in target_names:
            continue
        value = node.value
        if isinstance(value, (ast.List, ast.Dict, ast.Set)):
            return True
    return False


def _mutates_time_name(source: str) -> bool:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return False
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            if any(_target_name(target) in {"sim_time", "current_time"} for target in node.targets):
                return True
        elif isinstance(node, ast.AugAssign):
            if _target_name(node.target) in {"sim_time", "current_time"}:
                return True
    return False


def _target_name(target: ast.AST) -> str:
    if isinstance(target, ast.Name):
        return target.id
    return ""
