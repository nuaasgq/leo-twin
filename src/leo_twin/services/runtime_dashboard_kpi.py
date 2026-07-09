"""Backend-owned runtime dashboard KPI view."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from leo_twin.services.runtime_reproducibility import stable_hash_payload


RUNTIME_DASHBOARD_KPI_V1_ID = "leo_twin.runtime_dashboard_kpi.v1"

_EPSILON = 1e-9

_METRIC_SPECS: tuple[dict[str, str], ...] = (
    {
        "metric": "NETWORK_EFFECTIVE_THROUGHPUT",
        "category": "NETWORK",
        "display_name": "Effective throughput",
        "sample_key": "network_effective_throughput_mbps",
        "runtime_summary_key": "network_quality_effective_throughput_mbps",
        "unit": "Mbps",
    },
    {
        "metric": "NETWORK_EFFECTIVE_LATENCY",
        "category": "NETWORK",
        "display_name": "Effective latency",
        "sample_key": "network_effective_latency_s",
        "runtime_summary_key": "network_quality_effective_latency_avg_s",
        "unit": "s",
    },
    {
        "metric": "NETWORK_EFFECTIVE_LOSS_PROXY",
        "category": "NETWORK",
        "display_name": "Loss proxy",
        "sample_key": "network_effective_loss_proxy_rate",
        "runtime_summary_key": "network_quality_effective_loss_proxy_rate",
        "unit": "ratio",
    },
    {
        "metric": "NETWORK_EFFECTIVE_DELAY_VARIATION_PROXY",
        "category": "NETWORK",
        "display_name": "Delay-variation proxy",
        "sample_key": "network_effective_delay_variation_s",
        "runtime_summary_key": "network_quality_effective_delay_variation_proxy_s",
        "unit": "s",
    },
    {
        "metric": "COMPUTE_CPU_FP32_USED",
        "category": "COMPUTE",
        "display_name": "CPU FP32 used",
        "sample_key": "compute_resource_used_gflops_fp32",
        "runtime_summary_key": "compute_resource_used_gflops_fp32",
        "unit": "GFLOPS",
    },
    {
        "metric": "COMPUTE_CPU_FP64_USED",
        "category": "COMPUTE",
        "display_name": "CPU FP64 used",
        "sample_key": "compute_resource_used_gflops_fp64",
        "runtime_summary_key": "compute_resource_used_gflops_fp64",
        "unit": "GFLOPS",
    },
    {
        "metric": "COMPUTE_GPU_FP32_USED",
        "category": "COMPUTE",
        "display_name": "GPU FP32 used",
        "sample_key": "compute_resource_used_gpu_tflops_fp32",
        "runtime_summary_key": "compute_resource_used_gpu_tflops_fp32",
        "unit": "TFLOPS",
    },
    {
        "metric": "COMPUTE_GPU_FP16_USED",
        "category": "COMPUTE",
        "display_name": "GPU FP16 used",
        "sample_key": "compute_resource_used_gpu_tflops_fp16",
        "runtime_summary_key": "compute_resource_used_gpu_tflops_fp16",
        "unit": "TFLOPS",
    },
    {
        "metric": "COMPUTE_NPU_INT8_USED",
        "category": "COMPUTE",
        "display_name": "NPU INT8 used",
        "sample_key": "compute_resource_used_npu_tops_int8",
        "runtime_summary_key": "compute_resource_used_npu_tops_int8",
        "unit": "TOPS",
    },
    {
        "metric": "COMPUTE_MEMORY_USED",
        "category": "COMPUTE",
        "display_name": "Memory used",
        "sample_key": "compute_resource_used_memory_gb",
        "runtime_summary_key": "compute_resource_used_memory_gb",
        "unit": "GB",
    },
    {
        "metric": "COMPUTE_STORAGE_USED",
        "category": "COMPUTE",
        "display_name": "Storage used",
        "sample_key": "compute_resource_used_storage_gb",
        "runtime_summary_key": "compute_resource_used_storage_gb",
        "unit": "GB",
    },
)


def build_runtime_dashboard_kpi_v1(
    kpi_time_series: Mapping[str, Any],
    metrics_summary: Mapping[str, Any],
    runtime_kpi_movement: Mapping[str, Any],
    network_kpi_dynamic_status: Mapping[str, Any],
) -> dict[str, object]:
    """Build a frontend-ready KPI surface from backend runtime evidence.

    The function standardizes already-computed runtime values. It does not
    synthesize KPI movement, recompute formulas, inspect snapshots, or model
    packets.
    """

    if not isinstance(kpi_time_series, Mapping):
        raise TypeError("kpi_time_series must be a mapping")
    if not isinstance(metrics_summary, Mapping):
        raise TypeError("metrics_summary must be a mapping")
    if not isinstance(runtime_kpi_movement, Mapping):
        raise TypeError("runtime_kpi_movement must be a mapping")
    if not isinstance(network_kpi_dynamic_status, Mapping):
        raise TypeError("network_kpi_dynamic_status must be a mapping")

    samples = _sorted_samples(kpi_time_series.get("samples"))
    tail_sample = samples[-1] if samples else {}
    movement_items = _items_by_metric(runtime_kpi_movement.get("items"))
    dynamic_items = _items_by_metric(network_kpi_dynamic_status.get("items"))
    items = tuple(
        _dashboard_item(
            spec,
            tail_sample=tail_sample,
            metrics_summary=metrics_summary,
            movement_item=movement_items.get(spec["metric"], {}),
            dynamic_item=dynamic_items.get(spec["metric"], {}),
        )
        for spec in _METRIC_SPECS
    )
    observed = tuple(item for item in items if item["observed"] is True)
    zero_current = tuple(item for item in observed if item["latest_is_zero"] is True)
    dynamic = tuple(item for item in items if item["is_time_varying"] is True)
    payload: dict[str, object] = {
        "version": "v1",
        "summary_id": RUNTIME_DASHBOARD_KPI_V1_ID,
        "source": "KPI_TIME_SERIES_TAIL_AND_METRICS_SUMMARY",
        "metric_model": str(
            metrics_summary.get("network_quality_metric_model", "FLOW_LEVEL_PROXY")
        ),
        "packet_level_simulation": False,
        "frontend_inference_required": False,
        "sample_count": len(samples),
        "tail_sample_time_s": _optional_float(tail_sample.get("sim_time")),
        "metrics_summary_event_time_s": _optional_float(
            metrics_summary.get("metrics_summary_event_time_s")
        ),
        "metrics_summary_observation_time_s": _optional_float(
            metrics_summary.get("metrics_summary_observation_time_s")
        ),
        "metrics_summary_time_source": str(
            metrics_summary.get("metrics_summary_time_source", "")
        ),
        "runtime_movement_status": str(
            runtime_kpi_movement.get("movement_status", "")
        ),
        "network_dynamic_status": str(
            network_kpi_dynamic_status.get("dynamic_status", "")
        ),
        "metric_count": len(items),
        "observed_metric_count": len(observed),
        "zero_current_metric_count": len(zero_current),
        "time_varying_metric_count": len(dynamic),
        "network_metric_count": sum(1 for item in items if item["category"] == "NETWORK"),
        "compute_metric_count": sum(1 for item in items if item["category"] == "COMPUTE"),
        "items": items,
        "model_assumptions": (
            "Dashboard KPI values are read from backend kpi_time_series_v1 tail samples when available.",
            "metrics_summary values are retained as source evidence and fallback values.",
            "Zero values are reported with backend movement or dynamic-status reasons.",
            "Network KPIs remain flow-level proxies and are not packet-level measurements.",
        ),
    }
    payload["summary_hash"] = stable_hash_payload(payload)
    return payload


def _dashboard_item(
    spec: Mapping[str, str],
    *,
    tail_sample: Mapping[str, Any],
    metrics_summary: Mapping[str, Any],
    movement_item: Mapping[str, Any],
    dynamic_item: Mapping[str, Any],
) -> dict[str, object]:
    sample_key = str(spec["sample_key"])
    runtime_summary_key = str(spec["runtime_summary_key"])
    tail_value = _optional_float(tail_sample.get(sample_key))
    runtime_value = _optional_float(metrics_summary.get(runtime_summary_key))
    current_value = tail_value if tail_value is not None else runtime_value
    value_source = "KPI_TAIL_SAMPLE" if tail_value is not None else "METRICS_SUMMARY"
    if current_value is None:
        value_source = "MISSING"
    latest_is_zero = current_value is not None and abs(current_value) <= _EPSILON
    movement_status = str(movement_item.get("movement_status", ""))
    variation_status = str(dynamic_item.get("variation_status", ""))
    flat_reason = str(movement_item.get("flat_reason", ""))
    zero_reason = _zero_reason(
        metric=str(spec["metric"]),
        latest_is_zero=latest_is_zero,
        tail_sample=tail_sample,
        dynamic_item=dynamic_item,
        flat_reason=flat_reason,
    )
    return {
        "metric": str(spec["metric"]),
        "category": str(spec["category"]),
        "display_name": str(spec["display_name"]),
        "unit": str(spec["unit"]),
        "sample_key": sample_key,
        "runtime_summary_key": runtime_summary_key,
        "current_value": current_value,
        "tail_sample_value": tail_value,
        "runtime_summary_value": runtime_value,
        "value_source": value_source,
        "observed": current_value is not None,
        "latest_is_zero": latest_is_zero,
        "is_time_varying": (
            movement_status == "TIME_VARYING" or variation_status == "TIME_VARYING"
        ),
        "movement_status": movement_status,
        "variation_status": variation_status,
        "visibility": str(dynamic_item.get("visibility", "SHOW_CURRENT_VALUE")),
        "flat_reason": flat_reason,
        "zero_value_note": zero_reason,
        "source_detail": _source_detail(str(spec["metric"]), tail_sample),
    }


def _source_detail(
    metric: str,
    tail_sample: Mapping[str, Any],
) -> dict[str, object]:
    if metric == "NETWORK_EFFECTIVE_THROUGHPUT":
        return {
            "source": str(tail_sample.get("network_effective_throughput_source", "")),
            "source_label": str(
                tail_sample.get("network_effective_throughput_source_label", "")
            ),
        }
    if metric == "NETWORK_EFFECTIVE_LOSS_PROXY":
        return {
            "recent_loss_zero_reason": str(
                tail_sample.get("network_recent_loss_zero_reason", "")
            ),
            "recent_loss_zero_reason_label": str(
                tail_sample.get("network_recent_loss_zero_reason_label", "")
            ),
        }
    if metric == "NETWORK_EFFECTIVE_DELAY_VARIATION_PROXY":
        return {
            "recent_delay_variation_zero_reason": str(
                tail_sample.get("network_recent_delay_variation_zero_reason", "")
            ),
            "recent_delay_variation_zero_reason_label": str(
                tail_sample.get("network_recent_delay_variation_zero_reason_label", "")
            ),
        }
    return {}


def _zero_reason(
    *,
    metric: str,
    latest_is_zero: bool,
    tail_sample: Mapping[str, Any],
    dynamic_item: Mapping[str, Any],
    flat_reason: str,
) -> str:
    if not latest_is_zero:
        return ""
    dynamic_note = str(dynamic_item.get("zero_value_note", ""))
    if dynamic_note:
        return dynamic_note
    if metric == "NETWORK_EFFECTIVE_THROUGHPUT":
        label = str(tail_sample.get("network_effective_throughput_source_label", ""))
        if label:
            return label
    if metric == "NETWORK_EFFECTIVE_LOSS_PROXY":
        label = str(tail_sample.get("network_recent_loss_zero_reason_label", ""))
        if label:
            return label
    if metric == "NETWORK_EFFECTIVE_DELAY_VARIATION_PROXY":
        label = str(
            tail_sample.get("network_recent_delay_variation_zero_reason_label", "")
        )
        if label:
            return label
    if flat_reason:
        return flat_reason
    return "Current backend KPI value is zero."


def _sorted_samples(value: object) -> tuple[Mapping[str, Any], ...]:
    if not isinstance(value, tuple | list):
        return ()
    samples = tuple(item for item in value if isinstance(item, Mapping))
    return tuple(sorted(samples, key=lambda item: (_float(item.get("sim_time")),)))


def _items_by_metric(value: object) -> dict[str, Mapping[str, Any]]:
    if not isinstance(value, tuple | list):
        return {}
    result: dict[str, Mapping[str, Any]] = {}
    for item in value:
        if isinstance(item, Mapping):
            result[str(item.get("metric", ""))] = item
    return result


def _optional_float(value: object) -> float | None:
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


def _float(value: object) -> float:
    optional = _optional_float(value)
    return 0.0 if optional is None else optional


__all__ = [
    "RUNTIME_DASHBOARD_KPI_V1_ID",
    "build_runtime_dashboard_kpi_v1",
]
