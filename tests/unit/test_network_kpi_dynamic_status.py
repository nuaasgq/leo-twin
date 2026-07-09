from __future__ import annotations

import json

from leo_twin.services.network_kpi_dynamic_status import (
    NETWORK_KPI_DYNAMIC_STATUS_V1_ID,
    build_network_kpi_dynamic_status_v1,
)


def test_network_kpi_dynamic_status_reports_dynamic_series() -> None:
    calibration = {
        "calibration_id": "leo_twin.network_kpi_calibration.v1",
        "metric_model": "FLOW_LEVEL_PROXY",
        "sample_count": 4,
        "sim_time_span_s": 30.0,
        "activity_context": {"active": True},
        "kpis": (
            _kpi("EFFECTIVE_THROUGHPUT", "TIME_VARYING", latest_value=80.0),
            _kpi("EFFECTIVE_LATENCY", "TIME_VARYING", latest_value=0.08),
            _kpi("EFFECTIVE_LOSS_PROXY", "FLAT_ZERO", latest_value=0.0),
        ),
    }

    first = build_network_kpi_dynamic_status_v1(calibration)
    second = build_network_kpi_dynamic_status_v1(calibration)

    assert first == second
    assert first["status_id"] == NETWORK_KPI_DYNAMIC_STATUS_V1_ID
    assert first["source"] == "NETWORK_KPI_CALIBRATION_V1"
    assert first["packet_level_simulation"] is False
    assert first["frontend_inference_required"] is False
    assert first["dynamic_status"] == "DYNAMIC"
    assert first["time_varying_kpi_count"] == 2
    assert first["flat_kpi_count"] == 1
    assert first["zero_latest_kpi_count"] == 1
    assert first["dynamic_metric_names"] == (
        "EFFECTIVE_THROUGHPUT",
        "EFFECTIVE_LATENCY",
    )
    assert first["zero_latest_metric_names"] == ("EFFECTIVE_LOSS_PROXY",)
    assert first["blocking_reasons"] == ()
    assert first["recommended_next_action"] == (
        "RENDER_BACKEND_KPI_SERIES_AND_EXPLANATION"
    )
    loss_item = first["items"][2]
    assert loss_item["visibility"] == "SHOW_ZERO_VALUE_REASON"
    assert "flow-level proxy inputs" in loss_item["zero_value_note"]
    assert json.loads(json.dumps(first, sort_keys=True))["status_id"] == (
        NETWORK_KPI_DYNAMIC_STATUS_V1_ID
    )


def test_network_kpi_dynamic_status_reports_insufficient_series() -> None:
    summary = build_network_kpi_dynamic_status_v1(
        {
            "sample_count": 1,
            "sim_time_span_s": 0.0,
            "activity_context": {"active": True},
            "kpis": (_kpi("EFFECTIVE_THROUGHPUT", "INSUFFICIENT_SAMPLES"),),
        }
    )

    assert summary["dynamic_status"] == "INSUFFICIENT_SERIES"
    assert summary["recommended_next_action"] == "COLLECT_MORE_RUNTIME_SAMPLES"
    assert summary["blocking_reasons"] == (
        {
            "reason_type": "INSUFFICIENT_SERIES",
            "sample_count": 1,
            "sim_time_span_s": 0.0,
            "message": "At least two samples over positive simulation time are required.",
        },
    )
    assert summary["items"][0]["visibility"] == "WAIT_FOR_MORE_SAMPLES"


def test_network_kpi_dynamic_status_reports_flat_with_activity() -> None:
    summary = build_network_kpi_dynamic_status_v1(
        {
            "sample_count": 5,
            "sim_time_span_s": 40.0,
            "activity_context": {"active": True},
            "kpis": (
                _kpi("EFFECTIVE_LOSS_PROXY", "FLAT_ZERO", latest_value=0.0),
                _kpi(
                    "EFFECTIVE_DELAY_VARIATION_PROXY",
                    "FLAT_ZERO",
                    latest_value=0.0,
                ),
            ),
        }
    )

    assert summary["dynamic_status"] == "FLAT_WITH_ACTIVITY"
    assert summary["activity_active"] is True
    assert summary["flat_metric_names"] == (
        "EFFECTIVE_LOSS_PROXY",
        "EFFECTIVE_DELAY_VARIATION_PROXY",
    )
    assert summary["recommended_next_action"] == (
        "CHECK_PRESSURE_INPUTS_AND_NETWORK_STRESS_TEMPLATE"
    )
    assert summary["blocking_reasons"][0]["reason_type"] == "FLAT_KPI_SERIES"
    assert summary["items"][1]["zero_value_note"].startswith(
        "Latest delay-variation proxy is zero"
    )


def _kpi(
    metric: str,
    variation_status: str,
    *,
    latest_value: float = 1.0,
) -> dict[str, object]:
    return {
        "metric": metric,
        "sample_key": metric.lower(),
        "runtime_summary_key": f"runtime.{metric.lower()}",
        "unit": "ratio",
        "observed": True,
        "first_value": 1.0,
        "latest_value": latest_value,
        "minimum_value": min(1.0, latest_value),
        "maximum_value": max(1.0, latest_value),
        "absolute_delta": abs(latest_value - 1.0)
        if variation_status == "TIME_VARYING"
        else 0.0,
        "endpoint_delta": latest_value - 1.0,
        "relative_delta": abs(latest_value - 1.0),
        "latest_is_zero": latest_value == 0.0,
        "variation_status": variation_status,
        "flat_reason": "observed samples are constant",
    }
