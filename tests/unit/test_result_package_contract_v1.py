from __future__ import annotations

import json

from leo_twin.services.result_package_contract import (
    RESULT_PACKAGE_CONTRACT_V1_ID,
    RUNTIME_EXPORT_REVIEW_SUMMARY_V1_ID,
    RUNTIME_REPRODUCIBILITY_MANIFEST_V1_ID,
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
        "review_summary_v1.json",
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
        "review_summary_v1.json",
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
    assert first["summary_hash"].startswith("sha256:")
    assert json.loads(json.dumps(first, sort_keys=True))["summary_id"] == (
        RUNTIME_EXPORT_REVIEW_SUMMARY_V1_ID
    )


def _file(name: str, filename: str, sha256: str) -> dict[str, object]:
    return {
        "name": name,
        "filename": filename,
        "path": f"exports/pkg-1/{filename}",
        "bytes": 10,
        "sha256": sha256,
    }
