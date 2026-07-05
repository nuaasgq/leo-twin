# 3D Scene Asset Manifest v1

## Purpose

3D asset manifest v1 records the visual assets used by the Cesium control
surface. It is a product delivery and license-traceability artifact, not a
simulation model.

Manifest id:

```text
leo_twin.3d_asset_manifest.v1
```

Frontend source:

```text
frontend/src/3d/assets/assetManifest.ts
```

## Current Assets

The manifest covers:

- Cesium bundled `NaturalEarthII` Earth texture tile map.
- Bundled Natural Earth 1:110m Admin 0 country boundary GeoJSON.
- Bundled NASA Satellite Kit GLB parts:
  - body
  - wings
  - radio
- Project-generated inline satellite SVG icon.

Local bundled files with stable SHA-256:

| Asset | SHA-256 |
| --- | --- |
| `frontend/public/assets/nasa-satellite-kit/satellite-kit-body-2.glb` | `175936434483f7b4d83d47fb36f8a2f900bea68b5ec231aa9ca84967432475b7` |
| `frontend/public/assets/nasa-satellite-kit/satellite-kit-wings-2.glb` | `b4b6d84ad0356a83dcbe640fda5a1c603c024e84591a65f650f662d3ef34bed1` |
| `frontend/public/assets/nasa-satellite-kit/satellite-kit-radio-1.glb` | `9b09e045fa455de38338748d66d12bee6a5d604427f33144cc39e8ff212b73d9` |
| `frontend/public/assets/natural-earth/ne_110m_admin_0_countries.geojson` | `6866c877d39cba9c357620878839b336d569f8c662d3cfab4cb1dbe2d39c977f` |

## Policy

- Assets are visual-only and do not affect Event Kernel behavior.
- Runtime loading is deterministic and uses bundled or package-managed assets.
- The frontend does not perform external runtime asset fetches.
- Replacement assets must include source URL, license note, local file path,
  SHA-256, and visual regression coverage before becoming defaults.
- No STK, EXATA, AFSIM, or DDS integration is introduced.

## Frontend Surface

The Cesium local layer summary now includes an `资产` row that reports the
manifest version, total asset count, and SHA-verified asset count. This makes
the active visual asset set visible to users without changing scene behavior.

## Follow-Up

- V2-061 should use the manifest to formalize the opaque Earth texture policy
  and country border rendering behavior.
- A future asset task can add a higher-resolution Earth texture after license
  review and screenshot regression.
- A future satellite model task can replace or supplement the NASA Satellite
  Kit model with a product-grade GLB while preserving hash and license checks.
