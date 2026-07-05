import { Color } from "cesium";
import { describe, expect, it } from "vitest";

import {
  OPAQUE_GLOBE_BASE_COLOR_HEX,
  earthVisualPolicyV2LayerSummary,
  earthVisualPolicyV2Summary,
  applyOpaqueGlobeVisualPolicy,
  applyTranslucentGlobeVisualPolicy,
  opaqueGlobeVisualPolicySummary,
  translucentGlobeVisualPolicySummary,
  TRANSLUCENT_GLOBE_BACK_ALPHA,
  TRANSLUCENT_GLOBE_BASE_COLOR_HEX,
  TRANSLUCENT_GLOBE_FRONT_ALPHA
} from "../src/3d/cesium/globeVisualPolicy";

describe("opaque globe visual policy", () => {
  it("locks the Cesium globe to an opaque depth-tested visual policy", () => {
    const scene = {
      backgroundColor: Color.TRANSPARENT,
      globe: {
        baseColor: Color.TRANSPARENT,
        depthTestAgainstTerrain: false,
        showGroundAtmosphere: false,
        translucency: {
          enabled: true,
          frontFaceAlpha: 0.5,
          backFaceAlpha: 0.2,
          frontFaceAlphaByDistance: { near: 0, far: 1 },
          backFaceAlphaByDistance: { near: 0, far: 1 }
        }
      },
      skyAtmosphere: {
        show: false
      }
    };

    applyOpaqueGlobeVisualPolicy(scene);

    expect(scene.backgroundColor).toBe(Color.BLACK);
    expect(scene.globe.baseColor.toCssColorString()).toBe(
      Color.fromCssColorString(OPAQUE_GLOBE_BASE_COLOR_HEX).toCssColorString()
    );
    expect(scene.globe.depthTestAgainstTerrain).toBe(true);
    expect(scene.globe.showGroundAtmosphere).toBe(true);
    expect(scene.globe.translucency.enabled).toBe(false);
    expect(scene.globe.translucency.frontFaceAlpha).toBe(1);
    expect(scene.globe.translucency.backFaceAlpha).toBe(1);
    expect(scene.globe.translucency.frontFaceAlphaByDistance).toBeUndefined();
    expect(scene.globe.translucency.backFaceAlphaByDistance).toBeUndefined();
    expect(scene.skyAtmosphere.show).toBe(true);
  });

  it("summarizes the visible earth policy for regression checks", () => {
    expect(opaqueGlobeVisualPolicySummary()).toEqual({
      mode: "OPAQUE",
      background: "BLACK",
      baseColor: "#07141d",
      depthTestAgainstTerrain: true,
      groundAtmosphere: true,
      globeTranslucency: false
    });
  });

  it("supports an explicit translucent observation policy without changing the default", () => {
    const scene = {
      backgroundColor: Color.TRANSPARENT,
      globe: {
        baseColor: Color.TRANSPARENT,
        depthTestAgainstTerrain: true,
        showGroundAtmosphere: false,
        translucency: {
          enabled: false,
          frontFaceAlpha: 1,
          backFaceAlpha: 1
        }
      },
      skyAtmosphere: {
        show: false
      }
    };

    applyTranslucentGlobeVisualPolicy(scene);

    expect(scene.backgroundColor).toBe(Color.BLACK);
    expect(scene.globe.baseColor.toCssColorString()).toBe(
      Color.fromCssColorString(TRANSLUCENT_GLOBE_BASE_COLOR_HEX).toCssColorString()
    );
    expect(scene.globe.depthTestAgainstTerrain).toBe(false);
    expect(scene.globe.showGroundAtmosphere).toBe(true);
    expect(scene.globe.translucency.enabled).toBe(true);
    expect(scene.globe.translucency.frontFaceAlpha).toBe(TRANSLUCENT_GLOBE_FRONT_ALPHA);
    expect(scene.globe.translucency.backFaceAlpha).toBe(TRANSLUCENT_GLOBE_BACK_ALPHA);
    expect(scene.skyAtmosphere.show).toBe(true);
    expect(translucentGlobeVisualPolicySummary()).toEqual({
      mode: "TRANSLUCENT",
      background: "BLACK",
      baseColor: "#0b2a39",
      depthTestAgainstTerrain: false,
      groundAtmosphere: true,
      globeTranslucency: true,
      frontFaceAlpha: 0.38,
      backFaceAlpha: 0.18
    });
  });
});

describe("earth visual policy v2", () => {
  it("summarizes the opaque default using the scene asset manifest", () => {
    expect(earthVisualPolicyV2Summary()).toEqual({
      version: "v2",
      policy_id: "leo_twin.earth_visual_policy.v2",
      default_mode: "OPAQUE",
      active_mode: "OPAQUE",
      earth_texture_asset_id: "earth.texture.cesium.natural_earth_ii",
      country_boundary_asset_id: "earth.boundaries.natural_earth_110m_admin_0",
      country_borders_visible: true,
      far_side_occlusion: "ENABLED",
      satellite_depth_test_required: true,
      country_label_depth_test_required: true,
      day_night_mode: "DISABLED_OPTIONAL_FUTURE",
      asset_manifest_id: "leo_twin.3d_asset_manifest.v1",
      visual_only: true,
      no_simulation_semantics: true
    });
    expect(earthVisualPolicyV2LayerSummary()).toEqual({
      label: "地球",
      value: "不透明 / v2",
      detail: "NaturalEarthII / 国界显示 / 背面遮挡开启 / 日夜关闭"
    });
  });

  it("reports translucent observation as an explicit non-default visual mode", () => {
    expect(earthVisualPolicyV2Summary("TRANSLUCENT", false)).toMatchObject({
      default_mode: "OPAQUE",
      active_mode: "TRANSLUCENT",
      country_borders_visible: false,
      far_side_occlusion: "DISABLED_FOR_TRANSLUCENT_OBSERVATION",
      satellite_depth_test_required: false,
      country_label_depth_test_required: false,
      visual_only: true,
      no_simulation_semantics: true
    });
    expect(earthVisualPolicyV2LayerSummary("TRANSLUCENT", false)).toEqual({
      label: "地球",
      value: "透明观测 / v2",
      detail: "NaturalEarthII / 国界隐藏 / 背面遮挡关闭 / 日夜关闭"
    });
  });
});
