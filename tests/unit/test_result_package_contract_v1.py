from __future__ import annotations

import json
from pathlib import Path

from leo_twin.schema.config import config_to_dict
from leo_twin.schema.config_loader import load_config
from leo_twin.services.benchmark_scenarios import (
    benchmark_scenario_by_id,
    benchmark_scenario_ids,
)
from leo_twin.services.result_package_contract import (
    RESULT_PACKAGE_CONTRACT_V1_ID,
    RUNTIME_EXPORT_ARTIFACT_BROWSER_INDEX_V1_ID,
    RUNTIME_EXPORT_DIAGNOSTICS_BUNDLE_V1_ID,
    RUNTIME_EXPORT_NETWORK_KPI_BENCHMARK_VALIDATION_V1_ID,
    RUNTIME_EXPORT_NETWORK_KPI_FORMULA_EVIDENCE_V1_ID,
    RUNTIME_EXPORT_NETWORK_TEMPORAL_PRESSURE_EVIDENCE_V1_ID,
    RUNTIME_EXPORT_NETWORK_KPI_DYNAMIC_STATUS_V1_ID,
    RUNTIME_EXPORT_NODE_NETWORK_PRESSURE_SUMMARY_V1_ID,
    RUNTIME_EXPORT_COMPUTE_RESOURCE_POOL_SUMMARY_V1_ID,
    RUNTIME_EXPORT_RUNTIME_KPI_MOVEMENT_SUMMARY_V1_ID,
    RUNTIME_EXPORT_RUNTIME_CLOSURE_READINESS_V1_ID,
    RUNTIME_EXPORT_RUNTIME_DASHBOARD_KPI_V1_ID,
    RUNTIME_EXPORT_NETWORK_FLOW_LIFECYCLE_SUMMARY_V1_ID,
    RUNTIME_EXPORT_SERVICE_LIFECYCLE_STAGE_SUMMARY_V1_ID,
    RUNTIME_EXPORT_TRAFFIC_DEMAND_EXPLANATION_V1_ID,
    RUNTIME_EXPORT_TRAFFIC_BUSINESS_ACTIVITY_WINDOW_V1_ID,
    RUNTIME_EXPORT_TRAFFIC_DEMAND_USER_PAGE_V1_ID,
    RUNTIME_EXPORT_V2_EXECUTABLE_READINESS_V1_ID,
    RUNTIME_EXPORT_USER_CONFIGURATION_TEMPLATE_VALIDATION_V1_ID,
    RUNTIME_EXPORT_USER_CONFIGURATION_CONTROL_SURFACE_EVIDENCE_V1_ID,
    RUNTIME_EXPORT_PACKAGE_AUDIT_INDEX_V1_ID,
    RUNTIME_EXPORT_PACKAGE_ACCEPTANCE_REPORT_V1_ID,
    RUNTIME_EXPORT_PACKAGE_HANDOFF_REPORT_V1_ID,
    RUNTIME_EXPORT_PACKAGE_REVIEW_COMPLETION_V1_ID,
    RUNTIME_EXPORT_BENCHMARK_ACCEPTANCE_BINDING_V1_ID,
    RUNTIME_EXPORT_REPRODUCIBILITY_BOUNDARY_V1_ID,
    RUNTIME_EXPORT_ROUTE_COMPARISON_REVIEW_REPORT_PAGE_V1_ID,
    RUNTIME_EXPORT_ROUTE_COMPARISON_REVIEW_REPORT_V1_ID,
    RUNTIME_EXPORT_SCENARIO_REVIEW_BUNDLE_V1_ID,
    RUNTIME_EXPORT_SCENARIO_REVIEW_CHECKLIST_V1_ID,
    RUNTIME_EXPORT_SCENARIO_REVIEW_CHECKLIST_TEMPLATE_COMPARISON_V1_ID,
    RUNTIME_EXPORT_SCENARIO_REVIEW_CHECKLIST_TEMPLATE_V1_ID,
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
    build_runtime_export_network_kpi_formula_evidence_v1,
    build_runtime_export_network_temporal_pressure_evidence_v1,
    build_runtime_export_network_kpi_dynamic_status_v1,
    build_runtime_export_node_network_pressure_summary_v1,
    build_runtime_export_compute_resource_pool_summary_v1,
    build_runtime_export_runtime_kpi_movement_summary_v1,
    build_runtime_export_runtime_closure_readiness_v1,
    build_runtime_export_runtime_dashboard_kpi_v1,
    build_runtime_export_network_flow_lifecycle_summary_v1,
    build_runtime_export_service_lifecycle_stage_summary_v1,
    build_runtime_export_traffic_demand_explanation_v1,
    build_runtime_export_traffic_business_activity_window_v1,
    build_runtime_export_traffic_demand_user_page_v1,
    build_runtime_export_v2_executable_readiness_v1,
    build_runtime_export_user_configuration_template_validation_v1,
    build_runtime_export_user_configuration_control_surface_evidence_v1,
    build_runtime_export_benchmark_acceptance_binding_v1,
    build_runtime_export_package_acceptance_report_v1,
    build_runtime_export_package_audit_index_v1,
    build_runtime_export_package_handoff_report_v1,
    build_runtime_export_package_review_completion_v1,
    build_runtime_export_reproducibility_boundary_v1,
    build_runtime_export_route_comparison_review_report_page_v1,
    build_runtime_export_route_comparison_review_report_v1,
    build_runtime_export_route_detail_item_v1,
    build_runtime_export_route_detail_index_v1,
    build_runtime_export_route_detail_page_v1,
    build_runtime_export_review_summary_v1,
    build_runtime_export_scenario_review_bundle_v1,
    build_runtime_export_scenario_review_checklist_v1,
    build_runtime_export_scenario_review_checklist_template_comparison_v1,
    build_runtime_export_scenario_review_checklist_template_v1,
    build_runtime_export_service_trace_comparison_review_report_page_v1,
    build_runtime_export_service_trace_comparison_review_report_v1,
    build_runtime_export_service_trace_item_v1,
    build_runtime_export_service_trace_page_v1,
    build_runtime_export_user_service_request_page_v1,
    build_runtime_export_user_service_request_summary_v2,
    result_package_contract_v1_to_dict,
    summarize_result_package_record_v1,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
_TRAFFIC_DEMAND_EXPLANATION_FILENAME = "traffic_demand_explanation_v1.json"
_ROUTE_PRESSURE_EVIDENCE_FILENAME = "route_pressure_evidence_v1.json"
_NODE_NETWORK_PRESSURE_SUMMARY_FILENAME = "node_network_pressure_summary_v1.json"
_COMPUTE_RESOURCE_POOL_SUMMARY_FILENAME = "compute_resource_pool_summary_v1.json"
_V2_EXECUTABLE_READINESS_FILENAME = "v2_executable_readiness_v1.json"
_TRAFFIC_BUSINESS_ACTIVITY_WINDOW_FILENAME = (
    "traffic_business_activity_window_v1.json"
)
_RUNTIME_KPI_MOVEMENT_SUMMARY_FILENAME = "runtime_kpi_movement_summary_v1.json"
_RUNTIME_CLOSURE_READINESS_FILENAME = "runtime_closure_readiness_v1.json"
_RUNTIME_DASHBOARD_KPI_FILENAME = "runtime_dashboard_kpi_v1.json"
_NETWORK_FLOW_LIFECYCLE_SUMMARY_FILENAME = "network_flow_lifecycle_summary_v1.json"
_SERVICE_LIFECYCLE_STAGE_SUMMARY_FILENAME = "service_lifecycle_stage_summary_v1.json"
_NETWORK_TEMPORAL_PRESSURE_EVIDENCE_FILENAME = (
    "network_temporal_pressure_evidence_v1.json"
)
_NETWORK_KPI_DYNAMIC_STATUS_FILENAME = "network_kpi_dynamic_status_v1.json"
_BENCHMARK_ACCEPTANCE_BINDING_FILENAME = "benchmark_acceptance_binding_v1.json"
_USER_CONFIGURATION_CONTROL_SURFACE_EVIDENCE_FILENAME = (
    "user_configuration_control_surface_evidence_v1.json"
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
        _ROUTE_PRESSURE_EVIDENCE_FILENAME,
        _NODE_NETWORK_PRESSURE_SUMMARY_FILENAME,
        _COMPUTE_RESOURCE_POOL_SUMMARY_FILENAME,
        _V2_EXECUTABLE_READINESS_FILENAME,
        "review_summary_v1.json",
        "diagnostics_bundle_v1.json",
        "network_kpi_benchmark_validation_v1.json",
        _BENCHMARK_ACCEPTANCE_BINDING_FILENAME,
        "network_kpi_formula_evidence_v1.json",
        _NETWORK_TEMPORAL_PRESSURE_EVIDENCE_FILENAME,
        "network_kpi_variation_explanation_v1.json",
        _NETWORK_KPI_DYNAMIC_STATUS_FILENAME,
        _RUNTIME_KPI_MOVEMENT_SUMMARY_FILENAME,
        _RUNTIME_CLOSURE_READINESS_FILENAME,
        _RUNTIME_DASHBOARD_KPI_FILENAME,
        _NETWORK_FLOW_LIFECYCLE_SUMMARY_FILENAME,
        _SERVICE_LIFECYCLE_STAGE_SUMMARY_FILENAME,
        "user_configuration_template_validation_v1.json",
        _USER_CONFIGURATION_CONTROL_SURFACE_EVIDENCE_FILENAME,
        _TRAFFIC_DEMAND_EXPLANATION_FILENAME,
        _TRAFFIC_BUSINESS_ACTIVITY_WINDOW_FILENAME,
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
        "GET /runtime/export/packages/{package_id}/acceptance-report"
        in first["source_endpoints"]
    )
    assert (
        "GET /runtime/export/packages/{package_id}/user-service-requests"
        in first["source_endpoints"]
    )
    assert (
        "GET /runtime/export/packages/{package_id}/traffic-demand-users"
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
        "GET /runtime/export/packages/{package_id}/scenario-review-checklist-template"
        in first["source_endpoints"]
    )
    assert (
        "GET /runtime/export/packages/{package_id}/scenario-review-checklist-template-comparison"
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
        _ROUTE_PRESSURE_EVIDENCE_FILENAME,
        _NODE_NETWORK_PRESSURE_SUMMARY_FILENAME,
        _COMPUTE_RESOURCE_POOL_SUMMARY_FILENAME,
        _V2_EXECUTABLE_READINESS_FILENAME,
        "review_summary_v1.json",
        "diagnostics_bundle_v1.json",
        "network_kpi_benchmark_validation_v1.json",
        _BENCHMARK_ACCEPTANCE_BINDING_FILENAME,
        "network_kpi_formula_evidence_v1.json",
        _NETWORK_TEMPORAL_PRESSURE_EVIDENCE_FILENAME,
        "network_kpi_variation_explanation_v1.json",
        _NETWORK_KPI_DYNAMIC_STATUS_FILENAME,
        _RUNTIME_KPI_MOVEMENT_SUMMARY_FILENAME,
        _RUNTIME_CLOSURE_READINESS_FILENAME,
        _RUNTIME_DASHBOARD_KPI_FILENAME,
        _NETWORK_FLOW_LIFECYCLE_SUMMARY_FILENAME,
        _SERVICE_LIFECYCLE_STAGE_SUMMARY_FILENAME,
        "user_configuration_template_validation_v1.json",
        _USER_CONFIGURATION_CONTROL_SURFACE_EVIDENCE_FILENAME,
        _TRAFFIC_DEMAND_EXPLANATION_FILENAME,
        _TRAFFIC_BUSINESS_ACTIVITY_WINDOW_FILENAME,
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
            "route_pressure_evidence_v1": _route_pressure_evidence(),
            "node_network_pressure_summary_v1": _node_network_pressure_summary(),
            "compute_resource_pool_summary_v1": _compute_resource_pool_summary(),
            "v2_executable_readiness_v1": _v2_executable_readiness(),
            "traffic_business_activity_window_v1": _traffic_business_activity_window(),
            "runtime_export_route_pressure_evidence_policy_v1": (
                _route_pressure_export_policy()
            ),
            "network_kpi_benchmark_validation_v1": (
                _network_kpi_benchmark_validation()
            ),
            "network_kpi_formula_evidence_v1": _network_kpi_formula_evidence(),
            "network_kpi_provenance_v2": _network_kpi_provenance_v2(),
            "network_kpi_variation_explanation_v1": (
                _network_kpi_variation_explanation()
            ),
            "network_kpi_dynamic_status_v1": _network_kpi_dynamic_status(),
            "runtime_kpi_movement_summary_v1": _runtime_kpi_movement_summary(),
            "runtime_closure_readiness_v1": _runtime_closure_readiness(),
            "runtime_dashboard_kpi_v1": _runtime_dashboard_kpi(),
            "network_flow_lifecycle_summary_v1": _network_flow_lifecycle_summary(),
            "service_lifecycle_stage_summary_v1": (
                _service_lifecycle_stage_summary()
            ),
            "user_service_request_summary_v2": _user_service_request_summary(),
            "runtime_export_user_service_request_policy_v1": (
                _user_service_request_export_policy()
            ),
            "runtime_export_route_detail_policy_v1": _route_detail_export_policy(),
            "runtime_export_service_trace_policy_v1": _service_trace_export_policy(),
        },
        "config": {"seed": 7, "duration_seconds": 120},
        "generated_config": _generated_config(),
        "user_configuration_template_validation_v1": (
            _user_configuration_template_validation()
        ),
        "user_configuration_control_surface_evidence_v1": (
            _user_configuration_control_surface_evidence()
        ),
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
        _BENCHMARK_ACCEPTANCE_BINDING_FILENAME,
        "network_kpi_formula_evidence_v1.json",
        _NETWORK_TEMPORAL_PRESSURE_EVIDENCE_FILENAME,
        "network_kpi_variation_explanation_v1.json",
        _NETWORK_KPI_DYNAMIC_STATUS_FILENAME,
        _RUNTIME_KPI_MOVEMENT_SUMMARY_FILENAME,
        _RUNTIME_CLOSURE_READINESS_FILENAME,
        _RUNTIME_DASHBOARD_KPI_FILENAME,
        _NETWORK_FLOW_LIFECYCLE_SUMMARY_FILENAME,
        _SERVICE_LIFECYCLE_STAGE_SUMMARY_FILENAME,
        "user_configuration_template_validation_v1.json",
        _USER_CONFIGURATION_CONTROL_SURFACE_EVIDENCE_FILENAME,
        _TRAFFIC_DEMAND_EXPLANATION_FILENAME,
        _TRAFFIC_BUSINESS_ACTIVITY_WINDOW_FILENAME,
        "review_summary_v1.json",
        "route_detail_index_v1.json",
        _ROUTE_PRESSURE_EVIDENCE_FILENAME,
        _NODE_NETWORK_PRESSURE_SUMMARY_FILENAME,
        _COMPUTE_RESOURCE_POOL_SUMMARY_FILENAME,
        _V2_EXECUTABLE_READINESS_FILENAME,
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
    assert first["route_pressure_evidence"]["evidence_present"] is True
    assert first["route_pressure_evidence"]["pressure_model"] == (
        "FLOW_PRESSURE_ADMISSION_V1"
    )
    assert first["route_pressure_evidence"]["pressure_admission_rejected_count"] == 1
    assert first["route_pressure_evidence"]["queued_route_count"] == 1
    assert first["route_pressure_evidence"]["saturated_route_count"] == 1
    assert first["route_pressure_evidence"]["pressure_edge_count"] == 2
    assert first["route_pressure_evidence"]["queued_edge_count"] == 1
    assert first["route_pressure_evidence"]["saturated_edge_count"] == 1
    assert first["route_pressure_evidence"]["max_edge_projected_utilization"] == 1.25
    assert first["route_pressure_evidence"]["packet_level_simulation"] is False
    assert first["route_pressure_evidence"]["event_replay"] is False
    assert first["node_network_pressure_summary"]["evidence_present"] is True
    assert first["node_network_pressure_summary"]["node_count"] == 3
    assert first["node_network_pressure_summary"]["pressure_edge_count"] == 4
    assert first["node_network_pressure_summary"]["frontend_inference_required"] is False
    assert first["compute_resource_pool_summary"]["evidence_present"] is True
    assert first["compute_resource_pool_summary"]["summary_hash"] == (
        "sha256:compute-pool"
    )
    assert first["compute_resource_pool_summary"]["node_count"] == 2
    assert first["compute_resource_pool_summary"]["dimension_count"] == 7
    assert first["compute_resource_pool_summary"]["saturated_dimension_count"] == 1
    assert first["compute_resource_pool_summary"]["frontend_inference_required"] is False
    assert first["compute_resource_pool_summary"]["evidence_hash"].startswith(
        "sha256:"
    )
    assert first["network_kpi_benchmark_validation"]["evidence_present"] is True
    assert first["network_kpi_benchmark_validation"]["validation_status"] == "PASS"
    assert first["network_kpi_benchmark_validation"]["failed_check_count"] == 0
    assert first["network_kpi_formula_evidence"]["evidence_present"] is True
    assert first["network_kpi_formula_evidence"]["formula_evidence_status"] == (
        "FORMULA_AND_TIME_EVIDENCE_READY"
    )
    assert first["network_kpi_formula_evidence"]["missing_selected_input_count"] == 0
    assert first["network_temporal_pressure_evidence"]["evidence_present"] is True
    assert first["network_temporal_pressure_evidence"]["status"] == "OBSERVED"
    assert first["network_temporal_pressure_evidence"]["time_pressure_factor"] == 0.85
    assert first["network_temporal_pressure_evidence"]["loss_proxy_rate"] == 0.07
    assert first["network_kpi_dynamic_status"]["evidence_present"] is True
    assert first["network_kpi_dynamic_status"]["dynamic_status"] == "DYNAMIC"
    assert first["network_kpi_dynamic_status"]["time_varying_kpi_count"] == 1
    assert first["runtime_kpi_movement_summary"]["evidence_present"] is True
    assert first["runtime_kpi_movement_summary"]["movement_status"] == (
        "TIME_VARYING_OBSERVED"
    )
    assert first["runtime_kpi_movement_summary"]["moving_metric_count"] == 3
    assert first["runtime_closure_readiness"]["evidence_present"] is True
    assert first["runtime_closure_readiness"]["closure_status"] == "RESULT_READY"
    assert first["runtime_closure_readiness"]["result_ready"] is True
    assert first["runtime_dashboard_kpi"]["evidence_present"] is True
    assert first["runtime_dashboard_kpi"]["metric_count"] == 5
    assert first["runtime_dashboard_kpi"]["time_varying_metric_count"] == 3
    assert first["network_flow_lifecycle_summary"]["evidence_present"] is True
    assert first["network_flow_lifecycle_summary"]["active_flow_count"] == 2
    assert first["service_lifecycle_stage_summary"]["evidence_present"] is True
    assert first["service_lifecycle_stage_summary"]["service_count"] == 2
    assert first["service_lifecycle_stage_summary"]["observed_stage_count"] == 5
    assert first["service_lifecycle_stage_summary"]["dominant_stage_kind"] == (
        "COMPUTE_EXECUTION"
    )
    assert first["user_configuration_template_validation"][
        "evidence_present"
    ] is True
    assert first["user_configuration_template_validation"]["validation_status"] == (
        "ALL_TEMPLATES_VALID"
    )
    assert first["user_configuration_template_validation"][
        "invalid_template_count"
    ] == 0
    assert first["user_configuration_control_surface_evidence"][
        "evidence_present"
    ] is True
    assert first["user_configuration_control_surface_evidence"][
        "coverage_status"
    ] == "COMPLETE"
    assert first["user_configuration_control_surface_evidence"][
        "key_field_count"
    ] == 2
    assert first["traffic_demand_explanation"]["evidence_present"] is True
    assert first["traffic_demand_explanation"]["request_count"] == 2
    assert first["traffic_demand_explanation"]["compute_service_request_count"] == 1
    assert first["traffic_demand_explanation"]["frontend_inference_required"] is False
    assert first["traffic_demand_explanation"]["packet_level_simulation"] is False
    assert first["user_service_requests"]["evidence_present"] is True
    assert first["user_service_requests"]["request_count"] == 2
    assert first["user_service_requests"]["exported_request_count"] == 2
    assert first["user_service_requests"]["hidden_request_count"] == 0
    assert first["artifacts"][
        "network_kpi_benchmark_validation_exported"
    ] is True
    assert first["artifacts"]["benchmark_acceptance_binding_exported"] is True
    assert first["artifacts"]["network_kpi_formula_evidence_exported"] is True
    assert first["artifacts"][
        "network_temporal_pressure_evidence_exported"
    ] is True
    assert first["artifacts"]["network_kpi_dynamic_status_exported"] is True
    assert first["artifacts"]["runtime_kpi_movement_summary_exported"] is True
    assert first["artifacts"]["runtime_closure_readiness_exported"] is True
    assert first["artifacts"]["runtime_dashboard_kpi_exported"] is True
    assert first["artifacts"]["network_flow_lifecycle_summary_exported"] is True
    assert first["artifacts"]["service_lifecycle_stage_summary_exported"] is True
    assert first["artifacts"][
        "user_configuration_template_validation_exported"
    ] is True
    assert first["artifacts"][
        "user_configuration_control_surface_evidence_exported"
    ] is True
    assert first["artifacts"]["traffic_demand_explanation_exported"] is True
    assert first["artifacts"]["route_pressure_evidence_exported"] is True
    assert first["artifacts"]["node_network_pressure_summary_exported"] is True
    assert first["artifacts"]["compute_resource_pool_summary_exported"] is True
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
        "generated_config": _generated_config(),
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


def test_runtime_export_network_kpi_formula_evidence_v1_is_deterministic() -> None:
    config_snapshot = {
        "type": "RUNTIME_CONFIG_SNAPSHOT",
        "status": {
            "network_kpi_formula_evidence_v1": _network_kpi_formula_evidence(),
            "network_kpi_provenance_v2": _network_kpi_provenance_v2(),
        },
        "config": {"seed": 7},
        "generated_config": _generated_config(),
    }

    first = build_runtime_export_network_kpi_formula_evidence_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        config_snapshot=config_snapshot,
    )
    second = build_runtime_export_network_kpi_formula_evidence_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        config_snapshot=dict(reversed(tuple(config_snapshot.items()))),
    )

    assert first == second
    assert first["artifact_id"] == RUNTIME_EXPORT_NETWORK_KPI_FORMULA_EVIDENCE_V1_ID
    assert first["runtime_status_field"] == "network_kpi_formula_evidence_v1"
    assert first["formula_evidence"]["formula_evidence_status"] == (
        "FORMULA_AND_TIME_EVIDENCE_READY"
    )
    assert first["evidence"]["evidence_present"] is True
    assert first["evidence"]["formula_evidence_status"] == (
        "FORMULA_AND_TIME_EVIDENCE_READY"
    )
    assert first["evidence"]["acceptable_for_demo_review"] is True
    assert first["evidence"]["evidence_hash"].startswith("sha256:")
    assert first["artifact_hash"].startswith("sha256:")
    assert "NO_METRIC_RECOMPUTE" in first["boundary_conditions"]


