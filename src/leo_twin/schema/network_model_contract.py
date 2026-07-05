"""Product-level network model contract v2."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from leo_twin.schema.full_system import NetworkLayer


NETWORK_MODEL_CONTRACT_V2_ID = "leo_twin.network_model_contract.v2"


class NetworkModelFidelity(StrEnum):
    """Network fidelity modes described by the product contract."""

    FLOW_LEVEL_PROXY = "FLOW_LEVEL_PROXY"


class NetworkKpiKind(StrEnum):
    """Network KPI names that must be explainable to users."""

    EFFECTIVE_THROUGHPUT = "EFFECTIVE_THROUGHPUT"
    EFFECTIVE_LATENCY = "EFFECTIVE_LATENCY"
    EFFECTIVE_LOSS_PROXY = "EFFECTIVE_LOSS_PROXY"
    EFFECTIVE_DELAY_VARIATION_PROXY = "EFFECTIVE_DELAY_VARIATION_PROXY"
    ROUTE_BLOCKING_RATIO = "ROUTE_BLOCKING_RATIO"
    CONGESTION_PRESSURE = "CONGESTION_PRESSURE"


@dataclass(frozen=True)
class NetworkLayerSemanticContract:
    """Semantic boundary for one layer in the SEES flow-level network model."""

    layer: NetworkLayer
    product_name: str
    responsibility: str
    input_contracts: tuple[str, ...]
    output_contracts: tuple[str, ...]
    state_sources: tuple[str, ...] = ()
    excluded_semantics: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.layer, NetworkLayer):
            object.__setattr__(self, "layer", NetworkLayer(str(self.layer)))
        _require_non_empty_str(self.product_name, "product_name")
        _require_non_empty_str(self.responsibility, "responsibility")
        object.__setattr__(
            self,
            "input_contracts",
            _normalize_str_tuple(self.input_contracts, "input_contracts"),
        )
        object.__setattr__(
            self,
            "output_contracts",
            _normalize_str_tuple(self.output_contracts, "output_contracts"),
        )
        object.__setattr__(
            self,
            "state_sources",
            _normalize_str_tuple(self.state_sources, "state_sources"),
        )
        object.__setattr__(
            self,
            "excluded_semantics",
            _normalize_str_tuple(self.excluded_semantics, "excluded_semantics"),
        )

    def to_dict(self) -> dict[str, object]:
        """Return deterministic JSON-compatible layer semantics."""

        return {
            "layer": self.layer.value,
            "product_name": self.product_name,
            "responsibility": self.responsibility,
            "input_contracts": self.input_contracts,
            "output_contracts": self.output_contracts,
            "state_sources": self.state_sources,
            "excluded_semantics": self.excluded_semantics,
        }


@dataclass(frozen=True)
class NetworkKpiSemanticContract:
    """Source and formula contract for one network KPI."""

    metric: NetworkKpiKind
    runtime_summary_key: str
    display_name: str
    layer: NetworkLayer
    unit: str
    source_fields: tuple[str, ...]
    formula_summary: str
    interpretation: str
    zero_value_semantics: str = ""
    packet_level_metric: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.metric, NetworkKpiKind):
            object.__setattr__(self, "metric", NetworkKpiKind(str(self.metric)))
        if not isinstance(self.layer, NetworkLayer):
            object.__setattr__(self, "layer", NetworkLayer(str(self.layer)))
        _require_non_empty_str(self.runtime_summary_key, "runtime_summary_key")
        _require_non_empty_str(self.display_name, "display_name")
        _require_non_empty_str(self.unit, "unit")
        _require_non_empty_str(self.formula_summary, "formula_summary")
        _require_non_empty_str(self.interpretation, "interpretation")
        object.__setattr__(
            self,
            "source_fields",
            _normalize_str_tuple(self.source_fields, "source_fields"),
        )
        if not isinstance(self.packet_level_metric, bool):
            raise TypeError("packet_level_metric must be a bool")

    def to_dict(self) -> dict[str, object]:
        """Return deterministic JSON-compatible KPI semantics."""

        return {
            "metric": self.metric.value,
            "runtime_summary_key": self.runtime_summary_key,
            "display_name": self.display_name,
            "layer": self.layer.value,
            "unit": self.unit,
            "source_fields": self.source_fields,
            "formula_summary": self.formula_summary,
            "interpretation": self.interpretation,
            "zero_value_semantics": self.zero_value_semantics,
            "packet_level_metric": self.packet_level_metric,
        }


@dataclass(frozen=True)
class NetworkModelContractV2:
    """Versioned product contract for network semantics and KPI provenance."""

    contract_id: str
    version: str
    fidelity: NetworkModelFidelity
    layer_contracts: tuple[NetworkLayerSemanticContract, ...]
    kpi_contracts: tuple[NetworkKpiSemanticContract, ...]
    event_inputs: tuple[str, ...]
    deterministic_inputs: tuple[str, ...]
    excluded_capabilities: tuple[str, ...]
    model_note: str

    def __post_init__(self) -> None:
        _require_non_empty_str(self.contract_id, "contract_id")
        _require_non_empty_str(self.version, "version")
        if not isinstance(self.fidelity, NetworkModelFidelity):
            object.__setattr__(self, "fidelity", NetworkModelFidelity(str(self.fidelity)))
        if not self.layer_contracts:
            raise ValueError("layer_contracts must not be empty")
        if not self.kpi_contracts:
            raise ValueError("kpi_contracts must not be empty")
        layer_order = tuple(contract.layer for contract in self.layer_contracts)
        if layer_order != _NETWORK_LAYER_ORDER:
            raise ValueError("layer_contracts must follow canonical network layer order")
        metric_order = tuple(contract.metric for contract in self.kpi_contracts)
        if metric_order != tuple(sorted(metric_order, key=lambda item: item.value)):
            raise ValueError("kpi_contracts must be ordered by metric name")
        object.__setattr__(
            self,
            "event_inputs",
            _normalize_str_tuple(self.event_inputs, "event_inputs"),
        )
        object.__setattr__(
            self,
            "deterministic_inputs",
            _normalize_str_tuple(self.deterministic_inputs, "deterministic_inputs"),
        )
        object.__setattr__(
            self,
            "excluded_capabilities",
            _normalize_str_tuple(self.excluded_capabilities, "excluded_capabilities"),
        )
        _require_non_empty_str(self.model_note, "model_note")

    def to_dict(self) -> dict[str, object]:
        """Return deterministic JSON-compatible network model contract."""

        return {
            "contract_id": self.contract_id,
            "version": self.version,
            "fidelity": self.fidelity.value,
            "packet_level_simulation": False,
            "layer_contracts": tuple(layer.to_dict() for layer in self.layer_contracts),
            "kpi_contracts": tuple(kpi.to_dict() for kpi in self.kpi_contracts),
            "event_inputs": self.event_inputs,
            "deterministic_inputs": self.deterministic_inputs,
            "excluded_capabilities": self.excluded_capabilities,
            "model_note": self.model_note,
        }


def default_network_model_contract_v2() -> NetworkModelContractV2:
    """Build the default SEES product network model contract v2."""

    return NetworkModelContractV2(
        contract_id=NETWORK_MODEL_CONTRACT_V2_ID,
        version="v2",
        fidelity=NetworkModelFidelity.FLOW_LEVEL_PROXY,
        layer_contracts=_default_layer_contracts(),
        kpi_contracts=_default_kpi_contracts(),
        event_inputs=(
            "ACCESS_START",
            "ACCESS_END",
            "LINK_UPDATE",
            "ROUTE_UPDATE",
            "FLOW_COMPLETE",
            "METRIC_SAMPLE",
        ),
        deterministic_inputs=(
            "runtime.seed",
            "scenario.traffic_model",
            "network.transport_loss_rate",
            "network.transport_congestion_window_segments",
            "network.routing_latency_weight",
            "network.routing_inverse_capacity_weight",
            "network.routing_hop_weight",
            "network.space_link_mode",
            "network.max_space_link_candidates_per_satellite",
        ),
        excluded_capabilities=(
            "PACKET_LEVEL_SIMULATION",
            "EXTERNAL_NETWORK_SIMULATOR",
            "RF_PROPAGATION",
            "ANTENNA_PATTERN",
            "RETRANSMISSION_PROTOCOL_EMULATION",
            "STOCHASTIC_UNSEEDED_LOSS",
        ),
        model_note=(
            "SEES network v2 is a deterministic flow-level layered abstraction. "
            "It explains KPI provenance but does not emulate packets or external "
            "network simulators."
        ),
    )


def network_model_contract_v2_to_dict(
    contract: NetworkModelContractV2 | None = None,
) -> dict[str, object]:
    """Return the default or supplied network contract as JSON-compatible data."""

    selected = default_network_model_contract_v2() if contract is None else contract
    if not isinstance(selected, NetworkModelContractV2):
        raise TypeError("contract must be NetworkModelContractV2 or None")
    return selected.to_dict()


def _default_layer_contracts() -> tuple[NetworkLayerSemanticContract, ...]:
    return (
        NetworkLayerSemanticContract(
            layer=NetworkLayer.APPLICATION,
            product_name="Application demand layer",
            responsibility=(
                "Convert user service intent into flow-level demand and optional "
                "compute-service metadata."
            ),
            input_contracts=("TaskRequest", "TrafficDemandRecord", "UserServiceIntent"),
            output_contracts=("FlowRequest", "TaskRequestMetadata"),
            state_sources=("scenario.traffic_model", "traffic_demand_summary"),
            excluded_semantics=("HTTP_OBJECT_TIMING", "MQTT_BROKER_STATE"),
        ),
        NetworkLayerSemanticContract(
            layer=NetworkLayer.TRANSPORT,
            product_name="Transport abstraction layer",
            responsibility=(
                "Apply flow-level transport overhead, configured loss proxy input, "
                "and congestion-window constraints."
            ),
            input_contracts=("FlowRequest", "Route"),
            output_contracts=("TransportState", "RouteWithTransportEffects"),
            state_sources=(
                "network.transport_protocol",
                "network.transport_loss_rate",
                "network.transport_congestion_window_segments",
            ),
            excluded_semantics=("PACKET_RETRANSMISSION", "TCP_STATE_MACHINE"),
        ),
        NetworkLayerSemanticContract(
            layer=NetworkLayer.NETWORK,
            product_name="Routing and topology layer",
            responsibility=(
                "Select deterministic flow routes over the current access and "
                "space-link graph."
            ),
            input_contracts=("LinkState", "FlowRequest", "OrbitBatchState"),
            output_contracts=("Route", "RouteState"),
            state_sources=(
                "ACCESS_START",
                "ACCESS_END",
                "LINK_UPDATE",
                "ROUTE_UPDATE",
            ),
            excluded_semantics=("ALL_PAIRS_LARGE_SCALE_ISL", "QUEUE_DISCIPLINE_EMULATION"),
        ),
        NetworkLayerSemanticContract(
            layer=NetworkLayer.DATA_LINK,
            product_name="Data-link flow layer",
            responsibility=(
                "Apply deterministic MAC profile effects to route capacity, "
                "latency, and contention proxies."
            ),
            input_contracts=("Route", "DataLinkProfile"),
            output_contracts=("LinkState", "RouteWithDataLinkEffects"),
            state_sources=("network.datalink_mac_protocol", "LinkState.utilization"),
            excluded_semantics=("FRAME_LEVEL_SCHEDULING", "COLLISION_SIMULATION"),
        ),
        NetworkLayerSemanticContract(
            layer=NetworkLayer.PHYSICAL,
            product_name="Physical terminal abstraction layer",
            responsibility=(
                "Expose configured terminal and link-budget inputs as deterministic "
                "capacity and delay factors."
            ),
            input_contracts=("AntennaProfile", "RadioTerminalProfile", "LinkState"),
            output_contracts=("PhysicalLinkProfile",),
            state_sources=(
                "network.antenna_diameter_m",
                "network.antenna_aperture_efficiency",
                "network.transmit_power_dbw",
                "network.system_loss_db",
            ),
            excluded_semantics=("ANTENNA_PATTERN", "POINTING_CONTROL_LOOP"),
        ),
        NetworkLayerSemanticContract(
            layer=NetworkLayer.CHANNEL,
            product_name="Channel abstraction layer",
            responsibility=(
                "Convert configured channel bandwidth, range, and rain inputs into "
                "flow-level capacity and delay proxies."
            ),
            input_contracts=("ChannelProfile", "LinkBudgetResult"),
            output_contracts=("ChannelState", "LinkState"),
            state_sources=(
                "network.carrier_frequency_hz",
                "network.channel_bandwidth_hz",
                "network.rain_rate_mm_h",
                "network.rain_effective_path_km",
            ),
            excluded_semantics=("RF_PROPAGATION_FIELD_SOLVER", "INTERFERENCE_MODEL"),
        ),
    )


def _default_kpi_contracts() -> tuple[NetworkKpiSemanticContract, ...]:
    contracts = (
        NetworkKpiSemanticContract(
            metric=NetworkKpiKind.CONGESTION_PRESSURE,
            runtime_summary_key="network_quality_congestion_proxy",
            display_name="Congestion pressure proxy",
            layer=NetworkLayer.DATA_LINK,
            unit="ratio",
            source_fields=("LinkState.utilization",),
            formula_summary=(
                "Maximum recent active-link utilization above nominal pressure threshold."
            ),
            interpretation=(
                "Higher values mean recent link utilization is near capacity in the "
                "flow-level abstraction."
            ),
            zero_value_semantics="No active link pressure above threshold.",
        ),
        NetworkKpiSemanticContract(
            metric=NetworkKpiKind.EFFECTIVE_DELAY_VARIATION_PROXY,
            runtime_summary_key="network_quality_effective_delay_variation_proxy_s",
            display_name="Effective delay-variation proxy",
            layer=NetworkLayer.NETWORK,
            unit="s",
            source_fields=(
                "network_quality_delay_variation_proxy_s",
                "network_quality_flow_latency_variation_proxy_s",
                "network_quality_pressure_delay_variation_proxy_s",
                "network_quality_time_pressure_delay_variation_proxy_s",
            ),
            formula_summary=(
                "Maximum of route latency spread, recent flow latency variation, "
                "pressure-driven delay variation proxy, and deterministic time-window "
                "pressure variation."
            ),
            interpretation=(
                "Represents flow-level delay variation for dashboard trend analysis, "
                "not packet inter-arrival jitter."
            ),
            zero_value_semantics=(
                "No route latency spread, no recent flow latency variation, and no "
                "pressure-driven delay variation."
            ),
        ),
        NetworkKpiSemanticContract(
            metric=NetworkKpiKind.EFFECTIVE_LATENCY,
            runtime_summary_key="network_quality_effective_latency_avg_s",
            display_name="Effective latency",
            layer=NetworkLayer.NETWORK,
            unit="s",
            source_fields=(
                "Route.latency",
                "network_quality_route_latency_avg_s",
                "network_quality_flow_latency_avg_s",
            ),
            formula_summary=(
                "Prefer recent completed-flow latency when available; otherwise use "
                "current available-route average latency."
            ),
            interpretation="Average flow-level latency available to dashboard users.",
            zero_value_semantics="No available route or completed-flow latency sample.",
        ),
        NetworkKpiSemanticContract(
            metric=NetworkKpiKind.EFFECTIVE_LOSS_PROXY,
            runtime_summary_key="network_quality_effective_loss_proxy_rate",
            display_name="Effective loss proxy",
            layer=NetworkLayer.TRANSPORT,
            unit="ratio",
            source_fields=(
                "network.transport_loss_rate",
                "network_quality_route_blocking_ratio",
                "network_quality_failed_flow_ratio",
                "network_quality_congestion_loss_proxy_rate",
                "network_quality_demand_loss_proxy_rate",
                "network_quality_time_pressure_loss_proxy_rate",
            ),
            formula_summary=(
                "Maximum of configured transport loss proxy, route blocking, failed "
                "flow ratio, congestion pressure loss, demand pressure loss, and "
                "deterministic time-window pressure loss."
            ),
            interpretation=(
                "Flow-level loss/quality degradation proxy. It must not be read as "
                "packet loss."
            ),
            zero_value_semantics=(
                "No configured loss, no blocked routes, no failed flows, and no "
                "pressure-driven loss."
            ),
        ),
        NetworkKpiSemanticContract(
            metric=NetworkKpiKind.EFFECTIVE_THROUGHPUT,
            runtime_summary_key="network_quality_effective_throughput_mbps",
            display_name="Effective throughput",
            layer=NetworkLayer.NETWORK,
            unit="Mbps",
            source_fields=(
                "network_quality_estimated_delivered_throughput_mbps",
                "network_quality_time_adjusted_delivered_throughput_mbps",
                "network_quality_estimated_available_throughput_mbps",
                "network_quality_available_route_demand_mbps",
            ),
            formula_summary=(
                "Prefer completed-flow throughput adjusted by deterministic time-window "
                "pressure; fall back to loss-adjusted available route demand/capacity."
            ),
            interpretation=(
                "Flow-level carried or currently supportable throughput estimate for "
                "trend analysis."
            ),
            zero_value_semantics="No completed flow and no available route demand/capacity.",
        ),
        NetworkKpiSemanticContract(
            metric=NetworkKpiKind.ROUTE_BLOCKING_RATIO,
            runtime_summary_key="network_quality_route_blocking_ratio",
            display_name="Route blocking ratio",
            layer=NetworkLayer.NETWORK,
            unit="ratio",
            source_fields=("Route.available", "Route.demand_capacity", "Route.capacity"),
            formula_summary="Unavailable routes divided by all recent route decisions.",
            interpretation="Fraction of recent flow routes blocked by topology or capacity.",
            zero_value_semantics="No recent route decision is blocked.",
        ),
    )
    return tuple(sorted(contracts, key=lambda contract: contract.metric.value))


_NETWORK_LAYER_ORDER = (
    NetworkLayer.APPLICATION,
    NetworkLayer.TRANSPORT,
    NetworkLayer.NETWORK,
    NetworkLayer.DATA_LINK,
    NetworkLayer.PHYSICAL,
    NetworkLayer.CHANNEL,
)


def _normalize_str_tuple(values: tuple[str, ...], field_name: str) -> tuple[str, ...]:
    if not isinstance(values, tuple):
        raise TypeError(f"{field_name} must be a tuple")
    normalized = tuple(str(value) for value in values)
    if any(not value for value in normalized):
        raise ValueError(f"{field_name} must not contain empty values")
    return normalized


def _require_non_empty_str(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value:
        raise TypeError(f"{field_name} must be a non-empty str")


__all__ = [
    "NETWORK_MODEL_CONTRACT_V2_ID",
    "NetworkKpiKind",
    "NetworkKpiSemanticContract",
    "NetworkLayerSemanticContract",
    "NetworkModelContractV2",
    "NetworkModelFidelity",
    "default_network_model_contract_v2",
    "network_model_contract_v2_to_dict",
]
