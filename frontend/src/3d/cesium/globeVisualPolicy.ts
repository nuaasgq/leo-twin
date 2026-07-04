import { Color } from "cesium";

export const OPAQUE_GLOBE_BASE_COLOR_HEX = "#07141d";
export const TRANSLUCENT_GLOBE_BASE_COLOR_HEX = "#0b2a39";
export const TRANSLUCENT_GLOBE_FRONT_ALPHA = 0.38;
export const TRANSLUCENT_GLOBE_BACK_ALPHA = 0.18;

export type GlobeVisualMode = "OPAQUE" | "TRANSLUCENT";

export interface GlobeVisualPolicySummary {
  mode: GlobeVisualMode;
  background: string;
  baseColor: string;
  depthTestAgainstTerrain: boolean;
  groundAtmosphere: boolean;
  globeTranslucency: boolean;
  frontFaceAlpha?: number;
  backFaceAlpha?: number;
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

export function applyTranslucentGlobeVisualPolicy(scene: GlobeVisualSceneTarget): void {
  scene.backgroundColor = Color.BLACK;
  scene.globe.baseColor = Color.fromCssColorString(TRANSLUCENT_GLOBE_BASE_COLOR_HEX);
  scene.globe.depthTestAgainstTerrain = false;
  scene.globe.showGroundAtmosphere = true;
  if (scene.globe.translucency) {
    scene.globe.translucency.enabled = true;
    scene.globe.translucency.frontFaceAlpha = TRANSLUCENT_GLOBE_FRONT_ALPHA;
    scene.globe.translucency.backFaceAlpha = TRANSLUCENT_GLOBE_BACK_ALPHA;
  }
  if (scene.skyAtmosphere) {
    scene.skyAtmosphere.show = true;
  }
}

export function applyGlobeVisualPolicy(
  scene: GlobeVisualSceneTarget,
  mode: GlobeVisualMode
): void {
  if (mode === "TRANSLUCENT") {
    applyTranslucentGlobeVisualPolicy(scene);
    return;
  }
  applyOpaqueGlobeVisualPolicy(scene);
}

export function opaqueGlobeVisualPolicySummary(): GlobeVisualPolicySummary {
  return {
    mode: "OPAQUE",
    background: "BLACK",
    baseColor: OPAQUE_GLOBE_BASE_COLOR_HEX,
    depthTestAgainstTerrain: true,
    groundAtmosphere: true,
    globeTranslucency: false
  };
}

export function translucentGlobeVisualPolicySummary(): GlobeVisualPolicySummary {
  return {
    mode: "TRANSLUCENT",
    background: "BLACK",
    baseColor: TRANSLUCENT_GLOBE_BASE_COLOR_HEX,
    depthTestAgainstTerrain: false,
    groundAtmosphere: true,
    globeTranslucency: true,
    frontFaceAlpha: TRANSLUCENT_GLOBE_FRONT_ALPHA,
    backFaceAlpha: TRANSLUCENT_GLOBE_BACK_ALPHA
  };
}
