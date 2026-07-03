"""WebSocket control message protocol for SEES runtime control."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from leo_twin.services.control.runtime import RuntimeAction, RuntimeController


class ControlMessageType(StrEnum):
    """Supported control channel message types."""

    CONFIG_UPDATE = "CONFIG_UPDATE"
    RUNTIME_CONTROL = "RUNTIME_CONTROL"


class ControlProtocolError(ValueError):
    """Raised when a control message is malformed or unsupported."""


@dataclass(frozen=True)
class ControlMessage:
    """Validated control channel message."""

    type: ControlMessageType
    payload: dict[str, Any]
    action: RuntimeAction | None = None


def parse_control_message(raw: str | bytes | Mapping[str, Any]) -> ControlMessage:
    """Parse and validate a control-channel message."""

    data = _decode_raw(raw)
    message_type = ControlMessageType(str(data.get("type", "")))
    payload = data.get("payload", {})
    if not isinstance(payload, Mapping):
        raise ControlProtocolError("control message payload must be a mapping")
    if message_type == ControlMessageType.CONFIG_UPDATE:
        return ControlMessage(
            type=message_type,
            payload=dict(payload),
        )
    if message_type == ControlMessageType.RUNTIME_CONTROL:
        raw_action = data.get("action")
        if raw_action is None:
            raise ControlProtocolError("RUNTIME_CONTROL requires an action")
        return ControlMessage(
            type=message_type,
            payload=dict(payload),
            action=RuntimeAction(str(raw_action)),
        )
    raise ControlProtocolError(f"unsupported control message type: {message_type}")


def handle_control_message(
    controller: RuntimeController,
    message: ControlMessage,
) -> dict[str, Any]:
    """Apply a validated message to a runtime controller and return an ACK."""

    if message.type == ControlMessageType.CONFIG_UPDATE:
        snapshot = controller.update_config(message.payload)
    elif message.type == ControlMessageType.RUNTIME_CONTROL:
        if message.action is None:
            raise ControlProtocolError("RUNTIME_CONTROL requires an action")
        snapshot = controller.handle_action(message.action, message.payload)
    else:
        raise ControlProtocolError(f"unsupported control message type: {message.type}")
    return {
        "type": "CONTROL_ACK",
        "ok": True,
        "status": snapshot.to_json(),
        "config": controller.config_json(),
    }


def control_error(error: Exception) -> dict[str, Any]:
    """Return a deterministic error response for the control channel."""

    return {
        "type": "CONTROL_ACK",
        "ok": False,
        "error": str(error),
    }


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
