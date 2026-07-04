"""Runtime session status contracts."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from math import isfinite

from leo_twin.schema.config import RuntimeMode


class RuntimeLifecycleState(StrEnum):
    """Lifecycle states owned by the runtime session layer."""

    UNINITIALIZED = "UNINITIALIZED"
    INITIALIZED = "INITIALIZED"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    STOPPED = "STOPPED"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"


@dataclass(frozen=True)
class RuntimeStatus:
    """Deterministic status snapshot for one runtime session."""

    session_id: str
    lifecycle_state: RuntimeLifecycleState | str
    simulation_mode: RuntimeMode | str
    speed_factor: float
    current_sim_time: float
    wall_clock_start_time: float | None
    processed_event_count: int
    queued_event_count: int | None = None
    last_error: str | None = None
    deterministic_replay: bool = False
    config_version: int = 0

    def __post_init__(self) -> None:
        if not isinstance(self.session_id, str) or not self.session_id:
            raise TypeError("session_id must be a non-empty str")
        if not isinstance(self.lifecycle_state, RuntimeLifecycleState):
            object.__setattr__(
                self,
                "lifecycle_state",
                RuntimeLifecycleState(str(self.lifecycle_state)),
            )
        if not isinstance(self.simulation_mode, RuntimeMode):
            object.__setattr__(
                self,
                "simulation_mode",
                RuntimeMode(str(self.simulation_mode)),
            )
        _require_finite(self.speed_factor, "speed_factor")
        _require_finite(self.current_sim_time, "current_sim_time")
        if self.speed_factor <= 0.0:
            raise ValueError("speed_factor must be positive")
        if self.current_sim_time < 0.0:
            raise ValueError("current_sim_time must be non-negative")
        if self.wall_clock_start_time is not None:
            _require_finite(self.wall_clock_start_time, "wall_clock_start_time")
        _require_non_negative_int(self.processed_event_count, "processed_event_count")
        if self.queued_event_count is not None:
            _require_non_negative_int(self.queued_event_count, "queued_event_count")
        if self.last_error is not None and not isinstance(self.last_error, str):
            raise TypeError("last_error must be a str or None")
        if not isinstance(self.deterministic_replay, bool):
            raise TypeError("deterministic_replay must be a bool")
        _require_non_negative_int(self.config_version, "config_version")

    def to_dict(self) -> dict[str, str | int | float | bool | None]:
        lifecycle_state = RuntimeLifecycleState(self.lifecycle_state).value
        simulation_mode = RuntimeMode(self.simulation_mode).value
        return {
            "session_id": self.session_id,
            "lifecycle_state": lifecycle_state,
            "status": lifecycle_state,
            "simulation_mode": simulation_mode,
            "mode": simulation_mode,
            "speed_factor": self.speed_factor,
            "current_sim_time": self.current_sim_time,
            "wall_clock_start_time": self.wall_clock_start_time,
            "processed_event_count": self.processed_event_count,
            "queued_event_count": self.queued_event_count,
            "last_error": self.last_error,
            "deterministic_replay": self.deterministic_replay,
            "config_version": self.config_version,
        }


def _require_finite(value: object, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field_name} must be an int or float")
    if not isfinite(float(value)):
        raise ValueError(f"{field_name} must be finite")


def _require_non_negative_int(value: object, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field_name} must be an int")
    if value < 0:
        raise ValueError(f"{field_name} must be non-negative")
