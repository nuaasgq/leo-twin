from __future__ import annotations

import json

from leo_twin.services.result_package_contract import (
    RESULT_PACKAGE_CONTRACT_V1_ID,
    RUNTIME_EXPORT_DIAGNOSTICS_BUNDLE_V1_ID,
    RUNTIME_EXPORT_ROUTE_DETAIL_ITEM_V1_ID,
    RUNTIME_EXPORT_ROUTE_DETAIL_INDEX_V1_ID,
    RUNTIME_EXPORT_ROUTE_DETAIL_PAGE_V1_ID,
    RUNTIME_EXPORT_REVIEW_SUMMARY_V1_ID,
    RUNTIME_REPRODUCIBILITY_MANIFEST_V1_ID,
    build_runtime_export_diagnostics_bundle_v1,
    build_runtime_export_route_detail_item_v1,
    build_runtime_export_route_detail_index_v1,
    build_runtime_export_route_detail_page_v1,
    build_runtime_export_review_summary_v1,
    result_package_contract_v1_to_dict,
    summarize_result_package_record_v1,
)


def test_result_package_contract_v1_is_deterministic_json_ready() -> None:
    first = result_package_contract_v1_to_dict()
    second = result_package_contract_v1_to_dict()

    assert first == second
    assert first["contract_id"] == RESULT_PACKAGE_CONTRACT_V1_ID
    assert first["required_manifest_id"] == RUNTIME_REPRODUCIBILITY_MANIFEST_V1_ID
    assert json.loads(json.dumps(first, sort_keys=True))["contract_id"] == (
        RESULT_PACKAGE_CONTRACT_V1_ID
    )
    assert [spec["filename"] for spec in first["required_files"]] == [
        "config_snapshot.json",
        "events.jsonl",
        "metrics.csv",
        "summary.json",
        "manifest.json",
    ]
    assert [spec["filename"] for spec in first["recommended_files"]] == [
        "service_lifecycle_trace_v2.json",
        "route_detail_index_v1.json",
        "review_summary_v1.json",
        "diagnostics_bundle_v1.json",
    ]
    assert "GET /runtime/export" in first["source_endpoints"]
    assert (
        "GET /runtime/export/packages/{package_id}/review-summary"
        in first["source_endpoints"]
    )
    assert "LIVE_EVENT_REPLAY_RESTORE" in first["excluded_semantics"]


def test_result_package_summary_accepts_complete_package_record() -> None:
    package = {
        "type": "RUNTIME_EXPORT",
        "ok": True,
        "package_id": "pkg-1",
        "package_dir": "exports/pkg-1",
        "files": (
            _file("config_snapshot", "config_snapshot.json", "sha256:a"),
            _file("events", "events.jsonl", "sha256:b"),
            _file("manifest", "manifest.json", "sha256:c"),
            _file("metrics", "metrics.csv", "sha256:d"),
            _file("summary", "summary.json", "sha256:e"),
        ),
        "manifest": {
            "manifest_id": RUNTIME_REPRODUCIBILITY_MANIFEST_V1_ID,
            "manifest_hash": "sha256:manifest",
        },
        "export_catalog_record": {"catalog_key": "PACKAGE:pkg-1"},
        "export_history_record": {"package_id": "pkg-1"},
    }

    summary = summarize_result_package_record_v1(package)

    assert summary["contract_id"] == RESULT_PACKAGE_CONTRACT_V1_ID
    assert summary["package_complete"] is True
    assert summary["missing_required_files"] == ()
    assert summary["file_hash_count"] == 5
    assert summary["missing_recommended_files"] == (
        "service_lifecycle_trace_v2.json",
        "route_detail_index_v1.json",
        "review_summary_v1.json",
        "diagnostics_bundle_v1.json",
    )
    assert summary["catalog_record_present"] is True
    assert summary["history_record_present"] is True


