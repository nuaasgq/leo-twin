# Architecture

## MVP-0 Scope

MVP-0 establishes the repository structure and the engineering rules for a future deterministic discrete-event simulation framework. It does not implement simulator behavior.

The only allowed output of MVP-0 is:

- Project structure.
- Architecture documentation.
- Data entity documentation.
- Development plan documentation.
- Placeholder configuration files.
- Pytest setup with structure-only checks.

## Explicitly Excluded From MVP-0

MVP-0 must not include:

- STK integration.
- EXATA or GloMoSim integration.
- AFSIM integration.
- DDS runtime integration.
- Packet-level network simulation.
- Real orbital mechanics, including SGP4 or high-precision astrodynamics.
- Real RF propagation or antenna models.
- Routing, networking, or link algorithms.
- Compute, scheduling, or task-offloading algorithms.
- Multithreading or distributed execution.
- AI or machine learning components.
- Visualization engines such as Cesium or Unity.

## Four-Layer Architecture

The project is organized into four implementation layers. Each layer has a narrow responsibility and must respect the dependency rules below.

### Core

The `core` layer will contain the deterministic simulation foundation. In future MVP-0 steps, it is the only layer allowed to control simulation time through the `SimulationKernel`.

Future core responsibilities may include:

- Simulation time ownership.
- Event scheduling contracts.
- Deterministic event ordering.
- Kernel lifecycle boundaries.

The core layer must not contain domain-specific satellite, network, compute, or visualization logic.

### Models

The `models` layer will contain domain state containers and simple domain abstractions. In MVP-0, model content is documentation-only.

Future model responsibilities may include:

- Satellite, user, beam, link, flow, compute node, task, event, and metric state definitions.
- Configuration-driven parameters.
- Deterministic state representation.

The models layer must not own simulation time, perform event dispatch, or call adapters.

### Services

The `services` layer will contain orchestration logic that coordinates models through the core simulation framework. In MVP-0, no services are implemented.

Future service responsibilities may include:

- Scenario assembly.
- Simulation run orchestration.
- Metrics collection orchestration.
- Coordination between independent model components.

Services must not bypass the core layer to mutate simulation time.

### Adapters

The `adapters` layer will contain boundary code for files, configuration loading, command-line entry points, and later external-facing integrations that remain inside the allowed project scope.

Adapters may depend on services, models, and schema definitions. Adapters must not contain simulation algorithms.

## Discrete Event System Principle

The future simulator will follow a Discrete Event System principle:

- Simulation state changes only when an event is processed.
- Simulation time advances only through the future `SimulationKernel`.
- Events must be ordered deterministically.
- Equivalent configuration and seed values must produce equivalent results.
- Parameters must come from explicit configuration, not hidden global state.

MVP-0 only documents this principle. It does not implement the event kernel.

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
- Cross-module changes are not allowed unless the current issue explicitly requires them.
- Refactoring beyond the current issue scope is not allowed.
