import { describe, expect, it } from "vitest";

import {
  buildComputeResourcePool,
  buildDataPanelConfiguredScale,
  buildDataPanelDisplaySummary,
  buildDataPanelNetworkFormulaInputs,
  buildDataPanelNetworkKpiCaveats,
  buildDataPanelNetworkKpiSource,
  buildDataPanelRouteConstraints,
  buildDataPanelRuntimeProgress,
  buildDataPanelSummary,
  buildDataPanelTelemetry,
  buildDataPanelTrafficDisplay,
  buildTopComputeNodeRows,
  resolveNetworkQualityKpis
} from "../src/dashboard/data_panel/DataPanel";
import { FidelitySummary, GeneratedScenarioConfig } from "../src/core/event_types";
import { WorldSnapshot } from "../src/state/snapshot_engine";

describe("buildDataPanelSummary", () => {
  it("summarizes orbit-network-compute telemetry for the standalone data panel", () => {
    const snapshot = makeSnapshot({
      last_sim_time: 24,
      event_count: 120,
      satellites: [
        {
          satellite_id: "sat-a",
          sim_time: 24,
          position: [1, 2, 3],
          status: "ACTIVE"
        },
        {
          satellite_id: "sat-b",
          sim_time: 24,
          position: [4, 5, 6],
          status: "ACTIVE"
        }
      ],
      ground_users: [
        {
          user_id: "user-a",
          status: "ACTIVE"
        }
      ],
      links: [
        {
          source_id: "sat-a",
          target_id: "sat-b",
          latency: 0.1,
          capacity: 100,
          availability: true
        },
        {
          source_id: "sat-a",
          target_id: "user-a",
          latency: 0.2,
          capacity: 40,
          availability: true
        },
        {
          source_id: "sat-b",
          target_id: "user-b",
          latency: 0.3,
          capacity: 20,
          availability: false
        }
      ],
      routes: [
        {
          route_id: "route-a",
          flow_id: "task-a",
          path: ["user-a", "sat-a", "compute-a"],
          latency: 0.8,
          capacity: 30,
          available: true
        },
        {
          route_id: "route-b",
          flow_id: "task-b",
          path: ["user-b", "sat-b", "sat-a", "compute-a"],
          latency: 1.2,
          capacity: 10,
          available: true
        },
        {
          route_id: "route-c",
          flow_id: "task-c",
          path: [],
          latency: 0,
          capacity: 0,
          available: false
        }
      ],
      active_tasks: [
        {
          task_id: "task-a",
          node_id: "compute-a",
          sim_time: 24,
          progress: 0.5,
          status: "RUNNING"
        }
      ],
      compute_nodes: [
        {
          node_id: "compute-a",
          running_tasks: 1,
          finished_tasks: 2,
          capacity: 20,
          available_capacity: 4,
          status: "BUSY",
          load_ratio: 0.8
        }
      ],
      metrics_summary: {
        network: {
          latency: 0.2,
          throughput: 140,
          linkUtilization: 0.5,
          series: []
        },
        compute: {
          taskQueueLength: 1,
          executionSuccessRate: 0.8,
          runningTasks: 1,
          finishedTasks: 2,
          deadlineMissedTasks: 1
        },
        orbit: {
          activeSatellites: 2,
          coverageRatio: 1,
          series: []
        },
        system: {
          eventRate: 5,
          systemLoad: 0.1,
          eventSeries: []
        }
      }
    });

    expect(buildDataPanelSummary(snapshot)).toEqual({
      simTime: 24,
      eventCount: 120,
      eventRate: 5,
      satelliteCount: 2,
      groundUserCount: 1,
      activeLinks: 2,
      spaceLinks: 1,
      accessLinks: 1,
      availableRoutes: 2,
      totalRoutes: 3,
      routeAvailabilityPercent: 67,
      averageRouteLatency: 1,
      averageRouteCapacity: 20,
      averageRouteHops: 2.5,
      maxRouteHops: 3,
      runningTasks: 1,
      finishedTasks: 2,
      deadlineMissedTasks: 1,
      computeNodes: 1,
      networkWaiting: 1,
      couplingHealth: 100
    });
  });

  it("returns bounded zero values for an empty snapshot", () => {
    const summary = buildDataPanelSummary(makeSnapshot());

    expect(summary.routeAvailabilityPercent).toBe(0);
    expect(summary.averageRouteLatency).toBe(0);
    expect(summary.averageRouteCapacity).toBe(0);
    expect(summary.averageRouteHops).toBe(0);
    expect(summary.maxRouteHops).toBe(0);
    expect(summary.couplingHealth).toBe(0);
  });
});

