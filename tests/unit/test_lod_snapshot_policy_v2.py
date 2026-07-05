from __future__ import annotations

import pytest

from leo_twin.services.lod_snapshot_policy import (
    LOD_SNAPSHOT_POLICY_V2_ID,
    lod_snapshot_policy_v2_to_dict,
)
from leo_twin.services.scale_policy_v2 import scale_policy_v2_to_dict


def test_lod_snapshot_policy_v2_uses_small_scale_full_detail_windows() -> None:
    policy = lod_snapshot_policy_v2_to_dict(satellite_count=72, user_count=100)

    assert policy["policy_id"] == LOD_SNAPSHOT_POLICY_V2_ID
    assert policy["source_policy_id"] == "leo_twin.scale_policy.v2"
    assert policy["active_profile_id"] == "baseline_72"
    assert policy["active_scale_band"] == "SMALL_72"
    assert policy["snapshot_lod_policy"] == "FULL_DETAIL_SNAPSHOT"
    assert policy["cursor_required"] is False
    assert policy["full_detail_allowed"] is True
    assert policy["hidden_detail_policy"] == (
        "FULL_DETAIL_MAY_BE_INCLUDED_WHEN_COUNTS_FIT_WINDOWS"
    )
    satellite_window = _window(policy, "satellites")
    assert satellite_window["max_rows"] == 100
    assert satellite_window["cursor_required_for_hidden_rows"] is False


def test_lod_snapshot_policy_v2_bounds_large_scale_detail_windows() -> None:
    policy = lod_snapshot_policy_v2_to_dict(satellite_count=1200, user_count=400)

    assert policy["active_profile_id"] == "large_1200"
    assert policy["active_scale_band"] == "LARGE_1200"
    assert policy["snapshot_lod_policy"] == "TOP_K_AND_WINDOWED_DETAIL"
    assert policy["detail_window_policy"] == "CURSOR_OR_WINDOWED_DETAIL_REQUIRED"
    assert policy["cursor_required"] is True
    assert policy["full_detail_allowed"] is False
    assert policy["hidden_detail_policy"] == (
        "HIDDEN_ROWS_REQUIRE_BACKEND_CURSOR_OR_EXPLICIT_DETAIL_REQUEST"
    )
    assert _window(policy, "satellites") == {
        "collection": "satellites",
        "max_rows": 120,
        "stable_key": "satellite_id",
        "purpose": "satellite detail rows",
        "cursor_required_for_hidden_rows": True,
        "raw_count_field": "satellites_count",
    }
    assert _window(policy, "routes")["max_rows"] == 96
    assert {item["summary"]: item["limit"] for item in policy["top_k_summaries"]} == {
        "network_constraints": 16,
        "compute_hotspots": 16,
        "active_services": 16,
        "route_bottlenecks": 16,
    }
    assert {
        item["history"]: item["max_points"] for item in policy["sampled_histories"]
    } == {
        "network_kpi_timeseries": 240,
        "service_latency_history": 240,
        "satellite_resource_history": 240,
        "selected_node_history": 240,
    }
    raw_count_policy = policy["raw_count_policy"]
    assert isinstance(raw_count_policy, dict)
    assert raw_count_policy["always_include_raw_counts"] is True
    assert "event_count" in raw_count_policy["fields"]


def test_lod_snapshot_policy_v2_extreme_scale_is_summary_first() -> None:
    policy = lod_snapshot_policy_v2_to_dict(satellite_count=12000, user_count=1000)

    assert policy["active_profile_id"] == "extreme_12000"
    assert policy["snapshot_lod_policy"] == "SUMMARY_AND_EXPORT_FIRST"
    assert policy["detail_window_policy"] == "OFFLINE_OR_CURSOR_DETAIL_ONLY"
    assert _window(policy, "satellites")["max_rows"] == 24
    assert _window(policy, "ground_users")["max_rows"] == 24
    assert _window(policy, "services")["max_rows"] == 24
    assert policy["top_k_summaries"][0]["limit"] == 8
    assert policy["sampled_histories"][0]["max_points"] == 60
    assert policy["determinism"] == {
        "stable_ordering": "backend sorts by stable identifiers before windowing",
        "sampling": "fixed-size tail samples with deterministic truncation",
        "frontend_inference": (
            "frontend may paginate/render but must not invent LOD semantics"
        ),
    }
    assert policy["event_kernel_policy"] == "NO_EVENT_KERNEL_BEHAVIOR_CHANGE"


def test_lod_snapshot_policy_v2_reuses_supplied_scale_policy() -> None:
    scale_policy = scale_policy_v2_to_dict(satellite_count=3000, user_count=500)

    first = lod_snapshot_policy_v2_to_dict(
        satellite_count=3000,
        user_count=500,
        scale_policy=scale_policy,
    )
    second = lod_snapshot_policy_v2_to_dict(
        satellite_count=3000,
        user_count=500,
        scale_policy=scale_policy,
    )

    assert first == second
    assert first["active_profile_id"] == "xl_3000"
    assert _window(first, "satellites")["max_rows"] == 80
    assert first["top_k_summaries"][0]["limit"] == 12
    assert first["sampled_histories"][0]["max_points"] == 180


@pytest.mark.parametrize(
    ("satellite_count", "user_count", "error"),
    (
        (0, 10, ValueError),
        (72, -1, ValueError),
        (False, 10, TypeError),
    ),
)
def test_lod_snapshot_policy_v2_rejects_invalid_counts(
    satellite_count: int,
    user_count: int,
    error: type[Exception],
) -> None:
    with pytest.raises(error):
        lod_snapshot_policy_v2_to_dict(
            satellite_count=satellite_count,
            user_count=user_count,
        )


def _window(policy: dict[str, object], collection: str) -> dict[str, object]:
    windows = policy["detail_windows"]
    assert isinstance(windows, tuple)
    for window in windows:
        assert isinstance(window, dict)
        if window["collection"] == collection:
            return window
    raise AssertionError(f"missing window {collection}")
