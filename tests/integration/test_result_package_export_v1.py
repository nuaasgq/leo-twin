from __future__ import annotations

import json
from pathlib import Path

from examples.integration_demo.config import DemoConfig
from examples.integration_demo.control_plane import DemoControlPlane
from examples.integration_demo.runtime import run_integration_demo
from leo_twin.services.detail_pagination_contract import DETAIL_ENDPOINT_MAX_LIMIT
from leo_twin.services.result_package_contract import (
    RUNTIME_EXPORT_ROUTE_COMPARISON_REVIEW_REPORT_V1_ID,
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
    assert (package_dir / "service_lifecycle_trace_v2.json").exists()
    filenames = {str(record["filename"]) for record in package["files"]}
    assert "service_lifecycle_trace_v2.json" in filenames
    assert "route_detail_index_v1.json" in filenames
    assert "review_summary_v1.json" in filenames
    assert "diagnostics_bundle_v1.json" in filenames

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
    review_summary = json.loads(
        (package_dir / "review_summary_v1.json").read_text(encoding="utf-8")
    )
    diagnostics_bundle = json.loads(
        (package_dir / "diagnostics_bundle_v1.json").read_text(encoding="utf-8")
    )

    assert manifest["manifest_id"] == RUNTIME_REPRODUCIBILITY_MANIFEST_V1_ID
    assert manifest["manifest_hash"] == summary["manifest_hash"]
    assert config_snapshot["type"] == "RUNTIME_CONFIG_SNAPSHOT"
    assert config_snapshot["status"]["export_status_policy"] == (
        "STABLE_RUNTIME_STATUS_WITHOUT_STREAM_DIAGNOSTICS"
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
    assert review_summary["type"] == "RUNTIME_EXPORT_REVIEW_SUMMARY_V1"
    assert review_summary["review_status"] == "REVIEW_READY"
    assert review_summary["route_trust"]["trust_id"] == route_trust_status["trust_id"]
    assert review_summary["route_trust"]["route_model"] == (
        route_trust_status["route_model"]
    )
    assert review_summary["route_trust"]["packet_level_simulation"] is False
    assert review_summary["route_trust"]["all_pairs_computation"] is False
    assert review_summary["reproducibility"]["manifest_hash"] == manifest[
        "manifest_hash"
    ]
    assert "review_summary_v1.json" in review_summary["artifacts"][
        "artifact_filenames"
    ]
    assert "route_detail_index_v1.json" in review_summary["artifacts"][
        "artifact_filenames"
    ]
    assert "diagnostics_bundle_v1.json" in review_summary["artifacts"][
        "artifact_filenames"
    ]
    assert diagnostics_bundle["type"] == "RUNTIME_EXPORT_DIAGNOSTICS_BUNDLE_V1"
    assert diagnostics_bundle["package"]["package_complete"] is True
    assert diagnostics_bundle["artifact_health"]["missing_required_filenames"] == []
    assert diagnostics_bundle["route_trust"]["trust_id"] == route_trust_status[
        "trust_id"
    ]
    assert diagnostics_bundle["route_trust"]["trust_status"] == route_trust_status[
        "trust_status"
    ]
    assert diagnostics_bundle["route_trust"]["evidence_present"] is True
    assert diagnostics_bundle["reproducibility"]["manifest_hash"] == manifest[
        "manifest_hash"
    ]
    assert diagnostics_bundle["model_boundaries"]["packet_level_simulation"] is False

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
    assert review_report["records"][0]["different_fields"] == (
        "latency",
        "bottleneck",
    )
    assert review_report["records"][0]["operator_note"] == (
        "reviewed during integration test"
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
    catalog = control_plane.runtime_export_catalog(output_root)["summary"]
    latest = catalog["latest_export"]
    assert latest["file_count"] == len(latest["files"])
    assert "route_comparison_review_report_v1.json" in {
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
