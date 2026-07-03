from __future__ import annotations

from dataclasses import dataclass

from leo_twin.core import SimulationKernel, SimulationModule
from leo_twin.schema import EventType, SimEvent
from leo_twin.services.control import (
    ControlledModule,
    EventFlowController,
    EventFlowPolicy,
    PerformanceMode,
    ScaleConfig,
    ScaleSafetyChecker,
)
from leo_twin.services.metrics import MetricsCollector


@dataclass(frozen=True)
class _ScaleRunResult:
    processed: tuple[tuple[str, float, int, str, str, str], ...]
    sink_events: tuple[str, ...]
    snapshot: tuple[int, int, int, int, int]


class _BurstModule(SimulationModule):
    def name(self) -> str:
        return "burst"

    def on_event(self, event: SimEvent, kernel) -> None:  # type: ignore[no-untyped-def]
        if event.event_type != "BURST":
            return

        for index in range(10):
            kernel.schedule_event(
                _event(
                    event_id=f"burst:dup:{index:04d}",
                    event_type="DUPLICATE_DELTA",
                    priority=0,
                    payload={"delta": "same"},
                )
            )

        for index in range(10):
            kernel.schedule_event(
                _event(
                    event_id=f"burst:low:{index:04d}",
                    event_type="LOW_PRIORITY",
                    priority=-1,
                    payload={"index": index},
                )
            )

        for index in range(10):
            kernel.schedule_event(
                _event(
                    event_id=f"burst:metric:{index:04d}",
                    event_type=EventType.METRIC_SAMPLE.value,
                    priority=0,
                    payload={"index": index},
                )
            )

        for index in range(30):
            kernel.schedule_event(
                _event(
                    event_id=f"burst:unique:{index:04d}",
                    event_type="UNIQUE_DELTA",
                    priority=0,
                    payload={"index": index},
                )
            )


class _SinkModule(SimulationModule):
    def __init__(self) -> None:
        self.events: list[str] = []

    def name(self) -> str:
        return "sink"

    def on_event(self, event: SimEvent, kernel) -> None:  # type: ignore[no-untyped-def]
        self.events.append(str(event.event_id))


def test_scale_mode_event_flow_controls_event_growth_deterministically() -> None:
    first = _run_scale_event_flow()
    second = _run_scale_event_flow()

    assert first == second
    assert len(first.sink_events) == 25
    accepted, deduplicated, suppressed, throttled, flushed = first.snapshot
    assert accepted == 25
    assert deduplicated == 9
    assert suppressed == 10
    assert throttled == 16
    assert flushed == 25
    assert first.sink_events[0] == "burst:dup:0000"
    assert first.sink_events[-1] == "burst:unique:0023"


def test_metrics_storage_is_bounded_and_segmented_under_load() -> None:
    collector = MetricsCollector(
        record_limit=128,
        event_log_limit=64,
        metric_sample_interval=10,
        event_log_sample_interval=5,
        event_log_segment_size=16,
    )

    for index in range(100_000):
        collector.observe(
            SimEvent(
                event_id=f"load:{index:06d}",
                sim_time=float(index),
                priority=0,
                source="load",
                target="metrics",
                event_type="LOAD_EVENT",
                payload={"bucket": index % 4},
            )
        )

    assert collector.summary()["event_count"] == 100_000
    assert len(collector.records()) <= 128
    assert len(collector.event_log()) <= 64

    segments = collector.events_jsonl_segments()
    assert len(segments) == 4
    assert all(1 <= len(segment.splitlines()) <= 16 for segment in segments)


def test_scale_safety_checker_allows_10k_partitioned_run_and_blocks_unsafe(
    tmp_path,
) -> None:
    checker = ScaleSafetyChecker()
    safe_config = ScaleConfig(
        satellite_count=10_000,
        user_count=100_000,
        simulation_duration=10.0,
        tick_interval=1.0,
        average_events_per_entity_per_tick=0.1,
        partition_count=1000,
    )

    safe_report = checker.validate(safe_config)

    assert safe_report.allowed
    assert safe_report.estimated_events == 110_000
    assert safe_report.estimated_memory_bytes <= safe_config.max_memory_bytes

    unsafe_report = checker.validate(
        ScaleConfig(
            satellite_count=10_000,
            user_count=100_000,
            simulation_duration=10.0,
            tick_interval=1.0,
            average_events_per_entity_per_tick=2.0,
            indexed_topology=False,
            max_event_count=100_000,
        )
    )

    assert not unsafe_report.allowed
    assert "network topology must be indexed before scale runs" in unsafe_report.violations
    assert "estimated event count exceeds configured max_event_count" in unsafe_report.violations

    source_path = tmp_path / "unsafe_pairwise.py"
    source_path.write_text(
        "\n".join(
            (
                "def recompute(satellites, ground_users):",
                "    for satellite in satellites:",
                "        for user in ground_users:",
                "            yield satellite, user",
            )
        ),
        encoding="utf-8",
    )

    pattern_report = checker.validate(safe_config, source_paths=(source_path,))
    assert not pattern_report.allowed
    assert any("nested satellite/user scan" in item for item in pattern_report.violations)


def _run_scale_event_flow() -> _ScaleRunResult:
    policy = EventFlowPolicy(
        mode=PerformanceMode.SCALE,
        batching_enabled=True,
        time_window=5.0,
        deduplicate=True,
        priority_floor=0,
        suppressed_event_types=(EventType.METRIC_SAMPLE.value,),
        max_events_per_window=25,
    )
    controller = EventFlowController(policy)
    kernel = SimulationKernel()
    sink = _SinkModule()
    kernel.register_module(ControlledModule(_BurstModule(), controller))
    kernel.register_module(sink)
    kernel.schedule_event(
        SimEvent(
            event_id="scenario:burst:0001",
            sim_time=0.0,
            priority=0,
            source="scenario",
            target="burst",
            event_type="BURST",
            payload=None,
        )
    )

    processed = kernel.run()
    snapshot = controller.snapshot()
    return _ScaleRunResult(
        processed=tuple(
            (
                event.event_id,
                event.sim_time,
                event.priority,
                event.source,
                event.target,
                str(event.event_type),
            )
            for event in processed
        ),
        sink_events=tuple(sink.events),
        snapshot=(
            snapshot.accepted,
            snapshot.deduplicated,
            snapshot.suppressed,
            snapshot.throttled,
            snapshot.flushed,
        ),
    )


def _event(
    event_id: str,
    event_type: str,
    priority: int,
    payload: object,
) -> SimEvent:
    return SimEvent(
        event_id=event_id,
        sim_time=0.0,
        priority=priority,
        source="burst",
        target="sink",
        event_type=event_type,
        payload=payload,
    )
