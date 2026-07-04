"""Control-plane integration for the full-system demo backend."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from leo_twin.schema.config_loader import write_config
from leo_twin.services.control import RuntimeAction, RuntimeStatus
from leo_twin.services.control import (
    RuntimeController,
    ScaleSafetyChecker,
    control_error,
    parse_control_message,
)
from leo_twin.services.scenario_builder import (
    scenario_builder_config_from_sees_config,
    scenario_builder_config_to_mapping,
    write_full_system_scenario_builder_config,
)

from examples.integration_demo.config import (
    DemoConfig,
    demo_config_from_sees_config,
    demo_config_to_sees_config,
)
from examples.integration_demo.runtime import DemoRunResult, run_integration_demo
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
        return cls(
            _base_config=result.config,
            _result=result,
            _controller=controller,
            _config_output_path=Path(config_output_path),
            _generated_config_output_path=Path(generated_config_output_path),
        )

    @property
    def result(self) -> DemoRunResult:
        return self._result

    @property
    def controller(self) -> RuntimeController:
        return self._controller

    def runtime_status(self) -> dict[str, Any]:
        return {
            "type": "RUNTIME_STATUS",
            "status": self._controller.snapshot().to_json(),
            "config": self._controller.config_json(),
            "generated_config": self._generated_config_json(),
        }

    def visible_snapshot(self) -> dict[str, JsonValue]:
        if self._controller.snapshot().status == RuntimeStatus.RUNNING:
            return self._result.final_snapshot
        return _initial_snapshot(self._result)

    def stream_events(self) -> tuple[dict[str, JsonValue], ...]:
        if self._controller.snapshot().status != RuntimeStatus.RUNNING:
            return ()
        return tuple(
            event_to_json(event)
            for event in self._result.processed_events
            if str(event.event_type) in _FRONTEND_EVENT_TYPES
        )

    def stream_snapshots(self) -> tuple[dict[str, JsonValue], ...]:
        if self._controller.snapshot().status != RuntimeStatus.RUNNING:
            return ()
        return self._result.state_timeline

    def handle_raw_message(self, raw: str | bytes) -> dict[str, Any]:
        try:
            message = parse_control_message(raw)
            if message.type.value == "CONFIG_UPDATE":
                return self._initialize(message.payload)
            if message.action is None:
                raise ValueError("runtime control message requires an action")
            if message.action == RuntimeAction.INITIALIZE:
                return self._initialize(message.payload)
            snapshot = self._controller.handle_action(message.action, message.payload)
            return {
                "type": "CONTROL_ACK",
                "ok": True,
                "status": snapshot.to_json(),
                "config": self._controller.config_json(),
                "generated_config": self._generated_config_json(),
            }
        except Exception as exc:  # noqa: BLE001 - returned as protocol error
            return control_error(exc)

    def _initialize(self, payload: dict[str, Any]) -> dict[str, Any]:
        snapshot = self._controller.initialize(payload)
        write_config(self._config_output_path, self._controller.config)
        write_full_system_scenario_builder_config(
            self._generated_config_output_path,
            scenario_builder_config_from_sees_config(self._controller.config),
        )
        updated_demo_config = demo_config_from_sees_config(
            self._controller.config,
            self._base_config,
        )
        self._result = run_integration_demo(updated_demo_config)
        return {
            "type": "CONTROL_ACK",
            "ok": True,
            "status": snapshot.to_json(),
            "config": self._controller.config_json(),
            "generated_config": self._generated_config_json(),
        }

    def _generated_config_json(self) -> dict[str, int | float | str]:
        return scenario_builder_config_to_mapping(
            scenario_builder_config_from_sees_config(self._controller.config)
        )


def _initial_snapshot(result: DemoRunResult) -> dict[str, JsonValue]:
    return {
        "satellites": [],
        "ground_users": [
            {
                "user_id": user.user_id,
                "cell_id": user.cell_id,
                "position": list(user.position),
                "status": user.status,
            }
            for user in sorted(
                result.scenario.ground_user_render_states,
                key=lambda item: item.user_id,
            )
        ],
        "links": [],
        "routes": [],
        "tasks": [],
        "compute_nodes": [],
        "metrics": [],
        "event_count": 0,
        "last_sim_time": 0.0,
    }
