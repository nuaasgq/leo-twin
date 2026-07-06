from __future__ import annotations

import json

from leo_twin.services.result_package_contract import (
    RESULT_PACKAGE_CONTRACT_V1_ID,
    RUNTIME_EXPORT_DIAGNOSTICS_BUNDLE_V1_ID,
    RUNTIME_EXPORT_NETWORK_KPI_BENCHMARK_VALIDATION_V1_ID,
    RUNTIME_EXPORT_PACKAGE_AUDIT_INDEX_V1_ID,
    RUNTIME_EXPORT_PACKAGE_HANDOFF_REPORT_V1_ID,
    RUNTIME_EXPORT_PACKAGE_REVIEW_COMPLETION_V1_ID,
    RUNTIME_EXPORT_REPRODUCIBILITY_BOUNDARY_V1_ID,
    RUNTIME_EXPORT_ROUTE_COMPARISON_REVIEW_REPORT_V1_ID,
    RUNTIME_EXPORT_SCENARIO_REVIEW_BUNDLE_V1_ID,
    RUNTIME_EXPORT_SCENARIO_REVIEW_CHECKLIST_V1_ID,
    RUNTIME_EXPORT_SERVICE_TRACE_COMPARISON_REVIEW_REPORT_PAGE_V1_ID,
    RUNTIME_EXPORT_SERVICE_TRACE_COMPARISON_REVIEW_REPORT_V1_ID,
    RUNTIME_EXPORT_ROUTE_DETAIL_ITEM_V1_ID,
    RUNTIME_EXPORT_ROUTE_DETAIL_INDEX_V1_ID,
    RUNTIME_EXPORT_ROUTE_DETAIL_PAGE_V1_ID,
    RUNTIME_EXPORT_SERVICE_TRACE_ITEM_V1_ID,
    RUNTIME_EXPORT_SERVICE_TRACE_PAGE_V1_ID,
    RUNTIME_EXPORT_REVIEW_SUMMARY_V1_ID,
    RUNTIME_EXPORT_USER_SERVICE_REQUEST_PAGE_V1_ID,
    RUNTIME_EXPORT_USER_SERVICE_REQUEST_SUMMARY_V2_ID,
    RUNTIME_REPRODUCIBILITY_MANIFEST_V1_ID,
    build_runtime_export_diagnostics_bundle_v1,
    build_runtime_export_network_kpi_benchmark_validation_v1,
    build_runtime_export_package_audit_index_v1,
    build_runtime_export_package_handoff_report_v1,
    build_runtime_export_package_review_completion_v1,
    build_runtime_export_reproducibility_boundary_v1,
    build_runtime_export_route_comparison_review_report_v1,
    build_runtime_export_route_detail_item_v1,
    build_runtime_export_route_detail_index_v1,
    build_runtime_export_route_detail_page_v1,
    build_runtime_export_review_summary_v1,
    build_runtime_export_scenario_review_bundle_v1,
    build_runtime_export_scenario_review_checklist_v1,
    build_runtime_export_service_trace_comparison_review_report_page_v1,
    build_runtime_export_service_trace_comparison_review_report_v1,
    build_runtime_export_service_trace_item_v1,
    build_runtime_export_service_trace_page_v1,
    build_runtime_export_user_service_request_page_v1,
    build_runtime_export_user_service_request_summary_v2,
    result_package_contract_v1_to_dict,
    summarize_result_package_record_v1,
)


def test_result_package_contract_v1_is_deterministic_json_ready() -> None:
    first = result_package_contract_v1_to_dict()
    second = result_package_contract_v1_to_dict()

    assert first == second
    assert first["contract_id"] == RESULT_PACKAGE_CONTRACT_V1_ID
    assert first["required_manifest_id"] == RUNTIME_REPRODUCIBILITY_MANIFEST_V1_ID
    assert first["reproducibility_boundary_id"] == (
        RUNTIME_EXPORT_REPRODUCIBILITY_BOUNDARY_V1_ID
    )
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
        "user_service_request_summary_v2.json",
        "route_detail_index_v1.json",
        "review_summary_v1.json",
        "diagnostics_bundle_v1.json",
        "network_kpi_benchmark_validation_v1.json",
        "scenario_review_bundle_v1.json",
        "export_package_audit_index_v1.json",
        "package_handoff_report_v1.md",
    ]
    assert "GET /runtime/export" in first["source_endpoints"]
    assert (
        "GET /runtime/export/packages/{package_id}/review-summary"
        in first["source_endpoints"]
    )
    assert (
        "GET /runtime/export/packages/{package_id}/review-completion"
        in first["source_endpoints"]
    )
    assert (
        "GET /runtime/export/packages/{package_id}/user-service-requests"
        in first["source_endpoints"]
    )
    assert (
        "GET /runtime/export/packages/{package_id}/handoff-report"
        in first["source_endpoints"]
    )
    assert (
        "GET /runtime/export/packages/{package_id}/service-traces"
        in first["source_endpoints"]
    )
    assert (
        "GET /runtime/export/packages/{package_id}/service-traces/{trace_id}"
        in first["source_endpoints"]
    )
    assert (
        "POST /runtime/export/packages/{package_id}/service-trace-comparison-review-report"
        in first["source_endpoints"]
    )
    assert (
        "POST /runtime/export/packages/{package_id}/scenario-review-checklist"
        in first["source_endpoints"]
    )
    assert "LIVE_EVENT_REPLAY_RESTORE" in first["excluded_semantics"]


def test_runtime_export_reproducibility_boundary_v1_is_deterministic() -> None:
    route_policy = dict(_route_detail_export_policy())
    route_policy["route_count"] = 3
    route_policy["hidden_route_count"] = 1
    service_policy = dict(_service_trace_export_policy())
    service_policy["service_count"] = 5
    service_policy["hidden_trace_count"] = 2
    runtime_status = {
        "runtime_export_route_detail_policy_v1": route_policy,
        "runtime_export_service_trace_policy_v1": service_policy,
    }
    manifest = {
        "manifest_id": RUNTIME_REPRODUCIBILITY_MANIFEST_V1_ID,
        "control_config_hash": "sha256:control",
        "generated_config_hash": "sha256:generated",
        "runtime_state_hash": "sha256:state",
        "metrics_summary_hash": "sha256:metrics",
        "deterministic_replay": False,
    }

    first = build_runtime_export_reproducibility_boundary_v1(
        runtime_status=runtime_status,
        manifest=manifest,
    )
    second = build_runtime_export_reproducibility_boundary_v1(
        runtime_status=dict(reversed(tuple(runtime_status.items()))),
        manifest=dict(reversed(tuple(manifest.items()))),
    )

    assert first == second
    assert first["boundary_id"] == RUNTIME_EXPORT_REPRODUCIBILITY_BOUNDARY_V1_ID
    assert first["restore_scope"] == "CONFIG_ONLY"
    assert first["compare_scope"] == "CONFIG_AND_GENERATED_CONFIG"
    assert first["read_scope"] == "PERSISTED_ARTIFACTS_ONLY"
    assert first["event_replay_restore"] is False
    assert first["recompute_on_read"] is False
    assert first["package_mutation_on_read"] is False
    assert first["packet_capture"] is False
    assert first["external_simulators"] is False
    assert first["route_detail_export"]["hidden_route_count"] == 1
    assert first["service_trace_export"]["hidden_trace_count"] == 2
    assert "CONFIG_ONLY_RESTORE" in first["boundary_conditions"]
    assert "NO_RECOMPUTE_ON_COMPARE_OR_READ" in first["boundary_conditions"]
    assert "NO_PACKAGE_MUTATION_ON_READ" in first["boundary_conditions"]
    assert first["boundary_hash"].startswith("sha256:")
    assert json.loads(json.dumps(first, sort_keys=True))["boundary_id"] == (
        RUNTIME_EXPORT_REPRODUCIBILITY_BOUNDARY_V1_ID
    )


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
        "user_service_request_summary_v2.json",
        "route_detail_index_v1.json",
        "review_summary_v1.json",
        "diagnostics_bundle_v1.json",
        "network_kpi_benchmark_validation_v1.json",
        "scenario_review_bundle_v1.json",
        "export_package_audit_index_v1.json",
        "package_handoff_report_v1.md",
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
            "network_kpi_benchmark_validation_v1": (
                _network_kpi_benchmark_validation()
            ),
            "user_service_request_summary_v2": _user_service_request_summary(),
            "runtime_export_user_service_request_policy_v1": (
                _user_service_request_export_policy()
            ),
            "runtime_export_route_detail_policy_v1": _route_detail_export_policy(),
            "runtime_export_service_trace_policy_v1": _service_trace_export_policy(),
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
        "network_kpi_benchmark_validation_v1.json",
        "review_summary_v1.json",
        "route_detail_index_v1.json",
        "scenario_review_bundle_v1.json",
        "service_lifecycle_trace_v2.json",
        "summary.json",
        "user_service_request_summary_v2.json",
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
    assert first["network_kpi_benchmark_validation"]["evidence_present"] is True
    assert first["network_kpi_benchmark_validation"]["validation_status"] == "PASS"
    assert first["network_kpi_benchmark_validation"]["failed_check_count"] == 0
    assert first["user_service_requests"]["evidence_present"] is True
    assert first["user_service_requests"]["request_count"] == 2
    assert first["user_service_requests"]["exported_request_count"] == 2
    assert first["user_service_requests"]["hidden_request_count"] == 0
    assert first["artifacts"][
        "network_kpi_benchmark_validation_exported"
    ] is True
    assert first["artifacts"]["user_service_request_summary_exported"] is True
    assert first["route_comparison_review"]["review_scope"] == (
        "PACKAGE_ROUTE_DETAIL_TO_LIVE_RUNTIME_ROUTE_DETAIL"
    )
    assert first["route_comparison_review"]["review_report_id"] == (
        RUNTIME_EXPORT_ROUTE_COMPARISON_REVIEW_REPORT_V1_ID
    )
    assert first["route_comparison_review"]["compare_action"] == "compare with live"
    assert "ROUTE_ID_MISMATCH" in first["route_comparison_review"]["status_reasons"]
    assert first["route_comparison_review"]["review_report_record_schema"][
        "status_values"
    ] == ("MATCH", "DIFFERENT", "UNAVAILABLE", "ERROR")
    assert first["reproducibility_boundary"]["boundary_id"] == (
        RUNTIME_EXPORT_REPRODUCIBILITY_BOUNDARY_V1_ID
    )
    assert first["reproducibility"]["boundary_hash"] == first[
        "reproducibility_boundary"
    ]["boundary_hash"]
    assert "CONFIG_ONLY_RESTORE" in first["reproducibility_boundary"][
        "boundary_conditions"
    ]
    assert "diagnostics_bundle_v1.json" in first["artifacts"]["artifact_filenames"]
    assert "scenario_review_bundle_v1.json" in first["artifacts"][
        "artifact_filenames"
    ]
    assert first["summary_hash"].startswith("sha256:")
    assert json.loads(json.dumps(first, sort_keys=True))["summary_id"] == (
        RUNTIME_EXPORT_REVIEW_SUMMARY_V1_ID
    )


