# User and Satellite Detail-by-ID v1

Date: 2026-07-06
Branch: `feature/T245-user-satellite-detail-by-id-v1`

## Goal

Selected dashboard user and satellite inspectors should use backend-owned
entity detail records instead of depending only on the currently loaded table
window.

## Backend Contract

The integration demo server keeps the existing cursor endpoints:

- `GET /runtime/details/users`
- `GET /runtime/details/satellites`

It also exposes single-entity detail endpoints:

- `GET /runtime/details/users/<user_id>`
- `GET /runtime/details/satellites/<satellite_id>`

Responses use the existing runtime node detail card shape:

```json
{
  "type": "RUNTIME_ENTITY_DETAIL",
  "kind": "user",
  "entity_id": "user-0001",
  "summary": {
    "entity_type": "USER",
    "entity_id": "user-0001",
    "title": "User user-0001",
    "subtitle": "ACTIVE",
    "fields": []
  }
}
```

The satellite endpoint uses `kind: "satellite"` and
`summary.entity_type: "SATELLITE"`.

## Frontend Behavior

The standalone dashboard still renders the current table window immediately.
When a user or satellite row is selected, the App requests the exact backend
detail card by id and passes it to the detail inspector. The explicit entity
card has priority over bounded window summaries and local fallback rows.

If the entity endpoint fails or returns no record, the dashboard falls back to
the existing row-based inspector path.

## Boundaries

- No Event Kernel changes.
- No simulation model behavior changes.
- No packet-level simulation.
- No dashboard layout rewrite.
- Existing cursor endpoints remain backward compatible.

