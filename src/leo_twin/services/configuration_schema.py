"""Backend-owned user configuration schema v2 contracts."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from leo_twin.schema.config import (
    ComputeSchedulingPolicyConfig,
    OrbitUpdateModeConfig,
    RuntimeMode,
    SEESConfig,
    SpaceLinkModeConfig,
    TrafficClassConfig,
    TrafficDestinationTypeConfig,
    WorkloadSmoothingModeConfig,
    config_to_dict,
)
from leo_twin.schema.config_loader import ConfigValidationError, config_from_mapping
from leo_twin.schema.full_system import (
    ApplicationProtocol,
    DataLinkProtocol,
    RoutingProtocol,
    TransportProtocol,
)


USER_CONFIGURATION_SCHEMA_V2_ID = "sees.user_configuration.v2"

UserConfigurationSchema = dict[str, object]
UserConfigurationValidationReport = dict[str, object]


_KEY_FIELD_PATHS = frozenset(
    {
        "scenario.satellite_count",
        "scenario.user_count",
        "scenario.compute_nodes",
        "scenario.compute_capacity",
        "scenario.compute_gpu_tflops_fp32",
        "scenario.compute_npu_tops_int8",
        "scenario.orbit.update_interval_seconds",
        "scenario.orbit.plane_count",
        "scenario.orbit.altitude_m",
        "scenario.orbit.inclination_deg",
        "scenario.traffic_model.traffic_class",
        "scenario.traffic_model.destination_type",
        "scenario.traffic_model.flow_interval_seconds",
        "scenario.traffic_model.task_interval_seconds",
        "scenario.traffic_model.flow_demand_capacity",
        "scenario.traffic_model.task_compute_demand",
        "scenario.traffic_model.task_data_size",
        "scenario.traffic_model.output_data_size",
        "network.application_protocol",
        "network.transport_protocol",
        "network.transport_loss_rate",
        "network.transport_congestion_window_segments",
        "network.routing_protocol",
        "network.datalink_mac_protocol",
        "network.space_link_mode",
        "runtime.mode",
        "runtime.speed_factor",
        "runtime.seed",
        "runtime.duration",
    }
)

_SECTION_PURPOSES = {
    "scenario": "Constellation scale, compute resources, workload shaping, orbit, and demand.",
    "scenario.orbit": "Simplified deterministic orbit allocation and update cadence.",
    "scenario.traffic_model": "Flow-level communication and compute-service demand generation.",
    "network": "Flow-level protocol, routing, channel abstraction, and ISL fidelity inputs.",
    "runtime": "Execution mode, deterministic seed, pacing, and terminal duration.",
    "ui": "Frontend rendering preferences; not a source of model semantics.",
    "ui.visualization": "Initial layer visibility switches for the frontend.",
}

_LABELS = {
    "scenario.satellite_count": "Satellite count",
    "scenario.user_count": "User node count",
    "scenario.compute_nodes": "Compute satellite count",
    "scenario.compute_capacity": "CPU FP32 capacity per compute satellite",
    "scenario.compute_cpu_gflops_fp64": "CPU FP64 capacity per compute satellite",
    "scenario.compute_gpu_tflops_fp32": "GPU FP32 capacity per compute satellite",
    "scenario.compute_gpu_tflops_fp16": "GPU FP16 capacity per compute satellite",
    "scenario.compute_npu_tops_int8": "NPU INT8 capacity per compute satellite",
    "scenario.compute_memory_gb": "Memory per compute satellite",
    "scenario.compute_storage_gb": "Storage per compute satellite",
    "scenario.orbit.update_interval_seconds": "Orbit update interval",
    "scenario.orbit.plane_count": "Orbit plane count",
    "scenario.orbit.altitude_m": "Orbit altitude",
    "scenario.orbit.inclination_deg": "Orbit inclination",
    "scenario.traffic_model.flow_interval_seconds": "Flow arrival interval",
    "scenario.traffic_model.task_interval_seconds": "Task arrival interval",
    "scenario.traffic_model.flow_demand_capacity": "Flow demand capacity",
    "scenario.traffic_model.task_compute_demand": "Task compute demand",
    "scenario.traffic_model.task_data_size": "Input data size",
    "scenario.traffic_model.output_data_size": "Output data size",
    "scenario.traffic_model.emergency_weight": "Emergency service weight",
    "network.transport_loss_rate": "Transport loss proxy input",
    "network.transport_congestion_window_segments": "Transport congestion window",
    "network.carrier_frequency_hz": "Carrier frequency",
    "network.channel_bandwidth_hz": "Channel bandwidth",
    "network.rain_rate_mm_h": "Rain rate",
    "network.antenna_diameter_m": "Antenna diameter",
    "network.antenna_aperture_efficiency": "Antenna aperture efficiency",
    "network.transmit_power_dbw": "Transmit power",
    "network.system_loss_db": "System loss",
    "network.noise_temperature_k": "Noise temperature",
    "network.space_link_mode": "Space-space link mode",
    "network.time_pressure_period_s": "Temporal pressure period",
    "network.time_pressure_burst_center_phase": "Temporal pressure burst center",
    "network.time_pressure_burst_width_phase": "Temporal pressure burst width",
    "network.time_pressure_burst_amplitude": "Temporal pressure burst amplitude",
    "runtime.mode": "Runtime mode",
    "runtime.speed_factor": "Runtime speed factor",
    "runtime.seed": "Deterministic seed",
    "runtime.duration": "Simulation duration",
}

_DESCRIPTIONS = {
    "scenario.compute_capacity": (
        "Legacy scalar capacity retained for compatibility and interpreted as FP32 GFLOPS."
    ),
    "scenario.compute_nodes": (
        "Number of satellites that expose onboard compute resources."
    ),
    "scenario.orbit.orbit_update_mode": (
        "Optional override; null lets backend scale policy choose the safe update mode."
    ),
    "scenario.traffic_model.traffic_class": (
        "Primary flow-level service class when service-mix weights are all zero."
    ),
    "scenario.traffic_model.destination_type": (
        "Backend destination category for generated flows and compute services."
    ),
    "scenario.traffic_model.output_data_size": (
        "Result metadata for compute-service traffic; no packet-level output is generated."
    ),
    "scenario.traffic_model.emergency_weight": (
        "Optional deterministic service-mix weight for high-priority emergency flows."
    ),
    "network.transport_loss_rate": (
        "Deterministic flow-level loss proxy input, not packet loss simulation."
    ),
    "network.space_link_mode": (
        "Optional ISL fidelity override; null lets backend scale policy choose."
    ),
    "network.time_pressure_period_s": (
        "Period for deterministic flow-level temporal pressure KPI variation."
    ),
    "network.time_pressure_burst_center_phase": (
        "Normalized phase center of the deterministic business burst window."
    ),
    "network.time_pressure_burst_width_phase": (
        "Normalized half-width of the deterministic business burst window."
    ),
    "network.time_pressure_burst_amplitude": (
        "Additional deterministic burst envelope amplitude; no randomness or packets."
    ),
    "runtime.mode": (
        "Runtime pacing mode selected before start. Real-time mode should keep speed_factor at 1."
    ),
}

_UNITS = {
    "scenario.compute_capacity": "GFLOPS FP32",
    "scenario.compute_cpu_gflops_fp64": "GFLOPS FP64",
    "scenario.compute_gpu_tflops_fp32": "TFLOPS FP32",
    "scenario.compute_gpu_tflops_fp16": "TFLOPS FP16",
    "scenario.compute_npu_tops_int8": "TOPS INT8",
    "scenario.compute_memory_gb": "GB",
    "scenario.compute_storage_gb": "GB",
    "scenario.initial_workload_window_s": "s",
    "scenario.orbit.update_interval_seconds": "s",
    "scenario.orbit.altitude_m": "m",
    "scenario.orbit.inclination_deg": "deg",
    "scenario.traffic_model.flow_interval_seconds": "s",
    "scenario.traffic_model.task_interval_seconds": "s",
    "scenario.traffic_model.flow_demand_capacity": "Mbps",
    "scenario.traffic_model.task_data_size": "MB",
    "scenario.traffic_model.output_data_size": "MB",
    "network.carrier_frequency_hz": "Hz",
    "network.channel_bandwidth_hz": "Hz",
    "network.rain_rate_mm_h": "mm/h",
    "network.rain_attenuation_coefficient_db_per_km_per_mm_h": "dB/km/(mm/h)",
    "network.rain_effective_path_km": "km",
    "network.antenna_diameter_m": "m",
    "network.transmit_power_dbw": "dBW",
    "network.system_loss_db": "dB",
    "network.noise_temperature_k": "K",
    "network.time_pressure_period_s": "s",
    "runtime.duration": "s",
}

_ENUM_VALUES = {
    "scenario.compute_scheduling_policy": tuple(
        policy.value for policy in ComputeSchedulingPolicyConfig
    ),
    "scenario.workload_smoothing_mode": tuple(
        mode.value for mode in WorkloadSmoothingModeConfig
    ),
    "scenario.orbit.orbit_update_mode": tuple(mode.value for mode in OrbitUpdateModeConfig),
    "scenario.traffic_model.traffic_class": tuple(
        traffic_class.value for traffic_class in TrafficClassConfig
    ),
    "scenario.traffic_model.destination_type": tuple(
        destination.value for destination in TrafficDestinationTypeConfig
    ),
    "network.application_protocol": tuple(protocol.value for protocol in ApplicationProtocol),
    "network.transport_protocol": tuple(protocol.value for protocol in TransportProtocol),
    "network.routing_protocol": tuple(protocol.value for protocol in RoutingProtocol),
    "network.datalink_mac_protocol": tuple(protocol.value for protocol in DataLinkProtocol),
    "network.space_link_mode": tuple(mode.value for mode in SpaceLinkModeConfig),
    "runtime.mode": tuple(mode.value for mode in RuntimeMode),
}

_NULLABLE_PATHS = frozenset(
    {
        "scenario.orbit.orbit_update_mode",
        "network.space_link_mode",
    }
)

_POSITIVE_INT_PATHS = frozenset(
    {
        "scenario.satellite_count",
        "scenario.user_count",
        "scenario.compute_nodes",
        "scenario.cell_count",
        "scenario.orbit.update_interval_seconds",
        "scenario.orbit.plane_count",
        "scenario.traffic_model.flow_interval_seconds",
        "scenario.traffic_model.task_interval_seconds",
        "network.max_space_link_candidates_per_satellite",
        "network.batch_space_link_update_limit",
        "runtime.duration",
        "ui.update_frequency_hz",
    }
)

_NON_NEGATIVE_INT_PATHS = frozenset(
    {
        "scenario.ground_station_count",
        "scenario.max_initial_events_per_tick",
        "network.transport_congestion_window_segments",
    }
)

_POSITIVE_NUMBER_PATHS = frozenset(
    {
        "scenario.compute_capacity",
        "scenario.traffic_model.flow_demand_capacity",
        "scenario.traffic_model.task_compute_demand",
        "scenario.traffic_model.task_data_size",
        "network.carrier_frequency_hz",
        "network.channel_bandwidth_hz",
        "network.antenna_diameter_m",
        "network.noise_temperature_k",
        "network.time_pressure_period_s",
    }
)

_NON_NEGATIVE_NUMBER_PATHS = frozenset(
    {
        "scenario.compute_cpu_gflops_fp64",
        "scenario.compute_gpu_tflops_fp32",
        "scenario.compute_gpu_tflops_fp16",
        "scenario.compute_npu_tops_int8",
        "scenario.compute_memory_gb",
        "scenario.compute_storage_gb",
        "scenario.initial_workload_window_s",
        "scenario.orbit.altitude_m",
        "scenario.traffic_model.output_data_size",
        "scenario.traffic_model.data_transfer_weight",
        "scenario.traffic_model.telemetry_weight",
        "scenario.traffic_model.bulk_downlink_weight",
        "scenario.traffic_model.compute_service_weight",
        "scenario.traffic_model.emergency_weight",
        "network.rain_rate_mm_h",
        "network.rain_attenuation_coefficient_db_per_km_per_mm_h",
        "network.rain_effective_path_km",
        "network.system_loss_db",
        "network.routing_latency_weight",
        "network.routing_inverse_capacity_weight",
        "network.routing_hop_weight",
    }
)

_RANGE_LIMITS = {
    "scenario.orbit.inclination_deg": {"minimum": 0.0, "maximum": 180.0},
    "runtime.speed_factor": {"minimum": 1.0, "maximum": 100.0},
    "network.time_pressure_burst_center_phase": {"minimum": 0.0, "maximum": 1.0},
    "network.time_pressure_burst_width_phase": {"minimum": 0.0, "maximum": 1.0},
    "network.time_pressure_burst_amplitude": {"minimum": 0.0, "maximum": 1.0},
}

_PROBABILITY_PATHS = frozenset({"network.transport_loss_rate"})
_EFFICIENCY_PATHS = frozenset({"network.antenna_aperture_efficiency"})

_CONFIGURATION_EXAMPLES = (
    {
        "id": "accepted_minimal_72sat",
        "purpose": "Minimal user override; omitted fields are filled from backend defaults.",
        "mapping": {
            "scenario": {
                "satellite_count": 72,
                "compute_nodes": 72,
            },
            "runtime": {
                "duration": 600,
                "seed": 20260703,
            },
        },
        "expected": "accepted",
    },
    {
        "id": "rejected_unknown_field",
        "purpose": "Unknown keys must fail loudly instead of being ignored.",
        "mapping": {
            "scenario": {
                "satellite_count": 72,
                "unsupported_compute_gpu": 1.0,
            },
        },
        "expected": "rejected",
    },
)

_TEMPLATE_REFERENCES = (
    {
        "id": "baseline_72sat",
        "path": "configs/templates/sees_user_detailed.example.yaml",
        "scale": "72 satellites",
        "expected_kpi_behavior": "Stable baseline KPI curves for full-contract validation.",
        "fidelity_mode": "SMALL_SCALE_PER_SATELLITE_ORBIT",
        "comment_policy": "Executable YAML with user-facing comments.",
    },
    {
        "id": "dynamic_observability_120sat",
        "path": "configs/templates/sees_user_dynamic_observability.example.yaml",
        "scale": "120 satellites",
        "expected_kpi_behavior": "Time-varying network and compute observability.",
        "fidelity_mode": "MEDIUM_SCALE_DYNAMIC_OBSERVABILITY",
        "comment_policy": "Executable YAML with dashboard-oriented comments.",
    },
    {
        "id": "network_stress_120sat",
        "path": "configs/templates/sees_user_network_stress_120.example.yaml",
        "scale": "120 satellites",
        "expected_kpi_behavior": "Non-zero loss, jitter, and route-pressure proxies.",
        "fidelity_mode": "MEDIUM_SCALE_NETWORK_STRESS",
        "comment_policy": "Executable YAML with network stress comments.",
    },
    {
        "id": "large_scale_1200sat",
        "path": "configs/templates/sees_user_large_scale_1200.example.yaml",
        "scale": "1200 satellites",
        "expected_kpi_behavior": "Aggregated KPI behavior with explicit scale fidelity limits.",
        "fidelity_mode": "LARGE_SCALE_BATCH_ORBIT_BOUNDED_ISL",
        "comment_policy": "Executable YAML with scale-mode comments.",
    },
)


def build_user_configuration_schema_v2(
    config: SEESConfig | None = None,
) -> UserConfigurationSchema:
    """Return a deterministic machine-readable user configuration schema."""

    effective_config = SEESConfig() if config is None else config
    if not isinstance(effective_config, SEESConfig):
        raise TypeError("config must be SEESConfig or None")
    defaults = _flatten_paths(config_to_dict(SEESConfig()))
    current = _flatten_paths(config_to_dict(effective_config))
    field_paths = tuple(sorted(defaults))
    fields = tuple(
        _field_schema(path, defaults[path], current[path])
        for path in field_paths
    )
    return {
        "version": "v2",
        "schema_id": USER_CONFIGURATION_SCHEMA_V2_ID,
        "source": "backend_sees_config",
        "format": "YAML_OR_JSON_MAPPING",
        "unknown_key_policy": "REJECT",
        "defaulting_policy": "OMITTED_FIELDS_USE_BACKEND_DEFAULTS",
        "frontend_policy": "CONTROL_PANEL_KEY_FIELDS_ONLY",
        "forbidden_integrations": ("STK", "EXATA", "AFSIM", "DDS"),
        "packet_level_simulation": False,
        "field_count": len(fields),
        "key_field_count": sum(1 for path in field_paths if path in _KEY_FIELD_PATHS),
        "file_only_field_count": sum(1 for path in field_paths if path not in _KEY_FIELD_PATHS),
        "root_sections": tuple(_section_schema(section) for section in sorted(_SECTION_PURPOSES)),
        "fields": fields,
        "templates": _TEMPLATE_REFERENCES,
        "examples": _CONFIGURATION_EXAMPLES,
        "notes": (
            "This schema describes the full detailed config file, not only frontend controls.",
            "Template YAML files carry user-facing comments because comments are not preserved in parsed config mappings.",
            "All accepted configs are deterministic when runtime.seed and template version are fixed.",
        ),
    }


def validate_user_configuration_mapping_v2(
    raw: Mapping[str, Any],
) -> UserConfigurationValidationReport:
    """Validate a user config mapping with the v2 schema reporting contract."""

    if not isinstance(raw, Mapping):
        return _validation_report(
            ok=False,
            errors=(
                {
                    "source": "schema",
                    "message": "config root must be a mapping",
                },
            ),
        )
    try:
        config = config_from_mapping(raw)
    except ConfigValidationError as exc:
        return _validation_report(
            ok=False,
            errors=(
                {
                    "source": "config_loader",
                    "message": str(exc),
                },
            ),
        )
    return _validation_report(
        ok=True,
        errors=(),
        normalized_config=config_to_dict(config),
    )


def _validation_report(
    *,
    ok: bool,
    errors: tuple[dict[str, str], ...],
    normalized_config: Mapping[str, Any] | None = None,
) -> UserConfigurationValidationReport:
    return {
        "version": "v2",
        "schema_id": USER_CONFIGURATION_SCHEMA_V2_ID,
        "ok": ok,
        "error_count": len(errors),
        "errors": errors,
        "normalized_config": None if normalized_config is None else dict(normalized_config),
    }


def _field_schema(
    path: str,
    default_value: object,
    current_value: object,
) -> dict[str, object]:
    enum_values = _ENUM_VALUES.get(path)
    nullable = path in _NULLABLE_PATHS
    constraints = _constraints(path)
    value_type = _value_type(path, default_value, enum_values, nullable)
    field: dict[str, object] = {
        "path": path,
        "section": _most_specific_section(path),
        "label": _LABELS.get(path, _label_from_path(path)),
        "description": _DESCRIPTIONS.get(path, _default_description(path)),
        "value_type": value_type,
        "default_value": default_value,
        "current_value": current_value,
        "required_in_effective_config": True,
        "required_in_user_file": False,
        "editable_surface": (
            "CONTROL_PANEL_KEY_FIELD"
            if path in _KEY_FIELD_PATHS
            else "DETAILED_CONFIG_FILE_ONLY"
        ),
        "validation_rules": _validation_rules(path, value_type, enum_values, constraints, nullable),
    }
    if enum_values is not None:
        field["enum_values"] = enum_values
    if nullable:
        field["nullable"] = True
    if path in _UNITS:
        field["unit"] = _UNITS[path]
    field.update(constraints)
    return field


def _section_schema(section: str) -> dict[str, str]:
    return {
        "path": section,
        "purpose": _SECTION_PURPOSES[section],
    }


def _constraints(path: str) -> dict[str, object]:
    if path in _POSITIVE_INT_PATHS:
        return {"minimum": 1}
    if path in _NON_NEGATIVE_INT_PATHS:
        return {"minimum": 0}
    if path in _POSITIVE_NUMBER_PATHS:
        return {"exclusive_minimum": 0.0}
    if path in _NON_NEGATIVE_NUMBER_PATHS:
        return {"minimum": 0.0}
    if path in _PROBABILITY_PATHS:
        return {"minimum": 0.0, "exclusive_maximum": 1.0}
    if path in _EFFICIENCY_PATHS:
        return {"exclusive_minimum": 0.0, "maximum": 1.0}
    if path in _RANGE_LIMITS:
        return dict(_RANGE_LIMITS[path])
    return {}


def _validation_rules(
    path: str,
    value_type: str,
    enum_values: tuple[str, ...] | None,
    constraints: Mapping[str, object],
    nullable: bool,
) -> tuple[str, ...]:
    rules = [f"type:{value_type}"]
    if nullable:
        rules.append("nullable:true")
    if enum_values is not None:
        rules.append(f"enum:{'|'.join(enum_values)}")
    for key in sorted(constraints):
        rules.append(f"{key}:{constraints[key]}")
    if path == "scenario.traffic_model.destination_type":
        rules.append("compute_service_requires:COMPUTE_NODE")
    if path in {
        "network.routing_latency_weight",
        "network.routing_inverse_capacity_weight",
        "network.routing_hop_weight",
    }:
        rules.append("routing_requires_at_least_one_positive_weight")
    return tuple(rules)


def _value_type(
    path: str,
    default_value: object,
    enum_values: tuple[str, ...] | None,
    nullable: bool,
) -> str:
    if enum_values is not None:
        return "enum|null" if nullable else "enum"
    if default_value is None:
        return "null"
    if isinstance(default_value, bool):
        return "boolean"
    if isinstance(default_value, int):
        return "integer"
    if isinstance(default_value, float):
        return "number"
    if isinstance(default_value, str):
        return "string"
    raise TypeError(f"unsupported config default type at {path}: {type(default_value)!r}")


def _most_specific_section(path: str) -> str:
    candidates = tuple(
        section
        for section in _SECTION_PURPOSES
        if path == section or path.startswith(f"{section}.")
    )
    if not candidates:
        return path.split(".", maxsplit=1)[0]
    return max(candidates, key=len)


def _label_from_path(path: str) -> str:
    return path.rsplit(".", maxsplit=1)[-1].replace("_", " ").capitalize()


def _default_description(path: str) -> str:
    section = _most_specific_section(path)
    return f"{_SECTION_PURPOSES[section]} Field path: {path}."


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


__all__ = [
    "USER_CONFIGURATION_SCHEMA_V2_ID",
    "UserConfigurationSchema",
    "UserConfigurationValidationReport",
    "build_user_configuration_schema_v2",
    "validate_user_configuration_mapping_v2",
]
