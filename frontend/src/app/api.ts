import { decodeStateSnapshot } from "../core/decoder";
import { RuntimeStatusPayload, ScenarioConfig, StateSnapshot } from "../core/event_types";

export async function loadScenarioConfig(endpoint = "/scenario/config"): Promise<ScenarioConfig> {
  const response = await fetch(endpoint);
  if (!response.ok) {
    throw new Error(`failed to load scenario config: ${response.status}`);
  }
  return decodeScenarioConfig(await response.json());
}

export async function loadMetricsSnapshot(endpoint = "/metrics/snapshot"): Promise<StateSnapshot> {
  const response = await fetch(endpoint);
  if (!response.ok) {
    throw new Error(`failed to load metrics snapshot: ${response.status}`);
  }
  return decodeStateSnapshot(await response.json());
}

export async function loadRuntimeStatus(endpoint = "/runtime/status"): Promise<RuntimeStatusPayload> {
  const response = await fetch(endpoint);
  if (!response.ok) {
    throw new Error(`failed to load runtime status: ${response.status}`);
  }
  return decodeRuntimeStatus(await response.json());
}

function decodeScenarioConfig(value: unknown): ScenarioConfig {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new TypeError("scenario config must be an object");
  }
  return value as ScenarioConfig;
}

function decodeRuntimeStatus(value: unknown): RuntimeStatusPayload {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new TypeError("runtime status must be an object");
  }
  const status = (value as { status?: unknown }).status;
  if (typeof status !== "object" || status === null || Array.isArray(status)) {
    throw new TypeError("runtime status response must include status object");
  }
  return status as RuntimeStatusPayload;
}
