import { describe, expect, it } from "vitest";

import {
  buildOrbitTrackSamples,
  projectSatelliteState,
  satelliteMotionProjectionLabel
} from "../src/3d/cesium/positions";

describe("buildOrbitTrackSamples", () => {
  it("builds a closed deterministic display orbit through the satellite position", () => {
    const samples = buildOrbitTrackSamples(
      {
        satellite_id: "sat-a",
        sim_time: 120,
        position: [7_000_000, 0, 0],
        velocity: [0, 7_500, 0],
        status: "ACTIVE"
      },
      16
    );

    expect(samples).toHaveLength(17);
    expect(samples[0]).toEqual([7_000_000, 0, 0]);
    expect(samples[16]).toEqual(samples[0]);
    for (const sample of samples) {
      expect(Math.hypot(sample[0], sample[1], sample[2])).toBeCloseTo(7_000_000, 6);
    }
  });

  it("uses a stable fallback plane when velocity is unavailable", () => {
    const first = buildOrbitTrackSamples(
      {
        satellite_id: "sat-a",
        sim_time: 120,
        position: [0, 7_000_000, 0],
        status: "ACTIVE"
      },
      8
    );
    const second = buildOrbitTrackSamples(
      {
        satellite_id: "sat-a",
        sim_time: 120,
        position: [0, 7_000_000, 0],
        status: "ACTIVE"
      },
      8
    );

    expect(second).toEqual(first);
    expect(first[0]).toEqual([0, 7_000_000, 0]);
    expect(first[first.length - 1]).toEqual(first[0]);
  });
});

describe("satelliteMotionProjectionLabel", () => {
  it("labels display-clock projection relative to the latest snapshot", () => {
    expect(satelliteMotionProjectionLabel(120, 120)).toBe("快照同步");
    expect(satelliteMotionProjectionLabel(120.03, 120)).toBe("快照同步");
    expect(satelliteMotionProjectionLabel(122.5, 120)).toBe("显示外推 +2.5秒");
    expect(satelliteMotionProjectionLabel(118, 120)).toBe("快照同步");
  });
});

describe("projectSatelliteState", () => {
  it("uses velocity to advance display-only satellite motion between event updates", () => {
    expect(
      projectSatelliteState(
        {
          satellite_id: "sat-a",
          sim_time: 10,
          position: [7_000_000, 0, 0],
          velocity: [0, 7_500, 0],
          status: "ACTIVE"
        },
        12.5
      )
    ).toEqual({
      satellite_id: "sat-a",
      sim_time: 12.5,
      position: [7_000_000, 18_750, 0],
      velocity: [0, 7_500, 0],
      status: "ACTIVE"
    });
  });

  it("does not extrapolate backwards or without velocity", () => {
    const satellite = {
      satellite_id: "sat-a",
      sim_time: 10,
      position: [7_000_000, 0, 0],
      status: "ACTIVE"
    } as const;

    expect(projectSatelliteState(satellite, 9)).toBe(satellite);
    expect(projectSatelliteState(satellite, 12)).toBe(satellite);
  });
});
