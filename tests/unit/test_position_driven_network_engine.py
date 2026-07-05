from __future__ import annotations

import pytest

from leo_twin.core import SimulationKernel, SimulationModule
from leo_twin.models.compute import COMPUTE_NODE_UPDATE
from leo_twin.models.network import (
    ChannelBudgetSelector,
    LinkBudgetCalculator,
    GroundEndpoint,
    NetworkStackRuntime,
    PositionDrivenNetworkEngine,
    RadioTerminalProfile,
    RoutingRuntime,
    SpaceLinkMode,
    build_default_leo_protocol_stack,
    default_application_runtime,
    default_data_link_runtime,
    default_transport_runtime,
)
from leo_twin.schema import (
    AntennaProfile,
    ApplicationProtocol,
    ChannelProfile,
    ComputeNodeState,
    DataLinkProtocol,
    EventType,
    FlowRequest,
    FlowState,
    LinkMedium,
    LinkState,
    NetworkLayer,
    OrbitBatchState,
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


def _pointing_budget_engine(steering_mode: str) -> PositionDrivenNetworkEngine:
    antenna = AntennaProfile(
        antenna_id=f"pointing-ant-{steering_mode}",
        gain_dbi=28.0,
        beam_width_deg=4.0,
        steering_mode=steering_mode,
    )
    budget = LinkBudgetCalculator(
        transmit_terminal=RadioTerminalProfile(
            terminal_id=f"sat-terminal-{steering_mode}",
            antenna=antenna,
            transmit_power_dbw=0.0,
        ),
        receive_terminal=RadioTerminalProfile(
            terminal_id=f"ground-terminal-{steering_mode}",
            antenna=antenna,
            transmit_power_dbw=0.0,
        ),
        channel=ChannelProfile(
            channel_id=f"pointing-channel-{steering_mode}",
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
                max_range_km=2500.0,
            ),
        ),
        compute_node_ids=("node-a",),
        link_capacity=1_000_000.0,
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


def test_meter_position_input_can_be_scaled_to_kilometer_geometry() -> None:
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
        position_scale_to_km=0.001,
    )
    metrics = MetricsSink()
    kernel.register_module(network)
    kernel.register_module(metrics)
    kernel.schedule_event(
        _event("orbit-meters", EventType.ORBIT_UPDATE.value, _state((7_000_000.0, 0.0, 0.0)))
    )

    kernel.run()

    assert [event.event_type for event in metrics.events] == [
        EventType.ACCESS_START.value,
        EventType.LINK_UPDATE.value,
    ]
    assert network.compute_access()[0].satellite_id == "sat-001"
    assert network.active_link_states()[0].latency == pytest.approx(0.629)


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

    processed = kernel.run()

    assert len(compute.routes) == 1
    assert compute.routes[0].available is True
    assert compute.routes[0].path == ("user-east", "sat-001", "node-a")
    completed = [
        event
        for event in metrics.events
        if event.event_type == EventType.FLOW_COMPLETE
    ]
    assert len(completed) == 1
    assert completed[0].sim_time == pytest.approx(1.0 + compute.routes[0].latency)
    assert completed[0].target == "metrics"
    route_metric_index = next(
        index
        for index, event in enumerate(processed)
        if event.event_type == EventType.ROUTE_UPDATE and event.target == "metrics"
    )
    complete_index = next(
        index
        for index, event in enumerate(processed)
        if event.event_type == EventType.FLOW_COMPLETE and event.target == "metrics"
    )
    assert processed[route_metric_index].sim_time <= processed[complete_index].sim_time
    assert completed[0].payload == FlowState(
        flow_id="flow-001",
        route_id="route:flow-001",
        source_id="user-east",
        target_id="node-a",
        status="complete",
        route_path=("user-east", "sat-001", "node-a"),
        latency=compute.routes[0].latency,
        capacity=10.0,
    )


