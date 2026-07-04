"""Deterministic scenario construction for the integration demo."""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, pi, radians, sin

from leo_twin.models.compute import ComputeNode
from leo_twin.models.network import GroundEndpoint
from leo_twin.models.orbit import AutoPlaneAllocator, ConstellationAllocation, OrbitSatelliteConfig
from leo_twin.services.derived_summary import build_backend_derived_summary
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

from examples.integration_demo.config import DemoConfig


_EARTH_RADIUS_KM = 6371.0
_GROUND_ENDPOINT_MIN_ELEVATION_DEG = 10.0
_GROUND_ENDPOINT_MAX_RANGE_KM = 2500.0


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
    initial_events = _initial_events(config)
    backend_summary = _backend_summary(config, constellation_allocation)
    return DemoScenario(
        orbit_satellites=orbit_satellites,
        orbit_elements=orbit_elements,
        network_satellites=network_satellites,
        ground_users=ground_users,
        ground_user_render_states=render_users,
        ground_endpoints=ground_endpoints,
        compute_nodes=compute_nodes,
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
                "compute_scheduling_policy": config.compute_scheduling_policy,
                "orbit": {
                    "update_interval_seconds": config.orbit_tick_seconds,
                    "plane_count": constellation_allocation.plane_count,
                    "altitude_m": config.orbit_altitude_m,
                    "inclination_deg": config.orbit_inclination_deg,
                },
                "traffic_model": {
                    "flow_interval_seconds": config.flow_interval_seconds,
                    "task_interval_seconds": config.task_interval_seconds,
                    "flow_demand_capacity": config.flow_demand_capacity,
                    "task_compute_demand": config.task_compute_demand,
                    "task_data_size": config.task_data_size,
                },
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
            },
            "runtime": {
                "mode": "REAL_TIME",
                "speed_factor": 1.0,
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
    return build_backend_derived_summary(
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
        arrival_interval_seconds=config.flow_interval_seconds,
    )


def _scheduled_task_count(config: DemoConfig) -> int:
    ticks = range(0, config.duration_seconds, config.task_interval_seconds)
    return len(tuple(ticks)) * min(config.compute_node_count, config.satellite_count)


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
        )
        for index, satellite_id in enumerate(_compute_node_satellite_ids(config))
    )


def _initial_events(config: DemoConfig) -> tuple[SimEvent, ...]:
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

    task_index = 0
    compute_node_ids = _compute_node_satellite_ids(config)
    for tick in range(0, config.duration_seconds, config.task_interval_seconds):
        for offset, target_id in enumerate(compute_node_ids):
            task_id = f"task-{task_index:05d}"
            source_id = f"user-{(task_index * 13) % config.ground_user_count:04d}"
            submit_time = float(tick) + 0.2 + offset * 0.01
            events.append(
                SimEvent(
                    event_id=f"scenario:flow-arrival:{task_index:05d}",
                    sim_time=submit_time - 0.05,
                    priority=5,
                    source="scenario",
                    target="network",
                    event_type=EventType.FLOW_ARRIVAL.value,
                    payload=FlowRequest(
                        flow_id=task_id,
                        source_id=source_id,
                        target_id=target_id,
                        demand_capacity=config.flow_demand_capacity,
                    ),
                )
            )
            events.append(
                SimEvent(
                    event_id=f"scenario:task-arrival:{task_index:05d}",
                    sim_time=submit_time,
                    priority=4,
                    source="scenario",
                    target="compute",
                    event_type=EventType.TASK_ARRIVAL.value,
                    payload=TaskRequest(
                        task_id=task_id,
                        source_id=source_id,
                        submit_time=submit_time,
                        compute_demand=config.task_compute_demand + float(task_index % 5),
                        data_size=config.task_data_size + float(task_index % 3),
                        deadline=float(tick) + 20.0,
                    ),
                )
            )
            task_index += 1

    return tuple(sorted(events, key=lambda event: (event.sim_time, -event.priority, str(event.event_id))))


def _compute_node_satellite_ids(config: DemoConfig) -> tuple[str, ...]:
    count = min(config.compute_node_count, config.satellite_count)
    return tuple(f"sat-{index:03d}" for index in range(count))


def _cell_id(config: DemoConfig, index: int) -> str:
    return f"cell-{index % config.cell_count:03d}"
