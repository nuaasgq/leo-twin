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
bottleneck filters, and row actions for both package-owned route detail review
and existing live route detail comparison. A `compare with live` action can
load both detail channels for the selected route in one click. Package detail
actions read
`/runtime/export/packages/{package_id}/routes/{route_id}` and render the
exported row summary in the dashboard, so replay review does not depend on
live runtime state. The live action remains a current-runtime comparison when
the referenced route is still available. When both package and live details are
loaded for the same route id, the dashboard shows a field-level
package-vs-live comparison for availability, path, next hop, KPI proxy, and
bottleneck context. If the comparison cannot be shown yet, a status card
identifies whether package detail, live detail, or route-id alignment is the
blocking condition. Result packages now also expose backend-owned
`route_comparison_review` metadata in review summary, diagnostics, and route
detail artifacts so this workflow is auditable outside the frontend. The
metadata names the `RUNTIME_EXPORT_ROUTE_COMPARISON_REVIEW_REPORT_V1` report
template and its record schema, so selected package-vs-live comparison outcomes
can be captured with deterministic ordering. The API layer can POST selected
review records to the package-level route comparison review report endpoint,
which writes `route_comparison_review_report_v1.json` and updates the export
catalog. The dashboard route comparison card exposes a save action for the
currently displayed package-vs-live comparison and records the compared fields,
different fields, package detail hash, live detail hash, and status reason.
The live route detail endpoint exposes a backend-generated `detail_hash`, so
saved review reports can bind both sides of the comparison. After a save, the
dashboard export package view surfaces the catalog-owned
`route_comparison_review_report_v1.json` artifact link, file hash, and latest
report hash so the operator can verify that the review record is persisted.
When the artifact exists, the dashboard also loads the saved report JSON as a
read-only artifact and renders record counts, match/different/unavailable/error
totals, route detail hash pairs, and operator notes. The report drawer supports
local status filtering, text search across route id/status/hash/note fields, and
offset pagination over the saved records. The frontend does not recompute routes
or download the full `route_detail_index_v1.json` by default. Saved reports also
record the backend restore-preflight `runtime_export_boundary_alignment_v1`
evidence, including alignment hash, alignment status, warnings, and the runtime
export boundary hash. This binds the operator's route comparison outcome to the
same config-only restore, config/generated-config compare, persisted-artifact
read, and no-replay/no-recompute/no-packet boundary used by package
compare/preflight review. The package review area also surfaces
`export_package_audit_index_v1.json` from the export catalog. That audit index
binds manifest, boundary alignment, diagnostics, route review report, and
user configuration export evidence into one backend-owned long-term review
entry without route recomputation. Newer packages also include
`scenario_review_bundle_v1.json` as the backend-generated operator entry point;
the audit index records that file hash alongside the other package evidence.
The dashboard loads the scenario review bundle as a guided entry card and loads
the audit index JSON to render the evidence groups directly, including
schema/config/export/binding hashes and validation status for the user
configuration. The scenario review card also renders ordered artifact workflow
rows for configuration, manifest, diagnostics, audit, route, service trace,
event, metric, and summary review. T313 adds
`scenario_review_checklist_v1.json` as the backend-persisted operator decision
record for those rows. The dashboard now exposes editable reviewed/skipped/
follow-up/error controls and operator notes for each guided review row, posts
them to the backend checklist endpoint, and refreshes the audit index so
checklist presence, hash, status, and record count stay backend-owned evidence.
The package review completion banner now prefers the backend-owned
`package_review_completion_v1` object embedded in the audit index, falling back
to local aggregation only for older packages. That object aggregates checklist
state with audit readiness, saved route comparison report presence, and
scenario-review bundle readiness, so operators can see the handoff state before
drilling into raw JSON. This lets operators inspect and record the package
audit boundary without opening raw JSON first. Tools that only need that
handoff summary can call
`GET /runtime/export/packages/{package_id}/review-completion`, which reads the
same backend-owned audit evidence without replaying or recomputing the package.
Operators who need a human-readable handoff file can use
`GET /runtime/export/packages/{package_id}/handoff-report` to download
`package_handoff_report_v1.md`, a deterministic Markdown report generated from
that same completion evidence. The dashboard package-review area now surfaces
the same Markdown link from the backend export catalog alongside the completion
banner, so handoff review does not require manually constructing the URL.
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
