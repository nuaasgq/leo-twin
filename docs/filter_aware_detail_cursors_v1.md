# Filter-Aware Detail Cursors v1

Date: 2026-07-06
Branch: `feature/T243-filter-aware-detail-cursors-v1`

## Purpose

This task makes selected dashboard detail cursor endpoints filter-aware.

The previous dashboard showed backend cursor controls, but text and structured
filters were still local to the loaded page. This task lets the frontend send
the current filter state to backend cursor endpoints for user, satellite, and
route detail pages.

## Backend Contract

Supported optional query parameters:

- `/runtime/details/users`
  - `query`
- `/runtime/details/satellites`
  - `query`
- `/runtime/details/routes`
  - `query`
  - `availability`
  - `business_type`
  - `bottleneck_component`

Filtering is applied before cursor pagination. Counts in the response describe
the filtered collection. When a filter is active, the summary also reports:

- `filter_applied`
- `filter_query`
- `unfiltered_user_count`, `unfiltered_satellite_count`, or
  `unfiltered_route_count`
- route-specific filter metadata for route pages

## Frontend Behavior

- User and satellite cursor refresh/next/previous actions send the current
  detail text filter.
- Route cursor refresh/next/previous actions send the current route text,
  availability, business type, and bottleneck filters.
- The detail scope notice now states that refresh/turn-page actions send the
  active filters to the backend, while the table still renders only the current
  backend page and local window.

## Boundaries

- No Event Kernel changes.
- No simulation model changes.
- No packet-level simulation.
- No new frontend architecture.
- Service and compute-node filter UI remain follow-up work.

## Follow-Up

- Add service lifecycle and compute-node filter controls.
- Add detail-by-id endpoints for selected entities.
- Add backend filter metadata to the large detail pagination contract v3.
