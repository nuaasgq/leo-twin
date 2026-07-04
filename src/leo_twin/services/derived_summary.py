"""Backend-derived semantic summaries for frontend explanation surfaces."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from leo_twin.models.compute import ComputeResourceVector
from leo_twin.models.orbit import ConstellationAllocation
from leo_twin.models.traffic import TrafficClass, TrafficDestinationType


BackendDerivedSummary = dict[str, object]
_EARTH_RADIUS_KM = 6371.0
_EARTH_MU_KM3_S2 = 398600.4418


def build_backend_derived_summary(
    *,
    constellation: ConstellationAllocation | Mapping[str, object],
    satellite_count: int,
    user_count: int,
    compute_node_count: int,
    compute_capacity: float,
    flow_count: int,
    demand_capacity: float,
    task_compute_demand: float,
    task_data_size: float,
    application_protocol: str,
    traffic_class: TrafficClass | str | None = None,
    traffic_destination_type: TrafficDestinationType | str | None = None,
    traffic_output_data_size: float = 0.0,
    compute_cpu_gflops_fp64: float = 0.0,
    compute_gpu_tflops_fp32: float = 0.0,
    compute_gpu_tflops_fp16: float = 0.0,
    compute_npu_tops_int8: float = 0.0,
    compute_memory_gb: float = 0.0,
    compute_storage_gb: float = 0.0,
    arrival_interval_seconds: int | float | None = None,
    orbit_altitude_m: float | None = None,
    orbit_inclination_deg: float | None = None,
    beam_count: int = 7,
    beam_radius_m: float = 160_000.0,
    beam_length_m: float = 600_000.0,
    phase_policy: str = "DETERMINISTIC_PLANE_SLOT_PHASE",
) -> BackendDerivedSummary:
    """Build deterministic backend-owned explanations for frontend display."""

    constellation_summary = _constellation_summary(
        constellation,
        orbit_altitude_m=orbit_altitude_m,
        orbit_inclination_deg=orbit_inclination_deg,
        phase_policy=phase_policy,
    )
    selected_traffic_class = _selected_traffic_class(
        application_protocol,
        traffic_class,
    )
    selected_destination_type = _selected_destination_type(
        selected_traffic_class,
        traffic_destination_type,
    )
    compute_vector = ComputeResourceVector(
        cpu_gflops_fp32=compute_capacity,
        cpu_gflops_fp64=compute_cpu_gflops_fp64,
        gpu_tflops_fp32=compute_gpu_tflops_fp32,
        gpu_tflops_fp16=compute_gpu_tflops_fp16,
        npu_tops_int8=compute_npu_tops_int8,
        memory_gb=compute_memory_gb,
        storage_gb=compute_storage_gb,
    )
    total_cpu_gflops_fp32 = compute_vector.cpu_gflops_fp32 * compute_node_count
    traffic_summary: dict[str, object] = {
        "traffic_class": selected_traffic_class.value,
        "destination_type": selected_destination_type.value,
        "generated_flow_count": flow_count,
        "arrival_model": "DETERMINISTIC_INTERVAL",
        "input_data_size_mb": task_data_size,
        "output_data_size_mb": float(traffic_output_data_size),
        "priority": 0,
        "demand_capacity_mbps": demand_capacity,
        "task_compute_demand": task_compute_demand,
    }
    if arrival_interval_seconds is not None:
        traffic_summary["arrival_interval_seconds"] = float(arrival_interval_seconds)

    compute_summary = {
        "resource_model": "ComputeResourceVector",
        "node_role": "SATELLITE_HOSTED_COMPUTE",
        "compute_node_count": compute_node_count,
        "legacy_capacity_per_node": compute_capacity,
        "cpu_gflops_fp32_per_node": compute_vector.cpu_gflops_fp32,
        "cpu_gflops_fp64_per_node": compute_vector.cpu_gflops_fp64,
        "gpu_tflops_fp32_per_node": compute_vector.gpu_tflops_fp32,
        "gpu_tflops_fp16_per_node": compute_vector.gpu_tflops_fp16,
        "npu_tops_int8_per_node": compute_vector.npu_tops_int8,
        "memory_gb_per_node": compute_vector.memory_gb,
        "storage_gb_per_node": compute_vector.storage_gb,
        "total_cpu_gflops_fp32": total_cpu_gflops_fp32,
        "total_cpu_gflops_fp64": compute_vector.cpu_gflops_fp64 * compute_node_count,
        "total_gpu_tflops_fp32": compute_vector.gpu_tflops_fp32 * compute_node_count,
        "total_gpu_tflops_fp16": compute_vector.gpu_tflops_fp16 * compute_node_count,
        "total_npu_tops_int8": compute_vector.npu_tops_int8 * compute_node_count,
        "total_memory_gb": compute_vector.memory_gb * compute_node_count,
        "total_storage_gb": compute_vector.storage_gb * compute_node_count,
        "capacity_unit": "GFLOPS FP32",
        "compatibility_note": "Legacy scalar capacity maps to cpu_gflops_fp32.",
    }
    coverage_summary = {
        "coverage_model": "DETERMINISTIC_GEOMETRIC_FOOTPRINT",
        "selected_satellite_detail_mode": "SELECTED_SATELLITE_ONLY",
        "beam_pattern": "CENTER_PLUS_HEX_RING_VISUAL_APPROXIMATION",
        "default_beam_count": int(beam_count),
        "beam_radius_m": float(beam_radius_m),
        "beam_length_m": float(beam_length_m),
        "global_beam_render_limit": 1,
        "model_note": (
            "Selected-satellite beam cells are deterministic visual footprints; "
            "no RF propagation or antenna-pattern simulation is performed."
        ),
    }

    return {
        "derived_constellation_summary": constellation_summary,
        "traffic_demand_summary": traffic_summary,
        "compute_resource_summary": compute_summary,
        "coverage_beam_summary": coverage_summary,
        "model_assumptions": _model_assumptions(
            constellation_summary,
            satellite_count=satellite_count,
            user_count=user_count,
        ),
    }


def _constellation_summary(
    constellation: ConstellationAllocation | Mapping[str, object],
    *,
    orbit_altitude_m: float | None = None,
    orbit_inclination_deg: float | None = None,
    phase_policy: str,
) -> dict[str, object]:
    if isinstance(constellation, ConstellationAllocation):
        summary: dict[str, object] = dict(constellation.to_summary())
        _add_constellation_geometry(
            summary,
            orbit_altitude_m=orbit_altitude_m,
            orbit_inclination_deg=orbit_inclination_deg,
            phase_policy=phase_policy,
        )
        return summary
    if not isinstance(constellation, Mapping):
        raise TypeError("constellation must be ConstellationAllocation or mapping")
    summary = dict(constellation)
    _add_constellation_geometry(
        summary,
        orbit_altitude_m=orbit_altitude_m,
        orbit_inclination_deg=orbit_inclination_deg,
        phase_policy=phase_policy,
    )
    return summary


def _add_constellation_geometry(
    summary: dict[str, object],
    *,
    orbit_altitude_m: float | None,
    orbit_inclination_deg: float | None,
    phase_policy: str,
) -> None:
    satellite_count = int(summary["satellite_count"])
    plane_count = int(summary["plane_count"])
    satellites_per_plane = int(summary["satellites_per_plane"])
    summary["satellites_per_plane_distribution"] = _plane_distribution(
        satellite_count,
        plane_count,
    )
    summary["raan_spacing_deg"] = 360.0 / float(plane_count)
    summary["mean_anomaly_spacing_deg"] = 360.0 / float(satellites_per_plane)
    summary["phase_policy"] = str(phase_policy)
    if orbit_altitude_m is not None:
        summary["altitude_m"] = float(orbit_altitude_m)
        summary["orbital_period_minutes"] = _circular_orbital_period_minutes(
            orbit_altitude_m,
        )
        summary["orbital_period_model_note"] = (
            "Simplified circular-orbit period estimate; no SGP4 or external ephemeris."
        )
    if orbit_inclination_deg is not None:
        summary["inclination_deg"] = float(orbit_inclination_deg)


def _circular_orbital_period_minutes(altitude_m: float) -> float:
    altitude_km = float(altitude_m) / 1000.0
    semi_major_axis_km = _EARTH_RADIUS_KM + altitude_km
    return float(
        2.0
        * 3.141592653589793
        * (semi_major_axis_km**3 / _EARTH_MU_KM3_S2) ** 0.5
        / 60.0
    )


def _plane_distribution(satellite_count: int, plane_count: int) -> list[int]:
    base = satellite_count // plane_count
    remainder = satellite_count % plane_count
    return [
        base + (1 if plane_index < remainder else 0)
        for plane_index in range(plane_count)
    ]


def _traffic_class(application_protocol: str) -> TrafficClass:
    normalized = str(application_protocol).upper()
    if normalized == "TELEMETRY":
        return TrafficClass.TELEMETRY
    if normalized in {"TASK_OFFLOAD_FLOW", "COMPUTE_SERVICE"}:
        return TrafficClass.COMPUTE_SERVICE
    if normalized in {"BULK_DOWNLINK", "FILE_TRANSFER"}:
        return TrafficClass.BULK_DOWNLINK
    return TrafficClass.DATA_TRANSFER


def _selected_traffic_class(
    application_protocol: str,
    traffic_class: TrafficClass | str | None,
) -> TrafficClass:
    if traffic_class is None:
        return _traffic_class(application_protocol)
    if isinstance(traffic_class, TrafficClass):
        return traffic_class
    return TrafficClass(str(traffic_class))


def _destination_type(traffic_class: TrafficClass) -> TrafficDestinationType:
    if traffic_class == TrafficClass.COMPUTE_SERVICE:
        return TrafficDestinationType.COMPUTE_NODE
    if traffic_class in {TrafficClass.TELEMETRY, TrafficClass.BULK_DOWNLINK}:
        return TrafficDestinationType.GROUND_ENDPOINT
    return TrafficDestinationType.SERVICE_ENDPOINT


def _selected_destination_type(
    traffic_class: TrafficClass,
    destination_type: TrafficDestinationType | str | None,
) -> TrafficDestinationType:
    if destination_type is None:
        return _destination_type(traffic_class)
    if isinstance(destination_type, TrafficDestinationType):
        return destination_type
    return TrafficDestinationType(str(destination_type))


def _model_assumptions(
    constellation_summary: Mapping[str, Any],
    *,
    satellite_count: int,
    user_count: int,
) -> tuple[str, ...]:
    profile = str(constellation_summary.get("profile", "CUSTOM_WALKER"))
    assumptions = [
        "Orbit allocation is deterministic and simplified; no SGP4 or external ephemeris is used.",
        "Network behavior is flow-level, not packet-level.",
        "Compute capacity is a deterministic abstract resource vector, not real execution.",
        "Coverage beams are bounded geometric visualization footprints, not RF antenna patterns.",
        f"Scenario scale uses {satellite_count} satellites and {user_count} users from backend config.",
    ]
    if profile == "STARLINK_SHELL_1_LIKE":
        assumptions.append(
            "Starlink Shell 1-like is an approximate allocation profile, not exact Starlink fidelity."
        )
    return tuple(assumptions)
