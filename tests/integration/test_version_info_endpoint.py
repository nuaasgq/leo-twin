from __future__ import annotations

from pathlib import Path

from examples.integration_demo.config import DemoConfig
from examples.integration_demo.control_plane import DemoControlPlane
from examples.integration_demo.runtime import run_integration_demo
from leo_twin.services.build_info import VERSION_INFO_V1_ID


def test_demo_control_plane_exposes_version_info(tmp_path: Path) -> None:
    control_plane = DemoControlPlane.from_result(
        run_integration_demo(_base_demo_config()),
        config_output_path=tmp_path / "sees_control.yaml",
        generated_config_output_path=tmp_path / "generated_full_system_demo.json",
    )

    response = control_plane.version_info()
    summary = response["summary"]

    assert response["type"] == "VERSION_INFO"
    assert summary["version_info_id"] == VERSION_INFO_V1_ID
    assert summary["project"]["name"] == "leo-twin"
    assert summary["frontend"]["name"] == "leo-twin-observability-frontend"
    assert "/runtime/version" in summary["diagnostic_endpoints"]
    assert summary["constraints"]["event_kernel_frozen"] is True


def _base_demo_config() -> DemoConfig:
    return DemoConfig(
        seed=9876,
        satellite_count=4,
        ground_user_count=8,
        ground_station_count=1,
        compute_node_count=2,
        duration_seconds=60,
        orbit_tick_seconds=1,
        network_slot_seconds=30,
        flow_interval_seconds=30,
        task_interval_seconds=30,
        cell_count=8,
        state_snapshot_interval_events=20,
        metric_sample_interval=10,
        websocket_events="/stream/events",
        websocket_state="/stream/state",
        metrics_snapshot="/metrics/snapshot",
        scenario_config="/scenario/config",
        backend_host="127.0.0.1",
        backend_port=8765,
    )
