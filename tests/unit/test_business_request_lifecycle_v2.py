from __future__ import annotations

from leo_twin.services.business_request_lifecycle import (
    BUSINESS_REQUEST_LIFECYCLE_V2_ID,
    build_business_request_lifecycle_v2,
)


def _timeline() -> dict[str, object]:
    return {
        "version": "v1",
        "current_sim_time": 12.0,
        "request_count": 3,
        "items": (
            {
                "request_id": "svc-00-compute_service-00000",
                "input_flow_id": "svc-00-compute_service-00000-input",
                "task_id": "svc-00-compute_service-00000-task",
                "output_flow_id": "svc-00-compute_service-00000-output",
                "source_id": "user-a",
                "target_id": "sat-a",
                "arrival_time": 2.0,
                "time_offset_s": -10.0,
                "request_state": "PAST",
                "traffic_class": "COMPUTE_SERVICE",
                "destination_type": "COMPUTE_NODE",
                "priority": 2,
                "input_data_mb": 12.0,
                "output_data_mb": 3.0,
                "has_compute_task": True,
                "has_output_flow": True,
                "service_state": "ARRIVED_BEFORE_RECENT_WINDOW",
            },
            {
                "request_id": "svc-01-compute_service-00000",
                "input_flow_id": "svc-01-compute_service-00000-input",
                "task_id": "svc-01-compute_service-00000-task",
                "output_flow_id": "svc-01-compute_service-00000-output",
                "source_id": "user-b",
                "target_id": "sat-b",
                "arrival_time": 8.0,
                "time_offset_s": -4.0,
                "request_state": "RECENTLY_ARRIVED",
                "traffic_class": "COMPUTE_SERVICE",
                "destination_type": "COMPUTE_NODE",
                "priority": 1,
                "input_data_mb": 8.0,
                "output_data_mb": 2.0,
                "has_compute_task": True,
                "has_output_flow": True,
                "service_state": "ARRIVED_IN_RECENT_WINDOW",
            },
            {
                "request_id": "svc-02-compute_service-00000",
                "input_flow_id": "svc-02-compute_service-00000-input",
                "task_id": "svc-02-compute_service-00000-task",
                "output_flow_id": "svc-02-compute_service-00000-output",
                "source_id": "user-c",
                "target_id": "sat-c",
                "arrival_time": 20.0,
                "time_offset_s": 8.0,
                "request_state": "PENDING",
                "traffic_class": "COMPUTE_SERVICE",
                "destination_type": "COMPUTE_NODE",
                "priority": 1,
                "input_data_mb": 6.0,
                "output_data_mb": 1.0,
                "has_compute_task": True,
                "has_output_flow": True,
                "service_state": "SCHEDULED",
            },
        ),
    }


def _service_history() -> dict[str, object]:
    return {
        "items": (
            {
                "task_id": "svc-00-compute_service-00000-task",
                "input_flow_id": "svc-00-compute_service-00000-input",
                "output_flow_id": "svc-00-compute_service-00000-output",
                "input_route_id": "route:input-0",
                "output_route_id": "route:output-0",
                "compute_node_id": "sat-a",
                "complete": True,
                "first_sample_sim_time": 4.0,
                "last_sample_sim_time": 10.0,
                "input_network_latency_s": 2.0,
                "compute_queue_delay_s": 0.5,
                "compute_execution_delay_s": 3.0,
                "output_network_latency_s": 1.0,
                "total_latency_s": 6.5,
                "component_timeline": (
                    {
                        "component": "input_network",
                        "sample_sim_time": 4.0,
                        "duration_s": 2.0,
                        "input_flow_id": "svc-00-compute_service-00000-input",
                        "route_id": "route:input-0",
                    },
                    {
                        "component": "compute_queue",
                        "sample_sim_time": 5.0,
                        "duration_s": 0.5,
                    },
                    {
                        "component": "compute_execution",
                        "sample_sim_time": 7.0,
                        "duration_s": 3.0,
                    },
                    {
                        "component": "output_network",
                        "sample_sim_time": 10.0,
                        "duration_s": 1.0,
                        "output_flow_id": "svc-00-compute_service-00000-output",
                        "route_id": "route:output-0",
                    },
                ),
            },
            {
                "task_id": "svc-01-compute_service-00000-task",
                "input_flow_id": "svc-01-compute_service-00000-input",
                "output_flow_id": "svc-01-compute_service-00000-output",
                "input_route_id": "route:input-1",
                "compute_node_id": "sat-b",
                "complete": False,
                "first_sample_sim_time": 8.0,
                "last_sample_sim_time": 11.0,
                "input_network_latency_s": 1.5,
                "compute_queue_delay_s": 0.25,
                "compute_execution_delay_s": 2.0,
                "component_timeline": (
                    {
                        "component": "input_network",
                        "sample_sim_time": 8.0,
                        "duration_s": 1.5,
                    },
                    {
                        "component": "compute_execution",
                        "sample_sim_time": 11.0,
                        "duration_s": 2.0,
                    },
                ),
            },
        ),
    }


