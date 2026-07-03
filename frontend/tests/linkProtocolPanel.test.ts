import { describe, expect, it } from "vitest";

import { buildLinkProtocolSummary } from "../src/dashboard/link_protocol/LinkProtocolPanel";

describe("buildLinkProtocolSummary", () => {
  it("summarizes links and selects the lowest-latency route deterministically", () => {
    const summary = buildLinkProtocolSummary({
      active_route_id: null,
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
      activeLinks: 2,
      availableRoutes: 2,
      bestRouteId: "route-fast",
      bestPath: "user -> sat-a -> sat-b -> node",
      bestLatency: 1.5,
      bottleneckCapacity: 40,
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
        }
      ]
    });
  });

  it("prefers the active route when it is available", () => {
    const summary = buildLinkProtocolSummary({
      active_route_id: "route-selected",
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
  });
});
