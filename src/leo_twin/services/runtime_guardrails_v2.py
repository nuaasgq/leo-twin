"""Runtime guardrails v2 for scale-aware execution explanations."""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil
from typing import Any, Literal, Mapping

from leo_twin.runtime.stream_buffer import StreamBackpressurePolicy
from leo_twin.services.control.scale_safety import ScaleConfig, ScaleSafetyChecker
from leo_twin.services.lod_snapshot_policy import lod_snapshot_policy_v2_to_dict
from leo_twin.services.scale_policy_v2 import scale_policy_v2_to_dict


RUNTIME_GUARDRAILS_V2_ID = "leo_twin.runtime_guardrails.v2"
RuntimeGuardrailDecision = Literal["ALLOW", "DEGRADE", "REFUSE"]


@dataclass(frozen=True)
class RuntimeGuardrailConfigV2:
    """Inputs for deterministic runtime guardrail estimation."""

    satellite_count: int
    user_count: int
    compute_node_count: int
    simulation_duration_seconds: float
    tick_interval_seconds: float = 1.0
    average_events_per_entity_per_tick: float = 0.1
    partition_count: int = 100
    event_stream_max_items: int = StreamBackpressurePolicy().max_items
    state_stream_max_items: int = StreamBackpressurePolicy().max_items
    stream_max_batch_size: int = StreamBackpressurePolicy().max_batch_size
    snapshot_interval_events: int = 10_000
    max_event_count: int = 1_000_000
    max_memory_bytes: int = 512 * 1024 * 1024

    def __post_init__(self) -> None:
        _require_positive_int(self.satellite_count, "satellite_count")
        _require_non_negative_int(self.user_count, "user_count")
        _require_positive_int(self.compute_node_count, "compute_node_count")
        _require_positive_float(
            self.simulation_duration_seconds,
            "simulation_duration_seconds",
        )
        _require_positive_float(self.tick_interval_seconds, "tick_interval_seconds")
        _require_non_negative_float(
            self.average_events_per_entity_per_tick,
            "average_events_per_entity_per_tick",
        )
        _require_positive_int(self.partition_count, "partition_count")
        _require_positive_int(self.event_stream_max_items, "event_stream_max_items")
        _require_positive_int(self.state_stream_max_items, "state_stream_max_items")
        _require_positive_int(self.stream_max_batch_size, "stream_max_batch_size")
        _require_positive_int(self.snapshot_interval_events, "snapshot_interval_events")
        _require_positive_int(self.max_event_count, "max_event_count")
        _require_positive_int(self.max_memory_bytes, "max_memory_bytes")


def runtime_guardrails_v2_to_dict(
    config: RuntimeGuardrailConfigV2,
    *,
    scale_policy: Mapping[str, Any] | None = None,
    lod_snapshot_policy: Mapping[str, Any] | None = None,
) -> dict[str, object]:
    """Return backend-owned runtime guardrail estimates and decisions."""

    if not isinstance(config, RuntimeGuardrailConfigV2):
        raise TypeError("config must be RuntimeGuardrailConfigV2")
    resolved_scale_policy = (
        dict(scale_policy)
        if scale_policy is not None
        else scale_policy_v2_to_dict(
            satellite_count=config.satellite_count,
            user_count=config.user_count,
        )
    )
    resolved_lod_policy = (
        dict(lod_snapshot_policy)
        if lod_snapshot_policy is not None
        else lod_snapshot_policy_v2_to_dict(
            satellite_count=config.satellite_count,
            user_count=config.user_count,
            scale_policy=resolved_scale_policy,
        )
    )
    safety_report = ScaleSafetyChecker().validate(_scale_config(config))
    event_stream = _stream_guardrail(
        name="event_stream",
        estimated_items=safety_report.estimated_events,
        max_items=config.event_stream_max_items,
        max_batch_size=config.stream_max_batch_size,
    )
    state_stream = _stream_guardrail(
        name="state_stream",
        estimated_items=_estimated_state_snapshots(
            safety_report.estimated_events,
            config.snapshot_interval_events,
        ),
        max_items=config.state_stream_max_items,
        max_batch_size=config.stream_max_batch_size,
    )
    degrade_reasons = _degrade_reasons(
        scale_policy=resolved_scale_policy,
        lod_snapshot_policy=resolved_lod_policy,
        event_stream=event_stream,
        state_stream=state_stream,
        risks=safety_report.risks,
    )
    refusal_reasons = tuple(safety_report.violations)
    decision = _decision(refusal_reasons, degrade_reasons)
    return {
        "version": "v2",
        "guardrail_id": RUNTIME_GUARDRAILS_V2_ID,
        "source_policy_ids": {
            "scale_policy": resolved_scale_policy["policy_id"],
            "lod_snapshot_policy": resolved_lod_policy["policy_id"],
        },
        "active_profile_id": resolved_scale_policy["active_profile_id"],
        "active_scale_band": resolved_scale_policy["active_scale_band"],
        "configured_counts": {
            "satellite_count": config.satellite_count,
            "user_count": config.user_count,
            "compute_node_count": config.compute_node_count,
        },
        "runtime_config": {
            "simulation_duration_seconds": float(config.simulation_duration_seconds),
            "tick_interval_seconds": float(config.tick_interval_seconds),
            "average_events_per_entity_per_tick": float(
                config.average_events_per_entity_per_tick
            ),
            "partition_count": config.partition_count,
            "snapshot_interval_events": config.snapshot_interval_events,
        },
        "limits": {
            "max_event_count": config.max_event_count,
            "max_memory_bytes": config.max_memory_bytes,
            "event_stream_max_items": config.event_stream_max_items,
            "state_stream_max_items": config.state_stream_max_items,
            "stream_max_batch_size": config.stream_max_batch_size,
        },
        "estimates": {
            "event_volume": safety_report.estimated_events,
            "memory_bytes": safety_report.estimated_memory_bytes,
            "interactions_per_tick": safety_report.estimated_interactions_per_tick,
            "queue_depth": safety_report.estimated_queue_depth,
            "computation_per_tick": safety_report.estimated_computation_per_tick,
            "stream_backlog": {
                "event_stream": event_stream,
                "state_stream": state_stream,
            },
        },
        "scale_safety_report": {
            "allowed": safety_report.allowed,
            "violations": safety_report.violations,
            "risks": safety_report.risks,
        },
        "decision": decision,
        "degrade_reasons": degrade_reasons,
        "refusal_reasons": refusal_reasons,
        "runtime_actions": _runtime_actions(decision),
        "event_kernel_policy": "NO_EVENT_KERNEL_BEHAVIOR_CHANGE",
    }