def test_business_request_lifecycle_v2_is_backend_owned_and_deterministic() -> None:
    first = build_business_request_lifecycle_v2(
        _timeline(),
        _service_history(),
        current_sim_time=12.0,
    )
    second = build_business_request_lifecycle_v2(
        _timeline(),
        _service_history(),
        current_sim_time=12.0,
    )

    assert first == second
    assert first["version"] == "v2"
    assert first["summary_id"] == BUSINESS_REQUEST_LIFECYCLE_V2_ID
    assert first["source"] == "traffic_request_timeline_v1 + service_latency_history_v1"
    assert first["packet_level_simulation"] is False
    assert first["frontend_inference_required"] is False
    assert first["request_count"] == 3
    assert first["timeline_window_request_count"] == 3
    assert first["completed_request_count"] == 1
    assert first["active_request_count"] == 1
    assert first["pending_request_count"] == 1
    assert first["summary_hash"].startswith("sha256:")


def test_business_request_lifecycle_v2_reports_completed_compute_service() -> None:
    summary = build_business_request_lifecycle_v2(
        _timeline(),
        _service_history(),
        current_sim_time=12.0,
    )

    item = summary["items"][0]
    assert item["request_id"] == "svc-00-compute_service-00000"
    assert item["lifecycle_state"] == "COMPLETED"
    assert item["current_stage"] == "complete"
    assert item["observed_complete"] is True
    assert item["observed_stage_count"] == 4
    assert item["observed_total_latency_s"] == 6.5
    assert item["input_network_latency_s"] == 2.0
    assert item["compute_queue_delay_s"] == 0.5
    assert item["compute_execution_delay_s"] == 3.0
    assert item["output_network_latency_s"] == 1.0
    assert item["compute_node_id"] == "sat-a"
    assert item["detail_hash"].startswith("sha256:")


def test_business_request_lifecycle_v2_reports_partial_and_pending_states() -> None:
    summary = build_business_request_lifecycle_v2(
        _timeline(),
        _service_history(),
        current_sim_time=12.0,
    )

    partial = summary["items"][1]
    pending = summary["items"][2]

    assert partial["lifecycle_state"] == "COMPUTE_EXECUTION"
    assert partial["observed_execution_state"] == "OBSERVED_IN_PROGRESS"
    assert partial["observed_complete"] is False
    assert partial["observed_stage_count"] == 3
    assert partial["pending_stage_count"] == 1
    assert pending["lifecycle_state"] == "PENDING"
    assert pending["observed_execution_state"] == "NOT_OBSERVED"
    assert pending["observed_stage_count"] == 0


def test_business_request_lifecycle_v2_supports_cursor_and_query() -> None:
    summary = build_business_request_lifecycle_v2(
        _timeline(),
        _service_history(),
        current_sim_time=12.0,
        cursor=0,
        limit=1,
        query="user-b",
    )

    assert summary["filter_applied"] is True
    assert summary["unfiltered_window_request_count"] == 3
    assert summary["item_count"] == 1
    assert summary["has_more"] is False
    assert summary["items"][0]["source_id"] == "user-b"
