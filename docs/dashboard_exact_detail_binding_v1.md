# Dashboard Exact Detail Binding v1

Date: 2026-07-06
Branch: `feature/T247-route-service-compute-exact-inspector-v1`

## Goal

Bind the exact detail APIs for routes, service lifecycle rows, and compute-node
rows into the standalone dashboard. This completes the first exact-detail pass
across all visible runtime detail tables.

## Behavior

The dashboard now keeps selected row state for:

- route explanation rows
- service lifecycle rows
- compute-node resource rows

When a row is selected, the App requests the matching backend exact-detail
endpoint:

- `GET /runtime/details/routes/<route_id>`
- `GET /runtime/details/services/<service_id>`
- `GET /runtime/details/compute-nodes/<node_id>`

The returned backend row is preferred by the inspector. If the request fails or
has not completed yet, the dashboard still shows an immediate fallback based on
the current cursor-window row.

## UI Scope

The task does not redesign the dashboard layout. It adds selectable rows and
small exact-detail cards:

- route exact detail in the network section
- service exact detail in the compute/service section
- compute-node exact detail in the compute/service section

## Boundaries

- No Event Kernel changes.
- No backend simulation model changes.
- No packet-level simulation.
- No new dashboard data semantics inferred in the frontend.
- Exact detail cards use backend fields first and local row labels only as a
  temporary fallback.

