"""Lightweight scalability pattern analyzer."""

import re
from collections.abc import Mapping
from typing import Any


PAIRWISE_TERMS = ("sat", "satellite", "user", "node", "beam", "link")


def analyze(context: Mapping[str, Any]) -> dict[str, Any]:
    target_files = context["target_files"]
    score = 15
    violations: list[str] = []
    risks: list[str] = []
    required_fixes: list[str] = []

    for path, text in sorted(target_files.items()):
        if _has_pairwise_loop(text):
            score -= 8
            violations.append(f"{path} appears to contain full pairwise iteration.")
            required_fixes.append("Avoid brute-force pairwise satellite/user or graph recomputation patterns.")

        if re.search(r"\brecompute_.*graph\b|\bbuild_.*graph\b", text, re.IGNORECASE):
            score -= 4
            risks.append(f"{path} contains graph recomputation naming patterns.")

        if "while True" in text and "schedule_event" in text:
            score -= 5
            violations.append(f"{path} may schedule unbounded event growth.")
            required_fixes.append("Bound event generation or document a deterministic termination condition.")

    return {
        "score": max(0, min(15, score)),
        "violations": violations,
        "risks": risks,
        "required_fixes": required_fixes,
        "auto_reject": False,
    }


def _has_pairwise_loop(source: str) -> bool:
    lines = [line.lower() for line in source.splitlines()]
    for index, line in enumerate(lines):
        if not _is_domain_loop(line):
            continue
        for nested in lines[index + 1 : index + 8]:
            if _is_domain_loop(nested):
                return True
    return False


def _is_domain_loop(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith("for ") and any(term in stripped for term in PAIRWISE_TERMS)
