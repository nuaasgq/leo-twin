"""Backend-derived semantic summaries for frontend explanation surfaces."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from leo_twin.models.compute import ComputeResourceVector
from leo_twin.models.orbit import ConstellationAllocation
from leo_twin.models.traffic import TrafficClass, TrafficDestinationType


BackendDerivedSummary = dict[str, object]


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
    arrival_interval_seconds: int | float | None = None,
) -> BackendDerivedSummary:
    """Build deterministic backend-owned explanations for frontend display."""

    constellation_summary = _constellation_summary(constellation)
    traffic_class = _traffic_class(application_protocol)
    compute_vector = ComputeResourceVector.from_capacity(compute_capacity)
    total_cpu_gflops_fp32 = compute_vector.cpu_gflops_fp32 * compute_node_count
    traffic_summary: dict[str, object] = {
        "traffic_class": traffic_class.value,
        "destination_type": _destination_type(traffic_class).value,
        "generated_flow_count": flow_count,
        "arrival_model": "DETERMINISTIC_INTERVAL",
        "input_data_size_mb": task_data_size,
        "output_data_size_mb": 0.0,
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
        "total_cpu_gflops_fp32": total_cpu_gflops_fp32,
        "capacity_unit": "GFLOPS FP32",
        "compatibility_note": "Legacy scalar capacity maps to cpu_gflops_fp32.",
    }

    return {
        "derived_constellation_summary": constellation_summary,
        "traffic_demand_summary": traffic_summary,
        "compute_resource_summary": compute_summary,
        "model_assumptions": _model_assumptions(
            constellation_summary,
            satellite_count=satellite_count,
            user_count=user_count,
        ),
    }


def _constellation_summary(
    constellation: ConstellationAllocation | Mapping[str, object],
) -> dict[str, object]:
    if isinstance(constellation, ConstellationAllocation):
        return dict(constellation.to_summary())
    if not isinstance(constellation, Mapping):
        raise TypeError("constellation must be ConstellationAllocation or mapping")
    return dict(constellation)


def _traffic_class(application_protocol: str) -> TrafficClass:
    normalized = str(application_protocol).upper()
    if normalized == "TELEMETRY":
        return TrafficClass.TELEMETRY
    if normalized in {"TASK_OFFLOAD_FLOW", "COMPUTE_SERVICE"}:
        return TrafficClass.COMPUTE_SERVICE
    if normalized in {"BULK_DOWNLINK", "FILE_TRANSFER"}:
        return TrafficClass.BULK_DOWNLINK
    return TrafficClass.DATA_TRANSFER


def _destination_type(traffic_class: TrafficClass) -> TrafficDestinationType:
    if traffic_class == TrafficClass.COMPUTE_SERVICE:
        return TrafficDestinationType.COMPUTE_NODE
    if traffic_class in {TrafficClass.TELEMETRY, TrafficClass.BULK_DOWNLINK}:
        return TrafficDestinationType.GROUND_ENDPOINT
    return TrafficDestinationType.SERVICE_ENDPOINT


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
        f"Scenario scale uses {satellite_count} satellites and {user_count} users from backend config.",
    ]
    if profile == "STARLINK_SHELL_1_LIKE":
        assumptions.append(
            "Starlink Shell 1-like is an approximate allocation profile, not exact Starlink fidelity."
        )
    return tuple(assumptions)
