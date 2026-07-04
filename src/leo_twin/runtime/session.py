"""Product runtime session over the frozen Event Kernel."""

from __future__ import annotations

from dataclasses import dataclass, replace
from threading import RLock
from time import perf_counter
from typing import Protocol

from leo_twin.runtime.clock import SimulationClockController
from leo_twin.runtime.profiling import (
    PROFILE_TIMING_FIELDS,
    RuntimeTickObserver,
    empty_profiling_summary,
)
from leo_twin.runtime.snapshot_stream import SnapshotProjector, SnapshotStream
from leo_twin.runtime.status import RuntimeLifecycleState, RuntimeStatus
from leo_twin.schema import SimEvent
from leo_twin.schema.config import RuntimeConfig, RuntimeMode, ScenarioConfig


class KernelPort(Protocol):
    """Public Event Kernel surface used by runtime sessions."""

    def schedule_event(self, event: SimEvent) -> None:
        ...

    def run(self, until_time: float | None = None) -> tuple[SimEvent, ...]:
        ...

    def stop(self) -> None:
        ...

    def get_current_time(self) -> float:
        ...


@dataclass(frozen=True)
class RuntimeKernelSpec:
    """Kernel and observation hooks for one initialized session."""

    kernel: KernelPort
    initial_events: tuple[SimEvent, ...] = ()
    snapshot_projector: SnapshotProjector | None = None
    initial_snapshot: object | None = None
    tick_observer: RuntimeTickObserver | None = None


class KernelFactory(Protocol):
    """Build a fresh kernel instance for a runtime session."""

    def __call__(
        self,
        scenario_config: ScenarioConfig,
        runtime_config: RuntimeConfig,
    ) -> RuntimeKernelSpec:
        ...


