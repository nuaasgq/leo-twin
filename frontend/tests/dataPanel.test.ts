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
  buildDataPanelBackendCursorDisplay,
  buildDataPanelDetailScopeNotes,
  buildDataPanelDetailCoverageNote,
  buildDataPanelSelectedDetailEvidenceNote,
  buildDataPanelServiceTraceCorrelationEvidenceNote,
  buildDataPanelDetailPageSizes,
  buildDataPanelPaginationContractNotes,
  buildDataPanelDetailWindowPolicyNote,
  buildDataPanelDisplaySummary,
  buildDataPanelExportArtifactHealthDisplay,
  buildDataPanelExportAcceptanceReportStatus,
  buildDataPanelBenchmarkEvidenceFocus,
  buildDataPanelArtifactHealthInspectorFocus,
  buildDataPanelPackageArtifactInspectorFocus,
  buildDataPanelRouteEvidenceInspectorFocus,
  buildDataPanelServiceTraceEvidenceInspectorFocus,
  buildDataPanelUserServiceRequestEvidenceInspectorFocus,
  buildDataPanelBenchmarkEvidenceArtifactViewerDisplay,
  buildDataPanelJsonArtifactInspectorRows,
  buildDataPanelExportBoundaryAlignmentDisplay,
  buildDataPanelExportCatalogDisplay,
  buildDataPanelExportCompareDisplay,
  buildDataPanelExportCompareStatus,
  buildDataPanelExportDiagnosticsDisplay,
  buildDataPanelExportDiagnosticsStatus,
  buildDataPanelExportHistoryDisplay,
  buildDataPanelExportManifestInspectorDisplay,
  buildDataPanelExportManifestInspectorStatus,
  buildDataPanelExportReproducibilityBoundaryDisplay,
  buildDataPanelExportReviewSummaryDisplay,
  buildDataPanelExportReviewSummaryStatus,
  buildDataPanelExportUserServiceRequestStatus,
  buildDataPanelExportReviewCompletionSummary,
  buildDataPanelExportRouteDetailItemDisplay,
  buildDataPanelExportRouteDetailItemStatus,
  buildDataPanelExportServiceTraceItemDisplay,
  buildDataPanelExportServiceTraceItemStatus,
  buildDataPanelExportServiceTraceLiveComparisonDisplay,
  buildDataPanelExportServiceTraceLiveComparisonStatus,
  buildDataPanelExportServiceTraceComparisonReviewRecord,
  buildDataPanelExportServiceTraceComparisonReviewReportDisplay,
  buildDataPanelExportServiceTraceComparisonReviewReportStatus,
  buildDataPanelExportServiceTraceComparisonReviewSaveStatus,
  buildDataPanelExportPackageAuditIndexArtifactDisplay,
  buildDataPanelExportPackageHandoffReportArtifactDisplay,
  buildDataPanelExportPackageAuditIndexDisplay,
  buildDataPanelExportPackageAuditIndexStatus,
  buildDataPanelExportScenarioReviewChecklistStatus,
  buildDataPanelExportScenarioReviewChecklistTemplateComparisonStatus,
  buildDataPanelExportScenarioReviewBundleDisplay,
  buildDataPanelExportScenarioReviewBundleStatus,
  buildDataPanelScenarioReviewWorkflowInspectorFocus,
  buildDataPanelScenarioReviewChecklistDraft,
  buildDataPanelScenarioReviewChecklistSaveRequest,
  updateDataPanelScenarioReviewChecklistDraft,
  buildDataPanelExportRouteComparisonReviewArtifactDisplay,
  buildDataPanelExportRouteComparisonReviewReportDisplay,
  buildDataPanelExportRouteComparisonReviewReportStatus,
  buildDataPanelExportRouteComparisonReviewRecord,
  buildDataPanelExportRouteComparisonReviewSaveStatus,
  buildDataPanelExportRouteLiveComparisonDisplay,
  buildDataPanelExportRouteLiveComparisonStatus,
  buildDataPanelExportRouteDetailIndexDisplay,
  buildDataPanelExportRouteDetailPageDisplay,
  buildDataPanelExportRouteDetailIndexStatus,
  buildDataPanelExportServiceLifecycleTraceStatus,
  buildDataPanelExportRestoreActionDisplay,
  buildDataPanelExportRestorePreflightDisplay,
  buildDataPanelExportRestorePreflightStatus,
  buildDataPanelFilterScopeNotes,
  buildDataPanelNetworkFormulaInputs,
  buildDataPanelNetworkComponentTail,
  buildDataPanelNetworkKpiCaveats,
  buildDataPanelNetworkKpiBenchmarkValidationDisplay,
  buildDataPanelNetworkKpiCalibrationDisplay,
  buildDataPanelNetworkKpiCredibilityDisplay,
  buildDataPanelNetworkKpiFormulaEvidenceDisplay,
  buildDataPanelNetworkKpiVariationExplanationDisplay,
  buildDataPanelNetworkKpiFormulaInspector,
  buildDataPanelModelAssumptionsDisplay,
  buildDataPanelModelTrustEvidenceWorkspace,
  buildDataPanelRouteProvenanceTrustDisplay,
  buildDataPanelNetworkKpiProvenanceItems,
  buildDataPanelNetworkKpiSource,
  buildDataPanelNodeDetailDrawerItems,
  buildDataPanelReproducibilityDisplay,
  buildDataPanelRouteConstraints,
  buildDataPanelRouteExplanationRows,
  buildDataPanelRuntimeProgress,
  buildDataPanelSatelliteResourceHistory,
  buildDataPanelServiceLatencyDisplay,
  buildDataPanelServiceLifecycleTraceDisplay,
  buildDataPanelServiceTraceFocus,
  buildDataPanelServiceTraceBrowserDisplay,
  buildServiceTraceCorrelationInspector,
  buildDataPanelServiceDetailRows,
  buildDataPanelServiceLatencyRows,
  buildDataPanelComputeNodeDetailRows,
  buildComputeNodeExactDetailInspector,
  buildRouteExplanationDetailInspector,
  buildServiceLifecycleDetailInspector,
  buildServiceTraceDetailDrawerItem,
  buildSatelliteDetailDrawerSectionsV1,
  buildSatelliteResourceInspector,
  buildDataPanelSummary,
  buildDataPanelTelemetry,
  buildDataPanelTrafficDisplay,
  buildDataPanelUserConfigurationContractDisplay,
  buildDataPanelUserConfigurationFieldSections,
  buildDataPanelUserConfigurationReferenceFieldSections,
  buildDataPanelUserConfigurationReferenceFieldRows,
  buildDataPanelUserConfigurationTemplateValidationRows,
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
  filterRuntimeExportRouteDetailIndexRoutes,
  filterSatelliteResourceRows,
  filterServiceLifecycleTraceDisplay,
  filterUserBusinessRequestRows,
  appendExactDetailStatusToInspector,
  paginateDetailRows,
  resolveNetworkQualityKpis,
  RuntimeDetailPages,
  runtimeNodeDetailPageToSummary,
  runtimeExportServiceTracePageToLifecycleTrace,
  selectComputeNodeDetailRow,
  selectRuntimeNodeDetailSummary,
  selectRuntimeComputeNodeDetailPage,
  selectRouteExplanationRow,
  selectServiceDetailRow,
  selectServiceLifecycleTraceRow,
  selectRuntimeServiceTracePage,
  serviceTraceDetailMatchesRow,
  serviceTraceDetailCursorFilters,
  selectRuntimeRouteExplanationSummary,
  selectRuntimeSatelliteDetailCard,
  selectRuntimeSatelliteServiceSummary,
  selectRuntimeServiceDetailPage,
  selectRuntimeUserDetailCard,
  selectRuntimeUserRequestSummary,
  selectSatelliteResourceRow,
  selectExactDetailRequestStatus,
  selectUserConfigurationApplyPayload,
  selectUserBusinessRequestRow,
  userConfigurationPreflightModeEnabled,
  userConfigurationTextEndpointFormat
} from "../src/dashboard/data_panel/DataPanel";
import {
  FidelitySummary,
  GeneratedScenarioConfig,
  RuntimeStatusPayload,
  RuntimeUserServiceRequestSummaryV2,
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
      user_service_request_summary_v2: {
        version: "v2",
        source: "BACKEND_RUNTIME_STATUS",
        summary_scope: "USER_SERVICE_REQUEST_WINDOW",
        request_model: "FLOW_LEVEL_USER_SERVICE_REQUEST_PROXY",
        route_model: "FLOW_LEVEL_ROUTE_PROXY",
        compute_model: "SERVICE_LIFECYCLE_PROXY",
        packet_level_simulation: false,
        frontend_inference_required: false,
        cursor: 20,
        limit: 100,
        next_cursor: 21,
        has_more: false,
        user_count: 2,
        request_count: 2,
        item_count: 1,
        active_user_count: 1,
        active_request_count: 1,
        communication_request_count: 1,
        compute_service_user_count: 0,
        compute_request_count: 0,
        waiting_user_count: 0,
        network_waiting_request_count: 0,
        completed_request_count: 0,
        window_user_count: 1,
        window_request_count: 1,
        window_active_user_count: 1,
        window_active_request_count: 1,
        window_compute_service_user_count: 0,
        window_compute_request_count: 0,
        window_waiting_user_count: 0,
        window_network_waiting_request_count: 0,
        hidden_user_count: 1,
        hidden_request_count: 1,
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
      },
      services: {
        version: "v1",
        source: "SERVICE_LATENCY_HISTORY",
        summary_scope: "SERVICE_LIFECYCLE_DETAIL_WINDOW",
        cursor: 0,
        limit: 20,
        next_cursor: 1,
        has_more: false,
        service_count: 1,
        item_count: 1,
        complete_service_count: 0,
        queued_service_count: 1,
        window_service_count: 1,
        hidden_service_count: 0,
        items: [
          {
            service_id: "service-page",
            task_id: "task-page",
            complete: false,
            service_state: "RUNNING",
            service_state_label: "Service running",
            input_network_latency_s: 0.1,
            compute_queue_delay_s: 0.2,
            compute_execution_delay_s: 0.3,
            output_network_latency_s: 0.4,
            total_latency_s: 1,
            stage_count: 0,
            stages: []
          }
        ]
      },
      serviceTraces: {
        version: "v2",
        source: "SERVICE_LATENCY_HISTORY",
        source_summary: "service_latency_history_v1",
        summary_scope: "SERVICE_LIFECYCLE_TRACE_WINDOW",
        cursor: 10,
        limit: 20,
        next_cursor: 11,
        has_more: false,
        service_count: 1,
        trace_count: 1,
        complete_trace_count: 1,
        running_trace_count: 0,
        incomplete_trace_count: 0,
        hidden_trace_count: 0,
        items: [
          {
            trace_id: "trace:service-page",
            service_id: "service-page",
            task_id: "task-page",
            service_class: "COMPUTE_SERVICE",
            input_flow_id: "service-page-input",
            output_flow_id: "service-page-output",
            input_route_id: "route-page-input",
            output_route_id: "route-page-output",
            compute_node_id: "sat-page",
            placement_status: "PLACED",
            input_network_latency_s: 0.1,
            compute_queue_delay_s: 0.2,
            compute_execution_delay_s: 0.3,
            output_network_latency_s: 0.4,
            total_latency_s: 1,
            terminal_state: "COMPLETE",
            terminal_state_reason: "TOTAL_LATENCY_OBSERVED",
            stage_count: 0,
            observed_stage_count: 0,
            pending_stage_count: 0,
            stages: []
          }
        ]
      },
      computeNodes: {
        version: "v1",
        source: "BACKEND_RUNTIME_SNAPSHOT",
        summary_scope: "COMPUTE_NODE_DETAIL_WINDOW",
        cursor: 0,
        limit: 20,
        next_cursor: 1,
        has_more: false,
        compute_node_count: 1,
        item_count: 1,
        busy_compute_node_count: 1,
        window_compute_node_count: 1,
        hidden_compute_node_count: 0,
        items: [
          {
            node_id: "sat-page",
            platform_type: "SATELLITE_COMPUTE_NODE",
            status: "BUSY",
            compute_load_ratio: 0.65,
            compute_capacity_gflops_fp32: 100,
            compute_used_gflops_fp32: 65,
            compute_available_gflops_fp32: 35,
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
            finished_task_count: 2
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
    expect(selectRuntimeUserRequestSummary(runtimeStatus, null)?.cursor).toBe(20);
    expect(selectRuntimeUserRequestSummary(runtimeStatus, null)?.source).toBe(
      "BACKEND_RUNTIME_STATUS"
    );
    expect(selectRuntimeNodeDetailSummary(runtimeStatus, null)?.users[0].title).toBe(
      "状态用户"
    );
    expect(
      selectRuntimeRouteExplanationSummary(runtimeStatus, null)?.items[0].route_id
    ).toBe("route-status");
    expect(selectRuntimeServiceDetailPage(detailPages)?.items[0].service_id).toBe(
      "service-page"
    );
    expect(
      selectRuntimeServiceTracePage(runtimeStatus, detailPages)?.items[0].trace_id
    ).toBe("trace:service-page");
    expect(
      selectRuntimeServiceTracePage(runtimeStatus, null)?.items[0].trace_id
    ).toBeUndefined();
    expect(selectRuntimeComputeNodeDetailPage(detailPages)?.items[0].node_id).toBe(
      "sat-page"
    );
  });

  it("builds service trace backend cursor filters", () => {
    expect(
      serviceTraceDetailCursorFilters(
        " route:input ",
        "COMPLETE",
        " sat-a ",
        "OUTPUT_NETWORK",
        "TOTAL_LATENCY_OBSERVED"
      )
    ).toEqual({
      query: "route:input",
      terminalState: "COMPLETE",
      computeNodeId: "sat-a",
      stageKind: "OUTPUT_NETWORK",
      terminalReason: "TOTAL_LATENCY_OBSERVED"
    });
    expect(serviceTraceDetailCursorFilters("", "ALL", "")).toEqual({});
  });
});

describe("buildDataPanelBackendCursorDisplay", () => {
  it("summarizes backend cursor windows and navigation cursors", () => {
    expect(
      buildDataPanelBackendCursorDisplay(
        {
          cursor: 80,
          limit: 40,
          next_cursor: 120,
          has_more: true,
          item_count: 40
        },
        180
      )
    ).toEqual({
      rangeLabel: "81-120 / 180",
      statusLabel: "下一游标 120",
      previousCursor: 40,
      nextCursor: 120,
      canPrevious: true,
      canNext: true
    });
  });

  it("handles empty or terminal backend cursor windows deterministically", () => {
    expect(
      buildDataPanelBackendCursorDisplay(
        {
          cursor: -5,
          limit: 0,
          next_cursor: 0,
          has_more: false,
          item_count: 0
        },
        0
      )
    ).toEqual({
      rangeLabel: "0 / 0",
      statusLabel: "当前已到最后一页",
      previousCursor: 0,
      nextCursor: 0,
      canPrevious: false,
      canNext: false
    });
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
        template_validation: {
          version: "v1",
          evidence_id: "sees.user_configuration_template_validation.v1",
          source: "BACKEND_USER_CONFIGURATION",
          schema_id: "sees.user_configuration.v2",
          validation_scope: "APPROVED_EXECUTABLE_TEMPLATES",
          template_count: 4,
          valid_template_count: 4,
          invalid_template_count: 0,
          all_templates_valid: true,
          templates: [
            {
              id: "baseline_72sat",
              label: "72-satellite baseline",
              path: "configs/templates/sees_user_detailed.example.yaml",
              scale: "72 satellites",
              fidelity_mode: "SMALL_SCALE_PER_SATELLITE_ORBIT",
              expected_kpi_behavior: "Stable baseline KPI curves.",
              file_exists: true,
              file_hash:
                "sha256:5656565656565656565656565656565656565656565656565656565656565656",
              config_hash:
                "sha256:7878787878787878787878787878787878787878787878787878787878787878",
              load_ok: true,
              validation_ok: true,
              error_count: 0,
              errors: [],
              config_summary: {
                satellite_count: 72,
                user_count: 1000,
                compute_nodes: 72,
                traffic_class: "COMPUTE_SERVICE",
                destination_type: "COMPUTE_NODE",
                runtime_mode: "REAL_TIME",
                runtime_duration: 600,
                runtime_seed: 20260703,
                orbit_update_mode: null,
                space_link_mode: null
              },
              row_hash:
                "sha256:9090909090909090909090909090909090909090909090909090909090909090"
            }
          ],
          evidence_hash:
            "sha256:3434343434343434343434343434343434343434343434343434343434343434"
        },
        load_command: {
          type: "RUNTIME_CONTROL",
          action: "LOAD_TEMPLATE",
          payload_key: "template_id",
          requires_uninitialized_runtime: true
        }
      },
      {
        version: "v1",
        reference_id: "sees.user_configuration_reference.v1",
        source: "BACKEND_USER_CONFIGURATION",
        schema_id: "sees.user_configuration.v2",
        reference_scope: "FULL_USER_CONFIGURATION_FILE_AND_FRONTEND_SURFACE",
        format: "YAML_OR_JSON_MAPPING",
        frontend_policy: "CONTROL_PANEL_KEY_FIELDS_ONLY",
        detailed_config_file: "configs/sees_control.yaml",
        generated_config_file: "configs/generated_full_system_demo.json",
        template_config_file: "configs/templates/sees_user_detailed.example.yaml",
        template_profiles: [],
        unknown_key_policy: "REJECT",
        defaulting_policy: "OMITTED_FIELDS_USE_BACKEND_DEFAULTS",
        mutation_policy: {
          ui_surface: "KEY_FIELDS_ONLY",
          full_file_surface: "DETAILED_CONFIG_FILE",
          validate_endpoint: "POST /scenario/user-config/validate-text",
          apply_commands: ["CONFIG_UPDATE", "LOAD_TEMPLATE"]
        },
        field_count: 42,
        key_field_count: 12,
        file_only_field_count: 30,
        section_count: 2,
        sections: [
          {
            section: "scenario",
            purpose: "Scenario configuration reference",
            field_count: 2,
            key_field_count: 1,
            file_only_field_count: 1,
            key_paths: ["scenario.satellite_count"],
            file_only_paths: ["scenario.compute_gpu_tflops_fp16"]
          },
          {
            section: "network",
            purpose: "Network configuration reference",
            field_count: 1,
            key_field_count: 0,
            file_only_field_count: 1,
            key_paths: [],
            file_only_paths: ["network.carrier_frequency_hz"]
          }
        ],
        fields: [
          {
            path: "scenario.satellite_count",
            section: "scenario",
            label: "Satellite count",
            description: "Primary constellation size.",
            value_type: "integer",
            editable_surface: "CONTROL_PANEL_KEY_FIELD",
            ui_key_field: true,
            default_value: 72,
            current_value: 120,
            required_in_user_file: false,
            validation_rules: ["minimum 1"],
            minimum: 1
          },
          {
            path: "scenario.compute_gpu_tflops_fp16",
            section: "scenario",
            label: "GPU FP16",
            description: "Detailed file-only FP16 capacity.",
            value_type: "number",
            editable_surface: "DETAILED_CONFIG_FILE_ONLY",
            ui_key_field: false,
            default_value: 5,
            current_value: 5,
            required_in_user_file: false,
            validation_rules: ["minimum 0"],
            minimum: 0,
            unit: "TFLOPS"
          },
          {
            path: "network.carrier_frequency_hz",
            section: "network",
            label: "Carrier frequency",
            description: "Detailed file-only carrier metadata.",
            value_type: "number",
            editable_surface: "DETAILED_CONFIG_FILE_ONLY",
            ui_key_field: false,
            default_value: 20000000000,
            current_value: 20000000000,
            required_in_user_file: false,
            validation_rules: ["minimum 1"],
            minimum: 1,
            unit: "Hz"
          }
        ],
        model_boundaries: {
          event_kernel_policy: "NO_EVENT_KERNEL_BEHAVIOR_CHANGE",
          packet_level_simulation: false,
          external_simulators: false,
          forbidden_integrations: ["STK", "EXATA", "AFSIM", "DDS"],
          frontend_semantics_source: "BACKEND_USER_CONFIGURATION"
        },
        operator_workflow: ["Use control panel key fields first."],
        notes: ["Reference is backend-owned."],
        reference_hash:
          "sha256:1212121212121212121212121212121212121212121212121212121212121212"
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
      "format YAML_OR_JSON_MAPPING",
      "file-only 30",
      "templates valid 4/4",
      "template errors 0",
      "template evidence 343434343434",
      "reference 121212121212"
    ]);
    expect(display?.referenceSummaryLabels).toEqual([
      "reference 121212121212",
      "分区 2",
      "字段 42",
      "关键 12",
      "文件 30",
      "模板 0"
    ]);
    expect(display?.templateValidationRows).toEqual([
      {
        id: "baseline_72sat",
        label: "72-satellite baseline",
        statusLabel: "VALIDATED",
        pathLabel: "configs/templates/sees_user_detailed.example.yaml",
        scaleLabel: "72 sat / 1,000 user / 72 compute / COMPUTE_SERVICE / COMPUTE_NODE",
        runtimeLabel: "REAL_TIME / 600s / seed 20,260,703",
        modeLabel: "orbit auto / space auto",
        fileHashLabel: "565656565656",
        configHashLabel: "787878787878",
        errorLabel: "none"
      }
    ]);
    expect(display?.referenceBoundaryLabels).toEqual([
      "语义源 BACKEND_USER_CONFIGURATION",
      "Event Kernel NO_EVENT_KERNEL_BEHAVIOR_CHANGE",
      "无包级仿真",
      "无外部仿真器",
      "禁用 STK/EXATA/AFSIM/DDS"
    ]);
    expect(display?.referenceRows).toEqual([
      {
        path: "scenario.compute_gpu_tflops_fp16",
        section: "scenario",
        label: "GPU FP16",
        description: "Detailed file-only FP16 capacity.",
        typeLabel: "number / TFLOPS",
        surfaceLabel: "详细配置文件 / 可省略",
        defaultValueLabel: "5",
        currentValueLabel: "5",
        validationLabel: "minimum 0"
      },
      {
        path: "scenario.satellite_count",
        section: "scenario",
        label: "Satellite count",
        description: "Primary constellation size.",
        typeLabel: "integer",
        surfaceLabel: "关键控件 / 可省略",
        defaultValueLabel: "72",
        currentValueLabel: "120",
        validationLabel: "minimum 1"
      },
      {
        path: "network.carrier_frequency_hz",
        section: "network",
        label: "Carrier frequency",
        description: "Detailed file-only carrier metadata.",
        typeLabel: "number / Hz",
        surfaceLabel: "详细配置文件 / 可省略",
        defaultValueLabel: "20,000,000,000",
        currentValueLabel: "20,000,000,000",
        validationLabel: "minimum 1"
      }
    ]);
  });

  it("reports loading and error states for user configuration contract", () => {
    expect(
      buildDataPanelUserConfigurationContractDisplay(null, null, null, null, true)
    ).toMatchObject({
      tone: "pending",
      statusLabel: "加载中"
    });
    expect(
      buildDataPanelUserConfigurationContractDisplay(
        null,
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
    expect(
      buildDataPanelUserConfigurationContractDisplay(null, null, null, null)
    ).toBeNull();
  });
});

describe("buildDataPanelUserConfigurationTemplateValidationRows", () => {
  it("maps backend template validation rows without local validation", () => {
    expect(
      buildDataPanelUserConfigurationTemplateValidationRows({
        version: "v1",
        evidence_id: "sees.user_configuration_template_validation.v1",
        source: "BACKEND_USER_CONFIGURATION",
        schema_id: "sees.user_configuration.v2",
        validation_scope: "APPROVED_EXECUTABLE_TEMPLATES",
        template_count: 2,
        valid_template_count: 1,
        invalid_template_count: 1,
        all_templates_valid: false,
        templates: [
          {
            id: "large_scale_1200sat",
            label: "1200-satellite scale mode",
            path: "configs/templates/sees_user_large_scale_1200.example.yaml",
            file_exists: true,
            file_hash:
              "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            config_hash:
              "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            load_ok: true,
            validation_ok: true,
            error_count: 0,
            errors: [],
            config_summary: {
              satellite_count: 1200,
              user_count: 1200,
              compute_nodes: 1200,
              traffic_class: "COMPUTE_SERVICE",
              destination_type: "COMPUTE_NODE",
              runtime_mode: "REAL_TIME",
              runtime_duration: 300,
              runtime_seed: 20260707,
              orbit_update_mode: "BATCH",
              space_link_mode: "BOUNDED_CANDIDATE"
            },
            row_hash:
              "sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
          },
          {
            id: "missing_template",
            label: "Missing template",
            path: "configs/templates/missing.yaml",
            file_exists: false,
            file_hash: "",
            config_hash: "",
            load_ok: false,
            validation_ok: false,
            error_count: 1,
            errors: [
              {
                source: "template_file",
                message: "template file is missing"
              }
            ],
            row_hash:
              "sha256:dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"
          }
        ],
        evidence_hash:
          "sha256:eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
      })
    ).toEqual([
      {
        id: "large_scale_1200sat",
        label: "1200-satellite scale mode",
        statusLabel: "VALIDATED",
        pathLabel: "configs/templates/sees_user_large_scale_1200.example.yaml",
        scaleLabel: "1,200 sat / 1,200 user / 1,200 compute / COMPUTE_SERVICE / COMPUTE_NODE",
        runtimeLabel: "REAL_TIME / 300s / seed 20,260,707",
        modeLabel: "BATCH / BOUNDED_CANDIDATE",
        fileHashLabel: "aaaaaaaaaaaa",
        configHashLabel: "bbbbbbbbbbbb",
        errorLabel: "none"
      },
      {
        id: "missing_template",
        label: "Missing template",
        statusLabel: "FILE_MISSING",
        pathLabel: "configs/templates/missing.yaml",
        scaleLabel: "",
        runtimeLabel: "runtime unknown",
        modeLabel: "orbit auto / space auto",
        fileHashLabel: "",
        configHashLabel: "",
        errorLabel: "template_file: template file is missing"
      }
    ]);
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

describe("buildDataPanelUserConfigurationReferenceFieldSections", () => {
  it("summarizes backend-owned reference sections deterministically", () => {
    const sections = buildDataPanelUserConfigurationReferenceFieldSections({
      version: "v1",
      reference_id: "sees.user_configuration.reference.v1",
      source: "BACKEND_USER_CONFIGURATION_REFERENCE",
      schema_id: "sees.user_configuration.v2",
      reference_scope: "FULL_USER_CONFIGURATION_REFERENCE",
      format: "YAML_OR_JSON_MAPPING",
      frontend_policy: "CONTROL_PANEL_KEY_FIELDS_ONLY",
      detailed_config_file: "configs/sees_control.yaml",
      generated_config_file: "configs/generated_full_system_demo.json",
      template_config_file: "configs/templates/sees_control.template.yaml",
      template_profiles: [],
      unknown_key_policy: "REJECT",
      defaulting_policy: "OMITTED_FIELDS_USE_BACKEND_DEFAULTS",
      mutation_policy: {
        ui_surface: "KEY_FIELDS_ONLY",
        full_file_surface: "YAML_OR_JSON_MAPPING",
        validate_endpoint: "/scenario/user-config/validate",
        apply_commands: ["CONFIG_UPDATE"]
      },
      field_count: 3,
      key_field_count: 1,
      file_only_field_count: 2,
      section_count: 2,
      sections: [
        {
          section: "scenario",
          purpose: "Scenario scale and runtime controls.",
          field_count: 2,
          key_field_count: 1,
          file_only_field_count: 1,
          key_paths: ["scenario.satellite_count"],
          file_only_paths: ["scenario.compute_gpu_tflops_fp32"]
        },
        {
          section: "network",
          purpose: "Network proxy settings.",
          field_count: 1,
          key_field_count: 0,
          file_only_field_count: 1,
          key_paths: [],
          file_only_paths: ["network.loss_proxy_enabled"]
        }
      ],
      fields: [
        {
          path: "scenario.satellite_count",
          section: "scenario",
          label: "Satellite count",
          description: "Total satellite nodes.",
          value_type: "number",
          default_value: 72,
          current_value: 72,
          editable_surface: "CONTROL_PANEL_KEY_FIELD",
          ui_key_field: true,
          required_in_user_file: false,
          validation_rules: ["minimum 1"]
        },
        {
          path: "scenario.compute_gpu_tflops_fp32",
          section: "scenario",
          label: "FP32 GPU",
          description: "Per-satellite FP32 GPU peak capacity.",
          value_type: "number",
          default_value: 0,
          current_value: 0,
          editable_surface: "DETAILED_CONFIG_FILE_ONLY",
          ui_key_field: false,
          required_in_user_file: false,
          validation_rules: ["minimum 0"]
        },
        {
          path: "network.loss_proxy_enabled",
          section: "network",
          label: "Loss proxy",
          description: "Enables deterministic flow-level loss proxy.",
          value_type: "boolean",
          default_value: true,
          current_value: true,
          editable_surface: "DETAILED_CONFIG_FILE_ONLY",
          ui_key_field: false,
          required_in_user_file: false,
          validation_rules: []
        }
      ],
      model_boundaries: {
        event_kernel_policy: "NO_EVENT_KERNEL_BEHAVIOR_CHANGE",
        packet_level_simulation: false,
        external_simulators: false,
        forbidden_integrations: ["STK", "EXATA", "AFSIM", "DDS"],
        frontend_semantics_source: "BACKEND_USER_CONFIGURATION"
      },
      operator_workflow: ["Edit key fields in the control panel first."],
      notes: ["Detailed fields remain file-owned."],
      reference_hash:
        "sha256:1234123412341234123412341234123412341234123412341234123412341234"
    });

    expect(sections).toEqual([
      {
        sectionPath: "scenario",
        purpose: "Scenario scale and runtime controls.",
        metaLabels: ["字段 2", "关键 1", "文件 1"],
        sampleFields: [
          {
            path: "scenario.satellite_count",
            label: "scenario.satellite_count / Satellite count",
            description: "Total satellite nodes."
          },
          {
            path: "scenario.compute_gpu_tflops_fp32",
            label: "scenario.compute_gpu_tflops_fp32 / FP32 GPU",
            description: "Per-satellite FP32 GPU peak capacity."
          }
        ]
      },
      {
        sectionPath: "network",
        purpose: "Network proxy settings.",
        metaLabels: ["字段 1", "关键 0", "文件 1"],
        sampleFields: [
          {
            path: "network.loss_proxy_enabled",
            label: "network.loss_proxy_enabled / Loss proxy",
            description: "Enables deterministic flow-level loss proxy."
          }
        ]
      }
    ]);
  });
});

describe("buildDataPanelUserConfigurationReferenceFieldRows", () => {
  it("builds deterministic full reference table rows", () => {
    const rows = buildDataPanelUserConfigurationReferenceFieldRows({
      version: "v1",
      reference_id: "sees.user_configuration.reference.v1",
      source: "BACKEND_USER_CONFIGURATION_REFERENCE",
      schema_id: "sees.user_configuration.v2",
      reference_scope: "FULL_USER_CONFIGURATION_REFERENCE",
      format: "YAML_OR_JSON_MAPPING",
      frontend_policy: "CONTROL_PANEL_KEY_FIELDS_ONLY",
      detailed_config_file: "configs/sees_control.yaml",
      generated_config_file: "configs/generated_full_system_demo.json",
      template_config_file: "configs/templates/sees_control.template.yaml",
      template_profiles: [],
      unknown_key_policy: "REJECT",
      defaulting_policy: "OMITTED_FIELDS_USE_BACKEND_DEFAULTS",
      mutation_policy: {
        ui_surface: "KEY_FIELDS_ONLY",
        full_file_surface: "YAML_OR_JSON_MAPPING",
        validate_endpoint: "/scenario/user-config/validate",
        apply_commands: ["CONFIG_UPDATE"]
      },
      field_count: 2,
      key_field_count: 1,
      file_only_field_count: 1,
      section_count: 2,
      sections: [
        {
          section: "network",
          purpose: "Network proxy settings.",
          field_count: 1,
          key_field_count: 0,
          file_only_field_count: 1,
          key_paths: [],
          file_only_paths: ["network.loss_proxy_enabled"]
        },
        {
          section: "scenario",
          purpose: "Scenario scale controls.",
          field_count: 1,
          key_field_count: 1,
          file_only_field_count: 0,
          key_paths: ["scenario.satellite_count"],
          file_only_paths: []
        }
      ],
      fields: [
        {
          path: "scenario.satellite_count",
          section: "scenario",
          label: "Satellite count",
          description: "Total satellite nodes.",
          value_type: "integer",
          default_value: 72,
          current_value: 120,
          editable_surface: "CONTROL_PANEL_KEY_FIELD",
          ui_key_field: true,
          required_in_user_file: false,
          validation_rules: ["minimum 1"]
        },
        {
          path: "network.loss_proxy_enabled",
          section: "network",
          label: "Loss proxy",
          description: "Enables deterministic flow-level loss proxy.",
          value_type: "boolean",
          default_value: true,
          current_value: false,
          editable_surface: "DETAILED_CONFIG_FILE_ONLY",
          ui_key_field: false,
          required_in_user_file: true,
          validation_rules: []
        }
      ],
      model_boundaries: {
        event_kernel_policy: "NO_EVENT_KERNEL_BEHAVIOR_CHANGE",
        packet_level_simulation: false,
        external_simulators: false,
        forbidden_integrations: ["STK", "EXATA", "AFSIM", "DDS"],
        frontend_semantics_source: "BACKEND_USER_CONFIGURATION"
      },
      operator_workflow: [],
      notes: [],
      reference_hash:
        "sha256:3434343434343434343434343434343434343434343434343434343434343434"
    });

    expect(rows).toEqual([
      {
        path: "network.loss_proxy_enabled",
        section: "network",
        label: "Loss proxy",
        description: "Enables deterministic flow-level loss proxy.",
        typeLabel: "boolean",
        surfaceLabel: "详细配置文件 / 文件必填",
        defaultValueLabel: "true",
        currentValueLabel: "false",
        validationLabel: "无额外规则"
      },
      {
        path: "scenario.satellite_count",
        section: "scenario",
        label: "Satellite count",
        description: "Total satellite nodes.",
        typeLabel: "integer",
        surfaceLabel: "关键控件 / 可省略",
        defaultValueLabel: "72",
        currentValueLabel: "120",
        validationLabel: "minimum 1"
      }
    ]);
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
          reviewSummaryHref:
            "/runtime/export/packages/integration-demo-new/review-summary",
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
          reviewSummaryHref:
            "/runtime/export/packages/integration-demo-old/review-summary",
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

  it("summarizes selected package artifact health from backend catalog records", () => {
    const display = buildDataPanelExportArtifactHealthDisplay(
      {
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
            catalog_key: "PACKAGE:pkg-review",
            export_type: "PACKAGE",
            package_id: "pkg-review",
            package_dir: "artifacts/runtime_exports/pkg-review",
            relative_package_dir: "pkg-review",
            file_count: 1,
            manifest_hash:
              "sha256:0000000000000000000000000000000000000000000000000000000000000000",
            current_sim_time: 12,
            processed_event_count: 100,
            files: [
              {
                name: "package-only",
                filename: "package_only.json",
                bytes: 64,
                sha256:
                  "sha256:9999999999999999999999999999999999999999999999999999999999999999"
              }
            ]
          },
          {
            catalog_key: "ARCHIVE:pkg-review",
            export_type: "ARCHIVE",
            package_id: "pkg-review",
            package_dir: "artifacts/runtime_exports/pkg-review",
            relative_package_dir: "pkg-review",
            file_count: 6,
            manifest_hash:
              "sha256:1111111111111111111111111111111111111111111111111111111111111111",
            current_sim_time: 12,
            processed_event_count: 100,
            archive_filename: "pkg-review.zip",
            archive_sha256:
              "sha256:2222222222222222222222222222222222222222222222222222222222222222",
            archive_bytes: 8192,
            files: [
              {
                name: "config_snapshot",
                filename: "config_snapshot.json",
                bytes: 100,
                sha256:
                  "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
              },
              {
                name: "events",
                filename: "events.jsonl",
                bytes: 2048,
                sha256:
                  "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
              },
              {
                name: "manifest",
                filename: "manifest.json",
                bytes: 120,
                sha256:
                  "sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
              },
              {
                name: "review_summary",
                filename: "review_summary_v1.json",
                bytes: 512,
                sha256:
                  "sha256:dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"
              },
              {
                name: "service_lifecycle_trace",
                filename: "service_lifecycle_trace_v2.json",
                bytes: 4096,
                sha256:
                  "sha256:eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
              },
              {
                name: "summary",
                filename: "summary.json",
                bytes: 300,
                sha256:
                  "sha256:ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
              }
            ]
          }
        ]
      },
      "pkg-review",
      {
        type: "RUNTIME_EXPORT_REVIEW_SUMMARY_V1",
        version: "v1",
        summary_id: "leo_twin.runtime_export_review_summary.v1",
        source: "BACKEND_RUNTIME_EXPORT",
        summary_scope: "USER_READABLE_RESULT_PACKAGE_REVIEW",
        package_id: "pkg-review",
        package_dir: "artifacts/runtime_exports/pkg-review",
        review_status: "INCOMPLETE",
        scenario: {
          seed: 4321,
          satellite_count: 72,
          user_count: 20,
          compute_node_count: 2,
          duration_seconds: 120
        },
        runtime: {
          lifecycle_state: "STOPPED",
          current_sim_time: 120,
          processed_event_count: 4096,
          queued_event_count: 0
        },
        reproducibility: {
          manifest_id: "leo_twin.runtime_reproducibility_manifest.v1",
          manifest_hash:
            "sha256:1111111111111111111111111111111111111111111111111111111111111111",
          config_hash:
            "sha256:2222222222222222222222222222222222222222222222222222222222222222",
          generated_config_hash:
            "sha256:3333333333333333333333333333333333333333333333333333333333333333",
          event_kernel_policy: "NO_EVENT_KERNEL_BEHAVIOR_CHANGE"
        },
        artifacts: {
          artifact_count: 6,
          artifact_filenames: [
            "config_snapshot.json",
            "events.jsonl",
            "manifest.json",
            "review_summary_v1.json",
            "service_lifecycle_trace_v2.json",
            "summary.json"
          ],
          required_filenames: [
            "config_snapshot.json",
            "events.jsonl",
            "manifest.json",
            "metrics.csv",
            "summary.json"
          ],
          missing_required_filenames: ["metrics.csv"],
          service_lifecycle_trace_exported: true,
          review_summary_exported: true
        },
        review_notes: ["metrics.csv is required"],
        summary_hash:
          "sha256:abababababababababababababababababababababababababababababababab"
      }
    );

    expect(display).toMatchObject({
      packageId: "pkg-review",
      sourceLabel: "BACKEND_RUNTIME_EXPORT_CATALOG / ARCHIVE / files",
      summaryLabel: "pkg-review / 登记 6 个文件 / 缺失 1 个"
    });
    expect(display?.rows).toContainEqual(
      expect.objectContaining({
        filename: "events.jsonl",
        roleLabel: "必需",
        statusLabel: "必需已登记",
        hashLabel: "bbbbbbbbbbbb",
        href: "/runtime/export/packages/pkg-review/files/events.jsonl",
        required: true,
        present: true
      })
    );
    expect(display?.rows).toContainEqual(
      expect.objectContaining({
        filename: "metrics.csv",
        roleLabel: "必需",
        statusLabel: "缺失",
        sizeLabel: "-",
        hashLabel: "-",
        href: null,
        required: true,
        present: false
      })
    );
    expect(display?.rows.some((row) => row.filename === "package_only.json")).toBe(
      false
    );
    expect(
      buildDataPanelExportArtifactHealthDisplay(undefined, "pkg-review", null)
    ).toBeNull();
  });

  it("marks the artifact health row linked to the selected benchmark evidence focus", () => {
    const catalog = {
      version: "v1",
      source: "BACKEND_RUNTIME_EXPORT_CATALOG",
      catalog_scope: "PERSISTED_EXPORT_PACKAGES",
      catalog_file: "artifacts/runtime_exports/runtime_export_catalog_v1.json",
      export_root: "artifacts/runtime_exports",
      record_count: 1,
      catalog_hash:
        "sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
      latest_export: null,
      records: [
        {
          catalog_key: "ARCHIVE:pkg-review",
          export_type: "ARCHIVE",
          package_id: "pkg-review",
          package_dir: "artifacts/runtime_exports/pkg-review",
          relative_package_dir: "pkg-review",
          file_count: 2,
          manifest_hash:
            "sha256:1111111111111111111111111111111111111111111111111111111111111111",
          current_sim_time: 12,
          processed_event_count: 100,
          archive_filename: "pkg-review.zip",
          archive_sha256:
            "sha256:2222222222222222222222222222222222222222222222222222222222222222",
          archive_bytes: 8192,
          files: [
            {
              name: "manifest",
              filename: "manifest.json",
              bytes: 120,
              sha256:
                "sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
            },
            {
              name: "network_kpi_benchmark_validation",
              filename: "network_kpi_benchmark_validation_v1.json",
              bytes: 512,
              sha256:
                "sha256:dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"
            }
          ]
        }
      ]
    };
    const focus = buildDataPanelBenchmarkEvidenceFocus({
      tone: "different",
      groupLabel: "expected range",
      itemLabel: "avg_latency_ms",
      statusLabel: "FAIL",
      expectedLabel: "expected 20-80 ms",
      observedLabel: "observed 120 ms",
      issueLabel: "latency outside benchmark range",
      hashLabel: "deadbeefcafe",
      contextLabel: "KPI benchmark / avg_latency_ms",
      pointerLabel: "json /checks/0",
      jsonPointer: "/checks/0",
      artifactLabel: "network_kpi_benchmark_validation_v1.json",
      artifactHref:
        "/runtime/export/packages/pkg-review/files/network_kpi_benchmark_validation_v1.json",
      artifactTitle:
        "network_kpi_benchmark_validation_v1.json contains the backend-owned evidence."
    });

    const display = buildDataPanelExportArtifactHealthDisplay(
      catalog,
      "pkg-review",
      null,
      focus
    );

    expect(
      display?.rows.find(
        (row) => row.filename === "network_kpi_benchmark_validation_v1.json"
      )
    ).toMatchObject({
      focused: true,
      inspectable: true,
      focusLabel: "expected range / avg_latency_ms / FAIL / deadbeefcafe"
    });
    expect(display?.rows.find((row) => row.filename === "manifest.json")).toMatchObject({
      focused: false,
      inspectable: true,
      focusLabel: ""
    });
    expect(
      buildDataPanelArtifactHealthInspectorFocus(
        display?.rows.find((row) => row.filename === "manifest.json")
      )
    ).toMatchObject({
      focusSourceLabel: "Artifact inspector focus",
      statusLabel: "artifact / manifest.json",
      jsonPointer: "",
      artifactLabel: "manifest.json",
      artifactHref: "/runtime/export/packages/pkg-review/files/manifest.json"
    });
    expect(
      buildDataPanelBenchmarkEvidenceArtifactViewerDisplay(
        buildDataPanelArtifactHealthInspectorFocus(
          display?.rows.find((row) => row.filename === "manifest.json")
        ),
        {
          manifest_id: "leo_twin.runtime_reproducibility_manifest.v1",
          artifact_count: 2
        },
        false,
        null
      )
    ).toMatchObject({
      tone: "match",
      statusLabel: "pointer target resolved",
      summaryLabel: "manifest.json / /",
      inspectorEnabled: true,
      inspectorRows: [
        expect.objectContaining({
          pointer: "",
          pointerLabel: "json /",
          selected: true
        }),
        expect.objectContaining({
          pointer: "/artifact_count"
        }),
        expect.objectContaining({
          pointer: "/manifest_id"
        })
      ]
    });
    expect(
      buildDataPanelArtifactHealthInspectorFocus({
        filename: "events.jsonl",
        roleLabel: "required",
        statusLabel: "registered",
        sizeLabel: "1 KiB",
        hashLabel: "events",
        href: "/runtime/export/packages/pkg-review/files/events.jsonl",
        required: true,
        present: true,
        inspectable: false,
        focused: false,
        focusLabel: "",
        title: "events.jsonl"
      })
    ).toBeNull();
  });

  it("surfaces saved route comparison review report artifacts from backend catalog", () => {
    const catalog = {
      version: "v1",
      source: "BACKEND_RUNTIME_EXPORT_CATALOG",
      catalog_scope: "PERSISTED_EXPORT_PACKAGES",
      catalog_file: "artifacts/runtime_exports/runtime_export_catalog_v1.json",
      export_root: "artifacts/runtime_exports",
      record_count: 1,
      catalog_hash:
        "sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
      latest_export: null,
      records: [
        {
          catalog_key: "PACKAGE:pkg-review",
          export_type: "PACKAGE",
          package_id: "pkg-review",
          package_dir: "artifacts/runtime_exports/pkg-review",
          relative_package_dir: "pkg-review",
          file_count: 3,
          manifest_hash:
            "sha256:1111111111111111111111111111111111111111111111111111111111111111",
          current_sim_time: 12,
          processed_event_count: 100,
          files: [
            {
              name: "route_comparison_review_report_v1",
              filename: "route_comparison_review_report_v1.json",
              bytes: 2048,
              sha256:
                "sha256:7777777777777777777777777777777777777777777777777777777777777777"
            },
            {
              name: "export_package_audit_index_v1",
              filename: "export_package_audit_index_v1.json",
              bytes: 1024,
              sha256:
                "sha256:9999999999999999999999999999999999999999999999999999999999999999"
            },
            {
              name: "package_handoff_report_v1",
              filename: "package_handoff_report_v1.md",
              bytes: 3072,
              sha256:
                "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
            }
          ]
        }
      ]
    };

    expect(
      buildDataPanelExportRouteComparisonReviewArtifactDisplay(
        catalog,
        "pkg-review",
        "sha256:8888888888888888888888888888888888888888888888888888888888888888"
      )
    ).toEqual({
      packageId: "pkg-review",
      tone: "match",
      statusLabel: "review report artifact present",
      summaryLabel: "pkg-review / 2 KiB / file 777777777777",
      hashLabels: [
        "catalog cccccccccccc",
        "file 777777777777",
        "report 888888888888"
      ],
      artifactHref:
        "/runtime/export/packages/pkg-review/files/route_comparison_review_report_v1.json",
      artifactTitle:
        "route_comparison_review_report_v1.json / 2 KiB / sha256:7777777777777777777777777777777777777777777777777777777777777777"
    });

    expect(
      buildDataPanelExportPackageAuditIndexArtifactDisplay(
        catalog,
        "pkg-review",
        "sha256:8888888888888888888888888888888888888888888888888888888888888888"
      )
    ).toEqual({
      packageId: "pkg-review",
      tone: "match",
      statusLabel: "audit index artifact present",
      summaryLabel: "pkg-review / 1 KiB / file 999999999999",
      hashLabels: [
        "catalog cccccccccccc",
        "audit 999999999999",
        "route report 888888888888"
      ],
      artifactHref:
        "/runtime/export/packages/pkg-review/files/export_package_audit_index_v1.json",
      artifactTitle:
        "export_package_audit_index_v1.json / 1 KiB / sha256:9999999999999999999999999999999999999999999999999999999999999999"
    });

    expect(
      buildDataPanelExportPackageHandoffReportArtifactDisplay(
        catalog,
        "pkg-review",
        "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
      )
    ).toEqual({
      packageId: "pkg-review",
      tone: "match",
      statusLabel: "handoff report artifact present",
      summaryLabel: "pkg-review / 3 KiB / file aaaaaaaaaaaa",
      hashLabels: [
        "catalog cccccccccccc",
        "report aaaaaaaaaaaa",
        "completion bbbbbbbbbbbb"
      ],
      artifactHref: "/runtime/export/packages/pkg-review/handoff-report",
      artifactTitle:
        "package_handoff_report_v1.md / 3 KiB / sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    });

    expect(
      buildDataPanelExportRouteComparisonReviewArtifactDisplay(
        {
          ...catalog,
          records: [
            {
              ...catalog.records[0],
              file_count: 0,
              files: []
            }
          ]
        },
        "pkg-review"
      )
    ).toMatchObject({
      packageId: "pkg-review",
      tone: "different",
      statusLabel: "review report not saved",
      artifactHref: null,
      hashLabels: [
        "catalog cccccccccccc",
        "package PACKAGE",
        "report hash waiting"
      ]
    });

    expect(
      buildDataPanelExportPackageAuditIndexArtifactDisplay(
        {
          ...catalog,
          records: [
            {
              ...catalog.records[0],
              file_count: 0,
              files: []
            }
          ]
        },
        "pkg-review"
      )
    ).toMatchObject({
      packageId: "pkg-review",
      tone: "different",
      statusLabel: "audit index not saved",
      artifactHref: null,
      hashLabels: [
        "catalog cccccccccccc",
        "package PACKAGE",
        "route report hash waiting"
      ]
    });

    expect(
      buildDataPanelExportPackageHandoffReportArtifactDisplay(
        {
          ...catalog,
          records: [
            {
              ...catalog.records[0],
              file_count: 0,
              files: []
            }
          ]
        },
        "pkg-review"
      )
    ).toMatchObject({
      packageId: "pkg-review",
      tone: "different",
      statusLabel: "handoff report not saved",
      artifactHref: null,
      hashLabels: [
        "catalog cccccccccccc",
        "package PACKAGE",
        "completion hash waiting"
      ]
    });

    expect(
      buildDataPanelExportRouteComparisonReviewArtifactDisplay(undefined, "pkg-review")
    ).toBeNull();
    expect(
      buildDataPanelExportPackageAuditIndexArtifactDisplay(undefined, "pkg-review")
    ).toBeNull();
    expect(
      buildDataPanelExportPackageHandoffReportArtifactDisplay(undefined, "pkg-review")
    ).toBeNull();
  });

  it("summarizes loaded export package audit indexes by evidence section", () => {
    const auditIndex = {
      type: "RUNTIME_EXPORT_PACKAGE_AUDIT_INDEX_V1",
      version: "v1",
      audit_index_id: "leo_twin.runtime_export_package_audit_index.v1",
      source: "BACKEND_RUNTIME_EXPORT_PACKAGE",
      audit_scope: "RESULT_PACKAGE_LONG_TERM_AUDIT_INDEX",
      package_id: "pkg-review",
      package_dir: "artifacts/runtime_exports/pkg-review",
      manifest_hash:
        "sha256:1111111111111111111111111111111111111111111111111111111111111111",
      control_config_hash:
        "sha256:2222222222222222222222222222222222222222222222222222222222222222",
      generated_config_hash:
        "sha256:3333333333333333333333333333333333333333333333333333333333333333",
      runtime_state_hash:
        "sha256:4444444444444444444444444444444444444444444444444444444444444444",
      runtime_export_boundary_hash:
        "sha256:5555555555555555555555555555555555555555555555555555555555555555",
      boundary_alignment_hash:
        "sha256:6666666666666666666666666666666666666666666666666666666666666666",
      boundary_alignment_status: "ALIGNED",
      boundary_alignment_warnings: [],
      user_configuration_binding_v1: {
        type: "USER_CONFIGURATION_AUDIT_BINDING_V1",
        version: "v1",
        binding_id: "leo_twin.user_configuration_audit_binding.v1",
        source: "BACKEND_RUNTIME_EXPORT_PACKAGE",
        schema_id: "sees.user_configuration.v2",
        export_scope: "CURRENT_EFFECTIVE_SEES_CONFIG",
        format: "JSON_MAPPING",
        config_hash:
          "sha256:1212121212121212121212121212121212121212121212121212121212121212",
        export_hash:
          "sha256:1313131313131313131313131313131313131313131313131313131313131313",
        validation_ok: true,
        validation_error_count: 0,
        unknown_key_policy: "REJECT",
        defaulting_policy: "OMITTED_FIELDS_USE_BACKEND_DEFAULTS",
        import_paths: ["CONFIG_UPDATE control message for partial updates"],
        binding_hash:
          "sha256:1414141414141414141414141414141414141414141414141414141414141414"
      },
      user_configuration_schema_id: "sees.user_configuration.v2",
      user_configuration_config_hash:
        "sha256:1212121212121212121212121212121212121212121212121212121212121212",
      user_configuration_export_hash:
        "sha256:1313131313131313131313131313131313131313131313131313131313131313",
      user_configuration_validation_ok: true,
      review_summary_hash:
        "sha256:7777777777777777777777777777777777777777777777777777777777777777",
      diagnostics_hash:
        "sha256:8888888888888888888888888888888888888888888888888888888888888888",
      network_kpi_formula_evidence_hash:
        "sha256:edededededededededededededededededededededededededededededededed",
      network_kpi_formula_evidence_status: "FORMULA_AND_TIME_EVIDENCE_READY",
      network_kpi_formula_evidence_present: true,
      network_kpi_formula_evidence_missing_selected_input_count: 0,
      user_configuration_template_validation_hash:
        "sha256:fefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefe",
      user_configuration_template_validation_status: "ALL_TEMPLATES_VALID",
      user_configuration_template_validation_present: true,
      user_configuration_template_validation_all_templates_valid: true,
      user_configuration_template_validation_invalid_template_count: 0,
      traffic_demand_explanation_hash:
        "sha256:7878787878787878787878787878787878787878787878787878787878787878",
      traffic_demand_explanation_present: true,
      traffic_demand_explanation_request_count: 20,
      traffic_demand_explanation_compute_service_request_count: 8,
      traffic_demand_explanation_frontend_inference_required: false,
      user_service_request_summary_hash:
        "sha256:abababababababababababababababababababababababababababababababab",
      user_service_request_summary_present: true,
      user_service_request_summary_request_count: 20,
      user_service_request_summary_exported_request_count: 18,
      user_service_request_summary_hidden_request_count: 2,
      route_comparison_review_report_hash:
        "sha256:9999999999999999999999999999999999999999999999999999999999999999",
      route_comparison_review_report_present: true,
      service_trace_comparison_review_report_hash:
        "sha256:edededededededededededededededededededededededededededededededed",
      service_trace_comparison_review_report_present: true,
      service_trace_comparison_review_record_count: 2,
      service_trace_comparison_review_error_count: 0,
      artifact_count: 3,
      artifact_hashes: [
        {
          name: "config_snapshot",
          filename: "config_snapshot.json",
          bytes: 1024,
          sha256:
            "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        },
        {
          name: "manifest",
          filename: "manifest.json",
          bytes: 2048,
          sha256:
            "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
        },
        {
          name: "diagnostics_bundle_v1",
          filename: "diagnostics_bundle_v1.json",
          bytes: 4096,
          sha256:
            "sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
        }
      ],
      required_artifact_filenames: ["config_snapshot.json", "manifest.json"],
      missing_required_artifact_filenames: [],
      self_artifact_excluded_from_hashes: true,
      audit_status: "AUDIT_READY",
      audit_warnings: [],
      forbidden_external_integrations: ["STK", "EXATA", "AFSIM", "DDS"],
      packet_level_simulation: false,
      event_replay_restore: false,
      model_recomputation: false,
      package_mutation_on_read: false,
      audit_hash:
        "sha256:dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"
    };

    const display = buildDataPanelExportPackageAuditIndexDisplay(auditIndex, 2);

    expect(display).toEqual({
      packageId: "pkg-review",
      tone: "match",
      statusLabel: "audit ready",
      summaryLabel:
        "pkg-review / AUDIT_READY / audit dddddddddddd / artifacts 3",
      auditHref:
        "/runtime/export/packages/pkg-review/files/export_package_audit_index_v1.json",
      manifestLabels: [
        "manifest 111111111111",
        "control 222222222222",
        "generated 333333333333",
        "runtime 444444444444"
      ],
      configurationLabels: [
        "schema sees.user_configuration.v2",
        "config 121212121212",
        "export 131313131313",
        "binding 141414141414",
        "validation ok"
      ],
      boundaryLabels: [
        "boundary 555555555555",
        "alignment 666666666666",
        "status ALIGNED",
        "self hash excluded yes"
      ],
      diagnosticsLabels: [
        "review 777777777777",
        "diagnostics 888888888888",
        "KPI formula FORMULA_AND_TIME_EVIDENCE_READY",
        "KPI formula missing inputs 0",
        "KPI formula edededededed",
        "config templates ALL_TEMPLATES_VALID",
        "config template invalid 0",
        "config templates valid",
        "config template fefefefefefe",
        "traffic demand present",
        "traffic requests 20",
        "traffic compute 8",
        "traffic frontend inference no",
        "traffic demand 787878787878",
        "user services present",
        "user service requests 20",
        "user services exported 18",
        "user services hidden 2",
        "user services abababababab",
        "packet no",
        "recompute no"
      ],
      routeReviewLabels: [
        "route report present",
        "route report 999999999999",
        "event replay restore no",
        "package mutation no"
      ],
      serviceTraceReviewLabels: [
        "service trace report present",
        "service trace report edededededed",
        "service trace records 2",
        "service trace errors 0"
      ],
      artifactRows: [
        {
          filename: "config_snapshot.json",
          sizeLabel: "1 KiB",
          hashLabel: "aaaaaaaaaaaa"
        },
        {
          filename: "manifest.json",
          sizeLabel: "2 KiB",
          hashLabel: "bbbbbbbbbbbb"
        }
      ],
      artifactSummaryLabel: "showing 2 of 3 artifact hashes / hidden 1",
      warningLabels: []
    });
    expect(
      buildDataPanelExportPackageAuditIndexStatus(display, "pkg-review")
    ).toMatchObject({
      tone: "match",
      auditHref:
        "/runtime/export/packages/pkg-review/files/export_package_audit_index_v1.json",
      artifactSummaryLabel: "showing 2 of 3 artifact hashes / hidden 1"
    });
    expect(
      buildDataPanelExportPackageAuditIndexStatus(null, "pkg-review", true)
    ).toMatchObject({
      tone: "pending",
      statusLabel: "loading audit index"
    });
    expect(
      buildDataPanelExportPackageAuditIndexStatus(
        null,
        "pkg-review",
        false,
        "audit failed"
      )
    ).toMatchObject({
      tone: "error",
      warningLabels: ["audit failed"]
    });
  });

  it("summarizes scenario review bundles as a guided package entry", () => {
    const bundle = {
      type: "RUNTIME_EXPORT_SCENARIO_REVIEW_BUNDLE_V1",
      version: "v1",
      bundle_id: "leo_twin.runtime_export_scenario_review_bundle.v1",
      source: "BACKEND_RUNTIME_EXPORT_PACKAGE",
      review_scope: "USER_CONFIGURATION_TO_RESULT_PACKAGE_REVIEW",
      package_id: "pkg-review",
      package_dir: "artifacts/runtime_exports/pkg-review",
      scenario: {
        seed: 7,
        satellite_count: 72,
        user_count: 20,
        compute_node_count: 12,
        duration_seconds: 120
      },
      runtime: {
        lifecycle_state: "STOPPED",
        current_sim_time: 120,
        processed_event_count: 4200,
        queued_event_count: 0
      },
      user_configuration: {
        type: "USER_CONFIGURATION_AUDIT_BINDING_V1",
        version: "v1",
        binding_id: "leo_twin.user_configuration_audit_binding.v1",
        source: "BACKEND_RUNTIME_EXPORT_PACKAGE",
        schema_id: "sees.user_configuration.v2",
        export_scope: "CURRENT_EFFECTIVE_SEES_CONFIG",
        format: "JSON_MAPPING",
        config_hash:
          "sha256:1212121212121212121212121212121212121212121212121212121212121212",
        export_hash:
          "sha256:1313131313131313131313131313131313131313131313131313131313131313",
        validation_ok: true,
        validation_error_count: 0,
        unknown_key_policy: "REJECT",
        defaulting_policy: "OMITTED_FIELDS_USE_BACKEND_DEFAULTS",
        import_paths: ["CONFIG_UPDATE control message for partial updates"],
        binding_hash:
          "sha256:1414141414141414141414141414141414141414141414141414141414141414"
      },
      reproducibility: {
        manifest_id: "leo_twin.runtime_reproducibility_manifest.v1",
        manifest_hash:
          "sha256:2222222222222222222222222222222222222222222222222222222222222222",
        control_config_hash:
          "sha256:3333333333333333333333333333333333333333333333333333333333333333",
        generated_config_hash:
          "sha256:4444444444444444444444444444444444444444444444444444444444444444",
        runtime_state_hash:
          "sha256:5555555555555555555555555555555555555555555555555555555555555555",
        metrics_summary_hash:
          "sha256:6666666666666666666666666666666666666666666666666666666666666666",
        runtime_export_boundary_hash:
          "sha256:7777777777777777777777777777777777777777777777777777777777777777"
      },
      review_summary: {
        summary_id: "leo_twin.runtime_export_review_summary.v1",
        summary_hash:
          "sha256:8888888888888888888888888888888888888888888888888888888888888888",
        review_status: "REVIEW_READY"
      },
      diagnostics: {
        bundle_id: "leo_twin.runtime_export_diagnostics_bundle.v1",
        diagnostics_hash:
          "sha256:9999999999999999999999999999999999999999999999999999999999999999",
        finding_count: 1,
        finding_labels: [{ severity: "INFO", code: "RESULT_PACKAGE_REVIEW_READY" }]
      },
      network_kpi_formula_evidence: {
        evidence_id: "leo_twin.network_kpi_formula_evidence.v1",
        metric_model: "FLOW_LEVEL_PROXY",
        formula_evidence_status: "FORMULA_AND_TIME_EVIDENCE_READY",
        kpi_count: 6,
        observed_kpi_count: 6,
        missing_selected_input_count: 0,
        time_varying_kpi_count: 4,
        evidence_hash:
          "sha256:edededededededededededededededededededededededededededededededed",
        evidence_present: true
      },
      network_kpi_variation_explanation: {
        explanation_id: "leo_twin.network_kpi_variation_explanation.v1",
        metric_model: "FLOW_LEVEL_PROXY",
        explanation_status: "TIME_VARIATION_EXPLAINED",
        sample_count: 4,
        kpi_count: 6,
        time_varying_kpi_count: 4,
        flat_kpi_count: 2,
        missing_explanation_count: 0,
        evidence_hash:
          "sha256:eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
        evidence_present: true
      },
      user_configuration_template_validation: {
        evidence_id: "sees.user_configuration_template_validation.v1",
        schema_id: "sees.user_configuration.v2",
        validation_status: "ALL_TEMPLATES_VALID",
        template_count: 3,
        valid_template_count: 3,
        invalid_template_count: 0,
        all_templates_valid: true,
        template_evidence_hash:
          "sha256:fdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfd",
        evidence_hash:
          "sha256:fefefefefefefefefefefefefefefefefefefefefefefefefefefefefefe",
        evidence_present: true
      },
      traffic_demand_explanation: {
        evidence_id: "leo_twin.traffic_demand_explanation.v1",
        request_count: 20,
        compute_service_request_count: 8,
        traffic_class_row_count: 2,
        per_user_state_count: 20,
        frontend_inference_required: false,
        packet_level_simulation: false,
        evidence_hash:
          "sha256:7878787878787878787878787878787878787878787878787878787878787878",
        evidence_present: true
      },
      user_service_requests: {
        evidence_id: "leo_twin.user_service_request_export_evidence.v2",
        request_model: "FLOW_LEVEL_USER_SERVICE_REQUEST_PROXY",
        request_count: 20,
        exported_request_count: 18,
        hidden_request_count: 2,
        compute_request_count: 8,
        network_waiting_request_count: 3,
        summary_hash:
          "sha256:abababababababababababababababababababababababababababababababab",
        evidence_present: true
      },
      audit_index: {
        audit_index_id: "leo_twin.runtime_export_package_audit_index.v1",
        filename: "export_package_audit_index_v1.json",
        hash_binding_direction:
          "audit index records this scenario_review_bundle_v1.json file hash"
      },
      artifact_review: {
        artifact_count: 10,
        artifact_filenames: [
          "scenario_review_bundle_v1.json",
          "export_package_audit_index_v1.json",
          "review_summary_v1.json",
          "diagnostics_bundle_v1.json",
          "manifest.json",
          "config_snapshot.json",
          "route_detail_index_v1.json",
          "service_lifecycle_trace_v2.json",
          "service_trace_comparison_review_report_v1.json",
          "network_kpi_formula_evidence_v1.json",
          "network_kpi_variation_explanation_v1.json",
          "user_configuration_template_validation_v1.json",
          "traffic_demand_explanation_v1.json",
          "user_service_request_summary_v2.json",
          "events.jsonl",
          "metrics.csv"
        ],
        entrypoint_filenames: ["scenario_review_bundle_v1.json"]
      },
      model_boundaries: {
        event_kernel_policy: "NO_EVENT_KERNEL_BEHAVIOR_CHANGE",
        event_replay_restore: false,
        model_recomputation: false,
        route_recomputation: false,
        service_recomputation: false,
        packet_capture: false,
        packet_level_simulation: false,
        external_simulators: false,
        forbidden_external_integrations: ["STK", "EXATA", "AFSIM", "DDS"]
      },
      recommended_review_order: [
        "scenario_review_bundle_v1.json",
        "export_package_audit_index_v1.json",
        "review_summary_v1.json",
        "diagnostics_bundle_v1.json",
        "manifest.json",
        "config_snapshot.json",
        "route_detail_index_v1.json",
        "service_lifecycle_trace_v2.json",
        "service_trace_comparison_review_report_v1.json",
        "network_kpi_formula_evidence_v1.json",
        "network_kpi_variation_explanation_v1.json",
        "user_configuration_template_validation_v1.json",
        "traffic_demand_explanation_v1.json",
        "user_service_request_summary_v2.json",
        "events.jsonl",
        "metrics.csv",
        "summary.json"
      ],
      scenario_review_status: "SCENARIO_REVIEW_READY",
      scenario_review_warnings: [],
      scenario_review_hash:
        "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    };

    const display = buildDataPanelExportScenarioReviewBundleDisplay(bundle);

    expect(display).toEqual({
      packageId: "pkg-review",
      tone: "match",
      statusLabel: "scenario review ready",
      summaryLabel:
        "pkg-review / SCENARIO_REVIEW_READY / review aaaaaaaaaaaa",
      bundleHref:
        "/runtime/export/packages/pkg-review/files/scenario_review_bundle_v1.json",
      scenarioLabels: [
        "satellites 72",
        "users 20",
        "compute 12",
        "duration 120 s",
        "sim 120 s"
      ],
      configurationLabels: [
        "schema sees.user_configuration.v2",
        "config 121212121212",
        "binding 141414141414",
        "validation ok"
      ],
      evidenceLabels: [
        "manifest 222222222222",
        "boundary 777777777777",
        "review 888888888888",
        "diagnostics 999999999999",
        "KPI formula FORMULA_AND_TIME_EVIDENCE_READY",
        "KPI formula edededededed",
        "KPI variation TIME_VARIATION_EXPLAINED",
        "KPI variation moving 4",
        "KPI variation eeeeeeeeeeee",
        "config templates ALL_TEMPLATES_VALID",
        "config templates valid 3 / 3",
        "config template fefefefefefe",
        "traffic requests 20",
        "traffic compute 8",
        "traffic demand 787878787878",
        "user services 18 / 20",
        "user services abababababab",
        "audit export_package_audit_index_v1.json"
      ],
      boundaryLabels: [
        "event kernel NO_EVENT_KERNEL_BEHAVIOR_CHANGE",
        "event replay no",
        "recompute no",
        "packet no",
        "external no"
      ],
      workflowRows: [
        {
          stepLabel: "1 scenario entry",
          statusLabel: "available",
          detailLabel: "scenario_review_bundle_v1.json",
          href:
            "/runtime/export/packages/pkg-review/files/scenario_review_bundle_v1.json",
          title:
            "1 scenario entry / scenario_review_bundle_v1.json / package artifact available",
          tone: "match"
        },
        {
          stepLabel: "2 audit index",
          statusLabel: "available",
          detailLabel: "export_package_audit_index_v1.json",
          href:
            "/runtime/export/packages/pkg-review/files/export_package_audit_index_v1.json",
          title:
            "2 audit index / export_package_audit_index_v1.json / package artifact available",
          tone: "match"
        },
        {
          stepLabel: "3 review summary",
          statusLabel: "available",
          detailLabel: "review_summary_v1.json",
          href:
            "/runtime/export/packages/pkg-review/files/review_summary_v1.json",
          title:
            "3 review summary / review_summary_v1.json / package artifact available",
          tone: "match"
        },
        {
          stepLabel: "4 diagnostics",
          statusLabel: "available",
          detailLabel: "diagnostics_bundle_v1.json",
          href:
            "/runtime/export/packages/pkg-review/files/diagnostics_bundle_v1.json",
          title:
            "4 diagnostics / diagnostics_bundle_v1.json / package artifact available",
          tone: "match"
        },
        {
          stepLabel: "5 manifest",
          statusLabel: "available",
          detailLabel: "manifest.json",
          href: "/runtime/export/packages/pkg-review/files/manifest.json",
          title: "5 manifest / manifest.json / package artifact available",
          tone: "match"
        },
        {
          stepLabel: "6 configuration",
          statusLabel: "available",
          detailLabel: "config_snapshot.json",
          href: "/runtime/export/packages/pkg-review/files/config_snapshot.json",
          title:
            "6 configuration / config_snapshot.json / package artifact available",
          tone: "match"
        },
        {
          stepLabel: "7 route evidence",
          statusLabel: "available",
          detailLabel: "route_detail_index_v1.json",
          href:
            "/runtime/export/packages/pkg-review/files/route_detail_index_v1.json",
          title:
            "7 route evidence / route_detail_index_v1.json / package artifact available",
          tone: "match"
        },
        {
          stepLabel: "8 service trace",
          statusLabel: "available",
          detailLabel: "service_lifecycle_trace_v2.json",
          href:
            "/runtime/export/packages/pkg-review/files/service_lifecycle_trace_v2.json",
          title:
            "8 service trace / service_lifecycle_trace_v2.json / package artifact available",
          tone: "match"
        },
        {
          stepLabel: "9 service trace review",
          statusLabel: "available",
          detailLabel: "service_trace_comparison_review_report_v1.json",
          href:
            "/runtime/export/packages/pkg-review/files/service_trace_comparison_review_report_v1.json",
          title:
            "9 service trace review / service_trace_comparison_review_report_v1.json / package artifact available",
          tone: "match"
        },
        {
          stepLabel: "10 KPI formula evidence",
          statusLabel: "available",
          detailLabel: "network_kpi_formula_evidence_v1.json",
          href:
            "/runtime/export/packages/pkg-review/files/network_kpi_formula_evidence_v1.json",
          title:
            "10 KPI formula evidence / network_kpi_formula_evidence_v1.json / package artifact available",
          tone: "match"
        },
        {
          stepLabel: "11 KPI variation explanation",
          statusLabel: "available",
          detailLabel: "network_kpi_variation_explanation_v1.json",
          href:
            "/runtime/export/packages/pkg-review/files/network_kpi_variation_explanation_v1.json",
          title:
            "11 KPI variation explanation / network_kpi_variation_explanation_v1.json / package artifact available",
          tone: "match"
        },
        {
          stepLabel: "12 config template validation",
          statusLabel: "available",
          detailLabel: "user_configuration_template_validation_v1.json",
          href:
            "/runtime/export/packages/pkg-review/files/user_configuration_template_validation_v1.json",
          title:
            "12 config template validation / user_configuration_template_validation_v1.json / package artifact available",
          tone: "match"
        },
        {
          stepLabel: "13 traffic demand",
          statusLabel: "available",
          detailLabel: "traffic_demand_explanation_v1.json",
          href:
            "/runtime/export/packages/pkg-review/files/traffic_demand_explanation_v1.json",
          title:
            "13 traffic demand / traffic_demand_explanation_v1.json / package artifact available",
          tone: "match"
        },
        {
          stepLabel: "14 user services",
          statusLabel: "available",
          detailLabel: "user_service_request_summary_v2.json",
          href:
            "/runtime/export/packages/pkg-review/files/user_service_request_summary_v2.json",
          title:
            "14 user services / user_service_request_summary_v2.json / package artifact available",
          tone: "match"
        },
        {
          stepLabel: "15 event evidence",
          statusLabel: "available",
          detailLabel: "events.jsonl",
          href: "/runtime/export/packages/pkg-review/files/events.jsonl",
          title: "15 event evidence / events.jsonl / package artifact available",
          tone: "match"
        },
        {
          stepLabel: "16 metrics",
          statusLabel: "available",
          detailLabel: "metrics.csv",
          href: "/runtime/export/packages/pkg-review/files/metrics.csv",
          title: "16 metrics / metrics.csv / package artifact available",
          tone: "match"
        },
        {
          stepLabel: "17 summary",
          statusLabel: "missing",
          detailLabel: "summary.json",
          href: null,
          title:
            "17 summary / summary.json / not listed in scenario review bundle",
          tone: "different"
        }
      ],
      warningLabels: []
    });
    expect(
      buildDataPanelExportScenarioReviewBundleStatus(display, "pkg-review")
    ).toMatchObject({
      tone: "match",
      bundleHref:
        "/runtime/export/packages/pkg-review/files/scenario_review_bundle_v1.json"
    });
    expect(
      buildDataPanelExportScenarioReviewBundleStatus(null, "pkg-review", true)
    ).toMatchObject({
      tone: "pending",
      statusLabel: "loading scenario review"
    });
    expect(
      buildDataPanelExportScenarioReviewBundleStatus(
        null,
        "pkg-review",
        false,
        "scenario review failed"
      )
    ).toMatchObject({
      tone: "error",
      warningLabels: ["scenario review failed"]
    });
  });

  it("builds scenario review checklist drafts and save payloads", () => {
    const bundle = {
      type: "RUNTIME_EXPORT_SCENARIO_REVIEW_BUNDLE_V1",
      version: "v1",
      bundle_id: "leo_twin.runtime_export_scenario_review_bundle.v1",
      source: "BACKEND_RUNTIME_EXPORT_PACKAGE",
      review_scope: "USER_CONFIGURATION_TO_RESULT_PACKAGE_REVIEW",
      package_id: "pkg-review",
      package_dir: "artifacts/runtime_exports/pkg-review",
      scenario: {
        seed: 7,
        satellite_count: 72,
        user_count: 20,
        compute_node_count: 12,
        duration_seconds: 120
      },
      runtime: {
        lifecycle_state: "STOPPED",
        current_sim_time: 120,
        processed_event_count: 4200,
        queued_event_count: 0
      },
      user_configuration: {
        type: "USER_CONFIGURATION_AUDIT_BINDING_V1",
        version: "v1",
        binding_id: "leo_twin.user_configuration_audit_binding.v1",
        source: "BACKEND_RUNTIME_EXPORT_PACKAGE",
        schema_id: "sees.user_configuration.v2",
        export_scope: "CURRENT_EFFECTIVE_SEES_CONFIG",
        format: "JSON_MAPPING",
        config_hash: "sha256:config",
        export_hash: "sha256:export",
        validation_ok: true,
        validation_error_count: 0,
        unknown_key_policy: "REJECT",
        defaulting_policy: "OMITTED_FIELDS_USE_BACKEND_DEFAULTS",
        import_paths: [],
        binding_hash: "sha256:binding"
      },
      reproducibility: {
        manifest_id: "leo_twin.runtime_reproducibility_manifest.v1",
        manifest_hash: "sha256:manifest",
        control_config_hash: "sha256:control",
        generated_config_hash: "sha256:generated",
        runtime_state_hash: "sha256:runtime",
        metrics_summary_hash: "sha256:metrics",
        runtime_export_boundary_hash: "sha256:boundary"
      },
      review_summary: {
        summary_id: "leo_twin.runtime_export_review_summary.v1",
        summary_hash: "sha256:review",
        review_status: "REVIEW_READY"
      },
      diagnostics: {
        bundle_id: "leo_twin.runtime_export_diagnostics_bundle.v1",
        diagnostics_hash: "sha256:diagnostics",
        finding_count: 0,
        finding_labels: []
      },
      audit_index: {
        audit_index_id: "leo_twin.runtime_export_package_audit_index.v1",
        filename: "export_package_audit_index_v1.json",
        hash_binding_direction:
          "audit index records this scenario_review_bundle_v1.json file hash"
      },
      artifact_review: {
        artifact_count: 3,
        artifact_filenames: [
          "scenario_review_bundle_v1.json",
          "export_package_audit_index_v1.json",
          "review_summary_v1.json"
        ],
        entrypoint_filenames: ["scenario_review_bundle_v1.json"]
      },
      model_boundaries: {
        event_kernel_policy: "NO_EVENT_KERNEL_BEHAVIOR_CHANGE",
        event_replay_restore: false,
        model_recomputation: false,
        route_recomputation: false,
        service_recomputation: false,
        packet_capture: false,
        packet_level_simulation: false,
        external_simulators: false,
        forbidden_external_integrations: ["STK", "EXATA", "AFSIM", "DDS"]
      },
      recommended_review_order: [
        "scenario_review_bundle_v1.json",
        "export_package_audit_index_v1.json",
        "review_summary_v1.json"
      ],
      scenario_review_status: "SCENARIO_REVIEW_READY",
      scenario_review_warnings: [],
      scenario_review_hash: "sha256:scenario-review"
    };
    const checklist = {
      type: "RUNTIME_EXPORT_SCENARIO_REVIEW_CHECKLIST_V1",
      version: "v1",
      checklist_id: "leo_twin.runtime_export_scenario_review_checklist.v1",
      source: "OPERATOR_SCENARIO_REVIEW_CHECKLIST",
      checklist_scope: "SCENARIO_REVIEW_BUNDLE_OPERATOR_DECISIONS",
      package_id: "pkg-review",
      package_dir: "artifacts/runtime_exports/pkg-review",
      scenario_review_bundle_id:
        "leo_twin.runtime_export_scenario_review_bundle.v1",
      scenario_review_hash: "sha256:scenario-review",
      record_count: 1,
      reviewed_count: 1,
      skipped_count: 0,
      followup_count: 0,
      error_count: 0,
      submitted_records_complete: true,
      expected_review_count: 1,
      reviewed_recommended_count: 1,
      missing_recommended_review_count: 0,
      attention_recommended_review_count: 0,
      missing_recommended_review_filenames: [],
      attention_recommended_review_filenames: [],
      recommended_review_complete: true,
      recommended_review_status: "RECOMMENDED_REVIEW_COMPLETE",
      checklist_status: "CHECKLIST_COMPLETE",
      records: [
        {
          artifact_filename: "scenario_review_bundle_v1.json",
          step_label: "1 scenario entry",
          review_status: "REVIEWED",
          status_reason: "",
          operator_note: "checked scenario evidence",
          evidence_hash: "sha256:scenario-review",
          review_order_index: 0,
          record_hash: "sha256:record"
        }
      ],
      ordering: "recommended_review_order ascending",
      boundary_conditions: ["NO_EVENT_REPLAY"],
      checklist_hash: "sha256:checklist"
    };
    const display = buildDataPanelExportScenarioReviewBundleDisplay(bundle as any);
    const draft = buildDataPanelScenarioReviewChecklistDraft(
      bundle as any,
      checklist as any
    );

    expect(draft["scenario_review_bundle_v1.json"]).toEqual({
      reviewStatus: "REVIEWED",
      operatorNote: "checked scenario evidence"
    });
    expect(draft["export_package_audit_index_v1.json"]).toEqual({
      reviewStatus: "REVIEWED",
      operatorNote: ""
    });
    const template = {
      type: "RUNTIME_EXPORT_SCENARIO_REVIEW_CHECKLIST_TEMPLATE_V1",
      version: "v1",
      template_id:
        "leo_twin.runtime_export_scenario_review_checklist_template.v1",
      source: "BACKEND_RUNTIME_EXPORT_PACKAGE",
      template_scope: "SCENARIO_REVIEW_RECOMMENDED_STEPS_OPERATOR_TEMPLATE",
      package_id: "pkg-review",
      package_dir: "artifacts/runtime_exports/pkg-review",
      scenario_review_bundle_id:
        "leo_twin.runtime_export_scenario_review_bundle.v1",
      scenario_review_hash: "sha256:scenario-review",
      audit_hash: "sha256:audit",
      expected_review_filenames: [
        "scenario_review_bundle_v1.json",
        "export_package_audit_index_v1.json"
      ],
      expected_review_count: 2,
      evidence_present_count: 2,
      missing_evidence_filenames: [],
      missing_evidence_count: 0,
      template_status: "TEMPLATE_READY",
      records: [
        {
          artifact_filename: "export_package_audit_index_v1.json",
          step_label: "2 audit index",
          review_status: "NEEDS_FOLLOWUP",
          status_reason: "OPERATOR_REVIEW_REQUIRED",
          operator_note: "",
          evidence_hash: "sha256:backend-audit",
          evidence_present: true,
          evidence_source: "BACKEND_REVIEW_EVIDENCE_HASH",
          review_order_index: 1,
          template_record_hash: "sha256:template-record"
        }
      ],
      record_policy: "template records prefill evidence",
      boundary_conditions: ["NO_EVENT_REPLAY"],
      template_hash: "sha256:template"
    };
    const templateDraft = buildDataPanelScenarioReviewChecklistDraft(
      bundle as any,
      null,
      template as any
    );
    expect(templateDraft["export_package_audit_index_v1.json"]).toEqual({
      reviewStatus: "NEEDS_FOLLOWUP",
      operatorNote: ""
    });
    expect(
      buildDataPanelExportScenarioReviewChecklistStatus(checklist as any)
    ).toMatchObject({
      tone: "match",
      statusLabel: "审核清单已完成",
      summaryLabel:
        "CHECKLIST_COMPLETE / records 1 / recommended 1/1 / checklist checklist",
      warningLabels: []
    });
    expect(
      buildDataPanelExportScenarioReviewChecklistStatus({
        ...checklist,
        expected_review_count: 3,
        reviewed_recommended_count: 1,
        missing_recommended_review_filenames: [
          "export_package_audit_index_v1.json",
          "service_trace_comparison_review_report_v1.json"
        ],
        missing_recommended_review_count: 2,
        recommended_review_complete: false,
        recommended_review_status: "RECOMMENDED_REVIEW_INCOMPLETE"
      } as any)
    ).toMatchObject({
      tone: "different",
      summaryLabel:
        "CHECKLIST_COMPLETE / records 1 / recommended 1/3 / checklist checklist",
      warningLabels: [
        "RECOMMENDED_REVIEW_INCOMPLETE",
        "missing export_package_audit_index_v1.json",
        "missing service_trace_comparison_review_report_v1.json"
      ]
    });
    expect(
      buildDataPanelExportScenarioReviewChecklistTemplateComparisonStatus({
        type: "RUNTIME_EXPORT_SCENARIO_REVIEW_CHECKLIST_TEMPLATE_COMPARISON_V1",
        version: "v1",
        comparison_id:
          "leo_twin.runtime_export_scenario_review_checklist_template_comparison.v1",
        source: "BACKEND_RUNTIME_EXPORT_PACKAGE",
        comparison_scope: "SAVED_CHECKLIST_VS_LATEST_BACKEND_TEMPLATE",
        package_id: "pkg-review",
        package_dir: "artifacts/runtime_exports/pkg-review",
        scenario_review_hash: "sha256:scenario-review",
        template_hash: "sha256:template",
        template_status: "TEMPLATE_READY",
        checklist_present: true,
        checklist_hash: "sha256:checklist",
        checklist_status: "CHECKLIST_COMPLETE",
        comparison_status: "DRIFT",
        template_record_count: 2,
        checklist_record_count: 2,
        aligned_record_count: 1,
        missing_checklist_record_count: 0,
        evidence_hash_mismatch_count: 1,
        operator_attention_count: 0,
        extra_checklist_record_count: 1,
        records: [
          {
            artifact_filename: "scenario_review_bundle_v1.json",
            step_label: "1 scenario entry",
            review_order_index: 0,
            template_evidence_hash: "sha256:scenario-review",
            template_record_hash: "sha256:template-record-a",
            checklist_evidence_hash: "sha256:scenario-review",
            checklist_record_hash: "sha256:checklist-record-a",
            checklist_review_status: "REVIEWED",
            comparison_status: "ALIGNED",
            issue_labels: [],
            comparison_record_hash: "sha256:comparison-record-a"
          },
          {
            artifact_filename: "export_package_audit_index_v1.json",
            step_label: "2 audit index",
            review_order_index: 1,
            template_evidence_hash: "sha256:audit-new",
            template_record_hash: "sha256:template-record-b",
            checklist_evidence_hash: "sha256:audit-old",
            checklist_record_hash: "sha256:checklist-record-b",
            checklist_review_status: "REVIEWED",
            comparison_status: "DRIFT",
            issue_labels: ["EVIDENCE_HASH_MISMATCH"],
            comparison_record_hash: "sha256:comparison-record-b"
          }
        ],
        extra_records: [
          {
            artifact_filename: "old_artifact.json",
            step_label: "old artifact",
            review_order_index: 99,
            checklist_evidence_hash: "sha256:old",
            checklist_record_hash: "sha256:old-record",
            checklist_review_status: "REVIEWED",
            comparison_status: "EXTRA",
            issue_labels: ["EXTRA_CHECKLIST_RECORD"],
            comparison_record_hash: "sha256:extra-record"
          }
        ],
        boundary_conditions: ["NO_EVENT_REPLAY"],
        comparison_hash: "sha256:comparison"
      } as any)
    ).toMatchObject({
      tone: "different",
      statusLabel: "template drift detected",
      summaryLabel: "DRIFT / aligned 1/2 / compare comparison",
      evidenceLabels: [
        "template template",
        "checklist checklist",
        "missing 0",
        "drift 1",
        "attention 0",
        "extra 1"
      ],
      warningLabels: [
        "DRIFT",
        "export_package_audit_index_v1.json: EVIDENCE_HASH_MISMATCH",
        "old_artifact.json: EXTRA_CHECKLIST_RECORD"
      ]
    });
    const request = buildDataPanelScenarioReviewChecklistSaveRequest(
      bundle as any,
      display?.workflowRows.slice(0, 3) ?? [],
      draft,
      { audit_hash: "sha256:audit" } as any
    );

    expect(request).toMatchObject({
      packageId: "pkg-review",
      records: [
        {
          artifact_filename: "scenario_review_bundle_v1.json",
          review_status: "REVIEWED",
          operator_note: "checked scenario evidence",
          evidence_hash: "sha256:scenario-review"
        },
        {
          artifact_filename: "export_package_audit_index_v1.json",
          review_status: "REVIEWED",
          evidence_hash: "sha256:audit"
        },
        {
          artifact_filename: "review_summary_v1.json",
          review_status: "REVIEWED",
          evidence_hash: "sha256:review"
        }
      ]
    });
    const templateRequest = buildDataPanelScenarioReviewChecklistSaveRequest(
      bundle as any,
      display?.workflowRows.slice(1, 2) ?? [],
      templateDraft,
      { audit_hash: "sha256:audit" } as any,
      template as any
    );
    expect(templateRequest).toMatchObject({
      packageId: "pkg-review",
      records: [
        {
          artifact_filename: "export_package_audit_index_v1.json",
          step_label: "2 audit index",
          review_status: "NEEDS_FOLLOWUP",
          status_reason: "OPERATOR_REVIEW_REQUIRED",
          evidence_hash: "sha256:backend-audit"
        }
      ]
    });
    const auditBackedDisplay = buildDataPanelExportScenarioReviewBundleDisplay(
      bundle as any,
      {
        audit_hash: "sha256:audit",
        service_trace_comparison_review_report_present: true,
        service_trace_comparison_review_report_hash: "sha256:trace-report"
      } as any
    );
    const auditBackedDraft = updateDataPanelScenarioReviewChecklistDraft(
      draft,
      "service_trace_comparison_review_report_v1.json",
      {
        reviewStatus: "REVIEWED",
        operatorNote: "trace review checked"
      }
    );
    const serviceTraceReviewRequest =
      buildDataPanelScenarioReviewChecklistSaveRequest(
        bundle as any,
        (auditBackedDisplay?.workflowRows ?? []).filter(
          (row) =>
            row.detailLabel === "service_trace_comparison_review_report_v1.json"
        ),
        auditBackedDraft,
        {
          audit_hash: "sha256:audit",
          service_trace_comparison_review_report_present: true,
          service_trace_comparison_review_report_hash: "sha256:trace-report"
        } as any
      );
    expect(serviceTraceReviewRequest).toMatchObject({
      packageId: "pkg-review",
      records: [
        {
          artifact_filename: "service_trace_comparison_review_report_v1.json",
          step_label: "9 service trace review",
          review_status: "REVIEWED",
          operator_note: "trace review checked",
          status_reason: "",
          evidence_hash: "sha256:trace-report"
        }
      ]
    });
  });

  it("summarizes package review completion evidence", () => {
    const auditIndex = {
      type: "RUNTIME_EXPORT_PACKAGE_AUDIT_INDEX_V1",
      version: "v1",
      audit_index_id: "leo_twin.runtime_export_package_audit_index.v1",
      source: "BACKEND_RUNTIME_EXPORT_PACKAGE",
      audit_scope: "RESULT_PACKAGE_LONG_TERM_AUDIT_INDEX",
      package_id: "pkg-review",
      package_dir: "artifacts/runtime_exports/pkg-review",
      manifest_hash: "sha256:manifest",
      control_config_hash: "sha256:control",
      generated_config_hash: "sha256:generated",
      runtime_state_hash: "sha256:runtime",
      runtime_export_boundary_hash: "sha256:boundary",
      boundary_alignment_hash: "sha256:alignment",
      boundary_alignment_status: "ALIGNED",
      boundary_alignment_warnings: [],
      review_summary_hash: "sha256:review",
      diagnostics_hash: "sha256:diagnostics",
      route_comparison_review_report_hash: "sha256:route-report",
      route_comparison_review_report_present: true,
      service_trace_comparison_review_report_hash: "sha256:trace-report",
      service_trace_comparison_review_report_present: true,
      service_trace_comparison_review_record_count: 1,
      service_trace_comparison_review_error_count: 0,
      scenario_review_checklist_hash: "sha256:checklist",
      scenario_review_checklist_present: true,
      scenario_review_checklist_record_count: 2,
      scenario_review_checklist_status: "CHECKLIST_COMPLETE",
      scenario_review_checklist_recommended_review_complete: true,
      scenario_review_checklist_recommended_review_status:
        "RECOMMENDED_REVIEW_COMPLETE",
      scenario_review_checklist_expected_review_count: 2,
      scenario_review_checklist_reviewed_recommended_count: 2,
      scenario_review_checklist_missing_recommended_review_count: 0,
      scenario_review_checklist_attention_recommended_review_count: 0,
      artifact_count: 2,
      artifact_hashes: [],
      required_artifact_filenames: [],
      missing_required_artifact_filenames: [],
      self_artifact_excluded_from_hashes: true,
      audit_status: "AUDIT_READY",
      audit_warnings: [],
      forbidden_external_integrations: ["STK", "EXATA", "AFSIM", "DDS"],
      packet_level_simulation: false,
      event_replay_restore: false,
      model_recomputation: false,
      package_mutation_on_read: false,
      audit_hash: "sha256:audit"
    };
    const routeReport = {
      type: "RUNTIME_EXPORT_ROUTE_COMPARISON_REVIEW_REPORT_V1",
      version: "v1",
      report_id: "leo_twin.runtime_export_route_comparison_review_report.v1",
      source: "OPERATOR_ROUTE_COMPARISON_REVIEW",
      report_scope: "SELECTED_PACKAGE_VS_LIVE_ROUTE_COMPARISON_OUTCOMES",
      package_id: "pkg-review",
      package_dir: "artifacts/runtime_exports/pkg-review",
      route_comparison_review: _runtimeExportRouteComparisonReview(),
      record_count: 1,
      match_count: 1,
      different_count: 0,
      unavailable_count: 0,
      error_count: 0,
      records: [],
      ordering: "route_id ascending",
      boundary_conditions: ["NO_ROUTE_RECOMPUTE"],
      report_hash: "sha256:route-report"
    };
    const scenarioReviewBundle = {
      scenario_review_status: "SCENARIO_REVIEW_READY",
      scenario_review_warnings: []
    };
    const checklist = {
      checklist_status: "CHECKLIST_COMPLETE",
      record_count: 2,
      submitted_records_complete: true,
      expected_review_count: 2,
      reviewed_recommended_count: 2,
      recommended_review_complete: true,
      checklist_hash: "sha256:checklist"
    };

    expect(
      buildDataPanelExportReviewCompletionSummary({
        auditIndex: auditIndex as any,
        routeReport: routeReport as any,
        scenarioReviewBundle: scenarioReviewBundle as any,
        scenarioReviewChecklist: checklist as any
      })
    ).toEqual({
      tone: "match",
      statusLabel: "review package complete",
      summaryLabel: "ready / audit AUDIT_READY / checklist CHECKLIST_COMPLETE",
      evidenceLabels: [
        "audit AUDIT_READY",
        "route report saved",
        "route records 1",
        "scenario SCENARIO_REVIEW_READY",
        "checklist CHECKLIST_COMPLETE",
        "checklist records 2",
        "checklist recommended 2/2"
      ],
      warningLabels: []
    });
    expect(
      buildDataPanelExportReviewCompletionSummary({
        auditIndex: {
          ...auditIndex,
          package_review_completion_v1: {
            type: "RUNTIME_EXPORT_PACKAGE_REVIEW_COMPLETION_V1",
            version: "v1",
            completion_id:
              "leo_twin.runtime_export_package_review_completion.v1",
            source: "BACKEND_RUNTIME_EXPORT_PACKAGE_AUDIT_INDEX",
            completion_scope: "RESULT_PACKAGE_OPERATOR_HANDOFF_READINESS",
            package_id: "pkg-review",
            package_dir: "artifacts/runtime_exports/pkg-review",
            completion_status: "REVIEW_COMPLETE",
            handoff_ready: true,
            audit_status: "AUDIT_READY",
            audit_warnings: [],
            route_comparison_review_report_present: true,
            route_comparison_review_report_hash: "sha256:route-report",
            route_comparison_review_record_count: 1,
            route_comparison_review_error_count: 0,
            service_trace_comparison_review_report_present: true,
            service_trace_comparison_review_report_hash: "sha256:trace-report",
            service_trace_comparison_review_record_count: 1,
            service_trace_comparison_review_error_count: 0,
            scenario_review_bundle_present: true,
            scenario_review_checklist_present: true,
            scenario_review_checklist_hash: "sha256:checklist",
            scenario_review_checklist_status: "CHECKLIST_COMPLETE",
            scenario_review_checklist_record_count: 2,
            review_summary_status: "REVIEW_READY",
            review_summary_hash: "sha256:review",
            diagnostics_error_count: 0,
            diagnostics_hash: "sha256:diagnostics",
            boundary_alignment_status: "ALIGNED",
            boundary_alignment_hash: "sha256:alignment",
            user_configuration_validation_ok: true,
            missing_or_warning_evidence: [],
            evidence_labels: ["backend completion evidence"],
            boundary_conditions: ["BACKEND_OWNED_HANDOFF_SUMMARY"],
            completion_hash: "sha256:backend-completion"
          }
        } as any,
        routeReport: null,
        scenarioReviewBundle: null,
        scenarioReviewChecklist: null
      })
    ).toMatchObject({
      tone: "match",
      statusLabel: "review package complete",
      summaryLabel:
        "REVIEW_COMPLETE / audit AUDIT_READY / completion backend-comp",
      evidenceLabels: [
        "backend completion evidence",
        "completion backend-comp"
      ],
      warningLabels: []
    });
    expect(
      buildDataPanelExportReviewCompletionSummary({
        auditIndex: {
          ...auditIndex,
          route_comparison_review_report_present: false
        } as any,
        routeReport: null,
        scenarioReviewBundle: scenarioReviewBundle as any,
        scenarioReviewChecklist: checklist as any
      })
    ).toMatchObject({
      tone: "different",
      statusLabel: "review package needs action",
      warningLabels: ["route comparison review report missing"]
    });
    expect(
      buildDataPanelExportReviewCompletionSummary({
        auditIndex: {
          ...auditIndex,
          scenario_review_checklist_status: "CHECKLIST_WARN"
        } as any,
        routeReport: routeReport as any,
        scenarioReviewBundle: scenarioReviewBundle as any,
        scenarioReviewChecklist: {
          ...checklist,
          checklist_status: "CHECKLIST_WARN"
        } as any
      })
    ).toMatchObject({
      tone: "different",
      warningLabels: ["scenario review checklist CHECKLIST_WARN"]
    });
  });

  it("summarizes backend-owned package acceptance reports", () => {
    expect(
      buildDataPanelExportAcceptanceReportStatus({
        type: "RUNTIME_EXPORT_PACKAGE_ACCEPTANCE_REPORT_V1",
        version: "v1",
        acceptance_id: "leo_twin.runtime_export_package_acceptance_report.v1",
        source: "BACKEND_RUNTIME_EXPORT_PACKAGE_AUDIT_INDEX",
        acceptance_scope: "INDUSTRIAL_V2_DEMO_CLOSED_LOOP_ACCEPTANCE",
        package_id: "pkg-review",
        package_dir: "artifacts/runtime_exports/pkg-review",
        acceptance_status: "WARN",
        demo_closed_loop_ready: true,
        handoff_ready: true,
        audit_status: "AUDIT_READY",
        completion_status: "REVIEW_COMPLETE",
        check_count: 2,
        pass_count: 1,
        warn_count: 1,
        fail_count: 0,
        checks: [
          {
            check_id: "review_completion",
            status: "PASS",
            summary: "REVIEW_COMPLETE",
            evidence_hash: "sha256:completion",
            evidence_labels: ["audit AUDIT_READY"],
            issue_labels: [],
            recommendation: "no action",
            check_hash: "sha256:check-pass"
          },
          {
            check_id: "service_trace_review",
            status: "WARN",
            summary: "service trace comparison review is optional but recommended",
            evidence_hash: "",
            evidence_labels: ["service_trace_report missing"],
            issue_labels: ["SERVICE_TRACE_REVIEW_OPTIONAL_MISSING"],
            recommendation:
              "save a service trace comparison review report for stronger handoff",
            check_hash: "sha256:check-warn"
          }
        ],
        operator_next_actions: [
          "save a service trace comparison review report for stronger handoff"
        ],
        evidence_hashes: [
          "audit sha256:audit",
          "completion sha256:completion",
          "manifest sha256:manifest"
        ],
        boundary_conditions: ["BACKEND_OWNED_ACCEPTANCE_SUMMARY"],
        acceptance_hash: "sha256:acceptance"
      } as any)
    ).toMatchObject({
      tone: "pending",
      statusLabel: "acceptance WARN",
      summaryLabel: "WARN / pass 1 / warn 1 / fail 0 / acceptance acceptance",
      evidenceLabels: [
        "closed loop ready",
        "handoff ready",
        "checks 2",
        "completion REVIEW_COMPLETE",
        "audit AUDIT_READY",
        "audit audit",
        "completion completion",
        "manifest manifest"
      ],
      benchmarkGate: null,
      warningLabels: [
        "service_trace_review: service trace comparison review is optional but recommended",
        "save a service trace comparison review report for stronger handoff"
      ]
    });
    expect(buildDataPanelExportAcceptanceReportStatus(null)).toBeNull();
  });

  it("surfaces backend-owned benchmark gate evidence in package acceptance reports", () => {
    const display = buildDataPanelExportAcceptanceReportStatus(
      {
        type: "RUNTIME_EXPORT_PACKAGE_ACCEPTANCE_REPORT_V1",
        version: "v1",
        acceptance_id: "leo_twin.runtime_export_package_acceptance_report.v1",
        source: "BACKEND_RUNTIME_EXPORT_PACKAGE_AUDIT_INDEX",
        acceptance_scope: "INDUSTRIAL_V2_DEMO_CLOSED_LOOP_ACCEPTANCE",
        package_id: "pkg-standard",
        package_dir: "artifacts/runtime_exports/pkg-standard",
        acceptance_status: "PASS",
        demo_closed_loop_ready: true,
        handoff_ready: true,
        audit_status: "AUDIT_READY",
        completion_status: "REVIEW_COMPLETE",
        check_count: 1,
        pass_count: 1,
        warn_count: 0,
        fail_count: 0,
        checks: [
          {
            check_id: "benchmark_scenario_gate",
            status: "PASS",
            summary: "standard benchmark scenario accepted",
            evidence_hash: "sha256:benchmark",
            evidence_labels: ["scenario small_demo_72sat"],
            issue_labels: [],
            recommendation: "no action",
            check_hash: "sha256:benchmark-check"
          }
        ],
        operator_next_actions: [],
        evidence_hashes: ["benchmark sha256:benchmark"],
        boundary_conditions: ["BACKEND_OWNED_ACCEPTANCE_SUMMARY"],
        acceptance_hash: "sha256:acceptance"
      } as any,
      {
        benchmark_acceptance_binding_v1: {
          type: "RUNTIME_EXPORT_BENCHMARK_ACCEPTANCE_BINDING_V1",
          version: "v1",
          binding_id: "leo_twin.runtime_export_benchmark_acceptance_binding.v1",
          source: "BACKEND_RUNTIME_EXPORT_PACKAGE_AUDIT_INDEX",
          matrix_id: "leo_twin.benchmark_scenario_matrix.v1",
          binding_status: "BENCHMARK_MATCHED",
          check_status: "PASS",
          scenario_id: "small_demo_72sat",
          label: "72 satellite closed-loop demo",
          config_path: "configs/acceptance/small_demo_72sat.yaml",
          scale_tier: "small",
          matched_identity_metrics: [
            "satellite_count",
            "user_count",
            "compute_node_count",
            "runtime_duration_s",
            "orbit_update_interval_s",
            "plane_count"
          ],
          expected_range_results: [
            {
              metric: "event_count",
              status: "PASS",
              observed_value: 4096,
              minimum: 1,
              maximum: 100000,
              unit: "events",
              evidence_artifact_filename: "export_package_audit_index_v1.json",
              evidence_artifact_role: "benchmark_acceptance_audit_index",
              evidence_context_id: "benchmark.expected_range.event_count",
              evidence_context_label: "expected range metric event_count",
              evidence_json_pointer:
                "/benchmark_acceptance_binding_v1/expected_range_results",
              issue_labels: [],
              result_hash: "sha256:range"
            }
          ],
          fidelity_results: [
            {
              check_id: "orbit_update_mode",
              status: "PASS",
              expected: "PER_SATELLITE",
              actual: "PER_SATELLITE",
              evidence_artifact_filename: "config_snapshot.json",
              evidence_artifact_role: "runtime_config_snapshot_status",
              evidence_context_id: "fidelity_summary.orbit_update_mode",
              evidence_context_label: "fidelity summary orbit_update_mode",
              evidence_json_pointer: "/status/fidelity_summary/orbit_update_mode",
              issue_labels: [],
              result_hash: "sha256:fidelity"
            }
          ],
          runtime_status_results: [
            {
              check_id: "route_trust",
              status: "PASS",
              expected: "PASS",
              actual: "PASS",
              evidence_artifact_filename: "route_detail_index_v1.json",
              evidence_artifact_role: "route_trust_evidence",
              evidence_context_id: "route_provenance_trust_summary_v1",
              evidence_context_label: "route trust runtime status",
              evidence_json_pointer: "/route_trust",
              issue_labels: [],
              result_hash: "sha256:runtime"
            },
            {
              check_id: "runtime_status.network_kpi",
              status: "PASS",
              expected: "PASS",
              actual: "PASS",
              evidence_artifact_filename:
                "network_kpi_benchmark_validation_v1.json",
              evidence_artifact_role: "network_kpi_benchmark_validation",
              evidence_context_id: "network_kpi_benchmark_validation_v1",
              evidence_context_label: "network KPI benchmark validation",
              evidence_json_pointer: "/validation",
              issue_labels: [],
              result_hash: "sha256:kpi"
            }
          ],
          issue_labels: [],
          recommendation: "no action",
          binding_hash: "sha256:binding"
        }
      } as any
    );

    expect(display?.benchmarkGate).toMatchObject({
      tone: "match",
      statusLabel: "standard benchmark PASS",
      summaryLabel:
        "72 satellite closed-loop demo / small / BENCHMARK_MATCHED / binding",
      evidenceLabels: [
        "status PASS",
        "scenario small_demo_72sat",
        "matrix leo_twin.benchmark_scenario_matrix.v1",
        "config configs/acceptance/small_demo_72sat.yaml",
        "identity 6",
        "range 1 pass / 0 warn / 0 fail",
        "fidelity 1 pass / 0 warn / 0 fail",
        "runtime 2 pass / 0 warn / 0 fail",
        "binding binding",
        "check benchmark-ch"
      ],
      rows: [
        {
          tone: "match",
          groupLabel: "expected range",
          itemLabel: "event_count",
          statusLabel: "PASS",
          expectedLabel: "expected 1-100000 events",
          observedLabel: "observed 4096 events",
          issueLabel: "",
          hashLabel: "range",
          contextLabel:
            "expected range metric event_count / benchmark.expected_range.event_count",
          pointerLabel:
            "json /benchmark_acceptance_binding_v1/expected_range_results",
          artifactLabel: "export_package_audit_index_v1.json",
          artifactHref:
            "/runtime/export/packages/pkg-standard/files/export_package_audit_index_v1.json",
          artifactTitle:
            "export_package_audit_index_v1.json / benchmark_acceptance_audit_index contains the backend-owned evidence for this benchmark row."
        },
        {
          tone: "match",
          groupLabel: "fidelity",
          itemLabel: "orbit_update_mode",
          statusLabel: "PASS",
          expectedLabel: "expected PER_SATELLITE",
          observedLabel: "observed PER_SATELLITE",
          issueLabel: "",
          hashLabel: "fidelity",
          contextLabel:
            "fidelity summary orbit_update_mode / fidelity_summary.orbit_update_mode",
          pointerLabel: "json /status/fidelity_summary/orbit_update_mode",
          artifactLabel: "config_snapshot.json",
          artifactHref:
            "/runtime/export/packages/pkg-standard/files/config_snapshot.json",
          artifactTitle:
            "config_snapshot.json / runtime_config_snapshot_status contains the backend-owned evidence for this benchmark row."
        },
        {
          tone: "match",
          groupLabel: "runtime status",
          itemLabel: "route_trust",
          statusLabel: "PASS",
          expectedLabel: "expected PASS",
          observedLabel: "observed PASS",
          issueLabel: "",
          hashLabel: "runtime",
          contextLabel:
            "route trust runtime status / route_provenance_trust_summary_v1",
          pointerLabel: "json /route_trust",
          artifactLabel: "route_detail_index_v1.json",
          artifactHref:
            "/runtime/export/packages/pkg-standard/files/route_detail_index_v1.json",
          artifactTitle:
            "route_detail_index_v1.json / route_trust_evidence contains the backend-owned evidence for this benchmark row."
        },
        {
          tone: "match",
          groupLabel: "runtime status",
          itemLabel: "runtime_status.network_kpi",
          statusLabel: "PASS",
          expectedLabel: "expected PASS",
          observedLabel: "observed PASS",
          issueLabel: "",
          hashLabel: "kpi",
          contextLabel:
            "network KPI benchmark validation / network_kpi_benchmark_validation_v1",
          pointerLabel: "json /validation",
          artifactLabel: "network_kpi_benchmark_validation_v1.json",
          artifactHref:
            "/runtime/export/packages/pkg-standard/files/network_kpi_benchmark_validation_v1.json",
          artifactTitle:
            "network_kpi_benchmark_validation_v1.json / network_kpi_benchmark_validation contains the backend-owned evidence for this benchmark row."
        }
      ],
      warningLabels: []
    });

    expect(
      buildDataPanelBenchmarkEvidenceFocus(display?.benchmarkGate?.rows[3])
    ).toEqual({
      focusSourceLabel: "Benchmark evidence focus",
      tone: "match",
      statusLabel: "runtime status / runtime_status.network_kpi",
      summaryLabel: "PASS / kpi",
      metaLabels: [
        "network KPI benchmark validation / network_kpi_benchmark_validation_v1",
        "json /validation",
        "expected PASS",
        "observed PASS"
      ],
      jsonPointer: "/validation",
      defaultInspectorFilter: "/validation",
      artifactLabel: "network_kpi_benchmark_validation_v1.json",
      artifactHref:
        "/runtime/export/packages/pkg-standard/files/network_kpi_benchmark_validation_v1.json",
      artifactTitle:
        "network_kpi_benchmark_validation_v1.json / network_kpi_benchmark_validation contains the backend-owned evidence for this benchmark row."
    });
    expect(buildDataPanelBenchmarkEvidenceFocus(null)).toBeNull();
  });

  it("builds a read-only artifact pointer viewer from benchmark evidence focus", () => {
    const focus = buildDataPanelBenchmarkEvidenceFocus({
      tone: "different",
      groupLabel: "runtime status",
      itemLabel: "runtime_status.network_kpi",
      statusLabel: "FAIL",
      expectedLabel: "expected PASS",
      observedLabel: "observed FAIL",
      issueLabel: "benchmark KPI failed",
      hashLabel: "kpi",
      contextLabel: "network KPI benchmark validation / network_kpi",
      pointerLabel: "json /validation/checks/0/observed_value",
      jsonPointer: "/validation/checks/0/observed_value",
      artifactLabel: "network_kpi_benchmark_validation_v1.json",
      artifactHref:
        "/runtime/export/packages/pkg-standard/files/network_kpi_benchmark_validation_v1.json",
      artifactTitle:
        "network_kpi_benchmark_validation_v1.json contains benchmark evidence."
    });

    expect(
      buildDataPanelBenchmarkEvidenceArtifactViewerDisplay(
        focus,
        {
          validation: {
            checks: [
              {
                metric: "latency",
                observed_value: 96.5
              }
            ]
          }
        },
        false,
        null
      )
    ).toMatchObject({
      tone: "different",
      statusLabel: "pointer target resolved",
      summaryLabel:
        "network_kpi_benchmark_validation_v1.json / /validation/checks/0/observed_value",
      segmentLabels: expect.arrayContaining([
        "pointer /validation/checks/0/observed_value",
        "target number",
        "segment 1: validation",
        "segment 2: checks",
        "segment 3: 0",
        "segment 4: observed_value"
      ]),
      targetPreview: "96.5"
    });
    expect(
      buildDataPanelBenchmarkEvidenceArtifactViewerDisplay(
        focus,
        {
          validation: {
            checks: [
              {
                metric: "latency",
                observed_value: 96.5
              }
            ]
          }
        },
        false,
        null,
        "observed"
      )
    ).toMatchObject({
      inspectorEnabled: true,
      inspectorFilterLabel:
        "paths 5 shown / 5 matched / 6 scanned / selected pointer visible",
      inspectorRows: expect.arrayContaining([
        expect.objectContaining({
          pointer: "/validation/checks/0/observed_value",
          pointerLabel: "json /validation/checks/0/observed_value",
          selected: true,
          previewLabel: "96.5"
        }),
        expect.objectContaining({
          pointer: "",
          selected: false
        })
      ])
    });
  });

  it("builds deterministic artifact inspector rows with selected pointer priority", () => {
    const display = buildDataPanelJsonArtifactInspectorRows(
      {
        zeta: 1,
        alpha: {
          child: "selected",
          other: true
        },
        list: [{ child: "array" }]
      },
      "/alpha/child",
      "child",
      4
    );

    expect(display.summaryLabel).toBe(
      "paths 4 shown / 6 matched / 8 scanned / selected pointer visible"
    );
    expect(display.rows).toEqual([
      expect.objectContaining({
        pointer: "/alpha/child",
        selected: true,
        previewLabel: '"selected"'
      }),
      expect.objectContaining({
        pointer: "",
        selected: false
      }),
      expect.objectContaining({
        pointer: "/alpha",
        selected: false
      }),
      expect.objectContaining({
        pointer: "/list",
        selected: false
      })
    ]);
  });

  it("reports missing and escaped JSON pointer targets deterministically", () => {
    const escapedFocus = {
      focusSourceLabel: "Benchmark evidence focus",
      tone: "match" as const,
      statusLabel: "expected range / escaped",
      summaryLabel: "PASS / escaped",
      metaLabels: [],
      jsonPointer: "/a~1b/c~0d",
      defaultInspectorFilter: "",
      artifactLabel: "export_package_audit_index_v1.json",
      artifactHref:
        "/runtime/export/packages/pkg-standard/files/export_package_audit_index_v1.json",
      artifactTitle: "escaped pointer artifact"
    };

    expect(
      buildDataPanelBenchmarkEvidenceArtifactViewerDisplay(
        escapedFocus,
        {
          "a/b": {
            "c~d": "resolved"
          }
        },
        false,
        null
      )
    ).toMatchObject({
      statusLabel: "pointer target resolved",
      targetPreview: '"resolved"',
      segmentLabels: expect.arrayContaining(["segment 1: a/b", "segment 2: c~d"])
    });

    expect(
      buildDataPanelBenchmarkEvidenceArtifactViewerDisplay(
        { ...escapedFocus, jsonPointer: "/a~1b/missing" },
        {
          "a/b": {
            "c~d": "resolved"
          }
        },
        false,
        null
      )
    ).toMatchObject({
      tone: "different",
      statusLabel: "pointer target missing",
      targetPreview: "No JSON value was found at /a~1b/missing."
    });
  });

  it("keeps artifact pointer viewer read-only when no JSON preview is available", () => {
    const focus = {
      focusSourceLabel: "Benchmark evidence focus",
      tone: "match" as const,
      statusLabel: "acceptance / gate",
      summaryLabel: "PASS / hash",
      metaLabels: [],
      jsonPointer: null,
      defaultInspectorFilter: "",
      artifactLabel: "events.jsonl",
      artifactHref: "/runtime/export/packages/pkg-standard/files/events.jsonl",
      artifactTitle: "events artifact"
    };

    expect(
      buildDataPanelBenchmarkEvidenceArtifactViewerDisplay(
        focus,
        undefined,
        false,
        null
      )
    ).toMatchObject({
      tone: "pending",
      statusLabel: "json pointer not recorded",
      targetPreview: "No backend evidence_json_pointer was recorded for this row."
    });
    expect(
      buildDataPanelBenchmarkEvidenceArtifactViewerDisplay(
        { ...focus, jsonPointer: "/events/0" },
        undefined,
        false,
        null
      )
    ).toMatchObject({
      tone: "pending",
      statusLabel: "non-json artifact",
      targetPreview:
        "Pointer preview is available only for JSON result-package artifacts."
    });
  });

  it("builds a scenario review workflow inspector focus for config template validation artifacts", () => {
    const focus = buildDataPanelScenarioReviewWorkflowInspectorFocus("pkg-review", {
      stepLabel: "11 config template validation",
      statusLabel: "available",
      detailLabel: "user_configuration_template_validation_v1.json",
      href:
        "/runtime/export/packages/pkg-review/files/user_configuration_template_validation_v1.json",
      title:
        "11 config template validation / user_configuration_template_validation_v1.json / package artifact available",
      tone: "match"
    });

    expect(focus).toEqual({
      focusSourceLabel: "Scenario review workflow artifact focus",
      tone: "match",
      statusLabel:
        "11 config template validation / user_configuration_template_validation_v1.json",
      summaryLabel: "available / match",
      metaLabels: [
        "artifact user_configuration_template_validation_v1.json",
        "json /template_validation/templates",
        "workflow 11 config template validation",
        "11 config template validation / user_configuration_template_validation_v1.json / package artifact available",
        "read-only scenario review artifact"
      ],
      jsonPointer: "/template_validation/templates",
      defaultInspectorFilter: "template_validation",
      artifactLabel: "user_configuration_template_validation_v1.json",
      artifactHref:
        "/runtime/export/packages/pkg-review/files/user_configuration_template_validation_v1.json",
      artifactTitle:
        "user_configuration_template_validation_v1.json / /template_validation/templates / read-only package artifact"
    });
    expect(
      buildDataPanelBenchmarkEvidenceArtifactViewerDisplay(
        focus,
        {
          template_validation: {
            templates: [
              {
                id: "default-72",
                validation_ok: true
              }
            ]
          }
        },
        false,
        null
      )
    ).toMatchObject({
      tone: "match",
      statusLabel: "pointer target resolved",
      targetPreview:
        '[\n  {\n    "id": "default-72",\n    "validation_ok": true\n  }\n]',
      inspectorEnabled: true
    });
    const trafficFocus = buildDataPanelScenarioReviewWorkflowInspectorFocus(
      "pkg-review",
      {
        stepLabel: "12 traffic demand",
        statusLabel: "available",
        detailLabel: "traffic_demand_explanation_v1.json",
        href:
          "/runtime/export/packages/pkg-review/files/traffic_demand_explanation_v1.json",
        title:
          "12 traffic demand / traffic_demand_explanation_v1.json / package artifact available",
        tone: "match"
      }
    );
    expect(trafficFocus).toMatchObject({
      focusSourceLabel: "Scenario review workflow artifact focus",
      statusLabel: "12 traffic demand / traffic_demand_explanation_v1.json",
      jsonPointer: "/traffic_demand_explanation",
      defaultInspectorFilter: "traffic_demand_explanation",
      artifactLabel: "traffic_demand_explanation_v1.json",
      artifactHref:
        "/runtime/export/packages/pkg-review/files/traffic_demand_explanation_v1.json",
      artifactTitle:
        "traffic_demand_explanation_v1.json / /traffic_demand_explanation / read-only package artifact"
    });
    expect(
      buildDataPanelBenchmarkEvidenceArtifactViewerDisplay(
        trafficFocus,
        {
          traffic_demand_explanation: {
            request_count: 20,
            configured_request_count: 20,
            explained_request_count: 20,
            input_flow_count: 20,
            task_request_count: 8,
            output_flow_count: 8,
            communication_only_request_count: 12,
            compute_service_request_count: 8,
            active_traffic_classes: ["DATA_TRANSFER", "COMPUTE_SERVICE"],
            traffic_class_rows: [
              {
                traffic_class: "DATA_TRANSFER",
                request_count: 12,
                input_flow_count: 12,
                task_request_count: 0,
                output_flow_count: 0,
                total_input_data_mb: 24,
                total_output_data_mb: 0,
                destination_types: ["SERVICE_ENDPOINT"]
              },
              {
                traffic_class: "COMPUTE_SERVICE",
                request_count: 8,
                input_flow_count: 8,
                task_request_count: 8,
                output_flow_count: 8,
                total_input_data_mb: 64,
                total_output_data_mb: 16,
                destination_types: ["COMPUTE_NODE"]
              }
            ],
            per_user_active_service_state: [
              {
                user_id: "user-00001",
                request_count: 12,
                service_classes: ["DATA_TRANSFER"],
                primary_service_class: "DATA_TRANSFER",
                max_priority: 1,
                first_arrival_time: 0,
                last_arrival_time: 55,
                flow_ids: ["flow-a", "flow-b"],
                task_ids: [],
                output_flow_ids: [],
                total_input_data_mb: 24,
                total_output_data_mb: 0
              },
              {
                user_id: "user-00002",
                request_count: 8,
                service_classes: ["COMPUTE_SERVICE"],
                primary_service_class: "COMPUTE_SERVICE",
                max_priority: 3,
                first_arrival_time: 10,
                last_arrival_time: 75,
                flow_ids: ["flow-c"],
                task_ids: ["task-c"],
                output_flow_ids: ["flow-c-output"],
                total_input_data_mb: 64,
                total_output_data_mb: 16
              }
            ],
            correlation_summary: {
              all_compute_services_have_task: true,
              all_compute_services_have_output_flow: true,
              packet_level_simulation: false,
              frontend_inference_required: false
            },
            explanation_window_policy: "FULL_CONFIGURED_WINDOW",
            endpoint_window_policy: "ROUND_ROBIN_ENDPOINT_IDS_CAPPED_AT_512",
            frontend_inference_required: false,
            packet_level_simulation: false,
            acceptable_for_demo_review: true,
            evidence_hash:
              "sha256:7878787878787878787878787878787878787878787878787878787878787878"
          }
        },
        false,
        null,
        "user-00002",
        {
          type: "RUNTIME_EXPORT_TRAFFIC_DEMAND_USER_PAGE_V1",
          version: "v1",
          page_id: "leo_twin.runtime_export_traffic_demand_user_page.v1",
          source: "BACKEND_RUNTIME_EXPORT_PACKAGE",
          package_id: "pkg-review",
          artifact_type: "RUNTIME_EXPORT_TRAFFIC_DEMAND_EXPLANATION_V1",
          artifact_source: "BACKEND_RUNTIME_EXPORT",
          artifact_scope: "TRAFFIC_DEMAND_OFFLINE_REVIEW",
          artifact_hash:
            "sha256:abababababababababababababababababababababababababababababababab",
          evidence_hash:
            "sha256:cdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcd",
          explanation_id: "leo_twin.traffic_demand_explanation.v1",
          explanation_window_policy: "FULL_CONFIGURED_WINDOW",
          endpoint_window_policy: "ROUND_ROBIN_ENDPOINT_IDS_CAPPED_AT_512",
          packet_level_simulation: false,
          frontend_inference_required: false,
          cursor: 0,
          limit: 8,
          next_cursor: 1,
          has_more: false,
          user_count: 1,
          item_count: 1,
          unfiltered_user_count: 2,
          request_count: 8,
          compute_service_user_count: 1,
          communication_service_user_count: 0,
          filter_applied: true,
          filters: {
            query: "user-00002",
            traffic_class: "ALL"
          },
          boundary_conditions: [
            "ARTIFACT_WINDOW_ONLY",
            "NO_TRAFFIC_REGENERATION",
            "NO_EVENT_REPLAY",
            "NO_PACKAGE_MUTATION"
          ],
          items: [
            {
              user_id: "user-00002",
              request_count: 8,
              service_classes: ["COMPUTE_SERVICE"],
              primary_service_class: "COMPUTE_SERVICE",
              max_priority: 3,
              first_arrival_time: 10,
              last_arrival_time: 75,
              flow_ids: ["flow-c"],
              task_ids: ["task-c"],
              output_flow_ids: ["flow-c-output"],
              total_input_data_mb: 64,
              total_output_data_mb: 16
            }
          ],
          page_hash:
            "sha256:efefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefef"
        }
      )
    ).toMatchObject({
      tone: "match",
      statusLabel: "pointer target resolved",
      inspectorEnabled: true,
      trafficDemandCard: {
        tone: "match",
        statusLabel: "traffic demand review ready",
        summaryLabel: "requests 20 / compute 8 / classes 2",
        metaLabels: [
          "configured 20",
          "explained 20",
          "flows 20",
          "tasks 8",
          "outputs 8",
          "frontend inference no",
          "packet no"
        ],
        classRows: [
          {
            trafficClassLabel: "DATA_TRANSFER",
            requestLabel: "requests 12",
            flowLabel: "flows 12 / tasks 0 / outputs 0",
            dataLabel: "24 MB in / 0 MB out",
            destinationLabel: "SERVICE_ENDPOINT"
          },
          {
            trafficClassLabel: "COMPUTE_SERVICE",
            requestLabel: "requests 8",
            flowLabel: "flows 8 / tasks 8 / outputs 8",
            dataLabel: "64 MB in / 16 MB out",
            destinationLabel: "COMPUTE_NODE"
          }
        ],
        userFilterLabel:
          "backend page users 1 shown / 1 matched / 2 total / filter user-00002 / cursor 0 -> 1",
        userPageControls: {
          pageLabel: "cursor 0-1 / 1 matched",
          canPrevious: false,
          canNext: false,
          previousCursor: 0,
          nextCursor: 1
        },
        userRows: [
          {
            userId: "user-00002",
            serviceLabel: "COMPUTE_SERVICE",
            requestLabel: "requests 8 / priority 3",
            flowLabel: "flows 1 / tasks 1 / outputs 1",
            dataLabel: "64 MB in / 16 MB out",
            arrivalLabel: "arrival 10 s -> 75 s"
          }
        ],
        stateLabels: [
          "active classes DATA_TRANSFER + COMPUTE_SERVICE",
          "per-user states 2",
          "compute correlation complete",
          "window FULL_CONFIGURED_WINDOW",
          "endpoint ROUND_ROBIN_ENDPOINT_IDS_CAPPED_AT_512",
          "evidence 787878787878"
        ]
      }
    });
    expect(
      buildDataPanelScenarioReviewWorkflowInspectorFocus("pkg-review", {
        stepLabel: "14 event evidence",
        statusLabel: "available",
        detailLabel: "events.jsonl",
        href: "/runtime/export/packages/pkg-review/files/events.jsonl",
        title: "events",
        tone: "match"
      })
    ).toBeNull();
  });

  it("summarizes saved route comparison review report contents", () => {
    const report = {
      type: "RUNTIME_EXPORT_ROUTE_COMPARISON_REVIEW_REPORT_V1",
      version: "v1",
      report_id: "leo_twin.runtime_export_route_comparison_review_report.v1",
      source: "OPERATOR_ROUTE_COMPARISON_REVIEW",
      report_scope: "SELECTED_PACKAGE_VS_LIVE_ROUTE_COMPARISON_OUTCOMES",
      package_id: "pkg-review",
      package_dir: "artifacts/runtime_exports/pkg-review",
      route_comparison_review: _runtimeExportRouteComparisonReview(),
      runtime_export_boundary_alignment_v1: _runtimeExportBoundaryAlignment(),
      boundary_alignment_hash:
        "sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
      boundary_alignment_status: "ALIGNED",
      boundary_alignment_warnings: [],
      runtime_export_boundary_hash:
        "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
      record_count: 3,
      match_count: 1,
      different_count: 1,
      unavailable_count: 1,
      error_count: 0,
      records: [
        {
          route_id: "route-a",
          comparison_status: "MATCH",
          package_route_detail_hash:
            "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
          live_route_detail_hash:
            "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
          matched_field_count: 12,
          different_field_count: 0,
          compared_fields: ["path", "latency"],
          different_fields: [],
          status_reason: "FIELDS_MATCH",
          operator_note: "baseline route is aligned"
        },
        {
          route_id: "route-b",
          comparison_status: "DIFFERENT",
          package_route_detail_hash:
            "sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
          live_route_detail_hash:
            "sha256:dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd",
          matched_field_count: 10,
          different_field_count: 2,
          compared_fields: ["path", "latency", "bottleneck"],
          different_fields: ["latency", "bottleneck"],
          status_reason: "FIELDS_DIFFER",
          operator_note: ""
        },
        {
          route_id: "route-c",
          comparison_status: "UNAVAILABLE",
          package_route_detail_hash:
            "sha256:eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
          live_route_detail_hash: "",
          matched_field_count: 0,
          different_field_count: 0,
          compared_fields: [],
          different_fields: [],
          status_reason: "LIVE_ROUTE_MISSING",
          operator_note: "live route not available"
        }
      ],
      ordering: "route_id ascending, then comparison_status ascending",
      boundary_conditions: ["NO_ROUTE_RECOMPUTE"],
      report_hash:
        "sha256:9999999999999999999999999999999999999999999999999999999999999999"
    };
    const display = buildDataPanelExportRouteComparisonReviewReportDisplay(
      report,
      { limit: 2 }
    );

    expect(display).toEqual({
      packageId: "pkg-review",
      tone: "different",
      statusLabel: "saved comparisons need review",
      summaryLabel:
        "pkg-review / records 3 / different 1 / error 0 / 999999999999 / hidden 1",
      metaLabels: [
        "match 1",
        "different 1",
        "unavailable 1",
        "error 0",
        "boundary alignment cccccccccccc",
        "alignment status ALIGNED",
        "boundary bbbbbbbbbbbb",
        "ordering route_id ascending, then comparison_status ascending"
      ],
      recordRows: [
        {
          routeId: "route-a",
          tone: "match",
          statusLabel: "MATCH",
          hashLabel: "package aaaaaaaaaaaa / live bbbbbbbbbbbb",
          noteLabel: "baseline route is aligned"
        },
        {
          routeId: "route-b",
          tone: "different",
          statusLabel: "DIFFERENT",
          hashLabel: "package cccccccccccc / live dddddddddddd",
          noteLabel: "FIELDS_DIFFER"
        }
      ],
      reportHref:
        "/runtime/export/packages/pkg-review/files/route_comparison_review_report_v1.json",
      filterLabel: "showing 1-2 of 3 filtered / total 3 / status ALL",
      pageCursor: 0,
      pageLimit: 2,
      previousCursor: 0,
      nextCursor: 2,
      canPreviousPage: false,
      canNextPage: true
    });
    expect(
      buildDataPanelExportRouteComparisonReviewReportDisplay(
        {
          ...report,
          records: [
            ...report.records,
            {
              route_id: "route-d",
              comparison_status: "ERROR",
              package_route_detail_hash:
                "sha256:abababababababababababababababababababababababababababababababab",
              live_route_detail_hash: "",
              matched_field_count: 0,
              different_field_count: 0,
              compared_fields: [],
              different_fields: [],
              status_reason: "LIVE_DETAIL_ERROR",
              operator_note: "operator needs retry"
            }
          ],
          record_count: 4,
          error_count: 1
        },
        {
          cursor: 0,
          limit: 1,
          query: "retry",
          status: "ERROR"
        }
      )
    ).toMatchObject({
      summaryLabel:
        "pkg-review / records 4 / different 1 / error 1 / 999999999999",
      filterLabel: "showing 1-1 of 1 filtered / total 4 / status ERROR / query retry",
      pageCursor: 0,
      pageLimit: 1,
      canPreviousPage: false,
      canNextPage: false,
      recordRows: [
        {
          routeId: "route-d",
          statusLabel: "ERROR",
          noteLabel: "operator needs retry"
        }
      ]
    });
    expect(
      buildDataPanelExportRouteComparisonReviewReportStatus(
        display,
        "pkg-review",
        false,
        null
      )
    ).toBe(display);
    expect(
      buildDataPanelExportRouteComparisonReviewReportStatus(
        null,
        "pkg-review",
        true,
        null
      )
    ).toMatchObject({
      tone: "pending",
      statusLabel: "loading saved review report",
      recordRows: []
    });
    expect(
      buildDataPanelExportRouteComparisonReviewReportStatus(
        null,
        "pkg-review",
        false,
        "HTTP 500"
      )
    ).toMatchObject({
      tone: "error",
      statusLabel: "saved review report load failed",
      metaLabels: ["HTTP 500"]
    });
  });

  it("summarizes backend-paged service trace comparison review report contents", () => {
    const report = {
      type: "RUNTIME_EXPORT_SERVICE_TRACE_COMPARISON_REVIEW_REPORT_PAGE_V1",
      version: "v1",
      page_id:
        "leo_twin.runtime_export_service_trace_comparison_review_report_page.v1",
      report_id:
        "leo_twin.runtime_export_service_trace_comparison_review_report.v1",
      report_type: "RUNTIME_EXPORT_SERVICE_TRACE_COMPARISON_REVIEW_REPORT_V1",
      source: "BACKEND_RUNTIME_EXPORT_PACKAGE",
      report_scope:
        "SELECTED_PACKAGE_VS_LIVE_SERVICE_TRACE_COMPARISON_OUTCOMES",
      package_id: "pkg-review",
      package_dir: "artifacts/runtime_exports/pkg-review",
      service_trace_comparison_review: {
        version: "v1",
        source: "BACKEND_RUNTIME_EXPORT",
        review_scope: "PACKAGE_SERVICE_TRACE_TO_LIVE_RUNTIME_SERVICE_TRACE",
        package_service_trace_endpoint:
          "GET /runtime/export/packages/{package_id}/service-traces/{trace_id}",
        live_service_trace_endpoint:
          "GET /runtime/details/service-traces/{trace_id}",
        compare_action: "compare with live service trace",
        comparison_requires_live_runtime: true,
        trace_id_alignment_required: true,
        exported_rows_only: true,
        compared_fields: ["terminal"],
        status_reasons: ["TRACE_ID_MISMATCH"],
        boundary_conditions: ["NO_SERVICE_RECOMPUTE"]
      },
      runtime_export_boundary_alignment_v1: _runtimeExportBoundaryAlignment(),
      boundary_alignment_hash:
        "sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
      boundary_alignment_status: "ALIGNED",
      boundary_alignment_warnings: [],
      runtime_export_boundary_hash:
        "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
      report_hash:
        "sha256:9999999999999999999999999999999999999999999999999999999999999999",
      report_record_count: 3,
      record_count: 2,
      unfiltered_record_count: 3,
      match_count: 0,
      different_count: 1,
      unavailable_count: 1,
      error_count: 0,
      cursor: 1,
      limit: 1,
      next_cursor: 2,
      has_more: false,
      item_count: 1,
      hidden_record_count: 1,
      filter_applied: true,
      filters: {
        query: "operator",
        status: "DIFFERENT"
      },
      records: [
        {
          trace_id: "trace:run",
          comparison_status: "DIFFERENT",
          package_trace_item_hash:
            "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
          live_trace_detail_hash:
            "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
          matched_field_count: 3,
          different_field_count: 1,
          compared_fields: ["terminal"],
          different_fields: ["terminal"],
          status_reason: "FIELDS_DIFFER",
          operator_note: "operator reviewed"
        }
      ],
      ordering: "trace_id ascending, then comparison_status ascending",
      boundary_conditions: ["NO_SERVICE_RECOMPUTE"],
      page_hash:
        "sha256:dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"
    };
    const display =
      buildDataPanelExportServiceTraceComparisonReviewReportDisplay(report);

    expect(display).toEqual({
      packageId: "pkg-review",
      tone: "different",
      statusLabel: "saved trace comparisons need review",
      summaryLabel:
        "pkg-review / records 2 / different 1 / error 0 / 999999999999",
      metaLabels: [
        "match 0",
        "different 1",
        "unavailable 1",
        "error 0",
        "backend cursor page dddddddddddd",
        "boundary alignment cccccccccccc",
        "alignment status ALIGNED",
        "boundary bbbbbbbbbbbb",
        "ordering trace_id ascending, then comparison_status ascending"
      ],
      recordRows: [
        {
          traceId: "trace:run",
          tone: "different",
          statusLabel: "DIFFERENT",
          hashLabel: "package aaaaaaaaaaaa / live bbbbbbbbbbbb",
          noteLabel: "operator reviewed"
        }
      ],
      reportHref:
        "/runtime/export/packages/pkg-review/files/service_trace_comparison_review_report_v1.json",
      filterLabel:
        "showing 2-2 of 2 filtered / total 3 / status DIFFERENT / query operator",
      pageCursor: 1,
      pageLimit: 1,
      previousCursor: 0,
      nextCursor: 2,
      canPreviousPage: true,
      canNextPage: false
    });
    expect(
      buildDataPanelExportServiceTraceComparisonReviewReportStatus(
        display,
        "pkg-review",
        false,
        null
      )
    ).toBe(display);
    expect(
      buildDataPanelExportServiceTraceComparisonReviewReportStatus(
        null,
        "pkg-review",
        true,
        null
      )
    ).toMatchObject({
      tone: "pending",
      statusLabel: "loading saved service trace review report",
      recordRows: []
    });
    expect(
      buildDataPanelExportServiceTraceComparisonReviewReportStatus(
        null,
        "pkg-review",
        false,
        "HTTP 500"
      )
    ).toMatchObject({
      tone: "error",
      statusLabel: "saved service trace review report load failed",
      metaLabels: ["HTTP 500"]
    });
  });
});

describe("buildDataPanelExportCompareDisplay", () => {
  it("summarizes runtime export review summaries for dashboard review", () => {
    const display = buildDataPanelExportReviewSummaryDisplay({
      type: "RUNTIME_EXPORT_REVIEW_SUMMARY_V1",
      version: "v1",
      summary_id: "leo_twin.runtime_export_review_summary.v1",
      source: "BACKEND_RUNTIME_EXPORT",
      summary_scope: "USER_READABLE_RESULT_PACKAGE_REVIEW",
      package_id: "pkg-review",
      package_dir: "artifacts/runtime_exports/pkg-review",
      review_status: "REVIEW_READY",
      scenario: {
        seed: 4321,
        satellite_count: 72,
        user_count: 20,
        compute_node_count: 2,
        duration_seconds: 120
      },
      runtime: {
        lifecycle_state: "RUNNING",
        current_sim_time: 12.5,
        processed_event_count: 4096,
        queued_event_count: 8
      },
      route_comparison_review: _runtimeExportRouteComparisonReview(),
      network_kpi_benchmark_validation: {
        version: "v1",
        validation_id: "leo_twin.network_kpi_benchmark_validation.v1",
        source: "config_snapshot.status.network_kpi_benchmark_validation_v1",
        evidence_present: true,
        benchmark_profile: "FLOW_LEVEL_PROXY_RUNTIME_GUARDRAILS",
        metric_model: "FLOW_LEVEL_NETWORK_KPI_PROXY",
        validation_status: "PASS",
        check_count: 12,
        passed_check_count: 12,
        warning_check_count: 0,
        failed_check_count: 0,
        missing_check_count: 0,
        packet_level_simulation: false,
        acceptable_for_demo_review: true,
        caveats: [],
        validation_hash:
          "sha256:cdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcd"
      },
      network_kpi_formula_evidence: {
        version: "v1",
        evidence_id: "leo_twin.network_kpi_formula_evidence.v1",
        source: "config_snapshot.status.network_kpi_formula_evidence_v1",
        evidence_present: true,
        runtime_status_source: "NETWORK_KPI_PROVENANCE_V2_AND_CALIBRATION_V1",
        provenance_id: "leo_twin.network_kpi_provenance.v2",
        calibration_id: "leo_twin.network_kpi_calibration.v1",
        metric_model: "FLOW_LEVEL_PROXY",
        formula_evidence_status: "FORMULA_AND_TIME_EVIDENCE_READY",
        kpi_count: 6,
        observed_kpi_count: 6,
        runtime_value_missing_count: 0,
        selected_input_count: 10,
        selected_observed_input_count: 10,
        missing_selected_input_count: 0,
        time_varying_kpi_count: 4,
        flat_kpi_count: 2,
        packet_level_simulation: false,
        acceptable_for_demo_review: true,
        caveats: ["Formula evidence summarizes backend flow-level proxy inputs."],
        evidence_hash:
          "sha256:edededededededededededededededededededededededededededededededed"
      },
      user_configuration_template_validation: {
        version: "v1",
        evidence_id: "sees.user_configuration_template_validation.v1",
        source: "config_snapshot.user_configuration_template_validation_v1",
        evidence_present: true,
        schema_id: "sees.user_configuration.v2",
        validation_scope: "APPROVED_USER_CONFIGURATION_TEMPLATES",
        validation_status: "ALL_TEMPLATES_VALID",
        template_count: 3,
        valid_template_count: 3,
        invalid_template_count: 0,
        missing_file_count: 0,
        load_failed_count: 0,
        validation_failed_count: 0,
        all_templates_valid: true,
        packet_level_simulation: false,
        external_simulators: false,
        forbidden_integrations: ["STK", "EXATA", "AFSIM", "DDS"],
        acceptable_for_demo_review: true,
        invalid_template_ids: [],
        template_evidence_hash:
          "sha256:fdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfd",
        notes: ["Approved templates validate against schema v2."],
        evidence_hash:
          "sha256:fefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefe"
      },
      traffic_demand_explanation: {
        version: "v1",
        evidence_id: "leo_twin.traffic_demand_explanation.v1",
        source:
          "config_snapshot.generated_config.backend_summary.traffic_demand_explanation_v1",
        runtime_summary_source: "backend_summary.traffic_demand_summary",
        evidence_present: true,
        request_count: 20,
        configured_request_count: 20,
        explained_request_count: 20,
        input_flow_count: 20,
        task_request_count: 8,
        output_flow_count: 8,
        communication_only_request_count: 12,
        compute_service_request_count: 8,
        active_traffic_classes: ["DATA_TRANSFER", "COMPUTE_SERVICE"],
        active_traffic_class_count: 2,
        traffic_class_row_count: 2,
        per_user_state_count: 20,
        explanation_window_policy: "FULL_CONFIGURED_WINDOW",
        endpoint_window_policy: "ROUND_ROBIN_ENDPOINT_IDS_CAPPED_AT_512",
        all_compute_services_have_task: true,
        all_compute_services_have_output_flow: true,
        packet_level_simulation: false,
        frontend_inference_required: false,
        acceptable_for_demo_review: true,
        model_assumptions: ["Flow-level demand explanation."],
        explanation_hash:
          "sha256:6969696969696969696969696969696969696969696969696969696969696969",
        evidence_hash:
          "sha256:7878787878787878787878787878787878787878787878787878787878787878"
      },
      user_service_requests: {
        version: "v2",
        evidence_id: "leo_twin.user_service_request_export_evidence.v2",
        source: "config_snapshot.status.user_service_request_summary_v2",
        evidence_present: true,
        request_model: "FLOW_LEVEL_USER_SERVICE_REQUEST_PROXY",
        route_model: "FLOW_LEVEL_ROUTE_PROXY",
        compute_model: "TASK_RESOURCE_DEMAND_PROXY",
        request_count: 20,
        exported_request_count: 18,
        hidden_request_count: 2,
        active_request_count: 9,
        communication_request_count: 12,
        compute_request_count: 8,
        network_waiting_request_count: 3,
        completed_request_count: 11,
        packet_level_simulation: false,
        frontend_inference_required: false,
        artifact_window_only: true,
        export_limit: 5000,
        summary_hash:
          "sha256:abababababababababababababababababababababababababababababababab"
      },
      reproducibility: {
        manifest_id: "leo_twin.runtime_reproducibility_manifest.v1",
        manifest_hash:
          "sha256:1111111111111111111111111111111111111111111111111111111111111111",
        config_hash:
          "sha256:2222222222222222222222222222222222222222222222222222222222222222",
        generated_config_hash:
          "sha256:3333333333333333333333333333333333333333333333333333333333333333",
        event_kernel_policy: "NO_EVENT_KERNEL_BEHAVIOR_CHANGE"
      },
      artifacts: {
        artifact_count: 10,
        artifact_filenames: [
          "config_snapshot.json",
          "events.jsonl",
          "manifest.json",
          "metrics.csv",
          "review_summary_v1.json",
          "service_lifecycle_trace_v2.json",
          "summary.json",
          "user_configuration_template_validation_v1.json",
          "traffic_demand_explanation_v1.json",
          "user_service_request_summary_v2.json"
        ],
        required_filenames: [
          "config_snapshot.json",
          "events.jsonl",
          "metrics.csv",
          "summary.json",
          "manifest.json"
        ],
        missing_required_filenames: [],
        service_lifecycle_trace_exported: true,
        review_summary_exported: true,
        network_kpi_formula_evidence_exported: true,
        user_configuration_template_validation_exported: true,
        traffic_demand_explanation_exported: true,
        user_service_request_summary_exported: true
      },
      review_notes: ["Use manifest.json"],
      summary_hash:
        "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    });

    expect(display).toEqual({
      packageId: "pkg-review",
      tone: "match",
      statusLabel: "可审阅",
      summaryLabel: "pkg-review / 10 个文件 / 12.5 s / 4,096 事件",
      metaLabels: [
        "seed 4321",
        "卫星 72",
        "用户 20",
        "算力 2",
        "manifest 111111111111",
        "summary aaaaaaaaaaaa",
        "KPI benchmark PASS",
        "KPI failed 0",
        "KPI checks 12",
        "KPI benchmark cdcdcdcdcdcd",
        "KPI formula FORMULA_AND_TIME_EVIDENCE_READY",
        "KPI formula missing inputs 0",
        "KPI formula moving 4",
        "KPI formula edededededed",
        "config templates ALL_TEMPLATES_VALID",
        "config templates valid 3 / 3",
        "config template invalid 0",
        "config template fefefefefefe",
        "traffic demand present",
        "traffic requests 20",
        "traffic classes 2",
        "compute service requests 8",
        "traffic frontend inference no",
        "traffic demand 787878787878",
        "user services present",
        "user service requests 20",
        "user services exported 18",
        "user services hidden 2",
        "compute requests 8",
        "network waiting 3",
        "user services abababababab",
        "route compare compare with live",
        "compare fields 12",
        "live runtime required",
        "report RUNTIME_EXPORT_ROUTE_COMPARISON_REVIEW_REPORT_V1"
      ],
      artifactLabels: [
        "必需文件缺失 0",
        "service trace 已导出",
        "review summary 已导出",
        "KPI formula exported",
        "config templates exported",
        "traffic demand exported",
        "user services exported"
      ]
    });
    expect(
      buildDataPanelExportReviewSummaryStatus(display, "pkg-review", false, null)
    ).toBe(display);
    expect(
      buildDataPanelExportReviewSummaryStatus(display, "pkg-next", true, null)
    ).toEqual({
      tone: "pending",
      statusLabel: "正在加载审阅摘要",
      summaryLabel: "pkg-next",
      metaLabels: ["只读摘要", "不生成新导出包"],
      artifactLabels: []
    });
    expect(
      buildDataPanelExportReviewSummaryStatus(display, "pkg-next", false, "HTTP 404")
    ).toEqual({
      tone: "error",
      statusLabel: "审阅摘要加载失败",
      summaryLabel: "pkg-next",
      metaLabels: ["HTTP 404"],
      artifactLabels: []
    });
  });

  it("summarizes runtime export user service request pages for dashboard review", () => {
    const status = buildDataPanelExportUserServiceRequestStatus(
      {
        type: "RUNTIME_EXPORT_USER_SERVICE_REQUEST_PAGE_V1",
        version: "v1",
        page_id: "leo_twin.runtime_export_user_service_request_page.v1",
        source: "BACKEND_RUNTIME_EXPORT",
        package_id: "pkg-review",
        artifact_type: "RUNTIME_EXPORT_USER_SERVICE_REQUEST_SUMMARY_V2",
        artifact_source: "user_service_request_summary_v2.json",
        artifact_policy: "STANDALONE_RUNTIME_EXPORT_ARTIFACT",
        artifact_window_only: true,
        user_service_request_export_policy: {
          policy: "EXPORT_USER_SERVICE_REQUEST_WINDOW"
        },
        artifact_hash:
          "sha256:cdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcd",
        summary_hash:
          "sha256:abababababababababababababababababababababababababababababababab",
        request_model: "FLOW_LEVEL_USER_SERVICE_REQUEST_PROXY",
        route_model: "FLOW_LEVEL_ROUTE_PROXY",
        compute_model: "TASK_RESOURCE_DEMAND_PROXY",
        packet_level_simulation: false,
        frontend_inference_required: false,
        summary_scope: "USER_SERVICE_REQUEST_WINDOW",
        export_cursor: 0,
        export_limit: 100,
        export_next_cursor: 2,
        export_has_more: false,
        cursor: 0,
        limit: 1,
        next_cursor: 1,
        has_more: true,
        request_count: 2,
        item_count: 1,
        unfiltered_request_count: 2,
        active_request_count: 2,
        communication_request_count: 2,
        compute_request_count: 1,
        network_waiting_request_count: 1,
        hidden_request_count: 0,
        filter_applied: true,
        filters: {
          query: "sat-00001",
          service_class: "ALL",
          terminal_state: "ALL",
          network_waiting: "ALL"
        },
        boundary_conditions: ["NO_SERVICE_RECOMPUTE"],
        items: [
          {
            user_id: "user-00001",
            platform_type: "GROUND_USER",
            platform_type_label: "ground user",
            status: "ACTIVE",
            communication_route_count: 1,
            available_route_count: 1,
            compute_service_count: 1,
            network_queue_count: 1,
            selected_satellite_id: "sat-00001",
            destination_id: "sat-00001",
            compute_node_id: "sat-00001",
            path: ["user-00001", "sat-00001"],
            request_id: "svc-00001",
            service_request_id: "svc-00001",
            service_class: "COMPUTE_SERVICE",
            service_class_label: "compute service",
            business_type: "COMPUTE_SERVICE",
            business_label: "compute service",
            request_active: true,
            communication_request_active: true,
            compute_request_active: true,
            network_waiting: true,
            terminal_state: "RUNNING",
            terminal_state_label: "running",
            route_id: "route-00001",
            flow_id: "flow-00001",
            task_id: "task-00001",
            trace_id: "trace:svc-00001",
            target_node_id: "sat-00001",
            next_hop_id: "sat-00001",
            network_queue_depth: 1,
            route_available: true,
            input_output_coupled: true,
            latency_components_observed: true,
            route_model: "FLOW_LEVEL_ROUTE_PROXY",
            service_model: "TASK_RESOURCE_DEMAND_PROXY",
            packet_level_simulation: false,
            status_digest: "running compute service",
            active_business_type: "COMPUTE_SERVICE",
            active_business_label: "compute service",
            request_state: "RUNNING",
            request_state_label: "running"
          }
        ],
        page_hash:
          "sha256:efefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefef"
      },
      "pkg-review",
      false,
      null
    );

    expect(status).toEqual({
      tone: "match",
      statusLabel: "user services paged",
      summaryLabel: "pkg-review / requests 2 / page 1 / active 2",
      metaLabels: [
        "model FLOW_LEVEL_USER_SERVICE_REQUEST_PROXY",
        "compute 1",
        "network waiting 1",
        "hidden 0",
        "artifact window only",
        "policy EXPORT_USER_SERVICE_REQUEST_WINDOW",
        "artifact cdcdcdcdcdcd",
        "summary abababababab",
        "page efefefefefef",
        "row click links user/route/service evidence"
      ],
      artifactHref:
        "/runtime/export/packages/pkg-review/files/user_service_request_summary_v2.json",
      rows: [
        expect.objectContaining({
          userId: "user-00001",
          requestId: "svc-00001",
          serviceRequestId: "svc-00001",
          routeId: "route-00001",
          flowId: "flow-00001",
          taskId: "task-00001",
          traceId: "trace:svc-00001",
          computeNodeId: "sat-00001",
          computeLabel: "1 compute",
          selectedSatelliteId: "sat-00001",
          artifactFilename: "user_service_request_summary_v2.json",
          artifactPointer: "/summary/items",
          artifactFilter: "trace:svc-00001",
          correlationLabel:
            "request svc-00001 / route route-00001 / flow flow-00001 / task task-00001 / trace trace:svc-00001 / compute sat-00001 / next sat-00001"
        })
      ],
      filterLabel: "query sat-00001 / backend artifact page 1-1 / 2",
      pageCursor: 0,
      pageLimit: 1,
      previousCursor: 0,
      nextCursor: 1,
      canPreviousPage: false,
      canNextPage: true
    });
    expect(
      buildDataPanelUserServiceRequestEvidenceInspectorFocus(
        "pkg-review",
        status?.rows[0]
      )
    ).toMatchObject({
      focusSourceLabel: "User service request evidence inspector focus",
      statusLabel: "user service / svc-00001",
      artifactLabel: "user_service_request_summary_v2.json",
      jsonPointer: "/summary/items",
      defaultInspectorFilter: "trace:svc-00001"
    });
    expect(
      buildDataPanelExportUserServiceRequestStatus(null, "pkg-review", true)
    ).toMatchObject({
      tone: "pending",
      statusLabel: "loading user service requests"
    });
    expect(
      buildDataPanelExportUserServiceRequestStatus(
        null,
        "pkg-review",
        false,
        "HTTP 404"
      )
    ).toMatchObject({
      tone: "error",
      metaLabels: ["HTTP 404"]
    });
  });

  it("summarizes runtime export diagnostics bundles for dashboard review", () => {
    const display = buildDataPanelExportDiagnosticsDisplay({
      type: "RUNTIME_EXPORT_DIAGNOSTICS_BUNDLE_V1",
      version: "v1",
      bundle_id: "leo_twin.runtime_export_diagnostics_bundle.v1",
      source: "BACKEND_RUNTIME_EXPORT",
      diagnostics_scope: "RESULT_PACKAGE_OPERATOR_REVIEW",
      package: {
        package_id: "pkg-review",
        package_dir: "artifacts/runtime_exports/pkg-review",
        package_complete: true,
        review_status: "REVIEW_READY",
        contract_id: "leo_twin.result_package_contract.v1"
      },
      runtime: {
        lifecycle_state: "STOPPED",
        current_sim_time: 120,
        processed_event_count: 4096,
        queued_event_count: 0
      },
      route_comparison_review: _runtimeExportRouteComparisonReview(),
      network_kpi_benchmark_validation: {
        version: "v1",
        validation_id: "leo_twin.network_kpi_benchmark_validation.v1",
        source: "config_snapshot.status.network_kpi_benchmark_validation_v1",
        evidence_present: true,
        benchmark_profile: "FLOW_LEVEL_PROXY_RUNTIME_GUARDRAILS",
        metric_model: "FLOW_LEVEL_NETWORK_KPI_PROXY",
        validation_status: "PASS",
        check_count: 12,
        passed_check_count: 12,
        warning_check_count: 0,
        failed_check_count: 0,
        missing_check_count: 0,
        packet_level_simulation: false,
        acceptable_for_demo_review: true,
        caveats: [],
        validation_hash:
          "sha256:cdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcd"
      },
      network_kpi_formula_evidence: {
        version: "v1",
        evidence_id: "leo_twin.network_kpi_formula_evidence.v1",
        source: "config_snapshot.status.network_kpi_formula_evidence_v1",
        evidence_present: true,
        metric_model: "FLOW_LEVEL_PROXY",
        formula_evidence_status: "FORMULA_AND_TIME_EVIDENCE_READY",
        kpi_count: 6,
        observed_kpi_count: 6,
        runtime_value_missing_count: 0,
        selected_input_count: 10,
        selected_observed_input_count: 10,
        missing_selected_input_count: 0,
        time_varying_kpi_count: 4,
        flat_kpi_count: 2,
        packet_level_simulation: false,
        acceptable_for_demo_review: true,
        caveats: [],
        evidence_hash:
          "sha256:edededededededededededededededededededededededededededededededed"
      },
      user_configuration_template_validation: {
        version: "v1",
        evidence_id: "sees.user_configuration_template_validation.v1",
        source: "config_snapshot.user_configuration_template_validation_v1",
        evidence_present: true,
        schema_id: "sees.user_configuration.v2",
        validation_scope: "APPROVED_USER_CONFIGURATION_TEMPLATES",
        validation_status: "ALL_TEMPLATES_VALID",
        template_count: 3,
        valid_template_count: 3,
        invalid_template_count: 0,
        missing_file_count: 0,
        load_failed_count: 0,
        validation_failed_count: 0,
        all_templates_valid: true,
        packet_level_simulation: false,
        external_simulators: false,
        forbidden_integrations: ["STK", "EXATA", "AFSIM", "DDS"],
        acceptable_for_demo_review: true,
        invalid_template_ids: [],
        template_evidence_hash:
          "sha256:fdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfd",
        notes: ["Approved templates validate against schema v2."],
        evidence_hash:
          "sha256:fefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefe"
      },
      user_service_requests: {
        version: "v2",
        evidence_id: "leo_twin.user_service_request_export_evidence.v2",
        source: "config_snapshot.status.user_service_request_summary_v2",
        evidence_present: true,
        request_model: "FLOW_LEVEL_USER_SERVICE_REQUEST_PROXY",
        route_model: "FLOW_LEVEL_ROUTE_PROXY",
        compute_model: "TASK_RESOURCE_DEMAND_PROXY",
        request_count: 20,
        exported_request_count: 18,
        hidden_request_count: 2,
        active_request_count: 9,
        communication_request_count: 12,
        compute_request_count: 8,
        network_waiting_request_count: 3,
        completed_request_count: 11,
        packet_level_simulation: false,
        frontend_inference_required: false,
        artifact_window_only: true,
        export_limit: 5000,
        summary_hash:
          "sha256:abababababababababababababababababababababababababababababababab"
      },
      traffic_demand_explanation: {
        version: "v1",
        evidence_id: "leo_twin.traffic_demand_explanation.v1",
        source:
          "config_snapshot.generated_config.backend_summary.traffic_demand_explanation_v1",
        runtime_summary_source: "backend_summary.traffic_demand_summary",
        evidence_present: true,
        request_count: 20,
        configured_request_count: 20,
        explained_request_count: 20,
        input_flow_count: 20,
        task_request_count: 8,
        output_flow_count: 8,
        communication_only_request_count: 12,
        compute_service_request_count: 8,
        active_traffic_classes: ["DATA_TRANSFER", "COMPUTE_SERVICE"],
        active_traffic_class_count: 2,
        traffic_class_row_count: 2,
        per_user_state_count: 20,
        explanation_window_policy: "FULL_CONFIGURED_WINDOW",
        endpoint_window_policy: "ROUND_ROBIN_ENDPOINT_IDS_CAPPED_AT_512",
        all_compute_services_have_task: true,
        all_compute_services_have_output_flow: true,
        packet_level_simulation: false,
        frontend_inference_required: false,
        acceptable_for_demo_review: true,
        model_assumptions: ["Flow-level demand explanation."],
        explanation_hash:
          "sha256:6969696969696969696969696969696969696969696969696969696969696969",
        evidence_hash:
          "sha256:7878787878787878787878787878787878787878787878787878787878787878"
      },
      reproducibility: {
        manifest_id: "leo_twin.runtime_reproducibility_manifest.v1",
        manifest_ok: true,
        manifest_hash:
          "sha256:1111111111111111111111111111111111111111111111111111111111111111",
        config_hash: "sha256:config",
        generated_config_hash: "sha256:generated",
        review_summary_hash: "sha256:summary"
      },
      artifact_health: {
        artifact_count: 9,
        artifact_filenames: [
          "config_snapshot.json",
          "diagnostics_bundle_v1.json",
          "events.jsonl",
          "manifest.json",
          "metrics.csv",
          "review_summary_v1.json",
          "service_lifecycle_trace_v2.json",
          "summary.json",
          "user_configuration_template_validation_v1.json"
        ],
        required_filenames: [
          "config_snapshot.json",
          "events.jsonl",
          "manifest.json",
          "metrics.csv",
          "summary.json"
        ],
        recommended_filenames: [
          "service_lifecycle_trace_v2.json",
          "review_summary_v1.json",
          "diagnostics_bundle_v1.json"
        ],
        present_required_filenames: [
          "config_snapshot.json",
          "events.jsonl",
          "manifest.json",
          "metrics.csv",
          "summary.json"
        ],
        missing_required_filenames: [],
        present_recommended_filenames: [
          "service_lifecycle_trace_v2.json",
          "review_summary_v1.json",
          "diagnostics_bundle_v1.json"
        ],
        missing_recommended_filenames: []
      },
      model_boundaries: {
        event_kernel_policy: "NO_EVENT_KERNEL_BEHAVIOR_CHANGE",
        packet_level_simulation: false,
        external_simulators: [],
        forbidden_external_integrations: ["STK", "EXATA", "AFSIM", "DDS"],
        diagnostics_policy: "Deterministic package index only."
      },
      findings: [
        {
          severity: "INFO",
          code: "RESULT_PACKAGE_REVIEW_READY",
          message: "Required artifacts, manifest id, and review summary are ready."
        }
      ],
      finding_count: 1,
      recommended_next_actions: ["Attach the package directory or deterministic archive."],
      diagnostics_hash:
        "sha256:abababababababababababababababababababababababababababababababab"
    });

    expect(display).toMatchObject({
      packageId: "pkg-review",
      tone: "match",
      statusLabel: "诊断通过",
      summaryLabel: "pkg-review / findings 1 / artifacts 9 / abababababab",
      metaLabels: [
        "manifest OK",
        "必需缺失 0",
        "推荐缺失 0",
        "ERROR 0",
        "WARN 0",
        "events 4,096"
      ],
      findingRows: [
        {
          severity: "INFO",
          code: "RESULT_PACKAGE_REVIEW_READY",
          tone: "info"
        }
      ],
      actionLabels: ["Attach the package directory or deterministic archive."],
      diagnosticsHref:
        "/runtime/export/packages/pkg-review/files/diagnostics_bundle_v1.json"
    });
    expect(display?.modelBoundaryLabels).toContain("无包级仿真");
    expect(display?.modelBoundaryLabels).toContain("禁用 STK/EXATA/AFSIM/DDS");
    expect(display?.modelBoundaryLabels).toContain(
      "route compare compare with live"
    );
    expect(display?.modelBoundaryLabels).toContain("compare fields 12");
    expect(display?.modelBoundaryLabels).toContain("live runtime required");
    expect(display?.modelBoundaryLabels).toContain("KPI benchmark PASS");
    expect(display?.modelBoundaryLabels).toContain("KPI failed 0");
    expect(display?.modelBoundaryLabels).toContain("KPI checks 12");
    expect(display?.modelBoundaryLabels).toContain("KPI benchmark cdcdcdcdcdcd");
    expect(display?.modelBoundaryLabels).toContain(
      "KPI formula FORMULA_AND_TIME_EVIDENCE_READY"
    );
    expect(display?.modelBoundaryLabels).toContain("KPI formula missing inputs 0");
    expect(display?.modelBoundaryLabels).toContain("KPI formula moving 4");
    expect(display?.modelBoundaryLabels).toContain("KPI formula edededededed");
    expect(display?.modelBoundaryLabels).toContain(
      "config templates ALL_TEMPLATES_VALID"
    );
    expect(display?.modelBoundaryLabels).toContain("config templates valid 3 / 3");
    expect(display?.modelBoundaryLabels).toContain("config template invalid 0");
    expect(display?.modelBoundaryLabels).toContain("config template fefefefefefe");
    expect(display?.modelBoundaryLabels).toContain("traffic demand present");
    expect(display?.modelBoundaryLabels).toContain("traffic requests 20");
    expect(display?.modelBoundaryLabels).toContain("traffic classes 2");
    expect(display?.modelBoundaryLabels).toContain("compute service requests 8");
    expect(display?.modelBoundaryLabels).toContain("traffic frontend inference no");
    expect(display?.modelBoundaryLabels).toContain("traffic demand 787878787878");
    expect(display?.modelBoundaryLabels).toContain("user services present");
    expect(display?.modelBoundaryLabels).toContain("user service requests 20");
    expect(display?.modelBoundaryLabels).toContain("user services exported 18");
    expect(display?.modelBoundaryLabels).toContain("user services hidden 2");
    expect(display?.modelBoundaryLabels).toContain("compute requests 8");
    expect(display?.modelBoundaryLabels).toContain("network waiting 3");
    expect(display?.modelBoundaryLabels).toContain("user services abababababab");
    expect(display?.modelBoundaryLabels).toContain(
      "report RUNTIME_EXPORT_ROUTE_COMPARISON_REVIEW_REPORT_V1"
    );
    expect(
      buildDataPanelExportDiagnosticsStatus(display, "pkg-review", false, null)
    ).toBe(display);
    expect(
      buildDataPanelExportDiagnosticsStatus(display, "pkg-next", true, null)
    ).toEqual({
      tone: "pending",
      statusLabel: "正在加载诊断包",
      summaryLabel: "pkg-next",
      metaLabels: ["只读诊断", "不执行恢复或重放"],
      modelBoundaryLabels: [],
      findingRows: [],
      actionLabels: [],
      diagnosticsHref: null
    });
    expect(
      buildDataPanelExportDiagnosticsStatus(display, "pkg-next", false, "HTTP 404")
    ).toMatchObject({
      tone: "error",
      statusLabel: "诊断包加载失败",
      summaryLabel: "pkg-next",
      metaLabels: ["HTTP 404"],
      diagnosticsHref: null
    });
  });

  it("summarizes runtime export service lifecycle traces for package review", () => {
    const trace = {
      version: "v2",
      contract_id: "leo_twin.service_lifecycle_trace_contract.v2",
      source: "RUNTIME_EXPORT_PACKAGE",
      source_summary: "service_latency_history_v1",
      summary_scope: "SERVICE_LIFECYCLE_TRACE_WINDOW",
      trace_model: "COMMUNICATION_COMPUTE_COMPONENT_PROXY",
      cursor: 0,
      limit: 100,
      next_cursor: 1,
      has_more: false,
      service_count: 2,
      trace_count: 2,
      complete_trace_count: 1,
      running_trace_count: 1,
      incomplete_trace_count: 0,
      hidden_trace_count: 0,
      items: [
        {
          trace_id: "trace:done",
          service_id: "svc-done",
          task_id: "task-done",
          service_class: "COMPUTE_SERVICE",
          input_flow_id: "flow-in",
          output_flow_id: "flow-out",
          input_route_id: "route-in",
          output_route_id: "route-out",
          compute_node_id: "sat-00002",
          placement_status: "PLACED",
          input_network_latency_s: 1,
          compute_queue_delay_s: 0.5,
          compute_execution_delay_s: 2,
          output_network_latency_s: 1,
          total_latency_s: 4.5,
          terminal_state: "COMPLETE",
          terminal_state_reason: "TOTAL_LATENCY_OBSERVED",
          stage_count: 4,
          observed_stage_count: 4,
          pending_stage_count: 0,
          stages: []
        },
        {
          trace_id: "trace:run",
          service_id: "svc-run",
          task_id: "task-run",
          service_class: "COMPUTE_SERVICE",
          input_flow_id: "flow-run-in",
          output_flow_id: "flow-run-out",
          input_route_id: "route-run-in",
          output_route_id: "",
          compute_node_id: "sat-00003",
          placement_status: "PLACED",
          input_network_latency_s: 1,
          compute_queue_delay_s: 0.2,
          compute_execution_delay_s: 1,
          output_network_latency_s: 0,
          total_latency_s: 0,
          terminal_state: "RUNNING",
          terminal_state_reason: "OUTPUT_NETWORK_PENDING",
          stage_count: 4,
          observed_stage_count: 3,
          pending_stage_count: 1,
          stages: []
        }
      ]
    };
    const display = buildDataPanelServiceLifecycleTraceDisplay(trace, 5);

    expect(
      buildDataPanelExportServiceLifecycleTraceStatus(
        display,
        trace,
        "pkg-review",
        false,
        null
      )
    ).toMatchObject({
      tone: "different",
      statusLabel: "service traces need review",
      summaryLabel: "pkg-review / traces 2 / complete 1 / running 1 / incomplete 0",
      metaLabels: [
        "service 2",
        "hidden 0",
        "cursor 0 -> 1",
        "complete window",
        "model COMMUNICATION_COMPUTE_COMPONENT_PROXY"
      ],
      traceHref:
        "/runtime/export/packages/pkg-review/files/service_lifecycle_trace_v2.json",
      display: {
        items: [
          expect.objectContaining({ traceId: "trace:done" }),
          expect.objectContaining({ traceId: "trace:run" })
        ]
      }
    });
    expect(
      buildDataPanelExportServiceLifecycleTraceStatus(
        null,
        null,
        "pkg-review",
        true,
        null
      )
    ).toMatchObject({
      tone: "pending",
      statusLabel: "loading service trace artifact",
      traceHref: null,
      display: null
    });
    expect(
      buildDataPanelExportServiceLifecycleTraceStatus(
        null,
        null,
        "pkg-review",
        false,
        "HTTP 404"
      )
    ).toMatchObject({
      tone: "error",
      statusLabel: "service trace artifact load failed",
      metaLabels: ["HTTP 404"]
    });
    const pagedTrace = {
      ...trace,
      service_count: 3,
      trace_count: 3,
      complete_trace_count: 1,
      running_trace_count: 1,
      incomplete_trace_count: 1,
      items: [
        ...trace.items,
        {
          ...trace.items[0],
          trace_id: "trace:queued",
          service_id: "svc-queued",
          task_id: "task-queued",
          input_flow_id: "flow-queued-in",
          output_flow_id: "flow-queued-out",
          input_route_id: "route-queued-in",
          output_route_id: "",
          compute_node_id: "sat-00004",
          terminal_state: "INCOMPLETE",
          terminal_state_reason: "NO_COMPONENT_OBSERVATIONS",
          observed_stage_count: 0,
          pending_stage_count: 4,
          total_latency_s: 0
        }
      ]
    };
    const pagedDisplay = buildDataPanelServiceLifecycleTraceDisplay(pagedTrace, 10);

    expect(
      buildDataPanelExportServiceLifecycleTraceStatus(
        pagedDisplay,
        pagedTrace,
        "pkg-review",
        false,
        null,
        { cursor: 1, limit: 1 }
      )
    ).toMatchObject({
      filterLabel: "all service traces / local artifact page 2-2 / 3",
      pageCursor: 1,
      pageLimit: 1,
      previousCursor: 0,
      nextCursor: 2,
      canPreviousPage: true,
      canNextPage: true,
      display: {
        items: [expect.objectContaining({ traceId: "trace:run" })]
      }
    });
    expect(
      buildDataPanelExportServiceLifecycleTraceStatus(
        pagedDisplay,
        pagedTrace,
        "pkg-review",
        false,
        null,
        {
          query: "route-run",
          terminalState: "RUNNING",
          computeNodeId: "sat-00003",
          terminalReason: "OUTPUT_NETWORK_PENDING",
          cursor: 0,
          limit: 1
        }
      )
    ).toMatchObject({
      filterLabel:
        "query route-run / state RUNNING / compute sat-00003 / reason OUTPUT_NETWORK_PENDING / local artifact page 1-1 / 1",
      canPreviousPage: false,
      canNextPage: false,
      display: {
        items: [expect.objectContaining({ traceId: "trace:run" })]
      }
    });
    const backendPage = {
      type: "RUNTIME_EXPORT_SERVICE_TRACE_PAGE_V1",
      version: "v1",
      page_id: "leo_twin.runtime_export_service_trace_page.v1",
      source: "BACKEND_RUNTIME_EXPORT_PACKAGE",
      package_id: "pkg-review",
      artifact_type: "SERVICE_LIFECYCLE_TRACE_EXPORT_V2",
      artifact_source: "BACKEND_RUNTIME_STATUS",
      artifact_policy: "STANDALONE_RUNTIME_EXPORT_ARTIFACT",
      artifact_window_only: true,
      trace_contract_id: "leo_twin.service_lifecycle_trace_contract.v2",
      trace_model: "COMMUNICATION_COMPUTE_COMPONENT_PROXY",
      source_summary: "service_latency_history_v1",
      summary_scope: "SERVICE_LIFECYCLE_TRACE_WINDOW",
      export_cursor: 0,
      export_limit: 100,
      export_next_cursor: 3,
      export_has_more: false,
      cursor: 1,
      limit: 1,
      next_cursor: 2,
      has_more: true,
      service_count: 3,
      trace_count: 3,
      item_count: 1,
      unfiltered_trace_count: 3,
      complete_trace_count: 1,
      running_trace_count: 1,
      incomplete_trace_count: 1,
      hidden_trace_count: 2,
      filter_applied: false,
      filters: {
        query: "",
        terminal_state: "ALL",
        compute_node_id: "",
        stage_kind: "ALL",
        terminal_reason: "ALL"
      },
      boundary_conditions: [
        "ARTIFACT_WINDOW_ONLY",
        "NO_EVENT_REPLAY",
        "NO_SERVICE_RECOMPUTE",
        "NO_PACKAGE_MUTATION"
      ],
      items: [pagedTrace.items[1]],
      page_hash: "sha256:tracepage1234567890"
    };
    const backendTrace = runtimeExportServiceTracePageToLifecycleTrace(backendPage);
    const backendDisplay = buildDataPanelServiceLifecycleTraceDisplay(
      backendTrace,
      backendTrace.items.length
    );
    expect(
      buildDataPanelExportServiceLifecycleTraceStatus(
        backendDisplay,
        backendTrace,
        "pkg-review",
        false,
        null,
        {
          backendPage,
          cursor: backendPage.cursor,
          limit: backendPage.limit
        }
      )
    ).toMatchObject({
      filterLabel: "all service traces / backend artifact page 2-2 / 3",
      pageCursor: 1,
      pageLimit: 1,
      previousCursor: 0,
      nextCursor: 2,
      canPreviousPage: true,
      canNextPage: true,
      metaLabels: expect.arrayContaining([
        "artifact window only",
        "page hash tracepage123"
      ]),
      display: {
        items: [expect.objectContaining({ traceId: "trace:run" })]
      }
    });
  });

  it("summarizes runtime export route detail indexes for dashboard review", () => {
    const display = buildDataPanelExportRouteDetailIndexDisplay({
      type: "RUNTIME_EXPORT_ROUTE_DETAIL_INDEX_V1",
      version: "v1",
      index_id: "leo_twin.runtime_export_route_detail_index.v1",
      source: "BACKEND_RUNTIME_EXPORT",
      index_scope: "ROUTE_EXPLANATION_WINDOW_EXPORT",
      package_id: "pkg-review",
      package_dir: "artifacts/runtime_exports/pkg-review",
      route_model: "FLOW_LEVEL_ROUTE_PROXY",
      packet_level_simulation: false,
      all_pairs_computation: false,
      route_summary: {
        source: "BACKEND_RUNTIME_SNAPSHOT",
        summary_scope: "ROUTE_EXPLANATION_WINDOW",
        cursor: 0,
        limit: 500,
        next_cursor: 2,
        has_more: false,
        route_count: 2,
        indexed_route_count: 2,
        hidden_route_count: 0,
        available_route_count: 1,
        blocked_route_count: 1,
        over_demand_route_count: 0,
        compute_service_route_count: 1,
        network_service_route_count: 1
      },
      route_detail_export_policy: {
        version: "v1",
        source: "BACKEND_RUNTIME_EXPORT",
        policy: "EXPORT_ROUTE_DETAIL_INDEX_WINDOW",
        route_summary_source: "visible_snapshot.routes",
        route_detail_limit: 5000,
        route_count: 2,
        indexed_route_count: 2,
        hidden_route_count: 0,
        packet_level_simulation: false,
        all_pairs_computation: false
      },
      route_trust: {
        version: "v1",
        trust_id: "leo_twin.route_provenance_trust.v1",
        source: "config_snapshot.status.route_provenance_trust_summary_v1",
        evidence_present: true,
        route_model: "FLOW_LEVEL_ROUTE_PROXY",
        packet_level_simulation: false,
        all_pairs_computation: false,
        trust_status: "COMPLETE_FLOW_LEVEL_ROUTE_PROXY",
        route_count: 2,
        assessed_route_count: 2,
        hidden_route_count: 0,
        available_route_count: 1,
        blocked_route_count: 1,
        over_demand_route_count: 0,
        explained_route_count: 2,
        missing_explanation_count: 0,
        path_context_route_count: 2,
        next_hop_route_count: 2,
        loss_proxy_route_count: 1,
        bottleneck_components: ["LOSS_PROXY"],
        sample_route_ids: ["route-a", "route-b"],
        caveats: []
      },
      route_ids: ["route-a", "route-b"],
      sample_route_ids: ["route-a", "route-b"],
      indexed_sample_route_ids: ["route-a", "route-b"],
      missing_sample_route_ids: [],
      source_order_policy: "route_explanation_summary_v1.items order is preserved",
      routes: [
        _runtimeExportRouteIndexRoute("route-a", true),
        _runtimeExportRouteIndexRoute("route-b", false)
      ],
      route_detail_index_hash:
        "sha256:cdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcd"
    });

    expect(display).toMatchObject({
      packageId: "pkg-review",
      tone: "match",
      statusLabel: "路由证据可复盘",
      summaryLabel: "pkg-review / indexed 2/2 / hidden 0 / cdcdcdcdcdcd",
      metaLabels: [
        "samples 2/2",
        "missing samples 0",
        "export limit 5,000",
        "available 1",
        "blocked 1",
        "compute 1",
        "network 1"
      ],
      boundaryLabels: [
        "FLOW_LEVEL_ROUTE_PROXY",
        "无包级仿真",
        "无全对全路由计算",
        "route_explanation_summary_v1.items order is preserved"
      ],
      indexHref:
        "/runtime/export/packages/pkg-review/files/route_detail_index_v1.json"
    });
    expect(display?.routeRows).toMatchObject([
      { routeId: "route-a", pathLabel: "user-0 -> sat-0", available: true },
      { routeId: "route-b", pathLabel: "user-0 -> sat-0", available: false }
    ]);
    expect(
      buildDataPanelRouteEvidenceInspectorFocus("pkg-review", display?.routeRows[1])
    ).toMatchObject({
      focusSourceLabel: "Route evidence inspector focus",
      statusLabel: "route evidence / route-b",
      artifactLabel: "route_detail_index_v1.json",
      jsonPointer: "/routes/1",
      defaultInspectorFilter: "route-b"
    });
    expect(
      buildDataPanelExportRouteDetailIndexStatus(display, "pkg-review", false, null)
    ).toBe(display);
    expect(
      buildDataPanelExportRouteDetailIndexStatus(display, "pkg-next", true, null)
    ).toMatchObject({
      tone: "pending",
      statusLabel: "正在加载路由证据索引",
      summaryLabel: "pkg-next",
      indexHref: null
    });
    expect(
      buildDataPanelExportRouteDetailIndexStatus(display, "pkg-next", false, "HTTP 404")
    ).toMatchObject({
      tone: "error",
      statusLabel: "路由证据索引加载失败",
      summaryLabel: "pkg-next",
      metaLabels: ["HTTP 404"],
      indexHref: null
    });
  });

  it("filters runtime export route detail indexes for reproducibility review", () => {
    const routes = [
      _runtimeExportRouteIndexRoute("route-a", true),
      _runtimeExportRouteIndexRoute("route-b", false),
      {
        ..._runtimeExportRouteIndexRoute("route-c", true),
        destination_id: "sat-1",
        selected_satellite_id: "sat-1",
        primary_next_hop_id: "sat-1",
        next_hop_ids: ["sat-1"],
        path: ["user-0", "sat-1"],
        path_label: "user-0 -> sat-1",
        bottleneck_component: "CAPACITY",
        bottleneck_reason: "ROUTE_CAPACITY_PRESSURE",
        bottleneck_reason_label: "Route capacity pressure",
        explanation_label: "route is capacity constrained"
      }
    ];

    expect(
      filterRuntimeExportRouteDetailIndexRoutes(routes, "route-b data_transfer").map(
        (route) => route.route_id
      )
    ).toEqual(["route-b"]);

    const display = buildDataPanelExportRouteDetailIndexDisplay(
      _runtimeExportRouteDetailIndex(routes),
      {
        query: "sat-1 capacity",
        routeLimit: 1
      }
    );

    expect(display).toMatchObject({
      packageId: "pkg-review",
      filterLabel: "shown 1/1 / matched 1/3 / query sat-1 capacity",
      routeRows: [
        {
          routeId: "route-c",
          pathLabel: "user-0 -> sat-1",
          packageDetailHref:
            "/runtime/export/packages/pkg-review/routes/route-c",
          artifactFilename: "route_detail_index_v1.json",
          artifactPointer: "/routes/2",
          artifactFilter: "route-c",
          compareActionLabel: "compare with live",
          liveDetailActionLabel: "live route detail"
        }
      ]
    });
  });

  it("summarizes runtime export route detail pages for dashboard review", () => {
    const page = _runtimeExportRouteDetailPage([
      _runtimeExportRouteIndexRoute("route-a", true),
      _runtimeExportRouteIndexRoute("route-b", false)
    ]);

    const display = buildDataPanelExportRouteDetailPageDisplay(page);

    expect(display).toMatchObject({
      packageId: "pkg-review",
      tone: "match",
      summaryLabel: "pkg-review / page 2/12 / total 20 / cdcdcdcdcdcd",
      metaLabels: [
        "server page 0-2",
        "matched 12",
        "export limit 5,000",
        "available 8",
        "blocked 4",
        "compute 7",
        "network 5",
        "route compare compare with live",
        "compare fields 12",
        "live runtime required",
        "report RUNTIME_EXPORT_ROUTE_COMPARISON_REVIEW_REPORT_V1"
      ],
      boundaryLabels: [
        "ROUTE_EXPLANATION_WINDOW_EXPORT",
        "BACKEND_RUNTIME_EXPORT_PACKAGE",
        "server filter applied",
        "EXPORT_ROUTE_DETAIL_INDEX_WINDOW",
        "visible_snapshot.routes"
      ],
      filterLabel:
        "shown 2/12 / query sat-0 / AVAILABLE / COMPUTE_SERVICE / server page",
      pageCursor: 0,
      pageLimit: 2,
      previousCursor: 0,
      nextCursor: 2,
      canPreviousPage: false,
      canNextPage: true,
      indexHref:
        "/runtime/export/packages/pkg-review/files/route_detail_index_v1.json"
    });
    expect(display?.routeRows).toMatchObject([
      {
        routeId: "route-a",
        packageDetailHref: "/runtime/export/packages/pkg-review/routes/route-a",
        artifactPointer: "/routes"
      },
      {
        routeId: "route-b",
        packageDetailHref: "/runtime/export/packages/pkg-review/routes/route-b",
        artifactPointer: "/routes"
      }
    ]);
  });

  it("summarizes runtime export route detail items for package review", () => {
    const display = buildDataPanelExportRouteDetailItemDisplay({
      type: "RUNTIME_EXPORT_ROUTE_DETAIL_ITEM_V1",
      version: "v1",
      item_id: "leo_twin.runtime_export_route_detail_item.v1",
      source: "BACKEND_RUNTIME_EXPORT_PACKAGE",
      package_id: "pkg-review",
      index_id: "leo_twin.runtime_export_route_detail_index.v1",
      route_detail_index_hash:
        "sha256:cdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcd",
      route_id: "route-a",
      route: _runtimeExportRouteIndexRoute("route-a", true),
      item_hash:
        "sha256:abababababababababababababababababababababababababababababababab"
    });

    expect(display).toMatchObject({
      packageId: "pkg-review",
      routeId: "route-a",
      tone: "match",
      statusLabel: "package route detail ready",
      summaryLabel: "pkg-review / route-a / abababababab",
      detailHref: "/runtime/export/packages/pkg-review/routes/route-a"
    });
    expect(display?.fields).toEqual(
      expect.arrayContaining([
        expect.objectContaining({
          label: "source",
          value: "BACKEND_RUNTIME_EXPORT_PACKAGE"
        }),
        expect.objectContaining({ label: "flow", value: "flow-route-a" }),
        expect.objectContaining({ label: "business", value: "compute service" }),
        expect.objectContaining({
          label: "source -> destination",
          value: "user-0 -> sat-0"
        }),
        expect.objectContaining({ label: "path", value: "user-0 -> sat-0" })
      ])
    );
    expect(
      buildDataPanelExportRouteDetailItemStatus(
        display,
        "pkg-review",
        "route-a",
        false,
        null
      )
    ).toBe(display);
    expect(
      buildDataPanelExportRouteDetailItemStatus(
        display,
        "pkg-review",
        "route-b",
        true,
        null
      )
    ).toMatchObject({
      tone: "pending",
      statusLabel: "loading package route detail",
      summaryLabel: "pkg-review / route-b",
      detailHref: null
    });
    expect(
      buildDataPanelExportRouteDetailItemStatus(
        display,
        "pkg-review",
        "route-b",
        false,
        "HTTP 404"
      )
    ).toMatchObject({
      tone: "error",
      statusLabel: "package route detail load failed",
      summaryLabel: "pkg-review / route-b",
      detailHref: "/runtime/export/packages/pkg-review/routes/route-b"
    });
    expect(
      buildDataPanelExportRouteDetailItemStatus(
        display,
        "pkg-other",
        "route-a",
        false,
        null
      )
    ).toBeNull();
  });

  it("summarizes runtime export service trace items for package review", () => {
    const display = buildDataPanelExportServiceTraceItemDisplay({
      type: "RUNTIME_EXPORT_SERVICE_TRACE_ITEM_V1",
      version: "v1",
      item_id: "leo_twin.runtime_export_service_trace_item.v1",
      source: "BACKEND_RUNTIME_EXPORT_PACKAGE",
      package_id: "pkg-review",
      artifact_type: "SERVICE_LIFECYCLE_TRACE_EXPORT_V2",
      artifact_source: "BACKEND_RUNTIME_STATUS",
      artifact_policy: "STANDALONE_RUNTIME_EXPORT_ARTIFACT",
      artifact_window_only: true,
      trace_contract_id: "leo_twin.service_lifecycle_trace_contract.v2",
      trace_model: "COMMUNICATION_COMPUTE_COMPONENT_PROXY",
      source_summary: "service_latency_history_v1",
      summary_scope: "SERVICE_LIFECYCLE_TRACE_ITEM",
      trace_id: "trace:run",
      trace: {
        trace_id: "trace:run",
        service_id: "svc-run",
        task_id: "task-run",
        service_class: "COMPUTE_SERVICE",
        input_flow_id: "flow-in",
        output_flow_id: "flow-out",
        input_route_id: "route-in",
        output_route_id: "route-out",
        compute_node_id: "sat-00003",
        input_network_latency_s: 0.12,
        compute_queue_delay_s: 0.02,
        compute_execution_delay_s: 0.4,
        output_network_latency_s: 0.08,
        total_latency_s: 0.62,
        terminal_state: "RUNNING",
        terminal_state_reason: "OUTPUT_NETWORK_PENDING",
        stage_count: 4,
        observed_stage_count: 3,
        pending_stage_count: 1,
        stages: []
      },
      boundary_conditions: [
        "ARTIFACT_WINDOW_ONLY",
        "NO_EVENT_REPLAY",
        "NO_SERVICE_RECOMPUTE",
        "NO_PACKAGE_MUTATION"
      ],
      item_hash:
        "sha256:cdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcd"
    });

    expect(display).toMatchObject({
      packageId: "pkg-review",
      traceId: "trace:run",
      tone: "different",
      statusLabel: "package service trace needs review",
      summaryLabel: "pkg-review / trace:run / cdcdcdcdcdcd",
      detailHref:
        "/runtime/export/packages/pkg-review/service-traces/trace%3Arun"
    });
    expect(display?.fields).toEqual(
      expect.arrayContaining([
        expect.objectContaining({
          label: "source",
          value: "BACKEND_RUNTIME_EXPORT_PACKAGE"
        }),
        expect.objectContaining({
          label: "service",
          value: "svc-run / COMPUTE_SERVICE"
        }),
        expect.objectContaining({ label: "task", value: "task-run" }),
        expect.objectContaining({ label: "compute node", value: "sat-00003" }),
        expect.objectContaining({
          label: "input",
          value: "flow-in / route-in"
        }),
        expect.objectContaining({
          label: "output",
          value: "flow-out / route-out"
        })
      ])
    );
    expect(
      buildDataPanelExportServiceTraceItemStatus(
        display,
        "pkg-review",
        "trace:run",
        false,
        null
      )
    ).toBe(display);
    expect(
      buildDataPanelExportServiceTraceItemStatus(
        display,
        "pkg-review",
        "trace:queued",
        true,
        null
      )
    ).toMatchObject({
      tone: "pending",
      statusLabel: "loading package service trace",
      summaryLabel: "pkg-review / trace:queued",
      detailHref: null
    });
    expect(
      buildDataPanelExportServiceTraceItemStatus(
        display,
        "pkg-review",
        "trace:queued",
        false,
        "HTTP 404"
      )
    ).toMatchObject({
      tone: "error",
      statusLabel: "package service trace load failed",
      summaryLabel: "pkg-review / trace:queued",
      detailHref:
        "/runtime/export/packages/pkg-review/service-traces/trace%3Aqueued"
    });
    expect(
      buildDataPanelExportServiceTraceItemStatus(
        display,
        "pkg-other",
        "trace:run",
        false,
        null
      )
    ).toBeNull();
  });

  it("compares package service trace items with live runtime trace details", () => {
    const packageItem = {
      type: "RUNTIME_EXPORT_SERVICE_TRACE_ITEM_V1",
      version: "v1",
      item_id: "leo_twin.runtime_export_service_trace_item.v1",
      source: "BACKEND_RUNTIME_EXPORT_PACKAGE",
      package_id: "pkg-review",
      artifact_type: "SERVICE_LIFECYCLE_TRACE_EXPORT_V2",
      artifact_source: "BACKEND_RUNTIME_STATUS",
      artifact_policy: "STANDALONE_RUNTIME_EXPORT_ARTIFACT",
      artifact_window_only: true,
      trace_contract_id: "leo_twin.service_lifecycle_trace_contract.v2",
      trace_model: "COMMUNICATION_COMPUTE_COMPONENT_PROXY",
      source_summary: "service_latency_history_v1",
      summary_scope: "SERVICE_LIFECYCLE_TRACE_ITEM",
      trace_id: "trace:run",
      trace: {
        trace_id: "trace:run",
        service_id: "svc-run",
        task_id: "task-run",
        service_class: "COMPUTE_SERVICE",
        input_flow_id: "flow-in",
        output_flow_id: "flow-out",
        input_route_id: "route-in",
        output_route_id: "route-out",
        compute_node_id: "sat-00003",
        input_network_latency_s: 0.12,
        compute_queue_delay_s: 0.02,
        compute_execution_delay_s: 0.4,
        output_network_latency_s: 0.08,
        total_latency_s: 0.62,
        terminal_state: "RUNNING",
        terminal_state_reason: "OUTPUT_NETWORK_PENDING",
        stage_count: 4,
        observed_stage_count: 3,
        pending_stage_count: 1,
        stages: []
      },
      boundary_conditions: [
        "ARTIFACT_WINDOW_ONLY",
        "NO_EVENT_REPLAY",
        "NO_SERVICE_RECOMPUTE",
        "NO_PACKAGE_MUTATION"
      ],
      item_hash:
        "sha256:cdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcd"
    };
    const liveDetail = {
      version: "v2",
      source: "BACKEND_RUNTIME_DETAIL",
      summary_scope: "SERVICE_TRACE_EXACT_DETAIL",
      detail_hash: "sha256:live-trace-detail",
      trace: packageItem.trace,
      correlation: {
        trace_id: "trace:run",
        service_id: "svc-run",
        task_id: "task-run",
        flow_ids: ["flow-in", "flow-out"],
        route_ids: ["route-in", "route-out"],
        user_ids: ["user-0"],
        satellite_ids: ["sat-00003"],
        compute_node_id: "sat-00003",
        route_count: 2,
        user_count: 1,
        satellite_count: 1,
        compute_node_detail_available: true
      },
      routes: [],
      users: [],
      satellites: [],
      compute_node: null
    };

    expect(
      buildDataPanelExportServiceTraceLiveComparisonDisplay(
        packageItem,
        liveDetail
      )
    ).toMatchObject({
      traceId: "trace:run",
      tone: "match",
      statusLabel: "package and live service trace match",
      summaryLabel: "trace:run / matched 17/17 / differences 0"
    });

    const changedDisplay = buildDataPanelExportServiceTraceLiveComparisonDisplay(
      packageItem,
      {
        ...liveDetail,
        trace: {
          ...liveDetail.trace,
          terminal_state: "COMPLETE",
          terminal_state_reason: "TOTAL_LATENCY_OBSERVED",
          total_latency_s: 0.74,
          pending_stage_count: 0,
          observed_stage_count: 4
        }
      }
    );
    expect(changedDisplay).toMatchObject({
      traceId: "trace:run",
      tone: "different",
      statusLabel: "package and live service trace differ",
      summaryLabel: "trace:run / matched 13/17 / differences 4"
    });
    expect(changedDisplay?.rows).toEqual(
      expect.arrayContaining([
        expect.objectContaining({
          field: "terminal",
          packageValue: "RUNNING",
          liveValue: "COMPLETE",
          matches: false
        }),
        expect.objectContaining({
          field: "reason",
          packageValue: "OUTPUT_NETWORK_PENDING",
          liveValue: "TOTAL_LATENCY_OBSERVED",
          matches: false
        }),
        expect.objectContaining({
          field: "total latency",
          packageValue: "620 ms",
          liveValue: "740 ms",
          matches: false
        }),
        expect.objectContaining({
          field: "stage counts",
          packageValue: "3 observed / 1 pending / 4 total",
          liveValue: "4 observed / 0 pending / 4 total",
          matches: false
        })
      ])
    );
    expect(
      buildDataPanelExportServiceTraceLiveComparisonDisplay(packageItem, {
        ...liveDetail,
        trace: { ...liveDetail.trace, trace_id: "trace:other" }
      })
    ).toBeNull();
  });

  it("explains package-live service trace comparison request status", () => {
    const packageItem = {
      type: "RUNTIME_EXPORT_SERVICE_TRACE_ITEM_V1",
      version: "v1",
      item_id: "leo_twin.runtime_export_service_trace_item.v1",
      source: "BACKEND_RUNTIME_EXPORT_PACKAGE",
      package_id: "pkg-review",
      artifact_type: "SERVICE_LIFECYCLE_TRACE_EXPORT_V2",
      artifact_source: "BACKEND_RUNTIME_STATUS",
      artifact_policy: "STANDALONE_RUNTIME_EXPORT_ARTIFACT",
      artifact_window_only: true,
      trace_contract_id: "leo_twin.service_lifecycle_trace_contract.v2",
      trace_model: "COMMUNICATION_COMPUTE_COMPONENT_PROXY",
      source_summary: "service_latency_history_v1",
      summary_scope: "SERVICE_LIFECYCLE_TRACE_ITEM",
      trace_id: "trace:run",
      trace: {
        trace_id: "trace:run",
        service_id: "svc-run",
        task_id: "task-run",
        service_class: "COMPUTE_SERVICE",
        input_flow_id: "flow-in",
        output_flow_id: "flow-out",
        input_route_id: "route-in",
        output_route_id: "route-out",
        compute_node_id: "sat-00003",
        input_network_latency_s: 0.12,
        compute_queue_delay_s: 0.02,
        compute_execution_delay_s: 0.4,
        output_network_latency_s: 0.08,
        total_latency_s: 0.62,
        terminal_state: "RUNNING",
        terminal_state_reason: "OUTPUT_NETWORK_PENDING",
        stage_count: 4,
        observed_stage_count: 3,
        pending_stage_count: 1,
        stages: []
      },
      boundary_conditions: ["ARTIFACT_WINDOW_ONLY"],
      item_hash: "sha256:item"
    };
    const liveDetail = {
      version: "v2",
      source: "BACKEND_RUNTIME_DETAIL",
      summary_scope: "SERVICE_TRACE_EXACT_DETAIL",
      detail_hash: "sha256:live-trace-detail",
      trace: packageItem.trace,
      correlation: {
        trace_id: "trace:run",
        service_id: "svc-run",
        task_id: "task-run",
        flow_ids: ["flow-in", "flow-out"],
        route_ids: ["route-in", "route-out"],
        user_ids: [],
        satellite_ids: ["sat-00003"],
        compute_node_id: "sat-00003",
        route_count: 2,
        user_count: 0,
        satellite_count: 1,
        compute_node_detail_available: true
      },
      routes: [],
      users: [],
      satellites: [],
      compute_node: null
    };
    const comparison = buildDataPanelExportServiceTraceLiveComparisonDisplay(
      packageItem,
      liveDetail
    );

    expect(
      buildDataPanelExportServiceTraceLiveComparisonStatus(
        comparison,
        packageItem,
        null,
        liveDetail,
        { entityId: "trace:run", loading: false, error: null }
      )
    ).toBeNull();
    expect(
      buildDataPanelExportServiceTraceLiveComparisonStatus(
        null,
        null,
        {
          packageId: "pkg-review",
          traceId: "trace:run",
          tone: "pending",
          statusLabel: "loading package service trace",
          summaryLabel: "pkg-review / trace:run",
          fields: [],
          detailHref: null
        },
        null,
        { entityId: "trace:run", loading: true, error: null }
      )
    ).toMatchObject({
      tone: "pending",
      statusLabel: "waiting for package service trace",
      summaryLabel: "package trace:run / live trace:run"
    });
    expect(
      buildDataPanelExportServiceTraceLiveComparisonStatus(
        null,
        packageItem,
        null,
        null,
        { entityId: "trace:run", loading: false, error: "HTTP 404" }
      )
    ).toMatchObject({
      tone: "error",
      statusLabel: "live service trace unavailable",
      summaryLabel: "package trace:run / live trace:run",
      notes: ["HTTP 404"]
    });
    expect(
      buildDataPanelExportServiceTraceLiveComparisonStatus(
        null,
        packageItem,
        null,
        { ...liveDetail, trace: { ...liveDetail.trace, trace_id: "trace:other" } },
        { entityId: "trace:other", loading: false, error: null }
      )
    ).toMatchObject({
      tone: "different",
      statusLabel: "service trace id mismatch",
      summaryLabel: "package trace:run / live trace:other"
    });
  });

  it("builds package-live service trace comparison review save records", () => {
    const packageItem = {
      type: "RUNTIME_EXPORT_SERVICE_TRACE_ITEM_V1",
      version: "v1",
      item_id: "leo_twin.runtime_export_service_trace_item.v1",
      source: "BACKEND_RUNTIME_EXPORT_PACKAGE",
      package_id: "pkg-review",
      artifact_type: "SERVICE_LIFECYCLE_TRACE_EXPORT_V2",
      artifact_source: "BACKEND_RUNTIME_STATUS",
      artifact_policy: "STANDALONE_RUNTIME_EXPORT_ARTIFACT",
      artifact_window_only: true,
      trace_contract_id: "leo_twin.service_lifecycle_trace_contract.v2",
      trace_model: "COMMUNICATION_COMPUTE_COMPONENT_PROXY",
      source_summary: "service_latency_history_v1",
      summary_scope: "SERVICE_LIFECYCLE_TRACE_ITEM",
      trace_id: "trace:run",
      trace: {
        trace_id: "trace:run",
        service_id: "svc-run",
        task_id: "task-run",
        service_class: "COMPUTE_SERVICE",
        input_flow_id: "flow-in",
        output_flow_id: "flow-out",
        input_route_id: "route-in",
        output_route_id: "route-out",
        compute_node_id: "sat-00003",
        input_network_latency_s: 0.12,
        compute_queue_delay_s: 0.02,
        compute_execution_delay_s: 0.4,
        output_network_latency_s: 0.08,
        total_latency_s: 0.62,
        terminal_state: "RUNNING",
        terminal_state_reason: "OUTPUT_NETWORK_PENDING",
        stage_count: 4,
        observed_stage_count: 3,
        pending_stage_count: 1,
        stages: []
      },
      boundary_conditions: ["ARTIFACT_WINDOW_ONLY"],
      item_hash: "sha256:package-trace"
    };
    const liveDetail = {
      version: "v2",
      source: "BACKEND_RUNTIME_DETAIL",
      summary_scope: "SERVICE_TRACE_EXACT_DETAIL",
      detail_hash: "sha256:live-trace-detail",
      trace: {
        ...packageItem.trace,
        terminal_state: "COMPLETE",
        terminal_state_reason: "TOTAL_LATENCY_OBSERVED",
        total_latency_s: 0.74,
        observed_stage_count: 4,
        pending_stage_count: 0
      },
      correlation: {
        trace_id: "trace:run",
        service_id: "svc-run",
        task_id: "task-run",
        flow_ids: ["flow-in", "flow-out"],
        route_ids: ["route-in", "route-out"],
        user_ids: [],
        satellite_ids: ["sat-00003"],
        compute_node_id: "sat-00003",
        route_count: 2,
        user_count: 0,
        satellite_count: 1,
        compute_node_detail_available: true
      },
      routes: [],
      users: [],
      satellites: [],
      compute_node: null
    };
    const comparison = buildDataPanelExportServiceTraceLiveComparisonDisplay(
      packageItem,
      liveDetail
    );

    expect(
      buildDataPanelExportServiceTraceComparisonReviewRecord(
        packageItem,
        liveDetail,
        comparison
      )
    ).toMatchObject({
      trace_id: "trace:run",
      comparison_status: "DIFFERENT",
      package_trace_item_hash: "sha256:package-trace",
      live_trace_detail_hash: "sha256:live-trace-detail",
      matched_field_count: 13,
      different_field_count: 4,
      compared_fields: expect.arrayContaining([
        "compute_node",
        "input_flow",
        "output_route",
        "total_latency",
        "stage_counts"
      ]),
      different_fields: ["terminal", "reason", "total_latency", "stage_counts"],
      status_reason: "FIELDS_DIFFER"
    });
    expect(
      buildDataPanelExportServiceTraceComparisonReviewSaveStatus(
        comparison,
        packageItem
      )
    ).toMatchObject({
      traceId: "trace:run",
      tone: "ready",
      buttonLabel: "save trace report",
      disabled: false
    });
    expect(
      buildDataPanelExportServiceTraceComparisonReviewSaveStatus(
        comparison,
        packageItem,
        { pendingTraceId: "trace:run" }
      )
    ).toMatchObject({
      tone: "pending",
      buttonLabel: "saving report",
      disabled: true
    });
    expect(
      buildDataPanelExportServiceTraceComparisonReviewSaveStatus(
        comparison,
        packageItem,
        { error: "HTTP 500" }
      )
    ).toMatchObject({
      tone: "error",
      detailLabel: "HTTP 500"
    });
    expect(
      buildDataPanelExportServiceTraceComparisonReviewSaveStatus(
        comparison,
        packageItem,
        { reportHash: "sha256:report" }
      )
    ).toMatchObject({
      tone: "success",
      detailLabel: "saved report"
    });
  });

  it("compares package route details with live runtime route details", () => {
    const packageRoute = _runtimeExportRouteIndexRoute("route-a", true);
    const packageItem = {
      type: "RUNTIME_EXPORT_ROUTE_DETAIL_ITEM_V1",
      version: "v1",
      item_id: "leo_twin.runtime_export_route_detail_item.v1",
      source: "BACKEND_RUNTIME_EXPORT_PACKAGE",
      package_id: "pkg-review",
      index_id: "leo_twin.runtime_export_route_detail_index.v1",
      route_detail_index_hash:
        "sha256:cdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcd",
      route_id: "route-a",
      route: packageRoute,
      item_hash:
        "sha256:abababababababababababababababababababababababababababababababab"
    };

    expect(
      buildDataPanelExportRouteLiveComparisonDisplay(packageItem, packageRoute)
    ).toMatchObject({
      routeId: "route-a",
      tone: "match",
      statusLabel: "package and live route match",
      summaryLabel: "route-a / matched 12/12 / differences 0"
    });

    const changedLiveRoute = {
      ...packageRoute,
      latency_s: 0.25,
      bottleneck_component: "CAPACITY",
      bottleneck_reason_label: "Route capacity pressure"
    };
    const changedDisplay = buildDataPanelExportRouteLiveComparisonDisplay(
      packageItem,
      changedLiveRoute
    );
    expect(changedDisplay).toMatchObject({
      routeId: "route-a",
      tone: "different",
      statusLabel: "package and live route differ",
      summaryLabel: "route-a / matched 10/12 / differences 2"
    });
    expect(changedDisplay?.rows).toEqual(
      expect.arrayContaining([
        expect.objectContaining({
          field: "latency",
          packageValue: "100 ms",
          liveValue: "250 ms",
          matches: false
        }),
        expect.objectContaining({
          field: "bottleneck",
          packageValue: "LOSS_PROXY",
          liveValue: "CAPACITY",
          matches: false
        })
      ])
    );
    expect(
      buildDataPanelExportRouteLiveComparisonDisplay(packageItem, {
        ...packageRoute,
        route_id: "route-b"
      })
    ).toBeNull();
  });

  it("explains package-live route comparison request status", () => {
    const packageRoute = _runtimeExportRouteIndexRoute("route-a", true);
    const packageItem = {
      type: "RUNTIME_EXPORT_ROUTE_DETAIL_ITEM_V1",
      version: "v1",
      item_id: "leo_twin.runtime_export_route_detail_item.v1",
      source: "BACKEND_RUNTIME_EXPORT_PACKAGE",
      package_id: "pkg-review",
      index_id: "leo_twin.runtime_export_route_detail_index.v1",
      route_detail_index_hash:
        "sha256:cdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcd",
      route_id: "route-a",
      route: packageRoute,
      item_hash:
        "sha256:abababababababababababababababababababababababababababababababab"
    };
    const comparison = buildDataPanelExportRouteLiveComparisonDisplay(
      packageItem,
      packageRoute
    );

    expect(
      buildDataPanelExportRouteLiveComparisonStatus(
        comparison,
        packageItem,
        null,
        packageRoute,
        { entityId: "route-a", loading: false, error: null }
      )
    ).toBeNull();
    expect(
      buildDataPanelExportRouteLiveComparisonStatus(
        null,
        null,
        {
          packageId: "pkg-review",
          routeId: "route-a",
          tone: "pending",
          statusLabel: "loading package route detail",
          summaryLabel: "pkg-review / route-a",
          fields: [],
          detailHref: null
        },
        null,
        { entityId: "route-a", loading: true, error: null }
      )
    ).toMatchObject({
      tone: "pending",
      statusLabel: "waiting for package route detail",
      summaryLabel: "package route-a / live route-a"
    });
    expect(
      buildDataPanelExportRouteLiveComparisonStatus(
        null,
        packageItem,
        null,
        null,
        { entityId: "route-a", loading: false, error: "HTTP 404" }
      )
    ).toMatchObject({
      tone: "error",
      statusLabel: "live route detail unavailable",
      summaryLabel: "package route-a / live route-a",
      notes: ["HTTP 404"]
    });
    expect(
      buildDataPanelExportRouteLiveComparisonStatus(
        null,
        packageItem,
        null,
        { ...packageRoute, route_id: "route-b" },
        { entityId: "route-b", loading: false, error: null }
      )
    ).toMatchObject({
      tone: "different",
      statusLabel: "route id mismatch",
      summaryLabel: "package route-a / live route-b"
    });
  });

  it("builds package-live route comparison review save records", () => {
    const packageRoute = _runtimeExportRouteIndexRoute("route-a", true);
    const packageItem = {
      type: "RUNTIME_EXPORT_ROUTE_DETAIL_ITEM_V1",
      version: "v1",
      item_id: "leo_twin.runtime_export_route_detail_item.v1",
      source: "BACKEND_RUNTIME_EXPORT_PACKAGE",
      package_id: "pkg-review",
      index_id: "leo_twin.runtime_export_route_detail_index.v1",
      route_detail_index_hash:
        "sha256:cdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcd",
      route_id: "route-a",
      route: packageRoute,
      item_hash:
        "sha256:abababababababababababababababababababababababababababababababab"
    };
    const changedLiveRoute = {
      ...packageRoute,
      detail_hash:
        "sha256:cdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcd",
      latency_s: 0.25,
      bottleneck_component: "CAPACITY",
      bottleneck_reason: "ROUTE_CAPACITY_PRESSURE",
      bottleneck_reason_label: "Route capacity pressure"
    };
    const comparison = buildDataPanelExportRouteLiveComparisonDisplay(
      packageItem,
      changedLiveRoute
    );

    expect(
      buildDataPanelExportRouteComparisonReviewRecord(
        packageItem,
        changedLiveRoute,
        comparison
      )
    ).toEqual({
      route_id: "route-a",
      comparison_status: "DIFFERENT",
      package_route_detail_hash:
        "sha256:abababababababababababababababababababababababababababababababab",
      live_route_detail_hash:
        "sha256:cdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcd",
      matched_field_count: 10,
      different_field_count: 2,
      compared_fields: [
        "availability",
        "business",
        "flow",
        "source_destination",
        "selected_satellite",
        "primary_next_hop",
        "path",
        "capacity_demand",
        "latency",
        "loss",
        "pressure",
        "bottleneck"
      ],
      different_fields: ["latency", "bottleneck"],
      status_reason: "FIELDS_DIFFER",
      operator_note: "Saved from dashboard package-vs-live route comparison."
    });
    expect(
      buildDataPanelExportRouteComparisonReviewSaveStatus(comparison, packageItem)
    ).toMatchObject({
      routeId: "route-a",
      tone: "ready",
      buttonLabel: "save review report",
      disabled: false
    });
    expect(
      buildDataPanelExportRouteComparisonReviewSaveStatus(comparison, packageItem, {
        pendingRouteId: "route-a"
      })
    ).toMatchObject({
      tone: "pending",
      buttonLabel: "saving report",
      disabled: true
    });
    expect(
      buildDataPanelExportRouteComparisonReviewSaveStatus(comparison, packageItem, {
        reportHash:
          "sha256:1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
      })
    ).toMatchObject({
      tone: "success",
      detailLabel: "saved 1234567890ab"
    });
  });

  it("summarizes runtime export manifests with catalog and diagnostics integrity", () => {
    const display = buildDataPanelExportManifestInspectorDisplay(
      {
        version: "v1",
        source: "BACKEND_RUNTIME_STATUS",
        manifest_id: "leo_twin.runtime_reproducibility_manifest.v1",
        session_id: "integration-demo-4321",
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
          "sha256:abababababababababababababababababababababababababababababababab",
        artifact_policy: "LIVE_STATUS_MANIFEST_ONLY",
        artifacts: [
          {
            name: "events.jsonl",
            format: "jsonl",
            status: "AVAILABLE_FOR_BATCH_EXPORT",
            source: "MetricsCollector.write_outputs"
          },
          {
            name: "manifest.json",
            format: "json",
            status: "AVAILABLE_FOR_BATCH_EXPORT",
            source: "runtime_export"
          }
        ],
        artifact_count: 2
      },
      "pkg-review",
      {
        version: "v1",
        source: "BACKEND_RUNTIME_EXPORT_CATALOG",
        catalog_scope: "PERSISTED_EXPORT_PACKAGES",
        catalog_file: "artifacts/runtime_exports/runtime_export_catalog_v1.json",
        export_root: "artifacts/runtime_exports",
        record_count: 1,
        catalog_hash:
          "sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
        latest_export: null,
        records: [
          {
            catalog_key: "ARCHIVE:pkg-review",
            export_type: "ARCHIVE",
            package_id: "pkg-review",
            package_dir: "artifacts/runtime_exports/pkg-review",
            relative_package_dir: "pkg-review",
            file_count: 2,
            manifest_hash:
              "sha256:abababababababababababababababababababababababababababababababab",
            current_sim_time: 120,
            processed_event_count: 4096,
            files: [
              {
                name: "events",
                filename: "events.jsonl",
                bytes: 2048,
                sha256:
                  "sha256:eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
              },
              {
                name: "manifest",
                filename: "manifest.json",
                bytes: 512,
                sha256:
                  "sha256:ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
              }
            ]
          }
        ]
      },
      {
        type: "RUNTIME_EXPORT_DIAGNOSTICS_BUNDLE_V1",
        version: "v1",
        bundle_id: "leo_twin.runtime_export_diagnostics_bundle.v1",
        source: "BACKEND_RUNTIME_EXPORT",
        diagnostics_scope: "RESULT_PACKAGE_OPERATOR_REVIEW",
        package: {
          package_id: "pkg-review",
          package_dir: "artifacts/runtime_exports/pkg-review",
          package_complete: true,
          review_status: "REVIEW_READY",
          contract_id: "leo_twin.result_package_contract.v1"
        },
        runtime: {
          lifecycle_state: "STOPPED",
          current_sim_time: 120,
          processed_event_count: 4096,
          queued_event_count: 0
        },
        reproducibility: {
          manifest_id: "leo_twin.runtime_reproducibility_manifest.v1",
          manifest_ok: true,
          manifest_hash:
            "sha256:abababababababababababababababababababababababababababababababab",
          config_hash: "sha256:config",
          generated_config_hash: "sha256:generated",
          review_summary_hash: "sha256:summary"
        },
        artifact_health: {
          artifact_count: 2,
          artifact_filenames: ["events.jsonl", "manifest.json"],
          required_filenames: ["events.jsonl", "manifest.json"],
          recommended_filenames: [],
          present_required_filenames: ["events.jsonl", "manifest.json"],
          missing_required_filenames: [],
          present_recommended_filenames: [],
          missing_recommended_filenames: []
        },
        model_boundaries: {
          event_kernel_policy: "NO_EVENT_KERNEL_BEHAVIOR_CHANGE",
          packet_level_simulation: false,
          external_simulators: [],
          forbidden_external_integrations: ["STK", "EXATA", "AFSIM", "DDS"],
          diagnostics_policy: "Deterministic package index only."
        },
        findings: [],
        finding_count: 0,
        recommended_next_actions: [],
        diagnostics_hash: "sha256:diagnostics"
      }
    );

    expect(display).toMatchObject({
      packageId: "pkg-review",
      tone: "match",
      statusLabel: "manifest 一致",
      summaryLabel:
        "pkg-review / LIVE_STATUS_MANIFEST_ONLY / 2 artifacts / abababababab",
      hashLabels: [
        "manifest abababababab",
        "scenario 111111111111",
        "config 222222222222",
        "generated 333333333333",
        "metrics 444444444444",
        "runtime 555555555555"
      ],
      integrityLabels: [
        "manifest id OK",
        "diagnostics 一致",
        "catalog manifest ffffffffffff",
        "catalog artifact 缺失 0"
      ],
      artifactRows: [
        {
          name: "events.jsonl",
          statusLabel: "jsonl / AVAILABLE_FOR_BATCH_EXPORT",
          catalogPresent: true
        },
        {
          name: "manifest.json",
          statusLabel: "json / AVAILABLE_FOR_BATCH_EXPORT",
          catalogPresent: true
        }
      ],
      manifestHref: "/runtime/export/packages/pkg-review/manifest"
    });
    expect(display?.artifactRows[0]?.sourceLabel).toContain("eeeeeeeeeeee");
    expect(
      buildDataPanelExportManifestInspectorStatus(display, "pkg-review", false, null)
    ).toBe(display);
    expect(
      buildDataPanelExportManifestInspectorStatus(display, "pkg-next", true, null)
    ).toEqual({
      tone: "pending",
      statusLabel: "正在加载 manifest",
      summaryLabel: "pkg-next",
      hashLabels: ["只读 manifest", "不执行重放"],
      integrityLabels: [],
      artifactRows: [],
      manifestHref: null
    });
    expect(
      buildDataPanelExportManifestInspectorStatus(display, "pkg-next", false, "HTTP 404")
    ).toMatchObject({
      tone: "error",
      statusLabel: "manifest 加载失败",
      summaryLabel: "pkg-next",
      hashLabels: ["HTTP 404"],
      manifestHref: null
    });
  });

  it("summarizes runtime export reproducibility boundary evidence", () => {
    const boundary = {
      type: "RUNTIME_EXPORT_REPRODUCIBILITY_BOUNDARY_V1",
      version: "v1",
      boundary_id: "leo_twin.runtime_export_reproducibility_boundary.v1",
      source: "BACKEND_RUNTIME_EXPORT",
      boundary_scope: "RESULT_PACKAGE_REPRODUCIBILITY_AND_RESTORE_BOUNDARY",
      manifest_id: "leo_twin.runtime_reproducibility_manifest.v1",
      control_config_hash:
        "sha256:2222222222222222222222222222222222222222222222222222222222222222",
      generated_config_hash:
        "sha256:3333333333333333333333333333333333333333333333333333333333333333",
      runtime_state_hash:
        "sha256:5555555555555555555555555555555555555555555555555555555555555555",
      metrics_summary_hash:
        "sha256:4444444444444444444444444444444444444444444444444444444444444444",
      deterministic_replay_evidence: true,
      runtime_deterministic_replay_enabled: false,
      restore_scope: "CONFIG_ONLY",
      compare_scope: "CONFIG_AND_GENERATED_CONFIG",
      read_scope: "PERSISTED_ARTIFACTS_ONLY",
      event_kernel_policy: "NO_EVENT_KERNEL_BEHAVIOR_CHANGE",
      event_replay_restore: false,
      live_event_replay_restore: false,
      recompute_on_read: false,
      route_recomputation: false,
      service_recomputation: false,
      package_mutation_on_read: false,
      packet_capture: false,
      packet_level_simulation: false,
      external_simulators: false,
      forbidden_external_integrations: ["STK", "EXATA", "AFSIM", "DDS"],
      required_evidence_artifacts: [
        "config_snapshot.json",
        "events.jsonl",
        "metrics.csv",
        "summary.json",
        "manifest.json"
      ],
      optional_evidence_artifacts: [
        "service_lifecycle_trace_v2.json",
        "route_detail_index_v1.json",
        "review_summary_v1.json",
        "diagnostics_bundle_v1.json"
      ],
      route_detail_export: {
        policy: "EXPORT_ROUTE_DETAIL_INDEX_WINDOW",
        route_detail_limit: 5000,
        route_count: 20,
        indexed_route_count: 12,
        hidden_route_count: 8,
        artifact_window_only: true
      },
      service_trace_export: {
        policy: "EXPORT_SERVICE_TRACE_WINDOW",
        service_trace_limit: 5000,
        service_count: 7,
        exported_trace_count: 5,
        hidden_trace_count: 2,
        artifact_window_only: true
      },
      boundary_conditions: [
        "DETERMINISTIC_ARTIFACT_REPLAY_EVIDENCE",
        "CONFIG_ONLY_RESTORE",
        "NO_LIVE_EVENT_REPLAY_RESTORE",
        "NO_RECOMPUTE_ON_COMPARE_OR_READ",
        "NO_PACKAGE_MUTATION_ON_READ"
      ],
      boundary_hash:
        "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
    };

    const display = buildDataPanelExportReproducibilityBoundaryDisplay(
      {
        version: "v1",
        source: "BACKEND_RUNTIME_STATUS",
        manifest_id: "leo_twin.runtime_reproducibility_manifest.v1",
        session_id: "integration-demo-4321",
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
          "sha256:abababababababababababababababababababababababababababababababab",
        artifact_policy: "LIVE_STATUS_MANIFEST_ONLY",
        artifacts: [],
        runtime_export_reproducibility_boundary_v1: boundary
      },
      {
        type: "RUNTIME_EXPORT_REVIEW_SUMMARY_V1",
        version: "v1",
        summary_id: "leo_twin.runtime_export_review_summary.v1",
        source: "BACKEND_RUNTIME_EXPORT",
        summary_scope: "USER_READABLE_RESULT_PACKAGE_REVIEW",
        package_id: "pkg-review",
        package_dir: "artifacts/runtime_exports/pkg-review",
        review_status: "REVIEW_READY",
        scenario: {
          seed: 4321,
          satellite_count: 72,
          user_count: 20,
          compute_node_count: 2,
          duration_seconds: 120
        },
        runtime: {
          lifecycle_state: "STOPPED",
          current_sim_time: 120,
          processed_event_count: 4096,
          queued_event_count: 0
        },
        reproducibility: {
          manifest_id: "leo_twin.runtime_reproducibility_manifest.v1",
          manifest_hash:
            "sha256:abababababababababababababababababababababababababababababababab",
          config_hash: "sha256:config",
          generated_config_hash: "sha256:generated",
          boundary_hash:
            "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
          event_kernel_policy: "NO_EVENT_KERNEL_BEHAVIOR_CHANGE"
        },
        reproducibility_boundary: boundary,
        artifacts: {
          artifact_count: 8,
          artifact_filenames: ["manifest.json"],
          required_filenames: ["manifest.json"],
          missing_required_filenames: [],
          service_lifecycle_trace_exported: true,
          review_summary_exported: true
        },
        review_notes: [],
        summary_hash:
          "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
      },
      {
        type: "RUNTIME_EXPORT_DIAGNOSTICS_BUNDLE_V1",
        version: "v1",
        bundle_id: "leo_twin.runtime_export_diagnostics_bundle.v1",
        source: "BACKEND_RUNTIME_EXPORT",
        diagnostics_scope: "RESULT_PACKAGE_OPERATOR_REVIEW",
        package: {
          package_id: "pkg-review",
          package_dir: "artifacts/runtime_exports/pkg-review",
          package_complete: true,
          review_status: "REVIEW_READY",
          contract_id: "leo_twin.result_package_contract.v1"
        },
        runtime: {
          lifecycle_state: "STOPPED",
          current_sim_time: 120,
          processed_event_count: 4096,
          queued_event_count: 0
        },
        reproducibility: {
          manifest_id: "leo_twin.runtime_reproducibility_manifest.v1",
          manifest_ok: true,
          manifest_hash:
            "sha256:abababababababababababababababababababababababababababababababab",
          config_hash: "sha256:config",
          generated_config_hash: "sha256:generated",
          review_summary_hash: "sha256:summary",
          boundary_hash:
            "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
        },
        reproducibility_boundary: boundary,
        artifact_health: {
          artifact_count: 8,
          artifact_filenames: ["manifest.json"],
          required_filenames: ["manifest.json"],
          recommended_filenames: [],
          present_required_filenames: ["manifest.json"],
          missing_required_filenames: [],
          present_recommended_filenames: [],
          missing_recommended_filenames: []
        },
        model_boundaries: {
          event_kernel_policy: "NO_EVENT_KERNEL_BEHAVIOR_CHANGE",
          packet_level_simulation: false,
          external_simulators: [],
          forbidden_external_integrations: ["STK", "EXATA", "AFSIM", "DDS"],
          event_replay_restore: false,
          route_recomputation: false,
          service_recomputation: false,
          diagnostics_policy: "Deterministic package index only."
        },
        findings: [],
        finding_count: 0,
        recommended_next_actions: [],
        diagnostics_hash: "sha256:diagnostics"
      },
      "pkg-review"
    );

    expect(display).toMatchObject({
      packageId: "pkg-review",
      tone: "match",
      statusLabel: "复现边界一致",
      summaryLabel: "pkg-review / CONFIG_ONLY / CONFIG_AND_GENERATED_CONFIG / bbbbbbbbbbbb",
      scopeLabels: [
        "restore CONFIG_ONLY",
        "compare CONFIG_AND_GENERATED_CONFIG",
        "read PERSISTED_ARTIFACTS_ONLY",
        "manifest leo_twin.runtime_reproducibility_manifest.v1",
        "boundary bbbbbbbbbbbb",
        "hash 一致"
      ],
      boundaryHref: "/runtime/export/packages/pkg-review/manifest"
    });
    expect(display?.boundaryLabels).toContain("no recompute on read");
    expect(display?.boundaryLabels).toContain("no package mutation on read");
    expect(display?.windowLabels).toContain("routes 12/20");
    expect(display?.windowLabels).toContain("hidden traces 2");
    expect(display?.conditionLabels).toContain("NO_RECOMPUTE_ON_COMPARE_OR_READ");
  });

  it("aligns compare and restore preflight with reproducibility boundary evidence", () => {
    const boundary = _runtimeExportReproducibilityBoundary();
    const display = buildDataPanelExportBoundaryAlignmentDisplay(
      {
        version: "v1",
        source: "BACKEND_RUNTIME_STATUS",
        manifest_id: "leo_twin.runtime_reproducibility_manifest.v1",
        session_id: "integration-demo-4321",
        scenario_hash: "sha256:scenario",
        control_config_hash: "sha256:control",
        generated_config_hash: "sha256:generated",
        metrics_summary_hash: "sha256:metrics",
        runtime_state_hash: "sha256:runtime",
        manifest_hash: "sha256:manifest",
        artifact_policy: "LIVE_STATUS_MANIFEST_ONLY",
        artifacts: [],
        runtime_export_reproducibility_boundary_v1: boundary
      },
      {
        type: "RUNTIME_EXPORT_REVIEW_SUMMARY_V1",
        version: "v1",
        summary_id: "leo_twin.runtime_export_review_summary.v1",
        source: "BACKEND_RUNTIME_EXPORT",
        summary_scope: "USER_READABLE_RESULT_PACKAGE_REVIEW",
        package_id: "pkg-review",
        package_dir: "artifacts/runtime_exports/pkg-review",
        review_status: "REVIEW_READY",
        scenario: {
          seed: 4321,
          satellite_count: 72,
          user_count: 20,
          compute_node_count: 2,
          duration_seconds: 120
        },
        runtime: {
          lifecycle_state: "STOPPED",
          current_sim_time: 120,
          processed_event_count: 4096,
          queued_event_count: 0
        },
        reproducibility: {
          manifest_id: "leo_twin.runtime_reproducibility_manifest.v1",
          manifest_hash: "sha256:manifest",
          config_hash: "sha256:config",
          generated_config_hash: "sha256:generated",
          boundary_hash: boundary.boundary_hash,
          event_kernel_policy: "NO_EVENT_KERNEL_BEHAVIOR_CHANGE"
        },
        reproducibility_boundary: boundary,
        artifacts: {
          artifact_count: 8,
          artifact_filenames: ["manifest.json"],
          required_filenames: ["manifest.json"],
          missing_required_filenames: [],
          service_lifecycle_trace_exported: true,
          review_summary_exported: true
        },
        review_notes: [],
        summary_hash: "sha256:summary"
      },
      {
        type: "RUNTIME_EXPORT_DIAGNOSTICS_BUNDLE_V1",
        version: "v1",
        bundle_id: "leo_twin.runtime_export_diagnostics_bundle.v1",
        source: "BACKEND_RUNTIME_EXPORT",
        diagnostics_scope: "RESULT_PACKAGE_OPERATOR_REVIEW",
        package: {
          package_id: "pkg-review",
          package_dir: "artifacts/runtime_exports/pkg-review",
          package_complete: true,
          review_status: "REVIEW_READY",
          contract_id: "leo_twin.result_package_contract.v1"
        },
        runtime: {
          lifecycle_state: "STOPPED",
          current_sim_time: 120,
          processed_event_count: 4096,
          queued_event_count: 0
        },
        reproducibility: {
          manifest_id: "leo_twin.runtime_reproducibility_manifest.v1",
          manifest_ok: true,
          manifest_hash: "sha256:manifest",
          config_hash: "sha256:config",
          generated_config_hash: "sha256:generated",
          review_summary_hash: "sha256:summary",
          boundary_hash: boundary.boundary_hash
        },
        reproducibility_boundary: boundary,
        artifact_health: {
          artifact_count: 8,
          artifact_filenames: ["manifest.json"],
          required_filenames: ["manifest.json"],
          recommended_filenames: [],
          present_required_filenames: ["manifest.json"],
          missing_required_filenames: [],
          present_recommended_filenames: [],
          missing_recommended_filenames: []
        },
        model_boundaries: {
          event_kernel_policy: "NO_EVENT_KERNEL_BEHAVIOR_CHANGE",
          packet_level_simulation: false,
          external_simulators: [],
          forbidden_external_integrations: ["STK", "EXATA", "AFSIM", "DDS"],
          diagnostics_policy: "Deterministic package index only."
        },
        findings: [],
        finding_count: 0,
        recommended_next_actions: [],
        diagnostics_hash: "sha256:diagnostics"
      },
      {
        version: "v1",
        source: "BACKEND_RUNTIME_EXPORT_COMPARE",
        comparison_scope: "CONFIG_AND_GENERATED_CONFIG",
        package_id: "pkg-review",
        compatibility: "MATCH",
        same_config: true,
        same_generated_config: true,
        same_manifest_hash: true,
        package_manifest_hash: "sha256:manifest",
        current_manifest_hash: "sha256:manifest",
        diff_count: 0,
        diff_limit: 100,
        diff_truncated: false,
        sections: [],
        differences: [],
        compare_hash: "sha256:comparehash"
      },
      {
        version: "v1",
        source: "BACKEND_RUNTIME_EXPORT_RESTORE_PREFLIGHT",
        preflight_scope: "CONFIG_RESTORE_PREVIEW_ONLY",
        package_id: "pkg-review",
        readiness: "NO_CHANGE",
        can_restore: true,
        requires_user_confirmation: false,
        would_mutate_current_runtime: false,
        would_write_config_files: false,
        would_reset_runtime_session: false,
        would_stop_live_streams: false,
        current_lifecycle_state: "STOPPED",
        package_config_hash: "sha256:config",
        current_config_hash: "sha256:config",
        same_config: true,
        same_generated_config: true,
        config_diff_count: 0,
        generated_config_diff_count: 0,
        compare_hash: "sha256:comparehash",
        blocked_reasons: [],
        warnings: [],
        next_action: "NO_RESTORE_REQUIRED",
        preflight_hash: "sha256:preflighthash"
      },
      "pkg-review"
    );

    expect(display).toMatchObject({
      packageId: "pkg-review",
      tone: "match",
      statusLabel: "恢复判断有边界证据",
      summaryLabel: "pkg-review / boundary bbbbbbbbbbbb / warnings 0",
      evidenceLabels: [
        "boundary bbbbbbbbbbbb",
        "hash 一致",
        "restore CONFIG_ONLY",
        "compare CONFIG_AND_GENERATED_CONFIG",
        "read PERSISTED_ARTIFACTS_ONLY"
      ],
      warningLabels: []
    });
    expect(display?.compareLabels).toContain("compare CONFIG_AND_GENERATED_CONFIG");
    expect(display?.restoreLabels).toContain("preflight CONFIG_RESTORE_PREVIEW_ONLY");
  });

  it("warns when compare and restore preflight are missing boundary evidence", () => {
    const display = buildDataPanelExportBoundaryAlignmentDisplay(
      null,
      null,
      null,
      {
        version: "v1",
        source: "BACKEND_RUNTIME_EXPORT_COMPARE",
        comparison_scope: "CONFIG_AND_GENERATED_CONFIG",
        package_id: "pkg-review",
        compatibility: "MATCH",
        same_config: true,
        same_generated_config: true,
        same_manifest_hash: true,
        package_manifest_hash: "sha256:manifest",
        current_manifest_hash: "sha256:manifest",
        diff_count: 0,
        diff_limit: 100,
        diff_truncated: false,
        sections: [],
        differences: [],
        compare_hash: "sha256:comparehash"
      },
      null,
      "pkg-review"
    );

    expect(display).toMatchObject({
      packageId: "pkg-review",
      tone: "different",
      statusLabel: "缺少复现边界",
      summaryLabel: "pkg-review / compare+restore 缺少统一边界证据",
      evidenceLabels: ["manifest/review/diagnostics boundary missing"],
      restoreLabels: ["restore preflight not loaded"],
      warningLabels: ["runtime_export_reproducibility_boundary_v1 missing"]
    });
  });

  it("uses backend boundary alignment when artifact boundary is not loaded", () => {
    const backendAlignment = _runtimeExportBoundaryAlignment();
    const display = buildDataPanelExportBoundaryAlignmentDisplay(
      null,
      null,
      null,
      {
        version: "v1",
        source: "BACKEND_RUNTIME_EXPORT_COMPARE",
        comparison_scope: "CONFIG_AND_GENERATED_CONFIG",
        package_id: "pkg-review",
        compatibility: "MATCH",
        same_config: true,
        same_generated_config: true,
        same_manifest_hash: true,
        package_manifest_hash: "sha256:manifest",
        current_manifest_hash: "sha256:manifest",
        diff_count: 0,
        diff_limit: 100,
        diff_truncated: false,
        sections: [],
        differences: [],
        runtime_export_boundary_alignment_v1: backendAlignment,
        compare_hash: "sha256:comparehash"
      },
      null,
      "pkg-review"
    );

    expect(display).toMatchObject({
      packageId: "pkg-review",
      tone: "match",
      statusLabel: "后端边界证据一致",
      summaryLabel: "pkg-review / backend boundary bbbbbbbbbbbb / warnings 0",
      evidenceLabels: [
        "source BACKEND_RUNTIME_EXPORT_COMPARE",
        "backend ALIGNED",
        "alignment cccccccccccc",
        "backend boundary bbbbbbbbbbbb",
        "restore CONFIG_ONLY",
        "compare CONFIG_AND_GENERATED_CONFIG",
        "read PERSISTED_ARTIFACTS_ONLY"
      ],
      warningLabels: []
    });
  });

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
  it("formats backend benchmark validation guardrails", () => {
    const display = buildDataPanelNetworkKpiBenchmarkValidationDisplay({
      version: "v1",
      validation_id: "leo_twin.network_kpi_benchmark_validation.v1",
      source: "NETWORK_KPI_PROVENANCE_V2_AND_METRICS_SUMMARY",
      benchmark_profile: "FLOW_LEVEL_PROXY_RUNTIME_GUARDRAILS",
      provenance_id: "leo_twin.network_kpi_provenance.v2",
      metric_model: "FLOW_LEVEL_PROXY",
      packet_level_simulation: false,
      validation_status: "WARN",
      check_count: 4,
      passed_check_count: 2,
      warning_check_count: 1,
      failed_check_count: 0,
      missing_check_count: 1,
      checks: [
        {
          check_id: "packet_level_guard",
          metric: "network_kpi_provenance_v2.packet_level_simulation",
          current_value: false,
          status: "PASS",
          severity: "FAIL",
          expectation: "packet-level simulation is forbidden",
          source: "network_kpi_provenance_v2",
          explanation: "Flow-level proxy only."
        },
        {
          check_id: "active_demand_throughput_nonzero",
          metric: "network_quality_effective_throughput_mbps",
          current_value: 0,
          status: "WARN",
          severity: "WARN",
          expectation: "throughput should be positive when activity exists",
          source: "metrics_summary",
          explanation: "Flat zero under active demand."
        },
        {
          check_id: "selected_formula_input_coverage",
          metric: "network_kpi_provenance_v2.kpis.formula_trace",
          current_value: 0,
          status: "MISSING",
          severity: "WARN",
          expectation: "selected inputs should be visible",
          source: "network_kpi_provenance_v2.kpis.formula_trace",
          explanation: "No selected inputs."
        }
      ],
      caveats: [
        "Benchmark validation v1 is a deterministic product guardrail.",
        "validation_status=WARN"
      ]
    });

    expect(display).toEqual({
      tone: "different",
      statusLabel: "基准告警",
      summaryLabel: "检查 2/4 通过；WARN 1 / FAIL 0 / 缺数据 1",
      metaLabels: [
        "profile FLOW_LEVEL_PROXY_RUNTIME_GUARDRAILS",
        "模型 流级代理",
        "无包级仿真",
        "provenance leo_twin.net"
      ],
      issueLabels: [
        "WARN network_quality_effective_throughput_mbps: 0 / throughput should be positive when activity exists",
        "MISSING network_kpi_provenance_v2.kpis.formula_trace: 0 / selected inputs should be visible"
      ],
      caveats: [
        "Benchmark validation v1 is a deterministic product guardrail.",
        "validation_status=WARN"
      ]
    });
    expect(buildDataPanelNetworkKpiBenchmarkValidationDisplay(null)).toBeNull();
  });

  it("formats backend network KPI calibration movement evidence", () => {
    const display = buildDataPanelNetworkKpiCalibrationDisplay({
      version: "v1",
      calibration_id: "leo_twin.network_kpi_calibration.v1",
      source: "KPI_TIME_SERIES_V1_AND_METRICS_SUMMARY",
      metric_model: "FLOW_LEVEL_PROXY",
      packet_level_simulation: false,
      sample_count: 2,
      sim_time_start_s: 0,
      sim_time_end_s: 60,
      sim_time_span_s: 60,
      activity_context: {
        active: true,
        requested_route_demand_mbps: 200,
        offered_route_capacity_mbps: 220,
        recent_flow_count: 2,
        available_route_count: 2
      },
      time_driver: {
        source: "SIMULATION_TIME",
        period_s: 120,
        phase: 0.5,
        factor: 0.85,
        loss_proxy_rate: 0.07,
        delay_variation_proxy_s: 0.006
      },
      kpi_count: 4,
      observed_kpi_count: 4,
      time_varying_kpi_count: 3,
      flat_kpi_count: 1,
      zero_latest_kpi_count: 0,
      calibration_status: "TIME_VARYING_OBSERVED",
      kpis: [
        {
          metric: "EFFECTIVE_THROUGHPUT",
          sample_key: "network_effective_throughput_mbps",
          runtime_summary_key: "network_quality_effective_throughput_mbps",
          unit: "Mbps",
          observed: true,
          first_value: 180,
          latest_value: 171,
          minimum_value: 171,
          maximum_value: 180,
          absolute_delta: 9,
          endpoint_delta: -9,
          relative_delta: 0.05,
          latest_is_zero: false,
          variation_status: "TIME_VARYING",
          flat_reason: ""
        },
        {
          metric: "EFFECTIVE_LATENCY",
          sample_key: "network_effective_latency_s",
          runtime_summary_key: "network_quality_effective_latency_avg_s",
          unit: "s",
          observed: true,
          first_value: 0.045,
          latest_value: 0.045,
          minimum_value: 0.045,
          maximum_value: 0.045,
          absolute_delta: 0,
          endpoint_delta: 0,
          relative_delta: 0,
          latest_is_zero: false,
          variation_status: "FLAT_NONZERO",
          flat_reason: "values are non-zero but unchanged"
        }
      ],
      caveats: [
        "Calibration audits movement only; it does not change KPI formulas.",
        "Packet-level simulation remains forbidden."
      ]
    });

    expect(display).toMatchObject({
      tone: "match",
      sourceLabel:
        "leo_twin.network_kpi_calibration.v1 / KPI_TIME_SERIES_V1_AND_METRICS_SUMMARY",
      statusLabel: "已观察到随仿真时间变化",
      summaryLabel: "样本 2 / 时间跨度 1分0秒 / 变化 KPI 3/4",
      metaLabels: [
        "模型 流级代理",
        "无包级仿真",
        "活动需求 200 Mbps",
        "时间驱动 SIMULATION_TIME / phase 0.5 / factor 85%",
        "平坦 1 / 最新零值 0"
      ],
      rows: [
        {
          metric: "EFFECTIVE_THROUGHPUT",
          metricLabel: "有效吞吐 / EFFECTIVE_THROUGHPUT",
          statusLabel: "随时间变化",
          valueLabel: "最新 171 Mbps",
          deltaLabel: "变化 9 Mbps / 端点 -9 Mbps",
          rangeLabel: "范围 171 Mbps - 180 Mbps",
          tone: "observed"
        },
        {
          metric: "EFFECTIVE_LATENCY",
          metricLabel: "有效时延 / EFFECTIVE_LATENCY",
          statusLabel: "非零但平坦",
          valueLabel: "最新 45 ms",
          deltaLabel: "变化 0 ms / 端点 0 ms",
          rangeLabel: "范围 45 ms - 45 ms",
          tone: "missing"
        }
      ],
      caveats: [
        "Calibration audits movement only; it does not change KPI formulas.",
        "Packet-level simulation remains forbidden."
      ]
    });
    expect(buildDataPanelNetworkKpiCalibrationDisplay(null)).toBeNull();
  });

  it("warns when KPI calibration reports flat metrics under active demand", () => {
    const display = buildDataPanelNetworkKpiCalibrationDisplay({
      version: "v1",
      calibration_id: "leo_twin.network_kpi_calibration.v1",
      source: "KPI_TIME_SERIES_V1_AND_METRICS_SUMMARY",
      metric_model: "FLOW_LEVEL_PROXY",
      packet_level_simulation: false,
      sample_count: 2,
      sim_time_start_s: 0,
      sim_time_end_s: 30,
      sim_time_span_s: 30,
      activity_context: {
        active: true,
        requested_route_demand_mbps: 100,
        offered_route_capacity_mbps: 100,
        recent_flow_count: 1,
        available_route_count: 1
      },
      time_driver: {
        source: "SIMULATION_TIME",
        period_s: 120,
        phase: 0.25,
        factor: 0,
        loss_proxy_rate: 0,
        delay_variation_proxy_s: 0
      },
      kpi_count: 4,
      observed_kpi_count: 4,
      time_varying_kpi_count: 0,
      flat_kpi_count: 4,
      zero_latest_kpi_count: 2,
      calibration_status: "FLAT_UNDER_ACTIVITY",
      kpis: [],
      caveats: []
    });

    expect(display?.tone).toBe("different");
    expect(display?.statusLabel).toBe("业务活动下指标仍平坦");
    expect(display?.summaryLabel).toBe("样本 2 / 时间跨度 30秒 / 变化 KPI 0/4");
  });

  it("renders per-KPI backend formula provenance for dashboard inspection", () => {
    const display = buildDataPanelNetworkKpiFormulaInspector(
      {
        version: "v2",
        provenance_id: "leo_twin.network_kpi_provenance.v2",
        source: "BACKEND_METRICS_SUMMARY",
        network_model_contract_id: "leo_twin.network_model_contract.v2",
        network_model_contract_version: "v2",
        metric_model: "FLOW_LEVEL_PROXY",
        packet_level_simulation: false,
        proxy_note: "Flow-level proxy only.",
        provenance_note: "KPI provenance from backend metrics.",
        kpi_count: 2,
        kpis: [
          {
            metric: "EFFECTIVE_THROUGHPUT",
            runtime_summary_key: "network_quality_effective_throughput_mbps",
            current_value: 180,
            status: "OBSERVED",
            display_name: "Effective throughput",
            layer: "NETWORK",
            unit: "Mbps",
            formula_summary:
              "Prefer completed-flow throughput adjusted by deterministic pressure.",
            interpretation: "Flow-level carried throughput estimate.",
            zero_value_semantics: "No completed flow and no available route.",
            packet_level_metric: false,
            observed_source: {
              source: "COMPLETED_FLOW_CAPACITY",
              label: "completed flow capacity"
            },
            zero_reason: null,
            source_fields: [
              {
                field: "network_quality_estimated_delivered_throughput_mbps",
                current_value: 180,
                value_source: "METRICS_SUMMARY"
              },
              {
                field: "network_quality_available_route_demand_mbps",
                current_value: null,
                value_source: "MODEL_OR_CONFIG_STATE"
              }
            ],
            formula_inputs: [
              {
                field: "network_quality_estimated_delivered_throughput_mbps",
                current_value: 180,
                value_source: "METRICS_SUMMARY",
                observed: true,
                selected_for_current_value: true,
                role: "SELECTED_RUNTIME_INPUT",
                selection_reason:
                  "selected by observed_source=COMPLETED_FLOW_CAPACITY and observed in metrics_summary"
              },
              {
                field: "network_quality_available_route_demand_mbps",
                current_value: null,
                value_source: "MODEL_OR_CONFIG_STATE",
                observed: false,
                selected_for_current_value: false,
                role: "DECLARED_SUPPORTING_INPUT",
                selection_reason:
                  "declared by network model contract; current runtime value is not exposed"
              }
            ],
            formula_trace: {
              selection_policy:
                "Prefer completed-flow throughput with deterministic pressure context.",
              runtime_summary_key: "network_quality_effective_throughput_mbps",
              runtime_value_observed: true,
              current_value: 180,
              observed_source: "COMPLETED_FLOW_CAPACITY",
              observed_source_label: "completed flow capacity",
              declared_input_count: 2,
              observed_input_count: 1,
              selected_input_count: 1,
              selected_observed_input_count: 1,
              missing_input_count: 1,
              selected_source_fields: [
                "network_quality_estimated_delivered_throughput_mbps"
              ]
            }
          },
          {
            metric: "EFFECTIVE_LOSS_PROXY",
            runtime_summary_key: "network_quality_effective_loss_proxy_rate",
            current_value: null,
            status: "MISSING_RUNTIME_VALUE",
            display_name: "Effective loss proxy",
            layer: "TRANSPORT",
            unit: "ratio",
            formula_summary: "Maximum of configured and pressure loss proxies.",
            interpretation: "Flow-level loss proxy, not packet loss.",
            zero_value_semantics: "No configured or pressure-driven loss.",
            packet_level_metric: false,
            observed_source: {
              source: "RUNTIME_SUMMARY_KEY",
              label: "Runtime summary field"
            },
            zero_reason: {
              reason: "",
              label: ""
            },
            source_fields: [
              {
                field: "network.transport_loss_rate",
                current_value: null,
                value_source: "MODEL_OR_CONFIG_STATE"
              }
            ]
          }
        ]
      },
      {
        version: "v1",
        credibility_id: "leo_twin.network_kpi_credibility.v1",
        source: "NETWORK_KPI_PROVENANCE_V2",
        provenance_id: "leo_twin.network_kpi_provenance.v2",
        metric_model: "FLOW_LEVEL_PROXY",
        packet_level_simulation: false,
        credibility_status: "PARTIAL_RUNTIME_VALUES",
        kpi_count: 2,
        observed_kpi_count: 1,
        missing_kpi_count: 1,
        packet_level_metric_count: 0,
        flow_level_proxy_metric_count: 2,
        zero_value_kpi_count: 0,
        zero_value_explained_count: 0,
        source_field_count: 3,
        observed_source_field_count: 1,
        missing_source_field_count: 2,
        missing_metrics: ["EFFECTIVE_LOSS_PROXY"],
        zero_unexplained_metrics: [],
        caveats: []
      }
    );

    expect(display).toMatchObject({
      tone: "different",
      sourceLabel:
        "leo_twin.network_kpi_provenance.v2 / leo_twin.network_model_contract.v2",
      statusLabel: "部分运行值",
      summaryLabel: "流级代理 / 公式 2/2",
      metaLabels: ["contract v2", "无包级仿真", "KPI 2", "展示 2"],
      rows: [
        {
          metric: "EFFECTIVE_LOSS_PROXY",
          valueLabel: "- ratio",
          layerLabel: "TRANSPORT / MISSING_RUNTIME_VALUE",
          sourceFieldsLabel:
            "来源字段 0/1：network.transport_loss_rate=-",
          zeroReasonLabel: "零值语义：No configured or pressure-driven loss.",
          tone: "missing"
        },
        {
          metric: "EFFECTIVE_THROUGHPUT",
          valueLabel: "180 Mbps",
          layerLabel: "NETWORK / OBSERVED",
          sourceLabel: "completed flow capacity",
          sourceFieldsLabel:
            "来源字段 1/2：network_quality_estimated_delivered_throughput_mbps=180 / network_quality_available_route_demand_mbps=-",
          formulaInputsLabel:
            "输入审计 1 选中 / 1/2 可观测：*network_quality_estimated_delivered_throughput_mbps=180",
          formulaTraceLabel:
            "选择 completed flow capacity；选中可观测 1/1；缺失输入 1；Prefer completed-flow throughput with deterministic pressure context.",
          tone: "observed"
        }
      ]
    });
    expect(buildDataPanelNetworkKpiFormulaInspector(undefined, undefined)).toBeNull();
  });

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

  it("formats backend network KPI formula evidence from provenance and calibration", () => {
    const display = buildDataPanelNetworkKpiFormulaEvidenceDisplay({
      version: "v1",
      evidence_id: "leo_twin.network_kpi_formula_evidence.v1",
      source: "NETWORK_KPI_PROVENANCE_V2_AND_CALIBRATION_V1",
      provenance_id: "leo_twin.network_kpi_provenance.v2",
      calibration_id: "leo_twin.network_kpi_calibration.v1",
      metric_model: "FLOW_LEVEL_PROXY",
      packet_level_simulation: false,
      kpi_count: 2,
      observed_kpi_count: 2,
      runtime_value_missing_count: 0,
      selected_input_count: 3,
      selected_observed_input_count: 3,
      missing_selected_input_count: 0,
      time_varying_kpi_count: 1,
      flat_kpi_count: 1,
      formula_evidence_status: "FORMULA_AND_TIME_EVIDENCE_READY",
      kpis: [
        {
          metric: "EFFECTIVE_THROUGHPUT",
          display_name: "有效吞吐量",
          runtime_summary_key: "network_quality_effective_throughput_mbps",
          current_value: 180,
          unit: "Mbps",
          status: "OBSERVED",
          observed_source: "COMPLETED_FLOW_CAPACITY",
          observed_source_label: "completed flow capacity",
          formula_summary: "min(delivered, route capacity)",
          selection_policy: "Prefer completed-flow throughput.",
          selected_input_count: 2,
          selected_observed_input_count: 2,
          missing_selected_input_count: 0,
          selected_inputs: [
            {
              field: "network_quality_estimated_delivered_throughput_mbps",
              current_value: 180,
              observed: true,
              role: "primary",
              selection_reason: "selected source"
            },
            {
              field: "network_quality_time_adjusted_delivered_throughput_mbps",
              current_value: 171,
              observed: true,
              role: "time_driver",
              selection_reason: "time adjusted source"
            }
          ],
          variation_status: "TIME_VARYING",
          flat_reason: "",
          latest_is_zero: false,
          evidence_status: "FORMULA_AND_TIME_VARYING"
        },
        {
          metric: "EFFECTIVE_LOSS_PROXY",
          display_name: "有效丢包代理",
          runtime_summary_key: "network_quality_effective_loss_proxy_rate",
          current_value: 0.02,
          unit: "ratio",
          status: "OBSERVED",
          observed_source: "PRESSURE_LOSS_PROXY",
          observed_source_label: "pressure loss proxy",
          formula_summary: "max(route loss, demand pressure loss)",
          selection_policy: "Prefer pressure loss proxy.",
          selected_input_count: 1,
          selected_observed_input_count: 1,
          missing_selected_input_count: 0,
          selected_inputs: [
            {
              field: "network_quality_time_pressure_loss_proxy_rate",
              current_value: 0.02,
              observed: true,
              role: "time_driver",
              selection_reason: "selected source"
            }
          ],
          variation_status: "FLAT_NONZERO",
          flat_reason: "unchanged pressure inputs",
          latest_is_zero: false,
          evidence_status: "FORMULA_READY_FLAT_OR_LIMITED_SERIES"
        }
      ],
      caveats: ["Formula evidence summarizes backend flow-level proxy inputs."]
    });

    expect(display).toMatchObject({
      tone: "match",
      sourceLabel:
        "leo_twin.network_kpi_formula_evidence.v1 / NETWORK_KPI_PROVENANCE_V2_AND_CALIBRATION_V1",
      statusLabel: "公式与时间证据齐备",
      summaryLabel: "流级代理 / 公式证据 2/2",
      metaLabels: ["无包级仿真", "选中输入 3/3", "变化 KPI 1", "平坦 KPI 1"],
      caveats: ["Formula evidence summarizes backend flow-level proxy inputs."]
    });
    expect(display?.rows[1]).toMatchObject({
      metric: "EFFECTIVE_THROUGHPUT",
      displayName: "有效吞吐量 / EFFECTIVE_THROUGHPUT",
      evidenceLabel: "公式输入与时间变化匹配",
      valueLabel: "180 Mbps",
      selectedInputLabel:
        "选中输入 2/2：network_quality_estimated_delivered_throughput_mbps=180 / network_quality_time_adjusted_delivered_throughput_mbps=171",
      variationLabel: "随时间变化",
      tone: "observed"
    });
    expect(buildDataPanelNetworkKpiFormulaEvidenceDisplay(undefined)).toBeNull();
  });

  it("formats backend network KPI variation explanations from runtime status", () => {
    const display = buildDataPanelNetworkKpiVariationExplanationDisplay({
      version: "v1",
      explanation_id: "leo_twin.network_kpi_variation_explanation.v1",
      source: "NETWORK_KPI_FORMULA_EVIDENCE_V1_AND_CALIBRATION_V1",
      provenance_id: "leo_twin.network_kpi_provenance.v2",
      calibration_id: "leo_twin.network_kpi_calibration.v1",
      formula_evidence_id: "leo_twin.network_kpi_formula_evidence.v1",
      metric_model: "FLOW_LEVEL_PROXY",
      packet_level_simulation: false,
      sample_count: 2,
      sim_time_span_s: 60,
      activity_context: {
        active: true,
        requested_route_demand_mbps: 200,
        offered_route_capacity_mbps: 220,
        recent_flow_count: 2,
        available_route_count: 2
      },
      kpi_count: 2,
      time_varying_kpi_count: 1,
      flat_kpi_count: 1,
      zero_latest_kpi_count: 0,
      missing_explanation_count: 0,
      explanation_status: "TIME_VARIATION_EXPLAINED",
      items: [
        {
          metric: "EFFECTIVE_THROUGHPUT",
          display_name: "有效吞吐量",
          runtime_summary_key: "network_quality_effective_throughput_mbps",
          sample_key: "network_effective_throughput_mbps",
          current_value: 180,
          unit: "Mbps",
          observed: true,
          observed_source: "COMPLETED_FLOW_CAPACITY",
          observed_source_label: "completed flow capacity",
          formula_summary: "min(delivered, route capacity)",
          selected_input_count: 2,
          selected_observed_input_count: 2,
          missing_selected_input_count: 0,
          selected_inputs: [
            {
              field: "network_quality_estimated_delivered_throughput_mbps",
              current_value: 180,
              observed: true,
              role: "primary",
              selection_reason: "selected source"
            },
            {
              field: "network_quality_time_adjusted_delivered_throughput_mbps",
              current_value: 171,
              observed: true,
              role: "time_driver",
              selection_reason: "time adjusted source"
            }
          ],
          first_value: 160,
          latest_value: 180,
          minimum_value: 160,
          maximum_value: 180,
          absolute_delta: 20,
          endpoint_delta: 20,
          relative_delta: 0.111,
          latest_is_zero: false,
          variation_status: "TIME_VARYING",
          flat_reason: "",
          evidence_status: "FORMULA_AND_TIME_VARYING",
          explanation_status: "TIME_VARIATION_EXPLAINED",
          trust_label: "time-varying flow-level proxy",
          user_explanation:
            "有效吞吐量 随仿真时间变化，因为后端选中的 2 个流级输入和 KPI 时间序列样本发生变化。"
        },
        {
          metric: "EFFECTIVE_LOSS_PROXY",
          display_name: "丢包代理",
          runtime_summary_key: "network_quality_effective_loss_proxy_rate",
          sample_key: "network_effective_loss_proxy_rate",
          current_value: 0.02,
          unit: "ratio",
          observed: true,
          observed_source: "PRESSURE_LOSS_PROXY",
          observed_source_label: "pressure loss proxy",
          formula_summary: "max(route loss, pressure loss)",
          selected_input_count: 1,
          selected_observed_input_count: 1,
          missing_selected_input_count: 0,
          selected_inputs: [
            {
              field: "network_quality_time_pressure_loss_proxy_rate",
              current_value: 0.02,
              observed: true,
              role: "time_driver",
              selection_reason: "selected source"
            }
          ],
          first_value: 0.02,
          latest_value: 0.02,
          minimum_value: 0.02,
          maximum_value: 0.02,
          absolute_delta: 0,
          endpoint_delta: 0,
          relative_delta: 0,
          latest_is_zero: false,
          variation_status: "FLAT_NONZERO",
          flat_reason: "selected pressure inputs did not change",
          evidence_status: "FORMULA_READY_FLAT_OR_LIMITED_SERIES",
          explanation_status: "FLAT_NONZERO_EXPLAINED",
          trust_label: "flat flow-level proxy",
          user_explanation:
            "丢包代理 保持不变，因为选中的压力输入没有变化。"
        }
      ],
      model_assumptions: [
        "网络 KPI 变化解释来自后端 KPI provenance、选中公式输入和确定性运行时 KPI 样本。"
      ],
      caveats: [
        "变化解释 v1 只是观测摘要，不改变任何 KPI 公式。"
      ],
      explanation_hash:
        "sha256:abababababababababababababababababababababababababababababababab"
    });

    expect(display).toMatchObject({
      tone: "match",
      sourceLabel:
        "leo_twin.network_kpi_variation_explanation.v1 / NETWORK_KPI_FORMULA_EVIDENCE_V1_AND_CALIBRATION_V1",
      statusLabel: "已解释时间变化",
      summaryLabel: "流级代理 / 样本 2 / 跨度 1分0秒 / 变化 KPI 1/2",
      metaLabels: [
        "无包级仿真",
        "活动需求 200 Mbps",
        "平坦 KPI 1",
        "缺失解释 0",
        "证据 abababababab"
      ],
      caveats: [
        "网络 KPI 变化解释来自后端 KPI provenance、选中公式输入和确定性运行时 KPI 样本。",
        "变化解释 v1 只是观测摘要，不改变任何 KPI 公式。"
      ]
    });
    expect(display?.rows[1]).toMatchObject({
      metric: "EFFECTIVE_THROUGHPUT",
      displayName: "有效吞吐量 / EFFECTIVE_THROUGHPUT",
      statusLabel: "已解释时间变化",
      valueLabel: "180 Mbps",
      inputLabel:
        "选中输入 2/2：network_quality_estimated_delivered_throughput_mbps=180 / network_quality_time_adjusted_delivered_throughput_mbps=171",
      explanationLabel:
        "有效吞吐量 随仿真时间变化，因为后端选中的 2 个流级输入和 KPI 时间序列样本发生变化。",
      tone: "observed"
    });
    expect(buildDataPanelNetworkKpiVariationExplanationDisplay(undefined)).toBeNull();
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

describe("buildDataPanelRouteProvenanceTrustDisplay", () => {
  it("formats backend route provenance trust fields for dashboard evidence", () => {
    const display = buildDataPanelRouteProvenanceTrustDisplay({
      version: "v1",
      trust_id: "leo_twin.route_provenance_trust.v1",
      source: "route_explanation_summary_v1",
      route_model: "FLOW_LEVEL_ROUTE_PROXY",
      packet_level_simulation: false,
      all_pairs_computation: false,
      trust_status: "COMPLETE_FLOW_LEVEL_ROUTE_PROXY",
      summary_scope: "ROUTE_EXPLANATION_WINDOW",
      route_count: 2,
      window_item_count: 2,
      assessed_route_count: 2,
      hidden_route_count: 0,
      unassessed_route_count: 0,
      available_route_count: 1,
      blocked_route_count: 1,
      over_demand_route_count: 0,
      compute_service_route_count: 1,
      network_service_route_count: 1,
      explained_route_count: 2,
      missing_explanation_count: 0,
      path_context_route_count: 2,
      next_hop_route_count: 2,
      loss_proxy_route_count: 1,
      core_field_count: 16,
      observed_core_field_count: 16,
      missing_core_field_count: 0,
      context_field_count: 18,
      observed_context_field_count: 18,
      missing_context_field_count: 0,
      bottleneck_components: ["AVAILABILITY", "LOSS_PROXY"],
      sample_route_ids: ["route-b", "route-a"],
      caveats: [
        "Route explanations are flow-level route proxies, not packet-level traces.",
        "Route trust reuses route_explanation_summary_v1 and does not recompute paths."
      ]
    });

    expect(display).toEqual({
      tone: "match",
      sourceLabel: "leo_twin.route_provenance_trust.v1 / route_explanation_summary_v1",
      statusLabel: "完整流级路由代理",
      summaryLabel: "路由 2/2 已解释；核心字段 16/16；上下文 18/18",
      metaLabels: [
        "模型 流级路由代理",
        "无包级仿真",
        "无全对链路计算",
        "可用 1 / 阻塞 1",
        "瓶颈 AVAILABILITY, LOSS_PROXY",
        "窗口 2 路由"
      ],
      caveats: [
        "Route explanations are flow-level route proxies, not packet-level traces.",
        "Route trust reuses route_explanation_summary_v1 and does not recompute paths."
      ]
    });
  });

  it("surfaces partial route windows and missing context", () => {
    const display = buildDataPanelRouteProvenanceTrustDisplay({
      version: "v1",
      trust_id: "leo_twin.route_provenance_trust.v1",
      source: "route_explanation_summary_v1",
      route_model: "FLOW_LEVEL_ROUTE_PROXY",
      packet_level_simulation: false,
      all_pairs_computation: false,
      trust_status: "PARTIAL_ROUTE_EXPLANATIONS",
      route_count: 3,
      window_item_count: 1,
      assessed_route_count: 1,
      hidden_route_count: 2,
      unassessed_route_count: 2,
      available_route_count: 0,
      blocked_route_count: 3,
      over_demand_route_count: 1,
      compute_service_route_count: 1,
      network_service_route_count: 2,
      explained_route_count: 1,
      missing_explanation_count: 0,
      path_context_route_count: 0,
      next_hop_route_count: 0,
      loss_proxy_route_count: 0,
      core_field_count: 8,
      observed_core_field_count: 8,
      missing_core_field_count: 0,
      context_field_count: 9,
      observed_context_field_count: 3,
      missing_context_field_count: 6,
      bottleneck_components: ["PATH"],
      sample_route_ids: ["route-partial"],
      caveats: ["Only the current route window is listed; additional routes exist."]
    });

    expect(display?.tone).toBe("different");
    expect(display?.statusLabel).toBe("路由解释部分覆盖");
    expect(display?.summaryLabel).toBe("路由 1/3 已解释；核心字段 8/8；上下文 3/9");
    expect(display?.metaLabels).toContain("隐藏 2 路由");
    expect(display?.caveats).toEqual([
      "Only the current route window is listed; additional routes exist.",
      "未评估路由 2 条",
      "缺少上下文字段 6 个",
      "超需求路由 1 条"
    ]);
  });

  it("hides route trust display until backend status provides the summary", () => {
    expect(buildDataPanelRouteProvenanceTrustDisplay(null)).toBeNull();
    expect(buildDataPanelRouteProvenanceTrustDisplay(undefined)).toBeNull();
  });
});

describe("buildDataPanelModelTrustEvidenceWorkspace", () => {
  it("combines backend configuration, KPI, fidelity, replay, and runtime evidence", () => {
    const display = buildDataPanelModelTrustEvidenceWorkspace({
      configurationExplanation: {
        sourceLabel: "BACKEND_DERIVED_SUMMARY / sees.user_configuration.v2",
        summaryLabel: "2 个配置入口 / 6 个语义分组 / READ_ONLY_EXPLANATION",
        determinismLabel: "seed runtime.seed / unknown REJECT / default OMITTED",
        boundaryLabel: "STK/EXATA/AFSIM/DDS 禁止；无包级仿真",
        surfaces: [],
        sections: []
      },
      modelAssumptions: {
        sourceLabel: "backend_summary.model_assumptions + runtime credibility",
        summaryLabel: "2 条假设 / 1 条规模边界 / 1 条KPI边界",
        boundaryLabel: "STK/EXATA/AFSIM/DDS 禁止；无包级仿真",
        fidelityLabel: "STANDARD / 72 星 / 20 用户",
        rows: []
      },
      networkKpiCredibility: {
        tone: "match",
        statusLabel: "完整流级代理",
        summaryLabel: "KPI 6/6 有运行值；来源字段 18/18 可观测",
        metaLabels: ["模型 流级代理", "无包级指标"],
        caveats: ["No packet-level simulation."]
      },
      networkKpiBenchmarkValidation: {
        tone: "match",
        statusLabel: "基准通过",
        summaryLabel: "检查 12/12 通过；WARN 0 / FAIL 0 / 缺数据 0",
        metaLabels: ["profile FLOW_LEVEL_PROXY_RUNTIME_GUARDRAILS"],
        issueLabels: [],
        caveats: ["Benchmark validation v1 is a deterministic product guardrail."]
      },
      networkKpiCalibration: {
        tone: "match",
        sourceLabel:
          "leo_twin.network_kpi_calibration.v1 / KPI_TIME_SERIES_V1_AND_METRICS_SUMMARY",
        statusLabel: "已观察到随仿真时间变化",
        summaryLabel: "样本 2 / 时间跨度 1分0秒 / 变化 KPI 3/4",
        metaLabels: ["模型 流级代理", "无包级仿真"],
        rows: [
          {
            metric: "EFFECTIVE_THROUGHPUT",
            metricLabel: "有效吞吐 / EFFECTIVE_THROUGHPUT",
            statusLabel: "随时间变化",
            valueLabel: "最新 171 Mbps",
            deltaLabel: "变化 9 Mbps / 端点 -9 Mbps",
            rangeLabel: "范围 171 Mbps - 180 Mbps",
            tone: "observed",
            title: "network_effective_throughput_mbps"
          }
        ],
        caveats: ["Calibration audits movement only."]
      },
      networkKpiFormulaEvidence: {
        tone: "match",
        sourceLabel:
          "leo_twin.network_kpi_formula_evidence.v1 / NETWORK_KPI_PROVENANCE_V2_AND_CALIBRATION_V1",
        statusLabel: "公式与时间证据齐备",
        summaryLabel: "流级代理 / 公式证据 6/6",
        metaLabels: ["无包级仿真", "选中输入 10/10", "变化 KPI 4", "平坦 KPI 2"],
        rows: [
          {
            metric: "EFFECTIVE_THROUGHPUT",
            displayName: "有效吞吐量 / EFFECTIVE_THROUGHPUT",
            evidenceLabel: "公式输入与时间变化匹配",
            valueLabel: "180 Mbps",
            selectedInputLabel: "选中输入 2/2：network_quality_estimated_delivered_throughput_mbps=180",
            variationLabel: "随时间变化",
            tone: "observed",
            title: "min(delivered, route capacity)"
          }
        ],
        caveats: ["Formula evidence summarizes backend flow-level proxy inputs."]
      },
      networkKpiFormulaInspector: {
        tone: "match",
        sourceLabel: "leo_twin.network_kpi_provenance.v2 / leo_twin.network_model_contract.v2",
        statusLabel: "完整流级代理",
        summaryLabel: "流级代理 / 公式 6/6",
        metaLabels: ["contract v2", "无包级仿真"],
        rows: [
          {
            metric: "EFFECTIVE_THROUGHPUT",
            displayName: "有效吞吐量 / EFFECTIVE_THROUGHPUT",
            valueLabel: "180 Mbps",
            layerLabel: "TRANSPORT / OBSERVED",
            sourceLabel: "completed flow capacity",
            formulaLabel: "min(delivered, route capacity)",
            sourceFieldsLabel: "来源字段 2/2",
            formulaInputsLabel: null,
            formulaTraceLabel: null,
            zeroReasonLabel: null,
            tone: "observed",
            title: "throughput interpretation"
          }
        ]
      },
      routeProvenanceTrust: {
        tone: "match",
        sourceLabel: "leo_twin.route_provenance_trust.v1 / route_explanation_summary_v1",
        statusLabel: "完整流级路由代理",
        summaryLabel: "路由 2/2 已解释；核心字段 16/16；上下文 18/18",
        metaLabels: ["模型 流级路由代理", "无包级仿真"],
        caveats: [
          "Route explanations are flow-level route proxies, not packet-level traces."
        ]
      },
      fidelitySummary: {
        orbit_update_mode: "PER_SATELLITE",
        metrics_mode: "DETAILED",
        space_link_mode: "DETAILED_SMALL_SCALE",
        detailed_space_link_enabled: true,
        space_link_candidate_policy: "ALL_SMALL_SCALE",
        max_space_link_candidates_per_satellite: 8,
        batch_space_link_update_limit: 10000,
        scale_limit_reason: "",
        current_scale_mode: "STANDARD",
        fidelity_warnings: [],
        satellite_count: 72,
        user_count: 20
      },
      reproducibilityManifest: {
        version: "v1",
        source: "runtime/status",
        manifest_id: "manifest-demo",
        session_id: "session-demo",
        seed: 42,
        duration_s: 600,
        runtime_mode: "REAL_TIME",
        speed_factor: 1,
        config_version: 3,
        deterministic_replay: true,
        scenario_hash: "sha256:scenariohash",
        control_config_hash: "sha256:controlhash",
        generated_config_hash: "sha256:generatedhash",
        metrics_summary_hash: "sha256:metricshash",
        runtime_state_hash: "sha256:runtimehash",
        manifest_hash: "sha256:manifesthash",
        artifact_policy: "REPRODUCIBLE_PACKAGE",
        artifacts: [],
        artifact_count: 4,
        notes: ["Deterministic manifest."]
      },
      exportDiagnosticsBundle: {
        type: "RUNTIME_EXPORT_DIAGNOSTICS_BUNDLE_V1",
        version: "v1",
        bundle_id: "diag-demo",
        source: "runtime/export",
        diagnostics_scope: "PACKAGE",
        package: {
          package_id: "pkg-demo",
          package_dir: "exports/pkg-demo",
          package_complete: true,
          review_status: "REVIEW_READY",
          contract_id: "runtime_export_package.v1"
        },
        runtime: {
          lifecycle_state: "COMPLETED",
          current_sim_time: 600,
          processed_event_count: 3905,
          queued_event_count: 0
        },
        reproducibility: {
          manifest_id: "manifest-demo",
          manifest_ok: true,
          manifest_hash: "sha256:manifesthash",
          config_hash: "sha256:controlhash",
          generated_config_hash: "sha256:generatedhash",
          review_summary_hash: "sha256:summaryhash"
        },
        artifact_health: {
          artifact_count: 4,
          artifact_filenames: ["manifest.json", "summary.json"],
          required_filenames: ["manifest.json", "summary.json"],
          recommended_filenames: ["diagnostics_bundle_v1.json"],
          present_required_filenames: ["manifest.json", "summary.json"],
          missing_required_filenames: [],
          present_recommended_filenames: ["diagnostics_bundle_v1.json"],
          missing_recommended_filenames: []
        },
        model_boundaries: {
          event_kernel_policy: "FROZEN_DETERMINISTIC_KERNEL",
          packet_level_simulation: false,
          external_simulators: [],
          forbidden_external_integrations: ["STK", "EXATA", "AFSIM", "DDS"],
          diagnostics_policy: "READ_ONLY"
        },
        findings: [],
        finding_count: 0,
        recommended_next_actions: ["Archive package."],
        diagnostics_hash: "sha256:diagnosticshash"
      },
      runtimeStatus: {
        status: "COMPLETED",
        lifecycle_state: "COMPLETED",
        mode: "REAL_TIME",
        speed_factor: 1,
        seed: 42,
        duration: 600,
        config_version: 3,
        last_action: "STOP",
        initialized: true,
        current_sim_time: 600,
        processed_event_count: 3905
      }
    });

    expect(display).toMatchObject({
      tone: "match",
      sourceLabel: "runtime status + backend summary + export diagnostics",
      statusLabel: "证据链完整",
      summaryLabel: "10 类证据 / 10 类可用 / 0 类待补齐",
      scoreLabel: "可用 10/10 / 警告 0 / 错误 0",
      metaLabels: [
        "配置语义已声明",
        "KPI基准已验证",
        "KPI变化已校准",
        "KPI公式证据已核验",
        "KPI公式可追踪",
        "路由证据可追踪",
        "manifest已生成",
        "诊断包已加载"
      ],
      actionLabels: ["证据链可用于导出结果包并进入复盘验收。"]
    });
    expect(display?.rows.map((row) => row.kind)).toEqual([
      "configuration",
      "fidelity",
      "kpi",
      "benchmark",
      "calibration",
      "formula",
      "formula",
      "route",
      "replay",
      "runtime"
    ]);
    expect(display?.rows[4]).toMatchObject({
      label: "KPI变化校准",
      statusLabel: "已观察到随仿真时间变化",
      tone: "match",
      source:
        "leo_twin.network_kpi_calibration.v1 / KPI_TIME_SERIES_V1_AND_METRICS_SUMMARY"
    });
    expect(display?.rows[5]).toMatchObject({
      label: "KPI公式证据",
      tone: "match"
    });
    expect(display?.rows[6]).toMatchObject({
      label: "KPI公式来源",
      tone: "match"
    });
    expect(display?.rows[7]).toMatchObject({
      label: "路由解释可信度",
      statusLabel: "完整流级路由代理",
      tone: "match",
      source: "leo_twin.route_provenance_trust.v1 / route_explanation_summary_v1"
    });
    expect(display?.rows[8]).toMatchObject({
      label: "复盘证据",
      statusLabel: "REVIEW_READY",
      tone: "match",
      source: "runtime_export_diagnostics_bundle_v1"
    });
  });

  it("surfaces pending and invalid evidence without hiding the workspace", () => {
    const display = buildDataPanelModelTrustEvidenceWorkspace({
      networkKpiCredibility: {
        tone: "error",
        statusLabel: "包级指标越界",
        summaryLabel: "KPI 5/6 有运行值；来源字段 10/12 可观测",
        metaLabels: ["包级指标 1"],
        caveats: ["Packet-level metric is not allowed."]
      },
      fidelitySummary: {
        orbit_update_mode: "BATCH",
        metrics_mode: "AGGREGATED",
        space_link_mode: "BOUNDED_CANDIDATE",
        detailed_space_link_enabled: false,
        space_link_candidate_policy: "SAME_PLANE_AND_ADJACENT_PLANE_BOUNDED_CANDIDATES",
        max_space_link_candidates_per_satellite: 4,
        batch_space_link_update_limit: 999,
        scale_limit_reason: "satellite_count >= 300",
        current_scale_mode: "LARGE_SCALE_AGGREGATED",
        fidelity_warnings: ["Orbit updates are batched."],
        satellite_count: 1200,
        user_count: 100
      },
      exportDiagnosticsBundle: {
        type: "RUNTIME_EXPORT_DIAGNOSTICS_BUNDLE_V1",
        version: "v1",
        bundle_id: "diag-error",
        source: "runtime/export",
        diagnostics_scope: "PACKAGE",
        package: {
          package_id: "pkg-error",
          package_dir: "exports/pkg-error",
          package_complete: false,
          review_status: "INCOMPLETE",
          contract_id: "runtime_export_package.v1"
        },
        runtime: {
          lifecycle_state: "ERROR",
          current_sim_time: 12,
          processed_event_count: 100,
          queued_event_count: 5
        },
        reproducibility: {
          manifest_id: "manifest-error",
          manifest_ok: false,
          manifest_hash: "sha256:manifesthash",
          config_hash: "sha256:controlhash",
          generated_config_hash: "sha256:generatedhash",
          review_summary_hash: "sha256:summaryhash"
        },
        artifact_health: {
          artifact_count: 1,
          artifact_filenames: ["summary.json"],
          required_filenames: ["manifest.json", "summary.json"],
          recommended_filenames: ["diagnostics_bundle_v1.json"],
          present_required_filenames: ["summary.json"],
          missing_required_filenames: ["manifest.json"],
          present_recommended_filenames: [],
          missing_recommended_filenames: ["diagnostics_bundle_v1.json"]
        },
        model_boundaries: {
          event_kernel_policy: "FROZEN_DETERMINISTIC_KERNEL",
          packet_level_simulation: false,
          external_simulators: [],
          forbidden_external_integrations: ["STK", "EXATA", "AFSIM", "DDS"],
          diagnostics_policy: "READ_ONLY"
        },
        findings: [
          {
            severity: "ERROR",
            code: "MISSING_MANIFEST",
            message: "manifest.json is missing."
          }
        ],
        finding_count: 1,
        recommended_next_actions: ["Regenerate package."],
        diagnostics_hash: "sha256:diagnosticshash"
      },
      runtimeStatus: {
        status: "ERROR",
        lifecycle_state: "ERROR",
        mode: "PAUSED",
        speed_factor: 1,
        seed: 42,
        duration: 600,
        config_version: 3,
        last_action: "START",
        initialized: true,
        current_sim_time: 12,
        processed_event_count: 100,
        last_error: "runtime failed"
      }
    });

    expect(display?.tone).toBe("error");
    expect(display?.statusLabel).toBe("证据链存在错误");
    expect(display?.summaryLabel).toBe("10 类证据 / 1 类可用 / 6 类待补齐");
    expect(display?.rows.map((row) => [row.kind, row.tone])).toEqual([
      ["configuration", "pending"],
      ["fidelity", "different"],
      ["kpi", "error"],
      ["benchmark", "pending"],
      ["calibration", "pending"],
      ["formula", "pending"],
      ["formula", "pending"],
      ["route", "pending"],
      ["replay", "error"],
      ["runtime", "error"]
    ]);
    expect(display?.actionLabels).toEqual([
      "配置语义：等待后端解释",
      "KPI可信度：包级指标越界",
      "KPI基准验证：等待基准验证",
      "KPI变化校准：等待校准摘要",
      "KPI公式证据：等待公式证据摘要",
      "KPI公式来源：等待公式证据",
      "路由解释可信度：等待路由证据",
      "复盘证据：INCOMPLETE",
      "运行证据：已停止",
      "ERROR MISSING_MANIFEST"
    ]);
  });

  it("returns null only when no evidence input exists", () => {
    expect(buildDataPanelModelTrustEvidenceWorkspace({})).toBeNull();
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

describe("buildDataPanelServiceDetailRows", () => {
  it("formats backend cursor service lifecycle detail rows", () => {
    const rows = buildDataPanelServiceDetailRows(
      {
        version: "v1",
        source: "SERVICE_LATENCY_HISTORY",
        summary_scope: "SERVICE_LIFECYCLE_DETAIL_WINDOW",
        cursor: 0,
        limit: 2,
        next_cursor: 1,
        has_more: true,
        service_count: 3,
        item_count: 1,
        complete_service_count: 1,
        queued_service_count: 1,
        window_service_count: 1,
        hidden_service_count: 2,
        items: [
          {
            service_id: "svc-0",
            task_id: "svc-00-compute_service-00000-task",
            input_flow_id: "input-0",
            output_flow_id: "output-0",
            input_route_id: "route-input",
            output_route_id: "route-output",
            compute_node_id: "sat-00001",
            complete: false,
            service_state: "RUNNING",
            service_state_label: "Service running",
            placement_status: "QUEUED",
            placement_policy: "MIN_ESTIMATED_FINISH_TIME",
            placement_bottleneck_resource: "gpu_tflops_fp32",
            placement_candidate_count: 3,
            placement_capable_candidate_count: 2,
            placement_candidate_queue_label: "sat-00001:QUEUED",
            first_sample_sim_time: 1,
            last_sample_sim_time: 2,
            input_network_latency_s: 0.1,
            compute_queue_delay_s: 0.2,
            compute_execution_delay_s: 0.3,
            output_network_latency_s: 0.4,
            total_latency_s: 1,
            stage_count: 1,
            stages: [
              {
                component: "compute_queue",
                label: "Compute queue",
                sample_sim_time: 1.5,
                duration_s: 0.2
              }
            ]
          }
        ]
      },
      1
    );

    expect(rows).toMatchObject({
      sourceLabel: "后端服务详情页 1 / 3",
      summaryLabel: "1 行 / 完成 1 / 排队 1 / 可继续游标读取",
      items: [
        {
          serviceId: "svc-0",
          taskLabel: "...vice-00000-task",
          stateLabel: "Service running",
          placementLabel:
            "节点 sat-00001 / 排队 / 瓶颈 gpu_tflops_fp32 / 候选 2/3 / 队列 sat-00001:QUEUED",
          networkLatencyLabel: "100 ms / 400 ms",
          computeLatencyLabel: "200 ms / 300 ms",
          totalLatencyLabel: "1,000 ms"
        }
      ]
    });
    expect(rows.items[0].traceTitle).toContain("service=svc-0");
    expect(rows.items[0].traceTitle).toContain(
      "stages=compute_queue@1.5s=200 ms"
    );
  });

  it("returns an empty waiting state before backend service pages arrive", () => {
    expect(buildDataPanelServiceDetailRows(null)).toEqual({
      sourceLabel: "等待后端服务详情页",
      summaryLabel: "暂无服务生命周期游标明细",
      items: []
    });
  });
});

describe("buildDataPanelServiceLifecycleTraceDisplay", () => {
  it("formats backend-owned service lifecycle trace v2 rows", () => {
    const display = buildDataPanelServiceLifecycleTraceDisplay({
      version: "v2",
      contract_id: "leo_twin.service_lifecycle_trace_contract.v2",
      source: "SERVICE_LATENCY_HISTORY",
      source_summary: "service_latency_history_v1",
      summary_scope: "SERVICE_LIFECYCLE_TRACE_WINDOW",
      trace_model: "COMMUNICATION_COMPUTE_COMPONENT_PROXY",
      cursor: 0,
      limit: 100,
      next_cursor: 1,
      has_more: true,
      service_count: 2,
      trace_count: 1,
      complete_trace_count: 0,
      running_trace_count: 1,
      incomplete_trace_count: 0,
      hidden_trace_count: 1,
      items: [
        {
          trace_id: "trace:svc-01",
          service_id: "svc-01-compute_service-00000",
          task_id: "svc-01-compute_service-00000-task",
          service_class: "COMPUTE_SERVICE",
          input_flow_id: "svc-01-compute_service-00000-input",
          output_flow_id: "svc-01-compute_service-00000-output",
          input_route_id: "route:input",
          output_route_id: "",
          compute_node_id: "sat-00001",
          placement_status: "PLACED",
          placement_policy: "MIN_ESTIMATED_FINISH_TIME",
          placement_bottleneck_resource: "cpu_gflops_fp32",
          first_sample_sim_time: 6,
          last_sample_sim_time: 10,
          input_network_latency_s: 4,
          compute_queue_delay_s: 1,
          compute_execution_delay_s: 2.5,
          output_network_latency_s: 0,
          total_latency_s: 0,
          terminal_state: "RUNNING",
          terminal_state_reason: "OUTPUT_NETWORK_PENDING",
          stage_count: 4,
          observed_stage_count: 3,
          pending_stage_count: 1,
          stages: [
            {
              stage_index: 0,
              stage_id: "svc-01:input_network",
              component: "input_network",
              stage_kind: "INPUT_NETWORK",
              stage_label: "Input network",
              stage_status: "OBSERVED",
              sample_sim_time: 6,
              duration_s: 4,
              flow_id: "svc-01-compute_service-00000-input",
              route_id: "route:input",
              compute_node_id: ""
            },
            {
              stage_index: 3,
              stage_id: "svc-01:output_network",
              component: "output_network",
              stage_kind: "OUTPUT_NETWORK",
              stage_label: "Output network",
              stage_status: "PENDING",
              sample_sim_time: 10,
              duration_s: 0,
              flow_id: "svc-01-compute_service-00000-output",
              route_id: "",
              compute_node_id: ""
            }
          ]
        }
      ]
    });

    expect(display.sourceLabel).toBe(
      "service_latency_history_v1 -> service_lifecycle_trace_v2"
    );
    expect(display.summaryLabel).toContain("1 trace / 2 service");
    expect(display.summaryLabel).toContain("运行 1");
    expect(display.items[0]).toMatchObject({
      traceId: "trace:svc-01",
      serviceId: "svc-01-compute_service-00000",
      serviceLabel: "...e_service-00000",
      inputFlowId: "svc-01-compute_service-00000-input",
      outputFlowId: "svc-01-compute_service-00000-output",
      routeIds: ["route:input"],
      flowIds: [
        "svc-01-compute_service-00000-input",
        "svc-01-compute_service-00000-output"
      ],
      primaryRouteId: "route:input",
      computeNodeId: "sat-00001",
      terminalStateReason: "OUTPUT_NETWORK_PENDING",
      terminalStateLabel: "运行中 / OUTPUT_NETWORK_PENDING",
      computeNodeLabel: "算力 sat-00001",
      networkLatencyLabel: "4,000 ms / 0 ms",
      computeLatencyLabel: "1,000 ms / 2,500 ms",
      totalLatencyLabel: "0 ms",
      artifactFilename: "service_lifecycle_trace_v2.json",
      artifactPointer: "/items/0",
      artifactFilter: "trace:svc-01"
    });
    expect(
      buildDataPanelServiceTraceEvidenceInspectorFocus(
        "pkg-review",
        display.items[0]
      )
    ).toMatchObject({
      focusSourceLabel: "Service trace evidence inspector focus",
      statusLabel: "service trace / trace:svc-01",
      artifactLabel: "service_lifecycle_trace_v2.json",
      jsonPointer: "/items/0",
      defaultInspectorFilter: "trace:svc-01"
    });
    expect(display.items[0].traceTitle).toContain("terminal=RUNNING");
    expect(display.items[0].stages).toEqual([
      {
        stageId: "svc-01:input_network",
        component: "input_network",
        stageKind: "INPUT_NETWORK",
        stageStatus: "OBSERVED",
        label: "Input network",
        statusLabel: "已观测",
        durationLabel: "4,000 ms",
        traceTitle:
          "input_network@6s=4,000 ms OBSERVED route=route:input flow=svc-01-compute_service-00000-input"
      },
      {
        stageId: "svc-01:output_network",
        component: "output_network",
        stageKind: "OUTPUT_NETWORK",
        stageStatus: "PENDING",
        label: "Output network",
        statusLabel: "等待",
        durationLabel: "0 ms",
        traceTitle:
          "output_network@10s=0 ms PENDING flow=svc-01-compute_service-00000-output"
      }
    ]);
  });

  it("filters service lifecycle trace rows by query terminal state and compute node", () => {
    const display = buildDataPanelServiceLifecycleTraceDisplay({
      version: "v2",
      source: "SERVICE_LATENCY_HISTORY",
      source_summary: "service_latency_history_v1",
      summary_scope: "SERVICE_LIFECYCLE_TRACE_WINDOW",
      cursor: 0,
      limit: 100,
      next_cursor: 2,
      has_more: false,
      service_count: 2,
      trace_count: 2,
      complete_trace_count: 1,
      running_trace_count: 1,
      incomplete_trace_count: 0,
      hidden_trace_count: 0,
      items: [
        {
          trace_id: "trace:run",
          service_id: "svc-run-compute_service-00000",
          task_id: "svc-run-compute_service-00000-task",
          service_class: "COMPUTE_SERVICE",
          input_flow_id: "svc-run-compute_service-00000-input",
          output_flow_id: "svc-run-compute_service-00000-output",
          input_route_id: "route:run-input",
          output_route_id: "route:run-output",
          compute_node_id: "sat-00001",
          placement_status: "PLACED",
          input_network_latency_s: 1,
          compute_queue_delay_s: 0.1,
          compute_execution_delay_s: 2,
          output_network_latency_s: 0,
          total_latency_s: 0,
          terminal_state: "RUNNING",
          terminal_state_reason: "OUTPUT_NETWORK_PENDING",
          stage_count: 4,
          observed_stage_count: 3,
          pending_stage_count: 1,
          stages: [
            {
              stage_index: 0,
              stage_id: "run:input_network",
              component: "input_network",
              stage_kind: "NETWORK",
              stage_label: "Input network",
              stage_status: "OBSERVED",
              duration_s: 1,
              flow_id: "svc-run-compute_service-00000-input",
              route_id: "route:run-input"
            }
          ]
        },
        {
          trace_id: "trace:done",
          service_id: "svc-done-compute_service-00000",
          task_id: "svc-done-compute_service-00000-task",
          service_class: "COMPUTE_SERVICE",
          input_flow_id: "svc-done-compute_service-00000-input",
          output_flow_id: "svc-done-compute_service-00000-output",
          input_route_id: "route:done-input",
          output_route_id: "route:done-output",
          compute_node_id: "sat-00002",
          placement_status: "PLACED",
          input_network_latency_s: 1,
          compute_queue_delay_s: 0.1,
          compute_execution_delay_s: 2,
          output_network_latency_s: 1,
          total_latency_s: 4.1,
          terminal_state: "COMPLETE",
          terminal_state_reason: "TOTAL_LATENCY_OBSERVED",
          stage_count: 4,
          observed_stage_count: 4,
          pending_stage_count: 0,
          stages: [
            {
              stage_index: 3,
              stage_id: "done:output_network",
              component: "output_network",
              stage_kind: "NETWORK",
              stage_label: "Output network",
              stage_status: "OBSERVED",
              duration_s: 1,
              flow_id: "svc-done-compute_service-00000-output",
              route_id: "route:done-output"
            }
          ]
        }
      ]
    });

    expect(display.items.map((row) => row.terminalState)).toEqual([
      "RUNNING",
      "COMPLETE"
    ]);
    expect(
      filterServiceLifecycleTraceDisplay(display, "route:done").items.map(
        (row) => row.traceId
      )
    ).toEqual(["trace:done"]);
    expect(
      filterServiceLifecycleTraceDisplay(display, {
        terminalState: "RUNNING"
      }).items.map((row) => row.traceId)
    ).toEqual(["trace:run"]);
    expect(
      filterServiceLifecycleTraceDisplay(display, {
        computeNodeId: " SAT-00002 "
      }).items.map((row) => row.traceId)
    ).toEqual(["trace:done"]);
    expect(
      filterServiceLifecycleTraceDisplay(display, {
        stageKind: "output network"
      }).items.map((row) => row.traceId)
    ).toEqual(["trace:done"]);
    expect(
      filterServiceLifecycleTraceDisplay(display, {
        terminalReason: "output-network-pending"
      }).items.map((row) => row.traceId)
    ).toEqual(["trace:run"]);
    expect(
      filterServiceLifecycleTraceDisplay(display, {
        query: "output network",
        terminalState: "COMPLETE",
        computeNodeId: "sat-00002",
        stageKind: "OUTPUT_NETWORK",
        terminalReason: "TOTAL_LATENCY_OBSERVED"
      }).items.map((row) => row.traceId)
    ).toEqual(["trace:done"]);
    expect(filterServiceLifecycleTraceDisplay(display, "")).toBe(display);
    expect(
      filterServiceLifecycleTraceDisplay(display, {
        query: "not-present"
      }).summaryLabel
    ).toContain("筛选 0");
  });

  it("builds backend exact service trace focus filters", () => {
    const display = buildDataPanelServiceLifecycleTraceDisplay({
      version: "v2",
      source: "SERVICE_LATENCY_HISTORY",
      source_summary: "service_latency_history_v1",
      summary_scope: "SERVICE_LIFECYCLE_TRACE_WINDOW",
      cursor: 0,
      limit: 100,
      next_cursor: 1,
      has_more: false,
      service_count: 1,
      trace_count: 1,
      complete_trace_count: 1,
      running_trace_count: 0,
      incomplete_trace_count: 0,
      hidden_trace_count: 0,
      items: [
        {
          trace_id: "trace:svc-02",
          service_id: "svc-02-compute_service-00000",
          task_id: "svc-02-compute_service-00000-task",
          service_class: "COMPUTE_SERVICE",
          input_flow_id: "svc-02-compute_service-00000-input",
          output_flow_id: "svc-02-compute_service-00000-output",
          input_route_id: "route:input-02",
          output_route_id: "route:output-02",
          compute_node_id: "sat-00002",
          placement_status: "PLACED",
          input_network_latency_s: 1,
          compute_queue_delay_s: 0.2,
          compute_execution_delay_s: 3,
          output_network_latency_s: 1.5,
          total_latency_s: 5.7,
          terminal_state: "COMPLETE",
          terminal_state_reason: "TOTAL_LATENCY_OBSERVED",
          stage_count: 4,
          observed_stage_count: 4,
          pending_stage_count: 0,
          stages: []
        }
      ]
    });
    const row = selectServiceLifecycleTraceRow(display.items, "trace:svc-02");
    const focus = buildDataPanelServiceTraceFocus(row, {
      version: "v2",
      source: "BACKEND_RUNTIME_DETAIL",
      summary_scope: "SERVICE_TRACE_EXACT_DETAIL",
      detail_hash: "sha256:trace",
      trace: {
        trace_id: "trace:svc-02",
        service_id: "svc-02-compute_service-00000",
        task_id: "svc-02-compute_service-00000-task",
        service_class: "COMPUTE_SERVICE",
        input_flow_id: "svc-02-compute_service-00000-input",
        output_flow_id: "svc-02-compute_service-00000-output",
        input_route_id: "route:input-02",
        output_route_id: "route:output-02",
        compute_node_id: "sat-00002",
        input_network_latency_s: 1,
        compute_queue_delay_s: 0.2,
        compute_execution_delay_s: 3,
        output_network_latency_s: 1.5,
        total_latency_s: 5.7,
        terminal_state: "COMPLETE",
        terminal_state_reason: "TOTAL_LATENCY_OBSERVED",
        stage_count: 4,
        observed_stage_count: 4,
        pending_stage_count: 0,
        stages: []
      },
      correlation: {
        trace_id: "trace:svc-02",
        service_id: "svc-02-compute_service-00000",
        task_id: "svc-02-compute_service-00000-task",
        flow_ids: [
          "svc-02-compute_service-00000-input",
          "svc-02-compute_service-00000-output"
        ],
        route_ids: ["route:input-02", "route:output-02"],
        user_ids: ["user-7"],
        satellite_ids: ["sat-00002", "sat-00003"],
        compute_node_id: "sat-00002",
        route_count: 2,
        user_count: 1,
        satellite_count: 2,
        compute_node_detail_available: false
      },
      routes: [],
      users: [],
      satellites: [],
      compute_node: null
    });

    expect(focus).toMatchObject({
      active: true,
      sourceLabel: "后端精确服务链路聚焦",
      detailFilter: "sat-00002",
      routeFilter: "route:input-02",
      serviceFilter: "svc-02-compute_service-00000",
      serviceTraceFilter: "trace:svc-02",
      computeNodeFilter: "sat-00002",
      traceId: "trace:svc-02",
      serviceId: "svc-02-compute_service-00000",
      routeIds: ["route:input-02", "route:output-02"],
      flowIds: [
        "svc-02-compute_service-00000-input",
        "svc-02-compute_service-00000-output"
      ],
      userIds: ["user-7"],
      satelliteIds: ["sat-00002", "sat-00003"],
      computeNodeId: "sat-00002"
    });
    expect(focus.summaryLabel).toContain("2 路由");
    expect(focus.summaryLabel).toContain("1 用户");
  });

  it("builds visible-window service trace focus filters", () => {
    const display = buildDataPanelServiceLifecycleTraceDisplay({
      version: "v2",
      source: "SERVICE_LATENCY_HISTORY",
      source_summary: "service_latency_history_v1",
      summary_scope: "SERVICE_LIFECYCLE_TRACE_WINDOW",
      cursor: 0,
      limit: 100,
      next_cursor: 1,
      has_more: false,
      service_count: 1,
      trace_count: 1,
      complete_trace_count: 0,
      running_trace_count: 1,
      incomplete_trace_count: 0,
      hidden_trace_count: 0,
      items: [
        {
          trace_id: "trace:run",
          service_id: "svc-run-compute_service-00000",
          task_id: "svc-run-compute_service-00000-task",
          service_class: "COMPUTE_SERVICE",
          input_flow_id: "svc-run-compute_service-00000-input",
          output_flow_id: "svc-run-compute_service-00000-output",
          input_route_id: "route:run-input",
          output_route_id: "route:run-output",
          compute_node_id: "sat-00001",
          input_network_latency_s: 1,
          compute_queue_delay_s: 0.1,
          compute_execution_delay_s: 2,
          output_network_latency_s: 0,
          total_latency_s: 0,
          terminal_state: "RUNNING",
          terminal_state_reason: "OUTPUT_NETWORK_PENDING",
          stage_count: 4,
          observed_stage_count: 3,
          pending_stage_count: 1,
          stages: []
        }
      ]
    });
    const focus = buildDataPanelServiceTraceFocus(display.items[0]);

    expect(focus).toMatchObject({
      active: true,
      sourceLabel: "窗口服务链路聚焦",
      detailFilter: "sat-00001",
      routeFilter: "route:run-input",
      serviceFilter: "svc-run-compute_service-00000",
      serviceTraceFilter: "trace:run",
      computeNodeFilter: "sat-00001",
      userIds: [],
      satelliteIds: ["sat-00001"]
    });
    expect(focus.summaryLabel).toContain("2 路由");
    expect(focus.summaryLabel).toContain("2 流");
  });

  it("keeps service trace focus inactive before selection", () => {
    expect(buildDataPanelServiceTraceFocus(null)).toEqual({
      active: false,
      sourceLabel: "服务链路聚焦",
      summaryLabel: "等待选择服务 trace",
      detailFilter: "",
      routeFilter: "",
      serviceFilter: "",
      serviceTraceFilter: "",
      computeNodeFilter: "",
      traceId: "",
      serviceId: "",
      routeIds: [],
      flowIds: [],
      userIds: [],
      satelliteIds: [],
      computeNodeId: ""
    });
  });

  it("correlates a selected trace with user, route, satellite, and compute rows", () => {
    const display = buildDataPanelServiceLifecycleTraceDisplay({
      version: "v2",
      source: "SERVICE_LATENCY_HISTORY",
      source_summary: "service_latency_history_v1",
      summary_scope: "SERVICE_LIFECYCLE_TRACE_WINDOW",
      cursor: 0,
      limit: 100,
      next_cursor: 1,
      has_more: false,
      service_count: 1,
      trace_count: 1,
      complete_trace_count: 1,
      running_trace_count: 0,
      incomplete_trace_count: 0,
      hidden_trace_count: 0,
      items: [
        {
          trace_id: "trace:svc-02",
          service_id: "svc-02-compute_service-00000",
          task_id: "svc-02-compute_service-00000-task",
          service_class: "COMPUTE_SERVICE",
          input_flow_id: "svc-02-compute_service-00000-input",
          output_flow_id: "svc-02-compute_service-00000-output",
          input_route_id: "route:input-02",
          output_route_id: "route:output-02",
          compute_node_id: "sat-00002",
          placement_status: "PLACED",
          first_sample_sim_time: 2,
          last_sample_sim_time: 9,
          input_network_latency_s: 1,
          compute_queue_delay_s: 0.2,
          compute_execution_delay_s: 3,
          output_network_latency_s: 1.5,
          total_latency_s: 5.7,
          terminal_state: "COMPLETE",
          terminal_state_reason: "TOTAL_LATENCY_OBSERVED",
          stage_count: 4,
          observed_stage_count: 4,
          pending_stage_count: 0,
          stages: []
        }
      ]
    });
    const selected = selectServiceLifecycleTraceRow(
      display.items,
      "trace:svc-02"
    );
    const inspector = buildServiceTraceCorrelationInspector(
      selected,
      {
        sourceLabel: "users",
        summaryLabel: "1 user",
        items: [
          {
            userId: "user-7",
            platformTypeLabel: "terminal",
            communicationLabel: "1 / 1 routes",
            computeLabel: "1 compute",
            networkQueueLabel: "empty",
            selectedSatelliteId: "sat-00002",
            destinationId: "sat-00002",
            placementLabel: "sat-00002",
            statusLabel: "ACTIVE",
            latencyCapacityLabel: "1 s / 10 Mbps",
            serviceLabel: "svc-02-compute_service-00000-input",
            pathLabel: "route:input-02: user-7 -> sat-00002"
          }
        ]
      },
      {
        sourceLabel: "routes",
        items: [
          {
            routeId: "route:input-02",
            flowId: "svc-02-compute_service-00000-input",
            available: true,
            availabilityLabel: "available",
            businessType: "COMPUTE_SERVICE",
            businessLabel: "compute",
            nextHopLabel: "sat-00002",
            capacityDemandLabel: "10 / 5 Mbps",
            pressureLabel: "50%",
            bottleneckComponent: "NONE",
            bottleneckLabel: "none",
            explanationLabel: "route ready",
            pathLabel: "user-7 -> sat-00002 -> compute"
          }
        ]
      },
      {
        sourceLabel: "satellites",
        summaryLabel: "1 satellite",
        items: [
          {
            satelliteId: "sat-00002",
            statusLabel: "ACTIVE",
            loadPercent: 42,
            loadLabel: "42%",
            serviceObjectLabel: "user-7",
            nextHopLabel: "compute",
            cpuFp32Label: "4 / 10 GFLOPS",
            cpuFp64Label: "0 / 2 GFLOPS",
            gpuLabel: "0 / 1 TFLOPS",
            npuLabel: "0 / 1 TOPS",
            memoryStorageLabel: "1 / 4 GB",
            taskLabel: "1 running",
            networkLabel: "1 link"
          }
        ]
      },
      {
        sourceLabel: "compute",
        summaryLabel: "1 node",
        items: [
          {
            nodeId: "sat-00002",
            statusLabel: "BUSY",
            loadLabel: "42%",
            fp32Label: "4 / 10 GFLOPS",
            acceleratorLabel: "GPU 0 / 1 TFLOPS",
            memoryStorageLabel: "1 / 4 GB",
            taskLabel: "1 running",
            traceTitle: "node=sat-00002"
          }
        ]
      }
    );

    expect(selected?.serviceId).toBe("svc-02-compute_service-00000");
    expect(inspector).toMatchObject({
      title: "服务 trace ...e_service-00000",
      subtitle: "完成 / TOTAL_LATENCY_OBSERVED",
      fields: expect.arrayContaining([
        { label: "用户", value: "user-7 / svc-02-compute_service-00000-input", tone: "resource" },
        { label: "卫星", value: "sat-00002 / 42%", tone: "resource" },
        { label: "算力节点", value: "sat-00002 / 42%", tone: "resource" },
        { label: "下一跳", value: "sat-00002" }
      ])
    });
  });

  it("prefers backend exact service trace details over visible-window correlation", () => {
    const display = buildDataPanelServiceLifecycleTraceDisplay({
      version: "v2",
      source: "BACKEND_RUNTIME_EXPORT",
      source_summary: "latest export",
      summary_scope: "LATEST_RUNTIME_EXPORT",
      trace_model: "COMMUNICATION_COMPUTE_SERVICE_LIFECYCLE",
      cursor: 0,
      limit: 100,
      next_cursor: 1,
      has_more: false,
      service_count: 1,
      trace_count: 1,
      complete_trace_count: 1,
      running_trace_count: 0,
      incomplete_trace_count: 0,
      hidden_trace_count: 0,
      items: [
        {
          trace_id: "trace:svc-02",
          service_id: "svc-02-compute_service-00000",
          task_id: "svc-02-compute_service-00000-task",
          service_class: "COMPUTE_SERVICE",
          input_flow_id: "svc-02-compute_service-00000-input",
          output_flow_id: "svc-02-compute_service-00000-output",
          input_route_id: "route:input-02",
          output_route_id: "route:output-02",
          compute_node_id: "sat-00002",
          placement_status: "PLACED",
          first_sample_sim_time: 2,
          last_sample_sim_time: 9,
          input_network_latency_s: 1,
          compute_queue_delay_s: 0.2,
          compute_execution_delay_s: 3,
          output_network_latency_s: 1.5,
          total_latency_s: 5.7,
          terminal_state: "COMPLETE",
          terminal_state_reason: "TOTAL_LATENCY_OBSERVED",
          stage_count: 4,
          observed_stage_count: 4,
          pending_stage_count: 0,
          stages: []
        }
      ]
    });
    const selected = selectServiceLifecycleTraceRow(
      display.items,
      "trace:svc-02"
    );
    const backendDetail = {
      version: "v2",
      source: "BACKEND_RUNTIME_DETAIL",
      summary_scope: "SERVICE_TRACE_EXACT_DETAIL",
      detail_hash: "sha256:live-trace-detail",
      trace: {
        trace_id: "trace:svc-02",
        service_id: "svc-02-compute_service-00000",
        task_id: "svc-02-compute_service-00000-task",
        service_class: "COMPUTE_SERVICE",
        input_flow_id: "svc-02-compute_service-00000-input",
        output_flow_id: "svc-02-compute_service-00000-output",
        input_route_id: "route:input-02",
        output_route_id: "route:output-02",
        compute_node_id: "sat-00002",
        placement_status: "PLACED",
        input_network_latency_s: 1,
        compute_queue_delay_s: 0.2,
        compute_execution_delay_s: 3,
        output_network_latency_s: 1.5,
        total_latency_s: 5.7,
        terminal_state: "COMPLETE",
        terminal_state_reason: "TOTAL_LATENCY_OBSERVED",
        stage_count: 4,
        observed_stage_count: 4,
        pending_stage_count: 0,
        stages: []
      },
      correlation: {
        trace_id: "trace:svc-02",
        service_id: "svc-02-compute_service-00000",
        task_id: "svc-02-compute_service-00000-task",
        flow_ids: [
          "svc-02-compute_service-00000-input",
          "svc-02-compute_service-00000-output"
        ],
        route_ids: ["route:input-02", "route:output-02"],
        user_ids: ["user-7"],
        satellite_ids: ["sat-00002", "sat-00003"],
        compute_node_id: "sat-00002",
        route_count: 2,
        user_count: 1,
        satellite_count: 2,
        compute_node_detail_available: false
      },
      routes: [],
      users: [],
      satellites: [],
      compute_node: null
    };
    const emptyUsers = { sourceLabel: "users", summaryLabel: "0 users", items: [] };
    const emptyRoutes = { sourceLabel: "routes", items: [] };
    const emptySatellites = {
      sourceLabel: "satellites",
      summaryLabel: "0 satellites",
      items: []
    };
    const emptyComputeNodes = {
      sourceLabel: "compute",
      summaryLabel: "0 nodes",
      items: []
    };

    expect(serviceTraceDetailMatchesRow(backendDetail, selected)).toBe(true);

    const inspector = buildServiceTraceCorrelationInspector(
      selected,
      emptyUsers,
      emptyRoutes,
      emptySatellites,
      emptyComputeNodes,
      backendDetail
    );

    expect(inspector.fields).toEqual(
      expect.arrayContaining([
        { label: "source", value: "backend exact detail", tone: "resource" },
        { label: "users", value: "user-7", tone: "resource" },
        {
          label: "satellites",
          value: "sat-00002 / sat-00003",
          tone: "resource"
        },
        { label: "compute node", value: "sat-00002", tone: "resource" }
      ])
    );
  });

  it("summarizes backend exact service trace correlation evidence", () => {
    const traceRow = {
      traceId: "trace:svc-02",
      serviceId: "svc-02-compute_service-00000",
      taskId: "svc-02-compute_service-00000-task",
      inputFlowId: "svc-02-compute_service-00000-input",
      outputFlowId: "svc-02-compute_service-00000-output",
      inputRouteId: "route:input-02",
      outputRouteId: "route:output-02",
      computeNodeId: "sat-00002",
      primaryRouteId: "route:input-02",
      routeIds: ["route:input-02", "route:output-02"],
      flowIds: [
        "svc-02-compute_service-00000-input",
        "svc-02-compute_service-00000-output"
      ],
      serviceLabel: "...e_service-00000",
      terminalState: "COMPLETE",
      terminalStateReason: "TOTAL_LATENCY_OBSERVED",
      terminalStateLabel: "完成 / TOTAL_LATENCY_OBSERVED",
      computeNodeLabel: "算力 sat-00002",
      networkLatencyLabel: "1000.00 ms / 1500.00 ms",
      computeLatencyLabel: "200.00 ms / 3000.00 ms",
      totalLatencyLabel: "5700.00 ms",
      traceTitle: "trace:svc-02",
      artifactFilename: "service_lifecycle_trace_v2.json",
      artifactPointer: "/items/0",
      artifactFilter: "trace:svc-02",
      stages: []
    };
    const note = buildDataPanelServiceTraceCorrelationEvidenceNote({
      trace: traceRow,
      users: { sourceLabel: "users", summaryLabel: "0 users", items: [] },
      routes: { sourceLabel: "routes", items: [] },
      satellites: {
        sourceLabel: "satellites",
        summaryLabel: "0 satellites",
        items: []
      },
      computeNodes: {
        sourceLabel: "compute",
        summaryLabel: "0 nodes",
        items: []
      },
      backendDetail: {
        version: "v2",
        source: "BACKEND_RUNTIME_DETAIL",
        summary_scope: "SERVICE_TRACE_EXACT_DETAIL",
        detail_hash: "sha256:live-trace-detail",
        trace: {
          trace_id: "trace:svc-02",
          service_id: "svc-02-compute_service-00000",
          task_id: "svc-02-compute_service-00000-task",
          service_class: "COMPUTE_SERVICE",
          input_flow_id: "svc-02-compute_service-00000-input",
          output_flow_id: "svc-02-compute_service-00000-output",
          input_route_id: "route:input-02",
          output_route_id: "route:output-02",
          compute_node_id: "sat-00002",
          placement_status: "PLACED",
          input_network_latency_s: 1,
          compute_queue_delay_s: 0.2,
          compute_execution_delay_s: 3,
          output_network_latency_s: 1.5,
          total_latency_s: 5.7,
          terminal_state: "COMPLETE",
          terminal_state_reason: "TOTAL_LATENCY_OBSERVED",
          stage_count: 4,
          observed_stage_count: 4,
          pending_stage_count: 0,
          stages: []
        },
        correlation: {
          trace_id: "trace:svc-02",
          service_id: "svc-02-compute_service-00000",
          task_id: "svc-02-compute_service-00000-task",
          flow_ids: [
            "svc-02-compute_service-00000-input",
            "svc-02-compute_service-00000-output"
          ],
          route_ids: ["route:input-02", "route:output-02"],
          user_ids: ["user-7"],
          satellite_ids: ["sat-00002", "sat-00003"],
          compute_node_id: "sat-00002",
          route_count: 2,
          user_count: 1,
          satellite_count: 2,
          compute_node_detail_available: false
        },
        routes: [],
        users: [],
        satellites: [],
        compute_node: null
      }
    });

    expect(note).toMatchObject({
      label: "服务链路闭环",
      value: "5 / 5 后端精确",
      tone: "backend"
    });
    expect(note.detail).toContain("后端精确详情");
    expect(note.detail).toContain("路由 2");
    expect(note.detail).toContain("用户 1");
    expect(note.detail).toContain("卫星 2");
    expect(note.detail).toContain("算力节点 sat-00002");
    expect(note.detail).toContain("阶段 4 已观测 / 0 待观测 / 4 合计");
    expect(note.detail).toContain("时延 输入网络");
  });

  it("summarizes visible-window service trace correlation evidence", () => {
    const traceRow = {
      traceId: "trace:svc-02",
      serviceId: "svc-02-compute_service-00000",
      taskId: "svc-02-compute_service-00000-task",
      inputFlowId: "svc-02-compute_service-00000-input",
      outputFlowId: "svc-02-compute_service-00000-output",
      inputRouteId: "route:input-02",
      outputRouteId: "route:output-02",
      computeNodeId: "sat-00002",
      primaryRouteId: "route:input-02",
      routeIds: ["route:input-02", "route:output-02"],
      flowIds: [
        "svc-02-compute_service-00000-input",
        "svc-02-compute_service-00000-output"
      ],
      serviceLabel: "...e_service-00000",
      terminalState: "RUNNING",
      terminalStateReason: "OUTPUT_NETWORK_PENDING",
      terminalStateLabel: "运行 / OUTPUT_NETWORK_PENDING",
      computeNodeLabel: "算力 sat-00002",
      networkLatencyLabel: "1000.00 ms / 1500.00 ms",
      computeLatencyLabel: "200.00 ms / 3000.00 ms",
      totalLatencyLabel: "5700.00 ms",
      traceTitle: "trace:svc-02",
      artifactFilename: "service_lifecycle_trace_v2.json",
      artifactPointer: "/items/0",
      artifactFilter: "trace:svc-02",
      stages: [
        {
          stageId: "stage-input",
          component: "network",
          stageKind: "INPUT_NETWORK",
          stageStatus: "OBSERVED",
          label: "输入网络",
          statusLabel: "已观测",
          durationLabel: "1000.00 ms",
          traceTitle: "input"
        },
        {
          stageId: "stage-output",
          component: "network",
          stageKind: "OUTPUT_NETWORK",
          stageStatus: "PENDING",
          label: "输出网络",
          statusLabel: "等待",
          durationLabel: "0.00 ms",
          traceTitle: "output"
        }
      ]
    };
    const note = buildDataPanelServiceTraceCorrelationEvidenceNote({
      trace: traceRow,
      users: {
        sourceLabel: "users",
        summaryLabel: "1 user",
        items: [
          {
            userId: "user-7",
            platformTypeLabel: "terminal",
            communicationLabel: "1 / 1 routes",
            computeLabel: "1 compute",
            networkQueueLabel: "empty",
            selectedSatelliteId: "sat-00002",
            destinationId: "sat-00002",
            placementLabel: "sat-00002",
            statusLabel: "ACTIVE",
            latencyCapacityLabel: "1 s / 10 Mbps",
            serviceLabel: "svc-02-compute_service-00000-input",
            pathLabel: "route:input-02: user-7 -> sat-00002"
          }
        ]
      },
      routes: {
        sourceLabel: "routes",
        items: [
          {
            routeId: "route:input-02",
            flowId: "svc-02-compute_service-00000-input",
            available: true,
            availabilityLabel: "available",
            businessType: "COMPUTE_SERVICE",
            businessLabel: "compute",
            nextHopLabel: "sat-00002",
            capacityDemandLabel: "10 / 5 Mbps",
            pressureLabel: "50%",
            bottleneckComponent: "NONE",
            bottleneckLabel: "none",
            explanationLabel: "route ready",
            pathLabel: "user-7 -> sat-00002 -> compute"
          }
        ]
      },
      satellites: {
        sourceLabel: "satellites",
        summaryLabel: "1 satellite",
        items: [
          {
            satelliteId: "sat-00002",
            statusLabel: "ACTIVE",
            loadPercent: 42,
            loadLabel: "42%",
            serviceObjectLabel: "user-7",
            nextHopLabel: "compute",
            cpuFp32Label: "4 / 10 GFLOPS",
            cpuFp64Label: "0 / 2 GFLOPS",
            gpuLabel: "0 / 1 TFLOPS",
            npuLabel: "0 / 1 TOPS",
            memoryStorageLabel: "1 / 4 GB",
            taskLabel: "1 running",
            networkLabel: "1 link"
          }
        ]
      },
      computeNodes: {
        sourceLabel: "compute",
        summaryLabel: "1 node",
        items: [
          {
            nodeId: "sat-00002",
            statusLabel: "BUSY",
            loadLabel: "42%",
            fp32Label: "4 / 10 GFLOPS",
            acceleratorLabel: "GPU 0 / 1 TFLOPS",
            memoryStorageLabel: "1 / 4 GB",
            taskLabel: "1 running",
            traceTitle: "node=sat-00002"
          }
        ]
      }
    });

    expect(note).toMatchObject({
      label: "服务链路闭环",
      value: "5 / 5 窗口匹配",
      tone: "history"
    });
    expect(note.detail).toContain("当前窗口关联");
    expect(note.detail).toContain("流 2");
    expect(note.detail).toContain("路由 1");
    expect(note.detail).toContain("用户 1");
    expect(note.detail).toContain("卫星 1");
    expect(note.detail).toContain("阶段 1 已观测 / 1 待观测 / 2 窗口样本");
  });

  it("shows a waiting service trace correlation evidence note before selection", () => {
    const note = buildDataPanelServiceTraceCorrelationEvidenceNote({
      trace: null,
      users: { sourceLabel: "users", summaryLabel: "0 users", items: [] },
      routes: { sourceLabel: "routes", items: [] },
      satellites: {
        sourceLabel: "satellites",
        summaryLabel: "0 satellites",
        items: []
      },
      computeNodes: {
        sourceLabel: "compute",
        summaryLabel: "0 nodes",
        items: []
      }
    });

    expect(note).toEqual({
      label: "服务链路闭环",
      value: "等待选择",
      detail:
        "选择一条服务链路后，将核对服务、流、路由、用户、卫星、算力节点和阶段时延是否来自同一条后端语义链。",
      tone: "history"
    });
  });

  it("builds a backend exact service trace detail drawer", () => {
    const item = buildServiceTraceDetailDrawerItem(
      {
        version: "v2",
        source: "BACKEND_RUNTIME_DETAIL",
        summary_scope: "SERVICE_TRACE_EXACT_DETAIL",
        detail_hash: "sha256:live-trace-detail",
        trace: {
          trace_id: "trace:svc-02",
          service_id: "svc-02-compute_service-00000",
          task_id: "svc-02-compute_service-00000-task",
          service_class: "COMPUTE_SERVICE",
          input_flow_id: "svc-02-compute_service-00000-input",
          output_flow_id: "svc-02-compute_service-00000-output",
          input_route_id: "route:input-02",
          output_route_id: "route:output-02",
          compute_node_id: "sat-00002",
          placement_status: "PLACED",
          input_network_latency_s: 1,
          compute_queue_delay_s: 0.2,
          compute_execution_delay_s: 3,
          output_network_latency_s: 1.5,
          total_latency_s: 5.7,
          terminal_state: "COMPLETE",
          terminal_state_reason: "TOTAL_LATENCY_OBSERVED",
          stage_count: 4,
          observed_stage_count: 4,
          pending_stage_count: 0,
          stages: []
        },
        correlation: {
          trace_id: "trace:svc-02",
          service_id: "svc-02-compute_service-00000",
          task_id: "svc-02-compute_service-00000-task",
          flow_ids: [
            "svc-02-compute_service-00000-input",
            "svc-02-compute_service-00000-output"
          ],
          route_ids: ["route:input-02", "route:output-02"],
          user_ids: ["user-7"],
          satellite_ids: ["sat-00002"],
          compute_node_id: "sat-00002",
          route_count: 2,
          user_count: 1,
          satellite_count: 1,
          compute_node_detail_available: true
        },
        routes: [
          {
            route_id: "route:input-02",
            flow_id: "svc-02-compute_service-00000-input",
            user_id: "user-7",
            source_id: "user-7",
            destination_id: "sat-00002",
            selected_satellite_id: "sat-00002",
            primary_next_hop_id: "sat-00002",
            next_hop_ids: ["sat-00002"],
            hop_count: 1,
            path_label: "user-7 -> sat-00002",
            available: true,
            capacity_mbps: 100,
            demand_mbps: 10,
            latency_s: 1,
            loss_proxy_rate: 0.01,
            route_pressure_proxy: 0.1,
            business_type: "COMPUTE_SERVICE",
            business_label: "compute",
            bottleneck_component: "NONE",
            bottleneck_reason: "NONE",
            bottleneck_reason_label: "no bottleneck",
            explanation_label: "route ready"
          }
        ],
        users: [
          {
            entity_type: "USER",
            entity_id: "user-7",
            title: "用户 user-7",
            subtitle: "ACTIVE",
            fields: [{ label: "业务", value: "compute", tone: "resource" }]
          }
        ],
        satellites: [
          {
            entity_type: "SATELLITE",
            entity_id: "sat-00002",
            title: "卫星 sat-00002",
            subtitle: "BUSY",
            fields: [{ label: "负载", value: "42%", tone: "resource" }]
          }
        ],
        compute_node: {
          node_id: "sat-00002",
          platform_type: "SATELLITE",
          status: "BUSY",
          compute_load_ratio: 0.42,
          compute_capacity_gflops_fp32: 100,
          compute_used_gflops_fp32: 42,
          compute_available_gflops_fp32: 58,
          compute_capacity_gflops_fp64: 50,
          compute_used_gflops_fp64: 1,
          compute_capacity_gpu_tflops_fp32: 2,
          compute_used_gpu_tflops_fp32: 0.5,
          compute_capacity_gpu_tflops_fp16: 4,
          compute_used_gpu_tflops_fp16: 1,
          compute_capacity_npu_tops_int8: 8,
          compute_used_npu_tops_int8: 2,
          compute_capacity_memory_gb: 32,
          compute_used_memory_gb: 12,
          compute_capacity_storage_gb: 256,
          compute_used_storage_gb: 64,
          running_task_count: 1,
          finished_task_count: 3
        }
      },
      { title: "fallback", subtitle: "loading", fields: [] }
    );

    expect(item).toMatchObject({
      kind: "service_trace",
      title: "服务 trace ...e_service-00000",
      fields: expect.arrayContaining([
        { label: "服务", value: "svc-02-compute_service-00000" },
        { label: "用户", value: "user-7" },
        { label: "卫星", value: "sat-00002" }
      ])
    });
    expect(item.sections.map((section) => section.sectionId)).toEqual(
      expect.arrayContaining([
        "service_trace_lifecycle",
        "service_trace_correlation",
        "service_trace_routes",
        "service_trace_user_0_summary",
        "service_trace_satellite_0_summary",
        "service_trace_compute_node"
      ])
    );
    expect(
      item.sections.find((section) => section.sectionId === "service_trace_routes")
        ?.fields[0]
    ).toMatchObject({
      label: "route:input-02",
      tone: "resource"
    });
  });

  it("builds a backend exact service trace wide browser display", () => {
    const display = buildDataPanelServiceTraceBrowserDisplay(
      {
        version: "v2",
        source: "BACKEND_RUNTIME_DETAIL",
        summary_scope: "SERVICE_TRACE_EXACT_DETAIL",
        detail_hash: "sha256:live-trace-detail",
        trace: {
          trace_id: "trace:svc-02",
          service_id: "svc-02-compute_service-00000",
          task_id: "svc-02-compute_service-00000-task",
          service_class: "COMPUTE_SERVICE",
          input_flow_id: "svc-02-compute_service-00000-input",
          output_flow_id: "svc-02-compute_service-00000-output",
          input_route_id: "route:input-02",
          output_route_id: "route:output-02",
          compute_node_id: "sat-00002",
          placement_status: "PLACED",
          input_network_latency_s: 1,
          compute_queue_delay_s: 0.2,
          compute_execution_delay_s: 3,
          output_network_latency_s: 1.5,
          total_latency_s: 5.7,
          terminal_state: "COMPLETE",
          terminal_state_reason: "TOTAL_LATENCY_OBSERVED",
          stage_count: 4,
          observed_stage_count: 4,
          pending_stage_count: 0,
          stages: []
        },
        correlation: {
          trace_id: "trace:svc-02",
          service_id: "svc-02-compute_service-00000",
          task_id: "svc-02-compute_service-00000-task",
          flow_ids: [
            "svc-02-compute_service-00000-input",
            "svc-02-compute_service-00000-output"
          ],
          route_ids: ["route:input-02", "route:output-02"],
          user_ids: ["user-7"],
          satellite_ids: ["sat-00002"],
          compute_node_id: "sat-00002",
          route_count: 2,
          user_count: 1,
          satellite_count: 1,
          compute_node_detail_available: true
        },
        routes: [
          {
            route_id: "route:input-02",
            flow_id: "svc-02-compute_service-00000-input",
            user_id: "user-7",
            source_id: "user-7",
            destination_id: "sat-00002",
            selected_satellite_id: "sat-00002",
            primary_next_hop_id: "sat-00002",
            next_hop_ids: ["sat-00002"],
            hop_count: 1,
            path_label: "user-7 -> sat-00002",
            available: true,
            capacity_mbps: 100,
            demand_mbps: 10,
            latency_s: 1,
            loss_proxy_rate: 0.01,
            route_pressure_proxy: 0.1,
            business_type: "COMPUTE_SERVICE",
            business_label: "compute",
            bottleneck_component: "NONE",
            bottleneck_reason: "NONE",
            bottleneck_reason_label: "no bottleneck",
            explanation_label: "route ready"
          }
        ],
        users: [
          {
            entity_type: "USER",
            entity_id: "user-7",
            title: "用户 user-7",
            subtitle: "ACTIVE",
            fields: [{ label: "业务", value: "compute", tone: "resource" }]
          }
        ],
        satellites: [],
        compute_node: {
          node_id: "sat-00002",
          platform_type: "SATELLITE",
          status: "BUSY",
          compute_load_ratio: 0.42,
          compute_capacity_gflops_fp32: 100,
          compute_used_gflops_fp32: 42,
          compute_available_gflops_fp32: 58,
          compute_capacity_gflops_fp64: 50,
          compute_used_gflops_fp64: 1,
          compute_capacity_gpu_tflops_fp32: 2,
          compute_used_gpu_tflops_fp32: 0.5,
          compute_capacity_gpu_tflops_fp16: 4,
          compute_used_gpu_tflops_fp16: 1,
          compute_capacity_npu_tops_int8: 8,
          compute_used_npu_tops_int8: 2,
          compute_capacity_memory_gb: 32,
          compute_used_memory_gb: 12,
          compute_capacity_storage_gb: 256,
          compute_used_storage_gb: 64,
          running_task_count: 1,
          finished_task_count: 3
        }
      },
      { title: "fallback", subtitle: "loading", fields: [] }
    );

    expect(display).toMatchObject({
      active: true,
      sourceLabel: "后端精确服务链路详情",
      title: "服务 trace ...e_service-00000",
      summaryFields: expect.arrayContaining([
        { label: "服务", value: "svc-02-compute_service-00000" },
        { label: "用户", value: "user-7" },
        { label: "卫星", value: "sat-00002" }
      ])
    });
    expect(display.summaryLabel).toContain("5 组详情");
    expect(display.sections.map((section) => section.sectionId)).toEqual(
      expect.arrayContaining([
        "service_trace_lifecycle",
        "service_trace_correlation",
        "service_trace_routes",
        "service_trace_user_0_summary",
        "service_trace_compute_node"
      ])
    );
  });

  it("builds a visible-window service trace wide browser fallback", () => {
    const display = buildDataPanelServiceTraceBrowserDisplay(null, {
      title: "服务 trace ...e_service-00000",
      subtitle: "完成 / TOTAL_LATENCY_OBSERVED",
      fields: [
        { label: "服务", value: "svc-02-compute_service-00000" },
        { label: "路由", value: "route:input-02", tone: "resource" }
      ]
    });

    expect(display).toMatchObject({
      active: true,
      sourceLabel: "当前窗口服务链路详情",
      title: "服务 trace ...e_service-00000",
      summaryLabel: "1 组详情 / 0 路由组 / 0 节点组"
    });
    expect(display.sections).toEqual([
      {
        sectionId: "service_trace_visible_window",
        title: "当前窗口关联",
        fields: [
          { label: "服务", value: "svc-02-compute_service-00000" },
          { label: "路由", value: "route:input-02", tone: "resource" }
        ]
      }
    ]);
  });

  it("keeps the service trace wide browser empty before selection", () => {
    expect(
      buildDataPanelServiceTraceBrowserDisplay(null, {
        title: "服务 trace 关联",
        subtitle: "选择一条 service_lifecycle_trace_v2",
        fields: []
      })
    ).toEqual({
      active: false,
      sourceLabel: "当前窗口服务链路详情",
      title: "服务链路宽详情",
      subtitle: "等待选择服务 trace",
      emptyLabel: "选择一条服务 trace 后显示后端精确详情",
      summaryLabel: "等待选择",
      summaryFields: [],
      sections: []
    });
  });

  it("keeps the fallback inspector while service trace detail is loading", () => {
    const item = buildServiceTraceDetailDrawerItem(null, {
      title: "trace loading",
      subtitle: "waiting",
      fields: [{ label: "source", value: "visible window" }]
    });

    expect(item).toEqual({
      kind: "service_trace",
      title: "trace loading",
      subtitle: "waiting",
      emptyLabel: "选择一条服务 trace 后显示后端精确详情",
      sections: [],
      fields: [{ label: "source", value: "visible window" }]
    });
  });

  it("returns a backend waiting state before trace v2 arrives", () => {
    expect(buildDataPanelServiceLifecycleTraceDisplay(null)).toEqual({
      sourceLabel: "等待后端 service_lifecycle_trace_v2",
      summaryLabel: "暂无通信-计算服务 trace",
      items: []
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

describe("buildDataPanelComputeNodeDetailRows", () => {
  it("formats backend cursor compute-node resource detail rows", () => {
    const rows = buildDataPanelComputeNodeDetailRows(
      {
        version: "v1",
        source: "BACKEND_RUNTIME_SNAPSHOT",
        summary_scope: "COMPUTE_NODE_DETAIL_WINDOW",
        cursor: 0,
        limit: 2,
        next_cursor: 1,
        has_more: true,
        compute_node_count: 2,
        item_count: 1,
        busy_compute_node_count: 1,
        window_compute_node_count: 1,
        hidden_compute_node_count: 1,
        items: [
          {
            node_id: "sat-000",
            platform_type: "SATELLITE_COMPUTE_NODE",
            status: "BUSY",
            compute_load_ratio: 0.75,
            compute_capacity_gflops_fp32: 100,
            compute_used_gflops_fp32: 75,
            compute_available_gflops_fp32: 25,
            compute_capacity_gflops_fp64: 10,
            compute_used_gflops_fp64: 2,
            compute_capacity_gpu_tflops_fp32: 2,
            compute_used_gpu_tflops_fp32: 1,
            compute_capacity_gpu_tflops_fp16: 4,
            compute_used_gpu_tflops_fp16: 2,
            compute_capacity_npu_tops_int8: 8,
            compute_used_npu_tops_int8: 3,
            compute_capacity_memory_gb: 32,
            compute_used_memory_gb: 8,
            compute_capacity_storage_gb: 512,
            compute_used_storage_gb: 128,
            running_task_count: 2,
            finished_task_count: 7
          }
        ]
      },
      1
    );

    expect(rows).toMatchObject({
      sourceLabel: "后端算力节点详情页 1 / 2",
      summaryLabel: "1 行 / 忙碌 1 / 可继续游标读取",
      items: [
        {
          nodeId: "sat-000",
          statusLabel: "BUSY",
          loadLabel: "75%",
          fp32Label: "75 / 100 GFLOPS",
          acceleratorLabel: "GPU 1 / 2 TFLOPS / NPU 3 / 8 TOPS",
          memoryStorageLabel: "内存 8 / 32 GB / 存储 128 / 512 GB",
          taskLabel: "2 运行 / 7 完成"
        }
      ]
    });
    expect(rows.items[0].traceTitle).toContain("node=sat-000");
    expect(rows.items[0].traceTitle).toContain("gpu_fp32=1 / 2 TFLOPS");
  });

  it("returns an empty waiting state before backend compute-node pages arrive", () => {
    expect(buildDataPanelComputeNodeDetailRows(undefined)).toEqual({
      sourceLabel: "等待后端算力节点详情页",
      summaryLabel: "暂无算力节点游标明细",
      items: []
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

  it("labels backend user service request v2 summaries", () => {
    const backendSummary: RuntimeUserServiceRequestSummaryV2 = {
      version: "v2",
      source: "BACKEND_RUNTIME_STATUS",
      request_model: "FLOW_LEVEL_USER_SERVICE_REQUEST_PROXY",
      route_model: "FLOW_LEVEL_ROUTE_PROXY",
      compute_model: "SERVICE_LIFECYCLE_PROXY",
      packet_level_simulation: false,
      frontend_inference_required: false,
      user_count: 1,
      request_count: 1,
      item_count: 1,
      active_user_count: 1,
      active_request_count: 1,
      communication_request_count: 1,
      compute_service_user_count: 0,
      compute_request_count: 0,
      waiting_user_count: 0,
      network_waiting_request_count: 0,
      completed_request_count: 0,
      window_user_count: 1,
      window_request_count: 1,
      window_active_user_count: 1,
      window_active_request_count: 1,
      window_compute_service_user_count: 0,
      window_compute_request_count: 0,
      window_waiting_user_count: 0,
      window_network_waiting_request_count: 0,
      hidden_user_count: 0,
      hidden_request_count: 0,
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
          primary_route_id: "route-a",
          primary_flow_id: "flow-a",
          primary_next_hop_id: "sat-0",
          active_business_type: "DATA_TRANSFER",
          active_business_label: "Data transfer",
          request_state: "NETWORK_SERVICE_READY",
          request_state_label: "Network service route ready",
          path: ["user-0", "sat-0", "service-0"],
          request_id: "flow-a",
          service_request_id: "flow-a",
          service_class: "DATA_TRANSFER",
          service_class_label: "Data transfer",
          business_type: "DATA_TRANSFER",
          business_label: "Data transfer",
          request_active: true,
          communication_request_active: true,
          compute_request_active: false,
          network_waiting: false,
          terminal_state: "RUNNING_NETWORK_SERVICE",
          terminal_state_label: "Running network service",
          route_id: "route-a",
          flow_id: "flow-a",
          task_id: "",
          trace_id: "",
          target_node_id: "service-0",
          next_hop_id: "sat-0",
          network_queue_depth: 0,
          route_available: true,
          input_output_coupled: false,
          latency_components_observed: false,
          route_model: "FLOW_LEVEL_ROUTE_PROXY",
          service_model: "FLOW_LEVEL_COMMUNICATION_COMPUTE_PROXY",
          packet_level_simulation: false,
          status_digest:
            "DATA_TRANSFER/NETWORK_SERVICE_READY/RUNNING_NETWORK_SERVICE/sat-0"
        }
      ]
    };

    const rows = buildUserBusinessRequestRows(
      makeSnapshot({
        ground_users: [{ user_id: "user-0", status: "ACTIVE" }]
      }),
      undefined,
      backendSummary
    );

    expect(rows.sourceLabel).toBe("backend user_service_request_summary_v2");
    expect(rows.items[0]).toMatchObject({
      userId: "user-0",
      serviceLabel: "Data transfer / Network service route ready / flow-a"
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

  it("prefers explicit runtime entity detail cards", () => {
    expect(
      buildUserBusinessRequestInspector(userRow, undefined, {
        entity_type: "USER",
        entity_id: "user-0",
        title: "explicit user detail",
        subtitle: "EXACT_BY_ID",
        fields: [{ label: "source", value: "entity endpoint", tone: "normal" }]
      })
    ).toMatchObject({
      title: "explicit user detail",
      subtitle: "EXACT_BY_ID",
      fields: [{ label: "source", value: "entity endpoint", tone: "normal" }]
    });
    expect(
      buildSatelliteResourceInspector(satelliteRow, undefined, {
        entity_type: "SATELLITE",
        entity_id: "sat-0",
        title: "explicit satellite detail",
        subtitle: "EXACT_BY_ID",
        fields: [{ label: "source", value: "entity endpoint", tone: "resource" }]
      })
    ).toMatchObject({
      title: "explicit satellite detail",
      subtitle: "EXACT_BY_ID",
      fields: [{ label: "source", value: "entity endpoint", tone: "resource" }]
    });
  });

  it("appends exact detail request status only for the selected entity", () => {
    const inspector = {
      title: "route-a",
      subtitle: "exact route",
      fields: [{ label: "route", value: "route-a" }]
    };
    const loadingStatus = selectExactDetailRequestStatus(
      { entityId: "route-a", loading: true, error: null },
      "route-a"
    );

    expect(loadingStatus).toEqual({
      entityId: "route-a",
      loading: true,
      error: null
    });
    expect(
      appendExactDetailStatusToInspector(inspector, loadingStatus).fields[0]
    ).toEqual({
      label: "精确详情",
      value: "正在读取后端精确详情",
      tone: "resource"
    });
    expect(
      appendExactDetailStatusToInspector(inspector, {
        entityId: "route-a",
        loading: false,
        error: "后端精确详情读取失败"
      }).fields[0]
    ).toEqual({
      label: "精确详情",
      value: "后端精确详情读取失败",
      tone: "warning"
    });
    expect(
      appendExactDetailStatusToInspector(inspector, {
        entityId: "route-a",
        loading: false,
        error: null
      }).fields[0]
    ).toEqual({
      label: "精确详情",
      value: "后端精确详情已同步",
      tone: "resource"
    });
    expect(
      selectExactDetailRequestStatus(
        { entityId: "route-a", loading: true, error: null },
        "route-b"
      )
    ).toBeNull();
    expect(appendExactDetailStatusToInspector(inspector, null)).toBe(inspector);
  });

  it("builds exact route service and compute-node inspectors", () => {
    const routeRows = [
      {
        routeId: "route-a",
        flowId: "flow-a",
        available: true,
        availabilityLabel: "available",
        businessType: "DATA_TRANSFER",
        businessLabel: "data",
        nextHopLabel: "sat-a",
        capacityDemandLabel: "10 / 5 Mbps",
        pressureLabel: "50%",
        bottleneckComponent: "NONE",
        bottleneckLabel: "none",
        explanationLabel: "available",
        pathLabel: "user-a -> sat-a"
      },
      {
        routeId: "route-b",
        flowId: "flow-b",
        available: false,
        availabilityLabel: "blocked",
        businessType: "COMPUTE_SERVICE",
        businessLabel: "compute",
        nextHopLabel: "sat-b",
        capacityDemandLabel: "4 / 8 Mbps",
        pressureLabel: "200%",
        bottleneckComponent: "CAPACITY",
        bottleneckLabel: "capacity",
        explanationLabel: "capacity below demand",
        pathLabel: "user-b -> sat-b"
      }
    ];
    const serviceRows = [
      {
        serviceId: "task-a",
        taskLabel: "task-a",
        stateLabel: "running",
        placementLabel: "sat-a",
        networkLatencyLabel: "10 ms / 20 ms",
        computeLatencyLabel: "30 ms / 40 ms",
        totalLatencyLabel: "100 ms",
        traceTitle: "task-a trace"
      }
    ];
    const computeRows = [
      {
        nodeId: "sat-a",
        statusLabel: "BUSY",
        loadLabel: "50%",
        fp32Label: "50 / 100 GFLOPS",
        acceleratorLabel: "GPU 0 / 0 TFLOPS",
        memoryStorageLabel: "memory 1 / 2 GB",
        taskLabel: "1 running / 2 finished",
        traceTitle: "sat-a trace"
      }
    ];

    expect(selectRouteExplanationRow(routeRows, "route-b")?.routeId).toBe("route-b");
    expect(selectServiceDetailRow(serviceRows, "task-a")?.serviceId).toBe("task-a");
    expect(selectComputeNodeDetailRow(computeRows, "sat-a")?.nodeId).toBe("sat-a");
    expect(buildRouteExplanationDetailInspector(routeRows[0])).toMatchObject({
      title: "路由 route-a",
      subtitle: "data / available"
    });
    expect(
      buildRouteExplanationDetailInspector(routeRows[0], {
        route_id: "route-exact",
        flow_id: "flow-exact",
        user_id: "user-exact",
        source_id: "user-exact",
        destination_id: "sat-exact",
        selected_satellite_id: "sat-exact",
        primary_next_hop_id: "sat-exact",
        next_hop_ids: ["sat-exact"],
        hop_count: 1,
        path_label: "user-exact -> sat-exact",
        available: false,
        capacity_mbps: 4,
        demand_mbps: 8,
        latency_s: 0.12,
        loss_proxy_rate: 0.03,
        route_pressure_proxy: 2,
        business_type: "COMPUTE_SERVICE",
        business_label: "compute exact",
        bottleneck_component: "CAPACITY",
        bottleneck_reason: "ROUTE_CAPACITY_BELOW_DEMAND",
        bottleneck_reason_label: "capacity exact",
        explanation_label: "capacity below demand"
      })
    ).toMatchObject({
      title: "路由 route-exact",
      subtitle: "compute exact / 阻塞",
      fields: expect.arrayContaining([
        { label: "流", value: "flow-exact" },
        { label: "瓶颈", value: "capacity exact", tone: "warning" }
      ])
    });
    expect(
      buildServiceLifecycleDetailInspector(serviceRows[0], {
        service_id: "service-exact",
        task_id: "task-exact",
        input_flow_id: "flow-in",
        output_flow_id: "flow-out",
        input_route_id: "route-in",
        output_route_id: "route-out",
        compute_node_id: "sat-exact",
        complete: false,
        service_state: "RUNNING",
        service_state_label: "running exact",
        placement_status: "QUEUED",
        placement_policy: "MIN_ESTIMATED_FINISH_TIME",
        placement_bottleneck_resource: "gpu_tflops_fp32",
        placement_candidate_count: 3,
        placement_capable_candidate_count: 2,
        placement_candidate_queue_label: "sat-exact:queued",
        input_network_latency_s: 0.1,
        compute_queue_delay_s: 0.2,
        compute_execution_delay_s: 0.3,
        output_network_latency_s: 0.4,
        total_latency_s: 1,
        stage_count: 0,
        stages: []
      })
    ).toMatchObject({
      title: "服务 service-exact",
      subtitle: "running exact",
      fields: expect.arrayContaining([
        { label: "算力节点", value: "sat-exact" },
        { label: "计算", value: "200 ms / 300 ms", tone: "warning" }
      ])
    });
    expect(
      buildComputeNodeExactDetailInspector(computeRows[0], {
        node_id: "sat-exact",
        platform_type: "SATELLITE_COMPUTE_NODE",
        status: "BUSY",
        compute_load_ratio: 0.5,
        compute_capacity_gflops_fp32: 100,
        compute_used_gflops_fp32: 50,
        compute_available_gflops_fp32: 50,
        compute_capacity_gflops_fp64: 10,
        compute_used_gflops_fp64: 2,
        compute_capacity_gpu_tflops_fp32: 4,
        compute_used_gpu_tflops_fp32: 1,
        compute_capacity_gpu_tflops_fp16: 8,
        compute_used_gpu_tflops_fp16: 2,
        compute_capacity_npu_tops_int8: 16,
        compute_used_npu_tops_int8: 4,
        compute_capacity_memory_gb: 64,
        compute_used_memory_gb: 8,
        compute_capacity_storage_gb: 512,
        compute_used_storage_gb: 32,
        running_task_count: 1,
        finished_task_count: 2
      })
    ).toMatchObject({
      title: "算力节点 sat-exact",
      subtitle: "BUSY",
      fields: expect.arrayContaining([
        { label: "CPU FP32", value: "50 / 100 GFLOPS", tone: "resource" },
        { label: "任务", value: "1 运行 / 2 完成" }
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

describe("buildDataPanelFilterScopeNotes", () => {
  it("explains that filtering is scoped to active backend cursor pages", () => {
    expect(
      buildDataPanelFilterScopeNotes(
        {
          version: "v1",
          source: "BACKEND_RUNTIME_SNAPSHOT",
          summary_scope: "USER_REQUEST_DETAIL_WINDOW",
          cursor: 120,
          limit: 120,
          next_cursor: 240,
          has_more: true,
          user_count: 1200,
          item_count: 120,
          active_user_count: 80,
          compute_service_user_count: 20,
          waiting_user_count: 4,
          hidden_user_count: 1080,
          items: []
        },
        {
          version: "v1",
          source: "BACKEND_RUNTIME_SNAPSHOT",
          summary_scope: "SATELLITE_SERVICE_DETAIL_WINDOW",
          cursor: 0,
          limit: 96,
          next_cursor: 96,
          has_more: true,
          satellite_count: 1200,
          item_count: 96,
          hidden_satellite_count: 1104,
          items: []
        },
        {
          version: "v1",
          source: "BACKEND_RUNTIME_SNAPSHOT",
          summary_scope: "ROUTE_EXPLANATION_DETAIL_WINDOW",
          cursor: 64,
          limit: 64,
          next_cursor: 100,
          has_more: false,
          route_count: 100,
          item_count: 36,
          available_route_count: 30,
          blocked_route_count: 6,
          over_demand_route_count: 2,
          compute_service_route_count: 12,
          network_service_route_count: 88,
          items: []
        }
      )
    ).toEqual([
      {
        label: "筛选作用域",
        value: "当前后端页",
        detail:
          "用户 121-240 / 1,200，可继续翻页；卫星 1-96 / 1,200，可继续翻页；路由 65-100 / 100。刷新或翻页会把当前筛选条件发送到后端详情端点；表格仍只渲染当前后端页与本地窗口。",
        tone: "limit"
      }
    ]);
  });

  it("omits the scope note for legacy summaries without cursor metadata", () => {
    expect(
      buildDataPanelFilterScopeNotes({
        version: "v1",
        source: "BACKEND_RUNTIME_STATUS",
        user_count: 10,
        item_count: 10,
        active_user_count: 1,
        compute_service_user_count: 0,
        waiting_user_count: 0,
        hidden_user_count: 0,
        items: []
      })
    ).toEqual([]);
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
      serviceTraces: 120,
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
      serviceTraces: 120,
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

  it("summarizes complete backend detail coverage across all detail families", () => {
    expect(
      buildDataPanelDetailCoverageNote({
        userSummary: {
          source: "BACKEND_RUNTIME_STATUS",
          cursor: 0,
          limit: 2,
          next_cursor: 2,
          has_more: false,
          user_count: 2,
          item_count: 2,
          active_user_count: 1,
          compute_service_user_count: 1,
          waiting_user_count: 0,
          hidden_user_count: 0
        } as any,
        satelliteSummary: {
          source: "BACKEND_RUNTIME_STATUS",
          cursor: 0,
          limit: 2,
          next_cursor: 2,
          has_more: false,
          satellite_count: 2,
          item_count: 2,
          hidden_satellite_count: 0
        } as any,
        routeSummary: {
          version: "v1",
          source: "BACKEND_RUNTIME_STATUS",
          cursor: 0,
          limit: 2,
          next_cursor: 2,
          has_more: false,
          route_count: 2,
          item_count: 2,
          available_route_count: 2,
          blocked_route_count: 0,
          over_demand_route_count: 0,
          compute_service_route_count: 1,
          network_service_route_count: 1,
          items: []
        },
        servicePage: {
          source: "BACKEND_RUNTIME_STATUS",
          cursor: 0,
          limit: 1,
          next_cursor: 1,
          has_more: false,
          service_count: 1,
          item_count: 1,
          hidden_service_count: 0
        } as any,
        serviceTracePage: {
          source: "BACKEND_RUNTIME_STATUS",
          cursor: 0,
          limit: 1,
          next_cursor: 1,
          has_more: false,
          trace_count: 1,
          hidden_trace_count: 0,
          items: [{}]
        } as any,
        computeNodePage: {
          source: "BACKEND_RUNTIME_STATUS",
          cursor: 0,
          limit: 2,
          next_cursor: 2,
          has_more: false,
          compute_node_count: 2,
          item_count: 2,
          hidden_compute_node_count: 0
        } as any,
        nodeDetailSummary: {
          version: "v1",
          source: "BACKEND_RUNTIME_STATUS",
          user_detail_count: 1,
          satellite_detail_count: 1,
          users: [],
          satellites: []
        },
        paginationContract: makeLargeDetailPaginationContract()
      })
    ).toEqual({
      label: "详情覆盖度",
      value: "6 / 6 来源",
      detail:
        "后端详情覆盖完整；当前返回 10 / 10 行；无显式隐藏行；游标 6 类；可继续 0 类；精确卡片 2 个；large_1200 / zero_based_offset",
      tone: "backend"
    });
  });

  it("warns when backend detail coverage is partial or still cursor-limited", () => {
    expect(
      buildDataPanelDetailCoverageNote({
        userSummary: {
          source: "BACKEND_RUNTIME_STATUS",
          cursor: 0,
          limit: 10,
          next_cursor: 10,
          has_more: true,
          user_count: 20,
          request_count: 30,
          item_count: 10,
          active_user_count: 8,
          compute_service_user_count: 4,
          waiting_user_count: 2,
          hidden_user_count: 3,
          hidden_request_count: 5
        } as any
      })
    ).toEqual({
      label: "详情覆盖度",
      value: "1 / 6 来源",
      detail:
        "后端详情部分覆盖；当前返回 10 / 20 行；隐藏或未加载 5 行；游标 1 类；可继续 1 类；精确卡片 0 个；分页契约未声明",
      tone: "limit"
    });
  });

  it("shows a pending detail coverage card before backend detail summaries arrive", () => {
    expect(buildDataPanelDetailCoverageNote({})).toEqual({
      label: "详情覆盖度",
      value: "0 / 6 来源",
      detail:
        "等待后端详情；当前返回 0 / 0 行；无显式隐藏行；无后端游标页；精确卡片 0 个；分页契约未声明",
      tone: "history"
    });
  });

  it("summarizes selected detail evidence when exact backend details are synced", () => {
    expect(
      buildDataPanelSelectedDetailEvidenceNote({
        userId: "user-0",
        satelliteId: "sat-0",
        routeId: "route-0",
        serviceId: "service-0",
        traceId: "trace-0",
        computeNodeId: "sat-0",
        userRow: { userId: "user-0" } as any,
        satelliteRow: { satelliteId: "sat-0" } as any,
        routeRow: { routeId: "route-0" } as any,
        serviceRow: { serviceId: "service-0" } as any,
        traceRow: { traceId: "trace-0" } as any,
        computeNodeRow: { nodeId: "sat-0" } as any,
        backendDetails: {
          user: { entity_id: "user-0" } as any,
          satellite: { entity_id: "sat-0" } as any,
          route: { route_id: "route-0" } as any,
          service: { service_id: "service-0" } as any,
          serviceTrace: { trace: { trace_id: "trace-0" } } as any,
          computeNode: { node_id: "sat-0" } as any
        },
        requestStatuses: {
          user: { entityId: "user-0", loading: false, error: null },
          satellite: { entityId: "sat-0", loading: false, error: null },
          route: { entityId: "route-0", loading: false, error: null },
          service: { entityId: "service-0", loading: false, error: null },
          serviceTrace: { entityId: "trace-0", loading: false, error: null },
          computeNode: { entityId: "sat-0", loading: false, error: null }
        }
      })
    ).toEqual({
      label: "选中详情证据",
      value: "6 / 6 精确",
      detail:
        "已选 用户、卫星、路由、服务、服务链路、算力节点；表格行 6/6；后端精确 6/6",
      tone: "backend"
    });
  });

  it("warns when selected detail evidence is loading or missing exact backend details", () => {
    expect(
      buildDataPanelSelectedDetailEvidenceNote({
        userId: "user-0",
        routeId: "route-0",
        serviceId: "service-0",
        userRow: { userId: "user-0" } as any,
        routeRow: { routeId: "route-0" } as any,
        serviceRow: { serviceId: "service-0" } as any,
        backendDetails: {
          user: { entity_id: "user-0" } as any,
          route: null,
          service: null
        },
        requestStatuses: {
          user: { entityId: "user-0", loading: false, error: null },
          route: { entityId: "route-0", loading: true, error: null },
          service: { entityId: "service-0", loading: false, error: "HTTP 404" }
        }
      })
    ).toEqual({
      label: "选中详情证据",
      value: "1 / 3 精确",
      detail:
        "已选 用户、路由、服务；表格行 3/3；后端精确 1/3；读取中 1；错误 服务:HTTP 404",
      tone: "limit"
    });
  });

  it("shows selected detail evidence as pending before a detail row is selected", () => {
    expect(buildDataPanelSelectedDetailEvidenceNote({})).toEqual({
      label: "选中详情证据",
      value: "等待选择",
      detail:
        "未选择用户、卫星、路由、服务、服务链路或算力节点；点击明细表格行后会显示后端精确详情证据。",
      tone: "history"
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

function _runtimeExportRouteComparisonReview() {
  return {
    version: "v1",
    source: "BACKEND_RUNTIME_EXPORT",
    review_scope: "PACKAGE_ROUTE_DETAIL_TO_LIVE_RUNTIME_ROUTE_DETAIL",
    review_report_type: "RUNTIME_EXPORT_ROUTE_COMPARISON_REVIEW_REPORT_V1",
    review_report_id: "leo_twin.runtime_export_route_comparison_review_report.v1",
    package_route_detail_endpoint:
      "GET /runtime/export/packages/{package_id}/routes/{route_id}",
    live_route_detail_endpoint: "GET /runtime/details/routes/{route_id}",
    compare_action: "compare with live",
    comparison_requires_live_runtime: true,
    route_id_alignment_required: true,
    exported_rows_only: true,
    compared_fields: [
      "availability",
      "business",
      "flow",
      "source_destination",
      "selected_satellite",
      "primary_next_hop",
      "path",
      "capacity_demand",
      "latency",
      "loss",
      "pressure",
      "bottleneck"
    ],
    status_reasons: [
      "PACKAGE_DETAIL_NOT_LOADED",
      "PACKAGE_DETAIL_LOADING",
      "PACKAGE_DETAIL_UNAVAILABLE",
      "LIVE_DETAIL_NOT_LOADED",
      "LIVE_DETAIL_LOADING",
      "LIVE_DETAIL_UNAVAILABLE",
      "ROUTE_ID_MISMATCH"
    ],
    boundary_conditions: [
      "NO_ROUTE_RECOMPUTE",
      "NO_EVENT_REPLAY",
      "NO_PACKET_CAPTURE",
      "NO_PACKAGE_MUTATION",
      "CURRENT_RUNTIME_MAY_DIFFER_FROM_EXPORTED_PACKAGE"
    ],
    review_report_record_schema: {
      required_fields: [
        "route_id",
        "comparison_status",
        "compared_fields",
        "different_fields",
        "status_reason"
      ],
      optional_fields: [
        "package_route_detail_hash",
        "live_route_detail_hash",
        "matched_field_count",
        "different_field_count",
        "operator_note"
      ],
      status_values: ["MATCH", "DIFFERENT", "UNAVAILABLE", "ERROR"],
      ordering: "route_id ascending, then comparison_status ascending"
    }
  };
}

function _runtimeExportReproducibilityBoundary(
  overrides: Partial<{
    boundary_hash: string;
    event_replay_restore: boolean;
    recompute_on_read: boolean;
    package_mutation_on_read: boolean;
  }> = {}
) {
  return {
    type: "RUNTIME_EXPORT_REPRODUCIBILITY_BOUNDARY_V1",
    version: "v1",
    boundary_id: "leo_twin.runtime_export_reproducibility_boundary.v1",
    source: "BACKEND_RUNTIME_EXPORT",
    boundary_scope: "RESULT_PACKAGE_REPRODUCIBILITY_AND_RESTORE_BOUNDARY",
    manifest_id: "leo_twin.runtime_reproducibility_manifest.v1",
    control_config_hash: "sha256:control",
    generated_config_hash: "sha256:generated",
    runtime_state_hash: "sha256:runtime",
    metrics_summary_hash: "sha256:metrics",
    deterministic_replay_evidence: true,
    runtime_deterministic_replay_enabled: false,
    restore_scope: "CONFIG_ONLY",
    compare_scope: "CONFIG_AND_GENERATED_CONFIG",
    read_scope: "PERSISTED_ARTIFACTS_ONLY",
    event_kernel_policy: "NO_EVENT_KERNEL_BEHAVIOR_CHANGE",
    event_replay_restore: overrides.event_replay_restore ?? false,
    live_event_replay_restore: false,
    recompute_on_read: overrides.recompute_on_read ?? false,
    route_recomputation: false,
    service_recomputation: false,
    package_mutation_on_read: overrides.package_mutation_on_read ?? false,
    packet_capture: false,
    packet_level_simulation: false,
    external_simulators: false,
    forbidden_external_integrations: ["STK", "EXATA", "AFSIM", "DDS"],
    required_evidence_artifacts: [
      "config_snapshot.json",
      "events.jsonl",
      "metrics.csv",
      "summary.json",
      "manifest.json"
    ],
    optional_evidence_artifacts: [
      "service_lifecycle_trace_v2.json",
      "route_detail_index_v1.json",
      "review_summary_v1.json",
      "diagnostics_bundle_v1.json"
    ],
    route_detail_export: {
      policy: "EXPORT_ROUTE_DETAIL_INDEX_WINDOW",
      route_detail_limit: 5000,
      route_count: 20,
      indexed_route_count: 12,
      hidden_route_count: 8,
      artifact_window_only: true
    },
    service_trace_export: {
      policy: "EXPORT_SERVICE_TRACE_WINDOW",
      service_trace_limit: 5000,
      service_count: 7,
      exported_trace_count: 5,
      hidden_trace_count: 2,
      artifact_window_only: true
    },
    boundary_conditions: [
      "DETERMINISTIC_ARTIFACT_REPLAY_EVIDENCE",
      "CONFIG_ONLY_RESTORE",
      "NO_LIVE_EVENT_REPLAY_RESTORE",
      "NO_RECOMPUTE_ON_COMPARE_OR_READ",
      "NO_PACKAGE_MUTATION_ON_READ"
    ],
    boundary_hash:
      overrides.boundary_hash ??
      "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
  };
}

function _runtimeExportBoundaryAlignment(
  overrides: Partial<{
    alignment_status: string;
    boundary_hash: string;
    warnings: string[];
  }> = {}
) {
  return {
    type: "RUNTIME_EXPORT_BOUNDARY_ALIGNMENT_V1",
    version: "v1",
    alignment_id: "leo_twin.runtime_export_boundary_alignment.v1",
    source: "BACKEND_RUNTIME_EXPORT_COMPARE",
    alignment_scope: "PACKAGE_COMPARE_AND_RESTORE_BOUNDARY",
    package_id: "pkg-review",
    package_boundary_present: true,
    current_boundary_present: false,
    boundary_hash:
      overrides.boundary_hash ??
      "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
    current_boundary_hash: "",
    boundary_hash_matches_current: false,
    boundary_id_aligned: true,
    restore_scope: "CONFIG_ONLY",
    compare_scope: "CONFIG_AND_GENERATED_CONFIG",
    read_scope: "PERSISTED_ARTIFACTS_ONLY",
    preflight_scope: "",
    compare_scope_aligned: true,
    restore_scope_aligned: true,
    read_scope_aligned: true,
    preflight_scope_aligned: true,
    forbidden_behavior_inactive: true,
    event_replay_restore: false,
    live_event_replay_restore: false,
    recompute_on_read: false,
    route_recomputation: false,
    service_recomputation: false,
    package_mutation_on_read: false,
    packet_capture: false,
    packet_level_simulation: false,
    external_simulators: false,
    alignment_status: overrides.alignment_status ?? "ALIGNED",
    warnings: overrides.warnings ?? [],
    alignment_hash:
      "sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
  };
}

function _runtimeExportRouteIndexRoute(routeId: string, available: boolean) {
  return {
    route_id: routeId,
    flow_id: `flow-${routeId}`,
    user_id: "user-0",
    source_id: "user-0",
    destination_id: "sat-0",
    selected_satellite_id: "sat-0",
    primary_next_hop_id: "sat-0",
    next_hop_ids: ["sat-0"],
    hop_count: 1,
    path: ["user-0", "sat-0"],
    path_label: "user-0 -> sat-0",
    available,
    capacity_mbps: available ? 80 : 40,
    demand_mbps: 60,
    latency_s: available ? 0.1 : 0.2,
    loss_proxy_rate: available ? 0.01 : 0.05,
    route_pressure_proxy: available ? 0.75 : 1,
    business_type: available ? "COMPUTE_SERVICE" : "DATA_TRANSFER",
    business_label: available ? "compute service" : "data transfer",
    bottleneck_component: available ? "LOSS_PROXY" : "AVAILABILITY",
    bottleneck_reason: available ? "ROUTE_LOSS_PROXY_POSITIVE" : "ROUTE_UNAVAILABLE",
    bottleneck_reason_label: available
      ? "Route loss proxy is positive"
      : "Route unavailable",
    explanation_label: available
      ? "route has a positive flow-level loss proxy"
      : "route is unavailable"
  };
}

function _runtimeExportRouteDetailIndex(
  routes: readonly ReturnType<typeof _runtimeExportRouteIndexRoute>[]
) {
  return {
    type: "RUNTIME_EXPORT_ROUTE_DETAIL_INDEX_V1",
    version: "v1",
    index_id: "leo_twin.runtime_export_route_detail_index.v1",
    source: "BACKEND_RUNTIME_EXPORT",
    index_scope: "ROUTE_EXPLANATION_WINDOW_EXPORT",
    package_id: "pkg-review",
    package_dir: "artifacts/runtime_exports/pkg-review",
    route_model: "FLOW_LEVEL_ROUTE_PROXY",
    packet_level_simulation: false,
    all_pairs_computation: false,
    route_summary: {
      source: "BACKEND_RUNTIME_SNAPSHOT",
      summary_scope: "ROUTE_EXPLANATION_WINDOW",
      cursor: 0,
      limit: 500,
      next_cursor: routes.length,
      has_more: false,
      route_count: routes.length,
      indexed_route_count: routes.length,
      hidden_route_count: 0,
      available_route_count: routes.filter((route) => route.available).length,
      blocked_route_count: routes.filter((route) => !route.available).length,
      over_demand_route_count: 0,
      compute_service_route_count: routes.filter(
        (route) => route.business_type === "COMPUTE_SERVICE"
      ).length,
      network_service_route_count: routes.filter(
        (route) => route.business_type !== "COMPUTE_SERVICE"
      ).length
    },
    route_detail_export_policy: {
      version: "v1",
      source: "BACKEND_RUNTIME_EXPORT",
      policy: "EXPORT_ROUTE_DETAIL_INDEX_WINDOW",
      route_summary_source: "visible_snapshot.routes",
      route_detail_limit: 5000,
      route_count: routes.length,
      indexed_route_count: routes.length,
      hidden_route_count: 0,
      packet_level_simulation: false,
      all_pairs_computation: false
    },
    route_comparison_review: _runtimeExportRouteComparisonReview(),
    route_trust: {
      version: "v1",
      trust_id: "leo_twin.route_provenance_trust.v1",
      source: "config_snapshot.status.route_provenance_trust_summary_v1",
      evidence_present: true,
      route_model: "FLOW_LEVEL_ROUTE_PROXY",
      packet_level_simulation: false,
      all_pairs_computation: false,
      trust_status: "COMPLETE_FLOW_LEVEL_ROUTE_PROXY",
      route_count: routes.length,
      assessed_route_count: routes.length,
      hidden_route_count: 0,
      available_route_count: routes.filter((route) => route.available).length,
      blocked_route_count: routes.filter((route) => !route.available).length,
      over_demand_route_count: 0,
      explained_route_count: routes.length,
      missing_explanation_count: 0,
      path_context_route_count: routes.length,
      next_hop_route_count: routes.length,
      loss_proxy_route_count: routes.filter((route) => route.loss_proxy_rate > 0)
        .length,
      bottleneck_components: ["LOSS_PROXY", "CAPACITY"],
      sample_route_ids: routes.map((route) => route.route_id),
      caveats: []
    },
    route_ids: routes.map((route) => route.route_id),
    sample_route_ids: routes.map((route) => route.route_id),
    indexed_sample_route_ids: routes.map((route) => route.route_id),
    missing_sample_route_ids: [],
    source_order_policy: "route_explanation_summary_v1.items order is preserved",
    routes,
    route_detail_index_hash:
      "sha256:cdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcd"
  };
}

function _runtimeExportRouteDetailPage(
  routes: readonly ReturnType<typeof _runtimeExportRouteIndexRoute>[]
) {
  return {
    type: "RUNTIME_EXPORT_ROUTE_DETAIL_PAGE_V1",
    version: "v1",
    page_id: "leo_twin.runtime_export_route_detail_page.v1",
    source: "BACKEND_RUNTIME_EXPORT_PACKAGE",
    package_id: "pkg-review",
    index_id: "leo_twin.runtime_export_route_detail_index.v1",
    route_detail_export_policy: {
      version: "v1",
      source: "BACKEND_RUNTIME_EXPORT",
      policy: "EXPORT_ROUTE_DETAIL_INDEX_WINDOW",
      route_summary_source: "visible_snapshot.routes",
      route_detail_limit: 5000,
      route_count: 20,
      indexed_route_count: 20,
      hidden_route_count: 0,
      packet_level_simulation: false,
      all_pairs_computation: false
    },
    route_comparison_review: _runtimeExportRouteComparisonReview(),
    route_detail_index_hash:
      "sha256:cdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcd",
    index_scope: "ROUTE_EXPLANATION_WINDOW_EXPORT",
    cursor: 0,
    limit: 2,
    next_cursor: 2,
    has_more: true,
    route_count: 12,
    item_count: routes.length,
    unfiltered_route_count: 20,
    filter_applied: true,
    filters: {
      query: "sat-0",
      availability: "AVAILABLE",
      business_type: "COMPUTE_SERVICE",
      bottleneck_component: "ALL"
    },
    available_route_count: 8,
    blocked_route_count: 4,
    compute_service_route_count: 7,
    network_service_route_count: 5,
    items: routes,
    page_hash: "sha256:page"
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
