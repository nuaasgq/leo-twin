from __future__ import annotations

from pathlib import Path

from leo_twin.schema import EventType, SimEvent
from leo_twin.services.control import (
    EventFlowPolicy,
    PartitionedEventBuffer,
    PerformanceMode,
    RingBuffer,
    ScaleConfig,
    ScaleSafetyChecker,
    SegmentedReplayLog,
    SemanticEventCompressor,
    SnapshotDownsampler,
)


SATELLITE_COUNT = 10_000
USER_COUNT = 100_000
EVENT_COUNT = 1_000_000


def test_10k_stability_v2_runs_bounded_partitioned_scale_stream(tmp_path) -> None:
    checker = ScaleSafetyChecker()
    report = checker.raise_if_unsafe(
        ScaleConfig(
            satellite_count=SATELLITE_COUNT,
            user_count=USER_COUNT,
            compute_node_count=100,
            simulation_duration=100.0,
            tick_interval=1.0,
            average_events_per_entity_per_tick=0.1,
            partition_count=1000,
            max_event_count=1_500_000,
            max_queue_depth=128,
            event_log_limit=4096,
        ),
        source_paths=(
            Path("src/leo_twin/models/network/engine.py"),
            Path("src/leo_twin/models/compute/engine.py"),
        ),
    )
    assert report.allowed
    assert report.estimated_events >= EVENT_COUNT
    assert report.estimated_queue_depth <= 128

    partitioned_buffer = PartitionedEventBuffer(
        region_count=2048,
        max_events_per_partition=16,
    )
    compressor = SemanticEventCompressor(
        window_seconds=10.0,
        max_events_per_group=64,
        keep_replay_events=False,
        region_count=2048,
    )
    recent_events = RingBuffer[str](capacity=4096)
    compressed_batches = RingBuffer[tuple[str, str, int]](capacity=4096)
    snapshots = SnapshotDownsampler[tuple[int, int, int]](
        interval=10_000,
        capacity=128,
    )
    replay_log = SegmentedReplayLog(tmp_path / "replay", segment_size=65_536)

    for index in range(EVENT_COUNT):
        event = _orbit_event(index)
        key = partitioned_buffer.push(event)
        assert partitioned_buffer.pop_partition(key) == event
        recent_events.append(str(event.event_id))
        replay_log.append_line(str(event.event_id))
        for batch in compressor.ingest(event):
            compressed_batches.append(
                (batch.batch_id, batch.event_digest, batch.event_count)
            )
        if index > 0 and index % SATELLITE_COUNT == 0:
            for batch in compressor.flush_window_before(float(index // SATELLITE_COUNT)):
                compressed_batches.append(
                    (batch.batch_id, batch.event_digest, batch.event_count)
                )
        if index == 0 or index % 10_000 == 0:
            snapshots.observe((index, 0, compressed_batches.snapshot().size))

    for batch in compressor.flush_all():
        compressed_batches.append((batch.batch_id, batch.event_digest, batch.event_count))
    replay_log.flush()

    partition_snapshot = partitioned_buffer.snapshot()
    assert partition_snapshot.total_events == 0
    assert partition_snapshot.pushed == EVENT_COUNT
    assert partition_snapshot.popped == EVENT_COUNT
    assert partition_snapshot.max_partition_depth == 0
    assert recent_events.snapshot().size == 4096
    assert recent_events.snapshot().dropped == EVENT_COUNT - 4096
    assert compressed_batches.snapshot().size <= 4096
    assert snapshots.buffer_snapshot().size <= 128
    assert replay_log.total_items() == EVENT_COUNT
    assert all(segment.item_count <= 65_536 for segment in replay_log.segments())


def test_scale_compression_is_deterministic_and_reconstructable() -> None:
    first = _compressed_signature()
    second = _compressed_signature()

    assert first == second

    compressor = SemanticEventCompressor(
        window_seconds=100.0,
        max_events_per_group=32,
        keep_replay_events=True,
    )
    source_events = tuple(_orbit_event(index * SATELLITE_COUNT) for index in range(32))
    for event in source_events:
        emitted = compressor.ingest(event)
        if emitted:
            batch = emitted[0]
            break
    else:
        batch = compressor.flush_all()[0]

    assert batch.compressed_type == "ORBIT_BATCH_UPDATE"
    assert compressor.reconstruct(batch) == source_events


def test_scale_safety_detects_quadratic_patterns_and_unsafe_modes(tmp_path) -> None:
    checker = ScaleSafetyChecker()
    unsafe_report = checker.validate(
        ScaleConfig(
            satellite_count=SATELLITE_COUNT,
            user_count=USER_COUNT,
            simulation_duration=100.0,
            tick_interval=1.0,
            average_events_per_entity_per_tick=0.1,
            partition_count=1000,
            partitioned_execution=False,
            compression_enabled=False,
            frontend_batch_size=100,
            snapshot_interval_events=100,
            max_event_count=1_500_000,
        )
    )

    assert not unsafe_report.allowed
    assert "scale runs require partitioned event execution" in unsafe_report.violations
    assert "scale runs require semantic event compression" in unsafe_report.violations
    assert "frontend websocket batch size is too small for scale runs" in unsafe_report.violations
    assert "snapshot interval is too frequent for scale runs" in unsafe_report.violations

    pairwise_source = tmp_path / "pairwise.py"
    pairwise_source.write_text(
        "\n".join(
            (
                "def full_scan(satellites, ground_users):",
                "    for satellite in satellites:",
                "        for user in ground_users:",
                "            yield satellite, user",
            )
        ),
        encoding="utf-8",
    )
    report = checker.validate(
        ScaleConfig(
            satellite_count=SATELLITE_COUNT,
            user_count=USER_COUNT,
            simulation_duration=10.0,
            max_event_count=1_500_000,
        ),
        source_paths=(pairwise_source,),
    )
    assert not report.allowed
    assert any("nested satellite/user scan" in violation for violation in report.violations)


def test_scale_modes_and_frontend_protection_contracts() -> None:
    normal = EventFlowPolicy.for_mode(PerformanceMode.NORMAL)
    optimized = EventFlowPolicy.for_mode(PerformanceMode.OPTIMIZED)
    scale = EventFlowPolicy.for_mode(PerformanceMode.SCALE)

    assert not normal.partitioning_enabled
    assert optimized.partitioning_enabled
    assert optimized.compression_enabled
    assert scale.partitioning_enabled
    assert scale.compression_enabled
    assert scale.frontend_batch_size >= 2000
    assert scale.snapshot_interval_events >= 10_000

    websocket_client = Path("frontend/src/stream/websocket_client/index.ts").read_text(
        encoding="utf-8"
    )
    sync_engine = Path("frontend/src/core/sync_engine/index.ts").read_text(
        encoding="utf-8"
    )
    state_store = Path("frontend/src/stream/state_store/index.ts").read_text(
        encoding="utf-8"
    )

    assert "batchSize" in websocket_client
    assert "flushIntervalMs" in websocket_client
    assert "requestAnimationFrame" in sync_engine
    assert "eventLogLimit" in state_store
    assert "this.publish();" in state_store


def _compressed_signature() -> tuple[tuple[str, str, int], ...]:
    compressor = SemanticEventCompressor(
        window_seconds=10.0,
        max_events_per_group=64,
        keep_replay_events=False,
        region_count=2048,
    )
    batches: list[tuple[str, str, int]] = []
    for index in range(50_000):
        for batch in compressor.ingest(_orbit_event(index)):
            batches.append((batch.batch_id, batch.event_digest, batch.event_count))
        if index > 0 and index % SATELLITE_COUNT == 0:
            for batch in compressor.flush_window_before(float(index // SATELLITE_COUNT)):
                batches.append((batch.batch_id, batch.event_digest, batch.event_count))
    for batch in compressor.flush_all():
        batches.append((batch.batch_id, batch.event_digest, batch.event_count))
    return tuple(batches)


def _orbit_event(index: int) -> SimEvent:
    satellite_index = index % SATELLITE_COUNT
    tick = index // SATELLITE_COUNT
    return SimEvent(
        event_id=f"orbit:{index:07d}",
        sim_time=float(tick),
        priority=0,
        source="orbit",
        target="frontend",
        event_type=EventType.ORBIT_UPDATE.value,
        payload={
            "satellite_id": f"sat-{satellite_index:05d}",
            "region_id": f"region-{satellite_index % 2048:04d}",
            "sim_time": float(tick),
            "position": (float(satellite_index), float(tick), 0.0),
            "status": "ACTIVE",
        },
    )
