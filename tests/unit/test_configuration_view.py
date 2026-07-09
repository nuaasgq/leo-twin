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
    build_user_configuration_reference,
    build_user_configuration_template_validation_evidence,
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
            "scale": "72 satellites, 72 compute nodes, baseline user demand.",
            "expected_kpi_behavior": (
                "Stable low-to-medium pressure KPI curves for validating the full "
                "configuration contract."
            ),
            "fidelity_mode": "SMALL_SCALE_PER_SATELLITE_ORBIT",
            "recommended_use": "Start here for deterministic smoke tests and full YAML editing.",
        },
        {
            "id": "dynamic_observability_120sat",
            "label": "120-satellite dynamic observability",
            "path": "configs/templates/sees_user_dynamic_observability.example.yaml",
            "purpose": (
                "Mixed traffic, non-zero network proxies, and per-satellite compute "
                "resources for dashboard validation."
            ),
            "scale": "120 satellites, 120 compute nodes, mixed communication/compute demand.",
            "expected_kpi_behavior": (
                "Visible time-varying throughput, latency, loss proxy, jitter proxy, "
                "and compute resource movement."
            ),
            "fidelity_mode": "MEDIUM_SCALE_DYNAMIC_OBSERVABILITY",
            "recommended_use": "Use for dashboard data-panel validation and operator demos.",
        },
        {
            "id": "network_stress_120sat",
            "label": "120-satellite network stress observability",
            "path": "configs/templates/sees_user_network_stress_120.example.yaml",
            "purpose": (
                "Higher flow-level demand, loss, rain, and routing pressure for "
                "validating changing network KPI curves."
            ),
            "scale": "120 satellites with elevated user demand and network pressure.",
            "expected_kpi_behavior": (
                "Non-zero loss and jitter proxies with route pressure and recent-flow "
                "KPI variation."
            ),
            "fidelity_mode": "MEDIUM_SCALE_NETWORK_STRESS",
            "recommended_use": "Use when checking KPI provenance, congestion, and stress behavior.",
        },
        {
            "id": "large_scale_1200sat",
            "label": "1200-satellite scale mode",
            "path": "configs/templates/sees_user_large_scale_1200.example.yaml",
            "purpose": (
                "Scale-safe batch orbit and bounded ISL template for large "
                "interactive scenarios."
            ),
            "scale": "1200 satellites with batched orbit updates and bounded ISL candidates.",
            "expected_kpi_behavior": (
                "Aggregated large-scale metrics with explicit fidelity degradation "
                "and bounded detail windows."
            ),
            "fidelity_mode": "LARGE_SCALE_BATCH_ORBIT_BOUNDED_ISL",
            "recommended_use": "Use for 1200-node responsiveness and scale-fidelity checks.",
        },
    )
    assert first["key_field_count"] == len(first["key_fields"])
    template_validation = first["template_validation"]
    assert isinstance(template_validation, dict)
    assert template_validation["evidence_id"] == (
        "sees.user_configuration_template_validation.v1"
    )
    assert template_validation["all_templates_valid"] is True
    assert template_validation["template_count"] == len(first["template_profiles"])
    assert template_validation["evidence_hash"].startswith("sha256:")
    control_surface_evidence = first["control_surface_evidence"]
    assert isinstance(control_surface_evidence, dict)
    assert control_surface_evidence["evidence_id"] == (
        "sees.user_configuration_control_surface_evidence.v1"
    )
    assert control_surface_evidence["coverage_status"] == "COMPLETE"
    assert control_surface_evidence["key_field_count"] == first["key_field_count"]
    assert control_surface_evidence["evidence_hash"].startswith("sha256:")
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
    compute_vector_paths = (
        "scenario.compute_capacity",
        "scenario.compute_cpu_gflops_fp64",
        "scenario.compute_gpu_tflops_fp32",
        "scenario.compute_gpu_tflops_fp16",
        "scenario.compute_npu_tops_int8",
        "scenario.compute_memory_gb",
        "scenario.compute_storage_gb",
    )
    for path in compute_vector_paths:
        assert _field(first, path)["editable_in_ui"] is True
        assert path not in first["file_only_fields"]
    assert _field(first, "network.transport_protocol")["value"] == "UDP"
    assert _field(first, "runtime.duration")["unit"] == "s"
    assert "network.carrier_frequency_hz" in first["file_only_fields"]
    file_only_sections = {
        section["section"]: section for section in first["file_only_sections"]
    }
    assert file_only_sections["scenario"]["field_count"] >= 1
    assert file_only_sections["scenario.traffic_model"]["field_count"] >= 4
    assert file_only_sections["network"]["field_count"] >= 8
    assert "network.carrier_frequency_hz" in file_only_sections["network"][
        "example_paths"
    ]
    assert {
        section["section"]
        for section in first["detailed_file_sections"]
    } >= {"scenario", "scenario.orbit", "scenario.traffic_model", "network", "runtime", "ui"}


