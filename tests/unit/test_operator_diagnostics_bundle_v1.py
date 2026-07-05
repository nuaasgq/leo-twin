from __future__ import annotations

import json

from leo_twin.services.build_info import VERSION_INFO_V1_ID
from leo_twin.services.launcher_health import LAUNCHER_HEALTH_V2_ID
from leo_twin.services.operator_diagnostics import (
    OPERATOR_DIAGNOSTICS_BUNDLE_V1_ID,
    build_operator_diagnostics_bundle_manifest_v1,
    summarize_operator_diagnostics_bundle_v1,
)


def test_operator_diagnostics_bundle_manifest_complete() -> None:
    manifest = build_operator_diagnostics_bundle_manifest_v1(
        bundle_dir="artifacts/operator_diagnostics/diag-1",
        launcher_health={
            "type": "LAUNCHER_HEALTH",
            "health_id": LAUNCHER_HEALTH_V2_ID,
            "overall_status": "HEALTHY",
        },
        runtime_status={"type": "RUNTIME_STATUS", "status": {"status": "RUNNING"}},
        version_info={"type": "VERSION_INFO", "version_info_id": VERSION_INFO_V1_ID},
        user_config_export={"type": "USER_CONFIGURATION_EXPORT", "summary": {}},
        runtime_export_catalog={"type": "RUNTIME_EXPORT_CATALOG", "summary": {}},
        log_files=(
            {
                "name": "backend_stdout",
                "filename": "backend.out.log",
                "path": "logs/backend.out.log",
                "bytes": 42,
                "sha256": "sha256:abc",
            },
        ),
    )
    summary = summarize_operator_diagnostics_bundle_v1(manifest)

    assert manifest["type"] == "OPERATOR_DIAGNOSTICS_BUNDLE"
    assert manifest["bundle_id"] == OPERATOR_DIAGNOSTICS_BUNDLE_V1_ID
    assert manifest["bundle_status"] == "COMPLETE"
    assert manifest["present_section_count"] == 5
    assert manifest["manifest_hash"].startswith("sha256:")
    assert json.loads(json.dumps(manifest, sort_keys=True))["bundle_id"] == (
        OPERATOR_DIAGNOSTICS_BUNDLE_V1_ID
    )
    assert summary == {
        "bundle_id": OPERATOR_DIAGNOSTICS_BUNDLE_V1_ID,
        "bundle_status": "COMPLETE",
        "bundle_dir": "artifacts\\operator_diagnostics\\diag-1",
        "section_count": 5,
        "present_section_count": 5,
        "invalid_section_count": 0,
        "log_file_count": 1,
        "manifest_hash": manifest["manifest_hash"],
        "ready_for_support": True,
        "missing_sections": (),
        "invalid_sections": (),
    }


def test_operator_diagnostics_bundle_manifest_partial() -> None:
    manifest = build_operator_diagnostics_bundle_manifest_v1(
        bundle_dir="diag-partial",
        launcher_health={
            "type": "LAUNCHER_HEALTH",
            "health_id": LAUNCHER_HEALTH_V2_ID,
        },
    )
    summary = summarize_operator_diagnostics_bundle_v1(manifest)

    assert manifest["bundle_status"] == "PARTIAL"
    assert summary["ready_for_support"] is True
    assert "runtime_status" in summary["missing_sections"]
    assert manifest["recommended_next_actions"][0] == (
        "Attach the partial diagnostics bundle and note missing sections."
    )


def test_operator_diagnostics_bundle_manifest_detects_invalid_sections() -> None:
    manifest = build_operator_diagnostics_bundle_manifest_v1(
        bundle_dir="diag-invalid",
        launcher_health={"type": "LAUNCHER_HEALTH", "health_id": "wrong"},
        runtime_status={"type": "NOT_RUNTIME_STATUS"},
    )
    summary = summarize_operator_diagnostics_bundle_v1(manifest)

    assert manifest["bundle_status"] == "INVALID"
    assert summary["ready_for_support"] is False
    assert summary["invalid_section_count"] == 2
    assert summary["invalid_sections"] == ("launcher_health", "runtime_status")
    assert manifest["recommended_next_actions"] == (
        "Re-run diagnostics collection after restarting services.",
    )
