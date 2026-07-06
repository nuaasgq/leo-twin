from __future__ import annotations

import pytest

from leo_twin.services.detail_pagination_contract import (
    DETAIL_ENDPOINT_MAX_LIMIT,
    LARGE_DETAIL_PAGINATION_CONTRACT_V2_ID,
    large_detail_pagination_contract_v2_to_dict,
)
from leo_twin.services.lod_snapshot_policy import lod_snapshot_policy_v2_to_dict
from leo_twin.services.scale_policy_v2 import scale_policy_v2_to_dict


def test_large_detail_pagination_contract_v2_derives_large_scale_cursors() -> None:
    contract = large_detail_pagination_contract_v2_to_dict(
        satellite_count=1200,
        user_count=400,
        compute_node_count=120,
        route_count_estimate=240,
        service_count_estimate=80,
    )

    assert contract["contract_id"] == LARGE_DETAIL_PAGINATION_CONTRACT_V2_ID
    assert contract["active_profile_id"] == "large_1200"
    assert contract["active_scale_band"] == "LARGE_1200"
    assert contract["source_policy_ids"] == {
        "scale_policy": "leo_twin.scale_policy.v2",
        "lod_snapshot_policy": "leo_twin.lod_snapshot_policy.v2",
    }
    assert contract["cursor_model"] == {
        "cursor_type": "zero_based_offset",
        "limit_type": "positive_int",
        "next_cursor_policy": "min(total_count, cursor + returned_item_count)",
        "has_more_policy": "next_cursor < total_count",
        "max_limit": DETAIL_ENDPOINT_MAX_LIMIT,
    }
    collections = _collections(contract)
    assert collections["ground_users"]["endpoint"] == "/runtime/details/users"
    assert collections["ground_users"]["recommended_limit"] == 120
    assert collections["ground_users"]["cursor_required"] is True
    assert collections["ground_users"]["hidden_count_estimate"] == 280
    assert collections["satellites"]["endpoint"] == "/runtime/details/satellites"
    assert collections["routes"]["endpoint"] == "/runtime/details/routes"
    assert collections["routes"]["recommended_limit"] == 96
    assert collections["routes"]["hidden_count_estimate"] == 144
    assert collections["services"]["endpoint"] == "/runtime/details/services"
    assert collections["service_traces"]["endpoint"] == (
        "/runtime/details/service-traces"
    )
    assert collections["service_traces"]["recommended_limit"] == (
        collections["services"]["recommended_limit"]
    )
    assert collections["service_traces"]["query_parameters"] == (
        "cursor",
        "limit",
        "query",
        "terminal_state",
        "compute_node_id",
    )
    assert collections["compute_nodes"]["endpoint"] == (
        "/runtime/details/compute-nodes"
    )
    assert collections["compute_nodes"]["hidden_count_estimate"] == 0
    assert contract["combined_node_endpoint"] == {
        "kind": "nodes",
        "endpoint": "/runtime/details/nodes",
        "summary_type": "RuntimeNodeDetailPageV1",
        "composition": ("ground_users", "satellites"),
        "purpose": "combined user and satellite node detail cards",
        "stable_ordering": (
            "all users first, then satellites; each group sorted by stable id"
        ),
    }
    assert contract["event_kernel_policy"] == "NO_EVENT_KERNEL_BEHAVIOR_CHANGE"


def test_large_detail_pagination_contract_v2_reuses_supplied_policies() -> None:
    scale_policy = scale_policy_v2_to_dict(satellite_count=3000, user_count=500)
    lod_policy = lod_snapshot_policy_v2_to_dict(
        satellite_count=3000,
        user_count=500,
        scale_policy=scale_policy,
    )

    first = large_detail_pagination_contract_v2_to_dict(
        satellite_count=3000,
        user_count=500,
        compute_node_count=300,
        route_count_estimate=700,
        service_count_estimate=350,
        scale_policy=scale_policy,
        lod_snapshot_policy=lod_policy,
    )
    second = large_detail_pagination_contract_v2_to_dict(
        satellite_count=3000,
        user_count=500,
        compute_node_count=300,
        route_count_estimate=700,
        service_count_estimate=350,
        scale_policy=scale_policy,
        lod_snapshot_policy=lod_policy,
    )

    assert first == second
    assert first["active_profile_id"] == "xl_3000"
    collections = _collections(first)
    assert collections["satellites"]["recommended_limit"] == 80
    assert collections["routes"]["recommended_limit"] == 64
    assert collections["services"]["cursor_required_for_hidden_rows"] is True
    assert collections["service_traces"]["hidden_count_estimate"] == (
        collections["services"]["hidden_count_estimate"]
    )
    assert collections["compute_nodes"]["hidden_count_estimate"] == 220


@pytest.mark.parametrize(
    ("kwargs", "error"),
    (
        (
            {
                "satellite_count": 0,
                "user_count": 1,
                "compute_node_count": 1,
            },
            ValueError,
        ),
        (
            {
                "satellite_count": 1,
                "user_count": -1,
                "compute_node_count": 1,
            },
            ValueError,
        ),
        (
            {
                "satellite_count": 1,
                "user_count": 1,
                "compute_node_count": False,
            },
            TypeError,
        ),
        (
            {
                "satellite_count": 1,
                "user_count": 1,
                "compute_node_count": 1,
                "route_count_estimate": -1,
            },
            ValueError,
        ),
    ),
)
def test_large_detail_pagination_contract_v2_rejects_invalid_counts(
    kwargs: dict[str, object],
    error: type[Exception],
) -> None:
    with pytest.raises(error):
        large_detail_pagination_contract_v2_to_dict(**kwargs)


def _collections(contract: dict[str, object]) -> dict[str, dict[str, object]]:
    collections = contract["collections"]
    assert isinstance(collections, tuple)
    result: dict[str, dict[str, object]] = {}
    for collection in collections:
        assert isinstance(collection, dict)
        result[str(collection["collection"])] = collection
    return result
