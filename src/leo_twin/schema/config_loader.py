"""Deterministic YAML/JSON configuration loader for the SEES control plane."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from leo_twin.schema.config import (
    ComputeSchedulingPolicyConfig,
    NetworkProfile,
    OrbitParameters,
    RuntimeConfig,
    RuntimeMode,
    SEESConfig,
    ScenarioConfig,
    TrafficModel,
    UIConfig,
    VisualizationToggles,
    config_to_dict,
)
from leo_twin.schema.full_system import (
    ApplicationProtocol,
    DataLinkProtocol,
    RoutingProtocol,
    TransportProtocol,
)


class ConfigValidationError(ValueError):
    """Raised when configuration data fails schema validation."""


DEFAULT_CONFIG = SEESConfig()

_TOP_LEVEL_KEYS = frozenset({"scenario", "network", "runtime", "ui"})
_SCENARIO_KEYS = frozenset(
    {
        "satellite_count",
        "user_count",
        "compute_nodes",
        "compute_capacity",
        "ground_station_count",
        "cell_count",
        "compute_scheduling_policy",
        "orbit",
        "traffic_model",
    }
)
_ORBIT_KEYS = frozenset(
    {
        "update_interval_seconds",
        "plane_count",
        "altitude_m",
        "inclination_deg",
        "orbit_update_mode",
    }
)
_TRAFFIC_KEYS = frozenset(
    {
        "flow_interval_seconds",
        "task_interval_seconds",
        "flow_demand_capacity",
        "task_compute_demand",
        "task_data_size",
    }
)
_NETWORK_KEYS = frozenset(
    {
        "application_protocol",
        "transport_protocol",
        "routing_protocol",
        "datalink_mac_protocol",
        "transport_loss_rate",
        "transport_congestion_window_segments",
        "routing_latency_weight",
        "routing_inverse_capacity_weight",
        "routing_hop_weight",
        "carrier_frequency_hz",
        "channel_bandwidth_hz",
        "rain_rate_mm_h",
        "rain_attenuation_coefficient_db_per_km_per_mm_h",
        "rain_effective_path_km",
        "antenna_diameter_m",
        "antenna_aperture_efficiency",
        "transmit_power_dbw",
        "system_loss_db",
        "noise_temperature_k",
    }
)
_RUNTIME_KEYS = frozenset({"mode", "speed_factor", "seed", "duration"})
_UI_KEYS = frozenset({"visualization", "update_frequency_hz", "dashboard_layout"})
_VISUALIZATION_KEYS = frozenset({"satellites", "links", "users", "metrics"})


def load_config(path: str | Path | None = None) -> SEESConfig:
    """Load a SEES config from YAML or JSON, using defaults when omitted."""

    if path is None:
        return DEFAULT_CONFIG
    source = Path(path)
    text = source.read_text(encoding="utf-8")
    if source.suffix.lower() == ".json":
        raw = json.loads(text)
    elif source.suffix.lower() in {".yaml", ".yml", ""}:
        raw = parse_simple_yaml(text)
    else:
        raise ConfigValidationError(f"unsupported config file type: {source.suffix}")
    return config_from_mapping(raw)


def write_config(path: str | Path, config: SEESConfig) -> None:
    """Write a deterministic YAML config file."""

    Path(path).write_text(_config_yaml(config), encoding="utf-8")


def config_from_mapping(raw: Mapping[str, Any]) -> SEESConfig:
    """Validate raw mapping data and fill missing values from defaults."""

    if not isinstance(raw, Mapping):
        raise ConfigValidationError("config root must be a mapping")
    _reject_unknown(raw, _TOP_LEVEL_KEYS, "config")
    merged = _deep_merge(config_to_dict(DEFAULT_CONFIG), raw)
    return _build_config(merged)


def merge_config_update(config: SEESConfig, update: Mapping[str, Any]) -> SEESConfig:
    """Apply a deterministic partial control-plane update to a config."""

    if not isinstance(update, Mapping):
        raise ConfigValidationError("config update must be a mapping")
    normalized = _normalize_update(update)
    merged = _deep_merge(config_to_dict(config), normalized)
    return config_from_mapping(merged)


def parse_simple_yaml(text: str) -> dict[str, Any]:
    """Parse a deterministic subset of YAML used by SEES config files."""

    root: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, root)]
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        if "\t" in raw_line:
            raise ConfigValidationError(f"tabs are not allowed in config line {line_number}")
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        key, value = _split_key_value(line.strip(), line_number)
        while stack and stack[-1][0] >= indent:
            stack.pop()
        if not stack:
            raise ConfigValidationError(f"invalid indentation at config line {line_number}")
        parent = stack[-1][1]
        if key in parent:
            raise ConfigValidationError(f"duplicate config key at line {line_number}: {key}")
        if value == "":
            child: dict[str, Any] = {}
            parent[key] = child
            stack.append((indent, child))
        else:
            parent[key] = _scalar(value)
    return root


def _build_config(data: Mapping[str, Any]) -> SEESConfig:
    try:
        scenario = _mapping(data["scenario"], "scenario")
        network = _mapping(data["network"], "network")
        runtime = _mapping(data["runtime"], "runtime")
        ui = _mapping(data["ui"], "ui")
        _reject_unknown(scenario, _SCENARIO_KEYS, "scenario")
        _reject_unknown(network, _NETWORK_KEYS, "network")
        _reject_unknown(runtime, _RUNTIME_KEYS, "runtime")
        _reject_unknown(ui, _UI_KEYS, "ui")

        orbit = _mapping(scenario["orbit"], "scenario.orbit")
        traffic = _mapping(scenario["traffic_model"], "scenario.traffic_model")
        visualization = _mapping(ui["visualization"], "ui.visualization")
        _reject_unknown(orbit, _ORBIT_KEYS, "scenario.orbit")
        _reject_unknown(traffic, _TRAFFIC_KEYS, "scenario.traffic_model")
        _reject_unknown(visualization, _VISUALIZATION_KEYS, "ui.visualization")

        return SEESConfig(
            scenario=ScenarioConfig(
                satellite_count=scenario["satellite_count"],
                user_count=scenario["user_count"],
                compute_nodes=scenario["compute_nodes"],
                compute_capacity=scenario["compute_capacity"],
                ground_station_count=scenario["ground_station_count"],
                cell_count=scenario["cell_count"],
                compute_scheduling_policy=ComputeSchedulingPolicyConfig(
                    str(scenario["compute_scheduling_policy"])
                ),
                orbit=OrbitParameters(**dict(orbit)),
                traffic_model=TrafficModel(**dict(traffic)),
            ),
            network=NetworkProfile(
                application_protocol=ApplicationProtocol(
                    str(network["application_protocol"])
                ),
                transport_protocol=TransportProtocol(str(network["transport_protocol"])),
                routing_protocol=RoutingProtocol(str(network["routing_protocol"])),
                datalink_mac_protocol=DataLinkProtocol(
                    str(network["datalink_mac_protocol"])
                ),
                transport_loss_rate=network["transport_loss_rate"],
                transport_congestion_window_segments=network[
                    "transport_congestion_window_segments"
                ],
                routing_latency_weight=network["routing_latency_weight"],
                routing_inverse_capacity_weight=network[
                    "routing_inverse_capacity_weight"
                ],
                routing_hop_weight=network["routing_hop_weight"],
                carrier_frequency_hz=network["carrier_frequency_hz"],
                channel_bandwidth_hz=network["channel_bandwidth_hz"],
                rain_rate_mm_h=network["rain_rate_mm_h"],
                rain_attenuation_coefficient_db_per_km_per_mm_h=network[
                    "rain_attenuation_coefficient_db_per_km_per_mm_h"
                ],
                rain_effective_path_km=network["rain_effective_path_km"],
                antenna_diameter_m=network["antenna_diameter_m"],
                antenna_aperture_efficiency=network["antenna_aperture_efficiency"],
                transmit_power_dbw=network["transmit_power_dbw"],
                system_loss_db=network["system_loss_db"],
                noise_temperature_k=network["noise_temperature_k"],
            ),
            runtime=RuntimeConfig(
                mode=RuntimeMode(str(runtime["mode"])),
                speed_factor=runtime["speed_factor"],
                seed=runtime["seed"],
                duration=runtime["duration"],
            ),
            ui=UIConfig(
                visualization=VisualizationToggles(**dict(visualization)),
                update_frequency_hz=ui["update_frequency_hz"],
                dashboard_layout=ui["dashboard_layout"],
            ),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ConfigValidationError(str(exc)) from exc


def _normalize_update(update: Mapping[str, Any]) -> dict[str, Any]:
    nested: dict[str, Any] = {}
    direct = dict(update)
    for key in (
        "satellite_count",
        "user_count",
        "compute_nodes",
        "compute_capacity",
        "compute_scheduling_policy",
    ):
        if key in direct:
            nested.setdefault("scenario", {})[key] = direct.pop(key)
    for key in ("mode", "speed_factor", "seed", "duration"):
        if key in direct:
            nested.setdefault("runtime", {})[key] = direct.pop(key)
    for key in (
        "application_protocol",
        "transport_protocol",
        "routing_protocol",
        "datalink_mac_protocol",
        "transport_loss_rate",
        "transport_congestion_window_segments",
        "routing_latency_weight",
        "routing_inverse_capacity_weight",
        "routing_hop_weight",
        "carrier_frequency_hz",
        "channel_bandwidth_hz",
        "rain_rate_mm_h",
        "rain_attenuation_coefficient_db_per_km_per_mm_h",
        "rain_effective_path_km",
        "antenna_diameter_m",
        "antenna_aperture_efficiency",
        "transmit_power_dbw",
        "system_loss_db",
        "noise_temperature_k",
    ):
        if key in direct:
            nested.setdefault("network", {})[key] = direct.pop(key)
    if "orbit" in direct:
        nested.setdefault("scenario", {})["orbit"] = direct.pop("orbit")
    if "traffic_model" in direct:
        nested.setdefault("scenario", {})["traffic_model"] = direct.pop("traffic_model")
    if "visualization" in direct:
        nested.setdefault("ui", {})["visualization"] = direct.pop("visualization")
    merged = _deep_merge(nested, direct)
    _reject_unknown(merged, _TOP_LEVEL_KEYS, "config update")
    return merged


def _deep_merge(base: Mapping[str, Any], overlay: Mapping[str, Any]) -> dict[str, Any]:
    result = dict(base)
    for key in sorted(overlay):
        value = overlay[key]
        existing = result.get(key)
        if isinstance(existing, Mapping) and isinstance(value, Mapping):
            result[key] = _deep_merge(existing, value)
        else:
            result[key] = value
    return result


def _reject_unknown(data: Mapping[str, Any], allowed: frozenset[str], context: str) -> None:
    unknown = sorted(str(key) for key in data if str(key) not in allowed)
    if unknown:
        raise ConfigValidationError(f"unknown {context} keys: {', '.join(unknown)}")


def _mapping(value: Any, field_name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise TypeError(f"{field_name} must be a mapping")
    return value


def _split_key_value(line: str, line_number: int) -> tuple[str, str]:
    if ":" not in line:
        raise ConfigValidationError(f"invalid config line {line_number}: {line!r}")
    key, value = line.split(":", 1)
    key = key.strip()
    if not key:
        raise ConfigValidationError(f"empty config key at line {line_number}")
    return key, value.strip()


def _scalar(value: str) -> Any:
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered == "null":
        return None
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        return value


def _config_yaml(config: SEESConfig) -> str:
    data = config_to_dict(config)
    lines: list[str] = []
    for section_name in ("scenario", "network", "runtime", "ui"):
        lines.append(f"{section_name}:")
        section = data[section_name]
        if not isinstance(section, Mapping):
            raise ConfigValidationError(f"{section_name} must be a mapping")
        _append_yaml_mapping(lines, section, indent=2, context=section_name)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _append_yaml_mapping(
    lines: list[str],
    data: Mapping[str, Any],
    indent: int,
    context: str,
) -> None:
    prefix = " " * indent
    for key in _ordered_keys(context, data):
        value = data[key]
        if isinstance(value, Mapping):
            lines.append(f"{prefix}{key}:")
            _append_yaml_mapping(lines, value, indent + 2, context=f"{context}.{key}")
        else:
            lines.append(f"{prefix}{key}: {_yaml_scalar(value)}")


def _ordered_keys(context: str, data: Mapping[str, Any]) -> tuple[str, ...]:
    preferred = {
        "scenario": (
            "satellite_count",
            "user_count",
            "compute_nodes",
            "compute_capacity",
            "ground_station_count",
            "cell_count",
            "compute_scheduling_policy",
            "orbit",
            "traffic_model",
        ),
        "scenario.orbit": (
            "update_interval_seconds",
            "plane_count",
            "altitude_m",
            "inclination_deg",
            "orbit_update_mode",
        ),
        "scenario.traffic_model": (
            "flow_interval_seconds",
            "task_interval_seconds",
            "flow_demand_capacity",
            "task_compute_demand",
            "task_data_size",
        ),
        "network": (
            "application_protocol",
            "transport_protocol",
            "routing_protocol",
            "datalink_mac_protocol",
            "transport_loss_rate",
            "transport_congestion_window_segments",
            "routing_latency_weight",
            "routing_inverse_capacity_weight",
            "routing_hop_weight",
            "carrier_frequency_hz",
            "channel_bandwidth_hz",
            "rain_rate_mm_h",
            "rain_attenuation_coefficient_db_per_km_per_mm_h",
            "rain_effective_path_km",
            "antenna_diameter_m",
            "antenna_aperture_efficiency",
            "transmit_power_dbw",
            "system_loss_db",
            "noise_temperature_k",
        ),
        "runtime": ("mode", "speed_factor", "seed", "duration"),
        "ui": ("visualization", "update_frequency_hz", "dashboard_layout"),
        "ui.visualization": ("satellites", "links", "users", "metrics"),
    }.get(context, ())
    ordered = [key for key in preferred if key in data]
    ordered.extend(sorted(str(key) for key in data if str(key) not in preferred))
    return tuple(ordered)


def _yaml_scalar(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "null"
    if isinstance(value, str):
        return value
    return str(value)
