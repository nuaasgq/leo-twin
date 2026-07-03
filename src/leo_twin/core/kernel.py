"""Deterministic discrete-event simulation kernel."""

from leo_twin.core.event_queue import EventQueue
from leo_twin.core.simulation_module import SimulationModule
from leo_twin.schema import SimEvent


class SimulationKernel:
    """Own simulation time, event scheduling, and module dispatch."""

    def __init__(self) -> None:
        self._event_queue = EventQueue()
        self._modules: dict[str, SimulationModule] = {}
        self._current_time = 0.0
        self._stopped = False

    def register_module(self, module: SimulationModule) -> None:
        module_name = module.name()
        if module_name in self._modules:
            raise ValueError(f"module already registered: {module_name!r}")
        self._modules[module_name] = module

    def schedule_event(self, event: SimEvent) -> None:
        if event.sim_time < self._current_time:
            raise ValueError(
                "cannot schedule an event before the current simulation time"
            )
        self._event_queue.push(event)

    def run(self, until_time: float | None = None) -> tuple[SimEvent, ...]:
        processed_events: list[SimEvent] = []

        while not self._event_queue.is_empty() and not self._stopped:
            next_event = self._event_queue.peek()
            if until_time is not None and next_event.sim_time > until_time:
                break

            try:
                module = self._modules[next_event.target]
            except KeyError as exc:
                raise KeyError(
                    f"no module registered for target: {next_event.target!r}"
                ) from exc

            event = self._event_queue.pop()
            self._current_time = event.sim_time
            processed_events.append(event)
            module.on_event(event, self)

        return tuple(processed_events)

    def stop(self) -> None:
        self._stopped = True

    def get_current_time(self) -> float:
        return self._current_time
