"""Runtime observation consistency evidence for live status consumers."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from leo_twin.services.runtime_reproducibility import stable_hash_payload


RUNTIME_OBSERVATION_CONSISTENCY_V1_ID = (
    "leo_twin.runtime_observation_consistency.v1"
)

_EPSILON = 1e-6


def build_runtime_observation_consistency_v1(
    runtime_status: Mapping[str, Any],
) -> dict[str, object]:
    """Audit whether runtime, KPI, metrics, and traffic observations align.

    The builder reads backend-owned status fields only. It does not replay
    events, synthesize KPI movement, or infer frontend state.
    """

    if not isinstance(runtime_status, Mapping):
        raise TypeError("runtime_status must be a mapping")

    checks = (
        _metrics_observation_time_check(runtime_status),
        _metrics_event_time_bounds_check(runtime_status),
        _event_count_alignment_check(runtime_status),
        _kpi_tail_alignment_check(runtime_status),
        _traffic_timeline_alignment_check(runtime_status),
        _traffic_business_window_alignment_check(runtime_status),
        _closure_readiness_alignment_check(runtime_status),
    )
    pass_count = sum(1 for check in checks if check["status"] == "PASS")
    wait_count = sum(1 for check in checks if check["status"] == "WAIT")
    fail_count = len(checks) - pass_count - wait_count
    payload: dict[str, object] = {
        "version": "v1",
        "summary_id": RUNTIME_OBSERVATION_CONSISTENCY_V1_ID,
        "source": "BACKEND_RUNTIME_STATUS",
        "target": "LIVE_RUNTIME_OBSERVATION_CONSISTENCY",
        "lifecycle_state": str(runtime_status.get("lifecycle_state", "")),
        "current_sim_time": _number(runtime_status.get("current_sim_time")),
        "runtime_observation_sim_time": _observation_sim_time(runtime_status),
        "runtime_observation_time_source": str(
            runtime_status.get("runtime_observation_time_source", "")
        ),
        "processed_event_count": _integer(runtime_status.get("processed_event_count")),
        "queued_event_count": _integer(runtime_status.get("queued_event_count")),
        "runtime_duration_seconds": _number(
            runtime_status.get("runtime_duration_seconds")
        ),
        "runtime_duration_reached": runtime_status.get("runtime_duration_reached")
        is True,
        "metrics_summary_event_time_s": _path_number(
            runtime_status,
            "metrics_summary.metrics_summary_event_time_s",
            "metrics_summary.last_sim_time",
        ),
        "metrics_summary_observation_time_s": _path_number(
            runtime_status,
            "metrics_summary.metrics_summary_observation_time_s",
        ),
        "kpi_time_series_sample_count": _integer(
            _path_value(runtime_status, "kpi_time_series_v1.sample_count")
        ),
        "kpi_time_series_tail_sim_time_s": _kpi_tail_sim_time(runtime_status),
        "traffic_timeline_current_sim_time": _path_number(
            runtime_status,
            "traffic_request_timeline_v1.current_sim_time",
        ),
        "traffic_business_window_current_sim_time": _path_number(
            runtime_status,
            "traffic_business_activity_window_v1.current_sim_time",
        ),
        "closure_readiness_status": str(
            _path_value(runtime_status, "runtime_closure_readiness_v1.closure_status")
            or ""
        ),
        "check_count": len(checks),
        "passed_check_count": pass_count,
        "waiting_check_count": wait_count,
        "failed_check_count": fail_count,
        "consistency_status": _consistency_status(
            passed_count=pass_count,
            waiting_count=wait_count,
            failed_count=fail_count,
            check_count=len(checks),
        ),
        "blocking_check_ids": tuple(
            str(check["check_id"]) for check in checks if check["status"] == "FAIL"
        ),
        "waiting_check_ids": tuple(
            str(check["check_id"]) for check in checks if check["status"] == "WAIT"
        ),
        "checks": checks,
        "frontend_inference_required": False,
        "packet_level_simulation": False,
        "model_assumptions": (
            "Observation consistency is derived from backend runtime status fields.",
            "Metrics observation time should follow runtime current_sim_time; event time may lag between discrete events.",
            "KPI and traffic windows are checked for time alignment, not for packet-level fidelity.",
            "No frontend-side inference is required to decide whether observations are synchronized.",
        ),
    }
    payload["consistency_hash"] = stable_hash_payload(payload)
    return payload


def _metrics_observation_time_check(
    runtime_status: Mapping[str, Any],
) -> dict[str, object]:
    observation_time = _observation_sim_time(runtime_status)
    observed = _path_number(
        runtime_status,
        "metrics_summary.metrics_summary_observation_time_s",
    )
    if observation_time is None or observed is None:
        return _check(
            "metrics_observation_time",
            "Metrics observation time",
            "WAIT",
            ("runtime or metrics observation time is not available",),
            (
                "runtime_observation_sim_time",
                "metrics_summary.metrics_summary_observation_time_s",
            ),
            observed_value=observed,
            expected_value=observation_time,
        )
    status = "PASS" if _same_time(observation_time, observed) else "FAIL"
    issues = (
        ()
        if status == "PASS"
        else ("metrics observation time differs from runtime_observation_sim_time",)
    )
    return _check(
        "metrics_observation_time",
        "Metrics observation time",
        status,
        issues,
        (
            "runtime_observation_sim_time",
            "metrics_summary.metrics_summary_observation_time_s",
        ),
        observed_value=observed,
        expected_value=observation_time,
    )


def _metrics_event_time_bounds_check(
    runtime_status: Mapping[str, Any],
) -> dict[str, object]:
    observation_time = _observation_sim_time(runtime_status)
    event_time = _path_number(
        runtime_status,
        "metrics_summary.metrics_summary_event_time_s",
        "metrics_summary.last_sim_time",
    )
    if observation_time is None or event_time is None:
        return _check(
            "metrics_event_time_bounds",
            "Metrics event-time bounds",
            "WAIT",
            ("runtime or metrics event time is not available",),
            (
                "runtime_observation_sim_time",
                "metrics_summary.metrics_summary_event_time_s",
            ),
            observed_value=event_time,
            expected_value=observation_time,
        )
    status = "PASS" if event_time <= observation_time + _EPSILON else "FAIL"
    issues = (
        ()
        if status == "PASS"
        else ("metrics event time is ahead of runtime_observation_sim_time",)
    )
    return _check(
        "metrics_event_time_bounds",
        "Metrics event-time bounds",
        status,
        issues,
        (
            "runtime_observation_sim_time",
            "metrics_summary.metrics_summary_event_time_s",
        ),
        observed_value=event_time,
        expected_value=observation_time,
    )


def _event_count_alignment_check(
    runtime_status: Mapping[str, Any],
) -> dict[str, object]:
    processed = _integer(runtime_status.get("processed_event_count"))
    metric_count = _integer(_path_value(runtime_status, "metrics_summary.event_count"))
    if processed is None or metric_count is None:
        return _check(
            "event_count_alignment",
            "Runtime and metrics event count",
            "WAIT",
            ("runtime or metrics event count is not available",),
            ("processed_event_count", "metrics_summary.event_count"),
            observed_value=metric_count,
            expected_value=processed,
        )
    status = "PASS" if metric_count <= processed else "FAIL"
    issues = () if status == "PASS" else ("metrics event_count exceeds runtime processed_event_count",)
    return _check(
        "event_count_alignment",
        "Runtime and metrics event count",
        status,
        issues,
        ("processed_event_count", "metrics_summary.event_count"),
        observed_value=metric_count,
        expected_value=processed,
    )


def _kpi_tail_alignment_check(
    runtime_status: Mapping[str, Any],
) -> dict[str, object]:
    observation_time = _observation_sim_time(runtime_status)
    sample_count = _integer(_path_value(runtime_status, "kpi_time_series_v1.sample_count"))
    tail_time = _kpi_tail_sim_time(runtime_status)
    if (
        sample_count is None
        or sample_count <= 0
        or observation_time is None
        or tail_time is None
    ):
        return _check(
            "kpi_tail_time",
            "KPI time-series tail",
            "WAIT",
            ("KPI time-series tail is not available yet",),
            (
                "runtime_observation_sim_time",
                "kpi_time_series_v1.samples[-1].sim_time",
            ),
            observed_value=tail_time,
            expected_value=observation_time,
        )
    status = "PASS" if _same_time(observation_time, tail_time) else "FAIL"
    issues = (
        ()
        if status == "PASS"
        else ("KPI tail sample time differs from runtime_observation_sim_time",)
    )
    return _check(
        "kpi_tail_time",
        "KPI time-series tail",
        status,
        issues,
        (
            "runtime_observation_sim_time",
            "kpi_time_series_v1.samples[-1].sim_time",
        ),
        observed_value=tail_time,
        expected_value=observation_time,
    )


def _traffic_timeline_alignment_check(
    runtime_status: Mapping[str, Any],
) -> dict[str, object]:
    observation_time = _observation_sim_time(runtime_status)
    timeline_time = _path_number(
        runtime_status,
        "traffic_request_timeline_v1.current_sim_time",
    )
    if observation_time is None or timeline_time is None:
        return _check(
            "traffic_timeline_time",
            "Traffic request timeline time",
            "WAIT",
            ("traffic request timeline current time is not available",),
            (
                "runtime_observation_sim_time",
                "traffic_request_timeline_v1.current_sim_time",
            ),
            observed_value=timeline_time,
            expected_value=observation_time,
        )
    status = "PASS" if _same_time(observation_time, timeline_time) else "FAIL"
    issues = (
        ()
        if status == "PASS"
        else ("traffic timeline time differs from runtime_observation_sim_time",)
    )
    return _check(
        "traffic_timeline_time",
        "Traffic request timeline time",
        status,
        issues,
        (
            "runtime_observation_sim_time",
            "traffic_request_timeline_v1.current_sim_time",
        ),
        observed_value=timeline_time,
        expected_value=observation_time,
    )


def _traffic_business_window_alignment_check(
    runtime_status: Mapping[str, Any],
) -> dict[str, object]:
    observation_time = _observation_sim_time(runtime_status)
    window_time = _path_number(
        runtime_status,
        "traffic_business_activity_window_v1.current_sim_time",
    )
    if observation_time is None or window_time is None:
        return _check(
            "traffic_business_window_time",
            "Traffic business window time",
            "WAIT",
            ("traffic business window current time is not available",),
            (
                "runtime_observation_sim_time",
                "traffic_business_activity_window_v1.current_sim_time",
            ),
            observed_value=window_time,
            expected_value=observation_time,
        )
    status = "PASS" if _same_time(observation_time, window_time) else "FAIL"
    issues = (
        ()
        if status == "PASS"
        else ("traffic business window time differs from runtime_observation_sim_time",)
    )
    return _check(
        "traffic_business_window_time",
        "Traffic business window time",
        status,
        issues,
        (
            "runtime_observation_sim_time",
            "traffic_business_activity_window_v1.current_sim_time",
        ),
        observed_value=window_time,
        expected_value=observation_time,
    )


def _closure_readiness_alignment_check(
    runtime_status: Mapping[str, Any],
) -> dict[str, object]:
    current = _number(runtime_status.get("current_sim_time"))
    closure_time = _path_number(
        runtime_status,
        "runtime_closure_readiness_v1.current_sim_time",
    )
    if current is None or closure_time is None:
        return _check(
            "closure_readiness_time",
            "Runtime closure readiness time",
            "WAIT",
            ("closure readiness time is not available yet",),
            ("current_sim_time", "runtime_closure_readiness_v1.current_sim_time"),
            observed_value=closure_time,
            expected_value=current,
        )
    status = "PASS" if _same_time(current, closure_time) else "FAIL"
    issues = () if status == "PASS" else ("closure readiness time differs from runtime current_sim_time",)
    return _check(
        "closure_readiness_time",
        "Runtime closure readiness time",
        status,
        issues,
        ("current_sim_time", "runtime_closure_readiness_v1.current_sim_time"),
        observed_value=closure_time,
        expected_value=current,
    )


def _check(
    check_id: str,
    label: str,
    status: str,
    issues: tuple[str, ...],
    required_paths: tuple[str, ...],
    *,
    observed_value: object,
    expected_value: object,
) -> dict[str, object]:
    return {
        "check_id": check_id,
        "label": label,
        "status": status,
        "issues": issues,
        "required_paths": required_paths,
        "observed_value": observed_value,
        "expected_value": expected_value,
    }


def _consistency_status(
    *,
    passed_count: int,
    waiting_count: int,
    failed_count: int,
    check_count: int,
) -> str:
    if failed_count > 0:
        return "INCONSISTENT"
    if passed_count == check_count:
        return "CONSISTENT"
    if waiting_count > 0:
        return "OBSERVING"
    return "UNKNOWN"


def _same_time(left: float, right: float) -> bool:
    return abs(left - right) <= _EPSILON


def _observation_sim_time(runtime_status: Mapping[str, Any]) -> float | None:
    observation = _number(runtime_status.get("runtime_observation_sim_time"))
    if observation is not None:
        return observation
    return _number(runtime_status.get("current_sim_time"))


def _kpi_tail_sim_time(runtime_status: Mapping[str, Any]) -> float | None:
    samples = _path_value(runtime_status, "kpi_time_series_v1.samples")
    if not isinstance(samples, Sequence) or isinstance(samples, (str, bytes)):
        return None
    records = tuple(sample for sample in samples if isinstance(sample, Mapping))
    if not records:
        return None
    return _number(records[-1].get("sim_time"))


def _path_number(
    data: Mapping[str, Any],
    *paths: str,
) -> float | None:
    for path in paths:
        value = _number(_path_value(data, path))
        if value is not None:
            return value
    return None


def _path_value(data: Mapping[str, Any], path: str) -> object:
    current: object = data
    for part in path.split("."):
        if not isinstance(current, Mapping):
            return None
        current = current.get(part)
    return current


def _integer(value: object) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    return None


def _number(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None
