import { describe, expect, it } from "vitest";

import { buildOrbitTrackSamples } from "../src/3d/cesium/positions";

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
