import { decodeStateSnapshot } from "../core/decoder";
import {
  GeneratedScenarioConfig,
  RuntimeDetailPageEnvelope,
  RuntimeNodeDetailPageV1,
  RuntimeSatelliteServiceSummaryV1,
  RuntimeStatusEnvelope,
  RuntimeStatusPayload,
  RuntimeUserRequestSummaryV1,
  ScenarioConfig,
  StateSnapshot
} from "../core/event_types";

export async function loadScenarioConfig(endpoint = "/scenario/config"): Promise<ScenarioConfig> {
  const response = await fetch(endpoint);
  if (!response.ok) {
    throw new Error(`failed to load scenario config from ${endpoint}: HTTP ${response.status}`);
  }
  return decodeScenarioConfig(await response.json());
}

export async function loadMetricsSnapshot(endpoint = "/metrics/snapshot"): Promise<StateSnapshot> {
  const response = await fetch(endpoint);
  if (!response.ok) {
    throw new Error(`failed to load metrics snapshot from ${endpoint}: HTTP ${response.status}`);
  }
  return decodeStateSnapshot(await response.json());
}

export async function loadRuntimeStatus(endpoint = "/runtime/status"): Promise<RuntimeStatusPayload> {
  return (await loadRuntimeState(endpoint)).status;
}

export async function loadRuntimeState(endpoint = "/runtime/status"): Promise<RuntimeStatusEnvelope> {
  const response = await fetch(endpoint);
  if (!response.ok) {
    throw new Error(`failed to load runtime status from ${endpoint}: HTTP ${response.status}`);
  }
  return decodeRuntimeStatusEnvelope(await response.json());
}

export async function loadRuntimeUserDetails(
  cursor = 0,
  limit = 100,
  endpoint = "/runtime/details/users"
): Promise<RuntimeUserRequestSummaryV1> {
  const page = await loadRuntimeDetailPage(endpoint, cursor, limit);
  if (page.kind !== "users") {
    throw new TypeError(`runtime detail response kind must be users, got ${page.kind}`);
  }
  return page.summary as RuntimeUserRequestSummaryV1;
}

export async function loadRuntimeSatelliteDetails(
  cursor = 0,
  limit = 120,
  endpoint = "/runtime/details/satellites"
): Promise<RuntimeSatelliteServiceSummaryV1> {
  const page = await loadRuntimeDetailPage(endpoint, cursor, limit);
  if (page.kind !== "satellites") {
    throw new TypeError(`runtime detail response kind must be satellites, got ${page.kind}`);
  }
  return page.summary as RuntimeSatelliteServiceSummaryV1;
}

export async function loadRuntimeNodeDetails(
  cursor = 0,
  limit = 100,
  endpoint = "/runtime/details/nodes"
): Promise<RuntimeNodeDetailPageV1> {
  const page = await loadRuntimeDetailPage(endpoint, cursor, limit);
  if (page.kind !== "nodes") {
    throw new TypeError(`runtime detail response kind must be nodes, got ${page.kind}`);
  }
  return page.summary as RuntimeNodeDetailPageV1;
}

export function runtimeApiErrorMessage(error: unknown): string {
  const message = error instanceof Error ? error.message : String(error);
  if (
    message.includes("Failed to fetch") ||
    message.includes("NetworkError") ||
    message.includes("Load failed")
  ) {
    return [
      "无法连接后端服务。",
      "请运行 start_leo_twin.bat，或执行 scripts\\sees_launcher.ps1 status 检查 ",
      "http://127.0.0.1:8765/runtime/status。"
    ].join("");
  }
  if (message.includes("failed to load")) {
    return `后端接口返回错误：${message}`;
  }
  if (message.includes("must be an object") || message.includes("must include")) {
    return `后端接口格式不符合前端契约：${message}`;
  }
  return `运行状态刷新失败：${message}`;
}

function decodeScenarioConfig(value: unknown): ScenarioConfig {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new TypeError("scenario config must be an object");
  }
  return value as ScenarioConfig;
}

async function loadRuntimeDetailPage(
  endpoint: string,
  cursor: number,
  limit: number
): Promise<RuntimeDetailPageEnvelope> {
  const url = `${endpoint}?cursor=${encodeURIComponent(String(cursor))}&limit=${encodeURIComponent(
    String(limit)
  )}`;
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`failed to load runtime details from ${url}: HTTP ${response.status}`);
  }
  return decodeRuntimeDetailPage(await response.json());
}

export function decodeRuntimeDetailPage(value: unknown): RuntimeDetailPageEnvelope {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new TypeError("runtime detail response must be an object");
  }
  const kind = (value as { kind?: unknown }).kind;
  const summary = (value as { summary?: unknown }).summary;
  if (kind !== "users" && kind !== "satellites" && kind !== "nodes") {
    throw new TypeError("runtime detail response kind must be users, satellites, or nodes");
  }
  if (typeof summary !== "object" || summary === null || Array.isArray(summary)) {
    throw new TypeError("runtime detail response must include summary object");
  }
  return {
    ...(value as Record<string, unknown>),
    kind,
    summary: summary as
      | RuntimeUserRequestSummaryV1
      | RuntimeSatelliteServiceSummaryV1
      | RuntimeNodeDetailPageV1
  } as RuntimeDetailPageEnvelope;
}

export function decodeRuntimeStatusEnvelope(value: unknown): RuntimeStatusEnvelope {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new TypeError("runtime status must be an object");
  }
  const status = (value as { status?: unknown }).status;
  if (typeof status !== "object" || status === null || Array.isArray(status)) {
    throw new TypeError("runtime status response must include status object");
  }
  return {
    ...(value as Record<string, unknown>),
    status: status as RuntimeStatusPayload,
    generated_config: decodeGeneratedScenarioConfig(
      (value as { generated_config?: unknown }).generated_config
    )
  };
}

function decodeGeneratedScenarioConfig(value: unknown): GeneratedScenarioConfig | undefined {
  if (value === undefined) {
    return undefined;
  }
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new TypeError("generated scenario config must be an object");
  }
  return value as GeneratedScenarioConfig;
}
