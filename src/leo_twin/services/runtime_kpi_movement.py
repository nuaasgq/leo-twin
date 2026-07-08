"""Runtime KPI movement evidence for dashboard and diagnostics consumers."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from leo_twin.services.runtime_reproducibility import stable_hash_payload


RUNTIME_KPI_MOVEMENT_SUMMARY_V1_ID = "leo_twin.runtime_kpi_movement_summary.v1"

RuntimeKpiMovementSummaryV1 = dict[str, object]

_EPSILON = 1e-9
_METRIC_SPECS = (
    {
        "metric": "NETWORK_EFFECTIVE_THROUGHPUT",
        "category": "NETWORK",
        "sample_key": "network_effective_throughput_mbps",
        "runtime_summary_key": "network_quality_effective_throughput_mbps",
        "unit": "Mbps",
    },
    {
        "metric": "NETWORK_EFFECTIVE_LATENCY",
        "category": "NETWORK",
        "sample_key": "network_effective_latency_s",
        "runtime_summary_key": "network_quality_effective_latency_avg_s",
        "unit": "s",
    },
    {
        "metric": "NETWORK_EFFECTIVE_LOSS_PROXY",
        "category": "NETWORK",
        "sample_key": "network_effective_loss_proxy_rate",
        "runtime_summary_key": "network_quality_effective_loss_proxy_rate",
        "unit": "ratio",
    },
    {
        "metric": "NETWORK_EFFECTIVE_DELAY_VARIATION_PROXY",
        "category": "NETWORK",
        "sample_key": "network_effective_delay_variation_s",
        "runtime_summary_key": "network_quality_effective_delay_variation_proxy_s",
        "unit": "s",
    },
    {
        "metric": "COMPUTE_CPU_FP32_USED",
        "category": "COMPUTE",
        "sample_key": "compute_resource_used_gflops_fp32",
        "runtime_summary_key": "compute_resource_used_gflops_fp32",
        "unit": "GFLOPS",
    },
    {
        "metric": "COMPUTE_CPU_FP64_USED",
        "category": "COMPUTE",
        "sample_key": "compute_resource_used_gflops_fp64",
        "runtime_summary_key": "compute_resource_used_gflops_fp64",
        "unit": "GFLOPS",
    },
    {
        "metric": "COMPUTE_GPU_FP32_USED",
        "category": "COMPUTE",
        "sample_key": "compute_resource_used_gpu_tflops_fp32",
        "runtime_summary_key": "compute_resource_used_gpu_tflops_fp32",
        "unit": "TFLOPS",
    },
    {
        "metric": "COMPUTE_GPU_FP16_USED",
        "category": "COMPUTE",
        "sample_key": "compute_resource_used_gpu_tflops_fp16",
        "runtime_summary_key": "compute_resource_used_gpu_tflops_fp16",
        "unit": "TFLOPS",
    },
    {
        "metric": "COMPUTE_NPU_INT8_USED",
        "category": "COMPUTE",
        "sample_key": "compute_resource_used_npu_tops_int8",
        "runtime_summary_key": "compute_resource_used_npu_tops_int8",
        "unit": "TOPS",
    },
    {
        "metric": "COMPUTE_MEMORY_USED",
        "category": "COMPUTE",
        "sample_key": "compute_resource_used_memory_gb",
        "runtime_summary_key": "compute_resource_used_memory_gb",
        "unit": "GB",
    },
    {
        "metric": "COMPUTE_STORAGE_USED",
        "category": "COMPUTE",
        "sample_key": "compute_resource_used_storage_gb",
        "runtime_summary_key": "compute_resource_used_storage_gb",
        "unit": "GB",
    },
)


def build_runtime_kpi_movement_summary_v1(
    kpi_time_series: Mapping[str, Any],
    metrics: Mapping[str, Any],
) -> RuntimeKpiMovementSummaryV1:
    """Build runtime-wide KPI movement evidence from backend samples.

    This function audits existing samples only. It does not change metric
    formulas, synthesize movement, replay events, or model packets.
    """

    if not isinstance(kpi_time_series, Mapping):
        raise TypeError("kpi_time_series must be a mapping")
    if not isinstance(metrics, Mapping):
        raise TypeError("metrics must be a mapping")

    samples = _sorted_samples(kpi_time_series.get("samples"))
    sim_times = tuple(
        value for value in (_number(sample.get("sim_time")) for sample in samples)
        if value is not None
    )
    sim_start = min(sim_times, default=0.0)
    sim_end = max(sim_times, default=0.0)
    sim_span = max(0.0, sim_end - sim_start)
    items = tuple(_movement_item(spec, samples, metrics) for spec in _METRIC_SPECS)
    observed = tuple(item for item in items if item["observed"] is True)
    moving = tuple(item for item in observed if item["movement_status"] == "TIME_VARYING")
    flat = tuple(item for item in observed if str(item["movement_status"]).startswith("FLAT"))
    zero_latest = tuple(item for item in observed if item["latest_is_zero"] is True)
    activity_context = _activity_context(samples, metrics)
    payload: dict[str, object] = {
        "version": "v1",
        "summary_id": RUNTIME_KPI_MOVEMENT_SUMMARY_V1_ID,
        "source": "KPI_TIME_SERIES_V1_AND_METRICS_SUMMARY",
        "metric_model": str(metrics.get("network_quality_metric_model", "FLOW_LEVEL_PROXY")),
        "packet_level_simulation": False,
        "frontend_inference_required": False,
        "sample_count": len(samples),
        "sim_time_start_s": sim_start,
        "sim_time_end_s": sim_end,
        "sim_time_span_s": sim_span,
        "activity_context": activity_context,
        "metric_count": len(items),
        "observed_metric_count": len(observed),
        "moving_metric_count": len(moving),
        "flat_metric_count": len(flat),
        "zero_latest_metric_count": len(zero_latest),
        "network_moving_metric_count": sum(
            1 for item in moving if item["category"] == "NETWORK"
        ),
        "compute_moving_metric_count": sum(
            1 for item in moving if item["category"] == "COMPUTE"
        ),
        "movement_status": _movement_status(
            sample_count=len(samples),
            sim_time_span_s=sim_span,
            moving_metric_count=len(moving),
            active=activity_context["active"] is True,
        ),
        "items": items,
        "model_assumptions": (
            "Movement evidence is derived only from backend kpi_time_series_v1 samples.",
            "Flat metrics are reported as flat; no frontend-side variation is inferred.",
            "Network metrics are flow-level proxies and are not packet-level measurements.",
        ),
    }
    payload["summary_hash"] = stable_hash_payload(payload)
    return payload


def _movement_item(
    spec: Mapping[str, str],
    samples: tuple[Mapping[str, Any], ...],
    metrics: Mapping[str, Any],
) -> dict[str, object]:
    sample_key = str(spec["sample_key"])
    values = tuple(
        value
        for value in (_number(sample.get(sample_key)) for sample in samples)
        if value is not None
    )
    runtime_summary_key = str(spec["runtime_summary_key"])
    latest_runtime_value = _number(metrics.get(runtime_summary_key))
    if not values:
        return {
            "metric": str(spec["metric"]),
            "category": str(spec["category"]),
            "sample_key": sample_key,
            "runtime_summary_key": runtime_summary_key,
            "unit": str(spec["unit"]),
            "observed": False,
            "sample_count": 0,
            "first_value": None,
            "latest_value": latest_runtime_value,
            "minimum_value": None,
            "maximum_value": None,
            "absolute_delta": 0.0,
            "endpoint_delta": 0.0,
            "relative_delta": 0.0,
            "latest_is_zero": latest_runtime_value == 0.0,
            "movement_status": "MISSING_SAMPLE_VALUE",
            "flat_reason": "sample key is not present in kpi_time_series_v1",
        }

    first = values[0]
    latest = latest_runtime_value if latest_runtime_value is not None else values[-1]
    minimum = min(values)
    maximum = max(values)
    absolute_delta = maximum - minimum
    endpoint_delta = latest - first
    relative_delta = absolute_delta / max(abs(first), abs(latest), 1.0)
    latest_is_zero = abs(latest) <= _EPSILON
    if len(values) < 2:
        movement_status = "INSUFFICIENT_SAMPLES"
    elif absolute_delta > _EPSILON:
        movement_status = "TIME_VARYING"
    elif latest_is_zero:
        movement_status = "FLAT_ZERO"
    else:
        movement_status = "FLAT_NONZERO"
    return {
        "metric": str(spec["metric"]),
        "category": str(spec["category"]),
        "sample_key": sample_key,
        "runtime_summary_key": runtime_summary_key,
        "unit": str(spec["unit"]),
        "observed": True,
        "sample_count": len(values),
        "first_value": first,
        "latest_value": latest,
        "minimum_value": minimum,
        "maximum_value": maximum,
        "absolute_delta": absolute_delta,
        "endpoint_delta": endpoint_delta,
        "relative_delta": relative_delta,
        "latest_is_zero": latest_is_zero,
        "movement_status": movement_status,
        "flat_reason": _flat_reason(movement_status),
    }


def _movement_status(
    *,
    sample_count: int,
    sim_time_span_s: float,
    moving_metric_count: int,
    active: bool,
) -> str:
    if sample_count < 2 or sim_time_span_s <= _EPSILON:
        return "INSUFFICIENT_SERIES"
    if moving_metric_count >= 3:
        return "TIME_VARYING_OBSERVED"
    if moving_metric_count > 0:
        return "PARTIAL_TIME_VARIATION"
    if active:
        return "FLAT_UNDER_ACTIVITY"
    return "FLAT_NO_ACTIVITY"


def _flat_reason(status: str) -> str:
    if status == "TIME_VARYING":
        return "sample values changed over simulation time"
    if status == "INSUFFICIENT_SAMPLES":
        return "fewer than two samples are available"
    if status == "FLAT_ZERO":
        return "all observed sample values are zero"
    if status == "FLAT_NONZERO":
        return "observed samples are non-zero but unchanged"
    return status


def _activity_context(
    samples: tuple[Mapping[str, Any], ...],
    metrics: Mapping[str, Any],
) -> dict[str, object]:
    latest = samples[-1] if samples else {}
    requested_demand = _first_number(
        metrics,
        "network_quality_requested_route_demand_mbps",
        latest,
        "network_requested_route_demand_mbps",
    )
    offered_capacity = _first_number(
        metrics,
        "network_quality_offered_route_capacity_mbps",
        latest,
        "network_offered_route_capacity_mbps",
    )
    recent_flow_count = _number(latest.get("network_recent_flow_count")) or 0.0
    compute_used = sum(
        _first_number(metrics, spec["runtime_summary_key"], latest, spec["sample_key"])
        for spec in _METRIC_SPECS
        if spec["category"] == "COMPUTE"
    )
    active = (
        requested_demand > 0.0
        or offered_capacity > 0.0
        or recent_flow_count > 0.0
        or compute_used > 0.0
    )
    return {
        "active": active,
        "requested_route_demand_mbps": requested_demand,
        "offered_route_capacity_mbps": offered_capacity,
        "recent_flow_count": recent_flow_count,
        "compute_used_resource_sum": compute_used,
    }


def _first_number(
    first: Mapping[str, Any],
    first_key: str,
    second: Mapping[str, Any],
    second_key: str,
) -> float:
    value = _number(first.get(first_key))
    if value is not None:
        return value
    return _number(second.get(second_key)) or 0.0


def _sorted_samples(value: object) -> tuple[Mapping[str, Any], ...]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return ()
    records = tuple(item for item in value if isinstance(item, Mapping))
    return tuple(sorted(records, key=lambda item: (_number(item.get("sim_time")) or 0.0)))


def _number(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None
