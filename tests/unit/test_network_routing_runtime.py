from __future__ import annotations

from leo_twin.models.network import RoutingRuntime, StaticRouteEntry
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

    assert route == Route(
        route_id="route:flow-001",
        flow_id="flow-001",
        path=("user-a", "sat-a", "node-a"),
        latency=5.0,
        capacity=50.0,
        available=True,
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


def test_routing_returns_unavailable_when_capacity_is_insufficient() -> None:
    runtime = RoutingRuntime(RoutingProtocol.LINK_STATE)

    route = runtime.route(_request(demand=200.0), _links())

    assert route.available is False
    assert route.path == ()
