from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

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
    assert control_plane.advance_loop_snapshot()["event_stream"]["retained_count"] == 0
    assert control_plane.advance_loop_snapshot()["snapshot_stream"]["retained_count"] == 0
    assert control_plane.stream_event_batch(cursor=0)["items"] == []


def test_http_cursor_batches_return_incremental_events(tmp_path: Path) -> None:
    control_plane = _initialized_running_control_plane(tmp_path)

    first = control_plane.stream_event_batch(cursor=0, limit=1)
    assert len(first["items"]) == 1
    assert first["next_cursor"] > first["cursor"]

    second = control_plane.stream_event_batch(cursor=int(first["next_cursor"]), limit=1)
    assert second["cursor"] == first["next_cursor"]
    assert second["next_cursor"] >= second["cursor"]
    assert second["items"] != first["items"]


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