def test_result_package_summary_reports_missing_files_and_manifest() -> None:
    package = {
        "type": "RUNTIME_EXPORT",
        "ok": True,
        "package_id": "pkg-2",
        "files": (_file("events", "events.jsonl", "sha256:events"),),
        "manifest": {"manifest_id": "wrong"},
    }

    summary = summarize_result_package_record_v1(package)

    assert summary["package_complete"] is False
    assert summary["manifest_id"] == "wrong"
    assert summary["present_required_files"] == ("events.jsonl",)
    assert summary["missing_required_files"] == (
        "config_snapshot.json",
        "metrics.csv",
        "summary.json",
        "manifest.json",
    )


def test_runtime_export_review_summary_v1_is_deterministic_and_review_ready() -> None:
    config_snapshot = {
        "type": "RUNTIME_CONFIG_SNAPSHOT",
        "status": {
            "lifecycle_state": "RUNNING",
            "current_sim_time": 12.5,
            "processed_event_count": 42,
            "queued_event_count": 3,
            "route_explanation_summary_v1": _route_summary(),
            "route_provenance_trust_summary_v1": _route_trust(),
        },
        "config": {"seed": 7, "duration_seconds": 120},
        "generated_config": {
            "seed": 7,
            "satellite_count": 72,
            "ground_user_count": 20,
            "compute_node_count": 12,
            "duration_seconds": 120,
        },
    }
    manifest = {
        "manifest_id": RUNTIME_REPRODUCIBILITY_MANIFEST_V1_ID,
        "manifest_hash": "sha256:manifest",
        "config_hash": "sha256:config",
        "generated_config_hash": "sha256:generated",
    }
    filenames = (
        "config_snapshot.json",
        "events.jsonl",
        "manifest.json",
        "metrics.csv",
        "diagnostics_bundle_v1.json",
        "review_summary_v1.json",
        "route_detail_index_v1.json",
        "service_lifecycle_trace_v2.json",
        "summary.json",
    )

    first = build_runtime_export_review_summary_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        config_snapshot=config_snapshot,
        manifest=manifest,
        artifact_filenames=filenames,
    )
    second = build_runtime_export_review_summary_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        config_snapshot=config_snapshot,
        manifest=manifest,
        artifact_filenames=tuple(reversed(filenames)),
    )

    assert first == second
    assert first["summary_id"] == RUNTIME_EXPORT_REVIEW_SUMMARY_V1_ID
    assert first["review_status"] == "REVIEW_READY"
    assert first["scenario"] == {
        "seed": 7,
        "satellite_count": 72,
        "user_count": 20,
        "compute_node_count": 12,
        "duration_seconds": 120,
    }
    assert first["artifacts"]["missing_required_filenames"] == ()
    assert first["artifacts"]["review_summary_exported"] is True
    assert first["route_trust"]["trust_id"] == "leo_twin.route_provenance_trust.v1"
    assert first["route_trust"]["evidence_present"] is True
    assert first["route_trust"]["route_model"] == "FLOW_LEVEL_ROUTE_PROXY"
    assert first["route_trust"]["packet_level_simulation"] is False
    assert first["route_trust"]["all_pairs_computation"] is False
    assert first["route_trust"]["assessed_route_count"] == 2
    assert first["route_trust"]["sample_route_ids"] == ("route-0", "route-1")
    assert "diagnostics_bundle_v1.json" in first["artifacts"]["artifact_filenames"]
    assert first["summary_hash"].startswith("sha256:")
    assert json.loads(json.dumps(first, sort_keys=True))["summary_id"] == (
        RUNTIME_EXPORT_REVIEW_SUMMARY_V1_ID
    )


