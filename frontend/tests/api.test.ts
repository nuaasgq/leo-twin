import { afterEach, describe, expect, it, vi } from "vitest";

import {
  loadRuntimeExportCatalog,
  loadRuntimeExportDiagnosticsBundle,
  loadRuntimeExportHistory,
  loadRuntimeExportManifest,
  loadRuntimeExportPackageCompare,
  loadRuntimeExportRouteDetailIndex,
  loadRuntimeExportRouteDetailItem,
  loadRuntimeExportRouteDetailPage,
  loadRuntimeExportReviewSummary,
  loadRuntimeExportRestorePreflight,
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
  loadUserConfigurationSchema,
  loadUserConfigurationTemplates,
  validateUserConfigurationCandidate,
  validateUserConfigurationTextCandidate,
  runtimeExportArchiveHref,
  runtimeExportPackageArchiveHref,
  runtimeExportPackageCompareHref,
  runtimeExportPackageFileHref,
  runtimeExportPackageManifestHref,
  runtimeExportPackageRecordHref,
  runtimeExportPackageRouteDetailsHref,
  runtimeExportPackageRouteDetailHref,
  runtimeExportPackageReviewSummaryHref,
  runtimeExportRestorePreflightHref,
  runtimeDetailEntityHref,
  userConfigurationExportHref,
  userConfigurationSchemaHref,
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
  });

  it("exposes stable user configuration contract links", () => {
    expect(userConfigurationSchemaHref()).toBe("/scenario/user-config/schema");
    expect(userConfigurationTemplatesHref()).toBe("/scenario/user-config/templates");
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
          compare_hash: "sha256:compare"
        }
      })
    }));
    vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);

    await expect(loadRuntimeExportPackageCompare("pkg")).resolves.toMatchObject({
      compatibility: "DIFFERENT",
      diff_count: 1,
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
          preflight_hash: "sha256:preflight"
        }
      })
    }));
    vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);

    await expect(loadRuntimeExportRestorePreflight("pkg")).resolves.toMatchObject({
      readiness: "READY",
      requires_user_confirmation: true,
      would_mutate_current_runtime: false
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
    await expect(loadUserConfigurationExport()).resolves.toMatchObject({
      config_hash: "sha256:config",
      validation_ok: true
    });
    expect(fetchMock).toHaveBeenNthCalledWith(1, "/scenario/user-config/schema");
    expect(fetchMock).toHaveBeenNthCalledWith(2, "/scenario/user-config/templates");
    expect(fetchMock).toHaveBeenNthCalledWith(3, "/scenario/user-config/export");
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
      "/runtime/details/users?cursor=2&limit=80"
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
