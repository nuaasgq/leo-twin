"""Full-system coupling contracts without cross-module implementation imports."""

from __future__ import annotations

from leo_twin.models.compute.contracts import COMPUTE_NODE_UPDATE
from leo_twin.schema import (
    CouplingContract,
    CouplingSignalType,
    FrontendSurfaceContract,
    FrontendSurfaceRole,
)


FULL_SYSTEM_COUPLING_CONTRACTS: tuple[CouplingContract, ...] = (
    CouplingContract(
        coupling_id="orbit-to-network-topology",
        signal_type=CouplingSignalType.ORBIT_TO_NETWORK,
        producer="orbit",
        consumer="network",
        event_type="ORBIT_UPDATE",
        payload_schema="SatelliteState",
        description="Satellite state updates drive coverage, topology, and link changes.",
    ),
    CouplingContract(
        coupling_id="network-to-compute-route",
        signal_type=CouplingSignalType.NETWORK_TO_COMPUTE,
        producer="network",
        consumer="compute",
        event_type="ROUTE_UPDATE",
        payload_schema="Route",
        description="Route availability and path metrics drive compute task transfer state.",
    ),
    CouplingContract(
        coupling_id="compute-to-network-load",
        signal_type=CouplingSignalType.COMPUTE_TO_NETWORK,
        producer="compute",
        consumer="network",
        event_type=COMPUTE_NODE_UPDATE,
        payload_schema="ComputeNodeState",
        description=(
            "Compute node capacity updates drive deterministic network route "
            "refreshes and capacity feedback."
        ),
    ),
    CouplingContract(
        coupling_id="domain-to-metrics-observation",
        signal_type=CouplingSignalType.DOMAIN_TO_METRICS,
        producer="domain-modules",
        consumer="metrics",
        event_type="*",
        payload_schema="read-only event payload",
        description="Metrics observes events without mutating domain state.",
    ),
)


_FRONTEND_SURFACES: tuple[FrontendSurfaceContract, ...] = (
    FrontendSurfaceContract(
        surface_id="three-d-control",
        role=FrontendSurfaceRole.THREE_D_CONTROL,
        title_zh="三维仿真与控制台",
        websocket_topics=("control", "orbit", "network", "compute", "metrics"),
        control_enabled=True,
    ),
    FrontendSurfaceContract(
        surface_id="data-dashboard",
        role=FrontendSurfaceRole.DATA_DASHBOARD,
        title_zh="数据态势面板",
        websocket_topics=("orbit", "network", "compute", "metrics"),
        control_enabled=False,
    ),
)


def full_system_coupling_contracts() -> tuple[CouplingContract, ...]:
    """Return deterministic cross-domain coupling contracts."""

    return FULL_SYSTEM_COUPLING_CONTRACTS


def frontend_surface_contracts() -> tuple[FrontendSurfaceContract, ...]:
    """Return deterministic frontend surface contracts."""

    return _FRONTEND_SURFACES
