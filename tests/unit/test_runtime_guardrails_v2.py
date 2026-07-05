from __future__ import annotations

import pytest

from leo_twin.services.runtime_guardrails_v2 import (
    RUNTIME_GUARDRAILS_V2_ID,
    RuntimeGuardrailConfigV2,
    runtime_guardrails_v2_to_dict,
)
from leo_twin.services.scale_policy_v2 import scale_policy_v2_to_dict


def test_runtime_guardrails_v2_allows_small_short_runs() -> None:
    summary = runtime_guardrails_v2_to_dict(
        RuntimeGuardrailConfigV2(
            satellite_count=72,
            user_count=100,
            compute_node_count=10,
            simulation_duration_seconds=10.0,
        )
    )

    assert summary["guardrail_id"] == RUNTIME_GUARDRAILS_V2_ID
    assert summary["active_profile_id"] == "baseline_72"
    assert summary["decision"] == "ALLOW"
    assert summary["degrade_reasons"] == ()
    assert summary["refusal_reasons"] == ()
    assert summary["runtime_actions"]["pre_run_check"] == "ALLOW"
    estimates = summary["estimates"]
    assert isinstance(estimates, dict)
    assert estimates["event_volume"] == 172
    assert estimates["memory_bytes"] == 119_296
    event_stream = estimates["stream_backlog"]["event_stream"]
    assert event_stream == {
        "name": "event_stream",
        "estimated_items": 172,
        "max_items": 10_000,
        "max_batch_size": 1_000,
        "overflow_risk": False,
        "expected_dropped_without_cursor": 0,
        "cursor_required": False,
    }
    assert summary["event_kernel_policy"] == "NO_EVENT_KERNEL_BEHAVIOR_CHANGE"


def test_runtime_guardrails_v2_degrades_large_runs_with_cursor_and_stream_notice() -> None:
    summary = runtime_guardrails_v2_to_dict(
        RuntimeGuardrailConfigV2(
            satellite_count=1200,
            user_count=400,
            compute_node_count=120,
            simulation_duration_seconds=600.0,
        )
    )

    assert summary["active_profile_id"] == "large_1200"
    assert summary["active_scale_band"] == "LARGE_1200"
    assert summary["decision"] == "DEGRADE"
    assert "LOD policy requires cursor or explicit detail requests" in summary[
        "degrade_reasons"
    ]
    assert "event stream may overflow without cursor reads" in summary[
        "degrade_reasons"
    ]
    assert summary["refusal_reasons"] == ()
    assert summary["runtime_actions"]["pre_run_check"] == "ALLOW_WITH_DEGRADE_NOTICE"
    estimates = summary["estimates"]
    assert isinstance(estimates, dict)
    assert estimates["event_volume"] == 96_000
    assert estimates["memory_bytes"] == 49_510_400
    backlog = estimates["stream_backlog"]
    assert backlog["event_stream"]["expected_dropped_without_cursor"] == 86_000
    assert backlog["state_stream"]["estimated_items"] == 10
    assert backlog["state_stream"]["overflow_risk"] is False


def test_runtime_guardrails_v2_refuses_unsafe_event_volume() -> None:
    summary = runtime_guardrails_v2_to_dict(
        RuntimeGuardrailConfigV2(
            satellite_count=3000,
            user_count=50_000,
            compute_node_count=300,
            simulation_duration_seconds=100.0,
            average_events_per_entity_per_tick=1.0,
            max_event_count=100_000,
        )
    )

    assert summary["decision"] == "REFUSE"
    assert "estimated event count exceeds configured max_event_count" in summary[
        "refusal_reasons"
    ]
    assert summary["runtime_actions"]["pre_run_check"] == "BLOCK_START"
    scale_report = summary["scale_safety_report"]
    assert isinstance(scale_report, dict)
    assert scale_report["allowed"] is False
    assert "estimated event count exceeds configured max_event_count" in scale_report[
        "violations"
    ]


def test_runtime_guardrails_v2_reuses_supplied_scale_policy() -> None:
    scale_policy = scale_policy_v2_to_dict(satellite_count=6000, user_count=1000)
    summary = runtime_guardrails_v2_to_dict(
        RuntimeGuardrailConfigV2(
            satellite_count=6000,
            user_count=1000,
            compute_node_count=600,
            simulation_duration_seconds=60.0,
        ),
        scale_policy=scale_policy,
    )

    assert summary["source_policy_ids"]["scale_policy"] == "leo_twin.scale_policy.v2"
    assert summary["active_profile_id"] == "xxl_6000"
    assert summary["decision"] == "DEGRADE"
    assert any(
        "STRICT_GUARDS_AND_DEGRADE_REASON_REQUIRED" in reason
        for reason in summary["degrade_reasons"]
    )


@pytest.mark.parametrize(
    ("config_kwargs", "error"),
    (
        (
            {
                "satellite_count": 0,
                "user_count": 1,
                "compute_node_count": 1,
                "simulation_duration_seconds": 1.0,
            },
            ValueError,
        ),
        (
            {
                "satellite_count": 1,
                "user_count": -1,
                "compute_node_count": 1,
                "simulation_duration_seconds": 1.0,
            },
            ValueError,
        ),
        (
            {
                "satellite_count": 1,
                "user_count": 1,
                "compute_node_count": 1,
                "simulation_duration_seconds": 0.0,
            },
            ValueError,
        ),
        (
            {
                "satellite_count": True,
                "user_count": 1,
                "compute_node_count": 1,
                "simulation_duration_seconds": 1.0,
            },
            TypeError,
        ),
    ),
)
def test_runtime_guardrails_v2_rejects_invalid_inputs(
    config_kwargs: dict[str, object],
    error: type[Exception],
) -> None:
    with pytest.raises(error):
        RuntimeGuardrailConfigV2(**config_kwargs)
