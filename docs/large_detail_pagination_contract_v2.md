# Large Detail Pagination Contract v2

Date: 2026-07-06
Branch: `feature/T237-large-detail-pagination-contract-v2`
Contract id: `leo_twin.large_detail_pagination_contract.v2`

## Purpose

Large detail pagination contract v2 defines how high-cardinality runtime
details are exposed to frontend and external users without rendering or
returning unbounded tables.

The contract covers:

- ground-user detail rows;
- satellite detail rows;
- route and bottleneck rows;
- communication-compute service lifecycle rows;
- communication-compute service trace rows;
- satellite-hosted compute-node resource rows.

This task adds a backend-owned contract and extends existing read-only detail
endpoints. It does not modify the Event Kernel, runtime advancement, orbit,
network, compute scheduling, business generation, or frontend layout.

## Source Policies

The contract is derived from:

- `leo_twin.scale_policy.v2`;
- `leo_twin.lod_snapshot_policy.v2`;
- configured satellite, user, compute-node, route, and service count estimates.

It is returned in:

`backend_summary.large_detail_pagination_contract_v2`

## Cursor Model

All detail endpoints use the same cursor model:

- `cursor`: zero-based offset;
- `limit`: positive integer, capped by backend maximum;
- `next_cursor`: `min(total_count, cursor + returned_item_count)`;
- `has_more`: `next_cursor < total_count`;
- maximum endpoint limit: `5000`.

The same snapshot, cursor, and limit must return the same rows.

## Collections

The contract records one collection entry for each large detail surface:

| Collection | Endpoint | Summary Type | Stable Key |
| --- | --- | --- | --- |
| `ground_users` | `/runtime/details/users` | `RuntimeUserRequestSummaryV1` | `user_id` |
| `satellites` | `/runtime/details/satellites` | `RuntimeSatelliteServiceSummaryV1` | `satellite_id` |
| `routes` | `/runtime/details/routes` | `RuntimeRouteExplanationSummaryV1` | `route_id` |
| `services` | `/runtime/details/services` | `RuntimeServiceDetailPageV1` | `task_id` |
| `service_traces` | `/runtime/details/service-traces` | `RuntimeServiceLifecycleTraceV2` | `trace_id` |
| `compute_nodes` | `/runtime/details/compute-nodes` | `RuntimeComputeNodeDetailPageV1` | `node_id` |

The existing combined node-card endpoint remains available:

`/runtime/details/nodes`

It composes user and satellite detail cards for the dashboard drawer.

## Runtime Endpoint Scope

New endpoints added in this task:

- `/runtime/details/routes`
- `/runtime/details/services`
- `/runtime/details/service-traces`
- `/runtime/details/compute-nodes`

`/runtime/details/service-traces` additionally accepts:

- `query`
- `terminal_state`
- `compute_node_id`

The endpoints are read-only observation surfaces. They reuse existing runtime
snapshot, route explanation, service latency history, and satellite KPI slice
data.

## Frontend Rules

Frontend consumers should:

- read collection metadata from
  `backend_summary.large_detail_pagination_contract_v2`;
- display raw counts from each page summary;
- use backend cursor windows for hidden rows;
- avoid rendering unbounded rows;
- not infer pagination semantics locally.

## Boundaries

This contract does not implement:

- packet-level simulation;
- new traffic demand logic;
- new network or compute model behavior;
- distributed execution;
- frontend virtual scrolling;
- Event Kernel changes.

## Follow-Up

- V2-053 should bind the standalone dashboard tables to these backend cursor
  contracts.
- Detail drawers can later request single-node full detail by entity id.
- Result export should include cursor contract metadata alongside exported
  summary files.
