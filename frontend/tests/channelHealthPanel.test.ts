import { describe, expect, it } from "vitest";

import { buildChannelHealthSummary } from "../src/dashboard/channel_health/ChannelHealthPanel";

describe("buildChannelHealthSummary", () => {
  it("summarizes physical channel settings and weak links deterministically", () => {
    const summary = buildChannelHealthSummary({
      scenario_config: {
        network: {
          carrier_frequency_hz: 22_000_000_000,
          channel_bandwidth_hz: 250_000_000,
          rain_rate_mm_h: 10,
          rain_attenuation_coefficient_db_per_km_per_mm_h: 0.02,
          rain_effective_path_km: 5
        }
      },
      links: [
        {
          source_id: "sat-b",
          target_id: "user-2",
          latency: 0.4,
          capacity: 40,
          availability: true
        },
        {
          source_id: "sat-a",
          target_id: "sat-b",
          latency: 0.2,
          capacity: 80,
          availability: true
        },
        {
          source_id: "sat-a",
          target_id: "user-1",
          latency: 0.5,
          capacity: 40,
          availability: true
        },
        {
          source_id: "sat-x",
          target_id: "user-x",
          latency: 0.1,
          capacity: 10,
          availability: false
        }
      ]
    });

    expect(summary).toEqual({
      carrierFrequencyGhz: 22,
      bandwidthMhz: 250,
      rainRate: 10,
      estimatedRainFadeDb: 1,
      availableLinks: 3,
      averageCapacity: 53.333333333333336,
      weakestCapacity: 40,
      averageRangeKm: 109923.90126666667,
      freeSpacePathLossDb: 220.12029628377394,
      estimatedSnrDb: -7.976103479918592,
      spectralEfficiency: 0.21333333333333335,
      healthScore: 69,
      rows: [
        {
          linkId: "sat-a -> user-1",
          latency: 0.5,
          capacity: 40,
          status: "可用"
        },
        {
          linkId: "sat-b -> user-2",
          latency: 0.4,
          capacity: 40,
          status: "可用"
        },
        {
          linkId: "sat-a -> sat-b",
          latency: 0.2,
          capacity: 80,
          status: "可用"
        }
      ]
    });
  });

  it("uses deterministic defaults before channel configuration is loaded", () => {
    expect(
      buildChannelHealthSummary({
        scenario_config: null,
        links: []
      })
    ).toEqual({
      carrierFrequencyGhz: 20,
      bandwidthMhz: 100,
      rainRate: 0,
      estimatedRainFadeDb: 0,
      availableLinks: 0,
      averageCapacity: 0,
      weakestCapacity: 0,
      averageRangeKm: 0,
      freeSpacePathLossDb: 0,
      estimatedSnrDb: 0,
      spectralEfficiency: 0,
      healthScore: 0,
      rows: []
    });
  });
});
