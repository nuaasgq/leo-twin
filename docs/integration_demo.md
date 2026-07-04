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
.\start_leo_twin.bat
```

This starts both backend and frontend, then opens the frontend in the browser.

Other launcher commands:

```powershell
.\restart_leo_twin.bat
.\stop_leo_twin.bat
.\scripts\sees_launcher.ps1 status
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
- `WS /stream/events`
- `WS /stream/state`

Replay artifacts:

```powershell
python run_demo.py --no-server --write-replay artifacts/integration_demo
```

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
