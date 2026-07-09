from __future__ import annotations

import json

import pytest

from leo_twin.services.executable_readiness import (
    V2_EXECUTABLE_READINESS_V1_ID,
    build_v2_executable_readiness_v1,
)


def test_v2_executable_readiness_reports_ready_for_complete_status() -> None:
    first = build_v2_executable_readiness_v1(_complete_runtime_status())
    second = build_v2_executable_readiness_v1(_complete_runtime_status())

    assert first == second
    assert first["version"] == "v1"
    assert first["readiness_id"] == V2_EXECUTABLE_READINESS_V1_ID
    assert first["source"] == "BACKEND_RUNTIME_STATUS"
    assert first["target"] == "INDUSTRIAL_V2_EXECUTABLE_DEMO_LOOP"
    assert first["readiness_status"] == "READY"
    assert first["executable_ready"] is True
    assert first["gate_count"] == 8
    assert first["passed_gate_count"] == 8
    assert first["failed_gate_count"] == 0
    assert first["missing_required_gate_ids"] == ()
    assert first["frontend_inference_required"] is False
    assert first["packet_level_simulation"] is False
    assert str(first["readiness_hash"]).startswith("sha256:")
    gates = {gate["gate_id"]: gate for gate in first["gates"]}
    assert gates["traffic_business"]["status"] == "PASS"
    assert gates["traffic_business"]["required_paths"] == (
        "traffic_request_timeline_v1",
        "traffic_business_activity_window_v1",
    )
    assert gates["compute_resource"]["status"] == "PASS"
    assert json.loads(json.dumps(first, sort_keys=True))["readiness_id"] == (
        V2_EXECUTABLE_READINESS_V1_ID
    )


def test_v2_executable_readiness_reports_missing_required_fields() -> None:
    status = _complete_runtime_status()
    del status["traffic_business_activity_window_v1"]
    del status["network_kpi_formula_evidence_v1"]

    readiness = build_v2_executable_readiness_v1(status)
    gates = {gate["gate_id"]: gate for gate in readiness["gates"]}

    assert readiness["readiness_status"] == "NOT_READY"
    assert readiness["executable_ready"] is False
    assert readiness["failed_gate_count"] == 2
    assert readiness["missing_required_gate_ids"] == (
        "traffic_business",
        "network_kpi",
    )
    assert gates["traffic_business"]["missing_paths"] == (
        "traffic_business_activity_window_v1",
    )
    assert gates["network_kpi"]["missing_paths"] == (
        "network_kpi_formula_evidence_v1",
    )


def test_v2_executable_readiness_fails_boundary_violations() -> None:
    status = _complete_runtime_status()
    status["traffic_request_timeline_v1"] = {
        **status["traffic_request_timeline_v1"],
        "frontend_inference_required": True,
    }
    status["compute_resource_pool_summary_v1"] = {
        **status["compute_resource_pool_summary_v1"],
        "dimension_count": 6,
    }
    status["user_configuration_control_surface_evidence_v1"] = {
        **status["user_configuration_control_surface_evidence_v1"],
        "coverage_status": "DRIFT_DETECTED",
    }

    readiness = build_v2_executable_readiness_v1(status)
    gates = {gate["gate_id"]: gate for gate in readiness["gates"]}

    assert readiness["readiness_status"] == "NOT_READY"
    assert gates["traffic_business"]["issues"] == (
        "traffic_request_timeline_v1 requires frontend inference",
    )
    assert gates["compute_resource"]["issues"] == (
        "compute resource pool exposes fewer than 7 dimensions",
    )
    assert gates["configuration_contract"]["issues"] == (
        "configuration control surface coverage is not COMPLETE",
    )


def test_v2_executable_readiness_rejects_non_mapping_status() -> None:
    with pytest.raises(TypeError, match="runtime_status"):
        build_v2_executable_readiness_v1(object())  # type: ignore[arg-type]


def _complete_runtime_status() -> dict[str, object]:
    return {
        "configuration_surface_summary": {"schema_id": "sees.user_configuration.v2"},
        "user_configuration_control_surface_evidence_v1": {
            "coverage_status": "COMPLETE",
        },
        "lifecycle_state": "RUNNING",
        "current_sim_time": 12.0,
        "processed_event_count": 42,
        "queued_event_count": 5,
        "runtime_duration_seconds": 600.0,
        "runtime_completion_source": "SimulationSession",
        "stream_diagnostics_v1": {
            "event_stream": {"cursor": 1},
            "state_stream": {"cursor": 2},
        },
        "traffic_request_timeline_v1": {
            "summary_id": "leo_twin.traffic_request_timeline.v1",
            "packet_level_simulation": False,
            "frontend_inference_required": False,
        },
        "traffic_business_activity_window_v1": {
            "summary_id": "leo_twin.traffic_business_activity_window.v1",
            "packet_level_simulation": False,
            "frontend_inference_required": False,
        },
        "metrics_summary": {
            "network_quality_effective_throughput_mbps": 100.0,
            "network_quality_effective_latency_avg_s": 0.04,
            "network_quality_loss_proxy_rate": 0.01,
            "network_quality_effective_delay_variation_proxy_s": 0.002,
        },
        "network_kpi_provenance_v2": {
            "summary_id": "leo_twin.network_kpi_provenance.v2",
            "packet_level_simulation": False,
            "frontend_inference_required": False,
        },
        "network_kpi_formula_evidence_v1": {
            "summary_id": "leo_twin.network_kpi_formula_evidence.v1",
            "packet_level_simulation": False,
            "frontend_inference_required": False,
        },
        "compute_resource_pool_summary_v1": {
            "summary_id": "leo_twin.compute_resource_pool_summary.v1",
            "dimension_count": 7,
            "dimensions": ({"dimension": "cpu_gflops_fp32"},),
            "packet_level_simulation": False,
            "frontend_inference_required": False,
        },
        "user_request_summary_v1": {"summary_id": "user_request"},
        "user_service_request_summary_v2": {"summary_id": "user_service"},
        "satellite_service_summary_v1": {"summary_id": "satellite_service"},
        "node_detail_summary_v1": {"summary_id": "node_detail"},
        "fidelity_summary": {
            "orbit_update_mode": "PER_SATELLITE",
            "metrics_mode": "DETAILED",
            "space_link_mode": "DETAILED_SMALL_SCALE",
            "satellite_count": 72,
            "user_count": 1000,
        },
        "reproducibility_manifest_v1": {
            "manifest_id": "leo_twin.runtime_reproducibility_manifest.v1",
            "runtime_state_hash": "sha256:runtime",
        },
        "runtime_export_history_v1": {"export_count": 0},
    }