def test_concurrent_flows_emit_link_pressure_and_release_updates() -> None:
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
            "flow-a",
            EventType.FLOW_ARRIVAL.value,
            FlowRequest("flow-a", "user-east", "node-a", 30.0),
            1.0,
        )
    )
    kernel.schedule_event(
        _event(
            "flow-b",
            EventType.FLOW_ARRIVAL.value,
            FlowRequest("flow-b", "user-east", "node-a", 30.0),
            1.0,
        )
    )

    kernel.run()

    assert len(compute.routes) == 2
    assert compute.routes[0].loss_rate == 0.0
    assert compute.routes[1].loss_rate == pytest.approx(0.1)
    assert compute.routes[1].latency > compute.routes[0].latency
    link_utilizations = [
        event.payload.utilization
        for event in metrics.events
        if event.event_type == EventType.LINK_UPDATE
        and isinstance(event.payload, LinkState)
        and event.payload.utilization is not None
    ]
    assert link_utilizations == pytest.approx([0.6, 1.0, 0.6, 0.0])


def test_application_runtime_changes_route_availability_through_flow_demand() -> None:
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
        link_capacity=20.0,
        propagation_speed_km_s=1000.0,
        cell_size_km=1000.0,
        application_runtime=default_application_runtime(ApplicationProtocol.HTTP),
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
            FlowRequest("flow-001", "user-east", "node-a", 18.0),
            1.0,
        )
    )

    kernel.run()

    assert compute.routes[0].available is False
    assert compute.routes[0].path == ()
    completed = [
        event
        for event in metrics.events
        if event.event_type == EventType.FLOW_COMPLETE
    ]
    assert len(completed) == 1
    assert completed[0].sim_time == pytest.approx(1.0)
    assert completed[0].payload == FlowState(
        flow_id="flow-001",
        route_id="route:flow-001",
        source_id="user-east",
        target_id="node-a",
        status="blocked",
        route_path=(),
        latency=None,
        capacity=0.0,
    )


def test_active_flow_reroutes_when_access_link_ends() -> None:
    kernel = SimulationKernel()
    network = _engine()
    metrics = MetricsSink()
    compute = ComputeSink()
    kernel.register_module(network)
    kernel.register_module(metrics)
    kernel.register_module(compute)
    kernel.schedule_event(
        _event("orbit-1", EventType.ORBIT_UPDATE.value, _state((7000.0, 0.0, 0.0)))
    )
    kernel.schedule_event(
        _event(
            "flow",
            EventType.FLOW_ARRIVAL.value,
            FlowRequest("flow-001", "user-east", "node-a", 10.0),
            1.0,
        )
    )
    kernel.schedule_event(
        _event("orbit-2", EventType.ORBIT_UPDATE.value, _state((0.0, 7000.0, 0.0)), 2.0)
    )

    kernel.run()

    assert [route.available for route in compute.routes] == [True, False]
    assert compute.routes[0].path == ("user-east", "sat-001", "node-a")
    assert compute.routes[1].path == ()


def test_active_flow_is_not_rerouted_without_link_delta() -> None:
    kernel = SimulationKernel()
    network = _engine()
    metrics = MetricsSink()
    compute = ComputeSink()
    kernel.register_module(network)
    kernel.register_module(metrics)
    kernel.register_module(compute)
    kernel.schedule_event(
        _event("orbit-1", EventType.ORBIT_UPDATE.value, _state((7000.0, 0.0, 0.0)))
    )
    kernel.schedule_event(
        _event(
            "flow",
            EventType.FLOW_ARRIVAL.value,
            FlowRequest("flow-001", "user-east", "node-a", 10.0),
            1.0,
        )
    )
    kernel.schedule_event(
        _event("orbit-2", EventType.ORBIT_UPDATE.value, _state((7000.0, 0.0, 0.0)), 2.0)
    )

    kernel.run()

    assert len(compute.routes) == 1
    assert compute.routes[0].available is True


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


