from __future__ import annotations

import json
from pathlib import Path

from examples.integration_demo.config import DemoConfig
from examples.integration_demo.control_plane import DemoControlPlane
from examples.integration_demo.runtime import run_integration_demo
from leo_twin.services.detail_pagination_contract import DETAIL_ENDPOINT_MAX_LIMIT
from leo_twin.services.result_package_contract import (
    RUNTIME_EXPORT_NETWORK_KPI_BENCHMARK_VALIDATION_V1_ID,
    RUNTIME_EXPORT_BENCHMARK_ACCEPTANCE_BINDING_V1_ID,
    RUNTIME_EXPORT_NETWORK_KPI_FORMULA_EVIDENCE_V1_ID,
    RUNTIME_EXPORT_NETWORK_TEMPORAL_PRESSURE_EVIDENCE_V1_ID,
    RUNTIME_EXPORT_NETWORK_KPI_VARIATION_EXPLANATION_V1_ID,
    RUNTIME_EXPORT_NETWORK_KPI_DYNAMIC_STATUS_V1_ID,
    RUNTIME_EXPORT_NODE_NETWORK_PRESSURE_SUMMARY_V1_ID,
    RUNTIME_EXPORT_RUNTIME_KPI_MOVEMENT_SUMMARY_V1_ID,
    RUNTIME_EXPORT_NETWORK_FLOW_LIFECYCLE_SUMMARY_V1_ID,
    RUNTIME_EXPORT_SERVICE_LIFECYCLE_STAGE_SUMMARY_V1_ID,
    RUNTIME_EXPORT_TRAFFIC_DEMAND_EXPLANATION_V1_ID,
    RUNTIME_EXPORT_TRAFFIC_BUSINESS_ACTIVITY_WINDOW_V1_ID,
    RUNTIME_EXPORT_V2_EXECUTABLE_READINESS_V1_ID,
    RUNTIME_EXPORT_USER_CONFIGURATION_TEMPLATE_VALIDATION_V1_ID,
    RUNTIME_EXPORT_USER_CONFIGURATION_CONTROL_SURFACE_EVIDENCE_V1_ID,
    RUNTIME_EXPORT_PACKAGE_ACCEPTANCE_REPORT_V1_ID,
    RUNTIME_EXPORT_PACKAGE_AUDIT_INDEX_V1_ID,
    RUNTIME_EXPORT_REPRODUCIBILITY_BOUNDARY_V1_ID,
    RUNTIME_EXPORT_ROUTE_COMPARISON_REVIEW_REPORT_V1_ID,
    RUNTIME_EXPORT_SCENARIO_REVIEW_BUNDLE_V1_ID,
    RUNTIME_EXPORT_SCENARIO_REVIEW_CHECKLIST_V1_ID,
    RUNTIME_EXPORT_SCENARIO_REVIEW_CHECKLIST_TEMPLATE_COMPARISON_V1_ID,
    RUNTIME_EXPORT_SERVICE_TRACE_COMPARISON_REVIEW_REPORT_V1_ID,
    RUNTIME_REPRODUCIBILITY_MANIFEST_V1_ID,
    summarize_result_package_record_v1,
)


