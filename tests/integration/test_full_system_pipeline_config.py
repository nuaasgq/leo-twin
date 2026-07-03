from __future__ import annotations

import json

import pytest

from examples.full_system_pipeline_config import load_full_system_pipeline_config


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
    assert config.flow["flow_id"] == "flow-001"
    assert config.task["task_id"] == "flow-001"
    assert config.compute["node_id"] == "node-a"


def test_full_system_pipeline_config_rejects_missing_section(tmp_path) -> None:
    config_path = tmp_path / "bad-config.json"
    config_path.write_text(json.dumps({"orbit": {}}), encoding="utf-8")

    with pytest.raises(ValueError, match="ground_endpoint must be a mapping"):
        load_full_system_pipeline_config(config_path)
