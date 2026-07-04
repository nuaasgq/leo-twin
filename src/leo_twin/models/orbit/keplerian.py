"""Deterministic Keplerian orbit runtime module."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from math import atan2, cos, isfinite, pi, radians, sin, sqrt
from typing import Any

from leo_twin.core import SimulationKernel, SimulationModule
from leo_twin.schema import EventType, OrbitalElementSet, SatelliteState, SimEvent


@dataclass(frozen=True)
class J2SecularDriftProfile:
    """Deterministic J2 secular drift parameters for low-order orbit evolution."""

    j2: float = 1.08262668e-3
    equatorial_radius_km: float = 6378.137

    def __post_init__(self) -> None:
        _require_positive_number(self.j2, "j2")
        _require_positive_number(self.equatorial_radius_km, "equatorial_radius_km")

    def drift_rates_rad_s(
        self,
        semi_major_axis_km: float,
        eccentricity: float,
        inclination_rad: float,
        gravitational_parameter_km3_s2: float,
    ) -> tuple[float, float]:
        """Return deterministic RAAN and argument-of-perigee drift rates."""

        semi_latus_rectum = semi_major_axis_km * (1.0 - eccentricity**2)
        mean_motion = sqrt(gravitational_parameter_km3_s2 / (semi_major_axis_km**3))
        radius_ratio_squared = (self.equatorial_radius_km / semi_latus_rectum) ** 2
        inclination_cosine = cos(inclination_rad)
        factor = self.j2 * radius_ratio_squared * mean_motion
        raan_rate = -1.5 * factor * inclination_cosine
        argument_rate = 0.75 * factor * (5.0 * inclination_cosine**2 - 1.0)
        return raan_rate, argument_rate


class KeplerianOrbitPropagator:
    """Propagate configured orbital elements into inertial state vectors."""

    def __init__(
        self,
        elements: Iterable[OrbitalElementSet],
        gravitational_parameter_km3_s2: float,
        earth_rotation_rate_rad_s: float = 0.0,
        max_iterations: int = 12,
        tolerance: float = 1e-12,
        j2_profile: J2SecularDriftProfile | None = None,
    ) -> None:
        _require_positive_number(gravitational_parameter_km3_s2, "gravitational_parameter_km3_s2")
        _require_finite_number(earth_rotation_rate_rad_s, "earth_rotation_rate_rad_s")
        _require_positive_int(max_iterations, "max_iterations")
        _require_positive_number(tolerance, "tolerance")
        configured_elements = tuple(sorted(elements, key=lambda item: item.satellite_id))
        if not configured_elements:
            raise ValueError("elements must contain at least one satellite")
        self._elements = configured_elements
        self._mu = float(gravitational_parameter_km3_s2)
        self._earth_rotation_rate_rad_s = float(earth_rotation_rate_rad_s)
        self._max_iterations = max_iterations
        self._tolerance = float(tolerance)
        self._j2_profile = j2_profile

    def states_at(self, requested_time: float) -> tuple[SatelliteState, ...]:
        """Return deterministic satellite states at one simulation time."""

        _require_finite_number(requested_time, "requested_time")
        return tuple(self._state_for(element, requested_time) for element in self._elements)

    def _state_for(
        self,
        element: OrbitalElementSet,
        requested_time: float,
    ) -> SatelliteState:
        semi_major_axis = element.semi_major_axis_km
        eccentricity = element.eccentricity
        mean_motion = sqrt(self._mu / (semi_major_axis**3))
        elapsed = requested_time - element.epoch
        mean_anomaly = _normalize_radians(radians(element.mean_anomaly_deg) + mean_motion * elapsed)
        eccentric_anomaly = self._solve_eccentric_anomaly(mean_anomaly, eccentricity)
        position_perifocal, velocity_perifocal = self._perifocal_state(
            semi_major_axis,
            eccentricity,
            eccentric_anomaly,
        )
        inclination_rad = radians(element.inclination_deg)
        raan_rad = radians(element.raan_deg)
        argument_rad = radians(element.argument_of_perigee_deg)
        if self._j2_profile is not None:
            raan_rate, argument_rate = self._j2_profile.drift_rates_rad_s(
                semi_major_axis_km=semi_major_axis,
                eccentricity=eccentricity,
                inclination_rad=inclination_rad,
                gravitational_parameter_km3_s2=self._mu,
            )
            raan_rad += raan_rate * elapsed
            argument_rad += argument_rate * elapsed

        position_inertial = _rotate_perifocal_to_inertial(
            position_perifocal,
            raan_rad=raan_rad,
            inclination_rad=inclination_rad,
            argument_rad=argument_rad,
        )
        velocity_inertial = _rotate_perifocal_to_inertial(
            velocity_perifocal,
            raan_rad=raan_rad,
            inclination_rad=inclination_rad,
            argument_rad=argument_rad,
        )
        position, velocity = _inertial_to_earth_fixed(
            position=position_inertial,
            velocity=velocity_inertial,
            elapsed=elapsed,
            earth_rotation_rate_rad_s=self._earth_rotation_rate_rad_s,
        )
        return SatelliteState(
            satellite_id=element.satellite_id,
            sim_time=requested_time,
            position=position,
            velocity=velocity,
            status="ACTIVE",
        )

    def _solve_eccentric_anomaly(self, mean_anomaly: float, eccentricity: float) -> float:
        eccentric_anomaly = mean_anomaly if eccentricity < 0.8 else pi
        for _ in range(self._max_iterations):
            residual = eccentric_anomaly - eccentricity * sin(eccentric_anomaly) - mean_anomaly
            derivative = 1.0 - eccentricity * cos(eccentric_anomaly)
            delta = residual / derivative
            eccentric_anomaly -= delta
            if abs(delta) <= self._tolerance:
                break
        return eccentric_anomaly

    def _perifocal_state(
        self,
        semi_major_axis: float,
        eccentricity: float,
        eccentric_anomaly: float,
    ) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
        cos_e = cos(eccentric_anomaly)
        sin_e = sin(eccentric_anomaly)
        one_minus_e_cos_e = 1.0 - eccentricity * cos_e
        radius = semi_major_axis * one_minus_e_cos_e
        beta = sqrt(1.0 - eccentricity**2)
        position = (
            semi_major_axis * (cos_e - eccentricity),
            semi_major_axis * beta * sin_e,
            0.0,
        )
        velocity_scale = sqrt(self._mu * semi_major_axis) / radius
        velocity = (
            -velocity_scale * sin_e,
            velocity_scale * beta * cos_e,
            0.0,
        )
        return position, velocity


class KeplerianOrbitEngine(SimulationModule):
    """Publish deterministic Keplerian satellite states on orbit triggers."""

    def __init__(
        self,
        elements: Iterable[OrbitalElementSet],
        module_name: str = "orbit",
        update_targets: Iterable[str] = ("network", "metrics"),
        gravitational_parameter_km3_s2: float = 398600.4418,
        earth_rotation_rate_rad_s: float = 0.0,
        state_vector_scale: float = 1.0,
        j2_profile: J2SecularDriftProfile | None = None,
    ) -> None:
        _require_non_empty_str(module_name, "module_name")
        _require_positive_number(state_vector_scale, "state_vector_scale")
        configured_targets = tuple(update_targets)
        if not configured_targets:
            raise ValueError("update_targets must contain at least one target")
        for target in configured_targets:
            _require_non_empty_str(target, "update_targets")
        self._module_name = module_name
        self._update_targets = tuple(sorted(set(configured_targets)))
        self._propagator = KeplerianOrbitPropagator(
            elements=elements,
            gravitational_parameter_km3_s2=gravitational_parameter_km3_s2,
            earth_rotation_rate_rad_s=earth_rotation_rate_rad_s,
            j2_profile=j2_profile,
        )
        self._state_vector_scale = float(state_vector_scale)
        self._event_sequence = 0

    def name(self) -> str:
        return self._module_name

    def on_event(self, event: SimEvent, kernel: SimulationKernel) -> None:
        if event.event_type != EventType.ORBIT_TRIGGER:
            return
        for state in self.states_at(event.sim_time):
            for target in self._update_targets:
                kernel.schedule_event(
                    self._event(
                        dispatch_time=event.sim_time,
                        target=target,
                        payload=state,
                    )
                )

    def states_at(self, requested_time: float) -> tuple[SatelliteState, ...]:
        """Return deterministic satellite states at one simulation time."""

        states = self._propagator.states_at(requested_time)
        if self._state_vector_scale == 1.0:
            return states
        return tuple(self._scaled_state(state) for state in states)

    def _scaled_state(self, state: SatelliteState) -> SatelliteState:
        return SatelliteState(
            satellite_id=state.satellite_id,
            sim_time=state.sim_time,
            position=tuple(value * self._state_vector_scale for value in state.position),
            velocity=tuple(value * self._state_vector_scale for value in state.velocity),
            status=state.status,
        )

    def _event(
        self,
        dispatch_time: float,
        target: str,
        payload: SatelliteState,
    ) -> SimEvent:
        self._event_sequence += 1
        return SimEvent(
            event_id=f"{self._module_name}:keplerian-update:{self._event_sequence:08d}",
            sim_time=dispatch_time,
            priority=0,
            source=self._module_name,
            target=target,
            event_type=EventType.ORBIT_UPDATE.value,
            payload=payload,
        )


def _rotate_perifocal_to_inertial(
    vector: tuple[float, float, float],
    raan_rad: float,
    inclination_rad: float,
    argument_rad: float,
) -> tuple[float, float, float]:
    cos_raan = cos(raan_rad)
    sin_raan = sin(raan_rad)
    cos_inclination = cos(inclination_rad)
    sin_inclination = sin(inclination_rad)
    cos_argument = cos(argument_rad)
    sin_argument = sin(argument_rad)

    x_perifocal, y_perifocal, z_perifocal = vector
    x_value = (
        (cos_raan * cos_argument - sin_raan * sin_argument * cos_inclination) * x_perifocal
        + (-cos_raan * sin_argument - sin_raan * cos_argument * cos_inclination) * y_perifocal
        + (sin_raan * sin_inclination) * z_perifocal
    )
    y_value = (
        (sin_raan * cos_argument + cos_raan * sin_argument * cos_inclination) * x_perifocal
        + (-sin_raan * sin_argument + cos_raan * cos_argument * cos_inclination) * y_perifocal
        + (-cos_raan * sin_inclination) * z_perifocal
    )
    z_value = (
        (sin_argument * sin_inclination) * x_perifocal
        + (cos_argument * sin_inclination) * y_perifocal
        + (cos_inclination) * z_perifocal
    )
    return (x_value, y_value, z_value)


def _inertial_to_earth_fixed(
    position: tuple[float, float, float],
    velocity: tuple[float, float, float],
    elapsed: float,
    earth_rotation_rate_rad_s: float,
) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
    if earth_rotation_rate_rad_s == 0.0:
        return position, velocity
    theta = earth_rotation_rate_rad_s * elapsed
    rotated_position = _rotate_z(position, -theta)
    rotated_velocity = _rotate_z(velocity, -theta)
    earth_fixed_velocity = (
        rotated_velocity[0] + earth_rotation_rate_rad_s * rotated_position[1],
        rotated_velocity[1] - earth_rotation_rate_rad_s * rotated_position[0],
        rotated_velocity[2],
    )
    return rotated_position, earth_fixed_velocity


def _rotate_z(
    vector: tuple[float, float, float],
    angle_rad: float,
) -> tuple[float, float, float]:
    cos_angle = cos(angle_rad)
    sin_angle = sin(angle_rad)
    return (
        cos_angle * vector[0] - sin_angle * vector[1],
        sin_angle * vector[0] + cos_angle * vector[1],
        vector[2],
    )


def _normalize_radians(value: float) -> float:
    return atan2(sin(value), cos(value)) % (2.0 * pi)


def _require_non_empty_str(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value:
        raise TypeError(f"{field_name} must be a non-empty str")


def _require_finite_number(value: Any, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field_name} must be an int or float")
    if not isfinite(value):
        raise ValueError(f"{field_name} must be finite")


def _require_positive_number(value: Any, field_name: str) -> None:
    _require_finite_number(value, field_name)
    if value <= 0:
        raise ValueError(f"{field_name} must be positive")


def _require_positive_int(value: int, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field_name} must be an int")
    if value <= 0:
        raise ValueError(f"{field_name} must be positive")
