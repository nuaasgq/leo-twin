from __future__ import annotations

import json


from leo_twin.models.network.quality import (
    NETWORK_QUALITY_PROXY_MODEL_V2_ID,
    NetworkQualityInputs,
    dominant_network_quality_proxy_source,
    estimate_network_quality,
    quality_congestion_loss_proxy_rate,
)


def test_network_quality_proxy_model_is_deterministic_and_flow_level() -> None:
    inputs = NetworkQualityInputs(
        sim_time=0.0,
        route_latency_avg_s=0.05,
        route_delay_variation_proxy_s=0.01,
        route_blocking_ratio=0.0,
        failed_flow_ratio=0.0,
        route_loss_proxy_rate=0.0,
        congestion_proxy=0.0,
        offered_route_capacity_mbps=200.0,
        requested_route_demand_mbps=0.0,
        completed_flow_capacity_mbps=180.0,
        successful_flow_count=2,
        flow_latency_avg_s=0.04,
        flow_latency_variation_proxy_s=0.015,
    )

    first = estimate_network_quality(inputs)
    second = estimate_network_quality(inputs)

    assert first == second
    assert first.model_id == NETWORK_QUALITY_PROXY_MODEL_V2_ID
    assert first.metric_model == "FLOW_LEVEL_PROXY"
    assert _approx(0.9) == first.throughput_pressure_proxy
    assert _approx(0.05) == first.pressure_loss_proxy_rate
    assert _approx(0.05) == first.effective_loss_proxy_rate
    assert _approx(0.04) == first.effective_latency_avg_s
    assert _approx(0.015) == first.effective_delay_variation_proxy_s
    assert _approx(190.0) == first.effective_available_throughput_mbps
    assert _approx(180.0) == first.effective_throughput_mbps
    assert first.throughput_source == "COMPLETED_FLOW_CAPACITY"
    assert first.latency_source == "COMPLETED_FLOW_LATENCY"
    assert first.loss_source == "PRESSURE_LOSS_PROXY"
    assert first.delay_variation_source == "FLOW_LATENCY_VARIATION"
    assert json.loads(json.dumps(first.to_dict(), sort_keys=True))["model_id"] == (
        NETWORK_QUALITY_PROXY_MODEL_V2_ID
    )


def test_network_quality_proxy_model_varies_with_simulation_time() -> None:
    base = dict(
        route_latency_avg_s=0.05,
        route_delay_variation_proxy_s=0.0,
        route_blocking_ratio=0.0,
        failed_flow_ratio=0.0,
        route_loss_proxy_rate=0.0,
        congestion_proxy=0.0,
        offered_route_capacity_mbps=200.0,
        requested_route_demand_mbps=0.0,
        completed_flow_capacity_mbps=180.0,
        successful_flow_count=2,
        flow_latency_avg_s=0.04,
        flow_latency_variation_proxy_s=0.0,
    )

    early = estimate_network_quality(NetworkQualityInputs(sim_time=2.0, **base))
    peak = estimate_network_quality(NetworkQualityInputs(sim_time=60.0, **base))

    assert early.time_pressure_factor < peak.time_pressure_factor
    assert early.time_pressure_loss_proxy_rate == 0.0
    assert peak.time_pressure_loss_proxy_rate > 0.0
    assert peak.effective_loss_proxy_rate > early.effective_loss_proxy_rate
    assert peak.effective_delay_variation_proxy_s > early.effective_delay_variation_proxy_s
    assert peak.effective_throughput_mbps < early.effective_throughput_mbps
    assert peak.loss_source == "PRESSURE_LOSS_PROXY"
    assert peak.delay_variation_source == "PRESSURE_DELAY_VARIATION"


