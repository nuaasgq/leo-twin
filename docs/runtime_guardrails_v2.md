# Runtime Guardrails v2

Date: 2026-07-06
Branch: `feature/T236-runtime-guardrails-v2`
Policy id: `leo_twin.runtime_guardrails.v2`

## Purpose

Runtime guardrails v2 turns pre-run execution safety into a deterministic
backend-owned summary. It estimates event volume, memory use, and stream backlog
before a scenario starts, then classifies the run as `ALLOW`, `DEGRADE`, or
`REFUSE`.

This task adds a policy and explanation contract. It does not modify the Event
Kernel, session advancement loop, stream buffer implementation, orbit model,
network model, compute model, or frontend rendering architecture.

## Source Policies

The guardrail summary is derived from:

- configured satellite, user, and compute-node counts;
- runtime duration and tick interval;
- `leo_twin.scale_policy.v2`;
- `leo_twin.lod_snapshot_policy.v2`;
- existing `ScaleSafetyChecker` estimates.

It is returned in `backend_summary.runtime_guardrails_v2` next to
`scale_policy_v2` and `lod_snapshot_policy_v2`.

## Summary Fields

`runtime_guardrails_v2_to_dict()` returns:

- `version`
- `guardrail_id`
- `source_policy_ids`
- `active_profile_id`
- `active_scale_band`
- `configured_counts`
- `runtime_config`
- `limits`
- `estimates`
- `scale_safety_report`
- `decision`
- `degrade_reasons`
- `refusal_reasons`
- `runtime_actions`
- `event_kernel_policy`

The `estimates` field includes:

- event volume;
- memory bytes;
- interactions per tick;
- queue depth;
- computation per tick;
- event/state stream backlog risk;
- whether cursor reads are required to avoid hidden dropped items.

## Decision Semantics

- `ALLOW`: current estimates fit the configured guardrail limits and no active
  profile requires a degrade notice.
- `DEGRADE`: execution is allowed, but the frontend and result package should
  show explicit fidelity, LOD, or cursor-read notices.
- `REFUSE`: execution should be blocked until configured violations are fixed.

`REFUSE` is currently driven by the existing scale safety violations such as
event count or memory estimate exceeding configured limits.

## Boundaries

This policy does not claim that all large-scale scenarios are fully detailed or
industrially validated. It only makes runtime safety and degradation explicit.

Current excluded behavior remains:

- Event Kernel behavior changes;
- packet-level simulation;
- STK / EXATA / AFSIM / DDS integration;
- distributed execution;
- unbounded frontend tables;
- implicit frontend inference of runtime safety.

## Follow-Up

- V2-043: add backend cursor/detail contracts for large users, satellites,
  routes, services, and compute nodes.
- Later runtime work should apply this guardrail decision to start-time control
  paths and result package metadata.
- Dashboard v3 should render `decision`, `degrade_reasons`, and
  `refusal_reasons` from this backend-owned summary.
