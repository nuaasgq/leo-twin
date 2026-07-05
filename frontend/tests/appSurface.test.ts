import { describe, expect, it } from "vitest";

import {
  backpressureNoticeDismissKey,
  backpressureNoticeText,
  bodySurfaceAttribute,
  completionNoticeDismissKey,
  completionNoticeDetail,
  completionNoticeText,
  buildRuntimeRibbonSummary,
  buildSurfaceSyncSummary,
  connectionDiagnosticItems,
  controlErrorMessage,
  defaultRuntimeProgressAnchor,
  fidelityNoticeText,
  nextRuntimeProgressAnchor,
  runtimeProgressSimTime,
  runtimeWebSocketErrorMessage,
  runtimeStatusRequiresStreams,
  scenarioWithRuntimeConfig,
  selectRuntimeDisplayEventCount,
  selectRuntimeDisplaySimTime,
  selectFidelitySummary,
  shouldResetWorldBeforeStreamConnect,
  shouldShowBackpressureNotice,
  shouldShowRuntimeBackpressureNotice,
  shouldShowCompletionNotice,
  shouldShowFidelityNotice,
  standaloneDashboardHref,
  surfaceFromPathname
} from "../src/app/App";
import {
  runtimeEffectiveSpeedFactor,
  runtimeSpeedFactorLabel
} from "../src/runtime_display";
import {
  FidelitySummary,
  GeneratedScenarioConfig,
  RuntimeBackpressureSummary,
  RuntimeStatusPayload
} from "../src/core/event_types";
import { WorldSnapshot } from "../src/state/snapshot_engine";

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

