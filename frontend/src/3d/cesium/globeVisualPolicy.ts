import { Color } from "cesium";

import {
  SCENE_3D_ASSET_MANIFEST_V1,
  Scene3dAssetManifest
} from "../assets/assetManifest";

export const OPAQUE_GLOBE_BASE_COLOR_HEX = "#07141d";
export const TRANSLUCENT_GLOBE_BASE_COLOR_HEX = "#0b2a39";
export const TRANSLUCENT_GLOBE_FRONT_ALPHA = 0.38;
export const TRANSLUCENT_GLOBE_BACK_ALPHA = 0.18;
export const EARTH_VISUAL_POLICY_V2_ID = "leo_twin.earth_visual_policy.v2";

export type GlobeVisualMode = "OPAQUE" | "TRANSLUCENT";
export type EarthFarSideOcclusion =
  | "ENABLED"
  | "DISABLED_FOR_TRANSLUCENT_OBSERVATION";
export type DayNightVisualMode = "DISABLED_OPTIONAL_FUTURE";

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

export interface EarthVisualPolicyV2Summary {
  version: "v2";
  policy_id: string;
  default_mode: GlobeVisualMode;
  active_mode: GlobeVisualMode;
  earth_texture_asset_id: string;
  country_boundary_asset_id: string;
  country_borders_visible: boolean;
  far_side_occlusion: EarthFarSideOcclusion;
  satellite_depth_test_required: boolean;
  country_label_depth_test_required: boolean;
  day_night_mode: DayNightVisualMode;
  asset_manifest_id: string;
  visual_only: true;
  no_simulation_semantics: true;
}

export interface EarthVisualPolicyV2LayerSummary {
  label: string;
  value: string;
  detail: string;
}

interface GlobeTranslucencyTarget {
  enabled: boolean;
  frontFaceAlpha?: number;
  backFaceAlpha?: number;
  frontFaceAlphaByDistance?: unknown;
  backFaceAlphaByDistance?: unknown;
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
    scene.globe.translucency.frontFaceAlphaByDistance = undefined;
    scene.globe.translucency.backFaceAlphaByDistance = undefined;
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

export function earthVisualPolicyV2Summary(
  activeMode: GlobeVisualMode = "OPAQUE",
  countryBordersVisible = true,
  manifest: Scene3dAssetManifest = SCENE_3D_ASSET_MANIFEST_V1
): EarthVisualPolicyV2Summary {
  const earthTextureAsset = manifest.assets.find(
    (asset) => asset.role === "EARTH_TEXTURE"
  );
  const countryBoundaryAsset = manifest.assets.find(
    (asset) => asset.role === "COUNTRY_BOUNDARIES"
  );
  const isOpaque = activeMode === "OPAQUE";
  return {
    version: "v2",
    policy_id: EARTH_VISUAL_POLICY_V2_ID,
    default_mode: "OPAQUE",
    active_mode: activeMode,
    earth_texture_asset_id: earthTextureAsset?.id ?? "UNKNOWN",
    country_boundary_asset_id: countryBoundaryAsset?.id ?? "UNKNOWN",
    country_borders_visible: countryBordersVisible,
    far_side_occlusion: isOpaque
      ? "ENABLED"
      : "DISABLED_FOR_TRANSLUCENT_OBSERVATION",
    satellite_depth_test_required: isOpaque,
    country_label_depth_test_required: isOpaque,
    day_night_mode: "DISABLED_OPTIONAL_FUTURE",
    asset_manifest_id: manifest.manifest_id,
    visual_only: true,
    no_simulation_semantics: true
  };
}

export function earthVisualPolicyV2LayerSummary(
  activeMode: GlobeVisualMode = "OPAQUE",
  countryBordersVisible = true,
  manifest: Scene3dAssetManifest = SCENE_3D_ASSET_MANIFEST_V1
): EarthVisualPolicyV2LayerSummary {
  const summary = earthVisualPolicyV2Summary(
    activeMode,
    countryBordersVisible,
    manifest
  );
  const modeLabel = summary.active_mode === "OPAQUE" ? "不透明" : "透明观测";
  const borderLabel = summary.country_borders_visible ? "国界显示" : "国界隐藏";
  const occlusionLabel =
    summary.far_side_occlusion === "ENABLED" ? "背面遮挡开启" : "背面遮挡关闭";
  return {
    label: "地球",
    value: `${modeLabel} / ${summary.version}`,
    detail: `NaturalEarthII / ${borderLabel} / ${occlusionLabel} / 日夜关闭`
  };
}
