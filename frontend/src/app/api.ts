import { decodeStateSnapshot } from "../core/decoder";
import {
  GeneratedScenarioConfig,
  RuntimeDetailPageEnvelope,
  RuntimeComputeNodeDetailPageV1,
  RuntimeExportCatalogEnvelope,
  RuntimeExportCatalogV1,
  RuntimeExportDiagnosticsBundleV1,
  RuntimeExportHistoryEnvelope,
  RuntimeExportHistoryV1,
  RuntimeExportPackageCompareEnvelope,
  RuntimeExportPackageCompareV1,
  RuntimeExportPackageAuditIndexV1,
  RuntimeExportPackageReviewCompletionEnvelope,
  RuntimeExportPackageReviewCompletionV1,
  RuntimeExportScenarioReviewBundleV1,
  RuntimeExportScenarioReviewChecklistEnvelope,
  RuntimeExportScenarioReviewChecklistRecordV1,
  RuntimeExportScenarioReviewChecklistV1,
  RuntimeExportRouteComparisonReviewReportEnvelope,
  RuntimeExportRouteComparisonReviewReportRecordV1,
  RuntimeExportRouteComparisonReviewReportV1,
  RuntimeExportRouteDetailIndexV1,
  RuntimeExportRouteDetailItemV1,
  RuntimeExportRouteDetailPageV1,
  RuntimeExportServiceTracePageV1,
  RuntimeExportReviewSummaryV1,
  RuntimeExportRestorePreflightEnvelope,
  RuntimeExportRestorePreflightV1,
  RuntimeReproducibilityManifestV1,
  RuntimeEntityDetailEnvelopeV1,
  RuntimeNodeDetailCardV1,
  RuntimeNodeDetailPageV1,
  RuntimeComputeNodeDetailItemV1,
  RuntimeRouteExplanationSummaryV1,
  RuntimeRouteExplanationItemV1,
  RuntimeSatelliteServiceSummaryV1,
  RuntimeServiceDetailItemV1,
  RuntimeServiceDetailPageV1,
  RuntimeServiceLifecycleTraceV2,
  RuntimeServiceTraceDetailV2,
  RuntimeStatusEnvelope,
  RuntimeStatusPayload,
  RuntimeUserRequestSummaryV1,
  RuntimeUserServiceRequestSummaryV2,
  ScenarioConfig,
  StateSnapshot,
  UserConfigurationExportEnvelope,
  UserConfigurationExportV1,
  UserConfigurationReferenceEnvelope,
  UserConfigurationReferenceV1,
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
export const DEFAULT_USER_CONFIG_REFERENCE_ENDPOINT = "/scenario/user-config/reference";
export const DEFAULT_USER_CONFIG_EXPORT_ENDPOINT = "/scenario/user-config/export";
export const DEFAULT_USER_CONFIG_VALIDATE_ENDPOINT = "/scenario/user-config/validate";
export const DEFAULT_USER_CONFIG_VALIDATE_TEXT_ENDPOINT =
  "/scenario/user-config/validate-text";

export interface RuntimeDetailQueryFilters {
  query?: string;
  summaryVersion?: string;
  availability?: string;
  businessType?: string;
  bottleneckComponent?: string;
  terminalState?: string;
  computeNodeId?: string;
  stageKind?: string;
  terminalReason?: string;
}

export interface RuntimeExportRouteComparisonReviewReportRequest {
  records: readonly Partial<RuntimeExportRouteComparisonReviewReportRecordV1>[];
}

export interface RuntimeExportScenarioReviewChecklistRequest {
  records: readonly Partial<RuntimeExportScenarioReviewChecklistRecordV1>[];
}

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
  endpoint = "/runtime/details/users",
  filters: RuntimeDetailQueryFilters = {}
): Promise<RuntimeUserRequestSummaryV1 | RuntimeUserServiceRequestSummaryV2> {
  const page = await loadRuntimeDetailPage(endpoint, cursor, limit, {
    summaryVersion: "v2",
    ...filters
  });
  if (page.kind !== "users") {
    throw new TypeError(`runtime detail response kind must be users, got ${page.kind}`);
  }
  return page.summary as RuntimeUserRequestSummaryV1 | RuntimeUserServiceRequestSummaryV2;
}

export async function loadRuntimeSatelliteDetails(
  cursor = 0,
  limit = 120,
  endpoint = "/runtime/details/satellites",
  filters: RuntimeDetailQueryFilters = {}
): Promise<RuntimeSatelliteServiceSummaryV1> {
  const page = await loadRuntimeDetailPage(endpoint, cursor, limit, filters);
  if (page.kind !== "satellites") {
    throw new TypeError(`runtime detail response kind must be satellites, got ${page.kind}`);
  }
  return page.summary as RuntimeSatelliteServiceSummaryV1;
}

export async function loadRuntimeUserDetail(
  userId: string,
  endpoint = "/runtime/details/users"
): Promise<RuntimeNodeDetailCardV1> {
  const detail = await loadRuntimeEntityDetail(runtimeDetailEntityHref(userId, endpoint));
  if (detail.kind !== "user") {
    throw new TypeError(`runtime entity detail kind must be user, got ${detail.kind}`);
  }
  return detail.summary as RuntimeNodeDetailCardV1;
}

