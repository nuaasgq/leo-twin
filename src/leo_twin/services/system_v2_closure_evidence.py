"""Backend-owned industrial v2 demo closure evidence."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from leo_twin.services.runtime_reproducibility import stable_hash_payload


SYSTEM_V2_CLOSURE_EVIDENCE_V1_ID = "leo_twin.system_v2_closure_evidence.v1"


def build_system_v2_closure_evidence_v1(
    runtime_status: Mapping[str, Any],
) -> dict[str, object]:
    """Summarize whether the current runtime is ready for v2 demo handoff.

    The summary is a backend observation contract. It reads existing runtime
    status evidence and does not replay events, recompute models, or mutate the
    Event Kernel.
    """

    if not isinstance(runtime_status, Mapping):
        raise TypeError("runtime_status must be a mapping")

    gates = (
        _configuration_closure_gate(runtime_status),
        _executable_readiness_gate(runtime_status),
        _observation_consistency_gate(runtime_status),
        _runtime_result_closure_gate(runtime_status),
        _standard_scenario_acceptance_gate(runtime_status),
        _semantic_evidence_surface_gate(runtime_status),
        _reproducibility_and_package_contract_gate(runtime_status),
    )
    pass_count = sum(1 for gate in gates if gate["status"] == "PASS")
    warn_count = sum(1 for gate in gates if gate["status"] == "WARN")
    wait_count = sum(1 for gate in gates if gate["status"] == "WAIT")
    fail_count = len(gates) - pass_count - warn_count - wait_count
    closure_status = _closure_status(
        pass_count=pass_count,
        warn_count=warn_count,
        wait_count=wait_count,
        fail_count=fail_count,
        gate_count=len(gates),
    )
    payload: dict[str, object] = {
        "version": "v1",
        "closure_id": SYSTEM_V2_CLOSURE_EVIDENCE_V1_ID,
        "source": "BACKEND_RUNTIME_STATUS",
        "target": "INDUSTRIAL_V2_DEMO_CLOSURE_HANDOFF",
        "lifecycle_state": str(runtime_status.get("lifecycle_state", "")),
        "current_sim_time": _number(runtime_status.get("current_sim_time")),
        "runtime_observation_sim_time": _number(
            runtime_status.get("runtime_observation_sim_time")
        ),
        "runtime_duration_seconds": _number(
            runtime_status.get("runtime_duration_seconds")
        ),
        "runtime_duration_reached": runtime_status.get("runtime_duration_reached")
        is True,
        "processed_event_count": _integer(runtime_status.get("processed_event_count")),
        "queued_event_count": _integer(runtime_status.get("queued_event_count")),
        "closure_status": closure_status,
        "demo_loop_closed": closure_status == "SEALED",
        "gate_count": len(gates),
        "passed_gate_count": pass_count,
        "warning_gate_count": warn_count,
        "waiting_gate_count": wait_count,
        "failed_gate_count": fail_count,
        "blocking_gate_ids": tuple(
            str(gate["gate_id"]) for gate in gates if gate["status"] == "FAIL"
        ),
        "warning_gate_ids": tuple(
            str(gate["gate_id"]) for gate in gates if gate["status"] == "WARN"
        ),
        "waiting_gate_ids": tuple(
            str(gate["gate_id"]) for gate in gates if gate["status"] == "WAIT"
        ),
        "gates": gates,
        "frontend_inference_required": False,
        "packet_level_simulation": False,
        "event_kernel_policy": "NO_EVENT_KERNEL_BEHAVIOR_CHANGE",
        "forbidden_external_integrations": ("STK", "EXATA", "AFSIM", "DDS"),
        "model_boundaries": (
            "DETERMINISTIC_DISCRETE_EVENT_RUNTIME_STATUS_EVIDENCE",
            "FLOW_LEVEL_NETWORK_AND_SERVICE_EVIDENCE",
            "NO_PACKET_LEVEL_SIMULATION",
            "NO_EXTERNAL_SIMULATOR",
            "NO_EVENT_KERNEL_CHANGE",
        ),
        "operator_next_action": _operator_next_action(closure_status),
    }
    payload["closure_hash"] = stable_hash_payload(payload)
    return payload


def _configuration_closure_gate(
    runtime_status: Mapping[str, Any],
) -> dict[str, object]:
    closure = _mapping(_path_value(runtime_status, "user_configuration_closure_v2"))
    if not closure:
        return _gate(
            gate_id="configuration_closure",
            label="User configuration closure",
            status="FAIL",
            required_paths=("user_configuration_closure_v2",),
            runtime_status=runtime_status,
            issues=("user_configuration_closure_v2 is missing",),
        )
    ready = (
        str(closure.get("closure_status", "")) == "READY"
        and closure.get("configuration_ready") is True
        and _integer(closure.get("failed_gate_count")) == 0
    )
    return _gate(
        gate_id="configuration_closure",
        label="User configuration closure",
        status="PASS" if ready else "FAIL",
        required_paths=(
            "user_configuration_closure_v2.closure_status",
            "user_configuration_closure_v2.configuration_ready",
            "user_configuration_closure_v2.failed_gate_count",
        ),
        runtime_status=runtime_status,
        issues=() if ready else ("user configuration closure is not READY",),
    )


def _executable_readiness_gate(
    runtime_status: Mapping[str, Any],
) -> dict[str, object]:
    readiness = _mapping(_path_value(runtime_status, "v2_executable_readiness_v1"))
    ready = (
        readiness.get("executable_ready") is True
        and str(readiness.get("readiness_status", "")) == "READY"
        and _integer(readiness.get("failed_gate_count")) == 0
    )
    return _gate(
        gate_id="executable_readiness",
        label="Executable v2 readiness",
        status="PASS" if ready else "FAIL",
        required_paths=(
            "v2_executable_readiness_v1.readiness_status",
            "v2_executable_readiness_v1.executable_ready",
            "v2_executable_readiness_v1.failed_gate_count",
        ),
        runtime_status=runtime_status,
        issues=() if ready else ("v2 executable readiness is not READY",),
    )


def _observation_consistency_gate(
    runtime_status: Mapping[str, Any],
) -> dict[str, object]:
    consistency = _mapping(
        _path_value(runtime_status, "runtime_observation_consistency_v1")
    )
    status = str(consistency.get("consistency_status", ""))
    failed_count = _integer(consistency.get("failed_check_count"))
    if status == "CONSISTENT" and failed_count == 0:
        gate_status = "PASS"
        issues: tuple[str, ...] = ()
    elif status == "OBSERVING":
        gate_status = "WAIT"
        issues = ("runtime observation consistency is still collecting evidence",)
    else:
        gate_status = "FAIL"
        issues = ("runtime observation consistency is not CONSISTENT",)
    return _gate(
        gate_id="observation_consistency",
        label="Runtime observation consistency",
        status=gate_status,
        required_paths=(
            "runtime_observation_consistency_v1.consistency_status",
            "runtime_observation_consistency_v1.failed_check_count",
        ),
        runtime_status=runtime_status,
        issues=issues,
    )


def _runtime_result_closure_gate(
    runtime_status: Mapping[str, Any],
) -> dict[str, object]:
    closure = _mapping(_path_value(runtime_status, "runtime_closure_readiness_v1"))
    result_ready = closure.get("result_ready") is True
    closure_status = str(closure.get("closure_status", ""))
    lifecycle_state = str(runtime_status.get("lifecycle_state", ""))
    if result_ready and closure_status == "COMPLETED_RESULT_READY":
        gate_status = "PASS"
        issues: tuple[str, ...] = ()
    elif lifecycle_state in {"INITIALIZED", "RUNNING", "PAUSED", "UNINITIALIZED"}:
        gate_status = "WAIT"
        issues = ("runtime has not reached completed result closure yet",)
    else:
        gate_status = "FAIL"
        issues = tuple(
            str(item) for item in _string_tuple(closure.get("blocking_gate_ids"))
        ) or ("runtime closure readiness is not result-ready",)
    return _gate(
        gate_id="runtime_result_closure",
        label="Runtime result closure",
        status=gate_status,
        required_paths=(
            "runtime_closure_readiness_v1.closure_status",
            "runtime_closure_readiness_v1.result_ready",
            "runtime_closure_readiness_v1.failed_gate_count",
        ),
        runtime_status=runtime_status,
        issues=issues,
    )


def _standard_scenario_acceptance_gate(
    runtime_status: Mapping[str, Any],
) -> dict[str, object]:
    acceptance = _mapping(
        _path_value(runtime_status, "standard_scenario_acceptance_v2")
    )
    acceptance_status = str(acceptance.get("acceptance_status", ""))
    if acceptance_status == "PASS":
        gate_status = "PASS"
        issues: tuple[str, ...] = ()
    elif acceptance_status == "WARN":
        gate_status = "WARN"
        issues = ("runtime config is custom or partially matches a standard scenario",)
    else:
        gate_status = "FAIL"
        issues = ("standard scenario acceptance is not PASS",)
    return _gate(
        gate_id="standard_scenario_acceptance",
        label="Standard scenario acceptance",
        status=gate_status,
        required_paths=(
            "standard_scenario_acceptance_v2.acceptance_status",
            "standard_scenario_acceptance_v2.current_scenario_id",
            "standard_scenario_acceptance_v2.result_package_evidence_filenames",
        ),
        runtime_status=runtime_status,
        issues=issues,
    )


def _semantic_evidence_surface_gate(
    runtime_status: Mapping[str, Any],
) -> dict[str, object]:
    required_paths = (
        "network_kpi_assurance_v2",
        "business_request_lifecycle_v2",
        "compute_service_resource_evidence_v1",
        "user_service_request_summary_v2",
        "compute_resource_pool_summary_v1",
    )
    boundary_issues = tuple(
        issue
        for path in required_paths
        for issue in _boundary_issues(runtime_status, path)
    )
    missing = tuple(path for path in required_paths if _path_value(runtime_status, path) is _MISSING)
    return _gate(
        gate_id="semantic_evidence_surfaces",
        label="Network, business, and compute semantic evidence",
        status="FAIL" if missing or boundary_issues else "PASS",
        required_paths=required_paths,
        runtime_status=runtime_status,
        issues=(*boundary_issues, *(f"{path} is missing" for path in missing)),
    )


def _reproducibility_and_package_contract_gate(
    runtime_status: Mapping[str, Any],
) -> dict[str, object]:
    filenames = _string_tuple(
        _path_value(
            runtime_status,
            "standard_scenario_acceptance_v2.result_package_evidence_filenames",
        )
    )
    required_package_files = (
        "config_snapshot.json",
        "manifest.json",
        "standard_scenario_acceptance_v2.json",
        "system_v2_closure_evidence_v1.json",
        "package_handoff_report_v1.md",
    )
    missing_package_files = tuple(
        filename for filename in required_package_files if filename not in filenames
    )
    manifest_id = str(
        _path_value(runtime_status, "reproducibility_manifest_v1.manifest_id")
    )
    manifest_ready = bool(manifest_id and manifest_id != str(_MISSING))
    status = "PASS" if manifest_ready and not missing_package_files else "FAIL"
    issues = _compact(
        None if manifest_ready else "reproducibility manifest is missing",
        *(
            f"standard scenario package evidence omits {filename}"
            for filename in missing_package_files
        ),
    )
    return _gate(
        gate_id="reproducibility_and_package_contract",
        label="Reproducibility and package evidence contract",
        status=status,
        required_paths=(
            "reproducibility_manifest_v1.manifest_id",
            "reproducibility_manifest_v1.runtime_state_hash",
            "standard_scenario_acceptance_v2.result_package_evidence_filenames",
        ),
        runtime_status=runtime_status,
        issues=issues,
    )


def _gate(
    *,
    gate_id: str,
    label: str,
    status: str,
    required_paths: tuple[str, ...],
    runtime_status: Mapping[str, Any],
    issues: tuple[str, ...],
) -> dict[str, object]:
    missing_paths = tuple(
        path for path in required_paths if _path_value(runtime_status, path) is _MISSING
    )
    final_status = "FAIL" if missing_paths and status == "PASS" else status
    return {
        "gate_id": gate_id,
        "label": label,
        "status": final_status,
        "required_paths": required_paths,
        "missing_paths": missing_paths,
        "issue_count": len(issues) + len(missing_paths),
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


def _closure_status(
    *,
    pass_count: int,
    warn_count: int,
    wait_count: int,
    fail_count: int,
    gate_count: int,
) -> str:
    if fail_count > 0:
        return "NOT_SEALED"
    if wait_count > 0:
        return "COLLECTING_EVIDENCE"
    if warn_count > 0:
        return "SEALED_WITH_WARNINGS"
    if pass_count == gate_count:
        return "SEALED"
    return "UNKNOWN"


def _operator_next_action(closure_status: str) -> str:
    if closure_status == "SEALED":
        return "V2 demo closure evidence is ready for package handoff."
    if closure_status == "SEALED_WITH_WARNINGS":
        return "Review warning gates before treating this as a standard v2 demo handoff."
    if closure_status == "COLLECTING_EVIDENCE":
        return "Let the runtime complete and export the result package after closure gates pass."
    if closure_status == "NOT_SEALED":
        return "Inspect failed closure gates before v2 demo handoff."
    return "Inspect runtime status before v2 demo handoff."


def _boundary_issues(
    runtime_status: Mapping[str, Any],
    path: str,
) -> tuple[str, ...]:
    value = _path_value(runtime_status, path)
    if not isinstance(value, Mapping):
        return ()
    return _compact(
        f"{path} reports packet_level_simulation=true"
        if value.get("packet_level_simulation") is True
        else None,
        f"{path} requires frontend inference"
        if value.get("frontend_inference_required") is True
        else None,
    )


_MISSING = object()


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
            "closure_id",
            "summary_id",
            "readiness_id",
            "acceptance_id",
            "version",
            "source",
        ):
            if key in value:
                return {"type": "mapping", key: value[key]}
        return {"type": "mapping", "key_count": len(value)}
    if isinstance(value, tuple | list):
        return {"type": "sequence", "item_count": len(value)}
    return value


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _string_tuple(value: object) -> tuple[str, ...]:
    if isinstance(value, (str, bytes)):
        return (str(value),) if value else ()
    if isinstance(value, tuple | list):
        return tuple(str(item) for item in value)
    return ()


def _compact(*items: str | None) -> tuple[str, ...]:
    return tuple(item for item in items if item)


def _integer(value: object) -> int:
    if isinstance(value, bool) or value is _MISSING:
        return 0
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return 0


def _number(value: object) -> float:
    if isinstance(value, bool) or value is _MISSING:
        return 0.0
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return 0.0


__all__ = [
    "SYSTEM_V2_CLOSURE_EVIDENCE_V1_ID",
    "build_system_v2_closure_evidence_v1",
]
