# Dashboard Satellite Detail Drawer v1

## Purpose

Satellite detail drawer v1 turns the selected satellite resource row into a
structured drill-down surface for service, routing, compute resources, tasks,
and network context. It is a frontend view model over existing backend runtime
observability fields; it does not add new simulation behavior.

The drawer prefers backend-owned `node_detail_summary_v1` satellite cards when
they are available. When the backend card is absent, the dashboard falls back
to `satellite_service_summary_v1`, `satellite_kpi_slices_v1`, and snapshot
resource rows that are already used by the satellite resource table.

## Sections

Fallback satellite detail sections are:

1. `service_routing`
   - satellite node id
   - runtime/resource role status
   - served users or service objects
   - next-hop nodes
2. `compute_resource_pool`
   - load ratio
   - CPU FP32 and FP64 usage
   - GPU FP32 and FP16 usage
   - NPU INT8 usage
   - memory and storage usage
3. `network_task_context`
   - running and completed task summary
   - link, route, queue, latency, demand, capacity, and loss proxy label when
     provided by backend summaries

## Data Sources

- `runtimeStatus.satellite_service_summary_v1.items`
- `runtimeStatus.satellite_kpi_slices_v1.slices`
- `runtimeStatus.node_detail_summary_v1.satellites`
- current `WorldSnapshot` satellite, compute node, route, and link states

## Model Boundary

- The drawer is observability only.
- It does not change Event Kernel behavior.
- It does not compute all satellite pairs.
- It does not add packet-level queues or RF/link-budget simulation.
- Network labels remain current flow-level proxy outputs from runtime
  summaries.

## Follow-Up

- V2-053 should add virtualization or backend paging for large detail tables.
- V2-054 should add a clearer model assumptions panel beside node details.
- Future backend work should enrich `node_detail_summary_v1` with selected
  satellite coverage, beam, and per-resource timeline sections.
