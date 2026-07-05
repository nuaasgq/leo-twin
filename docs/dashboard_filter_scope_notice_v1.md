# Dashboard Filter Scope Notice v1

Date: 2026-07-06
Branch: `feature/T242-dashboard-filter-scope-notice-v1`

## Purpose

This task makes dashboard filtering scope explicit for large backend cursor
pages.

The dashboard now has cursor controls for user, satellite, route, service, and
compute-node detail pages. However, text and structured filters still operate
on the currently loaded backend page and local render window. This task exposes
that limitation directly in the existing detail scope notes.

## Behavior

- Adds a backend-derived filter scope note when cursor metadata is present.
- The note lists active backend page ranges for:
  - users;
  - satellites;
  - routes.
- The note is hidden for legacy summaries without cursor metadata.
- Existing local filtering, local pagination, and backend cursor reads remain
  unchanged.

## Boundaries

- No Event Kernel changes.
- No backend endpoint changes.
- No filter-aware backend query implementation.
- No model behavior changes.
- No dashboard architecture rewrite.

## Follow-Up

- Add filter-aware backend cursor requests.
- Persist filter context in backend detail endpoints.
- Add entity detail-by-id endpoints for direct selection from filtered results.
