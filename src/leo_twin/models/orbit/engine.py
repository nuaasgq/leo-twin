"""Event-driven deterministic satellite motion generator."""

from collections.abc import Iterable
from math import cos, isfinite, sin
from typing import Any

from leo_twin.core import SimulationKernel, SimulationModule
from leo_twin.models.orbit.contracts import OrbitSatelliteConfig
from leo_twin.schema import EventType, SatelliteState, SimEvent


class OrbitEngine(SimulationModule):
    """Publish simplified circular satellite states on orbit triggers."""

    def __init__(
        self,
        satellites: Iterable[OrbitSatelliteConfig],
        module_name: str = "orbit",
        update_targets: Iterable[str] = ("network", "metrics"),
    ) -> None:
        _require_non_empty_str(module_name, "module_name")
        self._module_name = module_name
        self._satellites = tuple(
            sorted(satellites, key=lambda item: item.satellite_id)
        )
        if not self._satellites:
            raise ValueError("satellites must contain at least one config")

        configured_targets = tuple(update_targets)
        if not configured_targets:
            raise ValueError("update_targets must contain at least one target")
        for target in configured_targets:
            _require_non_empty_str(target, "update_targets")
        self._update_targets = tuple(sorted(set(configured_targets)))

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
                        sim_time=event.sim_time,
                        target=target,
                        payload=state,
                    )
                )

    def states_at(self, sim_time: float) -> tuple[SatelliteState, ...]:
        """Return deterministic satellite states at one simulation time."""

        _require_finite_number(sim_time, "sim_time")
        return tuple(self._state_for(config, sim_time) for config in self._satellites)

    def _state_for(
        self,
        config: OrbitSatelliteConfig,
        sim_time: float,
    ) -> SatelliteState:
        theta = config.phase + config.angular_velocity * sim_time
        radius = config.orbital_radius
        cos_theta = cos(theta)
        sin_theta = sin(theta)
        cos_inclination = cos(config.inclination)
        sin_inclination = sin(config.inclination)

        position = (
            radius * cos_theta,
            radius * sin_theta * cos_inclination,
            radius * sin_theta * sin_inclination,
        )
        velocity = (
            -radius * config.angular_velocity * sin_theta,
            radius * config.angular_velocity * cos_theta * cos_inclination,
            radius * config.angular_velocity * cos_theta * sin_inclination,
        )

        return SatelliteState(
            satellite_id=config.satellite_id,
            sim_time=sim_time,
            position=position,
            velocity=velocity,
            status=config.status,
        )

    def _event(
        self,
        sim_time: float,
        target: str,
        payload: SatelliteState,
    ) -> SimEvent:
        self._event_sequence += 1
        return SimEvent(
            event_id=f"{self._module_name}:orbit-update:{self._event_sequence:08d}",
            sim_time=sim_time,
            priority=0,
            source=self._module_name,
            target=target,
            event_type=EventType.ORBIT_UPDATE.value,
            payload=payload,
        )


def _require_non_empty_str(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value:
        raise TypeError(f"{field_name} must be a non-empty str")


def _require_finite_number(value: Any, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field_name} must be an int or float")
    if not isfinite(value):
        raise ValueError(f"{field_name} must be finite")
