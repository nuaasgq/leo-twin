import { describe, expect, it } from "vitest";

import {
  buildRuntimeRibbonSummary,
  defaultRuntimeProgressAnchor,
  nextRuntimeProgressAnchor,
  runtimeProgressSimTime,
  runtimeStatusRequiresStreams,
  scenarioWithRuntimeConfig,
  standaloneDashboardHref,
  surfaceFromPathname
} from "../src/app/App";
import { RuntimeStatusPayload } from "../src/core/event_types";

describe("surfaceFromPathname", () => {
  it("selects the control surface by default", () => {
    expect(surfaceFromPathname("/")).toBe("control");
    expect(surfaceFromPathname("/scenario")).toBe("control");
  });

  it("selects the standalone dashboard surface", () => {
    expect(surfaceFromPathname("/dashboard")).toBe("dashboard");
    expect(surfaceFromPathname("/dashboard/network")).toBe("dashboard");
  });
});

describe("standaloneDashboardHref", () => {
  it("builds a deterministic absolute dashboard URL", () => {
    expect(standaloneDashboardHref("http://127.0.0.1:5173")).toBe(
      "http://127.0.0.1:5173/dashboard"
    );
    expect(standaloneDashboardHref("http://127.0.0.1:5173/")).toBe(
      "http://127.0.0.1:5173/dashboard"
    );
  });
});

describe("buildRuntimeRibbonSummary", () => {
  it("summarizes the visible simulation process deterministically", () => {
    const summary = buildRuntimeRibbonSummary({
      simTime: 125,
      eventCount: 12345,
      runtimeStatus: {
        status: "RUNNING",
        mode: "ACCELERATED",
        speed_factor: 20,
        seed: 20260703,
        duration: 600,
        config_version: 2,
        last_action: "START",
        initialized: true
      },
      scenario: {
        satellite_count: 10000,
        user_count: 100000,
        compute_nodes: 64,
        compute_capacity: 10,
        compute_scheduling_policy: "FIFO",
        orbit: {
          update_interval_seconds: 60,
          plane_count: 40,
          altitude_km: 550,
          inclination_deg: 53
        },
        traffic_model: {
          flow_interval_seconds: 60,
          task_interval_seconds: 60,
          flow_demand_capacity: 25,
          task_compute_demand: 20,
          task_data_size: 2
        },
        visualization: {
          satellites: true,
          links: true,
          users: true,
          metrics: true
        },
        network: {
          application_protocol: "TASK_OFFLOAD_FLOW",
          transport_protocol: "TCP",
          transport_loss_rate: 0,
          transport_congestion_window_segments: 0,
          routing_protocol: "LINK_STATE",
          datalink_mac_protocol: "TDMA",
          routing_latency_weight: 1,
          routing_inverse_capacity_weight: 0,
          routing_hop_weight: 0,
          carrier_frequency_ghz: 20,
          channel_bandwidth_mhz: 100,
          rain_rate_mm_h: 0,
          rain_attenuation_coefficient_db_per_km_per_mm_h: 0,
          rain_effective_path_km: 0,
          antenna_diameter_m: 0.45,
          antenna_aperture_efficiency: 0.65,
          transmit_power_dbw: 20,
          system_loss_db: 1,
          noise_temperature_k: 290
        }
      }
    });

    expect(summary).toEqual({
      percent: 20.833333333333336,
      percentLabel: "20.8%",
      elapsedLabel: "2分5秒",
      durationLabel: "10分0秒",
      eventCountLabel: "12,345",
      satelliteCountLabel: "10,000",
      userCountLabel: "100,000"
    });
  });
});

describe("runtimeStatusRequiresStreams", () => {
  const baseStatus: RuntimeStatusPayload = {
    status: "STOPPED",
    mode: "REAL_TIME",
    speed_factor: 1,
    seed: 20260703,
    duration: 600,
    config_version: 1,
    last_action: "INIT"
  };

  it("reattaches frontend streams only when the runtime is running", () => {
    expect(runtimeStatusRequiresStreams({ ...baseStatus, status: "RUNNING" })).toBe(true);
    expect(runtimeStatusRequiresStreams({ ...baseStatus, status: "PAUSED" })).toBe(false);
    expect(runtimeStatusRequiresStreams({ ...baseStatus, status: "STOPPED" })).toBe(false);
    expect(runtimeStatusRequiresStreams(undefined)).toBe(false);
  });
});

