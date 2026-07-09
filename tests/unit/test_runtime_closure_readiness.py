from __future__ import annotations

import json

import pytest

from leo_twin.services.runtime_closure_readiness import (
    RUNTIME_CLOSURE_READINESS_V1_ID,
    build_runtime_closure_readiness_v1,
)


def test_runtime_closure_readiness_reports_completed_result_ready() -> None:
    first = build_runtime_closure_readiness_v1(_closed_runtime_status())
    second = build_runtime_closure_readiness_v1(_closed_runtime_status())

    assert first == second
    assert first["version"] == "v1"
    assert first["summary_id"] == RUNTIME_CLOSURE_READINESS_V1_ID
    assert first["source"] == "BACKEND_RUNTIME_STATUS"
    assert first["target"] == "INDUSTRIAL_V2_RUNTIME_RESULT_CLOSURE"
    assert first["closure_status"] == "COMPLETED_RESULT_READY"
    assert first["result_ready"] is True
    assert first["gate_count"] == 6
    assert first["passed_gate_count"] == 6
    assert first["waiting_gate_count"] == 0
    assert first["failed_gate_count"] == 0
    assert first["blocking_gate_ids"] == ()
    assert first["frontend_inference_required"] is False
    assert first["packet_level_simulation"] is False
    assert str(first["closure_hash"]).startswith("sha256:")
    assert json.loads(json.dumps(first, sort_keys=True))["summary_id"] == (
        RUNTIME_CLOSURE_READINESS_V1_ID
    )


def test_runtime_closure_readiness_waits_before_runtime_starts() -> None:
    status = _closed_runtime_status()
    status.update(
        {
            "lifecycle_state": "INITIALIZED",
            "current_sim_time": 0.0,
            "runtime_duration_reached": False,
            "runtime_completion_reason": "",
            "runtime_kpi_movement_summary_v1": {
                "sample_count": 1,
                "sim_time_span_s": 0.0,
            },
            "network_kpi_dynamic_status_v1": {
                "dynamic_status": "INSUFFICIENT_SERIES",
            },
            "traffic_request_timeline_v1": {
                "request_count": 4,
                "state_counts": {
                    "PAST": 0,
                    "RECENTLY_ARRIVED": 0,
                    "PENDING": 4,
                },
            },
            "network_flow_lifecycle_summary_v1": {
                "active_flow_count": 0,
                "completed_flow_count": 0,
                "failed_flow_count": 0,
            },
            "service_lifecycle_stage_summary_v1": {
                "complete_service_count": 0,
                "incomplete_service_count": 0,
            },
        }
    )

    readiness = build_runtime_closure_readiness_v1(status)
    gates = {gate["gate_id"]: gate for gate in readiness["gates"]}

    assert readiness["closure_status"] == "NOT_STARTED"
    assert readiness["result_ready"] is False
    assert readiness["waiting_gate_count"] == 5
    assert gates["runtime_terminal"]["status"] == "WAIT"
    assert gates["kpi_series_evidence"]["status"] == "WAIT"
    assert gates["traffic_request_evidence"]["status"] == "WAIT"
    assert gates["network_flow_terminal"]["status"] == "WAIT"
    assert gates["communication_compute_service_closure"]["status"] == "WAIT"
    assert gates["compute_resource_vector"]["status"] == "PASS"


def test_runtime_closure_readiness_reports_completed_result_gaps() -> None:
    status = _closed_runtime_status()
    status["runtime_kpi_movement_summary_v1"] = {
        "sample_count": 1,
        "sim_time_span_s": 0.0,
    }
    status["network_kpi_dynamic_status_v1"] = {
        "dynamic_status": "INSUFFICIENT_SERIES",
    }
    status["network_flow_lifecycle_summary_v1"] = {
        "active_flow_count": 2,
        "completed_flow_count": 0,
        "failed_flow_count": 0,
    }
    status["service_lifecycle_stage_summary_v1"] = {
        "complete_service_count": 0,
        "incomplete_service_count": 2,
    }

    readiness = build_runtime_closure_readiness_v1(status)
    gates = {gate["gate_id"]: gate for gate in readiness["gates"]}

    assert readiness["closure_status"] == "COMPLETED_WITH_RESULT_GAPS"
    assert readiness["result_ready"] is False
    assert readiness["failed_gate_count"] == 3
    assert readiness["blocking_gate_ids"] == (
        "kpi_series_evidence",
        "network_flow_terminal",
        "communication_compute_service_closure",
    )
    assert gates["runtime_terminal"]["status"] == "PASS"
    assert gates["kpi_series_evidence"]["status"] == "FAIL"
    assert gates["network_flow_terminal"]["issues"] == (
        "no terminal network flow evidence",
        "network flows are still active",
    )
    assert gates["communication_compute_service_closure"]["issues"] == (
        "no complete communication-compute service trace",
        "service traces are still incomplete",
    )


def test_runtime_closure_readiness_rejects_non_mapping_status() -> None:
    with pytest.raises(TypeError, match="runtime_status"):
        build_runtime_closure_readiness_v1(object())  # type: ignore[arg-type]


def _closed_runtime_status() -> dict[str, object]:
    return {
        "lifecycle_state": "COMPLETED",
        "current_sim_time": 600.0,
        "runtime_duration_seconds": 600.0,
        "runtime_duration_reached": True,
        "runtime_completion_reason": "RUNTIME_DURATION_REACHED",
        "kpi_time_series_v1": {"sample_count": 3},
        "runtime_kpi_movement_summary_v1": {
            "sample_count": 3,
            "sim_time_span_s": 600.0,
        },
        "network_kpi_dynamic_status_v1": {
            "dynamic_status": "PARTIALLY_DYNAMIC",
        },
        "traffic_request_timeline_v1": {
            "request_count": 4,
            "state_counts": {
                "PAST": 4,
                "RECENTLY_ARRIVED": 0,
                "PENDING": 0,
            },
        },
        "traffic_business_activity_window_v1": {"request_count": 4},
        "network_flow_lifecycle_summary_v1": {
            "active_flow_count": 0,
            "completed_flow_count": 4,
            "failed_flow_count": 0,
        },
        "service_lifecycle_stage_summary_v1": {
            "complete_service_count": 4,
            "incomplete_service_count": 0,
        },
        "service_latency_history_v1": {"item_count": 4},
        "compute_resource_pool_summary_v1": {
            "dimension_count": 7,
            "dimensions": ({"dimension": "cpu_gflops_fp32"},),
        },
    }
