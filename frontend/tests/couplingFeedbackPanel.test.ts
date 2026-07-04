import { describe, expect, it } from "vitest";

import { buildCouplingFeedbackSummary } from "../src/dashboard/coupling_feedback/CouplingFeedbackPanel";

describe("buildCouplingFeedbackSummary", () => {
  it("summarizes deterministic orbit-network-compute feedback state", () => {
    const summary = buildCouplingFeedbackSummary({
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
          source_id: "sat-c",
          target_id: "user-c",
          latency: 0.4,
          capacity: 10,
          availability: false
        }
      ],
      routes: [
        {
          route_id: "route-a",
          flow_id: "task-a",
          path: ["user-a", "sat-a", "node-a"],
          latency: 0.8,
          capacity: 30,
          available: true
        },
        {
          route_id: "route-b",
          flow_id: "task-b",
          path: [],
          latency: 0,
          capacity: 0,
          available: false
        }
      ],
      active_tasks: [
        {
          task_id: "task-a",
          node_id: "node-a",
          sim_time: 10,
          progress: 0.4,
          status: "RUNNING"
        }
      ],
      compute_nodes: [
        {
          node_id: "node-a",
          running_tasks: 1,
          finished_tasks: 0,
          capacity: 20,
          available_capacity: 4,
          status: "BUSY",
          load_ratio: 0.8
        },
        {
          node_id: "node-b",
          running_tasks: 0,
          finished_tasks: 0,
          capacity: 20,
          available_capacity: 20,
          status: "IDLE",
          load_ratio: 0
        }
      ],
      metrics_summary: {
        network: {
          latency: 0,
          throughput: 0,
          linkUtilization: 0,
          series: [],
          topology: {
            activeSpaceLinks: 1,
            activeAccessLinks: 1,
            linkUpdateEvents: 2,
            accessStartEvents: 1,
            accessEndEvents: 0,
            routeUpdateEvents: 3,
            topologyEvents: 3
          }
        },
        compute: {
          taskQueueLength: 0,
          executionSuccessRate: 1,
          runningTasks: 1,
          finishedTasks: 0,
          deadlineMissedTasks: 0
        },
        orbit: {
          activeSatellites: 2,
          coverageRatio: 1,
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
      activeAccessLinks: 1,
      activeSpaceLinks: 1,
      availableRoutes: 1,
      totalRoutes: 2,
      waitingForNetwork: 1,
      busyComputeNodes: 1,
      computeNodes: 2,
      averageComputeLoad: 0.4,
      routeUpdateEvents: 3,
      statusLabel: "网络等待",
      signalRows: [
        {
          label: "轨道 -> 网络",
          value: "1 条接入",
          detail: "1 条星间链路参与拓扑"
        },
        {
          label: "网络 -> 算力",
          value: "1/2 条路由",
          detail: "1 个任务等待网络可达"
        },
        {
          label: "算力 -> 网络",
          value: "40%",
          detail: "1 个忙碌节点反馈容量"
        }
      ]
    });
  });

  it("reports a stable feedback loop when routes and compute are healthy", () => {
    const summary = buildCouplingFeedbackSummary({
      links: [
        {
          source_id: "sat-a",
          target_id: "user-a",
          latency: 0.2,
          capacity: 40,
          availability: true
        }
      ],
      routes: [
        {
          route_id: "route-a",
          flow_id: "task-a",
          path: ["user-a", "sat-a", "node-a"],
          latency: 0.8,
          capacity: 30,
          available: true
        }
      ],
      active_tasks: [],
      compute_nodes: [
        {
          node_id: "node-a",
          running_tasks: 0,
          finished_tasks: 0,
          capacity: 20,
          available_capacity: 20,
          status: "IDLE",
          load_ratio: 0
        }
      ],
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
          activeSatellites: 1,
          coverageRatio: 1,
          series: []
        },
        system: {
          eventRate: 0,
          systemLoad: 0,
          eventSeries: []
        }
      }
    });

    expect(summary.statusLabel).toBe("闭环稳定");
    expect(summary.waitingForNetwork).toBe(0);
    expect(summary.averageComputeLoad).toBe(0);
  });
});
