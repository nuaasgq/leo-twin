# Service and Compute Detail Filters v1

Date: 2026-07-06
Branch: `feature/T244-service-compute-detail-filters-v1`

## Purpose

This task extends filter-aware backend cursor reads to the remaining dashboard
detail pages:

- service lifecycle details;
- compute-node resource details.

T243 added filter-aware cursor requests for user, satellite, and route pages.
This task completes the first pass across all five visible dashboard detail
collections.

## Backend Contract

Supported optional query parameters:

- `/runtime/details/services`
  - `query`
- `/runtime/details/compute-nodes`
  - `query`

Filtering is applied before cursor pagination. Counts in the response describe
the filtered collection. When a filter is active, the summary also reports:

- `filter_applied`
- `filter_query`
- `unfiltered_service_count` or `unfiltered_compute_node_count`

## Frontend Behavior

- The service lifecycle table has a backend text filter.
- The compute-node resource table has a backend text filter.
- Refresh, previous-page, and next-page actions send the active query to the
  corresponding backend detail endpoint.
- The table still renders only the current backend page and local window.

## Boundaries

- No Event Kernel changes.
- No simulation model changes.
- No packet-level simulation.
- No frontend architecture rewrite.
- No new service or compute scheduling behavior.

## Follow-Up

- Add detail-by-id endpoints for selected services and compute nodes.
- Add filter metadata to a future large detail pagination contract version.
- Split large dashboard sections into smaller lazy chunks.
