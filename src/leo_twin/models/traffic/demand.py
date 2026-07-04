"""Deterministic traffic demand model v1."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from math import isfinite
from typing import Any

from leo_twin.schema import EventType, FlowRequest, SimEvent, TaskRequest


class TrafficClass(StrEnum):
    """Supported flow-level traffic classes."""

    DATA_TRANSFER = "DATA_TRANSFER"
    TELEMETRY = "TELEMETRY"
    BULK_DOWNLINK = "BULK_DOWNLINK"
    COMPUTE_SERVICE = "COMPUTE_SERVICE"


class TrafficDestinationType(StrEnum):
    """Destination category carried as traffic model metadata."""

    GROUND_ENDPOINT = "GROUND_ENDPOINT"
    SATELLITE = "SATELLITE"
    COMPUTE_NODE = "COMPUTE_NODE"
    SERVICE_ENDPOINT = "SERVICE_ENDPOINT"


@dataclass(frozen=True)
class TrafficDemandProfile:
    """Configuration for one deterministic traffic demand sequence."""

    traffic_class: TrafficClass | str
    source_ids: tuple[str, ...]
    destination_ids: tuple[str, ...]
    request_count: int
    arrival_interval: float
    input_data_size: float
    output_data_size: float = 0.0
    priority: int = 0
    destination_type: TrafficDestinationType | str = TrafficDestinationType.GROUND_ENDPOINT
    start_time: float = 0.0
    compute_demand: float = 1.0
    cpu_ops: float = 0.0
    fp32_ops: float = 0.0
    fp16_ops: float = 0.0
    int8_ops: float = 0.0
    memory_gb: float = 0.0
    input_data_mb: float = 0.0
    output_data_mb: float = 0.0
    application_id: str | None = None
    id_prefix: str = "traffic"
    output_destination_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.traffic_class, TrafficClass):
            object.__setattr__(self, "traffic_class", TrafficClass(str(self.traffic_class)))
        if not isinstance(self.destination_type, TrafficDestinationType):
            object.__setattr__(
                self,
                "destination_type",
                TrafficDestinationType(str(self.destination_type)),
            )
        object.__setattr__(
            self,
            "source_ids",
            _normalize_non_empty_str_tuple(self.source_ids, "source_ids"),
        )
        object.__setattr__(
            self,
            "destination_ids",
            _normalize_non_empty_str_tuple(self.destination_ids, "destination_ids"),
        )
        object.__setattr__(
            self,
            "output_destination_ids",
            _normalize_str_tuple(self.output_destination_ids, "output_destination_ids"),
        )
        _require_non_negative_int(self.request_count, "request_count")
        _require_positive_number(self.arrival_interval, "arrival_interval")
        _require_non_negative_number(self.input_data_size, "input_data_size")
        _require_non_negative_number(self.output_data_size, "output_data_size")
        _require_int(self.priority, "priority")
        _require_non_negative_number(self.start_time, "start_time")
        _require_non_negative_number(self.compute_demand, "compute_demand")
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
        if self.application_id is not None:
            _require_non_empty_str(self.application_id, "application_id")
        _require_non_empty_str(self.id_prefix, "id_prefix")


@dataclass(frozen=True)
class ComputeOutputFlowMetadata:
    """Deferred output flow description for a compute-service demand."""

    flow_id: str
    task_id: str
    input_flow_id: str
    source_id: str
    target_id: str
    data_size: float
    priority: int
    traffic_class: TrafficClass = TrafficClass.COMPUTE_SERVICE
    destination_type: TrafficDestinationType = TrafficDestinationType.GROUND_ENDPOINT
    application_id: str | None = None

    def __post_init__(self) -> None:
        _require_non_empty_str(self.flow_id, "flow_id")
        _require_non_empty_str(self.task_id, "task_id")
        _require_non_empty_str(self.input_flow_id, "input_flow_id")
        _require_non_empty_str(self.source_id, "source_id")
        _require_non_empty_str(self.target_id, "target_id")
        _require_non_negative_number(self.data_size, "data_size")
        _require_int(self.priority, "priority")
        if not isinstance(self.traffic_class, TrafficClass):
            object.__setattr__(self, "traffic_class", TrafficClass(str(self.traffic_class)))
        if not isinstance(self.destination_type, TrafficDestinationType):
            object.__setattr__(
                self,
                "destination_type",
                TrafficDestinationType(str(self.destination_type)),
            )
        if self.application_id is not None:
            _require_non_empty_str(self.application_id, "application_id")

    def to_flow_request(self) -> FlowRequest:
        """Build the future output FlowRequest without scheduling it."""

        return FlowRequest(
            flow_id=self.flow_id,
            source_id=self.source_id,
            target_id=self.target_id,
            demand_capacity=self.data_size,
            application_id=self.application_id,
            priority=self.priority,
        )


@dataclass(frozen=True)
class TrafficDemandRecord:
    """One generated arrival and its correlated runtime requests."""

    arrival_time: float
    traffic_class: TrafficClass
    destination_type: TrafficDestinationType
    input_data_size: float
    output_data_size: float
    input_flow: FlowRequest
    task: TaskRequest | None = None
    output_flow: ComputeOutputFlowMetadata | None = None

    def __post_init__(self) -> None:
        _require_non_negative_number(self.arrival_time, "arrival_time")
        if not isinstance(self.traffic_class, TrafficClass):
            object.__setattr__(self, "traffic_class", TrafficClass(str(self.traffic_class)))
        if not isinstance(self.destination_type, TrafficDestinationType):
            object.__setattr__(
                self,
                "destination_type",
                TrafficDestinationType(str(self.destination_type)),
            )
        _require_non_negative_number(self.input_data_size, "input_data_size")
        _require_non_negative_number(self.output_data_size, "output_data_size")
        if not isinstance(self.input_flow, FlowRequest):
            raise TypeError("input_flow must be a FlowRequest")
        if self.task is not None and not isinstance(self.task, TaskRequest):
            raise TypeError("task must be a TaskRequest or None")
        if self.output_flow is not None and not isinstance(
            self.output_flow,
            ComputeOutputFlowMetadata,
        ):
            raise TypeError("output_flow must be ComputeOutputFlowMetadata or None")


@dataclass(frozen=True)
class TrafficDemandBatch:
    """Generated deterministic traffic demand records."""

    records: tuple[TrafficDemandRecord, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.records, tuple):
            raise TypeError("records must be a tuple")
        for record in self.records:
            if not isinstance(record, TrafficDemandRecord):
                raise TypeError("records must contain TrafficDemandRecord values")

    @property
    def flow_requests(self) -> tuple[FlowRequest, ...]:
        """Input FlowRequest values generated for network ingestion."""

        return tuple(record.input_flow for record in self.records)

    @property
    def task_requests(self) -> tuple[TaskRequest, ...]:
        """TaskRequest values generated for compute-service demands."""

        return tuple(record.task for record in self.records if record.task is not None)

    @property
    def output_flow_metadata(self) -> tuple[ComputeOutputFlowMetadata, ...]:
        """Deferred output-flow metadata for compute-service demands."""

        return tuple(
            record.output_flow
            for record in self.records
            if record.output_flow is not None
        )

    def flow_arrival_events(
        self,
        *,
        event_id_prefix: str = "traffic-flow",
        source: str = "traffic",
        target: str = "network",
    ) -> tuple[SimEvent, ...]:
        """Return deterministic FLOW_ARRIVAL events without scheduling them."""

        return tuple(
            SimEvent(
                event_id=f"{event_id_prefix}-{index:05d}",
                sim_time=record.arrival_time,
                priority=record.input_flow.priority,
                source=source,
                target=target,
                event_type=EventType.FLOW_ARRIVAL.value,
                payload=record.input_flow,
            )
            for index, record in enumerate(self.records)
        )

    def task_arrival_events(
        self,
        *,
        event_id_prefix: str = "traffic-task",
        source: str = "traffic",
        target: str = "compute",
    ) -> tuple[SimEvent, ...]:
        """Return deterministic TASK_ARRIVAL events without scheduling them."""

        task_items = tuple(
            (record.arrival_time, record.task)
            for record in self.records
            if record.task is not None
        )
        return tuple(
            SimEvent(
                event_id=f"{event_id_prefix}-{index:05d}",
                sim_time=arrival_time,
                priority=task.priority,
                source=source,
                target=target,
                event_type=EventType.TASK_ARRIVAL.value,
                payload=task,
            )
            for index, (arrival_time, task) in enumerate(task_items)
        )


@dataclass(frozen=True)
class TrafficDemandConfig:
    """Traffic demand model configuration."""

    profiles: tuple[TrafficDemandProfile, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.profiles, tuple):
            raise TypeError("profiles must be a tuple")
        for profile in self.profiles:
            if not isinstance(profile, TrafficDemandProfile):
                raise TypeError("profiles must contain TrafficDemandProfile values")


class TrafficDemandModel:
    """Generate flow-level traffic demands from deterministic profiles."""

    def __init__(self, config: TrafficDemandConfig) -> None:
        if not isinstance(config, TrafficDemandConfig):
            raise TypeError("config must be TrafficDemandConfig")
        self._config = config

    @property
    def config(self) -> TrafficDemandConfig:
        return self._config

    def generate(self) -> TrafficDemandBatch:
        """Generate all configured traffic demand records deterministically."""

        records: list[TrafficDemandRecord] = []
        for profile_index, profile in enumerate(self._config.profiles):
            records.extend(_generate_profile_records(profile_index, profile))
        return TrafficDemandBatch(records=tuple(records))


def generate_traffic_demand(
    profiles: tuple[TrafficDemandProfile, ...],
) -> TrafficDemandBatch:
    """Convenience wrapper for one-shot deterministic traffic generation."""

    return TrafficDemandModel(TrafficDemandConfig(profiles=profiles)).generate()


def _generate_profile_records(
    profile_index: int,
    profile: TrafficDemandProfile,
) -> tuple[TrafficDemandRecord, ...]:
    records: list[TrafficDemandRecord] = []
    application_id = profile.application_id or profile.traffic_class.value
    for request_index in range(profile.request_count):
        source_id = profile.source_ids[request_index % len(profile.source_ids)]
        target_id = profile.destination_ids[request_index % len(profile.destination_ids)]
        base_id = (
            f"{profile.id_prefix}-{profile_index:02d}-"
            f"{profile.traffic_class.value.lower()}-{request_index:05d}"
        )
        arrival_time = profile.start_time + request_index * profile.arrival_interval
        flow_id = (
            f"{base_id}-input"
            if profile.traffic_class == TrafficClass.COMPUTE_SERVICE
            else base_id
        )
        input_flow = FlowRequest(
            flow_id=flow_id,
            source_id=source_id,
            target_id=target_id,
            demand_capacity=profile.input_data_size,
            application_id=application_id,
            priority=profile.priority,
        )
        if profile.traffic_class == TrafficClass.COMPUTE_SERVICE:
            records.append(
                _compute_service_record(
                    profile=profile,
                    base_id=base_id,
                    arrival_time=arrival_time,
                    input_flow=input_flow,
                    request_index=request_index,
                    application_id=application_id,
                )
            )
        else:
            records.append(
                TrafficDemandRecord(
                    arrival_time=arrival_time,
                    traffic_class=profile.traffic_class,
                    destination_type=profile.destination_type,
                    input_data_size=profile.input_data_size,
                    output_data_size=profile.output_data_size,
                    input_flow=input_flow,
                )
            )
    return tuple(records)


def _compute_service_record(
    *,
    profile: TrafficDemandProfile,
    base_id: str,
    arrival_time: float,
    input_flow: FlowRequest,
    request_index: int,
    application_id: str,
) -> TrafficDemandRecord:
    task = TaskRequest(
        task_id=f"{base_id}-task",
        source_id=input_flow.source_id,
        submit_time=arrival_time,
        compute_demand=profile.compute_demand,
        data_size=profile.input_data_size,
        flow_id=input_flow.flow_id,
        priority=profile.priority,
        cpu_ops=profile.cpu_ops,
        fp32_ops=profile.fp32_ops,
        fp16_ops=profile.fp16_ops,
        int8_ops=profile.int8_ops,
        memory_gb=profile.memory_gb,
        input_data_mb=profile.input_data_mb,
        output_data_mb=profile.output_data_mb,
    )
    output_target_ids = profile.output_destination_ids or profile.source_ids
    output_target_id = output_target_ids[request_index % len(output_target_ids)]
    output_flow = ComputeOutputFlowMetadata(
        flow_id=f"{base_id}-output",
        task_id=task.task_id,
        input_flow_id=input_flow.flow_id,
        source_id=input_flow.target_id,
        target_id=output_target_id,
        data_size=profile.output_data_size,
        priority=profile.priority,
        application_id=application_id,
    )
    return TrafficDemandRecord(
        arrival_time=arrival_time,
        traffic_class=profile.traffic_class,
        destination_type=profile.destination_type,
        input_data_size=profile.input_data_size,
        output_data_size=profile.output_data_size,
        input_flow=input_flow,
        task=task,
        output_flow=output_flow,
    )


def _normalize_non_empty_str_tuple(values: tuple[str, ...], field_name: str) -> tuple[str, ...]:
    normalized = _normalize_str_tuple(values, field_name)
    if not normalized:
        raise ValueError(f"{field_name} must not be empty")
    return normalized


def _normalize_str_tuple(values: tuple[str, ...], field_name: str) -> tuple[str, ...]:
    if not isinstance(values, tuple):
        raise TypeError(f"{field_name} must be a tuple")
    normalized = tuple(str(value) for value in values)
    if any(not value for value in normalized):
        raise ValueError(f"{field_name} must not contain empty values")
    return normalized


def _require_non_empty_str(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value:
        raise TypeError(f"{field_name} must be a non-empty str")


def _require_int(value: Any, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field_name} must be an int")


def _require_non_negative_int(value: Any, field_name: str) -> None:
    _require_int(value, field_name)
    if value < 0:
        raise ValueError(f"{field_name} must be non-negative")


def _require_positive_number(value: Any, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field_name} must be an int or float")
    if not isfinite(float(value)) or value <= 0.0:
        raise ValueError(f"{field_name} must be finite and positive")


def _require_non_negative_number(value: Any, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field_name} must be an int or float")
    if not isfinite(float(value)) or value < 0.0:
        raise ValueError(f"{field_name} must be finite and non-negative")


__all__ = [
    "ComputeOutputFlowMetadata",
    "TrafficClass",
    "TrafficDemandBatch",
    "TrafficDemandConfig",
    "TrafficDemandModel",
    "TrafficDemandProfile",
    "TrafficDemandRecord",
    "TrafficDestinationType",
    "generate_traffic_demand",
]
