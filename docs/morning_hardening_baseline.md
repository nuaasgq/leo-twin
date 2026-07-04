# Morning Product Hardening Baseline

Date: 2026-07-05

Branch: `feature/T163-frontend-dashboard-compute-v2`

Baseline commit: `5a32b02 feat(runtime): smooth scale workload backpressure`

## Scope

This baseline records the system health before starting the next product
hardening phases. No product logic was changed for this phase.

## Tests Run

### Backend Targeted

Command:

```powershell
python -m pytest tests/integration/test_live_runtime_streaming.py tests/integration/test_runtime_session_control.py tests/integration/test_orbit_batch_scale.py tests/unit/test_position_driven_network_engine.py tests/unit/test_metrics_module.py tests/unit/test_backend_derived_summary.py -q
```

Result: passed, 60 tests.

### Frontend

Command:

```powershell
pnpm --dir frontend test
```

Result: passed, 22 files / 84 tests.

Command:

```powershell
pnpm --dir frontend build
```

Result: passed.

## Smoke Test

The smoke test used the integration demo control plane with local temporary
config output paths, so it did not alter the repository runtime config files.

### 72 Satellites

- Initialize: 6.60 ms
- Start: 0.70 ms
- Explicit tick: 15.92 ms
- Tick events: 423
- Pause: 0.31 ms
- Stop: 10.19 ms
- Reset: 2.35 ms
- State stream contained satellites.
- Fidelity summary existed.
- Fidelity mode: `SMALL_SCALE_DETAILED`
- Orbit update mode: `PER_SATELLITE`
- Space link mode: `DETAILED_SMALL_SCALE`

### 1200 Satellites / 1200 Compute Nodes

- Initialize: 53.15 ms
- Start: 0.41 ms
- Explicit tick from full START path: 2169.18 ms
- Tick events: 4073
- Pause: 0.25 ms
- Stop: 10.91 ms
- Reset: 67.02 ms
- State stream contained satellites.
- Fidelity summary existed.
- Fidelity mode: `LARGE_SCALE_AGGREGATED`
- Orbit update mode: `BATCH`
- Space link mode: `BOUNDED_CANDIDATE`

An isolated explicit first tick without starting the background loop completed
in 1466.91 ms and processed 4073 events.

## Runtime Profiling Observation

For the isolated 1200-satellite explicit first tick:

- `tick_duration_ms`: 1466.881
- `tick_budget_ms`: 1000.0
- `processed_event_count`: 4073
- `queue_depth`: 4802
- `overloaded`: true
- `first_tick_heavy`: true
- `bottleneck_component`: `metrics_aggregation`
- `recommended_action`: `keep_scale_mode_enabled_or_reduce_scenario_scale`

Measured component times:

- `orbit_batch_update_time_ms`: 8.7621
- `network_batch_ingestion_time_ms`: 103.416
- `access_update_time_ms`: 65.2332
- `space_space_candidate_update_time_ms`: 32.3496
- `metrics_aggregation_time_ms`: 801.609
- `snapshot_projection_time_ms`: 539.0032
- `total_tick_time_ms`: 1466.881

## Current Bottleneck

The current main bottleneck is not orbit batching or bounded ISL candidate
selection. The first scale tick is dominated by metrics aggregation and
snapshot projection.

## 1200 Runtime Responsiveness

The 1200-satellite runtime is still controllable:

- `INITIALIZE`, `START`, `PAUSE`, `STOP`, and `RESET` all completed.
- State stream snapshots included satellites and fidelity summary.
- Pause/stop/reset remained sub-100 ms in the smoke run after the explicit tick
  returned.

## Known Local Workspace State

The active workspace still has two local runtime/generated config modifications:

- `configs/generated_full_system_demo.json`
- `configs/sees_control.yaml`

They are excluded from this baseline phase and must not be committed unless a
future task explicitly makes them product fixtures.

## Phase Readiness

- Phase 1 requirements are already present in commit `5a32b02`.
- Phase 2 requirements are already present in commit `73fab2b`.
- The best next hardening target is scale-mode metrics/snapshot aggregation,
  because profiling shows those components dominate the remaining first-tick
  cost.
