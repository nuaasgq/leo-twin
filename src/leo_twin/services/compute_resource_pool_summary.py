"""Runtime compute resource pool summary v1."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from leo_twin.services.runtime_reproducibility import stable_hash_payload


COMPUTE_RESOURCE_POOL_SUMMARY_V1_ID = "leo_twin.compute_resource_pool_summary.v1"

ComputeResourcePoolSummaryV1 = dict[str, object]

_RESOURCE_DIMENSIONS = (
    (
        "cpu_gflops_fp32",
        "CPU FP32 GFLOPS",
        "GFLOPS FP32",
        "compute_resource_total_gflops_fp32",
        "compute_resource_available_gflops_fp32",
        "compute_resource_used_gflops_fp32",
    ),
    (
        "cpu_gflops_fp64",
        "CPU FP64 GFLOPS",
        "GFLOPS FP64",
        "compute_resource_total_gflops_fp64",
        "compute_resource_available_gflops_fp64",
        "compute_resource_used_gflops_fp64",
    ),
    (
        "gpu_tflops_fp32",
        "GPU FP32 TFLOPS",
        "TFLOPS FP32",
        "compute_resource_total_gpu_tflops_fp32",
        "compute_resource_available_gpu_tflops_fp32",
        "compute_resource_used_gpu_tflops_fp32",
    ),
    (
        "gpu_tflops_fp16",
        "GPU FP16 TFLOPS",
        "TFLOPS FP16",
        "compute_resource_total_gpu_tflops_fp16",
        "compute_resource_available_gpu_tflops_fp16",
        "compute_resource_used_gpu_tflops_fp16",
    ),
    (
        "npu_tops_int8",
        "NPU INT8 TOPS",
        "TOPS INT8",
        "compute_resource_total_npu_tops_int8",
        "compute_resource_available_npu_tops_int8",
        "compute_resource_used_npu_tops_int8",
    ),
    (
        "memory_gb",
        "Memory GB",
        "GB",
        "compute_resource_total_memory_gb",
        "compute_resource_available_memory_gb",
        "compute_resource_used_memory_gb",
    ),
    (
        "storage_gb",
        "Storage GB",
        "GB",
        "compute_resource_total_storage_gb",
        "compute_resource_available_storage_gb",
        "compute_resource_used_storage_gb",
    ),
)


def build_compute_resource_pool_summary_v1(
    metrics: Mapping[str, Any],
) -> ComputeResourcePoolSummaryV1:
    """Build a frontend-ready compute resource pool contract from metrics."""

    if not isinstance(metrics, Mapping):
        raise TypeError("metrics must be a mapping")
    dimensions = tuple(_resource_dimension(metrics, spec) for spec in _RESOURCE_DIMENSIONS)
    active_dimensions = tuple(row for row in dimensions if row["total"] > 0.0)
    consumed_dimensions = tuple(row for row in dimensions if row["used"] > 0.0)
    saturated_dimensions = tuple(
        row for row in dimensions if row["resource_status"] == "SATURATED"
    )
    payload: dict[str, object] = {
        "version": "v1",
        "summary_id": COMPUTE_RESOURCE_POOL_SUMMARY_V1_ID,
        "source": "METRICS_SUMMARY_COMPUTE_RESOURCE_FIELDS",
        "metric_model": "RESOURCE_VECTOR_FLOW_LEVEL_ESTIMATE",
        "packet_level_simulation": False,
        "frontend_inference_required": False,
        "node_count": int(_number(metrics, "compute_resource_node_count")),
        "busy_node_count": int(_number(metrics, "compute_resource_busy_nodes")),
        "idle_node_count": int(_number(metrics, "compute_resource_idle_nodes")),
        "vector_capacity_reported": bool(
            metrics.get("compute_resource_vector_capacity_reported", False)
        ),
        "vector_utilization_mode": str(
            metrics.get("compute_resource_vector_utilization_mode", "")
        ),
        "dimension_count": len(dimensions),
        "active_dimension_count": len(active_dimensions),
        "consumed_dimension_count": len(consumed_dimensions),
        "saturated_dimension_count": len(saturated_dimensions),
        "bottleneck": {
            "resource": str(metrics.get("compute_resource_bottleneck_resource", "")),
            "label": str(metrics.get("compute_resource_bottleneck_label", "")),
            "utilization": _number(
                metrics,
                "compute_resource_bottleneck_utilization",
            ),
            "used": _number(metrics, "compute_resource_bottleneck_used"),
            "total": _number(metrics, "compute_resource_bottleneck_total"),
            "available": _number(
                metrics,
                "compute_resource_bottleneck_available",
            ),
            "status": str(metrics.get("compute_resource_bottleneck_status", "")),
        },
        "dimensions": dimensions,
        "visualization_policy": {
            "preferred_chart": "PER_DIMENSION_UTILIZATION_BARS",
            "pie_chart_allowed": False,
            "reason": (
                "Compute dimensions use different units; do not sum FP32, FP64, "
                "GPU, NPU, memory, and storage into one pie denominator."
            ),
        },
        "model_assumptions": (
            "Resource pool values are derived from ComputeNodeState metrics.",
            "Legacy scalar capacity is treated as CPU FP32 GFLOPS.",
            "Vector dimensions are deterministic estimates, not real hardware telemetry.",
        ),
    }
    payload["summary_hash"] = stable_hash_payload(payload)
    return payload


def _resource_dimension(
    metrics: Mapping[str, Any],
    spec: tuple[str, str, str, str, str, str],
) -> dict[str, object]:
    resource, label, unit, total_key, available_key, used_key = spec
    total = _number(metrics, total_key)
    available = _number(metrics, available_key)
    used = _number(metrics, used_key)
    utilization = 0.0 if total <= 0.0 else min(1.0, max(0.0, used / total))
    return {
        "resource": resource,
        "label": label,
        "unit": unit,
        "total": total,
        "available": available,
        "used": used,
        "utilization": utilization,
        "resource_status": _resource_status(total, used, utilization),
        "source_fields": {
            "total": total_key,
            "available": available_key,
            "used": used_key,
        },
    }


def _resource_status(total: float, used: float, utilization: float) -> str:
    if total <= 0.0:
        return "NOT_CONFIGURED"
    if utilization >= 0.999 or used >= total:
        return "SATURATED"
    if utilization >= 0.7:
        return "BUSY"
    if used > 0.0:
        return "ACTIVE"
    return "IDLE"


def _number(metrics: Mapping[str, Any], key: str) -> float:
    value = metrics.get(key, 0.0)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return 0.0
    return max(0.0, float(value))
