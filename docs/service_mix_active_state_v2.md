# Service Mix Active State v2

Date: 2026-07-06
Branch: `feature/T254-service-mix-active-state-v2`

## Goal

Extend the deterministic traffic demand model from individual service-class
generation to a backend-owned service mix summary with per-user active service
state. This is the V2-012 business-demand step and builds on:

- `leo_twin.service_request_contract.v2`
- `TrafficArrivalProfile` v2

## Supported Service Classes

The demand model and product contract now expose:

- `DATA_TRANSFER`
- `TELEMETRY`
- `BULK_DOWNLINK`
- `COMPUTE_SERVICE`
- `EMERGENCY`

`EMERGENCY` is a flow-level high-priority service class. It uses the existing
deterministic flow abstraction and does not introduce packet-level simulation,
stochastic retry, preemption, or deadline scheduling.

## Service Mix Configuration

`TrafficServiceMixItem` passes arrival and endpoint-selection profile fields
through to `TrafficDemandProfile`, including:

- `arrival_profile`
- `seed`
- `burst_size`
- `burst_spacing`
- `diurnal_period`
- `diurnal_peak_time`
- `diurnal_amplitude`
- `source_region_weights`
- `destination_region_weights`

The user configuration schema also exposes `emergency_weight` with default
`0.0`. Existing configurations remain compatible because `EMERGENCY` only
participates when selected explicitly or assigned a positive service-mix weight.

## Backend Summary

`TrafficDemandBatch.service_mix_summary()` returns deterministic aggregate and
per-user active state fields:

- `generated_request_count`
- `generated_request_counts`
- `active_service_classes`
- `per_user_active_service_state`

Each per-user row includes:

- `user_id`
- `request_count`
- `service_classes`
- `primary_service_class`
- `max_priority`
- `first_arrival_time`
- `last_arrival_time`
- `flow_ids`
- `task_ids`
- `output_flow_ids`
- `total_input_data_mb`
- `total_output_data_mb`

The primary service class is selected deterministically by highest priority,
then earliest arrival time, then service id.

## Runtime Boundaries

This task changes traffic-demand contracts, configuration propagation, backend
summary fields, and tests. It does not change Event Kernel behavior, network
routing, compute scheduling, metrics formulas, frontend rendering, or external
simulator integration.

## Verification

Unit and integration tests cover:

- explicit `EMERGENCY` service class support;
- deterministic service-mix request counts;
- per-user active service state grouping and primary-class selection;
- backend-derived service mix summary output;
- SEES config to scenario-builder propagation;
- integration demo frontend config compatibility.
