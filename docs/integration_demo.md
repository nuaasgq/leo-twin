# Full System Integration Demo

This demo runs the SEES event-driven backend and streams the resulting
digital-twin event log to the React/Cesium observability frontend.

## Scenario

- 72 satellites
- 1000 ground users
- 3 ground stations
- 10 compute nodes
- 600 seconds of logical simulation time

The demo uses `configs/integration_demo.yaml`.

## One-Click Windows Launcher

For normal Windows use, start from the repository root:

```powershell
.\leo_twin_launcher.bat
.\start_leo_twin.bat
```

The menu launcher lets you start the console, start the dashboard, inspect
status, run a read-only smoke check, restart, stop services, or run product
acceptance verification in fast or full-build mode. The direct
`start_leo_twin.bat` path starts both backend and frontend, waits until both
ports are ready, checks the backend `/runtime/status` endpoint and the frontend
homepage over HTTP, then opens the frontend in the browser.

Other launcher commands:

```powershell
.\restart_leo_twin.bat
.\dashboard_leo_twin.bat
.\status_leo_twin.bat
.\smoke_leo_twin.bat
.\stop_leo_twin.bat
.\scripts\sees_launcher.ps1 status
```

If the browser does not open automatically, run `.\scripts\sees_launcher.ps1
status` and open `http://127.0.0.1:5173` after the frontend reports running.
The launcher writes backend and frontend logs to `artifacts\launcher` and shows
the last log lines when either service fails its HTTP health check. To keep the
service consoles visible for manual inspection, run:

```powershell
.\scripts\sees_launcher.ps1 start -VisibleWindows
```

Troubleshooting notes: `docs\launcher_troubleshooting.md`.

To open the standalone dashboard directly after startup or restart, run:

```powershell
.\scripts\sees_launcher.ps1 restart -OpenSurface dashboard
```

After the launcher reports both services healthy, run a read-only smoke check:

```powershell
.\scripts\smoke_runtime_health.ps1
.\scripts\smoke_runtime_health.ps1 -JsonSummary
.\scripts\smoke_runtime_health.ps1 -ExpectedSatelliteCount 120 -ExpectedUserCount 100 -ExpectedComputeNodeCount 120 -ExpectedConstellationProfile CUSTOM_WALKER -ExpectedTrafficClass COMPUTE_SERVICE
```

## Backend

```powershell
python run_demo.py
```

Default backend address:

```text
http://127.0.0.1:8765
```

Endpoints:

- `GET /scenario/config`
- `GET /metrics/snapshot`
- `GET /runtime/status`
- `GET /runtime/export`
- `WS /stream/events`
- `WS /stream/state`

Replay artifacts:

```powershell
python run_demo.py --no-server --write-replay artifacts/integration_demo
```

Live runtime export:

```powershell
Invoke-RestMethod http://127.0.0.1:8765/runtime/export
```

The live export writes a deterministic result package under
`artifacts/runtime_exports`. Each package contains `manifest.json`,
`config_snapshot.json`, `events.jsonl`, `metrics.csv`, and `summary.json`.

## Frontend

```powershell
cd frontend
pnpm install
pnpm dev
```

The Vite development server proxies `/stream`, `/metrics`, and `/scenario` to
the backend at `127.0.0.1:8765`.

## Validation

```powershell
python -m pytest
cd frontend
pnpm test
pnpm build
```
