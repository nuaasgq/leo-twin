import { ScenarioConfig } from "../../core/event_types";

export interface VisualLayerLimits {
  showSatellites: boolean;
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
  return {
    showSatellites,
    beamRenderLimit: 0,
    groundUserRenderLimit: showUsers ? 80 : 0,
    linkRenderLimit: showLinks ? 96 : 0,
    routeRenderLimit: showLinks ? 8 : 0
  };
}
