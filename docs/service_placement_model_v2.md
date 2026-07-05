# Service Placement Model v2

## Scope

Service Placement Model v2 defines how a communication-compute service chooses
a satellite-hosted compute node after the input network transfer is ready.

This task is a contract and deterministic model step. It does not change the
Event Kernel, does not introduce packet-level simulation, and does not execute
real compute workloads.

## Contract

The backend exposes `service_placement_contract_v2` in the backend-derived
summary. The contract id is:

`leo_twin.service_placement_contract.v2`

The default policy is:

`MIN_ESTIMATED_FINISH_TIME`

Candidate ordering is deterministic:

1. `finish_time`
2. `start_time`
3. `node_id`

## Inputs

The placement model consumes:

- `TaskRequest` resource demand fields.
- `ComputeNode` resource vector fields.
- Explicit `ServicePlacementQueueState.available_at`.
- Explicit `ServicePlacementQueueState.queued_task_count`.
- Optional `max_queue_depth`.

The service-time estimate is delegated to the existing compute resource
estimator. CPU, GPU, NPU, memory, and storage semantics therefore remain aligned
with `ComputeResourceVector`.

## Outputs

`place_compute_service()` returns a `ServicePlacementDecision` with:

- `status`: `PLACED`, `QUEUED`, or `REJECTED`.
- `selected_node_id`.
- `ready_time`, `start_time`, and `finish_time`.
- `queue_delay` and `execution_delay`.
- `bottleneck_resource`.
- `rejection_reason` when rejected.
- Per-candidate deterministic evaluation summaries.

## Rejection Reasons

- `NO_NODES`
- `NO_CAPABLE_NODE`
- `CAPACITY_LIMIT_EXCEEDED`
- `QUEUE_LIMIT_EXCEEDED`

## Determinism

Given the same task, nodes, queue states, policy, and queue depth, the selected
node and timing outputs are identical. Candidate nodes are normalized by
`node_id` before evaluation, so caller iteration order does not affect results.

## Current Limits

- The model is flow-level and deterministic only.
- It does not model packet queues, retransmission, RF propagation, thermal
  limits, power limits, preemption, service migration, or real code execution.
- Runtime integration remains incremental. `RouteAwareComputeEngine` can reuse
  this model in a later task to replace its local `_select_node()` logic.
