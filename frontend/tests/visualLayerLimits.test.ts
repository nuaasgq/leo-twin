import { describe, expect, it } from "vitest";

import { ScenarioConfig } from "../src/core/event_types";
import { visualLayerLimits } from "../src/3d/cesium/renderLimits";

describe("visualLayerLimits", () => {
  it("enables bounded network visual layers by default", () => {
    expect(visualLayerLimits(null)).toEqual({
      showSatellites: true,
      beamRenderLimit: 0,
      groundUserRenderLimit: 80,
      linkRenderLimit: 96,
      routeRenderLimit: 8
    });
  });

  it("honors scenario visualization switches", () => {
    const config: ScenarioConfig = {
      ui: {
        visualization: {
          satellites: false,
          users: false,
          links: false,
          metrics: true
        }
      }
    };

    expect(visualLayerLimits(config)).toEqual({
      showSatellites: false,
      beamRenderLimit: 0,
      groundUserRenderLimit: 0,
      linkRenderLimit: 0,
      routeRenderLimit: 0
    });
  });
});
