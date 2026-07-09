# Runtime Dashboard KPI v1

Date: 2026-07-09
Branch: `feature/T439-runtime-dashboard-kpi-v1`

## Goal

Expose one backend-owned KPI object for frontend dashboard panels so they do not
need to infer current throughput, latency, loss proxy, delay-variation proxy, or
compute resource usage from snapshots.

`runtime_dashboard_kpi_v1` standardizes:

- current KPI value;
- tail sample value from `kpi_time_series_v1`;
- supporting `metrics_summary` value;
- observation time and metrics time source;
- movement or dynamic status;
- zero-value explanation;
- source detail for throughput, loss proxy, and delay variation proxy.

## Runtime Status Field

The integration demo runtime status exposes:

- `runtime_dashboard_kpi_v1`

The object id is:

- `leo_twin.runtime_dashboard_kpi.v1`

## KPI Rows

The v1 row set matches the backend KPI movement contract:

1. `NETWORK_EFFECTIVE_THROUGHPUT`
2. `NETWORK_EFFECTIVE_LATENCY`
3. `NETWORK_EFFECTIVE_LOSS_PROXY`
4. `NETWORK_EFFECTIVE_DELAY_VARIATION_PROXY`
5. `COMPUTE_CPU_FP32_USED`
6. `COMPUTE_CPU_FP64_USED`
7. `COMPUTE_GPU_FP32_USED`
8. `COMPUTE_GPU_FP16_USED`
9. `COMPUTE_NPU_INT8_USED`
10. `COMPUTE_MEMORY_USED`
11. `COMPUTE_STORAGE_USED`

Each row includes:

- `metric`
- `category`
- `display_name`
- `unit`
- `sample_key`
- `runtime_summary_key`
- `current_value`
- `tail_sample_value`
- `runtime_summary_value`
- `value_source`
- `movement_status`
- `variation_status`
- `visibility`
- `zero_value_note`
- `source_detail`

## Boundary

This contract reads already-generated backend runtime evidence. It does not
change metrics formulas, synthesize movement, replay events, inspect frontend
snapshots, add packet-level simulation, or introduce external simulators.

The current-value priority is:

1. `kpi_time_series_v1` tail sample
2. `metrics_summary` fallback
3. missing value

The summary explicitly preserves:

- no packet-level simulation;
- no frontend semantic inference;
- no STK, EXATA, AFSIM, or DDS;
- no Event Kernel domain behavior changes.

## Intended Use

Frontend dashboard panels should prefer this object for current runtime KPI
cards and charts. Snapshot-derived network and compute summaries may still be
shown as topology/context evidence, but they should not be treated as the source
of truth for runtime KPI semantics when this field is present.