class SimulationSession:
    """Own and externally drive one simulation run instance."""

    def __init__(
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
    ) -> None:
        if not session_id:
            raise ValueError("session_id must be non-empty")
        if control_step_seconds <= 0.0:
            raise ValueError("control_step_seconds must be positive")
        self._session_id = session_id
        self._runtime_config = runtime_config
        self._scenario_config = scenario_config
        self._kernel_factory = kernel_factory
        self._snapshot_interval_events = snapshot_interval_events
        self._snapshot_max_frequency_hz = snapshot_max_frequency_hz
        self._deterministic_replay = deterministic_replay
        self._control_step_seconds = float(control_step_seconds)
        self._clock = SimulationClockController(
            runtime_config.mode,
            runtime_config.speed_factor,
            deterministic_replay=deterministic_replay,
        )
        self._kernel: KernelPort | None = None
        self._tick_observer: RuntimeTickObserver | None = None
        self._snapshot_stream = SnapshotStream()
        self._processed_events: list[SimEvent] = []
        self._lifecycle_state = RuntimeLifecycleState.UNINITIALIZED
        self._last_error: str | None = None
        self._config_version = 0
        self._last_profiling_summary: dict[str, object] | None = None
        self._last_backpressure_summary: dict[str, object] | None = None
        self._lock = RLock()

    @property
    def session_id(self) -> str:
        return self._session_id

    @property
    def runtime_config(self) -> RuntimeConfig:
        with self._lock:
            return self._runtime_config

    @property
    def scenario_config(self) -> ScenarioConfig:
        with self._lock:
            return self._scenario_config

    @property
    def kernel(self) -> KernelPort | None:
        with self._lock:
            return self._kernel

    @property
    def lifecycle_state(self) -> RuntimeLifecycleState:
        with self._lock:
            return self._lifecycle_state

    @property
    def processed_events(self) -> tuple[SimEvent, ...]:
        with self._lock:
            return tuple(self._processed_events)

    def initialize(
        self,
        *,
        runtime_config: RuntimeConfig | None = None,
        scenario_config: ScenarioConfig | None = None,
    ) -> RuntimeStatus:
        """Create a fresh kernel and schedule scenario initialization events."""

        with self._lock:
            if runtime_config is not None:
                self._runtime_config = runtime_config
            if scenario_config is not None:
                self._scenario_config = scenario_config
            self._clock = SimulationClockController(
                self._runtime_config.mode,
                self._runtime_config.speed_factor,
                deterministic_replay=self._deterministic_replay,
            )
            try:
                spec = self._kernel_factory(self._scenario_config, self._runtime_config)
                self._kernel = spec.kernel
                self._tick_observer = spec.tick_observer
                for event in spec.initial_events:
                    self._kernel.schedule_event(event)
                self._snapshot_stream = SnapshotStream(
                    projector=spec.snapshot_projector,
                    initial_snapshot=spec.initial_snapshot,
                    snapshot_interval_events=self._snapshot_interval_events,
                    max_frequency_hz=self._snapshot_max_frequency_hz,
                )
                self._processed_events.clear()
                self._last_profiling_summary = None
                self._last_backpressure_summary = None
                self._lifecycle_state = RuntimeLifecycleState.INITIALIZED
                self._last_error = None
                self._config_version += 1
            except Exception as exc:
                self._last_error = str(exc)
                self._lifecycle_state = RuntimeLifecycleState.ERROR
                raise
            return self.get_status()

    def start(self) -> RuntimeStatus:
        with self._lock:
            if self._lifecycle_state == RuntimeLifecycleState.UNINITIALIZED:
                self.initialize()
            self._require_kernel()
            if self._lifecycle_state == RuntimeLifecycleState.STOPPED:
                raise RuntimeError("stopped session must be reset before start")
            self._lifecycle_state = RuntimeLifecycleState.RUNNING
            self._clock.start(self._current_sim_time())
            self.advance_control_step()
            return self.get_status()

    def start_live(self) -> RuntimeStatus:
        """Start the session without draining a control step on the caller thread."""

        with self._lock:
            if self._lifecycle_state == RuntimeLifecycleState.UNINITIALIZED:
                self.initialize()
            self._require_kernel()
            if self._lifecycle_state == RuntimeLifecycleState.STOPPED:
                raise RuntimeError("stopped session must be reset before start")
            self._lifecycle_state = RuntimeLifecycleState.RUNNING
            self._clock.start(self._current_sim_time())
            return self.get_status()

    def pause(self) -> RuntimeStatus:
        with self._lock:
            self._require_kernel()
            self._lifecycle_state = RuntimeLifecycleState.PAUSED
            self._clock.pause(self._current_sim_time())
            return self.get_status()

    def resume(self) -> RuntimeStatus:
        with self._lock:
            self._require_kernel()
            if self._lifecycle_state != RuntimeLifecycleState.PAUSED:
                raise RuntimeError("only a paused session can be resumed")
            self._lifecycle_state = RuntimeLifecycleState.RUNNING
            self._clock.resume(self._current_sim_time())
            self.advance_control_step()
            return self.get_status()

    def resume_live(self) -> RuntimeStatus:
        """Resume the session without advancing on the caller thread."""

        with self._lock:
            self._require_kernel()
            if self._lifecycle_state != RuntimeLifecycleState.PAUSED:
                raise RuntimeError("only a paused session can be resumed")
            self._lifecycle_state = RuntimeLifecycleState.RUNNING
            self._clock.resume(self._current_sim_time())
            return self.get_status()

    def stop(self) -> RuntimeStatus:
        with self._lock:
            kernel = self._require_kernel()
            kernel.stop()
            self._clock.stop()
            self._lifecycle_state = RuntimeLifecycleState.STOPPED
            return self.get_status()

    def reset(self) -> RuntimeStatus:
        with self._lock:
            status = self.initialize()
            self._clock.reset()
            return status

    def set_speed_factor(self, value: float) -> RuntimeStatus:
        with self._lock:
            current = self._current_sim_time()
            self._runtime_config = replace(self._runtime_config, speed_factor=float(value))
            self._clock.set_speed_factor(self._runtime_config.speed_factor, current)
            self._config_version += 1
            return self.get_status()

    def set_mode(self, mode: RuntimeMode | str) -> RuntimeStatus:
        with self._lock:
            current = self._current_sim_time()
            self._runtime_config = replace(self._runtime_config, mode=RuntimeMode(str(mode)))
            self._clock.set_mode(self._runtime_config.mode, current)
            if self._runtime_config.mode == RuntimeMode.PAUSED:
                self._lifecycle_state = RuntimeLifecycleState.PAUSED
            self._config_version += 1
            return self.get_status()

    def advance(self, *, wall_time: float | None = None) -> tuple[SimEvent, ...]:
        with self._lock:
            if self._lifecycle_state != RuntimeLifecycleState.RUNNING:
                return ()
            target = self._clock.target_sim_time(
                self._current_sim_time(),
                wall_time=wall_time,
            )
            return self._run_until(target)

    def advance_bounded(self, max_delta_seconds: float) -> tuple[SimEvent, ...]:
        """Advance toward wall-clock time, capped by one bounded sim-time step."""

        if max_delta_seconds <= 0.0:
            raise ValueError("max_delta_seconds must be positive")
        with self._lock:
            if self._lifecycle_state != RuntimeLifecycleState.RUNNING:
                return ()
            current = self._current_sim_time()
            wall_target = self._clock.target_sim_time(current)
            bounded_target = self._clock.deterministic_target(
                current,
                max_delta_seconds,
            )
            return self._run_until(min(wall_target, bounded_target))

    def advance_control_step(self) -> tuple[SimEvent, ...]:
        with self._lock:
            if self._lifecycle_state != RuntimeLifecycleState.RUNNING:
                return ()
            target = self._clock.deterministic_target(
                self._current_sim_time(),
                self._control_step_seconds,
            )
            return self._run_until(target)

    def advance_to_end(self) -> tuple[SimEvent, ...]:
        with self._lock:
            if self._lifecycle_state not in {
                RuntimeLifecycleState.RUNNING,
                RuntimeLifecycleState.COMPLETED,
            }:
                return ()
            before = len(self._processed_events)
            self._run_until(None)
            if self._lifecycle_state == RuntimeLifecycleState.RUNNING:
                self._lifecycle_state = RuntimeLifecycleState.COMPLETED
            self._snapshot_stream.flush()
            return tuple(self._processed_events[before:])

    def get_status(self) -> RuntimeStatus:
        with self._lock:
            return RuntimeStatus(
                session_id=self._session_id,
                lifecycle_state=self._lifecycle_state,
                simulation_mode=self._runtime_config.mode,
                speed_factor=self._runtime_config.speed_factor,
                current_sim_time=self._current_sim_time(),
                wall_clock_start_time=self._clock.wall_clock_start_time,
                processed_event_count=len(self._processed_events),
                queued_event_count=_queued_event_count(self._kernel),
                last_error=self._last_error,
                deterministic_replay=self._deterministic_replay,
                config_version=self._config_version,
                profiling_summary=self._last_profiling_summary,
                backpressure_summary=self._last_backpressure_summary,
            )

    def record_tick_observability(
        self,
        *,
        tick_duration_ms: float,
        tick_budget_ms: float,
        tick_index: int,
        processed_event_count: int,
    ) -> None:
        """Store operational tick profiling/backpressure after an advance loop tick."""

        with self._lock:
            profiling = (
                dict(self._last_profiling_summary)
                if self._last_profiling_summary is not None
                else empty_profiling_summary(
                    processed_event_count=processed_event_count,
                )
            )
            profiling["total_tick_time_ms"] = round(
                max(0.0, float(tick_duration_ms)),
                6,
            )
            profiling["processed_event_count"] = int(processed_event_count)
            self._last_profiling_summary = profiling
            queue_depth = _queued_event_count(self._kernel)
            self._last_backpressure_summary = _backpressure_summary(
                profiling=profiling,
                tick_duration_ms=float(tick_duration_ms),
                tick_budget_ms=float(tick_budget_ms),
                queue_depth=0 if queue_depth is None else queue_depth,
                processed_event_count=processed_event_count,
                first_tick=tick_index == 1,
            )

    def get_snapshot(self) -> object:
        with self._lock:
            return self._snapshot_stream.current_snapshot()

    def pop_snapshots(self) -> tuple[object, ...]:
        with self._lock:
            return self._snapshot_stream.pop_pending()

    def snapshots(self) -> tuple[object, ...]:
        with self._lock:
            return self._snapshot_stream.pending()

    def _run_until(self, target: float | None) -> tuple[SimEvent, ...]:
        kernel = self._require_kernel()
        observer = self._tick_observer
        try:
            if observer is not None:
                observer.reset()
            events = kernel.run(until_time=target)
            self._processed_events.extend(events)
            snapshot_started = perf_counter()
            self._snapshot_stream.ingest(events)
            if events and _queued_event_count(kernel) == 0:
                self._snapshot_stream.flush()
                if self._lifecycle_state == RuntimeLifecycleState.RUNNING:
                    self._lifecycle_state = RuntimeLifecycleState.COMPLETED
            snapshot_projection_time_ms = (perf_counter() - snapshot_started) * 1000.0
            if observer is not None:
                self._last_profiling_summary = observer.summary(
                    snapshot_projection_time_ms=snapshot_projection_time_ms,
                    processed_event_count=len(events),
                )
            return events
        except Exception as exc:
            self._last_error = str(exc)
            self._lifecycle_state = RuntimeLifecycleState.ERROR
            raise

    def _require_kernel(self) -> KernelPort:
        if self._kernel is None:
            raise RuntimeError("session is not initialized")
        return self._kernel

    def _current_sim_time(self) -> float:
        if self._kernel is None:
            return 0.0
        return self._kernel.get_current_time()


