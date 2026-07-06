from __future__ import annotations

import json
import queue
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, TypeVar

from examples.integration_demo.config import DemoConfig
from examples.integration_demo.control_plane import DemoControlPlane
from examples.integration_demo.runtime import run_integration_demo
from examples.integration_demo.server import _live_stream_finished
from leo_twin.core import SimulationKernel, SimulationModule
from leo_twin.runtime import (
    RuntimeKernelSpec,
    RuntimeLifecycleState,
    SessionAdvanceLoop,
    SimulationSession,
)
from leo_twin.schema import SimEvent
from leo_twin.schema.config import OrbitParameters, RuntimeConfig, ScenarioConfig


def test_start_pause_resume_stop_drive_live_advance_loop(tmp_path: Path) -> None:
    control_plane = _control_plane(tmp_path)
    control_plane.handle_raw_message(
        json.dumps({"type": "RUNTIME_CONTROL", "action": "INITIALIZE"})
    )

    start_ack = control_plane.handle_raw_message(
        json.dumps({"type": "RUNTIME_CONTROL", "action": "START"})
    )
    assert start_ack["ok"] is True
    assert start_ack["status"]["status"] == "RUNNING"
    assert start_ack["status"]["lifecycle_state"] == "RUNNING"
    assert control_plane.advance_loop_snapshot()["state"] == "RUNNING"
    control_plane._require_advance_loop().tick()

    pause_ack = control_plane.handle_raw_message(
        json.dumps({"type": "RUNTIME_CONTROL", "action": "PAUSE"})
    )
    assert pause_ack["status"]["status"] == "PAUSED"
    assert pause_ack["status"]["lifecycle_state"] == "PAUSED"
    paused_time = float(pause_ack["status"]["current_sim_time"])
    control_plane._require_advance_loop().tick()
    control_plane._require_advance_loop().tick()
    assert control_plane.runtime_status()["status"]["current_sim_time"] == paused_time

    resume_ack = control_plane.handle_raw_message(
        json.dumps({"type": "RUNTIME_CONTROL", "action": "RESUME"})
    )
    assert resume_ack["status"]["status"] == "RUNNING"
    assert resume_ack["status"]["lifecycle_state"] == "RUNNING"
    assert control_plane.advance_loop_snapshot()["state"] == "RUNNING"
    control_plane._require_session().advance_control_step()
    control_plane._require_advance_loop().publish_pending()
    assert control_plane.runtime_status()["status"]["current_sim_time"] > paused_time

    stop_ack = control_plane.handle_raw_message(
        json.dumps({"type": "RUNTIME_CONTROL", "action": "STOP"})
    )
    assert stop_ack["status"]["status"] == "STOPPED"
    assert stop_ack["status"]["lifecycle_state"] == "STOPPED"
    assert control_plane.advance_loop_snapshot()["state"] == "STOPPED"


def test_reset_replaces_session_and_clears_stream_buffers(tmp_path: Path) -> None:
    control_plane = _initialized_running_control_plane(tmp_path)

    first_batch = control_plane.stream_event_batch(cursor=0, limit=10)
    assert first_batch["items"]
    assert control_plane.advance_loop_snapshot()["event_stream"]["retained_count"] > 0

    reset_ack = control_plane.handle_raw_message(
        json.dumps({"type": "RUNTIME_CONTROL", "action": "RESET"})
    )

    assert reset_ack["ok"] is True
    assert reset_ack["status"]["last_action"] == "RESET"
    assert reset_ack["status"]["initialized"] is False
    assert reset_ack["status"]["lifecycle_state"] == "INITIALIZED"
    reset_user_history = reset_ack["status"]["user_request_history_v1"]
    assert reset_user_history["series"]
    assert all(
        sample["sim_time"] == 0.0
        for series in reset_user_history["series"]
        for sample in series["samples"]
    )
    assert control_plane.advance_loop_snapshot()["event_stream"]["retained_count"] == 0
    assert control_plane.advance_loop_snapshot()["snapshot_stream"]["retained_count"] == 0
    assert control_plane.stream_event_batch(cursor=0)["items"] == []


