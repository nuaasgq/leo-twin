import { decodeStateSnapshot } from "../core/decoder";
import {
  GeneratedScenarioConfig,
  RuntimeDetailPageEnvelope,
  RuntimeExportCatalogEnvelope,
  RuntimeExportCatalogV1,
  RuntimeExportHistoryEnvelope,
  RuntimeExportHistoryV1,
  RuntimeExportPackageCompareEnvelope,
  RuntimeExportPackageCompareV1,
  RuntimeExportRestorePreflightEnvelope,
  RuntimeExportRestorePreflightV1,
  RuntimeNodeDetailPageV1,
  RuntimeSatelliteServiceSummaryV1,
  RuntimeStatusEnvelope,
  RuntimeStatusPayload,
  RuntimeUserRequestSummaryV1,
  ScenarioConfig,
  StateSnapshot,
  UserConfigurationExportEnvelope,
  UserConfigurationExportV1,
  UserConfigurationSchemaEnvelope,
  UserConfigurationSchemaV2,
  UserConfigurationTemplateCatalogEnvelope,
  UserConfigurationTemplateCatalogV1,
  UserConfigurationValidationReportEnvelope,
  UserConfigurationValidationReportV1
} from "../core/event_types";

export const DEFAULT_RUNTIME_EXPORT_ARCHIVE_ENDPOINT = "/runtime/export/archive";
export const DEFAULT_RUNTIME_EXPORT_PACKAGES_ENDPOINT = "/runtime/export/packages";
export const DEFAULT_USER_CONFIG_SCHEMA_ENDPOINT = "/scenario/user-config/schema";
export const DEFAULT_USER_CONFIG_TEMPLATES_ENDPOINT = "/scenario/user-config/templates";
export const DEFAULT_USER_CONFIG_EXPORT_ENDPOINT = "/scenario/user-config/export";
export const DEFAULT_USER_CONFIG_VALIDATE_ENDPOINT = "/scenario/user-config/validate";

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

export async function loadRuntimeExportHistory(
  endpoint = "/runtime/export/history"
): Promise<RuntimeExportHistoryV1> {
  const response = await fetch(endpoint);
  if (!response.ok) {
    throw new Error(`failed to load runtime export history from ${endpoint}: HTTP ${response.status}`);
  }
  return decodeRuntimeExportHistory(await response.json()).summary;
}

export async function loadRuntimeExportCatalog(
  endpoint = "/runtime/export/catalog"
): Promise<RuntimeExportCatalogV1> {
  const response = await fetch(endpoint);
  if (!response.ok) {
    throw new Error(`failed to load runtime export catalog from ${endpoint}: HTTP ${response.status}`);
  }
  return decodeRuntimeExportCatalog(await response.json()).summary;
}

export async function loadRuntimeExportPackageCompare(
  packageId: string,
  endpoint = DEFAULT_RUNTIME_EXPORT_PACKAGES_ENDPOINT
): Promise<RuntimeExportPackageCompareV1> {
  const url = runtimeExportPackageCompareHref(packageId, endpoint);
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`failed to load runtime export package compare from ${url}: HTTP ${response.status}`);
  }
  return decodeRuntimeExportPackageCompare(await response.json()).summary;
}

export async function loadRuntimeExportRestorePreflight(
  packageId: string,
  endpoint = DEFAULT_RUNTIME_EXPORT_PACKAGES_ENDPOINT
): Promise<RuntimeExportRestorePreflightV1> {
  const url = runtimeExportRestorePreflightHref(packageId, endpoint);
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`failed to load runtime export restore preflight from ${url}: HTTP ${response.status}`);
  }
  return decodeRuntimeExportRestorePreflight(await response.json()).summary;
}

export async function loadUserConfigurationSchema(
  endpoint = DEFAULT_USER_CONFIG_SCHEMA_ENDPOINT
): Promise<UserConfigurationSchemaV2> {
  const response = await fetch(endpoint);
  if (!response.ok) {
    throw new Error(`failed to load user configuration schema from ${endpoint}: HTTP ${response.status}`);
  }
  return decodeUserConfigurationSchema(await response.json()).summary;
}

