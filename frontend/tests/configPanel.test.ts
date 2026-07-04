import { describe, expect, it } from "vitest";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";

import {
  ConfigPanel,
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
      "可视化图层",
      "网络协议栈与路由",
      "物理层与信道参数",
      "当前生效场景"
    ]);
  });
});

describe("ConfigPanel priority controls", () => {
  it("places runtime mode above simulation progress for first-touch control", () => {
    const markup = renderToStaticMarkup(
      createElement(ConfigPanel, {
        scenario: defaultScenario(),
        runtime: runtimeStatus("STOPPED", true),
        progress: {
          sim_time: 0,
          duration: 600,
          event_count: 0
        },
        generatedConfig: null,
        onRuntimeControl: () => undefined
      })
    );

    const modeIndex = markup.indexOf('id="runtime-mode"');
    const progressIndex = markup.indexOf('aria-label="仿真进度"');

    expect(modeIndex).toBeGreaterThan(-1);
    expect(progressIndex).toBeGreaterThan(-1);
    expect(modeIndex).toBeLessThan(progressIndex);
  });

  it("renders numeric inputs next to key range controls", () => {
    const markup = renderToStaticMarkup(
      createElement(ConfigPanel, {
        scenario: defaultScenario(),
        runtime: runtimeStatus("STOPPED", true),
        progress: {
          sim_time: 0,
          duration: 600,
          event_count: 0
        },
        generatedConfig: null,
        onRuntimeControl: () => undefined
      })
    );

    expect(markup).toContain('id="satellite-count-input"');
    expect(markup).toContain('id="user-count-input"');
    expect(markup).toContain('id="compute-node-count-input"');
    expect(markup).toContain('id="speed-factor-input"');
    expect(markup).toContain('id="duration-seconds-input"');
  });

  it("uses backend-provided compute node count instead of satellite count", () => {
    const markup = renderToStaticMarkup(
      createElement(ConfigPanel, {
        scenario: defaultScenario(),
        runtime: runtimeStatus("STOPPED", true),
        progress: {
          sim_time: 0,
          duration: 600,
          event_count: 0
        },
        generatedConfig: null,
        onRuntimeControl: () => undefined
      })
    );

    expect(markup).toContain('id="compute-node-count-input"');
    expect(markup).toContain('value="8"');
  });

  it("renders backend control errors near runtime controls", () => {
    const markup = renderToStaticMarkup(
      createElement(ConfigPanel, {
        scenario: defaultScenario(),
        runtime: runtimeStatus("STOPPED", true),
        progress: {
          sim_time: 0,
          duration: 600,
          event_count: 0
        },
        generatedConfig: null,
        controlError: "当前配置超出实时交互演示安全上限。",
        onRuntimeControl: () => undefined
      })
    );

    expect(markup).toContain('role="alert"');
    expect(markup).toContain("实时交互演示安全上限");
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
      noise_temperature_k: 310,
      backend_summary: {
        derived_constellation_summary: {
          profile: "STARLINK_SHELL_1_LIKE",
          satellite_count: 10000,
          plane_count: 40,
          satellites_per_plane: 250,
          satellites_per_plane_distribution: Array(40).fill(250),
          total_slots: 10000,
          plane_count_explicit: true,
          model_note: "Approximate Starlink Shell 1-like plane allocation; not exact Starlink fidelity.",
          altitude_m: 550000,
          inclination_deg: 53,
          raan_spacing_deg: 9,
          mean_anomaly_spacing_deg: 1.44,
          phase_policy: "SLOT_INDEX_PHASE_WITH_PLANE_OFFSET"
        },
        traffic_demand_summary: {
          traffic_class: "COMPUTE_SERVICE",
          destination_type: "COMPUTE_NODE",
          generated_flow_count: 1200,
          arrival_model: "DETERMINISTIC_INTERVAL",
          input_data_size_mb: 10,
          output_data_size_mb: 0,
          priority: 0,
          demand_capacity_mbps: 1,
          task_compute_demand: 20
        },
        compute_resource_summary: {
          resource_model: "ComputeResourceVector",
          node_role: "SATELLITE_HOSTED_COMPUTE",
          compute_node_count: 64,
          legacy_capacity_per_node: 10,
          cpu_gflops_fp32_per_node: 10,
          cpu_gflops_fp64_per_node: 0,
          gpu_tflops_fp32_per_node: 0,
          gpu_tflops_fp16_per_node: 0,
          npu_tops_int8_per_node: 0,
          memory_gb_per_node: 0,
          storage_gb_per_node: 0,
          total_cpu_gflops_fp32: 640,
          total_cpu_gflops_fp64: 0,
          total_gpu_tflops_fp32: 0,
          total_gpu_tflops_fp16: 0,
          total_npu_tops_int8: 0,
          total_memory_gb: 0,
          total_storage_gb: 0,
          capacity_unit: "GFLOPS FP32",
          compatibility_note: "Legacy scalar capacity maps to cpu_gflops_fp32."
        },
        coverage_beam_summary: {
          coverage_model: "DETERMINISTIC_GEOMETRIC_FOOTPRINT",
          selected_satellite_detail_mode: "SELECTED_SATELLITE_ONLY",
          beam_pattern: "CENTER_PLUS_HEX_RING_VISUAL_APPROXIMATION",
          default_beam_count: 7,
          beam_radius_m: 160_000,
          beam_length_m: 600_000,
          global_beam_render_limit: 1,
          model_note:
            "Selected-satellite beam cells are deterministic visual footprints; no RF propagation or antenna-pattern simulation is performed."
        },
        model_assumptions: [
          "Orbit allocation is deterministic and simplified; no SGP4 or external ephemeris is used."
        ]
      }
    };

    const items = generatedScenarioSummaryItems(config);

    expect(items).toContainEqual({ label: "生效卫星", value: "10,000" });
    expect(items).toContainEqual({ label: "算力卫星", value: "64" });
    expect(items).toContainEqual({ label: "星座剖面", value: "近似 Starlink Shell 1" });
    expect(items).toContainEqual({ label: "每面卫星", value: "250" });
    expect(items).toContainEqual({ label: "RAAN 间隔", value: "9°" });
    expect(items).toContainEqual({ label: "相位策略", value: "槽位相位 + 面偏置" });
    expect(items).toContainEqual({ label: "业务类型", value: "通信-计算服务" });
    expect(items).toContainEqual({ label: "业务流量", value: "1,200" });
    expect(items).toContainEqual({ label: "FP32 算力", value: "640 GFLOPS" });
    expect(items).toContainEqual({
      label: "模型假设",
      value: "Orbit allocation is deterministic and simp..."
    });
    expect(items).toContainEqual({ label: "轨道面", value: "40" });
    expect(items).toContainEqual({ label: "传输协议", value: "UDP" });
    expect(items).toContainEqual({ label: "轨道高度", value: "550 km" });
    expect(items).toContainEqual({ label: "GPU FP32", value: "0 TFLOPS" });
    expect(items).toContainEqual({ label: "GPU FP16", value: "0 TFLOPS" });
    expect(items).toContainEqual({ label: "NPU INT8", value: "0 TOPS" });
    expect(items).toContainEqual({ label: "内存/存储", value: "0 / 0 GB" });
    expect(items).toContainEqual({ label: "波束模式", value: "中心 + 六邻区蜂窝" });
    expect(items).toContainEqual({ label: "默认波束", value: "7 个" });
    expect(items).toContainEqual({ label: "波束半径", value: "160 km" });
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

function defaultScenario() {
  return {
    satellite_count: 120,
    user_count: 500,
    compute_nodes: 8,
    compute_capacity: 10,
    compute_scheduling_policy: "FIFO",
    orbit: {
      update_interval_seconds: 30,
      plane_count: 12,
      altitude_km: 550,
      inclination_deg: 53
    },
    traffic_model: {
      flow_interval_seconds: 30,
      task_interval_seconds: 30,
      flow_demand_capacity: 5,
      task_compute_demand: 10,
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
      transport_congestion_window_segments: 32,
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
  };
}