def test_large_batch_runtime_keeps_snapshot_and_controls_responsive(tmp_path: Path) -> None:
    control_plane = _control_plane(tmp_path)
    initialize_ack = control_plane.handle_raw_message(
        json.dumps(
            {
                "type": "RUNTIME_CONTROL",
                "action": "INITIALIZE",
                "payload": {
                    "satellite_count": 1200,
                    "user_count": 20,
                    "compute_nodes": 1200,
                    "duration": 120,
                    "orbit": {
                        "update_interval_seconds": 60,
                        "plane_count": 12,
                        "altitude_m": 550_000.0,
                        "inclination_deg": 53.0,
                    },
                    "traffic_model": {
                        "flow_interval_seconds": 60,
                        "task_interval_seconds": 60,
                        "flow_demand_capacity": 25.0,
                        "task_compute_demand": 20.0,
                        "task_data_size": 2.0,
                    },
                },
            }
        )
    )

    assert initialize_ack["ok"] is True
    fidelity = initialize_ack["status"]["fidelity_summary"]
    assert fidelity == initialize_ack["generated_config"]["backend_summary"][
        "fidelity_summary"
    ]
    assert set(fidelity) == {
        "satellite_count",
        "user_count",
        "orbit_update_mode",
        "metrics_mode",
        "space_link_mode",
        "detailed_space_link_enabled",
        "space_link_candidate_policy",
        "max_space_link_candidates_per_satellite",
        "batch_space_link_update_limit",
        "scale_limit_reason",
        "current_scale_mode",
        "fidelity_warnings",
    }
    assert fidelity["orbit_update_mode"] == "BATCH"
    assert fidelity["metrics_mode"] == "AGGREGATED"
    assert fidelity["space_link_mode"] == "BOUNDED_CANDIDATE"
    assert fidelity["detailed_space_link_enabled"] is False
    assert fidelity["space_link_candidate_policy"] == (
        "SAME_PLANE_AND_ADJACENT_PLANE_BOUNDED_CANDIDATES"
    )
    assert fidelity["max_space_link_candidates_per_satellite"] == 4
    assert fidelity["batch_space_link_update_limit"] == 999
    assert fidelity["current_scale_mode"] == "LARGE_SCALE_AGGREGATED"
    assert "bounded candidate updates are enabled" in fidelity[
        "scale_limit_reason"
    ]
    assert any(
        "bounded candidate updates" in warning
        for warning in fidelity["fidelity_warnings"]
    )
    assert fidelity["satellite_count"] == 1200
    assert fidelity["user_count"] == 20
    assert len(control_plane.visible_snapshot()["satellites"]) == 1200
    assert control_plane.visible_snapshot()["fidelity_summary"] == fidelity

    start_ack = control_plane.handle_raw_message(
        json.dumps({"type": "RUNTIME_CONTROL", "action": "START"})
    )
    assert start_ack["ok"] is True
    control_plane._require_advance_loop().tick()
    status_after_tick = control_plane.runtime_status()["status"]
    profiling = status_after_tick["profiling_summary"]
    backpressure = status_after_tick["backpressure_summary"]

    assert set(profiling) >= {
        "orbit_batch_update_time_ms",
        "network_batch_ingestion_time_ms",
        "access_update_time_ms",
        "space_space_candidate_update_time_ms",
        "flow_arrival_processing_time_ms",
        "route_update_time_ms",
        "compute_task_arrival_processing_time_ms",
        "compute_queue_update_time_ms",
        "metrics_aggregation_time_ms",
        "snapshot_projection_time_ms",
        "total_tick_time_ms",
        "processed_event_count",
        "event_type_counts",
    }
    assert set(backpressure) == {
        "tick_duration_ms",
        "tick_budget_ms",
        "overloaded",
        "queue_depth",
        "processed_event_count",
        "deferred_event_count",
        "first_tick_heavy",
        "bottleneck_component",
        "recommended_action",
    }
    assert backpressure["tick_budget_ms"] == 1000.0
    assert backpressure["processed_event_count"] == profiling["processed_event_count"]
    state_batch = control_plane.stream_snapshot_batch(cursor=0, limit=10)
    assert state_batch["items"]
    assert state_batch["items"][0]["fidelity_summary"] == fidelity
    pause_ack = _call_with_timeout(
        lambda: control_plane.handle_raw_message(
            json.dumps({"type": "RUNTIME_CONTROL", "action": "PAUSE"})
        ),
        timeout_seconds=10.0,
    )
    assert pause_ack["ok"] is True
    assert pause_ack["status"]["status"] == "PAUSED"

    stop_ack = _call_with_timeout(
        lambda: control_plane.handle_raw_message(
            json.dumps({"type": "RUNTIME_CONTROL", "action": "STOP"})
        ),
        timeout_seconds=10.0,
    )
    assert stop_ack["ok"] is True
    assert stop_ack["status"]["status"] == "STOPPED"


