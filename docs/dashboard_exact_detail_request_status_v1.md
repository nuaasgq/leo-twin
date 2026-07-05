# Dashboard Exact Detail Request Status v1

Date: 2026-07-06
Branch: `feature/T248-exact-detail-request-status-v1`

## Goal

Make backend exact-detail requests visible in the standalone dashboard. Users
should be able to tell whether a selected user, satellite, route, service, or
compute-node detail card is still loading, synchronized with the backend, or
showing a backend request error.

## Behavior

The App now tracks exact-detail request state separately from the returned
detail payload for:

- users
- satellites
- routes
- services
- compute nodes

When a row is selected, the matching request state enters loading mode. On
success, the corresponding detail card shows that backend exact detail is
synchronized. On failure, the detail card shows the backend error while keeping
the current cursor-window fallback semantics available through the existing
inspector builders.

Request status is scoped to the selected entity id. A stale request for a
previously selected entity is ignored by the visible inspector.

## Boundaries

- No Event Kernel changes.
- No backend runtime or model behavior changes.
- No dashboard layout rewrite.
- No new frontend-owned business semantics.
- Existing exact-detail and cursor endpoints remain unchanged.

## Verification

- Unit coverage checks request-state selection and inspector status insertion.
- Frontend build validates the TypeScript contract between App and DataPanel.
