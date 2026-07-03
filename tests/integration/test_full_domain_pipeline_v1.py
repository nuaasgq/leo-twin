from __future__ import annotations

from examples.full_system_pipeline_demo import run_full_system_pipeline_demo
from leo_twin.schema import EventType


def test_full_domain_pipeline_runs_orbit_network_compute_lifecycle() -> None:
    result = run_full_system_pipeline_demo()

    assert result.processed_event_types == (
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
    assert result.metrics_summary["available_link_capacity"] == 5.0
    assert result.metrics_summary["routes_total"] == 1
    assert result.metrics_summary["routes_available"] == 1
    assert result.metrics_summary["running_tasks"] == 0
    assert result.metrics_summary["finished_tasks"] == 1
    assert result.stack_layer_statuses == (
        ("APPLICATION", "OK"),
        ("TRANSPORT", "OK"),
        ("NETWORK", "OK"),
        ("DATA_LINK", "OK"),
        ("PHYSICAL", "OK"),
        ("CHANNEL", "OK"),
    )
    assert len(result.scheduled_tasks) == 1
    assert result.scheduled_tasks[0].task_id == "flow-001"
    assert result.scheduled_tasks[0].start_time == 4.0
    assert result.scheduled_tasks[0].finish_time == 6.0


def test_full_domain_pipeline_is_deterministic() -> None:
    first = run_full_system_pipeline_demo()
    second = run_full_system_pipeline_demo()

    assert first == second
