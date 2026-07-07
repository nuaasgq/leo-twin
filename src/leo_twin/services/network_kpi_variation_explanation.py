"""Product-facing network KPI variation explanation summary v1."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from leo_twin.services.runtime_reproducibility import stable_hash_payload


NETWORK_KPI_VARIATION_EXPLANATION_V1_ID = (
    "leo_twin.network_kpi_variation_explanation.v1"
)

NetworkKpiVariationExplanationV1 = dict[str, object]


def build_network_kpi_variation_explanation_v1(
    metrics: Mapping[str, Any],
    provenance: Mapping[str, Any],
    calibration: Mapping[str, Any],
    formula_evidence: Mapping[str, Any],
) -> NetworkKpiVariationExplanationV1:
    """Explain why backend network KPI values moved or stayed flat.

    The explanation is a product-facing observation summary. It does not
    change KPI formulas, replay events, or introduce packet-level simulation.
    """

    if not isinstance(metrics, Mapping):
        raise TypeError("metrics must be a mapping")
    if not isinstance(provenance, Mapping):
        raise TypeError("provenance must be a mapping")
    if not isinstance(calibration, Mapping):
        raise TypeError("calibration must be a mapping")
    if not isinstance(formula_evidence, Mapping):
        raise TypeError("formula_evidence must be a mapping")

    provenance_by_metric = _records_by_metric(provenance.get("kpis"))
    calibration_by_metric = _records_by_metric(calibration.get("kpis"))
    formula_by_metric = _records_by_metric(formula_evidence.get("kpis"))
    metric_order = _metric_order(
        formula_by_metric,
        provenance_by_metric,
        calibration_by_metric,
    )
    activity_context = _mapping(calibration.get("activity_context"))
    activity_active = activity_context.get("active") is True
    items = tuple(
        _explanation_item(
            metric=metric,
            metrics=metrics,
            provenance=provenance_by_metric.get(metric),
            calibration=calibration_by_metric.get(metric),
            formula=formula_by_metric.get(metric),
            activity_active=activity_active,
        )
        for metric in metric_order
    )
    time_varying = tuple(
        item for item in items if item["variation_status"] == "TIME_VARYING"
    )
    flat = tuple(
        item for item in items if str(item["variation_status"]).startswith("FLAT")
    )
    zero_latest = tuple(item for item in items if item["latest_is_zero"] is True)
    missing_explanation = tuple(
        item
        for item in items
        if str(item["explanation_status"]).startswith("MISSING")
        or item["explanation_status"] == "FORMULA_ONLY_NO_TIME_SERIES"
    )
    payload: dict[str, object] = {
        "version": "v1",
        "explanation_id": NETWORK_KPI_VARIATION_EXPLANATION_V1_ID,
        "source": "NETWORK_KPI_FORMULA_EVIDENCE_V1_AND_CALIBRATION_V1",
        "provenance_id": str(provenance.get("provenance_id", "")),
        "calibration_id": str(calibration.get("calibration_id", "")),
        "formula_evidence_id": str(formula_evidence.get("evidence_id", "")),
        "metric_model": str(
            formula_evidence.get(
                "metric_model",
                provenance.get(
                    "metric_model",
                    metrics.get("network_quality_metric_model", "FLOW_LEVEL_PROXY"),
                ),
            )
        ),
        "packet_level_simulation": bool(
            provenance.get("packet_level_simulation") is True
            or calibration.get("packet_level_simulation") is True
            or formula_evidence.get("packet_level_simulation") is True
        ),
        "sample_count": _int(calibration.get("sample_count")),
        "sim_time_span_s": _number(calibration.get("sim_time_span_s")) or 0.0,
        "activity_context": {
            "active": activity_active,
            "requested_route_demand_mbps": _number(
                activity_context.get("requested_route_demand_mbps")
            )
            or 0.0,
            "offered_route_capacity_mbps": _number(
                activity_context.get("offered_route_capacity_mbps")
            )
            or 0.0,
            "recent_flow_count": _number(activity_context.get("recent_flow_count"))
            or 0.0,
            "available_route_count": _number(
                activity_context.get("available_route_count")
            )
            or 0.0,
        },
        "kpi_count": len(items),
        "time_varying_kpi_count": len(time_varying),
        "flat_kpi_count": len(flat),
        "zero_latest_kpi_count": len(zero_latest),
        "missing_explanation_count": len(missing_explanation),
        "explanation_status": _explanation_status(
            kpi_count=len(items),
            sample_count=_int(calibration.get("sample_count")),
            sim_time_span_s=_number(calibration.get("sim_time_span_s")) or 0.0,
            time_varying_count=len(time_varying),
            activity_active=activity_active,
        ),
        "items": items,
        "model_assumptions": _model_assumptions(),
        "caveats": _caveats(),
    }
    payload["explanation_hash"] = stable_hash_payload(payload)
    return payload


def _explanation_item(
    *,
    metric: str,
    metrics: Mapping[str, Any],
    provenance: Mapping[str, Any] | None,
    calibration: Mapping[str, Any] | None,
    formula: Mapping[str, Any] | None,
    activity_active: bool,
) -> dict[str, object]:
    provenance_record = _mapping(provenance)
    calibration_record = _mapping(calibration)
    formula_record = _mapping(formula)
    runtime_summary_key = str(
        formula_record.get(
            "runtime_summary_key",
            calibration_record.get(
                "runtime_summary_key",
                provenance_record.get("runtime_summary_key", ""),
            ),
        )
    )
    variation_status = str(
        formula_record.get(
            "variation_status",
            calibration_record.get("variation_status", "MISSING_TIME_SERIES"),
        )
    )
    evidence_status = str(
        formula_record.get("evidence_status", "MISSING_FORMULA_EVIDENCE")
    )
    selected_inputs = tuple(
        _selected_input_record(item) for item in _records(formula_record.get("selected_inputs"))
    )
    latest_value = _number(calibration_record.get("latest_value"))
    if latest_value is None:
        latest_value = _number(formula_record.get("current_value"))
    current_value = _json_value(
        formula_record.get(
            "current_value",
            provenance_record.get("current_value", metrics.get(runtime_summary_key)),
        )
    )
    explanation_status = _item_explanation_status(
        runtime_status=str(formula_record.get("status", provenance_record.get("status", ""))),
        variation_status=variation_status,
        evidence_status=evidence_status,
    )
    flat_reason = str(
        formula_record.get("flat_reason", calibration_record.get("flat_reason", ""))
    )
    display_name = str(
        formula_record.get(
            "display_name",
            provenance_record.get("display_name", metric),
        )
    )
    return {
        "metric": metric,
        "display_name": display_name,
        "runtime_summary_key": runtime_summary_key,
        "sample_key": str(calibration_record.get("sample_key", "")),
        "current_value": current_value,
        "unit": str(
            formula_record.get("unit", calibration_record.get("unit", provenance_record.get("unit", "")))
        ),
        "observed": str(
            formula_record.get("status", provenance_record.get("status", ""))
        )
        == "OBSERVED",
        "observed_source": str(formula_record.get("observed_source", "")),
        "observed_source_label": str(
            formula_record.get("observed_source_label", "")
        ),
        "formula_summary": str(
            formula_record.get(
                "formula_summary",
                provenance_record.get("formula_summary", ""),
            )
        ),
        "selected_input_count": _int(formula_record.get("selected_input_count")),
        "selected_observed_input_count": _int(
            formula_record.get("selected_observed_input_count")
        ),
        "missing_selected_input_count": _int(
            formula_record.get("missing_selected_input_count")
        ),
        "selected_inputs": selected_inputs,
        "first_value": _number(calibration_record.get("first_value")),
        "latest_value": latest_value,
        "minimum_value": _number(calibration_record.get("minimum_value")),
        "maximum_value": _number(calibration_record.get("maximum_value")),
        "absolute_delta": _number(calibration_record.get("absolute_delta")) or 0.0,
        "endpoint_delta": _number(calibration_record.get("endpoint_delta")) or 0.0,
        "relative_delta": _number(calibration_record.get("relative_delta")) or 0.0,
        "latest_is_zero": calibration_record.get("latest_is_zero") is True,
        "variation_status": variation_status,
        "flat_reason": flat_reason,
        "evidence_status": evidence_status,
        "explanation_status": explanation_status,
        "trust_label": _trust_label(explanation_status, variation_status),
        "user_explanation": _user_explanation(
            metric=metric,
            display_name=display_name,
            variation_status=variation_status,
            evidence_status=evidence_status,
            flat_reason=flat_reason,
            activity_active=activity_active,
            selected_input_count=len(selected_inputs),
        ),
    }


def _records_by_metric(value: object) -> dict[str, Mapping[str, Any]]:
    result: dict[str, Mapping[str, Any]] = {}
    for item in _records(value):
        metric = str(item.get("metric", ""))
        if metric:
            result[metric] = item
    return result


def _metric_order(*groups: Mapping[str, Mapping[str, Any]]) -> tuple[str, ...]:
    seen: set[str] = set()
    ordered: list[str] = []
    for group in groups:
        for metric in group:
            if metric not in seen:
                ordered.append(metric)
                seen.add(metric)
    return tuple(ordered)


def _selected_input_record(input_record: Mapping[str, Any]) -> dict[str, object]:
    return {
        "field": str(input_record.get("field", "")),
        "current_value": _json_value(input_record.get("current_value")),
        "observed": input_record.get("observed") is True,
        "role": str(input_record.get("role", "")),
        "selection_reason": str(input_record.get("selection_reason", "")),
    }


def _explanation_status(
    *,
    kpi_count: int,
    sample_count: int,
    sim_time_span_s: float,
    time_varying_count: int,
    activity_active: bool,
) -> str:
    if kpi_count == 0:
        return "NO_KPI_EVIDENCE"
    if sample_count < 2 or sim_time_span_s <= 0.0:
        return "INSUFFICIENT_SERIES"
    if time_varying_count > 0:
        return "TIME_VARIATION_EXPLAINED"
    if activity_active:
        return "FLAT_UNDER_ACTIVITY_EXPLAINED"
    return "FLAT_NO_ACTIVITY_EXPLAINED"


def _item_explanation_status(
    *,
    runtime_status: str,
    variation_status: str,
    evidence_status: str,
) -> str:
    if runtime_status and runtime_status != "OBSERVED":
        return "MISSING_RUNTIME_VALUE"
    if evidence_status in {"MISSING_RUNTIME_VALUE", "MISSING_SELECTED_INPUT"}:
        return evidence_status
    if variation_status == "TIME_VARYING":
        return "TIME_VARIATION_EXPLAINED"
    if variation_status == "FLAT_ZERO":
        return "FLAT_ZERO_EXPLAINED"
    if variation_status == "FLAT_NONZERO":
        return "FLAT_NONZERO_EXPLAINED"
    if variation_status == "INSUFFICIENT_SAMPLES":
        return "INSUFFICIENT_SERIES"
    if variation_status in {"MISSING_CALIBRATION", "MISSING_SAMPLE_VALUE", "MISSING_TIME_SERIES"}:
        return "FORMULA_ONLY_NO_TIME_SERIES"
    return "FORMULA_READY"


def _trust_label(explanation_status: str, variation_status: str) -> str:
    if explanation_status == "TIME_VARIATION_EXPLAINED":
        return "time-varying flow-level proxy"
    if explanation_status in {"FLAT_ZERO_EXPLAINED", "FLAT_NONZERO_EXPLAINED"}:
        return "flat flow-level proxy"
    if explanation_status == "INSUFFICIENT_SERIES":
        return "needs more runtime samples"
    if explanation_status.startswith("MISSING"):
        return "missing backend evidence"
    if variation_status.startswith("FLAT"):
        return "flat flow-level proxy"
    return "formula-only flow-level proxy"


def _user_explanation(
    *,
    metric: str,
    display_name: str,
    variation_status: str,
    evidence_status: str,
    flat_reason: str,
    activity_active: bool,
    selected_input_count: int,
) -> str:
    label = display_name or metric
    if evidence_status == "MISSING_RUNTIME_VALUE":
        return (
            f"{label} 缺少后端运行值，暂时无法解释该 KPI 是否随仿真时间变化。"
        )
    if evidence_status == "MISSING_SELECTED_INPUT":
        return (
            f"{label} 已有运行值，但至少一个后端选中公式输入未暴露到 metrics_summary。"
        )
    if variation_status == "TIME_VARYING":
        return (
            f"{label} 随仿真时间变化，因为后端选中的 {selected_input_count} "
            "个流级输入和 KPI 时间序列样本发生变化。"
        )
    if variation_status == "FLAT_ZERO":
        return (
            f"{label} 保持为零。后端最新值为零，需要结合零值原因和业务活动上下文判断；"
            "该值不是包级丢包或包级抖动测量。"
        )
    if variation_status == "FLAT_NONZERO":
        reason = _translated_flat_reason(flat_reason)
        return f"{label} 保持不变，因为{reason}。"
    if variation_status == "INSUFFICIENT_SAMPLES":
        return (
            f"{label} 至少需要两个数值型 KPI 样本，才能证明是否存在时间变化。"
        )
    if activity_active:
        return (
            f"{label} 当前已有公式证据，但在业务活动存在时仍缺少完整时间序列证据。"
        )
    return f"{label} 当前已有公式证据，但尚未观测到时间变化。"


def _translated_flat_reason(flat_reason: str) -> str:
    if not flat_reason:
        return "选中的路由、业务流或压力输入没有变化"
    normalized = flat_reason.lower()
    if "observed samples are constant" in normalized:
        return "观测样本保持常数，路由、业务流或压力输入没有变化"
    if "all observed samples are zero" in normalized:
        return "所有观测样本为零，需要结合零值原因和活动上下文"
    if "pressure inputs did not change" in normalized:
        return "选中的压力输入没有变化"
    if "values are non-zero but unchanged" in normalized:
        return "取值非零但未变化"
    if "unchanged pressure inputs" in normalized:
        return "选中的压力输入没有变化"
    return flat_reason


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


def _number(value: object) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    if value != value or value in {float("inf"), float("-inf")}:
        return None
    return float(value)


def _json_value(value: object) -> str | int | float | bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float, str)):
        return value
    return None


def _model_assumptions() -> tuple[str, ...]:
    return (
        "网络 KPI 变化解释来自后端 KPI provenance、选中公式输入和确定性运行时 KPI 样本。",
        "所有网络指标仍是流级代理；该摘要不会引入包级仿真。",
        "当选中的路由、业务流、压力或时间驱动输入保持不变时，KPI 平坦是可解释的。",
    )


def _caveats() -> tuple[str, ...]:
    return (
        "变化解释 v1 只是观测摘要，不改变任何 KPI 公式。",
        "代理指标随时间变化表示后端样本发生变化，不代表包级测量保真度。",
        "当当前场景没有改变压力输入时，丢包或抖动代理保持平坦也可能是合理结果。",
    )


__all__ = [
    "NETWORK_KPI_VARIATION_EXPLANATION_V1_ID",
    "NetworkKpiVariationExplanationV1",
    "build_network_kpi_variation_explanation_v1",
]
