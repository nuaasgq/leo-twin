# Codex Development Rules

This document defines the operating rules for Codex when working in this repository.

## MVP-0 Scope

MVP-0 is limited to a deterministic discrete-event simulation framework skeleton for a future Low Earth Orbit satellite internet digital twin and communication-computing network simulator.

MVP-0 may include:

- Repository structure.
- Documentation.
- Placeholder configuration files.
- Test setup.
- Future framework interfaces only when introduced by a scoped issue.

MVP-0 must not include high-fidelity simulation models or external simulator integration.

## Forbidden Operations

Codex must not:

- Use or integrate STK.
- Use or integrate EXATA or GloMoSim.
- Use or integrate AFSIM.
- Use or integrate DDS runtime.
- Implement packet-level network simulation.
- Implement real orbital mechanics, SGP4, or high-precision astrodynamics.
- Implement real RF propagation or antenna models.
- Implement routing, networking, or compute algorithms unless a future issue explicitly allows a bounded placeholder.
- Implement multithreading or distributed execution.
- Add AI or machine learning components.
- Add visualization engines such as Cesium, Unity, or similar tools.
- Expand architecture beyond the current approved scope.

## No External Simulator Dependency

The project must not depend on external simulators during MVP-0. All MVP-0 behavior must remain local, deterministic, testable, and independent of STK, EXATA, GloMoSim, AFSIM, DDS runtime, visualization engines, or external simulation services.

## Git Workflow Rules

- One issue = one feature = one branch.
- Branch names must describe the current scoped issue.
- A commit must contain only changes related to the current issue.
- Do not mix unrelated documentation, architecture, feature, test, or cleanup work.
- Do not refactor unrelated code.
- Before committing, run the relevant tests.
- The main branch must remain a stable integration target.

## Module Dependency Rules

Allowed dependency direction:

```text
adapters -> services -> models -> core
schema may be used by adapters, services, models, and core
```

Rules:

- `core` must not import from `models`, `services`, or `adapters`.
- `models` must not import from `services` or `adapters`.
- `services` must not import from `adapters`.
- `adapters` must not be imported by lower layers.
- Shared structured definitions belong in `schema`.
- Simulation time must be controlled only by the future `SimulationKernel`.
- Core logic must not use global mutable state.

## Testing Requirements

- All functionality must be test-driven.
- Tests must be deterministic.
- Tests must not rely on wall-clock time, network access, random behavior without an explicit seed, or machine-specific state.
- MVP-0 initialization tests may only verify project structure and test runner setup.
- No simulation tests should be added before simulation behavior exists.

## Determinism Requirement

Given the same code, configuration, and seed, future simulation runs must produce equivalent results. Any use of randomness must be controlled by explicit configuration. Hidden global state and uncontrolled time sources are not allowed in core logic.
