"""Stable command protocol for runtime sessions."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from leo_twin.runtime.session import SimulationSession


class RuntimeCommand(StrEnum):
    """Commands accepted by the product runtime control surface."""

    INITIALIZE = "INITIALIZE"
    START = "START"
    PAUSE = "PAUSE"
    RESUME = "RESUME"
    STOP = "STOP"
    RESET = "RESET"
    SET_SPEED = "SET_SPEED"
    SET_MODE = "SET_MODE"
    LOAD_TEMPLATE = "LOAD_TEMPLATE"
    REQUEST_STATUS = "REQUEST_STATUS"
    REQUEST_SNAPSHOT = "REQUEST_SNAPSHOT"


class ControlProtocolError(ValueError):
    """Raised when a control command is malformed."""


@dataclass(frozen=True)
class ControlCommand:
    """Validated runtime control command."""

    command: RuntimeCommand
    payload: dict[str, Any]


class ControlProtocol:
    """Apply validated control commands to a simulation session."""

    def __init__(self, session: SimulationSession) -> None:
        self._session = session

    def handle(self, raw: str | bytes | Mapping[str, Any] | ControlCommand) -> dict[str, Any]:
        command_name = "UNKNOWN"
        try:
            command = raw if isinstance(raw, ControlCommand) else parse_control_command(raw)
            command_name = command.command.value
            payload = command.payload
            if command.command == RuntimeCommand.INITIALIZE:
                self._session.initialize()
            elif command.command == RuntimeCommand.START:
                self._session.start()
            elif command.command == RuntimeCommand.PAUSE:
                self._session.pause()
            elif command.command == RuntimeCommand.RESUME:
                self._session.resume()
            elif command.command == RuntimeCommand.STOP:
                self._session.stop()
            elif command.command == RuntimeCommand.RESET:
                self._session.reset()
            elif command.command == RuntimeCommand.SET_SPEED:
                self._session.set_speed_factor(_payload_float(payload, "speed_factor"))
            elif command.command == RuntimeCommand.SET_MODE:
                self._session.set_mode(str(_payload_value(payload, "mode")))
            elif command.command == RuntimeCommand.REQUEST_STATUS:
                pass
            elif command.command == RuntimeCommand.REQUEST_SNAPSHOT:
                pass
            else:
                raise ControlProtocolError(f"unsupported command: {command.command}")
            response: dict[str, Any] = {
                "type": "CONTROL_ACK",
                "ok": True,
                "command": command.command.value,
                "status": self._session.get_status().to_dict(),
            }
            if command.command == RuntimeCommand.REQUEST_SNAPSHOT:
                response["snapshot"] = self._session.get_snapshot()
            return response
        except Exception as exc:  # noqa: BLE001 - protocol must convert failures to NACK
            return {
                "type": "CONTROL_ACK",
                "ok": False,
                "command": command_name,
                "status": self._session.get_status().to_dict(),
                "error": str(exc),
            }


def parse_control_command(raw: str | bytes | Mapping[str, Any]) -> ControlCommand:
    data = _decode_raw(raw)
    payload = data.get("payload", {})
    if not isinstance(payload, Mapping):
        raise ControlProtocolError("control payload must be a mapping")

    if data.get("type") == "CONFIG_UPDATE":
        return ControlCommand(RuntimeCommand.INITIALIZE, dict(payload))

    raw_command = data.get("command", data.get("action"))
    if raw_command is None and data.get("type") == "RUNTIME_CONTROL":
        raise ControlProtocolError("RUNTIME_CONTROL requires action or command")
    if raw_command is None:
        raise ControlProtocolError("runtime control message requires command")
    try:
        command = RuntimeCommand(str(raw_command))
    except ValueError as exc:
        raise ControlProtocolError(f"unsupported runtime command: {raw_command}") from exc
    return ControlCommand(command, dict(payload))


def _decode_raw(raw: str | bytes | Mapping[str, Any]) -> Mapping[str, Any]:
    if isinstance(raw, Mapping):
        return raw
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8")
    if not isinstance(raw, str):
        raise ControlProtocolError("control message must be JSON text or a mapping")
    value = json.loads(raw)
    if not isinstance(value, Mapping):
        raise ControlProtocolError("control message root must be a mapping")
    return value


def _payload_value(payload: Mapping[str, Any], key: str) -> Any:
    if key not in payload:
        raise ControlProtocolError(f"{key} is required")
    return payload[key]


def _payload_float(payload: Mapping[str, Any], key: str) -> float:
    value = _payload_value(payload, key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ControlProtocolError(f"{key} must be numeric")
    return float(value)
