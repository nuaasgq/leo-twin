from __future__ import annotations

import json

from leo_twin.models.orbit import AutoPlaneAllocator
from leo_twin.schema import (
    NETWORK_MODEL_CONTRACT_V2_ID,
    NetworkKpiKind,
    NetworkLayer,
    default_network_model_contract_v2,
    network_model_contract_v2_to_dict,
)
from leo_twin.services.derived_summary import build_backend_derived_summary


def test_network_model_contract_v2_is_deterministic_and_json_ready() -> None:
    first = network_model_contract_v2_to_dict()
    second = network_model_contract_v2_to_dict(default_network_model_contract_v2())

    assert first == second
    assert first["contract_id"] == NETWORK_MODEL_CONTRACT_V2_ID
    assert first["version"] == "v2"
    assert first["fidelity"] == "FLOW_LEVEL_PROXY"
    assert first["packet_level_simulation"] is False
    assert "PACKET_LEVEL_SIMULATION" in first["excluded_capabilities"]
    assert "EXTERNAL_NETWORK_SIMULATOR" in first["excluded_capabilities"]
    assert json.loads(json.dumps(first, sort_keys=True))["contract_id"] == (
        NETWORK_MODEL_CONTRACT_V2_ID
    )


def test_network_model_contract_v2_defines_canonical_layer_boundaries() -> None:
    contract = network_model_contract_v2_to_dict()
    layers = contract["layer_contracts"]
    assert isinstance(layers, tuple)

    assert tuple(layer["layer"] for layer in layers) == (
        NetworkLayer.APPLICATION.value,
        NetworkLayer.TRANSPORT.value,
        NetworkLayer.NETWORK.value,
        NetworkLayer.DATA_LINK.value,
        NetworkLayer.PHYSICAL.value,
        NetworkLayer.CHANNEL.value,
    )
    network_layer = _layer(contract, "NETWORK")
    assert "Route" in network_layer["output_contracts"]
    assert "OrbitBatchState" in network_layer["input_contracts"]
    assert "ALL_PAIRS_LARGE_SCALE_ISL" in network_layer["excluded_semantics"]
    channel_layer = _layer(contract, "CHANNEL")
    assert "network.channel_bandwidth_hz" in channel_layer["state_sources"]
    assert "RF_PROPAGATION_FIELD_SOLVER" in channel_layer["excluded_semantics"]


def test_network_model_contract_v2_defines_kpi_provenance_sources() -> None:
    contract = network_model_contract_v2_to_dict()
    kpis = contract["kpi_contracts"]
    assert isinstance(kpis, tuple)

    assert tuple(kpi["metric"] for kpi in kpis) == tuple(
        sorted(metric.value for metric in NetworkKpiKind)
    )
    throughput = _kpi(contract, "EFFECTIVE_THROUGHPUT")
    assert throughput["runtime_summary_key"] == (
        "network_quality_effective_throughput_mbps"
    )
    assert throughput["unit"] == "Mbps"
    assert "network_quality_estimated_delivered_throughput_mbps" in throughput[
        "source_fields"
    ]
    assert "network_quality_time_adjusted_delivered_throughput_mbps" in throughput[
        "source_fields"
    ]
    assert "network_quality_active_flow_capacity_mbps" in throughput["source_fields"]
    assert (
        "network_quality_time_adjusted_active_throughput_mbps"
        in throughput["source_fields"]
    )
    assert throughput["packet_level_metric"] is False

    loss = _kpi(contract, "EFFECTIVE_LOSS_PROXY")
    assert loss["runtime_summary_key"] == "network_quality_effective_loss_proxy_rate"
    assert "network.transport_loss_rate" in loss["source_fields"]
    assert "network_quality_active_flow_blocking_ratio" in loss["source_fields"]
    assert "network_quality_time_pressure_loss_proxy_rate" in loss["source_fields"]
    assert "packet loss" in loss["interpretation"]

    delay_variation = _kpi(contract, "EFFECTIVE_DELAY_VARIATION_PROXY")
    assert delay_variation["runtime_summary_key"] == (
        "network_quality_effective_delay_variation_proxy_s"
    )
    assert (
        "network_quality_time_pressure_delay_variation_proxy_s"
        in delay_variation["source_fields"]
    )
    assert (
        "network_quality_active_flow_latency_variation_proxy_s"
        in delay_variation["source_fields"]
    )
    assert "not packet inter-arrival jitter" in delay_variation["interpretation"]


def test_backend_summary_exposes_network_model_contract_v2_with_protocol_profile() -> None:
    allocation = AutoPlaneAllocator.allocate(satellite_count=72, plane_count=12)

    summary = build_backend_derived_summary(
        constellation=allocation,
        satellite_count=72,
        user_count=100,
        compute_node_count=72,
        compute_capacity=10.0,
        flow_count=20,
        demand_capacity=25.0,
        task_compute_demand=20.0,
        task_data_size=2.0,
        application_protocol="MQTT",
        transport_protocol="UDP",
        routing_protocol="DISTANCE_VECTOR",
        datalink_mac_protocol="SLOTTED_ALOHA",
    )

    contract = summary["network_model_contract_v2"]
    assert isinstance(contract, dict)
    assert contract["contract_id"] == NETWORK_MODEL_CONTRACT_V2_ID
    assert contract["configured_protocol_profile"] == {
        "application_protocol": "MQTT",
        "transport_protocol": "UDP",
        "routing_protocol": "DISTANCE_VECTOR",
        "datalink_mac_protocol": "SLOTTED_ALOHA",
    }


def _layer(contract: dict[str, object], layer_name: str) -> dict[str, object]:
    layers = contract["layer_contracts"]
    assert isinstance(layers, tuple)
    for layer in layers:
        assert isinstance(layer, dict)
        if layer["layer"] == layer_name:
            return layer
    raise AssertionError(f"missing layer {layer_name}")


def _kpi(contract: dict[str, object], metric: str) -> dict[str, object]:
    kpis = contract["kpi_contracts"]
    assert isinstance(kpis, tuple)
    for kpi in kpis:
        assert isinstance(kpi, dict)
        if kpi["metric"] == metric:
            return kpi
    raise AssertionError(f"missing KPI {metric}")
