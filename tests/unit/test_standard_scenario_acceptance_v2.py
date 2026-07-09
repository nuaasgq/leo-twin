from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from leo_twin.schema.config_loader import load_config
from leo_twin.services.benchmark_scenarios import (
    benchmark_scenario_by_id,
    benchmark_scenario_ids,
)
from leo_twin.services.standard_scenario_acceptance import (
    RESULT_PACKAGE_EVIDENCE_FILENAMES,
    STANDARD_SCENARIO_ACCEPTANCE_V2_ID,
    build_standard_scenario_acceptance_v2,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize("scenario_id", benchmark_scenario_ids())
def test_standard_scenario_acceptance_v2_matches_shipped_scenarios(
    scenario_id: str,
) -> None:
    scenario = benchmark_scenario_by_id(scenario_id, PROJECT_ROOT)
    config = load_config(PROJECT_ROOT / str(scenario["config_path"]))
    runtime_status = _runtime_status_for(scenario)

    first = build_standard_scenario_acceptance_v2(
        config,
        runtime_status,
        generated_config=_generated_config_for(scenario),
        project_root=PROJECT_ROOT,
    )
    second = build_standard_scenario_acceptance_v2(
        config,
        runtime_status,
        generated_config=_generated_config_for(scenario),
        project_root=PROJECT_ROOT,
    )

    assert first == second
    assert first["acceptance_id"] == STANDARD_SCENARIO_ACCEPTANCE_V2_ID
    assert first["current_scenario_id"] == scenario_id
    assert first["nearest_scenario_id"] == scenario_id
    assert first["matched_standard_scenario"] is True
    assert first["match_status"] == "EXACT_STANDARD_SCENARIO"
    assert first["acceptance_status"] == "PASS"
    assert first["missing_runtime_status_fields"] == ()
    assert first["packet_level_simulation"] is False
    assert first["frontend_inference_required"] is False
    assert "standard_scenario_acceptance_v2.json" in (
        first["result_package_evidence_filenames"]
    )
    assert first["result_package_evidence_filenames"] == (
        RESULT_PACKAGE_EVIDENCE_FILENAMES
    )
    assert first["acceptance_hash"].startswith("sha256:")


def test_standard_scenario_acceptance_v2_fails_missing_runtime_evidence() -> None:
    scenario = benchmark_scenario_by_id("small_demo_72sat", PROJECT_ROOT)
    config = load_config(PROJECT_ROOT / str(scenario["config_path"]))
    runtime_status = _runtime_status_for(scenario)
    runtime_status.pop("network_kpi_assurance_v2")

    evidence = build_standard_scenario_acceptance_v2(
        config,
        runtime_status,
        generated_config=_generated_config_for(scenario),
        project_root=PROJECT_ROOT,
    )

    assert evidence["current_scenario_id"] == "small_demo_72sat"
    assert evidence["matched_standard_scenario"] is True
    assert evidence["acceptance_status"] == "FAIL"
    assert evidence["missing_runtime_status_fields"] == (
        "network_kpi_assurance_v2",
    )
    coverage_gate = next(
        check
        for check in evidence["gate_checks"]
        if check["check_id"] == "runtime_status_field_coverage"
    )
    assert coverage_gate["status"] == "FAIL"


def test_standard_scenario_acceptance_v2_warns_for_custom_scenario() -> None:
    scenario = benchmark_scenario_by_id("small_demo_72sat", PROJECT_ROOT)
    config = load_config(PROJECT_ROOT / str(scenario["config_path"]))
    custom_config = replace(
        config,
        scenario=replace(config.scenario, satellite_count=73),
    )

    evidence = build_standard_scenario_acceptance_v2(
        custom_config,
        _runtime_status_for(scenario),
        generated_config=_generated_config_for(scenario),
        project_root=PROJECT_ROOT,
    )

    assert evidence["current_scenario_id"] == ""
    assert evidence["nearest_scenario_id"] == "small_demo_72sat"
    assert evidence["matched_standard_scenario"] is False
    assert evidence["match_status"] == "CUSTOM_OR_PARTIAL_SCENARIO"
    assert evidence["acceptance_status"] == "WARN"
    standard_gate = next(
        check
        for check in evidence["gate_checks"]
        if check["check_id"] == "standard_scenario_match"
    )
    assert standard_gate["status"] == "WARN"


def _runtime_status_for(scenario: dict[str, object]) -> dict[str, object]:
    return {
        "lifecycle_state": "INITIALIZED",
        "current_sim_time": 0.0,
        "processed_event_count": 0,
        "fidelity_summary": scenario["fidelity_summary"],
        "metrics_summary": {},
        "network_kpi_benchmark_validation_v1": {},
        "network_kpi_assurance_v2": {},
        "runtime_dashboard_kpi_v1": {},
        "runtime_closure_readiness_v1": {},
        "runtime_observation_consistency_v1": {},
        "business_request_lifecycle_v2": {},
        "compute_service_resource_evidence_v1": {},
        "user_configuration_closure_v2": {},
        "reproducibility_manifest_v1": {},
    }


def _generated_config_for(scenario: dict[str, object]) -> dict[str, object]:
    return {
        "backend_summary": {
            "derived_constellation_summary": scenario[
                "derived_constellation_summary"
            ],
            "traffic_demand_summary": scenario["traffic_demand_summary"],
            "compute_resource_summary": scenario["compute_resource_summary"],
        }
    }