export async function loadRuntimeSatelliteDetail(
  satelliteId: string,
  endpoint = "/runtime/details/satellites"
): Promise<RuntimeNodeDetailCardV1> {
  const detail = await loadRuntimeEntityDetail(
    runtimeDetailEntityHref(satelliteId, endpoint)
  );
  if (detail.kind !== "satellite") {
    throw new TypeError(
      `runtime entity detail kind must be satellite, got ${detail.kind}`
    );
  }
  return detail.summary as RuntimeNodeDetailCardV1;
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

export async function loadRuntimeRouteDetails(
  cursor = 0,
  limit = 100,
  endpoint = "/runtime/details/routes",
  filters: RuntimeDetailQueryFilters = {}
): Promise<RuntimeRouteExplanationSummaryV1> {
  const page = await loadRuntimeDetailPage(endpoint, cursor, limit, filters);
  if (page.kind !== "routes") {
    throw new TypeError(`runtime detail response kind must be routes, got ${page.kind}`);
  }
  return page.summary as RuntimeRouteExplanationSummaryV1;
}

export async function loadRuntimeRouteDetail(
  routeId: string,
  endpoint = "/runtime/details/routes"
): Promise<RuntimeRouteExplanationItemV1> {
  const detail = await loadRuntimeEntityDetail(runtimeDetailEntityHref(routeId, endpoint));
  if (detail.kind !== "route") {
    throw new TypeError(`runtime entity detail kind must be route, got ${detail.kind}`);
  }
  return detail.summary as RuntimeRouteExplanationItemV1;
}

export async function loadRuntimeServiceDetails(
  cursor = 0,
  limit = 100,
  endpoint = "/runtime/details/services",
  filters: RuntimeDetailQueryFilters = {}
): Promise<RuntimeServiceDetailPageV1> {
  const page = await loadRuntimeDetailPage(endpoint, cursor, limit, filters);
  if (page.kind !== "services") {
    throw new TypeError(`runtime detail response kind must be services, got ${page.kind}`);
  }
  return page.summary as RuntimeServiceDetailPageV1;
}

export async function loadRuntimeServiceTraceDetails(
  cursor = 0,
  limit = 100,
  endpoint = "/runtime/details/service-traces",
  filters: RuntimeDetailQueryFilters = {}
): Promise<RuntimeServiceLifecycleTraceV2> {
  const page = await loadRuntimeDetailPage(endpoint, cursor, limit, filters);
  if (page.kind !== "service_traces") {
    throw new TypeError(
      `runtime detail response kind must be service_traces, got ${page.kind}`
    );
  }
  return page.summary as RuntimeServiceLifecycleTraceV2;
}

export async function loadRuntimeServiceDetail(
  serviceId: string,
  endpoint = "/runtime/details/services"
): Promise<RuntimeServiceDetailItemV1> {
  const detail = await loadRuntimeEntityDetail(runtimeDetailEntityHref(serviceId, endpoint));
  if (detail.kind !== "service") {
    throw new TypeError(`runtime entity detail kind must be service, got ${detail.kind}`);
  }
  return detail.summary as RuntimeServiceDetailItemV1;
}

export async function loadRuntimeServiceTraceDetail(
  traceId: string,
  endpoint = "/runtime/details/service-traces"
): Promise<RuntimeServiceTraceDetailV2> {
  const detail = await loadRuntimeEntityDetail(runtimeDetailEntityHref(traceId, endpoint));
  if (detail.kind !== "service_trace") {
    throw new TypeError(
      `runtime entity detail kind must be service_trace, got ${detail.kind}`
    );
  }
  return detail.summary as RuntimeServiceTraceDetailV2;
}

export async function loadRuntimeComputeNodeDetails(
  cursor = 0,
  limit = 100,
  endpoint = "/runtime/details/compute-nodes",
  filters: RuntimeDetailQueryFilters = {}
): Promise<RuntimeComputeNodeDetailPageV1> {
  const page = await loadRuntimeDetailPage(endpoint, cursor, limit, filters);
  if (page.kind !== "compute_nodes") {
    throw new TypeError(
      `runtime detail response kind must be compute_nodes, got ${page.kind}`
    );
  }
  return page.summary as RuntimeComputeNodeDetailPageV1;
}

export async function loadRuntimeComputeNodeDetail(
  nodeId: string,
  endpoint = "/runtime/details/compute-nodes"
): Promise<RuntimeComputeNodeDetailItemV1> {
  const detail = await loadRuntimeEntityDetail(runtimeDetailEntityHref(nodeId, endpoint));
  if (detail.kind !== "compute_node") {
    throw new TypeError(
      `runtime entity detail kind must be compute_node, got ${detail.kind}`
    );
  }
  return detail.summary as RuntimeComputeNodeDetailItemV1;
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

export async function loadRuntimeExportReviewSummary(
  packageId: string,
  endpoint = DEFAULT_RUNTIME_EXPORT_PACKAGES_ENDPOINT
): Promise<RuntimeExportReviewSummaryV1> {
  const url = runtimeExportPackageReviewSummaryHref(packageId, endpoint);
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`failed to load runtime export review summary from ${url}: HTTP ${response.status}`);
  }
  return decodeRuntimeExportReviewSummary(await response.json());
}

