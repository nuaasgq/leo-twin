# Service Request Contract v2

Date: 2026-07-06
Branch: `feature/T252-service-request-contract-v2`

## Goal

Define a product-level user business service request contract for SEES v2. This
contract sits above the existing runtime `FlowRequest`, `TaskRequest`, and
`TrafficDemandRecord` objects. It gives frontend, configuration, traffic, network,
compute, and result-export work a shared vocabulary for user demand.

## Contract Id

`leo_twin.service_request_contract.v2`

## Supported Service Classes

- `DATA_TRANSFER`
- `TELEMETRY`
- `BULK_DOWNLINK`
- `COMPUTE_SERVICE`
- `EMERGENCY`

These are the service classes currently represented by the deterministic
traffic demand model.

## Required Fields

The contract defines these product-facing fields:

- `service_id`
- `user_id`
- `service_class`
- `priority`
- `destination_policy`
- `destination_id`
- `input_data_mb`
- `output_data_mb`
- `duration_s`
- `deadline_s`
- `retry_policy`

`duration_s`, `deadline_s`, and `retry_policy` are explicitly marked as
reserved when current runtime behavior does not yet implement them. In the
current product, retry defaults to `NO_RETRY`.

## Runtime Mapping

The current runtime mapping is deterministic:

- `TrafficDemandProfile` expands into `TrafficDemandRecord`.
- `TrafficDemandRecord.input_flow` schedules `FLOW_ARRIVAL`.
- `TrafficDemandRecord.task` schedules `TASK_ARRIVAL` for `COMPUTE_SERVICE`.
- `TrafficDemandRecord.output_flow` stores deferred result-flow metadata.

Generated ids derive from the service id base:

- flow-only service: `service_id`
- compute input flow: `service_id-input`
- compute task: `service_id-task`
- compute output metadata: `service_id-output`

## Boundaries

This task does not change runtime behavior. It does not add packet-level
traffic, stochastic retry, deadline-aware scheduling, duration holding behavior,
application payload content, or external simulator integration.