describe("runtime progress clock", () => {
  const runningStatus: RuntimeStatusPayload = {
    status: "RUNNING",
    lifecycle_state: "RUNNING",
    mode: "REAL_TIME",
    speed_factor: 1,
    seed: 20260703,
    duration: 600,
    config_version: 1,
    last_action: "START",
    initialized: true,
    current_sim_time: 2
  };

  it("advances display progress between sparse event batches", () => {
    const anchor = defaultRuntimeProgressAnchor(runningStatus, 1_000);

    expect(runtimeProgressSimTime(anchor, 3_500)).toBe(4.5);
  });

  it("does not reset the display clock when polled status has the same sim time", () => {
    const first = defaultRuntimeProgressAnchor(runningStatus, 1_000);
    const next = nextRuntimeProgressAnchor(first, 2, runningStatus, 3_000);

    expect(next).toBe(first);
    expect(runtimeProgressSimTime(next, 3_000)).toBe(4);
  });

  it("stops requesting streams when the lifecycle is completed", () => {
    expect(
      runtimeStatusRequiresStreams({
        ...runningStatus,
        lifecycle_state: "COMPLETED"
      })
    ).toBe(false);
  });
});

describe("scenarioWithRuntimeConfig", () => {
  it("merges control-plane network and visualization config into the scenario", () => {
    expect(
      scenarioWithRuntimeConfig(
        {},
        {
          scenario: {
            compute_capacity: 18,
            compute_scheduling_policy: "EARLIEST_DEADLINE_FIRST",
            orbit: {
              update_interval_seconds: 30,
              plane_count: 24,
              altitude_m: 600_000,
              inclination_deg: 55
            },
            traffic_model: {
              flow_interval_seconds: 30,
              task_interval_seconds: 45,
              flow_demand_capacity: 12.5,
              task_compute_demand: 15,
              task_data_size: 4
            }
          },
          network: {
            application_protocol: "MQTT",
            transport_protocol: "UDP",
            transport_loss_rate: 0.025,
            transport_congestion_window_segments: 32,
            routing_protocol: "DISTANCE_VECTOR",
            datalink_mac_protocol: "CSMA_CA",
            routing_latency_weight: 0.2,
            routing_inverse_capacity_weight: 400,
            routing_hop_weight: 1,
            carrier_frequency_hz: 22_000_000_000,
            channel_bandwidth_hz: 250_000_000,
            rain_rate_mm_h: 12,
            rain_attenuation_coefficient_db_per_km_per_mm_h: 0.01,
            rain_effective_path_km: 5,
            antenna_diameter_m: 0.55,
            antenna_aperture_efficiency: 0.7,
            transmit_power_dbw: 23,
            system_loss_db: 1.5,
            noise_temperature_k: 310
          },
          ui: {
            visualization: {
              satellites: false,
              links: true,
              users: false,
              metrics: true
            }
          }
        }
      )
    ).toEqual({
      scenario: {
        compute_capacity: 18,
        compute_scheduling_policy: "EARLIEST_DEADLINE_FIRST",
        orbit: {
          update_interval_seconds: 30,
          plane_count: 24,
          altitude_m: 600_000,
          inclination_deg: 55
        },
        traffic_model: {
          flow_interval_seconds: 30,
          task_interval_seconds: 45,
          flow_demand_capacity: 12.5,
          task_compute_demand: 15,
          task_data_size: 4
        }
      },
      network: {
        application_protocol: "MQTT",
        transport_protocol: "UDP",
        transport_loss_rate: 0.025,
        transport_congestion_window_segments: 32,
        routing_protocol: "DISTANCE_VECTOR",
        datalink_mac_protocol: "CSMA_CA",
        routing_latency_weight: 0.2,
        routing_inverse_capacity_weight: 400,
        routing_hop_weight: 1,
        carrier_frequency_hz: 22_000_000_000,
        channel_bandwidth_hz: 250_000_000,
        rain_rate_mm_h: 12,
        rain_attenuation_coefficient_db_per_km_per_mm_h: 0.01,
        rain_effective_path_km: 5,
        antenna_diameter_m: 0.55,
        antenna_aperture_efficiency: 0.7,
        transmit_power_dbw: 23,
        system_loss_db: 1.5,
        noise_temperature_k: 310
      },
      ui: {
        visualization: {
          satellites: false,
          links: true,
          users: false,
          metrics: true
        }
      }
    });
  });
});
