from __future__ import annotations

import json

import pytest

from leo_twin.services.scenario_builder import (
    FullSystemScenarioBuilderConfig,
    build_full_system_scenario,
    load_full_system_scenario_builder_config,
    scenario_builder_config_from_mapping,
)


def test_full_system_scenario_builder_generates_requested_counts() -> None:
    config = FullSystemScenarioBuilderConfig(
        seed=7,
        satellite_count=8,
        user_count=12,
        compute_node_count=3,
        flow_count=5,
        orbit_plane_count=4,
    )

    scenario = build_full_system_scenario(config)

    assert len(scenario.orbit_elements) == 8
    assert len(scenario.ground_endpoints) == 12
    assert len(scenario.compute_nodes) == 3
    assert len(scenario.flows) == 5
    assert len(scenario.tasks) == 5
    assert scenario.orbit_elements[0].satellite_id == "sat-00000"
    assert scenario.ground_endpoints[0].endpoint_id == "user-00000"
    assert scenario.compute_nodes[-1].node_id == "node-0002"


def test_full_system_scenario_builder_is_deterministic() -> None:
    config = FullSystemScenarioBuilderConfig(
        seed=99,
        satellite_count=6,
        user_count=4,
        compute_node_count=2,
        flow_count=4,
        orbit_plane_count=3,
    )

    assert build_full_system_scenario(config) == build_full_system_scenario(config)


def test_full_system_scenario_builder_seed_changes_initial_phase() -> None:
    base = FullSystemScenarioBuilderConfig(
        seed=1,
        satellite_count=4,
        user_count=4,
        compute_node_count=2,
        flow_count=2,
        orbit_plane_count=2,
    )
    shifted = FullSystemScenarioBuilderConfig(
        seed=2,
        satellite_count=4,
        user_count=4,
        compute_node_count=2,
        flow_count=2,
        orbit_plane_count=2,
    )

    first = build_full_system_scenario(base)
    second = build_full_system_scenario(shifted)

    assert first.orbit_elements[0].raan_deg != second.orbit_elements[0].raan_deg
    assert first.orbit_elements[0].mean_anomaly_deg != second.orbit_elements[0].mean_anomaly_deg
    assert first.ground_endpoints[0].position != second.ground_endpoints[0].position


def test_full_system_scenario_builder_aligns_flows_and_tasks() -> None:
    config = FullSystemScenarioBuilderConfig(
        satellite_count=4,
        user_count=3,
        compute_node_count=2,
        flow_count=6,
        orbit_plane_count=2,
        demand_capacity=2.5,
        task_compute_demand=12.0,
        task_data_size=4.0,
    )

    scenario = build_full_system_scenario(config)

    assert tuple(flow.flow_id for flow in scenario.flows) == tuple(
        task.task_id for task in scenario.tasks
    )
    assert tuple(flow.source_id for flow in scenario.flows) == tuple(
        task.source_id for task in scenario.tasks
    )
    assert tuple(flow.target_id for flow in scenario.flows) == (
        "node-0000",
        "node-0001",
        "node-0000",
        "node-0001",
        "node-0000",
        "node-0001",
    )
    assert scenario.flows[0].demand_capacity == 2.5
    assert scenario.tasks[0].compute_demand == 12.0
    assert scenario.tasks[0].data_size == 4.0


def test_full_system_scenario_builder_rejects_invalid_config() -> None:
    with pytest.raises(ValueError, match="orbit_plane_count"):
        FullSystemScenarioBuilderConfig(
            satellite_count=2,
            user_count=2,
            compute_node_count=1,
            orbit_plane_count=3,
        )

    with pytest.raises(ValueError, match="flow_count"):
        FullSystemScenarioBuilderConfig(flow_count=-1)


def test_scenario_builder_config_from_mapping_rejects_unknown_fields() -> None:
    with pytest.raises(ValueError, match="unknown scenario builder fields"):
        scenario_builder_config_from_mapping({"satellite_count": 4, "unexpected": 1})


def test_load_full_system_scenario_builder_config_from_json(tmp_path) -> None:
    config_path = tmp_path / "scenario.json"
    config_path.write_text(
        json.dumps(
            {
                "seed": 5,
                "satellite_count": 4,
                "user_count": 8,
                "compute_node_count": 2,
                "flow_count": 3,
                "orbit_plane_count": 2,
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    config = load_full_system_scenario_builder_config(config_path)

    assert config.seed == 5
    assert config.satellite_count == 4
    assert config.user_count == 8
    assert config.compute_node_count == 2
    assert config.flow_count == 3
    assert config.orbit_plane_count == 2
    assert config.max_range_km == 2000.0


def test_default_generated_scenario_config_file_loads() -> None:
    config = load_full_system_scenario_builder_config()

    assert config.satellite_count == 6
    assert config.user_count == 12
    assert config.compute_node_count == 3
    assert config.flow_count == 6
