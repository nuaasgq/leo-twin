from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from examples.integration_demo.config import DemoConfig
from examples.integration_demo.control_plane import DemoControlPlane
from examples.integration_demo.runtime import run_integration_demo
from leo_twin.schema.config import SEESConfig, config_to_dict
from leo_twin.schema.config_loader import load_config
from leo_twin.services.benchmark_scenarios import (
    benchmark_scenario_by_id,
    benchmark_scenario_ids,
    benchmark_scenario_matrix_v1_to_dict,
)
from leo_twin.services.model_verification_report import (
    model_verification_report_template_v1_to_dict,
)
from leo_twin.services.scale_fidelity import (
    ScaleFidelityConfig,
    build_scale_fidelity_summary,
)
from leo_twin.services.scenario_builder import (
    scenario_builder_backend_summary,
    scenario_builder_config_from_sees_config,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_benchmark_acceptance_report_template_matches_matrix() -> None:
    matrix = benchmark_scenario_matrix_v1_to_dict(PROJECT_ROOT)
    template = model_verification_report_template_v1_to_dict(PROJECT_ROOT)
    reports = {
        report["scenario_id"]: report
        for report in template["scenario_reports"]  # type: ignore[index]
    }

    assert tuple(reports) == benchmark_scenario_ids()
    for scenario in matrix["scenarios"]:  # type: ignore[index]
        scenario_id = scenario["scenario_id"]
        report = reports[scenario_id]
        assert report["deterministic_seed"] == scenario["runtime_seed"]
        assert report["expected_outputs"]["expected_ranges"] == scenario[
            "expected_ranges"
        ]
        assert report["expected_outputs"]["fidelity_expectation"] == scenario[
            "fidelity_expectation"
        ]


@pytest.mark.parametrize("scenario_id", benchmark_scenario_ids())
def test_benchmark_acceptance_backend_summaries_are_deterministic(
    scenario_id: str,
) -> None:
    scenario = benchmark_scenario_by_id(scenario_id, PROJECT_ROOT)
    config = load_config(PROJECT_ROOT / str(scenario["config_path"]))

    first = _backend_summary(config)
    second = _backend_summary(config)

    assert first == second
    assert first["derived_constellation_summary"] == scenario[
        "derived_constellation_summary"
    ]
    assert first["traffic_demand_summary"]["traffic_class"] == scenario[
        "traffic_class"
    ]
    assert first["traffic_demand_summary"]["destination_type"] == scenario[
        "traffic_destination_type"
    ]
    assert first["compute_resource_summary"]["compute_node_count"] == scenario[
        "compute_node_count"
    ]


@pytest.mark.parametrize("scenario_id", benchmark_scenario_ids())
def test_benchmark_acceptance_scale_policy_matches_matrix(
    scenario_id: str,
) -> None:
    scenario = benchmark_scenario_by_id(scenario_id, PROJECT_ROOT)
    config = load_config(PROJECT_ROOT / str(scenario["config_path"]))
    fidelity = _fidelity_summary(config)
    expected = scenario["fidelity_expectation"]

    assert fidelity == scenario["fidelity_summary"]
    assert {
        "orbit_update_mode": fidelity["orbit_update_mode"],
        "metrics_mode": fidelity["metrics_mode"],
        "space_link_mode": fidelity["space_link_mode"],
    } == expected


def test_benchmark_acceptance_runtime_kpi_ranges_for_small_baseline(
    tmp_path: Path,
) -> None:
    scenario = benchmark_scenario_by_id("small_demo_72sat", PROJECT_ROOT)
    config = load_config(PROJECT_ROOT / str(scenario["config_path"]))
    control_plane = _control_plane(tmp_path, "small_demo_72sat_kpi_ranges")

    initialize_ack = control_plane.handle_raw_message(
        json.dumps(
            {
                "type": "RUNTIME_CONTROL",
                "action": "INITIALIZE",
                "payload": config_to_dict(config),
            }
        )
    )
    assert initialize_ack["ok"] is True

    start_ack = control_plane.handle_raw_message(
        json.dumps({"type": "RUNTIME_CONTROL", "action": "START"})
    )
    assert start_ack["ok"] is True
    for _ in range(2):
        assert control_plane._require_session().advance_control_step()
        control_plane._require_advance_loop().publish_pending()

    status = control_plane.runtime_status()["status"]
    metrics = status["metrics_summary"]

    _assert_non_negative(metrics, "network_quality_effective_throughput_mbps")
    _assert_non_negative(
        metrics,
        "network_quality_effective_available_throughput_mbps",
    )
    _assert_non_negative(metrics, "network_quality_effective_latency_avg_s")
    _assert_non_negative(
        metrics,
        "network_quality_effective_delay_variation_proxy_s",
    )
    _assert_ratio(metrics, "network_quality_effective_loss_proxy_rate")
    _assert_ratio(metrics, "network_quality_route_blocking_ratio")
    _assert_ratio(metrics, "network_quality_failed_flow_ratio")
    _assert_ratio(metrics, "network_quality_congestion_proxy")

    provenance = status["network_kpi_provenance_v2"]
    assert provenance["packet_level_simulation"] is False
    assert provenance["kpi_count"] == 6
    assert all(
        item["status"] == "OBSERVED" and item["current_value"] is not None
        for item in provenance["kpis"]
        if isinstance(item, dict)
    )


def test_benchmark_acceptance_expected_ranges_match_config_sources() -> None:
    for scenario_id in benchmark_scenario_ids():
        scenario = benchmark_scenario_by_id(scenario_id, PROJECT_ROOT)
        config = load_config(PROJECT_ROOT / str(scenario["config_path"]))
        for expected_range in scenario["expected_ranges"]:
            source = str(expected_range["source"])
            value = float(_config_value(config, source))
            assert expected_range["minimum"] <= value <= expected_range["maximum"]


def _backend_summary(config: SEESConfig) -> dict[str, object]:
    return scenario_builder_backend_summary(
        scenario_builder_config_from_sees_config(config)
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


def _config_value(config: SEESConfig, source: str) -> int | float:
    value: Any = config
    for part in source.split("."):
        value = getattr(value, part)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{source} did not resolve to a numeric value")
    return value


def _assert_non_negative(metrics: dict[str, object], key: str) -> None:
    value = metrics[key]
    assert isinstance(value, (int, float))
    assert value >= 0.0


def _assert_ratio(metrics: dict[str, object], key: str) -> None:
    value = metrics[key]
    assert isinstance(value, (int, float))
    assert 0.0 <= value <= 1.0


def _control_plane(tmp_path: Path, scenario_id: str) -> DemoControlPlane:
    return DemoControlPlane.from_result(
        run_integration_demo(_base_demo_config()),
        config_output_path=tmp_path / f"{scenario_id}_sees_control.yaml",
        generated_config_output_path=tmp_path
        / f"{scenario_id}_generated_full_system_demo.json",
    )


def _base_demo_config() -> DemoConfig:
    return DemoConfig(
        seed=1234,
        satellite_count=8,
        ground_user_count=20,
        ground_station_count=1,
        compute_node_count=2,
        duration_seconds=180,
        orbit_tick_seconds=1,
        network_slot_seconds=30,
        flow_interval_seconds=30,
        task_interval_seconds=30,
        cell_count=10,
        state_snapshot_interval_events=20,
        metric_sample_interval=10,
        websocket_events="/stream/events",
        websocket_state="/stream/state",
        metrics_snapshot="/metrics/snapshot",
        scenario_config="/scenario/config",
        backend_host="127.0.0.1",
        backend_port=8765,
    )
