import { afterEach, describe, expect, it, vi } from "vitest";

import {
  loadRuntimeExportCatalog,
  loadRuntimeExportHistory,
  loadRuntimeNodeDetails,
  loadRuntimeSatelliteDetails,
  loadRuntimeState,
  loadRuntimeUserDetails,
  runtimeExportArchiveHref,
  runtimeExportPackageArchiveHref,
  runtimeExportPackageFileHref,
  runtimeExportPackageManifestHref,
  runtimeExportPackageRecordHref,
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
    expect(runtimeExportPackageFileHref("pkg 1", "events 1.jsonl")).toBe(
      "/runtime/export/packages/pkg%201/files/events%201.jsonl"
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

  it("includes endpoint and HTTP status when runtime status fails", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => ({ ok: false, status: 503 })) as unknown as typeof fetch
    );

    await expect(loadRuntimeState("/runtime/status")).rejects.toThrow(
      "failed to load runtime status from /runtime/status: HTTP 503"
    );
  });

  it("loads paginated runtime user and satellite detail pages", async () => {
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
