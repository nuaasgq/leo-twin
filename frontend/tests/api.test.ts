import { afterEach, describe, expect, it, vi } from "vitest";

import {
  loadRuntimeSatelliteDetails,
  loadRuntimeState,
  loadRuntimeUserDetails,
  runtimeApiErrorMessage
} from "../src/app/api";

describe("runtime API diagnostics", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
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
            source: "BACKEND_RUNTIME_SNAPSHOT",
            satellite_count: 3,
            item_count: 1,
            hidden_satellite_count: 2,
            items: []
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
    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      "/runtime/details/users?cursor=2&limit=80"
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      "/runtime/details/satellites?cursor=3&limit=120"
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
