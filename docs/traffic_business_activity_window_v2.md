# Traffic Business Activity Window v2

Date: 2026-07-09
Branch: `feature/T422-traffic-business-window-v2`

## Goal

Expose a backend-owned, simulation-time-relative user business activity window
for the v2 executable demo. The dashboard should be able to show which user
nodes currently have active, recent, or pending business without inferring that
state from static frontend data.

## Backend Contract

`TrafficDemandBatch.runtime_business_activity_window(...)` returns
`leo_twin.traffic_business_activity_window.v1`.

The runtime integration demo exposes the same object in `/runtime/status` as:

- `traffic_business_activity_window_v1`

Important fields:

- `current_sim_time`
- `request_count`
- `user_count`
- `active_user_count`
- `recent_user_count`
- `pending_user_count`
- `window_user_count`
- `state_counts`
- `window_state_counts`
- `items`

Each item includes:

- `user_id`
- `platform_type`
- `business_state`
- `request_count`
- `active_request_count`
- `recent_request_count`
- `pending_request_count`
- `communication_request_count`
- `compute_request_count`
- `service_classes`
- `active_business_types`
- `current_or_next_business_type`
- `primary_request_id`
- `primary_flow_id`
- `primary_target_id`
- `selected_satellite_id`
- `next_arrival_time`
- `time_to_next_request_s`

## Model Boundary

This is a flow-level business schedule summary. It does not simulate packets,
retry logic, RF propagation, or external simulators. `ACTIVE_BUSINESS` is based
on deterministic request arrival records and an assumed service-duration window.
Actual network queue and compute execution state remain joined through runtime
observability summaries such as user request summaries, service latency history,
and lifecycle traces.

## Determinism

The same `TrafficDemandBatch`, `sim_time`, window parameters, and user limit
produce identical rows, counts, and ordering. Rows are ordered by business state,
arrival time, and deterministic entity id ordering.
