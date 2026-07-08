from __future__ import annotations

from leo_twin.services.network_flow_lifecycle_summary import (
    NETWORK_FLOW_LIFECYCLE_SUMMARY_V1_ID,
    build_network_flow_lifecycle_summary_v1,
)


def test_network_flow_lifecycle_summary_reports_active_window() -> None:
    summary = build_network_flow_lifecycle_summary_v1(
        {
            "network_flow_lifecycle_model": "ROUTE_UPDATE_TO_FLOW_COMPLETE_WINDOW",
            "network_flow_lifecycle_source": "BACKEND_METRICS_COLLECTOR",
            "network_flow_lifecycle_packet_level_simulation": False,
            "network_flow_lifecycle_active_flow_count": 3,
            "network_flow_lifecycle_active_available_flow_count": 2,
            "network_flow_lifecycle_active_blocked_flow_count": 1,
            "network_flow_lifecycle_active_demand_mbps": 75.0,
            "network_flow_lifecycle_active_capacity_mbps": 120.0,
            "network_flow_lifecycle_active_latency_avg_s": 0.08,
            "network_flow_lifecycle_oldest_active_age_s": 4.5,
            "network_flow_lifecycle_completed_flow_count": 5,
            "network_flow_lifecycle_successful_flow_count": 4,
            "network_flow_lifecycle_failed_flow_count": 1,
        }
    )

    assert summary["version"] == "v1"
    assert summary["summary_id"] == NETWORK_FLOW_LIFECYCLE_SUMMARY_V1_ID
    assert summary["source"] == "METRICS_SUMMARY_NETWORK_FLOW_LIFECYCLE_FIELDS"
    assert summary["metrics_source"] == "BACKEND_METRICS_COLLECTOR"
    assert summary["packet_level_simulation"] is False
    assert summary["frontend_inference_required"] is False
    assert summary["active_flow_count"] == 3
    assert summary["active_available_flow_count"] == 2
    assert summary["active_blocked_flow_count"] == 1
    assert summary["active_demand_mbps"] == 75.0
    assert summary["active_capacity_mbps"] == 120.0
    assert summary["active_latency_avg_s"] == 0.08
    assert summary["oldest_active_age_s"] == 4.5
    assert summary["completed_flow_count"] == 5
    assert summary["successful_flow_count"] == 4
    assert summary["failed_flow_count"] == 1
    assert summary["lifecycle_status"] == "ACTIVE_WITH_NETWORK_WAIT"
    assert summary["summary_hash"].startswith("sha256:")


def test_network_flow_lifecycle_summary_reports_idle_and_completed_status() -> None:
    idle = build_network_flow_lifecycle_summary_v1({})
    completed = build_network_flow_lifecycle_summary_v1(
        {
            "network_flow_lifecycle_completed_flow_count": 2,
            "network_flow_lifecycle_successful_flow_count": 2,
            "network_flow_lifecycle_failed_flow_count": 0,
        }
    )
    failed = build_network_flow_lifecycle_summary_v1(
        {
            "network_flow_lifecycle_completed_flow_count": 2,
            "network_flow_lifecycle_successful_flow_count": 1,
            "network_flow_lifecycle_failed_flow_count": 1,
        }
    )

    assert idle["lifecycle_status"] == "IDLE_NO_FLOW_SAMPLE"
    assert completed["lifecycle_status"] == "COMPLETED"
    assert failed["lifecycle_status"] == "COMPLETED_WITH_FAILURES"