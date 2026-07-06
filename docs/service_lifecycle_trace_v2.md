# Service Lifecycle Trace v2

Date: 2026-07-06
Branch: `feature/T255-service-lifecycle-trace-v2`

## Goal

Define and expose a backend-owned communication-compute service lifecycle trace.
This is the V2-013 business-demand integration step after service request
contracts, arrival profiles, and service mix active state.

## Contract

Contract id:

`leo_twin.service_lifecycle_trace_contract.v2`

The trace is derived from `service_latency_history_v1`, which is already emitted
from deterministic `METRIC_SAMPLE` records produced by the route-aware compute
model. The runtime status now includes:

`service_lifecycle_trace_v2`

Runtime result exports also write a standalone deterministic artifact:

`service_lifecycle_trace_v2.json`

The export artifact has type `SERVICE_LIFECYCLE_TRACE_EXPORT_V2` and carries the
same backend-owned `service_lifecycle_trace_v2` summary that is present in the
stable export status snapshot. This keeps the trace available for offline
review without requiring consumers to parse `config_snapshot.json`.

## Lifecycle Stages

Each trace row exposes these ordered stages:

- `input_network`
- `compute_queue`
- `compute_execution`
- `output_network`

The terminal state is reported separately as one of:

- `RUNNING`
- `COMPLETE`
- `INCOMPLETE`

`COMPLETE` requires observed total latency. If output flow metadata exists but
no output network component has been observed yet, the trace reports
`RUNNING` with `OUTPUT_NETWORK_PENDING`.

## Trace Fields

Each trace includes:

- `trace_id`
- `service_id`
- `task_id`
- `service_class`
- `input_flow_id`
- `output_flow_id`
- `input_route_id`
- `output_route_id`
- `compute_node_id`
- placement policy/status/bottleneck fields
- component latency fields
- `terminal_state`
- `terminal_state_reason`
- ordered `stages`

The `service_id` is normalized from the generated service id base:

- `*-task` -> `*`
- `*-input` -> `*`
- `*-output` -> `*`

## Boundaries

This task does not modify Event Kernel behavior, network routing, compute
scheduling, packet-level semantics, retry behavior, deadline-aware preemption,
or external simulator integration. It is an observability and product contract
layer over existing deterministic runtime metrics.

Current `RouteAwareComputeEngine` scheduling is driven by `TASK_ARRIVAL` plus a
matching `ROUTE_UPDATE`. The trace does not claim that compute execution waits
for a separate `FLOW_COMPLETE` event in this implementation.

## Verification

Tests cover:

- deterministic schema contract serialization;
- deterministic lifecycle trace generation from service latency history;
- pending output-network state;
- completed communication-compute service trace from the integration lifecycle
  test.
