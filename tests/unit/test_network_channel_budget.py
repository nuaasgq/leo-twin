from __future__ import annotations

import pytest

from leo_twin.models.network import (
    LinkBudgetCalculator,
    RadioTerminalProfile,
    free_space_path_loss_db,
    shannon_capacity_mbps,
    thermal_noise_power_dbw,
)
from leo_twin.schema import AntennaProfile, ChannelProfile, LinkMedium


def _antenna(antenna_id: str, gain_dbi: float) -> AntennaProfile:
    return AntennaProfile(
        antenna_id=antenna_id,
        gain_dbi=gain_dbi,
        beam_width_deg=2.0,
        steering_mode="electronic",
    )


def _calculator(transmit_power_dbw: float = 20.0) -> LinkBudgetCalculator:
    return LinkBudgetCalculator(
        transmit_terminal=RadioTerminalProfile(
            terminal_id="sat-terminal",
            antenna=_antenna("sat-ant", 32.0),
            transmit_power_dbw=transmit_power_dbw,
            system_loss_db=1.0,
        ),
        receive_terminal=RadioTerminalProfile(
            terminal_id="ground-terminal",
            antenna=_antenna("ground-ant", 36.0),
            transmit_power_dbw=0.0,
            system_loss_db=1.0,
            noise_temperature_k=290.0,
        ),
        channel=ChannelProfile(
            channel_id="ka-space-ground",
            medium=LinkMedium.SPACE_GROUND,
            carrier_frequency_hz=20_000_000_000.0,
            bandwidth_hz=500_000_000.0,
            loss_model_name="free_space_budget",
        ),
        atmospheric_loss_db=2.0,
        polarization_loss_db=0.5,
        implementation_loss_db=1.0,
    )


def test_link_budget_primitives_are_deterministic() -> None:
    assert free_space_path_loss_db(629.0, 20_000_000_000.0) == pytest.approx(
        174.443613,
        abs=1e-6,
    )
    assert thermal_noise_power_dbw(500_000_000.0, 290.0) == pytest.approx(
        -116.985487,
        abs=1e-6,
    )
    assert shannon_capacity_mbps(500_000_000.0, 10.0) == pytest.approx(
        1729.715810,
        abs=1e-6,
    )


def test_link_budget_calculator_returns_deterministic_result() -> None:
    calculator = _calculator()

    first = calculator.evaluate(629.0)
    second = calculator.evaluate(629.0)

    assert first == second
    assert first.propagation_delay_s == pytest.approx(0.002098, abs=1e-6)
    assert first.path_loss_db == pytest.approx(174.443613, abs=1e-6)
    assert first.snr_db == pytest.approx(25.041874, abs=1e-6)
    assert first.capacity_mbps == pytest.approx(4161.620976, abs=1e-6)


def test_link_budget_capacity_drops_with_lower_transmit_power() -> None:
    high_power = _calculator(transmit_power_dbw=20.0).evaluate(629.0)
    low_power = _calculator(transmit_power_dbw=0.0).evaluate(629.0)

    assert low_power.snr_db == pytest.approx(high_power.snr_db - 20.0)
    assert low_power.capacity_mbps < high_power.capacity_mbps
