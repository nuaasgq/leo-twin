import { afterEach, describe, expect, it, vi } from "vitest";

import {
  loadRuntimeExportCatalog,
  loadRuntimeExportHistory,
  loadRuntimeExportPackageCompare,
  loadRuntimeExportRestorePreflight,
  loadRuntimeComputeNodeDetails,
  loadRuntimeNodeDetails,
  loadRuntimeRouteDetails,
  loadRuntimeSatelliteDetails,
  loadRuntimeServiceDetails,
  loadRuntimeState,
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
  runtimeExportRestorePreflightHref,
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
    await expect(loadRuntimeComputeNodeDetails(7, 50)).resolves.toMatchObject({
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
      "/runtime/details/compute-nodes?cursor=7&limit=50"
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      7,
      "/runtime/details/routes?cursor=8&limit=60&query=sat-1&availability=BLOCKED&business_type=DATA_TRANSFER&bottleneck_component=AVAILABILITY"
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
