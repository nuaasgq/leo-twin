"""Operator diagnostics bundle manifest helpers."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from leo_twin.services.build_info import VERSION_INFO_V1_ID
from leo_twin.services.launcher_health import LAUNCHER_HEALTH_V2_ID
from leo_twin.services.runtime_reproducibility import stable_hash_payload


OPERATOR_DIAGNOSTICS_BUNDLE_V1_ID = "leo_twin.operator_diagnostics_bundle.v1"


def build_operator_diagnostics_bundle_manifest_v1(
    *,
    bundle_dir: str | Path,
    launcher_health: Mapping[str, Any] | None = None,
    runtime_status: Mapping[str, Any] | None = None,
    version_info: Mapping[str, Any] | None = None,
    user_config_export: Mapping[str, Any] | None = None,
    runtime_export_catalog: Mapping[str, Any] | None = None,
    log_files: Sequence[Mapping[str, Any]] = (),
) -> dict[str, object]:
    """Build a deterministic manifest for an operator diagnostics bundle."""

    bundle_path = Path(bundle_dir)
    sections = {
        "launcher_health": _section_record(
            "launcher_health.json",
            launcher_health,
            expected_id_key="health_id",
            expected_id=LAUNCHER_HEALTH_V2_ID,
        ),
        "runtime_status": _section_record(
            "runtime_status.json",
            runtime_status,
            expected_type="RUNTIME_STATUS",
        ),
        "version_info": _section_record(
            "version_info.json",
            version_info,
            expected_id_key="version_info_id",
            expected_id=VERSION_INFO_V1_ID,
        ),
        "user_config_export": _section_record(
            "user_config_export.json",
            user_config_export,
            expected_type="USER_CONFIGURATION_EXPORT",
        ),
        "runtime_export_catalog": _section_record(
            "runtime_export_catalog.json",
            runtime_export_catalog,
            expected_type="RUNTIME_EXPORT_CATALOG",
        ),
    }
    normalized_logs = tuple(_log_file_record(item) for item in log_files)
    manifest: dict[str, object] = {
        "type": "OPERATOR_DIAGNOSTICS_BUNDLE",
        "bundle_id": OPERATOR_DIAGNOSTICS_BUNDLE_V1_ID,
        "version": "v1",
        "bundle_dir": str(bundle_path),
        "bundle_status": _bundle_status(sections, normalized_logs),
        "sections": sections,
        "section_count": len(sections),
        "present_section_count": sum(
            1 for section in sections.values() if section["present"] is True
        ),
        "log_files": normalized_logs,
        "log_file_count": len(normalized_logs),
        "recommended_next_actions": _recommended_next_actions(sections, normalized_logs),
        "artifact_policy": {
            "format": "directory",
            "json_files": tuple(record["filename"] for record in sections.values()),
            "log_copy_policy": "copy selected launcher stdout/stderr logs when present",
        },
        "constraints": {
            "event_kernel_frozen": True,
            "packet_level_simulation": False,
            "forbidden_integrations": ("STK", "EXATA", "AFSIM", "DDS"),
        },
    }
    manifest["manifest_hash"] = stable_hash_payload(manifest)
    return manifest


def summarize_operator_diagnostics_bundle_v1(
    manifest: Mapping[str, Any],
) -> dict[str, object]:
    """Summarize a diagnostics bundle manifest for UI or CLI display."""

    if not isinstance(manifest, Mapping):
        raise TypeError("manifest must be a mapping")
    sections = _mapping(manifest.get("sections"))
    section_records = tuple(
        _mapping(sections[key]) for key in sorted(sections)
    )
    present = tuple(section for section in section_records if section.get("present") is True)
    invalid = tuple(
        section
        for section in section_records
        if section.get("present") is True and section.get("valid") is not True
    )
    return {
        "bundle_id": str(manifest.get("bundle_id", "")),
        "bundle_status": str(manifest.get("bundle_status", "")),
        "bundle_dir": str(manifest.get("bundle_dir", "")),
        "section_count": len(section_records),
        "present_section_count": len(present),
        "invalid_section_count": len(invalid),
        "log_file_count": int(manifest.get("log_file_count", 0)),
        "manifest_hash": str(manifest.get("manifest_hash", "")),
        "ready_for_support": (
            manifest.get("bundle_status") in {"COMPLETE", "PARTIAL"}
            and len(present) > 0
            and len(invalid) == 0
        ),
        "missing_sections": tuple(
            str(section.get("name", ""))
            for section in section_records
            if section.get("present") is not True
        ),
        "invalid_sections": tuple(
            str(section.get("name", ""))
            for section in invalid
        ),
    }


def _section_record(
    filename: str,
    payload: Mapping[str, Any] | None,
    *,
    expected_type: str | None = None,
    expected_id_key: str | None = None,
    expected_id: str | None = None,
) -> dict[str, object]:
    present = payload is not None
    valid = False
    if payload is not None:
        valid = True
        if expected_type is not None:
            valid = valid and payload.get("type") == expected_type
        if expected_id_key is not None and expected_id is not None:
            valid = valid and payload.get(expected_id_key) == expected_id
    return {
        "name": filename.removesuffix(".json"),
        "filename": filename,
        "present": present,
        "valid": valid,
        "payload_hash": "" if payload is None else stable_hash_payload(payload),
    }


def _log_file_record(value: Mapping[str, Any]) -> dict[str, object]:
    if not isinstance(value, Mapping):
        raise TypeError("log_files must contain mappings")
    filename = str(value.get("filename", ""))
    path = str(value.get("path", ""))
    if not filename:
        raise ValueError("log file filename is required")
    return {
        "name": str(value.get("name", filename)),
        "filename": filename,
        "path": path,
        "bytes": int(value.get("bytes", 0)),
        "sha256": str(value.get("sha256", "")),
    }


def _bundle_status(
    sections: Mapping[str, Mapping[str, object]],
    log_files: tuple[Mapping[str, object], ...],
) -> str:
    present_count = sum(1 for section in sections.values() if section["present"] is True)
    invalid_count = sum(
        1
        for section in sections.values()
        if section["present"] is True and section["valid"] is not True
    )
    if invalid_count > 0:
        return "INVALID"
    if present_count == len(sections) and log_files:
        return "COMPLETE"
    if present_count > 0 or log_files:
        return "PARTIAL"
    return "EMPTY"


def _recommended_next_actions(
    sections: Mapping[str, Mapping[str, object]],
    log_files: tuple[Mapping[str, object], ...],
) -> tuple[str, ...]:
    status = _bundle_status(sections, log_files)
    if status == "COMPLETE":
        return ("Attach the diagnostics bundle directory when reporting issues.",)
    if status == "INVALID":
        return ("Re-run diagnostics collection after restarting services.",)
    if status == "EMPTY":
        return ("Start services or run launcher health before collecting diagnostics.",)
    missing = tuple(
        str(section["name"])
        for section in sections.values()
        if section["present"] is not True
    )
    return (
        "Attach the partial diagnostics bundle and note missing sections.",
        f"Missing sections: {', '.join(missing)}",
    )


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}
