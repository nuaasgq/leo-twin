"""Runtime network temporal pressure profile summary v1."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from leo_twin.schema.config import SEESConfig
from leo_twin.services.runtime_reproducibility import stable_hash_payload


NETWORK_TEMPORAL_PRESSURE_PROFILE_V1_ID = (
    "leo_twin.network_temporal_pressure_profile.v1"
)

NetworkTemporalPressureProfileV1 = dict[str, object]

_CONFIG_FIELDS = (
    "network.time_pressure_period_s",
    "network.time_pressure_burst_center_phase",
    "network.time_pressure_burst_width_phase",
    "network.time_pressure_burst_amplitude",
)

_RUNTIME_FIELDS = (
    "network_quality_time_pressure_period_s",
    "network_quality_time_pressure_phase",
    "network_quality_time_pressure_load_proxy",
    "network_quality_time_pressure_triangular_wave",
    "network_quality_time_pressure_burst_window_factor",
    "network_quality_time_pressure_burst_amplitude",
    "network_quality_time_pressure_envelope",
    "network_quality_time_pressure_factor",
    "network_quality_time_pressure_loss_proxy_rate",
    "network_quality_time_pressure_delay_variation_proxy_s",
)

_REQUIRED_RUNTIME_FIELDS = (
    "network_quality_time_pressure_period_s",
    "network_quality_time_pressure_phase",
    "network_quality_time_pressure_factor",
)


def build_network_temporal_pressure_profile_v1(
    config: SEESConfig,
    metrics: Mapping[str, Any],
) -> NetworkTemporalPressureProfileV1:
    """Expose configured and currently observed temporal pressure semantics.

    This is a status/observation contract only. It does not recompute metrics,
    advance the runtime, or introduce packet-level simulation.
    """

    if not isinstance(config, SEESConfig):
        raise TypeError("config must be SEESConfig")
    if not isinstance(metrics, Mapping):
        raise TypeError("metrics must be a mapping")

    observed_required_count = sum(
        1 for field in _REQUIRED_RUNTIME_FIELDS if field in metrics
    )
    observed_source_count = sum(
        1 for field in _RUNTIME_FIELDS if field in metrics
    )
    status = (
        "OBSERVED"
        if observed_required_count == len(_REQUIRED_RUNTIME_FIELDS)
        else "CONFIGURED_WAITING_FOR_METRICS"
    )
    payload: dict[str, object] = {
        "version": "v1",
        "profile_id": NETWORK_TEMPORAL_PRESSURE_PROFILE_V1_ID,
        "source": "SEES_CONFIG_AND_METRICS_SUMMARY",
        "configuration_source": "network.time_pressure_*",
        "runtime_source": "metrics_summary.network_quality_time_pressure_*",
        "metric_model": str(
            metrics.get("network_quality_metric_model", "FLOW_LEVEL_PROXY")
        ),
        "temporal_pressure_model": "DETERMINISTIC_TRIANGULAR_LOAD_GATED_PROXY",
        "packet_level_simulation": False,
        "frontend_inference_required": False,
        "status": status,
        "configured": _configured_profile(config),
        "observed": _observed_profile(metrics),
        "configured_field_count": len(_CONFIG_FIELDS),
        "observed_source_field_count": observed_source_count,
        "required_runtime_field_count": len(_REQUIRED_RUNTIME_FIELDS),
        "observed_required_runtime_field_count": observed_required_count,
        "config_fields": tuple(_config_field_records(config)),
        "runtime_fields": tuple(_runtime_field_records(metrics)),
        "model_assumptions": (
            "Temporal pressure is a deterministic flow-level proxy configured "
            "from network.time_pressure_* fields.",
            "Runtime values are observed from MetricsCollector summaries; "
            "no frontend inference is required.",
            "No packet-level queue, packet loss, RF propagation, or external simulator is used.",
        ),
    }
    payload["profile_hash"] = stable_hash_payload(payload)
    return payload


def _configured_profile(config: SEESConfig) -> dict[str, float]:
    network = config.network
    return {
        "period_s": float(network.time_pressure_period_s),
        "burst_center_phase": float(network.time_pressure_burst_center_phase),
        "burst_width_phase": float(network.time_pressure_burst_width_phase),
        "burst_amplitude": float(network.time_pressure_burst_amplitude),
    }


def _observed_profile(metrics: Mapping[str, Any]) -> dict[str, object]:
    return {
        "period_s": _value(metrics, "network_quality_time_pressure_period_s"),
        "phase": _value(metrics, "network_quality_time_pressure_phase"),
        "load_proxy": _value(metrics, "network_quality_time_pressure_load_proxy"),
        "triangular_wave": _value(
            metrics,
            "network_quality_time_pressure_triangular_wave",
        ),
        "burst_window_factor": _value(
            metrics,
            "network_quality_time_pressure_burst_window_factor",
        ),
        "burst_amplitude": _value(
            metrics,
            "network_quality_time_pressure_burst_amplitude",
        ),
        "envelope": _value(metrics, "network_quality_time_pressure_envelope"),
        "factor": _value(metrics, "network_quality_time_pressure_factor"),
        "loss_proxy_rate": _value(
            metrics,
            "network_quality_time_pressure_loss_proxy_rate",
        ),
        "delay_variation_proxy_s": _value(
            metrics,
            "network_quality_time_pressure_delay_variation_proxy_s",
        ),
    }


def _config_field_records(config: SEESConfig) -> tuple[dict[str, object], ...]:
    configured = _configured_profile(config)
    values = {
        "network.time_pressure_period_s": configured["period_s"],
        "network.time_pressure_burst_center_phase": configured[
            "burst_center_phase"
        ],
        "network.time_pressure_burst_width_phase": configured["burst_width_phase"],
        "network.time_pressure_burst_amplitude": configured["burst_amplitude"],
    }
    return tuple(
        {
            "field": field,
            "current_value": values[field],
            "value_source": "SEES_CONFIG",
        }
        for field in _CONFIG_FIELDS
    )


def _runtime_field_records(metrics: Mapping[str, Any]) -> tuple[dict[str, object], ...]:
    return tuple(
        {
            "field": field,
            "current_value": _value(metrics, field),
            "value_source": "METRICS_SUMMARY" if field in metrics else "MISSING",
        }
        for field in _RUNTIME_FIELDS
    )


def _value(metrics: Mapping[str, Any], field: str) -> object:
    value = metrics.get(field)
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return float(value)
    if value is None:
        return None
    return str(value)
