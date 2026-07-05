from __future__ import annotations

import json

from leo_twin.services.network_kpi_provenance import (
    NETWORK_KPI_PROVENANCE_V2_ID,
    build_network_kpi_provenance_v2,
)


def test_network_kpi_provenance_v2_binds_metrics_to_network_contract() -> None:
    metrics = {
        "network_quality_metric_model": "FLOW_LEVEL_PROXY",
        "network_quality_proxy_note": (
            "Flow-level proxy only; no packet-level simulation is performed."
        ),
        "network_quality_provenance_note": (
            "Flow-level KPI provenance from route, link, and completed-flow state; "
            "no packet-level samples are used."
        ),
        "network_quality_effective_throughput_mbps": 180.0,
        "network_quality_estimated_delivered_throughput_mbps": 180.0,
        "network_quality_estimated_available_throughput_mbps": 171.0,
        "network_quality_available_route_demand_mbps": 200.0,
        "network_quality_throughput_source": "COMPLETED_FLOW_CAPACITY",
        "network_quality_throughput_source_label": "completed flow capacity",
        "network_quality_effective_latency_avg_s": 0.045,
        "network_quality_route_latency_avg_s": 0.05,
        "network_quality_flow_latency_avg_s": 0.045,
        "network_quality_latency_source": "COMPLETED_FLOW_LATENCY",
        "network_quality_latency_source_label": "completed flow latency",
        "network_quality_effective_loss_proxy_rate": 0.05,
        "network_quality_route_blocking_ratio": 0.02,
        "network_quality_failed_flow_ratio": 0.0,
        "network_quality_congestion_loss_proxy_rate": 0.03,
        "network_quality_demand_loss_proxy_rate": 0.05,
        "network_quality_loss_source": "PRESSURE_LOSS_PROXY",
        "network_quality_loss_source_label": "pressure loss proxy",
        "network_quality_loss_zero_reason": "POSITIVE_PROXY",
        "network_quality_loss_zero_reason_label": "positive proxy",
        "network_quality_effective_delay_variation_proxy_s": 0.006,
        "network_quality_delay_variation_proxy_s": 0.004,
        "network_quality_flow_latency_variation_proxy_s": 0.006,
        "network_quality_pressure_delay_variation_proxy_s": 0.001,
        "network_quality_delay_variation_source": "FLOW_LATENCY_VARIATION",
        "network_quality_delay_variation_source_label": "flow latency variation",
        "network_quality_delay_variation_zero_reason": "POSITIVE_PROXY",
        "network_quality_delay_variation_zero_reason_label": "positive proxy",
        "network_quality_congestion_proxy": 0.8,
    }

    provenance = build_network_kpi_provenance_v2(metrics)

    assert provenance["version"] == "v2"
    assert provenance["provenance_id"] == NETWORK_KPI_PROVENANCE_V2_ID
    assert provenance["source"] == "BACKEND_METRICS_SUMMARY"
    assert provenance["network_model_contract_id"] == (
        "leo_twin.network_model_contract.v2"
    )
    assert provenance["metric_model"] == "FLOW_LEVEL_PROXY"
    assert provenance["packet_level_simulation"] is False
    assert provenance["kpi_count"] == len(provenance["kpis"])
    assert json.loads(json.dumps(provenance, sort_keys=True))["provenance_id"] == (
        NETWORK_KPI_PROVENANCE_V2_ID
    )

    throughput = _kpi(provenance, "EFFECTIVE_THROUGHPUT")
    assert throughput["runtime_summary_key"] == (
        "network_quality_effective_throughput_mbps"
    )
    assert throughput["current_value"] == 180.0
    assert throughput["status"] == "OBSERVED"
    assert throughput["observed_source"] == {
        "source": "COMPLETED_FLOW_CAPACITY",
        "label": "completed flow capacity",
    }
    assert throughput["packet_level_metric"] is False
    throughput_fields = _source_fields(throughput)
    assert throughput_fields[
        "network_quality_estimated_delivered_throughput_mbps"
    ] == {
        "field": "network_quality_estimated_delivered_throughput_mbps",
        "current_value": 180.0,
        "value_source": "METRICS_SUMMARY",
    }

    loss = _kpi(provenance, "EFFECTIVE_LOSS_PROXY")
    assert loss["current_value"] == 0.05
    assert loss["zero_reason"] == {
        "reason": "POSITIVE_PROXY",
        "label": "positive proxy",
    }
    loss_fields = _source_fields(loss)
    assert loss_fields["network.transport_loss_rate"]["value_source"] == (
        "MODEL_OR_CONFIG_STATE"
    )
    assert loss_fields["network_quality_failed_flow_ratio"]["current_value"] == 0.0

    delay_variation = _kpi(provenance, "EFFECTIVE_DELAY_VARIATION_PROXY")
    assert delay_variation["current_value"] == 0.006
    assert delay_variation["observed_source"]["source"] == "FLOW_LATENCY_VARIATION"


def test_network_kpi_provenance_v2_reports_missing_runtime_values() -> None:
    provenance = build_network_kpi_provenance_v2({})

    assert provenance["metric_model"] == "FLOW_LEVEL_PROXY"
    assert all(
        item["status"] == "MISSING_RUNTIME_VALUE"
        for item in provenance["kpis"]
        if isinstance(item, dict)
    )
    throughput = _kpi(provenance, "EFFECTIVE_THROUGHPUT")
    assert throughput["current_value"] is None
    assert throughput["observed_source"] == {"source": "", "label": ""}


def _kpi(provenance: dict[str, object], metric: str) -> dict[str, object]:
    kpis = provenance["kpis"]
    assert isinstance(kpis, tuple)
    for item in kpis:
        assert isinstance(item, dict)
        if item["metric"] == metric:
            return item
    raise AssertionError(f"missing KPI {metric}")


def _source_fields(item: dict[str, object]) -> dict[str, dict[str, object]]:
    source_fields = item["source_fields"]
    assert isinstance(source_fields, tuple)
    result: dict[str, dict[str, object]] = {}
    for source_field in source_fields:
        assert isinstance(source_field, dict)
        result[str(source_field["field"])] = source_field
    return result
