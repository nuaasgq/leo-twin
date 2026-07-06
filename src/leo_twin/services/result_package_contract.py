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
RUNTIME_EXPORT_ROUTE_DETAIL_ITEM_V1_ID = (
    "leo_twin.runtime_export_route_detail_item.v1"
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
            "GET /runtime/export/packages/{package_id}/routes",
            "GET /runtime/export/packages/{package_id}/routes/{route_id}",
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
        "reproducibility": {
            "manifest_id": str(manifest.get("manifest_id", "")),
            "manifest_hash": str(manifest.get("manifest_hash", "")),
            "config_hash": str(manifest.get("config_hash", "")),
            "generated_config_hash": str(manifest.get("generated_config_hash", "")),
            "event_kernel_policy": "NO_EVENT_KERNEL_BEHAVIOR_CHANGE",
        },
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
        "reproducibility": {
            "manifest_id": manifest_id,
            "manifest_ok": manifest_ok,
            "manifest_hash": str(manifest.get("manifest_hash", "")),
            "config_hash": str(manifest.get("config_hash", "")),
            "generated_config_hash": str(manifest.get("generated_config_hash", "")),
            "review_summary_hash": str(review_summary.get("summary_hash", "")),
        },
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
                "route_id": normalized_route_id,
                "route": route,
            }
            detail["item_hash"] = stable_hash_payload(detail)
            return detail
    return None


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
