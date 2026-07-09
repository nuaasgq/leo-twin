import csv
import io
import json
from math import sqrt

import pytest

from leo_twin.schema import (
    ComputeNodeState,
    EventType,
    FlowState,
    LinkState,
    MetricRecord,
    Route,
    SatelliteState,
    SimEvent,
    TaskState,
)
from leo_twin.models.compute import COMPUTE_NODE_UPDATE
from leo_twin.services.metrics import MetricsCollector


class _ScheduledEventSink:
    def __init__(self) -> None:
        self.events: list[SimEvent] = []

    def schedule_event(self, event: SimEvent) -> None:
        self.events.append(event)


def _event(
    event_id: str,
    sim_time: float,
    event_type: str,
    payload: object,
    source: str,
) -> SimEvent:
    return SimEvent(
        event_id=event_id,
        sim_time=sim_time,
        priority=0,
        source=source,
        target="metrics",
        event_type=event_type,
        payload=payload,
    )


def _sample_events() -> tuple[SimEvent, ...]:
    return (
        _event(
            "orbit-1",
            0.0,
            EventType.ORBIT_UPDATE,
            SatelliteState(
                satellite_id="sat-a",
                sim_time=0.0,
                position=(1.0, 2.0, 3.0),
                velocity=(0.0, 0.1, 0.2),
                status="online",
            ),
            "orbit",
        ),
        _event(
            "access-start-1",
            1.0,
            EventType.ACCESS_START,
            LinkState(
                source_id="sat-a",
                target_id="user-1",
                latency=10.0,
                capacity=50.0,
                availability=True,
            ),
            "network",
        ),
        _event(
            "link-update-1",
            1.5,
            EventType.LINK_UPDATE,
            LinkState(
                source_id="sat-a",
                target_id="user-1",
                latency=8.0,
                capacity=60.0,
                availability=True,
            ),
            "network",
        ),
        _event(
            "route-1",
            2.0,
            EventType.ROUTE_UPDATE,
            Route(
                route_id="route:flow-1",
                flow_id="flow-1",
                path=("user-1", "sat-a", "user-2"),
                latency=16.0,
                capacity=60.0,
                available=True,
            ),
            "network",
        ),
        _event(
            "flow-1",
            3.0,
            EventType.FLOW_COMPLETE,
            FlowState(
                flow_id="flow-1",
                route_id="route:flow-1",
                source_id="user-1",
                target_id="user-2",
                status="complete",
            ),
            "network",
        ),
        _event(
            "task-start-1",
            4.0,
            EventType.TASK_START,
            TaskState(
                task_id="task-1",
                node_id="sat-a",
                sim_time=4.0,
                progress=0.0,
                status="running",
            ),
            "compute",
        ),
        _event(
            "task-finish-1",
            5.0,
            EventType.TASK_FINISH,
            TaskState(
                task_id="task-1",
                node_id="sat-a",
                sim_time=5.0,
                progress=1.0,
                status="finished",
            ),
            "compute",
        ),
        _event(
            "access-end-1",
            6.0,
            EventType.ACCESS_END,
            LinkState(
                source_id="sat-a",
                target_id="user-1",
                latency=8.0,
                capacity=60.0,
                availability=False,
            ),
            "network",
        ),
    )


def test_metrics_collector_kpis_are_consistent_with_observations() -> None:
    collector = MetricsCollector()

    for event in _sample_events():
        collector.observe(event)

    summary = collector.summary()
    records = collector.records()

    assert summary["event_count"] == 8
    assert summary["unique_satellites"] == 1
    assert summary["satellite_altitude_avg"] == pytest.approx(sqrt(14.0) - 6371.0)
    assert summary["satellite_altitude_max"] == pytest.approx(sqrt(14.0) - 6371.0)
    assert summary["satellite_altitude_min"] == pytest.approx(sqrt(14.0) - 6371.0)
    assert summary["observed_links"] == 1
    assert summary["active_link_capacity_avg"] == 0.0
    assert summary["active_link_capacity_max"] == 0.0
    assert summary["active_link_capacity_min"] == 0.0
    assert summary["active_link_latency_avg"] == 0.0
    assert summary["active_links"] == 0
    assert summary["available_link_capacity"] == 0.0
    assert summary["routes_total"] == 1
    assert summary["routes_available"] == 1
    assert summary["route_capacity_max"] == 60.0
    assert summary["route_capacity_min"] == 60.0
    assert summary["route_hop_count_avg"] == 2.0
    assert summary["route_hop_count_max"] == 2
    assert summary["route_hop_count_min"] == 2
    assert summary["route_latency_avg"] == 16.0
    assert summary["route_latency_min"] == 16.0
    assert summary["completed_flows"] == 1
    assert summary["running_tasks"] == 0
    assert summary["finished_tasks"] == 1
    assert summary["deadline_missed_tasks"] == 0
    assert summary["network_quality_offered_route_capacity_mbps"] == 60.0
    assert summary["network_quality_estimated_delivered_throughput_mbps"] == 60.0
    assert summary["network_quality_estimated_available_throughput_mbps"] == 60.0
    assert summary["network_quality_route_latency_avg_s"] == 16.0
    assert summary["network_quality_route_latency_min_s"] == 16.0
    assert summary["network_quality_route_latency_max_s"] == 16.0
    assert summary["network_quality_delay_variation_proxy_s"] == 0.0
    assert summary["network_quality_route_blocking_ratio"] == 0.0
    assert summary["network_quality_failed_flow_ratio"] == 0.0
    assert summary["network_quality_congestion_proxy"] == 0.0
    assert summary["network_quality_congestion_loss_proxy_rate"] == 0.0
    assert summary["network_quality_loss_proxy_rate"] == 0.0
    assert summary["network_quality_metric_model"] == "FLOW_LEVEL_PROXY"
    assert (
        summary["network_quality_loss_metric_semantics"]
        == "LOSS_PROXY_RATE_NOT_PACKET_LOSS"
    )
    assert (
        summary["network_quality_delay_variation_metric_semantics"]
        == "DELAY_VARIATION_PROXY_NOT_PACKET_JITTER"
    )
    assert summary["network_quality_loss_zero_reason"] == "NO_LOSS_PROXY_TRIGGERED"
    assert summary["network_quality_loss_zero_reason_label"] == (
        "路由阻塞、失败流、链路拥塞和业务压力均未触发损耗代理"
    )
    assert (
        summary["network_quality_delay_variation_zero_reason"]
        == "INSUFFICIENT_VARIATION_SAMPLE"
    )
    assert summary["network_quality_delay_variation_zero_reason_label"] == (
        "时延样本不足，无法形成离散度代理"
    )
    assert summary["network_quality_proxy_note"] == (
        "Flow-level proxy only; no packet-level simulation is performed."
    )
    assert summary["task_duration_avg"] == 1.0
    assert summary["task_duration_max"] == 1.0
    assert summary["task_duration_min"] == 1.0
    assert summary["last_sim_time"] == 6.0
    assert summary["events.ACCESS_START.count"] == 1
    assert summary["events.LINK_UPDATE.count"] == 1
    assert summary["events.TASK_FINISH.count"] == 1

    assert _last_record(records, "events.observed.count").value == float(summary["event_count"])
    assert _last_record(records, "satellite.altitude_km").value == pytest.approx(
        sqrt(14.0) - 6371.0
    )
    assert _last_record(records, "satellite.latitude_deg").value == pytest.approx(
        53.30077479951012
    )
    assert _last_record(records, "satellite.longitude_deg").value == pytest.approx(
        63.43494882292201
    )
    assert _last_record(records, "links.active.count").value == float(summary["active_links"])
    assert _last_record(records, "links.available_capacity.total").value == summary[
        "available_link_capacity"
    ]
    assert _last_record(records, "routes.total.count").value == float(summary["routes_total"])
    assert _last_record(records, "routes.available.count").value == float(
        summary["routes_available"]
    )
    assert _last_record(records, "route.hop_count").value == 2.0
    assert _last_record(records, "route.path").value == "user-1 -> sat-a -> user-2"
    assert _last_record(records, "flows.completed.count").value == float(
        summary["completed_flows"]
    )
    assert _last_record(records, "tasks.running.count").value == float(summary["running_tasks"])
    assert _last_record(records, "tasks.finished.count").value == float(
        summary["finished_tasks"]
    )
    assert _last_record(records, "task.duration").value == 1.0
    assert _last_record(records, "tasks.deadline_missed.count").value == float(
        summary["deadline_missed_tasks"]
    )


