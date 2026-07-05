# 5-Hour Module Upgrade Plan

Date: 2026-07-05
Branch: `feature/T164-dashboard-observability-v1`

This plan turns the current product feedback into a bounded five-hour upgrade
flow. The work preserves the frozen deterministic Event Kernel and keeps all
new behavior behind configuration contracts, event-driven model boundaries,
runtime summaries, and frontend observation surfaces.

## Constraints

- Do not modify Event Kernel ordering, time authority, or dispatch behavior.
- Do not introduce STK, EXATA, AFSIM, DDS, packet-level simulation, or
  distributed execution.
- Keep backend-generated summaries as the source of product semantics.
- Keep the frontend focused on key controls; detailed scenario settings belong
  in user-facing configuration files and backend summaries.
- Commit and push each completed task. Do not commit local runtime/generated
  config state.

## Five-Hour Execution Flow

### Hour 1 - Dashboard Observability Foundation

- Fix the standalone dashboard page so vertical scrolling is obvious and stable.
- Add full per-user node status rows: node id, platform type, communication
  activity, compute activity, queue estimate, selected or serving satellite,
  target node, route state, and latency/capacity summary.
- Enrich per-satellite rows with service objects, next-hop candidates, route
  pressure, compute usage, and active task counts.
- Keep the implementation frontend-only except for tests and documentation.

### Hour 2 - User-Facing Detailed Configuration Contract

- Add a product configuration document and example YAML for detailed users:
  constellation profile, runtime, traffic demand, network layer profiles,
  compute resource vector, fidelity policy, and UI key-control mapping.
- Keep the UI limited to key controls and show backend-derived assumptions.
- Add config loader validation tests for accepted detailed keys.

### Hour 3 - Traffic Demand Model v2 Planning and First Backend Contract

- Define user platform classes, service mixes, arrival schedules, input/output
  data sizes, priority classes, and destination policies.
- Add deterministic per-user demand summaries without packet-level simulation.
- Expose backend request-state summaries for the dashboard.

### Hour 4 - Flow-Level Network KPI Dynamics v1

- Replace static-looking KPI fallback behavior with deterministic flow-level
  time variation derived from route demand, link utilization, topology changes,
  and configured transport profile.
- Add backend source labels explaining that loss and jitter remain flow-level
  proxies, not packet measurements.
- Add acceptance fixtures that prove throughput, latency, loss proxy, and delay
  variation change over simulation time for the same seed.

### Hour 5 - Satellite/Compute Detail and UX Polish

- Add satellite resource service summaries: served users, ingress/egress route
  counts, next hop, compute queue, FP32/FP64/GPU/NPU/memory/storage usage.
- Add dashboard filters and sticky table headers for large scenarios.
- Add visual checks for dashboard scrolling and table completeness at 72, 120,
  and 1200 satellites.

## Parallel Agent Work Packages

- Agent B Orbit: constellation/profile summaries and selected-satellite context.
- Agent C Network: flow-level route pressure, next-hop, latency/loss/jitter
  proxy semantics.
- Agent D Compute: per-satellite resource and queue summaries.
- Agent E Metrics: dynamic KPI samples and backend provenance labels.
- Frontend Adapter: dashboard scroll, tables, filters, and source explanations.

## First Executed Task

Task T164 starts with Hour 1 because it is directly user-visible and bounded:
standalone dashboard scrolling plus richer per-user and per-satellite status
tables derived from existing snapshots/runtime summaries.