def test_runtime_export_network_kpi_benchmark_validation_v1_is_deterministic() -> None:
    config_snapshot = {
        "type": "RUNTIME_CONFIG_SNAPSHOT",
        "status": {
            "network_kpi_benchmark_validation_v1": (
                _network_kpi_benchmark_validation()
            ),
        },
        "config": {"seed": 7},
        "generated_config": {"seed": 7, "satellite_count": 72},
    }

    first = build_runtime_export_network_kpi_benchmark_validation_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        config_snapshot=config_snapshot,
    )
    second = build_runtime_export_network_kpi_benchmark_validation_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        config_snapshot=dict(reversed(tuple(config_snapshot.items()))),
    )

    assert first == second
    assert first["artifact_id"] == (
        RUNTIME_EXPORT_NETWORK_KPI_BENCHMARK_VALIDATION_V1_ID
    )
    assert first["runtime_status_field"] == "network_kpi_benchmark_validation_v1"
    assert first["validation"]["validation_status"] == "PASS"
    assert first["evidence"]["evidence_present"] is True
    assert first["evidence"]["validation_status"] == "PASS"
    assert first["evidence"]["acceptable_for_demo_review"] is True
    assert first["artifact_hash"].startswith("sha256:")
    assert "NO_METRIC_RECOMPUTE" in first["boundary_conditions"]


def test_runtime_export_user_service_request_summary_v2_is_deterministic() -> None:
    config_snapshot = {
        "type": "RUNTIME_CONFIG_SNAPSHOT",
        "status": {
            "user_service_request_summary_v2": _user_service_request_summary(),
            "runtime_export_user_service_request_policy_v1": (
                _user_service_request_export_policy()
            ),
        },
        "config": {"seed": 7},
        "generated_config": {"seed": 7, "satellite_count": 72},
    }

    first = build_runtime_export_user_service_request_summary_v2(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        config_snapshot=config_snapshot,
    )
    second = build_runtime_export_user_service_request_summary_v2(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        config_snapshot=dict(reversed(tuple(config_snapshot.items()))),
    )

    assert first == second
    assert first["artifact_id"] == RUNTIME_EXPORT_USER_SERVICE_REQUEST_SUMMARY_V2_ID
    assert first["runtime_status_field"] == "user_service_request_summary_v2"
    assert first["artifact_policy"] == "STANDALONE_RUNTIME_EXPORT_ARTIFACT"
    assert first["artifact_window_only"] is True
    assert first["summary"] == config_snapshot["status"][
        "user_service_request_summary_v2"
    ]
    assert first["user_service_request_export_policy"] == config_snapshot["status"][
        "runtime_export_user_service_request_policy_v1"
    ]
    assert first["evidence"]["evidence_present"] is True
    assert first["evidence"]["request_count"] == 2
    assert first["evidence"]["exported_request_count"] == 2
    assert first["evidence"]["packet_level_simulation"] is False
    assert first["artifact_hash"].startswith("sha256:")
    assert "NO_SERVICE_RECOMPUTE" in first["boundary_conditions"]


def test_runtime_export_user_service_request_page_v1_filters_artifact_window() -> None:
    artifact = {
        "type": "RUNTIME_EXPORT_USER_SERVICE_REQUEST_SUMMARY_V2",
        "version": "v2",
        "artifact_id": RUNTIME_EXPORT_USER_SERVICE_REQUEST_SUMMARY_V2_ID,
        "source": "BACKEND_RUNTIME_EXPORT",
        "artifact_policy": "STANDALONE_RUNTIME_EXPORT_ARTIFACT",
        "artifact_window_only": True,
        "package_id": "pkg-1",
        "summary": _user_service_request_summary(),
        "user_service_request_export_policy": _user_service_request_export_policy(),
        "evidence": {
            "summary_hash": "sha256:user-service-summary",
        },
        "boundary_conditions": ("NO_SERVICE_RECOMPUTE",),
        "artifact_hash": "sha256:user-service-artifact",
    }

    first = build_runtime_export_user_service_request_page_v1(
        artifact,
        package_id="pkg-1",
        cursor=0,
        limit=1,
        query="sat-1",
        service_class="DATA_TRANSFER",
        terminal_state="WAITING_NETWORK",
        network_waiting="WAITING",
    )
    second = build_runtime_export_user_service_request_page_v1(
        dict(reversed(tuple(artifact.items()))),
        package_id="pkg-1",
        cursor=0,
        limit=1,
        query="sat-1",
        service_class="DATA_TRANSFER",
        terminal_state="WAITING_NETWORK",
        network_waiting="WAITING",
    )

    assert first == second
    assert first["page_id"] == RUNTIME_EXPORT_USER_SERVICE_REQUEST_PAGE_V1_ID
    assert first["package_id"] == "pkg-1"
    assert first["artifact_window_only"] is True
    assert first["artifact_hash"] == "sha256:user-service-artifact"
    assert first["summary_hash"] == "sha256:user-service-summary"
    assert first["request_model"] == "FLOW_LEVEL_USER_SERVICE_REQUEST_PROXY"
    assert first["cursor"] == 0
    assert first["limit"] == 1
    assert first["next_cursor"] == 1
    assert first["has_more"] is False
    assert first["request_count"] == 1
    assert first["unfiltered_request_count"] == 2
    assert first["item_count"] == 1
    assert first["network_waiting_request_count"] == 1
    assert first["filter_applied"] is True
    assert first["filters"] == {
        "query": "sat-1",
        "service_class": "DATA_TRANSFER",
        "terminal_state": "WAITING_NETWORK",
        "network_waiting": "WAITING",
    }
    assert first["items"][0]["user_id"] == "user-1"
    assert first["items"][0]["request_id"] == "flow-1"
    assert first["items"][0]["trace_id"] == ""
    assert first["items"][0]["network_waiting"] is True
    assert first["page_hash"].startswith("sha256:")
    assert "NO_SERVICE_RECOMPUTE" in first["boundary_conditions"]

    trace_match = build_runtime_export_user_service_request_page_v1(
        artifact,
        package_id="pkg-1",
        cursor=0,
        limit=10,
        query="trace:service-0",
    )
    assert trace_match["request_count"] == 1
    assert trace_match["items"][0]["request_id"] == "service-0"
    assert trace_match["items"][0]["trace_id"] == "trace:service-0"


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
            "network_kpi_benchmark_validation_v1": (
                _network_kpi_benchmark_validation()
            ),
            "user_service_request_summary_v2": _user_service_request_summary(),
            "runtime_export_user_service_request_policy_v1": (
                _user_service_request_export_policy()
            ),
            "runtime_export_route_detail_policy_v1": _route_detail_export_policy(),
            "runtime_export_service_trace_policy_v1": _service_trace_export_policy(),
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
        "export_package_audit_index_v1.json",
        "package_handoff_report_v1.md",
        "manifest.json",
        "metrics.csv",
        "network_kpi_benchmark_validation_v1.json",
        "review_summary_v1.json",
        "route_detail_index_v1.json",
        "scenario_review_bundle_v1.json",
        "service_lifecycle_trace_v2.json",
        "summary.json",
        "user_service_request_summary_v2.json",
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
    assert first["reproducibility_boundary"]["boundary_id"] == (
        RUNTIME_EXPORT_REPRODUCIBILITY_BOUNDARY_V1_ID
    )
    assert first["reproducibility"]["boundary_hash"] == first[
        "reproducibility_boundary"
    ]["boundary_hash"]
    assert first["route_trust"]["trust_status"] == "COMPLETE_FLOW_LEVEL_ROUTE_PROXY"
    assert first["route_trust"]["available_route_count"] == 2
    assert first["route_trust"]["bottleneck_components"] == ("capacity",)
    assert first["network_kpi_benchmark_validation"]["evidence_present"] is True
    assert first["network_kpi_benchmark_validation"]["validation_status"] == "PASS"
    assert first["network_kpi_benchmark_validation"]["failed_check_count"] == 0
    assert first["user_service_requests"]["evidence_present"] is True
    assert first["user_service_requests"]["request_count"] == 2
    assert first["user_service_requests"]["exported_request_count"] == 2
    assert first["route_comparison_review"]["live_route_detail_endpoint"] == (
        "GET /runtime/details/routes/{route_id}"
    )
    assert first["route_comparison_review"]["exported_rows_only"] is True
    assert first["artifact_health"]["missing_required_filenames"] == ()
    assert first["artifact_health"]["missing_recommended_filenames"] == ()
    assert first["model_boundaries"]["event_replay_restore"] is False
    assert first["model_boundaries"]["route_recomputation"] is False
    assert first["model_boundaries"]["service_recomputation"] is False
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


