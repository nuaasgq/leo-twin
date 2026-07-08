"""Deterministic scenario construction for the integration demo."""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, pi, radians, sin

from leo_twin.models.compute import ComputeNode
from leo_twin.models.network import GroundEndpoint
from leo_twin.models.orbit import AutoPlaneAllocator, ConstellationAllocation, OrbitSatelliteConfig
from leo_twin.models.traffic import (
    TrafficClass,
    TrafficDemandBatch,
    TrafficDemandRecord,
    TrafficDestinationType,
    TrafficServiceMixConfig,
    TrafficServiceMixItem,
    generate_traffic_service_mix,
)
from leo_twin.services.configuration_view import build_user_configuration_view
from leo_twin.services.derived_summary import build_backend_derived_summary
from leo_twin.services.scale_fidelity import (
    ScaleFidelityConfig,
    build_scale_fidelity_summary,
)
from leo_twin.schema import (
    CoverageSlot,
    EventType,
    FlowRequest,
    GroundUserProfile,
    OrbitalElementSet,
    SatelliteProfile,
    SimEvent,
    TaskRequest,
)

from examples.integration_demo.config import DemoConfig, demo_config_to_sees_config


_EARTH_RADIUS_KM = 6371.0
_GROUND_ENDPOINT_MIN_ELEVATION_DEG = 10.0
_GROUND_ENDPOINT_MAX_RANGE_KM = 2500.0
_SCALE_WORKLOAD_SMOOTHING_NODE_THRESHOLD = 300


@dataclass(frozen=True)
class GroundUserRenderState:
    user_id: str
    cell_id: str
    position: tuple[float, float, float]
    status: str = "ACTIVE"


@dataclass(frozen=True)
class DemoScenario:
    orbit_satellites: tuple[OrbitSatelliteConfig, ...]
    orbit_elements: tuple[OrbitalElementSet, ...]
    network_satellites: tuple[SatelliteProfile, ...]
    ground_users: tuple[GroundUserProfile, ...]
    ground_user_render_states: tuple[GroundUserRenderState, ...]
    ground_endpoints: tuple[GroundEndpoint, ...]
    compute_nodes: tuple[ComputeNode, ...]
    traffic_demand: TrafficDemandBatch
    initial_events: tuple[SimEvent, ...]
    frontend_config: dict[str, object]


