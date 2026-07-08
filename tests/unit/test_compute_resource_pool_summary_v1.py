from __future__ import annotations

import json

import pytest

from leo_twin.services.compute_resource_pool_summary import (
    COMPUTE_RESOURCE_POOL_SUMMARY_V1_ID,
    build_compute_resource_pool_summary_v1,
)


def test_compute_resource_pool_summary_reports_resource_vector_dimensions() -> None:
    metrics = {
        "compute_resource_node_count": 2,
        "compute_resource_busy_nodes": 1,
        "compute_resource_idle_nodes": 1,
        "compute_resource_total_gflops_fp32": 30.0,
        "compute_resource_available_gflops_fp32": 15.0,
        "compute_resource_used_gflops_fp32": 15.0,
        "compute_resource_total_gflops_fp64": 6.0,
        "compute_resource_available_gflops_fp64": 3.0,
        "compute_resource_used_gflops_fp64": 3.0,
        "compute_resource_total_gpu_tflops_fp32": 2.0,
        "compute_resource_available_gpu_tflops_fp32": 0.0,
        "compute_resource_used_gpu_tflops_fp32": 2.0,
        "compute_resource_total_gpu_tflops_fp16": 4.0,
        "compute_resource_available_gpu_tflops_fp16": 4.0,
        "compute_resource_used_gpu_tflops_fp16": 0.0,
        "compute_resource_total_npu_tops_int8": 8.0,
        "compute_resource_available_npu_tops_int8": 6.0,
        "compute_resource_used_npu_tops_int8": 2.0,
        "compute_resource_total_memory_gb": 64.0,
        "compute_resource_available_memory_gb": 48.0,
        "compute_resource_used_memory_gb": 16.0,
        "compute_resource_total_storage_gb": 1024.0,
        "compute_resource_available_storage_gb": 900.0,
        "compute_resource_used_storage_gb": 124.0,
        "compute_resource_vector_capacity_reported": True,
        "compute_resource_vector_utilization_mode": "RESOURCE_VECTOR_ESTIMATED",
        "compute_resource_bottleneck_resource": "gpu_tflops_fp32",
        "compute_resource_bottleneck_label": "GPU FP32 TFLOPS",
        "compute_resource_bottleneck_utilization": 1.0,
        "compute_resource_bottleneck_used": 2.0,
        "compute_resource_bottleneck_total": 2.0,
        "compute_resource_bottleneck_available": 0.0,
        "compute_resource_bottleneck_status": "SATURATED",
    }

    summary = build_compute_resource_pool_summary_v1(metrics)
    rows = {row["resource"]: row for row in summary["dimensions"]}

    assert summary["version"] == "v1"
    assert summary["summary_id"] == COMPUTE_RESOURCE_POOL_SUMMARY_V1_ID
    assert summary["source"] == "METRICS_SUMMARY_COMPUTE_RESOURCE_FIELDS"
    assert summary["metric_model"] == "RESOURCE_VECTOR_FLOW_LEVEL_ESTIMATE"
    assert summary["packet_level_simulation"] is False
    assert summary["frontend_inference_required"] is False
    assert summary["node_count"] == 2
    assert summary["busy_node_count"] == 1
    assert summary["idle_node_count"] == 1
    assert summary["vector_capacity_reported"] is True
    assert summary["vector_utilization_mode"] == "RESOURCE_VECTOR_ESTIMATED"
    assert summary["dimension_count"] == 7
    assert summary["active_dimension_count"] == 7
    assert summary["consumed_dimension_count"] == 6
    assert summary["saturated_dimension_count"] == 1
    assert summary["bottleneck"] == {
        "resource": "gpu_tflops_fp32",
        "label": "GPU FP32 TFLOPS",
        "utilization": 1.0,
        "used": 2.0,
        "total": 2.0,
        "available": 0.0,
        "status": "SATURATED",
    }
    assert rows["cpu_gflops_fp32"]["utilization"] == 0.5
    assert rows["gpu_tflops_fp32"]["resource_status"] == "SATURATED"
    assert rows["gpu_tflops_fp16"]["resource_status"] == "IDLE"
    assert rows["memory_gb"]["unit"] == "GB"
    assert summary["visualization_policy"] == {
        "preferred_chart": "PER_DIMENSION_UTILIZATION_BARS",
        "pie_chart_allowed": False,
        "reason": (
            "Compute dimensions use different units; do not sum FP32, FP64, "
            "GPU, NPU, memory, and storage into one pie denominator."
        ),
    }
    assert str(summary["summary_hash"]).startswith("sha256:")
    json.dumps(summary, sort_keys=True)


def test_compute_resource_pool_summary_handles_missing_metrics() -> None:
    summary = build_compute_resource_pool_summary_v1({})

    assert summary["node_count"] == 0
    assert summary["active_dimension_count"] == 0
    assert summary["consumed_dimension_count"] == 0
    assert all(row["resource_status"] == "NOT_CONFIGURED" for row in summary["dimensions"])


def test_compute_resource_pool_summary_rejects_invalid_metrics() -> None:
    with pytest.raises(TypeError):
        build_compute_resource_pool_summary_v1(object())  # type: ignore[arg-type]
