"""Backend-owned fidelity summary for scale-aware runtime surfaces."""

from __future__ import annotations

from dataclasses import dataclass
from leo_twin.models.network.position_engine import (
    DEFAULT_BATCH_SPACE_LINK_UPDATE_LIMIT,
    DEFAULT_MAX_SPACE_LINK_CANDIDATES_PER_SATELLITE,
    SpaceLinkMode,
)
from leo_twin.models.orbit import MetricsMode, OrbitUpdateMode, SimulationFidelityPolicy


FidelitySummary = dict[str, object]


@dataclass(frozen=True)
class ScaleFidelityConfig:
    """Input configuration for deterministic scale fidelity explanation."""

    satellite_count: int
    user_count: int
    forced_orbit_update_mode: OrbitUpdateMode | str | None = None
    forced_space_link_mode: SpaceLinkMode | str | None = None
    space_link_enabled: bool = True
    max_space_link_candidates_per_satellite: int = (
        DEFAULT_MAX_SPACE_LINK_CANDIDATES_PER_SATELLITE
    )
    batch_space_link_update_limit: int = DEFAULT_BATCH_SPACE_LINK_UPDATE_LIMIT


def build_scale_fidelity_summary(config: ScaleFidelityConfig) -> FidelitySummary:
    """Return backend-owned fidelity mode details for the active runtime config."""

    if not isinstance(config, ScaleFidelityConfig):
        raise TypeError("config must be ScaleFidelityConfig")
    _require_positive_int(config.satellite_count, "satellite_count")
    _require_non_negative_int(config.user_count, "user_count")
    _require_positive_int(
        config.max_space_link_candidates_per_satellite,
        "max_space_link_candidates_per_satellite",
    )
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
        forced_space_link_mode=config.forced_space_link_mode,
        batch_space_link_update_limit=config.batch_space_link_update_limit,
    )
    detailed_space_link_enabled = space_link_mode == SpaceLinkMode.DETAILED_SMALL_SCALE
    warnings = _fidelity_warnings(
        policy=policy,
        space_link_mode=space_link_mode,
        max_space_link_candidates_per_satellite=(
            config.max_space_link_candidates_per_satellite
        ),
    )
    return {
        "satellite_count": config.satellite_count,
        "user_count": config.user_count,
        "orbit_update_mode": policy.orbit_update_mode.value,
        "metrics_mode": policy.metrics_mode.value,
        "space_link_mode": space_link_mode.value,
        "detailed_space_link_enabled": detailed_space_link_enabled,
        "space_link_candidate_policy": _space_link_candidate_policy(space_link_mode),
        "max_space_link_candidates_per_satellite": (
            config.max_space_link_candidates_per_satellite
        ),
        "batch_space_link_update_limit": config.batch_space_link_update_limit,
        "scale_limit_reason": _scale_limit_reason(
            policy=policy,
            space_link_mode=space_link_mode,
            satellite_count=config.satellite_count,
            max_space_link_candidates_per_satellite=(
                config.max_space_link_candidates_per_satellite
            ),
            batch_space_link_update_limit=config.batch_space_link_update_limit,
        ),
        "current_scale_mode": _current_scale_mode(policy, space_link_mode),
        "fidelity_warnings": warnings,
    }


def _space_link_mode(
    *,
    satellite_count: int,
    enabled: bool,
    forced_space_link_mode: SpaceLinkMode | str | None,
    batch_space_link_update_limit: int,
) -> SpaceLinkMode:
    if not enabled:
        return SpaceLinkMode.DISABLED
    if forced_space_link_mode is not None:
        return SpaceLinkMode(str(forced_space_link_mode))
    if satellite_count <= batch_space_link_update_limit:
        return SpaceLinkMode.DETAILED_SMALL_SCALE
    return SpaceLinkMode.BOUNDED_CANDIDATE


def _space_link_candidate_policy(mode: SpaceLinkMode) -> str:
    if mode == SpaceLinkMode.DISABLED:
        return "NO_SPACE_SPACE_LINKS"
    if mode == SpaceLinkMode.DETAILED_SMALL_SCALE:
        return "CELL_INDEX_NEARBY_WITH_RANGE_LIMIT"
    return "SAME_PLANE_AND_ADJACENT_PLANE_BOUNDED_CANDIDATES"


def _scale_limit_reason(
    *,
    policy: SimulationFidelityPolicy,
    space_link_mode: SpaceLinkMode,
    satellite_count: int,
    max_space_link_candidates_per_satellite: int,
    batch_space_link_update_limit: int,
) -> str:
    reasons: list[str] = []
    if policy.orbit_update_mode == OrbitUpdateMode.BATCH:
        reasons.append("orbit updates are batched")
    if policy.metrics_mode == MetricsMode.AGGREGATED:
        reasons.append("metrics are aggregated")
    if space_link_mode == SpaceLinkMode.DISABLED:
        reasons.append("space-space links are disabled")
    elif space_link_mode == SpaceLinkMode.BOUNDED_CANDIDATE:
        reasons.append(
            "detailed all-pairs space-space link updates are disabled because "
            f"satellite_count={satellite_count} exceeds "
            f"batch_space_link_update_limit={batch_space_link_update_limit}; "
            "bounded candidate updates are enabled with "
            "max_space_link_candidates_per_satellite="
            f"{max_space_link_candidates_per_satellite}"
        )
    return "none" if not reasons else "; ".join(reasons)


def _current_scale_mode(
    policy: SimulationFidelityPolicy,
    space_link_mode: SpaceLinkMode,
) -> str:
    if space_link_mode == SpaceLinkMode.DISABLED:
        return "SPACE_LINK_DISABLED"
    if policy.metrics_mode == MetricsMode.AGGREGATED:
        return "LARGE_SCALE_AGGREGATED"
    if policy.orbit_update_mode == OrbitUpdateMode.BATCH:
        return "LARGE_SCALE_BATCH"
    return "SMALL_SCALE_DETAILED"


def _fidelity_warnings(
    *,
    policy: SimulationFidelityPolicy,
    space_link_mode: SpaceLinkMode,
    max_space_link_candidates_per_satellite: int,
) -> tuple[str, ...]:
    warnings: list[str] = []
    if policy.orbit_update_mode == OrbitUpdateMode.BATCH:
        warnings.append("Orbit updates are batched to avoid per-satellite event flood.")
    if policy.metrics_mode == MetricsMode.AGGREGATED:
        warnings.append("Metrics are aggregated for large-scale responsiveness.")
    if space_link_mode == SpaceLinkMode.BOUNDED_CANDIDATE:
        warnings.append(
            "Space-space links use bounded candidate updates capped at "
            f"{max_space_link_candidates_per_satellite} candidates per satellite."
        )
    if space_link_mode == SpaceLinkMode.DISABLED:
        warnings.append("Space-space link updates are disabled.")
    return tuple(warnings)


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
