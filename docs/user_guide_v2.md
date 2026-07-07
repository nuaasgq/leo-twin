# LEO-Twin / SEES User Guide v2

Date: 2026-07-07

This guide is the user-facing entry point for the current SEES v2 product
prototype. It is written for operators who need to start the system, configure
a scenario, inspect the dashboard, export results, and collect diagnostics.

## 1. Start The System

From the repository root, use the Windows launcher:

```powershell
.\leo_twin_launcher.bat
```

Direct shortcuts:

```powershell
.\start_leo_twin.bat
.\dashboard_leo_twin.bat
.\restart_leo_twin.bat
.\stop_leo_twin.bat
.\status_leo_twin.bat
```

Default surfaces:

- console: `http://127.0.0.1:5173`
- dashboard: `http://127.0.0.1:5173/dashboard`
- backend status: `http://127.0.0.1:8765/runtime/status`
- backend version: `http://127.0.0.1:8765/runtime/version`

## 2. Check Health

Human-readable status:

```powershell
.\status_leo_twin.bat
.\scripts\sees_launcher.ps1 status
```

Machine-readable launcher health:

```powershell
.\scripts\sees_launcher.ps1 status -JsonSummary
.\scripts\sees_launcher.ps1 health -JsonSummary
```

Read-only runtime smoke:

```powershell
.\smoke_leo_twin.bat
.\scripts\smoke_runtime_health.ps1 -JsonSummary
```

Control-path smoke, which mutates and resets the active session:

```powershell
.\control_smoke_leo_twin.bat
.\scripts\smoke_runtime_control_cycle.ps1 -JsonSummary
```

Browser acceptance smoke, which clicks the real console buttons, verifies the
dashboard surface, fails on browser page errors, and resets the active session:

```powershell
.\browser_smoke_leo_twin.bat
.\scripts\smoke_browser_acceptance.ps1 -JsonSummary
```

The browser smoke uses a 90-second default wait window because initialization
rebuilds the backend session and dashboard detail endpoints can briefly return
transient errors during that rebuild. Browser button commands are sent through
the same backend control protocol via `POST /control`; the `/control`
WebSocket remains available for the backend control-cycle smoke.

## 3. Configure A Scenario

The frontend shows key controls only. The full detailed configuration remains
file/API driven.

Main user configuration endpoints:

- `GET /scenario/user-config/schema`
- `GET /scenario/user-config/templates`
- `GET /scenario/user-config/template-validation`
- `GET /scenario/user-config/reference`
- `GET /scenario/user-config/export`
- `POST /scenario/user-config/validate`
- `POST /scenario/user-config/validate-text`

Use `/scenario/user-config/reference` when you need the full backend-owned
configuration reference: it lists key UI fields, detailed file-only fields,
template profiles, validation/apply workflow, and model boundaries in one
stable object. The control panel should still show only key operational fields.
The standalone dashboard's configuration contract card links to this reference
and shows its stable hash/file-only field count next to the schema, templates,
and current export links. It also includes a scrollable reference browser for
all backend-declared sections and fields, including the edit surface, current
value, default value, and validation rules for each field.

Use `/scenario/user-config/template-validation` when you need a read-only
operator check that the shipped YAML templates are executable through the same
backend config loader and schema validation path used by runtime control. The
template catalog and reference endpoints also carry this evidence with template
counts, valid/invalid counts, file hashes, config hashes, scale summaries, and
the no-Event-Kernel/no-packet/no-external-simulator boundary.
The standalone dashboard configuration contract section renders the compact
template validation counts and an expandable template validation table so users
can inspect each approved YAML template, its validation status, scale/runtime
summary, orbit/space-link mode, file hash, config hash, and error summary
without applying the template.

Minimal YAML example:

```yaml
scenario:
  satellite_count: 72
  compute_nodes: 72
runtime:
  duration: 600
  seed: 20260703
```

Validation is explicit. A valid preflight response provides a normalized config
and an apply command. Applying a config reinitializes the active runtime session.

Runtime/local generated config files are not source files:

- `configs\sees_control.yaml`
- `configs\generated_full_system_demo.json`

Do not commit them unless a task explicitly says they are part of the change.

## 4. Use The Console And Dashboard

The console is for simulation control and 3D inspection:

