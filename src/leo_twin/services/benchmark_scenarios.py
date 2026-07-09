"""Deterministic benchmark scenario matrix for product acceptance v2."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from leo_twin.schema.config import SEESConfig
from leo_twin.schema.config_loader import load_config
from leo_twin.services.scale_fidelity import (
    ScaleFidelityConfig,
    build_scale_fidelity_summary,
)
from leo_twin.services.scenario_builder import (
    scenario_builder_backend_summary,
    scenario_builder_config_from_sees_config,
)


BENCHMARK_SCENARIO_MATRIX_V1_ID = "leo_twin.benchmark_scenario_matrix.v1"
PROJECT_ROOT = Path(__file__).resolve().parents[3]


@dataclass(frozen=True)
class BenchmarkExpectedRange:
    """A deterministic numeric acceptance guardrail for one benchmark field."""

    metric: str
    minimum: float
    maximum: float
    unit: str
    source: str
    expectation: str = "inclusive"

    def __post_init__(self) -> None:
        _require_non_empty_string(self.metric, "metric")
        _require_finite_number(self.minimum, "minimum")
        _require_finite_number(self.maximum, "maximum")
        if self.minimum > self.maximum:
            raise ValueError("minimum must be <= maximum")
        _require_non_empty_string(self.unit, "unit")
        _require_non_empty_string(self.source, "source")
        _require_non_empty_string(self.expectation, "expectation")

    def to_dict(self) -> dict[str, object]:
        return {
            "metric": self.metric,
            "minimum": self.minimum,
            "maximum": self.maximum,
            "unit": self.unit,
            "source": self.source,
            "expectation": self.expectation,
        }


@dataclass(frozen=True)
class BenchmarkScenarioDefinition:
    """Static identity and intent for a shipped acceptance scenario."""

    scenario_id: str
    label: str
    config_path: str
    scale_tier: str
    intended_use: str
    expected_metrics_mode: str
    expected_orbit_update_mode: str
    expected_space_link_mode: str
    model_note: str

    def __post_init__(self) -> None:
        for field_name in (
            "scenario_id",
            "label",
            "config_path",
            "scale_tier",
            "intended_use",
            "expected_metrics_mode",
            "expected_orbit_update_mode",
            "expected_space_link_mode",
            "model_note",
        ):
            _require_non_empty_string(getattr(self, field_name), field_name)


@dataclass(frozen=True)
class BenchmarkScenarioSpec:
    """Resolved benchmark scenario spec derived from the shipped config file."""

    definition: BenchmarkScenarioDefinition
    satellite_count: int
    user_count: int
    compute_node_count: int
    runtime_duration_s: int
    runtime_seed: int
    orbit_update_interval_s: int
    plane_count: int
    compute_scheduling_policy: str
    application_protocol: str
    traffic_class: str
    traffic_destination_type: str
    fidelity_summary: dict[str, object]
    derived_constellation_summary: dict[str, object]
    traffic_demand_summary: dict[str, object]
    compute_resource_summary: dict[str, object]
    expected_ranges: tuple[BenchmarkExpectedRange, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "scenario_id": self.definition.scenario_id,
            "label": self.definition.label,
            "config_path": self.definition.config_path,
            "scale_tier": self.definition.scale_tier,
            "intended_use": self.definition.intended_use,
            "satellite_count": self.satellite_count,
            "user_count": self.user_count,
            "compute_node_count": self.compute_node_count,
            "runtime_duration_s": self.runtime_duration_s,
            "runtime_seed": self.runtime_seed,
            "orbit_update_interval_s": self.orbit_update_interval_s,
            "plane_count": self.plane_count,
            "compute_scheduling_policy": self.compute_scheduling_policy,
            "application_protocol": self.application_protocol,
            "traffic_class": self.traffic_class,
            "traffic_destination_type": self.traffic_destination_type,
            "fidelity_expectation": {
                "orbit_update_mode": self.definition.expected_orbit_update_mode,
                "metrics_mode": self.definition.expected_metrics_mode,
                "space_link_mode": self.definition.expected_space_link_mode,
            },
            "fidelity_summary": self.fidelity_summary,
            "derived_constellation_summary": self.derived_constellation_summary,
            "traffic_demand_summary": self.traffic_demand_summary,
            "compute_resource_summary": self.compute_resource_summary,
            "expected_ranges": tuple(
                expected_range.to_dict() for expected_range in self.expected_ranges
            ),
            "runtime_status_expectation": _runtime_status_expectation(),
            "acceptance_command": (
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                "scripts/verify_product_acceptance.ps1",
                "-AcceptanceConfig",
                self.definition.config_path,
            ),
            "model_note": self.definition.model_note,
        }


def _require_non_empty_string(value: object, field_name: str) -> None:
    if not isinstance(value, str) or not value:
        raise TypeError(f"{field_name} must be a non-empty string")


def _require_finite_number(value: object, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field_name} must be a number")
    if value != value or value in {float("inf"), float("-inf")}:
        raise ValueError(f"{field_name} must be finite")


_SCENARIO_DEFINITIONS: tuple[BenchmarkScenarioDefinition, ...] = (
    BenchmarkScenarioDefinition(
        scenario_id="small_demo_72sat",
        label="72-satellite detailed baseline",
        config_path="configs/acceptance/small_demo_72sat.yaml",
        scale_tier="SMALL_DETAILED",
        intended_use=(
            "Detailed control-plane smoke and dashboard semantic baseline."
        ),
        expected_metrics_mode="DETAILED",
        expected_orbit_update_mode="PER_SATELLITE",
        expected_space_link_mode="DETAILED_SMALL_SCALE",
        model_note=(
            "Small-scale acceptance keeps per-satellite orbit updates and detailed "
            "space-space link mode for compatibility checks."
        ),
    ),
    BenchmarkScenarioDefinition(
        scenario_id="medium_demo_300sat",
        label="300-satellite bounded scale baseline",
        config_path="configs/acceptance/medium_demo_300sat.yaml",
        scale_tier="MEDIUM_BATCH",
        intended_use=(
            "Scale transition smoke for batched orbit updates and bounded ISL "
            "candidate policy."
        ),
        expected_metrics_mode="DETAILED",
        expected_orbit_update_mode="BATCH",
        expected_space_link_mode="BOUNDED_CANDIDATE",
        model_note=(
            "Medium-scale acceptance uses batched orbit publication while keeping "
            "detailed KPI sampling."
        ),
    ),
    BenchmarkScenarioDefinition(
        scenario_id="scale_demo_1200sat_short",
        label="1200-satellite short scale baseline",
        config_path="configs/acceptance/scale_demo_1200sat_short.yaml",
        scale_tier="LARGE_AGGREGATED",
        intended_use=(
            "Large-scale live-control smoke for responsiveness under aggregated "
            "metrics and bounded ISL candidates."
        ),
        expected_metrics_mode="AGGREGATED",
        expected_orbit_update_mode="BATCH",
        expected_space_link_mode="BOUNDED_CANDIDATE",
        model_note=(
            "Large-scale acceptance is a responsiveness and reproducibility guard, "
            "not a high-fidelity orbital, RF, or packet-level validation case."
        ),
    ),
)


def benchmark_scenario_matrix_v1_to_dict(
    project_root: Path | None = None,
) -> dict[str, object]:
    """Return the backend-owned benchmark scenario matrix."""

    root = Path(project_root) if project_root is not None else PROJECT_ROOT
    scenarios = tuple(
        _resolve_scenario(definition, root).to_dict()
        for definition in _SCENARIO_DEFINITIONS
    )
    return {
        "matrix_id": BENCHMARK_SCENARIO_MATRIX_V1_ID,
        "version": "v1",
        "source": "configs/acceptance",
        "scenario_count": len(scenarios),
        "scenarios": scenarios,
        "acceptance_policy": (
            "Each benchmark config must load through the SEES config loader, "
            "initialize through DemoControlPlane, expose backend-derived summaries, "
            "advance a live runtime tick, and keep the Event Kernel free of "
            "domain-specific batch/fidelity logic."
        ),
        "result_artifact_expectation": (
            "config snapshot",
            "events.jsonl",
            "metrics.csv",
            "summary.json",
            "runtime log",
        ),
        "runtime_status_expectation": _runtime_status_expectation(),
        "forbidden_integrations": ("STK", "EXATA", "AFSIM", "DDS"),
        "packet_level_simulation": False,
        "model_assumptions": (
            "Benchmarks use deterministic flow-level abstractions.",
            "Expected ranges are product guardrails, not RF or orbital truth claims.",
            "Scale-mode fidelity is derived by backend policy and surfaced explicitly.",
        ),
    }


def benchmark_scenario_by_id(
    scenario_id: str,
    project_root: Path | None = None,
) -> dict[str, object]:
    """Return one benchmark scenario spec by deterministic scenario id."""

    _require_non_empty_string(scenario_id, "scenario_id")
    matrix = benchmark_scenario_matrix_v1_to_dict(project_root)
    for scenario in matrix["scenarios"]:
        assert isinstance(scenario, dict)
        if scenario["scenario_id"] == scenario_id:
            return scenario
    raise KeyError(f"unknown benchmark scenario id: {scenario_id}")


def benchmark_scenario_ids() -> tuple[str, ...]:
    """Return shipped benchmark scenario ids in deterministic order."""

    return tuple(definition.scenario_id for definition in _SCENARIO_DEFINITIONS)


def _runtime_status_expectation() -> dict[str, object]:
    return {
        "required_fields": (
            "fidelity_summary",
            "metrics_summary",
            "network_kpi_provenance_v2",
            "network_kpi_credibility_v1",
            "network_kpi_benchmark_validation_v1",
            "network_kpi_calibration_v1",
            "network_kpi_calibration_v1.temporal_pressure_calibration",
            "network_kpi_provenance_v2.temporal_pressure_evidence",
            "runtime_observation_consistency_v1",
            "route_explanation_summary_v1",
            "route_provenance_trust_summary_v1",
            "reproducibility_manifest_v1",
        ),
        "network_kpi_calibration": {
            "field": "network_kpi_calibration_v1",
            "source": "kpi_time_series_v1 + metrics_summary",
            "allowed_calibration_statuses": (
                "TIME_VARYING_OBSERVED",
                "PARTIAL_TIME_VARIATION",
                "FLAT_UNDER_ACTIVITY",
                "FLAT_NO_ACTIVITY",
                "INSUFFICIENT_SERIES",
            ),
            "packet_level_simulation": False,
        },
        "network_temporal_pressure_calibration": {
            "field": "network_kpi_calibration_v1.temporal_pressure_calibration",
            "source": "network_kpi_calibration_v1",
            "calibration_id": "leo_twin.network_temporal_pressure_calibration.v1",
            "temporal_pressure_model": (
                "DETERMINISTIC_TRIANGULAR_LOAD_GATED_PROXY"
            ),
            "allowed_statuses": (
                "TEMPORAL_DRIVER_ALIGNED",
                "TEMPORAL_DRIVER_INACTIVE",
                "TEMPORAL_DRIVER_NO_KPI_MOVEMENT",
                "INSUFFICIENT_SERIES",
            ),
            "packet_level_simulation": False,
            "frontend_inference_required": False,
            "calibration_hash_required": True,
        },
        "network_kpi_benchmark_validation": {
            "field": "network_kpi_benchmark_validation_v1",
            "source": "network_kpi_provenance_v2 + metrics_summary",
            "benchmark_profile": "FLOW_LEVEL_PROXY_RUNTIME_GUARDRAILS",
            "allowed_validation_statuses": (
                "PASS",
                "WARN",
                "INSUFFICIENT_DATA",
            ),
            "packet_level_simulation": False,
            "maximum_failed_check_count": 0,
        },
        "network_temporal_pressure_evidence": {
            "field": "network_kpi_provenance_v2.temporal_pressure_evidence",
            "source": "network_kpi_provenance_v2",
            "temporal_pressure_model": (
                "DETERMINISTIC_TRIANGULAR_LOAD_GATED_PROXY"
            ),
            "allowed_statuses": ("OBSERVED",),
            "minimum_observed_required_field_count": 3,
            "packet_level_simulation": False,
            "frontend_inference_required": False,
        },
        "route_trust": {
            "field": "route_provenance_trust_summary_v1",
            "source": "route_explanation_summary_v1",
            "route_model": "FLOW_LEVEL_ROUTE_PROXY",
            "allowed_trust_statuses": (
                "COMPLETE_FLOW_LEVEL_ROUTE_PROXY",
                "PARTIAL_ROUTE_EXPLANATIONS",
            ),
            "packet_level_simulation": False,
            "all_pairs_computation": False,
            "minimum_assessed_route_count": 1,
        },
    }


def _resolve_scenario(
    definition: BenchmarkScenarioDefinition,
    project_root: Path,
) -> BenchmarkScenarioSpec:
    config_path = project_root / definition.config_path
    config = load_config(config_path)
    backend_summary = scenario_builder_backend_summary(
        scenario_builder_config_from_sees_config(config)
    )
    fidelity_summary = _fidelity_summary(config)
    _assert_expected_fidelity(definition, fidelity_summary)
    return BenchmarkScenarioSpec(
        definition=definition,
        satellite_count=config.scenario.satellite_count,
        user_count=config.scenario.user_count,
        compute_node_count=config.scenario.compute_nodes,
        runtime_duration_s=config.runtime.duration,
        runtime_seed=config.runtime.seed,
        orbit_update_interval_s=config.scenario.orbit.update_interval_seconds,
        plane_count=config.scenario.orbit.plane_count,
        compute_scheduling_policy=config.scenario.compute_scheduling_policy.value,
        application_protocol=config.network.application_protocol.value,
        traffic_class=str(
            backend_summary["traffic_demand_summary"]["traffic_class"]  # type: ignore[index]
        ),
        traffic_destination_type=str(
            backend_summary["traffic_demand_summary"]["destination_type"]  # type: ignore[index]
        ),
        fidelity_summary=fidelity_summary,
        derived_constellation_summary=dict(
            backend_summary["derived_constellation_summary"]  # type: ignore[arg-type]
        ),
        traffic_demand_summary=_compact_traffic_summary(
            backend_summary["traffic_demand_summary"]  # type: ignore[arg-type]
        ),
        compute_resource_summary=_compact_compute_summary(
            backend_summary["compute_resource_summary"]  # type: ignore[arg-type]
        ),
        expected_ranges=_expected_ranges(config),
    )


def _fidelity_summary(config: SEESConfig) -> dict[str, object]:
    return build_scale_fidelity_summary(
        ScaleFidelityConfig(
            satellite_count=config.scenario.satellite_count,
            user_count=config.scenario.user_count,
            forced_orbit_update_mode=(
                None
                if config.scenario.orbit.orbit_update_mode is None
                else config.scenario.orbit.orbit_update_mode.value
            ),
            forced_space_link_mode=(
                None
                if config.network.space_link_mode is None
                else config.network.space_link_mode.value
            ),
            max_space_link_candidates_per_satellite=(
                config.network.max_space_link_candidates_per_satellite
            ),
            batch_space_link_update_limit=config.network.batch_space_link_update_limit,
        )
    )


def _assert_expected_fidelity(
    definition: BenchmarkScenarioDefinition,
    fidelity_summary: dict[str, object],
) -> None:
    expected = {
        "orbit_update_mode": definition.expected_orbit_update_mode,
        "metrics_mode": definition.expected_metrics_mode,
        "space_link_mode": definition.expected_space_link_mode,
    }
    actual = {key: fidelity_summary[key] for key in expected}
    if actual != expected:
        raise ValueError(
            f"benchmark fidelity mismatch for {definition.scenario_id}: "
            f"expected {expected}, got {actual}"
        )


def _compact_traffic_summary(summary: dict[str, object]) -> dict[str, object]:
    keys = (
        "traffic_class",
        "traffic_class_label",
        "destination_type",
        "destination_type_label",
        "generated_flow_count",
        "generated_task_count",
        "arrival_model",
        "source_selection_policy",
        "destination_selection_policy",
        "input_data_size_mb",
        "output_data_size_mb",
        "demand_capacity_mbps",
        "task_compute_demand",
        "service_mix_mode",
        "service_mix_generated_request_counts",
    )
    return {key: summary[key] for key in keys if key in summary}


def _compact_compute_summary(summary: dict[str, object]) -> dict[str, object]:
    keys = (
        "resource_model",
        "node_role",
        "compute_node_count",
        "legacy_capacity_per_node",
        "cpu_gflops_fp32_per_node",
        "cpu_gflops_fp64_per_node",
        "gpu_tflops_fp32_per_node",
        "gpu_tflops_fp16_per_node",
        "npu_tops_int8_per_node",
        "memory_gb_per_node",
        "storage_gb_per_node",
        "total_cpu_gflops_fp32",
        "total_cpu_gflops_fp64",
        "total_gpu_tflops_fp32",
        "total_gpu_tflops_fp16",
        "total_npu_tops_int8",
        "total_memory_gb",
        "total_storage_gb",
        "capacity_unit",
    )
    return {key: summary[key] for key in keys if key in summary}


def _expected_ranges(config: SEESConfig) -> tuple[BenchmarkExpectedRange, ...]:
    fields = (
        (
            "satellite_count",
            config.scenario.satellite_count,
            "count",
            "scenario.satellite_count",
        ),
        ("user_count", config.scenario.user_count, "count", "scenario.user_count"),
        (
            "compute_node_count",
            config.scenario.compute_nodes,
            "count",
            "scenario.compute_nodes",
        ),
        (
            "runtime_duration_s",
            config.runtime.duration,
            "seconds",
            "runtime.duration",
        ),
        (
            "orbit_update_interval_s",
            config.scenario.orbit.update_interval_seconds,
            "seconds",
            "scenario.orbit.update_interval_seconds",
        ),
        ("plane_count", config.scenario.orbit.plane_count, "count", "scenario.orbit.plane_count"),
        (
            "flow_interval_s",
            config.scenario.traffic_model.flow_interval_seconds,
            "seconds",
            "scenario.traffic_model.flow_interval_seconds",
        ),
        (
            "task_interval_s",
            config.scenario.traffic_model.task_interval_seconds,
            "seconds",
            "scenario.traffic_model.task_interval_seconds",
        ),
        (
            "flow_demand_capacity_mbps",
            config.scenario.traffic_model.flow_demand_capacity,
            "Mbps",
            "scenario.traffic_model.flow_demand_capacity",
        ),
        (
            "task_compute_demand",
            config.scenario.traffic_model.task_compute_demand,
            "work_units",
            "scenario.traffic_model.task_compute_demand",
        ),
        (
            "task_data_size_mb",
            config.scenario.traffic_model.task_data_size,
            "MB",
            "scenario.traffic_model.task_data_size",
        ),
        (
            "max_space_link_candidates_per_satellite",
            config.network.max_space_link_candidates_per_satellite,
            "count",
            "network.max_space_link_candidates_per_satellite",
        ),
        (
            "batch_space_link_update_limit",
            config.network.batch_space_link_update_limit,
            "count",
            "network.batch_space_link_update_limit",
        ),
        (
            "time_pressure_period_s",
            config.network.time_pressure_period_s,
            "seconds",
            "network.time_pressure_period_s",
        ),
        (
            "time_pressure_burst_center_phase",
            config.network.time_pressure_burst_center_phase,
            "phase",
            "network.time_pressure_burst_center_phase",
        ),
        (
            "time_pressure_burst_width_phase",
            config.network.time_pressure_burst_width_phase,
            "phase",
            "network.time_pressure_burst_width_phase",
        ),
        (
            "time_pressure_burst_amplitude",
            config.network.time_pressure_burst_amplitude,
            "ratio",
            "network.time_pressure_burst_amplitude",
        ),
    )
    return tuple(
        BenchmarkExpectedRange(
            metric=metric,
            minimum=float(value),
            maximum=float(value),
            unit=unit,
            source=source,
            expectation="exact",
        )
        for metric, value, unit, source in fields
    )
