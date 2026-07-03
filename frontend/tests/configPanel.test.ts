import { describe, expect, it } from "vitest";

import {
  generatedScenarioSummaryItems,
  pauseResumeControl,
  runtimeProgressSummary
} from "../src/config_panel/ConfigPanel";
import { GeneratedScenarioConfig } from "../src/core/event_types";

describe("generatedScenarioSummaryItems", () => {
  it("formats generated scenario config for the Chinese control panel", () => {
    const config: GeneratedScenarioConfig = {
      seed: 1234,
      satellite_count: 10000,
      user_count: 100000,
      compute_node_count: 64,
      flow_count: 1200,
      orbit_plane_count: 40,
      epoch: 0,
      semi_major_axis_km: 6921,
      eccentricity: 0,
      inclination_deg: 53.5,
      earth_radius_km: 6371,
      min_elevation_deg: 10,
      max_range_km: 2000,
      compute_capacity: 10,
      demand_capacity: 1,
      task_compute_demand: 20,
      task_data_size: 10
    };

    expect(generatedScenarioSummaryItems(config)).toEqual([
      { label: "生效卫星", value: "10,000" },
      { label: "生效用户", value: "100,000" },
      { label: "计算节点", value: "64" },
      { label: "业务流量", value: "1,200" },
      { label: "轨道面", value: "40" },
      { label: "随机种子", value: "1,234" },
      { label: "轨道高度", value: "550 km" },
      { label: "倾角", value: "53.5°" }
    ]);
  });

  it("shows a waiting state before initialization", () => {
    expect(generatedScenarioSummaryItems(null)).toEqual([
      { label: "生成场景", value: "等待初始化" }
    ]);
  });
});

describe("pauseResumeControl", () => {
  it("maps runtime state to Chinese pause and resume controls", () => {
    expect(pauseResumeControl(runtimeStatus("RUNNING"))).toEqual({
      label: "暂停",
      action: "PAUSE",
      disabled: false
    });
    expect(pauseResumeControl(runtimeStatus("PAUSED"))).toEqual({
      label: "继续",
      action: "RESUME",
      disabled: false
    });
    expect(pauseResumeControl(runtimeStatus("STOPPED"))).toEqual({
      label: "暂停",
      action: "PAUSE",
      disabled: true
    });
  });
});

describe("runtimeProgressSummary", () => {
  it("formats simulation progress for the Chinese control panel", () => {
    expect(
      runtimeProgressSummary({
        sim_time: 125,
        duration: 600,
        event_count: 12345
      })
    ).toEqual({
      elapsedLabel: "2分5秒",
      totalLabel: "10分0秒",
      eventCountLabel: "12,345",
      percent: 20.833333333333336,
      percentLabel: "20.83%"
    });
  });

  it("clamps progress to the configured duration", () => {
    expect(
      runtimeProgressSummary({
        sim_time: 900,
        duration: 600,
        event_count: 1
      }).percentLabel
    ).toBe("100%");
  });
});

function runtimeStatus(status: "RUNNING" | "PAUSED" | "STOPPED") {
  return {
    status,
    mode: status === "PAUSED" ? "PAUSED" : "REAL_TIME",
    speed_factor: 1,
    seed: 20260703,
    duration: 600,
    config_version: 1,
    last_action: status
  } as const;
}
