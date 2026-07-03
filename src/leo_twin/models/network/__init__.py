"""Network module package for flow-level event-driven routing."""

from leo_twin.models.network.contracts import NetworkModuleContract
from leo_twin.models.network.channel import (
    ChannelBudgetSelector,
    LinkBudgetCalculator,
    LinkBudgetResult,
    RainFadeProfile,
    RadioTerminalProfile,
    antenna_pointing_loss_db,
    free_space_path_loss_db,
    shannon_capacity_mbps,
    thermal_noise_power_dbw,
)
from leo_twin.models.network.engine import NetworkEngine
from leo_twin.models.network.geometry import (
    AccessLinkCandidate,
    GroundEndpoint,
    GroundEndpointIndex,
    PositionDrivenAccessModel,
)
from leo_twin.models.network.position_engine import PositionDrivenNetworkEngine
from leo_twin.models.network.routing import (
    RoutingCostProfile,
    RoutingRuntime,
    StaticRouteEntry,
)
from leo_twin.models.network.stack import (
    LayerTrace,
    NetworkStackRuntime,
    NetworkStackTrace,
    build_default_leo_protocol_stack,
)
from leo_twin.models.network.transport import (
    TransportDecision,
    TransportProfile,
    TransportRuntime,
    default_transport_runtime,
)

NetworkModule = NetworkEngine

__all__ = [
    "AccessLinkCandidate",
    "ChannelBudgetSelector",
    "GroundEndpoint",
    "GroundEndpointIndex",
    "LayerTrace",
    "LinkBudgetCalculator",
    "LinkBudgetResult",
    "NetworkEngine",
    "NetworkModule",
    "NetworkModuleContract",
    "NetworkStackRuntime",
    "NetworkStackTrace",
    "PositionDrivenAccessModel",
    "PositionDrivenNetworkEngine",
    "RainFadeProfile",
    "RadioTerminalProfile",
    "RoutingCostProfile",
    "RoutingRuntime",
    "StaticRouteEntry",
    "TransportDecision",
    "TransportProfile",
    "TransportRuntime",
    "antenna_pointing_loss_db",
    "build_default_leo_protocol_stack",
    "default_transport_runtime",
    "free_space_path_loss_db",
    "shannon_capacity_mbps",
    "thermal_noise_power_dbw",
]
