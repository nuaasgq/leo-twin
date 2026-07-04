import { describe, expect, it } from "vitest";

import {
  buildComputeResourcePool,
  buildDataPanelDisplaySummary,
  buildDataPanelNetworkKpiSource,
  buildDataPanelRuntimeProgress,
  buildDataPanelSummary,
  buildDataPanelTelemetry,
  buildDataPanelTrafficDisplay,
  resolveNetworkQualityKpis
} from "../src/dashboard/data_panel/DataPanel";
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
      modelNote: "后端流级代理指标；未进行包级仿真。"
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
      modelNote: "后端网络质量指标为流级代理模型；未进行包级仿真。"
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
      modelNote: "后端网络质量指标为流级代理模型；未进行包级仿真。"
    });
  });

  it("marks fallback estimates when backend network quality is absent", () => {
    expect(buildDataPanelNetworkKpiSource(makeSnapshot())).toEqual({
      sourceLabel: "前端快照估算",
      modelNote: "未收到后端网络质量指标时，根据快照链路与路由做显示估算。"
    });
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
