import { afterEach, describe, expect, it, vi } from "vitest";

import {
  loadRuntimeExportCatalog,
  loadRuntimeExportDiagnosticsBundle,
  loadRuntimeExportHistory,
  loadRuntimeExportManifest,
  loadRuntimeExportPackageJsonArtifact,
  loadRuntimeExportPackageAcceptanceReport,
  loadRuntimeExportPackageCompare,
  loadRuntimeExportPackageAuditIndex,
  loadRuntimeExportPackageHandoffReport,
  loadRuntimeExportPackageReviewCompletion,
  loadRuntimeExportScenarioReviewBundle,
  loadRuntimeExportScenarioReviewChecklist,
  loadRuntimeExportScenarioReviewChecklistTemplate,
  loadRuntimeExportScenarioReviewChecklistTemplateComparison,
  loadRuntimeExportRouteComparisonReviewReport,
  loadRuntimeExportServiceTraceComparisonReviewReport,
  loadRuntimeExportServiceTraceComparisonReviewReportPage,
  loadRuntimeExportRouteDetailIndex,
  loadRuntimeExportRouteDetailItem,
  loadRuntimeExportRouteDetailPage,
  loadRuntimeExportReviewSummary,
  loadRuntimeExportRestorePreflight,
  loadRuntimeExportServiceLifecycleTrace,
  loadRuntimeExportServiceTraceItem,
  loadRuntimeExportServiceTracePage,
  loadRuntimeExportTrafficDemandUserPage,
  loadRuntimeExportUserServiceRequestSummaryArtifact,
  loadRuntimeExportUserServiceRequestPage,
  loadRuntimeComputeNodeDetail,
  loadRuntimeComputeNodeDetails,
  loadRuntimeNodeDetails,
  loadRuntimeRouteDetail,
  loadRuntimeRouteDetails,
  loadRuntimeSatelliteDetail,
  loadRuntimeSatelliteDetails,
  loadRuntimeServiceDetail,
  loadRuntimeServiceDetails,
  loadRuntimeServiceTraceDetails,
  loadRuntimeServiceTraceDetail,
  loadRuntimeState,
  loadRuntimeUserDetail,
  loadRuntimeUserDetails,
  loadUserConfigurationExport,
  loadUserConfigurationReference,
  loadUserConfigurationSchema,
  loadUserConfigurationTemplateValidation,
  loadUserConfigurationTemplates,
  validateUserConfigurationCandidate,
  validateUserConfigurationTextCandidate,
  runtimeExportArchiveHref,
  runtimeExportPackageArchiveHref,
  runtimeExportPackageCompareHref,
  runtimeExportPackageFileHref,
  runtimeExportPackageManifestHref,
  runtimeExportPackageAcceptanceReportHref,
  runtimeExportPackageHandoffReportHref,
  runtimeExportPackageReviewCompletionHref,
  runtimeExportPackageRecordHref,
  runtimeExportPackageRouteDetailsHref,
  runtimeExportPackageRouteDetailHref,
  runtimeExportPackageServiceTraceHref,
  runtimeExportPackageServiceTracesHref,
  runtimeExportPackageTrafficDemandUsersHref,
  runtimeExportPackageUserServiceRequestsHref,
  runtimeExportPackageReviewSummaryHref,
  runtimeExportRouteComparisonReviewReportHref,
  runtimeExportServiceTraceComparisonReviewReportHref,
  runtimeExportServiceTraceComparisonReviewReportRecordsHref,
  runtimeExportScenarioReviewChecklistHref,
  runtimeExportScenarioReviewChecklistTemplateHref,
  runtimeExportScenarioReviewChecklistTemplateComparisonHref,
  runtimeExportRestorePreflightHref,
  runtimeDetailEntityHref,
  saveRuntimeExportRouteComparisonReviewReport,
  saveRuntimeExportServiceTraceComparisonReviewReport,
  saveRuntimeExportScenarioReviewChecklist,
  userConfigurationExportHref,
  userConfigurationReferenceHref,
  userConfigurationSchemaHref,
  userConfigurationTemplateValidationHref,
  userConfigurationTemplatesHref,
  userConfigurationValidateHref,
  userConfigurationValidateTextHref,
  runtimeApiErrorMessage
} from "../src/app/api";

