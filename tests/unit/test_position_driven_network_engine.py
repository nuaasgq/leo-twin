from __future__ import annotations

import pytest

from leo_twin.core import SimulationKernel, SimulationModule
from leo_twin.models.network import (
    ChannelBudgetSelector,
    LinkBudgetCalculator,
    GroundEndpoint,
    PositionDrivenNetworkEngine,
    RadioTerminalProfile,
    RoutingRuntime,
    default_transport_runtime,
)
from leo_twin.schema import (
    AntennaProfile,
    ChannelProfile,
    EventType,
    FlowRequest,
    LinkMedium,
    LinkState,
    Route,
    RoutingProtocol,
    SatelliteState,
    SimEvent,
    TransportProtocol,
)


EARTH_RADIUS_KM = 6371.0


class MetricsSink(SimulationModule):
    def __init__(self) -> None:
        self.events: list[SimEvent] = []

    def name(self) -> str:
        return "metrics"

    def on_event(self, event: SimEvent, kernel: SimulationKernel) -> None:
        self.events.append(event)


class ComputeSink(SimulationModule):
    def __init__(self) -> None:
        self.routes: list[Route] = []

    def name(self) -> str:
        return "compute"

    def on_event(self, event: SimEvent, kernel: SimulationKernel) -> None:
        if event.event_type == EventType.ROUTE_UPDATE:
            self.routes.append(event.payload)


def _engine() -> PositionDrivenNetworkEngine:
    return PositionDrivenNetworkEngine(
        endpoints=(
            GroundEndpoint(
                endpoint_id="user-east",
                position=(EARTH_RADIUS_KM, 0.0, 0.0),
                min_elevation_deg=10.0,
                max_range_km=2000.0,
            ),
        ),
        compute_node_ids=("node-a",),
        link_capacity=50.0,
        propagation_speed_km_s=1000.0,
        cell_size_km=1000.0,
    )


def _budget_engine() -> PositionDrivenNetworkEngine:
    antenna = AntennaProfile(
        antenna_id="test-ant",
        gain_dbi=28.0,
        beam_width_deg=4.0,
        steering_mode="fixed",
    )
    budget = LinkBudgetCalculator(
        transmit_terminal=RadioTerminalProfile(
            terminal_id="sat-terminal",
            antenna=antenna,
            transmit_power_dbw=0.0,
        ),
        receive_terminal=RadioTerminalProfile(
            terminal_id="ground-terminal",
            antenna=antenna,
            transmit_power_dbw=0.0,
        ),
        channel=ChannelProfile(
            channel_id="budget-channel",
            medium=LinkMedium.SPACE_GROUND,
            carrier_frequency_hz=20_000_000_000.0,
            bandwidth_hz=100_000_000.0,
            loss_model_name="free_space_budget",
        ),
    )
    return PositionDrivenNetworkEngine(
        endpoints=(
            GroundEndpoint(
                endpoint_id="user-east",
                position=(EARTH_RADIUS_KM, 0.0, 0.0),
                min_elevation_deg=10.0,
                max_range_km=2000.0,
            ),
        ),
        compute_node_ids=("node-a",),
        link_capacity=10000.0,
        link_budget_calculator=budget,
        cell_size_km=1000.0,
    )


def _budget_for_medium(medium: LinkMedium) -> LinkBudgetCalculator:
    antenna = AntennaProfile(
        antenna_id=f"ant-{medium.value.lower()}",
        gain_dbi=30.0,
        beam_width_deg=4.0,
        steering_mode="fixed",
    )
    return LinkBudgetCalculator(
        transmit_terminal=RadioTerminalProfile(
            terminal_id=f"tx-{medium.value.lower()}",
            antenna=antenna,
            transmit_power_dbw=10.0,
        ),
        receive_terminal=RadioTerminalProfile(
            terminal_id=f"rx-{medium.value.lower()}",
            antenna=antenna,
            transmit_power_dbw=0.0,
        ),
        channel=ChannelProfile(
            channel_id=f"channel-{medium.value.lower()}",
            medium=medium,
            carrier_frequency_hz=20_000_000_000.0,
            bandwidth_hz=100_000_000.0,
            loss_model_name="free_space_budget",
        ),
    )


