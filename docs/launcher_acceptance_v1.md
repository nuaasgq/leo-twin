# Launcher One-Click Acceptance v1

Date: 2026-07-09
Branch: `feature/T426-launcher-health-acceptance-v1`

Launcher one-click acceptance v1 adds a machine-readable startup acceptance
summary to the existing launcher health surface. It does not change service
startup behavior, simulation runtime behavior, Event Kernel ordering, model
fidelity, packet abstraction, or any frontend architecture.

## Contract

The summary object is exposed as:

```text
one_click_acceptance_v1
```

with the acceptance id:

```text
leo_twin.launcher_one_click_acceptance.v1
```

Fields:

- `status`: `PASS`, `BLOCKED`, or `STOPPED`;
- `ready`: true only when startup acceptance passes;
- `required_service_count`: required launcher-managed service count;
- `ready_service_count`: number of services with `READY` readiness;
- `blocked_service_count`: number of required services not `READY`;
- `blocking_services`: deterministic service names that block acceptance;
- `smoke_command`: follow-up runtime smoke command;
- `next_action`: operator next action;
- `criteria`: stable pass criteria.

## Semantics

Acceptance is derived from the same service probes used by
`leo_twin.launcher_health.v2`:

- `PASS`: backend and frontend are both `READY`;
- `STOPPED`: backend and frontend are both `STOPPED`;
- `BLOCKED`: any mixed, port-only, or partially healthy state.

This contract is intentionally small. It gives users and automation a single
startup answer without asking them to inspect individual backend/frontend
fields, while preserving the detailed launcher health payload for diagnosis.