def test_metrics_collector_reports_flow_level_network_quality_proxy() -> None:
    collector = MetricsCollector()
    for event in (
        _event(
            "route-a",
            1.0,
            EventType.ROUTE_UPDATE,
            Route(
                route_id="route-a",
                flow_id="flow-a",
                path=("user-a", "sat-a", "user-b"),
                latency=0.02,
                capacity=120.0,
                available=True,
            ),
            "network",
        ),
        _event(
            "route-b",
            1.0,
            EventType.ROUTE_UPDATE,
            Route(
                route_id="route-b",
                flow_id="flow-b",
                path=(),
                latency=0.0,
                capacity=0.0,
                available=False,
            ),
            "network",
        ),
        _event(
            "route-c",
            1.0,
            EventType.ROUTE_UPDATE,
            Route(
                route_id="route-c",
                flow_id="flow-c",
                path=("user-c", "sat-c", "sat-d", "user-d"),
                latency=0.08,
                capacity=80.0,
                available=True,
            ),
            "network",
        ),
        _event(
            "flow-a",
            2.0,
            EventType.FLOW_COMPLETE,
            FlowState(
                flow_id="flow-a",
                route_id="route-a",
                source_id="user-a",
                target_id="user-b",
                status="complete",
            ),
            "network",
        ),
    ):
        collector.observe(event)

    summary = collector.summary()

    assert summary["network_quality_available_route_count"] == 2
    assert summary["network_quality_route_decision_count"] == 3
    assert summary["network_quality_available_route_decision_count"] == 2
    assert summary["network_quality_unavailable_route_decision_count"] == 1
    assert summary["network_quality_topology_blocked_route_count"] == 1
    assert summary["network_quality_pressure_admission_rejected_route_count"] == 0
    assert summary["network_quality_queue_pressure_route_count"] == 0
    assert summary["network_quality_route_admission_model"] == "FLOW_PRESSURE_ADMISSION_V1"
    assert summary["network_quality_route_admission_source"] == "ROUTE_UPDATE"
    assert summary["network_quality_offered_route_capacity_mbps"] == 200.0
    assert summary["network_quality_estimated_delivered_throughput_mbps"] == 120.0
    assert summary["network_quality_route_latency_avg_s"] == pytest.approx(0.05)
    assert summary["network_quality_route_latency_min_s"] == 0.02
    assert summary["network_quality_route_latency_max_s"] == 0.08
    assert summary["network_quality_delay_variation_proxy_s"] == pytest.approx(0.03)
    assert summary["network_quality_route_blocking_ratio"] == pytest.approx(1 / 3)
    assert summary["network_quality_failed_flow_ratio"] == 0.0
    assert summary["network_quality_congestion_proxy"] == 0.0
    assert summary["network_quality_congestion_loss_proxy_rate"] == 0.0
    assert summary["network_quality_loss_proxy_rate"] == pytest.approx(1 / 3)


def test_metrics_collector_reports_dynamic_network_quality_proxy() -> None:
    collector = MetricsCollector()
    for event in (
        _event(
            "link-a",
            1.0,
            EventType.LINK_UPDATE,
            LinkState(
                source_id="sat-a",
                target_id="sat-b",
                latency=0.01,
                capacity=100.0,
                availability=True,
                utilization=0.95,
            ),
            "network",
        ),
        _event(
            "route-a-1",
            1.0,
            EventType.ROUTE_UPDATE,
            Route(
                route_id="route-a",
                flow_id="flow-a",
                path=("user-a", "sat-a", "sat-b", "user-b"),
                latency=0.02,
                capacity=100.0,
                available=True,
            ),
            "network",
        ),
        _event(
            "route-a-2",
            2.0,
            EventType.ROUTE_UPDATE,
            Route(
                route_id="route-a",
                flow_id="flow-a",
                path=("user-a", "sat-a", "sat-b", "user-b"),
                latency=0.05,
                capacity=100.0,
                available=True,
            ),
            "network",
        ),
        _event(
            "flow-a",
            3.0,
            EventType.FLOW_COMPLETE,
            FlowState(
                flow_id="flow-a",
                route_id="route-a",
                source_id="user-a",
                target_id="user-b",
                status="complete",
            ),
            "network",
        ),
    ):
        collector.observe(event)

    summary = collector.summary()

    assert summary["network_quality_available_route_count"] == 1
    assert summary["network_quality_offered_route_capacity_mbps"] == 100.0
    assert summary["network_quality_estimated_delivered_throughput_mbps"] == 100.0
    assert summary["network_quality_route_latency_avg_s"] == pytest.approx(0.05)
    assert summary["network_quality_delay_variation_proxy_s"] == pytest.approx(0.03)
    assert summary["network_quality_failed_flow_ratio"] == 0.0
    assert summary["network_quality_congestion_proxy"] == pytest.approx(0.95)
    assert summary["network_quality_congestion_loss_proxy_rate"] == pytest.approx(0.075)
    assert summary["network_quality_loss_proxy_rate"] == pytest.approx(0.075)
    assert summary["network_quality_estimated_available_throughput_mbps"] == pytest.approx(
        92.5
    )


def test_metrics_collector_reports_route_constraint_summary() -> None:
    collector = MetricsCollector()
    for event in (
        _event(
            "link-hot",
            1.0,
            EventType.LINK_UPDATE,
            LinkState(
                source_id="sat-a",
                target_id="sat-b",
                latency=0.02,
                capacity=80.0,
                availability=True,
                utilization=0.92,
            ),
            "network",
        ),
        _event(
            "link-low",
            1.0,
            EventType.LINK_UPDATE,
            LinkState(
                source_id="sat-b",
                target_id="sat-c",
                latency=0.05,
                capacity=20.0,
                availability=True,
                utilization=0.7,
            ),
            "network",
        ),
        _event(
            "route-wide",
            2.0,
            EventType.ROUTE_UPDATE,
            Route(
                route_id="route-wide",
                flow_id="flow-wide",
                path=("sat-a", "sat-b"),
                latency=0.02,
                capacity=100.0,
                available=True,
                demand_capacity=50.0,
            ),
            "network",
        ),
        _event(
            "route-low",
            2.0,
            EventType.ROUTE_UPDATE,
            Route(
                route_id="route-low",
                flow_id="flow-low",
                path=("sat-a", "sat-b", "sat-c"),
                latency=0.08,
                capacity=20.0,
                available=True,
                demand_capacity=30.0,
                loss_rate=0.1,
            ),
            "network",
        ),
        _event(
            "route-down",
            2.0,
            EventType.ROUTE_UPDATE,
            Route(
                route_id="route-down",
                flow_id="flow-down",
                path=(),
                latency=0.0,
                capacity=0.0,
                available=False,
                demand_capacity=10.0,
            ),
            "network",
        ),
    ):
        collector.observe(event)

    summary = collector.summary()

    assert summary["network_constraint_summary_source"] == "BACKEND_METRICS_COLLECTOR"
    assert summary["network_constraint_route_count"] == 3
    assert summary["network_constraint_available_route_count"] == 2
    assert summary["network_constraint_unavailable_route_count"] == 1
    assert summary["network_constraint_over_demand_route_count"] == 2
    assert summary["network_constraint_active_link_count"] == 2
    assert summary["network_constraint_overloaded_link_count"] == 1
    assert summary["network_constraint_top_route_id"] == "route-down"
    assert summary["network_constraint_top_route_flow_id"] == "flow-down"
    assert summary["network_constraint_top_route_available"] is False
    assert summary["network_constraint_top_route_capacity_mbps"] == 0.0
    assert summary["network_constraint_top_route_latency_s"] == 0.0
    assert summary["network_constraint_top_route_hop_count"] == 0
    assert summary["network_constraint_top_route_demand_mbps"] == 10.0
    assert summary["network_constraint_top_route_loss_rate"] == 0.0
    assert summary["network_constraint_top_route_pressure_proxy"] == 1.0
    assert summary["network_constraint_top_route_path"] == ""
    assert summary["network_constraint_top_link_id"] == "sat-a->sat-b"
    assert summary["network_constraint_top_link_capacity_mbps"] == 80.0
    assert summary["network_constraint_top_link_latency_s"] == 0.02
    assert summary["network_constraint_top_link_utilization"] == pytest.approx(0.92)


def test_metrics_collector_reports_network_flow_lifecycle_summary() -> None:
    collector = MetricsCollector()
    collector.observe(
        _event(
            "route-active",
            1.0,
            EventType.ROUTE_UPDATE,
            Route(
                route_id="route-active",
                flow_id="flow-active",
                path=("user-a", "sat-a", "user-b"),
                latency=0.05,
                capacity=100.0,
                available=True,
                demand_capacity=30.0,
            ),
            "network",
        )
    )
    collector.observe(
        _event(
            "route-blocked",
            2.0,
            EventType.ROUTE_UPDATE,
            Route(
                route_id="route-blocked",
                flow_id="flow-blocked",
                path=(),
                latency=0.0,
                capacity=0.0,
                available=False,
                demand_capacity=15.0,
            ),
            "network",
        )
    )

    active = collector.summary()

    assert active["network_flow_lifecycle_model"] == (
        "ROUTE_UPDATE_TO_FLOW_COMPLETE_WINDOW"
    )
    assert active["network_flow_lifecycle_source"] == "BACKEND_METRICS_COLLECTOR"
    assert active["network_flow_lifecycle_packet_level_simulation"] is False
    assert active["network_flow_lifecycle_active_flow_count"] == 2
    assert active["network_flow_lifecycle_active_available_flow_count"] == 1
    assert active["network_flow_lifecycle_active_blocked_flow_count"] == 1
    assert active["network_flow_lifecycle_active_demand_mbps"] == 45.0
    assert active["network_flow_lifecycle_active_capacity_mbps"] == 100.0
    assert active["network_flow_lifecycle_active_latency_avg_s"] == 0.05
    assert active["network_flow_lifecycle_oldest_active_age_s"] == 1.0
    assert active["network_flow_lifecycle_completed_flow_count"] == 0

    collector.observe(
        _event(
            "flow-blocked",
            2.0,
            EventType.FLOW_COMPLETE,
            FlowState(
                flow_id="flow-blocked",
                route_id="route-blocked",
                source_id="user-c",
                target_id="user-d",
                status="blocked",
            ),
            "network",
        )
    )
    partial = collector.summary()

    assert partial["network_flow_lifecycle_active_flow_count"] == 1
    assert partial["network_flow_lifecycle_active_blocked_flow_count"] == 0
    assert partial["network_flow_lifecycle_completed_flow_count"] == 1
    assert partial["network_flow_lifecycle_successful_flow_count"] == 0
    assert partial["network_flow_lifecycle_failed_flow_count"] == 1

    collector.observe(
        _event(
            "flow-active",
            4.0,
            EventType.FLOW_COMPLETE,
            FlowState(
                flow_id="flow-active",
                route_id="route-active",
                source_id="user-a",
                target_id="user-b",
                status="complete",
                latency=0.05,
                capacity=90.0,
            ),
            "network",
        )
    )
    complete = collector.summary()

    assert complete["network_flow_lifecycle_active_flow_count"] == 0
    assert complete["network_flow_lifecycle_active_demand_mbps"] == 0.0
    assert complete["network_flow_lifecycle_oldest_active_age_s"] == 0.0
    assert complete["network_flow_lifecycle_completed_flow_count"] == 2
    assert complete["network_flow_lifecycle_successful_flow_count"] == 1
    assert complete["network_flow_lifecycle_failed_flow_count"] == 1