export async function loadRuntimeExportManifest(
  packageId: string,
  endpoint = DEFAULT_RUNTIME_EXPORT_PACKAGES_ENDPOINT
): Promise<RuntimeReproducibilityManifestV1> {
  const url = runtimeExportPackageManifestHref(packageId, endpoint);
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`failed to load runtime export manifest from ${url}: HTTP ${response.status}`);
  }
  return decodeRuntimeExportManifest(await response.json());
}

export async function loadRuntimeExportDiagnosticsBundle(
  packageId: string,
  endpoint = DEFAULT_RUNTIME_EXPORT_PACKAGES_ENDPOINT
): Promise<RuntimeExportDiagnosticsBundleV1> {
  const url = runtimeExportPackageFileHref(
    packageId,
    "diagnostics_bundle_v1.json",
    endpoint
  );
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`failed to load runtime export diagnostics bundle from ${url}: HTTP ${response.status}`);
  }
  return decodeRuntimeExportDiagnosticsBundle(await response.json());
}

export async function loadRuntimeExportServiceLifecycleTrace(
  packageId: string,
  endpoint = DEFAULT_RUNTIME_EXPORT_PACKAGES_ENDPOINT
): Promise<RuntimeServiceLifecycleTraceV2> {
  const url = runtimeExportPackageFileHref(
    packageId,
    "service_lifecycle_trace_v2.json",
    endpoint
  );
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`failed to load runtime export service lifecycle trace from ${url}: HTTP ${response.status}`);
  }
  return decodeRuntimeServiceLifecycleTrace(await response.json());
}

export async function loadRuntimeExportServiceTracePage(
  packageId: string,
  cursor = 0,
  limit = 100,
  filters: RuntimeDetailQueryFilters = {},
  endpoint = DEFAULT_RUNTIME_EXPORT_PACKAGES_ENDPOINT
): Promise<RuntimeExportServiceTracePageV1> {
  const url = runtimeExportPackageServiceTracesHref(
    packageId,
    cursor,
    limit,
    filters,
    endpoint
  );
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`failed to load runtime export service trace page from ${url}: HTTP ${response.status}`);
  }
  return decodeRuntimeExportServiceTracePage(await response.json());
}

export async function loadRuntimeExportRouteDetailIndex(
  packageId: string,
  endpoint = DEFAULT_RUNTIME_EXPORT_PACKAGES_ENDPOINT
): Promise<RuntimeExportRouteDetailIndexV1> {
  const url = runtimeExportPackageFileHref(
    packageId,
    "route_detail_index_v1.json",
    endpoint
  );
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`failed to load runtime export route detail index from ${url}: HTTP ${response.status}`);
  }
  return decodeRuntimeExportRouteDetailIndex(await response.json());
}

export async function loadRuntimeExportRouteDetailPage(
  packageId: string,
  cursor = 0,
  limit = 100,
  filters: RuntimeDetailQueryFilters = {},
  endpoint = DEFAULT_RUNTIME_EXPORT_PACKAGES_ENDPOINT
): Promise<RuntimeExportRouteDetailPageV1> {
  const url = runtimeExportPackageRouteDetailsHref(
    packageId,
    cursor,
    limit,
    filters,
    endpoint
  );
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`failed to load runtime export route detail page from ${url}: HTTP ${response.status}`);
  }
  return decodeRuntimeExportRouteDetailPage(await response.json());
}

export async function loadRuntimeExportRouteDetailItem(
  packageId: string,
  routeId: string,
  endpoint = DEFAULT_RUNTIME_EXPORT_PACKAGES_ENDPOINT
): Promise<RuntimeExportRouteDetailItemV1> {
  const url = runtimeExportPackageRouteDetailHref(packageId, routeId, endpoint);
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`failed to load runtime export route detail item from ${url}: HTTP ${response.status}`);
  }
  return decodeRuntimeExportRouteDetailItem(await response.json());
}

export async function loadRuntimeExportRouteComparisonReviewReport(
  packageId: string,
  endpoint = DEFAULT_RUNTIME_EXPORT_PACKAGES_ENDPOINT
): Promise<RuntimeExportRouteComparisonReviewReportV1> {
  const url = runtimeExportPackageFileHref(
    packageId,
    "route_comparison_review_report_v1.json",
    endpoint
  );
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`failed to load runtime export route comparison review report from ${url}: HTTP ${response.status}`);
  }
  return decodeRuntimeExportRouteComparisonReviewReportArtifact(await response.json());
}

export async function loadRuntimeExportPackageAuditIndex(
  packageId: string,
  endpoint = DEFAULT_RUNTIME_EXPORT_PACKAGES_ENDPOINT
): Promise<RuntimeExportPackageAuditIndexV1> {
  const url = runtimeExportPackageFileHref(
    packageId,
    "export_package_audit_index_v1.json",
    endpoint
  );
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`failed to load runtime export package audit index from ${url}: HTTP ${response.status}`);
  }
  return decodeRuntimeExportPackageAuditIndex(await response.json());
}

