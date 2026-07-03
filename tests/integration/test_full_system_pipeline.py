from leo_twin.core import SimulationKernel
from leo_twin.models.compute import ComputeEngine, ComputeNode
from leo_twin.models.network import NetworkEngine
from leo_twin.models.orbit import OrbitEngine, OrbitSatelliteConfig
from leo_twin.schema import (
    CoverageSlot,
    EventType,
    FlowRequest,
    GroundUserProfile,
    Route,
    SatelliteProfile,
    SimEvent,
    TaskRequest,
)
from leo_twin.services.metrics import MetricsCollector


def test_full_system_pipeline_is_event_driven_and_deterministic() -> None:
    first = _run_pipeline()
    second = _run_pipeline()

    assert first == second
    event_types = [event[5] for event in first["processed_events"]]
    assert EventType.ORBIT_UPDATE.value in event_types
    assert EventType.ACCESS_START.value in event_types
    assert EventType.LINK_UPDATE.value in event_types
    assert EventType.ROUTE_UPDATE.value in event_types
    assert EventType.TASK_START.value in event_types
    assert EventType.TASK_FINISH.value in event_types

    route_events = [
        event for event in first["processed_payloads"] if isinstance(event, Route)
    ]
    assert route_events == [
        Route(
            route_id="route:flow-1",
            flow_id="flow-1",
            path=("user-1", "sat-a", "user-2"),
            latency=20.0,
            capacity=100.0,
            available=True,
        ),
        Route(
            route_id="route:flow-1",
            flow_id="flow-1",
            path=("user-1", "sat-a", "user-2"),
            latency=20.0,
            capacity=100.0,
            available=True,
        ),
    ]

    summary = first["metrics_summary"]
    assert summary["unique_satellites"] == 1
    assert summary["active_links"] == 2
    assert summary["routes_total"] == 1
    assert summary["routes_available"] == 1
    assert summary["finished_tasks"] == 1
    assert summary["event_count"] >= 8
    assert first["metrics_csv"].startswith(
        "sim_time,metric_name,entity_id,value,tags\n"
    )
    assert first["summary_json"].endswith("\n")
    assert first["events_jsonl"].endswith("\n")


def _run_pipeline() -> dict[str, object]:
    kernel = SimulationKernel()
    orbit = OrbitEngine(
        satellites=(
            OrbitSatelliteConfig(
                satellite_id="sat-a",
                orbital_radius=10.0,
                angular_velocity=0.1,
            ),
        ),
        update_targets=("network", "metrics"),
    )
    network = NetworkEngine(
        satellites=(
            SatelliteProfile(
                satellite_id="sat-a",
                coverage=(CoverageSlot(slot=0, cell_ids=("cell-a",)),),
                link_latency=10.0,
                link_capacity=100.0,
            ),
        ),
        ground_users=(
            GroundUserProfile(user_id="user-1", cell_id="cell-a"),
            GroundUserProfile(user_id="user-2", cell_id="cell-a"),
        ),
        route_targets=("compute", "metrics"),
    )
    compute = ComputeEngine(nodes=(ComputeNode(node_id="node-a", capacity=20.0),))
    metrics = MetricsCollector()

    for module in (orbit, network, compute, metrics):
        kernel.register_module(module)

    kernel.schedule_event(
        SimEvent(
            event_id="scenario:orbit-trigger:0001",
            sim_time=0.0,
            priority=0,
            source="scenario",
            target="orbit",
            event_type=EventType.ORBIT_TRIGGER.value,
            payload=None,
        )
    )
    kernel.schedule_event(
        SimEvent(
            event_id="scenario:flow-arrival:0001",
            sim_time=0.1,
            priority=0,
            source="scenario",
            target="network",
            event_type=EventType.FLOW_ARRIVAL.value,
            payload=FlowRequest(
                flow_id="flow-1",
                source_id="user-1",
                target_id="user-2",
                demand_capacity=25.0,
            ),
        )
    )
    kernel.schedule_event(
        SimEvent(
            event_id="scenario:task-arrival:0001",
            sim_time=0.2,
            priority=0,
            source="scenario",
            target="compute",
            event_type=EventType.TASK_ARRIVAL.value,
            payload=TaskRequest(
                task_id="task-1",
                source_id="user-1",
                submit_time=0.2,
                compute_demand=10.0,
                data_size=1.0,
            ),
        )
    )

    processed = kernel.run()
    return {
        "processed_events": tuple(
            (
                event.event_id,
                event.sim_time,
                event.priority,
                event.source,
                event.target,
                event.event_type,
            )
            for event in processed
        ),
        "processed_payloads": tuple(event.payload for event in processed),
        "metrics_summary": metrics.summary(),
        "metrics_csv": metrics.metrics_csv(),
        "summary_json": metrics.summary_json(),
        "events_jsonl": metrics.events_jsonl(),
    }
