import { decodeStateSnapshot } from "../core/decoder";
import { ScenarioConfig, StateSnapshot } from "../core/event_types";

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

function decodeScenarioConfig(value: unknown): ScenarioConfig {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new TypeError("scenario config must be an object");
  }
  return value as ScenarioConfig;
}
