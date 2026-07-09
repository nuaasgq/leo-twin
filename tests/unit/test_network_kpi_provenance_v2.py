from __future__ import annotations

import json

from leo_twin.services.network_kpi_provenance import (
    NETWORK_KPI_CREDIBILITY_V1_ID,
    NETWORK_KPI_PROVENANCE_V2_ID,
    NETWORK_TEMPORAL_PRESSURE_EVIDENCE_V1_ID,
    build_network_kpi_credibility_v1,
    build_network_kpi_provenance_v2,
)
from leo_twin.services.network_kpi_calibration import build_network_kpi_calibration_v1
from leo_twin.services.network_kpi_formula_evidence import (
    NETWORK_KPI_FORMULA_EVIDENCE_V1_ID,
    build_network_kpi_formula_evidence_v1,
)
from leo_twin.services.network_kpi_variation_explanation import (
    NETWORK_KPI_VARIATION_EXPLANATION_V1_ID,
    build_network_kpi_variation_explanation_v1,
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
        "network_quality_time_adjusted_delivered_throughput_mbps": 171.0,
        "network_quality_estimated_available_throughput_mbps": 171.0,
        "network_quality_available_route_demand_mbps": 200.0,
        "network_quality_active_flow_capacity_mbps": 0.0,
        "network_quality_time_adjusted_active_throughput_mbps": 0.0,
        "network_quality_active_flow_pressure_proxy": 0.0,
        "network_quality_throughput_source": "COMPLETED_FLOW_CAPACITY",
        "network_quality_throughput_source_label": "completed flow capacity",
        "network_quality_effective_latency_avg_s": 0.045,
        "network_quality_route_latency_avg_s": 0.05,
        "network_quality_flow_latency_avg_s": 0.045,
        "network_quality_active_flow_latency_avg_s": 0.0,
        "network_quality_latency_source": "COMPLETED_FLOW_LATENCY",
        "network_quality_latency_source_label": "completed flow latency",
        "network_quality_effective_loss_proxy_rate": 0.05,
        "network_quality_failed_flow_ratio": 0.0,
        "network_quality_active_flow_blocking_ratio": 0.0,
        "network_quality_congestion_loss_proxy_rate": 0.03,
        "network_quality_demand_loss_proxy_rate": 0.05,
        "network_quality_time_pressure_period_s": 120.0,
        "network_quality_time_pressure_phase": 0.5,
        "network_quality_time_pressure_factor": 0.85,
        "network_quality_time_pressure_loss_proxy_rate": 0.07,
        "network_quality_demand_pressure_proxy": 0.92,
        "network_quality_throughput_pressure_proxy": 0.75,
        "network_quality_flow_delivered_capacity_mbps": 180.0,
        "network_quality_route_blocking_ratio": 0.0,
        "network_quality_route_decision_count": 4,
        "network_quality_available_route_decision_count": 4,
        "network_quality_unavailable_route_decision_count": 0,
        "network_quality_pressure_admission_rejected_route_count": 0,
        "network_quality_pressure_admission_rejection_ratio": 0.0,
        "network_quality_topology_blocked_route_count": 0,
        "network_quality_loss_source": "PRESSURE_LOSS_PROXY",
        "network_quality_loss_source_label": "pressure loss proxy",
        "network_quality_loss_zero_reason": "POSITIVE_PROXY",
        "network_quality_loss_zero_reason_label": "positive proxy",
        "network_quality_effective_delay_variation_proxy_s": 0.006,
        "network_quality_delay_variation_proxy_s": 0.004,
        "network_quality_flow_latency_variation_proxy_s": 0.006,
        "network_quality_active_flow_latency_variation_proxy_s": 0.0,
        "network_quality_pressure_delay_variation_proxy_s": 0.001,
        "network_quality_time_pressure_delay_variation_proxy_s": 0.002,
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
    temporal = provenance["temporal_pressure_evidence"]
    assert isinstance(temporal, dict)
    assert temporal["version"] == "v1"
    assert temporal["evidence_id"] == NETWORK_TEMPORAL_PRESSURE_EVIDENCE_V1_ID
    assert temporal["source"] == "METRICS_SUMMARY"
    assert temporal["temporal_pressure_model"] == (
        "DETERMINISTIC_TRIANGULAR_LOAD_GATED_PROXY"
    )
    assert temporal["packet_level_simulation"] is False
    assert temporal["frontend_inference_required"] is False
    assert temporal["status"] == "OBSERVED"
    assert temporal["time_pressure_period_s"] == 120.0
    assert temporal["time_pressure_phase"] == 0.5
    assert temporal["time_pressure_factor"] == 0.85
    assert temporal["dominant_load_component"] == {
        "component": "demand_pressure",
        "field": "network_quality_demand_pressure_proxy",
        "current_value": 0.92,
        "value_source": "METRICS_SUMMARY",
    }
    assert temporal["load_pressure_proxy"] == 0.92
    assert temporal["loss_proxy_rate"] == 0.07
    assert temporal["delay_variation_proxy_s"] == 0.002
    assert temporal["temporal_pressure_active"] is True
    assert temporal["loss_proxy_active"] is True
    assert temporal["delay_variation_proxy_active"] is True
    assert temporal["throughput_delta_mbps"] == 9.0
    temporal_fields = _temporal_source_fields(temporal)
    assert temporal_fields["network_quality_time_pressure_factor"] == {
        "field": "network_quality_time_pressure_factor",
        "current_value": 0.85,
        "value_source": "METRICS_SUMMARY",
    }

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
    throughput_inputs = _formula_inputs(throughput)
    assert throughput_inputs[
        "network_quality_estimated_delivered_throughput_mbps"
    ]["role"] == "SELECTED_RUNTIME_INPUT"
    assert throughput_inputs[
        "network_quality_time_adjusted_delivered_throughput_mbps"
    ]["selected_for_current_value"] is True
    assert throughput_inputs[
        "network_quality_available_route_demand_mbps"
    ]["role"] == "OBSERVED_SUPPORTING_INPUT"
    assert throughput["formula_trace"] == {
        "selection_policy": (
            "Prefer completed-flow throughput with deterministic pressure context; "
            "otherwise use active in-flight flow throughput before loss-adjusted "
            "available route demand/capacity."
        ),
        "runtime_summary_key": "network_quality_effective_throughput_mbps",
        "runtime_value_observed": True,
        "current_value": 180.0,
        "observed_source": "COMPLETED_FLOW_CAPACITY",
        "observed_source_label": "completed flow capacity",
        "declared_input_count": 6,
        "observed_input_count": 6,
        "selected_input_count": 2,
        "selected_observed_input_count": 2,
        "missing_input_count": 0,
        "selected_source_fields": (
            "network_quality_estimated_delivered_throughput_mbps",
            "network_quality_time_adjusted_delivered_throughput_mbps",
        ),
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
    loss_inputs = _formula_inputs(loss)
    assert loss_inputs["network.transport_loss_rate"]["role"] == (
        "DECLARED_SUPPORTING_INPUT"
    )
    assert loss_inputs["network_quality_demand_loss_proxy_rate"]["role"] == (
        "SELECTED_RUNTIME_INPUT"
    )
    assert loss_inputs[
        "network_quality_time_pressure_loss_proxy_rate"
    ]["selected_for_current_value"] is True
    assert loss["formula_trace"]["selected_input_count"] == 3

    blocking = _kpi(provenance, "ROUTE_BLOCKING_RATIO")
    blocking_fields = _source_fields(blocking)
    assert blocking_fields[
        "network_quality_pressure_admission_rejected_route_count"
    ]["current_value"] == 0
    blocking_inputs = _formula_inputs(blocking)
    assert blocking_inputs[
        "network_quality_route_decision_count"
    ]["role"] == "SELECTED_RUNTIME_INPUT"
    assert blocking["formula_trace"]["selected_source_fields"] == (
        "network_quality_route_decision_count",
        "network_quality_available_route_decision_count",
        "network_quality_unavailable_route_decision_count",
        "network_quality_pressure_admission_rejected_route_count",
        "network_quality_topology_blocked_route_count",
    )

    delay_variation = _kpi(provenance, "EFFECTIVE_DELAY_VARIATION_PROXY")
    assert delay_variation["current_value"] == 0.006
    assert delay_variation["observed_source"]["source"] == "FLOW_LATENCY_VARIATION"
    delay_inputs = _formula_inputs(delay_variation)
    assert delay_inputs[
        "network_quality_flow_latency_variation_proxy_s"
    ]["role"] == "SELECTED_RUNTIME_INPUT"

    credibility = build_network_kpi_credibility_v1(provenance)
    assert credibility["version"] == "v1"
    assert credibility["credibility_id"] == NETWORK_KPI_CREDIBILITY_V1_ID
    assert credibility["source"] == "NETWORK_KPI_PROVENANCE_V2"
    assert credibility["provenance_id"] == NETWORK_KPI_PROVENANCE_V2_ID
    assert credibility["credibility_status"] == "COMPLETE_FLOW_LEVEL_PROXY"
    assert credibility["kpi_count"] == 6
    assert credibility["observed_kpi_count"] == 6
    assert credibility["missing_kpi_count"] == 0
    assert credibility["packet_level_simulation"] is False
    assert credibility["packet_level_metric_count"] == 0
    assert credibility["flow_level_proxy_metric_count"] == 6
    assert credibility["zero_value_kpi_count"] >= 1
    assert credibility["zero_value_explained_count"] == credibility["zero_value_kpi_count"]
    assert credibility["missing_metrics"] == ()
    assert credibility["zero_unexplained_metrics"] == ()
    assert "flow-level proxies" in credibility["caveats"][0]


def test_network_kpi_provenance_v2_reports_missing_runtime_values() -> None:
    provenance = build_network_kpi_provenance_v2({})

    assert provenance["metric_model"] == "FLOW_LEVEL_PROXY"
    assert all(
        item["status"] == "MISSING_RUNTIME_VALUE"
        for item in provenance["kpis"]
        if isinstance(item, dict)
    )
    temporal = provenance["temporal_pressure_evidence"]
    assert isinstance(temporal, dict)
    assert temporal["status"] == "MISSING_RUNTIME_VALUES"
    assert temporal["observed_required_field_count"] == 0
    assert temporal["dominant_load_component"] == {
        "component": "demand_pressure",
        "field": "network_quality_demand_pressure_proxy",
        "current_value": 0.0,
        "value_source": "MISSING",
    }
    assert temporal["time_pressure_factor"] is None
    assert temporal["loss_proxy_active"] is False

    throughput = _kpi(provenance, "EFFECTIVE_THROUGHPUT")
    assert throughput["current_value"] is None
    assert throughput["observed_source"] == {"source": "", "label": ""}
    assert throughput["formula_trace"]["runtime_value_observed"] is False
    assert throughput["formula_trace"]["observed_input_count"] == 0
    assert throughput["formula_trace"]["missing_input_count"] == len(
        throughput["formula_inputs"]
    )

    credibility = build_network_kpi_credibility_v1(provenance)
    assert credibility["credibility_status"] == "MISSING_RUNTIME_VALUES"
    assert credibility["observed_kpi_count"] == 0
    assert credibility["missing_kpi_count"] == credibility["kpi_count"]
    assert credibility["missing_metrics"] == tuple(
        item["metric"] for item in provenance["kpis"] if isinstance(item, dict)
    )


def test_network_kpi_formula_evidence_v1_combines_formula_inputs_and_calibration() -> None:
    metrics = {
        "network_quality_metric_model": "FLOW_LEVEL_PROXY",
        "network_quality_effective_throughput_mbps": 180.0,
        "network_quality_estimated_delivered_throughput_mbps": 180.0,
        "network_quality_time_adjusted_delivered_throughput_mbps": 171.0,
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
        "network_quality_failed_flow_ratio": 0.0,
        "network_quality_congestion_loss_proxy_rate": 0.03,
        "network_quality_demand_loss_proxy_rate": 0.05,
        "network_quality_time_pressure_loss_proxy_rate": 0.07,
        "network_quality_loss_source": "PRESSURE_LOSS_PROXY",
        "network_quality_loss_source_label": "pressure loss proxy",
        "network_quality_effective_delay_variation_proxy_s": 0.006,
        "network_quality_delay_variation_proxy_s": 0.004,
        "network_quality_flow_latency_variation_proxy_s": 0.006,
        "network_quality_pressure_delay_variation_proxy_s": 0.001,
        "network_quality_time_pressure_delay_variation_proxy_s": 0.002,
        "network_quality_delay_variation_source": "FLOW_LATENCY_VARIATION",
        "network_quality_delay_variation_source_label": "flow latency variation",
        "network_quality_route_blocking_ratio": 0.0,
        "network_quality_route_decision_count": 4,
        "network_quality_available_route_decision_count": 4,
        "network_quality_unavailable_route_decision_count": 0,
        "network_quality_pressure_admission_rejected_route_count": 0,
        "network_quality_pressure_admission_rejection_ratio": 0.0,
        "network_quality_topology_blocked_route_count": 0,
        "network_quality_congestion_proxy": 0.8,
        "network_quality_requested_route_demand_mbps": 200.0,
        "network_quality_offered_route_capacity_mbps": 220.0,
    }
    series = {
        "samples": (
            {
                "sim_time": 1.0,
                "network_effective_throughput_mbps": 160.0,
                "network_effective_latency_s": 0.04,
                "network_effective_loss_proxy_rate": 0.04,
                "network_effective_delay_variation_s": 0.005,
            },
            {
                "sim_time": 2.0,
                "network_effective_throughput_mbps": 180.0,
                "network_effective_latency_s": 0.045,
                "network_effective_loss_proxy_rate": 0.05,
                "network_effective_delay_variation_s": 0.006,
            },
        )
    }
    provenance = build_network_kpi_provenance_v2(metrics)
    calibration = build_network_kpi_calibration_v1(series, metrics)

    evidence = build_network_kpi_formula_evidence_v1(
        metrics,
        provenance,
        calibration,
    )

    assert evidence["version"] == "v1"
    assert evidence["evidence_id"] == NETWORK_KPI_FORMULA_EVIDENCE_V1_ID
    assert evidence["source"] == "NETWORK_KPI_PROVENANCE_V2_AND_CALIBRATION_V1"
    assert evidence["provenance_id"] == NETWORK_KPI_PROVENANCE_V2_ID
    assert evidence["calibration_id"] == "leo_twin.network_kpi_calibration.v1"
    assert evidence["packet_level_simulation"] is False
    assert evidence["kpi_count"] == len(evidence["kpis"])
    assert evidence["observed_kpi_count"] == evidence["kpi_count"]
    assert evidence["missing_selected_input_count"] == 0
    assert evidence["time_varying_kpi_count"] >= 1
    assert evidence["formula_evidence_status"] == "FORMULA_AND_TIME_EVIDENCE_READY"
    throughput = _formula_evidence_kpi(evidence, "EFFECTIVE_THROUGHPUT")
    assert throughput["current_value"] == 180.0
    assert throughput["observed_source"] == "COMPLETED_FLOW_CAPACITY"
    assert throughput["selected_input_count"] == 2
    assert throughput["selected_observed_input_count"] == 2
    assert throughput["variation_status"] == "TIME_VARYING"
    assert throughput["evidence_status"] == "FORMULA_AND_TIME_VARYING"
    assert [item["field"] for item in throughput["selected_inputs"]] == [
        "network_quality_estimated_delivered_throughput_mbps",
        "network_quality_time_adjusted_delivered_throughput_mbps",
    ]
    assert json.loads(json.dumps(evidence, sort_keys=True))["evidence_id"] == (
        NETWORK_KPI_FORMULA_EVIDENCE_V1_ID
    )


def test_network_kpi_variation_explanation_v1_explains_metric_movement() -> None:
    metrics = {
        "network_quality_metric_model": "FLOW_LEVEL_PROXY",
        "network_quality_effective_throughput_mbps": 180.0,
        "network_quality_estimated_delivered_throughput_mbps": 180.0,
        "network_quality_time_adjusted_delivered_throughput_mbps": 171.0,
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
        "network_quality_failed_flow_ratio": 0.0,
        "network_quality_congestion_loss_proxy_rate": 0.03,
        "network_quality_demand_loss_proxy_rate": 0.05,
        "network_quality_time_pressure_loss_proxy_rate": 0.07,
        "network_quality_loss_source": "PRESSURE_LOSS_PROXY",
        "network_quality_loss_source_label": "pressure loss proxy",
        "network_quality_effective_delay_variation_proxy_s": 0.006,
        "network_quality_delay_variation_proxy_s": 0.004,
        "network_quality_flow_latency_variation_proxy_s": 0.006,
        "network_quality_pressure_delay_variation_proxy_s": 0.001,
        "network_quality_time_pressure_delay_variation_proxy_s": 0.002,
        "network_quality_delay_variation_source": "FLOW_LATENCY_VARIATION",
        "network_quality_delay_variation_source_label": "flow latency variation",
        "network_quality_route_blocking_ratio": 0.0,
        "network_quality_route_decision_count": 4,
        "network_quality_available_route_decision_count": 4,
        "network_quality_unavailable_route_decision_count": 0,
        "network_quality_pressure_admission_rejected_route_count": 0,
        "network_quality_pressure_admission_rejection_ratio": 0.0,
        "network_quality_topology_blocked_route_count": 0,
        "network_quality_congestion_proxy": 0.8,
        "network_quality_requested_route_demand_mbps": 200.0,
        "network_quality_offered_route_capacity_mbps": 220.0,
    }
    series = {
        "samples": (
            {
                "sim_time": 1.0,
                "network_effective_throughput_mbps": 160.0,
                "network_effective_latency_s": 0.04,
                "network_effective_loss_proxy_rate": 0.04,
                "network_effective_delay_variation_s": 0.005,
            },
            {
                "sim_time": 2.0,
                "network_effective_throughput_mbps": 180.0,
                "network_effective_latency_s": 0.045,
                "network_effective_loss_proxy_rate": 0.05,
                "network_effective_delay_variation_s": 0.006,
            },
        )
    }
    provenance = build_network_kpi_provenance_v2(metrics)
    calibration = build_network_kpi_calibration_v1(series, metrics)
    evidence = build_network_kpi_formula_evidence_v1(
        metrics,
        provenance,
        calibration,
    )

    explanation = build_network_kpi_variation_explanation_v1(
        metrics,
        provenance,
        calibration,
        evidence,
    )

    assert explanation["version"] == "v1"
    assert explanation["explanation_id"] == NETWORK_KPI_VARIATION_EXPLANATION_V1_ID
    assert explanation["source"] == "NETWORK_KPI_FORMULA_EVIDENCE_V1_AND_CALIBRATION_V1"
    assert explanation["packet_level_simulation"] is False
    assert explanation["sample_count"] == 2
    assert explanation["time_varying_kpi_count"] >= 1
    assert explanation["explanation_status"] == "TIME_VARIATION_EXPLAINED"
    assert str(explanation["explanation_hash"]).startswith("sha256:")
    throughput = _variation_explanation_kpi(explanation, "EFFECTIVE_THROUGHPUT")
    assert throughput["variation_status"] == "TIME_VARYING"
    assert throughput["explanation_status"] == "TIME_VARIATION_EXPLAINED"
    assert "随仿真时间变化" in str(throughput["user_explanation"])
    assert [item["field"] for item in throughput["selected_inputs"]] == [
        "network_quality_estimated_delivered_throughput_mbps",
        "network_quality_time_adjusted_delivered_throughput_mbps",
    ]
    assert json.loads(json.dumps(explanation, sort_keys=True))["explanation_id"] == (
        NETWORK_KPI_VARIATION_EXPLANATION_V1_ID
    )


def test_network_kpi_variation_explanation_v1_explains_flat_active_kpis() -> None:
    metrics = {
        "network_quality_metric_model": "FLOW_LEVEL_PROXY",
        "network_quality_effective_throughput_mbps": 100.0,
        "network_quality_estimated_delivered_throughput_mbps": 100.0,
        "network_quality_time_adjusted_delivered_throughput_mbps": 100.0,
        "network_quality_throughput_source": "COMPLETED_FLOW_CAPACITY",
        "network_quality_throughput_source_label": "completed flow capacity",
        "network_quality_effective_latency_avg_s": 0.04,
        "network_quality_flow_latency_avg_s": 0.04,
        "network_quality_latency_source": "COMPLETED_FLOW_LATENCY",
        "network_quality_latency_source_label": "completed flow latency",
        "network_quality_effective_loss_proxy_rate": 0.0,
        "network_quality_failed_flow_ratio": 0.0,
        "network_quality_congestion_loss_proxy_rate": 0.0,
        "network_quality_demand_loss_proxy_rate": 0.0,
        "network_quality_time_pressure_loss_proxy_rate": 0.0,
        "network_quality_loss_source": "PRESSURE_LOSS_PROXY",
        "network_quality_loss_source_label": "pressure loss proxy",
        "network_quality_effective_delay_variation_proxy_s": 0.0,
        "network_quality_delay_variation_proxy_s": 0.0,
        "network_quality_flow_latency_variation_proxy_s": 0.0,
        "network_quality_pressure_delay_variation_proxy_s": 0.0,
        "network_quality_time_pressure_delay_variation_proxy_s": 0.0,
        "network_quality_delay_variation_source": "FLOW_LATENCY_VARIATION",
        "network_quality_delay_variation_source_label": "flow latency variation",
        "network_quality_route_blocking_ratio": 0.0,
        "network_quality_route_decision_count": 4,
        "network_quality_available_route_decision_count": 4,
        "network_quality_unavailable_route_decision_count": 0,
        "network_quality_pressure_admission_rejected_route_count": 0,
        "network_quality_pressure_admission_rejection_ratio": 0.0,
        "network_quality_topology_blocked_route_count": 0,
        "network_quality_congestion_proxy": 0.0,
        "network_quality_requested_route_demand_mbps": 100.0,
        "network_quality_offered_route_capacity_mbps": 100.0,
    }
    series = {
        "samples": (
            {
                "sim_time": 1.0,
                "network_effective_throughput_mbps": 100.0,
                "network_effective_latency_s": 0.04,
                "network_effective_loss_proxy_rate": 0.0,
                "network_effective_delay_variation_s": 0.0,
            },
            {
                "sim_time": 2.0,
                "network_effective_throughput_mbps": 100.0,
                "network_effective_latency_s": 0.04,
                "network_effective_loss_proxy_rate": 0.0,
                "network_effective_delay_variation_s": 0.0,
            },
        )
    }
    provenance = build_network_kpi_provenance_v2(metrics)
    calibration = build_network_kpi_calibration_v1(series, metrics)
    evidence = build_network_kpi_formula_evidence_v1(
        metrics,
        provenance,
        calibration,
    )

    explanation = build_network_kpi_variation_explanation_v1(
        metrics,
        provenance,
        calibration,
        evidence,
    )

    assert explanation["explanation_status"] == "FLAT_UNDER_ACTIVITY_EXPLAINED"
    assert explanation["time_varying_kpi_count"] == 0
    assert explanation["flat_kpi_count"] >= 1
    loss = _variation_explanation_kpi(explanation, "EFFECTIVE_LOSS_PROXY")
    assert loss["variation_status"] == "FLAT_ZERO"
    assert loss["explanation_status"] == "FLAT_ZERO_EXPLAINED"
    assert "保持为零" in str(loss["user_explanation"])


def _kpi(provenance: dict[str, object], metric: str) -> dict[str, object]:
    kpis = provenance["kpis"]
    assert isinstance(kpis, tuple)
    for item in kpis:
        assert isinstance(item, dict)
        if item["metric"] == metric:
            return item
    raise AssertionError(f"missing KPI {metric}")


def _temporal_source_fields(item: dict[str, object]) -> dict[str, dict[str, object]]:
    source_fields = item["source_fields"]
    assert isinstance(source_fields, tuple)
    result: dict[str, dict[str, object]] = {}
    for field in source_fields:
        assert isinstance(field, dict)
        result[str(field["field"])] = field
    return result

def _source_fields(item: dict[str, object]) -> dict[str, dict[str, object]]:
    source_fields = item["source_fields"]
    assert isinstance(source_fields, tuple)
    result: dict[str, dict[str, object]] = {}
    for source_field in source_fields:
        assert isinstance(source_field, dict)
        result[str(source_field["field"])] = source_field
    return result


def _formula_inputs(item: dict[str, object]) -> dict[str, dict[str, object]]:
    formula_inputs = item["formula_inputs"]
    assert isinstance(formula_inputs, tuple)
    result: dict[str, dict[str, object]] = {}
    for formula_input in formula_inputs:
        assert isinstance(formula_input, dict)
        result[str(formula_input["field"])] = formula_input
    return result


def _formula_evidence_kpi(
    evidence: dict[str, object],
    metric: str,
) -> dict[str, object]:
    kpis = evidence["kpis"]
    assert isinstance(kpis, tuple)
    for item in kpis:
        assert isinstance(item, dict)
        if item["metric"] == metric:
            return item
    raise AssertionError(f"missing formula evidence KPI {metric}")


def _variation_explanation_kpi(
    explanation: dict[str, object],
    metric: str,
) -> dict[str, object]:
    items = explanation["items"]
    assert isinstance(items, tuple)
    for item in items:
        assert isinstance(item, dict)
        if item["metric"] == metric:
            return item
    raise AssertionError(f"missing variation explanation KPI {metric}")