def _queued_event_count(kernel: KernelPort | None) -> int | None:
    if kernel is None:
        return None
    count_attr = getattr(kernel, "queued_event_count", None)
    if callable(count_attr):
        value = count_attr()
        return int(value) if value is not None else None
    if isinstance(count_attr, int):
        return count_attr
    queue = getattr(kernel, "_event_queue", None)
    heap = getattr(queue, "_heap", None)
    if isinstance(heap, list):
        return len(heap)
    return None


def _backpressure_summary(
    *,
    profiling: dict[str, object],
    tick_duration_ms: float,
    tick_budget_ms: float,
    queue_depth: int,
    processed_event_count: int,
    first_tick: bool,
) -> dict[str, object]:
    overloaded = tick_duration_ms > tick_budget_ms
    bottleneck_component = _bottleneck_component(profiling)
    return {
        "tick_duration_ms": round(max(0.0, tick_duration_ms), 6),
        "tick_budget_ms": round(max(0.0, tick_budget_ms), 6),
        "overloaded": overloaded,
        "queue_depth": int(queue_depth),
        "processed_event_count": int(processed_event_count),
        "deferred_event_count": int(queue_depth),
        "first_tick_heavy": bool(first_tick and overloaded),
        "bottleneck_component": bottleneck_component,
        "recommended_action": _recommended_action(overloaded, bottleneck_component),
    }


def _bottleneck_component(profiling: dict[str, object]) -> str:
    candidates: dict[str, float] = {}
    for key in PROFILE_TIMING_FIELDS:
        if key == "total_tick_time_ms" or not key.endswith("_time_ms"):
            continue
        value = profiling.get(key, 0.0)
        if isinstance(value, (int, float)):
            candidates[key.removesuffix("_time_ms")] = float(value)
    if not candidates:
        return "none"
    component, elapsed_ms = max(
        candidates.items(),
        key=lambda item: (item[1], item[0]),
    )
    return component if elapsed_ms > 0.0 else "none"


def _recommended_action(overloaded: bool, bottleneck_component: str) -> str:
    if not overloaded:
        return "none"
    if bottleneck_component in {
        "flow_arrival_processing",
        "compute_task_arrival_processing",
        "compute_queue_update",
    }:
        return "widen_initial_workload_smoothing_window"
    if bottleneck_component == "space_space_candidate_update":
        return "reduce_space_link_candidate_cap_or_keep_bounded_mode"
    if bottleneck_component == "snapshot_projection":
        return "lower_snapshot_frequency_or_stream_batch_size"
    return "keep_scale_mode_enabled_or_reduce_scenario_scale"