export async function loadRuntimeExportPackageReviewCompletion(
  packageId: string,
  endpoint = DEFAULT_RUNTIME_EXPORT_PACKAGES_ENDPOINT
): Promise<RuntimeExportPackageReviewCompletionV1> {
  const url = runtimeExportPackageReviewCompletionHref(packageId, endpoint);
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`failed to load runtime export package review completion from ${url}: HTTP ${response.status}`);
  }
  return decodeRuntimeExportPackageReviewCompletionEnvelope(await response.json()).summary;
}

export async function loadRuntimeExportPackageHandoffReport(
  packageId: string,
  endpoint = DEFAULT_RUNTIME_EXPORT_PACKAGES_ENDPOINT
): Promise<string> {
  const url = runtimeExportPackageHandoffReportHref(packageId, endpoint);
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`failed to load runtime export package handoff report from ${url}: HTTP ${response.status}`);
  }
  return response.text();
}

export async function loadRuntimeExportScenarioReviewBundle(
  packageId: string,
  endpoint = DEFAULT_RUNTIME_EXPORT_PACKAGES_ENDPOINT
): Promise<RuntimeExportScenarioReviewBundleV1> {
  const url = runtimeExportPackageFileHref(
    packageId,
    "scenario_review_bundle_v1.json",
    endpoint
  );
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`failed to load runtime export scenario review bundle from ${url}: HTTP ${response.status}`);
  }
  return decodeRuntimeExportScenarioReviewBundle(await response.json());
}

export async function loadRuntimeExportScenarioReviewChecklist(
  packageId: string,
  endpoint = DEFAULT_RUNTIME_EXPORT_PACKAGES_ENDPOINT
): Promise<RuntimeExportScenarioReviewChecklistV1> {
  const url = runtimeExportPackageFileHref(
    packageId,
    "scenario_review_checklist_v1.json",
    endpoint
  );
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`failed to load runtime export scenario review checklist from ${url}: HTTP ${response.status}`);
  }
  return decodeRuntimeExportScenarioReviewChecklist(await response.json());
}

export async function saveRuntimeExportRouteComparisonReviewReport(
  packageId: string,
  request: RuntimeExportRouteComparisonReviewReportRequest,
  endpoint = DEFAULT_RUNTIME_EXPORT_PACKAGES_ENDPOINT
): Promise<RuntimeExportRouteComparisonReviewReportV1> {
  const url = runtimeExportRouteComparisonReviewReportHref(packageId, endpoint);
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(request)
  });
  if (!response.ok) {
    throw new Error(`failed to save runtime export route comparison review report to ${url}: HTTP ${response.status}`);
  }
  return decodeRuntimeExportRouteComparisonReviewReport(await response.json()).summary;
}

export async function saveRuntimeExportScenarioReviewChecklist(
  packageId: string,
  request: RuntimeExportScenarioReviewChecklistRequest,
  endpoint = DEFAULT_RUNTIME_EXPORT_PACKAGES_ENDPOINT
): Promise<RuntimeExportScenarioReviewChecklistV1> {
  const url = runtimeExportScenarioReviewChecklistHref(packageId, endpoint);
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(request)
  });
  if (!response.ok) {
    throw new Error(`failed to save runtime export scenario review checklist to ${url}: HTTP ${response.status}`);
  }
  return decodeRuntimeExportScenarioReviewChecklistResponse(await response.json()).summary;
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

