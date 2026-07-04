"""Cursor-based runtime stream buffers with bounded backpressure."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from math import isfinite
from threading import RLock
from typing import Generic, TypeVar


T = TypeVar("T")


@dataclass(frozen=True)
class StreamBackpressurePolicy:
    """Bound retained stream data and per-read batch size."""

    max_items: int = 10_000
    max_batch_size: int = 1_000

    def __post_init__(self) -> None:
        _require_positive_int(self.max_items, "max_items")
        _require_positive_int(self.max_batch_size, "max_batch_size")


@dataclass(frozen=True)
class StreamBatch(Generic[T]):
    """A deterministic cursor read response."""

    items: tuple[T, ...]
    cursor: int
    next_cursor: int
    overflow: bool = False
    dropped_count: int = 0

    def to_dict(self) -> dict[str, object]:
        return {
            "items": list(self.items),
            "cursor": self.cursor,
            "next_cursor": self.next_cursor,
            "overflow": self.overflow,
            "dropped_count": self.dropped_count,
        }


@dataclass(frozen=True)
class StreamBufferSnapshot:
    """Operational state for a stream buffer."""

    next_sequence: int
    oldest_sequence: int
    retained_count: int
    total_dropped_count: int

    def to_dict(self) -> dict[str, int]:
        return {
            "next_sequence": self.next_sequence,
            "oldest_sequence": self.oldest_sequence,
            "retained_count": self.retained_count,
            "total_dropped_count": self.total_dropped_count,
        }


class StreamBuffer(Generic[T]):
    """Retain recent stream items and serve cursor reads.

    Cursors are monotonically increasing sequence numbers. A consumer passes the
    last observed cursor and receives items with greater sequence numbers.
    """

    def __init__(
        self,
        policy: StreamBackpressurePolicy | None = None,
    ) -> None:
        self._policy = policy or StreamBackpressurePolicy()
        self._entries: deque[tuple[int, T]] = deque()
        self._next_sequence = 1
        self._total_dropped_count = 0
        self._lock = RLock()

    @property
    def policy(self) -> StreamBackpressurePolicy:
        return self._policy

    def publish(self, item: T) -> int:
        with self._lock:
            sequence = self._next_sequence
            self._next_sequence += 1
            self._entries.append((sequence, item))
            while len(self._entries) > self._policy.max_items:
                self._entries.popleft()
                self._total_dropped_count += 1
            return sequence

    def publish_many(self, items: tuple[T, ...]) -> tuple[int, ...]:
        return tuple(self.publish(item) for item in items)

    def read_after(
        self,
        cursor: int = 0,
        *,
        limit: int | None = None,
    ) -> StreamBatch[T]:
        with self._lock:
            selected_limit = self._limit(limit)
            oldest = self._oldest_sequence()
            overflow = bool(self._entries) and cursor < oldest - 1
            dropped_count = max(0, oldest - cursor - 1) if overflow else 0
            items: list[T] = []
            next_cursor = cursor
            for sequence, item in self._entries:
                if sequence <= cursor:
                    continue
                items.append(item)
                next_cursor = sequence
                if len(items) >= selected_limit:
                    break
            return StreamBatch(
                items=tuple(items),
                cursor=cursor,
                next_cursor=next_cursor,
                overflow=overflow,
                dropped_count=dropped_count,
            )

    def snapshot(self) -> StreamBufferSnapshot:
        with self._lock:
            return StreamBufferSnapshot(
                next_sequence=self._next_sequence,
                oldest_sequence=self._oldest_sequence(),
                retained_count=len(self._entries),
                total_dropped_count=self._total_dropped_count,
            )

    def clear(self) -> None:
        with self._lock:
            self._entries.clear()
            self._next_sequence = 1
            self._total_dropped_count = 0

    def _oldest_sequence(self) -> int:
        if not self._entries:
            return self._next_sequence
        return self._entries[0][0]

    def _limit(self, value: int | None) -> int:
        if value is None:
            return self._policy.max_batch_size
        _require_positive_int(value, "limit")
        return min(value, self._policy.max_batch_size)


def _require_positive_int(value: object, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field_name} must be an int")
    if not isfinite(float(value)) or value <= 0:
        raise ValueError(f"{field_name} must be positive")
