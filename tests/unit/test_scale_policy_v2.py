from __future__ import annotations

import pytest

from leo_twin.services.scale_policy_v2 import (
    SCALE_POLICY_V2_ID,
    scale_policy_profile_for_satellite_count,
    scale_policy_v2_to_dict,
)


@pytest.mark.parametrize(
    ("satellite_count", "expected_profile", "expected_band"),
    (
        (72, "baseline_72", "SMALL_72"),
        (300, "medium_300", "MEDIUM_300"),
        (1200, "large_1200", "LARGE_1200"),
        (3000, "xl_3000", "XL_3000"),
        (6000, "xxl_6000", "XXL_6000"),
        (12000, "extreme_12000", "EXTREME_12000"),
    ),
)
def test_scale_policy_v2_selects_named_product_profiles(
    satellite_count: int,
    expected_profile: str,
    expected_band: str,
) -> None:
    profile = scale_policy_profile_for_satellite_count(satellite_count)

    assert profile.profile_id == expected_profile
    assert profile.scale_band == expected_band


def test_scale_policy_v2_exposes_deterministic_profile_matrix() -> None:
    first = scale_policy_v2_to_dict(satellite_count=3000, user_count=400)
    second = scale_policy_v2_to_dict(satellite_count=3000, user_count=400)

    assert first == second
    assert first["policy_id"] == SCALE_POLICY_V2_ID
    assert first["profile_targets"] == (72, 300, 1200, 3000, 6000, 12000)
    assert first["active_profile_id"] == "xl_3000"
    assert first["active_scale_band"] == "XL_3000"
    assert first["packet_level_simulation"] is False
    assert first["event_kernel_policy"] == "NO_EVENT_KERNEL_BEHAVIOR_CHANGE"
    active_profile = first["active_profile"]
    assert isinstance(active_profile, dict)
    assert active_profile["snapshot_lod_policy"] == (
        "AGGREGATE_FIRST_WITH_DETAIL_WINDOWS"
    )
    assert active_profile["detail_window_policy"] == (
        "BACKEND_CURSOR_DETAIL_REQUIRED"
    )
    assert active_profile["frontend_policy"] == (
        "VIRTUAL_TABLES_AND_SAMPLE_RENDERING"
    )
    active_fidelity = first["active_fidelity_summary"]
    assert isinstance(active_fidelity, dict)
    assert active_fidelity["orbit_update_mode"] == "BATCH"
    assert active_fidelity["metrics_mode"] == "AGGREGATED"
    assert active_fidelity["space_link_mode"] == "BOUNDED_CANDIDATE"


def test_scale_policy_v2_keeps_small_and_medium_modes_distinct() -> None:
    small = scale_policy_v2_to_dict(satellite_count=72, user_count=100)
    medium = scale_policy_v2_to_dict(satellite_count=300, user_count=100)

    assert small["active_profile_id"] == "baseline_72"
    assert medium["active_profile_id"] == "medium_300"
    small_fidelity = small["active_fidelity_summary"]
    medium_fidelity = medium["active_fidelity_summary"]
    assert isinstance(small_fidelity, dict)
    assert isinstance(medium_fidelity, dict)
    assert small_fidelity["orbit_update_mode"] == "PER_SATELLITE"
    assert small_fidelity["metrics_mode"] == "DETAILED"
    assert medium_fidelity["orbit_update_mode"] == "BATCH"
    assert medium_fidelity["metrics_mode"] == "DETAILED"
    assert medium_fidelity["space_link_mode"] == "DETAILED_SMALL_SCALE"


def test_scale_policy_v2_extreme_profile_is_not_a_full_detail_claim() -> None:
    summary = scale_policy_v2_to_dict(satellite_count=12000, user_count=1000)

    assert summary["active_profile_id"] == "extreme_12000"
    active_profile = summary["active_profile"]
    assert isinstance(active_profile, dict)
    assert active_profile["frontend_policy"] == "NO_FULL_SCENE_DETAIL_RENDERING"
    assert active_profile["runtime_guardrail_policy"] == "PRE_RUN_ACCEPTANCE_REQUIRED"
    assert "not a current product claim" in str(active_profile["limitation_note"])
    assert summary["forbidden_integrations"] == ("STK", "EXATA", "AFSIM", "DDS")


@pytest.mark.parametrize(
    ("satellite_count", "user_count", "error"),
    (
        (0, 10, ValueError),
        (72, -1, ValueError),
        (True, 10, TypeError),
    ),
)
def test_scale_policy_v2_rejects_invalid_counts(
    satellite_count: int,
    user_count: int,
    error: type[Exception],
) -> None:
    with pytest.raises(error):
        scale_policy_v2_to_dict(
            satellite_count=satellite_count,
            user_count=user_count,
        )