describe("buildDataPanelRouteConstraints", () => {
  it("builds deterministic route constraint rows from snapshot links and routes", () => {
    expect(
      buildDataPanelRouteConstraints(
        makeSnapshot({
          links: [
            {
              source_id: "sat-a",
              target_id: "sat-b",
              latency: 0.1,
              capacity: 80,
              availability: true
            },
            {
              source_id: "sat-b",
              target_id: "sat-c",
              latency: 0.3,
              capacity: 20,
              availability: true
            },
            {
              source_id: "sat-c",
              target_id: "sat-d",
              latency: 0.2,
              capacity: 50,
              availability: true
            }
          ],
          routes: [
            {
              route_id: "route-good",
              flow_id: "flow-good",
              path: ["sat-a", "sat-b", "sat-c"],
              latency: 0.4,
              capacity: 20,
              available: true,
              demand_capacity: 25,
              loss_rate: 0.05
            },
            {
              route_id: "route-low",
              flow_id: "flow-low",
              path: ["sat-a", "sat-b"],
              latency: 0.1,
              capacity: 80,
              available: true
            },
            {
              route_id: "route-down",
              flow_id: "flow-down",
              path: [],
              latency: 0,
              capacity: 0,
              available: false
            }
          ]
        })
      )
    ).toEqual({
      sourceLabel: "快照路由明细",
      items: [
        {
          routeId: "route-down",
          flowId: "flow-down",
          statusLabel: "不可用",
          hopCount: 0,
          latencyLabel: "0 s",
          capacityLabel: "0 Mbps",
          demandLossLabel: "未声明",
          bottleneckLabel: "无可用路径",
          pathLabel: "无路径"
        },
        {
          routeId: "route-good",
          flowId: "flow-good",
          statusLabel: "可用",
          hopCount: 2,
          latencyLabel: "0.4 s",
          capacityLabel: "20 Mbps",
          demandLossLabel: "需求25 Mbps / 损耗5%",
          bottleneckLabel: "sat-b → sat-c / 20 Mbps / 0.3 s",
          pathLabel: "sat-a → sat-b → sat-c"
        },
        {
          routeId: "route-low",
          flowId: "flow-low",
          statusLabel: "可用",
          hopCount: 1,
          latencyLabel: "0.1 s",
          capacityLabel: "80 Mbps",
          demandLossLabel: "未声明",
          bottleneckLabel: "sat-a → sat-b / 80 Mbps / 0.1 s",
          pathLabel: "sat-a → sat-b"
        }
      ]
    });
  });

  it("prefers backend route constraint summary when available", () => {
    expect(
      buildDataPanelRouteConstraints(makeSnapshot(), {
        network_constraint_summary_source: "BACKEND_METRICS_COLLECTOR",
        network_constraint_top_route_id: "route-backend",
        network_constraint_top_route_flow_id: "flow-backend",
        network_constraint_top_route_available: false,
        network_constraint_top_route_capacity_mbps: 0,
        network_constraint_top_route_latency_s: 0.125,
        network_constraint_top_route_hop_count: 3,
        network_constraint_top_route_demand_mbps: 40,
        network_constraint_top_route_loss_rate: 0.08,
        network_constraint_top_route_pressure_proxy: 1,
        network_constraint_top_route_path: "user-a -> sat-a -> sat-b -> user-b",
        network_constraint_top_link_id: "sat-a->sat-b",
        network_constraint_top_link_capacity_mbps: 20,
        network_constraint_top_link_latency_s: 0.05,
        network_constraint_top_link_utilization: 0.92
      })
    ).toEqual({
      sourceLabel: "后端约束摘要",
      items: [
        {
          routeId: "route-backend",
          flowId: "flow-backend",
          statusLabel: "不可用",
          hopCount: 3,
          latencyLabel: "0.125 s",
          capacityLabel: "0 Mbps",
          demandLossLabel: "需求40 Mbps / 损耗8% / 压力100%",
          bottleneckLabel: "sat-a->sat-b / 20 Mbps / 0.05 s / 利用率92%",
          pathLabel: "user-a -> sat-a -> sat-b -> user-b"
        }
      ]
    });
  });

  it("returns no route constraint rows for an empty snapshot", () => {
    expect(buildDataPanelRouteConstraints(makeSnapshot())).toEqual({
      sourceLabel: "快照路由明细",
      items: []
    });
  });
});

describe("buildDataPanelDisplaySummary", () => {
  it("uses the shared frontend display clock for dashboard-console sync", () => {
    const summary = buildDataPanelSummary(
      makeSnapshot({
        last_sim_time: 12,
        event_count: 30
      })
    );

    expect(buildDataPanelDisplaySummary(summary, 18.5, 42)).toMatchObject({
      simTime: 18.5,
      eventCount: 42
    });
  });

  it("never moves dashboard values backwards when snapshots are newer", () => {
    const summary = buildDataPanelSummary(
      makeSnapshot({
        last_sim_time: 24,
        event_count: 120
      })
    );

    expect(buildDataPanelDisplaySummary(summary, 18, 42)).toMatchObject({
      simTime: 24,
      eventCount: 120
    });
  });
});

describe("buildDataPanelRuntimeProgress", () => {
  it("formats the standalone data panel simulation progress", () => {
    expect(buildDataPanelRuntimeProgress(3661, 7200)).toEqual({
      percent: 50.84722222222222,
      percentLabel: "50.8%",
      elapsedLabel: "1时1分",
      durationLabel: "2时0分"
    });
  });

  it("clamps the data panel progress to the configured duration", () => {
    expect(buildDataPanelRuntimeProgress(900, 600).percentLabel).toBe("100%");
  });
});

