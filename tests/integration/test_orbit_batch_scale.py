from __future__ import annotations

from pathlib import Path

from leo_twin.core import SimulationKernel, SimulationModule
from leo_twin.models.network import GroundEndpoint, PositionDrivenNetworkEngine
from leo_twin.models.orbit import KeplerianOrbitEngine, OrbitUpdateMode
from leo_twin.schema import (
    EventType,
    OrbitBatchState,
    OrbitalElementSet,
    SatelliteState,
    SimEvent,
)
from leo_twin.services.metrics import MetricsCollector


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class _EventSink(SimulationModule):
    def __init__(self, module_name: str) -> None:
        self._module_name = module_name
        self.events: list[SimEvent] = []

    def name(self) -> str:
        return self._module_name

    def on_event(self, event: SimEvent, kernel: SimulationKernel) -> None:
        self.events.append(event)


def test_72_satellites_keep_per_satellite_orbit_updates_deterministically() -> None:
    first = _run_orbit_once(72)
    second = _run_orbit_once(72)

    assert [event.event_id for event in first] == [event.event_id for event in second]
    assert [event.event_type for event in first] == [event.event_type for event in second]
    assert EventType.ORBIT_UPDATE.value in {event.event_type for event in first}
    assert EventType.ORBIT_BATCH_UPDATE.value not in {event.event_type for event in first}


def test_1200_satellites_use_orbit_batch_update_by_default() -> None:
    processed = _run_orbit_once(1200)
    event_types = [event.event_type for event in processed]

    assert event_types.count(EventType.ORBIT_TRIGGER.value) == 1
    assert event_types.count(EventType.ORBIT_BATCH_UPDATE.value) == 2
    assert EventType.ORBIT_UPDATE.value not in event_types


def test_orbit_batch_update_contains_all_satellite_states_for_tick() -> None:
    processed = _run_orbit_once(1200)
    batches = [
        event.payload
        for event in processed
        if event.event_type == EventType.ORBIT_BATCH_UPDATE.value
    ]

    assert len(batches) == 2
    assert all(isinstance(batch, OrbitBatchState) for batch in batches)
    assert all(batch.satellite_count == 1200 for batch in batches)
    assert all(len(batch.satellite_states) == 1200 for batch in batches)
    assert batches[0].satellite_states == batches[1].satellite_states


def test_position_network_engine_consumes_orbit_batch_update() -> None:
    kernel = SimulationKernel()
    network = PositionDrivenNetworkEngine(
        endpoints=(
            GroundEndpoint(
                endpoint_id="user-001",
                position=(6371.0, 0.0, 0.0),
                min_elevation_deg=0.0,
                max_range_km=1000.0,
            ),
        ),
        compute_node_ids=("sat-001",),
        metrics_target="metrics",
        route_targets=("metrics",),
        position_scale_to_km=1.0,
    )
    metrics = _EventSink("metrics")
    kernel.register_module(network)
    kernel.register_module(metrics)
    kernel.schedule_event(
        _event(
            event_id="orbit-batch",
            target="network",
            event_type=EventType.ORBIT_BATCH_UPDATE.value,
            payload=_batch(
                (
                    _state("sat-001", (7000.0, 0.0, 0.0)),
                    _state("sat-002", (0.0, 7000.0, 0.0)),
                )
            ),
        )
    )

    kernel.run()

    assert network.active_link_states()
    assert {event.event_type for event in metrics.events} >= {
        EventType.ACCESS_START.value,
        EventType.LINK_UPDATE.value,
    }


