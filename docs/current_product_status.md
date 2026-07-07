# Current Product Status

Date: 2026-07-07

Branch: `feature/T372-dashboard-template-validation-detail-v1`

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

## Current Product Signals

- Backend runtime status is the source of truth for generated product summary.
- Dashboard service latency now uses backend-provided component summary,
  per-service trace rows, and visible `component_timeline` stage chips.
- Runtime health smoke reports endpoint timings, orbit/protocol fields,
  constellation profile, traffic class, compute node count, and compute
  resource model.
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
- Runtime export packages now include `network_kpi_formula_evidence_v1.json`
  and propagate its status/hash into review summary, diagnostics, scenario
  review, audit index, and dashboard export review labels. Offline package
  review can inspect KPI formula/input/time-series evidence without metric
  recomputation.
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
- Formula evidence is exported as a package artifact, but the dashboard still
  uses compact labels rather than a dedicated artifact drawer for every KPI
  input row.
- Template validation evidence is visible in the dashboard configuration
  contract section; a future configuration UX pass can add template search,
  filtering, and direct jump-to-template actions.
