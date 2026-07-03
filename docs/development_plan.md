# Development Plan

This document defines the planned MVP-0 development sequence. It is a roadmap only and does not implement simulation behavior.

## MVP-0 Phases

1. Project initialization and documentation.
2. Deterministic event kernel foundation.
3. Configuration schema and loading boundaries.
4. Placeholder domain state schemas.
5. Minimal deterministic scenario execution.
6. Metrics recording foundation.
7. Demo scenario assembly.

Each phase must be delivered through a scoped issue, a dedicated branch, and tests that match the feature being introduced.

## Twelve-Step Roadmap

1. Initialize project structure, documentation, placeholder configs, and pytest setup.
2. Define the event object contract and deterministic ordering requirements.
3. Implement the minimal event kernel with simulation time controlled only by `SimulationKernel`.
4. Add configuration schema boundaries and deterministic seed handling.
5. Add placeholder orbit state representation without real orbital mechanics.
6. Add placeholder coverage state representation without RF or antenna modeling.
7. Add logical link state representation without packet-level networking.
8. Add routing service boundaries without real routing algorithms.
9. Add compute node and task state representation without scheduling algorithms.
10. Add metrics record schema and deterministic output contracts.
11. Add integration tests for a minimal deterministic scenario.
12. Add a CLI-driven demo runner after kernel, state, metrics, and configuration contracts exist.

## Scope Control

The roadmap is intentionally staged. A future step must not be implemented early. Every step must preserve the MVP-0 constraints unless a later approved phase explicitly changes the project scope.