- initialize, start, pause, resume, stop, reset;
- configure key scenario controls;
- inspect the 3D Earth, satellites, links, users, and selected-satellite views;
- see scale/fidelity notices from backend runtime status.

The standalone dashboard is for data situation awareness:

- network KPI trend, provenance, benchmark validation, backend calibration
  evidence for whether KPI curves are time-varying or flat, formula evidence
  showing selected backend inputs for the current KPI values, and backend
  variation explanations describing why each KPI moved or stayed flat;
- business/service traces;
- backend traffic-demand explanation from
  `backend_summary.traffic_demand_explanation_v1` for generated business
  request counts, active traffic classes, priority/data-volume summaries,
  compute-service correlation completeness, arrival windows, and per-user
  active service state. Offline result-package review of
  `traffic_demand_explanation_v1.json` includes the same compact explanation
  card, bounded per-user demand rows, and artifact-filtered user inspection
  without regenerating demand in the browser;
- route explanations;
- compute resource and task timeline summaries;
- user, satellite, and node detail pages;
- detail coverage status for backend detail families, cursor windows, hidden
  rows, exact node cards, and the active pagination contract;
- selected-detail evidence for the current user, satellite, route, service,
  service trace, and compute node selection, including whether backend exact
  detail is loading, synced, missing, or failed;
- a node evidence workspace that joins detail-page coverage, selected-row
  presence, and exact-detail request status so operators can see which node or
  service evidence comes from backend pages and which exact detail is still
  pending;
- an exact-detail review workspace that summarizes each selected detail family
  as backend exact detail, visible-window fallback, loading, failed, pending,
  or not selected, and counts reviewable fields, warnings, and resource/sync
  fields without recomputing business semantics in the browser;
- a read-only exact-detail raw JSON inspector. When backend exact details are
  synchronized, it exposes bounded JSON pointer rows for the selected payloads
  so operators can inspect the source fields behind the summary cards. Use the
  local JSON path filter to narrow rows by pointer, key, type, or preview value
  without changing backend payloads. Common exact-detail fields are also shown
  as focus rows when present, so route ids, latency, service state, compute
  node ids, and compute-resource fields are easier to inspect. For custom
  review, enter JSON pointers in the pin field; pinned paths show resolved,
  missing, or invalid status against the synchronized payloads, with a compact
  count summary for quick review readiness checks. When a package route detail
  is compared with the matching live route detail, the same pins are reused for
  a path-level package/live route diff. When a package service trace is
  compared with the matching live exact trace detail, the same pins are reused
  for a service-trace path diff using `/service_trace/...` or the `/trace`
  shortcut root. Saved route and service-trace comparison reports persist those
  pinned path rows into the package review JSON, including pointer, package/live
  values, status, and match/difference counts;
- service-trace closed-loop evidence, showing whether the selected service
  trace has correlated flow, route, user, satellite, compute-node, stage, and
  latency evidence from backend exact detail or the visible dashboard window.
  Package-vs-live service trace review also supports pinned JSON path
  comparison, so selected lifecycle fields can be checked as match, different,
  missing, or invalid without replaying events;
- one-click service-trace focus, which applies correlated filters across user,
  satellite, route, service, service-trace, and compute-node tables for the
  selected trace;
- a wide service-trace browser that expands the selected trace into lifecycle,
  correlation, route, user, satellite, and compute-node sections;
- configuration explanation and model assumptions.
- model-trust evidence, including configuration semantics, scale fidelity,
  KPI credibility, benchmark validation, KPI calibration, KPI formula evidence,
  route evidence, replay/export evidence, and runtime state.

Backend runtime status is the source of truth. The frontend should not invent
business semantics locally.

## 5. Export Results

Live runtime export:

```powershell
Invoke-RestMethod http://127.0.0.1:8765/runtime/export
```

Archive export:

```text
http://127.0.0.1:8765/runtime/export/archive
```

Each result package contains:

- `config_snapshot.json`
- `events.jsonl`
- `metrics.csv`
- `summary.json`
- `manifest.json`
- `service_lifecycle_trace_v2.json`
- `route_detail_index_v1.json`
- `review_summary_v1.json`
- `diagnostics_bundle_v1.json`
- `network_kpi_benchmark_validation_v1.json`
- `network_kpi_formula_evidence_v1.json`
- `network_kpi_variation_explanation_v1.json`
- `user_configuration_template_validation_v1.json`
- `traffic_demand_explanation_v1.json`
- `scenario_review_bundle_v1.json`
- `export_package_audit_index_v1.json`

