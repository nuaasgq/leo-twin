"""Configuration loading for the full-system integration demo."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from leo_twin.core.config import (
    OrbitParameters,
    RuntimeConfig,
    RuntimeMode,
    SEESConfig,
    ScenarioConfig,
    TrafficModel,
    UIConfig,
    VisualizationToggles,
)
from leo_twin.schema.config import NetworkProfile
from leo_twin.schema.full_system import DataLinkProtocol, RoutingProtocol, TransportProtocol


@dataclass(frozen=True)
class DemoConfig:
    seed: int
    satellite_count: int
    ground_user_count: int
    ground_station_count: int
    compute_node_count: int
    duration_seconds: int
    orbit_tick_seconds: int
    network_slot_seconds: int
    flow_interval_seconds: int
    task_interval_seconds: int
    cell_count: int
    state_snapshot_interval_events: int
    metric_sample_interval: int
    websocket_events: str
    websocket_state: str
    metrics_snapshot: str
    scenario_config: str
    backend_host: str
    backend_port: int
    transport_protocol: str = "TCP"
    routing_protocol: str = "LINK_STATE"
    datalink_mac_protocol: str = "TDMA"
    carrier_frequency_hz: float = 20_000_000_000.0
    channel_bandwidth_hz: float = 100_000_000.0
    rain_rate_mm_h: float = 0.0
    rain_attenuation_coefficient_db_per_km_per_mm_h: float = 0.0
    rain_effective_path_km: float = 0.0
    antenna_diameter_m: float = 0.45
    antenna_aperture_efficiency: float = 0.65
    compute_scheduling_policy: str = "FIFO"


DEFAULT_CONFIG_PATH = Path("configs/integration_demo.yaml")


def load_demo_config(path: str | Path = DEFAULT_CONFIG_PATH) -> DemoConfig:
    data = _parse_simple_yaml(Path(path).read_text(encoding="utf-8"))
    scenario = _section(data, "scenario")
    network = data.get("network", {})
    if not isinstance(network, dict):
        raise TypeError("network must be a config section")
    frontend = _section(data, "frontend")
    return DemoConfig(
        seed=_int(scenario, "seed"),
        satellite_count=_int(scenario, "satellite_count"),
        ground_user_count=_int(scenario, "ground_user_count"),
        ground_station_count=_int(scenario, "ground_station_count"),
        compute_node_count=_int(scenario, "compute_node_count"),
        compute_scheduling_policy=_optional_str(
            scenario,
            "compute_scheduling_policy",
            "FIFO",
        ),
        duration_seconds=_int(scenario, "duration_seconds"),
        orbit_tick_seconds=_int(scenario, "orbit_tick_seconds"),
        network_slot_seconds=_int(scenario, "network_slot_seconds"),
        flow_interval_seconds=_int(scenario, "flow_interval_seconds"),
        task_interval_seconds=_int(scenario, "task_interval_seconds"),
        cell_count=_int(scenario, "cell_count"),
        state_snapshot_interval_events=_int(
            scenario,
            "state_snapshot_interval_events",
        ),
        metric_sample_interval=_int(scenario, "metric_sample_interval"),
        websocket_events=_str(frontend, "websocket_events"),
        websocket_state=_str(frontend, "websocket_state"),
        metrics_snapshot=_str(frontend, "metrics_snapshot"),
        scenario_config=_str(frontend, "scenario_config"),
        backend_host=_str(frontend, "backend_host"),
        backend_port=_int(frontend, "backend_port"),
        transport_protocol=_optional_str(network, "transport_protocol", "TCP"),
        routing_protocol=_optional_str(network, "routing_protocol", "LINK_STATE"),
        datalink_mac_protocol=_optional_str(network, "datalink_mac_protocol", "TDMA"),
        carrier_frequency_hz=_optional_float(
            network,
            "carrier_frequency_hz",
            20_000_000_000.0,
        ),
        channel_bandwidth_hz=_optional_float(
            network,
            "channel_bandwidth_hz",
            100_000_000.0,
        ),
        rain_rate_mm_h=_optional_float(network, "rain_rate_mm_h", 0.0),
        rain_attenuation_coefficient_db_per_km_per_mm_h=_optional_float(
            network,
            "rain_attenuation_coefficient_db_per_km_per_mm_h",
            0.0,
        ),
        rain_effective_path_km=_optional_float(network, "rain_effective_path_km", 0.0),
        antenna_diameter_m=_optional_float(network, "antenna_diameter_m", 0.45),
        antenna_aperture_efficiency=_optional_float(
            network,
            "antenna_aperture_efficiency",
            0.65,
        ),
    )


def demo_config_to_sees_config(config: DemoConfig) -> SEESConfig:
    """Translate legacy demo config into the SEES control-plane schema."""

    return SEESConfig(
        scenario=ScenarioConfig(
            satellite_count=config.satellite_count,
            user_count=config.ground_user_count,
            compute_nodes=config.compute_node_count,
            ground_station_count=config.ground_station_count,
            cell_count=config.cell_count,
            compute_scheduling_policy=config.compute_scheduling_policy,
            orbit=OrbitParameters(update_interval_seconds=config.orbit_tick_seconds),
            traffic_model=TrafficModel(
                flow_interval_seconds=config.flow_interval_seconds,
                task_interval_seconds=config.task_interval_seconds,
            ),
        ),
        network=NetworkProfile(
            transport_protocol=TransportProtocol(str(config.transport_protocol)),
            routing_protocol=RoutingProtocol(str(config.routing_protocol)),
            datalink_mac_protocol=DataLinkProtocol(str(config.datalink_mac_protocol)),
            carrier_frequency_hz=config.carrier_frequency_hz,
            channel_bandwidth_hz=config.channel_bandwidth_hz,
            rain_rate_mm_h=config.rain_rate_mm_h,
            rain_attenuation_coefficient_db_per_km_per_mm_h=(
                config.rain_attenuation_coefficient_db_per_km_per_mm_h
            ),
            rain_effective_path_km=config.rain_effective_path_km,
            antenna_diameter_m=config.antenna_diameter_m,
            antenna_aperture_efficiency=config.antenna_aperture_efficiency,
        ),
        runtime=RuntimeConfig(
            mode=RuntimeMode.REAL_TIME,
            speed_factor=1.0,
            seed=config.seed,
            duration=config.duration_seconds,
        ),
        ui=UIConfig(
            visualization=VisualizationToggles(),
            update_frequency_hz=max(1, 1000 // max(1, config.metric_sample_interval)),
            dashboard_layout="right_panel",
        ),
    )


def demo_config_from_sees_config(
    config: SEESConfig,
    base: DemoConfig,
) -> DemoConfig:
    """Translate control-plane config back to demo runtime configuration."""

    return DemoConfig(
        seed=config.runtime.seed,
        satellite_count=config.scenario.satellite_count,
        ground_user_count=config.scenario.user_count,
        ground_station_count=config.scenario.ground_station_count,
        compute_node_count=config.scenario.compute_nodes,
        compute_scheduling_policy=config.scenario.compute_scheduling_policy.value,
        duration_seconds=config.runtime.duration,
        orbit_tick_seconds=config.scenario.orbit.update_interval_seconds,
        network_slot_seconds=config.scenario.orbit.update_interval_seconds,
        flow_interval_seconds=config.scenario.traffic_model.flow_interval_seconds,
        task_interval_seconds=config.scenario.traffic_model.task_interval_seconds,
        cell_count=config.scenario.cell_count,
        state_snapshot_interval_events=base.state_snapshot_interval_events,
        metric_sample_interval=base.metric_sample_interval,
        websocket_events=base.websocket_events,
        websocket_state=base.websocket_state,
        metrics_snapshot=base.metrics_snapshot,
        scenario_config=base.scenario_config,
        backend_host=base.backend_host,
        backend_port=base.backend_port,
        transport_protocol=config.network.transport_protocol.value,
        routing_protocol=config.network.routing_protocol.value,
        datalink_mac_protocol=config.network.datalink_mac_protocol.value,
        carrier_frequency_hz=config.network.carrier_frequency_hz,
        channel_bandwidth_hz=config.network.channel_bandwidth_hz,
        rain_rate_mm_h=config.network.rain_rate_mm_h,
        rain_attenuation_coefficient_db_per_km_per_mm_h=(
            config.network.rain_attenuation_coefficient_db_per_km_per_mm_h
        ),
        rain_effective_path_km=config.network.rain_effective_path_km,
        antenna_diameter_m=config.network.antenna_diameter_m,
        antenna_aperture_efficiency=config.network.antenna_aperture_efficiency,
    )


def _parse_simple_yaml(text: str) -> dict[str, dict[str, Any]]:
    root: dict[str, dict[str, Any]] = {}
    current_section: str | None = None
    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        if not line.startswith(" "):
            key, value = _split_key_value(line)
            if value:
                raise ValueError("top-level config entries must be sections")
            current_section = key
            root[current_section] = {}
            continue
        if current_section is None:
            raise ValueError("nested config entry appears before a section")
        key, value = _split_key_value(line.strip())
        root[current_section][key] = _scalar(value)
    return root


def _split_key_value(line: str) -> tuple[str, str]:
    if ":" not in line:
        raise ValueError(f"invalid config line: {line!r}")
    key, value = line.split(":", 1)
    key = key.strip()
    if not key:
        raise ValueError(f"empty config key: {line!r}")
    return key, value.strip()


def _scalar(value: str) -> Any:
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        return value.strip('"')


def _section(data: dict[str, dict[str, Any]], key: str) -> dict[str, Any]:
    try:
        return data[key]
    except KeyError as exc:
        raise KeyError(f"missing config section: {key}") from exc


def _int(section: dict[str, Any], key: str) -> int:
    value = section[key]
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{key} must be an int")
    return value


def _str(section: dict[str, Any], key: str) -> str:
    value = section[key]
    if not isinstance(value, str) or not value:
        raise TypeError(f"{key} must be a non-empty string")
    return value


def _optional_str(section: dict[str, Any], key: str, default: str) -> str:
    if key not in section:
        return default
    return _str(section, key)


def _optional_float(section: dict[str, Any], key: str, default: float) -> float:
    if key not in section:
        return default
    value = section[key]
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{key} must be a number")
    return float(value)
