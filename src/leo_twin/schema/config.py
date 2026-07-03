"""Structured configuration schema for the SEES control plane."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from enum import StrEnum
from math import isfinite
from typing import Any

from leo_twin.schema.full_system import RoutingProtocol, TransportProtocol


class RuntimeMode(StrEnum):
    """Runtime execution modes exposed to configuration and UI controls."""

    REAL_TIME = "REAL_TIME"
    ACCELERATED = "ACCELERATED"
    PAUSED = "PAUSED"


@dataclass(frozen=True)
class OrbitParameters:
    """Configuration-only orbit parameters."""

    update_interval_seconds: int = 60
    plane_count: int = 12
    altitude_m: float = 550_000.0
    inclination_deg: float = 53.0

    def __post_init__(self) -> None:
        _require_positive_int(self.update_interval_seconds, "orbit.update_interval_seconds")
        _require_positive_int(self.plane_count, "orbit.plane_count")
        _require_non_negative_finite(self.altitude_m, "orbit.altitude_m")
        _require_finite_range(self.inclination_deg, "orbit.inclination_deg", 0.0, 180.0)


@dataclass(frozen=True)
class TrafficModel:
    """Configuration-only traffic generation parameters."""

    flow_interval_seconds: int = 60
    task_interval_seconds: int = 60
    flow_demand_capacity: float = 25.0
    task_compute_demand: float = 20.0

    def __post_init__(self) -> None:
        _require_positive_int(self.flow_interval_seconds, "traffic_model.flow_interval_seconds")
        _require_positive_int(self.task_interval_seconds, "traffic_model.task_interval_seconds")
        _require_positive_finite(self.flow_demand_capacity, "traffic_model.flow_demand_capacity")
        _require_positive_finite(self.task_compute_demand, "traffic_model.task_compute_demand")


@dataclass(frozen=True)
class NetworkProfile:
    """Configuration-only network protocol profile."""

    transport_protocol: TransportProtocol = TransportProtocol.TCP
    routing_protocol: RoutingProtocol = RoutingProtocol.LINK_STATE

    def __post_init__(self) -> None:
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


@dataclass(frozen=True)
class ScenarioConfig:
    """Scenario parameters controlled by config files and UI commands."""

    satellite_count: int = 72
    user_count: int = 1000
    compute_nodes: int = 10
    ground_station_count: int = 3
    cell_count: int = 100
    orbit: OrbitParameters = field(default_factory=OrbitParameters)
    traffic_model: TrafficModel = field(default_factory=TrafficModel)

    def __post_init__(self) -> None:
        _require_positive_int(self.satellite_count, "scenario.satellite_count")
        _require_positive_int(self.user_count, "scenario.user_count")
        _require_positive_int(self.compute_nodes, "scenario.compute_nodes")
        _require_non_negative_int(self.ground_station_count, "scenario.ground_station_count")
        _require_positive_int(self.cell_count, "scenario.cell_count")


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