def test_http_cursor_batches_return_incremental_events(tmp_path: Path) -> None:
    control_plane = _initialized_running_control_plane(tmp_path)

    first = control_plane.stream_event_batch(cursor=0, limit=1)
    assert len(first["items"]) == 1
    assert first["next_cursor"] > first["cursor"]

    second = control_plane.stream_event_batch(cursor=int(first["next_cursor"]), limit=1)
    assert second["cursor"] == first["next_cursor"]
    assert second["next_cursor"] >= second["cursor"]
    assert second["items"] != first["items"]


def test_runtime_detail_pages_return_deterministic_windows(tmp_path: Path) -> None:
    control_plane = _initialized_running_control_plane(tmp_path)
    user_first = control_plane.runtime_user_details(cursor=0, limit=2)
    user_second = control_plane.runtime_user_details(cursor=2, limit=2)
    satellite_first = control_plane.runtime_satellite_details(cursor=0, limit=3)
    satellite_second = control_plane.runtime_satellite_details(cursor=3, limit=3)
    user_detail = control_plane.runtime_user_detail("user-0001")
    satellite_detail = control_plane.runtime_satellite_detail("sat-000")
    node_first = control_plane.runtime_node_details(cursor=0, limit=2)
    node_after_users = control_plane.runtime_node_details(
        cursor=user_first["summary"]["user_count"],
        limit=2,
    )
    route_first = control_plane.runtime_route_details(cursor=0, limit=2)
    service_first = control_plane.runtime_service_details(cursor=0, limit=2)
    service_trace_first = control_plane.runtime_service_trace_details(cursor=0, limit=2)
    compute_node_first = control_plane.runtime_compute_node_details(cursor=0, limit=2)

    user_first_summary = user_first["summary"]
    user_second_summary = user_second["summary"]
    satellite_first_summary = satellite_first["summary"]
    satellite_second_summary = satellite_second["summary"]
    node_first_summary = node_first["summary"]
    node_after_users_summary = node_after_users["summary"]

    assert user_first["type"] == "RUNTIME_DETAIL_PAGE"
    assert user_first["kind"] == "users"
    assert user_first_summary["cursor"] == 0
    assert user_first_summary["limit"] == 2
    assert user_first_summary["next_cursor"] == 2
    assert user_first_summary["has_more"] is True
    assert [item["user_id"] for item in user_first_summary["items"]] == [
        "ground-station-00",
        "user-0000",
    ]
    assert user_second_summary["cursor"] == 2
    assert [item["user_id"] for item in user_second_summary["items"]] == [
        "user-0001",
        "user-0002",
    ]
    assert user_detail["type"] == "RUNTIME_ENTITY_DETAIL"
    assert user_detail["kind"] == "user"
    assert user_detail["entity_id"] == "user-0001"
    assert user_detail["summary"]["entity_type"] == "USER"
    assert user_detail["summary"]["entity_id"] == "user-0001"

    assert satellite_first["type"] == "RUNTIME_DETAIL_PAGE"
    assert satellite_first["kind"] == "satellites"
    assert satellite_first_summary["cursor"] == 0
    assert satellite_first_summary["limit"] == 3
    assert satellite_first_summary["next_cursor"] == 3
    assert satellite_first_summary["has_more"] is True
    assert [item["satellite_id"] for item in satellite_first_summary["items"]] == [
        "sat-000",
        "sat-001",
        "sat-002",
    ]
    assert satellite_second_summary["cursor"] == 3
    assert [item["satellite_id"] for item in satellite_second_summary["items"]] == [
        "sat-003",
        "sat-004",
        "sat-005",
    ]
    assert satellite_detail["type"] == "RUNTIME_ENTITY_DETAIL"
    assert satellite_detail["kind"] == "satellite"
    assert satellite_detail["entity_id"] == "sat-000"
    assert satellite_detail["summary"]["entity_type"] == "SATELLITE"
    assert satellite_detail["summary"]["entity_id"] == "sat-000"

    assert node_first["type"] == "RUNTIME_DETAIL_PAGE"
    assert node_first["kind"] == "nodes"
    assert node_first_summary["cursor"] == 0
    assert node_first_summary["limit"] == 2
    assert node_first_summary["next_cursor"] == 2
    assert node_first_summary["window_user_detail_count"] == 2
    assert node_first_summary["window_satellite_detail_count"] == 0
    assert [item["entity_id"] for item in node_first_summary["items"]] == [
        "ground-station-00",
        "user-0000",
    ]
    assert node_after_users["kind"] == "nodes"
    assert node_after_users_summary["cursor"] == user_first_summary["user_count"]
    assert node_after_users_summary["window_user_detail_count"] == 0
    assert node_after_users_summary["window_satellite_detail_count"] == 2
    assert [item["entity_id"] for item in node_after_users_summary["items"]] == [
        "sat-000",
        "sat-001",
    ]

    assert route_first["type"] == "RUNTIME_DETAIL_PAGE"
    assert route_first["kind"] == "routes"
    assert route_first["summary"]["cursor"] == 0
    assert route_first["summary"]["limit"] == 2
    assert route_first["summary"]["route_count"] >= route_first["summary"][
        "item_count"
    ]
    if route_first["summary"]["items"]:
        first_route_id = route_first["summary"]["items"][0]["route_id"]
        route_detail = control_plane.runtime_route_detail(first_route_id)
        assert route_detail["type"] == "RUNTIME_ENTITY_DETAIL"
        assert route_detail["kind"] == "route"
        assert route_detail["entity_id"] == first_route_id
        assert route_detail["summary"]["route_id"] == first_route_id

    assert service_first["type"] == "RUNTIME_DETAIL_PAGE"
    assert service_first["kind"] == "services"
    assert service_first["summary"]["cursor"] == 0
    assert service_first["summary"]["limit"] == 2
    assert service_first["summary"]["service_count"] >= service_first["summary"][
        "item_count"
    ]
    if service_first["summary"]["items"]:
        first_service_id = service_first["summary"]["items"][0]["service_id"]
        service_detail = control_plane.runtime_service_detail(first_service_id)
        assert service_detail["type"] == "RUNTIME_ENTITY_DETAIL"
        assert service_detail["kind"] == "service"
        assert service_detail["entity_id"] == first_service_id
        assert service_detail["summary"]["service_id"] == first_service_id
        service_trace_detail = control_plane.runtime_service_trace_detail(
            first_service_id
        )
        assert service_trace_detail["type"] == "RUNTIME_ENTITY_DETAIL"
        assert service_trace_detail["kind"] == "service_trace"
        assert service_trace_detail["summary"]["version"] == "v2"
        assert service_trace_detail["summary"]["trace"]["task_id"] == first_service_id
        assert service_trace_detail["summary"]["correlation"]["route_count"] >= 0
        assert "flow_ids" in service_trace_detail["summary"]["correlation"]

    assert service_trace_first["type"] == "RUNTIME_DETAIL_PAGE"
    assert service_trace_first["kind"] == "service_traces"
    assert service_trace_first["summary"]["version"] == "v2"
    assert service_trace_first["summary"]["cursor"] == 0
    assert service_trace_first["summary"]["limit"] == 2
    if service_trace_first["summary"]["items"]:
        first_trace = service_trace_first["summary"]["items"][0]
        first_compute_node_id = first_trace["compute_node_id"]
        filtered_trace = control_plane.runtime_service_trace_details(
            cursor=0,
            limit=2,
            terminal_state=first_trace["terminal_state"],
            compute_node_id=first_compute_node_id,
        )
        assert filtered_trace["summary"]["filter_terminal_state"] == first_trace[
            "terminal_state"
        ]
        if first_compute_node_id:
            assert (
                filtered_trace["summary"]["filter_compute_node_id"]
                == first_compute_node_id.lower()
            )
        assert filtered_trace["summary"]["items"][0]["trace_id"] == first_trace[
            "trace_id"
        ]

    assert compute_node_first["type"] == "RUNTIME_DETAIL_PAGE"
    assert compute_node_first["kind"] == "compute_nodes"
    assert compute_node_first["summary"]["cursor"] == 0
    assert compute_node_first["summary"]["limit"] == 2
    assert compute_node_first["summary"]["compute_node_count"] >= (
        compute_node_first["summary"]["item_count"]
    )
    if compute_node_first["summary"]["items"]:
        first_compute_node_id = compute_node_first["summary"]["items"][0]["node_id"]
        compute_node_detail = control_plane.runtime_compute_node_detail(
            first_compute_node_id
        )
        assert compute_node_detail["type"] == "RUNTIME_ENTITY_DETAIL"
        assert compute_node_detail["kind"] == "compute_node"
        assert compute_node_detail["entity_id"] == first_compute_node_id
        assert compute_node_detail["summary"]["node_id"] == first_compute_node_id


