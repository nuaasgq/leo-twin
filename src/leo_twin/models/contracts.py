"""Formal module interface contracts for parallel domain development."""

from typing import Protocol

from leo_twin.core import SimulationKernel
from leo_twin.schema import (
    AccessAssociation,
    MetricRecord,
    Route,
    SimEvent,
)


class OrbitModuleContract(Protocol):
    """Orbit module interface contract."""

    def name(self) -> str:
        ...

    def on_event(self, event: SimEvent, kernel: SimulationKernel) -> None:
        ...


class NetworkModuleContract(Protocol):
    """Network module interface contract."""

    def name(self) -> str:
        ...

    def on_event(self, event: SimEvent, kernel: SimulationKernel) -> None:
        ...

    def update_topology(self, sim_time: float) -> tuple[SimEvent, ...]:
        ...

    def compute_access(self) -> tuple[AccessAssociation, ...]:
        ...


class ComputeModuleContract(Protocol):
    """Compute module interface contract."""

    def name(self) -> str:
        ...

    def on_event(self, event: SimEvent, kernel: SimulationKernel) -> None:
        ...


class MetricsModuleContract(Protocol):
    """Metrics module interface contract."""

    def name(self) -> str:
        ...

    def on_event(self, event: SimEvent, kernel: SimulationKernel) -> None:
        ...

    def records(self) -> tuple[MetricRecord, ...]:
        ...

    def summary(self) -> dict[str, str | float | int | bool]:
        ...
