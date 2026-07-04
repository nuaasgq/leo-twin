"""External wall-clock to simulation-time control."""

from __future__ import annotations

import time
from collections.abc import Callable
from math import isfinite

from leo_twin.schema.config import RuntimeMode


class SimulationClockController:
    """Map wall-clock pacing policy to kernel run targets.

    The clock never mutates kernel time. It only computes an external target
    time; the Event Kernel remains the authority for accepted simulation time.
    """

    def __init__(
        self,
        mode: RuntimeMode | str = RuntimeMode.REAL_TIME,
        speed_factor: float = 1.0,
        *,
        deterministic_replay: bool = False,
        time_fn: Callable[[], float] = time.time,
    ) -> None:
        self._mode = RuntimeMode(str(mode))
        self._speed_factor = _validate_speed_factor(speed_factor)
        self._deterministic_replay = deterministic_replay
        self._time_fn = time_fn
        self._paused = self._mode == RuntimeMode.PAUSED
        self._wall_clock_start_time: float | None = None
        self._wall_clock_anchor: float | None = None
        self._sim_time_anchor = 0.0

    @property
    def mode(self) -> RuntimeMode:
        return self._mode

    @property
    def speed_factor(self) -> float:
        return self._speed_factor

    @property
    def deterministic_replay(self) -> bool:
        return self._deterministic_replay

    @property
    def wall_clock_start_time(self) -> float | None:
        return self._wall_clock_start_time

    def start(self, current_sim_time: float) -> None:
        self._sim_time_anchor = _validate_non_negative(current_sim_time, "current_sim_time")
        if self._wall_clock_start_time is None:
            self._wall_clock_start_time = self._time_fn()
        self._wall_clock_anchor = self._time_fn()
        self._paused = self._mode == RuntimeMode.PAUSED

    def pause(self, current_sim_time: float) -> None:
        self._sim_time_anchor = _validate_non_negative(current_sim_time, "current_sim_time")
        self._wall_clock_anchor = None
        self._paused = True

    def resume(self, current_sim_time: float) -> None:
        self._sim_time_anchor = _validate_non_negative(current_sim_time, "current_sim_time")
        if self._wall_clock_start_time is None:
            self._wall_clock_start_time = self._time_fn()
        self._wall_clock_anchor = self._time_fn()
        self._paused = self._mode == RuntimeMode.PAUSED

    def stop(self) -> None:
        self._wall_clock_anchor = None
        self._paused = True

    def reset(self) -> None:
        self._wall_clock_start_time = None
        self._wall_clock_anchor = None
        self._sim_time_anchor = 0.0
        self._paused = self._mode == RuntimeMode.PAUSED

    def set_mode(self, mode: RuntimeMode | str, current_sim_time: float) -> None:
        self._mode = RuntimeMode(str(mode))
        if self._mode == RuntimeMode.PAUSED:
            self.pause(current_sim_time)
        elif self._paused:
            self.resume(current_sim_time)

    def set_speed_factor(self, speed_factor: float, current_sim_time: float) -> None:
        self._sim_time_anchor = _validate_non_negative(current_sim_time, "current_sim_time")
        self._wall_clock_anchor = self._time_fn() if not self._paused else None
        self._speed_factor = _validate_speed_factor(speed_factor)

    def target_sim_time(
        self,
        current_sim_time: float,
        *,
        wall_time: float | None = None,
    ) -> float:
        """Return the next externally requested simulation time."""

        current = _validate_non_negative(current_sim_time, "current_sim_time")
        if self._paused or self._mode == RuntimeMode.PAUSED:
            return current
        if self._deterministic_replay:
            return current
        if self._wall_clock_anchor is None:
            return current
        now = self._time_fn() if wall_time is None else wall_time
        elapsed = max(0.0, now - self._wall_clock_anchor)
        factor = self._speed_factor if self._mode == RuntimeMode.ACCELERATED else 1.0
        return max(current, self._sim_time_anchor + elapsed * factor)

    def deterministic_target(self, current_sim_time: float, step_seconds: float) -> float:
        """Return a deterministic run target for replay and tests."""

        current = _validate_non_negative(current_sim_time, "current_sim_time")
        step = _validate_non_negative(step_seconds, "step_seconds")
        if self._paused or self._mode == RuntimeMode.PAUSED:
            return current
        factor = self._speed_factor if self._mode == RuntimeMode.ACCELERATED else 1.0
        return current + step * factor

    def wall_delay_for_sim_delta(self, sim_delta: float) -> float:
        """Return the wall-clock delay implied by the active pacing policy."""

        delta = _validate_non_negative(sim_delta, "sim_delta")
        if self._paused or self._mode == RuntimeMode.PAUSED:
            return float("inf")
        if self._mode == RuntimeMode.ACCELERATED:
            return delta / self._speed_factor
        return delta


def _validate_speed_factor(value: float) -> float:
    speed = _validate_non_negative(value, "speed_factor")
    if speed <= 0.0:
        raise ValueError("speed_factor must be positive")
    return speed


def _validate_non_negative(value: float, field_name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field_name} must be an int or float")
    result = float(value)
    if not isfinite(result):
        raise ValueError(f"{field_name} must be finite")
    if result < 0.0:
        raise ValueError(f"{field_name} must be non-negative")
    return result
