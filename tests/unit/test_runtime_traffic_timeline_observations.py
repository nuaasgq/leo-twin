from __future__ import annotations

from examples.integration_demo.control_plane import _merge_traffic_timeline_observations


def test_traffic_timeline_observation_merge_joins_service_trace_ids() -> None:
    timeline = {
        "version": "v1",
        "items": (
            {
                "request_id": "service-001",
                "input_flow_id": "service-001-input",
                "task_id": "service-001-task",
                "output_flow_id": "service-001-output",
            },
            {
                "request_id": "service-002",
                "input_flow_id": "service-002-input",
                "task_id": "service-002-task",
                "output_flow_id": "service-002-output",
            },
        ),
    }
    service_history = {
        "items": (
            {
                "task_id": "service-001-task",
                "input_flow_id": "service-001-input",
                "output_flow_id": "service-001-output",
                "complete": True,
                "total_latency_s": 7.4,
                "last_sample_sim_time": 12.0,
                "component_timeline": (
                    {"component": "input_network"},
                    {"component": "total"},
                ),
            },
        )
    }

    merged = _merge_traffic_timeline_observations(timeline, service_history)
    first, second = merged["items"]

    assert merged["observation_source"] == "service_latency_history_v1"
    assert merged["observation_model"] == "PLANNED_REQUEST_WITH_SERVICE_TRACE_JOIN"
    assert merged["observation_packet_level_simulation"] is False
    assert merged["observed_item_count"] == 1
    assert merged["completed_item_count"] == 1
    assert merged["running_item_count"] == 0
    assert merged["not_observed_item_count"] == 1
    assert first["observed_execution_state"] == "COMPLETED"
    assert first["observed_complete"] is True
    assert first["observed_task_id"] == "service-001-task"
    assert first["observed_input_flow_id"] == "service-001-input"
    assert first["observed_output_flow_id"] == "service-001-output"
    assert first["observed_total_latency_s"] == 7.4
    assert first["observed_last_sample_sim_time"] == 12.0
    assert first["observed_component_count"] == 2
    assert second["observed_execution_state"] == "NOT_OBSERVED"
    assert second["observed_complete"] is False
    assert second["observed_total_latency_s"] is None


def test_traffic_timeline_observation_merge_reports_in_progress_trace() -> None:
    timeline = {
        "items": (
            {
                "request_id": "service-003",
                "input_flow_id": "service-003-input",
                "task_id": "service-003-task",
                "output_flow_id": "service-003-output",
            },
        ),
    }
    service_history = {
        "items": (
            {
                "task_id": "service-003-task",
                "input_flow_id": "service-003-input",
                "output_flow_id": "service-003-output",
                "complete": False,
                "total_latency_s": 0.0,
                "last_sample_sim_time": 5.0,
                "component_timeline": ({"component": "input_network"},),
            },
        )
    }

    merged = _merge_traffic_timeline_observations(timeline, service_history)
    item = merged["items"][0]

    assert merged["observed_item_count"] == 1
    assert merged["completed_item_count"] == 0
    assert merged["running_item_count"] == 1
    assert item["observed_execution_state"] == "OBSERVED_IN_PROGRESS"
    assert item["observed_complete"] is False
    assert item["observed_component_count"] == 1
