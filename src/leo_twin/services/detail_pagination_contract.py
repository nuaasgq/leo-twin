"""Large detail pagination contract v2 for runtime observation surfaces."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from leo_twin.services.lod_snapshot_policy import lod_snapshot_policy_v2_to_dict
from leo_twin.services.scale_policy_v2 import scale_policy_v2_to_dict


LARGE_DETAIL_PAGINATION_CONTRACT_V2_ID = (
    "leo_twin.large_detail_pagination_contract.v2"
)
DETAIL_ENDPOINT_MAX_LIMIT = 5_000


def large_detail_pagination_contract_v2_to_dict(
    *,
    satellite_count: int,
    user_count: int,
    compute_node_count: int,
    route_count_estimate: int = 0,
    service_count_estimate: int = 0,
    scale_policy: Mapping[str, Any] | None = None,
    lod_snapshot_policy: Mapping[str, Any] | None = None,
) -> dict[str, object]:
    """Return backend-owned cursor/detail contract for large collections."""

    _require_positive_int(satellite_count, "satellite_count")
    _require_non_negative_int(user_count, "user_count")
    _require_positive_int(compute_node_count, "compute_node_count")
    _require_non_negative_int(route_count_estimate, "route_count_estimate")
    _require_non_negative_int(service_count_estimate, "service_count_estimate")
    resolved_scale_policy = (
        dict(scale_policy)
        if scale_policy is not None
        else scale_policy_v2_to_dict(
            satellite_count=satellite_count,
            user_count=user_count,
        )
    )
    resolved_lod_policy = (
        dict(lod_snapshot_policy)
        if lod_snapshot_policy is not None
        else lod_snapshot_policy_v2_to_dict(
            satellite_count=satellite_count,
            user_count=user_count,
            scale_policy=resolved_scale_policy,
        )
    )
    windows = _detail_windows_by_collection(resolved_lod_policy)
    collections = (
        _collection_contract(
            windows,
            collection="ground_users",
            kind="users",
            label_zh="用户节点状态明细",
            endpoint="/runtime/details/users",
            summary_type="RuntimeUserRequestSummaryV1",
            item_type="RuntimeUserRequestItemV1",
            stable_key="user_id",
            sort_policy="stable entity id ascending",
            count_field="user_count",
            estimated_total_count=user_count,
            default_limit=100,
        ),
        _collection_contract(
            windows,
            collection="satellites",
            kind="satellites",
            label_zh="卫星资源消耗明细",
            endpoint="/runtime/details/satellites",
            summary_type="RuntimeSatelliteServiceSummaryV1",
            item_type="RuntimeSatelliteServiceItemV1",
            stable_key="satellite_id",
            sort_policy="stable satellite id ascending",
            count_field="satellite_count",
            estimated_total_count=satellite_count,
            default_limit=120,
        ),
        _collection_contract(
            windows,
            collection="node_pressure",
            window_collection="satellites",
            kind="node_pressure",
            label_zh="Node network pressure detail",
            endpoint="/runtime/details/node-pressure",
            summary_type="RuntimeNodeNetworkPressureDetailPageV1",
            item_type="RuntimeNodeNetworkPressureDetailItemV1",
            stable_key="entity_id",
            sort_policy="all users first, then satellites; each group sorted by stable id",
            count_field="node_count",
            estimated_total_count=user_count + satellite_count,
            default_limit=120,
            query_parameters=("cursor", "limit", "query", "entity_type"),
        ),
        _collection_contract(
            windows,
            collection="routes",
            kind="routes",
            label_zh="路由与瓶颈明细",
            endpoint="/runtime/details/routes",
            summary_type="RuntimeRouteExplanationSummaryV1",
            item_type="RuntimeRouteExplanationItemV1",
            stable_key="route_id",
            sort_policy="unavailable, pressure, user id, route id",
            count_field="route_count",
            estimated_total_count=route_count_estimate,
            default_limit=100,
        ),
        _collection_contract(
            windows,
            collection="services",
            kind="services",
            label_zh="业务服务生命周期明细",
            endpoint="/runtime/details/services",
            summary_type="RuntimeServiceDetailPageV1",
            item_type="RuntimeServiceDetailItemV1",
            stable_key="task_id",
            sort_policy="latest service sample first, task id",
            count_field="service_count",
            estimated_total_count=service_count_estimate,
            default_limit=100,
        ),
        _collection_contract(
            windows,
            collection="service_traces",
            window_collection="services",
            kind="service_traces",
            label_zh="通信-计算服务 trace",
            endpoint="/runtime/details/service-traces",
            summary_type="RuntimeServiceLifecycleTraceV2",
            item_type="RuntimeServiceLifecycleTraceItemV2",
            stable_key="trace_id",
            sort_policy="latest service sample first, task id",
            count_field="service_count",
            estimated_total_count=service_count_estimate,
            default_limit=100,
            query_parameters=(
                "cursor",
                "limit",
                "query",
                "terminal_state",
                "compute_node_id",
                "stage_kind",
                "terminal_reason",
            ),
        ),
        _collection_contract(
            windows,
            collection="compute_nodes",
            kind="compute_nodes",
            label_zh="算力节点资源明细",
            endpoint="/runtime/details/compute-nodes",
            summary_type="RuntimeComputeNodeDetailPageV1",
            item_type="RuntimeComputeNodeDetailItemV1",
            stable_key="node_id",
            sort_policy="stable compute node id ascending",
            count_field="compute_node_count",
            estimated_total_count=compute_node_count,
            default_limit=100,
        ),
    )
    return {
        "version": "v2",
        "contract_id": LARGE_DETAIL_PAGINATION_CONTRACT_V2_ID,
        "source_policy_ids": {
            "scale_policy": resolved_scale_policy["policy_id"],
            "lod_snapshot_policy": resolved_lod_policy["policy_id"],
        },
        "active_profile_id": resolved_scale_policy["active_profile_id"],
        "active_scale_band": resolved_scale_policy["active_scale_band"],
        "cursor_model": {
            "cursor_type": "zero_based_offset",
            "limit_type": "positive_int",
            "next_cursor_policy": "min(total_count, cursor + returned_item_count)",
            "has_more_policy": "next_cursor < total_count",
            "max_limit": DETAIL_ENDPOINT_MAX_LIMIT,
        },
        "collections": collections,
        "combined_node_endpoint": {
            "kind": "nodes",
            "endpoint": "/runtime/details/nodes",
            "summary_type": "RuntimeNodeDetailPageV1",
            "composition": ("ground_users", "satellites"),
            "purpose": "combined user and satellite node detail cards",
            "stable_ordering": "all users first, then satellites; each group sorted by stable id",
        },
        "frontend_policy": {
            "rendering": "use backend cursor windows; do not render unbounded rows",
            "hidden_rows": resolved_lod_policy["hidden_detail_policy"],
            "raw_counts": "display total counts from summary count fields",
            "local_inference": "frontend may format rows but must not invent pagination semantics",
        },
        "determinism": {
            "ordering": "backend-owned stable ordering per collection",
            "cursor_replay": "same snapshot, cursor, and limit return identical rows",
            "mutation_policy": "read-only observation endpoints",
        },
        "event_kernel_policy": "NO_EVENT_KERNEL_BEHAVIOR_CHANGE",
    }


def _collection_contract(
    windows: Mapping[str, Mapping[str, object]],
    *,
    collection: str,
    window_collection: str | None = None,
    kind: str,
    label_zh: str,
    endpoint: str,
    summary_type: str,
    item_type: str,
    stable_key: str,
    sort_policy: str,
    count_field: str,
    estimated_total_count: int,
    default_limit: int,
    query_parameters: tuple[str, ...] = ("cursor", "limit"),
) -> dict[str, object]:
    window = windows[window_collection or collection]
    recommended_limit = int(window["max_rows"])
    cursor_required_for_hidden_rows = bool(window["cursor_required_for_hidden_rows"])
    hidden_count_estimate = max(0, estimated_total_count - recommended_limit)
    return {
        "collection": collection,
        "kind": kind,
        "label_zh": label_zh,
        "endpoint": endpoint,
        "http_method": "GET",
        "query_parameters": query_parameters,
        "response_envelope_type": "RUNTIME_DETAIL_PAGE",
        "summary_type": summary_type,
        "item_type": item_type,
        "stable_key": stable_key,
        "sort_policy": sort_policy,
        "count_field": count_field,
        "estimated_total_count": estimated_total_count,
        "default_limit": min(default_limit, DETAIL_ENDPOINT_MAX_LIMIT),
        "recommended_limit": recommended_limit,
        "max_limit": DETAIL_ENDPOINT_MAX_LIMIT,
        "cursor_required": cursor_required_for_hidden_rows or hidden_count_estimate > 0,
        "cursor_required_for_hidden_rows": cursor_required_for_hidden_rows,
        "hidden_count_estimate": hidden_count_estimate,
        "window_source": "lod_snapshot_policy_v2.detail_windows",
        "availability": "HTTP_CURSOR_ENDPOINT_AVAILABLE",
    }


def _detail_windows_by_collection(
    lod_snapshot_policy: Mapping[str, Any],
) -> dict[str, Mapping[str, object]]:
    windows = lod_snapshot_policy.get("detail_windows")
    if not isinstance(windows, tuple):
        raise TypeError("lod_snapshot_policy.detail_windows must be a tuple")
    result: dict[str, Mapping[str, object]] = {}
    for window in windows:
        if not isinstance(window, Mapping):
            raise TypeError("detail window must be a mapping")
        collection = str(window.get("collection", ""))
        if collection:
            result[collection] = window
    required = {"ground_users", "satellites", "routes", "services", "compute_nodes"}
    missing = required - set(result)
    if missing:
        raise ValueError(f"missing detail windows: {', '.join(sorted(missing))}")
    return result


def _require_positive_int(value: object, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field_name} must be an int")
    if value <= 0:
        raise ValueError(f"{field_name} must be positive")


def _require_non_negative_int(value: object, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field_name} must be an int")
    if value < 0:
        raise ValueError(f"{field_name} must be non-negative")
