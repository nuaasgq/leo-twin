import { describe, expect, it } from "vitest";

import {
  NASA_SATELLITE_KIT_MODEL_PARTS,
  buildSatelliteModelParts,
  satelliteModelEntityIds
} from "../src/3d/orbit_renderer/satelliteModelEntities";
import {
  SATELLITE_DEPTH_TEST_DISABLE_DISTANCE,
  SATELLITE_ICON_DATA_URI
} from "../src/3d/orbit_renderer/satelliteEntities";
import { selectedCoverageBeamSatellites } from "../src/3d/beam_renderer/beamEntities";
import {
  appendSatelliteInsetTrail,
  satelliteComputeSummary,
  satelliteAltitudeKm,
  satelliteInsetPoint,
  selectedDisplaySatellite
} from "../src/3d/cesium/satelliteFollow";
import { SatelliteState } from "../src/core/event_types";

describe("satellite model entities", () => {
  it("builds a deterministic fallback multi-part satellite display model", () => {
    const parts = buildSatelliteModelParts(satelliteA);

    expect(parts.map((part) => part.kind)).toEqual([
      "bus",
      "panel-left",
      "panel-right",
      "antenna",
      "sensor"
    ]);
    expect(parts[0].position).toEqual([7_000_000, 0, 0]);
    expect(parts[1].position).toEqual([7_000_000, 0, -126_000]);
    expect(parts[2].position).toEqual([7_000_000, 0, 126_000]);
    expect(parts[3].position).toEqual([7_082_000, 0, 0]);
    expect(parts[4].position).toEqual([6_934_000, 0, 0]);
  });

  it("uses bundled NASA Satellite Kit GLB assets for the primary satellite model", () => {
    expect(NASA_SATELLITE_KIT_MODEL_PARTS.map((asset) => asset.idSuffix)).toEqual([
      "body",
      "wings",
      "radio"
    ]);
    expect(satelliteModelEntityIds(satelliteA)).toEqual([
      "satellite-model:nasa-kit:sat-a:body",
      "satellite-model:nasa-kit:sat-a:wings",
      "satellite-model:nasa-kit:sat-a:radio"
    ]);
    for (const asset of NASA_SATELLITE_KIT_MODEL_PARTS) {
      expect(asset.uri).toMatch(/^\/assets\/nasa-satellite-kit\/.+\.glb$/);
    }
  });
});

describe("satellite overview icon", () => {
  it("keeps satellite overlays depth-tested so the opaque globe occludes far-side satellites", () => {
    expect(SATELLITE_DEPTH_TEST_DISABLE_DISTANCE).toBe(0);
  });

  it("uses a recognizable satellite glyph instead of only a point marker", () => {
    const decodedIcon = decodeURIComponent(
      SATELLITE_ICON_DATA_URI.replace("data:image/svg+xml;charset=UTF-8,", "")
    );

    expect(decodedIcon).toContain("linearGradient");
    expect(decodedIcon).toContain("panel");
    expect(decodedIcon).toContain("antenna");
    expect(decodedIcon.match(/<rect/g)?.length ?? 0).toBeGreaterThanOrEqual(4);
  });
});

describe("selected satellite coverage beams", () => {
  it("renders coverage only for the selected satellite within the bounded limit", () => {
    expect(selectedCoverageBeamSatellites([satelliteA, satelliteB], "sat-b", 1)).toEqual([
      satelliteB
    ]);
    expect(selectedCoverageBeamSatellites([satelliteA, satelliteB], "sat-b", 0)).toEqual([]);
    expect(selectedCoverageBeamSatellites([satelliteA, satelliteB], "", 1)).toEqual([]);
    expect(selectedCoverageBeamSatellites([satelliteA, satelliteB], "missing", 1)).toEqual([]);
  });
});

describe("satellite follow inset", () => {
  it("selects a stable target satellite and projects it into the inset", () => {
    expect(selectedDisplaySatellite([satelliteA, satelliteB], "sat-b")).toBe(satelliteB);
    expect(selectedDisplaySatellite([satelliteA, satelliteB], "missing")).toBe(
      satelliteA
    );
    expect(selectedDisplaySatellite([], "sat-a")).toBeNull();

    const insetPoint = satelliteInsetPoint(satelliteA);

    expect(insetPoint.satelliteId).toBe("sat-a");
    expect(insetPoint.simTime).toBe(1);
    expect(insetPoint.x).toBeCloseTo(84, 3);
    expect(insetPoint.y).toBeCloseTo(50.026, 3);
    expect(satelliteAltitudeKm(satelliteA)).toBeCloseTo(629, 6);
  });

  it("appends incremental motion and resets when the followed satellite changes", () => {
    const firstTrail = appendSatelliteInsetTrail([], satelliteA);
    const duplicateTrail = appendSatelliteInsetTrail(firstTrail, satelliteA);
    const secondTrail = appendSatelliteInsetTrail(firstTrail, {
      ...satelliteA,
      sim_time: 2,
      position: [0, 7_000_000, 0]
    });
    const switchedTrail = appendSatelliteInsetTrail(secondTrail, satelliteB);

    expect(duplicateTrail).toBe(firstTrail);
    expect(secondTrail).toHaveLength(2);
    expect(secondTrail[1].x).toBeCloseTo(49.927, 3);
    expect(secondTrail[1].y).toBeCloseTo(74, 2);
    expect(switchedTrail).toHaveLength(1);
    expect(switchedTrail[0].satelliteId).toBe("sat-b");
  });

  it("summarizes selected satellite compute-node resources", () => {
    expect(
      satelliteComputeSummary({
        capacity: 20,
        available_capacity: 5,
        load_ratio: 0.75,
        status: "BUSY"
      })
    ).toEqual({
      capacityLabel: "20 GFLOPS FP32",
      availableLabel: "5 GFLOPS",
      utilizationLabel: "75%",
      statusLabel: "BUSY"
    });
    expect(satelliteComputeSummary(null)).toBeNull();
  });
});

const satelliteA: SatelliteState = {
  satellite_id: "sat-a",
  sim_time: 1,
  position: [7_000_000, 0, 0],
  velocity: [0, 7_500, 0],
  status: "ACTIVE"
};

const satelliteB: SatelliteState = {
  satellite_id: "sat-b",
  sim_time: 1,
  position: [0, 0, 7_000_000],
  velocity: [7_500, 0, 0],
  status: "ACTIVE"
};
