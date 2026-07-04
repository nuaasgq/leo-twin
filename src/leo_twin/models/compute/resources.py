"""Deterministic compute resource vectors and service-time estimation."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any

from leo_twin.models.compute.contracts import ComputeNode
from leo_twin.schema import TaskRequest


_OPS_PER_GFLOP = 1_000_000_000.0
_OPS_PER_TFLOP = 1_000_000_000_000.0
_MB_PER_GB = 1024.0
_NO_BOTTLENECK = "none"


@dataclass(frozen=True)
class ComputeResourceVector:
    """Compute resource capacity vector for deterministic model estimates.

    The legacy scalar ``capacity`` maps to ``cpu_gflops_fp32`` so existing
    compute-demand divided by capacity semantics can be preserved explicitly.
    Memory and storage are capacity limits, not throughput estimators.
    """

    cpu_gflops_fp32: float = 0.0
    cpu_gflops_fp64: float = 0.0
    gpu_tflops_fp32: float = 0.0
    gpu_tflops_fp16: float = 0.0
    npu_tops_int8: float = 0.0
    memory_gb: float = 0.0
    storage_gb: float = 0.0

    def __post_init__(self) -> None:
        for field_name in _RESOURCE_FIELD_NAMES:
            _set_non_negative_float(self, field_name)

    @property
    def capacity(self) -> float:
        """Legacy scalar capacity view used by existing compute scheduling."""

        return self.cpu_gflops_fp32

    @classmethod
    def from_capacity(
        cls,
        capacity: float,
        *,
        memory_gb: float = 0.0,
        storage_gb: float = 0.0,
    ) -> "ComputeResourceVector":
        """Build a vector from the existing scalar compute capacity contract."""

        _require_positive_number(capacity, "capacity")
        return cls(
            cpu_gflops_fp32=float(capacity),
            memory_gb=memory_gb,
            storage_gb=storage_gb,
        )


@dataclass(frozen=True)
class TaskResourceDemand:
    """Task resource demand consumed by the deterministic service estimator."""

    cpu_ops: float = 0.0
    fp32_ops: float = 0.0
    fp16_ops: float = 0.0
    int8_ops: float = 0.0
    memory_gb: float = 0.0
    input_data_mb: float = 0.0
    output_data_mb: float = 0.0

    def __post_init__(self) -> None:
        for field_name in _DEMAND_FIELD_NAMES:
            _set_non_negative_float(self, field_name)

    @classmethod
    def from_compute_demand(
        cls,
        compute_demand: float,
        *,
        memory_gb: float = 0.0,
        input_data_mb: float = 0.0,
        output_data_mb: float = 0.0,
    ) -> "TaskResourceDemand":
        """Build a CPU demand from the existing scalar task demand contract.

        Existing ``compute_demand / capacity`` scheduling is reproduced by
        interpreting one legacy demand unit as one giga-operation.
        """

        _require_non_negative_number(compute_demand, "compute_demand")
        return cls(
            cpu_ops=float(compute_demand) * _OPS_PER_GFLOP,
            memory_gb=memory_gb,
            input_data_mb=input_data_mb,
            output_data_mb=output_data_mb,
        )


@dataclass(frozen=True)
class ComputeServiceTimeEstimate:
    """Deterministic bottleneck service-time estimate."""

    service_time: float
    bottleneck_resource: str
    resource_times: tuple[tuple[str, float], ...] = ()

    def __post_init__(self) -> None:
        _require_non_negative_number(self.service_time, "service_time")
        if not isinstance(self.bottleneck_resource, str) or not self.bottleneck_resource:
            raise TypeError("bottleneck_resource must be a non-empty str")
        if not isinstance(self.resource_times, tuple):
            raise TypeError("resource_times must be a tuple")
        for item in self.resource_times:
            if not isinstance(item, tuple) or len(item) != 2:
                raise TypeError("resource_times entries must be 2-tuples")
            resource_name, resource_time = item
            if not isinstance(resource_name, str) or not resource_name:
                raise TypeError("resource name must be a non-empty str")
            _require_non_negative_number(resource_time, "resource time")


def estimate_compute_service_time(
    resources: ComputeResourceVector,
    demand: TaskResourceDemand,
) -> ComputeServiceTimeEstimate:
    """Estimate service time as the maximum active resource lane time.

    The estimator is a deterministic abstraction only. It does not execute work,
    touch the event kernel, or infer memory/storage throughput.
    """

    if not isinstance(resources, ComputeResourceVector):
        raise TypeError("resources must be ComputeResourceVector")
    if not isinstance(demand, TaskResourceDemand):
        raise TypeError("demand must be TaskResourceDemand")

    _require_capacity_limits(resources, demand)

    resource_times: list[tuple[str, float]] = []
    if demand.cpu_ops > 0.0:
        resource_name, rate_gflops = _cpu_rate(resources)
        resource_times.append(
            (resource_name, demand.cpu_ops / (rate_gflops * _OPS_PER_GFLOP))
        )
    if demand.fp32_ops > 0.0:
        resource_times.append(
            (
                "gpu_tflops_fp32",
                _resource_time(
                    demand.fp32_ops,
                    resources.gpu_tflops_fp32,
                    _OPS_PER_TFLOP,
                    "gpu_tflops_fp32",
                    "fp32_ops",
                ),
            )
        )
    if demand.fp16_ops > 0.0:
        resource_times.append(
            (
                "gpu_tflops_fp16",
                _resource_time(
                    demand.fp16_ops,
                    resources.gpu_tflops_fp16,
                    _OPS_PER_TFLOP,
                    "gpu_tflops_fp16",
                    "fp16_ops",
                ),
            )
        )
    if demand.int8_ops > 0.0:
        resource_times.append(
            (
                "npu_tops_int8",
                _resource_time(
                    demand.int8_ops,
                    resources.npu_tops_int8,
                    _OPS_PER_TFLOP,
                    "npu_tops_int8",
                    "int8_ops",
                ),
            )
        )

    if not resource_times:
        return ComputeServiceTimeEstimate(
            service_time=0.0,
            bottleneck_resource=_NO_BOTTLENECK,
        )

    service_time = max(resource_time for _, resource_time in resource_times)
    bottleneck_resource = next(
        resource_name
        for resource_name, resource_time in resource_times
        if resource_time == service_time
    )
    return ComputeServiceTimeEstimate(
        service_time=service_time,
        bottleneck_resource=bottleneck_resource,
        resource_times=tuple(resource_times),
    )


def compute_resource_vector_from_node(node: ComputeNode) -> ComputeResourceVector:
    """Build the estimator resource vector represented by a compute node."""

    if not isinstance(node, ComputeNode):
        raise TypeError("node must be ComputeNode")
    return ComputeResourceVector(
        cpu_gflops_fp32=node.capacity,
        cpu_gflops_fp64=node.cpu_gflops_fp64,
        gpu_tflops_fp32=node.gpu_tflops_fp32,
        gpu_tflops_fp16=node.gpu_tflops_fp16,
        npu_tops_int8=node.npu_tops_int8,
        memory_gb=node.memory_gb,
        storage_gb=node.storage_gb,
    )


def task_resource_demand_from_request(task: TaskRequest) -> TaskResourceDemand:
    """Build the estimator demand represented by a task request.

    Current task requests carry the legacy scalar ``compute_demand`` contract.
    The estimator maps it to CPU operations so existing timing remains
    deterministic while all schedulers share the resource-vector path.
    """

    if not isinstance(task, TaskRequest):
        raise TypeError("task must be TaskRequest")
    return TaskResourceDemand.from_compute_demand(task.compute_demand)


def estimate_task_service_time(
    node: ComputeNode,
    task: TaskRequest,
) -> ComputeServiceTimeEstimate:
    """Estimate service time for a task on a concrete compute node."""

    return estimate_compute_service_time(
        compute_resource_vector_from_node(node),
        task_resource_demand_from_request(task),
    )


_RESOURCE_FIELD_NAMES = (
    "cpu_gflops_fp32",
    "cpu_gflops_fp64",
    "gpu_tflops_fp32",
    "gpu_tflops_fp16",
    "npu_tops_int8",
    "memory_gb",
    "storage_gb",
)
_DEMAND_FIELD_NAMES = (
    "cpu_ops",
    "fp32_ops",
    "fp16_ops",
    "int8_ops",
    "memory_gb",
    "input_data_mb",
    "output_data_mb",
)


def _set_non_negative_float(instance: object, field_name: str) -> None:
    value = getattr(instance, field_name)
    _require_non_negative_number(value, field_name)
    object.__setattr__(instance, field_name, float(value))


def _resource_time(
    demand_ops: float,
    rate: float,
    ops_per_rate_unit: float,
    resource_name: str,
    demand_name: str,
) -> float:
    if rate <= 0.0:
        raise ValueError(
            f"{resource_name} must be positive when {demand_name} is non-zero"
        )
    return demand_ops / (rate * ops_per_rate_unit)


def _cpu_rate(resources: ComputeResourceVector) -> tuple[str, float]:
    if resources.cpu_gflops_fp32 > 0.0:
        return "cpu_gflops_fp32", resources.cpu_gflops_fp32
    if resources.cpu_gflops_fp64 > 0.0:
        return "cpu_gflops_fp64", resources.cpu_gflops_fp64
    raise ValueError(
        "cpu_gflops_fp32 or cpu_gflops_fp64 must be positive "
        "when cpu_ops is non-zero"
    )


def _require_capacity_limits(
    resources: ComputeResourceVector,
    demand: TaskResourceDemand,
) -> None:
    if demand.memory_gb > resources.memory_gb:
        raise ValueError("memory_gb demand exceeds resource capacity")

    storage_demand_gb = (demand.input_data_mb + demand.output_data_mb) / _MB_PER_GB
    if storage_demand_gb > resources.storage_gb:
        raise ValueError("input/output data demand exceeds storage_gb capacity")


def _require_non_negative_number(value: Any, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field_name} must be an int or float")
    if not isfinite(value):
        raise ValueError(f"{field_name} must be finite")
    if value < 0:
        raise ValueError(f"{field_name} must be non-negative")


def _require_positive_number(value: Any, field_name: str) -> None:
    _require_non_negative_number(value, field_name)
    if value <= 0:
        raise ValueError(f"{field_name} must be positive")
