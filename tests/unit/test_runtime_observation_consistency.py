from __future__ import annotations

from leo_twin.services.runtime_observation_consistency import (
    RUNTIME_OBSERVATION_CONSISTENCY_V1_ID,
    build_runtime_observation_consistency_v1,
)


def test_runtime_observation_consistency_reports_aligned_backend_views() -> None:
    status = _runtime_status()

    summary = build_runtime_observation_consistency_v1(status)

    assert summary["summary_id"] == RUNTIME_OBSERVATION_CONSISTENCY_V1_ID
    assert summary["source"] == "BACKEND_RUNTIME_STATUS"
    assert summary["consistency_status"] == "CONSISTENT"
    assert summary["passed_check_count"] == summary["check_count"]
    assert summary["failed_check_count"] == 0
    assert summary["waiting_check_count"] == 0
    assert summary["blocking_check_ids"] == ()
    assert summary["waiting_check_ids"] == ()
    assert summary["current_sim_time"] == 12.0
    assert summary["metrics_summary_observation_time_s"] == 12.0
    assert summary["kpi_time_series_tail_sim_time_s"] == 12.0
    assert summary["traffic_timeline_current_sim_time"] == 12.0
    assert summary["traffic_business_window_current_sim_time"] == 12.0
    assert summary["frontend_inference_required"] is False
    assert summary["packet_level_simulation"] is False
    assert str(summary["consistency_hash"]).startswith("sha256:")
    assert {
        "metrics_observation_time",
        "metrics_event_time_bounds",
        "event_count_alignment",
        "kpi_tail_time",
        "traffic_timeline_time",
        "traffic_business_window_time",
        "closure_readiness_time",
    } == {check["check_id"] for check in summary["checks"]}


def test_runtime_observation_consistency_reports_inconsistent_backend_views() -> None:
    status = _runtime_status()
    status["metrics_summary"] = {
        **status["metrics_summary"],
        "metrics_summary_observation_time_s": 8.0,
        "event_count": 99,
    }
    status["kpi_time_series_v1"] = {
        **status["kpi_time_series_v1"],
        "samples": ({"sim_time": 8.0},),
    }

    summary = build_runtime_observation_consistency_v1(status)

    assert summary["consistency_status"] == "INCONSISTENT"
    assert summary["failed_check_count"] == 3
    assert set(summary["blocking_check_ids"]) == {
        "metrics_observation_time",
        "event_count_alignment",
        "kpi_tail_time",
    }


def _runtime_status() -> dict[str, object]:
    return {
        "lifecycle_state": "RUNNING",
        "current_sim_time": 12.0,
        "processed_event_count": 42,
        "queued_event_count": 7,
        "runtime_duration_seconds": 120.0,
        "runtime_duration_reached": False,
        "metrics_summary": {
            "event_count": 40,
            "last_sim_time": 10.0,
            "metrics_summary_event_time_s": 10.0,
            "metrics_summary_observation_time_s": 12.0,
        },
        "kpi_time_series_v1": {
            "sample_count": 2,
            "samples": (
                {"sim_time": 0.0},
                {"sim_time": 12.0},
            ),
        },
        "traffic_request_timeline_v1": {
            "current_sim_time": 12.0,
        },
        "traffic_business_activity_window_v1": {
            "current_sim_time": 12.0,
        },
        "runtime_closure_readiness_v1": {
            "current_sim_time": 12.0,
            "closure_status": "WAITING_FOR_RUNTIME_COMPLETION",
        },
    }
