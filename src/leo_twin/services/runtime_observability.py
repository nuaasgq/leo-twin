"""Backend-owned runtime observability summaries for dashboard consumers."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


RuntimeObservabilitySummary = dict[str, object]


def build_runtime_lifecycle_summaries(
    snapshot: Mapping[str, Any],
    *,
    service_latency_history: Mapping[str, Any] | None = None,
    satellite_kpi_slices: Mapping[str, Any] | None = None,
    user_cursor: int = 0,
    user_limit: int = 1000,
    satellite_cursor: int = 0,
    satellite_limit: int = 1500,
) -> RuntimeObservabilitySummary:
    """Build deterministic per-user and per-satellite lifecycle summaries."""

    return {
        "user_request_summary_v1": build_runtime_user_request_summary(
            snapshot,
            service_latency_history=service_latency_history,
            cursor=user_cursor,
            limit=user_limit,
        ),
        "satellite_service_summary_v1": build_runtime_satellite_service_summary(
            snapshot,
            service_latency_history=service_latency_history,
            satellite_kpi_slices=satellite_kpi_slices,
            cursor=satellite_cursor,
            limit=satellite_limit,
        ),
    }


def build_runtime_user_request_summary(
    snapshot: Mapping[str, Any],
    *,
    service_latency_history: Mapping[str, Any] | None = None,
    cursor: int = 0,
    limit: int = 1000,
) -> dict[str, object]:
    """Build one deterministic page of per-user request detail rows."""

    if not isinstance(snapshot, Mapping):
        raise TypeError("snapshot must be a mapping")
    service_lookup = _service_lookup(service_latency_history)
    routes = tuple(_records(snapshot.get("routes")))
    users = tuple(_records(snapshot.get("ground_users")))
    return _user_request_summary(
        users,
        routes,
        service_lookup,
        cursor=cursor,
        limit=limit,
    )


def build_runtime_satellite_service_summary(
    snapshot: Mapping[str, Any],
    *,
    service_latency_history: Mapping[str, Any] | None = None,
    satellite_kpi_slices: Mapping[str, Any] | None = None,
    cursor: int = 0,
    limit: int = 1500,
) -> dict[str, object]:
    """Build one deterministic page of per-satellite service detail rows."""

    if not isinstance(snapshot, Mapping):
        raise TypeError("snapshot must be a mapping")
    service_lookup = _service_lookup(service_latency_history)
    routes = tuple(_records(snapshot.get("routes")))
    compute_nodes = tuple(_records(snapshot.get("compute_nodes")))
    satellites = tuple(_records(snapshot.get("satellites")))
    links = tuple(_records(snapshot.get("links")))
    return _satellite_service_summary(
        satellites,
        compute_nodes,
        routes,
        links,
        satellite_kpi_slices,
        service_lookup,
        cursor=cursor,
        limit=limit,
    )


def _user_request_summary(
    users: tuple[Mapping[str, Any], ...],
    routes: tuple[Mapping[str, Any], ...],
    service_lookup: Mapping[str, str],
    *,
    cursor: int,
    limit: int,
) -> dict[str, object]:
    routes_by_user: dict[str, list[Mapping[str, Any]]] = {}
    for route in routes:
        user_id = _route_user_id(route)
        if user_id is None:
            continue
        routes_by_user.setdefault(user_id, []).append(route)
    user_by_id = {_str(user.get("user_id")): user for user in users}
    user_ids = tuple(
        sorted(
            {
                *(user_id for user_id in user_by_id if user_id),
                *(user_id for user_id in routes_by_user if user_id),
            },
            key=_entity_sort_key,
        )
    )
    active_count = 0
    compute_count = 0
    waiting_count = 0
    for user_id in user_ids:
        user_routes = tuple(routes_by_user.get(user_id, ()))
        if user_routes:
            active_count += 1
        if any(_route_is_compute_service(route, service_lookup) for route in user_routes):
            compute_count += 1
        if any(not bool(route.get("available")) for route in user_routes):
            waiting_count += 1
    normalized_cursor = _page_cursor(cursor)
    normalized_limit = _page_limit(limit)
    page_user_ids = user_ids[
        normalized_cursor : normalized_cursor + normalized_limit
    ]
    items = tuple(
        _user_item(user_id, user_by_id.get(user_id), routes_by_user.get(user_id, ()), service_lookup)
        for user_id in page_user_ids
    )
    next_cursor = min(len(user_ids), normalized_cursor + len(items))
    return {
        "version": "v1",
        "source": "BACKEND_RUNTIME_SNAPSHOT",
        "summary_scope": "FULL_USER_SET_WITH_WINDOW_ITEMS",
        "cursor": normalized_cursor,
        "limit": normalized_limit,
        "next_cursor": next_cursor,
        "has_more": next_cursor < len(user_ids),
        "user_count": len(user_ids),
        "item_count": len(items),
        "active_user_count": active_count,
        "compute_service_user_count": compute_count,
        "waiting_user_count": waiting_count,
        "window_user_count": len(items),
        "window_active_user_count": sum(
            1 for item in items if item["communication_route_count"] > 0
        ),
        "window_compute_service_user_count": sum(
            1 for item in items if item["compute_service_count"] > 0
        ),
        "window_waiting_user_count": sum(
            1 for item in items if item["network_queue_count"] > 0
        ),
        "hidden_user_count": max(0, len(user_ids) - len(items)),
        "items": items,
    }


def _user_item(
    user_id: str,
    user: Mapping[str, Any] | None,
    routes: Sequence[Mapping[str, Any]],
    service_lookup: Mapping[str, str],
) -> dict[str, object]:
    ordered_routes = tuple(sorted(routes, key=_route_sort_key))
    available_routes = tuple(route for route in ordered_routes if bool(route.get("available")))
    compute_routes = tuple(
        route for route in ordered_routes if _route_is_compute_service(route, service_lookup)
    )
    waiting_routes = tuple(route for route in ordered_routes if not bool(route.get("available")))
    selected_route = _selected_route(ordered_routes, service_lookup)
    selected_satellite_id = (
        _route_first_satellite(selected_route) if selected_route is not None else None
    )
    destination_id = (
        _route_path(selected_route)[-1] if selected_route is not None and _route_path(selected_route) else None
    )
    flow_id = _str(selected_route.get("flow_id")) if selected_route is not None else ""
    return {
        "user_id": user_id,
        "platform_type": "GROUND_STATION" if user_id.startswith("ground-station") else "GROUND_USER_TERMINAL",
        "cell_id": _str(user.get("cell_id")) if user is not None else "",
        "communication_route_count": len(ordered_routes),
        "available_route_count": len(available_routes),
        "compute_service_count": len(compute_routes),
        "network_queue_count": len(waiting_routes),
        "selected_satellite_id": selected_satellite_id or "",
        "destination_id": destination_id or "",
        "status": _user_status(user, ordered_routes, available_routes),
        "primary_route_id": _str(selected_route.get("route_id")) if selected_route is not None else "",
        "primary_flow_id": flow_id,
        "latency_s": _float(selected_route.get("latency")) if selected_route is not None else None,
        "capacity_mbps": _float(selected_route.get("capacity")) if selected_route is not None else None,
        "loss_proxy_rate": _optional_float(selected_route.get("loss_rate")) if selected_route is not None else None,
        "service_state": service_lookup.get(flow_id, ""),
        "active_business_type": _route_business_type(selected_route, service_lookup),
        "active_business_label": _route_business_label(selected_route, service_lookup),
        "request_state": _user_request_state(
            ordered_routes,
            available_routes,
            compute_routes,
            service_lookup.get(flow_id, ""),
        ),
        "path": tuple(_route_path(selected_route)) if selected_route is not None else (),
    }


def _satellite_service_summary(
    satellites: tuple[Mapping[str, Any], ...],
    compute_nodes: tuple[Mapping[str, Any], ...],
    routes: tuple[Mapping[str, Any], ...],
    links: tuple[Mapping[str, Any], ...],
    satellite_kpi_slices: Mapping[str, Any] | None,
    service_lookup: Mapping[str, str],
    *,
    cursor: int,
    limit: int,
) -> dict[str, object]:
    satellite_ids = tuple(
        sorted(
            {
                *(_str(item.get("satellite_id")) for item in satellites),
                *(_str(item.get("node_id")) for item in compute_nodes),
                *(_str(item.get("satellite_id")) for item in _records((satellite_kpi_slices or {}).get("slices"))),
            }
            - {""},
            key=_entity_sort_key,
        )
    )
    satellite_by_id = {_str(item.get("satellite_id")): item for item in satellites}
    node_by_id = {_str(item.get("node_id")): item for item in compute_nodes}
    slice_by_id = {
        _str(item.get("satellite_id")): item
        for item in _records((satellite_kpi_slices or {}).get("slices"))
    }
    link_counts = _link_counts_by_satellite(links)
    route_context = _route_context_by_satellite(routes, service_lookup)
    normalized_cursor = _page_cursor(cursor)
    normalized_limit = _page_limit(limit)
    page_satellite_ids = satellite_ids[
        normalized_cursor : normalized_cursor + normalized_limit
    ]
    items = tuple(
        _satellite_item(
            satellite_id,
            satellite_by_id.get(satellite_id),
            node_by_id.get(satellite_id),
            slice_by_id.get(satellite_id),
            link_counts.get(satellite_id, {}),
            route_context.get(satellite_id, {}),
        )
        for satellite_id in page_satellite_ids
    )
    next_cursor = min(len(satellite_ids), normalized_cursor + len(items))
    return {
        "version": "v1",
        "source": "BACKEND_RUNTIME_SNAPSHOT",
        "summary_scope": "FULL_SATELLITE_SET_WITH_WINDOW_ITEMS",
        "cursor": normalized_cursor,
        "limit": normalized_limit,
        "next_cursor": next_cursor,
        "has_more": next_cursor < len(satellite_ids),
        "satellite_count": len(satellite_ids),
        "item_count": len(items),
        "window_satellite_count": len(items),
        "hidden_satellite_count": max(0, len(satellite_ids) - len(items)),
        "items": items,
    }


def _satellite_item(
    satellite_id: str,
    satellite: Mapping[str, Any] | None,
    node: Mapping[str, Any] | None,
    kpi_slice: Mapping[str, Any] | None,
    link_counts: Mapping[str, int],
    route_context: Mapping[str, object],
) -> dict[str, object]:
    capacity = max(0.0, _first_float(kpi_slice, "compute_capacity_gflops_fp32", node, "capacity"))
    used = max(
        0.0,
        _first_float(kpi_slice, "compute_used_gflops_fp32", node, "used_cpu_gflops_fp32"),
    )
    if used == 0.0 and node is not None:
        used = max(0.0, capacity - _first_float(node, "available_capacity"))
    load_ratio = _clamp_ratio(
        _first_float(kpi_slice, "compute_load_ratio", node, "load_ratio", default=used / capacity if capacity > 0 else 0.0)
    )
    return {
        "satellite_id": satellite_id,
        "status": _str((node or satellite or {}).get("status")) or "ACTIVE",
        "service_user_ids": tuple(route_context.get("service_user_ids", ())),
        "service_user_count": len(tuple(route_context.get("service_user_ids", ()))),
        "primary_service_user_id": _first_tuple_item(
            tuple(route_context.get("service_user_ids", ()))
        ),
        "next_hop_ids": tuple(route_context.get("next_hop_ids", ())),
        "next_hop_count": len(tuple(route_context.get("next_hop_ids", ()))),
        "primary_next_hop_id": _first_tuple_item(
            tuple(route_context.get("next_hop_ids", ()))
        ),
        "route_count": int(route_context.get("route_count", 0)),
        "available_route_count": int(route_context.get("available_route_count", 0)),
        "compute_service_route_count": int(
            route_context.get("compute_service_route_count", 0)
        ),
        "network_service_route_count": int(
            route_context.get("network_service_route_count", 0)
        ),
        "active_link_count": int(
            _first_float(kpi_slice, "active_link_count", default=float(link_counts.get("active", 0)))
        ),
        "active_access_link_count": int(
            _first_float(kpi_slice, "active_access_link_count", default=float(link_counts.get("access", 0)))
        ),
        "active_space_link_count": int(
            _first_float(kpi_slice, "active_space_link_count", default=float(link_counts.get("space", 0)))
        ),
        "compute_load_ratio": load_ratio,
        "compute_capacity_gflops_fp32": capacity,
        "compute_used_gflops_fp32": used,
        "compute_capacity_gflops_fp64": _first_float(kpi_slice, "compute_capacity_gflops_fp64", node, "cpu_gflops_fp64"),
        "compute_used_gflops_fp64": _first_float(kpi_slice, "compute_used_gflops_fp64", node, "used_cpu_gflops_fp64"),
        "compute_capacity_gpu_tflops_fp32": _first_float(kpi_slice, "compute_capacity_gpu_tflops_fp32", node, "gpu_tflops_fp32"),
        "compute_used_gpu_tflops_fp32": _first_float(kpi_slice, "compute_used_gpu_tflops_fp32", node, "used_gpu_tflops_fp32"),
        "compute_capacity_gpu_tflops_fp16": _first_float(kpi_slice, "compute_capacity_gpu_tflops_fp16", node, "gpu_tflops_fp16"),
        "compute_used_gpu_tflops_fp16": _first_float(kpi_slice, "compute_used_gpu_tflops_fp16", node, "used_gpu_tflops_fp16"),
        "compute_capacity_npu_tops_int8": _first_float(kpi_slice, "compute_capacity_npu_tops_int8", node, "npu_tops_int8"),
        "compute_used_npu_tops_int8": _first_float(kpi_slice, "compute_used_npu_tops_int8", node, "used_npu_tops_int8"),
        "compute_capacity_memory_gb": _first_float(kpi_slice, "compute_capacity_memory_gb", node, "memory_gb"),
        "compute_used_memory_gb": _first_float(kpi_slice, "compute_used_memory_gb", node, "used_memory_gb"),
        "compute_capacity_storage_gb": _first_float(kpi_slice, "compute_capacity_storage_gb", node, "storage_gb"),
        "compute_used_storage_gb": _first_float(kpi_slice, "compute_used_storage_gb", node, "used_storage_gb"),
        "running_task_count": int(_first_float(kpi_slice, "running_task_count", node, "running_tasks")),
        "finished_task_count": int(_first_float(kpi_slice, "finished_task_count", node, "finished_tasks")),
    }


def _route_context_by_satellite(
    routes: tuple[Mapping[str, Any], ...],
    service_lookup: Mapping[str, str],
) -> dict[str, dict[str, object]]:
    context: dict[str, dict[str, object]] = {}
    for route in sorted(routes, key=_route_sort_key):
        path = _route_path(route)
        user_id = _route_user_id(route)
        for index, node_id in enumerate(path):
            if not node_id.startswith("sat-"):
                continue
            entry = context.setdefault(
                node_id,
                {
                    "service_user_ids": set(),
                    "next_hop_ids": set(),
                    "route_count": 0,
                    "available_route_count": 0,
                    "compute_service_route_count": 0,
                    "network_service_route_count": 0,
                },
            )
            entry["route_count"] = int(entry["route_count"]) + 1
            if bool(route.get("available")):
                entry["available_route_count"] = int(entry["available_route_count"]) + 1
            if _route_is_compute_service(route, service_lookup):
                entry["compute_service_route_count"] = (
                    int(entry["compute_service_route_count"]) + 1
                )
            else:
                entry["network_service_route_count"] = (
                    int(entry["network_service_route_count"]) + 1
                )
            if user_id is not None:
                entry["service_user_ids"].add(user_id)  # type: ignore[union-attr]
            next_hop = path[index + 1] if index + 1 < len(path) else "END"
            entry["next_hop_ids"].add(next_hop)  # type: ignore[union-attr]
    return {
        satellite_id: {
            **entry,
            "service_user_ids": tuple(sorted(entry["service_user_ids"], key=_entity_sort_key)),  # type: ignore[arg-type]
            "next_hop_ids": tuple(sorted(entry["next_hop_ids"], key=_entity_sort_key)),  # type: ignore[arg-type]
        }
        for satellite_id, entry in sorted(context.items(), key=lambda item: _entity_sort_key(item[0]))
    }


def _link_counts_by_satellite(
    links: tuple[Mapping[str, Any], ...],
) -> dict[str, dict[str, int]]:
    counts: dict[str, dict[str, int]] = {}
    for link in links:
        if not bool(link.get("availability", True)):
            continue
        source_id = _str(link.get("source_id"))
        target_id = _str(link.get("target_id"))
        for node_id in (source_id, target_id):
            if not node_id.startswith("sat-"):
                continue
            entry = counts.setdefault(node_id, {"active": 0, "access": 0, "space": 0})
            entry["active"] += 1
            if source_id.startswith("sat-") and target_id.startswith("sat-"):
                entry["space"] += 1
            else:
                entry["access"] += 1
    return counts


def _selected_route(
    routes: Sequence[Mapping[str, Any]],
    service_lookup: Mapping[str, str],
) -> Mapping[str, Any] | None:
    if not routes:
        return None
    return sorted(
        routes,
        key=lambda route: (
            not _route_is_compute_service(route, service_lookup),
            not bool(route.get("available")),
            _float(route.get("latency")),
            _str(route.get("route_id")),
        ),
    )[0]


def _user_status(
    user: Mapping[str, Any] | None,
    routes: Sequence[Mapping[str, Any]],
    available_routes: Sequence[Mapping[str, Any]],
) -> str:
    base = _str(user.get("status")) if user is not None else ""
    if not routes:
        return base or "IDLE"
    if available_routes:
        return f"{base}/AVAILABLE" if base else "AVAILABLE"
    return f"{base}/WAITING_ROUTE" if base else "WAITING_ROUTE"


def _user_request_state(
    routes: Sequence[Mapping[str, Any]],
    available_routes: Sequence[Mapping[str, Any]],
    compute_routes: Sequence[Mapping[str, Any]],
    service_state: str,
) -> str:
    if not routes:
        return "IDLE"
    if not available_routes:
        return "NETWORK_WAITING"
    if compute_routes and service_state:
        return "COMPUTE_SERVICE_ACTIVE"
    if compute_routes:
        return "COMPUTE_SERVICE_READY"
    return "NETWORK_SERVICE_READY"


def _route_business_type(
    route: Mapping[str, Any] | None,
    service_lookup: Mapping[str, str],
) -> str:
    if route is None:
        return "NONE"
    if _route_is_compute_service(route, service_lookup):
        return "COMPUTE_SERVICE"
    path = _route_path(route)
    if path and path[0].startswith("sat-"):
        return "BULK_DOWNLINK"
    return "DATA_TRANSFER"


def _route_business_label(
    route: Mapping[str, Any] | None,
    service_lookup: Mapping[str, str],
) -> str:
    labels = {
        "NONE": "无业务",
        "COMPUTE_SERVICE": "通信-计算服务",
        "BULK_DOWNLINK": "批量下传",
        "DATA_TRANSFER": "数据传输",
    }
    return labels[_route_business_type(route, service_lookup)]


def _route_is_compute_service(
    route: Mapping[str, Any],
    service_lookup: Mapping[str, str],
) -> bool:
    flow_id = _str(route.get("flow_id"))
    return flow_id in service_lookup or any(
        "compute" in node_id for node_id in _route_path(route)
    )


def _route_user_id(route: Mapping[str, Any]) -> str | None:
    return next((node_id for node_id in _route_path(route) if node_id.startswith("user-")), None)


def _route_first_satellite(route: Mapping[str, Any]) -> str | None:
    return next((node_id for node_id in _route_path(route) if node_id.startswith("sat-")), None)


def _route_path(route: Mapping[str, Any] | None) -> tuple[str, ...]:
    if route is None:
        return ()
    path = route.get("path", ())
    if not isinstance(path, Sequence) or isinstance(path, (str, bytes)):
        return ()
    return tuple(_str(item) for item in path)


def _first_tuple_item(values: tuple[object, ...]) -> str:
    if not values:
        return ""
    return _str(values[0])


def _route_sort_key(route: Mapping[str, Any]) -> tuple[tuple[object, ...], str]:
    return (_entity_sort_key(_route_user_id(route) or ""), _str(route.get("route_id")))


def _service_lookup(history: Mapping[str, Any] | None) -> dict[str, str]:
    lookup: dict[str, str] = {}
    if history is None:
        return lookup
    for item in _records(history.get("items")):
        label = _service_label(item)
        for key in ("input_flow_id", "output_flow_id"):
            flow_id = _str(item.get(key))
            if flow_id:
                lookup[flow_id] = label
    return lookup


def _service_label(item: Mapping[str, Any]) -> str:
    task_id = _str(item.get("task_id")) or "service"
    total_ms = _optional_float(item.get("total_latency_s"))
    state = "COMPLETE" if bool(item.get("complete")) else "RUNNING"
    if total_ms is None:
        return f"{task_id}/{state}"
    return f"{task_id}/{round(total_ms * 1000.0)}ms/{state}"


def _records(value: object) -> tuple[Mapping[str, Any], ...]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return ()
    return tuple(item for item in value if isinstance(item, Mapping))


def _str(value: object) -> str:
    return "" if value is None else str(value)


def _float(value: object) -> float:
    parsed = _optional_float(value)
    return 0.0 if parsed is None else parsed


def _optional_float(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _first_float(
    first: Mapping[str, Any] | None,
    first_key: str,
    second: Mapping[str, Any] | None = None,
    second_key: str | None = None,
    *,
    default: float = 0.0,
) -> float:
    first_value = _optional_float(first.get(first_key)) if first is not None else None
    if first_value is not None:
        return first_value
    if second is not None:
        second_value = _optional_float(second.get(second_key or first_key))
        if second_value is not None:
            return second_value
    return default


def _clamp_ratio(value: float) -> float:
    return max(0.0, min(1.0, value))


def _page_cursor(value: int) -> int:
    if not isinstance(value, int):
        raise TypeError("cursor must be an int")
    return max(0, value)


def _page_limit(value: int) -> int:
    if not isinstance(value, int):
        raise TypeError("limit must be an int")
    return max(1, value)


def _entity_sort_key(value: str) -> tuple[object, ...]:
    parts: list[object] = []
    current = ""
    in_digit = False
    for char in value:
        if char.isdigit() != in_digit and current:
            parts.append(int(current) if in_digit else current)
            current = ""
        in_digit = char.isdigit()
        current += char
    if current:
        parts.append(int(current) if in_digit else current)
    return tuple(parts)
