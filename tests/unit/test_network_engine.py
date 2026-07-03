from leo_twin.core import SimulationKernel, SimulationModule
from leo_twin.models import NetworkEngine
from leo_twin.schema import (
    CoverageSlot,
    FlowRequest,
    GroundUserProfile,
    Route,
    SatelliteProfile,
    SimEvent,
)


class RouteSink(SimulationModule):
    def __init__(self) -> None:
        self.routes: list[Route] = []

    def name(self) -> str:
        return "client"

    def on_event(self, event: SimEvent, kernel: SimulationKernel) -> None:
        if event.event_type == "ROUTE_UPDATE":
            self.routes.append(event.payload)


def _engine() -> NetworkEngine:
    return NetworkEngine(
        satellites=(
            SatelliteProfile(
                satellite_id="sat-b",
                coverage=(
                    CoverageSlot(slot=0, cell_ids=("cell-2",)),
                    CoverageSlot(slot=1, cell_ids=()),
                ),
                link_latency=20.0,
                link_capacity=50.0,
            ),
            SatelliteProfile(
                satellite_id="sat-a",
                coverage=(
                    CoverageSlot(slot=0, cell_ids=("cell-1", "cell-2")),
                    CoverageSlot(slot=1, cell_ids=("cell-2",)),
                ),
                link_latency=10.0,
                link_capacity=100.0,
            ),
        ),
        ground_users=(
            GroundUserProfile(user_id="user-2", cell_id="cell-2"),
            GroundUserProfile(user_id="user-1", cell_id="cell-1"),
        ),
    )


def _event(event_id: int, event_type: str, payload: object = None) -> SimEvent:
    return SimEvent(
        event_id=event_id,
        sim_time=0.0,
        priority=0,
        source="client",
        target="network",
        event_type=event_type,
        payload={} if payload is None else payload,
    )


def test_topology_update_is_deterministic() -> None:
    first = _engine()
    second = _engine()

    first_events = first.update_topology(0.0)
    second_events = second.update_topology(0.0)

    assert first.compute_access() == second.compute_access()
    assert [(event.event_type, event.payload) for event in first_events] == [
        (event.event_type, event.payload) for event in second_events
    ]
    assert first.compute_access() == (
        ("sat-a", "user-1"),
        ("sat-a", "user-2"),
        ("sat-b", "user-2"),
    )


def test_access_event_generation_for_start_and_end() -> None:
    engine = _engine()

    start_events = engine.update_topology(0.0)
    end_events = engine.update_topology(1.0)

    assert [event.event_type for event in start_events].count("ACCESS_START") == 3
    assert [event.event_type for event in start_events].count("LINK_UPDATE") == 3
    assert [event.event_type for event in end_events].count("ACCESS_END") == 2
    assert [event.event_type for event in end_events].count("LINK_UPDATE") == 2
    assert engine.compute_access() == (("sat-a", "user-2"),)


def test_routing_output_is_consistent() -> None:
    engine = _engine()
    engine.update_topology(0.0)
    request = FlowRequest(
        flow_id="flow-1",
        source_id="user-1",
        target_id="user-2",
        demand_capacity=25.0,
    )

    first = engine.route_flow(request)
    second = engine.route_flow(request)

    assert first == second
    assert first == Route(
        route_id="route:flow-1",
        flow_id="flow-1",
        path=("user-1", "sat-a", "user-2"),
        latency=20.0,
        capacity=100.0,
        available=True,
    )


def test_network_engine_integrates_with_simulation_kernel() -> None:
    kernel = SimulationKernel()
    engine = _engine()
    sink = RouteSink()
    kernel.register_module(engine)
    kernel.register_module(sink)
    kernel.schedule_event(_event(1, "NETWORK_UPDATE"))
    kernel.schedule_event(
        _event(
            2,
            "FLOW_ARRIVAL",
            FlowRequest(
                flow_id="flow-1",
                source_id="user-1",
                target_id="user-2",
                demand_capacity=25.0,
            ),
        )
    )

    processed = kernel.run()

    assert any(event.event_type == "LINK_UPDATE" for event in processed)
    assert sink.routes == [
        Route(
            route_id="route:flow-1",
            flow_id="flow-1",
            path=("user-1", "sat-a", "user-2"),
            latency=20.0,
            capacity=100.0,
            available=True,
        )
    ]