def test_runtime_export_scenario_review_bundle_v1_is_deterministic() -> None:
    config_snapshot = {
        "type": "RUNTIME_CONFIG_SNAPSHOT",
        "status": {
            "lifecycle_state": "STOPPED",
            "current_sim_time": 120,
            "processed_event_count": 4200,
            "queued_event_count": 0,
            "route_explanation_summary_v1": _route_summary(),
            "route_provenance_trust_summary_v1": _route_trust(),
            "user_service_request_summary_v2": _user_service_request_summary(),
            "runtime_export_user_service_request_policy_v1": (
                _user_service_request_export_policy()
            ),
            "runtime_export_route_detail_policy_v1": _route_detail_export_policy(),
            "runtime_export_service_trace_policy_v1": _service_trace_export_policy(),
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
        "control_config_hash": "sha256:control",
        "generated_config_hash": "sha256:generated",
        "runtime_state_hash": "sha256:runtime",
        "metrics_summary_hash": "sha256:metrics",
    }
    filenames = (
        "config_snapshot.json",
        "diagnostics_bundle_v1.json",
        "events.jsonl",
        "export_package_audit_index_v1.json",
        "package_handoff_report_v1.md",
        "manifest.json",
        "metrics.csv",
        "network_kpi_benchmark_validation_v1.json",
        "review_summary_v1.json",
        "route_detail_index_v1.json",
        "scenario_review_bundle_v1.json",
        "service_lifecycle_trace_v2.json",
        "summary.json",
        "user_service_request_summary_v2.json",
    )
    user_configuration_export = {
        "version": "v1",
        "source": "BACKEND_USER_CONFIGURATION",
        "schema_id": "sees.user_configuration.v2",
        "export_scope": "CURRENT_EFFECTIVE_SEES_CONFIG",
        "format": "JSON_MAPPING",
        "unknown_key_policy": "REJECT",
        "defaulting_policy": "OMITTED_FIELDS_USE_BACKEND_DEFAULTS",
        "import_paths": ("CONFIG_UPDATE control message for partial updates",),
        "config_hash": "sha256:user-config",
        "validation_ok": True,
        "validation_error_count": 0,
        "config": {"seed": 7},
    }
    review_summary = build_runtime_export_review_summary_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        config_snapshot=config_snapshot,
        manifest=manifest,
        artifact_filenames=filenames,
    )
    diagnostics_bundle = build_runtime_export_diagnostics_bundle_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        config_snapshot=config_snapshot,
        manifest=manifest,
        review_summary=review_summary,
        artifact_filenames=filenames,
    )

    first = build_runtime_export_scenario_review_bundle_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        config_snapshot=config_snapshot,
        manifest=manifest,
        review_summary=review_summary,
        diagnostics_bundle=diagnostics_bundle,
        user_configuration_export=user_configuration_export,
        artifact_filenames=filenames,
    )
    second = build_runtime_export_scenario_review_bundle_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        config_snapshot=config_snapshot,
        manifest=manifest,
        review_summary=review_summary,
        diagnostics_bundle=diagnostics_bundle,
        user_configuration_export=user_configuration_export,
        artifact_filenames=tuple(reversed(filenames)),
    )

    assert first == second
    assert first["bundle_id"] == RUNTIME_EXPORT_SCENARIO_REVIEW_BUNDLE_V1_ID
    assert first["scenario_review_status"] == "SCENARIO_REVIEW_READY"
    assert first["scenario_review_warnings"] == ()
    assert first["scenario"]["satellite_count"] == 72
    assert first["user_configuration"]["config_hash"] == "sha256:user-config"
    assert first["user_configuration"]["validation_ok"] is True
    assert first["user_configuration"]["binding_hash"].startswith("sha256:")
    assert first["reproducibility"]["manifest_hash"] == "sha256:manifest"
    assert first["reproducibility"]["runtime_export_boundary_hash"].startswith(
        "sha256:"
    )
    assert first["review_summary"]["summary_hash"] == review_summary["summary_hash"]
    assert first["diagnostics"]["diagnostics_hash"] == (
        diagnostics_bundle["diagnostics_hash"]
    )
    assert first["audit_index"]["audit_index_id"] == (
        RUNTIME_EXPORT_PACKAGE_AUDIT_INDEX_V1_ID
    )
    assert first["user_service_requests"]["evidence_present"] is True
    assert first["user_service_requests"]["request_count"] == 2
    assert first["user_service_requests"]["summary_hash"] == review_summary[
        "user_service_requests"
    ]["summary_hash"]
    assert first["model_boundaries"]["packet_level_simulation"] is False
    assert first["model_boundaries"]["external_simulators"] is False
    assert first["recommended_review_order"][0] == "scenario_review_bundle_v1.json"
    assert "user_service_request_summary_v2.json" in first[
        "recommended_review_order"
    ]
    assert "service_trace_comparison_review_report_v1.json" in first[
        "recommended_review_order"
    ]
    assert first["recommended_review_order"].index(
        "service_lifecycle_trace_v2.json"
    ) < first["recommended_review_order"].index(
        "service_trace_comparison_review_report_v1.json"
    )
    assert "export_package_audit_index_v1.json" in first["artifact_review"][
        "artifact_filenames"
    ]
    assert "user_service_request_summary_v2.json" in first["artifact_review"][
        "entrypoint_filenames"
    ]
    assert first["scenario_review_hash"].startswith("sha256:")
    assert json.loads(json.dumps(first, sort_keys=True))["bundle_id"] == (
        RUNTIME_EXPORT_SCENARIO_REVIEW_BUNDLE_V1_ID
    )