def test_demo_runtime_status_completes_at_configured_duration(tmp_path: Path) -> None:
    control_plane = _control_plane(tmp_path)
    initialized = control_plane.handle_raw_message(
        json.dumps(
            {
                "type": "RUNTIME_CONTROL",
                "action": "INITIALIZE",
                "payload": {
                    "duration": 2,
                    "orbit": {"update_interval_seconds": 1},
                    "traffic_model": {
                        "flow_interval_seconds": 1,
                        "task_interval_seconds": 1,
                    },
                },
            }
        )
    )
    assert initialized["ok"] is True
    started = control_plane.handle_raw_message(
        json.dumps({"type": "RUNTIME_CONTROL", "action": "START"})
    )
    assert started["ok"] is True
    control_plane._require_advance_loop().stop()

    for _ in range(4):
        control_plane._require_session().advance_control_step()
        control_plane._require_advance_loop().publish_pending()

    status = control_plane.runtime_status()["status"]
    kpi_series = status["kpi_time_series_v1"]

    assert status["lifecycle_state"] == "COMPLETED"
    assert status["status"] == "COMPLETED"
    assert status["current_sim_time"] == 2.0
    assert kpi_series["samples"][-1]["sim_time"] == 2.0


def test_legacy_live_streams_stop_after_session_completion(tmp_path: Path) -> None:
    control_plane = _control_plane(tmp_path)
    initialized = control_plane.handle_raw_message(
        json.dumps(
            {
                "type": "RUNTIME_CONTROL",
                "action": "INITIALIZE",
                "payload": {
                    "duration": 2,
                    "orbit": {"update_interval_seconds": 1},
                    "traffic_model": {
                        "flow_interval_seconds": 1,
                        "task_interval_seconds": 1,
                    },
                },
            }
        )
    )
    assert initialized["ok"] is True
    started = control_plane.handle_raw_message(
        json.dumps({"type": "RUNTIME_CONTROL", "action": "START"})
    )
    assert started["ok"] is True
    control_plane._require_advance_loop().stop()

    for _ in range(4):
        control_plane._require_session().advance_control_step()
        control_plane._require_advance_loop().publish_pending()

    assert control_plane._require_session().get_status().lifecycle_state == (
        RuntimeLifecycleState.COMPLETED
    )
    assert control_plane.controller.snapshot().status == "RUNNING"
    assert control_plane.stream_events() == ()
    assert control_plane.stream_snapshots() == ()