def test_compute_node_update_reroutes_active_flows_with_capacity_feedback() -> None:
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
        routing_runtime=RoutingRuntime(RoutingProtocol.LINK_STATE),
        static_links=(LinkState("user-east", "node-a", 0.5, 100.0, True),),
    )
    compute = ComputeSink()
    metrics = MetricsSink()
    kernel.register_module(network)
    kernel.register_module(compute)
    kernel.register_module(metrics)
    kernel.schedule_event(
        _event(
            "flow",
            EventType.FLOW_ARRIVAL.value,
            FlowRequest("flow-001", "user-east", "node-a", 50.0),
        )
    )
    kernel.schedule_event(
        _event(
            "node-busy",
            COMPUTE_NODE_UPDATE,
            ComputeNodeState(
                node_id="node-a",
                sim_time=1.0,
                capacity=100.0,
                available_capacity=20.0,
                status="BUSY",
            ),
            1.0,
        )
    )
    kernel.schedule_event(
        _event(
            "node-idle",
            COMPUTE_NODE_UPDATE,
            ComputeNodeState(
                node_id="node-a",
                sim_time=2.0,
                capacity=100.0,
                available_capacity=100.0,
                status="IDLE",
            ),
            2.0,
        )
    )

    kernel.run()

    assert [route.available for route in compute.routes] == [True, False, True]
    assert [route.capacity for route in compute.routes] == [100.0, 0.0, 100.0]


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


def test_position_driven_engine_can_apply_data_link_runtime_to_route() -> None:
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
        data_link_runtime=default_data_link_runtime(DataLinkProtocol.SLOTTED_ALOHA),
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

    assert compute.routes[0].latency == pytest.approx(0.638)
    assert compute.routes[0].capacity == pytest.approx(
        100.0 * 0.62 * (1.0 - 22.0 / 1522.0) * 0.92
    )
    assert compute.routes[0].available is True


def test_position_driven_engine_records_protocol_stack_trace_for_routed_flow() -> None:
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
        stack_runtime=NetworkStackRuntime(build_default_leo_protocol_stack()),
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

    trace = network.stack_trace_for_flow("flow-001")
    assert trace is not None
    assert trace.route_id == compute.routes[0].route_id
    assert trace.available is True
    assert trace.transport_protocol == "TCP"
    assert tuple(layer.layer for layer in trace.layers) == (
        NetworkLayer.APPLICATION,
        NetworkLayer.TRANSPORT,
        NetworkLayer.NETWORK,
        NetworkLayer.DATA_LINK,
        NetworkLayer.PHYSICAL,
        NetworkLayer.CHANNEL,
    )
    assert trace.layers[2].status == "OK"
    assert network.stack_traces() == (trace,)


def test_position_driven_stack_trace_updates_after_reroute() -> None:
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
        stack_runtime=NetworkStackRuntime(build_default_leo_protocol_stack()),
    )
    metrics = MetricsSink()
    compute = ComputeSink()
    kernel.register_module(network)
    kernel.register_module(metrics)
    kernel.register_module(compute)
    kernel.schedule_event(
        _event("orbit-1", EventType.ORBIT_UPDATE.value, _state((7000.0, 0.0, 0.0)))
    )
    kernel.schedule_event(
        _event(
            "flow",
            EventType.FLOW_ARRIVAL.value,
            FlowRequest("flow-001", "user-east", "node-a", 10.0),
            1.0,
        )
    )
    kernel.schedule_event(
        _event("orbit-2", EventType.ORBIT_UPDATE.value, _state((0.0, 7000.0, 0.0)), 2.0)
    )

    kernel.run()

    trace = network.stack_trace_for_flow("flow-001")
    assert trace is not None
    assert [route.available for route in compute.routes] == [True, False]
    assert trace.available is False
    assert trace.layers[2].status == "UNAVAILABLE"


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


