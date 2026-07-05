# Dashboard Detail Window Policy v1

## Purpose

Detail window policy v1 makes the standalone dashboard's large user and
satellite tables explicit and testable. The dashboard already pages detail
rows; this policy exposes the active render budget so users can see that large
scenarios are not rendered as one giant DOM table.

The policy is frontend-side observability only. It does not change simulation
behavior or backend runtime state.

## Current Policy

- User detail table page size: 80 rows.
- Satellite resource table page size: 120 rows.
- Combined active render budget: 200 rows.
- The dashboard renders only the current user page and current satellite page.
- Hidden rows remain reachable through the existing previous/next page
  controls and backend cursor summaries where available.

## Display Fields

The dashboard now emits a `表格窗口化` note in the detail observability section:

- rendered rows / total rows
- current user table window
- current satellite table window
- configured render budget
- hidden rows waiting for pagination when the filter result exceeds the active
  windows

## Model Boundary

- This is a UI stability policy, not a new model.
- It does not modify Event Kernel behavior.
- It does not introduce packet-level network simulation.
- It does not compute additional satellite links or task queues.
- It does not replace future backend paging or true virtual scrolling.

## Follow-Up

- Add backend cursor APIs for full user and satellite detail windows where
  frontend fallback rows become too large.
- Add table virtualization when the dashboard needs continuous scroll rather
  than page controls.
- Split the large DataPanel bundle after the dashboard information architecture
  stabilizes.
