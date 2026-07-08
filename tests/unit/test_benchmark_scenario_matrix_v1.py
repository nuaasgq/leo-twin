from __future__ import annotations

import json
from pathlib import Path

import pytest

from leo_twin.schema.config_loader import load_config
from leo_twin.services.benchmark_scenarios import (
    BENCHMARK_SCENARIO_MATRIX_V1_ID,
    benchmark_scenario_by_id,
    benchmark_scenario_ids,
    benchmark_scenario_matrix_v1_to_dict,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_benchmark_scenario_matrix_v1_is_deterministic_and_json_ready() -> None:
    first = benchmark_scenario_matrix_v1_to_dict(PROJECT_ROOT)
    second = benchmark_scenario_matrix_v1_to_dict(PROJECT_ROOT)

    assert first == second
    assert first["matrix_id"] == BENCHMARK_SCENARIO_MATRIX_V1_ID
    assert first["scenario_count"] == 3
    assert json.loads(json.dumps(first, sort_keys=True))["matrix_id"] == (
        BENCHMARK_SCENARIO_MATRIX_V1_ID
    )


def test_benchmark_scenario_matrix_covers_required_baselines() -> None:
    matrix = benchmark_scenario_matrix_v1_to_dict(PROJECT_ROOT)
    scenarios = {
        scenario["scenario_id"]: scenario
        for scenario in matrix["scenarios"]  # type: ignore[index]
    }

    assert benchmark_scenario_ids() == (
        "small_demo_72sat",
        "medium_demo_300sat",
        "scale_demo_1200sat_short",
    )
    assert set(scenarios) == set(benchmark_scenario_ids())
    assert scenarios["small_demo_72sat"]["satellite_count"] == 72
    assert scenarios["medium_demo_300sat"]["satellite_count"] == 300
    assert scenarios["scale_demo_1200sat_short"]["satellite_count"] == 1200
    assert scenarios["scale_demo_1200sat_short"]["scale_tier"] == (
        "LARGE_AGGREGATED"
    )


@pytest.mark.parametrize("scenario_id", benchmark_scenario_ids())
def test_benchmark_scenario_matrix_matches_acceptance_config(
    scenario_id: str,
) -> None:
    scenario = benchmark_scenario_by_id(scenario_id, PROJECT_ROOT)
    config = load_config(PROJECT_ROOT / str(scenario["config_path"]))

    assert (PROJECT_ROOT / str(scenario["config_path"])).exists()
    assert scenario["satellite_count"] == config.scenario.satellite_count
    assert scenario["user_count"] == config.scenario.user_count
    assert scenario["compute_node_count"] == config.scenario.compute_nodes
    assert scenario["runtime_duration_s"] == config.runtime.duration
    assert scenario["runtime_seed"] == config.runtime.seed
    assert scenario["orbit_update_interval_s"] == (
        config.scenario.orbit.update_interval_seconds
    )
    assert scenario["plane_count"] == config.scenario.orbit.plane_count
    assert scenario["compute_scheduling_policy"] == (
        config.scenario.compute_scheduling_policy.value
    )
    assert scenario["application_protocol"] == config.network.application_protocol.value
    assert scenario["traffic_class"] == "COMPUTE_SERVICE"
    assert scenario["traffic_destination_type"] == "COMPUTE_NODE"


def test_benchmark_scenario_matrix_records_backend_fidelity_expectations() -> None:
    scenarios = {
        scenario["scenario_id"]: scenario
        for scenario in benchmark_scenario_matrix_v1_to_dict(PROJECT_ROOT)[
            "scenarios"
        ]
    }

    assert scenarios["small_demo_72sat"]["fidelity_expectation"] == {
        "orbit_update_mode": "PER_SATELLITE",
        "metrics_mode": "DETAILED",
        "space_link_mode": "DETAILED_SMALL_SCALE",
    }
    assert scenarios["medium_demo_300sat"]["fidelity_summary"]["metrics_mode"] == (
        "DETAILED"
    )
    assert scenarios["scale_demo_1200sat_short"]["fidelity_summary"][
        "metrics_mode"
    ] == "AGGREGATED"
    assert scenarios["scale_demo_1200sat_short"]["fidelity_summary"][
        "space_link_candidate_policy"
    ] == "SAME_PLANE_AND_ADJACENT_PLANE_BOUNDED_CANDIDATES"


def test_benchmark_scenario_matrix_expected_ranges_are_exact_guardrails() -> None:
    scenario = benchmark_scenario_by_id("medium_demo_300sat", PROJECT_ROOT)
    ranges = {
        expected_range["metric"]: expected_range
        for expected_range in scenario["expected_ranges"]  # type: ignore[index]
    }

    assert ranges["satellite_count"] == {
        "metric": "satellite_count",
        "minimum": 300.0,
        "maximum": 300.0,
        "unit": "count",
        "source": "scenario.satellite_count",
        "expectation": "exact",
    }
    assert ranges["max_space_link_candidates_per_satellite"]["minimum"] == 4.0
    assert ranges["batch_space_link_update_limit"]["maximum"] == 999.0
    assert all(
        expected_range["minimum"] <= expected_range["maximum"]
        for expected_range in ranges.values()
    )


def test_benchmark_scenario_matrix_records_scope_boundaries() -> None:
    matrix = benchmark_scenario_matrix_v1_to_dict(PROJECT_ROOT)

    assert matrix["forbidden_integrations"] == ("STK", "EXATA", "AFSIM", "DDS")
    assert matrix["packet_level_simulation"] is False
    assert "Event Kernel" in matrix["acceptance_policy"]
    assert "events.jsonl" in matrix["result_artifact_expectation"]


def test_benchmark_scenario_matrix_requires_network_kpi_calibration() -> None:
    scenario = benchmark_scenario_by_id("small_demo_72sat", PROJECT_ROOT)
    expectation = scenario["runtime_status_expectation"]  # type: ignore[index]

    assert "network_kpi_calibration_v1" in expectation["required_fields"]
    assert (
        "network_kpi_calibration_v1.temporal_pressure_calibration"
        in expectation["required_fields"]
    )
    calibration = expectation["network_kpi_calibration"]
    assert calibration == {
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
    }
    temporal_calibration = expectation["network_temporal_pressure_calibration"]
    assert temporal_calibration == {
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
    }


def test_benchmark_scenario_matrix_requires_temporal_pressure_evidence() -> None:
    for scenario_id in benchmark_scenario_ids():
        scenario = benchmark_scenario_by_id(scenario_id, PROJECT_ROOT)
        expectation = scenario["runtime_status_expectation"]  # type: ignore[index]

        assert (
            "network_kpi_provenance_v2.temporal_pressure_evidence"
            in expectation["required_fields"]
        )
        temporal = expectation["network_temporal_pressure_evidence"]
        assert temporal == {
            "field": "network_kpi_provenance_v2.temporal_pressure_evidence",
            "source": "network_kpi_provenance_v2",
            "temporal_pressure_model": (
                "DETERMINISTIC_TRIANGULAR_LOAD_GATED_PROXY"
            ),
            "allowed_statuses": ("OBSERVED",),
            "minimum_observed_required_field_count": 3,
            "packet_level_simulation": False,
            "frontend_inference_required": False,
        }