def test_runtime_export_package_satisfies_result_package_contract_v1(
    tmp_path: Path,
) -> None:
    control_plane = DemoControlPlane.from_result(
        run_integration_demo(_base_demo_config()),
        config_output_path=tmp_path / "sees_control.yaml",
        generated_config_output_path=tmp_path / "generated_full_system_demo.json",
    )

    output_root = tmp_path / "exports"
    package = control_plane.export_runtime_package(output_root)
    summary = summarize_result_package_record_v1(package)
    package_dir = Path(str(package["package_dir"]))

    assert summary["package_complete"] is True
    assert summary["manifest_id"] == RUNTIME_REPRODUCIBILITY_MANIFEST_V1_ID
    assert summary["missing_required_files"] == ()
    assert summary["present_required_files"] == (
        "config_snapshot.json",
        "events.jsonl",
        "metrics.csv",
        "summary.json",
        "manifest.json",
    )
    assert (package_dir / "config_snapshot.json").exists()
    assert (package_dir / "events.jsonl").exists()
    assert (package_dir / "metrics.csv").exists()
    assert (package_dir / "summary.json").exists()
    assert (package_dir / "manifest.json").exists()
    assert (package_dir / "diagnostics_bundle_v1.json").exists()
    assert (package_dir / "review_summary_v1.json").exists()
    assert (package_dir / "route_detail_index_v1.json").exists()
    assert (package_dir / "route_pressure_evidence_v1.json").exists()
    assert (package_dir / "node_network_pressure_summary_v1.json").exists()
    assert (package_dir / "compute_resource_pool_summary_v1.json").exists()
    assert (package_dir / "v2_executable_readiness_v1.json").exists()
    assert (package_dir / "network_kpi_benchmark_validation_v1.json").exists()
    assert (package_dir / "benchmark_acceptance_binding_v1.json").exists()
    assert (package_dir / "network_kpi_formula_evidence_v1.json").exists()
    assert (package_dir / "network_temporal_pressure_evidence_v1.json").exists()
    assert (package_dir / "network_kpi_variation_explanation_v1.json").exists()
    assert (package_dir / "network_kpi_dynamic_status_v1.json").exists()
    assert (package_dir / "runtime_kpi_movement_summary_v1.json").exists()
    assert (package_dir / "network_flow_lifecycle_summary_v1.json").exists()
    assert (package_dir / "service_lifecycle_stage_summary_v1.json").exists()
    assert (package_dir / "user_configuration_template_validation_v1.json").exists()
    assert (package_dir / "user_configuration_control_surface_evidence_v1.json").exists()
    assert (package_dir / "traffic_demand_explanation_v1.json").exists()
    assert (package_dir / "traffic_business_activity_window_v1.json").exists()
    assert (package_dir / "user_service_request_summary_v2.json").exists()
    assert (package_dir / "service_lifecycle_trace_v2.json").exists()
    assert (package_dir / "scenario_review_bundle_v1.json").exists()
    assert (package_dir / "export_package_audit_index_v1.json").exists()
    assert (package_dir / "package_handoff_report_v1.md").exists()
    filenames = {str(record["filename"]) for record in package["files"]}
    assert "service_lifecycle_trace_v2.json" in filenames
    assert "route_detail_index_v1.json" in filenames
    assert "route_pressure_evidence_v1.json" in filenames
    assert "node_network_pressure_summary_v1.json" in filenames
    assert "compute_resource_pool_summary_v1.json" in filenames
    assert "v2_executable_readiness_v1.json" in filenames
    assert "review_summary_v1.json" in filenames
    assert "diagnostics_bundle_v1.json" in filenames
    assert "network_kpi_benchmark_validation_v1.json" in filenames
    assert "benchmark_acceptance_binding_v1.json" in filenames
    assert "network_kpi_formula_evidence_v1.json" in filenames
    assert "network_temporal_pressure_evidence_v1.json" in filenames
    assert "network_kpi_variation_explanation_v1.json" in filenames
    assert "network_kpi_dynamic_status_v1.json" in filenames
    assert "runtime_kpi_movement_summary_v1.json" in filenames
    assert "network_flow_lifecycle_summary_v1.json" in filenames
    assert "service_lifecycle_stage_summary_v1.json" in filenames
    assert "user_configuration_template_validation_v1.json" in filenames
    assert "user_configuration_control_surface_evidence_v1.json" in filenames
    assert "traffic_demand_explanation_v1.json" in filenames
    assert "traffic_business_activity_window_v1.json" in filenames
    assert "user_service_request_summary_v2.json" in filenames
    assert "scenario_review_bundle_v1.json" in filenames
    assert "export_package_audit_index_v1.json" in filenames
    assert "package_handoff_report_v1.md" in filenames

    manifest = json.loads((package_dir / "manifest.json").read_text(encoding="utf-8"))
    config_snapshot = json.loads(
        (package_dir / "config_snapshot.json").read_text(encoding="utf-8")
    )
    service_lifecycle_trace = json.loads(
        (package_dir / "service_lifecycle_trace_v2.json").read_text(encoding="utf-8")
    )
    route_detail_index = json.loads(
        (package_dir / "route_detail_index_v1.json").read_text(encoding="utf-8")
    )
    route_pressure_evidence = json.loads(
        (package_dir / "route_pressure_evidence_v1.json").read_text(encoding="utf-8")
    )
    node_network_pressure_summary = json.loads(
        (package_dir / "node_network_pressure_summary_v1.json").read_text(
            encoding="utf-8"
        )
    )
    compute_resource_pool_summary = json.loads(
        (package_dir / "compute_resource_pool_summary_v1.json").read_text(
            encoding="utf-8"
        )
    )
    v2_executable_readiness = json.loads(
        (package_dir / "v2_executable_readiness_v1.json").read_text(
            encoding="utf-8"
        )
    )
    review_summary = json.loads(
        (package_dir / "review_summary_v1.json").read_text(encoding="utf-8")
    )
    diagnostics_bundle = json.loads(
        (package_dir / "diagnostics_bundle_v1.json").read_text(encoding="utf-8")
    )
    network_kpi_benchmark_validation = json.loads(
        (package_dir / "network_kpi_benchmark_validation_v1.json").read_text(
            encoding="utf-8"
        )
    )
    benchmark_acceptance_binding = json.loads(
        (package_dir / "benchmark_acceptance_binding_v1.json").read_text(
            encoding="utf-8"
        )
    )
    network_kpi_formula_evidence = json.loads(
        (package_dir / "network_kpi_formula_evidence_v1.json").read_text(
            encoding="utf-8"
        )
    )
    network_temporal_pressure_evidence = json.loads(
        (package_dir / "network_temporal_pressure_evidence_v1.json").read_text(
            encoding="utf-8"
        )
    )
    network_kpi_variation_explanation = json.loads(
        (package_dir / "network_kpi_variation_explanation_v1.json").read_text(
            encoding="utf-8"
        )
    )
    network_kpi_dynamic_status = json.loads(
        (package_dir / "network_kpi_dynamic_status_v1.json").read_text(
            encoding="utf-8"
        )
    )
    runtime_kpi_movement_summary = json.loads(
        (package_dir / "runtime_kpi_movement_summary_v1.json").read_text(
            encoding="utf-8"
        )
    )
    network_flow_lifecycle_summary = json.loads(
        (package_dir / "network_flow_lifecycle_summary_v1.json").read_text(
            encoding="utf-8"
        )
    )
    service_lifecycle_stage_summary = json.loads(
        (package_dir / "service_lifecycle_stage_summary_v1.json").read_text(
            encoding="utf-8"
        )
    )
    user_configuration_template_validation = json.loads(
        (package_dir / "user_configuration_template_validation_v1.json").read_text(
            encoding="utf-8"
        )
    )
    user_configuration_control_surface_evidence = json.loads(
        (package_dir / "user_configuration_control_surface_evidence_v1.json").read_text(
            encoding="utf-8"
        )
    )
    traffic_demand_explanation = json.loads(
        (package_dir / "traffic_demand_explanation_v1.json").read_text(
            encoding="utf-8"
        )
    )
    traffic_business_activity_window = json.loads(
        (package_dir / "traffic_business_activity_window_v1.json").read_text(
            encoding="utf-8"
        )
    )
    user_service_request_summary = json.loads(
        (package_dir / "user_service_request_summary_v2.json").read_text(
            encoding="utf-8"
        )
    )
    scenario_review_bundle = json.loads(
        (package_dir / "scenario_review_bundle_v1.json").read_text(
            encoding="utf-8"
        )
    )
    audit_index = json.loads(
        (package_dir / "export_package_audit_index_v1.json").read_text(
            encoding="utf-8"
        )
    )
    initial_handoff_report = (package_dir / "package_handoff_report_v1.md").read_text(
        encoding="utf-8"
    )

    assert manifest["manifest_id"] == RUNTIME_REPRODUCIBILITY_MANIFEST_V1_ID
    assert manifest["manifest_hash"] == summary["manifest_hash"]
    assert config_snapshot["type"] == "RUNTIME_CONFIG_SNAPSHOT"
    assert config_snapshot["status"]["reproducibility_manifest_v1"] == manifest
    assert config_snapshot["status"]["export_status_policy"] == (
        "STABLE_RUNTIME_STATUS_WITHOUT_STREAM_DIAGNOSTICS"
    )
    assert config_snapshot["user_configuration_control_surface_evidence_v1"] == (
        config_snapshot["status"]["user_configuration_control_surface_evidence_v1"]
    )
    assert config_snapshot["user_configuration_control_surface_evidence_v1"][
        "coverage_status"
    ] == "COMPLETE"
    reproducibility_boundary = config_snapshot["status"][
        "runtime_export_reproducibility_boundary_v1"
    ]
    assert reproducibility_boundary["boundary_id"] == (
        RUNTIME_EXPORT_REPRODUCIBILITY_BOUNDARY_V1_ID
    )
    assert reproducibility_boundary["restore_scope"] == "CONFIG_ONLY"
    assert reproducibility_boundary["event_replay_restore"] is False
    assert reproducibility_boundary["recompute_on_read"] is False
    assert reproducibility_boundary["package_mutation_on_read"] is False
    assert "NO_LIVE_EVENT_REPLAY_RESTORE" in reproducibility_boundary[
        "boundary_conditions"
    ]
    assert manifest["runtime_export_reproducibility_boundary_v1"] == (
        reproducibility_boundary
    )
    assert service_lifecycle_trace["type"] == "SERVICE_LIFECYCLE_TRACE_EXPORT_V2"
    assert service_lifecycle_trace["summary"] == config_snapshot["status"][
        "service_lifecycle_trace_v2"
    ]
    service_trace_export_policy = config_snapshot["status"][
        "runtime_export_service_trace_policy_v1"
    ]
    assert service_trace_export_policy["policy"] == "EXPORT_SERVICE_TRACE_WINDOW"
    assert service_trace_export_policy["service_trace_limit"] == DETAIL_ENDPOINT_MAX_LIMIT
    assert service_trace_export_policy["exported_trace_count"] == (
        service_lifecycle_trace["summary"]["trace_count"]
    )
    assert service_trace_export_policy["hidden_trace_count"] == (
        service_lifecycle_trace["summary"]["hidden_trace_count"]
    )
    assert service_lifecycle_trace["service_trace_export_policy"] == (
        service_trace_export_policy
    )
    route_summary_status = config_snapshot["status"]["route_explanation_summary_v1"]
    route_export_policy = config_snapshot["status"][
        "runtime_export_route_detail_policy_v1"
    ]
    route_trust_status = config_snapshot["status"]["route_provenance_trust_summary_v1"]
    assert route_trust_status["trust_id"] == "leo_twin.route_provenance_trust.v1"
    assert route_summary_status["limit"] == DETAIL_ENDPOINT_MAX_LIMIT
    assert route_export_policy["policy"] == "EXPORT_ROUTE_DETAIL_INDEX_WINDOW"
    assert route_export_policy["route_detail_limit"] == DETAIL_ENDPOINT_MAX_LIMIT
    assert route_export_policy["indexed_route_count"] == len(
        route_summary_status["items"]
    )
    assert route_detail_index["type"] == "RUNTIME_EXPORT_ROUTE_DETAIL_INDEX_V1"
    assert route_detail_index["route_detail_export_policy"] == route_export_policy
    assert route_detail_index["route_trust"]["trust_id"] == route_trust_status[
        "trust_id"
    ]
    assert route_detail_index["route_summary"]["route_count"] == route_summary_status[
        "route_count"
    ]
    assert route_detail_index["route_summary"]["indexed_route_count"] == len(
        route_summary_status["items"]
    )
    assert route_detail_index["route_detail_index_hash"].startswith("sha256:")
    assert route_pressure_evidence["type"] == "RUNTIME_EXPORT_ROUTE_PRESSURE_EVIDENCE_V1"
    assert route_pressure_evidence["summary"] == config_snapshot["status"][
        "route_pressure_evidence_v1"
    ]
    assert route_pressure_evidence["route_pressure_evidence_export_policy"] == (
        config_snapshot["status"]["runtime_export_route_pressure_evidence_policy_v1"]
    )
    assert node_network_pressure_summary["artifact_id"] == (
        RUNTIME_EXPORT_NODE_NETWORK_PRESSURE_SUMMARY_V1_ID
    )
    assert node_network_pressure_summary["summary"] == (
        config_snapshot["status"]["node_network_pressure_summary_v1"]
    )
    assert node_network_pressure_summary["evidence"]["evidence_present"] is True
    assert compute_resource_pool_summary["type"] == (
        "RUNTIME_EXPORT_COMPUTE_RESOURCE_POOL_SUMMARY_V1"
    )
    assert compute_resource_pool_summary["artifact_id"] == (
        "leo_twin.runtime_export_compute_resource_pool_summary.v1"
    )
    assert compute_resource_pool_summary["source"] == "BACKEND_RUNTIME_STATUS"
    assert compute_resource_pool_summary["compute_resource_pool_summary"] == (
        config_snapshot["status"]["compute_resource_pool_summary_v1"]
    )
    assert compute_resource_pool_summary["evidence"]["summary_hash"] == (
        config_snapshot["status"]["compute_resource_pool_summary_v1"][
            "summary_hash"
        ]
    )
    assert compute_resource_pool_summary["evidence"]["packet_level_simulation"] is False
    assert (
        compute_resource_pool_summary["evidence"]["frontend_inference_required"]
        is False
    )
    assert compute_resource_pool_summary["artifact_hash"].startswith("sha256:")
    assert review_summary["type"] == "RUNTIME_EXPORT_REVIEW_SUMMARY_V1"
    assert review_summary["review_status"] == "REVIEW_READY"
    assert review_summary["route_trust"]["trust_id"] == route_trust_status["trust_id"]
    assert review_summary["route_trust"]["route_model"] == (
        route_trust_status["route_model"]
    )
    assert review_summary["route_trust"]["packet_level_simulation"] is False
    assert review_summary["route_trust"]["all_pairs_computation"] is False
    assert review_summary["route_pressure_evidence"]["evidence_present"] is True
    assert review_summary["route_pressure_evidence"]["route_count"] == (
        route_pressure_evidence["summary"]["route_count"]
    )
    assert review_summary["route_pressure_evidence"]["pressure_edge_count"] == (
        route_pressure_evidence["summary"]["pressure_edge_count"]
    )
    assert review_summary["route_pressure_evidence"][
        "pressure_admission_rejected_count"
    ] == route_pressure_evidence["summary"].get(
        "pressure_admission_rejected_count", 0
    )
    assert review_summary["route_pressure_evidence"]["packet_level_simulation"] is False
    assert review_summary["node_network_pressure_summary"]["evidence_present"] is True
    assert review_summary["node_network_pressure_summary"]["node_count"] == (
        node_network_pressure_summary["evidence"]["node_count"]
    )
    assert review_summary["node_network_pressure_summary"]["pressure_edge_count"] == (
        node_network_pressure_summary["evidence"]["pressure_edge_count"]
    )
    assert review_summary["node_network_pressure_summary"][
        "frontend_inference_required"
    ] is False
    assert review_summary["artifacts"]["route_pressure_evidence_exported"] is True
    assert review_summary["artifacts"][
        "node_network_pressure_summary_exported"
    ] is True
    assert review_summary["network_kpi_benchmark_validation"][
        "validation_id"
    ] == "leo_twin.network_kpi_benchmark_validation.v1"
    assert review_summary["network_kpi_benchmark_validation"][
        "evidence_present"
    ] is True
    assert review_summary["network_kpi_benchmark_validation"][
        "failed_check_count"
    ] == 0
    assert review_summary["network_kpi_formula_evidence"][
        "evidence_present"
    ] is True
    assert review_summary["network_kpi_formula_evidence"][
        "formula_evidence_status"
    ] in {
        "FORMULA_AND_TIME_EVIDENCE_READY",
        "FORMULA_READY",
        "FORMULA_READY_FLAT_SERIES",
        "FORMULA_READY_INSUFFICIENT_SERIES",
    }
    assert review_summary["network_temporal_pressure_evidence"][
        "evidence_present"
    ] is True
    assert review_summary["network_temporal_pressure_evidence"]["status"] in {
        "OBSERVED",
        "MISSING_RUNTIME_VALUES",
    }
    assert review_summary["network_kpi_variation_explanation"][
        "evidence_present"
    ] is True
    assert review_summary["network_kpi_variation_explanation"][
        "explanation_status"
    ] in {
        "TIME_VARIATION_EXPLAINED",
        "FLAT_UNDER_ACTIVITY_EXPLAINED",
        "FLAT_NO_ACTIVITY_EXPLAINED",
        "INSUFFICIENT_SERIES",
    }
    assert review_summary["network_kpi_dynamic_status"][
        "evidence_present"
    ] is True
    assert review_summary["network_kpi_dynamic_status"]["dynamic_status"] in {
        "DYNAMIC",
        "PARTIALLY_DYNAMIC",
        "FLAT_WITH_ACTIVITY",
        "FLAT_NO_ACTIVITY",
        "INSUFFICIENT_SERIES",
    }
    assert review_summary["reproducibility"]["manifest_hash"] == manifest[
        "manifest_hash"
    ]
    assert review_summary["reproducibility"]["boundary_hash"] == (
        reproducibility_boundary["boundary_hash"]
    )
    assert review_summary["reproducibility_boundary"] == reproducibility_boundary
    assert "review_summary_v1.json" in review_summary["artifacts"][
        "artifact_filenames"
    ]
    assert "route_detail_index_v1.json" in review_summary["artifacts"][
        "artifact_filenames"
    ]
    assert "diagnostics_bundle_v1.json" in review_summary["artifacts"][
        "artifact_filenames"
    ]
    assert "compute_resource_pool_summary_v1.json" in review_summary["artifacts"][
        "artifact_filenames"
    ]
    assert review_summary["compute_resource_pool_summary"][
        "evidence_present"
    ] is True
    assert review_summary["compute_resource_pool_summary"]["summary_hash"] == (
        compute_resource_pool_summary["evidence"]["summary_hash"]
    )
    assert review_summary["compute_resource_pool_summary"][
        "dimension_count"
    ] == compute_resource_pool_summary["evidence"]["dimension_count"]
    assert review_summary["artifacts"][
        "compute_resource_pool_summary_exported"
    ] is True
    assert v2_executable_readiness["artifact_id"] == (
        RUNTIME_EXPORT_V2_EXECUTABLE_READINESS_V1_ID
    )
    assert v2_executable_readiness["readiness"] == (
        config_snapshot["status"]["v2_executable_readiness_v1"]
    )
    assert v2_executable_readiness["evidence"]["evidence_present"] is True
    assert v2_executable_readiness["evidence"]["packet_level_simulation"] is False
    assert "NO_READINESS_RECOMPUTE" in v2_executable_readiness[
        "boundary_conditions"
    ]
    assert review_summary["v2_executable_readiness"]["evidence_hash"] == (
        v2_executable_readiness["evidence"]["evidence_hash"]
    )
    assert review_summary["v2_executable_readiness"]["failed_gate_count"] == (
        v2_executable_readiness["evidence"]["failed_gate_count"]
    )
    assert review_summary["artifacts"]["v2_executable_readiness_exported"] is True
    assert review_summary["artifacts"][
        "network_kpi_benchmark_validation_exported"
    ] is True
    assert review_summary["artifacts"][
        "benchmark_acceptance_binding_exported"
    ] is True
    assert review_summary["artifacts"][
        "network_kpi_formula_evidence_exported"
    ] is True
    assert review_summary["artifacts"][
        "network_temporal_pressure_evidence_exported"
    ] is True
    assert review_summary["artifacts"][
        "network_kpi_variation_explanation_exported"
    ] is True
    assert review_summary["artifacts"][
        "network_kpi_dynamic_status_exported"
    ] is True
    assert review_summary["artifacts"]["runtime_kpi_movement_summary_exported"] is True
    assert review_summary["network_flow_lifecycle_summary"]["evidence_present"] is True
    assert review_summary["network_flow_lifecycle_summary"]["evidence_hash"] == (
        network_flow_lifecycle_summary["evidence"]["evidence_hash"]
    )
    assert review_summary["artifacts"]["network_flow_lifecycle_summary_exported"] is True
    assert review_summary["service_lifecycle_stage_summary"]["evidence_present"] is True
    assert review_summary["service_lifecycle_stage_summary"]["evidence_hash"] == (
        service_lifecycle_stage_summary["evidence"]["evidence_hash"]
    )
    assert review_summary["artifacts"][
        "service_lifecycle_stage_summary_exported"
    ] is True
    assert review_summary["user_configuration_template_validation"][
        "evidence_present"
    ] is True
    assert review_summary["user_configuration_template_validation"][
        "validation_status"
    ] == "ALL_TEMPLATES_VALID"
    assert review_summary["user_configuration_template_validation"][
        "invalid_template_count"
    ] == 0
    assert review_summary["artifacts"][
        "user_configuration_template_validation_exported"
    ] is True
    assert review_summary["user_configuration_control_surface_evidence"][
        "evidence_present"
    ] is True
    assert review_summary["user_configuration_control_surface_evidence"][
        "coverage_status"
    ] == "COMPLETE"
    assert review_summary["user_configuration_control_surface_evidence"][
        "key_field_count"
    ] == config_snapshot["user_configuration_control_surface_evidence_v1"][
        "key_field_count"
    ]
    assert review_summary["artifacts"][
        "user_configuration_control_surface_evidence_exported"
    ] is True
    assert review_summary["traffic_demand_explanation"]["evidence_present"] is True
    assert review_summary["traffic_demand_explanation"][
        "frontend_inference_required"
    ] is False
    assert review_summary["artifacts"][
        "traffic_demand_explanation_exported"
    ] is True
    assert traffic_business_activity_window["artifact_id"] == (
        RUNTIME_EXPORT_TRAFFIC_BUSINESS_ACTIVITY_WINDOW_V1_ID
    )
    assert traffic_business_activity_window["activity_window"] == (
        config_snapshot["status"]["traffic_business_activity_window_v1"]
    )
    assert traffic_business_activity_window["evidence"]["evidence_present"] is True
    assert traffic_business_activity_window["evidence"][
        "packet_level_simulation"
    ] is False
    assert "NO_TRAFFIC_REGENERATION" in traffic_business_activity_window[
        "boundary_conditions"
    ]
    assert review_summary["traffic_business_activity_window"]["evidence_hash"] == (
        traffic_business_activity_window["evidence"]["evidence_hash"]
    )
    assert review_summary["traffic_business_activity_window"]["request_count"] == (
        traffic_business_activity_window["evidence"]["request_count"]
    )
    assert review_summary["artifacts"][
        "traffic_business_activity_window_exported"
    ] is True
    assert diagnostics_bundle["type"] == "RUNTIME_EXPORT_DIAGNOSTICS_BUNDLE_V1"
    assert diagnostics_bundle["package"]["package_complete"] is True
    assert diagnostics_bundle["artifact_health"]["missing_required_filenames"] == []
    artifact_browser = diagnostics_bundle["artifact_browser_index_v1"]
    assert artifact_browser["index_id"] == (
        "leo_twin.runtime_export_artifact_browser_index.v1"
    )
    assert artifact_browser["index_scope"] == "RESULT_PACKAGE_ARTIFACT_BROWSER"
    assert artifact_browser["default_focus_filename"] == "scenario_review_bundle_v1.json"
    assert artifact_browser["missing_required_count"] == 0
    assert artifact_browser["browser_hash"].startswith("sha256:")
    browser_categories = {
        category["category"]: category for category in artifact_browser["categories"]
    }
    assert browser_categories["NETWORK_KPI_EVIDENCE"]["present_count"] >= 3
    assert browser_categories["COMPUTE_RESOURCE_EVIDENCE"]["present_count"] == 1
    compute_browser_item = next(
        item
        for item in artifact_browser["items"]
        if item["filename"] == "compute_resource_pool_summary_v1.json"
    )
    assert compute_browser_item["category"] == "COMPUTE_RESOURCE_EVIDENCE"
    assert compute_browser_item["present"] is True
    assert compute_browser_item["default_json_pointer"] == (
        "/compute_resource_pool_summary/dimensions"
    )
    variation_browser_item = next(
        item
        for item in artifact_browser["items"]
        if item["filename"] == "network_kpi_variation_explanation_v1.json"
    )
    assert variation_browser_item["category"] == "NETWORK_KPI_EVIDENCE"
    assert variation_browser_item["present"] is True
    assert variation_browser_item["default_json_pointer"] == "/evidence"
    dynamic_status_browser_item = next(
        item
        for item in artifact_browser["items"]
        if item["filename"] == "network_kpi_dynamic_status_v1.json"
    )
    assert dynamic_status_browser_item["category"] == "NETWORK_KPI_EVIDENCE"
    assert dynamic_status_browser_item["present"] is True
    assert dynamic_status_browser_item["default_json_pointer"] == "/dynamic_status"
    benchmark_acceptance_browser_item = next(
        item
        for item in artifact_browser["items"]
        if item["filename"] == "benchmark_acceptance_binding_v1.json"
    )
    assert benchmark_acceptance_browser_item["category"] == "AUDIT_HANDOFF"
    assert benchmark_acceptance_browser_item["present"] is True
    assert benchmark_acceptance_browser_item["default_json_pointer"] == (
        "/expected_range_results"
    )
    control_surface_browser_item = next(
        item
        for item in artifact_browser["items"]
        if item["filename"] == "user_configuration_control_surface_evidence_v1.json"
    )
    assert control_surface_browser_item["category"] == "CORE_REPRODUCIBILITY"
    assert control_surface_browser_item["present"] is True
    assert control_surface_browser_item["default_json_pointer"] == (
        "/control_surface_evidence/fields"
    )
    pressure_browser_item = next(
        item
        for item in artifact_browser["items"]
        if item["filename"] == "route_pressure_evidence_v1.json"
    )
    assert pressure_browser_item["category"] == "ROUTE_SERVICE_EVIDENCE"
    assert pressure_browser_item["present"] is True
    assert pressure_browser_item["default_json_pointer"] == "/summary/items"
    node_pressure_browser_item = next(
        item
        for item in artifact_browser["items"]
        if item["filename"] == "node_network_pressure_summary_v1.json"
    )
    assert node_pressure_browser_item["category"] == "ROUTE_SERVICE_EVIDENCE"
    assert node_pressure_browser_item["present"] is True
    assert node_pressure_browser_item["default_json_pointer"] == "/summary/items"
    assert diagnostics_bundle["route_trust"]["trust_id"] == route_trust_status[
        "trust_id"
    ]
    assert diagnostics_bundle["route_trust"]["trust_status"] == route_trust_status[
        "trust_status"
    ]
    assert diagnostics_bundle["route_trust"]["evidence_present"] is True
    assert diagnostics_bundle["route_pressure_evidence"]["evidence_hash"] == (
        review_summary["route_pressure_evidence"]["evidence_hash"]
    )
    assert diagnostics_bundle["route_pressure_evidence"]["evidence_present"] is True
    assert diagnostics_bundle["route_pressure_evidence"]["event_replay"] is False
    assert diagnostics_bundle["node_network_pressure_summary"]["evidence_hash"] == (
        review_summary["node_network_pressure_summary"]["evidence_hash"]
    )
    assert diagnostics_bundle["node_network_pressure_summary"][
        "evidence_present"
    ] is True
    assert diagnostics_bundle["compute_resource_pool_summary"]["evidence_hash"] == (
        review_summary["compute_resource_pool_summary"]["evidence_hash"]
    )
    assert diagnostics_bundle["compute_resource_pool_summary"][
        "evidence_present"
    ] is True
    assert diagnostics_bundle["network_kpi_benchmark_validation"][
        "validation_hash"
    ] == review_summary["network_kpi_benchmark_validation"]["validation_hash"]
    assert diagnostics_bundle["network_kpi_benchmark_validation"][
        "failed_check_count"
    ] == 0
    assert diagnostics_bundle["network_kpi_formula_evidence"][
        "evidence_hash"
    ] == review_summary["network_kpi_formula_evidence"]["evidence_hash"]
    assert diagnostics_bundle["network_kpi_formula_evidence"][
        "evidence_present"
    ] is True
    assert diagnostics_bundle["network_temporal_pressure_evidence"][
        "evidence_hash"
    ] == review_summary["network_temporal_pressure_evidence"]["evidence_hash"]
    assert diagnostics_bundle["network_temporal_pressure_evidence"][
        "evidence_present"
    ] is True
    assert diagnostics_bundle["network_flow_lifecycle_summary"]["evidence_hash"] == (
        review_summary["network_flow_lifecycle_summary"]["evidence_hash"]
    )
    assert diagnostics_bundle["service_lifecycle_stage_summary"]["evidence_hash"] == (
        review_summary["service_lifecycle_stage_summary"]["evidence_hash"]
    )
    assert diagnostics_bundle["service_lifecycle_stage_summary"][
        "evidence_present"
    ] is True
    assert diagnostics_bundle["network_kpi_variation_explanation"][
        "evidence_hash"
    ] == review_summary["network_kpi_variation_explanation"]["evidence_hash"]
    assert diagnostics_bundle["network_kpi_dynamic_status"][
        "evidence_hash"
    ] == review_summary["network_kpi_dynamic_status"]["evidence_hash"]
    assert diagnostics_bundle["network_kpi_dynamic_status"][
        "evidence_present"
    ] is True
    assert diagnostics_bundle["runtime_kpi_movement_summary"]["evidence_hash"] == (
        review_summary["runtime_kpi_movement_summary"]["evidence_hash"]
    )
    assert diagnostics_bundle["network_kpi_variation_explanation"][
        "evidence_present"
    ] is True
    assert diagnostics_bundle["user_configuration_template_validation"][
        "evidence_hash"
    ] == review_summary["user_configuration_template_validation"]["evidence_hash"]
    assert diagnostics_bundle["user_configuration_template_validation"][
        "validation_status"
    ] == "ALL_TEMPLATES_VALID"
    assert diagnostics_bundle["user_configuration_control_surface_evidence"][
        "evidence_hash"
    ] == review_summary["user_configuration_control_surface_evidence"][
        "evidence_hash"
    ]
    assert diagnostics_bundle["user_configuration_control_surface_evidence"][
        "coverage_status"
    ] == "COMPLETE"
    assert diagnostics_bundle["user_configuration_control_surface_evidence"][
        "evidence_present"
    ] is True
    assert diagnostics_bundle["traffic_demand_explanation"]["evidence_hash"] == (
        review_summary["traffic_demand_explanation"]["evidence_hash"]
    )
    assert diagnostics_bundle["traffic_demand_explanation"][
        "evidence_present"
    ] is True
    assert diagnostics_bundle["traffic_business_activity_window"]["evidence_hash"] == (
        review_summary["traffic_business_activity_window"]["evidence_hash"]
    )
    assert diagnostics_bundle["traffic_business_activity_window"][
        "evidence_present"
    ] is True
    assert diagnostics_bundle["v2_executable_readiness"]["evidence_hash"] == (
        review_summary["v2_executable_readiness"]["evidence_hash"]
    )
    assert diagnostics_bundle["v2_executable_readiness"]["evidence_present"] is True
    assert diagnostics_bundle["reproducibility"]["manifest_hash"] == manifest[
        "manifest_hash"
    ]
    assert diagnostics_bundle["reproducibility"]["boundary_hash"] == (
        reproducibility_boundary["boundary_hash"]
    )
    assert diagnostics_bundle["reproducibility_boundary"] == reproducibility_boundary
    assert diagnostics_bundle["model_boundaries"]["packet_level_simulation"] is False
    assert diagnostics_bundle["model_boundaries"]["event_replay_restore"] is False
    assert network_kpi_benchmark_validation["artifact_id"] == (
        RUNTIME_EXPORT_NETWORK_KPI_BENCHMARK_VALIDATION_V1_ID
    )
    assert network_kpi_benchmark_validation["validation"] == (
        config_snapshot["status"]["network_kpi_benchmark_validation_v1"]
    )
    assert network_kpi_benchmark_validation["evidence"][
        "validation_hash"
    ] == review_summary["network_kpi_benchmark_validation"]["validation_hash"]
    assert "NO_METRIC_RECOMPUTE" in network_kpi_benchmark_validation[
        "boundary_conditions"
    ]
    assert network_kpi_formula_evidence["artifact_id"] == (
        RUNTIME_EXPORT_NETWORK_KPI_FORMULA_EVIDENCE_V1_ID
    )
    assert network_kpi_formula_evidence["formula_evidence"] == (
        config_snapshot["status"]["network_kpi_formula_evidence_v1"]
    )
    assert network_kpi_formula_evidence["evidence"]["evidence_hash"] == (
        review_summary["network_kpi_formula_evidence"]["evidence_hash"]
    )
    assert "NO_METRIC_RECOMPUTE" in network_kpi_formula_evidence[
        "boundary_conditions"
    ]
    assert network_kpi_variation_explanation["artifact_id"] == (
        RUNTIME_EXPORT_NETWORK_KPI_VARIATION_EXPLANATION_V1_ID
    )
    assert network_kpi_variation_explanation["variation_explanation"] == (
        config_snapshot["status"]["network_kpi_variation_explanation_v1"]
    )
    assert network_kpi_dynamic_status["artifact_id"] == (
        RUNTIME_EXPORT_NETWORK_KPI_DYNAMIC_STATUS_V1_ID
    )
    assert network_kpi_dynamic_status["dynamic_status"] == (
        config_snapshot["status"]["network_kpi_dynamic_status_v1"]
    )
    assert runtime_kpi_movement_summary["artifact_id"] == (
        RUNTIME_EXPORT_RUNTIME_KPI_MOVEMENT_SUMMARY_V1_ID
    )
    assert runtime_kpi_movement_summary["movement_summary"] == (
        config_snapshot["status"]["runtime_kpi_movement_summary_v1"]
    )
    assert runtime_kpi_movement_summary["evidence"]["evidence_hash"] == (
        review_summary["runtime_kpi_movement_summary"]["evidence_hash"]
    )
    assert network_flow_lifecycle_summary["artifact_id"] == (
        RUNTIME_EXPORT_NETWORK_FLOW_LIFECYCLE_SUMMARY_V1_ID
    )
    assert network_flow_lifecycle_summary["summary"] == (
        config_snapshot["status"]["network_flow_lifecycle_summary_v1"]
    )
    assert network_flow_lifecycle_summary["evidence"]["evidence_hash"] == (
        review_summary["network_flow_lifecycle_summary"]["evidence_hash"]
    )
    assert service_lifecycle_stage_summary["artifact_id"] == (
        RUNTIME_EXPORT_SERVICE_LIFECYCLE_STAGE_SUMMARY_V1_ID
    )
    assert service_lifecycle_stage_summary["stage_summary"] == (
        config_snapshot["status"]["service_lifecycle_stage_summary_v1"]
    )
    assert service_lifecycle_stage_summary["evidence"]["evidence_hash"] == (
        review_summary["service_lifecycle_stage_summary"]["evidence_hash"]
    )
    assert "NO_SERVICE_LIFECYCLE_RECOMPUTE" in service_lifecycle_stage_summary[
        "boundary_conditions"
    ]
    assert node_network_pressure_summary["evidence"]["evidence_hash"] == (
        review_summary["node_network_pressure_summary"]["evidence_hash"]
    )
    assert network_temporal_pressure_evidence["artifact_id"] == (
        RUNTIME_EXPORT_NETWORK_TEMPORAL_PRESSURE_EVIDENCE_V1_ID
    )
    assert network_temporal_pressure_evidence["temporal_pressure_evidence"] == (
        config_snapshot["status"]["network_kpi_provenance_v2"][
            "temporal_pressure_evidence"
        ]
    )
    assert network_temporal_pressure_evidence["evidence"]["evidence_hash"] == (
        review_summary["network_temporal_pressure_evidence"]["evidence_hash"]
    )
    assert network_temporal_pressure_evidence["evidence"][
        "packet_level_simulation"
    ] is False
    assert "NO_METRIC_RECOMPUTE" in network_temporal_pressure_evidence[
        "boundary_conditions"
    ]
    assert network_kpi_variation_explanation["evidence"]["evidence_hash"] == (
        review_summary["network_kpi_variation_explanation"]["evidence_hash"]
    )
    assert "NO_METRIC_RECOMPUTE" in network_kpi_variation_explanation[
        "boundary_conditions"
    ]
    assert network_kpi_dynamic_status["evidence"]["evidence_hash"] == (
        review_summary["network_kpi_dynamic_status"]["evidence_hash"]
    )
    assert "NO_METRIC_RECOMPUTE" in network_kpi_dynamic_status[
        "boundary_conditions"
    ]
    assert user_configuration_template_validation["artifact_id"] == (
        RUNTIME_EXPORT_USER_CONFIGURATION_TEMPLATE_VALIDATION_V1_ID
    )
    assert user_configuration_template_validation["template_validation"] == (
        config_snapshot["user_configuration_template_validation_v1"]
    )
    assert user_configuration_template_validation["evidence"]["evidence_hash"] == (
        review_summary["user_configuration_template_validation"]["evidence_hash"]
    )
    assert user_configuration_template_validation["evidence"][
        "validation_status"
    ] == "ALL_TEMPLATES_VALID"
    assert "NO_TEMPLATE_RELOAD" in user_configuration_template_validation[
        "boundary_conditions"
    ]
    assert user_configuration_control_surface_evidence["artifact_id"] == (
        RUNTIME_EXPORT_USER_CONFIGURATION_CONTROL_SURFACE_EVIDENCE_V1_ID
    )
    assert user_configuration_control_surface_evidence[
        "control_surface_evidence"
    ] == config_snapshot["user_configuration_control_surface_evidence_v1"]
    assert user_configuration_control_surface_evidence["evidence"][
        "evidence_hash"
    ] == review_summary["user_configuration_control_surface_evidence"][
        "evidence_hash"
    ]
    assert user_configuration_control_surface_evidence["evidence"][
        "coverage_status"
    ] == "COMPLETE"
    assert user_configuration_control_surface_evidence["evidence"][
        "acceptable_for_demo_review"
    ] is True
    assert "NO_CONFIG_RECOMPUTE" in user_configuration_control_surface_evidence[
        "boundary_conditions"
    ]
    assert traffic_demand_explanation["artifact_id"] == (
        RUNTIME_EXPORT_TRAFFIC_DEMAND_EXPLANATION_V1_ID
    )
    assert traffic_demand_explanation["traffic_demand_explanation"] == (
        config_snapshot["generated_config"]["backend_summary"][
            "traffic_demand_explanation_v1"
        ]
    )
    assert traffic_demand_explanation["evidence"]["evidence_hash"] == (
        review_summary["traffic_demand_explanation"]["evidence_hash"]
    )
    assert traffic_demand_explanation["evidence"][
        "frontend_inference_required"
    ] is False
    assert "NO_TRAFFIC_REGENERATION" in traffic_demand_explanation[
        "boundary_conditions"
    ]
    assert user_service_request_summary["artifact_id"] == (
        "leo_twin.runtime_export_user_service_request_summary.v2"
    )
    assert user_service_request_summary["summary"] == (
        config_snapshot["status"]["user_service_request_summary_v2"]
    )
    assert user_service_request_summary["user_service_request_export_policy"] == (
        config_snapshot["status"]["runtime_export_user_service_request_policy_v1"]
    )
    assert user_service_request_summary["evidence"]["summary_hash"] == (
        review_summary["user_service_requests"]["summary_hash"]
    )
    assert "NO_SERVICE_RECOMPUTE" in user_service_request_summary[
        "boundary_conditions"
    ]
    assert scenario_review_bundle["bundle_id"] == (
        RUNTIME_EXPORT_SCENARIO_REVIEW_BUNDLE_V1_ID
    )
    assert scenario_review_bundle["scenario_review_status"] == (
        "SCENARIO_REVIEW_READY"
    )
    assert scenario_review_bundle["user_configuration"]["schema_id"] == (
        "sees.user_configuration.v2"
    )
    assert scenario_review_bundle["user_configuration"]["validation_ok"] is True
    assert scenario_review_bundle["review_summary"]["summary_hash"] == (
        review_summary["summary_hash"]
    )
    assert scenario_review_bundle["diagnostics"]["diagnostics_hash"] == (
        diagnostics_bundle["diagnostics_hash"]
    )
    assert scenario_review_bundle["route_pressure_evidence"]["evidence_hash"] == (
        review_summary["route_pressure_evidence"]["evidence_hash"]
    )
    assert scenario_review_bundle["route_pressure_evidence"][
        "evidence_present"
    ] is True
    assert scenario_review_bundle["node_network_pressure_summary"]["evidence_hash"] == (
        node_network_pressure_summary["evidence"]["evidence_hash"]
    )
    assert scenario_review_bundle["node_network_pressure_summary"][
        "evidence_present"
    ] is True
    assert scenario_review_bundle["compute_resource_pool_summary"][
        "evidence_hash"
    ] == compute_resource_pool_summary["evidence"]["evidence_hash"]
    assert scenario_review_bundle["compute_resource_pool_summary"][
        "evidence_present"
    ] is True
    assert scenario_review_bundle["v2_executable_readiness"][
        "evidence_hash"
    ] == v2_executable_readiness["evidence"]["evidence_hash"]
    assert scenario_review_bundle["v2_executable_readiness"][
        "failed_gate_count"
    ] == v2_executable_readiness["evidence"]["failed_gate_count"]
    assert scenario_review_bundle["v2_executable_readiness"][
        "evidence_present"
    ] is True
    assert scenario_review_bundle["network_kpi_benchmark_validation"][
        "validation_hash"
    ] == network_kpi_benchmark_validation["evidence"]["validation_hash"]
    assert scenario_review_bundle["network_kpi_benchmark_validation"][
        "evidence_present"
    ] is True
    assert scenario_review_bundle["network_kpi_formula_evidence"][
        "evidence_hash"
    ] == network_kpi_formula_evidence["evidence"]["evidence_hash"]
    assert scenario_review_bundle["network_kpi_formula_evidence"][
        "evidence_present"
    ] is True
    assert scenario_review_bundle["network_temporal_pressure_evidence"][
        "evidence_hash"
    ] == network_temporal_pressure_evidence["evidence"]["evidence_hash"]
    assert scenario_review_bundle["network_temporal_pressure_evidence"][
        "evidence_present"
    ] is True
    assert scenario_review_bundle["network_flow_lifecycle_summary"]["evidence_hash"] == (
        network_flow_lifecycle_summary["evidence"]["evidence_hash"]
    )
    assert scenario_review_bundle["network_flow_lifecycle_summary"]["evidence_present"] is True
    assert scenario_review_bundle["service_lifecycle_stage_summary"]["evidence_hash"] == (
        service_lifecycle_stage_summary["evidence"]["evidence_hash"]
    )
    assert scenario_review_bundle["service_lifecycle_stage_summary"][
        "evidence_present"
    ] is True
    assert scenario_review_bundle["network_kpi_variation_explanation"][
        "evidence_hash"
    ] == network_kpi_variation_explanation["evidence"]["evidence_hash"]
    assert scenario_review_bundle["network_kpi_dynamic_status"][
        "evidence_hash"
    ] == network_kpi_dynamic_status["evidence"]["evidence_hash"]
    assert scenario_review_bundle["network_kpi_dynamic_status"][
        "evidence_present"
    ] is True
    assert scenario_review_bundle["runtime_kpi_movement_summary"]["evidence_hash"] == (
        runtime_kpi_movement_summary["evidence"]["evidence_hash"]
    )
    assert scenario_review_bundle["network_kpi_variation_explanation"][
        "evidence_present"
    ] is True
    assert scenario_review_bundle["user_configuration_template_validation"][
        "evidence_hash"
    ] == user_configuration_template_validation["evidence"]["evidence_hash"]
    assert scenario_review_bundle["user_configuration_template_validation"][
        "all_templates_valid"
    ] is True
    assert scenario_review_bundle["user_configuration_control_surface_evidence"][
        "evidence_hash"
    ] == user_configuration_control_surface_evidence["evidence"]["evidence_hash"]
    assert scenario_review_bundle["user_configuration_control_surface_evidence"][
        "coverage_status"
    ] == "COMPLETE"
    assert scenario_review_bundle["user_configuration_control_surface_evidence"][
        "evidence_present"
    ] is True
    assert scenario_review_bundle["traffic_demand_explanation"][
        "evidence_hash"
    ] == traffic_demand_explanation["evidence"]["evidence_hash"]
    assert scenario_review_bundle["traffic_demand_explanation"][
        "evidence_present"
    ] is True
    assert scenario_review_bundle["traffic_business_activity_window"][
        "evidence_hash"
    ] == traffic_business_activity_window["evidence"]["evidence_hash"]
    assert scenario_review_bundle["traffic_business_activity_window"][
        "request_count"
    ] == traffic_business_activity_window["evidence"]["request_count"]
    assert scenario_review_bundle["traffic_business_activity_window"][
        "evidence_present"
    ] is True
    assert scenario_review_bundle["user_service_requests"][
        "summary_hash"
    ] == user_service_request_summary["evidence"]["summary_hash"]
    assert scenario_review_bundle["user_service_requests"][
        "evidence_present"
    ] is True
    assert scenario_review_bundle["audit_index"]["filename"] == (
        "export_package_audit_index_v1.json"
    )
    assert scenario_review_bundle["model_boundaries"][
        "packet_level_simulation"
    ] is False
    assert "service_trace_comparison_review_report_v1.json" in (
        scenario_review_bundle["recommended_review_order"]
    )
    assert "user_configuration_template_validation_v1.json" in (
        scenario_review_bundle["recommended_review_order"]
    )
    assert "user_configuration_control_surface_evidence_v1.json" in (
        scenario_review_bundle["recommended_review_order"]
    )
    assert "traffic_demand_explanation_v1.json" in (
        scenario_review_bundle["recommended_review_order"]
    )
    assert "network_temporal_pressure_evidence_v1.json" in (
        scenario_review_bundle["recommended_review_order"]
    )
    assert "benchmark_acceptance_binding_v1.json" in (
        scenario_review_bundle["recommended_review_order"]
    )
    assert "network_kpi_variation_explanation_v1.json" in (
        scenario_review_bundle["recommended_review_order"]
    )
    assert "network_kpi_dynamic_status_v1.json" in (
        scenario_review_bundle["recommended_review_order"]
    )
    assert "network_flow_lifecycle_summary_v1.json" in (
        scenario_review_bundle["recommended_review_order"]
    )
    assert "service_lifecycle_stage_summary_v1.json" in (
        scenario_review_bundle["recommended_review_order"]
    )
    assert "route_pressure_evidence_v1.json" in (
        scenario_review_bundle["recommended_review_order"]
    )
    assert "node_network_pressure_summary_v1.json" in (
        scenario_review_bundle["recommended_review_order"]
    )
    assert "compute_resource_pool_summary_v1.json" in (
        scenario_review_bundle["recommended_review_order"]
    )
    assert scenario_review_bundle["scenario_review_hash"].startswith("sha256:")
    assert audit_index["audit_index_id"] == RUNTIME_EXPORT_PACKAGE_AUDIT_INDEX_V1_ID
    assert audit_index["package_id"] == package["package_id"]
    assert audit_index["manifest_hash"] == manifest["manifest_hash"]
    assert audit_index["runtime_export_boundary_hash"] == (
        reproducibility_boundary["boundary_hash"]
    )
    assert audit_index["boundary_alignment_status"] == "ALIGNED"
    assert benchmark_acceptance_binding["binding_id"] == (
        RUNTIME_EXPORT_BENCHMARK_ACCEPTANCE_BINDING_V1_ID
    )
    assert audit_index["benchmark_acceptance_binding_v1"] == (
        benchmark_acceptance_binding
    )
    assert audit_index["benchmark_acceptance_binding_hash"] == (
        benchmark_acceptance_binding["binding_hash"]
    )
    user_config_export = control_plane.user_configuration_export()["summary"]
    assert audit_index["user_configuration_schema_id"] == "sees.user_configuration.v2"
    assert audit_index["user_configuration_config_hash"] == (
        user_config_export["config_hash"]
    )
    assert audit_index["user_configuration_validation_ok"] is True
    assert audit_index["user_configuration_control_surface_evidence_present"] is True
    assert audit_index["user_configuration_control_surface_evidence_status"] == (
        "COMPLETE"
    )
    assert audit_index["user_configuration_control_surface_evidence_hash"] == (
        user_configuration_control_surface_evidence["evidence"]["evidence_hash"]
    )
    assert audit_index["user_configuration_control_surface_key_field_count"] == (
        review_summary["user_configuration_control_surface_evidence"][
            "key_field_count"
        ]
    )
    assert audit_index["user_configuration_control_surface_missing_key_count"] == 0
    assert audit_index["user_configuration_binding_v1"]["binding_id"] == (
        "leo_twin.user_configuration_audit_binding.v1"
    )
    assert audit_index["user_configuration_binding_v1"]["schema_id"] == (
        "sees.user_configuration.v2"
    )
    assert audit_index["user_configuration_binding_v1"]["binding_hash"].startswith(
        "sha256:"
    )
    assert audit_index["network_kpi_benchmark_validation_present"] is True
    assert audit_index["network_kpi_benchmark_validation_status"] in {
        "PASS",
        "WARN",
        "INSUFFICIENT_DATA",
    }
    assert audit_index["network_kpi_benchmark_validation_failed_check_count"] == 0
    assert audit_index["network_kpi_benchmark_validation_hash"] == (
        network_kpi_benchmark_validation["evidence"]["validation_hash"]
    )
    assert audit_index["network_kpi_formula_evidence_present"] is True
    assert audit_index["network_kpi_formula_evidence_hash"] == (
        network_kpi_formula_evidence["evidence"]["evidence_hash"]
    )
    assert audit_index["network_kpi_formula_evidence_missing_selected_input_count"] >= 0
    assert audit_index["network_temporal_pressure_evidence_present"] is True
    assert audit_index["network_temporal_pressure_evidence_hash"] == (
        network_temporal_pressure_evidence["evidence"]["evidence_hash"]
    )
    assert audit_index["network_temporal_pressure_evidence_status"] in {
        "OBSERVED",
        "MISSING_RUNTIME_VALUES",
    }
    assert audit_index["network_temporal_pressure_evidence_loss_proxy_rate"] >= 0.0
    assert audit_index["network_kpi_variation_explanation_present"] is True
    assert audit_index["network_kpi_variation_explanation_hash"] == (
        network_kpi_variation_explanation["evidence"]["evidence_hash"]
    )
    assert audit_index["network_kpi_dynamic_status_present"] is True
    assert audit_index["network_kpi_dynamic_status_hash"] == (
        network_kpi_dynamic_status["evidence"]["evidence_hash"]
    )
    assert audit_index["network_kpi_dynamic_status_status"] in {
        "DYNAMIC",
        "PARTIALLY_DYNAMIC",
        "FLAT_WITH_ACTIVITY",
        "FLAT_NO_ACTIVITY",
        "INSUFFICIENT_SERIES",
    }
    assert audit_index["runtime_kpi_movement_summary_present"] is True
    assert audit_index["runtime_kpi_movement_summary_hash"] == (
        runtime_kpi_movement_summary["evidence"]["evidence_hash"]
    )
    assert audit_index["network_flow_lifecycle_summary_present"] is True
    assert audit_index["network_flow_lifecycle_summary_hash"] == (
        network_flow_lifecycle_summary["evidence"]["evidence_hash"]
    )
    assert audit_index["network_flow_lifecycle_summary_active_flow_count"] >= 0
    assert audit_index["service_lifecycle_stage_summary_present"] is True
    assert audit_index["service_lifecycle_stage_summary_hash"] == (
        service_lifecycle_stage_summary["evidence"]["evidence_hash"]
    )
    assert audit_index["service_lifecycle_stage_summary_service_count"] >= 0
    assert audit_index["service_lifecycle_stage_summary_observed_stage_count"] >= 0
    assert audit_index[
        "network_kpi_variation_explanation_missing_explanation_count"
    ] == network_kpi_variation_explanation["evidence"][
        "missing_explanation_count"
    ]
    assert audit_index["user_configuration_template_validation_present"] is True
    assert audit_index["user_configuration_template_validation_status"] == (
        "ALL_TEMPLATES_VALID"
    )
    assert audit_index[
        "user_configuration_template_validation_all_templates_valid"
    ] is True
    assert audit_index["user_configuration_template_validation_hash"] == (
        user_configuration_template_validation["evidence"]["evidence_hash"]
    )
    assert audit_index["traffic_demand_explanation_present"] is True
    assert audit_index["traffic_demand_explanation_hash"] == (
        traffic_demand_explanation["evidence"]["evidence_hash"]
    )
    assert audit_index["traffic_demand_explanation_request_count"] == (
        traffic_demand_explanation["evidence"]["request_count"]
    )
    assert audit_index["traffic_business_activity_window_present"] is True
    assert audit_index["traffic_business_activity_window_hash"] == (
        traffic_business_activity_window["evidence"]["evidence_hash"]
    )
    assert audit_index["traffic_business_activity_window_request_count"] == (
        traffic_business_activity_window["evidence"]["request_count"]
    )
    assert audit_index["traffic_business_activity_window_active_user_count"] == (
        traffic_business_activity_window["evidence"]["active_user_count"]
    )
    assert audit_index["route_pressure_evidence_present"] is True
    assert audit_index["route_pressure_evidence_hash"] == (
        review_summary["route_pressure_evidence"]["evidence_hash"]
    )
    assert audit_index["route_pressure_evidence_route_count"] == (
        review_summary["route_pressure_evidence"]["route_count"]
    )
    assert audit_index["route_pressure_evidence_pressure_edge_count"] == (
        review_summary["route_pressure_evidence"]["pressure_edge_count"]
    )
    assert audit_index["route_pressure_evidence_max_edge_projected_utilization"] == (
        review_summary["route_pressure_evidence"]["max_edge_projected_utilization"]
    )
    assert audit_index["node_network_pressure_summary_present"] is True
    assert audit_index["node_network_pressure_summary_hash"] == (
        node_network_pressure_summary["evidence"]["evidence_hash"]
    )
    assert audit_index["node_network_pressure_summary_node_count"] == (
        review_summary["node_network_pressure_summary"]["node_count"]
    )
    assert audit_index["node_network_pressure_summary_pressure_edge_count"] == (
        review_summary["node_network_pressure_summary"]["pressure_edge_count"]
    )
    assert audit_index["node_network_pressure_summary_max_projected_utilization"] == (
        review_summary["node_network_pressure_summary"]["max_projected_utilization"]
    )
    assert audit_index["compute_resource_pool_summary_present"] is True
    assert audit_index["compute_resource_pool_summary_hash"] == (
        compute_resource_pool_summary["evidence"]["evidence_hash"]
    )
    assert audit_index["compute_resource_pool_summary_dimension_count"] == (
        review_summary["compute_resource_pool_summary"]["dimension_count"]
    )
    assert audit_index["compute_resource_pool_summary_saturated_dimension_count"] == (
        review_summary["compute_resource_pool_summary"][
            "saturated_dimension_count"
        ]
    )
    assert audit_index["v2_executable_readiness_present"] is True
    assert audit_index["v2_executable_readiness_hash"] == (
        v2_executable_readiness["evidence"]["evidence_hash"]
    )
    assert audit_index["v2_executable_readiness_failed_gate_count"] == (
        v2_executable_readiness["evidence"]["failed_gate_count"]
    )
    assert audit_index["user_service_request_summary_present"] is True
    assert audit_index["user_service_request_summary_hash"] == (
        user_service_request_summary["evidence"]["summary_hash"]
    )
    assert audit_index["user_service_request_summary_exported_request_count"] == (
        user_service_request_summary["evidence"]["exported_request_count"]
    )
    assert audit_index["route_comparison_review_report_present"] is False
    assert audit_index["route_comparison_review_report_hash"] == ""
    assert audit_index["service_trace_comparison_review_report_present"] is False
    assert audit_index["service_trace_comparison_review_report_hash"] == ""
    assert audit_index["service_trace_comparison_review_record_count"] == 0
    assert audit_index["service_trace_comparison_review_error_count"] == 0
    assert audit_index["scenario_review_checklist_present"] is False
    assert audit_index["scenario_review_checklist_hash"] == ""
    assert audit_index["scenario_review_checklist_record_count"] == 0
    assert audit_index["package_review_completion_status"] == "REVIEW_INCOMPLETE"
    assert audit_index["package_review_completion_v1"]["handoff_ready"] is False
    assert "Report id: leo_twin.runtime_export_package_handoff_report.v1" in (
        initial_handoff_report
    )
    assert "Completion status: REVIEW_INCOMPLETE" in initial_handoff_report
    assert "Handoff ready: false" in initial_handoff_report
    assert "ROUTE_COMPARISON_REVIEW_REPORT_MISSING" in audit_index[
        "package_review_completion_v1"
    ]["missing_or_warning_evidence"]
    assert "SCENARIO_REVIEW_CHECKLIST_MISSING" in audit_index[
        "package_review_completion_v1"
    ]["missing_or_warning_evidence"]
    assert audit_index["self_artifact_excluded_from_hashes"] is True
    assert "ROUTE_COMPARISON_REVIEW_REPORT_NOT_SAVED" in audit_index["audit_warnings"]
    assert audit_index["audit_hash"].startswith("sha256:")
    assert "export_package_audit_index_v1.json" not in {
        str(record["filename"]) for record in audit_index["artifact_hashes"]
    }
    assert "scenario_review_bundle_v1.json" in {
        str(record["filename"]) for record in audit_index["artifact_hashes"]
    }

    review_report_response = (
        control_plane.runtime_export_package_route_comparison_review_report(
            str(package["package_id"]),
            {
                "records": [
                    {
                        "route_id": "route-1",
                        "comparison_status": "DIFFERENT",
                        "package_route_detail_hash": "sha256:package-route-1",
                        "live_route_detail_hash": "sha256:live-route-1",
                        "compared_fields": ["path", "latency", "bottleneck"],
                        "different_fields": ["bottleneck", "latency"],
                        "pinned_path_diffs": [
                            {
                                "pointer": "/route/latency_s",
                                "package_value": "0.1",
                                "live_value": "0.25",
                                "package_status": "RESOLVED",
                                "live_status": "RESOLVED",
                                "comparison_status": "DIFFERENT",
                            }
                        ],
                        "status_reason": "FIELDS_DIFFER",
                        "operator_note": "reviewed during integration test",
                    }
                ]
            },
            output_root,
        )
    )
    review_report = review_report_response["summary"]
    assert review_report_response["type"] == (
        "RUNTIME_EXPORT_ROUTE_COMPARISON_REVIEW_REPORT"
    )
    assert review_report["report_id"] == (
        RUNTIME_EXPORT_ROUTE_COMPARISON_REVIEW_REPORT_V1_ID
    )
    assert review_report["package_id"] == package["package_id"]
    assert review_report["record_count"] == 1
    assert review_report["different_count"] == 1
    assert review_report["runtime_export_boundary_hash"] == (
        reproducibility_boundary["boundary_hash"]
    )
    assert review_report["boundary_alignment_status"] == "ALIGNED"
    assert review_report["boundary_alignment_warnings"] == ()
    assert review_report["boundary_alignment_hash"].startswith("sha256:")
    assert review_report["runtime_export_boundary_alignment_v1"][
        "alignment_id"
    ] == "leo_twin.runtime_export_boundary_alignment.v1"
    assert review_report["runtime_export_boundary_alignment_v1"][
        "boundary_hash"
    ] == reproducibility_boundary["boundary_hash"]
    assert review_report["runtime_export_boundary_alignment_v1"][
        "preflight_scope"
    ] == "CONFIG_RESTORE_PREVIEW_ONLY"
    assert review_report["records"][0]["different_fields"] == (
        "latency",
        "bottleneck",
    )
    assert review_report["records"][0]["pinned_path_count"] == 1
    assert review_report["records"][0]["pinned_path_diffs"][0]["pointer"] == (
        "/route/latency_s"
    )
    assert review_report["records"][0]["operator_note"] == (
        "reviewed during integration test"
    )
    route_report_page = (
        control_plane.runtime_export_package_route_comparison_review_report_records(
            str(package["package_id"]),
            output_root,
            cursor=0,
            limit=5,
            query="/route/latency_s",
            status="DIFFERENT",
        )
    )
    assert route_report_page["type"] == (
        "RUNTIME_EXPORT_ROUTE_COMPARISON_REVIEW_REPORT_PAGE_V1"
    )
    assert route_report_page["record_count"] == 1
    assert route_report_page["records"][0]["route_id"] == "route-1"
    assert route_report_page["records"][0]["pinned_path_diffs"][0]["pointer"] == (
        "/route/latency_s"
    )
    review_report_path = package_dir / "route_comparison_review_report_v1.json"
    assert review_report_path.exists()
    assert json.loads(review_report_path.read_text(encoding="utf-8")) == json.loads(
        json.dumps(review_report, sort_keys=True)
    )
    report_artifact = control_plane.runtime_export_package_artifact(
        str(package["package_id"]),
        "route_comparison_review_report_v1.json",
        output_root,
    )
    assert report_artifact["filename"] == "route_comparison_review_report_v1.json"
    assert report_artifact["sha256"] == review_report_response["artifact"]["sha256"]
    updated_audit_index = review_report_response["audit_index"]
    assert updated_audit_index["audit_index_id"] == (
        RUNTIME_EXPORT_PACKAGE_AUDIT_INDEX_V1_ID
    )
    assert updated_audit_index["route_comparison_review_report_present"] is True
    assert updated_audit_index["route_comparison_review_report_hash"] == (
        review_report["report_hash"]
    )
    assert updated_audit_index["boundary_alignment_hash"] == (
        review_report["boundary_alignment_hash"]
    )
    assert updated_audit_index["user_configuration_config_hash"] == (
        user_config_export["config_hash"]
    )
    assert updated_audit_index["user_configuration_validation_ok"] is True
    assert updated_audit_index["runtime_export_boundary_hash"] == (
        reproducibility_boundary["boundary_hash"]
    )
    assert updated_audit_index["scenario_review_checklist_present"] is False
    assert updated_audit_index["package_review_completion_status"] == (
        "REVIEW_INCOMPLETE"
    )
    assert "SCENARIO_REVIEW_CHECKLIST_MISSING" in updated_audit_index[
        "package_review_completion_v1"
    ]["missing_or_warning_evidence"]
    assert updated_audit_index["audit_status"] == "AUDIT_READY"
    assert updated_audit_index["audit_warnings"] == ()
    audit_artifact = control_plane.runtime_export_package_artifact(
        str(package["package_id"]),
        "export_package_audit_index_v1.json",
        output_root,
    )
    assert audit_artifact["sha256"] == review_report_response["audit_artifact"][
        "sha256"
    ]
    assert json.loads(
        (package_dir / "export_package_audit_index_v1.json").read_text(
            encoding="utf-8"
        )
    ) == json.loads(json.dumps(updated_audit_index, sort_keys=True))

    service_trace_report_response = (
        control_plane.runtime_export_package_service_trace_comparison_review_report(
            str(package["package_id"]),
            {
                "records": [
                    {
                        "trace_id": "trace:run",
                        "comparison_status": "DIFFERENT",
                        "package_trace_item_hash": "sha256:package-trace-1",
                        "live_trace_detail_hash": "",
                        "compared_fields": [
                            "terminal",
                            "reason",
                            "total_latency",
                            "stage_counts",
                        ],
                        "different_fields": ["stage_counts", "terminal"],
                        "pinned_path_diffs": [
                            {
                                "pointer": "/trace/terminal_state",
                                "package_value": '"RUNNING"',
                                "live_value": '"COMPLETE"',
                                "package_status": "RESOLVED",
                                "live_status": "RESOLVED",
                                "comparison_status": "DIFFERENT",
                            }
                        ],
                        "status_reason": "FIELDS_DIFFER",
                        "operator_note": "reviewed service trace during integration test",
                    }
                ]
            },
            output_root,
        )
    )
    service_trace_report = service_trace_report_response["summary"]
    assert service_trace_report_response["type"] == (
        "RUNTIME_EXPORT_SERVICE_TRACE_COMPARISON_REVIEW_REPORT"
    )
    assert service_trace_report["report_id"] == (
        RUNTIME_EXPORT_SERVICE_TRACE_COMPARISON_REVIEW_REPORT_V1_ID
    )
    assert service_trace_report["package_id"] == package["package_id"]
    assert service_trace_report["record_count"] == 1
    assert service_trace_report["different_count"] == 1
    assert service_trace_report["runtime_export_boundary_hash"] == (
        reproducibility_boundary["boundary_hash"]
    )
    assert service_trace_report["boundary_alignment_status"] == "ALIGNED"
    assert service_trace_report["records"][0]["different_fields"] == (
        "terminal",
        "stage_counts",
    )
    assert service_trace_report["records"][0]["pinned_path_count"] == 1
    assert service_trace_report["records"][0]["pinned_path_different_count"] == 1
    assert service_trace_report["records"][0]["pinned_path_diffs"][0][
        "pointer"
    ] == "/trace/terminal_state"
    service_trace_report_path = (
        package_dir / "service_trace_comparison_review_report_v1.json"
    )
    assert service_trace_report_path.exists()
    assert json.loads(
        service_trace_report_path.read_text(encoding="utf-8")
    ) == json.loads(json.dumps(service_trace_report, sort_keys=True))
    service_trace_report_artifact = control_plane.runtime_export_package_artifact(
        str(package["package_id"]),
        "service_trace_comparison_review_report_v1.json",
        output_root,
    )
    assert service_trace_report_artifact["filename"] == (
        "service_trace_comparison_review_report_v1.json"
    )
    assert service_trace_report_artifact["sha256"] == (
        service_trace_report_response["artifact"]["sha256"]
    )
    assert service_trace_report_response["audit_index"]["audit_index_id"] == (
        RUNTIME_EXPORT_PACKAGE_AUDIT_INDEX_V1_ID
    )
    service_trace_audit_index = service_trace_report_response["audit_index"]
    assert service_trace_audit_index[
        "service_trace_comparison_review_report_present"
    ] is True
    assert service_trace_audit_index[
        "service_trace_comparison_review_report_hash"
    ] == service_trace_report["report_hash"]
    assert service_trace_audit_index[
        "service_trace_comparison_review_record_count"
    ] == 1
    assert service_trace_audit_index[
        "service_trace_comparison_review_error_count"
    ] == 0
    assert service_trace_audit_index["package_review_completion_v1"][
        "service_trace_comparison_review_report_present"
    ] is True
    assert service_trace_audit_index["package_review_completion_v1"][
        "service_trace_comparison_review_report_hash"
    ] == service_trace_report["report_hash"]
    service_trace_report_page = (
        control_plane.runtime_export_package_service_trace_comparison_review_report_records(
            str(package["package_id"]),
            output_root,
            cursor=0,
            limit=1,
            query="integration test",
            status="DIFFERENT",
        )
    )
    assert service_trace_report_page["type"] == (
        "RUNTIME_EXPORT_SERVICE_TRACE_COMPARISON_REVIEW_REPORT_PAGE_V1"
    )
    assert service_trace_report_page["report_hash"] == service_trace_report[
        "report_hash"
    ]
    assert service_trace_report_page["record_count"] == 1
    assert service_trace_report_page["item_count"] == 1
    assert service_trace_report_page["filters"] == {
        "query": "integration test",
        "status": "DIFFERENT",
    }
    assert service_trace_report_page["records"][0]["trace_id"] == "trace:run"

    checklist_template_response = (
        control_plane.runtime_export_package_scenario_review_checklist_template(
            str(package["package_id"]),
            output_root,
        )
    )
    checklist_template = checklist_template_response["summary"]
    assert checklist_template_response["type"] == (
        "RUNTIME_EXPORT_SCENARIO_REVIEW_CHECKLIST_TEMPLATE"
    )
    assert checklist_template["expected_review_count"] == len(
        scenario_review_bundle["recommended_review_order"]
    )
    assert checklist_template["template_status"] == "TEMPLATE_READY"
    assert checklist_template["missing_evidence_filenames"] == ()
    assert [record["artifact_filename"] for record in checklist_template["records"]] == (
        list(scenario_review_bundle["recommended_review_order"])
    )
    assert checklist_template["records"][0]["evidence_hash"] == (
        scenario_review_bundle["scenario_review_hash"]
    )
    assert any(
        record["artifact_filename"]
        == "service_trace_comparison_review_report_v1.json"
        and record["evidence_hash"] == service_trace_report["report_hash"]
        for record in checklist_template["records"]
    )
    assert any(
        record["artifact_filename"] == "compute_resource_pool_summary_v1.json"
        and record["evidence_hash"]
        == scenario_review_bundle["compute_resource_pool_summary"]["evidence_hash"]
        and "compute resource pool" in record["step_label"]
        for record in checklist_template["records"]
    )
    checklist_records = [
        {
            "artifact_filename": record["artifact_filename"],
            "step_label": record["step_label"],
            "review_status": "REVIEWED",
            "operator_note": "recommended review step checked",
            "evidence_hash": record["evidence_hash"],
        }
        for record in checklist_template["records"]
    ]
    checklist_response = control_plane.runtime_export_package_scenario_review_checklist(
        str(package["package_id"]),
        {"records": checklist_records},
        output_root,
    )
    checklist = checklist_response["summary"]
    assert checklist_response["type"] == "RUNTIME_EXPORT_SCENARIO_REVIEW_CHECKLIST"
    assert checklist_response["handoff_report_artifact"]["filename"] == (
        "package_handoff_report_v1.md"
    )
    assert checklist["checklist_id"] == RUNTIME_EXPORT_SCENARIO_REVIEW_CHECKLIST_V1_ID
    assert checklist["record_count"] == len(
        scenario_review_bundle["recommended_review_order"]
    )
    assert checklist["reviewed_count"] == checklist["record_count"]
    assert checklist["checklist_status"] == "CHECKLIST_COMPLETE"
    assert checklist["submitted_records_complete"] is True
    assert checklist["recommended_review_complete"] is True
    assert checklist["recommended_review_status"] == "RECOMMENDED_REVIEW_COMPLETE"
    assert checklist["expected_review_count"] == checklist["record_count"]
    assert checklist["reviewed_recommended_count"] == checklist["record_count"]
    assert checklist["missing_recommended_review_filenames"] == ()
    assert checklist["attention_recommended_review_filenames"] == ()
    assert checklist["scenario_review_hash"] == (
        scenario_review_bundle["scenario_review_hash"]
    )
    checklist_path = package_dir / "scenario_review_checklist_v1.json"
    assert checklist_path.exists()
    assert json.loads(checklist_path.read_text(encoding="utf-8")) == json.loads(
        json.dumps(checklist, sort_keys=True)
    )
    checklist_artifact = control_plane.runtime_export_package_artifact(
        str(package["package_id"]),
        "scenario_review_checklist_v1.json",
        output_root,
    )
    assert checklist_artifact["sha256"] == checklist_response["artifact"]["sha256"]
    checklist_audit = checklist_response["audit_index"]
    assert checklist_audit["route_comparison_review_report_present"] is True
    assert checklist_audit[
        "service_trace_comparison_review_report_present"
    ] is True
    assert checklist_audit["service_trace_comparison_review_report_hash"] == (
        service_trace_report["report_hash"]
    )
    assert checklist_audit["scenario_review_checklist_present"] is True
    assert checklist_audit["scenario_review_checklist_hash"] == (
        checklist["checklist_hash"]
    )
    assert checklist_audit["scenario_review_checklist_record_count"] == (
        checklist["record_count"]
    )
    assert checklist_audit["scenario_review_checklist_status"] == (
        "CHECKLIST_COMPLETE"
    )
    assert checklist_audit[
        "scenario_review_checklist_recommended_review_complete"
    ] is True
    assert checklist_audit["scenario_review_checklist_expected_review_count"] == (
        checklist["record_count"]
    )
    assert checklist_audit["scenario_review_checklist_reviewed_recommended_count"] == (
        checklist["record_count"]
    )
    assert checklist_audit["package_review_completion_status"] == "REVIEW_COMPLETE"
    assert checklist_audit["package_review_completion_v1"]["handoff_ready"] is True
    assert checklist_audit["package_review_completion_v1"][
        "missing_or_warning_evidence"
    ] == ()
    assert checklist_audit["package_review_completion_hash"] == (
        checklist_audit["package_review_completion_v1"]["completion_hash"]
    )
    checklist_template_comparison_response = (
        control_plane.runtime_export_package_scenario_review_checklist_template_comparison(
            str(package["package_id"]),
            output_root,
        )
    )
    checklist_template_comparison = checklist_template_comparison_response["summary"]
    assert checklist_template_comparison_response["type"] == (
        "RUNTIME_EXPORT_SCENARIO_REVIEW_CHECKLIST_TEMPLATE_COMPARISON"
    )
    assert checklist_template_comparison["comparison_id"] == (
        RUNTIME_EXPORT_SCENARIO_REVIEW_CHECKLIST_TEMPLATE_COMPARISON_V1_ID
    )
    assert checklist_template_comparison["comparison_status"] == "ALIGNED"
    assert checklist_template_comparison["template_hash"].startswith("sha256:")
    assert checklist_template_comparison["checklist_hash"] == (
        checklist["checklist_hash"]
    )
    assert checklist_template_comparison["aligned_record_count"] == (
        checklist_template_comparison["template_record_count"]
    )
    assert checklist_template_comparison["evidence_hash_mismatch_count"] == 0
    assert checklist_template_comparison["comparison_hash"].startswith("sha256:")
    completion_response = control_plane.runtime_export_package_review_completion(
        str(package["package_id"]),
        output_root,
    )
    assert completion_response["type"] == "RUNTIME_EXPORT_PACKAGE_REVIEW_COMPLETION"
    assert completion_response["summary"] == json.loads(
        json.dumps(checklist_audit["package_review_completion_v1"], sort_keys=True)
    )
    assert completion_response["source_artifact"]["filename"] == (
        "export_package_audit_index_v1.json"
    )
    acceptance_response = control_plane.runtime_export_package_acceptance_report(
        str(package["package_id"]),
        output_root,
    )
    acceptance_report = acceptance_response["summary"]
    assert acceptance_response["type"] == "RUNTIME_EXPORT_PACKAGE_ACCEPTANCE_REPORT"
    assert acceptance_response["source_artifact"]["filename"] == (
        "export_package_audit_index_v1.json"
    )
    assert acceptance_report["acceptance_id"] == (
        RUNTIME_EXPORT_PACKAGE_ACCEPTANCE_REPORT_V1_ID
    )
    assert acceptance_report["acceptance_status"] == "WARN"
    assert acceptance_report["demo_closed_loop_ready"] is True
    assert acceptance_report["handoff_ready"] is True
    assert acceptance_report["completion_status"] == "REVIEW_COMPLETE"
    assert acceptance_report["fail_count"] == 0
    assert acceptance_report["warn_count"] == 1
    assert acceptance_report["pass_count"] == acceptance_report["check_count"] - 1
    assert [check["check_id"] for check in acceptance_report["checks"]] == [
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
    benchmark_gate = next(
        check
        for check in acceptance_report["checks"]
        if check["check_id"] == "benchmark_scenario_gate"
    )
    assert benchmark_gate["status"] == "WARN"
    assert benchmark_gate["issue_labels"] == (
        "NO_STANDARD_BENCHMARK_SCENARIO_MATCH",
    )
    assert acceptance_report["acceptance_hash"].startswith("sha256:")
    handoff_artifact = control_plane.runtime_export_package_artifact(
        str(package["package_id"]),
        "package_handoff_report_v1.md",
        output_root,
    )
    assert handoff_artifact["content_type"] == "text/markdown; charset=utf-8"
    assert handoff_artifact["filename"] == "package_handoff_report_v1.md"
    final_handoff_report = Path(str(handoff_artifact["path"])).read_text(
        encoding="utf-8"
    )
    assert "Completion status: REVIEW_COMPLETE" in final_handoff_report
    assert "Handoff ready: true" in final_handoff_report
    assert "Service trace comparison review report present: true" in (
        final_handoff_report
    )
    assert service_trace_report["report_hash"] in final_handoff_report
    assert checklist_audit["package_review_completion_hash"] in final_handoff_report
    assert checklist_audit["audit_status"] == "AUDIT_READY"
    assert checklist_audit["audit_warnings"] == ()
    catalog = control_plane.runtime_export_catalog(output_root)["summary"]
    latest = catalog["latest_export"]
    assert latest["file_count"] == len(latest["files"])
    assert "route_comparison_review_report_v1.json" in {
        str(record["filename"]) for record in latest["files"]
    }
    assert "scenario_review_checklist_v1.json" in {
        str(record["filename"]) for record in latest["files"]
    }
    assert "export_package_audit_index_v1.json" in {
        str(record["filename"]) for record in latest["files"]
    }
    assert "scenario_review_bundle_v1.json" in {
        str(record["filename"]) for record in latest["files"]
    }
    assert "network_kpi_benchmark_validation_v1.json" in {
        str(record["filename"]) for record in latest["files"]
    }
    assert "benchmark_acceptance_binding_v1.json" in {
        str(record["filename"]) for record in latest["files"]
    }


def _base_demo_config() -> DemoConfig:
    return DemoConfig(
        seed=4321,
        satellite_count=8,
        ground_user_count=20,
        ground_station_count=1,
        compute_node_count=2,
        duration_seconds=120,
        orbit_tick_seconds=1,
        network_slot_seconds=30,
        flow_interval_seconds=30,
        task_interval_seconds=30,
        cell_count=10,
        state_snapshot_interval_events=20,
        metric_sample_interval=10,
        websocket_events="/stream/events",
        websocket_state="/stream/state",
        metrics_snapshot="/metrics/snapshot",
        scenario_config="/scenario/config",
        backend_host="127.0.0.1",
        backend_port=8765,
    )
