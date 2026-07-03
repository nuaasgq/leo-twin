import random
from math import nan

import pytest

from leo_twin.core import EventQueue, SimulationKernel, SimulationModule
from leo_twin.schema import SimEvent


class _MockModule(SimulationModule):
    def __init__(
        self,
        module_name: str,
        next_target: str,
        execution_order: list[tuple[int | str, str]],
    ) -> None:
        self._module_name = module_name
        self._next_target = next_target
        self._execution_order = execution_order
        self.received_event_ids: list[int | str] = []

    def name(self) -> str:
        return self._module_name

    def on_event(self, event: SimEvent, kernel: SimulationKernel) -> None:
        self.received_event_ids.append(event.event_id)
        self._execution_order.append((event.event_id, self.name()))

        if not isinstance(event.payload, dict):
            return

        remaining = event.payload.get("remaining", 0)
        if remaining <= 0:
            return

        kernel.schedule_event(
            SimEvent(
                event_id=f"{event.event_id}.{remaining}",
                sim_time=event.sim_time + 1.0,
                priority=event.priority,
                source=self.name(),
                target=self._next_target,
                event_type="MOCK_PROPAGATE",
                payload={"remaining": remaining - 1},
            )
        )


class MockOrbitModule(_MockModule):
    def __init__(self, execution_order: list[tuple[int | str, str]]) -> None:
        super().__init__("mock-orbit", "mock-network", execution_order)


class MockNetworkModule(_MockModule):
    def __init__(self, execution_order: list[tuple[int | str, str]]) -> None:
        super().__init__("mock-network", "mock-compute", execution_order)


class MockComputeModule(_MockModule):
    def __init__(self, execution_order: list[tuple[int | str, str]]) -> None:
        super().__init__("mock-compute", "mock-orbit", execution_order)


def _register_mock_modules(
    kernel: SimulationKernel,
    execution_order: list[tuple[int | str, str]],
) -> tuple[MockOrbitModule, MockNetworkModule, MockComputeModule]:
    modules = (
        MockOrbitModule(execution_order),
        MockNetworkModule(execution_order),
        MockComputeModule(execution_order),
    )
    for module in modules:
        kernel.register_module(module)
    return modules


def _event(
    event_id: int | str,
    sim_time: float,
    priority: int,
    target: str = "mock-orbit",
    payload: object | None = None,
) -> SimEvent:
    return SimEvent(
        event_id=event_id,
        sim_time=sim_time,
        priority=priority,
        source="test",
        target=target,
        event_type="MOCK_EVENT",
        payload={} if payload is None else payload,
    )


def test_event_ordering() -> None:
    queue = EventQueue()
    events = [
        _event("later", 2.0, 100),
        _event("priority-low", 1.0, 1),
        _event(2, 1.0, 2),
        _event(1, 1.0, 2),
        _event("id-b", 1.0, 2),
        _event("id-a", 1.0, 2),
    ]

    for event in events:
        queue.push(event)

    assert queue.peek().event_id == 1

    ordered_ids = [queue.pop().event_id for _ in events]

    assert ordered_ids == [1, 2, "id-a", "id-b", "priority-low", "later"]
    assert queue.is_empty()

    with pytest.raises(ValueError, match="duplicate event_id"):
        duplicate_queue = EventQueue()
        duplicate_queue.push(_event("duplicate", 0.0, 0))
        duplicate_queue.push(_event("duplicate", 1.0, 0))

    with pytest.raises(ValueError, match="sim_time must be finite"):
        _event("nan-time", nan, 0)

    with pytest.raises(TypeError, match="event_id must be an int or str"):
        _event(True, 0.0, 0)


def test_same_seed_produces_identical_execution_order() -> None:
    def run_scenario(
        seed: int,
    ) -> tuple[tuple[int | str, float, int, str, str], ...]:
        rng = random.Random(seed)
        kernel = SimulationKernel()
        execution_order: list[tuple[int | str, str]] = []
        _register_mock_modules(kernel, execution_order)
        targets = ("mock-orbit", "mock-network", "mock-compute")

        for event_id in range(12):
            kernel.schedule_event(
                _event(
                    event_id=event_id,
                    sim_time=float(rng.randint(0, 4)),
                    priority=rng.randint(0, 3),
                    target=rng.choice(targets),
                )
            )

        processed_events = kernel.run()
        return tuple(
            (
                event.event_id,
                event.sim_time,
                event.priority,
                event.target,
                event.event_type,
            )
            for event in processed_events
        )

    assert run_scenario(2026) == run_scenario(2026)


def test_multiple_modules_receive_targeted_events() -> None:
    kernel = SimulationKernel()
    execution_order: list[tuple[int | str, str]] = []
    orbit, network, compute = _register_mock_modules(
        kernel,
        execution_order,
    )

    kernel.schedule_event(_event(1, 0.0, 0, target=orbit.name()))
    kernel.schedule_event(_event(2, 0.0, 0, target=network.name()))
    kernel.schedule_event(_event(3, 0.0, 0, target=compute.name()))
    kernel.run()

    assert orbit.received_event_ids == [1]
    assert network.received_event_ids == [2]
    assert compute.received_event_ids == [3]
    assert execution_order == [
        (1, "mock-orbit"),
        (2, "mock-network"),
        (3, "mock-compute"),
    ]

    with pytest.raises(ValueError, match="module already registered"):
        kernel.register_module(MockOrbitModule(execution_order))

    unknown_target_kernel = SimulationKernel()
    with pytest.raises(KeyError, match="no module registered"):
        unknown_target_kernel.schedule_event(_event(99, 0.0, 0))
        unknown_target_kernel.run()
    assert unknown_target_kernel.get_current_time() == 0.0


def test_kernel_runs_until_time_and_then_completes() -> None:
    kernel = SimulationKernel()
    execution_order: list[tuple[int | str, str]] = []
    _register_mock_modules(kernel, execution_order)
    kernel.schedule_event(
        _event(
            event_id="root",
            sim_time=0.0,
            priority=0,
            target="mock-orbit",
            payload={"remaining": 11},
        )
    )

    first_run = kernel.run(until_time=5.0)

    assert len(first_run) == 6
    assert kernel.get_current_time() == 5.0

    second_run = kernel.run()

    assert len(first_run + second_run) == 12
    assert kernel.get_current_time() == 11.0
    assert [module_name for _, module_name in execution_order] == [
        "mock-orbit",
        "mock-network",
        "mock-compute",
    ] * 4

    stopped_kernel = SimulationKernel()
    stopped_order: list[tuple[int | str, str]] = []
    _register_mock_modules(stopped_kernel, stopped_order)
    stopped_kernel.schedule_event(_event(1, 0.0, 0))
    stopped_kernel.stop()

    assert stopped_kernel.run() == ()
    assert stopped_kernel.get_current_time() == 0.0

    past_time_kernel = SimulationKernel()
    past_time_order: list[tuple[int | str, str]] = []
    _register_mock_modules(past_time_kernel, past_time_order)
    past_time_kernel.schedule_event(_event("first", 2.0, 0))
    past_time_kernel.run()

    with pytest.raises(ValueError, match="before the current simulation time"):
        past_time_kernel.schedule_event(_event("past", 1.0, 0))
