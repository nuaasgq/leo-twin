# Launcher Troubleshooting

Date: 2026-07-05

Use this checklist when the local console or dashboard does not open, appears
stale, or the backend/frontend buttons do not respond.

## First Checks

Run the interactive launcher:

```powershell
.\leo_twin_launcher.bat
```

For non-destructive checks:

```powershell
.\status_leo_twin.bat
.\smoke_leo_twin.bat
```

For a control-path check that intentionally mutates the running backend session:

```powershell
.\control_smoke_leo_twin.bat
```

Expected URLs:

- Console: `http://127.0.0.1:5173`
- Dashboard: `http://127.0.0.1:5173/dashboard`
- Backend runtime status: `http://127.0.0.1:8765/runtime/status`

## Common Symptoms

| Symptom | Check | Action |
| --- | --- | --- |
| Browser opens but page is blank | Run `.\status_leo_twin.bat` | If frontend is stopped, run `.\restart_leo_twin.bat`. |
| Dashboard does not open automatically | Run `.\scripts\sees_launcher.ps1 status` | Open the Dashboard URL printed by status. |
| Buttons stay in starting/stopping state | Run `.\smoke_leo_twin.bat`, then `.\control_smoke_leo_twin.bat` | If health passes but control smoke fails, restart services and inspect `artifacts\launcher\*-backend.err.log`. |
| Port is already occupied | Run `.\restart_leo_twin.bat` | The launcher stops listeners on configured backend/frontend ports before restart. |
| `node` is not recognized | Run `.\scripts\verify_frontend_visuals.ps1` | The script repairs bundled Node PATH when launched from the bundled `pnpm.cmd` path. |
| Need dashboard-first startup | Run `.\dashboard_leo_twin.bat` | This starts services and opens `/dashboard`. |

## Logs

Launcher logs are written to:

```text
artifacts\launcher
```

When startup health checks fail, `scripts\sees_launcher.ps1` prints the last
backend and frontend log lines automatically.

## Non-Destructive Validation

The read-only health smoke does not send `/control` commands and does not
modify generated runtime config files:

```powershell
.\scripts\smoke_runtime_health.ps1 -JsonSummary
```

Use the aggregate acceptance command after both services are already running:

```powershell
.\scripts\verify_product_acceptance.ps1 -SkipBuild
```

## Control-Path Validation

The control-cycle smoke opens the existing control websocket and exercises
INITIALIZE, START, PAUSE, RESUME, STOP, and RESET. It is intended for diagnosing
button pending states and will reset the current demo session:

```powershell
.\scripts\smoke_runtime_control_cycle.ps1 -JsonSummary
```
