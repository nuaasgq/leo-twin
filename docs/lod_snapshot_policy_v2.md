# LOD Snapshot Policy v2

Date: 2026-07-06
Branch: `feature/T235-lod-snapshot-policy-v2`
Policy id: `leo_twin.lod_snapshot_policy.v2`

## Purpose

LOD snapshot policy v2 defines how large runtime snapshots should expose
detail windows, Top-K summaries, sampled histories, and raw counts across the
scale bands defined by `leo_twin.scale_policy.v2`.

This task creates a backend-owned contract. It does not change the Event Kernel,
runtime session advancement, existing snapshot publication, or frontend
rendering architecture.

## Source Policy

The policy is derived from:

- configured `satellite_count`;
- configured `user_count`;
- active `scale_policy_v2` profile.

It is returned in `backend_summary.lod_snapshot_policy_v2` next to
`backend_summary.scale_policy_v2`.

## Policy Surfaces

The policy includes:

- `raw_count_policy`: raw counts that must remain visible even when detail rows
  are windowed.
- `detail_windows`: bounded row windows for satellites, ground users, routes,
  services, and compute nodes.
- `top_k_summaries`: bounded ranked summaries for constraints, compute
  hotspots, active services, and route bottlenecks.
- `sampled_histories`: deterministic tail samples for KPI, service latency,
  satellite resource, and selected node history.
- `cursor_required`: whether hidden rows require a backend cursor or explicit
  detail request.
- `hidden_detail_policy`: user-facing explanation for rows outside the active
  windows.

## Scale Behavior

- `baseline_72`: small-scale windows may include full detail when counts fit.
- `medium_300`: details are windowed, but backend cursor is not required yet.
- `large_1200`: hidden rows require backend cursor or explicit detail request.
- `xl_3000`: aggregate-first with smaller detail windows.
- `xxl_6000`: aggregate-only by default with explicit detail requests.
- `extreme_12000`: summary/export-first; full-scene detail is not a current
  product claim.

## Determinism

The policy requires:

- stable ordering by backend identifiers before windowing;
- fixed-size tail samples for histories;
- frontend may render, paginate, and format values, but must not invent LOD
  semantics.

## Follow-Up

- V2-042: enforce runtime guardrails for event volume, memory, stream backlog,
  and refusal/degrade reasons.
- V2-043: implement backend cursor/detail contracts for large collections.
- Dashboard v3 should display raw counts and hidden-row explanations from this
  backend-owned policy.