def _state(
    position: tuple[float, float, float],
    satellite_id: str = "sat-001",
) -> SatelliteState:
    return SatelliteState(
        satellite_id=satellite_id,
        sim_time=0.0,
        position=position,
        velocity=(0.0, 0.0, 0.0),
        status="ACTIVE",
    )


def _event(
    event_id: str,
    event_type: str,
    payload: object,
    dispatch_time: float = 0.0,
) -> SimEvent:
    return SimEvent(
        event_id=event_id,
        sim_time=dispatch_time,
        priority=0,
        source="scenario",
        target="network",
        event_type=event_type,
        payload=payload,
    )


def test_orbit_update_generates_access_start_and_link_update() -> None:
    kernel = SimulationKernel()
    network = _engine()
    metrics = MetricsSink()
    kernel.register_module(network)
    kernel.register_module(metrics)
    kernel.schedule_event(
        _event("orbit", EventType.ORBIT_UPDATE.value, _state((7000.0, 0.0, 0.0)))
    )

    kernel.run()

    assert [event.event_type for event in metrics.events] == [
        EventType.ACCESS_START.value,
        EventType.LINK_UPDATE.value,
    ]
    assert isinstance(metrics.events[0].payload, LinkState)
    assert network.compute_access()[0].satellite_id == "sat-001"


def test_position_loss_generates_access_end() -> None:
    kernel = SimulationKernel()
    network = _engine()
    metrics = MetricsSink()
    kernel.register_module(network)
    kernel.register_module(metrics)
    kernel.schedule_event(
        _event("orbit-1", EventType.ORBIT_UPDATE.value, _state((7000.0, 0.0, 0.0)))
    )
    kernel.schedule_event(
        _event("orbit-2", EventType.ORBIT_UPDATE.value, _state((0.0, 7000.0, 0.0)))
    )

    kernel.run()

    assert [event.event_type for event in metrics.events] == [
        EventType.ACCESS_START.value,
        EventType.LINK_UPDATE.value,
        EventType.ACCESS_END.value,
        EventType.LINK_UPDATE.value,
    ]
    assert network.compute_access() == ()


def test_flow_arrival_outputs_route_from_active_access() -> None:
    kernel = SimulationKernel()
    network = _engine()
    metrics = MetricsSink()
    compute = ComputeSink()
    kernel.register_module(network)
    kernel.register_module(metrics)
    kernel.register_module(compute)
    kernel.schedule_event(
        _event("orbit", EventType.ORBIT_UPDATE.value, _state((7000.0, 0.0, 0.0)))
    )
    kernel.schedule_event(
        _event(
            "flow",
            EventType.FLOW_ARRIVAL.value,
            FlowRequest(
                flow_id="flow-001",
                source_id="user-east",
                target_id="node-a",
                demand_capacity=10.0,
            ),
            1.0,
        )
    )

    kernel.run()

    assert len(compute.routes) == 1
    assert compute.routes[0].available is True
    assert compute.routes[0].path == ("user-east", "sat-001", "node-a")


def test_position_driven_engine_can_use_routing_runtime_and_static_links() -> None:
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
        link_capacity=50.0,
        propagation_speed_km_s=1000.0,
        cell_size_km=1000.0,
        routing_runtime=RoutingRuntime(RoutingProtocol.LINK_STATE),
        static_links=(LinkState("sat-001", "node-a", 2.0, 50.0, True),),
    )
    metrics = MetricsSink()
    compute = ComputeSink()
    kernel.register_module(network)
    kernel.register_module(metrics)
    kernel.register_module(compute)
    kernel.schedule_event(
        _event("orbit", EventType.ORBIT_UPDATE.value, _state((7000.0, 0.0, 0.0)))
    )
    kernel.schedule_event(
        _event(
            "flow",
            EventType.FLOW_ARRIVAL.value,
            FlowRequest("flow-001", "user-east", "node-a", 10.0),
            1.0,
        )
    )

    kernel.run()

    assert compute.routes[0].path == ("user-east", "sat-001", "node-a")
    assert compute.routes[0].latency == 2.629