describe("buildDataPanelConfiguredScale", () => {
  const fidelitySummary: FidelitySummary = {
    orbit_update_mode: "BATCH",
    metrics_mode: "AGGREGATED",
    space_link_mode: "BOUNDED_CANDIDATE",
    detailed_space_link_enabled: false,
    space_link_candidate_policy: "SAME_PLANE_AND_ADJACENT_PLANE_BOUNDED_CANDIDATES",
    max_space_link_candidates_per_satellite: 4,
    batch_space_link_update_limit: 999,
    scale_limit_reason: "large scale",
    current_scale_mode: "LARGE_SCALE_AGGREGATED",
    fidelity_warnings: [],
    satellite_count: 1200,
    user_count: 100
  };

  it("uses backend-derived constellation summary when generated config is available", () => {
    const generatedConfig = {
      satellite_count: 1200,
      user_count: 100,
      orbit_plane_count: 40,
      backend_summary: {
        derived_constellation_summary: {
          profile: "STARLINK_SHELL_1_LIKE",
          satellite_count: 1200,
          plane_count: 40,
          satellites_per_plane: 30,
          total_slots: 1200,
          plane_count_explicit: false,
          model_note: "Approximate Starlink Shell 1-like plane allocation."
        },
        fidelity_summary: fidelitySummary
      }
    } as GeneratedScenarioConfig;

    expect(buildDataPanelConfiguredScale(generatedConfig, fidelitySummary)).toBe(
      "1,200 星 / 40 面 / 30 星/面 / 100 用户 / 大规模聚合"
    );
  });

  it("falls back to runtime fidelity summary before initialization config is present", () => {
    expect(buildDataPanelConfiguredScale(null, fidelitySummary)).toBe(
      "1,200 星 / 100 用户 / 大规模聚合"
    );
  });

  it("shows waiting text when no backend scale source exists yet", () => {
    expect(buildDataPanelConfiguredScale(null, null)).toBe("等待初始化");
  });
});

describe("buildDataPanelTrafficDisplay", () => {
  it("uses backend traffic labels and lifecycle notes", () => {
    expect(
      buildDataPanelTrafficDisplay({
        traffic_class: "SCIENCE_PAYLOAD",
        traffic_class_label: "科学载荷业务",
        destination_type: "PAYLOAD_ENDPOINT",
        destination_type_label: "载荷端点",
        generated_flow_count: 12,
        arrival_model: "DETERMINISTIC_INTERVAL",
        input_data_size_mb: 10,
        output_data_size_mb: 1,
        priority: 0,
        demand_capacity_mbps: 25,
        task_compute_demand: 20,
        execution_shape: "PAYLOAD_FLOW_ONLY",
        execution_label: "载荷数据流",
        requires_compute_node_destination: false,
        compatibility_note: "后端声明该业务不触发算力任务。",
        lifecycle_note: "载荷数据流完成即完成业务。"
      })
    ).toEqual({
      label: "科学载荷业务 / 载荷端点 / 载荷数据流",
      note: "载荷数据流完成即完成业务。"
    });
  });

  it("falls back to deterministic labels for older backend summaries", () => {
    expect(
      buildDataPanelTrafficDisplay({
        traffic_class: "BULK_DOWNLINK",
        destination_type: "GROUND_ENDPOINT",
        generated_flow_count: 12,
        arrival_model: "DETERMINISTIC_INTERVAL",
        input_data_size_mb: 10,
        output_data_size_mb: 1,
        priority: 0,
        demand_capacity_mbps: 25,
        task_compute_demand: 20
      })
    ).toEqual({
      label: "批量下传 / 地面端 / 仅网络流",
      note: null
    });
  });
});

