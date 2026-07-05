# Product Acceptance Scenarios

Date: 2026-07-05

These scenarios are deterministic SEES control-plane configurations for
product acceptance smoke tests. They are not local runtime output files.

## Scenario Matrix

| Scenario | Config | Satellites | Users | Compute nodes | Orbit mode | Metrics mode | Space link mode | Duration | Seed |
| --- | --- | ---: | ---: | ---: | --- | --- | --- | ---: | ---: |
| small_demo_72sat | `configs/acceptance/small_demo_72sat.yaml` | 72 | 1000 | 72 | `PER_SATELLITE` | `DETAILED` | `DETAILED_SMALL_SCALE` | 120 s | 20260705 |
| medium_demo_300sat | `configs/acceptance/medium_demo_300sat.yaml` | 300 | 2000 | 300 | `BATCH` | `DETAILED` | `BOUNDED_CANDIDATE` | 120 s | 20260705 |
| scale_demo_1200sat_short | `configs/acceptance/scale_demo_1200sat_short.yaml` | 1200 | 100 | 1200 | `BATCH` | `AGGREGATED` | `BOUNDED_CANDIDATE` | 120 s | 20260705 |

`metrics_mode` is reported by backend fidelity policy, not as an independent
loader field. The YAML comments and this table document the expected derived
mode.

## Traffic And Compute Semantics

All three scenarios use:

- Application protocol: `TASK_OFFLOAD_FLOW`
- Traffic class: backend-derived `COMPUTE_SERVICE`
- Traffic model: deterministic interval flow/task arrivals
- Compute service mix: satellite-hosted compute nodes
- Scheduling policy: `FIFO`
- Network abstraction: flow-level, not packet-level

## Acceptance Checks

The integration acceptance test verifies:

- The scenario YAML loads through the SEES config loader.
- Runtime `INITIALIZE` succeeds.
- Runtime can start and advance a short live tick.
- Runtime status and generated backend summary exist.
- Runtime health smoke can read backend `/runtime/status`, frontend console,
  and frontend dashboard without mutating configuration.
- State stream contains satellites.
- Fidelity summary exists and reports the expected scale mode.
- Pause, stop, and reset remain controllable.
- Derived constellation summary is deterministic for the same config.
- Communication-compute service metrics expose component latency summary and
  bounded per-service `component_timeline` rows.
- The dashboard renders service latency components, per-service trace rows, and
  visible component timeline chips from backend-provided runtime status fields.
- The Event Kernel remains free of domain-specific batch orbit logic.

Local read-only health smoke:

```powershell
.\scripts\smoke_runtime_health.ps1
```

Frontend visual/dashboard verification:

```powershell
.\scripts\verify_frontend_visuals.ps1
```

Aggregate product acceptance verification:

```powershell
.\scripts\verify_product_acceptance.ps1
```

## Limitations

- These scenarios are smoke/acceptance inputs, not high-fidelity orbital or RF
  validation cases.
- `scale_demo_1200sat_short` intentionally uses scale-mode batching and bounded
  ISL candidates to preserve interactivity.
- Metrics and snapshots can still dominate the first large-scale tick; use
  runtime backpressure profiling for follow-up performance work.