def test_server_side_advance_loop_stops_at_configured_duration() -> None:
    session = SimulationSession(
        session_id="duration-loop-test",
        runtime_config=RuntimeConfig(seed=7, duration=2),
        scenario_config=ScenarioConfig(
            satellite_count=1,
            user_count=1,
            compute_nodes=1,
            cell_count=1,
            orbit=OrbitParameters(update_interval_seconds=1),
        ),
        kernel_factory=_kernel_factory,
        snapshot_interval_events=1,
        deterministic_replay=True,
        control_step_seconds=1.0,
    )
    session.initialize()
    session.start_live()
    loop = SessionAdvanceLoop(session, tick_interval_seconds=0.001)

    loop.start()
    assert _wait_for(lambda: loop.state.value == "STOPPED", timeout_seconds=1.0)
    loop.publish_pending()

    assert session.get_status().lifecycle_state == RuntimeLifecycleState.COMPLETED
    assert session.get_status().current_sim_time == 2.0
    assert [event.event_id for event in loop.event_stream.read_after(0).items] == [0, 1, 2]


def test_demo_live_session_does_not_precompute_full_orbit_step(tmp_path: Path) -> None:
    control_plane = DemoControlPlane.from_result(
        run_integration_demo(_slow_orbit_demo_config()),
        config_output_path=tmp_path / "sees_control.yaml",
        generated_config_output_path=tmp_path / "generated_full_system_demo.json",
    )
    control_plane.handle_raw_message(
        json.dumps({"type": "RUNTIME_CONTROL", "action": "INITIALIZE"})
    )

    start_ack = control_plane.handle_raw_message(
        json.dumps({"type": "RUNTIME_CONTROL", "action": "START"})
    )

    assert start_ack["ok"] is True
    assert start_ack["status"]["deterministic_replay"] is False
    assert start_ack["status"]["current_sim_time"] < 60
    assert start_ack["status"]["queued_event_count"] > 0