def test_runtime_export_scenario_review_checklist_v1_is_deterministic() -> None:
    scenario_review_bundle = {
        "bundle_id": RUNTIME_EXPORT_SCENARIO_REVIEW_BUNDLE_V1_ID,
        "scenario_review_hash": "sha256:scenario-review",
        "recommended_review_order": (
            "scenario_review_bundle_v1.json",
            "export_package_audit_index_v1.json",
            "review_summary_v1.json",
            "service_trace_comparison_review_report_v1.json",
        ),
        "artifact_review": {
            "artifact_filenames": (
                "export_package_audit_index_v1.json",
                "scenario_review_bundle_v1.json",
                "review_summary_v1.json",
            )
        },
    }
    records = (
        {
            "step_label": "Audit index checked",
            "artifact_filename": "export_package_audit_index_v1.json",
            "review_status": "needs_followup",
            "operator_note": "route report still needs reviewer sign-off",
            "evidence_hash": "sha256:audit",
        },
        {
            "step_label": "Scenario entry checked",
            "artifact_filename": "scenario_review_bundle_v1.json",
            "review_status": "reviewed",
            "operator_note": "configuration binding is present",
            "evidence_hash": "sha256:scenario",
        },
        {
            "step_label": "Summary intentionally skipped",
            "artifact_filename": "review_summary_v1.json",
            "review_status": "skipped",
            "status_reason": "already covered by diagnostics",
        },
        {
            "step_label": "Service trace review checked",
            "artifact_filename": "service_trace_comparison_review_report_v1.json",
            "review_status": "reviewed",
            "operator_note": "service trace comparison report is signed off",
            "evidence_hash": "sha256:service-trace-report",
        },
    )

    first = build_runtime_export_scenario_review_checklist_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        scenario_review_bundle=scenario_review_bundle,
        records=records,
    )
    second = build_runtime_export_scenario_review_checklist_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        scenario_review_bundle=scenario_review_bundle,
        records=tuple(reversed(records)),
    )

    assert first == second
    assert first["checklist_id"] == RUNTIME_EXPORT_SCENARIO_REVIEW_CHECKLIST_V1_ID
    assert first["package_id"] == "pkg-1"
    assert first["scenario_review_hash"] == "sha256:scenario-review"
    assert first["record_count"] == 4
    assert first["reviewed_count"] == 2
    assert first["skipped_count"] == 1
    assert first["followup_count"] == 1
    assert first["error_count"] == 0
    assert first["checklist_status"] == "CHECKLIST_WARN"
    assert [record["artifact_filename"] for record in first["records"]] == [
        "scenario_review_bundle_v1.json",
        "export_package_audit_index_v1.json",
        "review_summary_v1.json",
        "service_trace_comparison_review_report_v1.json",
    ]
    assert first["records"][0]["review_status"] == "REVIEWED"
    assert first["records"][3]["status_reason"] == ""
    assert first["records"][0]["record_hash"].startswith("sha256:")
    assert first["checklist_hash"].startswith("sha256:")
    assert json.loads(json.dumps(first, sort_keys=True))["checklist_id"] == (
        RUNTIME_EXPORT_SCENARIO_REVIEW_CHECKLIST_V1_ID
    )


def test_runtime_export_route_detail_index_v1_is_deterministic_and_review_ready() -> None:
    config_snapshot = {
        "type": "RUNTIME_CONFIG_SNAPSHOT",
        "status": {
            "route_explanation_summary_v1": _route_summary(),
            "runtime_export_route_detail_policy_v1": _route_detail_export_policy(),
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
    assert first["route_detail_export_policy"] == _route_detail_export_policy()
    assert first["route_ids"] == ("route-0", "route-1")
    assert first["sample_route_ids"] == ("route-0", "route-1")
    assert first["indexed_sample_route_ids"] == ("route-0", "route-1")
    assert first["missing_sample_route_ids"] == ()
    assert first["route_comparison_review"]["package_route_detail_endpoint"] == (
        "GET /runtime/export/packages/{package_id}/routes/{route_id}"
    )
    assert first["route_comparison_review"]["boundary_conditions"] == (
        "NO_ROUTE_RECOMPUTE",
        "NO_EVENT_REPLAY",
        "NO_PACKET_CAPTURE",
        "NO_PACKAGE_MUTATION",
        "CURRENT_RUNTIME_MAY_DIFFER_FROM_EXPORTED_PACKAGE",
    )
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
                "runtime_export_route_detail_policy_v1": _route_detail_export_policy(),
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
    assert first["route_detail_export_policy"] == _route_detail_export_policy()
    assert first["route_comparison_review"] == route_index["route_comparison_review"]
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


def test_runtime_export_service_trace_page_v1_filters_artifact_window() -> None:
    trace_export = _service_trace_export()

    first = build_runtime_export_service_trace_page_v1(
        trace_export,
        package_id="pkg-1",
        cursor=0,
        limit=1,
        query="route-run",
        terminal_state="running",
        compute_node_id=" sat-00003 ",
        stage_kind="output-network",
        terminal_reason="output_network_pending",
    )
    second = build_runtime_export_service_trace_page_v1(
        trace_export,
        package_id="pkg-1",
        cursor=0,
        limit=1,
        query="route-run",
        terminal_state="running",
        compute_node_id=" sat-00003 ",
        stage_kind="output-network",
        terminal_reason="output_network_pending",
    )

    assert first == second
    assert first["page_id"] == RUNTIME_EXPORT_SERVICE_TRACE_PAGE_V1_ID
    assert first["type"] == "RUNTIME_EXPORT_SERVICE_TRACE_PAGE_V1"
    assert first["source"] == "BACKEND_RUNTIME_EXPORT_PACKAGE"
    assert first["package_id"] == "pkg-1"
    assert first["artifact_window_only"] is True
    assert first["service_trace_export_policy"]["policy"] == (
        "EXPORT_SERVICE_TRACE_WINDOW"
    )
    assert first["service_trace_export_policy"]["service_trace_limit"] == 5000
    assert first["artifact_type"] == "SERVICE_LIFECYCLE_TRACE_EXPORT_V2"
    assert first["trace_contract_id"] == (
        "leo_twin.service_lifecycle_trace_contract.v2"
    )
    assert first["trace_model"] == "COMMUNICATION_COMPUTE_COMPONENT_PROXY"
    assert first["cursor"] == 0
    assert first["limit"] == 1
    assert first["next_cursor"] == 1
    assert first["has_more"] is False
    assert first["trace_count"] == 1
    assert first["item_count"] == 1
    assert first["unfiltered_trace_count"] == 3
    assert first["complete_trace_count"] == 0
    assert first["running_trace_count"] == 1
    assert first["incomplete_trace_count"] == 0
    assert first["filter_applied"] is True
    assert first["filters"] == {
        "query": "route-run",
        "terminal_state": "RUNNING",
        "compute_node_id": "sat-00003",
        "stage_kind": "OUTPUT_NETWORK",
        "terminal_reason": "OUTPUT_NETWORK_PENDING",
    }
    assert first["boundary_conditions"] == (
        "ARTIFACT_WINDOW_ONLY",
        "NO_EVENT_REPLAY",
        "NO_SERVICE_RECOMPUTE",
        "NO_PACKAGE_MUTATION",
    )
    assert first["items"][0]["trace_id"] == "trace:run"
    assert first["items"][0]["compute_node_id"] == "sat-00003"
    assert first["page_hash"].startswith("sha256:")

    second_page = build_runtime_export_service_trace_page_v1(
        trace_export,
        package_id="pkg-1",
        cursor=1,
        limit=1,
    )
    assert second_page["trace_count"] == 3
    assert second_page["item_count"] == 1
    assert second_page["items"][0]["trace_id"] == "trace:run"
    assert second_page["has_more"] is True


def test_runtime_export_service_trace_item_v1_reads_exact_package_trace() -> None:
    trace_export = _service_trace_export()

    first = build_runtime_export_service_trace_item_v1(
        trace_export,
        "trace:run",
        package_id="pkg-1",
    )
    second = build_runtime_export_service_trace_item_v1(
        trace_export,
        "run",
        package_id="pkg-1",
    )

    assert first is not None
    assert second is not None
    assert first["item_id"] == RUNTIME_EXPORT_SERVICE_TRACE_ITEM_V1_ID
    assert first["type"] == "RUNTIME_EXPORT_SERVICE_TRACE_ITEM_V1"
    assert first["source"] == "BACKEND_RUNTIME_EXPORT_PACKAGE"
    assert first["package_id"] == "pkg-1"
    assert first["artifact_window_only"] is True
    assert first["trace_id"] == "trace:run"
    assert first["trace"]["trace_id"] == "trace:run"
    assert first["trace"]["compute_node_id"] == "sat-00003"
    assert first["trace"]["terminal_state"] == "RUNNING"
    assert first["trace_contract_id"] == (
        "leo_twin.service_lifecycle_trace_contract.v2"
    )
    assert first["boundary_conditions"] == (
        "ARTIFACT_WINDOW_ONLY",
        "NO_EVENT_REPLAY",
        "NO_SERVICE_RECOMPUTE",
        "NO_PACKAGE_MUTATION",
    )
    assert first["item_hash"].startswith("sha256:")
    assert second["trace"]["trace_id"] == "trace:run"
    assert (
        build_runtime_export_service_trace_item_v1(trace_export, "missing")
        is None
    )


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
    assert detail["route_comparison_review"] == route_index["route_comparison_review"]
    assert detail["route_id"] == "route-1"
    assert detail["route"]["path_label"] == "user-1 -> sat-1"
    assert detail["item_hash"].startswith("sha256:")
    assert build_runtime_export_route_detail_item_v1(route_index, "missing") is None


def test_runtime_export_route_comparison_review_report_v1_is_deterministic() -> None:
    route_index = build_runtime_export_route_detail_index_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        config_snapshot={
            "type": "RUNTIME_CONFIG_SNAPSHOT",
            "status": {
                "route_explanation_summary_v1": _route_summary(),
                "runtime_export_route_detail_policy_v1": _route_detail_export_policy(),
                "route_provenance_trust_summary_v1": _route_trust(),
            },
        },
    )
    review = route_index["route_comparison_review"]
    runtime_export_boundary_alignment = {
        "type": "RUNTIME_EXPORT_BOUNDARY_ALIGNMENT_V1",
        "version": "v1",
        "alignment_id": "leo_twin.runtime_export_boundary_alignment.v1",
        "source": "BACKEND_RUNTIME_EXPORT_RESTORE_PREFLIGHT",
        "alignment_scope": "PACKAGE_COMPARE_AND_RESTORE_BOUNDARY",
        "package_id": "pkg-1",
        "package_boundary_present": True,
        "current_boundary_present": False,
        "boundary_hash": "sha256:boundary-1",
        "current_boundary_hash": "",
        "boundary_hash_matches_current": False,
        "boundary_id_aligned": True,
        "restore_scope": "CONFIG_ONLY",
        "compare_scope": "CONFIG_AND_GENERATED_CONFIG",
        "read_scope": "PERSISTED_ARTIFACTS_ONLY",
        "preflight_scope": "CONFIG_RESTORE_PREVIEW_ONLY",
        "compare_scope_aligned": True,
        "restore_scope_aligned": True,
        "read_scope_aligned": True,
        "preflight_scope_aligned": True,
        "forbidden_behavior_inactive": True,
        "event_replay_restore": False,
        "live_event_replay_restore": False,
        "recompute_on_read": False,
        "route_recomputation": False,
        "service_recomputation": False,
        "package_mutation_on_read": False,
        "packet_capture": False,
        "packet_level_simulation": False,
        "external_simulators": False,
        "alignment_status": "ALIGNED",
        "warnings": (),
        "alignment_hash": "sha256:alignment-1",
    }
    records = (
        {
            "route_id": "route-1",
            "comparison_status": "different",
            "package_route_detail_hash": "sha256:package-route-1",
            "live_route_detail_hash": "sha256:live-route-1",
            "compared_fields": ("latency", "bottleneck", "path"),
            "different_fields": ("bottleneck", "latency"),
            "status_reason": "FIELDS_DIFFER",
            "operator_note": "capacity changed after runtime advanced",
        },
        {
            "route_id": "route-0",
            "comparison_status": "match",
            "package_route_detail_hash": "sha256:package-route-0",
            "live_route_detail_hash": "sha256:live-route-0",
            "compared_fields": ("availability", "path"),
            "different_fields": (),
            "status_reason": "MATCHED",
        },
    )

    first = build_runtime_export_route_comparison_review_report_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        route_comparison_review=review,
        runtime_export_boundary_alignment=runtime_export_boundary_alignment,
        records=records,
    )
    second = build_runtime_export_route_comparison_review_report_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        route_comparison_review=review,
        runtime_export_boundary_alignment=runtime_export_boundary_alignment,
        records=tuple(reversed(records)),
    )

    assert first == second
    assert first["report_id"] == RUNTIME_EXPORT_ROUTE_COMPARISON_REVIEW_REPORT_V1_ID
    assert first["record_count"] == 2
    assert first["match_count"] == 1
    assert first["different_count"] == 1
    assert first["unavailable_count"] == 0
    assert first["error_count"] == 0
    assert [record["route_id"] for record in first["records"]] == [
        "route-0",
        "route-1",
    ]
    assert first["records"][1]["different_fields"] == ("latency", "bottleneck")
    assert first["records"][1]["matched_field_count"] == 1
    assert first["records"][1]["different_field_count"] == 2
    assert first["records"][1]["operator_note"] == (
        "capacity changed after runtime advanced"
    )
    assert first["runtime_export_boundary_alignment_v1"] == (
        runtime_export_boundary_alignment
    )
    assert first["boundary_alignment_hash"] == "sha256:alignment-1"
    assert first["boundary_alignment_status"] == "ALIGNED"
    assert first["boundary_alignment_warnings"] == ()
    assert first["runtime_export_boundary_hash"] == "sha256:boundary-1"
    assert first["boundary_conditions"] == review["boundary_conditions"]
    assert first["report_hash"].startswith("sha256:")
    assert json.loads(json.dumps(first, sort_keys=True))["report_id"] == (
        RUNTIME_EXPORT_ROUTE_COMPARISON_REVIEW_REPORT_V1_ID
    )


