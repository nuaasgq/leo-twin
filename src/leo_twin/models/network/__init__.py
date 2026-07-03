"""Network module package for flow-level event-driven routing."""

from leo_twin.models.network.contracts import NetworkModuleContract
from leo_twin.models.network.engine import NetworkEngine

NetworkModule = NetworkEngine

__all__ = ["NetworkEngine", "NetworkModule", "NetworkModuleContract"]
