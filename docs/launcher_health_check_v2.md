# Launcher Health Check v2

Date: 2026-07-06
Branch: `feature/T222-launcher-health-check-v2`

Launcher health check v2 gives operators one local diagnostic surface for the
Windows launcher. It does not change simulation behavior or Event Kernel logic.

## Commands

Human-readable status:

```powershell
.\scripts\sees_launcher.ps1 status
.\scripts\sees_launcher.ps1 health
```

Machine-readable status:

```powershell
.\scripts\sees_launcher.ps1 status -JsonSummary
.\scripts\sees_launcher.ps1 health -JsonSummary
```

The JSON payload uses:

```text
leo_twin.launcher_health.v2
```

It also includes a one-click startup acceptance object:

```text
leo_twin.launcher_one_click_acceptance.v1
```

## Reported Fields

The health summary reports:

- overall status: `HEALTHY`, `DEGRADED`, or `STOPPED`;
- backend port, URL, health URL, process ids, process names, and readiness;
- frontend port, URL, health URL, process ids, process names, and readiness;
- latest backend/frontend stdout and stderr log paths;
- repository root;
- launcher log directory;
- scenario config path;
- effective control config path;
- generated config path;
- one-click acceptance status, blockers, next action, and smoke command;
- recommended diagnostic actions.

## Readiness Semantics

Each service reports:

- `READY`: port is listening and HTTP health check passes;
- `PORT_ONLY`: port is listening but HTTP health check fails;
- `STOPPED`: configured port is not listening.

Overall status is:

- `HEALTHY` when backend and frontend are both `READY`;
- `STOPPED` when both are `STOPPED`;
- `DEGRADED` for mixed or partial readiness.

## One-Click Acceptance Semantics

`one_click_acceptance_v1` is a deterministic operator summary derived from the
same backend/frontend service probes:

- `PASS`: backend and frontend are both `READY`;
- `STOPPED`: both required services are stopped;
- `BLOCKED`: at least one required service is not `READY`.

The object reports `blocking_services`, `blocked_service_count`,
`ready_service_count`, `next_action`, and `smoke_command`. It is intended for
launcher scripts, operator diagnostics, and automated smoke checks. It does not
start or stop services by itself and does not change simulation behavior.

## Paths

Default paths:

```text
artifacts\launcher
configs\integration_demo.yaml
configs\sees_control.yaml
configs\generated_full_system_demo.json
```

`configs\sees_control.yaml` and
`configs\generated_full_system_demo.json` are runtime/local state files and
must not be committed unless a task explicitly scopes them.

## Constraints

The health summary repeats the product constraints for diagnostics:

- Event Kernel frozen;
- no packet-level simulation;
- no STK, EXATA, AFSIM, or DDS.