def test_runtime_export_network_temporal_pressure_evidence_v1_is_deterministic() -> None:
    temporal_pressure = _network_kpi_provenance_v2()["temporal_pressure_evidence"]
    config_snapshot = {
        "type": "RUNTIME_CONFIG_SNAPSHOT",
        "status": {
            "network_kpi_provenance_v2": _network_kpi_provenance_v2(),
        },
        "config": {"seed": 7},
        "generated_config": _generated_config(),
    }

    first = build_runtime_export_network_temporal_pressure_evidence_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        config_snapshot=config_snapshot,
    )
    second = build_runtime_export_network_temporal_pressure_evidence_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        config_snapshot=dict(reversed(tuple(config_snapshot.items()))),
    )

    assert first == second
    assert first["artifact_id"] == (
        RUNTIME_EXPORT_NETWORK_TEMPORAL_PRESSURE_EVIDENCE_V1_ID
    )
    assert first["runtime_status_field"] == (
        "network_kpi_provenance_v2.temporal_pressure_evidence"
    )
    assert first["temporal_pressure_evidence"] == temporal_pressure
    assert first["evidence"]["evidence_present"] is True
    assert first["evidence"]["status"] == "OBSERVED"
    assert first["evidence"]["temporal_pressure_model"] == (
        "DETERMINISTIC_TRIANGULAR_LOAD_GATED_PROXY"
    )
    assert first["evidence"]["time_pressure_factor"] == 0.85
    assert first["evidence"]["loss_proxy_rate"] == 0.07
    assert first["evidence"]["packet_level_simulation"] is False
    assert first["evidence"]["frontend_inference_required"] is False
    assert first["evidence"]["acceptable_for_demo_review"] is True
    assert first["evidence"]["evidence_hash"].startswith("sha256:")
    assert first["artifact_hash"].startswith("sha256:")
    assert "NO_METRIC_RECOMPUTE" in first["boundary_conditions"]


def test_runtime_export_network_kpi_dynamic_status_v1_is_deterministic() -> None:
    config_snapshot = {
        "type": "RUNTIME_CONFIG_SNAPSHOT",
        "status": {
            "network_kpi_dynamic_status_v1": _network_kpi_dynamic_status(),
        },
        "config": {"seed": 7},
        "generated_config": _generated_config(),
    }

    first = build_runtime_export_network_kpi_dynamic_status_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        config_snapshot=config_snapshot,
    )
    second = build_runtime_export_network_kpi_dynamic_status_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        config_snapshot=dict(reversed(tuple(config_snapshot.items()))),
    )

    assert first == second
    assert first["type"] == "RUNTIME_EXPORT_NETWORK_KPI_DYNAMIC_STATUS_V1"
    assert first["artifact_id"] == RUNTIME_EXPORT_NETWORK_KPI_DYNAMIC_STATUS_V1_ID
    assert first["runtime_status_field"] == "network_kpi_dynamic_status_v1"
    assert first["dynamic_status"] == _network_kpi_dynamic_status()
    assert first["evidence"]["evidence_present"] is True
    assert first["evidence"]["dynamic_status"] == "DYNAMIC"
    assert first["evidence"]["time_varying_kpi_count"] == 1
    assert first["evidence"]["flat_kpi_count"] == 1
    assert first["evidence"]["packet_level_simulation"] is False
    assert first["evidence"]["frontend_inference_required"] is False
    assert first["evidence"]["acceptable_for_demo_review"] is True
    assert first["evidence"]["evidence_hash"].startswith("sha256:")
    assert first["artifact_hash"].startswith("sha256:")
    assert "NO_METRIC_RECOMPUTE" in first["boundary_conditions"]


def test_runtime_export_runtime_kpi_movement_summary_v1_is_deterministic() -> None:
    config_snapshot = {
        "status": {
            "runtime_kpi_movement_summary_v1": _runtime_kpi_movement_summary(),
        }
    }

    first = build_runtime_export_runtime_kpi_movement_summary_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        config_snapshot=config_snapshot,
    )
    second = build_runtime_export_runtime_kpi_movement_summary_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        config_snapshot=config_snapshot,
    )

    assert first == second
    assert first["type"] == "RUNTIME_EXPORT_RUNTIME_KPI_MOVEMENT_SUMMARY_V1"
    assert first["artifact_id"] == RUNTIME_EXPORT_RUNTIME_KPI_MOVEMENT_SUMMARY_V1_ID
    assert first["runtime_status_field"] == "runtime_kpi_movement_summary_v1"
    assert first["movement_summary"] == _runtime_kpi_movement_summary()
    assert first["evidence"]["evidence_present"] is True
    assert first["evidence"]["movement_status"] == "TIME_VARYING_OBSERVED"
    assert "NO_METRIC_RECOMPUTE" in first["boundary_conditions"]
    assert first["artifact_hash"].startswith("sha256:")


def test_runtime_export_runtime_closure_readiness_v1_is_deterministic() -> None:
    config_snapshot = {
        "status": {
            "runtime_closure_readiness_v1": _runtime_closure_readiness(),
        }
    }

    first = build_runtime_export_runtime_closure_readiness_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        config_snapshot=config_snapshot,
    )
    second = build_runtime_export_runtime_closure_readiness_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        config_snapshot=config_snapshot,
    )

    assert first == second
    assert first["type"] == "RUNTIME_EXPORT_RUNTIME_CLOSURE_READINESS_V1"
    assert first["artifact_id"] == RUNTIME_EXPORT_RUNTIME_CLOSURE_READINESS_V1_ID
    assert first["source"] == "BACKEND_RUNTIME_STATUS"
    assert first["runtime_status_field"] == "runtime_closure_readiness_v1"
    assert first["closure_readiness"] == _runtime_closure_readiness()
    assert first["evidence"]["evidence_present"] is True
    assert first["evidence"]["closure_status"] == "RESULT_READY"
    assert first["evidence"]["result_ready"] is True
    assert first["evidence"]["failed_gate_count"] == 0
    assert first["evidence"]["packet_level_simulation"] is False
    assert first["evidence"]["frontend_inference_required"] is False
    assert first["evidence"]["acceptable_for_demo_review"] is True
    assert "NO_CLOSURE_RECOMPUTE" in first["boundary_conditions"]
    assert first["artifact_hash"].startswith("sha256:")


def test_runtime_export_runtime_dashboard_kpi_v1_is_deterministic() -> None:
    config_snapshot = {
        "status": {
            "runtime_dashboard_kpi_v1": _runtime_dashboard_kpi(),
        }
    }

    first = build_runtime_export_runtime_dashboard_kpi_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        config_snapshot=config_snapshot,
    )
    second = build_runtime_export_runtime_dashboard_kpi_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        config_snapshot=config_snapshot,
    )

    assert first == second
    assert first["type"] == "RUNTIME_EXPORT_RUNTIME_DASHBOARD_KPI_V1"
    assert first["artifact_id"] == RUNTIME_EXPORT_RUNTIME_DASHBOARD_KPI_V1_ID
    assert first["source"] == "BACKEND_RUNTIME_STATUS"
    assert first["runtime_status_field"] == "runtime_dashboard_kpi_v1"
    assert first["dashboard_kpi"] == _runtime_dashboard_kpi()
    assert first["evidence"]["evidence_present"] is True
    assert first["evidence"]["metric_model"] == "FLOW_LEVEL_PROXY"
    assert first["evidence"]["metric_count"] == 5
    assert first["evidence"]["time_varying_metric_count"] == 3
    assert first["evidence"]["packet_level_simulation"] is False
    assert first["evidence"]["frontend_inference_required"] is False
    assert first["evidence"]["acceptable_for_demo_review"] is True
    assert "NO_DASHBOARD_KPI_RECOMPUTE" in first["boundary_conditions"]
    assert first["artifact_hash"].startswith("sha256:")


def test_runtime_export_network_flow_lifecycle_summary_v1_is_deterministic() -> None:
    config_snapshot = {
        "status": {
            "network_flow_lifecycle_summary_v1": _network_flow_lifecycle_summary(),
        }
    }

    first = build_runtime_export_network_flow_lifecycle_summary_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        config_snapshot=config_snapshot,
    )
    second = build_runtime_export_network_flow_lifecycle_summary_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        config_snapshot=config_snapshot,
    )

    assert first == second
    assert first["type"] == "RUNTIME_EXPORT_NETWORK_FLOW_LIFECYCLE_SUMMARY_V1"
    assert first["artifact_id"] == RUNTIME_EXPORT_NETWORK_FLOW_LIFECYCLE_SUMMARY_V1_ID
    assert first["runtime_status_field"] == "network_flow_lifecycle_summary_v1"
    assert first["summary"] == _network_flow_lifecycle_summary()
    assert first["evidence"]["evidence_present"] is True
    assert first["evidence"]["lifecycle_status"] == "ACTIVE"
    assert first["evidence"]["active_flow_count"] == 2
    assert first["evidence"]["completed_flow_count"] == 1
    assert first["evidence"]["frontend_inference_required"] is False
    assert first["evidence"]["acceptable_for_demo_review"] is True
    assert "NO_FLOW_LIFECYCLE_RECOMPUTE" in first["boundary_conditions"]
    assert first["artifact_hash"].startswith("sha256:")


def test_runtime_export_service_lifecycle_stage_summary_v1_is_deterministic() -> None:
    config_snapshot = {
        "status": {
            "service_lifecycle_stage_summary_v1": (
                _service_lifecycle_stage_summary()
            ),
        }
    }

    first = build_runtime_export_service_lifecycle_stage_summary_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        config_snapshot=config_snapshot,
    )
    second = build_runtime_export_service_lifecycle_stage_summary_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        config_snapshot=config_snapshot,
    )

    assert first == second
    assert first["type"] == "RUNTIME_EXPORT_SERVICE_LIFECYCLE_STAGE_SUMMARY_V1"
    assert first["artifact_id"] == RUNTIME_EXPORT_SERVICE_LIFECYCLE_STAGE_SUMMARY_V1_ID
    assert first["runtime_status_field"] == "service_lifecycle_stage_summary_v1"
    assert first["stage_summary"] == _service_lifecycle_stage_summary()
    assert first["evidence"]["evidence_present"] is True
    assert first["evidence"]["service_count"] == 2
    assert first["evidence"]["observed_stage_count"] == 5
    assert first["evidence"]["pending_stage_count"] == 3
    assert first["evidence"]["dominant_stage_kind"] == "COMPUTE_EXECUTION"
    assert first["evidence"]["frontend_inference_required"] is False
    assert first["evidence"]["acceptable_for_demo_review"] is True
    assert "NO_SERVICE_LIFECYCLE_RECOMPUTE" in first["boundary_conditions"]
    assert first["artifact_hash"].startswith("sha256:")


def test_runtime_export_compute_resource_pool_summary_v1_is_deterministic() -> None:
    config_snapshot = {
        "status": {
            "compute_resource_pool_summary_v1": _compute_resource_pool_summary(),
        }
    }

    first = build_runtime_export_compute_resource_pool_summary_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        config_snapshot=config_snapshot,
    )
    second = build_runtime_export_compute_resource_pool_summary_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        config_snapshot=config_snapshot,
    )

    assert first == second
    assert first["type"] == "RUNTIME_EXPORT_COMPUTE_RESOURCE_POOL_SUMMARY_V1"
    assert first["artifact_id"] == RUNTIME_EXPORT_COMPUTE_RESOURCE_POOL_SUMMARY_V1_ID
    assert first["source"] == "BACKEND_RUNTIME_STATUS"
    assert first["runtime_status_field"] == "compute_resource_pool_summary_v1"
    assert first["compute_resource_pool_summary"] == _compute_resource_pool_summary()
    assert first["evidence"]["evidence_present"] is True
    assert first["evidence"]["summary_hash"] == "sha256:compute-pool"
    assert first["evidence"]["node_count"] == 2
    assert first["evidence"]["dimension_count"] == 7
    assert first["evidence"]["saturated_dimension_count"] == 1
    assert first["evidence"]["packet_level_simulation"] is False
    assert first["evidence"]["frontend_inference_required"] is False
    assert first["evidence"]["acceptable_for_demo_review"] is True
    assert first["evidence"]["evidence_hash"].startswith("sha256:")
    assert "NO_COMPUTE_RESOURCE_RECOMPUTE" in first["boundary_conditions"]
    assert first["artifact_hash"].startswith("sha256:")


def test_runtime_export_v2_executable_readiness_v1_is_deterministic() -> None:
    config_snapshot = {
        "status": {
            "v2_executable_readiness_v1": _v2_executable_readiness(),
        }
    }

    first = build_runtime_export_v2_executable_readiness_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        config_snapshot=config_snapshot,
    )
    second = build_runtime_export_v2_executable_readiness_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        config_snapshot=config_snapshot,
    )

    assert first == second
    assert first["type"] == "RUNTIME_EXPORT_V2_EXECUTABLE_READINESS_V1"
    assert first["artifact_id"] == RUNTIME_EXPORT_V2_EXECUTABLE_READINESS_V1_ID
    assert first["source"] == "BACKEND_RUNTIME_STATUS"
    assert first["runtime_status_field"] == "v2_executable_readiness_v1"
    assert first["readiness"] == _v2_executable_readiness()
    assert first["evidence"]["evidence_present"] is True
    assert first["evidence"]["executable_ready"] is True
    assert first["evidence"]["failed_gate_count"] == 0
    assert first["evidence"]["packet_level_simulation"] is False
    assert first["evidence"]["frontend_inference_required"] is False
    assert first["evidence"]["acceptable_for_demo_review"] is True
    assert "NO_READINESS_RECOMPUTE" in first["boundary_conditions"]
    assert first["artifact_hash"].startswith("sha256:")


