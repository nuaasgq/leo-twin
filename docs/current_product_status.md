# Current Product Status

Date: 2026-07-05

Branch: `feature/T163-frontend-dashboard-compute-v2`

## Local Entry Points

- Interactive launcher: `.\leo_twin_launcher.bat`
- Console-first startup: `.\start_leo_twin.bat`
- Dashboard-first startup: `.\dashboard_leo_twin.bat`
- Status: `.\status_leo_twin.bat`
- Machine-readable launcher health: `.\scripts\sees_launcher.ps1 status -JsonSummary`
- Operator diagnostics bundle: `.\diagnostics_leo_twin.bat`
- Read-only health smoke: `.\smoke_leo_twin.bat`
- Mutating control-cycle smoke: `.\control_smoke_leo_twin.bat`
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
The latest frontend run after the pending-control render test included 25
frontend test files / 197 tests.

## Current Product Signals

- Backend runtime status is the source of truth for generated product summary.
- Dashboard service latency now uses backend-provided component summary,
  per-service trace rows, and visible `component_timeline` stage chips.
- Runtime health smoke reports endpoint timings, orbit/protocol fields,
  constellation profile, traffic class, compute node count, and compute
  resource model.
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
- Launcher workflow is Windows-first and supports menu, batch shortcuts,
  status, read-only smoke, control-cycle smoke, dashboard-first startup, and
  fast/full acceptance checks.

## Remaining Gaps

- Browser-rendered Playwright smoke is still not part of CI.
- Service trace drill-down filtering remains a future dashboard enhancement.
- Acceptance scripts validate currently running services; they do not yet
  launch disposable backends from selected acceptance YAML files.
- Runtime config staging guard is script-enforced, not a Git hook.
- Control-cycle smoke validates backend control protocol responsiveness, not
  browser button clicks.
