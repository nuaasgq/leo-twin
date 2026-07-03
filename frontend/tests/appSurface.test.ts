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
          network: {
            transport_protocol: "UDP",
            routing_protocol: "DISTANCE_VECTOR"
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
      network: {
        transport_protocol: "UDP",
        routing_protocol: "DISTANCE_VECTOR"
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
