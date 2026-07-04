from __future__ import annotations

import json

from leo_twin.schema import (
    ApplicationState,
    ChannelState,
    ComputeNodeState,
    FlowRequest,
    FlowState,
    GroundUserState,
    LinkState,
    MetricRecord,
    Route,
    RouteState,
    RuntimeConfigState,
    RuntimeMode,
    RuntimeStatus,
    SatelliteState,
    TaskRequest,
    TaskState,
    TransportState,
    WorldSnapshot,
)
from leo_twin.schema import network


def test_product_contracts_serialize_to_deterministic_json() -> None:
    snapshot = _snapshot()

    encoded = snapshot.to_json()
    decoded = json.loads(encoded)

    assert decoded["runtime"]["mode"] == "ACCELERATED"
    assert decoded["runtime"]["status"] == "RUNNING"
    assert decoded["satellites"][0]["satellite_id"] == "sat-a"
    assert decoded["satellites"][1]["satellite_id"] == "sat-b"
    assert decoded["links"][0]["link_id"] == "sat-a->sat-b"
    assert decoded["routes"][0]["route_id"] == "route-a"
    assert encoded == snapshot.to_json()
    assert decoded == json.loads(
        json.dumps(snapshot.to_dict(), ensure_ascii=False, sort_keys=True)
    )


def test_world_snapshot_orders_state_collections_deterministically() -> None:
    snapshot = _snapshot()

    assert tuple(state.satellite_id for state in snapshot.satellites) == ("sat-a", "sat-b")
    assert tuple(user.user_id for user in snapshot.ground_users) == ("user-a", "user-b")
    assert tuple(link.link_id for link in snapshot.links) == (
        "sat-a->sat-b",
        "sat-a->user-a",
    )
    assert tuple(metric.metric_name for metric in snapshot.metrics) == (
        "alpha",
        "beta",
    )


def test_backward_compatibility_aliases_use_canonical_contracts() -> None:
    assert Route is RouteState
    assert network.Route is RouteState
    assert network.LinkState is LinkState
    assert network.FlowRequest is FlowRequest

    old_route = Route(
        route_id="route-legacy",
        flow_id="flow-a",
        path=("user-a", "sat-a", "compute-a"),
        latency=1.0,
        capacity=10.0,
        available=True,
    )
    old_link = network.LinkState("sat-a", "user-a", 0.1, 50.0, True)
    old_flow = network.FlowRequest("flow-a", "user-a", "compute-a", 10.0)

    assert isinstance(old_route, RouteState)
    assert old_link.link_id == "sat-a->user-a"
    assert old_flow.demand_capacity == 10.0


def test_product_contracts_cover_required_runtime_domains() -> None:
    required = (
        SatelliteState,
        ChannelState,
        LinkState,
        RouteState,
        FlowRequest,
        FlowState,
        TaskRequest,
        TaskState,
        TransportState,
        ApplicationState,
        WorldSnapshot,
    )

    assert all(hasattr(contract, "__dataclass_fields__") for contract in required)


def _snapshot() -> WorldSnapshot:
    return WorldSnapshot(
        timestamp=1000.0,
        reducer_version=2,
        last_sim_time=12.0,
        event_count=42,
        satellites=(
            SatelliteState(
                satellite_id="sat-b",
                sim_time=12.0,
                position=(2.0, 0.0, 0.0),
                velocity=(0.0, 1.0, 0.0),
                status="ACTIVE",
            ),
            SatelliteState(
                satellite_id="sat-a",
                sim_time=12.0,
                position=(1.0, 0.0, 0.0),
                velocity=(0.0, 1.0, 0.0),
                status="ACTIVE",
            ),
        ),
        ground_users=(
            GroundUserState(user_id="user-b", position=(120.0, 30.0, 0.0), cell_id="cell-b"),
            GroundUserState(user_id="user-a", position=(121.0, 31.0, 0.0), cell_id="cell-a"),
        ),
        channels=(
            ChannelState(
                channel_id="channel-a",
                sim_time=12.0,
                source_id="sat-a",
                target_id="user-a",
                medium="SPACE_GROUND",
                carrier_frequency_hz=20_000_000_000.0,
                bandwidth_hz=100_000_000.0,
                availability=True,
                attenuation_db=1.5,
                snr_db=12.0,
            ),
        ),
        links=(
            LinkState("sat-a", "user-a", 0.02, 100.0, True, channel_id="channel-a"),
            LinkState("sat-a", "sat-b", 0.01, 200.0, True),
        ),
        routes=(
            RouteState(
                route_id="route-a",
                flow_id="flow-a",
                path=("user-a", "sat-a", "compute-a"),
                latency=0.08,
                capacity=50.0,
                available=True,
                routing_protocol="LINK_STATE",
            ),
        ),
        flows=(
            FlowState(
                flow_id="flow-a",
                route_id="route-a",
                source_id="user-a",
                target_id="compute-a",
                status="ROUTED",
                route_path=("user-a", "sat-a", "compute-a"),
                latency=0.08,
                capacity=50.0,
            ),
        ),
        transport=(
            TransportState(
                flow_id="flow-a",
                sim_time=12.0,
                protocol="TCP",
                status="OPEN",
                loss_rate=0.01,
                congestion_window_segments=32,
            ),
        ),
        applications=(
            ApplicationState(
                flow_id="flow-a",
                sim_time=12.0,
                protocol="TASK_OFFLOAD_FLOW",
                status="READY",
                demand_capacity=25.0,
                source_id="user-a",
                target_id="compute-a",
            ),
        ),
        compute_nodes=(
            ComputeNodeState(
                node_id="compute-a",
                sim_time=12.0,
                capacity=100.0,
                available_capacity=60.0,
                status="BUSY",
                load_ratio=0.4,
            ),
        ),
        active_tasks=(
            TaskState(
                task_id="task-a",
                node_id="compute-a",
                sim_time=12.0,
                progress=0.5,
                status="RUNNING",
                flow_id="flow-a",
            ),
        ),
        metrics=(
            MetricRecord(
                metric_name="beta",
                sim_time=12.0,
                entity_id="sat-a",
                value=2.0,
                tags=(("z", "1"), ("a", "1")),
            ),
            MetricRecord(
                metric_name="alpha",
                sim_time=12.0,
                entity_id="sat-a",
                value=1.0,
            ),
        ),
        runtime=RuntimeConfigState(
            mode=RuntimeMode.ACCELERATED,
            speed_factor=10.0,
            seed=20260704,
            duration=600.0,
            status=RuntimeStatus.RUNNING,
            config_version=3,
        ),
        active_route_id="route-a",
    )
