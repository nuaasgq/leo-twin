# Dashboard Core Detail Cursor Controls v1

Date: 2026-07-06
Branch: `feature/T241-dashboard-core-detail-cursors-v1`

## Purpose

This task completes the first dashboard cursor-control pass for the core
backend detail pages:

- users;
- satellites;
- routes;
- services;
- compute nodes.

T240 added visible cursor controls for service and compute-node pages. This task
extends the same mechanism to user, satellite, and route pages.

## Behavior

- `App.tsx` now keeps active cursor state for all five visible detail
  collections.
- The dashboard detail refresh loop uses active cursors for users, satellites,
  routes, services, and compute nodes.
- The standalone dashboard shows backend page controls for:
  - user node status;
  - satellite resource usage;
  - route explanations;
  - service lifecycle;
  - compute-node resources.
- Cursor controls are hidden when a legacy runtime status summary does not
  include cursor metadata.

## Boundaries

- No Event Kernel changes.
- No backend endpoint changes.
- No model behavior changes.
- No packet-level simulation.
- Existing local filtering and local window pagination remain compatible.

## Follow-Up

- Add filter-aware backend cursor requests.
- Add detail-by-id requests for selected user, satellite, route, service, and
  compute node.
- Split large dashboard sections into smaller lazy chunks.
