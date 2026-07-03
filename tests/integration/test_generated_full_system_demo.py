from __future__ import annotations

from examples.generated_full_system_demo import run_generated_full_system_demo
from leo_twin.schema import EventType
from leo_twin.services.scenario_builder import FullSystemScenarioBuilderConfig


def test_generated_full_system_demo_runs_domain_lifecycle() -> None:
    result = run_generated_full_system_demo(
        FullSystemScenarioBuilderConfig(
            seed=11,
            satellite_count=4,
            user_count=6,
            compute_node_count=2,
            flow_count=4,
            orbit_plane_count=2,
            min_elevation_deg=-90.0,
            max_range_km=30000.0,
            compute_capacity=20.0,
        )
    )

    assert result.satellite_count == 4
    assert result.ground_endpoint_count == 6
    assert result.compute_node_count == 2
    assert result.flow_count == 4
    assert result.active_link_count > 0
    assert len(result.scheduled_tasks) == 4
    assert result.metrics_summary["routes_available"] == 4
    assert result.metrics_summary["route_latency_min"] > 0.0
    assert result.metrics_summary["route_capacity_max"] == 100.0
    assert result.metrics_summary["active_link_capacity_avg"] == 100.0
    assert result.metrics_summary["finished_tasks"] == 4
    assert EventType.ORBIT_UPDATE.value in result.processed_event_types
    assert EventType.ROUTE_UPDATE.value in result.processed_event_types
    assert EventType.TASK_START.value in result.processed_event_types
    assert EventType.TASK_FINISH.value in result.processed_event_types


def test_generated_full_system_demo_is_deterministic() -> None:
    config = FullSystemScenarioBuilderConfig(
        seed=12,
        satellite_count=3,
        user_count=5,
        compute_node_count=2,
        flow_count=3,
        orbit_plane_count=1,
        earth_rotation_rate_rad_s=0.000072921159,
        min_elevation_deg=-90.0,
        max_range_km=30000.0,
        compute_capacity=20.0,
    )

    assert run_generated_full_system_demo(config) == run_generated_full_system_demo(config)


def test_generated_full_system_demo_can_enable_space_links() -> None:
    result = run_generated_full_system_demo(
        FullSystemScenarioBuilderConfig(
            seed=13,
            satellite_count=3,
            user_count=3,
            compute_node_count=1,
            flow_count=0,
            orbit_plane_count=1,
            min_elevation_deg=-90.0,
            max_range_km=30000.0,
            space_link_max_range_km=50000.0,
            space_link_capacity=75.0,
            compute_capacity=20.0,
        )
    )

    assert result.active_link_count >= 12
