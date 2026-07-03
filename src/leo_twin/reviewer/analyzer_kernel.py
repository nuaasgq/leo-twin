"""Kernel integrity analyzer."""

import ast
import re
from collections.abc import Mapping
from typing import Any


DOMAIN_TERMS = re.compile(
    r"\b(orbit|satellite|beam|network|route|routing|compute|task|flow)\b",
    re.IGNORECASE,
)


def analyze(context: Mapping[str, Any]) -> dict[str, Any]:
    files = context["files"]
    target_files = context["target_files"]
    kernel_text = files.get("src/leo_twin/core/kernel.py", "")
    queue_text = files.get("src/leo_twin/core/event_queue.py", "")
    score = 25
    violations: list[str] = []
    risks: list[str] = []
    required_fixes: list[str] = []
    auto_reject = False

    if "class SimulationKernel" not in kernel_text:
        return {
            "score": 0,
            "violations": ["SimulationKernel is missing."],
            "risks": [],
            "required_fixes": ["Implement SimulationKernel before review can pass."],
            "auto_reject": True,
        }

    imported_layers = _project_import_layers(kernel_text)
    forbidden_layers = sorted(imported_layers & {"models", "services", "adapters"})
    if forbidden_layers:
        auto_reject = True
        score = 0
        violations.append(
            "SimulationKernel imports forbidden layer(s): "
            + ", ".join(forbidden_layers)
            + "."
        )
        required_fixes.append("Remove domain-layer imports from the kernel.")

    stripped_kernel = _strip_comments(kernel_text)
    if DOMAIN_TERMS.search(stripped_kernel):
        auto_reject = True
        score = min(score, 5)
        violations.append("SimulationKernel appears to contain domain-specific logic.")
        required_fixes.append("Keep orbit, network, routing, compute, and flow logic out of the kernel.")

    if "EventQueue" not in kernel_text:
        score -= 6
        violations.append("SimulationKernel does not use EventQueue.")
        required_fixes.append("Dispatch events through EventQueue.")

    if "_current_time" not in kernel_text or "get_current_time" not in kernel_text:
        score -= 5
        violations.append("SimulationKernel does not expose centralized time state.")
        required_fixes.append("Keep simulation time centralized in SimulationKernel.")

    if not _has_deterministic_ordering(queue_text):
        score -= 7
        violations.append("EventQueue ordering rule is not structurally detectable.")
        required_fixes.append("Order events by sim_time, descending priority, and event_id.")

    time_mutators = [
        path
        for path, text in target_files.items()
        if path != "src/leo_twin/core/kernel.py"
        and re.search(r"\b(_current_time|current_time)\s*=", text)
    ]
    if time_mutators:
        score -= 6
        violations.append(
            "Simulation time appears to be modified outside the kernel: "
            + ", ".join(sorted(time_mutators))
            + "."
        )
        required_fixes.append("Move simulation time mutation back into SimulationKernel.")

    return {
        "score": max(0, min(25, score)),
        "violations": violations,
        "risks": risks,
        "required_fixes": required_fixes,
        "auto_reject": auto_reject,
    }


def _project_import_layers(source: str) -> set[str]:
    layers: set[str] = set()
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return layers

    for node in ast.walk(tree):
        module_name = ""
        if isinstance(node, ast.Import):
            for alias in node.names:
                module_name = alias.name
                layer = _layer_from_module(module_name)
                if layer:
                    layers.add(layer)
        elif isinstance(node, ast.ImportFrom) and node.module:
            module_name = node.module
            layer = _layer_from_module(module_name)
            if layer:
                layers.add(layer)
    return layers


def _layer_from_module(module_name: str) -> str | None:
    parts = module_name.split(".")
    if len(parts) >= 2 and parts[0] == "leo_twin":
        return parts[1]
    return None


def _strip_comments(source: str) -> str:
    return "\n".join(line.split("#", 1)[0] for line in source.splitlines())


def _has_deterministic_ordering(queue_text: str) -> bool:
    required_terms = ("heapq", "sim_time", "priority", "event_id")
    return all(term in queue_text for term in required_terms)
