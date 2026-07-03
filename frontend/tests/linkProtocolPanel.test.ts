import { describe, expect, it } from "vitest";

import { buildLinkProtocolSummary } from "../src/dashboard/link_protocol/LinkProtocolPanel";

describe("buildLinkProtocolSummary", () => {
  it("summarizes links and selects the lowest-latency route deterministically", () => {
    const summary = buildLinkProtocolSummary({
      active_route_id: null,
      scenario_config: {
        network: {
          transport_protocol: "UDP",
          routing_protocol: "DISTANCE_VECTOR",
          carrier_frequency_hz: 22_000_000_000,
          channel_bandwidth_hz: 250_000_000,
          rain_rate_mm_h: 12.5,
          rain_attenuation_coefficient_db_per_km_per_mm_h: 0.015,
          rain_effective_path_km: 4
        }
      },
      links: [
        {
          source_id: "sat-b",
          target_id: "sat-c",
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
          latency: 0.3,
          capacity: 30,
          availability: true
        },
        {
          source_id: "sat-x",
          target_id: "sat-y",
          latency: 0.1,
          capacity: 100,
          availability: false
        }
      ],
      routes: [
        {
          route_id: "route-slow",
          flow_id: "flow-a",
          path: ["user", "sat-b", "node"],
          latency: 2.0,
          capacity: 40,
          available: true
        },
        {
          route_id: "route-fast",
          flow_id: "flow-b",
          path: ["user", "sat-a", "sat-b", "node"],
          latency: 1.5,
          capacity: 60,
          available: true
        }
      ]
    });

    expect(summary).toEqual({
      activeLinks: 3,
      availableRoutes: 2,
      bestRouteId: "route-fast",
      bestPath: "user -> sat-a -> sat-b -> node",
      bestHopCount: 3,
      bestLatency: 1.5,
      bottleneckCapacity: 30,
      spaceLinks: 2,
      accessLinks: 1,
      transportProtocol: "UDP",
      routingProtocol: "DISTANCE_VECTOR",
      stackLayers: 6,
      carrierFrequencyGhz: 22,
      bandwidthMhz: 250,
      estimatedRainFadeDb: 0.75,
      rows: [
        {
          linkId: "sat-a -> sat-b",
          latency: 0.2,
          capacity: 80,
          status: "可用"
        },
        {
          linkId: "sat-b -> sat-c",
          latency: 0.4,
          capacity: 40,
          status: "可用"
        },
        {
          linkId: "sat-a -> user-1",
          latency: 0.3,
          capacity: 30,
          status: "可用"
        }
      ]
    });
  });

  it("prefers the active route when it is available", () => {
    const summary = buildLinkProtocolSummary({
      active_route_id: "route-selected",
      scenario_config: null,
      links: [],
      routes: [
        {
          route_id: "route-fast",
          flow_id: "flow-a",
          path: ["a", "b"],
          latency: 1,
          capacity: 10,
          available: true
        },
        {
          route_id: "route-selected",
          flow_id: "flow-b",
          path: ["x", "y"],
          latency: 5,
          capacity: 20,
          available: true
        }
      ]
    });

    expect(summary.bestRouteId).toBe("route-selected");
    expect(summary.bestPath).toBe("x -> y");
    expect(summary.transportProtocol).toBe("TCP");
    expect(summary.routingProtocol).toBe("LINK_STATE");
    expect(summary.stackLayers).toBe(6);
    expect(summary.carrierFrequencyGhz).toBe(20);
    expect(summary.bandwidthMhz).toBe(100);
    expect(summary.estimatedRainFadeDb).toBe(0);
  });
});
