# Dashboard Filter Scope Notice v1

Date: 2026-07-06
Branch: `feature/T242-dashboard-filter-scope-notice-v1`

## Purpose

This task made dashboard filtering scope explicit for large backend cursor
pages.

The dashboard has cursor controls for user, satellite, route, service, and
compute-node detail pages. At the time of this task, text and structured
filters still operated on the currently loaded backend page and local render
window. T243 later added filter-aware backend cursor requests for user,
satellite, and route detail pages.

## Behavior

- Adds a backend-derived filter scope note when cursor metadata is present.
- The note lists active backend page ranges for:
  - users;
  - satellites;
  - routes.
- The note is hidden for legacy summaries without cursor metadata.
- Existing local filtering, local pagination, and backend cursor reads remained
  unchanged in this task.

## Boundaries

- No Event Kernel changes.
- No backend endpoint changes.
- No filter-aware backend query implementation.
- No model behavior changes.
- No dashboard architecture rewrite.

## Follow-Up

- Filter-aware backend cursor requests for user, satellite, and route detail
  pages were added in T243.
- Persist filter context in backend detail endpoints.
- Add entity detail-by-id endpoints for direct selection from filtered results.