def build_demo_scenario(config: DemoConfig) -> DemoScenario:
    ground_users = _ground_users(config)
    render_users = _ground_user_render_states(config)
    ground_endpoints = _ground_endpoints(render_users)
    constellation_allocation = _constellation_allocation(config)
    orbit_satellites = _orbit_satellites(config, constellation_allocation)
    orbit_elements = _orbit_elements(config, constellation_allocation)
    network_satellites = _network_satellites(config)
    compute_nodes = _compute_nodes(config)
    traffic_demand = _traffic_demand_batch(config)
    initial_events = _initial_events(config, traffic_demand)
    backend_summary = _backend_summary(config, constellation_allocation)
    orbit_frontend_config: dict[str, object] = {
        "update_interval_seconds": config.orbit_tick_seconds,
        "plane_count": constellation_allocation.plane_count,
        "altitude_m": config.orbit_altitude_m,
        "inclination_deg": config.orbit_inclination_deg,
    }
    if config.orbit_update_mode is not None:
        orbit_frontend_config["orbit_update_mode"] = config.orbit_update_mode
    return DemoScenario(
        orbit_satellites=orbit_satellites,
        orbit_elements=orbit_elements,
        network_satellites=network_satellites,
        ground_users=ground_users,
        ground_user_render_states=render_users,
        ground_endpoints=ground_endpoints,
        compute_nodes=compute_nodes,
        traffic_demand=traffic_demand,
        initial_events=initial_events,
        frontend_config={
            "scenario_id": f"integration-demo-{config.seed}",
            "satellites": [
                {
                    "satellite_id": satellite.satellite_id,
                    "label": satellite.satellite_id,
                }
                for satellite in orbit_satellites
            ],
            "ground_users": [
                {
                    "user_id": user.user_id,
                    "cell_id": user.cell_id,
                    "position": list(user.position),
                    "status": user.status,
                }
                for user in render_users
            ],
            "render": {
                "beam_length_m": 600_000,
                "beam_radius_m": 160_000,
                "max_satellites": config.satellite_count,
            },
            "scenario": {
                "satellite_count": config.satellite_count,
                "user_count": config.ground_user_count,
                "compute_nodes": min(config.compute_node_count, config.satellite_count),
                "compute_capacity": config.compute_capacity,
                "compute_cpu_gflops_fp64": config.compute_cpu_gflops_fp64,
                "compute_gpu_tflops_fp32": config.compute_gpu_tflops_fp32,
                "compute_gpu_tflops_fp16": config.compute_gpu_tflops_fp16,
                "compute_npu_tops_int8": config.compute_npu_tops_int8,
                "compute_memory_gb": config.compute_memory_gb,
                "compute_storage_gb": config.compute_storage_gb,
                "compute_scheduling_policy": config.compute_scheduling_policy,
                "orbit": orbit_frontend_config,
                "traffic_model": _traffic_frontend_config(config),
            },
            "network": {
                "application_protocol": config.application_protocol,
                "transport_protocol": config.transport_protocol,
                "routing_protocol": config.routing_protocol,
                "datalink_mac_protocol": config.datalink_mac_protocol,
                "transport_loss_rate": config.transport_loss_rate,
                "transport_congestion_window_segments": (
                    config.transport_congestion_window_segments
                ),
                "routing_latency_weight": config.routing_latency_weight,
                "routing_inverse_capacity_weight": config.routing_inverse_capacity_weight,
                "routing_hop_weight": config.routing_hop_weight,
                "carrier_frequency_hz": config.carrier_frequency_hz,
                "channel_bandwidth_hz": config.channel_bandwidth_hz,
                "rain_rate_mm_h": config.rain_rate_mm_h,
                "rain_attenuation_coefficient_db_per_km_per_mm_h": (
                    config.rain_attenuation_coefficient_db_per_km_per_mm_h
                ),
                "rain_effective_path_km": config.rain_effective_path_km,
                "antenna_diameter_m": config.antenna_diameter_m,
                "antenna_aperture_efficiency": config.antenna_aperture_efficiency,
                "transmit_power_dbw": config.transmit_power_dbw,
                "system_loss_db": config.system_loss_db,
                "noise_temperature_k": config.noise_temperature_k,
                "space_link_mode": config.space_link_mode,
                "max_space_link_candidates_per_satellite": (
                    config.max_space_link_candidates_per_satellite
                ),
                "batch_space_link_update_limit": config.batch_space_link_update_limit,
                "time_pressure_period_s": config.time_pressure_period_s,
                "time_pressure_burst_center_phase": (
                    config.time_pressure_burst_center_phase
                ),
                "time_pressure_burst_width_phase": (
                    config.time_pressure_burst_width_phase
                ),
                "time_pressure_burst_amplitude": (
                    config.time_pressure_burst_amplitude
                ),
            },
            "runtime": {
                "mode": config.runtime_mode,
                "speed_factor": config.runtime_speed_factor,
                "seed": config.seed,
                "duration": config.duration_seconds,
                "status": "STOPPED",
            },
            "ui": {
                "visualization": {
                    "satellites": True,
                    "links": True,
                    "users": True,
                    "metrics": True,
                },
                "update_frequency_hz": max(1, 1000 // max(1, config.metric_sample_interval)),
                "dashboard_layout": "right_panel",
            },
            "derived_constellation_summary": (
                backend_summary["derived_constellation_summary"]
            ),
            "backend_summary": backend_summary,
            "endpoints": {
                "events": config.websocket_events,
                "state": config.websocket_state,
                "metrics": config.metrics_snapshot,
                "config": config.scenario_config,
                "control": "/control",
                "runtime_status": "/runtime/status",
            },
        },
    )


def _orbit_satellites(
    config: DemoConfig,
    allocation: ConstellationAllocation,
) -> tuple[OrbitSatelliteConfig, ...]:
    planes = allocation.plane_count
    satellites_per_plane = allocation.satellites_per_plane
    orbital_radius = 6_371_000.0 + config.orbit_altitude_m
    inclination_scale = config.orbit_inclination_deg / 90.0
    return tuple(
        OrbitSatelliteConfig(
            satellite_id=f"sat-{index:03d}",
            orbital_radius=orbital_radius + 1_000.0 * allocation.slot_index(index),
            angular_velocity=0.001 + (index % 5) * 0.00001,
            phase=(allocation.slot_index(index) / satellites_per_plane) * 2.0 * pi,
            inclination=(allocation.plane_index(index) / planes) * inclination_scale,
        )
        for index in range(config.satellite_count)
    )


def _orbit_elements(
    config: DemoConfig,
    allocation: ConstellationAllocation,
) -> tuple[OrbitalElementSet, ...]:
    plane_count = allocation.plane_count
    satellites_per_plane = allocation.satellites_per_plane
    semi_major_axis_km = 6371.0 + config.orbit_altitude_m / 1000.0
    return tuple(
        OrbitalElementSet(
            satellite_id=f"sat-{index:03d}",
            epoch=0.0,
            semi_major_axis_km=semi_major_axis_km + float(allocation.slot_index(index)),
            eccentricity=0.001,
            inclination_deg=config.orbit_inclination_deg,
            raan_deg=(allocation.plane_index(index) * 360.0 / plane_count) % 360.0,
            argument_of_perigee_deg=0.0,
            mean_anomaly_deg=(
                allocation.slot_index(index) * 360.0 / satellites_per_plane
                + allocation.plane_index(index) * 0.5
            )
            % 360.0,
        )
        for index in range(config.satellite_count)
    )


def _constellation_allocation(config: DemoConfig) -> ConstellationAllocation:
    return AutoPlaneAllocator.allocate(
        satellite_count=config.satellite_count,
        plane_count=config.orbit_plane_count if config.orbit_plane_count_explicit else None,
        profile=config.constellation_profile,
    )


def _backend_summary(
    config: DemoConfig,
    allocation: ConstellationAllocation,
) -> dict[str, object]:
    summary = build_backend_derived_summary(
        constellation=allocation,
        satellite_count=config.satellite_count,
        user_count=config.ground_user_count,
        compute_node_count=min(config.compute_node_count, config.satellite_count),
        compute_capacity=config.compute_capacity,
        flow_count=_scheduled_task_count(config),
        demand_capacity=config.flow_demand_capacity,
        task_compute_demand=config.task_compute_demand,
        task_data_size=config.task_data_size,
        application_protocol=config.application_protocol,
        transport_protocol=config.transport_protocol,
        routing_protocol=config.routing_protocol,
        datalink_mac_protocol=config.datalink_mac_protocol,
        traffic_class=config.traffic_class,
        traffic_destination_type=config.traffic_destination_type,
        traffic_output_data_size=config.traffic_output_data_size,
        traffic_data_transfer_weight=config.traffic_data_transfer_weight,
        traffic_telemetry_weight=config.traffic_telemetry_weight,
        traffic_bulk_downlink_weight=config.traffic_bulk_downlink_weight,
        traffic_compute_service_weight=config.traffic_compute_service_weight,
        traffic_emergency_weight=config.traffic_emergency_weight,
        compute_cpu_gflops_fp64=config.compute_cpu_gflops_fp64,
        compute_gpu_tflops_fp32=config.compute_gpu_tflops_fp32,
        compute_gpu_tflops_fp16=config.compute_gpu_tflops_fp16,
        compute_npu_tops_int8=config.compute_npu_tops_int8,
        compute_memory_gb=config.compute_memory_gb,
        compute_storage_gb=config.compute_storage_gb,
        arrival_interval_seconds=config.flow_interval_seconds,
        orbit_altitude_m=config.orbit_altitude_m,
        orbit_inclination_deg=config.orbit_inclination_deg,
        phase_policy="SLOT_INDEX_PHASE_WITH_PLANE_OFFSET",
        runtime_mode=config.runtime_mode,
        runtime_speed_factor=config.runtime_speed_factor,
        runtime_duration_seconds=config.duration_seconds,
        runtime_seed=config.seed,
    )
    summary["fidelity_summary"] = _fidelity_summary(config)
    summary["workload_smoothing_summary"] = _workload_smoothing_summary(config)
    summary["configuration_surface_summary"] = build_user_configuration_view(
        demo_config_to_sees_config(config)
    )
    return summary


def _fidelity_summary(config: DemoConfig) -> dict[str, object]:
    return build_scale_fidelity_summary(
        ScaleFidelityConfig(
            satellite_count=config.satellite_count,
            user_count=config.ground_user_count,
            forced_orbit_update_mode=config.orbit_update_mode,
            forced_space_link_mode=config.space_link_mode,
            space_link_enabled=True,
            max_space_link_candidates_per_satellite=(
                config.max_space_link_candidates_per_satellite
            ),
            batch_space_link_update_limit=config.batch_space_link_update_limit,
        )
    )


def _scheduled_task_count(config: DemoConfig) -> int:
    ticks = range(0, config.duration_seconds, config.task_interval_seconds)
    traffic_class = TrafficClass(str(config.traffic_class))
    destination_type = TrafficDestinationType(str(config.traffic_destination_type))
    return len(tuple(ticks)) * len(
        _traffic_target_ids(config, traffic_class, destination_type)
    )


def _network_satellites(config: DemoConfig) -> tuple[SatelliteProfile, ...]:
    slot_count = config.duration_seconds // config.network_slot_seconds + 1
    return tuple(
        SatelliteProfile(
            satellite_id=f"sat-{satellite_index:03d}",
            coverage=tuple(
                CoverageSlot(
                    slot=slot,
                    cell_ids=(
                        _cell_id(config, satellite_index * 3 + slot * 7),
                        _cell_id(config, satellite_index * 3 + slot * 7 + 1),
                    ),
                )
                for slot in range(slot_count)
            ),
            link_latency=10.0 + float(satellite_index % 6),
            link_capacity=100.0 + float((satellite_index % 4) * 25),
        )
        for satellite_index in range(config.satellite_count)
    )


def _ground_users(config: DemoConfig) -> tuple[GroundUserProfile, ...]:
    return tuple(
        GroundUserProfile(
            user_id=f"user-{index:04d}",
            cell_id=_cell_id(config, index),
        )
        for index in range(config.ground_user_count)
    ) + tuple(
        GroundUserProfile(
            user_id=f"ground-station-{index:02d}",
            cell_id=_cell_id(config, index * 17),
        )
        for index in range(config.ground_station_count)
    )


def _ground_user_render_states(config: DemoConfig) -> tuple[GroundUserRenderState, ...]:
    users: list[GroundUserRenderState] = []
    total = config.ground_user_count + config.ground_station_count
    for index in range(total):
        is_station = index >= config.ground_user_count
        render_index = index - config.ground_user_count if is_station else index
        user_id = (
            f"ground-station-{render_index:02d}"
            if is_station
            else f"user-{index:04d}"
        )
        cell_index = render_index * 17 if is_station else index
        longitude = -170.0 + float((index * 37 + config.seed) % 340)
        latitude = -62.0 + float((index * 19 + config.seed) % 124)
        height = 0.0
        users.append(
            GroundUserRenderState(
                user_id=user_id,
                cell_id=_cell_id(config, cell_index),
                position=(longitude, latitude, height),
                status="GROUND_STATION" if is_station else "ACTIVE",
            )
        )
    return tuple(users)


def _ground_endpoints(
    users: tuple[GroundUserRenderState, ...],
) -> tuple[GroundEndpoint, ...]:
    return tuple(
        GroundEndpoint(
            endpoint_id=user.user_id,
            position=_ecef_km_from_geodetic(user.position),
            min_elevation_deg=_GROUND_ENDPOINT_MIN_ELEVATION_DEG,
            max_range_km=_GROUND_ENDPOINT_MAX_RANGE_KM,
        )
        for user in sorted(users, key=lambda item: item.user_id)
    )


def _ecef_km_from_geodetic(
    position: tuple[float, float, float],
) -> tuple[float, float, float]:
    longitude_deg, latitude_deg, height_m = position
    longitude = radians(longitude_deg)
    latitude = radians(latitude_deg)
    radius_km = _EARTH_RADIUS_KM + height_m / 1000.0
    cos_latitude = cos(latitude)
    return (
        radius_km * cos_latitude * cos(longitude),
        radius_km * cos_latitude * sin(longitude),
        radius_km * sin(latitude),
    )


def _compute_nodes(config: DemoConfig) -> tuple[ComputeNode, ...]:
    return tuple(
        ComputeNode(
            node_id=satellite_id,
            capacity=config.compute_capacity + float(index % 5) * 2.5,
            cpu_gflops_fp64=config.compute_cpu_gflops_fp64,
            gpu_tflops_fp32=config.compute_gpu_tflops_fp32,
            gpu_tflops_fp16=config.compute_gpu_tflops_fp16,
            npu_tops_int8=config.compute_npu_tops_int8,
            memory_gb=config.compute_memory_gb,
            storage_gb=config.compute_storage_gb,
        )
        for index, satellite_id in enumerate(_compute_node_satellite_ids(config))
    )


def _initial_events(
    config: DemoConfig,
    traffic_demand: TrafficDemandBatch | None = None,
) -> tuple[SimEvent, ...]:
    events: list[SimEvent] = []
    for tick in range(0, config.duration_seconds + 1, config.orbit_tick_seconds):
        events.append(
            SimEvent(
                event_id=f"scenario:orbit-trigger:{tick:04d}",
                sim_time=float(tick),
                priority=10,
                source="scenario",
                target="orbit",
                event_type=EventType.ORBIT_TRIGGER.value,
                payload=None,
            )
        )

    demand = traffic_demand if traffic_demand is not None else _traffic_demand_batch(config)
    task_event_index = 0
    for flow_index, record in enumerate(demand.records):
        events.append(
            SimEvent(
                event_id=f"scenario:flow-arrival:{flow_index:05d}",
                sim_time=record.arrival_time,
                priority=5,
                source="scenario",
                target="network",
                event_type=EventType.FLOW_ARRIVAL.value,
                payload=record.input_flow,
            )
        )
        if record.task is None:
            continue
        events.append(
            SimEvent(
                event_id=f"scenario:task-arrival:{task_event_index:05d}",
                sim_time=record.task.submit_time,
                priority=4,
                source="scenario",
                target="compute",
                event_type=EventType.TASK_ARRIVAL.value,
                payload=record.task,
            )
        )
        task_event_index += 1

    return tuple(
        sorted(
            events,
            key=lambda event: (event.sim_time, -event.priority, str(event.event_id)),
        )
    )


def _traffic_demand_batch(config: DemoConfig) -> TrafficDemandBatch:
    service_mix_weights = _traffic_service_mix_weights(config)
    if service_mix_weights is not None:
        return generate_traffic_service_mix(
            TrafficServiceMixConfig(
                items=tuple(
                    _traffic_service_mix_item(config, traffic_class, weight)
                    for traffic_class, weight in service_mix_weights
                ),
                total_request_count=_scheduled_task_count(config),
                arrival_interval=_service_mix_arrival_interval_s(config),
                start_time=0.15,
                id_prefix="demo-service",
            )
        )

    records: list[TrafficDemandRecord] = []
    flow_index = 0
    traffic_class = TrafficClass(str(config.traffic_class))
    destination_type = TrafficDestinationType(str(config.traffic_destination_type))
    target_ids = _traffic_target_ids(config, traffic_class, destination_type)
    spacing_s = _initial_workload_spacing_s(config, len(target_ids))
    for tick in range(0, config.duration_seconds, config.task_interval_seconds):
        for offset, target_id in enumerate(target_ids):
            flow_id = f"task-{flow_index:05d}"
            source_id = _traffic_source_id(config, traffic_class, flow_index)
            submit_time = float(tick) + 0.2 + offset * spacing_s
            deadline = (
                submit_time + 20.0
                if _workload_smoothing_active(config)
                else float(tick) + 20.0
            )
            input_flow = FlowRequest(
                flow_id=flow_id,
                source_id=source_id,
                target_id=target_id,
                demand_capacity=config.flow_demand_capacity,
            )
            task = (
                TaskRequest(
                    task_id=flow_id,
                    source_id=source_id,
                    submit_time=submit_time,
                    compute_demand=config.task_compute_demand + float(flow_index % 5),
                    data_size=config.task_data_size + float(flow_index % 3),
                    deadline=deadline,
                )
                if traffic_class == TrafficClass.COMPUTE_SERVICE
                else None
            )
            records.append(
                TrafficDemandRecord(
                    arrival_time=submit_time - 0.05,
                    traffic_class=traffic_class,
                    destination_type=destination_type,
                    input_data_size=config.flow_demand_capacity,
                    output_data_size=config.traffic_output_data_size,
                    input_flow=input_flow,
                    task=task,
                )
            )
            flow_index += 1
    return TrafficDemandBatch(records=tuple(records))


def _traffic_service_mix_weights(
    config: DemoConfig,
) -> tuple[tuple[TrafficClass, float], ...] | None:
    weights = (
        (TrafficClass.DATA_TRANSFER, config.traffic_data_transfer_weight),
        (TrafficClass.TELEMETRY, config.traffic_telemetry_weight),
        (TrafficClass.BULK_DOWNLINK, config.traffic_bulk_downlink_weight),
        (TrafficClass.COMPUTE_SERVICE, config.traffic_compute_service_weight),
        (TrafficClass.EMERGENCY, config.traffic_emergency_weight),
    )
    if sum(weight for _, weight in weights) <= 0.0:
        return None
    return tuple(
        (traffic_class, float(weight))
        for traffic_class, weight in weights
        if weight > 0.0
    )


def _traffic_service_mix_item(
    config: DemoConfig,
    traffic_class: TrafficClass,
    weight: float,
) -> TrafficServiceMixItem:
    destination_type = _service_mix_destination_type(traffic_class)
    return TrafficServiceMixItem(
        traffic_class=traffic_class,
        weight=weight,
        source_ids=_service_mix_source_ids(config, traffic_class),
        destination_ids=_traffic_target_ids(config, traffic_class, destination_type),
        input_data_size=config.flow_demand_capacity,
        output_data_size=(
            config.traffic_output_data_size
            if traffic_class
            in {TrafficClass.BULK_DOWNLINK, TrafficClass.COMPUTE_SERVICE}
            else 0.0
        ),
        priority=0,
        destination_type=destination_type,
        compute_demand=config.task_compute_demand,
        input_data_mb=config.task_data_size,
        output_data_mb=config.traffic_output_data_size,
        output_destination_ids=_ground_user_ids(config),
    )


def _service_mix_destination_type(
    traffic_class: TrafficClass,
) -> TrafficDestinationType:
    if traffic_class == TrafficClass.COMPUTE_SERVICE:
        return TrafficDestinationType.COMPUTE_NODE
    if traffic_class in {TrafficClass.TELEMETRY, TrafficClass.BULK_DOWNLINK}:
        return TrafficDestinationType.GROUND_ENDPOINT
    return TrafficDestinationType.SERVICE_ENDPOINT


def _service_mix_source_ids(
    config: DemoConfig,
    traffic_class: TrafficClass,
) -> tuple[str, ...]:
    if traffic_class in {TrafficClass.TELEMETRY, TrafficClass.BULK_DOWNLINK}:
        return tuple(f"sat-{index:03d}" for index in range(config.satellite_count))
    return _ground_user_ids(config)


def _ground_user_ids(config: DemoConfig) -> tuple[str, ...]:
    return tuple(f"user-{index:04d}" for index in range(config.ground_user_count))


def _service_mix_arrival_interval_s(config: DemoConfig) -> float:
    total_request_count = _scheduled_task_count(config)
    if total_request_count <= 1:
        return 0.001
    duration_window_s = max(0.001, float(config.duration_seconds) - 0.2)
    return max(0.001, duration_window_s / float(total_request_count - 1))


def _traffic_source_id(
    config: DemoConfig,
    traffic_class: TrafficClass,
    flow_index: int,
) -> str:
    if traffic_class in {TrafficClass.TELEMETRY, TrafficClass.BULK_DOWNLINK}:
        return f"sat-{flow_index % config.satellite_count:03d}"
    return f"user-{(flow_index * 13) % config.ground_user_count:04d}"


def _traffic_target_ids(
    config: DemoConfig,
    traffic_class: TrafficClass,
    destination_type: TrafficDestinationType,
) -> tuple[str, ...]:
    if traffic_class == TrafficClass.COMPUTE_SERVICE:
        return _compute_node_satellite_ids(config)
    if destination_type == TrafficDestinationType.SATELLITE:
        return tuple(f"sat-{index:03d}" for index in range(config.satellite_count))
    if destination_type == TrafficDestinationType.COMPUTE_NODE:
        return _compute_node_satellite_ids(config)
    if destination_type == TrafficDestinationType.GROUND_ENDPOINT:
        return _ground_endpoint_ids(config)
    return _service_endpoint_ids(config)


def _ground_endpoint_ids(config: DemoConfig) -> tuple[str, ...]:
    station_ids = tuple(
        f"ground-station-{index:02d}" for index in range(config.ground_station_count)
    )
    if station_ids:
        return station_ids
    return tuple(f"user-{index:04d}" for index in range(config.ground_user_count))


def _service_endpoint_ids(config: DemoConfig) -> tuple[str, ...]:
    return _ground_endpoint_ids(config)


def _compute_node_satellite_ids(config: DemoConfig) -> tuple[str, ...]:
    count = min(config.compute_node_count, config.satellite_count)
    return tuple(f"sat-{index:03d}" for index in range(count))


def _traffic_frontend_config(config: DemoConfig) -> dict[str, object]:
    traffic: dict[str, object] = {
        "flow_interval_seconds": config.flow_interval_seconds,
        "task_interval_seconds": config.task_interval_seconds,
        "flow_demand_capacity": config.flow_demand_capacity,
        "task_compute_demand": config.task_compute_demand,
        "task_data_size": config.task_data_size,
        "traffic_class": config.traffic_class,
        "destination_type": config.traffic_destination_type,
        "output_data_size": config.traffic_output_data_size,
        "data_transfer_weight": config.traffic_data_transfer_weight,
        "telemetry_weight": config.traffic_telemetry_weight,
        "bulk_downlink_weight": config.traffic_bulk_downlink_weight,
        "compute_service_weight": config.traffic_compute_service_weight,
        "emergency_weight": config.traffic_emergency_weight,
    }
    if _workload_smoothing_should_be_exposed(config):
        traffic.update(
            {
                "initial_workload_smoothing_enabled": _workload_smoothing_active(config),
                "initial_workload_window_s": _workload_smoothing_window_s(config),
                "max_initial_events_per_tick": config.max_initial_events_per_tick,
                "workload_smoothing_mode": _workload_smoothing_mode(config),
            }
        )
    return traffic


def _workload_smoothing_should_be_exposed(config: DemoConfig) -> bool:
    return (
        _workload_smoothing_active(config)
        or config.initial_workload_window_s > 0.0
        or config.max_initial_events_per_tick > 0
    )


def _workload_smoothing_summary(config: DemoConfig) -> dict[str, object]:
    workload_count = min(config.compute_node_count, config.satellite_count)
    return {
        "enabled": _workload_smoothing_active(config),
        "mode": _workload_smoothing_mode(config),
        "scale_triggered": _scale_workload_smoothing_required(config),
        "initial_workload_window_s": _workload_smoothing_window_s(config),
        "max_initial_events_per_tick": config.max_initial_events_per_tick,
        "workload_count": workload_count,
        "spacing_s": _initial_workload_spacing_s(config, workload_count),
    }


def _workload_smoothing_active(config: DemoConfig) -> bool:
    return (
        config.initial_workload_smoothing_enabled
        or _workload_smoothing_mode(config) != "NONE"
        or _scale_workload_smoothing_required(config)
    )


def _workload_smoothing_mode(config: DemoConfig) -> str:
    mode = str(config.workload_smoothing_mode)
    if mode != "NONE":
        return mode
    if config.initial_workload_smoothing_enabled or _scale_workload_smoothing_required(config):
        return "DETERMINISTIC_STAGGER"
    return "NONE"


def _scale_workload_smoothing_required(config: DemoConfig) -> bool:
    return (
        min(config.compute_node_count, config.satellite_count)
        >= _SCALE_WORKLOAD_SMOOTHING_NODE_THRESHOLD
    )


def _workload_smoothing_window_s(config: DemoConfig) -> float:
    if not _workload_smoothing_active(config):
        return 0.0
    if config.initial_workload_window_s > 0.0:
        return float(config.initial_workload_window_s)
    if config.task_interval_seconds <= 1:
        return 1.0
    return float(min(60, max(1, config.task_interval_seconds - 1)))


def _initial_workload_spacing_s(config: DemoConfig, workload_count: int) -> float:
    if not _workload_smoothing_active(config):
        return 0.01
    if workload_count <= 1:
        return 0.0
    spacing_s = _workload_smoothing_window_s(config) / float(workload_count - 1)
    if (
        config.workload_smoothing_mode == "RATE_LIMITED"
        and config.max_initial_events_per_tick > 0
    ):
        spacing_s = max(spacing_s, 2.0 / float(config.max_initial_events_per_tick))
    return max(0.001, spacing_s)


def _cell_id(config: DemoConfig, index: int) -> str:
    return f"cell-{index % config.cell_count:03d}"