The standalone dashboard export review area loads the selected package's
server-side route evidence page and shows route evidence counts,
export-window policy, cursor navigation, searchable/filterable route rows, and
package route-detail review without rerunning the simulation. The package
review area also loads `service_lifecycle_trace_v2.json` when it is present in
the export catalog and displays a read-only communication-compute service chain
review with trace counts, terminal-state totals, bounded stage rows,
backend-served artifact filters, and deterministic page controls. These filters
cover trace text, terminal state, compute node id, lifecycle stage, and
terminal reason. The package detail view reads the exported package itself and
does not rerun the simulation. The separate live lookup only
compares against the current runtime route detail endpoint when the same route
id is still present. Use `compare with live` to load both detail channels for
the same route in one click. If both package and live details are loaded for
the same route, the dashboard shows a package-vs-live comparison card with
matched and different route fields. If exact-detail JSON pointers are pinned,
the same card also compares those pinned `/route/...` paths against the package
route payload and the live route payload, reporting match, different, missing,
or invalid for each pinned path. If the comparison is not ready, the same area
explains whether package detail, live detail, or route-id mismatch is the
reason. The package review artifacts include `route_comparison_review`
metadata so the available comparison fields, live-runtime requirement, and
no-recompute boundaries are visible outside the dashboard UI. The same metadata
declares the `RUNTIME_EXPORT_ROUTE_COMPARISON_REVIEW_REPORT_V1` template for
recording selected route comparison outcomes with deterministic record ordering.
Runtime export rebuilds the package route evidence window with a 5000-row
maximum; hidden rows beyond that limit are reported in the package policy.
Service trace exports now use the same 5000-row default window and record
`runtime_export_service_trace_policy_v1` in `config_snapshot.json`; the trace
artifact and backend page response expose the same policy with exported and
hidden trace counts.
New exports also include `runtime_export_reproducibility_boundary_v1` in
`manifest.json`, `config_snapshot.json`, `review_summary_v1.json`, and
`diagnostics_bundle_v1.json`. This backend-owned boundary states that the
package is deterministic artifact evidence, restore is config-only, package
reads do not recompute model state, and live event replay restore, packet
capture, packet-level simulation, package mutation on read, and external
simulator artifacts are outside the export contract. The dashboard export
review area renders this boundary as a dedicated read-only card before the
manifest inspector, including boundary hash agreement, restore/read/compare
scope, route/service export windows, and no-replay/no-recompute/no-mutation
conditions. The dashboard also cross-checks the loaded package compare and
restore preflight results against the same boundary, so users can see whether a
restore decision is backed by config-only restore, config/generated-config
compare, persisted-artifact reads, and matching boundary hashes before acting.
New compare and restore-preflight API responses include
`runtime_export_boundary_alignment_v1`, so the dashboard can show the backend
alignment status, alignment hash, boundary hash, and warnings even before every
review artifact has finished loading. Older packages or older backend responses
still fall back to the manifest/review/diagnostics cross-check.
New exports also persist `user_configuration_template_validation_v1.json`.
This file is the offline copy of the backend-approved YAML template validation
evidence shown in the configuration contract card. Review summary,
diagnostics, scenario review, and audit index artifacts all expose compact
status/hash fields for this file so an exported package can prove which
approved user-facing configuration templates were validated without reloading
templates or applying a new config.
New exports also persist `traffic_demand_explanation_v1.json`. This file is
copied from
`config_snapshot.generated_config.backend_summary.traffic_demand_explanation_v1`
and records backend-owned business-demand semantics such as request counts,
active traffic classes, input flows, compute tasks, output flows,
compute-service correlation status, and per-user active-service row counts.
The review summary, diagnostics, scenario review, and audit index artifacts all
bind compact evidence fields for this file. Reading the artifact does not
regenerate traffic, replay events, perform packet-level simulation, or require
frontend-side business inference.
Packages also expose a cursor endpoint for the same per-user demand evidence:

```powershell
Invoke-RestMethod "http://127.0.0.1:8765/runtime/export/packages/<package_id>/traffic-demand-users?cursor=0&limit=100&traffic_class=COMPUTE_SERVICE"
```

