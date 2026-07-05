"""Product scale policy v2 for runtime fidelity and LOD explanations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from leo_twin.services.scale_fidelity import (
    ScaleFidelityConfig,
    build_scale_fidelity_summary,
)


SCALE_POLICY_V2_ID = "leo_twin.scale_policy.v2"

ScaleBand = Literal[
    "SMALL_72",
    "MEDIUM_300",
    "LARGE_1200",
    "XL_3000",
    "XXL_6000",
    "EXTREME_12000",
]


@dataclass(frozen=True)
class ScalePolicyProfileV2:
    """One deterministic product scale profile."""

    profile_id: str
    scale_band: ScaleBand
    target_satellite_count: int
    satellite_count_min: int
    satellite_count_max: int | None
    orbit_update_mode: str
    metrics_mode: str
    space_link_mode: str
    snapshot_lod_policy: str
    detail_window_policy: str
    frontend_policy: str
    runtime_guardrail_policy: str
    recommended_use: str
    limitation_note: str

    def to_dict(self) -> dict[str, object]:
        return {
            "profile_id": self.profile_id,
            "scale_band": self.scale_band,
            "target_satellite_count": self.target_satellite_count,
            "satellite_count_min": self.satellite_count_min,
            "satellite_count_max": self.satellite_count_max,
            "orbit_update_mode": self.orbit_update_mode,
            "metrics_mode": self.metrics_mode,
            "space_link_mode": self.space_link_mode,
            "snapshot_lod_policy": self.snapshot_lod_policy,
            "detail_window_policy": self.detail_window_policy,
            "frontend_policy": self.frontend_policy,
            "runtime_guardrail_policy": self.runtime_guardrail_policy,
            "recommended_use": self.recommended_use,
            "limitation_note": self.limitation_note,
        }


SCALE_POLICY_V2_PROFILES: tuple[ScalePolicyProfileV2, ...] = (
    ScalePolicyProfileV2(
        profile_id="baseline_72",
        scale_band="SMALL_72",
        target_satellite_count=72,
        satellite_count_min=1,
        satellite_count_max=99,
        orbit_update_mode="PER_SATELLITE",
        metrics_mode="DETAILED",
        space_link_mode="DETAILED_SMALL_SCALE",
        snapshot_lod_policy="FULL_DETAIL_SNAPSHOT",
        detail_window_policy="FULL_NODE_DETAIL_ALLOWED",
        frontend_policy="RENDER_SMALL_SCALE_DETAIL",
        runtime_guardrail_policy="STANDARD_RUNTIME_GUARDS",
        recommended_use="model debugging, UI acceptance, and small benchmark runs",
        limitation_note="Small scale remains simplified and is not high-fidelity physics.",
    ),
    ScalePolicyProfileV2(
        profile_id="medium_300",
        scale_band="MEDIUM_300",
        target_satellite_count=300,
        satellite_count_min=100,
        satellite_count_max=999,
        orbit_update_mode="BATCH",
        metrics_mode="DETAILED",
        space_link_mode="DETAILED_SMALL_SCALE",
        snapshot_lod_policy="BATCH_ORBIT_WITH_BOUNDED_RENDER_DETAIL",
        detail_window_policy="WINDOWED_NODE_DETAIL",
        frontend_policy="RENDER_BOUNDED_DETAIL_AND_SUMMARIES",
        runtime_guardrail_policy="EVENT_VOLUME_ESTIMATE_REQUIRED",
        recommended_use="medium constellation behavior and dashboard workflow checks",
        limitation_note="Orbit events are batched; detailed rendering must stay bounded.",
    ),
    ScalePolicyProfileV2(
        profile_id="large_1200",
        scale_band="LARGE_1200",
        target_satellite_count=1200,
        satellite_count_min=1000,
        satellite_count_max=2999,
        orbit_update_mode="BATCH",
        metrics_mode="AGGREGATED",
        space_link_mode="BOUNDED_CANDIDATE",
        snapshot_lod_policy="TOP_K_AND_WINDOWED_DETAIL",
        detail_window_policy="CURSOR_OR_WINDOWED_DETAIL_REQUIRED",
        frontend_policy="LOD_RENDERING_AND_FIDELITY_NOTICE",
        runtime_guardrail_policy="SCALE_SAFETY_CHECK_REQUIRED",
        recommended_use="large-scale live control and aggregate KPI inspection",
        limitation_note="Metrics are aggregated and ISL updates are bounded candidates.",
    ),
    ScalePolicyProfileV2(
        profile_id="xl_3000",
        scale_band="XL_3000",
        target_satellite_count=3000,
        satellite_count_min=3000,
        satellite_count_max=5999,
        orbit_update_mode="BATCH",
        metrics_mode="AGGREGATED",
        space_link_mode="BOUNDED_CANDIDATE",
        snapshot_lod_policy="AGGREGATE_FIRST_WITH_DETAIL_WINDOWS",
        detail_window_policy="BACKEND_CURSOR_DETAIL_REQUIRED",
        frontend_policy="VIRTUAL_TABLES_AND_SAMPLE_RENDERING",
        runtime_guardrail_policy="STRICT_EVENT_AND_MEMORY_GUARDS",
        recommended_use="scale strategy validation before broader production scenarios",
        limitation_note="Backend cursor APIs should be preferred over large raw snapshots.",
    ),
    ScalePolicyProfileV2(
        profile_id="xxl_6000",
        scale_band="XXL_6000",
        target_satellite_count=6000,
        satellite_count_min=6000,
        satellite_count_max=11999,
        orbit_update_mode="BATCH",
        metrics_mode="AGGREGATED",
        space_link_mode="BOUNDED_CANDIDATE",
        snapshot_lod_policy="AGGREGATE_ONLY_BY_DEFAULT",
        detail_window_policy="EXPLICIT_NODE_DETAIL_REQUESTS_ONLY",
        frontend_policy="SUMMARY_FIRST_WITH_OPT_IN_DETAIL",
        runtime_guardrail_policy="STRICT_GUARDS_AND_DEGRADE_REASON_REQUIRED",
        recommended_use="operator-facing stress and summary-observability planning",
        limitation_note="Detailed per-node surfaces must be opt-in and bounded.",
    ),
    ScalePolicyProfileV2(
        profile_id="extreme_12000",
        scale_band="EXTREME_12000",
        target_satellite_count=12000,
        satellite_count_min=12000,
        satellite_count_max=None,
        orbit_update_mode="BATCH",
        metrics_mode="AGGREGATED",
        space_link_mode="BOUNDED_CANDIDATE",
        snapshot_lod_policy="SUMMARY_AND_EXPORT_FIRST",
        detail_window_policy="OFFLINE_OR_CURSOR_DETAIL_ONLY",
        frontend_policy="NO_FULL_SCENE_DETAIL_RENDERING",
        runtime_guardrail_policy="PRE_RUN_ACCEPTANCE_REQUIRED",
        recommended_use="future acceptance planning and offline reproducibility packages",
        limitation_note="Interactive full-detail operation is not a current product claim.",
    ),
)


def scale_policy_v2_to_dict(
    *,
    satellite_count: int,
    user_count: int,
) -> dict[str, object]:
    """Return deterministic product scale policy and active profile."""

    _require_positive_int(satellite_count, "satellite_count")
    _require_non_negative_int(user_count, "user_count")
    active_profile = scale_policy_profile_for_satellite_count(satellite_count)
    active_fidelity = build_scale_fidelity_summary(
        ScaleFidelityConfig(
            satellite_count=satellite_count,
            user_count=user_count,
        )
    )
    return {
        "version": "v2",
        "policy_id": SCALE_POLICY_V2_ID,
        "profile_targets": (72, 300, 1200, 3000, 6000, 12000),
        "active_profile_id": active_profile.profile_id,
        "active_scale_band": active_profile.scale_band,
        "active_profile": active_profile.to_dict(),
        "active_fidelity_summary": active_fidelity,
        "profiles": tuple(profile.to_dict() for profile in SCALE_POLICY_V2_PROFILES),
        "frontend_notice_policy": (
            "Frontend must display backend fidelity and scale-limit fields instead "
            "of inferring degradation locally."
        ),
        "result_reproducibility_policy": (
            "Result packages should include config snapshot, fidelity summary, "
            "scale policy, events, metrics, and run summary."
        ),
        "forbidden_integrations": ("STK", "EXATA", "AFSIM", "DDS"),
        "packet_level_simulation": False,
        "event_kernel_policy": "NO_EVENT_KERNEL_BEHAVIOR_CHANGE",
    }


def scale_policy_profile_for_satellite_count(
    satellite_count: int,
) -> ScalePolicyProfileV2:
    """Select the deterministic scale profile for one satellite count."""

    _require_positive_int(satellite_count, "satellite_count")
    for profile in SCALE_POLICY_V2_PROFILES:
        if satellite_count < profile.satellite_count_min:
            continue
        if profile.satellite_count_max is None:
            return profile
        if satellite_count <= profile.satellite_count_max:
            return profile
    return SCALE_POLICY_V2_PROFILES[-1]


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
