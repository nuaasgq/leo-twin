"""Structured configuration schema for the SEES control plane."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from enum import StrEnum
from math import isfinite
from typing import Any

from leo_twin.schema.full_system import (
    ApplicationProtocol,
    DataLinkProtocol,
    RoutingProtocol,
    TransportProtocol,
)


class RuntimeMode(StrEnum):
    """Runtime execution modes exposed to configuration and UI controls."""

    REAL_TIME = "REAL_TIME"
    ACCELERATED = "ACCELERATED"
    PAUSED = "PAUSED"


class ComputeSchedulingPolicyConfig(StrEnum):
    """Compute scheduling policies exposed through the control plane."""

    FIFO = "FIFO"
    SHORTEST_JOB_FIRST = "SHORTEST_JOB_FIRST"
    EARLIEST_DEADLINE_FIRST = "EARLIEST_DEADLINE_FIRST"


class OrbitUpdateModeConfig(StrEnum):
    """Orbit update granularity exposed through scenario configuration."""

    PER_SATELLITE = "PER_SATELLITE"
    BATCH = "BATCH"


class SpaceLinkModeConfig(StrEnum):
    """Space-space link update granularity exposed through network configuration."""

    DISABLED = "DISABLED"
    BOUNDED_CANDIDATE = "BOUNDED_CANDIDATE"
    DETAILED_SMALL_SCALE = "DETAILED_SMALL_SCALE"


class WorkloadSmoothingModeConfig(StrEnum):
    """Initial generated workload staggering exposed through configuration."""

    NONE = "NONE"
    DETERMINISTIC_STAGGER = "DETERMINISTIC_STAGGER"
    RATE_LIMITED = "RATE_LIMITED"


class TrafficClassConfig(StrEnum):
    """Flow-level traffic classes exposed through scenario configuration."""

    DATA_TRANSFER = "DATA_TRANSFER"
    TELEMETRY = "TELEMETRY"
    BULK_DOWNLINK = "BULK_DOWNLINK"
    COMPUTE_SERVICE = "COMPUTE_SERVICE"


class TrafficDestinationTypeConfig(StrEnum):
    """Traffic destination categories exposed through scenario configuration."""

    GROUND_ENDPOINT = "GROUND_ENDPOINT"
    SATELLITE = "SATELLITE"
    COMPUTE_NODE = "COMPUTE_NODE"
    SERVICE_ENDPOINT = "SERVICE_ENDPOINT"


DEFAULT_BATCH_SPACE_LINK_UPDATE_LIMIT = 999
DEFAULT_MAX_SPACE_LINK_CANDIDATES_PER_SATELLITE = 4


@dataclass(frozen=True)
class OrbitParameters:
    """Configuration-only orbit parameters."""

    update_interval_seconds: int = 60
    plane_count: int = 12
    altitude_m: float = 550_000.0
    inclination_deg: float = 53.0
    orbit_update_mode: OrbitUpdateModeConfig | None = None

    def __post_init__(self) -> None:
        _require_positive_int(self.update_interval_seconds, "orbit.update_interval_seconds")
        _require_positive_int(self.plane_count, "orbit.plane_count")
        _require_non_negative_finite(self.altitude_m, "orbit.altitude_m")
        _require_finite_range(self.inclination_deg, "orbit.inclination_deg", 0.0, 180.0)
        if self.orbit_update_mode is not None and not isinstance(
            self.orbit_update_mode,
            OrbitUpdateModeConfig,
        ):
            object.__setattr__(
                self,
                "orbit_update_mode",
                OrbitUpdateModeConfig(str(self.orbit_update_mode)),
            )


@dataclass(frozen=True)
class TrafficModel:
    """Configuration-only traffic generation parameters."""

    flow_interval_seconds: int = 60
    task_interval_seconds: int = 60
    flow_demand_capacity: float = 25.0
    task_compute_demand: float = 20.0
    task_data_size: float = 10.0
    traffic_class: TrafficClassConfig = TrafficClassConfig.COMPUTE_SERVICE
    destination_type: TrafficDestinationTypeConfig = TrafficDestinationTypeConfig.COMPUTE_NODE
    output_data_size: float = 0.0

    def __post_init__(self) -> None:
        _require_positive_int(self.flow_interval_seconds, "traffic_model.flow_interval_seconds")
        _require_positive_int(self.task_interval_seconds, "traffic_model.task_interval_seconds")
        _require_positive_finite(self.flow_demand_capacity, "traffic_model.flow_demand_capacity")
        _require_positive_finite(self.task_compute_demand, "traffic_model.task_compute_demand")
        _require_positive_finite(self.task_data_size, "traffic_model.task_data_size")
        if not isinstance(self.traffic_class, TrafficClassConfig):
            object.__setattr__(
                self,
                "traffic_class",
                TrafficClassConfig(str(self.traffic_class)),
            )
        if not isinstance(self.destination_type, TrafficDestinationTypeConfig):
            object.__setattr__(
                self,
                "destination_type",
                TrafficDestinationTypeConfig(str(self.destination_type)),
            )
        _require_non_negative_finite(self.output_data_size, "traffic_model.output_data_size")
        object.__setattr__(self, "output_data_size", float(self.output_data_size))


@dataclass(frozen=True)
class NetworkProfile:
    """Configuration-only network protocol profile."""

    application_protocol: ApplicationProtocol = ApplicationProtocol.TASK_OFFLOAD_FLOW
    transport_protocol: TransportProtocol = TransportProtocol.TCP
    routing_protocol: RoutingProtocol = RoutingProtocol.LINK_STATE
    datalink_mac_protocol: DataLinkProtocol = DataLinkProtocol.TDMA
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
    space_link_mode: SpaceLinkModeConfig | None = None
    max_space_link_candidates_per_satellite: int = (
        DEFAULT_MAX_SPACE_LINK_CANDIDATES_PER_SATELLITE
    )
    batch_space_link_update_limit: int = DEFAULT_BATCH_SPACE_LINK_UPDATE_LIMIT

    def __post_init__(self) -> None:
        if not isinstance(self.application_protocol, ApplicationProtocol):
            object.__setattr__(
                self,
                "application_protocol",
                ApplicationProtocol(str(self.application_protocol)),
            )
        if not isinstance(self.transport_protocol, TransportProtocol):
            object.__setattr__(
                self,
                "transport_protocol",
                TransportProtocol(str(self.transport_protocol)),
            )
        if not isinstance(self.routing_protocol, RoutingProtocol):
            object.__setattr__(
                self,
                "routing_protocol",
                RoutingProtocol(str(self.routing_protocol)),
            )
        if not isinstance(self.datalink_mac_protocol, DataLinkProtocol):
            object.__setattr__(
                self,
                "datalink_mac_protocol",
                DataLinkProtocol(str(self.datalink_mac_protocol)),
            )
        if self.space_link_mode is not None and not isinstance(
            self.space_link_mode,
            SpaceLinkModeConfig,
        ):
            object.__setattr__(
                self,
                "space_link_mode",
                SpaceLinkModeConfig(str(self.space_link_mode)),
            )
        _require_probability(self.transport_loss_rate, "network.transport_loss_rate")
        _require_non_negative_int(
            self.transport_congestion_window_segments,
            "network.transport_congestion_window_segments",
        )
        _require_non_negative_finite(
            self.routing_latency_weight,
            "network.routing_latency_weight",
        )
        _require_non_negative_finite(
            self.routing_inverse_capacity_weight,
            "network.routing_inverse_capacity_weight",
        )
        _require_non_negative_finite(
            self.routing_hop_weight,
            "network.routing_hop_weight",
        )
        if (
            self.routing_latency_weight == 0.0
            and self.routing_inverse_capacity_weight == 0.0
            and self.routing_hop_weight == 0.0
        ):
            raise ValueError("at least one network routing weight must be positive")
        _require_positive_finite(self.carrier_frequency_hz, "network.carrier_frequency_hz")
        _require_positive_finite(self.channel_bandwidth_hz, "network.channel_bandwidth_hz")
        _require_non_negative_finite(self.rain_rate_mm_h, "network.rain_rate_mm_h")
        _require_non_negative_finite(
            self.rain_attenuation_coefficient_db_per_km_per_mm_h,
            "network.rain_attenuation_coefficient_db_per_km_per_mm_h",
        )
        _require_non_negative_finite(
            self.rain_effective_path_km,
            "network.rain_effective_path_km",
        )
        _require_positive_finite(self.antenna_diameter_m, "network.antenna_diameter_m")
        _require_efficiency(
            self.antenna_aperture_efficiency,
            "network.antenna_aperture_efficiency",
        )
        _require_finite(self.transmit_power_dbw, "network.transmit_power_dbw")
        _require_non_negative_finite(self.system_loss_db, "network.system_loss_db")
        _require_positive_finite(self.noise_temperature_k, "network.noise_temperature_k")
        _require_positive_int(
            self.max_space_link_candidates_per_satellite,
            "network.max_space_link_candidates_per_satellite",
        )
        _require_positive_int(
            self.batch_space_link_update_limit,
            "network.batch_space_link_update_limit",
        )
        object.__setattr__(self, "carrier_frequency_hz", float(self.carrier_frequency_hz))
        object.__setattr__(self, "channel_bandwidth_hz", float(self.channel_bandwidth_hz))
        object.__setattr__(self, "rain_rate_mm_h", float(self.rain_rate_mm_h))
        object.__setattr__(
            self,
            "rain_attenuation_coefficient_db_per_km_per_mm_h",
            float(self.rain_attenuation_coefficient_db_per_km_per_mm_h),
        )
        object.__setattr__(self, "rain_effective_path_km", float(self.rain_effective_path_km))
        object.__setattr__(self, "antenna_diameter_m", float(self.antenna_diameter_m))
        object.__setattr__(
            self,
            "antenna_aperture_efficiency",
            float(self.antenna_aperture_efficiency),
        )
        object.__setattr__(self, "transmit_power_dbw", float(self.transmit_power_dbw))
        object.__setattr__(self, "system_loss_db", float(self.system_loss_db))
        object.__setattr__(self, "noise_temperature_k", float(self.noise_temperature_k))
        object.__setattr__(self, "transport_loss_rate", float(self.transport_loss_rate))
        object.__setattr__(
            self,
            "transport_congestion_window_segments",
            int(self.transport_congestion_window_segments),
        )
        object.__setattr__(
            self,
            "routing_latency_weight",
            float(self.routing_latency_weight),
        )
        object.__setattr__(
            self,
            "routing_inverse_capacity_weight",
            float(self.routing_inverse_capacity_weight),
        )
        object.__setattr__(self, "routing_hop_weight", float(self.routing_hop_weight))
        object.__setattr__(
            self,
            "max_space_link_candidates_per_satellite",
            int(self.max_space_link_candidates_per_satellite),
        )
        object.__setattr__(
            self,
            "batch_space_link_update_limit",
            int(self.batch_space_link_update_limit),
        )


@dataclass(frozen=True)
class ScenarioConfig:
    """Scenario parameters controlled by config files and UI commands."""

    satellite_count: int = 72
    user_count: int = 1000
    compute_nodes: int = 10
    compute_capacity: float = 10.0
    compute_cpu_gflops_fp64: float = 0.0
    compute_gpu_tflops_fp32: float = 0.0
    compute_gpu_tflops_fp16: float = 0.0
    compute_npu_tops_int8: float = 0.0
    compute_memory_gb: float = 0.0
    compute_storage_gb: float = 0.0
    ground_station_count: int = 3
    cell_count: int = 100
    compute_scheduling_policy: ComputeSchedulingPolicyConfig = ComputeSchedulingPolicyConfig.FIFO
    initial_workload_smoothing_enabled: bool = False
    initial_workload_window_s: float = 0.0
    max_initial_events_per_tick: int = 0
    workload_smoothing_mode: WorkloadSmoothingModeConfig = WorkloadSmoothingModeConfig.NONE
    orbit: OrbitParameters = field(default_factory=OrbitParameters)
    traffic_model: TrafficModel = field(default_factory=TrafficModel)

    def __post_init__(self) -> None:
        _require_positive_int(self.satellite_count, "scenario.satellite_count")
        _require_positive_int(self.user_count, "scenario.user_count")
        _require_positive_int(self.compute_nodes, "scenario.compute_nodes")
        _require_positive_finite(self.compute_capacity, "scenario.compute_capacity")
        for field_name in (
            "compute_cpu_gflops_fp64",
            "compute_gpu_tflops_fp32",
            "compute_gpu_tflops_fp16",
            "compute_npu_tops_int8",
            "compute_memory_gb",
            "compute_storage_gb",
        ):
            _require_non_negative_finite(
                getattr(self, field_name),
                f"scenario.{field_name}",
            )
            object.__setattr__(self, field_name, float(getattr(self, field_name)))
        _require_non_negative_int(self.ground_station_count, "scenario.ground_station_count")
        _require_positive_int(self.cell_count, "scenario.cell_count")
        if not isinstance(self.compute_scheduling_policy, ComputeSchedulingPolicyConfig):
            object.__setattr__(
                self,
                "compute_scheduling_policy",
                ComputeSchedulingPolicyConfig(str(self.compute_scheduling_policy)),
            )
        _require_bool(
            self.initial_workload_smoothing_enabled,
            "scenario.initial_workload_smoothing_enabled",
        )
        _require_non_negative_finite(
            self.initial_workload_window_s,
            "scenario.initial_workload_window_s",
        )
        _require_non_negative_int(
            self.max_initial_events_per_tick,
            "scenario.max_initial_events_per_tick",
        )
        if not isinstance(self.workload_smoothing_mode, WorkloadSmoothingModeConfig):
            object.__setattr__(
                self,
                "workload_smoothing_mode",
                WorkloadSmoothingModeConfig(str(self.workload_smoothing_mode)),
            )
        object.__setattr__(
            self,
            "initial_workload_window_s",
            float(self.initial_workload_window_s),
        )


@dataclass(frozen=True)
class RuntimeConfig:
    """Runtime execution control parameters."""

    mode: RuntimeMode = RuntimeMode.REAL_TIME
    speed_factor: float = 1.0
    seed: int = 20_260_703
    duration: int = 600

    def __post_init__(self) -> None:
        if not isinstance(self.mode, RuntimeMode):
            object.__setattr__(self, "mode", RuntimeMode(str(self.mode)))
        _require_speed_factor(self.speed_factor)
        object.__setattr__(self, "speed_factor", float(self.speed_factor))
        _require_int(self.seed, "runtime.seed")
        _require_positive_int(self.duration, "runtime.duration")


@dataclass(frozen=True)
class VisualizationToggles:
    """UI rendering switches controlled by configuration."""

    satellites: bool = True
    links: bool = True
    users: bool = True
    metrics: bool = True

    def __post_init__(self) -> None:
        _require_bool(self.satellites, "ui.visualization.satellites")
        _require_bool(self.links, "ui.visualization.links")
        _require_bool(self.users, "ui.visualization.users")
        _require_bool(self.metrics, "ui.visualization.metrics")


@dataclass(frozen=True)
class UIConfig:
    """Frontend control-plane preferences."""

    visualization: VisualizationToggles = field(default_factory=VisualizationToggles)
    update_frequency_hz: int = 20
    dashboard_layout: str = "right_panel"

    def __post_init__(self) -> None:
        _require_positive_int(self.update_frequency_hz, "ui.update_frequency_hz")
        if not isinstance(self.dashboard_layout, str) or not self.dashboard_layout:
            raise TypeError("ui.dashboard_layout must be a non-empty string")


@dataclass(frozen=True)
class SEESConfig:
    """Top-level deterministic control-plane configuration."""

    scenario: ScenarioConfig = field(default_factory=ScenarioConfig)
    network: NetworkProfile = field(default_factory=NetworkProfile)
    runtime: RuntimeConfig = field(default_factory=RuntimeConfig)
    ui: UIConfig = field(default_factory=UIConfig)


def config_to_dict(config: SEESConfig) -> dict[str, Any]:
    """Return a deterministic JSON-compatible representation of a config."""

    if not is_dataclass(config) or isinstance(config, type):
        raise TypeError("config_to_dict requires a SEESConfig instance")
    return _normalize_value(asdict(config))


def _normalize_value(value: Any) -> Any:
    if isinstance(value, StrEnum):
        return value.value
    if isinstance(value, dict):
        return {str(key): _normalize_value(value[key]) for key in sorted(value)}
    if isinstance(value, list):
        return [_normalize_value(item) for item in value]
    return value


def _require_bool(value: bool, field_name: str) -> None:
    if not isinstance(value, bool):
        raise TypeError(f"{field_name} must be a bool")


def _require_int(value: int, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field_name} must be an int")


def _require_positive_int(value: int, field_name: str) -> None:
    _require_int(value, field_name)
    if value <= 0:
        raise ValueError(f"{field_name} must be positive")


def _require_non_negative_int(value: int, field_name: str) -> None:
    _require_int(value, field_name)
    if value < 0:
        raise ValueError(f"{field_name} must be non-negative")


def _require_positive_finite(value: float, field_name: str) -> None:
    _require_finite(value, field_name)
    if value <= 0:
        raise ValueError(f"{field_name} must be positive")


def _require_non_negative_finite(value: float, field_name: str) -> None:
    _require_finite(value, field_name)
    if value < 0:
        raise ValueError(f"{field_name} must be non-negative")


def _require_efficiency(value: float, field_name: str) -> None:
    _require_finite(value, field_name)
    if value <= 0.0 or value > 1.0:
        raise ValueError(f"{field_name} must be in (0, 1]")


def _require_probability(value: float, field_name: str) -> None:
    _require_finite(value, field_name)
    if value < 0.0 or value >= 1.0:
        raise ValueError(f"{field_name} must be in [0, 1)")


def _require_finite_range(
    value: float,
    field_name: str,
    minimum: float,
    maximum: float,
) -> None:
    _require_finite(value, field_name)
    if value < minimum or value > maximum:
        raise ValueError(f"{field_name} must be in [{minimum}, {maximum}]")


def _require_finite(value: float, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field_name} must be an int or float")
    if not isfinite(float(value)):
        raise ValueError(f"{field_name} must be finite")


def _require_speed_factor(value: float) -> None:
    _require_finite(value, "runtime.speed_factor")
    if value < 1.0 or value > 100.0:
        raise ValueError("runtime.speed_factor must be in [1, 100]")
