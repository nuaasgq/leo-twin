"""Deterministic flow-level network quality proxy model.

This module converts route, flow, congestion, and temporal pressure inputs into
network KPI proxy estimates. It is intentionally flow-level: values are not
packet loss, packet jitter, RF propagation, or external-simulator output.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from leo_twin.models.network.pressure import (
    NETWORK_TIME_PRESSURE_PERIOD_S,
    TemporalPressureState,
    time_varying_pressure_delay_variation,
    time_varying_pressure_loss_rate,
    time_varying_pressure_state,
)


NETWORK_QUALITY_PROXY_MODEL_V2_ID = "leo_twin.network_quality_proxy_model.v2"


@dataclass(frozen=True)
class NetworkQualityInputs:
    """Numeric inputs for deterministic flow-level network KPI estimates."""

    sim_time: float
    route_latency_avg_s: float
    route_delay_variation_proxy_s: float
    route_blocking_ratio: float
    failed_flow_ratio: float
    route_loss_proxy_rate: float
    congestion_proxy: float
    offered_route_capacity_mbps: float
    requested_route_demand_mbps: float
    completed_flow_capacity_mbps: float
    successful_flow_count: int
    flow_latency_avg_s: float
    flow_latency_variation_proxy_s: float
    active_flow_count: int = 0
    active_available_flow_count: int = 0
    active_flow_demand_mbps: float = 0.0
    active_flow_capacity_mbps: float = 0.0
    active_flow_latency_avg_s: float = 0.0
    active_flow_latency_variation_proxy_s: float = 0.0
    active_flow_blocking_ratio: float = 0.0
    time_pressure_period_s: float = NETWORK_TIME_PRESSURE_PERIOD_S
    time_pressure_burst_center_phase: float = 0.5
    time_pressure_burst_width_phase: float = 0.25
    time_pressure_burst_amplitude: float = 0.0

    def __post_init__(self) -> None:
        _require_finite(self.sim_time, "sim_time")
        _require_non_negative(self.route_latency_avg_s, "route_latency_avg_s")
        _require_non_negative(
            self.route_delay_variation_proxy_s,
            "route_delay_variation_proxy_s",
        )
        _require_probability(self.route_blocking_ratio, "route_blocking_ratio")
        _require_probability(self.failed_flow_ratio, "failed_flow_ratio")
        _require_probability(self.route_loss_proxy_rate, "route_loss_proxy_rate")
        _require_probability(self.congestion_proxy, "congestion_proxy")
        _require_non_negative(
            self.offered_route_capacity_mbps,
            "offered_route_capacity_mbps",
        )
        _require_non_negative(
            self.requested_route_demand_mbps,
            "requested_route_demand_mbps",
        )
        _require_non_negative(
            self.completed_flow_capacity_mbps,
            "completed_flow_capacity_mbps",
        )
        if self.successful_flow_count < 0:
            raise ValueError("successful_flow_count must be non-negative")
        _require_non_negative(self.flow_latency_avg_s, "flow_latency_avg_s")
        _require_non_negative(
            self.flow_latency_variation_proxy_s,
            "flow_latency_variation_proxy_s",
        )
        if self.active_flow_count < 0:
            raise ValueError("active_flow_count must be non-negative")
        if self.active_available_flow_count < 0:
            raise ValueError("active_available_flow_count must be non-negative")
        if self.active_available_flow_count > self.active_flow_count:
            raise ValueError(
                "active_available_flow_count must not exceed active_flow_count"
            )
        _require_non_negative(
            self.active_flow_demand_mbps,
            "active_flow_demand_mbps",
        )
        _require_non_negative(
            self.active_flow_capacity_mbps,
            "active_flow_capacity_mbps",
        )
        _require_non_negative(
            self.active_flow_latency_avg_s,
            "active_flow_latency_avg_s",
        )
        _require_non_negative(
            self.active_flow_latency_variation_proxy_s,
            "active_flow_latency_variation_proxy_s",
        )
        _require_probability(
            self.active_flow_blocking_ratio,
            "active_flow_blocking_ratio",
        )
        _require_positive(self.time_pressure_period_s, "time_pressure_period_s")
        _require_probability(
            self.time_pressure_burst_center_phase,
            "time_pressure_burst_center_phase",
        )
        _require_probability(
            self.time_pressure_burst_width_phase,
            "time_pressure_burst_width_phase",
        )
        _require_probability(
            self.time_pressure_burst_amplitude,
            "time_pressure_burst_amplitude",
        )


@dataclass(frozen=True)
class NetworkQualityEstimate:
    """Deterministic network quality proxy estimate."""

    model_id: str
    metric_model: str
    base_loss_proxy_rate: float
    congestion_loss_proxy_rate: float
    demand_pressure_proxy: float
    demand_loss_proxy_rate: float
    throughput_pressure_proxy: float
    active_flow_pressure_proxy: float
    temporal_pressure: TemporalPressureState
    time_pressure_factor: float
    time_pressure_loss_proxy_rate: float
    pressure_loss_proxy_rate: float
    effective_loss_proxy_rate: float
    flow_latency_avg_s: float
    flow_latency_variation_proxy_s: float
    effective_latency_avg_s: float
    time_pressure_delay_variation_proxy_s: float
    pressure_delay_variation_proxy_s: float
    effective_delay_variation_proxy_s: float
    effective_available_throughput_mbps: float
    time_adjusted_completed_throughput_mbps: float
    time_adjusted_active_throughput_mbps: float
    effective_throughput_mbps: float
    throughput_source: str
    latency_source: str
    loss_source: str
    delay_variation_source: str

    def to_dict(self) -> dict[str, float | str | dict[str, float]]:
        return {
            "model_id": self.model_id,
            "metric_model": self.metric_model,
            "base_loss_proxy_rate": self.base_loss_proxy_rate,
            "congestion_loss_proxy_rate": self.congestion_loss_proxy_rate,
            "demand_pressure_proxy": self.demand_pressure_proxy,
            "demand_loss_proxy_rate": self.demand_loss_proxy_rate,
            "throughput_pressure_proxy": self.throughput_pressure_proxy,
            "active_flow_pressure_proxy": self.active_flow_pressure_proxy,
            "temporal_pressure": self.temporal_pressure.to_dict(),
            "time_pressure_factor": self.time_pressure_factor,
            "time_pressure_loss_proxy_rate": self.time_pressure_loss_proxy_rate,
            "pressure_loss_proxy_rate": self.pressure_loss_proxy_rate,
            "effective_loss_proxy_rate": self.effective_loss_proxy_rate,
            "flow_latency_avg_s": self.flow_latency_avg_s,
            "flow_latency_variation_proxy_s": self.flow_latency_variation_proxy_s,
            "effective_latency_avg_s": self.effective_latency_avg_s,
            "time_pressure_delay_variation_proxy_s": (
                self.time_pressure_delay_variation_proxy_s
            ),
            "pressure_delay_variation_proxy_s": (
                self.pressure_delay_variation_proxy_s
            ),
            "effective_delay_variation_proxy_s": (
                self.effective_delay_variation_proxy_s
            ),
            "effective_available_throughput_mbps": (
                self.effective_available_throughput_mbps
            ),
            "time_adjusted_completed_throughput_mbps": (
                self.time_adjusted_completed_throughput_mbps
            ),
            "time_adjusted_active_throughput_mbps": (
                self.time_adjusted_active_throughput_mbps
            ),
            "effective_throughput_mbps": self.effective_throughput_mbps,
            "throughput_source": self.throughput_source,
            "latency_source": self.latency_source,
            "loss_source": self.loss_source,
            "delay_variation_source": self.delay_variation_source,
        }


def estimate_network_quality(inputs: NetworkQualityInputs) -> NetworkQualityEstimate:
    """Estimate deterministic flow-level network KPI proxies."""

    if not isinstance(inputs, NetworkQualityInputs):
        raise TypeError("inputs must be NetworkQualityInputs")

    congestion_loss_proxy_rate = quality_congestion_loss_proxy_rate(
        inputs.congestion_proxy
    )
    base_loss_proxy_rate = _clamp_probability(
        max(
            inputs.route_blocking_ratio,
            inputs.failed_flow_ratio,
            inputs.route_loss_proxy_rate,
            inputs.active_flow_blocking_ratio,
            congestion_loss_proxy_rate,
        )
    )
    demand_pressure_proxy = _demand_pressure_proxy(
        requested_route_demand_mbps=max(
            inputs.requested_route_demand_mbps,
            inputs.active_flow_demand_mbps,
        ),
        offered_route_capacity_mbps=inputs.offered_route_capacity_mbps,
    )
    demand_loss_proxy_rate = quality_congestion_loss_proxy_rate(demand_pressure_proxy)
    completed_throughput_pressure_proxy = _clamp_probability(
        inputs.completed_flow_capacity_mbps / inputs.offered_route_capacity_mbps
        if inputs.offered_route_capacity_mbps > 0.0
        else 0.0
    )
    active_flow_pressure_proxy = _demand_pressure_proxy(
        requested_route_demand_mbps=inputs.active_flow_demand_mbps,
        offered_route_capacity_mbps=inputs.offered_route_capacity_mbps,
    )
    active_throughput_pressure_proxy = _clamp_probability(
        inputs.active_flow_capacity_mbps / inputs.offered_route_capacity_mbps
        if inputs.offered_route_capacity_mbps > 0.0
        else 0.0
    )
    throughput_pressure_proxy = max(
        completed_throughput_pressure_proxy,
        active_throughput_pressure_proxy,
    )
    flow_pressure_proxy = max(
        completed_throughput_pressure_proxy
        if inputs.successful_flow_count > 1
        else 0.0,
        active_flow_pressure_proxy if inputs.active_flow_count > 0 else 0.0,
    )
    temporal_pressure = time_varying_pressure_state(
        inputs.sim_time,
        max(demand_pressure_proxy, flow_pressure_proxy, inputs.congestion_proxy),
        period_s=inputs.time_pressure_period_s,
        burst_center_phase=inputs.time_pressure_burst_center_phase,
        burst_width_phase=inputs.time_pressure_burst_width_phase,
        burst_amplitude=inputs.time_pressure_burst_amplitude,
    )
    time_pressure_factor = temporal_pressure.factor
    time_pressure_loss_proxy_rate = time_varying_pressure_loss_rate(
        time_pressure_factor
    )
    throughput_pressure_loss_proxy_rate = (
        quality_congestion_loss_proxy_rate(
            max(completed_throughput_pressure_proxy, active_flow_pressure_proxy)
        )
        if inputs.successful_flow_count > 1 or inputs.active_flow_count > 0
        else 0.0
    )
    pressure_loss_proxy_rate = max(
        throughput_pressure_loss_proxy_rate,
        demand_loss_proxy_rate,
        time_pressure_loss_proxy_rate,
    )
    effective_loss_proxy_rate = _clamp_probability(
        max(base_loss_proxy_rate, pressure_loss_proxy_rate)
    )
    effective_latency_avg_s = (
        inputs.flow_latency_avg_s
        if inputs.flow_latency_avg_s > 0.0
        else inputs.active_flow_latency_avg_s
        if inputs.active_flow_latency_avg_s > 0.0
        else inputs.route_latency_avg_s
    )
    time_pressure_delay_variation_proxy_s = time_varying_pressure_delay_variation(
        effective_latency_avg_s,
        time_pressure_factor,
    )
    throughput_pressure_delay_variation_proxy_s = (
        effective_latency_avg_s * max(0.0, throughput_pressure_proxy - 0.75) * 0.1
        if inputs.successful_flow_count > 1
        else 0.0
    )
    pressure_delay_variation_proxy_s = max(
        throughput_pressure_delay_variation_proxy_s,
        time_pressure_delay_variation_proxy_s,
    )
    effective_delay_variation_proxy_s = max(
        inputs.route_delay_variation_proxy_s,
        inputs.flow_latency_variation_proxy_s,
        inputs.active_flow_latency_variation_proxy_s,
        pressure_delay_variation_proxy_s,
    )
    effective_available_throughput_mbps = inputs.offered_route_capacity_mbps * (
        1.0 - effective_loss_proxy_rate
    )
    time_adjusted_completed_throughput_mbps = inputs.completed_flow_capacity_mbps * (
        1.0 - time_pressure_loss_proxy_rate
    )
    time_adjusted_active_throughput_mbps = inputs.active_flow_capacity_mbps * (
        1.0 - time_pressure_loss_proxy_rate
    )
    effective_throughput_mbps = (
        time_adjusted_completed_throughput_mbps
        if inputs.completed_flow_capacity_mbps > 0.0
        else time_adjusted_active_throughput_mbps
        if inputs.active_flow_count > 0
        else effective_available_throughput_mbps
    )
    throughput_source = (
        "COMPLETED_FLOW_CAPACITY"
        if inputs.completed_flow_capacity_mbps > 0.0
        else "ACTIVE_FLOW_CAPACITY"
        if inputs.active_flow_count > 0
        else "AVAILABLE_ROUTE_CAPACITY_AFTER_LOSS"
    )
    latency_source = (
        "COMPLETED_FLOW_LATENCY"
        if inputs.flow_latency_avg_s > 0.0
        else "ACTIVE_FLOW_LATENCY"
        if inputs.active_flow_latency_avg_s > 0.0
        else "AVAILABLE_ROUTE_LATENCY"
    )
    loss_source = dominant_network_quality_proxy_source(
        (
            ("ROUTE_BLOCKING_RATIO", inputs.route_blocking_ratio),
            ("FAILED_FLOW_RATIO", inputs.failed_flow_ratio),
            ("ROUTE_LOSS_RATE", inputs.route_loss_proxy_rate),
            ("ACTIVE_FLOW_BLOCKING_RATIO", inputs.active_flow_blocking_ratio),
            ("CONGESTION_LOSS_PROXY", congestion_loss_proxy_rate),
            ("PRESSURE_LOSS_PROXY", pressure_loss_proxy_rate),
            ("TIME_PRESSURE_LOSS_PROXY", time_pressure_loss_proxy_rate),
        )
    )
    delay_variation_source = dominant_network_quality_proxy_source(
        (
            ("ROUTE_LATENCY_VARIATION", inputs.route_delay_variation_proxy_s),
            ("FLOW_LATENCY_VARIATION", inputs.flow_latency_variation_proxy_s),
            (
                "ACTIVE_FLOW_LATENCY_VARIATION",
                inputs.active_flow_latency_variation_proxy_s,
            ),
            ("PRESSURE_DELAY_VARIATION", pressure_delay_variation_proxy_s),
            (
                "TIME_PRESSURE_DELAY_VARIATION",
                time_pressure_delay_variation_proxy_s,
            ),
        )
    )
    return NetworkQualityEstimate(
        model_id=NETWORK_QUALITY_PROXY_MODEL_V2_ID,
        metric_model="FLOW_LEVEL_PROXY",
        base_loss_proxy_rate=base_loss_proxy_rate,
        congestion_loss_proxy_rate=congestion_loss_proxy_rate,
        demand_pressure_proxy=demand_pressure_proxy,
        demand_loss_proxy_rate=demand_loss_proxy_rate,
        throughput_pressure_proxy=throughput_pressure_proxy,
        active_flow_pressure_proxy=active_flow_pressure_proxy,
        temporal_pressure=temporal_pressure,
        time_pressure_factor=time_pressure_factor,
        time_pressure_loss_proxy_rate=time_pressure_loss_proxy_rate,
        pressure_loss_proxy_rate=pressure_loss_proxy_rate,
        effective_loss_proxy_rate=effective_loss_proxy_rate,
        flow_latency_avg_s=inputs.flow_latency_avg_s,
        flow_latency_variation_proxy_s=inputs.flow_latency_variation_proxy_s,
        effective_latency_avg_s=effective_latency_avg_s,
        time_pressure_delay_variation_proxy_s=(
            time_pressure_delay_variation_proxy_s
        ),
        pressure_delay_variation_proxy_s=pressure_delay_variation_proxy_s,
        effective_delay_variation_proxy_s=effective_delay_variation_proxy_s,
        effective_available_throughput_mbps=effective_available_throughput_mbps,
        time_adjusted_completed_throughput_mbps=(
            time_adjusted_completed_throughput_mbps
        ),
        time_adjusted_active_throughput_mbps=(
            time_adjusted_active_throughput_mbps
        ),
        effective_throughput_mbps=effective_throughput_mbps,
        throughput_source=throughput_source,
        latency_source=latency_source,
        loss_source=loss_source,
        delay_variation_source=delay_variation_source,
    )


def quality_congestion_loss_proxy_rate(utilization: float) -> float:
    """Return deterministic congestion loss proxy for a utilization ratio."""

    if utilization <= 0.8:
        return 0.0
    return _clamp_probability((float(utilization) - 0.8) * 0.5)


def dominant_network_quality_proxy_source(
    sources: tuple[tuple[str, float], ...],
) -> str:
    """Return the first source with the largest numeric contribution."""

    selected_name = ""
    selected_value = -1.0
    for name, value in sources:
        numeric_value = float(value)
        if numeric_value > selected_value:
            selected_name = name
            selected_value = numeric_value
    return selected_name


def _demand_pressure_proxy(
    *,
    requested_route_demand_mbps: float,
    offered_route_capacity_mbps: float,
) -> float:
    if offered_route_capacity_mbps > 0.0:
        return _clamp_probability(
            requested_route_demand_mbps / offered_route_capacity_mbps
        )
    return 1.0 if requested_route_demand_mbps > 0.0 else 0.0


def _clamp_probability(value: float) -> float:
    return min(1.0, max(0.0, float(value)))


def _require_finite(value: float, field_name: str) -> None:
    if not isfinite(float(value)):
        raise ValueError(f"{field_name} must be finite")


def _require_non_negative(value: float, field_name: str) -> None:
    _require_finite(value, field_name)
    if float(value) < 0.0:
        raise ValueError(f"{field_name} must be non-negative")


def _require_positive(value: float, field_name: str) -> None:
    _require_finite(value, field_name)
    if float(value) <= 0.0:
        raise ValueError(f"{field_name} must be positive")


def _require_probability(value: float, field_name: str) -> None:
    _require_finite(value, field_name)
    if not 0.0 <= float(value) <= 1.0:
        raise ValueError(f"{field_name} must be within [0, 1]")