def test_position_driven_engine_can_apply_transport_runtime_to_route() -> None:
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
        link_capacity=100.0,
        propagation_speed_km_s=1000.0,
        cell_size_km=1000.0,
        transport_runtime=default_transport_runtime(TransportProtocol.TCP),
    )
    metrics = MetricsSink()
    compute = ComputeSink()
    kernel.register_module(network)
    kernel.register_module(metrics)
    kernel.register_module(compute)
    kernel.schedule_event(
        _event("orbit", EventType.ORBIT_UPDATE.value, _state((7000.0, 0.0, 0.0)))
    )
    kernel.schedule_event(
        _event(
            "flow",
            EventType.FLOW_ARRIVAL.value,
            FlowRequest("flow-001", "user-east", "node-a", 10.0),
            1.0,
        )
    )

    kernel.run()

    assert compute.routes[0].latency == 1.258
    assert compute.routes[0].capacity == pytest.approx(89.546667)


def test_link_budget_limits_position_driven_link_capacity_and_latency() -> None:
    kernel = SimulationKernel()
    network = _budget_engine()
    metrics = MetricsSink()
    kernel.register_module(network)
    kernel.register_module(metrics)
    kernel.schedule_event(
        _event("orbit", EventType.ORBIT_UPDATE.value, _state((7000.0, 0.0, 0.0)))
    )

    kernel.run()

    link = network.active_link_states()[0]
    assert link.capacity < 10000.0
    assert link.capacity > 0.0
    assert link.latency < 0.01


def test_position_driven_engine_generates_space_link_update() -> None:
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
        link_capacity=50.0,
        propagation_speed_km_s=1000.0,
        cell_size_km=1000.0,
        space_link_max_range_km=1500.0,
        space_link_capacity=75.0,
    )
    metrics = MetricsSink()
    kernel.register_module(network)
    kernel.register_module(metrics)
    kernel.schedule_event(
        _event("orbit-a", EventType.ORBIT_UPDATE.value, _state((7000.0, 0.0, 0.0), "sat-001"))
    )
    kernel.schedule_event(
        _event("orbit-b", EventType.ORBIT_UPDATE.value, _state((8000.0, 0.0, 0.0), "sat-002"))
    )

    kernel.run()

    space_links = [
        event.payload
        for event in metrics.events
        if isinstance(event.payload, LinkState)
        and event.payload.source_id == "sat-001"
        and event.payload.target_id == "sat-002"
    ]
    assert space_links == [
        LinkState(
            source_id="sat-001",
            target_id="sat-002",
            latency=1.0,
            capacity=75.0,
            availability=True,
        )
    ]
    assert space_links[0] in network.active_link_states()


def test_position_driven_engine_ends_space_link_when_satellite_moves_out_of_range() -> None:
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
        link_capacity=50.0,
        propagation_speed_km_s=1000.0,
        cell_size_km=1000.0,
        space_link_max_range_km=1500.0,
    )
    metrics = MetricsSink()
    kernel.register_module(network)
    kernel.register_module(metrics)
    kernel.schedule_event(
        _event("orbit-a", EventType.ORBIT_UPDATE.value, _state((7000.0, 0.0, 0.0), "sat-001"))
    )
    kernel.schedule_event(
        _event("orbit-b", EventType.ORBIT_UPDATE.value, _state((8000.0, 0.0, 0.0), "sat-002"))
    )
    kernel.schedule_event(
        _event("orbit-b-far", EventType.ORBIT_UPDATE.value, _state((10000.0, 0.0, 0.0), "sat-002"), 1.0)
    )

    kernel.run()

    space_links = [
        event.payload
        for event in metrics.events
        if isinstance(event.payload, LinkState)
        and event.payload.source_id == "sat-001"
        and event.payload.target_id == "sat-002"
    ]
    assert [link.availability for link in space_links] == [True, False]
    assert all(
        not (link.source_id == "sat-001" and link.target_id == "sat-002")
        for link in network.active_link_states()
    )


