# Selected Coverage Visual Policy v2

Date: 2026-07-06
Branch: `feature/T232-selected-coverage-visual-policy-v2`
Policy id: `leo_twin.selected_coverage_visual_policy.v2`

## Purpose

Selected coverage visual policy v2 productizes the existing selected-satellite
coverage display. It makes the footprint, honeycomb beam cells, and covered-user
counting semantics explicit for users and tests while keeping the implementation
visual-only.

This task does not change the Event Kernel, orbit model, network access model,
routing, compute behavior, RF propagation, antenna pattern, link budget, or
packet-level simulation.

## Source of Truth

The frontend policy is derived from backend `coverage_beam_summary` when that
summary exists. The local 3D layer switch controls visibility only. It does not
change backend semantics or simulation state.

Policy fields:

- `version`
- `policy_id`
- `selected_satellite_detail_mode`
- `coverage_model`
- `fidelity_level`
- `beam_pattern`
- `footprint_intersection_policy`
- `beam_cell_count`
- `beam_radius_m`
- `beam_length_m`
- `global_beam_render_limit`
- `local_layer_enabled`
- `excluded_physics`
- `visual_only`
- `no_access_semantics`

## Visual Model

- Detail mode: selected satellite only.
- Footprint model: deterministic geometric footprint.
- Beam pattern: center cell plus a bounded hexagonal neighbor ring.
- Default beam count: 7 cells.
- Default footprint radius: 160 km.
- Default beam length: 600 km.
- Global render limit: one selected-satellite coverage display.

The visual footprint and honeycomb cells are deterministic products of the
selected satellite state and backend coverage summary. They are intended for
operator inspection and UI explanation.

## Explicit Non-Claims

The coverage display excludes:

- RF propagation.
- Antenna pattern simulation.
- Link-budget calculation.
- Interference modeling.

Covered-user counting uses deterministic geometric containment for the selected
visual footprint. It is not an access decision and does not imply successful
communication service.

## Follow-Up

- Bind selected coverage cells to a richer satellite-detail side panel.
- Add screenshot regression for selected-satellite footprint and beam cells.
- Add backend cursor or detail endpoint if future large-scale coverage
  inspection needs per-beam user lists beyond the bounded UI summary.
