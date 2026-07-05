import { describe, expect, it } from "vitest";

import {
  buildComputeResourcePool,
  buildComputeResourcePoolFromRuntime,
  buildComputeResourcePoolModeNote,
  buildDataPanelComputeBottleneckDisplay,
  buildDataPanelComputeTaskTimelineDisplay,
  buildDataPanelComputeVectorTail,
  buildDataPanelConfiguredScale,
  buildDataPanelConfigurationExplanationDisplay,
  buildDataPanelInformationArchitectureDisplay,
  buildDataPanelDetailScopeNotes,
  buildDataPanelDetailPageSizes,
  buildDataPanelPaginationContractNotes,
  buildDataPanelDetailWindowPolicyNote,
  buildDataPanelDisplaySummary,
  buildDataPanelExportCatalogDisplay,
  buildDataPanelExportCompareDisplay,
  buildDataPanelExportCompareStatus,
  buildDataPanelExportHistoryDisplay,
  buildDataPanelExportRestoreActionDisplay,
  buildDataPanelExportRestorePreflightDisplay,
  buildDataPanelExportRestorePreflightStatus,
  buildDataPanelNetworkFormulaInputs,
  buildDataPanelNetworkComponentTail,
  buildDataPanelNetworkKpiCaveats,
  buildDataPanelNetworkKpiCredibilityDisplay,
  buildDataPanelModelAssumptionsDisplay,
  buildDataPanelNetworkKpiProvenanceItems,
  buildDataPanelNetworkKpiSource,
  buildDataPanelNodeDetailDrawerItems,
  buildDataPanelReproducibilityDisplay,
  buildDataPanelRouteConstraints,
  buildDataPanelRouteExplanationRows,
  buildDataPanelRuntimeProgress,
  buildDataPanelSatelliteResourceHistory,
  buildDataPanelServiceLatencyDisplay,
  buildDataPanelServiceLatencyRows,
  buildSatelliteDetailDrawerSectionsV1,
  buildSatelliteResourceInspector,
  buildDataPanelSummary,
  buildDataPanelTelemetry,
  buildDataPanelTrafficDisplay,
  buildDataPanelUserConfigurationContractDisplay,
  buildDataPanelUserConfigurationFieldSections,
  buildDataPanelUserConfigurationValidationDisplay,
  buildUserBusinessRequestInspector,
  buildUserDetailDrawerSectionsV1,
  buildDataPanelUserRequestHistory,
  buildRuntimeKpiTelemetrySamples,
  buildRuntimeDetailWindowNote,
  buildRuntimeDetailSourceBadge,
  buildSatelliteResourceRows,
  buildTopComputeNodeRows,
  buildUserBusinessRequestRows,
  COMPUTE_SERIES_OPTIONS,
  filterRouteExplanationRows,
  filterSatelliteResourceRows,
  filterUserBusinessRequestRows,
  paginateDetailRows,
  resolveNetworkQualityKpis,
  RuntimeDetailPages,
  runtimeNodeDetailPageToSummary,
  selectRuntimeNodeDetailSummary,
  selectRuntimeRouteExplanationSummary,
  selectRuntimeSatelliteDetailCard,
  selectRuntimeSatelliteServiceSummary,
  selectRuntimeUserDetailCard,
  selectRuntimeUserRequestSummary,
  selectSatelliteResourceRow,
  selectUserConfigurationApplyPayload,
  selectUserBusinessRequestRow,
  userConfigurationPreflightModeEnabled,
  userConfigurationTextEndpointFormat
} from "../src/dashboard/data_panel/DataPanel";
import {
  FidelitySummary,
  GeneratedScenarioConfig,
  RuntimeStatusPayload,
  UserConfigurationValidationReportV1
} from "../src/core/event_types";
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

describe("runtime detail page selection", () => {
  it("prefers server-side detail pages over bounded runtime status summaries", () => {
    const runtimeStatus = {
      status: "RUNNING",
      mode: "REAL_TIME",
      speed_factor: 1,
      seed: 1,
      duration: 600,
      config_version: 1,
      last_action: "START",
      user_request_summary_v1: {
        version: "v1",
        source: "BACKEND_RUNTIME_SNAPSHOT",
        user_count: 2,
        item_count: 1,
        active_user_count: 1,
        compute_service_user_count: 0,
        waiting_user_count: 0,
        hidden_user_count: 1,
        items: []
      },
      satellite_service_summary_v1: {
        version: "v1",
        source: "BACKEND_RUNTIME_SNAPSHOT",
        satellite_count: 2,
        item_count: 1,
        hidden_satellite_count: 1,
        items: []
      },
      node_detail_summary_v1: {
        version: "v1",
        source: "BACKEND_RUNTIME_STATUS",
        user_detail_count: 1,
        satellite_detail_count: 0,
        users: [
          {
            entity_type: "USER",
            entity_id: "user-status",
            title: "状态用户",
            subtitle: "STATUS",
            fields: []
          }
        ],
        satellites: []
      },
      route_explanation_summary_v1: {
        version: "v1",
        source: "BACKEND_RUNTIME_SNAPSHOT",
        route_count: 1,
        item_count: 1,
        available_route_count: 1,
        blocked_route_count: 0,
        over_demand_route_count: 0,
        compute_service_route_count: 0,
        network_service_route_count: 1,
        items: [
          {
            route_id: "route-status",
            flow_id: "flow-status",
            user_id: "user-status",
            source_id: "user-status",
            destination_id: "service-status",
            selected_satellite_id: "sat-status",
            primary_next_hop_id: "sat-status",
            next_hop_ids: ["sat-status"],
            hop_count: 1,
            path_label: "user-status -> sat-status",
            available: true,
            route_pressure_proxy: 0,
            business_type: "DATA_TRANSFER",
            business_label: "数据传输",
            bottleneck_component: "NONE",
            bottleneck_reason: "NONE",
            bottleneck_reason_label: "No bottleneck",
            explanation_label: "status route"
          }
        ]
      }
    } as RuntimeStatusPayload;
    const detailPages: RuntimeDetailPages = {
      users: {
        ...runtimeStatus.user_request_summary_v1!,
        cursor: 80,
        item_count: 80,
        hidden_user_count: 0
      },
      satellites: {
        ...runtimeStatus.satellite_service_summary_v1!,
        cursor: 120,
        item_count: 120,
        hidden_satellite_count: 0
      },
      nodes: {
        version: "v1",
        source: "BACKEND_RUNTIME_STATUS",
        summary_scope: "COMBINED_USER_SATELLITE_NODE_DETAIL_WINDOW",
        cursor: 0,
        limit: 2,
        next_cursor: 2,
        has_more: false,
        node_count: 2,
        user_count: 1,
        satellite_count: 1,
        item_count: 2,
        hidden_node_count: 0,
        window_user_detail_count: 1,
        window_satellite_detail_count: 1,
        items: [
          {
            entity_type: "USER",
            entity_id: "user-page",
            title: "页面用户",
            subtitle: "PAGE",
            fields: [{ label: "路径", value: "page path", tone: "normal" }]
          },
          {
            entity_type: "SATELLITE",
            entity_id: "sat-page",
            title: "页面卫星",
            subtitle: "PAGE",
            fields: [{ label: "负载", value: "65%", tone: "resource" }]
          }
        ]
      },
      routes: {
        version: "v1",
        source: "BACKEND_RUNTIME_SNAPSHOT",
        cursor: 40,
        limit: 40,
        next_cursor: 41,
        has_more: false,
        route_count: 1,
        item_count: 1,
        available_route_count: 1,
        blocked_route_count: 0,
        over_demand_route_count: 0,
        compute_service_route_count: 0,
        network_service_route_count: 1,
        items: [
          {
            route_id: "route-page",
            flow_id: "flow-page",
            user_id: "user-page",
            source_id: "user-page",
            destination_id: "service-page",
            selected_satellite_id: "sat-page",
            primary_next_hop_id: "sat-page",
            next_hop_ids: ["sat-page"],
            hop_count: 1,
            path_label: "user-page -> sat-page",
            available: true,
            route_pressure_proxy: 0,
            business_type: "DATA_TRANSFER",
            business_label: "数据传输",
            bottleneck_component: "NONE",
            bottleneck_reason: "NONE",
            bottleneck_reason_label: "No bottleneck",
            explanation_label: "page route"
          }
        ]
      }
    };

    expect(selectRuntimeUserRequestSummary(runtimeStatus, detailPages)?.cursor).toBe(80);
    expect(selectRuntimeSatelliteServiceSummary(runtimeStatus, detailPages)?.cursor).toBe(
      120
    );
    expect(runtimeNodeDetailPageToSummary(detailPages.nodes!).users[0].title).toBe(
      "页面用户"
    );
    expect(
      selectRuntimeNodeDetailSummary(runtimeStatus, detailPages)?.satellites[0].title
    ).toBe("页面卫星");
    expect(selectRuntimeRouteExplanationSummary(runtimeStatus, detailPages)?.cursor).toBe(
      40
    );
    expect(
      selectRuntimeRouteExplanationSummary(runtimeStatus, detailPages)?.items[0]
        .route_id
    ).toBe("route-page");
    expect(selectRuntimeUserRequestSummary(runtimeStatus, null)?.cursor).toBeUndefined();
    expect(selectRuntimeNodeDetailSummary(runtimeStatus, null)?.users[0].title).toBe(
      "状态用户"
    );
    expect(
      selectRuntimeRouteExplanationSummary(runtimeStatus, null)?.items[0].route_id
    ).toBe("route-status");
  });
});