def test_runtime_export_diagnostics_bundle_v1_is_deterministic_and_review_ready() -> None:
    config_snapshot = {
        "type": "RUNTIME_CONFIG_SNAPSHOT",
        "status": {
            "lifecycle_state": "STOPPED",
            "current_sim_time": 120,
            "processed_event_count": 4200,
            "queued_event_count": 0,
            "route_explanation_summary_v1": _route_summary(),
            "route_provenance_trust_summary_v1": _route_trust(),
        },
        "config": {"seed": 7, "duration_seconds": 120},
        "generated_config": {
            "seed": 7,
            "satellite_count": 72,
            "ground_user_count": 20,
            "compute_node_count": 12,
            "duration_seconds": 120,
        },
    }
    manifest = {
        "manifest_id": RUNTIME_REPRODUCIBILITY_MANIFEST_V1_ID,
        "manifest_hash": "sha256:manifest",
        "config_hash": "sha256:config",
        "generated_config_hash": "sha256:generated",
    }
    filenames = (
        "config_snapshot.json",
        "diagnostics_bundle_v1.json",
        "events.jsonl",
        "manifest.json",
        "metrics.csv",
        "review_summary_v1.json",
        "route_detail_index_v1.json",
        "service_lifecycle_trace_v2.json",
        "summary.json",
    )
    review_summary = build_runtime_export_review_summary_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        config_snapshot=config_snapshot,
        manifest=manifest,
        artifact_filenames=filenames,
    )

    first = build_runtime_export_diagnostics_bundle_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        config_snapshot=config_snapshot,
        manifest=manifest,
        review_summary=review_summary,
        artifact_filenames=tuple(reversed(filenames)),
    )
    second = build_runtime_export_diagnostics_bundle_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        config_snapshot=config_snapshot,
        manifest=manifest,
        review_summary=review_summary,
        artifact_filenames=filenames,
    )

    assert first == second
    assert first["bundle_id"] == RUNTIME_EXPORT_DIAGNOSTICS_BUNDLE_V1_ID
    assert first["package"]["package_complete"] is True
    assert first["reproducibility"]["manifest_ok"] is True
    assert first["route_trust"]["trust_status"] == "COMPLETE_FLOW_LEVEL_ROUTE_PROXY"
    assert first["route_trust"]["available_route_count"] == 2
    assert first["route_trust"]["bottleneck_components"] == ("capacity",)
    assert first["artifact_health"]["missing_required_filenames"] == ()
    assert first["artifact_health"]["missing_recommended_filenames"] == ()
    assert first["findings"] == (
        {
            "severity": "INFO",
            "code": "RESULT_PACKAGE_REVIEW_READY",
            "message": "Required artifacts, manifest id, and review summary are ready.",
        },
    )
    assert first["diagnostics_hash"].startswith("sha256:")
    assert json.loads(json.dumps(first, sort_keys=True))["bundle_id"] == (
        RUNTIME_EXPORT_DIAGNOSTICS_BUNDLE_V1_ID
    )


def test_runtime_export_route_detail_index_v1_is_deterministic_and_review_ready() -> None:
    config_snapshot = {
        "type": "RUNTIME_CONFIG_SNAPSHOT",
        "status": {
            "route_explanation_summary_v1": _route_summary(),
            "route_provenance_trust_summary_v1": _route_trust(),
        },
    }

    first = build_runtime_export_route_detail_index_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        config_snapshot=config_snapshot,
    )
    second = build_runtime_export_route_detail_index_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        config_snapshot=config_snapshot,
    )

    assert first == second
    assert first["index_id"] == RUNTIME_EXPORT_ROUTE_DETAIL_INDEX_V1_ID
    assert first["route_model"] == "FLOW_LEVEL_ROUTE_PROXY"
    assert first["packet_level_simulation"] is False
    assert first["all_pairs_computation"] is False
    assert first["route_summary"]["route_count"] == 2
    assert first["route_summary"]["indexed_route_count"] == 2
    assert first["route_summary"]["hidden_route_count"] == 0
    assert first["route_ids"] == ("route-0", "route-1")
    assert first["sample_route_ids"] == ("route-0", "route-1")
    assert first["indexed_sample_route_ids"] == ("route-0", "route-1")
    assert first["missing_sample_route_ids"] == ()
    assert first["routes"][0]["route_id"] == "route-0"
    assert first["routes"][0]["path_label"] == "user-0 -> sat-0"
    assert first["route_detail_index_hash"].startswith("sha256:")
    assert json.loads(json.dumps(first, sort_keys=True))["index_id"] == (
        RUNTIME_EXPORT_ROUTE_DETAIL_INDEX_V1_ID
    )


