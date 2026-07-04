import { afterEach, describe, expect, it, vi } from "vitest";

import { loadRuntimeState, runtimeApiErrorMessage } from "../src/app/api";

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
