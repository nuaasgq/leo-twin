from __future__ import annotations

import pytest

from leo_twin.models.network import RoutingCostProfile, RoutingRuntime, StaticRouteEntry
from leo_twin.schema import FlowRequest, LinkState, Route, RoutingProtocol


def _request(demand: float = 10.0) -> FlowRequest:
    return FlowRequest("flow-001", "user-a", "node-a", demand)


def _links() -> tuple[LinkState, ...]:
    return (
        LinkState("user-a", "sat-b", latency=4.0, capacity=100.0, availability=True),
        LinkState("sat-b", "node-a", latency=4.0, capacity=100.0, availability=True),
        LinkState("user-a", "sat-a", latency=2.0, capacity=50.0, availability=True),
        LinkState("sat-a", "node-a", latency=3.0, capacity=50.0, availability=True),
        LinkState("user-a", "sat-c", latency=1.0, capacity=5.0, availability=True),
        LinkState("sat-c", "node-a", latency=1.0, capacity=5.0, availability=True),
    )


def test_link_state_routing_selects_lowest_latency_capacity_feasible_path() -> None:
    runtime = RoutingRuntime(RoutingProtocol.LINK_STATE)

    route = runtime.route(_request(), _links())

    assert runtime.cost_profile == RoutingCostProfile()
    assert route == Route(
        route_id="route:flow-001",
        flow_id="flow-001",
        path=("user-a", "sat-a", "node-a"),
        latency=5.0,
        capacity=50.0,
        available=True,
        demand_capacity=10.0,
    )


def test_shortest_path_routing_is_deterministic() -> None:
    runtime = RoutingRuntime(RoutingProtocol.SHORTEST_PATH)

    first = runtime.route(_request(), _links())
    second = runtime.route(_request(), tuple(reversed(_links())))

    assert first == second


def test_static_routing_uses_configured_path() -> None:
    runtime = RoutingRuntime(
        RoutingProtocol.STATIC,
        static_routes=(
            StaticRouteEntry(
                source_id="user-a",
                target_id="node-a",
                path=("user-a", "sat-b", "node-a"),
            ),
        ),
    )

    route = runtime.route(_request(), _links())

    assert route.path == ("user-a", "sat-b", "node-a")
    assert route.latency == 8.0
    assert route.capacity == 100.0


def test_distance_vector_defaults_to_lowest_hop_count() -> None:
    runtime = RoutingRuntime(RoutingProtocol.DISTANCE_VECTOR)
    links = (
        LinkState("user-a", "node-a", latency=20.0, capacity=20.0, availability=True),
        LinkState("user-a", "sat-a", latency=1.0, capacity=20.0, availability=True),
        LinkState("sat-a", "node-a", latency=1.0, capacity=20.0, availability=True),
    )

    route = runtime.route(_request(), links)

    assert route.path == ("user-a", "node-a")
    assert route.latency == 20.0


def test_routing_cost_profile_can_prefer_higher_capacity_path() -> None:
    runtime = RoutingRuntime(
        RoutingProtocol.LINK_STATE,
        cost_profile=RoutingCostProfile(inverse_capacity_weight=400.0),
    )

    route = runtime.route(_request(), _links())

    assert route.path == ("user-a", "sat-b", "node-a")
    assert route.latency == 8.0
    assert route.capacity == 100.0


def test_routing_cost_profile_can_prefer_lower_hop_count() -> None:
    runtime = RoutingRuntime(
        RoutingProtocol.SHORTEST_PATH,
        cost_profile=RoutingCostProfile(hop_weight=0.2),
    )
    links = (
        LinkState("user-a", "node-a", latency=3.1, capacity=20.0, availability=True),
        LinkState("user-a", "sat-a", latency=1.0, capacity=20.0, availability=True),
        LinkState("sat-a", "sat-b", latency=1.0, capacity=20.0, availability=True),
        LinkState("sat-b", "node-a", latency=1.0, capacity=20.0, availability=True),
    )

    route = runtime.route(_request(), links)

    assert route.path == ("user-a", "node-a")
    assert route.latency == 3.1


def test_routing_cost_profile_rejects_zero_weight_profile() -> None:
    with pytest.raises(ValueError, match="at least one routing cost weight"):
        RoutingCostProfile(
            latency_weight=0.0,
            inverse_capacity_weight=0.0,
            hop_weight=0.0,
        )


def test_routing_returns_unavailable_when_capacity_is_insufficient() -> None:
    runtime = RoutingRuntime(RoutingProtocol.LINK_STATE)

    route = runtime.route(_request(demand=200.0), _links())

    assert route.available is False
    assert route.path == ()
