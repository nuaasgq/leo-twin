from __future__ import annotations

import pytest

from leo_twin.models.compute import (
    ComputeNode,
    ComputeResourceVector,
    TaskResourceDemand,
    compute_resource_vector_from_node,
    estimate_compute_service_time,
    estimate_task_service_time,
    task_resource_demand_from_request,
)
from leo_twin.schema import TaskRequest


def test_legacy_capacity_vector_matches_scalar_compute_model() -> None:
    resources = ComputeResourceVector.from_capacity(
        20.0,
        memory_gb=4.0,
        storage_gb=1.0,
    )
    demand = TaskResourceDemand.from_compute_demand(
        40.0,
        memory_gb=1.0,
        input_data_mb=128.0,
        output_data_mb=128.0,
    )

    estimate = estimate_compute_service_time(resources, demand)

    assert resources.capacity == 20.0
    assert estimate.service_time == pytest.approx(2.0)
    assert estimate.bottleneck_resource == "cpu_gflops_fp32"
    assert estimate.resource_times == (("cpu_gflops_fp32", 2.0),)


def test_task_service_time_helper_preserves_legacy_scheduler_timing() -> None:
    node = ComputeNode(
        "sat-001",
        capacity=40.0,
        cpu_gflops_fp64=8.0,
        gpu_tflops_fp32=2.5,
        gpu_tflops_fp16=5.0,
        npu_tops_int8=12.0,
        memory_gb=32.0,
        storage_gb=512.0,
    )
    task = TaskRequest(
        task_id="task-a",
        source_id="user-a",
        submit_time=0.0,
        compute_demand=100.0,
        data_size=1.0,
    )

    resources = compute_resource_vector_from_node(node)
    demand = task_resource_demand_from_request(task)
    estimate = estimate_task_service_time(node, task)

    assert resources == ComputeResourceVector(
        cpu_gflops_fp32=40.0,
        cpu_gflops_fp64=8.0,
        gpu_tflops_fp32=2.5,
        gpu_tflops_fp16=5.0,
        npu_tops_int8=12.0,
        memory_gb=32.0,
        storage_gb=512.0,
    )
    assert demand == TaskResourceDemand(cpu_ops=100_000_000_000.0)
    assert estimate.service_time == pytest.approx(2.5)
    assert estimate.bottleneck_resource == "cpu_gflops_fp32"


def test_task_service_time_helper_uses_explicit_task_resource_demand() -> None:
    node = ComputeNode(
        "gpu-node",
        capacity=100.0,
        gpu_tflops_fp32=2.0,
        gpu_tflops_fp16=4.0,
        npu_tops_int8=8.0,
        memory_gb=16.0,
        storage_gb=2.0,
    )
    task = TaskRequest(
        task_id="task-gpu",
        source_id="user-a",
        submit_time=0.0,
        compute_demand=1.0,
        data_size=1.0,
        fp32_ops=10_000_000_000_000.0,
        memory_gb=4.0,
        input_data_mb=256.0,
        output_data_mb=128.0,
    )

    demand = task_resource_demand_from_request(task)
    estimate = estimate_task_service_time(node, task)

    assert demand == TaskResourceDemand(
        fp32_ops=10_000_000_000_000.0,
        memory_gb=4.0,
        input_data_mb=256.0,
        output_data_mb=128.0,
    )
    assert estimate.service_time == pytest.approx(5.0)
    assert estimate.bottleneck_resource == "gpu_tflops_fp32"


def test_cpu_only_task_uses_cpu_bottleneck() -> None:
    resources = ComputeResourceVector(
        cpu_gflops_fp32=50.0,
        memory_gb=8.0,
        storage_gb=2.0,
    )
    demand = TaskResourceDemand(
        cpu_ops=125_000_000_000.0,
        memory_gb=2.0,
        input_data_mb=256.0,
        output_data_mb=128.0,
    )

    estimate = estimate_compute_service_time(resources, demand)

    assert estimate.service_time == pytest.approx(2.5)
    assert estimate.bottleneck_resource == "cpu_gflops_fp32"


def test_gpu_fp32_task_uses_gpu_bottleneck() -> None:
    resources = ComputeResourceVector(
        cpu_gflops_fp32=100.0,
        gpu_tflops_fp32=4.0,
        memory_gb=16.0,
        storage_gb=4.0,
    )
    demand = TaskResourceDemand(
        cpu_ops=5_000_000_000.0,
        fp32_ops=20_000_000_000_000.0,
        memory_gb=4.0,
        input_data_mb=512.0,
        output_data_mb=512.0,
    )

    estimate = estimate_compute_service_time(resources, demand)

    assert estimate.service_time == pytest.approx(5.0)
    assert estimate.bottleneck_resource == "gpu_tflops_fp32"
    assert tuple(name for name, _ in estimate.resource_times) == (
        "cpu_gflops_fp32",
        "gpu_tflops_fp32",
    )
    assert tuple(value for _, value in estimate.resource_times) == pytest.approx(
        (0.05, 5.0)
    )


def test_npu_int8_task_uses_npu_bottleneck() -> None:
    resources = ComputeResourceVector(
        npu_tops_int8=8.0,
        memory_gb=8.0,
        storage_gb=2.0,
    )
    demand = TaskResourceDemand(
        int8_ops=16_000_000_000_000.0,
        memory_gb=1.0,
        input_data_mb=128.0,
        output_data_mb=128.0,
    )

    estimate = estimate_compute_service_time(resources, demand)

    assert estimate.service_time == pytest.approx(2.0)
    assert estimate.bottleneck_resource == "npu_tops_int8"
    assert estimate.resource_times == (("npu_tops_int8", 2.0),)


def test_service_time_estimator_is_deterministic_for_equal_inputs() -> None:
    resources = ComputeResourceVector(
        cpu_gflops_fp32=10.0,
        gpu_tflops_fp32=1.0,
        npu_tops_int8=2.0,
        memory_gb=8.0,
        storage_gb=2.0,
    )
    demand = TaskResourceDemand(
        cpu_ops=10_000_000_000.0,
        fp32_ops=1_000_000_000_000.0,
        int8_ops=2_000_000_000_000.0,
        memory_gb=2.0,
        input_data_mb=100.0,
        output_data_mb=100.0,
    )

    first = estimate_compute_service_time(resources, demand)
    second = estimate_compute_service_time(resources, demand)

    assert first == second
    assert first.service_time == pytest.approx(1.0)
    assert first.bottleneck_resource == "cpu_gflops_fp32"


def test_estimator_rejects_unavailable_processing_resource() -> None:
    resources = ComputeResourceVector(memory_gb=8.0, storage_gb=1.0)
    demand = TaskResourceDemand(fp32_ops=1_000_000_000_000.0)

    with pytest.raises(ValueError, match="gpu_tflops_fp32"):
        estimate_compute_service_time(resources, demand)


def test_estimator_rejects_memory_or_storage_capacity_overrun() -> None:
    resources = ComputeResourceVector(
        cpu_gflops_fp32=10.0,
        memory_gb=1.0,
        storage_gb=1.0,
    )

    with pytest.raises(ValueError, match="memory_gb"):
        estimate_compute_service_time(
            resources,
            TaskResourceDemand(cpu_ops=1.0, memory_gb=2.0),
        )

    with pytest.raises(ValueError, match="storage_gb"):
        estimate_compute_service_time(
            resources,
            TaskResourceDemand(
                cpu_ops=1.0,
                input_data_mb=1024.0,
                output_data_mb=1.0,
            ),
        )
