from __future__ import annotations

from pathlib import Path

from leo_twin.schema.config import (
    NetworkProfile,
    RuntimeConfig,
    SEESConfig,
    ScenarioConfig,
)
from leo_twin.schema.config_loader import ConfigValidationError, load_config
from leo_twin.services.configuration_view import (
    build_user_configuration_view,
    configuration_template_profiles,
    load_user_configuration_template,
)


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
    assert first["template_profiles"] == (
        {
            "id": "baseline_72sat",
            "label": "72-satellite baseline",
            "path": "configs/templates/sees_user_detailed.example.yaml",
            "purpose": "Executable baseline for full-contract editing.",
        },
        {
            "id": "dynamic_observability_120sat",
            "label": "120-satellite dynamic observability",
            "path": "configs/templates/sees_user_dynamic_observability.example.yaml",
            "purpose": (
                "Mixed traffic, non-zero network proxies, and per-satellite compute "
                "resources for dashboard validation."
            ),
        },
        {
            "id": "network_stress_120sat",
            "label": "120-satellite network stress observability",
            "path": "configs/templates/sees_user_network_stress_120.example.yaml",
            "purpose": (
                "Higher flow-level demand, loss, rain, and routing pressure for "
                "validating changing network KPI curves."
            ),
        },
        {
            "id": "large_scale_1200sat",
            "label": "1200-satellite scale mode",
            "path": "configs/templates/sees_user_large_scale_1200.example.yaml",
            "purpose": (
                "Scale-safe batch orbit and bounded ISL template for large "
                "interactive scenarios."
            ),
        },
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
    file_only_sections = {
        section["section"]: section for section in first["file_only_sections"]
    }
    assert file_only_sections["scenario"]["field_count"] >= 1
    assert "scenario.compute_gpu_tflops_fp16" in file_only_sections["scenario"][
        "example_paths"
    ]
    assert file_only_sections["scenario.traffic_model"]["field_count"] >= 4
    assert file_only_sections["network"]["field_count"] >= 8
    assert "network.carrier_frequency_hz" in file_only_sections["network"][
        "example_paths"
    ]
    assert {
        section["section"]
        for section in first["detailed_file_sections"]
    } >= {"scenario", "scenario.orbit", "scenario.traffic_model", "network", "runtime", "ui"}


def test_detailed_user_config_template_loads_with_full_contract() -> None:
    template_path = "configs/templates/sees_user_detailed.example.yaml"
    template_text = Path(template_path).read_text(encoding="utf-8")
    config = load_config(template_path)

    assert "frontend control panel should expose only key operational controls" in template_text
    assert "STK, EXATA, AFSIM, DDS" in template_text
    assert "flow-level proxy metrics" in template_text
    assert "service mix weights" in template_text
    assert config.scenario.satellite_count == 72
    assert config.scenario.compute_nodes == 72
    assert config.scenario.traffic_model.traffic_class == "COMPUTE_SERVICE"
    assert config.scenario.traffic_model.service_mix_weights() == {
        "DATA_TRANSFER": 0.0,
        "TELEMETRY": 0.0,
        "BULK_DOWNLINK": 0.0,
        "COMPUTE_SERVICE": 0.0,
    }
    assert config.network.max_space_link_candidates_per_satellite == 4
    assert config.runtime.duration == 600
    assert config.ui.visualization.satellites is True


def test_dynamic_observability_user_config_template_loads() -> None:
    template_path = "configs/templates/sees_user_dynamic_observability.example.yaml"
    template_text = Path(template_path).read_text(encoding="utf-8")
    config = load_config(template_path)

    assert "120-satellite scenario" in template_text
    assert "flow-level proxy metrics" in template_text
    assert "STK, EXATA, AFSIM, DDS" in template_text
    assert config.scenario.satellite_count == 120
    assert config.scenario.compute_nodes == 120
    assert config.scenario.compute_capacity == 40.0
    assert config.scenario.compute_gpu_tflops_fp32 == 2.0
    assert config.scenario.compute_memory_gb == 32.0
    assert config.scenario.initial_workload_smoothing_enabled is True
    assert config.scenario.traffic_model.traffic_class == "COMPUTE_SERVICE"
    assert config.scenario.traffic_model.service_mix_weights() == {
        "DATA_TRANSFER": 2.0,
        "TELEMETRY": 1.0,
        "BULK_DOWNLINK": 1.0,
        "COMPUTE_SERVICE": 2.0,
    }
    assert config.network.transport_protocol == "UDP"
    assert config.network.transport_loss_rate == 0.02
    assert config.runtime.mode == "ACCELERATED"
    assert config.runtime.speed_factor == 10.0


def test_network_stress_120_user_config_template_loads() -> None:
    template_path = "configs/templates/sees_user_network_stress_120.example.yaml"
    template_text = Path(template_path).read_text(encoding="utf-8")
    config = load_config(template_path)

    assert "network stress observability" in template_text
    assert "flow-level proxy" in template_text
    assert "STK, EXATA, AFSIM, DDS" in template_text
    assert config.scenario.satellite_count == 120
    assert config.scenario.user_count == 240
    assert config.scenario.compute_nodes == 120
    assert config.scenario.initial_workload_smoothing_enabled is True
    assert config.scenario.orbit.update_interval_seconds == 20
    assert config.scenario.traffic_model.flow_interval_seconds == 5
    assert config.scenario.traffic_model.flow_demand_capacity == 320.0
    assert config.scenario.traffic_model.service_mix_weights() == {
        "DATA_TRANSFER": 3.0,
        "TELEMETRY": 1.0,
        "BULK_DOWNLINK": 2.0,
        "COMPUTE_SERVICE": 3.0,
    }
    assert config.network.transport_protocol == "UDP"
    assert config.network.transport_loss_rate == 0.05
    assert config.network.rain_rate_mm_h == 10.0
    assert config.network.routing_inverse_capacity_weight == 500.0
    assert config.network.space_link_mode == "BOUNDED_CANDIDATE"
    assert config.runtime.mode == "ACCELERATED"
    assert config.runtime.speed_factor == 5.0
    assert config.runtime.duration == 600


def test_user_configuration_templates_load_by_backend_profile_id() -> None:
    profiles = configuration_template_profiles()

    assert [profile["id"] for profile in profiles] == [
        "baseline_72sat",
        "dynamic_observability_120sat",
        "network_stress_120sat",
        "large_scale_1200sat",
    ]

    config = load_user_configuration_template("network_stress_120sat")

    assert config.scenario.satellite_count == 120
    assert config.scenario.user_count == 240
    assert config.network.transport_loss_rate == 0.05
    assert config.runtime.duration == 600


def test_user_configuration_template_loader_rejects_unknown_ids() -> None:
    try:
        load_user_configuration_template("not-a-template")
    except ConfigValidationError as exc:
        assert "unknown configuration template_id" in str(exc)
        assert "network_stress_120sat" in str(exc)
    else:
        raise AssertionError("unknown template ids must be rejected")


def test_large_scale_1200_user_config_template_loads() -> None:
    template_path = "configs/templates/sees_user_large_scale_1200.example.yaml"
    template_text = Path(template_path).read_text(encoding="utf-8")
    config = load_config(template_path)

    assert "large-scale 1200-satellite" in template_text
    assert "BOUNDED_CANDIDATE avoids all-pairs ISL" in template_text
    assert "STK, EXATA, AFSIM, DDS" in template_text
    assert config.scenario.satellite_count == 1200
    assert config.scenario.user_count == 1200
    assert config.scenario.compute_nodes == 1200
    assert config.scenario.orbit.orbit_update_mode == "BATCH"
    assert config.scenario.orbit.plane_count == 40
    assert config.scenario.initial_workload_smoothing_enabled is True
    assert config.scenario.traffic_model.service_mix_weights() == {
        "DATA_TRANSFER": 2.0,
        "TELEMETRY": 1.0,
        "BULK_DOWNLINK": 1.0,
        "COMPUTE_SERVICE": 3.0,
    }
    assert config.network.space_link_mode == "BOUNDED_CANDIDATE"
    assert config.network.max_space_link_candidates_per_satellite == 4
    assert config.runtime.mode == "REAL_TIME"
    assert config.runtime.speed_factor == 1.0


def _field(summary: dict[str, object], path: str) -> dict[str, object]:
    fields = summary["key_fields"]
    assert isinstance(fields, tuple)
    for field in fields:
        assert isinstance(field, dict)
        if field["path"] == path:
            return field
    raise AssertionError(f"missing field {path}")
