"""Registry for product runtime sessions."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from threading import RLock

from leo_twin.runtime.session import (
    KernelFactory,
    SimulationSession,
)
from leo_twin.runtime.status import RuntimeStatus
from leo_twin.schema.config import RuntimeConfig, ScenarioConfig


@dataclass(frozen=True)
class RuntimeSessionRecord:
    """Stable registry view of one session."""

    session_id: str
    status: RuntimeStatus

    def to_dict(self) -> dict[str, object]:
        return {
            "session_id": self.session_id,
            "status": self.status.to_dict(),
        }


class SimulationSessionRegistry:
    """Own multiple runtime sessions without changing kernel behavior."""

    def __init__(self) -> None:
        self._sessions: dict[str, SimulationSession] = {}
        self._lock = RLock()

    def create(
        self,
        *,
        session_id: str,
        runtime_config: RuntimeConfig,
        scenario_config: ScenarioConfig,
        kernel_factory: KernelFactory,
        snapshot_interval_events: int = 1,
        snapshot_max_frequency_hz: float | None = None,
        deterministic_replay: bool = False,
        control_step_seconds: float = 1.0,
        initialize: bool = True,
    ) -> SimulationSession:
        session = SimulationSession(
            session_id=session_id,
            runtime_config=runtime_config,
            scenario_config=scenario_config,
            kernel_factory=kernel_factory,
            snapshot_interval_events=snapshot_interval_events,
            snapshot_max_frequency_hz=snapshot_max_frequency_hz,
            deterministic_replay=deterministic_replay,
            control_step_seconds=control_step_seconds,
        )
        if initialize:
            session.initialize()
        self.register(session)
        return session

    def register(self, session: SimulationSession) -> None:
        with self._lock:
            if session.session_id in self._sessions:
                raise ValueError(f"session already registered: {session.session_id}")
            self._sessions[session.session_id] = session

    def get(self, session_id: str) -> SimulationSession:
        with self._lock:
            try:
                return self._sessions[session_id]
            except KeyError as exc:
                raise KeyError(f"unknown runtime session: {session_id}") from exc

    def remove(self, session_id: str) -> SimulationSession:
        with self._lock:
            try:
                return self._sessions.pop(session_id)
            except KeyError as exc:
                raise KeyError(f"unknown runtime session: {session_id}") from exc

    def contains(self, session_id: str) -> bool:
        with self._lock:
            return session_id in self._sessions

    def list_sessions(self) -> tuple[RuntimeSessionRecord, ...]:
        with self._lock:
            return tuple(
                RuntimeSessionRecord(session_id, session.get_status())
                for session_id, session in sorted(self._sessions.items())
            )

    def statuses(self) -> tuple[RuntimeStatus, ...]:
        return tuple(record.status for record in self.list_sessions())

    def session_ids(self) -> tuple[str, ...]:
        with self._lock:
            return tuple(sorted(self._sessions))

    def __len__(self) -> int:
        with self._lock:
            return len(self._sessions)

    def __iter__(self) -> Iterable[SimulationSession]:
        with self._lock:
            return iter(tuple(self._sessions[key] for key in sorted(self._sessions)))
