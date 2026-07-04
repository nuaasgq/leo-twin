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
        load_ratio: 0.75,
        cpu_gflops_fp64: 8,
        gpu_tflops_fp32: 2.5,
        gpu_tflops_fp16: 5,
        npu_tops_int8: 12,
        memory_gb: 32,
        storage_gb: 512,
        resource_usage_mode: "RESOURCE_VECTOR_ESTIMATED",
        available_cpu_gflops_fp32: 10,
        used_cpu_gflops_fp32: 10,
        available_gpu_tflops_fp32: 0,
        used_gpu_tflops_fp32: 2.5,
        available_memory_gb: 24,
        used_memory_gb: 8,
        available_storage_gb: 500,
        used_storage_gb: 12
      }
    });

    expect(event.payload).toEqual({
      node_id: "compute-01",
      sim_time: 2,
      capacity: 20,
      available_capacity: 5,
      status: "BUSY",
      load_ratio: 0.75,
      cpu_gflops_fp64: 8,
      gpu_tflops_fp32: 2.5,
      gpu_tflops_fp16: 5,
      npu_tops_int8: 12,
      memory_gb: 32,
      storage_gb: 512,
      resource_usage_mode: "RESOURCE_VECTOR_ESTIMATED",
      available_cpu_gflops_fp32: 10,
      used_cpu_gflops_fp32: 10,
      available_gpu_tflops_fp32: 0,
      used_gpu_tflops_fp32: 2.5,
      available_memory_gb: 24,
      used_memory_gb: 8,
      available_storage_gb: 500,
      used_storage_gb: 12
    });
  });

  it("decodes route demand capacity from state snapshots", () => {
    const snapshot = decodeStateSnapshot({
      routes: [
        {
          route_id: "route-flow-a",
          flow_id: "flow-a",
          path: ["user-a", "sat-a", "user-b"],
          latency: 0.02,
          capacity: 100,
          available: true,
          demand_capacity: 90,
          loss_rate: 0.04
        }
      ]
    });

    expect(snapshot.routes?.[0]?.demand_capacity).toBe(90);
    expect(snapshot.routes?.[0]?.loss_rate).toBe(0.04);
  });

  it("decodes backend fidelity summary on state snapshots", () => {
    const snapshot = decodeStateSnapshot({
      satellites: [],
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
    });

    expect(snapshot.fidelity_summary).toMatchObject({
      orbit_update_mode: "BATCH",
      satellite_count: 1200
    });
  });
});
