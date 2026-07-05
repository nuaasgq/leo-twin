# Backpressure Notice Dismissal v1

Date: 2026-07-06
Branch: `feature/T250-backpressure-notice-dismissal-v1`

## Goal

Make the runtime backpressure notice behave like an operator-controlled UI
notice. If the user closes the current pressure warning and refreshes the page,
the same warning should not immediately reappear during the same browser
session.

## Behavior

The frontend stores the dismissed pressure notice key in `sessionStorage`.
The key is derived from the backend pressure summary fields that define the
stable warning identity:

- overloaded flag
- first-tick-heavy flag
- bottleneck component
- recommended action

Volatile tick samples such as tick duration, queue depth, and processed event
count do not change the dismissal key. A different bottleneck or recommended
action produces a different key and can show a new warning.

When the backend no longer reports a visible pressure warning, the stored
pressure dismissal key is cleared. If browser storage is unavailable, the App
falls back to the existing in-memory close behavior.

## Boundaries

- No backend changes.
- No Event Kernel changes.
- No runtime status protocol changes.
- No dashboard layout changes.
- No model or simulation semantics changed.

## Verification

- Unit coverage checks pressure notice key stability.
- Unit coverage checks session storage read/write/clear behavior.
- Unit coverage checks storage failures are non-fatal.