def test_live_stream_reads_do_not_run_until_idle(tmp_path: Path) -> None:
    control_plane = _initialized_running_control_plane(tmp_path)

    def fail_run_until_idle(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("live stream reads must not drain the simulation")

    control_plane._require_advance_loop().run_until_idle = (  # type: ignore[method-assign]
        fail_run_until_idle
    )

    assert control_plane.stream_event_batch(cursor=0, limit=10)["items"]
    assert control_plane.stream_snapshot_batch(cursor=0, limit=10)["items"]
    assert control_plane.stream_events()
    assert control_plane.stream_snapshots()


def test_websocket_live_stream_finish_policy_keeps_running_streams_open() -> None:
    assert _live_stream_finished(RuntimeLifecycleState.RUNNING, sent_items=False) is False
    assert _live_stream_finished(RuntimeLifecycleState.COMPLETED, sent_items=True) is False
    assert _live_stream_finished(RuntimeLifecycleState.COMPLETED, sent_items=False) is True
    assert _live_stream_finished(RuntimeLifecycleState.STOPPED, sent_items=False) is True


def test_deterministic_replay_advance_loop_sequence_is_stable() -> None:
    first = _deterministic_replay_sequence()
    second = _deterministic_replay_sequence()

    assert first == second
    assert first == (0, 1, 2, 3, 4)


def _initialized_running_control_plane(tmp_path: Path) -> DemoControlPlane:
    control_plane = _control_plane(tmp_path)
    control_plane.handle_raw_message(
        json.dumps({"type": "RUNTIME_CONTROL", "action": "INITIALIZE"})
    )
    start_ack = control_plane.handle_raw_message(
        json.dumps({"type": "RUNTIME_CONTROL", "action": "START"})
    )
    assert start_ack["ok"] is True
    control_plane._require_advance_loop().tick()
    return control_plane


def _control_plane(tmp_path: Path) -> DemoControlPlane:
    return DemoControlPlane.from_result(
        run_integration_demo(_small_demo_config()),
        config_output_path=tmp_path / "sees_control.yaml",
        generated_config_output_path=tmp_path / "generated_full_system_demo.json",
    )


def _small_demo_config() -> DemoConfig:
    return DemoConfig(
        seed=1234,
        satellite_count=8,
        ground_user_count=20,
        ground_station_count=1,
        compute_node_count=2,
        duration_seconds=180,
        orbit_tick_seconds=1,
        network_slot_seconds=30,
        flow_interval_seconds=30,
        task_interval_seconds=30,
        cell_count=10,
        state_snapshot_interval_events=20,
        metric_sample_interval=10,
        websocket_events="/stream/events",
        websocket_state="/stream/state",
        metrics_snapshot="/metrics/snapshot",
        scenario_config="/scenario/config",
        backend_host="127.0.0.1",
        backend_port=8765,
    )


def _slow_orbit_demo_config() -> DemoConfig:
    return DemoConfig(
        seed=1234,
        satellite_count=8,
        ground_user_count=20,
        ground_station_count=1,
        compute_node_count=2,
        duration_seconds=180,
        orbit_tick_seconds=60,
        network_slot_seconds=60,
        flow_interval_seconds=60,
        task_interval_seconds=60,
        cell_count=10,
        state_snapshot_interval_events=20,
        metric_sample_interval=10,
        websocket_events="/stream/events",
        websocket_state="/stream/state",
        metrics_snapshot="/metrics/snapshot",
        scenario_config="/scenario/config",
        backend_host="127.0.0.1",
        backend_port=8765,
    )


def _deterministic_replay_sequence() -> tuple[int, ...]:
    session = SimulationSession(
        session_id="deterministic-replay-test",
        runtime_config=RuntimeConfig(seed=7, duration=10),
        scenario_config=ScenarioConfig(
            satellite_count=1,
            user_count=1,
            compute_nodes=1,
            cell_count=1,
            orbit=OrbitParameters(update_interval_seconds=1),
        ),
        kernel_factory=_kernel_factory,
        snapshot_interval_events=1,
        deterministic_replay=True,
        control_step_seconds=1.0,
    )
    session.initialize()
    session.start()
    loop = SessionAdvanceLoop(session, tick_interval_seconds=0.001)
    loop.publish_pending()
    loop.run_until_idle()
    return tuple(int(event.event_id) for event in loop.event_stream.read_after(0).items)


T = TypeVar("T")


def _call_with_timeout(callback: Callable[[], T], timeout_seconds: float) -> T:
    results: queue.Queue[tuple[str, T | BaseException]] = queue.Queue(maxsize=1)

    def run() -> None:
        try:
            results.put(("result", callback()))
        except BaseException as exc:  # noqa: BLE001 - re-raised below
            results.put(("error", exc))

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    thread.join(timeout_seconds)
    if thread.is_alive():
        raise AssertionError("control command did not respond before timeout")
    kind, value = results.get_nowait()
    if kind == "error":
        raise value  # type: ignore[misc]
    return value  # type: ignore[return-value]


def _wait_for(callback: Callable[[], bool], timeout_seconds: float) -> bool:
    deadline = time.time() + timeout_seconds
    while time.time() <= deadline:
        if callback():
            return True
        time.sleep(0.001)
    return callback()


def _kernel_factory(
    _scenario_config: ScenarioConfig,
    _runtime_config: RuntimeConfig,
) -> RuntimeKernelSpec:
    kernel = SimulationKernel()
    kernel.register_module(_Recorder())
    return RuntimeKernelSpec(
        kernel=kernel,
        initial_events=tuple(_event(index, float(index)) for index in range(5)),
        snapshot_projector=_Projector([]),
        initial_snapshot={"event_ids": [], "event_count": 0, "last_sim_time": 0.0},
    )


class _Recorder(SimulationModule):
    def name(self) -> str:
        return "recorder"

    def on_event(self, event: SimEvent, kernel: SimulationKernel) -> None:
        return


@dataclass
class _Projector:
    event_ids: list[int | str]
    last_sim_time: float = 0.0

    def apply(self, event: SimEvent) -> None:
        self.event_ids.append(event.event_id)
        self.last_sim_time = event.sim_time

    def snapshot(self) -> dict[str, Any]:
        return {
            "event_ids": list(self.event_ids),
            "event_count": len(self.event_ids),
            "last_sim_time": self.last_sim_time,
        }


def _event(event_id: int, sim_time: float) -> SimEvent:
    return SimEvent(
        event_id=event_id,
        sim_time=sim_time,
        priority=0,
        source="test",
        target="recorder",
        event_type="TEST_EVENT",
        payload={},
    )
