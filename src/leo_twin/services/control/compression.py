"""Semantic event compression for scale-mode observability and replay."""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass, fields, is_dataclass
from math import floor, isfinite
from typing import Any

from leo_twin.schema import EventType, SimEvent
from leo_twin.services.control.partitioning import EventPartitionKey, PartitionedEventBuffer


CompressionPayload = dict[str, str | int | float | bool | tuple[str, ...] | tuple[tuple[str, int], ...]]


@dataclass(frozen=True)
class CompressedEventBatch:
    """A deterministic external compressed event batch."""

    batch_id: str
    compressed_type: str
    window_id: int
    sim_time_start: float
    sim_time_end: float
    priority: int
    partition: EventPartitionKey
    event_count: int
    first_event_id: str
    last_event_id: str
    event_digest: str
    payload_summary: CompressionPayload
    replay_events: tuple[SimEvent, ...] = ()


@dataclass(frozen=True)
class CompressionSnapshot:
    """Deterministic compression counters."""

    ingested: int
    emitted_batches: int
    buffered_groups: int
    buffered_events: int
    compressed_counts: tuple[tuple[str, int], ...]


class SemanticEventCompressor:
    """Aggregate high-frequency events without touching kernel semantics."""

    def __init__(
        self,
        *,
        window_seconds: float = 1.0,
        max_events_per_group: int = 1024,
        keep_replay_events: bool = False,
        region_count: int = 1024,
    ) -> None:
        _require_positive_number(window_seconds, "window_seconds")
        _require_positive_int(max_events_per_group, "max_events_per_group")
        self._window_seconds = float(window_seconds)
        self._max_events_per_group = max_events_per_group
        self._keep_replay_events = keep_replay_events
        self._partitioner = PartitionedEventBuffer(region_count=region_count)
        self._groups: dict[tuple[int, EventPartitionKey, str], _CompressionGroup] = {}
        self._ingested = 0
        self._emitted_batches = 0
        self._compressed_counts: Counter[str] = Counter()

    def ingest(self, event: SimEvent) -> tuple[CompressedEventBatch, ...]:
        window_id = self._window_for(event.sim_time)
        partition = self._partitioner.partition_for(event)
        compressed_type = compression_type_for(event)
        group_key = (window_id, partition, compressed_type)
        group = self._groups.get(group_key)
        if group is None:
            group = _CompressionGroup(
                window_id=window_id,
                partition=partition,
                compressed_type=compressed_type,
                keep_replay_events=self._keep_replay_events,
            )
            self._groups[group_key] = group

        group.record_event(event)
        self._ingested += 1
        self._compressed_counts[compressed_type] += 1
        if group.event_count >= self._max_events_per_group:
            return (self._flush_group(group_key),)
        return ()

    def flush_window_before(self, sim_time: float) -> tuple[CompressedEventBatch, ...]:
        cutoff_window = self._window_for(sim_time)
        keys = tuple(
            key for key in sorted(self._groups) if key[0] < cutoff_window
        )
        return tuple(self._flush_group(key) for key in keys)

    def flush_all(self) -> tuple[CompressedEventBatch, ...]:
        return tuple(self._flush_group(key) for key in tuple(sorted(self._groups)))

    def reconstruct(self, batch: CompressedEventBatch) -> tuple[SimEvent, ...]:
        if not batch.replay_events:
            raise ValueError("batch was created without embedded replay events")
        return batch.replay_events

    def snapshot(self) -> CompressionSnapshot:
        return CompressionSnapshot(
            ingested=self._ingested,
            emitted_batches=self._emitted_batches,
            buffered_groups=len(self._groups),
            buffered_events=sum(group.event_count for group in self._groups.values()),
            compressed_counts=tuple(sorted(self._compressed_counts.items())),
        )

    def _flush_group(
        self,
        group_key: tuple[int, EventPartitionKey, str],
    ) -> CompressedEventBatch:
        group = self._groups.pop(group_key)
        batch = group.to_batch(self._emitted_batches)
        self._emitted_batches += 1
        return batch

    def _window_for(self, sim_time: float) -> int:
        _require_non_negative_number(sim_time, "sim_time")
        return int(floor(sim_time / self._window_seconds))