def test_runtime_export_service_trace_comparison_review_report_v1_is_deterministic() -> None:
    service_trace_page = build_runtime_export_service_trace_page_v1(
        _service_trace_export(),
        package_id="pkg-1",
    )
    review = service_trace_page["service_trace_comparison_review"]
    runtime_export_boundary_alignment = {
        "type": "RUNTIME_EXPORT_BOUNDARY_ALIGNMENT_V1",
        "version": "v1",
        "alignment_id": "leo_twin.runtime_export_boundary_alignment.v1",
        "source": "BACKEND_RUNTIME_EXPORT_RESTORE_PREFLIGHT",
        "alignment_scope": "PACKAGE_COMPARE_AND_RESTORE_BOUNDARY",
        "package_id": "pkg-1",
        "boundary_hash": "sha256:boundary-1",
        "alignment_status": "ALIGNED",
        "warnings": (),
        "alignment_hash": "sha256:alignment-1",
    }
    records = (
        {
            "trace_id": "trace:run",
            "comparison_status": "different",
            "package_trace_item_hash": "sha256:package-trace-1",
            "live_trace_detail_hash": "",
            "compared_fields": (
                "terminal",
                "reason",
                "total_latency",
                "stage_counts",
            ),
            "different_fields": ("stage_counts", "terminal"),
            "status_reason": "FIELDS_DIFFER",
            "operator_note": "trace finished after package export",
        },
        {
            "trace_id": "trace:done",
            "comparison_status": "match",
            "package_trace_item_hash": "sha256:package-trace-0",
            "live_trace_detail_hash": "",
            "compared_fields": ("terminal", "total_latency"),
            "different_fields": (),
            "status_reason": "MATCHED",
        },
    )

    first = build_runtime_export_service_trace_comparison_review_report_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        service_trace_comparison_review=review,
        runtime_export_boundary_alignment=runtime_export_boundary_alignment,
        records=records,
    )
    second = build_runtime_export_service_trace_comparison_review_report_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        service_trace_comparison_review=review,
        runtime_export_boundary_alignment=runtime_export_boundary_alignment,
        records=tuple(reversed(records)),
    )

    assert first == second
    assert first["report_id"] == (
        RUNTIME_EXPORT_SERVICE_TRACE_COMPARISON_REVIEW_REPORT_V1_ID
    )
    assert first["record_count"] == 2
    assert first["match_count"] == 1
    assert first["different_count"] == 1
    assert [record["trace_id"] for record in first["records"]] == [
        "trace:done",
        "trace:run",
    ]
    assert first["records"][1]["different_fields"] == (
        "terminal",
        "stage_counts",
    )
    assert first["records"][1]["matched_field_count"] == 2
    assert first["records"][1]["different_field_count"] == 2
    assert first["records"][1]["operator_note"] == (
        "trace finished after package export"
    )
    assert first["runtime_export_boundary_alignment_v1"] == (
        runtime_export_boundary_alignment
    )
    assert first["boundary_alignment_hash"] == "sha256:alignment-1"
    assert first["boundary_alignment_status"] == "ALIGNED"
    assert first["runtime_export_boundary_hash"] == "sha256:boundary-1"
    assert first["boundary_conditions"] == review["boundary_conditions"]
    assert first["report_hash"].startswith("sha256:")
    assert json.loads(json.dumps(first, sort_keys=True))["report_id"] == (
        RUNTIME_EXPORT_SERVICE_TRACE_COMPARISON_REVIEW_REPORT_V1_ID
    )


