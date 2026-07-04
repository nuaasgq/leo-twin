from leo_twin.core import SimulationKernel, SimulationModule
from leo_twin.models.compute import COMPUTE_NODE_UPDATE, ComputeEngine, ComputeNode
from leo_twin.schema import (
    ComputeNodeState,
    EventType,
    FlowState,
    SimEvent,
    TaskRequest,
    TaskState,
)


class MetricsSink(SimulationModule):
    def __init__(self) -> None:
        self.events: list[SimEvent] = []

    def name(self) -> str:
        return "metrics"

    def on_event(self, event: SimEvent, kernel: SimulationKernel) -> None:
        self.events.append(event)


def _task(task_id: str, compute_demand: float = 10.0) -> TaskRequest:
    return TaskRequest(
        task_id=task_id,
        source_id="user-1",
        submit_time=0.0,
        compute_demand=compute_demand,
        data_size=1.0,
    )


def _event(
    event_id: int | str,
    event_type: str,
    payload: object,
    sim_time: float = 0.0,
) -> SimEvent:
    return SimEvent(
        event_id=event_id,
        sim_time=sim_time,
        priority=0,
        source="scenario",
        target="compute",
        event_type=event_type,
        payload=payload,
    )


def _run_task_scenario() -> tuple[ComputeEngine, MetricsSink, tuple[SimEvent, ...]]:
    kernel = SimulationKernel()
    engine = ComputeEngine(
        nodes=(
            ComputeNode(node_id="node-b", capacity=10.0),
            ComputeNode(node_id="node-a", capacity=10.0),
        )
    )
    sink = MetricsSink()
    kernel.register_module(engine)
    kernel.register_module(sink)

    kernel.schedule_event(_event(3, EventType.TASK_ARRIVAL.value, _task("task-3")))
    kernel.schedule_event(_event(1, EventType.TASK_ARRIVAL.value, _task("task-1")))
    kernel.schedule_event(_event(2, EventType.TASK_ARRIVAL.value, _task("task-2")))

    return engine, sink, kernel.run()


def test_task_lifecycle_events_and_node_state_updates_are_scheduled() -> None:
    kernel = SimulationKernel()
    engine = ComputeEngine(
        nodes=(ComputeNode(node_id="fast-node", capacity=20.0),)
    )
    sink = MetricsSink()
    kernel.register_module(engine)
    kernel.register_module(sink)
    kernel.schedule_event(
        _event(
            1,
            EventType.TASK_ARRIVAL.value,
            _task("task-1", compute_demand=40.0),
        )
    )

    kernel.run()

    assert [event.event_type for event in sink.events] == [
        EventType.TASK_START.value,
        COMPUTE_NODE_UPDATE,
        EventType.TASK_FINISH.value,
        COMPUTE_NODE_UPDATE,
    ]
    assert sink.events[0].payload == TaskState(
        task_id="task-1",
        node_id="fast-node",
        sim_time=0.0,
        progress=0.0,
        status="RUNNING",
    )
    assert sink.events[1].payload == ComputeNodeState(
        node_id="fast-node",
        sim_time=0.0,
        capacity=20.0,
        available_capacity=0.0,
        status="BUSY",
    )
    assert sink.events[2].payload == TaskState(
        task_id="task-1",
        node_id="fast-node",
        sim_time=2.0,
        progress=1.0,
        status="FINISHED",
    )
    assert sink.events[3].payload == ComputeNodeState(
        node_id="fast-node",
        sim_time=2.0,
        capacity=20.0,
        available_capacity=20.0,
        status="IDLE",
    )


