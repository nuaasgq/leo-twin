"""Backend-owned fidelity summary for scale-aware runtime surfaces."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from leo_twin.models.network.position_engine import (
    DEFAULT_BATCH_SPACE_LINK_UPDATE_LIMIT,
)
from leo_twin.models.orbit import MetricsMode, OrbitUpdateMode, SimulationFidelityPolicy


class SpaceLinkMode(StrEnum):
    """Supported space-space link fidelity modes exposed to users."""

    DISABLED = "DISABLED"
    DETAILED_SMALL_SCALE = "DETAILED_SMALL_SCALE"
    REDUCED_LARGE_BATCH = "REDUCED_LARGE_BATCH"


FidelitySummary = dict[str, str | int | bool]


@dataclass(frozen=True)
class ScaleFidelityConfig:
    """Input configuration for deterministic scale fidelity explanation."""

    satellite_count: int
    user_count: int
    forced_orbit_update_mode: OrbitUpdateMode | str | None = None
    space_link_enabled: bool = True
    batch_space_link_update_limit: int = DEFAULT_BATCH_SPACE_LINK_UPDATE_LIMIT


def build_scale_fidelity_summary(config: ScaleFidelityConfig) -> FidelitySummary:
    """Return backend-owned fidelity mode details for the active runtime config."""

    if not isinstance(config, ScaleFidelityConfig):
        raise TypeError("config must be ScaleFidelityConfig")
    _require_positive_int(config.satellite_count, "satellite_count")
    _require_non_negative_int(config.user_count, "user_count")
    _require_positive_int(
        config.batch_space_link_update_limit,
        "batch_space_link_update_limit",
    )

    policy = SimulationFidelityPolicy.for_satellite_count(
        config.satellite_count,
        forced_orbit_update_mode=config.forced_orbit_update_mode,
    )
    space_link_mode = _space_link_mode(
        satellite_count=config.satellite_count,
        enabled=config.space_link_enabled,
        batch_space_link_update_limit=config.batch_space_link_update_limit,
    )
    detailed_space_link_enabled = space_link_mode == SpaceLinkMode.DETAILED_SMALL_SCALE
    return {
        "orbit_update_mode": policy.orbit_update_mode.value,
        "metrics_mode": policy.metrics_mode.value,
        "space_link_mode": space_link_mode.value,
        "detailed_space_link_enabled": detailed_space_link_enabled,
        "space_link_candidate_policy": _space_link_candidate_policy(space_link_mode),
        "scale_limit_reason": _scale_limit_reason(
            policy=policy,
            space_link_mode=space_link_mode,
            satellite_count=config.satellite_count,
            batch_space_link_update_limit=config.batch_space_link_update_limit,
        ),
        "satellite_count": config.satellite_count,
        "user_count": config.user_count,
    }


def _space_link_mode(
    *,
    satellite_count: int,
    enabled: bool,
    batch_space_link_update_limit: int,
) -> SpaceLinkMode:
    if not enabled:
        return SpaceLinkMode.DISABLED
    if satellite_count <= batch_space_link_update_limit:
        return SpaceLinkMode.DETAILED_SMALL_SCALE
    return SpaceLinkMode.REDUCED_LARGE_BATCH


def _space_link_candidate_policy(mode: SpaceLinkMode) -> str:
    if mode == SpaceLinkMode.DISABLED:
        return "NO_SPACE_SPACE_LINKS"
    if mode == SpaceLinkMode.DETAILED_SMALL_SCALE:
        return "CELL_INDEX_NEARBY_WITH_RANGE_LIMIT"
    return "SPACE_GROUND_ONLY_WHEN_BATCH_EXCEEDS_LIMIT"


def _scale_limit_reason(
    *,
    policy: SimulationFidelityPolicy,
    space_link_mode: SpaceLinkMode,
    satellite_count: int,
    batch_space_link_update_limit: int,
) -> str:
    reasons: list[str] = []
    if policy.orbit_update_mode == OrbitUpdateMode.BATCH:
        reasons.append("orbit updates are batched")
    if policy.metrics_mode == MetricsMode.AGGREGATED:
        reasons.append("metrics are aggregated")
    if space_link_mode == SpaceLinkMode.DISABLED:
        reasons.append("space-space links are disabled")
    elif space_link_mode == SpaceLinkMode.REDUCED_LARGE_BATCH:
        reasons.append(
            "detailed space-space link updates are skipped because "
            f"satellite_count={satellite_count} exceeds "
            f"batch_space_link_update_limit={batch_space_link_update_limit}"
        )
    return "none" if not reasons else "; ".join(reasons)


def _require_positive_int(value: object, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field_name} must be an int")
    if value <= 0:
        raise ValueError(f"{field_name} must be positive")


def _require_non_negative_int(value: object, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field_name} must be an int")
    if value < 0:
        raise ValueError(f"{field_name} must be non-negative")
