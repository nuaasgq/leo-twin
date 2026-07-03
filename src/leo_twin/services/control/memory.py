"""Bounded memory primitives for scale-mode execution."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Generic, TypeVar


T = TypeVar("T")


@dataclass(frozen=True)
class RingBufferSnapshot:
    """Deterministic state of a bounded ring buffer."""

    size: int
    capacity: int
    dropped: int


class RingBuffer(Generic[T]):
    """Bounded FIFO buffer that never grows past its configured capacity."""

    def __init__(self, capacity: int) -> None:
        _require_positive_int(capacity, "capacity")
        self._capacity = capacity
        self._items: deque[T] = deque(maxlen=capacity)
        self._dropped = 0

    def append(self, item: T) -> None:
        if len(self._items) == self._capacity:
            self._dropped += 1
        self._items.append(item)

    def extend(self, items: tuple[T, ...]) -> None:
        for item in items:
            self.append(item)

    def items(self) -> tuple[T, ...]:
        return tuple(self._items)

    def snapshot(self) -> RingBufferSnapshot:
        return RingBufferSnapshot(
            size=len(self._items),
            capacity=self._capacity,
            dropped=self._dropped,
        )


@dataclass(frozen=True)
class ReplaySegment:
    """Metadata for one deterministic replay segment."""

    segment_id: str
    path: Path
    item_count: int


class SegmentedReplayLog:
    """Write replay data in bounded-size segments for lazy reconstruction."""

    def __init__(self, output_dir: str | Path, segment_size: int = 10_000) -> None:
        _require_positive_int(segment_size, "segment_size")
        self._output_dir = Path(output_dir)
        self._segment_size = segment_size
        self._buffer: list[str] = []
        self._segments: list[ReplaySegment] = []
        self._total_items = 0

    def append_line(self, line: str) -> None:
        if not isinstance(line, str):
            raise TypeError("line must be a str")
        self._buffer.append(line.rstrip("\n"))
        self._total_items += 1
        if len(self._buffer) >= self._segment_size:
            self.flush()

    def flush(self) -> tuple[ReplaySegment, ...]:
        if not self._buffer:
            return tuple(self._segments)
        self._output_dir.mkdir(parents=True, exist_ok=True)
        segment_id = f"segment-{len(self._segments):06d}"
        path = self._output_dir / f"{segment_id}.jsonl"
        path.write_text("\n".join(self._buffer) + "\n", encoding="utf-8")
        self._segments.append(
            ReplaySegment(
                segment_id=segment_id,
                path=path,
                item_count=len(self._buffer),
            )
        )
        self._buffer.clear()
        return tuple(self._segments)

    def segments(self) -> tuple[ReplaySegment, ...]:
        return tuple(self._segments)

    def total_items(self) -> int:
        return self._total_items


class SnapshotDownsampler(Generic[T]):
    """Keep deterministic snapshots at a fixed event interval."""

    def __init__(self, interval: int, capacity: int) -> None:
        _require_positive_int(interval, "interval")
        self._interval = interval
        self._buffer = RingBuffer[T](capacity)
        self._seen = 0

    def observe(self, snapshot: T) -> bool:
        self._seen += 1
        if self._seen == 1 or self._seen % self._interval == 0:
            self._buffer.append(snapshot)
            return True
        return False

    def snapshots(self) -> tuple[T, ...]:
        return self._buffer.items()

    def buffer_snapshot(self) -> RingBufferSnapshot:
        return self._buffer.snapshot()


def _require_positive_int(value: int, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field_name} must be an int")
    if value <= 0:
        raise ValueError(f"{field_name} must be positive")
