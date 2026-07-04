"""Frozen product-level domain data contracts."""

from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from enum import StrEnum
from json import dumps
from math import isfinite
from typing import Any


class RuntimeStatus(StrEnum):
    """Runtime lifecycle states shared by backend control and frontend snapshot."""

    STOPPED = "STOPPED"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"


class RuntimeMode(StrEnum):
    """Runtime pacing modes shared by backend control and frontend snapshot."""

    REAL_TIME = "REAL_TIME"
    ACCELERATED = "ACCELERATED"
    PAUSED = "PAUSED"


@dataclass(frozen=True)
class SatelliteState:
    """Canonical state published by orbit and consumed by all domains."""

    satellite_id: str
    sim_time: float
    position: tuple[float, float, float]
    velocity: tuple[float, float, float]
    status: str

    def __post_init__(self) -> None:
        _require_non_empty_str(self.satellite_id, "satellite_id")
        _require_finite_number(self.sim_time, "sim_time")
        _require_vector3(self.position, "position")
        _require_vector3(self.velocity, "velocity")
        _require_non_empty_str(self.status, "status")


@dataclass(frozen=True)
class OrbitBatchState:
    """Canonical batch of satellite states for scale-safe orbit publication."""

    sim_time: float
    satellite_states: tuple[SatelliteState, ...]
    satellite_count: int
    partition_id: str | None = None

    def __post_init__(self) -> None:
        _require_finite_number(self.sim_time, "sim_time")
        if not isinstance(self.satellite_states, tuple):
            raise TypeError("satellite_states must be a tuple")
        if any(not isinstance(state, SatelliteState) for state in self.satellite_states):
            raise TypeError("satellite_states must contain SatelliteState items")
        _require_non_negative_int(self.satellite_count, "satellite_count")
        if self.satellite_count != len(self.satellite_states):
            raise ValueError("satellite_count must match satellite_states length")
        for state in self.satellite_states:
            if state.sim_time != self.sim_time:
                raise ValueError("each satellite state sim_time must match batch sim_time")
        object.__setattr__(
            self,
            "satellite_states",
            tuple(sorted(self.satellite_states, key=lambda item: item.satellite_id)),
        )
        if self.partition_id is not None:
            _require_non_empty_str(self.partition_id, "partition_id")


@dataclass(frozen=True)
class GroundUserState:
    """Canonical frontend and network contract for ground users."""

    user_id: str
    position: tuple[float, float, float] | None = None
    cell_id: str | None = None
    status: str = "ACTIVE"

    def __post_init__(self) -> None:
        _require_non_empty_str(self.user_id, "user_id")
        if self.position is not None:
            _require_vector3(self.position, "position")
        if self.cell_id is not None:
            _require_non_empty_str(self.cell_id, "cell_id")
        _require_non_empty_str(self.status, "status")


@dataclass(frozen=True)
class AccessAssociation:
    """Satellite-ground association output by the network module."""

    satellite_id: str
    user_id: str

    def __post_init__(self) -> None:
        _require_non_empty_str(self.satellite_id, "satellite_id")
        _require_non_empty_str(self.user_id, "user_id")


@dataclass(frozen=True)
class ChannelState:
    """Canonical channel observation for space-ground and space-space links."""

    channel_id: str
    sim_time: float
    source_id: str
    target_id: str
    medium: str
    carrier_frequency_hz: float
    bandwidth_hz: float
    availability: bool
    attenuation_db: float = 0.0
    snr_db: float | None = None

    def __post_init__(self) -> None:
        _require_non_empty_str(self.channel_id, "channel_id")
        _require_finite_number(self.sim_time, "sim_time")
        _require_non_empty_str(self.source_id, "source_id")
        _require_non_empty_str(self.target_id, "target_id")
        _require_non_empty_str(self.medium, "medium")
        _require_positive_number(self.carrier_frequency_hz, "carrier_frequency_hz")
        _require_positive_number(self.bandwidth_hz, "bandwidth_hz")
        _require_bool(self.availability, "availability")
        _require_non_negative_number(self.attenuation_db, "attenuation_db")
        if self.snr_db is not None:
            _require_finite_number(self.snr_db, "snr_db")


