import { describe, expect, it } from "vitest";

import { buildGroundTrackSummary } from "../src/dashboard/ground_track/GroundTrackPanel";

describe("buildGroundTrackSummary", () => {
  it("summarizes satellite ground-track metric records deterministically", () => {
    const summary = buildGroundTrackSummary({
      metrics: [
        metric("sat-b", "satellite.longitude_deg", 120),
        metric("sat-a", "satellite.altitude_km", 629),
        metric("sat-a", "satellite.latitude_deg", 10),
        metric("sat-b", "satellite.altitude_km", 631),
        metric("sat-a", "satellite.longitude_deg", 30),
        metric("sat-b", "satellite.latitude_deg", -20),
        metric("ignored", "link.capacity", 100)
      ]
    });

    expect(summary).toEqual({
      observedSatellites: 2,
      averageAltitudeKm: 630,
      maxAltitudeKm: 631,
      latitudeSpanDeg: 30,
      rows: [
        {
          satelliteId: "sat-a",
          latitudeDeg: 10,
          longitudeDeg: 30,
          altitudeKm: 629
        },
        {
          satelliteId: "sat-b",
          latitudeDeg: -20,
          longitudeDeg: 120,
          altitudeKm: 631
        }
      ]
    });
  });

  it("ignores incomplete ground-track records", () => {
    expect(
      buildGroundTrackSummary({
        metrics: [
          metric("sat-a", "satellite.altitude_km", 629),
          metric("sat-a", "satellite.latitude_deg", 10)
        ]
      })
    ).toEqual({
      observedSatellites: 0,
      averageAltitudeKm: 0,
      maxAltitudeKm: 0,
      latitudeSpanDeg: 0,
      rows: []
    });
  });
});

function metric(entityId: string, metricName: string, value: number) {
  return {
    metric_name: metricName,
    sim_time: 1,
    entity_id: entityId,
    value
  };
}
