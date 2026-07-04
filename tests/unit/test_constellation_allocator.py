from __future__ import annotations

import pytest

from leo_twin.models.orbit import AutoPlaneAllocator, ConstellationProfile


@pytest.mark.parametrize(
    ("satellite_count", "plane_count", "satellites_per_plane"),
    (
        (72, 12, 6),
        (300, 30, 10),
        (1584, 72, 22),
    ),
)
def test_starlink_shell_1_like_auto_allocation_is_deterministic(
    satellite_count: int,
    plane_count: int,
    satellites_per_plane: int,
) -> None:
    first = AutoPlaneAllocator.allocate(
        satellite_count=satellite_count,
        profile=ConstellationProfile.STARLINK_SHELL_1_LIKE,
    )
    second = AutoPlaneAllocator.allocate(
        satellite_count=satellite_count,
        profile=ConstellationProfile.STARLINK_SHELL_1_LIKE,
    )

    assert first == second
    assert first.plane_count == plane_count
    assert first.satellites_per_plane == satellites_per_plane
    assert first.total_slots == satellite_count
    assert first.plane_count_explicit is False
    assert "not exact Starlink fidelity" in first.model_note


def test_explicit_plane_count_overrides_auto_profile() -> None:
    allocation = AutoPlaneAllocator.allocate(
        satellite_count=300,
        plane_count=15,
        profile="STARLINK_SHELL_1_LIKE",
    )

    assert allocation.profile == ConstellationProfile.STARLINK_SHELL_1_LIKE
    assert allocation.plane_count == 15
    assert allocation.satellites_per_plane == 20
    assert allocation.plane_count_explicit is True
    assert allocation.plane_index(16) == 1
    assert allocation.slot_index(16) == 1


def test_custom_walker_uses_square_like_divisor_when_auto_allocated() -> None:
    allocation = AutoPlaneAllocator.allocate(satellite_count=72)

    assert allocation.profile == ConstellationProfile.CUSTOM_WALKER
    assert allocation.plane_count == 8
    assert allocation.satellites_per_plane == 9
    assert allocation.to_summary()["profile"] == "CUSTOM_WALKER"
