from __future__ import annotations

import json
from pathlib import Path

import pytest

from examples.integration_demo.config import DemoConfig
from examples.integration_demo.control_plane import DemoControlPlane
from examples.integration_demo.runtime import run_integration_demo
from leo_twin.schema.config import config_to_dict
from leo_twin.schema.config_loader import load_config
from leo_twin.services.scenario_builder import (
    scenario_builder_backend_summary,
    scenario_builder_config_from_sees_config,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

ACCEPTANCE_SCENARIOS = (
    (
        "small_demo_72sat",
        "configs/acceptance/small_demo_72sat.yaml",
        72,
        "PER_SATELLITE",
        "DETAILED_SMALL_SCALE",
    ),
    (
        "medium_demo_300sat",
        "configs/acceptance/medium_demo_300sat.yaml",
        300,
        "BATCH",
        "BOUNDED_CANDIDATE",
    ),
    (
        "scale_demo_1200sat_short",
        "configs/acceptance/scale_demo_1200sat_short.yaml",
        1200,
        "BATCH",
        "BOUNDED_CANDIDATE",
    ),
)


@pytest.mark.parametrize(
    ("scenario_id", "config_path", "satellite_count", "orbit_mode", "space_link_mode"),
    ACCEPTANCE_SCENARIOS,
)
def test_product_acceptance_scenario_runtime_smoke(
    tmp_path: Path,
    scenario_id: str,
    config_path: str,
    satellite_count: int,
    orbit_mode: str,
    space_link_mode: str,
) -> None:
    config = load_config(PROJECT_ROOT / config_path)
    control_plane = _control_plane(tmp_path, scenario_id)
    summary = _deterministic_backend_summary(config)

    initialize_ack = control_plane.handle_raw_message(
        json.dumps(
            {
                "type": "RUNTIME_CONTROL",
                "action": "INITIALIZE",
                "payload": config_to_dict(config),
            }
        )
    )

    assert initialize_ack["ok"] is True
    assert initialize_ack["status"]["fidelity_summary"]["orbit_update_mode"] == orbit_mode
    assert initialize_ack["status"]["fidelity_summary"]["space_link_mode"] == space_link_mode
    assert initialize_ack["generated_config"]["backend_summary"][
        "derived_constellation_summary"
    ] == summary["derived_constellation_summary"]
    assert len(control_plane.visible_snapshot()["satellites"]) == satellite_count

    start_ack = control_plane.handle_raw_message(
        json.dumps({"type": "RUNTIME_CONTROL", "action": "START"})
    )
    assert start_ack["ok"] is True
    assert start_ack["status"]["status"] == "RUNNING"
    events = control_plane._require_advance_loop().tick()
    assert events

    state_batch = control_plane.stream_snapshot_batch(cursor=0, limit=3)
    assert state_batch["items"]
    assert len(state_batch["items"][0]["satellites"]) == satellite_count
    assert state_batch["items"][0]["fidelity_summary"]

    pause_ack = control_plane.handle_raw_message(
        json.dumps({"type": "RUNTIME_CONTROL", "action": "PAUSE"})
    )
    assert pause_ack["ok"] is True
    assert pause_ack["status"]["status"] == "PAUSED"

    stop_ack = control_plane.handle_raw_message(
        json.dumps({"type": "RUNTIME_CONTROL", "action": "STOP"})
    )
    assert stop_ack["ok"] is True
    assert stop_ack["status"]["status"] == "STOPPED"

    reset_ack = control_plane.handle_raw_message(
        json.dumps({"type": "RUNTIME_CONTROL", "action": "RESET"})
    )
    assert reset_ack["ok"] is True
    assert reset_ack["status"]["lifecycle_state"] == "INITIALIZED"


def test_acceptance_scenarios_leave_event_kernel_unchanged() -> None:
    kernel_source = (PROJECT_ROOT / "src/leo_twin/core/kernel.py").read_text(
        encoding="utf-8"
    )

    assert "ORBIT_BATCH_UPDATE" not in kernel_source
    assert "OrbitBatchState" not in kernel_source
    assert "SpaceLinkMode" not in kernel_source


def _deterministic_backend_summary(config: object) -> dict[str, object]:
    first = scenario_builder_backend_summary(
        scenario_builder_config_from_sees_config(config)  # type: ignore[arg-type]
    )
    second = scenario_builder_backend_summary(
        scenario_builder_config_from_sees_config(config)  # type: ignore[arg-type]
    )
    assert first == second
    return first


def _control_plane(tmp_path: Path, scenario_id: str) -> DemoControlPlane:
    return DemoControlPlane.from_result(
        run_integration_demo(_base_demo_config()),
        config_output_path=tmp_path / f"{scenario_id}_sees_control.yaml",
        generated_config_output_path=tmp_path
        / f"{scenario_id}_generated_full_system_demo.json",
    )


def _base_demo_config() -> DemoConfig:
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
