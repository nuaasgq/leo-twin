from __future__ import annotations

from leo_twin.core import SimulationKernel, SimulationModule
from leo_twin.models.compute import ComputeNode, RouteAwareComputeEngine
from leo_twin.models.traffic import (
    TrafficClass,
    TrafficDemandProfile,
    TrafficDestinationType,
    generate_traffic_demand,
)
from leo_twin.schema import EventType, FlowRequest, Route, SimEvent
from leo_twin.services.metrics import MetricsCollector
from leo_twin.services.runtime_observability import (
    build_runtime_service_lifecycle_stage_summary_v1,
    build_runtime_service_lifecycle_trace_v2,
)


class DeterministicServiceNetwork(SimulationModule):
    """Flow-level network stub for communication-compute lifecycle tests."""

    def name(self) -> str:
        return "network"

    def on_event(self, event: SimEvent, kernel: SimulationKernel) -> None:
        if event.event_type != EventType.FLOW_ARRIVAL.value:
            return
        flow = event.payload
        if not isinstance(flow, FlowRequest):
            raise TypeError("network test stub expects FlowRequest")
        is_output = flow.flow_id.endswith("-output")
        route = Route(
            route_id=f"route:{flow.flow_id}",
            flow_id=flow.flow_id,
            path=(flow.source_id, "sat-relay", flow.target_id),
            latency=1.0 if is_output else 2.0,
            capacity=10.0 if is_output else 5.0,
            available=True,
        )
        for target in ("compute", "metrics"):
            kernel.schedule_event(
                SimEvent(
                    event_id=f"network:route:{flow.flow_id}:{target}",
                    sim_time=event.sim_time,
                    priority=0,
                    source="network",
                    target=target,
                    event_type=EventType.ROUTE_UPDATE.value,
                    payload=route,
                )
            )


