# Current Product Status

Date: 2026-07-05

Branch: `feature/T163-frontend-dashboard-compute-v2`

## Local Entry Points

- Interactive launcher: `.\leo_twin_launcher.bat`
- Console-first startup: `.\start_leo_twin.bat`
- Dashboard-first startup: `.\dashboard_leo_twin.bat`
- Status: `.\status_leo_twin.bat`
- Read-only health smoke: `.\smoke_leo_twin.bat`

Default local URLs:

- Console: `http://127.0.0.1:5173`
- Dashboard: `http://127.0.0.1:5173/dashboard`
- Backend runtime status: `http://127.0.0.1:8765/runtime/status`

## Acceptance Command

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\verify_product_acceptance.ps1 -ExpectedSatelliteCount 120 -ExpectedUserCount 100 -ExpectedComputeNodeCount 120 -ExpectedConstellationProfile CUSTOM_WALKER -ExpectedTrafficClass COMPUTE_SERVICE
```

The latest full local run passed:

- runtime config staging guard;
- forbidden runtime import guard;
- backend service timeline targeted tests;
- frontend visual/dashboard tests;
- frontend build;
- read-only runtime health smoke.

## Current Product Signals

- Backend runtime status is the source of truth for generated product summary.
- Dashboard service latency now uses backend-provided component summary,
  per-service trace rows, and visible `component_timeline` stage chips.
- Runtime health smoke reports endpoint timings, orbit/protocol fields,
  constellation profile, traffic class, compute node count, and compute
  resource model.
- Launcher workflow is Windows-first and supports menu, batch shortcuts,
  status, smoke, dashboard-first startup, and fast/full acceptance checks.

## Remaining Gaps

- Browser-rendered Playwright smoke is still not part of CI.
- Service trace drill-down filtering remains a future dashboard enhancement.
- Acceptance scripts validate currently running services; they do not yet
  launch disposable backends from selected acceptance YAML files.
- Runtime config staging guard is script-enforced, not a Git hook.