def test_metrics_collector_consumes_orbit_batch_update_summary() -> None:
    kernel = SimulationKernel()
    metrics = MetricsCollector()
    kernel.register_module(metrics)
    kernel.schedule_event(
        _event(
            event_id="orbit-batch",
            target="metrics",
            event_type=EventType.ORBIT_BATCH_UPDATE.value,
            payload=_batch(
                (
                    _state("sat-001", (7000.0, 0.0, 0.0), sim_time=10.0),
                    _state("sat-002", (0.0, 7000.0, 0.0), sim_time=10.0),
                    _state("sat-003", (0.0, 0.0, 7000.0), sim_time=10.0),
                ),
                sim_time=10.0,
            ),
            sim_time=10.0,
        )
    )

    kernel.run()
    summary = metrics.summary()

    assert summary["satellite_count"] == 3
    assert summary["last_orbit_update_time"] == 10.0
    assert summary["batch_size"] == 3
    assert summary["orbit_event_reduction_ratio"] == 3.0
    assert summary["events.ORBIT_BATCH_UPDATE.count"] == 1


def test_batch_mode_reduces_orbit_event_count_by_one_order_of_magnitude() -> None:
    per_satellite = _run_orbit_once(1200, update_mode=OrbitUpdateMode.PER_SATELLITE)
    batched = _run_orbit_once(1200)
    per_satellite_orbit_events = sum(
        1 for event in per_satellite if event.event_type == EventType.ORBIT_UPDATE.value
    )
    batched_orbit_events = sum(
        1 for event in batched if event.event_type == EventType.ORBIT_BATCH_UPDATE.value
    )

    assert per_satellite_orbit_events == 2400
    assert batched_orbit_events == 2
    assert per_satellite_orbit_events / batched_orbit_events >= 10


def test_event_kernel_remains_free_of_orbit_batch_domain_logic() -> None:
    kernel_source = (PROJECT_ROOT / "src/leo_twin/core/kernel.py").read_text(
        encoding="utf-8"
    )

    assert "ORBIT_BATCH_UPDATE" not in kernel_source
    assert "OrbitBatchState" not in kernel_source


def _run_orbit_once(
    satellite_count: int,
    *,
    update_mode: OrbitUpdateMode | None = None,
) -> tuple[SimEvent, ...]:
    kernel = SimulationKernel()
    orbit = KeplerianOrbitEngine(
        elements=_elements(satellite_count),
        update_targets=("network", "metrics"),
        update_mode=update_mode,
    )
    kernel.register_module(orbit)
    kernel.register_module(_EventSink("network"))
    kernel.register_module(_EventSink("metrics"))
    kernel.schedule_event(
        _event(
            event_id="trigger",
            target="orbit",
            event_type=EventType.ORBIT_TRIGGER.value,
            payload=None,
        )
    )
    return kernel.run()


def _elements(count: int) -> tuple[OrbitalElementSet, ...]:
    return tuple(
        OrbitalElementSet(
            satellite_id=f"sat-{index:04d}",
            epoch=0.0,
            semi_major_axis_km=6921.0 + float(index % 5),
            eccentricity=0.001,
            inclination_deg=53.0,
            raan_deg=float((index * 11) % 360),
            argument_of_perigee_deg=0.0,
            mean_anomaly_deg=float((index * 7) % 360),
        )
        for index in range(count)
    )


def _batch(
    states: tuple[SatelliteState, ...],
    *,
    sim_time: float = 0.0,
) -> OrbitBatchState:
    return OrbitBatchState(
        sim_time=sim_time,
        satellite_states=states,
        satellite_count=len(states),
    )


def _state(
    satellite_id: str,
    position: tuple[float, float, float],
    *,
    sim_time: float = 0.0,
) -> SatelliteState:
    return SatelliteState(
        satellite_id=satellite_id,
        sim_time=sim_time,
        position=position,
        velocity=(0.0, 0.0, 0.0),
        status="ACTIVE",
    )


def _event(
    *,
    event_id: str,
    target: str,
    event_type: str,
    payload: object,
    sim_time: float = 0.0,
) -> SimEvent:
    return SimEvent(
        event_id=event_id,
        sim_time=sim_time,
        priority=0,
        source="test",
        target=target,
        event_type=event_type,
        payload=payload,
    )
