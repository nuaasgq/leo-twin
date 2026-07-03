from math import pi

import pytest

from leo_twin.core import SimulationKernel, SimulationModule
from leo_twin.models.orbit import OrbitEngine, OrbitSatelliteConfig
from leo_twin.schema import EventType, SatelliteState, SimEvent


class OrbitSink(SimulationModule):
    def __init__(self, module_name: str) -> None:
        self._module_name = module_name
        self.states: list[SatelliteState] = []

    def name(self) -> str:
        return self._module_name

    def on_event(self, event: SimEvent, kernel: SimulationKernel) -> None:
        if event.event_type == EventType.ORBIT_UPDATE:
            self.states.append(event.payload)


class RecordingKernel:
    def __init__(self) -> None:
        self.scheduled_events: list[SimEvent] = []

    def schedule_event(self, event: SimEvent) -> None:
        self.scheduled_events.append(event)


def _engine(
    update_targets: tuple[str, ...] = ("network", "metrics"),
) -> OrbitEngine:
    return OrbitEngine(
        satellites=(
            OrbitSatelliteConfig(
                satellite_id="sat-b",
                orbital_radius=20.0,
                angular_velocity=0.25,
                phase=pi / 2,
                inclination=pi / 2,
            ),
            OrbitSatelliteConfig(
                satellite_id="sat-a",
                orbital_radius=10.0,
                angular_velocity=0.5,
            ),
        ),
        update_targets=update_targets,
    )


def _trigger(event_id: int | str = "trigger", sim_time: float = 0.0) -> SimEvent:
    return SimEvent(
        event_id=event_id,
        sim_time=sim_time,
        priority=0,
        source="scenario",
        target="orbit",
        event_type=EventType.ORBIT_TRIGGER.value,
        payload=None,
    )


def test_satellite_motion_is_deterministic_and_sorted() -> None:
    engine = _engine()

    first = engine.states_at(0.0)
    second = engine.states_at(0.0)

    assert first == second
    assert [state.satellite_id for state in first] == ["sat-a", "sat-b"]
    assert first[0] == SatelliteState(
        satellite_id="sat-a",
        sim_time=0.0,
        position=(10.0, 0.0, 0.0),
        velocity=(-0.0, 5.0, 0.0),
        status="ACTIVE",
    )
    assert first[1].position == pytest.approx((0.0, 0.0, 20.0))
    assert first[1].velocity == pytest.approx((-5.0, 0.0, 0.0))


def test_orbit_trigger_schedules_update_events_only_through_kernel() -> None:
    engine = _engine(update_targets=("network", "metrics"))
    kernel = RecordingKernel()

    result = engine.on_event(_trigger(sim_time=4.0), kernel)

    assert result is None
    assert [event.event_id for event in kernel.scheduled_events] == [
        "orbit:orbit-update:00000001",
        "orbit:orbit-update:00000002",
        "orbit:orbit-update:00000003",
        "orbit:orbit-update:00000004",
    ]
    assert [
        (event.event_type, event.source, event.target)
        for event in kernel.scheduled_events
    ] == [
        (EventType.ORBIT_UPDATE.value, "orbit", "metrics"),
        (EventType.ORBIT_UPDATE.value, "orbit", "network"),
        (EventType.ORBIT_UPDATE.value, "orbit", "metrics"),
        (EventType.ORBIT_UPDATE.value, "orbit", "network"),
    ]
    assert all(
        isinstance(event.payload, SatelliteState)
        for event in kernel.scheduled_events
    )
    assert {event.payload.satellite_id for event in kernel.scheduled_events} == {
        "sat-a",
        "sat-b",
    }


def test_non_orbit_trigger_event_is_ignored() -> None:
    engine = _engine()
    kernel = RecordingKernel()
    event = SimEvent(
        event_id="ignore",
        sim_time=0.0,
        priority=0,
        source="scenario",
        target="orbit",
        event_type=EventType.FLOW_ARRIVAL.value,
        payload=None,
    )

    engine.on_event(event, kernel)

    assert kernel.scheduled_events == []


def test_orbit_engine_integrates_with_simulation_kernel() -> None:
    kernel = SimulationKernel()
    engine = OrbitEngine(
        satellites=(
            OrbitSatelliteConfig(
                satellite_id="sat-1",
                orbital_radius=10.0,
                angular_velocity=pi / 2,
            ),
        )
    )
    network = OrbitSink("network")
    metrics = OrbitSink("metrics")
    kernel.register_module(engine)
    kernel.register_module(network)
    kernel.register_module(metrics)
    kernel.schedule_event(_trigger(event_id=1, sim_time=1.0))

    processed = kernel.run()

    assert [event.event_type for event in processed] == [
        EventType.ORBIT_TRIGGER.value,
        EventType.ORBIT_UPDATE.value,
        EventType.ORBIT_UPDATE.value,
    ]
    expected = SatelliteState(
        satellite_id="sat-1",
        sim_time=1.0,
        position=(0.0, 10.0, 0.0),
        velocity=(-5.0 * pi, 0.0, 0.0),
        status="ACTIVE",
    )
    assert network.states[0].position == pytest.approx(expected.position)
    assert network.states[0].velocity == pytest.approx(expected.velocity)
    assert metrics.states == network.states
