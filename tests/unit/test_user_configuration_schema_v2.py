from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from leo_twin.schema.config import RuntimeConfig, SEESConfig, ScenarioConfig, config_to_dict
from leo_twin.services.configuration_schema import (
    USER_CONFIGURATION_SCHEMA_V2_ID,
    build_user_configuration_schema_v2,
    validate_user_configuration_mapping_v2,
)
from leo_twin.services.configuration_view import build_user_configuration_view


def test_user_configuration_schema_v2_covers_full_effective_config() -> None:
    config = SEESConfig(
        scenario=ScenarioConfig(
            satellite_count=120,
            compute_nodes=120,
            compute_cpu_gflops_fp64=6.0,
            compute_gpu_tflops_fp32=2.5,
            compute_gpu_tflops_fp16=5.0,
            compute_npu_tops_int8=12.0,
            compute_memory_gb=32.0,
            compute_storage_gb=512.0,
        ),
        runtime=RuntimeConfig(mode="ACCELERATED", speed_factor=10.0),
    )

    schema = build_user_configuration_schema_v2(config)
    fields = _fields_by_path(schema)
    default_paths = set(_flatten_paths(config_to_dict(SEESConfig())))

    assert schema["version"] == "v2"
    assert schema["schema_id"] == USER_CONFIGURATION_SCHEMA_V2_ID
    assert schema["source"] == "backend_sees_config"
    assert schema["unknown_key_policy"] == "REJECT"
    assert schema["defaulting_policy"] == "OMITTED_FIELDS_USE_BACKEND_DEFAULTS"
    assert schema["forbidden_integrations"] == ("STK", "EXATA", "AFSIM", "DDS")
    assert schema["packet_level_simulation"] is False
    assert schema["field_count"] == len(default_paths)
    assert set(fields) == default_paths
    assert json.loads(json.dumps(schema, sort_keys=True))["schema_id"] == (
        USER_CONFIGURATION_SCHEMA_V2_ID
    )

    assert fields["scenario.satellite_count"]["value_type"] == "integer"
    assert fields["scenario.satellite_count"]["minimum"] == 1
    assert fields["scenario.satellite_count"]["default_value"] == 72
    assert fields["scenario.satellite_count"]["current_value"] == 120
    compute_vector_expectations = {
        "scenario.compute_capacity": ("GFLOPS FP32", 10.0),
        "scenario.compute_cpu_gflops_fp64": ("GFLOPS FP64", 6.0),
        "scenario.compute_gpu_tflops_fp32": ("TFLOPS FP32", 2.5),
        "scenario.compute_gpu_tflops_fp16": ("TFLOPS FP16", 5.0),
        "scenario.compute_npu_tops_int8": ("TOPS INT8", 12.0),
        "scenario.compute_memory_gb": ("GB", 32.0),
        "scenario.compute_storage_gb": ("GB", 512.0),
    }
    for path, (unit, current_value) in compute_vector_expectations.items():
        assert fields[path]["unit"] == unit
        if path == "scenario.compute_capacity":
            assert fields[path]["exclusive_minimum"] == 0.0
        else:
            assert fields[path]["minimum"] == 0.0
        assert fields[path]["current_value"] == current_value
        assert fields[path]["editable_surface"] == "CONTROL_PANEL_KEY_FIELD"
    assert fields["scenario.orbit.orbit_update_mode"]["value_type"] == "enum|null"
    assert fields["scenario.orbit.orbit_update_mode"]["nullable"] is True
    assert fields["scenario.orbit.orbit_update_mode"]["enum_values"] == (
        "PER_SATELLITE",
        "BATCH",
    )
    assert fields["runtime.mode"]["enum_values"] == (
        "REAL_TIME",
        "ACCELERATED",
        "PAUSED",
    )
    assert fields["runtime.speed_factor"]["minimum"] == 1.0
    assert fields["runtime.speed_factor"]["maximum"] == 100.0
    assert fields["network.transport_loss_rate"]["exclusive_maximum"] == 1.0
    assert fields["network.time_pressure_period_s"]["unit"] == "s"
    assert fields["network.time_pressure_period_s"]["exclusive_minimum"] == 0.0
    assert fields["network.time_pressure_burst_amplitude"]["maximum"] == 1.0
    assert fields["network.time_pressure_burst_amplitude"][
        "editable_surface"
    ] == "DETAILED_CONFIG_FILE_ONLY"
    assert "routing_requires_at_least_one_positive_weight" in fields[
        "network.routing_latency_weight"
    ]["validation_rules"]
    templates = {template["id"]: template for template in schema["templates"]}
    assert templates["baseline_72sat"]["fidelity_mode"] == (
        "SMALL_SCALE_PER_SATELLITE_ORBIT"
    )
    assert templates["network_stress_120sat"]["expected_kpi_behavior"] == (
        "Non-zero loss, jitter, and route-pressure proxies."
    )
    assert templates["large_scale_1200sat"]["scale"] == "1200 satellites"


