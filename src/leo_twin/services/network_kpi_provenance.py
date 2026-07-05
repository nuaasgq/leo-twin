"""Runtime network KPI provenance contract v2."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from leo_twin.schema.network_model_contract import (
    NETWORK_MODEL_CONTRACT_V2_ID,
    network_model_contract_v2_to_dict,
)


NETWORK_KPI_PROVENANCE_V2_ID = "leo_twin.network_kpi_provenance.v2"

NetworkKpiProvenanceV2 = dict[str, object]

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
        "kpi_count": len(kpis),
        "kpis": kpis,
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


__all__ = [
    "NETWORK_KPI_PROVENANCE_V2_ID",
    "NetworkKpiProvenanceV2",
    "build_network_kpi_provenance_v2",
]