export async function loadUserConfigurationReference(
  endpoint = DEFAULT_USER_CONFIG_REFERENCE_ENDPOINT
): Promise<UserConfigurationReferenceV1> {
  const response = await fetch(endpoint);
  if (!response.ok) {
    throw new Error(`failed to load user configuration reference from ${endpoint}: HTTP ${response.status}`);
  }
  return decodeUserConfigurationReference(await response.json()).summary;
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

export async function validateUserConfigurationTextCandidate(
  text: string,
  format: "auto" | "json" | "yaml" = "auto",
  endpoint = DEFAULT_USER_CONFIG_VALIDATE_TEXT_ENDPOINT
): Promise<UserConfigurationValidationReportV1> {
  const url = userConfigurationValidateTextHref(format, endpoint);
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "text/plain; charset=utf-8"
    },
    body: text
  });
  if (!response.ok) {
    throw new Error(`failed to validate user configuration text from ${url}: HTTP ${response.status}`);
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

export function runtimeDetailEntityHref(entityId: string, endpoint: string): string {
  return `${endpoint.replace(/\/+$/, "")}/${encodeURIComponent(entityId)}`;
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

export function runtimeExportPackageReviewSummaryHref(
  packageId: string,
  endpoint = DEFAULT_RUNTIME_EXPORT_PACKAGES_ENDPOINT
): string {
  return `${runtimeExportPackageRecordHref(packageId, endpoint)}/review-summary`;
}

export function runtimeExportPackageReviewCompletionHref(
  packageId: string,
  endpoint = DEFAULT_RUNTIME_EXPORT_PACKAGES_ENDPOINT
): string {
  return `${runtimeExportPackageRecordHref(packageId, endpoint)}/review-completion`;
}

export function runtimeExportPackageHandoffReportHref(
  packageId: string,
  endpoint = DEFAULT_RUNTIME_EXPORT_PACKAGES_ENDPOINT
): string {
  return `${runtimeExportPackageRecordHref(packageId, endpoint)}/handoff-report`;
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

export function runtimeExportPackageRouteDetailsHref(
  packageId: string,
  cursor = 0,
  limit = 100,
  filters: RuntimeDetailQueryFilters = {},
  endpoint = DEFAULT_RUNTIME_EXPORT_PACKAGES_ENDPOINT
): string {
  const params = new URLSearchParams({
    cursor: String(cursor),
    limit: String(limit)
  });
  appendRuntimeDetailFilterParams(params, filters);
  return `${runtimeExportPackageRecordHref(packageId, endpoint)}/routes?${params.toString()}`;
}

export function runtimeExportPackageServiceTracesHref(
  packageId: string,
  cursor = 0,
  limit = 100,
  filters: RuntimeDetailQueryFilters = {},
  endpoint = DEFAULT_RUNTIME_EXPORT_PACKAGES_ENDPOINT
): string {
  const params = new URLSearchParams({
    cursor: String(cursor),
    limit: String(limit)
  });
  appendRuntimeDetailFilterParams(params, filters);
  return `${runtimeExportPackageRecordHref(packageId, endpoint)}/service-traces?${params.toString()}`;
}

export function runtimeExportPackageRouteDetailHref(
  packageId: string,
  routeId: string,
  endpoint = DEFAULT_RUNTIME_EXPORT_PACKAGES_ENDPOINT
): string {
  return `${runtimeExportPackageRecordHref(packageId, endpoint)}/routes/${encodeURIComponent(
    routeId
  )}`;
}

export function runtimeExportRouteComparisonReviewReportHref(
  packageId: string,
  endpoint = DEFAULT_RUNTIME_EXPORT_PACKAGES_ENDPOINT
): string {
  return `${runtimeExportPackageRecordHref(packageId, endpoint)}/route-comparison-review-report`;
}

export function runtimeExportScenarioReviewChecklistHref(
  packageId: string,
  endpoint = DEFAULT_RUNTIME_EXPORT_PACKAGES_ENDPOINT
): string {
  return `${runtimeExportPackageRecordHref(packageId, endpoint)}/scenario-review-checklist`;
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

export function userConfigurationReferenceHref(
  endpoint = DEFAULT_USER_CONFIG_REFERENCE_ENDPOINT
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

export function userConfigurationValidateTextHref(
  format: "auto" | "json" | "yaml" = "auto",
  endpoint = DEFAULT_USER_CONFIG_VALIDATE_TEXT_ENDPOINT
): string {
  return `${endpoint}?format=${encodeURIComponent(format)}`;
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
  limit: number,
  filters: RuntimeDetailQueryFilters = {}
): Promise<RuntimeDetailPageEnvelope> {
  const params = new URLSearchParams({
    cursor: String(cursor),
    limit: String(limit)
  });
  appendRuntimeDetailFilterParams(params, filters);
  const url = `${endpoint}?${params.toString()}`;
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`failed to load runtime details from ${url}: HTTP ${response.status}`);
  }
  return decodeRuntimeDetailPage(await response.json());
}

async function loadRuntimeEntityDetail(
  endpoint: string
): Promise<RuntimeEntityDetailEnvelopeV1> {
  const response = await fetch(endpoint);
  if (!response.ok) {
    throw new Error(`failed to load runtime entity detail from ${endpoint}: HTTP ${response.status}`);
  }
  return decodeRuntimeEntityDetail(await response.json());
}

function appendRuntimeDetailFilterParams(
  params: URLSearchParams,
  filters: RuntimeDetailQueryFilters
): void {
  const query = filters.query?.trim();
  if (query) {
    params.set("query", query);
  }
  const summaryVersion = filters.summaryVersion?.trim();
  if (summaryVersion) {
    params.set("summary_version", summaryVersion);
  }
  const availability = filters.availability?.trim();
  if (availability && availability !== "ALL") {
    params.set("availability", availability);
  }
  const businessType = filters.businessType?.trim();
  if (businessType && businessType !== "ALL") {
    params.set("business_type", businessType);
  }
  const bottleneckComponent = filters.bottleneckComponent?.trim();
  if (bottleneckComponent && bottleneckComponent !== "ALL") {
    params.set("bottleneck_component", bottleneckComponent);
  }
  const terminalState = filters.terminalState?.trim();
  if (terminalState && terminalState !== "ALL") {
    params.set("terminal_state", terminalState);
  }
  const computeNodeId = filters.computeNodeId?.trim();
  if (computeNodeId) {
    params.set("compute_node_id", computeNodeId);
  }
  const stageKind = filters.stageKind?.trim();
  if (stageKind && stageKind !== "ALL") {
    params.set("stage_kind", stageKind);
  }
  const terminalReason = filters.terminalReason?.trim();
  if (terminalReason && terminalReason !== "ALL") {
    params.set("terminal_reason", terminalReason);
  }
}

export function decodeRuntimeDetailPage(value: unknown): RuntimeDetailPageEnvelope {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new TypeError("runtime detail response must be an object");
  }
  const kind = (value as { kind?: unknown }).kind;
  const summary = (value as { summary?: unknown }).summary;
  if (
    kind !== "users" &&
    kind !== "satellites" &&
    kind !== "nodes" &&
    kind !== "routes" &&
    kind !== "services" &&
    kind !== "service_traces" &&
    kind !== "compute_nodes"
  ) {
    throw new TypeError(
      "runtime detail response kind must be users, satellites, nodes, routes, services, service_traces, or compute_nodes"
    );
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
      | RuntimeRouteExplanationSummaryV1
      | RuntimeServiceDetailPageV1
      | RuntimeServiceLifecycleTraceV2
      | RuntimeComputeNodeDetailPageV1
  } as RuntimeDetailPageEnvelope;
}

export function decodeRuntimeEntityDetail(value: unknown): RuntimeEntityDetailEnvelopeV1 {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new TypeError("runtime entity detail response must be an object");
  }
  const kind = (value as { kind?: unknown }).kind;
  const entityId = (value as { entity_id?: unknown }).entity_id;
  const summary = (value as { summary?: unknown }).summary;
  if (
    kind !== "user" &&
    kind !== "satellite" &&
    kind !== "route" &&
    kind !== "service" &&
    kind !== "service_trace" &&
    kind !== "compute_node"
  ) {
    throw new TypeError(
      "runtime entity detail kind must be user, satellite, route, service, service_trace, or compute_node"
    );
  }
  if (typeof entityId !== "string" || entityId.trim().length === 0) {
    throw new TypeError("runtime entity detail response must include entity_id string");
  }
  if (typeof summary !== "object" || summary === null || Array.isArray(summary)) {
    throw new TypeError("runtime entity detail response must include summary object");
  }
  return {
    ...(value as Record<string, unknown>),
    kind,
    entity_id: entityId,
    summary: summary as
      | RuntimeNodeDetailCardV1
      | RuntimeRouteExplanationItemV1
      | RuntimeServiceDetailItemV1
      | RuntimeServiceTraceDetailV2
      | RuntimeComputeNodeDetailItemV1
  } as RuntimeEntityDetailEnvelopeV1;
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

export function decodeRuntimeExportReviewSummary(
  value: unknown
): RuntimeExportReviewSummaryV1 {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new TypeError("runtime export review summary response must be an object");
  }
  if (
    typeof (value as { package_id?: unknown }).package_id !== "string" ||
    typeof (value as { artifacts?: unknown }).artifacts !== "object" ||
    (value as { artifacts?: unknown }).artifacts === null ||
    Array.isArray((value as { artifacts?: unknown }).artifacts)
  ) {
    throw new TypeError(
      "runtime export review summary response must include package_id and artifacts"
    );
  }
  return value as RuntimeExportReviewSummaryV1;
}

export function decodeRuntimeExportManifest(
  value: unknown
): RuntimeReproducibilityManifestV1 {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new TypeError("runtime export manifest response must be an object");
  }
  if (
    typeof (value as { manifest_id?: unknown }).manifest_id !== "string" ||
    typeof (value as { manifest_hash?: unknown }).manifest_hash !== "string" ||
    !Array.isArray((value as { artifacts?: unknown }).artifacts)
  ) {
    throw new TypeError(
      "runtime export manifest response must include manifest_id, manifest_hash, and artifacts"
    );
  }
  return value as RuntimeReproducibilityManifestV1;
}

