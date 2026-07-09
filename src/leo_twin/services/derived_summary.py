"""Backend-derived semantic summaries for frontend explanation surfaces."""

from __future__ import annotations

from collections.abc import Mapping
from math import isfinite
from typing import Any

from leo_twin.models.compute import ComputeResourceVector
from leo_twin.models.orbit import ConstellationAllocation
from leo_twin.models.traffic import (
    TrafficClass,
    TrafficDestinationType,
    TrafficServiceMixConfig,
    TrafficServiceMixItem,
    generate_traffic_service_mix,
)
from leo_twin.services.configuration_schema import USER_CONFIGURATION_SCHEMA_V2_ID
from leo_twin.schema.cache_offload_migration_contract import (
    cache_offload_migration_contract_v1_to_dict,
)
from leo_twin.schema.compute_resource_contract import compute_resource_contract_v2_to_dict
from leo_twin.schema.network_model_contract import network_model_contract_v2_to_dict
from leo_twin.schema.service_placement_contract import (
    service_placement_contract_v2_to_dict,
)
from leo_twin.services.dashboard_information_architecture import (
    dashboard_information_architecture_v3_to_dict,
)
from leo_twin.services.detail_pagination_contract import (
    large_detail_pagination_contract_v2_to_dict,
)
from leo_twin.services.lod_snapshot_policy import lod_snapshot_policy_v2_to_dict
from leo_twin.services.runtime_guardrails_v2 import (
    RuntimeGuardrailConfigV2,
    runtime_guardrails_v2_to_dict,
)
from leo_twin.services.scale_policy_v2 import scale_policy_v2_to_dict


