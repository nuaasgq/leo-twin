"""Model verification report template for benchmark acceptance scenarios."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from leo_twin.schema.compute_resource_contract import compute_resource_contract_v2_to_dict
from leo_twin.schema.network_model_contract import network_model_contract_v2_to_dict
from leo_twin.services.benchmark_scenarios import (
    BENCHMARK_SCENARIO_MATRIX_V1_ID,
    PROJECT_ROOT,
    benchmark_scenario_matrix_v1_to_dict,
)


MODEL_VERIFICATION_REPORT_TEMPLATE_V1_ID = (
    "leo_twin.model_verification_report_template.v1"
)


def model_verification_report_template_v1_to_dict(
    project_root: Path | None = None,
) -> dict[str, object]:
    """Return a deterministic model verification report template."""

    matrix = benchmark_scenario_matrix_v1_to_dict(
        PROJECT_ROOT if project_root is None else Path(project_root)
    )
    network_contract = network_model_contract_v2_to_dict()
    compute_contract = compute_resource_contract_v2_to_dict()
    scenarios = tuple(
        _scenario_report_template(
            scenario,
            matrix=matrix,
            network_contract=network_contract,
            compute_contract=compute_contract,
        )
        for scenario in _records(matrix.get("scenarios"))
    )
    return {
        "template_id": MODEL_VERIFICATION_REPORT_TEMPLATE_V1_ID,
        "version": "v1",
        "benchmark_matrix_id": BENCHMARK_SCENARIO_MATRIX_V1_ID,
        "benchmark_matrix_version": str(matrix.get("version", "")),
        "purpose": (
            "Provide a repeatable review template for benchmark scenario model "
            "assumptions, formulas, boundary conditions, deterministic seeds, "
            "expected outputs, and evidence collection."
        ),
        "contracts": {
            "network_model_contract_id": str(network_contract["contract_id"]),
            "network_model_contract_version": str(network_contract["version"]),
            "compute_resource_contract_id": str(compute_contract["contract_id"]),
            "compute_resource_contract_version": str(compute_contract["version"]),
        },
        "report_sections": (
            "scenario_identity",
            "configuration_boundary_conditions",
            "determinism_plan",
            "formula_checks",
            "expected_outputs",
            "evidence_checklist",
            "known_limitations",
            "review_decision",
        ),
        "formula_catalog": {
            "network_kpi_checks": _network_formula_checks(network_contract),
            "compute_service_time_check": _compute_service_time_check(compute_contract),
        },
        "scenario_reports": scenarios,
        "scenario_report_count": len(scenarios),
        "global_exclusions": {
            "forbidden_integrations": tuple(matrix.get("forbidden_integrations", ())),
            "packet_level_simulation": matrix.get("packet_level_simulation") is True,
            "network_excluded_capabilities": tuple(
                network_contract.get("excluded_capabilities", ())
            ),
            "compute_excluded_capabilities": tuple(
                compute_contract["service_time_estimator"].get(
                    "excluded_semantics",
                    (),
                )
            ),
        },
        "acceptance_commands": (
            "python -m pytest tests/unit/test_benchmark_scenario_matrix_v1.py -q",
            "python -m pytest tests/unit/test_model_verification_report_template_v1.py -q",
            "python -m pytest tests/integration/test_product_acceptance_scenarios.py -q",
        ),
        "review_decision_values": (
            "PASS",
            "PASS_WITH_LIMITATIONS",
            "FAIL_MODEL_DRIFT",
            "FAIL_NON_DETERMINISTIC",
            "FAIL_SCOPE_VIOLATION",
        ),
    }


def _scenario_report_template(
    scenario: Mapping[str, Any],
    *,
    matrix: Mapping[str, Any],
    network_contract: Mapping[str, Any],
    compute_contract: Mapping[str, Any],
) -> dict[str, object]:
    fidelity_summary = _mapping(scenario.get("fidelity_summary"))
    runtime_status_expectation = _mapping(scenario.get("runtime_status_expectation"))
    return {
        "scenario_id": str(scenario.get("scenario_id", "")),
        "label": str(scenario.get("label", "")),
        "config_path": str(scenario.get("config_path", "")),
        "scale_tier": str(scenario.get("scale_tier", "")),
        "deterministic_seed": int(scenario.get("runtime_seed", 0)),
        "configuration_boundary_conditions": {
            "satellite_count": int(scenario.get("satellite_count", 0)),
            "user_count": int(scenario.get("user_count", 0)),
            "compute_node_count": int(scenario.get("compute_node_count", 0)),
            "runtime_duration_s": int(scenario.get("runtime_duration_s", 0)),
            "orbit_update_interval_s": int(
                scenario.get("orbit_update_interval_s", 0)
            ),
            "plane_count": int(scenario.get("plane_count", 0)),
            "application_protocol": str(scenario.get("application_protocol", "")),
            "traffic_class": str(scenario.get("traffic_class", "")),
            "traffic_destination_type": str(
                scenario.get("traffic_destination_type", "")
            ),
            "orbit_update_mode": str(fidelity_summary.get("orbit_update_mode", "")),
            "metrics_mode": str(fidelity_summary.get("metrics_mode", "")),
            "space_link_mode": str(fidelity_summary.get("space_link_mode", "")),
            "scale_limit_reason": str(fidelity_summary.get("scale_limit_reason", "")),
        },
        "determinism_plan": {
            "same_input_rule": "Same config path and seed must produce identical summaries.",
            "seed_source": "runtime.seed",
            "seed_value": int(scenario.get("runtime_seed", 0)),
            "ordered_outputs": (
                "benchmark_scenario_matrix_v1",
                "backend_summary",
                "fidelity_summary",
                "runtime_status",
            ),
            "forbidden_randomness": "unseeded randomness",
        },
        "formula_checks": {
            "network_kpi_checks": _network_formula_checks(network_contract),
            "compute_service_time_check": _compute_service_time_check(compute_contract),
        },
        "expected_outputs": {
            "expected_ranges": tuple(scenario.get("expected_ranges", ())),
            "fidelity_expectation": dict(
                _mapping(scenario.get("fidelity_expectation"))
            ),
            "result_artifact_expectation": tuple(
                matrix.get("result_artifact_expectation", ())
            ),
            "runtime_status_fields": tuple(
                runtime_status_expectation.get("required_fields", ())
            ),
            "runtime_status_expectation": dict(runtime_status_expectation),
            "state_stream_fields": (
                "WorldSnapshot.satellites",
                "WorldSnapshot.fidelity_summary",
            ),
        },
        "evidence_checklist": (
            {
                "evidence": "config_load",
                "method": "load_config(config_path)",
                "required": True,
            },
            {
                "evidence": "backend_summary_determinism",
                "method": "build backend summary twice and compare equality",
                "required": True,
            },
            {
                "evidence": "live_runtime_smoke",
                "method": "initialize, start, advance one tick, pause, stop, reset",
                "required": True,
            },
            {
                "evidence": "route_trust_acceptance",
                "method": (
                    "check route_provenance_trust_summary_v1 against "
                    "route_explanation_summary_v1 for every benchmark scenario"
                ),
                "required": True,
            },
            {
                "evidence": "artifact_manifest",
                "method": "record config snapshot, events.jsonl, metrics.csv, summary.json",
                "required": True,
            },
        ),
        "known_limitations": (
            str(scenario.get("model_note", "")),
            str(network_contract.get("model_note", "")),
            str(compute_contract.get("model_note", "")),
        ),
        "review_decision": {
            "value": "PENDING_REVIEW",
            "reviewer_notes": "",
        },
    }


def _network_formula_checks(
    network_contract: Mapping[str, Any],
) -> tuple[dict[str, object], ...]:
    return tuple(
        {
            "metric": str(kpi.get("metric", "")),
            "runtime_summary_key": str(kpi.get("runtime_summary_key", "")),
            "layer": str(kpi.get("layer", "")),
            "unit": str(kpi.get("unit", "")),
            "source_fields": tuple(kpi.get("source_fields", ())),
            "formula_summary": str(kpi.get("formula_summary", "")),
            "zero_value_semantics": str(kpi.get("zero_value_semantics", "")),
            "packet_level_metric": kpi.get("packet_level_metric") is True,
            "verification_method": (
                "Compare runtime summary value with documented source fields and "
                "formula summary; record zero-value reason when value is zero."
            ),
        }
        for kpi in _records(network_contract.get("kpi_contracts"))
    )


def _compute_service_time_check(
    compute_contract: Mapping[str, Any],
) -> dict[str, object]:
    estimator = _mapping(compute_contract.get("service_time_estimator"))
    return {
        "estimator_id": str(estimator.get("estimator_id", "")),
        "model": str(estimator.get("model", "")),
        "formula_summary": str(estimator.get("formula_summary", "")),
        "bottleneck_policy": str(estimator.get("bottleneck_policy", "")),
        "capacity_limit_policy": str(estimator.get("capacity_limit_policy", "")),
        "legacy_mapping": str(estimator.get("legacy_mapping", "")),
        "verification_method": (
            "Check queue delay and execution delay against the deterministic "
            "bottleneck resource estimator and configured compute resource vector."
        ),
    }


def _records(value: object) -> tuple[Mapping[str, Any], ...]:
    if not isinstance(value, (list, tuple)):
        return ()
    return tuple(item for item in value if isinstance(item, Mapping))


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}
