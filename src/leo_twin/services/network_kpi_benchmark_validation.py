"""Runtime network KPI benchmark guardrail validation v1."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


NETWORK_KPI_BENCHMARK_VALIDATION_V1_ID = (
    "leo_twin.network_kpi_benchmark_validation.v1"
)

NetworkKpiBenchmarkValidationV1 = dict[str, object]


def build_network_kpi_benchmark_validation_v1(
    metrics: Mapping[str, Any],
    provenance: Mapping[str, Any],
) -> NetworkKpiBenchmarkValidationV1:
    """Build deterministic product guardrails for runtime network KPI values."""

    if not isinstance(metrics, Mapping):
        raise TypeError("metrics must be a mapping")
    if not isinstance(provenance, Mapping):
        raise TypeError("provenance must be a mapping")

    checks = (
        _packet_level_guard(provenance),
        _kpi_observed_guard(provenance),
        _selected_input_guard(provenance),
        _non_negative_check(
            metrics,
            "network_quality_effective_throughput_mbps",
            severity="FAIL",
            explanation="Effective throughput must be a non-negative flow-level value.",
        ),
        _non_negative_check(
            metrics,
            "network_quality_effective_latency_avg_s",
            severity="FAIL",
            explanation="Effective latency must be a non-negative flow-level value.",
        ),
        _ratio_check(
            metrics,
            "network_quality_effective_loss_proxy_rate",
            explanation="Loss proxy must stay within [0, 1] and is not packet loss.",
        ),
        _non_negative_check(
            metrics,
            "network_quality_effective_delay_variation_proxy_s",
            severity="FAIL",
            explanation="Delay-variation proxy must be non-negative and is not packet jitter.",
        ),
        _ratio_check(
            metrics,
            "network_quality_route_blocking_ratio",
            explanation="Route blocking ratio must stay within [0, 1].",
        ),
        _ratio_check(
            metrics,
            "network_quality_failed_flow_ratio",
            explanation="Failed flow ratio must stay within [0, 1].",
        ),
        _ratio_check(
            metrics,
            "network_quality_congestion_proxy",
            explanation="Congestion pressure proxy must stay within [0, 1].",
        ),
        _active_demand_throughput_guard(metrics),
        _active_route_latency_guard(metrics),
    )
    failed = tuple(check for check in checks if check["status"] == "FAIL")
    warned = tuple(check for check in checks if check["status"] == "WARN")
    passed = tuple(check for check in checks if check["status"] == "PASS")
    missing = tuple(check for check in checks if check["status"] == "MISSING")
    validation_status = _validation_status(
        failed_count=len(failed),
        warning_count=len(warned),
        missing_count=len(missing),
        pass_count=len(passed),
    )
    return {
        "version": "v1",
        "validation_id": NETWORK_KPI_BENCHMARK_VALIDATION_V1_ID,
        "source": "NETWORK_KPI_PROVENANCE_V2_AND_METRICS_SUMMARY",
        "benchmark_profile": "FLOW_LEVEL_PROXY_RUNTIME_GUARDRAILS",
        "provenance_id": str(provenance.get("provenance_id", "")),
        "metric_model": str(provenance.get("metric_model", "")),
        "packet_level_simulation": provenance.get("packet_level_simulation") is True,
        "validation_status": validation_status,
        "check_count": len(checks),
        "passed_check_count": len(passed),
        "warning_check_count": len(warned),
        "failed_check_count": len(failed),
        "missing_check_count": len(missing),
        "checks": checks,
        "caveats": _caveats(validation_status),
    }


def _packet_level_guard(provenance: Mapping[str, Any]) -> dict[str, object]:
    packet_level = provenance.get("packet_level_simulation") is True
    packet_level_kpis = tuple(
        item
        for item in _records(provenance.get("kpis"))
        if item.get("packet_level_metric") is True
    )
    failed = packet_level or bool(packet_level_kpis)
    return _check(
        check_id="packet_level_guard",
        metric="network_kpi_provenance_v2.packet_level_simulation",
        current_value=packet_level,
        status="FAIL" if failed else "PASS",
        severity="FAIL",
        expectation="packet-level simulation and packet-level KPI declarations are forbidden",
        source="network_kpi_provenance_v2",
        explanation=(
            "The current product contract requires deterministic flow-level proxies, "
            "not packet-level network measurements."
        ),
    )


def _kpi_observed_guard(provenance: Mapping[str, Any]) -> dict[str, object]:
    kpis = _records(provenance.get("kpis"))
    missing = tuple(item for item in kpis if item.get("status") != "OBSERVED")
    status = "PASS" if kpis and not missing else "WARN"
    if not kpis:
        status = "MISSING"
    return _check(
        check_id="kpi_runtime_value_coverage",
        metric="network_kpi_provenance_v2.kpis.status",
        current_value=len(kpis) - len(missing),
        status=status,
        severity="WARN",
        expectation="all declared network KPI rows should expose current runtime values",
        source="network_kpi_provenance_v2.kpis",
        explanation=f"{len(kpis) - len(missing)} of {len(kpis)} KPI rows are observed.",
    )


def _selected_input_guard(provenance: Mapping[str, Any]) -> dict[str, object]:
    selected = 0
    selected_observed = 0
    for item in _records(provenance.get("kpis")):
        trace = item.get("formula_trace")
        if not isinstance(trace, Mapping):
            continue
        selected += _int_value(trace.get("selected_input_count"))
        selected_observed += _int_value(trace.get("selected_observed_input_count"))
    if selected == 0:
        status = "MISSING"
    elif selected_observed == selected:
        status = "PASS"
    else:
        status = "WARN"
    return _check(
        check_id="selected_formula_input_coverage",
        metric="network_kpi_provenance_v2.kpis.formula_trace",
        current_value=selected_observed,
        status=status,
        severity="WARN",
        expectation="selected formula inputs should be visible in metrics_summary",
        source="network_kpi_provenance_v2.kpis.formula_trace",
        explanation=f"{selected_observed} of {selected} selected formula inputs are observed.",
    )


def _non_negative_check(
    metrics: Mapping[str, Any],
    metric: str,
    *,
    severity: str,
    explanation: str,
) -> dict[str, object]:
    value = _number_value(metrics.get(metric))
    status = "MISSING" if value is None else "PASS" if value >= 0.0 else "FAIL"
    return _check(
        check_id=f"{metric}.non_negative",
        metric=metric,
        current_value=value,
        status=status,
        severity=severity,
        expectation="value must be >= 0",
        source="metrics_summary",
        explanation=explanation,
    )


def _ratio_check(
    metrics: Mapping[str, Any],
    metric: str,
    *,
    explanation: str,
) -> dict[str, object]:
    value = _number_value(metrics.get(metric))
    status = (
        "MISSING"
        if value is None
        else "PASS"
        if 0.0 <= value <= 1.0
        else "FAIL"
    )
    return _check(
        check_id=f"{metric}.ratio_range",
        metric=metric,
        current_value=value,
        status=status,
        severity="FAIL",
        expectation="value must be within [0, 1]",
        source="metrics_summary",
        explanation=explanation,
    )


def _active_demand_throughput_guard(metrics: Mapping[str, Any]) -> dict[str, object]:
    demand = _number_value(metrics.get("network_quality_requested_route_demand_mbps"))
    available = _number_value(metrics.get("network_quality_available_route_count"))
    throughput = _number_value(metrics.get("network_quality_effective_throughput_mbps"))
    has_activity = (demand is not None and demand > 0.0) or (
        available is not None and available > 0.0
    )
    if throughput is None:
        status = "MISSING"
    elif has_activity and throughput <= 0.0:
        status = "WARN"
    else:
        status = "PASS"
    return _check(
        check_id="active_demand_throughput_nonzero",
        metric="network_quality_effective_throughput_mbps",
        current_value=throughput,
        status=status,
        severity="WARN",
        expectation="throughput should be positive when route demand or active routes exist",
        source="metrics_summary",
        explanation=(
            "This guard catches flat zero throughput in scenarios that already expose "
            "route demand or available routes."
        ),
    )


def _active_route_latency_guard(metrics: Mapping[str, Any]) -> dict[str, object]:
    available = _number_value(metrics.get("network_quality_available_route_count"))
    latency = _number_value(metrics.get("network_quality_effective_latency_avg_s"))
    if latency is None:
        status = "MISSING"
    elif available is not None and available > 0.0 and latency <= 0.0:
        status = "WARN"
    else:
        status = "PASS"
    return _check(
        check_id="active_route_latency_nonzero",
        metric="network_quality_effective_latency_avg_s",
        current_value=latency,
        status=status,
        severity="WARN",
        expectation="latency should be positive when available routes exist",
        source="metrics_summary",
        explanation=(
            "This guard catches flat zero latency after network routes are available."
        ),
    )


def _validation_status(
    *,
    failed_count: int,
    warning_count: int,
    missing_count: int,
    pass_count: int,
) -> str:
    if failed_count > 0:
        return "FAIL"
    if pass_count == 0 or missing_count > 0:
        return "INSUFFICIENT_DATA"
    if warning_count > 0:
        return "WARN"
    return "PASS"


def _check(
    *,
    check_id: str,
    metric: str,
    current_value: object,
    status: str,
    severity: str,
    expectation: str,
    source: str,
    explanation: str,
) -> dict[str, object]:
    return {
        "check_id": check_id,
        "metric": metric,
        "current_value": current_value,
        "status": status,
        "severity": severity,
        "expectation": expectation,
        "source": source,
        "explanation": explanation,
    }


def _records(value: object) -> tuple[Mapping[str, Any], ...]:
    if not isinstance(value, (list, tuple)):
        return ()
    return tuple(item for item in value if isinstance(item, Mapping))


def _number_value(value: object) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    if value != value or value in {float("inf"), float("-inf")}:
        return None
    return float(value)


def _int_value(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        return 0
    return max(0, value)


def _caveats(validation_status: str) -> tuple[str, ...]:
    return (
        "Benchmark validation v1 is a deterministic product guardrail, not a physical RF or packet-level validation.",
        "Checks are derived from metrics_summary and network_kpi_provenance_v2 only.",
        f"validation_status={validation_status}",
    )


__all__ = [
    "NETWORK_KPI_BENCHMARK_VALIDATION_V1_ID",
    "NetworkKpiBenchmarkValidationV1",
    "build_network_kpi_benchmark_validation_v1",
]
