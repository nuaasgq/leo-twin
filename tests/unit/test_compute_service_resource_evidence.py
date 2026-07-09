from __future__ import annotations

from leo_twin.services.compute_service_resource_evidence import (
    COMPUTE_SERVICE_RESOURCE_EVIDENCE_V1_ID,
    build_compute_service_resource_evidence_v1,
)


def test_compute_service_resource_evidence_reports_queue_and_resource_pressure() -> None:
    first = build_compute_service_resource_evidence_v1(
        _service_history(),
        _resource_pool(),
    )
    second = build_compute_service_resource_evidence_v1(
        _service_history(),
        _resource_pool(),
    )

    assert first == second
    assert first["version"] == "v1"
    assert first["summary_id"] == COMPUTE_SERVICE_RESOURCE_EVIDENCE_V1_ID
    assert first["source"] == "service_latency_history_v1 + compute_resource_pool_summary_v1"
    assert first["packet_level_simulation"] is False
    assert first["frontend_inference_required"] is False
    assert first["service_count"] == 2
    assert first["complete_service_count"] == 1
    assert first["running_service_count"] == 1
    assert first["queued_service_count"] == 1
    assert first["executing_service_count"] == 2
    assert first["queue_pressure_status"] == "QUEUE_PRESSURE_WITH_RESOURCE_SATURATION"
    assert first["resource_pressure_status"] == "RESOURCE_SATURATED"
    assert first["avg_compute_queue_delay_s"] == 0.25
    assert first["max_compute_queue_delay_s"] == 0.5
    assert first["avg_compute_execution_delay_s"] == 2.5
    assert first["queue_to_execution_ratio"] == 0.1
    assert first["saturated_resource_dimension_count"] == 1
    assert first["summary_hash"].startswith("sha256:")


def test_compute_service_resource_evidence_reports_node_and_service_rows() -> None:
    summary = build_compute_service_resource_evidence_v1(
        _service_history(),
        _resource_pool(),
    )

    assert summary["compute_node_count"] == 2
    nodes = {row["compute_node_id"]: row for row in summary["node_rows"]}
    assert nodes["sat-a"]["service_count"] == 1
    assert nodes["sat-a"]["queued_service_count"] == 1
    assert nodes["sat-a"]["dominant_bottleneck_resource"] == "gpu_tflops_fp32"
    assert nodes["sat-a"]["node_hash"].startswith("sha256:")
    first_item = summary["items"][0]
    assert first_item["task_id"] == "svc-00-task"
    assert first_item["queue_state"] == "QUEUED"
    assert first_item["execution_state"] == "EXECUTED"
    assert first_item["resource_evidence_state"] == "PLACEMENT_OBSERVED"
    assert first_item["detail_hash"].startswith("sha256:")


def test_compute_service_resource_evidence_supports_cursor_and_query() -> None:
    summary = build_compute_service_resource_evidence_v1(
        _service_history(),
        _resource_pool(),
        limit=1,
        query="sat-b",
    )

    assert summary["filter_applied"] is True
    assert summary["unfiltered_service_count"] == 2
    assert summary["service_count"] == 1
    assert summary["item_count"] == 1
    assert summary["has_more"] is False
    assert summary["items"][0]["compute_node_id"] == "sat-b"


def test_compute_service_resource_evidence_handles_empty_inputs() -> None:
    summary = build_compute_service_resource_evidence_v1(
        {"items": ()},
        {"dimensions": (), "bottleneck": {}},
    )

    assert summary["service_count"] == 0
    assert summary["queue_pressure_status"] == "NO_SERVICE_EVIDENCE"
    assert summary["resource_pressure_status"] == "RESOURCE_NOT_CONFIGURED"
    assert summary["items"] == ()


def _service_history() -> dict[str, object]:
    return {
        "items": (
            {
                "task_id": "svc-00-task",
                "input_flow_id": "svc-00-input",
                "output_flow_id": "svc-00-output",
                "compute_node_id": "sat-a",
                "complete": True,
                "service_placement_status": "PLACED",
                "service_placement_policy": "MIN_ESTIMATED_FINISH_TIME",
                "service_placement_bottleneck_resource": "gpu_tflops_fp32",
                "service_placement_candidate_count": 4,
                "service_placement_capable_candidate_count": 2,
                "service_placement_candidate_queue_label": "sat-a:q=1",
                "compute_queue_delay_s": 0.5,
                "compute_execution_delay_s": 3.0,
                "input_network_latency_s": 2.0,
                "output_network_latency_s": 1.0,
                "total_latency_s": 6.5,
                "first_sample_sim_time": 4.0,
                "last_sample_sim_time": 10.0,
            },
            {
                "task_id": "svc-01-task",
                "input_flow_id": "svc-01-input",
                "output_flow_id": "svc-01-output",
                "compute_node_id": "sat-b",
                "complete": False,
                "service_placement_status": "PLACED",
                "service_placement_policy": "MIN_ESTIMATED_FINISH_TIME",
                "service_placement_bottleneck_resource": "cpu_gflops_fp32",
                "service_placement_candidate_count": 4,
                "service_placement_capable_candidate_count": 3,
                "service_placement_candidate_queue_label": "sat-b:q=0",
                "compute_queue_delay_s": 0.0,
                "compute_execution_delay_s": 2.0,
                "input_network_latency_s": 1.0,
                "output_network_latency_s": 0.0,
                "total_latency_s": 0.0,
                "first_sample_sim_time": 8.0,
                "last_sample_sim_time": 11.0,
            },
        ),
    }


def _resource_pool() -> dict[str, object]:
    return {
        "active_dimension_count": 2,
        "consumed_dimension_count": 2,
        "bottleneck": {
            "resource": "gpu_tflops_fp32",
            "label": "GPU FP32 TFLOPS",
            "utilization": 1.0,
            "status": "SATURATED",
        },
        "dimensions": (
            {
                "resource": "gpu_tflops_fp32",
                "label": "GPU FP32 TFLOPS",
                "unit": "TFLOPS FP32",
                "total": 2.0,
                "available": 0.0,
                "used": 2.0,
                "utilization": 1.0,
                "resource_status": "SATURATED",
            },
            {
                "resource": "cpu_gflops_fp32",
                "label": "CPU FP32 GFLOPS",
                "unit": "GFLOPS FP32",
                "total": 30.0,
                "available": 20.0,
                "used": 10.0,
                "utilization": 1.0 / 3.0,
                "resource_status": "ACTIVE",
            },
        ),
    }
