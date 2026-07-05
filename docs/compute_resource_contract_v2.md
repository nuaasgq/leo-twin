# Compute Resource Contract v2

Date: 2026-07-05
Contract id: `leo_twin.compute_resource_contract.v2`

## Purpose

Compute Resource Contract v2 defines how SEES describes satellite-hosted compute
capacity and task resource demand. It is the backend-owned explanation surface
for resource pools, per-satellite resource lanes, task demand lanes, and
deterministic service-time estimation.

This task stabilizes semantics. It does not change Event Kernel behavior,
compute scheduling behavior, or the existing service-time formulas.

## Resource Model

The product resource model is `ComputeResourceVector`.

Each compute satellite has these capacity lanes:

- CPU FP32: `compute_capacity`
- CPU FP64: `compute_cpu_gflops_fp64`
- GPU FP32: `compute_gpu_tflops_fp32`
- GPU FP16: `compute_gpu_tflops_fp16`
- NPU INT8: `compute_npu_tops_int8`
- memory: `compute_memory_gb`
- storage: `compute_storage_gb`

The legacy scalar `compute_capacity` remains compatible and maps to CPU FP32
GFLOPS.

## Task Demand Model

Tasks may express demand through:

- `cpu_ops`
- `fp32_ops`
- `fp16_ops`
- `int8_ops`
- `memory_gb`
- `input_data_mb`
- `output_data_mb`

If explicit operation counts are absent, legacy `compute_demand` maps to
`cpu_ops`, with one legacy demand unit equal to one giga-operation.

## Service-Time Estimator

The deterministic estimator uses:

```text
service_time = max(active_resource_lane_time)
```

Processing lanes contribute time:

- CPU operations use CPU FP32 capacity, falling back to CPU FP64 when CPU FP32 is
  absent;
- FP32 operations use GPU FP32 capacity;
- FP16 operations use GPU FP16 capacity;
- INT8 operations use NPU INT8 capacity.

Memory and storage are capacity limits. They can reject over-capacity tasks but
do not add throughput time.

## Excluded Semantics

The contract explicitly does not model:

- real code execution;
- CUDA or NPU runtime behavior;
- memory bandwidth;
- storage I/O bandwidth;
- thermal or power limits;
- preemptive scheduling.

## Backend Summary

Generated scenario summaries expose:

```text
backend_summary.compute_resource_contract_v2
```

The object also includes `configured_node_profile`, so frontend and result
exports can display the actual per-node resource profile selected by the user.

## Follow-Up

V2-031 should add deterministic service placement semantics. V2-032 should
formalize task queue and execution timelines using this contract as the source
of truth.
