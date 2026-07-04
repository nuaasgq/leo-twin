import { describe, expect, it } from "vitest";

import {
  buildSatelliteModelParts,
  satelliteModelEntityIds
} from "../src/3d/orbit_renderer/satelliteModelEntities";
import {
  appendSatelliteInsetTrail,
  satelliteAltitudeKm,
  satelliteInsetPoint,
  selectedDisplaySatellite
} from "../src/3d/cesium/satelliteFollow";
import { SatelliteState } from "../src/core/event_types";

describe("satellite model entities", () => {
  it("builds a deterministic multi-part 3D satellite display model", () => {
    const parts = buildSatelliteModelParts(satelliteA);

    expect(parts.map((part) => part.kind)).toEqual([
      "bus",
      "panel-left",
      "panel-right",
      "antenna",
      "sensor"
    ]);
    expect(parts.map((part) => part.id)).toEqual(satelliteModelEntityIds(satelliteA));
    expect(parts[0].position).toEqual([7_000_000, 0, 0]);
    expect(parts[1].position).toEqual([7_000_000, 0, -126_000]);
    expect(parts[2].position).toEqual([7_000_000, 0, 126_000]);
    expect(parts[3].position).toEqual([7_082_000, 0, 0]);
    expect(parts[4].position).toEqual([6_934_000, 0, 0]);
  });
});

describe("satellite follow inset", () => {
  it("selects a stable target satellite and projects it into the inset", () => {
    expect(selectedDisplaySatellite([satelliteA, satelliteB], "sat-b")).toBe(satelliteB);
    expect(selectedDisplaySatellite([satelliteA, satelliteB], "missing")).toBe(
      satelliteA
    );
    expect(selectedDisplaySatellite([], "sat-a")).toBeNull();

    expect(satelliteInsetPoint(satelliteA)).toEqual({
      satelliteId: "sat-a",
      simTime: 1,
      x: 50,
      y: 50
    });
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
    expect(secondTrail[1].x).toBe(71);
    expect(switchedTrail).toHaveLength(1);
    expect(switchedTrail[0].satelliteId).toBe("sat-b");
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
