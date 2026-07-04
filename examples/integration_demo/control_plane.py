"""Control-plane integration for the full-system demo backend."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from leo_twin.runtime import (
    ControlCommand,
    RuntimeCommand,
    RuntimeKernelSpec,
    RuntimeLifecycleState,
    SessionAdvanceLoop,
    SimulationController,
    SimulationSession,
    StreamBackpressurePolicy,
    StreamBuffer,
    parse_control_command,
)
from leo_twin.schema.config_loader import write_config
from leo_twin.services.control import (
    RuntimeController,
    ScaleSafetyChecker,
)
from leo_twin.services.scenario_builder import (
    scenario_builder_backend_summary,
    scenario_builder_config_from_sees_config,
    scenario_builder_config_to_mapping,
    write_full_system_scenario_builder_config,
)

from examples.integration_demo.config import (
    DemoConfig,
    demo_config_from_sees_config,
    demo_config_to_sees_config,
)
from examples.integration_demo.replay import DemoStateProjector
from examples.integration_demo.runtime import (
    DemoRunResult,
    DemoRuntimeContext,
    build_integration_demo_runtime,
    finalize_integration_demo_run,
    run_integration_demo,
)
from examples.integration_demo.serialization import JsonValue, event_to_json


_FRONTEND_EVENT_TYPES = frozenset(
    {
        "ORBIT_UPDATE",
        "LINK_UPDATE",
        "ACCESS_START",
        "ACCESS_END",
        "ROUTE_UPDATE",
        "TASK_START",
        "TASK_FINISH",
        "COMPUTE_NODE_UPDATE",
        "METRIC_SAMPLE",
    }
)


@dataclass
class DemoControlPlane:
    """Own the mutable control-plane state for a demo server instance."""

    _base_config: DemoConfig
    _result: DemoRunResult
    _controller: RuntimeController
    _config_output_path: Path
    _generated_config_output_path: Path
    _session: SimulationSession | None = None
    _runtime_adapter: SimulationController | None = None
    _runtime_context: DemoRuntimeContext | None = None
    _advance_loop: SessionAdvanceLoop | None = None
    _initialized: bool = False

    @classmethod
    def from_result(
        cls,
        result: DemoRunResult,
        config_output_path: str | Path = "configs/sees_control.yaml",
        generated_config_output_path: str | Path = "configs/generated_full_system_demo.json",
    ) -> "DemoControlPlane":
        controller = RuntimeController(
            demo_config_to_sees_config(result.config),
            scale_safety_checker=ScaleSafetyChecker(),
        )
        control_plane = cls(
            _base_config=result.config,
            _result=result,
            _controller=controller,
            _config_output_path=Path(config_output_path),
            _generated_config_output_path=Path(generated_config_output_path),
        )
        control_plane._install_runtime_session(result.config)
        return control_plane

    @property
    def result(self) -> DemoRunResult:
        return self._result

    @property
    def controller(self) -> RuntimeController:
        return self._controller

    def runtime_status(self) -> dict[str, Any]:
        return {
            "type": "RUNTIME_STATUS",
            "status": self._status_json(),
            "config": self._controller.config_json(),
            "generated_config": self._generated_config_json(),
        }

    def visible_snapshot(self) -> dict[str, JsonValue]:
        session = self._require_session()
        if self._initialized and session.lifecycle_state in {
            RuntimeLifecycleState.RUNNING,
            RuntimeLifecycleState.PAUSED,
            RuntimeLifecycleState.COMPLETED,
        }:
            return session.get_snapshot()  # type: ignore[return-value]
        return _initial_snapshot(self._result)

    def stream_events(self) -> tuple[dict[str, JsonValue], ...]:
        if not self._initialized or self._controller.snapshot().status != "RUNNING":
            return ()
        self._require_advance_loop().publish_pending()
        batch = self._require_advance_loop().event_stream.read_after(0)
        return tuple(
            event_to_json(event)
            for event in batch.items
            if str(event.event_type) in _FRONTEND_EVENT_TYPES
        )

    def stream_snapshots(self) -> tuple[dict[str, JsonValue], ...]:
        if not self._initialized or self._controller.snapshot().status != "RUNNING":
            return ()
        loop = self._require_advance_loop()
        loop.publish_pending()
        snapshots = loop.snapshot_stream.read_after(0).items
        if not snapshots:
            snapshots = (self._require_runtime_adapter().snapshot(),)
        return snapshots  # type: ignore[return-value]

    def stream_event_batch(
        self,
        cursor: int = 0,
        limit: int | None = None,
    ) -> dict[str, Any]:
        self._require_advance_loop().publish_pending()
        return _frontend_event_batch(
            self._require_advance_loop().event_stream,
            cursor,
            limit,
        )

    def stream_snapshot_batch(
        self,
        cursor: int = 0,
        limit: int | None = None,
    ) -> dict[str, Any]:
        self._require_advance_loop().publish_pending()
        return self._require_advance_loop().snapshot_stream.read_after(
            cursor,
            limit=limit,
        ).to_dict()

    def handle_raw_message(self, raw: str | bytes) -> dict[str, Any]:
        command_name = "UNKNOWN"
        try:
            command = parse_control_command(raw)
            command_name = command.command.value
            if command.command == RuntimeCommand.INITIALIZE:
                return self._initialize(command.payload)
            if command.command == RuntimeCommand.START and not self._initialized:
                raise RuntimeError("simulation must be initialized before start")
            if command.command == RuntimeCommand.REQUEST_STATUS:
                return self._ack(command)
            if command.command == RuntimeCommand.REQUEST_SNAPSHOT:
                response = self._ack(command)
                response["snapshot"] = self.visible_snapshot()
                return response
            if command.command == RuntimeCommand.RESET:
                return self._reset(command.payload)

            self._controller.handle_action(command.command.value, command.payload)
            if command.command == RuntimeCommand.START:
                self._require_session().start_live()
                runtime_ack = {"ok": True}
            elif command.command == RuntimeCommand.RESUME:
                self._require_session().resume_live()
                runtime_ack = {"ok": True}
            else:
                runtime_ack = self._require_runtime_adapter().handle_raw_message(
                    {"command": command.command.value, "payload": command.payload}
                )
            if not runtime_ack["ok"]:
                return self._nack(command_name, str(runtime_ack["error"]))
            if command.command == RuntimeCommand.START:
                self._require_advance_loop().publish_pending()
                response = self._ack(command)
                self._require_advance_loop().start()
                return response
            if command.command == RuntimeCommand.RESUME:
                self._require_advance_loop().publish_pending()
                response = self._ack(command)
                self._require_advance_loop().start()
                return response
            if command.command == RuntimeCommand.PAUSE:
                self._require_advance_loop().publish_pending()
            if command.command == RuntimeCommand.STOP:
                loop = self._require_advance_loop()
                loop.stop()
                loop.publish_pending()
            return self._ack(command)
        except Exception as exc:  # noqa: BLE001 - returned as protocol error
            return self._nack(command_name, str(exc))

    def _initialize(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._stop_advance_loop()
        self._controller.initialize(payload)
        write_config(self._config_output_path, self._controller.config)
        write_full_system_scenario_builder_config(
            self._generated_config_output_path,
            scenario_builder_config_from_sees_config(self._controller.config),
        )
        updated_demo_config = demo_config_from_sees_config(
            self._controller.config,
            self._base_config,
        )
        self._install_runtime_session(updated_demo_config)
        if self._runtime_context is not None:
            self._result = finalize_integration_demo_run(self._runtime_context, ())
        self._initialized = True
        return self._ack(ControlCommand(RuntimeCommand.INITIALIZE, payload))

    def _reset(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._stop_advance_loop()
        if self._advance_loop is not None:
            self._advance_loop.reset_streams()
        self._controller.handle_action(RuntimeCommand.RESET.value, payload)
        reset_demo_config = demo_config_from_sees_config(
            self._controller.config,
            self._base_config,
        )
        self._install_runtime_session(reset_demo_config)
        if self._runtime_context is not None:
            self._result = finalize_integration_demo_run(self._runtime_context, ())
        self._initialized = False
        return self._ack(ControlCommand(RuntimeCommand.RESET, payload))

    def _install_runtime_session(self, config: DemoConfig) -> None:
        self._stop_advance_loop()
        sees_config = demo_config_to_sees_config(config)

        def kernel_factory(
            _scenario_config: object,
            _runtime_config: object,
        ) -> RuntimeKernelSpec:
            context = build_integration_demo_runtime(config)
            self._runtime_context = context
            return RuntimeKernelSpec(
                kernel=context.kernel,
                initial_events=context.scenario.initial_events,
                snapshot_projector=DemoStateProjector(
                    context.scenario.ground_user_render_states,
                    config.state_snapshot_interval_events,
                ),
                initial_snapshot=_initial_snapshot_from_ground_users(
                    context.scenario.ground_user_render_states
                ),
            )

        session = SimulationSession(
            session_id=f"integration-demo-{config.seed}",
            runtime_config=sees_config.runtime,
            scenario_config=sees_config.scenario,
            kernel_factory=kernel_factory,  # type: ignore[arg-type]
            snapshot_interval_events=config.state_snapshot_interval_events,
            deterministic_replay=False,
            control_step_seconds=1.0,
        )
        session.initialize()
        self._session = session
        self._runtime_adapter = SimulationController(session)
        self._advance_loop = SessionAdvanceLoop(
            session,
            stream_policy=StreamBackpressurePolicy(
                max_items=100_000,
                max_batch_size=100_000,
            ),
            tick_interval_seconds=0.01,
        )

    def advance_loop_snapshot(self) -> dict[str, Any]:
        return self._require_advance_loop().snapshot().to_dict()

    def runtime_lifecycle_state(self) -> RuntimeLifecycleState:
        return self._require_session().lifecycle_state

    def _stop_advance_loop(self) -> None:
        if self._advance_loop is not None:
            self._advance_loop.stop()

    def _generated_config_json(self) -> dict[str, Any]:
        builder_config = scenario_builder_config_from_sees_config(self._controller.config)
        generated = scenario_builder_config_to_mapping(builder_config)
        generated["backend_summary"] = scenario_builder_backend_summary(builder_config)
        return generated

    def _status_json(self) -> dict[str, str | int | float | bool | None]:
        runtime_status = self._require_session().get_status().to_dict()
        status = dict(runtime_status)
        status.update(self._controller.snapshot().to_json())
        status["lifecycle_state"] = runtime_status["lifecycle_state"]
        status["current_sim_time"] = runtime_status["current_sim_time"]
        status["wall_clock_start_time"] = runtime_status["wall_clock_start_time"]
        status["processed_event_count"] = runtime_status["processed_event_count"]
        status["queued_event_count"] = runtime_status["queued_event_count"]
        status["last_error"] = runtime_status["last_error"]
        status["deterministic_replay"] = runtime_status["deterministic_replay"]
        status["initialized"] = self._initialized
        return status

    def _ack(self, command: ControlCommand) -> dict[str, Any]:
        return {
            "type": "CONTROL_ACK",
            "ok": True,
            "command": command.command.value,
            "status": self._status_json(),
            "config": self._controller.config_json(),
            "generated_config": self._generated_config_json(),
        }

    def _nack(self, command: str, error: str) -> dict[str, Any]:
        return {
            "type": "CONTROL_ACK",
            "ok": False,
            "command": command,
            "status": self._status_json(),
            "error": error,
        }

    def _require_session(self) -> SimulationSession:
        if self._session is None:
            raise RuntimeError("runtime session is not installed")
        return self._session

    def _require_runtime_adapter(self) -> SimulationController:
        if self._runtime_adapter is None:
            raise RuntimeError("runtime adapter is not installed")
        return self._runtime_adapter

    def _require_advance_loop(self) -> SessionAdvanceLoop:
        if self._advance_loop is None:
            raise RuntimeError("runtime advance loop is not installed")
        return self._advance_loop


def _initial_snapshot(result: DemoRunResult) -> dict[str, JsonValue]:
    return _initial_snapshot_from_ground_users(result.scenario.ground_user_render_states)


def _initial_snapshot_from_ground_users(ground_users: tuple[Any, ...]) -> dict[str, JsonValue]:
    return {
        "satellites": [],
        "ground_users": [
            {
                "user_id": user.user_id,
                "cell_id": user.cell_id,
                "position": list(user.position),
                "status": user.status,
            }
            for user in sorted(ground_users, key=lambda item: item.user_id)
        ],
        "links": [],
        "routes": [],
        "tasks": [],
        "compute_nodes": [],
        "metrics": [],
        "event_count": 0,
        "last_sim_time": 0.0,
    }


def _frontend_event_batch(
    stream: StreamBuffer[Any],
    cursor: int,
    limit: int | None,
) -> dict[str, Any]:
    selected_limit = stream.policy.max_batch_size if limit is None else min(
        limit,
        stream.policy.max_batch_size,
    )
    if selected_limit <= 0:
        raise ValueError("limit must be positive")
    items: list[dict[str, JsonValue]] = []
    next_cursor = cursor
    overflow = False
    dropped_count = 0
    first_read = True
    while len(items) < selected_limit:
        batch = stream.read_after(next_cursor, limit=selected_limit)
        if first_read:
            overflow = batch.overflow
            dropped_count = batch.dropped_count
            first_read = False
        if batch.next_cursor == next_cursor:
            break
        next_cursor = batch.next_cursor
        for event in batch.items:
            if str(event.event_type) in _FRONTEND_EVENT_TYPES:
                items.append(event_to_json(event))
                if len(items) >= selected_limit:
                    break
        if len(batch.items) < selected_limit:
            break
    return {
        "items": items,
        "cursor": cursor,
        "next_cursor": next_cursor,
        "overflow": overflow,
        "dropped_count": dropped_count,
    }
