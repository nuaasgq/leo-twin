from __future__ import annotations

from leo_twin.core import SimulationKernel, SimulationModule
from leo_twin.models.compute import (
    COMPUTE_NODE_UPDATE,
    ComputeNode,
    ComputeSchedulingPolicy,
    ComputeSchedulingRuntime,
    RouteAwareComputeEngine,
)
from leo_twin.schema import EventType, Route, SimEvent, TaskRequest


class MetricsSink(SimulationModule):
    def __init__(self) -> None:
        self.events: list[SimEvent] = []

    def name(self) -> str:
        return "metrics"

    def on_event(self, event: SimEvent, kernel: SimulationKernel) -> None:
        self.events.append(event)


class NetworkSink(SimulationModule):
    def __init__(self) -> None:
        self.events: list[SimEvent] = []

    def name(self) -> str:
        return "network"

    def on_event(self, event: SimEvent, kernel: SimulationKernel) -> None:
        self.events.append(event)


def _task(
    task_id: str = "flow-001",
    compute_demand: float = 20.0,
    data_size: float = 10.0,
    deadline: float | None = None,
    flow_id: str | None = None,
) -> TaskRequest:
    return TaskRequest(
        task_id=task_id,
        source_id="user-001",
        submit_time=0.0,
        compute_demand=compute_demand,
        data_size=data_size,
        deadline=deadline,
        flow_id=flow_id,
    )


def _route(
    available: bool = True,
    flow_id: str = "flow-001",
    latency: float = 2.0,
    capacity: float = 5.0,
) -> Route:
    return Route(
        route_id=f"route-{flow_id}",
        flow_id=flow_id,
        path=("user-001", "sat-001", "node-a"),
        latency=latency,
        capacity=capacity,
        available=available,
    )


def _event(
    event_id: str,
    event_type: str,
    payload: object,
    dispatch_time: float = 0.0,
) -> SimEvent:
    return SimEvent(
        event_id=event_id,
        sim_time=dispatch_time,
        priority=0,
        source="scenario",
        target="compute",
        event_type=event_type,
        payload=payload,
    )


def test_task_waits_until_matching_route_update_arrives() -> None:
    kernel = SimulationKernel()
    engine = RouteAwareComputeEngine(nodes=(ComputeNode("node-a", capacity=10.0),))
    sink = MetricsSink()
    kernel.register_module(engine)
    kernel.register_module(sink)
    kernel.schedule_event(_event("task", EventType.TASK_ARRIVAL.value, _task()))
    kernel.schedule_event(_event("route", EventType.ROUTE_UPDATE.value, _route(), 3.0))

    kernel.run()

    assert engine.pending_tasks() == ()
    decision = engine.scheduled_tasks()[0]
    assert decision.ready_time == 7.0
    assert decision.transfer_time == 4.0
    assert decision.compute_time == 2.0
    assert [event.event_type for event in sink.events] == [
        EventType.TASK_START.value,
        COMPUTE_NODE_UPDATE,
        EventType.TASK_FINISH.value,
        COMPUTE_NODE_UPDATE,
    ]


def test_unavailable_route_keeps_task_pending() -> None:
    kernel = SimulationKernel()
    engine = RouteAwareComputeEngine(nodes=(ComputeNode("node-a", capacity=10.0),))
    sink = MetricsSink()
    kernel.register_module(engine)
    kernel.register_module(sink)
    kernel.schedule_event(_event("task", EventType.TASK_ARRIVAL.value, _task()))
    kernel.schedule_event(_event("route", EventType.ROUTE_UPDATE.value, _route(False)))

    kernel.run()

    assert engine.pending_tasks() == ("flow-001",)
    assert engine.scheduled_tasks() == ()
    assert sink.events == []


def test_route_aware_compute_uses_route_endpoint_node_when_present() -> None:
    kernel = SimulationKernel()
    engine = RouteAwareComputeEngine(
        nodes=(
            ComputeNode("node-b", capacity=100.0),
            ComputeNode("node-a", capacity=10.0),
        )
    )
    sink = MetricsSink()
    kernel.register_module(engine)
    kernel.register_module(sink)
    kernel.schedule_event(_event("route", EventType.ROUTE_UPDATE.value, _route()))
    kernel.schedule_event(_event("task", EventType.TASK_ARRIVAL.value, _task()))

    kernel.run()

    decision = engine.scheduled_tasks()[0]
    assert decision.node_id == "node-a"
    assert decision.start_time == 4.0
    assert decision.finish_time == 6.0
    assert decision.placement_policy == "MIN_ESTIMATED_FINISH_TIME"
    assert decision.placement_status == "PLACED"
    assert decision.queue_delay == 0.0
    assert decision.bottleneck_resource == "cpu_gflops_fp32"
    assert decision.candidate_count == 1
    assert decision.capable_candidate_count == 1
    assert (
        decision.candidate_queue_label
        == "node-a:PLACED/available=0s/q=0/finish=6s"
    )


