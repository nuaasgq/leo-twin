import { Color } from "cesium";
import { describe, expect, it } from "vitest";

import {
  OPAQUE_GLOBE_BASE_COLOR_HEX,
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