def test_runtime_export_traffic_business_activity_window_v1_is_deterministic() -> None:
    config_snapshot = {
        "status": {
            "traffic_business_activity_window_v1": (
                _traffic_business_activity_window()
            ),
        }
    }

    first = build_runtime_export_traffic_business_activity_window_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        config_snapshot=config_snapshot,
    )
    second = build_runtime_export_traffic_business_activity_window_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        config_snapshot=config_snapshot,
    )

    assert first == second
    assert first["type"] == "RUNTIME_EXPORT_TRAFFIC_BUSINESS_ACTIVITY_WINDOW_V1"
    assert first["artifact_id"] == (
        RUNTIME_EXPORT_TRAFFIC_BUSINESS_ACTIVITY_WINDOW_V1_ID
    )
    assert first["source"] == "BACKEND_RUNTIME_STATUS"
    assert first["runtime_status_field"] == "traffic_business_activity_window_v1"
    assert first["activity_window"] == _traffic_business_activity_window()
    assert first["evidence"]["evidence_present"] is True
    assert first["evidence"]["request_count"] == 2
    assert first["evidence"]["active_user_count"] == 1
    assert first["evidence"]["pending_user_count"] == 1
    assert first["evidence"]["artifact_window_only"] is True
    assert first["evidence"]["packet_level_simulation"] is False
    assert first["evidence"]["frontend_inference_required"] is False
    assert first["evidence"]["acceptable_for_demo_review"] is True
    assert "NO_TRAFFIC_REGENERATION" in first["boundary_conditions"]
    assert first["artifact_hash"].startswith("sha256:")


def test_runtime_export_node_network_pressure_summary_v1_is_deterministic() -> None:
    config_snapshot = {
        "status": {
            "node_network_pressure_summary_v1": _node_network_pressure_summary(),
            "compute_resource_pool_summary_v1": _compute_resource_pool_summary(),
        }
    }

    first = build_runtime_export_node_network_pressure_summary_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        config_snapshot=config_snapshot,
    )
    second = build_runtime_export_node_network_pressure_summary_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        config_snapshot=config_snapshot,
    )

    assert first == second
    assert first["type"] == "RUNTIME_EXPORT_NODE_NETWORK_PRESSURE_SUMMARY_V1"
    assert first["artifact_id"] == RUNTIME_EXPORT_NODE_NETWORK_PRESSURE_SUMMARY_V1_ID
    assert first["runtime_status_field"] == "node_network_pressure_summary_v1"
    assert first["summary"] == _node_network_pressure_summary()
    assert first["evidence"]["evidence_present"] is True
    assert first["evidence"]["pressure_model"] == "FLOW_PRESSURE_ADMISSION_V1"
    assert first["evidence"]["node_count"] == 3
    assert first["evidence"]["pressure_edge_count"] == 4
    assert first["evidence"]["frontend_inference_required"] is False
    assert first["evidence"]["acceptable_for_demo_review"] is True
    assert "NO_NODE_PRESSURE_RECOMPUTE" in first["boundary_conditions"]
    assert first["artifact_hash"].startswith("sha256:")


def test_runtime_export_user_configuration_template_validation_v1_is_deterministic() -> None:
    config_snapshot = {
        "type": "RUNTIME_CONFIG_SNAPSHOT",
        "status": {},
        "config": {"seed": 7},
        "generated_config": {"seed": 7, "satellite_count": 72},
        "user_configuration_template_validation_v1": (
            _user_configuration_template_validation()
        ),
        "user_configuration_control_surface_evidence_v1": (
            _user_configuration_control_surface_evidence()
        ),
    }

    first = build_runtime_export_user_configuration_template_validation_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        config_snapshot=config_snapshot,
    )
    second = build_runtime_export_user_configuration_template_validation_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        config_snapshot=dict(reversed(tuple(config_snapshot.items()))),
    )

    assert first == second
    assert first["artifact_id"] == (
        RUNTIME_EXPORT_USER_CONFIGURATION_TEMPLATE_VALIDATION_V1_ID
    )
    assert (
        first["config_snapshot_field"] == "user_configuration_template_validation_v1"
    )
    assert first["template_validation"] == config_snapshot[
        "user_configuration_template_validation_v1"
    ]
    assert first["evidence"]["evidence_present"] is True
    assert first["evidence"]["validation_status"] == "ALL_TEMPLATES_VALID"
    assert first["evidence"]["template_count"] == 2
    assert first["evidence"]["invalid_template_count"] == 0
    assert first["evidence"]["packet_level_simulation"] is False
    assert first["evidence"]["external_simulators"] is False
    assert first["evidence"]["acceptable_for_demo_review"] is True
    assert first["evidence"]["evidence_hash"].startswith("sha256:")
    assert first["artifact_hash"].startswith("sha256:")
    assert "NO_TEMPLATE_RELOAD" in first["boundary_conditions"]


def test_runtime_export_user_configuration_control_surface_evidence_v1_is_deterministic() -> None:
    config_snapshot = {
        "type": "RUNTIME_CONFIG_SNAPSHOT",
        "status": {},
        "config": {"seed": 7},
        "generated_config": {"seed": 7, "satellite_count": 72},
        "user_configuration_control_surface_evidence_v1": (
            _user_configuration_control_surface_evidence()
        ),
    }

    first = build_runtime_export_user_configuration_control_surface_evidence_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        config_snapshot=config_snapshot,
    )
    second = build_runtime_export_user_configuration_control_surface_evidence_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        config_snapshot=dict(reversed(tuple(config_snapshot.items()))),
    )

    assert first == second
    assert first["artifact_id"] == (
        RUNTIME_EXPORT_USER_CONFIGURATION_CONTROL_SURFACE_EVIDENCE_V1_ID
    )
    assert first["config_snapshot_field"] == (
        "user_configuration_control_surface_evidence_v1"
    )
    assert first["control_surface_evidence"] == config_snapshot[
        "user_configuration_control_surface_evidence_v1"
    ]
    assert first["evidence"]["evidence_present"] is True
    assert first["evidence"]["coverage_status"] == "COMPLETE"
    assert first["evidence"]["key_field_count"] == 2
    assert first["evidence"]["missing_key_count"] == 0
    assert first["evidence"]["wrong_surface_count"] == 0
    assert first["evidence"]["packet_level_simulation"] is False
    assert first["evidence"]["external_simulators"] is False
    assert first["evidence"]["acceptable_for_demo_review"] is True
    assert first["evidence"]["evidence_hash"].startswith("sha256:")
    assert first["artifact_hash"].startswith("sha256:")
    assert "NO_CONFIG_RECOMPUTE" in first["boundary_conditions"]


def test_runtime_export_traffic_demand_explanation_v1_is_deterministic() -> None:
    config_snapshot = {
        "type": "RUNTIME_CONFIG_SNAPSHOT",
        "status": {},
        "config": {"seed": 7},
        "generated_config": _generated_config(),
    }

    first = build_runtime_export_traffic_demand_explanation_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        config_snapshot=config_snapshot,
    )
    second = build_runtime_export_traffic_demand_explanation_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        config_snapshot=dict(reversed(tuple(config_snapshot.items()))),
    )

    assert first == second
    assert first["artifact_id"] == RUNTIME_EXPORT_TRAFFIC_DEMAND_EXPLANATION_V1_ID
    assert first["config_snapshot_field"] == (
        "generated_config.backend_summary.traffic_demand_explanation_v1"
    )
    assert first["traffic_demand_explanation"] == _traffic_demand_explanation()
    assert first["evidence"]["evidence_present"] is True
    assert first["evidence"]["request_count"] == 2
    assert first["evidence"]["configured_request_count"] == 2
    assert first["evidence"]["explained_request_count"] == 2
    assert first["evidence"]["compute_service_request_count"] == 1
    assert first["evidence"]["communication_only_request_count"] == 1
    assert first["evidence"]["active_traffic_classes"] == (
        "DATA_TRANSFER",
        "COMPUTE_SERVICE",
    )
    assert first["evidence"]["frontend_inference_required"] is False
    assert first["evidence"]["packet_level_simulation"] is False
    assert first["evidence"]["acceptable_for_demo_review"] is True
    assert first["evidence"]["evidence_hash"].startswith("sha256:")
    assert first["artifact_hash"].startswith("sha256:")
    assert "NO_TRAFFIC_REGENERATION" in first["boundary_conditions"]


