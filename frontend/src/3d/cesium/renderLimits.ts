import { ScenarioConfig } from "../../core/event_types";
import { scene3dAssetManifestSummary } from "../assets/assetManifest";

const SMALL_SCALE_FULL_ICON_LIMIT = 120;

export interface VisualLayerLimits {
  showSatellites: boolean;
  satelliteIconRenderLimit: number;
  satelliteModelRenderLimit: number;
  orbitTrackRenderLimit: number;
  beamRenderLimit: number;
  groundUserRenderLimit: number;
  linkRenderLimit: number;
  routeRenderLimit: number;
}

export interface LocalVisualLayerState {
  countryOverlays: boolean;
  satellitePoints: boolean;
  satelliteIcons: boolean;
  satelliteModels: boolean;
  orbitTracks: boolean;
  coverageBeams: boolean;
  groundUsers: boolean;
  links: boolean;
  routes: boolean;
}

export type LocalVisualLayerKey = keyof LocalVisualLayerState;

export interface VisualLayerControlSummaryItem {
  label: string;
  value: string;
  detail: string;
}

export const DEFAULT_LOCAL_VISUAL_LAYERS: LocalVisualLayerState = {
  countryOverlays: true,
  satellitePoints: true,
  satelliteIcons: true,
  satelliteModels: true,
  orbitTracks: true,
  coverageBeams: true,
  groundUsers: true,
  links: true,
  routes: true
};

export function visualLayerLimits(
  scenarioConfig: ScenarioConfig | null | undefined
): VisualLayerLimits {
  const visualization = scenarioConfig?.ui?.visualization;
  const showSatellites = visualization?.satellites ?? true;
  const showLinks = visualization?.links ?? true;
  const showUsers = visualization?.users ?? true;
  const showMetrics = visualization?.metrics ?? true;
  const configuredSatelliteCount = configuredVisualSatelliteCount(scenarioConfig);
  return {
    showSatellites,
    satelliteIconRenderLimit: showSatellites
      ? satelliteIconRenderLimit(configuredSatelliteCount)
      : 0,
    satelliteModelRenderLimit: showSatellites ? 32 : 0,
    orbitTrackRenderLimit: showSatellites && showMetrics ? 48 : 0,
    beamRenderLimit: showSatellites && showMetrics ? 1 : 0,
    groundUserRenderLimit: showUsers ? 80 : 0,
    linkRenderLimit: showLinks ? 96 : 0,
    routeRenderLimit: showLinks && showMetrics ? 8 : 0
  };
}

export function satelliteIconRenderLimit(configuredSatelliteCount = 0): number {
  if (configuredSatelliteCount > 0 && configuredSatelliteCount <= SMALL_SCALE_FULL_ICON_LIMIT) {
    return configuredSatelliteCount;
  }
  return SMALL_SCALE_FULL_ICON_LIMIT;
}

function configuredVisualSatelliteCount(
  scenarioConfig: ScenarioConfig | null | undefined
): number {
  const count =
    scenarioConfig?.backend_summary?.derived_constellation_summary?.satellite_count ??
    scenarioConfig?.scenario?.satellite_count ??
    scenarioConfig?.satellites?.length ??
    0;
  return Number.isFinite(count) ? Math.max(0, Math.floor(count)) : 0;
}

export function applyLocalVisualLayerLimits(
  limits: VisualLayerLimits,
  localLayers: LocalVisualLayerState = DEFAULT_LOCAL_VISUAL_LAYERS
): VisualLayerLimits {
  return {
    showSatellites: limits.showSatellites && localLayers.satellitePoints,
    satelliteIconRenderLimit: localLayers.satelliteIcons
      ? limits.satelliteIconRenderLimit
      : 0,
    satelliteModelRenderLimit: localLayers.satelliteModels
      ? limits.satelliteModelRenderLimit
      : 0,
    orbitTrackRenderLimit: localLayers.orbitTracks ? limits.orbitTrackRenderLimit : 0,
    beamRenderLimit: localLayers.coverageBeams ? limits.beamRenderLimit : 0,
    groundUserRenderLimit: localLayers.groundUsers ? limits.groundUserRenderLimit : 0,
    linkRenderLimit: localLayers.links ? limits.linkRenderLimit : 0,
    routeRenderLimit: localLayers.routes ? limits.routeRenderLimit : 0
  };
}

export function visualSatelliteModelRenderSatellites<
  Satellite extends { satellite_id: string }
>(
  satellites: readonly Satellite[],
  renderLimit: number,
  selectedSatelliteId = ""
): readonly Satellite[] {
  if (renderLimit <= 0) {
    return [];
  }
  const selected = selectedSatelliteId
    ? satellites.find((satellite) => satellite.satellite_id === selectedSatelliteId)
    : undefined;
  const rendered = satellites.slice(0, renderLimit);
  if (!selected || rendered.some((satellite) => satellite.satellite_id === selected.satellite_id)) {
    return rendered;
  }
  return [...rendered, selected];
}

export function visualLayerControlSummary(
  scenarioConfig: ScenarioConfig | null | undefined,
  localLayers: LocalVisualLayerState = DEFAULT_LOCAL_VISUAL_LAYERS
): readonly VisualLayerControlSummaryItem[] {
  const limits = applyLocalVisualLayerLimits(
    visualLayerLimits(scenarioConfig),
    localLayers
  );
  return [
    scene3dAssetManifestSummary(),
    {
      label: "国界",
      value: localLayers.countryOverlays ? "显示" : "隐藏",
      detail: "Natural Earth 国家边界"
    },
    {
      label: "点位",
      value: limits.showSatellites ? "显示" : "隐藏",
      detail: "全部卫星点位"
    },
    {
      label: "图标",
      value: formatLayerLimit(limits.satelliteIconRenderLimit),
      detail: "卫星图标上限"
    },
    {
      label: "模型",
      value: formatLayerLimit(limits.satelliteModelRenderLimit),
      detail: "GLB 模型上限，选中卫星优先"
    },
    {
      label: "轨迹",
      value: formatLayerLimit(limits.orbitTrackRenderLimit),
      detail: "轨道轨迹上限"
    },
    {
      label: "波束",
      value: formatLayerLimit(limits.beamRenderLimit),
      detail: "选中卫星覆盖波束"
    },
    {
      label: "用户",
      value: formatLayerLimit(limits.groundUserRenderLimit),
      detail: "地面用户上限"
    },
    {
      label: "链路",
      value: formatLayerLimit(limits.linkRenderLimit),
      detail: "可视链路上限"
    },
    {
      label: "路由",
      value: formatLayerLimit(limits.routeRenderLimit),
      detail: "路径高亮上限"
    }
  ];
}

function formatLayerLimit(limit: number): string {
  return limit <= 0 ? "隐藏" : `≤${limit.toLocaleString("zh-CN")}`;
}
