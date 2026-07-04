"""Throttled state snapshot streaming outside the Event Kernel."""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any, Protocol

from leo_twin.schema import SimEvent


class SnapshotProjector(Protocol):
    """Projection hook that converts processed events into frontend state."""

    def apply(self, event: SimEvent) -> None:
        ...

    def snapshot(self) -> Any:
        ...


class SnapshotStream:
    """Maintain a throttled WorldSnapshot-compatible stream."""

    def __init__(
        self,
        *,
        projector: SnapshotProjector | None = None,
        initial_snapshot: Any | None = None,
        snapshot_interval_events: int = 1,
        max_frequency_hz: float | None = None,
        time_fn: Callable[[], float] = time.time,
    ) -> None:
        if snapshot_interval_events <= 0:
            raise ValueError("snapshot_interval_events must be positive")
        if max_frequency_hz is not None and max_frequency_hz <= 0.0:
            raise ValueError("max_frequency_hz must be positive when provided")
        self._projector = projector
        self._current_snapshot = (
            initial_snapshot if initial_snapshot is not None else _empty_snapshot()
        )
        self._snapshot_interval_events = snapshot_interval_events
        self._min_wall_interval = (
            None if max_frequency_hz is None else 1.0 / max_frequency_hz
        )
        self._time_fn = time_fn
        self._event_count = 0
        self._last_emit_time: float | None = None
        self._pending: list[Any] = []

    @property
    def event_count(self) -> int:
        return self._event_count

    def ingest(self, events: tuple[SimEvent, ...]) -> None:
        for event in events:
            self._event_count += 1
            if self._projector is not None:
                self._projector.apply(event)
            if self._event_count % self._snapshot_interval_events == 0:
                self._emit_if_allowed()

    def current_snapshot(self) -> Any:
        if self._projector is not None:
            self._current_snapshot = self._projector.snapshot()
        return self._current_snapshot

    def flush(self) -> None:
        snapshot = self.current_snapshot()
        if not self._pending or self._pending[-1] != snapshot:
            self._pending.append(snapshot)
            self._last_emit_time = self._time_fn()

    def pop_pending(self) -> tuple[Any, ...]:
        pending = tuple(self._pending)
        self._pending.clear()
        return pending

    def pending(self) -> tuple[Any, ...]:
        return tuple(self._pending)

    def _emit_if_allowed(self) -> None:
        now = self._time_fn()
        if (
            self._min_wall_interval is not None
            and self._last_emit_time is not None
            and now - self._last_emit_time < self._min_wall_interval
        ):
            return
        snapshot = self.current_snapshot()
        self._pending.append(snapshot)
        self._last_emit_time = now


def _empty_snapshot() -> dict[str, int | float]:
    return {"event_count": 0, "last_sim_time": 0.0}
