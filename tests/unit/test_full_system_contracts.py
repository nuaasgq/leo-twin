from __future__ import annotations

import pytest

from leo_twin.models.coupling import (
    frontend_surface_contracts,
    full_system_coupling_contracts,
)
from leo_twin.models.compute import COMPUTE_NODE_UPDATE
from leo_twin.schema import (
    AntennaProfile,
    ChannelProfile,
    FrontendSurfaceRole,
    LinkMedium,
    NetworkLayer,
    OrbitalElementSet,
    ProtocolLayerContract,
    ProtocolStackContract,
    TransportProtocol,
)


def test_orbital_element_contract_is_deterministic_data_only() -> None:
    elements = OrbitalElementSet(
        satellite_id="SAT-001",
        epoch=0.0,
        semi_major_axis_km=6878.0,
        eccentricity=0.001,
        inclination_deg=53.0,
        raan_deg=10.0,
        argument_of_perigee_deg=20.0,
        mean_anomaly_deg=30.0,
    )

    assert elements.satellite_id == "SAT-001"
    assert elements.semi_major_axis_km == 6878.0


def test_network_stack_contract_enforces_canonical_layer_order() -> None:
    stack = ProtocolStackContract(
        stack_id="default-stack",
        layers=(
            ProtocolLayerContract(
                layer=NetworkLayer.APPLICATION,
                protocol_name="任务卸载业务流",
                inputs=("TaskRequest",),
                outputs=("FlowRequest",),
            ),
            ProtocolLayerContract(
                layer=NetworkLayer.TRANSPORT,
                protocol_name=TransportProtocol.TCP.value,
                inputs=("FlowRequest",),
                outputs=("SegmentProfile",),
            ),
                ProtocolLayerContract(
                    layer=NetworkLayer.NETWORK,
                    protocol_name="LINK_STATE",
                    inputs=("SegmentProfile",),
                    outputs=("Route",),
                ),
            ProtocolLayerContract(
                layer=NetworkLayer.DATA_LINK,
                protocol_name="SPACE_LINK_PROFILE",
                inputs=("Route",),
                outputs=("LinkState",),
            ),
            ProtocolLayerContract(
                layer=NetworkLayer.PHYSICAL,
                protocol_name="CONFIGURED_PHYSICAL_PROFILE",
                inputs=("LinkState",),
                outputs=("ChannelProfile",),
            ),
            ProtocolLayerContract(
                layer=NetworkLayer.CHANNEL,
                protocol_name="SPACE_GROUND_CHANNEL",
                inputs=("ChannelProfile",),
                outputs=("LinkBudgetProfile",),
            ),
        ),
    )

    assert tuple(layer.layer for layer in stack.layers) == (
        NetworkLayer.APPLICATION,
        NetworkLayer.TRANSPORT,
        NetworkLayer.NETWORK,
        NetworkLayer.DATA_LINK,
        NetworkLayer.PHYSICAL,
        NetworkLayer.CHANNEL,
    )


def test_network_stack_contract_rejects_layer_reordering() -> None:
    with pytest.raises(ValueError, match="canonical network stack order"):
        ProtocolStackContract(
            stack_id="bad-stack",
            layers=(
                ProtocolLayerContract(
                    layer=NetworkLayer.NETWORK,
                    protocol_name="LINK_STATE",
                    inputs=("SegmentProfile",),
                    outputs=("Route",),
                ),
                ProtocolLayerContract(
                    layer=NetworkLayer.TRANSPORT,
                    protocol_name=TransportProtocol.UDP.value,
                    inputs=("FlowRequest",),
                    outputs=("SegmentProfile",),
                ),
            ),
        )


def test_channel_and_antenna_profiles_validate_inputs() -> None:
    antenna = AntennaProfile(
        antenna_id="ANT-001",
        gain_dbi=32.5,
        beam_width_deg=2.0,
        steering_mode="electronic",
    )
    channel = ChannelProfile(
        channel_id="CH-SG-001",
        medium=LinkMedium.SPACE_GROUND,
        carrier_frequency_hz=20_000_000_000.0,
        bandwidth_hz=500_000_000.0,
        loss_model_name="configured_loss_profile",
    )

    assert antenna.steering_mode == "electronic"
    assert channel.medium == LinkMedium.SPACE_GROUND


def test_coupling_contracts_keep_domain_boundaries_event_driven() -> None:
    contracts = full_system_coupling_contracts()
    by_id = {contract.coupling_id: contract for contract in contracts}

    assert by_id["orbit-to-network-topology"].event_type == "ORBIT_UPDATE"
    assert by_id["network-to-compute-route"].event_type == "ROUTE_UPDATE"
    assert by_id["compute-to-network-load"].event_type == COMPUTE_NODE_UPDATE
    assert by_id["compute-to-network-load"].payload_schema == "ComputeNodeState"
    assert by_id["domain-to-metrics-observation"].consumer == "metrics"


def test_frontend_surface_contracts_are_chinese_and_split() -> None:
    surfaces = frontend_surface_contracts()
    roles = {surface.role for surface in surfaces}

    assert roles == {
        FrontendSurfaceRole.THREE_D_CONTROL,
        FrontendSurfaceRole.DATA_DASHBOARD,
    }
    assert any(surface.title_zh == "三维仿真与控制台" for surface in surfaces)
    assert any(surface.title_zh == "数据态势面板" for surface in surfaces)
    assert [surface.control_enabled for surface in surfaces] == [True, False]
