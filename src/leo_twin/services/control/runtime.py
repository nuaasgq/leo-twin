"""Runtime control-plane state management for SEES."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from collections.abc import Iterable
from math import ceil
from pathlib import Path
from typing import Protocol

from leo_twin.schema.config import RuntimeMode, SEESConfig, config_to_dict
from leo_twin.schema.config_loader import (
    ConfigValidationError,
    merge_config_update,
)
from leo_twin.models.orbit import (
    SAFE_PER_SATELLITE_ORBIT_EVENT_THRESHOLD,
    OrbitUpdateMode,
    estimate_orbit_event_volume,
    resolve_orbit_update_mode,
)
from leo_twin.services.control.scale_safety import ScaleConfig, ScaleSafetyChecker


class RuntimeStatus(StrEnum):
    """Lifecycle state controlled by the runtime controller."""

    STOPPED = "STOPPED"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"


class RuntimeAction(StrEnum):
    """Actions accepted by the runtime control plane."""

    INITIALIZE = "INITIALIZE"
    START = "START"
    STOP = "STOP"
    PAUSE = "PAUSE"
    RESUME = "RESUME"
    RESET = "RESET"
    SET_SPEED = "SET_SPEED"
    SET_MODE = "SET_MODE"


class KernelStopPort(Protocol):
    """Minimal indirect kernel control port used by RuntimeController."""

    def stop(self) -> None:
        ...


@dataclass(frozen=True)
class RuntimeSnapshot:
    """Deterministic runtime-control snapshot."""

    status: RuntimeStatus
    mode: RuntimeMode
    speed_factor: float
    seed: int
    duration: int
    config_version: int
    last_action: str

    def to_json(self) -> dict[str, str | int | float]:
        return {
            "status": self.status.value,
            "mode": self.mode.value,
            "speed_factor": self.speed_factor,
            "seed": self.seed,
            "duration": self.duration,
            "config_version": self.config_version,
            "last_action": self.last_action,
        }


class SimulationClockController:
    """Deterministic runtime clock policy controller.

    The controller stores mode and speed policy only. It does not read wall
    clock time and it does not advance the SimulationKernel.
    """

    def __init__(self, runtime_mode: RuntimeMode, speed_factor: float) -> None:
        self._mode = runtime_mode
        self._speed_factor = speed_factor

    @property
    def mode(self) -> RuntimeMode:
        return self._mode

    @property
    def speed_factor(self) -> float:
        return self._speed_factor

    def apply_runtime_config(self, config: SEESConfig) -> None:
        self._mode = config.runtime.mode
        self._speed_factor = config.runtime.speed_factor

    def set_mode(self, mode: RuntimeMode | str) -> None:
        self._mode = RuntimeMode(str(mode))

    def set_speed_factor(self, speed_factor: float) -> None:
        updated = merge_config_update(SEESConfig(), {"speed_factor": speed_factor})
        self._speed_factor = updated.runtime.speed_factor

    def wall_delay_for_sim_delta(self, sim_delta: float) -> float:
        """Return deterministic delay policy for a simulation delta."""

        if self._mode == RuntimeMode.PAUSED:
            return float("inf")
        if self._mode == RuntimeMode.ACCELERATED:
            return max(0.0, sim_delta / self._speed_factor)
        return max(0.0, sim_delta)


class RuntimeController:
    """Apply config and lifecycle commands outside the simulation kernel."""

    def __init__(
        self,
        config: SEESConfig | None = None,
        scale_safety_checker: ScaleSafetyChecker | None = None,
        scale_source_paths: Iterable[str | Path] = (),
    ) -> None:
        self._config = SEESConfig() if config is None else config
        self._clock = SimulationClockController(
            self._config.runtime.mode,
            self._config.runtime.speed_factor,
        )
        self._status = (
            RuntimeStatus.PAUSED
            if self._config.runtime.mode == RuntimeMode.PAUSED
            else RuntimeStatus.STOPPED
        )
        self._config_version = 0
        self._last_action = "INIT"
        self._scale_safety_checker = scale_safety_checker
        self._scale_source_paths = tuple(scale_source_paths)

    @property
    def config(self) -> SEESConfig:
        return self._config

    @property
    def clock(self) -> SimulationClockController:
        return self._clock

    def apply_config(self, config: SEESConfig) -> RuntimeSnapshot:
        if not isinstance(config, SEESConfig):
            raise ConfigValidationError("RuntimeController requires a SEESConfig")
        self._config = config
        self._clock.apply_runtime_config(config)
        if config.runtime.mode == RuntimeMode.PAUSED:
            self._status = RuntimeStatus.PAUSED
        self._config_version += 1
        self._last_action = "CONFIG_UPDATE"
        return self.snapshot()

    def update_config(self, update: dict[str, object]) -> RuntimeSnapshot:
        return self.apply_config(merge_config_update(self._config, update))

    def initialize(self, update: dict[str, object] | None = None) -> RuntimeSnapshot:
        next_config = self._config
        if update:
            next_config = merge_config_update(self._config, update)
        self._validate_scale_safety(next_config)
        if update:
            self._config = next_config
            self._clock.apply_runtime_config(self._config)
            self._config_version += 1
        self._status = RuntimeStatus.STOPPED
        self._last_action = RuntimeAction.INITIALIZE.value
        return self.snapshot()

    def start(self) -> RuntimeSnapshot:
        self._validate_scale_safety(self._config)
        self._status = RuntimeStatus.RUNNING
        if self._clock.mode == RuntimeMode.PAUSED:
            self._clock.set_mode(RuntimeMode.REAL_TIME)
        self._last_action = RuntimeAction.START.value
        return self.snapshot()

    def pause(self) -> RuntimeSnapshot:
        self._status = RuntimeStatus.PAUSED
        self._clock.set_mode(RuntimeMode.PAUSED)
        self._last_action = RuntimeAction.PAUSE.value
        return self.snapshot()

    def resume(self) -> RuntimeSnapshot:
        self._status = RuntimeStatus.RUNNING
        if self._clock.mode == RuntimeMode.PAUSED:
            self._clock.set_mode(RuntimeMode.REAL_TIME)
        self._last_action = RuntimeAction.RESUME.value
        return self.snapshot()

    def stop(self, kernel: KernelStopPort | None = None) -> RuntimeSnapshot:
        self._status = RuntimeStatus.STOPPED
        if kernel is not None:
            kernel.stop()
        self._last_action = RuntimeAction.STOP.value
        return self.snapshot()

    def reset(self) -> RuntimeSnapshot:
        self._status = RuntimeStatus.STOPPED
        if self._clock.mode == RuntimeMode.PAUSED:
            self._clock.set_mode(self._config.runtime.mode)
        self._last_action = RuntimeAction.RESET.value
        return self.snapshot()

    def set_speed_factor(self, speed_factor: float) -> RuntimeSnapshot:
        if self._status == RuntimeStatus.RUNNING:
            raise RuntimeError(
                "speed factor cannot be changed while runtime is running; pause or stop first"
            )
        self.apply_config(merge_config_update(self._config, {"speed_factor": speed_factor}))
        self._last_action = RuntimeAction.SET_SPEED.value
        return self.snapshot()

    def set_mode(self, mode: RuntimeMode | str) -> RuntimeSnapshot:
        if self._status == RuntimeStatus.RUNNING:
            raise RuntimeError(
                "runtime mode cannot be changed while runtime is running; pause or stop first"
            )
        self.apply_config(merge_config_update(self._config, {"mode": str(mode)}))
        self._last_action = RuntimeAction.SET_MODE.value
        if self._clock.mode == RuntimeMode.PAUSED:
            self._status = RuntimeStatus.PAUSED
        return self.snapshot()

    def handle_action(
        self,
        action: RuntimeAction | str,
        payload: dict[str, object] | None = None,
        kernel: KernelStopPort | None = None,
    ) -> RuntimeSnapshot:
        selected = RuntimeAction(str(action))
        data = {} if payload is None else payload
        if selected == RuntimeAction.INITIALIZE:
            return self.initialize(data)
        if selected == RuntimeAction.START:
            return self.start()
        if selected == RuntimeAction.STOP:
            return self.stop(kernel)
        if selected == RuntimeAction.PAUSE:
            return self.pause()
        if selected == RuntimeAction.RESUME:
            return self.resume()
        if selected == RuntimeAction.RESET:
            return self.reset()
        if selected == RuntimeAction.SET_SPEED:
            return self.set_speed_factor(float(data["speed_factor"]))
        if selected == RuntimeAction.SET_MODE:
            return self.set_mode(str(data["mode"]))
        raise ValueError(f"unsupported runtime action: {selected}")

    def snapshot(self) -> RuntimeSnapshot:
        return RuntimeSnapshot(
            status=self._status,
            mode=self._clock.mode,
            speed_factor=self._clock.speed_factor,
            seed=self._config.runtime.seed,
            duration=self._config.runtime.duration,
            config_version=self._config_version,
            last_action=self._last_action,
        )

    def config_json(self) -> dict[str, object]:
        return config_to_dict(self._config)

    def _validate_scale_safety(self, config: SEESConfig) -> None:
        if self._scale_safety_checker is None:
            return
        self._scale_safety_checker.raise_if_unsafe(
            _scale_config_from_runtime_config(config),
            self._scale_source_paths,
        )


def _scale_config_from_runtime_config(config: SEESConfig) -> ScaleConfig:
    duration = float(config.runtime.duration)
    orbit_interval = config.scenario.orbit.update_interval_seconds
    flow_interval = config.scenario.traffic_model.flow_interval_seconds
    task_interval = config.scenario.traffic_model.task_interval_seconds
    compute_nodes = min(config.scenario.compute_nodes, config.scenario.satellite_count)
    orbit_tick_total = _scheduled_tick_count(duration, orbit_interval, include_final=True)
    orbit_target_count = 2
    forced_orbit_mode = config.scenario.orbit.orbit_update_mode
    orbit_mode = resolve_orbit_update_mode(
        config.scenario.satellite_count,
        forced_orbit_update_mode=(
            forced_orbit_mode.value if forced_orbit_mode is not None else None
        ),
    )
    per_satellite_orbit_events = estimate_orbit_event_volume(
        satellite_count=config.scenario.satellite_count,
        update_target_count=orbit_target_count,
        orbit_tick_count=orbit_tick_total,
    )
    orbit_update_events = (
        per_satellite_orbit_events
        if orbit_mode == OrbitUpdateMode.PER_SATELLITE
        else orbit_tick_total * orbit_target_count
    )
    flow_events = _scheduled_tick_count(duration, flow_interval) * compute_nodes
    task_events = _scheduled_tick_count(duration, task_interval) * compute_nodes
    return ScaleConfig(
        satellite_count=config.scenario.satellite_count,
        user_count=config.scenario.user_count,
        simulation_duration=duration,
        compute_node_count=compute_nodes,
        tick_interval=float(orbit_interval),
        partition_count=config.scenario.cell_count,
        scheduled_event_count=orbit_update_events + flow_events + task_events,
        max_event_count=(
            SAFE_PER_SATELLITE_ORBIT_EVENT_THRESHOLD
            if orbit_mode == OrbitUpdateMode.PER_SATELLITE
            else 1_000_000
        ),
    )


def _scheduled_tick_count(
    duration: float,
    interval: int,
    *,
    include_final: bool = False,
) -> int:
    count = ceil(duration / float(interval))
    if include_final and duration % float(interval) == 0.0:
        return count + 1
    return count
