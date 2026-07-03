from __future__ import annotations

import json
from pathlib import Path

import pytest

from examples.integration_demo.config import DemoConfig
from examples.integration_demo.control_plane import DemoControlPlane
from examples.integration_demo.runtime import run_integration_demo
from leo_twin.core.config import ConfigValidationError, config_from_mapping, load_config
from leo_twin.services.control import RuntimeController


def test_config_loads_correctly() -> None:
    config = load_config("configs/sees_control.yaml")

    assert config.scenario.satellite_count == 72
    assert config.scenario.user_count == 1000
    assert config.scenario.compute_nodes == 10
    assert config.scenario.compute_scheduling_policy == "FIFO"
    assert config.runtime.mode == "REAL_TIME"
    assert config.runtime.speed_factor == 1.0
    assert config.network.transport_protocol == "TCP"
    assert config.network.routing_protocol == "LINK_STATE"
    assert config.network.datalink_mac_protocol == "TDMA"
    assert config.network.antenna_diameter_m == 0.45
    assert config.network.antenna_aperture_efficiency == 0.65
    assert config.ui.visualization.satellites is True


def test_invalid_config_is_rejected() -> None:
    with pytest.raises(ConfigValidationError):
        config_from_mapping({"scenario": {"satellite_count": 0}})

    with pytest.raises(ConfigValidationError):
        config_from_mapping({"scenario": {"unknown_field": 1}})

    with pytest.raises(ConfigValidationError):
        config_from_mapping({"network": {"transport_protocol": "SCTP"}})


def test_network_protocol_profile_can_be_updated_directly() -> None:
    controller = RuntimeController(load_config("configs/sees_control.yaml"))
    snapshot = controller.update_config(
        {
            "transport_protocol": "UDP",
            "routing_protocol": "DISTANCE_VECTOR",
            "datalink_mac_protocol": "SLOTTED_ALOHA",
            "carrier_frequency_hz": 22_000_000_000.0,
            "channel_bandwidth_hz": 250_000_000.0,
            "rain_rate_mm_h": 12.5,
            "rain_attenuation_coefficient_db_per_km_per_mm_h": 0.015,
            "rain_effective_path_km": 4.0,
            "antenna_diameter_m": 0.55,
            "antenna_aperture_efficiency": 0.7,
            "compute_scheduling_policy": "SHORTEST_JOB_FIRST",
        }
    )

    assert snapshot.last_action == "CONFIG_UPDATE"
    assert controller.config.network.transport_protocol == "UDP"
    assert controller.config.network.routing_protocol == "DISTANCE_VECTOR"
    assert controller.config.network.datalink_mac_protocol == "SLOTTED_ALOHA"
    assert controller.config.network.carrier_frequency_hz == 22_000_000_000.0
    assert controller.config.network.channel_bandwidth_hz == 250_000_000.0
    assert controller.config.network.rain_rate_mm_h == 12.5
    assert controller.config.network.antenna_diameter_m == 0.55
    assert controller.config.network.antenna_aperture_efficiency == 0.7
    assert controller.config.scenario.compute_scheduling_policy == "SHORTEST_JOB_FIRST"


def test_runtime_mode_switching_works() -> None:
    controller = RuntimeController(load_config("configs/sees_control.yaml"))

    accelerated = controller.handle_action(
        "SET_MODE",
        {"mode": "ACCELERATED"},
    )
    assert accelerated.mode == "ACCELERATED"
    assert controller.handle_action("SET_SPEED", {"speed_factor": 25}).speed_factor == 25
    assert controller.handle_action("START").status == "RUNNING"
    assert controller.handle_action("PAUSE").status == "PAUSED"
    assert controller.handle_action("STOP").status == "STOPPED"


