"""Product contract and validation helpers for runtime result packages."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


RESULT_PACKAGE_CONTRACT_V1_ID = "leo_twin.result_package_contract.v1"
RUNTIME_REPRODUCIBILITY_MANIFEST_V1_ID = (
    "leo_twin.runtime_reproducibility_manifest.v1"
)


_REQUIRED_FILE_SPECS: tuple[dict[str, object], ...] = (
    {
        "logical_name": "config_snapshot",
        "filename": "config_snapshot.json",
        "format": "json",
        "content": "runtime status, applied SEES config, generated backend config",
    },
    {
        "logical_name": "events",
        "filename": "events.jsonl",
        "format": "jsonl",
        "content": "deterministically ordered processed runtime events",
    },
    {
        "logical_name": "metrics",
        "filename": "metrics.csv",
        "format": "csv",
        "content": "sampled metric records and KPI observations",
    },
    {
        "logical_name": "summary",
        "filename": "summary.json",
        "format": "json",
        "content": "metrics summary and aggregate runtime counters",
    },
    {
        "logical_name": "manifest",
        "filename": "manifest.json",
        "format": "json",
        "content": "runtime reproducibility manifest with stable hashes",
    },
)


def result_package_contract_v1_to_dict() -> dict[str, object]:
    """Return the deterministic product contract for exported result packages."""

    return {
        "contract_id": RESULT_PACKAGE_CONTRACT_V1_ID,
        "version": "v1",
        "package_type": "RUNTIME_EXPORT",
        "source_endpoints": (
            "GET /runtime/export",
            "GET /runtime/export/archive",
            "GET /runtime/export/catalog",
            "GET /runtime/export/packages/{package_id}",
            "GET /runtime/export/packages/{package_id}/manifest",
            "GET /runtime/export/packages/{package_id}/files/{filename}",
        ),
        "catalog_filename": "runtime_export_catalog_v1.json",
        "required_files": _REQUIRED_FILE_SPECS,
        "required_file_count": len(_REQUIRED_FILE_SPECS),
        "required_manifest_id": RUNTIME_REPRODUCIBILITY_MANIFEST_V1_ID,
        "hash_policy": {
            "file_hash": "sha256 over artifact bytes",
            "manifest_hash": "stable canonical JSON hash",
            "catalog_hash_source": "catalog records include file hashes",
        },
        "archive_policy": {
            "format": "zip",
            "deterministic_entry_timestamp": "2026-01-01T00:00:00",
            "entry_order": "filename ascending",
        },
        "restore_policy": {
            "restore_scope": "configuration restore through control plane",
            "rollback_export": "write rollback package before applying restore",
            "event_replay": "not applied to live runtime in v1",
        },
        "benchmark_binding": {
            "matrix_id": "leo_twin.benchmark_scenario_matrix.v1",
            "verification_template_id": "leo_twin.model_verification_report_template.v1",
            "evidence_role": (
                "A benchmark run result package should provide config, events, "
                "metrics, summary, and manifest evidence for review."
            ),
        },
        "excluded_semantics": (
            "PACKET_CAPTURE",
            "BINARY_TRACE_FORMAT",
            "EXTERNAL_SIMULATOR_ARTIFACT",
            "LIVE_EVENT_REPLAY_RESTORE",
        ),
    }


def summarize_result_package_record_v1(
    package: Mapping[str, Any],
) -> dict[str, object]:
    """Summarize whether a runtime export package satisfies the v1 contract."""

    if not isinstance(package, Mapping):
        raise TypeError("package must be a mapping")
    contract = result_package_contract_v1_to_dict()
    required_files = tuple(
        str(spec["filename"]) for spec in contract["required_files"]  # type: ignore[index]
    )
    file_records = tuple(_file_records(package.get("files")))
    filenames = tuple(sorted(str(record.get("filename", "")) for record in file_records))
    present_required = tuple(filename for filename in required_files if filename in filenames)
    missing_required = tuple(
        filename for filename in required_files if filename not in filenames
    )
    manifest = _mapping(package.get("manifest"))
    manifest_id = str(manifest.get("manifest_id", ""))
    file_hashes = tuple(
        str(record.get("sha256", ""))
        for record in sorted(file_records, key=lambda item: str(item.get("filename", "")))
        if str(record.get("sha256", "")).startswith("sha256:")
    )
    package_ok = package.get("ok") is True
    manifest_ok = manifest_id == RUNTIME_REPRODUCIBILITY_MANIFEST_V1_ID
    return {
        "contract_id": RESULT_PACKAGE_CONTRACT_V1_ID,
        "package_id": str(package.get("package_id", "")),
        "package_type": str(package.get("type", "")),
        "package_ok": package_ok,
        "package_dir": str(package.get("package_dir", "")),
        "file_count": len(file_records),
        "required_file_count": len(required_files),
        "present_required_files": present_required,
        "missing_required_files": missing_required,
        "package_complete": package_ok and manifest_ok and not missing_required,
        "manifest_id": manifest_id,
        "manifest_hash": str(manifest.get("manifest_hash", "")),
        "file_hash_count": len(file_hashes),
        "file_hashes": file_hashes,
        "catalog_record_present": isinstance(
            package.get("export_catalog_record"),
            Mapping,
        ),
        "history_record_present": isinstance(
            package.get("export_history_record"),
            Mapping,
        ),
    }


def _file_records(value: object) -> tuple[Mapping[str, Any], ...]:
    if not isinstance(value, (list, tuple)):
        return ()
    return tuple(item for item in value if isinstance(item, Mapping))


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}
