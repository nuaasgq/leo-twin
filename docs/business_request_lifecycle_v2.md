# Business Request Lifecycle v2

`business_request_lifecycle_v2` is a backend-owned runtime status summary for
per-business-request lifecycle evidence.

## Sources

- `traffic_request_timeline_v1`: configured flow-level request schedule.
- `service_latency_history_v1`: observed communication-compute service stages.

The backend joins requests by stable request id, task id, input flow id, and
output flow id. The frontend should display the returned fields directly
instead of deriving lifecycle semantics locally.

## Lifecycle States

- `PENDING`: request arrival time is after the current simulation time.
- `NETWORK_INPUT`: input network stage has been observed.
- `COMPUTE_QUEUE`: compute queue stage has been observed.
- `COMPUTE_EXECUTION`: compute execution stage has been observed.
- `NETWORK_OUTPUT`: output/result network stage has been observed.
- `COMPLETED`: service latency history marks the request complete.
- `COMMUNICATION_ONLY_OBSERVED`: non-compute request is visible in the request
  timeline without compute-service trace evidence.
- `NOT_OBSERVED`: request has arrived, but no matching runtime service trace was
  observed in `service_latency_history_v1`.

## Boundaries

- The model is flow-level and deterministic.
- Packet-level queues, packet captures, retransmissions, stochastic transport,
  RF propagation, antenna patterns, and external simulators are not modeled.
- Event Kernel ordering behavior is unchanged.

## Frontend Contract

Consumers should use:

- `summary_id`: `leo_twin.business_request_lifecycle.v2`
- `items[].lifecycle_state`
- `items[].current_stage`
- `items[].observed_stage_count`
- `items[].input_network_latency_s`
- `items[].compute_queue_delay_s`
- `items[].compute_execution_delay_s`
- `items[].output_network_latency_s`
- `items[].detail_hash`
- `summary_hash`

The field `frontend_inference_required` is always `false` for this summary.
