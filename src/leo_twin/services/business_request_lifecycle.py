"""Backend-owned business request lifecycle evidence v2."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from leo_twin.services.runtime_reproducibility import stable_hash_payload


BUSINESS_REQUEST_LIFECYCLE_V2_ID = "leo_twin.business_request_lifecycle.v2"

BusinessRequestLifecycleV2 = dict[str, object]

_LIFECYCLE_COMPONENTS = (
    "input_network",
    "compute_queue",
    "compute_execution",
    "output_network",
)

_COMPONENT_DURATION_FIELDS = {
    "input_network": "input_network_latency_s",
    "compute_queue": "compute_queue_delay_s",
    "compute_execution": "compute_execution_delay_s",
    "output_network": "output_network_latency_s",
}


def build_business_request_lifecycle_v2(
    traffic_request_timeline: Mapping[str, Any] | None,
    service_latency_history: Mapping[str, Any] | None,
    *,
    current_sim_time: float | None = None,
    cursor: int = 0,
    limit: int = 128,
    query: str = "",
) -> BusinessRequestLifecycleV2:
    """Build deterministic per-business-request lifecycle evidence.

    The summary joins the configured request timeline with runtime service
    latency observations. It is intentionally flow-level: no packet queues or
    packet traces are inferred.
    """

    timeline = traffic_request_timeline if isinstance(traffic_request_timeline, Mapping) else {}
    services = (
        service_latency_history if isinstance(service_latency_history, Mapping) else {}
    )
    service_index = _service_observation_index(services)
    all_rows = tuple(
        _lifecycle_row(item, service_index)
        for item in _records(timeline.get("items"))
    )
    filtered_rows = tuple(
        row for row in all_rows if _matches_query(row, query)
    )
    normalized_cursor = _page_cursor(cursor)
    normalized_limit = _page_limit(limit)
    rows = filtered_rows[normalized_cursor : normalized_cursor + normalized_limit]
    next_cursor = min(len(filtered_rows), normalized_cursor + len(rows))
    request_count = _int(timeline.get("request_count"))
    current = (
        _float(current_sim_time)
        if current_sim_time is not None
        else _float(timeline.get("current_sim_time"))
    )
    payload: dict[str, object] = {
        "version": "v2",
        "summary_id": BUSINESS_REQUEST_LIFECYCLE_V2_ID,
        "source": "traffic_request_timeline_v1 + service_latency_history_v1",
        "timeline_source": "traffic_request_timeline_v1",
        "service_trace_source": "service_latency_history_v1",
        "lifecycle_model": "PLANNED_REQUEST_WITH_RUNTIME_SERVICE_TRACE_JOIN",
        "packet_level_simulation": False,
        "frontend_inference_required": False,
        "current_sim_time": current,
        "cursor": normalized_cursor,
        "limit": normalized_limit,
        "next_cursor": next_cursor,
        "has_more": next_cursor < len(filtered_rows),
        "request_count": request_count,
        "timeline_window_request_count": len(all_rows),
        "observed_request_count": sum(
            1 for row in filtered_rows if row["observed_execution_state"] != "NOT_OBSERVED"
        ),
        "completed_request_count": sum(
            1 for row in filtered_rows if row["lifecycle_state"] == "COMPLETED"
        ),
        "active_request_count": sum(
            1 for row in filtered_rows if row["lifecycle_state"] in _active_states()
        ),
        "pending_request_count": sum(
            1 for row in filtered_rows if row["lifecycle_state"] == "PENDING"
        ),
        "not_observed_request_count": sum(
            1 for row in filtered_rows if row["lifecycle_state"] == "NOT_OBSERVED"
        ),
        "item_count": len(rows),
        "window_item_count": len(rows),
        "hidden_request_count": max(0, len(filtered_rows) - len(rows)),
        "state_counts": _value_counts(filtered_rows, "lifecycle_state", "lifecycle_state"),
        "traffic_class_counts": _value_counts(filtered_rows, "traffic_class", "traffic_class"),
        "observed_stage_counts": _stage_counts(filtered_rows),
        "items": rows,
        "field_sources": {
            "planned_request": "traffic_request_timeline_v1.items",
            "runtime_stage_observation": "service_latency_history_v1.items",
            "latency_components": "service_latency_history_v1 component latency fields",
            "lifecycle_state": "backend deterministic stage classifier",
        },
        "model_assumptions": (
            "One row represents one configured flow-level business request in the current timeline window.",
            "Compute-service stages are joined by request id, task id, input flow id, or output flow id.",
            "Communication-only requests may be present in the timeline without compute service traces.",
            "Packet-level behavior, retransmissions, and stochastic transport effects are not simulated.",
        ),
    }
    filter_query = _normalized_query(query)
    if filter_query:
        payload.update(
            {
                "filter_query": filter_query,
                "filter_applied": True,
                "unfiltered_window_request_count": len(all_rows),
            }
        )
    payload["summary_hash"] = stable_hash_payload(payload)
    return payload


def _lifecycle_row(
    timeline_item: Mapping[str, Any],
    service_index: Mapping[str, Mapping[str, Any]],
) -> dict[str, object]:
    service = _matched_service(timeline_item, service_index)
    stages = _stage_rows(service)
    observed_state = _observed_execution_state(service)
    lifecycle_state = _lifecycle_state(timeline_item, service, stages)
    row: dict[str, object] = {
        "request_id": _str(timeline_item.get("request_id")),
        "source_id": _str(timeline_item.get("source_id")),
        "target_id": _str(timeline_item.get("target_id")),
        "traffic_class": _str(timeline_item.get("traffic_class")) or "UNKNOWN",
        "destination_type": _str(timeline_item.get("destination_type")),
        "priority": _int(timeline_item.get("priority")),
        "planned_arrival_time": _float(timeline_item.get("arrival_time")),
        "time_offset_s": _float(timeline_item.get("time_offset_s")),
        "timeline_request_state": _str(timeline_item.get("request_state")) or "UNKNOWN",
        "timeline_service_state": _str(timeline_item.get("service_state")),
        "input_flow_id": _str(timeline_item.get("input_flow_id")),
        "task_id": _str(timeline_item.get("task_id")),
        "output_flow_id": _str(timeline_item.get("output_flow_id")),
        "has_compute_task": bool(timeline_item.get("has_compute_task")),
        "has_output_flow": bool(timeline_item.get("has_output_flow")),
        "input_data_mb": _float(timeline_item.get("input_data_mb")),
        "output_data_mb": _float(timeline_item.get("output_data_mb")),
        "observed_execution_state": observed_state,
        "observed_complete": bool(service.get("complete")) if service is not None else False,
        "observed_stage_count": sum(
            1 for stage in stages if stage["stage_status"] == "OBSERVED"
        ),
        "pending_stage_count": sum(
            1 for stage in stages if stage["stage_status"] == "PENDING"
        ),
        "lifecycle_state": lifecycle_state,
        "lifecycle_state_label": _lifecycle_state_label(lifecycle_state),
        "current_stage": _current_stage(lifecycle_state),
        "service_task_id": _str(service.get("task_id")) if service is not None else "",
        "service_input_flow_id": (
            _str(service.get("input_flow_id")) if service is not None else ""
        ),
        "service_output_flow_id": (
            _str(service.get("output_flow_id")) if service is not None else ""
        ),
        "compute_node_id": _str(service.get("compute_node_id")) if service is not None else "",
        "input_route_id": _str(service.get("input_route_id")) if service is not None else "",
        "output_route_id": _str(service.get("output_route_id")) if service is not None else "",
        "first_sample_sim_time": (
            _optional_float(service.get("first_sample_sim_time"))
            if service is not None
            else None
        ),
        "last_sample_sim_time": (
            _optional_float(service.get("last_sample_sim_time"))
            if service is not None
            else None
        ),
        "input_network_latency_s": _service_component_duration(service, "input_network"),
        "compute_queue_delay_s": _service_component_duration(service, "compute_queue"),
        "compute_execution_delay_s": _service_component_duration(service, "compute_execution"),
        "output_network_latency_s": _service_component_duration(service, "output_network"),
        "observed_total_latency_s": (
            _optional_float(service.get("total_latency_s"))
            if service is not None
            else None
        ),
        "stages": stages,
        "service_trace_join_keys": _join_keys(timeline_item),
        "packet_level_simulation": False,
        "frontend_inference_required": False,
    }
    row["detail_hash"] = stable_hash_payload(row)
    return row


def _service_observation_index(
    service_latency_history: Mapping[str, Any],
) -> dict[str, Mapping[str, Any]]:
    index: dict[str, Mapping[str, Any]] = {}
    services = tuple(
        sorted(
            _records(service_latency_history.get("items")),
            key=_service_sort_key,
        )
    )
    for item in services:
        for key in _service_keys(item):
            index.setdefault(key, item)
    return index


def _matched_service(
    timeline_item: Mapping[str, Any],
    service_index: Mapping[str, Mapping[str, Any]],
) -> Mapping[str, Any] | None:
    for key in _join_keys(timeline_item):
        service = service_index.get(key)
        if service is not None:
            return service
    return None


def _join_keys(item: Mapping[str, Any]) -> tuple[str, ...]:
    values = (
        _str(item.get("request_id")),
        _str(item.get("task_id")),
        _str(item.get("input_flow_id")),
        _str(item.get("output_flow_id")),
        _without_suffix(_str(item.get("task_id")), "-task"),
        _without_suffix(_str(item.get("input_flow_id")), "-input"),
        _without_suffix(_str(item.get("output_flow_id")), "-output"),
    )
    return _unique_non_empty(values)


def _service_keys(item: Mapping[str, Any]) -> tuple[str, ...]:
    values = (
        _str(item.get("task_id")),
        _str(item.get("input_flow_id")),
        _str(item.get("output_flow_id")),
        _without_suffix(_str(item.get("task_id")), "-task"),
        _without_suffix(_str(item.get("input_flow_id")), "-input"),
        _without_suffix(_str(item.get("output_flow_id")), "-output"),
    )
    return _unique_non_empty(values)


def _stage_rows(service: Mapping[str, Any] | None) -> tuple[dict[str, object], ...]:
    return tuple(
        _stage_row(service, component, index)
        for index, component in enumerate(_LIFECYCLE_COMPONENTS)
    )


def _stage_row(
    service: Mapping[str, Any] | None,
    component: str,
    index: int,
) -> dict[str, object]:
    stage = _component_timeline_stage(service, component)
    duration = _service_component_duration(service, component)
    observed = service is not None and (stage is not None or duration is not None)
    status = "OBSERVED" if observed else "PENDING" if service is not None else "NOT_OBSERVED"
    return {
        "stage_index": index,
        "component": component,
        "stage_kind": component.upper(),
        "stage_status": status,
        "sample_sim_time": (
            _optional_float(stage.get("sample_sim_time"))
            if stage is not None
            else (
                _optional_float(service.get("last_sample_sim_time"))
                if service is not None and observed
                else None
            )
        ),
        "duration_s": 0.0 if duration is None else duration,
        "flow_id": _stage_flow_id(service, stage, component),
        "route_id": _str(stage.get("route_id")) if stage is not None else _stage_route_id(service, component),
    }


def _component_timeline_stage(
    service: Mapping[str, Any] | None,
    component: str,
) -> Mapping[str, Any] | None:
    if service is None:
        return None
    for item in _records(service.get("component_timeline")):
        if _str(item.get("component")) == component:
            return item
    return None


def _stage_flow_id(
    service: Mapping[str, Any] | None,
    stage: Mapping[str, Any] | None,
    component: str,
) -> str:
    if stage is not None:
        flow_id = _str(stage.get("input_flow_id")) or _str(stage.get("output_flow_id"))
        if flow_id:
            return flow_id
    if service is None:
        return ""
    if component == "output_network":
        return _str(service.get("output_flow_id"))
    if component == "input_network":
        return _str(service.get("input_flow_id"))
    return _str(service.get("task_id"))


def _stage_route_id(service: Mapping[str, Any] | None, component: str) -> str:
    if service is None:
        return ""
    if component == "output_network":
        return _str(service.get("output_route_id"))
    if component == "input_network":
        return _str(service.get("input_route_id"))
    return ""


def _service_component_duration(
    service: Mapping[str, Any] | None,
    component: str,
) -> float | None:
    if service is None:
        return None
    stage = _component_timeline_stage(service, component)
    if stage is not None:
        duration = _optional_float(stage.get("duration_s"))
        if duration is not None:
            return duration
    return _optional_float(service.get(_COMPONENT_DURATION_FIELDS[component]))


def _observed_execution_state(service: Mapping[str, Any] | None) -> str:
    if service is None:
        return "NOT_OBSERVED"
    if service.get("complete") is True:
        return "COMPLETED"
    return "OBSERVED_IN_PROGRESS"


def _lifecycle_state(
    timeline_item: Mapping[str, Any],
    service: Mapping[str, Any] | None,
    stages: Sequence[Mapping[str, object]],
) -> str:
    if _str(timeline_item.get("request_state")) == "PENDING":
        return "PENDING"
    if service is None:
        if _str(timeline_item.get("traffic_class")) != "COMPUTE_SERVICE":
            return "COMMUNICATION_ONLY_OBSERVED"
        return "NOT_OBSERVED"
    if service.get("complete") is True:
        return "COMPLETED"
    observed_components = {
        _str(stage.get("component"))
        for stage in stages
        if _str(stage.get("stage_status")) == "OBSERVED"
    }
    if "output_network" in observed_components:
        return "NETWORK_OUTPUT"
    if "compute_execution" in observed_components:
        return "COMPUTE_EXECUTION"
    if "compute_queue" in observed_components:
        return "COMPUTE_QUEUE"
    if "input_network" in observed_components:
        return "NETWORK_INPUT"
    return "NOT_OBSERVED"


def _current_stage(lifecycle_state: str) -> str:
    return {
        "PENDING": "scheduled",
        "NETWORK_INPUT": "input_network",
        "COMPUTE_QUEUE": "compute_queue",
        "COMPUTE_EXECUTION": "compute_execution",
        "NETWORK_OUTPUT": "output_network",
        "COMPLETED": "complete",
        "COMMUNICATION_ONLY_OBSERVED": "network_flow",
        "NOT_OBSERVED": "unknown",
    }.get(lifecycle_state, "unknown")


def _lifecycle_state_label(lifecycle_state: str) -> str:
    return {
        "PENDING": "Scheduled",
        "NETWORK_INPUT": "Input network",
        "COMPUTE_QUEUE": "Compute queue",
        "COMPUTE_EXECUTION": "Compute execution",
        "NETWORK_OUTPUT": "Output network",
        "COMPLETED": "Completed",
        "COMMUNICATION_ONLY_OBSERVED": "Communication-only flow",
        "NOT_OBSERVED": "Not observed",
    }.get(lifecycle_state, lifecycle_state)


def _active_states() -> set[str]:
    return {
        "NETWORK_INPUT",
        "COMPUTE_QUEUE",
        "COMPUTE_EXECUTION",
        "NETWORK_OUTPUT",
        "COMMUNICATION_ONLY_OBSERVED",
    }


def _stage_counts(rows: Sequence[Mapping[str, object]]) -> tuple[dict[str, object], ...]:
    result: list[dict[str, object]] = []
    for component in _LIFECYCLE_COMPONENTS:
        stages = tuple(
            stage
            for row in rows
            for stage in _records(row.get("stages"))
            if _str(stage.get("component")) == component
        )
        result.append(
            {
                "component": component,
                "stage_kind": component.upper(),
                "observed_count": sum(
                    1 for stage in stages if _str(stage.get("stage_status")) == "OBSERVED"
                ),
                "pending_count": sum(
                    1 for stage in stages if _str(stage.get("stage_status")) == "PENDING"
                ),
                "not_observed_count": sum(
                    1 for stage in stages if _str(stage.get("stage_status")) == "NOT_OBSERVED"
                ),
            }
        )
    return tuple(result)


def _value_counts(
    rows: Sequence[Mapping[str, object]],
    source_key: str,
    output_key: str,
) -> tuple[dict[str, object], ...]:
    counts: dict[str, int] = {}
    for row in rows:
        key = _str(row.get(source_key)) or "UNKNOWN"
        counts[key] = counts.get(key, 0) + 1
    return tuple(
        {output_key: key, "request_count": counts[key]}
        for key in sorted(counts)
    )


def _matches_query(row: Mapping[str, object], query: str) -> bool:
    needle = _normalized_query(query)
    if not needle:
        return True
    haystack = " ".join(
        _str(row.get(key)).lower()
        for key in (
            "request_id",
            "source_id",
            "target_id",
            "traffic_class",
            "lifecycle_state",
            "input_flow_id",
            "task_id",
            "output_flow_id",
            "compute_node_id",
        )
    )
    return needle in haystack


def _records(value: object) -> tuple[Mapping[str, Any], ...]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return ()
    return tuple(item for item in value if isinstance(item, Mapping))


def _service_sort_key(item: Mapping[str, Any]) -> tuple[str, str, str]:
    return (
        _str(item.get("task_id")),
        _str(item.get("input_flow_id")),
        _str(item.get("output_flow_id")),
    )


def _page_cursor(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return 0
    return max(0, int(value))


def _page_limit(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return 128
    return min(500, max(1, int(value)))


def _unique_non_empty(values: Sequence[str]) -> tuple[str, ...]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        normalized = value.strip()
        if normalized and normalized not in seen:
            seen.add(normalized)
            result.append(normalized)
    return tuple(result)


def _without_suffix(value: str, suffix: str) -> str:
    return value[: -len(suffix)] if value.endswith(suffix) else ""


def _normalized_query(value: object) -> str:
    return str(value or "").strip().lower()


def _str(value: object) -> str:
    if value is None:
        return ""
    return str(value)


def _int(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return 0
    return max(0, int(value))


def _float(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return 0.0
    number = float(value)
    if number != number or number in {float("inf"), float("-inf")}:
        return 0.0
    return number


def _optional_float(value: object) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    if number != number or number in {float("inf"), float("-inf")}:
        return None
    return number


__all__ = [
    "BUSINESS_REQUEST_LIFECYCLE_V2_ID",
    "BusinessRequestLifecycleV2",
    "build_business_request_lifecycle_v2",
]
