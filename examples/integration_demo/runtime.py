"""Full-system integration demo runner."""

from __future__ import annotations

from dataclasses import dataclass

from leo_twin.core import SimulationKernel, SimulationModule
from leo_twin.models.compute import ComputeEngine
from leo_twin.models.network import NetworkEngine
from leo_twin.models.orbit import OrbitEngine
from leo_twin.schema import SimEvent
from leo_twin.services.metrics import MetricsCollector

from examples.integration_demo.config import DemoConfig
from examples.integration_demo.replay import DemoStateProjector, ReplayResult, replay_events
from examples.integration_demo.scenario import DemoScenario, build_demo_scenario
from examples.integration_demo.serialization import JsonValue, events_jsonl


@dataclass(frozen=True)
class DemoRunResult:
    config: DemoConfig
    scenario: DemoScenario
    processed_events: tuple[SimEvent, ...]
    frontend_events: tuple[SimEvent, ...]
    final_snapshot: dict[str, JsonValue]
    state_timeline: tuple[dict[str, JsonValue], ...]
    metrics_summary: dict[str, str | float | int | bool]
    replay: ReplayResult

    def event_log_jsonl(self) -> str:
        return events_jsonl(self.processed_events)


class FrontendEventSink(SimulationModule):
    """Receive frontend-bound events through the kernel for demo logging."""

    def __init__(self, module_name: str = "frontend") -> None:
        self._module_name = module_name
        self._events: list[SimEvent] = []

    def name(self) -> str:
        return self._module_name

    def on_event(self, event: SimEvent, kernel: SimulationKernel) -> None:
        self._events.append(event)

    def events(self) -> tuple[SimEvent, ...]:
        return tuple(self._events)


def run_integration_demo(config: DemoConfig) -> DemoRunResult:
    scenario = build_demo_scenario(config)
    kernel = SimulationKernel()
    frontend_sink = FrontendEventSink()
    metrics = MetricsCollector(
        emit_metric_events=True,
        metric_target=frontend_sink.name(),
        record_limit=100_000,
        event_log_limit=100_000,
        metric_sample_interval=config.metric_sample_interval,
        event_log_sample_interval=1,
        event_log_segment_size=10_000,
    )

    modules: tuple[SimulationModule, ...] = (
        OrbitEngine(
            satellites=scenario.orbit_satellites,
            update_targets=("network", "metrics"),
        ),
        NetworkEngine(
            satellites=scenario.network_satellites,
            ground_users=scenario.ground_users,
            slot_duration=float(config.network_slot_seconds),
            route_targets=("compute", "metrics"),
        ),
        ComputeEngine(nodes=scenario.compute_nodes),
        metrics,
        frontend_sink,
    )
    for module in modules:
        kernel.register_module(module)

    for event in scenario.initial_events:
        kernel.schedule_event(event)

    processed_events = kernel.run()
    projector = DemoStateProjector(
        scenario.ground_user_render_states,
        config.state_snapshot_interval_events,
    )
    for event in processed_events:
        projector.apply(event)

    replay = replay_events(
        processed_events,
        scenario.ground_user_render_states,
        config.state_snapshot_interval_events,
    )
    return DemoRunResult(
        config=config,
        scenario=scenario,
        processed_events=processed_events,
        frontend_events=frontend_sink.events(),
        final_snapshot=projector.snapshot(),
        state_timeline=projector.timeline(),
        metrics_summary=metrics.summary(),
        replay=replay,
    )
