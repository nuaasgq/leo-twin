"""Product contract and validation helpers for runtime result packages."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from leo_twin.services.benchmark_scenarios import benchmark_scenario_matrix_v1_to_dict
from leo_twin.services.runtime_reproducibility import stable_hash_payload


RESULT_PACKAGE_CONTRACT_V1_ID = "leo_twin.result_package_contract.v1"
RUNTIME_REPRODUCIBILITY_MANIFEST_V1_ID = (
    "leo_twin.runtime_reproducibility_manifest.v1"
)
RUNTIME_EXPORT_REVIEW_SUMMARY_V1_ID = "leo_twin.runtime_export_review_summary.v1"
RUNTIME_EXPORT_DIAGNOSTICS_BUNDLE_V1_ID = (
    "leo_twin.runtime_export_diagnostics_bundle.v1"
)
RUNTIME_EXPORT_SCENARIO_REVIEW_BUNDLE_V1_ID = (
    "leo_twin.runtime_export_scenario_review_bundle.v1"
)
RUNTIME_EXPORT_SCENARIO_REVIEW_CHECKLIST_V1_ID = (
    "leo_twin.runtime_export_scenario_review_checklist.v1"
)
RUNTIME_EXPORT_SCENARIO_REVIEW_CHECKLIST_TEMPLATE_V1_ID = (
    "leo_twin.runtime_export_scenario_review_checklist_template.v1"
)
RUNTIME_EXPORT_SCENARIO_REVIEW_CHECKLIST_TEMPLATE_COMPARISON_V1_ID = (
    "leo_twin.runtime_export_scenario_review_checklist_template_comparison.v1"
)
RUNTIME_EXPORT_ROUTE_DETAIL_INDEX_V1_ID = (
    "leo_twin.runtime_export_route_detail_index.v1"
)
RUNTIME_EXPORT_ROUTE_DETAIL_PAGE_V1_ID = (
    "leo_twin.runtime_export_route_detail_page.v1"
)
RUNTIME_EXPORT_SERVICE_TRACE_PAGE_V1_ID = (
    "leo_twin.runtime_export_service_trace_page.v1"
)
RUNTIME_EXPORT_SERVICE_TRACE_ITEM_V1_ID = (
    "leo_twin.runtime_export_service_trace_item.v1"
)
RUNTIME_EXPORT_REPRODUCIBILITY_BOUNDARY_V1_ID = (
    "leo_twin.runtime_export_reproducibility_boundary.v1"
)
RUNTIME_EXPORT_ROUTE_DETAIL_ITEM_V1_ID = (
    "leo_twin.runtime_export_route_detail_item.v1"
)
RUNTIME_EXPORT_ROUTE_COMPARISON_REVIEW_REPORT_V1_ID = (
    "leo_twin.runtime_export_route_comparison_review_report.v1"
)
RUNTIME_EXPORT_SERVICE_TRACE_COMPARISON_REVIEW_REPORT_V1_ID = (
    "leo_twin.runtime_export_service_trace_comparison_review_report.v1"
)
RUNTIME_EXPORT_SERVICE_TRACE_COMPARISON_REVIEW_REPORT_PAGE_V1_ID = (
    "leo_twin.runtime_export_service_trace_comparison_review_report_page.v1"
)
RUNTIME_EXPORT_PACKAGE_AUDIT_INDEX_V1_ID = (
    "leo_twin.runtime_export_package_audit_index.v1"
)
RUNTIME_EXPORT_PACKAGE_REVIEW_COMPLETION_V1_ID = (
    "leo_twin.runtime_export_package_review_completion.v1"
)
RUNTIME_EXPORT_PACKAGE_HANDOFF_REPORT_V1_ID = (
    "leo_twin.runtime_export_package_handoff_report.v1"
)
RUNTIME_EXPORT_PACKAGE_ACCEPTANCE_REPORT_V1_ID = (
    "leo_twin.runtime_export_package_acceptance_report.v1"
)
RUNTIME_EXPORT_BENCHMARK_ACCEPTANCE_BINDING_V1_ID = (
    "leo_twin.runtime_export_benchmark_acceptance_binding.v1"
)
RUNTIME_EXPORT_NETWORK_KPI_BENCHMARK_VALIDATION_V1_ID = (
    "leo_twin.runtime_export_network_kpi_benchmark_validation.v1"
)
RUNTIME_EXPORT_NETWORK_KPI_FORMULA_EVIDENCE_V1_ID = (
    "leo_twin.runtime_export_network_kpi_formula_evidence.v1"
)
RUNTIME_EXPORT_USER_CONFIGURATION_TEMPLATE_VALIDATION_V1_ID = (
    "leo_twin.runtime_export_user_configuration_template_validation.v1"
)
RUNTIME_EXPORT_TRAFFIC_DEMAND_EXPLANATION_V1_ID = (
    "leo_twin.runtime_export_traffic_demand_explanation.v1"
)
RUNTIME_EXPORT_USER_SERVICE_REQUEST_SUMMARY_V2_ID = (
    "leo_twin.runtime_export_user_service_request_summary.v2"
)
RUNTIME_EXPORT_USER_SERVICE_REQUEST_PAGE_V1_ID = (
    "leo_twin.runtime_export_user_service_request_page.v1"
)
USER_CONFIGURATION_AUDIT_BINDING_V1_ID = (
    "leo_twin.user_configuration_audit_binding.v1"
)
USER_CONFIGURATION_SCHEMA_V2_ID = "sees.user_configuration.v2"
EXPORT_PACKAGE_AUDIT_INDEX_FILENAME = "export_package_audit_index_v1.json"
CONFIG_SNAPSHOT_FILENAME = "config_snapshot.json"
ROUTE_DETAIL_INDEX_FILENAME = "route_detail_index_v1.json"
NETWORK_KPI_BENCHMARK_VALIDATION_FILENAME = (
    "network_kpi_benchmark_validation_v1.json"
)
NETWORK_KPI_FORMULA_EVIDENCE_FILENAME = "network_kpi_formula_evidence_v1.json"
USER_CONFIGURATION_TEMPLATE_VALIDATION_FILENAME = (
    "user_configuration_template_validation_v1.json"
)
TRAFFIC_DEMAND_EXPLANATION_FILENAME = "traffic_demand_explanation_v1.json"


_REQUIRED_FILE_SPECS: tuple[dict[str, object], ...] = (
    {
        "logical_name": "config_snapshot",
        "filename": "config_snapshot.json",
        "format": "json",
        "content": "runtime status, applied SEES config, generated backend config",
    },
    {
        "logical_name": "events",
        "filename": "events.jsonl",
        "format": "jsonl",
        "content": "deterministically ordered processed runtime events",
    },
    {
        "logical_name": "metrics",
        "filename": "metrics.csv",
        "format": "csv",
        "content": "sampled metric records and KPI observations",
    },
    {
        "logical_name": "summary",
        "filename": "summary.json",
        "format": "json",
        "content": "metrics summary and aggregate runtime counters",
    },
    {
        "logical_name": "manifest",
        "filename": "manifest.json",
        "format": "json",
        "content": "runtime reproducibility manifest with stable hashes",
    },
)


def result_package_contract_v1_to_dict() -> dict[str, object]:
    """Return the deterministic product contract for exported result packages."""

    return {
        "contract_id": RESULT_PACKAGE_CONTRACT_V1_ID,
        "version": "v1",
        "package_type": "RUNTIME_EXPORT",
        "source_endpoints": (
            "GET /runtime/export",
            "GET /runtime/export/archive",
            "GET /runtime/export/catalog",
            "GET /runtime/export/packages/{package_id}",
            "GET /runtime/export/packages/{package_id}/manifest",
            "GET /runtime/export/packages/{package_id}/review-summary",
            "GET /runtime/export/packages/{package_id}/review-completion",
            "GET /runtime/export/packages/{package_id}/acceptance-report",
            "GET /runtime/export/packages/{package_id}/handoff-report",
            "GET /runtime/export/packages/{package_id}/service-traces",
            "GET /runtime/export/packages/{package_id}/service-traces/{trace_id}",
            "GET /runtime/export/packages/{package_id}/user-service-requests",
            "GET /runtime/export/packages/{package_id}/routes",
            "GET /runtime/export/packages/{package_id}/routes/{route_id}",
            "POST /runtime/export/packages/{package_id}/route-comparison-review-report",
            "POST /runtime/export/packages/{package_id}/service-trace-comparison-review-report",
            "GET /runtime/export/packages/{package_id}/scenario-review-checklist-template",
            "GET /runtime/export/packages/{package_id}/scenario-review-checklist-template-comparison",
            "POST /runtime/export/packages/{package_id}/scenario-review-checklist",
            "GET /runtime/export/packages/{package_id}/files/{filename}",
        ),
        "catalog_filename": "runtime_export_catalog_v1.json",
        "required_files": _REQUIRED_FILE_SPECS,
        "required_file_count": len(_REQUIRED_FILE_SPECS),
        "recommended_files": (
            {
                "logical_name": "service_lifecycle_trace_v2",
                "filename": "service_lifecycle_trace_v2.json",
                "format": "json",
                "content": "communication-compute lifecycle trace for offline review",
            },
            {
                "logical_name": "user_service_request_summary_v2",
                "filename": "user_service_request_summary_v2.json",
                "format": "json",
                "content": (
                    "backend-owned per-user communication/compute request "
                    "state window for offline dashboard review"
                ),
            },
            {
                "logical_name": "route_detail_index_v1",
                "filename": "route_detail_index_v1.json",
                "format": "json",
                "content": "indexed route explanation rows for route trust review",
            },
            {
                "logical_name": "review_summary_v1",
                "filename": "review_summary_v1.json",
                "format": "json",
                "content": "user-readable package summary and review readiness",
            },
            {
                "logical_name": "diagnostics_bundle_v1",
                "filename": "diagnostics_bundle_v1.json",
                "format": "json",
                "content": (
                    "deterministic result-package diagnostics, artifact health, "
                    "and operator next actions"
                ),
            },
            {
                "logical_name": "network_kpi_benchmark_validation_v1",
                "filename": "network_kpi_benchmark_validation_v1.json",
                "format": "json",
                "content": (
                    "runtime network KPI benchmark guardrail evidence exported "
                    "for offline review"
                ),
            },
            {
                "logical_name": "network_kpi_formula_evidence_v1",
                "filename": "network_kpi_formula_evidence_v1.json",
                "format": "json",
                "content": (
                    "runtime network KPI formula input and time-series evidence "
                    "exported for offline review"
                ),
            },
            {
                "logical_name": "user_configuration_template_validation_v1",
                "filename": "user_configuration_template_validation_v1.json",
                "format": "json",
                "content": (
                    "backend-owned approved user configuration template "
                    "validation evidence exported for offline review"
                ),
            },
            {
                "logical_name": "traffic_demand_explanation_v1",
                "filename": "traffic_demand_explanation_v1.json",
                "format": "json",
                "content": (
                    "backend-owned generated traffic-demand explanation "
                    "exported for offline business-request review"
                ),
            },
            {
                "logical_name": "scenario_review_bundle_v1",
                "filename": "scenario_review_bundle_v1.json",
                "format": "json",
                "content": (
                    "operator scenario review entry that binds user "
                    "configuration, reproducibility, diagnostics, and audit "
                    "evidence"
                ),
            },
            {
                "logical_name": "export_package_audit_index_v1",
                "filename": "export_package_audit_index_v1.json",
                "format": "json",
                "content": (
                    "long-term package audit index for manifest, boundary, "
                    "diagnostics, user configuration, review report, and "
                    "artifact hashes"
                ),
            },
            {
                "logical_name": "package_handoff_report_v1",
                "filename": "package_handoff_report_v1.md",
                "format": "markdown",
                "content": (
                    "operator-facing handoff report derived from backend "
                    "package review completion evidence"
                ),
            },
        ),
        "required_manifest_id": RUNTIME_REPRODUCIBILITY_MANIFEST_V1_ID,
        "hash_policy": {
            "file_hash": "sha256 over artifact bytes",
            "manifest_hash": "stable canonical JSON hash",
            "catalog_hash_source": "catalog records include file hashes",
        },
        "archive_policy": {
            "format": "zip",
            "deterministic_entry_timestamp": "2026-01-01T00:00:00",
            "entry_order": "filename ascending",
        },
        "restore_policy": {
            "restore_scope": "configuration restore through control plane",
            "rollback_export": "write rollback package before applying restore",
            "event_replay": "not applied to live runtime in v1",
        },
        "reproducibility_boundary_id": (
            RUNTIME_EXPORT_REPRODUCIBILITY_BOUNDARY_V1_ID
        ),
        "benchmark_binding": {
            "matrix_id": "leo_twin.benchmark_scenario_matrix.v1",
            "verification_template_id": "leo_twin.model_verification_report_template.v1",
            "evidence_role": (
                "A benchmark run result package should provide config, events, "
                "metrics, summary, and manifest evidence for review."
            ),
        },
        "excluded_semantics": (
            "PACKET_CAPTURE",
            "BINARY_TRACE_FORMAT",
            "EXTERNAL_SIMULATOR_ARTIFACT",
            "LIVE_EVENT_REPLAY_RESTORE",
        ),
    }


def build_runtime_export_reproducibility_boundary_v1(
    *,
    runtime_status: Mapping[str, Any],
    manifest: Mapping[str, Any],
) -> dict[str, object]:
    """Build the unified reproducibility boundary for runtime result packages."""

    if not isinstance(runtime_status, Mapping):
        raise TypeError("runtime_status must be a mapping")
    if not isinstance(manifest, Mapping):
        raise TypeError("manifest must be a mapping")

    route_policy = _mapping(runtime_status.get("runtime_export_route_detail_policy_v1"))
    service_policy = _mapping(
        runtime_status.get("runtime_export_service_trace_policy_v1")
    )
    user_service_policy = _mapping(
        runtime_status.get("runtime_export_user_service_request_policy_v1")
    )
    boundary: dict[str, object] = {
        "type": "RUNTIME_EXPORT_REPRODUCIBILITY_BOUNDARY_V1",
        "version": "v1",
        "boundary_id": RUNTIME_EXPORT_REPRODUCIBILITY_BOUNDARY_V1_ID,
        "source": "BACKEND_RUNTIME_EXPORT",
        "boundary_scope": "RESULT_PACKAGE_REPRODUCIBILITY_AND_RESTORE_BOUNDARY",
        "manifest_id": str(manifest.get("manifest_id", "")),
        "control_config_hash": str(manifest.get("control_config_hash", "")),
        "generated_config_hash": str(manifest.get("generated_config_hash", "")),
        "runtime_state_hash": str(manifest.get("runtime_state_hash", "")),
        "metrics_summary_hash": str(manifest.get("metrics_summary_hash", "")),
        "deterministic_replay_evidence": True,
        "runtime_deterministic_replay_enabled": _bool(
            manifest.get("deterministic_replay")
        ),
        "restore_scope": "CONFIG_ONLY",
        "compare_scope": "CONFIG_AND_GENERATED_CONFIG",
        "read_scope": "PERSISTED_ARTIFACTS_ONLY",
        "event_kernel_policy": "NO_EVENT_KERNEL_BEHAVIOR_CHANGE",
        "event_replay_restore": False,
        "live_event_replay_restore": False,
        "recompute_on_read": False,
        "route_recomputation": False,
        "service_recomputation": False,
        "package_mutation_on_read": False,
        "packet_capture": False,
        "packet_level_simulation": False,
        "external_simulators": False,
        "forbidden_external_integrations": ("STK", "EXATA", "AFSIM", "DDS"),
        "required_evidence_artifacts": (
            "config_snapshot.json",
            "events.jsonl",
            "metrics.csv",
            "summary.json",
            "manifest.json",
        ),
        "optional_evidence_artifacts": (
            "service_lifecycle_trace_v2.json",
            "route_detail_index_v1.json",
            "review_summary_v1.json",
            "diagnostics_bundle_v1.json",
            "network_kpi_benchmark_validation_v1.json",
            "network_kpi_formula_evidence_v1.json",
            "user_configuration_template_validation_v1.json",
            "traffic_demand_explanation_v1.json",
            "user_service_request_summary_v2.json",
            "scenario_review_bundle_v1.json",
        ),
        "route_detail_export": {
            "policy": str(route_policy.get("policy", "")),
            "route_detail_limit": _integer(route_policy.get("route_detail_limit")),
            "route_count": _integer(route_policy.get("route_count")),
            "indexed_route_count": _integer(route_policy.get("indexed_route_count")),
            "hidden_route_count": _integer(route_policy.get("hidden_route_count")),
            "artifact_window_only": True,
        },
        "service_trace_export": {
            "policy": str(service_policy.get("policy", "")),
            "service_trace_limit": _integer(service_policy.get("service_trace_limit")),
            "service_count": _integer(service_policy.get("service_count")),
            "exported_trace_count": _integer(
                service_policy.get("exported_trace_count")
            ),
            "hidden_trace_count": _integer(service_policy.get("hidden_trace_count")),
            "artifact_window_only": True,
        },
        "user_service_request_export": {
            "policy": str(user_service_policy.get("policy", "")),
            "user_service_request_limit": _integer(
                user_service_policy.get("user_service_request_limit")
            ),
            "request_count": _integer(user_service_policy.get("request_count")),
            "exported_request_count": _integer(
                user_service_policy.get("exported_request_count")
            ),
            "hidden_request_count": _integer(
                user_service_policy.get("hidden_request_count")
            ),
            "artifact_window_only": True,
        },
        "boundary_conditions": (
            "DETERMINISTIC_ARTIFACT_REPLAY_EVIDENCE",
            "CONFIG_ONLY_RESTORE",
            "CONFIG_AND_GENERATED_CONFIG_COMPARE",
            "PERSISTED_ARTIFACTS_ONLY_READ",
            "NO_LIVE_EVENT_REPLAY_RESTORE",
            "NO_RECOMPUTE_ON_COMPARE_OR_READ",
            "NO_PACKAGE_MUTATION_ON_READ",
            "NO_PACKET_CAPTURE",
            "NO_PACKET_LEVEL_SIMULATION",
            "NO_EXTERNAL_SIMULATOR_ARTIFACT",
        ),
    }
    boundary["boundary_hash"] = stable_hash_payload(boundary)
    return boundary


def build_runtime_export_network_kpi_benchmark_validation_v1(
    *,
    package_id: str,
    package_dir: str,
    config_snapshot: Mapping[str, Any],
) -> dict[str, object]:
    """Build offline review evidence for runtime network KPI guardrails."""

    if not isinstance(config_snapshot, Mapping):
        raise TypeError("config_snapshot must be a mapping")

    status = _mapping(config_snapshot.get("status"))
    validation = _mapping(status.get("network_kpi_benchmark_validation_v1"))
    evidence = _runtime_export_network_kpi_validation_evidence(status)
    artifact: dict[str, object] = {
        "type": "RUNTIME_EXPORT_NETWORK_KPI_BENCHMARK_VALIDATION_V1",
        "version": "v1",
        "artifact_id": RUNTIME_EXPORT_NETWORK_KPI_BENCHMARK_VALIDATION_V1_ID,
        "source": "BACKEND_RUNTIME_EXPORT",
        "artifact_scope": "NETWORK_KPI_BENCHMARK_GUARDRAIL_REVIEW",
        "package_id": str(package_id),
        "package_dir": str(package_dir),
        "runtime_status_field": "network_kpi_benchmark_validation_v1",
        "validation": dict(validation),
        "evidence": evidence,
        "boundary_conditions": (
            "READ_RUNTIME_STATUS_ONLY",
            "NO_METRIC_RECOMPUTE",
            "NO_EVENT_REPLAY",
            "NO_PACKET_LEVEL_SIMULATION",
            "NO_EXTERNAL_SIMULATOR_ARTIFACT",
        ),
    }
    artifact["artifact_hash"] = stable_hash_payload(artifact)
    return artifact


def build_runtime_export_network_kpi_formula_evidence_v1(
    *,
    package_id: str,
    package_dir: str,
    config_snapshot: Mapping[str, Any],
) -> dict[str, object]:
    """Build offline review evidence for runtime network KPI formula inputs."""

    if not isinstance(config_snapshot, Mapping):
        raise TypeError("config_snapshot must be a mapping")

    status = _mapping(config_snapshot.get("status"))
    formula_evidence = _mapping(status.get("network_kpi_formula_evidence_v1"))
    evidence = _runtime_export_network_kpi_formula_evidence(status)
    artifact: dict[str, object] = {
        "type": "RUNTIME_EXPORT_NETWORK_KPI_FORMULA_EVIDENCE_V1",
        "version": "v1",
        "artifact_id": RUNTIME_EXPORT_NETWORK_KPI_FORMULA_EVIDENCE_V1_ID,
        "source": "BACKEND_RUNTIME_EXPORT",
        "artifact_scope": "NETWORK_KPI_FORMULA_INPUT_TIME_SERIES_REVIEW",
        "package_id": str(package_id),
        "package_dir": str(package_dir),
        "runtime_status_field": "network_kpi_formula_evidence_v1",
        "formula_evidence": dict(formula_evidence),
        "evidence": evidence,
        "boundary_conditions": (
            "READ_RUNTIME_STATUS_ONLY",
            "NO_METRIC_RECOMPUTE",
            "NO_EVENT_REPLAY",
            "NO_PACKET_LEVEL_SIMULATION",
            "NO_EXTERNAL_SIMULATOR_ARTIFACT",
        ),
    }
    artifact["artifact_hash"] = stable_hash_payload(artifact)
    return artifact


def build_runtime_export_user_configuration_template_validation_v1(
    *,
    package_id: str,
    package_dir: str,
    config_snapshot: Mapping[str, Any],
) -> dict[str, object]:
    """Build offline review evidence for approved user configuration templates."""

    if not isinstance(config_snapshot, Mapping):
        raise TypeError("config_snapshot must be a mapping")

    template_validation = _mapping(
        config_snapshot.get("user_configuration_template_validation_v1")
    )
    evidence = _runtime_export_user_configuration_template_validation_evidence(
        config_snapshot
    )
    artifact: dict[str, object] = {
        "type": "RUNTIME_EXPORT_USER_CONFIGURATION_TEMPLATE_VALIDATION_V1",
        "version": "v1",
        "artifact_id": RUNTIME_EXPORT_USER_CONFIGURATION_TEMPLATE_VALIDATION_V1_ID,
        "source": "BACKEND_RUNTIME_EXPORT",
        "artifact_scope": "USER_CONFIGURATION_TEMPLATE_VALIDATION_REVIEW",
        "package_id": str(package_id),
        "package_dir": str(package_dir),
        "config_snapshot_field": "user_configuration_template_validation_v1",
        "template_validation": dict(template_validation),
        "evidence": evidence,
        "boundary_conditions": (
            "READ_CONFIG_SNAPSHOT_ONLY",
            "NO_TEMPLATE_RELOAD",
            "NO_CONFIG_APPLY",
            "NO_EVENT_REPLAY",
            "NO_PACKET_LEVEL_SIMULATION",
            "NO_EXTERNAL_SIMULATOR_ARTIFACT",
        ),
    }
    artifact["artifact_hash"] = stable_hash_payload(artifact)
    return artifact


def build_runtime_export_traffic_demand_explanation_v1(
    *,
    package_id: str,
    package_dir: str,
    config_snapshot: Mapping[str, Any],
) -> dict[str, object]:
    """Build offline review evidence for backend traffic-demand semantics."""

    if not isinstance(config_snapshot, Mapping):
        raise TypeError("config_snapshot must be a mapping")

    generated_config = _mapping(config_snapshot.get("generated_config"))
    backend_summary = _mapping(generated_config.get("backend_summary"))
    explanation = _mapping(backend_summary.get("traffic_demand_explanation_v1"))
    evidence = _runtime_export_traffic_demand_explanation_evidence(config_snapshot)
    artifact: dict[str, object] = {
        "type": "RUNTIME_EXPORT_TRAFFIC_DEMAND_EXPLANATION_V1",
        "version": "v1",
        "artifact_id": RUNTIME_EXPORT_TRAFFIC_DEMAND_EXPLANATION_V1_ID,
        "source": "BACKEND_RUNTIME_EXPORT",
        "artifact_scope": "TRAFFIC_DEMAND_BUSINESS_SEMANTICS_REVIEW",
        "package_id": str(package_id),
        "package_dir": str(package_dir),
        "config_snapshot_field": (
            "generated_config.backend_summary.traffic_demand_explanation_v1"
        ),
        "artifact_policy": "STANDALONE_RUNTIME_EXPORT_ARTIFACT",
        "traffic_demand_explanation": dict(explanation),
        "evidence": evidence,
        "boundary_conditions": (
            "READ_GENERATED_CONFIG_ONLY",
            "NO_TRAFFIC_REGENERATION",
            "NO_EVENT_REPLAY",
            "NO_PACKET_LEVEL_SIMULATION",
            "NO_EXTERNAL_SIMULATOR_ARTIFACT",
        ),
    }
    artifact["artifact_hash"] = stable_hash_payload(artifact)
    return artifact


def build_runtime_export_user_service_request_summary_v2(
    *,
    package_id: str,
    package_dir: str,
    config_snapshot: Mapping[str, Any],
) -> dict[str, object]:
    """Build offline review evidence for runtime user service request state."""

    if not isinstance(config_snapshot, Mapping):
        raise TypeError("config_snapshot must be a mapping")

    status = _mapping(config_snapshot.get("status"))
    summary = _mapping(status.get("user_service_request_summary_v2"))
    policy = _mapping(status.get("runtime_export_user_service_request_policy_v1"))
    artifact: dict[str, object] = {
        "type": "RUNTIME_EXPORT_USER_SERVICE_REQUEST_SUMMARY_V2",
        "version": "v2",
        "artifact_id": RUNTIME_EXPORT_USER_SERVICE_REQUEST_SUMMARY_V2_ID,
        "source": "BACKEND_RUNTIME_EXPORT",
        "artifact_scope": "USER_SERVICE_REQUEST_OFFLINE_REVIEW",
        "package_id": str(package_id),
        "package_dir": str(package_dir),
        "runtime_status_field": "user_service_request_summary_v2",
        "artifact_policy": "STANDALONE_RUNTIME_EXPORT_ARTIFACT",
        "artifact_window_only": True,
        "summary": dict(summary),
        "user_service_request_export_policy": dict(policy),
        "evidence": _runtime_export_user_service_request_evidence(status),
        "boundary_conditions": (
            "READ_RUNTIME_STATUS_ONLY",
            "NO_SERVICE_RECOMPUTE",
            "NO_EVENT_REPLAY",
            "NO_PACKET_LEVEL_SIMULATION",
            "NO_EXTERNAL_SIMULATOR_ARTIFACT",
        ),
    }
    artifact["artifact_hash"] = stable_hash_payload(artifact)
    return artifact


def build_runtime_export_review_summary_v1(
    *,
    package_id: str,
    package_dir: str,
    config_snapshot: Mapping[str, Any],
    manifest: Mapping[str, Any],
    artifact_filenames: tuple[str, ...],
) -> dict[str, object]:
    """Build a deterministic user-facing review summary for a result package."""

    if not isinstance(config_snapshot, Mapping):
        raise TypeError("config_snapshot must be a mapping")
    if not isinstance(manifest, Mapping):
        raise TypeError("manifest must be a mapping")

    contract = result_package_contract_v1_to_dict()
    status = _mapping(config_snapshot.get("status"))
    config = _mapping(config_snapshot.get("config"))
    generated_config = _mapping(config_snapshot.get("generated_config"))
    required_filenames = tuple(
        str(spec["filename"]) for spec in contract["required_files"]  # type: ignore[index]
    )
    artifacts = tuple(sorted(str(filename) for filename in artifact_filenames))
    missing_required = tuple(
        filename for filename in required_filenames if filename not in artifacts
    )
    review_status = (
        "REVIEW_READY"
        if not missing_required
        and str(manifest.get("manifest_id", ""))
        == RUNTIME_REPRODUCIBILITY_MANIFEST_V1_ID
        else "INCOMPLETE"
    )
    route_trust = _runtime_export_route_trust_evidence(status)
    network_kpi_validation = _runtime_export_network_kpi_validation_evidence(status)
    network_kpi_formula_evidence = _runtime_export_network_kpi_formula_evidence(
        status
    )
    user_config_template_validation = (
        _runtime_export_user_configuration_template_validation_evidence(
            config_snapshot
        )
    )
    traffic_demand_explanation = _runtime_export_traffic_demand_explanation_evidence(
        config_snapshot
    )
    user_service_requests = _runtime_export_user_service_request_evidence(status)
    route_comparison_review = _runtime_export_route_comparison_review_metadata()
    reproducibility_boundary = _runtime_export_reproducibility_boundary(
        status,
        manifest,
    )
    summary: dict[str, object] = {
        "type": "RUNTIME_EXPORT_REVIEW_SUMMARY_V1",
        "version": "v1",
        "summary_id": RUNTIME_EXPORT_REVIEW_SUMMARY_V1_ID,
        "source": "BACKEND_RUNTIME_EXPORT",
        "summary_scope": "USER_READABLE_RESULT_PACKAGE_REVIEW",
        "package_id": str(package_id),
        "package_dir": str(package_dir),
        "review_status": review_status,
        "scenario": {
            "seed": _value(generated_config, "seed", _value(config, "seed", 0)),
            "satellite_count": _value(
                generated_config,
                "satellite_count",
                _value(config, "satellite_count", 0),
            ),
            "user_count": _value(
                generated_config,
                "ground_user_count",
                _value(generated_config, "user_count", _value(config, "user_count", 0)),
            ),
            "compute_node_count": _value(
                generated_config,
                "compute_node_count",
                _value(config, "compute_node_count", 0),
            ),
            "duration_seconds": _value(
                generated_config,
                "duration_seconds",
                _value(config, "duration_seconds", 0),
            ),
        },
        "runtime": {
            "lifecycle_state": str(status.get("lifecycle_state", "")),
            "current_sim_time": _number(status.get("current_sim_time")),
            "processed_event_count": _integer(status.get("processed_event_count")),
            "queued_event_count": _integer(status.get("queued_event_count")),
        },
        "route_trust": route_trust,
        "network_kpi_benchmark_validation": network_kpi_validation,
        "network_kpi_formula_evidence": network_kpi_formula_evidence,
        "user_configuration_template_validation": user_config_template_validation,
        "traffic_demand_explanation": traffic_demand_explanation,
        "user_service_requests": user_service_requests,
        "route_comparison_review": route_comparison_review,
        "reproducibility": {
            "manifest_id": str(manifest.get("manifest_id", "")),
            "manifest_hash": str(manifest.get("manifest_hash", "")),
            "config_hash": str(manifest.get("config_hash", "")),
            "control_config_hash": str(manifest.get("control_config_hash", "")),
            "generated_config_hash": str(manifest.get("generated_config_hash", "")),
            "runtime_state_hash": str(manifest.get("runtime_state_hash", "")),
            "boundary_hash": str(reproducibility_boundary.get("boundary_hash", "")),
            "event_kernel_policy": "NO_EVENT_KERNEL_BEHAVIOR_CHANGE",
        },
        "reproducibility_boundary": reproducibility_boundary,
        "artifacts": {
            "artifact_count": len(artifacts),
            "artifact_filenames": artifacts,
            "required_filenames": required_filenames,
            "missing_required_filenames": missing_required,
            "service_lifecycle_trace_exported": (
                "service_lifecycle_trace_v2.json" in artifacts
            ),
            "review_summary_exported": "review_summary_v1.json" in artifacts,
            "network_kpi_benchmark_validation_exported": (
                "network_kpi_benchmark_validation_v1.json" in artifacts
            ),
            "network_kpi_formula_evidence_exported": (
                "network_kpi_formula_evidence_v1.json" in artifacts
            ),
            "user_configuration_template_validation_exported": (
                "user_configuration_template_validation_v1.json" in artifacts
            ),
            "traffic_demand_explanation_exported": (
                "traffic_demand_explanation_v1.json" in artifacts
            ),
            "user_service_request_summary_exported": (
                "user_service_request_summary_v2.json" in artifacts
            ),
        },
        "review_notes": (
            "Use manifest.json and config_snapshot.json to verify deterministic inputs.",
            "Use events.jsonl, metrics.csv, and summary.json as replay evidence.",
            "Use service_lifecycle_trace_v2.json for communication-compute trace review.",
            "Use user_service_request_summary_v2.json for per-user business request state review.",
            "Use route_trust to inspect flow-level route explanation evidence.",
            "Use network_kpi_benchmark_validation_v1.json to review KPI guardrail evidence.",
            "Use network_kpi_formula_evidence_v1.json to review KPI formula input and time-series evidence.",
            "Use user_configuration_template_validation_v1.json to review approved configuration template validation evidence.",
            "Use traffic_demand_explanation_v1.json to review backend-owned business request generation semantics.",
            "Use route_detail_index_v1.json to inspect exported route explanation rows.",
            "Use route_comparison_review to compare exported route rows with the current live runtime when available.",
            "This package does not contain packet captures or external simulator artifacts.",
        ),
    }
    summary["summary_hash"] = stable_hash_payload(summary)
    return summary


def build_runtime_export_diagnostics_bundle_v1(
    *,
    package_id: str,
    package_dir: str,
    config_snapshot: Mapping[str, Any],
    manifest: Mapping[str, Any],
    review_summary: Mapping[str, Any],
    artifact_filenames: tuple[str, ...],
) -> dict[str, object]:
    """Build a deterministic diagnostics index for a runtime result package."""

    if not isinstance(config_snapshot, Mapping):
        raise TypeError("config_snapshot must be a mapping")
    if not isinstance(manifest, Mapping):
        raise TypeError("manifest must be a mapping")
    if not isinstance(review_summary, Mapping):
        raise TypeError("review_summary must be a mapping")

    contract = result_package_contract_v1_to_dict()
    status = _mapping(config_snapshot.get("status"))
    required_filenames = _contract_filenames(contract, "required_files")
    recommended_filenames = _contract_filenames(contract, "recommended_files")
    artifacts = tuple(sorted(str(filename) for filename in artifact_filenames))
    present_required = tuple(
        filename for filename in required_filenames if filename in artifacts
    )
    missing_required = tuple(
        filename for filename in required_filenames if filename not in artifacts
    )
    present_recommended = tuple(
        filename for filename in recommended_filenames if filename in artifacts
    )
    missing_recommended = tuple(
        filename for filename in recommended_filenames if filename not in artifacts
    )
    manifest_id = str(manifest.get("manifest_id", ""))
    manifest_ok = manifest_id == RUNTIME_REPRODUCIBILITY_MANIFEST_V1_ID
    review_status = str(review_summary.get("review_status", ""))
    package_complete = manifest_ok and not missing_required
    route_trust = _runtime_export_route_trust_evidence(status)
    network_kpi_validation = _runtime_export_network_kpi_validation_evidence(status)
    network_kpi_formula_evidence = _runtime_export_network_kpi_formula_evidence(
        status
    )
    user_config_template_validation = (
        _runtime_export_user_configuration_template_validation_evidence(
            config_snapshot
        )
    )
    traffic_demand_explanation = _runtime_export_traffic_demand_explanation_evidence(
        config_snapshot
    )
    user_service_requests = _runtime_export_user_service_request_evidence(status)
    route_comparison_review = _runtime_export_route_comparison_review_metadata()
    reproducibility_boundary = _runtime_export_reproducibility_boundary(
        status,
        manifest,
    )
    findings = _runtime_export_diagnostic_findings(
        manifest_ok=manifest_ok,
        review_status=review_status,
        missing_required=missing_required,
        missing_recommended=missing_recommended,
        route_trust=route_trust,
        network_kpi_validation=network_kpi_validation,
        network_kpi_formula_evidence=network_kpi_formula_evidence,
        user_config_template_validation=user_config_template_validation,
        traffic_demand_explanation=traffic_demand_explanation,
        user_service_requests=user_service_requests,
    )
    diagnostics: dict[str, object] = {
        "type": "RUNTIME_EXPORT_DIAGNOSTICS_BUNDLE_V1",
        "version": "v1",
        "bundle_id": RUNTIME_EXPORT_DIAGNOSTICS_BUNDLE_V1_ID,
        "source": "BACKEND_RUNTIME_EXPORT",
        "diagnostics_scope": "RESULT_PACKAGE_OPERATOR_REVIEW",
        "package": {
            "package_id": str(package_id),
            "package_dir": str(package_dir),
            "package_complete": package_complete,
            "review_status": review_status,
            "contract_id": RESULT_PACKAGE_CONTRACT_V1_ID,
        },
        "runtime": {
            "lifecycle_state": str(status.get("lifecycle_state", "")),
            "current_sim_time": _number(status.get("current_sim_time")),
            "processed_event_count": _integer(status.get("processed_event_count")),
            "queued_event_count": _integer(status.get("queued_event_count")),
        },
        "route_trust": route_trust,
        "network_kpi_benchmark_validation": network_kpi_validation,
        "network_kpi_formula_evidence": network_kpi_formula_evidence,
        "user_configuration_template_validation": user_config_template_validation,
        "traffic_demand_explanation": traffic_demand_explanation,
        "user_service_requests": user_service_requests,
        "route_comparison_review": route_comparison_review,
        "reproducibility": {
            "manifest_id": manifest_id,
            "manifest_ok": manifest_ok,
            "manifest_hash": str(manifest.get("manifest_hash", "")),
            "config_hash": str(manifest.get("config_hash", "")),
            "control_config_hash": str(manifest.get("control_config_hash", "")),
            "generated_config_hash": str(manifest.get("generated_config_hash", "")),
            "runtime_state_hash": str(manifest.get("runtime_state_hash", "")),
            "review_summary_hash": str(review_summary.get("summary_hash", "")),
            "boundary_hash": str(reproducibility_boundary.get("boundary_hash", "")),
        },
        "reproducibility_boundary": reproducibility_boundary,
        "artifact_health": {
            "artifact_count": len(artifacts),
            "artifact_filenames": artifacts,
            "required_filenames": required_filenames,
            "recommended_filenames": recommended_filenames,
            "present_required_filenames": present_required,
            "missing_required_filenames": missing_required,
            "present_recommended_filenames": present_recommended,
            "missing_recommended_filenames": missing_recommended,
        },
        "model_boundaries": {
            "event_kernel_policy": "NO_EVENT_KERNEL_BEHAVIOR_CHANGE",
            "packet_level_simulation": False,
            "external_simulators": (),
            "forbidden_external_integrations": ("STK", "EXATA", "AFSIM", "DDS"),
            "event_replay_restore": False,
            "route_recomputation": False,
            "service_recomputation": False,
            "diagnostics_policy": (
                "Deterministic package index only; no event replay or packet capture."
            ),
        },
        "findings": findings,
        "finding_count": len(findings),
        "recommended_next_actions": _runtime_export_diagnostic_next_actions(
            package_complete=package_complete,
            missing_recommended=missing_recommended,
        ),
    }
    diagnostics["diagnostics_hash"] = stable_hash_payload(diagnostics)
    return diagnostics


def build_runtime_export_scenario_review_bundle_v1(
    *,
    package_id: str,
    package_dir: str,
    config_snapshot: Mapping[str, Any],
    manifest: Mapping[str, Any],
    review_summary: Mapping[str, Any],
    diagnostics_bundle: Mapping[str, Any],
    user_configuration_export: Mapping[str, Any] | None = None,
    artifact_filenames: tuple[str, ...] = (),
) -> dict[str, object]:
    """Build a deterministic operator entry point for scenario review."""

    if not isinstance(config_snapshot, Mapping):
        raise TypeError("config_snapshot must be a mapping")
    if not isinstance(manifest, Mapping):
        raise TypeError("manifest must be a mapping")
    if not isinstance(review_summary, Mapping):
        raise TypeError("review_summary must be a mapping")
    if not isinstance(diagnostics_bundle, Mapping):
        raise TypeError("diagnostics_bundle must be a mapping")

    status = _mapping(config_snapshot.get("status"))
    user_config_binding = _runtime_export_user_configuration_audit_binding(
        config_snapshot,
        user_configuration_export,
    )
    reproducibility_boundary = _runtime_export_reproducibility_boundary(
        status,
        manifest,
    )
    findings = _records(diagnostics_bundle.get("findings"))
    finding_labels = tuple(
        {
            "severity": str(finding.get("severity", "")),
            "code": str(finding.get("code", "")),
        }
        for finding in findings
    )
    scenario_review_warnings: list[str] = []
    if user_config_binding["validation_ok"] is not True:
        scenario_review_warnings.append("USER_CONFIGURATION_NOT_VALIDATED")
    if str(review_summary.get("review_status", "")) != "REVIEW_READY":
        scenario_review_warnings.append("REVIEW_SUMMARY_NOT_READY")
    if any(str(item.get("severity", "")) == "ERROR" for item in findings):
        scenario_review_warnings.append("DIAGNOSTICS_HAS_ERROR_FINDINGS")
    network_kpi_validation = _mapping(
        review_summary.get("network_kpi_benchmark_validation")
    )
    network_kpi_formula_evidence = _mapping(
        review_summary.get("network_kpi_formula_evidence")
    )
    user_config_template_validation = _mapping(
        review_summary.get("user_configuration_template_validation")
    )
    traffic_demand_explanation = _mapping(
        review_summary.get("traffic_demand_explanation")
    )
    user_service_requests = _mapping(review_summary.get("user_service_requests"))
    if user_service_requests.get("evidence_present") is not True:
        scenario_review_warnings.append("USER_SERVICE_REQUEST_SUMMARY_MISSING")
    if network_kpi_formula_evidence.get("evidence_present") is not True:
        scenario_review_warnings.append("NETWORK_KPI_FORMULA_EVIDENCE_MISSING")
    if user_config_template_validation.get("evidence_present") is not True:
        scenario_review_warnings.append(
            "USER_CONFIGURATION_TEMPLATE_VALIDATION_MISSING"
        )
    if traffic_demand_explanation.get("evidence_present") is not True:
        scenario_review_warnings.append("TRAFFIC_DEMAND_EXPLANATION_MISSING")

    bundle: dict[str, object] = {
        "type": "RUNTIME_EXPORT_SCENARIO_REVIEW_BUNDLE_V1",
        "version": "v1",
        "bundle_id": RUNTIME_EXPORT_SCENARIO_REVIEW_BUNDLE_V1_ID,
        "source": "BACKEND_RUNTIME_EXPORT_PACKAGE",
        "review_scope": "USER_CONFIGURATION_TO_RESULT_PACKAGE_REVIEW",
        "package_id": str(package_id),
        "package_dir": str(package_dir),
        "scenario": dict(_mapping(review_summary.get("scenario"))),
        "runtime": dict(_mapping(review_summary.get("runtime"))),
        "user_configuration": user_config_binding,
        "reproducibility": {
            "manifest_id": str(manifest.get("manifest_id", "")),
            "manifest_hash": str(manifest.get("manifest_hash", "")),
            "control_config_hash": str(manifest.get("control_config_hash", "")),
            "generated_config_hash": str(manifest.get("generated_config_hash", "")),
            "runtime_state_hash": str(manifest.get("runtime_state_hash", "")),
            "metrics_summary_hash": str(manifest.get("metrics_summary_hash", "")),
            "runtime_export_boundary_hash": str(
                reproducibility_boundary.get("boundary_hash", "")
            ),
        },
        "review_summary": {
            "summary_id": str(review_summary.get("summary_id", "")),
            "summary_hash": str(review_summary.get("summary_hash", "")),
            "review_status": str(review_summary.get("review_status", "")),
        },
        "diagnostics": {
            "bundle_id": str(diagnostics_bundle.get("bundle_id", "")),
            "diagnostics_hash": str(diagnostics_bundle.get("diagnostics_hash", "")),
            "finding_count": len(findings),
            "finding_labels": finding_labels,
        },
        "network_kpi_benchmark_validation": {
            "validation_id": str(network_kpi_validation.get("validation_id", "")),
            "benchmark_profile": str(
                network_kpi_validation.get("benchmark_profile", "")
            ),
            "validation_status": str(
                network_kpi_validation.get("validation_status", "")
            ),
            "failed_check_count": _integer(
                network_kpi_validation.get("failed_check_count")
            ),
            "validation_hash": str(network_kpi_validation.get("validation_hash", "")),
            "evidence_present": network_kpi_validation.get("evidence_present") is True,
        },
        "network_kpi_formula_evidence": {
            "evidence_id": str(network_kpi_formula_evidence.get("evidence_id", "")),
            "metric_model": str(network_kpi_formula_evidence.get("metric_model", "")),
            "formula_evidence_status": str(
                network_kpi_formula_evidence.get("formula_evidence_status", "")
            ),
            "kpi_count": _integer(network_kpi_formula_evidence.get("kpi_count")),
            "observed_kpi_count": _integer(
                network_kpi_formula_evidence.get("observed_kpi_count")
            ),
            "missing_selected_input_count": _integer(
                network_kpi_formula_evidence.get("missing_selected_input_count")
            ),
            "time_varying_kpi_count": _integer(
                network_kpi_formula_evidence.get("time_varying_kpi_count")
            ),
            "evidence_hash": str(
                network_kpi_formula_evidence.get("evidence_hash", "")
            ),
            "evidence_present": (
                network_kpi_formula_evidence.get("evidence_present") is True
            ),
        },
        "user_configuration_template_validation": {
            "evidence_id": str(user_config_template_validation.get("evidence_id", "")),
            "schema_id": str(user_config_template_validation.get("schema_id", "")),
            "validation_status": str(
                user_config_template_validation.get("validation_status", "")
            ),
            "template_count": _integer(
                user_config_template_validation.get("template_count")
            ),
            "valid_template_count": _integer(
                user_config_template_validation.get("valid_template_count")
            ),
            "invalid_template_count": _integer(
                user_config_template_validation.get("invalid_template_count")
            ),
            "all_templates_valid": (
                user_config_template_validation.get("all_templates_valid") is True
            ),
            "template_evidence_hash": str(
                user_config_template_validation.get("template_evidence_hash", "")
            ),
            "evidence_hash": str(
                user_config_template_validation.get("evidence_hash", "")
            ),
            "evidence_present": (
                user_config_template_validation.get("evidence_present") is True
            ),
        },
        "traffic_demand_explanation": {
            "evidence_id": str(traffic_demand_explanation.get("evidence_id", "")),
            "request_count": _integer(
                traffic_demand_explanation.get("request_count")
            ),
            "configured_request_count": _integer(
                traffic_demand_explanation.get("configured_request_count")
            ),
            "explained_request_count": _integer(
                traffic_demand_explanation.get("explained_request_count")
            ),
            "communication_only_request_count": _integer(
                traffic_demand_explanation.get("communication_only_request_count")
            ),
            "compute_service_request_count": _integer(
                traffic_demand_explanation.get("compute_service_request_count")
            ),
            "active_traffic_classes": _string_tuple(
                traffic_demand_explanation.get("active_traffic_classes")
            ),
            "frontend_inference_required": (
                traffic_demand_explanation.get("frontend_inference_required") is True
            ),
            "packet_level_simulation": (
                traffic_demand_explanation.get("packet_level_simulation") is True
            ),
            "evidence_hash": str(
                traffic_demand_explanation.get("evidence_hash", "")
            ),
            "evidence_present": (
                traffic_demand_explanation.get("evidence_present") is True
            ),
        },
        "user_service_requests": {
            "evidence_id": str(user_service_requests.get("evidence_id", "")),
            "request_model": str(user_service_requests.get("request_model", "")),
            "request_count": _integer(user_service_requests.get("request_count")),
            "exported_request_count": _integer(
                user_service_requests.get("exported_request_count")
            ),
            "hidden_request_count": _integer(
                user_service_requests.get("hidden_request_count")
            ),
            "active_request_count": _integer(
                user_service_requests.get("active_request_count")
            ),
            "compute_request_count": _integer(
                user_service_requests.get("compute_request_count")
            ),
            "network_waiting_request_count": _integer(
                user_service_requests.get("network_waiting_request_count")
            ),
            "summary_hash": str(user_service_requests.get("summary_hash", "")),
            "evidence_present": user_service_requests.get("evidence_present") is True,
        },
        "audit_index": {
            "audit_index_id": RUNTIME_EXPORT_PACKAGE_AUDIT_INDEX_V1_ID,
            "filename": "export_package_audit_index_v1.json",
            "hash_binding_direction": (
                "audit index records this scenario_review_bundle_v1.json file hash"
            ),
        },
        "artifact_review": {
            "artifact_count": len(tuple(artifact_filenames)),
            "artifact_filenames": tuple(sorted(str(item) for item in artifact_filenames)),
            "entrypoint_filenames": (
                "scenario_review_bundle_v1.json",
                "export_package_audit_index_v1.json",
                "review_summary_v1.json",
                "diagnostics_bundle_v1.json",
                "network_kpi_benchmark_validation_v1.json",
                "network_kpi_formula_evidence_v1.json",
                "user_configuration_template_validation_v1.json",
                "traffic_demand_explanation_v1.json",
                "user_service_request_summary_v2.json",
                "manifest.json",
                "config_snapshot.json",
            ),
        },
        "model_boundaries": {
            "event_kernel_policy": "NO_EVENT_KERNEL_BEHAVIOR_CHANGE",
            "event_replay_restore": False,
            "model_recomputation": False,
            "route_recomputation": False,
            "service_recomputation": False,
            "packet_capture": False,
            "packet_level_simulation": False,
            "external_simulators": False,
            "forbidden_external_integrations": ("STK", "EXATA", "AFSIM", "DDS"),
        },
        "recommended_review_order": (
            "scenario_review_bundle_v1.json",
            "export_package_audit_index_v1.json",
            "review_summary_v1.json",
            "diagnostics_bundle_v1.json",
            "network_kpi_benchmark_validation_v1.json",
            "network_kpi_formula_evidence_v1.json",
            "user_configuration_template_validation_v1.json",
            "traffic_demand_explanation_v1.json",
            "user_service_request_summary_v2.json",
            "service_lifecycle_trace_v2.json",
            "service_trace_comparison_review_report_v1.json",
            "manifest.json",
            "config_snapshot.json",
            "events.jsonl",
            "metrics.csv",
            "summary.json",
        ),
        "scenario_review_status": (
            "SCENARIO_REVIEW_READY"
            if not scenario_review_warnings
            else "SCENARIO_REVIEW_WARN"
        ),
        "scenario_review_warnings": tuple(scenario_review_warnings),
    }
    bundle["scenario_review_hash"] = stable_hash_payload(bundle)
    return bundle


def build_runtime_export_scenario_review_checklist_v1(
    *,
    package_id: str,
    package_dir: str,
    scenario_review_bundle: Mapping[str, Any],
    records: tuple[Mapping[str, Any], ...] = (),
) -> dict[str, object]:
    """Build a deterministic operator checklist for scenario review decisions."""

    if not isinstance(scenario_review_bundle, Mapping):
        raise TypeError("scenario_review_bundle must be a mapping")
    review_order = _string_tuple(
        scenario_review_bundle.get("recommended_review_order")
    )
    artifact_review = _mapping(scenario_review_bundle.get("artifact_review"))
    known_artifacts = frozenset(
        (
            *_string_tuple(artifact_review.get("artifact_filenames")),
            *review_order,
        )
    )
    normalized_records = tuple(
        sorted(
            (
                _runtime_export_scenario_review_checklist_record(
                    record,
                    review_order=review_order,
                    known_artifacts=known_artifacts,
                )
                for record in records
            ),
            key=lambda item: (
                _runtime_export_scenario_review_order_index(
                    str(item["artifact_filename"]),
                    review_order,
                ),
                str(item["artifact_filename"]),
                str(item["step_label"]),
                str(item["review_status"]),
                str(item["operator_note"]),
            ),
        )
    )
    reviewed_count = sum(
        1 for record in normalized_records if record["review_status"] == "REVIEWED"
    )
    skipped_count = sum(
        1 for record in normalized_records if record["review_status"] == "SKIPPED"
    )
    followup_count = sum(
        1
        for record in normalized_records
        if record["review_status"] == "NEEDS_FOLLOWUP"
    )
    error_count = sum(
        1 for record in normalized_records if record["review_status"] == "ERROR"
    )
    submitted_records_complete = bool(
        normalized_records and reviewed_count == len(normalized_records)
    )
    reviewed_recommended, missing_recommended, attention_recommended = (
        _runtime_export_scenario_review_recommended_coverage(
            review_order,
            normalized_records,
        )
    )
    recommended_review_complete = bool(
        review_order and not missing_recommended and not attention_recommended
    )
    recommended_review_status = "RECOMMENDED_REVIEW_UNSPECIFIED"
    if review_order and recommended_review_complete:
        recommended_review_status = "RECOMMENDED_REVIEW_COMPLETE"
    elif review_order:
        recommended_review_status = "RECOMMENDED_REVIEW_INCOMPLETE"
    checklist_status = "CHECKLIST_EMPTY"
    if submitted_records_complete:
        checklist_status = "CHECKLIST_COMPLETE"
    elif error_count or followup_count:
        checklist_status = "CHECKLIST_WARN"
    elif normalized_records:
        checklist_status = "CHECKLIST_PARTIAL"
    checklist: dict[str, object] = {
        "type": "RUNTIME_EXPORT_SCENARIO_REVIEW_CHECKLIST_V1",
        "version": "v1",
        "checklist_id": RUNTIME_EXPORT_SCENARIO_REVIEW_CHECKLIST_V1_ID,
        "source": "OPERATOR_SCENARIO_REVIEW_CHECKLIST",
        "checklist_scope": "SCENARIO_REVIEW_BUNDLE_OPERATOR_DECISIONS",
        "package_id": str(package_id),
        "package_dir": str(package_dir),
        "scenario_review_bundle_id": str(
            scenario_review_bundle.get("bundle_id", "")
        ),
        "scenario_review_hash": str(
            scenario_review_bundle.get("scenario_review_hash", "")
        ),
        "record_count": len(normalized_records),
        "reviewed_count": reviewed_count,
        "skipped_count": skipped_count,
        "followup_count": followup_count,
        "error_count": error_count,
        "submitted_records_complete": submitted_records_complete,
        "expected_review_filenames": review_order,
        "expected_review_count": len(review_order),
        "reviewed_recommended_filenames": reviewed_recommended,
        "reviewed_recommended_count": len(reviewed_recommended),
        "missing_recommended_review_filenames": missing_recommended,
        "missing_recommended_review_count": len(missing_recommended),
        "attention_recommended_review_filenames": attention_recommended,
        "attention_recommended_review_count": len(attention_recommended),
        "recommended_review_complete": recommended_review_complete,
        "recommended_review_status": recommended_review_status,
        "checklist_status": checklist_status,
        "records": normalized_records,
        "ordering": (
            "recommended_review_order ascending, then artifact_filename, "
            "step_label, review_status, and operator_note ascending"
        ),
        "boundary_conditions": (
            "NO_EVENT_REPLAY",
            "NO_MODEL_RECOMPUTE",
            "NO_PACKAGE_READ_MUTATION",
            "OPERATOR_SUPPLIED_REVIEW_DECISIONS",
        ),
    }
    checklist["checklist_hash"] = stable_hash_payload(checklist)
    return checklist


def build_runtime_export_scenario_review_checklist_template_v1(
    *,
    package_id: str,
    package_dir: str,
    scenario_review_bundle: Mapping[str, Any],
    audit_index: Mapping[str, Any] | None = None,
) -> dict[str, object]:
    """Build a deterministic backend template for operator checklist editing."""

    if not isinstance(scenario_review_bundle, Mapping):
        raise TypeError("scenario_review_bundle must be a mapping")
    audit = _mapping(audit_index)
    review_order = _string_tuple(
        scenario_review_bundle.get("recommended_review_order")
    )
    artifact_hashes = _runtime_export_artifact_hashes_by_filename(audit)
    records = tuple(
        _runtime_export_scenario_review_checklist_template_record(
            filename,
            index=index,
            scenario_review_bundle=scenario_review_bundle,
            audit_index=audit,
            artifact_hashes=artifact_hashes,
        )
        for index, filename in enumerate(review_order)
    )
    missing_evidence = tuple(
        str(record["artifact_filename"])
        for record in records
        if record["evidence_present"] is not True
    )
    template: dict[str, object] = {
        "type": "RUNTIME_EXPORT_SCENARIO_REVIEW_CHECKLIST_TEMPLATE_V1",
        "version": "v1",
        "template_id": RUNTIME_EXPORT_SCENARIO_REVIEW_CHECKLIST_TEMPLATE_V1_ID,
        "source": "BACKEND_RUNTIME_EXPORT_PACKAGE",
        "template_scope": "SCENARIO_REVIEW_RECOMMENDED_STEPS_OPERATOR_TEMPLATE",
        "package_id": str(package_id),
        "package_dir": str(package_dir),
        "scenario_review_bundle_id": str(
            scenario_review_bundle.get("bundle_id", "")
        ),
        "scenario_review_hash": str(
            scenario_review_bundle.get("scenario_review_hash", "")
        ),
        "audit_hash": str(audit.get("audit_hash", "")),
        "expected_review_filenames": review_order,
        "expected_review_count": len(review_order),
        "evidence_present_count": len(records) - len(missing_evidence),
        "missing_evidence_filenames": missing_evidence,
        "missing_evidence_count": len(missing_evidence),
        "template_status": (
            "TEMPLATE_READY" if not missing_evidence else "TEMPLATE_WARN"
        ),
        "records": records,
        "record_policy": (
            "template records prefill step_label, evidence_hash, and "
            "review_order_index; operators still choose review_status and note"
        ),
        "boundary_conditions": (
            "NO_EVENT_REPLAY",
            "NO_MODEL_RECOMPUTE",
            "NO_PACKAGE_READ_MUTATION",
            "BACKEND_GENERATED_OPERATOR_TEMPLATE",
        ),
    }
    template["template_hash"] = stable_hash_payload(template)
    return template


def build_runtime_export_scenario_review_checklist_template_comparison_v1(
    *,
    package_id: str,
    package_dir: str,
    scenario_review_checklist: Mapping[str, Any] | None = None,
    scenario_review_checklist_template: Mapping[str, Any],
) -> dict[str, object]:
    """Compare a saved operator checklist against the latest backend template."""

    if not isinstance(scenario_review_checklist_template, Mapping):
        raise TypeError("scenario_review_checklist_template must be a mapping")
    checklist = _mapping(scenario_review_checklist)
    template = _mapping(scenario_review_checklist_template)
    template_records = _records(template.get("records"))
    checklist_records = _records(checklist.get("records"))
    checklist_by_filename = {
        str(record.get("artifact_filename", "")): record
        for record in checklist_records
        if str(record.get("artifact_filename", ""))
    }
    template_filenames = tuple(
        str(record.get("artifact_filename", ""))
        for record in template_records
        if str(record.get("artifact_filename", ""))
    )
    compared_records = tuple(
        _runtime_export_scenario_review_template_comparison_record(
            template_record,
            checklist_by_filename.get(str(template_record.get("artifact_filename", ""))),
        )
        for template_record in template_records
    )
    extra_records = tuple(
        _runtime_export_scenario_review_template_extra_record(record)
        for record in checklist_records
        if str(record.get("artifact_filename", "")) not in set(template_filenames)
    )
    checklist_present = bool(checklist)
    missing_count = sum(
        1 for record in compared_records if "MISSING_CHECKLIST_RECORD" in record["issue_labels"]
    )
    mismatch_count = sum(
        1 for record in compared_records if "EVIDENCE_HASH_MISMATCH" in record["issue_labels"]
    )
    attention_count = sum(
        1 for record in compared_records if "OPERATOR_REVIEW_NOT_REVIEWED" in record["issue_labels"]
    )
    aligned_count = sum(
        1 for record in compared_records if record["comparison_status"] == "ALIGNED"
    )
    comparison_status = "ALIGNED"
    if not checklist_present:
        comparison_status = "CHECKLIST_MISSING"
    elif str(template.get("template_status", "")) != "TEMPLATE_READY":
        comparison_status = "TEMPLATE_WARN"
    elif missing_count or mismatch_count or attention_count or extra_records:
        comparison_status = "DRIFT"
    comparison: dict[str, object] = {
        "type": "RUNTIME_EXPORT_SCENARIO_REVIEW_CHECKLIST_TEMPLATE_COMPARISON_V1",
        "version": "v1",
        "comparison_id": (
            RUNTIME_EXPORT_SCENARIO_REVIEW_CHECKLIST_TEMPLATE_COMPARISON_V1_ID
        ),
        "source": "BACKEND_RUNTIME_EXPORT_PACKAGE",
        "comparison_scope": "SAVED_CHECKLIST_VS_LATEST_BACKEND_TEMPLATE",
        "package_id": str(package_id),
        "package_dir": str(package_dir),
        "scenario_review_hash": str(template.get("scenario_review_hash", "")),
        "template_hash": str(template.get("template_hash", "")),
        "template_status": str(template.get("template_status", "")),
        "checklist_present": checklist_present,
        "checklist_hash": str(checklist.get("checklist_hash", "")),
        "checklist_status": str(checklist.get("checklist_status", "")),
        "comparison_status": comparison_status,
        "template_record_count": len(template_records),
        "checklist_record_count": len(checklist_records),
        "aligned_record_count": aligned_count,
        "missing_checklist_record_count": missing_count,
        "evidence_hash_mismatch_count": mismatch_count,
        "operator_attention_count": attention_count,
        "extra_checklist_record_count": len(extra_records),
        "records": compared_records,
        "extra_records": extra_records,
        "boundary_conditions": (
            "NO_EVENT_REPLAY",
            "NO_MODEL_RECOMPUTE",
            "NO_PACKAGE_READ_MUTATION",
            "BACKEND_GENERATED_TEMPLATE_COMPARISON",
            "AUDIT_INDEX_HASH_REFRESH_IS_NOT_TREATED_AS_CHECKLIST_DRIFT",
        ),
    }
    comparison["comparison_hash"] = stable_hash_payload(comparison)
    return comparison


def build_runtime_export_route_detail_index_v1(
    *,
    package_id: str,
    package_dir: str,
    config_snapshot: Mapping[str, Any],
) -> dict[str, object]:
    """Build a deterministic route detail index for result-package review."""

    if not isinstance(config_snapshot, Mapping):
        raise TypeError("config_snapshot must be a mapping")

    status = _mapping(config_snapshot.get("status"))
    route_summary = _mapping(status.get("route_explanation_summary_v1"))
    route_trust = _runtime_export_route_trust_evidence(status)
    route_comparison_review = _runtime_export_route_comparison_review_metadata()
    route_detail_export_policy = _mapping(
        status.get("runtime_export_route_detail_policy_v1")
    )
    route_items = tuple(
        _runtime_export_route_detail_record(item)
        for item in _records(route_summary.get("items"))
    )
    route_ids = tuple(
        str(item.get("route_id", "")) for item in route_items if str(item.get("route_id", ""))
    )
    route_id_set = set(route_ids)
    sample_route_ids = _string_tuple(route_trust.get("sample_route_ids"))
    indexed_sample_route_ids = tuple(
        route_id for route_id in sample_route_ids if route_id in route_id_set
    )
    missing_sample_route_ids = tuple(
        route_id for route_id in sample_route_ids if route_id not in route_id_set
    )
    hidden_route_count = max(
        0,
        _integer(route_summary.get("route_count")) - len(route_items),
    )
    index: dict[str, object] = {
        "type": "RUNTIME_EXPORT_ROUTE_DETAIL_INDEX_V1",
        "version": "v1",
        "index_id": RUNTIME_EXPORT_ROUTE_DETAIL_INDEX_V1_ID,
        "source": "BACKEND_RUNTIME_EXPORT",
        "index_scope": "ROUTE_EXPLANATION_WINDOW_EXPORT",
        "package_id": str(package_id),
        "package_dir": str(package_dir),
        "route_model": str(route_trust.get("route_model", "")),
        "packet_level_simulation": _bool(route_trust.get("packet_level_simulation")),
        "all_pairs_computation": _bool(route_trust.get("all_pairs_computation")),
        "route_summary": {
            "source": str(route_summary.get("source", "")),
            "summary_scope": str(route_summary.get("summary_scope", "")),
            "cursor": _integer(route_summary.get("cursor")),
            "limit": _integer(route_summary.get("limit")),
            "next_cursor": _integer(route_summary.get("next_cursor")),
            "has_more": _bool(route_summary.get("has_more")),
            "route_count": _integer(route_summary.get("route_count")),
            "indexed_route_count": len(route_items),
            "hidden_route_count": hidden_route_count,
            "available_route_count": _integer(
                route_summary.get("available_route_count")
            ),
            "blocked_route_count": _integer(route_summary.get("blocked_route_count")),
            "over_demand_route_count": _integer(
                route_summary.get("over_demand_route_count")
            ),
            "compute_service_route_count": _integer(
                route_summary.get("compute_service_route_count")
            ),
            "network_service_route_count": _integer(
                route_summary.get("network_service_route_count")
            ),
        },
        "route_detail_export_policy": dict(route_detail_export_policy),
        "route_trust": route_trust,
        "route_comparison_review": route_comparison_review,
        "route_ids": route_ids,
        "sample_route_ids": sample_route_ids,
        "indexed_sample_route_ids": indexed_sample_route_ids,
        "missing_sample_route_ids": missing_sample_route_ids,
        "source_order_policy": "route_explanation_summary_v1.items order is preserved",
        "routes": route_items,
    }
    index["route_detail_index_hash"] = stable_hash_payload(index)
    return index


def build_runtime_export_route_detail_page_v1(
    route_detail_index: Mapping[str, Any],
    *,
    cursor: int = 0,
    limit: int = 100,
    query: str = "",
    availability: str = "ALL",
    business_type: str = "ALL",
    bottleneck_component: str = "ALL",
) -> dict[str, object]:
    """Build a deterministic page from an exported route detail index."""

    if not isinstance(route_detail_index, Mapping):
        raise TypeError("route_detail_index must be a mapping")
    routes = tuple(
        _runtime_export_route_detail_record(item)
        for item in _records(route_detail_index.get("routes"))
    )
    filtered_routes = tuple(
        route
        for route in routes
        if _runtime_export_route_detail_matches_filter(
            route,
            query=query,
            availability=availability,
            business_type=business_type,
            bottleneck_component=bottleneck_component,
        )
    )
    normalized_cursor = _page_cursor(cursor)
    normalized_limit = _page_limit(limit)
    items = filtered_routes[normalized_cursor : normalized_cursor + normalized_limit]
    next_cursor = min(len(filtered_routes), normalized_cursor + len(items))
    normalized_filters = _runtime_export_route_detail_filter_summary(
        query=query,
        availability=availability,
        business_type=business_type,
        bottleneck_component=bottleneck_component,
    )
    filter_applied = _runtime_export_route_detail_filter_applied(normalized_filters)
    page: dict[str, object] = {
        "type": "RUNTIME_EXPORT_ROUTE_DETAIL_PAGE_V1",
        "version": "v1",
        "page_id": RUNTIME_EXPORT_ROUTE_DETAIL_PAGE_V1_ID,
        "source": "BACKEND_RUNTIME_EXPORT_PACKAGE",
        "package_id": str(route_detail_index.get("package_id", "")),
        "index_id": str(route_detail_index.get("index_id", "")),
        "route_detail_export_policy": dict(
            _mapping(route_detail_index.get("route_detail_export_policy"))
        ),
        "route_comparison_review": dict(
            _mapping(route_detail_index.get("route_comparison_review"))
        ),
        "route_detail_index_hash": str(
            route_detail_index.get("route_detail_index_hash", "")
        ),
        "index_scope": str(route_detail_index.get("index_scope", "")),
        "cursor": normalized_cursor,
        "limit": normalized_limit,
        "next_cursor": next_cursor,
        "has_more": next_cursor < len(filtered_routes),
        "route_count": len(filtered_routes),
        "item_count": len(items),
        "unfiltered_route_count": len(routes),
        "filter_applied": filter_applied,
        "filters": normalized_filters,
        "available_route_count": sum(1 for route in filtered_routes if route["available"]),
        "blocked_route_count": sum(1 for route in filtered_routes if not route["available"]),
        "compute_service_route_count": sum(
            1
            for route in filtered_routes
            if str(route["business_type"]).upper() == "COMPUTE_SERVICE"
        ),
        "network_service_route_count": sum(
            1
            for route in filtered_routes
            if str(route["business_type"]).upper() != "COMPUTE_SERVICE"
        ),
        "items": items,
    }
    page["page_hash"] = stable_hash_payload(page)
    return page


def build_runtime_export_service_trace_page_v1(
    service_trace_export: Mapping[str, Any],
    *,
    package_id: str = "",
    cursor: int = 0,
    limit: int = 100,
    query: str = "",
    terminal_state: str = "ALL",
    compute_node_id: str = "",
    stage_kind: str = "ALL",
    terminal_reason: str = "ALL",
) -> dict[str, object]:
    """Build a deterministic page from an exported service trace artifact."""

    if not isinstance(service_trace_export, Mapping):
        raise TypeError("service_trace_export must be a mapping")
    summary = _mapping(service_trace_export.get("summary"))
    traces = tuple(
        _runtime_export_service_trace_record(item)
        for item in _records(summary.get("items"))
    )
    filtered_traces = tuple(
        trace
        for trace in traces
        if _runtime_export_service_trace_matches_filter(
            trace,
            query=query,
            terminal_state=terminal_state,
            compute_node_id=compute_node_id,
            stage_kind=stage_kind,
            terminal_reason=terminal_reason,
        )
    )
    normalized_cursor = _page_cursor(cursor)
    normalized_limit = _page_limit(limit)
    items = filtered_traces[normalized_cursor : normalized_cursor + normalized_limit]
    next_cursor = min(len(filtered_traces), normalized_cursor + len(items))
    normalized_filters = _runtime_export_service_trace_filter_summary(
        query=query,
        terminal_state=terminal_state,
        compute_node_id=compute_node_id,
        stage_kind=stage_kind,
        terminal_reason=terminal_reason,
    )
    filter_applied = _runtime_export_service_trace_filter_applied(
        normalized_filters
    )
    page: dict[str, object] = {
        "type": "RUNTIME_EXPORT_SERVICE_TRACE_PAGE_V1",
        "version": "v1",
        "page_id": RUNTIME_EXPORT_SERVICE_TRACE_PAGE_V1_ID,
        "source": "BACKEND_RUNTIME_EXPORT_PACKAGE",
        "package_id": str(package_id),
        "artifact_type": str(service_trace_export.get("type", "")),
        "artifact_source": str(service_trace_export.get("source", "")),
        "artifact_policy": str(service_trace_export.get("artifact_policy", "")),
        "service_trace_export_policy": dict(
            _mapping(service_trace_export.get("service_trace_export_policy"))
        ),
        "service_trace_comparison_review": _runtime_export_service_trace_comparison_review_metadata(),
        "artifact_window_only": True,
        "trace_contract_id": str(summary.get("contract_id", "")),
        "trace_model": str(summary.get("trace_model", "")),
        "source_summary": str(summary.get("source_summary", "")),
        "summary_scope": str(summary.get("summary_scope", "")),
        "export_cursor": _integer(summary.get("cursor")),
        "export_limit": _integer(summary.get("limit")),
        "export_next_cursor": _integer(summary.get("next_cursor")),
        "export_has_more": _bool(summary.get("has_more")),
        "cursor": normalized_cursor,
        "limit": normalized_limit,
        "next_cursor": next_cursor,
        "has_more": next_cursor < len(filtered_traces),
        "service_count": len(filtered_traces),
        "trace_count": len(filtered_traces),
        "item_count": len(items),
        "unfiltered_trace_count": len(traces),
        "complete_trace_count": sum(
            1 for trace in filtered_traces if trace["terminal_state"] == "COMPLETE"
        ),
        "running_trace_count": sum(
            1 for trace in filtered_traces if trace["terminal_state"] == "RUNNING"
        ),
        "incomplete_trace_count": sum(
            1
            for trace in filtered_traces
            if trace["terminal_state"] == "INCOMPLETE"
        ),
        "hidden_trace_count": max(0, len(filtered_traces) - len(items)),
        "filter_applied": filter_applied,
        "filters": normalized_filters,
        "boundary_conditions": (
            "ARTIFACT_WINDOW_ONLY",
            "NO_EVENT_REPLAY",
            "NO_SERVICE_RECOMPUTE",
            "NO_PACKAGE_MUTATION",
        ),
        "items": items,
    }
    page["page_hash"] = stable_hash_payload(page)
    return page


def build_runtime_export_service_trace_item_v1(
    service_trace_export: Mapping[str, Any],
    trace_id: str,
    *,
    package_id: str = "",
) -> dict[str, object] | None:
    """Build one deterministic service trace detail from an exported package."""

    if not isinstance(service_trace_export, Mapping):
        raise TypeError("service_trace_export must be a mapping")
    normalized_trace_id = str(trace_id).strip()
    if not normalized_trace_id:
        return None
    summary = _mapping(service_trace_export.get("summary"))
    for item in _records(summary.get("items")):
        trace = _runtime_export_service_trace_record(item)
        if normalized_trace_id in _runtime_export_service_trace_lookup_ids(trace):
            detail: dict[str, object] = {
                "type": "RUNTIME_EXPORT_SERVICE_TRACE_ITEM_V1",
                "version": "v1",
                "item_id": RUNTIME_EXPORT_SERVICE_TRACE_ITEM_V1_ID,
                "source": "BACKEND_RUNTIME_EXPORT_PACKAGE",
                "package_id": str(package_id or service_trace_export.get("package_id", "")),
                "artifact_type": str(service_trace_export.get("type", "")),
                "artifact_source": str(service_trace_export.get("source", "")),
                "artifact_policy": str(
                    service_trace_export.get("artifact_policy", "")
                ),
                "service_trace_export_policy": dict(
                    _mapping(service_trace_export.get("service_trace_export_policy"))
                ),
                "service_trace_comparison_review": (
                    _runtime_export_service_trace_comparison_review_metadata()
                ),
                "artifact_window_only": True,
                "trace_contract_id": str(summary.get("contract_id", "")),
                "trace_model": str(summary.get("trace_model", "")),
                "source_summary": str(summary.get("source_summary", "")),
                "summary_scope": "SERVICE_LIFECYCLE_TRACE_ITEM",
                "trace_id": str(trace.get("trace_id", "")),
                "trace": trace,
                "boundary_conditions": (
                    "ARTIFACT_WINDOW_ONLY",
                    "NO_EVENT_REPLAY",
                    "NO_SERVICE_RECOMPUTE",
                    "NO_PACKAGE_MUTATION",
                ),
            }
            detail["item_hash"] = stable_hash_payload(detail)
            return detail
    return None


def build_runtime_export_user_service_request_page_v1(
    user_service_request_export: Mapping[str, Any],
    *,
    package_id: str = "",
    cursor: int = 0,
    limit: int = 100,
    query: str = "",
    service_class: str = "ALL",
    terminal_state: str = "ALL",
    network_waiting: str = "ALL",
) -> dict[str, object]:
    """Build a deterministic page from an exported user-service artifact."""

    if not isinstance(user_service_request_export, Mapping):
        raise TypeError("user_service_request_export must be a mapping")
    summary = _mapping(user_service_request_export.get("summary"))
    requests = tuple(
        _runtime_export_user_service_request_record(item)
        for item in _records(summary.get("items"))
    )
    filtered_requests = tuple(
        request
        for request in requests
        if _runtime_export_user_service_request_matches_filter(
            request,
            query=query,
            service_class=service_class,
            terminal_state=terminal_state,
            network_waiting=network_waiting,
        )
    )
    normalized_cursor = _page_cursor(cursor)
    normalized_limit = _page_limit(limit)
    items = filtered_requests[
        normalized_cursor : normalized_cursor + normalized_limit
    ]
    next_cursor = min(len(filtered_requests), normalized_cursor + len(items))
    normalized_filters = _runtime_export_user_service_request_filter_summary(
        query=query,
        service_class=service_class,
        terminal_state=terminal_state,
        network_waiting=network_waiting,
    )
    filter_applied = _runtime_export_user_service_request_filter_applied(
        normalized_filters
    )
    page: dict[str, object] = {
        "type": "RUNTIME_EXPORT_USER_SERVICE_REQUEST_PAGE_V1",
        "version": "v1",
        "page_id": RUNTIME_EXPORT_USER_SERVICE_REQUEST_PAGE_V1_ID,
        "source": "BACKEND_RUNTIME_EXPORT_PACKAGE",
        "package_id": str(package_id or user_service_request_export.get("package_id", "")),
        "artifact_type": str(user_service_request_export.get("type", "")),
        "artifact_source": str(user_service_request_export.get("source", "")),
        "artifact_policy": str(user_service_request_export.get("artifact_policy", "")),
        "user_service_request_export_policy": dict(
            _mapping(
                user_service_request_export.get(
                    "user_service_request_export_policy"
                )
            )
        ),
        "artifact_window_only": _bool(
            user_service_request_export.get("artifact_window_only")
        ),
        "artifact_hash": str(user_service_request_export.get("artifact_hash", "")),
        "summary_hash": str(
            _mapping(user_service_request_export.get("evidence")).get(
                "summary_hash",
                "",
            )
        ),
        "request_model": str(summary.get("request_model", "")),
        "route_model": str(summary.get("route_model", "")),
        "compute_model": str(summary.get("compute_model", "")),
        "packet_level_simulation": _bool(summary.get("packet_level_simulation")),
        "frontend_inference_required": _bool(
            summary.get("frontend_inference_required")
        ),
        "summary_scope": str(summary.get("summary_scope", "")),
        "export_cursor": _integer(summary.get("cursor")),
        "export_limit": _integer(summary.get("limit")),
        "export_next_cursor": _integer(summary.get("next_cursor")),
        "export_has_more": _bool(summary.get("has_more")),
        "cursor": normalized_cursor,
        "limit": normalized_limit,
        "next_cursor": next_cursor,
        "has_more": next_cursor < len(filtered_requests),
        "request_count": len(filtered_requests),
        "item_count": len(items),
        "unfiltered_request_count": len(requests),
        "active_request_count": sum(
            1 for request in filtered_requests if request["request_active"]
        ),
        "compute_request_count": sum(
            1
            for request in filtered_requests
            if str(request["service_class"]).upper() == "COMPUTE_SERVICE"
        ),
        "communication_request_count": sum(
            1
            for request in filtered_requests
            if str(request["service_class"]).upper() != "COMPUTE_SERVICE"
        ),
        "network_waiting_request_count": sum(
            1 for request in filtered_requests if request["network_waiting"]
        ),
        "hidden_request_count": max(0, len(filtered_requests) - len(items)),
        "filter_applied": filter_applied,
        "filters": normalized_filters,
        "boundary_conditions": (
            "ARTIFACT_WINDOW_ONLY",
            "NO_EVENT_REPLAY",
            "NO_SERVICE_RECOMPUTE",
            "NO_PACKAGE_MUTATION",
        ),
        "items": items,
    }
    page["page_hash"] = stable_hash_payload(page)
    return page


def build_runtime_export_route_detail_item_v1(
    route_detail_index: Mapping[str, Any],
    route_id: str,
) -> dict[str, object] | None:
    """Build one deterministic route detail item from an exported package index."""

    if not isinstance(route_detail_index, Mapping):
        raise TypeError("route_detail_index must be a mapping")
    normalized_route_id = str(route_id).strip()
    if not normalized_route_id:
        return None
    for item in _records(route_detail_index.get("routes")):
        route = _runtime_export_route_detail_record(item)
        if str(route["route_id"]) == normalized_route_id:
            detail: dict[str, object] = {
                "type": "RUNTIME_EXPORT_ROUTE_DETAIL_ITEM_V1",
                "version": "v1",
                "item_id": RUNTIME_EXPORT_ROUTE_DETAIL_ITEM_V1_ID,
                "source": "BACKEND_RUNTIME_EXPORT_PACKAGE",
                "package_id": str(route_detail_index.get("package_id", "")),
                "index_id": str(route_detail_index.get("index_id", "")),
                "route_detail_index_hash": str(
                    route_detail_index.get("route_detail_index_hash", "")
                ),
                "route_comparison_review": dict(
                    _mapping(route_detail_index.get("route_comparison_review"))
                ),
                "route_id": normalized_route_id,
                "route": route,
            }
            detail["item_hash"] = stable_hash_payload(detail)
            return detail
    return None


def build_runtime_export_route_comparison_review_report_v1(
    *,
    package_id: str,
    package_dir: str,
    route_comparison_review: Mapping[str, Any],
    runtime_export_boundary_alignment: Mapping[str, Any] | None = None,
    records: tuple[Mapping[str, Any], ...] = (),
) -> dict[str, object]:
    """Build a deterministic operator report for selected route comparisons."""

    if not isinstance(route_comparison_review, Mapping):
        raise TypeError("route_comparison_review must be a mapping")
    normalized_review = _mapping(route_comparison_review)
    normalized_alignment = _mapping(runtime_export_boundary_alignment)
    normalized_records = tuple(
        sorted(
            (
                _runtime_export_route_comparison_report_record(
                    record,
                    normalized_review,
                )
                for record in records
            ),
            key=lambda item: (
                str(item["route_id"]),
                str(item["comparison_status"]),
                str(item["package_route_detail_hash"]),
                str(item["live_route_detail_hash"]),
            ),
        )
    )
    match_count = sum(
        1 for record in normalized_records if record["comparison_status"] == "MATCH"
    )
    different_count = sum(
        1
        for record in normalized_records
        if record["comparison_status"] == "DIFFERENT"
    )
    unavailable_count = sum(
        1
        for record in normalized_records
        if record["comparison_status"] == "UNAVAILABLE"
    )
    error_count = sum(
        1 for record in normalized_records if record["comparison_status"] == "ERROR"
    )
    report: dict[str, object] = {
        "type": "RUNTIME_EXPORT_ROUTE_COMPARISON_REVIEW_REPORT_V1",
        "version": "v1",
        "report_id": RUNTIME_EXPORT_ROUTE_COMPARISON_REVIEW_REPORT_V1_ID,
        "source": "OPERATOR_ROUTE_COMPARISON_REVIEW",
        "report_scope": "SELECTED_PACKAGE_VS_LIVE_ROUTE_COMPARISON_OUTCOMES",
        "package_id": str(package_id),
        "package_dir": str(package_dir),
        "route_comparison_review": dict(normalized_review),
        "runtime_export_boundary_alignment_v1": dict(normalized_alignment),
        "boundary_alignment_hash": str(
            normalized_alignment.get("alignment_hash", "")
        ),
        "boundary_alignment_status": str(
            normalized_alignment.get("alignment_status", "")
        ),
        "boundary_alignment_warnings": _string_tuple(
            normalized_alignment.get("warnings")
        ),
        "runtime_export_boundary_hash": str(
            normalized_alignment.get("boundary_hash", "")
        ),
        "record_count": len(normalized_records),
        "match_count": match_count,
        "different_count": different_count,
        "unavailable_count": unavailable_count,
        "error_count": error_count,
        "records": normalized_records,
        "ordering": "route_id ascending, then comparison_status ascending",
        "boundary_conditions": _string_tuple(
            normalized_review.get("boundary_conditions")
        ),
    }
    report["report_hash"] = stable_hash_payload(report)
    return report


def build_runtime_export_service_trace_comparison_review_report_v1(
    *,
    package_id: str,
    package_dir: str,
    service_trace_comparison_review: Mapping[str, Any] | None = None,
    runtime_export_boundary_alignment: Mapping[str, Any] | None = None,
    records: tuple[Mapping[str, Any], ...] = (),
) -> dict[str, object]:
    """Build a deterministic operator report for selected service trace comparisons."""

    normalized_review = (
        _runtime_export_service_trace_comparison_review_metadata()
        if service_trace_comparison_review is None
        else _mapping(service_trace_comparison_review)
    )
    normalized_alignment = _mapping(runtime_export_boundary_alignment)
    normalized_records = tuple(
        sorted(
            (
                _runtime_export_service_trace_comparison_report_record(
                    record,
                    normalized_review,
                )
                for record in records
            ),
            key=lambda item: (
                str(item["trace_id"]),
                str(item["comparison_status"]),
                str(item["package_trace_item_hash"]),
                str(item["live_trace_detail_hash"]),
            ),
        )
    )
    match_count = sum(
        1 for record in normalized_records if record["comparison_status"] == "MATCH"
    )
    different_count = sum(
        1
        for record in normalized_records
        if record["comparison_status"] == "DIFFERENT"
    )
    unavailable_count = sum(
        1
        for record in normalized_records
        if record["comparison_status"] == "UNAVAILABLE"
    )
    error_count = sum(
        1 for record in normalized_records if record["comparison_status"] == "ERROR"
    )
    report: dict[str, object] = {
        "type": "RUNTIME_EXPORT_SERVICE_TRACE_COMPARISON_REVIEW_REPORT_V1",
        "version": "v1",
        "report_id": RUNTIME_EXPORT_SERVICE_TRACE_COMPARISON_REVIEW_REPORT_V1_ID,
        "source": "OPERATOR_SERVICE_TRACE_COMPARISON_REVIEW",
        "report_scope": "SELECTED_PACKAGE_VS_LIVE_SERVICE_TRACE_COMPARISON_OUTCOMES",
        "package_id": str(package_id),
        "package_dir": str(package_dir),
        "service_trace_comparison_review": dict(normalized_review),
        "runtime_export_boundary_alignment_v1": dict(normalized_alignment),
        "boundary_alignment_hash": str(
            normalized_alignment.get("alignment_hash", "")
        ),
        "boundary_alignment_status": str(
            normalized_alignment.get("alignment_status", "")
        ),
        "boundary_alignment_warnings": _string_tuple(
            normalized_alignment.get("warnings")
        ),
        "runtime_export_boundary_hash": str(
            normalized_alignment.get("boundary_hash", "")
        ),
        "record_count": len(normalized_records),
        "match_count": match_count,
        "different_count": different_count,
        "unavailable_count": unavailable_count,
        "error_count": error_count,
        "records": normalized_records,
        "ordering": "trace_id ascending, then comparison_status ascending",
        "boundary_conditions": _string_tuple(
            normalized_review.get("boundary_conditions")
        ),
    }
    report["report_hash"] = stable_hash_payload(report)
    return report


def build_runtime_export_service_trace_comparison_review_report_page_v1(
    report: Mapping[str, Any],
    *,
    cursor: int = 0,
    limit: int = 100,
    query: str = "",
    status: str = "ALL",
) -> dict[str, object]:
    """Build a deterministic cursor page from a saved service trace review report."""

    if not isinstance(report, Mapping):
        raise TypeError("report must be a mapping")
    review = _mapping(report.get("service_trace_comparison_review"))
    normalized_records = tuple(
        _runtime_export_service_trace_comparison_report_record(record, review)
        for record in _records(report.get("records"))
    )
    normalized_status = _normalized_filter_value(status, "ALL")
    if normalized_status not in {"ALL", "MATCH", "DIFFERENT", "UNAVAILABLE", "ERROR"}:
        normalized_status = "ALL"
    normalized_query = _normalized_search_query(query)
    filtered_records = tuple(
        record
        for record in normalized_records
        if _runtime_export_service_trace_comparison_report_record_matches_filter(
            record,
            query=normalized_query,
            status=normalized_status,
        )
    )
    normalized_cursor = _page_cursor(cursor)
    normalized_limit = _page_limit(limit)
    items = filtered_records[
        normalized_cursor : normalized_cursor + normalized_limit
    ]
    next_cursor = min(len(filtered_records), normalized_cursor + len(items))
    page: dict[str, object] = {
        "type": "RUNTIME_EXPORT_SERVICE_TRACE_COMPARISON_REVIEW_REPORT_PAGE_V1",
        "version": "v1",
        "page_id": RUNTIME_EXPORT_SERVICE_TRACE_COMPARISON_REVIEW_REPORT_PAGE_V1_ID,
        "source": "BACKEND_RUNTIME_EXPORT_PACKAGE",
        "report_id": str(report.get("report_id", "")),
        "report_type": str(report.get("type", "")),
        "report_scope": str(report.get("report_scope", "")),
        "package_id": str(report.get("package_id", "")),
        "package_dir": str(report.get("package_dir", "")),
        "service_trace_comparison_review": dict(review),
        "runtime_export_boundary_alignment_v1": dict(
            _mapping(report.get("runtime_export_boundary_alignment_v1"))
        ),
        "boundary_alignment_hash": str(report.get("boundary_alignment_hash", "")),
        "boundary_alignment_status": str(
            report.get("boundary_alignment_status", "")
        ),
        "boundary_alignment_warnings": _string_tuple(
            report.get("boundary_alignment_warnings")
        ),
        "runtime_export_boundary_hash": str(
            report.get("runtime_export_boundary_hash", "")
        ),
        "report_hash": str(report.get("report_hash", "")),
        "report_record_count": _integer(report.get("record_count")),
        "record_count": len(filtered_records),
        "unfiltered_record_count": len(normalized_records),
        "match_count": sum(
            1
            for record in filtered_records
            if record["comparison_status"] == "MATCH"
        ),
        "different_count": sum(
            1
            for record in filtered_records
            if record["comparison_status"] == "DIFFERENT"
        ),
        "unavailable_count": sum(
            1
            for record in filtered_records
            if record["comparison_status"] == "UNAVAILABLE"
        ),
        "error_count": sum(
            1
            for record in filtered_records
            if record["comparison_status"] == "ERROR"
        ),
        "cursor": normalized_cursor,
        "limit": normalized_limit,
        "next_cursor": next_cursor,
        "has_more": next_cursor < len(filtered_records),
        "item_count": len(items),
        "hidden_record_count": max(0, len(filtered_records) - len(items)),
        "filter_applied": normalized_status != "ALL" or bool(normalized_query),
        "filters": {
            "query": normalized_query,
            "status": normalized_status,
        },
        "records": items,
        "ordering": str(
            report.get(
                "ordering",
                "trace_id ascending, then comparison_status ascending",
            )
        ),
        "boundary_conditions": _string_tuple(report.get("boundary_conditions")),
    }
    page["page_hash"] = stable_hash_payload(page)
    return page


def build_runtime_export_benchmark_acceptance_binding_v1(
    *,
    config_snapshot: Mapping[str, Any],
) -> dict[str, object]:
    """Bind one package config snapshot to the shipped benchmark gate matrix."""

    if not isinstance(config_snapshot, Mapping):
        raise TypeError("config_snapshot must be a mapping")
    matrix = benchmark_scenario_matrix_v1_to_dict()
    scenarios = _records(matrix.get("scenarios"))
    identity_metrics = (
        "satellite_count",
        "user_count",
        "compute_node_count",
        "runtime_duration_s",
        "orbit_update_interval_s",
        "plane_count",
    )
    candidates = tuple(
        scenario
        for scenario in scenarios
        if all(
            _runtime_export_benchmark_metric_matches(
                config_snapshot,
                scenario,
                metric,
            )
            for metric in identity_metrics
        )
    )
    issue_labels: list[str] = []
    if not candidates:
        binding: dict[str, object] = {
            "type": "RUNTIME_EXPORT_BENCHMARK_ACCEPTANCE_BINDING_V1",
            "version": "v1",
            "binding_id": RUNTIME_EXPORT_BENCHMARK_ACCEPTANCE_BINDING_V1_ID,
            "source": "BACKEND_RUNTIME_EXPORT_CONFIG_SNAPSHOT",
            "matrix_id": str(matrix.get("matrix_id", "")),
            "binding_status": "NO_STANDARD_SCENARIO_MATCH",
            "check_status": "WARN",
            "scenario_id": "",
            "label": "",
            "config_path": "",
            "scale_tier": "",
            "matched_identity_metrics": (),
            "expected_range_results": (),
            "fidelity_results": (),
            "runtime_status_results": (),
            "issue_labels": ("NO_STANDARD_BENCHMARK_SCENARIO_MATCH",),
            "recommendation": (
                "run one of the shipped 72, 300, or 1200 benchmark configs "
                "for benchmark-gated acceptance"
            ),
        }
        binding["binding_hash"] = stable_hash_payload(binding)
        return binding
    if len(candidates) > 1:
        issue_labels.append("MULTIPLE_STANDARD_BENCHMARK_SCENARIO_MATCHES")
    scenario = candidates[0]
    expected_range_results = tuple(
        _runtime_export_benchmark_expected_range_result(
            config_snapshot,
            expected_range,
        )
        for expected_range in _records(scenario.get("expected_ranges"))
    )
    fidelity_results = _runtime_export_benchmark_fidelity_results(
        config_snapshot,
        scenario,
    )
    runtime_status_results = _runtime_export_benchmark_runtime_status_results(
        config_snapshot,
        scenario,
    )
    for result in (
        *expected_range_results,
        *fidelity_results,
        *runtime_status_results,
    ):
        if result["status"] != "PASS":
            issue_labels.extend(_string_tuple(result.get("issue_labels")))
    check_status = "FAIL" if issue_labels else "PASS"
    binding = {
        "type": "RUNTIME_EXPORT_BENCHMARK_ACCEPTANCE_BINDING_V1",
        "version": "v1",
        "binding_id": RUNTIME_EXPORT_BENCHMARK_ACCEPTANCE_BINDING_V1_ID,
        "source": "BACKEND_RUNTIME_EXPORT_CONFIG_SNAPSHOT",
        "matrix_id": str(matrix.get("matrix_id", "")),
        "binding_status": "MATCHED_STANDARD_SCENARIO",
        "check_status": check_status,
        "scenario_id": str(scenario.get("scenario_id", "")),
        "label": str(scenario.get("label", "")),
        "config_path": str(scenario.get("config_path", "")),
        "scale_tier": str(scenario.get("scale_tier", "")),
        "matched_identity_metrics": identity_metrics,
        "expected_range_results": expected_range_results,
        "fidelity_results": fidelity_results,
        "runtime_status_results": runtime_status_results,
        "issue_labels": tuple(sorted(set(issue_labels))),
        "recommendation": (
            "inspect failed benchmark gate evidence"
            if issue_labels
            else "no action"
        ),
    }
    binding["binding_hash"] = stable_hash_payload(binding)
    return binding


def build_runtime_export_package_audit_index_v1(
    *,
    package_id: str,
    package_dir: str,
    config_snapshot: Mapping[str, Any],
    manifest: Mapping[str, Any],
    review_summary: Mapping[str, Any],
    diagnostics_bundle: Mapping[str, Any],
    artifact_records: tuple[Mapping[str, Any], ...] = (),
    route_comparison_review_report: Mapping[str, Any] | None = None,
    service_trace_comparison_review_report: Mapping[str, Any] | None = None,
    scenario_review_checklist: Mapping[str, Any] | None = None,
    runtime_export_boundary_alignment: Mapping[str, Any] | None = None,
    user_configuration_export: Mapping[str, Any] | None = None,
) -> dict[str, object]:
    """Build a deterministic long-term audit index for a result package."""

    if not isinstance(config_snapshot, Mapping):
        raise TypeError("config_snapshot must be a mapping")
    if not isinstance(manifest, Mapping):
        raise TypeError("manifest must be a mapping")
    if not isinstance(review_summary, Mapping):
        raise TypeError("review_summary must be a mapping")
    if not isinstance(diagnostics_bundle, Mapping):
        raise TypeError("diagnostics_bundle must be a mapping")

    status = _mapping(config_snapshot.get("status"))
    boundary = _mapping(manifest.get("runtime_export_reproducibility_boundary_v1"))
    if not boundary:
        boundary = _runtime_export_reproducibility_boundary(status, manifest)
    route_report = _mapping(route_comparison_review_report)
    service_trace_report = _mapping(service_trace_comparison_review_report)
    scenario_checklist = _mapping(scenario_review_checklist)
    alignment = _mapping(runtime_export_boundary_alignment)
    if not alignment:
        alignment = _mapping(route_report.get("runtime_export_boundary_alignment_v1"))
    user_config_binding = _runtime_export_user_configuration_audit_binding(
        config_snapshot,
        user_configuration_export,
    )
    benchmark_acceptance_binding = (
        build_runtime_export_benchmark_acceptance_binding_v1(
            config_snapshot=config_snapshot,
        )
    )
    network_kpi_validation = _runtime_export_network_kpi_validation_evidence(status)
    network_kpi_formula_evidence = _runtime_export_network_kpi_formula_evidence(
        status
    )
    user_config_template_validation = (
        _runtime_export_user_configuration_template_validation_evidence(
            config_snapshot
        )
    )
    traffic_demand_explanation = _runtime_export_traffic_demand_explanation_evidence(
        config_snapshot
    )
    user_service_requests = _runtime_export_user_service_request_evidence(status)
    normalized_artifacts = tuple(
        sorted(
            (
                {
                    "name": str(record.get("name", "")),
                    "filename": str(record.get("filename", "")),
                    "bytes": _integer(record.get("bytes")),
                    "sha256": str(record.get("sha256", "")),
                }
                for record in _file_records(artifact_records)
                if str(record.get("filename", ""))
            ),
            key=lambda item: (str(item["filename"]), str(item["name"])),
        )
    )
    required_filenames = tuple(
        str(spec["filename"]) for spec in _REQUIRED_FILE_SPECS
    )
    artifact_filenames = tuple(str(item["filename"]) for item in normalized_artifacts)
    missing_required = tuple(
        filename for filename in required_filenames if filename not in artifact_filenames
    )
    diagnostics_findings = _records(diagnostics_bundle.get("findings"))
    audit_warnings: list[str] = []
    if missing_required:
        audit_warnings.append("REQUIRED_AUDIT_ARTIFACTS_MISSING")
    if not route_report:
        audit_warnings.append("ROUTE_COMPARISON_REVIEW_REPORT_NOT_SAVED")
    if service_trace_report and _integer(service_trace_report.get("error_count")) > 0:
        audit_warnings.append("SERVICE_TRACE_COMPARISON_REVIEW_REPORT_HAS_ERRORS")
    if not alignment:
        audit_warnings.append("BOUNDARY_ALIGNMENT_EVIDENCE_NOT_RECORDED")
    if str(scenario_checklist.get("checklist_status", "")) == "CHECKLIST_WARN":
        audit_warnings.append("SCENARIO_REVIEW_CHECKLIST_NEEDS_ATTENTION")
    if scenario_checklist and (
        scenario_checklist.get("recommended_review_complete") is not True
    ):
        audit_warnings.append(
            "SCENARIO_REVIEW_CHECKLIST_RECOMMENDED_STEPS_INCOMPLETE"
        )
    if user_config_binding["validation_ok"] is not True:
        audit_warnings.append("USER_CONFIGURATION_EXPORT_NOT_VALIDATED")
    if any(str(item.get("severity", "")) == "ERROR" for item in diagnostics_findings):
        audit_warnings.append("DIAGNOSTICS_BUNDLE_HAS_ERROR_FINDINGS")
    audit_status = "AUDIT_READY" if not audit_warnings else "AUDIT_WARN"
    package_review_completion = build_runtime_export_package_review_completion_v1(
        package_id=package_id,
        package_dir=package_dir,
        audit_status=audit_status,
        audit_warnings=tuple(audit_warnings),
        review_summary=review_summary,
        diagnostics_bundle=diagnostics_bundle,
        artifact_records=normalized_artifacts,
        route_comparison_review_report=route_report,
        service_trace_comparison_review_report=service_trace_report,
        scenario_review_checklist=scenario_checklist,
        runtime_export_boundary_alignment=alignment,
        user_configuration_binding=user_config_binding,
    )

    audit_index: dict[str, object] = {
        "type": "RUNTIME_EXPORT_PACKAGE_AUDIT_INDEX_V1",
        "version": "v1",
        "audit_index_id": RUNTIME_EXPORT_PACKAGE_AUDIT_INDEX_V1_ID,
        "source": "BACKEND_RUNTIME_EXPORT_PACKAGE",
        "audit_scope": "RESULT_PACKAGE_LONG_TERM_AUDIT_INDEX",
        "package_id": str(package_id),
        "package_dir": str(package_dir),
        "manifest_hash": str(manifest.get("manifest_hash", "")),
        "control_config_hash": str(manifest.get("control_config_hash", "")),
        "generated_config_hash": str(manifest.get("generated_config_hash", "")),
        "runtime_state_hash": str(manifest.get("runtime_state_hash", "")),
        "runtime_export_boundary_hash": str(boundary.get("boundary_hash", "")),
        "boundary_alignment_hash": str(alignment.get("alignment_hash", "")),
        "boundary_alignment_status": str(alignment.get("alignment_status", "")),
        "boundary_alignment_warnings": _string_tuple(alignment.get("warnings")),
        "user_configuration_binding_v1": user_config_binding,
        "user_configuration_schema_id": str(user_config_binding["schema_id"]),
        "user_configuration_config_hash": str(user_config_binding["config_hash"]),
        "user_configuration_export_hash": str(user_config_binding["export_hash"]),
        "user_configuration_validation_ok": user_config_binding["validation_ok"],
        "benchmark_acceptance_binding_v1": benchmark_acceptance_binding,
        "benchmark_acceptance_binding_status": str(
            benchmark_acceptance_binding["binding_status"]
        ),
        "benchmark_acceptance_check_status": str(
            benchmark_acceptance_binding["check_status"]
        ),
        "benchmark_acceptance_scenario_id": str(
            benchmark_acceptance_binding["scenario_id"]
        ),
        "benchmark_acceptance_binding_hash": str(
            benchmark_acceptance_binding["binding_hash"]
        ),
        "review_summary_hash": str(review_summary.get("summary_hash", "")),
        "diagnostics_hash": str(diagnostics_bundle.get("diagnostics_hash", "")),
        "network_kpi_benchmark_validation_hash": str(
            network_kpi_validation.get("validation_hash", "")
        ),
        "network_kpi_benchmark_validation_status": str(
            network_kpi_validation.get("validation_status", "")
        ),
        "network_kpi_benchmark_validation_present": (
            network_kpi_validation.get("evidence_present") is True
        ),
        "network_kpi_benchmark_validation_failed_check_count": _integer(
            network_kpi_validation.get("failed_check_count")
        ),
        "network_kpi_formula_evidence_hash": str(
            network_kpi_formula_evidence.get("evidence_hash", "")
        ),
        "network_kpi_formula_evidence_status": str(
            network_kpi_formula_evidence.get("formula_evidence_status", "")
        ),
        "network_kpi_formula_evidence_present": (
            network_kpi_formula_evidence.get("evidence_present") is True
        ),
        "network_kpi_formula_evidence_missing_selected_input_count": _integer(
            network_kpi_formula_evidence.get("missing_selected_input_count")
        ),
        "user_configuration_template_validation_hash": str(
            user_config_template_validation.get("evidence_hash", "")
        ),
        "user_configuration_template_validation_status": str(
            user_config_template_validation.get("validation_status", "")
        ),
        "user_configuration_template_validation_present": (
            user_config_template_validation.get("evidence_present") is True
        ),
        "user_configuration_template_validation_all_templates_valid": (
            user_config_template_validation.get("all_templates_valid") is True
        ),
        "user_configuration_template_validation_invalid_template_count": _integer(
            user_config_template_validation.get("invalid_template_count")
        ),
        "traffic_demand_explanation_hash": str(
            traffic_demand_explanation.get("evidence_hash", "")
        ),
        "traffic_demand_explanation_present": (
            traffic_demand_explanation.get("evidence_present") is True
        ),
        "traffic_demand_explanation_request_count": _integer(
            traffic_demand_explanation.get("request_count")
        ),
        "traffic_demand_explanation_compute_service_request_count": _integer(
            traffic_demand_explanation.get("compute_service_request_count")
        ),
        "traffic_demand_explanation_frontend_inference_required": (
            traffic_demand_explanation.get("frontend_inference_required") is True
        ),
        "user_service_request_summary_hash": str(
            user_service_requests.get("summary_hash", "")
        ),
        "user_service_request_summary_present": (
            user_service_requests.get("evidence_present") is True
        ),
        "user_service_request_summary_request_count": _integer(
            user_service_requests.get("request_count")
        ),
        "user_service_request_summary_exported_request_count": _integer(
            user_service_requests.get("exported_request_count")
        ),
        "user_service_request_summary_hidden_request_count": _integer(
            user_service_requests.get("hidden_request_count")
        ),
        "route_comparison_review_report_hash": str(route_report.get("report_hash", "")),
        "route_comparison_review_report_present": bool(route_report),
        "service_trace_comparison_review_report_hash": str(
            service_trace_report.get("report_hash", "")
        ),
        "service_trace_comparison_review_report_present": bool(service_trace_report),
        "service_trace_comparison_review_record_count": _integer(
            service_trace_report.get("record_count")
        ),
        "service_trace_comparison_review_error_count": _integer(
            service_trace_report.get("error_count")
        ),
        "scenario_review_checklist_hash": str(
            scenario_checklist.get("checklist_hash", "")
        ),
        "scenario_review_checklist_present": bool(scenario_checklist),
        "scenario_review_checklist_record_count": _integer(
            scenario_checklist.get("record_count")
        ),
        "scenario_review_checklist_status": str(
            scenario_checklist.get("checklist_status", "")
        ),
        "scenario_review_checklist_recommended_review_complete": (
            scenario_checklist.get("recommended_review_complete") is True
        ),
        "scenario_review_checklist_recommended_review_status": str(
            scenario_checklist.get("recommended_review_status", "")
        ),
        "scenario_review_checklist_expected_review_count": _integer(
            scenario_checklist.get("expected_review_count")
        ),
        "scenario_review_checklist_reviewed_recommended_count": _integer(
            scenario_checklist.get("reviewed_recommended_count")
        ),
        "scenario_review_checklist_missing_recommended_review_count": _integer(
            scenario_checklist.get("missing_recommended_review_count")
        ),
        "scenario_review_checklist_attention_recommended_review_count": _integer(
            scenario_checklist.get("attention_recommended_review_count")
        ),
        "scenario_review_checklist_missing_recommended_review_filenames": (
            _string_tuple(
                scenario_checklist.get("missing_recommended_review_filenames")
            )
        ),
        "scenario_review_checklist_attention_recommended_review_filenames": (
            _string_tuple(
                scenario_checklist.get("attention_recommended_review_filenames")
            )
        ),
        "package_review_completion_v1": package_review_completion,
        "package_review_completion_status": str(
            package_review_completion["completion_status"]
        ),
        "package_review_completion_hash": str(
            package_review_completion["completion_hash"]
        ),
        "artifact_count": len(normalized_artifacts),
        "artifact_hashes": normalized_artifacts,
        "required_artifact_filenames": required_filenames,
        "missing_required_artifact_filenames": missing_required,
        "self_artifact_excluded_from_hashes": True,
        "audit_status": audit_status,
        "audit_warnings": tuple(audit_warnings),
        "forbidden_external_integrations": ("STK", "EXATA", "AFSIM", "DDS"),
        "packet_level_simulation": False,
        "event_replay_restore": False,
        "model_recomputation": False,
        "package_mutation_on_read": False,
    }
    audit_index["audit_hash"] = stable_hash_payload(audit_index)
    return audit_index


def build_runtime_export_package_review_completion_v1(
    *,
    package_id: str,
    package_dir: str,
    audit_status: str,
    audit_warnings: tuple[str, ...] = (),
    review_summary: Mapping[str, Any],
    diagnostics_bundle: Mapping[str, Any],
    artifact_records: tuple[Mapping[str, Any], ...] = (),
    route_comparison_review_report: Mapping[str, Any] | None = None,
    service_trace_comparison_review_report: Mapping[str, Any] | None = None,
    scenario_review_checklist: Mapping[str, Any] | None = None,
    runtime_export_boundary_alignment: Mapping[str, Any] | None = None,
    user_configuration_binding: Mapping[str, Any] | None = None,
) -> dict[str, object]:
    """Build backend-owned package review handoff completion evidence."""

    if not isinstance(review_summary, Mapping):
        raise TypeError("review_summary must be a mapping")
    if not isinstance(diagnostics_bundle, Mapping):
        raise TypeError("diagnostics_bundle must be a mapping")

    route_report = _mapping(route_comparison_review_report)
    service_trace_report = _mapping(service_trace_comparison_review_report)
    checklist = _mapping(scenario_review_checklist)
    alignment = _mapping(runtime_export_boundary_alignment)
    user_config = _mapping(user_configuration_binding)
    network_kpi_validation = _mapping(
        diagnostics_bundle.get("network_kpi_benchmark_validation")
    )
    network_kpi_formula_evidence = _mapping(
        diagnostics_bundle.get("network_kpi_formula_evidence")
    )
    user_config_template_validation = _mapping(
        diagnostics_bundle.get("user_configuration_template_validation")
    )
    artifact_filenames = tuple(
        sorted(
            str(record.get("filename", ""))
            for record in _file_records(artifact_records)
            if str(record.get("filename", ""))
        )
    )
    diagnostics_findings = _records(diagnostics_bundle.get("findings"))
    diagnostics_error_count = sum(
        1 for finding in diagnostics_findings if str(finding.get("severity", "")) == "ERROR"
    )
    route_report_present = bool(route_report)
    route_report_error_count = _integer(route_report.get("error_count"))
    route_report_ready = route_report_present and route_report_error_count == 0
    service_trace_report_present = bool(service_trace_report)
    service_trace_report_error_count = _integer(
        service_trace_report.get("error_count")
    )
    service_trace_report_ready = (
        not service_trace_report_present or service_trace_report_error_count == 0
    )
    checklist_present = bool(checklist)
    checklist_status = str(checklist.get("checklist_status", ""))
    checklist_submitted_records_complete = (
        checklist.get("submitted_records_complete") is True
    )
    checklist_recommended_complete = (
        checklist.get("recommended_review_complete") is True
    )
    checklist_expected_review_count = _integer(checklist.get("expected_review_count"))
    checklist_reviewed_recommended_count = _integer(
        checklist.get("reviewed_recommended_count")
    )
    checklist_missing_recommended = _string_tuple(
        checklist.get("missing_recommended_review_filenames")
    )
    checklist_attention_recommended = _string_tuple(
        checklist.get("attention_recommended_review_filenames")
    )
    checklist_complete = (
        checklist_present
        and checklist_status == "CHECKLIST_COMPLETE"
        and checklist_submitted_records_complete
        and checklist_recommended_complete
    )
    scenario_bundle_present = "scenario_review_bundle_v1.json" in artifact_filenames
    review_summary_ready = str(review_summary.get("review_status", "")) == "REVIEW_READY"
    diagnostics_ready = diagnostics_error_count == 0
    boundary_aligned = str(alignment.get("alignment_status", "")) == "ALIGNED"
    user_configuration_validated = user_config.get("validation_ok") is True
    audit_ready = str(audit_status) == "AUDIT_READY"
    missing_or_warning: list[str] = []
    if not audit_ready:
        missing_or_warning.append("AUDIT_INDEX_NOT_READY")
    if not route_report_present:
        missing_or_warning.append("ROUTE_COMPARISON_REVIEW_REPORT_MISSING")
    elif not route_report_ready:
        missing_or_warning.append("ROUTE_COMPARISON_REVIEW_REPORT_HAS_ERRORS")
    if not service_trace_report_ready:
        missing_or_warning.append("SERVICE_TRACE_COMPARISON_REVIEW_REPORT_HAS_ERRORS")
    if not scenario_bundle_present:
        missing_or_warning.append("SCENARIO_REVIEW_BUNDLE_MISSING")
    if not checklist_present:
        missing_or_warning.append("SCENARIO_REVIEW_CHECKLIST_MISSING")
    elif checklist_status != "CHECKLIST_COMPLETE":
        missing_or_warning.append("SCENARIO_REVIEW_CHECKLIST_NOT_COMPLETE")
    elif not checklist_recommended_complete:
        missing_or_warning.append("SCENARIO_REVIEW_RECOMMENDED_STEPS_INCOMPLETE")
    if not review_summary_ready:
        missing_or_warning.append("REVIEW_SUMMARY_NOT_READY")
    if not diagnostics_ready:
        missing_or_warning.append("DIAGNOSTICS_HAS_ERROR_FINDINGS")
    if not boundary_aligned:
        missing_or_warning.append("BOUNDARY_ALIGNMENT_NOT_ALIGNED")
    if not user_configuration_validated:
        missing_or_warning.append("USER_CONFIGURATION_NOT_VALIDATED")
    completion_ready = not missing_or_warning
    completion: dict[str, object] = {
        "type": "RUNTIME_EXPORT_PACKAGE_REVIEW_COMPLETION_V1",
        "version": "v1",
        "completion_id": RUNTIME_EXPORT_PACKAGE_REVIEW_COMPLETION_V1_ID,
        "source": "BACKEND_RUNTIME_EXPORT_PACKAGE_AUDIT_INDEX",
        "completion_scope": "RESULT_PACKAGE_OPERATOR_HANDOFF_READINESS",
        "package_id": str(package_id),
        "package_dir": str(package_dir),
        "completion_status": (
            "REVIEW_COMPLETE" if completion_ready else "REVIEW_INCOMPLETE"
        ),
        "handoff_ready": completion_ready,
        "audit_status": str(audit_status),
        "audit_warnings": _string_tuple(audit_warnings),
        "route_comparison_review_report_present": route_report_present,
        "route_comparison_review_report_hash": str(route_report.get("report_hash", "")),
        "route_comparison_review_record_count": _integer(route_report.get("record_count")),
        "route_comparison_review_error_count": route_report_error_count,
        "service_trace_comparison_review_report_present": (
            service_trace_report_present
        ),
        "service_trace_comparison_review_report_hash": str(
            service_trace_report.get("report_hash", "")
        ),
        "service_trace_comparison_review_record_count": _integer(
            service_trace_report.get("record_count")
        ),
        "service_trace_comparison_review_error_count": (
            service_trace_report_error_count
        ),
        "scenario_review_bundle_present": scenario_bundle_present,
        "scenario_review_checklist_present": checklist_present,
        "scenario_review_checklist_hash": str(checklist.get("checklist_hash", "")),
        "scenario_review_checklist_status": checklist_status,
        "scenario_review_checklist_record_count": _integer(checklist.get("record_count")),
        "scenario_review_checklist_submitted_records_complete": (
            checklist_submitted_records_complete
        ),
        "scenario_review_checklist_recommended_review_complete": (
            checklist_recommended_complete
        ),
        "scenario_review_checklist_recommended_review_status": str(
            checklist.get("recommended_review_status", "")
        ),
        "scenario_review_checklist_expected_review_count": (
            checklist_expected_review_count
        ),
        "scenario_review_checklist_reviewed_recommended_count": (
            checklist_reviewed_recommended_count
        ),
        "scenario_review_checklist_missing_recommended_review_count": len(
            checklist_missing_recommended
        ),
        "scenario_review_checklist_attention_recommended_review_count": len(
            checklist_attention_recommended
        ),
        "scenario_review_checklist_missing_recommended_review_filenames": (
            checklist_missing_recommended
        ),
        "scenario_review_checklist_attention_recommended_review_filenames": (
            checklist_attention_recommended
        ),
        "review_summary_status": str(review_summary.get("review_status", "")),
        "review_summary_hash": str(review_summary.get("summary_hash", "")),
        "diagnostics_error_count": diagnostics_error_count,
        "diagnostics_hash": str(diagnostics_bundle.get("diagnostics_hash", "")),
        "network_kpi_benchmark_validation_present": (
            network_kpi_validation.get("evidence_present") is True
        ),
        "network_kpi_benchmark_validation_status": str(
            network_kpi_validation.get("validation_status", "")
        ),
        "network_kpi_benchmark_validation_failed_check_count": _integer(
            network_kpi_validation.get("failed_check_count")
        ),
        "network_kpi_formula_evidence_present": (
            network_kpi_formula_evidence.get("evidence_present") is True
        ),
        "network_kpi_formula_evidence_status": str(
            network_kpi_formula_evidence.get("formula_evidence_status", "")
        ),
        "network_kpi_formula_evidence_missing_selected_input_count": _integer(
            network_kpi_formula_evidence.get("missing_selected_input_count")
        ),
        "user_configuration_template_validation_present": (
            user_config_template_validation.get("evidence_present") is True
        ),
        "user_configuration_template_validation_status": str(
            user_config_template_validation.get("validation_status", "")
        ),
        "user_configuration_template_validation_invalid_template_count": _integer(
            user_config_template_validation.get("invalid_template_count")
        ),
        "boundary_alignment_status": str(alignment.get("alignment_status", "")),
        "boundary_alignment_hash": str(alignment.get("alignment_hash", "")),
        "user_configuration_validation_ok": user_configuration_validated,
        "missing_or_warning_evidence": tuple(missing_or_warning),
        "evidence_labels": (
            f"audit {audit_status}",
            f"route_report {'saved' if route_report_present else 'missing'}",
            f"route_errors {route_report_error_count}",
            (
                "service_trace_report "
                f"{'saved' if service_trace_report_present else 'optional_missing'}"
            ),
            f"service_trace_errors {service_trace_report_error_count}",
            f"scenario_bundle {'present' if scenario_bundle_present else 'missing'}",
            f"checklist {checklist_status or 'missing'}",
            f"checklist_records {_integer(checklist.get('record_count'))}",
            (
                "checklist_recommended "
                f"{checklist_reviewed_recommended_count}/"
                f"{checklist_expected_review_count}"
            ),
            (
                "network_kpi "
                f"{network_kpi_validation.get('validation_status', 'missing')}"
            ),
            (
                "network_kpi_formula "
                f"{network_kpi_formula_evidence.get('formula_evidence_status', 'missing')}"
            ),
            (
                "config_templates "
                f"{user_config_template_validation.get('validation_status', 'missing')}"
            ),
        ),
        "boundary_conditions": (
            "NO_EVENT_REPLAY",
            "NO_MODEL_RECOMPUTE",
            "NO_PACKAGE_READ_MUTATION",
            "BACKEND_OWNED_HANDOFF_SUMMARY",
        ),
    }
    completion["completion_hash"] = stable_hash_payload(completion)
    return completion


def build_runtime_export_package_acceptance_report_v1(
    *,
    audit_index: Mapping[str, Any],
) -> dict[str, object]:
    """Build a deterministic pass/warn/fail acceptance report for one package."""

    if not isinstance(audit_index, Mapping):
        raise TypeError("audit_index must be a mapping")
    audit = _mapping(audit_index)
    completion = _mapping(audit.get("package_review_completion_v1"))
    if not completion:
        raise ValueError("audit_index has no package_review_completion_v1 object")

    missing_required = _string_tuple(audit.get("missing_required_artifact_filenames"))
    route_errors = _integer(completion.get("route_comparison_review_error_count"))
    service_trace_errors = _integer(
        completion.get("service_trace_comparison_review_error_count")
    )
    network_kpi_failed = _integer(
        completion.get("network_kpi_benchmark_validation_failed_check_count")
    )
    boundary_issues = tuple(
        field
        for field in (
            "packet_level_simulation",
            "event_replay_restore",
            "model_recomputation",
            "package_mutation_on_read",
        )
        if audit.get(field) is not False
    )
    forbidden_integrations = _string_tuple(
        audit.get("forbidden_external_integrations")
    )
    forbidden_missing = tuple(
        item
        for item in ("STK", "EXATA", "AFSIM", "DDS")
        if item not in forbidden_integrations
    )
    service_trace_present = (
        completion.get("service_trace_comparison_review_report_present") is True
    )
    benchmark_binding = _mapping(audit.get("benchmark_acceptance_binding_v1"))
    benchmark_status = str(benchmark_binding.get("check_status", "WARN"))
    benchmark_scenario_id = str(benchmark_binding.get("scenario_id", ""))
    checks = (
        _runtime_export_acceptance_check(
            "required_artifacts",
            "FAIL" if missing_required else "PASS",
            (
                "required result package artifacts are present"
                if not missing_required
                else "required result package artifacts are missing"
            ),
            evidence_hash=str(audit.get("audit_hash", "")),
            evidence_labels=(
                f"artifact_count {_integer(audit.get('artifact_count'))}",
                f"missing_required {len(missing_required)}",
            ),
            issue_labels=missing_required,
            recommendation=(
                "rerun runtime export after the scenario completes"
                if missing_required
                else "no action"
            ),
        ),
        _runtime_export_acceptance_check(
            "review_completion",
            "PASS" if completion.get("handoff_ready") is True else "FAIL",
            str(completion.get("completion_status", "")),
            evidence_hash=str(completion.get("completion_hash", "")),
            evidence_labels=_string_tuple(completion.get("evidence_labels")),
            issue_labels=_string_tuple(completion.get("missing_or_warning_evidence")),
            recommendation=(
                "complete blocking review evidence before handoff"
                if completion.get("handoff_ready") is not True
                else "no action"
            ),
        ),
        _runtime_export_acceptance_check(
            "route_review",
            (
                "PASS"
                if completion.get("route_comparison_review_report_present") is True
                and route_errors == 0
                else "FAIL"
            ),
            "route comparison review report is saved and error-free",
            evidence_hash=str(
                completion.get("route_comparison_review_report_hash", "")
            ),
            evidence_labels=(
                "route_report "
                f"{'saved' if completion.get('route_comparison_review_report_present') is True else 'missing'}",
                f"route_errors {route_errors}",
            ),
            issue_labels=(
                ()
                if completion.get("route_comparison_review_report_present") is True
                and route_errors == 0
                else ("ROUTE_REVIEW_NOT_ACCEPTED",)
            ),
            recommendation=(
                "save route comparison review report without error records"
                if completion.get("route_comparison_review_report_present") is not True
                or route_errors != 0
                else "no action"
            ),
        ),
        _runtime_export_acceptance_check(
            "service_trace_review",
            "FAIL" if service_trace_errors > 0 else "PASS" if service_trace_present else "WARN",
            "service trace comparison review is optional but recommended",
            evidence_hash=str(
                completion.get("service_trace_comparison_review_report_hash", "")
            ),
            evidence_labels=(
                f"service_trace_report {'saved' if service_trace_present else 'missing'}",
                f"service_trace_errors {service_trace_errors}",
            ),
            issue_labels=(
                ("SERVICE_TRACE_REVIEW_HAS_ERRORS",)
                if service_trace_errors > 0
                else () if service_trace_present else ("SERVICE_TRACE_REVIEW_OPTIONAL_MISSING",)
            ),
            recommendation=(
                "save a service trace comparison review report for stronger handoff"
                if not service_trace_present
                else "no action"
            ),
        ),
        _runtime_export_acceptance_check(
            "scenario_review",
            (
                "PASS"
                if completion.get("scenario_review_checklist_present") is True
                and completion.get(
                    "scenario_review_checklist_recommended_review_complete"
                )
                is True
                else "FAIL"
            ),
            str(completion.get("scenario_review_checklist_status", "")) or "missing",
            evidence_hash=str(completion.get("scenario_review_checklist_hash", "")),
            evidence_labels=(
                "scenario_checklist "
                f"{completion.get('scenario_review_checklist_status', '') or 'missing'}",
                (
                    "scenario_recommended "
                    f"{_integer(completion.get('scenario_review_checklist_reviewed_recommended_count'))}/"
                    f"{_integer(completion.get('scenario_review_checklist_expected_review_count'))}"
                ),
            ),
            issue_labels=(
                ()
                if completion.get("scenario_review_checklist_present") is True
                and completion.get(
                    "scenario_review_checklist_recommended_review_complete"
                )
                is True
                else ("SCENARIO_REVIEW_NOT_ACCEPTED",)
            ),
            recommendation=(
                "save a complete scenario review checklist"
                if completion.get("scenario_review_checklist_present") is not True
                or completion.get(
                    "scenario_review_checklist_recommended_review_complete"
                )
                is not True
                else "no action"
            ),
        ),
        _runtime_export_acceptance_check(
            "network_kpi_benchmark",
            (
                "PASS"
                if str(
                    completion.get("network_kpi_benchmark_validation_status", "")
                )
                == "PASS"
                and network_kpi_failed == 0
                else "WARN"
            ),
            str(completion.get("network_kpi_benchmark_validation_status", "")),
            evidence_labels=(
                "network_kpi "
                f"{completion.get('network_kpi_benchmark_validation_status', 'missing')}",
                f"network_kpi_failed {network_kpi_failed}",
            ),
            issue_labels=(
                ()
                if str(
                    completion.get("network_kpi_benchmark_validation_status", "")
                )
                == "PASS"
                and network_kpi_failed == 0
                else ("NETWORK_KPI_BENCHMARK_NOT_PASS",)
            ),
            recommendation=(
                "inspect network KPI benchmark validation evidence"
                if str(
                    completion.get("network_kpi_benchmark_validation_status", "")
                )
                != "PASS"
                or network_kpi_failed != 0
                else "no action"
            ),
        ),
        _runtime_export_acceptance_check(
            "benchmark_scenario_gate",
            benchmark_status if benchmark_binding else "WARN",
            str(benchmark_binding.get("binding_status", "NO_BENCHMARK_BINDING")),
            evidence_hash=str(benchmark_binding.get("binding_hash", "")),
            evidence_labels=(
                f"scenario {benchmark_scenario_id or 'unmatched'}",
                f"scale {benchmark_binding.get('scale_tier', '')}",
                f"binding {benchmark_binding.get('binding_status', 'missing')}",
            ),
            issue_labels=(
                _string_tuple(benchmark_binding.get("issue_labels"))
                if benchmark_binding
                else ("BENCHMARK_ACCEPTANCE_BINDING_MISSING",)
            ),
            recommendation=(
                str(benchmark_binding.get("recommendation", ""))
                if benchmark_binding
                else "rerun export with benchmark binding support"
            ),
        ),
        _runtime_export_acceptance_check(
            "model_boundary",
            "FAIL" if boundary_issues else "PASS",
            "model boundary exclusions are preserved",
            evidence_hash=str(audit.get("runtime_export_boundary_hash", "")),
            evidence_labels=(
                f"boundary {completion.get('boundary_alignment_status', '')}",
                f"violations {len(boundary_issues)}",
            ),
            issue_labels=boundary_issues,
            recommendation=(
                "remove replay/recompute/mutation/packet-level behavior"
                if boundary_issues
                else "no action"
            ),
        ),
        _runtime_export_acceptance_check(
            "user_configuration",
            (
                "PASS"
                if completion.get("user_configuration_validation_ok") is True
                else "FAIL"
            ),
            "user configuration binding is validated",
            evidence_hash=str(audit.get("user_configuration_config_hash", "")),
            evidence_labels=(
                f"schema {audit.get('user_configuration_schema_id', '')}",
                "validation "
                f"{'ok' if completion.get('user_configuration_validation_ok') is True else 'failed'}",
            ),
            issue_labels=(
                ()
                if completion.get("user_configuration_validation_ok") is True
                else ("USER_CONFIGURATION_NOT_VALIDATED",)
            ),
            recommendation=(
                "fix user configuration validation before acceptance"
                if completion.get("user_configuration_validation_ok") is not True
                else "no action"
            ),
        ),
        _runtime_export_acceptance_check(
            "forbidden_integrations",
            "FAIL" if forbidden_missing else "PASS",
            "forbidden external simulator list is explicit",
            evidence_hash=str(audit.get("audit_hash", "")),
            evidence_labels=forbidden_integrations,
            issue_labels=forbidden_missing,
            recommendation=(
                "restore forbidden integration declarations"
                if forbidden_missing
                else "no action"
            ),
        ),
    )
    fail_count = sum(1 for check in checks if check["status"] == "FAIL")
    warn_count = sum(1 for check in checks if check["status"] == "WARN")
    pass_count = sum(1 for check in checks if check["status"] == "PASS")
    acceptance_status = "FAIL" if fail_count else "WARN" if warn_count else "PASS"
    report: dict[str, object] = {
        "type": "RUNTIME_EXPORT_PACKAGE_ACCEPTANCE_REPORT_V1",
        "version": "v1",
        "acceptance_id": RUNTIME_EXPORT_PACKAGE_ACCEPTANCE_REPORT_V1_ID,
        "source": "BACKEND_RUNTIME_EXPORT_PACKAGE_AUDIT_INDEX",
        "acceptance_scope": "INDUSTRIAL_V2_DEMO_CLOSED_LOOP_ACCEPTANCE",
        "package_id": str(audit.get("package_id", completion.get("package_id", ""))),
        "package_dir": str(audit.get("package_dir", completion.get("package_dir", ""))),
        "acceptance_status": acceptance_status,
        "demo_closed_loop_ready": fail_count == 0,
        "handoff_ready": completion.get("handoff_ready") is True,
        "audit_status": str(audit.get("audit_status", "")),
        "completion_status": str(completion.get("completion_status", "")),
        "check_count": len(checks),
        "pass_count": pass_count,
        "warn_count": warn_count,
        "fail_count": fail_count,
        "checks": checks,
        "operator_next_actions": tuple(
            check["recommendation"]
            for check in checks
            if check["status"] != "PASS" and check["recommendation"] != "no action"
        ),
        "evidence_hashes": (
            f"audit {audit.get('audit_hash', '')}",
            f"completion {completion.get('completion_hash', '')}",
            f"manifest {audit.get('manifest_hash', '')}",
            f"boundary {audit.get('runtime_export_boundary_hash', '')}",
            f"user_config {audit.get('user_configuration_config_hash', '')}",
            f"benchmark {benchmark_binding.get('binding_hash', '')}",
        ),
        "boundary_conditions": (
            "NO_EVENT_REPLAY",
            "NO_MODEL_RECOMPUTE",
            "NO_PACKAGE_READ_MUTATION",
            "NO_PACKET_LEVEL_SIMULATION",
            "NO_EXTERNAL_SIMULATOR_ARTIFACTS",
            "BACKEND_OWNED_ACCEPTANCE_SUMMARY",
        ),
    }
    report["acceptance_hash"] = stable_hash_payload(report)
    return report


def build_runtime_export_package_handoff_report_v1(
    *,
    audit_index: Mapping[str, Any],
) -> str:
    """Build a deterministic operator-facing handoff report from audit evidence."""

    if not isinstance(audit_index, Mapping):
        raise TypeError("audit_index must be a mapping")
    completion = _mapping(audit_index.get("package_review_completion_v1"))
    if not completion:
        raise ValueError("audit_index has no package_review_completion_v1 object")

    missing_or_warning = _string_tuple(
        completion.get("missing_or_warning_evidence")
    )
    evidence_labels = _string_tuple(completion.get("evidence_labels"))
    boundary_conditions = _string_tuple(completion.get("boundary_conditions"))
    handoff_ready = completion.get("handoff_ready") is True
    follow_up_lines = (
        tuple(f"- {item}" for item in missing_or_warning)
        if missing_or_warning
        else ("- No blocking evidence is missing.",)
    )
    evidence_lines = (
        tuple(f"- {item}" for item in evidence_labels)
        if evidence_labels
        else ("- No compact evidence labels were recorded.",)
    )
    boundary_lines = (
        tuple(f"- {item}" for item in boundary_conditions)
        if boundary_conditions
        else ("- No boundary conditions were recorded.",)
    )
    lines = [
        "# Runtime Export Package Handoff Report v1",
        "",
        f"Report id: {RUNTIME_EXPORT_PACKAGE_HANDOFF_REPORT_V1_ID}",
        f"Source audit index id: {audit_index.get('audit_index_id', '')}",
        f"Package id: {completion.get('package_id', audit_index.get('package_id', ''))}",
        f"Completion status: {completion.get('completion_status', '')}",
        f"Handoff ready: {'true' if handoff_ready else 'false'}",
        f"Completion hash: {completion.get('completion_hash', '')}",
        "",
        "## Review Evidence",
        f"- Audit status: {completion.get('audit_status', '')}",
        (
            "- Route comparison review report present: "
            f"{'true' if completion.get('route_comparison_review_report_present') is True else 'false'}"
        ),
        (
            "- Route comparison review error count: "
            f"{completion.get('route_comparison_review_error_count', 0)}"
        ),
        (
            "- Service trace comparison review report present: "
            f"{'true' if completion.get('service_trace_comparison_review_report_present') is True else 'false'}"
        ),
        (
            "- Service trace comparison review error count: "
            f"{completion.get('service_trace_comparison_review_error_count', 0)}"
        ),
        (
            "- Scenario review checklist status: "
            f"{completion.get('scenario_review_checklist_status', '') or 'missing'}"
        ),
        (
            "- Scenario review checklist records: "
            f"{completion.get('scenario_review_checklist_record_count', 0)}"
        ),
        f"- Review summary status: {completion.get('review_summary_status', '')}",
        f"- Diagnostics error count: {completion.get('diagnostics_error_count', 0)}",
        (
            "- Network KPI benchmark validation: "
            f"{completion.get('network_kpi_benchmark_validation_status', '') or 'missing'}"
        ),
        (
            "- Network KPI benchmark failed checks: "
            f"{completion.get('network_kpi_benchmark_validation_failed_check_count', 0)}"
        ),
        (
            "- Boundary alignment status: "
            f"{completion.get('boundary_alignment_status', '')}"
        ),
        (
            "- User configuration validation ok: "
            f"{'true' if completion.get('user_configuration_validation_ok') is True else 'false'}"
        ),
        "",
        "## Evidence Labels",
        *evidence_lines,
        "",
        "## Required Follow-up",
        *follow_up_lines,
        "",
        "## Boundary Conditions",
        *boundary_lines,
        "",
        "## Machine Evidence",
        f"- Audit hash: {audit_index.get('audit_hash', '')}",
        f"- Manifest hash: {audit_index.get('manifest_hash', '')}",
        (
            "- Runtime export boundary hash: "
            f"{audit_index.get('runtime_export_boundary_hash', '')}"
        ),
        f"- Diagnostics hash: {completion.get('diagnostics_hash', '')}",
        f"- Review summary hash: {completion.get('review_summary_hash', '')}",
        (
            "- Route comparison review report hash: "
            f"{completion.get('route_comparison_review_report_hash', '')}"
        ),
        (
            "- Service trace comparison review report hash: "
            f"{completion.get('service_trace_comparison_review_report_hash', '')}"
        ),
        (
            "- Scenario review checklist hash: "
            f"{completion.get('scenario_review_checklist_hash', '')}"
        ),
        "",
        (
            "This report is generated from backend audit evidence. It does not "
            "replay events, recompute models, mutate result packages on read, "
            "capture packets, or call external simulators."
        ),
    ]
    return "\n".join(lines) + "\n"


def _runtime_export_acceptance_check(
    check_id: str,
    status: str,
    summary: str,
    *,
    evidence_hash: str = "",
    evidence_labels: tuple[str, ...] = (),
    issue_labels: tuple[str, ...] = (),
    recommendation: str = "no action",
) -> dict[str, object]:
    check = {
        "check_id": str(check_id),
        "status": str(status),
        "summary": str(summary),
        "evidence_hash": str(evidence_hash),
        "evidence_labels": _string_tuple(evidence_labels),
        "issue_labels": _string_tuple(issue_labels),
        "recommendation": str(recommendation),
    }
    return {
        **check,
        "check_hash": stable_hash_payload(check),
    }


def _runtime_export_benchmark_metric_matches(
    config_snapshot: Mapping[str, Any],
    scenario: Mapping[str, Any],
    metric: str,
) -> bool:
    observed = _runtime_export_benchmark_metric_value(config_snapshot, metric)
    if observed is None:
        return False
    return _number(observed) == _number(scenario.get(metric))


def _runtime_export_benchmark_expected_range_result(
    config_snapshot: Mapping[str, Any],
    expected_range: Mapping[str, Any],
) -> dict[str, object]:
    metric = str(expected_range.get("metric", ""))
    observed = _runtime_export_benchmark_metric_value(config_snapshot, metric)
    issue_labels: tuple[str, ...] = ()
    status = "PASS"
    if observed is None:
        status = "FAIL"
        issue_labels = ("BENCHMARK_METRIC_MISSING",)
        observed_value = ""
    else:
        observed_value = _number(observed)
        if not (
            _number(expected_range.get("minimum"))
            <= observed_value
            <= _number(expected_range.get("maximum"))
        ):
            status = "FAIL"
            issue_labels = ("BENCHMARK_METRIC_OUT_OF_RANGE",)
    result = {
        "metric": metric,
        "source": str(expected_range.get("source", "")),
        "status": status,
        "evidence_artifact_filename": EXPORT_PACKAGE_AUDIT_INDEX_FILENAME,
        "evidence_artifact_role": "benchmark_acceptance_audit_index",
        "evidence_context_id": f"benchmark.expected_range.{metric}",
        "evidence_context_label": f"expected range metric {metric}",
        "evidence_json_pointer": "/benchmark_acceptance_binding_v1/expected_range_results",
        "observed_value": observed_value,
        "minimum": _number(expected_range.get("minimum")),
        "maximum": _number(expected_range.get("maximum")),
        "unit": str(expected_range.get("unit", "")),
        "issue_labels": issue_labels,
    }
    return {
        **result,
        "result_hash": stable_hash_payload(result),
    }


def _runtime_export_benchmark_fidelity_results(
    config_snapshot: Mapping[str, Any],
    scenario: Mapping[str, Any],
) -> tuple[dict[str, object], ...]:
    status = _mapping(config_snapshot.get("status"))
    fidelity_summary = _mapping(status.get("fidelity_summary"))
    expectation = _mapping(scenario.get("fidelity_expectation"))
    return tuple(
        _runtime_export_benchmark_string_result(
            check_id=f"fidelity.{field}",
            expected=str(expectation.get(field, "")),
            actual=str(fidelity_summary.get(field, "")),
            missing_label="BENCHMARK_FIDELITY_MISSING",
            mismatch_label="BENCHMARK_FIDELITY_MISMATCH",
            evidence_artifact_filename=CONFIG_SNAPSHOT_FILENAME,
            evidence_artifact_role="runtime_config_snapshot_status",
            evidence_context_id=f"fidelity_summary.{field}",
            evidence_context_label=f"fidelity summary {field}",
            evidence_json_pointer=f"/status/fidelity_summary/{field}",
        )
        for field in ("orbit_update_mode", "metrics_mode", "space_link_mode")
    )


def _runtime_export_benchmark_runtime_status_results(
    config_snapshot: Mapping[str, Any],
    scenario: Mapping[str, Any],
) -> tuple[dict[str, object], ...]:
    status = _mapping(config_snapshot.get("status"))
    expectation = _mapping(scenario.get("runtime_status_expectation"))
    route_expectation = _mapping(expectation.get("route_trust"))
    kpi_expectation = _mapping(expectation.get("network_kpi_benchmark_validation"))
    route_summary = _mapping(status.get(str(route_expectation.get("field", ""))))
    kpi_validation = _mapping(status.get(str(kpi_expectation.get("field", ""))))
    route_status = str(route_summary.get("trust_status", ""))
    route_allowed = _string_tuple(route_expectation.get("allowed_trust_statuses"))
    route_assessed = _integer(route_summary.get("assessed_route_count"))
    route_minimum = _integer(route_expectation.get("minimum_assessed_route_count"))
    route_pass = route_status in route_allowed and route_assessed >= route_minimum
    kpi_status = str(kpi_validation.get("validation_status", ""))
    kpi_allowed = _string_tuple(kpi_expectation.get("allowed_validation_statuses"))
    kpi_failed = _integer(kpi_validation.get("failed_check_count"))
    kpi_max_failed = _integer(kpi_expectation.get("maximum_failed_check_count"))
    kpi_pass = kpi_status in kpi_allowed and kpi_failed <= kpi_max_failed
    return (
        _runtime_export_benchmark_status_result(
            check_id="runtime_status.route_trust",
            status="PASS" if route_pass else "FAIL",
            expected="/".join(route_allowed),
            actual=route_status,
            observed_count=route_assessed,
            minimum_count=route_minimum,
            issue_label="BENCHMARK_ROUTE_TRUST_NOT_ACCEPTED",
            evidence_artifact_filename=ROUTE_DETAIL_INDEX_FILENAME,
            evidence_artifact_role="route_trust_evidence",
            evidence_context_id=str(route_expectation.get("field", "")),
            evidence_context_label="route trust runtime status",
            evidence_json_pointer="/route_trust",
        ),
        _runtime_export_benchmark_status_result(
            check_id="runtime_status.network_kpi",
            status="PASS" if kpi_pass else "FAIL",
            expected="/".join(kpi_allowed),
            actual=kpi_status,
            observed_count=kpi_failed,
            minimum_count=0,
            issue_label="BENCHMARK_NETWORK_KPI_NOT_ACCEPTED",
            evidence_artifact_filename=NETWORK_KPI_BENCHMARK_VALIDATION_FILENAME,
            evidence_artifact_role="network_kpi_benchmark_validation",
            evidence_context_id=str(kpi_expectation.get("field", "")),
            evidence_context_label="network KPI benchmark validation",
            evidence_json_pointer="/validation",
        ),
    )


def _runtime_export_benchmark_string_result(
    *,
    check_id: str,
    expected: str,
    actual: str,
    missing_label: str,
    mismatch_label: str,
    evidence_artifact_filename: str,
    evidence_artifact_role: str,
    evidence_context_id: str,
    evidence_context_label: str,
    evidence_json_pointer: str,
) -> dict[str, object]:
    issue_labels: tuple[str, ...] = ()
    status = "PASS"
    if not actual:
        status = "FAIL"
        issue_labels = (missing_label,)
    elif actual != expected:
        status = "FAIL"
        issue_labels = (mismatch_label,)
    result = {
        "check_id": check_id,
        "status": status,
        "evidence_artifact_filename": evidence_artifact_filename,
        "evidence_artifact_role": evidence_artifact_role,
        "evidence_context_id": evidence_context_id,
        "evidence_context_label": evidence_context_label,
        "evidence_json_pointer": evidence_json_pointer,
        "expected": expected,
        "actual": actual,
        "issue_labels": issue_labels,
    }
    return {
        **result,
        "result_hash": stable_hash_payload(result),
    }


def _runtime_export_benchmark_status_result(
    *,
    check_id: str,
    status: str,
    expected: str,
    actual: str,
    observed_count: int,
    minimum_count: int,
    issue_label: str,
    evidence_artifact_filename: str,
    evidence_artifact_role: str,
    evidence_context_id: str,
    evidence_context_label: str,
    evidence_json_pointer: str,
) -> dict[str, object]:
    result = {
        "check_id": check_id,
        "status": status,
        "evidence_artifact_filename": evidence_artifact_filename,
        "evidence_artifact_role": evidence_artifact_role,
        "evidence_context_id": evidence_context_id,
        "evidence_context_label": evidence_context_label,
        "evidence_json_pointer": evidence_json_pointer,
        "expected": expected,
        "actual": actual,
        "observed_count": observed_count,
        "minimum_count": minimum_count,
        "issue_labels": () if status == "PASS" else (issue_label,),
    }
    return {
        **result,
        "result_hash": stable_hash_payload(result),
    }


def _runtime_export_benchmark_metric_value(
    config_snapshot: Mapping[str, Any],
    metric: str,
) -> object | None:
    config = _mapping(config_snapshot.get("config"))
    generated = _mapping(config_snapshot.get("generated_config"))
    paths = {
        "satellite_count": (
            ("generated", "satellite_count"),
            ("config", "satellite_count"),
            ("config", "scenario", "satellite_count"),
        ),
        "user_count": (
            ("generated", "ground_user_count"),
            ("generated", "user_count"),
            ("config", "ground_user_count"),
            ("config", "scenario", "user_count"),
        ),
        "compute_node_count": (
            ("generated", "compute_node_count"),
            ("generated", "compute_nodes"),
            ("config", "compute_node_count"),
            ("config", "compute_nodes"),
            ("config", "scenario", "compute_nodes"),
        ),
        "runtime_duration_s": (
            ("generated", "duration_seconds"),
            ("config", "duration_seconds"),
            ("config", "runtime", "duration"),
        ),
        "orbit_update_interval_s": (
            ("generated", "orbit_tick_seconds"),
            ("config", "orbit_tick_seconds"),
            ("config", "scenario", "orbit", "update_interval_seconds"),
        ),
        "plane_count": (
            ("generated", "plane_count"),
            ("config", "plane_count"),
            ("config", "scenario", "orbit", "plane_count"),
        ),
        "flow_interval_s": (
            ("config", "flow_interval_seconds"),
            ("config", "scenario", "traffic_model", "flow_interval_seconds"),
        ),
        "task_interval_s": (
            ("config", "task_interval_seconds"),
            ("config", "scenario", "traffic_model", "task_interval_seconds"),
        ),
        "flow_demand_capacity_mbps": (
            ("config", "flow_demand_capacity"),
            ("config", "scenario", "traffic_model", "flow_demand_capacity"),
        ),
        "task_compute_demand": (
            ("config", "task_compute_demand"),
            ("config", "scenario", "traffic_model", "task_compute_demand"),
        ),
        "task_data_size_mb": (
            ("config", "task_data_size"),
            ("config", "scenario", "traffic_model", "task_data_size"),
        ),
        "max_space_link_candidates_per_satellite": (
            ("config", "network", "max_space_link_candidates_per_satellite"),
        ),
        "batch_space_link_update_limit": (
            ("config", "network", "batch_space_link_update_limit"),
        ),
    }.get(metric, ())
    roots = {"config": config, "generated": generated}
    for path in paths:
        value = _runtime_export_nested_value(roots, path)
        if value is not None:
            return value
    return None


def _runtime_export_nested_value(
    roots: Mapping[str, Mapping[str, Any]],
    path: tuple[str, ...],
) -> object | None:
    if not path:
        return None
    current: object = roots.get(path[0], {})
    for key in path[1:]:
        mapping = _mapping(current)
        if key not in mapping:
            return None
        current = mapping[key]
    return current


def _runtime_export_user_configuration_audit_binding(
    config_snapshot: Mapping[str, Any],
    user_configuration_export: Mapping[str, Any] | None,
) -> dict[str, object]:
    export = _mapping(user_configuration_export)
    config = _mapping(config_snapshot.get("config"))
    config_hash = str(export.get("config_hash", ""))
    if not config_hash and config:
        config_hash = stable_hash_payload(config)
    validation_ok = export.get("validation_ok")
    binding: dict[str, object] = {
        "type": "USER_CONFIGURATION_AUDIT_BINDING_V1",
        "version": "v1",
        "binding_id": USER_CONFIGURATION_AUDIT_BINDING_V1_ID,
        "source": "BACKEND_RUNTIME_EXPORT_PACKAGE",
        "schema_id": str(export.get("schema_id", USER_CONFIGURATION_SCHEMA_V2_ID)),
        "export_scope": str(export.get("export_scope", "CURRENT_EFFECTIVE_SEES_CONFIG")),
        "format": str(export.get("format", "JSON_MAPPING")),
        "config_hash": config_hash,
        "export_hash": stable_hash_payload(export) if export else "",
        "validation_ok": validation_ok is True,
        "validation_error_count": _integer(export.get("validation_error_count")),
        "unknown_key_policy": str(export.get("unknown_key_policy", "REJECT")),
        "defaulting_policy": str(
            export.get("defaulting_policy", "OMITTED_FIELDS_USE_BACKEND_DEFAULTS")
        ),
        "import_paths": _string_tuple(export.get("import_paths")),
    }
    binding["binding_hash"] = stable_hash_payload(binding)
    return binding


def summarize_result_package_record_v1(
    package: Mapping[str, Any],
) -> dict[str, object]:
    """Summarize whether a runtime export package satisfies the v1 contract."""

    if not isinstance(package, Mapping):
        raise TypeError("package must be a mapping")
    contract = result_package_contract_v1_to_dict()
    required_files = tuple(
        str(spec["filename"]) for spec in contract["required_files"]  # type: ignore[index]
    )
    recommended_files = _contract_filenames(contract, "recommended_files")
    file_records = tuple(_file_records(package.get("files")))
    filenames = tuple(sorted(str(record.get("filename", "")) for record in file_records))
    present_required = tuple(filename for filename in required_files if filename in filenames)
    missing_required = tuple(
        filename for filename in required_files if filename not in filenames
    )
    present_recommended = tuple(
        filename for filename in recommended_files if filename in filenames
    )
    missing_recommended = tuple(
        filename for filename in recommended_files if filename not in filenames
    )
    manifest = _mapping(package.get("manifest"))
    manifest_id = str(manifest.get("manifest_id", ""))
    file_hashes = tuple(
        str(record.get("sha256", ""))
        for record in sorted(file_records, key=lambda item: str(item.get("filename", "")))
        if str(record.get("sha256", "")).startswith("sha256:")
    )
    package_ok = package.get("ok") is True
    manifest_ok = manifest_id == RUNTIME_REPRODUCIBILITY_MANIFEST_V1_ID
    return {
        "contract_id": RESULT_PACKAGE_CONTRACT_V1_ID,
        "package_id": str(package.get("package_id", "")),
        "package_type": str(package.get("type", "")),
        "package_ok": package_ok,
        "package_dir": str(package.get("package_dir", "")),
        "file_count": len(file_records),
        "required_file_count": len(required_files),
        "present_required_files": present_required,
        "missing_required_files": missing_required,
        "recommended_file_count": len(recommended_files),
        "present_recommended_files": present_recommended,
        "missing_recommended_files": missing_recommended,
        "package_complete": package_ok and manifest_ok and not missing_required,
        "manifest_id": manifest_id,
        "manifest_hash": str(manifest.get("manifest_hash", "")),
        "file_hash_count": len(file_hashes),
        "file_hashes": file_hashes,
        "catalog_record_present": isinstance(
            package.get("export_catalog_record"),
            Mapping,
        ),
        "history_record_present": isinstance(
            package.get("export_history_record"),
            Mapping,
        ),
    }


def _contract_filenames(
    contract: Mapping[str, Any],
    field_name: str,
) -> tuple[str, ...]:
    value = contract.get(field_name)
    if not isinstance(value, (list, tuple)):
        return ()
    filenames: list[str] = []
    for item in value:
        if isinstance(item, Mapping):
            filenames.append(str(item.get("filename", "")))
    return tuple(filename for filename in filenames if filename)


def _runtime_export_reproducibility_boundary(
    status: Mapping[str, Any],
    manifest: Mapping[str, Any],
) -> dict[str, object]:
    boundary = status.get("runtime_export_reproducibility_boundary_v1")
    if isinstance(boundary, Mapping):
        return dict(boundary)
    return build_runtime_export_reproducibility_boundary_v1(
        runtime_status=status,
        manifest=manifest,
    )


def _runtime_export_diagnostic_findings(
    *,
    manifest_ok: bool,
    review_status: str,
    missing_required: tuple[str, ...],
    missing_recommended: tuple[str, ...],
    route_trust: Mapping[str, Any],
    network_kpi_validation: Mapping[str, Any],
    network_kpi_formula_evidence: Mapping[str, Any],
    user_config_template_validation: Mapping[str, Any],
    traffic_demand_explanation: Mapping[str, Any],
    user_service_requests: Mapping[str, Any],
) -> tuple[dict[str, object], ...]:
    findings: list[dict[str, object]] = []
    if not manifest_ok:
        findings.append(
            _diagnostic_finding(
                "ERROR",
                "MANIFEST_ID_MISMATCH",
                "manifest.json does not use the expected runtime reproducibility id.",
            )
        )
    if missing_required:
        findings.append(
            _diagnostic_finding(
                "ERROR",
                "REQUIRED_ARTIFACTS_MISSING",
                f"Missing required artifacts: {', '.join(missing_required)}.",
            )
        )
    if review_status != "REVIEW_READY":
        findings.append(
            _diagnostic_finding(
                "WARN",
                "REVIEW_SUMMARY_NOT_READY",
                f"review_summary_v1.json reports {review_status or 'UNKNOWN'}.",
            )
        )
    if missing_recommended:
        findings.append(
            _diagnostic_finding(
                "WARN",
                "RECOMMENDED_ARTIFACTS_MISSING",
                f"Missing recommended artifacts: {', '.join(missing_recommended)}.",
            )
        )
    if route_trust.get("evidence_present") is not True:
        findings.append(
            _diagnostic_finding(
                "WARN",
                "ROUTE_TRUST_EVIDENCE_MISSING",
                "config_snapshot.status does not include route_provenance_trust_summary_v1.",
            )
        )
    if route_trust.get("packet_level_simulation") is True:
        findings.append(
            _diagnostic_finding(
                "ERROR",
                "ROUTE_TRUST_PACKET_LEVEL_DECLARED",
                "route trust evidence declares packet-level simulation, which is outside the v1 model boundary.",
            )
        )
    if route_trust.get("all_pairs_computation") is True:
        findings.append(
            _diagnostic_finding(
                "ERROR",
                "ROUTE_TRUST_ALL_PAIRS_DECLARED",
                "route trust evidence declares all-pairs route computation, which is outside the v1 scale boundary.",
            )
        )
    if network_kpi_validation.get("evidence_present") is not True:
        findings.append(
            _diagnostic_finding(
                "WARN",
                "NETWORK_KPI_BENCHMARK_VALIDATION_MISSING",
                "config_snapshot.status does not include network_kpi_benchmark_validation_v1.",
            )
        )
    if network_kpi_validation.get("packet_level_simulation") is True:
        findings.append(
            _diagnostic_finding(
                "ERROR",
                "NETWORK_KPI_BENCHMARK_PACKET_LEVEL_DECLARED",
                "network KPI benchmark evidence declares packet-level simulation, which is outside the v2 demo boundary.",
            )
        )
    if str(network_kpi_validation.get("validation_status", "")) == "FAIL":
        findings.append(
            _diagnostic_finding(
                "ERROR",
                "NETWORK_KPI_BENCHMARK_VALIDATION_FAILED",
                "network KPI benchmark guardrails reported failed checks.",
            )
        )
    elif str(network_kpi_validation.get("validation_status", "")) in {
        "WARN",
        "INSUFFICIENT_DATA",
    }:
        findings.append(
            _diagnostic_finding(
                "WARN",
                "NETWORK_KPI_BENCHMARK_VALIDATION_NOT_PASS",
                (
                    "network KPI benchmark guardrails require operator review: "
                    f"{network_kpi_validation.get('validation_status', '')}."
                ),
            )
        )
    if network_kpi_formula_evidence.get("evidence_present") is not True:
        findings.append(
            _diagnostic_finding(
                "WARN",
                "NETWORK_KPI_FORMULA_EVIDENCE_MISSING",
                "config_snapshot.status does not include network_kpi_formula_evidence_v1.",
            )
        )
    if network_kpi_formula_evidence.get("packet_level_simulation") is True:
        findings.append(
            _diagnostic_finding(
                "ERROR",
                "NETWORK_KPI_FORMULA_PACKET_LEVEL_DECLARED",
                "network KPI formula evidence declares packet-level simulation, which is outside the v2 demo boundary.",
            )
        )
    if network_kpi_formula_evidence.get("evidence_present") is True and str(
        network_kpi_formula_evidence.get("formula_evidence_status", "")
    ) in {
        "PARTIAL_RUNTIME_VALUES",
        "MISSING_SELECTED_INPUTS",
        "NO_KPI_PROVENANCE",
    }:
        findings.append(
            _diagnostic_finding(
                "WARN",
                "NETWORK_KPI_FORMULA_EVIDENCE_INCOMPLETE",
                (
                    "network KPI formula evidence requires operator review: "
                    f"{network_kpi_formula_evidence.get('formula_evidence_status', '')}."
                ),
            )
        )
    if user_config_template_validation.get("evidence_present") is not True:
        findings.append(
            _diagnostic_finding(
                "WARN",
                "USER_CONFIGURATION_TEMPLATE_VALIDATION_MISSING",
                "config_snapshot does not include user_configuration_template_validation_v1.",
            )
        )
    if user_config_template_validation.get("packet_level_simulation") is True:
        findings.append(
            _diagnostic_finding(
                "ERROR",
                "USER_CONFIGURATION_TEMPLATE_PACKET_LEVEL_DECLARED",
                "user configuration template validation evidence declares packet-level simulation.",
            )
        )
    if user_config_template_validation.get("external_simulators") is True:
        findings.append(
            _diagnostic_finding(
                "ERROR",
                "USER_CONFIGURATION_TEMPLATE_EXTERNAL_SIMULATOR_DECLARED",
                "user configuration template validation evidence declares external simulator use.",
            )
        )
    if user_config_template_validation.get("evidence_present") is True and (
        user_config_template_validation.get("all_templates_valid") is not True
    ):
        findings.append(
            _diagnostic_finding(
                "WARN",
                "USER_CONFIGURATION_TEMPLATE_VALIDATION_INCOMPLETE",
                (
                    "approved user configuration template validation requires "
                    "operator review."
                ),
            )
        )
    if traffic_demand_explanation.get("evidence_present") is not True:
        findings.append(
            _diagnostic_finding(
                "WARN",
                "TRAFFIC_DEMAND_EXPLANATION_MISSING",
                (
                    "config_snapshot.generated_config.backend_summary does not "
                    "include traffic_demand_explanation_v1."
                ),
            )
        )
    if traffic_demand_explanation.get("packet_level_simulation") is True:
        findings.append(
            _diagnostic_finding(
                "ERROR",
                "TRAFFIC_DEMAND_EXPLANATION_PACKET_LEVEL_DECLARED",
                "traffic demand explanation declares packet-level simulation.",
            )
        )
    if traffic_demand_explanation.get("frontend_inference_required") is True:
        findings.append(
            _diagnostic_finding(
                "WARN",
                "TRAFFIC_DEMAND_EXPLANATION_FRONTEND_INFERENCE_REQUIRED",
                "traffic demand explanation still requires frontend semantic inference.",
            )
        )
    if user_service_requests.get("evidence_present") is not True:
        findings.append(
            _diagnostic_finding(
                "WARN",
                "USER_SERVICE_REQUEST_SUMMARY_MISSING",
                "config_snapshot.status does not include user_service_request_summary_v2.",
            )
        )
    if user_service_requests.get("packet_level_simulation") is True:
        findings.append(
            _diagnostic_finding(
                "ERROR",
                "USER_SERVICE_REQUEST_PACKET_LEVEL_DECLARED",
                "user service request evidence declares packet-level simulation, which is outside the v2 demo boundary.",
            )
        )
    if user_service_requests.get("frontend_inference_required") is True:
        findings.append(
            _diagnostic_finding(
                "WARN",
                "USER_SERVICE_REQUEST_FRONTEND_INFERENCE_REQUIRED",
                "user service request evidence still requires frontend semantic inference.",
            )
        )
    if not findings:
        findings.append(
            _diagnostic_finding(
                "INFO",
                "RESULT_PACKAGE_REVIEW_READY",
                "Required artifacts, manifest id, and review summary are ready.",
            )
        )
    return tuple(findings)


def _diagnostic_finding(
    severity: str,
    code: str,
    message: str,
) -> dict[str, object]:
    return {
        "severity": severity,
        "code": code,
        "message": message,
    }


def _runtime_export_diagnostic_next_actions(
    *,
    package_complete: bool,
    missing_recommended: tuple[str, ...],
) -> tuple[str, ...]:
    if not package_complete:
        return (
            "Re-export the runtime package after the run reaches a stable state.",
            "Attach diagnostics_bundle_v1.json when reporting missing artifacts.",
        )
    if missing_recommended:
        return (
            "Package is reproducible with required artifacts.",
            "Attach the package directory and note missing recommended artifacts.",
        )
    return (
        "Attach the package directory or deterministic archive for review.",
        "Use manifest.json, review_summary_v1.json, and diagnostics_bundle_v1.json as the first inspection points.",
    )


def _runtime_export_route_comparison_review_metadata() -> dict[str, object]:
    return {
        "version": "v1",
        "source": "BACKEND_RUNTIME_EXPORT",
        "review_scope": "PACKAGE_ROUTE_DETAIL_TO_LIVE_RUNTIME_ROUTE_DETAIL",
        "review_report_type": "RUNTIME_EXPORT_ROUTE_COMPARISON_REVIEW_REPORT_V1",
        "review_report_id": RUNTIME_EXPORT_ROUTE_COMPARISON_REVIEW_REPORT_V1_ID,
        "package_route_detail_endpoint": (
            "GET /runtime/export/packages/{package_id}/routes/{route_id}"
        ),
        "live_route_detail_endpoint": "GET /runtime/details/routes/{route_id}",
        "compare_action": "compare with live",
        "comparison_requires_live_runtime": True,
        "route_id_alignment_required": True,
        "exported_rows_only": True,
        "compared_fields": (
            "availability",
            "business",
            "flow",
            "source_destination",
            "selected_satellite",
            "primary_next_hop",
            "path",
            "capacity_demand",
            "latency",
            "loss",
            "pressure",
            "bottleneck",
        ),
        "status_reasons": (
            "PACKAGE_DETAIL_NOT_LOADED",
            "PACKAGE_DETAIL_LOADING",
            "PACKAGE_DETAIL_UNAVAILABLE",
            "LIVE_DETAIL_NOT_LOADED",
            "LIVE_DETAIL_LOADING",
            "LIVE_DETAIL_UNAVAILABLE",
            "ROUTE_ID_MISMATCH",
        ),
        "boundary_conditions": (
            "NO_ROUTE_RECOMPUTE",
            "NO_EVENT_REPLAY",
            "NO_PACKET_CAPTURE",
            "NO_PACKAGE_MUTATION",
            "CURRENT_RUNTIME_MAY_DIFFER_FROM_EXPORTED_PACKAGE",
        ),
        "review_report_record_schema": {
            "required_fields": (
                "route_id",
                "comparison_status",
                "compared_fields",
                "different_fields",
                "status_reason",
            ),
            "optional_fields": (
                "package_route_detail_hash",
                "live_route_detail_hash",
                "matched_field_count",
                "different_field_count",
                "operator_note",
            ),
            "status_values": (
                "MATCH",
                "DIFFERENT",
                "UNAVAILABLE",
                "ERROR",
            ),
            "ordering": "route_id ascending, then comparison_status ascending",
        },
    }


def _runtime_export_service_trace_comparison_review_metadata() -> dict[str, object]:
    return {
        "version": "v1",
        "source": "BACKEND_RUNTIME_EXPORT",
        "review_scope": "PACKAGE_SERVICE_TRACE_TO_LIVE_RUNTIME_SERVICE_TRACE",
        "review_report_type": "RUNTIME_EXPORT_SERVICE_TRACE_COMPARISON_REVIEW_REPORT_V1",
        "review_report_id": RUNTIME_EXPORT_SERVICE_TRACE_COMPARISON_REVIEW_REPORT_V1_ID,
        "package_service_trace_endpoint": (
            "GET /runtime/export/packages/{package_id}/service-traces/{trace_id}"
        ),
        "live_service_trace_endpoint": "GET /runtime/details/service-traces/{trace_id}",
        "compare_action": "compare with live service trace",
        "comparison_requires_live_runtime": True,
        "trace_id_alignment_required": True,
        "exported_rows_only": True,
        "compared_fields": (
            "trace",
            "service",
            "task",
            "class",
            "terminal",
            "reason",
            "compute_node",
            "input_flow",
            "input_route",
            "output_flow",
            "output_route",
            "input_latency",
            "queue_delay",
            "execution_delay",
            "output_latency",
            "total_latency",
            "stage_counts",
        ),
        "status_reasons": (
            "PACKAGE_TRACE_NOT_LOADED",
            "PACKAGE_TRACE_LOADING",
            "PACKAGE_TRACE_UNAVAILABLE",
            "LIVE_TRACE_NOT_LOADED",
            "LIVE_TRACE_LOADING",
            "LIVE_TRACE_UNAVAILABLE",
            "TRACE_ID_MISMATCH",
        ),
        "boundary_conditions": (
            "NO_SERVICE_RECOMPUTE",
            "NO_EVENT_REPLAY",
            "NO_PACKET_CAPTURE",
            "NO_PACKAGE_MUTATION",
            "CURRENT_RUNTIME_MAY_DIFFER_FROM_EXPORTED_PACKAGE",
        ),
        "review_report_record_schema": {
            "required_fields": (
                "trace_id",
                "comparison_status",
                "compared_fields",
                "different_fields",
                "status_reason",
            ),
            "optional_fields": (
                "package_trace_item_hash",
                "live_trace_detail_hash",
                "matched_field_count",
                "different_field_count",
                "operator_note",
            ),
            "status_values": (
                "MATCH",
                "DIFFERENT",
                "UNAVAILABLE",
                "ERROR",
            ),
            "ordering": "trace_id ascending, then comparison_status ascending",
        },
    }


def _runtime_export_scenario_review_checklist_record(
    record: Mapping[str, Any],
    *,
    review_order: tuple[str, ...],
    known_artifacts: frozenset[str],
) -> dict[str, object]:
    artifact_filename = str(record.get("artifact_filename", "")).strip()
    step_label = str(record.get("step_label", "")).strip()
    raw_status = str(record.get("review_status", "")).strip().upper()
    allowed_statuses = {"REVIEWED", "SKIPPED", "NEEDS_FOLLOWUP", "ERROR"}
    review_status = raw_status if raw_status in allowed_statuses else "ERROR"
    status_reason = str(record.get("status_reason", "")).strip()
    if raw_status and raw_status not in allowed_statuses:
        status_reason = f"INVALID_REVIEW_STATUS:{raw_status}"
    if artifact_filename and known_artifacts and artifact_filename not in known_artifacts:
        status_reason = status_reason or "ARTIFACT_NOT_LISTED_IN_SCENARIO_REVIEW_BUNDLE"
    if not artifact_filename:
        status_reason = status_reason or "ARTIFACT_FILENAME_REQUIRED"
        review_status = "ERROR"
    if not step_label:
        step_label = artifact_filename or "unlabeled review step"
    record_hash_source = {
        "artifact_filename": artifact_filename,
        "step_label": step_label,
        "review_status": review_status,
        "status_reason": status_reason,
        "operator_note": str(record.get("operator_note", "")).strip(),
        "evidence_hash": str(record.get("evidence_hash", "")).strip(),
        "review_order_index": _runtime_export_scenario_review_order_index(
            artifact_filename,
            review_order,
        ),
    }
    return {
        **record_hash_source,
        "record_hash": stable_hash_payload(record_hash_source),
    }


def _runtime_export_scenario_review_checklist_template_record(
    artifact_filename: str,
    *,
    index: int,
    scenario_review_bundle: Mapping[str, Any],
    audit_index: Mapping[str, Any],
    artifact_hashes: Mapping[str, str],
) -> dict[str, object]:
    evidence_hash = _runtime_export_scenario_review_evidence_hash(
        artifact_filename,
        scenario_review_bundle=scenario_review_bundle,
        audit_index=audit_index,
        artifact_hashes=artifact_hashes,
    )
    evidence_source = _runtime_export_scenario_review_evidence_source(
        artifact_filename,
        evidence_hash,
    )
    record = {
        "artifact_filename": artifact_filename,
        "step_label": _runtime_export_scenario_review_step_label(
            artifact_filename,
            index,
        ),
        "review_status": "NEEDS_FOLLOWUP",
        "status_reason": (
            "OPERATOR_REVIEW_REQUIRED"
            if evidence_hash
            else "EVIDENCE_HASH_NOT_AVAILABLE"
        ),
        "operator_note": "",
        "evidence_hash": evidence_hash,
        "evidence_present": bool(evidence_hash),
        "evidence_source": evidence_source,
        "review_order_index": index,
    }
    return {
        **record,
        "template_record_hash": stable_hash_payload(record),
    }


def _runtime_export_scenario_review_template_comparison_record(
    template_record: Mapping[str, Any],
    checklist_record: Mapping[str, Any] | None,
) -> dict[str, object]:
    artifact_filename = str(template_record.get("artifact_filename", ""))
    checklist = _mapping(checklist_record)
    template_evidence_hash = str(template_record.get("evidence_hash", ""))
    checklist_evidence_hash = str(checklist.get("evidence_hash", ""))
    checklist_review_status = str(checklist.get("review_status", ""))
    audit_index_refresh_only = (
        artifact_filename == "export_package_audit_index_v1.json"
        and bool(checklist)
        and bool(checklist_evidence_hash)
        and bool(template_evidence_hash)
        and checklist_evidence_hash != template_evidence_hash
    )
    issue_labels: list[str] = []
    if not checklist:
        issue_labels.append("MISSING_CHECKLIST_RECORD")
    if (
        checklist
        and checklist_evidence_hash != template_evidence_hash
        and not audit_index_refresh_only
    ):
        issue_labels.append("EVIDENCE_HASH_MISMATCH")
    if checklist and checklist_review_status != "REVIEWED":
        issue_labels.append("OPERATOR_REVIEW_NOT_REVIEWED")
    comparison_status = "ALIGNED"
    if "MISSING_CHECKLIST_RECORD" in issue_labels:
        comparison_status = "MISSING"
    elif "EVIDENCE_HASH_MISMATCH" in issue_labels:
        comparison_status = "DRIFT"
    elif "OPERATOR_REVIEW_NOT_REVIEWED" in issue_labels:
        comparison_status = "ATTENTION"
    record = {
        "artifact_filename": artifact_filename,
        "step_label": str(template_record.get("step_label", "")),
        "review_order_index": _integer(template_record.get("review_order_index")),
        "template_evidence_hash": template_evidence_hash,
        "template_record_hash": str(template_record.get("template_record_hash", "")),
        "checklist_evidence_hash": checklist_evidence_hash,
        "checklist_record_hash": str(checklist.get("record_hash", "")),
        "checklist_review_status": checklist_review_status,
        "comparison_status": comparison_status,
        "issue_labels": tuple(issue_labels),
    }
    return {
        **record,
        "comparison_record_hash": stable_hash_payload(record),
    }


def _runtime_export_scenario_review_template_extra_record(
    checklist_record: Mapping[str, Any],
) -> dict[str, object]:
    record = {
        "artifact_filename": str(checklist_record.get("artifact_filename", "")),
        "step_label": str(checklist_record.get("step_label", "")),
        "review_order_index": _integer(checklist_record.get("review_order_index")),
        "checklist_evidence_hash": str(checklist_record.get("evidence_hash", "")),
        "checklist_record_hash": str(checklist_record.get("record_hash", "")),
        "checklist_review_status": str(checklist_record.get("review_status", "")),
        "comparison_status": "EXTRA",
        "issue_labels": ("EXTRA_CHECKLIST_RECORD",),
    }
    return {
        **record,
        "comparison_record_hash": stable_hash_payload(record),
    }


def _runtime_export_artifact_hashes_by_filename(
    audit_index: Mapping[str, Any],
) -> dict[str, str]:
    return {
        str(record.get("filename", "")): str(record.get("sha256", ""))
        for record in _file_records(_mapping(audit_index).get("artifact_hashes"))
        if str(record.get("filename", ""))
    }


def _runtime_export_scenario_review_evidence_hash(
    artifact_filename: str,
    *,
    scenario_review_bundle: Mapping[str, Any],
    audit_index: Mapping[str, Any],
    artifact_hashes: Mapping[str, str],
) -> str:
    filename = str(artifact_filename)
    if filename == "scenario_review_bundle_v1.json":
        return str(scenario_review_bundle.get("scenario_review_hash", ""))
    if filename == "export_package_audit_index_v1.json":
        return str(audit_index.get("audit_hash", ""))
    if filename == "review_summary_v1.json":
        return str(_mapping(scenario_review_bundle.get("review_summary")).get("summary_hash", ""))
    if filename == "diagnostics_bundle_v1.json":
        return str(
            _mapping(scenario_review_bundle.get("diagnostics")).get(
                "diagnostics_hash",
                "",
            )
        )
    if filename == "network_kpi_benchmark_validation_v1.json":
        return str(
            _mapping(
                scenario_review_bundle.get("network_kpi_benchmark_validation")
            ).get("validation_hash", "")
        )
    if filename == "network_kpi_formula_evidence_v1.json":
        return str(
            _mapping(
                scenario_review_bundle.get("network_kpi_formula_evidence")
            ).get("evidence_hash", "")
        )
    if filename == "user_service_request_summary_v2.json":
        return str(
            _mapping(scenario_review_bundle.get("user_service_requests")).get(
                "summary_hash",
                "",
            )
        )
    if filename == "traffic_demand_explanation_v1.json":
        return str(
            _mapping(scenario_review_bundle.get("traffic_demand_explanation")).get(
                "evidence_hash",
                "",
            )
        )
    if filename == "route_comparison_review_report_v1.json":
        return str(audit_index.get("route_comparison_review_report_hash", ""))
    if filename == "service_trace_comparison_review_report_v1.json":
        return str(
            audit_index.get("service_trace_comparison_review_report_hash", "")
        )
    if filename == "manifest.json":
        return str(
            _mapping(scenario_review_bundle.get("reproducibility")).get(
                "manifest_hash",
                "",
            )
        )
    if filename == "config_snapshot.json":
        return str(
            _mapping(scenario_review_bundle.get("user_configuration")).get(
                "config_hash",
                "",
            )
        )
    return str(artifact_hashes.get(filename, ""))


def _runtime_export_scenario_review_evidence_source(
    artifact_filename: str,
    evidence_hash: str,
) -> str:
    if not evidence_hash:
        return "MISSING"
    if artifact_filename in {
        "events.jsonl",
        "metrics.csv",
        "summary.json",
        "service_lifecycle_trace_v2.json",
    }:
        return "AUDIT_INDEX_ARTIFACT_SHA256"
    return "BACKEND_REVIEW_EVIDENCE_HASH"


def _runtime_export_scenario_review_step_label(
    artifact_filename: str,
    index: int,
) -> str:
    labels = {
        "scenario_review_bundle_v1.json": "scenario entry",
        "export_package_audit_index_v1.json": "audit index",
        "review_summary_v1.json": "review summary",
        "diagnostics_bundle_v1.json": "diagnostics",
        "network_kpi_benchmark_validation_v1.json": "network KPI benchmark",
        "network_kpi_formula_evidence_v1.json": "network KPI formula evidence",
        "traffic_demand_explanation_v1.json": "traffic demand",
        "user_service_request_summary_v2.json": "user services",
        "service_lifecycle_trace_v2.json": "service trace",
        "service_trace_comparison_review_report_v1.json": "service trace review",
        "route_comparison_review_report_v1.json": "route review",
        "manifest.json": "manifest",
        "config_snapshot.json": "configuration",
        "events.jsonl": "event evidence",
        "metrics.csv": "metrics",
        "summary.json": "summary",
    }
    return f"{index + 1} {labels.get(artifact_filename, artifact_filename)}"


def _runtime_export_scenario_review_recommended_coverage(
    review_order: tuple[str, ...],
    records: tuple[Mapping[str, Any], ...],
) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
    reviewed: list[str] = []
    missing: list[str] = []
    attention: list[str] = []
    for filename in review_order:
        matching_statuses = tuple(
            str(record.get("review_status", ""))
            for record in records
            if str(record.get("artifact_filename", "")) == filename
        )
        if not matching_statuses:
            missing.append(filename)
        elif all(status == "REVIEWED" for status in matching_statuses):
            reviewed.append(filename)
        else:
            attention.append(filename)
    return tuple(reviewed), tuple(missing), tuple(attention)


def _runtime_export_scenario_review_order_index(
    artifact_filename: str,
    review_order: tuple[str, ...],
) -> int:
    try:
        return review_order.index(artifact_filename)
    except ValueError:
        return len(review_order) + 1


def _runtime_export_route_trust_evidence(
    status: Mapping[str, Any],
) -> dict[str, object]:
    route_trust = _mapping(status.get("route_provenance_trust_summary_v1"))
    evidence_present = bool(route_trust)
    if not evidence_present:
        return {
            "version": "v1",
            "trust_id": "",
            "source": "config_snapshot.status.route_provenance_trust_summary_v1",
            "evidence_present": False,
            "route_model": "UNKNOWN",
            "packet_level_simulation": False,
            "all_pairs_computation": False,
            "trust_status": "MISSING_ROUTE_TRUST_EVIDENCE",
            "route_count": 0,
            "assessed_route_count": 0,
            "hidden_route_count": 0,
            "available_route_count": 0,
            "blocked_route_count": 0,
            "over_demand_route_count": 0,
            "explained_route_count": 0,
            "missing_explanation_count": 0,
            "path_context_route_count": 0,
            "next_hop_route_count": 0,
            "loss_proxy_route_count": 0,
            "bottleneck_components": (),
            "sample_route_ids": (),
            "caveats": (
                "Runtime status did not expose route_provenance_trust_summary_v1.",
            ),
        }
    return {
        "version": "v1",
        "trust_id": str(route_trust.get("trust_id", "")),
        "source": "config_snapshot.status.route_provenance_trust_summary_v1",
        "evidence_present": True,
        "route_summary_source": str(route_trust.get("source", "")),
        "route_model": str(route_trust.get("route_model", "")),
        "packet_level_simulation": _bool(route_trust.get("packet_level_simulation")),
        "all_pairs_computation": _bool(route_trust.get("all_pairs_computation")),
        "trust_status": str(route_trust.get("trust_status", "")),
        "route_count": _integer(route_trust.get("route_count")),
        "assessed_route_count": _integer(
            route_trust.get("assessed_route_count", route_trust.get("window_item_count"))
        ),
        "hidden_route_count": _integer(route_trust.get("hidden_route_count")),
        "available_route_count": _integer(route_trust.get("available_route_count")),
        "blocked_route_count": _integer(route_trust.get("blocked_route_count")),
        "over_demand_route_count": _integer(
            route_trust.get("over_demand_route_count")
        ),
        "explained_route_count": _integer(route_trust.get("explained_route_count")),
        "missing_explanation_count": _integer(
            route_trust.get("missing_explanation_count")
        ),
        "path_context_route_count": _integer(
            route_trust.get("path_context_route_count")
        ),
        "next_hop_route_count": _integer(route_trust.get("next_hop_route_count")),
        "loss_proxy_route_count": _integer(route_trust.get("loss_proxy_route_count")),
        "bottleneck_components": _string_tuple(
            route_trust.get("bottleneck_components")
        ),
        "sample_route_ids": _string_tuple(route_trust.get("sample_route_ids")),
        "caveats": _string_tuple(route_trust.get("caveats")),
    }


def _runtime_export_network_kpi_validation_evidence(
    status: Mapping[str, Any],
) -> dict[str, object]:
    validation = _mapping(status.get("network_kpi_benchmark_validation_v1"))
    evidence_present = bool(validation)
    if not evidence_present:
        evidence: dict[str, object] = {
            "version": "v1",
            "validation_id": "",
            "source": "config_snapshot.status.network_kpi_benchmark_validation_v1",
            "evidence_present": False,
            "benchmark_profile": "UNKNOWN",
            "metric_model": "UNKNOWN",
            "validation_status": "MISSING_KPI_BENCHMARK_VALIDATION",
            "check_count": 0,
            "passed_check_count": 0,
            "warning_check_count": 0,
            "failed_check_count": 0,
            "missing_check_count": 0,
            "packet_level_simulation": False,
            "acceptable_for_demo_review": False,
            "caveats": (
                "Runtime status did not expose network_kpi_benchmark_validation_v1.",
            ),
        }
        evidence["validation_hash"] = stable_hash_payload(evidence)
        return evidence

    failed_check_count = _integer(validation.get("failed_check_count"))
    validation_status = str(validation.get("validation_status", ""))
    acceptable = (
        failed_check_count == 0
        and validation_status in {"PASS", "WARN", "INSUFFICIENT_DATA"}
        and validation.get("packet_level_simulation") is not True
    )
    evidence = {
        "version": "v1",
        "validation_id": str(validation.get("validation_id", "")),
        "source": "config_snapshot.status.network_kpi_benchmark_validation_v1",
        "evidence_present": True,
        "benchmark_profile": str(validation.get("benchmark_profile", "")),
        "metric_model": str(validation.get("metric_model", "")),
        "validation_status": validation_status,
        "check_count": _integer(validation.get("check_count")),
        "passed_check_count": _integer(validation.get("passed_check_count")),
        "warning_check_count": _integer(validation.get("warning_check_count")),
        "failed_check_count": failed_check_count,
        "missing_check_count": _integer(validation.get("missing_check_count")),
        "packet_level_simulation": validation.get("packet_level_simulation") is True,
        "acceptable_for_demo_review": acceptable,
        "caveats": _string_tuple(validation.get("caveats")),
    }
    evidence["validation_hash"] = stable_hash_payload(evidence)
    return evidence


def _runtime_export_network_kpi_formula_evidence(
    status: Mapping[str, Any],
) -> dict[str, object]:
    formula_evidence = _mapping(status.get("network_kpi_formula_evidence_v1"))
    evidence_present = bool(formula_evidence)
    if not evidence_present:
        evidence: dict[str, object] = {
            "version": "v1",
            "evidence_id": "",
            "source": "config_snapshot.status.network_kpi_formula_evidence_v1",
            "evidence_present": False,
            "metric_model": "UNKNOWN",
            "formula_evidence_status": "MISSING_KPI_FORMULA_EVIDENCE",
            "kpi_count": 0,
            "observed_kpi_count": 0,
            "runtime_value_missing_count": 0,
            "selected_input_count": 0,
            "selected_observed_input_count": 0,
            "missing_selected_input_count": 0,
            "time_varying_kpi_count": 0,
            "flat_kpi_count": 0,
            "packet_level_simulation": False,
            "acceptable_for_demo_review": False,
            "caveats": (
                "Runtime status did not expose network_kpi_formula_evidence_v1.",
            ),
        }
        evidence["evidence_hash"] = stable_hash_payload(evidence)
        return evidence

    formula_status = str(formula_evidence.get("formula_evidence_status", ""))
    acceptable = (
        formula_status
        in {
            "FORMULA_AND_TIME_EVIDENCE_READY",
            "FORMULA_READY",
            "FORMULA_READY_FLAT_SERIES",
            "FORMULA_READY_INSUFFICIENT_SERIES",
        }
        and formula_evidence.get("packet_level_simulation") is not True
        and _integer(formula_evidence.get("runtime_value_missing_count")) == 0
        and _integer(formula_evidence.get("missing_selected_input_count")) == 0
    )
    evidence = {
        "version": "v1",
        "evidence_id": str(formula_evidence.get("evidence_id", "")),
        "source": "config_snapshot.status.network_kpi_formula_evidence_v1",
        "runtime_status_source": str(formula_evidence.get("source", "")),
        "evidence_present": True,
        "provenance_id": str(formula_evidence.get("provenance_id", "")),
        "calibration_id": str(formula_evidence.get("calibration_id", "")),
        "metric_model": str(formula_evidence.get("metric_model", "")),
        "formula_evidence_status": formula_status,
        "kpi_count": _integer(formula_evidence.get("kpi_count")),
        "observed_kpi_count": _integer(formula_evidence.get("observed_kpi_count")),
        "runtime_value_missing_count": _integer(
            formula_evidence.get("runtime_value_missing_count")
        ),
        "selected_input_count": _integer(formula_evidence.get("selected_input_count")),
        "selected_observed_input_count": _integer(
            formula_evidence.get("selected_observed_input_count")
        ),
        "missing_selected_input_count": _integer(
            formula_evidence.get("missing_selected_input_count")
        ),
        "time_varying_kpi_count": _integer(
            formula_evidence.get("time_varying_kpi_count")
        ),
        "flat_kpi_count": _integer(formula_evidence.get("flat_kpi_count")),
        "packet_level_simulation": (
            formula_evidence.get("packet_level_simulation") is True
        ),
        "acceptable_for_demo_review": acceptable,
        "caveats": _string_tuple(formula_evidence.get("caveats")),
    }
    evidence["evidence_hash"] = stable_hash_payload(evidence)
    return evidence


def _runtime_export_user_configuration_template_validation_evidence(
    config_snapshot: Mapping[str, Any],
) -> dict[str, object]:
    template_validation = _mapping(
        config_snapshot.get("user_configuration_template_validation_v1")
    )
    evidence_present = bool(template_validation)
    if not evidence_present:
        evidence: dict[str, object] = {
            "version": "v1",
            "evidence_id": "",
            "source": "config_snapshot.user_configuration_template_validation_v1",
            "evidence_present": False,
            "schema_id": USER_CONFIGURATION_SCHEMA_V2_ID,
            "validation_scope": "UNKNOWN",
            "validation_status": "MISSING_TEMPLATE_VALIDATION_EVIDENCE",
            "template_count": 0,
            "valid_template_count": 0,
            "invalid_template_count": 0,
            "missing_file_count": 0,
            "load_failed_count": 0,
            "validation_failed_count": 0,
            "all_templates_valid": False,
            "packet_level_simulation": False,
            "external_simulators": False,
            "acceptable_for_demo_review": False,
            "invalid_template_ids": (),
            "caveats": (
                "Config snapshot did not include user_configuration_template_validation_v1.",
            ),
        }
        evidence["evidence_hash"] = stable_hash_payload(evidence)
        return evidence

    template_rows = _records(template_validation.get("templates"))
    invalid_rows = tuple(
        row
        for row in template_rows
        if row.get("file_exists") is not True
        or row.get("load_ok") is not True
        or row.get("validation_ok") is not True
    )
    model_boundaries = _mapping(template_validation.get("model_boundaries"))
    packet_level = model_boundaries.get("packet_level_simulation") is True
    external_simulators = model_boundaries.get("external_simulators") is True
    all_templates_valid = template_validation.get("all_templates_valid") is True
    evidence = {
        "version": "v1",
        "evidence_id": str(template_validation.get("evidence_id", "")),
        "source": "config_snapshot.user_configuration_template_validation_v1",
        "evidence_present": True,
        "schema_id": str(
            template_validation.get("schema_id", USER_CONFIGURATION_SCHEMA_V2_ID)
        ),
        "validation_scope": str(template_validation.get("validation_scope", "")),
        "validation_status": (
            "ALL_TEMPLATES_VALID"
            if all_templates_valid
            else "TEMPLATE_VALIDATION_REQUIRES_REVIEW"
        ),
        "template_count": _integer(template_validation.get("template_count")),
        "valid_template_count": _integer(
            template_validation.get("valid_template_count")
        ),
        "invalid_template_count": _integer(
            template_validation.get("invalid_template_count")
        ),
        "missing_file_count": sum(
            1 for row in template_rows if row.get("file_exists") is not True
        ),
        "load_failed_count": sum(
            1
            for row in template_rows
            if row.get("file_exists") is True and row.get("load_ok") is not True
        ),
        "validation_failed_count": sum(
            1
            for row in template_rows
            if row.get("load_ok") is True and row.get("validation_ok") is not True
        ),
        "all_templates_valid": all_templates_valid,
        "packet_level_simulation": packet_level,
        "external_simulators": external_simulators,
        "forbidden_integrations": _string_tuple(
            model_boundaries.get("forbidden_integrations")
        ),
        "acceptable_for_demo_review": (
            all_templates_valid and not packet_level and not external_simulators
        ),
        "invalid_template_ids": tuple(str(row.get("id", "")) for row in invalid_rows),
        "template_evidence_hash": str(template_validation.get("evidence_hash", "")),
        "notes": _string_tuple(template_validation.get("notes")),
    }
    evidence["evidence_hash"] = stable_hash_payload(evidence)
    return evidence


def _runtime_export_traffic_demand_explanation_evidence(
    config_snapshot: Mapping[str, Any],
) -> dict[str, object]:
    generated_config = _mapping(config_snapshot.get("generated_config"))
    backend_summary = _mapping(generated_config.get("backend_summary"))
    explanation = _mapping(backend_summary.get("traffic_demand_explanation_v1"))
    evidence_present = bool(explanation)
    source = "config_snapshot.generated_config.backend_summary.traffic_demand_explanation_v1"
    if not evidence_present:
        evidence: dict[str, object] = {
            "version": "v1",
            "evidence_id": RUNTIME_EXPORT_TRAFFIC_DEMAND_EXPLANATION_V1_ID,
            "source": source,
            "evidence_present": False,
            "request_count": 0,
            "configured_request_count": 0,
            "explained_request_count": 0,
            "input_flow_count": 0,
            "task_request_count": 0,
            "output_flow_count": 0,
            "communication_only_request_count": 0,
            "compute_service_request_count": 0,
            "active_traffic_classes": (),
            "traffic_class_row_count": 0,
            "per_user_state_count": 0,
            "packet_level_simulation": False,
            "frontend_inference_required": False,
            "acceptable_for_demo_review": False,
            "caveats": (
                "Generated config did not expose backend_summary.traffic_demand_explanation_v1.",
            ),
        }
        evidence["evidence_hash"] = stable_hash_payload(evidence)
        return evidence

    correlation = _mapping(explanation.get("correlation_summary"))
    active_classes = _string_tuple(explanation.get("active_traffic_classes"))
    row_count = len(_records(explanation.get("traffic_class_rows")))
    per_user_count = len(_records(explanation.get("per_user_active_service_state")))
    packet_level = correlation.get("packet_level_simulation") is True
    frontend_inference = (
        explanation.get("frontend_inference_required") is True
        or correlation.get("frontend_inference_required") is True
    )
    compute_request_count = _integer(explanation.get("compute_service_request_count"))
    compute_correlation_ok = (
        compute_request_count == 0
        or (
            correlation.get("all_compute_services_have_task") is True
            and correlation.get("all_compute_services_have_output_flow") is True
        )
    )
    evidence = {
        "version": "v1",
        "evidence_id": str(
            explanation.get(
                "explanation_id",
                RUNTIME_EXPORT_TRAFFIC_DEMAND_EXPLANATION_V1_ID,
            )
        ),
        "source": source,
        "runtime_summary_source": str(explanation.get("source", "")),
        "evidence_present": True,
        "request_count": _integer(explanation.get("request_count")),
        "configured_request_count": _integer(
            explanation.get(
                "configured_request_count",
                explanation.get("request_count"),
            )
        ),
        "explained_request_count": _integer(
            explanation.get(
                "explained_request_count",
                explanation.get("request_count"),
            )
        ),
        "input_flow_count": _integer(explanation.get("input_flow_count")),
        "task_request_count": _integer(explanation.get("task_request_count")),
        "output_flow_count": _integer(explanation.get("output_flow_count")),
        "communication_only_request_count": _integer(
            explanation.get("communication_only_request_count")
        ),
        "compute_service_request_count": compute_request_count,
        "active_traffic_classes": active_classes,
        "active_traffic_class_count": len(active_classes),
        "traffic_class_row_count": row_count,
        "per_user_state_count": per_user_count,
        "explanation_window_policy": str(
            explanation.get("explanation_window_policy", "")
        ),
        "endpoint_window_policy": str(explanation.get("endpoint_window_policy", "")),
        "all_compute_services_have_task": (
            correlation.get("all_compute_services_have_task") is True
        ),
        "all_compute_services_have_output_flow": (
            correlation.get("all_compute_services_have_output_flow") is True
        ),
        "packet_level_simulation": packet_level,
        "frontend_inference_required": frontend_inference,
        "acceptable_for_demo_review": (
            not packet_level and not frontend_inference and compute_correlation_ok
        ),
        "model_assumptions": _string_tuple(explanation.get("model_assumptions")),
        "explanation_hash": stable_hash_payload(explanation),
    }
    evidence["evidence_hash"] = stable_hash_payload(evidence)
    return evidence


def _runtime_export_user_service_request_evidence(
    status: Mapping[str, Any],
) -> dict[str, object]:
    summary = _mapping(status.get("user_service_request_summary_v2"))
    policy = _mapping(status.get("runtime_export_user_service_request_policy_v1"))
    evidence_present = bool(summary)
    if not evidence_present:
        evidence: dict[str, object] = {
            "version": "v2",
            "evidence_id": RUNTIME_EXPORT_USER_SERVICE_REQUEST_SUMMARY_V2_ID,
            "source": "config_snapshot.status.user_service_request_summary_v2",
            "evidence_present": False,
            "request_model": "UNKNOWN",
            "request_count": 0,
            "exported_request_count": 0,
            "hidden_request_count": 0,
            "active_request_count": 0,
            "compute_request_count": 0,
            "network_waiting_request_count": 0,
            "packet_level_simulation": False,
            "frontend_inference_required": False,
            "artifact_window_only": True,
            "caveats": (
                "Runtime status did not expose user_service_request_summary_v2.",
            ),
        }
        evidence["summary_hash"] = stable_hash_payload(evidence)
        return evidence

    exported_request_count = _integer(summary.get("item_count"))
    request_count = _integer(summary.get("request_count", summary.get("user_count")))
    hidden_request_count = _integer(
        summary.get(
            "hidden_request_count",
            max(0, request_count - exported_request_count),
        )
    )
    evidence = {
        "version": "v2",
        "evidence_id": RUNTIME_EXPORT_USER_SERVICE_REQUEST_SUMMARY_V2_ID,
        "source": "config_snapshot.status.user_service_request_summary_v2",
        "evidence_present": True,
        "request_model": str(summary.get("request_model", "")),
        "route_model": str(summary.get("route_model", "")),
        "compute_model": str(summary.get("compute_model", "")),
        "request_count": request_count,
        "exported_request_count": exported_request_count,
        "hidden_request_count": hidden_request_count,
        "active_request_count": _integer(summary.get("active_request_count")),
        "communication_request_count": _integer(
            summary.get("communication_request_count")
        ),
        "compute_request_count": _integer(summary.get("compute_request_count")),
        "network_waiting_request_count": _integer(
            summary.get("network_waiting_request_count")
        ),
        "completed_request_count": _integer(summary.get("completed_request_count")),
        "service_class_counts": tuple(_records(summary.get("service_class_counts"))),
        "terminal_state_counts": tuple(_records(summary.get("terminal_state_counts"))),
        "packet_level_simulation": summary.get("packet_level_simulation") is True,
        "frontend_inference_required": (
            summary.get("frontend_inference_required") is True
        ),
        "artifact_window_only": bool(policy.get("artifact_window_only", True)),
        "export_limit": _integer(
            policy.get("user_service_request_limit", summary.get("limit"))
        ),
        "policy": str(policy.get("policy", "")),
        "model_assumptions": _string_tuple(summary.get("model_assumptions")),
    }
    evidence["summary_hash"] = stable_hash_payload(evidence)
    return evidence


def _runtime_export_route_detail_record(
    item: Mapping[str, Any],
) -> dict[str, object]:
    path = _string_tuple(item.get("path"))
    next_hop_ids = _string_tuple(item.get("next_hop_ids"))
    return {
        "route_id": str(item.get("route_id", "")),
        "flow_id": str(item.get("flow_id", "")),
        "user_id": str(item.get("user_id", "")),
        "source_id": str(item.get("source_id", "")),
        "destination_id": str(item.get("destination_id", "")),
        "selected_satellite_id": str(item.get("selected_satellite_id", "")),
        "primary_next_hop_id": str(item.get("primary_next_hop_id", "")),
        "next_hop_ids": next_hop_ids,
        "hop_count": _integer(item.get("hop_count")),
        "path": path,
        "path_label": str(item.get("path_label", "")),
        "available": _bool(item.get("available")),
        "capacity_mbps": _number(item.get("capacity_mbps")),
        "demand_mbps": _number(item.get("demand_mbps")),
        "latency_s": _number(item.get("latency_s")),
        "loss_proxy_rate": _number(item.get("loss_proxy_rate")),
        "route_pressure_proxy": _number(item.get("route_pressure_proxy")),
        "business_type": str(item.get("business_type", "")),
        "business_label": str(item.get("business_label", "")),
        "bottleneck_component": str(item.get("bottleneck_component", "")),
        "bottleneck_reason": str(item.get("bottleneck_reason", "")),
        "bottleneck_reason_label": str(item.get("bottleneck_reason_label", "")),
        "explanation_label": str(item.get("explanation_label", "")),
    }


def _runtime_export_service_trace_record(
    item: Mapping[str, Any],
) -> dict[str, object]:
    stages = tuple(
        _runtime_export_service_trace_stage_record(stage)
        for stage in _records(item.get("stages"))
    )
    return {
        "trace_id": str(item.get("trace_id", "")),
        "service_id": str(item.get("service_id", "")),
        "task_id": str(item.get("task_id", "")),
        "service_class": str(item.get("service_class", "")),
        "input_flow_id": str(item.get("input_flow_id", "")),
        "output_flow_id": str(item.get("output_flow_id", "")),
        "input_route_id": str(item.get("input_route_id", "")),
        "output_route_id": str(item.get("output_route_id", "")),
        "compute_node_id": str(item.get("compute_node_id", "")),
        "placement_status": str(item.get("placement_status", "")),
        "input_network_latency_s": _number(item.get("input_network_latency_s")),
        "compute_queue_delay_s": _number(item.get("compute_queue_delay_s")),
        "compute_execution_delay_s": _number(item.get("compute_execution_delay_s")),
        "output_network_latency_s": _number(item.get("output_network_latency_s")),
        "total_latency_s": _number(item.get("total_latency_s")),
        "terminal_state": _runtime_export_service_trace_code(
            item.get("terminal_state"),
            "INCOMPLETE",
        ),
        "terminal_state_reason": _runtime_export_service_trace_code(
            item.get("terminal_state_reason"),
            "NO_COMPONENT_OBSERVATIONS",
        ),
        "stage_count": _integer(item.get("stage_count", len(stages))),
        "observed_stage_count": _integer(item.get("observed_stage_count")),
        "pending_stage_count": _integer(item.get("pending_stage_count")),
        "stages": stages,
    }


def _runtime_export_user_service_request_record(
    item: Mapping[str, Any],
) -> dict[str, object]:
    path = _string_tuple(item.get("path"))
    return {
        "detail_hash": str(item.get("detail_hash", "")),
        "user_id": str(item.get("user_id", "")),
        "platform_type": str(item.get("platform_type", "")),
        "platform_type_label": str(item.get("platform_type_label", "")),
        "cell_id": str(item.get("cell_id", "")),
        "status": str(item.get("status", "")),
        "request_id": str(item.get("request_id", "")),
        "service_request_id": str(item.get("service_request_id", "")),
        "service_class": str(item.get("service_class", "")),
        "service_class_label": str(item.get("service_class_label", "")),
        "business_type": str(item.get("business_type", "")),
        "business_label": str(item.get("business_label", "")),
        "request_active": _bool(item.get("request_active")),
        "communication_request_active": _bool(
            item.get("communication_request_active")
        ),
        "compute_request_active": _bool(item.get("compute_request_active")),
        "network_waiting": _bool(item.get("network_waiting"))
        or _integer(item.get("network_queue_depth")) > 0
        or _integer(item.get("network_queue_count")) > 0,
        "terminal_state": str(item.get("terminal_state", "")),
        "terminal_state_label": str(item.get("terminal_state_label", "")),
        "route_id": str(item.get("route_id", "")),
        "flow_id": str(item.get("flow_id", "")),
        "task_id": str(item.get("task_id", "")),
        "trace_id": str(item.get("trace_id", "")),
        "target_node_id": str(item.get("target_node_id", "")),
        "selected_satellite_id": str(item.get("selected_satellite_id", "")),
        "destination_id": str(item.get("destination_id", "")),
        "next_hop_id": str(item.get("next_hop_id", "")),
        "compute_node_id": str(item.get("compute_node_id", "")),
        "network_queue_depth": _integer(item.get("network_queue_depth")),
        "network_queue_count": _integer(item.get("network_queue_count")),
        "network_queue_reason": str(item.get("network_queue_reason", "")),
        "network_queue_reason_label": str(
            item.get("network_queue_reason_label", "")
        ),
        "route_available": _bool(item.get("route_available")),
        "communication_route_count": _integer(
            item.get("communication_route_count")
        ),
        "available_route_count": _integer(item.get("available_route_count")),
        "compute_service_count": _integer(item.get("compute_service_count")),
        "latency_s": _number(item.get("latency_s")),
        "capacity_mbps": _number(item.get("capacity_mbps")),
        "loss_proxy_rate": _number(item.get("loss_proxy_rate")),
        "service_state": str(item.get("service_state", "")),
        "service_task_id": str(item.get("service_task_id", "")),
        "service_complete": _bool(item.get("service_complete")),
        "service_total_latency_s": _number(item.get("service_total_latency_s")),
        "input_network_latency_s": _number(item.get("input_network_latency_s")),
        "compute_queue_delay_s": _number(item.get("compute_queue_delay_s")),
        "compute_execution_delay_s": _number(
            item.get("compute_execution_delay_s")
        ),
        "output_network_latency_s": _number(item.get("output_network_latency_s")),
        "input_route_id": str(item.get("input_route_id", "")),
        "output_route_id": str(item.get("output_route_id", "")),
        "service_placement_status": str(
            item.get("service_placement_status", "")
        ),
        "service_placement_policy": str(
            item.get("service_placement_policy", "")
        ),
        "service_placement_bottleneck_resource": str(
            item.get("service_placement_bottleneck_resource", "")
        ),
        "service_placement_candidate_count": _integer(
            item.get("service_placement_candidate_count")
        ),
        "service_placement_capable_candidate_count": _integer(
            item.get("service_placement_capable_candidate_count")
        ),
        "service_placement_candidate_queue_label": str(
            item.get("service_placement_candidate_queue_label", "")
        ),
        "input_output_coupled": _bool(item.get("input_output_coupled")),
        "latency_components_observed": _bool(
            item.get("latency_components_observed")
        ),
        "route_model": str(item.get("route_model", "")),
        "service_model": str(item.get("service_model", "")),
        "packet_level_simulation": _bool(item.get("packet_level_simulation")),
        "status_digest": str(item.get("status_digest", "")),
        "active_business_type": str(item.get("active_business_type", "")),
        "active_business_label": str(item.get("active_business_label", "")),
        "request_state": str(item.get("request_state", "")),
        "request_state_label": str(item.get("request_state_label", "")),
        "path": path,
        "route_path_label": str(item.get("route_path_label", "")),
        "primary_route_id": str(item.get("primary_route_id", "")),
        "primary_flow_id": str(item.get("primary_flow_id", "")),
        "primary_next_hop_id": str(item.get("primary_next_hop_id", "")),
    }


def _runtime_export_service_trace_stage_record(
    stage: Mapping[str, Any],
) -> dict[str, object]:
    return {
        "stage_index": _integer(stage.get("stage_index")),
        "stage_id": str(stage.get("stage_id", "")),
        "component": str(stage.get("component", "")),
        "stage_kind": str(stage.get("stage_kind", "")),
        "stage_label": str(stage.get("stage_label", "")),
        "stage_status": str(stage.get("stage_status", "")),
        "duration_s": _number(stage.get("duration_s")),
        "flow_id": str(stage.get("flow_id", "")),
        "route_id": str(stage.get("route_id", "")),
    }


def _runtime_export_route_comparison_report_record(
    record: Mapping[str, Any],
    route_comparison_review: Mapping[str, Any],
) -> dict[str, object]:
    field_order = _string_tuple(route_comparison_review.get("compared_fields"))
    compared_fields = _ordered_subset(
        _string_tuple(record.get("compared_fields")) or field_order,
        field_order,
    )
    different_fields = _ordered_subset(
        _string_tuple(record.get("different_fields")),
        field_order,
    )
    status = str(record.get("comparison_status", "")).strip().upper()
    if status not in {"MATCH", "DIFFERENT", "UNAVAILABLE", "ERROR"}:
        status = "ERROR"
    matched_field_count = _integer(record.get("matched_field_count"))
    if matched_field_count <= 0 and compared_fields:
        matched_field_count = max(0, len(compared_fields) - len(different_fields))
    different_field_count = _integer(record.get("different_field_count"))
    if different_field_count <= 0:
        different_field_count = len(different_fields)
    return {
        "route_id": str(record.get("route_id", "")),
        "comparison_status": status,
        "package_route_detail_hash": str(
            record.get("package_route_detail_hash", "")
        ),
        "live_route_detail_hash": str(record.get("live_route_detail_hash", "")),
        "matched_field_count": matched_field_count,
        "different_field_count": different_field_count,
        "compared_fields": compared_fields,
        "different_fields": different_fields,
        "status_reason": str(record.get("status_reason", "")),
        "operator_note": str(record.get("operator_note", "")),
    }


def _runtime_export_service_trace_comparison_report_record(
    record: Mapping[str, Any],
    service_trace_comparison_review: Mapping[str, Any],
) -> dict[str, object]:
    field_order = _string_tuple(
        service_trace_comparison_review.get("compared_fields")
    )
    compared_fields = _ordered_subset(
        _string_tuple(record.get("compared_fields")) or field_order,
        field_order,
    )
    different_fields = _ordered_subset(
        _string_tuple(record.get("different_fields")),
        field_order,
    )
    status = str(record.get("comparison_status", "")).strip().upper()
    if status not in {"MATCH", "DIFFERENT", "UNAVAILABLE", "ERROR"}:
        status = "ERROR"
    matched_field_count = _integer(record.get("matched_field_count"))
    if matched_field_count <= 0 and compared_fields:
        matched_field_count = max(0, len(compared_fields) - len(different_fields))
    different_field_count = _integer(record.get("different_field_count"))
    if different_field_count <= 0:
        different_field_count = len(different_fields)
    return {
        "trace_id": str(record.get("trace_id", "")),
        "comparison_status": status,
        "package_trace_item_hash": str(
            record.get("package_trace_item_hash", "")
        ),
        "live_trace_detail_hash": str(record.get("live_trace_detail_hash", "")),
        "matched_field_count": matched_field_count,
        "different_field_count": different_field_count,
        "compared_fields": compared_fields,
        "different_fields": different_fields,
        "status_reason": str(record.get("status_reason", "")),
        "operator_note": str(record.get("operator_note", "")),
    }


def _runtime_export_service_trace_comparison_report_record_matches_filter(
    record: Mapping[str, Any],
    *,
    query: str,
    status: str,
) -> bool:
    if status != "ALL" and str(record.get("comparison_status", "")).upper() != status:
        return False
    if not query:
        return True
    values = (
        str(record.get("trace_id", "")),
        str(record.get("comparison_status", "")),
        str(record.get("package_trace_item_hash", "")),
        str(record.get("live_trace_detail_hash", "")),
        str(record.get("status_reason", "")),
        str(record.get("operator_note", "")),
        *tuple(str(value) for value in _string_tuple(record.get("compared_fields"))),
        *tuple(str(value) for value in _string_tuple(record.get("different_fields"))),
    )
    return any(query in _normalized_search_query(value) for value in values)


def _ordered_subset(
    values: tuple[str, ...],
    field_order: tuple[str, ...],
) -> tuple[str, ...]:
    if not field_order:
        return tuple(sorted(dict.fromkeys(values)))
    value_set = set(values)
    ordered = tuple(field for field in field_order if field in value_set)
    extras = tuple(sorted(value for value in value_set if value not in field_order))
    return ordered + extras


def _runtime_export_route_detail_matches_filter(
    route: Mapping[str, Any],
    *,
    query: str,
    availability: str,
    business_type: str,
    bottleneck_component: str,
) -> bool:
    normalized_availability = str(availability or "ALL").strip().upper()
    if normalized_availability == "AVAILABLE" and not _bool(route.get("available")):
        return False
    if normalized_availability == "BLOCKED" and _bool(route.get("available")):
        return False
    normalized_business_type = str(business_type or "ALL").strip().upper()
    if (
        normalized_business_type
        and normalized_business_type != "ALL"
        and str(route.get("business_type", "")).strip().upper()
        != normalized_business_type
    ):
        return False
    normalized_bottleneck = str(bottleneck_component or "ALL").strip().upper()
    if (
        normalized_bottleneck
        and normalized_bottleneck != "ALL"
        and str(route.get("bottleneck_component", "")).strip().upper()
        != normalized_bottleneck
    ):
        return False
    terms = _search_terms(query)
    if not terms:
        return True
    haystack = _runtime_export_route_detail_search_text(route)
    return all(term in haystack for term in terms)


def _runtime_export_route_detail_filter_summary(
    *,
    query: str,
    availability: str,
    business_type: str,
    bottleneck_component: str,
) -> dict[str, str]:
    return {
        "query": _normalized_search_query(query),
        "availability": _normalized_filter_value(availability, "ALL"),
        "business_type": _normalized_filter_value(business_type, "ALL"),
        "bottleneck_component": _normalized_filter_value(
            bottleneck_component,
            "ALL",
        ),
    }


def _runtime_export_route_detail_filter_applied(
    filters: Mapping[str, Any],
) -> bool:
    return (
        str(filters.get("query", "")).strip() != ""
        or str(filters.get("availability", "ALL")).upper() != "ALL"
        or str(filters.get("business_type", "ALL")).upper() != "ALL"
        or str(filters.get("bottleneck_component", "ALL")).upper() != "ALL"
    )


def _runtime_export_route_detail_search_text(route: Mapping[str, Any]) -> str:
    values = (
        str(route.get("route_id", "")),
        str(route.get("flow_id", "")),
        str(route.get("user_id", "")),
        str(route.get("source_id", "")),
        str(route.get("destination_id", "")),
        str(route.get("selected_satellite_id", "")),
        str(route.get("primary_next_hop_id", "")),
        *_string_tuple(route.get("next_hop_ids")),
        *_string_tuple(route.get("path")),
        str(route.get("path_label", "")),
        str(route.get("business_type", "")),
        str(route.get("business_label", "")),
        str(route.get("bottleneck_component", "")),
        str(route.get("bottleneck_reason", "")),
        str(route.get("bottleneck_reason_label", "")),
        str(route.get("explanation_label", "")),
    )
    return " ".join(values).lower()


def _runtime_export_service_trace_matches_filter(
    trace: Mapping[str, Any],
    *,
    query: str,
    terminal_state: str,
    compute_node_id: str,
    stage_kind: str,
    terminal_reason: str,
) -> bool:
    normalized_terminal_state = _runtime_export_service_trace_terminal_state(
        terminal_state
    )
    if (
        normalized_terminal_state != "ALL"
        and str(trace.get("terminal_state", "")).strip().upper()
        != normalized_terminal_state
    ):
        return False
    normalized_terminal_reason = _runtime_export_service_trace_terminal_reason(
        terminal_reason
    )
    if (
        normalized_terminal_reason != "ALL"
        and _runtime_export_service_trace_code(trace.get("terminal_state_reason"), "")
        != normalized_terminal_reason
    ):
        return False
    normalized_compute_node = _normalized_search_query(compute_node_id)
    if normalized_compute_node and _normalized_search_query(
        str(trace.get("compute_node_id", ""))
    ) != normalized_compute_node:
        return False
    normalized_stage_kind = _runtime_export_service_trace_stage_kind(stage_kind)
    if normalized_stage_kind != "ALL" and not any(
        _runtime_export_service_trace_stage_matches_filter(
            stage,
            normalized_stage_kind,
        )
        for stage in _records(trace.get("stages"))
    ):
        return False
    terms = _search_terms(query)
    if not terms:
        return True
    haystack = _runtime_export_service_trace_search_text(trace)
    return all(term in haystack for term in terms)


def _runtime_export_service_trace_stage_matches_filter(
    stage: Mapping[str, Any],
    stage_kind: str,
) -> bool:
    return (
        _runtime_export_service_trace_stage_kind(stage.get("stage_kind")) == stage_kind
        or _runtime_export_service_trace_stage_kind(stage.get("component"))
        == stage_kind
    )


def _runtime_export_service_trace_filter_summary(
    *,
    query: str,
    terminal_state: str,
    compute_node_id: str,
    stage_kind: str,
    terminal_reason: str,
) -> dict[str, str]:
    return {
        "query": _normalized_search_query(query),
        "terminal_state": _runtime_export_service_trace_terminal_state(
            terminal_state
        ),
        "compute_node_id": _normalized_search_query(compute_node_id),
        "stage_kind": _runtime_export_service_trace_stage_kind(stage_kind),
        "terminal_reason": _runtime_export_service_trace_terminal_reason(
            terminal_reason
        ),
    }


def _runtime_export_service_trace_filter_applied(
    filters: Mapping[str, Any],
) -> bool:
    return (
        str(filters.get("query", "")).strip() != ""
        or str(filters.get("terminal_state", "ALL")).upper() != "ALL"
        or str(filters.get("compute_node_id", "")).strip() != ""
        or str(filters.get("stage_kind", "ALL")).upper() != "ALL"
        or str(filters.get("terminal_reason", "ALL")).upper() != "ALL"
    )


def _runtime_export_service_trace_search_text(trace: Mapping[str, Any]) -> str:
    stages = _records(trace.get("stages"))
    values = (
        str(trace.get("trace_id", "")),
        str(trace.get("service_id", "")),
        str(trace.get("task_id", "")),
        str(trace.get("service_class", "")),
        str(trace.get("input_flow_id", "")),
        str(trace.get("output_flow_id", "")),
        str(trace.get("input_route_id", "")),
        str(trace.get("output_route_id", "")),
        str(trace.get("compute_node_id", "")),
        str(trace.get("placement_status", "")),
        str(trace.get("terminal_state", "")),
        str(trace.get("terminal_state_reason", "")),
        *(
            str(value)
            for stage in stages
            for value in (
                stage.get("stage_id", ""),
                stage.get("component", ""),
                stage.get("stage_kind", ""),
                stage.get("stage_label", ""),
                stage.get("stage_status", ""),
                stage.get("flow_id", ""),
                stage.get("route_id", ""),
            )
        ),
    )
    return " ".join(values).lower()


def _runtime_export_service_trace_lookup_ids(
    trace: Mapping[str, Any],
) -> tuple[str, ...]:
    values = (
        str(trace.get("trace_id", "")),
        str(trace.get("service_id", "")),
        str(trace.get("trace_id", "")).removeprefix("trace:"),
        str(trace.get("task_id", "")),
        str(trace.get("input_flow_id", "")),
        str(trace.get("output_flow_id", "")),
    )
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        normalized = value.strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        ordered.append(normalized)
    return tuple(ordered)


def _runtime_export_user_service_request_matches_filter(
    request: Mapping[str, Any],
    *,
    query: str,
    service_class: str,
    terminal_state: str,
    network_waiting: str,
) -> bool:
    normalized_service_class = _normalized_filter_value(service_class, "ALL")
    if (
        normalized_service_class
        and normalized_service_class != "ALL"
        and str(request.get("service_class", "")).strip().upper()
        != normalized_service_class
    ):
        return False
    normalized_terminal_state = _runtime_export_user_service_request_code(
        terminal_state,
        "ALL",
    )
    if (
        normalized_terminal_state != "ALL"
        and _runtime_export_user_service_request_code(
            request.get("terminal_state"),
            "",
        )
        != normalized_terminal_state
    ):
        return False
    normalized_waiting = str(network_waiting or "ALL").strip().upper()
    if normalized_waiting in {"YES", "TRUE", "WAITING"} and not _bool(
        request.get("network_waiting")
    ):
        return False
    if normalized_waiting in {"NO", "FALSE", "READY"} and _bool(
        request.get("network_waiting")
    ):
        return False
    terms = _search_terms(query)
    if not terms:
        return True
    haystack = _runtime_export_user_service_request_search_text(request)
    return all(term in haystack for term in terms)


def _runtime_export_user_service_request_filter_summary(
    *,
    query: str,
    service_class: str,
    terminal_state: str,
    network_waiting: str,
) -> dict[str, str]:
    return {
        "query": _normalized_search_query(query),
        "service_class": _normalized_filter_value(service_class, "ALL"),
        "terminal_state": _runtime_export_user_service_request_code(
            terminal_state,
            "ALL",
        ),
        "network_waiting": _runtime_export_user_service_waiting_filter(
            network_waiting
        ),
    }


def _runtime_export_user_service_request_filter_applied(
    filters: Mapping[str, Any],
) -> bool:
    return (
        str(filters.get("query", "")).strip() != ""
        or str(filters.get("service_class", "ALL")).upper() != "ALL"
        or str(filters.get("terminal_state", "ALL")).upper() != "ALL"
        or str(filters.get("network_waiting", "ALL")).upper() != "ALL"
    )


def _runtime_export_user_service_request_search_text(
    request: Mapping[str, Any],
) -> str:
    values = (
        str(request.get("user_id", "")),
        str(request.get("request_id", "")),
        str(request.get("service_request_id", "")),
        str(request.get("service_class", "")),
        str(request.get("service_class_label", "")),
        str(request.get("business_type", "")),
        str(request.get("business_label", "")),
        str(request.get("terminal_state", "")),
        str(request.get("terminal_state_label", "")),
        str(request.get("route_id", "")),
        str(request.get("flow_id", "")),
        str(request.get("task_id", "")),
        str(request.get("trace_id", "")),
        str(request.get("target_node_id", "")),
        str(request.get("selected_satellite_id", "")),
        str(request.get("destination_id", "")),
        str(request.get("next_hop_id", "")),
        str(request.get("compute_node_id", "")),
        str(request.get("network_queue_reason", "")),
        str(request.get("network_queue_reason_label", "")),
        str(request.get("service_state", "")),
        str(request.get("status_digest", "")),
        str(request.get("route_path_label", "")),
        *_string_tuple(request.get("path")),
    )
    return " ".join(values).lower()


def _runtime_export_user_service_waiting_filter(value: object) -> str:
    normalized = str(value or "ALL").strip().upper()
    if normalized in {"YES", "TRUE", "WAITING"}:
        return "WAITING"
    if normalized in {"NO", "FALSE", "READY"}:
        return "READY"
    return "ALL"


def _runtime_export_user_service_request_code(value: object, default: str) -> str:
    normalized = "_".join(
        part
        for part in (
            str(value or default)
            .strip()
            .upper()
            .replace("-", "_")
            .replace("/", "_")
            .split()
        )
        if part
    )
    return normalized or default


def _runtime_export_service_trace_terminal_state(value: object) -> str:
    normalized = _runtime_export_service_trace_code(value, "ALL")
    if normalized in {"ALL", "RUNNING", "COMPLETE", "INCOMPLETE"}:
        return normalized
    return "ALL"


def _runtime_export_service_trace_stage_kind(value: object) -> str:
    normalized = _runtime_export_service_trace_code(value, "ALL")
    if normalized in {
        "ALL",
        "INPUT_NETWORK",
        "COMPUTE_QUEUE",
        "COMPUTE_EXECUTION",
        "OUTPUT_NETWORK",
    }:
        return normalized
    return "ALL"


def _runtime_export_service_trace_terminal_reason(value: object) -> str:
    normalized = _runtime_export_service_trace_code(value, "ALL")
    if normalized in {
        "ALL",
        "TOTAL_LATENCY_OBSERVED",
        "OUTPUT_NETWORK_PENDING",
        "COMPONENTS_OBSERVED_BUT_TOTAL_MISSING",
        "NO_COMPONENT_OBSERVATIONS",
    }:
        return normalized
    return "ALL"


def _runtime_export_service_trace_code(value: object, default: str) -> str:
    normalized = "_".join(
        part
        for part in (
            str(value or default)
            .replace("_", " ")
            .replace("-", " ")
            .strip()
            .upper()
            .split()
        )
        if part
    )
    return normalized or default


def _search_terms(query: str) -> tuple[str, ...]:
    normalized = _normalized_search_query(query)
    if not normalized:
        return ()
    return tuple(part for part in normalized.split(" ") if part)


def _normalized_search_query(query: str) -> str:
    return " ".join(str(query or "").strip().lower().split())


def _normalized_filter_value(value: str, default: str) -> str:
    normalized = str(value or default).strip().upper()
    return normalized or default


def _page_cursor(cursor: int) -> int:
    return max(0, _integer(cursor))


def _page_limit(limit: int) -> int:
    normalized_limit = _integer(limit)
    if normalized_limit <= 0:
        return 100
    return min(5000, normalized_limit)


def _records(value: object) -> tuple[Mapping[str, Any], ...]:
    if not isinstance(value, (list, tuple)):
        return ()
    return tuple(item for item in value if isinstance(item, Mapping))


def _file_records(value: object) -> tuple[Mapping[str, Any], ...]:
    if not isinstance(value, (list, tuple)):
        return ()
    return tuple(item for item in value if isinstance(item, Mapping))


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _value(mapping: Mapping[str, Any], key: str, default: object) -> object:
    return mapping.get(key, default)


def _integer(value: object) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return 0


def _number(value: object) -> float:
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value))
    except (TypeError, ValueError):
        return 0.0


def _bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    text = str(value).strip().lower()
    if text in {"true", "1", "yes", "y"}:
        return True
    return False


def _string_tuple(value: object) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        return ()
    return tuple(str(item) for item in value if str(item))
