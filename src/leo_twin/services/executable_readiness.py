"""Backend-owned executable v2 readiness summary."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from leo_twin.services.runtime_reproducibility import stable_hash_payload


V2_EXECUTABLE_READINESS_V1_ID = "leo_twin.v2_executable_readiness.v1"

_GATE_SPECS: tuple[dict[str, object], ...] = (
    {
        "gate_id": "configuration_contract",
        "label": "User configuration contract",
        "required_paths": (
            "configuration_surface_summary",
            "user_configuration_control_surface_evidence_v1.coverage_status",
        ),
    },
    {
        "gate_id": "runtime_control",
        "label": "Runtime session control",
        "required_paths": (
            "lifecycle_state",
            "current_sim_time",
            "processed_event_count",
            "queued_event_count",
            "runtime_duration_seconds",
            "runtime_completion_source",
            "stream_diagnostics_v1.event_stream",
            "stream_diagnostics_v1.state_stream",
        ),
    },
    {
        "gate_id": "traffic_business",
        "label": "Traffic business state",
        "required_paths": (
            "traffic_request_timeline_v1",
            "traffic_business_activity_window_v1",
        ),
    },
    {
        "gate_id": "network_kpi",
        "label": "Network KPI evidence",
        "required_paths": (
            "metrics_summary.network_quality_effective_throughput_mbps",
            "metrics_summary.network_quality_effective_latency_avg_s",
            "metrics_summary.network_quality_loss_proxy_rate",
            "metrics_summary.network_quality_effective_delay_variation_proxy_s",
            "network_kpi_provenance_v2",
            "network_kpi_formula_evidence_v1",
        ),
    },
    {
        "gate_id": "compute_resource",
        "label": "Compute resource pool",
        "required_paths": (
            "compute_resource_pool_summary_v1",
            "compute_resource_pool_summary_v1.dimension_count",
            "compute_resource_pool_summary_v1.dimensions",
        ),
    },
    {
        "gate_id": "node_detail",
        "label": "User and satellite node detail",
        "required_paths": (
            "user_request_summary_v1",
            "user_service_request_summary_v2",
            "satellite_service_summary_v1",
            "node_detail_summary_v1",
        ),
    },
    {
        "gate_id": "scale_fidelity",
        "label": "Scale fidelity notice",
        "required_paths": (
            "fidelity_summary.orbit_update_mode",
            "fidelity_summary.metrics_mode",
            "fidelity_summary.space_link_mode",
            "fidelity_summary.satellite_count",
            "fidelity_summary.user_count",
        ),
    },
    {
        "gate_id": "reproducibility_export",
        "label": "Reproducibility and export surface",
        "required_paths": (
            "reproducibility_manifest_v1.manifest_id",
            "reproducibility_manifest_v1.runtime_state_hash",
            "runtime_export_history_v1",
        ),
    },
)


def build_v2_executable_readiness_v1(
    runtime_status: Mapping[str, Any],
) -> dict[str, object]:
    """Return deterministic readiness evidence for the executable v2 demo loop."""

    if not isinstance(runtime_status, Mapping):
        raise TypeError("runtime_status must be a mapping")
    gates = tuple(_readiness_gate(runtime_status, spec) for spec in _GATE_SPECS)
    passed_count = sum(1 for gate in gates if gate["status"] == "PASS")
    failed_count = len(gates) - passed_count
    readiness_status = "READY" if failed_count == 0 else "NOT_READY"
    result: dict[str, object] = {
        "version": "v1",
        "readiness_id": V2_EXECUTABLE_READINESS_V1_ID,
        "source": "BACKEND_RUNTIME_STATUS",
        "target": "INDUSTRIAL_V2_EXECUTABLE_DEMO_LOOP",
        "readiness_status": readiness_status,
        "executable_ready": readiness_status == "READY",
        "gate_count": len(gates),
        "passed_gate_count": passed_count,
        "failed_gate_count": failed_count,
        "gates": gates,
        "missing_required_gate_ids": tuple(
            str(gate["gate_id"]) for gate in gates if gate["status"] != "PASS"
        ),
        "frontend_inference_required": False,
        "packet_level_simulation": False,
        "model_boundaries": {
            "event_kernel_policy": "NO_EVENT_KERNEL_BEHAVIOR_CHANGE",
            "packet_level_simulation": False,
            "external_simulators": False,
            "forbidden_integrations": ("STK", "EXATA", "AFSIM", "DDS"),
        },
        "operator_next_action": (
            "Executable v2 demo loop has required backend evidence."
            if readiness_status == "READY"
            else "Inspect failed gates before treating this run as a v2 executable demo."
        ),
    }
    result["readiness_hash"] = stable_hash_payload(result)
    return result


def _readiness_gate(
    runtime_status: Mapping[str, Any],
    spec: Mapping[str, object],
) -> dict[str, object]:
    gate_id = str(spec["gate_id"])
    required_paths = tuple(str(path) for path in spec["required_paths"])
    missing_paths = tuple(
        path for path in required_paths if not _path_present(runtime_status, path)
    )
    issues = _gate_issues(gate_id, runtime_status)
    status = "FAIL" if missing_paths or issues else "PASS"
    return {
        "gate_id": gate_id,
        "label": str(spec["label"]),
        "status": status,
        "required_paths": required_paths,
        "missing_paths": missing_paths,
        "issue_count": len(issues),
        "issues": issues,
        "evidence": tuple(
            _gate_evidence_row(runtime_status, path) for path in required_paths
        ),
    }


def _gate_evidence_row(
    runtime_status: Mapping[str, Any],
    path: str,
) -> dict[str, object]:
    value = _path_value(runtime_status, path)
    return {
        "path": path,
        "present": value is not _MISSING,
        "value_summary": _value_summary(value),
    }


def _gate_issues(gate_id: str, runtime_status: Mapping[str, Any]) -> tuple[str, ...]:
    issues: list[str] = []
    if gate_id == "configuration_contract":
        coverage = _path_value(
            runtime_status,
            "user_configuration_control_surface_evidence_v1.coverage_status",
        )
        if coverage is not _MISSING and coverage != "COMPLETE":
            issues.append("configuration control surface coverage is not COMPLETE")
    if gate_id == "traffic_business":
        for path in (
            "traffic_request_timeline_v1",
            "traffic_business_activity_window_v1",
        ):
            _append_boundary_issues(issues, runtime_status, path)
    if gate_id == "network_kpi":
        _append_boundary_issues(issues, runtime_status, "network_kpi_provenance_v2")
        _append_boundary_issues(issues, runtime_status, "network_kpi_formula_evidence_v1")
    if gate_id == "compute_resource":
        dimension_count = _path_value(
            runtime_status,
            "compute_resource_pool_summary_v1.dimension_count",
        )
        if isinstance(dimension_count, int) and dimension_count < 7:
            issues.append("compute resource pool exposes fewer than 7 dimensions")
        _append_boundary_issues(issues, runtime_status, "compute_resource_pool_summary_v1")
    return tuple(issues)


def _append_boundary_issues(
    issues: list[str],
    runtime_status: Mapping[str, Any],
    path: str,
) -> None:
    value = _path_value(runtime_status, path)
    if not isinstance(value, Mapping):
        return
    if value.get("packet_level_simulation") is True:
        issues.append(f"{path} reports packet_level_simulation=true")
    if value.get("frontend_inference_required") is True:
        issues.append(f"{path} requires frontend inference")


_MISSING = object()


def _path_present(data: Mapping[str, Any], path: str) -> bool:
    value = _path_value(data, path)
    return value is not _MISSING and value is not None


def _path_value(data: Mapping[str, Any], path: str) -> object:
    current: object = data
    for part in path.split("."):
        if not isinstance(current, Mapping) or part not in current:
            return _MISSING
        current = current[part]
    return current


def _value_summary(value: object) -> object:
    if value is _MISSING:
        return "MISSING"
    if isinstance(value, Mapping):
        for key in (
            "summary_id",
            "manifest_id",
            "evidence_id",
            "readiness_id",
            "version",
            "source",
        ):
            if key in value:
                return {"type": "mapping", key: value[key]}
        return {"type": "mapping", "key_count": len(value)}
    if isinstance(value, tuple | list):
        return {"type": "sequence", "item_count": len(value)}
    return value


__all__ = [
    "V2_EXECUTABLE_READINESS_V1_ID",
    "build_v2_executable_readiness_v1",
]
