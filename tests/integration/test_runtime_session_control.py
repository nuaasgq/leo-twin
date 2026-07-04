from __future__ import annotations

import json
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

from examples.integration_demo.config import DemoConfig
from examples.integration_demo.control_plane import DemoControlPlane
from examples.integration_demo.runtime import run_integration_demo
from examples.integration_demo.server import _stream_query
from leo_twin.core import SimulationKernel, SimulationModule
from leo_twin.runtime import (
    ControlProtocol,
    RuntimeKernelSpec,
    RuntimeLifecycleState,
    SessionAdvanceLoop,
    SimulationSession,
    SimulationSessionRegistry,
    StreamBackpressurePolicy,
    StreamBuffer,
)
from leo_twin.schema import SimEvent
from leo_twin.schema.config import (
    OrbitParameters,
    RuntimeConfig,
    RuntimeMode,
    ScenarioConfig,
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


def test_initialize_creates_valid_session() -> None:
    session = _session()

    status = session.initialize()

    assert status.lifecycle_state == RuntimeLifecycleState.INITIALIZED
    assert status.current_sim_time == 0.0
    assert status.processed_event_count == 0
    assert status.queued_event_count == 5
    assert session.get_snapshot()["event_count"] == 0


def test_start_pause_resume_stop_and_reset_lifecycle() -> None:
    session = _initialized_session()

    start_status = session.start()
    assert start_status.lifecycle_state == RuntimeLifecycleState.RUNNING
    assert start_status.current_sim_time == 1.0
    assert session.get_snapshot()["event_ids"] == [0, 1]

    paused_status = session.pause()
    before = paused_status.current_sim_time
    session.advance_control_step()
    assert session.get_status().current_sim_time == before

    resumed_status = session.resume()
    assert resumed_status.lifecycle_state == RuntimeLifecycleState.RUNNING
    assert resumed_status.current_sim_time == 2.0
    assert session.get_snapshot()["event_ids"] == [0, 1, 2]

    stopped_status = session.stop()
    assert stopped_status.lifecycle_state == RuntimeLifecycleState.STOPPED

    reset_status = session.reset()
    assert reset_status.lifecycle_state == RuntimeLifecycleState.INITIALIZED
    assert reset_status.current_sim_time == 0.0
    assert reset_status.processed_event_count == 0
    assert reset_status.queued_event_count == 5
    assert session.get_snapshot()["event_count"] == 0


def test_set_speed_factor_changes_accelerated_progression() -> None:
    slow = _initialized_session(mode=RuntimeMode.ACCELERATED, speed_factor=1.0)
    fast = _initialized_session(mode=RuntimeMode.ACCELERATED, speed_factor=3.0)

    assert slow.start().current_sim_time == 1.0
    assert fast.start().current_sim_time == 3.0

    slow.set_speed_factor(4.0)
    slow.advance_control_step()
    assert slow.get_status().current_sim_time == 4.0


def test_repeated_deterministic_run_produces_same_status_and_snapshots() -> None:
    first_statuses, first_snapshots = _deterministic_sequence()
    second_statuses, second_snapshots = _deterministic_sequence()

    assert first_statuses == second_statuses
    assert first_snapshots == second_snapshots


def test_invalid_command_returns_nack_not_crash() -> None:
    session = _initialized_session()
    ack = ControlProtocol(session).handle(json.dumps({"command": "BOGUS"}))

    assert ack["ok"] is False
    assert ack["type"] == "CONTROL_ACK"
    assert ack["error"]
    assert ack["status"]["lifecycle_state"] == "INITIALIZED"


def test_demo_server_adapter_uses_runtime_status_and_control_layer(tmp_path) -> None:
    control_plane = DemoControlPlane.from_result(
        run_integration_demo(_small_demo_config()),
        config_output_path=tmp_path / "sees_control.yaml",
        generated_config_output_path=tmp_path / "generated_full_system_demo.json",
    )

    status = control_plane.runtime_status()
    assert status["status"]["initialized"] is False
    assert status["status"]["lifecycle_state"] == "INITIALIZED"
    assert status["status"]["queued_event_count"] is not None
    assert status["status"]["fidelity_summary"]["orbit_update_mode"] == "PER_SATELLITE"
    assert status["status"]["metrics_summary"]["event_count"] >= 0
    assert status["generated_config"]["backend_summary"]["fidelity_summary"] == status[
        "status"
    ]["fidelity_summary"]

    blocked = control_plane.handle_raw_message(
        json.dumps({"type": "RUNTIME_CONTROL", "action": "START"})
    )
    assert blocked["ok"] is False
    assert "initialized before start" in blocked["error"]

    initialized = control_plane.handle_raw_message(
        json.dumps({"type": "RUNTIME_CONTROL", "action": "INITIALIZE"})
    )
    assert initialized["ok"] is True
    assert initialized["status"]["initialized"] is True

    started = control_plane.handle_raw_message(
        json.dumps({"type": "RUNTIME_CONTROL", "action": "START"})
    )
    assert started["ok"] is True
    assert started["status"]["status"] == "RUNNING"
    assert started["status"]["processed_event_count"] == 0
    control_plane._require_advance_loop().tick()
    assert control_plane.stream_events()
    assert control_plane.stream_snapshots()
    status_after_tick = control_plane.runtime_status()["status"]
    assert "network_quality_loss_proxy_rate" in status_after_tick["metrics_summary"]
    assert "compute_resource_used_gflops_fp32" in status_after_tick["metrics_summary"]
    kpi_series = status_after_tick["kpi_time_series_v1"]
    assert kpi_series["version"] == "v1"
    assert kpi_series["sample_count"] == len(kpi_series["samples"])
    assert kpi_series["tail_sample_source"] == "CURRENT_METRICS_SUMMARY"
    assert kpi_series["tail_sample_source_label"] == "当前指标摘要同步"
    assert kpi_series["samples"]
    assert kpi_series["samples"] == sorted(
        kpi_series["samples"],
        key=lambda sample: sample["sim_time"],
    )
    assert {
        "sim_time",
        "network_effective_throughput_mbps",
        "network_requested_route_demand_mbps",
        "network_demand_pressure_proxy",
        "network_effective_latency_s",
        "network_effective_loss_proxy_rate",
        "network_effective_delay_variation_s",
        "compute_resource_used_gflops_fp32",
    }.issubset(kpi_series["samples"][-1])
    latest_kpi_sample = kpi_series["samples"][-1]
    assert latest_kpi_sample["network_effective_loss_proxy_rate"] == status_after_tick[
        "metrics_summary"
    ]["network_quality_effective_loss_proxy_rate"]
    assert latest_kpi_sample["network_effective_delay_variation_s"] == status_after_tick[
        "metrics_summary"
    ]["network_quality_effective_delay_variation_proxy_s"]

    requested = control_plane.handle_raw_message(json.dumps({"command": "REQUEST_STATUS"}))
    assert requested["ok"] is True
    assert requested["command"] == "REQUEST_STATUS"

    invalid = control_plane.handle_raw_message(json.dumps({"command": "NOPE"}))
    assert invalid["ok"] is False

    control_plane.handle_raw_message(json.dumps({"type": "RUNTIME_CONTROL", "action": "STOP"}))


def test_runtime_kpi_series_changes_with_configured_flow_demand(tmp_path) -> None:
    low = _runtime_status_after_route_demand(
        replace(_small_demo_config(), flow_demand_capacity=10.0),
        tmp_path / "low",
    )
    high = _runtime_status_after_route_demand(
        replace(_small_demo_config(), flow_demand_capacity=450.0),
        tmp_path / "high",
    )

    assert low["metrics_summary"]["network_quality_requested_route_demand_mbps"] < high[
        "metrics_summary"
    ]["network_quality_requested_route_demand_mbps"]
    assert (
        low["metrics_summary"]["network_quality_flow_success_count"]
        + low["metrics_summary"]["network_quality_flow_failure_count"]
    ) > 0
    assert (
        high["metrics_summary"]["network_quality_flow_success_count"]
        + high["metrics_summary"]["network_quality_flow_failure_count"]
    ) > 0
    assert low["kpi_time_series_v1"]["samples"][-1][
        "network_requested_route_demand_mbps"
    ] < high["kpi_time_series_v1"]["samples"][-1][
        "network_requested_route_demand_mbps"
    ]


def test_session_registry_owns_multiple_sessions() -> None:
    registry = SimulationSessionRegistry()
    first = registry.create(
        session_id="alpha",
        runtime_config=RuntimeConfig(seed=1, duration=10),
        scenario_config=_scenario_config(),
        kernel_factory=_kernel_factory,
        deterministic_replay=True,
    )
    second = registry.create(
        session_id="beta",
        runtime_config=RuntimeConfig(seed=2, duration=10),
        scenario_config=_scenario_config(),
        kernel_factory=_kernel_factory,
        deterministic_replay=True,
    )

    assert registry.get("alpha") is first
    assert registry.get("beta") is second
    assert registry.session_ids() == ("alpha", "beta")
    assert [record.session_id for record in registry.list_sessions()] == ["alpha", "beta"]

    try:
        registry.register(first)
    except ValueError as exc:
        assert "already registered" in str(exc)
    else:
        raise AssertionError("duplicate session registration should fail")


def test_stream_buffer_uses_cursor_and_reports_backpressure() -> None:
    stream: StreamBuffer[int] = StreamBuffer(
        StreamBackpressurePolicy(max_items=3, max_batch_size=2)
    )
    stream.publish_many((1, 2, 3, 4, 5))

    first = stream.read_after(0)
    assert first.items == (3, 4)
    assert first.next_cursor == 4
    assert first.overflow is True
    assert first.dropped_count == 2

    second = stream.read_after(first.next_cursor)
    assert second.items == (5,)
    assert second.next_cursor == 5
    assert second.overflow is False
    assert stream.snapshot().retained_count == 3


def test_server_side_advance_loop_publishes_cursor_streams() -> None:
    session = _initialized_session()
    loop = SessionAdvanceLoop(
        session,
        stream_policy=StreamBackpressurePolicy(max_items=10, max_batch_size=10),
        tick_interval_seconds=0.001,
    )

    session.start()
    loop.run_until_idle()

    event_batch = loop.event_stream.read_after(0)
    snapshot_batch = loop.snapshot_stream.read_after(0)

    assert [event.event_id for event in event_batch.items] == [0, 1, 2, 3, 4]
    assert event_batch.next_cursor == 5
    assert snapshot_batch.items[-1]["event_count"] == 5
    assert session.get_status().lifecycle_state == RuntimeLifecycleState.COMPLETED


def test_demo_adapter_exposes_cursor_batches(tmp_path) -> None:
    control_plane = DemoControlPlane.from_result(
        run_integration_demo(_small_demo_config()),
        config_output_path=tmp_path / "sees_control.yaml",
        generated_config_output_path=tmp_path / "generated_full_system_demo.json",
    )
    control_plane.handle_raw_message(
        json.dumps({"type": "RUNTIME_CONTROL", "action": "INITIALIZE"})
    )
    control_plane.handle_raw_message(json.dumps({"type": "RUNTIME_CONTROL", "action": "START"}))
    control_plane._require_advance_loop().tick()

    first = control_plane.stream_event_batch(cursor=0, limit=100)
    second = control_plane.stream_event_batch(
        cursor=int(first["next_cursor"]),
        limit=100,
    )

    assert first["items"]
    assert first["next_cursor"] > first["cursor"]
    assert second["cursor"] == first["next_cursor"]
    assert "overflow" in first
    assert control_plane.stream_snapshot_batch(cursor=0)["items"]

    control_plane.handle_raw_message(json.dumps({"type": "RUNTIME_CONTROL", "action": "STOP"}))


def test_demo_server_stream_query_parses_cursor_options() -> None:
    assert _stream_query({"cursor": ["5"], "limit": ["10"]}) == (5, 10)
    assert _stream_query({}) == (0, None)


def _deterministic_sequence() -> tuple[tuple[dict[str, Any], ...], tuple[dict[str, Any], ...]]:
    session = _initialized_session(mode=RuntimeMode.ACCELERATED, speed_factor=2.0)
    statuses: list[dict[str, Any]] = []
    snapshots: list[dict[str, Any]] = []
    session.start()
    for _ in range(2):
        session.advance_control_step()
        status = session.get_status().to_dict()
        statuses.append(
            {
                "lifecycle_state": status["lifecycle_state"],
                "current_sim_time": status["current_sim_time"],
                "processed_event_count": status["processed_event_count"],
                "queued_event_count": status["queued_event_count"],
            }
        )
        snapshots.append(session.get_snapshot())
    return tuple(statuses), tuple(snapshots)


def _initialized_session(
    *,
    mode: RuntimeMode = RuntimeMode.REAL_TIME,
    speed_factor: float = 1.0,
) -> SimulationSession:
    session = _session(mode=mode, speed_factor=speed_factor)
    session.initialize()
    return session


def _session(
    *,
    mode: RuntimeMode = RuntimeMode.REAL_TIME,
    speed_factor: float = 1.0,
) -> SimulationSession:
    return SimulationSession(
        session_id="test-session",
        runtime_config=RuntimeConfig(
            mode=mode,
            speed_factor=speed_factor,
            seed=7,
            duration=10,
        ),
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


def _scenario_config() -> ScenarioConfig:
    return ScenarioConfig(
        satellite_count=1,
        user_count=1,
        compute_nodes=1,
        cell_count=1,
        orbit=OrbitParameters(update_interval_seconds=1),
    )


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


def _small_demo_config() -> DemoConfig:
    return DemoConfig(
        seed=1234,
        satellite_count=6,
        ground_user_count=8,
        ground_station_count=1,
        compute_node_count=2,
        duration_seconds=120,
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


def _runtime_status_after_route_demand(config: DemoConfig, output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    control_plane = DemoControlPlane.from_result(
        run_integration_demo(config),
        config_output_path=output_dir / "sees_control.yaml",
        generated_config_output_path=output_dir / "generated_full_system_demo.json",
    )
    initialized = control_plane.handle_raw_message(
        json.dumps({"type": "RUNTIME_CONTROL", "action": "INITIALIZE"})
    )
    assert initialized["ok"] is True
    started = control_plane.handle_raw_message(
        json.dumps({"type": "RUNTIME_CONTROL", "action": "START"})
    )
    assert started["ok"] is True
    for _ in range(5):
        control_plane._require_session().advance_control_step()
        control_plane._require_advance_loop().publish_pending()
        status = control_plane.runtime_status()["status"]
        if status["metrics_summary"]["network_quality_requested_route_demand_mbps"] > 0:
            return status
    raise AssertionError("route demand did not reach runtime metrics")