describe("buildDataPanelNetworkKpiSource", () => {
  it("reports backend runtime KPI time series as the preferred source", () => {
    expect(
      buildDataPanelNetworkKpiSource(
        makeSnapshot(),
        {
          network_quality_proxy_note:
            "Flow-level proxy only; no packet-level simulation is performed."
        },
        {
          version: "v1",
          sample_count: 1,
          tail_sample_source: "CURRENT_METRICS_SUMMARY",
          tail_sample_source_label: "当前指标摘要同步",
          samples: [
            {
              sim_time: 10,
              network_effective_throughput_mbps: 150,
              network_effective_latency_s: 0.11,
              network_effective_loss_proxy_rate: 0.04,
              network_effective_delay_variation_s: 0.006,
              compute_resource_used_gflops_fp32: 2500
            }
          ]
        }
      )
    ).toEqual({
      sourceLabel: "后端实时 KPI 序列",
      modelNote: "后端流级代理指标；未进行包级仿真。",
      caveats: ["尾点：当前指标摘要同步"]
    });
  });

  it("reports backend metric summaries before frontend snapshot estimates", () => {
    expect(
      buildDataPanelNetworkKpiSource(makeSnapshot(), {
        network_quality_effective_throughput_mbps: 77,
        network_quality_effective_latency_avg_s: 0.15
      })
    ).toEqual({
      sourceLabel: "后端指标摘要",
      modelNote: "后端网络质量指标为流级代理模型；未进行包级仿真。",
      caveats: []
    });
  });

  it("includes backend KPI provenance labels when available", () => {
    expect(
      buildDataPanelNetworkKpiSource(makeSnapshot(), {
        network_quality_proxy_note:
          "Flow-level proxy only; no packet-level simulation is performed.",
        network_quality_effective_throughput_mbps: 77,
        network_quality_effective_latency_avg_s: 0.15,
        network_quality_throughput_source_label: "已完成流容量",
        network_quality_latency_source_label: "已完成流时延",
        network_quality_loss_source_label: "业务压力损耗代理",
        network_quality_delay_variation_source_label: "流完成时延离散度",
        network_quality_metric_model: "FLOW_LEVEL_PROXY",
        network_quality_loss_zero_reason_label:
          "路由阻塞、失败流、链路拥塞和业务压力均未触发损耗代理",
        network_quality_delay_variation_zero_reason_label:
          "时延样本不足，无法形成离散度代理"
      })
    ).toEqual({
      sourceLabel: "后端指标摘要",
      modelNote:
        "后端流级代理指标；未进行包级仿真。 来源：吞吐量 已完成流容量；时延 已完成流时延；丢包 业务压力损耗代理；抖动 流完成时延离散度。",
      caveats: [
        "指标模型：后端流级代理",
        "丢包率：路由阻塞、失败流、链路拥塞和业务压力均未触发损耗代理",
        "抖动：时延样本不足，无法形成离散度代理"
      ]
    });
  });

  it("reports snapshot KPI series when runtime series is absent", () => {
    expect(
      buildDataPanelNetworkKpiSource(
        makeSnapshot({
          metrics_summary: {
            network: {
              latency: 0,
              throughput: 0,
              linkUtilization: 0,
              series: [],
              kpiSeries: [
                {
                  simTime: 10,
                  throughputMbps: 80,
                  latencyMs: 70,
                  lossPercent: 1,
                  jitterMs: 2
                }
              ]
            },
            compute: {
              taskQueueLength: 0,
              executionSuccessRate: 1,
              runningTasks: 0,
              finishedTasks: 0,
              deadlineMissedTasks: 0
            },
            orbit: {
              activeSatellites: 0,
              coverageRatio: 0,
              series: []
            },
            system: {
              eventRate: 1,
              systemLoad: 0,
              eventSeries: [{ index: 0, simTime: 10 }]
            }
          }
        })
      )
    ).toEqual({
      sourceLabel: "状态快照 KPI 序列",
      modelNote: "后端网络质量指标为流级代理模型；未进行包级仿真。",
      caveats: []
    });
  });

  it("marks fallback estimates when backend network quality is absent", () => {
    expect(buildDataPanelNetworkKpiSource(makeSnapshot())).toEqual({
      sourceLabel: "前端快照估算",
      modelNote: "未收到后端网络质量指标时，根据快照链路与路由做显示估算。",
      caveats: []
    });
  });
});

describe("buildDataPanelNetworkKpiCaveats", () => {
  it("maps backend KPI semantic fields into compact dashboard caveats", () => {
    expect(
      buildDataPanelNetworkKpiCaveats(
        {
          network_quality_metric_model: "FLOW_LEVEL_PROXY",
          network_quality_loss_zero_reason_label:
            "路由阻塞、失败流、链路拥塞和业务压力均未触发损耗代理",
          network_quality_delay_variation_zero_reason_label:
            "时延样本不足，无法形成离散度代理"
        },
        {
          version: "v1",
          sample_count: 1,
          tail_sample_source: "CURRENT_METRICS_SUMMARY",
          tail_sample_source_label: "当前指标摘要同步",
          samples: [
            {
              sim_time: 10,
              network_effective_throughput_mbps: 150,
              network_effective_latency_s: 0.11,
              network_effective_loss_proxy_rate: 0.04,
              network_effective_delay_variation_s: 0.006,
              compute_resource_used_gflops_fp32: 2500
            }
          ]
        }
      )
    ).toEqual([
      "指标模型：后端流级代理",
      "丢包率：路由阻塞、失败流、链路拥塞和业务压力均未触发损耗代理",
      "抖动：时延样本不足，无法形成离散度代理",
      "尾点：当前指标摘要同步"
    ]);
  });

  it("does not warn on positive backend proxy values", () => {
    expect(
      buildDataPanelNetworkKpiCaveats({
        network_quality_metric_model: "FLOW_LEVEL_PROXY",
        network_quality_loss_zero_reason_label: "当前代理指标为正值",
        network_quality_delay_variation_zero_reason_label: "当前代理指标为正值"
      })
    ).toEqual(["指标模型：后端流级代理"]);
  });
});

describe("buildDataPanelNetworkFormulaInputs", () => {
  it("formats backend network KPI formula inputs for dashboard display", () => {
    expect(
      buildDataPanelNetworkFormulaInputs({
        network_quality_requested_route_demand_mbps: 90,
        network_quality_offered_route_capacity_mbps: 100,
        network_quality_flow_delivered_capacity_mbps: 88,
        network_quality_route_loss_proxy_rate: 0.12,
        network_quality_congestion_proxy: 0.95,
        network_quality_demand_pressure_proxy: 0.9
      })
    ).toEqual([
      { label: "请求需求", value: "90 Mbps" },
      { label: "路由容量", value: "100 Mbps" },
      { label: "完成流容量", value: "88 Mbps" },
      { label: "路由损耗", value: "12%" },
      { label: "拥塞代理", value: "95%" },
      { label: "业务压力", value: "90%" }
    ]);
  });

  it("hides formula inputs when backend metrics are absent", () => {
    expect(buildDataPanelNetworkFormulaInputs(null)).toEqual([]);
  });
});

