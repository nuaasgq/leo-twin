from __future__ import annotations

import pytest

from leo_twin.models.network.pressure import (
    NETWORK_TIME_PRESSURE_PERIOD_S,
    FlowPressureLedger,
    pressure_loss_rate,
    pressure_queue_delay,
    time_varying_pressure_delay_variation,
    time_varying_pressure_factor,
    time_varying_pressure_loss_rate,
    time_varying_pressure_phase,
)


def test_flow_pressure_ledger_reserves_demand_per_edge() -> None:
    ledger = FlowPressureLedger()

    affected = ledger.reserve("flow-a", (("user-a", "sat-001"),), 30.0)
    ledger.reserve("flow-b", (("user-a", "sat-001"),), 25.0)

    assert affected == (("user-a", "sat-001"),)
    assert ledger.active_demand(("user-a", "sat-001")) == pytest.approx(55.0)
    assert ledger.utilization(("user-a", "sat-001"), 100.0) == pytest.approx(0.55)


def test_flow_pressure_ledger_release_removes_only_target_flow() -> None:
    ledger = FlowPressureLedger()
    ledger.reserve("flow-a", (("user-a", "sat-001"),), 30.0)
    ledger.reserve("flow-b", (("user-a", "sat-001"),), 25.0)

    released = ledger.release("flow-a")

    assert released == (("user-a", "sat-001"),)
    assert ledger.active_demand(("user-a", "sat-001")) == pytest.approx(25.0)
    assert "flow-a" not in ledger.reservations
    assert "flow-b" in ledger.reservations


def test_flow_pressure_ledger_rereserve_replaces_old_flow_edges() -> None:
    ledger = FlowPressureLedger()
    ledger.reserve(
        "flow-a",
        (("user-a", "sat-001"), ("sat-001", "node-a")),
        40.0,
    )

    affected = ledger.reserve("flow-a", (("user-b", "sat-002"),), 10.0)

    assert affected == (("user-b", "sat-002"),)
    assert ledger.active_demand(("user-a", "sat-001")) == 0.0
    assert ledger.active_demand(("sat-001", "node-a")) == 0.0
    assert ledger.active_demand(("user-b", "sat-002")) == pytest.approx(10.0)


def test_flow_pressure_utilization_caps_and_handles_zero_capacity() -> None:
    ledger = FlowPressureLedger()
    ledger.reserve("flow-a", (("user-a", "sat-001"),), 160.0)

    assert ledger.utilization(("user-a", "sat-001"), 100.0) == pytest.approx(1.0)
    assert ledger.utilization(("user-a", "sat-001"), 0.0) == pytest.approx(1.0)


def test_pressure_loss_and_queue_delay_are_deterministic_flow_level_proxies() -> None:
    assert pressure_loss_rate(0.80) == 0.0
    assert pressure_loss_rate(1.00) == pytest.approx(0.10)
    assert pressure_queue_delay(0.2, 0.70) == 0.0
    assert pressure_queue_delay(0.2, 1.00) == pytest.approx(0.05)


def test_time_varying_pressure_helpers_are_deterministic_load_gated_proxies() -> None:
    assert NETWORK_TIME_PRESSURE_PERIOD_S == 120.0
    assert time_varying_pressure_phase(0.0) == 0.0
    assert time_varying_pressure_phase(60.0) == pytest.approx(0.5)
    assert time_varying_pressure_phase(120.0) == 0.0
    assert time_varying_pressure_factor(60.0, 0.0) == 0.0
    assert time_varying_pressure_factor(0.0, 0.8) == pytest.approx(0.36)
    assert time_varying_pressure_factor(30.0, 0.8) == pytest.approx(0.58)
    assert time_varying_pressure_factor(60.0, 0.8) == pytest.approx(0.8)
    assert time_varying_pressure_loss_rate(0.55) == 0.0
    assert time_varying_pressure_loss_rate(0.8) == pytest.approx(0.05)
    assert time_varying_pressure_delay_variation(0.2, 0.4) == 0.0
    assert time_varying_pressure_delay_variation(0.2, 0.8) == pytest.approx(0.016)


def test_pressure_route_admission_reports_queue_state_before_reserve() -> None:
    ledger = FlowPressureLedger()
    ledger.reserve("flow-a", (("user-a", "sat-001"),), 30.0)

    decision = ledger.evaluate_route(
        edges=(("user-a", "sat-001"),),
        demand_capacity=30.0,
        edge_capacities={("user-a", "sat-001"): 50.0},
        base_latency_s=0.2,
    )

    assert decision.admitted is True
    assert decision.blocked_reason is None
    assert decision.max_projected_utilization == pytest.approx(1.2)
    assert decision.pressure_utilization == pytest.approx(1.0)
    assert decision.queue_delay_s == pytest.approx(0.05)
    assert decision.loss_rate == pytest.approx(0.1)
    assert decision.edge_states[0].status == "saturated"
    assert decision.edge_states[0].queued_demand == pytest.approx(10.0)


def test_pressure_route_admission_rejects_extreme_oversubscription_without_reserve() -> None:
    ledger = FlowPressureLedger()
    ledger.reserve("flow-a", (("user-a", "sat-001"),), 60.0)

    decision = ledger.evaluate_route(
        edges=(("user-a", "sat-001"),),
        demand_capacity=30.0,
        edge_capacities={("user-a", "sat-001"): 50.0},
        base_latency_s=0.2,
    )

    assert decision.admitted is False
    assert decision.blocked_reason == "pressure_admission_limit"
    assert decision.max_projected_utilization == pytest.approx(1.8)
    assert decision.edge_states[0].status == "rejected"
    assert ledger.active_demand(("user-a", "sat-001")) == pytest.approx(60.0)
