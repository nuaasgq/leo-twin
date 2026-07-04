import { ScenarioConfig } from "../../core/event_types";

export interface VisualLayerLimits {
  showSatellites: boolean;
  satelliteIconRenderLimit: number;
  orbitTrackRenderLimit: number;
  beamRenderLimit: number;
  groundUserRenderLimit: number;
  linkRenderLimit: number;
  routeRenderLimit: number;
}

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
    orbitTrackRenderLimit: showSatellites && showMetrics ? 48 : 0,
    beamRenderLimit: showSatellites && showMetrics ? 1 : 0,
    groundUserRenderLimit: showUsers ? 80 : 0,
    linkRenderLimit: showLinks ? 96 : 0,
    routeRenderLimit: showLinks && showMetrics ? 8 : 0
  };
}
