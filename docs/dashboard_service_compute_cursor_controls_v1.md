# Dashboard Service and Compute Cursor Controls v1

Date: 2026-07-06
Branch: `feature/T240-dashboard-service-compute-cursors-v1`

## Purpose

This task adds visible backend cursor navigation for the standalone dashboard
service lifecycle table and compute-node resource table.

T239 made the first backend cursor pages visible. This task lets operators move
through later service and compute-node pages without changing the backend
pagination contract.

## Behavior

- `App.tsx` keeps separate cursor state for:
  - service lifecycle details;
  - compute-node resource details.
- The periodic dashboard detail refresh uses the active cursors for these two
  pages instead of always returning to cursor zero.
- Each table shows:
  - current backend row range;
  - previous cursor action;
  - next cursor action;
  - explicit refresh action;
  - local loading/error text for that cursor page.
- Config version changes reset service and compute-node cursors to zero.

## Boundaries

- No Event Kernel changes.
- No backend endpoint changes.
- No model behavior changes.
- No dashboard architecture rewrite.
- Existing compatibility fallbacks remain in place when cursor pages are absent.

## Follow-Up

- Add backend cursor controls for user, satellite, and route pages.
- Add detail-by-id requests for selected service and selected compute node.
- Add column filters once backend cursor reads can preserve filter context.
