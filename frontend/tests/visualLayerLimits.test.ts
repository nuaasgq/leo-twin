import { describe, expect, it } from "vitest";

import { ScenarioConfig } from "../src/core/event_types";
import {
  DEFAULT_LOCAL_VISUAL_LAYERS,
  applyLocalVisualLayerLimits,
  visualLayerLimits,
  visualSatelliteModelRenderSatellites
} from "../src/3d/cesium/renderLimits";

describe("visualLayerLimits", () => {
  it("enables bounded network visual layers by default", () => {
    expect(visualLayerLimits(null)).toEqual({
      showSatellites: true,
      satelliteIconRenderLimit: 96,
      satelliteModelRenderLimit: 32,
      orbitTrackRenderLimit: 48,
      beamRenderLimit: 1,
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
      satelliteIconRenderLimit: 0,
      satelliteModelRenderLimit: 0,
      orbitTrackRenderLimit: 0,
      beamRenderLimit: 0,
      groundUserRenderLimit: 0,
      linkRenderLimit: 0,
      routeRenderLimit: 0
    });
  });

  it("uses the metrics switch for orbit and route auxiliary layers", () => {
    const config: ScenarioConfig = {
      ui: {
        visualization: {
          satellites: true,
          users: true,
          links: true,
          metrics: false
        }
      }
    };

    expect(visualLayerLimits(config)).toEqual({
      showSatellites: true,
      satelliteIconRenderLimit: 96,
      satelliteModelRenderLimit: 32,
      orbitTrackRenderLimit: 0,
      beamRenderLimit: 0,
      groundUserRenderLimit: 80,
      linkRenderLimit: 96,
      routeRenderLimit: 0
    });
  });

  it("keeps backend layer limits unchanged when local layers are all enabled", () => {
    const limits = visualLayerLimits(null);

    expect(applyLocalVisualLayerLimits(limits, DEFAULT_LOCAL_VISUAL_LAYERS)).toEqual(
      limits
    );
  });

  it("locally suppresses selected visual layers without changing other budgets", () => {
    expect(
      applyLocalVisualLayerLimits(visualLayerLimits(null), {
        ...DEFAULT_LOCAL_VISUAL_LAYERS,
        satellitePoints: false,
        satelliteIcons: false,
        coverageBeams: false,
        links: false
      })
    ).toEqual({
      showSatellites: false,
      satelliteIconRenderLimit: 0,
      satelliteModelRenderLimit: 32,
      orbitTrackRenderLimit: 48,
      beamRenderLimit: 0,
      groundUserRenderLimit: 80,
      linkRenderLimit: 0,
      routeRenderLimit: 8
    });
  });

  it("cannot re-enable layers disabled by scenario configuration", () => {
    const config: ScenarioConfig = {
      ui: {
        visualization: {
          satellites: false,
          users: false,
          links: false,
          metrics: false
        }
      }
    };
    const disabledLimits = visualLayerLimits(config);

    expect(
      applyLocalVisualLayerLimits(disabledLimits, DEFAULT_LOCAL_VISUAL_LAYERS)
    ).toEqual(disabledLimits);
  });
});

describe("visualSatelliteModelRenderSatellites", () => {
  const satellites = Array.from({ length: 8 }, (_, index) => ({
    satellite_id: `sat-${index}`
  }));

  it("keeps model rendering bounded by default", () => {
    expect(
      visualSatelliteModelRenderSatellites(satellites, 3).map(
        (satellite) => satellite.satellite_id
      )
    ).toEqual(["sat-0", "sat-1", "sat-2"]);
  });

  it("adds the selected satellite model when it is outside the default model budget", () => {
    expect(
      visualSatelliteModelRenderSatellites(satellites, 3, "sat-6").map(
        (satellite) => satellite.satellite_id
      )
    ).toEqual(["sat-0", "sat-1", "sat-2", "sat-6"]);
  });

  it("does not duplicate selected satellites already inside the model budget", () => {
    expect(
      visualSatelliteModelRenderSatellites(satellites, 3, "sat-1").map(
        (satellite) => satellite.satellite_id
      )
    ).toEqual(["sat-0", "sat-1", "sat-2"]);
  });
});