def test_metrics_collector_reports_effective_flow_level_network_quality() -> None:
    collector = MetricsCollector()
    last_records: tuple[MetricRecord, ...] = ()
    for event in (
        _event(
            "route-a",
            1.0,
            EventType.ROUTE_UPDATE,
            Route(
                route_id="route-a",
                flow_id="flow-a",
                path=("user-a", "sat-a", "user-b"),
                latency=0.02,
                capacity=100.0,
                available=True,
            ),
            "network",
        ),
        _event(
            "route-b",
            1.0,
            EventType.ROUTE_UPDATE,
            Route(
                route_id="route-b",
                flow_id="flow-b",
                path=("user-c", "sat-b", "user-d"),
                latency=0.04,
                capacity=100.0,
                available=True,
            ),
            "network",
        ),
        _event(
            "flow-a",
            2.0,
            EventType.FLOW_COMPLETE,
            FlowState(
                flow_id="flow-a",
                route_id="route-a",
                source_id="user-a",
                target_id="user-b",
                status="complete",
                latency=0.025,
                capacity=90.0,
            ),
            "network",
        ),
        _event(
            "flow-b",
            2.5,
            EventType.FLOW_COMPLETE,
            FlowState(
                flow_id="flow-b",
                route_id="route-b",
                source_id="user-c",
                target_id="user-d",
                status="complete",
                latency=0.055,
                capacity=90.0,
            ),
            "network",
        ),
    ):
        last_records = collector.observe(event)

    summary = collector.summary()

    assert summary["network_quality_flow_success_count"] == 2
    assert summary["network_quality_flow_failure_count"] == 0
    assert summary["network_quality_flow_success_ratio"] == 1.0
    assert summary["network_quality_flow_latency_avg_s"] == pytest.approx(0.04)
    assert summary["network_quality_flow_latency_variation_proxy_s"] == pytest.approx(
        0.015
    )
    assert summary["network_quality_flow_delivered_capacity_mbps"] == 180.0
    assert summary["network_quality_throughput_pressure_proxy"] == pytest.approx(0.9)
    assert summary["network_quality_pressure_loss_proxy_rate"] == pytest.approx(0.05)
    assert summary["network_quality_effective_loss_proxy_rate"] == pytest.approx(0.05)
    assert summary["network_quality_effective_latency_avg_s"] == pytest.approx(0.04)
    assert summary["network_quality_effective_delay_variation_proxy_s"] == pytest.approx(
        0.015
    )
    assert summary["network_quality_effective_available_throughput_mbps"] == pytest.approx(
        190.0
    )
    assert summary["network_quality_effective_throughput_mbps"] == 180.0
    assert summary["network_quality_throughput_source"] == "COMPLETED_FLOW_CAPACITY"
    assert summary["network_quality_throughput_source_label"] == "已完成流容量"
    assert summary["network_quality_latency_source"] == "COMPLETED_FLOW_LATENCY"
    assert summary["network_quality_latency_source_label"] == "已完成流时延"
    assert summary["network_quality_loss_source"] == "PRESSURE_LOSS_PROXY"
    assert summary["network_quality_loss_source_label"] == "业务压力损耗代理"
    assert summary["network_quality_loss_zero_reason"] == "POSITIVE_PROXY"
    assert summary["network_quality_loss_zero_reason_label"] == "当前代理指标为正值"
    assert summary["network_quality_delay_variation_source"] == "FLOW_LATENCY_VARIATION"
    assert (
        summary["network_quality_delay_variation_source_label"]
        == "流完成时延离散度"
    )
    assert summary["network_quality_delay_variation_zero_reason"] == "POSITIVE_PROXY"
    assert (
        summary["network_quality_delay_variation_zero_reason_label"]
        == "当前代理指标为正值"
    )
    assert summary["network_quality_provenance_note"] == (
        "Flow-level KPI provenance from route, link, active-flow, and "
        "completed-flow state; no packet-level samples are used."
    )
    assert _last_record(
        last_records,
        "network.quality.effective_throughput_mbps",
    ).value == 180.0
    assert _last_record(
        last_records,
        "network.quality.effective_latency_s",
    ).value == pytest.approx(0.04)
    assert _last_record(
        last_records,
        "network.quality.effective_loss_proxy_rate",
    ).value == pytest.approx(0.05)
    assert _last_record(
        last_records,
        "network.quality.effective_delay_variation_s",
    ).value == pytest.approx(0.015)


def test_metrics_collector_reports_route_admission_and_queue_pressure_evidence() -> None:
    collector = MetricsCollector()
    for event in (
        _event(
            "route-queued",
            1.0,
            EventType.ROUTE_UPDATE,
            Route(
                route_id="route-queued",
                flow_id="flow-queued",
                path=("user-a", "sat-a", "user-b"),
                latency=0.03,
                capacity=80.0,
                available=True,
                demand_capacity=90.0,
                loss_rate=0.1,
                pressure_edge_states=(
                    {
                        "edge_id": "user-a->sat-a",
                        "source_id": "user-a",
                        "target_id": "sat-a",
                        "pressure_state": "SATURATED",
                        "active_demand_mbps": 70.0,
                        "incoming_demand_mbps": 20.0,
                        "projected_demand_mbps": 90.0,
                        "capacity_mbps": 80.0,
                        "projected_utilization": 1.125,
                        "pressure_utilization": 1.0,
                        "queued_demand_mbps": 10.0,
                        "queue_delay_s": 0.01,
                        "loss_proxy_rate": 0.1,
                        "admission_rejected": False,
                    },
                ),
            ),
            "network",
        ),
        _event(
            "route-rejected",
            1.0,
            EventType.ROUTE_UPDATE,
            Route(
                route_id="route-rejected",
                flow_id="flow-rejected",
                path=("user-c", "sat-c", "user-d"),
                latency=0.04,
                capacity=0.0,
                available=False,
                demand_capacity=30.0,
                loss_rate=0.2,
                pressure_edge_states=(
                    {
                        "edge_id": "user-c->sat-c",
                        "source_id": "user-c",
                        "target_id": "sat-c",
                        "pressure_state": "ADMISSION_REJECTED",
                        "active_demand_mbps": 60.0,
                        "incoming_demand_mbps": 30.0,
                        "projected_demand_mbps": 90.0,
                        "capacity_mbps": 50.0,
                        "projected_utilization": 1.8,
                        "pressure_utilization": 1.0,
                        "queued_demand_mbps": 40.0,
                        "queue_delay_s": 0.02,
                        "loss_proxy_rate": 0.1,
                        "admission_rejected": True,
                    },
                ),
            ),
            "network",
        ),
    ):
        collector.observe(event)

    summary = collector.summary()

    assert summary["network_quality_route_decision_count"] == 2
    assert summary["network_quality_available_route_decision_count"] == 1
    assert summary["network_quality_unavailable_route_decision_count"] == 1
    assert summary["network_quality_topology_blocked_route_count"] == 0
    assert summary["network_quality_pressure_admission_rejected_route_count"] == 1
    assert summary["network_quality_pressure_admission_rejection_ratio"] == pytest.approx(0.5)
    assert summary["network_quality_queue_pressure_route_count"] == 1
    assert summary["network_quality_saturated_route_count"] == 1
    assert summary["network_quality_max_route_pressure_loss_rate"] == pytest.approx(0.2)
    assert summary["network_quality_queue_pressure_proxy"] == pytest.approx(1.0)
    assert summary["network_quality_route_blocking_ratio"] == pytest.approx(0.5)
    assert summary["network_quality_effective_loss_proxy_rate"] == pytest.approx(0.5)
    evidence = collector.route_pressure_evidence()
    assert evidence["version"] == "v1"
    assert evidence["source"] == "BACKEND_METRICS_COLLECTOR"
    assert evidence["pressure_model"] == "FLOW_PRESSURE_ADMISSION_V1"
    assert evidence["packet_level_simulation"] is False
    assert evidence["route_count"] == 2
    assert evidence["pressure_admission_rejected_count"] == 1
    assert evidence["queued_route_count"] == 0
    assert evidence["saturated_route_count"] == 1
    assert evidence["pressure_edge_count"] == 2
    assert evidence["pressure_admission_rejected_edge_count"] == 1
    assert evidence["saturated_edge_count"] == 1
    assert evidence["max_edge_projected_utilization"] == pytest.approx(1.8)
    assert evidence["max_edge_queue_delay_s"] == pytest.approx(0.02)
    assert evidence["edge_items"][0]["edge_id"] == "user-c->sat-c"
    assert evidence["edge_items"][0]["pressure_state"] == "ADMISSION_REJECTED"
    assert evidence["edge_items"][1]["pressure_state"] == "SATURATED"
    assert evidence["items"][0]["route_id"] == "route-rejected"
    assert evidence["items"][0]["pressure_state"] == "ADMISSION_REJECTED"
    assert evidence["items"][0]["blocked_reason"] == "flow_pressure_admission_limit"
    assert evidence["items"][1]["pressure_state"] == "SATURATED"
    assert evidence["items"][1]["queue_over_demand_mbps"] == pytest.approx(10.0)


