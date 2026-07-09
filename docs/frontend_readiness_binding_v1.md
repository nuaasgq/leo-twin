# Frontend Readiness Binding v1

Date: 2026-07-09

## Scope

This task binds the data dashboard to two backend-owned runtime status
summaries:

- `v2_executable_readiness_v1`
- `traffic_business_activity_window_v1`

The frontend does not infer these business semantics locally. It renders the
backend source label, status, counts, and bounded sample rows when the fields
are present, and remains backward-compatible when they are absent.

## Data Panel Behavior

`v2_executable_readiness_v1` is displayed in two places:

- the top runtime summary strip, showing whether the v2 executable loop is
  ready;
- a readiness card, showing backend source, operator next action, gate count,
  failed count, frontend-inference boundary, packet-level boundary, and failed
  gate details when present.

`traffic_business_activity_window_v1` is displayed in the dynamic situation
area:

- active user count;
- pending user count;
- recent, idle, hidden, lookback, and lookahead window metadata;
- bounded user samples with state, traffic class, target, next-arrival timing,
  and active/pending request counts.

## Compatibility

The binding is optional and additive. Existing runtime status payloads without
these fields render as before.

No backend protocol route, Event Kernel behavior, simulation model formula,
runtime progression, or result export behavior is changed by this task.

## Validation

- `pnpm --dir frontend test`: 27 test files passed, 477 tests passed.
- `pnpm --dir frontend build`: passed.

The build reports the existing Vite chunk-size warning for the data panel bundle.
No new build failure is introduced.
