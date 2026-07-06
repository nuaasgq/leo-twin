# Dashboard Model Trust Evidence Workspace v1

Date: 2026-07-06

## Purpose

Dashboard model trust evidence workspace v1 gives the standalone dashboard a
single read-only evidence surface for model trust. It connects existing backend
runtime semantics instead of adding new simulation behavior.

The workspace answers five user-facing questions:

- Which configuration semantics and forbidden boundaries are declared?
- Which large-scale fidelity policy is active?
- Are network KPIs backed by backend provenance and source fields?
- Is there a reproducibility manifest or export diagnostics package?
- What runtime state proves the current run is live, completed, or failed?

## Data Sources

The workspace uses existing frontend view models and runtime payloads:

- `backend_summary.configuration_explanation_v2`
- `backend_summary.model_assumptions`
- `runtimeStatus.fidelity_summary`
- `runtimeStatus.network_kpi_credibility_v1`
- `runtimeStatus.network_kpi_provenance_v2`
- `runtimeStatus.route_provenance_trust_summary_v1`
- `runtimeStatus.reproducibility_manifest_v1`
- runtime export catalog, review summary, route detail index, and diagnostics
  bundle data
- `/runtime/status`

## Evidence Rows

Rows are emitted in a deterministic order:

1. configuration semantics
2. fidelity boundary
3. KPI credibility
4. KPI formula provenance
5. route explanation provenance
6. replay/export evidence

The replay/export evidence lane now uses the package-owned
`/runtime/export/packages/{package_id}/routes` cursor endpoint when a selected
result package provides route evidence. The dashboard treats it as
backend-owned route evidence: it displays indexed route counts, export-window
policy, cursor controls, backend-filtered route rows, availability/business/
bottleneck filters, and row actions that open the existing live route detail
endpoint when the referenced route is still available in the current runtime.
Each row can also link to the package-owned
`/runtime/export/packages/{package_id}/routes/{route_id}` JSON so replay review
does not depend on live runtime state. The frontend does not recompute routes
or download the full `route_detail_index_v1.json` by default.
7. runtime evidence

Each row has a tone:

- `match`: evidence is present and usable.
- `different`: evidence is present but degraded, partial, or warning-bearing.
- `pending`: evidence is not present yet.
- `error`: evidence indicates an invalid or failed state.

The overall workspace tone is derived deterministically from row tones:

1. any error -> `error`
2. any warning/degradation -> `different`
3. any pending evidence -> `pending`
4. otherwise -> `match`

## Model Boundary

- No Event Kernel behavior changes are introduced.
- No orbit, network, compute, traffic, or metrics formulas are changed.
- No packet-level simulation is introduced.
- No STK, EXATA, AFSIM, or DDS integration is introduced.
- The frontend does not invent model trust semantics; it summarizes existing
  backend fields and marks missing evidence explicitly.

## Follow-Up

- Add package-side route-detail pagination or route-id lookup when exported
  packages need to cover hidden route rows beyond the current export window.
- Link each model assumption to a concrete verification report instance.
- Promote result-review evidence into a wider workspace when exported package
  history becomes large.