def test_position_driven_budget_applies_fixed_antenna_pointing_loss() -> None:
    low_elevation_state = _state((7000.0, 1000.0, 0.0))

    fixed_link = _link_after_orbit_update(
        _pointing_budget_engine("fixed"),
        low_elevation_state,
    )
    tracking_link = _link_after_orbit_update(
        _pointing_budget_engine("electronic"),
        low_elevation_state,
    )

    assert fixed_link.latency == pytest.approx(tracking_link.latency)
    assert fixed_link.capacity < tracking_link.capacity


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


def test_position_driven_engine_skips_zero_distance_space_links() -> None:
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
        cell_size_km=1000.0,
        link_budget_selector=ChannelBudgetSelector(
            calculators=(_budget_for_medium(LinkMedium.SPACE_SPACE),)
        ),
        space_link_max_range_km=1500.0,
    )
    metrics = MetricsSink()
    kernel.register_module(network)
    kernel.register_module(metrics)
    kernel.schedule_event(
        _event("orbit-a", EventType.ORBIT_UPDATE.value, _state((7000.0, 0.0, 0.0), "sat-001"))
    )
    kernel.schedule_event(
        _event("orbit-b", EventType.ORBIT_UPDATE.value, _state((7000.0, 0.0, 0.0), "sat-002"))
    )

    kernel.run()

    assert all(
        not (
            isinstance(event.payload, LinkState)
            and event.payload.source_id == "sat-001"
            and event.payload.target_id == "sat-002"
        )
        for event in metrics.events
    )


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


def test_space_link_update_threshold_suppresses_small_changes() -> None:
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
        space_link_update_latency_epsilon_s=0.01,
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
        _event("orbit-b-small", EventType.ORBIT_UPDATE.value, _state((8000.005, 0.0, 0.0), "sat-002"), 1.0)
    )

    kernel.run()

    space_links = _space_link_payloads(metrics.events)
    assert [link.latency for link in space_links] == [1.0]


def test_space_link_update_threshold_allows_significant_changes() -> None:
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
        space_link_update_latency_epsilon_s=0.01,
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
        _event("orbit-b-large", EventType.ORBIT_UPDATE.value, _state((8050.0, 0.0, 0.0), "sat-002"), 1.0)
    )

    kernel.run()

    space_links = _space_link_payloads(metrics.events)
    assert [link.latency for link in space_links] == [1.0, 1.05]


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


def test_routing_runtime_does_not_use_unrelated_ground_users_as_transit() -> None:
    network = PositionDrivenNetworkEngine(
        endpoints=(
            GroundEndpoint(
                endpoint_id="user-east",
                position=(EARTH_RADIUS_KM, 0.0, 0.0),
                min_elevation_deg=10.0,
                max_range_km=2000.0,
            ),
            GroundEndpoint(
                endpoint_id="user-relay",
                position=(EARTH_RADIUS_KM, 0.0, 0.0),
                min_elevation_deg=10.0,
                max_range_km=2000.0,
            ),
        ),
        compute_node_ids=("node-a",),
        link_capacity=100.0,
        propagation_speed_km_s=1000.0,
        cell_size_km=1000.0,
        routing_runtime=RoutingRuntime(RoutingProtocol.LINK_STATE),
        static_links=(LinkState("sat-002", "node-a", 2.0, 100.0, True),),
    )
    network._active_links = {
        ("sat-001", "user-east"): LinkState("sat-001", "user-east", 0.5, 100.0, True),
        ("sat-001", "user-relay"): LinkState("sat-001", "user-relay", 0.5, 100.0, True),
        ("sat-002", "user-relay"): LinkState("sat-002", "user-relay", 0.5, 100.0, True),
    }

    route = network.route_flow(FlowRequest("flow-001", "user-east", "node-a", 10.0))

    assert route.available is False
    assert "user-relay" not in route.path


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


def test_bounded_candidate_space_link_mode_caps_candidates() -> None:
    candidate_counts, space_links = _bounded_space_link_result(
        satellite_count=12,
        max_candidates=2,
    )

    assert len(candidate_counts) == 12
    assert all(count <= 2 for count in candidate_counts.values())
    assert all(count > 0 for count in candidate_counts.values())
    assert len(space_links) <= 12 * 2
    assert len(space_links) < (12 * 11) // 2


