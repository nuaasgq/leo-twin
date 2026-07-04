"""Thin controller facade over runtime session services."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from typing import Any

from leo_twin.runtime.control_protocol import ControlProtocol
from leo_twin.runtime.session import SimulationSession
from leo_twin.schema import SimEvent


class SimulationController:
    """Expose status, command, event, and snapshot access for adapters."""

    def __init__(self, session: SimulationSession) -> None:
        self._session = session
        self._protocol = ControlProtocol(session)

    @property
    def session(self) -> SimulationSession:
        return self._session

    def handle_raw_message(self, raw: str | bytes | Mapping[str, Any]) -> dict[str, Any]:
        return self._protocol.handle(raw)

    def runtime_status(self) -> dict[str, Any]:
        return {
            "type": "RUNTIME_STATUS",
            "status": self._session.get_status().to_dict(),
        }

    def stream_events(
        self,
        event_filter: Callable[[SimEvent], bool] | None = None,
    ) -> tuple[SimEvent, ...]:
        events = self._session.processed_events
        if event_filter is None:
            return events
        return tuple(event for event in events if event_filter(event))

    def stream_snapshots(self) -> tuple[object, ...]:
        return self._session.pop_snapshots()

    def snapshot(self) -> object:
        return self._session.get_snapshot()

    def advance_to_end(self) -> tuple[SimEvent, ...]:
        return self._session.advance_to_end()

    def advance_control_step(self) -> tuple[SimEvent, ...]:
        return self._session.advance_control_step()

    def iter_events(
        self,
        event_filter: Callable[[SimEvent], bool] | None = None,
    ) -> Iterable[SimEvent]:
        return iter(self.stream_events(event_filter))
