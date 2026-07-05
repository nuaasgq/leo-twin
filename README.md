# leo-twin

`leo-twin` is a deterministic Low Earth Orbit satellite internet communication-computing digital twin simulation platform.

## Current Phase

The current phase is **full-system engineering iteration**.

MVP-0 remains the historical foundation: it established the deterministic discrete-event kernel and repository rules. The project now includes event-driven orbit, network, compute, metrics, control-plane, reviewer, and frontend subsystems. All domain interaction still flows through `SimEvent` and `SimulationKernel.schedule_event()`.

## Current Capabilities

- Deterministic event kernel with strict event ordering.
- Keplerian-style orbit runtime for configurable satellite state generation.
- Position-driven network runtime with access, link, routing, transport, physical, and channel abstractions.
- Route-aware compute runtime with scheduling policies and compute-to-network load feedback.
- Metrics collection and full-system pipeline demos.
- Config-driven runtime control with initialize/start/pause/stop/reset actions.
- Chinese frontend surfaces for three-dimensional control and standalone data dashboard.
- Reviewer and CI gate workflow for deterministic engineering checks.

## Engineering Rules

- One issue = one feature = one branch.
- All functionality must be test-driven.
- All results must be deterministic.
- All parameters must be configuration-driven.
- Event Kernel remains the only simulation time authority.
- Domain modules must not call each other directly.
- Cross-domain communication must use events only.

## Run Locally

Windows one-command launcher:

```powershell
.\leo_twin_launcher.bat
.\start_leo_twin.bat
```

The menu launcher includes console/dashboard startup, status, read-only health
smoke, restart/stop, and fast/full product acceptance verification.

Useful launcher commands:

```powershell
.\restart_leo_twin.bat
.\dashboard_leo_twin.bat
.\status_leo_twin.bat
.\smoke_leo_twin.bat
.\control_smoke_leo_twin.bat
.\stop_leo_twin.bat
.\scripts\sees_launcher.ps1 status
.\scripts\sees_launcher.ps1 restart -OpenSurface dashboard
.\scripts\smoke_runtime_health.ps1
.\scripts\smoke_runtime_health.ps1 -JsonSummary
.\scripts\smoke_runtime_control_cycle.ps1
```

Default local surfaces:

- Console: `http://127.0.0.1:5173`
- Dashboard: `http://127.0.0.1:5173/dashboard`
- Backend status: `http://127.0.0.1:8765/runtime/status`

Launcher logs are written to `artifacts\launcher`.
Troubleshooting notes are in `docs\launcher_troubleshooting.md`.
Current product status is summarized in `docs\current_product_status.md`.

## Run Tests

```powershell
$env:PYTHONPATH='src;.'
pytest
```

Frontend:

```powershell
pnpm --dir frontend test
pnpm --dir frontend build
```

Frontend visual/dashboard verification:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\verify_frontend_visuals.ps1
```

Product acceptance verification:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\verify_product_acceptance.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\verify_product_acceptance.ps1 -ExpectedSatelliteCount 120 -ExpectedUserCount 100 -ExpectedComputeNodeCount 120 -ExpectedConstellationProfile CUSTOM_WALKER -ExpectedTrafficClass COMPUTE_SERVICE
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\verify_product_acceptance.ps1 -AcceptanceConfig configs\acceptance\small_demo_72sat.yaml
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\verify_product_acceptance.ps1 -SkipBuild -RunControlCycleSmoke
```

Control-cycle smoke verification. This mutates the running backend session by
initializing, starting, pausing, resuming, stopping, and resetting it:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke_runtime_control_cycle.ps1
```

Before committing local development work:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\pre_commit_checks.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\check_no_runtime_config_staged.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\check_forbidden_runtime_imports.ps1
```
