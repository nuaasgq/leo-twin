# Dashboard User Detail Drawer v1

## Purpose

User detail drawer v1 turns the selected user row into a structured drill-down
surface. It is a frontend view model over backend runtime observability fields;
it does not introduce new simulation behavior.

The drawer prefers backend-owned `node_detail_summary_v1` cards when they are
available. When the backend card is absent, the dashboard falls back to
`user_request_summary_v1` rows and builds deterministic sections locally.

## Sections

Fallback user detail sections are:

1. `business_request`
   - user node id
   - platform type
   - active service label
   - request state
   - selected satellite
   - destination node
2. `network_path_queue`
   - communication route count
   - network queue label
   - route path label
   - latency and capacity label
3. `compute_service`
   - compute service count
   - service placement label

## Data Sources

- `runtimeStatus.user_request_summary_v1.items`
- `runtimeStatus.node_detail_summary_v1.users`
- existing selected-user table state in the standalone dashboard

## Model Boundary

- The drawer is observability only.
- It does not change Event Kernel behavior.
- It does not add packet-level queues.
- It does not infer RF, transport congestion, or high-fidelity routing beyond
  backend-provided labels.
- Queue and latency labels are flow-level proxy outputs from the current runtime
  summaries.

## Follow-Up

- V2-052 should add the equivalent satellite detail drawer v1.
- V2-053 should replace large tables with virtualization or backend paging.
- Future backend work should enrich `node_detail_summary_v1` so the fallback
  sections become less important over time.
