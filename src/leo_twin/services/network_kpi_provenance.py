"""Runtime network KPI provenance contract v2."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from leo_twin.schema.network_model_contract import (
    NETWORK_MODEL_CONTRACT_V2_ID,
    network_model_contract_v2_to_dict,
)


NETWORK_KPI_PROVENANCE_V2_ID = "leo_twin.network_kpi_provenance.v2"
NETWORK_KPI_CREDIBILITY_V1_ID = "leo_twin.network_kpi_credibility.v1"
NETWORK_TEMPORAL_PRESSURE_EVIDENCE_V1_ID = (
    "leo_twin.network_temporal_pressure_evidence.v1"
)

NetworkKpiProvenanceV2 = dict[str, object]
NetworkKpiCredibilityV1 = dict[str, object]
NetworkTemporalPressureEvidenceV1 = dict[str, object]

_SOURCE_KEYS_BY_METRIC = {
    "EFFECTIVE_THROUGHPUT": (
        "network_quality_throughput_source",
        "network_quality_throughput_source_label",
    ),
    "EFFECTIVE_LATENCY": (
        "network_quality_latency_source",
        "network_quality_latency_source_label",
    ),
    "EFFECTIVE_LOSS_PROXY": (
        "network_quality_loss_source",
        "network_quality_loss_source_label",
    ),
    "EFFECTIVE_DELAY_VARIATION_PROXY": (
        "network_quality_delay_variation_source",
        "network_quality_delay_variation_source_label",
    ),
}

_ZERO_REASON_KEYS_BY_METRIC = {
    "EFFECTIVE_LOSS_PROXY": (
        "network_quality_loss_zero_reason",
        "network_quality_loss_zero_reason_label",
    ),
    "EFFECTIVE_DELAY_VARIATION_PROXY": (
        "network_quality_delay_variation_zero_reason",
        "network_quality_delay_variation_zero_reason_label",
    ),
}

_FORMULA_SELECTION_POLICY_BY_METRIC = {
    "CONGESTION_PRESSURE": (
        "Report the current congestion-pressure runtime summary value and "
        "declared link-utilization input."
    ),
    "EFFECTIVE_DELAY_VARIATION_PROXY": (
        "Use the largest available route-spread, completed-flow variation, "
        "active-flow variation, pressure variation, or time-window pressure "
        "variation proxy."
    ),
    "EFFECTIVE_LATENCY": (
        "Prefer completed-flow latency when present; otherwise use active "
        "in-flight flow latency before current available-route latency."
    ),
    "EFFECTIVE_LOSS_PROXY": (
        "Use the maximum available configured, route, failed-flow, congestion, "
        "active-flow blocking, demand, and time-window pressure loss proxy."
    ),
    "EFFECTIVE_THROUGHPUT": (
        "Prefer completed-flow throughput with deterministic pressure context; "
        "otherwise use active in-flight flow throughput before loss-adjusted "
        "available route demand/capacity."
    ),
    "ROUTE_BLOCKING_RATIO": (
        "Report blocked route decisions divided by recent route decisions."
    ),
}

_TEMPORAL_PRESSURE_REQUIRED_FIELDS = (
    "network_quality_time_pressure_period_s",
    "network_quality_time_pressure_phase",
    "network_quality_time_pressure_factor",
)

_TEMPORAL_PRESSURE_FIELDS = (
    "network_quality_time_pressure_period_s",
    "network_quality_time_pressure_phase",
    "network_quality_time_pressure_factor",
    "network_quality_time_pressure_loss_proxy_rate",
    "network_quality_time_pressure_delay_variation_proxy_s",
    "network_quality_demand_pressure_proxy",
    "network_quality_active_flow_pressure_proxy",
    "network_quality_throughput_pressure_proxy",
    "network_quality_congestion_proxy",
    "network_quality_flow_delivered_capacity_mbps",
    "network_quality_time_adjusted_delivered_throughput_mbps",
    "network_quality_active_flow_capacity_mbps",
    "network_quality_time_adjusted_active_throughput_mbps",
)

_TEMPORAL_LOAD_FIELDS = (
    ("demand_pressure", "network_quality_demand_pressure_proxy"),
    ("active_flow_pressure", "network_quality_active_flow_pressure_proxy"),
    ("throughput_pressure", "network_quality_throughput_pressure_proxy"),
    ("link_congestion", "network_quality_congestion_proxy"),
)


_SELECTED_FIELDS_BY_SOURCE = {
    ("EFFECTIVE_THROUGHPUT", "COMPLETED_FLOW_CAPACITY"): (
        "network_quality_estimated_delivered_throughput_mbps",
        "network_quality_time_adjusted_delivered_throughput_mbps",
    ),
    ("EFFECTIVE_THROUGHPUT", "ACTIVE_FLOW_CAPACITY"): (
        "network_quality_active_flow_capacity_mbps",
        "network_quality_time_adjusted_active_throughput_mbps",
    ),
    ("EFFECTIVE_THROUGHPUT", "AVAILABLE_ROUTE_CAPACITY"): (
        "network_quality_estimated_available_throughput_mbps",
        "network_quality_available_route_demand_mbps",
    ),
    ("EFFECTIVE_LATENCY", "COMPLETED_FLOW_LATENCY"): (
        "network_quality_flow_latency_avg_s",
    ),
    ("EFFECTIVE_LATENCY", "ACTIVE_FLOW_LATENCY"): (
        "network_quality_active_flow_latency_avg_s",
    ),
    ("EFFECTIVE_LATENCY", "AVAILABLE_ROUTE_LATENCY"): (
        "network_quality_route_latency_avg_s",
    ),
    ("EFFECTIVE_LOSS_PROXY", "PRESSURE_LOSS_PROXY"): (
        "network_quality_congestion_loss_proxy_rate",
        "network_quality_demand_loss_proxy_rate",
        "network_quality_time_pressure_loss_proxy_rate",
    ),
    ("EFFECTIVE_LOSS_PROXY", "ROUTE_BLOCKING_RATIO"): (
        "network_quality_route_blocking_ratio",
        "network_quality_pressure_admission_rejected_route_count",
        "network_quality_pressure_admission_rejection_ratio",
        "network_quality_topology_blocked_route_count",
    ),
    ("EFFECTIVE_LOSS_PROXY", "FAILED_FLOW_RATIO"): (
        "network_quality_failed_flow_ratio",
    ),
    ("EFFECTIVE_LOSS_PROXY", "ACTIVE_FLOW_BLOCKING_RATIO"): (
        "network_quality_active_flow_blocking_ratio",
    ),
    ("EFFECTIVE_DELAY_VARIATION_PROXY", "FLOW_LATENCY_VARIATION"): (
        "network_quality_flow_latency_variation_proxy_s",
    ),
    ("EFFECTIVE_DELAY_VARIATION_PROXY", "ACTIVE_FLOW_LATENCY_VARIATION"): (
        "network_quality_active_flow_latency_variation_proxy_s",
    ),
    ("EFFECTIVE_DELAY_VARIATION_PROXY", "ROUTE_LATENCY_SPREAD"): (
        "network_quality_delay_variation_proxy_s",
    ),
    ("EFFECTIVE_DELAY_VARIATION_PROXY", "PRESSURE_DELAY_VARIATION"): (
        "network_quality_pressure_delay_variation_proxy_s",
        "network_quality_time_pressure_delay_variation_proxy_s",
    ),
    ("ROUTE_BLOCKING_RATIO", "RUNTIME_SUMMARY_KEY"): (
        "network_quality_route_decision_count",
        "network_quality_available_route_decision_count",
        "network_quality_unavailable_route_decision_count",
        "network_quality_pressure_admission_rejected_route_count",
        "network_quality_topology_blocked_route_count",
    ),
}


def build_network_kpi_provenance_v2(
    metrics: Mapping[str, Any],
    *,
    network_model_contract: Mapping[str, Any] | None = None,
) -> NetworkKpiProvenanceV2:
    """Build deterministic runtime KPI provenance from backend metrics."""

    if not isinstance(metrics, Mapping):
        raise TypeError("metrics must be a mapping")
    contract = (
        network_model_contract_v2_to_dict()
        if network_model_contract is None
        else dict(network_model_contract)
    )
    kpi_contracts = tuple(_records(contract.get("kpi_contracts")))
    kpis = tuple(_kpi_provenance_item(kpi, metrics) for kpi in kpi_contracts)
    return {
        "version": "v2",
        "provenance_id": NETWORK_KPI_PROVENANCE_V2_ID,
        "source": "BACKEND_METRICS_SUMMARY",
        "network_model_contract_id": str(
            contract.get("contract_id", NETWORK_MODEL_CONTRACT_V2_ID)
        ),
        "network_model_contract_version": str(contract.get("version", "v2")),
        "metric_model": _metric_string(metrics, "network_quality_metric_model")
        or str(contract.get("fidelity", "FLOW_LEVEL_PROXY")),
        "packet_level_simulation": False,
        "proxy_note": _metric_string(metrics, "network_quality_proxy_note"),
        "provenance_note": _metric_string(metrics, "network_quality_provenance_note"),
        "temporal_pressure_evidence": _temporal_pressure_evidence(metrics),
        "kpi_count": len(kpis),
        "kpis": kpis,
    }


def build_network_kpi_credibility_v1(
    provenance: Mapping[str, Any],
) -> NetworkKpiCredibilityV1:
    """Summarize KPI provenance coverage for product-facing trust reporting."""

    if not isinstance(provenance, Mapping):
        raise TypeError("provenance must be a mapping")
    kpis = tuple(_records(provenance.get("kpis")))
    observed = tuple(item for item in kpis if item.get("status") == "OBSERVED")
    missing = tuple(item for item in kpis if item.get("status") != "OBSERVED")
    packet_level_metrics = tuple(
        item for item in kpis if item.get("packet_level_metric") is True
    )
    zero_value_kpis = tuple(
        item for item in kpis if _is_zero_value(item.get("current_value"))
    )
    zero_value_explained = tuple(
        item for item in zero_value_kpis if _has_zero_explanation(item)
    )
    source_field_records = tuple(
        field
        for item in kpis
        for field in _records(item.get("source_fields"))
    )
    observed_source_fields = tuple(
        field
        for field in source_field_records
        if field.get("value_source") == "METRICS_SUMMARY"
    )
    missing_source_fields = tuple(
        field
        for field in source_field_records
        if field.get("value_source") != "METRICS_SUMMARY"
    )
    packet_level_simulation = provenance.get("packet_level_simulation") is True
    credibility_status = _credibility_status(
        kpi_count=len(kpis),
        observed_count=len(observed),
        missing_count=len(missing),
        packet_level_metric_count=len(packet_level_metrics),
        packet_level_simulation=packet_level_simulation,
    )
    zero_unexplained_metrics = tuple(
        str(item.get("metric", ""))
        for item in zero_value_kpis
        if not _has_zero_explanation(item)
    )
    return {
        "version": "v1",
        "credibility_id": NETWORK_KPI_CREDIBILITY_V1_ID,
        "source": "NETWORK_KPI_PROVENANCE_V2",
        "provenance_id": str(provenance.get("provenance_id", "")),
        "metric_model": str(provenance.get("metric_model", "")),
        "packet_level_simulation": packet_level_simulation,
        "credibility_status": credibility_status,
        "kpi_count": len(kpis),
        "observed_kpi_count": len(observed),
        "missing_kpi_count": len(missing),
        "packet_level_metric_count": len(packet_level_metrics),
        "flow_level_proxy_metric_count": len(kpis) - len(packet_level_metrics),
        "zero_value_kpi_count": len(zero_value_kpis),
        "zero_value_explained_count": len(zero_value_explained),
        "source_field_count": len(source_field_records),
        "observed_source_field_count": len(observed_source_fields),
        "missing_source_field_count": len(missing_source_fields),
        "missing_metrics": tuple(str(item.get("metric", "")) for item in missing),
        "zero_unexplained_metrics": zero_unexplained_metrics,
        "caveats": _credibility_caveats(
            credibility_status,
            missing_count=len(missing),
            packet_level_metric_count=len(packet_level_metrics),
            packet_level_simulation=packet_level_simulation,
            zero_unexplained_count=len(zero_unexplained_metrics),
        ),
    }


def _temporal_pressure_evidence(
    metrics: Mapping[str, Any],
) -> NetworkTemporalPressureEvidenceV1:
    observed_required_count = sum(
        1 for field in _TEMPORAL_PRESSURE_REQUIRED_FIELDS if field in metrics
    )
    status = (
        "OBSERVED"
        if observed_required_count == len(_TEMPORAL_PRESSURE_REQUIRED_FIELDS)
        else "MISSING_RUNTIME_VALUES"
    )
    dominant_load = _dominant_temporal_load_component(metrics)
    time_pressure_factor = _metric_number(
        metrics,
        "network_quality_time_pressure_factor",
    ) or 0.0
    loss_proxy_rate = _metric_number(
        metrics,
        "network_quality_time_pressure_loss_proxy_rate",
    ) or 0.0
    delay_variation_proxy_s = _metric_number(
        metrics,
        "network_quality_time_pressure_delay_variation_proxy_s",
    ) or 0.0
    delivered_throughput = _metric_number(
        metrics,
        "network_quality_flow_delivered_capacity_mbps",
    ) or 0.0
    adjusted_throughput = _metric_number(
        metrics,
        "network_quality_time_adjusted_delivered_throughput_mbps",
    ) or 0.0
    throughput_delta = max(0.0, delivered_throughput - adjusted_throughput)
    return {
        "version": "v1",
        "evidence_id": NETWORK_TEMPORAL_PRESSURE_EVIDENCE_V1_ID,
        "source": "METRICS_SUMMARY",
        "metric_model": _metric_string(metrics, "network_quality_metric_model")
        or "FLOW_LEVEL_PROXY",
        "temporal_pressure_model": "DETERMINISTIC_TRIANGULAR_LOAD_GATED_PROXY",
        "packet_level_simulation": False,
        "frontend_inference_required": False,
        "status": status,
        "required_field_count": len(_TEMPORAL_PRESSURE_REQUIRED_FIELDS),
        "observed_required_field_count": observed_required_count,
        "source_field_count": len(_TEMPORAL_PRESSURE_FIELDS),
        "time_pressure_period_s": _metric_value(
            metrics,
            "network_quality_time_pressure_period_s",
        ),
        "time_pressure_phase": _metric_value(
            metrics,
            "network_quality_time_pressure_phase",
        ),
        "time_pressure_factor": _metric_value(
            metrics,
            "network_quality_time_pressure_factor",
        ),
        "dominant_load_component": dominant_load,
        "load_pressure_proxy": dominant_load["current_value"],
        "loss_proxy_rate": float(loss_proxy_rate),
        "delay_variation_proxy_s": float(delay_variation_proxy_s),
        "temporal_pressure_active": time_pressure_factor > 0.0,
        "loss_proxy_active": loss_proxy_rate > 0.0,
        "delay_variation_proxy_active": delay_variation_proxy_s > 0.0,
        "delivered_throughput_mbps": float(delivered_throughput),
        "time_adjusted_delivered_throughput_mbps": float(adjusted_throughput),
        "throughput_delta_mbps": float(throughput_delta),
        "source_fields": tuple(
            _source_field_value(field, metrics)
            for field in _TEMPORAL_PRESSURE_FIELDS
        ),
        "model_assumptions": (
            "Temporal pressure is a deterministic load-gated flow-level proxy.",
            "No packet-level queue or packet-loss simulation is performed.",
            "The pressure factor explains KPI movement over simulation time when load inputs are non-zero.",
        ),
    }


def _dominant_temporal_load_component(
    metrics: Mapping[str, Any],
) -> dict[str, object]:
    selected_name = "none"
    selected_field = ""
    selected_value = 0.0
    selected_source = "MISSING"
    for name, field in _TEMPORAL_LOAD_FIELDS:
        value = _metric_number(metrics, field)
        candidate_value = 0.0 if value is None else value
        if selected_field == "" or candidate_value > selected_value:
            selected_name = name
            selected_field = field
            selected_value = candidate_value
            selected_source = "METRICS_SUMMARY" if value is not None else "MISSING"
    return {
        "component": selected_name,
        "field": selected_field,
        "current_value": float(selected_value),
        "value_source": selected_source,
    }



def _kpi_provenance_item(
    kpi_contract: Mapping[str, Any],
    metrics: Mapping[str, Any],
) -> dict[str, object]:
    metric = str(kpi_contract.get("metric", ""))
    runtime_key = str(kpi_contract.get("runtime_summary_key", ""))
    source_fields = tuple(str(field) for field in _values(kpi_contract.get("source_fields")))
    current_value = _metric_value(metrics, runtime_key)
    observed_source = _observed_source(metric, metrics)
    zero_reason = _zero_reason(metric, metrics)
    formula_inputs = tuple(
        _formula_input_value(field, metric, observed_source, metrics)
        for field in source_fields
    )
    return {
        "metric": metric,
        "runtime_summary_key": runtime_key,
        "current_value": current_value,
        "status": "OBSERVED" if runtime_key in metrics else "MISSING_RUNTIME_VALUE",
        "display_name": str(kpi_contract.get("display_name", "")),
        "layer": str(kpi_contract.get("layer", "")),
        "unit": str(kpi_contract.get("unit", "")),
        "formula_summary": str(kpi_contract.get("formula_summary", "")),
        "interpretation": str(kpi_contract.get("interpretation", "")),
        "zero_value_semantics": str(kpi_contract.get("zero_value_semantics", "")),
        "packet_level_metric": False,
        "observed_source": observed_source,
        "zero_reason": zero_reason,
        "source_fields": tuple(
            _source_field_value(field, metrics)
            for field in source_fields
        ),
        "formula_inputs": formula_inputs,
        "formula_trace": _formula_trace(
            metric=metric,
            runtime_key=runtime_key,
            current_value=current_value,
            observed_source=observed_source,
            source_fields=source_fields,
            formula_inputs=formula_inputs,
            runtime_value_observed=runtime_key in metrics,
        ),
    }


def _source_field_value(field: str, metrics: Mapping[str, Any]) -> dict[str, object]:
    if field in metrics:
        return {
            "field": field,
            "current_value": _metric_value(metrics, field),
            "value_source": "METRICS_SUMMARY",
        }
    return {
        "field": field,
        "current_value": None,
        "value_source": "MODEL_OR_CONFIG_STATE",
    }


def _formula_input_value(
    field: str,
    metric: str,
    observed_source: Mapping[str, str],
    metrics: Mapping[str, Any],
) -> dict[str, object]:
    value_source = "METRICS_SUMMARY" if field in metrics else "MODEL_OR_CONFIG_STATE"
    selected_fields = _selected_fields(metric, observed_source)
    selected = field in selected_fields
    observed = value_source == "METRICS_SUMMARY"
    if selected and observed:
        role = "SELECTED_RUNTIME_INPUT"
        reason = (
            f"selected by observed_source={observed_source.get('source', '')} "
            "and observed in metrics_summary"
        )
    elif selected:
        role = "SELECTED_DECLARED_INPUT"
        reason = (
            f"selected by observed_source={observed_source.get('source', '')} "
            "but current value is not exposed in metrics_summary"
        )
    elif observed:
        role = "OBSERVED_SUPPORTING_INPUT"
        reason = "observed supporting formula input from metrics_summary"
    else:
        role = "DECLARED_SUPPORTING_INPUT"
        reason = "declared by network model contract; current runtime value is not exposed"
    return {
        "field": field,
        "current_value": _metric_value(metrics, field),
        "value_source": value_source,
        "observed": observed,
        "selected_for_current_value": selected,
        "role": role,
        "selection_reason": reason,
    }


def _formula_trace(
    *,
    metric: str,
    runtime_key: str,
    current_value: object,
    observed_source: Mapping[str, str],
    source_fields: tuple[str, ...],
    formula_inputs: tuple[Mapping[str, Any], ...],
    runtime_value_observed: bool,
) -> dict[str, object]:
    selected_fields = _selected_fields(metric, observed_source)
    observed_inputs = tuple(
        item for item in formula_inputs if item.get("observed") is True
    )
    selected_inputs = tuple(
        item for item in formula_inputs if item.get("selected_for_current_value") is True
    )
    selected_observed_inputs = tuple(
        item
        for item in selected_inputs
        if item.get("observed") is True
    )
    return {
        "selection_policy": _FORMULA_SELECTION_POLICY_BY_METRIC.get(
            metric,
            "Use the runtime summary key declared by the network model contract.",
        ),
        "runtime_summary_key": runtime_key,
        "runtime_value_observed": runtime_value_observed,
        "current_value": current_value,
        "observed_source": str(observed_source.get("source", "")),
        "observed_source_label": str(observed_source.get("label", "")),
        "declared_input_count": len(source_fields),
        "observed_input_count": len(observed_inputs),
        "selected_input_count": len(selected_inputs),
        "selected_observed_input_count": len(selected_observed_inputs),
        "missing_input_count": max(0, len(source_fields) - len(observed_inputs)),
        "selected_source_fields": selected_fields,
    }


def _selected_fields(
    metric: str,
    observed_source: Mapping[str, str],
) -> tuple[str, ...]:
    source = str(observed_source.get("source", ""))
    return _SELECTED_FIELDS_BY_SOURCE.get((metric, source), ())


def _observed_source(metric: str, metrics: Mapping[str, Any]) -> dict[str, str]:
    keys = _SOURCE_KEYS_BY_METRIC.get(metric)
    if keys is None:
        return {
            "source": "RUNTIME_SUMMARY_KEY",
            "label": "Runtime summary field",
        }
    source_key, label_key = keys
    return {
        "source": _metric_string(metrics, source_key),
        "label": _metric_string(metrics, label_key),
    }


def _zero_reason(metric: str, metrics: Mapping[str, Any]) -> dict[str, str] | None:
    keys = _ZERO_REASON_KEYS_BY_METRIC.get(metric)
    if keys is None:
        return None
    reason_key, label_key = keys
    return {
        "reason": _metric_string(metrics, reason_key),
        "label": _metric_string(metrics, label_key),
    }


def _records(value: object) -> tuple[Mapping[str, Any], ...]:
    if not isinstance(value, (list, tuple)):
        return ()
    return tuple(item for item in value if isinstance(item, Mapping))


def _values(value: object) -> tuple[object, ...]:
    if not isinstance(value, (list, tuple)):
        return ()
    return tuple(value)


def _metric_string(metrics: Mapping[str, Any], key: str) -> str:
    value = metrics.get(key)
    return value if isinstance(value, str) else ""


def _metric_value(metrics: Mapping[str, Any], key: str) -> str | int | float | bool | None:
    value = metrics.get(key)
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float, str)):
        return value
    return None


def _metric_number(metrics: Mapping[str, Any], key: str) -> float | None:
    value = metrics.get(key)
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _is_zero_value(value: object) -> bool:
    return (
        not isinstance(value, bool)
        and isinstance(value, (int, float))
        and float(value) == 0.0
    )


def _has_zero_explanation(item: Mapping[str, Any]) -> bool:
    zero_reason = item.get("zero_reason")
    if isinstance(zero_reason, Mapping) and str(zero_reason.get("reason", "")):
        return True
    return bool(str(item.get("zero_value_semantics", "")))


def _credibility_status(
    *,
    kpi_count: int,
    observed_count: int,
    missing_count: int,
    packet_level_metric_count: int,
    packet_level_simulation: bool,
) -> str:
    if packet_level_simulation or packet_level_metric_count > 0:
        return "INVALID_PACKET_LEVEL_METRIC"
    if kpi_count == 0 or observed_count == 0:
        return "MISSING_RUNTIME_VALUES"
    if missing_count > 0:
        return "PARTIAL_RUNTIME_VALUES"
    return "COMPLETE_FLOW_LEVEL_PROXY"


def _credibility_caveats(
    credibility_status: str,
    *,
    missing_count: int,
    packet_level_metric_count: int,
    packet_level_simulation: bool,
    zero_unexplained_count: int,
) -> tuple[str, ...]:
    caveats = [
        (
            "Network KPI values are deterministic flow-level proxies, "
            "not packet-level measurements."
        )
    ]
    if missing_count > 0:
        caveats.append(f"{missing_count} KPI runtime values are missing from metrics_summary.")
    if packet_level_simulation or packet_level_metric_count > 0:
        caveats.append("Packet-level network metrics are outside the current product contract.")
    if zero_unexplained_count > 0:
        caveats.append(f"{zero_unexplained_count} zero-valued KPI entries lack explicit zero reasons.")
    caveats.append(f"credibility_status={credibility_status}")
    return tuple(caveats)


__all__ = [
    "NETWORK_KPI_CREDIBILITY_V1_ID",
    "NETWORK_KPI_PROVENANCE_V2_ID",
    "NETWORK_TEMPORAL_PRESSURE_EVIDENCE_V1_ID",
    "NetworkKpiCredibilityV1",
    "NetworkKpiProvenanceV2",
    "NetworkTemporalPressureEvidenceV1",
    "build_network_kpi_credibility_v1",
    "build_network_kpi_provenance_v2",
]
