from __future__ import annotations

from leo_twin.core import SimulationKernel, SimulationModule
from leo_twin.models.compute import (
    COMPUTE_NODE_UPDATE,
    ComputeNode,
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


def _task(task_id: str = "flow-001") -> TaskRequest:
    return TaskRequest(
        task_id=task_id,
        source_id="user-001",
        submit_time=0.0,
        compute_demand=20.0,
        data_size=10.0,
    )


def _route(available: bool = True) -> Route:
    return Route(
        route_id="route-flow-001",
        flow_id="flow-001",
        path=("user-001", "sat-001", "node-a"),
        latency=2.0,
        capacity=5.0,
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
    assert engine.scheduled_tasks()[0].ready_time == 7.0
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