@dataclass(frozen=True)
class LinkState:
    """Canonical flow-level link abstraction."""

    source_id: str
    target_id: str
    latency: float
    capacity: float
    availability: bool
    link_id: str = ""
    channel_id: str | None = None
    medium: str | None = None
    utilization: float | None = None

    def __post_init__(self) -> None:
        _require_non_empty_str(self.source_id, "source_id")
        _require_non_empty_str(self.target_id, "target_id")
        _require_non_negative_number(self.latency, "latency")
        _require_non_negative_number(self.capacity, "capacity")
        _require_bool(self.availability, "availability")
        if not self.link_id:
            object.__setattr__(self, "link_id", f"{self.source_id}->{self.target_id}")
        else:
            _require_non_empty_str(self.link_id, "link_id")
        if self.channel_id is not None:
            _require_non_empty_str(self.channel_id, "channel_id")
        if self.medium is not None:
            _require_non_empty_str(self.medium, "medium")
        if self.utilization is not None:
            _require_probability(self.utilization, "utilization")


@dataclass(frozen=True)
class RouteState:
    """Canonical deterministic route output for one flow request."""

    route_id: str
    flow_id: str
    path: tuple[str, ...]
    latency: float
    capacity: float
    available: bool
    routing_protocol: str | None = None
    cost: float | None = None

    def __post_init__(self) -> None:
        _require_non_empty_str(self.route_id, "route_id")
        _require_non_empty_str(self.flow_id, "flow_id")
        object.__setattr__(self, "path", _normalize_str_tuple(self.path, "path", sort=False))
        _require_non_negative_number(self.latency, "latency")
        _require_non_negative_number(self.capacity, "capacity")
        _require_bool(self.available, "available")
        if self.routing_protocol is not None:
            _require_non_empty_str(self.routing_protocol, "routing_protocol")
        if self.cost is not None:
            _require_non_negative_number(self.cost, "cost")


Route = RouteState


@dataclass(frozen=True)
class FlowRequest:
    """Canonical flow-level route request consumed by network engines."""

    flow_id: str
    source_id: str
    target_id: str
    demand_capacity: float
    application_id: str | None = None
    priority: int = 0

    def __post_init__(self) -> None:
        _require_non_empty_str(self.flow_id, "flow_id")
        _require_non_empty_str(self.source_id, "source_id")
        _require_non_empty_str(self.target_id, "target_id")
        _require_non_negative_number(self.demand_capacity, "demand_capacity")
        if self.application_id is not None:
            _require_non_empty_str(self.application_id, "application_id")
        _require_int(self.priority, "priority")


@dataclass(frozen=True)
class FlowState:
    """Canonical flow state consumed by compute and metrics modules."""

    flow_id: str
    route_id: str
    source_id: str
    target_id: str
    status: str
    route_path: tuple[str, ...] = ()
    latency: float | None = None
    capacity: float | None = None

    def __post_init__(self) -> None:
        _require_non_empty_str(self.flow_id, "flow_id")
        _require_non_empty_str(self.route_id, "route_id")
        _require_non_empty_str(self.source_id, "source_id")
        _require_non_empty_str(self.target_id, "target_id")
        _require_non_empty_str(self.status, "status")
        object.__setattr__(
            self,
            "route_path",
            _normalize_str_tuple(self.route_path, "route_path", sort=False),
        )
        if self.latency is not None:
            _require_non_negative_number(self.latency, "latency")
        if self.capacity is not None:
            _require_non_negative_number(self.capacity, "capacity")


@dataclass(frozen=True)
class TransportState:
    """Canonical transport-layer state for a flow."""

    flow_id: str
    sim_time: float
    protocol: str
    status: str
    loss_rate: float = 0.0
    congestion_window_segments: int = 0

    def __post_init__(self) -> None:
        _require_non_empty_str(self.flow_id, "flow_id")
        _require_finite_number(self.sim_time, "sim_time")
        _require_non_empty_str(self.protocol, "protocol")
        _require_non_empty_str(self.status, "status")
        _require_probability(self.loss_rate, "loss_rate")
        _require_non_negative_int(
            self.congestion_window_segments,
            "congestion_window_segments",
        )