export function decodeRuntimeExportDiagnosticsBundle(
  value: unknown
): RuntimeExportDiagnosticsBundleV1 {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new TypeError("runtime export diagnostics bundle response must be an object");
  }
  if (
    typeof (value as { package?: unknown }).package !== "object" ||
    (value as { package?: unknown }).package === null ||
    Array.isArray((value as { package?: unknown }).package) ||
    typeof (value as { artifact_health?: unknown }).artifact_health !== "object" ||
    (value as { artifact_health?: unknown }).artifact_health === null ||
    Array.isArray((value as { artifact_health?: unknown }).artifact_health) ||
    !Array.isArray((value as { findings?: unknown }).findings)
  ) {
    throw new TypeError(
      "runtime export diagnostics bundle response must include package, artifact_health, and findings"
    );
  }
  return value as RuntimeExportDiagnosticsBundleV1;
}

export function decodeRuntimeServiceLifecycleTrace(
  value: unknown
): RuntimeServiceLifecycleTraceV2 {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new TypeError("runtime service lifecycle trace response must be an object");
  }
  if (
    typeof (value as { source?: unknown }).source !== "string" ||
    typeof (value as { source_summary?: unknown }).source_summary !== "string" ||
    typeof (value as { trace_count?: unknown }).trace_count !== "number" ||
    !Array.isArray((value as { items?: unknown }).items)
  ) {
    throw new TypeError(
      "runtime service lifecycle trace response must include source, source_summary, trace_count, and items"
    );
  }
  return value as RuntimeServiceLifecycleTraceV2;
}

export function decodeRuntimeExportRouteDetailIndex(
  value: unknown
): RuntimeExportRouteDetailIndexV1 {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new TypeError("runtime export route detail index response must be an object");
  }
  if (
    typeof (value as { package_id?: unknown }).package_id !== "string" ||
    typeof (value as { route_summary?: unknown }).route_summary !== "object" ||
    (value as { route_summary?: unknown }).route_summary === null ||
    Array.isArray((value as { route_summary?: unknown }).route_summary) ||
    typeof (value as { route_trust?: unknown }).route_trust !== "object" ||
    (value as { route_trust?: unknown }).route_trust === null ||
    Array.isArray((value as { route_trust?: unknown }).route_trust) ||
    !Array.isArray((value as { routes?: unknown }).routes)
  ) {
    throw new TypeError(
      "runtime export route detail index response must include package_id, route_summary, route_trust, and routes"
    );
  }
  return value as RuntimeExportRouteDetailIndexV1;
}