describe("buildRuntimeDetailWindowNote", () => {
  it("explains when the backend detail window covers a 1200-node scenario", () => {
    expect(
      buildRuntimeDetailWindowNote(
        {
          version: "v1",
          source: "BACKEND_RUNTIME_SNAPSHOT",
          summary_scope: "PAGE",
          cursor: 0,
          limit: 5000,
          has_more: false,
          user_count: 1200,
          item_count: 1200,
          active_user_count: 80,
          compute_service_user_count: 20,
          waiting_user_count: 4,
          hidden_user_count: 0,
          items: []
        },
        "users"
      )
    ).toBe("后端窗口 1-1,200 / 1,200；当前窗口覆盖全部明细");
  });

  it("reports remaining cursor-readable rows when the backend window is partial", () => {
    expect(
      buildRuntimeDetailWindowNote(
        {
          version: "v1",
          source: "BACKEND_RUNTIME_SNAPSHOT",
          summary_scope: "PAGE",
          cursor: 5000,
          limit: 5000,
          next_cursor: 10000,
          has_more: true,
          satellite_count: 12000,
          item_count: 5000,
          hidden_satellite_count: 2000,
          items: []
        },
        "satellites"
      )
    ).toBe("后端窗口 5,001-10,000 / 12,000；仍有 2,000 行可通过游标继续读取");
  });

  it("omits the note for legacy status summaries without cursor metadata", () => {
    expect(
      buildRuntimeDetailWindowNote(
        {
          version: "v1",
          source: "BACKEND_RUNTIME_SNAPSHOT",
          user_count: 10,
          item_count: 10,
          active_user_count: 1,
          compute_service_user_count: 0,
          waiting_user_count: 0,
          hidden_user_count: 0,
          items: []
        },
        "users"
      )
    ).toBeNull();
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

describe("buildDataPanelRouteExplanationRows", () => {
  it("formats backend route explanation records for the dashboard", () => {
    expect(
      buildDataPanelRouteExplanationRows({
        version: "v1",
        source: "BACKEND_RUNTIME_SNAPSHOT",
        summary_scope: "ROUTE_EXPLANATION_WINDOW",
        cursor: 0,
        limit: 500,
        next_cursor: 2,
        has_more: false,
        route_count: 2,
        item_count: 2,
        available_route_count: 1,
        blocked_route_count: 1,
        over_demand_route_count: 1,
        compute_service_route_count: 1,
        network_service_route_count: 1,
        items: [
          {
            route_id: "route-b",
            flow_id: "flow-b",
            user_id: "user-1",
            source_id: "user-1",
            destination_id: "service-0",
            selected_satellite_id: "sat-0",
            primary_next_hop_id: "sat-0",
            next_hop_ids: ["sat-0", "sat-1", "service-0"],
            hop_count: 3,
            path_label: "user-1 -> sat-0 -> sat-1 -> service-0",
            available: false,
            capacity_mbps: 40,
            demand_mbps: 60,
            latency_s: 0.2,
            loss_proxy_rate: 0.05,
            route_pressure_proxy: 1,
            business_type: "DATA_TRANSFER",
            business_label: "数据传输",
            bottleneck_component: "CAPACITY",
            bottleneck_reason: "ROUTE_CAPACITY_BELOW_DEMAND",
            bottleneck_reason_label: "Route capacity below demand",
            explanation_label: "capacity 40 Mbps < demand 60 Mbps"
          },
          {
            route_id: "route-a",
            flow_id: "flow-a",
            user_id: "user-0",
            source_id: "user-0",
            destination_id: "compute-0",
            selected_satellite_id: "sat-0",
            primary_next_hop_id: "sat-0",
            next_hop_ids: ["sat-0", "compute-0"],
            hop_count: 2,
            path_label: "user-0 -> sat-0 -> compute-0",
            available: true,
            capacity_mbps: 80,
            demand_mbps: 60,
            latency_s: 0.1,
            loss_proxy_rate: 0.01,
            route_pressure_proxy: 0.75,
            business_type: "COMPUTE_SERVICE",
            business_label: "通信-计算服务",
            bottleneck_component: "LOSS_PROXY",
            bottleneck_reason: "ROUTE_LOSS_PROXY_POSITIVE",
            bottleneck_reason_label: "Route loss proxy is positive",
            explanation_label: "route has a positive flow-level loss proxy"
          }
        ]
      })
    ).toEqual({
      sourceLabel: "后端路由解释 2/2 条；阻塞 1 / 超需求 1",
      items: [
        {
          routeId: "route-b",
          flowId: "flow-b",
          available: false,
          availabilityLabel: "阻塞",
          businessType: "DATA_TRANSFER",
          businessLabel: "数据传输",
          nextHopLabel: "sat-0",
          capacityDemandLabel: "40 Mbps / 60 Mbps",
          pressureLabel: "100%",
          bottleneckComponent: "CAPACITY",
          bottleneckLabel: "Route capacity below demand",
          explanationLabel: "capacity 40 Mbps < demand 60 Mbps",
          pathLabel: "user-1 -> sat-0 -> sat-1 -> service-0"
        },
        {
          routeId: "route-a",
          flowId: "flow-a",
          available: true,
          availabilityLabel: "可用",
          businessType: "COMPUTE_SERVICE",
          businessLabel: "通信-计算服务",
          nextHopLabel: "sat-0",
          capacityDemandLabel: "80 Mbps / 60 Mbps",
          pressureLabel: "75%",
          bottleneckComponent: "LOSS_PROXY",
          bottleneckLabel: "Route loss proxy is positive",
          explanationLabel: "route has a positive flow-level loss proxy",
          pathLabel: "user-0 -> sat-0 -> compute-0"
        }
      ]
    });
  });

  it("waits for backend route explanations before rendering rows", () => {
    expect(buildDataPanelRouteExplanationRows(undefined)).toEqual({
      sourceLabel: "等待后端路由解释",
      items: []
    });
  });

  it("filters route explanation rows by business, bottleneck, next hop, or path", () => {
    const rows = buildDataPanelRouteExplanationRows({
      version: "v1",
      source: "BACKEND_RUNTIME_SNAPSHOT",
      route_count: 2,
      item_count: 2,
      available_route_count: 1,
      blocked_route_count: 1,
      over_demand_route_count: 1,
      compute_service_route_count: 1,
      network_service_route_count: 1,
      items: [
        {
          route_id: "route-b",
          flow_id: "flow-b",
          user_id: "user-1",
          source_id: "user-1",
          destination_id: "service-0",
          selected_satellite_id: "sat-0",
          primary_next_hop_id: "sat-0",
          next_hop_ids: ["sat-0", "sat-1", "service-0"],
          hop_count: 3,
          path_label: "user-1 -> sat-0 -> sat-1 -> service-0",
          available: false,
          capacity_mbps: 40,
          demand_mbps: 60,
          route_pressure_proxy: 1,
          business_type: "DATA_TRANSFER",
          business_label: "数据传输",
          bottleneck_component: "CAPACITY",
          bottleneck_reason: "ROUTE_CAPACITY_BELOW_DEMAND",
          bottleneck_reason_label: "Route capacity below demand",
          explanation_label: "capacity 40 Mbps < demand 60 Mbps"
        },
        {
          route_id: "route-a",
          flow_id: "flow-a",
          user_id: "user-0",
          source_id: "user-0",
          destination_id: "compute-0",
          selected_satellite_id: "sat-0",
          primary_next_hop_id: "sat-0",
          next_hop_ids: ["sat-0", "compute-0"],
          hop_count: 2,
          path_label: "user-0 -> sat-0 -> compute-0",
          available: true,
          capacity_mbps: 80,
          demand_mbps: 60,
          route_pressure_proxy: 0.75,
          business_type: "COMPUTE_SERVICE",
          business_label: "通信-计算服务",
          bottleneck_component: "LOSS_PROXY",
          bottleneck_reason: "ROUTE_LOSS_PROXY_POSITIVE",
          bottleneck_reason_label: "Route loss proxy is positive",
          explanation_label: "route has a positive flow-level loss proxy"
        }
      ]
    });

    expect(filterRouteExplanationRows(rows, "capacity").items.map((row) => row.routeId)).toEqual([
      "route-b"
    ]);
    expect(filterRouteExplanationRows(rows, "计算").items.map((row) => row.routeId)).toEqual([
      "route-a"
    ]);
    expect(filterRouteExplanationRows(rows, "compute-0").items.map((row) => row.routeId)).toEqual([
      "route-a"
    ]);
    expect(filterRouteExplanationRows(rows, "  SAT-1 ").items.map((row) => row.routeId)).toEqual([
      "route-b"
    ]);
    expect(
      filterRouteExplanationRows(rows, {
        query: "",
        availability: "BLOCKED",
        businessType: "DATA_TRANSFER",
        bottleneckComponent: "CAPACITY"
      }).items.map((row) => row.routeId)
    ).toEqual(["route-b"]);
    expect(
      filterRouteExplanationRows(rows, {
        query: "compute",
        availability: "AVAILABLE",
        businessType: "COMPUTE_SERVICE",
        bottleneckComponent: "LOSS_PROXY"
      }).items.map((row) => row.routeId)
    ).toEqual(["route-a"]);
    expect(
      filterRouteExplanationRows(rows, {
        query: "",
        availability: "AVAILABLE",
        businessType: "DATA_TRANSFER",
        bottleneckComponent: "ALL"
      }).items
    ).toEqual([]);
    expect(filterRouteExplanationRows(rows, "").items).toBe(rows.items);
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

describe("buildDataPanelReproducibilityDisplay", () => {
  it("summarizes backend runtime reproducibility manifest for the dashboard", () => {
    expect(
      buildDataPanelReproducibilityDisplay({
        version: "v1",
        source: "BACKEND_RUNTIME_STATUS",
        manifest_id: "leo_twin.runtime_reproducibility_manifest.v1",
        session_id: "integration-demo-7",
        scenario_hash:
          "sha256:1111111111111111111111111111111111111111111111111111111111111111",
        control_config_hash:
          "sha256:2222222222222222222222222222222222222222222222222222222222222222",
        generated_config_hash:
          "sha256:3333333333333333333333333333333333333333333333333333333333333333",
        metrics_summary_hash:
          "sha256:4444444444444444444444444444444444444444444444444444444444444444",
        runtime_state_hash:
          "sha256:5555555555555555555555555555555555555555555555555555555555555555",
        manifest_hash:
          "sha256:abcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcd",
        artifact_policy: "LIVE_STATUS_MANIFEST_ONLY",
        artifacts: [
          {
            name: "events.jsonl",
            format: "jsonl",
            status: "AVAILABLE_FOR_BATCH_EXPORT",
            source: "MetricsCollector.write_outputs"
          }
        ],
        artifact_count: 4
      })
    ).toEqual({
      primaryLabel: "integration-demo-7 / abcdefabcdef",
      secondaryLabel: "LIVE_STATUS_MANIFEST_ONLY / 4 artifacts"
    });
    expect(buildDataPanelReproducibilityDisplay(undefined)).toBeNull();
  });
});

describe("buildDataPanelUserConfigurationContractDisplay", () => {
  it("summarizes backend user configuration schema, templates and export", () => {
    const display = buildDataPanelUserConfigurationContractDisplay(
      {
        version: "v2",
        schema_id: "sees.user_configuration.v2",
        source: "backend_sees_config",
        format: "YAML_OR_JSON_MAPPING",
        unknown_key_policy: "REJECT",
        defaulting_policy: "OMITTED_FIELDS_USE_BACKEND_DEFAULTS",
        frontend_policy: "CONTROL_PANEL_KEY_FIELDS_ONLY",
        forbidden_integrations: ["STK", "EXATA", "AFSIM", "DDS"],
        packet_level_simulation: false,
        field_count: 42,
        key_field_count: 12,
        file_only_field_count: 30,
        root_sections: [
          {
            path: "scenario",
            purpose: "卫星规模、轨道和算力配置"
          },
          {
            path: "network",
            purpose: "网络链路和指标代理配置"
          }
        ],
        fields: [
          {
            path: "scenario.satellite_count",
            section: "scenario",
            label: "卫星数量",
            description: "场景中的卫星节点数量。",
            value_type: "integer",
            default_value: 72,
            current_value: 120,
            required_in_effective_config: true,
            required_in_user_file: false,
            editable_surface: "CONTROL_PANEL_KEY_FIELD",
            validation_rules: ["minimum 1"],
            minimum: 1
          },
          {
            path: "scenario.compute_gpu_tflops_fp16",
            section: "scenario",
            label: "FP16 GPU 算力",
            description: "单颗卫星的 FP16 GPU 峰值算力。",
            value_type: "number",
            default_value: 5,
            current_value: 5,
            required_in_effective_config: true,
            required_in_user_file: false,
            editable_surface: "DETAILED_CONFIG_FILE_ONLY",
            validation_rules: ["minimum 0"],
            minimum: 0,
            unit: "TFLOPS"
          },
          {
            path: "network.carrier_frequency_hz",
            section: "network",
            label: "载波频率",
            description: "网络抽象模型记录的载波频率元数据。",
            value_type: "number",
            default_value: 20000000000,
            current_value: 20000000000,
            required_in_effective_config: true,
            required_in_user_file: false,
            editable_surface: "DETAILED_CONFIG_FILE_ONLY",
            validation_rules: ["minimum 1"],
            minimum: 1,
            unit: "Hz"
          }
        ],
        templates: [],
        examples: []
      },
      {
        version: "v1",
        source: "BACKEND_USER_CONFIGURATION",
        schema_id: "sees.user_configuration.v2",
        catalog_scope: "APPROVED_EXECUTABLE_TEMPLATES",
        mutation_policy: "READ_ONLY_CATALOG",
        template_count: 4,
        templates: [],
        load_command: {
          type: "RUNTIME_CONTROL",
          action: "LOAD_TEMPLATE",
          payload_key: "template_id",
          requires_uninitialized_runtime: true
        }
      },
      {
        version: "v1",
        source: "BACKEND_USER_CONFIGURATION",
        schema_id: "sees.user_configuration.v2",
        export_scope: "CURRENT_EFFECTIVE_SEES_CONFIG",
        format: "JSON_MAPPING",
        yaml_config_file: "configs/sees_control.yaml",
        generated_config_file: "configs/generated_full_system_demo.json",
        unknown_key_policy: "REJECT",
        defaulting_policy: "OMITTED_FIELDS_USE_BACKEND_DEFAULTS",
        import_paths: ["CONFIG_UPDATE control message for partial updates"],
        config_hash:
          "sha256:abcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcd",
        validation_ok: true,
        validation_error_count: 0,
        validation_errors: [],
        config: { scenario: { satellite_count: 72 } }
      }
    );

    expect(display).toMatchObject({
      tone: "match",
      sourceLabel: "BACKEND_USER_CONFIGURATION / sees.user_configuration.v2",
      summaryLabel: "字段 42 / 关键 12 / 模板 4",
      statusLabel: "当前配置可复现",
      detailLabel: "config abcdefabcdef / CURRENT_EFFECTIVE_SEES_CONFIG",
      schemaHref: "/scenario/user-config/schema",
      templatesHref: "/scenario/user-config/templates",
      exportHref: "/scenario/user-config/export"
    });
    expect(display?.fieldSections).toEqual([
      {
        sectionPath: "scenario",
        purpose: "卫星规模、轨道和算力配置",
        metaLabels: ["字段 2", "关键 1", "文件 1"],
        sampleFields: [
          {
            path: "scenario.satellite_count",
            label: "scenario.satellite_count · 卫星数量",
            description: "场景中的卫星节点数量。"
          },
          {
            path: "scenario.compute_gpu_tflops_fp16",
            label: "scenario.compute_gpu_tflops_fp16 · FP16 GPU 算力",
            description: "单颗卫星的 FP16 GPU 峰值算力。"
          }
        ]
      },
      {
        sectionPath: "network",
        purpose: "网络链路和指标代理配置",
        metaLabels: ["字段 1", "关键 0", "文件 1"],
        sampleFields: [
          {
            path: "network.carrier_frequency_hz",
            label: "network.carrier_frequency_hz · 载波频率",
            description: "网络抽象模型记录的载波频率元数据。"
          }
        ]
      }
    ]);
    expect(display?.metaLabels).toEqual([
      "unknown REJECT",
      "default OMITTED_FIELDS_USE_BACKEND_DEFAULTS",
      "validation ok",
      "format YAML_OR_JSON_MAPPING"
    ]);
  });

  it("reports loading and error states for user configuration contract", () => {
    expect(
      buildDataPanelUserConfigurationContractDisplay(null, null, null, true)
    ).toMatchObject({
      tone: "pending",
      statusLabel: "加载中"
    });
    expect(
      buildDataPanelUserConfigurationContractDisplay(
        null,
        null,
        null,
        false,
        "HTTP 503"
      )
    ).toMatchObject({
      tone: "error",
      statusLabel: "配置契约加载失败",
      summaryLabel: "HTTP 503"
    });
    expect(buildDataPanelUserConfigurationContractDisplay(null, null, null)).toBeNull();
  });
});

describe("buildDataPanelUserConfigurationFieldSections", () => {
  it("groups declared and extra schema fields deterministically", () => {
    const sections = buildDataPanelUserConfigurationFieldSections({
      version: "v2",
      schema_id: "sees.user_configuration.v2",
      source: "backend_sees_config",
      format: "YAML_OR_JSON_MAPPING",
      unknown_key_policy: "REJECT",
      defaulting_policy: "OMITTED_FIELDS_USE_BACKEND_DEFAULTS",
      frontend_policy: "CONTROL_PANEL_KEY_FIELDS_ONLY",
      forbidden_integrations: ["STK", "EXATA", "AFSIM", "DDS"],
      packet_level_simulation: false,
      field_count: 3,
      key_field_count: 1,
      file_only_field_count: 2,
      root_sections: [
        {
          path: "runtime",
          purpose: "运行时配置"
        }
      ],
      fields: [
        {
          path: "ui.visualization.coverage",
          section: "ui",
          label: "覆盖显示",
          description: "是否显示覆盖层。",
          value_type: "boolean",
          default_value: true,
          current_value: true,
          required_in_effective_config: true,
          required_in_user_file: false,
          editable_surface: "DETAILED_CONFIG_FILE_ONLY",
          validation_rules: []
        },
        {
          path: "runtime.duration",
          section: "runtime",
          label: "仿真时长",
          description: "仿真运行的目标时长。",
          value_type: "number",
          default_value: 600,
          current_value: 600,
          required_in_effective_config: true,
          required_in_user_file: false,
          editable_surface: "CONTROL_PANEL_KEY_FIELD",
          validation_rules: ["minimum 1"],
          minimum: 1,
          unit: "s"
        },
        {
          path: "network.loss_proxy_enabled",
          section: "network",
          label: "丢包代理",
          description: "是否启用流级丢包代理。",
          value_type: "boolean",
          default_value: true,
          current_value: true,
          required_in_effective_config: true,
          required_in_user_file: false,
          editable_surface: "DETAILED_CONFIG_FILE_ONLY",
          validation_rules: []
        }
      ],
      templates: [],
      examples: []
    });

    expect(sections.map((section) => section.sectionPath)).toEqual([
      "runtime",
      "network",
      "ui"
    ]);
    expect(sections[0]?.metaLabels).toEqual(["字段 1", "关键 1", "文件 0"]);
    expect(sections[1]?.purpose).toBe("后端 schema 字段分组");
    expect(sections[2]?.sampleFields[0]?.label).toBe(
      "ui.visualization.coverage · 覆盖显示"
    );
  });
});

describe("buildDataPanelUserConfigurationValidationDisplay", () => {
  it("summarizes accepted and rejected validation reports", () => {
    expect(
      buildDataPanelUserConfigurationValidationDisplay({
        version: "v1",
        source: "BACKEND_USER_CONFIGURATION",
        schema_id: "sees.user_configuration.v2",
        validation_scope: "USER_PROVIDED_CONFIG_MAPPING",
        format: "JSON_MAPPING",
        mutation_policy: "VALIDATE_ONLY_NO_APPLY",
        unknown_key_policy: "REJECT",
        defaulting_policy: "OMITTED_FIELDS_USE_BACKEND_DEFAULTS",
        ok: true,
        error_count: 0,
        errors: [],
        normalized_config_hash:
          "sha256:abcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcd",
        normalized_config: {
          scenario: {
            satellite_count: 72
          }
        },
        text_parse: {
          version: "v1",
          source: "BACKEND_USER_CONFIGURATION",
          requested_format: "yaml",
          detected_format: "yaml",
          ok: true
        },
        apply_readiness: {
          version: "v1",
          source: "BACKEND_RUNTIME_STATUS",
          can_apply: true,
          readiness: "APPLY_ALLOWED_REINITIALIZES_SESSION",
          requires_confirmation: false,
          recommended_action: "APPLY_WHEN_READY",
          reason: "runtime session exists; applying config will rebuild the initialized session",
          runtime_initialized: false,
          controller_status: "STOPPED",
          lifecycle_state: "INITIALIZED",
          session_effect: "REINITIALIZES_SESSION",
          stream_effect: "STOPS_AND_RECREATES_STREAM_BUFFERS"
        },
        apply_command: {
          type: "CONFIG_UPDATE",
          action: "CONFIG_UPDATE",
          payload_source: "normalized_config",
          payload_format: "SEES_CONFIG_MAPPING",
          requires_preflight_ok: true,
          runtime_effect: "REINITIALIZES_SESSION_AND_STREAMS",
          requires_explicit_user_action: true
        }
      })
    ).toEqual({
      tone: "match",
      statusLabel: "配置可通过预检",
      detailLabel: "normalized abcdefabcdef",
      metaLabels: [
        "scope USER_PROVIDED_CONFIG_MAPPING",
        "mutation VALIDATE_ONLY_NO_APPLY",
        "unknown REJECT",
        "default OMITTED_FIELDS_USE_BACKEND_DEFAULTS",
        "text parsed",
        "format yaml",
        "requested yaml",
        "endpoint /scenario/user-config/validate-text?format=yaml",
        "apply CONFIG_UPDATE/CONFIG_UPDATE",
        "payload normalized_config",
        "effect REINITIALIZES_SESSION_AND_STREAMS"
      ],
      readinessLabels: [
        "可应用 APPLY_ALLOWED_REINITIALIZES_SESSION",
        "runtime STOPPED/INITIALIZED",
        "建议 APPLY_WHEN_READY",
        "无需额外确认",
        "session REINITIALIZES_SESSION",
        "stream STOPS_AND_RECREATES_STREAM_BUFFERS",
        "runtime session exists; applying config will rebuild the initialized session"
      ],
      changeLabels: [],
      changeRows: [],
      errorLabels: []
    });

    expect(
      buildDataPanelUserConfigurationValidationDisplay({
        version: "v1",
        source: "BACKEND_USER_CONFIGURATION",
        schema_id: "sees.user_configuration.v2",
        validation_scope: "USER_PROVIDED_CONFIG_MAPPING",
        format: "JSON_MAPPING",
        mutation_policy: "VALIDATE_ONLY_NO_APPLY",
        unknown_key_policy: "REJECT",
        defaulting_policy: "OMITTED_FIELDS_USE_BACKEND_DEFAULTS",
        ok: false,
        error_count: 1,
        errors: [
          {
            source: "config_loader",
            message: "unknown scenario keys: unsupported_compute_gpu"
          }
        ],
        normalized_config_hash: null,
        normalized_config: null,
        apply_command: {
          type: "CONFIG_UPDATE",
          action: "CONFIG_UPDATE",
          payload_source: "normalized_config",
          payload_format: "SEES_CONFIG_MAPPING",
          requires_preflight_ok: true,
          requires_explicit_user_action: true
        }
      })
    ).toMatchObject({
      tone: "error",
      statusLabel: "配置预检未通过",
      detailLabel: "1 个错误",
      errorLabels: ["config_loader: unknown scenario keys: unsupported_compute_gpu"]
    });
  });

  it("reports pending, request error, and empty validation states", () => {
    expect(buildDataPanelUserConfigurationValidationDisplay(null, true)).toMatchObject({
      tone: "pending",
      statusLabel: "后端预检中",
      readinessLabels: [],
      changeLabels: [],
      changeRows: []
    });
    expect(
      buildDataPanelUserConfigurationValidationDisplay(null, false, "HTTP 400")
    ).toMatchObject({
      tone: "error",
      statusLabel: "预检请求失败",
      readinessLabels: [],
      changeLabels: [],
      changeRows: [],
      errorLabels: ["HTTP 400"]
    });
    expect(buildDataPanelUserConfigurationValidationDisplay(null)).toBeNull();
  });

  it("renders backend user configuration change summaries", () => {
    const display = buildDataPanelUserConfigurationValidationDisplay({
      version: "v1",
      source: "BACKEND_USER_CONFIGURATION",
      schema_id: "sees.user_configuration.v2",
      validation_scope: "USER_PROVIDED_CONFIG_MAPPING",
      format: "JSON_MAPPING",
      mutation_policy: "VALIDATE_ONLY_NO_APPLY",
      unknown_key_policy: "REJECT",
      defaulting_policy: "OMITTED_FIELDS_USE_BACKEND_DEFAULTS",
      ok: true,
      error_count: 0,
      errors: [],
      normalized_config_hash:
        "sha256:abcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcd",
      normalized_config: {
        scenario: {
          satellite_count: 84
        }
      },
      change_summary: {
        version: "v1",
        source: "BACKEND_USER_CONFIGURATION",
        baseline: "CURRENT_EFFECTIVE_SEES_CONFIG",
        candidate: "NORMALIZED_USER_CONFIG",
        changed_field_count: 3,
        section_counts: {
          runtime: 1,
          scenario: 2
        },
        preview_limit: 24,
        change_count: 3,
        hidden_change_count: 0,
        changes: [
          {
            path: "runtime.duration",
            section: "runtime",
            change_type: "CHANGED",
            current_value: 120,
            candidate_value: 600
          },
          {
            path: "scenario.satellite_count",
            section: "scenario",
            change_type: "CHANGED",
            current_value: 12,
            candidate_value: 84
          }
        ]
      },
      apply_command: {
        type: "CONFIG_UPDATE",
        action: "CONFIG_UPDATE",
        payload_source: "normalized_config",
        requires_preflight_ok: true,
        requires_explicit_user_action: true
      }
    });

    expect(display).toMatchObject({
      changeLabels: [
        "变更 3 字段",
        "预览 3 / 24",
        "runtime 1",
        "scenario 2"
      ],
      changeRows: [
        {
          path: "runtime.duration",
          changeType: "CHANGED",
          valueLabel: "120 -> 600"
        },
        {
          path: "scenario.satellite_count",
          changeType: "CHANGED",
          valueLabel: "12 -> 84"
        }
      ]
    });
  });

  it("selects only backend-normalized explicit apply payloads", () => {
    const report = {
      version: "v1",
      source: "BACKEND_USER_CONFIGURATION",
      schema_id: "sees.user_configuration.v2",
      validation_scope: "USER_PROVIDED_CONFIG_MAPPING",
      format: "JSON_MAPPING",
      mutation_policy: "VALIDATE_ONLY_NO_APPLY",
      unknown_key_policy: "REJECT",
      defaulting_policy: "OMITTED_FIELDS_USE_BACKEND_DEFAULTS",
      ok: true,
      error_count: 0,
      errors: [],
      normalized_config_hash: "sha256:config",
      normalized_config: {
        scenario: {
          satellite_count: 72
        }
      },
      apply_command: {
        type: "CONFIG_UPDATE",
        action: "CONFIG_UPDATE",
        payload_source: "normalized_config",
        requires_preflight_ok: true,
        requires_explicit_user_action: true
      }
    };

    expect(selectUserConfigurationApplyPayload(report)).toEqual({
      scenario: {
        satellite_count: 72
      }
    });
    expect(
      selectUserConfigurationApplyPayload({
        ...report,
        apply_command: {
          ...report.apply_command,
          payload_source: "raw_text"
        }
      })
    ).toBeNull();
    expect(
      selectUserConfigurationApplyPayload({
        ...report,
        ok: false
      })
    ).toBeNull();
  });

  it("maps user configuration preflight modes to backend endpoint formats", () => {
    const mappingValidator = async () =>
      ({
        ok: true
      }) as UserConfigurationValidationReportV1;
    const textValidator = async () =>
      ({
        ok: true
      }) as UserConfigurationValidationReportV1;

    expect(userConfigurationTextEndpointFormat("auto_text")).toBe("auto");
    expect(userConfigurationTextEndpointFormat("yaml_text")).toBe("yaml");
    expect(userConfigurationTextEndpointFormat("json_text")).toBe("json");
    expect(userConfigurationTextEndpointFormat("json_mapping")).toBe("auto");
    expect(
      userConfigurationPreflightModeEnabled("json_mapping", mappingValidator, undefined)
    ).toBe(true);
    expect(
      userConfigurationPreflightModeEnabled("yaml_text", mappingValidator, undefined)
    ).toBe(false);
    expect(
      userConfigurationPreflightModeEnabled("yaml_text", undefined, textValidator)
    ).toBe(true);
  });
});

describe("buildDataPanelConfigurationExplanationDisplay", () => {
  it("summarizes backend-owned dashboard information architecture v3", () => {
    const display = buildDataPanelInformationArchitectureDisplay({
      version: "v3",
      architecture_id: "leo_twin.dashboard_information_architecture.v3",
      source: "BACKEND_DERIVED_SUMMARY",
      frontend_policy: "RENDER_BACKEND_SECTIONS_WITH_LOCAL_FORMATTING_ONLY",
      backend_source_of_truth: true,
      frontend_inference_policy: "Frontend must not invent model semantics.",
      layout_policy: {
        page_scroll: true,
        primary_order: ["OVERVIEW", "NETWORK"],
        section_grouping: "overview first",
        card_policy: "no nested cards",
        large_scale_policy: "detail rows must be bounded"
      },
      sections: [
        {
          section: "NETWORK",
          title_zh: "网络态势",
          title_en: "Network",
          priority: 20,
          purpose: "Explain network KPIs.",
          primary_data_sources: ["metrics_summary.network"],
          runtime_status_fields: ["metrics_summary.network"],
          detail_surfaces: ["network KPI trends", "route explanation table"],
          expected_controls: ["route search"],
          empty_state: "No network samples.",
          scale_behavior: "Use aggregate KPI series.",
          owner: "BACKEND_SUMMARY_CONTRACT"
        },
        {
          section: "OVERVIEW",
          title_zh: "总览",
          title_en: "Overview",
          priority: 10,
          purpose: "Show runtime health first.",
          primary_data_sources: ["RuntimeStatusPayload", "fidelity_summary"],
          runtime_status_fields: ["state", "current_sim_time"],
          detail_surfaces: ["runtime progress strip", "scale and fidelity notice"],
          expected_controls: ["export"],
          empty_state: "Waiting for status.",
          scale_behavior: "Always visible.",
          owner: "BACKEND_SUMMARY_CONTRACT"
        }
      ],
      determinism: {
        section_order: "priority_ascending_then_section_id",
        unknown_section_policy: "display_after_known_sections_with_backend_label",
        stable_identifiers: ["OVERVIEW", "NETWORK"]
      },
      follow_up_tasks: ["V2-051 user detail drawer"]
    });

    expect(display).toMatchObject({
      sourceLabel:
        "BACKEND_DERIVED_SUMMARY / leo_twin.dashboard_information_architecture.v3",
      summaryLabel:
        "2 个态势分区 / RENDER_BACKEND_SECTIONS_WITH_LOCAL_FORMATTING_ONLY",
      policyLabel: "后端为语义源；前端只做格式化",
      layoutLabel: "整页滚动 / detail rows must be bounded"
    });
    expect(display?.sections).toEqual([
      {
        section: "OVERVIEW",
        title: "OVERVIEW · 总览",
        purpose: "Show runtime health first.",
        sourcesLabel: "RuntimeStatusPayload / fidelity_summary",
        surfacesLabel:
          "runtime progress strip / scale and fidelity notice · Always visible."
      },
      {
        section: "NETWORK",
        title: "NETWORK · 网络态势",
        purpose: "Explain network KPIs.",
        sourcesLabel: "metrics_summary.network",
        surfacesLabel:
          "network KPI trends / route explanation table · Use aggregate KPI series."
      }
    ]);
    expect(buildDataPanelInformationArchitectureDisplay(null)).toBeNull();
    expect(buildDataPanelInformationArchitectureDisplay(undefined)).toBeNull();
  });

  it("summarizes backend-owned configuration explanation v2", () => {
    const display = buildDataPanelConfigurationExplanationDisplay({
      version: "v2",
      explanation_id: "leo_twin.configuration_explanation.v2",
      schema_id: "sees.user_configuration.v2",
      source: "BACKEND_DERIVED_SUMMARY",
      frontend_policy: "CONTROL_PANEL_KEY_FIELDS_ONLY",
      mutation_policy: "READ_ONLY_EXPLANATION",
      configuration_surfaces: [
        {
          surface: "CONTROL_PANEL_KEY_FIELDS",
          purpose: "Expose high-impact parameters.",
          source: "configuration_surface_summary.key_fields"
        },
        {
          surface: "CURRENT_EFFECTIVE_CONFIG_EXPORT",
          purpose: "Expose normalized config and stable hash.",
          source: "/scenario/user-config/export"
        }
      ],
      section_explanations: [
        {
          section: "scenario",
          title: "星座、用户和算力规模",
          source_fields: ["scenario.satellite_count", "scenario.user_count"],
          current_values: {
            satellite_count: 1200,
            user_count: 100,
            constellation_profile: "CUSTOM_WALKER",
            ignored_null: null
          },
          model_semantics: "Scenario fields define deterministic scale.",
          excluded_semantics: ["SGP4", "RF_LINK_BUDGET"]
        },
        {
          section: "traffic",
          title: "业务需求生成",
          source_fields: ["scenario.traffic_model.*"],
          current_values: {
            traffic_class: "COMPUTE_SERVICE",
            active_service_classes: ["DATA_TRANSFER", "COMPUTE_SERVICE"],
            packet_level_simulation: false
          },
          model_semantics: "Traffic fields generate flow-level requests.",
          excluded_semantics: ["PACKET_GENERATION"]
        }
      ],
      determinism: {
        seed_source: "runtime.seed",
        ordered_generation: true,
        unknown_key_policy: "REJECT",
        defaulting_policy: "OMITTED_FIELDS_USE_BACKEND_DEFAULTS",
        result_package_expectation: "config snapshot, events.jsonl, metrics.csv, summary.json"
      },
      forbidden_integrations: ["STK", "EXATA", "AFSIM", "DDS"],
      packet_level_simulation: false,
      model_boundary_note: "Read-only explanation."
    });

    expect(display).toMatchObject({
      sourceLabel: "BACKEND_DERIVED_SUMMARY / sees.user_configuration.v2",
      summaryLabel: "2 个配置入口 / 2 个语义分组 / READ_ONLY_EXPLANATION",
      determinismLabel:
        "seed runtime.seed / unknown REJECT / default OMITTED_FIELDS_USE_BACKEND_DEFAULTS",
      boundaryLabel: "STK/EXATA/AFSIM/DDS 禁止；无包级仿真"
    });
    expect(display?.surfaces).toEqual([
      {
        surface: "CONTROL_PANEL_KEY_FIELDS",
        label:
          "CONTROL_PANEL_KEY_FIELDS · configuration_surface_summary.key_fields",
        purpose: "Expose high-impact parameters."
      },
      {
        surface: "CURRENT_EFFECTIVE_CONFIG_EXPORT",
        label: "CURRENT_EFFECTIVE_CONFIG_EXPORT · /scenario/user-config/export",
        purpose: "Expose normalized config and stable hash."
      }
    ]);
    expect(display?.sections).toEqual([
      {
        section: "scenario",
        title: "scenario · 星座、用户和算力规模",
        currentValueLabel:
          "satellite_count=1,200 / user_count=100 / constellation_profile=CUSTOM_WALKER",
        sourceFieldsLabel: "scenario.satellite_count / scenario.user_count",
        excludedSemanticsLabel: "排除 SGP4 / RF_LINK_BUDGET"
      },
      {
        section: "traffic",
        title: "traffic · 业务需求生成",
        currentValueLabel:
          "traffic_class=COMPUTE_SERVICE / active_service_classes=DATA_TRANSFER,COMPUTE_SERVICE / packet_level_simulation=false",
        sourceFieldsLabel: "scenario.traffic_model.*",
        excludedSemanticsLabel: "排除 PACKET_GENERATION"
      }
    ]);
  });

  it("returns null when configuration explanation is unavailable", () => {
    expect(buildDataPanelConfigurationExplanationDisplay(null)).toBeNull();
    expect(buildDataPanelConfigurationExplanationDisplay(undefined)).toBeNull();
  });
});

describe("buildDataPanelExportHistoryDisplay", () => {
  it("summarizes the latest backend export history record", () => {
    expect(
      buildDataPanelExportHistoryDisplay({
        version: "v1",
        source: "BACKEND_RUNTIME_STATUS",
        history_scope: "CURRENT_SESSION_RECENT_EXPORTS",
        history_limit: 8,
        export_count: 2,
        retained_count: 2,
        latest_export: {
          sequence: 2,
          export_type: "ARCHIVE",
          package_id: "integration-demo-7-t00000012p000-e00000040",
          package_dir: "artifacts/runtime_exports/demo",
          file_count: 6,
          manifest_hash:
            "sha256:1111111111111111111111111111111111111111111111111111111111111111",
          current_sim_time: 12,
          processed_event_count: 40,
          archive_filename: "integration-demo-7.zip",
          archive_sha256:
            "sha256:abcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcd",
          archive_bytes: 4096
        },
        items: []
      })
    ).toEqual({
      primaryLabel: "ARCHIVE / integration-demo-7.zip",
      secondaryLabel: "t=12s / events=40 / abcdefabcdef"
    });
    expect(buildDataPanelExportHistoryDisplay(undefined)).toBeNull();
  });
});

describe("buildDataPanelExportCatalogDisplay", () => {
  it("summarizes backend persisted export catalog rows in newest-first order", () => {
    const display = buildDataPanelExportCatalogDisplay({
      version: "v1",
      source: "BACKEND_RUNTIME_EXPORT_CATALOG",
      catalog_scope: "PERSISTED_EXPORT_PACKAGES",
      catalog_file: "artifacts/runtime_exports/runtime_export_catalog_v1.json",
      export_root: "artifacts/runtime_exports",
      record_count: 2,
      catalog_hash:
        "sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
      latest_export: null,
      records: [
        {
          catalog_key: "PACKAGE:old",
          export_type: "PACKAGE",
          package_id: "integration-demo-old",
          package_dir: "artifacts/runtime_exports/old",
          relative_package_dir: "old",
          file_count: 5,
          manifest_hash:
            "sha256:1111111111111111111111111111111111111111111111111111111111111111",
          current_sim_time: 4,
          processed_event_count: 100,
          files: []
        },
        {
          catalog_key: "ARCHIVE:new",
          export_type: "ARCHIVE",
          package_id: "integration-demo-new",
          package_dir: "artifacts/runtime_exports/new",
          relative_package_dir: "new",
          file_count: 6,
          manifest_hash:
            "sha256:2222222222222222222222222222222222222222222222222222222222222222",
          current_sim_time: 12.5,
          processed_event_count: 4096,
          archive_filename: "integration-demo-new.zip",
          archive_sha256:
            "sha256:abcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcd",
          archive_bytes: 8192,
          files: []
        }
      ]
    });

    expect(display).toMatchObject({
      sourceLabel: "BACKEND_RUNTIME_EXPORT_CATALOG / PERSISTED_EXPORT_PACKAGES",
      summaryLabel: "已登记 2 条 / 显示 2 条 / catalog cccccccccccc",
      rows: [
        {
          key: "ARCHIVE:new",
          typeLabel: "ARCHIVE",
          packageId: "integration-demo-new",
          simTimeLabel: "12.5 s",
          eventCountLabel: "4,096",
          archiveLabel: "integration-demo-new.zip",
          hashLabel: "abcdefabcdef",
          recordHref: "/runtime/export/packages/integration-demo-new",
          manifestHref: "/runtime/export/packages/integration-demo-new/manifest",
          archiveHref: "/runtime/export/packages/integration-demo-new/archive",
          compareHref: "/runtime/export/packages/integration-demo-new/compare",
          restorePreflightHref:
            "/runtime/export/packages/integration-demo-new/restore-preflight"
        },
        {
          key: "PACKAGE:old",
          typeLabel: "PACKAGE",
          packageId: "integration-demo-old",
          simTimeLabel: "4 s",
          eventCountLabel: "100",
          archiveLabel: "未生成归档",
          hashLabel: "111111111111",
          recordHref: "/runtime/export/packages/integration-demo-old",
          manifestHref: "/runtime/export/packages/integration-demo-old/manifest",
          archiveHref: null,
          compareHref: "/runtime/export/packages/integration-demo-old/compare",
          restorePreflightHref:
            "/runtime/export/packages/integration-demo-old/restore-preflight"
        }
      ]
    });
  });

  it("returns null before backend catalog is loaded", () => {
    expect(buildDataPanelExportCatalogDisplay(undefined)).toBeNull();
  });
});

describe("buildDataPanelExportCompareDisplay", () => {
  it("summarizes matching package compare previews", () => {
    expect(
      buildDataPanelExportCompareDisplay({
        version: "v1",
        source: "BACKEND_RUNTIME_EXPORT_COMPARE",
        comparison_scope: "CONFIG_AND_GENERATED_CONFIG",
        package_id: "pkg-match",
        compatibility: "MATCH",
        same_config: true,
        same_generated_config: true,
        same_manifest_hash: true,
        package_manifest_hash: "sha256:old",
        current_manifest_hash: "sha256:old",
        diff_count: 0,
        diff_limit: 32,
        diff_truncated: false,
        sections: [],
        differences: [],
        compare_hash:
          "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
      })
    ).toEqual({
      packageId: "pkg-match",
      tone: "match",
      statusLabel: "配置一致",
      summaryLabel: "pkg-match / 差异 0 项",
      configLabel: "config 一致",
      generatedConfigLabel: "generated 一致",
      hashLabel: "compare aaaaaaaaaaaa",
      diffRows: []
    });
  });

  it("summarizes changed package compare previews with bounded diff rows", () => {
    expect(
      buildDataPanelExportCompareDisplay(
        {
          version: "v1",
          source: "BACKEND_RUNTIME_EXPORT_COMPARE",
          comparison_scope: "CONFIG_AND_GENERATED_CONFIG",
          package_id: "pkg-diff",
          compatibility: "DIFFERENT",
          same_config: false,
          same_generated_config: false,
          same_manifest_hash: false,
          package_manifest_hash: "sha256:old",
          current_manifest_hash: "sha256:new",
          diff_count: 3,
          diff_limit: 2,
          diff_truncated: true,
          sections: [
            { section: "config", diff_count: 1, matches: false },
            { section: "generated_config", diff_count: 2, matches: false }
          ],
          differences: [
            {
              section: "config",
              path: "$.scenario.satellite_count",
              package_missing: false,
              current_missing: false,
              package_value: 72,
              current_value: 120
            },
            {
              section: "generated_config",
              path: "$.satellite_count",
              package_missing: false,
              current_missing: false,
              package_value: 72,
              current_value: 120
            }
          ],
          compare_hash:
            "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
        },
        1
      )
    ).toMatchObject({
      packageId: "pkg-diff",
      tone: "different",
      statusLabel: "配置不同",
      summaryLabel: "pkg-diff / 差异 3 项 / 显示 1 项",
      configLabel: "config 不同",
      generatedConfigLabel: "generated 不同",
      hashLabel: "compare bbbbbbbbbbbb",
      diffRows: [
        {
          section: "config",
          path: "$.scenario.satellite_count",
          valueLabel: "72 -> 120"
        }
      ]
    });
  });

  it("returns null before package compare preview is loaded", () => {
    expect(buildDataPanelExportCompareDisplay(undefined)).toBeNull();
  });
});

describe("buildDataPanelExportCompareStatus", () => {
  const display = {
    packageId: "pkg-1",
    tone: "different" as const,
    statusLabel: "配置不同",
    summaryLabel: "pkg-1 / 差异 2 项",
    configLabel: "config 不同",
    generatedConfigLabel: "generated 不同",
    hashLabel: "compare abcdefabcdef",
    diffRows: [
      {
        section: "config",
        path: "$.scenario.satellite_count",
        valueLabel: "72 -> 120",
        title: "config $.scenario.satellite_count: 72 -> 120"
      }
    ]
  };

  it("prefers loading and error state over stale compare display", () => {
    expect(buildDataPanelExportCompareStatus(display, "pkg-2", true, null)).toEqual({
      tone: "pending",
      statusLabel: "正在加载对比",
      summaryLabel: "pkg-2",
      metaLabels: ["只读预览", "不修改当前配置"],
      diffRows: []
    });
    expect(
      buildDataPanelExportCompareStatus(display, "pkg-2", false, "后端 404")
    ).toEqual({
      tone: "error",
      statusLabel: "对比加载失败",
      summaryLabel: "pkg-2",
      metaLabels: ["后端 404"],
      diffRows: []
    });
  });

  it("maps loaded compare display into dashboard status", () => {
    expect(buildDataPanelExportCompareStatus(display, "pkg-1", false, null)).toEqual({
      tone: "different",
      statusLabel: "配置不同",
      summaryLabel: "pkg-1 / 差异 2 项",
      metaLabels: ["config 不同", "generated 不同", "compare abcdefabcdef"],
      diffRows: display.diffRows
    });
    expect(buildDataPanelExportCompareStatus(null, null, false, null)).toBeNull();
  });
});

describe("buildDataPanelExportRestorePreflightDisplay", () => {
  it("summarizes no-change restore preflights", () => {
    expect(
      buildDataPanelExportRestorePreflightDisplay({
        version: "v1",
        source: "BACKEND_RUNTIME_EXPORT_RESTORE_PREFLIGHT",
        preflight_scope: "CONFIG_RESTORE_PREVIEW_ONLY",
        package_id: "pkg-same",
        readiness: "NO_CHANGE",
        can_restore: true,
        requires_user_confirmation: false,
        would_mutate_current_runtime: false,
        would_write_config_files: false,
        would_reset_runtime_session: false,
        would_stop_live_streams: false,
        current_lifecycle_state: "PAUSED",
        package_config_hash: "sha256:aaa",
        current_config_hash: "sha256:aaa",
        same_config: true,
        same_generated_config: true,
        config_diff_count: 0,
        generated_config_diff_count: 0,
        compare_hash: "sha256:compare",
        blocked_reasons: [],
        warnings: [],
        next_action: "NO_RESTORE_REQUIRED",
        preflight_hash:
          "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
      })
    ).toEqual({
      packageId: "pkg-same",
      readiness: "NO_CHANGE",
      canRestore: true,
      tone: "match",
      statusLabel: "无需恢复",
      summaryLabel: "pkg-same / config差异 0 / generated差异 0",
      metaLabels: [
        "确认 不需要",
        "写配置 不会",
        "重置runtime 不会",
        "当前 PAUSED",
        "preflight aaaaaaaaaaaa"
      ],
      warningRows: []
    });
  });

  it("summarizes ready and blocked restore preflights", () => {
    const ready = buildDataPanelExportRestorePreflightDisplay({
      version: "v1",
      source: "BACKEND_RUNTIME_EXPORT_RESTORE_PREFLIGHT",
      preflight_scope: "CONFIG_RESTORE_PREVIEW_ONLY",
      package_id: "pkg-ready",
      readiness: "READY",
      can_restore: true,
      requires_user_confirmation: true,
      would_mutate_current_runtime: false,
      would_write_config_files: true,
      would_reset_runtime_session: true,
      would_stop_live_streams: true,
      current_lifecycle_state: "RUNNING",
      package_config_hash: "sha256:old",
      current_config_hash: "sha256:new",
      same_config: false,
      same_generated_config: false,
      config_diff_count: 2,
      generated_config_diff_count: 4,
      compare_hash: "sha256:compare",
      blocked_reasons: [],
      warnings: ["RESTORE_WOULD_STOP_RUNNING_SESSION"],
      next_action: "USER_CONFIRMATION_REQUIRED_BEFORE_RESTORE",
      preflight_hash:
        "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
    });
    expect(ready).toMatchObject({
      tone: "different",
      statusLabel: "可恢复，需确认",
      summaryLabel: "pkg-ready / config差异 2 / generated差异 4",
      warningRows: ["警告: RESTORE_WOULD_STOP_RUNNING_SESSION"]
    });

    const blocked = buildDataPanelExportRestorePreflightDisplay({
      version: "v1",
      source: "BACKEND_RUNTIME_EXPORT_RESTORE_PREFLIGHT",
      preflight_scope: "CONFIG_RESTORE_PREVIEW_ONLY",
      package_id: "pkg-blocked",
      readiness: "BLOCKED",
      can_restore: false,
      requires_user_confirmation: false,
      would_mutate_current_runtime: false,
      would_write_config_files: false,
      would_reset_runtime_session: false,
      would_stop_live_streams: false,
      current_lifecycle_state: "PAUSED",
      package_config_hash: "",
      current_config_hash: "sha256:new",
      same_config: false,
      same_generated_config: false,
      config_diff_count: 0,
      generated_config_diff_count: 0,
      compare_hash: "sha256:compare",
      blocked_reasons: ["package config is invalid"],
      warnings: [],
      next_action: "FIX_PACKAGE_OR_SELECT_ANOTHER_EXPORT",
      preflight_hash:
        "sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
    });
    expect(blocked).toMatchObject({
      tone: "error",
      statusLabel: "预检阻塞",
      warningRows: ["阻塞: package config is invalid"]
    });
  });

  it("maps restore preflight loading and error state", () => {
    const display = buildDataPanelExportRestorePreflightDisplay({
      version: "v1",
      source: "BACKEND_RUNTIME_EXPORT_RESTORE_PREFLIGHT",
      preflight_scope: "CONFIG_RESTORE_PREVIEW_ONLY",
      package_id: "pkg-ready",
      readiness: "READY",
      can_restore: true,
      requires_user_confirmation: true,
      would_mutate_current_runtime: false,
      would_write_config_files: true,
      would_reset_runtime_session: true,
      would_stop_live_streams: true,
      current_lifecycle_state: "PAUSED",
      package_config_hash: "sha256:old",
      current_config_hash: "sha256:new",
      same_config: false,
      same_generated_config: false,
      config_diff_count: 2,
      generated_config_diff_count: 4,
      compare_hash: "sha256:compare",
      blocked_reasons: [],
      warnings: [],
      next_action: "USER_CONFIRMATION_REQUIRED_BEFORE_RESTORE",
      preflight_hash:
        "sha256:dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"
    });
    expect(buildDataPanelExportRestorePreflightStatus(display, "pkg-2", true)).toMatchObject({
      tone: "pending",
      statusLabel: "正在加载预检",
      summaryLabel: "pkg-2",
      metaLabels: ["只读预检", "不会修改当前配置"],
      warningRows: []
    });
    expect(
      buildDataPanelExportRestorePreflightStatus(display, "pkg-2", false, "HTTP 404")
    ).toMatchObject({
      tone: "error",
      statusLabel: "预检加载失败",
      summaryLabel: "pkg-2",
      metaLabels: ["HTTP 404"],
      warningRows: []
    });
    expect(buildDataPanelExportRestorePreflightStatus(display, "pkg-ready")).toMatchObject({
      tone: "different",
      statusLabel: "可恢复，需确认"
    });
    expect(buildDataPanelExportRestorePreflightStatus(null, null)).toBeNull();
  });
});

describe("buildDataPanelExportRestoreActionDisplay", () => {
  const readyStatus = {
    tone: "different" as const,
    packageId: "pkg-ready",
    readiness: "READY",
    canRestore: true,
    statusLabel: "ready",
    summaryLabel: "pkg-ready",
    metaLabels: [],
    warningRows: []
  };

  it("requires a second click before sending restore", () => {
    expect(buildDataPanelExportRestoreActionDisplay(readyStatus)).toMatchObject({
      packageId: "pkg-ready",
      tone: "ready",
      disabled: false,
      requiresSecondClick: true
    });
    expect(
      buildDataPanelExportRestoreActionDisplay(readyStatus, {
        armedPackageId: "pkg-ready"
      })
    ).toMatchObject({
      packageId: "pkg-ready",
      tone: "confirm",
      disabled: false,
      requiresSecondClick: false
    });
  });

  it("reports pending, success and blocked restore actions", () => {
    expect(
      buildDataPanelExportRestoreActionDisplay(readyStatus, {
        pendingPackageId: "pkg-ready"
      })
    ).toMatchObject({
      tone: "pending",
      disabled: true
    });
    expect(
      buildDataPanelExportRestoreActionDisplay(readyStatus, {
        result: {
          version: "v1",
          source: "BACKEND_RUNTIME_EXPORT_RESTORE_COMMAND",
          package_id: "pkg-ready",
          readiness: "READY",
          restored: true,
          wrote_config_files: true,
          reset_runtime_session: true,
          stopped_live_streams: true,
          preflight_hash: "sha256:preflight",
          restored_config_hash: "sha256:old",
          previous_config_hash: "sha256:new",
          rollback_package_id: "rollback-pkg-1",
          rollback_package_dir: "artifacts/runtime_exports/rollback-pkg-1",
          rollback_catalog_key: "PACKAGE:rollback-pkg-1",
          restore_result_hash: "sha256:result"
        }
      })
    ).toMatchObject({
      tone: "success",
      disabled: true
    });
    expect(
      buildDataPanelExportRestoreActionDisplay({
        ...readyStatus,
        readiness: "BLOCKED",
        canRestore: false,
        tone: "error"
      })
    ).toMatchObject({
      tone: "disabled",
      disabled: true
    });
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

  it("summarizes backend traffic generation semantics when provided", () => {
    const display = buildDataPanelTrafficDisplay({
      traffic_class: "COMPUTE_SERVICE",
      traffic_class_label: "通信-计算服务",
      destination_type: "COMPUTE_NODE",
      destination_type_label: "星上算力节点",
      generated_flow_count: 120,
      generated_task_count: 120,
      generated_output_flow_metadata_count: 120,
      arrival_model: "DETERMINISTIC_INTERVAL",
      source_selection_policy: "ROUND_ROBIN_GROUND_USERS",
      destination_selection_policy: "ROUND_ROBIN_COMPUTE_NODES",
      input_data_size_mb: 2,
      output_data_size_mb: 0.5,
      total_input_data_mb: 240,
      total_output_data_mb: 60,
      priority: 0,
      demand_capacity_mbps: 25,
      task_compute_demand: 20,
      service_mix_mode: "WEIGHTED_MIX",
      service_mix_normalized_weights: {
        DATA_TRANSFER: 0.6666666667,
        TELEMETRY: 0,
        BULK_DOWNLINK: 0,
        COMPUTE_SERVICE: 0.3333333333
      },
      active_service_classes: ["DATA_TRANSFER", "COMPUTE_SERVICE"],
      service_mix_generated_request_counts: {
        DATA_TRANSFER: 80,
        TELEMETRY: 0,
        BULK_DOWNLINK: 0,
        COMPUTE_SERVICE: 40
      },
      execution_shape: "FLOW_THEN_COMPUTE_TASK",
      execution_label: "输入流 + 计算任务",
      requires_compute_node_destination: true,
      lifecycle_note: "输入流完成后触发计算任务。",
      arrival_interval_seconds: 60,
      system_request_rate_per_minute: 1,
      average_user_request_rate_per_minute: 0.001
    });

    expect(display.label).toBe("通信-计算服务 / 星上算力节点 / 输入流 + 计算任务");
    expect(display.note).toContain(
      "业务组合: 数据传输 66.7% / 80 请求 + 通信-计算服务 33.3% / 40 请求"
    );
    expect(display.note).toContain("生成 120 流 / 120 任务 / 120 结果流元数据");
    expect(display.note).toContain("数据 240 MB 输入 / 60 MB 输出");
    expect(display.note).toContain("速率 1 次/分钟 / 单用户 0.001 次/分钟");
    expect(display.note).toContain(
      "源/目的 ROUND_ROBIN_GROUND_USERS -> ROUND_ROBIN_COMPUTE_NODES"
    );
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

  it("prefers structured backend KPI provenance when available", () => {
    const source = buildDataPanelNetworkKpiSource(
      makeSnapshot(),
      {
        network_quality_effective_throughput_mbps: 77,
        network_quality_effective_latency_avg_s: 0.15
      },
      undefined,
      {
        version: "v1",
        metric_model: "FLOW_LEVEL_PROXY",
        packet_level_simulation: false,
        proxy_note: "Flow-level proxy only; no packet-level simulation is performed.",
        sources: {
          throughput: {
            source: "COMPLETED_FLOW_CAPACITY",
            label: "structured-throughput"
          },
          latency: {
            source: "COMPLETED_FLOW_LATENCY",
            label: "structured-latency"
          },
          loss: {
            source: "PRESSURE_LOSS_PROXY",
            label: "structured-loss"
          },
          delay_variation: {
            source: "FLOW_LATENCY_VARIATION",
            label: "structured-jitter"
          }
        },
        zero_reasons: {
          loss: {
            reason: "NO_LOSS_PROXY_TRIGGERED",
            label: "structured-loss-zero"
          },
          delay_variation: {
            reason: "INSUFFICIENT_VARIATION_SAMPLE",
            label: "structured-jitter-zero"
          }
        }
      }
    );

    expect(source.modelNote).toContain("structured-throughput");
    expect(source.modelNote).toContain("structured-jitter");
    expect(source.caveats.some((item) => item.includes("structured-loss-zero"))).toBe(
      true
    );
    expect(source.caveats.some((item) => item.includes("structured-jitter-zero"))).toBe(
      true
    );
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

describe("buildDataPanelNetworkKpiProvenanceItems", () => {
  it("explains recent flow-window KPI chart fields from backend provenance", () => {
    const items = buildDataPanelNetworkKpiProvenanceItems(
      {
        network_quality_throughput_source_label: "已完成流容量",
        network_quality_latency_source_label: "已完成流时延",
        network_quality_loss_source_label: "近期失败流比例",
        network_quality_delay_variation_source_label: "近期流时延离散度",
        network_quality_metric_model: "FLOW_LEVEL_PROXY"
      },
      {
        version: "v1",
        samples: [
          {
            sim_time: 70,
            network_effective_throughput_mbps: 150,
            network_effective_latency_s: 0.11,
            network_effective_loss_proxy_rate: 0.04,
            network_effective_delay_variation_s: 0.006,
            network_recent_window_s: 60,
            network_recent_flow_count: 3,
            network_recent_delivered_throughput_mbps: 65,
            network_recent_latency_s: 0.18,
            network_recent_loss_proxy_rate: 0.25,
            network_recent_loss_zero_reason_label: "当前代理指标为正值",
            network_recent_delay_variation_s: 0.012,
            network_recent_delay_variation_zero_reason_label: "当前代理指标为正值",
            compute_resource_used_gflops_fp32: 2500
          }
        ]
      }
    );

    expect(items.map((item) => [item.label, item.value])).toEqual([
      ["曲线窗口", "最近 1分0秒 完成流"],
      ["窗口样本", "3 条完成流"],
      ["吞吐", "已完成流容量"],
      ["时延", "已完成流时延"],
      ["丢包", "近期失败流比例"],
      ["抖动", "近期流时延离散度"],
      ["语义", "流级代理 / 非包级"]
    ]);
  });

  it("surfaces recent-window zero reasons from backend KPI samples", () => {
    const items = buildDataPanelNetworkKpiProvenanceItems(
      {
        network_quality_metric_model: "FLOW_LEVEL_PROXY"
      },
      {
        version: "v1",
        samples: [
          {
            sim_time: 70,
            network_effective_throughput_mbps: 150,
            network_effective_latency_s: 0.11,
            network_effective_loss_proxy_rate: 0,
            network_effective_delay_variation_s: 0,
            network_recent_window_s: 60,
            network_recent_flow_count: 0,
            network_recent_delivered_throughput_mbps: 0,
            network_recent_latency_s: 0,
            network_recent_loss_proxy_rate: 0,
            network_recent_loss_zero_reason_label:
              "最近窗口暂无完成流，零值仅表示窗口未形成样本",
            network_recent_delay_variation_s: 0,
            network_recent_delay_variation_zero_reason_label:
              "最近窗口暂无完成流，零值仅表示窗口未形成样本",
            compute_resource_used_gflops_fp32: 2500
          }
        ]
      }
    );

    expect(items.map((item) => [item.label, item.value])).toEqual([
      ["曲线窗口", "最近 1分0秒 完成流"],
      ["窗口样本", "0 条完成流"],
      ["窗口丢包", "最近窗口暂无完成流，零值仅表示窗口未形成样本"],
      ["窗口抖动", "最近窗口暂无完成流，零值仅表示窗口未形成样本"],
      ["语义", "流级代理 / 非包级"]
    ]);
  });

  it("prefers structured runtime provenance and falls back to cumulative mode", () => {
    const items = buildDataPanelNetworkKpiProvenanceItems(
      {},
      undefined,
      {
        version: "v1",
        metric_model: "FLOW_LEVEL_PROXY",
        packet_level_simulation: false,
        sources: {
          throughput: {
            source: "COMPLETED_FLOW_CAPACITY",
            label: "structured-throughput"
          },
          latency: {
            source: "COMPLETED_FLOW_LATENCY",
            label: "structured-latency"
          },
          loss: {
            source: "PRESSURE_LOSS_PROXY",
            label: "structured-loss"
          },
          delay_variation: {
            source: "FLOW_LATENCY_VARIATION",
            label: "structured-jitter"
          }
        },
        zero_reasons: {}
      }
    );

    expect(items.map((item) => [item.label, item.value])).toEqual([
      ["曲线窗口", "累计有效指标"],
      ["吞吐", "structured-throughput"],
      ["时延", "structured-latency"],
      ["丢包", "structured-loss"],
      ["抖动", "structured-jitter"],
      ["语义", "流级代理 / 非包级"]
    ]);
  });
});

describe("buildDataPanelNetworkKpiCredibilityDisplay", () => {
  it("formats complete backend network KPI credibility as a trusted flow-level proxy", () => {
    expect(
      buildDataPanelNetworkKpiCredibilityDisplay({
        version: "v1",
        credibility_id: "leo_twin.network_kpi_credibility.v1",
        source: "NETWORK_KPI_PROVENANCE_V2",
        provenance_id: "leo_twin.network_kpi_provenance.v2",
        metric_model: "FLOW_LEVEL_PROXY",
        packet_level_simulation: false,
        credibility_status: "COMPLETE_FLOW_LEVEL_PROXY",
        kpi_count: 6,
        observed_kpi_count: 6,
        missing_kpi_count: 0,
        packet_level_metric_count: 0,
        flow_level_proxy_metric_count: 6,
        zero_value_kpi_count: 2,
        zero_value_explained_count: 2,
        source_field_count: 18,
        observed_source_field_count: 18,
        missing_source_field_count: 0,
        missing_metrics: [],
        zero_unexplained_metrics: [],
        caveats: ["All network KPIs are flow-level proxies.", "No packet-level simulation."]
      })
    ).toEqual({
      tone: "match",
      statusLabel: "完整流级代理",
      summaryLabel: "KPI 6/6 有运行值；来源字段 18/18 可观测",
      metaLabels: [
        "模型 流级代理",
        "流级代理 6",
        "无包级指标",
        "零值解释 2/2",
        "缺失 KPI 0"
      ],
      caveats: ["All network KPIs are flow-level proxies.", "No packet-level simulation."]
    });
  });

  it("surfaces missing runtime KPI values from backend credibility fields", () => {
    const display = buildDataPanelNetworkKpiCredibilityDisplay({
      version: "v1",
      credibility_id: "leo_twin.network_kpi_credibility.v1",
      source: "NETWORK_KPI_PROVENANCE_V2",
      provenance_id: "leo_twin.network_kpi_provenance.v2",
      metric_model: "FLOW_LEVEL_PROXY",
      packet_level_simulation: false,
      credibility_status: "PARTIAL_RUNTIME_VALUES",
      kpi_count: 6,
      observed_kpi_count: 4,
      missing_kpi_count: 2,
      packet_level_metric_count: 0,
      flow_level_proxy_metric_count: 6,
      zero_value_kpi_count: 1,
      zero_value_explained_count: 0,
      source_field_count: 18,
      observed_source_field_count: 12,
      missing_source_field_count: 6,
      missing_metrics: ["network_effective_loss_proxy_rate", "network_effective_jitter_s"],
      zero_unexplained_metrics: ["network_effective_loss_proxy_rate"],
      caveats: ["Missing runtime KPI values."]
    });

    expect(display).toMatchObject({
      tone: "different",
      statusLabel: "部分运行值",
      summaryLabel: "KPI 4/6 有运行值；来源字段 12/18 可观测"
    });
    expect(display?.metaLabels).toContain("缺失 KPI 2");
    expect(display?.caveats).toContain(
      "缺失指标：network_effective_loss_proxy_rate, network_effective_jitter_s"
    );
    expect(display?.caveats).toContain(
      "零值未解释：network_effective_loss_proxy_rate"
    );
  });

  it("marks packet-level KPI declarations as invalid for the current product mode", () => {
    const display = buildDataPanelNetworkKpiCredibilityDisplay({
      version: "v1",
      credibility_id: "leo_twin.network_kpi_credibility.v1",
      source: "NETWORK_KPI_PROVENANCE_V2",
      provenance_id: "leo_twin.network_kpi_provenance.v2",
      metric_model: "FLOW_LEVEL_PROXY",
      packet_level_simulation: false,
      credibility_status: "INVALID_PACKET_LEVEL_METRIC",
      kpi_count: 6,
      observed_kpi_count: 6,
      missing_kpi_count: 0,
      packet_level_metric_count: 1,
      flow_level_proxy_metric_count: 5,
      zero_value_kpi_count: 0,
      zero_value_explained_count: 0,
      source_field_count: 18,
      observed_source_field_count: 18,
      missing_source_field_count: 0,
      missing_metrics: [],
      zero_unexplained_metrics: [],
      caveats: ["Packet-level metric is not allowed."]
    });

    expect(display?.tone).toBe("error");
    expect(display?.statusLabel).toBe("包级指标越界");
    expect(display?.metaLabels).toContain("包级指标 1");
  });

  it("hides the credibility card until backend status provides the summary", () => {
    expect(buildDataPanelNetworkKpiCredibilityDisplay(null)).toBeNull();
    expect(buildDataPanelNetworkKpiCredibilityDisplay(undefined)).toBeNull();
  });
});

describe("buildDataPanelModelAssumptionsDisplay", () => {
  it("combines backend model assumptions, fidelity warnings, and KPI credibility", () => {
    const display = buildDataPanelModelAssumptionsDisplay(
      [
        "Network behavior is flow-level, not packet-level.",
        "Compute capacity is a deterministic abstract resource vector."
      ],
      {
        orbit_update_mode: "BATCH",
        metrics_mode: "AGGREGATED",
        space_link_mode: "BOUNDED_CANDIDATE",
        detailed_space_link_enabled: false,
        space_link_candidate_policy: "SAME_PLANE_AND_ADJACENT_PLANE_BOUNDED_CANDIDATES",
        max_space_link_candidates_per_satellite: 4,
        batch_space_link_update_limit: 999,
        scale_limit_reason: "satellite_count >= 300",
        current_scale_mode: "LARGE_SCALE_AGGREGATED",
        fidelity_warnings: [
          "Orbit updates are batched.",
          "Space-space links use bounded candidate updates."
        ],
        satellite_count: 1200,
        user_count: 100
      },
      {
        tone: "match",
        statusLabel: "完整流级代理",
        summaryLabel: "KPI 6/6 有运行值；来源字段 18/18 可观测",
        metaLabels: ["模型 流级代理", "无包级指标"],
        caveats: ["No packet-level simulation.", "Loss is pressure proxy."]
      },
      {
        sourceLabel: "BACKEND_DERIVED_SUMMARY / sees.user_configuration.v2",
        summaryLabel: "2 个配置入口 / 6 个语义分组 / READ_ONLY_EXPLANATION",
        determinismLabel:
          "seed runtime.seed / unknown REJECT / default OMITTED_FIELDS_USE_BACKEND_DEFAULTS",
        boundaryLabel: "STK/EXATA/AFSIM/DDS 禁止；无包级仿真",
        surfaces: [],
        sections: []
      }
    );

    expect(display).toMatchObject({
      sourceLabel: "backend_summary.model_assumptions + runtime credibility",
      summaryLabel: "2 条假设 / 3 条规模边界 / 3 条KPI边界",
      boundaryLabel: "STK/EXATA/AFSIM/DDS 禁止；无包级仿真",
      fidelityLabel: "LARGE_SCALE_AGGREGATED / 1,200 星 / 100 用户"
    });
    expect(display?.rows).toEqual([
      {
        kind: "assumption",
        label: "模型假设 1",
        detail: "Network behavior is flow-level, not packet-level.",
        source: "backend_summary.model_assumptions"
      },
      {
        kind: "assumption",
        label: "模型假设 2",
        detail: "Compute capacity is a deterministic abstract resource vector.",
        source: "backend_summary.model_assumptions"
      },
      {
        kind: "fidelity",
        label: "规模保真策略",
        detail:
          "orbit=BATCH / metrics=AGGREGATED / space=BOUNDED_CANDIDATE / satellite_count >= 300",
        source: "fidelity_summary"
      },
      {
        kind: "fidelity",
        label: "规模提示 1",
        detail: "Orbit updates are batched.",
        source: "fidelity_summary.fidelity_warnings"
      },
      {
        kind: "fidelity",
        label: "规模提示 2",
        detail: "Space-space links use bounded candidate updates.",
        source: "fidelity_summary.fidelity_warnings"
      },
      {
        kind: "kpi",
        label: "KPI可信度",
        detail: "完整流级代理 / KPI 6/6 有运行值；来源字段 18/18 可观测",
        source: "network_kpi_credibility_v1"
      },
      {
        kind: "kpi",
        label: "KPI边界 1",
        detail: "No packet-level simulation.",
        source: "network_kpi_credibility_v1.caveats"
      },
      {
        kind: "kpi",
        label: "KPI边界 2",
        detail: "Loss is pressure proxy.",
        source: "network_kpi_credibility_v1.caveats"
      }
    ]);
  });

  it("does not render a model panel before backend assumptions or boundaries exist", () => {
    expect(
      buildDataPanelModelAssumptionsDisplay(null, null, null, null)
    ).toBeNull();
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

describe("buildDataPanelNetworkComponentTail", () => {
  it("formats backend KPI time-series component tail fields", () => {
    expect(
      buildDataPanelNetworkComponentTail({
        version: "v1",
        samples: [
          {
            sim_time: 12,
            network_effective_throughput_mbps: 88,
            network_requested_route_demand_mbps: 90,
            network_offered_route_capacity_mbps: 100,
            network_demand_pressure_proxy: 0.9,
            network_effective_latency_s: 0.12,
            network_effective_loss_proxy_rate: 0.08,
            network_route_loss_proxy_rate: 0.03,
            network_pressure_loss_proxy_rate: 0.08,
            network_effective_delay_variation_s: 0.014,
            network_route_delay_variation_s: 0.01,
            network_pressure_delay_variation_s: 0.004,
            compute_resource_used_gflops_fp32: 12
          }
        ]
      })
    ).toEqual([
      { label: "样本路由容量", value: "100 Mbps" },
      { label: "样本请求需求", value: "90 Mbps" },
      { label: "样本需求压力", value: "90%" },
      { label: "样本路由损耗", value: "3%" },
      { label: "样本压力损耗", value: "8%" },
      { label: "样本路由抖动", value: "10 ms" },
      { label: "样本压力抖动", value: "4 ms" }
    ]);
  });

  it("hides component tail fields until backend time-series samples exist", () => {
    expect(buildDataPanelNetworkComponentTail(undefined)).toEqual([]);
  });

  it("shows backend time-pressure components when runtime samples provide them", () => {
    expect(
      buildDataPanelNetworkComponentTail({
        version: "v1",
        samples: [
          {
            sim_time: 60,
            network_effective_throughput_mbps: 170,
            network_effective_latency_s: 0.12,
            network_effective_loss_proxy_rate: 0.07,
            network_effective_delay_variation_s: 0.014,
            network_time_pressure_factor: 0.9,
            network_time_pressure_loss_proxy_rate: 0.07,
            network_time_pressure_delay_variation_s: 0.004,
            compute_resource_used_gflops_fp32: 12
          }
        ]
      })
    ).toEqual([
      { label: "样本时间压力", value: "90%" },
      { label: "样本时间损耗", value: "7%" },
      { label: "样本时间抖动", value: "4 ms" }
    ]);
  });
});

describe("buildDataPanelServiceLatencyDisplay", () => {
  it("formats backend communication-compute service latency components", () => {
    const display = buildDataPanelServiceLatencyDisplay({
      service_latency_model: "COMMUNICATION_COMPUTE_COMPONENT_PROXY",
      service_latency_task_count: 2,
      service_latency_complete_count: 1,
      service_latency_input_network_avg_s: 4,
      service_latency_compute_queue_avg_s: 0,
      service_latency_compute_execution_avg_s: 2,
      service_latency_output_network_avg_s: 1.4,
      service_latency_total_avg_s: 7.4
    });

    expect(display).toMatchObject({
      sourceLabel: "通信-计算服务延迟",
      modelLabel: "后端服务组件代理",
      taskCountLabel: "2 个服务",
      completeCountLabel: "1 个完整闭环",
      totalLatencyLabel: "7,400 ms"
    });
    expect(display.items.map((item) => item.value)).toEqual([
      "4,000 ms",
      "0 ms",
      "2,000 ms",
      "1,400 ms"
    ]);
  });

  it("hides service latency items until backend samples exist", () => {
    expect(buildDataPanelServiceLatencyDisplay(null).items).toEqual([]);
    expect(
      buildDataPanelServiceLatencyDisplay({
        service_latency_task_count: 0,
        service_latency_input_network_avg_s: 4
      }).items
    ).toEqual([]);
  });
});

describe("buildDataPanelServiceLatencyRows", () => {
  it("formats bounded per-service latency trace rows", () => {
    const rows = buildDataPanelServiceLatencyRows(
      {
        version: "v1",
        mode: "RECENT_SERVICE_LIMITED",
        service_count: 2,
        service_limit: 32,
        item_count: 2,
        items: [
          {
            task_id: "svc-00-compute_service-00000-task",
            input_flow_id: "svc-00-compute_service-00000-input",
            output_flow_id: "svc-00-compute_service-00000-output",
            input_route_id: "route:svc-00-compute_service-00000-input",
            output_route_id: "route:svc-00-compute_service-00000-output",
            compute_node_id: "sat-00001",
            service_placement_status: "PLACED",
            service_placement_policy: "MIN_ESTIMATED_FINISH_TIME",
            service_placement_bottleneck_resource: "cpu_gflops_fp32",
            service_placement_candidate_count: 4,
            service_placement_capable_candidate_count: 2,
            service_placement_candidate_queue_label:
              "sat-00001:PLACED/available=0s/q=0/finish=8s",
            first_sample_sim_time: 6,
            last_sample_sim_time: 8,
            component_timeline: [
              {
                component: "input_network",
                sample_sim_time: 6,
                duration_s: 4
              },
              {
                component: "compute_queue",
                sample_sim_time: 6,
                duration_s: 0
              },
              {
                component: "compute_execution",
                sample_sim_time: 7,
                duration_s: 2
              },
              {
                component: "output_network",
                sample_sim_time: 8,
                duration_s: 1.4
              },
              {
                component: "total",
                sample_sim_time: 8,
                duration_s: 7.4
              }
            ],
            complete: true,
            input_network_latency_s: 4,
            compute_queue_delay_s: 0,
            compute_execution_delay_s: 2,
            output_network_latency_s: 1.4,
            total_latency_s: 7.4
          },
          {
            task_id: "svc-short",
            complete: false,
            input_network_latency_s: 1,
            compute_queue_delay_s: 0,
            compute_execution_delay_s: 1,
            output_network_latency_s: 0,
            total_latency_s: 0
          }
        ]
      },
      1
    );

    expect(rows).toEqual([
      {
        taskId: "svc-00-compute_service-00000-task",
        taskLabel: "...vice-00000-task",
        traceTitle:
          "task=svc-00-compute_service-00000-task / input=svc-00-compute_service-00000-input / output=svc-00-compute_service-00000-output / input_route=route:svc-00-compute_service-00000-input / output_route=route:svc-00-compute_service-00000-output / placement_node=sat-00001 / placement_status=PLACED / placement_policy=MIN_ESTIMATED_FINISH_TIME / placement_bottleneck=cpu_gflops_fp32 / placement_candidates=2/4 / placement_queue=sat-00001:PLACED/available=0s/q=0/finish=8s / first=6s / last=8s / timeline=input_network@6s=4,000 ms, compute_queue@6s=0 ms, compute_execution@7s=2,000 ms, output_network@8s=1,400 ms, total@8s=7,400 ms",
        statusLabel: "完整闭环",
        placementLabel:
          "节点 sat-00001 / 已放置 / 瓶颈 cpu_gflops_fp32 / 候选 2/4 / 队列 sat-00001:PLACED/available=0s/q=0/finish=8s",
        totalLatencyLabel: "7,400 ms",
        timeline: [
          {
            component: "input_network",
            label: "输入网络",
            timeLabel: "6s",
            durationLabel: "4,000 ms",
            traceTitle: "component=input_network / time=6s / duration=4,000 ms"
          },
          {
            component: "compute_queue",
            label: "计算排队",
            timeLabel: "6s",
            durationLabel: "0 ms",
            traceTitle: "component=compute_queue / time=6s / duration=0 ms"
          },
          {
            component: "compute_execution",
            label: "计算执行",
            timeLabel: "7s",
            durationLabel: "2,000 ms",
            traceTitle: "component=compute_execution / time=7s / duration=2,000 ms"
          },
          {
            component: "output_network",
            label: "输出网络",
            timeLabel: "8s",
            durationLabel: "1,400 ms",
            traceTitle: "component=output_network / time=8s / duration=1,400 ms"
          },
          {
            component: "total",
            label: "总延迟",
            timeLabel: "8s",
            durationLabel: "7,400 ms",
            traceTitle: "component=total / time=8s / duration=7,400 ms"
          }
        ]
      }
    ]);
  });

  it("keeps legacy service rows when component timeline is absent", () => {
    const rows = buildDataPanelServiceLatencyRows({
      version: "v1",
      mode: "RECENT_SERVICE_LIMITED",
      items: [
        {
          task_id: "svc-legacy",
          complete: true,
          input_network_latency_s: 1,
          compute_queue_delay_s: 0,
          compute_execution_delay_s: 1,
          output_network_latency_s: 0,
          total_latency_s: 2
        }
      ]
    });

    expect(rows[0]).toMatchObject({
      taskId: "svc-legacy",
      totalLatencyLabel: "2,000 ms",
      placementLabel: "无计算放置",
      timeline: []
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

describe("COMPUTE_SERIES_OPTIONS", () => {
  it("keeps selectable compute chart series ordered by resource type", () => {
    expect(
      COMPUTE_SERIES_OPTIONS.map((option) => [
        option.key,
        option.shortLabel,
        option.unit
      ])
    ).toEqual([
      ["computeUsedTflops", "FP32", "TFLOPS"],
      ["computeCpuFp64Gflops", "FP64", "GFLOPS"],
      ["computeGpuFp32Tflops", "GPU32", "TFLOPS"],
      ["computeGpuFp16Tflops", "GPU16", "TFLOPS"],
      ["computeNpuInt8Tops", "INT8", "TOPS"],
      ["computeMemoryGb", "\u5185\u5b58", "GB"],
      ["computeStorageGb", "\u5b58\u50a8", "GB"]
    ]);
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

  it("uses recent flow-window KPI fields for time-varying network charts", () => {
    const telemetry = buildDataPanelTelemetry(
      makeSnapshot(),
      20,
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
            network_recent_flow_count: 3,
            network_recent_delivered_throughput_mbps: 65,
            network_recent_latency_s: 0.18,
            network_recent_loss_proxy_rate: 0.25,
            network_recent_delay_variation_s: 0.012,
            compute_resource_used_gflops_fp32: 2500
          }
        ]
      }
    );

    expect(telemetry).toHaveLength(1);
    expect(telemetry[0]).toMatchObject({
      throughputMbps: 65,
      latencyMs: 180,
      lossPercent: 25,
      jitterMs: 12
    });
  });

  it("falls back to effective KPI fields when the recent flow window is empty", () => {
    const telemetry = buildDataPanelTelemetry(
      makeSnapshot(),
      20,
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
            network_recent_flow_count: 0,
            network_recent_delivered_throughput_mbps: 0,
            network_recent_latency_s: 0,
            network_recent_loss_proxy_rate: 0,
            network_recent_delay_variation_s: 0,
            compute_resource_used_gflops_fp32: 2500
          }
        ]
      }
    );

    expect(telemetry).toHaveLength(1);
    expect(telemetry[0]).toMatchObject({
      throughputMbps: 150,
      latencyMs: 110,
      lossPercent: 4,
      jitterMs: 6
    });
  });

  it("extends backend runtime KPI telemetry to the displayed simulation time", () => {
    const telemetry = buildDataPanelTelemetry(
      makeSnapshot(),
      25,
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

    expect(telemetry).toHaveLength(2);
    expect(telemetry[1]).toMatchObject({
      simTime: 25,
      throughputMbps: 150,
      latencyMs: 110,
      lossPercent: 4,
      jitterMs: 6,
      computeUsedTflops: 2.5
    });
  });

  it("builds a bounded runtime KPI sample tail at the displayed simulation time", () => {
    const samples = buildRuntimeKpiTelemetrySamples(
      {
        version: "v1",
        samples: Array.from({ length: 25 }, (_, index) => ({
          sim_time: index,
          network_effective_throughput_mbps: 100 + index,
          network_effective_latency_s: 0.1,
          network_effective_loss_proxy_rate: 0.01,
          network_effective_delay_variation_s: 0.002,
          compute_resource_used_gflops_fp32: 1000 + index
        }))
      },
      30
    );

    expect(samples).toHaveLength(24);
    expect(samples[0].sim_time).toBe(2);
    expect(samples[samples.length - 1]).toMatchObject({
      sim_time: 30,
      network_effective_throughput_mbps: 124,
      compute_resource_used_gflops_fp32: 1024
    });
  });

  it("maps backend compute vector KPI fields into telemetry points", () => {
    const telemetry = buildDataPanelTelemetry(
      makeSnapshot(),
      20,
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
            compute_resource_used_gflops_fp32: 2500,
            compute_resource_used_gflops_fp64: 12,
            compute_resource_used_gpu_tflops_fp32: 2.5,
            compute_resource_used_gpu_tflops_fp16: 5,
            compute_resource_used_npu_tops_int8: 8,
            compute_resource_used_memory_gb: 16,
            compute_resource_used_storage_gb: 32
          }
        ]
      }
    );

    expect(telemetry).toHaveLength(1);
    expect(telemetry[0]).toMatchObject({
      computeUsedTflops: 2.5,
      computeCpuFp64Gflops: 12,
      computeGpuFp32Tflops: 2.5,
      computeGpuFp16Tflops: 5,
      computeNpuInt8Tops: 8,
      computeMemoryGb: 16,
      computeStorageGb: 32
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

describe("buildDataPanelComputeVectorTail", () => {
  it("formats compute resource vector usage from the latest backend KPI sample", () => {
    expect(
      buildDataPanelComputeVectorTail({
        version: "v1",
        sample_count: 1,
        tail_sample_source: "CURRENT_METRICS_SUMMARY",
        samples: [
          {
            sim_time: 12,
            network_effective_throughput_mbps: 80,
            network_effective_latency_s: 0.08,
            network_effective_loss_proxy_rate: 0.01,
            network_effective_delay_variation_s: 0.002,
            compute_resource_used_gflops_fp32: 1500,
            compute_resource_used_gflops_fp64: 12,
            compute_resource_used_gpu_tflops_fp32: 2.5,
            compute_resource_used_gpu_tflops_fp16: 5,
            compute_resource_used_npu_tops_int8: 8,
            compute_resource_used_memory_gb: 16,
            compute_resource_used_storage_gb: 32
          }
        ]
      })
    ).toEqual([
      { label: "CPU FP64", value: "12 GFLOPS" },
      { label: "GPU FP32", value: "2.5 TFLOPS" },
      { label: "GPU FP16", value: "5 TFLOPS" },
      { label: "NPU INT8", value: "8 TOPS" },
      { label: "内存", value: "16 GB" },
      { label: "存储", value: "32 GB" }
    ]);
  });

  it("keeps old FP32-only backend KPI samples compatible", () => {
    expect(
      buildDataPanelComputeVectorTail({
        version: "v1",
        samples: [
          {
            sim_time: 12,
            network_effective_throughput_mbps: 80,
            network_effective_latency_s: 0.08,
            network_effective_loss_proxy_rate: 0.01,
            network_effective_delay_variation_s: 0.002,
            compute_resource_used_gflops_fp32: 1500
          }
        ]
      })
    ).toEqual([]);
  });
});

describe("buildDataPanelComputeBottleneckDisplay", () => {
  it("formats backend-owned compute resource bottleneck summary", () => {
    expect(
      buildDataPanelComputeBottleneckDisplay({
        compute_resource_bottleneck_resource: "gpu_tflops_fp32",
        compute_resource_bottleneck_label: "GPU FP32 TFLOPS",
        compute_resource_bottleneck_utilization: 0.875,
        compute_resource_bottleneck_used: 3.5,
        compute_resource_bottleneck_total: 4,
        compute_resource_bottleneck_available: 0.5,
        compute_resource_bottleneck_status: "PRESSURED"
      })
    ).toEqual({
      label: "GPU FP32 TFLOPS",
      utilizationLabel: "87.5%",
      statusLabel: "受压",
      detailLabel: "已用 3.5 / 总量 4，可用 0.5"
    });
  });

  it("stays hidden when backend has no bottleneck summary", () => {
    expect(buildDataPanelComputeBottleneckDisplay({})).toBeNull();
    expect(
      buildDataPanelComputeBottleneckDisplay({
        compute_resource_bottleneck_resource: "none",
        compute_resource_bottleneck_label: "No compute resource capacity"
      })
    ).toBeNull();
  });
});

describe("buildDataPanelComputeTaskTimelineDisplay", () => {
  it("formats backend-owned compute task timeline summary", () => {
    expect(
      buildDataPanelComputeTaskTimelineDisplay({
        version: "v1",
        source: "SERVICE_LATENCY_HISTORY",
        summary_scope: "RECENT_COMPUTE_TASK_QUEUE_EXECUTION",
        task_count: 2,
        item_count: 2,
        complete_task_count: 1,
        queued_task_count: 1,
        total_compute_queue_delay_s: 3,
        total_compute_execution_delay_s: 6,
        avg_compute_queue_delay_s: 1.5,
        avg_compute_execution_delay_s: 3,
        items: [
          {
            task_id: "svc-00-compute_service-00000-task",
            compute_node_id: "sat-00001",
            placement_status: "QUEUED",
            placement_bottleneck_resource: "gpu_tflops_fp32",
            queue_delay_s: 3,
            execution_delay_s: 4,
            total_latency_s: 0,
            complete: false,
            queue_state: "QUEUED",
            queue_state_label: "Compute queue waiting",
            first_sample_sim_time: 2,
            last_sample_sim_time: 12,
            stage_count: 2,
            stages: [
              {
                component: "compute_queue",
                label: "Compute queue",
                sample_sim_time: 6,
                duration_s: 3
              },
              {
                component: "compute_execution",
                label: "Compute execution",
                sample_sim_time: 10,
                duration_s: 4
              }
            ]
          }
        ]
      })
    ).toEqual({
      sourceLabel: "后端计算任务时间线",
      summaryLabel: "2 shown / 2 total / 1 complete",
      queuedTaskLabel: "1",
      totalQueueDelayLabel: "3,000 ms",
      totalExecutionDelayLabel: "6,000 ms",
      items: [
        {
          taskId: "svc-00-compute_service-00000-task",
          taskLabel: "...vice-00000-task",
          nodeLabel: "节点 sat-00001",
          queueExecutionLabel: "3,000 ms / 4,000 ms",
          traceTitle:
            "task=svc-00-compute_service-00000-task / node=sat-00001 / placement=QUEUED / bottleneck=gpu_tflops_fp32 / queue=3,000 ms / execution=4,000 ms / state=QUEUED / stages=compute_queue@6s=3,000 ms, compute_execution@10s=4,000 ms"
        }
      ]
    });
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
    expect(buildComputeResourcePoolModeNote(pool)).toBe(
      "兼容模式：FP32 主容量来自旧标量；其他资源向量来自节点快照或默认值。"
    );
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
    expect(buildComputeResourcePoolModeNote(pool)).toBe(
      "后端资源向量：CPU FP32/FP64、GPU FP32/FP16、NPU INT8、内存、存储。"
    );
  });
  it("uses the latest backend KPI sample for live resource-pool consumption", () => {
    const pool = buildComputeResourcePoolFromRuntime(
      makeSnapshot(),
      {
        compute_resource_total_gflops_fp32: 80,
        compute_resource_available_gflops_fp32: 70,
        compute_resource_used_gflops_fp32: 10,
        compute_resource_total_gpu_tflops_fp32: 6,
        compute_resource_available_gpu_tflops_fp32: 5,
        compute_resource_used_gpu_tflops_fp32: 1,
        compute_resource_total_memory_gb: 96,
        compute_resource_available_memory_gb: 90,
        compute_resource_used_memory_gb: 6,
        compute_resource_vector_utilization_mode: "RESOURCE_VECTOR_ESTIMATED"
      },
      {
        version: "v1",
        samples: [
          {
            sim_time: 12,
            network_effective_throughput_mbps: 80,
            network_effective_latency_s: 0.08,
            network_effective_loss_proxy_rate: 0.01,
            network_effective_delay_variation_s: 0.002,
            compute_resource_used_gflops_fp32: 30,
            compute_resource_used_gpu_tflops_fp32: 2,
            compute_resource_used_memory_gb: 24
          }
        ]
      }
    );

    expect(pool).toMatchObject({
      totalTflops: 80,
      usedTflops: 30,
      availableTflops: 50,
      usedPercent: 37.5
    });
    expect(pool.vectorSummary).toMatchObject({
      usedGpuFp32Tflops: 2,
      availableGpuFp32Tflops: 4,
      usedMemoryGb: 24,
      availableMemoryGb: 72
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

describe("buildUserBusinessRequestRows", () => {
  it("prefers backend user request summaries when available", () => {
    const rows = buildUserBusinessRequestRows(
      makeSnapshot({
        ground_users: [{ user_id: "user-0", status: "ACTIVE" }]
      }),
      undefined,
      {
        version: "v1",
        source: "BACKEND_RUNTIME_SNAPSHOT",
        user_count: 1,
        item_count: 1,
        active_user_count: 1,
        compute_service_user_count: 1,
        waiting_user_count: 0,
        window_user_count: 1,
        window_active_user_count: 1,
        window_compute_service_user_count: 1,
        window_waiting_user_count: 0,
        hidden_user_count: 0,
        items: [
          {
            user_id: "user-0",
            platform_type: "GROUND_USER_TERMINAL",
            platform_type_label: "地面用户终端",
            cell_id: "cell-a",
            communication_route_count: 2,
            available_route_count: 1,
            compute_service_count: 1,
            network_queue_count: 0,
            network_queue_reason: "NO_QUEUE",
            network_queue_reason_label: "无网络排队",
            selected_satellite_id: "sat-0",
            destination_id: "compute-0",
            status: "ACTIVE/AVAILABLE",
            primary_route_id: "route-a",
            primary_flow_id: "flow-a",
            primary_next_hop_id: "sat-0",
            route_hop_count: 2,
            route_path_label: "route-a: user-0 -> sat-0 -> compute-0",
            latency_s: 0.12,
            capacity_mbps: 80,
            loss_proxy_rate: 0.02,
            service_state: "task-0/330ms/RUNNING",
            service_task_id: "task-0",
            service_complete: false,
            service_total_latency_s: 0.33,
            input_network_latency_s: 0.12,
            compute_queue_delay_s: 0.01,
            compute_execution_delay_s: 0.2,
            output_network_latency_s: 0,
            input_route_id: "route-a",
            output_route_id: "route-out",
            compute_node_id: "sat-0",
            service_placement_status: "QUEUED",
            service_placement_policy: "MIN_ESTIMATED_FINISH_TIME",
            service_placement_bottleneck_resource: "gpu_tflops_fp32",
            service_placement_candidate_count: 3,
            service_placement_capable_candidate_count: 2,
            service_placement_candidate_queue_label:
              "sat-0:QUEUED/available=4s/q=1/finish=6s",
            active_business_type: "COMPUTE_SERVICE",
            active_business_label: "通信-计算服务",
            request_state: "COMPUTE_SERVICE_ACTIVE",
            request_state_label: "计算服务进行中",
            path: ["user-0", "sat-0", "compute-0"]
          }
        ]
      }
    );

    expect(rows.sourceLabel).toBe("backend user_request_summary_v1");
    expect(rows.summaryLabel).toContain("1 shown / 1 total");
    expect(rows.summaryLabel).toContain("active 1 total");
    expect(rows.summaryLabel).toContain("window active 1");
    expect(rows.items[0]).toMatchObject({
      userId: "user-0",
      platformTypeLabel: "地面用户终端 / cell-a",
      communicationLabel: "1 / 2 routes / next sat-0",
      computeLabel: "1 compute",
      networkQueueLabel: "无网络排队",
      selectedSatelliteId: "sat-0",
      destinationId: "compute-0",
      placementLabel:
        "节点 sat-0 / 排队 / 瓶颈 gpu_tflops_fp32 / 候选 2/3 / 队列 sat-0:QUEUED/available=4s/q=1/finish=6s",
      statusLabel: "ACTIVE/AVAILABLE",
      latencyCapacityLabel: "0.12 s / 80 Mbps",
      serviceLabel:
        "通信-计算服务 / 计算服务进行中 / task-0 active / total 330 ms / in 120 ms + queue 10 ms + exec 200 ms / input route-a / output route-out"
    });
  });

  it("fills backend-hidden users from snapshot fallback rows", () => {
    const rows = buildUserBusinessRequestRows(
      makeSnapshot({
        ground_users: [
          { user_id: "user-0", status: "ACTIVE" },
          { user_id: "user-1", status: "ACTIVE" }
        ],
        routes: [
          {
            route_id: "route-user-1",
            flow_id: "flow-user-1",
            path: ["user-1", "sat-1", "compute-1"],
            latency: 0.2,
            capacity: 40,
            available: true
          }
        ]
      }),
      undefined,
      {
        version: "v1",
        source: "BACKEND_RUNTIME_SNAPSHOT",
        user_count: 2,
        item_count: 1,
        active_user_count: 2,
        compute_service_user_count: 0,
        waiting_user_count: 0,
        window_user_count: 1,
        window_active_user_count: 1,
        window_compute_service_user_count: 0,
        window_waiting_user_count: 0,
        hidden_user_count: 1,
        items: [
          {
            user_id: "user-0",
            platform_type: "GROUND_USER_TERMINAL",
            communication_route_count: 1,
            available_route_count: 1,
            compute_service_count: 0,
            network_queue_count: 0,
            selected_satellite_id: "sat-0",
            destination_id: "service-0",
            status: "ACTIVE/AVAILABLE",
            primary_route_id: "route-backend",
            primary_flow_id: "flow-backend",
            path: ["user-0", "sat-0", "service-0"]
          }
        ]
      }
    );

    expect(rows.sourceLabel).toContain("快照补齐");
    expect(rows.summaryLabel).toContain("补齐 1");
    expect(rows.items.map((row) => row.userId)).toEqual(["user-0", "user-1"]);
    expect(rows.items[0].pathLabel).toContain("route-backend");
    expect(rows.items[1]).toMatchObject({
      userId: "user-1",
      selectedSatelliteId: "sat-1",
      destinationId: "compute-1"
    });
  });

  it("shows per-user node status and service latency linkage", () => {
    const rows = buildUserBusinessRequestRows(
      makeSnapshot({
        ground_users: [{ user_id: "user-0", cell_id: "cell-a", status: "ACTIVE" }],
        routes: [
          {
            route_id: "route-1",
            flow_id: "flow-input",
            path: ["user-0", "sat-0", "compute-0"],
            latency: 0.12,
            capacity: 80,
            demand_capacity: 60,
            loss_rate: 0.02,
            available: true
          }
        ]
      }),
      {
        version: "v1",
        mode: "RECENT_LIMITED",
        items: [
          {
            task_id: "task-service-0",
            input_flow_id: "flow-input",
            compute_node_id: "sat-0",
            service_placement_status: "PLACED",
            service_placement_bottleneck_resource: "cpu_gflops_fp32",
            service_placement_candidate_count: 1,
            service_placement_capable_candidate_count: 1,
            complete: false,
            input_network_latency_s: 0.12,
            compute_queue_delay_s: 0.01,
            compute_execution_delay_s: 0.2,
            output_network_latency_s: 0,
            total_latency_s: 0.33
          }
        ]
      }
    );

    expect(rows.sourceLabel).toBe("快照用户/路由 + 后端服务延迟历史");
    expect(rows.items[0]).toMatchObject({
      userId: "user-0",
      platformTypeLabel: "地面用户终端 / cell-a",
      communicationLabel: "1 / 1 条",
      computeLabel: "1 条计算业务",
      networkQueueLabel: "队列空",
      selectedSatelliteId: "sat-0",
      destinationId: "compute-0",
      placementLabel: "节点 sat-0 / 已放置 / 瓶颈 cpu_gflops_fp32 / 候选 1/1",
      statusLabel: "ACTIVE / 业务可达",
      latencyCapacityLabel: "0.12 s / 80 Mbps",
      serviceLabel: "task-service-0 / 330 ms / 进行中"
    });
  });

  it("keeps idle users visible even when they have no current route", () => {
    const rows = buildUserBusinessRequestRows(
      makeSnapshot({
        ground_users: [
          { user_id: "user-0", status: "ACTIVE" },
          { user_id: "user-1", status: "IDLE" }
        ],
        routes: [
          {
            route_id: "route-1",
            flow_id: "flow-1",
            path: ["user-0", "sat-0", "service-0"],
            latency: 0.2,
            capacity: 40,
            available: true
          }
        ]
      })
    );

    expect(rows.items.map((row) => row.userId)).toEqual(["user-0", "user-1"]);
    expect(rows.items[1]).toMatchObject({
      userId: "user-1",
      communicationLabel: "无通信业务",
      computeLabel: "无计算业务",
      networkQueueLabel: "队列空",
      selectedSatelliteId: "未选择",
      statusLabel: "IDLE"
    });
  });
});

describe("detail inspectors", () => {
  const userRow = {
    userId: "user-0",
    platformTypeLabel: "地面用户终端 / cell-a",
    communicationLabel: "1 / 2 routes / next sat-0",
    computeLabel: "1 compute",
    networkQueueLabel: "empty",
    selectedSatelliteId: "sat-0",
    destinationId: "compute-0",
    placementLabel: "节点 sat-0 / 排队 / 瓶颈 gpu_tflops_fp32 / 候选 2/3",
    statusLabel: "ACTIVE/AVAILABLE",
    latencyCapacityLabel: "0.12 s / 80 Mbps",
    serviceLabel: "task-0 active / total 330 ms",
    pathLabel: "route-a: user-0 -> sat-0 -> compute-0"
  };
  const satelliteRow = {
    satelliteId: "sat-0",
    statusLabel: "BUSY / Satellite compute node",
    loadPercent: 75,
    loadLabel: "75%",
    serviceObjectLabel: "user-0, user-1",
    nextHopLabel: "compute-0",
    cpuFp32Label: "75 / 100 GFLOPS",
    cpuFp64Label: "2 / 8 GFLOPS",
    gpuLabel: "GPU32 1 / 2 TFLOPS · GPU16 2 / 4 TFLOPS",
    npuLabel: "6 / 12 TOPS",
    memoryStorageLabel: "10 / 32 GB · 64 / 512 GB",
    taskLabel: "运行 2 / 完成 7",
    networkLabel: "route 2 / available 1"
  };

  it("selects requested rows or falls back to the current window head", () => {
    expect(selectUserBusinessRequestRow([userRow], "missing")).toBe(userRow);
    expect(selectUserBusinessRequestRow([], "user-0")).toBeNull();
    expect(selectSatelliteResourceRow([satelliteRow], "sat-0")).toBe(satelliteRow);
    expect(selectSatelliteResourceRow([], null)).toBeNull();
  });

  it("prefers backend-owned node detail cards when available", () => {
    const backendDetailSummary = {
      version: "v1",
      source: "BACKEND_RUNTIME_STATUS",
      user_detail_count: 1,
      satellite_detail_count: 1,
      users: [
        {
          entity_type: "USER",
          entity_id: "user-0",
          title: "后端用户 user-0",
          subtitle: "COMPUTE_SERVICE_ACTIVE",
          sections: [
            {
              section_id: "compute_placement",
              title: "计算与队列",
              fields: [
                { label: "服务放置", value: "后端节点 sat-0", tone: "resource" }
              ]
            }
          ],
          fields: [
            { label: "服务放置", value: "后端节点 sat-0", tone: "resource" },
            { label: "路径", value: "backend route path" }
          ]
        }
      ],
      satellites: [
        {
          entity_type: "SATELLITE",
          entity_id: "sat-0",
          title: "后端卫星 sat-0",
          subtitle: "COMPUTE_NODE",
          sections: [
            {
              section_id: "compute_resources",
              title: "算力资源",
              fields: [
                { label: "CPU FP32", value: "80 / 100 GFLOPS", tone: "resource" }
              ]
            }
          ],
          fields: [
            { label: "CPU FP32", value: "80 / 100 GFLOPS", tone: "resource" },
            { label: "网络", value: "链路 4 / 路由 2", tone: "normal" }
          ]
        }
      ]
    } as const;

    expect(selectRuntimeUserDetailCard(backendDetailSummary, "user-0")?.title).toBe(
      "后端用户 user-0"
    );
    expect(selectRuntimeUserDetailCard(backendDetailSummary, "missing")).toBeNull();
    expect(
      selectRuntimeSatelliteDetailCard(backendDetailSummary, "sat-0")?.title
    ).toBe("后端卫星 sat-0");
    expect(selectRuntimeSatelliteDetailCard(backendDetailSummary, null)).toBeNull();
    expect(buildUserBusinessRequestInspector(userRow, backendDetailSummary)).toMatchObject({
      title: "后端用户 user-0",
      subtitle: "COMPUTE_SERVICE_ACTIVE",
      sections: [
        {
          sectionId: "compute_placement",
          title: "计算与队列",
          fields: [{ label: "服务放置", value: "后端节点 sat-0", tone: "resource" }]
        }
      ],
      fields: expect.arrayContaining([
        { label: "服务放置", value: "后端节点 sat-0", tone: "resource" },
        { label: "路径", value: "backend route path", tone: "normal" }
      ])
    });
    expect(buildSatelliteResourceInspector(satelliteRow, backendDetailSummary)).toMatchObject({
      title: "后端卫星 sat-0",
      subtitle: "COMPUTE_NODE",
      sections: [
        {
          sectionId: "compute_resources",
          title: "算力资源",
          fields: [{ label: "CPU FP32", value: "80 / 100 GFLOPS", tone: "resource" }]
        }
      ],
      fields: expect.arrayContaining([
        { label: "CPU FP32", value: "80 / 100 GFLOPS", tone: "resource" },
        { label: "网络", value: "链路 4 / 路由 2", tone: "normal" }
      ])
    });
  });

  it("builds user and satellite detail inspector fields", () => {
    expect(buildUserBusinessRequestInspector(userRow)).toMatchObject({
      title: "用户 user-0",
      subtitle: "ACTIVE/AVAILABLE",
      sections: [
        {
          sectionId: "business_request",
          title: "业务请求",
          fields: expect.arrayContaining([
            { label: "活跃业务", value: userRow.serviceLabel },
            { label: "目标卫星", value: userRow.selectedSatelliteId }
          ])
        },
        {
          sectionId: "network_path_queue",
          title: "网络与队列",
          fields: expect.arrayContaining([
            { label: "网络队列", value: userRow.networkQueueLabel, tone: "normal" },
            { label: "路径", value: userRow.pathLabel }
          ])
        },
        {
          sectionId: "compute_service",
          title: "计算服务",
          fields: expect.arrayContaining([
            { label: "服务放置", value: userRow.placementLabel, tone: "resource" }
          ])
        }
      ],
      fields: expect.arrayContaining([
        { label: "服务放置", value: userRow.placementLabel, tone: "resource" },
        { label: "路径", value: userRow.pathLabel }
      ])
    });
    expect(buildSatelliteResourceInspector(satelliteRow)).toMatchObject({
      title: "卫星 sat-0",
      subtitle: "BUSY / Satellite compute node",
      sections: [
        {
          sectionId: "service_routing",
          title: "服务与路由",
          fields: expect.arrayContaining([
            { label: "服务对象", value: satelliteRow.serviceObjectLabel },
            { label: "下一跳节点", value: satelliteRow.nextHopLabel }
          ])
        },
        {
          sectionId: "compute_resource_pool",
          title: "算力资源池",
          fields: expect.arrayContaining([
            { label: "CPU FP32", value: satelliteRow.cpuFp32Label, tone: "resource" },
            { label: "GPU", value: satelliteRow.gpuLabel, tone: "resource" }
          ])
        },
        {
          sectionId: "network_task_context",
          title: "网络与任务",
          fields: expect.arrayContaining([
            { label: "任务队列", value: satelliteRow.taskLabel },
            { label: "网络KPI", value: satelliteRow.networkLabel, tone: "normal" }
          ])
        }
      ],
      fields: expect.arrayContaining([
        { label: "GPU", value: satelliteRow.gpuLabel, tone: "resource" },
        { label: "网络", value: satelliteRow.networkLabel }
      ])
    });
  });

  it("builds user detail drawer v1 sections from runtime request rows", () => {
    expect(buildUserDetailDrawerSectionsV1(userRow)).toEqual([
      {
        sectionId: "business_request",
        title: "业务请求",
        fields: [
          { label: "用户节点", value: "user-0" },
          { label: "平台类型", value: "地面用户终端 / cell-a" },
          { label: "活跃业务", value: "task-0 active / total 330 ms" },
          { label: "请求状态", value: "ACTIVE/AVAILABLE" },
          { label: "目标卫星", value: "sat-0" },
          { label: "目标节点", value: "compute-0" }
        ]
      },
      {
        sectionId: "network_path_queue",
        title: "网络与队列",
        fields: [
          { label: "通信路由", value: "1 / 2 routes / next sat-0" },
          { label: "网络队列", value: "empty", tone: "normal" },
          { label: "路径", value: "route-a: user-0 -> sat-0 -> compute-0" },
          { label: "时延/容量", value: "0.12 s / 80 Mbps" }
        ]
      },
      {
        sectionId: "compute_service",
        title: "计算服务",
        fields: [
          { label: "计算业务", value: "1 compute", tone: "resource" },
          {
            label: "服务放置",
            value: "节点 sat-0 / 排队 / 瓶颈 gpu_tflops_fp32 / 候选 2/3",
            tone: "resource"
          }
        ]
      }
    ]);
  });

  it("builds satellite detail drawer v1 sections from runtime resource rows", () => {
    expect(buildSatelliteDetailDrawerSectionsV1(satelliteRow)).toEqual([
      {
        sectionId: "service_routing",
        title: "服务与路由",
        fields: [
          { label: "卫星节点", value: "sat-0" },
          { label: "运行状态", value: "BUSY / Satellite compute node" },
          { label: "服务对象", value: "user-0, user-1" },
          { label: "下一跳节点", value: "compute-0" }
        ]
      },
      {
        sectionId: "compute_resource_pool",
        title: "算力资源池",
        fields: [
          { label: "负载", value: "75%", tone: "resource" },
          { label: "CPU FP32", value: "75 / 100 GFLOPS", tone: "resource" },
          { label: "CPU FP64", value: "2 / 8 GFLOPS", tone: "resource" },
          {
            label: "GPU",
            value: "GPU32 1 / 2 TFLOPS · GPU16 2 / 4 TFLOPS",
            tone: "resource"
          },
          { label: "NPU", value: "6 / 12 TOPS", tone: "resource" },
          { label: "内存/存储", value: "10 / 32 GB · 64 / 512 GB", tone: "resource" }
        ]
      },
      {
        sectionId: "network_task_context",
        title: "网络与任务",
        fields: [
          { label: "任务队列", value: "运行 2 / 完成 7" },
          { label: "网络KPI", value: "route 2 / available 1", tone: "normal" }
        ]
      }
    ]);

    expect(
      buildSatelliteDetailDrawerSectionsV1({
        ...satelliteRow,
        networkLabel: "links 3 / queued 1 / loss 2%"
      })[2].fields[1]
    ).toEqual({
      label: "网络KPI",
      value: "links 3 / queued 1 / loss 2%",
      tone: "warning"
    });
  });

  it("builds full drawer items without truncating detail field values", () => {
    const userInspector = buildUserBusinessRequestInspector(userRow);
    const satelliteInspector = buildSatelliteResourceInspector(satelliteRow);
    const drawerItems = buildDataPanelNodeDetailDrawerItems(
      userInspector,
      satelliteInspector
    );

    expect(drawerItems).toHaveLength(2);
    expect(drawerItems[0]).toMatchObject({
      kind: "user",
      title: "用户 user-0",
      emptyLabel: "当前窗口暂无选中用户节点"
    });
    expect(drawerItems[0].fields).toEqual(userInspector.fields);
    expect(drawerItems[0].sections).toEqual(userInspector.sections);
    expect(drawerItems[1]).toMatchObject({
      kind: "satellite",
      title: "卫星 sat-0",
      emptyLabel: "当前窗口暂无选中卫星节点"
    });
    expect(drawerItems[1].fields).toEqual(satelliteInspector.fields);
    expect(drawerItems[1].sections).toEqual(satelliteInspector.sections);
    expect(
      buildDataPanelNodeDetailDrawerItems(
        {
          ...userInspector,
          sections: [
            {
              sectionId: "business_path",
              title: "业务链路",
              fields: [{ label: "路径", value: userRow.pathLabel }]
            }
          ]
        },
        satelliteInspector
      )[0].sections
    ).toEqual([
      {
        sectionId: "business_path",
        title: "业务链路",
        fields: [{ label: "路径", value: userRow.pathLabel }]
      }
    ]);
  });

  it("returns empty inspector shells when no row is visible", () => {
    expect(buildUserBusinessRequestInspector(null)).toEqual({
      title: "用户详情",
      subtitle: "当前窗口暂无用户节点",
      fields: []
    });
    expect(buildSatelliteResourceInspector(undefined)).toEqual({
      title: "卫星详情",
      subtitle: "当前窗口暂无卫星节点",
      fields: []
    });
  });
});

describe("buildDataPanelUserRequestHistory", () => {
  const history = {
    version: "v1",
    mode: "RECENT_USER_REQUEST_LIMITED",
    source: "BACKEND_RUNTIME_STATUS",
    history_scope: "STATUS_POLL_SAMPLED_VISIBLE_USERS",
    sample_policy: "ONE_SAMPLE_PER_RUNTIME_STATUS_PER_VISIBLE_USER",
    sample_limit: 3,
    user_count: 2,
    summary_item_count: 2,
    hidden_user_count: 1,
    history_user_count: 2,
    series_count: 2,
    series: [
      {
        user_id: "user-10",
        samples: [
          {
            sim_time: 1,
            communication_route_count: 2,
            available_route_count: 1,
            compute_service_count: 1,
            network_queue_count: 1,
            selected_satellite_id: "sat-3",
            destination_id: "compute-0",
            status: "ACTIVE/WAITING_ROUTE",
            primary_route_id: "route-10-a",
            primary_flow_id: "flow-10-a",
            latency_s: 0.12,
            capacity_mbps: 80,
            loss_proxy_rate: 0.02,
            service_state: "task-10/120ms/RUNNING"
          },
          {
            sim_time: 2,
            communication_route_count: 3,
            available_route_count: 2,
            compute_service_count: 1,
            network_queue_count: 0,
            selected_satellite_id: "sat-4",
            destination_id: "compute-1",
            status: "ACTIVE/AVAILABLE",
            primary_route_id: "route-10-b",
            primary_flow_id: "flow-10-b",
            latency_s: 0.08,
            capacity_mbps: 120,
            loss_proxy_rate: 0.01,
            service_state: "task-10/80ms/RUNNING"
          }
        ]
      },
      {
        user_id: "user-2",
        samples: [
          {
            sim_time: 3,
            communication_route_count: 1,
            available_route_count: 1,
            compute_service_count: 0,
            network_queue_count: 0,
            status: "ACTIVE/AVAILABLE"
          }
        ]
      }
    ]
  };

  it("defaults to the first deterministic user series", () => {
    const display = buildDataPanelUserRequestHistory(history);

    expect(display.sourceLabel).toBe("后端 user_request_history_v1");
    expect(display.selectedUserId).toBe("user-2");
    expect(display.availableUserIds).toEqual(["user-2", "user-10"]);
    expect(display.summaryLabel).toContain("状态轮询采样");
    expect(display.summaryLabel).toContain("1 个用户未进入历史窗口");
    expect(display.summaryLabel).toContain("单用户上限 3 点");
    expect(display.points).toEqual([
      {
        timeLabel: "3秒",
        simTime: 3,
        communicationRouteCount: 1,
        availableRouteCount: 1,
        computeServiceCount: 0,
        networkQueueCount: 0,
        latencyMs: 0,
        capacityMbps: 0,
        lossPercent: 0,
        selectedSatelliteId: "未选择",
        destinationId: "未声明",
        statusLabel: "ACTIVE/AVAILABLE",
        primaryRouteId: "none",
        primaryFlowId: "none",
        serviceLabel: "无服务状态"
      }
    ]);
  });

  it("uses explicit user selection and maps route quality fields", () => {
    const display = buildDataPanelUserRequestHistory(history, "user-10", 1);

    expect(display.selectedUserId).toBe("user-10");
    expect(display.points).toEqual([
      {
        timeLabel: "2秒",
        simTime: 2,
        communicationRouteCount: 3,
        availableRouteCount: 2,
        computeServiceCount: 1,
        networkQueueCount: 0,
        latencyMs: 80,
        capacityMbps: 120,
        lossPercent: 1,
        selectedSatelliteId: "sat-4",
        destinationId: "compute-1",
        statusLabel: "ACTIVE/AVAILABLE",
        primaryRouteId: "route-10-b",
        primaryFlowId: "flow-10-b",
        serviceLabel: "task-10/80ms/RUNNING"
      }
    ]);
  });

  it("falls back to an empty display when user history is unavailable", () => {
    expect(buildDataPanelUserRequestHistory(undefined)).toEqual({
      sourceLabel: "等待后端 user_request_history_v1",
      summaryLabel: "暂无用户业务历史",
      selectedUserId: null,
      availableUserIds: [],
      points: []
    });
  });
});

describe("buildSatelliteResourceRows", () => {
  it("prefers backend satellite service summaries when available", () => {
    const rows = buildSatelliteResourceRows(
      makeSnapshot(),
      undefined,
      {
        version: "v1",
        source: "BACKEND_RUNTIME_SNAPSHOT",
        satellite_count: 1,
        item_count: 1,
        hidden_satellite_count: 0,
        items: [
          {
            satellite_id: "sat-0",
            status: "BUSY",
            resource_role: "COMPUTE_NODE",
            resource_role_label: "Satellite compute node",
            service_user_ids: ["user-0", "user-1"],
            service_user_count: 2,
            primary_service_user_id: "user-0",
            next_hop_ids: ["compute-0", "sat-1"],
            next_hop_count: 2,
            primary_next_hop_id: "compute-0",
            primary_route_id: "route-a",
            primary_flow_id: "flow-a",
            route_count: 2,
            available_route_count: 1,
            network_queue_route_count: 1,
            compute_service_route_count: 1,
            network_service_route_count: 1,
            route_mix_label: "compute=1; network=1; queued=1",
            route_capacity_mbps: 120,
            route_demand_mbps: 100,
            route_latency_avg_s: 0.045,
            route_delay_variation_proxy_s: 0.004,
            route_loss_proxy_rate: 0.02,
            active_link_count: 3,
            active_access_link_count: 1,
            active_space_link_count: 2,
            compute_load_ratio: 0.64,
            compute_capacity_gflops_fp32: 100,
            compute_used_gflops_fp32: 64,
            compute_capacity_gflops_fp64: 8,
            compute_used_gflops_fp64: 2,
            compute_capacity_gpu_tflops_fp32: 2,
            compute_used_gpu_tflops_fp32: 1,
            compute_capacity_gpu_tflops_fp16: 4,
            compute_used_gpu_tflops_fp16: 2,
            compute_capacity_npu_tops_int8: 10,
            compute_used_npu_tops_int8: 4,
            compute_capacity_memory_gb: 32,
            compute_used_memory_gb: 8,
            compute_capacity_storage_gb: 512,
            compute_used_storage_gb: 64,
            running_task_count: 2,
            finished_task_count: 7
          }
        ]
      }
    );

    expect(rows.sourceLabel).toBe("backend satellite_service_summary_v1");
    expect(rows.items[0]).toMatchObject({
      satelliteId: "sat-0",
      statusLabel: "BUSY / Satellite compute node",
      loadLabel: "64%",
      serviceObjectLabel: "user-0, user-1 / 2 routes",
      nextHopLabel: "compute-0, sat-1 / 2 routes",
      cpuFp32Label: "64 / 100 GFLOPS",
      cpuFp64Label: "2 / 8 GFLOPS",
      npuLabel: "4 / 10 TOPS",
      taskLabel: "2 running / 7 done / compute=1; network=1; queued=1",
      networkLabel:
        "links 3 / access 1 / space 2 / routes 2 / queued 1 / cap 120 Mbps / demand 100 Mbps / lat 45 ms / loss 2% / primary route-a"
    });
  });

  it("fills backend-hidden satellites from snapshot fallback rows", () => {
    const rows = buildSatelliteResourceRows(
      makeSnapshot({
        satellites: Array.from({ length: 120 }, (_, index) => ({
          satellite_id: `sat-${index}`,
          sim_time: 10,
          position: [7_000_000, 0, 0],
          status: "ACTIVE"
        })),
        compute_nodes: Array.from({ length: 120 }, (_, index) => ({
          node_id: `sat-${index}`,
          running_tasks: index % 4,
          finished_tasks: index,
          capacity: 100,
          available_capacity: 80,
          status: "ACTIVE",
          load_ratio: 0.2
        }))
      }),
      undefined,
      {
        version: "v1",
        source: "BACKEND_RUNTIME_SNAPSHOT",
        satellite_count: 120,
        item_count: 1,
        hidden_satellite_count: 119,
        items: [
          {
            satellite_id: "sat-0",
            status: "BUSY",
            service_user_ids: ["user-0"],
            next_hop_ids: [],
            route_count: 1,
            available_route_count: 1,
            active_link_count: 1,
            active_access_link_count: 1,
            active_space_link_count: 0,
            compute_load_ratio: 0.5,
            compute_capacity_gflops_fp32: 100,
            compute_used_gflops_fp32: 50,
            compute_capacity_gflops_fp64: 0,
            compute_used_gflops_fp64: 0,
            compute_capacity_gpu_tflops_fp32: 0,
            compute_used_gpu_tflops_fp32: 0,
            compute_capacity_gpu_tflops_fp16: 0,
            compute_used_gpu_tflops_fp16: 0,
            compute_capacity_npu_tops_int8: 0,
            compute_used_npu_tops_int8: 0,
            compute_capacity_memory_gb: 0,
            compute_used_memory_gb: 0,
            compute_capacity_storage_gb: 0,
            compute_used_storage_gb: 0,
            running_task_count: 1,
            finished_task_count: 0
          }
        ]
      }
    );

    expect(rows.sourceLabel).toContain("快照补齐");
    expect(rows.summaryLabel).toContain("补齐 119");
    expect(rows.items).toHaveLength(120);
    expect(rows.items[0]).toMatchObject({
      satelliteId: "sat-0",
      statusLabel: "BUSY",
      cpuFp32Label: "50 / 100 GFLOPS"
    });
    expect(rows.items[119]).toMatchObject({
      satelliteId: "sat-119",
      cpuFp32Label: "20 / 100 GFLOPS"
    });
  });

  it("keeps 120 satellites visible in deterministic id order", () => {
    const rows = buildSatelliteResourceRows(
      makeSnapshot({
        satellites: Array.from({ length: 120 }, (_, index) => ({
          satellite_id: `sat-${index}`,
          sim_time: 10,
          position: [7_000_000, 0, 0],
          status: "ACTIVE"
        })),
        compute_nodes: Array.from({ length: 120 }, (_, index) => ({
          node_id: `sat-${index}`,
          running_tasks: index % 3,
          finished_tasks: index,
          capacity: 100,
          available_capacity: 75,
          status: "ACTIVE",
          load_ratio: 0.25
        }))
      })
    );

    expect(rows.items).toHaveLength(120);
    expect(rows.items[0].satelliteId).toBe("sat-0");
    expect(rows.items[119]).toMatchObject({
      satelliteId: "sat-119",
      cpuFp32Label: "25 / 100 GFLOPS",
      loadLabel: "25%"
    });
  });

  it("merges backend satellite KPI slices into resource, service, and network labels", () => {
    const rows = buildSatelliteResourceRows(
      makeSnapshot({
        satellites: [
          {
            satellite_id: "sat-0",
            sim_time: 10,
            position: [7_000_000, 0, 0],
            status: "ACTIVE"
          }
        ],
        compute_nodes: [
          {
            node_id: "sat-0",
            running_tasks: 0,
            finished_tasks: 0,
            capacity: 100,
            available_capacity: 95,
            status: "ACTIVE",
            load_ratio: 0.05
          }
        ],
        routes: [
          {
            route_id: "route-a",
            flow_id: "flow-a",
            path: ["user-0", "sat-0", "sat-1", "service-0"],
            latency: 0.1,
            capacity: 80,
            available: true
          },
          {
            route_id: "route-b",
            flow_id: "flow-b",
            path: ["user-1", "sat-0", "compute-0"],
            latency: 0.2,
            capacity: 40,
            available: true
          }
        ]
      }),
      {
        version: "v1",
        mode: "TOP_ACTIVITY_LIMITED",
        slices: [
          {
            satellite_id: "sat-0",
            active_link_count: 4,
            active_access_link_count: 2,
            active_space_link_count: 2,
            route_count: 3,
            available_route_count: 2,
            route_capacity_mbps: 120,
            route_demand_mbps: 100,
            route_latency_avg_s: 0.045,
            route_delay_variation_proxy_s: 0.005,
            route_loss_proxy_rate: 0.02,
            compute_capacity_gflops_fp32: 100,
            compute_used_gflops_fp32: 64,
            compute_capacity_gflops_fp64: 8,
            compute_used_gflops_fp64: 2,
            compute_capacity_gpu_tflops_fp32: 2,
            compute_used_gpu_tflops_fp32: 1,
            compute_capacity_npu_tops_int8: 10,
            compute_used_npu_tops_int8: 4,
            compute_capacity_memory_gb: 32,
            compute_used_memory_gb: 8,
            compute_capacity_storage_gb: 512,
            compute_used_storage_gb: 64,
            compute_load_ratio: 0.64,
            running_task_count: 2,
            finished_task_count: 7
          }
        ]
      }
    );

    expect(rows.sourceLabel).toBe("后端卫星KPI切片 + 快照算力节点");
    expect(rows.items[0]).toMatchObject({
      satelliteId: "sat-0",
      loadLabel: "64%",
      cpuFp32Label: "64 / 100 GFLOPS",
      cpuFp64Label: "2 / 8 GFLOPS",
      npuLabel: "4 / 10 TOPS",
      serviceObjectLabel: "user-0, user-1 / 关联 2 条",
      nextHopLabel: "compute-0, sat-1 / 关联 2 条",
      taskLabel: "2 运行 / 7 完成"
    });
    expect(rows.items[0].networkLabel).toContain("链路 4 / 路由 3");
    expect(rows.items[0].memoryStorageLabel).toContain("内存 8 / 32 GB");
  });
});

describe("buildDataPanelSatelliteResourceHistory", () => {
  const history = {
    version: "v1",
    mode: "RECENT_LIMITED",
    sample_limit: 3,
    satellite_count: 2,
    series_count: 2,
    series: [
      {
        satellite_id: "sat-10",
        samples: [
          {
            sim_time: 1,
            compute_load_ratio: 0.2,
            compute_used_gflops_fp32: 20,
            compute_used_gflops_fp64: 2,
            compute_used_gpu_tflops_fp32: 0.5,
            compute_used_gpu_tflops_fp16: 1,
            compute_used_npu_tops_int8: 3,
            compute_used_memory_gb: 4,
            compute_used_storage_gb: 8
          },
          {
            sim_time: 2,
            compute_load_ratio: 0.4,
            compute_used_gflops_fp32: 40,
            compute_used_gflops_fp64: 4,
            compute_used_gpu_tflops_fp32: 0.75,
            compute_used_gpu_tflops_fp16: 1.5,
            compute_used_npu_tops_int8: 5,
            compute_used_memory_gb: 6,
            compute_used_storage_gb: 10
          }
        ]
      },
      {
        satellite_id: "sat-2",
        samples: [
          {
            sim_time: 3,
            compute_load_ratio: 0.75,
            compute_used_gflops_fp32: 75,
            compute_used_memory_gb: 12,
            compute_used_storage_gb: 24
          }
        ]
      }
    ]
  };

  it("defaults to the first deterministic satellite series", () => {
    const display = buildDataPanelSatelliteResourceHistory(history);

    expect(display.sourceLabel).toBe("后端 satellite_kpi_history_v1");
    expect(display.selectedSatelliteId).toBe("sat-2");
    expect(display.availableSatelliteIds).toEqual(["sat-2", "sat-10"]);
    expect(display.summaryLabel).toContain("sat-2");
    expect(display.points).toEqual([
      {
        timeLabel: "3秒",
        simTime: 3,
        loadPercent: 75,
        usedFp32Gflops: 75,
        usedFp64Gflops: 0,
        usedGpuFp32Tflops: 0,
        usedGpuFp16Tflops: 0,
        usedNpuInt8Tops: 0,
        usedMemoryGb: 12,
        usedStorageGb: 24
      }
    ]);
  });

  it("uses an explicit satellite selection and bounds the sample window", () => {
    const display = buildDataPanelSatelliteResourceHistory(history, "sat-10", 1);

    expect(display.selectedSatelliteId).toBe("sat-10");
    expect(display.points).toEqual([
      {
        timeLabel: "2秒",
        simTime: 2,
        loadPercent: 40,
        usedFp32Gflops: 40,
        usedFp64Gflops: 4,
        usedGpuFp32Tflops: 0.75,
        usedGpuFp16Tflops: 1.5,
        usedNpuInt8Tops: 5,
        usedMemoryGb: 6,
        usedStorageGb: 10
      }
    ]);
  });

  it("falls back to an empty display when backend history is unavailable", () => {
    expect(buildDataPanelSatelliteResourceHistory(undefined)).toEqual({
      sourceLabel: "等待后端 satellite_kpi_history_v1",
      summaryLabel: "暂无单星资源历史",
      selectedSatelliteId: null,
      availableSatelliteIds: [],
      points: []
    });
  });
});

describe("buildDataPanelDetailScopeNotes", () => {
  it("explains full detail coverage separately from bounded satellite KPI slices", () => {
    const notes = buildDataPanelDetailScopeNotes(
      {
        sourceLabel: "backend user_request_summary_v1 + 快照补齐",
        summaryLabel: "1,200 users",
        items: Array.from({ length: 1200 }, (_, index) => ({
          userId: `user-${index}`,
          platformTypeLabel: "地面用户终端",
          communicationLabel: "无通信业务",
          computeLabel: "无计算业务",
          networkQueueLabel: "队列空",
          selectedSatelliteId: "未选择",
          destinationId: "未声明",
          placementLabel: "无计算放置",
          statusLabel: "IDLE",
          latencyCapacityLabel: "无链路",
          serviceLabel: "无业务",
          pathLabel: `user-${index}: no active route`
        }))
      },
      {
        sourceLabel: "backend satellite_service_summary_v1 + 快照补齐",
        summaryLabel: "1,200 satellites",
        items: Array.from({ length: 1200 }, (_, index) => ({
          satelliteId: `sat-${index}`,
          statusLabel: "ACTIVE",
          loadPercent: 0,
          loadLabel: "0%",
          serviceObjectLabel: "无服务对象",
          nextHopLabel: "无下一跳",
          cpuFp32Label: "0 / 100 GFLOPS",
          cpuFp64Label: "0 / 0 GFLOPS",
          gpuLabel: "FP32 0 / 0 TFLOPS / FP16 0 / 0 TFLOPS",
          npuLabel: "0 / 0 TOPS",
          memoryStorageLabel: "内存 0 / 0 GB / 存储 0 / 0 GB",
          taskLabel: "0 运行 / 0 完成",
          networkLabel: "links 0 / access 0 / space 0 / routes 0"
        }))
      },
      {
        version: "v1",
        source: "BACKEND_RUNTIME_SNAPSHOT",
        user_count: 1200,
        item_count: 1000,
        active_user_count: 80,
        compute_service_user_count: 20,
        waiting_user_count: 4,
        window_user_count: 1000,
        window_active_user_count: 64,
        window_compute_service_user_count: 12,
        window_waiting_user_count: 3,
        hidden_user_count: 200,
        items: []
      },
      {
        version: "v1",
        source: "BACKEND_RUNTIME_SNAPSHOT",
        satellite_count: 1200,
        item_count: 1000,
        window_satellite_count: 1000,
        hidden_satellite_count: 200,
        items: []
      },
      {
        version: "v1",
        mode: "TOP_ACTIVITY_LIMITED",
        slice_limit: 64,
        satellite_count: 1200,
        slice_count: 64,
        slices: []
      },
      {
        version: "v1",
        mode: "RECENT_LIMITED",
        slice_limit: 64,
        sample_limit: 32,
        satellite_count: 1200,
        series_count: 64,
        series: []
      }
    );

    expect(notes.map((note) => [note.label, note.value, note.tone])).toEqual([
      ["用户明细", "1,200 / 1,200 行", "limit"],
      ["卫星明细", "1,200 / 1,200 行", "limit"],
      ["卫星KPI切片", "64 / 1,200 切片", "limit"],
      ["单星历史", "64 / 1,200 条序列", "history"]
    ]);
    expect(notes[0].detail).toContain("全量活跃 80 / 算力业务 20 / 排队 4");
    expect(notes[0].detail).toContain("后端窗口返回 1,000 行，隐藏 200 行");
    expect(notes[1].detail).toContain("后端窗口返回 1,000 行，隐藏 200 行");
    expect(notes[2].detail).toContain("TOP_ACTIVITY_LIMITED，上限 64");
    expect(notes[2].detail).toContain("不等同于全量卫星明细");
    expect(notes[3].detail).toContain("卫星上限 64 / 单星样本上限 32");
  });

  it("falls back to a waiting note before backend observability summaries arrive", () => {
    expect(
      buildDataPanelDetailScopeNotes(
        { sourceLabel: "快照用户/路由", summaryLabel: "0", items: [] },
        { sourceLabel: "快照算力节点", summaryLabel: "0", items: [] }
      )
    ).toEqual([
      {
        label: "明细来源",
        value: "等待后端摘要",
        detail: "暂时使用快照回退行，后端 runtime observability 到达后会显示覆盖范围。",
        tone: "history"
      }
    ]);
  });
});

describe("detail row filters", () => {
  it("filters user request rows by node, destination, service, or path text", () => {
    const rows = buildUserBusinessRequestRows(
      makeSnapshot({
        ground_users: [
          { user_id: "user-0", status: "ACTIVE" },
          { user_id: "user-1", status: "ACTIVE" }
        ],
        routes: [
          {
            route_id: "route-a",
            flow_id: "flow-a",
            path: ["user-0", "sat-0", "compute-0"],
            latency: 0.1,
            capacity: 80,
            available: true
          },
          {
            route_id: "route-b",
            flow_id: "flow-b",
            path: ["user-1", "sat-1", "service-1"],
            latency: 0.2,
            capacity: 40,
            available: true
          }
        ]
      }),
      {
        version: "v1",
        mode: "RECENT_SERVICE_LIMITED",
        items: [
          {
            task_id: "task-a",
            input_flow_id: "flow-a",
            compute_node_id: "sat-0",
            service_placement_status: "PLACED",
            service_placement_bottleneck_resource: "cpu_gflops_fp32",
            service_placement_candidate_count: 2,
            service_placement_capable_candidate_count: 1,
            complete: false,
            input_network_latency_s: 0,
            compute_queue_delay_s: 0,
            compute_execution_delay_s: 0,
            output_network_latency_s: 0,
            total_latency_s: 0
          }
        ]
      }
    );

    expect(filterUserBusinessRequestRows(rows, "compute-0").items.map((row) => row.userId)).toEqual([
      "user-0"
    ]);
    expect(filterUserBusinessRequestRows(rows, "  SAT-1 ").items.map((row) => row.userId)).toEqual([
      "user-1"
    ]);
    expect(filterUserBusinessRequestRows(rows, "cpu_gflops").items.map((row) => row.userId)).toEqual([
      "user-0"
    ]);
    expect(filterUserBusinessRequestRows(rows, "").items).toBe(rows.items);
  });

  it("filters satellite resource rows by satellite, served user, or next hop", () => {
    const rows = buildSatelliteResourceRows(
      makeSnapshot(),
      undefined,
      {
        version: "v1",
        source: "BACKEND_RUNTIME_SNAPSHOT",
        satellite_count: 2,
        item_count: 2,
        hidden_satellite_count: 0,
        items: [
          {
            satellite_id: "sat-0",
            status: "ACTIVE",
            service_user_ids: ["user-0"],
            next_hop_ids: ["compute-0"],
            route_count: 1,
            available_route_count: 1,
            active_link_count: 1,
            active_access_link_count: 1,
            active_space_link_count: 0,
            compute_load_ratio: 0.2,
            compute_capacity_gflops_fp32: 100,
            compute_used_gflops_fp32: 20,
            compute_capacity_gflops_fp64: 0,
            compute_used_gflops_fp64: 0,
            compute_capacity_gpu_tflops_fp32: 0,
            compute_used_gpu_tflops_fp32: 0,
            compute_capacity_gpu_tflops_fp16: 0,
            compute_used_gpu_tflops_fp16: 0,
            compute_capacity_npu_tops_int8: 0,
            compute_used_npu_tops_int8: 0,
            compute_capacity_memory_gb: 0,
            compute_used_memory_gb: 0,
            compute_capacity_storage_gb: 0,
            compute_used_storage_gb: 0,
            running_task_count: 1,
            finished_task_count: 0
          },
          {
            satellite_id: "sat-1",
            status: "ACTIVE",
            service_user_ids: ["user-1"],
            next_hop_ids: ["sat-2"],
            route_count: 1,
            available_route_count: 1,
            active_link_count: 1,
            active_access_link_count: 0,
            active_space_link_count: 1,
            compute_load_ratio: 0.1,
            compute_capacity_gflops_fp32: 100,
            compute_used_gflops_fp32: 10,
            compute_capacity_gflops_fp64: 0,
            compute_used_gflops_fp64: 0,
            compute_capacity_gpu_tflops_fp32: 0,
            compute_used_gpu_tflops_fp32: 0,
            compute_capacity_gpu_tflops_fp16: 0,
            compute_used_gpu_tflops_fp16: 0,
            compute_capacity_npu_tops_int8: 0,
            compute_used_npu_tops_int8: 0,
            compute_capacity_memory_gb: 0,
            compute_used_memory_gb: 0,
            compute_capacity_storage_gb: 0,
            compute_used_storage_gb: 0,
            running_task_count: 0,
            finished_task_count: 1
          }
        ]
      }
    );

    expect(filterSatelliteResourceRows(rows, "compute-0").items.map((row) => row.satelliteId)).toEqual([
      "sat-0"
    ]);
    expect(filterSatelliteResourceRows(rows, "user-1").items.map((row) => row.satelliteId)).toEqual([
      "sat-1"
    ]);
  });
});

describe("paginateDetailRows", () => {
  it("derives large detail table budgets from backend pagination contract", () => {
    const contract = makeLargeDetailPaginationContract();

    expect(buildDataPanelDetailPageSizes(contract)).toEqual({
      users: 120,
      satellites: 96,
      routes: 64,
      services: 80,
      computeNodes: 50
    });
    expect(buildDataPanelPaginationContractNotes(contract)).toEqual([
      {
        label: "后端分页契约",
        value: "large_1200 / zero_based_offset",
        detail:
          "用户节点状态明细 120 行 @ /runtime/details/users；卫星资源消耗明细 96 行 @ /runtime/details/satellites；路由与瓶颈明细 64 行 @ /runtime/details/routes；业务服务生命周期明细 80 行 @ /runtime/details/services；算力节点资源明细 50 行 @ /runtime/details/compute-nodes；统一上限 5,000；估计隐藏 1,178 行通过后端游标读取",
        tone: "limit"
      }
    ]);
  });

  it("falls back to compatible table budgets without backend pagination contract", () => {
    expect(buildDataPanelDetailPageSizes(null)).toEqual({
      users: 80,
      satellites: 120,
      routes: 96,
      services: 120,
      computeNodes: 120
    });
    expect(buildDataPanelPaginationContractNotes(undefined)).toEqual([
      {
        label: "后端分页契约",
        value: "兼容模式",
        detail:
          "当前 backend_summary 未提供 large_detail_pagination_contract_v2，表格使用前端兼容窗口。",
        tone: "limit"
      }
    ]);
  });

  it("returns a deterministic bounded window for large detail tables", () => {
    const items = Array.from({ length: 250 }, (_, index) => `row-${index}`);

    expect(paginateDetailRows(items, 1, 100)).toEqual({
      items: items.slice(100, 200),
      totalCount: 250,
      pageIndex: 1,
      pageSize: 100,
      pageCount: 3,
      startIndex: 100,
      endIndex: 200
    });
  });

  it("clamps out-of-range pages and handles empty tables", () => {
    const items = Array.from({ length: 25 }, (_, index) => index);
    expect(paginateDetailRows(items, 9, 10)).toMatchObject({
      items: [20, 21, 22, 23, 24],
      pageIndex: 2,
      pageCount: 3,
      startIndex: 20,
      endIndex: 25
    });
    expect(paginateDetailRows([], 4, 10)).toMatchObject({
      items: [],
      totalCount: 0,
      pageIndex: 0,
      pageCount: 1,
      startIndex: 0,
      endIndex: 0
    });
  });

  it("rejects invalid page sizes", () => {
    expect(() => paginateDetailRows([1, 2, 3], 0, 0)).toThrow(RangeError);
  });

  it("summarizes the active detail window render budget for 1200 node scenarios", () => {
    const userPage = paginateDetailRows(
      Array.from({ length: 300 }, (_, index) => `user-${index}`),
      0,
      80
    );
    const satellitePage = paginateDetailRows(
      Array.from({ length: 1200 }, (_, index) => `sat-${index}`),
      2,
      120
    );

    expect(buildDataPanelDetailWindowPolicyNote(userPage, satellitePage)).toEqual({
      label: "表格窗口化",
      value: "200 / 1,500 行渲染",
      detail:
        "用户窗口 1-80 / 300，上限 80；卫星窗口 241-360 / 1,200，上限 120；渲染预算 200 行；预算来源 前端兼容窗口；隐藏 1,300 行等待翻页，避免大规模场景一次性展开 DOM。",
      tone: "limit"
    });
  });

  it("marks small filtered detail windows as fully rendered", () => {
    const userPage = paginateDetailRows(["user-0"], 0, 80);
    const satellitePage = paginateDetailRows([], 0, 120);

    expect(
      buildDataPanelDetailWindowPolicyNote(
        userPage,
        satellitePage,
        makeLargeDetailPaginationContract()
      )
    ).toEqual({
      label: "表格窗口化",
      value: "1 / 1 行渲染",
      detail:
        "用户窗口 1-1 / 1，上限 80；卫星窗口 0 / 0，上限 120；渲染预算 200 行；预算来源 后端契约 leo_twin.large_detail_pagination_contract.v2；当前筛选结果可在一屏窗口内完整渲染。",
      tone: "backend"
    });
  });
});

describe("buildRuntimeDetailSourceBadge", () => {
  it("marks backend-owned detail summaries distinctly from snapshot fallbacks", () => {
    expect(buildRuntimeDetailSourceBadge("backend user_request_summary_v1")).toMatchObject({
      label: "后端摘要",
      tone: "backend"
    });
    expect(
      buildRuntimeDetailSourceBadge("快照用户/路由 + 后端服务延迟历史")
    ).toMatchObject({
      label: "后端增强",
      tone: "mixed"
    });
    expect(buildRuntimeDetailSourceBadge("快照用户/路由")).toMatchObject({
      label: "快照回退",
      tone: "snapshot"
    });
  });
});

function makeLargeDetailPaginationContract() {
  return {
    version: "v2",
    contract_id: "leo_twin.large_detail_pagination_contract.v2",
    source_policy_ids: {
      scale_policy: "leo_twin.scale_policy.v2",
      lod_snapshot_policy: "leo_twin.lod_snapshot_policy.v2"
    },
    active_profile_id: "large_1200",
    active_scale_band: "LARGE_1200",
    cursor_model: {
      cursor_type: "zero_based_offset",
      limit_type: "positive_int",
      next_cursor_policy: "min(total_count, cursor + returned_item_count)",
      has_more_policy: "next_cursor < total_count",
      max_limit: 5000
    },
    collections: [
      makeLargeDetailPaginationCollection({
        collection: "ground_users",
        kind: "users",
        label_zh: "用户节点状态明细",
        endpoint: "/runtime/details/users",
        recommended_limit: 120,
        hidden_count_estimate: 280
      }),
      makeLargeDetailPaginationCollection({
        collection: "satellites",
        kind: "satellites",
        label_zh: "卫星资源消耗明细",
        endpoint: "/runtime/details/satellites",
        recommended_limit: 96,
        hidden_count_estimate: 880
      }),
      makeLargeDetailPaginationCollection({
        collection: "routes",
        kind: "routes",
        label_zh: "路由与瓶颈明细",
        endpoint: "/runtime/details/routes",
        recommended_limit: 64,
        hidden_count_estimate: 18
      }),
      makeLargeDetailPaginationCollection({
        collection: "services",
        kind: "services",
        label_zh: "业务服务生命周期明细",
        endpoint: "/runtime/details/services",
        recommended_limit: 80,
        hidden_count_estimate: 0
      }),
      makeLargeDetailPaginationCollection({
        collection: "compute_nodes",
        kind: "compute_nodes",
        label_zh: "算力节点资源明细",
        endpoint: "/runtime/details/compute-nodes",
        recommended_limit: 50,
        hidden_count_estimate: 0
      })
    ],
    combined_node_endpoint: {
      kind: "nodes",
      endpoint: "/runtime/details/nodes",
      summary_type: "RuntimeNodeDetailPageV1",
      composition: ["ground_users", "satellites"],
      purpose: "combined user and satellite node detail cards",
      stable_ordering: "all users first, then satellites; each group sorted by stable id"
    },
    frontend_policy: {
      rendering: "use backend cursor windows; do not render unbounded rows",
      hidden_rows: "HIDDEN_ROWS_REQUIRE_BACKEND_CURSOR_OR_EXPLICIT_DETAIL_REQUEST",
      raw_counts: "display total counts from summary count fields",
      local_inference:
        "frontend may format rows but must not invent pagination semantics"
    },
    determinism: {
      ordering: "backend-owned stable ordering per collection",
      cursor_replay: "same snapshot, cursor, and limit return identical rows",
      mutation_policy: "read-only observation endpoints"
    },
    event_kernel_policy: "NO_EVENT_KERNEL_BEHAVIOR_CHANGE"
  };
}

function makeLargeDetailPaginationCollection(overrides: {
  collection: string;
  kind: string;
  label_zh: string;
  endpoint: string;
  recommended_limit: number;
  hidden_count_estimate: number;
}) {
  return {
    ...overrides,
    http_method: "GET",
    query_parameters: ["cursor", "limit"],
    response_envelope_type: "RUNTIME_DETAIL_PAGE",
    summary_type: "RuntimeDetailSummary",
    item_type: "RuntimeDetailItem",
    stable_key: `${overrides.kind}_id`,
    sort_policy: "stable id ascending",
    count_field: `${overrides.collection}_count`,
    estimated_total_count:
      overrides.recommended_limit + overrides.hidden_count_estimate,
    default_limit: 100,
    max_limit: 5000,
    cursor_required: overrides.hidden_count_estimate > 0,
    cursor_required_for_hidden_rows: true,
    window_source: "lod_snapshot_policy_v2.detail_windows",
    availability: "HTTP_CURSOR_ENDPOINT_AVAILABLE"
  };
}

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
