from __future__ import annotations

from leo_twin.services.network_kpi_assurance import (
    NETWORK_KPI_ASSURANCE_V2_ID,
    build_network_kpi_assurance_v2,
)


def test_network_kpi_assurance_reports_dynamic_ready_status() -> None:
    first = _build(
        dynamic_status="DYNAMIC",
        formula_status="FORMULA_AND_TIME_EVIDENCE_READY",
        explanation_status="TIME_VARIATION_EXPLAINED",
        throughput_variation="TIME_VARYING",
        loss_variation="FLAT_ZERO",
    )
    second = _build(
        dynamic_status="DYNAMIC",
        formula_status="FORMULA_AND_TIME_EVIDENCE_READY",
        explanation_status="TIME_VARIATION_EXPLAINED",
        throughput_variation="TIME_VARYING",
        loss_variation="FLAT_ZERO",
    )

    assert first == second
    assert first["version"] == "v2"
    assert first["summary_id"] == NETWORK_KPI_ASSURANCE_V2_ID
    assert first["packet_level_simulation"] is False
    assert first["frontend_inference_required"] is False
    assert first["assurance_status"] == "TIME_VARYING_FLOW_PROXY_READY"
    assert first["recommended_next_action"] == "DISPLAY_DYNAMIC_KPI_SERIES"
    assert first["time_varying_kpi_count"] == 1
    assert first["flat_kpi_count"] == 1
    assert first["zero_latest_kpi_count"] == 1
    assert first["chart_ready_kpi_count"] == 1
    assert first["items"][0]["display_policy"] == "SHOW_TIME_SERIES"
    assert first["items"][1]["display_policy"] == "SHOW_ZERO_VALUE_REASON"
    assert first["assurance_hash"].startswith("sha256:")
    assert first["items"][0]["item_hash"].startswith("sha256:")


def test_network_kpi_assurance_reports_flat_under_activity() -> None:
    summary = _build(
        dynamic_status="FLAT_WITH_ACTIVITY",
        formula_status="FORMULA_READY_FLAT_SERIES",
        explanation_status="FLAT_UNDER_ACTIVITY_EXPLAINED",
        throughput_variation="FLAT_NONZERO",
        loss_variation="FLAT_ZERO",
    )

    assert summary["assurance_status"] == "FLAT_UNDER_ACTIVITY_EXPLAINED"
    assert summary["recommended_next_action"] == (
        "DISPLAY_FLAT_REASON_AND_PRESSURE_INPUTS"
    )
    assert summary["activity_context"]["active"] is True
    assert summary["explained_flat_kpi_count"] == 2
    assert summary["items"][0]["display_policy"] == "SHOW_FLAT_REASON"
    assert summary["items"][1]["display_policy"] == "SHOW_ZERO_VALUE_REASON"


def test_network_kpi_assurance_reports_insufficient_runtime_samples() -> None:
    summary = _build(
        dynamic_status="INSUFFICIENT_SERIES",
        formula_status="FORMULA_READY_INSUFFICIENT_SERIES",
        explanation_status="INSUFFICIENT_SERIES",
        throughput_variation="INSUFFICIENT_SAMPLES",
        loss_variation="INSUFFICIENT_SAMPLES",
        sample_count=1,
        sim_time_span_s=0.0,
    )

    assert summary["assurance_status"] == "NEEDS_MORE_RUNTIME_SAMPLES"
    assert summary["recommended_next_action"] == "COLLECT_MORE_RUNTIME_SAMPLES"
    assert summary["sample_count"] == 1
    assert summary["sim_time_span_s"] == 0.0
    assert summary["items"][0]["display_policy"] == "WAIT_FOR_MORE_SAMPLES"


