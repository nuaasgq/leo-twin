"""Deterministic review engine and input loading."""

from __future__ import annotations

import ast
import json
import re
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

from leo_twin.reviewer import (
    analyzer_architecture,
    analyzer_kernel,
    analyzer_scalability,
    analyzer_simulation,
    analyzer_tests,
)


SCORE_KEYS = (
    "kernel_integrity",
    "architecture",
    "simulation_semantics",
    "scalability",
    "test_quality",
)

ANALYZERS = (
    ("kernel_integrity", analyzer_kernel.analyze),
    ("architecture", analyzer_architecture.analyze),
    ("simulation_semantics", analyzer_simulation.analyze),
    ("scalability", analyzer_scalability.analyze),
    ("test_quality", analyzer_tests.analyze),
)

HARD_STOP_TERMS = {
    "external simulator import": ("stk", "exata", "glomosim", "afsim", "dds"),
    "packet-level simulation": ("packetlevel", "packet_level", "packet-level"),
    "real RF or antenna modeling": ("rf propagation", "antenna pattern"),
    "real orbital mechanics": ("sgp4", "astrodynamics"),
}
MULTI_EXEC_IMPORTS = {
    "threading",
    "multiprocessing",
    "concurrent.futures",
    "asyncio",
    "socket",
    "mpi4py",
    "ray",
    "dask",
}
TEXT_FILE_SUFFIXES = {".py", ".toml", ".yaml", ".yml", ".md", ".txt"}


def review_path(
    diff_path: str | Path,
    repository_root: str | Path | None = None,
    commit_message: str | None = None,
) -> dict[str, Any]:
    path = Path(diff_path)
    root = Path.cwd() if repository_root is None else Path(repository_root)
    if path.is_dir():
        files = _load_file_snapshot(path)
        return review_files(
            files,
            diff_text="",
            commit_message=commit_message,
            changed_files=sorted(files),
        )

    diff_text = path.read_text(encoding="utf-8")
    files = _load_file_snapshot(root)
    return review_files(
        files,
        diff_text=diff_text,
        commit_message=commit_message,
        changed_files=_parse_changed_files(diff_text),
    )


def review_text(
    diff_text: str,
    repository_root: str | Path | None = None,
    commit_message: str | None = None,
) -> dict[str, Any]:
    root = Path.cwd() if repository_root is None else Path(repository_root)
    return review_files(
        _load_file_snapshot(root),
        diff_text=diff_text,
        commit_message=commit_message,
        changed_files=_parse_changed_files(diff_text),
    )


def review_files(
    files: Mapping[str, str],
    diff_text: str = "",
    commit_message: str | None = None,
    changed_files: Iterable[str] = (),
) -> dict[str, Any]:
    normalized_files = {
        _normalize_path(path): text for path, text in sorted(files.items())
    }
    context = _build_context(
        normalized_files,
        diff_text,
        tuple(sorted(_normalize_path(path) for path in changed_files)),
        commit_message or "",
    )

    scores: dict[str, int] = {}
    violations: list[str] = []
    risks: list[str] = []
    required_fixes: list[str] = []
    auto_reject = False

    for score_key, analyzer in ANALYZERS:
        result = analyzer(context)
        scores[score_key] = int(result["score"])
        violations.extend(result["violations"])
        risks.extend(result["risks"])
        required_fixes.extend(result["required_fixes"])
        auto_reject = auto_reject or bool(result["auto_reject"])

    hard_stop_violations = _hard_stop_violations(context)
    if hard_stop_violations:
        violations.extend(hard_stop_violations)
        required_fixes.append("Remove hard-stop violations before merging.")
        auto_reject = True

    total_score = sum(scores[key] for key in SCORE_KEYS)
    if _has_unseeded_randomness(context):
        violations.append("Unseeded randomness detected.")
        required_fixes.append("Use a documented, explicitly seeded RNG.")
        total_score = max(0, total_score - 20)

    total_score = max(0, min(100, total_score))
    decision = "REJECT" if auto_reject else _decision_from_score(total_score)

    return {
        "decision": decision,
        "total_score": total_score,
        "scores": {key: scores[key] for key in SCORE_KEYS},
        "violations": _stable_unique(violations),
        "risks": _stable_unique(risks),
        "required_fixes": _stable_unique(required_fixes),
    }


def to_json(report: Mapping[str, Any]) -> str:
    return json.dumps(report, indent=2, sort_keys=True)


def summary(report: Mapping[str, Any]) -> str:
    return (
        f"LEO-Twin review: {report['decision']} "
        f"score={report['total_score']} "
        f"violations={len(report['violations'])} "
        f"risks={len(report['risks'])}"
    )


def _build_context(
    files: Mapping[str, str],
    diff_text: str,
    changed_files: tuple[str, ...],
    commit_message: str,
) -> dict[str, Any]:
    added_by_file = _parse_added_lines_by_file(diff_text)
    target_files = {
        path: text
        for path, text in files.items()
        if _is_simulation_target_file(path)
    }
    target_added_by_file = {
        path: text
        for path, text in added_by_file.items()
        if _is_simulation_target_file(path)
    }
    return {
        "files": dict(files),
        "target_files": target_files,
        "diff_text": diff_text,
        "changed_files": changed_files,
        "commit_message": commit_message,
        "added_by_file": added_by_file,
        "target_added_by_file": target_added_by_file,
    }


