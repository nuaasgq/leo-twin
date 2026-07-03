"""Control-plane integration for the full-system demo backend."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from leo_twin.services.control import (
    RuntimeController,
    control_error,
    parse_control_message,
)

from examples.integration_demo.config import (
    DemoConfig,
    demo_config_from_sees_config,
    demo_config_to_sees_config,
)
from examples.integration_demo.runtime import DemoRunResult, run_integration_demo


@dataclass
class DemoControlPlane:
    """Own the mutable control-plane state for a demo server instance."""

    _base_config: DemoConfig
    _result: DemoRunResult
    _controller: RuntimeController

    @classmethod
    def from_result(cls, result: DemoRunResult) -> "DemoControlPlane":
        controller = RuntimeController(demo_config_to_sees_config(result.config))
        return cls(
            _base_config=result.config,
            _result=result,
            _controller=controller,
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
        }

    def handle_raw_message(self, raw: str | bytes) -> dict[str, Any]:
        try:
            message = parse_control_message(raw)
            if message.type.value == "CONFIG_UPDATE":
                snapshot = self._controller.update_config(message.payload)
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
                }
            if message.action is None:
                raise ValueError("runtime control message requires an action")
            snapshot = self._controller.handle_action(message.action, message.payload)
            return {
                "type": "CONTROL_ACK",
                "ok": True,
                "status": snapshot.to_json(),
                "config": self._controller.config_json(),
            }
        except Exception as exc:  # noqa: BLE001 - returned as protocol error
            return control_error(exc)
