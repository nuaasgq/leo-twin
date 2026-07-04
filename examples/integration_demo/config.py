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
from leo_twin.schema.config import (
    DEFAULT_BATCH_SPACE_LINK_UPDATE_LIMIT,
    DEFAULT_MAX_SPACE_LINK_CANDIDATES_PER_SATELLITE,
    NetworkProfile,
    WorkloadSmoothingModeConfig,
)
from leo_twin.schema.full_system import (
    ApplicationProtocol,
    DataLinkProtocol,
    RoutingProtocol,
    TransportProtocol,
)


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
    compute_capacity: float = 10.0
    orbit_plane_count: int = 12
    orbit_plane_count_explicit: bool = True
    constellation_profile: str = "CUSTOM_WALKER"
    orbit_altitude_m: float = 529_000.0
    orbit_inclination_deg: float = 53.0
    orbit_update_mode: str | None = None
    flow_demand_capacity: float = 25.0
    task_compute_demand: float = 20.0
    task_data_size: float = 2.0
    application_protocol: str = "TASK_OFFLOAD_FLOW"
    transport_protocol: str = "TCP"
    routing_protocol: str = "LINK_STATE"
    datalink_mac_protocol: str = "TDMA"
    transport_loss_rate: float = 0.0
    transport_congestion_window_segments: int = 0
    routing_latency_weight: float = 1.0
    routing_inverse_capacity_weight: float = 0.0
    routing_hop_weight: float = 0.0
    carrier_frequency_hz: float = 20_000_000_000.0
    channel_bandwidth_hz: float = 100_000_000.0
    rain_rate_mm_h: float = 0.0
    rain_attenuation_coefficient_db_per_km_per_mm_h: float = 0.0
    rain_effective_path_km: float = 0.0
    antenna_diameter_m: float = 0.45
    antenna_aperture_efficiency: float = 0.65
    transmit_power_dbw: float = 20.0
    system_loss_db: float = 1.0
    noise_temperature_k: float = 290.0
    space_link_mode: str | None = None
    max_space_link_candidates_per_satellite: int = (
        DEFAULT_MAX_SPACE_LINK_CANDIDATES_PER_SATELLITE
    )
    batch_space_link_update_limit: int = DEFAULT_BATCH_SPACE_LINK_UPDATE_LIMIT
    initial_workload_smoothing_enabled: bool = False
    initial_workload_window_s: float = 0.0
    max_initial_events_per_tick: int = 0
    workload_smoothing_mode: str = "NONE"
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
        compute_capacity=_optional_float(scenario, "compute_capacity", 10.0),
        compute_scheduling_policy=_optional_str(
            scenario,
            "compute_scheduling_policy",
            "FIFO",
        ),
        duration_seconds=_int(scenario, "duration_seconds"),
        orbit_tick_seconds=_int(scenario, "orbit_tick_seconds"),
        orbit_plane_count=_optional_int(scenario, "orbit_plane_count", 12),
        orbit_plane_count_explicit="orbit_plane_count" in scenario,
        constellation_profile=_optional_str(
            scenario,
            "constellation_profile",
            "CUSTOM_WALKER",
        ),
        orbit_altitude_m=_optional_float(scenario, "orbit_altitude_m", 529_000.0),
        orbit_inclination_deg=_optional_float(scenario, "orbit_inclination_deg", 53.0),
        orbit_update_mode=_optional_nullable_str(scenario, "orbit_update_mode"),
        initial_workload_smoothing_enabled=_optional_bool(
            scenario,
            "initial_workload_smoothing_enabled",
            False,
        ),
        initial_workload_window_s=_optional_float(
            scenario,
            "initial_workload_window_s",
            0.0,
        ),
        max_initial_events_per_tick=_optional_int(
            scenario,
            "max_initial_events_per_tick",
            0,
        ),
        workload_smoothing_mode=_optional_str(
            scenario,
            "workload_smoothing_mode",
            "NONE",
        ),
        network_slot_seconds=_int(scenario, "network_slot_seconds"),
        flow_interval_seconds=_int(scenario, "flow_interval_seconds"),
        task_interval_seconds=_int(scenario, "task_interval_seconds"),
        flow_demand_capacity=_optional_float(scenario, "flow_demand_capacity", 25.0),
        task_compute_demand=_optional_float(scenario, "task_compute_demand", 20.0),
        task_data_size=_optional_float(scenario, "task_data_size", 2.0),
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
        application_protocol=_optional_str(
            network,
            "application_protocol",
            "TASK_OFFLOAD_FLOW",
        ),
        transport_protocol=_optional_str(network, "transport_protocol", "TCP"),
        routing_protocol=_optional_str(network, "routing_protocol", "LINK_STATE"),
        datalink_mac_protocol=_optional_str(network, "datalink_mac_protocol", "TDMA"),
        transport_loss_rate=_optional_float(network, "transport_loss_rate", 0.0),
        transport_congestion_window_segments=_optional_int(
            network,
            "transport_congestion_window_segments",
            0,
        ),
        routing_latency_weight=_optional_float(network, "routing_latency_weight", 1.0),
        routing_inverse_capacity_weight=_optional_float(
            network,
            "routing_inverse_capacity_weight",
            0.0,
        ),
        routing_hop_weight=_optional_float(network, "routing_hop_weight", 0.0),
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
        transmit_power_dbw=_optional_float(network, "transmit_power_dbw", 20.0),
        system_loss_db=_optional_float(network, "system_loss_db", 1.0),
        noise_temperature_k=_optional_float(network, "noise_temperature_k", 290.0),
        space_link_mode=_optional_nullable_str(network, "space_link_mode"),
        max_space_link_candidates_per_satellite=_optional_int(
            network,
            "max_space_link_candidates_per_satellite",
            DEFAULT_MAX_SPACE_LINK_CANDIDATES_PER_SATELLITE,
        ),
        batch_space_link_update_limit=_optional_int(
            network,
            "batch_space_link_update_limit",
            DEFAULT_BATCH_SPACE_LINK_UPDATE_LIMIT,
        ),
    )


