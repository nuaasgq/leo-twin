from __future__ import annotations

import json

import pytest

from leo_twin.models.compute import (
    ComputeResourceVector,
    TaskResourceDemand,
    estimate_compute_service_time,
)
from leo_twin.models.orbit import AutoPlaneAllocator
from leo_twin.schema import (
    COMPUTE_RESOURCE_CONTRACT_V2_ID,
    ComputeResourceLaneKind,
    TaskDemandLaneKind,
    compute_resource_contract_v2_to_dict,
    default_compute_resource_contract_v2,
)
from leo_twin.services.derived_summary import build_backend_derived_summary


def test_compute_resource_contract_v2_is_deterministic_and_json_ready() -> None:
    first = compute_resource_contract_v2_to_dict()
    second = compute_resource_contract_v2_to_dict(default_compute_resource_contract_v2())

    assert first == second
    assert first["contract_id"] == COMPUTE_RESOURCE_CONTRACT_V2_ID
    assert first["version"] == "v2"
    assert first["resource_model"] == "ComputeResourceVector"
    assert first["node_role"] == "SATELLITE_HOSTED_COMPUTE"
    assert "TASK_ARRIVAL" in first["runtime_event_inputs"]
    assert "ComputeNodeState" in first["runtime_state_outputs"]
    assert json.loads(json.dumps(first, sort_keys=True))["contract_id"] == (
        COMPUTE_RESOURCE_CONTRACT_V2_ID
    )


def test_compute_resource_contract_v2_defines_all_resource_lanes() -> None:
    contract = compute_resource_contract_v2_to_dict()
    lanes = _resource_lanes(contract)

    assert tuple(lanes) == tuple(lane.value for lane in ComputeResourceLaneKind)
    assert lanes["CPU_FP32"]["capacity_field"] == "compute_capacity"
    assert lanes["CPU_FP32"]["unit"] == "GFLOPS FP32"
    assert lanes["CPU_FP32"]["compatibility_role"] == "legacy_scalar_capacity"
    assert lanes["CPU_FP32"]["throughput_lane"] is True
    assert lanes["GPU_FP32"]["capacity_field"] == "compute_gpu_tflops_fp32"
    assert lanes["GPU_FP32"]["node_state_used_field"] == "used_gpu_tflops_fp32"
    assert lanes["NPU_INT8"]["unit"] == "TOPS INT8"
    assert lanes["MEMORY"]["throughput_lane"] is False
    assert lanes["STORAGE"]["compatibility_role"] == (
        "input_output_data_capacity_limit"
    )


def test_compute_resource_contract_v2_defines_task_demand_lanes() -> None:
    contract = compute_resource_contract_v2_to_dict()
    demands = _demand_lanes(contract)

    assert tuple(demands) == tuple(lane.value for lane in TaskDemandLaneKind)
    assert demands["CPU_OPS"]["demand_field"] == "cpu_ops"
    assert demands["CPU_OPS"]["required_resource_lane"] == "CPU_FP32"
    assert "fallback to CPU_FP64" in demands["CPU_OPS"]["estimator_role"]
    assert demands["FP32_OPS"]["required_resource_lane"] == "GPU_FP32"
    assert demands["FP16_OPS"]["required_resource_lane"] == "GPU_FP16"
    assert demands["INT8_OPS"]["required_resource_lane"] == "NPU_INT8"
    assert demands["INPUT_DATA_MB"]["required_resource_lane"] == "STORAGE"
    assert demands["OUTPUT_DATA_MB"]["required_resource_lane"] == "STORAGE"


def test_compute_resource_contract_v2_matches_service_time_estimator_semantics() -> None:
    contract = compute_resource_contract_v2_to_dict()
    estimator = contract["service_time_estimator"]
    assert isinstance(estimator, dict)
    assert estimator["model"] == "MAX_ACTIVE_RESOURCE_LANE_TIME"
    assert "Memory and storage are capacity limits" in estimator[
        "capacity_limit_policy"
    ]
    assert "ComputeNode.capacity maps to cpu_gflops_fp32" in estimator[
        "legacy_mapping"
    ]

    resources = ComputeResourceVector(
        cpu_gflops_fp32=100.0,
        gpu_tflops_fp32=2.0,
        npu_tops_int8=8.0,
        memory_gb=16.0,
        storage_gb=4.0,
    )
    demand = TaskResourceDemand(
        cpu_ops=5_000_000_000.0,
        fp32_ops=20_000_000_000_000.0,
        int8_ops=8_000_000_000_000.0,
        memory_gb=4.0,
        input_data_mb=512.0,
        output_data_mb=512.0,
    )

    estimate = estimate_compute_service_time(resources, demand)

    assert estimate.service_time == pytest.approx(10.0)
    assert estimate.bottleneck_resource == "gpu_tflops_fp32"
    assert dict(estimate.resource_times) == {
        "cpu_gflops_fp32": pytest.approx(0.05),
        "gpu_tflops_fp32": pytest.approx(10.0),
        "npu_tops_int8": pytest.approx(1.0),
    }


def test_backend_summary_exposes_compute_resource_contract_v2() -> None:
    allocation = AutoPlaneAllocator.allocate(satellite_count=72, plane_count=12)

    summary = build_backend_derived_summary(
        constellation=allocation,
        satellite_count=72,
        user_count=100,
        compute_node_count=72,
        compute_capacity=40.0,
        compute_cpu_gflops_fp64=8.0,
        compute_gpu_tflops_fp32=2.5,
        compute_gpu_tflops_fp16=5.0,
        compute_npu_tops_int8=12.0,
        compute_memory_gb=32.0,
        compute_storage_gb=512.0,
        flow_count=20,
        demand_capacity=25.0,
        task_compute_demand=20.0,
        task_data_size=2.0,
        application_protocol="TASK_OFFLOAD_FLOW",
    )

    contract = summary["compute_resource_contract_v2"]
    assert isinstance(contract, dict)
    assert contract["contract_id"] == COMPUTE_RESOURCE_CONTRACT_V2_ID
    assert contract["configured_node_profile"] == {
        "compute_node_count": 72,
        "legacy_capacity_per_node": 40.0,
        "cpu_gflops_fp32_per_node": 40.0,
        "cpu_gflops_fp64_per_node": 8.0,
        "gpu_tflops_fp32_per_node": 2.5,
        "gpu_tflops_fp16_per_node": 5.0,
        "npu_tops_int8_per_node": 12.0,
        "memory_gb_per_node": 32.0,
        "storage_gb_per_node": 512.0,
    }


def _resource_lanes(contract: dict[str, object]) -> dict[str, dict[str, object]]:
    lanes = contract["resource_lanes"]
    assert isinstance(lanes, tuple)
    return {str(lane["lane"]): lane for lane in lanes if isinstance(lane, dict)}


def _demand_lanes(contract: dict[str, object]) -> dict[str, dict[str, object]]:
    lanes = contract["task_demand_lanes"]
    assert isinstance(lanes, tuple)
    return {str(lane["lane"]): lane for lane in lanes if isinstance(lane, dict)}
