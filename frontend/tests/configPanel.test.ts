import { describe, expect, it } from "vitest";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";

import {
  ConfigPanel,
  NETWORK_QUALITY_PRESETS,
  SCENARIO_SCALE_PRESETS,
  configurationTemplateProfileDetail,
  configurationTemplateSummaryItems,
  configPanelSectionTitles,
  generatedScenarioSummaryItems,
  initializationControlPayload,
  networkControlPayload,
  networkKeyControlPayload,
  orbitMotionExplanationItems,
  orbitControlPayload,
  pauseResumeControl,
  runtimeExecutionParameterLockReason,
  runtimeExecutionParametersLocked,
  runtimeProgressSummary,
  runtimeControlBusy,
  scalePresetSummaryItems,
  selectedNetworkQualityPreset,
  selectedScenarioScalePreset,
  startControlDisabled,
  trafficControlPayload,
  visualizationLayerEffectItems,
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

  it("locks execution parameters while the runtime is running", () => {
    const runningRuntime = runtimeStatus("RUNNING", true);
    const markup = renderToStaticMarkup(
      createElement(ConfigPanel, {
        scenario: defaultScenario(),
        runtime: runningRuntime,
        progress: {
          sim_time: 10,
          duration: 600,
          event_count: 5
        },
        generatedConfig: null,
        onRuntimeControl: () => undefined
      })
    );

    expect(runtimeExecutionParametersLocked(runningRuntime)).toBe(true);
    expect(markup).toMatch(/id="runtime-mode"[^>]*disabled=""/);
    expect(markup).toMatch(/id="speed-factor"[^>]*disabled=""/);
    expect(markup).toMatch(/id="speed-factor-input"[^>]*disabled=""/);
  });

  it("locks execution parameters after initialization before start", () => {
    const initializedRuntime = runtimeStatus("STOPPED", true);
    const editableRuntime = runtimeStatus("STOPPED", false);
    const markup = renderToStaticMarkup(
      createElement(ConfigPanel, {
        scenario: defaultScenario(),
        runtime: initializedRuntime,
        progress: {
          sim_time: 0,
          duration: 600,
          event_count: 0
        },
        generatedConfig: null,
        onRuntimeControl: () => undefined
      })
    );

    expect(runtimeExecutionParametersLocked(initializedRuntime)).toBe(true);
    expect(runtimeExecutionParameterLockReason(initializedRuntime)).toContain(
      "session 已初始化"
    );
    expect(runtimeExecutionParametersLocked(editableRuntime)).toBe(false);
    expect(markup).toContain("如需修改请先重置，再重新初始化");
    expect(markup).toMatch(/id="runtime-mode"[^>]*disabled=""/);
    expect(markup).toMatch(/id="duration-seconds-input"[^>]*disabled=""/);
  });

  it("pins speed controls to 1x in real-time mode", () => {
    const realtimeRuntime = {
      ...runtimeStatus("STOPPED", true),
      mode: "REAL_TIME",
      speed_factor: 25
    } as const;
    const markup = renderToStaticMarkup(
      createElement(ConfigPanel, {
        scenario: defaultScenario(),
        runtime: realtimeRuntime,
        progress: {
          sim_time: 0,
          duration: 600,
          event_count: 0
        },
        generatedConfig: null,
        onRuntimeControl: () => undefined
      })
    );

    expect(markup).toMatch(/id="speed-factor"(?=[^>]*disabled="")(?=[^>]*value="1")/);
    expect(markup).toMatch(/id="speed-factor-input"(?=[^>]*disabled="")(?=[^>]*value="1")/);
  });

  it("shows completed runtime status distinctly", () => {
    const markup = renderToStaticMarkup(
      createElement(ConfigPanel, {
        scenario: defaultScenario(),
        runtime: {
          status: "COMPLETED",
          lifecycle_state: "COMPLETED",
          mode: "REAL_TIME",
          speed_factor: 1,
          seed: 20260703,
          duration: 600,
          config_version: 1,
          last_action: "START",
          initialized: true
        },
        progress: {
          sim_time: 600,
          duration: 600,
          event_count: 100
        },
        generatedConfig: null,
        onRuntimeControl: () => undefined
      })
    );

    expect(markup).toContain("已完成");
  });

  it("shows completed when lifecycle is completed even if legacy status is running", () => {
    const markup = renderToStaticMarkup(
      createElement(ConfigPanel, {
        scenario: defaultScenario(),
        runtime: {
          ...runtimeStatus("RUNNING", true),
          lifecycle_state: "COMPLETED",
          current_sim_time: 600
        },
        progress: {
          sim_time: 600,
          duration: 600,
          event_count: 100
        },
        generatedConfig: null,
        onRuntimeControl: () => undefined
      })
    );

    expect(markup).toContain("已完成");
    expect(markup).not.toContain("运行中");
  });

  it("renders quick scale presets for 72, 300, and 1200 satellite scenarios", () => {
    expect(SCENARIO_SCALE_PRESETS.map((preset) => preset.satelliteCount)).toEqual([
      72,
      300,
      1200
    ]);
    expect(SCENARIO_SCALE_PRESETS.map((preset) => preset.computeNodeCount)).toEqual([
      72,
      300,
      1200
    ]);
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

    expect(markup).toContain('aria-label="场景规模预设"');
    expect(markup).toContain('aria-label="规模预设说明"');
    expect(markup).toContain("72 星");
    expect(markup).toContain("300 星");
    expect(markup).toContain("1200 星");
    expect(markup).toContain("规模稳定");
    expect(markup).toContain("自定义规模");
  });

  it("renders network quality presets for route-quality scenarios", () => {
    expect(NETWORK_QUALITY_PRESETS.map((preset) => preset.id)).toEqual([
      "stable-low-load",
      "congested-demand",
      "lossy-access",
      "delay-variation"
    ]);
    expect(
      selectedNetworkQualityPreset({
        flowDemandCapacity: NETWORK_QUALITY_PRESETS[2].flowDemandCapacity,
        applicationProtocol: NETWORK_QUALITY_PRESETS[2].applicationProtocol,
        transportProtocol: NETWORK_QUALITY_PRESETS[2].transportProtocol,
        transportLossRate: NETWORK_QUALITY_PRESETS[2].transportLossRate,
        transportCongestionWindowSegments:
          NETWORK_QUALITY_PRESETS[2].transportCongestionWindowSegments,
        routingProtocol: NETWORK_QUALITY_PRESETS[2].routingProtocol,
        datalinkMacProtocol: NETWORK_QUALITY_PRESETS[2].datalinkMacProtocol,
        routingLatencyWeight: NETWORK_QUALITY_PRESETS[2].routingLatencyWeight,
        routingInverseCapacityWeight:
          NETWORK_QUALITY_PRESETS[2].routingInverseCapacityWeight,
        routingHopWeight: NETWORK_QUALITY_PRESETS[2].routingHopWeight
      })?.id
    ).toBe("lossy-access");

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

    expect(markup).toContain('aria-label="网络质量预设"');
    expect(markup).toContain("稳定低负载");
    expect(markup).toContain("拥塞压力");
    expect(markup).toContain("有损接入");
    expect(markup).toContain("高时延波动");
  });

  it("renders compute resource vector inputs for satellite-hosted nodes", () => {
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

    expect(markup).toContain('id="compute-cpu-gflops-fp64"');
    expect(markup).toContain('id="compute-gpu-tflops-fp32"');
    expect(markup).toContain('id="compute-gpu-tflops-fp16"');
    expect(markup).toContain('id="compute-npu-tops-int8"');
    expect(markup).toContain('id="compute-memory-gb"');
    expect(markup).toContain('id="compute-storage-gb"');
  });

  it("renders orbit motion explanations near orbit controls", () => {
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

    expect(markup).toContain('aria-label="轨道运动说明"');
    expect(markup).toContain("采样步长");
    expect(markup).toContain("不代表卫星绕行周期");
    expect(markup).toContain("显示运动");
  });

  it("renders traffic mix controls from backend scenario fields", () => {
    const markup = renderToStaticMarkup(
      createElement(ConfigPanel, {
        scenario: {
          ...defaultScenario(),
          traffic_model: {
            ...defaultScenario().traffic_model,
            traffic_class: "BULK_DOWNLINK",
            destination_type: "GROUND_ENDPOINT",
            output_data_size: 3.5
          }
        },
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

    expect(markup).toContain('id="traffic-class"');
    expect(markup).toContain('value="BULK_DOWNLINK" selected');
    expect(markup).toContain('id="traffic-destination-type"');
    expect(markup).toContain('value="GROUND_ENDPOINT" selected');
    expect(markup).toContain('id="traffic-output-data-size"');
    expect(markup).toContain('value="3.5"');
  });

  it("locks compute-service traffic to compute-node destinations", () => {
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

    expect(markup).toContain('id="traffic-destination-type" disabled=""');
    expect(markup).toContain('value="COMPUTE_NODE" selected');
    expect(markup).toContain("初始化后显示后端业务约束摘要。");
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

  it("renders runtime action buttons disabled while a control command is pending", () => {
    const markup = renderToStaticMarkup(
      createElement(ConfigPanel, {
        scenario: defaultScenario(),
        runtime: {
          ...runtimeStatus("STOPPED", true),
          last_action: "START_PENDING"
        },
        progress: {
          sim_time: 0,
          duration: 600,
          event_count: 0
        },
        generatedConfig: null,
        onRuntimeControl: () => undefined
      })
    );

    expect(markup).toContain('<button type="button" disabled="">初始化</button>');
    expect(markup).toContain('<button type="button" disabled="">开始</button>');
    expect(markup).toContain('<button type="button" disabled="">停止</button>');
    expect(markup).toContain('<button type="button" disabled="">重置</button>');
  });
});

describe("scale preset summaries", () => {
  it("requires satellite, user, and compute counts to match the preset", () => {
    expect(
      selectedScenarioScalePreset({
        satelliteCount: 72,
        userCount: 1000,
        computeNodes: 72
      })?.id
    ).toBe("demo-72");

    expect(
      selectedScenarioScalePreset({
        satelliteCount: 72,
        userCount: 1000,
        computeNodes: 8
      })
    ).toBeNull();
  });

  it("shows preset expectations before backend initialization", () => {
    expect(
      scalePresetSummaryItems(
        {
          satelliteCount: 1200,
          userCount: 100,
          computeNodes: 1200
        },
        null
      )
    ).toEqual([
      { label: "规模预设", value: "1200 星 · 规模稳定" },
      { label: "预计拓扑", value: "大规模稳定性场景，卫星同时作为算力节点。" },
      {
        label: "预计保真",
        value: "预计启用批量轨道、聚合指标和有界星间链路候选。"
      }
    ]);
  });

  it("prefers backend-derived topology and fidelity after initialization", () => {
    const generatedConfig = {
      satellite_count: 1200,
      user_count: 100,
      compute_node_count: 1200,
      backend_summary: {
        derived_constellation_summary: {
          profile: "STARLINK_SHELL_1_LIKE",
          satellite_count: 1200,
          plane_count: 24,
          satellites_per_plane: 50,
          total_slots: 1200,
          plane_count_explicit: false,
          model_note: "Approximate Starlink-like deterministic allocation."
        },
        fidelity_summary: {
          orbit_update_mode: "BATCH",
          metrics_mode: "AGGREGATED",
          space_link_mode: "BOUNDED_CANDIDATE",
          detailed_space_link_enabled: false,
          space_link_candidate_policy: "SAME_PLANE_NEAREST_NEIGHBORS",
          max_space_link_candidates_per_satellite: 4,
          batch_space_link_update_limit: 5000,
          scale_limit_reason: "satellite_count>=1000",
          current_scale_mode: "LARGE_SCALE_AGGREGATED",
          fidelity_warnings: [],
          satellite_count: 1200,
          user_count: 100
        }
      }
    } as unknown as GeneratedScenarioConfig;

    expect(
      scalePresetSummaryItems(
        {
          satelliteCount: 1200,
          userCount: 100,
          computeNodes: 1200
        },
        generatedConfig
      )
    ).toEqual([
      { label: "后端轨道", value: "24 面 / 每面 50 星" },
      { label: "后端保真", value: "轨道 BATCH / 指标 AGGREGATED / 链路 BOUNDED_CANDIDATE" },
      { label: "后端说明", value: "Approximate Starlink-like deterministic al..." }
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
          orbital_period_minutes: 95.502118,
          orbital_period_model_note:
            "Simplified circular-orbit period estimate; no SGP4 or external ephemeris.",
          orbital_velocity_km_s: 7.588998,
          orbital_velocity_model_note:
            "Simplified circular-orbit speed estimate; no SGP4 or external ephemeris.",
          inclination_deg: 53,
          raan_spacing_deg: 9,
          mean_anomaly_spacing_deg: 1.44,
          phase_policy: "SLOT_INDEX_PHASE_WITH_PLANE_OFFSET"
        },
        traffic_demand_summary: {
          traffic_class: "COMPUTE_SERVICE",
          traffic_class_label: "通信-计算服务",
          destination_type: "COMPUTE_NODE",
          destination_type_label: "星上算力节点",
          generated_flow_count: 1200,
          arrival_model: "DETERMINISTIC_INTERVAL",
          input_data_size_mb: 10,
          output_data_size_mb: 0,
          priority: 0,
          demand_capacity_mbps: 1,
          task_compute_demand: 20,
          execution_shape: "FLOW_THEN_COMPUTE_TASK",
          execution_label: "输入流 + 计算任务",
          requires_compute_node_destination: true,
          compatibility_note: "通信-计算服务要求目的类型为星上算力节点。",
          lifecycle_note: "输入流完成后触发计算任务；输出数据大小作为结果流元数据保留。"
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
          fidelity_level: "DISPLAY_APPROXIMATION",
          footprint_intersection_policy: "VISUAL_GEOMETRIC_CONTAINMENT_ONLY",
          excluded_physics: [
            "RF_PROPAGATION",
            "ANTENNA_PATTERN",
            "LINK_BUDGET",
            "INTERFERENCE"
          ],
          default_beam_count: 7,
          beam_radius_m: 160_000,
          beam_length_m: 600_000,
          global_beam_render_limit: 1,
          model_note:
            "Selected-satellite beam cells are deterministic visual footprints; no RF propagation or antenna-pattern simulation is performed.",
          intersection_note:
            "Coverage/user intersections are deterministic geometric containment counts for visualization only; they are not access decisions."
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
    expect(items).toContainEqual({ label: "目的类型", value: "星上算力节点" });
    expect(items).toContainEqual({ label: "输入数据", value: "10 MB" });
    expect(items).toContainEqual({ label: "输出数据", value: "0 MB" });
    expect(items).toContainEqual({ label: "执行形态", value: "输入流 + 计算任务" });
    expect(items).toContainEqual({
      label: "业务约束",
      value: "通信-计算服务要求目的类型为星上算力节点。"
    });
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
    expect(items).toContainEqual({ label: "覆盖保真", value: "显示近似" });
    expect(items).toContainEqual({ label: "足迹交集", value: "仅视觉几何包含" });
    expect(items).toContainEqual({ label: "轨道周期", value: "95.5 min" });
    expect(items).toContainEqual({ label: "轨道速度", value: "7.59 km/s" });
  });

  it("shows a waiting state before initialization", () => {
    expect(generatedScenarioSummaryItems(null)).toEqual([
      { label: "生成场景", value: "等待初始化" }
    ]);
  });
});

describe("configurationTemplateSummaryItems", () => {
  it("maps backend template profiles into frontend display rows", () => {
    const config = {
      backend_summary: {
        configuration_surface_summary: {
          version: "v1",
          source: "backend_sees_config",
          detailed_config_file: "configs/sees_control.yaml",
          template_config_file: "configs/templates/sees_user_detailed.example.yaml",
          frontend_policy: "CONTROL_PANEL_KEY_FIELDS_ONLY",
          key_field_count: 29,
          detailed_field_count: 75,
          key_fields: [],
          detailed_file_sections: [],
          file_only_sections: [
            {
              section: "scenario.traffic_model",
              purpose: "Flow-level user business generation model.",
              field_count: 4,
              example_paths: [
                "scenario.traffic_model.data_transfer_weight",
                "scenario.traffic_model.telemetry_weight"
              ]
            },
            {
              section: "network",
              purpose: "Flow-level protocol, link budget, routing, and ISL fidelity inputs.",
              field_count: 10,
              example_paths: ["network.carrier_frequency_hz", "network.channel_bandwidth_hz"]
            }
          ],
          file_only_fields: [],
          template_profiles: [
            {
              id: "baseline_72sat",
              label: "72-satellite baseline",
              path: "configs/templates/sees_user_detailed.example.yaml",
              purpose: "Executable baseline for full-contract editing.",
              scale: "72 satellites, 72 compute nodes, baseline user demand.",
              expected_kpi_behavior: "Stable baseline KPI curves.",
              fidelity_mode: "SMALL_SCALE_PER_SATELLITE_ORBIT",
              recommended_use: "Start here for deterministic smoke tests."
            },
            {
              id: "dynamic_observability_120sat",
              label: "120-satellite dynamic observability",
              path: "configs/templates/sees_user_dynamic_observability.example.yaml",
              purpose: "Mixed traffic and non-zero network proxies.",
              scale: "120 satellites, 120 compute nodes.",
              expected_kpi_behavior: "Visible time-varying KPI movement.",
              fidelity_mode: "MEDIUM_SCALE_DYNAMIC_OBSERVABILITY",
              recommended_use: "Use for dashboard validation."
            }
          ]
        }
      }
    } as unknown as GeneratedScenarioConfig;

    expect(configurationTemplateSummaryItems(config)).toEqual([
      {
        label: "详细配置文件",
        value: "configs/sees_control.yaml",
        detail: "运行态生成配置，不应作为产品提交。"
      },
      {
        label: "前端配置策略",
        value: "CONTROL_PANEL_KEY_FIELDS_ONLY",
        detail: "29 个关键字段 / 75 个完整字段"
      },
      {
        label: "YAML 专用：业务生成",
        value: "4 个字段",
        detail:
          "Flow-level user business generation model. 示例：scenario.traffic_model.data_transfer_weight, scenario.traffic_model.telemetry_weight"
      },
      {
        label: "YAML 专用：网络",
        value: "10 个字段",
        detail:
          "Flow-level protocol, link budget, routing, and ISL fidelity inputs. 示例：network.carrier_frequency_hz, network.channel_bandwidth_hz"
      },
      {
        label: "72-satellite baseline",
        value: "configs/templates/sees_user_detailed.example.yaml",
        detail:
          "Executable baseline for full-contract editing. | 规模: 72 satellites, 72 compute nodes, baseline user demand. | 保真: SMALL_SCALE_PER_SATELLITE_ORBIT | KPI: Stable baseline KPI curves. | 用途: Start here for deterministic smoke tests.",
        templateId: "baseline_72sat"
      },
      {
        label: "120-satellite dynamic observability",
        value: "configs/templates/sees_user_dynamic_observability.example.yaml",
        detail:
          "Mixed traffic and non-zero network proxies. | 规模: 120 satellites, 120 compute nodes. | 保真: MEDIUM_SCALE_DYNAMIC_OBSERVABILITY | KPI: Visible time-varying KPI movement. | 用途: Use for dashboard validation.",
        templateId: "dynamic_observability_120sat"
      }
    ]);
  });

  it("summarizes backend template metadata for users", () => {
    expect(
      configurationTemplateProfileDetail({
        purpose: "Stress route pressure.",
        scale: "120 satellites",
        fidelity_mode: "MEDIUM_SCALE_NETWORK_STRESS",
        expected_kpi_behavior: "Loss and jitter proxies move over time.",
        recommended_use: "Use for KPI provenance checks."
      })
    ).toBe(
      "Stress route pressure. | 规模: 120 satellites | 保真: MEDIUM_SCALE_NETWORK_STRESS | KPI: Loss and jitter proxies move over time. | 用途: Use for KPI provenance checks."
    );
    expect(configurationTemplateProfileDetail({ purpose: "Baseline." })).toBe(
      "Baseline."
    );
  });

  it("renders backend template profiles in the control panel", () => {
    const generatedConfig = {
      seed: 20260705,
      satellite_count: 120,
      user_count: 600,
      compute_node_count: 120,
      flow_count: 60,
      orbit_plane_count: 12,
      epoch: 0,
      semi_major_axis_km: 6900,
      eccentricity: 0,
      inclination_deg: 53,
      earth_radius_km: 6371,
      min_elevation_deg: 10,
      max_range_km: 2000,
      compute_capacity: 40,
      demand_capacity: 180,
      task_compute_demand: 60,
      task_data_size: 16,
      backend_summary: {
        configuration_surface_summary: {
          version: "v1",
          source: "backend_sees_config",
          detailed_config_file: "configs/sees_control.yaml",
          template_config_file: "configs/templates/sees_user_detailed.example.yaml",
          frontend_policy: "CONTROL_PANEL_KEY_FIELDS_ONLY",
          key_field_count: 29,
          detailed_field_count: 75,
          key_fields: [],
          detailed_file_sections: [],
          file_only_sections: [
            {
              section: "network",
              purpose: "Flow-level protocol, link budget, routing, and ISL fidelity inputs.",
              field_count: 10,
              example_paths: ["network.carrier_frequency_hz"]
            }
          ],
          file_only_fields: [],
          template_profiles: [
            {
              id: "dynamic_observability_120sat",
              label: "120-satellite dynamic observability",
              path: "configs/templates/sees_user_dynamic_observability.example.yaml",
              purpose: "Mixed traffic and non-zero network proxies."
            }
          ]
        }
      }
    } as unknown as GeneratedScenarioConfig;

    const markup = renderToStaticMarkup(
      createElement(ConfigPanel, {
        scenario: defaultScenario(),
        runtime: runtimeStatus("STOPPED", true),
        progress: {
          sim_time: 0,
          duration: 600,
          event_count: 0
        },
        generatedConfig,
        onRuntimeControl: () => undefined
      })
    );

    expect(markup).toContain("详细配置模板");
    expect(markup).toContain("YAML 专用：网络");
    expect(markup).toContain("network.carrier_frequency_hz");
    expect(markup).toContain("120-satellite dynamic observability");
    expect(markup).toContain("configs/templates/sees_user_dynamic_observability.example.yaml");
    expect(markup).toContain("加载模板");
    expect(markup).toContain('data-template-id="dynamic_observability_120sat"');
  });

  it("returns no template rows before initialization", () => {
    expect(configurationTemplateSummaryItems(null)).toEqual([]);
  });
});

describe("orbitMotionExplanationItems", () => {
  it("uses backend-provided period and velocity when available", () => {
    expect(
      orbitMotionExplanationItems({
        updateIntervalSeconds: 10,
        altitudeM: 550_000,
        orbitalPeriodMinutes: 95.502118,
        orbitalVelocityKmS: 7.588998
      })
    ).toEqual([
      {
        label: "采样步长",
        value: "10 s",
        detail: "控制后端轨道状态刷新频率，不代表卫星绕行周期"
      },
      {
        label: "近圆轨道",
        value: "7.59 km/s",
        detail: "约 95.5 min 完成一圈，低轨卫星不是几分钟绕地一圈"
      },
      {
        label: "显示运动",
        value: "573 点/圈",
        detail: "前端在轨道样本之间插值/跟随，流畅度还受直播批量与渲染帧率影响"
      }
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

  it("disables pause and resume controls while a runtime command is pending", () => {
    expect(
      pauseResumeControl({
        ...runtimeStatus("RUNNING"),
        last_action: "PAUSE_PENDING"
      })
    ).toEqual({
      label: "暂停",
      action: "PAUSE",
      disabled: true
    });
    expect(
      pauseResumeControl({
        ...runtimeStatus("PAUSED"),
        last_action: "RESUME_PENDING"
      })
    ).toEqual({
      label: "继续",
      action: "RESUME",
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

  it("keeps start disabled during command pending transitions", () => {
    expect(
      startControlDisabled({
        ...runtimeStatus("STOPPED", true),
        last_action: "START_PENDING"
      })
    ).toBe(true);
  });
});

describe("runtimeControlBusy", () => {
  it("detects frontend-side pending control transitions", () => {
    expect(runtimeControlBusy(runtimeStatus("STOPPED", true))).toBe(false);
    expect(
      runtimeControlBusy({
        ...runtimeStatus("RUNNING", true),
        last_action: "STOP_PENDING"
      })
    ).toBe(true);
    expect(
      runtimeControlBusy({
        ...runtimeStatus("STOPPED", true),
        last_action: "RESET_PENDING"
      })
    ).toBe(true);
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

describe("visualizationLayerEffectItems", () => {
  it("explains what each visualization switch changes in the 3D view", () => {
    expect(
      visualizationLayerEffectItems({
        satellites: true,
        users: false,
        links: true,
        metrics: false
      })
    ).toEqual([
      {
        label: "卫星",
        stateLabel: "显示",
        detail: "控制卫星点、卫星图标和三维卫星模型"
      },
      {
        label: "用户",
        stateLabel: "隐藏",
        detail: "控制地面用户与地面站点"
      },
      {
        label: "链路",
        stateLabel: "显示",
        detail: "控制接入链路、星间链路和路由线"
      },
      {
        label: "轨迹",
        stateLabel: "隐藏",
        detail: "控制轨道轨迹、覆盖波束和路由辅助层"
      }
    ]);
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
        task_data_size: 4,
        traffic_class: "BULK_DOWNLINK",
        destination_type: "GROUND_ENDPOINT",
        output_data_size: 3.5
      })
    ).toEqual({
      flow_interval_seconds: 30,
      task_interval_seconds: 45,
      flow_demand_capacity: 12.5,
      task_compute_demand: 15,
      task_data_size: 4,
      traffic_class: "BULK_DOWNLINK",
      destination_type: "GROUND_ENDPOINT",
      output_data_size: 3.5
    });
  });
});

describe("initializationControlPayload", () => {
  it("sends the full compute resource vector in initialization payloads", () => {
    const payload = initializationControlPayload({
      satellite_count: 120,
      user_count: 500,
      compute_nodes: 120,
      compute_capacity: 40,
      compute_cpu_gflops_fp64: 8,
      compute_gpu_tflops_fp32: 2.5,
      compute_gpu_tflops_fp16: 5,
      compute_npu_tops_int8: 12,
      compute_memory_gb: 32,
      compute_storage_gb: 512,
      compute_scheduling_policy: "FIFO",
      mode: "ACCELERATED",
      speed_factor: 10,
      duration: 900,
      seed: 1234,
      orbit: {
        update_interval_seconds: 30,
        plane_count: 12,
        altitude_km: 550,
        inclination_deg: 53
      },
      traffic_model: {
        flow_interval_seconds: 20,
        task_interval_seconds: 30,
        flow_demand_capacity: 80,
        task_compute_demand: 60,
        task_data_size: 16,
        traffic_class: "COMPUTE_SERVICE",
        destination_type: "COMPUTE_NODE",
        output_data_size: 4
      },
      visualization: {
        satellites: true,
        links: true,
        users: true,
        metrics: true
      },
      network: {
        application_protocol: "MQTT",
        transport_protocol: "UDP",
        transport_loss_rate: 0.03,
        transport_congestion_window_segments: 64,
        routing_protocol: "DISTANCE_VECTOR",
        datalink_mac_protocol: "SLOTTED_ALOHA",
        routing_latency_weight: 0.2,
        routing_inverse_capacity_weight: 400,
        routing_hop_weight: 1,
        carrier_frequency_ghz: 22,
        channel_bandwidth_mhz: 250,
        rain_rate_mm_h: 8,
        rain_attenuation_coefficient_db_per_km_per_mm_h: 0.012,
        rain_effective_path_km: 4,
        antenna_diameter_m: 0.55,
        antenna_aperture_efficiency: 0.72,
        transmit_power_dbw: 23,
        system_loss_db: 1.5,
        noise_temperature_k: 310
      }
    });

    expect(payload).toMatchObject({
      satellite_count: 120,
      user_count: 500,
      compute_nodes: 120,
      compute_capacity: 40,
      compute_cpu_gflops_fp64: 8,
      compute_gpu_tflops_fp32: 2.5,
      compute_gpu_tflops_fp16: 5,
      compute_npu_tops_int8: 12,
      compute_memory_gb: 32,
      compute_storage_gb: 512,
      mode: "ACCELERATED",
      speed_factor: 10,
      duration: 900,
      seed: 1234,
      application_protocol: "MQTT",
      transport_protocol: "UDP",
      transport_loss_rate: 0.03,
      transport_congestion_window_segments: 64,
      routing_protocol: "DISTANCE_VECTOR",
      datalink_mac_protocol: "SLOTTED_ALOHA"
    });
    expect(payload.orbit).toEqual({
      update_interval_seconds: 30,
      plane_count: 12,
      altitude_m: 550_000,
      inclination_deg: 53
    });
    expect(payload.traffic_model).toEqual({
      flow_interval_seconds: 20,
      task_interval_seconds: 30,
      flow_demand_capacity: 80,
      task_compute_demand: 60,
      task_data_size: 16,
      traffic_class: "COMPUTE_SERVICE",
      destination_type: "COMPUTE_NODE",
      output_data_size: 4
    });
    expect(payload).not.toHaveProperty("routing_latency_weight");
    expect(payload).not.toHaveProperty("carrier_frequency_hz");
    expect(payload).not.toHaveProperty("rain_rate_mm_h");
  });

  it("normalizes speed factor by runtime mode for initialization", () => {
    const scenario = defaultScenario();
    expect(
      initializationControlPayload({
        ...scenario,
        mode: "REAL_TIME",
        speed_factor: 25,
        duration: 600,
        seed: 20260705
      }).speed_factor
    ).toBe(1);
    expect(
      initializationControlPayload({
        ...scenario,
        mode: "ACCELERATED",
        speed_factor: 25,
        duration: 600,
        seed: 20260705
      }).speed_factor
    ).toBe(25);
  });
});

describe("networkKeyControlPayload", () => {
  it("keeps initialization network updates to protocol and quality keys", () => {
    expect(
      networkKeyControlPayload({
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
      datalink_mac_protocol: "SLOTTED_ALOHA"
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
    compute_cpu_gflops_fp64: 4,
    compute_gpu_tflops_fp32: 2,
    compute_gpu_tflops_fp16: 4,
    compute_npu_tops_int8: 16,
    compute_memory_gb: 32,
    compute_storage_gb: 512,
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