def test_metrics_collector_uses_route_demand_for_network_pressure_proxy() -> None:
    collector = MetricsCollector()
    collector.observe(
        _event(
            "route-demand",
            1.0,
            EventType.ROUTE_UPDATE,
            Route(
                route_id="route-demand",
                flow_id="flow-demand",
                path=("user-a", "sat-a", "user-b"),
                latency=0.02,
                capacity=100.0,
                available=True,
                demand_capacity=90.0,
            ),
            "network",
        )
    )

    summary = collector.summary()

    assert summary["network_quality_requested_route_demand_mbps"] == 90.0
    assert summary["network_quality_available_route_demand_mbps"] == 90.0
    assert summary["network_quality_demand_pressure_proxy"] == pytest.approx(0.9)
    assert summary["network_quality_demand_loss_proxy_rate"] == pytest.approx(0.05)
    assert summary["network_quality_pressure_loss_proxy_rate"] == pytest.approx(0.05)
    assert summary["network_quality_effective_loss_proxy_rate"] == pytest.approx(0.05)
    assert summary["network_quality_effective_throughput_mbps"] == pytest.approx(95.0)


def test_metrics_summary_uses_active_inflight_flow_after_runtime_target_advances() -> None:
    collector = MetricsCollector(metric_sample_interval=100)
    collector.observe(
        _event(
            "route-active",
            1.0,
            EventType.ROUTE_UPDATE,
            Route(
                route_id="route-active",
                flow_id="flow-active",
                path=("user-a", "sat-a", "user-b"),
                latency=0.05,
                capacity=100.0,
                available=True,
                demand_capacity=70.0,
            ),
            "network",
        )
    )

    event_time_summary = collector.summary()
    runtime_summary = collector.summary(sim_time=10.0)
    runtime_tail = collector.kpi_time_series(sim_time=10.0)["samples"][-1]

    assert event_time_summary["network_quality_active_flow_count"] == 0
    assert event_time_summary["network_quality_throughput_source"] == (
        "AVAILABLE_ROUTE_CAPACITY_AFTER_LOSS"
    )
    assert runtime_summary["network_quality_active_flow_count"] == 1
    assert runtime_summary["network_quality_active_available_flow_count"] == 1
    assert runtime_summary["network_quality_active_flow_demand_mbps"] == 70.0
    assert runtime_summary["network_quality_active_flow_capacity_mbps"] == 70.0
    assert runtime_summary["network_quality_active_flow_latency_avg_s"] == 0.05
    assert runtime_summary["network_quality_active_flow_pressure_proxy"] == 0.7
    assert runtime_summary["network_quality_effective_throughput_mbps"] == 70.0
    assert runtime_summary["network_quality_throughput_source"] == (
        "ACTIVE_FLOW_CAPACITY"
    )
    assert runtime_summary["network_quality_latency_source"] == "ACTIVE_FLOW_LATENCY"
    assert runtime_tail["network_effective_throughput_source"] == "ACTIVE_FLOW_WINDOW"
    assert runtime_tail["network_active_flow_count"] == 1.0
    assert runtime_tail["network_active_flow_demand_mbps"] == 70.0
    assert runtime_tail["network_effective_throughput_mbps"] == 70.0


def test_metrics_collector_uses_route_loss_rate_for_network_loss_proxy() -> None:
    collector = MetricsCollector()
    collector.observe(
        _event(
            "route-loss",
            1.0,
            EventType.ROUTE_UPDATE,
            Route(
                route_id="route-loss",
                flow_id="flow-loss",
                path=("user-a", "sat-a", "user-b"),
                latency=0.02,
                capacity=100.0,
                available=True,
                loss_rate=0.12,
            ),
            "network",
        )
    )

    summary = collector.summary()

    assert summary["network_quality_route_loss_proxy_rate"] == pytest.approx(0.12)
    assert summary["network_quality_loss_proxy_rate"] == pytest.approx(0.12)
    assert summary["network_quality_effective_loss_proxy_rate"] == pytest.approx(0.12)
    assert summary["network_quality_effective_throughput_mbps"] == pytest.approx(88.0)
    assert summary["network_quality_loss_source"] == "ROUTE_LOSS_RATE"
    assert summary["network_quality_loss_source_label"] == "路由损耗率"
    assert summary["network_quality_loss_zero_reason"] == "POSITIVE_PROXY"
    assert summary["network_quality_loss_zero_reason_label"] == "当前代理指标为正值"


def test_metrics_collector_publishes_backend_kpi_time_series() -> None:
    collector = MetricsCollector()
    collector.observe(
        _event(
            "route-a",
            1.0,
            EventType.ROUTE_UPDATE,
            Route(
                route_id="route-a",
                flow_id="flow-a",
                path=("user-a", "sat-a", "user-b"),
                latency=0.02,
                capacity=100.0,
                available=True,
            ),
            "network",
        )
    )
    compute_records = collector.observe(
        _event(
            "compute-a",
            2.0,
            COMPUTE_NODE_UPDATE,
            ComputeNodeState(
                node_id="sat-a",
                sim_time=2.0,
                capacity=50.0,
                available_capacity=20.0,
                status="BUSY",
                used_cpu_gflops_fp64=4.0,
                used_gpu_tflops_fp32=1.5,
                used_gpu_tflops_fp16=3.0,
                used_npu_tops_int8=6.0,
                used_memory_gb=8.0,
                used_storage_gb=12.0,
                resource_usage_mode="RESOURCE_VECTOR_ESTIMATED",
            ),
            "compute",
        )
    )

    series = collector.kpi_time_series()

    assert series["version"] == "v1"
    assert series["sample_count"] == 2
    assert series["tail_sample_source"] == "CURRENT_METRICS_SUMMARY"
    assert series["tail_sample_source_label"] == "当前指标摘要同步"
    assert series["samples"][-1] == {
        "sim_time": 2.0,
        "network_effective_throughput_mbps": 100.0,
        "network_effective_throughput_source": "AVAILABLE_ROUTE_CAPACITY_AFTER_LOSS",
        "network_effective_throughput_source_label": "available route capacity estimate",
        "network_lifetime_effective_throughput_mbps": 100.0,
        "network_requested_route_demand_mbps": 0.0,
        "network_offered_route_capacity_mbps": 100.0,
        "network_available_route_demand_mbps": 0.0,
        "network_demand_pressure_proxy": 0.0,
        "network_throughput_pressure_proxy": 0.0,
        "network_effective_latency_s": 0.02,
        "network_route_latency_avg_s": 0.02,
        "network_effective_loss_proxy_rate": 0.0,
        "network_route_loss_proxy_rate": 0.0,
        "network_route_blocking_ratio": 0.0,
        "network_failed_flow_ratio": 0.0,
        "network_congestion_proxy": 0.0,
        "network_congestion_loss_proxy_rate": 0.0,
        "network_demand_loss_proxy_rate": 0.0,
        "network_pressure_loss_proxy_rate": 0.0,
        "network_effective_delay_variation_s": 0.0,
        "network_route_delay_variation_s": 0.0,
        "network_flow_delay_variation_s": 0.0,
        "network_pressure_delay_variation_s": 0.0,
        "network_effective_available_throughput_mbps": 100.0,
        "network_flow_delivered_capacity_mbps": 0.0,
        "network_time_adjusted_delivered_throughput_mbps": 0.0,
        "network_active_flow_count": 0.0,
        "network_active_available_flow_count": 0.0,
        "network_active_blocked_flow_count": 0.0,
        "network_active_flow_demand_mbps": 0.0,
        "network_active_flow_capacity_mbps": 0.0,
        "network_active_flow_latency_s": 0.0,
        "network_active_flow_latency_variation_s": 0.0,
        "network_active_flow_blocking_ratio": 0.0,
        "network_active_flow_pressure_proxy": 0.0,
        "network_time_adjusted_active_throughput_mbps": 0.0,
        "network_time_pressure_period_s": 120.0,
        "network_time_pressure_phase": pytest.approx(1 / 60),
        "network_time_pressure_load_proxy": 0.0,
        "network_time_pressure_triangular_wave": pytest.approx(1 / 30),
        "network_time_pressure_burst_window_factor": 0.0,
        "network_time_pressure_burst_amplitude": 0.0,
        "network_time_pressure_envelope": pytest.approx(0.4683333333333333),
        "network_time_pressure_factor": 0.0,
        "network_time_pressure_loss_proxy_rate": 0.0,
        "network_time_pressure_delay_variation_s": 0.0,
        "network_recent_window_s": 60.0,
        "network_recent_flow_count": 0.0,
        "network_recent_delivered_throughput_mbps": 0.0,
        "network_recent_latency_s": 0.0,
        "network_recent_loss_proxy_rate": 0.0,
        "network_recent_loss_zero_reason": "NO_RECENT_FLOW_SAMPLE",
        "network_recent_loss_zero_reason_label": (
            "最近窗口暂无完成流，零值仅表示窗口未形成样本"
        ),
        "network_recent_delay_variation_s": 0.0,
        "network_recent_delay_variation_zero_reason": "NO_RECENT_FLOW_SAMPLE",
        "network_recent_delay_variation_zero_reason_label": (
            "最近窗口暂无完成流，零值仅表示窗口未形成样本"
        ),
        "compute_resource_used_gflops_fp32": 30.0,
        "compute_resource_used_gflops_fp64": 4.0,
        "compute_resource_used_gpu_tflops_fp32": 1.5,
        "compute_resource_used_gpu_tflops_fp16": 3.0,
        "compute_resource_used_npu_tops_int8": 6.0,
        "compute_resource_used_memory_gb": 8.0,
        "compute_resource_used_storage_gb": 12.0,
    }
    assert _last_record(
        compute_records,
        "compute.resource.used_gflops_fp32",
    ).value == 30.0
    assert _last_record(
        compute_records,
        "compute.resource.used_gpu_tflops_fp32",
    ).value == 1.5
    assert _last_record(
        compute_records,
        "compute.resource.used_npu_tops_int8",
    ).value == 6.0