export async function loadUserConfigurationTemplates(
  endpoint = DEFAULT_USER_CONFIG_TEMPLATES_ENDPOINT
): Promise<UserConfigurationTemplateCatalogV1> {
  const response = await fetch(endpoint);
  if (!response.ok) {
    throw new Error(`failed to load user configuration templates from ${endpoint}: HTTP ${response.status}`);
  }
  return decodeUserConfigurationTemplates(await response.json()).summary;
}

export async function loadUserConfigurationExport(
  endpoint = DEFAULT_USER_CONFIG_EXPORT_ENDPOINT
): Promise<UserConfigurationExportV1> {
  const response = await fetch(endpoint);
  if (!response.ok) {
    throw new Error(`failed to load user configuration export from ${endpoint}: HTTP ${response.status}`);
  }
  return decodeUserConfigurationExport(await response.json()).summary;
}

export async function validateUserConfigurationCandidate(
  candidate: unknown,
  endpoint = DEFAULT_USER_CONFIG_VALIDATE_ENDPOINT
): Promise<UserConfigurationValidationReportV1> {
  const response = await fetch(endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(candidate)
  });
  if (!response.ok) {
    throw new Error(`failed to validate user configuration from ${endpoint}: HTTP ${response.status}`);
  }
  return decodeUserConfigurationValidationReport(await response.json()).summary;
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

export function runtimeExportArchiveHref(
  endpoint = DEFAULT_RUNTIME_EXPORT_ARCHIVE_ENDPOINT
): string {
  return endpoint;
}

export function runtimeExportPackageRecordHref(
  packageId: string,
  endpoint = DEFAULT_RUNTIME_EXPORT_PACKAGES_ENDPOINT
): string {
  return `${endpoint}/${encodeURIComponent(packageId)}`;
}

export function runtimeExportPackageManifestHref(
  packageId: string,
  endpoint = DEFAULT_RUNTIME_EXPORT_PACKAGES_ENDPOINT
): string {
  return `${runtimeExportPackageRecordHref(packageId, endpoint)}/manifest`;
}

export function runtimeExportPackageArchiveHref(
  packageId: string,
  endpoint = DEFAULT_RUNTIME_EXPORT_PACKAGES_ENDPOINT
): string {
  return `${runtimeExportPackageRecordHref(packageId, endpoint)}/archive`;
}

export function runtimeExportPackageCompareHref(
  packageId: string,
  endpoint = DEFAULT_RUNTIME_EXPORT_PACKAGES_ENDPOINT
): string {
  return `${runtimeExportPackageRecordHref(packageId, endpoint)}/compare`;
}

export function runtimeExportRestorePreflightHref(
  packageId: string,
  endpoint = DEFAULT_RUNTIME_EXPORT_PACKAGES_ENDPOINT
): string {
  return `${runtimeExportPackageRecordHref(packageId, endpoint)}/restore-preflight`;
}

export function runtimeExportPackageFileHref(
  packageId: string,
  filename: string,
  endpoint = DEFAULT_RUNTIME_EXPORT_PACKAGES_ENDPOINT
): string {
  return `${runtimeExportPackageRecordHref(packageId, endpoint)}/files/${encodeURIComponent(
    filename
  )}`;
}

export function userConfigurationSchemaHref(
  endpoint = DEFAULT_USER_CONFIG_SCHEMA_ENDPOINT
): string {
  return endpoint;
}

export function userConfigurationTemplatesHref(
  endpoint = DEFAULT_USER_CONFIG_TEMPLATES_ENDPOINT
): string {
  return endpoint;
}

export function userConfigurationExportHref(
  endpoint = DEFAULT_USER_CONFIG_EXPORT_ENDPOINT
): string {
  return endpoint;
}

export function userConfigurationValidateHref(
  endpoint = DEFAULT_USER_CONFIG_VALIDATE_ENDPOINT
): string {
  return endpoint;
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

export function decodeRuntimeExportHistory(value: unknown): RuntimeExportHistoryEnvelope {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new TypeError("runtime export history response must be an object");
  }
  const summary = (value as { summary?: unknown }).summary;
  if (typeof summary !== "object" || summary === null || Array.isArray(summary)) {
    throw new TypeError("runtime export history response must include summary object");
  }
  return {
    ...(value as Record<string, unknown>),
    summary: summary as RuntimeExportHistoryV1
  } as RuntimeExportHistoryEnvelope;
}