def test_user_configuration_schema_v2_validation_accepts_minimal_user_config() -> None:
    report = validate_user_configuration_mapping_v2(
        {
            "scenario": {
                "satellite_count": 72,
                "compute_nodes": 72,
            },
            "runtime": {
                "duration": 600,
                "seed": 20260703,
            },
        }
    )

    assert report["ok"] is True
    assert report["error_count"] == 0
    assert report["errors"] == ()
    normalized = report["normalized_config"]
    assert isinstance(normalized, dict)
    assert normalized["scenario"]["satellite_count"] == 72
    assert normalized["scenario"]["compute_nodes"] == 72
    assert normalized["scenario"]["compute_capacity"] == 10.0
    assert normalized["runtime"]["duration"] == 600
    assert normalized["network"]["transport_protocol"] == "TCP"


def test_user_configuration_schema_v2_validation_rejects_unknown_keys() -> None:
    report = validate_user_configuration_mapping_v2(
        {
            "scenario": {
                "satellite_count": 72,
                "unsupported_compute_gpu": 1.0,
            },
        }
    )

    assert report["ok"] is False
    assert report["error_count"] == 1
    assert report["normalized_config"] is None
    errors = report["errors"]
    assert isinstance(errors, tuple)
    assert errors[0]["source"] == "config_loader"
    assert "unknown scenario keys: unsupported_compute_gpu" in errors[0]["message"]


def test_user_configuration_schema_v2_validation_rejects_invalid_semantics() -> None:
    report = validate_user_configuration_mapping_v2(
        {
            "scenario": {
                "traffic_model": {
                    "traffic_class": "COMPUTE_SERVICE",
                    "destination_type": "GROUND_ENDPOINT",
                },
            },
        }
    )

    assert report["ok"] is False
    errors = report["errors"]
    assert isinstance(errors, tuple)
    assert "destination_type must be COMPUTE_NODE" in errors[0]["message"]


def test_configuration_view_exposes_user_configuration_schema_v2() -> None:
    view = build_user_configuration_view(
        SEESConfig(
            scenario=ScenarioConfig(
                satellite_count=300,
                compute_nodes=300,
                compute_gpu_tflops_fp32=4.0,
            )
        )
    )

    schema = view["user_config_schema_v2"]
    assert view["version"] == "v1"
    assert view["schema_version"] == "v2"
    assert view["schema_id"] == USER_CONFIGURATION_SCHEMA_V2_ID
    assert isinstance(schema, dict)
    assert schema["schema_id"] == USER_CONFIGURATION_SCHEMA_V2_ID
    assert schema["field_count"] == view["detailed_field_count"]
    schema_fields = _fields_by_path(schema)
    assert schema_fields["scenario.satellite_count"]["current_value"] == 300
    assert schema_fields["scenario.compute_gpu_tflops_fp32"]["current_value"] == 4.0


def test_user_configuration_schema_v2_examples_match_validation_policy() -> None:
    schema = build_user_configuration_schema_v2()

    examples = schema["examples"]
    assert isinstance(examples, tuple)
    outcomes = {
        example["id"]: validate_user_configuration_mapping_v2(example["mapping"])["ok"]
        for example in examples
        if isinstance(example, dict)
    }

    assert outcomes == {
        "accepted_minimal_72sat": True,
        "rejected_unknown_field": False,
    }


def _fields_by_path(schema: Mapping[str, object]) -> dict[str, dict[str, object]]:
    fields = schema["fields"]
    assert isinstance(fields, tuple)
    result: dict[str, dict[str, object]] = {}
    for field in fields:
        assert isinstance(field, dict)
        result[str(field["path"])] = field
    return result


def _flatten_paths(data: Mapping[str, Any]) -> dict[str, object]:
    flattened: dict[str, object] = {}

    def walk(prefix: str, value: object) -> None:
        if isinstance(value, Mapping):
            for key in sorted(value):
                child_path = f"{prefix}.{key}" if prefix else str(key)
                walk(child_path, value[key])
            return
        flattened[prefix] = value

    walk("", data)
    return dict(sorted(flattened.items()))
