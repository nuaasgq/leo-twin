# Scale Policy v2

Date: 2026-07-06
Branch: `feature/T234-scale-policy-v2`
Policy id: `leo_twin.scale_policy.v2`

## Purpose

Scale policy v2 defines product-facing scale bands for LEO-Twin / SEES. It
turns scale behavior into a deterministic backend-owned contract instead of
leaving frontend surfaces to infer fidelity degradation from satellite count.

This task is a policy and explanation baseline. It does not modify the Event
Kernel, orbit propagation, network logic, compute behavior, runtime loop, or
frontend rendering architecture.

## Profile Targets

The policy defines six named targets:

- 72 satellites: `baseline_72`
- 300 satellites: `medium_300`
- 1200 satellites: `large_1200`
- 3000 satellites: `xl_3000`
- 6000 satellites: `xxl_6000`
- 12000 satellites: `extreme_12000`

Each profile records:

- orbit update mode;
- metrics mode;
- space-link mode;
- snapshot LOD policy;
- detail-window policy;
- frontend rendering policy;
- runtime guardrail policy;
- recommended use;
- limitation note.

## Active Policy Summary

`scale_policy_v2_to_dict()` returns:

- `version`
- `policy_id`
- `profile_targets`
- `active_profile_id`
- `active_scale_band`
- `active_profile`
- `active_fidelity_summary`
- `profiles`
- `frontend_notice_policy`
- `result_reproducibility_policy`
- `forbidden_integrations`
- `packet_level_simulation`
- `event_kernel_policy`

The active fidelity summary reuses the existing backend scale fidelity service,
so current runtime behavior remains consistent with established orbit, metrics,
and bounded space-link mode selection.

## Boundaries

The 3000, 6000, and 12000 profiles are product guardrail profiles. They are not
claims that full-detail interactive operation is already industrial-grade at
those scales. Their purpose is to make the required degradation and acceptance
rules explicit before deeper runtime and frontend LOD work.

Current excluded behavior remains:

- STK / EXATA / AFSIM / DDS integration;
- packet-level simulation;
- Event Kernel behavior changes;
- full-scene detail rendering for extreme scale;
- unbounded per-node frontend tables.

## Follow-Up

- V2-041: implement LOD snapshot policy using these profile names.
- V2-042: bind event, memory, backlog, and stream guardrails to the active
  profile.
- V2-043: add backend cursor/detail contracts for users, satellites, routes,
  services, and compute nodes.
