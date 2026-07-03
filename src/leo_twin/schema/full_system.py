"""Full-system data contracts for phased high-fidelity evolution."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from math import isfinite
from typing import Any


class OrbitFidelity(StrEnum):
    """Configured orbit fidelity target without binding to an implementation."""

    KEPLERIAN = "KEPLERIAN"
    PERTURBATION_READY = "PERTURBATION_READY"
    EPHEMERIS_DRIVEN = "EPHEMERIS_DRIVEN"


class NetworkLayer(StrEnum):
    """Canonical network stack layers for the full-system phase."""

    APPLICATION = "APPLICATION"
    TRANSPORT = "TRANSPORT"
    NETWORK = "NETWORK"
    DATA_LINK = "DATA_LINK"
    PHYSICAL = "PHYSICAL"
    CHANNEL = "CHANNEL"


class ApplicationProtocol(StrEnum):
    """Application-layer flow profiles exposed to the network stack."""

    TASK_OFFLOAD_FLOW = "TASK_OFFLOAD_FLOW"
    HTTP = "HTTP"
    MQTT = "MQTT"
    TELEMETRY = "TELEMETRY"


class TransportProtocol(StrEnum):
    """Transport protocol profiles required by the product roadmap."""

    TCP = "TCP"
    UDP = "UDP"


class RoutingProtocol(StrEnum):
    """Deterministic routing protocol profile names."""

    STATIC = "STATIC"
    SHORTEST_PATH = "SHORTEST_PATH"
    LINK_STATE = "LINK_STATE"
    DISTANCE_VECTOR = "DISTANCE_VECTOR"


class DataLinkProtocol(StrEnum):
    """Deterministic data-link MAC profile names."""

    TDMA = "TDMA"
    SLOTTED_ALOHA = "SLOTTED_ALOHA"
    CSMA_CA = "CSMA_CA"


class LinkMedium(StrEnum):
    """Link medium classes used by channel and link contracts."""

    SPACE_GROUND = "SPACE_GROUND"
    SPACE_SPACE = "SPACE_SPACE"
    GROUND_GROUND = "GROUND_GROUND"


class CouplingSignalType(StrEnum):
    """Cross-domain influence classes expressed through events."""

    ORBIT_TO_NETWORK = "ORBIT_TO_NETWORK"
    NETWORK_TO_COMPUTE = "NETWORK_TO_COMPUTE"
    COMPUTE_TO_NETWORK = "COMPUTE_TO_NETWORK"
    DOMAIN_TO_METRICS = "DOMAIN_TO_METRICS"


class FrontendSurfaceRole(StrEnum):
    """User-facing frontend surface roles."""

    THREE_D_CONTROL = "THREE_D_CONTROL"
    DATA_DASHBOARD = "DATA_DASHBOARD"


@dataclass(frozen=True)
class OrbitalElementSet:
    """Configuration-only orbital element contract for later orbit engines."""

    satellite_id: str
    epoch: float
    semi_major_axis_km: float
    eccentricity: float
    inclination_deg: float
    raan_deg: float
    argument_of_perigee_deg: float
    mean_anomaly_deg: float
    fidelity: OrbitFidelity = OrbitFidelity.KEPLERIAN

    def __post_init__(self) -> None:
        _require_non_empty_str(self.satellite_id, "satellite_id")
        _require_finite_number(self.epoch, "epoch")
        _require_positive_number(self.semi_major_axis_km, "semi_major_axis_km")
        _require_range(self.eccentricity, "eccentricity", 0.0, 1.0, upper_inclusive=False)
        _require_range(self.inclination_deg, "inclination_deg", 0.0, 180.0)
        _require_range(self.raan_deg, "raan_deg", 0.0, 360.0, upper_inclusive=False)
        _require_range(
            self.argument_of_perigee_deg,
            "argument_of_perigee_deg",
            0.0,
            360.0,
            upper_inclusive=False,
        )
        _require_range(self.mean_anomaly_deg, "mean_anomaly_deg", 0.0, 360.0, upper_inclusive=False)
        if not isinstance(self.fidelity, OrbitFidelity):
            object.__setattr__(self, "fidelity", OrbitFidelity(str(self.fidelity)))


@dataclass(frozen=True)
class AntennaProfile:
    """Configuration-only antenna contract."""

    antenna_id: str
    gain_dbi: float
    beam_width_deg: float
    steering_mode: str

    def __post_init__(self) -> None:
        _require_non_empty_str(self.antenna_id, "antenna_id")
        _require_finite_number(self.gain_dbi, "gain_dbi")
        _require_range(self.beam_width_deg, "beam_width_deg", 0.0, 360.0)
        _require_non_empty_str(self.steering_mode, "steering_mode")


@dataclass(frozen=True)
class ChannelProfile:
    """Configuration-only channel contract for space and ground links."""

    channel_id: str
    medium: LinkMedium
    carrier_frequency_hz: float
    bandwidth_hz: float
    loss_model_name: str

    def __post_init__(self) -> None:
        _require_non_empty_str(self.channel_id, "channel_id")
        if not isinstance(self.medium, LinkMedium):
            object.__setattr__(self, "medium", LinkMedium(str(self.medium)))
        _require_positive_number(self.carrier_frequency_hz, "carrier_frequency_hz")
        _require_positive_number(self.bandwidth_hz, "bandwidth_hz")
        _require_non_empty_str(self.loss_model_name, "loss_model_name")


@dataclass(frozen=True)
class ProtocolLayerContract:
    """One layer contract inside a configurable network protocol stack."""

    layer: NetworkLayer
    protocol_name: str
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]
    parameters: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.layer, NetworkLayer):
            object.__setattr__(self, "layer", NetworkLayer(str(self.layer)))
        _require_non_empty_str(self.protocol_name, "protocol_name")
        object.__setattr__(self, "inputs", _normalize_str_tuple(self.inputs, "inputs"))
        object.__setattr__(self, "outputs", _normalize_str_tuple(self.outputs, "outputs"))
        object.__setattr__(self, "parameters", _normalize_parameters(self.parameters))


@dataclass(frozen=True)
class ProtocolStackContract:
    """A deterministic protocol stack contract from application to channel."""

    stack_id: str
    layers: tuple[ProtocolLayerContract, ...]

    def __post_init__(self) -> None:
        _require_non_empty_str(self.stack_id, "stack_id")
        if not self.layers:
            raise ValueError("layers must not be empty")
        normalized_layers = tuple(self.layers)
        actual_order = tuple(layer.layer for layer in normalized_layers)
        expected_order = tuple(layer for layer in _NETWORK_LAYER_ORDER if layer in actual_order)
        if actual_order != expected_order:
            raise ValueError("layers must follow canonical network stack order")
        object.__setattr__(self, "layers", normalized_layers)


@dataclass(frozen=True)
class CouplingContract:
    """Cross-domain event coupling contract."""

    coupling_id: str
    signal_type: CouplingSignalType
    producer: str
    consumer: str
    event_type: str
    payload_schema: str
    description: str

    def __post_init__(self) -> None:
        _require_non_empty_str(self.coupling_id, "coupling_id")
        if not isinstance(self.signal_type, CouplingSignalType):
            object.__setattr__(self, "signal_type", CouplingSignalType(str(self.signal_type)))
        _require_non_empty_str(self.producer, "producer")
        _require_non_empty_str(self.consumer, "consumer")
        _require_non_empty_str(self.event_type, "event_type")
        _require_non_empty_str(self.payload_schema, "payload_schema")
        _require_non_empty_str(self.description, "description")


@dataclass(frozen=True)
class FrontendSurfaceContract:
    """Contract for a Chinese user-facing frontend surface."""

    surface_id: str
    role: FrontendSurfaceRole
    title_zh: str
    websocket_topics: tuple[str, ...]
    control_enabled: bool

    def __post_init__(self) -> None:
        _require_non_empty_str(self.surface_id, "surface_id")
        if not isinstance(self.role, FrontendSurfaceRole):
            object.__setattr__(self, "role", FrontendSurfaceRole(str(self.role)))
        _require_non_empty_str(self.title_zh, "title_zh")
        object.__setattr__(
            self,
            "websocket_topics",
            _normalize_str_tuple(self.websocket_topics, "websocket_topics"),
        )
        if not isinstance(self.control_enabled, bool):
            raise TypeError("control_enabled must be a bool")


_NETWORK_LAYER_ORDER = (
    NetworkLayer.APPLICATION,
    NetworkLayer.TRANSPORT,
    NetworkLayer.NETWORK,
    NetworkLayer.DATA_LINK,
    NetworkLayer.PHYSICAL,
    NetworkLayer.CHANNEL,
)


def _require_non_empty_str(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value:
        raise TypeError(f"{field_name} must be a non-empty str")


def _require_finite_number(value: Any, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field_name} must be an int or float")
    if not isfinite(value):
        raise ValueError(f"{field_name} must be finite")


def _require_positive_number(value: Any, field_name: str) -> None:
    _require_finite_number(value, field_name)
    if value <= 0:
        raise ValueError(f"{field_name} must be positive")


def _require_range(
    value: Any,
    field_name: str,
    lower: float,
    upper: float,
    upper_inclusive: bool = True,
) -> None:
    _require_finite_number(value, field_name)
    upper_ok = value <= upper if upper_inclusive else value < upper
    if value < lower or not upper_ok:
        closing = "]" if upper_inclusive else ")"
        raise ValueError(f"{field_name} must be in [{lower}, {upper}{closing}")


def _normalize_str_tuple(values: tuple[str, ...], field_name: str) -> tuple[str, ...]:
    if not isinstance(values, tuple):
        raise TypeError(f"{field_name} must be a tuple")
    normalized = tuple(sorted(str(value) for value in values))
    if any(not value for value in normalized):
        raise ValueError(f"{field_name} must not contain empty values")
    return normalized


def _normalize_parameters(values: tuple[tuple[str, str], ...]) -> tuple[tuple[str, str], ...]:
    if not isinstance(values, tuple):
        raise TypeError("parameters must be a tuple")
    normalized: list[tuple[str, str]] = []
    for key, value in values:
        key_text = str(key)
        value_text = str(value)
        if not key_text:
            raise ValueError("parameter keys must be non-empty")
        normalized.append((key_text, value_text))
    return tuple(sorted(normalized))
