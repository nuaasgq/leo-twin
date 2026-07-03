import { describe, expect, it } from "vitest";

import { buildComputeQueueSummary } from "../src/dashboard/compute_queue/ComputeQueuePanel";

describe("buildComputeQueueSummary", () => {
  it("summarizes compute queues deterministically", () => {
    const summary = buildComputeQueueSummary({
      active_tasks: [
        {
          task_id: "task-c",
          node_id: "node-b",
          sim_time: 2,
          progress: 0.2,
          status: "RUNNING"
        },
        {
          task_id: "task-a",
          node_id: "node-a",
          sim_time: 1,
          progress: 0.8,
          status: "RUNNING"
        }
      ],
      compute_nodes: [
        {
          node_id: "node-b",
          running_tasks: 2,
          finished_tasks: 1
        },
        {
          node_id: "node-a",
          running_tasks: 1,
          finished_tasks: 5
        }
      ],
      routes: [
        {
          route_id: "route-a",
          flow_id: "task-a",
          path: ["user-a", "sat-a", "node-a"],
          latency: 1,
          capacity: 50,
          available: true
        },
        {
          route_id: "route-b",
          flow_id: "task-b",
          path: [],
          latency: 0,
          capacity: 0,
          available: false
        },
        {
          route_id: "route-c",
          flow_id: "task-c",
          path: ["user-c", "sat-c", "node-b"],
          latency: 2,
          capacity: 30,
          available: true
        }
      ]
    });

    expect(summary).toEqual({
      runningTasks: 3,
      finishedTasks: 6,
      totalRequests: 3,
      unfinishedTasks: 0,
      availableRoutes: 2,
      waitingForNetwork: 1,
      computeNodes: 2,
      busiestNodeId: "node-b",
      nodeRows: [
        {
          nodeId: "node-b",
          runningTasks: 2,
          finishedTasks: 1
        },
        {
          nodeId: "node-a",
          runningTasks: 1,
          finishedTasks: 5
        }
      ],
      taskRows: [
        {
          taskId: "task-a",
          nodeId: "node-a",
          progress: 0.8,
          status: "RUNNING"
        },
        {
          taskId: "task-c",
          nodeId: "node-b",
          progress: 0.2,
          status: "RUNNING"
        }
      ]
    });
  });
});
