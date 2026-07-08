# Product Contracts v1

This document freezes the product-level data contracts shared by the backend
runtime, metrics pipeline, control plane, and frontend observation surface.

The contracts are data-only. They do not implement orbit propagation, routing,
channel calculation, compute scheduling, rendering, or event-kernel behavior.

## Canonical Runtime Contracts

The canonical runtime contracts live in `leo_twin.schema.domain`.

| Contract | Purpose | Producer | Consumer |
| --- | --- | --- | --- |
| `SatelliteState` | Orbit state for one satellite | Orbit | Network, Metrics, Frontend |
| `GroundUserState` | Ground user placement and status | Scenario/Network | Network, Metrics, Frontend |
| `ChannelState` | Channel observation for a link medium | Network channel layer | Link, Metrics, Frontend |
| `LinkState` | Flow-level logical link state | Network | Routing, Metrics, Frontend |
| `RouteState` | Deterministic route output for one flow | Routing | Compute, Metrics, Frontend |
| `FlowRequest` | Flow-level route request | Application/Scenario | Network |
| `FlowState` | Flow lifecycle state | Network/Compute | Compute, Metrics, Frontend |
| `TransportState` | Transport-layer lifecycle state | Transport | Metrics, Frontend |
| `ApplicationState` | Application-layer lifecycle state | Application | Metrics, Frontend |
| `ComputeNodeState` | Compute node capacity and status | Compute | Metrics, Frontend |
| `TaskRequest` | Compute task request | Scenario/Application | Compute |
| `TaskState` | Compute task lifecycle state | Compute | Metrics, Frontend |
| `MetricRecord` | Deterministic metric sample | Metrics | Reports, Frontend |
| `RuntimeConfigState` | Runtime mode, speed, seed, and duration | Control Plane | Runtime, Frontend |
| `WorldSnapshot` | Observation-plane snapshot shared with frontend | Snapshot/Runtime | Frontend |

## Business Service Request Contract

`leo_twin.service_request_contract.v2` defines the product-level user business
request above the existing runtime `FlowRequest`, `TaskRequest`, and
`TrafficDemandRecord` objects. It records service id, user id, service class,
priority, destination policy, input/output data size, duration, deadline, retry
policy, and generated flow/task ids.

The current runtime supports deterministic flow-level mapping for
`DATA_TRANSFER`, `TELEMETRY`, `BULK_DOWNLINK`, `COMPUTE_SERVICE`, and
`EMERGENCY`.
`duration_s`, `deadline_s`, and `retry_policy` are contract fields, but current
runtime behavior marks unsupported execution semantics as reserved rather than
silently pretending deadline scheduling or retries exist.

## Service Lifecycle Trace Contract

`leo_twin.service_lifecycle_trace_contract.v2` defines the product-level
communication-compute service trace derived from `service_latency_history_v1`.
It reports ordered `input_network`, `compute_queue`, `compute_execution`, and
`output_network` stages, plus backend-owned terminal state fields. The trace is
an observability contract over existing deterministic runtime metrics; it does
not introduce packet-level timelines, stochastic retries, deadline-aware
preemption, or external simulators.

## Compatibility Names

`RouteState` is the canonical route contract.

For backward compatibility, `Route` remains available as an alias:

- `leo_twin.schema.Route`
- `leo_twin.schema.network.Route`

The following network module names also remain compatible aliases to canonical
domain contracts:

- `leo_twin.schema.network.LinkState`
- `leo_twin.schema.network.FlowRequest`

`RouteState.demand_capacity` and `RouteState.loss_rate` are optional for
backward compatibility. Network runtimes should populate demand from the
originating `FlowRequest` when available so metrics and frontend surfaces can
explain flow-level demand pressure without observing `FLOW_ARRIVAL` directly.
Data-link and transport runtimes may populate `loss_rate` as a deterministic
flow-level proxy from configured MAC collision loss and transport loss. This is
not packet-level loss measurement.

`RouteState.pressure_edge_states` is an optional deterministic tuple of
serializable edge-pressure records emitted by the flow-level network pressure
model. It preserves per-edge admission, queue, utilization, and loss-proxy
evidence such as `edge_id`, `source_id`, `target_id`, `pressure_state`,
`projected_utilization`, `queue_delay_s`, `loss_proxy_rate`, and
`admission_rejected`. These records explain route-level pressure decisions for
metrics, exports, and offline review. They remain flow-level evidence and do
not represent packet-level simulation.

## Compute Resource Demand

`TaskRequest.compute_demand` remains the legacy scalar CPU FP32 demand used by
existing scenarios and tests. When no explicit resource-lane fields are set,
compute services map this value to CPU operations deterministically.

`TaskRequest` also carries optional explicit resource demand fields:

- `cpu_ops`
- `fp32_ops`
- `fp16_ops`
- `int8_ops`
- `memory_gb`
- `input_data_mb`
- `output_data_mb`

These fields are data contracts only. They do not imply packet-level
simulation, external simulators, or Event Kernel changes. Runtime compute
models may use them for deterministic service-time estimation and resource
capacity checks.

`ComputeNodeState` keeps the legacy scalar `capacity` /
`available_capacity` fields as the CPU FP32 compatibility view. It also carries
optional resource-vector capacity and estimated used/available fields for CPU
FP32/FP64, GPU FP32/FP16, NPU INT8, memory, and storage. The
`resource_usage_mode` field identifies whether those per-resource usage values
come from the deterministic resource estimator or from the scalar compatibility
path.

## Determinism Rules

Contracts must be immutable dataclasses and deterministic when serialized.

`WorldSnapshot` normalizes ordered collections by stable identifiers:

- satellites by `satellite_id`
- ground users by `user_id`
- channels by `channel_id`
- links by `link_id`
- routes by `route_id`
- flows by `flow_id`
- transport and application state by `(flow_id, protocol)`
- compute nodes by `node_id`
- tasks by `task_id`
- metrics by `(sim_time, metric_name, entity_id, tags)`

`MetricRecord.tags` are sorted by key and value.

## Frontend Snapshot Boundary

`WorldSnapshot` is the backend-side canonical equivalent of the frontend
observation surface. It intentionally contains already-computed states and
summary-ready records only. It must not call domain modules or perform
simulation logic.

Frontend rendering code may project the snapshot into UI-specific structures,
but the semantic source remains this contract.

## Scope Boundaries

Product Contracts v1 does not introduce:

- new orbit propagation logic
- new routing algorithms
- new channel or RF calculations
- packet-level simulation
- frontend rendering changes
- Event Kernel changes
- external simulator dependencies
