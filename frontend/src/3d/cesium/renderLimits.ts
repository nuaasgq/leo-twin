import { ScenarioConfig } from "../../core/event_types";

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
  return {
    showSatellites,
    satelliteIconRenderLimit: showSatellites ? 96 : 0,
    satelliteModelRenderLimit: showSatellites ? 32 : 0,
    orbitTrackRenderLimit: showSatellites && showMetrics ? 48 : 0,
    beamRenderLimit: showSatellites && showMetrics ? 1 : 0,
    groundUserRenderLimit: showUsers ? 80 : 0,
    linkRenderLimit: showLinks ? 96 : 0,
    routeRenderLimit: showLinks && showMetrics ? 8 : 0
  };
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
