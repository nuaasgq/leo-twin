import { describe, expect, it } from "vitest";

import { buildDomainSummary } from "../src/dashboard/domain_summary/DomainSummary";

describe("buildDomainSummary", () => {
  it("summarizes linked orbit-network-compute state deterministically", () => {
    const summary = buildDomainSummary({
      links: [
        {
          source_id: "sat-1",
          target_id: "user-1",
          latency: 1.2,
          capacity: 50,
          availability: true
        },
        {
          source_id: "sat-2",
          target_id: "user-2",
          latency: 2.2,
          capacity: 10,
          availability: false
        }
      ],
      routes: [
        {
          route_id: "route-b",
          flow_id: "flow-b",
          path: ["user-1", "sat-2", "node-a"],
          latency: 2.0,
          capacity: 20,
          available: true
        },
        {
          route_id: "route-a",
          flow_id: "flow-a",
          path: ["user-1", "sat-1", "node-a"],
          latency: 1.5,
          capacity: 40,
          available: true
        }
      ],
      active_tasks: [
        {
          task_id: "task-1",
          node_id: "node-a",
          sim_time: 1,
          progress: 0.5,
          status: "RUNNING"
        }
      ],
      compute_nodes: [
        {
          node_id: "node-a",
          running_tasks: 1,
          finished_tasks: 2
        }
      ]
    });

    expect(summary).toEqual({
      activeLinks: 1,
      availableRoutes: 2,
      routeLatency: 1.5,
      routeCapacity: 40,
      runningTasks: 1,
      finishedTasks: 2,
      computeNodes: 1
    });
  });
});