def test_frontend_control_messages_are_processed(tmp_path) -> None:
    control_plane = _small_control_plane(tmp_path / "sees_control.yaml")

    ack = control_plane.handle_raw_message(
        json.dumps(
            {
                "type": "CONFIG_UPDATE",
                "payload": {
                    "satellite_count": 24,
                    "user_count": 40,
                    "compute_nodes": 3,
                    "transport_protocol": "UDP",
                    "routing_protocol": "DISTANCE_VECTOR",
                    "datalink_mac_protocol": "SLOTTED_ALOHA",
                    "carrier_frequency_hz": 22_000_000_000.0,
                    "channel_bandwidth_hz": 250_000_000.0,
                    "rain_rate_mm_h": 12.5,
                    "rain_attenuation_coefficient_db_per_km_per_mm_h": 0.015,
                    "rain_effective_path_km": 4.0,
                    "antenna_diameter_m": 0.55,
                    "antenna_aperture_efficiency": 0.7,
                    "compute_scheduling_policy": "SHORTEST_JOB_FIRST",
                },
            }
        )
    )
    assert ack["ok"] is True
    assert ack["status"]["last_action"] == "INITIALIZE"
    assert control_plane.result.config.satellite_count == 24
    assert len(control_plane.result.scenario.orbit_satellites) == 24
    assert control_plane.result.config.ground_user_count == 40
    assert control_plane.result.config.transport_protocol == "UDP"
    assert control_plane.result.config.routing_protocol == "DISTANCE_VECTOR"
    assert control_plane.result.config.datalink_mac_protocol == "SLOTTED_ALOHA"
    assert control_plane.result.config.carrier_frequency_hz == 22_000_000_000.0
    assert control_plane.result.config.channel_bandwidth_hz == 250_000_000.0
    assert control_plane.result.config.rain_rate_mm_h == 12.5
    assert control_plane.result.config.antenna_diameter_m == 0.55
    assert control_plane.result.config.antenna_aperture_efficiency == 0.7
    assert control_plane.result.config.compute_scheduling_policy == "SHORTEST_JOB_FIRST"
    assert control_plane.result.scenario.frontend_config["scenario"][
        "compute_scheduling_policy"
    ] == "SHORTEST_JOB_FIRST"
    assert control_plane.result.scenario.frontend_config["network"] == {
        "transport_protocol": "UDP",
        "routing_protocol": "DISTANCE_VECTOR",
        "datalink_mac_protocol": "SLOTTED_ALOHA",
        "carrier_frequency_hz": 22_000_000_000.0,
        "channel_bandwidth_hz": 250_000_000.0,
        "rain_rate_mm_h": 12.5,
        "rain_attenuation_coefficient_db_per_km_per_mm_h": 0.015,
        "rain_effective_path_km": 4.0,
        "antenna_diameter_m": 0.55,
        "antenna_aperture_efficiency": 0.7,
    }
    assert ack["generated_config"]["transport_protocol"] == "UDP"
    assert ack["generated_config"]["routing_protocol"] == "DISTANCE_VECTOR"
    assert ack["generated_config"]["datalink_mac_protocol"] == "SLOTTED_ALOHA"
    assert ack["generated_config"]["carrier_frequency_hz"] == 22_000_000_000.0
    assert ack["generated_config"]["antenna_diameter_m"] == 0.55
    assert ack["generated_config"]["antenna_aperture_efficiency"] == 0.7
    assert ack["generated_config"]["compute_scheduling_policy"] == "SHORTEST_JOB_FIRST"

    runtime_ack = control_plane.handle_raw_message(
        json.dumps({"type": "RUNTIME_CONTROL", "action": "START"})
    )
    assert runtime_ack["ok"] is True
    assert runtime_ack["status"]["status"] == "RUNNING"