BackendDerivedSummary = dict[str, object]
_EARTH_RADIUS_KM = 6371.0
_EARTH_MU_KM3_S2 = 398600.4418
_TRAFFIC_EXPLANATION_MAX_REQUESTS = 2_000
_TRAFFIC_EXPLANATION_MAX_ENDPOINT_IDS = 512


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
    transport_protocol: str = "TCP",
    routing_protocol: str = "LINK_STATE",
    datalink_mac_protocol: str = "TDMA",
    traffic_class: TrafficClass | str | None = None,
    traffic_destination_type: TrafficDestinationType | str | None = None,
    traffic_output_data_size: float = 0.0,
    traffic_data_transfer_weight: float = 0.0,
    traffic_telemetry_weight: float = 0.0,
    traffic_bulk_downlink_weight: float = 0.0,
    traffic_compute_service_weight: float = 0.0,
    traffic_emergency_weight: float = 0.0,
    compute_cpu_gflops_fp64: float = 0.0,
    compute_gpu_tflops_fp32: float = 0.0,
    compute_gpu_tflops_fp16: float = 0.0,
    compute_npu_tops_int8: float = 0.0,
    compute_memory_gb: float = 32.0,
    compute_storage_gb: float = 512.0,
    arrival_interval_seconds: int | float | None = None,
    flow_interval_seconds: int | float | None = None,
    task_interval_seconds: int | float | None = None,
    arrival_interval_source: str | None = None,
    traffic_schedule_policy: str | None = None,
    orbit_altitude_m: float | None = None,
    orbit_inclination_deg: float | None = None,
    beam_count: int = 7,
    beam_radius_m: float = 160_000.0,
    beam_length_m: float = 600_000.0,
    phase_policy: str = "DETERMINISTIC_PLANE_SLOT_PHASE",
    runtime_mode: str | None = None,
    runtime_speed_factor: float | None = None,
    runtime_duration_seconds: int | float | None = None,
    runtime_seed: int | None = None,
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
    service_mix_summary = _traffic_service_mix_summary(
        selected_traffic_class,
        selected_destination_type,
        flow_count=flow_count,
        data_transfer_weight=traffic_data_transfer_weight,
        telemetry_weight=traffic_telemetry_weight,
        bulk_downlink_weight=traffic_bulk_downlink_weight,
        compute_service_weight=traffic_compute_service_weight,
        emergency_weight=traffic_emergency_weight,
    )
    service_mix_request_counts = service_mix_summary[
        "service_mix_generated_request_counts"
    ]
    assert isinstance(service_mix_request_counts, dict)
    compute_service_request_count = int(
        service_mix_request_counts[TrafficClass.COMPUTE_SERVICE.value]
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
        "traffic_class_label": _traffic_class_label(selected_traffic_class),
        "destination_type": selected_destination_type.value,
        "destination_type_label": _traffic_destination_label(selected_destination_type),
        "generated_flow_count": flow_count,
        "generated_task_count": compute_service_request_count,
        "generated_output_flow_metadata_count": compute_service_request_count,
        "arrival_model": "DETERMINISTIC_INTERVAL",
        "source_selection_policy": "ROUND_ROBIN_GROUND_USERS",
        "destination_selection_policy": _traffic_destination_policy(
            selected_destination_type,
        ),
        "input_data_size_mb": task_data_size,
        "output_data_size_mb": float(traffic_output_data_size),
        "total_input_data_mb": float(flow_count * task_data_size),
        "total_output_data_mb": float(flow_count * traffic_output_data_size),
        "priority": 0,
        "demand_capacity_mbps": demand_capacity,
        "task_compute_demand": task_compute_demand,
        **service_mix_summary,
        **_traffic_lifecycle_summary(
            selected_traffic_class,
            selected_destination_type,
        ),
    }
    if arrival_interval_seconds is not None:
        arrival_interval = float(arrival_interval_seconds)
        system_rate = 60.0 / arrival_interval if arrival_interval > 0.0 else 0.0
        traffic_summary["arrival_interval_seconds"] = arrival_interval
        traffic_summary["system_request_rate_per_minute"] = system_rate
        traffic_summary["average_user_request_rate_per_minute"] = (
            system_rate / float(user_count) if user_count > 0 else 0.0
        )
    traffic_schedule_semantics = _traffic_schedule_semantics_v1(
        selected_traffic_class=selected_traffic_class,
        traffic_summary=traffic_summary,
        flow_count=flow_count,
        arrival_interval_seconds=arrival_interval_seconds,
        flow_interval_seconds=flow_interval_seconds,
        task_interval_seconds=task_interval_seconds,
        arrival_interval_source=arrival_interval_source,
        traffic_schedule_policy=traffic_schedule_policy,
    )
    traffic_summary["traffic_schedule_semantics_id"] = traffic_schedule_semantics[
        "summary_id"
    ]
    traffic_summary["effective_arrival_interval_source"] = (
        traffic_schedule_semantics["effective_arrival_interval_source"]
    )
    traffic_summary["effective_arrival_interval_seconds"] = (
        traffic_schedule_semantics["effective_arrival_interval_seconds"]
    )
    traffic_demand_explanation = _traffic_demand_explanation_v1(
        traffic_summary,
        selected_traffic_class=selected_traffic_class,
        selected_destination_type=selected_destination_type,
        satellite_count=satellite_count,
        user_count=user_count,
        compute_node_count=compute_node_count,
        flow_count=flow_count,
        task_compute_demand=task_compute_demand,
        task_data_size=task_data_size,
        traffic_output_data_size=traffic_output_data_size,
        arrival_interval_seconds=arrival_interval_seconds,
    )
    traffic_demand_explanation["traffic_schedule_semantics_v1"] = (
        traffic_schedule_semantics
    )

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
    compute_resource_contract = compute_resource_contract_v2_to_dict()
    compute_resource_contract["configured_node_profile"] = {
        "compute_node_count": compute_node_count,
        "legacy_capacity_per_node": compute_capacity,
        "cpu_gflops_fp32_per_node": compute_vector.cpu_gflops_fp32,
        "cpu_gflops_fp64_per_node": compute_vector.cpu_gflops_fp64,
        "gpu_tflops_fp32_per_node": compute_vector.gpu_tflops_fp32,
        "gpu_tflops_fp16_per_node": compute_vector.gpu_tflops_fp16,
        "npu_tops_int8_per_node": compute_vector.npu_tops_int8,
        "memory_gb_per_node": compute_vector.memory_gb,
        "storage_gb_per_node": compute_vector.storage_gb,
    }
    service_placement_contract = service_placement_contract_v2_to_dict()
    service_placement_contract["configured_policy"] = {
        "compute_node_count": compute_node_count,
        "default_policy": service_placement_contract["default_policy"],
        "queue_state_source": "RouteAwareComputeEngine._available_at",
        "max_queue_depth": None,
        "candidate_count_policy": (
            "Route path compute nodes are preferred when available; otherwise "
            "all configured satellite compute nodes remain candidates."
        ),
    }
    cache_offload_migration_contract = cache_offload_migration_contract_v1_to_dict()
    cache_offload_migration_contract["configured_observability"] = {
        "compute_node_count": compute_node_count,
        "cache_behavior_enabled": False,
        "offload_behavior_enabled": False,
        "migration_behavior_enabled": False,
        "observability_source": (
            "Future fields will be derived from service_latency_history_v1, "
            "compute_task_timeline_summary_v1, and node_detail_summary_v1."
        ),
    }
    coverage_summary = {
        "coverage_model": "DETERMINISTIC_GEOMETRIC_FOOTPRINT",
        "fidelity_level": "DISPLAY_APPROXIMATION",
        "selected_satellite_detail_mode": "SELECTED_SATELLITE_ONLY",
        "beam_pattern": "CENTER_PLUS_HEX_RING_VISUAL_APPROXIMATION",
        "footprint_intersection_policy": "VISUAL_GEOMETRIC_CONTAINMENT_ONLY",
        "default_beam_count": int(beam_count),
        "beam_radius_m": float(beam_radius_m),
        "beam_length_m": float(beam_length_m),
        "global_beam_render_limit": 1,
        "excluded_physics": [
            "RF_PROPAGATION",
            "ANTENNA_PATTERN",
            "LINK_BUDGET",
            "INTERFERENCE",
        ],
        "model_note": (
            "Selected-satellite beam cells are deterministic visual footprints; "
            "no RF propagation or antenna-pattern simulation is performed."
        ),
        "intersection_note": (
            "Coverage/user intersections are deterministic geometric containment "
            "counts for visualization only; they are not access decisions."
        ),
    }
    network_model_contract = network_model_contract_v2_to_dict()
    network_model_contract["configured_protocol_profile"] = {
        "application_protocol": str(application_protocol),
        "transport_protocol": str(transport_protocol),
        "routing_protocol": str(routing_protocol),
        "datalink_mac_protocol": str(datalink_mac_protocol),
    }
    scale_policy = scale_policy_v2_to_dict(
        satellite_count=satellite_count,
        user_count=user_count,
    )
    lod_snapshot_policy = lod_snapshot_policy_v2_to_dict(
        satellite_count=satellite_count,
        user_count=user_count,
        scale_policy=scale_policy,
    )
    runtime_guardrails = runtime_guardrails_v2_to_dict(
        RuntimeGuardrailConfigV2(
            satellite_count=satellite_count,
            user_count=user_count,
            compute_node_count=compute_node_count,
            simulation_duration_seconds=float(runtime_duration_seconds or 600.0),
        ),
        scale_policy=scale_policy,
        lod_snapshot_policy=lod_snapshot_policy,
    )
    detail_pagination_contract = large_detail_pagination_contract_v2_to_dict(
        satellite_count=satellite_count,
        user_count=user_count,
        compute_node_count=compute_node_count,
        route_count_estimate=flow_count,
        service_count_estimate=compute_service_request_count,
        scale_policy=scale_policy,
        lod_snapshot_policy=lod_snapshot_policy,
    )

    return {
        "derived_constellation_summary": constellation_summary,
        "traffic_demand_summary": traffic_summary,
        "traffic_demand_explanation_v1": traffic_demand_explanation,
        "traffic_schedule_semantics_v1": traffic_schedule_semantics,
        "compute_resource_summary": compute_summary,
        "compute_resource_contract_v2": compute_resource_contract,
        "service_placement_contract_v2": service_placement_contract,
        "cache_offload_migration_contract_v1": cache_offload_migration_contract,
        "coverage_beam_summary": coverage_summary,
        "network_model_contract_v2": network_model_contract,
        "scale_policy_v2": scale_policy,
        "lod_snapshot_policy_v2": lod_snapshot_policy,
        "runtime_guardrails_v2": runtime_guardrails,
        "large_detail_pagination_contract_v2": detail_pagination_contract,
        "dashboard_information_architecture_v3": (
            dashboard_information_architecture_v3_to_dict()
        ),
        "configuration_explanation_v2": _configuration_explanation_v2(
            constellation_summary=constellation_summary,
            traffic_summary=traffic_summary,
            compute_summary=compute_summary,
            network_model_contract=network_model_contract,
            satellite_count=satellite_count,
            user_count=user_count,
            compute_node_count=compute_node_count,
            runtime_mode=runtime_mode,
            runtime_speed_factor=runtime_speed_factor,
            runtime_duration_seconds=runtime_duration_seconds,
            runtime_seed=runtime_seed,
        ),
        "model_assumptions": _model_assumptions(
            constellation_summary,
            satellite_count=satellite_count,
            user_count=user_count,
            scale_policy=scale_policy,
            lod_snapshot_policy=lod_snapshot_policy,
            runtime_guardrails=runtime_guardrails,
            detail_pagination_contract=detail_pagination_contract,
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
        summary["orbital_velocity_km_s"] = _circular_orbital_velocity_km_s(
            orbit_altitude_m,
        )
        summary["orbital_velocity_model_note"] = (
            "Simplified circular-orbit speed estimate; no SGP4 or external ephemeris."
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


def _circular_orbital_velocity_km_s(altitude_m: float) -> float:
    altitude_km = float(altitude_m) / 1000.0
    semi_major_axis_km = _EARTH_RADIUS_KM + altitude_km
    return float((_EARTH_MU_KM3_S2 / semi_major_axis_km) ** 0.5)


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
    if normalized in {"EMERGENCY", "EMERGENCY_ALERT"}:
        return TrafficClass.EMERGENCY
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


_TRAFFIC_CLASS_ORDER = (
    TrafficClass.DATA_TRANSFER,
    TrafficClass.TELEMETRY,
    TrafficClass.BULK_DOWNLINK,
    TrafficClass.COMPUTE_SERVICE,
    TrafficClass.EMERGENCY,
)


def _traffic_service_mix_summary(
    selected_traffic_class: TrafficClass,
    selected_destination_type: TrafficDestinationType,
    *,
    flow_count: int,
    data_transfer_weight: float,
    telemetry_weight: float,
    bulk_downlink_weight: float,
    compute_service_weight: float,
    emergency_weight: float,
) -> dict[str, object]:
    raw_weights = {
        TrafficClass.DATA_TRANSFER.value: _non_negative_float(
            data_transfer_weight,
            "traffic_data_transfer_weight",
        ),
        TrafficClass.TELEMETRY.value: _non_negative_float(
            telemetry_weight,
            "traffic_telemetry_weight",
        ),
        TrafficClass.BULK_DOWNLINK.value: _non_negative_float(
            bulk_downlink_weight,
            "traffic_bulk_downlink_weight",
        ),
        TrafficClass.COMPUTE_SERVICE.value: _non_negative_float(
            compute_service_weight,
            "traffic_compute_service_weight",
        ),
        TrafficClass.EMERGENCY.value: _non_negative_float(
            emergency_weight,
            "traffic_emergency_weight",
        ),
    }
    total_weight = sum(raw_weights.values())
    effective_weights = dict(raw_weights)
    if total_weight == 0.0:
        effective_weights[selected_traffic_class.value] = 1.0
        total_weight = 1.0
    if (
        effective_weights[TrafficClass.COMPUTE_SERVICE.value] > 0.0
        and selected_destination_type != TrafficDestinationType.COMPUTE_NODE
    ):
        raise ValueError(
            "COMPUTE_SERVICE service mix requires destination_type=COMPUTE_NODE"
        )

    normalized_weights = {
        traffic_class.value: effective_weights[traffic_class.value] / total_weight
        for traffic_class in _TRAFFIC_CLASS_ORDER
    }
    active_classes = [
        traffic_class.value
        for traffic_class in _TRAFFIC_CLASS_ORDER
        if normalized_weights[traffic_class.value] > 0.0
    ]
    return {
        "service_mix_mode": (
            "WEIGHTED_MIX" if len(active_classes) > 1 else "SINGLE_CLASS"
        ),
        "service_mix_weights": {
            traffic_class.value: effective_weights[traffic_class.value]
            for traffic_class in _TRAFFIC_CLASS_ORDER
        },
        "service_mix_normalized_weights": normalized_weights,
        "active_service_classes": active_classes,
        "service_mix_generated_request_counts": _service_mix_request_counts(
            flow_count,
            normalized_weights,
        ),
    }


def _traffic_schedule_semantics_v1(
    *,
    selected_traffic_class: TrafficClass,
    traffic_summary: Mapping[str, object],
    flow_count: int,
    arrival_interval_seconds: int | float | None,
    flow_interval_seconds: int | float | None,
    task_interval_seconds: int | float | None,
    arrival_interval_source: str | None,
    traffic_schedule_policy: str | None,
) -> dict[str, object]:
    service_mix_mode = str(traffic_summary.get("service_mix_mode", "SINGLE_CLASS"))
    service_mix_enabled = (
        service_mix_mode == "WEIGHTED_MIX"
        or arrival_interval_source == "derived_service_mix_request_spacing"
        or traffic_schedule_policy == "WEIGHTED_SERVICE_MIX_EVEN_SPREAD"
    )
    effective_source = arrival_interval_source or _default_arrival_interval_source(
        selected_traffic_class,
        service_mix_enabled=service_mix_enabled,
    )
    schedule_policy = traffic_schedule_policy or _default_traffic_schedule_policy(
        selected_traffic_class,
        service_mix_enabled=service_mix_enabled,
    )
    flow_source, task_source = _traffic_schedule_event_sources(
        selected_traffic_class,
        service_mix_enabled=service_mix_enabled,
        effective_source=effective_source,
    )
    return {
        "summary_id": "leo_twin.traffic_schedule_semantics.v1",
        "version": "v1",
        "source": "backend_summary.traffic_demand_summary",
        "traffic_class": selected_traffic_class.value,
        "service_mix_mode": service_mix_mode,
        "service_mix_enabled": service_mix_enabled,
        "configured_flow_interval_seconds": _optional_float(flow_interval_seconds),
        "configured_task_interval_seconds": _optional_float(task_interval_seconds),
        "effective_arrival_interval_seconds": _optional_float(
            arrival_interval_seconds
        ),
        "effective_arrival_interval_source": effective_source,
        "flow_arrival_schedule_source": flow_source,
        "task_arrival_schedule_source": task_source,
        "schedule_policy": schedule_policy,
        "generated_request_count": max(0, int(flow_count)),
        "correlated_compute_service_pairs": (
            selected_traffic_class == TrafficClass.COMPUTE_SERVICE
        ),
        "packet_level_simulation": False,
        "frontend_inference_required": False,
        "model_note": (
            "Backend reports the deterministic flow-level request schedule used "
            "to generate traffic demand; no packet-level arrivals are modeled."
        ),
    }


def _default_arrival_interval_source(
    selected_traffic_class: TrafficClass,
    *,
    service_mix_enabled: bool,
) -> str:
    if service_mix_enabled:
        return "derived_service_mix_request_spacing"
    if selected_traffic_class == TrafficClass.COMPUTE_SERVICE:
        return "scenario.traffic_model.task_interval_seconds"
    return "scenario.traffic_model.flow_interval_seconds"


def _default_traffic_schedule_policy(
    selected_traffic_class: TrafficClass,
    *,
    service_mix_enabled: bool,
) -> str:
    if service_mix_enabled:
        return "WEIGHTED_SERVICE_MIX_EVEN_SPREAD"
    if selected_traffic_class == TrafficClass.COMPUTE_SERVICE:
        return "CORRELATED_INPUT_FLOW_AND_TASK_INTERVAL"
    return "FLOW_ONLY_INTERVAL"


def _traffic_schedule_event_sources(
    selected_traffic_class: TrafficClass,
    *,
    service_mix_enabled: bool,
    effective_source: str,
) -> tuple[str, str]:
    if service_mix_enabled:
        return (
            "derived_service_mix_request_spacing",
            (
                "derived_service_mix_request_spacing"
                if selected_traffic_class == TrafficClass.COMPUTE_SERVICE
                else "not_applicable"
            ),
        )
    if selected_traffic_class == TrafficClass.COMPUTE_SERVICE:
        return (effective_source, effective_source)
    return (effective_source, "not_applicable")


def _optional_float(value: int | float | None) -> float | None:
    if value is None:
        return None
    number = float(value)
    if not isfinite(number):
        raise ValueError("traffic schedule interval must be finite")
    return number


def _traffic_demand_explanation_v1(
    traffic_summary: Mapping[str, object],
    *,
    selected_traffic_class: TrafficClass,
    selected_destination_type: TrafficDestinationType,
    satellite_count: int,
    user_count: int,
    compute_node_count: int,
    flow_count: int,
    task_compute_demand: float,
    task_data_size: float,
    traffic_output_data_size: float,
    arrival_interval_seconds: int | float | None,
) -> dict[str, object]:
    configured_request_count = max(0, int(flow_count))
    explained_request_count = min(
        configured_request_count,
        _TRAFFIC_EXPLANATION_MAX_REQUESTS,
    )
    weights = traffic_summary.get("service_mix_weights", {})
    if not isinstance(weights, Mapping):
        weights = {selected_traffic_class.value: 1.0}
    items = tuple(
        TrafficServiceMixItem(
            traffic_class=traffic_class,
            weight=float(weights.get(traffic_class.value, 0.0)),
            source_ids=_traffic_explanation_source_ids(
                traffic_class,
                satellite_count=satellite_count,
                user_count=user_count,
            ),
            destination_ids=_traffic_explanation_destination_ids(
                _traffic_explanation_destination_type(
                    traffic_class,
                    selected_traffic_class=selected_traffic_class,
                    selected_destination_type=selected_destination_type,
                ),
                satellite_count=satellite_count,
                user_count=user_count,
                compute_node_count=compute_node_count,
            ),
            input_data_size=float(task_data_size),
            output_data_size=float(traffic_output_data_size),
            priority=int(traffic_summary.get("priority", 0)),
            destination_type=_traffic_explanation_destination_type(
                traffic_class,
                selected_traffic_class=selected_traffic_class,
                selected_destination_type=selected_destination_type,
            ),
            compute_demand=float(task_compute_demand),
            input_data_mb=float(task_data_size),
            output_data_mb=float(traffic_output_data_size),
            output_destination_ids=_traffic_explanation_source_ids(
                traffic_class,
                satellite_count=satellite_count,
                user_count=user_count,
            )
            if traffic_class == TrafficClass.COMPUTE_SERVICE
            else (),
        )
        for traffic_class in _TRAFFIC_CLASS_ORDER
        if float(weights.get(traffic_class.value, 0.0)) > 0.0
    )
    effective_items = items or (
        TrafficServiceMixItem(
            traffic_class=selected_traffic_class,
            weight=1.0,
            source_ids=_traffic_explanation_source_ids(
                selected_traffic_class,
                satellite_count=satellite_count,
                user_count=user_count,
            ),
            destination_ids=_traffic_explanation_destination_ids(
                selected_destination_type,
                satellite_count=satellite_count,
                user_count=user_count,
                compute_node_count=compute_node_count,
            ),
            input_data_size=float(task_data_size),
            output_data_size=float(traffic_output_data_size),
            priority=int(traffic_summary.get("priority", 0)),
            destination_type=selected_destination_type,
            compute_demand=float(task_compute_demand),
            input_data_mb=float(task_data_size),
            output_data_mb=float(traffic_output_data_size),
            output_destination_ids=_traffic_explanation_source_ids(
                selected_traffic_class,
                satellite_count=satellite_count,
                user_count=user_count,
            )
            if selected_traffic_class == TrafficClass.COMPUTE_SERVICE
            else (),
        ),
    )
    explanation = generate_traffic_service_mix(
        TrafficServiceMixConfig(
            items=effective_items,
            total_request_count=explained_request_count,
            arrival_interval=_traffic_explanation_interval(arrival_interval_seconds),
            id_prefix="backend-summary",
        )
    ).traffic_demand_explanation()
    explanation["source"] = "backend_summary.traffic_demand_summary"
    explanation["configured_request_count"] = configured_request_count
    explanation["explained_request_count"] = explained_request_count
    explanation["explanation_window_policy"] = (
        "FULL_CONFIGURED_WINDOW"
        if explained_request_count == configured_request_count
        else "BOUNDED_BACKEND_SUMMARY_WINDOW"
    )
    explanation["endpoint_window_policy"] = (
        "ROUND_ROBIN_ENDPOINT_IDS_CAPPED_AT_512_FOR_SUMMARY_PAYLOAD"
    )
    explanation["frontend_inference_required"] = False
    return explanation


def _traffic_explanation_destination_type(
    traffic_class: TrafficClass,
    *,
    selected_traffic_class: TrafficClass,
    selected_destination_type: TrafficDestinationType,
) -> TrafficDestinationType:
    if traffic_class == selected_traffic_class:
        return selected_destination_type
    return _destination_type(traffic_class)


def _traffic_explanation_source_ids(
    traffic_class: TrafficClass,
    *,
    satellite_count: int,
    user_count: int,
) -> tuple[str, ...]:
    if traffic_class in {TrafficClass.TELEMETRY, TrafficClass.BULK_DOWNLINK}:
        return _bounded_entity_ids("sat", satellite_count)
    return _bounded_entity_ids("user", user_count)


def _traffic_explanation_destination_ids(
    destination_type: TrafficDestinationType,
    *,
    satellite_count: int,
    user_count: int,
    compute_node_count: int,
) -> tuple[str, ...]:
    if destination_type == TrafficDestinationType.COMPUTE_NODE:
        return _bounded_entity_ids("sat-compute", compute_node_count)
    if destination_type == TrafficDestinationType.SATELLITE:
        return _bounded_entity_ids("sat", satellite_count)
    if destination_type == TrafficDestinationType.GROUND_ENDPOINT:
        return _bounded_entity_ids("ground-endpoint", user_count)
    return _bounded_entity_ids("service-endpoint", max(1, min(user_count, 32)))


def _bounded_entity_ids(prefix: str, count: int) -> tuple[str, ...]:
    bounded_count = min(
        max(1, int(count)),
        _TRAFFIC_EXPLANATION_MAX_ENDPOINT_IDS,
    )
    return tuple(f"{prefix}-{index:05d}" for index in range(bounded_count))


def _traffic_explanation_interval(value: int | float | None) -> float:
    if value is None:
        return 1.0
    interval = float(value)
    if not isfinite(interval) or interval <= 0.0:
        return 1.0
    return interval


def _service_mix_request_counts(
    flow_count: int,
    normalized_weights: Mapping[str, float],
) -> dict[str, int]:
    count = max(0, int(flow_count))
    floor_counts: dict[str, int] = {}
    fractions: list[tuple[float, int, str]] = []
    assigned = 0
    for order, traffic_class in enumerate(_TRAFFIC_CLASS_ORDER):
        class_name = traffic_class.value
        exact = count * float(normalized_weights[class_name])
        base = int(exact)
        floor_counts[class_name] = base
        assigned += base
        fractions.append((exact - base, order, class_name))
    remaining = count - assigned
    for _, _, class_name in sorted(fractions, key=lambda item: (-item[0], item[1]))[
        :remaining
    ]:
        floor_counts[class_name] += 1
    return {
        traffic_class.value: floor_counts[traffic_class.value]
        for traffic_class in _TRAFFIC_CLASS_ORDER
    }


def _non_negative_float(value: float, field_name: str) -> float:
    numeric = float(value)
    if not isfinite(numeric) or numeric < 0.0:
        raise ValueError(f"{field_name} must be a non-negative finite number")
    return numeric


def _traffic_class_label(traffic_class: TrafficClass) -> str:
    labels = {
        TrafficClass.COMPUTE_SERVICE: "通信-计算服务",
        TrafficClass.DATA_TRANSFER: "数据传输",
        TrafficClass.TELEMETRY: "遥测",
        TrafficClass.BULK_DOWNLINK: "批量下传",
        TrafficClass.EMERGENCY: "应急业务",
    }
    return labels[traffic_class]


def _traffic_destination_label(destination_type: TrafficDestinationType) -> str:
    labels = {
        TrafficDestinationType.COMPUTE_NODE: "星上算力节点",
        TrafficDestinationType.GROUND_ENDPOINT: "地面端",
        TrafficDestinationType.SATELLITE: "卫星节点",
        TrafficDestinationType.SERVICE_ENDPOINT: "服务端点",
    }
    return labels[destination_type]


def _traffic_destination_policy(destination_type: TrafficDestinationType) -> str:
    policies = {
        TrafficDestinationType.COMPUTE_NODE: "ROUND_ROBIN_COMPUTE_NODES",
        TrafficDestinationType.GROUND_ENDPOINT: "ROUND_ROBIN_GROUND_ENDPOINTS",
        TrafficDestinationType.SATELLITE: "ROUND_ROBIN_SATELLITES",
        TrafficDestinationType.SERVICE_ENDPOINT: "ROUND_ROBIN_SERVICE_ENDPOINTS",
    }
    return policies[destination_type]


def _traffic_lifecycle_summary(
    traffic_class: TrafficClass,
    destination_type: TrafficDestinationType,
) -> dict[str, object]:
    if traffic_class == TrafficClass.COMPUTE_SERVICE:
        if destination_type != TrafficDestinationType.COMPUTE_NODE:
            raise ValueError(
                "COMPUTE_SERVICE traffic requires destination_type=COMPUTE_NODE"
            )
        return {
            "execution_shape": "FLOW_THEN_COMPUTE_TASK",
            "execution_label": "输入流 + 计算任务",
            "requires_compute_node_destination": True,
            "compatibility_note": "通信-计算服务要求目的类型为星上算力节点。",
            "lifecycle_note": (
                "输入流完成后触发计算任务；输出数据大小作为结果流元数据保留。"
            ),
        }
    return {
        "execution_shape": "FLOW_ONLY",
        "execution_label": "流级网络业务",
        "requires_compute_node_destination": False,
        "compatibility_note": "该业务类型按流级网络业务执行，不生成计算任务。",
        "lifecycle_note": "网络流完成即完成本次业务；不触发星上计算任务生命周期。",
    }


def _configuration_explanation_v2(
    *,
    constellation_summary: Mapping[str, Any],
    traffic_summary: Mapping[str, object],
    compute_summary: Mapping[str, object],
    network_model_contract: Mapping[str, object],
    satellite_count: int,
    user_count: int,
    compute_node_count: int,
    runtime_mode: str | None,
    runtime_speed_factor: float | None,
    runtime_duration_seconds: int | float | None,
    runtime_seed: int | None,
) -> dict[str, object]:
    protocol_profile = network_model_contract.get("configured_protocol_profile", {})
    if not isinstance(protocol_profile, Mapping):
        protocol_profile = {}
    runtime_values: dict[str, object] = {}
    if runtime_mode is not None:
        runtime_values["runtime.mode"] = str(runtime_mode)
    if runtime_speed_factor is not None:
        runtime_values["runtime.speed_factor"] = float(runtime_speed_factor)
    if runtime_duration_seconds is not None:
        runtime_values["runtime.duration"] = float(runtime_duration_seconds)
    if runtime_seed is not None:
        runtime_values["runtime.seed"] = int(runtime_seed)
    return {
        "version": "v2",
        "explanation_id": "leo_twin.configuration_explanation.v2",
        "schema_id": USER_CONFIGURATION_SCHEMA_V2_ID,
        "source": "BACKEND_DERIVED_SUMMARY",
        "frontend_policy": "CONTROL_PANEL_KEY_FIELDS_ONLY",
        "mutation_policy": "READ_ONLY_EXPLANATION",
        "configuration_surfaces": (
            {
                "surface": "CONTROL_PANEL_KEY_FIELDS",
                "purpose": (
                    "Expose the small set of high-impact parameters for quick "
                    "interactive scenario setup."
                ),
                "source": "configuration_surface_summary.key_fields",
            },
            {
                "surface": "DETAILED_YAML_JSON_FILE",
                "purpose": (
                    "Carry the full deterministic scenario configuration, "
                    "including file-only model and fidelity parameters."
                ),
                "source": "configuration_surface_summary.user_config_schema_v2.fields",
            },
            {
                "surface": "APPROVED_TEMPLATE_CATALOG",
                "purpose": (
                    "Provide executable user-facing scenario templates with "
                    "comments and known scale/fidelity intent."
                ),
                "source": "/scenario/user-config/templates",
            },
            {
                "surface": "CURRENT_EFFECTIVE_CONFIG_EXPORT",
                "purpose": (
                    "Expose the normalized effective configuration and stable "
                    "hash for reproducible runs."
                ),
                "source": "/scenario/user-config/export",
            },
        ),
        "section_explanations": (
            {
                "section": "scenario",
                "title": "星座、用户和算力规模",
                "source_fields": (
                    "scenario.satellite_count",
                    "scenario.user_count",
                    "scenario.compute_nodes",
                    "scenario.orbit.*",
                ),
                "current_values": {
                    "satellite_count": satellite_count,
                    "user_count": user_count,
                    "compute_node_count": compute_node_count,
                    "constellation_profile": constellation_summary.get("profile"),
                    "plane_count": constellation_summary.get("plane_count"),
                    "satellites_per_plane": constellation_summary.get(
                        "satellites_per_plane"
                    ),
                    "altitude_m": constellation_summary.get("altitude_m"),
                    "inclination_deg": constellation_summary.get("inclination_deg"),
                },
                "model_semantics": (
                    "Scenario fields define deterministic constellation allocation, "
                    "ground-user scale, and satellite-hosted compute-node scale."
                ),
                "excluded_semantics": ("SGP4", "EXTERNAL_EPHEMERIS", "RF_LINK_BUDGET"),
            },
            {
                "section": "traffic",
                "title": "业务需求生成",
                "source_fields": (
                    "scenario.traffic_model.*",
                    "network.application_protocol",
                ),
                "current_values": {
                    "traffic_class": traffic_summary.get("traffic_class"),
                    "destination_type": traffic_summary.get("destination_type"),
                    "generated_flow_count": traffic_summary.get("generated_flow_count"),
                    "generated_task_count": traffic_summary.get("generated_task_count"),
                    "arrival_model": traffic_summary.get("arrival_model"),
                    "service_mix_mode": traffic_summary.get("service_mix_mode"),
                    "active_service_classes": traffic_summary.get(
                        "active_service_classes"
                    ),
                },
                "model_semantics": (
                    "Traffic fields generate deterministic flow-level service "
                    "requests; compute-service traffic links input flow metadata "
                    "to task generation."
                ),
                "excluded_semantics": ("PACKET_GENERATION", "UNSEEDED_RANDOM_TRAFFIC"),
            },
            {
                "section": "network",
                "title": "网络协议和 KPI 来源",
                "source_fields": (
                    "network.application_protocol",
                    "network.transport_protocol",
                    "network.routing_protocol",
                    "network.datalink_mac_protocol",
                    "network.space_link_mode",
                ),
                "current_values": {
                    "application_protocol": protocol_profile.get("application_protocol"),
                    "transport_protocol": protocol_profile.get("transport_protocol"),
                    "routing_protocol": protocol_profile.get("routing_protocol"),
                    "datalink_mac_protocol": protocol_profile.get(
                        "datalink_mac_protocol"
                    ),
                },
                "model_semantics": (
                    "Network fields select deterministic flow-level protocol, "
                    "routing, data-link, and channel abstractions used by KPI "
                    "provenance."
                ),
                "excluded_semantics": (
                    "PACKET_LEVEL_SIMULATION",
                    "EXATA_GLOMOSIM",
                    "RF_PROPAGATION_SOLVER",
                ),
            },
            {
                "section": "compute",
                "title": "星上算力资源",
                "source_fields": (
                    "scenario.compute_capacity",
                    "scenario.compute_*",
                    "scenario.compute_scheduling_policy",
                ),
                "current_values": {
                    "resource_model": compute_summary.get("resource_model"),
                    "node_role": compute_summary.get("node_role"),
                    "compute_node_count": compute_summary.get("compute_node_count"),
                    "cpu_gflops_fp32_per_node": compute_summary.get(
                        "cpu_gflops_fp32_per_node"
                    ),
                    "gpu_tflops_fp32_per_node": compute_summary.get(
                        "gpu_tflops_fp32_per_node"
                    ),
                    "npu_tops_int8_per_node": compute_summary.get(
                        "npu_tops_int8_per_node"
                    ),
                },
                "model_semantics": (
                    "Compute fields describe deterministic satellite-hosted "
                    "resource vectors and queue/execution timing proxies."
                ),
                "excluded_semantics": (
                    "REAL_CODE_EXECUTION",
                    "CUDA_RUNTIME",
                    "POWER_THERMAL_MODEL",
                ),
            },
            {
                "section": "runtime",
                "title": "运行时控制和复现",
                "source_fields": (
                    "runtime.mode",
                    "runtime.speed_factor",
                    "runtime.seed",
                    "runtime.duration",
                ),
                "current_values": runtime_values,
                "model_semantics": (
                    "Runtime fields control deterministic pacing, seed, and "
                    "terminal duration; simulation time remains owned by the "
                    "event kernel."
                ),
                "excluded_semantics": ("DOMAIN_LOGIC_IN_EVENT_KERNEL",),
            },
            {
                "section": "ui",
                "title": "界面展示偏好",
                "source_fields": ("ui.visualization.*",),
                "current_values": {
                    "semantic_owner": "backend_summary",
                    "ui_role": "render backend-owned state and explanations",
                },
                "model_semantics": (
                    "UI fields control initial rendering preferences only; "
                    "they do not define simulation model semantics."
                ),
                "excluded_semantics": ("FRONTEND_MODEL_INFERENCE",),
            },
        ),
        "determinism": {
            "seed_source": "runtime.seed",
            "ordered_generation": True,
            "unknown_key_policy": "REJECT",
            "defaulting_policy": "OMITTED_FIELDS_USE_BACKEND_DEFAULTS",
            "result_package_expectation": (
                "config snapshot, events.jsonl, metrics.csv, summary.json"
            ),
        },
        "forbidden_integrations": ("STK", "EXATA", "AFSIM", "DDS"),
        "packet_level_simulation": False,
        "model_boundary_note": (
            "This object explains how accepted configuration drives current "
            "backend model semantics; it is not a mutable configuration API."
        ),
    }


def _model_assumptions(
    constellation_summary: Mapping[str, Any],
    *,
    satellite_count: int,
    user_count: int,
    scale_policy: Mapping[str, Any],
    lod_snapshot_policy: Mapping[str, Any],
    runtime_guardrails: Mapping[str, Any],
    detail_pagination_contract: Mapping[str, Any],
) -> tuple[str, ...]:
    profile = str(constellation_summary.get("profile", "CUSTOM_WALKER"))
    scale_band = str(scale_policy.get("active_scale_band", "UNKNOWN"))
    hidden_detail_policy = str(
        lod_snapshot_policy.get("hidden_detail_policy", "UNKNOWN")
    )
    guardrail_decision = str(runtime_guardrails.get("decision", "UNKNOWN"))
    detail_collections = detail_pagination_contract.get("collections", ())
    detail_collection_count = (
        len(detail_collections) if isinstance(detail_collections, tuple) else 0
    )
    assumptions = [
        "Orbit allocation is deterministic and simplified; no SGP4 or external ephemeris is used.",
        "Network behavior is flow-level, not packet-level.",
        "Compute capacity is a deterministic abstract resource vector, not real execution.",
        "Coverage beams are bounded geometric visualization footprints, not RF antenna patterns.",
        f"Scale policy v2 classifies this scenario as {scale_band} for fidelity and LOD decisions.",
        f"LOD snapshot policy v2 uses {hidden_detail_policy} for rows outside active windows.",
        f"Runtime guardrails v2 classify pre-run execution as {guardrail_decision}.",
        f"Large detail pagination contract v2 exposes {detail_collection_count} cursor-backed collections.",
        f"Scenario scale uses {satellite_count} satellites and {user_count} users from backend config.",
    ]
    if profile == "STARLINK_SHELL_1_LIKE":
        assumptions.append(
            "Starlink Shell 1-like is an approximate allocation profile, not exact Starlink fidelity."
        )
    return tuple(assumptions)
