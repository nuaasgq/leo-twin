from __future__ import annotations

from functools import lru_cache

from examples.integration_demo import DemoRunResult, load_demo_config, run_integration_demo
from examples.integration_demo.replay import replay_events
from examples.integration_demo.server import _FRONTEND_EVENT_TYPES
from examples.integration_demo.serialization import event_to_json, stable_json
from leo_twin.schema import EventType


@lru_cache(maxsize=1)
def _demo_result() -> DemoRunResult:
    return run_integration_demo(load_demo_config())


def test_end_to_end_pipeline_test() -> None:
    result = _demo_result()
    event_types = {str(event.event_type) for event in result.processed_events}

    assert EventType.ORBIT_UPDATE.value in event_types
    assert EventType.ACCESS_START.value in event_types
    assert EventType.ACCESS_END.value in event_types
    assert EventType.LINK_UPDATE.value in event_types
    assert EventType.FLOW_ARRIVAL.value in event_types
    assert EventType.ROUTE_UPDATE.value in event_types
    assert EventType.TASK_START.value in event_types
    assert EventType.TASK_FINISH.value in event_types
    assert EventType.METRIC_SAMPLE.value in event_types
    assert len(result.scenario.orbit_satellites) == 72
    assert result.config.ground_user_count == 1000
    assert result.config.ground_station_count == 3
    assert len(result.scenario.compute_nodes) == 10


def test_frontend_sync_test() -> None:
    result = _demo_result()
    snapshot = result.final_snapshot
    scenario_config = result.scenario.frontend_config

    assert len(snapshot["satellites"]) == 72
    assert len(snapshot["ground_users"]) == 1003
    assert len(snapshot["tasks"]) == 100
    assert int(snapshot["event_count"]) == len(result.processed_events)
    assert len(result.frontend_events) > 0
    assert {
        str(event.event_type)
        for event in result.processed_events
        if str(event.event_type) in _FRONTEND_EVENT_TYPES
    } == _FRONTEND_EVENT_TYPES
    assert scenario_config["endpoints"] == {
        "config": "/scenario/config",
        "control": "/control",
        "events": "/stream/events",
        "state": "/stream/state",
        "metrics": "/metrics/snapshot",
        "runtime_status": "/runtime/status",
    }
    assert stable_json(snapshot).startswith("{")
    assert stable_json(scenario_config).startswith("{")


def test_replay_test() -> None:
    result = _demo_result()
    replay = replay_events(
        result.processed_events,
        result.scenario.ground_user_render_states,
        result.config.state_snapshot_interval_events,
    )

    assert replay.final_snapshot == result.final_snapshot
    assert replay.replay_signature == result.replay.replay_signature
    assert replay.timeline == result.state_timeline
    assert stable_json(event_to_json(result.processed_events[0])) in replay.replay_signature


def test_scale_test_basic() -> None:
    result = _demo_result()
    summary = result.metrics_summary

    assert len(result.processed_events) >= 10_000
    assert len(result.processed_events) == 13_010
    assert summary["event_count"] >= 10_000
    assert summary["routes_available"] >= 1
    assert summary["route_hop_count_avg"] >= 2.0
    assert 500.0 <= summary["satellite_altitude_avg"] <= 600.0
    assert summary["task_duration_avg"] >= 0.0
    assert summary["deadline_missed_tasks"] == 0
    assert len(result.state_timeline) <= len(result.processed_events) // 1000 + 1
    assert len(result.final_snapshot["links"]) <= 72 * 21
