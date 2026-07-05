# Route, Service, and Compute Detail-by-ID v1

Date: 2026-07-06
Branch: `feature/T246-route-service-compute-detail-by-id-v1`

## Goal

Extend the dashboard detail protocol so route, service lifecycle, and
compute-node rows can be requested exactly by id, matching the user and
satellite detail-by-id contract.

This is a protocol and backend-observability task. It does not redesign the
dashboard layout or add new simulation behavior.

## Backend Endpoints

Existing cursor endpoints remain unchanged:

- `GET /runtime/details/routes`
- `GET /runtime/details/services`
- `GET /runtime/details/compute-nodes`

New exact detail endpoints:

- `GET /runtime/details/routes/<route_id>`
- `GET /runtime/details/services/<service_id>`
- `GET /runtime/details/compute-nodes/<node_id>`

All exact detail endpoints return:

```json
{
  "type": "RUNTIME_ENTITY_DETAIL",
  "kind": "route",
  "entity_id": "route-0",
  "summary": {}
}
```

The `kind` values are `route`, `service`, and `compute_node`. The `summary`
object is the same row shape already used by the corresponding cursor page.

## Frontend API

The frontend now provides:

- `loadRuntimeRouteDetail(routeId)`
- `loadRuntimeServiceDetail(serviceId)`
- `loadRuntimeComputeNodeDetail(nodeId)`

The shared `RuntimeEntityDetailEnvelopeV1` type now covers:

- user detail cards
- satellite detail cards
- route explanation rows
- service lifecycle rows
- compute-node resource rows

## Boundaries

- No Event Kernel changes.
- No model behavior changes.
- No packet-level simulation.
- No frontend layout rewrite.
- Existing cursor endpoints remain backward compatible.

## Follow-Up

The next dashboard task can bind these APIs to route, service, and compute-node
row selections so those tables get exact inspectors instead of relying only on
the current cursor window.

