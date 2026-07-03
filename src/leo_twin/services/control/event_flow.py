"""External event-flow control for deterministic large-scale execution."""

from __future__ import annotations

import json
from collections import Counter, deque
from collections.abc import Mapping
from dataclasses import dataclass, fields, is_dataclass
from math import floor
from typing import Protocol

from leo_twin.schema import EventType, SimEvent
from leo_twin.services.control.modes import EventFlowPolicy


_EventIdKey = tuple[int, int | str]
_BufferEntry = tuple[int, SimEvent]
_CanonicalPayload = (
    str
    | int
    | float
    | bool
    | tuple["_CanonicalPayload", ...]
    | tuple[tuple[str, "_CanonicalPayload"], ...]
    | None
)


@dataclass(frozen=True)
class EventFlowSnapshot:
    """Deterministic counters exposed by the event-flow controller."""

    accepted: int
    buffered: int
    deduplicated: int
    flushed: int
    suppressed: int
    throttled: int
    window_counts: tuple[tuple[int, int], ...]


class _KernelLike(Protocol):
    def schedule_event(self, event: SimEvent) -> None:
        ...

    def stop(self) -> None:
        ...

    def get_current_time(self) -> float:
        ...


class _SimulationModuleLike(Protocol):
    def on_event(self, event: SimEvent, kernel: _KernelLike) -> None:
        ...

    def name(self) -> str:
        ...


class EventFlowController:
    """Control event propagation without modifying the simulation kernel."""

    def __init__(self, policy: EventFlowPolicy | None = None) -> None:
        self._policy = EventFlowPolicy() if policy is None else policy
        self._buffer: list[_BufferEntry] = []
        self._buffer_keys: set[tuple[object, ...]] = set()
        self._window_counts: dict[int, int] = {}
        self._window_order: deque[int] = deque()
        self._active_kernel: _KernelLike | None = None
        self._dispatch_time = 0.0
        self._counters: Counter[str] = Counter()

    @property
    def policy(self) -> EventFlowPolicy:
        return self._policy

    def begin_dispatch(self, event: SimEvent, kernel: _KernelLike) -> None:
        self._active_kernel = kernel
        self._dispatch_time = event.sim_time

    def schedule_event(self, event: SimEvent) -> None:
        window = self._window_for(event)
        if self._is_suppressed(event):
            self._counters["suppressed"] += 1
            return
        if self._is_throttled(event, window):
            self._counters["throttled"] += 1
            return
        if self._policy.deduplicate and self._is_duplicate(event, window):
            self._counters["deduplicated"] += 1
            return

        self._buffer.append((window, event))
        if self._policy.deduplicate:
            self._buffer_keys.add(_event_fingerprint(event, window))
        self._increment_window(window)
        self._counters["accepted"] += 1

    def flush_to(self, kernel: _KernelLike | None = None) -> tuple[SimEvent, ...]:
        target_kernel = self._active_kernel if kernel is None else kernel
        if target_kernel is None:
            raise RuntimeError("no kernel is available for event-flow flush")

        emitted: list[SimEvent] = []
        for _, event in sorted(self._buffer, key=_buffer_sort_key):
            target_kernel.schedule_event(event)
            emitted.append(event)

        self._counters["flushed"] += len(emitted)
        self._buffer.clear()
        self._buffer_keys.clear()
        return tuple(emitted)

    def stop(self) -> None:
        if self._active_kernel is None:
            raise RuntimeError("no active kernel is available to stop")
        self._active_kernel.stop()

    def get_current_time(self) -> float:
        return self._dispatch_time

    def snapshot(self) -> EventFlowSnapshot:
        return EventFlowSnapshot(
            accepted=self._counters["accepted"],
            buffered=len(self._buffer),
            deduplicated=self._counters["deduplicated"],
            flushed=self._counters["flushed"],
            suppressed=self._counters["suppressed"],
            throttled=self._counters["throttled"],
            window_counts=tuple(
                (window, self._window_counts[window])
                for window in sorted(self._window_counts)
            ),
        )

    def _is_suppressed(self, event: SimEvent) -> bool:
        return str(event.event_type) in self._policy.suppressed_event_types

    def _is_throttled(self, event: SimEvent, window: int) -> bool:
        if self._policy.priority_floor is not None:
            if event.priority < self._policy.priority_floor:
                return True
        if self._policy.max_events_per_window is None:
            return False
        return self._window_counts.get(window, 0) >= self._policy.max_events_per_window

    def _is_duplicate(self, event: SimEvent, window: int) -> bool:
        return _event_fingerprint(event, window) in self._buffer_keys

    def _increment_window(self, window: int) -> None:
        if window not in self._window_counts:
            self._window_order.append(window)
        self._window_counts[window] = self._window_counts.get(window, 0) + 1
        while len(self._window_order) > self._policy.window_history_limit:
            expired = self._window_order.popleft()
            self._window_counts.pop(expired, None)

    def _window_for(self, event: SimEvent) -> int:
        if not self._policy.batching_enabled or self._policy.time_window == 0:
            return int(floor(event.sim_time * 1_000_000_000))
        return int(floor(event.sim_time / self._policy.time_window))


class ControlledModule:
    """Wrap a module so emitted events pass through an external controller."""

    def __init__(
        self,
        module: _SimulationModuleLike,
        controller: EventFlowController,
    ) -> None:
        self._module = module
        self._controller = controller

    def name(self) -> str:
        return self._module.name()

    def on_event(self, event: SimEvent, kernel: _KernelLike) -> None:
        self._controller.begin_dispatch(event, kernel)
        self._module.on_event(event, self._controller)  # type: ignore[arg-type]
        self._controller.flush_to(kernel)


def _buffer_sort_key(entry: _BufferEntry) -> tuple[int, float, int, _EventIdKey]:
    window, event = entry
    return (window, event.sim_time, -event.priority, _event_id_key(event.event_id))


def _event_id_key(event_id: int | str) -> _EventIdKey:
    if isinstance(event_id, int):
        return (0, event_id)
    return (1, event_id)


def _event_fingerprint(event: SimEvent, window: int) -> tuple[object, ...]:
    payload = _canonical_payload(event.payload)
    return (
        window,
        event.source,
        event.target,
        str(event.event_type),
        json.dumps(payload, sort_keys=True, separators=(",", ":")),
    )


def _canonical_payload(value: object) -> _CanonicalPayload:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, EventType):
        return value.value
    if is_dataclass(value) and not isinstance(value, type):
        return tuple(
            (field.name, _canonical_payload(getattr(value, field.name)))
            for field in fields(value)
        )
    if isinstance(value, Mapping):
        return tuple(
            (str(key), _canonical_payload(value[key]))
            for key in sorted(value, key=lambda item: str(item))
        )
    if isinstance(value, tuple | list):
        return tuple(_canonical_payload(item) for item in value)
    raise TypeError(
        "deduplication requires deterministic JSON-compatible event payloads"
    )