def test_metrics_collector_kpi_time_series_refreshes_current_tail_sample() -> None:
    collector = MetricsCollector(metric_sample_interval=100)
    collector.observe(
        _event(
            "compute-a",
            1.0,
            COMPUTE_NODE_UPDATE,
            ComputeNodeState(
                node_id="sat-a",
                sim_time=1.0,
                capacity=50.0,
                available_capacity=20.0,
                status="BUSY",
            ),
            "compute",
        )
    )
    collector.observe(
        _event(
            "route-loss",
            2.0,
            EventType.ROUTE_UPDATE,
            Route(
                route_id="route-loss",
                flow_id="flow-loss",
                path=("user-a", "sat-a", "user-b"),
                latency=0.02,
                capacity=100.0,
                available=True,
                loss_rate=0.12,
            ),
            "network",
        )
    )

    series = collector.kpi_time_series()

    assert series["sample_count"] == 2
    assert series["tail_sample_source"] == "CURRENT_METRICS_SUMMARY"
    assert series["tail_sample_source_label"] == "当前指标摘要同步"
    assert series["samples"][-1]["sim_time"] == 2.0
    assert series["samples"][-1]["network_effective_loss_proxy_rate"] == 0.12
    assert series["samples"][-1]["network_route_loss_proxy_rate"] == 0.12
    assert series["samples"][-1]["network_pressure_loss_proxy_rate"] == 0.0
    assert series["samples"][-1][
        "network_effective_delay_variation_s"
    ] == collector.summary()["network_quality_effective_delay_variation_proxy_s"]


def test_metrics_collector_kpi_time_series_accepts_runtime_sim_time_tail() -> None:
    collector = MetricsCollector(metric_sample_interval=100)
    collector.observe(
        _event(
            "route-loss",
            2.0,
            EventType.ROUTE_UPDATE,
            Route(
                route_id="route-loss",
                flow_id="flow-loss",
                path=("user-a", "sat-a", "user-b"),
                latency=0.02,
                capacity=100.0,
                available=True,
                loss_rate=0.12,
            ),
            "network",
        )
    )

    series = collector.kpi_time_series(sim_time=5.0)

    assert series["sample_count"] == 2
    assert series["samples"][-1]["sim_time"] == 5.0
    assert series["samples"][-1]["network_effective_loss_proxy_rate"] == 0.12


def test_metrics_collector_can_include_initial_kpi_baseline_on_request() -> None:
    collector = MetricsCollector(metric_sample_interval=100)
    collector.observe(
        _event(
            "route-loss",
            0.15,
            EventType.ROUTE_UPDATE,
            Route(
                route_id="route-loss",
                flow_id="flow-loss",
                path=("user-a", "sat-a", "user-b"),
                latency=0.02,
                capacity=100.0,
                available=True,
                loss_rate=0.12,
            ),
            "network",
        )
    )

    default_series = collector.kpi_time_series(sim_time=1.0)
    baseline_series = collector.kpi_time_series(
        sim_time=1.0,
        include_initial_baseline=True,
    )

    assert default_series["samples"][0]["sim_time"] == 0.15
    assert baseline_series["samples"][0]["sim_time"] == 0.0
    assert baseline_series["samples"][0]["network_requested_route_demand_mbps"] == 0.0
    assert baseline_series["samples"][-1]["sim_time"] == 1.0


def test_metrics_collector_uses_runtime_sim_time_for_time_varying_pressure() -> None:
    collector = MetricsCollector(metric_sample_interval=100)
    for route_id, flow_id, sim_time, latency in (
        ("route-a", "flow-a", 1.0, 0.04),
        ("route-b", "flow-b", 1.0, 0.04),
    ):
        collector.observe(
            _event(
                route_id,
                sim_time,
                EventType.ROUTE_UPDATE,
                Route(
                    route_id=route_id,
                    flow_id=flow_id,
                    path=("user-a", "sat-a", "user-b"),
                    latency=latency,
                    capacity=100.0,
                    available=True,
                ),
                "network",
            )
        )
    for flow_id, route_id, sim_time, latency in (
        ("flow-a", "route-a", 2.0, 0.04),
        ("flow-b", "route-b", 2.0, 0.04),
    ):
        collector.observe(
            _event(
                flow_id,
                sim_time,
                EventType.FLOW_COMPLETE,
                FlowState(
                    flow_id=flow_id,
                    route_id=route_id,
                    source_id="user-a",
                    target_id="user-b",
                    status="complete",
                    latency=latency,
                    capacity=90.0,
                ),
                "network",
            )
        )

    early_tail = collector.kpi_time_series(sim_time=2.0)["samples"][-1]
    peak_tail = collector.kpi_time_series(sim_time=60.0)["samples"][-1]

    assert early_tail["network_time_pressure_factor"] < peak_tail[
        "network_time_pressure_factor"
    ]
    assert early_tail["network_time_pressure_loss_proxy_rate"] == 0.0
    assert peak_tail["network_time_pressure_loss_proxy_rate"] > 0.0
    assert peak_tail["network_effective_loss_proxy_rate"] > early_tail[
        "network_effective_loss_proxy_rate"
    ]
    assert peak_tail["network_effective_delay_variation_s"] > early_tail[
        "network_effective_delay_variation_s"
    ]
    assert peak_tail["network_effective_throughput_mbps"] < early_tail[
        "network_effective_throughput_mbps"
    ]
    assert peak_tail["network_time_pressure_phase"] == pytest.approx(0.5)
    assert peak_tail["network_time_pressure_triangular_wave"] == pytest.approx(1.0)
    assert peak_tail["network_time_pressure_burst_window_factor"] == pytest.approx(1.0)
    assert peak_tail["network_time_pressure_envelope"] == pytest.approx(1.0)
    assert peak_tail["network_time_pressure_envelope"] > early_tail[
        "network_time_pressure_envelope"
    ]
    assert peak_tail["network_time_pressure_load_proxy"] == early_tail[
        "network_time_pressure_load_proxy"
    ]


def test_metrics_collector_uses_configured_time_pressure_profile() -> None:
    collector = MetricsCollector(
        metric_sample_interval=100,
        time_pressure_period_s=80.0,
        time_pressure_burst_center_phase=0.25,
        time_pressure_burst_width_phase=0.25,
        time_pressure_burst_amplitude=0.2,
    )
    for route_id, flow_id in (("route-a", "flow-a"), ("route-b", "flow-b")):
        collector.observe(
            _event(
                route_id,
                1.0,
                EventType.ROUTE_UPDATE,
                Route(
                    route_id=route_id,
                    flow_id=flow_id,
                    path=("user-a", "sat-a", "user-b"),
                    latency=0.04,
                    capacity=100.0,
                    available=True,
                ),
                "network",
            )
        )
        collector.observe(
            _event(
                flow_id,
                2.0,
                EventType.FLOW_COMPLETE,
                FlowState(
                    flow_id=flow_id,
                    route_id=route_id,
                    source_id="user-a",
                    target_id="user-b",
                    status="complete",
                    latency=0.04,
                    capacity=90.0,
                ),
                "network",
            )
        )

    series = collector.kpi_time_series(sim_time=20.0)
    baseline, tail = series["samples"]

    assert baseline["network_time_pressure_period_s"] == 80.0
    assert baseline["network_time_pressure_burst_amplitude"] == 0.2
    assert tail["network_time_pressure_period_s"] == 80.0
    assert tail["network_time_pressure_phase"] == pytest.approx(0.25)
    assert tail["network_time_pressure_triangular_wave"] == pytest.approx(0.5)
    assert tail["network_time_pressure_burst_window_factor"] == pytest.approx(1.0)
    assert tail["network_time_pressure_burst_amplitude"] == pytest.approx(0.2)
    assert tail["network_time_pressure_envelope"] == pytest.approx(0.925)
    assert tail["network_time_pressure_factor"] > 0.0


def test_metrics_summary_can_use_runtime_observation_time_for_network_kpis() -> None:
    collector = MetricsCollector(
        metric_sample_interval=100,
        time_pressure_period_s=80.0,
        time_pressure_burst_center_phase=0.25,
        time_pressure_burst_width_phase=0.25,
        time_pressure_burst_amplitude=0.2,
    )
    for route_id, flow_id in (("route-a", "flow-a"), ("route-b", "flow-b")):
        collector.observe(
            _event(
                route_id,
                1.0,
                EventType.ROUTE_UPDATE,
                Route(
                    route_id=route_id,
                    flow_id=flow_id,
                    path=("user-a", "sat-a", "user-b"),
                    latency=0.04,
                    capacity=100.0,
                    available=True,
                    demand_capacity=90.0,
                ),
                "network",
            )
        )
        collector.observe(
            _event(
                flow_id,
                2.0,
                EventType.FLOW_COMPLETE,
                FlowState(
                    flow_id=flow_id,
                    route_id=route_id,
                    source_id="user-a",
                    target_id="user-b",
                    status="complete",
                    latency=0.04,
                    capacity=90.0,
                ),
                "network",
            )
        )

    event_time_summary = collector.summary()
    target_time_summary = collector.summary(sim_time=20.0)

    assert event_time_summary["metrics_summary_time_source"] == "EVENT_TIME"
    assert event_time_summary["metrics_summary_observation_time_s"] == 2.0
    assert target_time_summary["metrics_summary_time_source"] == (
        "RUNTIME_ADVANCE_TARGET"
    )
    assert target_time_summary["metrics_summary_event_time_s"] == 2.0
    assert target_time_summary["metrics_summary_observation_time_s"] == 20.0
    assert target_time_summary["network_quality_time_pressure_phase"] == pytest.approx(
        0.25
    )
    assert target_time_summary["network_quality_time_pressure_factor"] > (
        event_time_summary["network_quality_time_pressure_factor"]
    )
    assert target_time_summary["network_quality_effective_throughput_mbps"] < (
        event_time_summary["network_quality_effective_throughput_mbps"]
    )


