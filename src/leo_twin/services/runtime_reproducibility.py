"""Deterministic runtime reproducibility manifest helpers."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import fields, is_dataclass
from enum import Enum
from math import isfinite
from typing import Any


JsonValue = None | str | int | float | bool | list["JsonValue"] | dict[str, "JsonValue"]

_LIVE_STATUS_ARTIFACTS: tuple[dict[str, str], ...] = (
    {
        "name": "config_snapshot.json",
        "format": "json",
        "status": "EMBEDDED_IN_RUNTIME_STATUS",
        "source": "runtime_status.generated_config",
    },
    {
        "name": "events.jsonl",
        "format": "jsonl",
        "status": "AVAILABLE_FOR_BATCH_EXPORT",
        "source": "MetricsCollector.write_outputs",
    },
    {
        "name": "metrics.csv",
        "format": "csv",
        "status": "AVAILABLE_FOR_BATCH_EXPORT",
        "source": "MetricsCollector.write_outputs",
    },
    {
        "name": "summary.json",
        "format": "json",
        "status": "AVAILABLE_FOR_BATCH_EXPORT",
        "source": "MetricsCollector.write_outputs",
    },
)

_RUNTIME_STATE_KEYS = (
    "session_id",
    "lifecycle_state",
    "status",
    "mode",
    "speed_factor",
    "seed",
    "duration",
    "config_version",
    "last_action",
    "initialized",
    "current_sim_time",
    "processed_event_count",
    "queued_event_count",
    "deterministic_replay",
)


def stable_hash_payload(value: object) -> str:
    """Return a SHA-256 hash for a canonical JSON representation."""

    payload = stable_json_payload(value)
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(encoded).hexdigest()}"


def stable_json_payload(value: object) -> JsonValue:
    """Convert supported Python values to deterministic JSON-compatible data."""

    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not isfinite(value):
            raise ValueError("floating-point values must be finite")
        return value
    if isinstance(value, Enum):
        return stable_json_payload(value.value)
    if is_dataclass(value) and not isinstance(value, type):
        return {
            field.name: stable_json_payload(getattr(value, field.name))
            for field in fields(value)
        }
    if isinstance(value, Mapping):
        return {
            str(key): stable_json_payload(value[key])
            for key in sorted(value, key=lambda item: str(item))
        }
    if isinstance(value, tuple | list):
        return [stable_json_payload(item) for item in value]
    raise TypeError(f"value is not deterministic JSON serializable: {type(value).__name__}")


def build_runtime_reproducibility_manifest(
    *,
    session_id: str,
    runtime_status: Mapping[str, Any],
    control_config: Mapping[str, Any],
    generated_config: Mapping[str, Any],
    metrics_summary: Mapping[str, Any] | None = None,
) -> dict[str, JsonValue]:
    """Build a backend-owned manifest describing how a live run can be replayed."""

    runtime_state = _runtime_state(runtime_status, session_id)
    scenario_config = _without_keys(generated_config, {"backend_summary"})
    metrics_payload: Mapping[str, Any] = {} if metrics_summary is None else metrics_summary
    base_manifest: dict[str, JsonValue] = {
        "version": "v1",
        "source": "BACKEND_RUNTIME_STATUS",
        "manifest_id": "leo_twin.runtime_reproducibility_manifest.v1",
        "session_id": session_id,
        "seed": runtime_state.get("seed"),
        "duration_s": runtime_state.get("duration"),
        "runtime_mode": runtime_state.get("mode"),
        "speed_factor": runtime_state.get("speed_factor"),
        "config_version": runtime_state.get("config_version"),
        "deterministic_replay": runtime_state.get("deterministic_replay"),
        "runtime_state": stable_json_payload(runtime_state),
        "scenario_hash": stable_hash_payload(scenario_config),
        "control_config_hash": stable_hash_payload(control_config),
        "generated_config_hash": stable_hash_payload(generated_config),
        "metrics_summary_hash": stable_hash_payload(metrics_payload),
        "runtime_state_hash": stable_hash_payload(runtime_state),
        "artifact_policy": "LIVE_STATUS_MANIFEST_ONLY",
        "artifact_policy_note": (
            "Live runtime status exposes deterministic hashes and artifact "
            "availability; file package export is a separate batch path."
        ),
        "artifacts": stable_json_payload(_LIVE_STATUS_ARTIFACTS),
        "artifact_count": len(_LIVE_STATUS_ARTIFACTS),
        "excluded_runtime_fields": ["wall_clock_start_time"],
        "notes": [
            "Event Kernel ordering is unchanged.",
            "Live mode is reproducible through deterministic config and event outputs.",
            "Batch exports use events.jsonl, metrics.csv, and summary.json.",
        ],
    }
    base_manifest["manifest_hash"] = stable_hash_payload(base_manifest)
    return base_manifest


def _runtime_state(
    runtime_status: Mapping[str, Any],
    session_id: str,
) -> dict[str, Any]:
    state = {
        key: runtime_status[key]
        for key in _RUNTIME_STATE_KEYS
        if key in runtime_status
    }
    state["session_id"] = session_id
    return state


def _without_keys(
    value: Mapping[str, Any],
    excluded_keys: set[str],
) -> dict[str, Any]:
    return {
        str(key): value[key]
        for key in sorted(value, key=lambda item: str(item))
        if str(key) not in excluded_keys
    }