def test_compute_node_updates_publish_resource_vectors() -> None:
    kernel = SimulationKernel()
    engine = ComputeEngine(
        nodes=(
            ComputeNode(
                node_id="vector-node",
                capacity=40.0,
                cpu_gflops_fp64=8.0,
                gpu_tflops_fp32=2.5,
                gpu_tflops_fp16=5.0,
                npu_tops_int8=12.0,
                memory_gb=32.0,
                storage_gb=512.0,
            ),
        )
    )
    sink = MetricsSink()
    kernel.register_module(engine)
    kernel.register_module(sink)
    kernel.schedule_event(
        _event(
            1,
            EventType.TASK_ARRIVAL.value,
            _task("task-vector", compute_demand=40.0),
        )
    )

    kernel.run()

    busy_state = next(
        event.payload
        for event in sink.events
        if event.event_type == COMPUTE_NODE_UPDATE
    )
    assert busy_state == ComputeNodeState(
        node_id="vector-node",
        sim_time=0.0,
        capacity=40.0,
        available_capacity=0.0,
        status="BUSY",
        cpu_gflops_fp64=8.0,
        gpu_tflops_fp32=2.5,
        gpu_tflops_fp16=5.0,
        npu_tops_int8=12.0,
        memory_gb=32.0,
        storage_gb=512.0,
    )


def test_dict_task_payload_can_drive_explicit_gpu_service_time() -> None:
    kernel = SimulationKernel()
    engine = ComputeEngine(
        nodes=(
            ComputeNode(
                node_id="gpu-node",
                capacity=100.0,
                gpu_tflops_fp32=2.0,
                memory_gb=16.0,
                storage_gb=2.0,
            ),
        )
    )
    sink = MetricsSink()
    kernel.register_module(engine)
    kernel.register_module(sink)
    kernel.schedule_event(
        _event(
            1,
            EventType.TASK_ARRIVAL.value,
            {
                "task_id": "gpu-task",
                "source_id": "user-1",
                "submit_time": 0.0,
                "compute_demand": 1.0,
                "data_size": 1.0,
                "fp32_ops": 10_000_000_000_000.0,
                "memory_gb": 4.0,
                "input_data_mb": 256.0,
                "output_data_mb": 128.0,
            },
        )
    )

    kernel.run()

    assert engine.scheduled_tasks() == (("gpu-task", "gpu-node", 0.0, 5.0),)


def test_scheduler_uses_deterministic_earliest_finish_ordering() -> None:
    engine, sink, _ = _run_task_scenario()

    starts = [
        event.payload
        for event in sink.events
        if event.event_type == EventType.TASK_START.value
    ]
    finishes = [
        event.payload
        for event in sink.events
        if event.event_type == EventType.TASK_FINISH.value
    ]

    assert [(item.task_id, item.node_id, item.sim_time) for item in starts] == [
        ("task-1", "node-a", 0.0),
        ("task-2", "node-b", 0.0),
        ("task-3", "node-a", 1.0),
    ]
    assert [(item.task_id, item.node_id, item.sim_time) for item in finishes] == [
        ("task-1", "node-a", 1.0),
        ("task-2", "node-b", 1.0),
        ("task-3", "node-a", 2.0),
    ]
    assert engine.scheduled_tasks() == (
        ("task-1", "node-a", 0.0, 1.0),
        ("task-2", "node-b", 0.0, 1.0),
        ("task-3", "node-a", 1.0, 2.0),
    )


def test_same_inputs_produce_identical_compute_outputs() -> None:
    first_engine, first_sink, first_processed = _run_task_scenario()
    second_engine, second_sink, second_processed = _run_task_scenario()

    assert first_engine.scheduled_tasks() == second_engine.scheduled_tasks()
    assert _event_summary(first_processed) == _event_summary(second_processed)
    assert _event_summary(first_sink.events) == _event_summary(second_sink.events)


def test_flow_complete_is_consumed_without_scheduling_task_lifecycle() -> None:
    kernel = SimulationKernel()
    engine = ComputeEngine(nodes=(ComputeNode(node_id="node-a", capacity=10.0),))
    sink = MetricsSink()
    flow = FlowState(
        flow_id="flow-1",
        route_id="route-1",
        source_id="user-1",
        target_id="node-a",
        status="COMPLETE",
    )
    kernel.register_module(engine)
    kernel.register_module(sink)
    kernel.schedule_event(_event(1, EventType.FLOW_COMPLETE.value, flow))

    kernel.run()

    assert engine.completed_flows() == (flow,)
    assert sink.events == []


def _event_summary(events: tuple[SimEvent, ...] | list[SimEvent]) -> tuple[tuple, ...]:
    return tuple(
        (
            event.event_id,
            event.sim_time,
            event.priority,
            event.source,
            event.target,
            event.event_type,
            event.payload,
        )
        for event in events
    )
