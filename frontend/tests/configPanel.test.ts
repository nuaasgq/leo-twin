import { describe, expect, it } from "vitest";

import {
  configPanelSectionTitles,
  generatedScenarioSummaryItems,
  networkControlPayload,
  orbitControlPayload,
  pauseResumeControl,
  runtimeProgressSummary,
  startControlDisabled,
  trafficControlPayload,
  visualizationControlPayload
} from "../src/config_panel/ConfigPanel";
import { GeneratedScenarioConfig } from "../src/core/event_types";

describe("configPanelSectionTitles", () => {
  it("keeps the Chinese control panel grouped in an operational order", () => {
    expect(configPanelSectionTitles()).toEqual([
      "仿真执行控制",
      "场景规模与算力资源",
      "轨道参数",
      "业务流量与任务需求",
      "运行模式与可视化",
      "网络协议栈与路由",
      "物理层与信道参数",
      "当前生效场景"
    ]);
  });
});

describe("generatedScenarioSummaryItems", () => {
  it("formats generated scenario config for the Chinese control panel", () => {
    const config: GeneratedScenarioConfig = {
      seed: 1234,
      satellite_count: 10000,
      user_count: 100000,
      compute_node_count: 64,
      flow_count: 1200,
      compute_scheduling_policy: "SHORTEST_JOB_FIRST",
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
      task_data_size: 10,
      application_protocol: "MQTT",
      transport_protocol: "UDP",
      transport_loss_rate: 0.025,
      transport_congestion_window_segments: 32,
      routing_protocol: "DISTANCE_VECTOR",
      routing_latency_weight: 0.2,
      routing_inverse_capacity_weight: 400,
      routing_hop_weight: 1,
      carrier_frequency_hz: 22_000_000_000,
      channel_bandwidth_hz: 250_000_000,
      rain_rate_mm_h: 12.5,
      antenna_diameter_m: 0.6,
      antenna_aperture_efficiency: 0.7,
      transmit_power_dbw: 23,
      system_loss_db: 1.5,
      noise_temperature_k: 310
    };

    expect(generatedScenarioSummaryItems(config)).toEqual([
      { label: "生效卫星", value: "10,000" },
      { label: "生效用户", value: "100,000" },
      { label: "计算节点", value: "64" },
      { label: "业务流量", value: "1,200" },
      { label: "调度策略", value: "短作业优先" },
      { label: "轨道面", value: "40" },
      { label: "随机种子", value: "1,234" },
      { label: "应用协议", value: "MQTT" },
      { label: "传输协议", value: "UDP" },
      { label: "传输丢包", value: "2.5%" },
      { label: "拥塞窗口", value: "32 段" },
      { label: "路由协议", value: "DISTANCE_VECTOR" },
      { label: "路由权重", value: "时延 0.2 / 容量 400 / 跳数 1" },
      { label: "载波频率", value: "22 GHz" },
      { label: "信道带宽", value: "250 MHz" },
      { label: "雨强", value: "12.5 mm/h" },
      { label: "天线口径", value: "0.6 m" },
      { label: "孔径效率", value: "0.7" },
      { label: "发射功率", value: "23 dBW" },
      { label: "系统损耗", value: "1.5 dB" },
      { label: "噪声温度", value: "310 K" },
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

describe("startControlDisabled", () => {
  it("requires initialization before a stopped simulation can start", () => {
    expect(startControlDisabled(runtimeStatus("STOPPED", false))).toBe(true);
    expect(startControlDisabled(runtimeStatus("STOPPED", true))).toBe(false);
    expect(startControlDisabled(runtimeStatus("RUNNING", true))).toBe(true);
    expect(startControlDisabled(runtimeStatus("PAUSED", true))).toBe(true);
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

describe("visualizationControlPayload", () => {
  it("creates deterministic visualization update payloads", () => {
    expect(
      visualizationControlPayload({
        satellites: true,
        users: false,
        links: true,
        metrics: false
      })
    ).toEqual({
      satellites: true,
      links: true,
      users: false,
      metrics: false
    });
  });
});

describe("orbitControlPayload", () => {
  it("converts Chinese panel orbit units into control-plane fields", () => {
    expect(
      orbitControlPayload({
        update_interval_seconds: 30,
        plane_count: 24,
        altitude_km: 600,
        inclination_deg: 55
      })
    ).toEqual({
      update_interval_seconds: 30,
      plane_count: 24,
      altitude_m: 600_000,
      inclination_deg: 55
    });
  });
});

describe("trafficControlPayload", () => {
  it("creates deterministic traffic model payloads", () => {
    expect(
      trafficControlPayload({
        flow_interval_seconds: 30,
        task_interval_seconds: 45,
        flow_demand_capacity: 12.5,
        task_compute_demand: 15,
        task_data_size: 4
      })
    ).toEqual({
      flow_interval_seconds: 30,
      task_interval_seconds: 45,
      flow_demand_capacity: 12.5,
      task_compute_demand: 15,
      task_data_size: 4
    });
  });
});

describe("networkControlPayload", () => {
  it("converts Chinese panel units into deterministic control-plane fields", () => {
    expect(
      networkControlPayload({
        application_protocol: "MQTT",
        transport_protocol: "UDP",
        transport_loss_rate: 0.025,
        transport_congestion_window_segments: 32,
        routing_protocol: "DISTANCE_VECTOR",
        datalink_mac_protocol: "SLOTTED_ALOHA",
        routing_latency_weight: 0.2,
        routing_inverse_capacity_weight: 400,
        routing_hop_weight: 1,
        carrier_frequency_ghz: 22.5,
        channel_bandwidth_mhz: 250,
        rain_rate_mm_h: 8,
        rain_attenuation_coefficient_db_per_km_per_mm_h: 0.012,
        rain_effective_path_km: 4.5,
        antenna_diameter_m: 0.55,
        antenna_aperture_efficiency: 0.72,
        transmit_power_dbw: 23,
        system_loss_db: 1.5,
        noise_temperature_k: 310
      })
    ).toEqual({
      application_protocol: "MQTT",
      transport_protocol: "UDP",
      transport_loss_rate: 0.025,
      transport_congestion_window_segments: 32,
      routing_protocol: "DISTANCE_VECTOR",
      datalink_mac_protocol: "SLOTTED_ALOHA",
      routing_latency_weight: 0.2,
      routing_inverse_capacity_weight: 400,
      routing_hop_weight: 1,
      carrier_frequency_hz: 22_500_000_000,
      channel_bandwidth_hz: 250_000_000,
      rain_rate_mm_h: 8,
      rain_attenuation_coefficient_db_per_km_per_mm_h: 0.012,
      rain_effective_path_km: 4.5,
      antenna_diameter_m: 0.55,
      antenna_aperture_efficiency: 0.72,
      transmit_power_dbw: 23,
      system_loss_db: 1.5,
      noise_temperature_k: 310
    });
  });
});

function runtimeStatus(
  status: "RUNNING" | "PAUSED" | "STOPPED",
  initialized = true
) {
  return {
    status,
    mode: status === "PAUSED" ? "PAUSED" : "REAL_TIME",
    speed_factor: 1,
    seed: 20260703,
    duration: 600,
    config_version: 1,
    last_action: status,
    initialized
  } as const;
}