def test_runtime_export_route_detail_page_v1_filters_package_index() -> None:
    route_index = build_runtime_export_route_detail_index_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        config_snapshot={
            "type": "RUNTIME_CONFIG_SNAPSHOT",
            "status": {
                "route_explanation_summary_v1": _route_summary(),
                "route_provenance_trust_summary_v1": _route_trust(),
            },
        },
    )

    first = build_runtime_export_route_detail_page_v1(
        route_index,
        cursor=0,
        limit=1,
        query="sat-1 data",
        availability="AVAILABLE",
        business_type="DATA_TRANSFER",
        bottleneck_component="CAPACITY",
    )
    second = build_runtime_export_route_detail_page_v1(
        route_index,
        cursor=0,
        limit=1,
        query="sat-1 data",
        availability="AVAILABLE",
        business_type="DATA_TRANSFER",
        bottleneck_component="CAPACITY",
    )

    assert first == second
    assert first["page_id"] == RUNTIME_EXPORT_ROUTE_DETAIL_PAGE_V1_ID
    assert first["source"] == "BACKEND_RUNTIME_EXPORT_PACKAGE"
    assert first["package_id"] == "pkg-1"
    assert first["route_detail_index_hash"] == route_index["route_detail_index_hash"]
    assert first["cursor"] == 0
    assert first["limit"] == 1
    assert first["route_count"] == 1
    assert first["item_count"] == 1
    assert first["unfiltered_route_count"] == 2
    assert first["has_more"] is False
    assert first["filter_applied"] is True
    assert first["filters"] == {
        "query": "sat-1 data",
        "availability": "AVAILABLE",
        "business_type": "DATA_TRANSFER",
        "bottleneck_component": "CAPACITY",
    }
    assert first["items"][0]["route_id"] == "route-1"
    assert first["page_hash"].startswith("sha256:")


def test_runtime_export_route_detail_item_v1_reads_exact_package_route() -> None:
    route_index = build_runtime_export_route_detail_index_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        config_snapshot={
            "type": "RUNTIME_CONFIG_SNAPSHOT",
            "status": {
                "route_explanation_summary_v1": _route_summary(),
                "route_provenance_trust_summary_v1": _route_trust(),
            },
        },
    )

    detail = build_runtime_export_route_detail_item_v1(route_index, "route-1")

    assert detail is not None
    assert detail["item_id"] == RUNTIME_EXPORT_ROUTE_DETAIL_ITEM_V1_ID
    assert detail["source"] == "BACKEND_RUNTIME_EXPORT_PACKAGE"
    assert detail["package_id"] == "pkg-1"
    assert detail["route_detail_index_hash"] == route_index["route_detail_index_hash"]
    assert detail["route_id"] == "route-1"
    assert detail["route"]["path_label"] == "user-1 -> sat-1"
    assert detail["item_hash"].startswith("sha256:")
    assert build_runtime_export_route_detail_item_v1(route_index, "missing") is None


def test_runtime_export_diagnostics_bundle_v1_warns_when_route_trust_missing() -> None:
    config_snapshot = {
        "type": "RUNTIME_CONFIG_SNAPSHOT",
        "status": {
            "lifecycle_state": "STOPPED",
            "current_sim_time": 120,
            "processed_event_count": 4200,
            "queued_event_count": 0,
        },
        "config": {"seed": 7, "duration_seconds": 120},
        "generated_config": {
            "seed": 7,
            "satellite_count": 72,
            "ground_user_count": 20,
            "compute_node_count": 12,
            "duration_seconds": 120,
        },
    }
    manifest = {
        "manifest_id": RUNTIME_REPRODUCIBILITY_MANIFEST_V1_ID,
        "manifest_hash": "sha256:manifest",
        "config_hash": "sha256:config",
        "generated_config_hash": "sha256:generated",
    }
    filenames = (
        "config_snapshot.json",
        "diagnostics_bundle_v1.json",
        "events.jsonl",
        "manifest.json",
        "metrics.csv",
        "review_summary_v1.json",
        "route_detail_index_v1.json",
        "service_lifecycle_trace_v2.json",
        "summary.json",
    )
    review_summary = build_runtime_export_review_summary_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        config_snapshot=config_snapshot,
        manifest=manifest,
        artifact_filenames=filenames,
    )

    diagnostics = build_runtime_export_diagnostics_bundle_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        config_snapshot=config_snapshot,
        manifest=manifest,
        review_summary=review_summary,
        artifact_filenames=filenames,
    )

    assert review_summary["route_trust"]["evidence_present"] is False
    assert diagnostics["route_trust"]["trust_status"] == "MISSING_ROUTE_TRUST_EVIDENCE"
    assert diagnostics["route_trust"]["evidence_present"] is False
    assert diagnostics["package"]["package_complete"] is True
    assert {
        finding["code"] for finding in diagnostics["findings"]
    } == {"ROUTE_TRUST_EVIDENCE_MISSING"}
    assert diagnostics["finding_count"] == 1