def test_user_configuration_reference_v1_summarizes_full_file_contract() -> None:
    config = SEESConfig(
        scenario=ScenarioConfig(
            satellite_count=300,
            user_count=360,
            compute_nodes=300,
            compute_gpu_tflops_fp32=4.0,
        ),
        network=NetworkProfile(space_link_mode="BOUNDED_CANDIDATE"),
        runtime=RuntimeConfig(duration=900, seed=20260706),
    )

    first = build_user_configuration_reference(
        config,
        detailed_config_file="tmp/sees_control.yaml",
        generated_config_file="tmp/generated_full_system_demo.json",
    )
    second = build_user_configuration_reference(
        config,
        detailed_config_file="tmp/sees_control.yaml",
        generated_config_file="tmp/generated_full_system_demo.json",
    )

    assert first == second
    assert first["version"] == "v1"
    assert first["reference_id"] == "sees.user_configuration_reference.v1"
    assert first["source"] == "BACKEND_USER_CONFIGURATION"
    assert first["schema_id"] == "sees.user_configuration.v2"
    assert first["frontend_policy"] == "CONTROL_PANEL_KEY_FIELDS_ONLY"
    assert first["detailed_config_file"] == "tmp/sees_control.yaml"
    assert first["generated_config_file"] == "tmp/generated_full_system_demo.json"
    template_validation = first["template_validation"]
    assert isinstance(template_validation, dict)
    assert template_validation["evidence_id"] == (
        "sees.user_configuration_template_validation.v1"
    )
    assert template_validation["all_templates_valid"] is True
    assert template_validation["template_count"] == len(first["template_profiles"])
    assert template_validation["evidence_hash"].startswith("sha256:")
    control_surface_evidence = first["control_surface_evidence"]
    assert isinstance(control_surface_evidence, dict)
    assert control_surface_evidence["coverage_status"] == "COMPLETE"
    assert control_surface_evidence["key_field_count"] == first["key_field_count"]
    assert control_surface_evidence["evidence_hash"].startswith("sha256:")
    assert first["field_count"] == len(first["fields"])
    assert first["key_field_count"] > 0
    assert first["file_only_field_count"] > 0
    assert first["reference_hash"].startswith("sha256:")
    assert first["model_boundaries"] == {
        "event_kernel_policy": "NO_EVENT_KERNEL_BEHAVIOR_CHANGE",
        "packet_level_simulation": False,
        "external_simulators": False,
        "forbidden_integrations": ("STK", "EXATA", "AFSIM", "DDS"),
        "frontend_semantics_source": "BACKEND_USER_CONFIGURATION",
    }
    sections = {section["section"]: section for section in first["sections"]}
    assert sections["scenario"]["key_field_count"] > 0
    assert sections["network"]["file_only_field_count"] > 0
    fields = {field["path"]: field for field in first["fields"]}
    assert fields["scenario.satellite_count"]["ui_key_field"] is True
    assert fields["scenario.satellite_count"]["current_value"] == 300
    for path in (
        "scenario.compute_capacity",
        "scenario.compute_cpu_gflops_fp64",
        "scenario.compute_gpu_tflops_fp32",
        "scenario.compute_gpu_tflops_fp16",
        "scenario.compute_npu_tops_int8",
        "scenario.compute_memory_gb",
        "scenario.compute_storage_gb",
    ):
        assert fields[path]["ui_key_field"] is True
        assert path not in sections["scenario"]["file_only_paths"]
    assert fields["network.space_link_mode"]["current_value"] == "BOUNDED_CANDIDATE"
    assert "POST /scenario/user-config/validate-text" == first["mutation_policy"][
        "validate_endpoint"
    ]


