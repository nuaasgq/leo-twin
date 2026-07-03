import { describe, expect, it } from "vitest";

import { buildTopologyChangeSummary } from "../src/dashboard/topology_change/TopologyChangePanel";

describe("buildTopologyChangeSummary", () => {
  it("summarizes topology churn deterministically", () => {
    const summary = buildTopologyChangeSummary({
      metrics_summary: {
        network: {
          latency: 0,
          throughput: 0,
          linkUtilization: 0,
          series: [],
          topology: {
            activeSpaceLinks: 12,
            activeAccessLinks: 34,
            linkUpdateEvents: 80,
            accessStartEvents: 21,
            accessEndEvents: 9,
            routeUpdateEvents: 15,
            topologyEvents: 125
          }
        },
        compute: {
          taskQueueLength: 0,
          executionSuccessRate: 1,
          runningTasks: 0,
          finishedTasks: 0,
          deadlineMissedTasks: 0
        },
        orbit: {
          activeSatellites: 0,
          coverageRatio: 0,
          series: []
        },
        system: {
          eventRate: 0,
          systemLoad: 0,
          eventSeries: []
        }
      }
    });

    expect(summary).toEqual({
      activeSpaceLinks: 12,
      activeAccessLinks: 34,
      linkUpdateEvents: 80,
      accessStartEvents: 21,
      accessEndEvents: 9,
      routeUpdateEvents: 15,
      topologyEvents: 125,
      churnBalance: 12
    });
  });
});
