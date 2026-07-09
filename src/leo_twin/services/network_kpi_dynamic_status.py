"""Backend-owned dynamic status summary for network KPI time series."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from leo_twin.services.runtime_reproducibility import stable_hash_payload


NETWORK_KPI_DYNAMIC_STATUS_V1_ID = "leo_twin.network_kpi_dynamic_status.v1"

NetworkKpiDynamicStatusV1 = dict[str, object]

_DISPLAY_NAMES = {
    "EFFECTIVE_THROUGHPUT": "Effective throughput",
    "EFFECTIVE_LATENCY": "Effective latency",
    "EFFECTIVE_LOSS_PROXY": "Loss proxy",
    "EFFECTIVE_DELAY_VARIATION_PROXY": "Delay-variation proxy",
}


def build_network_kpi_dynamic_status_v1(
    calibration: Mapping[str, Any],
) -> NetworkKpiDynamicStatusV1:
    """Summarize whether network KPIs are dynamically moving over sim time."""

    if not isinstance(calibration, Mapping):
        raise TypeError("calibration must be a mapping")
    kpis = tuple(_kpi_item(item) for item in _records(calibration.get("kpis")))
    time_varying = tuple(item for item in kpis if item["is_time_varying"] is True)
    flat = tuple(item for item in kpis if item["is_flat"] is True)
    missing = tuple(item for item in kpis if item["observed"] is not True)
    zero_latest = tuple(item for item in kpis if item["latest_is_zero"] is True)
    activity_context = _mapping(calibration.get("activity_context"))
    activity_active = activity_context.get("active") is True
    dynamic_status = _dynamic_status(
        sample_count=_int(calibration.get("sample_count")),
        sim_time_span_s=_float(calibration.get("sim_time_span_s")),
        kpi_count=len(kpis),
        time_varying_count=len(time_varying),
        missing_count=len(missing),
        activity_active=activity_active,
    )
    payload: dict[str, object] = {
        "version": "v1",
        "status_id": NETWORK_KPI_DYNAMIC_STATUS_V1_ID,
        "source": "NETWORK_KPI_CALIBRATION_V1",
        "calibration_id": str(calibration.get("calibration_id", "")),
        "metric_model": str(calibration.get("metric_model", "FLOW_LEVEL_PROXY")),
        "packet_level_simulation": False,
        "frontend_inference_required": False,
        "sample_count": _int(calibration.get("sample_count")),
        "sim_time_span_s": _float(calibration.get("sim_time_span_s")),
        "activity_active": activity_active,
        "dynamic_status": dynamic_status,
        "kpi_count": len(kpis),
        "time_varying_kpi_count": len(time_varying),
        "flat_kpi_count": len(flat),
        "missing_kpi_count": len(missing),
        "zero_latest_kpi_count": len(zero_latest),
        "dynamic_metric_names": tuple(item["metric"] for item in time_varying),
        "flat_metric_names": tuple(item["metric"] for item in flat),
        "zero_latest_metric_names": tuple(item["metric"] for item in zero_latest),
        "items": kpis,
        "operator_summary": _operator_summary(dynamic_status),
        "blocking_reasons": _blocking_reasons(
            dynamic_status=dynamic_status,
            kpis=kpis,
            sample_count=_int(calibration.get("sample_count")),
            sim_time_span_s=_float(calibration.get("sim_time_span_s")),
            activity_active=activity_active,
        ),
        "recommended_next_action": _recommended_next_action(dynamic_status),
        "model_assumptions": (
            "Dynamic status is derived from backend network_kpi_calibration_v1.",
            "The summary audits flow-level proxy KPI movement; it does not recompute formulas.",
            "Loss and delay-variation remain proxy metrics, not packet-level measurements.",
        ),
    }
    payload["status_hash"] = stable_hash_payload(payload)
    return payload


def _kpi_item(item: Mapping[str, Any]) -> dict[str, object]:
    metric = str(item.get("metric", ""))
    variation_status = str(item.get("variation_status", "MISSING_SAMPLE_VALUE"))
    observed = item.get("observed") is True
    latest_is_zero = item.get("latest_is_zero") is True
    is_time_varying = variation_status == "TIME_VARYING"
    is_flat = variation_status.startswith("FLAT")
    return {
        "metric": metric,
        "display_name": _DISPLAY_NAMES.get(metric, metric),
        "runtime_summary_key": str(item.get("runtime_summary_key", "")),
        "sample_key": str(item.get("sample_key", "")),
        "unit": str(item.get("unit", "")),
        "observed": observed,
        "variation_status": variation_status,
        "is_time_varying": is_time_varying,
        "is_flat": is_flat,
        "latest_is_zero": latest_is_zero,
        "first_value": _optional_float(item.get("first_value")),
        "latest_value": _optional_float(item.get("latest_value")),
        "minimum_value": _optional_float(item.get("minimum_value")),
        "maximum_value": _optional_float(item.get("maximum_value")),
        "absolute_delta": _float(item.get("absolute_delta")),
        "endpoint_delta": _float(item.get("endpoint_delta")),
        "relative_delta": _float(item.get("relative_delta")),
        "flat_reason": str(item.get("flat_reason", "")),
        "visibility": _item_visibility(
            observed=observed,
            variation_status=variation_status,
            latest_is_zero=latest_is_zero,
        ),
        "zero_value_note": _zero_value_note(metric, latest_is_zero),
    }


def _dynamic_status(
    *,
    sample_count: int,
    sim_time_span_s: float,
    kpi_count: int,
    time_varying_count: int,
    missing_count: int,
    activity_active: bool,
) -> str:
    if kpi_count == 0 or missing_count == kpi_count:
        return "NO_KPI_EVIDENCE"
    if sample_count < 2 or sim_time_span_s <= 0.0:
        return "INSUFFICIENT_SERIES"
    if time_varying_count >= 2:
        return "DYNAMIC"
    if time_varying_count == 1:
        return "PARTIALLY_DYNAMIC"
    if activity_active:
        return "FLAT_WITH_ACTIVITY"
    return "FLAT_NO_ACTIVITY"


def _item_visibility(
    *,
    observed: bool,
    variation_status: str,
    latest_is_zero: bool,
) -> str:
    if not observed:
        return "WAIT_FOR_BACKEND_SAMPLE"
    if variation_status == "TIME_VARYING":
        return "SHOW_DYNAMIC_CHART"
    if latest_is_zero:
        return "SHOW_ZERO_VALUE_REASON"
    if variation_status.startswith("FLAT"):
        return "SHOW_FLAT_REASON"
    return "WAIT_FOR_MORE_SAMPLES"


def _zero_value_note(metric: str, latest_is_zero: bool) -> str:
    if not latest_is_zero:
        return ""
    if metric == "EFFECTIVE_LOSS_PROXY":
        return "Latest loss proxy is zero because the flow-level proxy inputs resolved to no loss at this sample."
    if metric == "EFFECTIVE_DELAY_VARIATION_PROXY":
        return "Latest delay-variation proxy is zero because the selected flow-level latency/pressure samples did not vary."
    return "Latest value is zero in the backend KPI calibration sample."


def _blocking_reasons(
    *,
    dynamic_status: str,
    kpis: tuple[dict[str, object], ...],
    sample_count: int,
    sim_time_span_s: float,
    activity_active: bool,
) -> tuple[dict[str, object], ...]:
    if dynamic_status == "NO_KPI_EVIDENCE":
        return (
            {
                "reason_type": "MISSING_KPI_EVIDENCE",
                "message": "No observed network KPI calibration rows are available.",
            },
        )
    if dynamic_status == "INSUFFICIENT_SERIES":
        return (
            {
                "reason_type": "INSUFFICIENT_SERIES",
                "sample_count": sample_count,
                "sim_time_span_s": sim_time_span_s,
                "message": "At least two samples over positive simulation time are required.",
            },
        )
    if dynamic_status in {"FLAT_WITH_ACTIVITY", "FLAT_NO_ACTIVITY"}:
        flat_metrics = tuple(item["metric"] for item in kpis if item["is_flat"] is True)
        return (
            {
                "reason_type": "FLAT_KPI_SERIES",
                "activity_active": activity_active,
                "flat_metric_names": flat_metrics,
                "message": "Observed KPI samples are flat under the current flow-level proxy inputs.",
            },
        )
    return ()


def _operator_summary(dynamic_status: str) -> str:
    if dynamic_status == "DYNAMIC":
        return "Network KPI samples show multi-metric time variation."
    if dynamic_status == "PARTIALLY_DYNAMIC":
        return "Only one network KPI currently varies over simulation time."
    if dynamic_status == "FLAT_WITH_ACTIVITY":
        return "Business activity exists, but network KPI proxy samples are flat."
    if dynamic_status == "FLAT_NO_ACTIVITY":
        return "Network KPI proxy samples are flat and no active demand context was observed."
    if dynamic_status == "INSUFFICIENT_SERIES":
        return "More runtime samples are required before dynamic behavior can be assessed."
    return "Network KPI calibration evidence is missing."


def _recommended_next_action(dynamic_status: str) -> str:
    if dynamic_status in {"DYNAMIC", "PARTIALLY_DYNAMIC"}:
        return "RENDER_BACKEND_KPI_SERIES_AND_EXPLANATION"
    if dynamic_status == "FLAT_WITH_ACTIVITY":
        return "CHECK_PRESSURE_INPUTS_AND_NETWORK_STRESS_TEMPLATE"
    if dynamic_status == "FLAT_NO_ACTIVITY":
        return "START_OR_ADVANCE_RUNTIME_WITH_ACTIVE_TRAFFIC"
    if dynamic_status == "INSUFFICIENT_SERIES":
        return "COLLECT_MORE_RUNTIME_SAMPLES"
    return "CHECK_METRICS_COLLECTION_AND_RUNTIME_STATUS"


def _records(value: object) -> tuple[Mapping[str, Any], ...]:
    if not isinstance(value, (list, tuple)):
        return ()
    return tuple(item for item in value if isinstance(item, Mapping))


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _int(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return 0
    return max(0, int(value))


def _float(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return 0.0
    return float(value)


def _optional_float(value: object) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


__all__ = [
    "NETWORK_KPI_DYNAMIC_STATUS_V1_ID",
    "NetworkKpiDynamicStatusV1",
    "build_network_kpi_dynamic_status_v1",
]
