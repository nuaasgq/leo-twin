"""Test quality analyzer."""

from collections.abc import Mapping
from typing import Any


def analyze(context: Mapping[str, Any]) -> dict[str, Any]:
    files = context["files"]
    test_files = {
        path: text
        for path, text in files.items()
        if path.startswith("tests/") and path.endswith(".py")
    }
    score = 20
    violations: list[str] = []
    risks: list[str] = []
    required_fixes: list[str] = []

    if not test_files:
        return {
            "score": 0,
            "violations": ["No pytest tests were found."],
            "risks": [],
            "required_fixes": ["Add deterministic tests before review can pass."],
            "auto_reject": False,
        }

    combined = "\n".join(text for _, text in sorted(test_files.items()))
    has_unit = any(path.startswith("tests/unit/test_") for path in test_files)
    has_integration = any(path.startswith("tests/integration/test_") for path in test_files)
    has_scale = any(path.startswith("tests/scale/test_") for path in test_files)
    has_determinism = _has_determinism_test(combined)
    has_kernel_tests = "SimulationKernel" in combined and "EventQueue" in combined

    if not has_unit:
        score -= 6
        violations.append("Unit tests are missing.")
        required_fixes.append("Add unit tests for changed behavior.")
    if not has_determinism:
        score -= 8
        violations.append("Determinism verification is missing.")
        required_fixes.append("Add same-seed or repeated-output determinism tests.")
    if not has_integration:
        score -= 3
        risks.append("Integration tests are missing.")
    if not has_scale:
        score -= 2
        risks.append("Scale tests are missing.")
    if not has_kernel_tests:
        score -= 4
        risks.append("Kernel behavior coverage is not detected in tests.")

    return {
        "score": max(0, min(20, score)),
        "violations": violations,
        "risks": risks,
        "required_fixes": required_fixes,
        "auto_reject": False,
    }


def _has_determinism_test(test_text: str) -> bool:
    lowered = test_text.lower()
    return (
        "determin" in lowered
        or "same seed" in lowered
        or "random(" in lowered
        or "random.random(" in lowered
    ) and ("==" in test_text or "assert" in lowered)
