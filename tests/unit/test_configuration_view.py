from __future__ import annotations

from leo_twin.schema.config import (
    NetworkProfile,
    RuntimeConfig,
    SEESConfig,
    ScenarioConfig,
)
from leo_twin.schema.config_loader import load_config
from leo_twin.services.configuration_view import build_user_configuration_view


def test_user_configuration_view_is_deterministic_and_frontend_ready() -> None:
    config = SEESConfig(
        scenario=ScenarioConfig(
            satellite_count=120,
            user_count=500,
            compute_nodes=120,
            compute_capacity=40.0,
            compute_gpu_tflops_fp32=2.5,
            compute_npu_tops_int8=12.0,
        ),
        network=NetworkProfile(
            transport_protocol="UDP",
            transport_loss_rate=0.025,
            space_link_mode="BOUNDED_CANDIDATE",
        ),
        runtime=RuntimeConfig(duration=900, speed_factor=10.0),
    )

    first = build_user_configuration_view(config)
    second = build_user_configuration_view(config)

    assert first == second
    assert first["version"] == "v1"
    assert first["source"] == "backend_sees_config"
    assert first["frontend_policy"] == "CONTROL_PANEL_KEY_FIELDS_ONLY"
    assert first["detailed_config_file"] == "configs/sees_control.yaml"
    assert (
        first["template_config_file"]
        == "configs/templates/sees_user_detailed.example.yaml"
    )
    assert first["key_field_count"] == len(first["key_fields"])
    assert first["detailed_field_count"] > first["key_field_count"]
    assert _field(first, "scenario.satellite_count") == {
        "path": "scenario.satellite_count",
        "label": "Satellite count",
        "section": "Scenario scale",
        "value": 120,
        "role": "Primary constellation size selected by the user.",
        "editable_in_ui": True,
    }
    assert _field(first, "scenario.compute_gpu_tflops_fp32")["value"] == 2.5
    assert _field(first, "network.transport_protocol")["value"] == "UDP"
    assert _field(first, "runtime.duration")["unit"] == "s"
    assert "scenario.compute_gpu_tflops_fp16" in first["file_only_fields"]
    assert "network.carrier_frequency_hz" in first["file_only_fields"]
    assert {
        section["section"]
        for section in first["detailed_file_sections"]
    } >= {"scenario", "scenario.orbit", "scenario.traffic_model", "network", "runtime", "ui"}


def test_detailed_user_config_template_loads_with_full_contract() -> None:
    config = load_config("configs/templates/sees_user_detailed.example.yaml")

    assert config.scenario.satellite_count == 72
    assert config.scenario.compute_nodes == 72
    assert config.scenario.traffic_model.traffic_class == "COMPUTE_SERVICE"
    assert config.network.max_space_link_candidates_per_satellite == 4
    assert config.runtime.duration == 600
    assert config.ui.visualization.satellites is True


def _field(summary: dict[str, object], path: str) -> dict[str, object]:
    fields = summary["key_fields"]
    assert isinstance(fields, tuple)
    for field in fields:
        assert isinstance(field, dict)
        if field["path"] == path:
            return field
    raise AssertionError(f"missing field {path}")
