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
- `GET /runtime/export/catalog`
- `GET /runtime/export/history`
- `GET /runtime/export/archive`
- `GET /runtime/export/packages/{package_id}`
- `GET /runtime/export/packages/{package_id}/manifest`
- `GET /runtime/export/packages/{package_id}/compare`
- `GET /runtime/export/packages/{package_id}/restore-preflight`
- `GET /runtime/export/packages/{package_id}/archive`
- `GET /runtime/export/packages/{package_id}/files/{filename}`
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

Downloadable archive:

```text
http://127.0.0.1:8765/runtime/export/archive
```

The live export writes a deterministic result package under
`artifacts/runtime_exports`. Each package contains `manifest.json`,
`config_snapshot.json`, `events.jsonl`, `metrics.csv`, and `summary.json`.
The archive endpoint returns the same package as a ZIP download with stable
entry ordering and fixed ZIP metadata.

Recent export history:

```powershell
Invoke-RestMethod http://127.0.0.1:8765/runtime/export/history
```

The runtime status payload also includes `runtime_export_history_v1`, which the
dashboard uses to show the latest package or archive export.

Persisted export catalog:

```powershell
Invoke-RestMethod http://127.0.0.1:8765/runtime/export/catalog
```

The catalog endpoint reads `artifacts/runtime_exports/runtime_export_catalog_v1.json`.
It persists package/archive metadata and hashes so previous exports remain
discoverable after the backend process restarts.

Persisted package artifact routes:

```text
http://127.0.0.1:8765/runtime/export/packages/{package_id}
http://127.0.0.1:8765/runtime/export/packages/{package_id}/manifest
http://127.0.0.1:8765/runtime/export/packages/{package_id}/compare
http://127.0.0.1:8765/runtime/export/packages/{package_id}/restore-preflight
http://127.0.0.1:8765/runtime/export/packages/{package_id}/archive
http://127.0.0.1:8765/runtime/export/packages/{package_id}/files/events.jsonl
```

These routes serve catalog-registered files from the export root. They do not
create a new export package and reject filenames that are not present in the
persisted catalog record.

The compare route reads the package `config_snapshot.json` and compares its
`config` and `generated_config` sections with the current backend runtime
configuration. It returns a deterministic summary with compatibility status,
diff counts, and a limited set of changed JSON paths. It does not restore or
mutate the current scenario.

The restore-preflight route validates the package `config_snapshot.json` as a
potential configuration restore source and reports readiness, required user
confirmation, config hashes, diff counts, warnings, and the next action. It is
strictly read-only: it does not write config files, stop the current runtime, or
replace the active scenario.

Runtime export restore is intentionally a control-plane command, not a GET
route. Send it through the existing `/control` WebSocket only after inspecting
the preflight result:

```json
{
  "type": "RUNTIME_CONTROL",
  "action": "RESTORE_EXPORT_PACKAGE",
  "payload": {
    "package_id": "runtime-export-...",
    "confirm_restore": true
  }
}
```

When the package is restorable, the backend first writes a rollback export
package for the current runtime configuration, then restores
`config_snapshot.config` through the same configuration validation and session
reinitialization path used by `INITIALIZE`. The command response includes
`restore_preflight` and `restore_result` summaries with package hashes,
rollback package id, and whether config files and live streams were affected.

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
