from __future__ import annotations

from leo_twin.services.network_kpi_calibration import (
    NETWORK_KPI_CALIBRATION_V1_ID,
    NETWORK_TEMPORAL_PRESSURE_CALIBRATION_V1_ID,
    build_network_kpi_calibration_v1,
)


def test_network_kpi_calibration_reports_time_varying_runtime_series() -> None:
    series = {
        "version": "v1",
        "samples": (
            _sample(
                0.0,
                throughput=180.0,
                latency=0.045,
                loss=0.01,
                delay_variation=0.001,
                time_pressure=0.0,
            ),
            _sample(
                60.0,
                throughput=171.0,
                latency=0.045,
                loss=0.07,
                delay_variation=0.006,
                time_pressure=0.85,
            ),
        ),
    }
    metrics = {
        "network_quality_metric_model": "FLOW_LEVEL_PROXY",
        "network_quality_effective_throughput_mbps": 171.0,
        "network_quality_effective_latency_avg_s": 0.045,
        "network_quality_effective_loss_proxy_rate": 0.07,
        "network_quality_effective_delay_variation_proxy_s": 0.006,
        "network_quality_requested_route_demand_mbps": 200.0,
        "network_quality_offered_route_capacity_mbps": 220.0,
        "network_quality_available_route_count": 2,
        "network_quality_time_pressure_period_s": 120.0,
        "network_quality_time_pressure_phase": 0.5,
        "network_quality_time_pressure_factor": 0.85,
        "network_quality_time_pressure_loss_proxy_rate": 0.07,
        "network_quality_time_pressure_delay_variation_proxy_s": 0.006,
    }

    calibration = build_network_kpi_calibration_v1(series, metrics)

    assert calibration["version"] == "v1"
    assert calibration["calibration_id"] == NETWORK_KPI_CALIBRATION_V1_ID
    assert calibration["source"] == "KPI_TIME_SERIES_V1_AND_METRICS_SUMMARY"
    assert calibration["packet_level_simulation"] is False
    assert calibration["sample_count"] == 2
    assert calibration["sim_time_span_s"] == 60.0
    assert calibration["calibration_status"] == "TIME_VARYING_OBSERVED"
    assert calibration["time_varying_kpi_count"] == 3
    assert calibration["flat_kpi_count"] == 1
    assert calibration["activity_context"]["active"] is True
    assert calibration["time_driver"] == {
        "source": "SIMULATION_TIME",
        "period_s": 120.0,
        "phase": 0.5,
        "factor": 0.85,
        "loss_proxy_rate": 0.07,
        "delay_variation_proxy_s": 0.006,
    }
    temporal = calibration["temporal_pressure_calibration"]
    assert temporal["calibration_id"] == (
        NETWORK_TEMPORAL_PRESSURE_CALIBRATION_V1_ID
    )
    assert temporal["status"] == "TEMPORAL_DRIVER_ALIGNED"
    assert temporal["temporal_pressure_model"] == (
        "DETERMINISTIC_TRIANGULAR_LOAD_GATED_PROXY"
    )
    assert temporal["packet_level_simulation"] is False
    assert temporal["frontend_inference_required"] is False
    assert temporal["temporal_pressure_active"] is True
    assert temporal["loss_proxy_active"] is True
    assert temporal["delay_variation_proxy_active"] is True
    assert temporal["aligned_metric_count"] == 3
    assert temporal["aligned_metrics"] == (
        "EFFECTIVE_THROUGHPUT",
        "EFFECTIVE_LOSS_PROXY",
        "EFFECTIVE_DELAY_VARIATION_PROXY",
    )
    assert str(temporal["calibration_hash"]).startswith("sha256:")
    kpis = _kpis(calibration)
    assert kpis["EFFECTIVE_THROUGHPUT"]["variation_status"] == "TIME_VARYING"
    assert kpis["EFFECTIVE_THROUGHPUT"]["absolute_delta"] == 9.0
    assert kpis["EFFECTIVE_LATENCY"]["variation_status"] == "FLAT_NONZERO"
    assert kpis["EFFECTIVE_LOSS_PROXY"]["variation_status"] == "TIME_VARYING"
    assert (
        kpis["EFFECTIVE_DELAY_VARIATION_PROXY"]["variation_status"]
        == "TIME_VARYING"
    )


def test_network_kpi_calibration_explains_insufficient_or_flat_series() -> None:
    calibration = build_network_kpi_calibration_v1(
        {"version": "v1", "samples": (_sample(0.0),)},
        {
            "network_quality_metric_model": "FLOW_LEVEL_PROXY",
            "network_quality_effective_throughput_mbps": 0.0,
            "network_quality_effective_latency_avg_s": 0.0,
            "network_quality_effective_loss_proxy_rate": 0.0,
            "network_quality_effective_delay_variation_proxy_s": 0.0,
        },
    )

    assert calibration["calibration_status"] == "INSUFFICIENT_SERIES"
    assert calibration["temporal_pressure_calibration"]["status"] == (
        "INSUFFICIENT_SERIES"
    )
    assert calibration["temporal_pressure_calibration"][
        "aligned_metric_count"
    ] == 0
    assert calibration["time_varying_kpi_count"] == 0
    assert calibration["zero_latest_kpi_count"] == 4
    kpis = _kpis(calibration)
    assert kpis["EFFECTIVE_THROUGHPUT"]["variation_status"] == (
        "INSUFFICIENT_SAMPLES"
    )
    assert "fewer than two" in kpis["EFFECTIVE_THROUGHPUT"]["flat_reason"]


def _sample(
    sim_time: float,
    *,
    throughput: float = 0.0,
    latency: float = 0.0,
    loss: float = 0.0,
    delay_variation: float = 0.0,
    time_pressure: float = 0.0,
) -> dict[str, float]:
    return {
        "sim_time": sim_time,
        "network_effective_throughput_mbps": throughput,
        "network_effective_latency_s": latency,
        "network_effective_loss_proxy_rate": loss,
        "network_effective_delay_variation_s": delay_variation,
        "network_requested_route_demand_mbps": 200.0 if throughput > 0.0 else 0.0,
        "network_offered_route_capacity_mbps": 220.0 if throughput > 0.0 else 0.0,
        "network_recent_flow_count": 2.0 if throughput > 0.0 else 0.0,
        "network_time_pressure_period_s": 120.0,
        "network_time_pressure_phase": sim_time / 120.0,
        "network_time_pressure_factor": time_pressure,
        "network_time_pressure_loss_proxy_rate": loss,
        "network_time_pressure_delay_variation_s": delay_variation,
    }


def _kpis(calibration: dict[str, object]) -> dict[str, dict[str, object]]:
    kpis = calibration["kpis"]
    assert isinstance(kpis, tuple)
    result: dict[str, dict[str, object]] = {}
    for item in kpis:
        assert isinstance(item, dict)
        result[str(item["metric"])] = item
    return result