def _load_file_snapshot(root: Path) -> dict[str, str]:
    files: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file() or ".git" in path.parts:
            continue
        if path.suffix.lower() not in TEXT_FILE_SUFFIXES and path.name != "pyproject.toml":
            continue
        relative_path = _normalize_path(path.relative_to(root).as_posix())
        if _should_skip_snapshot_file(relative_path):
            continue
        try:
            files[relative_path] = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
    return files


def _should_skip_snapshot_file(path: str) -> bool:
    return (
        path.startswith(".pytest_cache/")
        or "/__pycache__/" in path
        or path.startswith("artifacts/")
        or path.startswith("outputs/")
        or path.startswith("runs/")
    )


def _parse_changed_files(diff_text: str) -> tuple[str, ...]:
    changed: set[str] = set()
    for line in diff_text.splitlines():
        if line.startswith("diff --git "):
            parts = line.split()
            if len(parts) >= 4:
                changed.add(_normalize_path(parts[3].removeprefix("b/")))
        elif line.startswith("+++ b/"):
            changed.add(_normalize_path(line[6:]))
    return tuple(sorted(path for path in changed if path and path != "/dev/null"))


def _parse_added_lines_by_file(diff_text: str) -> dict[str, str]:
    current_path = "__diff__"
    added: dict[str, list[str]] = {current_path: []}
    for line in diff_text.splitlines():
        if line.startswith("+++ b/"):
            current_path = _normalize_path(line[6:])
            added.setdefault(current_path, [])
            continue
        if line.startswith("diff --git "):
            parts = line.split()
            if len(parts) >= 4:
                current_path = _normalize_path(parts[3].removeprefix("b/"))
                added.setdefault(current_path, [])
            continue
        if line.startswith("+") and not line.startswith("+++"):
            added.setdefault(current_path, []).append(line[1:])
    return {
        path: "\n".join(lines)
        for path, lines in sorted(added.items())
        if lines and path != "/dev/null"
    }


def _hard_stop_violations(context: Mapping[str, Any]) -> list[str]:
    target_files = context["target_files"]
    target_added_by_file = context["target_added_by_file"]
    hard_stops: list[str] = []

    import_violations = _forbidden_imports(context["files"])
    hard_stops.extend(import_violations)

    scanned_text = "\n".join(text for _, text in sorted(target_files.items()))
    scanned_text += "\n" + "\n".join(
        text for _, text in sorted(target_added_by_file.items())
    )
    lowered = scanned_text.lower()
    compact = re.sub(r"[^a-z0-9]+", "", lowered)

    for label, terms in HARD_STOP_TERMS.items():
        if any(term in lowered or term in compact for term in terms):
            hard_stops.append(f"Hard-stop violation detected: {label}.")

    if _kernel_has_domain_logic(target_files.get("src/leo_twin/core/kernel.py", "")):
        hard_stops.append("Hard-stop violation detected: kernel contains domain logic.")

    return hard_stops


def _forbidden_imports(files: Mapping[str, str]) -> list[str]:
    violations: list[str] = []
    for path, text in sorted(files.items()):
        if not path.endswith(".py"):
            continue
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        for module_name in _imported_module_names(tree):
            root_name = module_name.split(".", 1)[0].lower()
            if root_name in {"stk", "exata", "glomosim", "afsim", "dds"}:
                violations.append(f"Hard-stop violation: {path} imports {module_name}.")
            if module_name in MULTI_EXEC_IMPORTS or root_name in MULTI_EXEC_IMPORTS:
                violations.append(
                    f"Hard-stop violation: {path} imports {module_name} for concurrent or distributed execution."
                )
    return violations


def _imported_module_names(tree: ast.AST) -> tuple[str, ...]:
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.append(node.module)
    return tuple(sorted(names))


def _has_unseeded_randomness(context: Mapping[str, Any]) -> bool:
    target_files = context["target_files"]
    target_added_by_file = context["target_added_by_file"]
    source = "\n".join(text for _, text in sorted(target_files.items()))
    source += "\n" + "\n".join(text for _, text in sorted(target_added_by_file.items()))
    if "random" not in source:
        return False
    unseeded_patterns = (
        "random.random(",
        "random.choice(",
        "random.shuffle(",
        "random.randint(",
        "random.randrange(",
    )
    return any(pattern in source for pattern in unseeded_patterns) and "Random(" not in source


def _kernel_has_domain_logic(kernel_text: str) -> bool:
    if not kernel_text:
        return False
    stripped = "\n".join(line.split("#", 1)[0] for line in kernel_text.splitlines())
    return bool(analyzer_kernel.DOMAIN_TERMS.search(stripped))


def _is_simulation_target_file(path: str) -> bool:
    normalized = _normalize_path(path)
    if normalized.startswith("src/leo_twin/reviewer/"):
        return False
    if normalized.startswith("src/leo_twin/sees/"):
        return False
    if normalized.startswith("tests/"):
        return False
    if normalized.startswith("docs/"):
        return False
    if normalized.startswith("examples/"):
        return True
    if normalized.startswith("src/leo_twin/") and normalized.endswith(".py"):
        return True
    return normalized == "pyproject.toml"


def _decision_from_score(total_score: int) -> str:
    if total_score >= 90:
        return "PASS"
    if total_score >= 75:
        return "MINOR_FIX"
    if total_score >= 60:
        return "MAJOR_REVISION"
    return "REJECT"


def _stable_unique(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def _normalize_path(path: str | Path) -> str:
    return str(path).replace("\\", "/").lstrip("./")
