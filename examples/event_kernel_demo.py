"""Minimal deterministic demonstration of the event kernel."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from leo_twin.core import SimulationKernel, SimulationModule
from leo_twin.schema import SimEvent


class _MockModule(SimulationModule):
    def __init__(self, module_name: str, next_target: str) -> None:
        self._module_name = module_name
        self._next_target = next_target

    def name(self) -> str:
        return self._module_name

    def on_event(self, event: SimEvent, kernel: SimulationKernel) -> None:
        remaining = event.payload["remaining"]
        if remaining <= 0:
            return

        kernel.schedule_event(
            SimEvent(
                event_id=int(event.event_id) + 1,
                sim_time=event.sim_time + 1.0,
                priority=event.priority,
                source=self.name(),
                target=self._next_target,
                event_type="MOCK_PROPAGATE",
                payload={"remaining": remaining - 1},
            )
        )


class MockOrbitModule(_MockModule):
    def __init__(self) -> None:
        super().__init__("mock-orbit", "mock-network")


class MockNetworkModule(_MockModule):
    def __init__(self) -> None:
        super().__init__("mock-network", "mock-compute")


class MockComputeModule(_MockModule):
    def __init__(self) -> None:
        super().__init__("mock-compute", "mock-orbit")


def main() -> None:
    kernel = SimulationKernel()
    for module in (
        MockOrbitModule(),
        MockNetworkModule(),
        MockComputeModule(),
    ):
        kernel.register_module(module)

    kernel.schedule_event(
        SimEvent(
            event_id=0,
            sim_time=0.0,
            priority=0,
            source="demo",
            target="mock-orbit",
            event_type="MOCK_START",
            payload={"remaining": 14},
        )
    )

    processed_events = kernel.run()

    print("Event execution order:")
    for event in processed_events:
        print(
            f"{event.event_id}: time={event.sim_time:.1f}, "
            f"target={event.target}, type={event.event_type}"
        )
    print(f"Final simulation time: {kernel.get_current_time():.1f}")
    print(f"Processed events: {len(processed_events)}")


if __name__ == "__main__":
    main()
