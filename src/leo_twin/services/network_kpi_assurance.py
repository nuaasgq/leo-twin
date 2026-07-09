"""Product-facing network KPI assurance summary v2."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from leo_twin.services.runtime_reproducibility import stable_hash_payload


NETWORK_KPI_ASSURANCE_V2_ID = "leo_twin.network_kpi_assurance.v2"

NetworkKpiAssuranceV2 = dict[str, object]


def build_network_kpi_assurance_v2(
    metrics: Mapping[str, Any],
    provenance: Mapping[str, Any],
    credibility: Mapping[str, Any],
    calibration: Mapping[str, Any],
    dynamic_status: Mapping[str, Any],
    formula_evidence: Mapping[str, Any],
    variation_explanation: Mapping[str, Any],
) -> NetworkKpiAssuranceV2:
    """Build a compact assurance summary for network KPI display and review.

    The function does not recompute KPI formulas. It joins already generated
    backend evidence so UI and export consumers can distinguish dynamic,
    explained-flat, insufficient, and missing-evidence states.
    """

    _require_mapping(metrics, "metrics")
    _require_mapping(provenance, "provenance")
    _require_mapping(credibility, "credibility")
    _require_mapping(calibration, "calibration")
    _require_mapping(dynamic_status, "dynamic_status")
    _require_mapping(formula_evidence, "formula_evidence")
    _require_mapping(variation_explanation, "variation_explanation")

    provenance_by_metric = _records_by_metric(provenance.get("kpis"))
    calibration_by_metric = _records_by_metric(calibration.get("kpis"))
    dynamic_by_metric = _records_by_metric(dynamic_status.get("items"))
    formula_by_metric = _records_by_metric(formula_evidence.get("kpis"))
    variation_by_metric = _records_by_metric(variation_explanation.get("items"))
    metric_order = _metric_order(
        variation_by_metric,
        formula_by_metric,
        dynamic_by_metric,
        calibration_by_metric,
        provenance_by_metric,
    )
    items = tuple(
        _assurance_item(
            metric=metric,
            metrics=metrics,
            provenance=provenance_by_metric.get(metric),
            calibration=calibration_by_metric.get(metric),
            dynamic=dynamic_by_metric.get(metric),
            formula=formula_by_metric.get(metric),
            variation=variation_by_metric.get(metric),
        )
        for metric in metric_order
    )
    packet_level_simulation = any(
        mapping.get("packet_level_simulation") is True
        for mapping in (
            provenance,
            credibility,
            calibration,
            dynamic_status,
            formula_evidence,
            variation_explanation,
        )
    )
    assurance_status = _assurance_status(
        packet_level_simulation=packet_level_simulation,
        credibility_status=str(credibility.get("credibility_status", "")),
        formula_status=str(formula_evidence.get("formula_evidence_status", "")),
        dynamic_status=str(dynamic_status.get("dynamic_status", "")),
        explanation_status=str(variation_explanation.get("explanation_status", "")),
        missing_item_count=sum(
            1 for item in items if item["assurance_item_status"] == "MISSING_EVIDENCE"
        ),
    )
    activity_context = _mapping(calibration.get("activity_context"))
    payload: dict[str, object] = {
        "version": "v2",
        "summary_id": NETWORK_KPI_ASSURANCE_V2_ID,
        "source": (
            "network_kpi_provenance_v2 + network_kpi_calibration_v1 + "
            "network_kpi_variation_explanation_v1"
        ),
        "metric_model": str(
            provenance.get(
                "metric_model",
                metrics.get("network_quality_metric_model", "FLOW_LEVEL_PROXY"),
            )
        ),
        "packet_level_simulation": packet_level_simulation,
        "frontend_inference_required": False,
        "assurance_status": assurance_status,
        "credibility_status": str(credibility.get("credibility_status", "")),
        "dynamic_status": str(dynamic_status.get("dynamic_status", "")),
        "formula_evidence_status": str(
            formula_evidence.get("formula_evidence_status", "")
        ),
        "variation_explanation_status": str(
            variation_explanation.get("explanation_status", "")
        ),
        "sample_count": _int(calibration.get("sample_count")),
        "sim_time_span_s": _float(calibration.get("sim_time_span_s")),
        "activity_context": {
            "active": activity_context.get("active") is True,
            "requested_route_demand_mbps": _float(
                activity_context.get("requested_route_demand_mbps")
            ),
            "offered_route_capacity_mbps": _float(
                activity_context.get("offered_route_capacity_mbps")
            ),
            "recent_flow_count": _float(activity_context.get("recent_flow_count")),
            "available_route_count": _float(
                activity_context.get("available_route_count")
            ),
        },
        "kpi_count": len(items),
        "time_varying_kpi_count": sum(
            1 for item in items if item["variation_status"] == "TIME_VARYING"
        ),
        "flat_kpi_count": sum(
            1 for item in items if str(item["variation_status"]).startswith("FLAT")
        ),
        "zero_latest_kpi_count": sum(
            1 for item in items if item["latest_is_zero"] is True
        ),
        "missing_evidence_kpi_count": sum(
            1 for item in items if item["assurance_item_status"] == "MISSING_EVIDENCE"
        ),
        "chart_ready_kpi_count": sum(
            1 for item in items if item["display_policy"] == "SHOW_TIME_SERIES"
        ),
        "explained_flat_kpi_count": sum(
            1 for item in items if item["assurance_item_status"] == "EXPLAINED_FLAT"
        ),
        "items": items,
        "operator_summary": _operator_summary(assurance_status),
        "recommended_next_action": _recommended_next_action(assurance_status),
        "model_assumptions": (
            "Assurance v2 audits backend-generated flow-level KPI evidence only.",
            "It does not recompute throughput, latency, loss, or delay-variation formulas.",
            "Loss and delay variation are proxy metrics, not packet-level measurements.",
        ),
        "caveats": _caveats(assurance_status),
    }
    payload["assurance_hash"] = stable_hash_payload(payload)
    return payload


def _assurance_item(
    *,
    metric: str,
    metrics: Mapping[str, Any],
    provenance: Mapping[str, Any] | None,
    calibration: Mapping[str, Any] | None,
    dynamic: Mapping[str, Any] | None,
    formula: Mapping[str, Any] | None,
    variation: Mapping[str, Any] | None,
) -> dict[str, object]:
    provenance_record = _mapping(provenance)
    calibration_record = _mapping(calibration)
    dynamic_record = _mapping(dynamic)
    formula_record = _mapping(formula)
    variation_record = _mapping(variation)
    runtime_key = str(
        variation_record.get(
            "runtime_summary_key",
            formula_record.get(
                "runtime_summary_key",
                calibration_record.get(
                    "runtime_summary_key",
                    provenance_record.get("runtime_summary_key", ""),
                ),
            ),
        )
    )
    variation_status = str(
        variation_record.get(
            "variation_status",
            dynamic_record.get(
                "variation_status",
                calibration_record.get("variation_status", "MISSING_TIME_SERIES"),
            ),
        )
    )
    evidence_status = str(
        variation_record.get(
            "evidence_status",
            formula_record.get("evidence_status", ""),
        )
    )
    explanation_status = str(
        variation_record.get("explanation_status", "")
    )
    current_value = _json_value(
        variation_record.get(
            "current_value",
            formula_record.get(
                "current_value",
                provenance_record.get("current_value", metrics.get(runtime_key)),
            ),
        )
    )
    latest_is_zero = (
        variation_record.get("latest_is_zero") is True
        or dynamic_record.get("latest_is_zero") is True
        or calibration_record.get("latest_is_zero") is True
    )
    item_status = _item_status(
        evidence_status=evidence_status,
        explanation_status=explanation_status,
        variation_status=variation_status,
        current_value_present=current_value is not None,
    )
    display_policy = _display_policy(item_status, variation_status, latest_is_zero)
    item: dict[str, object] = {
        "metric": metric,
        "display_name": str(
            variation_record.get(
                "display_name",
                provenance_record.get("display_name", metric),
            )
        ),
        "runtime_summary_key": runtime_key,
        "sample_key": str(
            dynamic_record.get(
                "sample_key",
                calibration_record.get("sample_key", ""),
            )
        ),
        "current_value": current_value,
        "latest_value": _json_value(
            variation_record.get(
                "latest_value",
                calibration_record.get("latest_value"),
            )
        ),
        "unit": str(
            variation_record.get(
                "unit",
                provenance_record.get("unit", calibration_record.get("unit", "")),
            )
        ),
        "observed_source": str(
            variation_record.get(
                "observed_source",
                _mapping(provenance_record.get("observed_source")).get("source", ""),
            )
        ),
        "variation_status": variation_status,
        "evidence_status": evidence_status,
        "explanation_status": explanation_status,
        "assurance_item_status": item_status,
        "display_policy": display_policy,
        "latest_is_zero": latest_is_zero,
        "first_value": _optional_float(calibration_record.get("first_value")),
        "minimum_value": _optional_float(calibration_record.get("minimum_value")),
        "maximum_value": _optional_float(calibration_record.get("maximum_value")),
        "absolute_delta": _float(calibration_record.get("absolute_delta")),
        "relative_delta": _float(calibration_record.get("relative_delta")),
        "flat_reason": str(
            variation_record.get(
                "flat_reason",
                calibration_record.get("flat_reason", ""),
            )
        ),
        "zero_value_note": str(dynamic_record.get("zero_value_note", "")),
        "user_explanation": str(variation_record.get("user_explanation", "")),
        "trust_label": str(variation_record.get("trust_label", "")),
    }
    item["item_hash"] = stable_hash_payload(item)
    return item


def _assurance_status(
    *,
    packet_level_simulation: bool,
    credibility_status: str,
    formula_status: str,
    dynamic_status: str,
    explanation_status: str,
    missing_item_count: int,
) -> str:
    if packet_level_simulation:
        return "INVALID_PACKET_LEVEL_EVIDENCE"
    if missing_item_count > 0 or "MISSING" in credibility_status:
        return "MISSING_BACKEND_EVIDENCE"
    if dynamic_status == "INSUFFICIENT_SERIES" or explanation_status == "INSUFFICIENT_SERIES":
        return "NEEDS_MORE_RUNTIME_SAMPLES"
    if dynamic_status in {"DYNAMIC", "PARTIALLY_DYNAMIC"}:
        if formula_status.startswith("FORMULA"):
            return "TIME_VARYING_FLOW_PROXY_READY"
        return "TIME_VARYING_PARTIAL_EVIDENCE"
    if dynamic_status == "FLAT_WITH_ACTIVITY":
        return "FLAT_UNDER_ACTIVITY_EXPLAINED"
    if dynamic_status == "FLAT_NO_ACTIVITY":
        return "FLAT_NO_ACTIVITY_EXPLAINED"
    if credibility_status == "COMPLETE_FLOW_LEVEL_PROXY":
        return "FLOW_PROXY_EVIDENCE_READY"
    return "PARTIAL_FLOW_PROXY_EVIDENCE"


def _item_status(
    *,
    evidence_status: str,
    explanation_status: str,
    variation_status: str,
    current_value_present: bool,
) -> str:
    if not current_value_present or evidence_status == "MISSING_RUNTIME_VALUE":
        return "MISSING_EVIDENCE"
    if explanation_status == "TIME_VARIATION_EXPLAINED" or variation_status == "TIME_VARYING":
        return "TIME_VARYING"
    if variation_status.startswith("FLAT"):
        return "EXPLAINED_FLAT"
    if variation_status == "INSUFFICIENT_SAMPLES":
        return "NEEDS_MORE_SAMPLES"
    return "FORMULA_READY"


def _display_policy(
    item_status: str,
    variation_status: str,
    latest_is_zero: bool,
) -> str:
    if item_status == "MISSING_EVIDENCE":
        return "WAIT_FOR_BACKEND_EVIDENCE"
    if item_status == "NEEDS_MORE_SAMPLES":
        return "WAIT_FOR_MORE_SAMPLES"
    if variation_status == "TIME_VARYING":
        return "SHOW_TIME_SERIES"
    if latest_is_zero:
        return "SHOW_ZERO_VALUE_REASON"
    if variation_status.startswith("FLAT"):
        return "SHOW_FLAT_REASON"
    return "SHOW_CURRENT_VALUE_WITH_FORMULA"


def _operator_summary(assurance_status: str) -> str:
    return {
        "TIME_VARYING_FLOW_PROXY_READY": (
            "Network KPIs have backend time-series movement and formula evidence."
        ),
        "TIME_VARYING_PARTIAL_EVIDENCE": (
            "Network KPIs move over time, but some formula evidence is partial."
        ),
        "FLAT_UNDER_ACTIVITY_EXPLAINED": (
            "Business activity exists, but KPI proxy inputs are flat or zero; the flat state is explained."
        ),
        "FLAT_NO_ACTIVITY_EXPLAINED": (
            "KPI proxy samples are flat because no active demand context was observed."
        ),
        "NEEDS_MORE_RUNTIME_SAMPLES": (
            "More runtime samples are required before KPI movement can be assessed."
        ),
        "MISSING_BACKEND_EVIDENCE": (
            "One or more KPI rows are missing backend evidence."
        ),
        "INVALID_PACKET_LEVEL_EVIDENCE": (
            "Packet-level evidence was marked present, which is outside the current contract."
        ),
    }.get(assurance_status, "Network KPI flow-level proxy evidence is partial.")


def _recommended_next_action(assurance_status: str) -> str:
    return {
        "TIME_VARYING_FLOW_PROXY_READY": "DISPLAY_DYNAMIC_KPI_SERIES",
        "TIME_VARYING_PARTIAL_EVIDENCE": "DISPLAY_DYNAMIC_KPI_SERIES_WITH_CAVEATS",
        "FLAT_UNDER_ACTIVITY_EXPLAINED": "DISPLAY_FLAT_REASON_AND_PRESSURE_INPUTS",
        "FLAT_NO_ACTIVITY_EXPLAINED": "START_OR_ADVANCE_ACTIVE_TRAFFIC",
        "NEEDS_MORE_RUNTIME_SAMPLES": "COLLECT_MORE_RUNTIME_SAMPLES",
        "MISSING_BACKEND_EVIDENCE": "CHECK_METRICS_COLLECTION",
        "INVALID_PACKET_LEVEL_EVIDENCE": "CHECK_PRODUCT_CONTRACT_BOUNDARY",
    }.get(assurance_status, "DISPLAY_FLOW_PROXY_CAVEATS")


def _caveats(assurance_status: str) -> tuple[str, ...]:
    caveats = [
        "All values are deterministic flow-level proxy evidence.",
        "Loss and delay-variation are not packet-level loss or jitter measurements.",
    ]
    if assurance_status.startswith("FLAT"):
        caveats.append(
            "Flat KPI series can be valid when route, flow, and pressure inputs do not change."
        )
    if assurance_status == "NEEDS_MORE_RUNTIME_SAMPLES":
        caveats.append("At least two numeric samples over positive simulation time are required.")
    return tuple(caveats)


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
                seen.add(metric)
                ordered.append(metric)
    return tuple(ordered)


def _records(value: object) -> tuple[Mapping[str, Any], ...]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return ()
    return tuple(item for item in value if isinstance(item, Mapping))


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _require_mapping(value: object, name: str) -> None:
    if not isinstance(value, Mapping):
        raise TypeError(f"{name} must be a mapping")


def _json_value(value: object) -> str | int | float | bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float, str)):
        return value
    return None


def _int(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return 0
    return max(0, int(value))


def _float(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return 0.0
    number = float(value)
    if number != number or number in {float("inf"), float("-inf")}:
        return 0.0
    return number


def _optional_float(value: object) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    if number != number or number in {float("inf"), float("-inf")}:
        return None
    return number


__all__ = [
    "NETWORK_KPI_ASSURANCE_V2_ID",
    "NetworkKpiAssuranceV2",
    "build_network_kpi_assurance_v2",
]
