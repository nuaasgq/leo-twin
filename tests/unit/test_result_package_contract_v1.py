from __future__ import annotations

import json

from leo_twin.services.result_package_contract import (
    RESULT_PACKAGE_CONTRACT_V1_ID,
    RUNTIME_REPRODUCIBILITY_MANIFEST_V1_ID,
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
    assert "GET /runtime/export" in first["source_endpoints"]
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


def _file(name: str, filename: str, sha256: str) -> dict[str, object]:
    return {
        "name": name,
        "filename": filename,
        "path": f"exports/pkg-1/{filename}",
        "bytes": 10,
        "sha256": sha256,
    }