describe("resolveNetworkQualityKpis", () => {
  it("converts backend seconds and rates into dashboard display units", () => {
    expect(
      resolveNetworkQualityKpis(makeSnapshot(), {
        network_quality_effective_throughput_mbps: 77,
        network_quality_effective_latency_avg_s: 0.15,
        network_quality_effective_loss_proxy_rate: 0.07,
        network_quality_effective_delay_variation_proxy_s: 0.009
      })
    ).toEqual({
      source: "后端指标摘要",
      throughputMbps: 77,
      latencyMs: 150,
      lossPercent: 7,
      jitterMs: 9
    });
  });

  it("treats zero delivered throughput as incomplete and falls back to available capacity", () => {
    expect(
      resolveNetworkQualityKpis(makeSnapshot(), {
        network_quality_estimated_delivered_throughput_mbps: 0,
        network_quality_estimated_available_throughput_mbps: 88,
        network_quality_offered_route_capacity_mbps: 100,
        network_quality_route_latency_avg_s: 0.12,
        network_quality_loss_proxy_rate: 0.05,
        network_quality_delay_variation_proxy_s: 0.003
      })
    ).toMatchObject({
      source: "后端指标摘要",
      throughputMbps: 88,
      latencyMs: 120,
      lossPercent: 5,
      jitterMs: 3
    });
  });

  it("falls back to snapshot link and route estimates when backend metrics are absent", () => {
    expect(
      resolveNetworkQualityKpis(
        makeSnapshot({
          links: [
            {
              source_id: "sat-a",
              target_id: "sat-b",
              latency: 10,
              capacity: 40,
              availability: true
            },
            {
              source_id: "sat-b",
              target_id: "sat-c",
              latency: 20,
              capacity: 60,
              availability: true
            },
            {
              source_id: "sat-c",
              target_id: "sat-d",
              latency: 30,
              capacity: 0,
              availability: false
            }
          ]
        })
      )
    ).toMatchObject({
      source: "前端快照估算",
      throughputMbps: 100,
      latencyMs: 15,
      lossPercent: 3.333,
      jitterMs: 5
    });
  });
});

