"""Product contract and validation helpers for runtime result packages."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from leo_twin.services.runtime_reproducibility import stable_hash_payload


RESULT_PACKAGE_CONTRACT_V1_ID = "leo_twin.result_package_contract.v1"
RUNTIME_REPRODUCIBILITY_MANIFEST_V1_ID = (
    "leo_twin.runtime_reproducibility_manifest.v1"
)
RUNTIME_EXPORT_REVIEW_SUMMARY_V1_ID = "leo_twin.runtime_export_review_summary.v1"
RUNTIME_EXPORT_DIAGNOSTICS_BUNDLE_V1_ID = (
    "leo_twin.runtime_export_diagnostics_bundle.v1"
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
RUNTIME_EXPORT_REPRODUCIBILITY_BOUNDARY_V1_ID = (
    "leo_twin.runtime_export_reproducibility_boundary.v1"
)
RUNTIME_EXPORT_ROUTE_DETAIL_ITEM_V1_ID = (
    "leo_twin.runtime_export_route_detail_item.v1"
)
RUNTIME_EXPORT_ROUTE_COMPARISON_REVIEW_REPORT_V1_ID = (
    "leo_twin.runtime_export_route_comparison_review_report.v1"
)


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
            "GET /runtime/export/packages/{package_id}/service-traces",
            "GET /runtime/export/packages/{package_id}/routes",
            "GET /runtime/export/packages/{package_id}/routes/{route_id}",
            "POST /runtime/export/packages/{package_id}/route-comparison-review-report",
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
        },
        "review_notes": (
            "Use manifest.json and config_snapshot.json to verify deterministic inputs.",
            "Use events.jsonl, metrics.csv, and summary.json as replay evidence.",
            "Use service_lifecycle_trace_v2.json for communication-compute trace review.",
            "Use route_trust to inspect flow-level route explanation evidence.",
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
    records: tuple[Mapping[str, Any], ...] = (),
) -> dict[str, object]:
    """Build a deterministic operator report for selected route comparisons."""

    if not isinstance(route_comparison_review, Mapping):
        raise TypeError("route_comparison_review must be a mapping")
    normalized_review = _mapping(route_comparison_review)
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