This endpoint pages exported `per_user_active_service_state` rows and supports
`query` plus `traffic_class` filters. It reads the package artifact only; it
does not regenerate traffic, replay events, or mutate the package.
After using `compare with live`, the package-vs-live route comparison card can
save the currently displayed comparison into
`route_comparison_review_report_v1.json`. The saved record includes the
compared fields, different fields, package route detail hash, live route detail
hash, status reason, dashboard operator note, optional pinned path diff rows,
and the backend boundary alignment hash/status from the package
restore-preflight evidence. Service trace comparisons use the same pattern in
`service_trace_comparison_review_report_v1.json`. After the save completes,
the dashboard package review area shows the report artifact from the backend
export catalog with a direct JSON link and file hash. If the report artifact is
available, the dashboard loads it read-only and summarizes saved record counts,
MATCH/DIFFERENT/UNAVAILABLE/ERROR totals, route or trace detail hash pairs,
boundary alignment evidence, operator notes, and pinned-path counts. The route
report drawer can filter by status, search id/status/hash/note/pinned-path
text, and page through matching records through the backend cursor endpoint
without opening the raw JSON:

```powershell
Invoke-RestMethod "http://127.0.0.1:8765/runtime/export/packages/<package_id>/route-comparison-review-report/records?cursor=0&limit=100&status=DIFFERENT&query=/route/latency_s"
```

This records endpoint reads `route_comparison_review_report_v1.json` from the
selected package. It does not replay events, recompute routes, compare new live
state, or mutate package artifacts. Each package also exposes
`export_package_audit_index_v1.json`, which summarizes manifest, boundary
alignment, user configuration binding, diagnostics, route review report, and
artifact file hashes in one read-only audit entry. The dashboard loads this
audit index and displays it as a dedicated audit drawer with Manifest,
Configuration, Boundary, Diagnostics, Route Review, and Artifact Hash sections,
while still keeping a direct JSON link for operator review. The Configuration
section is backend-owned evidence from `/scenario/user-config/export`: it shows
the schema id, config hash, export hash, binding hash, and validation status
used for the exported package.
Each new package also contains `scenario_review_bundle_v1.json`, a compact
backend-generated review entry point that binds the effective user
configuration, scenario scale, runtime progress, reproducibility hashes,
review summary hash, diagnostics hash, audit-index filename, model boundaries,
and recommended review order. The dashboard loads it as a Scenario Review
Bundle card in the package review area with direct links to the JSON evidence.
The card also shows a guided review workflow that steps through scenario entry,
audit index, review summary, diagnostics, manifest, configuration, route
evidence, service trace, KPI formula evidence, configuration template
validation, traffic-demand explanation, user-service evidence, event evidence,
metrics, and summary artifacts, marking missing artifacts explicitly. It is
also available through the same package file endpoint and does not replay
events or recompute model state.
For JSON artifacts in that workflow, the dashboard can open the existing
read-only package artifact inspector. The configuration template validation
step opens `user_configuration_template_validation_v1.json` directly at
`/template_validation/templates`, which is the exported per-template validation
row list. This is an inspection path only: it does not reload templates,
revalidate configs, or mutate the active runtime session.
The diagnostics artifact also exposes `artifact_browser_index_v1`, which is the
backend source of truth for artifact categories, present/missing state, review
roles, default JSON pointers, and filter hints. The dashboard artifact-health
card and diagnostics drawer display this browser index when it is available, so
operators can move from a result package to the relevant KPI, business-demand,
route/service, reproducibility, or audit artifact without browser-side semantic
inference. Older packages that do not contain the index continue to use the
catalog and review-summary fallback.
In the artifact-health card, the browser index appears as compact category
rows. A row reports how many artifacts in that category are present or missing,
lists representative filenames, and exposes a default evidence button when the
backend marked an inspectable JSON artifact. Pressing that button opens the
read-only package artifact inspector at the backend-provided JSON pointer and
filter hint; it does not replay events, mutate the package, or recompute
acceptance.
Use the artifact browser filter controls to narrow the visible package files by
backend category, missing-artifact state, inspectable JSON artifacts, or text in
the filename/category/review-role fields. These controls are dashboard-local
review filters: they do not change the exported package, hide evidence from the
backend index, or alter artifact hashes.
The traffic-demand explanation step opens `traffic_demand_explanation_v1.json`
directly at `/traffic_demand_explanation`, so an operator can inspect generated
request counts, compute-service request counts, class rows, per-user state
counts, frontend-inference flags, and evidence hashes from the exported package
without regenerating traffic or replaying events.
When that artifact is selected, the dashboard also renders a compact
traffic-demand review card above the raw JSON preview. The card summarizes
configured/explained requests, input flows, tasks, output flows, active traffic
classes, per-class data volumes, per-user state count, compute-service
correlation status, packet-level flag, frontend-inference flag, and evidence
hash. The values are read from the exported artifact; the browser does not
derive new business-demand semantics. For per-user rows, the card now prefers
the backend traffic-demand user page endpoint and applies the current artifact
filter as the backend `query`. The label beginning with `backend page users`
shows the returned item count, matched count, total exported user count, and
cursor range. Use the previous/next controls in that card to page through the
backend traffic-demand user evidence. If that page is still loading or
unavailable, the card falls back to the bounded artifact preview.
The workflow includes an editable checklist. For each review row, the dashboard
lets the operator choose `REVIEWED`, `SKIPPED`, `NEEDS_FOLLOWUP`, or `ERROR`,
enter a short note, and save the checklist through the backend. After saving,
the dashboard refreshes the catalog and audit index so
`scenario_review_checklist_v1.json` and its hash/status/count are visible as
backend-owned package evidence.
The package review area also shows a completion banner sourced from
`export_package_audit_index_v1.json.package_review_completion_v1` when that
backend object is present. It combines audit status, saved route comparison
report presence, scenario review readiness, and checklist completion. Use that
banner as the first operator-facing signal for whether a result package is
ready for handoff, then inspect the underlying JSON links for evidence.
The same completion summary is available directly:

