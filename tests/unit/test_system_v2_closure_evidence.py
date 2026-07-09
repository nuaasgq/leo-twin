from __future__ import annotations

import pytest

from leo_twin.services.system_v2_closure_evidence import (
    SYSTEM_V2_CLOSURE_EVIDENCE_V1_ID,
    build_system_v2_closure_evidence_v1,
)


def test_system_v2_closure_evidence_reports_sealed_demo_loop() -> None:
    first = build_system_v2_closure_evidence_v1(_sealed_runtime_status())
    second = build_system_v2_closure_evidence_v1(_sealed_runtime_status())

    assert first == second
    assert first["closure_id"] == SYSTEM_V2_CLOSURE_EVIDENCE_V1_ID
    assert first["source"] == "BACKEND_RUNTIME_STATUS"
    assert first["target"] == "INDUSTRIAL_V2_DEMO_CLOSURE_HANDOFF"
    assert first["closure_status"] == "SEALED"
    assert first["demo_loop_closed"] is True
    assert first["gate_count"] == 7
    assert first["passed_gate_count"] == 7
    assert first["warning_gate_count"] == 0
    assert first["waiting_gate_count"] == 0
    assert first["failed_gate_count"] == 0
    assert first["blocking_gate_ids"] == ()
    assert first["frontend_inference_required"] is False
    assert first["packet_level_simulation"] is False
    assert str(first["closure_hash"]).startswith("sha256:")
    assert {
        "configuration_closure",
        "executable_readiness",
        "observation_consistency",
        "runtime_result_closure",
        "standard_scenario_acceptance",
        "semantic_evidence_surfaces",
        "reproducibility_and_package_contract",
    } == {gate["gate_id"] for gate in first["gates"]}


def test_system_v2_closure_evidence_waits_for_runtime_result_closure() -> None:
    status = _sealed_runtime_status()
    status["lifecycle_state"] = "RUNNING"
    status["runtime_duration_reached"] = False
    status["runtime_closure_readiness_v1"] = {
        **status["runtime_closure_readiness_v1"],
        "closure_status": "RUNNING_COLLECTING_EVIDENCE",
        "result_ready": False,
        "failed_gate_count": 0,
        "blocking_gate_ids": ("runtime_terminal",),
    }

    evidence = build_system_v2_closure_evidence_v1(status)

    assert evidence["closure_status"] == "COLLECTING_EVIDENCE"
    assert evidence["demo_loop_closed"] is False
    assert evidence["waiting_gate_ids"] == ("runtime_result_closure",)
    gates = {gate["gate_id"]: gate for gate in evidence["gates"]}
    assert gates["runtime_result_closure"]["status"] == "WAIT"


def test_system_v2_closure_evidence_fails_missing_package_contract() -> None:
    status = _sealed_runtime_status()
    status["standard_scenario_acceptance_v2"] = {
        **status["standard_scenario_acceptance_v2"],
        "result_package_evidence_filenames": (
            "config_snapshot.json",
            "manifest.json",
        ),
    }

    evidence = build_system_v2_closure_evidence_v1(status)

    assert evidence["closure_status"] == "NOT_SEALED"
    assert evidence["demo_loop_closed"] is False
    assert evidence["blocking_gate_ids"] == (
        "reproducibility_and_package_contract",
    )
    gates = {gate["gate_id"]: gate for gate in evidence["gates"]}
    assert gates["reproducibility_and_package_contract"]["status"] == "FAIL"
    assert "standard scenario package evidence omits package_handoff_report_v1.md" in (
        gates["reproducibility_and_package_contract"]["issues"]
    )


def test_system_v2_closure_evidence_rejects_non_mapping_status() -> None:
    with pytest.raises(TypeError, match="runtime_status"):
        build_system_v2_closure_evidence_v1(object())  # type: ignore[arg-type]


def _sealed_runtime_status() -> dict[str, object]:
    return {
        "lifecycle_state": "COMPLETED",
        "current_sim_time": 120.0,
        "runtime_observation_sim_time": 120.0,
        "runtime_duration_seconds": 120.0,
        "runtime_duration_reached": True,
        "processed_event_count": 900,
        "queued_event_count": 0,
        "user_configuration_closure_v2": {
            "summary_id": "sees.user_configuration_closure.v2",
            "closure_status": "READY",
            "configuration_ready": True,
            "failed_gate_count": 0,
            "packet_level_simulation": False,
            "frontend_inference_required": False,
        },
        "v2_executable_readiness_v1": {
            "readiness_id": "leo_twin.v2_executable_readiness.v1",
            "readiness_status": "READY",
            "executable_ready": True,
            "failed_gate_count": 0,
            "packet_level_simulation": False,
            "frontend_inference_required": False,
        },
        "runtime_observation_consistency_v1": {
            "summary_id": "leo_twin.runtime_observation_consistency.v1",
            "consistency_status": "CONSISTENT",
            "failed_check_count": 0,
            "packet_level_simulation": False,
            "frontend_inference_required": False,
        },
        "runtime_closure_readiness_v1": {
            "summary_id": "leo_twin.runtime_closure_readiness.v1",
            "closure_status": "COMPLETED_RESULT_READY",
            "result_ready": True,
            "failed_gate_count": 0,
            "blocking_gate_ids": (),
            "packet_level_simulation": False,
            "frontend_inference_required": False,
        },
        "standard_scenario_acceptance_v2": {
            "acceptance_id": "leo_twin.standard_scenario_acceptance.v2",
            "acceptance_status": "PASS",
            "current_scenario_id": "small_demo_72sat",
            "result_package_evidence_filenames": (
                "config_snapshot.json",
                "manifest.json",
                "standard_scenario_acceptance_v2.json",
                "system_v2_closure_evidence_v1.json",
                "package_handoff_report_v1.md",
            ),
            "packet_level_simulation": False,
            "frontend_inference_required": False,
        },
        "network_kpi_assurance_v2": {
            "summary_id": "leo_twin.network_kpi_assurance.v2",
            "packet_level_simulation": False,
            "frontend_inference_required": False,
        },
        "business_request_lifecycle_v2": {
            "summary_id": "leo_twin.business_request_lifecycle.v2",
            "packet_level_simulation": False,
            "frontend_inference_required": False,
        },
        "compute_service_resource_evidence_v1": {
            "summary_id": "leo_twin.compute_service_resource_evidence.v1",
            "packet_level_simulation": False,
            "frontend_inference_required": False,
        },
        "user_service_request_summary_v2": {
            "summary_id": "leo_twin.runtime_user_service_request_summary.v2",
            "packet_level_simulation": False,
            "frontend_inference_required": False,
        },
        "compute_resource_pool_summary_v1": {
            "summary_id": "leo_twin.compute_resource_pool_summary.v1",
            "packet_level_simulation": False,
            "frontend_inference_required": False,
        },
        "reproducibility_manifest_v1": {
            "manifest_id": "leo_twin.runtime_reproducibility_manifest.v1",
            "runtime_state_hash": "sha256:runtime",
        },
    }