describe("buildDataPanelTelemetry", () => {
  it("builds deterministic time-varying network and FP32 compute series", () => {
    const snapshot = makeSnapshot({
      last_sim_time: 30,
      links: [
        {
          source_id: "sat-a",
          target_id: "sat-b",
          latency: 10,
          capacity: 100,
          availability: true
        },
        {
          source_id: "sat-a",
          target_id: "user-a",
          latency: 20,
          capacity: 50,
          availability: true
        }
      ],
      compute_nodes: [
        {
          node_id: "sat-a",
          running_tasks: 1,
          finished_tasks: 0,
          capacity: 20,
          available_capacity: 5,
          status: "BUSY",
          load_ratio: 0.75
        }
      ],
      scenario_config: {
        network: {
          transport_loss_rate: 0.02
        }
      },
      metrics_summary: {
        network: {
          latency: 15,
          throughput: 150,
          linkUtilization: 0.5,
          series: []
        },
        compute: {
          taskQueueLength: 1,
          executionSuccessRate: 1,
          runningTasks: 1,
          finishedTasks: 0,
          deadlineMissedTasks: 0
        },
        orbit: {
          activeSatellites: 2,
          coverageRatio: 1,
          series: []
        },
        system: {
          eventRate: 2,
          systemLoad: 0.2,
          eventSeries: [
            { index: 0, simTime: 10 },
            { index: 1, simTime: 20 },
            { index: 2, simTime: 30 }
          ]
        }
      }
    });

    const telemetry = buildDataPanelTelemetry(snapshot, 30);

    expect(telemetry).toHaveLength(3);
    expect(telemetry.map((point) => point.timeLabel)).toEqual(["10秒", "20秒", "30秒"]);
    expect(telemetry[2]).toMatchObject({
      throughputMbps: 150,
      latencyMs: 15,
      lossPercent: 2,
      jitterMs: 5,
      computeUsedTflops: 15
    });
    expect(telemetry[0].throughputMbps).toBeLessThan(telemetry[2].throughputMbps);
  });

  it("uses backend network KPI series directly when present", () => {
    const telemetry = buildDataPanelTelemetry(
      makeSnapshot({
        last_sim_time: 20,
        metrics_summary: {
          network: {
            latency: 0,
            throughput: 0,
            linkUtilization: 0,
            series: [],
            kpiSeries: [
              {
                simTime: 10,
                throughputMbps: 80,
                latencyMs: 70,
                lossPercent: 1,
                jitterMs: 2
              },
              {
                simTime: 20,
                throughputMbps: 120,
                latencyMs: 90,
                lossPercent: 3,
                jitterMs: 5
              }
            ]
          },
          compute: {
            taskQueueLength: 0,
            executionSuccessRate: 1,
            runningTasks: 0,
            finishedTasks: 0,
            deadlineMissedTasks: 0
          },
          orbit: {
            activeSatellites: 0,
            coverageRatio: 0,
            series: []
          },
          system: {
            eventRate: 1,
            systemLoad: 0,
            eventSeries: [{ index: 0, simTime: 20 }]
          }
        }
      }),
      20
    );

    expect(telemetry).toHaveLength(2);
    expect(telemetry[0]).toMatchObject({
      throughputMbps: 80,
      latencyMs: 70,
      lossPercent: 1,
      jitterMs: 2
    });
    expect(telemetry[1]).toMatchObject({
      throughputMbps: 120,
      latencyMs: 90,
      lossPercent: 3,
      jitterMs: 5
    });
  });

  it("prefers runtime backend KPI time series over snapshot metric series", () => {
    const telemetry = buildDataPanelTelemetry(
      makeSnapshot({
        metrics_summary: {
          network: {
            latency: 0,
            throughput: 0,
            linkUtilization: 0,
            series: [],
            kpiSeries: [
              {
                simTime: 10,
                throughputMbps: 80,
                latencyMs: 70,
                lossPercent: 1,
                jitterMs: 2
              }
            ]
          },
          compute: {
            taskQueueLength: 0,
            executionSuccessRate: 1,
            runningTasks: 0,
            finishedTasks: 0,
            deadlineMissedTasks: 0
          },
          orbit: {
            activeSatellites: 0,
            coverageRatio: 0,
            series: []
          },
          system: {
            eventRate: 1,
            systemLoad: 0,
            eventSeries: [{ index: 0, simTime: 10 }]
          }
        }
      }),
      10,
      undefined,
      {
        version: "v1",
        sample_count: 1,
        samples: [
          {
            sim_time: 20,
            network_effective_throughput_mbps: 150,
            network_effective_latency_s: 0.11,
            network_effective_loss_proxy_rate: 0.04,
            network_effective_delay_variation_s: 0.006,
            compute_resource_used_gflops_fp32: 2500
          }
        ]
      }
    );

    expect(telemetry).toHaveLength(1);
    expect(telemetry[0]).toMatchObject({
      simTime: 20,
      throughputMbps: 150,
      latencyMs: 110,
      lossPercent: 4,
      jitterMs: 6,
      computeUsedTflops: 2.5
    });
  });

  it("prefers backend-owned runtime metrics for network quality telemetry", () => {
    const telemetry = buildDataPanelTelemetry(
      makeSnapshot({
        last_sim_time: 10,
        metrics_summary: {
          network: {
            latency: 0,
            throughput: 0,
            linkUtilization: 0,
            series: []
          },
          compute: {
            taskQueueLength: 0,
            executionSuccessRate: 1,
            runningTasks: 0,
            finishedTasks: 0,
            deadlineMissedTasks: 0
          },
          orbit: {
            activeSatellites: 0,
            coverageRatio: 0,
            series: []
          },
          system: {
            eventRate: 1,
            systemLoad: 0,
            eventSeries: [{ index: 0, simTime: 10 }]
          }
        }
      }),
      10,
      {
        network_quality_estimated_delivered_throughput_mbps: 42,
        network_quality_estimated_available_throughput_mbps: 99,
        network_quality_route_latency_avg_s: 0.12,
        network_quality_loss_proxy_rate: 0.05,
        network_quality_delay_variation_proxy_s: 0.003,
        compute_resource_used_gflops_fp32: 1500
      }
    );

    expect(telemetry[0]).toMatchObject({
      throughputMbps: 42,
      latencyMs: 120,
      lossPercent: 5,
      jitterMs: 3,
      computeUsedTflops: 1.5
    });
  });

  it("prefers backend effective network quality fields when available", () => {
    const telemetry = buildDataPanelTelemetry(
      makeSnapshot({
        last_sim_time: 10,
        metrics_summary: {
          network: {
            latency: 0,
            throughput: 0,
            linkUtilization: 0,
            series: []
          },
          compute: {
            taskQueueLength: 0,
            executionSuccessRate: 1,
            runningTasks: 0,
            finishedTasks: 0,
            deadlineMissedTasks: 0
          },
          orbit: {
            activeSatellites: 0,
            coverageRatio: 0,
            series: []
          },
          system: {
            eventRate: 1,
            systemLoad: 0,
            eventSeries: [{ index: 0, simTime: 10 }]
          }
        }
      }),
      10,
      {
        network_quality_estimated_delivered_throughput_mbps: 42,
        network_quality_effective_throughput_mbps: 77,
        network_quality_route_latency_avg_s: 0.12,
        network_quality_effective_latency_avg_s: 0.15,
        network_quality_loss_proxy_rate: 0.01,
        network_quality_effective_loss_proxy_rate: 0.07,
        network_quality_delay_variation_proxy_s: 0.003,
        network_quality_effective_delay_variation_proxy_s: 0.009
      }
    );

    expect(telemetry[0]).toMatchObject({
      throughputMbps: 77,
      latencyMs: 150,
      lossPercent: 7,
      jitterMs: 9
    });
  });

  it("falls back to backend available throughput before offered capacity", () => {
    const telemetry = buildDataPanelTelemetry(
      makeSnapshot({
        last_sim_time: 10,
        metrics_summary: {
          network: {
            latency: 0,
            throughput: 0,
            linkUtilization: 0,
            series: []
          },
          compute: {
            taskQueueLength: 0,
            executionSuccessRate: 1,
            runningTasks: 0,
            finishedTasks: 0,
            deadlineMissedTasks: 0
          },
          orbit: {
            activeSatellites: 0,
            coverageRatio: 0,
            series: []
          },
          system: {
            eventRate: 1,
            systemLoad: 0,
            eventSeries: [{ index: 0, simTime: 10 }]
          }
        }
      }),
      10,
      {
        network_quality_estimated_delivered_throughput_mbps: 0,
        network_quality_estimated_available_throughput_mbps: 88,
        network_quality_offered_route_capacity_mbps: 100
      }
    );

    expect(telemetry[0].throughputMbps).toBe(88);
  });
});

