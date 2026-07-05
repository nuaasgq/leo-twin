# Dashboard Cursor Contract Binding v1

Date: 2026-07-06
Branch: `feature/T238-dashboard-cursor-contract-binding-v1`

## Purpose

Dashboard cursor contract binding v1 connects the standalone data dashboard to
the backend-owned `leo_twin.large_detail_pagination_contract.v2`.

The dashboard already had bounded user and satellite tables. This task changes
their budget source from frontend constants to backend contract metadata where
available.

## Bound Detail Surfaces

The frontend now reads:

- collection endpoints;
- recommended cursor limits;
- combined node detail endpoint;
- cursor max limit;
- hidden-row estimates;
- active scale profile.

The App runtime detail refresh path uses the contract to request:

- `/runtime/details/users`
- `/runtime/details/satellites`
- `/runtime/details/nodes`
- `/runtime/details/routes`
- `/runtime/details/services`
- `/runtime/details/compute-nodes`

The DataPanel uses contract-derived window sizes for user and satellite detail
tables and prefers route cursor pages over bounded runtime-status route
summaries when available.

## User-Facing Explanation

The detail observability notes now include:

- backend pagination contract source;
- active profile and cursor model;
- per-collection recommended limits;
- endpoint names;
- hidden-row estimates;
- table render budget source.

## Compatibility

If `large_detail_pagination_contract_v2` is not available, the frontend keeps
the existing compatible behavior:

- user table fallback page size: 80;
- satellite table fallback page size: 120;
- legacy full-window detail requests.

## Boundaries

This task does not implement:

- continuous virtual scrolling;
- new backend model behavior;
- packet-level simulation;
- Event Kernel changes;
- full DataPanel layout redesign.

## Follow-Up

- Add UI controls for cursor navigation beyond the first backend page.
- Bind service and compute-node detail pages to dedicated dashboard tables.
- Add single-entity detail-by-id requests for user and satellite drawers.
