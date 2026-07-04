import { Color } from "cesium";
import { describe, expect, it } from "vitest";

import {
  OPAQUE_GLOBE_BASE_COLOR_HEX,
  applyOpaqueGlobeVisualPolicy,
  opaqueGlobeVisualPolicySummary
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
          backFaceAlpha: 0.2
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
    expect(scene.skyAtmosphere.show).toBe(true);
  });

  it("summarizes the visible earth policy for regression checks", () => {
    expect(opaqueGlobeVisualPolicySummary()).toEqual({
      background: "BLACK",
      baseColor: "#07141d",
      depthTestAgainstTerrain: true,
      groundAtmosphere: true,
      globeTranslucency: false
    });
  });
});
