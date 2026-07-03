from __future__ import annotations

import json

import pytest

from examples.full_system_pipeline_config import load_full_system_pipeline_config
from examples.full_system_pipeline_demo import antenna_from_config


def test_full_system_pipeline_config_loads_defaults() -> None:
    config = load_full_system_pipeline_config()

    assert config.orbit["satellite_id"] == "sat-001"
    assert config.ground_endpoint["endpoint_id"] == "user-east"
    assert config.network["link_capacity"] == 10000.0
    assert config.channel["medium"] == "SPACE_GROUND"
    assert config.link_budget["reference_range_km"] == 629.0
    assert config.transmit_terminal["antenna"]["antenna_id"] == "satellite-ka"
    assert config.receive_terminal["antenna"]["antenna_id"] == "ground-ka"
    assert config.transport["protocol"] == "TCP"
    assert config.transport["loss_rate"] == 0.0
    assert config.transport["congestion_window_segments"] is None
    assert config.flow["flow_id"] == "flow-001"
    assert config.task["task_id"] == "flow-001"
    assert config.compute["node_id"] == "node-a"


def test_full_system_pipeline_config_rejects_missing_section(tmp_path) -> None:
    config_path = tmp_path / "bad-config.json"
    config_path.write_text(json.dumps({"orbit": {}}), encoding="utf-8")

    with pytest.raises(ValueError, match="ground_endpoint must be a mapping"):
        load_full_system_pipeline_config(config_path)


def test_antenna_config_supports_direct_gain_and_aperture_profiles() -> None:
    direct = antenna_from_config(
        {
            "antenna_id": "direct-ka",
            "gain_dbi": 32.0,
            "beam_width_deg": 2.0,
            "steering_mode": "electronic",
        }
    )
    aperture = antenna_from_config(
        {
            "antenna_id": "aperture-ka",
            "steering_mode": "tracking",
            "aperture": {
                "diameter_m": 0.45,
                "carrier_frequency_hz": 20_000_000_000.0,
                "aperture_efficiency": 0.65,
            },
        }
    )

    assert direct.antenna_id == "direct-ka"
    assert direct.gain_dbi == 32.0
    assert direct.beam_width_deg == 2.0
    assert aperture.antenna_id == "aperture-ka"
    assert aperture.gain_dbi == pytest.approx(37.620567, abs=1e-6)
    assert aperture.beam_width_deg == pytest.approx(2.331719, abs=1e-6)
    assert aperture.steering_mode == "tracking"
