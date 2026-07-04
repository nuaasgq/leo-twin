from __future__ import annotations

import pytest

from leo_twin.models.orbit import AutoPlaneAllocator, ConstellationProfile
from leo_twin.services.derived_summary import build_backend_derived_summary
from leo_twin.services.scale_fidelity import (
    ScaleFidelityConfig,
    build_scale_fidelity_summary,
)


def test_backend_derived_summary_is_deterministic_and_frontend_ready() -> None:
    allocation = AutoPlaneAllocator.allocate(
        satellite_count=300,
        profile=ConstellationProfile.STARLINK_SHELL_1_LIKE,
    )

    first = build_backend_derived_summary(
        constellation=allocation,
        satellite_count=300,
        user_count=1000,
        compute_node_count=300,
        compute_capacity=10.0,
        flow_count=1200,
        demand_capacity=25.0,
        task_compute_demand=20.0,
        task_data_size=2.0,
        application_protocol="TASK_OFFLOAD_FLOW",
        arrival_interval_seconds=60,
        orbit_altitude_m=550_000.0,
        orbit_inclination_deg=53.0,
        phase_policy="TEST_PHASE_POLICY",
    )
    second = build_backend_derived_summary(
        constellation=allocation,
        satellite_count=300,
        user_count=1000,
        compute_node_count=300,
        compute_capacity=10.0,
        flow_count=1200,
        demand_capacity=25.0,
        task_compute_demand=20.0,
        task_data_size=2.0,
        application_protocol="TASK_OFFLOAD_FLOW",
        arrival_interval_seconds=60,
        orbit_altitude_m=550_000.0,
        orbit_inclination_deg=53.0,
        phase_policy="TEST_PHASE_POLICY",
    )

    assert first == second
    assert first["derived_constellation_summary"] == {
        "profile": "STARLINK_SHELL_1_LIKE",
        "satellite_count": 300,
        "plane_count": 30,
        "satellites_per_plane": 10,
        "satellites_per_plane_distribution": [10] * 30,
        "total_slots": 300,
        "plane_count_explicit": False,
        "model_note": (
            "Approximate Starlink Shell 1-like plane allocation; "
            "not exact Starlink fidelity."
        ),
        "raan_spacing_deg": 12.0,
        "mean_anomaly_spacing_deg": 36.0,
        "phase_policy": "TEST_PHASE_POLICY",
        "altitude_m": 550_000.0,
        "inclination_deg": 53.0,
    }
    assert first["traffic_demand_summary"] == {
        "traffic_class": "COMPUTE_SERVICE",
        "destination_type": "COMPUTE_NODE",
        "generated_flow_count": 1200,
        "arrival_model": "DETERMINISTIC_INTERVAL",
        "input_data_size_mb": 2.0,
        "output_data_size_mb": 0.0,
        "priority": 0,
        "demand_capacity_mbps": 25.0,
        "task_compute_demand": 20.0,
        "arrival_interval_seconds": 60.0,
    }
    assert first["compute_resource_summary"] == {
        "resource_model": "ComputeResourceVector",
        "node_role": "SATELLITE_HOSTED_COMPUTE",
        "compute_node_count": 300,
        "legacy_capacity_per_node": 10.0,
        "cpu_gflops_fp32_per_node": 10.0,
        "total_cpu_gflops_fp32": 3000.0,
        "capacity_unit": "GFLOPS FP32",
        "compatibility_note": "Legacy scalar capacity maps to cpu_gflops_fp32.",
    }
    assert any(
        "not exact Starlink fidelity" in assumption
        for assumption in first["model_assumptions"]
    )


@pytest.mark.parametrize(
    ("satellite_count", "plane_count", "profile", "expected_plane_count"),
    (
        (72, 12, ConstellationProfile.CUSTOM_WALKER, 12),
        (1200, 12, ConstellationProfile.CUSTOM_WALKER, 12),
        (1584, None, ConstellationProfile.STARLINK_SHELL_1_LIKE, 72),
    ),
)
def test_constellation_summary_is_deterministic_for_product_scales(
    satellite_count: int,
    plane_count: int | None,
    profile: ConstellationProfile,
    expected_plane_count: int,
) -> None:
    allocation = AutoPlaneAllocator.allocate(
        satellite_count=satellite_count,
        plane_count=plane_count,
        profile=profile,
    )

    first = build_backend_derived_summary(
        constellation=allocation,
        satellite_count=satellite_count,
        user_count=20,
        compute_node_count=min(10, satellite_count),
        compute_capacity=10.0,
        flow_count=10,
        demand_capacity=25.0,
        task_compute_demand=20.0,
        task_data_size=2.0,
        application_protocol="TASK_OFFLOAD_FLOW",
        orbit_altitude_m=550_000.0,
        orbit_inclination_deg=53.0,
    )["derived_constellation_summary"]
    second = build_backend_derived_summary(
        constellation=allocation,
        satellite_count=satellite_count,
        user_count=20,
        compute_node_count=min(10, satellite_count),
        compute_capacity=10.0,
        flow_count=10,
        demand_capacity=25.0,
        task_compute_demand=20.0,
        task_data_size=2.0,
        application_protocol="TASK_OFFLOAD_FLOW",
        orbit_altitude_m=550_000.0,
        orbit_inclination_deg=53.0,
    )["derived_constellation_summary"]

    assert first == second
    assert first["satellite_count"] == satellite_count
    assert first["plane_count"] == expected_plane_count
    assert sum(first["satellites_per_plane_distribution"]) == satellite_count
    assert len(first["satellites_per_plane_distribution"]) == expected_plane_count
    assert first["raan_spacing_deg"] == pytest.approx(360.0 / expected_plane_count)
    assert first["altitude_m"] == 550_000.0
    assert first["inclination_deg"] == 53.0
    assert first["phase_policy"] == "DETERMINISTIC_PLANE_SLOT_PHASE"


def test_scale_fidelity_summary_reports_large_scale_degradation() -> None:
    summary = build_scale_fidelity_summary(
        ScaleFidelityConfig(
            satellite_count=1200,
            user_count=20,
            space_link_enabled=True,
        )
    )

    assert summary == {
        "satellite_count": 1200,
        "user_count": 20,
        "orbit_update_mode": "BATCH",
        "metrics_mode": "AGGREGATED",
        "space_link_mode": "BOUNDED_CANDIDATE",
        "detailed_space_link_enabled": False,
        "space_link_candidate_policy": (
            "SAME_PLANE_AND_ADJACENT_PLANE_BOUNDED_CANDIDATES"
        ),
        "max_space_link_candidates_per_satellite": 4,
        "batch_space_link_update_limit": 999,
        "scale_limit_reason": (
            "orbit updates are batched; metrics are aggregated; "
            "detailed all-pairs space-space link updates are disabled because "
            "satellite_count=1200 exceeds batch_space_link_update_limit=999; "
            "bounded candidate updates are enabled with "
            "max_space_link_candidates_per_satellite=4"
        ),
        "current_scale_mode": "LARGE_SCALE_AGGREGATED",
        "fidelity_warnings": (
            "Orbit updates are batched to avoid per-satellite event flood.",
            "Metrics are aggregated for large-scale responsiveness.",
            "Space-space links use bounded candidate updates capped at "
            "4 candidates per satellite.",
        ),
    }