def test_compute_service_lifecycle_emits_component_metrics() -> None:
    batch = generate_traffic_demand(
        (
            TrafficDemandProfile(
                traffic_class=TrafficClass.COMPUTE_SERVICE,
                source_ids=("user-001",),
                destination_ids=("node-a",),
                output_destination_ids=("user-001",),
                request_count=1,
                arrival_interval=10.0,
                input_data_size=10.0,
                output_data_size=4.0,
                priority=3,
                destination_type=TrafficDestinationType.COMPUTE_NODE,
                compute_demand=20.0,
                id_prefix="svc",
            ),
        )
    )
    kernel = SimulationKernel()
    network = DeterministicServiceNetwork()
    compute = RouteAwareComputeEngine(
        nodes=(ComputeNode("node-a", capacity=10.0),),
        output_flow_metadata=batch.output_flow_metadata,
    )
    metrics = MetricsCollector(metric_sample_interval=1)
    kernel.register_module(network)
    kernel.register_module(compute)
    kernel.register_module(metrics)
    for event in batch.flow_arrival_events():
        kernel.schedule_event(event)
    for event in batch.task_arrival_events():
        kernel.schedule_event(event)

    kernel.run()

    decisions = compute.scheduled_tasks()
    assert len(decisions) == 1
    assert decisions[0].ready_time == 4.0
    assert decisions[0].start_time == 4.0
    assert decisions[0].finish_time == 6.0
    assert decisions[0].placement_policy == "MIN_ESTIMATED_FINISH_TIME"
    assert decisions[0].placement_status == "PLACED"
    assert decisions[0].bottleneck_resource == "cpu_gflops_fp32"
    assert decisions[0].candidate_count == 1
    assert decisions[0].capable_candidate_count == 1
    assert decisions[0].candidate_queue_label == (
        "node-a:PLACED/available=0s/q=0/finish=6s"
    )

    records = {
        record.metric_name: record.value
        for record in metrics.records()
        if str(record.metric_name).startswith("service.")
    }
    assert records == {
        "service.input_network_latency": 4.0,
        "service.compute_queue_delay": 0.0,
        "service.compute_execution_delay": 2.0,
        "service.output_network_latency": 1.4,
        "service.total_latency": 7.4,
    }
    summary = metrics.summary()
    assert summary["service_latency_summary_source"] == "METRIC_SAMPLE"
    assert (
        summary["service_latency_model"]
        == "COMMUNICATION_COMPUTE_COMPONENT_PROXY"
    )
    assert summary["service_latency_task_count"] == 1
    assert summary["service_latency_complete_count"] == 1
    assert summary["service_latency_input_network_avg_s"] == 4.0
    assert summary["service_latency_compute_queue_avg_s"] == 0.0
    assert summary["service_latency_compute_execution_avg_s"] == 2.0
    assert summary["service_latency_output_network_avg_s"] == 1.4
    assert summary["service_latency_total_avg_s"] == 7.4
    history = metrics.service_latency_history()
    trace = build_runtime_service_lifecycle_trace_v2(history)
    assert trace["service_count"] == 1
    assert trace["complete_trace_count"] == 1
    assert trace["items"][0]["service_id"] == "svc-00-compute_service-00000"
    assert tuple(stage["component"] for stage in trace["items"][0]["stages"]) == (
        "input_network",
        "compute_queue",
        "compute_execution",
        "output_network",
    )
    assert trace["items"][0]["terminal_state"] == "COMPLETE"
    assert trace["items"][0]["total_latency_s"] == 7.4
    stage_summary = build_runtime_service_lifecycle_stage_summary_v1(history)
    assert stage_summary["service_count"] == 1
    assert stage_summary["complete_service_count"] == 1
    assert stage_summary["observed_stage_count"] == 4
    assert stage_summary["pending_stage_count"] == 0
    assert stage_summary["dominant_stage_kind"] == "INPUT_NETWORK"
    assert stage_summary["stage_counts"][0]["total_duration_s"] == 4.0
    assert stage_summary["stage_counts"][2]["total_duration_s"] == 2.0
    assert stage_summary["terminal_state_counts"] == (
        {"terminal_state": "COMPLETE", "trace_count": 1},
    )
    assert history == {
        "version": "v1",
        "mode": "RECENT_SERVICE_LIMITED",
        "service_count": 1,
        "service_limit": 32,
        "item_count": 1,
        "items": [
                {
                    "task_id": "svc-00-compute_service-00000-task",
                    "input_flow_id": "svc-00-compute_service-00000-input",
                    "output_flow_id": "svc-00-compute_service-00000-output",
                    "input_route_id": "route:svc-00-compute_service-00000-input",
                    "output_route_id": "route:svc-00-compute_service-00000-output",
                    "compute_node_id": "node-a",
                    "service_placement_status": "PLACED",
                    "service_placement_policy": "MIN_ESTIMATED_FINISH_TIME",
                    "service_placement_bottleneck_resource": "cpu_gflops_fp32",
                    "service_placement_candidate_count": 1,
                    "service_placement_capable_candidate_count": 1,
                    "service_placement_candidate_queue_label": (
                        "node-a:PLACED/available=0s/q=0/finish=6s"
                    ),
                    "first_sample_sim_time": 6.0,
                "last_sample_sim_time": 6.0,
                "component_timeline": [
                    {
                        "component": "input_network",
                        "metric_name": "service.input_network_latency",
                        "sample_sim_time": 6.0,
                        "duration_s": 4.0,
                        "input_flow_id": "svc-00-compute_service-00000-input",
                        "route_id": "route:svc-00-compute_service-00000-input",
                    },
                    {
                        "component": "compute_queue",
                        "metric_name": "service.compute_queue_delay",
                        "sample_sim_time": 6.0,
                        "duration_s": 0.0,
                        "input_flow_id": "svc-00-compute_service-00000-input",
                        "route_id": "route:svc-00-compute_service-00000-input",
                    },
                    {
                        "component": "compute_execution",
                        "metric_name": "service.compute_execution_delay",
                        "sample_sim_time": 6.0,
                        "duration_s": 2.0,
                        "input_flow_id": "svc-00-compute_service-00000-input",
                        "route_id": "route:svc-00-compute_service-00000-input",
                    },
                    {
                        "component": "output_network",
                        "metric_name": "service.output_network_latency",
                        "sample_sim_time": 6.0,
                        "duration_s": 1.4,
                        "input_flow_id": "svc-00-compute_service-00000-input",
                        "output_flow_id": "svc-00-compute_service-00000-output",
                        "route_id": "route:svc-00-compute_service-00000-output",
                    },
                    {
                        "component": "total",
                        "metric_name": "service.total_latency",
                        "sample_sim_time": 6.0,
                        "duration_s": 7.4,
                        "input_flow_id": "svc-00-compute_service-00000-input",
                        "output_flow_id": "svc-00-compute_service-00000-output",
                        "route_id": "route:svc-00-compute_service-00000-output",
                    },
                ],
                "complete": True,
                "input_network_latency_s": 4.0,
                "compute_queue_delay_s": 0.0,
                "compute_execution_delay_s": 2.0,
                "output_network_latency_s": 1.4,
                "total_latency_s": 7.4,
            }
        ],
    }