def test_metrics_collector_kpi_time_series_prepends_initial_baseline_for_single_sample() -> None:
    collector = MetricsCollector()
    collector.observe(
        _event(
            "route-loss",
            2.0,
            EventType.ROUTE_UPDATE,
            Route(
                route_id="route-loss",
                flow_id="flow-loss",
                path=("user-a", "sat-a", "user-b"),
                latency=0.02,
                capacity=100.0,
                available=True,
                loss_rate=0.12,
            ),
            "network",
        )
    )

    series = collector.kpi_time_series()

    assert series["sample_count"] == 2
    assert series["samples"][0]["sim_time"] == 0.0
    assert series["samples"][0]["network_effective_throughput_mbps"] == 0.0
    assert series["samples"][0]["network_effective_throughput_source"] == "BASELINE"
    assert series["samples"][0]["network_lifetime_effective_throughput_mbps"] == 0.0
    assert series["samples"][0]["network_effective_loss_proxy_rate"] == 0.0
    assert series["samples"][0]["network_recent_window_s"] == 60.0
    assert series["samples"][0]["network_time_pressure_period_s"] == 120.0
    assert series["samples"][0]["network_time_pressure_load_proxy"] == 0.0
    assert series["samples"][0]["network_time_pressure_triangular_wave"] == 0.0
    assert series["samples"][0]["network_time_pressure_burst_window_factor"] == 0.0
    assert series["samples"][0]["network_time_pressure_burst_amplitude"] == 0.0
    assert series["samples"][0]["network_time_pressure_envelope"] == 0.45
    assert series["samples"][0]["network_time_pressure_factor"] == 0.0
    assert series["samples"][1]["sim_time"] == 2.0
    assert series["samples"][1]["network_effective_throughput_mbps"] == pytest.approx(
        88.0
    )
    assert series["samples"][1]["network_effective_loss_proxy_rate"] == pytest.approx(
        0.12
    )


def test_metrics_collector_reports_recent_flow_kpi_window() -> None:
    collector = MetricsCollector(metric_sample_interval=100)
    collector.observe(
        _event(
            "route-a",
            1.0,
            EventType.ROUTE_UPDATE,
            Route(
                route_id="route-a",
                flow_id="flow-a",
                path=("user-a", "sat-a", "user-b"),
                latency=0.1,
                capacity=100.0,
                available=True,
            ),
            "network",
        )
    )
    for flow_id, sim_time, latency, capacity, status in (
        ("flow-a", 10.0, 0.1, 80.0, "complete"),
        ("flow-b", 40.0, 0.2, 60.0, "complete"),
        ("flow-c", 50.0, None, 0.0, "blocked"),
    ):
        collector.observe(
            _event(
                flow_id,
                sim_time,
                EventType.FLOW_COMPLETE,
                FlowState(
                    flow_id=flow_id,
                    route_id="route-a",
                    source_id="user-a",
                    target_id="user-b",
                    status=status,
                    route_path=("user-a", "sat-a", "user-b"),
                    latency=latency,
                    capacity=capacity,
                ),
                "network",
            )
        )

    recent = collector.kpi_time_series(sim_time=70.0)["samples"][-1]
    assert recent["network_recent_window_s"] == 60.0
    assert recent["network_recent_flow_count"] == 3.0
    assert recent["network_recent_delivered_throughput_mbps"] == 140.0
    assert recent["network_recent_latency_s"] == pytest.approx(0.15)
    assert recent["network_recent_loss_proxy_rate"] == pytest.approx(1 / 3)
    assert recent["network_recent_loss_zero_reason"] == "POSITIVE_PROXY"
    assert recent["network_recent_loss_zero_reason_label"] == "当前代理指标为正值"
    assert recent["network_recent_delay_variation_s"] == pytest.approx(0.05)
    assert recent["network_recent_delay_variation_zero_reason"] == "POSITIVE_PROXY"
    assert (
        recent["network_recent_delay_variation_zero_reason_label"]
        == "当前代理指标为正值"
    )
    assert recent["network_effective_throughput_source"] == "RECENT_FLOW_WINDOW"
    assert recent["network_effective_throughput_source_label"] == (
        "recent completed flow window"
    )
    assert recent["network_lifetime_effective_throughput_mbps"] == pytest.approx(
        recent["network_flow_delivered_capacity_mbps"]
        * (1.0 - recent["network_time_pressure_loss_proxy_rate"])
    )
    assert recent["network_effective_throughput_mbps"] == pytest.approx(
        recent["network_recent_delivered_throughput_mbps"]
        * (1.0 - recent["network_time_pressure_loss_proxy_rate"])
    )
    assert recent["network_flow_delivered_capacity_mbps"] == pytest.approx(140.0)
    assert recent["network_flow_delay_variation_s"] == pytest.approx(0.05)

    expired = collector.kpi_time_series(sim_time=111.0)["samples"][-1]
    assert expired["network_effective_throughput_mbps"] == 0.0
    assert expired["network_effective_throughput_source"] == "NO_RECENT_FLOW_IN_WINDOW"
    assert expired["network_effective_throughput_source_label"] == (
        "no completed flow in recent window"
    )
    assert expired["network_lifetime_effective_throughput_mbps"] > 0.0
    assert expired["network_recent_flow_count"] == 0.0
    assert expired["network_recent_delivered_throughput_mbps"] == 0.0
    assert expired["network_recent_latency_s"] == 0.0
    assert expired["network_recent_loss_zero_reason"] == "NO_RECENT_FLOW_SAMPLE"
    assert expired["network_recent_loss_zero_reason_label"] == (
        "最近窗口暂无完成流，零值仅表示窗口未形成样本"
    )
    assert (
        expired["network_recent_delay_variation_zero_reason"]
        == "NO_RECENT_FLOW_SAMPLE"
    )
    assert expired["network_recent_delay_variation_zero_reason_label"] == (
        "最近窗口暂无完成流，零值仅表示窗口未形成样本"
    )


def test_metrics_collector_publishes_satellite_kpi_slices() -> None:
    collector = MetricsCollector()
    for event in (
        _event(
            "link-a-b",
            1.0,
            EventType.LINK_UPDATE,
            LinkState(
                source_id="sat-a",
                target_id="sat-b",
                latency=0.02,
                capacity=120.0,
                availability=True,
                utilization=0.5,
            ),
            "network",
        ),
        _event(
            "link-user-a",
            1.0,
            EventType.ACCESS_START,
            LinkState(
                source_id="user-a",
                target_id="sat-a",
                latency=0.04,
                capacity=40.0,
                availability=True,
                utilization=0.75,
            ),
            "network",
        ),
        _event(
            "route-a",
            1.0,
            EventType.ROUTE_UPDATE,
            Route(
                route_id="route-a",
                flow_id="flow-a",
                path=("user-a", "sat-a", "sat-b"),
                latency=0.02,
                capacity=60.0,
                available=True,
                demand_capacity=30.0,
                loss_rate=0.04,
            ),
            "network",
        ),
        _event(
            "route-b",
            1.0,
            EventType.ROUTE_UPDATE,
            Route(
                route_id="route-b",
                flow_id="flow-b",
                path=("sat-a", "user-b"),
                latency=0.08,
                capacity=20.0,
                available=True,
                demand_capacity=15.0,
                loss_rate=0.08,
            ),
            "network",
        ),
        _event(
            "compute-a",
            1.0,
            COMPUTE_NODE_UPDATE,
            ComputeNodeState(
                node_id="sat-a",
                sim_time=1.0,
                capacity=100.0,
                available_capacity=25.0,
                status="BUSY",
                cpu_gflops_fp64=8.0,
                gpu_tflops_fp32=2.5,
                gpu_tflops_fp16=5.0,
                npu_tops_int8=12.0,
                memory_gb=32.0,
                storage_gb=512.0,
                used_cpu_gflops_fp32=80.0,
                used_cpu_gflops_fp64=2.0,
                used_gpu_tflops_fp32=1.5,
                used_gpu_tflops_fp16=3.0,
                used_npu_tops_int8=6.0,
                used_memory_gb=10.0,
                used_storage_gb=64.0,
            ),
            "compute",
        ),
        _event(
            "task-start",
            1.0,
            EventType.TASK_START,
            TaskState(
                task_id="task-a",
                node_id="sat-a",
                sim_time=1.0,
                progress=0.2,
                status="RUNNING",
            ),
            "compute",
        ),
        _event(
            "task-finish",
            2.0,
            EventType.TASK_FINISH,
            TaskState(
                task_id="task-b",
                node_id="sat-a",
                sim_time=2.0,
                progress=1.0,
                status="FINISHED",
            ),
            "compute",
        ),
    ):
        collector.observe(event)

    slices = collector.satellite_kpi_slices()

    assert slices["version"] == "v1"
    assert slices["mode"] == "TOP_ACTIVITY_LIMITED"
    assert slices["slice_limit"] == 64
    assert slices["satellite_count"] == 2
    assert slices["slice_count"] == 2
    sat_a = next(
        item for item in slices["slices"] if item["satellite_id"] == "sat-a"
    )
    assert sat_a == {
        "satellite_id": "sat-a",
        "active_link_count": 2,
        "active_access_link_count": 1,
        "active_space_link_count": 1,
        "route_count": 2,
        "available_route_count": 2,
        "route_capacity_mbps": 80.0,
        "route_demand_mbps": 45.0,
        "route_latency_avg_s": pytest.approx(0.05),
        "route_delay_variation_proxy_s": pytest.approx(0.03),
        "route_loss_proxy_rate": pytest.approx(0.06),
        "compute_capacity_gflops_fp32": 100.0,
        "compute_used_gflops_fp32": 80.0,
        "compute_capacity_gflops_fp64": 8.0,
        "compute_used_gflops_fp64": 2.0,
        "compute_capacity_gpu_tflops_fp32": 2.5,
        "compute_used_gpu_tflops_fp32": 1.5,
        "compute_capacity_gpu_tflops_fp16": 5.0,
        "compute_used_gpu_tflops_fp16": 3.0,
        "compute_capacity_npu_tops_int8": 12.0,
        "compute_used_npu_tops_int8": 6.0,
        "compute_capacity_memory_gb": 32.0,
        "compute_used_memory_gb": 10.0,
        "compute_capacity_storage_gb": 512.0,
        "compute_used_storage_gb": 64.0,
        "compute_load_ratio": 0.8,
        "running_task_count": 1,
        "finished_task_count": 1,
    }
    assert [
        item["satellite_id"] for item in collector.satellite_kpi_slices(limit=1)["slices"]
    ] == ["sat-a"]


