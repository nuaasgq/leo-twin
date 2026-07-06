from __future__ import annotations

from leo_twin.services.runtime_reproducibility import (
    build_runtime_reproducibility_manifest,
    stable_hash_payload,
)


def test_stable_hash_payload_is_order_independent() -> None:
    left = {"b": [2, {"y": True, "x": 1}], "a": "demo"}
    right = {"a": "demo", "b": [2, {"x": 1, "y": True}]}

    assert stable_hash_payload(left) == stable_hash_payload(right)
    assert stable_hash_payload(left).startswith("sha256:")


def test_runtime_reproducibility_manifest_is_deterministic_and_excludes_wall_clock() -> None:
    runtime_status = {
        "session_id": "integration-demo-7",
        "lifecycle_state": "RUNNING",
        "status": "RUNNING",
        "mode": "REAL_TIME",
        "speed_factor": 1.0,
        "seed": 7,
        "duration": 120,
        "config_version": 2,
        "last_action": "START",
        "initialized": True,
        "current_sim_time": 12.0,
        "wall_clock_start_time": 123456.0,
        "processed_event_count": 40,
        "queued_event_count": 8,
        "deterministic_replay": False,
    }
    control_config = {"scenario": {"satellite_count": 72}, "runtime": {"seed": 7}}
    generated_config = {
        "seed": 7,
        "satellite_count": 72,
        "backend_summary": {"volatile_contract_display": "ignored for scenario hash"},
    }
    metrics_summary = {"event_count": 40, "last_sim_time": 12.0}

    first = build_runtime_reproducibility_manifest(
        session_id="integration-demo-7",
        runtime_status=runtime_status,
        control_config=control_config,
        generated_config=generated_config,
        metrics_summary=metrics_summary,
    )
    second = build_runtime_reproducibility_manifest(
        session_id="integration-demo-7",
        runtime_status={**runtime_status, "wall_clock_start_time": 999999.0},
        control_config=control_config,
        generated_config=generated_config,
        metrics_summary=metrics_summary,
    )
    changed = build_runtime_reproducibility_manifest(
        session_id="integration-demo-7",
        runtime_status=runtime_status,
        control_config=control_config,
        generated_config={**generated_config, "satellite_count": 73},
        metrics_summary=metrics_summary,
    )

    assert first == second
    assert first["version"] == "v1"
    assert first["source"] == "BACKEND_RUNTIME_STATUS"
    assert first["manifest_hash"].startswith("sha256:")
    assert first["scenario_hash"] != changed["scenario_hash"]
    assert first["manifest_hash"] != changed["manifest_hash"]
    assert first["runtime_state"]["session_id"] == "integration-demo-7"
    assert "wall_clock_start_time" not in first["runtime_state"]
    assert [artifact["name"] for artifact in first["artifacts"]] == [
        "config_snapshot.json",
        "events.jsonl",
        "metrics.csv",
        "summary.json",
        "service_lifecycle_trace_v2.json",
    ]
