"""Product-level compute resource contract v2."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


COMPUTE_RESOURCE_CONTRACT_V2_ID = "leo_twin.compute_resource_contract.v2"


class ComputeResourceLaneKind(StrEnum):
    """Canonical compute resource lanes exposed to product users."""

    CPU_FP32 = "CPU_FP32"
    CPU_FP64 = "CPU_FP64"
    GPU_FP32 = "GPU_FP32"
    GPU_FP16 = "GPU_FP16"
    NPU_INT8 = "NPU_INT8"
    MEMORY = "MEMORY"
    STORAGE = "STORAGE"


class TaskDemandLaneKind(StrEnum):
    """Canonical task demand lanes consumed by the service-time estimator."""

    CPU_OPS = "CPU_OPS"
    FP32_OPS = "FP32_OPS"
    FP16_OPS = "FP16_OPS"
    INT8_OPS = "INT8_OPS"
    MEMORY_GB = "MEMORY_GB"
    INPUT_DATA_MB = "INPUT_DATA_MB"
    OUTPUT_DATA_MB = "OUTPUT_DATA_MB"


@dataclass(frozen=True)
class ComputeResourceLaneContract:
    """One capacity lane inside the compute resource vector."""

    lane: ComputeResourceLaneKind
    capacity_field: str
    unit: str
    node_state_capacity_field: str
    node_state_used_field: str
    node_state_available_field: str
    throughput_lane: bool
    compatibility_role: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.lane, ComputeResourceLaneKind):
            object.__setattr__(self, "lane", ComputeResourceLaneKind(str(self.lane)))
        _require_non_empty_str(self.capacity_field, "capacity_field")
        _require_non_empty_str(self.unit, "unit")
        _require_non_empty_str(self.node_state_capacity_field, "node_state_capacity_field")
        _require_non_empty_str(self.node_state_used_field, "node_state_used_field")
        _require_non_empty_str(
            self.node_state_available_field,
            "node_state_available_field",
        )
        if not isinstance(self.throughput_lane, bool):
            raise TypeError("throughput_lane must be a bool")

    def to_dict(self) -> dict[str, object]:
        return {
            "lane": self.lane.value,
            "capacity_field": self.capacity_field,
            "unit": self.unit,
            "node_state_capacity_field": self.node_state_capacity_field,
            "node_state_used_field": self.node_state_used_field,
            "node_state_available_field": self.node_state_available_field,
            "throughput_lane": self.throughput_lane,
            "compatibility_role": self.compatibility_role,
        }


@dataclass(frozen=True)
class TaskDemandLaneContract:
    """One task demand lane consumed by the estimator."""

    lane: TaskDemandLaneKind
    demand_field: str
    required_resource_lane: ComputeResourceLaneKind
    unit: str
    estimator_role: str

    def __post_init__(self) -> None:
        if not isinstance(self.lane, TaskDemandLaneKind):
            object.__setattr__(self, "lane", TaskDemandLaneKind(str(self.lane)))
        if not isinstance(self.required_resource_lane, ComputeResourceLaneKind):
            object.__setattr__(
                self,
                "required_resource_lane",
                ComputeResourceLaneKind(str(self.required_resource_lane)),
            )
        _require_non_empty_str(self.demand_field, "demand_field")
        _require_non_empty_str(self.unit, "unit")
        _require_non_empty_str(self.estimator_role, "estimator_role")

    def to_dict(self) -> dict[str, object]:
        return {
            "lane": self.lane.value,
            "demand_field": self.demand_field,
            "required_resource_lane": self.required_resource_lane.value,
            "unit": self.unit,
            "estimator_role": self.estimator_role,
        }


@dataclass(frozen=True)
class ComputeServiceTimeEstimatorContract:
    """Product semantics of the deterministic compute service-time estimator."""

    estimator_id: str
    model: str
    formula_summary: str
    bottleneck_policy: str
    capacity_limit_policy: str
    legacy_mapping: str
    excluded_semantics: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_non_empty_str(self.estimator_id, "estimator_id")
        _require_non_empty_str(self.model, "model")
        _require_non_empty_str(self.formula_summary, "formula_summary")
        _require_non_empty_str(self.bottleneck_policy, "bottleneck_policy")
        _require_non_empty_str(self.capacity_limit_policy, "capacity_limit_policy")
        _require_non_empty_str(self.legacy_mapping, "legacy_mapping")
        object.__setattr__(
            self,
            "excluded_semantics",
            _normalize_str_tuple(self.excluded_semantics, "excluded_semantics"),
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "estimator_id": self.estimator_id,
            "model": self.model,
            "formula_summary": self.formula_summary,
            "bottleneck_policy": self.bottleneck_policy,
            "capacity_limit_policy": self.capacity_limit_policy,
            "legacy_mapping": self.legacy_mapping,
            "excluded_semantics": self.excluded_semantics,
        }


@dataclass(frozen=True)
class ComputeResourceContractV2:
    """Versioned product contract for satellite-hosted compute resources."""

    contract_id: str
    version: str
    resource_model: str
    node_role: str
    resource_lanes: tuple[ComputeResourceLaneContract, ...]
    task_demand_lanes: tuple[TaskDemandLaneContract, ...]
    service_time_estimator: ComputeServiceTimeEstimatorContract
    runtime_event_inputs: tuple[str, ...]
    runtime_state_outputs: tuple[str, ...]
    deterministic_inputs: tuple[str, ...]
    model_note: str

    def __post_init__(self) -> None:
        _require_non_empty_str(self.contract_id, "contract_id")
        _require_non_empty_str(self.version, "version")
        _require_non_empty_str(self.resource_model, "resource_model")
        _require_non_empty_str(self.node_role, "node_role")
        if not self.resource_lanes:
            raise ValueError("resource_lanes must not be empty")
        if not self.task_demand_lanes:
            raise ValueError("task_demand_lanes must not be empty")
        if not isinstance(self.service_time_estimator, ComputeServiceTimeEstimatorContract):
            raise TypeError("service_time_estimator must be ComputeServiceTimeEstimatorContract")
        object.__setattr__(
            self,
            "runtime_event_inputs",
            _normalize_str_tuple(self.runtime_event_inputs, "runtime_event_inputs"),
        )
        object.__setattr__(
            self,
            "runtime_state_outputs",
            _normalize_str_tuple(self.runtime_state_outputs, "runtime_state_outputs"),
        )
        object.__setattr__(
            self,
            "deterministic_inputs",
            _normalize_str_tuple(self.deterministic_inputs, "deterministic_inputs"),
        )
        _require_non_empty_str(self.model_note, "model_note")

    def to_dict(self) -> dict[str, object]:
        return {
            "contract_id": self.contract_id,
            "version": self.version,
            "resource_model": self.resource_model,
            "node_role": self.node_role,
            "resource_lanes": tuple(lane.to_dict() for lane in self.resource_lanes),
            "task_demand_lanes": tuple(
                lane.to_dict() for lane in self.task_demand_lanes
            ),
            "service_time_estimator": self.service_time_estimator.to_dict(),
            "runtime_event_inputs": self.runtime_event_inputs,
            "runtime_state_outputs": self.runtime_state_outputs,
            "deterministic_inputs": self.deterministic_inputs,
            "model_note": self.model_note,
        }


def default_compute_resource_contract_v2() -> ComputeResourceContractV2:
    """Build the default SEES compute resource contract v2."""

    return ComputeResourceContractV2(
        contract_id=COMPUTE_RESOURCE_CONTRACT_V2_ID,
        version="v2",
        resource_model="ComputeResourceVector",
        node_role="SATELLITE_HOSTED_COMPUTE",
        resource_lanes=_default_resource_lanes(),
        task_demand_lanes=_default_task_demand_lanes(),
        service_time_estimator=ComputeServiceTimeEstimatorContract(
            estimator_id="deterministic_bottleneck_resource_time.v1",
            model="MAX_ACTIVE_RESOURCE_LANE_TIME",
            formula_summary=(
                "Estimate each active processing lane time as operations divided "
                "by configured lane throughput; service_time is the maximum lane time."
            ),
            bottleneck_policy=(
                "The first lane reaching the maximum deterministic lane time is "
                "reported as bottleneck_resource."
            ),
            capacity_limit_policy=(
                "Memory and storage are capacity limits. They reject over-capacity "
                "tasks but do not add throughput time."
            ),
            legacy_mapping=(
                "ComputeNode.capacity maps to cpu_gflops_fp32; TaskRequest.compute_demand "
                "maps to cpu_ops with one legacy demand unit equal to one giga-operation."
            ),
            excluded_semantics=(
                "REAL_CODE_EXECUTION",
                "CUDA_RUNTIME",
                "NPU_RUNTIME",
                "MEMORY_BANDWIDTH_MODEL",
                "STORAGE_IO_MODEL",
                "THERMAL_POWER_MODEL",
                "PREEMPTIVE_SCHEDULING",
            ),
        ),
        runtime_event_inputs=("TASK_ARRIVAL", "TASK_START", "TASK_FINISH", "COMPUTE_NODE_UPDATE"),
        runtime_state_outputs=("ComputeNodeState", "TaskState", "MetricRecord"),
        deterministic_inputs=(
            "scenario.compute_capacity",
            "scenario.compute_cpu_gflops_fp64",
            "scenario.compute_gpu_tflops_fp32",
            "scenario.compute_gpu_tflops_fp16",
            "scenario.compute_npu_tops_int8",
            "scenario.compute_memory_gb",
            "scenario.compute_storage_gb",
            "TaskRequest.cpu_ops",
            "TaskRequest.fp32_ops",
            "TaskRequest.fp16_ops",
            "TaskRequest.int8_ops",
            "TaskRequest.memory_gb",
            "TaskRequest.input_data_mb",
            "TaskRequest.output_data_mb",
        ),
        model_note=(
            "SEES compute resources are deterministic satellite-hosted capacity "
            "vectors. They estimate queue/execution timing but do not execute code."
        ),
    )


def compute_resource_contract_v2_to_dict(
    contract: ComputeResourceContractV2 | None = None,
) -> dict[str, object]:
    """Return the default or supplied compute contract as JSON-compatible data."""

    selected = default_compute_resource_contract_v2() if contract is None else contract
    if not isinstance(selected, ComputeResourceContractV2):
        raise TypeError("contract must be ComputeResourceContractV2 or None")
    return selected.to_dict()


def _default_resource_lanes() -> tuple[ComputeResourceLaneContract, ...]:
    return (
        ComputeResourceLaneContract(
            lane=ComputeResourceLaneKind.CPU_FP32,
            capacity_field="compute_capacity",
            unit="GFLOPS FP32",
            node_state_capacity_field="capacity",
            node_state_used_field="used_cpu_gflops_fp32",
            node_state_available_field="available_cpu_gflops_fp32",
            throughput_lane=True,
            compatibility_role="legacy_scalar_capacity",
        ),
        ComputeResourceLaneContract(
            lane=ComputeResourceLaneKind.CPU_FP64,
            capacity_field="compute_cpu_gflops_fp64",
            unit="GFLOPS FP64",
            node_state_capacity_field="cpu_gflops_fp64",
            node_state_used_field="used_cpu_gflops_fp64",
            node_state_available_field="available_cpu_gflops_fp64",
            throughput_lane=True,
        ),
        ComputeResourceLaneContract(
            lane=ComputeResourceLaneKind.GPU_FP32,
            capacity_field="compute_gpu_tflops_fp32",
            unit="TFLOPS FP32",
            node_state_capacity_field="gpu_tflops_fp32",
            node_state_used_field="used_gpu_tflops_fp32",
            node_state_available_field="available_gpu_tflops_fp32",
            throughput_lane=True,
        ),
        ComputeResourceLaneContract(
            lane=ComputeResourceLaneKind.GPU_FP16,
            capacity_field="compute_gpu_tflops_fp16",
            unit="TFLOPS FP16",
            node_state_capacity_field="gpu_tflops_fp16",
            node_state_used_field="used_gpu_tflops_fp16",
            node_state_available_field="available_gpu_tflops_fp16",
            throughput_lane=True,
        ),
        ComputeResourceLaneContract(
            lane=ComputeResourceLaneKind.NPU_INT8,
            capacity_field="compute_npu_tops_int8",
            unit="TOPS INT8",
            node_state_capacity_field="npu_tops_int8",
            node_state_used_field="used_npu_tops_int8",
            node_state_available_field="available_npu_tops_int8",
            throughput_lane=True,
        ),
        ComputeResourceLaneContract(
            lane=ComputeResourceLaneKind.MEMORY,
            capacity_field="compute_memory_gb",
            unit="GB",
            node_state_capacity_field="memory_gb",
            node_state_used_field="used_memory_gb",
            node_state_available_field="available_memory_gb",
            throughput_lane=False,
            compatibility_role="capacity_limit_only",
        ),
        ComputeResourceLaneContract(
            lane=ComputeResourceLaneKind.STORAGE,
            capacity_field="compute_storage_gb",
            unit="GB",
            node_state_capacity_field="storage_gb",
            node_state_used_field="used_storage_gb",
            node_state_available_field="available_storage_gb",
            throughput_lane=False,
            compatibility_role="input_output_data_capacity_limit",
        ),
    )


def _default_task_demand_lanes() -> tuple[TaskDemandLaneContract, ...]:
    return (
        TaskDemandLaneContract(
            lane=TaskDemandLaneKind.CPU_OPS,
            demand_field="cpu_ops",
            required_resource_lane=ComputeResourceLaneKind.CPU_FP32,
            unit="operations",
            estimator_role="cpu lane time; fallback to CPU_FP64 when FP32 is absent",
        ),
        TaskDemandLaneContract(
            lane=TaskDemandLaneKind.FP32_OPS,
            demand_field="fp32_ops",
            required_resource_lane=ComputeResourceLaneKind.GPU_FP32,
            unit="operations",
            estimator_role="gpu fp32 lane time",
        ),
        TaskDemandLaneContract(
            lane=TaskDemandLaneKind.FP16_OPS,
            demand_field="fp16_ops",
            required_resource_lane=ComputeResourceLaneKind.GPU_FP16,
            unit="operations",
            estimator_role="gpu fp16 lane time",
        ),
        TaskDemandLaneContract(
            lane=TaskDemandLaneKind.INT8_OPS,
            demand_field="int8_ops",
            required_resource_lane=ComputeResourceLaneKind.NPU_INT8,
            unit="operations",
            estimator_role="npu int8 lane time",
        ),
        TaskDemandLaneContract(
            lane=TaskDemandLaneKind.MEMORY_GB,
            demand_field="memory_gb",
            required_resource_lane=ComputeResourceLaneKind.MEMORY,
            unit="GB",
            estimator_role="capacity limit",
        ),
        TaskDemandLaneContract(
            lane=TaskDemandLaneKind.INPUT_DATA_MB,
            demand_field="input_data_mb",
            required_resource_lane=ComputeResourceLaneKind.STORAGE,
            unit="MB",
            estimator_role="storage capacity limit with output_data_mb",
        ),
        TaskDemandLaneContract(
            lane=TaskDemandLaneKind.OUTPUT_DATA_MB,
            demand_field="output_data_mb",
            required_resource_lane=ComputeResourceLaneKind.STORAGE,
            unit="MB",
            estimator_role="storage capacity limit with input_data_mb",
        ),
    )


def _normalize_str_tuple(values: tuple[str, ...], field_name: str) -> tuple[str, ...]:
    if not isinstance(values, tuple):
        raise TypeError(f"{field_name} must be a tuple")
    normalized = tuple(str(value) for value in values)
    if any(not value for value in normalized):
        raise ValueError(f"{field_name} must not contain empty values")
    return normalized


def _require_non_empty_str(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value:
        raise TypeError(f"{field_name} must be a non-empty str")


__all__ = [
    "COMPUTE_RESOURCE_CONTRACT_V2_ID",
    "ComputeResourceContractV2",
    "ComputeResourceLaneContract",
    "ComputeResourceLaneKind",
    "ComputeServiceTimeEstimatorContract",
    "TaskDemandLaneContract",
    "TaskDemandLaneKind",
    "compute_resource_contract_v2_to_dict",
    "default_compute_resource_contract_v2",
]
