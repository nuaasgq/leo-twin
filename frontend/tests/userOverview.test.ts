import { describe, expect, it } from "vitest";

import type { RuntimeStatusPayload } from "../src/core/event_types";
import { buildUserOverviewSummary } from "../src/dashboard/user_overview/UserOverview";
import type { WorldSnapshot } from "../src/state/snapshot_engine";

describe("user-facing runtime overview", () => {
  it("prefers backend runtime metrics and summarizes only user-facing values", () => {
    const summary = buildUserOverviewSummary(
      makeSnapshot({
        satellites: [satellite("sat-0"), satellite("sat-1")],
        ground_users: [{ user_id: "user-0", status: "ACTIVE" }],
        links: [
          { source_id: "sat-0", target_id: "user-0", latency: 0.1, capacity: 20, availability: true },
          { source_id: "sat-1", target_id: "user-0", latency: 0.2, capacity: 10, availability: false }
        ],
        routes: [
          { route_id: "route-0", flow_id: "flow-0", path: ["user-0", "sat-0"], latency: 0.1, capacity: 20, available: true },
          { route_id: "route-1", flow_id: "flow-1", path: [], latency: 0, capacity: 0, available: false }
        ],
        compute_nodes: [
          computeNode("sat-0", 0.25, 1),
          computeNode("sat-1", 0.75, 3)
        ],
        metrics_summary: {
          ...makeSnapshot().metrics_summary,
          network: {
            latency: 8,
            throughput: 10,
            linkUtilization: 0.5,
            series: [],
            kpiSeries: [
              { simTime: 10, throughputMbps: 11, latencyMs: 9, lossPercent: 1, jitterMs: 2 }
            ]
          },
          compute: {
            taskQueueLength: 1,
            executionSuccessRate: 1,
            runningTasks: 2,
            finishedTasks: 4,
            deadlineMissedTasks: 0
          }
        }
      }),
      runtimeStatus({
        current_sim_time: 50,
        duration: 200,
        metrics_summary: {
          network_quality_effective_throughput_mbps: 88,
          network_quality_effective_latency_avg_s: 0.12,
          network_quality_effective_loss_proxy_rate: 0.03,
          network_quality_effective_delay_variation_proxy_s: 0.007
        }
      }),
      null
    );

    expect(summary).toMatchObject({
      statusLabel: "运行中",
      progressPercent: 25,
      satelliteCount: 2,
      userCount: 1,
      activeLinkCount: 1,
      availableRouteCount: 1,
      totalRouteCount: 2,
      throughputMbps: 88,
      latencyMs: 120,
      lossPercent: 3,
      jitterMs: 7,
      computeUtilizationPercent: 50,
      runningTaskCount: 2,
      finishedTaskCount: 4
    });
  });

});

function runtimeStatus(overrides: Partial<RuntimeStatusPayload> = {}): RuntimeStatusPayload {
  return {
    status: "RUNNING",
    mode: "REAL_TIME",
    speed_factor: 1,
    seed: 1,
    duration: 600,
    config_version: 1,
    last_action: "START",
    ...overrides
  };
}

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
      network: { latency: 0, throughput: 0, linkUtilization: 0, series: [] },
      compute: {
        taskQueueLength: 0,
        executionSuccessRate: 1,
        runningTasks: 0,
        finishedTasks: 0,
        deadlineMissedTasks: 0
      },
      orbit: { activeSatellites: 0, coverageRatio: 0, series: [] },
      system: { eventRate: 0, systemLoad: 0, eventSeries: [] }
    },
    scenario_config: null,
    fidelity_summary: null,
    active_route_id: null,
    spatial_index: new Map(),
    indexes: { satellites: new Map(), ground_users: new Map() },
    diff: { satellite_ids: [], link_ids: [], task_ids: [], metric_ids: [] },
    ...overrides
  };
}

function satellite(satelliteId: string): WorldSnapshot["satellites"][number] {
  return { satellite_id: satelliteId, sim_time: 0, position: [1, 2, 3], status: "ACTIVE" };
}

function computeNode(
  nodeId: string,
  loadRatio: number,
  finishedTasks: number
): WorldSnapshot["compute_nodes"][number] {
  return {
    node_id: nodeId,
    running_tasks: 0,
    finished_tasks: finishedTasks,
    capacity: 100,
    available_capacity: 100 * (1 - loadRatio),
    status: "ACTIVE",
    load_ratio: loadRatio
  };
}
