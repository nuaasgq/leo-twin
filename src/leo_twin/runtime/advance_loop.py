"""Server-side runtime advance loop."""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from enum import StrEnum

from leo_twin.runtime.session import SimulationSession
from leo_twin.runtime.status import RuntimeLifecycleState
from leo_twin.runtime.stream_buffer import (
    StreamBackpressurePolicy,
    StreamBuffer,
    StreamBufferSnapshot,
)
from leo_twin.schema import SimEvent


class AdvanceLoopState(StrEnum):
    """Lifecycle of the server-side advance loop."""

    STOPPED = "STOPPED"
    RUNNING = "RUNNING"


@dataclass(frozen=True)
class AdvanceLoopSnapshot:
    """Operational state for the server-side loop."""

    state: AdvanceLoopState
    tick_count: int
    event_stream: StreamBufferSnapshot
    snapshot_stream: StreamBufferSnapshot

    def to_dict(self) -> dict[str, object]:
        return {
            "state": self.state.value,
            "tick_count": self.tick_count,
            "event_stream": self.event_stream.to_dict(),
            "snapshot_stream": self.snapshot_stream.to_dict(),
        }


class SessionAdvanceLoop:
    """Advance a session from a backend-owned loop and publish stream buffers."""

    def __init__(
        self,
        session: SimulationSession,
        *,
        event_stream: StreamBuffer[SimEvent] | None = None,
        snapshot_stream: StreamBuffer[object] | None = None,
        stream_policy: StreamBackpressurePolicy | None = None,
        tick_interval_seconds: float = 0.05,
    ) -> None:
        if tick_interval_seconds <= 0.0:
            raise ValueError("tick_interval_seconds must be positive")
        policy = stream_policy or StreamBackpressurePolicy()
        self._session = session
        self._event_stream = event_stream or StreamBuffer(policy)
        self._snapshot_stream = snapshot_stream or StreamBuffer(policy)
        self._tick_interval_seconds = float(tick_interval_seconds)
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._state = AdvanceLoopState.STOPPED
        self._tick_count = 0
        self._published_event_count = 0
        self._lock = threading.RLock()

    @property
    def session(self) -> SimulationSession:
        return self._session

    @property
    def event_stream(self) -> StreamBuffer[SimEvent]:
        return self._event_stream

    @property
    def snapshot_stream(self) -> StreamBuffer[object]:
        return self._snapshot_stream

    @property
    def state(self) -> AdvanceLoopState:
        with self._lock:
            return self._state

    def start(self) -> None:
        with self._lock:
            if self._state == AdvanceLoopState.RUNNING:
                return
            self._stop_event.clear()
            self._thread = threading.Thread(
                target=self._run,
                name=f"runtime-advance-{self._session.session_id}",
                daemon=True,
            )
            self._state = AdvanceLoopState.RUNNING
            self._thread.start()

    def stop(self, timeout_seconds: float = 2.0) -> None:
        thread: threading.Thread | None
        with self._lock:
            self._stop_event.set()
            thread = self._thread
        if thread is not None and thread.is_alive():
            thread.join(timeout_seconds)
        with self._lock:
            self._thread = None
            self._state = AdvanceLoopState.STOPPED

    def tick(self) -> tuple[SimEvent, ...]:
        """Advance once and publish any resulting event/snapshot records."""

        with self._lock:
            self._tick_count += 1
        lifecycle = self._session.lifecycle_state
        if lifecycle != RuntimeLifecycleState.RUNNING:
            self._publish_pending_session_records()
            return ()
        events = (
            self._session.advance_control_step()
            if self._session.get_status().deterministic_replay
            else self._session.advance()
        )
        self._publish_pending_session_records()
        return events

    def publish_pending(self) -> None:
        """Publish records already processed by the session without advancing."""

        with self._lock:
            self._publish_pending_session_records()

    def run_until_idle(self, max_ticks: int = 10_000) -> None:
        if max_ticks <= 0:
            raise ValueError("max_ticks must be positive")
        for _ in range(max_ticks):
            self.tick()
            status = self._session.get_status()
            if status.lifecycle_state in {
                RuntimeLifecycleState.COMPLETED,
                RuntimeLifecycleState.STOPPED,
                RuntimeLifecycleState.ERROR,
            }:
                return
            if status.lifecycle_state != RuntimeLifecycleState.RUNNING:
                return
            if status.queued_event_count == 0:
                return
        raise RuntimeError("advance loop did not become idle before max_ticks")

    def wait_until_idle(self, timeout_seconds: float = 2.0) -> bool:
        deadline = time.time() + timeout_seconds
        while time.time() <= deadline:
            status = self._session.get_status()
            if status.lifecycle_state in {
                RuntimeLifecycleState.COMPLETED,
                RuntimeLifecycleState.STOPPED,
                RuntimeLifecycleState.ERROR,
            }:
                return True
            if status.queued_event_count == 0:
                return True
            time.sleep(min(self._tick_interval_seconds, 0.01))
        return False

    def snapshot(self) -> AdvanceLoopSnapshot:
        with self._lock:
            return AdvanceLoopSnapshot(
                state=self._state,
                tick_count=self._tick_count,
                event_stream=self._event_stream.snapshot(),
                snapshot_stream=self._snapshot_stream.snapshot(),
            )

    def reset_streams(self) -> None:
        with self._lock:
            self._event_stream.clear()
            self._snapshot_stream.clear()
            self._published_event_count = 0

    def _run(self) -> None:
        try:
            while not self._stop_event.is_set():
                self.tick()
                time.sleep(self._tick_interval_seconds)
        finally:
            with self._lock:
                self._state = AdvanceLoopState.STOPPED

    def _publish_pending_session_records(self) -> None:
        events = self._session.processed_events
        if len(events) < self._published_event_count:
            self._event_stream.clear()
            self._snapshot_stream.clear()
            self._published_event_count = 0
        if len(events) > self._published_event_count:
            new_events = events[self._published_event_count :]
            self._event_stream.publish_many(new_events)
            self._published_event_count = len(events)
        for snapshot in self._session.pop_snapshots():
            self._snapshot_stream.publish(snapshot)
