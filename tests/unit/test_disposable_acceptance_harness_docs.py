from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path
from types import ModuleType

from leo_twin.schema.config import SEESConfig
from leo_twin.schema.config_loader import merge_config_update


PROJECT_ROOT = Path(__file__).resolve().parents[2]
HELPER_PATH = PROJECT_ROOT / "scripts" / "disposable_acceptance_payload.py"


def _load_helper() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "disposable_acceptance_payload",
        HELPER_PATH,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_disposable_acceptance_helper_builds_control_safe_payload() -> None:
    helper = _load_helper()
    plan = helper.build_scenario_plan(
        PROJECT_ROOT / "configs" / "acceptance" / "small_demo_72sat.yaml",
        PROJECT_ROOT,
    )

    assert plan["scenario_id"] == "small_demo_72sat"
    assert plan["expectations"]["satellite_count"] == 72
    assert plan["expectations"]["user_count"] == 1000
    assert plan["expectations"]["compute_node_count"] == 72
    benchmark = plan["benchmark_acceptance"]
    assert benchmark["matrix_id"] == "leo_twin.benchmark_scenario_matrix.v1"
    assert benchmark["binding_id"] == (
        "leo_twin.runtime_export_benchmark_acceptance_binding.v1"
    )
    assert benchmark["acceptance_gate_check_id"] == "benchmark_scenario_gate"
    assert "time_pressure_period_s" in benchmark["expected_range_metrics"]
    assert "network.time_pressure_period_s" in benchmark["expected_range_sources"]
    assert "route_provenance_trust_summary_v1" in benchmark[
        "runtime_status_required_fields"
    ]
    assert "config_snapshot.json" in benchmark["result_package_evidence_files"]
    payload = plan["initialize_payload"]
    assert payload["satellite_count"] == 72
    assert payload["application_protocol"] == "TASK_OFFLOAD_FLOW"
    assert payload["transport_protocol"] == "TCP"
    assert payload["orbit"]["orbit_update_mode"] == "PER_SATELLITE"
    assert payload["ui"]["visualization"]["satellites"] is True
    merge_config_update(SEESConfig(), payload)


def test_disposable_acceptance_standard_plan_covers_72_300_1200() -> None:
    helper = _load_helper()
    plan = helper.build_standard_plan(PROJECT_ROOT)

    assert plan["type"] == "DISPOSABLE_ACCEPTANCE_PLAN"
    assert plan["benchmark_matrix_id"] == "leo_twin.benchmark_scenario_matrix.v1"
    assert plan["benchmark_acceptance_binding_id"] == (
        "leo_twin.runtime_export_benchmark_acceptance_binding.v1"
    )
    assert plan["package_acceptance_report_id"] == (
        "leo_twin.runtime_export_package_acceptance_report.v1"
    )
    assert plan["acceptance_gate_check_id"] == "benchmark_scenario_gate"
    assert [scenario["scenario_id"] for scenario in plan["scenarios"]] == [
        "small_demo_72sat",
        "medium_demo_300sat",
        "scale_demo_1200sat_short",
    ]
    assert [
        scenario["expectations"]["satellite_count"]
        for scenario in plan["scenarios"]
    ] == [72, 300, 1200]
    assert all(
        scenario["benchmark_acceptance"]["acceptance_gate_check_id"]
        == "benchmark_scenario_gate"
        for scenario in plan["scenarios"]
    )
    assert all(
        "network.time_pressure_period_s"
        in scenario["benchmark_acceptance"]["expected_range_sources"]
        for scenario in plan["scenarios"]
    )
    assert "configs/sees_control.yaml" in plan["runtime_config_drift_paths"]
    assert (
        "configs/generated_full_system_demo.json"
        in plan["runtime_config_drift_paths"]
    )


def test_disposable_acceptance_scripts_are_documented_and_guard_runtime_configs() -> None:
    wrapper = PROJECT_ROOT / "disposable_acceptance_leo_twin.bat"
    script = PROJECT_ROOT / "scripts" / "run_disposable_acceptance.ps1"
    health_script = PROJECT_ROOT / "scripts" / "smoke_runtime_health.ps1"
    user_guide = PROJECT_ROOT / "docs" / "user_guide_v2.md"
    status_doc = PROJECT_ROOT / "docs" / "current_product_status.md"

    assert wrapper.exists()
    assert script.exists()
    wrapper_text = wrapper.read_text(encoding="utf-8")
    script_text = script.read_text(encoding="utf-8")
    assert "run_disposable_acceptance.ps1" in wrapper_text
    assert "small_demo_72sat.yaml" in script_text
    assert "medium_demo_300sat.yaml" in script_text
    assert "scale_demo_1200sat_short.yaml" in script_text
    assert "Backup-RuntimeConfigPaths" in script_text
    assert "Restore-RuntimeConfigPaths" in script_text
    assert "configs\\sees_control.yaml" in script_text
    assert "configs\\generated_full_system_demo.json" in script_text
    assert "sees_launcher.ps1" in script_text
    assert "restart" in script_text
    assert "$CommandTimeoutSeconds" in script_text
    assert "artifacts\\disposable_acceptance\\commands" in script_text
    assert "Start-Process" in script_text
    assert "$ControlUrl" in script_text
    assert "verify_product_acceptance.ps1" in script_text
    assert "/runtime/export" in script_text
    assert "$PlanOnly" in script_text
    assert "benchmark_acceptance" in script_text
    assert "benchmark_matrix_id" in script_text

    health_text = health_script.read_text(encoding="utf-8")
    assert "Get-ForbiddenRuntimeMarkerFindings" in health_text
    assert "forbidden_integrations" in health_text
    assert "outside an explicit boundary declaration" in health_text

    guide_text = user_guide.read_text(encoding="utf-8")
    status_text = status_doc.read_text(encoding="utf-8")
    assert ".\\disposable_acceptance_leo_twin.bat -PlanOnly -JsonSummary" in guide_text
    assert ".\\scripts\\run_disposable_acceptance.ps1 -SkipBuild" in guide_text
    assert "Disposable acceptance harness" in status_text


def test_disposable_acceptance_planonly_command_outputs_json() -> None:
    command = [
        "powershell",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(PROJECT_ROOT / "scripts" / "run_disposable_acceptance.ps1"),
        "-PlanOnly",
        "-JsonSummary",
    ]
    env = dict(os.environ)
    env["PYTHON"] = sys.executable
    completed = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
        env=env,
    )
    assert '"type":  "DISPOSABLE_ACCEPTANCE_PLAN"' in completed.stdout
    assert '"scenario_count":  3' in completed.stdout
    assert '"benchmark_matrix_id":  "leo_twin.benchmark_scenario_matrix.v1"' in (
        completed.stdout
    )
    assert "benchmark_scenario_gate" in completed.stdout
    assert "network.time_pressure_period_s" in completed.stdout
    assert "small_demo_72sat" in completed.stdout
    assert "scale_demo_1200sat_short" in completed.stdout