def test_network_quality_proxy_model_uses_active_inflight_flow_before_available_capacity() -> None:
    estimate = estimate_network_quality(
        NetworkQualityInputs(
            sim_time=10.0,
            route_latency_avg_s=0.08,
            route_delay_variation_proxy_s=0.0,
            route_blocking_ratio=0.0,
            failed_flow_ratio=0.0,
            route_loss_proxy_rate=0.0,
            congestion_proxy=0.0,
            offered_route_capacity_mbps=100.0,
            requested_route_demand_mbps=70.0,
            completed_flow_capacity_mbps=0.0,
            successful_flow_count=0,
            flow_latency_avg_s=0.0,
            flow_latency_variation_proxy_s=0.0,
            active_flow_count=1,
            active_available_flow_count=1,
            active_flow_demand_mbps=70.0,
            active_flow_capacity_mbps=70.0,
            active_flow_latency_avg_s=0.05,
            active_flow_latency_variation_proxy_s=0.0,
            active_flow_blocking_ratio=0.0,
        )
    )

    assert estimate.throughput_source == "ACTIVE_FLOW_CAPACITY"
    assert estimate.latency_source == "ACTIVE_FLOW_LATENCY"
    assert estimate.effective_throughput_mbps == 70.0
    assert estimate.effective_latency_avg_s == 0.05
    assert estimate.active_flow_pressure_proxy == 0.7
    assert estimate.to_dict()["time_adjusted_active_throughput_mbps"] == 70.0


def test_network_quality_proxy_model_accounts_for_demand_without_routes() -> None:
    estimate = estimate_network_quality(
        NetworkQualityInputs(
            sim_time=60.0,
            route_latency_avg_s=0.0,
            route_delay_variation_proxy_s=0.0,
            route_blocking_ratio=0.0,
            failed_flow_ratio=0.0,
            route_loss_proxy_rate=0.0,
            congestion_proxy=0.0,
            offered_route_capacity_mbps=0.0,
            requested_route_demand_mbps=25.0,
            completed_flow_capacity_mbps=0.0,
            successful_flow_count=0,
            flow_latency_avg_s=0.0,
            flow_latency_variation_proxy_s=0.0,
        )
    )

    assert estimate.demand_pressure_proxy == 1.0
    assert _approx(0.1) == estimate.demand_loss_proxy_rate
    assert _approx(0.1) == estimate.effective_loss_proxy_rate
    assert estimate.effective_throughput_mbps == 0.0
    assert estimate.throughput_source == "AVAILABLE_ROUTE_CAPACITY_AFTER_LOSS"
    assert estimate.latency_source == "AVAILABLE_ROUTE_LATENCY"


def test_network_quality_proxy_helpers_validate_inputs() -> None:
    assert quality_congestion_loss_proxy_rate(0.8) == 0.0
    assert _approx(0.05) == quality_congestion_loss_proxy_rate(0.9)
    assert dominant_network_quality_proxy_source((('a', 0.1), ('b', 0.1))) == 'a'

    error = _raises(
        ValueError,
        lambda: NetworkQualityInputs(
            sim_time=0.0,
            route_latency_avg_s=0.0,
            route_delay_variation_proxy_s=0.0,
            route_blocking_ratio=1.5,
            failed_flow_ratio=0.0,
            route_loss_proxy_rate=0.0,
            congestion_proxy=0.0,
            offered_route_capacity_mbps=0.0,
            requested_route_demand_mbps=0.0,
            completed_flow_capacity_mbps=0.0,
            successful_flow_count=0,
            flow_latency_avg_s=0.0,
            flow_latency_variation_proxy_s=0.0,
        ),
    )
    assert "route_blocking_ratio" in str(error)

    error = _raises(
        TypeError,
        lambda: estimate_network_quality(object()),  # type: ignore[arg-type]
    )
    assert "NetworkQualityInputs" in str(error)


def _approx(expected: float, *, tolerance: float = 1e-9) -> float:
    return _Approx(expected, tolerance)


class _Approx(float):
    def __new__(cls, expected: float, tolerance: float) -> "_Approx":
        value = float.__new__(cls, expected)
        value.expected = float(expected)
        value.tolerance = float(tolerance)
        return value

    def __eq__(self, other: object) -> bool:
        try:
            return abs(float(other) - self.expected) <= self.tolerance
        except (TypeError, ValueError):
            return False


def _raises(error_type: type[BaseException], callback: object) -> BaseException:
    try:
        callback()  # type: ignore[operator]
    except error_type as exc:
        return exc
    raise AssertionError(f"expected {error_type.__name__}")