def test_runtime_export_service_trace_comparison_review_report_page_v1_filters_records() -> None:
    service_trace_page = build_runtime_export_service_trace_page_v1(
        _service_trace_export(),
        package_id="pkg-1",
    )
    review = service_trace_page["service_trace_comparison_review"]
    report = build_runtime_export_service_trace_comparison_review_report_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        service_trace_comparison_review=review,
        records=(
            {
                "trace_id": "trace:done",
                "comparison_status": "MATCH",
                "package_trace_item_hash": "sha256:package-trace-0",
                "live_trace_detail_hash": "sha256:live-trace-0",
                "compared_fields": ("terminal", "total_latency"),
                "different_fields": (),
                "status_reason": "MATCHED",
                "operator_note": "baseline aligned",
            },
            {
                "trace_id": "trace:run",
                "comparison_status": "DIFFERENT",
                "package_trace_item_hash": "sha256:package-trace-1",
                "live_trace_detail_hash": "sha256:live-trace-1",
                "compared_fields": (
                    "terminal",
                    "reason",
                    "total_latency",
                    "stage_counts",
                ),
                "different_fields": ("stage_counts", "terminal"),
                "status_reason": "FIELDS_DIFFER",
                "operator_note": "trace finished after package export",
            },
            {
                "trace_id": "trace:missing",
                "comparison_status": "UNAVAILABLE",
                "package_trace_item_hash": "sha256:package-trace-2",
                "live_trace_detail_hash": "",
                "compared_fields": (),
                "different_fields": (),
                "status_reason": "LIVE_TRACE_MISSING",
                "operator_note": "live runtime no longer has trace",
            },
        ),
    )

    first_page = build_runtime_export_service_trace_comparison_review_report_page_v1(
        report,
        cursor=0,
        limit=2,
    )
    second_page = build_runtime_export_service_trace_comparison_review_report_page_v1(
        report,
        cursor=2,
        limit=2,
    )
    filtered = build_runtime_export_service_trace_comparison_review_report_page_v1(
        report,
        status="different",
        query="after package",
    )
    repeated = build_runtime_export_service_trace_comparison_review_report_page_v1(
        report,
        status="different",
        query="after package",
    )

    assert first_page["page_id"] == (
        RUNTIME_EXPORT_SERVICE_TRACE_COMPARISON_REVIEW_REPORT_PAGE_V1_ID
    )
    assert first_page["report_hash"] == report["report_hash"]
    assert first_page["record_count"] == 3
    assert first_page["item_count"] == 2
    assert first_page["next_cursor"] == 2
    assert first_page["has_more"] is True
    assert [record["trace_id"] for record in first_page["records"]] == [
        "trace:done",
        "trace:missing",
    ]
    assert [record["trace_id"] for record in second_page["records"]] == [
        "trace:run",
    ]
    assert filtered == repeated
    assert filtered["filter_applied"] is True
    assert filtered["filters"] == {"query": "after package", "status": "DIFFERENT"}
    assert filtered["record_count"] == 1
    assert filtered["different_count"] == 1
    assert filtered["records"][0]["trace_id"] == "trace:run"
    assert filtered["page_hash"].startswith("sha256:")


def test_runtime_export_package_review_completion_v1_reports_missing_evidence() -> None:
    completion = build_runtime_export_package_review_completion_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        audit_status="AUDIT_WARN",
        audit_warnings=("ROUTE_COMPARISON_REVIEW_REPORT_NOT_SAVED",),
        review_summary={
            "summary_id": RUNTIME_EXPORT_REVIEW_SUMMARY_V1_ID,
            "summary_hash": "sha256:review",
            "review_status": "REVIEW_READY",
        },
        diagnostics_bundle={
            "bundle_id": RUNTIME_EXPORT_DIAGNOSTICS_BUNDLE_V1_ID,
            "diagnostics_hash": "sha256:diagnostics",
            "findings": (),
        },
        artifact_records=(
            _file(
                "scenario_review_bundle_v1",
                "scenario_review_bundle_v1.json",
                "sha256:scenario-bundle-file",
            ),
        ),
        route_comparison_review_report=None,
        scenario_review_checklist=None,
        runtime_export_boundary_alignment={
            "alignment_status": "ALIGNED",
            "alignment_hash": "sha256:alignment",
        },
        user_configuration_binding={"validation_ok": True},
    )

    assert completion["completion_id"] == RUNTIME_EXPORT_PACKAGE_REVIEW_COMPLETION_V1_ID
    assert completion["completion_status"] == "REVIEW_INCOMPLETE"
    assert completion["handoff_ready"] is False
    assert completion["route_comparison_review_report_present"] is False
    assert completion["service_trace_comparison_review_report_present"] is False
    assert completion["service_trace_comparison_review_error_count"] == 0
    assert completion["scenario_review_checklist_present"] is False
    assert completion["missing_or_warning_evidence"] == (
        "AUDIT_INDEX_NOT_READY",
        "ROUTE_COMPARISON_REVIEW_REPORT_MISSING",
        "SCENARIO_REVIEW_CHECKLIST_MISSING",
    )
    assert completion["completion_hash"].startswith("sha256:")


def test_runtime_export_package_handoff_report_v1_is_deterministic() -> None:
    audit_index = {
        "audit_index_id": RUNTIME_EXPORT_PACKAGE_AUDIT_INDEX_V1_ID,
        "package_id": "pkg-1",
        "audit_hash": "sha256:audit",
        "manifest_hash": "sha256:manifest",
        "runtime_export_boundary_hash": "sha256:boundary",
        "package_review_completion_v1": {
            "completion_id": RUNTIME_EXPORT_PACKAGE_REVIEW_COMPLETION_V1_ID,
            "package_id": "pkg-1",
            "completion_status": "REVIEW_COMPLETE",
            "handoff_ready": True,
            "completion_hash": "sha256:completion",
            "audit_status": "AUDIT_READY",
            "route_comparison_review_report_present": True,
            "route_comparison_review_error_count": 0,
            "route_comparison_review_report_hash": "sha256:route-report",
            "scenario_review_checklist_status": "CHECKLIST_COMPLETE",
            "scenario_review_checklist_record_count": 2,
            "scenario_review_checklist_hash": "sha256:checklist",
            "review_summary_status": "REVIEW_READY",
            "review_summary_hash": "sha256:review",
            "diagnostics_error_count": 0,
            "diagnostics_hash": "sha256:diagnostics",
            "boundary_alignment_status": "ALIGNED",
            "user_configuration_validation_ok": True,
            "missing_or_warning_evidence": (),
            "evidence_labels": ("audit AUDIT_READY", "route_report saved"),
            "boundary_conditions": (
                "NO_EVENT_REPLAY",
                "NO_MODEL_RECOMPUTE",
                "NO_PACKAGE_READ_MUTATION",
                "BACKEND_OWNED_HANDOFF_SUMMARY",
            ),
        },
    }

    first = build_runtime_export_package_handoff_report_v1(
        audit_index=audit_index,
    )
    second = build_runtime_export_package_handoff_report_v1(
        audit_index=json.loads(json.dumps(audit_index, sort_keys=True)),
    )

    assert first == second
    assert first.startswith("# Runtime Export Package Handoff Report v1\n")
    assert f"Report id: {RUNTIME_EXPORT_PACKAGE_HANDOFF_REPORT_V1_ID}" in first
    assert "Package id: pkg-1" in first
    assert "Completion status: REVIEW_COMPLETE" in first
    assert "Handoff ready: true" in first
    assert "Completion hash: sha256:completion" in first
    assert "- No blocking evidence is missing." in first
    assert "- NO_EVENT_REPLAY" in first
    assert "external simulators" in first


