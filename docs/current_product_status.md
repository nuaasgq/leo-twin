# Current Product Status

Date: 2026-07-08

Branch: `feature/T390-dashboard-exact-detail-review-workspace-v1`

## Local Entry Points

- Interactive launcher: `.\leo_twin_launcher.bat`
- Console-first startup: `.\start_leo_twin.bat`
- Dashboard-first startup: `.\dashboard_leo_twin.bat`
- Status: `.\status_leo_twin.bat`
- Machine-readable launcher health: `.\scripts\sees_launcher.ps1 status -JsonSummary`
- Operator diagnostics bundle: `.\diagnostics_leo_twin.bat`
- Read-only health smoke: `.\smoke_leo_twin.bat`
- Mutating control-cycle smoke: `.\control_smoke_leo_twin.bat`
- Browser acceptance smoke: `.\browser_smoke_leo_twin.bat`
- Disposable acceptance harness: `.\disposable_acceptance_leo_twin.bat`
- User guide: `docs\user_guide_v2.md`

Default local URLs:

- Console: `http://127.0.0.1:5173`
- Dashboard: `http://127.0.0.1:5173/dashboard`
- Backend runtime status: `http://127.0.0.1:8765/runtime/status`

## Acceptance Command

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\verify_product_acceptance.ps1 -ExpectedSatelliteCount 120 -ExpectedUserCount 100 -ExpectedComputeNodeCount 120 -ExpectedConstellationProfile CUSTOM_WALKER -ExpectedTrafficClass COMPUTE_SERVICE
```

Optional 1200-node control-cycle gate:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\verify_product_acceptance.ps1 -SkipBuild -RunControlCycleSmoke -ExpectedSatelliteCount 1200 -ExpectedUserCount 20 -ExpectedComputeNodeCount 1200 -ExpectedConstellationProfile CUSTOM_WALKER -ExpectedTrafficClass COMPUTE_SERVICE
```