def test_routing_runtime_uses_position_driven_space_link() -> None:
    kernel = SimulationKernel()
    network = PositionDrivenNetworkEngine(
        endpoints=(
            GroundEndpoint(
                endpoint_id="user-east",
                position=(EARTH_RADIUS_KM, 0.0, 0.0),
                min_elevation_deg=60.0,
                max_range_km=2000.0,
            ),
        ),
        compute_node_ids=("node-a",),
        link_capacity=100.0,
        propagation_speed_km_s=1000.0,
        cell_size_km=1000.0,
        routing_runtime=RoutingRuntime(RoutingProtocol.LINK_STATE),
        static_links=(LinkState("sat-002", "node-a", 2.0, 100.0, True),),
        space_link_max_range_km=1500.0,
        space_link_capacity=100.0,
    )
    metrics = MetricsSink()
    compute = ComputeSink()
    kernel.register_module(network)
    kernel.register_module(metrics)
    kernel.register_module(compute)
    kernel.schedule_event(
        _event("orbit-a", EventType.ORBIT_UPDATE.value, _state((7000.0, 0.0, 0.0), "sat-001"))
    )
    kernel.schedule_event(
        _event("orbit-b", EventType.ORBIT_UPDATE.value, _state((7000.0, 1000.0, 0.0), "sat-002"))
    )
    kernel.schedule_event(
        _event(
            "flow",
            EventType.FLOW_ARRIVAL.value,
            FlowRequest("flow-001", "user-east", "node-a", 10.0),
            1.0,
        )
    )

    kernel.run()

    assert compute.routes[0].available is True
    assert compute.routes[0].path == ("user-east", "sat-001", "sat-002", "node-a")
    assert compute.routes[0].latency == 3.629


def test_position_driven_space_link_uses_medium_budget_selector() -> None:
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
        link_capacity=10000.0,
        propagation_speed_km_s=1000.0,
        cell_size_km=1000.0,
        link_budget_selector=ChannelBudgetSelector(
            calculators=(_budget_for_medium(LinkMedium.SPACE_SPACE),)
        ),
        space_link_max_range_km=1500.0,
        space_link_capacity=10000.0,
    )
    metrics = MetricsSink()
    kernel.register_module(network)
    kernel.register_module(metrics)
    kernel.schedule_event(
        _event("orbit-a", EventType.ORBIT_UPDATE.value, _state((7000.0, 0.0, 0.0), "sat-001"))
    )
    kernel.schedule_event(
        _event("orbit-b", EventType.ORBIT_UPDATE.value, _state((8000.0, 0.0, 0.0), "sat-002"))
    )

    kernel.run()

    space_link = next(
        link
        for link in network.active_link_states()
        if link.source_id == "sat-001" and link.target_id == "sat-002"
    )
    assert space_link.latency == pytest.approx(0.003336, abs=1e-6)
    assert space_link.capacity < 10000.0


def test_position_driven_network_engine_is_deterministic() -> None:
    assert _run_scenario() == _run_scenario()


def _run_scenario() -> tuple[tuple[str, object], ...]:
    kernel = SimulationKernel()
    network = _engine()
    metrics = MetricsSink()
    compute = ComputeSink()
    kernel.register_module(network)
    kernel.register_module(metrics)
    kernel.register_module(compute)
    kernel.schedule_event(
        _event("orbit", EventType.ORBIT_UPDATE.value, _state((7000.0, 0.0, 0.0)))
    )
    kernel.schedule_event(
        _event(
            "flow",
            EventType.FLOW_ARRIVAL.value,
            FlowRequest("flow-001", "user-east", "node-a", 10.0),
            1.0,
        )
    )
    processed = kernel.run()
    return tuple((event.event_type, event.payload) for event in processed)
