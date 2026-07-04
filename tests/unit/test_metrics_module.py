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


def test_metrics_collector_reports_effective_flow_level_network_quality() -> None:
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
        collector.observe(event)

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