def test_route_aware_compute_falls_back_when_route_node_is_not_capable() -> None:
    kernel = SimulationKernel()
    engine = RouteAwareComputeEngine(
        nodes=(
            ComputeNode("node-b", capacity=100.0, gpu_tflops_fp32=10.0),
            ComputeNode("node-a", capacity=100.0),
        )
    )
    sink = MetricsSink()
    kernel.register_module(engine)
    kernel.register_module(sink)
    kernel.schedule_event(_event("route", EventType.ROUTE_UPDATE.value, _route()))
    kernel.schedule_event(
        _event(
            "task",
            EventType.TASK_ARRIVAL.value,
            TaskRequest(
                task_id="flow-001",
                source_id="user-001",
                submit_time=0.0,
                compute_demand=0.0,
                data_size=0.0,
                fp32_ops=10_000_000_000_000.0,
            ),
        )
    )

    kernel.run()

    decision = engine.scheduled_tasks()[0]
    assert decision.node_id == "node-b"
    assert decision.placement_status == "PLACED"
    assert decision.candidate_count == 2
    assert decision.capable_candidate_count == 1


def test_route_aware_compute_applies_scheduling_policy_to_ready_batch() -> None:
    kernel = SimulationKernel()
    engine = RouteAwareComputeEngine(
        nodes=(ComputeNode("node-a", capacity=10.0),),
        scheduling_runtime=ComputeSchedulingRuntime(
            ComputeSchedulingPolicy.SHORTEST_JOB_FIRST
        ),
    )
    sink = MetricsSink()
    kernel.register_module(engine)
    kernel.register_module(sink)
    kernel.schedule_event(
        _event(
            "task-large",
            EventType.TASK_ARRIVAL.value,
            _task("flow-large", compute_demand=30.0, data_size=0.0),
        )
    )
    kernel.schedule_event(
        _event(
            "task-small",
            EventType.TASK_ARRIVAL.value,
            _task("flow-small", compute_demand=5.0, data_size=0.0),
        )
    )
    kernel.schedule_event(
        _event(
            "route-large",
            EventType.ROUTE_UPDATE.value,
            _route(flow_id="flow-large", latency=0.0, capacity=10.0),
        )
    )
    kernel.schedule_event(
        _event(
            "route-small",
            EventType.ROUTE_UPDATE.value,
            _route(flow_id="flow-small", latency=0.0, capacity=10.0),
        )
    )

    kernel.run()

    decisions = {decision.task_id: decision for decision in engine.scheduled_tasks()}
    assert decisions["flow-small"].start_time == 0.0
    assert decisions["flow-small"].finish_time == 0.5
    assert decisions["flow-large"].start_time == 0.5
    assert decisions["flow-large"].finish_time == 3.5
    assert [
        event.payload.task_id
        for event in sink.events
        if event.event_type == EventType.TASK_START.value
    ] == ["flow-small", "flow-large"]


def test_route_aware_compute_marks_deadline_miss_without_rescheduling() -> None:
    kernel = SimulationKernel()
    engine = RouteAwareComputeEngine(nodes=(ComputeNode("node-a", capacity=10.0),))
    sink = MetricsSink()
    kernel.register_module(engine)
    kernel.register_module(sink)
    kernel.schedule_event(
        _event(
            "task",
            EventType.TASK_ARRIVAL.value,
            _task(deadline=5.0),
        )
    )
    kernel.schedule_event(_event("route", EventType.ROUTE_UPDATE.value, _route(), 3.0))

    kernel.run()

    decision = engine.scheduled_tasks()[0]
    finish_events = [
        event.payload
        for event in sink.events
        if event.event_type == EventType.TASK_FINISH.value
    ]
    assert decision.start_time == 7.0
    assert decision.finish_time == 9.0
    assert decision.status == "DEADLINE_MISSED"
    assert finish_events[0].status == "DEADLINE_MISSED"


def test_route_disruption_during_transfer_keeps_task_pending() -> None:
    kernel = SimulationKernel()
    engine = RouteAwareComputeEngine(nodes=(ComputeNode("node-a", capacity=10.0),))
    sink = MetricsSink()
    kernel.register_module(engine)
    kernel.register_module(sink)
    kernel.schedule_event(_event("route-up", EventType.ROUTE_UPDATE.value, _route()))
    kernel.schedule_event(_event("task", EventType.TASK_ARRIVAL.value, _task()))
    kernel.schedule_event(
        _event("route-down", EventType.ROUTE_UPDATE.value, _route(False), 2.0)
    )

    kernel.run()

    assert engine.pending_tasks() == ("flow-001",)
    assert engine.scheduled_tasks() == ()
    assert sink.events == []


