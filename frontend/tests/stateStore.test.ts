import { describe, expect, it } from "vitest";

import { SimEvent } from "../src/core/event_types";
import { ObservabilityStore, selectNetworkKpis } from "../src/stream/state_store";

describe("ObservabilityStore", () => {
  it("updates centralized rendering state from event stream", () => {
    const store = new ObservabilityStore({ eventLogLimit: 4 });
    store.applyScenarioConfig({
      ground_users: [{ user_id: "user-1", position: [120, 30, 0] }]
    });

    store.applyEvents([
      event("sat:1", "ORBIT_UPDATE", {
        satellite_id: "sat-1",
        sim_time: 1,
        position: [1, 2, 3],
        velocity: [0, 1, 0],
        status: "online"
      }),
      event("link:1", "ACCESS_START", {
        source_id: "sat-1",
        target_id: "user-1",
        latency: 12,
        capacity: 40,
        availability: true
      })
    ]);

    const state = store.getSnapshot();
    expect(state.satellites.get("sat-1")?.position).toEqual([1, 2, 3]);
    expect(state.groundUsers.get("user-1")?.position).toEqual([120, 30, 0]);
    expect(state.links.size).toBe(1);
    expect(selectNetworkKpis(state)).toEqual({
      latency: 12,
      throughput: 40,
      linkUtilization: 0
    });
  });

  it("keeps backend fidelity summary from scenario and state snapshots", () => {
    const store = new ObservabilityStore();
    store.applyScenarioConfig({
      backend_summary: {
        fidelity_summary: {
          orbit_update_mode: "BATCH",
          metrics_mode: "AGGREGATED",
          space_link_mode: "BOUNDED_CANDIDATE",
          detailed_space_link_enabled: false,
          space_link_candidate_policy: "SAME_PLANE_AND_ADJACENT_PLANE_BOUNDED_CANDIDATES",
          max_space_link_candidates_per_satellite: 4,
          batch_space_link_update_limit: 999,
          scale_limit_reason: "orbit updates are batched",
          current_scale_mode: "LARGE_SCALE_AGGREGATED",
          fidelity_warnings: ["Orbit updates are batched."],
          satellite_count: 1200,
          user_count: 20
        }
      }
    });

    expect(store.getSnapshot().fidelitySummary?.satellite_count).toBe(1200);

    store.applySnapshot({
      fidelity_summary: {
        orbit_update_mode: "BATCH",
        metrics_mode: "DETAILED",
        space_link_mode: "DETAILED_SMALL_SCALE",
        detailed_space_link_enabled: true,
        space_link_candidate_policy: "CELL_INDEX_NEARBY_WITH_RANGE_LIMIT",
        max_space_link_candidates_per_satellite: 4,
        batch_space_link_update_limit: 999,
        scale_limit_reason: "orbit updates are batched",
        current_scale_mode: "LARGE_SCALE_BATCH",
        fidelity_warnings: ["Orbit updates are batched."],
        satellite_count: 300,
        user_count: 20
      }
    });

    expect(store.getSnapshot().fidelitySummary?.satellite_count).toBe(300);
    expect(store.getSnapshot().fidelitySummary?.space_link_mode).toBe(
      "DETAILED_SMALL_SCALE"
    );
  });

  it("does not let stale state snapshots roll back newer event stream entities", () => {
    const store = new ObservabilityStore();
    store.applyEvents([
      event("orbit:new", "ORBIT_UPDATE", {
        satellite_id: "sat-1",
        sim_time: 10,
        position: [10, 0, 0],
        velocity: [0, 0, 0],
        status: "online"
      }),
      event("task:new", "TASK_START", {
        task_id: "task-1",
        node_id: "sat-1",
        sim_time: 10,
        progress: 0.8,
        status: "RUNNING"
      }),
      event("compute:new", "COMPUTE_NODE_UPDATE", {
        node_id: "sat-1",
        sim_time: 10,
        capacity: 10,
        available_capacity: 2,
        status: "BUSY"
      })
    ]);

    store.applySnapshot({
      satellites: [
        {
          satellite_id: "sat-1",
          sim_time: 5,
          position: [5, 0, 0],
          velocity: [0, 0, 0],
          status: "stale"
        }
      ],
      tasks: [
        {
          task_id: "task-1",
          node_id: "sat-1",
          sim_time: 5,
          progress: 0.1,
          status: "STALE"
        }
      ],
      compute_nodes: [
        {
          node_id: "sat-1",
          sim_time: 5,
          capacity: 10,
          available_capacity: 9,
          status: "STALE"
        }
      ]
    });

    const snapshot = store.getSnapshot();

    expect(snapshot.satellites.get("sat-1")).toMatchObject({
      sim_time: 10,
      position: [10, 0, 0],
      status: "online"
    });
    expect(snapshot.tasks.get("task-1")).toMatchObject({
      sim_time: 10,
      progress: 0.8,
      status: "RUNNING"
    });
    expect(snapshot.computeNodes.get("sat-1")).toMatchObject({
      sim_time: 10,
      available_capacity: 2,
      status: "BUSY"
    });
  });
});

function event(eventId: string, eventType: SimEvent["event_type"], payload: unknown): SimEvent {
  return {
    event_id: eventId,
    sim_time: 1,
    priority: 0,
    source: "test",
    target: "frontend",
    event_type: eventType,
    payload
  };
}