def test_runtime_export_package_audit_index_v1_is_deterministic() -> None:
    boundary = {
        "boundary_id": RUNTIME_EXPORT_REPRODUCIBILITY_BOUNDARY_V1_ID,
        "boundary_hash": "sha256:boundary",
    }
    alignment = {
        "alignment_id": "leo_twin.runtime_export_boundary_alignment.v1",
        "alignment_hash": "sha256:alignment",
        "alignment_status": "ALIGNED",
        "boundary_hash": "sha256:boundary",
        "warnings": (),
    }
    route_report = {
        "report_id": RUNTIME_EXPORT_ROUTE_COMPARISON_REVIEW_REPORT_V1_ID,
        "report_hash": "sha256:route-report",
        "record_count": 1,
        "error_count": 0,
        "runtime_export_boundary_alignment_v1": alignment,
    }
    service_trace_report = {
        "report_id": RUNTIME_EXPORT_SERVICE_TRACE_COMPARISON_REVIEW_REPORT_V1_ID,
        "report_hash": "sha256:service-trace-report",
        "record_count": 2,
        "error_count": 0,
    }
    scenario_review_checklist = {
        "checklist_id": RUNTIME_EXPORT_SCENARIO_REVIEW_CHECKLIST_V1_ID,
        "checklist_hash": "sha256:scenario-checklist",
        "checklist_status": "CHECKLIST_COMPLETE",
        "record_count": 2,
    }
    user_configuration_export = {
        "version": "v1",
        "source": "BACKEND_USER_CONFIGURATION",
        "schema_id": "sees.user_configuration.v2",
        "export_scope": "CURRENT_EFFECTIVE_SEES_CONFIG",
        "format": "JSON_MAPPING",
        "unknown_key_policy": "REJECT",
        "defaulting_policy": "OMITTED_FIELDS_USE_BACKEND_DEFAULTS",
        "import_paths": (
            "CONFIG_UPDATE control message for partial updates",
            "LOAD_TEMPLATE control message for approved templates",
        ),
        "config_hash": "sha256:user-config",
        "validation_ok": True,
        "validation_error_count": 0,
        "validation_errors": (),
        "config": {"seed": 7},
    }
    config_snapshot = {
        "type": "RUNTIME_CONFIG_SNAPSHOT",
        "status": {"runtime_export_reproducibility_boundary_v1": boundary},
        "config": {"seed": 7},
        "generated_config": {"seed": 7, "satellite_count": 72},
    }
    manifest = {
        "manifest_id": RUNTIME_REPRODUCIBILITY_MANIFEST_V1_ID,
        "manifest_hash": "sha256:manifest",
        "control_config_hash": "sha256:control",
        "generated_config_hash": "sha256:generated",
        "runtime_state_hash": "sha256:runtime",
        "runtime_export_reproducibility_boundary_v1": boundary,
    }
    review_summary = {
        "summary_id": RUNTIME_EXPORT_REVIEW_SUMMARY_V1_ID,
        "summary_hash": "sha256:review",
        "review_status": "REVIEW_READY",
    }
    diagnostics_bundle = {
        "bundle_id": RUNTIME_EXPORT_DIAGNOSTICS_BUNDLE_V1_ID,
        "diagnostics_hash": "sha256:diagnostics",
        "findings": ({"severity": "INFO", "code": "OK", "message": "ready"},),
    }
    artifact_records = (
        _file("manifest", "manifest.json", "sha256:manifest-file"),
        _file("config_snapshot", "config_snapshot.json", "sha256:config-file"),
        _file("events", "events.jsonl", "sha256:events-file"),
        _file("metrics", "metrics.csv", "sha256:metrics-file"),
        _file("summary", "summary.json", "sha256:summary-file"),
        _file(
            "route_comparison_review_report_v1",
            "route_comparison_review_report_v1.json",
            "sha256:route-report-file",
        ),
        _file(
            "service_trace_comparison_review_report_v1",
            "service_trace_comparison_review_report_v1.json",
            "sha256:service-trace-report-file",
        ),
        _file(
            "scenario_review_checklist_v1",
            "scenario_review_checklist_v1.json",
            "sha256:scenario-checklist-file",
        ),
        _file(
            "scenario_review_bundle_v1",
            "scenario_review_bundle_v1.json",
            "sha256:scenario-bundle-file",
        ),
    )

    first = build_runtime_export_package_audit_index_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        config_snapshot=config_snapshot,
        manifest=manifest,
        review_summary=review_summary,
        diagnostics_bundle=diagnostics_bundle,
        artifact_records=artifact_records,
        route_comparison_review_report=route_report,
        service_trace_comparison_review_report=service_trace_report,
        scenario_review_checklist=scenario_review_checklist,
        user_configuration_export=user_configuration_export,
    )
    second = build_runtime_export_package_audit_index_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        config_snapshot=config_snapshot,
        manifest=manifest,
        review_summary=review_summary,
        diagnostics_bundle=diagnostics_bundle,
        artifact_records=tuple(reversed(artifact_records)),
        route_comparison_review_report=route_report,
        service_trace_comparison_review_report=service_trace_report,
        scenario_review_checklist=scenario_review_checklist,
        user_configuration_export=user_configuration_export,
    )

    assert first == second
    assert first["audit_index_id"] == RUNTIME_EXPORT_PACKAGE_AUDIT_INDEX_V1_ID
    assert first["audit_status"] == "AUDIT_READY"
    assert first["audit_warnings"] == ()
    assert first["manifest_hash"] == "sha256:manifest"
    assert first["runtime_export_boundary_hash"] == "sha256:boundary"
    assert first["boundary_alignment_hash"] == "sha256:alignment"
    assert first["user_configuration_schema_id"] == "sees.user_configuration.v2"
    assert first["user_configuration_config_hash"] == "sha256:user-config"
    assert first["user_configuration_validation_ok"] is True
    assert first["user_configuration_binding_v1"]["binding_id"] == (
        "leo_twin.user_configuration_audit_binding.v1"
    )
    assert first["user_configuration_binding_v1"]["binding_hash"].startswith(
        "sha256:"
    )
    assert first["route_comparison_review_report_hash"] == "sha256:route-report"
    assert first["route_comparison_review_report_present"] is True
    assert first["service_trace_comparison_review_report_hash"] == (
        "sha256:service-trace-report"
    )
    assert first["service_trace_comparison_review_report_present"] is True
    assert first["service_trace_comparison_review_record_count"] == 2
    assert first["service_trace_comparison_review_error_count"] == 0
    assert first["scenario_review_checklist_hash"] == "sha256:scenario-checklist"
    assert first["scenario_review_checklist_present"] is True
    assert first["scenario_review_checklist_record_count"] == 2
    assert first["scenario_review_checklist_status"] == "CHECKLIST_COMPLETE"
    completion = first["package_review_completion_v1"]
    assert completion["completion_id"] == RUNTIME_EXPORT_PACKAGE_REVIEW_COMPLETION_V1_ID
    assert completion["completion_status"] == "REVIEW_COMPLETE"
    assert completion["handoff_ready"] is True
    assert completion["route_comparison_review_report_present"] is True
    assert completion["service_trace_comparison_review_report_present"] is True
    assert completion["service_trace_comparison_review_record_count"] == 2
    assert completion["service_trace_comparison_review_error_count"] == 0
    assert completion["scenario_review_checklist_status"] == "CHECKLIST_COMPLETE"
    assert completion["missing_or_warning_evidence"] == ()
    assert completion["completion_hash"].startswith("sha256:")
    assert first["package_review_completion_status"] == "REVIEW_COMPLETE"
    assert first["package_review_completion_hash"] == completion["completion_hash"]
    assert first["self_artifact_excluded_from_hashes"] is True
    assert [item["filename"] for item in first["artifact_hashes"]] == [
        "config_snapshot.json",
        "events.jsonl",
        "manifest.json",
        "metrics.csv",
        "route_comparison_review_report_v1.json",
        "scenario_review_bundle_v1.json",
        "scenario_review_checklist_v1.json",
        "service_trace_comparison_review_report_v1.json",
        "summary.json",
    ]
    assert first["audit_hash"].startswith("sha256:")
    assert json.loads(json.dumps(first, sort_keys=True))["audit_index_id"] == (
        RUNTIME_EXPORT_PACKAGE_AUDIT_INDEX_V1_ID
    )


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
        "export_package_audit_index_v1.json",
        "package_handoff_report_v1.md",
        "manifest.json",
        "metrics.csv",
        "network_kpi_benchmark_validation_v1.json",
        "review_summary_v1.json",
        "route_detail_index_v1.json",
        "scenario_review_bundle_v1.json",
        "service_lifecycle_trace_v2.json",
        "summary.json",
        "user_service_request_summary_v2.json",
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
    } == {
        "ROUTE_TRUST_EVIDENCE_MISSING",
        "NETWORK_KPI_BENCHMARK_VALIDATION_MISSING",
        "USER_SERVICE_REQUEST_SUMMARY_MISSING",
    }
    assert diagnostics["finding_count"] == 3


def _file(name: str, filename: str, sha256: str) -> dict[str, object]:
    return {
        "name": name,
        "filename": filename,
        "path": f"exports/pkg-1/{filename}",
        "bytes": 10,
        "sha256": sha256,
    }


def _service_trace_export() -> dict[str, object]:
    return {
        "type": "SERVICE_LIFECYCLE_TRACE_EXPORT_V2",
        "source": "BACKEND_RUNTIME_STATUS",
        "artifact_policy": "STANDALONE_RUNTIME_EXPORT_ARTIFACT",
        "service_trace_export_policy": _service_trace_export_policy(),
        "summary": {
            "version": "v2",
            "contract_id": "leo_twin.service_lifecycle_trace_contract.v2",
            "source": "SERVICE_LATENCY_HISTORY",
            "source_summary": "service_latency_history_v1",
            "summary_scope": "SERVICE_LIFECYCLE_TRACE_WINDOW",
            "trace_model": "COMMUNICATION_COMPUTE_COMPONENT_PROXY",
            "cursor": 0,
            "limit": 100,
            "next_cursor": 3,
            "has_more": False,
            "service_count": 3,
            "trace_count": 3,
            "complete_trace_count": 1,
            "running_trace_count": 1,
            "incomplete_trace_count": 1,
            "hidden_trace_count": 0,
            "items": (
                _service_trace_item(
                    trace_id="trace:done",
                    service_id="svc-done",
                    task_id="task-done",
                    input_route_id="route-done-in",
                    output_route_id="route-done-out",
                    compute_node_id="sat-00002",
                    terminal_state="COMPLETE",
                    terminal_state_reason="TOTAL_LATENCY_OBSERVED",
                ),
                _service_trace_item(
                    trace_id="trace:run",
                    service_id="svc-run",
                    task_id="task-run",
                    input_route_id="route-run-in",
                    output_route_id="",
                    compute_node_id="sat-00003",
                    terminal_state="RUNNING",
                    terminal_state_reason="OUTPUT_NETWORK_PENDING",
                ),
                _service_trace_item(
                    trace_id="trace:queued",
                    service_id="svc-queued",
                    task_id="task-queued",
                    input_route_id="route-queued-in",
                    output_route_id="",
                    compute_node_id="sat-00004",
                    terminal_state="INCOMPLETE",
                    terminal_state_reason="NO_COMPONENT_OBSERVATIONS",
                ),
            ),
        },
    }


