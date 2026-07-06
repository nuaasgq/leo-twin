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

The standalone dashboard consumes the same `service_lifecycle_trace_v2` status
field to render service rows and stage segments for input network, compute
queue, compute execution, and output network. The dashboard does not infer
lifecycle semantics locally; it only formats the backend-owned trace.

The export review area also loads package-owned
`service_lifecycle_trace_v2.json` when the backend export catalog declares the
artifact. It renders a read-only service chain review card with trace counts,
complete/running/incomplete totals, artifact link, and the same bounded trace
rows used by the live dashboard. This lets offline result packages review
input network, compute queue, compute execution, and output network evidence
without replaying the simulation.

The dashboard service trace panel also supports selecting one trace and
correlating it with currently visible user request rows, route explanations,
satellite resource rows, and compute-node detail rows. The correlation uses the
backend trace's flow ids, route ids, and compute node id; it does not create new
simulation state.

Runtime detail APIs now expose a backend exact-detail path for one trace:

`GET /runtime/details/service-traces/{trace_id}`

They also expose a cursor-readable trace page:

`GET /runtime/details/service-traces?cursor=0&limit=100&query=&terminal_state=ALL&compute_node_id=&stage_kind=ALL&terminal_reason=ALL`

The endpoint accepts the `trace:{service_id}` id, normalized `service_id`,
`task_id`, input flow id, or output flow id. It returns
`kind=service_trace`, the v2 trace, correlation ids, route explanation rows,
user detail cards, satellite detail cards, and compute-node detail when
available. The endpoint is read-only and derives all context from the current
runtime snapshot plus `service_latency_history_v1`.

The cursor-readable page returns `type=RUNTIME_DETAIL_PAGE`,
`kind=service_traces`, and a `RuntimeServiceLifecycleTraceV2` summary. It uses
the same deterministic ordering as the status trace and supports server-side
filters for text query, raw `terminal_state`, and `compute_node_id`.
It also supports backend-owned `stage_kind` and `terminal_reason` filters so
dashboard consumers can narrow lifecycle windows by component stage and terminal
reason without scanning hidden rows locally.

The standalone dashboard selection path now calls this exact-detail endpoint
for a selected service trace. When the backend detail matches the selected
trace row, the correlation inspector prefers the backend-owned user, route,
satellite, flow, and compute-node ids over the current visible table window.
The previous visible-window correlation remains as a fallback while the detail
request is loading or unavailable.

The dashboard detail drawer also renders the selected backend exact trace as a
service detail card. The card groups lifecycle latency components, correlation
ids, bounded route explanations, backend user cards, backend satellite cards,
and compute-node resource fields into scrollable sections. This keeps the
standalone dashboard aligned with backend semantics without adding a new
frontend-only business model.

The service trace browser supports filtering by trace keyword, backend
terminal state, and compute-node id. The dashboard now sends those controls to
`/runtime/details/service-traces` and uses the returned cursor window when it
is available, while retaining local filtering as a short-lived fallback during
loading or backend unavailability. The terminal-state filter uses the raw
backend `terminal_state` field on each trace row rather than parsing localized
display labels.

The backend cursor endpoint also accepts raw `stage_kind` values such as
`INPUT_NETWORK`, `COMPUTE_QUEUE`, `COMPUTE_EXECUTION`, and `OUTPUT_NETWORK`,
plus raw `terminal_reason` values such as `TOTAL_LATENCY_OBSERVED` and
`OUTPUT_NETWORK_PENDING`. These filters are applied before cursor slicing.
The standalone dashboard exposes the same filters in the service trace browser
and sends them to the backend cursor endpoint with cursor reset on every filter
change. Local filtering remains a loading/error fallback and uses the same
observable-stage rule for `stage_kind`.

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
