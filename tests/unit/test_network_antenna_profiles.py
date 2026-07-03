from __future__ import annotations

import pytest

from leo_twin.models.network import (
    ApertureAntennaSpec,
    LinkBudgetCalculator,
    RadioTerminalProfile,
    aperture_antenna_beam_width_deg,
    aperture_antenna_gain_dbi,
)
from leo_twin.schema import ChannelProfile, LinkMedium


def test_aperture_antenna_formulas_are_deterministic() -> None:
    gain_dbi = aperture_antenna_gain_dbi(
        diameter_m=0.45,
        carrier_frequency_hz=20_000_000_000.0,
        aperture_efficiency=0.65,
    )
    beam_width_deg = aperture_antenna_beam_width_deg(
        diameter_m=0.45,
        carrier_frequency_hz=20_000_000_000.0,
    )

    assert gain_dbi == pytest.approx(37.620567, abs=1e-6)
    assert beam_width_deg == pytest.approx(2.331719, abs=1e-6)


def test_aperture_antenna_spec_builds_schema_profile() -> None:
    profile = ApertureAntennaSpec(
        antenna_id="sat-ka-aperture",
        diameter_m=0.45,
        carrier_frequency_hz=20_000_000_000.0,
        aperture_efficiency=0.65,
        steering_mode="tracking",
    ).to_profile()

    assert profile.antenna_id == "sat-ka-aperture"
    assert profile.gain_dbi == pytest.approx(37.620567, abs=1e-6)
    assert profile.beam_width_deg == pytest.approx(2.331719, abs=1e-6)
    assert profile.steering_mode == "tracking"


def test_aperture_antenna_spec_rejects_invalid_efficiency() -> None:
    with pytest.raises(ValueError, match="aperture_efficiency"):
        ApertureAntennaSpec(
            antenna_id="invalid",
            diameter_m=0.45,
            carrier_frequency_hz=20_000_000_000.0,
            aperture_efficiency=1.2,
        )


def test_larger_aperture_increases_link_budget_capacity() -> None:
    channel = ChannelProfile(
        channel_id="ka-space-ground",
        medium=LinkMedium.SPACE_GROUND,
        carrier_frequency_hz=20_000_000_000.0,
        bandwidth_hz=500_000_000.0,
        loss_model_name="free_space_budget",
    )
    small = ApertureAntennaSpec(
        antenna_id="small-terminal",
        diameter_m=0.3,
        carrier_frequency_hz=channel.carrier_frequency_hz,
        aperture_efficiency=0.65,
    ).to_profile()
    large = ApertureAntennaSpec(
        antenna_id="large-terminal",
        diameter_m=0.9,
        carrier_frequency_hz=channel.carrier_frequency_hz,
        aperture_efficiency=0.65,
    ).to_profile()

    small_result = LinkBudgetCalculator(
        transmit_terminal=RadioTerminalProfile(
            terminal_id="sat-small",
            antenna=small,
            transmit_power_dbw=20.0,
        ),
        receive_terminal=RadioTerminalProfile(
            terminal_id="ground-small",
            antenna=small,
            transmit_power_dbw=0.0,
        ),
        channel=channel,
    ).evaluate(629.0)
    large_result = LinkBudgetCalculator(
        transmit_terminal=RadioTerminalProfile(
            terminal_id="sat-large",
            antenna=large,
            transmit_power_dbw=20.0,
        ),
        receive_terminal=RadioTerminalProfile(
            terminal_id="ground-large",
            antenna=large,
            transmit_power_dbw=0.0,
        ),
        channel=channel,
    ).evaluate(629.0)

    assert large.gain_dbi > small.gain_dbi
    assert large.beam_width_deg < small.beam_width_deg
    assert large_result.snr_db > small_result.snr_db
    assert large_result.capacity_mbps > small_result.capacity_mbps