def _scale_config(config: RuntimeGuardrailConfigV2) -> ScaleConfig:
    return ScaleConfig(
        satellite_count=config.satellite_count,
        user_count=max(1, config.user_count),
        simulation_duration=float(config.simulation_duration_seconds),
        compute_node_count=config.compute_node_count,
        tick_interval=float(config.tick_interval_seconds),
        average_events_per_entity_per_tick=float(
            config.average_events_per_entity_per_tick
        ),
        partition_count=config.partition_count,
        frontend_batch_size=max(500, config.stream_max_batch_size),
        snapshot_interval_events=config.snapshot_interval_events,
        max_event_count=config.max_event_count,
        max_memory_bytes=config.max_memory_bytes,
    )


def _stream_guardrail(
    *,
    name: str,
    estimated_items: int,
    max_items: int,
    max_batch_size: int,
) -> dict[str, object]:
    expected_dropped_without_cursor = max(0, estimated_items - max_items)
    return {
        "name": name,
        "estimated_items": estimated_items,
        "max_items": max_items,
        "max_batch_size": max_batch_size,
        "overflow_risk": expected_dropped_without_cursor > 0,
        "expected_dropped_without_cursor": expected_dropped_without_cursor,
        "cursor_required": expected_dropped_without_cursor > 0,
    }


def _estimated_state_snapshots(
    estimated_events: int,
    snapshot_interval_events: int,
) -> int:
    return max(1, ceil(estimated_events / float(snapshot_interval_events)))


def _degrade_reasons(
    *,
    scale_policy: Mapping[str, Any],
    lod_snapshot_policy: Mapping[str, Any],
    event_stream: Mapping[str, object],
    state_stream: Mapping[str, object],
    risks: tuple[str, ...],
) -> tuple[str, ...]:
    reasons: list[str] = []
    active_profile = scale_policy.get("active_profile")
    if isinstance(active_profile, Mapping):
        guardrail_policy = str(active_profile.get("runtime_guardrail_policy", ""))
        if guardrail_policy not in {"STANDARD_RUNTIME_GUARDS", ""}:
            reasons.append(f"active runtime guardrail policy is {guardrail_policy}")
    if bool(lod_snapshot_policy.get("cursor_required")):
        reasons.append("LOD policy requires cursor or explicit detail requests")
    if bool(event_stream.get("overflow_risk")):
        reasons.append("event stream may overflow without cursor reads")
    if bool(state_stream.get("overflow_risk")):
        reasons.append("state stream may overflow without cursor reads")
    reasons.extend(risks)
    return tuple(dict.fromkeys(reasons))


def _decision(
    refusal_reasons: tuple[str, ...],
    degrade_reasons: tuple[str, ...],
) -> RuntimeGuardrailDecision:
    if refusal_reasons:
        return "REFUSE"
    if degrade_reasons:
        return "DEGRADE"
    return "ALLOW"


def _runtime_actions(decision: RuntimeGuardrailDecision) -> dict[str, object]:
    if decision == "REFUSE":
        return {
            "pre_run_check": "BLOCK_START",
            "operator_message": "Refuse run until guardrail violations are resolved.",
            "fallback": "reduce scale, shorten duration, or enable stricter LOD/cursor mode",
        }
    if decision == "DEGRADE":
        return {
            "pre_run_check": "ALLOW_WITH_DEGRADE_NOTICE",
            "operator_message": "Run is allowed with explicit fidelity/LOD degradation notice.",
            "fallback": "use cursor reads, bounded detail windows, and result package export",
        }
    return {
        "pre_run_check": "ALLOW",
        "operator_message": "Run is within current runtime guardrails.",
        "fallback": "none",
    }


def _require_positive_int(value: object, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field_name} must be an int")
    if value <= 0:
        raise ValueError(f"{field_name} must be positive")


def _require_non_negative_int(value: object, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field_name} must be an int")
    if value < 0:
        raise ValueError(f"{field_name} must be non-negative")


def _require_positive_float(value: object, field_name: str) -> None:
    _require_non_negative_float(value, field_name)
    if float(value) <= 0.0:
        raise ValueError(f"{field_name} must be positive")


def _require_non_negative_float(value: object, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field_name} must be an int or float")
    if float(value) < 0.0:
        raise ValueError(f"{field_name} must be non-negative")