def demo_config_to_sees_config(config: DemoConfig) -> SEESConfig:
    """Translate legacy demo config into the SEES control-plane schema."""

    return SEESConfig(
        scenario=ScenarioConfig(
            satellite_count=config.satellite_count,
            user_count=config.ground_user_count,
            compute_nodes=config.compute_node_count,
            compute_capacity=config.compute_capacity,
            ground_station_count=config.ground_station_count,
            cell_count=config.cell_count,
            compute_scheduling_policy=config.compute_scheduling_policy,
            initial_workload_smoothing_enabled=(
                config.initial_workload_smoothing_enabled
            ),
            initial_workload_window_s=config.initial_workload_window_s,
            max_initial_events_per_tick=config.max_initial_events_per_tick,
            workload_smoothing_mode=WorkloadSmoothingModeConfig(
                str(config.workload_smoothing_mode)
            ),
            orbit=OrbitParameters(
                update_interval_seconds=config.orbit_tick_seconds,
                plane_count=config.orbit_plane_count,
                altitude_m=config.orbit_altitude_m,
                inclination_deg=config.orbit_inclination_deg,
                orbit_update_mode=config.orbit_update_mode,
            ),
            traffic_model=TrafficModel(
                flow_interval_seconds=config.flow_interval_seconds,
                task_interval_seconds=config.task_interval_seconds,
                flow_demand_capacity=config.flow_demand_capacity,
                task_compute_demand=config.task_compute_demand,
                task_data_size=config.task_data_size,
            ),
        ),
        network=NetworkProfile(
            application_protocol=ApplicationProtocol(str(config.application_protocol)),
            transport_protocol=TransportProtocol(str(config.transport_protocol)),
            routing_protocol=RoutingProtocol(str(config.routing_protocol)),
            datalink_mac_protocol=DataLinkProtocol(str(config.datalink_mac_protocol)),
            transport_loss_rate=config.transport_loss_rate,
            transport_congestion_window_segments=(
                config.transport_congestion_window_segments
            ),
            routing_latency_weight=config.routing_latency_weight,
            routing_inverse_capacity_weight=config.routing_inverse_capacity_weight,
            routing_hop_weight=config.routing_hop_weight,
            carrier_frequency_hz=config.carrier_frequency_hz,
            channel_bandwidth_hz=config.channel_bandwidth_hz,
            rain_rate_mm_h=config.rain_rate_mm_h,
            rain_attenuation_coefficient_db_per_km_per_mm_h=(
                config.rain_attenuation_coefficient_db_per_km_per_mm_h
            ),
            rain_effective_path_km=config.rain_effective_path_km,
            antenna_diameter_m=config.antenna_diameter_m,
            antenna_aperture_efficiency=config.antenna_aperture_efficiency,
            transmit_power_dbw=config.transmit_power_dbw,
            system_loss_db=config.system_loss_db,
            noise_temperature_k=config.noise_temperature_k,
            space_link_mode=config.space_link_mode,
            max_space_link_candidates_per_satellite=(
                config.max_space_link_candidates_per_satellite
            ),
            batch_space_link_update_limit=config.batch_space_link_update_limit,
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
        compute_capacity=config.scenario.compute_capacity,
        compute_scheduling_policy=config.scenario.compute_scheduling_policy.value,
        duration_seconds=config.runtime.duration,
        orbit_tick_seconds=config.scenario.orbit.update_interval_seconds,
        orbit_plane_count=config.scenario.orbit.plane_count,
        orbit_plane_count_explicit=True,
        constellation_profile=base.constellation_profile,
        orbit_altitude_m=config.scenario.orbit.altitude_m,
        orbit_inclination_deg=config.scenario.orbit.inclination_deg,
        orbit_update_mode=(
            config.scenario.orbit.orbit_update_mode.value
            if config.scenario.orbit.orbit_update_mode is not None
            else None
        ),
        initial_workload_smoothing_enabled=(
            config.scenario.initial_workload_smoothing_enabled
        ),
        initial_workload_window_s=config.scenario.initial_workload_window_s,
        max_initial_events_per_tick=config.scenario.max_initial_events_per_tick,
        workload_smoothing_mode=config.scenario.workload_smoothing_mode.value,
        network_slot_seconds=config.scenario.orbit.update_interval_seconds,
        flow_interval_seconds=config.scenario.traffic_model.flow_interval_seconds,
        task_interval_seconds=config.scenario.traffic_model.task_interval_seconds,
        flow_demand_capacity=config.scenario.traffic_model.flow_demand_capacity,
        task_compute_demand=config.scenario.traffic_model.task_compute_demand,
        task_data_size=config.scenario.traffic_model.task_data_size,
        cell_count=config.scenario.cell_count,
        state_snapshot_interval_events=base.state_snapshot_interval_events,
        metric_sample_interval=base.metric_sample_interval,
        websocket_events=base.websocket_events,
        websocket_state=base.websocket_state,
        metrics_snapshot=base.metrics_snapshot,
        scenario_config=base.scenario_config,
        backend_host=base.backend_host,
        backend_port=base.backend_port,
        application_protocol=config.network.application_protocol.value,
        transport_protocol=config.network.transport_protocol.value,
        routing_protocol=config.network.routing_protocol.value,
        datalink_mac_protocol=config.network.datalink_mac_protocol.value,
        transport_loss_rate=config.network.transport_loss_rate,
        transport_congestion_window_segments=(
            config.network.transport_congestion_window_segments
        ),
        routing_latency_weight=config.network.routing_latency_weight,
        routing_inverse_capacity_weight=config.network.routing_inverse_capacity_weight,
        routing_hop_weight=config.network.routing_hop_weight,
        carrier_frequency_hz=config.network.carrier_frequency_hz,
        channel_bandwidth_hz=config.network.channel_bandwidth_hz,
        rain_rate_mm_h=config.network.rain_rate_mm_h,
        rain_attenuation_coefficient_db_per_km_per_mm_h=(
            config.network.rain_attenuation_coefficient_db_per_km_per_mm_h
        ),
        rain_effective_path_km=config.network.rain_effective_path_km,
        antenna_diameter_m=config.network.antenna_diameter_m,
        antenna_aperture_efficiency=config.network.antenna_aperture_efficiency,
        transmit_power_dbw=config.network.transmit_power_dbw,
        system_loss_db=config.network.system_loss_db,
        noise_temperature_k=config.network.noise_temperature_k,
        space_link_mode=(
            config.network.space_link_mode.value
            if config.network.space_link_mode is not None
            else None
        ),
        max_space_link_candidates_per_satellite=(
            config.network.max_space_link_candidates_per_satellite
        ),
        batch_space_link_update_limit=config.network.batch_space_link_update_limit,
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


def _optional_nullable_str(section: dict[str, Any], key: str) -> str | None:
    if key not in section or section[key] is None:
        return None
    return _str(section, key)


def _optional_int(section: dict[str, Any], key: str, default: int) -> int:
    if key not in section:
        return default
    return _int(section, key)


def _optional_bool(section: dict[str, Any], key: str, default: bool) -> bool:
    if key not in section:
        return default
    value = section[key]
    if not isinstance(value, bool):
        raise TypeError(f"{key} must be a bool")
    return value


def _optional_float(section: dict[str, Any], key: str, default: float) -> float:
    if key not in section:
        return default
    value = section[key]
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{key} must be a number")
    return float(value)