Optional browser-rendered gate:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\verify_product_acceptance.ps1 -SkipBuild -SkipRuntimeSmoke -RunBrowserSmoke
```

Disposable acceptance harness for the shipped 72 / 300 / 1200 benchmark YAMLs:

```powershell
.\disposable_acceptance_leo_twin.bat -PlanOnly -JsonSummary
.\scripts\run_disposable_acceptance.ps1 -SkipBuild
```

The latest full local run passed:

- runtime config staging guard;
- forbidden runtime import guard;
- backend service timeline targeted tests;
- frontend visual/dashboard tests;
- frontend build;
- read-only runtime health smoke.

The latest fast local run with `-RunControlCycleSmoke` also passed for a
1200-satellite / 20-user / 1200-compute-node scenario and verified INITIALIZE,
START, PAUSE, RESUME, STOP, and RESET through the control websocket.
The latest T370 validation added result-package export checks for network KPI
formula evidence, passed 35 targeted backend tests, passed 26 frontend test
files / 456 tests, and completed a production build. Vite reported the
existing `DataPanel` chunk-size warning after minification.
The latest T371 validation adds user configuration template validation
evidence to the backend template catalog/reference surfaces and dashboard
configuration contract labels. Targeted backend configuration tests and
frontend configuration/API tests passed, and the production build completed.
Vite reported the existing `DataPanel` chunk-size warning after minification.
The latest T372 validation adds a dashboard per-template validation evidence
table on top of T371. `pnpm --dir frontend test dataPanel.test.ts` passed 216
tests, and `pnpm --dir frontend build` completed. Vite reported the existing
`DataPanel` chunk-size warning after minification.
The latest T373 validation persists the same backend-owned user configuration
template validation evidence into result packages as
`user_configuration_template_validation_v1.json`. Review summary, diagnostics,
scenario review, audit index, and dashboard export review labels now expose
the backend validation status/hash without reloading templates or applying a
new config.
The latest T374 validation adds a scenario-review workflow JSON inspector
entry for result-package artifacts. In particular,
`user_configuration_template_validation_v1.json` now opens the existing
read-only package artifact viewer at `/template_validation/templates`, so
operators can inspect exported per-template validation rows directly from the
package review workflow.
The latest T377 validation persists the backend-owned traffic-demand
explanation into result packages as `traffic_demand_explanation_v1.json`.
Review summary, diagnostics, scenario review, and audit index artifacts expose
request counts, compute-service counts, frontend-inference flags, and evidence
hashes without regenerating traffic or replaying events.
The latest T378 validation wires that exported traffic-demand explanation into
the standalone dashboard scenario-review workflow. Operators can open
`traffic_demand_explanation_v1.json` through the existing read-only package
artifact inspector at `/traffic_demand_explanation`, while review summary,
diagnostics, scenario review, and audit index labels show backend-owned request
counts and evidence hashes.
The latest T379 validation adds a compact dashboard card on top of that
artifact inspector. When `traffic_demand_explanation_v1.json` is selected, the
dashboard shows backend-owned request totals, compute-service counts, flow/task
counts, class rows, per-user state counts, correlation status, and
frontend-inference / packet-level flags before the raw JSON preview.
The latest T380 validation extends that card with bounded per-user demand rows
from the same exported artifact. The existing artifact filter can narrow the
user rows by user id or displayed service/request labels, while the browser
still treats `traffic_demand_explanation_v1.json` as the source of truth.
The latest T381 validation adds a package-owned traffic-demand user page
endpoint at `/runtime/export/packages/{package_id}/traffic-demand-users`. It
pages and filters exported `per_user_active_service_state` rows by query and
traffic class without regenerating demand, replaying events, or mutating the
result package. The frontend API contract exposes the same endpoint for the
next dashboard binding step.
The latest T382 validation binds the standalone dashboard traffic-demand compact
card to that backend page. When `traffic_demand_explanation_v1.json` is
selected, the card loads `traffic-demand-users` with the current artifact
filter and shows backend page counts/cursor state; if the page is still loading
or unavailable, it falls back to the bounded artifact preview.
The latest T383 validation adds explicit previous/next controls to that compact
card, so operators can page through backend traffic-demand user evidence from
the card without loading the full JSON artifact.

## Current Product Signals

- Backend runtime status is the source of truth for generated product summary.
- Dashboard service latency now uses backend-provided component summary,
  per-service trace rows, and visible `component_timeline` stage chips.
- Runtime health smoke reports endpoint timings, orbit/protocol fields,
  constellation profile, traffic class, compute node count, and compute
  resource model.
- Traffic demand batches now expose a deterministic
  `leo_twin.traffic_demand_explanation.v1` summary. It reports generated
  request counts, active traffic classes, per-class data volumes, priority
  ranges, compute-service task/output-flow correlation, arrival window, and
  per-user active service state without changing flow generation or event
  scheduling.
- The dashboard traffic-demand artifact card now renders a bounded per-user
  demand preview from exported `per_user_active_service_state` rows and reuses
  the artifact filter for user-level inspection without regenerating demand in
  the frontend.
- Runtime export packages now expose the same per-user traffic-demand state
  through a deterministic cursor endpoint,
  `/runtime/export/packages/{package_id}/traffic-demand-users`, so large
  package review can page user demand evidence instead of loading the whole
  artifact in the browser.
- The traffic-demand compact card now prefers that backend cursor page for
  per-user rows and shows `backend page users ... / cursor ...` in the card,
  preserving the artifact preview only as a fallback.
- The same card now includes previous/next cursor controls for the backend
  traffic-demand user page, keeping large package review inside the backend
  pagination contract.
- Generated backend summaries now expose the same traffic-demand explanation
  under `backend_summary.traffic_demand_explanation_v1`. The object is derived
  from the backend traffic configuration, uses a bounded endpoint/request
  explanation window for large payloads, and marks
  `frontend_inference_required=false` so UI surfaces can explain user business
  demand without recomputing it locally.
- Runtime status now includes backend-owned `network_kpi_calibration_v1`, which
  audits whether throughput, latency, loss proxy, and delay-variation proxy
  have actually changed over simulation time and explains flat values from
  backend sample evidence.
- The standalone dashboard renders `network_kpi_calibration_v1` in the network
  KPI panel and model-trust workspace, so users can see whether KPI curves are
  time-varying, partially varying, flat under activity, or sample-limited.
- Runtime status now includes backend-owned `network_kpi_formula_evidence_v1`,
  which joins KPI provenance and KPI calibration into a single formula/input/
  time-series evidence summary. The dashboard renders it in the network KPI
  panel and model-trust workspace rather than inferring formula credibility
  locally.
- Runtime status now also includes backend-owned
  `network_kpi_variation_explanation_v1`, which turns KPI calibration and
  formula evidence into user-facing explanations for why throughput, latency,
  loss proxy, and jitter proxy moved or stayed flat over simulation time. The
  standalone dashboard renders this explanation in the network KPI panel from
  backend-provided fields.
- Runtime export packages now include `network_kpi_formula_evidence_v1.json`
  and propagate its status/hash into review summary, diagnostics, scenario
  review, audit index, and dashboard export review labels. Offline package
  review can inspect KPI formula/input/time-series evidence without metric
  recomputation.
- Runtime export packages now also include
  `network_kpi_variation_explanation_v1.json` and propagate its status/hash,
  time-varying KPI count, and missing-explanation count into review summary,
  diagnostics, scenario review, audit index, and dashboard export review
  labels. Offline package review can inspect why flow-level KPI values moved
  or stayed flat without loading a live runtime.
- `diagnostics_bundle_v1.json` now includes backend-owned
  `artifact_browser_index_v1`, a deterministic package artifact browser index
  that groups core reproducibility, operator-review, KPI, business-demand,
  route/service, raw-runtime, and audit/handoff artifacts. The dashboard
  displays this backend-provided index in artifact health and diagnostics
  review surfaces and uses its JSON pointer/filter hints for read-only artifact
  inspection instead of hardcoding those review semantics locally.
- The dashboard artifact-health card now renders a compact artifact browser
  workspace from `artifact_browser_index_v1`. Each backend category shows
  present/missing counts, representative artifact filenames, the default JSON
  inspection target, and a direct evidence-inspection button when a readable
  JSON artifact is available.
- The same artifact browser workspace now supports local category, missing
  artifact, inspectable-JSON, and text filters. Filtering only changes the
  dashboard-visible artifact rows; the complete backend-derived artifact set
  remains available for review and evidence actions.
- Runtime export packages now also include
  `user_configuration_template_validation_v1.json` and propagate approved
  template validation status, valid/invalid counts, and evidence hash into the
  same result-package review surfaces. Offline package review can verify the
  shipped user-facing configuration templates without revalidating them in the
  frontend or mutating the active runtime config.
- Runtime export packages now also include
  `traffic_demand_explanation_v1.json`, copied from
  `config_snapshot.generated_config.backend_summary.traffic_demand_explanation_v1`.
  The review summary, diagnostics bundle, scenario review bundle, and audit
  index bind the same evidence hash and request counters so offline reviewers
  can inspect backend-owned business-demand semantics without traffic
  regeneration, event replay, packet-level simulation, or frontend inference.
- The dashboard scenario-review workflow now provides JSON-inspector entry
  points for package artifacts. Configuration template validation artifacts
  default to the `/template_validation/templates` path, and traffic-demand
  explanation artifacts default to `/traffic_demand_explanation`. The
  traffic-demand artifact now also renders a compact review card with request,
  flow, task, output-flow, class-row, per-user-state, and correlation labels.
  These views remain read-only and reuse the existing persisted package file
  endpoint.
- User configuration template catalog and reference surfaces now include
  backend-owned `sees.user_configuration_template_validation.v1` evidence.
  The evidence loads approved YAML templates through the same backend config
  loader/schema validation path used by runtime control, records file/config
  hashes and scale summaries, and is also available through
  `/scenario/user-config/template-validation`. The dashboard configuration
  contract card shows compact template validation counts, evidence hash labels,
  and a per-template validation table from backend output.
- The standalone dashboard now shows a detail-coverage card in the user/satellite
  detail section. It reports how many backend detail families are present,
  returned-vs-total rows, hidden/cursor-limited rows, exact node cards, and the
  active pagination contract.
- The same detail section now shows selected-detail evidence for the currently
  selected user, satellite, route, service, service trace, and compute node. It
  separates table-row evidence, backend exact-detail availability, loading
  state, and exact-detail errors.
- The same evidence row now includes a service-trace closed-loop correlation
  note. For a selected service trace it reports whether flow, route, user,
  satellite, compute-node, stage, and latency evidence comes from backend exact
  detail or from the current visible window fallback.
- The service trace table now exposes a compact focus bar. After selecting a
  service trace, users can apply one-click correlated filters to the user,
  satellite, route, service, service-trace, and compute-node detail tables, with
  backend exact trace detail preferred over visible-window fallback.
- The node-detail workspace now includes a wide service-trace browser. It
  expands the selected trace into lifecycle, correlation, route, user,
  satellite, and compute-node sections, using backend exact trace detail when
  available and visible-window fallback otherwise.
- The same node-detail area now includes a compact evidence workspace that
  joins backend detail-page coverage, selected table-row presence, and exact
  detail request status for users, satellites, routes, services, service
  traces, and compute nodes. The workspace is frontend display logic only; the
  source of truth remains the existing backend detail pages and App-owned exact
  detail requests.
- The node-detail area also includes an exact-detail review workspace. It
  summarizes, by detail family, whether the selected evidence is backend exact
  detail, visible-window fallback, loading, failed, or pending, and counts
  reviewable fields, warning fields, and resource/synchronization fields from
  the existing inspector view models.
- Launcher health v2 reports backend/frontend port readiness, HTTP readiness,
  process ids, latest log paths, config paths, and recommended actions.
- Operator diagnostics bundle captures launcher health, runtime status, version
  info, user config export, export catalog, and launcher logs under
  `artifacts\operator_diagnostics`.
- Runtime control-cycle smoke validates 1200-node control responsiveness
  through the existing backend control websocket and resets the active session
  at the end.
- Aggregate product acceptance can optionally run the mutating control-cycle
  smoke via `-RunControlCycleSmoke`.
- Browser acceptance smoke validates real console initialize/start clicks,
  dashboard visibility, browser page errors, and browser-side stop/reset cleanup
  through `scripts\smoke_browser_acceptance.ps1`. The browser command path uses
  backend `POST /control` as the frontend button transport, while the existing
  `/control` WebSocket remains available for backend control-cycle smoke and
  compatibility.
- Disposable acceptance harness prepares a clean temporary backend/frontend run,
  initializes each standard acceptance YAML through backend `/control`, starts
  and stops the runtime, reuses `verify_product_acceptance.ps1`, optionally
  exports a runtime package, and restores local runtime config drift files after
  execution.
- The Cesium control view disables Cesium's default render-loop error overlay
  and routes render errors into the existing local error state, so render errors
  no longer block runtime control buttons.
- Launcher workflow is Windows-first and supports menu, batch shortcuts,
  status, read-only smoke, control-cycle smoke, browser smoke,
  dashboard-first startup, and fast/full acceptance checks.
- System v2 baseline completion is reconciled in
  `docs\system_v2_completion_audit_v1.md`. The planned v2 workstreams now
  have Status coverage, while v2.1 hardening remains active.

## Remaining Gaps

- Browser-rendered smoke is available as an optional local gate, but is still
  not part of CI.
- Service trace drill-down filtering remains a future dashboard enhancement,
  although the dashboard now exposes detail coverage, cursor scope, and selected
  exact-detail evidence.
- Disposable acceptance can launch selected acceptance YAML files from a clean
  service restart, but it is still a local Windows harness rather than CI.
- Runtime config staging guard is script-enforced, not a Git hook.
- Control-cycle smoke validates backend control protocol responsiveness; use
  browser smoke when the risk is browser button wiring or dashboard rendering.
- The package JSON inspector is still an embedded bounded review card rather
  than a dedicated virtualized artifact browser.
- KPI calibration is visible in the dashboard; a future pass can add filtering
  or a wider drawer if more KPI families are added.
- KPI formula evidence is visible as a compact card; a future pass can add a
  wider source-field/input drawer if operators need to inspect every KPI input
  for larger scenarios.
- KPI variation explanation is visible in the dashboard runtime view and in
  exported result packages; a later artifact browser pass can add a wider
  per-KPI drawer for every explanation item.
- Formula evidence is exported as a package artifact, but the dashboard still
  uses compact labels rather than a dedicated artifact drawer for every KPI
  input row.
- Template validation evidence is visible in the dashboard configuration
  contract section; a future configuration UX pass can add template search,
  filtering, and direct jump-to-template actions.