def _build(
    *,
    dynamic_status: str,
    formula_status: str,
    explanation_status: str,
    throughput_variation: str,
    loss_variation: str,
    sample_count: int = 4,
    sim_time_span_s: float = 30.0,
) -> dict[str, object]:
    metrics = {
        "network_quality_metric_model": "FLOW_LEVEL_PROXY",
        "network_quality_effective_throughput_mbps": 96.0,
        "network_quality_effective_loss_proxy_rate": 0.0,
    }
    provenance = {
        "provenance_id": "leo_twin.network_kpi_provenance.v2",
        "metric_model": "FLOW_LEVEL_PROXY",
        "packet_level_simulation": False,
        "kpis": (
            _provenance_kpi("EFFECTIVE_THROUGHPUT", 96.0, "Mbps"),
            _provenance_kpi("EFFECTIVE_LOSS_PROXY", 0.0, "ratio"),
        ),
    }
    credibility = {
        "credibility_status": "COMPLETE_FLOW_LEVEL_PROXY",
        "packet_level_simulation": False,
    }
    calibration = {
        "sample_count": sample_count,
        "sim_time_span_s": sim_time_span_s,
        "activity_context": {
            "active": True,
            "requested_route_demand_mbps": 120.0,
            "offered_route_capacity_mbps": 160.0,
            "recent_flow_count": 3.0,
            "available_route_count": 4.0,
        },
        "kpis": (
            _calibration_kpi("EFFECTIVE_THROUGHPUT", throughput_variation, 96.0),
            _calibration_kpi("EFFECTIVE_LOSS_PROXY", loss_variation, 0.0),
        ),
    }
    dynamic = {
        "dynamic_status": dynamic_status,
        "packet_level_simulation": False,
        "items": (
            _dynamic_kpi("EFFECTIVE_THROUGHPUT", throughput_variation, 96.0),
            _dynamic_kpi("EFFECTIVE_LOSS_PROXY", loss_variation, 0.0),
        ),
    }
    formula = {
        "formula_evidence_status": formula_status,
        "packet_level_simulation": False,
        "kpis": (
            _formula_kpi("EFFECTIVE_THROUGHPUT", throughput_variation, 96.0),
            _formula_kpi("EFFECTIVE_LOSS_PROXY", loss_variation, 0.0),
        ),
    }
    variation = {
        "explanation_status": explanation_status,
        "packet_level_simulation": False,
        "items": (
            _variation_kpi("EFFECTIVE_THROUGHPUT", throughput_variation, 96.0),
            _variation_kpi("EFFECTIVE_LOSS_PROXY", loss_variation, 0.0),
        ),
    }
    return build_network_kpi_assurance_v2(
        metrics,
        provenance,
        credibility,
        calibration,
        dynamic,
        formula,
        variation,
    )


def _provenance_kpi(metric: str, current_value: float, unit: str) -> dict[str, object]:
    return {
        "metric": metric,
        "display_name": metric.replace("_", " ").title(),
        "runtime_summary_key": f"runtime.{metric.lower()}",
        "current_value": current_value,
        "unit": unit,
        "observed_source": {"source": "RUNTIME_SUMMARY_KEY"},
    }


def _calibration_kpi(
    metric: str,
    variation_status: str,
    latest_value: float,
) -> dict[str, object]:
    return {
        "metric": metric,
        "sample_key": f"sample.{metric.lower()}",
        "runtime_summary_key": f"runtime.{metric.lower()}",
        "unit": "ratio" if "LOSS" in metric else "Mbps",
        "first_value": 80.0 if latest_value else 0.0,
        "latest_value": latest_value,
        "minimum_value": min(80.0, latest_value) if latest_value else 0.0,
        "maximum_value": max(80.0, latest_value) if latest_value else 0.0,
        "absolute_delta": 16.0 if variation_status == "TIME_VARYING" else 0.0,
        "relative_delta": 0.2 if variation_status == "TIME_VARYING" else 0.0,
        "latest_is_zero": latest_value == 0.0,
        "variation_status": variation_status,
        "flat_reason": "observed samples are constant",
    }


def _dynamic_kpi(
    metric: str,
    variation_status: str,
    latest_value: float,
) -> dict[str, object]:
    item = _calibration_kpi(metric, variation_status, latest_value)
    item["zero_value_note"] = (
        "Latest loss proxy is zero because the flow-level proxy inputs resolved to no loss."
        if latest_value == 0.0
        else ""
    )
    return item


def _formula_kpi(
    metric: str,
    variation_status: str,
    current_value: float,
) -> dict[str, object]:
    return {
        "metric": metric,
        "runtime_summary_key": f"runtime.{metric.lower()}",
        "current_value": current_value,
        "unit": "ratio" if "LOSS" in metric else "Mbps",
        "observed_source": "RUNTIME_SUMMARY_KEY",
        "variation_status": variation_status,
        "evidence_status": "FORMULA_AND_TIME_VARYING"
        if variation_status == "TIME_VARYING"
        else "FORMULA_READY_FLAT_OR_LIMITED_SERIES",
    }


def _variation_kpi(
    metric: str,
    variation_status: str,
    current_value: float,
) -> dict[str, object]:
    return {
        "metric": metric,
        "display_name": metric.replace("_", " ").title(),
        "runtime_summary_key": f"runtime.{metric.lower()}",
        "current_value": current_value,
        "latest_value": current_value,
        "unit": "ratio" if "LOSS" in metric else "Mbps",
        "observed_source": "RUNTIME_SUMMARY_KEY",
        "variation_status": variation_status,
        "evidence_status": "FORMULA_AND_TIME_VARYING"
        if variation_status == "TIME_VARYING"
        else "FORMULA_READY_FLAT_OR_LIMITED_SERIES",
        "explanation_status": "TIME_VARIATION_EXPLAINED"
        if variation_status == "TIME_VARYING"
        else "FLAT_ZERO_EXPLAINED"
        if variation_status == "FLAT_ZERO"
        else "FLAT_NONZERO_EXPLAINED"
        if variation_status == "FLAT_NONZERO"
        else "INSUFFICIENT_SERIES",
        "latest_is_zero": current_value == 0.0,
        "flat_reason": "observed samples are constant",
        "user_explanation": "backend explanation",
        "trust_label": "flow-level proxy",
    }
