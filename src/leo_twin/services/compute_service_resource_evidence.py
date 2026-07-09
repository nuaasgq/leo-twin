"""Backend-owned compute service queue and resource evidence v1."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any

from leo_twin.services.runtime_reproducibility import stable_hash_payload


COMPUTE_SERVICE_RESOURCE_EVIDENCE_V1_ID = (
    "leo_twin.compute_service_resource_evidence.v1"
)

ComputeServiceResourceEvidenceV1 = dict[str, object]


def build_compute_service_resource_evidence_v1(
    service_latency_history: Mapping[str, Any],
    compute_resource_pool_summary: Mapping[str, Any],
    *,
    cursor: int = 0,
    limit: int = 128,
    query: str = "",
) -> ComputeServiceResourceEvidenceV1:
    """Build compute-service queue/resource evidence from runtime summaries."""

    if not isinstance(service_latency_history, Mapping):
        raise TypeError("service_latency_history must be a mapping")
    if not isinstance(compute_resource_pool_summary, Mapping):
        raise TypeError("compute_resource_pool_summary must be a mapping")

    all_items = tuple(
        _service_row(item)
        for item in sorted(
            _records(service_latency_history.get("items")),
            key=_service_sort_key,
        )
    )
    filtered_items = tuple(item for item in all_items if _matches_query(item, query))
    normalized_cursor = _page_cursor(cursor)
    normalized_limit = _page_limit(limit)
    page_items = filtered_items[
        normalized_cursor : normalized_cursor + normalized_limit
    ]
    next_cursor = min(len(filtered_items), normalized_cursor + len(page_items))
    node_rows = _node_rows(filtered_items)
    bottleneck_counts = _value_counts(
        filtered_items,
        "placement_bottleneck_resource",
        "bottleneck_resource",
    )
    resource_dimensions = tuple(
        _resource_dimension_row(item)
        for item in _records(compute_resource_pool_summary.get("dimensions"))
    )
    saturated_dimensions = tuple(
        row for row in resource_dimensions if row["resource_status"] == "SATURATED"
    )
    queued_services = tuple(
        item for item in filtered_items if item["compute_queue_delay_s"] > 0.0
    )
    executing_services = tuple(
        item for item in filtered_items if item["compute_execution_delay_s"] > 0.0
    )
    payload: dict[str, object] = {
        "version": "v1",
        "summary_id": COMPUTE_SERVICE_RESOURCE_EVIDENCE_V1_ID,
        "source": "service_latency_history_v1 + compute_resource_pool_summary_v1",
        "service_trace_source": "service_latency_history_v1",
        "resource_pool_source": "compute_resource_pool_summary_v1",
        "metric_model": "FLOW_LEVEL_COMPUTE_SERVICE_RESOURCE_EVIDENCE",
        "packet_level_simulation": False,
        "frontend_inference_required": False,
        "cursor": normalized_cursor,
        "limit": normalized_limit,
        "next_cursor": next_cursor,
        "has_more": next_cursor < len(filtered_items),
        "service_count": len(filtered_items),
        "item_count": len(page_items),
        "hidden_service_count": max(0, len(filtered_items) - len(page_items)),
        "complete_service_count": sum(
            1 for item in filtered_items if item["complete"] is True
        ),
        "running_service_count": sum(
            1 for item in filtered_items if item["complete"] is not True
        ),
        "queued_service_count": len(queued_services),
        "executing_service_count": len(executing_services),
        "placed_service_count": sum(
            1 for item in filtered_items if item["placement_status"]
        ),
        "queue_pressure_status": _queue_pressure_status(
            service_count=len(filtered_items),
            queued_count=len(queued_services),
            executing_count=len(executing_services),
            saturated_dimension_count=len(saturated_dimensions),
        ),
        "resource_pressure_status": _resource_pressure_status(
            compute_resource_pool_summary,
            saturated_dimension_count=len(saturated_dimensions),
        ),
        "avg_compute_queue_delay_s": _average(
            item["compute_queue_delay_s"] for item in filtered_items
        ),
        "max_compute_queue_delay_s": max(
            (item["compute_queue_delay_s"] for item in filtered_items),
            default=0.0,
        ),
        "avg_compute_execution_delay_s": _average(
            item["compute_execution_delay_s"] for item in filtered_items
        ),
        "max_compute_execution_delay_s": max(
            (item["compute_execution_delay_s"] for item in filtered_items),
            default=0.0,
        ),
        "avg_total_latency_s": _average(
            item["total_latency_s"] for item in filtered_items
        ),
        "max_total_latency_s": max(
            (item["total_latency_s"] for item in filtered_items),
            default=0.0,
        ),
        "queue_to_execution_ratio": _queue_to_execution_ratio(filtered_items),
        "bottleneck_resource_counts": bottleneck_counts,
        "compute_node_count": len(node_rows),
        "busy_compute_node_count": sum(1 for row in node_rows if row["service_count"] > 0),
        "node_rows": node_rows,
        "resource_dimension_count": len(resource_dimensions),
        "saturated_resource_dimension_count": len(saturated_dimensions),
        "resource_dimensions": resource_dimensions,
        "items": page_items,
        "field_sources": {
            "queue_delay": "service_latency_history_v1.items[].compute_queue_delay_s",
            "execution_delay": "service_latency_history_v1.items[].compute_execution_delay_s",
            "placement": "service_latency_history_v1 service_placement_* fields",
            "resource_pool": "compute_resource_pool_summary_v1.dimensions",
        },
        "model_assumptions": (
            "One service row is derived from one compute-service lifecycle trace.",
            "Queue and execution delays are deterministic flow-level service evidence.",
            "Resource pool values are estimates from ComputeNodeState metrics, not hardware telemetry.",
            "Packet-level networking and external simulators are not used.",
        ),
    }
    filter_query = _normalized_query(query)
    if filter_query:
        payload.update(
            {
                "filter_query": filter_query,
                "filter_applied": True,
                "unfiltered_service_count": len(all_items),
            }
        )
    payload["summary_hash"] = stable_hash_payload(payload)
    return payload


def _service_row(item: Mapping[str, Any]) -> dict[str, object]:
    row: dict[str, object] = {
        "service_id": _service_id(item),
        "task_id": _str(item.get("task_id")),
        "input_flow_id": _str(item.get("input_flow_id")),
        "output_flow_id": _str(item.get("output_flow_id")),
        "compute_node_id": _str(item.get("compute_node_id")),
        "complete": item.get("complete") is True,
        "service_state": "COMPLETED" if item.get("complete") is True else "RUNNING",
        "placement_status": _str(item.get("service_placement_status")),
        "placement_policy": _str(item.get("service_placement_policy")),
        "placement_bottleneck_resource": _str(
            item.get("service_placement_bottleneck_resource")
        ),
        "placement_candidate_count": _int(
            item.get("service_placement_candidate_count")
        ),
        "placement_capable_candidate_count": _int(
            item.get("service_placement_capable_candidate_count")
        ),
        "placement_candidate_queue_label": _str(
            item.get("service_placement_candidate_queue_label")
        ),
        "compute_queue_delay_s": _float(item.get("compute_queue_delay_s")),
        "compute_execution_delay_s": _float(item.get("compute_execution_delay_s")),
        "input_network_latency_s": _float(item.get("input_network_latency_s")),
        "output_network_latency_s": _float(item.get("output_network_latency_s")),
        "total_latency_s": _float(item.get("total_latency_s")),
        "first_sample_sim_time": _optional_float(item.get("first_sample_sim_time")),
        "last_sample_sim_time": _optional_float(item.get("last_sample_sim_time")),
        "queue_state": (
            "QUEUED" if _float(item.get("compute_queue_delay_s")) > 0.0 else "NO_QUEUE"
        ),
        "execution_state": (
            "EXECUTED"
            if _float(item.get("compute_execution_delay_s")) > 0.0
            else "NO_EXECUTION_SAMPLE"
        ),
        "resource_evidence_state": _service_resource_evidence_state(item),
    }
    row["detail_hash"] = stable_hash_payload(row)
    return row


def _resource_dimension_row(item: Mapping[str, Any]) -> dict[str, object]:
    row = {
        "resource": _str(item.get("resource")),
        "label": _str(item.get("label")),
        "unit": _str(item.get("unit")),
        "total": _float(item.get("total")),
        "available": _float(item.get("available")),
        "used": _float(item.get("used")),
        "utilization": _float(item.get("utilization")),
        "resource_status": _str(item.get("resource_status")) or "UNKNOWN",
    }
    return row


def _node_rows(items: Sequence[Mapping[str, object]]) -> tuple[dict[str, object], ...]:
    by_node: dict[str, list[Mapping[str, object]]] = {}
    for item in items:
        node_id = _str(item.get("compute_node_id")) or "UNKNOWN_NODE"
        by_node.setdefault(node_id, []).append(item)
    rows: list[dict[str, object]] = []
    for node_id in sorted(by_node):
        node_items = tuple(by_node[node_id])
        bottlenecks = Counter(
            _str(item.get("placement_bottleneck_resource")) or "UNKNOWN"
            for item in node_items
        )
        dominant_bottleneck = sorted(
            bottlenecks.items(),
            key=lambda entry: (-entry[1], entry[0]),
        )[0][0]
        row: dict[str, object] = {
            "compute_node_id": node_id,
            "service_count": len(node_items),
            "complete_service_count": sum(
                1 for item in node_items if item.get("complete") is True
            ),
            "queued_service_count": sum(
                1 for item in node_items if _float(item.get("compute_queue_delay_s")) > 0.0
            ),
            "avg_compute_queue_delay_s": _average(
                _float(item.get("compute_queue_delay_s")) for item in node_items
            ),
            "avg_compute_execution_delay_s": _average(
                _float(item.get("compute_execution_delay_s")) for item in node_items
            ),
            "dominant_bottleneck_resource": dominant_bottleneck,
        }
        row["node_hash"] = stable_hash_payload(row)
        rows.append(row)
    return tuple(rows)


def _value_counts(
    items: Sequence[Mapping[str, object]],
    source_key: str,
    output_key: str,
) -> tuple[dict[str, object], ...]:
    counts: Counter[str] = Counter(
        _str(item.get(source_key)) or "UNKNOWN" for item in items
    )
    return tuple(
        {output_key: key, "service_count": counts[key]}
        for key in sorted(counts)
    )


def _queue_pressure_status(
    *,
    service_count: int,
    queued_count: int,
    executing_count: int,
    saturated_dimension_count: int,
) -> str:
    if service_count == 0:
        return "NO_SERVICE_EVIDENCE"
    if queued_count > 0 and saturated_dimension_count > 0:
        return "QUEUE_PRESSURE_WITH_RESOURCE_SATURATION"
    if queued_count > 0:
        return "QUEUE_PRESSURE_OBSERVED"
    if executing_count > 0:
        return "EXECUTION_ONLY_OBSERVED"
    return "NO_COMPUTE_STAGE_EVIDENCE"


def _resource_pressure_status(
    compute_resource_pool_summary: Mapping[str, Any],
    *,
    saturated_dimension_count: int,
) -> str:
    bottleneck = _mapping(compute_resource_pool_summary.get("bottleneck"))
    bottleneck_status = _str(bottleneck.get("status"))
    utilization = _float(bottleneck.get("utilization"))
    if saturated_dimension_count > 0 or bottleneck_status == "SATURATED":
        return "RESOURCE_SATURATED"
    if bottleneck_status == "BUSY" or utilization >= 0.7:
        return "RESOURCE_BUSY"
    if _int(compute_resource_pool_summary.get("consumed_dimension_count")) > 0:
        return "RESOURCE_ACTIVE"
    if _int(compute_resource_pool_summary.get("active_dimension_count")) == 0:
        return "RESOURCE_NOT_CONFIGURED"
    return "RESOURCE_IDLE"


def _service_resource_evidence_state(item: Mapping[str, Any]) -> str:
    if _str(item.get("service_placement_status")):
        return "PLACEMENT_OBSERVED"
    if _float(item.get("compute_execution_delay_s")) > 0.0:
        return "EXECUTION_OBSERVED_WITHOUT_PLACEMENT_METADATA"
    if _float(item.get("compute_queue_delay_s")) > 0.0:
        return "QUEUE_OBSERVED_WITHOUT_PLACEMENT_METADATA"
    return "NO_COMPUTE_RESOURCE_METADATA"


def _queue_to_execution_ratio(items: Sequence[Mapping[str, object]]) -> float:
    queue = sum(_float(item.get("compute_queue_delay_s")) for item in items)
    execution = sum(_float(item.get("compute_execution_delay_s")) for item in items)
    return 0.0 if execution <= 0.0 else queue / execution


def _service_sort_key(item: Mapping[str, Any]) -> tuple[float, float, str]:
    return (
        -_float(item.get("compute_queue_delay_s")),
        -_float(item.get("last_sample_sim_time")),
        _str(item.get("task_id")),
    )


def _service_id(item: Mapping[str, Any]) -> str:
    task_id = _str(item.get("task_id"))
    if task_id.endswith("-task"):
        return task_id[: -len("-task")]
    return task_id or _str(item.get("input_flow_id")) or "unknown-service"


def _matches_query(item: Mapping[str, object], query: str) -> bool:
    needle = _normalized_query(query)
    if not needle:
        return True
    haystack = " ".join(
        _str(item.get(key)).lower()
        for key in (
            "service_id",
            "task_id",
            "compute_node_id",
            "placement_status",
            "placement_bottleneck_resource",
            "resource_evidence_state",
        )
    )
    return needle in haystack


def _records(value: object) -> tuple[Mapping[str, Any], ...]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return ()
    return tuple(item for item in value if isinstance(item, Mapping))


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _page_cursor(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return 0
    return max(0, int(value))


def _page_limit(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return 128
    return min(500, max(1, int(value)))


def _average(values: Sequence[float] | Any) -> float:
    numbers = tuple(_float(value) for value in values)
    return 0.0 if not numbers else sum(numbers) / len(numbers)


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
    "COMPUTE_SERVICE_RESOURCE_EVIDENCE_V1_ID",
    "ComputeServiceResourceEvidenceV1",
    "build_compute_service_resource_evidence_v1",
]
