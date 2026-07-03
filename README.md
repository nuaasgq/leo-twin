# leo-twin

`leo-twin` is a Low Earth Orbit satellite internet digital twin and communication-computing network simulation project.

## Current Phase

The current phase is **MVP-0**.

MVP-0 only establishes a deterministic discrete-event simulation framework foundation. It does not implement simulation models, orbital mechanics, networking, routing, compute models, visualization, external simulator integration, AI/ML, multithreading, or distributed execution.

## Repository Scope

This repository currently contains:

- Project structure for future core, model, service, adapter, schema, and example modules.
- Documentation for architecture, data entities, development plan, and Codex development rules.
- Placeholder configuration files for future deterministic scenarios.
- Pytest setup and a structure-only test.

## Development Rules

- One issue = one feature = one branch.
- All functionality must be test-driven.
- All results must be deterministic.
- All parameters must be configuration-driven.
- Core logic must not use global mutable state.
- Simulation time must be controlled only by the future `SimulationKernel`.
- MVP-0 must not introduce high-fidelity models or external simulator dependencies.

## Run Tests

```powershell
python -m pytest
```