```powershell
Invoke-RestMethod "http://127.0.0.1:8765/runtime/export/packages/<package_id>/review-completion"
```

For a human-readable handoff file, download the backend-generated Markdown
report:

```powershell
Invoke-WebRequest `
  -OutFile "package_handoff_report_v1.md" `
  "http://127.0.0.1:8765/runtime/export/packages/<package_id>/handoff-report"
```

The standalone dashboard also shows a `Package handoff report` card for the
selected export package when `package_handoff_report_v1.md` is present in the
backend catalog. Use the `handoff report MD` link there for the same report
without manually constructing the URL.

For package-owned review, use:

```powershell
Invoke-RestMethod "http://127.0.0.1:8765/runtime/export/packages/<package_id>/routes?cursor=0&limit=100"
Invoke-RestMethod "http://127.0.0.1:8765/runtime/export/packages/<package_id>/routes/<route_id>"
Invoke-RestMethod "http://127.0.0.1:8765/runtime/export/packages/<package_id>/service-traces?cursor=0&limit=100&terminal_state=RUNNING"
Invoke-RestMethod "http://127.0.0.1:8765/runtime/export/packages/<package_id>/route-comparison-review-report/records?cursor=0&limit=100&status=DIFFERENT"
$body = @{
  records = @(
    @{
      route_id = "<route_id>"
      comparison_status = "DIFFERENT"
      compared_fields = @("latency", "bottleneck")
      different_fields = @("latency")
      status_reason = "FIELDS_DIFFER"
      operator_note = "manual review note"
    }
  )
} | ConvertTo-Json -Depth 5
Invoke-RestMethod `
  -Method Post `
  -ContentType "application/json" `
  -Body $body `
  "http://127.0.0.1:8765/runtime/export/packages/<package_id>/route-comparison-review-report"
```

The first two calls read the exported route detail index artifact. They do not
require the current runtime to contain the same route id. The POST call writes
`route_comparison_review_report_v1.json` into the selected package and updates
the export catalog; it records supplied review outcomes and does not rerun a
route comparison automatically. During that explicit save, the backend also
records the package restore-preflight boundary alignment hash and status so the
saved operator report can be audited later. It also regenerates
`export_package_audit_index_v1.json` so the audit index includes the saved
report hash while preserving the exported package's user configuration binding
evidence.

Guided scenario review checklist:

```powershell
$checklistBody = @{
  records = @(
    @{
      artifact_filename = "scenario_review_bundle_v1.json"
      step_label = "Scenario bundle checked"
      review_status = "REVIEWED"
      operator_note = "user configuration and package entry evidence reviewed"
      evidence_hash = "<scenario_review_hash>"
    }
  )
} | ConvertTo-Json -Depth 5
Invoke-RestMethod `
  -Method Post `
  -ContentType "application/json" `
  -Body $checklistBody `
  "http://127.0.0.1:8765/runtime/export/packages/<package_id>/scenario-review-checklist"
```

This writes `scenario_review_checklist_v1.json`, updates the export catalog,
and regenerates `export_package_audit_index_v1.json` with the checklist hash,
status, and record count. It also refreshes `package_handoff_report_v1.md` so
the Markdown handoff state follows the backend audit completion evidence. It
records operator decisions only; it does not
replay events, recompute routes or services, mutate packages on read, or update
archives that were created before the save.

Package audit index:

```powershell
Invoke-RestMethod "http://127.0.0.1:8765/runtime/export/packages/<package_id>/files/export_package_audit_index_v1.json"
Invoke-RestMethod "http://127.0.0.1:8765/runtime/export/packages/<package_id>/files/scenario_review_bundle_v1.json"
```

Export catalog:

```powershell
Invoke-RestMethod http://127.0.0.1:8765/runtime/export/catalog
```

## 6. Collect Diagnostics

When reporting a problem, collect an operator diagnostics bundle:

```powershell
.\diagnostics_leo_twin.bat
.\scripts\collect_operator_diagnostics.ps1 -JsonSummary
```

Default output:

```text
artifacts\operator_diagnostics
```

The bundle includes launcher health, runtime status, version info, current
config export, export catalog, diagnostics manifest, and copied launcher logs.

## 7. Benchmark And Acceptance

Baseline scenarios:

- 72 satellites: detailed baseline;
- 300 satellites: bounded scale transition;
- 1200 satellites: large-scale short responsiveness baseline.

Acceptance commands:

```powershell
.\scripts\verify_product_acceptance.ps1 -SkipBuild
.\scripts\verify_product_acceptance.ps1 -AcceptanceConfig configs\acceptance\small_demo_72sat.yaml
.\scripts\verify_product_acceptance.ps1 -SkipBuild -SkipRuntimeSmoke -RunBrowserSmoke
```

Disposable acceptance run from the shipped benchmark YAML files:

```powershell
.\disposable_acceptance_leo_twin.bat -PlanOnly -JsonSummary
.\scripts\run_disposable_acceptance.ps1 -SkipBuild
.\scripts\run_disposable_acceptance.ps1 -SkipBuild -AcceptanceConfig configs\acceptance\small_demo_72sat.yaml
```

The disposable harness restarts local services, applies each selected YAML
through backend `/control`, starts and stops the runtime, reuses
`verify_product_acceptance.ps1`, then restores `configs\sees_control.yaml` and
`configs\generated_full_system_demo.json` so local run state is not delivered as
product source. Add `-KeepServices` when you want to inspect the final scenario
after the run, or `-ExportPackage` when you want the backend to create a result
package during the same acceptance pass.

Benchmark contracts:

- `leo_twin.benchmark_scenario_matrix.v1`
- `leo_twin.model_verification_report_template.v1`
- `leo_twin.result_package_contract.v1`

## 8. Current Model Boundaries

SEES v2 is a deterministic flow-level digital twin prototype. It is useful for
controlled scenario exploration, dashboard semantics, and reproducible
engineering experiments.

It is not yet a high-fidelity engineering decision simulator. Current limits:

- no STK, EXATA, AFSIM, or DDS integration;
- no packet-level simulation;
- no RF propagation field solver;
- no antenna pattern modeling;
- no SGP4 orbital fidelity;
- no real code execution on compute nodes;
- large-scale scenarios use explicit fidelity reduction such as batched orbit
  updates and bounded candidate ISL links.

When scale mode is active, the backend reports the selected fidelity policy in
runtime status and the frontend displays it to users.

## 9. Where To Read More

- `docs\integration_demo.md`
- `docs\user_configuration_schema_v2.md`
- `docs\launcher_health_check_v2.md`
- `docs\operator_diagnostics_bundle_v1.md`
- `docs\result_package_contract_v1.md`
- `docs\product_acceptance_scenarios.md`
- `docs\launcher_troubleshooting.md`