def _file(name: str, filename: str, sha256: str) -> dict[str, object]:
    return {
        "name": name,
        "filename": filename,
        "path": f"exports/pkg-1/{filename}",
        "bytes": 10,
        "sha256": sha256,
    }


def _route_trust() -> dict[str, object]:
    return {
        "version": "v1",
        "trust_id": "leo_twin.route_provenance_trust.v1",
        "source": "route_explanation_summary_v1",
        "route_model": "FLOW_LEVEL_ROUTE_PROXY",
        "packet_level_simulation": False,
        "all_pairs_computation": False,
        "trust_status": "COMPLETE_FLOW_LEVEL_ROUTE_PROXY",
        "route_count": 2,
        "window_item_count": 2,
        "assessed_route_count": 2,
        "hidden_route_count": 0,
        "available_route_count": 2,
        "blocked_route_count": 0,
        "over_demand_route_count": 1,
        "explained_route_count": 2,
        "missing_explanation_count": 0,
        "path_context_route_count": 2,
        "next_hop_route_count": 2,
        "loss_proxy_route_count": 1,
        "bottleneck_components": ("capacity",),
        "sample_route_ids": ("route-0", "route-1"),
        "caveats": ("Flow-level route proxy; no packet replay.",),
    }


def _route_summary() -> dict[str, object]:
    return {
        "version": "v1",
        "source": "BACKEND_RUNTIME_SNAPSHOT",
        "summary_scope": "ROUTE_EXPLANATION_WINDOW",
        "cursor": 0,
        "limit": 500,
        "next_cursor": 2,
        "has_more": False,
        "route_count": 2,
        "item_count": 2,
        "available_route_count": 2,
        "blocked_route_count": 0,
        "over_demand_route_count": 1,
        "compute_service_route_count": 1,
        "network_service_route_count": 1,
        "items": (
            _route_item("route-0", "flow-0", "user-0", "sat-0"),
            _route_item("route-1", "flow-1", "user-1", "sat-1"),
        ),
    }


def _route_item(
    route_id: str,
    flow_id: str,
    user_id: str,
    satellite_id: str,
) -> dict[str, object]:
    return {
        "route_id": route_id,
        "flow_id": flow_id,
        "user_id": user_id,
        "source_id": user_id,
        "destination_id": satellite_id,
        "selected_satellite_id": satellite_id,
        "primary_next_hop_id": satellite_id,
        "next_hop_ids": (satellite_id,),
        "hop_count": 1,
        "path_label": f"{user_id} -> {satellite_id}",
        "available": True,
        "capacity_mbps": 80.0,
        "demand_mbps": 60.0,
        "latency_s": 0.1,
        "loss_proxy_rate": 0.01,
        "route_pressure_proxy": 0.75,
        "business_type": "COMPUTE_SERVICE" if route_id == "route-0" else "DATA_TRANSFER",
        "business_label": "compute service" if route_id == "route-0" else "data transfer",
        "bottleneck_component": "capacity",
        "bottleneck_reason": "ROUTE_DEMAND_NEAR_CAPACITY",
        "bottleneck_reason_label": "Route demand is near capacity",
        "explanation_label": "flow-level route explanation",
    }
