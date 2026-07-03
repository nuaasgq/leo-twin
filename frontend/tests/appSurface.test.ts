import { describe, expect, it } from "vitest";

import {
  runtimeStatusRequiresStreams,
  scenarioWithRuntimeConfig,
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

describe("scenarioWithRuntimeConfig", () => {
  it("merges control-plane network and visualization config into the scenario", () => {
    expect(
      scenarioWithRuntimeConfig(
        {},
        {
          scenario: {
            compute_scheduling_policy: "EARLIEST_DEADLINE_FIRST"
          },
          network: {
            transport_protocol: "UDP",
            routing_protocol: "DISTANCE_VECTOR",
            carrier_frequency_hz: 22_000_000_000,
            channel_bandwidth_hz: 250_000_000,
            rain_rate_mm_h: 12,
            rain_attenuation_coefficient_db_per_km_per_mm_h: 0.01,
            rain_effective_path_km: 5,
            antenna_diameter_m: 0.55,
            antenna_aperture_efficiency: 0.7
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
        compute_scheduling_policy: "EARLIEST_DEADLINE_FIRST"
      },
      network: {
        transport_protocol: "UDP",
        routing_protocol: "DISTANCE_VECTOR",
        carrier_frequency_hz: 22_000_000_000,
        channel_bandwidth_hz: 250_000_000,
        rain_rate_mm_h: 12,
        rain_attenuation_coefficient_db_per_km_per_mm_h: 0.01,
        rain_effective_path_km: 5,
        antenna_diameter_m: 0.55,
        antenna_aperture_efficiency: 0.7
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