def test_route_recovery_restarts_transfer_with_latest_route() -> None:
    kernel = SimulationKernel()
    engine = RouteAwareComputeEngine(nodes=(ComputeNode("node-a", capacity=10.0),))
    sink = MetricsSink()
    kernel.register_module(engine)
    kernel.register_module(sink)
    kernel.schedule_event(_event("route-up", EventType.ROUTE_UPDATE.value, _route()))
    kernel.schedule_event(_event("task", EventType.TASK_ARRIVAL.value, _task()))
    kernel.schedule_event(
        _event("route-down", EventType.ROUTE_UPDATE.value, _route(False), 2.0)
    )
    kernel.schedule_event(
        _event(
            "route-recovered",
            EventType.ROUTE_UPDATE.value,
            _route(latency=0.0, capacity=10.0),
            5.0,
        )
    )

    kernel.run()

    decision = engine.scheduled_tasks()[0]
    assert engine.pending_tasks() == ()
    assert decision.ready_time == 6.0
    assert decision.transfer_time == 1.0
    assert decision.compute_time == 2.0
    assert decision.start_time == 6.0
    assert decision.finish_time == 8.0
    assert [
        (event.event_type, event.sim_time)
        for event in sink.events
        if event.event_type in {EventType.TASK_START.value, EventType.TASK_FINISH.value}
    ] == [
        (EventType.TASK_START.value, 6.0),
        (EventType.TASK_FINISH.value, 8.0),
    ]


def test_route_aware_compute_tracks_transfer_by_task_id_when_input_flow_differs() -> None:
    kernel = SimulationKernel()
    engine = RouteAwareComputeEngine(nodes=(ComputeNode("node-a", capacity=10.0),))
    sink = MetricsSink()
    kernel.register_module(engine)
    kernel.register_module(sink)
    kernel.schedule_event(
        _event(
            "route-up",
            EventType.ROUTE_UPDATE.value,
            _route(flow_id="svc-input", latency=2.0, capacity=5.0),
        )
    )
    kernel.schedule_event(
        _event(
            "task",
            EventType.TASK_ARRIVAL.value,
            _task(task_id="svc-task", flow_id="svc-input"),
        )
    )
    kernel.schedule_event(
        _event(
            "route-refreshed",
            EventType.ROUTE_UPDATE.value,
            _route(flow_id="svc-input", latency=0.0, capacity=10.0),
            2.0,
        )
    )

    kernel.run()

    decision = engine.scheduled_tasks()[0]
    assert engine.pending_tasks() == ()
    assert decision.task_id == "svc-task"
    assert decision.route_id == "route-svc-input"
    assert decision.ready_time == 3.0
    assert decision.transfer_time == 1.0
    assert [
        (event.event_type, event.payload.task_id, event.payload.flow_id)
        for event in sink.events
        if event.event_type in {EventType.TASK_START.value, EventType.TASK_FINISH.value}
    ] == [
        (EventType.TASK_START.value, "svc-task", "svc-input"),
        (EventType.TASK_FINISH.value, "svc-task", "svc-input"),
    ]


def test_route_aware_compute_can_publish_node_updates_to_network() -> None:
    kernel = SimulationKernel()
    engine = RouteAwareComputeEngine(
        nodes=(
            ComputeNode(
                "node-a",
                capacity=10.0,
                cpu_gflops_fp64=2.0,
                gpu_tflops_fp32=1.5,
                gpu_tflops_fp16=3.0,
                npu_tops_int8=8.0,
                memory_gb=16.0,
                storage_gb=256.0,
            ),
        ),
        state_update_targets=("network",),
    )
    metrics = MetricsSink()
    network = NetworkSink()
    kernel.register_module(engine)
    kernel.register_module(metrics)
    kernel.register_module(network)
    kernel.schedule_event(_event("route", EventType.ROUTE_UPDATE.value, _route()))
    kernel.schedule_event(_event("task", EventType.TASK_ARRIVAL.value, _task()))

    kernel.run()

    assert [event.event_type for event in network.events] == [
        COMPUTE_NODE_UPDATE,
        COMPUTE_NODE_UPDATE,
    ]
    assert [event.target for event in network.events] == ["network", "network"]
    assert network.events[0].payload.cpu_gflops_fp64 == 2.0
    assert network.events[0].payload.gpu_tflops_fp32 == 1.5
    assert network.events[0].payload.gpu_tflops_fp16 == 3.0
    assert network.events[0].payload.npu_tops_int8 == 8.0
    assert network.events[0].payload.memory_gb == 16.0
    assert network.events[0].payload.storage_gb == 256.0
    assert [event.event_type for event in metrics.events] == [
        EventType.TASK_START.value,
        COMPUTE_NODE_UPDATE,
        EventType.TASK_FINISH.value,
        COMPUTE_NODE_UPDATE,
    ]


def test_route_aware_compute_is_deterministic() -> None:
    first = _run_scenario()
    second = _run_scenario()

    assert first == second


def _run_scenario() -> tuple[tuple, ...]:
    kernel = SimulationKernel()
    engine = RouteAwareComputeEngine(nodes=(ComputeNode("node-a", capacity=10.0),))
    sink = MetricsSink()
    kernel.register_module(engine)
    kernel.register_module(sink)
    kernel.schedule_event(_event("route", EventType.ROUTE_UPDATE.value, _route()))
    kernel.schedule_event(_event("task", EventType.TASK_ARRIVAL.value, _task()))
    kernel.run()
    return tuple(
        (
            event.event_id,
            event.sim_time,
            event.event_type,
            event.payload,
        )
        for event in sink.events
    )
