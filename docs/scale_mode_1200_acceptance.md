# 1200-Satellite Scale Mode Acceptance

Date: 2026-07-04

Branch: `feature/T163-frontend-dashboard-compute-v2`

## Scope

This report defines what the current 1200-satellite live demo mode means after
Scale Firebreak v1, 1200 Node Live Control Stabilization, Scale Fidelity Notice
v1, and Scale Mode Productization v1.

This is a deterministic, single-process, event-driven scale mode. It is not
distributed execution, packet-level simulation, or a full high-fidelity ISL
simulator.

## What Scale Firebreak v1 Fixed

- Large constellations no longer emit one `ORBIT_UPDATE` per satellite per
  target by default.
- For `satellite_count >= 300`, orbit updates default to `ORBIT_BATCH_UPDATE`.
- Metrics can consume orbit batch summaries directly.
- The Event Kernel remains unchanged and contains no orbit-domain batch logic.

Event-volume logic:

```text
per_satellite_estimate = satellite_count * update_target_count * orbit_tick_count
batch_estimate = update_target_count * orbit_tick_count
```

For a 1200-satellite, 2-target, 3-tick run:

```text
before = 1200 * 2 * 3 = 7200 orbit update events
after  = 2 * 3 = 6 orbit batch update events
reduction = 1200x
```

## What 1200 Node Live Control Stabilization Fixed

- `SimulationSession` remains the runtime core.
- `SessionAdvanceLoop` owns live backend advancement.
- Control commands (`START`, `PAUSE`, `STOP`, `RESET`) no longer drain the
  entire simulation through `run_until_idle()` on live paths.
- Visible snapshots are available after initialization, including the initial
  1200 satellites.
- Stream buffers remain cursor based.

## Current Orbit Update Strategy

- Small scale can use `PER_SATELLITE`.
- 1200-satellite mode uses `BATCH`.
- The runtime status, generated backend summary, and state stream include
  `fidelity_summary.orbit_update_mode`.

## Current Metrics Strategy

- 1200-satellite mode uses `AGGREGATED` metrics.
- Metrics ingest `ORBIT_BATCH_UPDATE` without subscribing to the per-satellite
  orbit event flood.
- The fidelity summary exposes `metrics_mode`.

## Current ISL Strategy

1200-satellite mode now uses `BOUNDED_CANDIDATE` instead of silently skipping
space-space link updates.

Current candidate policy:

- Same-plane nearest neighbors.
- Adjacent-plane coarse candidates.
- Deterministic ring fallback.
- Hard cap: `max_space_link_candidates_per_satellite` (default `4`).
- Detailed all-pairs ISL remains unavailable for large batches by default.

The following fields are reported by backend fidelity summary:

- `satellite_count`
- `user_count`
- `orbit_update_mode`
- `metrics_mode`
- `space_link_mode`
- `detailed_space_link_enabled`
- `space_link_candidate_policy`
- `max_space_link_candidates_per_satellite`
- `batch_space_link_update_limit`
- `scale_limit_reason`
- `current_scale_mode`
- `fidelity_warnings`

## 1200 Live Control Smoke

Local control-plane smoke using the live initialization path:

- `INITIALIZE`: ok, 1200 satellites.
- `START`: status `RUNNING`.
- One explicit advance-loop tick completed.
- `PAUSE`: status `PAUSED`.
- `STOP`: status `STOPPED`.
- `RESET`: initialized flag cleared and visible satellites reset to `0`.
- Fidelity summary reported:
  - `orbit_update_mode=BATCH`
  - `metrics_mode=AGGREGATED`
  - `space_link_mode=BOUNDED_CANDIDATE`
  - `max_space_link_candidates_per_satellite=4`
  - `batch_space_link_update_limit=999`

Observed local timings:

- `INITIALIZE`: 51.76 ms.
- First `START` plus one explicit tick: 16164.06 ms.
- `PAUSE`: 0.27 ms.
- `STOP`: 10.92 ms.
- `RESET`: 127.94 ms.

The first tick is still heavy because the current 1200-node scenario also
creates 1200 compute nodes and a large same-time flow/task burst. That work is
outside this scale-fidelity task and should be handled by a later
traffic/compute batching or admission-control task.

## Known Fidelity Limitations

- Bounded ISL candidates are an approximation, not a high-fidelity optical/RF
  inter-satellite link model.
- The bounded candidate policy does not compute all satellite pairs.
- Link budgets remain deterministic simplified abstractions.
- The frontend consumes snapshots and fidelity summaries; it does not consume
  raw orbit or ISL event streams.
- Large first-tick flow/task bursts can still dominate wall-clock time even
  when orbit and ISL update volume is bounded.

## Recommended Next Scale Task

Implement a separate **1200-node traffic/compute first-tick smoothing** task:

- batch or stagger initial flow/task arrivals deterministically;
- report admission/backpressure state through runtime status;
- keep satellite-as-compute-node semantics;
- preserve Event Kernel behavior and live stream cursor contracts.
