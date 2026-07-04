from __future__ import annotations

from math import pi

import pytest

from examples.integration_demo.config import DemoConfig
from examples.integration_demo.scenario import build_demo_scenario
from leo_twin.schema import EventType, FlowRequest, TaskRequest


def test_demo_scenario_builds_position_network_ground_endpoints() -> None:
    scenario = build_demo_scenario(_demo_config())

    assert len(scenario.orbit_elements) == len(scenario.orbit_satellites)
    assert scenario.orbit_elements[0].satellite_id == scenario.orbit_satellites[0].satellite_id
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


def test_demo_scenario_uses_configured_orbit_parameters() -> None:
    scenario = build_demo_scenario(
        _demo_config(
            orbit_plane_count=3,
            orbit_altitude_m=600_000.0,
            orbit_inclination_deg=55.0,
        )
    )

    assert scenario.frontend_config["scenario"]["orbit"] == {
        "update_interval_seconds": 60,
        "plane_count": 3,
        "altitude_m": 600_000.0,
        "inclination_deg": 55.0,
    }
    assert scenario.orbit_elements[0].semi_major_axis_km == 6971.0
    assert scenario.orbit_elements[0].inclination_deg == 55.0
    assert {element.raan_deg for element in scenario.orbit_elements[:3]} == {
        0.0,
        120.0,
        240.0,
    }


def test_demo_scenario_auto_allocates_starlink_like_planes_when_not_explicit() -> None:
    scenario = build_demo_scenario(
        _demo_config(
            satellite_count=300,
            orbit_plane_count_explicit=False,
            constellation_profile="STARLINK_SHELL_1_LIKE",
        )
    )

    summary = scenario.frontend_config["derived_constellation_summary"]

    assert summary == {
        "profile": "STARLINK_SHELL_1_LIKE",
        "satellite_count": 300,
        "plane_count": 30,
        "satellites_per_plane": 10,
        "total_slots": 300,
        "plane_count_explicit": False,
        "model_note": (
            "Approximate Starlink Shell 1-like plane allocation; "
            "not exact Starlink fidelity."
        ),
    }
    assert scenario.frontend_config["scenario"]["orbit"]["plane_count"] == 30
    assert scenario.orbit_elements[30].raan_deg == pytest.approx(
        scenario.orbit_elements[0].raan_deg
    )
    assert scenario.orbit_elements[30].mean_anomaly_deg == pytest.approx(36.0)
    assert scenario.orbit_satellites[30].phase == pytest.approx(2.0 * pi / 10.0)


def test_demo_flow_requests_target_compute_nodes() -> None:
    scenario = build_demo_scenario(_demo_config())
    compute_node_ids = {node.node_id for node in scenario.compute_nodes}
    satellite_ids = {satellite.satellite_id for satellite in scenario.orbit_satellites}
    flows = tuple(
        event.payload
        for event in scenario.initial_events
        if event.event_type == EventType.FLOW_ARRIVAL
    )
    tasks = tuple(
        event.payload
        for event in scenario.initial_events
        if event.event_type == EventType.TASK_ARRIVAL
    )

    assert flows
    assert all(isinstance(flow, FlowRequest) for flow in flows)
    assert all(isinstance(task, TaskRequest) for task in tasks)
    assert compute_node_ids <= satellite_ids
    assert {flow.target_id for flow in flows if isinstance(flow, FlowRequest)} <= compute_node_ids
    assert tuple(flow.flow_id for flow in flows if isinstance(flow, FlowRequest)) == tuple(
        task.task_id for task in tasks if isinstance(task, TaskRequest)
    )


def test_demo_flow_and_task_demands_are_config_driven() -> None:
    scenario = build_demo_scenario(
        _demo_config(
            flow_demand_capacity=12.5,
            task_compute_demand=15.0,
            task_data_size=4.0,
        )
    )
    first_flow = next(
        event.payload
        for event in scenario.initial_events
        if event.event_type == EventType.FLOW_ARRIVAL
    )
    first_task = next(
        event.payload
        for event in scenario.initial_events
        if event.event_type == EventType.TASK_ARRIVAL
    )

    assert isinstance(first_flow, FlowRequest)
    assert isinstance(first_task, TaskRequest)
    assert first_flow.demand_capacity == 12.5
    assert first_task.compute_demand == 15.0
    assert first_task.data_size == 4.0
    assert scenario.frontend_config["scenario"]["traffic_model"] == {
        "flow_interval_seconds": 60,
        "task_interval_seconds": 60,
        "flow_demand_capacity": 12.5,
        "task_compute_demand": 15.0,
        "task_data_size": 4.0,
    }


def test_demo_compute_capacity_is_config_driven() -> None:
    scenario = build_demo_scenario(_demo_config(compute_capacity=18.0))

    assert tuple(node.node_id for node in scenario.compute_nodes) == ("sat-000", "sat-001")
    assert scenario.compute_nodes[0].capacity == 18.0
    assert scenario.compute_nodes[1].capacity == 20.5
    assert scenario.frontend_config["scenario"]["compute_capacity"] == 18.0


def _demo_config(**overrides: object) -> DemoConfig:
    values = dict(
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
    values.update(overrides)
    return DemoConfig(**values)