export function decodeRuntimeExportRouteDetailPage(
  value: unknown
): RuntimeExportRouteDetailPageV1 {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new TypeError("runtime export route detail page response must be an object");
  }
  if (
    typeof (value as { package_id?: unknown }).package_id !== "string" ||
    typeof (value as { route_detail_index_hash?: unknown })
      .route_detail_index_hash !== "string" ||
    typeof (value as { filters?: unknown }).filters !== "object" ||
    (value as { filters?: unknown }).filters === null ||
    Array.isArray((value as { filters?: unknown }).filters) ||
    !Array.isArray((value as { items?: unknown }).items)
  ) {
    throw new TypeError(
      "runtime export route detail page response must include package_id, route_detail_index_hash, filters, and items"
    );
  }
  return value as RuntimeExportRouteDetailPageV1;
}

export function decodeRuntimeExportServiceTracePage(
  value: unknown
): RuntimeExportServiceTracePageV1 {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new TypeError("runtime export service trace page response must be an object");
  }
  if (
    typeof (value as { package_id?: unknown }).package_id !== "string" ||
    typeof (value as { filters?: unknown }).filters !== "object" ||
    (value as { filters?: unknown }).filters === null ||
    Array.isArray((value as { filters?: unknown }).filters) ||
    typeof (value as { artifact_window_only?: unknown })
      .artifact_window_only !== "boolean" ||
    !Array.isArray((value as { items?: unknown }).items)
  ) {
    throw new TypeError(
      "runtime export service trace page response must include package_id, artifact_window_only, filters, and items"
    );
  }
  return value as RuntimeExportServiceTracePageV1;
}

export function decodeRuntimeExportRouteDetailItem(
  value: unknown
): RuntimeExportRouteDetailItemV1 {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new TypeError("runtime export route detail item response must be an object");
  }
  if (
    typeof (value as { package_id?: unknown }).package_id !== "string" ||
    typeof (value as { route_id?: unknown }).route_id !== "string" ||
    typeof (value as { route?: unknown }).route !== "object" ||
    (value as { route?: unknown }).route === null ||
    Array.isArray((value as { route?: unknown }).route)
  ) {
    throw new TypeError(
      "runtime export route detail item response must include package_id, route_id, and route"
    );
  }
  return value as RuntimeExportRouteDetailItemV1;
}

export function decodeRuntimeExportRouteComparisonReviewReport(
  value: unknown
): RuntimeExportRouteComparisonReviewReportEnvelope {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new TypeError(
      "runtime export route comparison review report response must be an object"
    );
  }
  const summary = (value as { summary?: unknown }).summary;
  const artifact = (value as { artifact?: unknown }).artifact;
  if (
    typeof summary !== "object" ||
    summary === null ||
    Array.isArray(summary) ||
    typeof (summary as { report_id?: unknown }).report_id !== "string" ||
    !Array.isArray((summary as { records?: unknown }).records) ||
    typeof artifact !== "object" ||
    artifact === null ||
    Array.isArray(artifact)
  ) {
    throw new TypeError(
      "runtime export route comparison review report response must include summary report_id, records, and artifact"
    );
  }
  return {
    ...(value as Record<string, unknown>),
    summary: summary as RuntimeExportRouteComparisonReviewReportV1,
    artifact: artifact as RuntimeExportRouteComparisonReviewReportEnvelope["artifact"]
  } as RuntimeExportRouteComparisonReviewReportEnvelope;
}

export function decodeRuntimeExportRouteComparisonReviewReportArtifact(
  value: unknown
): RuntimeExportRouteComparisonReviewReportV1 {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new TypeError(
      "runtime export route comparison review report artifact must be an object"
    );
  }
  if (
    typeof (value as { report_id?: unknown }).report_id !== "string" ||
    typeof (value as { package_id?: unknown }).package_id !== "string" ||
    !Array.isArray((value as { records?: unknown }).records) ||
    typeof (value as { report_hash?: unknown }).report_hash !== "string"
  ) {
    throw new TypeError(
      "runtime export route comparison review report artifact must include report_id, package_id, records, and report_hash"
    );
  }
  return value as RuntimeExportRouteComparisonReviewReportV1;
}

export function decodeRuntimeExportScenarioReviewChecklistResponse(
  value: unknown
): RuntimeExportScenarioReviewChecklistEnvelope {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new TypeError(
      "runtime export scenario review checklist response must be an object"
    );
  }
  const summary = (value as { summary?: unknown }).summary;
  const artifact = (value as { artifact?: unknown }).artifact;
  if (
    typeof summary !== "object" ||
    summary === null ||
    Array.isArray(summary) ||
    typeof (summary as { checklist_id?: unknown }).checklist_id !== "string" ||
    !Array.isArray((summary as { records?: unknown }).records) ||
    typeof artifact !== "object" ||
    artifact === null ||
    Array.isArray(artifact)
  ) {
    throw new TypeError(
      "runtime export scenario review checklist response must include summary checklist_id, records, and artifact"
    );
  }
  return {
    ...(value as Record<string, unknown>),
    summary: summary as RuntimeExportScenarioReviewChecklistV1,
    artifact: artifact as RuntimeExportScenarioReviewChecklistEnvelope["artifact"]
  } as RuntimeExportScenarioReviewChecklistEnvelope;
}

