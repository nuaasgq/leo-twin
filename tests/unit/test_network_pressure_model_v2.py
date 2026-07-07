from __future__ import annotations

import pytest

from leo_twin.models.network.pressure import (
    FlowPressureLedger,
    pressure_loss_rate,
    pressure_queue_delay,
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
