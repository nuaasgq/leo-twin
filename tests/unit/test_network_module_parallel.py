from leo_twin.core import SimulationKernel, SimulationModule
from leo_twin.models.network import NetworkEngine
from leo_twin.schema import (
    AccessAssociation,
    CoverageSlot,
    FlowRequest,
    GroundUserProfile,
    LinkState,
    Route,
    SatelliteProfile,
    SatelliteState,
    SimEvent,
)


class EventSink(SimulationModule):
    def __init__(self, module_name: str) -> None:
        self._module_name = module_name
        self.events: list[SimEvent] = []

    def name(self) -> str:
        return self._module_name

    def on_event(self, event: SimEvent, kernel: SimulationKernel) -> None:
        self.events.append(event)


def _network() -> NetworkEngine:
    return NetworkEngine(
        satellites=(
            SatelliteProfile(
                satellite_id="sat-b",
                coverage=(
                    CoverageSlot(slot=0, cell_ids=("cell-2",)),
                    CoverageSlot(slot=1, cell_ids=("cell-3",)),
                    CoverageSlot(slot=2, cell_ids=("cell-3",)),
                ),
                link_latency=15.0,
                link_capacity=40.0,
            ),
            SatelliteProfile(
                satellite_id="sat-a",
                coverage=(
                    CoverageSlot(slot=0, cell_ids=("cell-1", "cell-2")),
                    CoverageSlot(slot=1, cell_ids=("cell-1", "cell-2")),
                    CoverageSlot(slot=2, cell_ids=("cell-1",)),
                ),
                link_latency=10.0,
                link_capacity=100.0,
            ),
        ),
        ground_users=(
            GroundUserProfile(user_id="user-1", cell_id="cell-1"),
            GroundUserProfile(user_id="user-2", cell_id="cell-2"),
            GroundUserProfile(user_id="user-3", cell_id="cell-3"),
            GroundUserProfile(user_id="user-4", cell_id="cell-4"),
        ),
    )


def _orbit_update(event_id: int, sim_time: float, satellite_id: str) -> SimEvent:
    return SimEvent(
        event_id=event_id,
        sim_time=sim_time,
        priority=0,
        source="orbit",
        target="network",
        event_type="ORBIT_UPDATE",
        payload=SatelliteState(
            satellite_id=satellite_id,
            sim_time=sim_time,
            position=(0.0, 0.0, 0.0),
            velocity=(0.0, 0.0, 0.0),
            status="active",
        ),
    )


def _flow_arrival(event_id: int, sim_time: float) -> SimEvent:
    return SimEvent(
        event_id=event_id,
        sim_time=sim_time,
        priority=0,
        source="scenario",
        target="network",
        event_type="FLOW_ARRIVAL",
        payload=FlowRequest(
            flow_id="flow-1",
            source_id="user-1",
            target_id="user-2",
            demand_capacity=25.0,
        ),
    )


def test_coverage_access_uses_configured_cells_only() -> None:
    network = _network()

    events = network.update_topology(0.0)

    assert network.compute_access() == (
        AccessAssociation(satellite_id="sat-a", user_id="user-1"),
        AccessAssociation(satellite_id="sat-a", user_id="user-2"),
        AccessAssociation(satellite_id="sat-b", user_id="user-2"),
    )
    assert AccessAssociation(satellite_id="sat-b", user_id="user-1") not in (
        network.compute_access()
    )
    assert AccessAssociation(satellite_id="sat-a", user_id="user-4") not in (
        network.compute_access()
    )
    assert [event.event_type for event in events].count("ACCESS_START") == 3
    assert [event.event_type for event in events].count("LINK_UPDATE") == 3
    assert network.active_link_states() == (
        LinkState(
            source_id="sat-a",
            target_id="user-1",
            latency=10.0,
            capacity=100.0,
            availability=True,
        ),
        LinkState(
            source_id="sat-a",
            target_id="user-2",
            latency=10.0,
            capacity=100.0,
            availability=True,
        ),
        LinkState(
            source_id="sat-b",
            target_id="user-2",
            latency=15.0,
            capacity=40.0,
            availability=True,
        ),
    )


def test_stable_coverage_does_not_emit_duplicate_link_updates() -> None:
    network = _network()

    first_events = network.update_topology(0.0)
    same_slot_events = network.update_topology(0.5)
    stable_next_slot_events = network.update_topology(1.0)
    changed_slot_events = network.update_topology(2.0)

    assert len(first_events) == 6
    assert same_slot_events == ()
    assert [event.event_type for event in stable_next_slot_events] == [
        "ACCESS_END",
        "LINK_UPDATE",
        "ACCESS_START",
        "LINK_UPDATE",
    ]
    assert stable_next_slot_events[0].payload == LinkState(
        source_id="sat-b",
        target_id="user-2",
        latency=15.0,
        capacity=40.0,
        availability=False,
    )
    assert stable_next_slot_events[2].payload == LinkState(
        source_id="sat-b",
        target_id="user-3",
        latency=15.0,
        capacity=40.0,
        availability=True,
    )
    assert [event.event_type for event in changed_slot_events] == [
        "ACCESS_END",
        "LINK_UPDATE",
    ]
    assert network.compute_access() == (
        AccessAssociation(satellite_id="sat-a", user_id="user-1"),
        AccessAssociation(satellite_id="sat-b", user_id="user-3"),
    )


def test_flow_arrival_emits_route_update_through_kernel_schedule_event() -> None:
    kernel = SimulationKernel()
    network = _network()
    compute = EventSink("compute")
    metrics = EventSink("metrics")
    kernel.register_module(network)
    kernel.register_module(compute)
    kernel.register_module(metrics)

    kernel.schedule_event(_orbit_update(1, 0.0, "sat-a"))
    kernel.schedule_event(_flow_arrival(2, 0.1))

    kernel.run()

    compute_routes = [
        event.payload for event in compute.events if event.event_type == "ROUTE_UPDATE"
    ]
    metrics_routes = [
        event.payload for event in metrics.events if event.event_type == "ROUTE_UPDATE"
    ]
    assert compute_routes == metrics_routes == [
        Route(
            route_id="route:flow-1",
            flow_id="flow-1",
            path=("user-1", "sat-a", "user-2"),
            latency=20.0,
            capacity=100.0,
            available=True,
        )
    ]