describe("runtime API diagnostics", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("exposes the runtime export archive download endpoint", () => {
    expect(runtimeExportArchiveHref()).toBe("/runtime/export/archive");
    expect(runtimeExportArchiveHref("/custom/archive.zip")).toBe("/custom/archive.zip");
  });

  it("builds stable runtime export package artifact links", () => {
    expect(runtimeExportPackageRecordHref("pkg 1")).toBe(
      "/runtime/export/packages/pkg%201"
    );
    expect(runtimeExportPackageManifestHref("pkg 1")).toBe(
      "/runtime/export/packages/pkg%201/manifest"
    );
    expect(runtimeExportPackageReviewSummaryHref("pkg 1")).toBe(
      "/runtime/export/packages/pkg%201/review-summary"
    );
    expect(runtimeExportPackageReviewCompletionHref("pkg 1")).toBe(
      "/runtime/export/packages/pkg%201/review-completion"
    );
    expect(runtimeExportPackageAcceptanceReportHref("pkg 1")).toBe(
      "/runtime/export/packages/pkg%201/acceptance-report"
    );
    expect(runtimeExportPackageHandoffReportHref("pkg 1")).toBe(
      "/runtime/export/packages/pkg%201/handoff-report"
    );
    expect(runtimeExportPackageArchiveHref("pkg 1")).toBe(
      "/runtime/export/packages/pkg%201/archive"
    );
    expect(runtimeExportPackageCompareHref("pkg 1")).toBe(
      "/runtime/export/packages/pkg%201/compare"
    );
    expect(runtimeExportRestorePreflightHref("pkg 1")).toBe(
      "/runtime/export/packages/pkg%201/restore-preflight"
    );
    expect(runtimeExportPackageFileHref("pkg 1", "events 1.jsonl")).toBe(
      "/runtime/export/packages/pkg%201/files/events%201.jsonl"
    );
    expect(runtimeExportPackageRouteDetailHref("pkg 1", "route:input 1")).toBe(
      "/runtime/export/packages/pkg%201/routes/route%3Ainput%201"
    );
    expect(runtimeExportPackageServiceTraceHref("pkg 1", "trace:run 1")).toBe(
      "/runtime/export/packages/pkg%201/service-traces/trace%3Arun%201"
    );
    expect(runtimeExportRouteComparisonReviewReportHref("pkg 1")).toBe(
      "/runtime/export/packages/pkg%201/route-comparison-review-report"
    );
    expect(runtimeExportServiceTraceComparisonReviewReportHref("pkg 1")).toBe(
      "/runtime/export/packages/pkg%201/service-trace-comparison-review-report"
    );
    expect(
      runtimeExportServiceTraceComparisonReviewReportRecordsHref("pkg 1")
    ).toBe(
      "/runtime/export/packages/pkg%201/service-trace-comparison-review-report/records"
    );
    expect(runtimeExportScenarioReviewChecklistHref("pkg 1")).toBe(
      "/runtime/export/packages/pkg%201/scenario-review-checklist"
    );
    expect(runtimeExportScenarioReviewChecklistTemplateHref("pkg 1")).toBe(
      "/runtime/export/packages/pkg%201/scenario-review-checklist-template"
    );
    expect(
      runtimeExportScenarioReviewChecklistTemplateComparisonHref("pkg 1")
    ).toBe(
      "/runtime/export/packages/pkg%201/scenario-review-checklist-template-comparison"
    );
    expect(
      runtimeExportPackageRouteDetailsHref(
        "pkg 1",
        5,
        10,
        {
          query: "sat 1",
          availability: "AVAILABLE",
          businessType: "COMPUTE_SERVICE",
          bottleneckComponent: "CAPACITY"
        }
      )
    ).toBe(
      "/runtime/export/packages/pkg%201/routes?cursor=5&limit=10&query=sat+1&availability=AVAILABLE&business_type=COMPUTE_SERVICE&bottleneck_component=CAPACITY"
    );
    expect(
      runtimeExportPackageServiceTracesHref(
        "pkg 1",
        0,
        5,
        {
          query: "route run",
          terminalState: "RUNNING",
          computeNodeId: "sat-00003",
          stageKind: "OUTPUT_NETWORK",
          terminalReason: "OUTPUT_NETWORK_PENDING"
        }
      )
    ).toBe(
      "/runtime/export/packages/pkg%201/service-traces?cursor=0&limit=5&query=route+run&terminal_state=RUNNING&compute_node_id=sat-00003&stage_kind=OUTPUT_NETWORK&terminal_reason=OUTPUT_NETWORK_PENDING"
    );
    expect(
      runtimeExportPackageUserServiceRequestsHref(
        "pkg 1",
        0,
        5,
        {
          query: "sat 1",
          serviceClass: "COMPUTE_SERVICE",
          terminalState: "WAITING_NETWORK",
          networkWaiting: "WAITING"
        }
      )
    ).toBe(
      "/runtime/export/packages/pkg%201/user-service-requests?cursor=0&limit=5&query=sat+1&terminal_state=WAITING_NETWORK&service_class=COMPUTE_SERVICE&network_waiting=WAITING"
    );
    expect(
      runtimeExportPackageTrafficDemandUsersHref(
        "pkg 1",
        0,
        5,
        {
          query: "user 1",
          trafficClass: "COMPUTE_SERVICE"
        }
      )
    ).toBe(
      "/runtime/export/packages/pkg%201/traffic-demand-users?cursor=0&limit=5&query=user+1&traffic_class=COMPUTE_SERVICE"
    );
  });

  it("exposes stable user configuration contract links", () => {
    expect(userConfigurationSchemaHref()).toBe("/scenario/user-config/schema");
    expect(userConfigurationTemplatesHref()).toBe("/scenario/user-config/templates");
    expect(userConfigurationTemplateValidationHref()).toBe(
      "/scenario/user-config/template-validation"
    );
    expect(userConfigurationReferenceHref()).toBe("/scenario/user-config/reference");
    expect(userConfigurationExportHref()).toBe("/scenario/user-config/export");
    expect(userConfigurationValidateHref()).toBe("/scenario/user-config/validate");
  });

  it("loads runtime export package compare previews", async () => {
    const fetchMock = vi.fn(async () => ({
      ok: true,
      json: async () => ({
        type: "RUNTIME_EXPORT_PACKAGE_COMPARE",
        summary: {
          version: "v1",
          source: "BACKEND_RUNTIME_EXPORT_COMPARE",
          comparison_scope: "CONFIG_AND_GENERATED_CONFIG",
          package_id: "pkg",
          compatibility: "DIFFERENT",
          same_config: false,
          same_generated_config: false,
          same_manifest_hash: false,
          package_manifest_hash: "sha256:old",
          current_manifest_hash: "sha256:new",
          diff_count: 1,
          diff_limit: 32,
          diff_truncated: false,
          sections: [{ section: "generated_config", diff_count: 1, matches: false }],
          differences: [
            {
              section: "generated_config",
              path: "$.satellite_count",
              package_missing: false,
              current_missing: false,
              package_value: 72,
              current_value: 120
            }
          ],
          runtime_export_boundary_alignment_v1: {
            type: "RUNTIME_EXPORT_BOUNDARY_ALIGNMENT_V1",
            version: "v1",
            alignment_id: "leo_twin.runtime_export_boundary_alignment.v1",
            source: "BACKEND_RUNTIME_EXPORT_COMPARE",
            alignment_scope: "PACKAGE_COMPARE_AND_RESTORE_BOUNDARY",
            package_id: "pkg",
            package_boundary_present: true,
            current_boundary_present: false,
            boundary_hash: "sha256:boundary",
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
            alignment_status: "ALIGNED",
            warnings: [],
            alignment_hash: "sha256:alignment"
          },
          compare_hash: "sha256:compare"
        }
      })
    }));
    vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);

    await expect(loadRuntimeExportPackageCompare("pkg")).resolves.toMatchObject({
      compatibility: "DIFFERENT",
      diff_count: 1,
      runtime_export_boundary_alignment_v1: { alignment_status: "ALIGNED" },
      differences: [{ path: "$.satellite_count" }]
    });
    expect(fetchMock).toHaveBeenCalledWith("/runtime/export/packages/pkg/compare");
  });

  it("loads runtime export review summaries", async () => {
    const fetchMock = vi.fn(async () => ({
      ok: true,
      json: async () => ({
        type: "RUNTIME_EXPORT_REVIEW_SUMMARY_V1",
        version: "v1",
        summary_id: "leo_twin.runtime_export_review_summary.v1",
        source: "BACKEND_RUNTIME_EXPORT",
        summary_scope: "USER_READABLE_RESULT_PACKAGE_REVIEW",
        package_id: "pkg",
        package_dir: "artifacts/runtime_exports/pkg",
        review_status: "REVIEW_READY",
        scenario: {
          seed: 1,
          satellite_count: 72,
          user_count: 20,
          compute_node_count: 2,
          duration_seconds: 120
        },
        runtime: {
          lifecycle_state: "RUNNING",
          current_sim_time: 10,
          processed_event_count: 20,
          queued_event_count: 3
        },
        reproducibility: {
          manifest_id: "leo_twin.runtime_reproducibility_manifest.v1",
          manifest_hash: "sha256:manifest",
          config_hash: "sha256:config",
          generated_config_hash: "sha256:generated",
          event_kernel_policy: "NO_EVENT_KERNEL_BEHAVIOR_CHANGE"
        },
        artifacts: {
          artifact_count: 7,
          artifact_filenames: ["manifest.json"],
          required_filenames: ["manifest.json"],
          missing_required_filenames: [],
          service_lifecycle_trace_exported: true,
          review_summary_exported: true
        },
        review_notes: ["review"],
        summary_hash: "sha256:summary"
      })
    }));
    vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);

    await expect(loadRuntimeExportReviewSummary("pkg")).resolves.toMatchObject({
      package_id: "pkg",
      review_status: "REVIEW_READY",
      artifacts: { artifact_count: 7 }
    });
    expect(fetchMock).toHaveBeenCalledWith(
      "/runtime/export/packages/pkg/review-summary"
    );
  });

  it("loads runtime export manifests", async () => {
    const fetchMock = vi.fn(async () => ({
      ok: true,
      json: async () => ({
        version: "v1",
        source: "BACKEND_RUNTIME_STATUS",
        manifest_id: "leo_twin.runtime_reproducibility_manifest.v1",
        session_id: "integration-demo-1",
        scenario_hash: "sha256:scenario",
        control_config_hash: "sha256:config",
        generated_config_hash: "sha256:generated",
        metrics_summary_hash: "sha256:metrics",
        runtime_state_hash: "sha256:runtime",
        manifest_hash: "sha256:manifest",
        artifact_policy: "LIVE_STATUS_MANIFEST_ONLY",
        artifacts: [
          {
            name: "events.jsonl",
            format: "jsonl",
            status: "AVAILABLE_FOR_BATCH_EXPORT",
            source: "MetricsCollector.write_outputs"
          }
        ],
        artifact_count: 1
      })
    }));
    vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);

    await expect(loadRuntimeExportManifest("pkg")).resolves.toMatchObject({
      manifest_id: "leo_twin.runtime_reproducibility_manifest.v1",
      manifest_hash: "sha256:manifest",
      artifacts: [{ name: "events.jsonl" }]
    });
    expect(fetchMock).toHaveBeenCalledWith("/runtime/export/packages/pkg/manifest");
  });

  it("loads arbitrary runtime export JSON artifacts", async () => {
    const fetchMock = vi.fn(async () => ({
      ok: true,
      json: async () => ({
        validation: {
          status: "PASS",
          observed_value: 42
        }
      })
    }));
    vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);

    await expect(
      loadRuntimeExportPackageJsonArtifact(
        "pkg",
        "network_kpi_benchmark_validation_v1.json"
      )
    ).resolves.toEqual({
      validation: {
        status: "PASS",
        observed_value: 42
      }
    });
    expect(fetchMock).toHaveBeenCalledWith(
      "/runtime/export/packages/pkg/files/network_kpi_benchmark_validation_v1.json"
    );
  });

  it("loads runtime export diagnostics bundles", async () => {
    const fetchMock = vi.fn(async () => ({
      ok: true,
      json: async () => ({
        type: "RUNTIME_EXPORT_DIAGNOSTICS_BUNDLE_V1",
        version: "v1",
        bundle_id: "leo_twin.runtime_export_diagnostics_bundle.v1",
        source: "BACKEND_RUNTIME_EXPORT",
        diagnostics_scope: "RESULT_PACKAGE_OPERATOR_REVIEW",
        package: {
          package_id: "pkg",
          package_dir: "artifacts/runtime_exports/pkg",
          package_complete: true,
          review_status: "REVIEW_READY",
          contract_id: "leo_twin.result_package_contract.v1"
        },
        runtime: {
          lifecycle_state: "STOPPED",
          current_sim_time: 120,
          processed_event_count: 200,
          queued_event_count: 0
        },
        reproducibility: {
          manifest_id: "leo_twin.runtime_reproducibility_manifest.v1",
          manifest_ok: true,
          manifest_hash: "sha256:manifest",
          config_hash: "sha256:config",
          generated_config_hash: "sha256:generated",
          review_summary_hash: "sha256:summary"
        },
        artifact_health: {
          artifact_count: 8,
          artifact_filenames: ["diagnostics_bundle_v1.json"],
          required_filenames: ["manifest.json"],
          recommended_filenames: ["diagnostics_bundle_v1.json"],
          present_required_filenames: ["manifest.json"],
          missing_required_filenames: [],
          present_recommended_filenames: ["diagnostics_bundle_v1.json"],
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
            message: "ready"
          }
        ],
        finding_count: 1,
        recommended_next_actions: ["attach package"],
        diagnostics_hash: "sha256:diagnostics"
      })
    }));
    vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);

    await expect(loadRuntimeExportDiagnosticsBundle("pkg")).resolves.toMatchObject({
      package: { package_id: "pkg", package_complete: true },
      artifact_health: { artifact_count: 8 },
      findings: [{ code: "RESULT_PACKAGE_REVIEW_READY" }]
    });
    expect(fetchMock).toHaveBeenCalledWith(
      "/runtime/export/packages/pkg/files/diagnostics_bundle_v1.json"
    );
  });

  it("loads runtime export service lifecycle trace artifacts", async () => {
    const fetchMock = vi.fn(async () => ({
      ok: true,
      json: async () => ({
        version: "v2",
        source: "RUNTIME_EXPORT_PACKAGE",
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
        items: []
      })
    }));
    vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);

    await expect(loadRuntimeExportServiceLifecycleTrace("pkg")).resolves.toMatchObject({
      source: "RUNTIME_EXPORT_PACKAGE",
      trace_count: 1,
      complete_trace_count: 1
    });
    expect(fetchMock).toHaveBeenCalledWith(
      "/runtime/export/packages/pkg/files/service_lifecycle_trace_v2.json"
    );
  });

  it("loads runtime export service trace pages", async () => {
    const fetchMock = vi.fn(async () => ({
      ok: true,
      json: async () => ({
        type: "RUNTIME_EXPORT_SERVICE_TRACE_PAGE_V1",
        version: "v1",
        page_id: "leo_twin.runtime_export_service_trace_page.v1",
        source: "BACKEND_RUNTIME_EXPORT_PACKAGE",
        package_id: "pkg",
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
        export_next_cursor: 2,
        export_has_more: false,
        cursor: 0,
        limit: 1,
        next_cursor: 1,
        has_more: false,
        service_count: 1,
        trace_count: 1,
        item_count: 1,
        unfiltered_trace_count: 2,
        complete_trace_count: 0,
        running_trace_count: 1,
        incomplete_trace_count: 0,
        hidden_trace_count: 0,
        filter_applied: true,
        filters: {
          query: "route-run",
          terminal_state: "RUNNING",
          compute_node_id: "sat-00003",
          stage_kind: "OUTPUT_NETWORK",
          terminal_reason: "OUTPUT_NETWORK_PENDING"
        },
        boundary_conditions: [
          "ARTIFACT_WINDOW_ONLY",
          "NO_EVENT_REPLAY",
          "NO_SERVICE_RECOMPUTE",
          "NO_PACKAGE_MUTATION"
        ],
        items: [{ trace_id: "trace:run" }],
        page_hash: "sha256:trace-page"
      })
    }));
    vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);

    await expect(
      loadRuntimeExportServiceTracePage("pkg", 0, 1, {
        query: "route-run",
        terminalState: "RUNNING",
        computeNodeId: "sat-00003",
        stageKind: "OUTPUT_NETWORK",
        terminalReason: "OUTPUT_NETWORK_PENDING"
      })
    ).resolves.toMatchObject({
      package_id: "pkg",
      artifact_window_only: true,
      trace_count: 1,
      items: [{ trace_id: "trace:run" }]
    });
    expect(fetchMock).toHaveBeenCalledWith(
      "/runtime/export/packages/pkg/service-traces?cursor=0&limit=1&query=route-run&terminal_state=RUNNING&compute_node_id=sat-00003&stage_kind=OUTPUT_NETWORK&terminal_reason=OUTPUT_NETWORK_PENDING"
    );
  });

  it("loads exact runtime export service trace items", async () => {
    const fetchMock = vi.fn(async () => ({
      ok: true,
      json: async () => ({
        type: "RUNTIME_EXPORT_SERVICE_TRACE_ITEM_V1",
        version: "v1",
        item_id: "leo_twin.runtime_export_service_trace_item.v1",
        source: "BACKEND_RUNTIME_EXPORT_PACKAGE",
        package_id: "pkg",
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
        item_hash: "sha256:trace-item"
      })
    }));
    vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);

    await expect(
      loadRuntimeExportServiceTraceItem("pkg", "trace:run")
    ).resolves.toMatchObject({
      package_id: "pkg",
      trace_id: "trace:run",
      artifact_window_only: true,
      trace: { trace_id: "trace:run", compute_node_id: "sat-00003" }
    });
    expect(fetchMock).toHaveBeenCalledWith(
      "/runtime/export/packages/pkg/service-traces/trace%3Arun"
    );
  });

  it("loads runtime export user service request pages", async () => {
    const fetchMock = vi.fn(async () => ({
      ok: true,
      json: async () => ({
        type: "RUNTIME_EXPORT_USER_SERVICE_REQUEST_PAGE_V1",
        version: "v1",
        page_id: "leo_twin.runtime_export_user_service_request_page.v1",
        source: "BACKEND_RUNTIME_EXPORT",
        package_id: "pkg",
        artifact_type: "RUNTIME_EXPORT_USER_SERVICE_REQUEST_SUMMARY_V2",
        artifact_source: "user_service_request_summary_v2.json",
        artifact_policy: "STANDALONE_RUNTIME_EXPORT_ARTIFACT",
        artifact_window_only: true,
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
        export_next_cursor: 1,
        export_has_more: false,
        cursor: 0,
        limit: 1,
        next_cursor: 1,
        has_more: false,
        request_count: 1,
        item_count: 1,
        unfiltered_request_count: 1,
        active_request_count: 1,
        compute_request_count: 1,
        communication_request_count: 1,
        network_waiting_request_count: 0,
        hidden_request_count: 0,
        filter_applied: true,
        filters: {
          query: "sat-run",
          service_class: "COMPUTE_SERVICE",
          terminal_state: "RUNNING",
          network_waiting: "READY"
        },
        boundary_conditions: ["NO_SERVICE_RECOMPUTE"],
        items: [{ user_id: "user-00001", service_class: "COMPUTE_SERVICE" }],
        page_hash:
          "sha256:efefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefef"
      })
    }));
    vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);

    await expect(
      loadRuntimeExportUserServiceRequestPage("pkg", 0, 1, {
        query: "sat-run",
        serviceClass: "COMPUTE_SERVICE",
        terminalState: "RUNNING",
        networkWaiting: "READY"
      })
    ).resolves.toMatchObject({
      package_id: "pkg",
      artifact_window_only: true,
      request_count: 1,
      filters: {
        service_class: "COMPUTE_SERVICE",
        network_waiting: "READY"
      },
      items: [{ user_id: "user-00001" }]
    });
    expect(fetchMock).toHaveBeenCalledWith(
      "/runtime/export/packages/pkg/user-service-requests?cursor=0&limit=1&query=sat-run&terminal_state=RUNNING&service_class=COMPUTE_SERVICE&network_waiting=READY"
    );
  });

  it("loads runtime export traffic demand user pages", async () => {
    const fetchMock = vi.fn(async () => ({
      ok: true,
      json: async () => ({
        type: "RUNTIME_EXPORT_TRAFFIC_DEMAND_USER_PAGE_V1",
        version: "v1",
        page_id: "leo_twin.runtime_export_traffic_demand_user_page.v1",
        source: "BACKEND_RUNTIME_EXPORT_PACKAGE",
        package_id: "pkg",
        artifact_type: "RUNTIME_EXPORT_TRAFFIC_DEMAND_EXPLANATION_V1",
        artifact_source: "BACKEND_RUNTIME_EXPORT",
        artifact_scope: "TRAFFIC_DEMAND_OFFLINE_REVIEW",
        artifact_hash:
          "sha256:1212121212121212121212121212121212121212121212121212121212121212",
        evidence_hash:
          "sha256:3434343434343434343434343434343434343434343434343434343434343434",
        explanation_id: "leo_twin.traffic_demand_explanation.v1",
        explanation_window_policy: "FULL_CONFIGURED_WINDOW",
        endpoint_window_policy: "ROUND_ROBIN_ENDPOINT_IDS_CAPPED_AT_512",
        packet_level_simulation: false,
        frontend_inference_required: false,
        cursor: 0,
        limit: 1,
        next_cursor: 1,
        has_more: false,
        user_count: 1,
        item_count: 1,
        unfiltered_user_count: 2,
        request_count: 1,
        compute_service_user_count: 1,
        communication_service_user_count: 0,
        filter_applied: true,
        filters: {
          query: "user-00001",
          traffic_class: "COMPUTE_SERVICE"
        },
        boundary_conditions: [
          "ARTIFACT_WINDOW_ONLY",
          "NO_TRAFFIC_REGENERATION",
          "NO_EVENT_REPLAY",
          "NO_PACKAGE_MUTATION"
        ],
        items: [
          {
            user_id: "user-00001",
            request_count: 1,
            service_classes: ["COMPUTE_SERVICE"],
            primary_service_class: "COMPUTE_SERVICE",
            max_priority: 3,
            first_arrival_time: 10,
            last_arrival_time: 10,
            flow_ids: ["flow-input"],
            task_ids: ["task-1"],
            output_flow_ids: ["flow-output"],
            total_input_data_mb: 64,
            total_output_data_mb: 16
          }
        ],
        page_hash:
          "sha256:5656565656565656565656565656565656565656565656565656565656565656"
      })
    }));
    vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);

    await expect(
      loadRuntimeExportTrafficDemandUserPage("pkg", 0, 1, {
        query: "user-00001",
        trafficClass: "COMPUTE_SERVICE"
      })
    ).resolves.toMatchObject({
      package_id: "pkg",
      user_count: 1,
      filters: {
        query: "user-00001",
        traffic_class: "COMPUTE_SERVICE"
      },
      items: [{ user_id: "user-00001" }]
    });
    expect(fetchMock).toHaveBeenCalledWith(
      "/runtime/export/packages/pkg/traffic-demand-users?cursor=0&limit=1&query=user-00001&traffic_class=COMPUTE_SERVICE"
    );
  });

  it("loads runtime export user service request summary artifacts", async () => {
    const fetchMock = vi.fn(async () => ({
      ok: true,
      json: async () => ({
        type: "RUNTIME_EXPORT_USER_SERVICE_REQUEST_SUMMARY_V2",
        version: "v2",
        artifact_id: "leo_twin.runtime_export_user_service_request_summary.v2",
        source: "BACKEND_RUNTIME_EXPORT",
        artifact_scope: "USER_SERVICE_REQUEST_OFFLINE_REVIEW",
        package_id: "pkg",
        package_dir: "artifacts/runtime_exports/pkg",
        runtime_status_field: "user_service_request_summary_v2",
        artifact_policy: "STANDALONE_RUNTIME_EXPORT_ARTIFACT",
        artifact_window_only: true,
        summary: {
          version: "v2",
          source: "BACKEND_RUNTIME_STATUS",
          summary_scope: "USER_SERVICE_REQUEST_WINDOW",
          cursor: 0,
          limit: 100,
          next_cursor: 1,
          has_more: false,
          request_model: "FLOW_LEVEL_USER_SERVICE_REQUEST_PROXY",
          route_model: "FLOW_LEVEL_ROUTE_PROXY",
          compute_model: "TASK_RESOURCE_DEMAND_PROXY",
          packet_level_simulation: false,
          frontend_inference_required: false,
          user_count: 1,
          active_user_count: 1,
          compute_service_user_count: 1,
          communication_user_count: 1,
          item_count: 1,
          hidden_user_count: 0,
          request_count: 1,
          active_request_count: 1,
          communication_request_count: 1,
          compute_request_count: 1,
          network_waiting_request_count: 0,
          completed_request_count: 0,
          hidden_request_count: 0,
          items: [
            {
              user_id: "user-00001",
              platform_type: "GROUND_USER",
              platform_type_label: "ground user",
              status: "ACTIVE",
              communication_route_count: 1,
              available_route_count: 1,
              compute_service_count: 1,
              network_queue_count: 0,
              selected_satellite_id: "sat-00001",
              destination_id: "sat-00001",
              path: ["user-00001", "sat-00001"],
              request_id: "svc-00001",
              service_request_id: "svc-00001",
              service_class: "COMPUTE_SERVICE",
              service_class_label: "compute service"
            }
          ]
        },
        user_service_request_export_policy: {
          policy: "EXPORT_USER_SERVICE_REQUEST_WINDOW"
        },
        evidence: {
          version: "v2",
          evidence_id: "leo_twin.runtime_export_user_service_request_summary.v2",
          source: "config_snapshot.status.user_service_request_summary_v2",
          evidence_present: true,
          request_model: "FLOW_LEVEL_USER_SERVICE_REQUEST_PROXY",
          request_count: 1,
          exported_request_count: 1,
          hidden_request_count: 0,
          active_request_count: 1,
          compute_request_count: 1,
          network_waiting_request_count: 0,
          packet_level_simulation: false,
          frontend_inference_required: false,
          artifact_window_only: true,
          summary_hash:
            "sha256:abababababababababababababababababababababababababababababababab"
        },
        boundary_conditions: ["NO_SERVICE_RECOMPUTE"],
        artifact_hash:
          "sha256:cdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcd"
      })
    }));
    vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);

    await expect(
      loadRuntimeExportUserServiceRequestSummaryArtifact("pkg")
    ).resolves.toMatchObject({
      package_id: "pkg",
      artifact_window_only: true,
      summary: {
        request_model: "FLOW_LEVEL_USER_SERVICE_REQUEST_PROXY",
        request_count: 1,
        items: [{ user_id: "user-00001" }]
      }
    });
    expect(fetchMock).toHaveBeenCalledWith(
      "/runtime/export/packages/pkg/files/user_service_request_summary_v2.json"
    );
  });

  it("loads runtime export route detail indexes", async () => {
    const fetchMock = vi.fn(async () => ({
      ok: true,
      json: async () => ({
        type: "RUNTIME_EXPORT_ROUTE_DETAIL_INDEX_V1",
        version: "v1",
        index_id: "leo_twin.runtime_export_route_detail_index.v1",
        source: "BACKEND_RUNTIME_EXPORT",
        index_scope: "ROUTE_EXPLANATION_WINDOW_EXPORT",
        package_id: "pkg",
        package_dir: "artifacts/runtime_exports/pkg",
        route_model: "FLOW_LEVEL_ROUTE_PROXY",
        packet_level_simulation: false,
        all_pairs_computation: false,
        route_summary: {
          source: "BACKEND_RUNTIME_SNAPSHOT",
          summary_scope: "ROUTE_EXPLANATION_WINDOW",
          cursor: 0,
          limit: 500,
          next_cursor: 1,
          has_more: false,
          route_count: 1,
          indexed_route_count: 1,
          hidden_route_count: 0,
          available_route_count: 1,
          blocked_route_count: 0,
          over_demand_route_count: 0,
          compute_service_route_count: 1,
          network_service_route_count: 0
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
          route_count: 1,
          assessed_route_count: 1,
          hidden_route_count: 0,
          available_route_count: 1,
          blocked_route_count: 0,
          over_demand_route_count: 0,
          explained_route_count: 1,
          missing_explanation_count: 0,
          path_context_route_count: 1,
          next_hop_route_count: 1,
          loss_proxy_route_count: 0,
          bottleneck_components: [],
          sample_route_ids: ["route-0"],
          caveats: []
        },
        route_ids: ["route-0"],
        sample_route_ids: ["route-0"],
        indexed_sample_route_ids: ["route-0"],
        missing_sample_route_ids: [],
        source_order_policy: "route_explanation_summary_v1.items order is preserved",
        routes: [{ route_id: "route-0" }],
        route_detail_index_hash: "sha256:route"
      })
    }));
    vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);

    await expect(loadRuntimeExportRouteDetailIndex("pkg")).resolves.toMatchObject({
      package_id: "pkg",
      route_summary: { route_count: 1 },
      routes: [{ route_id: "route-0" }]
    });
    expect(fetchMock).toHaveBeenCalledWith(
      "/runtime/export/packages/pkg/files/route_detail_index_v1.json"
    );
  });

  it("loads runtime export route detail pages", async () => {
    const fetchMock = vi.fn(async () => ({
      ok: true,
      json: async () => ({
        type: "RUNTIME_EXPORT_ROUTE_DETAIL_PAGE_V1",
        version: "v1",
        page_id: "leo_twin.runtime_export_route_detail_page.v1",
        source: "BACKEND_RUNTIME_EXPORT_PACKAGE",
        package_id: "pkg",
        index_id: "leo_twin.runtime_export_route_detail_index.v1",
        route_detail_index_hash: "sha256:route",
        index_scope: "ROUTE_EXPLANATION_WINDOW_EXPORT",
        cursor: 0,
        limit: 1,
        next_cursor: 1,
        has_more: false,
        route_count: 1,
        item_count: 1,
        unfiltered_route_count: 1,
        filter_applied: true,
        filters: {
          query: "sat-0",
          availability: "AVAILABLE",
          business_type: "COMPUTE_SERVICE",
          bottleneck_component: "ALL"
        },
        available_route_count: 1,
        blocked_route_count: 0,
        compute_service_route_count: 1,
        network_service_route_count: 0,
        items: [{ route_id: "route-0" }],
        page_hash: "sha256:page"
      })
    }));
    vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);

    await expect(
      loadRuntimeExportRouteDetailPage("pkg", 0, 1, {
        query: "sat-0",
        availability: "AVAILABLE",
        businessType: "COMPUTE_SERVICE"
      })
    ).resolves.toMatchObject({
      package_id: "pkg",
      route_count: 1,
      items: [{ route_id: "route-0" }]
    });
    expect(fetchMock).toHaveBeenCalledWith(
      "/runtime/export/packages/pkg/routes?cursor=0&limit=1&query=sat-0&availability=AVAILABLE&business_type=COMPUTE_SERVICE"
    );
  });

  it("loads runtime export route detail items", async () => {
    const fetchMock = vi.fn(async () => ({
      ok: true,
      json: async () => ({
        type: "RUNTIME_EXPORT_ROUTE_DETAIL_ITEM_V1",
        version: "v1",
        item_id: "leo_twin.runtime_export_route_detail_item.v1",
        source: "BACKEND_RUNTIME_EXPORT_PACKAGE",
        package_id: "pkg",
        index_id: "leo_twin.runtime_export_route_detail_index.v1",
        route_detail_index_hash: "sha256:route",
        route_id: "route:0",
        route: { route_id: "route:0" },
        item_hash: "sha256:item"
      })
    }));
    vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);

    await expect(
      loadRuntimeExportRouteDetailItem("pkg", "route:0")
    ).resolves.toMatchObject({
      package_id: "pkg",
      route_id: "route:0",
      route: { route_id: "route:0" }
    });
    expect(fetchMock).toHaveBeenCalledWith(
      "/runtime/export/packages/pkg/routes/route%3A0"
    );
  });

  it("saves runtime export route comparison review reports", async () => {
    const fetchMock = vi.fn(async () => ({
      ok: true,
      json: async () => ({
        type: "RUNTIME_EXPORT_ROUTE_COMPARISON_REVIEW_REPORT",
        summary: {
          type: "RUNTIME_EXPORT_ROUTE_COMPARISON_REVIEW_REPORT_V1",
          version: "v1",
          report_id: "leo_twin.runtime_export_route_comparison_review_report.v1",
          source: "OPERATOR_ROUTE_COMPARISON_REVIEW",
          report_scope: "SELECTED_PACKAGE_VS_LIVE_ROUTE_COMPARISON_OUTCOMES",
          package_id: "pkg",
          package_dir: "artifacts/runtime_exports/pkg",
          route_comparison_review: {
            version: "v1",
            source: "BACKEND_RUNTIME_EXPORT",
            review_scope: "PACKAGE_ROUTE_DETAIL_TO_LIVE_RUNTIME_ROUTE_DETAIL",
            package_route_detail_endpoint:
              "GET /runtime/export/packages/{package_id}/routes/{route_id}",
            live_route_detail_endpoint: "GET /runtime/details/routes/{route_id}",
            compare_action: "compare with live",
            comparison_requires_live_runtime: true,
            route_id_alignment_required: true,
            exported_rows_only: true,
            compared_fields: ["latency", "bottleneck"],
            status_reasons: ["ROUTE_ID_MISMATCH"],
            boundary_conditions: ["NO_ROUTE_RECOMPUTE"]
          },
          runtime_export_boundary_alignment_v1: {
            type: "RUNTIME_EXPORT_BOUNDARY_ALIGNMENT_V1",
            version: "v1",
            alignment_id: "leo_twin.runtime_export_boundary_alignment.v1",
            source: "BACKEND_RUNTIME_EXPORT_RESTORE_PREFLIGHT",
            alignment_scope: "PACKAGE_COMPARE_AND_RESTORE_BOUNDARY",
            package_id: "pkg",
            package_boundary_present: true,
            current_boundary_present: false,
            boundary_hash: "sha256:boundary",
            current_boundary_hash: "",
            boundary_hash_matches_current: false,
            boundary_id_aligned: true,
            restore_scope: "CONFIG_ONLY",
            compare_scope: "CONFIG_AND_GENERATED_CONFIG",
            read_scope: "PERSISTED_ARTIFACTS_ONLY",
            preflight_scope: "CONFIG_RESTORE_PREVIEW_ONLY",
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
            alignment_status: "ALIGNED",
            warnings: [],
            alignment_hash: "sha256:alignment"
          },
          boundary_alignment_hash: "sha256:alignment",
          boundary_alignment_status: "ALIGNED",
          boundary_alignment_warnings: [],
          runtime_export_boundary_hash: "sha256:boundary",
          record_count: 1,
          match_count: 0,
          different_count: 1,
          unavailable_count: 0,
          error_count: 0,
          records: [
            {
              route_id: "route:0",
              comparison_status: "DIFFERENT",
              package_route_detail_hash: "sha256:package",
              live_route_detail_hash: "sha256:live",
              matched_field_count: 1,
              different_field_count: 1,
              compared_fields: ["latency", "bottleneck"],
              different_fields: ["latency"],
              status_reason: "FIELDS_DIFFER",
              operator_note: "operator reviewed"
            }
          ],
          ordering: "route_id ascending, then comparison_status ascending",
          boundary_conditions: ["NO_ROUTE_RECOMPUTE"],
          report_hash: "sha256:report"
        },
        artifact: {
          name: "route_comparison_review_report_v1",
          filename: "route_comparison_review_report_v1.json",
          bytes: 256,
          sha256: "sha256:artifact"
        }
      })
    }));
    vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);

    await expect(
      saveRuntimeExportRouteComparisonReviewReport("pkg", {
        records: [
          {
            route_id: "route:0",
            comparison_status: "DIFFERENT",
            different_fields: ["latency"],
            status_reason: "FIELDS_DIFFER"
          }
        ]
      })
    ).resolves.toMatchObject({
      package_id: "pkg",
      record_count: 1,
      different_count: 1,
      boundary_alignment_status: "ALIGNED",
      records: [{ route_id: "route:0", status_reason: "FIELDS_DIFFER" }]
    });
    expect(fetchMock).toHaveBeenCalledWith(
      "/runtime/export/packages/pkg/route-comparison-review-report",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          records: [
            {
              route_id: "route:0",
              comparison_status: "DIFFERENT",
              different_fields: ["latency"],
              status_reason: "FIELDS_DIFFER"
            }
          ]
        })
      }
    );
  });

  it("loads saved runtime export route comparison review report artifacts", async () => {
    const fetchMock = vi.fn(async () => ({
      ok: true,
      json: async () => ({
        type: "RUNTIME_EXPORT_ROUTE_COMPARISON_REVIEW_REPORT_V1",
        version: "v1",
        report_id: "leo_twin.runtime_export_route_comparison_review_report.v1",
        source: "OPERATOR_ROUTE_COMPARISON_REVIEW",
        report_scope: "SELECTED_PACKAGE_VS_LIVE_ROUTE_COMPARISON_OUTCOMES",
        package_id: "pkg",
        package_dir: "artifacts/runtime_exports/pkg",
        route_comparison_review: {
          version: "v1",
          source: "BACKEND_RUNTIME_EXPORT",
          review_scope: "PACKAGE_ROUTE_DETAIL_TO_LIVE_RUNTIME_ROUTE_DETAIL",
          package_route_detail_endpoint:
            "GET /runtime/export/packages/{package_id}/routes/{route_id}",
          live_route_detail_endpoint: "GET /runtime/details/routes/{route_id}",
          compare_action: "compare with live",
          comparison_requires_live_runtime: true,
          route_id_alignment_required: true,
          exported_rows_only: true,
          compared_fields: ["latency", "bottleneck"],
          status_reasons: ["FIELDS_DIFFER"],
          boundary_conditions: ["NO_ROUTE_RECOMPUTE"]
        },
        runtime_export_boundary_alignment_v1: {
          type: "RUNTIME_EXPORT_BOUNDARY_ALIGNMENT_V1",
          version: "v1",
          alignment_id: "leo_twin.runtime_export_boundary_alignment.v1",
          source: "BACKEND_RUNTIME_EXPORT_RESTORE_PREFLIGHT",
          alignment_scope: "PACKAGE_COMPARE_AND_RESTORE_BOUNDARY",
          package_id: "pkg",
          package_boundary_present: true,
          current_boundary_present: false,
          boundary_hash: "sha256:boundary",
          current_boundary_hash: "",
          boundary_hash_matches_current: false,
          boundary_id_aligned: true,
          restore_scope: "CONFIG_ONLY",
          compare_scope: "CONFIG_AND_GENERATED_CONFIG",
          read_scope: "PERSISTED_ARTIFACTS_ONLY",
          preflight_scope: "CONFIG_RESTORE_PREVIEW_ONLY",
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
          alignment_status: "ALIGNED",
          warnings: [],
          alignment_hash: "sha256:alignment"
        },
        boundary_alignment_hash: "sha256:alignment",
        boundary_alignment_status: "ALIGNED",
        boundary_alignment_warnings: [],
        runtime_export_boundary_hash: "sha256:boundary",
        record_count: 1,
        match_count: 0,
        different_count: 1,
        unavailable_count: 0,
        error_count: 0,
        records: [
          {
            route_id: "route:0",
            comparison_status: "DIFFERENT",
            package_route_detail_hash: "sha256:package",
            live_route_detail_hash: "sha256:live",
            matched_field_count: 1,
            different_field_count: 1,
            compared_fields: ["latency", "bottleneck"],
            different_fields: ["latency"],
            status_reason: "FIELDS_DIFFER",
            operator_note: "operator reviewed"
          }
        ],
        ordering: "route_id ascending, then comparison_status ascending",
        boundary_conditions: ["NO_ROUTE_RECOMPUTE"],
        report_hash: "sha256:report"
      })
    }));
    vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);

    await expect(
      loadRuntimeExportRouteComparisonReviewReport("pkg")
    ).resolves.toMatchObject({
      package_id: "pkg",
      record_count: 1,
      different_count: 1,
      runtime_export_boundary_hash: "sha256:boundary",
      records: [{ route_id: "route:0", operator_note: "operator reviewed" }]
    });
    expect(fetchMock).toHaveBeenCalledWith(
      "/runtime/export/packages/pkg/files/route_comparison_review_report_v1.json"
    );
  });

  it("saves runtime export scenario review checklists", async () => {
    const fetchMock = vi.fn(async () => ({
      ok: true,
      json: async () => ({
        type: "RUNTIME_EXPORT_SCENARIO_REVIEW_CHECKLIST",
        summary: {
          type: "RUNTIME_EXPORT_SCENARIO_REVIEW_CHECKLIST_V1",
          version: "v1",
          checklist_id: "leo_twin.runtime_export_scenario_review_checklist.v1",
          source: "OPERATOR_SCENARIO_REVIEW_CHECKLIST",
          checklist_scope: "SCENARIO_REVIEW_BUNDLE_OPERATOR_DECISIONS",
          package_id: "pkg",
          package_dir: "artifacts/runtime_exports/pkg",
          scenario_review_bundle_id: "leo_twin.runtime_export_scenario_review_bundle.v1",
          scenario_review_hash: "sha256:scenario-review",
          record_count: 1,
          reviewed_count: 1,
          skipped_count: 0,
          followup_count: 0,
          error_count: 0,
          checklist_status: "CHECKLIST_COMPLETE",
          records: [
            {
              artifact_filename: "scenario_review_bundle_v1.json",
              step_label: "Scenario bundle checked",
              review_status: "REVIEWED",
              status_reason: "",
              operator_note: "reviewed",
              evidence_hash: "sha256:scenario-review",
              review_order_index: 0,
              record_hash: "sha256:record"
            }
          ],
          ordering: "recommended_review_order ascending",
          boundary_conditions: ["NO_EVENT_REPLAY"],
          checklist_hash: "sha256:checklist"
        },
        artifact: {
          name: "scenario_review_checklist_v1",
          filename: "scenario_review_checklist_v1.json",
          bytes: 256,
          sha256: "sha256:artifact"
        }
      })
    }));
    vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);

    await expect(
      saveRuntimeExportScenarioReviewChecklist("pkg", {
        records: [
          {
            artifact_filename: "scenario_review_bundle_v1.json",
            step_label: "Scenario bundle checked",
            review_status: "REVIEWED",
            operator_note: "reviewed",
            evidence_hash: "sha256:scenario-review"
          }
        ]
      })
    ).resolves.toMatchObject({
      package_id: "pkg",
      record_count: 1,
      reviewed_count: 1,
      checklist_status: "CHECKLIST_COMPLETE",
      checklist_hash: "sha256:checklist"
    });
    expect(fetchMock).toHaveBeenCalledWith(
      "/runtime/export/packages/pkg/scenario-review-checklist",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          records: [
            {
              artifact_filename: "scenario_review_bundle_v1.json",
              step_label: "Scenario bundle checked",
              review_status: "REVIEWED",
              operator_note: "reviewed",
              evidence_hash: "sha256:scenario-review"
            }
          ]
        })
      }
    );
  });

  it("saves runtime export service trace comparison review reports", async () => {
    const fetchMock = vi.fn(async () => ({
      ok: true,
      json: async () => ({
        type: "RUNTIME_EXPORT_SERVICE_TRACE_COMPARISON_REVIEW_REPORT",
        summary: {
          type: "RUNTIME_EXPORT_SERVICE_TRACE_COMPARISON_REVIEW_REPORT_V1",
          version: "v1",
          report_id:
            "leo_twin.runtime_export_service_trace_comparison_review_report.v1",
          source: "OPERATOR_SERVICE_TRACE_COMPARISON_REVIEW",
          report_scope:
            "SELECTED_PACKAGE_VS_LIVE_SERVICE_TRACE_COMPARISON_OUTCOMES",
          package_id: "pkg",
          package_dir: "artifacts/runtime_exports/pkg",
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
            compared_fields: ["terminal", "reason", "total_latency"],
            status_reasons: ["TRACE_ID_MISMATCH"],
            boundary_conditions: ["NO_SERVICE_RECOMPUTE"]
          },
          boundary_alignment_hash: "sha256:alignment",
          boundary_alignment_status: "ALIGNED",
          boundary_alignment_warnings: [],
          runtime_export_boundary_hash: "sha256:boundary",
          record_count: 1,
          match_count: 0,
          different_count: 1,
          unavailable_count: 0,
          error_count: 0,
          records: [
            {
              trace_id: "trace:0",
              comparison_status: "DIFFERENT",
              package_trace_item_hash: "sha256:package",
              live_trace_detail_hash: "",
              matched_field_count: 2,
              different_field_count: 1,
              compared_fields: ["terminal", "reason", "total_latency"],
              different_fields: ["terminal"],
              status_reason: "FIELDS_DIFFER",
              operator_note: "operator reviewed"
            }
          ],
          ordering: "trace_id ascending, then comparison_status ascending",
          boundary_conditions: ["NO_SERVICE_RECOMPUTE"],
          report_hash: "sha256:trace-report"
        },
        artifact: {
          name: "service_trace_comparison_review_report_v1",
          filename: "service_trace_comparison_review_report_v1.json",
          bytes: 256,
          sha256: "sha256:artifact"
        }
      })
    }));
    vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);

    await expect(
      saveRuntimeExportServiceTraceComparisonReviewReport("pkg", {
        records: [
          {
            trace_id: "trace:0",
            comparison_status: "DIFFERENT",
            different_fields: ["terminal"],
            status_reason: "FIELDS_DIFFER"
          }
        ]
      })
    ).resolves.toMatchObject({
      package_id: "pkg",
      record_count: 1,
      different_count: 1,
      boundary_alignment_status: "ALIGNED",
      records: [{ trace_id: "trace:0", status_reason: "FIELDS_DIFFER" }]
    });
    expect(fetchMock).toHaveBeenCalledWith(
      "/runtime/export/packages/pkg/service-trace-comparison-review-report",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          records: [
            {
              trace_id: "trace:0",
              comparison_status: "DIFFERENT",
              different_fields: ["terminal"],
              status_reason: "FIELDS_DIFFER"
            }
          ]
        })
      }
    );
  });

  it("loads saved runtime export service trace comparison review report artifacts", async () => {
    const fetchMock = vi.fn(async () => ({
      ok: true,
      json: async () => ({
        type: "RUNTIME_EXPORT_SERVICE_TRACE_COMPARISON_REVIEW_REPORT_V1",
        version: "v1",
        report_id:
          "leo_twin.runtime_export_service_trace_comparison_review_report.v1",
        source: "OPERATOR_SERVICE_TRACE_COMPARISON_REVIEW",
        report_scope:
          "SELECTED_PACKAGE_VS_LIVE_SERVICE_TRACE_COMPARISON_OUTCOMES",
        package_id: "pkg",
        package_dir: "artifacts/runtime_exports/pkg",
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
        record_count: 1,
        match_count: 1,
        different_count: 0,
        unavailable_count: 0,
        error_count: 0,
        records: [
          {
            trace_id: "trace:0",
            comparison_status: "MATCH",
            package_trace_item_hash: "sha256:package",
            live_trace_detail_hash: "",
            matched_field_count: 1,
            different_field_count: 0,
            compared_fields: ["terminal"],
            different_fields: [],
            status_reason: "MATCHED",
            operator_note: ""
          }
        ],
        ordering: "trace_id ascending, then comparison_status ascending",
        boundary_conditions: ["NO_SERVICE_RECOMPUTE"],
        report_hash: "sha256:trace-report"
      })
    }));
    vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);

    await expect(
      loadRuntimeExportServiceTraceComparisonReviewReport("pkg")
    ).resolves.toMatchObject({
      package_id: "pkg",
      record_count: 1,
      report_hash: "sha256:trace-report",
      records: [{ trace_id: "trace:0", comparison_status: "MATCH" }]
    });
    expect(fetchMock).toHaveBeenCalledWith(
      "/runtime/export/packages/pkg/files/service_trace_comparison_review_report_v1.json"
    );
  });

  it("loads saved runtime export service trace comparison review report pages", async () => {
    const fetchMock = vi.fn(async () => ({
      ok: true,
      json: async () => ({
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
        package_id: "pkg",
        package_dir: "artifacts/runtime_exports/pkg",
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
        report_record_count: 2,
        record_count: 1,
        unfiltered_record_count: 2,
        match_count: 0,
        different_count: 1,
        unavailable_count: 0,
        error_count: 0,
        cursor: 0,
        limit: 5,
        next_cursor: 1,
        has_more: false,
        item_count: 1,
        hidden_record_count: 0,
        filter_applied: true,
        filters: {
          query: "operator",
          status: "DIFFERENT"
        },
        records: [
          {
            trace_id: "trace:0",
            comparison_status: "DIFFERENT",
            package_trace_item_hash: "sha256:package",
            live_trace_detail_hash: "sha256:live",
            matched_field_count: 0,
            different_field_count: 1,
            compared_fields: ["terminal"],
            different_fields: ["terminal"],
            status_reason: "FIELDS_DIFFER",
            operator_note: "operator reviewed"
          }
        ],
        ordering: "trace_id ascending, then comparison_status ascending",
        boundary_conditions: ["NO_SERVICE_RECOMPUTE"],
        report_hash: "sha256:trace-report",
        page_hash: "sha256:trace-page"
      })
    }));
    vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);

    await expect(
      loadRuntimeExportServiceTraceComparisonReviewReportPage("pkg", 0, 5, {
        query: "operator",
        status: "DIFFERENT"
      })
    ).resolves.toMatchObject({
      package_id: "pkg",
      page_hash: "sha256:trace-page",
      records: [{ trace_id: "trace:0", comparison_status: "DIFFERENT" }]
    });
    expect(fetchMock).toHaveBeenCalledWith(
      "/runtime/export/packages/pkg/service-trace-comparison-review-report/records?cursor=0&limit=5&query=operator&status=DIFFERENT"
    );
  });

  it("loads runtime export package audit index artifacts", async () => {
    const fetchMock = vi.fn(async () => ({
      ok: true,
      json: async () => ({
        type: "RUNTIME_EXPORT_PACKAGE_AUDIT_INDEX_V1",
        version: "v1",
        audit_index_id: "leo_twin.runtime_export_package_audit_index.v1",
        source: "BACKEND_RUNTIME_EXPORT_PACKAGE",
        audit_scope: "RESULT_PACKAGE_LONG_TERM_AUDIT_INDEX",
        package_id: "pkg",
        package_dir: "artifacts/runtime_exports/pkg",
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
        route_comparison_review_report_hash: "sha256:report",
        route_comparison_review_report_present: true,
        scenario_review_checklist_hash: "sha256:checklist",
        scenario_review_checklist_present: true,
        scenario_review_checklist_record_count: 1,
        scenario_review_checklist_status: "CHECKLIST_COMPLETE",
        artifact_count: 1,
        artifact_hashes: [
          {
            name: "manifest",
            filename: "manifest.json",
            bytes: 256,
            sha256: "sha256:manifest-file"
          }
        ],
        required_artifact_filenames: ["manifest.json"],
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
      })
    }));
    vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);

    await expect(loadRuntimeExportPackageAuditIndex("pkg")).resolves.toMatchObject({
      package_id: "pkg",
      audit_status: "AUDIT_READY",
      route_comparison_review_report_hash: "sha256:report",
      scenario_review_checklist_hash: "sha256:checklist",
      artifact_hashes: [{ filename: "manifest.json" }]
    });
    expect(fetchMock).toHaveBeenCalledWith(
      "/runtime/export/packages/pkg/files/export_package_audit_index_v1.json"
    );
  });

  it("loads runtime export package review completion summaries", async () => {
    const fetchMock = vi.fn(async () => ({
      ok: true,
      json: async () => ({
        type: "RUNTIME_EXPORT_PACKAGE_REVIEW_COMPLETION",
        summary: {
          type: "RUNTIME_EXPORT_PACKAGE_REVIEW_COMPLETION_V1",
          version: "v1",
          completion_id: "leo_twin.runtime_export_package_review_completion.v1",
          source: "BACKEND_RUNTIME_EXPORT_PACKAGE_AUDIT_INDEX",
          completion_scope: "RESULT_PACKAGE_OPERATOR_HANDOFF_READINESS",
          package_id: "pkg",
          package_dir: "artifacts/runtime_exports/pkg",
          completion_status: "REVIEW_COMPLETE",
          handoff_ready: true,
          audit_status: "AUDIT_READY",
          audit_warnings: [],
          route_comparison_review_report_present: true,
          route_comparison_review_report_hash: "sha256:route-report",
          route_comparison_review_record_count: 1,
          route_comparison_review_error_count: 0,
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
          evidence_labels: ["audit AUDIT_READY"],
          boundary_conditions: ["BACKEND_OWNED_HANDOFF_SUMMARY"],
          completion_hash: "sha256:completion"
        },
        source_artifact: {
          name: "export_package_audit_index_v1",
          filename: "export_package_audit_index_v1.json",
          bytes: 512,
          sha256: "sha256:audit-artifact"
        }
      })
    }));
    vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);

    await expect(loadRuntimeExportPackageReviewCompletion("pkg")).resolves.toMatchObject({
      package_id: "pkg",
      completion_status: "REVIEW_COMPLETE",
      handoff_ready: true,
      completion_hash: "sha256:completion"
    });
    expect(fetchMock).toHaveBeenCalledWith(
      "/runtime/export/packages/pkg/review-completion"
    );
  });

  it("loads runtime export package acceptance reports", async () => {
    const fetchMock = vi.fn(async () => ({
      ok: true,
      json: async () => ({
        type: "RUNTIME_EXPORT_PACKAGE_ACCEPTANCE_REPORT",
        summary: {
          type: "RUNTIME_EXPORT_PACKAGE_ACCEPTANCE_REPORT_V1",
          version: "v1",
          acceptance_id:
            "leo_twin.runtime_export_package_acceptance_report.v1",
          source: "BACKEND_RUNTIME_EXPORT_PACKAGE_AUDIT_INDEX",
          acceptance_scope: "INDUSTRIAL_V2_DEMO_CLOSED_LOOP_ACCEPTANCE",
          package_id: "pkg",
          package_dir: "artifacts/runtime_exports/pkg",
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
              check_id: "review_completion",
              status: "PASS",
              summary: "REVIEW_COMPLETE",
              evidence_hash: "sha256:completion",
              evidence_labels: ["audit AUDIT_READY"],
              issue_labels: [],
              recommendation: "no action",
              check_hash: "sha256:check"
            }
          ],
          operator_next_actions: [],
          evidence_hashes: ["audit sha256:audit"],
          boundary_conditions: ["BACKEND_OWNED_ACCEPTANCE_SUMMARY"],
          acceptance_hash: "sha256:acceptance"
        },
        source_artifact: {
          name: "export_package_audit_index_v1",
          filename: "export_package_audit_index_v1.json",
          bytes: 512,
          sha256: "sha256:audit-artifact"
        }
      })
    }));
    vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);

    await expect(loadRuntimeExportPackageAcceptanceReport("pkg")).resolves.toMatchObject({
      package_id: "pkg",
      acceptance_status: "PASS",
      demo_closed_loop_ready: true,
      acceptance_hash: "sha256:acceptance"
    });
    expect(fetchMock).toHaveBeenCalledWith(
      "/runtime/export/packages/pkg/acceptance-report"
    );
  });

  it("loads runtime export package handoff reports", async () => {
    const fetchMock = vi.fn(async () => ({
      ok: true,
      text: async () => "# Runtime Export Package Handoff Report v1\n"
    }));
    vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);

    await expect(loadRuntimeExportPackageHandoffReport("pkg")).resolves.toBe(
      "# Runtime Export Package Handoff Report v1\n"
    );
    expect(fetchMock).toHaveBeenCalledWith(
      "/runtime/export/packages/pkg/handoff-report"
    );
  });

  it("loads runtime export scenario review bundle artifacts", async () => {
    const fetchMock = vi.fn(async () => ({
      ok: true,
      json: async () => ({
        type: "RUNTIME_EXPORT_SCENARIO_REVIEW_BUNDLE_V1",
        version: "v1",
        bundle_id: "leo_twin.runtime_export_scenario_review_bundle.v1",
        source: "BACKEND_RUNTIME_EXPORT_PACKAGE",
        review_scope: "USER_CONFIGURATION_TO_RESULT_PACKAGE_REVIEW",
        package_id: "pkg",
        package_dir: "artifacts/runtime_exports/pkg",
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
          processed_event_count: 200,
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
          finding_count: 1,
          finding_labels: [{ severity: "INFO", code: "RESULT_PACKAGE_REVIEW_READY" }]
        },
        audit_index: {
          audit_index_id: "leo_twin.runtime_export_package_audit_index.v1",
          filename: "export_package_audit_index_v1.json",
          hash_binding_direction:
            "audit index records this scenario_review_bundle_v1.json file hash"
        },
        artifact_review: {
          artifact_count: 8,
          artifact_filenames: ["manifest.json"],
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
        recommended_review_order: ["scenario_review_bundle_v1.json"],
        scenario_review_status: "SCENARIO_REVIEW_READY",
        scenario_review_warnings: [],
        scenario_review_hash: "sha256:scenario-review"
      })
    }));
    vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);

    await expect(loadRuntimeExportScenarioReviewBundle("pkg")).resolves.toMatchObject({
      package_id: "pkg",
      scenario_review_status: "SCENARIO_REVIEW_READY",
      user_configuration: { validation_ok: true },
      scenario_review_hash: "sha256:scenario-review"
    });
    expect(fetchMock).toHaveBeenCalledWith(
      "/runtime/export/packages/pkg/files/scenario_review_bundle_v1.json"
    );
  });

  it("loads runtime export scenario review checklist artifacts", async () => {
    const fetchMock = vi.fn(async () => ({
      ok: true,
      json: async () => ({
        type: "RUNTIME_EXPORT_SCENARIO_REVIEW_CHECKLIST_V1",
        version: "v1",
        checklist_id: "leo_twin.runtime_export_scenario_review_checklist.v1",
        source: "OPERATOR_SCENARIO_REVIEW_CHECKLIST",
        checklist_scope: "SCENARIO_REVIEW_BUNDLE_OPERATOR_DECISIONS",
        package_id: "pkg",
        package_dir: "artifacts/runtime_exports/pkg",
        scenario_review_bundle_id: "leo_twin.runtime_export_scenario_review_bundle.v1",
        scenario_review_hash: "sha256:scenario-review",
        record_count: 1,
        reviewed_count: 1,
        skipped_count: 0,
        followup_count: 0,
        error_count: 0,
        checklist_status: "CHECKLIST_COMPLETE",
        records: [
          {
            artifact_filename: "scenario_review_bundle_v1.json",
            step_label: "Scenario bundle checked",
            review_status: "REVIEWED",
            status_reason: "",
            operator_note: "reviewed",
            evidence_hash: "sha256:scenario-review",
            review_order_index: 0,
            record_hash: "sha256:record"
          }
        ],
        ordering: "recommended_review_order ascending",
        boundary_conditions: ["NO_EVENT_REPLAY"],
        checklist_hash: "sha256:checklist"
      })
    }));
    vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);

    await expect(loadRuntimeExportScenarioReviewChecklist("pkg")).resolves.toMatchObject({
      package_id: "pkg",
      record_count: 1,
      checklist_status: "CHECKLIST_COMPLETE",
      checklist_hash: "sha256:checklist"
    });
    expect(fetchMock).toHaveBeenCalledWith(
      "/runtime/export/packages/pkg/files/scenario_review_checklist_v1.json"
    );
  });

  it("loads runtime export scenario review checklist templates", async () => {
    const fetchMock = vi.fn(async () => ({
      ok: true,
      json: async () => ({
        type: "RUNTIME_EXPORT_SCENARIO_REVIEW_CHECKLIST_TEMPLATE",
        summary: {
          type: "RUNTIME_EXPORT_SCENARIO_REVIEW_CHECKLIST_TEMPLATE_V1",
          version: "v1",
          template_id:
            "leo_twin.runtime_export_scenario_review_checklist_template.v1",
          source: "BACKEND_RUNTIME_EXPORT_PACKAGE",
          template_scope: "SCENARIO_REVIEW_RECOMMENDED_STEPS_OPERATOR_TEMPLATE",
          package_id: "pkg",
          package_dir: "artifacts/runtime_exports/pkg",
          scenario_review_bundle_id:
            "leo_twin.runtime_export_scenario_review_bundle.v1",
          scenario_review_hash: "sha256:scenario-review",
          audit_hash: "sha256:audit",
          expected_review_filenames: ["scenario_review_bundle_v1.json"],
          expected_review_count: 1,
          evidence_present_count: 1,
          missing_evidence_filenames: [],
          missing_evidence_count: 0,
          template_status: "TEMPLATE_READY",
          records: [
            {
              artifact_filename: "scenario_review_bundle_v1.json",
              step_label: "1 scenario entry",
              review_status: "NEEDS_FOLLOWUP",
              status_reason: "OPERATOR_REVIEW_REQUIRED",
              operator_note: "",
              evidence_hash: "sha256:scenario-review",
              evidence_present: true,
              evidence_source: "BACKEND_REVIEW_EVIDENCE_HASH",
              review_order_index: 0,
              template_record_hash: "sha256:template-record"
            }
          ],
          record_policy: "template records prefill evidence",
          boundary_conditions: ["NO_EVENT_REPLAY"],
          template_hash: "sha256:template"
        },
        scenario_review_bundle_artifact: {
          name: "scenario_review_bundle_v1",
          filename: "scenario_review_bundle_v1.json",
          bytes: 1024,
          sha256: "sha256:scenario-file"
        }
      })
    }));
    vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);

    await expect(
      loadRuntimeExportScenarioReviewChecklistTemplate("pkg")
    ).resolves.toMatchObject({
      package_id: "pkg",
      template_status: "TEMPLATE_READY",
      expected_review_count: 1,
      records: [
        {
          artifact_filename: "scenario_review_bundle_v1.json",
          evidence_hash: "sha256:scenario-review"
        }
      ],
      template_hash: "sha256:template"
    });
    expect(fetchMock).toHaveBeenCalledWith(
      "/runtime/export/packages/pkg/scenario-review-checklist-template"
    );
  });

  it("loads runtime export scenario review checklist template comparison", async () => {
    const fetchMock = vi.fn(async () => ({
      ok: true,
      json: async () => ({
        type: "RUNTIME_EXPORT_SCENARIO_REVIEW_CHECKLIST_TEMPLATE_COMPARISON",
        summary: {
          type: "RUNTIME_EXPORT_SCENARIO_REVIEW_CHECKLIST_TEMPLATE_COMPARISON_V1",
          version: "v1",
          comparison_id:
            "leo_twin.runtime_export_scenario_review_checklist_template_comparison.v1",
          source: "BACKEND_RUNTIME_EXPORT_PACKAGE",
          comparison_scope: "SAVED_CHECKLIST_VS_LATEST_BACKEND_TEMPLATE",
          package_id: "pkg",
          package_dir: "exports/pkg",
          scenario_review_hash: "sha256:scenario-review",
          template_hash: "sha256:template",
          template_status: "TEMPLATE_READY",
          checklist_present: true,
          checklist_hash: "sha256:checklist",
          checklist_status: "CHECKLIST_COMPLETE",
          comparison_status: "ALIGNED",
          template_record_count: 1,
          checklist_record_count: 1,
          aligned_record_count: 1,
          missing_checklist_record_count: 0,
          evidence_hash_mismatch_count: 0,
          operator_attention_count: 0,
          extra_checklist_record_count: 0,
          records: [
            {
              artifact_filename: "scenario_review_bundle_v1.json",
              step_label: "1 scenario entry",
              review_order_index: 0,
              template_evidence_hash: "sha256:scenario-review",
              template_record_hash: "sha256:template-record",
              checklist_evidence_hash: "sha256:scenario-review",
              checklist_record_hash: "sha256:checklist-record",
              checklist_review_status: "REVIEWED",
              comparison_status: "ALIGNED",
              issue_labels: [],
              comparison_record_hash: "sha256:comparison-record"
            }
          ],
          extra_records: [],
          boundary_conditions: ["NO_EVENT_REPLAY"],
          comparison_hash: "sha256:comparison"
        },
        template: {
          type: "RUNTIME_EXPORT_SCENARIO_REVIEW_CHECKLIST_TEMPLATE_V1",
          version: "v1",
          template_id:
            "leo_twin.runtime_export_scenario_review_checklist_template.v1",
          source: "BACKEND_RUNTIME_EXPORT_PACKAGE",
          package_id: "pkg",
          package_dir: "exports/pkg",
          scenario_review_hash: "sha256:scenario-review",
          audit_hash: "sha256:audit",
          expected_review_filenames: ["scenario_review_bundle_v1.json"],
          expected_review_count: 1,
          evidence_present_count: 1,
          missing_evidence_filenames: [],
          missing_evidence_count: 0,
          template_status: "TEMPLATE_READY",
          records: [],
          record_policy: "template records prefill evidence",
          boundary_conditions: ["NO_EVENT_REPLAY"],
          template_hash: "sha256:template"
        },
        scenario_review_bundle_artifact: {
          name: "scenario_review_bundle_v1",
          filename: "scenario_review_bundle_v1.json",
          bytes: 1024,
          sha256: "sha256:scenario-file"
        }
      })
    }));
    vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);

    await expect(
      loadRuntimeExportScenarioReviewChecklistTemplateComparison("pkg")
    ).resolves.toMatchObject({
      package_id: "pkg",
      comparison_status: "ALIGNED",
      aligned_record_count: 1,
      comparison_hash: "sha256:comparison"
    });
    expect(fetchMock).toHaveBeenCalledWith(
      "/runtime/export/packages/pkg/scenario-review-checklist-template-comparison"
    );
  });

  it("loads runtime export restore preflight previews", async () => {
    const fetchMock = vi.fn(async () => ({
      ok: true,
      json: async () => ({
        type: "RUNTIME_EXPORT_RESTORE_PREFLIGHT",
        summary: {
          version: "v1",
          source: "BACKEND_RUNTIME_EXPORT_RESTORE_PREFLIGHT",
          preflight_scope: "CONFIG_RESTORE_PREVIEW_ONLY",
          package_id: "pkg",
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
          generated_config_diff_count: 3,
          compare_hash: "sha256:compare",
          blocked_reasons: [],
          warnings: ["RESTORE_WOULD_REPLACE_RUNTIME_CONFIG_AND_REQUIRE_REINITIALIZATION"],
          next_action: "USER_CONFIRMATION_REQUIRED_BEFORE_RESTORE",
          runtime_export_boundary_alignment_v1: {
            type: "RUNTIME_EXPORT_BOUNDARY_ALIGNMENT_V1",
            version: "v1",
            alignment_id: "leo_twin.runtime_export_boundary_alignment.v1",
            source: "BACKEND_RUNTIME_EXPORT_RESTORE_PREFLIGHT",
            alignment_scope: "PACKAGE_COMPARE_AND_RESTORE_BOUNDARY",
            package_id: "pkg",
            package_boundary_present: true,
            current_boundary_present: false,
            boundary_hash: "sha256:boundary",
            current_boundary_hash: "",
            boundary_hash_matches_current: false,
            boundary_id_aligned: true,
            restore_scope: "CONFIG_ONLY",
            compare_scope: "CONFIG_AND_GENERATED_CONFIG",
            read_scope: "PERSISTED_ARTIFACTS_ONLY",
            preflight_scope: "CONFIG_RESTORE_PREVIEW_ONLY",
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
            alignment_status: "ALIGNED",
            warnings: [],
            alignment_hash: "sha256:alignment"
          },
          preflight_hash: "sha256:preflight"
        }
      })
    }));
    vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);

    await expect(loadRuntimeExportRestorePreflight("pkg")).resolves.toMatchObject({
      readiness: "READY",
      requires_user_confirmation: true,
      would_mutate_current_runtime: false,
      runtime_export_boundary_alignment_v1: { preflight_scope_aligned: true }
    });
    expect(fetchMock).toHaveBeenCalledWith(
      "/runtime/export/packages/pkg/restore-preflight"
    );
  });

  it("loads runtime export history summaries", async () => {
    const fetchMock = vi.fn(async () => ({
      ok: true,
      json: async () => ({
        type: "RUNTIME_EXPORT_HISTORY",
        summary: {
          version: "v1",
          source: "BACKEND_RUNTIME_STATUS",
          history_scope: "CURRENT_SESSION_RECENT_EXPORTS",
          history_limit: 8,
          export_count: 1,
          retained_count: 1,
          latest_export: {
            sequence: 1,
            export_type: "ARCHIVE",
            package_id: "pkg",
            package_dir: "artifacts/runtime_exports/pkg",
            file_count: 6,
            manifest_hash: "sha256:abc",
            current_sim_time: 10,
            processed_event_count: 20,
            archive_filename: "pkg.zip",
            archive_sha256: "sha256:def",
            archive_bytes: 4096
          },
          items: []
        }
      })
    }));
    vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);

    await expect(loadRuntimeExportHistory()).resolves.toMatchObject({
      export_count: 1,
      latest_export: { export_type: "ARCHIVE", archive_filename: "pkg.zip" }
    });
    expect(fetchMock).toHaveBeenCalledWith("/runtime/export/history");
  });

  it("loads persisted runtime export catalogs", async () => {
    const fetchMock = vi.fn(async () => ({
      ok: true,
      json: async () => ({
        type: "RUNTIME_EXPORT_CATALOG",
        summary: {
          version: "v1",
          source: "BACKEND_RUNTIME_EXPORT",
          catalog_scope: "RUNTIME_EXPORT_ROOT",
          catalog_file: "artifacts/runtime_exports/runtime_export_catalog_v1.json",
          export_root: "artifacts/runtime_exports",
          record_count: 1,
          catalog_hash: "sha256:catalog",
          latest_export: {
            catalog_key: "ARCHIVE:pkg",
            export_type: "ARCHIVE",
            package_id: "pkg",
            package_dir: "artifacts/runtime_exports/pkg",
            relative_package_dir: "pkg",
            file_count: 6,
            manifest_hash: "sha256:manifest",
            current_sim_time: 10,
            processed_event_count: 20,
            files: [],
            archive_filename: "pkg.zip",
            archive_sha256: "sha256:archive",
            archive_bytes: 4096
          },
          records: []
        }
      })
    }));
    vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);

    await expect(loadRuntimeExportCatalog()).resolves.toMatchObject({
      record_count: 1,
      latest_export: { export_type: "ARCHIVE", archive_filename: "pkg.zip" }
    });
    expect(fetchMock).toHaveBeenCalledWith("/runtime/export/catalog");
  });

  it("loads user configuration contract payloads", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          type: "USER_CONFIGURATION_SCHEMA_V2",
          summary: {
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
            root_sections: [],
            fields: [],
            templates: [],
            examples: []
          }
        })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          type: "USER_CONFIGURATION_TEMPLATE_CATALOG",
          summary: {
            version: "v1",
            source: "BACKEND_USER_CONFIGURATION",
            schema_id: "sees.user_configuration.v2",
            catalog_scope: "APPROVED_EXECUTABLE_TEMPLATES",
            mutation_policy: "READ_ONLY_CATALOG",
            template_count: 1,
            templates: [
              {
                id: "baseline_72sat",
                label: "72-satellite baseline",
                path: "configs/templates/sees_user_detailed.example.yaml",
                purpose: "Baseline"
              }
            ],
            load_command: {
              type: "RUNTIME_CONTROL",
              action: "LOAD_TEMPLATE",
              payload_key: "template_id",
              requires_uninitialized_runtime: true
            }
          }
        })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          type: "USER_CONFIGURATION_TEMPLATE_VALIDATION_V1",
          summary: {
            version: "v1",
            evidence_id: "sees.user_configuration_template_validation.v1",
            source: "BACKEND_USER_CONFIGURATION",
            schema_id: "sees.user_configuration.v2",
            validation_scope: "APPROVED_EXECUTABLE_TEMPLATES",
            template_count: 1,
            valid_template_count: 1,
            invalid_template_count: 0,
            all_templates_valid: true,
            templates: [
              {
                id: "baseline_72sat",
                label: "72-satellite baseline",
                path: "configs/templates/sees_user_detailed.example.yaml",
                file_exists: true,
                file_hash: "sha256:file",
                config_hash: "sha256:config",
                load_ok: true,
                validation_ok: true,
                error_count: 0,
                errors: [],
                row_hash: "sha256:row"
              }
            ],
            evidence_hash: "sha256:template-validation"
          }
        })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          type: "USER_CONFIGURATION_REFERENCE_V1",
          summary: {
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
              apply_commands: ["CONFIG_UPDATE"]
            },
            field_count: 42,
            key_field_count: 12,
            file_only_field_count: 30,
            section_count: 1,
            sections: [
              {
                section: "scenario",
                purpose: "Scenario",
                field_count: 10,
                key_field_count: 4,
                file_only_field_count: 6,
                key_paths: ["scenario.satellite_count"],
                file_only_paths: ["scenario.compute_gpu_tflops_fp16"]
              }
            ],
            fields: [
              {
                path: "scenario.satellite_count",
                section: "scenario",
                label: "Satellite count",
                description: "Primary constellation size",
                value_type: "integer",
                editable_surface: "CONTROL_PANEL_KEY_FIELD",
                ui_key_field: true,
                default_value: 72,
                current_value: 96,
                required_in_user_file: false,
                validation_rules: ["integer"]
              }
            ],
            model_boundaries: {
              event_kernel_policy: "NO_EVENT_KERNEL_BEHAVIOR_CHANGE",
              packet_level_simulation: false,
              external_simulators: false,
              forbidden_integrations: ["STK", "EXATA", "AFSIM", "DDS"],
              frontend_semantics_source: "BACKEND_USER_CONFIGURATION"
            },
            operator_workflow: ["Use key fields first."],
            notes: ["Reference is backend-owned."],
            reference_hash: "sha256:reference"
          }
        })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          type: "USER_CONFIGURATION_EXPORT",
          summary: {
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
            config_hash: "sha256:config",
            validation_ok: true,
            validation_error_count: 0,
            validation_errors: [],
            config: {
              scenario: {
                satellite_count: 72
              }
            }
          }
        })
      });
    vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);

    await expect(loadUserConfigurationSchema()).resolves.toMatchObject({
      schema_id: "sees.user_configuration.v2",
      field_count: 42
    });
    await expect(loadUserConfigurationTemplates()).resolves.toMatchObject({
      template_count: 1,
      mutation_policy: "READ_ONLY_CATALOG"
    });
    await expect(loadUserConfigurationTemplateValidation()).resolves.toMatchObject({
      evidence_id: "sees.user_configuration_template_validation.v1",
      all_templates_valid: true
    });
    await expect(loadUserConfigurationReference()).resolves.toMatchObject({
      reference_id: "sees.user_configuration_reference.v1",
      field_count: 42,
      model_boundaries: { packet_level_simulation: false }
    });
    await expect(loadUserConfigurationExport()).resolves.toMatchObject({
      config_hash: "sha256:config",
      validation_ok: true
    });
    expect(fetchMock).toHaveBeenNthCalledWith(1, "/scenario/user-config/schema");
    expect(fetchMock).toHaveBeenNthCalledWith(2, "/scenario/user-config/templates");
    expect(fetchMock).toHaveBeenNthCalledWith(
      3,
      "/scenario/user-config/template-validation"
    );
    expect(fetchMock).toHaveBeenNthCalledWith(4, "/scenario/user-config/reference");
    expect(fetchMock).toHaveBeenNthCalledWith(5, "/scenario/user-config/export");
  });

  it("validates user configuration candidates through the backend preflight endpoint", async () => {
    const fetchMock = vi.fn(async () => ({
      ok: true,
      json: async () => ({
        type: "USER_CONFIGURATION_VALIDATION_REPORT",
        summary: {
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
          normalized_config_hash: "sha256:normalized",
          normalized_config: {
            scenario: {
              satellite_count: 72
            }
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
        }
      })
    }));
    vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);

    await expect(
      validateUserConfigurationCandidate({
        scenario: {
          satellite_count: 72
        }
      })
    ).resolves.toMatchObject({
      ok: true,
      mutation_policy: "VALIDATE_ONLY_NO_APPLY",
      normalized_config_hash: "sha256:normalized"
    });
    expect(fetchMock).toHaveBeenCalledWith("/scenario/user-config/validate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        scenario: {
          satellite_count: 72
        }
      })
    });
  });

  it("validates user configuration text through the backend text preflight endpoint", async () => {
    const fetchMock = vi.fn(async () => ({
      ok: true,
      json: async () => ({
        type: "USER_CONFIGURATION_VALIDATION_REPORT",
        summary: {
          version: "v1",
          source: "BACKEND_USER_CONFIGURATION",
          schema_id: "sees.user_configuration.v2",
          validation_scope: "USER_PROVIDED_CONFIG_TEXT",
          format: "YAML_TEXT",
          mutation_policy: "VALIDATE_ONLY_NO_APPLY",
          unknown_key_policy: "REJECT",
          defaulting_policy: "OMITTED_FIELDS_USE_BACKEND_DEFAULTS",
          ok: true,
          error_count: 0,
          errors: [],
          normalized_config_hash: "sha256:normalized",
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
          apply_command: {
            type: "CONFIG_UPDATE",
            action: "CONFIG_UPDATE",
            payload_source: "normalized_config",
            payload_format: "SEES_CONFIG_MAPPING",
            requires_preflight_ok: true,
            runtime_effect: "REINITIALIZES_SESSION_AND_STREAMS",
            requires_explicit_user_action: true
          }
        }
      })
    }));
    vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);

    await expect(
      validateUserConfigurationTextCandidate("scenario:\n  satellite_count: 72\n", "yaml")
    ).resolves.toMatchObject({
      ok: true,
      validation_scope: "USER_PROVIDED_CONFIG_TEXT",
      text_parse: {
        requested_format: "yaml",
        detected_format: "yaml"
      }
    });
    expect(userConfigurationValidateTextHref("yaml")).toBe(
      "/scenario/user-config/validate-text?format=yaml"
    );
    expect(fetchMock).toHaveBeenCalledWith(
      "/scenario/user-config/validate-text?format=yaml",
      {
        method: "POST",
        headers: {
          "Content-Type": "text/plain; charset=utf-8"
        },
        body: "scenario:\n  satellite_count: 72\n"
      }
    );
  });

  it("includes endpoint and HTTP status when runtime status fails", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => ({ ok: false, status: 503 })) as unknown as typeof fetch
    );

    await expect(loadRuntimeState("/runtime/status")).rejects.toThrow(
      "failed to load runtime status from /runtime/status: HTTP 503"
    );
  });

  it("loads paginated runtime detail pages", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          type: "RUNTIME_DETAIL_PAGE",
          kind: "users",
          summary: {
            version: "v1",
            source: "BACKEND_RUNTIME_SNAPSHOT",
            user_count: 2,
            item_count: 1,
            active_user_count: 1,
            compute_service_user_count: 0,
            waiting_user_count: 0,
            hidden_user_count: 1,
            items: []
          }
        })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          type: "RUNTIME_DETAIL_PAGE",
          kind: "satellites",
          summary: {
            version: "v1",
            satellite_count: 3,
            item_count: 1,
            hidden_satellite_count: 2,
            items: []
          }
        })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          type: "RUNTIME_DETAIL_PAGE",
          kind: "nodes",
          summary: {
            version: "v1",
            source: "BACKEND_RUNTIME_STATUS",
            cursor: 4,
            limit: 20,
            next_cursor: 5,
            has_more: false,
            node_count: 5,
            user_count: 2,
            satellite_count: 3,
            item_count: 1,
            hidden_node_count: 4,
            window_user_detail_count: 0,
            window_satellite_detail_count: 1,
            items: [
              {
                entity_type: "SATELLITE",
                entity_id: "sat-0",
                title: "卫星 sat-0",
                subtitle: "ACTIVE",
                fields: [{ label: "负载", value: "65%", tone: "resource" }]
              }
            ]
          }
        })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          type: "RUNTIME_DETAIL_PAGE",
          kind: "routes",
          summary: {
            version: "v1",
            source: "BACKEND_RUNTIME_SNAPSHOT",
            route_count: 1,
            item_count: 1,
            items: [{ route_id: "route-0" }]
          }
        })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          type: "RUNTIME_DETAIL_PAGE",
          kind: "services",
          summary: {
            version: "v1",
            source: "SERVICE_LATENCY_HISTORY",
            service_count: 1,
            item_count: 1,
            items: [{ service_id: "service-0" }]
          }
        })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          type: "RUNTIME_DETAIL_PAGE",
          kind: "service_traces",
          summary: {
            version: "v2",
            source: "SERVICE_LATENCY_HISTORY",
            source_summary: "service_latency_history_v1",
            service_count: 1,
            trace_count: 1,
            items: [{ trace_id: "trace:service-0" }]
          }
        })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          type: "RUNTIME_DETAIL_PAGE",
          kind: "compute_nodes",
          summary: {
            version: "v1",
            source: "BACKEND_RUNTIME_SNAPSHOT",
            compute_node_count: 1,
            item_count: 1,
            items: [{ node_id: "sat-0" }]
          }
        })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          type: "RUNTIME_DETAIL_PAGE",
          kind: "routes",
          summary: {
            version: "v1",
            source: "BACKEND_RUNTIME_SNAPSHOT",
            route_count: 1,
            item_count: 1,
            items: [{ route_id: "route-filtered" }]
          }
        })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          type: "RUNTIME_DETAIL_PAGE",
          kind: "services",
          summary: {
            version: "v1",
            source: "SERVICE_LATENCY_HISTORY",
            service_count: 1,
            item_count: 1,
            items: [{ service_id: "service-filtered" }]
          }
        })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          type: "RUNTIME_DETAIL_PAGE",
          kind: "service_traces",
          summary: {
            version: "v2",
            source: "SERVICE_LATENCY_HISTORY",
            source_summary: "service_latency_history_v1",
            service_count: 1,
            trace_count: 1,
            items: [{ trace_id: "trace:filtered" }]
          }
        })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          type: "RUNTIME_DETAIL_PAGE",
          kind: "compute_nodes",
          summary: {
            version: "v1",
            source: "BACKEND_RUNTIME_SNAPSHOT",
            compute_node_count: 1,
            item_count: 1,
            items: [{ node_id: "sat-filtered" }]
          }
        })
      });
    vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);

    await expect(loadRuntimeUserDetails(2, 80)).resolves.toMatchObject({
      user_count: 2,
      item_count: 1
    });
    await expect(loadRuntimeSatelliteDetails(3, 120)).resolves.toMatchObject({
      satellite_count: 3,
      item_count: 1
    });
    await expect(loadRuntimeNodeDetails(4, 20)).resolves.toMatchObject({
      node_count: 5,
      item_count: 1,
      items: [{ entity_id: "sat-0" }]
    });
    await expect(loadRuntimeRouteDetails(5, 30)).resolves.toMatchObject({
      route_count: 1,
      items: [{ route_id: "route-0" }]
    });
    await expect(loadRuntimeServiceDetails(6, 40)).resolves.toMatchObject({
      service_count: 1,
      items: [{ service_id: "service-0" }]
    });
    await expect(loadRuntimeServiceTraceDetails(7, 45)).resolves.toMatchObject({
      service_count: 1,
      items: [{ trace_id: "trace:service-0" }]
    });
    await expect(loadRuntimeComputeNodeDetails(8, 50)).resolves.toMatchObject({
      compute_node_count: 1,
      items: [{ node_id: "sat-0" }]
    });
    await expect(
      loadRuntimeRouteDetails(8, 60, "/runtime/details/routes", {
        query: "sat-1",
        availability: "BLOCKED",
        businessType: "DATA_TRANSFER",
        bottleneckComponent: "AVAILABILITY"
      })
    ).resolves.toMatchObject({
      route_count: 1,
      items: [{ route_id: "route-filtered" }]
    });
    await expect(
      loadRuntimeServiceDetails(9, 70, "/runtime/details/services", {
        query: "sat-1"
      })
    ).resolves.toMatchObject({
      service_count: 1,
      items: [{ service_id: "service-filtered" }]
    });
    await expect(
      loadRuntimeServiceTraceDetails(10, 75, "/runtime/details/service-traces", {
        query: "route:input",
        terminalState: "COMPLETE",
        computeNodeId: "sat-a",
        stageKind: "OUTPUT_NETWORK",
        terminalReason: "TOTAL_LATENCY_OBSERVED"
      })
    ).resolves.toMatchObject({
      trace_count: 1,
      items: [{ trace_id: "trace:filtered" }]
    });
    await expect(
      loadRuntimeComputeNodeDetails(11, 80, "/runtime/details/compute-nodes", {
        query: "busy"
      })
    ).resolves.toMatchObject({
      compute_node_count: 1,
      items: [{ node_id: "sat-filtered" }]
    });
    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      "/runtime/details/users?cursor=2&limit=80&summary_version=v2"
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      "/runtime/details/satellites?cursor=3&limit=120"
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      3,
      "/runtime/details/nodes?cursor=4&limit=20"
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      4,
      "/runtime/details/routes?cursor=5&limit=30"
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      5,
      "/runtime/details/services?cursor=6&limit=40"
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      6,
      "/runtime/details/service-traces?cursor=7&limit=45"
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      7,
      "/runtime/details/compute-nodes?cursor=8&limit=50"
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      8,
      "/runtime/details/routes?cursor=8&limit=60&query=sat-1&availability=BLOCKED&business_type=DATA_TRANSFER&bottleneck_component=AVAILABILITY"
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      9,
      "/runtime/details/services?cursor=9&limit=70&query=sat-1"
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      10,
      "/runtime/details/service-traces?cursor=10&limit=75&query=route%3Ainput&terminal_state=COMPLETE&compute_node_id=sat-a&stage_kind=OUTPUT_NETWORK&terminal_reason=TOTAL_LATENCY_OBSERVED"
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      11,
      "/runtime/details/compute-nodes?cursor=11&limit=80&query=busy"
    );
  });

  it("loads runtime user and satellite entity details by id", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          type: "RUNTIME_ENTITY_DETAIL",
          kind: "user",
          entity_id: "user-0001",
          summary: {
            entity_type: "USER",
            entity_id: "user-0001",
            title: "user detail",
            subtitle: "ACTIVE",
            fields: [{ label: "status", value: "ACTIVE" }]
          }
        })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          type: "RUNTIME_ENTITY_DETAIL",
          kind: "satellite",
          entity_id: "sat-001",
          summary: {
            entity_type: "SATELLITE",
            entity_id: "sat-001",
            title: "satellite detail",
            subtitle: "ACTIVE",
            fields: [{ label: "load", value: "20%" }]
          }
        })
      });
    vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);

    await expect(loadRuntimeUserDetail("user-0001")).resolves.toMatchObject({
      entity_type: "USER",
      entity_id: "user-0001"
    });
    await expect(loadRuntimeSatelliteDetail("sat-001")).resolves.toMatchObject({
      entity_type: "SATELLITE",
      entity_id: "sat-001"
    });
    expect(fetchMock).toHaveBeenNthCalledWith(1, "/runtime/details/users/user-0001");
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      "/runtime/details/satellites/sat-001"
    );
    expect(runtimeDetailEntityHref("user/with space", "/runtime/details/users/")).toBe(
      "/runtime/details/users/user%2Fwith%20space"
    );
  });

  it("loads runtime route service and compute-node entity details by id", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          type: "RUNTIME_ENTITY_DETAIL",
          kind: "route",
          entity_id: "route-0",
          summary: {
            route_id: "route-0",
            flow_id: "flow-0",
            user_id: "user-0",
            source_id: "user-0",
            destination_id: "sat-0",
            selected_satellite_id: "sat-0",
            primary_next_hop_id: "sat-0",
            next_hop_ids: ["sat-0"],
            hop_count: 1,
            path_label: "user-0 -> sat-0",
            available: true,
            route_pressure_proxy: 0.5,
            business_type: "DATA_TRANSFER",
            business_label: "Data transfer",
            bottleneck_component: "NONE",
            bottleneck_reason: "NO_BOTTLENECK",
            bottleneck_reason_label: "No bottleneck",
            explanation_label: "available"
          }
        })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          type: "RUNTIME_ENTITY_DETAIL",
          kind: "service",
          entity_id: "task-0",
          summary: {
            service_id: "task-0",
            task_id: "task-0",
            complete: false,
            service_state: "RUNNING",
            service_state_label: "Service running",
            input_network_latency_s: 0.1,
            compute_queue_delay_s: 0.2,
            compute_execution_delay_s: 0.3,
            output_network_latency_s: 0.4,
            total_latency_s: 1.0,
            stage_count: 0,
            stages: []
          }
        })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          type: "RUNTIME_ENTITY_DETAIL",
          kind: "service_trace",
          entity_id: "trace:svc-0",
          summary: {
            version: "v2",
            source: "BACKEND_RUNTIME_STATUS",
            summary_scope: "SERVICE_LIFECYCLE_TRACE_EXACT_DETAIL",
            detail_hash: "sha256:service-trace-detail",
            trace: {
              trace_id: "trace:svc-0",
              service_id: "svc-0",
              task_id: "svc-0-task",
              service_class: "COMPUTE_SERVICE",
              input_network_latency_s: 0.1,
              compute_queue_delay_s: 0.2,
              compute_execution_delay_s: 0.3,
              output_network_latency_s: 0.4,
              total_latency_s: 1.0,
              terminal_state: "RUNNING",
              terminal_state_reason: "OUTPUT_NETWORK_PENDING",
              stage_count: 4,
              observed_stage_count: 3,
              pending_stage_count: 1,
              stages: []
            },
            correlation: {
              trace_id: "trace:svc-0",
              service_id: "svc-0",
              task_id: "svc-0-task",
              flow_ids: ["svc-0-input"],
              route_ids: ["route-0"],
              user_ids: ["user-0"],
              satellite_ids: ["sat-0"],
              compute_node_id: "sat-0",
              route_count: 1,
              user_count: 1,
              satellite_count: 1,
              compute_node_detail_available: true
            },
            routes: [],
            users: [],
            satellites: [],
            compute_node: null
          }
        })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          type: "RUNTIME_ENTITY_DETAIL",
          kind: "compute_node",
          entity_id: "sat-0",
          summary: {
            node_id: "sat-0",
            platform_type: "SATELLITE_COMPUTE_NODE",
            status: "BUSY",
            compute_load_ratio: 0.5,
            compute_capacity_gflops_fp32: 100,
            compute_used_gflops_fp32: 50,
            compute_available_gflops_fp32: 50,
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
        })
      });
    vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);

    await expect(loadRuntimeRouteDetail("route-0")).resolves.toMatchObject({
      route_id: "route-0"
    });
    await expect(loadRuntimeServiceDetail("task-0")).resolves.toMatchObject({
      service_id: "task-0"
    });
    await expect(loadRuntimeServiceTraceDetail("trace:svc-0")).resolves.toMatchObject({
      trace: { trace_id: "trace:svc-0" },
      correlation: { route_count: 1 }
    });
    await expect(loadRuntimeComputeNodeDetail("sat-0")).resolves.toMatchObject({
      node_id: "sat-0"
    });
    expect(fetchMock).toHaveBeenNthCalledWith(1, "/runtime/details/routes/route-0");
    expect(fetchMock).toHaveBeenNthCalledWith(2, "/runtime/details/services/task-0");
    expect(fetchMock).toHaveBeenNthCalledWith(
      3,
      "/runtime/details/service-traces/trace%3Asvc-0"
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      4,
      "/runtime/details/compute-nodes/sat-0"
    );
  });

  it("rejects malformed runtime detail pages", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => ({
        ok: true,
        json: async () => ({
          type: "RUNTIME_DETAIL_PAGE",
          kind: "satellites",
          summary: {}
        })
      })) as unknown as typeof fetch
    );

    await expect(loadRuntimeUserDetails()).rejects.toThrow(
      "runtime detail response kind must be users, got satellites"
    );
  });

  it("maps network failures to launcher troubleshooting text", () => {
    expect(runtimeApiErrorMessage(new TypeError("Failed to fetch"))).toContain(
      "scripts\\sees_launcher.ps1 status"
    );
  });

  it("maps backend HTTP failures to a user-visible endpoint error", () => {
    expect(
      runtimeApiErrorMessage(
        new Error("failed to load runtime status from /runtime/status: HTTP 500")
      )
    ).toBe("后端接口返回错误：failed to load runtime status from /runtime/status: HTTP 500");
  });

  it("maps malformed payloads to a frontend contract message", () => {
    expect(runtimeApiErrorMessage(new TypeError("runtime status must be an object"))).toBe(
      "后端接口格式不符合前端契约：runtime status must be an object"
    );
  });
});
