from __future__ import annotations

import pytest

from examples.integration_demo.config import DemoConfig
from examples.integration_demo.scenario import build_demo_scenario


def test_demo_scenario_builds_position_network_ground_endpoints() -> None:
    scenario = build_demo_scenario(_demo_config())

    assert len(scenario.ground_endpoints) == 5
    assert [endpoint.endpoint_id for endpoint in scenario.ground_endpoints] == [
        "ground-station-00",
        "user-0000",
        "user-0001",
        "user-0002",
        "user-0003",
    ]
    for endpoint in scenario.ground_endpoints:
        radius = sum(component * component for component in endpoint.position) ** 0.5
        assert radius == pytest.approx(6371.0)
        assert endpoint.min_elevation_deg == 10.0
        assert endpoint.max_range_km == 2500.0


def test_demo_scenario_ground_endpoints_are_deterministic() -> None:
    first = build_demo_scenario(_demo_config()).ground_endpoints
    second = build_demo_scenario(_demo_config()).ground_endpoints

    assert first == second


def _demo_config() -> DemoConfig:
    return DemoConfig(
        seed=1234,
        satellite_count=6,
        ground_user_count=4,
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