@dataclass(frozen=True)
class ApplicationState:
    """Canonical application-layer state for a flow."""

    flow_id: str
    sim_time: float
    protocol: str
    status: str
    demand_capacity: float
    source_id: str | None = None
    target_id: str | None = None

    def __post_init__(self) -> None:
        _require_non_empty_str(self.flow_id, "flow_id")
        _require_finite_number(self.sim_time, "sim_time")
        _require_non_empty_str(self.protocol, "protocol")
        _require_non_empty_str(self.status, "status")
        _require_non_negative_number(self.demand_capacity, "demand_capacity")
        if self.source_id is not None:
            _require_non_empty_str(self.source_id, "source_id")
        if self.target_id is not None:
            _require_non_empty_str(self.target_id, "target_id")


@dataclass(frozen=True)
class ComputeNodeState:
    """Canonical compute node state published by the compute module."""

    node_id: str
    sim_time: float
    capacity: float
    available_capacity: float
    status: str
    load_ratio: float | None = None
    cpu_gflops_fp64: float = 0.0
    gpu_tflops_fp32: float = 0.0
    gpu_tflops_fp16: float = 0.0
    npu_tops_int8: float = 0.0
    memory_gb: float = 0.0
    storage_gb: float = 0.0
    resource_usage_mode: str = "SCALAR_FP32_ONLY"
    available_cpu_gflops_fp32: float = 0.0
    used_cpu_gflops_fp32: float = 0.0
    available_cpu_gflops_fp64: float = 0.0
    used_cpu_gflops_fp64: float = 0.0
    available_gpu_tflops_fp32: float = 0.0
    used_gpu_tflops_fp32: float = 0.0
    available_gpu_tflops_fp16: float = 0.0
    used_gpu_tflops_fp16: float = 0.0
    available_npu_tops_int8: float = 0.0
    used_npu_tops_int8: float = 0.0
    available_memory_gb: float = 0.0
    used_memory_gb: float = 0.0
    available_storage_gb: float = 0.0
    used_storage_gb: float = 0.0

    def __post_init__(self) -> None:
        _require_non_empty_str(self.node_id, "node_id")
        _require_finite_number(self.sim_time, "sim_time")
        _require_non_negative_number(self.capacity, "capacity")
        _require_non_negative_number(self.available_capacity, "available_capacity")
        _require_non_empty_str(self.status, "status")
        _require_non_empty_str(self.resource_usage_mode, "resource_usage_mode")
        if self.load_ratio is not None:
            _require_probability(self.load_ratio, "load_ratio")
        for field_name in (
            "cpu_gflops_fp64",
            "gpu_tflops_fp32",
            "gpu_tflops_fp16",
            "npu_tops_int8",
            "memory_gb",
            "storage_gb",
            "available_cpu_gflops_fp32",
            "used_cpu_gflops_fp32",
            "available_cpu_gflops_fp64",
            "used_cpu_gflops_fp64",
            "available_gpu_tflops_fp32",
            "used_gpu_tflops_fp32",
            "available_gpu_tflops_fp16",
            "used_gpu_tflops_fp16",
            "available_npu_tops_int8",
            "used_npu_tops_int8",
            "available_memory_gb",
            "used_memory_gb",
            "available_storage_gb",
            "used_storage_gb",
        ):
            _require_non_negative_number(getattr(self, field_name), field_name)