describe("buildComputeResourcePool", () => {
  it("summarizes satellite-hosted FP32 compute capacity", () => {
    const pool = buildComputeResourcePool(
      makeSnapshot({
        compute_nodes: [
          {
            node_id: "sat-a",
            running_tasks: 1,
            finished_tasks: 0,
            capacity: 20,
            available_capacity: 5,
            status: "BUSY",
            load_ratio: 0.75,
            cpu_gflops_fp64: 4,
            gpu_tflops_fp32: 2,
            gpu_tflops_fp16: 4,
            npu_tops_int8: 8,
            memory_gb: 16,
            storage_gb: 256
          },
          {
            node_id: "sat-b",
            running_tasks: 0,
            finished_tasks: 0,
            capacity: 10,
            available_capacity: 10,
            status: "IDLE",
            load_ratio: 0,
            cpu_gflops_fp64: 2,
            gpu_tflops_fp32: 1,
            gpu_tflops_fp16: 2,
            npu_tops_int8: 4,
            memory_gb: 8,
            storage_gb: 128
          }
        ]
      })
    );

    expect(pool).toMatchObject({
      totalTflops: 30,
      usedTflops: 15,
      availableTflops: 15,
      usedPercent: 50
    });
    expect(pool.vectorSummary).toMatchObject({
      cpuFp64Gflops: 6,
      usedGpuFp32Tflops: 0,
      gpuFp32Tflops: 3,
      gpuFp16Tflops: 6,
      npuInt8Tops: 12,
      usedMemoryGb: 0,
      memoryGb: 24,
      storageGb: 384,
      utilizationMode: "SNAPSHOT_SCALAR_FP32_AVAILABLE_ONLY"
    });
    expect(pool.slices.map((slice) => slice.name)).toEqual(["已消耗 FP32", "可用 FP32"]);
  });

  it("prefers backend compute resource vector summary when available", () => {
    const pool = buildComputeResourcePool(makeSnapshot(), {
      compute_resource_total_gflops_fp32: 80,
      compute_resource_available_gflops_fp32: 50,
      compute_resource_used_gflops_fp32: 30,
      compute_resource_total_gflops_fp64: 12,
      compute_resource_available_gflops_fp64: 10,
      compute_resource_used_gflops_fp64: 2,
      compute_resource_total_gpu_tflops_fp32: 6,
      compute_resource_available_gpu_tflops_fp32: 4,
      compute_resource_used_gpu_tflops_fp32: 2,
      compute_resource_total_gpu_tflops_fp16: 12,
      compute_resource_available_gpu_tflops_fp16: 9,
      compute_resource_used_gpu_tflops_fp16: 3,
      compute_resource_total_npu_tops_int8: 24,
      compute_resource_available_npu_tops_int8: 20,
      compute_resource_used_npu_tops_int8: 4,
      compute_resource_total_memory_gb: 96,
      compute_resource_available_memory_gb: 88,
      compute_resource_used_memory_gb: 8,
      compute_resource_total_storage_gb: 2048,
      compute_resource_available_storage_gb: 2000,
      compute_resource_used_storage_gb: 48,
      compute_resource_vector_utilization_mode: "RESOURCE_VECTOR_ESTIMATED"
    });

    expect(pool).toMatchObject({
      totalTflops: 80,
      usedTflops: 30,
      availableTflops: 50,
      usedPercent: 37.5,
      vectorSummary: {
        cpuFp64Gflops: 12,
        usedCpuFp64Gflops: 2,
        availableCpuFp64Gflops: 10,
        gpuFp32Tflops: 6,
        usedGpuFp32Tflops: 2,
        availableGpuFp32Tflops: 4,
        gpuFp16Tflops: 12,
        usedGpuFp16Tflops: 3,
        availableGpuFp16Tflops: 9,
        npuInt8Tops: 24,
        usedNpuInt8Tops: 4,
        availableNpuInt8Tops: 20,
        memoryGb: 96,
        usedMemoryGb: 8,
        availableMemoryGb: 88,
        storageGb: 2048,
        usedStorageGb: 48,
        availableStorageGb: 2000,
        utilizationMode: "RESOURCE_VECTOR_ESTIMATED"
      }
    });
  });
});