def test_metrics_collector_publishes_bounded_satellite_kpi_history() -> None:
    collector = MetricsCollector(satellite_kpi_history_limit=2)
    for event in (
        _event(
            "compute-a-1",
            1.0,
            COMPUTE_NODE_UPDATE,
            ComputeNodeState(
                node_id="sat-a",
                sim_time=1.0,
                capacity=100.0,
                available_capacity=80.0,
                status="BUSY",
                cpu_gflops_fp64=8.0,
                gpu_tflops_fp32=2.5,
                gpu_tflops_fp16=5.0,
                npu_tops_int8=12.0,
                memory_gb=32.0,
                storage_gb=512.0,
                used_cpu_gflops_fp32=20.0,
                used_cpu_gflops_fp64=1.0,
                used_gpu_tflops_fp32=0.5,
                used_gpu_tflops_fp16=1.0,
                used_npu_tops_int8=2.0,
                used_memory_gb=4.0,
                used_storage_gb=16.0,
            ),
            "compute",
        ),
        _event(
            "compute-a-2",
            2.0,
            COMPUTE_NODE_UPDATE,
            ComputeNodeState(
                node_id="sat-a",
                sim_time=2.0,
                capacity=100.0,
                available_capacity=50.0,
                status="BUSY",
                used_cpu_gflops_fp32=50.0,
            ),
            "compute",
        ),
        _event(
            "compute-a-3",
            3.0,
            COMPUTE_NODE_UPDATE,
            ComputeNodeState(
                node_id="sat-a",
                sim_time=3.0,
                capacity=100.0,
                available_capacity=30.0,
                status="BUSY",
                used_cpu_gflops_fp32=70.0,
            ),
            "compute",
        ),
        _event(
            "compute-b-1",
            3.0,
            COMPUTE_NODE_UPDATE,
            ComputeNodeState(
                node_id="sat-b",
                sim_time=3.0,
                capacity=100.0,
                available_capacity=90.0,
                status="BUSY",
                used_cpu_gflops_fp32=10.0,
            ),
            "compute",
        ),
        _event(
            "compute-ground",
            3.0,
            COMPUTE_NODE_UPDATE,
            ComputeNodeState(
                node_id="ground-compute",
                sim_time=3.0,
                capacity=100.0,
                available_capacity=10.0,
                status="BUSY",
                used_cpu_gflops_fp32=90.0,
            ),
            "compute",
        ),
    ):
        collector.observe(event)

    history = collector.satellite_kpi_history(limit=1)

    assert history["version"] == "v1"
    assert history["mode"] == "RECENT_COMPUTE_LIMITED"
    assert history["slice_limit"] == 1
    assert history["sample_limit"] == 2
    assert history["satellite_count"] == 2
    assert history["series_count"] == 1
    series = history["series"][0]
    assert series["satellite_id"] == "sat-a"
    assert series["sample_count"] == 2
    assert [sample["sim_time"] for sample in series["samples"]] == [2.0, 3.0]
    assert series["samples"][-1] == {
        "sim_time": 3.0,
        "compute_load_ratio": 0.7,
        "compute_capacity_gflops_fp32": 100.0,
        "compute_used_gflops_fp32": 70.0,
        "compute_capacity_gflops_fp64": 0.0,
        "compute_used_gflops_fp64": 0.0,
        "compute_capacity_gpu_tflops_fp32": 0.0,
        "compute_used_gpu_tflops_fp32": 0.0,
        "compute_capacity_gpu_tflops_fp16": 0.0,
        "compute_used_gpu_tflops_fp16": 0.0,
        "compute_capacity_npu_tops_int8": 0.0,
        "compute_used_npu_tops_int8": 0.0,
        "compute_capacity_memory_gb": 0.0,
        "compute_used_memory_gb": 0.0,
        "compute_capacity_storage_gb": 0.0,
        "compute_used_storage_gb": 0.0,
    }


def test_metrics_collector_reports_compute_resource_pool_proxy() -> None:
    collector = MetricsCollector()
    for event in (
        _event(
            "compute-a",
            1.0,
            COMPUTE_NODE_UPDATE,
            ComputeNodeState(
                node_id="sat-a",
                sim_time=1.0,
                capacity=20.0,
                available_capacity=5.0,
                status="BUSY",
                cpu_gflops_fp64=4.0,
                gpu_tflops_fp32=2.0,
                gpu_tflops_fp16=4.0,
                npu_tops_int8=8.0,
                memory_gb=16.0,
                storage_gb=256.0,
            ),
            "compute",
        ),
        _event(
            "compute-b",
            1.0,
            COMPUTE_NODE_UPDATE,
            ComputeNodeState(
                node_id="sat-b",
                sim_time=1.0,
                capacity=10.0,
                available_capacity=10.0,
                status="IDLE",
                cpu_gflops_fp64=2.0,
                gpu_tflops_fp32=1.0,
                gpu_tflops_fp16=2.0,
                npu_tops_int8=4.0,
                memory_gb=8.0,
                storage_gb=128.0,
            ),
            "compute",
        ),
    ):
        collector.observe(event)

    summary = collector.summary()

    assert summary["compute_resource_node_count"] == 2
    assert summary["compute_resource_busy_nodes"] == 1
    assert summary["compute_resource_idle_nodes"] == 1
    assert summary["compute_resource_total_gflops_fp32"] == 30.0
    assert summary["compute_resource_available_gflops_fp32"] == 15.0
    assert summary["compute_resource_used_gflops_fp32"] == 15.0
    assert summary["compute_resource_total_gflops_fp64"] == 6.0
    assert summary["compute_resource_total_gpu_tflops_fp32"] == 3.0
    assert summary["compute_resource_total_gpu_tflops_fp16"] == 6.0
    assert summary["compute_resource_total_npu_tops_int8"] == 12.0
    assert summary["compute_resource_total_memory_gb"] == 24.0
    assert summary["compute_resource_total_storage_gb"] == 384.0
    assert summary["compute_resource_used_gpu_tflops_fp32"] == 0.0
    assert summary["compute_resource_vector_capacity_reported"] is True
    assert (
        summary["compute_resource_vector_utilization_mode"]
        == "SCALAR_FP32_AVAILABLE_ONLY"
    )
    assert summary["compute_resource_vector_dimension_count"] == 7
    assert summary["compute_resource_vector_active_dimension_count"] == 7
    assert summary["compute_resource_bottleneck_resource"] == "cpu_gflops_fp32"
    assert summary["compute_resource_bottleneck_label"] == "CPU FP32 GFLOPS"
    assert summary["compute_resource_bottleneck_utilization"] == pytest.approx(0.5)
    assert summary["compute_resource_bottleneck_used"] == 15.0
    assert summary["compute_resource_bottleneck_total"] == 30.0
    assert summary["compute_resource_bottleneck_available"] == 15.0
    assert summary["compute_resource_bottleneck_status"] == "NORMAL"
    assert summary["compute_resource_utilization"] == pytest.approx(0.5)
    assert summary["compute_resource_unit"] == "GFLOPS FP32"
    assert summary["compute_resource_proxy_note"] == (
        "Legacy scalar compute capacity maps to FP32 GFLOPS; "
        "resource-vector usage is deterministic estimator output when "
        "ComputeNodeState reports RESOURCE_VECTOR_ESTIMATED."
    )


def test_metrics_collector_reports_estimated_vector_resource_usage() -> None:
    collector = MetricsCollector()
    collector.observe(
        _event(
            "compute-vector",
            1.0,
            COMPUTE_NODE_UPDATE,
            ComputeNodeState(
                node_id="sat-a",
                sim_time=1.0,
                capacity=100.0,
                available_capacity=0.0,
                status="BUSY",
                gpu_tflops_fp32=2.0,
                memory_gb=16.0,
                storage_gb=2.0,
                resource_usage_mode="RESOURCE_VECTOR_ESTIMATED",
                available_cpu_gflops_fp32=100.0,
                used_cpu_gflops_fp32=0.0,
                available_gpu_tflops_fp32=0.0,
                used_gpu_tflops_fp32=2.0,
                available_memory_gb=12.0,
                used_memory_gb=4.0,
                available_storage_gb=1.5,
                used_storage_gb=0.5,
            ),
            "compute",
        )
    )

    summary = collector.summary()

    assert (
        summary["compute_resource_vector_utilization_mode"]
        == "RESOURCE_VECTOR_ESTIMATED"
    )
    assert summary["compute_resource_available_cpu_gflops_fp32"] == 100.0
    assert summary["compute_resource_used_cpu_gflops_fp32"] == 0.0
    assert summary["compute_resource_available_gpu_tflops_fp32"] == 0.0
    assert summary["compute_resource_used_gpu_tflops_fp32"] == 2.0
    assert summary["compute_resource_available_memory_gb"] == 12.0
    assert summary["compute_resource_used_memory_gb"] == 4.0
    assert summary["compute_resource_available_storage_gb"] == 1.5
    assert summary["compute_resource_used_storage_gb"] == 0.5
    assert summary["compute_resource_bottleneck_resource"] == "gpu_tflops_fp32"
    assert summary["compute_resource_bottleneck_label"] == "GPU FP32 TFLOPS"
    assert summary["compute_resource_bottleneck_utilization"] == pytest.approx(1.0)
    assert summary["compute_resource_bottleneck_used"] == 2.0
    assert summary["compute_resource_bottleneck_total"] == 2.0
    assert summary["compute_resource_bottleneck_available"] == 0.0
    assert summary["compute_resource_bottleneck_status"] == "SATURATED"


