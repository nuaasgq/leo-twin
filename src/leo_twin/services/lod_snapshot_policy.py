"""LOD snapshot policy v2 for scale-aware observation surfaces."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from leo_twin.services.scale_policy_v2 import scale_policy_v2_to_dict


LOD_SNAPSHOT_POLICY_V2_ID = "leo_twin.lod_snapshot_policy.v2"


@dataclass(frozen=True)
class LodSnapshotBudgets:
    """Bounded observation budgets for one scale profile."""

    profile_id: str
    satellite_window: int
    user_window: int
    route_window: int
    service_window: int
    compute_node_window: int
    top_k_limit: int
    sampled_history_points: int
    cursor_required: bool
    full_detail_allowed: bool


_BUDGETS_BY_PROFILE_ID: dict[str, LodSnapshotBudgets] = {
    "baseline_72": LodSnapshotBudgets(
        profile_id="baseline_72",
        satellite_window=100,
        user_window=250,
        route_window=120,
        service_window=120,
        compute_node_window=100,
        top_k_limit=20,
        sampled_history_points=600,
        cursor_required=False,
        full_detail_allowed=True,
    ),
    "medium_300": LodSnapshotBudgets(
        profile_id="medium_300",
        satellite_window=120,
        user_window=200,
        route_window=160,
        service_window=160,
        compute_node_window=120,
        top_k_limit=20,
        sampled_history_points=360,
        cursor_required=False,
        full_detail_allowed=False,
    ),
    "large_1200": LodSnapshotBudgets(
        profile_id="large_1200",
        satellite_window=120,
        user_window=120,
        route_window=96,
        service_window=120,
        compute_node_window=120,
        top_k_limit=16,
        sampled_history_points=240,
        cursor_required=True,
        full_detail_allowed=False,
    ),
    "xl_3000": LodSnapshotBudgets(
        profile_id="xl_3000",
        satellite_window=80,
        user_window=80,
        route_window=64,
        service_window=80,
        compute_node_window=80,
        top_k_limit=12,
        sampled_history_points=180,
        cursor_required=True,
        full_detail_allowed=False,
    ),
    "xxl_6000": LodSnapshotBudgets(
        profile_id="xxl_6000",
        satellite_window=50,
        user_window=50,
        route_window=48,
        service_window=50,
        compute_node_window=50,
        top_k_limit=10,
        sampled_history_points=120,
        cursor_required=True,
        full_detail_allowed=False,
    ),
    "extreme_12000": LodSnapshotBudgets(
        profile_id="extreme_12000",
        satellite_window=24,
        user_window=24,
        route_window=24,
        service_window=24,
        compute_node_window=24,
        top_k_limit=8,
        sampled_history_points=60,
        cursor_required=True,
        full_detail_allowed=False,
    ),
}


def lod_snapshot_policy_v2_to_dict(
    *,
    satellite_count: int,
    user_count: int,
    scale_policy: Mapping[str, Any] | None = None,
) -> dict[str, object]:
    """Return backend-owned LOD snapshot policy for one configured scale."""

    _require_positive_int(satellite_count, "satellite_count")
    _require_non_negative_int(user_count, "user_count")
    resolved_scale_policy = (
        dict(scale_policy)
        if scale_policy is not None
        else scale_policy_v2_to_dict(
            satellite_count=satellite_count,
            user_count=user_count,
        )
    )
    active_profile_id = str(resolved_scale_policy["active_profile_id"])
    active_scale_band = str(resolved_scale_policy["active_scale_band"])
    active_profile = resolved_scale_policy.get("active_profile")
    if not isinstance(active_profile, Mapping):
        raise TypeError("scale_policy.active_profile must be a mapping")
    budgets = _BUDGETS_BY_PROFILE_ID[active_profile_id]
    return {
        "version": "v2",
        "policy_id": LOD_SNAPSHOT_POLICY_V2_ID,
        "source_policy_id": resolved_scale_policy["policy_id"],
        "active_profile_id": active_profile_id,
        "active_scale_band": active_scale_band,
        "snapshot_lod_policy": active_profile["snapshot_lod_policy"],
        "detail_window_policy": active_profile["detail_window_policy"],
        "frontend_policy": active_profile["frontend_policy"],
        "configured_counts": {
            "satellite_count": satellite_count,
            "user_count": user_count,
        },
        "raw_count_policy": {
            "always_include_raw_counts": True,
            "fields": (
                "satellite_count",
                "ground_user_count",
                "link_count",
                "route_count",
                "service_count",
                "compute_node_count",
                "event_count",
            ),
            "source": "runtime snapshot collection lengths and runtime counters",
        },
        "detail_windows": _detail_windows(budgets),
        "top_k_summaries": _top_k_summaries(budgets),
        "sampled_histories": _sampled_histories(budgets),
        "cursor_required": budgets.cursor_required,
        "full_detail_allowed": budgets.full_detail_allowed,
        "hidden_detail_policy": _hidden_detail_policy(budgets),
        "determinism": {
            "stable_ordering": "backend sorts by stable identifiers before windowing",
            "sampling": "fixed-size tail samples with deterministic truncation",
            "frontend_inference": "frontend may paginate/render but must not invent LOD semantics",
        },
        "event_kernel_policy": "NO_EVENT_KERNEL_BEHAVIOR_CHANGE",
    }


def _detail_windows(budgets: LodSnapshotBudgets) -> tuple[dict[str, object], ...]:
    return (
        _detail_window(
            "satellites",
            budgets.satellite_window,
            "satellite_id",
            "satellite detail rows",
            budgets.cursor_required,
        ),
        _detail_window(
            "ground_users",
            budgets.user_window,
            "user_id",
            "ground user service rows",
            budgets.cursor_required,
        ),
        _detail_window(
            "routes",
            budgets.route_window,
            "route_id",
            "route and next-hop rows",
            budgets.cursor_required,
        ),
        _detail_window(
            "services",
            budgets.service_window,
            "service_id",
            "business request and service lifecycle rows",
            budgets.cursor_required,
        ),
        _detail_window(
            "compute_nodes",
            budgets.compute_node_window,
            "node_id",
            "satellite compute resource rows",
            budgets.cursor_required,
        ),
    )


def _detail_window(
    collection: str,
    max_rows: int,
    stable_key: str,
    purpose: str,
    cursor_required: bool,
) -> dict[str, object]:
    return {
        "collection": collection,
        "max_rows": max_rows,
        "stable_key": stable_key,
        "purpose": purpose,
        "cursor_required_for_hidden_rows": cursor_required,
        "raw_count_field": f"{collection}_count",
    }


def _top_k_summaries(budgets: LodSnapshotBudgets) -> tuple[dict[str, object], ...]:
    return tuple(
        {
            "summary": summary,
            "limit": budgets.top_k_limit,
            "ranking": ranking,
            "source": source,
        }
        for summary, ranking, source in (
            (
                "network_constraints",
                "highest congestion or blocking proxy first",
                "network KPI and route explanation summaries",
            ),
            (
                "compute_hotspots",
                "highest utilization first",
                "compute node resource summaries",
            ),
            (
                "active_services",
                "latest active or queued service first",
                "service lifecycle summaries",
            ),
            (
                "route_bottlenecks",
                "lowest available capacity or unavailable route first",
                "route explanation summaries",
            ),
        )
    )


def _sampled_histories(budgets: LodSnapshotBudgets) -> tuple[dict[str, object], ...]:
    return tuple(
        {
            "history": history,
            "max_points": budgets.sampled_history_points,
            "sampling_policy": "deterministic tail sample",
            "source": source,
        }
        for history, source in (
            ("network_kpi_timeseries", "runtime metrics stream"),
            ("service_latency_history", "service lifecycle observations"),
            ("satellite_resource_history", "satellite KPI slices"),
            ("selected_node_history", "selected detail surface"),
        )
    )


def _hidden_detail_policy(budgets: LodSnapshotBudgets) -> str:
    if budgets.full_detail_allowed:
        return "FULL_DETAIL_MAY_BE_INCLUDED_WHEN_COUNTS_FIT_WINDOWS"
    if budgets.cursor_required:
        return "HIDDEN_ROWS_REQUIRE_BACKEND_CURSOR_OR_EXPLICIT_DETAIL_REQUEST"
    return "HIDDEN_ROWS_REMAIN_WINDOWED_WITH_RAW_COUNTS_VISIBLE"


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
