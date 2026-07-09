# Compute Service Resource Evidence v1

`compute_service_resource_evidence_v1` is a backend-owned runtime status summary
for compute-service queue, execution, placement, and resource-pool evidence.

## Sources

- `service_latency_history_v1`
- `compute_resource_pool_summary_v1`

The summary joins service lifecycle traces with the current compute resource
pool summary. It does not change placement or scheduling behavior.

## Key Status Fields

- `queue_pressure_status`
  - `NO_SERVICE_EVIDENCE`
  - `QUEUE_PRESSURE_WITH_RESOURCE_SATURATION`
  - `QUEUE_PRESSURE_OBSERVED`
  - `EXECUTION_ONLY_OBSERVED`
  - `NO_COMPUTE_STAGE_EVIDENCE`
- `resource_pressure_status`
  - `RESOURCE_SATURATED`
  - `RESOURCE_BUSY`
  - `RESOURCE_ACTIVE`
  - `RESOURCE_IDLE`
  - `RESOURCE_NOT_CONFIGURED`

## Frontend Contract

Frontend consumers should use:

- `queued_service_count`
- `avg_compute_queue_delay_s`
- `avg_compute_execution_delay_s`
- `queue_to_execution_ratio`
- `bottleneck_resource_counts`
- `node_rows`
- `resource_dimensions`
- `items`
- `summary_hash`

`frontend_inference_required` is `false`; the frontend should not infer compute
queue/resource pressure locally when this backend field is present.

## Boundaries

- The model is deterministic and service-level.
- Resource values are estimates from `ComputeNodeState` metrics.
- Hardware telemetry, packet-level networking, stochastic scheduling, and
  external simulators are not modeled.
- Event Kernel behavior is unchanged.
