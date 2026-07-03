"""Deterministic full-system scenario builder."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass, fields
from math import ceil, cos, isfinite, radians, sin
from pathlib import Path
from typing import Any

from leo_twin.schema import (
    ApplicationProtocol,
    DataLinkProtocol,
    FlowRequest,
    OrbitalElementSet,
    RoutingProtocol,
    TaskRequest,
    TransportProtocol,
)
from leo_twin.schema.config import SEESConfig


DEFAULT_GENERATED_SCENARIO_CONFIG_PATH = (
    Path(__file__).resolve().parents[3] / "configs" / "generated_full_system_demo.json"
)


@dataclass(frozen=True)
class FullSystemScenarioBuilderConfig:
    """Configuration for deterministic full-system scenario generation."""

    seed: int = 2026
    satellite_count: int = 72
    user_count: int = 1000
    compute_node_count: int = 10
    flow_count: int = 100
    compute_scheduling_policy: str = "FIFO"
    orbit_plane_count: int = 6
    epoch: float = 0.0
    earth_rotation_rate_rad_s: float = 0.0
    semi_major_axis_km: float = 7000.0
    eccentricity: float = 0.0
    inclination_deg: float = 53.0
    earth_radius_km: float = 6371.0
    min_elevation_deg: float = 10.0
    max_range_km: float = 2000.0
    space_link_max_range_km: float = 0.0
    space_link_capacity: float = 100.0
    space_link_cell_size_km: float = 0.0
    application_protocol: str = ApplicationProtocol.TASK_OFFLOAD_FLOW.value
    transport_protocol: str = TransportProtocol.TCP.value
    routing_protocol: str = RoutingProtocol.LINK_STATE.value
    datalink_mac_protocol: str = DataLinkProtocol.TDMA.value
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
    compute_capacity: float = 10.0
    demand_capacity: float = 1.0
    task_compute_demand: float = 20.0
    task_data_size: float = 10.0

    def __post_init__(self) -> None:
        _require_int(self.seed, "seed")
        for field_name in (
            "satellite_count",
            "user_count",
            "compute_node_count",
            "orbit_plane_count",
        ):
            _require_positive_int(getattr(self, field_name), field_name)
        _require_non_negative_int(self.flow_count, "flow_count")
        object.__setattr__(
            self,
            "compute_scheduling_policy",
            _compute_scheduling_policy(str(self.compute_scheduling_policy)),
        )
        if self.orbit_plane_count > self.satellite_count:
            raise ValueError("orbit_plane_count must be <= satellite_count")
        _require_finite_number(self.epoch, "epoch")
        _require_finite_number(
            self.earth_rotation_rate_rad_s,
            "earth_rotation_rate_rad_s",
        )
        _require_positive_number(self.semi_major_axis_km, "semi_major_axis_km")
        _require_range(self.eccentricity, "eccentricity", 0.0, 1.0)
        _require_range(self.inclination_deg, "inclination_deg", 0.0, 180.0)
        _require_positive_number(self.earth_radius_km, "earth_radius_km")
        _require_range(self.min_elevation_deg, "min_elevation_deg", -90.0, 90.0)
        _require_positive_number(self.max_range_km, "max_range_km")
        _require_non_negative_number(
            self.space_link_max_range_km,
            "space_link_max_range_km",
        )
        _require_positive_number(self.space_link_capacity, "space_link_capacity")
        _require_non_negative_number(
            self.space_link_cell_size_km,
            "space_link_cell_size_km",
        )
        object.__setattr__(
            self,
            "application_protocol",
            ApplicationProtocol(str(self.application_protocol)).value,
        )
        object.__setattr__(
            self,
            "transport_protocol",
            TransportProtocol(str(self.transport_protocol)).value,
        )
        object.__setattr__(
            self,
            "routing_protocol",
            RoutingProtocol(str(self.routing_protocol)).value,
        )
        object.__setattr__(
            self,
            "datalink_mac_protocol",
            DataLinkProtocol(str(self.datalink_mac_protocol)).value,
        )
        _require_probability(self.transport_loss_rate, "transport_loss_rate")
        _require_non_negative_int(
            self.transport_congestion_window_segments,
            "transport_congestion_window_segments",
        )
        object.__setattr__(self, "transport_loss_rate", float(self.transport_loss_rate))
        object.__setattr__(
            self,
            "transport_congestion_window_segments",
            int(self.transport_congestion_window_segments),
        )
        _require_non_negative_number(self.routing_latency_weight, "routing_latency_weight")
        _require_non_negative_number(
            self.routing_inverse_capacity_weight,
            "routing_inverse_capacity_weight",
        )
        _require_non_negative_number(self.routing_hop_weight, "routing_hop_weight")
        if (
            self.routing_latency_weight == 0.0
            and self.routing_inverse_capacity_weight == 0.0
            and self.routing_hop_weight == 0.0
        ):
            raise ValueError("at least one routing weight must be positive")
        _require_positive_number(self.carrier_frequency_hz, "carrier_frequency_hz")
        _require_positive_number(self.channel_bandwidth_hz, "channel_bandwidth_hz")
        _require_non_negative_number(self.rain_rate_mm_h, "rain_rate_mm_h")
        _require_non_negative_number(
            self.rain_attenuation_coefficient_db_per_km_per_mm_h,
            "rain_attenuation_coefficient_db_per_km_per_mm_h",
        )
        _require_non_negative_number(
            self.rain_effective_path_km,
            "rain_effective_path_km",
        )
        _require_positive_number(self.antenna_diameter_m, "antenna_diameter_m")
        _require_efficiency(
            self.antenna_aperture_efficiency,
            "antenna_aperture_efficiency",
        )
        _require_finite_number(self.transmit_power_dbw, "transmit_power_dbw")
        _require_non_negative_number(self.system_loss_db, "system_loss_db")
        _require_positive_number(self.noise_temperature_k, "noise_temperature_k")
        _require_positive_number(self.compute_capacity, "compute_capacity")
        _require_non_negative_number(self.demand_capacity, "demand_capacity")
        _require_non_negative_number(self.task_compute_demand, "task_compute_demand")
        _require_non_negative_number(self.task_data_size, "task_data_size")


@dataclass(frozen=True)
class GroundEndpointSpec:
    """Configuration-only ground endpoint spec for position-driven networking."""

    endpoint_id: str
    position: tuple[float, float, float]
    min_elevation_deg: float
    max_range_km: float


@dataclass(frozen=True)
class ComputeNodeSpec:
    """Configuration-only compute node spec."""

    node_id: str
    capacity: float


@dataclass(frozen=True)
class GeneratedFullSystemScenario:
    """Generated deterministic scenario inputs for full-system runtime assembly."""

    orbit_elements: tuple[OrbitalElementSet, ...]
    ground_endpoints: tuple[GroundEndpointSpec, ...]
    compute_nodes: tuple[ComputeNodeSpec, ...]
    flows: tuple[FlowRequest, ...]
    tasks: tuple[TaskRequest, ...]


def build_full_system_scenario(
    config: FullSystemScenarioBuilderConfig,
) -> GeneratedFullSystemScenario:
    """Generate deterministic full-system scenario inputs from config."""

    return GeneratedFullSystemScenario(
        orbit_elements=_orbit_elements(config),
        ground_endpoints=_ground_endpoints(config),
        compute_nodes=_compute_nodes(config),
        flows=_flow_requests(config),
        tasks=_task_requests(config),
    )


def load_full_system_scenario_builder_config(
    path: str | Path = DEFAULT_GENERATED_SCENARIO_CONFIG_PATH,
) -> FullSystemScenarioBuilderConfig:
    """Load deterministic generated scenario config from a JSON file."""

    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return scenario_builder_config_from_mapping(data)


def write_full_system_scenario_builder_config(
    path: str | Path,
    config: FullSystemScenarioBuilderConfig,
) -> None:
    """Write deterministic generated scenario config as JSON."""

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(
            scenario_builder_config_to_mapping(config),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def scenario_builder_config_to_mapping(
    config: FullSystemScenarioBuilderConfig,
) -> dict[str, int | float | str]:
    """Return a deterministic JSON-compatible scenario builder config."""

    if not isinstance(config, FullSystemScenarioBuilderConfig):
        raise TypeError("config must be FullSystemScenarioBuilderConfig")
    return {
        field.name: getattr(config, field.name)
        for field in fields(FullSystemScenarioBuilderConfig)
    }


def scenario_builder_config_from_mapping(
    data: Mapping[str, Any],
) -> FullSystemScenarioBuilderConfig:
    """Build a scenario builder config from a mapping with strict field checks."""

    if not isinstance(data, Mapping):
        raise TypeError("scenario builder config must be a mapping")
    allowed_fields = {field.name for field in fields(FullSystemScenarioBuilderConfig)}
    unknown_fields = tuple(sorted(set(data) - allowed_fields))
    if unknown_fields:
        raise ValueError(f"unknown scenario builder fields: {', '.join(unknown_fields)}")
    return FullSystemScenarioBuilderConfig(**dict(data))


def scenario_builder_config_from_sees_config(
    config: SEESConfig,
) -> FullSystemScenarioBuilderConfig:
    """Map SEES control-plane config into generated full-system scenario config."""

    if not isinstance(config, SEESConfig):
        raise TypeError("config must be SEESConfig")
    return FullSystemScenarioBuilderConfig(
        seed=config.runtime.seed,
        satellite_count=config.scenario.satellite_count,
        user_count=config.scenario.user_count,
        compute_node_count=config.scenario.compute_nodes,
        compute_capacity=config.scenario.compute_capacity,
        flow_count=max(
            1,
            config.runtime.duration
            // config.scenario.traffic_model.flow_interval_seconds,
        ),
        compute_scheduling_policy=config.scenario.compute_scheduling_policy.value,
        orbit_plane_count=min(
            config.scenario.satellite_count,
            config.scenario.orbit.plane_count,
        ),
        semi_major_axis_km=6371.0 + config.scenario.orbit.altitude_m / 1000.0,
        inclination_deg=config.scenario.orbit.inclination_deg,
        demand_capacity=config.scenario.traffic_model.flow_demand_capacity,
        task_compute_demand=config.scenario.traffic_model.task_compute_demand,
        task_data_size=config.scenario.traffic_model.task_data_size,
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
    )


def _orbit_elements(
    config: FullSystemScenarioBuilderConfig,
) -> tuple[OrbitalElementSet, ...]:
    satellites_per_plane = ceil(config.satellite_count / config.orbit_plane_count)
    raan_offset = _wrap_degrees(config.seed % 360)
    anomaly_offset = _wrap_degrees((config.seed * 7) % 360)
    elements: list[OrbitalElementSet] = []
    for satellite_index in range(config.satellite_count):
        plane_index = satellite_index % config.orbit_plane_count
        slot_index = satellite_index // config.orbit_plane_count
        raan_deg = _wrap_degrees(
            raan_offset + plane_index * 360.0 / config.orbit_plane_count
        )
        mean_anomaly_deg = _wrap_degrees(
            anomaly_offset + slot_index * 360.0 / satellites_per_plane
        )
        elements.append(
            OrbitalElementSet(
                satellite_id=f"sat-{satellite_index:05d}",
                epoch=config.epoch,
                semi_major_axis_km=config.semi_major_axis_km,
                eccentricity=config.eccentricity,
                inclination_deg=config.inclination_deg,
                raan_deg=raan_deg,
                argument_of_perigee_deg=0.0,
                mean_anomaly_deg=mean_anomaly_deg,
            )
        )
    return tuple(elements)


def _ground_endpoints(
    config: FullSystemScenarioBuilderConfig,
) -> tuple[GroundEndpointSpec, ...]:
    endpoints: list[GroundEndpointSpec] = []
    longitude_offset = _wrap_degrees((config.seed * 11) % 360)
    for user_index in range(config.user_count):
        latitude_deg = -60.0 + 120.0 * (user_index + 0.5) / config.user_count
        longitude_deg = _wrap_degrees(longitude_offset + user_index * 137.507764)
        endpoints.append(
            GroundEndpointSpec(
                endpoint_id=f"user-{user_index:05d}",
                position=_surface_position(
                    radius_km=config.earth_radius_km,
                    latitude_deg=latitude_deg,
                    longitude_deg=longitude_deg,
                ),
                min_elevation_deg=config.min_elevation_deg,
                max_range_km=config.max_range_km,
            )
        )
    return tuple(endpoints)


def _compute_nodes(
    config: FullSystemScenarioBuilderConfig,
) -> tuple[ComputeNodeSpec, ...]:
    return tuple(
        ComputeNodeSpec(
            node_id=f"node-{node_index:04d}",
            capacity=config.compute_capacity,
        )
        for node_index in range(config.compute_node_count)
    )


def _flow_requests(
    config: FullSystemScenarioBuilderConfig,
) -> tuple[FlowRequest, ...]:
    return tuple(
        FlowRequest(
            flow_id=f"flow-{flow_index:05d}",
            source_id=f"user-{flow_index % config.user_count:05d}",
            target_id=f"node-{flow_index % config.compute_node_count:04d}",
            demand_capacity=config.demand_capacity,
        )
        for flow_index in range(config.flow_count)
    )


def _task_requests(
    config: FullSystemScenarioBuilderConfig,
) -> tuple[TaskRequest, ...]:
    return tuple(
        TaskRequest(
            task_id=f"flow-{task_index:05d}",
            source_id=f"user-{task_index % config.user_count:05d}",
            submit_time=0.0,
            compute_demand=config.task_compute_demand,
            data_size=config.task_data_size,
        )
        for task_index in range(config.flow_count)
    )


def _surface_position(
    radius_km: float,
    latitude_deg: float,
    longitude_deg: float,
) -> tuple[float, float, float]:
    latitude_rad = radians(latitude_deg)
    longitude_rad = radians(longitude_deg)
    equatorial_radius = radius_km * cos(latitude_rad)
    return (
        equatorial_radius * cos(longitude_rad),
        equatorial_radius * sin(longitude_rad),
        radius_km * sin(latitude_rad),
    )


def _wrap_degrees(value: float) -> float:
    return float(value % 360.0)


def _require_int(value: Any, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field_name} must be an int")


def _require_positive_int(value: Any, field_name: str) -> None:
    _require_int(value, field_name)
    if value <= 0:
        raise ValueError(f"{field_name} must be positive")


def _require_non_negative_int(value: Any, field_name: str) -> None:
    _require_int(value, field_name)
    if value < 0:
        raise ValueError(f"{field_name} must be non-negative")


def _require_finite_number(value: Any, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field_name} must be an int or float")
    if not isfinite(value):
        raise ValueError(f"{field_name} must be finite")


def _require_positive_number(value: Any, field_name: str) -> None:
    _require_finite_number(value, field_name)
    if value <= 0:
        raise ValueError(f"{field_name} must be positive")


def _require_non_negative_number(value: Any, field_name: str) -> None:
    _require_finite_number(value, field_name)
    if value < 0:
        raise ValueError(f"{field_name} must be non-negative")


def _require_efficiency(value: Any, field_name: str) -> None:
    _require_finite_number(value, field_name)
    if value <= 0.0 or value > 1.0:
        raise ValueError(f"{field_name} must be in (0, 1]")


def _require_probability(value: Any, field_name: str) -> None:
    _require_finite_number(value, field_name)
    if value < 0.0 or value >= 1.0:
        raise ValueError(f"{field_name} must be in [0, 1)")


def _require_range(
    value: Any,
    field_name: str,
    lower: float,
    upper: float,
) -> None:
    _require_finite_number(value, field_name)
    if value < lower or value >= upper:
        raise ValueError(f"{field_name} must be in [{lower}, {upper})")


def _compute_scheduling_policy(value: str) -> str:
    allowed = frozenset(("FIFO", "SHORTEST_JOB_FIRST", "EARLIEST_DEADLINE_FIRST"))
    if value not in allowed:
        raise ValueError("compute_scheduling_policy must be a supported policy")
    return value