@dataclass(frozen=True)
class TaskRequest:
    """Canonical compute task request consumed by the compute module."""

    task_id: str
    source_id: str
    submit_time: float
    compute_demand: float
    data_size: float
    deadline: float | None = None
    flow_id: str | None = None
    priority: int = 0
    cpu_ops: float = 0.0
    fp32_ops: float = 0.0
    fp16_ops: float = 0.0
    int8_ops: float = 0.0
    memory_gb: float = 0.0
    input_data_mb: float = 0.0
    output_data_mb: float = 0.0

    def __post_init__(self) -> None:
        _require_non_empty_str(self.task_id, "task_id")
        _require_non_empty_str(self.source_id, "source_id")
        _require_finite_number(self.submit_time, "submit_time")
        _require_non_negative_number(self.compute_demand, "compute_demand")
        _require_non_negative_number(self.data_size, "data_size")
        if self.deadline is not None:
            _require_finite_number(self.deadline, "deadline")
        if self.flow_id is not None:
            _require_non_empty_str(self.flow_id, "flow_id")
        _require_int(self.priority, "priority")
        for field_name in (
            "cpu_ops",
            "fp32_ops",
            "fp16_ops",
            "int8_ops",
            "memory_gb",
            "input_data_mb",
            "output_data_mb",
        ):
            _require_non_negative_number(getattr(self, field_name), field_name)


@dataclass(frozen=True)
class TaskState:
    """Canonical task state output by the compute module."""

    task_id: str
    node_id: str
    sim_time: float
    progress: float
    status: str
    flow_id: str | None = None

    def __post_init__(self) -> None:
        _require_non_empty_str(self.task_id, "task_id")
        _require_non_empty_str(self.node_id, "node_id")
        _require_finite_number(self.sim_time, "sim_time")
        _require_non_negative_number(self.progress, "progress")
        _require_non_empty_str(self.status, "status")
        if self.flow_id is not None:
            _require_non_empty_str(self.flow_id, "flow_id")


@dataclass(frozen=True)
class MetricRecord:
    """Canonical metric sample generated by the metrics module."""

    metric_name: str
    sim_time: float
    entity_id: str
    value: float | str | bool
    tags: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        _require_non_empty_str(self.metric_name, "metric_name")
        _require_finite_number(self.sim_time, "sim_time")
        _require_non_empty_str(self.entity_id, "entity_id")
        normalized_tags = tuple(sorted((str(key), str(value)) for key, value in self.tags))
        object.__setattr__(self, "tags", normalized_tags)


@dataclass(frozen=True)
class RuntimeConfigState:
    """Canonical runtime config snapshot shared with the frontend."""

    mode: RuntimeMode | str
    speed_factor: float
    seed: int
    duration: float
    status: RuntimeStatus | str = RuntimeStatus.STOPPED
    config_version: int = 0

    def __post_init__(self) -> None:
        if not isinstance(self.mode, RuntimeMode):
            object.__setattr__(self, "mode", RuntimeMode(str(self.mode)))
        if not isinstance(self.status, RuntimeStatus):
            object.__setattr__(self, "status", RuntimeStatus(str(self.status)))
        _require_positive_number(self.speed_factor, "speed_factor")
        _require_non_negative_int(self.seed, "seed")
        _require_positive_number(self.duration, "duration")
        _require_non_negative_int(self.config_version, "config_version")


