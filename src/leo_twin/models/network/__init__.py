"""Network module package for flow-level event-driven routing."""

from leo_twin.models.network.contracts import NetworkModuleContract
from leo_twin.models.network.engine import NetworkEngine
from leo_twin.models.network.geometry import (
    AccessLinkCandidate,
    GroundEndpoint,
    GroundEndpointIndex,
    PositionDrivenAccessModel,
)
from leo_twin.models.network.position_engine import PositionDrivenNetworkEngine
from leo_twin.models.network.stack import (
    LayerTrace,
    NetworkStackRuntime,
    NetworkStackTrace,
    build_default_leo_protocol_stack,
)

NetworkModule = NetworkEngine

__all__ = [
    "AccessLinkCandidate",
    "GroundEndpoint",
    "GroundEndpointIndex",
    "LayerTrace",
    "NetworkEngine",
    "NetworkModule",
    "NetworkModuleContract",
    "NetworkStackRuntime",
    "NetworkStackTrace",
    "PositionDrivenAccessModel",
    "PositionDrivenNetworkEngine",
    "build_default_leo_protocol_stack",
]
