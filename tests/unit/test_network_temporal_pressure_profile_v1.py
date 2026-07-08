from __future__ import annotations

import json

import pytest

from leo_twin.schema.config import NetworkProfile, SEESConfig
from leo_twin.services.network_temporal_pressure_profile import (
    NETWORK_TEMPORAL_PRESSURE_PROFILE_V1_ID,
    build_network_temporal_pressure_profile_v1,
)


def test_network_temporal_pressure_profile_binds_config_and_runtime_metrics() -> None:
    config = SEESConfig(
        network=NetworkProfile(
            time_pressure_period_s=90.0,
            time_pressure_burst_center_phase=0.4,
            time_pressure_burst_width_phase=0.2,
            time_pressure_burst_amplitude=0.15,
        )
    )
    metrics = {
        "network_quality_metric_model": "FLOW_LEVEL_PROXY",
        "network_quality_time_pressure_period_s": 90.0,
        "network_quality_time_pressure_phase": 0.4,
        "network_quality_time_pressure_load_proxy": 0.8,
        "network_quality_time_pressure_triangular_wave": 0.8,
        "network_quality_time_pressure_burst_window_factor": 1.0,
        "network_quality_time_pressure_burst_amplitude": 0.15,
        "network_quality_time_pressure_envelope": 1.0,
        "network_quality_time_pressure_factor": 0.8,
        "network_quality_time_pressure_loss_proxy_rate": 0.04,
        "network_quality_time_pressure_delay_variation_proxy_s": 0.002,
    }

    profile = build_network_temporal_pressure_profile_v1(config, metrics)

    assert profile["version"] == "v1"
    assert profile["profile_id"] == NETWORK_TEMPORAL_PRESSURE_PROFILE_V1_ID
    assert profile["source"] == "SEES_CONFIG_AND_METRICS_SUMMARY"
    assert profile["configuration_source"] == "network.time_pressure_*"
    assert profile["runtime_source"] == (
        "metrics_summary.network_quality_time_pressure_*"
    )
    assert profile["metric_model"] == "FLOW_LEVEL_PROXY"
    assert profile["temporal_pressure_model"] == (
        "DETERMINISTIC_TRIANGULAR_LOAD_GATED_PROXY"
    )
    assert profile["packet_level_simulation"] is False
    assert profile["frontend_inference_required"] is False
    assert profile["status"] == "OBSERVED"
    assert profile["configured"] == {
        "period_s": 90.0,
        "burst_center_phase": 0.4,
        "burst_width_phase": 0.2,
        "burst_amplitude": 0.15,
    }
    assert profile["observed"] == {
        "period_s": 90.0,
        "phase": 0.4,
        "load_proxy": 0.8,
        "triangular_wave": 0.8,
        "burst_window_factor": 1.0,
        "burst_amplitude": 0.15,
        "envelope": 1.0,
        "factor": 0.8,
        "loss_proxy_rate": 0.04,
        "delay_variation_proxy_s": 0.002,
    }
    assert profile["configured_field_count"] == 4
    assert profile["observed_source_field_count"] == 10
    assert profile["required_runtime_field_count"] == 3
    assert profile["observed_required_runtime_field_count"] == 3
    assert str(profile["profile_hash"]).startswith("sha256:")
    config_fields = {item["field"]: item for item in profile["config_fields"]}
    assert config_fields["network.time_pressure_burst_amplitude"] == {
        "field": "network.time_pressure_burst_amplitude",
        "current_value": 0.15,
        "value_source": "SEES_CONFIG",
    }
    runtime_fields = {item["field"]: item for item in profile["runtime_fields"]}
    assert runtime_fields["network_quality_time_pressure_factor"] == {
        "field": "network_quality_time_pressure_factor",
        "current_value": 0.8,
        "value_source": "METRICS_SUMMARY",
    }
    json.dumps(profile, sort_keys=True)


def test_network_temporal_pressure_profile_reports_missing_runtime_metrics() -> None:
    profile = build_network_temporal_pressure_profile_v1(SEESConfig(), {})

    assert profile["status"] == "CONFIGURED_WAITING_FOR_METRICS"
    assert profile["configured"] == {
        "period_s": 120.0,
        "burst_center_phase": 0.5,
        "burst_width_phase": 0.25,
        "burst_amplitude": 0.0,
    }
    assert profile["observed"]["period_s"] is None
    assert profile["observed_source_field_count"] == 0
    assert profile["observed_required_runtime_field_count"] == 0
    assert all(item["value_source"] == "MISSING" for item in profile["runtime_fields"])


def test_network_temporal_pressure_profile_rejects_invalid_inputs() -> None:
    with pytest.raises(TypeError):
        build_network_temporal_pressure_profile_v1(object(), {})  # type: ignore[arg-type]

    with pytest.raises(TypeError):
        build_network_temporal_pressure_profile_v1(SEESConfig(), object())  # type: ignore[arg-type]
