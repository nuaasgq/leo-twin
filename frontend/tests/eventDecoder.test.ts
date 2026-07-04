import { describe, expect, it } from "vitest";

import { decodeSimEvent, decodeStateSnapshot } from "../src/core/decoder";

describe("decodeSimEvent", () => {
  it("decodes supported SEES event payloads", () => {
    const event = decodeSimEvent({
      event_id: "orbit:0001",
      sim_time: 1.5,
      priority: 0,
      source: "orbit",
      target: "frontend",
      event_type: "ORBIT_UPDATE",
      payload: {
        satellite_id: "sat-001",
        sim_time: 1.5,
        position: [1, 2, 3],
        velocity: [0, 0, 1],
        status: "online"
      }
    });

    expect(event.event_type).toBe("ORBIT_UPDATE");
    expect(event.payload).toEqual({
      satellite_id: "sat-001",
      sim_time: 1.5,
      position: [1, 2, 3],
      velocity: [0, 0, 1],
      status: "online"
    });
  });

  it("rejects unsupported frontend event types", () => {
    expect(() =>
      decodeSimEvent({
        event_id: "flow:0001",
        sim_time: 0,
        priority: 0,
        source: "network",
        target: "frontend",
        event_type: "FLOW_ARRIVAL",
        payload: {}
      })
    ).toThrow("event_type is not supported");
  });

  it("decodes compute node update payloads", () => {
    const event = decodeSimEvent({
      event_id: "compute:0001",
      sim_time: 2,
      priority: 0,
      source: "compute",
      target: "frontend",
      event_type: "COMPUTE_NODE_UPDATE",
      payload: {
        node_id: "compute-01",
        sim_time: 2,
        capacity: 20,
        available_capacity: 5,
        status: "BUSY",
        load_ratio: 0.75
      }
    });

    expect(event.payload).toEqual({
      node_id: "compute-01",
      sim_time: 2,
      capacity: 20,
      available_capacity: 5,
      status: "BUSY",
      load_ratio: 0.75
    });
  });

  it("decodes backend fidelity summary on state snapshots", () => {
    const snapshot = decodeStateSnapshot({
      satellites: [],
      fidelity_summary: {
        orbit_update_mode: "BATCH",
        metrics_mode: "AGGREGATED",
        space_link_mode: "REDUCED_LARGE_BATCH",
        detailed_space_link_enabled: false,
        space_link_candidate_policy: "SPACE_GROUND_ONLY_WHEN_BATCH_EXCEEDS_LIMIT",
        scale_limit_reason: "orbit updates are batched",
        satellite_count: 1200,
        user_count: 20
      }
    });

    expect(snapshot.fidelity_summary).toMatchObject({
      orbit_update_mode: "BATCH",
      satellite_count: 1200
    });
  });
});