export function decodeRuntimeExportScenarioReviewChecklist(
  value: unknown
): RuntimeExportScenarioReviewChecklistV1 {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new TypeError("runtime export scenario review checklist must be an object");
  }
  if (
    typeof (value as { checklist_id?: unknown }).checklist_id !== "string" ||
    typeof (value as { package_id?: unknown }).package_id !== "string" ||
    !Array.isArray((value as { records?: unknown }).records) ||
    typeof (value as { checklist_hash?: unknown }).checklist_hash !== "string"
  ) {
    throw new TypeError(
      "runtime export scenario review checklist must include checklist_id, package_id, records, and checklist_hash"
    );
  }
  return value as RuntimeExportScenarioReviewChecklistV1;
}

export function decodeRuntimeExportPackageAuditIndex(
  value: unknown
): RuntimeExportPackageAuditIndexV1 {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new TypeError("runtime export package audit index must be an object");
  }
  if (
    typeof (value as { audit_index_id?: unknown }).audit_index_id !== "string" ||
    typeof (value as { package_id?: unknown }).package_id !== "string" ||
    !Array.isArray((value as { artifact_hashes?: unknown }).artifact_hashes) ||
    typeof (value as { audit_hash?: unknown }).audit_hash !== "string"
  ) {
    throw new TypeError(
      "runtime export package audit index must include audit_index_id, package_id, artifact_hashes, and audit_hash"
    );
  }
  return value as RuntimeExportPackageAuditIndexV1;
}

export function decodeRuntimeExportPackageReviewCompletionEnvelope(
  value: unknown
): RuntimeExportPackageReviewCompletionEnvelope {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new TypeError(
      "runtime export package review completion response must be an object"
    );
  }
  const summary = (value as { summary?: unknown }).summary;
  const sourceArtifact = (value as { source_artifact?: unknown }).source_artifact;
  if (
    typeof summary !== "object" ||
    summary === null ||
    Array.isArray(summary) ||
    typeof (summary as { completion_id?: unknown }).completion_id !== "string" ||
    typeof (summary as { completion_hash?: unknown }).completion_hash !==
      "string" ||
    typeof sourceArtifact !== "object" ||
    sourceArtifact === null ||
    Array.isArray(sourceArtifact)
  ) {
    throw new TypeError(
      "runtime export package review completion response must include summary completion_id, completion_hash, and source_artifact"
    );
  }
  return {
    ...(value as Record<string, unknown>),
    summary: summary as RuntimeExportPackageReviewCompletionV1,
    source_artifact:
      sourceArtifact as RuntimeExportPackageReviewCompletionEnvelope["source_artifact"]
  } as RuntimeExportPackageReviewCompletionEnvelope;
}

export function decodeRuntimeExportScenarioReviewBundle(
  value: unknown
): RuntimeExportScenarioReviewBundleV1 {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new TypeError("runtime export scenario review bundle must be an object");
  }
  if (
    typeof (value as { bundle_id?: unknown }).bundle_id !== "string" ||
    typeof (value as { package_id?: unknown }).package_id !== "string" ||
    typeof (value as { user_configuration?: unknown }).user_configuration !==
      "object" ||
    (value as { user_configuration?: unknown }).user_configuration === null ||
    Array.isArray((value as { user_configuration?: unknown }).user_configuration) ||
    typeof (value as { scenario_review_hash?: unknown }).scenario_review_hash !==
      "string"
  ) {
    throw new TypeError(
      "runtime export scenario review bundle must include bundle_id, package_id, user_configuration, and scenario_review_hash"
    );
  }
  return value as RuntimeExportScenarioReviewBundleV1;
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

export function decodeUserConfigurationReference(
  value: unknown
): UserConfigurationReferenceEnvelope {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new TypeError("user configuration reference response must be an object");
  }
  const summary = (value as { summary?: unknown }).summary;
  if (typeof summary !== "object" || summary === null || Array.isArray(summary)) {
    throw new TypeError("user configuration reference response must include summary object");
  }
  if (
    typeof (summary as { reference_id?: unknown }).reference_id !== "string" ||
    typeof (summary as { schema_id?: unknown }).schema_id !== "string" ||
    !Array.isArray((summary as { sections?: unknown }).sections) ||
    !Array.isArray((summary as { fields?: unknown }).fields) ||
    typeof (summary as { reference_hash?: unknown }).reference_hash !== "string"
  ) {
    throw new TypeError(
      "user configuration reference must include reference_id, schema_id, sections, fields, and reference_hash"
    );
  }
  return {
    ...(value as Record<string, unknown>),
    summary: summary as UserConfigurationReferenceV1
  } as UserConfigurationReferenceEnvelope;
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
