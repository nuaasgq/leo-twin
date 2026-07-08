"""Deterministic traffic demand model v1."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from math import cos, isfinite, pi
from random import Random
from typing import Any

from leo_twin.schema import EventType, FlowRequest, SimEvent, TaskRequest


class TrafficClass(StrEnum):
    """Supported flow-level traffic classes."""

    DATA_TRANSFER = "DATA_TRANSFER"
    TELEMETRY = "TELEMETRY"
    BULK_DOWNLINK = "BULK_DOWNLINK"
    COMPUTE_SERVICE = "COMPUTE_SERVICE"
    EMERGENCY = "EMERGENCY"


class TrafficDestinationType(StrEnum):
    """Destination category carried as traffic model metadata."""

    GROUND_ENDPOINT = "GROUND_ENDPOINT"
    SATELLITE = "SATELLITE"
    COMPUTE_NODE = "COMPUTE_NODE"
    SERVICE_ENDPOINT = "SERVICE_ENDPOINT"


class TrafficArrivalProfile(StrEnum):
    """Deterministic arrival and endpoint-selection profile."""

    PERIODIC = "PERIODIC"
    BURST = "BURST"
    DIURNAL = "DIURNAL"
    REGION_WEIGHTED = "REGION_WEIGHTED"


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
    arrival_profile: TrafficArrivalProfile | str = TrafficArrivalProfile.PERIODIC
    seed: int = 0
    burst_size: int = 1
    burst_spacing: float = 0.0
    diurnal_period: float = 86_400.0
    diurnal_peak_time: float = 0.0
    diurnal_amplitude: float = 0.0
    source_region_weights: tuple[float, ...] = ()
    destination_region_weights: tuple[float, ...] = ()

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
        if not isinstance(self.arrival_profile, TrafficArrivalProfile):
            object.__setattr__(
                self,
                "arrival_profile",
                TrafficArrivalProfile(str(self.arrival_profile)),
            )
        _require_non_negative_int(self.request_count, "request_count")
        _require_positive_number(self.arrival_interval, "arrival_interval")
        _require_non_negative_number(self.input_data_size, "input_data_size")
        _require_non_negative_number(self.output_data_size, "output_data_size")
        _require_int(self.priority, "priority")
        _require_non_negative_number(self.start_time, "start_time")
        _require_non_negative_number(self.compute_demand, "compute_demand")
        _require_int(self.seed, "seed")
        _require_positive_int(self.burst_size, "burst_size")
        _require_non_negative_number(self.burst_spacing, "burst_spacing")
        _require_positive_number(self.diurnal_period, "diurnal_period")
        _require_non_negative_number(self.diurnal_peak_time, "diurnal_peak_time")
        _require_probability(self.diurnal_amplitude, "diurnal_amplitude")
        object.__setattr__(
            self,
            "source_region_weights",
            _normalize_weight_tuple(
                self.source_region_weights,
                "source_region_weights",
                expected_length=len(self.source_ids),
            ),
        )
        object.__setattr__(
            self,
            "destination_region_weights",
            _normalize_weight_tuple(
                self.destination_region_weights,
                "destination_region_weights",
                expected_length=len(self.destination_ids),
            ),
        )
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

    def service_mix_summary(self) -> dict[str, object]:
        """Return deterministic aggregate and per-user service state."""

        counts = {
            traffic_class.value: sum(
                1 for record in self.records if record.traffic_class == traffic_class
            )
            for traffic_class in TrafficClass
        }
        active_classes = tuple(
            traffic_class.value
            for traffic_class in TrafficClass
            if counts[traffic_class.value] > 0
        )
        return {
            "version": "v2",
            "summary_id": "leo_twin.traffic_service_mix_summary.v2",
            "generated_request_count": len(self.records),
            "generated_request_counts": counts,
            "active_service_classes": active_classes,
            "schedule_ordering": "ARRIVAL_TIME_PRIORITY_CLASS_FLOW",
            "simultaneous_arrival_policy": (
                "HIGHER_PRIORITY_FIRST_THEN_CLASS_AND_FLOW_ID"
            ),
            "per_user_active_service_state": self.per_user_active_service_state(),
        }

    def traffic_demand_explanation(self) -> dict[str, object]:
        """Return deterministic product-facing demand semantics."""

        traffic_class_rows = tuple(
            _traffic_class_explanation_row(traffic_class, self.records)
            for traffic_class in TrafficClass
        )
        active_rows = tuple(
            row for row in traffic_class_rows if row["request_count"] > 0
        )
        arrival_times = tuple(record.arrival_time for record in self.records)
        priorities = tuple(record.input_flow.priority for record in self.records)
        compute_service_request_count = sum(
            1
            for record in self.records
            if record.traffic_class == TrafficClass.COMPUTE_SERVICE
        )
        total_input_data_mb = sum(record.input_data_size for record in self.records)
        total_output_data_mb = sum(record.output_data_size for record in self.records)
        return {
            "version": "v1",
            "explanation_id": "leo_twin.traffic_demand_explanation.v1",
            "source": "TrafficDemandBatch.records",
            "request_count": len(self.records),
            "input_flow_count": len(self.flow_requests),
            "task_request_count": len(self.task_requests),
            "output_flow_count": len(self.output_flow_metadata),
            "communication_only_request_count": (
                len(self.records) - compute_service_request_count
            ),
            "compute_service_request_count": compute_service_request_count,
            "active_traffic_classes": tuple(
                row["traffic_class"] for row in active_rows
            ),
            "traffic_class_rows": traffic_class_rows,
            "schedule_ordering": "ARRIVAL_TIME_PRIORITY_CLASS_FLOW",
            "simultaneous_arrival_policy": (
                "HIGHER_PRIORITY_FIRST_THEN_CLASS_AND_FLOW_ID"
            ),
            "arrival_window": {
                "first_arrival_time": min(arrival_times) if arrival_times else None,
                "last_arrival_time": max(arrival_times) if arrival_times else None,
                "duration_seconds": (
                    max(arrival_times) - min(arrival_times)
                    if len(arrival_times) >= 2
                    else 0.0
                ),
            },
            "priority_summary": {
                "min_priority": min(priorities) if priorities else None,
                "max_priority": max(priorities) if priorities else None,
                "unique_priorities": tuple(sorted(set(priorities))),
            },
            "data_volume": {
                "total_input_data_mb": total_input_data_mb,
                "total_output_data_mb": total_output_data_mb,
                "total_data_mb": total_input_data_mb + total_output_data_mb,
            },
            "correlation_summary": {
                "all_compute_services_have_task": (
                    len(self.task_requests) == compute_service_request_count
                ),
                "all_compute_services_have_output_flow": (
                    len(self.output_flow_metadata) == compute_service_request_count
                ),
                "packet_level_simulation": False,
                "frontend_inference_required": False,
            },
            "per_user_active_service_state": self.per_user_active_service_state(),
            "model_assumptions": (
                "Traffic demand explanation summarizes generated flow-level requests only.",
                (
                    "Compute-service rows carry correlated input flow, task, "
                    "and deferred output-flow metadata."
                ),
                (
                    "Packet-level traffic, stochastic retries, and external "
                    "simulators are outside this model."
                ),
            ),
        }

    def runtime_request_timeline(
        self,
        *,
        sim_time: float,
        lookback_window_s: float = 60.0,
        lookahead_window_s: float = 60.0,
        item_limit: int = 64,
    ) -> dict[str, object]:
        """Return a deterministic request timeline around current sim time."""

        _require_non_negative_number(sim_time, "sim_time")
        _require_non_negative_number(lookback_window_s, "lookback_window_s")
        _require_non_negative_number(lookahead_window_s, "lookahead_window_s")
        _require_positive_int(item_limit, "item_limit")
        current = float(sim_time)
        window_start = max(0.0, current - float(lookback_window_s))
        window_end = current + float(lookahead_window_s)
        ordered_records = tuple(
            sorted(
                self.records,
                key=lambda record: (
                    record.arrival_time,
                    -record.input_flow.priority,
                    _service_id_from_record(record),
                ),
            )
        )
        state_counts = {
            "PAST": 0,
            "RECENTLY_ARRIVED": 0,
            "PENDING": 0,
        }
        window_records: list[TrafficDemandRecord] = []
        for record in ordered_records:
            state = _request_timeline_state(
                record,
                sim_time=current,
                window_start=window_start,
            )
            state_counts[state] += 1
            if window_start <= record.arrival_time <= window_end:
                window_records.append(record)
        limited_records = tuple(window_records[:item_limit])
        return {
            "version": "v1",
            "summary_id": "leo_twin.traffic_request_timeline.v1",
            "source": "TrafficDemandBatch.records",
            "metric_model": "FLOW_LEVEL_REQUEST_SCHEDULE",
            "packet_level_simulation": False,
            "frontend_inference_required": False,
            "current_sim_time": current,
            "request_count": len(ordered_records),
            "state_counts": state_counts,
            "recent_request_count": state_counts["RECENTLY_ARRIVED"],
            "pending_request_count": state_counts["PENDING"],
            "past_request_count": state_counts["PAST"],
            "window": {
                "lookback_window_s": float(lookback_window_s),
                "lookahead_window_s": float(lookahead_window_s),
                "window_start_s": window_start,
                "window_end_s": window_end,
            },
            "window_request_count": len(window_records),
            "item_limit": item_limit,
            "item_count": len(limited_records),
            "hidden_window_request_count": max(
                0,
                len(window_records) - len(limited_records),
            ),
            "items": tuple(
                _traffic_request_timeline_item(record, current, window_start)
                for record in limited_records
            ),
            "model_assumptions": (
                "Timeline states are derived from configured flow-level arrival times.",
                "RECENTLY_ARRIVED means the request arrived within the lookback window, not packet-level completion.",
                "PENDING means scheduled after current sim time; no stochastic retry model is used.",
            ),
        }

    def per_user_active_service_state(self) -> tuple[dict[str, object], ...]:
        """Return deterministic per-source service state rows."""

        by_user: dict[str, list[TrafficDemandRecord]] = {}
        for record in self.records:
            by_user.setdefault(record.input_flow.source_id, []).append(record)
        return tuple(
            _per_user_active_service_state(user_id, tuple(by_user[user_id]))
            for user_id in sorted(by_user)
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


@dataclass(frozen=True)
class TrafficServiceMixItem:
    """One weighted business class in a deterministic service mix."""

    traffic_class: TrafficClass | str
    weight: float
    source_ids: tuple[str, ...]
    destination_ids: tuple[str, ...]
    input_data_size: float
    output_data_size: float = 0.0
    priority: int = 0
    destination_type: TrafficDestinationType | str | None = None
    compute_demand: float = 1.0
    cpu_ops: float = 0.0
    fp32_ops: float = 0.0
    fp16_ops: float = 0.0
    int8_ops: float = 0.0
    memory_gb: float = 0.0
    input_data_mb: float = 0.0
    output_data_mb: float = 0.0
    application_id: str | None = None
    output_destination_ids: tuple[str, ...] = ()
    arrival_profile: TrafficArrivalProfile | str = TrafficArrivalProfile.PERIODIC
    seed: int = 0
    burst_size: int = 1
    burst_spacing: float = 0.0
    diurnal_period: float = 86_400.0
    diurnal_peak_time: float = 0.0
    diurnal_amplitude: float = 0.0
    source_region_weights: tuple[float, ...] = ()
    destination_region_weights: tuple[float, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.traffic_class, TrafficClass):
            object.__setattr__(self, "traffic_class", TrafficClass(str(self.traffic_class)))
        destination_type = (
            _default_destination_type(self.traffic_class)
            if self.destination_type is None
            else self.destination_type
        )
        if not isinstance(destination_type, TrafficDestinationType):
            destination_type = TrafficDestinationType(str(destination_type))
        object.__setattr__(self, "destination_type", destination_type)
        if not isinstance(self.arrival_profile, TrafficArrivalProfile):
            object.__setattr__(
                self,
                "arrival_profile",
                TrafficArrivalProfile(str(self.arrival_profile)),
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
        _require_non_negative_number(self.weight, "weight")
        _require_non_negative_number(self.input_data_size, "input_data_size")
        _require_non_negative_number(self.output_data_size, "output_data_size")
        _require_int(self.priority, "priority")
        _require_non_negative_number(self.compute_demand, "compute_demand")
        _require_int(self.seed, "seed")
        _require_positive_int(self.burst_size, "burst_size")
        _require_non_negative_number(self.burst_spacing, "burst_spacing")
        _require_positive_number(self.diurnal_period, "diurnal_period")
        _require_non_negative_number(self.diurnal_peak_time, "diurnal_peak_time")
        _require_probability(self.diurnal_amplitude, "diurnal_amplitude")
        object.__setattr__(
            self,
            "source_region_weights",
            _normalize_weight_tuple(
                self.source_region_weights,
                "source_region_weights",
                expected_length=len(self.source_ids),
            ),
        )
        object.__setattr__(
            self,
            "destination_region_weights",
            _normalize_weight_tuple(
                self.destination_region_weights,
                "destination_region_weights",
                expected_length=len(self.destination_ids),
            ),
        )
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


@dataclass(frozen=True)
class TrafficServiceMixConfig:
    """Weighted service-mix plan that expands into demand profiles."""

    items: tuple[TrafficServiceMixItem, ...]
    total_request_count: int
    arrival_interval: float
    start_time: float = 0.0
    id_prefix: str = "service-mix"

    def __post_init__(self) -> None:
        if not isinstance(self.items, tuple):
            raise TypeError("items must be a tuple")
        if not self.items:
            raise ValueError("items must not be empty")
        for item in self.items:
            if not isinstance(item, TrafficServiceMixItem):
                raise TypeError("items must contain TrafficServiceMixItem values")
        _require_non_negative_int(self.total_request_count, "total_request_count")
        _require_positive_number(self.arrival_interval, "arrival_interval")
        _require_non_negative_number(self.start_time, "start_time")
        _require_non_empty_str(self.id_prefix, "id_prefix")
        if sum(float(item.weight) for item in self.items) <= 0.0:
            raise ValueError("service mix must contain at least one positive weight")

    def to_demand_profiles(self) -> tuple[TrafficDemandProfile, ...]:
        """Expand weighted service-mix items into deterministic demand profiles."""

        request_counts = _allocate_weighted_counts(
            self.total_request_count,
            tuple(float(item.weight) for item in self.items),
        )
        return tuple(
            _service_mix_item_to_profile(
                item,
                request_count=request_count,
                arrival_interval=self.arrival_interval,
                start_time=self.start_time,
                id_prefix=f"{self.id_prefix}-{index:02d}",
            )
            for index, (item, request_count) in enumerate(zip(self.items, request_counts))
        )


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
        return TrafficDemandBatch(
            records=tuple(sorted(records, key=_traffic_record_sort_key))
        )


def generate_traffic_demand(
    profiles: tuple[TrafficDemandProfile, ...],
) -> TrafficDemandBatch:
    """Convenience wrapper for one-shot deterministic traffic generation."""

    return TrafficDemandModel(TrafficDemandConfig(profiles=profiles)).generate()


def generate_traffic_service_mix(config: TrafficServiceMixConfig) -> TrafficDemandBatch:
    """Generate a deterministic demand batch from a weighted service mix."""

    if not isinstance(config, TrafficServiceMixConfig):
        raise TypeError("config must be TrafficServiceMixConfig")
    return generate_traffic_demand(config.to_demand_profiles())


def _allocate_weighted_counts(
    total_count: int,
    weights: tuple[float, ...],
) -> tuple[int, ...]:
    if total_count == 0:
        return tuple(0 for _ in weights)
    total_weight = sum(weights)
    if total_weight <= 0.0:
        raise ValueError("weights must contain at least one positive value")
    exact_counts = tuple(total_count * weight / total_weight for weight in weights)
    base_counts = [int(exact_count) for exact_count in exact_counts]
    remaining = total_count - sum(base_counts)
    remainders = sorted(
        (
            (exact_counts[index] - base_counts[index], index)
            for index in range(len(weights))
        ),
        key=lambda item: (-item[0], item[1]),
    )
    for _, index in remainders[:remaining]:
        base_counts[index] += 1
    return tuple(base_counts)


def _service_mix_item_to_profile(
    item: TrafficServiceMixItem,
    *,
    request_count: int,
    arrival_interval: float,
    start_time: float,
    id_prefix: str,
) -> TrafficDemandProfile:
    return TrafficDemandProfile(
        traffic_class=item.traffic_class,
        source_ids=item.source_ids,
        destination_ids=item.destination_ids,
        request_count=request_count,
        arrival_interval=arrival_interval,
        input_data_size=item.input_data_size,
        output_data_size=item.output_data_size,
        priority=item.priority,
        destination_type=item.destination_type,
        start_time=start_time,
        compute_demand=item.compute_demand,
        cpu_ops=item.cpu_ops,
        fp32_ops=item.fp32_ops,
        fp16_ops=item.fp16_ops,
        int8_ops=item.int8_ops,
        memory_gb=item.memory_gb,
        input_data_mb=item.input_data_mb,
        output_data_mb=item.output_data_mb,
        application_id=item.application_id,
        id_prefix=id_prefix,
        output_destination_ids=item.output_destination_ids,
        arrival_profile=item.arrival_profile,
        seed=item.seed,
        burst_size=item.burst_size,
        burst_spacing=item.burst_spacing,
        diurnal_period=item.diurnal_period,
        diurnal_peak_time=item.diurnal_peak_time,
        diurnal_amplitude=item.diurnal_amplitude,
        source_region_weights=item.source_region_weights,
        destination_region_weights=item.destination_region_weights,
    )


def _default_destination_type(traffic_class: TrafficClass) -> TrafficDestinationType:
    if traffic_class == TrafficClass.COMPUTE_SERVICE:
        return TrafficDestinationType.COMPUTE_NODE
    if traffic_class == TrafficClass.BULK_DOWNLINK:
        return TrafficDestinationType.GROUND_ENDPOINT
    if traffic_class == TrafficClass.TELEMETRY:
        return TrafficDestinationType.SERVICE_ENDPOINT
    if traffic_class == TrafficClass.EMERGENCY:
        return TrafficDestinationType.SERVICE_ENDPOINT
    return TrafficDestinationType.GROUND_ENDPOINT


def _traffic_record_sort_key(
    record: TrafficDemandRecord,
) -> tuple[float, int, str, str]:
    return (
        float(record.arrival_time),
        -int(record.input_flow.priority),
        record.traffic_class.value,
        record.input_flow.flow_id,
    )


def _generate_profile_records(
    profile_index: int,
    profile: TrafficDemandProfile,
) -> tuple[TrafficDemandRecord, ...]:
    records: list[TrafficDemandRecord] = []
    application_id = profile.application_id or profile.traffic_class.value
    arrival_times = _arrival_times(profile)
    for request_index in range(profile.request_count):
        source_id = _select_profile_id(
            profile.source_ids,
            profile.source_region_weights,
            request_index=request_index,
            profile_index=profile_index,
            seed=profile.seed,
            salt=17,
        )
        target_id = _select_profile_id(
            profile.destination_ids,
            profile.destination_region_weights,
            request_index=request_index,
            profile_index=profile_index,
            seed=profile.seed,
            salt=31,
        )
        base_id = (
            f"{profile.id_prefix}-{profile_index:02d}-"
            f"{profile.traffic_class.value.lower()}-{request_index:05d}"
        )
        arrival_time = arrival_times[request_index]
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


def _arrival_times(profile: TrafficDemandProfile) -> tuple[float, ...]:
    if profile.request_count == 0:
        return ()
    if profile.arrival_profile == TrafficArrivalProfile.BURST:
        return tuple(
            profile.start_time
            + (index // profile.burst_size) * profile.arrival_interval
            + (index % profile.burst_size) * profile.burst_spacing
            for index in range(profile.request_count)
        )
    if profile.arrival_profile == TrafficArrivalProfile.DIURNAL:
        return _diurnal_arrival_times(profile)
    return tuple(
        profile.start_time + index * profile.arrival_interval
        for index in range(profile.request_count)
    )


def _diurnal_arrival_times(profile: TrafficDemandProfile) -> tuple[float, ...]:
    times = [profile.start_time]
    current_time = profile.start_time
    for _ in range(1, profile.request_count):
        phase = 2.0 * pi * ((current_time - profile.diurnal_peak_time) / profile.diurnal_period)
        peak_factor = (1.0 + cos(phase)) / 2.0
        interval = profile.arrival_interval * (
            1.0 - profile.diurnal_amplitude * peak_factor
        )
        current_time += interval
        times.append(current_time)
    return tuple(times)


def _select_profile_id(
    ids: tuple[str, ...],
    weights: tuple[float, ...],
    *,
    request_index: int,
    profile_index: int,
    seed: int,
    salt: int,
) -> str:
    if not weights:
        return ids[request_index % len(ids)]
    index = _weighted_index(
        weights,
        seed=seed,
        profile_index=profile_index,
        request_index=request_index,
        salt=salt,
    )
    return ids[index]


def _weighted_index(
    weights: tuple[float, ...],
    *,
    seed: int,
    profile_index: int,
    request_index: int,
    salt: int,
) -> int:
    total = sum(weights)
    rng = Random(seed * 1_000_003 + profile_index * 10_007 + request_index * 101 + salt)
    draw = rng.random() * total
    cursor = 0.0
    for index, weight in enumerate(weights):
        cursor += weight
        if draw <= cursor:
            return index
    return len(weights) - 1


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


def _per_user_active_service_state(
    user_id: str,
    records: tuple[TrafficDemandRecord, ...],
) -> dict[str, object]:
    if not records:
        raise ValueError("records must not be empty")
    ordered_records = tuple(
        sorted(
            records,
            key=lambda record: (
                record.arrival_time,
                _service_id_from_record(record),
            ),
        )
    )
    primary_record = min(
        ordered_records,
        key=lambda record: (
            -record.input_flow.priority,
            record.arrival_time,
            _service_id_from_record(record),
        ),
    )
    service_classes = tuple(
        traffic_class.value
        for traffic_class in TrafficClass
        if any(record.traffic_class == traffic_class for record in ordered_records)
    )
    task_ids = tuple(
        record.task.task_id
        for record in ordered_records
        if record.task is not None
    )
    output_flow_ids = tuple(
        record.output_flow.flow_id
        for record in ordered_records
        if record.output_flow is not None
    )
    return {
        "user_id": user_id,
        "request_count": len(ordered_records),
        "service_classes": service_classes,
        "primary_service_class": primary_record.traffic_class.value,
        "max_priority": max(record.input_flow.priority for record in ordered_records),
        "first_arrival_time": ordered_records[0].arrival_time,
        "last_arrival_time": ordered_records[-1].arrival_time,
        "flow_ids": tuple(record.input_flow.flow_id for record in ordered_records),
        "task_ids": task_ids,
        "output_flow_ids": output_flow_ids,
        "total_input_data_mb": sum(record.input_data_size for record in ordered_records),
        "total_output_data_mb": sum(record.output_data_size for record in ordered_records),
    }


def _request_timeline_state(
    record: TrafficDemandRecord,
    *,
    sim_time: float,
    window_start: float,
) -> str:
    if record.arrival_time > sim_time:
        return "PENDING"
    if record.arrival_time >= window_start:
        return "RECENTLY_ARRIVED"
    return "PAST"


def _traffic_request_timeline_item(
    record: TrafficDemandRecord,
    sim_time: float,
    window_start: float,
) -> dict[str, object]:
    task_id = record.task.task_id if record.task is not None else ""
    output_flow_id = record.output_flow.flow_id if record.output_flow is not None else ""
    state = _request_timeline_state(
        record,
        sim_time=sim_time,
        window_start=window_start,
    )
    return {
        "request_id": _service_id_from_record(record),
        "input_flow_id": record.input_flow.flow_id,
        "task_id": task_id,
        "output_flow_id": output_flow_id,
        "source_id": record.input_flow.source_id,
        "target_id": record.input_flow.target_id,
        "arrival_time": float(record.arrival_time),
        "time_offset_s": float(record.arrival_time - sim_time),
        "request_state": state,
        "traffic_class": record.traffic_class.value,
        "destination_type": record.destination_type.value,
        "priority": int(record.input_flow.priority),
        "input_data_size": float(record.input_data_size),
        "output_data_size": float(record.output_data_size),
        "has_compute_task": record.task is not None,
        "has_output_flow": record.output_flow is not None,
        "service_state": _request_service_state(state),
    }


def _request_service_state(state: str) -> str:
    if state == "PENDING":
        return "SCHEDULED"
    if state == "RECENTLY_ARRIVED":
        return "ARRIVED_IN_RECENT_WINDOW"
    return "ARRIVED_BEFORE_RECENT_WINDOW"


def _traffic_class_explanation_row(
    traffic_class: TrafficClass,
    records: tuple[TrafficDemandRecord, ...],
) -> dict[str, object]:
    class_records = tuple(
        record for record in records if record.traffic_class == traffic_class
    )
    return {
        "traffic_class": traffic_class.value,
        "request_count": len(class_records),
        "input_flow_count": len(class_records),
        "task_request_count": sum(
            1 for record in class_records if record.task is not None
        ),
        "output_flow_count": sum(
            1 for record in class_records if record.output_flow is not None
        ),
        "total_input_data_mb": sum(record.input_data_size for record in class_records),
        "total_output_data_mb": sum(record.output_data_size for record in class_records),
        "destination_types": tuple(
            destination_type.value
            for destination_type in TrafficDestinationType
            if any(
                record.destination_type == destination_type
                for record in class_records
            )
        ),
    }


def _service_id_from_record(record: TrafficDemandRecord) -> str:
    flow_id = record.input_flow.flow_id
    if record.traffic_class == TrafficClass.COMPUTE_SERVICE and flow_id.endswith(
        "-input",
    ):
        return flow_id[: -len("-input")]
    return flow_id


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


def _normalize_weight_tuple(
    values: tuple[float, ...],
    field_name: str,
    *,
    expected_length: int,
) -> tuple[float, ...]:
    if not isinstance(values, tuple):
        raise TypeError(f"{field_name} must be a tuple")
    normalized = tuple(float(value) for value in values)
    if not normalized:
        return ()
    if len(normalized) != expected_length:
        raise ValueError(f"{field_name} length must match endpoint ids")
    if any(not isfinite(value) or value < 0.0 for value in normalized):
        raise ValueError(f"{field_name} values must be finite and non-negative")
    if sum(normalized) <= 0.0:
        raise ValueError(f"{field_name} must contain at least one positive weight")
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


def _require_positive_int(value: Any, field_name: str) -> None:
    _require_int(value, field_name)
    if value <= 0:
        raise ValueError(f"{field_name} must be positive")


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


def _require_probability(value: Any, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field_name} must be an int or float")
    numeric = float(value)
    if not isfinite(numeric) or numeric < 0.0 or numeric > 1.0:
        raise ValueError(f"{field_name} must be between 0 and 1")


__all__ = [
    "ComputeOutputFlowMetadata",
    "TrafficArrivalProfile",
    "TrafficClass",
    "TrafficDemandBatch",
    "TrafficDemandConfig",
    "TrafficDemandModel",
    "TrafficDemandProfile",
    "TrafficDemandRecord",
    "TrafficDestinationType",
    "TrafficServiceMixConfig",
    "TrafficServiceMixItem",
    "generate_traffic_demand",
    "generate_traffic_service_mix",
]
