import { decodeStateSnapshot } from "../core/decoder";
import {
  GeneratedScenarioConfig,
  RuntimeStatusEnvelope,
  RuntimeStatusPayload,
  ScenarioConfig,
  StateSnapshot
} from "../core/event_types";

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
  return (await loadRuntimeState(endpoint)).status;
}

export async function loadRuntimeState(endpoint = "/runtime/status"): Promise<RuntimeStatusEnvelope> {
  const response = await fetch(endpoint);
  if (!response.ok) {
    throw new Error(`failed to load runtime status: ${response.status}`);
  }
  return decodeRuntimeStatusEnvelope(await response.json());
}

function decodeScenarioConfig(value: unknown): ScenarioConfig {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new TypeError("scenario config must be an object");
  }
  return value as ScenarioConfig;
}

function decodeRuntimeStatusEnvelope(value: unknown): RuntimeStatusEnvelope {
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
