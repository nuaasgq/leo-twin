"""Interface implemented by event-driven simulation modules."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from leo_twin.schema import SimEvent

if TYPE_CHECKING:
    from leo_twin.core.kernel import SimulationKernel


class SimulationModule(ABC):
    """A module that reacts to events scheduled by the kernel."""

    @abstractmethod
    def on_event(self, event: SimEvent, kernel: "SimulationKernel") -> None:
        """Handle one event and optionally schedule new events."""

    @abstractmethod
    def name(self) -> str:
        """Return the deterministic module registration name."""
