# Satellite Camera Detail Policy v2

Date: 2026-07-06
Branch: `feature/T233-satellite-camera-detail-policy-v2`
Policy id: `leo_twin.satellite_camera_detail_policy.v2`

## Purpose

Satellite camera/detail policy v2 formalizes the 3D selected-satellite
inspection behavior. It describes how the control surface switches between Earth
overview and satellite follow mode, when the local inset is shown, how the
motion trail is bounded, and whether coverage/resource overlays are available.

This is a frontend observation-layer policy. It does not change orbit,
coverage, network, compute, metrics, runtime control, or Event Kernel behavior.

## Modes

- Default camera mode: `EARTH`.
- Follow camera mode: `SATELLITE`, available only when the current snapshot has
  selectable satellites.
- Target selection policy:
  `EXPLICIT_SELECTION_OR_FIRST_SNAPSHOT_SATELLITE`.
- Camera follow policy: `CESIUM_LOOK_AT_SELECTED_SATELLITE`.

If follow mode is requested while no satellite is selectable, the policy summary
falls back to `EARTH` and disables the inset.

## Detail Surface

When follow mode is active and a target satellite is selected, the 3D control
surface shows:

- selected satellite id;
- local inset scene;
- bounded local motion trail;
- selected-satellite coverage summary;
- covered-user visual containment summary;
- selected-satellite compute resource overlay when the compute node is present.

The default local trail window is 28 points. The trail resets when the selected
satellite changes, which keeps the local view deterministic and prevents stale
motion traces.

## Deterministic Summary Fields

`satelliteCameraDetailPolicyV2Summary()` returns:

- `version`
- `policy_id`
- `default_camera_mode`
- `active_camera_mode`
- `follow_available`
- `selected_satellite_id`
- `selectable_satellite_count`
- `target_selection_policy`
- `camera_follow_policy`
- `inset_enabled`
- `local_motion_trail_enabled`
- `trail_point_count`
- `max_trail_points`
- `coverage_overlay_enabled`
- `resource_overlay_enabled`
- `visual_only`
- `no_simulation_semantics`

The 3D control summary displays this as the `跟随` row so users can see whether
the active view is Earth overview or satellite follow mode.

## Follow-Up

- Add screenshot regression for the follow camera and inset surface.
- Add a richer selected-satellite detail drawer that reuses backend node detail
  records once large-scale cursor/detail APIs are available.
- Add explicit camera transition diagnostics if Cesium camera operations fail.