class _CompressionGroup:
    def __init__(
        self,
        *,
        window_id: int,
        partition: EventPartitionKey,
        compressed_type: str,
        keep_replay_events: bool,
    ) -> None:
        self.window_id = window_id
        self.partition = partition
        self.compressed_type = compressed_type
        self.keep_replay_events = keep_replay_events
        self.event_count = 0
        self.sim_time_start = 0.0
        self.sim_time_end = 0.0
        self.priority = -10_000_000
        self.first_event_id = ""
        self.last_event_id = ""
        self._digest = 0
        self._event_type_counts: Counter[str] = Counter()
        self._entity_counts: Counter[str] = Counter()
        self._metric_counts: Counter[str] = Counter()
        self._replay_events: list[SimEvent] = []

    def record_event(self, event: SimEvent) -> None:
        if self.event_count == 0:
            self.sim_time_start = event.sim_time
            self.first_event_id = str(event.event_id)
        self.event_count += 1
        self.sim_time_end = event.sim_time
        self.priority = max(self.priority, event.priority)
        self.last_event_id = str(event.event_id)
        self._digest = _rolling_digest(self._digest, _event_digest_input(event))
        self._event_type_counts[str(event.event_type)] += 1
        entity_id = _entity_id(event.payload)
        if entity_id is not None:
            self._entity_counts[entity_id] += 1
        metric_name = _metric_name(event.payload)
        if metric_name is not None:
            self._metric_counts[metric_name] += 1
        if self.keep_replay_events:
            self._replay_events.append(event)

    def to_batch(self, sequence: int) -> CompressedEventBatch:
        summary: CompressionPayload = {
            "event_types": tuple(sorted(self._event_type_counts.items())),
            "entities": tuple(sorted(self._entity_counts.items()))[:128],
            "entity_count": len(self._entity_counts),
            "metric_names": tuple(sorted(self._metric_counts.items()))[:128],
            "metric_name_count": len(self._metric_counts),
        }
        return CompressedEventBatch(
            batch_id=(
                f"compressed:{self.compressed_type}:"
                f"{self.window_id:08d}:{sequence:08d}"
            ),
            compressed_type=self.compressed_type,
            window_id=self.window_id,
            sim_time_start=self.sim_time_start,
            sim_time_end=self.sim_time_end,
            priority=self.priority,
            partition=self.partition,
            event_count=self.event_count,
            first_event_id=self.first_event_id,
            last_event_id=self.last_event_id,
            event_digest=f"{self._digest:016x}",
            payload_summary=summary,
            replay_events=tuple(self._replay_events),
        )


def compression_type_for(event: SimEvent) -> str:
    event_type = str(event.event_type)
    if event_type == EventType.ORBIT_UPDATE.value:
        return "ORBIT_BATCH_UPDATE"
    if event_type == EventType.LINK_UPDATE.value:
        return "LINK_DIFF_UPDATE"
    if event_type == EventType.METRIC_SAMPLE.value:
        return "METRIC_AGGREGATED_SAMPLE"
    return f"{event_type}_BATCH"


def _event_digest_input(event: SimEvent) -> str:
    return json.dumps(
        (
            str(event.event_id),
            event.sim_time,
            event.priority,
            event.source,
            event.target,
            str(event.event_type),
            _canonical_payload(event.payload),
        ),
        sort_keys=True,
        separators=(",", ":"),
    )


def _rolling_digest(current: int, text: str) -> int:
    value = current
    for char in text:
        value = ((value * 131) + ord(char)) & 0xFFFFFFFFFFFFFFFF
    return value


def _entity_id(payload: object) -> str | None:
    for key in ("satellite_id", "source_id", "target_id", "entity_id", "task_id"):
        value = _payload_value(payload, key)
        if isinstance(value, str) and value:
            return value
    return None


def _metric_name(payload: object) -> str | None:
    value = _payload_value(payload, "metric_name")
    if isinstance(value, str) and value:
        return value
    return None


def _payload_value(payload: object, key: str) -> Any:
    if isinstance(payload, dict):
        return payload.get(key)
    return getattr(payload, key, None)


def _canonical_payload(value: object) -> object:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, EventType):
        return value.value
    if is_dataclass(value) and not isinstance(value, type):
        return {
            field.name: _canonical_payload(getattr(value, field.name))
            for field in fields(value)
        }
    if isinstance(value, dict):
        return {
            str(key): _canonical_payload(value[key])
            for key in sorted(value, key=lambda item: str(item))
        }
    if isinstance(value, tuple | list):
        return [_canonical_payload(item) for item in value]
    return repr(value)


def _require_positive_int(value: int, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field_name} must be an int")
    if value <= 0:
        raise ValueError(f"{field_name} must be positive")


def _require_positive_number(value: float, field_name: str) -> None:
    _require_non_negative_number(value, field_name)
    if value <= 0:
        raise ValueError(f"{field_name} must be positive")


def _require_non_negative_number(value: float, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field_name} must be an int or float")
    if not isfinite(value) or value < 0:
        raise ValueError(f"{field_name} must be finite and non-negative")
