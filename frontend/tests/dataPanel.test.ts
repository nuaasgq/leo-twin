import { describe, expect, it } from "vitest";

import { buildDataPanelSummary } from "../src/dashboard/data_panel/DataPanel";
import { WorldSnapshot } from "../src/state/snapshot_engine";

describe("buildDataPanelSummary", () => {
  it("summarizes orbit-network-compute telemetry for the standalone data panel", () => {
    const snapshot = makeSnapshot({
      last_sim_time: 24,
      event_count: 120,
      satellites: [
        {
          satellite_id: "sat-a",
          sim_time: 24,
          position: [1, 2, 3],
          status: "ACTIVE"
        },
        {
          satellite_id: "sat-b",
          sim_time: 24,
          position: [4, 5, 6],
          status: "ACTIVE"
        }
      ],
      ground_users: [
        {
          user_id: "user-a",
          status: "ACTIVE"
        }
      ],
      links: [
        {
          source_id: "sat-a",
          target_id: "sat-b",
          latency: 0.1,
          capacity: 100,
          availability: true
        },
        {
          source_id: "sat-a",
          target_id: "user-a",
          latency: 0.2,
          capacity: 40,
          availability: true
        },
        {
          source_id: "sat-b",
          target_id: "user-b",
          latency: 0.3,
          capacity: 20,
          availability: false
        }
      ],
      routes: [
        {
          route_id: "route-a",
          flow_id: "task-a",
          path: ["user-a", "sat-a", "compute-a"],
          latency: 0.8,
          capacity: 30,
          available: true
        },
        {
          route_id: "route-b",
          flow_id: "task-b",
          path: ["user-b", "sat-b", "sat-a", "compute-a"],
          latency: 1.2,
          capacity: 10,
          available: true
        },
        {
          route_id: "route-c",
          flow_id: "task-c",
          path: [],
          latency: 0,
          capacity: 0,
          available: false
        }
      ],
      active_tasks: [
        {
          task_id: "task-a",
          node_id: "compute-a",
          sim_time: 24,
          progress: 0.5,
          status: "RUNNING"
        }
      ],
      compute_nodes: [
        {
          node_id: "compute-a",
          running_tasks: 1,
          finished_tasks: 2
        }
      ],
      metrics_summary: {
        network: {
          latency: 0.2,
          throughput: 140,
          linkUtilization: 0.5,
          series: []
        },
        compute: {
          taskQueueLength: 1,
          executionSuccessRate: 0.8,
          runningTasks: 1,
          finishedTasks: 2,
          deadlineMissedTasks: 1
        },
        orbit: {
          activeSatellites: 2,
          coverageRatio: 1,
          series: []
        },
        system: {
          eventRate: 5,
          systemLoad: 0.1,
          eventSeries: []
        }
      }
    });

    expect(buildDataPanelSummary(snapshot)).toEqual({
      simTime: 24,
      eventCount: 120,
      eventRate: 5,
      satelliteCount: 2,
      groundUserCount: 1,
      activeLinks: 2,
      spaceLinks: 1,
      accessLinks: 1,
      availableRoutes: 2,
      totalRoutes: 3,
      routeAvailabilityPercent: 67,
      averageRouteLatency: 1,
      averageRouteCapacity: 20,
      averageRouteHops: 2.5,
      maxRouteHops: 3,
      runningTasks: 1,
      finishedTasks: 2,
      deadlineMissedTasks: 1,
      computeNodes: 1,
      networkWaiting: 1,
      couplingHealth: 100
    });
  });

  it("returns bounded zero values for an empty snapshot", () => {
    const summary = buildDataPanelSummary(makeSnapshot());

    expect(summary.routeAvailabilityPercent).toBe(0);
    expect(summary.averageRouteLatency).toBe(0);
    expect(summary.averageRouteCapacity).toBe(0);
    expect(summary.averageRouteHops).toBe(0);
    expect(summary.maxRouteHops).toBe(0);
    expect(summary.couplingHealth).toBe(0);
  });
});

function makeSnapshot(overrides: Partial<WorldSnapshot> = {}): WorldSnapshot {
  return {
    timestamp: 0,
    reducer_version: 0,
    last_sim_time: 0,
    event_count: 0,
    satellites: [],
    links: [],
    routes: [],
    compute_nodes: [],
    ground_users: [],
    active_tasks: [],
    metrics: [],
    metrics_summary: {
      network: {
        latency: 0,
        throughput: 0,
        linkUtilization: 0,
        series: []
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
    },
    scenario_config: null,
    active_route_id: null,
    spatial_index: new Map(),
    indexes: {
      satellites: new Map(),
      ground_users: new Map()
    },
    diff: {
      satellite_ids: [],
      link_ids: [],
      task_ids: [],
      metric_ids: []
    },
    ...overrides
  };
}
