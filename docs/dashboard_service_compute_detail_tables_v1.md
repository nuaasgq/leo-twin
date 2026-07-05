# Dashboard Service and Compute Detail Tables v1

Date: 2026-07-06
Branch: `feature/T239-dashboard-service-compute-detail-tables-v1`

## Purpose

This task completes the frontend-facing part of the large detail pagination
contract for service lifecycle rows and compute-node resource rows.

Earlier work fetched and typed `/runtime/details/services` and
`/runtime/details/compute-nodes`, but the standalone dashboard did not expose
those cursor pages as dedicated tables. This task renders the backend-owned
cursor page data without changing model behavior.

## Data Sources

- Service lifecycle rows use `runtimeDetailPages.services`.
- Compute-node rows use `runtimeDetailPages.computeNodes`.
- Page sizes come from `leo_twin.large_detail_pagination_contract.v2` when the
  backend provides it.
- Compatible empty states remain available when the backend detail pages are
  not present.

## Dashboard Surfaces

- `ServiceDetailPageTable`
  - service/task id
  - service state
  - placement summary
  - input/output network latency
  - queue/execution compute latency
  - total service latency
- `ComputeNodeDetailPageTable`
  - node id and status
  - compute load ratio
  - FP32 usage
  - GPU FP32 and NPU INT8 usage
  - memory and storage usage
  - running/finished task counts

## Boundaries

- No Event Kernel changes.
- No runtime model behavior changes.
- No packet-level simulation.
- No dashboard architecture rewrite.
- No new network, orbit, or compute semantics.

## Follow-Up

- Add visible cursor navigation controls for service and compute-node pages.
- Add detail-by-id endpoints for selected service and selected compute node.
- Add column-level filtering once backend cursor navigation is available.
