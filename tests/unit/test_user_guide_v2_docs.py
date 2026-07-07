from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_user_guide_v2_covers_required_operator_workflows() -> None:
    guide = (PROJECT_ROOT / "docs/user_guide_v2.md").read_text(encoding="utf-8")

    for heading in (
        "## 1. Start The System",
        "## 2. Check Health",
        "## 3. Configure A Scenario",
        "## 4. Use The Console And Dashboard",
        "## 5. Export Results",
        "## 6. Collect Diagnostics",
        "## 7. Benchmark And Acceptance",
        "## 8. Current Model Boundaries",
    ):
        assert heading in guide

    for command_or_endpoint in (
        ".\\leo_twin_launcher.bat",
        ".\\scripts\\sees_launcher.ps1 status -JsonSummary",
        ".\\scripts\\smoke_runtime_health.ps1 -JsonSummary",
        ".\\scripts\\smoke_browser_acceptance.ps1 -JsonSummary",
        ".\\scripts\\collect_operator_diagnostics.ps1 -JsonSummary",
        "GET /scenario/user-config/schema",
        "POST /scenario/user-config/validate-text",
        "http://127.0.0.1:8765/runtime/export",
        "configs\\sees_control.yaml",
        "configs\\generated_full_system_demo.json",
    ):
        assert command_or_endpoint in guide


def test_user_guide_v2_covers_model_boundaries_and_contracts() -> None:
    guide = (PROJECT_ROOT / "docs/user_guide_v2.md").read_text(encoding="utf-8")

    for forbidden_or_boundary in (
        "no STK, EXATA, AFSIM, or DDS integration",
        "no packet-level simulation",
        "no RF propagation field solver",
        "no antenna pattern modeling",
        "no SGP4 orbital fidelity",
        "leo_twin.benchmark_scenario_matrix.v1",
        "leo_twin.model_verification_report_template.v1",
        "leo_twin.result_package_contract.v1",
    ):
        assert forbidden_or_boundary in guide
