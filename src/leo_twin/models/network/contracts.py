"""Network module contract local to the network package."""

from typing import Protocol

from leo_twin.core import SimulationKernel
from leo_twin.schema import AccessAssociation, SimEvent


class NetworkModuleContract(Protocol):
    """Formal interface implemented by the Network module."""

    def name(self) -> str:
        ...

    def on_event(self, event: SimEvent, kernel: SimulationKernel) -> None:
        ...

    def update_topology(self, sim_time: float) -> tuple[SimEvent, ...]:
        ...

    def compute_access(self) -> tuple[AccessAssociation, ...]:
        ...