def test_bounded_candidate_space_link_mode_is_deterministic() -> None:
    assert _bounded_space_link_result(
        satellite_count=12,
        max_candidates=3,
    ) == _bounded_space_link_result(
        satellite_count=12,
        max_candidates=3,
    )


def test_detailed_small_scale_space_link_batch_mode_remains_available() -> None:
    candidate_counts, space_links = _bounded_space_link_result(
        satellite_count=4,
        max_candidates=1,
        space_link_mode=SpaceLinkMode.DETAILED_SMALL_SCALE,
        plane_count=2,
    )

    assert candidate_counts == {
        "sat-000": 4,
        "sat-001": 4,
        "sat-002": 4,
        "sat-003": 4,
    }
    assert len(space_links) == 6


def test_position_driven_network_engine_is_deterministic() -> None:
    assert _run_scenario() == _run_scenario()


def _space_link_payloads(events: list[SimEvent]) -> list[LinkState]:
    return [
        event.payload
        for event in events
        if isinstance(event.payload, LinkState)
        and event.payload.source_id == "sat-001"
        and event.payload.target_id == "sat-002"
    ]


def _link_after_orbit_update(
    network: PositionDrivenNetworkEngine,
    state: SatelliteState,
) -> LinkState:
    kernel = SimulationKernel()
    metrics = MetricsSink()
    kernel.register_module(network)
    kernel.register_module(metrics)
    kernel.schedule_event(_event("orbit", EventType.ORBIT_UPDATE.value, state))
    kernel.run()
    return network.active_link_states()[0]


def _bounded_space_link_result(
    *,
    satellite_count: int,
    max_candidates: int,
    space_link_mode: SpaceLinkMode = SpaceLinkMode.BOUNDED_CANDIDATE,
    plane_count: int = 3,
) -> tuple[dict[str, int], tuple[tuple[str, str, float, float], ...]]:
    kernel = SimulationKernel()
    network = PositionDrivenNetworkEngine(
        endpoints=(
            GroundEndpoint(
                endpoint_id="user-east",
                position=(EARTH_RADIUS_KM, 0.0, 0.0),
                min_elevation_deg=-90.0,
                max_range_km=1.0,
            ),
        ),
        compute_node_ids=("node-a",),
        link_capacity=50.0,
        propagation_speed_km_s=1000.0,
        cell_size_km=1000.0,
        space_link_max_range_km=50_000.0,
        space_link_capacity=75.0,
        space_link_cell_size_km=50_000.0,
        space_link_mode=space_link_mode,
        max_space_link_candidates_per_satellite=max_candidates,
        space_link_plane_count=plane_count,
    )
    metrics = MetricsSink()
    kernel.register_module(network)
    kernel.register_module(metrics)
    kernel.schedule_event(
        _event(
            "orbit-batch",
            EventType.ORBIT_BATCH_UPDATE.value,
            OrbitBatchState(
                sim_time=0.0,
                satellite_states=_batch_states(satellite_count),
                satellite_count=satellite_count,
            ),
        )
    )

    kernel.run()

    space_links = tuple(
        sorted(
            (
                link.source_id,
                link.target_id,
                round(link.latency, 9),
                link.capacity,
            )
            for link in network.active_link_states()
            if link.source_id.startswith("sat-") and link.target_id.startswith("sat-")
        )
    )
    return network.space_link_candidate_counts(), space_links


def _batch_states(satellite_count: int) -> tuple[SatelliteState, ...]:
    return tuple(
        _state(
            (
                7000.0 + float(index * 10),
                float((index % 3) * 10),
                float((index % 5) * 5),
            ),
            satellite_id=f"sat-{index:03d}",
        )
        for index in range(satellite_count)
    )


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
