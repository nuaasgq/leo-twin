from __future__ import annotations

from leo_twin.core import SimulationKernel
from leo_twin.models.network import GroundEndpoint, PositionDrivenNetworkEngine
from leo_twin.schema import EventType, SatelliteState, SimEvent
from leo_twin.services.metrics import MetricsCollector


SATELLITE_COUNT = 1000
EARTH_RADIUS_KM = 6371.0


def test_position_driven_network_scale_smoke_is_deterministic() -> None:
    first = _run_scale_smoke(SATELLITE_COUNT)
    second = _run_scale_smoke(SATELLITE_COUNT)

    assert first == second
    assert first["processed_events"] == 3000
    assert first["active_links"] == SATELLITE_COUNT
    assert first["metrics_event_count"] == 2000
    assert first["available_link_capacity"] == SATELLITE_COUNT * 10.0


def _run_scale_smoke(satellite_count: int) -> dict[str, float | int]:
    kernel = SimulationKernel()
    network = PositionDrivenNetworkEngine(
        endpoints=(
            GroundEndpoint(
                endpoint_id="user-east",
                position=(EARTH_RADIUS_KM, 0.0, 0.0),
                min_elevation_deg=10.0,
                max_range_km=2000.0,
            ),
        ),
        compute_node_ids=("node-a",),
        link_capacity=10.0,
        cell_size_km=1000.0,
    )
    metrics = MetricsCollector()
    kernel.register_module(network)
    kernel.register_module(metrics)

    for index in range(satellite_count):
        kernel.schedule_event(
            SimEvent(
                event_id=f"orbit-{index:05d}",
                sim_time=0.0,
                priority=0,
                source="orbit",
                target="network",
                event_type=EventType.ORBIT_UPDATE.value,
                payload=SatelliteState(
                    satellite_id=f"sat-{index:05d}",
                    sim_time=0.0,
                    position=(7000.0, 0.0, 0.0),
                    velocity=(0.0, 0.0, 0.0),
                    status="ACTIVE",
                ),
            )
        )

    processed = kernel.run()
    summary = metrics.summary()
    return {
        "active_links": len(network.compute_access()),
        "available_link_capacity": float(summary["available_link_capacity"]),
        "metrics_event_count": int(summary["event_count"]),
        "processed_events": len(processed),
    }