@dataclass(frozen=True)
class WorldSnapshot:
    """Canonical observation-plane snapshot shared by backend and frontend."""

    timestamp: float
    reducer_version: int
    last_sim_time: float
    event_count: int
    satellites: tuple[SatelliteState, ...] = ()
    ground_users: tuple[GroundUserState, ...] = ()
    channels: tuple[ChannelState, ...] = ()
    links: tuple[LinkState, ...] = ()
    routes: tuple[RouteState, ...] = ()
    flows: tuple[FlowState, ...] = ()
    transport: tuple[TransportState, ...] = ()
    applications: tuple[ApplicationState, ...] = ()
    compute_nodes: tuple[ComputeNodeState, ...] = ()
    active_tasks: tuple[TaskState, ...] = ()
    metrics: tuple[MetricRecord, ...] = ()
    runtime: RuntimeConfigState | None = None
    active_route_id: str | None = None

    def __post_init__(self) -> None:
        _require_finite_number(self.timestamp, "timestamp")
        _require_non_negative_int(self.reducer_version, "reducer_version")
        _require_finite_number(self.last_sim_time, "last_sim_time")
        _require_non_negative_int(self.event_count, "event_count")
        object.__setattr__(
            self,
            "satellites",
            tuple(sorted(self.satellites, key=lambda item: item.satellite_id)),
        )
        object.__setattr__(
            self,
            "ground_users",
            tuple(sorted(self.ground_users, key=lambda item: item.user_id)),
        )
        object.__setattr__(
            self,
            "channels",
            tuple(sorted(self.channels, key=lambda item: item.channel_id)),
        )
        object.__setattr__(
            self,
            "links",
            tuple(sorted(self.links, key=lambda item: item.link_id)),
        )
        object.__setattr__(
            self,
            "routes",
            tuple(sorted(self.routes, key=lambda item: item.route_id)),
        )
        object.__setattr__(
            self,
            "flows",
            tuple(sorted(self.flows, key=lambda item: item.flow_id)),
        )
        object.__setattr__(
            self,
            "transport",
            tuple(sorted(self.transport, key=lambda item: (item.flow_id, item.protocol))),
        )
        object.__setattr__(
            self,
            "applications",
            tuple(sorted(self.applications, key=lambda item: (item.flow_id, item.protocol))),
        )
        object.__setattr__(
            self,
            "compute_nodes",
            tuple(sorted(self.compute_nodes, key=lambda item: item.node_id)),
        )
        object.__setattr__(
            self,
            "active_tasks",
            tuple(sorted(self.active_tasks, key=lambda item: item.task_id)),
        )
        object.__setattr__(
            self,
            "metrics",
            tuple(
                sorted(
                    self.metrics,
                    key=lambda item: (item.sim_time, item.metric_name, item.entity_id, item.tags),
                )
            ),
        )
        if self.runtime is not None and not isinstance(self.runtime, RuntimeConfigState):
            raise TypeError("runtime must be RuntimeConfigState or None")
        if self.active_route_id is not None:
            _require_non_empty_str(self.active_route_id, "active_route_id")

    def to_dict(self) -> dict[str, Any]:
        """Return a deterministic JSON-compatible dictionary."""

        return _to_jsonable(self)

    def to_json(self) -> str:
        """Return a deterministic JSON representation."""

        return dumps(self.to_dict(), ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _require_non_empty_str(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value:
        raise TypeError(f"{field_name} must be a non-empty str")


def _require_finite_number(value: Any, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field_name} must be an int or float")
    if not isfinite(value):
        raise ValueError(f"{field_name} must be finite")


def _require_non_negative_number(value: Any, field_name: str) -> None:
    _require_finite_number(value, field_name)
    if value < 0:
        raise ValueError(f"{field_name} must be non-negative")


def _require_positive_number(value: Any, field_name: str) -> None:
    _require_finite_number(value, field_name)
    if value <= 0:
        raise ValueError(f"{field_name} must be positive")


def _require_probability(value: Any, field_name: str) -> None:
    _require_finite_number(value, field_name)
    if value < 0 or value > 1:
        raise ValueError(f"{field_name} must be in [0, 1]")


def _require_bool(value: Any, field_name: str) -> None:
    if not isinstance(value, bool):
        raise TypeError(f"{field_name} must be a bool")


def _require_int(value: Any, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field_name} must be an int")


def _require_non_negative_int(value: Any, field_name: str) -> None:
    _require_int(value, field_name)
    if value < 0:
        raise ValueError(f"{field_name} must be non-negative")


def _require_vector3(value: Any, field_name: str) -> None:
    if not isinstance(value, tuple) or len(value) != 3:
        raise TypeError(f"{field_name} must be a 3-tuple")
    for item in value:
        _require_finite_number(item, field_name)


def _normalize_str_tuple(
    values: tuple[str, ...],
    field_name: str,
    *,
    sort: bool = True,
) -> tuple[str, ...]:
    if not isinstance(values, tuple):
        raise TypeError(f"{field_name} must be a tuple")
    normalized = tuple(str(value) for value in values)
    if any(not value for value in normalized):
        raise ValueError(f"{field_name} must not contain empty values")
    return tuple(sorted(normalized)) if sort else normalized


def _to_jsonable(value: Any) -> Any:
    if isinstance(value, StrEnum):
        return value.value
    if is_dataclass(value) and not isinstance(value, type):
        return {field.name: _to_jsonable(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, tuple):
        return [_to_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_to_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {
            str(key): _to_jsonable(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    return value