def test_initialize_writes_config_and_start_gates_streams(tmp_path) -> None:
    config_path = tmp_path / "sees_control.yaml"
    generated_config_path = tmp_path / "generated_full_system_demo.json"
    control_plane = _small_control_plane(config_path, generated_config_path)

    assert control_plane.stream_events() == ()
    assert control_plane.stream_snapshots() == ()
    assert control_plane.visible_snapshot()["satellites"] == []
    assert control_plane.visible_snapshot()["event_count"] == 0

    init_ack = control_plane.handle_raw_message(
        json.dumps(
            {
                "type": "RUNTIME_CONTROL",
                "action": "INITIALIZE",
                "payload": {
                    "satellite_count": 24,
                    "user_count": 40,
                    "mode": "ACCELERATED",
                    "speed_factor": 10,
                },
            }
        )
    )

    assert init_ack["ok"] is True
    assert init_ack["status"]["last_action"] == "INITIALIZE"
    assert init_ack["status"]["status"] == "STOPPED"
    assert "satellite_count: 24" in config_path.read_text(encoding="utf-8")
    assert "speed_factor: 10" in config_path.read_text(encoding="utf-8")
    generated_config = json.loads(generated_config_path.read_text(encoding="utf-8"))
    assert generated_config["satellite_count"] == 24
    assert generated_config["user_count"] == 40
    assert generated_config["compute_node_count"] == 2
    assert generated_config["seed"] == 1234
    assert generated_config["transport_protocol"] == "TCP"
    assert generated_config["routing_protocol"] == "LINK_STATE"
    assert generated_config["datalink_mac_protocol"] == "TDMA"
    assert generated_config["compute_scheduling_policy"] == "FIFO"
    assert init_ack["generated_config"]["satellite_count"] == 24
    assert init_ack["generated_config"]["user_count"] == 40
    assert control_plane.result.config.satellite_count == 24
    assert control_plane.stream_events() == ()

    start_ack = control_plane.handle_raw_message(
        json.dumps({"type": "RUNTIME_CONTROL", "action": "START"})
    )
    assert start_ack["status"]["status"] == "RUNNING"
    assert len(control_plane.stream_events()) > 0
    assert len(control_plane.stream_snapshots()) > 0

    stop_ack = control_plane.handle_raw_message(
        json.dumps({"type": "RUNTIME_CONTROL", "action": "STOP"})
    )
    assert stop_ack["status"]["status"] == "STOPPED"
    assert control_plane.stream_events() == ()

    reset_ack = control_plane.handle_raw_message(
        json.dumps({"type": "RUNTIME_CONTROL", "action": "RESET"})
    )
    assert reset_ack["status"]["last_action"] == "RESET"
    assert control_plane.visible_snapshot()["event_count"] == 0


def test_system_remains_deterministic_under_config_changes(tmp_path) -> None:
    first = _small_control_plane(tmp_path / "first.yaml")
    second = _small_control_plane(tmp_path / "second.yaml")
    command = json.dumps(
        {
            "type": "CONFIG_UPDATE",
            "payload": {
                "satellite_count": 24,
                "user_count": 40,
                "speed_factor": 10,
                "mode": "ACCELERATED",
            },
        }
    )

    first_ack = first.handle_raw_message(command)
    second_ack = second.handle_raw_message(command)

    assert first_ack == second_ack
    assert first.result.event_log_jsonl() == second.result.event_log_jsonl()
    assert first.result.final_snapshot == second.result.final_snapshot


def _small_control_plane(
    config_path: object = "configs/sees_control.yaml",
    generated_config_path: object | None = None,
) -> DemoControlPlane:
    resolved_generated_path = (
        generated_config_path
        if generated_config_path is not None
        else Path(config_path).with_name("generated_full_system_demo.json")
    )
    return DemoControlPlane.from_result(
        run_integration_demo(_small_demo_config()),
        config_output_path=config_path,
        generated_config_output_path=resolved_generated_path,
    )


def _small_demo_config() -> DemoConfig:
    return DemoConfig(
        seed=1234,
        satellite_count=12,
        ground_user_count=30,
        ground_station_count=1,
        compute_node_count=2,
        duration_seconds=120,
        orbit_tick_seconds=60,
        network_slot_seconds=60,
        flow_interval_seconds=60,
        task_interval_seconds=60,
        cell_count=10,
        state_snapshot_interval_events=100,
        metric_sample_interval=10,
        websocket_events="/stream/events",
        websocket_state="/stream/state",
        metrics_snapshot="/metrics/snapshot",
        scenario_config="/scenario/config",
        backend_host="127.0.0.1",
        backend_port=8765,
    )
