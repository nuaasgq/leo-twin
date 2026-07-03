from __future__ import annotations

import pytest

from leo_twin.models.network import (
    ChannelBudgetSelector,
    LinkBudgetCalculator,
    RainFadeProfile,
    RadioTerminalProfile,
    antenna_pointing_loss_db,
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


def _calculator(
    transmit_power_dbw: float = 20.0,
    medium: LinkMedium = LinkMedium.SPACE_GROUND,
    channel_id: str = "ka-space-ground",
) -> LinkBudgetCalculator:
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
            channel_id=channel_id,
            medium=medium,
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


def test_antenna_pointing_loss_uses_beam_width_and_is_bounded() -> None:
    antenna = _antenna("narrow-ant", 32.0)

    assert antenna_pointing_loss_db(antenna, 0.0) == 0.0
    assert antenna_pointing_loss_db(antenna, 1.0) == pytest.approx(3.0)
    assert antenna_pointing_loss_db(antenna, 20.0, max_loss_db=18.0) == 18.0

    with pytest.raises(ValueError, match="off_boresight_angle_deg"):
        antenna_pointing_loss_db(antenna, 181.0)


def test_link_budget_calculator_applies_antenna_pointing_losses() -> None:
    calculator = _calculator()

    aligned = calculator.evaluate(629.0)
    offset = calculator.evaluate(
        629.0,
        transmit_off_boresight_deg=1.0,
        receive_off_boresight_deg=1.0,
    )

    assert offset.transmit_pointing_loss_db == pytest.approx(3.0)
    assert offset.receive_pointing_loss_db == pytest.approx(3.0)
    assert offset.received_power_dbw == pytest.approx(aligned.received_power_dbw - 6.0)
    assert offset.snr_db == pytest.approx(aligned.snr_db - 6.0)
    assert offset.capacity_mbps < aligned.capacity_mbps


def test_link_budget_calculator_applies_rain_fade_profile() -> None:
    clear_sky = _calculator()
    rainy = LinkBudgetCalculator(
        transmit_terminal=clear_sky.transmit_terminal,
        receive_terminal=clear_sky.receive_terminal,
        channel=clear_sky.channel,
        atmospheric_loss_db=clear_sky.atmospheric_loss_db,
        polarization_loss_db=clear_sky.polarization_loss_db,
        implementation_loss_db=clear_sky.implementation_loss_db,
        rain_fade_profile=RainFadeProfile(
            rain_rate_mm_h=20.0,
            attenuation_coefficient_db_per_km_per_mm_h=0.015,
            effective_path_km=4.0,
        ),
    )

    clear_result = clear_sky.evaluate(629.0)
    rainy_result = rainy.evaluate(629.0)

    assert rainy_result.rain_fade_loss_db == pytest.approx(1.2)
    assert rainy_result.received_power_dbw == pytest.approx(
        clear_result.received_power_dbw - 1.2
    )
    assert rainy_result.snr_db == pytest.approx(clear_result.snr_db - 1.2)
    assert rainy_result.capacity_mbps < clear_result.capacity_mbps


def test_channel_budget_selector_uses_medium_specific_calculator() -> None:
    ground = _calculator(medium=LinkMedium.SPACE_GROUND, channel_id="ground")
    space = _calculator(
        transmit_power_dbw=10.0,
        medium=LinkMedium.SPACE_SPACE,
        channel_id="space",
    )
    selector = ChannelBudgetSelector(calculators=(space, ground))

    assert selector.calculator_for(LinkMedium.SPACE_GROUND) == ground
    assert selector.calculator_for("SPACE_SPACE") == space
    assert selector.evaluate(LinkMedium.SPACE_SPACE, 629.0) == space.evaluate(629.0)


def test_channel_budget_selector_supports_default_calculator() -> None:
    ground = _calculator()
    selector = ChannelBudgetSelector(calculators=(), default_calculator=ground)

    assert selector.optional_calculator_for(LinkMedium.SPACE_SPACE) == ground


def test_channel_budget_selector_rejects_duplicate_mediums() -> None:
    with pytest.raises(ValueError, match="mediums must be unique"):
        ChannelBudgetSelector(calculators=(_calculator(), _calculator(channel_id="copy")))
