from __future__ import annotations

from math import pi, sqrt

import pytest

from leo_twin.core import SimulationKernel, SimulationModule
from leo_twin.models.orbit import (
    J2SecularDriftProfile,
    KeplerianOrbitEngine,
    KeplerianOrbitPropagator,
)
from leo_twin.schema import EventType, OrbitalElementSet, SatelliteState, SimEvent


MU = 398600.4418


class OrbitSink(SimulationModule):
    def __init__(self, module_name: str) -> None:
        self._module_name = module_name
        self.states: list[SatelliteState] = []

    def name(self) -> str:
        return self._module_name

    def on_event(self, event: SimEvent, kernel: SimulationKernel) -> None:
        if event.event_type == EventType.ORBIT_UPDATE:
            self.states.append(event.payload)


def _element(satellite_id: str = "SAT-001") -> OrbitalElementSet:
    return OrbitalElementSet(
        satellite_id=satellite_id,
        epoch=0.0,
        semi_major_axis_km=7000.0,
        eccentricity=0.0,
        inclination_deg=0.0,
        raan_deg=0.0,
        argument_of_perigee_deg=0.0,
        mean_anomaly_deg=0.0,
    )


def _trigger(dispatch_time: float) -> SimEvent:
    return SimEvent(
        event_id="trigger",
        sim_time=dispatch_time,
        priority=0,
        source="scenario",
        target="orbit",
        event_type=EventType.ORBIT_TRIGGER.value,
        payload=None,
    )


def test_keplerian_circular_equatorial_state_at_epoch() -> None:
    propagator = KeplerianOrbitPropagator(
        elements=(_element(),),
        gravitational_parameter_km3_s2=MU,
    )

    state = propagator.states_at(0.0)[0]

    assert state.position == pytest.approx((7000.0, 0.0, 0.0))
    assert state.velocity == pytest.approx((0.0, sqrt(MU / 7000.0), 0.0))
    assert state.status == "ACTIVE"


def test_keplerian_circular_equatorial_state_after_quarter_period() -> None:
    semi_major_axis = 7000.0
    quarter_period = 0.25 * 2.0 * pi * sqrt((semi_major_axis**3) / MU)
    propagator = KeplerianOrbitPropagator(
        elements=(_element(),),
        gravitational_parameter_km3_s2=MU,
    )

    state = propagator.states_at(quarter_period)[0]

    assert state.position == pytest.approx((0.0, 7000.0, 0.0), abs=1e-8)
    assert state.velocity == pytest.approx((-sqrt(MU / 7000.0), 0.0, 0.0), abs=1e-10)


def test_keplerian_states_are_deterministic_and_sorted() -> None:
    propagator = KeplerianOrbitPropagator(
        elements=(_element("SAT-B"), _element("SAT-A")),
        gravitational_parameter_km3_s2=MU,
    )

    first = propagator.states_at(123.0)
    second = propagator.states_at(123.0)

    assert first == second
    assert [state.satellite_id for state in first] == ["SAT-A", "SAT-B"]


def test_keplerian_propagator_can_emit_earth_fixed_state() -> None:
    semi_major_axis = 7000.0
    mean_motion = sqrt(MU / (semi_major_axis**3))
    propagator = KeplerianOrbitPropagator(
        elements=(_element(),),
        gravitational_parameter_km3_s2=MU,
        earth_rotation_rate_rad_s=mean_motion,
    )

    state = propagator.states_at(10.0)[0]

    assert state.position == pytest.approx((7000.0, 0.0, 0.0), abs=1e-8)
    assert state.velocity == pytest.approx((0.0, 0.0, 0.0), abs=1e-10)


def test_j2_secular_drift_profile_produces_deterministic_rates() -> None:
    profile = J2SecularDriftProfile()

    raan_rate, argument_rate = profile.drift_rates_rad_s(
        semi_major_axis_km=7000.0,
        eccentricity=0.001,
        inclination_rad=0.9250245035569946,
        gravitational_parameter_km3_s2=MU,
    )

    assert raan_rate < 0.0
    assert argument_rate > 0.0
    assert (raan_rate, argument_rate) == profile.drift_rates_rad_s(
        semi_major_axis_km=7000.0,
        eccentricity=0.001,
        inclination_rad=0.9250245035569946,
        gravitational_parameter_km3_s2=MU,
    )


def test_keplerian_propagator_can_apply_j2_secular_drift() -> None:
    element = OrbitalElementSet(
        satellite_id="SAT-J2",
        epoch=0.0,
        semi_major_axis_km=7000.0,
        eccentricity=0.001,
        inclination_deg=53.0,
        raan_deg=10.0,
        argument_of_perigee_deg=20.0,
        mean_anomaly_deg=30.0,
    )
    base = KeplerianOrbitPropagator(
        elements=(element,),
        gravitational_parameter_km3_s2=MU,
    )
    perturbed = KeplerianOrbitPropagator(
        elements=(element,),
        gravitational_parameter_km3_s2=MU,
        j2_profile=J2SecularDriftProfile(),
    )

    base_state = base.states_at(3600.0)[0]
    first = perturbed.states_at(3600.0)[0]
    second = perturbed.states_at(3600.0)[0]

    assert first == second
    assert first.position != pytest.approx(base_state.position)
    assert first.velocity != pytest.approx(base_state.velocity)


def test_keplerian_orbit_engine_schedules_events_through_kernel() -> None:
    kernel = SimulationKernel()
    orbit = KeplerianOrbitEngine(elements=(_element(),), update_targets=("network", "metrics"))
    network = OrbitSink("network")
    metrics = OrbitSink("metrics")
    kernel.register_module(orbit)
    kernel.register_module(network)
    kernel.register_module(metrics)
    kernel.schedule_event(_trigger(60.0))

    processed = kernel.run()

    assert [event.event_type for event in processed] == [
        EventType.ORBIT_TRIGGER.value,
        EventType.ORBIT_UPDATE.value,
        EventType.ORBIT_UPDATE.value,
    ]
    assert len(network.states) == 1
    assert len(metrics.states) == 1
    assert network.states == metrics.states
    assert processed[1].event_id == "orbit:keplerian-update:00000001"


def test_keplerian_orbit_engine_can_scale_output_state_vectors() -> None:
    orbit = KeplerianOrbitEngine(
        elements=(_element(),),
        update_targets=("metrics",),
        state_vector_scale=1000.0,
    )

    state = orbit.states_at(0.0)[0]

    assert state.position == pytest.approx((7_000_000.0, 0.0, 0.0))
    assert state.velocity == pytest.approx((0.0, sqrt(MU / 7000.0) * 1000.0, 0.0))