def test_runtime_export_traffic_demand_user_page_v1_is_deterministic() -> None:
    traffic_demand_export = build_runtime_export_traffic_demand_explanation_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        config_snapshot={
            "type": "RUNTIME_CONFIG_SNAPSHOT",
            "status": {},
            "config": {"seed": 7},
            "generated_config": _generated_config(),
        },
    )

    first = build_runtime_export_traffic_demand_user_page_v1(
        traffic_demand_export,
        package_id="pkg-1",
        cursor=0,
        limit=1,
        traffic_class="COMPUTE_SERVICE",
    )
    second = build_runtime_export_traffic_demand_user_page_v1(
        dict(reversed(tuple(traffic_demand_export.items()))),
        package_id="pkg-1",
        cursor=0,
        limit=1,
        traffic_class="COMPUTE_SERVICE",
    )
    query_page = build_runtime_export_traffic_demand_user_page_v1(
        traffic_demand_export,
        package_id="pkg-1",
        cursor=0,
        limit=5,
        query="flow-data",
    )

    assert first == second
    assert first["page_id"] == RUNTIME_EXPORT_TRAFFIC_DEMAND_USER_PAGE_V1_ID
    assert first["type"] == "RUNTIME_EXPORT_TRAFFIC_DEMAND_USER_PAGE_V1"
    assert first["package_id"] == "pkg-1"
    assert first["artifact_hash"] == traffic_demand_export["artifact_hash"]
    assert first["filters"] == {
        "query": "",
        "traffic_class": "COMPUTE_SERVICE",
    }
    assert first["filter_applied"] is True
    assert first["unfiltered_user_count"] == 2
    assert first["user_count"] == 1
    assert first["item_count"] == 1
    assert first["request_count"] == 1
    assert first["compute_service_user_count"] == 1
    assert first["communication_service_user_count"] == 0
    assert first["items"][0]["user_id"] == "user-00000"
    assert first["items"][0]["service_classes"] == ("COMPUTE_SERVICE",)
    assert first["page_hash"].startswith("sha256:")
    assert "NO_TRAFFIC_REGENERATION" in first["boundary_conditions"]
    assert query_page["filters"] == {
        "query": "flow-data",
        "traffic_class": "ALL",
    }
    assert query_page["items"][0]["user_id"] == "user-00001"


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
            "route_pressure_evidence_v1": _route_pressure_evidence(),
            "node_network_pressure_summary_v1": _node_network_pressure_summary(),
            "compute_resource_pool_summary_v1": _compute_resource_pool_summary(),
            "v2_executable_readiness_v1": _v2_executable_readiness(),
            "traffic_business_activity_window_v1": _traffic_business_activity_window(),
            "runtime_export_route_pressure_evidence_policy_v1": (
                _route_pressure_export_policy()
            ),
            "network_kpi_benchmark_validation_v1": (
                _network_kpi_benchmark_validation()
            ),
            "network_kpi_formula_evidence_v1": _network_kpi_formula_evidence(),
            "network_kpi_provenance_v2": _network_kpi_provenance_v2(),
            "network_kpi_variation_explanation_v1": (
                _network_kpi_variation_explanation()
            ),
            "network_kpi_dynamic_status_v1": _network_kpi_dynamic_status(),
            "runtime_kpi_movement_summary_v1": _runtime_kpi_movement_summary(),
            "runtime_closure_readiness_v1": _runtime_closure_readiness(),
            "runtime_dashboard_kpi_v1": _runtime_dashboard_kpi(),
            "network_flow_lifecycle_summary_v1": _network_flow_lifecycle_summary(),
            "service_lifecycle_stage_summary_v1": (
                _service_lifecycle_stage_summary()
            ),
            "user_service_request_summary_v2": _user_service_request_summary(),
            "runtime_export_user_service_request_policy_v1": (
                _user_service_request_export_policy()
            ),
            "runtime_export_route_detail_policy_v1": _route_detail_export_policy(),
            "runtime_export_service_trace_policy_v1": _service_trace_export_policy(),
        },
        "config": {"seed": 7, "duration_seconds": 120},
        "generated_config": _generated_config(),
        "user_configuration_template_validation_v1": (
            _user_configuration_template_validation()
        ),
        "user_configuration_control_surface_evidence_v1": (
            _user_configuration_control_surface_evidence()
        ),
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
        _BENCHMARK_ACCEPTANCE_BINDING_FILENAME,
        "network_kpi_formula_evidence_v1.json",
        _NETWORK_TEMPORAL_PRESSURE_EVIDENCE_FILENAME,
        "network_kpi_variation_explanation_v1.json",
        _NETWORK_KPI_DYNAMIC_STATUS_FILENAME,
        _RUNTIME_KPI_MOVEMENT_SUMMARY_FILENAME,
        _RUNTIME_CLOSURE_READINESS_FILENAME,
        _RUNTIME_DASHBOARD_KPI_FILENAME,
        _NETWORK_FLOW_LIFECYCLE_SUMMARY_FILENAME,
        _SERVICE_LIFECYCLE_STAGE_SUMMARY_FILENAME,
        "user_configuration_template_validation_v1.json",
        _USER_CONFIGURATION_CONTROL_SURFACE_EVIDENCE_FILENAME,
        _TRAFFIC_DEMAND_EXPLANATION_FILENAME,
        _TRAFFIC_BUSINESS_ACTIVITY_WINDOW_FILENAME,
        "review_summary_v1.json",
        "route_detail_index_v1.json",
        _ROUTE_PRESSURE_EVIDENCE_FILENAME,
        _NODE_NETWORK_PRESSURE_SUMMARY_FILENAME,
        _COMPUTE_RESOURCE_POOL_SUMMARY_FILENAME,
        _V2_EXECUTABLE_READINESS_FILENAME,
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
    assert first["route_pressure_evidence"]["evidence_present"] is True
    assert first["route_pressure_evidence"]["route_count"] == 2
    assert first["route_pressure_evidence"]["pressure_admission_rejected_count"] == 1
    assert first["route_pressure_evidence"]["pressure_edge_count"] == 2
    assert first["route_pressure_evidence"]["max_edge_projected_utilization"] == 1.25
    assert first["route_pressure_evidence"]["acceptable_for_demo_review"] is True
    assert first["node_network_pressure_summary"]["evidence_present"] is True
    assert first["node_network_pressure_summary"]["node_count"] == 3
    assert first["node_network_pressure_summary"]["pressure_edge_count"] == 4
    assert first["compute_resource_pool_summary"]["evidence_present"] is True
    assert first["compute_resource_pool_summary"]["node_count"] == 2
    assert first["compute_resource_pool_summary"]["dimension_count"] == 7
    assert first["compute_resource_pool_summary"]["acceptable_for_demo_review"] is True
    assert first["compute_resource_pool_summary"]["evidence_hash"] == (
        review_summary["compute_resource_pool_summary"]["evidence_hash"]
    )
    assert first["network_kpi_benchmark_validation"]["evidence_present"] is True
    assert first["network_kpi_benchmark_validation"]["validation_status"] == "PASS"
    assert first["network_kpi_benchmark_validation"]["failed_check_count"] == 0
    assert first["network_kpi_formula_evidence"]["evidence_present"] is True
    assert first["network_kpi_formula_evidence"]["formula_evidence_status"] == (
        "FORMULA_AND_TIME_EVIDENCE_READY"
    )
    assert first["network_kpi_formula_evidence"]["acceptable_for_demo_review"] is True
    assert first["network_temporal_pressure_evidence"]["evidence_present"] is True
    assert first["network_temporal_pressure_evidence"]["status"] == "OBSERVED"
    assert first["network_temporal_pressure_evidence"][
        "acceptable_for_demo_review"
    ] is True
    assert first["network_kpi_dynamic_status"]["evidence_present"] is True
    assert first["network_kpi_dynamic_status"]["dynamic_status"] == "DYNAMIC"
    assert first["network_kpi_dynamic_status"]["acceptable_for_demo_review"] is True
    assert first["runtime_kpi_movement_summary"]["evidence_present"] is True
    assert first["runtime_closure_readiness"]["evidence_present"] is True
    assert first["runtime_closure_readiness"]["closure_status"] == "RESULT_READY"
    assert first["runtime_closure_readiness"]["result_ready"] is True
    assert first["runtime_dashboard_kpi"]["evidence_present"] is True
    assert first["runtime_dashboard_kpi"]["metric_count"] == 5
    assert first["runtime_dashboard_kpi"]["time_varying_metric_count"] == 3
    assert first["network_flow_lifecycle_summary"]["evidence_present"] is True
    assert first["service_lifecycle_stage_summary"]["evidence_present"] is True
    assert first["service_lifecycle_stage_summary"]["service_count"] == 2
    assert first["service_lifecycle_stage_summary"]["dominant_stage_kind"] == (
        "COMPUTE_EXECUTION"
    )
    assert first["service_lifecycle_stage_summary"]["evidence_hash"] == (
        review_summary["service_lifecycle_stage_summary"]["evidence_hash"]
    )
    assert first["user_configuration_template_validation"][
        "validation_status"
    ] == "ALL_TEMPLATES_VALID"
    assert first["user_configuration_template_validation"][
        "evidence_hash"
    ] == review_summary["user_configuration_template_validation"]["evidence_hash"]
    assert first["user_configuration_control_surface_evidence"][
        "evidence_hash"
    ] == review_summary["user_configuration_control_surface_evidence"][
        "evidence_hash"
    ]
    assert first["user_configuration_control_surface_evidence"][
        "coverage_status"
    ] == "COMPLETE"
    assert first["traffic_demand_explanation"]["evidence_present"] is True
    assert first["traffic_demand_explanation"]["request_count"] == 2
    assert first["traffic_demand_explanation"]["compute_service_request_count"] == 1
    assert first["traffic_demand_explanation"]["frontend_inference_required"] is False
    assert first["user_service_requests"]["evidence_present"] is True
    assert first["user_service_requests"]["request_count"] == 2
    assert first["user_service_requests"]["exported_request_count"] == 2
    assert first["route_comparison_review"]["live_route_detail_endpoint"] == (
        "GET /runtime/details/routes/{route_id}"
    )
    assert first["route_comparison_review"]["exported_rows_only"] is True
    assert first["artifact_health"]["missing_required_filenames"] == ()
    assert first["artifact_health"]["missing_recommended_filenames"] == ()
    artifact_browser = first["artifact_browser_index_v1"]
    assert artifact_browser["index_id"] == RUNTIME_EXPORT_ARTIFACT_BROWSER_INDEX_V1_ID
    assert artifact_browser["index_scope"] == "RESULT_PACKAGE_ARTIFACT_BROWSER"
    assert artifact_browser["default_focus_filename"] == "scenario_review_bundle_v1.json"
    assert artifact_browser["missing_required_count"] == 0
    assert artifact_browser["browser_hash"].startswith("sha256:")
    categories = {item["category"]: item for item in artifact_browser["categories"]}
    assert categories["NETWORK_KPI_EVIDENCE"]["present_count"] == 8
    assert categories["ROUTE_SERVICE_EVIDENCE"]["present_count"] == 5
    assert categories["COMPUTE_RESOURCE_EVIDENCE"]["present_count"] == 1
    benchmark_acceptance_item = next(
        item
        for item in artifact_browser["items"]
        if item["filename"] == _BENCHMARK_ACCEPTANCE_BINDING_FILENAME
    )
    assert benchmark_acceptance_item["category"] == "AUDIT_HANDOFF"
    assert benchmark_acceptance_item["present"] is True
    assert benchmark_acceptance_item["default_json_pointer"] == (
        "/expected_range_results"
    )
    assert benchmark_acceptance_item["filter_hint"] == "benchmark acceptance"
    compute_item = next(
        item
        for item in artifact_browser["items"]
        if item["filename"] == _COMPUTE_RESOURCE_POOL_SUMMARY_FILENAME
    )
    assert compute_item["category"] == "COMPUTE_RESOURCE_EVIDENCE"
    assert compute_item["present"] is True
    assert compute_item["default_json_pointer"] == (
        "/compute_resource_pool_summary/dimensions"
    )
    assert compute_item["filter_hint"] == "compute resource"
    variation_item = next(
        item
        for item in artifact_browser["items"]
        if item["filename"] == "network_kpi_variation_explanation_v1.json"
    )
    assert variation_item["category"] == "NETWORK_KPI_EVIDENCE"
    assert variation_item["present"] is True
    assert variation_item["default_json_pointer"] == "/evidence"
    assert variation_item["filter_hint"] == "variation"
    dynamic_item = next(
        item
        for item in artifact_browser["items"]
        if item["filename"] == _NETWORK_KPI_DYNAMIC_STATUS_FILENAME
    )
    assert dynamic_item["category"] == "NETWORK_KPI_EVIDENCE"
    assert dynamic_item["present"] is True
    assert dynamic_item["default_json_pointer"] == "/dynamic_status"
    assert dynamic_item["filter_hint"] == "dynamic status"
    movement_item = next(
        item
        for item in artifact_browser["items"]
        if item["filename"] == _RUNTIME_KPI_MOVEMENT_SUMMARY_FILENAME
    )
    assert movement_item["category"] == "NETWORK_KPI_EVIDENCE"
    assert movement_item["present"] is True
    assert movement_item["default_json_pointer"] == "/evidence"
    assert movement_item["filter_hint"] == "movement"
    closure_item = next(
        item
        for item in artifact_browser["items"]
        if item["filename"] == _RUNTIME_CLOSURE_READINESS_FILENAME
    )
    assert closure_item["category"] == "OPERATOR_REVIEW"
    assert closure_item["present"] is True
    assert closure_item["default_json_pointer"] == "/evidence"
    assert closure_item["filter_hint"] == "closure readiness"
    dashboard_item = next(
        item
        for item in artifact_browser["items"]
        if item["filename"] == _RUNTIME_DASHBOARD_KPI_FILENAME
    )
    assert dashboard_item["category"] == "NETWORK_KPI_EVIDENCE"
    assert dashboard_item["present"] is True
    assert dashboard_item["default_json_pointer"] == "/dashboard_kpi/items"
    assert dashboard_item["filter_hint"] == "dashboard kpi"
    temporal_pressure_item = next(
        item
        for item in artifact_browser["items"]
        if item["filename"] == _NETWORK_TEMPORAL_PRESSURE_EVIDENCE_FILENAME
    )
    assert temporal_pressure_item["category"] == "NETWORK_KPI_EVIDENCE"
    assert temporal_pressure_item["present"] is True
    assert temporal_pressure_item["default_json_pointer"] == "/evidence"
    assert temporal_pressure_item["filter_hint"] == "temporal pressure"
    pressure_item = next(
        item
        for item in artifact_browser["items"]
        if item["filename"] == _ROUTE_PRESSURE_EVIDENCE_FILENAME
    )
    assert pressure_item["category"] == "ROUTE_SERVICE_EVIDENCE"
    assert pressure_item["present"] is True
    assert pressure_item["default_json_pointer"] == "/summary/items"
    stage_item = next(
        item
        for item in artifact_browser["items"]
        if item["filename"] == _SERVICE_LIFECYCLE_STAGE_SUMMARY_FILENAME
    )
    assert stage_item["category"] == "ROUTE_SERVICE_EVIDENCE"
    assert stage_item["present"] is True
    assert stage_item["default_json_pointer"] == "/stage_summary/stage_counts"
    assert stage_item["filter_hint"] == "service stage"
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
            "route_pressure_evidence_v1": _route_pressure_evidence(),
            "node_network_pressure_summary_v1": _node_network_pressure_summary(),
            "compute_resource_pool_summary_v1": _compute_resource_pool_summary(),
            "v2_executable_readiness_v1": _v2_executable_readiness(),
            "traffic_business_activity_window_v1": _traffic_business_activity_window(),
            "runtime_export_route_pressure_evidence_policy_v1": (
                _route_pressure_export_policy()
            ),
            "network_kpi_formula_evidence_v1": _network_kpi_formula_evidence(),
            "network_kpi_provenance_v2": _network_kpi_provenance_v2(),
            "network_kpi_variation_explanation_v1": (
                _network_kpi_variation_explanation()
            ),
            "network_kpi_dynamic_status_v1": _network_kpi_dynamic_status(),
            "runtime_kpi_movement_summary_v1": _runtime_kpi_movement_summary(),
            "runtime_closure_readiness_v1": _runtime_closure_readiness(),
            "runtime_dashboard_kpi_v1": _runtime_dashboard_kpi(),
            "network_flow_lifecycle_summary_v1": _network_flow_lifecycle_summary(),
            "service_lifecycle_stage_summary_v1": (
                _service_lifecycle_stage_summary()
            ),
            "user_service_request_summary_v2": _user_service_request_summary(),
            "runtime_export_user_service_request_policy_v1": (
                _user_service_request_export_policy()
            ),
            "runtime_export_route_detail_policy_v1": _route_detail_export_policy(),
            "runtime_export_service_trace_policy_v1": _service_trace_export_policy(),
        },
        "config": {"seed": 7, "duration_seconds": 120},
        "generated_config": _generated_config(),
        "user_configuration_template_validation_v1": (
            _user_configuration_template_validation()
        ),
        "user_configuration_control_surface_evidence_v1": (
            _user_configuration_control_surface_evidence()
        ),
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
        _BENCHMARK_ACCEPTANCE_BINDING_FILENAME,
        "network_kpi_formula_evidence_v1.json",
        _NETWORK_TEMPORAL_PRESSURE_EVIDENCE_FILENAME,
        "network_kpi_variation_explanation_v1.json",
        _NETWORK_KPI_DYNAMIC_STATUS_FILENAME,
        _RUNTIME_KPI_MOVEMENT_SUMMARY_FILENAME,
        _RUNTIME_CLOSURE_READINESS_FILENAME,
        _RUNTIME_DASHBOARD_KPI_FILENAME,
        _NETWORK_FLOW_LIFECYCLE_SUMMARY_FILENAME,
        _SERVICE_LIFECYCLE_STAGE_SUMMARY_FILENAME,
        "user_configuration_template_validation_v1.json",
        _USER_CONFIGURATION_CONTROL_SURFACE_EVIDENCE_FILENAME,
        _TRAFFIC_DEMAND_EXPLANATION_FILENAME,
        _TRAFFIC_BUSINESS_ACTIVITY_WINDOW_FILENAME,
        "review_summary_v1.json",
        "route_detail_index_v1.json",
        _ROUTE_PRESSURE_EVIDENCE_FILENAME,
        _NODE_NETWORK_PRESSURE_SUMMARY_FILENAME,
        _COMPUTE_RESOURCE_POOL_SUMMARY_FILENAME,
        _V2_EXECUTABLE_READINESS_FILENAME,
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
    assert first["route_pressure_evidence"]["evidence_present"] is True
    assert first["route_pressure_evidence"]["evidence_hash"] == review_summary[
        "route_pressure_evidence"
    ]["evidence_hash"]
    assert first["route_pressure_evidence"]["queued_route_count"] == 1
    assert first["route_pressure_evidence"]["pressure_edge_count"] == 2
    assert first["node_network_pressure_summary"]["evidence_present"] is True
    assert first["node_network_pressure_summary"]["evidence_hash"] == review_summary[
        "node_network_pressure_summary"
    ]["evidence_hash"]
    assert first["node_network_pressure_summary"]["pressure_edge_count"] == 4
    assert first["compute_resource_pool_summary"]["evidence_present"] is True
    assert first["compute_resource_pool_summary"]["evidence_hash"] == (
        review_summary["compute_resource_pool_summary"]["evidence_hash"]
    )
    assert first["compute_resource_pool_summary"]["dimension_count"] == 7
    assert first["network_kpi_formula_evidence"]["evidence_present"] is True
    assert first["network_kpi_formula_evidence"]["formula_evidence_status"] == (
        "FORMULA_AND_TIME_EVIDENCE_READY"
    )
    assert first["network_kpi_formula_evidence"]["evidence_hash"] == (
        review_summary["network_kpi_formula_evidence"]["evidence_hash"]
    )
    assert first["network_temporal_pressure_evidence"]["evidence_hash"] == (
        review_summary["network_temporal_pressure_evidence"]["evidence_hash"]
    )
    assert first["network_temporal_pressure_evidence"]["evidence_present"] is True
    assert first["network_kpi_dynamic_status"]["evidence_hash"] == (
        review_summary["network_kpi_dynamic_status"]["evidence_hash"]
    )
    assert first["network_kpi_dynamic_status"]["dynamic_status"] == "DYNAMIC"
    assert first["network_kpi_dynamic_status"]["evidence_present"] is True
    assert first["runtime_closure_readiness"]["evidence_hash"] == (
        review_summary["runtime_closure_readiness"]["evidence_hash"]
    )
    assert first["runtime_closure_readiness"]["closure_status"] == "RESULT_READY"
    assert first["runtime_closure_readiness"]["result_ready"] is True
    assert first["runtime_dashboard_kpi"]["evidence_hash"] == (
        review_summary["runtime_dashboard_kpi"]["evidence_hash"]
    )
    assert first["runtime_dashboard_kpi"]["metric_count"] == 5
    assert first["runtime_dashboard_kpi"]["time_varying_metric_count"] == 3
    assert first["service_lifecycle_stage_summary"]["evidence_present"] is True
    assert first["service_lifecycle_stage_summary"]["service_count"] == 2
    assert first["service_lifecycle_stage_summary"]["dominant_stage_kind"] == (
        "COMPUTE_EXECUTION"
    )
    assert first["service_lifecycle_stage_summary"]["evidence_hash"] == (
        review_summary["service_lifecycle_stage_summary"]["evidence_hash"]
    )
    assert first["user_configuration_template_validation"][
        "validation_status"
    ] == "ALL_TEMPLATES_VALID"
    assert first["user_configuration_template_validation"][
        "evidence_hash"
    ] == review_summary["user_configuration_template_validation"]["evidence_hash"]
    assert first["user_configuration_template_validation"][
        "all_templates_valid"
    ] is True
    assert first["user_configuration_control_surface_evidence"][
        "evidence_present"
    ] is True
    assert first["user_configuration_control_surface_evidence"][
        "coverage_status"
    ] == "COMPLETE"
    assert first["traffic_demand_explanation"]["evidence_present"] is True
    assert first["traffic_demand_explanation"]["request_count"] == 2
    assert first["traffic_demand_explanation"]["compute_service_request_count"] == 1
    assert first["traffic_demand_explanation"]["frontend_inference_required"] is False
    assert first["traffic_demand_explanation"]["evidence_hash"] == (
        review_summary["traffic_demand_explanation"]["evidence_hash"]
    )
    assert first["model_boundaries"]["packet_level_simulation"] is False
    assert first["model_boundaries"]["external_simulators"] is False
    assert first["recommended_review_order"][0] == "scenario_review_bundle_v1.json"
    assert "user_service_request_summary_v2.json" in first[
        "recommended_review_order"
    ]
    assert "user_configuration_template_validation_v1.json" in first[
        "recommended_review_order"
    ]
    assert _USER_CONFIGURATION_CONTROL_SURFACE_EVIDENCE_FILENAME in first[
        "recommended_review_order"
    ]
    assert _TRAFFIC_DEMAND_EXPLANATION_FILENAME in first["recommended_review_order"]
    assert _NETWORK_TEMPORAL_PRESSURE_EVIDENCE_FILENAME in first[
        "recommended_review_order"
    ]
    assert _NETWORK_KPI_DYNAMIC_STATUS_FILENAME in first["recommended_review_order"]
    assert _RUNTIME_CLOSURE_READINESS_FILENAME in first["recommended_review_order"]
    assert _RUNTIME_DASHBOARD_KPI_FILENAME in first["recommended_review_order"]
    assert _BENCHMARK_ACCEPTANCE_BINDING_FILENAME in first[
        "recommended_review_order"
    ]
    assert first["recommended_review_order"].index(
        _BENCHMARK_ACCEPTANCE_BINDING_FILENAME
    ) < first["recommended_review_order"].index(
        "network_kpi_benchmark_validation_v1.json"
    )
    assert first["recommended_review_order"].index(
        _TRAFFIC_DEMAND_EXPLANATION_FILENAME
    ) < first["recommended_review_order"].index(
        "user_service_request_summary_v2.json"
    )
    assert "service_trace_comparison_review_report_v1.json" in first[
        "recommended_review_order"
    ]
    assert _SERVICE_LIFECYCLE_STAGE_SUMMARY_FILENAME in first[
        "recommended_review_order"
    ]
    assert first["recommended_review_order"].index(
        _SERVICE_LIFECYCLE_STAGE_SUMMARY_FILENAME
    ) < first["recommended_review_order"].index("service_lifecycle_trace_v2.json")
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
    assert _COMPUTE_RESOURCE_POOL_SUMMARY_FILENAME in first["artifact_review"][
        "entrypoint_filenames"
    ]
    assert _RUNTIME_CLOSURE_READINESS_FILENAME in first["artifact_review"][
        "entrypoint_filenames"
    ]
    assert _RUNTIME_DASHBOARD_KPI_FILENAME in first["artifact_review"][
        "entrypoint_filenames"
    ]
    assert _COMPUTE_RESOURCE_POOL_SUMMARY_FILENAME in first[
        "recommended_review_order"
    ]
    assert _SERVICE_LIFECYCLE_STAGE_SUMMARY_FILENAME in first["artifact_review"][
        "entrypoint_filenames"
    ]
    assert "user_configuration_template_validation_v1.json" in first[
        "artifact_review"
    ]["entrypoint_filenames"]
    assert _TRAFFIC_DEMAND_EXPLANATION_FILENAME in first["artifact_review"][
        "entrypoint_filenames"
    ]
    assert _NETWORK_TEMPORAL_PRESSURE_EVIDENCE_FILENAME in first[
        "artifact_review"
    ]["entrypoint_filenames"]
    assert _NETWORK_KPI_DYNAMIC_STATUS_FILENAME in first["artifact_review"][
        "entrypoint_filenames"
    ]
    assert _BENCHMARK_ACCEPTANCE_BINDING_FILENAME in first["artifact_review"][
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
    assert first["submitted_records_complete"] is False
    assert first["expected_review_count"] == 4
    assert first["reviewed_recommended_count"] == 2
    assert first["missing_recommended_review_count"] == 0
    assert first["attention_recommended_review_filenames"] == (
        "export_package_audit_index_v1.json",
        "review_summary_v1.json",
    )
    assert first["attention_recommended_review_count"] == 2
    assert first["recommended_review_complete"] is False
    assert first["recommended_review_status"] == "RECOMMENDED_REVIEW_INCOMPLETE"
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


def test_runtime_export_scenario_review_checklist_v1_distinguishes_submitted_and_recommended_completion() -> None:
    scenario_review_bundle = {
        "bundle_id": RUNTIME_EXPORT_SCENARIO_REVIEW_BUNDLE_V1_ID,
        "scenario_review_hash": "sha256:scenario-review",
        "recommended_review_order": (
            "scenario_review_bundle_v1.json",
            "export_package_audit_index_v1.json",
            "service_trace_comparison_review_report_v1.json",
        ),
        "artifact_review": {
            "artifact_filenames": (
                "scenario_review_bundle_v1.json",
                "export_package_audit_index_v1.json",
            )
        },
    }

    checklist = build_runtime_export_scenario_review_checklist_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        scenario_review_bundle=scenario_review_bundle,
        records=(
            {
                "step_label": "Scenario entry checked",
                "artifact_filename": "scenario_review_bundle_v1.json",
                "review_status": "REVIEWED",
                "evidence_hash": "sha256:scenario",
            },
        ),
    )

    assert checklist["checklist_status"] == "CHECKLIST_COMPLETE"
    assert checklist["submitted_records_complete"] is True
    assert checklist["recommended_review_complete"] is False
    assert checklist["recommended_review_status"] == "RECOMMENDED_REVIEW_INCOMPLETE"
    assert checklist["expected_review_count"] == 3
    assert checklist["reviewed_recommended_filenames"] == (
        "scenario_review_bundle_v1.json",
    )
    assert checklist["missing_recommended_review_filenames"] == (
        "export_package_audit_index_v1.json",
        "service_trace_comparison_review_report_v1.json",
    )
    assert checklist["attention_recommended_review_filenames"] == ()
    assert checklist["checklist_hash"].startswith("sha256:")