def test_user_configuration_template_validation_evidence_is_deterministic() -> None:
    first = build_user_configuration_template_validation_evidence()
    second = build_user_configuration_template_validation_evidence()

    assert first == second
    assert first["version"] == "v1"
    assert first["evidence_id"] == "sees.user_configuration_template_validation.v1"
    assert first["source"] == "BACKEND_USER_CONFIGURATION"
    assert first["schema_id"] == "sees.user_configuration.v2"
    assert first["validation_scope"] == "APPROVED_EXECUTABLE_TEMPLATES"
    assert first["template_count"] == 4
    assert first["valid_template_count"] == 4
    assert first["invalid_template_count"] == 0
    assert first["all_templates_valid"] is True
    assert first["evidence_hash"].startswith("sha256:")
    assert first["model_boundaries"] == {
        "event_kernel_policy": "NO_EVENT_KERNEL_BEHAVIOR_CHANGE",
        "packet_level_simulation": False,
        "external_simulators": False,
        "forbidden_integrations": ("STK", "EXATA", "AFSIM", "DDS"),
    }

    rows = {row["id"]: row for row in first["templates"]}
    assert tuple(rows) == (
        "baseline_72sat",
        "dynamic_observability_120sat",
        "network_stress_120sat",
        "large_scale_1200sat",
    )
    assert rows["baseline_72sat"]["file_exists"] is True
    assert rows["baseline_72sat"]["file_hash"].startswith("sha256:")
    assert rows["baseline_72sat"]["config_hash"].startswith("sha256:")
    assert rows["baseline_72sat"]["row_hash"].startswith("sha256:")
    assert rows["baseline_72sat"]["load_ok"] is True
    assert rows["baseline_72sat"]["validation_ok"] is True
    assert rows["baseline_72sat"]["error_count"] == 0
    assert rows["baseline_72sat"]["config_summary"] == {
        "satellite_count": 72,
        "user_count": 1000,
        "compute_nodes": 72,
        "traffic_class": "COMPUTE_SERVICE",
        "destination_type": "COMPUTE_NODE",
        "runtime_mode": "REAL_TIME",
        "runtime_duration": 600,
        "runtime_seed": 20260703,
        "orbit_update_mode": None,
        "space_link_mode": None,
    }
    assert rows["large_scale_1200sat"]["config_summary"]["satellite_count"] == 1200
    assert rows["large_scale_1200sat"]["config_summary"]["orbit_update_mode"] == "BATCH"
    assert rows["large_scale_1200sat"]["config_summary"]["space_link_mode"] == (
        "BOUNDED_CANDIDATE"
    )


def test_user_configuration_template_validation_reports_missing_files(
    tmp_path: Path,
) -> None:
    evidence = build_user_configuration_template_validation_evidence(
        repository_root=tmp_path
    )

    assert evidence["all_templates_valid"] is False
    assert evidence["valid_template_count"] == 0
    assert evidence["invalid_template_count"] == evidence["template_count"]
    first_row = evidence["templates"][0]
    assert first_row["file_exists"] is False
    assert first_row["load_ok"] is False
    assert first_row["validation_ok"] is False
    assert first_row["error_count"] == 1
    assert first_row["errors"][0]["source"] == "template_file"
    assert "template file is missing" in first_row["errors"][0]["message"]


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
        "EMERGENCY": 0.0,
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
        "EMERGENCY": 0.0,
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
    assert config.scenario.traffic_model.flow_interval_seconds == 10
    assert config.scenario.traffic_model.task_interval_seconds == 30
    assert config.scenario.traffic_model.flow_demand_capacity == 80.0
    assert config.scenario.traffic_model.service_mix_weights() == {
        "DATA_TRANSFER": 3.0,
        "TELEMETRY": 1.0,
        "BULK_DOWNLINK": 2.0,
        "COMPUTE_SERVICE": 3.0,
        "EMERGENCY": 0.0,
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
        "EMERGENCY": 0.0,
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
