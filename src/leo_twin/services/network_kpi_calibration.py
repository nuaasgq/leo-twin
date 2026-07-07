"""Deterministic network KPI calibration summary for runtime status."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


NETWORK_KPI_CALIBRATION_V1_ID = "leo_twin.network_kpi_calibration.v1"

NetworkKpiCalibrationV1 = dict[str, object]

_EPSILON = 1e-9
_CORE_KPIS = (
    {
        "metric": "EFFECTIVE_THROUGHPUT",
        "sample_key": "network_effective_throughput_mbps",
        "runtime_summary_key": "network_quality_effective_throughput_mbps",
        "unit": "Mbps",
    },
    {
        "metric": "EFFECTIVE_LATENCY",
        "sample_key": "network_effective_latency_s",
        "runtime_summary_key": "network_quality_effective_latency_avg_s",
        "unit": "s",
    },
    {
        "metric": "EFFECTIVE_LOSS_PROXY",
        "sample_key": "network_effective_loss_proxy_rate",
        "runtime_summary_key": "network_quality_effective_loss_proxy_rate",
        "unit": "ratio",
    },
    {
        "metric": "EFFECTIVE_DELAY_VARIATION_PROXY",
        "sample_key": "network_effective_delay_variation_s",
        "runtime_summary_key": "network_quality_effective_delay_variation_proxy_s",
        "unit": "s",
    },
)


def build_network_kpi_calibration_v1(
    kpi_time_series: Mapping[str, Any],
    metrics: Mapping[str, Any],
) -> NetworkKpiCalibrationV1:
    """Build a product-facing calibration summary from KPI samples.

    The summary does not change any KPI formula. It only audits whether the
    runtime sample sequence shows deterministic movement over simulation time.
    """

    if not isinstance(kpi_time_series, Mapping):
        raise TypeError("kpi_time_series must be a mapping")
    if not isinstance(metrics, Mapping):
        raise TypeError("metrics must be a mapping")

    samples = _sorted_samples(kpi_time_series.get("samples"))
    sim_times = tuple(_number(sample.get("sim_time")) for sample in samples)
    numeric_sim_times = tuple(value for value in sim_times if value is not None)
    sim_start = min(numeric_sim_times, default=0.0)
    sim_end = max(numeric_sim_times, default=0.0)
    sim_span = max(0.0, sim_end - sim_start)
    kpis = tuple(_calibrate_kpi(spec, samples, metrics) for spec in _CORE_KPIS)
    observed = tuple(item for item in kpis if item["observed"] is True)
    varying = tuple(item for item in observed if item["variation_status"] == "TIME_VARYING")
    flat = tuple(
        item
        for item in observed
        if str(item["variation_status"]).startswith("FLAT")
    )
    zero_latest = tuple(item for item in observed if item["latest_is_zero"] is True)
    activity_context = _activity_context(samples, metrics)
    return {
        "version": "v1",
        "calibration_id": NETWORK_KPI_CALIBRATION_V1_ID,
        "source": "KPI_TIME_SERIES_V1_AND_METRICS_SUMMARY",
        "metric_model": str(metrics.get("network_quality_metric_model", "FLOW_LEVEL_PROXY")),
        "packet_level_simulation": False,
        "sample_count": len(samples),
        "sim_time_start_s": sim_start,
        "sim_time_end_s": sim_end,
        "sim_time_span_s": sim_span,
        "activity_context": activity_context,
        "time_driver": _time_driver(samples, metrics),
        "kpi_count": len(kpis),
        "observed_kpi_count": len(observed),
        "time_varying_kpi_count": len(varying),
        "flat_kpi_count": len(flat),
        "zero_latest_kpi_count": len(zero_latest),
        "calibration_status": _calibration_status(
            sample_count=len(samples),
            sim_time_span_s=sim_span,
            time_varying_kpi_count=len(varying),
            active=activity_context["active"] is True,
        ),
        "kpis": kpis,
        "caveats": _caveats(),
    }


def _calibrate_kpi(
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
    latest_runtime_value = _number(metrics.get(str(spec["runtime_summary_key"])))
    if not values:
        return {
            "metric": str(spec["metric"]),
            "sample_key": sample_key,
            "runtime_summary_key": str(spec["runtime_summary_key"]),
            "unit": str(spec["unit"]),
            "observed": False,
            "first_value": None,
            "latest_value": latest_runtime_value,
            "minimum_value": None,
            "maximum_value": None,
            "absolute_delta": 0.0,
            "endpoint_delta": 0.0,
            "relative_delta": 0.0,
            "latest_is_zero": latest_runtime_value == 0.0,
            "variation_status": "MISSING_SAMPLE_VALUE",
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
        variation_status = "INSUFFICIENT_SAMPLES"
    elif absolute_delta > _EPSILON:
        variation_status = "TIME_VARYING"
    elif latest_is_zero:
        variation_status = "FLAT_ZERO"
    else:
        variation_status = "FLAT_NONZERO"
    return {
        "metric": str(spec["metric"]),
        "sample_key": sample_key,
        "runtime_summary_key": str(spec["runtime_summary_key"]),
        "unit": str(spec["unit"]),
        "observed": True,
        "first_value": first,
        "latest_value": latest,
        "minimum_value": minimum,
        "maximum_value": maximum,
        "absolute_delta": absolute_delta,
        "endpoint_delta": endpoint_delta,
        "relative_delta": relative_delta,
        "latest_is_zero": latest_is_zero,
        "variation_status": variation_status,
        "flat_reason": _flat_reason(variation_status),
    }


def _calibration_status(
    *,
    sample_count: int,
    sim_time_span_s: float,
    time_varying_kpi_count: int,
    active: bool,
) -> str:
    if sample_count < 2 or sim_time_span_s <= _EPSILON:
        return "INSUFFICIENT_SERIES"
    if time_varying_kpi_count >= 2:
        return "TIME_VARYING_OBSERVED"
    if time_varying_kpi_count == 1:
        return "PARTIAL_TIME_VARIATION"
    if active:
        return "FLAT_UNDER_ACTIVITY"
    return "FLAT_NO_ACTIVITY"


def _activity_context(
    samples: tuple[Mapping[str, Any], ...],
    metrics: Mapping[str, Any],
) -> dict[str, object]:
    latest = samples[-1] if samples else {}
    requested_demand = _number(
        metrics.get("network_quality_requested_route_demand_mbps")
    )
    if requested_demand is None:
        requested_demand = _number(latest.get("network_requested_route_demand_mbps")) or 0.0
    offered_capacity = _number(
        metrics.get("network_quality_offered_route_capacity_mbps")
    )
    if offered_capacity is None:
        offered_capacity = _number(latest.get("network_offered_route_capacity_mbps")) or 0.0
    recent_flow_count = _number(latest.get("network_recent_flow_count")) or 0.0
    active_route_count = _number(metrics.get("network_quality_available_route_count")) or 0.0
    active = (
        requested_demand > 0.0
        or offered_capacity > 0.0
        or recent_flow_count > 0.0
        or active_route_count > 0.0
    )
    return {
        "active": active,
        "requested_route_demand_mbps": requested_demand,
        "offered_route_capacity_mbps": offered_capacity,
        "recent_flow_count": recent_flow_count,
        "available_route_count": active_route_count,
    }


def _time_driver(
    samples: tuple[Mapping[str, Any], ...],
    metrics: Mapping[str, Any],
) -> dict[str, object]:
    latest = samples[-1] if samples else {}
    return {
        "source": "SIMULATION_TIME",
        "period_s": _metric_or_sample_number(
            metrics,
            latest,
            "network_quality_time_pressure_period_s",
            "network_time_pressure_period_s",
        ),
        "phase": _metric_or_sample_number(
            metrics,
            latest,
            "network_quality_time_pressure_phase",
            "network_time_pressure_phase",
        ),
        "factor": _metric_or_sample_number(
            metrics,
            latest,
            "network_quality_time_pressure_factor",
            "network_time_pressure_factor",
        ),
        "loss_proxy_rate": _metric_or_sample_number(
            metrics,
            latest,
            "network_quality_time_pressure_loss_proxy_rate",
            "network_time_pressure_loss_proxy_rate",
        ),
        "delay_variation_proxy_s": _metric_or_sample_number(
            metrics,
            latest,
            "network_quality_time_pressure_delay_variation_proxy_s",
            "network_time_pressure_delay_variation_s",
        ),
    }


def _metric_or_sample_number(
    metrics: Mapping[str, Any],
    sample: Mapping[str, Any],
    metric_key: str,
    sample_key: str,
) -> float:
    metric_value = _number(metrics.get(metric_key))
    if metric_value is not None:
        return metric_value
    sample_value = _number(sample.get(sample_key))
    if sample_value is not None:
        return sample_value
    return 0.0


def _sorted_samples(value: object) -> tuple[Mapping[str, Any], ...]:
    if not isinstance(value, (list, tuple)):
        return ()
    samples = tuple(item for item in value if isinstance(item, Mapping))
    return tuple(
        sorted(
            samples,
            key=lambda item: (
                _number(item.get("sim_time")) is None,
                _number(item.get("sim_time")) or 0.0,
            ),
        )
    )


def _number(value: object) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    if value != value or value in {float("inf"), float("-inf")}:
        return None
    return float(value)


def _flat_reason(variation_status: str) -> str:
    if variation_status == "TIME_VARYING":
        return ""
    if variation_status == "INSUFFICIENT_SAMPLES":
        return "fewer than two numeric samples are available"
    if variation_status == "FLAT_ZERO":
        return "all observed samples are zero; inspect zero reasons and activity context"
    if variation_status == "FLAT_NONZERO":
        return "observed samples are constant; route, flow, or pressure inputs did not change"
    return "sample value is missing"


def _caveats() -> tuple[str, ...]:
    return (
        "Calibration v1 audits deterministic flow-level KPI movement; it is not a packet-level measurement.",
        "A flat KPI can be valid when route, flow, and pressure inputs are unchanged.",
        "Packet-level loss and jitter remain outside the current product contract.",
    )


__all__ = [
    "NETWORK_KPI_CALIBRATION_V1_ID",
    "NetworkKpiCalibrationV1",
    "build_network_kpi_calibration_v1",
]
