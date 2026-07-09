"""Build deterministic control payloads for disposable acceptance runs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from leo_twin.schema.config import SEESConfig, config_to_dict  # noqa: E402
from leo_twin.schema.config_loader import load_config, merge_config_update  # noqa: E402
from leo_twin.services.benchmark_scenarios import (  # noqa: E402
    benchmark_scenario_matrix_v1_to_dict,
)
from leo_twin.services.result_package_contract import (  # noqa: E402
    RUNTIME_EXPORT_BENCHMARK_ACCEPTANCE_BINDING_V1_ID,
    RUNTIME_EXPORT_PACKAGE_ACCEPTANCE_REPORT_V1_ID,
)


STANDARD_ACCEPTANCE_CONFIGS = (
    "configs/acceptance/small_demo_72sat.yaml",
    "configs/acceptance/medium_demo_300sat.yaml",
    "configs/acceptance/scale_demo_1200sat_short.yaml",
)
RUNTIME_CONFIG_DRIFT_PATHS = (
    "configs/sees_control.yaml",
    "configs/generated_full_system_demo.json",
)
_FLAT_SCENARIO_CONTROL_KEYS = (
    "satellite_count",
    "user_count",
    "compute_nodes",
    "compute_capacity",
    "compute_cpu_gflops_fp64",
    "compute_gpu_tflops_fp32",
    "compute_gpu_tflops_fp16",
    "compute_npu_tops_int8",
    "compute_memory_gb",
    "compute_storage_gb",
    "compute_scheduling_policy",
    "initial_workload_smoothing_enabled",
    "initial_workload_window_s",
    "max_initial_events_per_tick",
    "workload_smoothing_mode",
)
_NESTED_SCENARIO_ONLY_KEYS = (
    "ground_station_count",
    "cell_count",
)


def initialize_payload_from_config(config: SEESConfig) -> dict[str, Any]:
    """Flatten a SEES config into the legacy-compatible INITIALIZE payload."""

    data = config_to_dict(config)
    scenario = dict(data["scenario"])
    payload: dict[str, Any] = {}
    payload.update({key: scenario[key] for key in _FLAT_SCENARIO_CONTROL_KEYS})
    payload["scenario"] = {
        key: scenario[key]
        for key in _NESTED_SCENARIO_ONLY_KEYS
        if key in scenario
    }
    payload.update(data["network"])
    payload.update(data["runtime"])
    payload["orbit"] = scenario["orbit"]
    payload["traffic_model"] = scenario["traffic_model"]
    payload["ui"] = data["ui"]

    # Validate the exact payload shape accepted by /control before emitting it.
    merge_config_update(SEESConfig(), payload)
    return payload


def scenario_id_for_config(config_path: Path, repo_root: Path) -> str:
    """Resolve the benchmark id for a config path when it is in the matrix."""

    normalized = _repo_relative_path(config_path, repo_root)
    matrix = benchmark_scenario_matrix_v1_to_dict(repo_root)
    for scenario in matrix["scenarios"]:
        if scenario["config_path"].replace("\\", "/") == normalized:
            return str(scenario["scenario_id"])
    return config_path.stem


def benchmark_acceptance_plan_for_config(
    config_path: Path,
    repo_root: Path,
) -> dict[str, Any]:
    """Return matrix-owned benchmark evidence expected for one config."""

    normalized = _repo_relative_path(config_path, repo_root)
    matrix = benchmark_scenario_matrix_v1_to_dict(repo_root)
    for scenario in matrix["scenarios"]:
        if scenario["config_path"].replace("\\", "/") != normalized:
            continue
        expected_ranges = tuple(scenario["expected_ranges"])
        runtime_expectation = dict(scenario["runtime_status_expectation"])
        return {
            "matrix_id": matrix["matrix_id"],
            "scenario_id": scenario["scenario_id"],
            "binding_id": RUNTIME_EXPORT_BENCHMARK_ACCEPTANCE_BINDING_V1_ID,
            "acceptance_report_id": RUNTIME_EXPORT_PACKAGE_ACCEPTANCE_REPORT_V1_ID,
            "acceptance_gate_check_id": "benchmark_scenario_gate",
            "expected_range_count": len(expected_ranges),
            "expected_range_metrics": tuple(
                str(item["metric"]) for item in expected_ranges
            ),
            "expected_range_sources": tuple(
                str(item["source"]) for item in expected_ranges
            ),
            "runtime_status_required_fields": tuple(
                runtime_expectation["required_fields"]
            ),
            "fidelity_expectation": dict(scenario["fidelity_expectation"]),
            "result_package_evidence_files": (
                "config_snapshot.json",
                "export_package_audit_index_v1.json",
            ),
            "boundary_conditions": (
                "NO_EVENT_KERNEL_BEHAVIOR_CHANGE",
                "NO_PACKET_LEVEL_SIMULATION",
                "NO_EXTERNAL_SIMULATOR_ARTIFACTS",
            ),
        }
    return {
        "matrix_id": matrix["matrix_id"],
        "scenario_id": config_path.stem,
        "binding_id": RUNTIME_EXPORT_BENCHMARK_ACCEPTANCE_BINDING_V1_ID,
        "acceptance_report_id": RUNTIME_EXPORT_PACKAGE_ACCEPTANCE_REPORT_V1_ID,
        "acceptance_gate_check_id": "benchmark_scenario_gate",
        "expected_range_count": 0,
        "expected_range_metrics": (),
        "expected_range_sources": (),
        "runtime_status_required_fields": (),
        "fidelity_expectation": {},
        "result_package_evidence_files": (),
        "boundary_conditions": (
            "NO_EVENT_KERNEL_BEHAVIOR_CHANGE",
            "NO_PACKET_LEVEL_SIMULATION",
            "NO_EXTERNAL_SIMULATOR_ARTIFACTS",
        ),
    }

def build_scenario_plan(config_path: str | Path, repo_root: str | Path) -> dict[str, Any]:
    """Build a deterministic disposable-run plan for one acceptance config."""

    root = Path(repo_root).resolve()
    resolved_config = _resolve_config_path(config_path, root)
    config = load_config(resolved_config)
    payload = initialize_payload_from_config(config)
    data = config_to_dict(config)
    scenario_id = scenario_id_for_config(resolved_config, root)
    config_rel = _repo_relative_path(resolved_config, root)
    benchmark_acceptance = benchmark_acceptance_plan_for_config(
        resolved_config,
        root,
    )
    return {
        "scenario_id": scenario_id,
        "config_path": config_rel,
        "initialize_payload": payload,
        "expectations": {
            "satellite_count": data["scenario"]["satellite_count"],
            "user_count": data["scenario"]["user_count"],
            "compute_node_count": data["scenario"]["compute_nodes"],
            "runtime_duration_s": data["runtime"]["duration"],
            "runtime_mode": data["runtime"]["mode"],
            "orbit_update_mode": data["scenario"]["orbit"]["orbit_update_mode"],
            "space_link_mode": data["network"]["space_link_mode"],
            "application_protocol": data["network"]["application_protocol"],
            "transport_protocol": data["network"]["transport_protocol"],
        },
        "benchmark_acceptance": benchmark_acceptance,
        "control_sequence": ("RESET", "INITIALIZE", "START", "STOP"),
        "acceptance_command": (
            "scripts/verify_product_acceptance.ps1",
            "-AcceptanceConfig",
            config_rel,
        ),
        "cleanup_policy": {
            "restore_runtime_config_paths": RUNTIME_CONFIG_DRIFT_PATHS,
            "stop_services_unless_keep_services": True,
        },
        "constraints": {
            "event_kernel_frozen": True,
            "packet_level_simulation": False,
            "forbidden_integrations": ("STK", "EXATA", "AFSIM", "DDS"),
        },
    }


def build_standard_plan(repo_root: str | Path) -> dict[str, Any]:
    """Build the three-scenario disposable acceptance plan."""

    root = Path(repo_root).resolve()
    matrix = benchmark_scenario_matrix_v1_to_dict(root)
    return {
        "type": "DISPOSABLE_ACCEPTANCE_PLAN",
        "version": "v1",
        "benchmark_matrix_id": matrix["matrix_id"],
        "benchmark_acceptance_binding_id": (
            RUNTIME_EXPORT_BENCHMARK_ACCEPTANCE_BINDING_V1_ID
        ),
        "package_acceptance_report_id": RUNTIME_EXPORT_PACKAGE_ACCEPTANCE_REPORT_V1_ID,
        "acceptance_gate_check_id": "benchmark_scenario_gate",
        "scenario_count": len(STANDARD_ACCEPTANCE_CONFIGS),
        "scenarios": [
            build_scenario_plan(config_path, root)
            for config_path in STANDARD_ACCEPTANCE_CONFIGS
        ],
        "runtime_config_drift_paths": RUNTIME_CONFIG_DRIFT_PATHS,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=str(PROJECT_ROOT))
    parser.add_argument("--config", default="")
    parser.add_argument("--standard-plan", action="store_true")
    args = parser.parse_args(argv)

    if args.standard_plan:
        result = build_standard_plan(args.repo_root)
    elif args.config:
        result = build_scenario_plan(args.config, args.repo_root)
    else:
        parser.error("--config or --standard-plan is required")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


def _resolve_config_path(config_path: str | Path, repo_root: Path) -> Path:
    path = Path(config_path)
    if not path.is_absolute():
        path = repo_root / path
    resolved = path.resolve()
    if not resolved.exists():
        raise FileNotFoundError(f"acceptance config not found: {resolved}")
    return resolved


def _repo_relative_path(path: Path, repo_root: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
