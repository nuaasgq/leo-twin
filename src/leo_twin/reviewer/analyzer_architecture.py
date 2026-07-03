"""Layer dependency analyzer."""

import ast
from collections.abc import Mapping
from typing import Any


LAYERS = {"core", "schema", "models", "services", "adapters", "examples"}
ALLOWED_IMPORTS = {
    "schema": {"schema"},
    "core": {"core", "schema"},
    "models": {"models", "core", "schema"},
    "services": {"services", "models", "schema"},
    "adapters": {"adapters", "services", "models", "schema"},
    "examples": {"examples", "core", "schema", "models", "services"},
}


def analyze(context: Mapping[str, Any]) -> dict[str, Any]:
    target_files = context["target_files"]
    score = 20
    violations: list[str] = []
    risks: list[str] = []
    required_fixes: list[str] = []
    graph: dict[str, set[str]] = {layer: set() for layer in LAYERS}

    for path, text in sorted(target_files.items()):
        source_layer = _layer_from_path(path)
        if source_layer is None:
            continue

        try:
            imported_layers = _imported_project_layers(text)
        except SyntaxError:
            risks.append(f"Could not parse imports in {path}.")
            score -= 2
            continue

        for imported_layer in sorted(imported_layers):
            if imported_layer == source_layer:
                continue
            graph[source_layer].add(imported_layer)
            if imported_layer not in ALLOWED_IMPORTS[source_layer]:
                violations.append(
                    f"{path} imports {imported_layer}, violating {source_layer} layer rules."
                )
                required_fixes.append(
                    f"Remove the {source_layer} -> {imported_layer} dependency."
                )
                score -= 5

    cycles = _find_cycles(graph)
    if cycles:
        score = min(score, 5)
        for cycle in cycles:
            violations.append("Circular layer dependency detected: " + " -> ".join(cycle) + ".")
        required_fixes.append("Break circular layer dependencies.")

    return {
        "score": max(0, min(20, score)),
        "violations": violations,
        "risks": risks,
        "required_fixes": required_fixes,
        "auto_reject": False,
    }


def _layer_from_path(path: str) -> str | None:
    normalized = path.replace("\\", "/")
    prefix = "src/leo_twin/"
    if not normalized.startswith(prefix):
        return None
    parts = normalized[len(prefix) :].split("/")
    if parts and parts[0] in LAYERS:
        return parts[0]
    return None


def _imported_project_layers(source: str) -> set[str]:
    layers: set[str] = set()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        module_names: list[str] = []
        if isinstance(node, ast.Import):
            module_names = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module:
            module_names = [node.module]

        for module_name in module_names:
            parts = module_name.split(".")
            if len(parts) >= 2 and parts[0] == "leo_twin" and parts[1] in LAYERS:
                layers.add(parts[1])
    return layers


def _find_cycles(graph: Mapping[str, set[str]]) -> list[list[str]]:
    cycles: list[list[str]] = []
    visited: set[str] = set()
    active: list[str] = []

    def visit(layer: str) -> None:
        if layer in active:
            start = active.index(layer)
            cycles.append(active[start:] + [layer])
            return
        if layer in visited:
            return
        active.append(layer)
        for next_layer in sorted(graph[layer]):
            visit(next_layer)
        active.pop()
        visited.add(layer)

    for layer in sorted(graph):
        visit(layer)

    unique_cycles: list[list[str]] = []
    seen: set[tuple[str, ...]] = set()
    for cycle in cycles:
        key = tuple(cycle)
        if key not in seen:
            seen.add(key)
            unique_cycles.append(cycle)
    return unique_cycles