export function decodeRuntimeExportCatalog(value: unknown): RuntimeExportCatalogEnvelope {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new TypeError("runtime export catalog response must be an object");
  }
  const summary = (value as { summary?: unknown }).summary;
  if (typeof summary !== "object" || summary === null || Array.isArray(summary)) {
    throw new TypeError("runtime export catalog response must include summary object");
  }
  return {
    ...(value as Record<string, unknown>),
    summary: summary as RuntimeExportCatalogV1
  } as RuntimeExportCatalogEnvelope;
}

export function decodeRuntimeExportPackageCompare(
  value: unknown
): RuntimeExportPackageCompareEnvelope {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new TypeError("runtime export package compare response must be an object");
  }
  const summary = (value as { summary?: unknown }).summary;
  if (typeof summary !== "object" || summary === null || Array.isArray(summary)) {
    throw new TypeError("runtime export package compare response must include summary object");
  }
  return {
    ...(value as Record<string, unknown>),
    summary: summary as RuntimeExportPackageCompareV1
  } as RuntimeExportPackageCompareEnvelope;
}

export function decodeRuntimeExportRestorePreflight(
  value: unknown
): RuntimeExportRestorePreflightEnvelope {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new TypeError("runtime export restore preflight response must be an object");
  }
  const summary = (value as { summary?: unknown }).summary;
  if (typeof summary !== "object" || summary === null || Array.isArray(summary)) {
    throw new TypeError("runtime export restore preflight response must include summary object");
  }
  return {
    ...(value as Record<string, unknown>),
    summary: summary as RuntimeExportRestorePreflightV1
  } as RuntimeExportRestorePreflightEnvelope;
}

export function decodeUserConfigurationSchema(value: unknown): UserConfigurationSchemaEnvelope {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new TypeError("user configuration schema response must be an object");
  }
  const summary = (value as { summary?: unknown }).summary;
  if (typeof summary !== "object" || summary === null || Array.isArray(summary)) {
    throw new TypeError("user configuration schema response must include summary object");
  }
  return {
    ...(value as Record<string, unknown>),
    summary: summary as UserConfigurationSchemaV2
  } as UserConfigurationSchemaEnvelope;
}

export function decodeUserConfigurationTemplates(
  value: unknown
): UserConfigurationTemplateCatalogEnvelope {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new TypeError("user configuration template catalog response must be an object");
  }
  const summary = (value as { summary?: unknown }).summary;
  if (typeof summary !== "object" || summary === null || Array.isArray(summary)) {
    throw new TypeError("user configuration template catalog response must include summary object");
  }
  return {
    ...(value as Record<string, unknown>),
    summary: summary as UserConfigurationTemplateCatalogV1
  } as UserConfigurationTemplateCatalogEnvelope;
}

export function decodeUserConfigurationExport(value: unknown): UserConfigurationExportEnvelope {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new TypeError("user configuration export response must be an object");
  }
  const summary = (value as { summary?: unknown }).summary;
  if (typeof summary !== "object" || summary === null || Array.isArray(summary)) {
    throw new TypeError("user configuration export response must include summary object");
  }
  return {
    ...(value as Record<string, unknown>),
    summary: summary as UserConfigurationExportV1
  } as UserConfigurationExportEnvelope;
}

export function decodeUserConfigurationValidationReport(
  value: unknown
): UserConfigurationValidationReportEnvelope {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new TypeError("user configuration validation response must be an object");
  }
  const summary = (value as { summary?: unknown }).summary;
  if (typeof summary !== "object" || summary === null || Array.isArray(summary)) {
    throw new TypeError("user configuration validation response must include summary object");
  }
  return {
    ...(value as Record<string, unknown>),
    summary: summary as UserConfigurationValidationReportV1
  } as UserConfigurationValidationReportEnvelope;
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
