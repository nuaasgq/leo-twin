# Earth Visual Policy v2

Date: 2026-07-06
Branch: `feature/T231-earth-visual-policy-v2`
Policy id: `leo_twin.earth_visual_policy.v2`

## Purpose

Earth visual policy v2 makes the Cesium globe rendering assumptions explicit for
operators and regression tests. It is a frontend observation-layer policy only:
it does not change orbit, coverage, network, compute, metrics, runtime control,
or Event Kernel behavior.

## Default Policy

- Default mode: `OPAQUE`.
- Earth texture asset: `earth.texture.cesium.natural_earth_ii`, sourced from the
  3D asset manifest `leo_twin.3d_asset_manifest.v1`.
- Country boundary asset:
  `earth.boundaries.natural_earth_110m_admin_0`, sourced from the same manifest.
- Country borders are visible by default through the local 3D layer toggle.
- Far-side satellites and routes are depth-occluded by the globe in the default
  opaque mode.
- Day/night visualization remains disabled and reserved for a future visual-only
  task.

## Explicit Observation Mode

The existing `TRANSLUCENT` mode remains available as an explicit operator
observation mode. It is useful for inspecting spatial relationships through the
globe, but it is not the default product view. The layer summary reports this as
`透明观测 / v2` and marks far-side occlusion as disabled for observation.

## Deterministic Summary Fields

`earthVisualPolicyV2Summary()` returns:

- `version`
- `policy_id`
- `default_mode`
- `active_mode`
- `earth_texture_asset_id`
- `country_boundary_asset_id`
- `country_borders_visible`
- `far_side_occlusion`
- `satellite_depth_test_required`
- `country_label_depth_test_required`
- `day_night_mode`
- `asset_manifest_id`
- `visual_only`
- `no_simulation_semantics`

The 3D layer control summary consumes these fields instead of hardcoding local
business meaning in the UI. The summary intentionally stays visual-only and does
not claim RF, lighting, terrain, or high-fidelity Earth rendering accuracy.

## Follow-Up

- Add selected-satellite coverage visualization v2 with deterministic footprint
  and multi-beam display.
- Add screenshot regression checks for the default opaque globe and transparent
  observation mode.
- Replace or supplement NaturalEarthII only through the asset manifest source,
  license, SHA, and render acceptance gate.
