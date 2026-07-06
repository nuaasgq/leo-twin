from __future__ import annotations

import json
from pathlib import Path

from examples.integration_demo.config import DemoConfig
from examples.integration_demo.control_plane import DemoControlPlane
from examples.integration_demo.runtime import run_integration_demo
from leo_twin.services.result_package_contract import (
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

    package = control_plane.export_runtime_package(tmp_path / "exports")
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
    assert (package_dir / "service_lifecycle_trace_v2.json").exists()
    filenames = {str(record["filename"]) for record in package["files"]}
    assert "service_lifecycle_trace_v2.json" in filenames
    assert "review_summary_v1.json" in filenames
    assert "diagnostics_bundle_v1.json" in filenames

    manifest = json.loads((package_dir / "manifest.json").read_text(encoding="utf-8"))
    config_snapshot = json.loads(
        (package_dir / "config_snapshot.json").read_text(encoding="utf-8")
    )
    service_lifecycle_trace = json.loads(
        (package_dir / "service_lifecycle_trace_v2.json").read_text(encoding="utf-8")
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
    assert review_summary["type"] == "RUNTIME_EXPORT_REVIEW_SUMMARY_V1"
    assert review_summary["review_status"] == "REVIEW_READY"
    assert review_summary["reproducibility"]["manifest_hash"] == manifest[
        "manifest_hash"
    ]
    assert "review_summary_v1.json" in review_summary["artifacts"][
        "artifact_filenames"
    ]
    assert "diagnostics_bundle_v1.json" in review_summary["artifacts"][
        "artifact_filenames"
    ]
    assert diagnostics_bundle["type"] == "RUNTIME_EXPORT_DIAGNOSTICS_BUNDLE_V1"
    assert diagnostics_bundle["package"]["package_complete"] is True
    assert diagnostics_bundle["artifact_health"]["missing_required_filenames"] == []
    assert diagnostics_bundle["reproducibility"]["manifest_hash"] == manifest[
        "manifest_hash"
    ]
    assert diagnostics_bundle["model_boundaries"]["packet_level_simulation"] is False


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
