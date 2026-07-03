"""Deterministic event partitioning for large-scale execution control."""

from __future__ import annotations

import heapq
import re
from collections import Counter
from dataclasses import dataclass
from typing import Any

from leo_twin.schema import EventType, SimEvent


_MODULE_TYPES = frozenset(("orbit", "network", "compute", "metrics", "frontend"))
_SATELLITE_PATTERN = re.compile(r"sat-[A-Za-z0-9_]+|sat[A-Za-z0-9_]+")
_EventIdKey = tuple[int, int | str]
_QueueKey = tuple[float, int, _EventIdKey]
_QueueEntry = tuple[_QueueKey, SimEvent]


@dataclass(frozen=True, order=True)
class EventPartitionKey:
    """Logical partition key for scale-mode event routing."""

    module_type: str
    region_id: str
    satellite_id: str


@dataclass(frozen=True)
class EventPartitionSnapshot:
    """Deterministic partition buffer state used by scale safety tests."""

    total_events: int
    partition_count: int
    max_partition_depth: int
    pushed: int
    popped: int
    module_counts: tuple[tuple[str, int], ...]


class PartitionedEventBuffer:
    """Maintain independent deterministic sub-queues per event partition."""

    def __init__(
        self,
        *,
        region_count: int = 1024,
        max_events_per_partition: int = 4096,
    ) -> None:
        _require_positive_int(region_count, "region_count")
        _require_positive_int(max_events_per_partition, "max_events_per_partition")
        self._region_count = region_count
        self._max_events_per_partition = max_events_per_partition
        self._queues: dict[EventPartitionKey, list[_QueueEntry]] = {}
        self._module_counts: Counter[str] = Counter()
        self._pushed = 0
        self._popped = 0

    def partition_for(self, event: SimEvent) -> EventPartitionKey:
        module_type = _module_type(event)
        satellite_id = _satellite_id(event.payload) or _satellite_id_from_text(
            event.source,
            event.target,
            str(event.event_id),
        )
        if satellite_id is None:
            satellite_id = "global"
        region_id = _region_id(event.payload)
        if region_id is None:
            region_id = f"region-{_stable_bucket(satellite_id, self._region_count):04d}"
        return EventPartitionKey(
            module_type=module_type,
            region_id=region_id,
            satellite_id=satellite_id,
        )

    def push(self, event: SimEvent) -> EventPartitionKey:
        key = self.partition_for(event)
        queue = self._queues.setdefault(key, [])
        if len(queue) >= self._max_events_per_partition:
            raise MemoryError(f"event partition is full: {key}")
        heapq.heappush(queue, (_queue_key(event), event))
        self._module_counts[key.module_type] += 1
        self._pushed += 1
        return key

    def pop_partition(self, key: EventPartitionKey) -> SimEvent:
        queue = self._queues[key]
        _, event = heapq.heappop(queue)
        if not queue:
            del self._queues[key]
        self._module_counts[key.module_type] -= 1
        if self._module_counts[key.module_type] == 0:
            del self._module_counts[key.module_type]
        self._popped += 1
        return event

    def drain_partition(
        self,
        key: EventPartitionKey,
        limit: int | None = None,
    ) -> tuple[SimEvent, ...]:
        if limit is not None:
            _require_positive_int(limit, "limit")
        drained: list[SimEvent] = []
        while key in self._queues and (limit is None or len(drained) < limit):
            drained.append(self.pop_partition(key))
        return tuple(drained)

    def partition_keys(self) -> tuple[EventPartitionKey, ...]:
        return tuple(sorted(self._queues))

    def is_empty(self) -> bool:
        return not self._queues

    def snapshot(self) -> EventPartitionSnapshot:
        depths = tuple(len(queue) for _, queue in sorted(self._queues.items()))
        return EventPartitionSnapshot(
            total_events=sum(depths),
            partition_count=len(depths),
            max_partition_depth=max(depths, default=0),
            pushed=self._pushed,
            popped=self._popped,
            module_counts=tuple(sorted(self._module_counts.items())),
        )


def _queue_key(event: SimEvent) -> _QueueKey:
    return (event.sim_time, -event.priority, _event_id_key(event.event_id))


def _event_id_key(event_id: int | str) -> _EventIdKey:
    if isinstance(event_id, int):
        return (0, event_id)
    return (1, event_id)


def _module_type(event: SimEvent) -> str:
    target = event.target.strip().lower()
    source = event.source.strip().lower()
    if target in _MODULE_TYPES:
        return target
    if source in _MODULE_TYPES:
        return source
    event_type = str(event.event_type)
    if event_type.startswith("ORBIT"):
        return "orbit"
    if event_type in {
        EventType.ACCESS_START.value,
        EventType.ACCESS_END.value,
        EventType.LINK_UPDATE.value,
        EventType.ROUTE_UPDATE.value,
    }:
        return "network"
    if event_type.startswith("TASK"):
        return "compute"
    if event_type == EventType.METRIC_SAMPLE.value:
        return "metrics"
    return "global"


def _satellite_id(payload: object) -> str | None:
    for key in ("satellite_id", "source_id", "target_id", "entity_id"):
        value = _payload_value(payload, key)
        if isinstance(value, str) and value.startswith("sat"):
            return value
    return None


def _satellite_id_from_text(*values: str) -> str | None:
    for value in values:
        match = _SATELLITE_PATTERN.search(value)
        if match:
            return match.group(0)
    return None


def _region_id(payload: object) -> str | None:
    value = _payload_value(payload, "region_id")
    if isinstance(value, str) and value:
        return value
    cell_id = _payload_value(payload, "cell_id")
    if isinstance(cell_id, str) and cell_id:
        return cell_id
    return None


def _payload_value(payload: object, key: str) -> Any:
    if isinstance(payload, dict):
        return payload.get(key)
    return getattr(payload, key, None)


def _stable_bucket(value: str, bucket_count: int) -> int:
    total = 0
    for index, char in enumerate(value):
        total += (index + 1) * ord(char)
    return total % bucket_count


def _require_positive_int(value: int, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field_name} must be an int")
    if value <= 0:
        raise ValueError(f"{field_name} must be positive")
