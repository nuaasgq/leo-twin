# Completion Notice Dismissal v1

Date: 2026-07-06
Branch: `feature/T249-completion-notice-refresh-v1`

## Goal

Fix the UI bug where the simulation-completed notice can reappear after the
user refreshes the page. A dismissed completion notice should stay dismissed
for the same completed runtime state during the current browser session.

## Behavior

The frontend now stores the dismissed completion notice key in
`sessionStorage`. The key is still derived from backend runtime status:

- config version
- configured duration
- current simulation time
- processed event count

When the user dismisses the completed-runtime notice, the key is written to
session storage. When the App is reloaded, it initializes the in-memory
dismissed key from the same storage location.

When a new runtime becomes active (`RUNNING` or `PAUSED`), the stored key is
cleared so a future completed run can show its own completion notice.

## Boundaries

- No backend changes.
- No Event Kernel changes.
- No runtime status protocol changes.
- No dashboard layout changes.
- The preference is scoped to the current browser session only.

## Failure Handling

If browser storage is unavailable or throws, the App falls back to the existing
in-memory dismissal behavior and does not crash.
