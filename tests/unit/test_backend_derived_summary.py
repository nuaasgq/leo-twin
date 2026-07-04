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
        "orbital_period_minutes": pytest.approx(95.502118),
        "orbital_period_model_note": (
            "Simplified circular-orbit period estimate; no SGP4 or external ephemeris."
        ),
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
        "cpu_gflops_fp64_per_node": 0.0,
        "gpu_tflops_fp32_per_node": 0.0,
        "gpu_tflops_fp16_per_node": 0.0,
        "npu_tops_int8_per_node": 0.0,
        "memory_gb_per_node": 0.0,
        "storage_gb_per_node": 0.0,
        "total_cpu_gflops_fp32": 3000.0,
        "total_cpu_gflops_fp64": 0.0,
        "total_gpu_tflops_fp32": 0.0,
        "total_gpu_tflops_fp16": 0.0,
        "total_npu_tops_int8": 0.0,
        "total_memory_gb": 0.0,
        "total_storage_gb": 0.0,
        "capacity_unit": "GFLOPS FP32",
        "compatibility_note": "Legacy scalar capacity maps to cpu_gflops_fp32.",
    }
    assert first["coverage_beam_summary"] == {
        "coverage_model": "DETERMINISTIC_GEOMETRIC_FOOTPRINT",
        "selected_satellite_detail_mode": "SELECTED_SATELLITE_ONLY",
        "beam_pattern": "CENTER_PLUS_HEX_RING_VISUAL_APPROXIMATION",
        "default_beam_count": 7,
        "beam_radius_m": 160_000.0,
        "beam_length_m": 600_000.0,
        "global_beam_render_limit": 1,
        "model_note": (
            "Selected-satellite beam cells are deterministic visual footprints; "
            "no RF propagation or antenna-pattern simulation is performed."
        ),
    }
    assert any(
        "not exact Starlink fidelity" in assumption
        for assumption in first["model_assumptions"]
    )
    assert any(
        "Coverage beams are bounded geometric visualization footprints" in assumption
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
    assert first["orbital_period_minutes"] == pytest.approx(95.502118)
    assert first["inclination_deg"] == 53.0
    assert first["phase_policy"] == "DETERMINISTIC_PLANE_SLOT_PHASE"


def test_compute_resource_summary_uses_configured_vector_lanes() -> None:
    allocation = AutoPlaneAllocator.allocate(satellite_count=12, plane_count=3)

    summary = build_backend_derived_summary(
        constellation=allocation,
        satellite_count=12,
        user_count=20,
        compute_node_count=4,
        compute_capacity=40.0,
        flow_count=10,
        demand_capacity=25.0,
        task_compute_demand=20.0,
        task_data_size=2.0,
        application_protocol="TASK_OFFLOAD_FLOW",
        compute_cpu_gflops_fp64=8.0,
        compute_gpu_tflops_fp32=2.5,
        compute_gpu_tflops_fp16=5.0,
        compute_npu_tops_int8=12.0,
        compute_memory_gb=32.0,
        compute_storage_gb=512.0,
    )["compute_resource_summary"]

    assert summary["cpu_gflops_fp32_per_node"] == 40.0
    assert summary["cpu_gflops_fp64_per_node"] == 8.0
    assert summary["gpu_tflops_fp32_per_node"] == 2.5
    assert summary["gpu_tflops_fp16_per_node"] == 5.0
    assert summary["npu_tops_int8_per_node"] == 12.0
    assert summary["memory_gb_per_node"] == 32.0
    assert summary["storage_gb_per_node"] == 512.0
    assert summary["total_cpu_gflops_fp32"] == 160.0
    assert summary["total_cpu_gflops_fp64"] == 32.0
    assert summary["total_gpu_tflops_fp32"] == 10.0
    assert summary["total_gpu_tflops_fp16"] == 20.0
    assert summary["total_npu_tops_int8"] == 48.0
    assert summary["total_memory_gb"] == 128.0
    assert summary["total_storage_gb"] == 2048.0


def test_traffic_summary_uses_explicit_traffic_model_fields() -> None:
    allocation = AutoPlaneAllocator.allocate(satellite_count=12, plane_count=3)

    summary = build_backend_derived_summary(
        constellation=allocation,
        satellite_count=12,
        user_count=20,
        compute_node_count=4,
        compute_capacity=40.0,
        flow_count=10,
        demand_capacity=25.0,
        task_compute_demand=20.0,
        task_data_size=2.0,
        application_protocol="TASK_OFFLOAD_FLOW",
        traffic_class="BULK_DOWNLINK",
        traffic_destination_type="GROUND_ENDPOINT",
        traffic_output_data_size=4.5,
    )["traffic_demand_summary"]

    assert summary["traffic_class"] == "BULK_DOWNLINK"
    assert summary["destination_type"] == "GROUND_ENDPOINT"
    assert summary["output_data_size_mb"] == 4.5
    assert summary["input_data_size_mb"] == 2.0
    assert summary["demand_capacity_mbps"] == 25.0


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
