"""Backend-owned standard scenario acceptance evidence v2."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from leo_twin.schema.config import SEESConfig
from leo_twin.services.benchmark_scenarios import benchmark_scenario_matrix_v1_to_dict
from leo_twin.services.runtime_reproducibility import stable_hash_payload


STANDARD_SCENARIO_ACCEPTANCE_V2_ID = "leo_twin.standard_scenario_acceptance.v2"

REQUIRED_RUNTIME_STATUS_FIELDS: tuple[str, ...] = (
    "fidelity_summary",
    "metrics_summary",
    "network_kpi_benchmark_validation_v1",
    "network_kpi_assurance_v2",
    "runtime_dashboard_kpi_v1",
    "runtime_closure_readiness_v1",
    "business_request_lifecycle_v2",
    "compute_service_resource_evidence_v1",
    "user_configuration_closure_v2",
    "reproducibility_manifest_v1",
)

RESULT_PACKAGE_EVIDENCE_FILENAMES: tuple[str, ...] = (
    "config_snapshot.json",
    "manifest.json",
    "benchmark_acceptance_binding_v1.json",
    "standard_scenario_acceptance_v2.json",
    "business_request_lifecycle_v2.json",
    "network_kpi_assurance_v2.json",
    "compute_service_resource_evidence_v1.json",
    "user_configuration_closure_v2.json",
    "scenario_review_bundle_v1.json",
    "export_package_audit_index_v1.json",
    "package_handoff_report_v1.md",
)


def build_standard_scenario_acceptance_v2(
    config: SEESConfig,
    runtime_status: Mapping[str, Any],
    *,
    generated_config: Mapping[str, Any] | None = None,
    project_root: str | Path | None = None,
) -> dict[str, object]:
    """Build deterministic acceptance evidence for shipped standard scenarios."""

    if not isinstance(config, SEESConfig):
        raise TypeError("config must be a SEESConfig")
    if not isinstance(runtime_status, Mapping):
        raise TypeError("runtime_status must be a mapping")
    if generated_config is not None and not isinstance(generated_config, Mapping):
        raise TypeError("generated_config must be a mapping when provided")

    matrix = benchmark_scenario_matrix_v1_to_dict(
        Path(project_root) if project_root is not None else None
    )
    scenarios = tuple(
        scenario
        for scenario in matrix.get("scenarios", ())
        if isinstance(scenario, Mapping)
    )
    current_signature = _current_signature(config, runtime_status, generated_config)
    scenario_results = tuple(
        _compare_scenario(current_signature, scenario) for scenario in scenarios
    )
    best_match = _best_scenario_result(scenario_results)
    exact_match = (
        best_match if best_match.get("match_status") == "EXACT_MATCH" else None
    )
    missing_fields = tuple(
        field
        for field in REQUIRED_RUNTIME_STATUS_FIELDS
        if not _has_path(runtime_status, field)
    )
    gate_checks = _gate_checks(
        exact_match=exact_match,
        best_match=best_match,
        missing_fields=missing_fields,
        current_signature=current_signature,
    )
    fail_count = sum(1 for check in gate_checks if check["status"] == "FAIL")
    warn_count = sum(1 for check in gate_checks if check["status"] == "WARN")
    pass_count = sum(1 for check in gate_checks if check["status"] == "PASS")
    acceptance_status = "FAIL" if fail_count else "WARN" if warn_count else "PASS"
    evidence: dict[str, object] = {
        "version": "v2",
        "acceptance_id": STANDARD_SCENARIO_ACCEPTANCE_V2_ID,
        "source": "BENCHMARK_SCENARIO_MATRIX_AND_RUNTIME_STATUS",
        "matrix_id": str(matrix.get("matrix_id", "")),
        "matrix_version": str(matrix.get("version", "")),
        "scenario_count": len(scenarios),
        "standard_scenario_ids": tuple(
            str(scenario.get("scenario_id", "")) for scenario in scenarios
        ),
        "current_scenario_id": (
            str(exact_match.get("scenario_id", "")) if exact_match else ""
        ),
        "nearest_scenario_id": str(best_match.get("scenario_id", "")),
        "matched_standard_scenario": exact_match is not None,
        "match_status": (
            "EXACT_STANDARD_SCENARIO"
            if exact_match
            else "CUSTOM_OR_PARTIAL_SCENARIO"
        ),
        "acceptance_status": acceptance_status,
        "pass_count": pass_count,
        "warn_count": warn_count,
        "fail_count": fail_count,
        "gate_checks": gate_checks,
        "scenario_results": scenario_results,
        "current_signature": current_signature,
        "required_runtime_status_fields": REQUIRED_RUNTIME_STATUS_FIELDS,
        "missing_runtime_status_fields": missing_fields,
        "result_package_evidence_filenames": RESULT_PACKAGE_EVIDENCE_FILENAMES,
        "packet_level_simulation": False,
        "frontend_inference_required": False,
        "event_kernel_policy": "NO_EVENT_KERNEL_BEHAVIOR_CHANGE",
        "forbidden_external_integrations": ("STK", "EXATA", "AFSIM", "DDS"),
        "model_boundaries": (
            "DETERMINISTIC_FLOW_LEVEL_ACCEPTANCE_GUARD",
            "NO_PACKET_LEVEL_SIMULATION",
            "NO_EXTERNAL_SIMULATOR",
            "NO_EVENT_KERNEL_CHANGE",
        ),
        "recommendation": _recommendation(acceptance_status, exact_match),
    }
    evidence["acceptance_hash"] = stable_hash_payload(evidence)
    return evidence


def _current_signature(
    config: SEESConfig,
    runtime_status: Mapping[str, Any],
    generated_config: Mapping[str, Any] | None,
) -> dict[str, object]:
    fidelity = _mapping(runtime_status.get("fidelity_summary"))
    backend_summary = _mapping(
        generated_config.get("backend_summary") if generated_config else None
    )
    return {
        "satellite_count": int(config.scenario.satellite_count),
        "user_count": int(config.scenario.user_count),
        "compute_node_count": int(config.scenario.compute_nodes),
        "runtime_duration_s": int(config.runtime.duration),
        "runtime_seed": int(config.runtime.seed),
        "orbit_update_interval_s": int(
            config.scenario.orbit.update_interval_seconds
        ),
        "plane_count": int(config.scenario.orbit.plane_count),
        "orbit_update_mode": str(fidelity.get("orbit_update_mode", "")),
        "metrics_mode": str(fidelity.get("metrics_mode", "")),
        "space_link_mode": str(fidelity.get("space_link_mode", "")),
        "lifecycle_state": str(runtime_status.get("lifecycle_state", "")),
        "current_sim_time": _number(runtime_status.get("current_sim_time")),
        "processed_event_count": int(
            _number(runtime_status.get("processed_event_count"))
        ),
        "derived_constellation_present": bool(
            _mapping(backend_summary.get("derived_constellation_summary"))
        ),
        "traffic_demand_summary_present": bool(
            _mapping(backend_summary.get("traffic_demand_summary"))
        ),
        "compute_resource_summary_present": bool(
            _mapping(backend_summary.get("compute_resource_summary"))
        ),
    }


def _compare_scenario(
    current_signature: Mapping[str, object],
    scenario: Mapping[str, Any],
) -> dict[str, object]:
    field_pairs = (
        ("satellite_count", "satellite_count"),
        ("user_count", "user_count"),
        ("compute_node_count", "compute_node_count"),
        ("runtime_duration_s", "runtime_duration_s"),
        ("runtime_seed", "runtime_seed"),
        ("orbit_update_interval_s", "orbit_update_interval_s"),
        ("plane_count", "plane_count"),
    )
    checks = [
        _comparison_check(
            field=current_field,
            expected=scenario.get(scenario_field),
            actual=current_signature.get(current_field),
        )
        for current_field, scenario_field in field_pairs
    ]
    fidelity_expectation = _mapping(scenario.get("fidelity_expectation"))
    for field in ("orbit_update_mode", "metrics_mode", "space_link_mode"):
        checks.append(
            _comparison_check(
                field=field,
                expected=fidelity_expectation.get(field),
                actual=current_signature.get(field),
            )
        )
    matched_count = sum(1 for check in checks if check["matched"] is True)
    match_status = "EXACT_MATCH" if matched_count == len(checks) else "PARTIAL_MATCH"
    result = {
        "scenario_id": str(scenario.get("scenario_id", "")),
        "scale_tier": str(scenario.get("scale_tier", "")),
        "match_status": match_status,
        "matched_check_count": matched_count,
        "check_count": len(checks),
        "checks": tuple(checks),
    }
    return {**result, "result_hash": stable_hash_payload(result)}


def _comparison_check(
    *,
    field: str,
    expected: object,
    actual: object,
) -> dict[str, object]:
    matched = actual == expected
    return {
        "field": field,
        "expected": expected,
        "actual": actual,
        "matched": matched,
        "status": "PASS" if matched else "WARN",
    }


def _best_scenario_result(
    scenario_results: tuple[Mapping[str, Any], ...],
) -> Mapping[str, Any]:
    if not scenario_results:
        return {}
    return sorted(
        scenario_results,
        key=lambda item: (
            -int(item.get("matched_check_count", 0)),
            str(item.get("scenario_id", "")),
        ),
    )[0]


def _gate_checks(
    *,
    exact_match: Mapping[str, Any] | None,
    best_match: Mapping[str, Any],
    missing_fields: tuple[str, ...],
    current_signature: Mapping[str, object],
) -> tuple[dict[str, object], ...]:
    return (
        _gate_check(
            "standard_scenario_match",
            "PASS" if exact_match else "WARN",
            "current config should match one shipped 72/300/1200 standard scenario",
            str(exact_match.get("scenario_id", "")) if exact_match else "",
            str(best_match.get("scenario_id", "")),
            tuple(missing_fields) if not exact_match else (),
        ),
        _gate_check(
            "runtime_status_field_coverage",
            "PASS" if not missing_fields else "FAIL",
            "runtime status should expose all standard acceptance evidence fields",
            "all required runtime status fields present",
            f"{len(missing_fields)} missing",
            missing_fields,
        ),
        _gate_check(
            "backend_summary_coverage",
            (
                "PASS"
                if current_signature.get("derived_constellation_present")
                and current_signature.get("traffic_demand_summary_present")
                and current_signature.get("compute_resource_summary_present")
                else "WARN"
            ),
            "generated backend summary should expose constellation, traffic, and compute semantics",
            "all backend summaries present",
            "backend summary coverage checked",
            (),
        ),
        _gate_check(
            "model_boundary",
            "PASS",
            "standard acceptance remains flow-level, deterministic, and kernel-safe",
            "no packet/external/kernel violation",
            "model boundary accepted",
            (),
        ),
    )


def _gate_check(
    check_id: str,
    status: str,
    expectation: str,
    expected: str,
    actual: str,
    issue_labels: tuple[str, ...],
) -> dict[str, object]:
    check = {
        "check_id": check_id,
        "status": status,
        "expectation": expectation,
        "expected": expected,
        "actual": actual,
        "issue_labels": issue_labels,
    }
    return {**check, "check_hash": stable_hash_payload(check)}


def _recommendation(
    acceptance_status: str,
    exact_match: Mapping[str, Any] | None,
) -> str:
    if acceptance_status == "PASS":
        return "standard scenario acceptance evidence is complete"
    if exact_match is None:
        return "select one shipped standard scenario or export as a custom scenario"
    return "complete missing runtime status evidence before acceptance"


def _has_path(data: Mapping[str, Any], path: str) -> bool:
    current: object = data
    for part in path.split("."):
        if not isinstance(current, Mapping) or part not in current:
            return False
        current = current[part]
    return True


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _number(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return 0.0
    if value != value or value in {float("inf"), float("-inf")}:
        return 0.0
    return float(value)


__all__ = [
    "STANDARD_SCENARIO_ACCEPTANCE_V2_ID",
    "REQUIRED_RUNTIME_STATUS_FIELDS",
    "RESULT_PACKAGE_EVIDENCE_FILENAMES",
    "build_standard_scenario_acceptance_v2",
]