def _service_trace_export_policy() -> dict[str, object]:
    return {
        "version": "v1",
        "source": "BACKEND_RUNTIME_EXPORT",
        "policy": "EXPORT_SERVICE_TRACE_WINDOW",
        "service_trace_source": "service_latency_history_v1",
        "service_trace_limit": 5000,
        "service_count": 3,
        "exported_trace_count": 3,
        "hidden_trace_count": 0,
        "artifact_window_only": True,
        "event_replay": False,
        "service_recomputation": False,
        "packet_level_simulation": False,
    }


def _service_trace_item(
    *,
    trace_id: str,
    service_id: str,
    task_id: str,
    input_route_id: str,
    output_route_id: str,
    compute_node_id: str,
    terminal_state: str,
    terminal_state_reason: str,
) -> dict[str, object]:
    return {
        "trace_id": trace_id,
        "service_id": service_id,
        "task_id": task_id,
        "service_class": "COMPUTE_SERVICE",
        "input_flow_id": f"{service_id}:input",
        "output_flow_id": f"{service_id}:output",
        "input_route_id": input_route_id,
        "output_route_id": output_route_id,
        "compute_node_id": compute_node_id,
        "placement_status": "PLACED",
        "input_network_latency_s": 1.0,
        "compute_queue_delay_s": 0.25,
        "compute_execution_delay_s": 2.0,
        "output_network_latency_s": 1.0 if output_route_id else 0.0,
        "total_latency_s": 4.25 if terminal_state == "COMPLETE" else 0.0,
        "terminal_state": terminal_state,
        "terminal_state_reason": terminal_state_reason,
        "stage_count": 4,
        "observed_stage_count": 4 if terminal_state == "COMPLETE" else 3,
        "pending_stage_count": 0 if terminal_state == "COMPLETE" else 1,
        "stages": (
            _service_trace_stage(
                trace_id,
                0,
                "input_network",
                "NETWORK",
                "Input network",
                "OBSERVED",
                input_route_id,
            ),
            _service_trace_stage(
                trace_id,
                1,
                "compute_queue",
                "COMPUTE_QUEUE",
                "Compute queue",
                "OBSERVED",
                "",
            ),
            _service_trace_stage(
                trace_id,
                2,
                "compute_execution",
                "COMPUTE_EXECUTION",
                "Compute execution",
                "OBSERVED",
                "",
            ),
            _service_trace_stage(
                trace_id,
                3,
                "output_network",
                "NETWORK",
                "Output network",
                "OBSERVED" if output_route_id else "PENDING",
                output_route_id,
            ),
        ),
    }


def _service_trace_stage(
    trace_id: str,
    stage_index: int,
    component: str,
    stage_kind: str,
    stage_label: str,
    stage_status: str,
    route_id: str,
) -> dict[str, object]:
    return {
        "stage_index": stage_index,
        "stage_id": f"{trace_id}:{component}",
        "component": component,
        "stage_kind": stage_kind,
        "stage_label": stage_label,
        "stage_status": stage_status,
        "duration_s": 1.0 if stage_status == "OBSERVED" else 0.0,
        "flow_id": f"{trace_id}:{component}:flow",
        "route_id": route_id,
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


def _network_kpi_benchmark_validation() -> dict[str, object]:
    return {
        "version": "v1",
        "validation_id": "leo_twin.network_kpi_benchmark_validation.v1",
        "source": "NETWORK_KPI_PROVENANCE_V2_AND_METRICS_SUMMARY",
        "benchmark_profile": "FLOW_LEVEL_PROXY_RUNTIME_GUARDRAILS",
        "provenance_id": "leo_twin.network_kpi_provenance.v2",
        "metric_model": "FLOW_LEVEL_NETWORK_KPI_PROXY",
        "packet_level_simulation": False,
        "validation_status": "PASS",
        "check_count": 3,
        "passed_check_count": 3,
        "warning_check_count": 0,
        "failed_check_count": 0,
        "missing_check_count": 0,
        "checks": (
            {
                "check_id": "packet_level_guard",
                "metric": "network_kpi_provenance_v2.packet_level_simulation",
                "current_value": False,
                "status": "PASS",
                "severity": "FAIL",
                "expectation": "no packet-level simulation",
                "source": "network_kpi_provenance_v2",
                "explanation": "flow-level proxy only",
            },
        ),
        "caveats": (
            "Benchmark validation v1 is a deterministic product guardrail.",
        ),
    }


def _user_service_request_summary() -> dict[str, object]:
    return {
        "version": "v2",
        "source": "BACKEND_RUNTIME_STATUS",
        "summary_scope": "USER_SERVICE_REQUEST_WINDOW",
        "request_model": "FLOW_LEVEL_USER_SERVICE_REQUEST_PROXY",
        "route_model": "FLOW_LEVEL_ROUTE_PROXY",
        "compute_model": "SERVICE_LIFECYCLE_PROXY",
        "packet_level_simulation": False,
        "frontend_inference_required": False,
        "cursor": 0,
        "limit": 5000,
        "next_cursor": 2,
        "has_more": False,
        "user_count": 2,
        "request_count": 2,
        "item_count": 2,
        "active_user_count": 2,
        "active_request_count": 2,
        "communication_request_count": 2,
        "compute_service_user_count": 1,
        "compute_request_count": 1,
        "waiting_user_count": 1,
        "network_waiting_request_count": 1,
        "completed_request_count": 0,
        "hidden_user_count": 0,
        "hidden_request_count": 0,
        "service_class_counts": (
            {"service_class": "COMPUTE_SERVICE", "request_count": 1},
            {"service_class": "DATA_TRANSFER", "request_count": 1},
        ),
        "terminal_state_counts": (
            {"terminal_state": "RUNNING_COMPUTE_SERVICE", "request_count": 1},
            {"terminal_state": "WAITING_NETWORK", "request_count": 1},
        ),
        "model_assumptions": (
            "One row summarizes the current flow-level request state for one user.",
            "Packet-level behavior is not simulated.",
        ),
        "items": (
            {
                "request_id": "service-0",
                "trace_id": "trace:service-0",
                "user_id": "user-0",
                "service_class": "COMPUTE_SERVICE",
                "request_state": "COMPUTE_SERVICE_ACTIVE",
                "terminal_state": "RUNNING_COMPUTE_SERVICE",
                "selected_satellite_id": "sat-0",
                "target_node_id": "sat-0",
                "network_queue_depth": 0,
                "detail_hash": "sha256:user-service-0",
            },
            {
                "request_id": "flow-1",
                "trace_id": "",
                "user_id": "user-1",
                "service_class": "DATA_TRANSFER",
                "request_state": "NETWORK_WAITING",
                "terminal_state": "WAITING_NETWORK",
                "selected_satellite_id": "sat-1",
                "target_node_id": "ground-station-0",
                "network_queue_depth": 1,
                "detail_hash": "sha256:user-service-1",
            },
        ),
    }


def _user_service_request_export_policy() -> dict[str, object]:
    return {
        "version": "v1",
        "source": "BACKEND_RUNTIME_EXPORT",
        "policy": "EXPORT_USER_SERVICE_REQUEST_WINDOW",
        "user_service_request_source": (
            "visible_snapshot.ground_users/routes + service_latency_history_v1"
        ),
        "user_service_request_limit": 5000,
        "request_count": 2,
        "exported_request_count": 2,
        "hidden_request_count": 0,
        "artifact_window_only": True,
        "event_replay": False,
        "service_recomputation": False,
        "packet_level_simulation": False,
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


def _route_detail_export_policy() -> dict[str, object]:
    return {
        "version": "v1",
        "source": "BACKEND_RUNTIME_EXPORT",
        "policy": "EXPORT_ROUTE_DETAIL_INDEX_WINDOW",
        "route_summary_source": "visible_snapshot.routes",
        "route_detail_limit": 5000,
        "route_count": 2,
        "indexed_route_count": 2,
        "hidden_route_count": 0,
        "packet_level_simulation": False,
        "all_pairs_computation": False,
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
