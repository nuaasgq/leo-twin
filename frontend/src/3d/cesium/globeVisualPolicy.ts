import { Color } from "cesium";

export const OPAQUE_GLOBE_BASE_COLOR_HEX = "#07141d";

export interface GlobeVisualPolicySummary {
  background: string;
  baseColor: string;
  depthTestAgainstTerrain: boolean;
  groundAtmosphere: boolean;
  globeTranslucency: boolean;
}

interface GlobeTranslucencyTarget {
  enabled: boolean;
  frontFaceAlpha?: number;
  backFaceAlpha?: number;
}

export interface GlobeVisualSceneTarget {
  backgroundColor: Color;
  globe: {
    baseColor: Color;
    depthTestAgainstTerrain: boolean;
    showGroundAtmosphere: boolean;
    translucency?: GlobeTranslucencyTarget;
  };
  skyAtmosphere?: {
    show: boolean;
  };
}

export function applyOpaqueGlobeVisualPolicy(scene: GlobeVisualSceneTarget): void {
  scene.backgroundColor = Color.BLACK;
  scene.globe.baseColor = Color.fromCssColorString(OPAQUE_GLOBE_BASE_COLOR_HEX);
  scene.globe.depthTestAgainstTerrain = true;
  scene.globe.showGroundAtmosphere = true;
  if (scene.globe.translucency) {
    scene.globe.translucency.enabled = false;
    scene.globe.translucency.frontFaceAlpha = 1;
    scene.globe.translucency.backFaceAlpha = 1;
  }
  if (scene.skyAtmosphere) {
    scene.skyAtmosphere.show = true;
  }
}

export function opaqueGlobeVisualPolicySummary(): GlobeVisualPolicySummary {
  return {
    background: "BLACK",
    baseColor: OPAQUE_GLOBE_BASE_COLOR_HEX,
    depthTestAgainstTerrain: true,
    groundAtmosphere: true,
    globeTranslucency: false
  };
}
