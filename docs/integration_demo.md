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
acceptance verification in fast or full-build mode, and collect an operator
diagnostics bundle. The direct
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
.\diagnostics_leo_twin.bat
.\scripts\sees_launcher.ps1 status
.\scripts\sees_launcher.ps1 status -JsonSummary
.\scripts\sees_launcher.ps1 health -JsonSummary
```

If the browser does not open automatically, run `.\scripts\sees_launcher.ps1
status` and open `http://127.0.0.1:5173` after the frontend reports running.
The launcher writes backend and frontend logs to `artifacts\launcher`; the
launcher health summary reports backend/frontend port readiness, HTTP
readiness, process ids, latest log paths, and config paths. It also shows the
last log lines when either service fails its HTTP health check. To keep the
service consoles visible for manual inspection, run:

```powershell
.\scripts\sees_launcher.ps1 start -VisibleWindows
```

To collect a support bundle with launcher health, runtime status, version info,
current config export, export catalog, and launcher logs, run:

```powershell
.\diagnostics_leo_twin.bat
.\scripts\collect_operator_diagnostics.ps1 -JsonSummary
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
- `GET /scenario/user-config/schema`
- `GET /scenario/user-config/templates`
- `GET /scenario/user-config/export`
- `POST /scenario/user-config/validate`
- `GET /metrics/snapshot`
- `GET /runtime/status`
- `GET /runtime/export`
- `GET /runtime/version`
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
`config_snapshot.json`, `events.jsonl`, `metrics.csv`, `summary.json`, and the
additional `service_lifecycle_trace_v2.json` observability artifact.
The archive endpoint returns the same package as a ZIP download with stable
entry ordering and fixed ZIP metadata.

Recent export history:

```powershell
Invoke-RestMethod http://127.0.0.1:8765/runtime/export/history
```

The runtime status payload also includes `runtime_export_history_v1`, which the
dashboard uses to show the latest package or archive export.

Runtime observability summaries:

```text
/runtime/status
  user_request_summary_v1
  satellite_service_summary_v1
  route_explanation_summary_v1
  node_detail_summary_v1
  service_lifecycle_trace_v2
```

`route_explanation_summary_v1` is backend-owned. It explains each visible route
with route/flow/user ids, source and destination, selected satellite, primary
next hop, path, capacity, demand, latency, loss proxy, business type,
bottleneck component, bottleneck reason, and a compact explanation label. It is
derived from the runtime snapshot and service history; it does not change route
selection or simulate packets.

Service trace detail APIs:

```text
/runtime/details/service-traces?cursor=0&limit=100&query=&terminal_state=ALL&compute_node_id=&stage_kind=ALL&terminal_reason=ALL
/runtime/details/service-traces/{trace_id}
```

The cursor endpoint returns deterministic `service_lifecycle_trace_v2` windows
with optional server-side query, raw terminal-state, compute-node, stage-kind,
and terminal-reason filters.
The exact trace endpoint accepts a trace id, normalized service id, task id,
input flow id, or output flow id and returns the backend-owned trace with
correlated user, route, satellite, and compute-node context.

Persisted export catalog:

```powershell
Invoke-RestMethod http://127.0.0.1:8765/runtime/export/catalog
```

The catalog endpoint reads `artifacts/runtime_exports/runtime_export_catalog_v1.json`.
It persists package/archive metadata and hashes so previous exports remain
discoverable after the backend process restarts.

User configuration contract:

```powershell
Invoke-RestMethod http://127.0.0.1:8765/scenario/user-config/schema
Invoke-RestMethod http://127.0.0.1:8765/scenario/user-config/templates
Invoke-RestMethod http://127.0.0.1:8765/scenario/user-config/export
$candidate = @{
  scenario = @{
    satellite_count = 72
    compute_nodes = 72
  }
  runtime = @{
    duration = 600
    seed = 20260703
  }
} | ConvertTo-Json -Depth 8
Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:8765/scenario/user-config/validate `
  -ContentType "application/json" `
  -Body $candidate

$yamlCandidate = @"
scenario:
  satellite_count: 72
  compute_nodes: 72
runtime:
  duration: 600
  seed: 20260703
"@
Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8765/scenario/user-config/validate-text?format=yaml" `
  -ContentType "text/plain; charset=utf-8" `
  -Body $yamlCandidate
```

These endpoints are backend-owned and read-only. They expose the full
user-facing configuration schema v2, the approved executable template catalog,
the current effective SEES config export with a stable hash and validation
status, and a validate-only user configuration preflight report. Configuration
import still happens only through explicit control-plane commands such as
`CONFIG_UPDATE`, `LOAD_TEMPLATE`, or `RESTORE_EXPORT_PACKAGE`.
`POST /scenario/user-config/validate` returns
`USER_CONFIGURATION_VALIDATION_REPORT` with normalized config/hash when
accepted, but it never writes config files, initializes runtime state, or
applies a `CONFIG_UPDATE` by itself. Accepted reports include an
`apply_command` that declares `normalized_config` as the safe
`CONFIG_UPDATE` payload source; applying it is a separate explicit user action
that reinitializes the demo runtime session and reconnects streams. Accepted
reports also include `change_summary`, a backend-generated diff between the
current effective config and the normalized candidate, with deterministic
field-path ordering and bounded preview rows. Reports include
`apply_readiness` as well, which records current controller/session lifecycle,
recommended action, confirmation requirement, and the fact that applying a
config rebuilds the session and stream buffers.
`POST /scenario/user-config/validate-text` accepts raw UTF-8 JSON/YAML text
with `format=auto|json|yaml` and returns the same report plus `text_parse`.
The standalone dashboard also shows these links in the user configuration
contract section so users can download the current full configuration and
inspect the backend schema without editing runtime state. The dashboard also
provides a JSON/YAML preflight box. JSON mapping mode calls
`POST /scenario/user-config/validate`; auto/YAML/JSON text modes call
`POST /scenario/user-config/validate-text`. The card displays the validation
report without auto-applying the candidate configuration. After a successful
preflight, the dashboard can send the backend-normalized mapping through the
existing `CONFIG_UPDATE` control channel. The preflight card renders the
backend `change_summary` so users can see changed field counts, section counts,
and bounded field-path previews before applying, and it renders
`apply_readiness` so the runtime/session side effect is visible before the
command is sent.

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

The standalone dashboard surfaces this as a guarded two-click restore action
inside the runtime export catalog. The first click arms the selected package;
the second click sends `RESTORE_EXPORT_PACKAGE` through `/control` with
`confirm_restore: true`. The read-only package, compare, and preflight links
remain non-mutating.

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
