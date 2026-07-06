"""Backend-owned runtime observability summaries for dashboard consumers."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from leo_twin.schema.service_lifecycle_trace_contract import (
    SERVICE_LIFECYCLE_TRACE_CONTRACT_V2_ID,
)


RuntimeObservabilitySummary = dict[str, object]
_SERVICE_LIFECYCLE_TRACE_COMPONENTS = (
    "input_network",
    "compute_queue",
    "compute_execution",
    "output_network",
)
_SERVICE_LIFECYCLE_DURATION_FIELDS = {
    "input_network": "input_network_latency_s",
    "compute_queue": "compute_queue_delay_s",
    "compute_execution": "compute_execution_delay_s",
    "output_network": "output_network_latency_s",
}


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

    user_summary = build_runtime_user_request_summary(
        snapshot,
        service_latency_history=service_latency_history,
        cursor=user_cursor,
        limit=user_limit,
    )
    satellite_summary = build_runtime_satellite_service_summary(
        snapshot,
        service_latency_history=service_latency_history,
        satellite_kpi_slices=satellite_kpi_slices,
        cursor=satellite_cursor,
        limit=satellite_limit,
    )
    route_explanation_summary = build_runtime_route_explanation_summary(
        snapshot,
        service_latency_history=service_latency_history,
    )
    return {
        "user_request_summary_v1": user_summary,
        "satellite_service_summary_v1": satellite_summary,
        "route_explanation_summary_v1": route_explanation_summary,
        "compute_task_timeline_summary_v1": build_runtime_compute_task_timeline_summary(
            service_latency_history
        ),
        "service_lifecycle_trace_v2": build_runtime_service_lifecycle_trace_v2(
            service_latency_history
        ),
        "node_detail_summary_v1": build_runtime_node_detail_summary(
            user_summary,
            satellite_summary,
        ),
    }


def build_runtime_compute_task_timeline_summary(
    service_latency_history: Mapping[str, Any] | None,
    *,
    limit: int = 8,
) -> dict[str, object]:
    """Build backend-owned compute queue/execution timeline summary rows."""

    items = tuple(_records((service_latency_history or {}).get("items")))
    ordered_items = tuple(sorted(items, key=_compute_task_timeline_sort_key))
    bounded_limit = _page_limit(limit)
    rows = tuple(
        _compute_task_timeline_item(item) for item in ordered_items[:bounded_limit]
    )
    queue_delays = tuple(
        _float(item.get("compute_queue_delay_s")) for item in ordered_items
    )
    execution_delays = tuple(
        _float(item.get("compute_execution_delay_s")) for item in ordered_items
    )
    return {
        "version": "v1",
        "source": "SERVICE_LATENCY_HISTORY",
        "summary_scope": "RECENT_COMPUTE_TASK_QUEUE_EXECUTION",
        "task_count": len(ordered_items),
        "item_count": len(rows),
        "complete_task_count": sum(1 for item in ordered_items if bool(item.get("complete"))),
        "queued_task_count": sum(
            1 for item in ordered_items if _float(item.get("compute_queue_delay_s")) > 0.0
        ),
        "total_compute_queue_delay_s": sum(queue_delays),
        "total_compute_execution_delay_s": sum(execution_delays),
        "avg_compute_queue_delay_s": _average(queue_delays),
        "avg_compute_execution_delay_s": _average(execution_delays),
        "items": rows,
    }


def build_runtime_service_lifecycle_trace_v2(
    service_latency_history: Mapping[str, Any] | None,
    *,
    cursor: int = 0,
    limit: int = 100,
    query: str = "",
) -> dict[str, object]:
    """Build deterministic product-level communication-compute service traces."""

    items = tuple(_records((service_latency_history or {}).get("items")))
    ordered_items = tuple(sorted(items, key=_service_detail_sort_key))
    all_traces = tuple(_service_lifecycle_trace_item(item) for item in ordered_items)
    filtered_traces = tuple(
        item for item in all_traces if _detail_item_matches_query(item, query)
    )
    normalized_cursor = _page_cursor(cursor)
    normalized_limit = _page_limit(limit)
    traces = filtered_traces[
        normalized_cursor : normalized_cursor + normalized_limit
    ]
    next_cursor = min(len(filtered_traces), normalized_cursor + len(traces))
    filter_query = _normalized_filter_text(query)
    result: dict[str, object] = {
        "version": "v2",
        "contract_id": SERVICE_LIFECYCLE_TRACE_CONTRACT_V2_ID,
        "source": "SERVICE_LATENCY_HISTORY",
        "source_summary": "service_latency_history_v1",
        "summary_scope": (
            "FILTERED_SERVICE_LIFECYCLE_TRACE_WINDOW"
            if filter_query
            else "SERVICE_LIFECYCLE_TRACE_WINDOW"
        ),
        "trace_model": "COMMUNICATION_COMPUTE_COMPONENT_PROXY",
        "cursor": normalized_cursor,
        "limit": normalized_limit,
        "next_cursor": next_cursor,
        "has_more": next_cursor < len(filtered_traces),
        "service_count": len(filtered_traces),
        "trace_count": len(traces),
        "complete_trace_count": sum(
            1 for item in filtered_traces if item["terminal_state"] == "COMPLETE"
        ),
        "running_trace_count": sum(
            1 for item in filtered_traces if item["terminal_state"] == "RUNNING"
        ),
        "incomplete_trace_count": sum(
            1 for item in filtered_traces if item["terminal_state"] == "INCOMPLETE"
        ),
        "hidden_trace_count": max(0, len(filtered_traces) - len(traces)),
        "items": traces,
    }
    if filter_query:
        result.update(
            {
                "unfiltered_service_count": len(ordered_items),
                "filter_query": filter_query,
                "filter_applied": True,
            }
        )
    return result


def build_runtime_node_detail_summary(
    user_summary: Mapping[str, Any],
    satellite_summary: Mapping[str, Any],
) -> dict[str, object]:
    """Build backend-owned UI detail cards from runtime summary rows."""

    if not isinstance(user_summary, Mapping):
        raise TypeError("user_summary must be a mapping")
    if not isinstance(satellite_summary, Mapping):
        raise TypeError("satellite_summary must be a mapping")
    user_cards = tuple(
        _user_detail_card(item) for item in _records(user_summary.get("items"))
    )
    satellite_cards = tuple(
        _satellite_detail_card(item)
        for item in _records(satellite_summary.get("items"))
    )
    return {
        "version": "v1",
        "source": "BACKEND_RUNTIME_STATUS",
        "summary_scope": "VISIBLE_RUNTIME_DETAIL_ROWS",
        "user_detail_count": len(user_cards),
        "satellite_detail_count": len(satellite_cards),
        "users": user_cards,
        "satellites": satellite_cards,
    }


def build_runtime_node_detail_page(
    snapshot: Mapping[str, Any],
    *,
    service_latency_history: Mapping[str, Any] | None = None,
    satellite_kpi_slices: Mapping[str, Any] | None = None,
    cursor: int = 0,
    limit: int = 100,
) -> dict[str, object]:
    """Build one deterministic cursor page of backend-owned node detail cards."""

    if not isinstance(snapshot, Mapping):
        raise TypeError("snapshot must be a mapping")
    normalized_cursor = _page_cursor(cursor)
    normalized_limit = _page_limit(limit)
    user_probe = build_runtime_user_request_summary(
        snapshot,
        service_latency_history=service_latency_history,
        cursor=0,
        limit=1,
    )
    satellite_probe = build_runtime_satellite_service_summary(
        snapshot,
        service_latency_history=service_latency_history,
        satellite_kpi_slices=satellite_kpi_slices,
        cursor=0,
        limit=1,
    )
    user_count = _count(user_probe.get("user_count"))
    satellite_count = _count(satellite_probe.get("satellite_count"))
    total_count = user_count + satellite_count
    remaining = normalized_limit
    user_cards: tuple[dict[str, object], ...] = ()
    satellite_cards: tuple[dict[str, object], ...] = ()
    satellite_cursor = max(0, normalized_cursor - user_count)

    if normalized_cursor < user_count and remaining > 0:
        user_limit = min(remaining, user_count - normalized_cursor)
        user_summary = build_runtime_user_request_summary(
            snapshot,
            service_latency_history=service_latency_history,
            cursor=normalized_cursor,
            limit=user_limit,
        )
        user_cards = tuple(
            _user_detail_card(item) for item in _records(user_summary.get("items"))
        )
        remaining -= len(user_cards)
        satellite_cursor = 0

    if remaining > 0 and satellite_cursor < satellite_count:
        satellite_summary = build_runtime_satellite_service_summary(
            snapshot,
            service_latency_history=service_latency_history,
            satellite_kpi_slices=satellite_kpi_slices,
            cursor=satellite_cursor,
            limit=remaining,
        )
        satellite_cards = tuple(
            _satellite_detail_card(item)
            for item in _records(satellite_summary.get("items"))
        )

    items = user_cards + satellite_cards
    next_cursor = min(total_count, normalized_cursor + len(items))
    return {
        "version": "v1",
        "source": "BACKEND_RUNTIME_STATUS",
        "summary_scope": "COMBINED_USER_SATELLITE_NODE_DETAIL_WINDOW",
        "cursor": normalized_cursor,
        "limit": normalized_limit,
        "next_cursor": next_cursor,
        "has_more": next_cursor < total_count,
        "node_count": total_count,
        "user_count": user_count,
        "satellite_count": satellite_count,
        "item_count": len(items),
        "hidden_node_count": max(0, total_count - len(items)),
        "window_user_detail_count": len(user_cards),
        "window_satellite_detail_count": len(satellite_cards),
        "items": items,
    }


def build_runtime_user_detail_card(
    snapshot: Mapping[str, Any],
    user_id: str,
    *,
    service_latency_history: Mapping[str, Any] | None = None,
) -> dict[str, object] | None:
    """Build one backend-owned user detail card by entity id."""

    if not isinstance(snapshot, Mapping):
        raise TypeError("snapshot must be a mapping")
    normalized_user_id = _str(user_id).strip()
    if not normalized_user_id:
        return None
    service_lookup = _service_lookup(service_latency_history)
    service_detail_lookup = _service_detail_lookup(service_latency_history)
    routes_by_user: dict[str, list[Mapping[str, Any]]] = {}
    for route in _records(snapshot.get("routes")):
        route_user_id = _route_user_id(route)
        if route_user_id is None:
            continue
        routes_by_user.setdefault(route_user_id, []).append(route)
    user_by_id = {
        _str(user.get("user_id")): user
        for user in _records(snapshot.get("ground_users"))
        if _str(user.get("user_id"))
    }
    if normalized_user_id not in user_by_id and normalized_user_id not in routes_by_user:
        return None
    item = _user_item(
        normalized_user_id,
        user_by_id.get(normalized_user_id),
        routes_by_user.get(normalized_user_id, ()),
        service_lookup,
        service_detail_lookup,
    )
    return _user_detail_card(item)


def build_runtime_satellite_detail_card(
    snapshot: Mapping[str, Any],
    satellite_id: str,
    *,
    service_latency_history: Mapping[str, Any] | None = None,
    satellite_kpi_slices: Mapping[str, Any] | None = None,
) -> dict[str, object] | None:
    """Build one backend-owned satellite detail card by entity id."""

    if not isinstance(snapshot, Mapping):
        raise TypeError("snapshot must be a mapping")
    normalized_satellite_id = _str(satellite_id).strip()
    if not normalized_satellite_id:
        return None
    service_lookup = _service_lookup(service_latency_history)
    routes = tuple(_records(snapshot.get("routes")))
    satellites = tuple(_records(snapshot.get("satellites")))
    compute_nodes = tuple(_records(snapshot.get("compute_nodes")))
    links = tuple(_records(snapshot.get("links")))
    satellite_by_id = {
        _str(item.get("satellite_id")): item
        for item in satellites
        if _str(item.get("satellite_id"))
    }
    node_by_id = {
        _str(item.get("node_id")): item
        for item in compute_nodes
        if _str(item.get("node_id"))
    }
    slice_by_id = {
        _str(item.get("satellite_id")): item
        for item in _records((satellite_kpi_slices or {}).get("slices"))
        if _str(item.get("satellite_id"))
    }
    if (
        normalized_satellite_id not in satellite_by_id
        and normalized_satellite_id not in node_by_id
        and normalized_satellite_id not in slice_by_id
    ):
        return None
    link_counts = _link_counts_by_satellite(links)
    route_context = _route_context_by_satellite(routes, service_lookup)
    item = _satellite_item(
        normalized_satellite_id,
        satellite_by_id.get(normalized_satellite_id),
        node_by_id.get(normalized_satellite_id),
        slice_by_id.get(normalized_satellite_id),
        link_counts.get(normalized_satellite_id, {}),
        route_context.get(normalized_satellite_id, {}),
    )
    return _satellite_detail_card(item)


def build_runtime_user_request_summary(
    snapshot: Mapping[str, Any],
    *,
    service_latency_history: Mapping[str, Any] | None = None,
    cursor: int = 0,
    limit: int = 1000,
    query: str = "",
) -> dict[str, object]:
    """Build one deterministic page of per-user request detail rows."""

    if not isinstance(snapshot, Mapping):
        raise TypeError("snapshot must be a mapping")
    service_lookup = _service_lookup(service_latency_history)
    service_detail_lookup = _service_detail_lookup(service_latency_history)
    routes = tuple(_records(snapshot.get("routes")))
    users = tuple(_records(snapshot.get("ground_users")))
    return _user_request_summary(
        users,
        routes,
        service_lookup,
        service_detail_lookup,
        cursor=cursor,
        limit=limit,
        query=query,
    )


def build_runtime_satellite_service_summary(
    snapshot: Mapping[str, Any],
    *,
    service_latency_history: Mapping[str, Any] | None = None,
    satellite_kpi_slices: Mapping[str, Any] | None = None,
    cursor: int = 0,
    limit: int = 1500,
    query: str = "",
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
        query=query,
    )


def build_runtime_route_explanation_summary(
    snapshot: Mapping[str, Any],
    *,
    service_latency_history: Mapping[str, Any] | None = None,
    cursor: int = 0,
    limit: int = 500,
    query: str = "",
    availability: str = "ALL",
    business_type: str = "ALL",
    bottleneck_component: str = "ALL",
) -> dict[str, object]:
    """Build backend-owned route explanation rows for dashboard consumers."""

    if not isinstance(snapshot, Mapping):
        raise TypeError("snapshot must be a mapping")
    routes = tuple(_records(snapshot.get("routes")))
    service_lookup = _service_lookup(service_latency_history)
    ordered_routes = tuple(sorted(routes, key=_route_explanation_sort_key))
    route_items = tuple(
        (route, _route_explanation_item(route, service_lookup))
        for route in ordered_routes
    )
    filtered_route_items = tuple(
        (route, item)
        for route, item in route_items
        if _route_explanation_matches_filter(
            item,
            query=query,
            availability=availability,
            business_type=business_type,
            bottleneck_component=bottleneck_component,
        )
    )
    normalized_cursor = _page_cursor(cursor)
    normalized_limit = _page_limit(limit)
    page_route_items = filtered_route_items[
        normalized_cursor : normalized_cursor + normalized_limit
    ]
    items = tuple(item for _, item in page_route_items)
    next_cursor = min(len(filtered_route_items), normalized_cursor + len(items))
    filter_active = _route_filter_is_active(
        query=query,
        availability=availability,
        business_type=business_type,
        bottleneck_component=bottleneck_component,
    )
    result: dict[str, object] = {
        "version": "v1",
        "source": "BACKEND_RUNTIME_SNAPSHOT",
        "summary_scope": (
            "FILTERED_ROUTE_EXPLANATION_WINDOW"
            if filter_active
            else "ROUTE_EXPLANATION_WINDOW"
        ),
        "cursor": normalized_cursor,
        "limit": normalized_limit,
        "next_cursor": next_cursor,
        "has_more": next_cursor < len(filtered_route_items),
        "route_count": len(filtered_route_items),
        "item_count": len(items),
        "available_route_count": sum(
            1 for route, _ in filtered_route_items if bool(route.get("available"))
        ),
        "blocked_route_count": sum(
            1 for route, _ in filtered_route_items if not bool(route.get("available"))
        ),
        "over_demand_route_count": sum(
            1
            for route, _ in filtered_route_items
            if _route_capacity_below_demand(route)
        ),
        "compute_service_route_count": sum(
            1
            for route, _ in filtered_route_items
            if _route_is_compute_service(route, service_lookup)
        ),
        "network_service_route_count": sum(
            1
            for route, _ in filtered_route_items
            if not _route_is_compute_service(route, service_lookup)
        ),
        "items": items,
    }
    if filter_active:
        result.update(
            {
                "unfiltered_route_count": len(ordered_routes),
                "filter_query": _normalized_filter_text(query),
                "filter_availability": _normalized_filter_choice(
                    availability,
                    default="ALL",
                ),
                "filter_business_type": _normalized_filter_choice(
                    business_type,
                    default="ALL",
                ),
                "filter_bottleneck_component": _normalized_filter_choice(
                    bottleneck_component,
                    default="ALL",
                ),
                "filter_applied": True,
            }
        )
    return result


def build_runtime_service_detail_page(
    service_latency_history: Mapping[str, Any] | None,
    *,
    cursor: int = 0,
    limit: int = 100,
    query: str = "",
) -> dict[str, object]:
    """Build one deterministic cursor page of service lifecycle rows."""

    items = tuple(_records((service_latency_history or {}).get("items")))
    ordered_items = tuple(sorted(items, key=_service_detail_sort_key))
    all_rows = tuple(_service_detail_item(item) for item in ordered_items)
    filtered_rows = tuple(
        row for row in all_rows if _detail_item_matches_query(row, query)
    )
    normalized_cursor = _page_cursor(cursor)
    normalized_limit = _page_limit(limit)
    rows = filtered_rows[
        normalized_cursor : normalized_cursor + normalized_limit
    ]
    next_cursor = min(len(filtered_rows), normalized_cursor + len(rows))
    filter_query = _normalized_filter_text(query)
    result: dict[str, object] = {
        "version": "v1",
        "source": "SERVICE_LATENCY_HISTORY",
        "summary_scope": (
            "FILTERED_SERVICE_LIFECYCLE_DETAIL_WINDOW"
            if filter_query
            else "SERVICE_LIFECYCLE_DETAIL_WINDOW"
        ),
        "cursor": normalized_cursor,
        "limit": normalized_limit,
        "next_cursor": next_cursor,
        "has_more": next_cursor < len(filtered_rows),
        "service_count": len(filtered_rows),
        "item_count": len(rows),
        "complete_service_count": sum(
            1 for row in filtered_rows if bool(row.get("complete"))
        ),
        "queued_service_count": sum(
            1
            for row in filtered_rows
            if _float(row.get("compute_queue_delay_s")) > 0.0
        ),
        "window_service_count": len(rows),
        "hidden_service_count": max(0, len(filtered_rows) - len(rows)),
        "items": rows,
    }
    if filter_query:
        result.update(
            {
                "unfiltered_service_count": len(ordered_items),
                "filter_query": filter_query,
                "filter_applied": True,
            }
        )
    return result


def build_runtime_compute_node_detail_page(
    snapshot: Mapping[str, Any],
    *,
    satellite_kpi_slices: Mapping[str, Any] | None = None,
    cursor: int = 0,
    limit: int = 100,
    query: str = "",
) -> dict[str, object]:
    """Build one deterministic cursor page of satellite-hosted compute nodes."""

    if not isinstance(snapshot, Mapping):
        raise TypeError("snapshot must be a mapping")
    compute_nodes = tuple(_records(snapshot.get("compute_nodes")))
    node_by_id = {_str(item.get("node_id")): item for item in compute_nodes}
    kpi_slice_by_id = {
        _str(item.get("satellite_id")): item
        for item in _records((satellite_kpi_slices or {}).get("slices"))
    }
    node_ids = tuple(
        sorted((node_id for node_id in node_by_id if node_id), key=_entity_sort_key)
    )
    all_rows = tuple(
        _compute_node_detail_item(
            node_id,
            node_by_id[node_id],
            kpi_slice_by_id.get(node_id),
        )
        for node_id in node_ids
    )
    filtered_rows = tuple(
        row for row in all_rows if _detail_item_matches_query(row, query)
    )
    normalized_cursor = _page_cursor(cursor)
    normalized_limit = _page_limit(limit)
    rows = filtered_rows[
        normalized_cursor : normalized_cursor + normalized_limit
    ]
    next_cursor = min(len(filtered_rows), normalized_cursor + len(rows))
    filter_query = _normalized_filter_text(query)
    result: dict[str, object] = {
        "version": "v1",
        "source": "BACKEND_RUNTIME_SNAPSHOT",
        "summary_scope": (
            "FILTERED_COMPUTE_NODE_DETAIL_WINDOW"
            if filter_query
            else "COMPUTE_NODE_DETAIL_WINDOW"
        ),
        "cursor": normalized_cursor,
        "limit": normalized_limit,
        "next_cursor": next_cursor,
        "has_more": next_cursor < len(filtered_rows),
        "compute_node_count": len(filtered_rows),
        "item_count": len(rows),
        "busy_compute_node_count": sum(
            1 for item in rows if str(item["status"]).upper() == "BUSY"
        ),
        "window_compute_node_count": len(rows),
        "hidden_compute_node_count": max(0, len(filtered_rows) - len(rows)),
        "items": rows,
    }
    if filter_query:
        result.update(
            {
                "unfiltered_compute_node_count": len(node_ids),
                "filter_query": filter_query,
                "filter_applied": True,
            }
        )
    return result


def build_runtime_route_detail_item(
    snapshot: Mapping[str, Any],
    route_id: str,
    *,
    service_latency_history: Mapping[str, Any] | None = None,
) -> dict[str, object] | None:
    """Build one backend-owned route explanation row by route id."""

    if not isinstance(snapshot, Mapping):
        raise TypeError("snapshot must be a mapping")
    normalized_route_id = _str(route_id).strip()
    if not normalized_route_id:
        return None
    service_lookup = _service_lookup(service_latency_history)
    for route in sorted(_records(snapshot.get("routes")), key=_route_explanation_sort_key):
        if _str(route.get("route_id")) == normalized_route_id:
            return _route_explanation_item(route, service_lookup)
    return None


def build_runtime_service_detail_item(
    service_latency_history: Mapping[str, Any] | None,
    service_id: str,
) -> dict[str, object] | None:
    """Build one backend-owned service lifecycle row by stable service id."""

    normalized_service_id = _str(service_id).strip()
    if not normalized_service_id:
        return None
    ordered_items = tuple(
        sorted(
            _records((service_latency_history or {}).get("items")),
            key=_service_detail_sort_key,
        )
    )
    for item in ordered_items:
        if _service_id(item) == normalized_service_id:
            return _service_detail_item(item)
    return None


def build_runtime_compute_node_detail_item(
    snapshot: Mapping[str, Any],
    node_id: str,
    *,
    satellite_kpi_slices: Mapping[str, Any] | None = None,
) -> dict[str, object] | None:
    """Build one backend-owned compute-node detail row by node id."""

    if not isinstance(snapshot, Mapping):
        raise TypeError("snapshot must be a mapping")
    normalized_node_id = _str(node_id).strip()
    if not normalized_node_id:
        return None
    node_by_id = {
        _str(item.get("node_id")): item
        for item in _records(snapshot.get("compute_nodes"))
        if _str(item.get("node_id"))
    }
    node = node_by_id.get(normalized_node_id)
    if node is None:
        return None
    kpi_slice_by_id = {
        _str(item.get("satellite_id")): item
        for item in _records((satellite_kpi_slices or {}).get("slices"))
        if _str(item.get("satellite_id"))
    }
    return _compute_node_detail_item(
        normalized_node_id,
        node,
        kpi_slice_by_id.get(normalized_node_id),
    )


def _user_request_summary(
    users: tuple[Mapping[str, Any], ...],
    routes: tuple[Mapping[str, Any], ...],
    service_lookup: Mapping[str, str],
    service_detail_lookup: Mapping[str, Mapping[str, Any]],
    *,
    cursor: int,
    limit: int,
    query: str,
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
    all_items = tuple(
        _user_item(
            user_id,
            user_by_id.get(user_id),
            routes_by_user.get(user_id, ()),
            service_lookup,
            service_detail_lookup,
        )
        for user_id in user_ids
    )
    filtered_items = tuple(
        item for item in all_items if _detail_item_matches_query(item, query)
    )
    active_count = sum(
        1 for item in filtered_items if item["communication_route_count"] > 0
    )
    compute_count = sum(
        1 for item in filtered_items if item["compute_service_count"] > 0
    )
    waiting_count = sum(
        1 for item in filtered_items if item["network_queue_count"] > 0
    )
    normalized_cursor = _page_cursor(cursor)
    normalized_limit = _page_limit(limit)
    items = filtered_items[
        normalized_cursor : normalized_cursor + normalized_limit
    ]
    next_cursor = min(len(filtered_items), normalized_cursor + len(items))
    filter_query = _normalized_filter_text(query)
    result: dict[str, object] = {
        "version": "v1",
        "source": "BACKEND_RUNTIME_SNAPSHOT",
        "summary_scope": (
            "FILTERED_USER_SET_WITH_WINDOW_ITEMS"
            if filter_query
            else "FULL_USER_SET_WITH_WINDOW_ITEMS"
        ),
        "cursor": normalized_cursor,
        "limit": normalized_limit,
        "next_cursor": next_cursor,
        "has_more": next_cursor < len(filtered_items),
        "user_count": len(filtered_items),
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
        "hidden_user_count": max(0, len(filtered_items) - len(items)),
        "items": items,
    }
    if filter_query:
        result.update(
            {
                "unfiltered_user_count": len(user_ids),
                "filter_query": filter_query,
                "filter_applied": True,
            }
        )
    return result


def _user_item(
    user_id: str,
    user: Mapping[str, Any] | None,
    routes: Sequence[Mapping[str, Any]],
    service_lookup: Mapping[str, str],
    service_detail_lookup: Mapping[str, Mapping[str, Any]],
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
    selected_path = (
        tuple(_route_path(selected_route)) if selected_route is not None else ()
    )
    destination_id = (
        selected_path[-1] if selected_route is not None and selected_path else None
    )
    flow_id = _str(selected_route.get("flow_id")) if selected_route is not None else ""
    service_detail = service_detail_lookup.get(flow_id, {})
    platform_type = (
        "GROUND_STATION" if user_id.startswith("ground-station") else "GROUND_USER_TERMINAL"
    )
    request_state = _user_request_state(
        ordered_routes,
        available_routes,
        compute_routes,
        service_lookup.get(flow_id, ""),
    )
    queue_reason = _network_queue_reason(
        ordered_routes,
        available_routes,
        waiting_routes,
        selected_route,
    )
    return {
        "user_id": user_id,
        "platform_type": platform_type,
        "platform_type_label": _platform_type_label(platform_type),
        "cell_id": _str(user.get("cell_id")) if user is not None else "",
        "communication_route_count": len(ordered_routes),
        "available_route_count": len(available_routes),
        "compute_service_count": len(compute_routes),
        "network_queue_count": len(waiting_routes),
        "network_queue_reason": queue_reason,
        "network_queue_reason_label": _network_queue_reason_label(queue_reason),
        "selected_satellite_id": selected_satellite_id or "",
        "destination_id": destination_id or "",
        "status": _user_status(user, ordered_routes, available_routes),
        "primary_route_id": _str(selected_route.get("route_id")) if selected_route is not None else "",
        "primary_flow_id": flow_id,
        "primary_next_hop_id": _route_next_hop_after_user(selected_path, user_id),
        "route_hop_count": max(0, len(selected_path) - 1),
        "route_path_label": _route_path_label(selected_path),
        "latency_s": _float(selected_route.get("latency")) if selected_route is not None else None,
        "capacity_mbps": _float(selected_route.get("capacity")) if selected_route is not None else None,
        "loss_proxy_rate": _optional_float(selected_route.get("loss_rate")) if selected_route is not None else None,
        "service_state": service_lookup.get(flow_id, ""),
        "service_task_id": _str(service_detail.get("task_id")),
        "service_complete": bool(service_detail.get("complete", False)),
        "service_total_latency_s": _optional_float(
            service_detail.get("total_latency_s")
        ),
        "input_network_latency_s": _optional_float(
            service_detail.get("input_network_latency_s")
        ),
        "compute_queue_delay_s": _optional_float(
            service_detail.get("compute_queue_delay_s")
        ),
        "compute_execution_delay_s": _optional_float(
            service_detail.get("compute_execution_delay_s")
        ),
        "output_network_latency_s": _optional_float(
            service_detail.get("output_network_latency_s")
        ),
        "input_route_id": _str(service_detail.get("input_route_id")),
        "output_route_id": _str(service_detail.get("output_route_id")),
        **_service_placement_detail_fields(service_detail),
        "active_business_type": _route_business_type(selected_route, service_lookup),
        "active_business_label": _route_business_label(selected_route, service_lookup),
        "request_state": request_state,
        "request_state_label": _request_state_label(request_state),
        "path": selected_path,
    }


def _service_placement_detail_fields(
    service_detail: Mapping[str, Any],
) -> dict[str, object]:
    keys = (
        "compute_node_id",
        "service_placement_status",
        "service_placement_policy",
        "service_placement_bottleneck_resource",
        "service_placement_candidate_count",
        "service_placement_capable_candidate_count",
        "service_placement_candidate_queue_label",
    )
    if not any(key in service_detail for key in keys):
        return {}
    return {
        "compute_node_id": _str(service_detail.get("compute_node_id")),
        "service_placement_status": _str(
            service_detail.get("service_placement_status")
        ),
        "service_placement_policy": _str(
            service_detail.get("service_placement_policy")
        ),
        "service_placement_bottleneck_resource": _str(
            service_detail.get("service_placement_bottleneck_resource")
        ),
        "service_placement_candidate_count": _optional_int(
            service_detail.get("service_placement_candidate_count")
        ),
        "service_placement_capable_candidate_count": _optional_int(
            service_detail.get("service_placement_capable_candidate_count")
        ),
        "service_placement_candidate_queue_label": _str(
            service_detail.get("service_placement_candidate_queue_label")
        ),
    }


def _user_detail_card(item: Mapping[str, Any]) -> dict[str, object]:
    user_id = _str(item.get("user_id"))
    cell_id = _str(item.get("cell_id"))
    route_count = _count(item.get("communication_route_count"))
    available_route_count = _count(item.get("available_route_count"))
    compute_service_count = _count(item.get("compute_service_count"))
    queue_count = _count(item.get("network_queue_count"))
    next_hop = _str(item.get("primary_next_hop_id"))
    communication = (
        f"{available_route_count} / {route_count} 条路由"
        if route_count > 0
        else "无通信业务"
    )
    if next_hop:
        communication = f"{communication} / 下一跳 {next_hop}"
    queue_reason = _str(item.get("network_queue_reason_label")) or _str(
        item.get("network_queue_reason")
    )
    platform_field = _detail_field(
        "平台",
        _join_non_empty(
            _str(item.get("platform_type_label"))
            or _str(item.get("platform_type")),
            cell_id,
            separator=" / ",
        ),
    )
    communication_field = _detail_field("通信", communication)
    compute_field = _detail_field(
        "计算",
        f"{compute_service_count} 条计算业务"
        if compute_service_count > 0
        else "无计算业务",
        tone="resource",
    )
    queue_field = _detail_field(
        "网络队列",
        f"{queue_count} 条 / {queue_reason}" if queue_count > 0 else "队列空",
        tone="warning" if queue_count > 0 else "normal",
    )
    target_satellite_field = _detail_field(
        "目标卫星",
        _str(item.get("selected_satellite_id")),
    )
    target_node_field = _detail_field("目标节点", _str(item.get("destination_id")))
    placement_field = _detail_field(
        "服务放置",
        _user_placement_label(item),
        tone="resource",
    )
    latency_capacity_field = _detail_field(
        "时延/容量",
        _user_latency_capacity_label(item),
    )
    service_link_field = _detail_field("服务链路", _user_service_label(item))
    path_field = _detail_field(
        "路径",
        _str(item.get("route_path_label"))
        or _route_path_label(_string_sequence(item.get("path"))),
    )
    fields = (
        platform_field,
        communication_field,
        compute_field,
        queue_field,
        target_satellite_field,
        target_node_field,
        placement_field,
        latency_capacity_field,
        service_link_field,
        path_field,
    )
    return {
        "entity_type": "USER",
        "entity_id": user_id,
        "title": f"用户 {user_id}",
        "subtitle": _str(item.get("status")) or "IDLE",
        "sections": (
            _detail_section("identity", "节点身份", (platform_field, communication_field)),
            _detail_section(
                "business_path",
                "业务链路",
                (
                    target_satellite_field,
                    target_node_field,
                    latency_capacity_field,
                    service_link_field,
                    path_field,
                ),
            ),
            _detail_section(
                "compute_placement",
                "计算与队列",
                (compute_field, queue_field, placement_field),
            ),
        ),
        "fields": fields,
    }


def _satellite_detail_card(item: Mapping[str, Any]) -> dict[str, object]:
    satellite_id = _str(item.get("satellite_id"))
    load_field = _detail_field(
        "负载",
        _ratio_percent_label(_float(item.get("compute_load_ratio"))),
        tone="resource",
    )
    service_object_field = _detail_field(
        "服务对象",
        _compact_entity_list(
            _string_sequence(item.get("service_user_ids")),
            _count(item.get("service_user_count")),
            "用户",
        ),
    )
    next_hop_field = _detail_field(
        "下一跳",
        _compact_entity_list(
            _string_sequence(item.get("next_hop_ids")),
            _count(item.get("next_hop_count")),
            "跳",
        ),
    )
    cpu_fp32_field = _detail_field(
        "CPU FP32",
        _resource_usage_label(
            _float(item.get("compute_used_gflops_fp32")),
            _float(item.get("compute_capacity_gflops_fp32")),
            "GFLOPS",
        ),
        tone="resource",
    )
    cpu_fp64_field = _detail_field(
        "CPU FP64",
        _resource_usage_label(
            _float(item.get("compute_used_gflops_fp64")),
            _float(item.get("compute_capacity_gflops_fp64")),
            "GFLOPS",
        ),
        tone="resource",
    )
    gpu_field = _detail_field(
        "GPU",
        (
            "FP32 "
            + _resource_usage_label(
                _float(item.get("compute_used_gpu_tflops_fp32")),
                _float(item.get("compute_capacity_gpu_tflops_fp32")),
                "TFLOPS",
            )
            + " / FP16 "
            + _resource_usage_label(
                _float(item.get("compute_used_gpu_tflops_fp16")),
                _float(item.get("compute_capacity_gpu_tflops_fp16")),
                "TFLOPS",
            )
        ),
        tone="resource",
    )
    npu_field = _detail_field(
        "NPU",
        _resource_usage_label(
            _float(item.get("compute_used_npu_tops_int8")),
            _float(item.get("compute_capacity_npu_tops_int8")),
            "TOPS",
        ),
        tone="resource",
    )
    memory_storage_field = _detail_field(
        "内存/存储",
        (
            "内存 "
            + _resource_usage_label(
                _float(item.get("compute_used_memory_gb")),
                _float(item.get("compute_capacity_memory_gb")),
                "GB",
            )
            + " / 存储 "
            + _resource_usage_label(
                _float(item.get("compute_used_storage_gb")),
                _float(item.get("compute_capacity_storage_gb")),
                "GB",
            )
        ),
        tone="resource",
    )
    task_field = _detail_field(
        "任务",
        (
            f"{_count(item.get('running_task_count'))} 运行 / "
            f"{_count(item.get('finished_task_count'))} 完成"
        ),
    )
    network_field = _detail_field("网络", _satellite_network_label(item))
    fields = (
        load_field,
        service_object_field,
        next_hop_field,
        cpu_fp32_field,
        cpu_fp64_field,
        gpu_field,
        npu_field,
        memory_storage_field,
        task_field,
        network_field,
    )
    return {
        "entity_type": "SATELLITE",
        "entity_id": satellite_id,
        "title": f"卫星 {satellite_id}",
        "subtitle": _join_non_empty(
            _str(item.get("status")) or "ACTIVE",
            _str(item.get("resource_role_label")),
            separator=" / ",
        ),
        "sections": (
            _detail_section(
                "service_routing",
                "服务与路由",
                (service_object_field, next_hop_field, task_field),
            ),
            _detail_section(
                "compute_resources",
                "算力资源",
                (
                    load_field,
                    cpu_fp32_field,
                    cpu_fp64_field,
                    gpu_field,
                    npu_field,
                    memory_storage_field,
                ),
            ),
            _detail_section("network_state", "网络状态", (network_field,)),
        ),
        "fields": fields,
    }


def _detail_field(label: str, value: object, *, tone: str = "normal") -> dict[str, str]:
    field = {
        "label": label,
        "value": _detail_value(value),
        "tone": tone,
    }
    return field


def _detail_section(
    section_id: str,
    title: str,
    fields: tuple[dict[str, str], ...],
) -> dict[str, object]:
    return {
        "section_id": section_id,
        "title": title,
        "fields": fields,
    }


def _detail_value(value: object) -> str:
    text = _str(value).strip()
    return text or "无"


def _user_placement_label(item: Mapping[str, Any]) -> str:
    compute_node_id = _str(item.get("compute_node_id"))
    if not compute_node_id:
        return "无计算放置"
    candidate_count = _optional_int(item.get("service_placement_candidate_count"))
    capable_count = _optional_int(
        item.get("service_placement_capable_candidate_count")
    )
    candidate_label = (
        f"候选 {max(0, capable_count or 0)}/{max(0, candidate_count or 0)}"
        if candidate_count is not None
        else ""
    )
    candidate_queue_label = _str(
        item.get("service_placement_candidate_queue_label")
    )
    return _join_non_empty(
        f"节点 {compute_node_id}",
        _str(item.get("service_placement_status")),
        f"策略 {_str(item.get('service_placement_policy'))}"
        if _str(item.get("service_placement_policy"))
        else "",
        f"瓶颈 {_str(item.get('service_placement_bottleneck_resource'))}"
        if _str(item.get("service_placement_bottleneck_resource"))
        else "",
        candidate_label,
        f"队列 {candidate_queue_label}" if candidate_queue_label else "",
        separator=" / ",
    )


def _user_latency_capacity_label(item: Mapping[str, Any]) -> str:
    latency = _optional_float(item.get("latency_s"))
    capacity = _optional_float(item.get("capacity_mbps"))
    if latency is None and capacity is None:
        return "无可用路由"
    return (
        f"{_format_number(latency or 0.0)} s / "
        f"{_format_number(capacity or 0.0)} Mbps"
    )


def _user_service_label(item: Mapping[str, Any]) -> str:
    parts = (
        _str(item.get("active_business_label")),
        _str(item.get("request_state_label")) or _str(item.get("request_state")),
        _str(item.get("service_task_id")),
        _str(item.get("service_state")),
    )
    return _join_non_empty(*parts, separator=" / ") or "无服务链路"


def _satellite_network_label(item: Mapping[str, Any]) -> str:
    link_part = (
        f"链路 {_count(item.get('active_link_count'))} / "
        f"接入 {_count(item.get('active_access_link_count'))} / "
        f"星间 {_count(item.get('active_space_link_count'))}"
    )
    route_part = (
        f"路由 {_count(item.get('available_route_count'))}/"
        f"{_count(item.get('route_count'))}"
    )
    queue_part = f"排队 {_count(item.get('network_queue_route_count'))}"
    kpi_part = _join_non_empty(
        f"时延 {_format_number(_float(item.get('route_latency_avg_s')))} s"
        if _optional_float(item.get("route_latency_avg_s")) is not None
        else "",
        f"损耗 {_format_number(_float(item.get('route_loss_proxy_rate')) * 100.0)}%"
        if _optional_float(item.get("route_loss_proxy_rate")) is not None
        else "",
        separator=" / ",
    )
    return _join_non_empty(link_part, route_part, queue_part, kpi_part, separator=" / ")


def _compute_task_timeline_sort_key(item: Mapping[str, Any]) -> tuple[float, str]:
    return (
        -_float(item.get("last_sample_sim_time")),
        _str(item.get("task_id")),
    )


def _compute_task_timeline_item(item: Mapping[str, Any]) -> dict[str, object]:
    queue_delay = _float(item.get("compute_queue_delay_s"))
    execution_delay = _float(item.get("compute_execution_delay_s"))
    total_latency = _float(item.get("total_latency_s"))
    stages = tuple(
        _compute_task_stage(stage)
        for stage in _records(item.get("component_timeline"))
        if _str(stage.get("component")) in {
            "input_network",
            "compute_queue",
            "compute_execution",
            "output_network",
            "total",
        }
    )
    return {
        "task_id": _str(item.get("task_id")),
        "compute_node_id": _str(item.get("compute_node_id")),
        "placement_status": _str(item.get("service_placement_status")),
        "placement_bottleneck_resource": _str(
            item.get("service_placement_bottleneck_resource")
        ),
        "queue_delay_s": queue_delay,
        "execution_delay_s": execution_delay,
        "total_latency_s": total_latency,
        "complete": bool(item.get("complete")),
        "queue_state": "QUEUED" if queue_delay > 0.0 else "NO_QUEUE",
        "queue_state_label": (
            "Compute queue waiting" if queue_delay > 0.0 else "No compute queue"
        ),
        "first_sample_sim_time": _optional_float(item.get("first_sample_sim_time")),
        "last_sample_sim_time": _optional_float(item.get("last_sample_sim_time")),
        "stage_count": len(stages),
        "stages": stages,
    }


def _service_detail_sort_key(item: Mapping[str, Any]) -> tuple[float, str, str]:
    return (
        -_float(item.get("last_sample_sim_time")),
        _str(item.get("task_id")),
        _str(item.get("input_flow_id")),
    )


def _service_detail_item(item: Mapping[str, Any]) -> dict[str, object]:
    stages = tuple(
        _compute_task_stage(stage)
        for stage in _records(item.get("component_timeline"))
        if _str(stage.get("component")) in {
            "input_network",
            "compute_queue",
            "compute_execution",
            "output_network",
            "total",
        }
    )
    complete = bool(item.get("complete"))
    return {
        "service_id": _service_id(item),
        "task_id": _str(item.get("task_id")),
        "input_flow_id": _str(item.get("input_flow_id")),
        "output_flow_id": _str(item.get("output_flow_id")),
        "input_route_id": _str(item.get("input_route_id")),
        "output_route_id": _str(item.get("output_route_id")),
        "compute_node_id": _str(item.get("compute_node_id")),
        "complete": complete,
        "service_state": "COMPLETE" if complete else "RUNNING",
        "service_state_label": "Service complete" if complete else "Service running",
        "placement_status": _str(item.get("service_placement_status")),
        "placement_policy": _str(item.get("service_placement_policy")),
        "placement_bottleneck_resource": _str(
            item.get("service_placement_bottleneck_resource")
        ),
        "placement_candidate_count": _optional_int(
            item.get("service_placement_candidate_count")
        ),
        "placement_capable_candidate_count": _optional_int(
            item.get("service_placement_capable_candidate_count")
        ),
        "placement_candidate_queue_label": _str(
            item.get("service_placement_candidate_queue_label")
        ),
        "first_sample_sim_time": _optional_float(item.get("first_sample_sim_time")),
        "last_sample_sim_time": _optional_float(item.get("last_sample_sim_time")),
        "input_network_latency_s": _float(item.get("input_network_latency_s")),
        "compute_queue_delay_s": _float(item.get("compute_queue_delay_s")),
        "compute_execution_delay_s": _float(item.get("compute_execution_delay_s")),
        "output_network_latency_s": _float(item.get("output_network_latency_s")),
        "total_latency_s": _float(item.get("total_latency_s")),
        "stage_count": len(stages),
        "stages": stages,
    }


def _service_lifecycle_trace_item(item: Mapping[str, Any]) -> dict[str, object]:
    service_id = _service_request_id(item)
    stages = tuple(
        _service_lifecycle_trace_stage(item, component, index)
        for index, component in enumerate(_SERVICE_LIFECYCLE_TRACE_COMPONENTS)
    )
    terminal_state = _service_lifecycle_terminal_state(item, stages)
    return {
        "trace_id": f"trace:{service_id}",
        "service_id": service_id,
        "task_id": _str(item.get("task_id")),
        "service_class": "COMPUTE_SERVICE",
        "input_flow_id": _str(item.get("input_flow_id")),
        "output_flow_id": _str(item.get("output_flow_id")),
        "input_route_id": _str(item.get("input_route_id")),
        "output_route_id": _str(item.get("output_route_id")),
        "compute_node_id": _str(item.get("compute_node_id")),
        "placement_status": _str(item.get("service_placement_status")),
        "placement_policy": _str(item.get("service_placement_policy")),
        "placement_bottleneck_resource": _str(
            item.get("service_placement_bottleneck_resource")
        ),
        "first_sample_sim_time": _optional_float(item.get("first_sample_sim_time")),
        "last_sample_sim_time": _optional_float(item.get("last_sample_sim_time")),
        "input_network_latency_s": _float(item.get("input_network_latency_s")),
        "compute_queue_delay_s": _float(item.get("compute_queue_delay_s")),
        "compute_execution_delay_s": _float(item.get("compute_execution_delay_s")),
        "output_network_latency_s": _float(item.get("output_network_latency_s")),
        "total_latency_s": _float(item.get("total_latency_s")),
        "terminal_state": terminal_state,
        "terminal_state_reason": _service_lifecycle_terminal_reason(item, stages),
        "stage_count": len(stages),
        "observed_stage_count": sum(
            1 for stage in stages if stage["stage_status"] == "OBSERVED"
        ),
        "pending_stage_count": sum(
            1 for stage in stages if stage["stage_status"] == "PENDING"
        ),
        "stages": stages,
    }


def _service_lifecycle_trace_stage(
    item: Mapping[str, Any],
    component: str,
    index: int,
) -> dict[str, object]:
    stage = _service_component_stage(item, component)
    duration_field = _SERVICE_LIFECYCLE_DURATION_FIELDS[component]
    duration = (
        _optional_float(stage.get("duration_s"))
        if stage is not None
        else _optional_float(item.get(duration_field))
    )
    observed = stage is not None or duration is not None
    status = _service_lifecycle_stage_status(item, component, observed)
    route_id = _service_lifecycle_stage_route_id(item, component, stage)
    flow_id = _service_lifecycle_stage_flow_id(item, component, stage)
    return {
        "stage_index": index,
        "stage_id": f"{_service_request_id(item)}:{component}",
        "component": component,
        "stage_kind": component.upper(),
        "stage_label": _compute_task_stage_label(component),
        "stage_status": status,
        "sample_sim_time": (
            _optional_float(stage.get("sample_sim_time"))
            if stage is not None
            else _optional_float(item.get("last_sample_sim_time"))
        ),
        "duration_s": 0.0 if duration is None else duration,
        "flow_id": flow_id,
        "route_id": route_id,
        "compute_node_id": (
            _str(item.get("compute_node_id"))
            if component in {"compute_queue", "compute_execution"}
            else ""
        ),
    }


def _service_component_stage(
    item: Mapping[str, Any],
    component: str,
) -> Mapping[str, Any] | None:
    for stage in _records(item.get("component_timeline")):
        if _str(stage.get("component")) == component:
            return stage
    return None


def _service_lifecycle_stage_status(
    item: Mapping[str, Any],
    component: str,
    observed: bool,
) -> str:
    if observed:
        return "OBSERVED"
    if component == "output_network" and _str(item.get("output_flow_id")):
        return "PENDING"
    return "UNKNOWN"


def _service_lifecycle_stage_route_id(
    item: Mapping[str, Any],
    component: str,
    stage: Mapping[str, Any] | None,
) -> str:
    if stage is not None and _str(stage.get("route_id")):
        return _str(stage.get("route_id"))
    if component == "input_network":
        return _str(item.get("input_route_id"))
    if component == "output_network":
        return _str(item.get("output_route_id"))
    return ""


def _service_lifecycle_stage_flow_id(
    item: Mapping[str, Any],
    component: str,
    stage: Mapping[str, Any] | None,
) -> str:
    if stage is not None:
        flow_id = _str(stage.get("output_flow_id")) or _str(stage.get("input_flow_id"))
        if flow_id:
            return flow_id
    if component == "output_network":
        return _str(item.get("output_flow_id"))
    if component == "input_network":
        return _str(item.get("input_flow_id"))
    return ""


def _service_lifecycle_terminal_state(
    item: Mapping[str, Any],
    stages: tuple[dict[str, object], ...],
) -> str:
    if bool(item.get("complete")):
        return "COMPLETE"
    if any(stage["stage_status"] == "OBSERVED" for stage in stages):
        return "RUNNING"
    return "INCOMPLETE"


def _service_lifecycle_terminal_reason(
    item: Mapping[str, Any],
    stages: tuple[dict[str, object], ...],
) -> str:
    if bool(item.get("complete")):
        return "TOTAL_LATENCY_OBSERVED"
    if any(
        stage["component"] == "output_network" and stage["stage_status"] == "PENDING"
        for stage in stages
    ):
        return "OUTPUT_NETWORK_PENDING"
    if any(stage["stage_status"] == "OBSERVED" for stage in stages):
        return "COMPONENTS_OBSERVED_BUT_TOTAL_MISSING"
    return "NO_COMPONENT_OBSERVATIONS"


def _compute_node_detail_item(
    node_id: str,
    node: Mapping[str, Any],
    kpi_slice: Mapping[str, Any] | None,
) -> dict[str, object]:
    capacity = max(
        0.0,
        _first_float(kpi_slice, "compute_capacity_gflops_fp32", node, "capacity"),
    )
    used = max(
        0.0,
        _first_float(
            kpi_slice,
            "compute_used_gflops_fp32",
            node,
            "used_cpu_gflops_fp32",
        ),
    )
    if used == 0.0:
        used = max(0.0, capacity - _first_float(node, "available_capacity"))
    return {
        "node_id": node_id,
        "platform_type": "SATELLITE_COMPUTE_NODE",
        "status": _str(node.get("status")) or "IDLE",
        "compute_load_ratio": _clamp_ratio(
            _first_float(
                kpi_slice,
                "compute_load_ratio",
                node,
                "load_ratio",
                default=used / capacity if capacity > 0.0 else 0.0,
            )
        ),
        "compute_capacity_gflops_fp32": capacity,
        "compute_used_gflops_fp32": used,
        "compute_available_gflops_fp32": max(0.0, capacity - used),
        "compute_capacity_gflops_fp64": _first_float(
            kpi_slice,
            "compute_capacity_gflops_fp64",
            node,
            "cpu_gflops_fp64",
        ),
        "compute_used_gflops_fp64": _first_float(
            kpi_slice,
            "compute_used_gflops_fp64",
            node,
            "used_cpu_gflops_fp64",
        ),
        "compute_capacity_gpu_tflops_fp32": _first_float(
            kpi_slice,
            "compute_capacity_gpu_tflops_fp32",
            node,
            "gpu_tflops_fp32",
        ),
        "compute_used_gpu_tflops_fp32": _first_float(
            kpi_slice,
            "compute_used_gpu_tflops_fp32",
            node,
            "used_gpu_tflops_fp32",
        ),
        "compute_capacity_gpu_tflops_fp16": _first_float(
            kpi_slice,
            "compute_capacity_gpu_tflops_fp16",
            node,
            "gpu_tflops_fp16",
        ),
        "compute_used_gpu_tflops_fp16": _first_float(
            kpi_slice,
            "compute_used_gpu_tflops_fp16",
            node,
            "used_gpu_tflops_fp16",
        ),
        "compute_capacity_npu_tops_int8": _first_float(
            kpi_slice,
            "compute_capacity_npu_tops_int8",
            node,
            "npu_tops_int8",
        ),
        "compute_used_npu_tops_int8": _first_float(
            kpi_slice,
            "compute_used_npu_tops_int8",
            node,
            "used_npu_tops_int8",
        ),
        "compute_capacity_memory_gb": _first_float(
            kpi_slice,
            "compute_capacity_memory_gb",
            node,
            "memory_gb",
        ),
        "compute_used_memory_gb": _first_float(
            kpi_slice,
            "compute_used_memory_gb",
            node,
            "used_memory_gb",
        ),
        "compute_capacity_storage_gb": _first_float(
            kpi_slice,
            "compute_capacity_storage_gb",
            node,
            "storage_gb",
        ),
        "compute_used_storage_gb": _first_float(
            kpi_slice,
            "compute_used_storage_gb",
            node,
            "used_storage_gb",
        ),
        "running_task_count": int(
            _first_float(kpi_slice, "running_task_count", node, "running_tasks")
        ),
        "finished_task_count": int(
            _first_float(kpi_slice, "finished_task_count", node, "finished_tasks")
        ),
    }


def _compute_task_stage(stage: Mapping[str, Any]) -> dict[str, object]:
    component = _str(stage.get("component"))
    return {
        "component": component,
        "label": _compute_task_stage_label(component),
        "sample_sim_time": _optional_float(stage.get("sample_sim_time")),
        "duration_s": _float(stage.get("duration_s")),
        "route_id": _str(stage.get("route_id")),
    }


def _compute_task_stage_label(component: str) -> str:
    labels = {
        "input_network": "Input network",
        "compute_queue": "Compute queue",
        "compute_execution": "Compute execution",
        "output_network": "Output network",
        "total": "Total service latency",
    }
    return labels.get(component, component)


def _compact_entity_list(values: tuple[str, ...], total_count: int, unit: str) -> str:
    normalized = tuple(value for value in values if value)
    total = max(total_count, len(normalized))
    if total <= 0:
        return "无"
    visible = ", ".join(normalized[:3]) if normalized else f"{total} 个{unit}"
    hidden_count = max(0, total - len(normalized[:3]))
    return f"{visible} +{hidden_count} 个{unit}" if hidden_count > 0 else visible


def _resource_usage_label(used: float, capacity: float, unit: str) -> str:
    return f"{_format_number(max(0.0, used))} / {_format_number(max(0.0, capacity))} {unit}"


def _ratio_percent_label(value: float) -> str:
    return f"{_format_number(_clamp_ratio(value) * 100.0)}%"


def _format_number(value: float) -> str:
    rounded = round(float(value), 3)
    if rounded.is_integer():
        return str(int(rounded))
    return f"{rounded:.3f}".rstrip("0").rstrip(".")


def _join_non_empty(*values: object, separator: str) -> str:
    return separator.join(_str(value) for value in values if _str(value))


def _string_sequence(value: object) -> tuple[str, ...]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return ()
    return tuple(_str(item) for item in value if _str(item))


def _count(value: object) -> int:
    parsed = _optional_int(value)
    return max(0, parsed or 0)


def _average(values: tuple[float, ...]) -> float:
    return sum(values) / len(values) if values else 0.0


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
    query: str,
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
    all_items = tuple(
        _satellite_item(
            satellite_id,
            satellite_by_id.get(satellite_id),
            node_by_id.get(satellite_id),
            slice_by_id.get(satellite_id),
            link_counts.get(satellite_id, {}),
            route_context.get(satellite_id, {}),
        )
        for satellite_id in satellite_ids
    )
    filtered_items = tuple(
        item for item in all_items if _detail_item_matches_query(item, query)
    )
    normalized_cursor = _page_cursor(cursor)
    normalized_limit = _page_limit(limit)
    items = filtered_items[
        normalized_cursor : normalized_cursor + normalized_limit
    ]
    next_cursor = min(len(filtered_items), normalized_cursor + len(items))
    filter_query = _normalized_filter_text(query)
    result: dict[str, object] = {
        "version": "v1",
        "source": "BACKEND_RUNTIME_SNAPSHOT",
        "summary_scope": (
            "FILTERED_SATELLITE_SET_WITH_WINDOW_ITEMS"
            if filter_query
            else "FULL_SATELLITE_SET_WITH_WINDOW_ITEMS"
        ),
        "cursor": normalized_cursor,
        "limit": normalized_limit,
        "next_cursor": next_cursor,
        "has_more": next_cursor < len(filtered_items),
        "satellite_count": len(filtered_items),
        "item_count": len(items),
        "window_satellite_count": len(items),
        "hidden_satellite_count": max(0, len(filtered_items) - len(items)),
        "items": items,
    }
    if filter_query:
        result.update(
            {
                "unfiltered_satellite_count": len(satellite_ids),
                "filter_query": filter_query,
                "filter_applied": True,
            }
        )
    return result


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
    route_count = int(route_context.get("route_count", 0))
    available_route_count = int(route_context.get("available_route_count", 0))
    compute_service_route_count = int(
        route_context.get("compute_service_route_count", 0)
    )
    network_service_route_count = int(
        route_context.get("network_service_route_count", 0)
    )
    network_queue_route_count = max(0, route_count - available_route_count)
    resource_role = "COMPUTE_NODE" if node is not None else "SATELLITE_ONLY"
    return {
        "satellite_id": satellite_id,
        "status": _str((node or satellite or {}).get("status")) or "ACTIVE",
        "resource_role": resource_role,
        "resource_role_label": _satellite_resource_role_label(resource_role),
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
        "primary_route_id": _str(route_context.get("primary_route_id")),
        "primary_flow_id": _str(route_context.get("primary_flow_id")),
        "route_count": route_count,
        "available_route_count": available_route_count,
        "network_queue_route_count": network_queue_route_count,
        "compute_service_route_count": compute_service_route_count,
        "network_service_route_count": network_service_route_count,
        "route_mix_label": _satellite_route_mix_label(
            compute_service_route_count,
            network_service_route_count,
            network_queue_route_count,
        ),
        "route_capacity_mbps": _first_float(kpi_slice, "route_capacity_mbps"),
        "route_demand_mbps": _first_float(kpi_slice, "route_demand_mbps"),
        "route_latency_avg_s": _first_float(kpi_slice, "route_latency_avg_s"),
        "route_delay_variation_proxy_s": _first_float(
            kpi_slice,
            "route_delay_variation_proxy_s",
        ),
        "route_loss_proxy_rate": _first_float(kpi_slice, "route_loss_proxy_rate"),
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
                    "primary_route_id": "",
                    "primary_flow_id": "",
                    "route_count": 0,
                    "available_route_count": 0,
                    "compute_service_route_count": 0,
                    "network_service_route_count": 0,
                },
            )
            if not entry["primary_route_id"]:
                entry["primary_route_id"] = _str(route.get("route_id"))
                entry["primary_flow_id"] = _str(route.get("flow_id"))
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


def _platform_type_label(platform_type: str) -> str:
    if platform_type == "GROUND_STATION":
        return "Ground station"
    if platform_type == "GROUND_USER_TERMINAL":
        return "Ground user terminal"
    return platform_type


def _request_state_label(request_state: str) -> str:
    if request_state == "IDLE":
        return "Idle"
    if request_state == "NETWORK_WAITING":
        return "Waiting for network route"
    if request_state == "COMPUTE_SERVICE_ACTIVE":
        return "Compute service active"
    if request_state == "COMPUTE_SERVICE_READY":
        return "Compute service route ready"
    if request_state == "NETWORK_SERVICE_READY":
        return "Network service route ready"
    return request_state


def _network_queue_reason(
    routes: Sequence[Mapping[str, Any]],
    available_routes: Sequence[Mapping[str, Any]],
    waiting_routes: Sequence[Mapping[str, Any]],
    selected_route: Mapping[str, Any] | None,
) -> str:
    if not routes:
        return "NO_BUSINESS_REQUEST"
    if not waiting_routes:
        return "NO_QUEUE"
    if available_routes:
        return "PARTIAL_ROUTE_WAITING"
    if selected_route is None:
        return "NO_SELECTED_ROUTE"
    path = _route_path(selected_route)
    if not path:
        return "NO_ROUTE_PATH"
    demand = _optional_float(selected_route.get("demand_capacity"))
    capacity = _optional_float(selected_route.get("capacity"))
    if demand is not None and capacity is not None and capacity < demand:
        return "ROUTE_CAPACITY_BELOW_DEMAND"
    return "ROUTE_UNAVAILABLE"


def _network_queue_reason_label(reason: str) -> str:
    if reason == "NO_BUSINESS_REQUEST":
        return "No current business request"
    if reason == "NO_QUEUE":
        return "No network queue"
    if reason == "PARTIAL_ROUTE_WAITING":
        return "Some requests are waiting"
    if reason == "NO_SELECTED_ROUTE":
        return "No selected route"
    if reason == "NO_ROUTE_PATH":
        return "No feasible path"
    if reason == "ROUTE_CAPACITY_BELOW_DEMAND":
        return "Route capacity below demand"
    if reason == "ROUTE_UNAVAILABLE":
        return "Route unavailable"
    return reason


def _route_explanation_item(
    route: Mapping[str, Any],
    service_lookup: Mapping[str, str],
) -> dict[str, object]:
    path = _route_path(route)
    source_id = path[0] if path else ""
    destination_id = path[-1] if path else ""
    user_id = _route_user_id(route) or ""
    reason = _route_bottleneck_reason(route)
    business_type = _route_business_type(route, service_lookup)
    next_hop = _route_primary_next_hop(path, user_id or source_id)
    capacity = _optional_float(route.get("capacity"))
    demand = _optional_float(route.get("demand_capacity"))
    available = bool(route.get("available"))
    return {
        "route_id": _str(route.get("route_id")),
        "flow_id": _str(route.get("flow_id")),
        "user_id": user_id,
        "source_id": source_id,
        "destination_id": destination_id,
        "selected_satellite_id": _route_first_satellite(route) or "",
        "primary_next_hop_id": next_hop,
        "next_hop_ids": tuple(path[1:]),
        "hop_count": max(0, len(path) - 1),
        "path_label": _route_path_label(path),
        "available": available,
        "capacity_mbps": capacity,
        "demand_mbps": demand,
        "latency_s": _optional_float(route.get("latency")),
        "loss_proxy_rate": _optional_float(route.get("loss_rate")),
        "route_pressure_proxy": _route_pressure_proxy_from_values(
            capacity,
            demand,
            _optional_float(route.get("loss_rate")),
            available,
        ),
        "business_type": business_type,
        "business_label": _route_business_label(route, service_lookup),
        "bottleneck_component": _route_bottleneck_component(reason),
        "bottleneck_reason": reason,
        "bottleneck_reason_label": _route_bottleneck_reason_label(reason),
        "explanation_label": _route_explanation_label(
            reason,
            available=available,
            capacity=capacity,
            demand=demand,
            next_hop=next_hop,
        ),
    }


def _detail_item_matches_query(item: Mapping[str, Any], query: str) -> bool:
    normalized_query = _normalized_filter_text(query)
    if not normalized_query:
        return True
    return normalized_query in " ".join(_filter_text_values(item)).lower()


def _route_explanation_matches_filter(
    item: Mapping[str, Any],
    *,
    query: str,
    availability: str,
    business_type: str,
    bottleneck_component: str,
) -> bool:
    if not _detail_item_matches_query(item, query):
        return False
    availability_filter = _normalized_filter_choice(availability, default="ALL")
    if availability_filter == "AVAILABLE" and not bool(item.get("available")):
        return False
    if availability_filter == "BLOCKED" and bool(item.get("available")):
        return False
    business_filter = _normalized_filter_choice(business_type, default="ALL")
    if business_filter != "ALL" and _str(item.get("business_type")).upper() != business_filter:
        return False
    bottleneck_filter = _normalized_filter_choice(
        bottleneck_component,
        default="ALL",
    )
    if (
        bottleneck_filter != "ALL"
        and _str(item.get("bottleneck_component")).upper() != bottleneck_filter
    ):
        return False
    return True


def _route_filter_is_active(
    *,
    query: str,
    availability: str,
    business_type: str,
    bottleneck_component: str,
) -> bool:
    return (
        bool(_normalized_filter_text(query))
        or _normalized_filter_choice(availability, default="ALL") != "ALL"
        or _normalized_filter_choice(business_type, default="ALL") != "ALL"
        or _normalized_filter_choice(bottleneck_component, default="ALL") != "ALL"
    )


def _normalized_filter_text(value: object) -> str:
    return " ".join(_str(value).strip().lower().split())


def _normalized_filter_choice(value: object, *, default: str) -> str:
    normalized = _str(value).strip().upper()
    return normalized or default


def _filter_text_values(value: object) -> tuple[str, ...]:
    if isinstance(value, Mapping):
        values: list[str] = []
        for key in sorted(value):
            values.extend(_filter_text_values(value[key]))
        return tuple(values)
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        values = []
        for item in value:
            values.extend(_filter_text_values(item))
        return tuple(values)
    text = _str(value).strip()
    return (text,) if text else ()


def _route_bottleneck_reason(route: Mapping[str, Any]) -> str:
    path = _route_path(route)
    if not path:
        return "NO_ROUTE_PATH"
    if _route_capacity_below_demand(route):
        return "ROUTE_CAPACITY_BELOW_DEMAND"
    if not bool(route.get("available")):
        return "ROUTE_UNAVAILABLE"
    loss_rate = _optional_float(route.get("loss_rate"))
    if loss_rate is not None and loss_rate > 0.0:
        return "ROUTE_LOSS_PROXY_POSITIVE"
    return "NO_BOTTLENECK"


def _route_bottleneck_component(reason: str) -> str:
    if reason == "NO_ROUTE_PATH":
        return "PATH"
    if reason == "ROUTE_CAPACITY_BELOW_DEMAND":
        return "CAPACITY"
    if reason == "ROUTE_UNAVAILABLE":
        return "AVAILABILITY"
    if reason == "ROUTE_LOSS_PROXY_POSITIVE":
        return "LOSS_PROXY"
    return "NONE"


def _route_bottleneck_reason_label(reason: str) -> str:
    labels = {
        "NO_ROUTE_PATH": "No feasible path",
        "ROUTE_CAPACITY_BELOW_DEMAND": "Route capacity below demand",
        "ROUTE_UNAVAILABLE": "Route unavailable",
        "ROUTE_LOSS_PROXY_POSITIVE": "Route loss proxy is positive",
        "NO_BOTTLENECK": "No route bottleneck",
    }
    return labels.get(reason, reason)


def _route_explanation_label(
    reason: str,
    *,
    available: bool,
    capacity: float | None,
    demand: float | None,
    next_hop: str,
) -> str:
    if reason == "ROUTE_CAPACITY_BELOW_DEMAND":
        return (
            f"capacity {capacity or 0.0:g} Mbps < demand {demand or 0.0:g} Mbps"
        )
    if reason == "ROUTE_UNAVAILABLE":
        return "route is unavailable in the current snapshot"
    if reason == "NO_ROUTE_PATH":
        return "route has no path"
    if reason == "ROUTE_LOSS_PROXY_POSITIVE":
        return "route has a positive flow-level loss proxy"
    if available and next_hop:
        return f"route ready via next hop {next_hop}"
    if available:
        return "route ready"
    return reason


def _route_primary_next_hop(path: Sequence[str], source_id: str) -> str:
    if source_id:
        next_hop = _route_next_hop_after_user(path, source_id)
        if next_hop:
            return next_hop
    return path[1] if len(path) > 1 else ""


def _route_capacity_below_demand(route: Mapping[str, Any]) -> bool:
    demand = _optional_float(route.get("demand_capacity"))
    capacity = _optional_float(route.get("capacity"))
    return demand is not None and capacity is not None and capacity < demand


def _route_pressure_proxy_from_values(
    capacity: float | None,
    demand: float | None,
    loss_rate: float | None,
    available: bool,
) -> float:
    if not available:
        return 1.0
    demand_pressure = 0.0
    if capacity is not None and demand is not None:
        demand_pressure = 1.0 if capacity <= 0.0 and demand > 0.0 else (
            max(0.0, demand / capacity) if capacity > 0.0 else 0.0
        )
    return min(1.0, max(demand_pressure, loss_rate or 0.0))


def _route_next_hop_after_user(path: Sequence[str], user_id: str) -> str:
    for index, node_id in enumerate(path):
        if node_id == user_id and index + 1 < len(path):
            return path[index + 1]
    return ""


def _route_path_label(path: Sequence[str]) -> str:
    return " -> ".join(path)


def _satellite_resource_role_label(resource_role: str) -> str:
    if resource_role == "COMPUTE_NODE":
        return "Satellite compute node"
    if resource_role == "SATELLITE_ONLY":
        return "Satellite platform"
    return resource_role


def _satellite_route_mix_label(
    compute_service_route_count: int,
    network_service_route_count: int,
    network_queue_route_count: int,
) -> str:
    return (
        f"compute={max(0, compute_service_route_count)}; "
        f"network={max(0, network_service_route_count)}; "
        f"queued={max(0, network_queue_route_count)}"
    )


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


def _route_explanation_sort_key(route: Mapping[str, Any]) -> tuple[int, float, tuple[object, ...], str]:
    return (
        0 if not bool(route.get("available")) else 1,
        -_route_pressure_proxy_from_values(
            _optional_float(route.get("capacity")),
            _optional_float(route.get("demand_capacity")),
            _optional_float(route.get("loss_rate")),
            bool(route.get("available")),
        ),
        _entity_sort_key(_route_user_id(route) or _str(route.get("flow_id"))),
        _str(route.get("route_id")),
    )


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


def _service_detail_lookup(
    history: Mapping[str, Any] | None,
) -> dict[str, Mapping[str, Any]]:
    lookup: dict[str, Mapping[str, Any]] = {}
    if history is None:
        return lookup
    for item in _records(history.get("items")):
        for key in ("input_flow_id", "output_flow_id"):
            flow_id = _str(item.get(key))
            if flow_id:
                lookup[flow_id] = item
    return lookup


def _service_label(item: Mapping[str, Any]) -> str:
    task_id = _str(item.get("task_id")) or "service"
    total_ms = _optional_float(item.get("total_latency_s"))
    state = "COMPLETE" if bool(item.get("complete")) else "RUNNING"
    if total_ms is None:
        return f"{task_id}/{state}"
    return f"{task_id}/{round(total_ms * 1000.0)}ms/{state}"


def _service_id(item: Mapping[str, Any]) -> str:
    return (
        _str(item.get("task_id"))
        or _str(item.get("input_flow_id"))
        or _str(item.get("output_flow_id"))
        or "service"
    )


def _service_request_id(item: Mapping[str, Any]) -> str:
    task_id = _str(item.get("task_id"))
    if task_id.endswith("-task"):
        return task_id[: -len("-task")]
    input_flow_id = _str(item.get("input_flow_id"))
    if input_flow_id.endswith("-input"):
        return input_flow_id[: -len("-input")]
    output_flow_id = _str(item.get("output_flow_id"))
    if output_flow_id.endswith("-output"):
        return output_flow_id[: -len("-output")]
    return _service_id(item)


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


def _optional_int(value: object) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
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