def test_metrics_collector_scales_satellite_positions_for_orbit_kpis() -> None:
    collector = MetricsCollector(satellite_position_scale_to_km=0.001)

    collector.observe(
        _event(
            "orbit-meters",
            0.0,
            EventType.ORBIT_UPDATE,
            SatelliteState(
                satellite_id="sat-meter",
                sim_time=0.0,
                position=(7_000_000.0, 0.0, 0.0),
                velocity=(0.0, 7_500.0, 0.0),
                status="online",
            ),
            "orbit",
        )
    )

    summary = collector.summary()

    assert summary["satellite_altitude_avg"] == pytest.approx(629.0)
    assert _last_record(collector.records(), "satellite.altitude_km").value == pytest.approx(
        629.0
    )


def test_metrics_collector_counts_deadline_missed_tasks() -> None:
    collector = MetricsCollector()

    collector.observe(
        _event(
            "task-finish-timeout",
            7.0,
            EventType.TASK_FINISH,
            TaskState(
                task_id="task-timeout",
                node_id="node-a",
                sim_time=7.0,
                progress=1.0,
                status="DEADLINE_MISSED",
            ),
            "compute",
        )
    )

    summary = collector.summary()
    records = collector.records()
    assert summary["finished_tasks"] == 1
    assert summary["deadline_missed_tasks"] == 1
    assert _last_record(records, "tasks.deadline_missed.count").value == 1.0


def test_service_latency_history_includes_sorted_component_timeline() -> None:
    collector = MetricsCollector()
    base_tags = (
        ("input_flow_id", "svc-input"),
        ("route_id", "route:svc-input"),
    )
    samples = (
        MetricRecord(
            metric_name="service.total_latency",
            sim_time=12.0,
            entity_id="svc-task",
            value="pending",
        ),
        MetricRecord(
            metric_name="service.total_latency",
            sim_time=12.0,
            entity_id="svc-task",
            value=7.4,
            tags=(
                ("input_flow_id", "svc-input"),
                ("output_flow_id", "svc-output"),
                ("route_id", "route:svc-output"),
            ),
        ),
        MetricRecord(
            metric_name="service.input_network_latency",
            sim_time=4.0,
            entity_id="svc-task",
            value=4.0,
            tags=base_tags,
        ),
        MetricRecord(
            metric_name="service.compute_queue_delay",
            sim_time=5.0,
            entity_id="svc-task",
            value=0.25,
            tags=base_tags,
        ),
        MetricRecord(
            metric_name="service.compute_execution_delay",
            sim_time=6.0,
            entity_id="svc-task",
            value=2.0,
            tags=base_tags,
        ),
        MetricRecord(
            metric_name="service.output_network_latency",
            sim_time=11.0,
            entity_id="svc-task",
            value=1.15,
            tags=(
                ("input_flow_id", "svc-input"),
                ("output_flow_id", "svc-output"),
                ("route_id", "route:svc-output"),
            ),
        ),
        MetricRecord(
            metric_name="service.untracked_delay",
            sim_time=7.0,
            entity_id="svc-task",
            value=99.0,
        ),
    )

    for index, sample in enumerate(samples):
        collector.observe(
            _event(
                f"metric-{index}",
                sample.sim_time,
                EventType.METRIC_SAMPLE,
                sample,
                "compute",
            )
        )

    history = collector.service_latency_history()
    assert history["item_count"] == 1
    assert history["items"][0] == {
        "task_id": "svc-task",
        "input_flow_id": "svc-input",
        "output_flow_id": "svc-output",
        "input_route_id": "route:svc-input",
        "output_route_id": "route:svc-output",
        "first_sample_sim_time": 4.0,
        "last_sample_sim_time": 12.0,
        "component_timeline": [
            {
                "component": "input_network",
                "metric_name": "service.input_network_latency",
                "sample_sim_time": 4.0,
                "duration_s": 4.0,
                "input_flow_id": "svc-input",
                "route_id": "route:svc-input",
            },
            {
                "component": "compute_queue",
                "metric_name": "service.compute_queue_delay",
                "sample_sim_time": 5.0,
                "duration_s": 0.25,
                "input_flow_id": "svc-input",
                "route_id": "route:svc-input",
            },
            {
                "component": "compute_execution",
                "metric_name": "service.compute_execution_delay",
                "sample_sim_time": 6.0,
                "duration_s": 2.0,
                "input_flow_id": "svc-input",
                "route_id": "route:svc-input",
            },
            {
                "component": "output_network",
                "metric_name": "service.output_network_latency",
                "sample_sim_time": 11.0,
                "duration_s": 1.15,
                "input_flow_id": "svc-input",
                "output_flow_id": "svc-output",
                "route_id": "route:svc-output",
            },
            {
                "component": "total",
                "metric_name": "service.total_latency",
                "sample_sim_time": 12.0,
                "duration_s": 7.4,
                "input_flow_id": "svc-input",
                "output_flow_id": "svc-output",
                "route_id": "route:svc-output",
            },
        ],
        "complete": True,
        "input_network_latency_s": 4.0,
        "compute_queue_delay_s": 0.25,
        "compute_execution_delay_s": 2.0,
        "output_network_latency_s": 1.15,
        "total_latency_s": 7.4,
    }


def test_service_latency_history_includes_placement_candidate_queue_label() -> None:
    collector = MetricsCollector()
    collector.observe(
        _event(
            "metric-placement-queue",
            8.0,
            EventType.METRIC_SAMPLE,
            MetricRecord(
                metric_name="service.total_latency",
                sim_time=8.0,
                entity_id="svc-task",
                value=4.0,
                tags=(
                    ("compute_node_id", "sat-a"),
                    ("service_placement_status", "QUEUED"),
                    ("service_placement_candidate_count", "2"),
                    ("service_placement_capable_candidate_count", "1"),
                    (
                        "service_placement_candidate_queue_label",
                        "sat-a:QUEUED/available=4s/q=1/finish=8s; "
                        "sat-b:PLACED/available=0s/q=0/finish=9s",
                    ),
                ),
            ),
            "compute",
        )
    )

    item = collector.service_latency_history()["items"][0]

    assert item["compute_node_id"] == "sat-a"
    assert item["service_placement_candidate_count"] == 2
    assert item["service_placement_capable_candidate_count"] == 1
    assert item["service_placement_candidate_queue_label"] == (
        "sat-a:QUEUED/available=4s/q=1/finish=8s; "
        "sat-b:PLACED/available=0s/q=0/finish=9s"
    )


def test_metrics_outputs_are_deterministic_and_have_expected_format(tmp_path) -> None:
    first = MetricsCollector()
    second = MetricsCollector()

    for event in _sample_events():
        first.observe(event)
        second.observe(event)

    assert first.records() == second.records()
    assert first.event_log() == second.event_log()
    assert first.metrics_csv() == second.metrics_csv()
    assert first.summary_json() == second.summary_json()
    assert first.events_jsonl() == second.events_jsonl()

    rows = list(csv.DictReader(io.StringIO(first.metrics_csv())))
    assert rows
    assert tuple(rows[0]) == ("sim_time", "metric_name", "entity_id", "value", "tags")
    assert rows[0] == {
        "sim_time": "0.0",
        "metric_name": "events.observed.count",
        "entity_id": "system",
        "value": "1.0",
        "tags": '{"event_type":"ORBIT_UPDATE","source":"orbit","target":"metrics"}',
    }
    assert json.loads(rows[0]["value"]) == 1.0
    assert json.loads(rows[0]["tags"]) == {
        "event_type": "ORBIT_UPDATE",
        "source": "orbit",
        "target": "metrics",
    }

    summary = json.loads(first.summary_json())
    assert summary == first.summary()
    assert first.summary_json().endswith("\n")

    replay_lines = first.events_jsonl().splitlines()
    first_replay_event = json.loads(replay_lines[0])
    assert first_replay_event == {
        "event_id": "orbit-1",
        "event_type": "ORBIT_UPDATE",
        "payload": {
            "position": [1.0, 2.0, 3.0],
            "satellite_id": "sat-a",
            "sim_time": 0.0,
            "status": "online",
            "velocity": [0.0, 0.1, 0.2],
        },
        "payload_type": "SatelliteState",
        "priority": 0,
        "sim_time": 0.0,
        "source": "orbit",
        "target": "metrics",
    }

    output_files = first.write_outputs(tmp_path)
    assert output_files["events"].read_text(encoding="utf-8") == first.events_jsonl()
    assert output_files["metrics"].read_text(encoding="utf-8") == first.metrics_csv()
    assert output_files["summary"].read_text(encoding="utf-8") == first.summary_json()


def test_metrics_on_event_emits_only_metric_sample_events() -> None:
    collector = MetricsCollector(emit_metric_events=True, metric_target="metrics-sink")
    sink = _ScheduledEventSink()
    observed = _sample_events()[1]

    collector.on_event(observed, sink)

    assert len(sink.events) == len(collector.records())
    assert {event.event_type for event in sink.events} == {EventType.METRIC_SAMPLE}
    assert {event.target for event in sink.events} == {"metrics-sink"}
    assert {event.source for event in sink.events} == {"metrics"}
    assert all(isinstance(event.payload, MetricRecord) for event in sink.events)
    assert not any(
        event.event_type
        in {
            EventType.ORBIT_UPDATE,
            EventType.ACCESS_START,
            EventType.ACCESS_END,
            EventType.LINK_UPDATE,
            EventType.ROUTE_UPDATE,
            EventType.FLOW_COMPLETE,
            EventType.TASK_START,
            EventType.TASK_FINISH,
        }
        for event in sink.events
    )


def _last_record(records: tuple[MetricRecord, ...], metric_name: str) -> MetricRecord:
    for record in reversed(records):
        if record.metric_name == metric_name:
            return record
    raise AssertionError(f"missing metric record: {metric_name}")
