from __future__ import annotations

import json
from pathlib import Path

from leo_twin.services.benchmark_scenarios import (
    BENCHMARK_SCENARIO_MATRIX_V1_ID,
    benchmark_scenario_ids,
)
from leo_twin.services.model_verification_report import (
    MODEL_VERIFICATION_REPORT_TEMPLATE_V1_ID,
    model_verification_report_template_v1_to_dict,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_model_verification_report_template_is_deterministic_json_ready() -> None:
    first = model_verification_report_template_v1_to_dict(PROJECT_ROOT)
    second = model_verification_report_template_v1_to_dict(PROJECT_ROOT)

    assert first == second
    assert first["template_id"] == MODEL_VERIFICATION_REPORT_TEMPLATE_V1_ID
    assert first["benchmark_matrix_id"] == BENCHMARK_SCENARIO_MATRIX_V1_ID
    assert first["scenario_report_count"] == 3
    assert json.loads(json.dumps(first, sort_keys=True))["template_id"] == (
        MODEL_VERIFICATION_REPORT_TEMPLATE_V1_ID
    )


def test_model_verification_report_template_covers_all_benchmark_scenarios() -> None:
    template = model_verification_report_template_v1_to_dict(PROJECT_ROOT)
    reports = {
        report["scenario_id"]: report
        for report in template["scenario_reports"]  # type: ignore[index]
    }

    assert tuple(reports) == benchmark_scenario_ids()
    assert reports["small_demo_72sat"]["deterministic_seed"] == 20260705
    assert reports["medium_demo_300sat"]["configuration_boundary_conditions"][
        "satellite_count"
    ] == 300
    assert reports["scale_demo_1200sat_short"]["configuration_boundary_conditions"][
        "satellite_count"
    ] == 1200


def test_model_verification_report_template_records_formula_checks() -> None:
    template = model_verification_report_template_v1_to_dict(PROJECT_ROOT)
    catalog = template["formula_catalog"]
    network_checks = catalog["network_kpi_checks"]  # type: ignore[index]
    compute_check = catalog["compute_service_time_check"]  # type: ignore[index]

    metrics = tuple(check["metric"] for check in network_checks)
    assert metrics == tuple(sorted(metrics))
    assert set(metrics) == {
        "CONGESTION_PRESSURE",
        "EFFECTIVE_DELAY_VARIATION_PROXY",
        "EFFECTIVE_LATENCY",
        "EFFECTIVE_LOSS_PROXY",
        "EFFECTIVE_THROUGHPUT",
        "ROUTE_BLOCKING_RATIO",
    }
    assert all(check["packet_level_metric"] is False for check in network_checks)
    assert all(check["formula_summary"] for check in network_checks)
    assert "service_time is the maximum lane time" in compute_check[
        "formula_summary"
    ]
    assert compute_check["model"] == "MAX_ACTIVE_RESOURCE_LANE_TIME"


def test_model_verification_report_template_records_large_scale_boundaries() -> None:
    template = model_verification_report_template_v1_to_dict(PROJECT_ROOT)
    reports = {
        report["scenario_id"]: report
        for report in template["scenario_reports"]  # type: ignore[index]
    }
    large = reports["scale_demo_1200sat_short"]
    boundaries = large["configuration_boundary_conditions"]

    assert large["scale_tier"] == "LARGE_AGGREGATED"
    assert boundaries["orbit_update_mode"] == "BATCH"
    assert boundaries["metrics_mode"] == "AGGREGATED"
    assert boundaries["space_link_mode"] == "BOUNDED_CANDIDATE"
    assert "bounded candidate updates are enabled" in boundaries[
        "scale_limit_reason"
    ]


def test_model_verification_report_template_defines_expected_outputs_and_evidence() -> None:
    template = model_verification_report_template_v1_to_dict(PROJECT_ROOT)
    report = template["scenario_reports"][0]  # type: ignore[index]
    outputs = report["expected_outputs"]
    evidence = report["evidence_checklist"]

    assert "events.jsonl" in outputs["result_artifact_expectation"]
    assert "metrics.csv" in outputs["result_artifact_expectation"]
    assert "summary.json" in outputs["result_artifact_expectation"]
    assert "network_kpi_provenance_v2" in outputs["runtime_status_fields"]
    assert "WorldSnapshot.fidelity_summary" in outputs["state_stream_fields"]
    assert tuple(item["evidence"] for item in evidence) == (
        "config_load",
        "backend_summary_determinism",
        "live_runtime_smoke",
        "artifact_manifest",
    )
    assert all(item["required"] is True for item in evidence)


def test_model_verification_report_template_preserves_scope_boundaries() -> None:
    template = model_verification_report_template_v1_to_dict(PROJECT_ROOT)
    exclusions = template["global_exclusions"]

    assert exclusions["forbidden_integrations"] == ("STK", "EXATA", "AFSIM", "DDS")
    assert exclusions["packet_level_simulation"] is False
    assert "PACKET_LEVEL_SIMULATION" in exclusions["network_excluded_capabilities"]
    assert "REAL_CODE_EXECUTION" in exclusions["compute_excluded_capabilities"]
    assert "FAIL_NON_DETERMINISTIC" in template["review_decision_values"]