describe("bodySurfaceAttribute", () => {
  it("keeps the body scroll mode tied to the active frontend surface", () => {
    expect(bodySurfaceAttribute("control")).toBe("control");
    expect(bodySurfaceAttribute("dashboard")).toBe("dashboard");
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

describe("buildSurfaceSyncSummary", () => {
  const baseStatus: RuntimeStatusPayload = {
    status: "RUNNING",
    mode: "ACCELERATED",
    speed_factor: 10,
    seed: 20260703,
    duration: 600,
    config_version: 2,
    last_action: "START",
    initialized: true
  };

  it("summarizes the shared console-dashboard display clock", () => {
    expect(
      buildSurfaceSyncSummary({
        displaySimTime: 130,
        snapshotSimTime: 125,
        eventCount: 12345,
        runtimeStatus: baseStatus
      })
    ).toEqual({
      displayTimeLabel: "显示 2分10秒",
      snapshotTimeLabel: "2分5秒",
      deltaLabel: "前端插值 +5秒",
      eventCountLabel: "12,345",
      statusLabel: "同步运行"
    });
  });

  it("labels paused and snapshot-leading sync states", () => {
    expect(
      buildSurfaceSyncSummary({
        displaySimTime: 118,
        snapshotSimTime: 120,
        eventCount: 42,
        runtimeStatus: { ...baseStatus, status: "PAUSED", last_action: "PAUSE" }
      })
    ).toMatchObject({
      deltaLabel: "快照领先 2秒",
      eventCountLabel: "42",
      statusLabel: "同步暂停"
    });
  });

  it("labels completed runtime sync states explicitly", () => {
    expect(
      buildSurfaceSyncSummary({
        displaySimTime: 600,
        snapshotSimTime: 600,
        eventCount: 100,
        runtimeStatus: {
          ...baseStatus,
          status: "COMPLETED",
          lifecycle_state: "COMPLETED",
          last_action: "START"
        }
      }).statusLabel
    ).toBe("同步完成");
  });

  it("prioritizes completed lifecycle over legacy running status", () => {
    expect(
      buildSurfaceSyncSummary({
        displaySimTime: 600,
        snapshotSimTime: 600,
        eventCount: 100,
        runtimeStatus: {
          ...baseStatus,
          status: "RUNNING",
          lifecycle_state: "COMPLETED",
          last_action: "START"
        }
      }).statusLabel
    ).toBe("同步完成");
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

describe("runtime speed display", () => {
  it("shows effective speed based on runtime mode", () => {
    expect(runtimeEffectiveSpeedFactor("REAL_TIME", 25)).toBe(1);
    expect(runtimeEffectiveSpeedFactor("ACCELERATED", 25)).toBe(25);
    expect(
      runtimeSpeedFactorLabel({
        status: "RUNNING",
        mode: "REAL_TIME",
        speed_factor: 25,
        seed: 20260703,
        duration: 600,
        config_version: 1,
        last_action: "START"
      })
    ).toBe("1x");
  });
});

describe("completion notice", () => {
  const completedStatus: RuntimeStatusPayload = {
    status: "COMPLETED",
    lifecycle_state: "COMPLETED",
    mode: "REAL_TIME",
    speed_factor: 1,
    seed: 20260703,
    duration: 600,
    config_version: 1,
    last_action: "START",
    current_sim_time: 600,
    processed_event_count: 128
  };

  it("shows an explicit completed runtime notice", () => {
    expect(shouldShowCompletionNotice(completedStatus)).toBe(true);
    expect(shouldShowCompletionNotice({ ...completedStatus, status: "RUNNING" })).toBe(true);
    expect(
      shouldShowCompletionNotice({
        ...completedStatus,
        status: "RUNNING",
        lifecycle_state: "RUNNING"
      })
    ).toBe(false);
    expect(completionNoticeText(completedStatus)).toContain("仿真已完成");
    expect(completionNoticeText(completedStatus)).toContain("配置时长");
    expect(completionNoticeDetail(completedStatus)).toContain("事件数 128");
    expect(completionNoticeDismissKey(completedStatus)).toBe(
      completionNoticeDismissKey({ ...completedStatus })
    );
    expect(completionNoticeDismissKey(completedStatus)).not.toBe(
      completionNoticeDismissKey({ ...completedStatus, processed_event_count: 256 })
    );
  });
});

describe("stream connection reset policy", () => {
  it("keeps the world state when attaching to an already running backend session", () => {
    expect(shouldResetWorldBeforeStreamConnect("ATTACH", 0)).toBe(false);
    expect(shouldResetWorldBeforeStreamConnect("RESUME", 100)).toBe(false);
  });

  it("resets only for a fresh START with no local stream history", () => {
    expect(shouldResetWorldBeforeStreamConnect("START", 0)).toBe(true);
    expect(shouldResetWorldBeforeStreamConnect("START", 25)).toBe(false);
  });
});

describe("fidelity notice", () => {
  const summary: FidelitySummary = {
    orbit_update_mode: "BATCH",
    metrics_mode: "AGGREGATED",
    space_link_mode: "BOUNDED_CANDIDATE",
    detailed_space_link_enabled: false,
    space_link_candidate_policy: "SAME_PLANE_AND_ADJACENT_PLANE_BOUNDED_CANDIDATES",
    max_space_link_candidates_per_satellite: 4,
    batch_space_link_update_limit: 999,
    scale_limit_reason:
      "orbit updates are batched; metrics are aggregated; bounded candidate updates are enabled",
    current_scale_mode: "LARGE_SCALE_AGGREGATED",
    fidelity_warnings: ["Orbit updates are batched."],
    satellite_count: 1200,
    user_count: 20
  };

  it("builds the visible scale notice from backend-provided fields", () => {
    expect(shouldShowFidelityNotice(summary)).toBe(true);
    expect(fidelityNoticeText(summary)).toBe(
      "规模模式：1,200 颗卫星。轨道更新采用批量模式。指标采用聚合模式。星间链路采用有界候选更新。"
    );
  });

  it("selects runtime status fidelity as the newest backend source of truth", () => {
    const fallback: FidelitySummary = {
      ...summary,
      satellite_count: 300,
      metrics_mode: "DETAILED"
    };
    const runtime: RuntimeStatusPayload = {
      status: "RUNNING",
      mode: "REAL_TIME",
      speed_factor: 1,
      seed: 20260703,
      duration: 600,
      config_version: 1,
      last_action: "START",
      fidelity_summary: summary
    };

    expect(
      selectFidelitySummary(
        runtime,
        { backend_summary: { fidelity_summary: fallback } } as unknown as GeneratedScenarioConfig,
        { fidelity_summary: fallback, scenario_config: null } as unknown as WorldSnapshot
      )
    ).toBe(summary);
  });
});

describe("backpressure notice", () => {
  const summary: RuntimeBackpressureSummary = {
    tick_duration_ms: 1234.4,
    tick_budget_ms: 1000,
    overloaded: true,
    queue_depth: 42,
    processed_event_count: 128,
    deferred_event_count: 42,
    first_tick_heavy: true,
    bottleneck_component: "flow_arrival_processing",
    recommended_action: "widen_initial_workload_smoothing_window"
  };

  it("renders overload text from backend-provided backpressure fields", () => {
    expect(shouldShowBackpressureNotice(summary)).toBe(true);
    expect(backpressureNoticeDismissKey(summary)).toContain("flow_arrival_processing");
    expect(backpressureNoticeText(summary)).toBe(
      "运行压力：最近推进 1,234.4 ms，预算 1,000 ms。瓶颈组件：flow_arrival_processing。"
    );
  });

  it("keeps the dismiss key stable across volatile tick samples", () => {
    expect(backpressureNoticeDismissKey(summary)).toBe(
      backpressureNoticeDismissKey({
        ...summary,
        tick_duration_ms: 1500,
        queue_depth: 64,
        processed_event_count: 256
      })
    );
  });

  it("changes the dismiss key when the backend reports a different bottleneck", () => {
    expect(backpressureNoticeDismissKey(summary)).not.toBe(
      backpressureNoticeDismissKey({
        ...summary,
        bottleneck_component: "stream_cursor_delivery"
      })
    );
  });

  it("does not show a warning when backend reports a healthy tick", () => {
    expect(
      shouldShowBackpressureNotice({
        ...summary,
        overloaded: false,
        first_tick_heavy: false
      })
    ).toBe(false);
  });

  it("suppresses stale pressure warnings after runtime completion or stop", () => {
    const runningStatus = {
      status: "RUNNING",
      lifecycle_state: "RUNNING",
      mode: "REAL_TIME",
      speed_factor: 1,
      seed: 20260703,
      duration: 600,
      config_version: 1,
      last_action: "START"
    } as RuntimeStatusPayload;

    expect(shouldShowRuntimeBackpressureNotice(runningStatus, summary)).toBe(true);
    expect(
      shouldShowRuntimeBackpressureNotice(
        {
          ...runningStatus,
          status: "COMPLETED",
          lifecycle_state: "COMPLETED"
        },
        summary
      )
    ).toBe(false);
    expect(
      shouldShowRuntimeBackpressureNotice(
        {
          ...runningStatus,
          status: "STOPPED",
          lifecycle_state: "STOPPED"
        },
        summary
      )
    ).toBe(false);
  });
});

describe("controlErrorMessage", () => {
  it("maps scale safety failures to an actionable Chinese message", () => {
    expect(controlErrorMessage("scale safety check failed: max_event_count")).toContain(
      "实时交互演示安全上限"
    );
  });
});

describe("runtimeWebSocketErrorMessage", () => {
  it("maps stream failures to launcher troubleshooting text", () => {
    expect(runtimeWebSocketErrorMessage("events")).toContain(
      "scripts\\sees_launcher.ps1 status"
    );
    expect(runtimeWebSocketErrorMessage("control")).toContain("restart_leo_twin.bat");
  });
});

describe("connectionDiagnosticItems", () => {
  it("maps channel health into compact topbar diagnostics", () => {
    expect(
      connectionDiagnosticItems({
        http: "live",
        control: "degraded",
        events: "connecting",
        state: "idle"
      })
    ).toEqual([
      { channel: "http", label: "HTTP", status: "live", statusLabel: "正常" },
      { channel: "control", label: "控制", status: "degraded", statusLabel: "异常" },
      { channel: "events", label: "事件", status: "connecting", statusLabel: "连接中" },
      { channel: "state", label: "状态", status: "idle", statusLabel: "空闲" }
    ]);
  });

  it("adds stream cursor details when backend diagnostics are available", () => {
    const items = connectionDiagnosticItems(
      {
        http: "live",
        control: "live",
        events: "live",
        state: "live"
      },
      {
        version: "v1",
        advance_loop_state: "RUNNING",
        tick_count: 12,
        event_stream: {
          name: "events",
          next_cursor: 4200,
          oldest_cursor: 4000,
          retained_count: 201,
          total_dropped_count: 0,
          max_items: 100000,
          max_batch_size: 100000,
          overflow_risk: false
        },
        state_stream: {
          name: "state",
          next_cursor: 88,
          oldest_cursor: 80,
          retained_count: 9,
          total_dropped_count: 3,
          max_items: 100000,
          max_batch_size: 100000,
          overflow_risk: true
        }
      }
    );

    expect(items[0]).toEqual({
      channel: "http",
      label: "HTTP",
      status: "live",
      statusLabel: "正常"
    });
    expect(items[1]).toMatchObject({
      channel: "control",
      label: "控制",
      status: "live",
      statusLabel: "正常",
      detail: "推进 12 tick"
    });
    expect(items[1].description).toContain("服务端推进循环 RUNNING");
    expect(items[1].description).toContain("事件数只统计离散仿真事件");
    expect(items[2]).toMatchObject({
      channel: "events",
      label: "事件",
      status: "live",
      statusLabel: "正常",
      detail: "游标 4,200 / 留存 201"
    });
    expect(items[2].description).toContain("事件流诊断");
    expect(items[2].description).toContain("浏览器消费游标尚未上报");
    expect(items[2].description).toContain("当前没有缓冲区溢出风险");
    expect(items[3]).toMatchObject({
      channel: "state",
      label: "状态",
      status: "live",
      statusLabel: "正常",
      detail: "游标 88 / 留存 9 / 丢弃 3"
    });
    expect(items[3].description).toContain("状态流诊断");
    expect(items[3].description).toContain("累计丢弃 3 条");
    expect(items[3].description).toContain("当前接近缓冲区上限");
  });

  it("compares backend stream cursors with frontend consumed cursors", () => {
    const items = connectionDiagnosticItems(
      {
        http: "live",
        control: "live",
        events: "live",
        state: "live"
      },
      {
        version: "v1",
        advance_loop_state: "RUNNING",
        tick_count: 12,
        event_stream: {
          name: "events",
          next_cursor: 4200,
          oldest_cursor: 4000,
          retained_count: 201,
          total_dropped_count: 0,
          max_items: 100000,
          max_batch_size: 100000,
          overflow_risk: false
        },
        state_stream: {
          name: "state",
          next_cursor: 88,
          oldest_cursor: 80,
          retained_count: 9,
          total_dropped_count: 3,
          max_items: 100000,
          max_batch_size: 100000,
          overflow_risk: true
        }
      },
      {
        events: 4100,
        state: 88
      }
    );

    expect(items[2]).toMatchObject({
      channel: "events",
      detail: "游标 4,200 / 留存 201 / 已收 4,100 / 滞后 100"
    });
    expect(items[2].description).toContain("浏览器已消费到 4,100，滞后 100 条");
    expect(items[3]).toMatchObject({
      channel: "state",
      detail: "游标 88 / 留存 9 / 已收 88 / 滞后 0 / 丢弃 3"
    });
    expect(items[3].description).toContain("浏览器已消费到 88，滞后 0 条");
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

  it("keeps the shared progress clock across dashboard attach route changes", () => {
    const first = defaultRuntimeProgressAnchor(runningStatus, 1_000);
    const attached = nextRuntimeProgressAnchor(
      first,
      2,
      { ...runningStatus, last_action: "REQUEST_STATUS" },
      3_000
    );

    expect(surfaceFromPathname("/dashboard")).toBe("dashboard");
    expect(surfaceFromPathname("/")).toBe("control");
    expect(shouldResetWorldBeforeStreamConnect("ATTACH", 0)).toBe(false);
    expect(attached).toBe(first);
    expect(selectRuntimeDisplaySimTime(runningStatus, 2, attached, 3_000)).toBe(4);
  });

  it("resets the shared display clock after reset or initialization", () => {
    const first = defaultRuntimeProgressAnchor(runningStatus, 1_000);
    const next = nextRuntimeProgressAnchor(
      first,
      0,
      {
        ...runningStatus,
        status: "STOPPED",
        lifecycle_state: "INITIALIZED",
        current_sim_time: 0,
        last_action: "RESET"
      },
      5_000
    );

    expect(next.simTime).toBe(0);
    expect(runtimeProgressSimTime(next, 6_000)).toBe(0);
  });

  it("immediately resets visible progress while a reset command is pending", () => {
    const first = defaultRuntimeProgressAnchor(runningStatus, 1_000);
    const pendingResetStatus: RuntimeStatusPayload = {
      ...runningStatus,
      last_action: "RESET_PENDING",
      current_sim_time: 120,
      processed_event_count: 900
    };
    const next = nextRuntimeProgressAnchor(first, 120, pendingResetStatus, 5_000);

    expect(next.simTime).toBe(0);
    expect(selectRuntimeDisplaySimTime(pendingResetStatus, 120, next, 6_000)).toBe(0);
    expect(selectRuntimeDisplayEventCount(pendingResetStatus, 900)).toBe(0);
  });

  it("uses runtime event counts only outside reset-like transitions", () => {
    expect(selectRuntimeDisplayEventCount({ ...runningStatus, processed_event_count: 80 }, 10)).toBe(
      80
    );
    expect(selectRuntimeDisplayEventCount(runningStatus, 10)).toBe(10);
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
            compute_cpu_gflops_fp64: 6,
            compute_gpu_tflops_fp32: 2.5,
            compute_gpu_tflops_fp16: 5,
            compute_npu_tops_int8: 12,
            compute_memory_gb: 32,
            compute_storage_gb: 512,
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
        compute_cpu_gflops_fp64: 6,
        compute_gpu_tflops_fp32: 2.5,
        compute_gpu_tflops_fp16: 5,
        compute_npu_tops_int8: 12,
        compute_memory_gb: 32,
        compute_storage_gb: 512,
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
