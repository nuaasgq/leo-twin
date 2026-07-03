"""Deterministic physical/channel link budget utilities."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, log10, log2
from typing import Any

from leo_twin.schema import AntennaProfile, ChannelProfile, LinkMedium


SPEED_OF_LIGHT_KM_S = 299792.458
_BOLTZMANN_W_PER_HZ_K = 1.380649e-23


@dataclass(frozen=True)
class RadioTerminalProfile:
    """Configuration for one deterministic radio terminal budget endpoint."""

    terminal_id: str
    antenna: AntennaProfile
    transmit_power_dbw: float
    system_loss_db: float = 0.0
    noise_temperature_k: float = 290.0

    def __post_init__(self) -> None:
        _require_non_empty_str(self.terminal_id, "terminal_id")
        _require_finite_number(self.transmit_power_dbw, "transmit_power_dbw")
        _require_non_negative_number(self.system_loss_db, "system_loss_db")
        _require_positive_number(self.noise_temperature_k, "noise_temperature_k")


@dataclass(frozen=True)
class LinkBudgetResult:
    """Computed deterministic physical/channel state for one link."""

    range_km: float
    propagation_delay_s: float
    path_loss_db: float
    received_power_dbw: float
    noise_power_dbw: float
    snr_db: float
    capacity_mbps: float
    transmit_pointing_loss_db: float = 0.0
    receive_pointing_loss_db: float = 0.0
    rain_fade_loss_db: float = 0.0

    def __post_init__(self) -> None:
        _require_positive_number(self.range_km, "range_km")
        _require_non_negative_number(self.propagation_delay_s, "propagation_delay_s")
        _require_finite_number(self.path_loss_db, "path_loss_db")
        _require_finite_number(self.received_power_dbw, "received_power_dbw")
        _require_finite_number(self.noise_power_dbw, "noise_power_dbw")
        _require_finite_number(self.snr_db, "snr_db")
        _require_non_negative_number(self.capacity_mbps, "capacity_mbps")
        _require_non_negative_number(
            self.transmit_pointing_loss_db,
            "transmit_pointing_loss_db",
        )
        _require_non_negative_number(
            self.receive_pointing_loss_db,
            "receive_pointing_loss_db",
        )
        _require_non_negative_number(self.rain_fade_loss_db, "rain_fade_loss_db")


@dataclass(frozen=True)
class RainFadeProfile:
    """Configuration-only deterministic rain attenuation profile."""

    rain_rate_mm_h: float
    attenuation_coefficient_db_per_km_per_mm_h: float
    effective_path_km: float

    def __post_init__(self) -> None:
        _require_non_negative_number(self.rain_rate_mm_h, "rain_rate_mm_h")
        _require_non_negative_number(
            self.attenuation_coefficient_db_per_km_per_mm_h,
            "attenuation_coefficient_db_per_km_per_mm_h",
        )
        _require_non_negative_number(self.effective_path_km, "effective_path_km")

    def loss_db(self) -> float:
        """Return deterministic rain fade loss in dB."""

        return (
            self.rain_rate_mm_h
            * self.attenuation_coefficient_db_per_km_per_mm_h
            * self.effective_path_km
        )


@dataclass(frozen=True)
class LinkBudgetCalculator:
    """Deterministic link budget calculator for configured LEO links."""

    transmit_terminal: RadioTerminalProfile
    receive_terminal: RadioTerminalProfile
    channel: ChannelProfile
    atmospheric_loss_db: float = 0.0
    polarization_loss_db: float = 0.0
    implementation_loss_db: float = 0.0
    rain_fade_profile: RainFadeProfile | None = None

    def __post_init__(self) -> None:
        _require_non_negative_number(self.atmospheric_loss_db, "atmospheric_loss_db")
        _require_non_negative_number(self.polarization_loss_db, "polarization_loss_db")
        _require_non_negative_number(self.implementation_loss_db, "implementation_loss_db")
        if self.rain_fade_profile is not None and not isinstance(
            self.rain_fade_profile,
            RainFadeProfile,
        ):
            raise TypeError("rain_fade_profile must be a RainFadeProfile")

    def evaluate(
        self,
        range_km: float,
        transmit_off_boresight_deg: float = 0.0,
        receive_off_boresight_deg: float = 0.0,
    ) -> LinkBudgetResult:
        """Evaluate deterministic budget values for one path range."""

        _require_positive_number(range_km, "range_km")
        transmit_pointing_loss_db = antenna_pointing_loss_db(
            self.transmit_terminal.antenna,
            transmit_off_boresight_deg,
        )
        receive_pointing_loss_db = antenna_pointing_loss_db(
            self.receive_terminal.antenna,
            receive_off_boresight_deg,
        )
        path_loss_db = free_space_path_loss_db(range_km, self.channel.carrier_frequency_hz)
        rain_fade_loss_db = (
            0.0 if self.rain_fade_profile is None else self.rain_fade_profile.loss_db()
        )
        received_power_dbw = (
            self.transmit_terminal.transmit_power_dbw
            + self.transmit_terminal.antenna.gain_dbi
            + self.receive_terminal.antenna.gain_dbi
            - path_loss_db
            - transmit_pointing_loss_db
            - receive_pointing_loss_db
            - self.transmit_terminal.system_loss_db
            - self.receive_terminal.system_loss_db
            - self.atmospheric_loss_db
            - rain_fade_loss_db
            - self.polarization_loss_db
        )
        noise_power_dbw = thermal_noise_power_dbw(
            bandwidth_hz=self.channel.bandwidth_hz,
            noise_temperature_k=self.receive_terminal.noise_temperature_k,
        )
        snr_db = received_power_dbw - noise_power_dbw - self.implementation_loss_db
        capacity_mbps = shannon_capacity_mbps(
            bandwidth_hz=self.channel.bandwidth_hz,
            snr_db=snr_db,
        )
        return LinkBudgetResult(
            range_km=range_km,
            propagation_delay_s=range_km / SPEED_OF_LIGHT_KM_S,
            path_loss_db=path_loss_db,
            received_power_dbw=received_power_dbw,
            noise_power_dbw=noise_power_dbw,
            snr_db=snr_db,
            capacity_mbps=capacity_mbps,
            transmit_pointing_loss_db=transmit_pointing_loss_db,
            receive_pointing_loss_db=receive_pointing_loss_db,
            rain_fade_loss_db=rain_fade_loss_db,
        )


@dataclass(frozen=True)
class ChannelBudgetSelector:
    """Select deterministic link budget calculators by link medium."""

    calculators: tuple[LinkBudgetCalculator, ...]
    default_calculator: LinkBudgetCalculator | None = None

    def __post_init__(self) -> None:
        if not self.calculators and self.default_calculator is None:
            raise ValueError("at least one calculator or default_calculator is required")
        mediums = tuple(calculator.channel.medium for calculator in self.calculators)
        if len(set(mediums)) != len(mediums):
            raise ValueError("calculator channel mediums must be unique")
        object.__setattr__(
            self,
            "calculators",
            tuple(sorted(self.calculators, key=lambda item: item.channel.medium.value)),
        )

    def calculator_for(self, medium: LinkMedium | str) -> LinkBudgetCalculator:
        """Return the calculator configured for the requested link medium."""

        normalized = medium if isinstance(medium, LinkMedium) else LinkMedium(str(medium))
        calculator = self.optional_calculator_for(normalized)
        if calculator is None:
            raise KeyError(f"no link budget calculator for medium: {normalized.value}")
        return calculator

    def optional_calculator_for(
        self,
        medium: LinkMedium | str,
    ) -> LinkBudgetCalculator | None:
        """Return a configured calculator or the default calculator if available."""

        normalized = medium if isinstance(medium, LinkMedium) else LinkMedium(str(medium))
        for calculator in self.calculators:
            if calculator.channel.medium == normalized:
                return calculator
        return self.default_calculator

    def evaluate(self, medium: LinkMedium | str, range_km: float) -> LinkBudgetResult:
        """Evaluate a link budget using the calculator for the given medium."""

        return self.calculator_for(medium).evaluate(range_km)


def free_space_path_loss_db(range_km: float, carrier_frequency_hz: float) -> float:
    """Return free-space path loss in dB for range in km and frequency in Hz."""

    _require_positive_number(range_km, "range_km")
    _require_positive_number(carrier_frequency_hz, "carrier_frequency_hz")
    carrier_frequency_ghz = carrier_frequency_hz / 1_000_000_000.0
    return 92.45 + 20.0 * log10(range_km) + 20.0 * log10(carrier_frequency_ghz)


def antenna_pointing_loss_db(
    antenna: AntennaProfile,
    off_boresight_angle_deg: float,
    max_loss_db: float = 30.0,
) -> float:
    """Return deterministic antenna gain loss from off-boresight pointing angle."""

    if not isinstance(antenna, AntennaProfile):
        raise TypeError("antenna must be an AntennaProfile")
    _require_pointing_angle(off_boresight_angle_deg, "off_boresight_angle_deg")
    _require_non_negative_number(max_loss_db, "max_loss_db")
    if off_boresight_angle_deg == 0.0 or max_loss_db == 0.0:
        return 0.0
    if antenna.beam_width_deg <= 0.0:
        return max_loss_db
    normalized_angle = (2.0 * off_boresight_angle_deg) / antenna.beam_width_deg
    return min(max_loss_db, 3.0 * normalized_angle * normalized_angle)


def thermal_noise_power_dbw(bandwidth_hz: float, noise_temperature_k: float) -> float:
    """Return thermal noise power in dBW."""

    _require_positive_number(bandwidth_hz, "bandwidth_hz")
    _require_positive_number(noise_temperature_k, "noise_temperature_k")
    return 10.0 * log10(_BOLTZMANN_W_PER_HZ_K * noise_temperature_k * bandwidth_hz)


def shannon_capacity_mbps(bandwidth_hz: float, snr_db: float) -> float:
    """Return deterministic Shannon capacity estimate in Mbps."""

    _require_positive_number(bandwidth_hz, "bandwidth_hz")
    _require_finite_number(snr_db, "snr_db")
    snr_linear = 10.0 ** (snr_db / 10.0)
    capacity_bps = bandwidth_hz * log2(1.0 + snr_linear)
    return capacity_bps / 1_000_000.0


def _require_non_empty_str(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value:
        raise TypeError(f"{field_name} must be a non-empty str")


def _require_finite_number(value: Any, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field_name} must be an int or float")
    if not isfinite(value):
        raise ValueError(f"{field_name} must be finite")


def _require_positive_number(value: Any, field_name: str) -> None:
    _require_finite_number(value, field_name)
    if value <= 0:
        raise ValueError(f"{field_name} must be positive")


def _require_non_negative_number(value: Any, field_name: str) -> None:
    _require_finite_number(value, field_name)
    if value < 0:
        raise ValueError(f"{field_name} must be non-negative")


def _require_pointing_angle(value: Any, field_name: str) -> None:
    _require_finite_number(value, field_name)
    if value < 0.0 or value > 180.0:
        raise ValueError(f"{field_name} must be in [0, 180]")
