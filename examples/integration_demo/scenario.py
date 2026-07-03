"""Deterministic scenario construction for the integration demo."""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, pi, radians, sin

from leo_twin.models.compute import ComputeNode
from leo_twin.models.network import GroundEndpoint
from leo_twin.models.orbit import OrbitSatelliteConfig
from leo_twin.schema import (
    CoverageSlot,
    EventType,
    FlowRequest,
    GroundUserProfile,
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
    orbit_satellites = _orbit_satellites(config)
    network_satellites = _network_satellites(config)
    compute_nodes = _compute_nodes(config)
    initial_events = _initial_events(config)
    return DemoScenario(
        orbit_satellites=orbit_satellites,
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
                "compute_nodes": config.compute_node_count,
            },
            "network": {
                "transport_protocol": config.transport_protocol,
                "routing_protocol": config.routing_protocol,
                "carrier_frequency_hz": config.carrier_frequency_hz,
                "channel_bandwidth_hz": config.channel_bandwidth_hz,
                "rain_rate_mm_h": config.rain_rate_mm_h,
                "rain_attenuation_coefficient_db_per_km_per_mm_h": (
                    config.rain_attenuation_coefficient_db_per_km_per_mm_h
                ),
                "rain_effective_path_km": config.rain_effective_path_km,
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


def _orbit_satellites(config: DemoConfig) -> tuple[OrbitSatelliteConfig, ...]:
    planes = 12
    satellites_per_plane = max(1, config.satellite_count // planes)
    return tuple(
        OrbitSatelliteConfig(
            satellite_id=f"sat-{index:03d}",
            orbital_radius=6_900_000.0 + 1_000.0 * (index % satellites_per_plane),
            angular_velocity=0.001 + (index % 5) * 0.00001,
            phase=((index % satellites_per_plane) / satellites_per_plane) * 2.0 * pi,
            inclination=((index // satellites_per_plane) / planes) * 0.9,
        )
        for index in range(config.satellite_count)
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
            node_id=f"compute-{index:02d}",
            capacity=10.0 + float(index % 5) * 2.5,
        )
        for index in range(config.compute_node_count)
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
    for tick in range(0, config.duration_seconds, config.task_interval_seconds):
        for offset in range(config.compute_node_count):
            task_id = f"task-{task_index:05d}"
            source_id = f"user-{(task_index * 13) % config.ground_user_count:04d}"
            target_id = f"compute-{offset:02d}"
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
                        demand_capacity=25.0,
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
                        compute_demand=20.0 + float(task_index % 5),
                        data_size=2.0 + float(task_index % 3),
                        deadline=float(tick) + 20.0,
                    ),
                )
            )
            task_index += 1

    return tuple(sorted(events, key=lambda event: (event.sim_time, -event.priority, str(event.event_id))))


def _cell_id(config: DemoConfig, index: int) -> str:
    return f"cell-{index % config.cell_count:03d}"