describe("buildTopComputeNodeRows", () => {
  it("orders satellite compute nodes by load, used FP32, tasks, and id", () => {
    const rows = buildTopComputeNodeRows(
      makeSnapshot({
        compute_nodes: [
          {
            node_id: "sat-c",
            running_tasks: 1,
            finished_tasks: 2,
            capacity: 40,
            available_capacity: 10,
            status: "BUSY",
            load_ratio: 0.75
          },
          {
            node_id: "sat-a",
            running_tasks: 3,
            finished_tasks: 1,
            capacity: 100,
            available_capacity: 20,
            status: "OVERLOADED",
            load_ratio: 0.8,
            used_cpu_gflops_fp32: 82
          },
          {
            node_id: "sat-b",
            running_tasks: 2,
            finished_tasks: 4,
            capacity: 100,
            available_capacity: 20,
            status: "BUSY",
            load_ratio: 0.8,
            used_cpu_gflops_fp32: 80
          },
          {
            node_id: "sat-d",
            running_tasks: 0,
            finished_tasks: 0,
            capacity: 10,
            available_capacity: 10,
            status: "IDLE",
            load_ratio: 0
          }
        ]
      }),
      undefined,
      3
    );

    expect(rows.map((row) => row.nodeId)).toEqual(["sat-a", "sat-b", "sat-c"]);
    expect(rows[0]).toMatchObject({
      statusLabel: "OVERLOADED",
      loadPercent: 80,
      usedFp32Gflops: 82,
      runningTasks: 3,
      loadLabel: "80%",
      fp32Label: "82 / 100 GFLOPS",
      taskLabel: "3 运行 / 1 完成"
    });
  });

  it("prefers backend satellite KPI slices over local compute-node aggregation", () => {
    const rows = buildTopComputeNodeRows(
      makeSnapshot({
        compute_nodes: [
          {
            node_id: "sat-a",
            running_tasks: 0,
            finished_tasks: 0,
            capacity: 100,
            available_capacity: 90,
            status: "IDLE",
            load_ratio: 0.1
          }
        ]
      }),
      {
        version: "v1",
        mode: "TOP_ACTIVITY_LIMITED",
        slice_limit: 64,
        satellite_count: 1,
        slice_count: 1,
        slices: [
          {
            satellite_id: "sat-a",
            active_link_count: 3,
            active_access_link_count: 1,
            active_space_link_count: 2,
            route_count: 4,
            available_route_count: 3,
            route_capacity_mbps: 120,
            route_demand_mbps: 100,
            route_latency_avg_s: 0.05,
            route_delay_variation_proxy_s: 0.01,
            route_loss_proxy_rate: 0.02,
            compute_capacity_gflops_fp32: 100,
            compute_used_gflops_fp32: 76,
            compute_load_ratio: 0.76,
            running_task_count: 2,
            finished_task_count: 5
          }
        ]
      }
    );

    expect(rows[0]).toMatchObject({
      nodeId: "sat-a",
      statusLabel: "IDLE",
      loadPercent: 76,
      usedFp32Gflops: 76,
      runningTasks: 2,
      loadLabel: "76%",
      fp32Label: "76 / 100 GFLOPS",
      taskLabel: "2 运行 / 5 完成"
    });
  });

  it("derives load from scalar capacity when live load ratio is missing", () => {
    expect(
      buildTopComputeNodeRows(
        makeSnapshot({
          compute_nodes: [
            {
              node_id: "sat-a",
              running_tasks: 0,
              finished_tasks: 0,
              capacity: 50,
              available_capacity: 20,
              status: "BUSY",
              load_ratio: Number.NaN
            }
          ]
        })
      )[0]
    ).toMatchObject({
      loadPercent: 60,
      loadLabel: "60%",
      fp32Label: "30 / 50 GFLOPS"
    });
  });
});

function makeSnapshot(overrides: Partial<WorldSnapshot> = {}): WorldSnapshot {
  return {
    timestamp: 0,
    reducer_version: 0,
    last_sim_time: 0,
    event_count: 0,
    satellites: [],
    links: [],
    routes: [],
    compute_nodes: [],
    ground_users: [],
    active_tasks: [],
    metrics: [],
    metrics_summary: {
      network: {
        latency: 0,
        throughput: 0,
        linkUtilization: 0,
        series: []
      },
      compute: {
        taskQueueLength: 0,
        executionSuccessRate: 1,
        runningTasks: 0,
        finishedTasks: 0,
        deadlineMissedTasks: 0
      },
      orbit: {
        activeSatellites: 0,
        coverageRatio: 0,
        series: []
      },
      system: {
        eventRate: 0,
        systemLoad: 0,
        eventSeries: []
      }
    },
    scenario_config: null,
    fidelity_summary: null,
    active_route_id: null,
    spatial_index: new Map(),
    indexes: {
      satellites: new Map(),
      ground_users: new Map()
    },
    diff: {
      satellite_ids: [],
      link_ids: [],
      task_ids: [],
      metric_ids: []
    },
    ...overrides
  };
}
