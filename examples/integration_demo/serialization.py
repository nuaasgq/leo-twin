"""Deterministic JSON serialization for demo events and snapshots."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import fields, is_dataclass
from typing import Any

from leo_twin.schema import EventType, SimEvent


JsonValue = None | str | int | float | bool | list["JsonValue"] | dict[str, "JsonValue"]


def event_to_json(event: SimEvent) -> dict[str, JsonValue]:
    return {
        "event_id": _json_value(event.event_id),
        "sim_time": event.sim_time,
        "priority": event.priority,
        "source": event.source,
        "target": event.target,
        "event_type": str(event.event_type),
        "payload": _json_value(event.payload),
    }


def stable_json(value: JsonValue) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def stable_json_pretty(value: JsonValue) -> str:
    return json.dumps(value, sort_keys=True, indent=2) + "\n"


def events_jsonl(events: tuple[SimEvent, ...]) -> str:
    return "\n".join(stable_json(event_to_json(event)) for event in events) + "\n"


def _json_value(value: Any) -> JsonValue:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, EventType):
        return value.value
    if is_dataclass(value) and not isinstance(value, type):
        return {
            field.name: _json_value(getattr(value, field.name))
            for field in fields(value)
        }
    if isinstance(value, Mapping):
        return {
            str(key): _json_value(value[key])
            for key in sorted(value, key=lambda item: str(item))
        }
    if isinstance(value, tuple | list):
        return [_json_value(item) for item in value]
    raise TypeError(f"value is not JSON serializable for demo replay: {type(value).__name__}")
