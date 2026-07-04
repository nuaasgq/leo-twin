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