def test_runtime_export_scenario_review_checklist_template_v1_is_deterministic() -> None:
    scenario_review_bundle = {
        "bundle_id": RUNTIME_EXPORT_SCENARIO_REVIEW_BUNDLE_V1_ID,
        "scenario_review_hash": "sha256:scenario-review",
        "recommended_review_order": (
            "scenario_review_bundle_v1.json",
            "export_package_audit_index_v1.json",
            "review_summary_v1.json",
            "service_lifecycle_trace_v2.json",
            "service_trace_comparison_review_report_v1.json",
        ),
        "review_summary": {"summary_hash": "sha256:review"},
        "diagnostics": {"diagnostics_hash": "sha256:diagnostics"},
        "reproducibility": {"manifest_hash": "sha256:manifest"},
        "user_configuration": {"config_hash": "sha256:config"},
    }
    audit_index = {
        "audit_hash": "sha256:audit",
        "service_trace_comparison_review_report_hash": "sha256:trace-report",
        "artifact_hashes": (
            {
                "name": "service_lifecycle_trace_v2",
                "filename": "service_lifecycle_trace_v2.json",
                "bytes": 2048,
                "sha256": "sha256:trace-artifact",
            },
        ),
    }

    first = build_runtime_export_scenario_review_checklist_template_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        scenario_review_bundle=scenario_review_bundle,
        audit_index=audit_index,
    )
    second = build_runtime_export_scenario_review_checklist_template_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        scenario_review_bundle=scenario_review_bundle,
        audit_index={
            **audit_index,
            "artifact_hashes": tuple(reversed(audit_index["artifact_hashes"])),
        },
    )

    assert first == second
    assert first["template_id"] == (
        RUNTIME_EXPORT_SCENARIO_REVIEW_CHECKLIST_TEMPLATE_V1_ID
    )
    assert first["template_status"] == "TEMPLATE_READY"
    assert first["expected_review_count"] == 5
    assert first["evidence_present_count"] == 5
    assert first["missing_evidence_filenames"] == ()
    assert [record["artifact_filename"] for record in first["records"]] == [
        "scenario_review_bundle_v1.json",
        "export_package_audit_index_v1.json",
        "review_summary_v1.json",
        "service_lifecycle_trace_v2.json",
        "service_trace_comparison_review_report_v1.json",
    ]
    assert first["records"][0]["step_label"] == "1 scenario entry"
    assert first["records"][0]["review_status"] == "NEEDS_FOLLOWUP"
    assert first["records"][1]["evidence_hash"] == "sha256:audit"
    assert first["records"][3]["evidence_hash"] == "sha256:trace-artifact"
    assert first["records"][3]["evidence_source"] == "AUDIT_INDEX_ARTIFACT_SHA256"
    assert first["records"][4]["evidence_hash"] == "sha256:trace-report"
    assert first["template_hash"].startswith("sha256:")
    assert json.loads(json.dumps(first, sort_keys=True))["template_id"] == (
        RUNTIME_EXPORT_SCENARIO_REVIEW_CHECKLIST_TEMPLATE_V1_ID
    )

    missing_report = build_runtime_export_scenario_review_checklist_template_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        scenario_review_bundle=scenario_review_bundle,
        audit_index={"audit_hash": "sha256:audit", "artifact_hashes": ()},
    )
    assert missing_report["template_status"] == "TEMPLATE_WARN"
    assert missing_report["missing_evidence_filenames"] == (
        "service_lifecycle_trace_v2.json",
        "service_trace_comparison_review_report_v1.json",
    )


def test_runtime_export_scenario_review_checklist_template_comparison_v1_detects_drift() -> None:
    template = {
        "template_id": RUNTIME_EXPORT_SCENARIO_REVIEW_CHECKLIST_TEMPLATE_V1_ID,
        "scenario_review_hash": "sha256:scenario-review",
        "template_hash": "sha256:template",
        "template_status": "TEMPLATE_READY",
        "records": (
            {
                "artifact_filename": "scenario_review_bundle_v1.json",
                "step_label": "1 scenario entry",
                "review_order_index": 0,
                "evidence_hash": "sha256:scenario-review",
                "template_record_hash": "sha256:template-record-a",
            },
            {
                "artifact_filename": "review_summary_v1.json",
                "step_label": "3 review summary",
                "review_order_index": 1,
                "evidence_hash": "sha256:review-new",
                "template_record_hash": "sha256:template-record-b",
            },
        ),
    }
    checklist = {
        "checklist_hash": "sha256:checklist",
        "checklist_status": "CHECKLIST_COMPLETE",
        "records": (
            {
                "artifact_filename": "scenario_review_bundle_v1.json",
                "step_label": "1 scenario entry",
                "review_order_index": 0,
                "evidence_hash": "sha256:scenario-review",
                "review_status": "REVIEWED",
                "record_hash": "sha256:checklist-record-a",
            },
            {
                "artifact_filename": "review_summary_v1.json",
                "step_label": "3 review summary",
                "review_order_index": 1,
                "evidence_hash": "sha256:review-old",
                "review_status": "REVIEWED",
                "record_hash": "sha256:checklist-record-b",
            },
            {
                "artifact_filename": "old_artifact.json",
                "step_label": "old artifact",
                "review_order_index": 99,
                "evidence_hash": "sha256:old",
                "review_status": "REVIEWED",
                "record_hash": "sha256:old-record",
            },
        ),
    }

    first = build_runtime_export_scenario_review_checklist_template_comparison_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        scenario_review_checklist=checklist,
        scenario_review_checklist_template=template,
    )
    second = build_runtime_export_scenario_review_checklist_template_comparison_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        scenario_review_checklist=checklist,
        scenario_review_checklist_template=template,
    )

    assert first == second
    assert first["comparison_id"] == (
        RUNTIME_EXPORT_SCENARIO_REVIEW_CHECKLIST_TEMPLATE_COMPARISON_V1_ID
    )
    assert first["comparison_status"] == "DRIFT"
    assert first["checklist_present"] is True
    assert first["aligned_record_count"] == 1
    assert first["missing_checklist_record_count"] == 0
    assert first["evidence_hash_mismatch_count"] == 1
    assert first["operator_attention_count"] == 0
    assert first["extra_checklist_record_count"] == 1
    assert first["records"][0]["comparison_status"] == "ALIGNED"
    assert first["records"][1]["comparison_status"] == "DRIFT"
    assert first["records"][1]["issue_labels"] == ("EVIDENCE_HASH_MISMATCH",)
    assert first["extra_records"][0]["comparison_status"] == "EXTRA"
    assert first["comparison_hash"].startswith("sha256:")
    assert json.loads(json.dumps(first, sort_keys=True))["comparison_id"] == (
        RUNTIME_EXPORT_SCENARIO_REVIEW_CHECKLIST_TEMPLATE_COMPARISON_V1_ID
    )

    missing = build_runtime_export_scenario_review_checklist_template_comparison_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        scenario_review_checklist=None,
        scenario_review_checklist_template=template,
    )
    assert missing["comparison_status"] == "CHECKLIST_MISSING"
    assert missing["checklist_present"] is False
    assert missing["missing_checklist_record_count"] == 2
    assert missing["records"][0]["comparison_status"] == "MISSING"


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
            "pinned_path_diffs": (
                {
                    "pointer": "/route/route_id",
                    "package_value": '"route-1"',
                    "live_value": '"route-1"',
                    "package_status": "resolved",
                    "live_status": "resolved",
                    "comparison_status": "match",
                },
                {
                    "pointer": "/route/latency_s",
                    "package_value": "0.1",
                    "live_value": "0.25",
                    "package_status": "resolved",
                    "live_status": "resolved",
                    "comparison_status": "different",
                },
            ),
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
    assert first["records"][1]["pinned_path_count"] == 2
    assert first["records"][1]["pinned_path_match_count"] == 1
    assert first["records"][1]["pinned_path_different_count"] == 1
    assert first["records"][1]["pinned_path_diffs"] == (
        {
            "pointer": "/route/route_id",
            "package_value": '"route-1"',
            "live_value": '"route-1"',
            "package_status": "RESOLVED",
            "live_status": "RESOLVED",
            "comparison_status": "MATCH",
        },
        {
            "pointer": "/route/latency_s",
            "package_value": "0.1",
            "live_value": "0.25",
            "package_status": "RESOLVED",
            "live_status": "RESOLVED",
            "comparison_status": "DIFFERENT",
        },
    )
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


