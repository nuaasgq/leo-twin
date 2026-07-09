"""Backend-owned runtime result-closure readiness summary."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from leo_twin.services.runtime_reproducibility import stable_hash_payload


RUNTIME_CLOSURE_READINESS_V1_ID = "leo_twin.runtime_closure_readiness.v1"

_TERMINAL_COMPLETION_REASONS = {
    "RUNTIME_DURATION_REACHED",
    "EVENT_QUEUE_DRAINED_BEFORE_DURATION",
}


def build_runtime_closure_readiness_v1(
    runtime_status: Mapping[str, Any],
) -> dict[str, object]:
    """Return deterministic evidence for whether a run has closed its result loop.

    This summary deliberately differs from ``v2_executable_readiness_v1``:
    executable readiness answers whether the backend surfaces needed by the
    product demo are present, while closure readiness answers whether the
    current run has reached terminal simulation time and accumulated enough
    business, KPI, network, service, and compute evidence to treat the result as
    a completed communication-compute demo loop.
    """

    if not isinstance(runtime_status, Mapping):
        raise TypeError("runtime_status must be a mapping")

    lifecycle_state = str(runtime_status.get("lifecycle_state", ""))
    runtime_completed = lifecycle_state == "COMPLETED"
    gates = (
        _runtime_terminal_gate(runtime_status),
        _kpi_evidence_gate(runtime_status, runtime_completed=runtime_completed),
        _traffic_evidence_gate(runtime_status, runtime_completed=runtime_completed),
        _network_flow_terminal_gate(
            runtime_status,
            runtime_completed=runtime_completed,
        ),
        _service_lifecycle_gate(
            runtime_status,
            runtime_completed=runtime_completed,
        ),
        _compute_resource_gate(runtime_status),
    )
    passed_count = sum(1 for gate in gates if gate["status"] == "PASS")
    waiting_count = sum(1 for gate in gates if gate["status"] == "WAIT")
    failed_count = len(gates) - passed_count - waiting_count
    result_ready = passed_count == len(gates)
    payload: dict[str, object] = {
        "version": "v1",
        "summary_id": RUNTIME_CLOSURE_READINESS_V1_ID,
        "source": "BACKEND_RUNTIME_STATUS",
        "target": "INDUSTRIAL_V2_RUNTIME_RESULT_CLOSURE",
        "lifecycle_state": lifecycle_state,
        "current_sim_time": _float(runtime_status.get("current_sim_time")),
        "runtime_duration_seconds": _float(
            runtime_status.get("runtime_duration_seconds")
        ),
        "runtime_duration_reached": runtime_status.get("runtime_duration_reached")
        is True,
        "runtime_completion_reason": str(
            runtime_status.get("runtime_completion_reason", "")
        ),
        "closure_status": _closure_status(
            lifecycle_state=lifecycle_state,
            result_ready=result_ready,
            failed_count=failed_count,
            waiting_count=waiting_count,
        ),
        "result_ready": result_ready,
        "gate_count": len(gates),
        "passed_gate_count": passed_count,
        "waiting_gate_count": waiting_count,
        "failed_gate_count": failed_count,
        "blocking_gate_ids": tuple(
            str(gate["gate_id"]) for gate in gates if gate["status"] != "PASS"
        ),
        "gates": gates,
        "frontend_inference_required": False,
        "packet_level_simulation": False,
        "model_assumptions": (
            "Runtime closure is derived from backend runtime status fields only.",
            "KPI evidence audits flow-level proxy samples; it does not synthesize movement.",
            "Communication-compute service closure requires observed service lifecycle evidence.",
            "No packet-level simulation, RF propagation, or external simulator is used.",
        ),
        "operator_next_action": _operator_next_action(
            lifecycle_state=lifecycle_state,
            result_ready=result_ready,
            failed_count=failed_count,
            waiting_count=waiting_count,
        ),
    }
    payload["closure_hash"] = stable_hash_payload(payload)
    return payload


def _runtime_terminal_gate(runtime_status: Mapping[str, Any]) -> dict[str, object]:
    lifecycle_state = str(runtime_status.get("lifecycle_state", ""))
    reason = str(runtime_status.get("runtime_completion_reason", ""))
    duration_reached = runtime_status.get("runtime_duration_reached") is True
    completed = lifecycle_state == "COMPLETED"
    terminal_reason = reason in _TERMINAL_COMPLETION_REASONS
    if completed and (duration_reached or terminal_reason):
        status = "PASS"
        issues: tuple[str, ...] = ()
    elif lifecycle_state in {"INITIALIZED", "RUNNING", "PAUSED", "UNINITIALIZED"}:
        status = "WAIT"
        issues = ("runtime has not reached terminal simulation state",)
    else:
        status = "FAIL"
        issues = (f"runtime lifecycle is {lifecycle_state or 'UNKNOWN'}",)
    return _gate(
        gate_id="runtime_terminal",
        label="Runtime terminal state",
        status=status,
        issues=issues,
        runtime_status=runtime_status,
        required_paths=(
            "lifecycle_state",
            "current_sim_time",
            "runtime_duration_seconds",
            "runtime_duration_reached",
            "runtime_completion_reason",
        ),
    )


def _kpi_evidence_gate(
    runtime_status: Mapping[str, Any],
    *,
    runtime_completed: bool,
) -> dict[str, object]:
    sample_count = _int(
        _path_value(runtime_status, "runtime_kpi_movement_summary_v1.sample_count")
    )
    sim_span = _float(
        _path_value(runtime_status, "runtime_kpi_movement_summary_v1.sim_time_span_s")
    )
    dynamic_status = str(
        _path_value(runtime_status, "network_kpi_dynamic_status_v1.dynamic_status")
    )
    enough_samples = sample_count >= 2 and sim_span > 0.0
    dynamic_evidence = dynamic_status not in {
        "",
        "INSUFFICIENT_SERIES",
        "NO_KPI_EVIDENCE",
    }
    if enough_samples and dynamic_evidence:
        status = "PASS"
        issues: tuple[str, ...] = ()
    else:
        status = "FAIL" if runtime_completed else "WAIT"
        issues = _compact(
            None if sample_count >= 2 else "fewer than two KPI samples",
            None if sim_span > 0.0 else "KPI samples do not span simulation time",
            None
            if dynamic_evidence
            else f"network KPI dynamic status is {dynamic_status or 'MISSING'}",
        )
    return _gate(
        gate_id="kpi_series_evidence",
        label="KPI time-series evidence",
        status=status,
        issues=issues,
        runtime_status=runtime_status,
        required_paths=(
            "kpi_time_series_v1.sample_count",
            "runtime_kpi_movement_summary_v1.sample_count",
            "runtime_kpi_movement_summary_v1.sim_time_span_s",
            "network_kpi_dynamic_status_v1.dynamic_status",
        ),
    )


def _traffic_evidence_gate(
    runtime_status: Mapping[str, Any],
    *,
    runtime_completed: bool,
) -> dict[str, object]:
    request_count = _int(_path_value(runtime_status, "traffic_request_timeline_v1.request_count"))
    state_counts = _mapping(
        _path_value(runtime_status, "traffic_request_timeline_v1.state_counts")
    )
    terminal_request_count = _int(state_counts.get("PAST")) + _int(
        state_counts.get("RECENTLY_ARRIVED")
    )
    if request_count > 0 and terminal_request_count > 0:
        status = "PASS"
        issues: tuple[str, ...] = ()
    else:
        status = "FAIL" if runtime_completed else "WAIT"
        issues = _compact(
            None if request_count > 0 else "no configured business requests",
            None
            if terminal_request_count > 0
            else "no arrived or past business requests observed",
        )
    return _gate(
        gate_id="traffic_request_evidence",
        label="Traffic request evidence",
        status=status,
        issues=issues,
        runtime_status=runtime_status,
        required_paths=(
            "traffic_request_timeline_v1.request_count",
            "traffic_request_timeline_v1.state_counts",
            "traffic_business_activity_window_v1.request_count",
        ),
    )


def _network_flow_terminal_gate(
    runtime_status: Mapping[str, Any],
    *,
    runtime_completed: bool,
) -> dict[str, object]:
    active = _int(
        _path_value(runtime_status, "network_flow_lifecycle_summary_v1.active_flow_count")
    )
    completed = _int(
        _path_value(
            runtime_status,
            "network_flow_lifecycle_summary_v1.completed_flow_count",
        )
    )
    failed = _int(
        _path_value(runtime_status, "network_flow_lifecycle_summary_v1.failed_flow_count")
    )
    terminal = completed + failed
    if terminal > 0 and active == 0:
        status = "PASS"
        issues: tuple[str, ...] = ()
    else:
        status = "FAIL" if runtime_completed else "WAIT"
        issues = _compact(
            None if terminal > 0 else "no terminal network flow evidence",
            None if active == 0 else "network flows are still active",
        )
    return _gate(
        gate_id="network_flow_terminal",
        label="Network flow terminal evidence",
        status=status,
        issues=issues,
        runtime_status=runtime_status,
        required_paths=(
            "network_flow_lifecycle_summary_v1.active_flow_count",
            "network_flow_lifecycle_summary_v1.completed_flow_count",
            "network_flow_lifecycle_summary_v1.failed_flow_count",
        ),
    )


def _service_lifecycle_gate(
    runtime_status: Mapping[str, Any],
    *,
    runtime_completed: bool,
) -> dict[str, object]:
    complete = _int(
        _path_value(
            runtime_status,
            "service_lifecycle_stage_summary_v1.complete_service_count",
        )
    )
    incomplete = _int(
        _path_value(
            runtime_status,
            "service_lifecycle_stage_summary_v1.incomplete_service_count",
        )
    )
    if complete > 0 and incomplete == 0:
        status = "PASS"
        issues: tuple[str, ...] = ()
    else:
        status = "FAIL" if runtime_completed else "WAIT"
        issues = _compact(
            None if complete > 0 else "no complete communication-compute service trace",
            None if incomplete == 0 else "service traces are still incomplete",
        )
    return _gate(
        gate_id="communication_compute_service_closure",
        label="Communication-compute service closure",
        status=status,
        issues=issues,
        runtime_status=runtime_status,
        required_paths=(
            "service_lifecycle_stage_summary_v1.complete_service_count",
            "service_lifecycle_stage_summary_v1.incomplete_service_count",
            "service_latency_history_v1.item_count",
        ),
    )


def _compute_resource_gate(runtime_status: Mapping[str, Any]) -> dict[str, object]:
    dimension_count = _int(
        _path_value(runtime_status, "compute_resource_pool_summary_v1.dimension_count")
    )
    if dimension_count >= 7:
        status = "PASS"
        issues: tuple[str, ...] = ()
    else:
        status = "FAIL"
        issues = ("compute resource pool exposes fewer than 7 dimensions",)
    return _gate(
        gate_id="compute_resource_vector",
        label="Compute resource vector evidence",
        status=status,
        issues=issues,
        runtime_status=runtime_status,
        required_paths=(
            "compute_resource_pool_summary_v1.dimension_count",
            "compute_resource_pool_summary_v1.dimensions",
        ),
    )


def _gate(
    *,
    gate_id: str,
    label: str,
    status: str,
    issues: tuple[str, ...],
    runtime_status: Mapping[str, Any],
    required_paths: tuple[str, ...],
) -> dict[str, object]:
    missing_paths = tuple(
        path for path in required_paths if _path_value(runtime_status, path) is _MISSING
    )
    final_status = "FAIL" if missing_paths and status != "WAIT" else status
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
    lifecycle_state: str,
    result_ready: bool,
    failed_count: int,
    waiting_count: int,
) -> str:
    if result_ready:
        return "COMPLETED_RESULT_READY"
    if lifecycle_state == "COMPLETED":
        return "COMPLETED_WITH_RESULT_GAPS"
    if lifecycle_state == "ERROR":
        return "ERROR"
    if lifecycle_state == "STOPPED":
        return "STOPPED_INCOMPLETE"
    if lifecycle_state == "RUNNING":
        return "RUNNING_COLLECTING_EVIDENCE"
    if lifecycle_state == "PAUSED":
        return "PAUSED_COLLECTING_EVIDENCE"
    if failed_count > 0 and waiting_count == 0:
        return "NOT_READY"
    return "NOT_STARTED"


def _operator_next_action(
    *,
    lifecycle_state: str,
    result_ready: bool,
    failed_count: int,
    waiting_count: int,
) -> str:
    if result_ready:
        return "Runtime result closure is ready for v2 demo review and export."
    if lifecycle_state in {"INITIALIZED", "UNINITIALIZED"}:
        return "Start the runtime and wait for backend evidence before reviewing results."
    if lifecycle_state in {"RUNNING", "PAUSED"} or waiting_count > 0:
        return "Continue or resume the runtime until terminal state and evidence gates close."
    if failed_count > 0:
        return "Inspect failed closure gates before treating this run as a completed demo result."
    return "Inspect runtime status before reviewing this run."


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
            "summary_id",
            "status_id",
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


def _mapping(value: object) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    return {}


def _compact(*items: str | None) -> tuple[str, ...]:
    return tuple(item for item in items if item)


def _int(value: object) -> int:
    if value is _MISSING:
        return 0
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return 0


def _float(value: object) -> float:
    if value is _MISSING:
        return 0.0
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return 0.0


__all__ = [
    "RUNTIME_CLOSURE_READINESS_V1_ID",
    "build_runtime_closure_readiness_v1",
]
