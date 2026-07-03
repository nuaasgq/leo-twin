from __future__ import annotations

import pytest

from examples.full_system_pipeline_demo import run_full_system_pipeline_demo
from leo_twin.schema import EventType


def test_full_domain_pipeline_runs_orbit_network_compute_lifecycle() -> None:
    result = run_full_system_pipeline_demo()
    domain_event_types = tuple(
        event_type
        for event_type in result.processed_event_types
        if event_type != "_COMPUTE_SCHEDULE_TICK"
    )

    assert domain_event_types == (
        EventType.TASK_ARRIVAL.value,
        EventType.ORBIT_TRIGGER.value,
        EventType.ORBIT_UPDATE.value,
        EventType.ORBIT_UPDATE.value,
        EventType.ACCESS_START.value,
        EventType.LINK_UPDATE.value,
        EventType.FLOW_ARRIVAL.value,
        EventType.ROUTE_UPDATE.value,
        EventType.ROUTE_UPDATE.value,
        EventType.ROUTE_UPDATE.value,
        EventType.TASK_START.value,
        "COMPUTE_NODE_UPDATE",
        EventType.TASK_FINISH.value,
        "COMPUTE_NODE_UPDATE",
    )
    assert result.metrics_event_types == (
        EventType.ORBIT_UPDATE.value,
        EventType.ACCESS_START.value,
        EventType.LINK_UPDATE.value,
        EventType.ROUTE_UPDATE.value,
        EventType.TASK_START.value,
        "COMPUTE_NODE_UPDATE",
        EventType.TASK_FINISH.value,
        "COMPUTE_NODE_UPDATE",
    )
    assert result.metrics_summary["event_count"] == 8
    assert result.metrics_summary["active_links"] == 1
    assert result.metrics_summary["available_link_capacity"] == pytest.approx(4161.620976)
    assert result.metrics_summary["routes_total"] == 1
    assert result.metrics_summary["routes_available"] == 1
    assert result.metrics_summary["running_tasks"] == 0
    assert result.metrics_summary["finished_tasks"] == 1
    assert result.metrics_summary["last_sim_time"] == pytest.approx(4.006879)
    assert result.stack_layer_statuses == (
        ("APPLICATION", "OK"),
        ("TRANSPORT", "OK"),
        ("NETWORK", "OK"),
        ("DATA_LINK", "OK"),
        ("PHYSICAL", "OK"),
        ("CHANNEL", "OK"),
    )
    attributes_by_layer = {layer: dict(attributes) for layer, attributes in result.stack_layer_attributes}
    assert attributes_by_layer["TRANSPORT"]["transport"] == "TCP"
    assert attributes_by_layer["NETWORK"]["latency"] == "2.004196"
    assert attributes_by_layer["NETWORK"]["capacity"] == "3726.592864"
    assert attributes_by_layer["PHYSICAL"]["path_loss_db"] == "174.443613"
    assert attributes_by_layer["PHYSICAL"]["received_power_dbw"] == "-90.943613"
    assert attributes_by_layer["CHANNEL"]["medium"] == "SPACE_GROUND"
    assert attributes_by_layer["CHANNEL"]["capacity_mbps"] == "4161.620976"
    assert attributes_by_layer["CHANNEL"]["snr_db"] == "25.041874"
    assert len(result.scheduled_tasks) == 1
    assert result.scheduled_tasks[0].task_id == "flow-001"
    assert result.scheduled_tasks[0].start_time == pytest.approx(2.006879)
    assert result.scheduled_tasks[0].finish_time == pytest.approx(4.006879)


def test_full_domain_pipeline_is_deterministic() -> None:
    first = run_full_system_pipeline_demo()
    second = run_full_system_pipeline_demo()

    assert first == second
