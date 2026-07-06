from __future__ import annotations

from leo_twin.services.network_kpi_benchmark_validation import (
    NETWORK_KPI_BENCHMARK_VALIDATION_V1_ID,
    build_network_kpi_benchmark_validation_v1,
)
from leo_twin.services.network_kpi_provenance import build_network_kpi_provenance_v2


def test_network_kpi_benchmark_validation_passes_flow_level_guardrails() -> None:
    metrics = _metrics()
    provenance = build_network_kpi_provenance_v2(metrics)

    validation = build_network_kpi_benchmark_validation_v1(metrics, provenance)

    assert validation["version"] == "v1"
    assert validation["validation_id"] == NETWORK_KPI_BENCHMARK_VALIDATION_V1_ID
    assert validation["source"] == "NETWORK_KPI_PROVENANCE_V2_AND_METRICS_SUMMARY"
    assert validation["benchmark_profile"] == "FLOW_LEVEL_PROXY_RUNTIME_GUARDRAILS"
    assert validation["provenance_id"] == provenance["provenance_id"]
    assert validation["validation_status"] == "PASS"
    assert validation["failed_check_count"] == 0
    assert validation["warning_check_count"] == 0
    assert validation["missing_check_count"] == 0
    assert validation["passed_check_count"] == validation["check_count"]
    checks = _checks(validation)
    assert checks["packet_level_guard"]["status"] == "PASS"
    assert checks["selected_formula_input_coverage"]["status"] == "PASS"
    assert checks["active_demand_throughput_nonzero"]["status"] == "PASS"
    assert checks["active_route_latency_nonzero"]["status"] == "PASS"


def test_network_kpi_benchmark_validation_warns_on_flat_zero_under_activity() -> None:
    metrics = {
        **_metrics(),
        "network_quality_effective_throughput_mbps": 0.0,
        "network_quality_effective_latency_avg_s": 0.0,
    }
    provenance = build_network_kpi_provenance_v2(metrics)

    validation = build_network_kpi_benchmark_validation_v1(metrics, provenance)

    assert validation["validation_status"] == "WARN"
    checks = _checks(validation)
    assert checks["active_demand_throughput_nonzero"]["status"] == "WARN"
    assert checks["active_route_latency_nonzero"]["status"] == "WARN"


def test_network_kpi_benchmark_validation_fails_out_of_range_values() -> None:
    metrics = {
        **_metrics(),
        "network_quality_effective_loss_proxy_rate": 1.2,
        "network_quality_congestion_proxy": -0.1,
    }
    provenance = build_network_kpi_provenance_v2(metrics)

    validation = build_network_kpi_benchmark_validation_v1(metrics, provenance)

    assert validation["validation_status"] == "FAIL"
    checks = _checks(validation)
    assert checks["network_quality_effective_loss_proxy_rate.ratio_range"][
        "status"
    ] == "FAIL"
    assert checks["network_quality_congestion_proxy.ratio_range"]["status"] == "FAIL"


def test_network_kpi_benchmark_validation_reports_missing_inputs() -> None:
    provenance = build_network_kpi_provenance_v2({})

    validation = build_network_kpi_benchmark_validation_v1({}, provenance)

    assert validation["validation_status"] == "INSUFFICIENT_DATA"
    assert validation["missing_check_count"] > 0
    checks = _checks(validation)
    assert checks["kpi_runtime_value_coverage"]["status"] == "WARN"
    assert checks["selected_formula_input_coverage"]["status"] == "MISSING"


def _metrics() -> dict[str, object]:
    return {
        "network_quality_metric_model": "FLOW_LEVEL_PROXY",
        "network_quality_effective_throughput_mbps": 180.0,
        "network_quality_estimated_delivered_throughput_mbps": 180.0,
        "network_quality_time_adjusted_delivered_throughput_mbps": 171.0,
        "network_quality_estimated_available_throughput_mbps": 171.0,
        "network_quality_requested_route_demand_mbps": 200.0,
        "network_quality_available_route_demand_mbps": 200.0,
        "network_quality_available_route_count": 2,
        "network_quality_throughput_source": "COMPLETED_FLOW_CAPACITY",
        "network_quality_throughput_source_label": "completed flow capacity",
        "network_quality_effective_latency_avg_s": 0.045,
        "network_quality_route_latency_avg_s": 0.05,
        "network_quality_flow_latency_avg_s": 0.045,
        "network_quality_latency_source": "COMPLETED_FLOW_LATENCY",
        "network_quality_latency_source_label": "completed flow latency",
        "network_quality_effective_loss_proxy_rate": 0.05,
        "network_quality_route_blocking_ratio": 0.0,
        "network_quality_failed_flow_ratio": 0.0,
        "network_quality_congestion_proxy": 0.8,
        "network_quality_congestion_loss_proxy_rate": 0.03,
        "network_quality_demand_loss_proxy_rate": 0.05,
        "network_quality_time_pressure_loss_proxy_rate": 0.07,
        "network_quality_loss_source": "PRESSURE_LOSS_PROXY",
        "network_quality_loss_source_label": "pressure loss proxy",
        "network_quality_effective_delay_variation_proxy_s": 0.006,
        "network_quality_delay_variation_proxy_s": 0.004,
        "network_quality_flow_latency_variation_proxy_s": 0.006,
        "network_quality_pressure_delay_variation_proxy_s": 0.001,
        "network_quality_time_pressure_delay_variation_proxy_s": 0.002,
        "network_quality_delay_variation_source": "FLOW_LATENCY_VARIATION",
        "network_quality_delay_variation_source_label": "flow latency variation",
    }


def _checks(validation: dict[str, object]) -> dict[str, dict[str, object]]:
    checks = validation["checks"]
    assert isinstance(checks, tuple)
    result: dict[str, dict[str, object]] = {}
    for check in checks:
        assert isinstance(check, dict)
        result[str(check["check_id"])] = check
    return result