def test_runtime_export_route_comparison_review_report_page_v1_filters_records() -> None:
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
    report = build_runtime_export_route_comparison_review_report_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        route_comparison_review=review,
        records=(
            {
                "route_id": "route-0",
                "comparison_status": "MATCH",
                "package_route_detail_hash": "sha256:package-route-0",
                "live_route_detail_hash": "sha256:live-route-0",
                "compared_fields": ("availability", "path"),
                "different_fields": (),
                "status_reason": "MATCHED",
                "operator_note": "baseline route aligned",
            },
            {
                "route_id": "route-1",
                "comparison_status": "DIFFERENT",
                "package_route_detail_hash": "sha256:package-route-1",
                "live_route_detail_hash": "sha256:live-route-1",
                "compared_fields": ("latency", "bottleneck", "path"),
                "different_fields": ("bottleneck", "latency"),
                "pinned_path_diffs": (
                    {
                        "pointer": "/route/latency_s",
                        "package_value": "0.1",
                        "live_value": "0.25",
                        "package_status": "RESOLVED",
                        "live_status": "RESOLVED",
                        "comparison_status": "DIFFERENT",
                    },
                ),
                "status_reason": "FIELDS_DIFFER",
                "operator_note": "capacity changed after runtime advanced",
            },
            {
                "route_id": "route-2",
                "comparison_status": "UNAVAILABLE",
                "package_route_detail_hash": "sha256:package-route-2",
                "live_route_detail_hash": "",
                "compared_fields": (),
                "different_fields": (),
                "status_reason": "LIVE_ROUTE_MISSING",
                "operator_note": "live runtime no longer has route",
            },
        ),
    )

    first_page = build_runtime_export_route_comparison_review_report_page_v1(
        report,
        cursor=0,
        limit=2,
    )
    second_page = build_runtime_export_route_comparison_review_report_page_v1(
        report,
        cursor=2,
        limit=2,
    )
    filtered = build_runtime_export_route_comparison_review_report_page_v1(
        report,
        status="different",
        query="runtime advanced",
    )
    repeated = build_runtime_export_route_comparison_review_report_page_v1(
        report,
        status="different",
        query="runtime advanced",
    )
    pinned_filtered = build_runtime_export_route_comparison_review_report_page_v1(
        report,
        status="different",
        query="/route/latency_s",
    )

    assert first_page["page_id"] == (
        RUNTIME_EXPORT_ROUTE_COMPARISON_REVIEW_REPORT_PAGE_V1_ID
    )
    assert first_page["report_hash"] == report["report_hash"]
    assert first_page["record_count"] == 3
    assert first_page["item_count"] == 2
    assert first_page["next_cursor"] == 2
    assert first_page["has_more"] is True
    assert [record["route_id"] for record in first_page["records"]] == [
        "route-0",
        "route-1",
    ]
    assert [record["route_id"] for record in second_page["records"]] == [
        "route-2",
    ]
    assert filtered == repeated
    assert filtered["filter_applied"] is True
    assert filtered["filters"] == {
        "query": "runtime advanced",
        "status": "DIFFERENT",
    }
    assert filtered["record_count"] == 1
    assert filtered["different_count"] == 1
    assert filtered["records"][0]["route_id"] == "route-1"
    assert pinned_filtered["record_count"] == 1
    assert pinned_filtered["records"][0]["pinned_path_different_count"] == 1
    assert pinned_filtered["records"][0]["pinned_path_diffs"][0]["pointer"] == (
        "/route/latency_s"
    )
    assert filtered["page_hash"].startswith("sha256:")


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
            "pinned_path_diffs": (
                {
                    "pointer": "/service_trace/trace/trace_id",
                    "package_value": '"trace:run"',
                    "live_value": '"trace:run"',
                    "package_status": "resolved",
                    "live_status": "resolved",
                    "comparison_status": "match",
                },
                {
                    "pointer": "/trace/terminal_state",
                    "package_value": '"RUNNING"',
                    "live_value": '"COMPLETE"',
                    "package_status": "resolved",
                    "live_status": "resolved",
                    "comparison_status": "different",
                },
            ),
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
    assert first["records"][1]["pinned_path_count"] == 2
    assert first["records"][1]["pinned_path_match_count"] == 1
    assert first["records"][1]["pinned_path_different_count"] == 1
    assert first["records"][1]["pinned_path_diffs"][1] == {
        "pointer": "/trace/terminal_state",
        "package_value": '"RUNNING"',
        "live_value": '"COMPLETE"',
        "package_status": "RESOLVED",
        "live_status": "RESOLVED",
        "comparison_status": "DIFFERENT",
    }
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
                "pinned_path_diffs": (
                    {
                        "pointer": "/trace/terminal_state",
                        "package_value": '"RUNNING"',
                        "live_value": '"COMPLETE"',
                        "package_status": "RESOLVED",
                        "live_status": "RESOLVED",
                        "comparison_status": "DIFFERENT",
                    },
                ),
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
    pinned_filtered = (
        build_runtime_export_service_trace_comparison_review_report_page_v1(
            report,
            status="different",
            query="/trace/terminal_state",
        )
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
    assert pinned_filtered["record_count"] == 1
    assert pinned_filtered["records"][0]["pinned_path_different_count"] == 1
    assert pinned_filtered["records"][0]["pinned_path_diffs"][0]["pointer"] == (
        "/trace/terminal_state"
    )
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
    assert completion[
        "scenario_review_checklist_recommended_review_complete"
    ] is False
    assert completion["scenario_review_checklist_expected_review_count"] == 0
    assert completion["scenario_review_checklist_reviewed_recommended_count"] == 0
    assert completion["missing_or_warning_evidence"] == (
        "AUDIT_INDEX_NOT_READY",
        "ROUTE_COMPARISON_REVIEW_REPORT_MISSING",
        "SCENARIO_REVIEW_CHECKLIST_MISSING",
    )
    assert completion["completion_hash"].startswith("sha256:")


def test_runtime_export_package_review_completion_v1_requires_recommended_checklist_steps() -> None:
    alignment = {"alignment_status": "ALIGNED", "alignment_hash": "sha256:alignment"}
    completion = build_runtime_export_package_review_completion_v1(
        package_id="pkg-1",
        package_dir="exports/pkg-1",
        audit_status="AUDIT_READY",
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
        route_comparison_review_report={
            "report_hash": "sha256:route-report",
            "record_count": 1,
            "error_count": 0,
        },
        scenario_review_checklist={
            "checklist_hash": "sha256:checklist",
            "checklist_status": "CHECKLIST_COMPLETE",
            "submitted_records_complete": True,
            "record_count": 1,
            "expected_review_count": 3,
            "reviewed_recommended_count": 1,
            "missing_recommended_review_filenames": (
                "export_package_audit_index_v1.json",
                "service_trace_comparison_review_report_v1.json",
            ),
            "attention_recommended_review_filenames": (),
            "recommended_review_complete": False,
            "recommended_review_status": "RECOMMENDED_REVIEW_INCOMPLETE",
        },
        runtime_export_boundary_alignment=alignment,
        user_configuration_binding={"validation_ok": True},
    )

    assert completion["completion_status"] == "REVIEW_INCOMPLETE"
    assert completion["handoff_ready"] is False
    assert completion["scenario_review_checklist_status"] == "CHECKLIST_COMPLETE"
    assert completion[
        "scenario_review_checklist_recommended_review_complete"
    ] is False
    assert completion["scenario_review_checklist_expected_review_count"] == 3
    assert completion["scenario_review_checklist_reviewed_recommended_count"] == 1
    assert completion[
        "scenario_review_checklist_missing_recommended_review_filenames"
    ] == (
        "export_package_audit_index_v1.json",
        "service_trace_comparison_review_report_v1.json",
    )
    assert completion["missing_or_warning_evidence"] == (
        "SCENARIO_REVIEW_RECOMMENDED_STEPS_INCOMPLETE",
    )


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


def test_runtime_export_benchmark_acceptance_binding_v1_matches_standard_scenarios() -> None:
    for scenario_id in benchmark_scenario_ids():
        scenario = benchmark_scenario_by_id(scenario_id, PROJECT_ROOT)
        config = load_config(PROJECT_ROOT / str(scenario["config_path"]))
        config_snapshot = {
            "type": "RUNTIME_CONFIG_SNAPSHOT",
            "status": {
                "fidelity_summary": scenario["fidelity_summary"],
                "route_provenance_trust_summary_v1": {
                    "trust_status": "COMPLETE_FLOW_LEVEL_ROUTE_PROXY",
                    "assessed_route_count": 1,
                },
                "network_kpi_benchmark_validation_v1": {
                    "validation_status": "PASS",
                    "failed_check_count": 0,
                },
                "network_kpi_calibration_v1": _network_kpi_calibration_v1(),
                "network_kpi_provenance_v2": _network_kpi_provenance_v2(),
            },
            "config": config_to_dict(config),
            "generated_config": {
                "satellite_count": scenario["satellite_count"],
                "ground_user_count": scenario["user_count"],
                "compute_node_count": scenario["compute_node_count"],
                "duration_seconds": scenario["runtime_duration_s"],
            },
        }

        binding = build_runtime_export_benchmark_acceptance_binding_v1(
            config_snapshot=config_snapshot,
        )

        assert binding["binding_id"] == (
            RUNTIME_EXPORT_BENCHMARK_ACCEPTANCE_BINDING_V1_ID
        )
        assert binding["binding_status"] == "MATCHED_STANDARD_SCENARIO"
        assert binding["check_status"] == "PASS"
        assert binding["scenario_id"] == scenario_id
        assert binding["expected_range_results"]
        assert all(
            result["status"] == "PASS"
            for result in binding["expected_range_results"]
        )
        expected_range_results = {
            result["metric"]: result for result in binding["expected_range_results"]
        }
        assert expected_range_results["time_pressure_period_s"][
            "observed_value"
        ] == config.network.time_pressure_period_s
        assert expected_range_results["time_pressure_burst_amplitude"][
            "observed_value"
        ] == config.network.time_pressure_burst_amplitude
        assert all(result["status"] == "PASS" for result in binding["fidelity_results"])
        assert all(
            result["status"] == "PASS"
            for result in binding["runtime_status_results"]
        )
        assert {
            result["evidence_artifact_filename"]
            for result in binding["expected_range_results"]
        } == {_BENCHMARK_ACCEPTANCE_BINDING_FILENAME}
        assert all(
            str(result["evidence_context_id"]).startswith("benchmark.expected_range.")
            for result in binding["expected_range_results"]
        )
        assert {
            result["evidence_json_pointer"]
            for result in binding["expected_range_results"]
        } == {"/expected_range_results"}
        assert {
            result["evidence_artifact_filename"]
            for result in binding["fidelity_results"]
        } == {"config_snapshot.json"}
        assert {
            result["evidence_context_id"]
            for result in binding["fidelity_results"]
        } == {
            "fidelity_summary.orbit_update_mode",
            "fidelity_summary.metrics_mode",
            "fidelity_summary.space_link_mode",
        }
        assert {
            result["evidence_json_pointer"]
            for result in binding["fidelity_results"]
        } == {
            "/status/fidelity_summary/orbit_update_mode",
            "/status/fidelity_summary/metrics_mode",
            "/status/fidelity_summary/space_link_mode",
        }
        runtime_artifacts = {
            result["check_id"]: result["evidence_artifact_filename"]
            for result in binding["runtime_status_results"]
        }
        assert runtime_artifacts == {
            "runtime_status.route_trust": "route_detail_index_v1.json",
            "runtime_status.network_kpi": (
                "network_kpi_benchmark_validation_v1.json"
            ),
            "runtime_status.network_temporal_pressure": (
                _NETWORK_TEMPORAL_PRESSURE_EVIDENCE_FILENAME
            ),
            "runtime_status.network_temporal_pressure_calibration": (
                "config_snapshot.json"
            ),
        }
        runtime_contexts = {
            result["check_id"]: result["evidence_context_id"]
            for result in binding["runtime_status_results"]
        }
        assert runtime_contexts == {
            "runtime_status.route_trust": "route_provenance_trust_summary_v1",
            "runtime_status.network_kpi": "network_kpi_benchmark_validation_v1",
            "runtime_status.network_temporal_pressure": (
                "network_kpi_provenance_v2.temporal_pressure_evidence"
            ),
            "runtime_status.network_temporal_pressure_calibration": (
                "network_kpi_calibration_v1.temporal_pressure_calibration"
            ),
        }
        runtime_pointers = {
            result["check_id"]: result["evidence_json_pointer"]
            for result in binding["runtime_status_results"]
        }
        assert runtime_pointers == {
            "runtime_status.route_trust": "/route_trust",
            "runtime_status.network_kpi": "/validation",
            "runtime_status.network_temporal_pressure": "/evidence",
            "runtime_status.network_temporal_pressure_calibration": (
                "/status/network_kpi_calibration_v1/"
                "temporal_pressure_calibration"
            ),
        }
        assert binding["binding_hash"].startswith("sha256:")


def test_runtime_export_benchmark_acceptance_binding_v1_warns_for_custom_scenario() -> None:
    binding = build_runtime_export_benchmark_acceptance_binding_v1(
        config_snapshot={
            "type": "RUNTIME_CONFIG_SNAPSHOT",
            "status": {},
            "config": {"satellite_count": 8, "duration_seconds": 120},
            "generated_config": {
                "satellite_count": 8,
                "ground_user_count": 20,
                "compute_node_count": 2,
                "duration_seconds": 120,
            },
        },
    )

    assert binding["binding_status"] == "NO_STANDARD_SCENARIO_MATCH"
    assert binding["check_status"] == "WARN"
    assert binding["issue_labels"] == ("NO_STANDARD_BENCHMARK_SCENARIO_MATCH",)


def test_runtime_export_package_acceptance_report_v1_marks_pass_warn_fail() -> None:
    completion = {
        "completion_id": RUNTIME_EXPORT_PACKAGE_REVIEW_COMPLETION_V1_ID,
        "package_id": "pkg-1",
        "package_dir": "exports/pkg-1",
        "completion_status": "REVIEW_COMPLETE",
        "handoff_ready": True,
        "completion_hash": "sha256:completion",
        "audit_status": "AUDIT_READY",
        "route_comparison_review_report_present": True,
        "route_comparison_review_error_count": 0,
        "route_comparison_review_report_hash": "sha256:route-report",
        "service_trace_comparison_review_report_present": True,
        "service_trace_comparison_review_error_count": 0,
        "service_trace_comparison_review_report_hash": "sha256:trace-report",
        "scenario_review_checklist_present": True,
        "scenario_review_checklist_status": "CHECKLIST_COMPLETE",
        "scenario_review_checklist_record_count": 2,
        "scenario_review_checklist_hash": "sha256:checklist",
        "scenario_review_checklist_recommended_review_complete": True,
        "scenario_review_checklist_reviewed_recommended_count": 2,
        "scenario_review_checklist_expected_review_count": 2,
        "network_kpi_benchmark_validation_status": "PASS",
        "network_kpi_benchmark_validation_failed_check_count": 0,
        "boundary_alignment_status": "ALIGNED",
        "user_configuration_validation_ok": True,
        "missing_or_warning_evidence": (),
        "evidence_labels": ("audit AUDIT_READY", "route_report saved"),
    }
    audit_index = {
        "audit_index_id": RUNTIME_EXPORT_PACKAGE_AUDIT_INDEX_V1_ID,
        "package_id": "pkg-1",
        "package_dir": "exports/pkg-1",
        "audit_hash": "sha256:audit",
        "manifest_hash": "sha256:manifest",
        "runtime_export_boundary_hash": "sha256:boundary",
        "user_configuration_schema_id": "sees.user_configuration.v2",
        "user_configuration_config_hash": "sha256:user-config",
        "benchmark_acceptance_binding_v1": {
            "type": "RUNTIME_EXPORT_BENCHMARK_ACCEPTANCE_BINDING_V1",
            "version": "v1",
            "binding_id": RUNTIME_EXPORT_BENCHMARK_ACCEPTANCE_BINDING_V1_ID,
            "source": "BACKEND_RUNTIME_EXPORT_CONFIG_SNAPSHOT",
            "matrix_id": "leo_twin.benchmark_scenario_matrix.v1",
            "binding_status": "MATCHED_STANDARD_SCENARIO",
            "check_status": "PASS",
            "scenario_id": "small_demo_72sat",
            "label": "72-satellite detailed baseline",
            "config_path": "configs/acceptance/small_demo_72sat.yaml",
            "scale_tier": "SMALL_DETAILED",
            "matched_identity_metrics": ("satellite_count",),
            "expected_range_results": (),
            "fidelity_results": (),
            "runtime_status_results": (),
            "issue_labels": (),
            "recommendation": "no action",
            "binding_hash": "sha256:benchmark-binding",
        },
        "artifact_count": 9,
        "missing_required_artifact_filenames": (),
        "audit_status": "AUDIT_READY",
        "audit_warnings": (),
        "forbidden_external_integrations": ("STK", "EXATA", "AFSIM", "DDS"),
        "packet_level_simulation": False,
        "event_replay_restore": False,
        "model_recomputation": False,
        "package_mutation_on_read": False,
        "package_review_completion_v1": completion,
    }

    first = build_runtime_export_package_acceptance_report_v1(
        audit_index=audit_index,
    )
    second = build_runtime_export_package_acceptance_report_v1(
        audit_index=json.loads(json.dumps(audit_index, sort_keys=True)),
    )

    assert first == second
    assert first["acceptance_id"] == RUNTIME_EXPORT_PACKAGE_ACCEPTANCE_REPORT_V1_ID
    assert first["acceptance_status"] == "PASS"
    assert first["demo_closed_loop_ready"] is True
    assert first["pass_count"] == 10
    assert first["warn_count"] == 0
    assert first["fail_count"] == 0
    assert [check["check_id"] for check in first["checks"]] == [
        "required_artifacts",
        "review_completion",
        "route_review",
        "service_trace_review",
        "scenario_review",
        "network_kpi_benchmark",
        "benchmark_scenario_gate",
        "model_boundary",
        "user_configuration",
        "forbidden_integrations",
    ]
    assert first["acceptance_hash"].startswith("sha256:")
    assert json.loads(json.dumps(first, sort_keys=True))["acceptance_id"] == (
        RUNTIME_EXPORT_PACKAGE_ACCEPTANCE_REPORT_V1_ID
    )

    warn = build_runtime_export_package_acceptance_report_v1(
        audit_index={
            **audit_index,
            "package_review_completion_v1": {
                **completion,
                "service_trace_comparison_review_report_present": False,
                "service_trace_comparison_review_report_hash": "",
            },
        },
    )
    assert warn["acceptance_status"] == "WARN"
    assert warn["demo_closed_loop_ready"] is True
    assert warn["warn_count"] == 1
    assert warn["operator_next_actions"] == (
        "save a service trace comparison review report for stronger handoff",
    )

    failed = build_runtime_export_package_acceptance_report_v1(
        audit_index={
            **audit_index,
            "missing_required_artifact_filenames": ("events.jsonl",),
            "package_review_completion_v1": {
                **completion,
                "completion_status": "REVIEW_INCOMPLETE",
                "handoff_ready": False,
                "missing_or_warning_evidence": (
                    "ROUTE_COMPARISON_REVIEW_REPORT_MISSING",
                ),
            },
        },
    )
    assert failed["acceptance_status"] == "FAIL"
    assert failed["demo_closed_loop_ready"] is False
    assert failed["fail_count"] == 2
    assert "complete blocking review evidence before handoff" in failed[
        "operator_next_actions"
    ]


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
        "submitted_records_complete": True,
        "record_count": 2,
        "expected_review_count": 2,
        "reviewed_recommended_count": 2,
        "missing_recommended_review_count": 0,
        "attention_recommended_review_count": 0,
        "missing_recommended_review_filenames": (),
        "attention_recommended_review_filenames": (),
        "recommended_review_complete": True,
        "recommended_review_status": "RECOMMENDED_REVIEW_COMPLETE",
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
        "status": {
            "runtime_export_reproducibility_boundary_v1": boundary,
            "network_kpi_dynamic_status_v1": _network_kpi_dynamic_status(),
            "runtime_kpi_movement_summary_v1": _runtime_kpi_movement_summary(),
            "runtime_closure_readiness_v1": _runtime_closure_readiness(),
            "runtime_dashboard_kpi_v1": _runtime_dashboard_kpi(),
            "network_flow_lifecycle_summary_v1": _network_flow_lifecycle_summary(),
            "service_lifecycle_stage_summary_v1": (
                _service_lifecycle_stage_summary()
            ),
        },
        "config": {"seed": 7},
        "generated_config": _generated_config(),
        "user_configuration_template_validation_v1": (
            _user_configuration_template_validation()
        ),
        "user_configuration_control_surface_evidence_v1": (
            _user_configuration_control_surface_evidence()
        ),
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
        "service_lifecycle_stage_summary": {
            "evidence_present": True,
            "evidence_hash": "sha256:service-stage",
            "service_count": 2,
            "observed_stage_count": 5,
            "pending_stage_count": 3,
            "dominant_stage_kind": "COMPUTE_EXECUTION",
        },
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
        _file(
            "user_configuration_template_validation_v1",
            "user_configuration_template_validation_v1.json",
            "sha256:template-validation-file",
        ),
        _file(
            "user_configuration_control_surface_evidence_v1",
            _USER_CONFIGURATION_CONTROL_SURFACE_EVIDENCE_FILENAME,
            "sha256:control-surface-file",
        ),
        _file(
            "traffic_demand_explanation_v1",
            _TRAFFIC_DEMAND_EXPLANATION_FILENAME,
            "sha256:traffic-demand-file",
        ),
        _file(
            "benchmark_acceptance_binding_v1",
            _BENCHMARK_ACCEPTANCE_BINDING_FILENAME,
            "sha256:benchmark-acceptance-file",
        ),
        _file(
            "network_kpi_dynamic_status_v1",
            _NETWORK_KPI_DYNAMIC_STATUS_FILENAME,
            "sha256:network-dynamic-status-file",
        ),
        _file(
            "service_lifecycle_stage_summary_v1",
            _SERVICE_LIFECYCLE_STAGE_SUMMARY_FILENAME,
            "sha256:service-stage-file",
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
    assert first["user_configuration_template_validation_present"] is True
    assert first["user_configuration_template_validation_status"] == (
        "ALL_TEMPLATES_VALID"
    )
    assert first[
        "user_configuration_template_validation_all_templates_valid"
    ] is True
    assert first["user_configuration_template_validation_invalid_template_count"] == 0
    assert first["user_configuration_template_validation_hash"].startswith("sha256:")
    assert first["user_configuration_control_surface_evidence_present"] is True
    assert first["user_configuration_control_surface_evidence_status"] == "COMPLETE"
    assert first["user_configuration_control_surface_key_field_count"] == 2
    assert first["user_configuration_control_surface_missing_key_count"] == 0
    assert first["user_configuration_control_surface_evidence_hash"].startswith(
        "sha256:"
    )
    assert first["traffic_demand_explanation_present"] is True
    assert first["traffic_demand_explanation_request_count"] == 2
    assert first["traffic_demand_explanation_compute_service_request_count"] == 1
    assert first["traffic_demand_explanation_frontend_inference_required"] is False
    assert first["traffic_demand_explanation_hash"].startswith("sha256:")
    assert first["network_kpi_dynamic_status_present"] is True
    assert first["network_kpi_dynamic_status_status"] == "DYNAMIC"
    assert first["network_kpi_dynamic_status_time_varying_kpi_count"] == 1
    assert first["network_kpi_dynamic_status_flat_kpi_count"] == 1
    assert first["network_kpi_dynamic_status_hash"].startswith("sha256:")
    assert first["runtime_kpi_movement_summary_present"] is True
    assert first["runtime_kpi_movement_summary_status"] == "TIME_VARYING_OBSERVED"
    assert first["runtime_kpi_movement_summary_moving_metric_count"] == 3
    assert first["runtime_kpi_movement_summary_compute_moving_metric_count"] == 1
    assert first["runtime_kpi_movement_summary_hash"].startswith("sha256:")
    assert first["runtime_closure_readiness_present"] is True
    assert first["runtime_closure_readiness_status"] == "RESULT_READY"
    assert first["runtime_closure_readiness_result_ready"] is True
    assert first["runtime_closure_readiness_failed_gate_count"] == 0
    assert first["runtime_closure_readiness_hash"].startswith("sha256:")
    assert first["runtime_dashboard_kpi_present"] is True
    assert first["runtime_dashboard_kpi_metric_count"] == 5
    assert first["runtime_dashboard_kpi_observed_metric_count"] == 5
    assert first["runtime_dashboard_kpi_zero_current_metric_count"] == 1
    assert first["runtime_dashboard_kpi_time_varying_metric_count"] == 3
    assert first["runtime_dashboard_kpi_hash"].startswith("sha256:")
    assert first["service_lifecycle_stage_summary_present"] is True
    assert first["service_lifecycle_stage_summary_service_count"] == 2
    assert first["service_lifecycle_stage_summary_observed_stage_count"] == 5
    assert first["service_lifecycle_stage_summary_dominant_stage_kind"] == (
        "COMPUTE_EXECUTION"
    )
    assert first["service_lifecycle_stage_summary_hash"].startswith("sha256:")
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
    assert first[
        "scenario_review_checklist_recommended_review_complete"
    ] is True
    assert first["scenario_review_checklist_expected_review_count"] == 2
    assert first["scenario_review_checklist_reviewed_recommended_count"] == 2
    assert first[
        "scenario_review_checklist_missing_recommended_review_filenames"
    ] == ()
    completion = first["package_review_completion_v1"]
    assert completion["completion_id"] == RUNTIME_EXPORT_PACKAGE_REVIEW_COMPLETION_V1_ID
    assert completion["completion_status"] == "REVIEW_COMPLETE"
    assert completion["handoff_ready"] is True
    assert completion["route_comparison_review_report_present"] is True
    assert completion["service_trace_comparison_review_report_present"] is True
    assert completion["service_trace_comparison_review_record_count"] == 2
    assert completion["service_trace_comparison_review_error_count"] == 0
    assert completion["service_lifecycle_stage_summary_present"] is True
    assert completion["service_lifecycle_stage_summary_service_count"] == 2
    assert completion["scenario_review_checklist_status"] == "CHECKLIST_COMPLETE"
    assert completion[
        "scenario_review_checklist_recommended_review_complete"
    ] is True
    assert completion["scenario_review_checklist_expected_review_count"] == 2
    assert completion["scenario_review_checklist_reviewed_recommended_count"] == 2
    assert completion["missing_or_warning_evidence"] == ()
    assert completion["completion_hash"].startswith("sha256:")
    assert first["package_review_completion_status"] == "REVIEW_COMPLETE"
    assert first["package_review_completion_hash"] == completion["completion_hash"]
    assert first["self_artifact_excluded_from_hashes"] is True
    assert [item["filename"] for item in first["artifact_hashes"]] == [
        _BENCHMARK_ACCEPTANCE_BINDING_FILENAME,
        "config_snapshot.json",
        "events.jsonl",
        "manifest.json",
        "metrics.csv",
        _NETWORK_KPI_DYNAMIC_STATUS_FILENAME,
        "route_comparison_review_report_v1.json",
        "scenario_review_bundle_v1.json",
        "scenario_review_checklist_v1.json",
        _SERVICE_LIFECYCLE_STAGE_SUMMARY_FILENAME,
        "service_trace_comparison_review_report_v1.json",
        "summary.json",
        _TRAFFIC_DEMAND_EXPLANATION_FILENAME,
        _USER_CONFIGURATION_CONTROL_SURFACE_EVIDENCE_FILENAME,
        "user_configuration_template_validation_v1.json",
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
            "v2_executable_readiness_v1": _v2_executable_readiness(),
            "runtime_kpi_movement_summary_v1": _runtime_kpi_movement_summary(),
            "runtime_closure_readiness_v1": _runtime_closure_readiness(),
            "runtime_dashboard_kpi_v1": _runtime_dashboard_kpi(),
            "traffic_business_activity_window_v1": _traffic_business_activity_window(),
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
        _BENCHMARK_ACCEPTANCE_BINDING_FILENAME,
        "network_kpi_formula_evidence_v1.json",
        _NETWORK_TEMPORAL_PRESSURE_EVIDENCE_FILENAME,
        "network_kpi_variation_explanation_v1.json",
        _NETWORK_KPI_DYNAMIC_STATUS_FILENAME,
        _RUNTIME_KPI_MOVEMENT_SUMMARY_FILENAME,
        _RUNTIME_CLOSURE_READINESS_FILENAME,
        _RUNTIME_DASHBOARD_KPI_FILENAME,
        _NETWORK_FLOW_LIFECYCLE_SUMMARY_FILENAME,
        _SERVICE_LIFECYCLE_STAGE_SUMMARY_FILENAME,
        "user_configuration_template_validation_v1.json",
        _USER_CONFIGURATION_CONTROL_SURFACE_EVIDENCE_FILENAME,
        _TRAFFIC_DEMAND_EXPLANATION_FILENAME,
        _TRAFFIC_BUSINESS_ACTIVITY_WINDOW_FILENAME,
        "review_summary_v1.json",
        "route_detail_index_v1.json",
        _ROUTE_PRESSURE_EVIDENCE_FILENAME,
        _NODE_NETWORK_PRESSURE_SUMMARY_FILENAME,
        _COMPUTE_RESOURCE_POOL_SUMMARY_FILENAME,
        _V2_EXECUTABLE_READINESS_FILENAME,
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
    assert review_summary["route_pressure_evidence"]["evidence_present"] is False
    assert diagnostics["route_trust"]["trust_status"] == "MISSING_ROUTE_TRUST_EVIDENCE"
    assert diagnostics["route_trust"]["evidence_present"] is False
    assert diagnostics["package"]["package_complete"] is True
    assert {
        finding["code"] for finding in diagnostics["findings"]
        } == {
            "ROUTE_TRUST_EVIDENCE_MISSING",
            "ROUTE_PRESSURE_EVIDENCE_MISSING",
            "NODE_NETWORK_PRESSURE_SUMMARY_MISSING",
            "COMPUTE_RESOURCE_POOL_SUMMARY_MISSING",
            "NETWORK_FLOW_LIFECYCLE_SUMMARY_MISSING",
            "SERVICE_LIFECYCLE_STAGE_SUMMARY_MISSING",
            "NETWORK_KPI_BENCHMARK_VALIDATION_MISSING",
            "NETWORK_KPI_FORMULA_EVIDENCE_MISSING",
            "NETWORK_TEMPORAL_PRESSURE_EVIDENCE_MISSING",
            "NETWORK_KPI_VARIATION_EXPLANATION_MISSING",
            "NETWORK_KPI_DYNAMIC_STATUS_MISSING",
            "USER_CONFIGURATION_TEMPLATE_VALIDATION_MISSING",
            "USER_CONFIGURATION_CONTROL_SURFACE_EVIDENCE_MISSING",
            "TRAFFIC_DEMAND_EXPLANATION_MISSING",
            "USER_SERVICE_REQUEST_SUMMARY_MISSING",
        }
    assert diagnostics["finding_count"] == 15


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


def _network_kpi_formula_evidence() -> dict[str, object]:
    return {
        "version": "v1",
        "evidence_id": "leo_twin.network_kpi_formula_evidence.v1",
        "source": "NETWORK_KPI_PROVENANCE_V2_AND_CALIBRATION_V1",
        "provenance_id": "leo_twin.network_kpi_provenance.v2",
        "calibration_id": "leo_twin.network_kpi_calibration.v1",
        "metric_model": "FLOW_LEVEL_PROXY",
        "packet_level_simulation": False,
        "kpi_count": 2,
        "observed_kpi_count": 2,
        "runtime_value_missing_count": 0,
        "selected_input_count": 3,
        "selected_observed_input_count": 3,
        "missing_selected_input_count": 0,
        "time_varying_kpi_count": 1,
        "flat_kpi_count": 1,
        "formula_evidence_status": "FORMULA_AND_TIME_EVIDENCE_READY",
        "kpis": (
            {
                "metric": "EFFECTIVE_THROUGHPUT",
                "display_name": "Effective throughput",
                "runtime_summary_key": "network_quality_effective_throughput_mbps",
                "current_value": 180.0,
                "unit": "Mbps",
                "status": "OBSERVED",
                "observed_source": "COMPLETED_FLOW_CAPACITY",
                "observed_source_label": "completed flow capacity",
                "formula_summary": "min(delivered, route capacity)",
                "selection_policy": "Prefer completed-flow throughput.",
                "selected_input_count": 2,
                "selected_observed_input_count": 2,
                "missing_selected_input_count": 0,
                "selected_inputs": (
                    {
                        "field": "network_quality_estimated_delivered_throughput_mbps",
                        "current_value": 180.0,
                        "observed": True,
                        "role": "primary",
                        "selection_reason": "selected source",
                    },
                    {
                        "field": "network_quality_time_adjusted_delivered_throughput_mbps",
                        "current_value": 171.0,
                        "observed": True,
                        "role": "time_driver",
                        "selection_reason": "time adjusted source",
                    },
                ),
                "variation_status": "TIME_VARYING",
                "flat_reason": "",
                "latest_is_zero": False,
                "evidence_status": "FORMULA_AND_TIME_VARYING",
            },
            {
                "metric": "EFFECTIVE_LOSS_PROXY",
                "display_name": "Effective loss proxy",
                "runtime_summary_key": "network_quality_effective_loss_proxy_rate",
                "current_value": 0.02,
                "unit": "ratio",
                "status": "OBSERVED",
                "observed_source": "PRESSURE_LOSS_PROXY",
                "observed_source_label": "pressure loss proxy",
                "formula_summary": "max(route loss, demand pressure loss)",
                "selection_policy": "Prefer pressure loss proxy.",
                "selected_input_count": 1,
                "selected_observed_input_count": 1,
                "missing_selected_input_count": 0,
                "selected_inputs": (
                    {
                        "field": "network_quality_time_pressure_loss_proxy_rate",
                        "current_value": 0.02,
                        "observed": True,
                        "role": "time_driver",
                        "selection_reason": "selected source",
                    },
                ),
                "variation_status": "FLAT_NONZERO",
                "flat_reason": "unchanged pressure inputs",
                "latest_is_zero": False,
                "evidence_status": "FORMULA_READY_FLAT_OR_LIMITED_SERIES",
            },
        ),
        "caveats": (
            "Formula evidence summarizes backend flow-level proxy inputs.",
        ),
    }


def _network_kpi_calibration_v1() -> dict[str, object]:
    return {
        "version": "v1",
        "calibration_id": "leo_twin.network_kpi_calibration.v1",
        "source": "KPI_TIME_SERIES_V1_AND_METRICS_SUMMARY",
        "packet_level_simulation": False,
        "sample_count": 2,
        "sim_time_span_s": 60.0,
        "calibration_status": "TIME_VARYING_OBSERVED",
        "temporal_pressure_calibration": {
            "version": "v1",
            "calibration_id": (
                "leo_twin.network_temporal_pressure_calibration.v1"
            ),
            "source": "NETWORK_KPI_CALIBRATION_V1",
            "temporal_pressure_model": (
                "DETERMINISTIC_TRIANGULAR_LOAD_GATED_PROXY"
            ),
            "packet_level_simulation": False,
            "frontend_inference_required": False,
            "sample_count": 2,
            "sim_time_span_s": 60.0,
            "period_s": 120.0,
            "factor": 0.85,
            "loss_proxy_rate": 0.07,
            "delay_variation_proxy_s": 0.002,
            "temporal_pressure_active": True,
            "loss_proxy_active": True,
            "delay_variation_proxy_active": True,
            "status": "TEMPORAL_DRIVER_ALIGNED",
            "aligned_metric_count": 3,
            "aligned_metrics": (
                "EFFECTIVE_THROUGHPUT",
                "EFFECTIVE_LOSS_PROXY",
                "EFFECTIVE_DELAY_VARIATION_PROXY",
            ),
            "model_assumptions": (
                "Temporal pressure calibration is a deterministic flow-level proxy.",
            ),
            "calibration_hash": "sha256:temporal-calibration-test",
        },
        "kpi_count": 0,
        "kpis": (),
    }


def _network_kpi_provenance_v2() -> dict[str, object]:
    return {
        "version": "v2",
        "provenance_id": "leo_twin.network_kpi_provenance.v2",
        "source": "BACKEND_METRICS_SUMMARY",
        "network_model_contract_id": "leo_twin.network_model_contract.v2",
        "metric_model": "FLOW_LEVEL_PROXY",
        "packet_level_simulation": False,
        "frontend_inference_required": False,
        "temporal_pressure_evidence": {
            "version": "v1",
            "evidence_id": "leo_twin.network_temporal_pressure_evidence.v1",
            "source": "METRICS_SUMMARY",
            "metric_model": "FLOW_LEVEL_PROXY",
            "temporal_pressure_model": (
                "DETERMINISTIC_TRIANGULAR_LOAD_GATED_PROXY"
            ),
            "packet_level_simulation": False,
            "frontend_inference_required": False,
            "status": "OBSERVED",
            "required_field_count": 3,
            "observed_required_field_count": 3,
            "source_field_count": 10,
            "time_pressure_period_s": 120.0,
            "time_pressure_phase": 0.5,
            "time_pressure_factor": 0.85,
            "dominant_load_component": {
                "component": "demand_pressure",
                "field": "network_quality_demand_pressure_proxy",
                "current_value": 0.92,
                "value_source": "METRICS_SUMMARY",
            },
            "load_pressure_proxy": 0.92,
            "loss_proxy_rate": 0.07,
            "delay_variation_proxy_s": 0.002,
            "temporal_pressure_active": True,
            "loss_proxy_active": True,
            "delay_variation_proxy_active": True,
            "delivered_throughput_mbps": 180.0,
            "time_adjusted_delivered_throughput_mbps": 171.0,
            "throughput_delta_mbps": 9.0,
            "source_fields": (
                "network_quality_time_pressure_factor",
                "network_quality_time_pressure_loss_proxy_rate",
                "network_quality_delay_variation_pressure_s",
            ),
            "model_assumptions": (
                "Temporal pressure is a deterministic load-gated flow-level proxy.",
            ),
        },
        "kpi_count": 0,
        "kpis": (),
    }


def _network_kpi_variation_explanation() -> dict[str, object]:
    return {
        "version": "v1",
        "explanation_id": "leo_twin.network_kpi_variation_explanation.v1",
        "source": "NETWORK_KPI_PROVENANCE_V2_AND_TIME_SERIES",
        "provenance_id": "leo_twin.network_kpi_provenance.v2",
        "calibration_id": "leo_twin.network_kpi_calibration.v1",
        "formula_evidence_id": "leo_twin.network_kpi_formula_evidence.v1",
        "metric_model": "FLOW_LEVEL_PROXY",
        "packet_level_simulation": False,
        "explanation_status": "TIME_VARIATION_EXPLAINED",
        "sample_count": 6,
        "sim_time_span_s": 120.0,
        "kpi_count": 2,
        "time_varying_kpi_count": 1,
        "flat_kpi_count": 1,
        "zero_latest_kpi_count": 0,
        "missing_explanation_count": 0,
        "model_assumptions": (
            "KPI variation is explained by backend flow-level proxy inputs.",
        ),
        "caveats": (
            "Variation explanation is deterministic and not packet-level.",
        ),
    }


def _network_kpi_dynamic_status() -> dict[str, object]:
    return {
        "version": "v1",
        "status_id": "leo_twin.network_kpi_dynamic_status.v1",
        "source": "NETWORK_KPI_CALIBRATION_V1",
        "calibration_id": "leo_twin.network_kpi_calibration.v1",
        "metric_model": "FLOW_LEVEL_PROXY",
        "packet_level_simulation": False,
        "frontend_inference_required": False,
        "sample_count": 6,
        "sim_time_span_s": 120.0,
        "activity_active": True,
        "dynamic_status": "DYNAMIC",
        "kpi_count": 2,
        "time_varying_kpi_count": 1,
        "flat_kpi_count": 1,
        "missing_kpi_count": 0,
        "zero_latest_kpi_count": 0,
        "dynamic_metric_names": ("EFFECTIVE_THROUGHPUT",),
        "flat_metric_names": ("EFFECTIVE_LOSS_PROXY",),
        "zero_latest_metric_names": (),
        "items": (),
        "operator_summary": (
            "Network KPI samples include backend-observed time variation."
        ),
        "blocking_reasons": (),
        "recommended_next_action": (
            "RENDER_BACKEND_KPI_SERIES_AND_EXPLANATION"
        ),
        "model_assumptions": (
            "Dynamic status is derived from backend network_kpi_calibration_v1.",
        ),
        "status_hash": "sha256:network-dynamic-status-test",
    }


def _runtime_kpi_movement_summary() -> dict[str, object]:
    return {
        "version": "v1",
        "summary_id": "leo_twin.runtime_kpi_movement_summary.v1",
        "source": "KPI_TIME_SERIES_V1_AND_METRICS_SUMMARY",
        "metric_model": "FLOW_LEVEL_PROXY",
        "packet_level_simulation": False,
        "frontend_inference_required": False,
        "sample_count": 6,
        "sim_time_span_s": 120.0,
        "metric_count": 11,
        "observed_metric_count": 11,
        "moving_metric_count": 3,
        "flat_metric_count": 8,
        "zero_latest_metric_count": 6,
        "network_moving_metric_count": 2,
        "compute_moving_metric_count": 1,
        "movement_status": "TIME_VARYING_OBSERVED",
        "model_assumptions": (
            "Movement evidence is derived only from backend kpi_time_series_v1 samples.",
        ),
        "items": (
            {
                "metric": "NETWORK_EFFECTIVE_THROUGHPUT",
                "category": "NETWORK",
                "movement_status": "TIME_VARYING",
                "absolute_delta": 20.0,
            },
        ),
    }


def _runtime_closure_readiness() -> dict[str, object]:
    return {
        "version": "v1",
        "summary_id": "leo_twin.runtime_closure_readiness.v1",
        "source": "BACKEND_RUNTIME_STATUS",
        "target": "industrial-v2-demo-result-loop",
        "lifecycle_state": "STOPPED",
        "current_sim_time": 120.0,
        "runtime_duration_seconds": 120.0,
        "runtime_duration_reached": True,
        "runtime_completion_reason": "DURATION_REACHED",
        "closure_status": "RESULT_READY",
        "result_ready": True,
        "gate_count": 3,
        "passed_gate_count": 3,
        "waiting_gate_count": 0,
        "failed_gate_count": 0,
        "blocking_gate_ids": (),
        "gates": (
            {
                "gate_id": "runtime_duration",
                "label": "runtime duration",
                "status": "PASS",
                "required_paths": ("runtime.current_sim_time",),
                "missing_paths": (),
                "issue_count": 0,
                "issues": (),
            },
            {
                "gate_id": "kpi_series",
                "label": "KPI series",
                "status": "PASS",
                "required_paths": ("runtime_kpi_movement_summary_v1",),
                "missing_paths": (),
                "issue_count": 0,
                "issues": (),
            },
            {
                "gate_id": "business_requests",
                "label": "business requests",
                "status": "PASS",
                "required_paths": ("traffic_business_activity_window_v1",),
                "missing_paths": (),
                "issue_count": 0,
                "issues": (),
            },
        ),
        "frontend_inference_required": False,
        "packet_level_simulation": False,
        "model_assumptions": (
            "Runtime closure is derived from backend status gates.",
        ),
        "operator_next_action": "EXPORT_RESULT_PACKAGE",
        "closure_hash": "sha256:runtime-closure",
    }


def _runtime_dashboard_kpi() -> dict[str, object]:
    return {
        "version": "v1",
        "summary_id": "leo_twin.runtime_dashboard_kpi.v1",
        "source": "BACKEND_RUNTIME_STATUS",
        "metric_model": "FLOW_LEVEL_PROXY",
        "packet_level_simulation": False,
        "frontend_inference_required": False,
        "sample_count": 6,
        "tail_sample_time_s": 120.0,
        "metrics_summary_event_time_s": 120.0,
        "metrics_summary_observation_time_s": 120.0,
        "metrics_summary_time_source": "RUNTIME_KPI_TAIL",
        "runtime_movement_status": "TIME_VARYING_OBSERVED",
        "network_dynamic_status": "DYNAMIC",
        "metric_count": 5,
        "observed_metric_count": 5,
        "zero_current_metric_count": 1,
        "time_varying_metric_count": 3,
        "network_metric_count": 4,
        "compute_metric_count": 1,
        "items": (
            {
                "metric": "NETWORK_EFFECTIVE_THROUGHPUT",
                "label": "全网平均吞吐量",
                "category": "NETWORK",
                "current_value": 120.5,
                "unit": "Mbps",
                "value_source": "KPI_TIME_SERIES_TAIL",
                "movement_status": "TIME_VARYING",
            },
            {
                "metric": "COMPUTE_RESOURCE_UTILIZATION",
                "label": "算力资源消耗",
                "category": "COMPUTE",
                "current_value": 0.42,
                "unit": "ratio",
                "value_source": "KPI_TIME_SERIES_TAIL",
                "movement_status": "TIME_VARYING",
            },
        ),
        "model_assumptions": (
            "Dashboard KPI values are backend-owned status fields.",
        ),
        "summary_hash": "sha256:runtime-dashboard-kpi",
    }


def _network_flow_lifecycle_summary() -> dict[str, object]:
    return {
        "version": "v1",
        "summary_id": "leo_twin.network_flow_lifecycle_summary.v1",
        "source": "METRICS_SUMMARY_NETWORK_FLOW_LIFECYCLE_FIELDS",
        "metrics_source": "BACKEND_METRICS_COLLECTOR",
        "lifecycle_model": "ROUTE_UPDATE_TO_FLOW_COMPLETE_WINDOW",
        "packet_level_simulation": False,
        "frontend_inference_required": False,
        "active_flow_count": 2,
        "active_available_flow_count": 2,
        "active_blocked_flow_count": 0,
        "active_demand_mbps": 30.0,
        "active_capacity_mbps": 120.0,
        "active_latency_avg_s": 0.08,
        "oldest_active_age_s": 12.0,
        "completed_flow_count": 1,
        "successful_flow_count": 1,
        "failed_flow_count": 0,
        "lifecycle_status": "ACTIVE",
        "model_assumptions": (
            "Flow lifecycle state is derived from ROUTE_UPDATE and FLOW_COMPLETE observations.",
            "Active demand and capacity are flow-level route proxies, not packet queues.",
            "Packet-level behavior is not simulated.",
        ),
        "summary_hash": "sha256:network-flow-lifecycle",
    }


def _service_lifecycle_stage_summary() -> dict[str, object]:
    return {
        "version": "v1",
        "summary_id": "leo_twin.service_lifecycle_stage_summary.v1",
        "source": "SERVICE_LATENCY_HISTORY",
        "source_summary": "service_latency_history_v1",
        "trace_model": "COMMUNICATION_COMPUTE_COMPONENT_PROXY",
        "packet_level_simulation": False,
        "frontend_inference_required": False,
        "service_count": 2,
        "complete_service_count": 1,
        "running_service_count": 1,
        "incomplete_service_count": 0,
        "stage_family_count": 4,
        "observed_stage_count": 5,
        "pending_stage_count": 3,
        "unknown_stage_count": 0,
        "total_stage_duration_s": 4.5,
        "dominant_stage_kind": "COMPUTE_EXECUTION",
        "dominant_stage_label": "Compute execution",
        "dominant_stage_reason": "MAX_TOTAL_DURATION",
        "stage_counts": (
            {
                "stage_kind": "INPUT_NETWORK",
                "stage_label": "Input network",
                "observed_count": 2,
                "pending_count": 0,
                "unknown_count": 0,
                "total_duration_s": 1.5,
            },
            {
                "stage_kind": "COMPUTE_EXECUTION",
                "stage_label": "Compute execution",
                "observed_count": 2,
                "pending_count": 0,
                "unknown_count": 0,
                "total_duration_s": 3.0,
            },
        ),
        "terminal_state_counts": (
            {"terminal_state": "COMPLETE", "count": 1},
            {"terminal_state": "RUNNING", "count": 1},
        ),
        "terminal_reason_counts": (
            {"terminal_reason": "OUTPUT_DELIVERED", "count": 1},
            {"terminal_reason": "WAITING_FOR_OUTPUT", "count": 1},
        ),
        "summary_hash": "sha256:service-stage",
    }

def _compute_resource_pool_summary() -> dict[str, object]:
    return {
        "version": "v1",
        "summary_id": "leo_twin.compute_resource_pool_summary.v1",
        "source": "METRICS_SUMMARY_COMPUTE_RESOURCE_FIELDS",
        "metric_model": "RESOURCE_VECTOR_FLOW_LEVEL_ESTIMATE",
        "packet_level_simulation": False,
        "frontend_inference_required": False,
        "node_count": 2,
        "busy_node_count": 1,
        "idle_node_count": 1,
        "vector_capacity_reported": True,
        "vector_utilization_mode": "RESOURCE_VECTOR_ESTIMATED",
        "dimension_count": 7,
        "active_dimension_count": 6,
        "consumed_dimension_count": 3,
        "saturated_dimension_count": 1,
        "bottleneck": {
            "resource": "gpu_tflops_fp32",
            "label": "GPU FP32 TFLOPS",
            "utilization": 1.0,
            "used": 2.0,
            "total": 2.0,
            "available": 0.0,
            "status": "SATURATED",
        },
        "dimensions": (
            {
                "resource": "cpu_gflops_fp32",
                "label": "CPU FP32 GFLOPS",
                "unit": "GFLOPS FP32",
                "total": 20.0,
                "available": 10.0,
                "used": 10.0,
                "utilization": 0.5,
                "resource_status": "ACTIVE",
            },
            {
                "resource": "gpu_tflops_fp32",
                "label": "GPU FP32 TFLOPS",
                "unit": "TFLOPS FP32",
                "total": 2.0,
                "available": 0.0,
                "used": 2.0,
                "utilization": 1.0,
                "resource_status": "SATURATED",
            },
        ),
        "visualization_policy": {
            "preferred_chart": "PER_DIMENSION_UTILIZATION_BARS",
            "pie_chart_allowed": False,
            "reason": "Compute dimensions use different units.",
        },
        "model_assumptions": (
            "Resource pool values are derived from ComputeNodeState metrics.",
        ),
        "summary_hash": "sha256:compute-pool",
    }


def _v2_executable_readiness() -> dict[str, object]:
    return {
        "version": "v1",
        "readiness_id": "leo_twin.v2_executable_readiness.v1",
        "source": "BACKEND_RUNTIME_STATUS",
        "target": "industrial-v2-demo-loop",
        "readiness_status": "READY",
        "executable_ready": True,
        "gate_count": 2,
        "passed_gate_count": 2,
        "failed_gate_count": 0,
        "gates": (
            {
                "gate_id": "runtime",
                "label": "runtime session",
                "status": "PASS",
                "required_paths": ("runtime.status",),
                "missing_paths": (),
                "issue_count": 0,
                "issues": (),
                "evidence": (
                    {
                        "path": "runtime.status",
                        "present": True,
                        "value_summary": "RUNNING",
                    },
                ),
            },
            {
                "gate_id": "traffic_business",
                "label": "traffic business",
                "status": "PASS",
                "required_paths": ("traffic_business_activity_window_v1",),
                "missing_paths": (),
                "issue_count": 0,
                "issues": (),
                "evidence": (
                    {
                        "path": "traffic_business_activity_window_v1",
                        "present": True,
                        "value_summary": "2 users",
                    },
                ),
            },
        ),
        "missing_required_gate_ids": (),
        "frontend_inference_required": False,
        "packet_level_simulation": False,
        "operator_next_action": "Run standard 72/300/1200 acceptance scenarios.",
        "readiness_hash": "sha256:readiness",
    }


def _traffic_business_activity_window() -> dict[str, object]:
    return {
        "version": "v1",
        "summary_id": "leo_twin.traffic_business_activity_window.v1",
        "source": "TrafficDemandBatch.records",
        "metric_model": "FLOW_LEVEL_BUSINESS_ACTIVITY_WINDOW",
        "packet_level_simulation": False,
        "frontend_inference_required": False,
        "current_sim_time": 12.0,
        "request_count": 2,
        "user_count": 2,
        "active_user_count": 1,
        "recent_user_count": 0,
        "pending_user_count": 1,
        "idle_user_count": 0,
        "window_user_count": 2,
        "window_active_user_count": 1,
        "window_recent_user_count": 0,
        "window_pending_user_count": 1,
        "window_idle_user_count": 0,
        "window": {
            "lookback_window_s": 10.0,
            "lookahead_window_s": 20.0,
            "window_start_s": 2.0,
            "window_end_s": 32.0,
            "assumed_service_duration_s": 5.0,
        },
        "item_limit": 2,
        "item_count": 2,
        "hidden_window_user_count": 0,
        "state_counts": {"ACTIVE_BUSINESS": 1, "PENDING_BUSINESS": 1},
        "window_state_counts": {"ACTIVE_BUSINESS": 1, "PENDING_BUSINESS": 1},
        "items": (
            {
                "user_id": "user-0",
                "platform_type": "GROUND_USER",
                "business_state": "ACTIVE_BUSINESS",
                "request_count": 1,
                "active_request_count": 1,
                "recent_request_count": 0,
                "pending_request_count": 0,
                "past_request_count": 0,
                "window_request_count": 1,
                "communication_request_count": 1,
                "compute_request_count": 0,
                "service_classes": ("DATA_TRANSFER",),
                "active_business_types": ("DATA_TRANSFER",),
                "window_business_types": ("DATA_TRANSFER",),
                "current_or_next_business_type": "DATA_TRANSFER",
                "primary_request_id": "req-0",
                "primary_flow_id": "flow-0",
                "primary_target_id": "sat-0",
                "selected_satellite_id": "sat-0",
                "current_or_next_arrival_time": 12.0,
                "last_arrival_time": 12.0,
                "next_arrival_time": None,
                "time_to_next_request_s": None,
                "active_flow_ids": ("flow-0",),
                "recent_flow_ids": (),
                "pending_flow_ids": (),
                "total_input_data_mb": 8.0,
                "total_output_data_mb": 0.0,
                "network_queue_model": "flow-level-queue",
                "compute_execution_model": "none",
            },
            {
                "user_id": "user-1",
                "platform_type": "GROUND_USER",
                "business_state": "PENDING_BUSINESS",
                "request_count": 1,
                "active_request_count": 0,
                "recent_request_count": 0,
                "pending_request_count": 1,
                "past_request_count": 0,
                "window_request_count": 1,
                "communication_request_count": 0,
                "compute_request_count": 1,
                "service_classes": ("COMPUTE_SERVICE",),
                "active_business_types": (),
                "window_business_types": ("COMPUTE_SERVICE",),
                "current_or_next_business_type": "COMPUTE_SERVICE",
                "primary_request_id": "req-1",
                "primary_flow_id": "flow-1",
                "primary_target_id": "sat-1",
                "selected_satellite_id": "sat-1",
                "current_or_next_arrival_time": 18.0,
                "last_arrival_time": None,
                "next_arrival_time": 18.0,
                "time_to_next_request_s": 6.0,
                "active_flow_ids": (),
                "recent_flow_ids": (),
                "pending_flow_ids": ("flow-1",),
                "total_input_data_mb": 64.0,
                "total_output_data_mb": 8.0,
                "network_queue_model": "flow-level-queue",
                "compute_execution_model": "resource-vector-estimator",
            },
        ),
        "model_assumptions": (
            "Business activity is derived from flow-level request arrival records.",
        ),
        "summary_hash": "sha256:traffic-business-activity",
    }


def _node_network_pressure_summary() -> dict[str, object]:
    return {
        "version": "v1",
        "summary_id": "leo_twin.node_network_pressure_summary.v1",
        "source": "BACKEND_RUNTIME_SNAPSHOT",
        "summary_scope": "NODE_NETWORK_PRESSURE_FROM_ROUTE_EDGE_STATES",
        "pressure_model": "FLOW_PRESSURE_ADMISSION_V1",
        "packet_level_simulation": False,
        "frontend_inference_required": False,
        "cursor": 0,
        "limit": 500,
        "next_cursor": 3,
        "has_more": False,
        "node_count": 3,
        "item_count": 3,
        "user_count": 1,
        "satellite_count": 2,
        "route_pressure_route_count": 2,
        "pressure_edge_count": 4,
        "max_projected_utilization": 1.4,
        "max_queue_delay_s": 0.03,
        "max_loss_proxy_rate": 0.12,
        "items": (
            {
                "node_id": "user-0",
                "node_type": "USER",
                "route_count": 2,
                "pressure_edge_count": 2,
                "max_projected_utilization": 1.2,
                "max_queue_delay_s": 0.02,
                "max_loss_proxy_rate": 0.08,
                "service_object_ids": ("sat-0", "sat-1"),
            },
            {
                "node_id": "sat-0",
                "node_type": "SATELLITE",
                "route_count": 1,
                "pressure_edge_count": 1,
                "max_projected_utilization": 1.4,
                "max_queue_delay_s": 0.03,
                "max_loss_proxy_rate": 0.12,
                "service_object_ids": ("user-0",),
            },
            {
                "node_id": "sat-1",
                "node_type": "SATELLITE",
                "route_count": 1,
                "pressure_edge_count": 1,
                "max_projected_utilization": 0.8,
                "max_queue_delay_s": 0.01,
                "max_loss_proxy_rate": 0.02,
                "service_object_ids": ("user-0",),
            },
        ),
        "model_assumptions": (
            "Node pressure is aggregated from route pressure edge states.",
        ),
        "caveats": (
            "Flow-level pressure proxy; no packet-level queue simulation.",
        ),
    }


def _user_configuration_template_validation() -> dict[str, object]:
    return {
        "version": "v1",
        "evidence_id": "sees.user_configuration_template_validation.v1",
        "source": "BACKEND_USER_CONFIGURATION_TEMPLATE_VALIDATOR",
        "schema_id": "sees.user_configuration.v2",
        "validation_scope": "APPROVED_USER_CONFIGURATION_TEMPLATES",
        "template_count": 2,
        "valid_template_count": 2,
        "invalid_template_count": 0,
        "all_templates_valid": True,
        "templates": (
            {
                "id": "default-72",
                "filename": "sees_user_config_72_satellite_demo.yaml",
                "file_exists": True,
                "load_ok": True,
                "validation_ok": True,
                "validation_error_count": 0,
                "template_hash": "sha256:template-72",
            },
            {
                "id": "scale-1200",
                "filename": "sees_user_config_1200_satellite_scale.yaml",
                "file_exists": True,
                "load_ok": True,
                "validation_ok": True,
                "validation_error_count": 0,
                "template_hash": "sha256:template-1200",
            },
        ),
        "model_boundaries": {
            "packet_level_simulation": False,
            "external_simulators": False,
            "forbidden_integrations": ("STK", "EXATA", "AFSIM", "DDS"),
        },
        "notes": (
            "Approved templates validate against user configuration schema v2.",
        ),
        "evidence_hash": "sha256:template-validation",
    }


def _user_configuration_control_surface_evidence() -> dict[str, object]:
    return {
        "version": "v1",
        "evidence_id": "sees.user_configuration_control_surface_evidence.v1",
        "source": "BACKEND_USER_CONFIGURATION_SCHEMA",
        "schema_id": "sees.user_configuration.v2",
        "coverage_status": "COMPLETE",
        "key_field_count": 2,
        "schema_field_count": 2,
        "covered_key_field_count": 2,
        "missing_key_paths": (),
        "wrong_surface_paths": (),
        "duplicate_key_paths": (),
        "duplicate_flat_payload_keys": (),
        "fields": (
            {
                "path": "scenario.satellite_count",
                "flat_payload_key": "satellite_count",
                "section": "scenario",
                "label": "Satellite count",
                "value_type": "integer",
                "editable_surface": "CONTROL_PANEL",
                "current_value": 72,
                "validation_rules": ("min=1",),
            },
            {
                "path": "scenario.duration_seconds",
                "flat_payload_key": "duration_seconds",
                "section": "scenario",
                "label": "Duration seconds",
                "value_type": "number",
                "editable_surface": "CONTROL_PANEL",
                "current_value": 120,
                "validation_rules": ("min=1",),
            },
        ),
        "model_boundaries": {
            "packet_level_simulation": False,
            "external_simulators": False,
            "forbidden_integrations": ("STK", "EXATA", "AFSIM", "DDS"),
        },
        "evidence_hash": "sha256:control-surface",
    }


def _generated_config() -> dict[str, object]:
    return {
        "seed": 7,
        "satellite_count": 72,
        "ground_user_count": 20,
        "compute_node_count": 12,
        "duration_seconds": 120,
        "backend_summary": {
            "traffic_demand_explanation_v1": _traffic_demand_explanation(),
        },
    }


def _traffic_demand_explanation() -> dict[str, object]:
    return {
        "version": "v1",
        "explanation_id": "leo_twin.traffic_demand_explanation.v1",
        "source": "backend_summary.traffic_demand_summary",
        "configured_request_count": 2,
        "explained_request_count": 2,
        "explanation_window_policy": "FULL_CONFIGURED_WINDOW",
        "endpoint_window_policy": (
            "ROUND_ROBIN_ENDPOINT_IDS_CAPPED_AT_512_FOR_SUMMARY_PAYLOAD"
        ),
        "frontend_inference_required": False,
        "request_count": 2,
        "input_flow_count": 2,
        "task_request_count": 1,
        "output_flow_count": 1,
        "communication_only_request_count": 1,
        "compute_service_request_count": 1,
        "active_traffic_classes": ("DATA_TRANSFER", "COMPUTE_SERVICE"),
        "traffic_class_rows": (
            {
                "traffic_class": "DATA_TRANSFER",
                "request_count": 1,
                "input_flow_count": 1,
                "task_request_count": 0,
                "output_flow_count": 0,
                "total_input_data_mb": 2.0,
                "total_output_data_mb": 0.0,
                "destination_types": ("SERVICE_ENDPOINT",),
            },
            {
                "traffic_class": "COMPUTE_SERVICE",
                "request_count": 1,
                "input_flow_count": 1,
                "task_request_count": 1,
                "output_flow_count": 1,
                "total_input_data_mb": 2.0,
                "total_output_data_mb": 0.0,
                "destination_types": ("COMPUTE_NODE",),
            },
        ),
        "arrival_window": {
            "first_arrival_time": 0.0,
            "last_arrival_time": 1.0,
            "duration_seconds": 1.0,
        },
        "priority_summary": {
            "min_priority": 0,
            "max_priority": 0,
            "unique_priorities": (0,),
        },
        "data_volume": {
            "total_input_data_mb": 4.0,
            "total_output_data_mb": 0.0,
            "total_data_mb": 4.0,
        },
        "correlation_summary": {
            "all_compute_services_have_task": True,
            "all_compute_services_have_output_flow": True,
            "packet_level_simulation": False,
            "frontend_inference_required": False,
        },
        "per_user_active_service_state": (
            {
                "user_id": "user-00000",
                "request_count": 1,
                "service_classes": ("COMPUTE_SERVICE",),
                "primary_service_class": "COMPUTE_SERVICE",
                "max_priority": 0,
                "first_arrival_time": 0.0,
                "last_arrival_time": 0.0,
                "flow_ids": ("flow-compute-input",),
                "task_ids": ("task-compute",),
                "output_flow_ids": ("flow-compute-output",),
                "total_input_data_mb": 2.0,
                "total_output_data_mb": 0.0,
            },
            {
                "user_id": "user-00001",
                "request_count": 1,
                "service_classes": ("DATA_TRANSFER",),
                "primary_service_class": "DATA_TRANSFER",
                "max_priority": 0,
                "first_arrival_time": 1.0,
                "last_arrival_time": 1.0,
                "flow_ids": ("flow-data",),
                "task_ids": (),
                "output_flow_ids": (),
                "total_input_data_mb": 2.0,
                "total_output_data_mb": 0.0,
            },
        ),
        "model_assumptions": (
            "Traffic demand explanation summarizes generated flow-level requests only.",
            "Packet-level traffic, stochastic retries, and external simulators are outside this model.",
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


def _route_pressure_evidence() -> dict[str, object]:
    return {
        "version": "v1",
        "source": "BACKEND_METRICS_COLLECTOR",
        "evidence_id": "leo_twin.route_pressure_evidence.v1",
        "pressure_model": "FLOW_PRESSURE_ADMISSION_V1",
        "route_source": "ROUTE_UPDATE",
        "packet_level_simulation": False,
        "route_count": 2,
        "item_limit": 64,
        "item_count": 2,
        "hidden_route_count": 0,
        "pressure_admission_rejected_count": 1,
        "topology_blocked_count": 0,
        "queued_route_count": 1,
        "saturated_route_count": 1,
        "pressure_edge_count": 2,
        "edge_item_limit": 128,
        "edge_item_count": 2,
        "hidden_edge_count": 0,
        "pressure_admission_rejected_edge_count": 0,
        "queued_edge_count": 1,
        "saturated_edge_count": 1,
        "max_edge_projected_utilization": 1.25,
        "max_edge_queue_delay_s": 0.02,
        "max_edge_loss_proxy_rate": 0.1,
        "edge_items": (
            {
                "route_id": "route-0",
                "flow_id": "flow-0",
                "edge_id": "user-0->sat-0",
                "pressure_state": "QUEUED",
                "projected_utilization": 0.95,
                "queue_delay_s": 0.01,
                "loss_proxy_rate": 0.05,
                "packet_level_simulation": False,
            },
            {
                "route_id": "route-1",
                "flow_id": "flow-1",
                "edge_id": "user-1->sat-1",
                "pressure_state": "SATURATED",
                "projected_utilization": 1.25,
                "queue_delay_s": 0.02,
                "loss_proxy_rate": 0.1,
                "packet_level_simulation": False,
            },
        ),
        "items": (
            {
                "route_id": "route-0",
                "flow_id": "flow-0",
                "pressure_state": "QUEUED",
                "blocked_reason": "demand_exceeds_capacity",
                "queue_over_demand_mbps": 12.0,
                "pressure_loss_rate": 0.15,
            },
            {
                "route_id": "route-1",
                "flow_id": "flow-1",
                "pressure_state": "SATURATED",
                "blocked_reason": "flow_pressure_admission_limit",
                "queue_over_demand_mbps": 20.0,
                "pressure_loss_rate": 0.25,
            },
        ),
    }


def _route_pressure_export_policy() -> dict[str, object]:
    return {
        "version": "v1",
        "source": "BACKEND_RUNTIME_EXPORT",
        "policy": "EXPORT_ROUTE_PRESSURE_EVIDENCE_WINDOW",
        "route_pressure_evidence_source": "route_pressure_evidence_v1",
        "route_pressure_evidence_limit": 64,
        "route_count": 2,
        "exported_item_count": 2,
        "hidden_route_count": 0,
        "packet_level_simulation": False,
        "event_replay": False,
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
