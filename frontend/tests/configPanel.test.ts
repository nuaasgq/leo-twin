import { describe, expect, it } from "vitest";

import { generatedScenarioSummaryItems } from "../src/config_panel/ConfigPanel";
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
