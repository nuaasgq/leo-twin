import { Suspense, lazy, useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { MouseEvent } from "react";

import type { ScenarioControlValues } from "../config_panel/ConfigPanel";
import {
  ControlAck,
  ControlChannelClient,
  RuntimeAction
} from "../config_panel/controlClient";
import {
  FidelitySummary,
  GeneratedScenarioConfig,
  LargeDetailPaginationCollectionV2,
  LargeDetailPaginationContractV2,
  RuntimeExportCatalogV1,
  RuntimeExportDiagnosticsBundleV1,
  RuntimeExportPackageCompareV1,
  RuntimeExportPackageAcceptanceReportV1,
  RuntimeExportPackageAuditIndexV1,
  RuntimeExportScenarioReviewBundleV1,
  RuntimeExportScenarioReviewChecklistV1,
  RuntimeExportScenarioReviewChecklistTemplateComparisonV1,
  RuntimeExportScenarioReviewChecklistTemplateV1,
  RuntimeExportRouteComparisonReviewReportPageV1,
  RuntimeExportServiceTraceComparisonReviewReportPageV1,
  RuntimeExportRouteDetailItemV1,
  RuntimeExportRouteDetailPageV1,
  RuntimeExportServiceTraceItemV1,
  RuntimeExportServiceTracePageV1,
  RuntimeExportReviewSummaryV1,
  RuntimeExportUserServiceRequestPageV1,
  RuntimeExportRestoreCommandResultV1,
  RuntimeExportRestorePreflightV1,
  RuntimeBackpressureSummary,
  RuntimeComputeNodeDetailItemV1,
  RuntimeNodeDetailCardV1,
  RuntimeRouteExplanationItemV1,
  RuntimeReproducibilityManifestV1,
  RuntimeServiceDetailItemV1,
  RuntimeServiceLifecycleTraceV2,
  RuntimeServiceTraceDetailV2,
  RuntimeStatusPayload,
  ScenarioConfig,
  UserConfigurationExportV1,
  UserConfigurationReferenceV1,
  UserConfigurationSchemaV2,
  UserConfigurationTemplateCatalogV1,
  UserConfigurationValidationReportV1
} from "../core/event_types";
import { SnapshotEngine, WorldSnapshot, useWorldSnapshot } from "../state/snapshot_engine";
import { runtimeSpeedFactorLabel } from "../runtime_display";
import { WorldStateReducer } from "../state/reducer";
import { EventRouter } from "../stream/event_router";
import { EventThrottleLayer } from "../stream/throttle_layer";
import { WebSocketStreamClient } from "../stream/websocket_client";
import {
  loadMetricsSnapshot,
  loadRuntimeComputeNodeDetail,
  loadRuntimeComputeNodeDetails,
  loadRuntimeExportCatalog,
  loadRuntimeExportDiagnosticsBundle,
  loadRuntimeExportManifest,
  loadRuntimeExportPackageAcceptanceReport,
  loadRuntimeExportPackageCompare,
  loadRuntimeExportPackageAuditIndex,
  loadRuntimeExportScenarioReviewBundle,
  loadRuntimeExportScenarioReviewChecklist,
  loadRuntimeExportScenarioReviewChecklistTemplateComparison,
  loadRuntimeExportScenarioReviewChecklistTemplate,
  loadRuntimeExportRouteComparisonReviewReportPage,
  loadRuntimeExportServiceTraceComparisonReviewReportPage,
  loadRuntimeExportRouteDetailItem,
  loadRuntimeExportRouteDetailPage,
  loadRuntimeExportReviewSummary,
  loadRuntimeExportRestorePreflight,
  loadRuntimeExportServiceTraceItem,
  loadRuntimeExportServiceTracePage,
  loadRuntimeExportUserServiceRequestPage,
  loadRuntimeNodeDetails,
  loadRuntimeRouteDetail,
  loadRuntimeRouteDetails,
  loadRuntimeSatelliteDetail,
  loadRuntimeSatelliteDetails,
  loadRuntimeServiceDetail,
  loadRuntimeServiceDetails,
  loadRuntimeServiceTraceDetails,
  loadRuntimeServiceTraceDetail,
  loadRuntimeUserDetail,
  loadRuntimeUserDetails,
  loadRuntimeState,
  loadScenarioConfig,
  loadUserConfigurationExport,
  loadUserConfigurationReference,
  loadUserConfigurationSchema,
  loadUserConfigurationTemplates,
  RuntimeDetailQueryFilters,
  runtimeApiErrorMessage,
  saveRuntimeExportRouteComparisonReviewReport,
  saveRuntimeExportServiceTraceComparisonReviewReport,
  saveRuntimeExportScenarioReviewChecklist as saveRuntimeExportScenarioReviewChecklistArtifact,
  validateUserConfigurationCandidate,
  validateUserConfigurationTextCandidate
} from "./api";
import type {
  DataPanelExportRouteComparisonReviewSaveRequest,
  DataPanelExportRouteComparisonReviewReportPageRequest,
  DataPanelExportServiceTraceComparisonReviewSaveRequest,
  DataPanelExportServiceTraceComparisonReviewReportPageRequest,
  DataPanelExportScenarioReviewChecklistSaveRequest,
  DataPanelExportRouteDetailPageRequest,
  DataPanelExportUserServiceRequestPageRequest,
  DataPanelExportServiceTracePageRequest,
  RuntimeDetailPages
} from "../dashboard/data_panel/DataPanel";
import { UserOverview } from "../dashboard/user_overview/UserOverview";
import "./App.css";

const RUNTIME_STATUS_POLL_MS = 250;
const RUNTIME_PROGRESS_TICK_MS = 100;
const RUNTIME_DETAIL_FALLBACK_LIMIT = 5000;
const RUNTIME_EXPORT_CATALOG_POLL_MS = 2500;
const USER_CONFIGURATION_CONTRACT_POLL_MS = 5000;
const ROUTE_COMPARISON_REVIEW_REPORT_FILENAME =
  "route_comparison_review_report_v1.json";
const SERVICE_TRACE_COMPARISON_REVIEW_REPORT_FILENAME =
  "service_trace_comparison_review_report_v1.json";
const EXPORT_PACKAGE_AUDIT_INDEX_FILENAME = "export_package_audit_index_v1.json";
const SCENARIO_REVIEW_BUNDLE_FILENAME = "scenario_review_bundle_v1.json";
const SCENARIO_REVIEW_CHECKLIST_FILENAME = "scenario_review_checklist_v1.json";
const SERVICE_LIFECYCLE_TRACE_FILENAME = "service_lifecycle_trace_v2.json";
const USER_SERVICE_REQUEST_SUMMARY_FILENAME =
  "user_service_request_summary_v2.json";

type RuntimeConnectionChannel = "http" | "control" | "events" | "state";
type RuntimeConnectionStatus = "idle" | "connecting" | "live" | "degraded";
type RuntimeConnectionHealth = Record<RuntimeConnectionChannel, RuntimeConnectionStatus>;
type RuntimeStreamConsumerCursors = Record<"events" | "state", number>;
type RuntimeDetailCursorKey =
  | "users"
  | "satellites"
  | "routes"
  | "services"
  | "serviceTraces"
  | "computeNodes";
type RuntimeDetailCursorState = Record<RuntimeDetailCursorKey, number>;
type RuntimeDetailCursorLoadingState = Record<RuntimeDetailCursorKey, boolean>;
type RuntimeDetailCursorErrorState = Record<RuntimeDetailCursorKey, string | null>;
type RuntimeDetailFilterState = Record<
  RuntimeDetailCursorKey,
  RuntimeDetailQueryFilters
>;
type RuntimeSelectedNodeDetails = {
  user: RuntimeNodeDetailCardV1 | null;
  satellite: RuntimeNodeDetailCardV1 | null;
  route: RuntimeRouteExplanationItemV1 | null;
  service: RuntimeServiceDetailItemV1 | null;
  serviceTrace: RuntimeServiceTraceDetailV2 | null;
  computeNode: RuntimeComputeNodeDetailItemV1 | null;
};
type RuntimeExactDetailRequestState = {
  entityId: string | null;
  loading: boolean;
  error: string | null;
};
type RuntimeSelectedNodeDetailRequests = {
  user: RuntimeExactDetailRequestState;
  satellite: RuntimeExactDetailRequestState;
  route: RuntimeExactDetailRequestState;
  service: RuntimeExactDetailRequestState;
  serviceTrace: RuntimeExactDetailRequestState;
  computeNode: RuntimeExactDetailRequestState;
};

const DEFAULT_RUNTIME_CONNECTION_HEALTH: RuntimeConnectionHealth = {
  http: "connecting",
  control: "connecting",
  events: "idle",
  state: "idle"
};

const DEFAULT_RUNTIME_STREAM_CONSUMER_CURSORS: RuntimeStreamConsumerCursors = {
  events: 0,
  state: 0
};

const DEFAULT_RUNTIME_DETAIL_CURSORS: RuntimeDetailCursorState = {
  users: 0,
  satellites: 0,
  routes: 0,
  services: 0,
  serviceTraces: 0,
  computeNodes: 0
};

const DEFAULT_RUNTIME_DETAIL_CURSOR_LOADING: RuntimeDetailCursorLoadingState = {
  users: false,
  satellites: false,
  routes: false,
  services: false,
  serviceTraces: false,
  computeNodes: false
};

const DEFAULT_RUNTIME_DETAIL_CURSOR_ERRORS: RuntimeDetailCursorErrorState = {
  users: null,
  satellites: null,
  routes: null,
  services: null,
  serviceTraces: null,
  computeNodes: null
};

const DEFAULT_RUNTIME_DETAIL_FILTERS: RuntimeDetailFilterState = {
  users: {},
  satellites: {},
  routes: {},
  services: {},
  serviceTraces: {},
  computeNodes: {}
};

function defaultRuntimeExactDetailRequest(): RuntimeExactDetailRequestState {
  return {
    entityId: null,
    loading: false,
    error: null
  };
}

function defaultRuntimeSelectedNodeDetailRequests(): RuntimeSelectedNodeDetailRequests {
  return {
    user: defaultRuntimeExactDetailRequest(),
    satellite: defaultRuntimeExactDetailRequest(),
    route: defaultRuntimeExactDetailRequest(),
    service: defaultRuntimeExactDetailRequest(),
    serviceTrace: defaultRuntimeExactDetailRequest(),
    computeNode: defaultRuntimeExactDetailRequest()
  };
}

const CesiumGlobe = lazy(async () => {
  const module = await import("../3d/cesium/CesiumGlobe");
  return { default: module.CesiumGlobe };
});

const ConfigPanel = lazy(async () => {
  const module = await import("../config_panel/ConfigPanel");
  return { default: module.ConfigPanel };
});

const DataPanel = lazy(async () => {
  const module = await import("../dashboard/data_panel/DataPanel");
  return { default: module.DataPanel };
});

export function App() {
  const [surface, setSurface] = useState<FrontendSurface>(() =>
    surfaceFromPathname(window.location.pathname)
  );
  const [advancedDashboardVisible, setAdvancedDashboardVisible] = useState(false);
  const reducer = useMemo(
    () => new WorldStateReducer({ eventLogLimit: 10_000, metricSeriesLimit: 300 }),
    []
  );
  const snapshotEngine = useMemo(
    () =>
      new SnapshotEngine(reducer, {
        snapshotHz: 20
      }),
    [reducer]
  );
  const snapshot = useWorldSnapshot(snapshotEngine);
  const [connectionState, setConnectionState] = useState<"connecting" | "live" | "degraded">(
    "connecting"
  );
  const [connectionHealth, setConnectionHealth] = useState<RuntimeConnectionHealth>(
    DEFAULT_RUNTIME_CONNECTION_HEALTH
  );
  const [streamConsumerCursors, setStreamConsumerCursors] =
    useState<RuntimeStreamConsumerCursors>(DEFAULT_RUNTIME_STREAM_CONSUMER_CURSORS);
  const [scenarioConfig, setScenarioConfig] = useState<ScenarioConfig | null>(null);
  const [generatedConfig, setGeneratedConfig] = useState<GeneratedScenarioConfig | null>(null);
  const [controlError, setControlError] = useState<string | null>(null);
  const [runtimeStatus, setRuntimeStatus] = useState<RuntimeStatusPayload>(defaultRuntimeStatus());
  const [runtimeDetailPages, setRuntimeDetailPages] = useState<RuntimeDetailPages | null>(
    null
  );
  const [runtimeDetailCursors, setRuntimeDetailCursors] =
    useState<RuntimeDetailCursorState>(DEFAULT_RUNTIME_DETAIL_CURSORS);
  const [runtimeDetailCursorLoading, setRuntimeDetailCursorLoading] =
    useState<RuntimeDetailCursorLoadingState>(DEFAULT_RUNTIME_DETAIL_CURSOR_LOADING);
  const [runtimeDetailCursorErrors, setRuntimeDetailCursorErrors] =
    useState<RuntimeDetailCursorErrorState>(DEFAULT_RUNTIME_DETAIL_CURSOR_ERRORS);
  const [runtimeDetailFilters, setRuntimeDetailFilters] =
    useState<RuntimeDetailFilterState>(DEFAULT_RUNTIME_DETAIL_FILTERS);
  const [runtimeSelectedNodeDetails, setRuntimeSelectedNodeDetails] =
    useState<RuntimeSelectedNodeDetails>({
      user: null,
      satellite: null,
      route: null,
      service: null,
      serviceTrace: null,
      computeNode: null
    });
  const [runtimeSelectedNodeDetailRequests, setRuntimeSelectedNodeDetailRequests] =
    useState<RuntimeSelectedNodeDetailRequests>(() =>
      defaultRuntimeSelectedNodeDetailRequests()
    );
  const [runtimeExportCatalog, setRuntimeExportCatalog] =
    useState<RuntimeExportCatalogV1 | null>(null);
  const [runtimeExportCompare, setRuntimeExportCompare] =
    useState<RuntimeExportPackageCompareV1 | null>(null);
  const [runtimeExportReviewSummary, setRuntimeExportReviewSummary] =
    useState<RuntimeExportReviewSummaryV1 | null>(null);
  const [runtimeExportManifest, setRuntimeExportManifest] =
    useState<RuntimeReproducibilityManifestV1 | null>(null);
  const [runtimeExportDiagnosticsBundle, setRuntimeExportDiagnosticsBundle] =
    useState<RuntimeExportDiagnosticsBundleV1 | null>(null);
  const [runtimeExportServiceLifecycleTrace, setRuntimeExportServiceLifecycleTrace] =
    useState<RuntimeServiceLifecycleTraceV2 | null>(null);
  const [runtimeExportServiceTracePage, setRuntimeExportServiceTracePage] =
    useState<RuntimeExportServiceTracePageV1 | null>(null);
  const [runtimeExportServiceTraceItem, setRuntimeExportServiceTraceItem] =
    useState<RuntimeExportServiceTraceItemV1 | null>(null);
  const [
    runtimeExportUserServiceRequestPage,
    setRuntimeExportUserServiceRequestPage
  ] = useState<RuntimeExportUserServiceRequestPageV1 | null>(null);
  const [runtimeExportRouteDetailPage, setRuntimeExportRouteDetailPage] =
    useState<RuntimeExportRouteDetailPageV1 | null>(null);
  const [runtimeExportRouteDetailItem, setRuntimeExportRouteDetailItem] =
    useState<RuntimeExportRouteDetailItemV1 | null>(null);
  const [
    runtimeExportRouteComparisonReviewReport,
    setRuntimeExportRouteComparisonReviewReport
  ] = useState<RuntimeExportRouteComparisonReviewReportPageV1 | null>(null);
  const [
    runtimeExportServiceTraceComparisonReviewReport,
    setRuntimeExportServiceTraceComparisonReviewReport
  ] = useState<RuntimeExportServiceTraceComparisonReviewReportPageV1 | null>(null);
  const [runtimeExportPackageAuditIndex, setRuntimeExportPackageAuditIndex] =
    useState<RuntimeExportPackageAuditIndexV1 | null>(null);
  const [
    runtimeExportPackageAcceptanceReport,
    setRuntimeExportPackageAcceptanceReport
  ] = useState<RuntimeExportPackageAcceptanceReportV1 | null>(null);
  const [
    runtimeExportScenarioReviewBundle,
    setRuntimeExportScenarioReviewBundle
  ] = useState<RuntimeExportScenarioReviewBundleV1 | null>(null);
  const [
    runtimeExportScenarioReviewChecklist,
    setRuntimeExportScenarioReviewChecklist
  ] = useState<RuntimeExportScenarioReviewChecklistV1 | null>(null);
  const [
    runtimeExportScenarioReviewChecklistTemplate,
    setRuntimeExportScenarioReviewChecklistTemplate
  ] = useState<RuntimeExportScenarioReviewChecklistTemplateV1 | null>(null);
  const [
    runtimeExportScenarioReviewChecklistTemplateComparison,
    setRuntimeExportScenarioReviewChecklistTemplateComparison
  ] = useState<RuntimeExportScenarioReviewChecklistTemplateComparisonV1 | null>(
    null
  );
  const [
    runtimeExportRouteDetailItemRouteId,
    setRuntimeExportRouteDetailItemRouteId
  ] = useState<string | null>(null);
  const [
    runtimeExportServiceTraceItemTraceId,
    setRuntimeExportServiceTraceItemTraceId
  ] = useState<string | null>(null);
  const [runtimeExportComparePackageId, setRuntimeExportComparePackageId] =
    useState<string | null>(null);
  const [runtimeExportCompareLoading, setRuntimeExportCompareLoading] = useState(false);
  const [runtimeExportCompareError, setRuntimeExportCompareError] = useState<string | null>(
    null
  );
  const [runtimeExportReviewSummaryLoading, setRuntimeExportReviewSummaryLoading] =
    useState(false);
  const [runtimeExportReviewSummaryError, setRuntimeExportReviewSummaryError] =
    useState<string | null>(null);
  const [runtimeExportManifestLoading, setRuntimeExportManifestLoading] =
    useState(false);
  const [runtimeExportManifestError, setRuntimeExportManifestError] =
    useState<string | null>(null);
  const [runtimeExportDiagnosticsBundleLoading, setRuntimeExportDiagnosticsBundleLoading] =
    useState(false);
  const [runtimeExportDiagnosticsBundleError, setRuntimeExportDiagnosticsBundleError] =
    useState<string | null>(null);
  const [
    runtimeExportServiceLifecycleTraceLoading,
    setRuntimeExportServiceLifecycleTraceLoading
  ] = useState(false);
  const [
    runtimeExportServiceLifecycleTraceError,
    setRuntimeExportServiceLifecycleTraceError
  ] = useState<string | null>(null);
  const [
    runtimeExportUserServiceRequestPageLoading,
    setRuntimeExportUserServiceRequestPageLoading
  ] = useState(false);
  const [
    runtimeExportUserServiceRequestPageError,
    setRuntimeExportUserServiceRequestPageError
  ] = useState<string | null>(null);
  const [runtimeExportRouteDetailIndexLoading, setRuntimeExportRouteDetailIndexLoading] =
    useState(false);
  const [runtimeExportRouteDetailIndexError, setRuntimeExportRouteDetailIndexError] =
    useState<string | null>(null);
  const [runtimeExportRouteDetailItemLoading, setRuntimeExportRouteDetailItemLoading] =
    useState(false);
  const [runtimeExportRouteDetailItemError, setRuntimeExportRouteDetailItemError] =
    useState<string | null>(null);
  const [
    runtimeExportServiceTraceItemLoading,
    setRuntimeExportServiceTraceItemLoading
  ] = useState(false);
  const [
    runtimeExportServiceTraceItemError,
    setRuntimeExportServiceTraceItemError
  ] = useState<string | null>(null);
  const [
    runtimeExportRouteComparisonReviewReportLoading,
    setRuntimeExportRouteComparisonReviewReportLoading
  ] = useState(false);
  const [
    runtimeExportRouteComparisonReviewReportError,
    setRuntimeExportRouteComparisonReviewReportError
  ] = useState<string | null>(null);
  const [
    runtimeExportServiceTraceComparisonReviewReportLoading,
    setRuntimeExportServiceTraceComparisonReviewReportLoading
  ] = useState(false);
  const [
    runtimeExportServiceTraceComparisonReviewReportError,
    setRuntimeExportServiceTraceComparisonReviewReportError
  ] = useState<string | null>(null);
  const [runtimeExportPackageAuditIndexLoading, setRuntimeExportPackageAuditIndexLoading] =
    useState(false);
  const [runtimeExportPackageAuditIndexError, setRuntimeExportPackageAuditIndexError] =
    useState<string | null>(null);
  const [
    runtimeExportScenarioReviewBundleLoading,
    setRuntimeExportScenarioReviewBundleLoading
  ] = useState(false);
  const [
    runtimeExportScenarioReviewBundleError,
    setRuntimeExportScenarioReviewBundleError
  ] = useState<string | null>(null);
  const [
    runtimeExportScenarioReviewChecklistLoading,
    setRuntimeExportScenarioReviewChecklistLoading
  ] = useState(false);
  const [
    runtimeExportScenarioReviewChecklistError,
    setRuntimeExportScenarioReviewChecklistError
  ] = useState<string | null>(null);
  const [
    runtimeExportRouteComparisonReviewSavePendingRouteId,
    setRuntimeExportRouteComparisonReviewSavePendingRouteId
  ] = useState<string | null>(null);
  const [
    runtimeExportRouteComparisonReviewSaveError,
    setRuntimeExportRouteComparisonReviewSaveError
  ] = useState<string | null>(null);
  const [
    runtimeExportRouteComparisonReviewSaveReportHash,
    setRuntimeExportRouteComparisonReviewSaveReportHash
  ] = useState<string | null>(null);
  const [
    runtimeExportServiceTraceComparisonReviewSavePendingTraceId,
    setRuntimeExportServiceTraceComparisonReviewSavePendingTraceId
  ] = useState<string | null>(null);
  const [
    runtimeExportServiceTraceComparisonReviewSaveError,
    setRuntimeExportServiceTraceComparisonReviewSaveError
  ] = useState<string | null>(null);
  const [
    runtimeExportServiceTraceComparisonReviewSaveReportHash,
    setRuntimeExportServiceTraceComparisonReviewSaveReportHash
  ] = useState<string | null>(null);
  const [
    runtimeExportScenarioReviewChecklistSavePending,
    setRuntimeExportScenarioReviewChecklistSavePending
  ] = useState(false);
  const [
    runtimeExportScenarioReviewChecklistSaveError,
    setRuntimeExportScenarioReviewChecklistSaveError
  ] = useState<string | null>(null);
  const [
    runtimeExportScenarioReviewChecklistSaveHash,
    setRuntimeExportScenarioReviewChecklistSaveHash
  ] = useState<string | null>(null);
  const [runtimeExportRestorePreflight, setRuntimeExportRestorePreflight] =
    useState<RuntimeExportRestorePreflightV1 | null>(null);
  const [runtimeExportRestorePreflightLoading, setRuntimeExportRestorePreflightLoading] =
    useState(false);
  const [runtimeExportRestorePreflightError, setRuntimeExportRestorePreflightError] =
    useState<string | null>(null);
  const [
    runtimeExportRestoreCommandPendingPackageId,
    setRuntimeExportRestoreCommandPendingPackageId
  ] = useState<string | null>(null);
  const [runtimeExportRestoreCommandError, setRuntimeExportRestoreCommandError] =
    useState<string | null>(null);
  const [runtimeExportRestoreResult, setRuntimeExportRestoreResult] =
    useState<RuntimeExportRestoreCommandResultV1 | null>(null);
  const [userConfigurationSchema, setUserConfigurationSchema] =
    useState<UserConfigurationSchemaV2 | null>(null);
  const [userConfigurationTemplates, setUserConfigurationTemplates] =
    useState<UserConfigurationTemplateCatalogV1 | null>(null);
  const [userConfigurationReference, setUserConfigurationReference] =
    useState<UserConfigurationReferenceV1 | null>(null);
  const [userConfigurationExport, setUserConfigurationExport] =
    useState<UserConfigurationExportV1 | null>(null);
  const [userConfigurationContractLoading, setUserConfigurationContractLoading] =
    useState(false);
  const [userConfigurationContractError, setUserConfigurationContractError] =
    useState<string | null>(null);
  const [dismissedBackpressureNoticeKey, setDismissedBackpressureNoticeKey] =
    useState<string | null>(() =>
      readBackpressureNoticeDismissKey(browserSessionStorage())
    );
  const [dismissedCompletionNoticeKey, setDismissedCompletionNoticeKey] =
    useState<string | null>(() =>
      readCompletionNoticeDismissKey(browserSessionStorage())
    );
  const [completionNoticeArmed, setCompletionNoticeArmed] = useState(false);
  const [runtimeProgressAnchor, setRuntimeProgressAnchor] = useState<RuntimeProgressAnchor>(() =>
    defaultRuntimeProgressAnchor(defaultRuntimeStatus())
  );
  const [runtimeProgressNowMs, setRuntimeProgressNowMs] = useState(() => Date.now());
  const streamClientRef = useRef<WebSocketStreamClient | null>(null);
  const streamRouterRef = useRef<EventRouter | null>(null);

  useEffect(() => {
    snapshotEngine.start();
    return () => snapshotEngine.stop();
  }, [snapshotEngine]);

  useEffect(() => {
    const syncSurfaceFromLocation = () => {
      setSurface(surfaceFromPathname(window.location.pathname));
    };
    window.addEventListener("popstate", syncSurfaceFromLocation);
    return () => window.removeEventListener("popstate", syncSurfaceFromLocation);
  }, []);

  useEffect(() => {
    document.body.dataset.frontendSurface = bodySurfaceAttribute(surface);
    return () => {
      delete document.body.dataset.frontendSurface;
    };
  }, [surface]);

  const navigateWithinApp = useCallback(
    (event: MouseEvent<HTMLAnchorElement>, pathname: string) => {
      if (
        event.defaultPrevented ||
        event.button !== 0 ||
        event.altKey ||
        event.ctrlKey ||
        event.metaKey ||
        event.shiftKey
      ) {
        return;
      }
      event.preventDefault();
      if (window.location.pathname !== pathname) {
        window.history.pushState(null, "", pathname);
      }
      setSurface(surfaceFromPathname(pathname));
    },
    []
  );

  const setConnectionChannel = useCallback(
    (channel: RuntimeConnectionChannel, status: RuntimeConnectionStatus) => {
      setConnectionHealth((previous) =>
        previous[channel] === status ? previous : { ...previous, [channel]: status }
      );
    },
    []
  );

  const closeStreams = useCallback(() => {
    streamClientRef.current?.close();
    streamRouterRef.current?.close();
    streamClientRef.current = null;
    streamRouterRef.current = null;
    setConnectionChannel("events", "idle");
    setConnectionChannel("state", "idle");
    setStreamConsumerCursors(DEFAULT_RUNTIME_STREAM_CONSUMER_CURSORS);
  }, [setConnectionChannel]);

  const resetWorld = useCallback(
    (scenario: ScenarioConfig | null) => {
      reducer.reset();
      if (scenario !== null) {
        snapshotEngine.applyScenarioConfig(scenario);
      }
      snapshotEngine.publishNow();
    },
    [reducer, snapshotEngine]
  );

  useEffect(() => {
    setRuntimeDetailCursors(DEFAULT_RUNTIME_DETAIL_CURSORS);
    setRuntimeDetailCursorErrors(DEFAULT_RUNTIME_DETAIL_CURSOR_ERRORS);
    setRuntimeDetailFilters(DEFAULT_RUNTIME_DETAIL_FILTERS);
    setRuntimeSelectedNodeDetails({
      user: null,
      satellite: null,
      route: null,
      service: null,
      serviceTrace: null,
      computeNode: null
    });
    setRuntimeSelectedNodeDetailRequests(defaultRuntimeSelectedNodeDetailRequests());
  }, [runtimeStatus.config_version]);

  const refreshRuntimeDetails = useCallback(async (
    detailConfig: GeneratedScenarioConfig | null = generatedConfig
  ) => {
    const requestPlan = runtimeDetailRequestPlan(
      detailConfig?.backend_summary?.large_detail_pagination_contract_v2
    );
    const [users, satellites, nodes, routes, services, serviceTraces, computeNodes] =
      await Promise.allSettled([
        loadRuntimeUserDetails(
          runtimeDetailCursors.users,
          requestPlan.users.limit,
          requestPlan.users.endpoint,
          runtimeDetailFilters.users
        ),
        loadRuntimeSatelliteDetails(
          runtimeDetailCursors.satellites,
          requestPlan.satellites.limit,
          requestPlan.satellites.endpoint,
          runtimeDetailFilters.satellites
        ),
        loadRuntimeNodeDetails(
          0,
          requestPlan.nodes.limit,
          requestPlan.nodes.endpoint
        ),
        loadRuntimeRouteDetails(
          runtimeDetailCursors.routes,
          requestPlan.routes.limit,
          requestPlan.routes.endpoint,
          runtimeDetailFilters.routes
        ),
        loadRuntimeServiceDetails(
          runtimeDetailCursors.services,
          requestPlan.services.limit,
          requestPlan.services.endpoint,
          runtimeDetailFilters.services
        ),
        loadRuntimeServiceTraceDetails(
          runtimeDetailCursors.serviceTraces,
          requestPlan.serviceTraces.limit,
          requestPlan.serviceTraces.endpoint,
          runtimeDetailFilters.serviceTraces
        ),
        loadRuntimeComputeNodeDetails(
          runtimeDetailCursors.computeNodes,
          requestPlan.computeNodes.limit,
          requestPlan.computeNodes.endpoint,
          runtimeDetailFilters.computeNodes
        )
    ]);
    if (
      users.status === "rejected" &&
      satellites.status === "rejected" &&
      nodes.status === "rejected" &&
      routes.status === "rejected" &&
      services.status === "rejected" &&
      serviceTraces.status === "rejected" &&
      computeNodes.status === "rejected"
    ) {
      setRuntimeDetailPages(null);
      return;
    }
    setRuntimeDetailPages({
      users: users.status === "fulfilled" ? users.value : null,
      satellites: satellites.status === "fulfilled" ? satellites.value : null,
      nodes: nodes.status === "fulfilled" ? nodes.value : null,
      routes: routes.status === "fulfilled" ? routes.value : null,
      services: services.status === "fulfilled" ? services.value : null,
      serviceTraces:
        serviceTraces.status === "fulfilled" ? serviceTraces.value : null,
      computeNodes: computeNodes.status === "fulfilled" ? computeNodes.value : null
    });
    setRuntimeDetailCursors((previous) => ({
      users: users.status === "fulfilled" ? users.value.cursor ?? 0 : previous.users,
      satellites:
        satellites.status === "fulfilled"
          ? satellites.value.cursor ?? 0
          : previous.satellites,
      routes: routes.status === "fulfilled" ? routes.value.cursor ?? 0 : previous.routes,
      services: services.status === "fulfilled" ? services.value.cursor : previous.services,
      serviceTraces:
        serviceTraces.status === "fulfilled"
          ? serviceTraces.value.cursor
          : previous.serviceTraces,
      computeNodes:
        computeNodes.status === "fulfilled" ? computeNodes.value.cursor : previous.computeNodes
    }));
    setRuntimeDetailCursorErrors((previous) => ({
      users: users.status === "fulfilled" ? null : previous.users,
      satellites: satellites.status === "fulfilled" ? null : previous.satellites,
      routes: routes.status === "fulfilled" ? null : previous.routes,
      services: services.status === "fulfilled" ? null : previous.services,
      serviceTraces:
        serviceTraces.status === "fulfilled" ? null : previous.serviceTraces,
      computeNodes: computeNodes.status === "fulfilled" ? null : previous.computeNodes
    }));
  }, [generatedConfig, runtimeDetailCursors, runtimeDetailFilters]);

  const refreshRuntimeUserDetailCursor = useCallback(async (
    cursor: number,
    filters: RuntimeDetailQueryFilters = runtimeDetailFilters.users
  ) => {
    const requestPlan = runtimeDetailRequestPlan(
      generatedConfig?.backend_summary?.large_detail_pagination_contract_v2
    );
    const safeCursor = normalizeRuntimeDetailCursor(cursor);
    const normalizedFilters = normalizeRuntimeDetailFilters(filters);
    setRuntimeDetailFilters((previous) => ({ ...previous, users: normalizedFilters }));
    setRuntimeDetailCursorLoading((previous) => ({ ...previous, users: true }));
    setRuntimeDetailCursorErrors((previous) => ({ ...previous, users: null }));
    try {
      const page = await loadRuntimeUserDetails(
        safeCursor,
        requestPlan.users.limit,
        requestPlan.users.endpoint,
        normalizedFilters
      );
      setRuntimeDetailPages((previous) => ({
        ...(previous ?? {}),
        users: page
      }));
      setRuntimeDetailCursors((previous) => ({ ...previous, users: page.cursor ?? 0 }));
      setConnectionChannel("http", "live");
    } catch (error) {
      setRuntimeDetailCursorErrors((previous) => ({
        ...previous,
        users: runtimeApiErrorMessage(error)
      }));
      setConnectionChannel("http", "degraded");
    } finally {
      setRuntimeDetailCursorLoading((previous) => ({ ...previous, users: false }));
    }
  }, [generatedConfig, runtimeDetailFilters.users, setConnectionChannel]);

  const refreshRuntimeSatelliteDetailCursor = useCallback(async (
    cursor: number,
    filters: RuntimeDetailQueryFilters = runtimeDetailFilters.satellites
  ) => {
    const requestPlan = runtimeDetailRequestPlan(
      generatedConfig?.backend_summary?.large_detail_pagination_contract_v2
    );
    const safeCursor = normalizeRuntimeDetailCursor(cursor);
    const normalizedFilters = normalizeRuntimeDetailFilters(filters);
    setRuntimeDetailFilters((previous) => ({
      ...previous,
      satellites: normalizedFilters
    }));
    setRuntimeDetailCursorLoading((previous) => ({ ...previous, satellites: true }));
    setRuntimeDetailCursorErrors((previous) => ({ ...previous, satellites: null }));
    try {
      const page = await loadRuntimeSatelliteDetails(
        safeCursor,
        requestPlan.satellites.limit,
        requestPlan.satellites.endpoint,
        normalizedFilters
      );
      setRuntimeDetailPages((previous) => ({
        ...(previous ?? {}),
        satellites: page
      }));
      setRuntimeDetailCursors((previous) => ({
        ...previous,
        satellites: page.cursor ?? 0
      }));
      setConnectionChannel("http", "live");
    } catch (error) {
      setRuntimeDetailCursorErrors((previous) => ({
        ...previous,
        satellites: runtimeApiErrorMessage(error)
      }));
      setConnectionChannel("http", "degraded");
    } finally {
      setRuntimeDetailCursorLoading((previous) => ({
        ...previous,
        satellites: false
      }));
    }
  }, [generatedConfig, runtimeDetailFilters.satellites, setConnectionChannel]);

  const refreshRuntimeRouteDetailCursor = useCallback(async (
    cursor: number,
    filters: RuntimeDetailQueryFilters = runtimeDetailFilters.routes
  ) => {
    const requestPlan = runtimeDetailRequestPlan(
      generatedConfig?.backend_summary?.large_detail_pagination_contract_v2
    );
    const safeCursor = normalizeRuntimeDetailCursor(cursor);
    const normalizedFilters = normalizeRuntimeDetailFilters(filters);
    setRuntimeDetailFilters((previous) => ({ ...previous, routes: normalizedFilters }));
    setRuntimeDetailCursorLoading((previous) => ({ ...previous, routes: true }));
    setRuntimeDetailCursorErrors((previous) => ({ ...previous, routes: null }));
    try {
      const page = await loadRuntimeRouteDetails(
        safeCursor,
        requestPlan.routes.limit,
        requestPlan.routes.endpoint,
        normalizedFilters
      );
      setRuntimeDetailPages((previous) => ({
        ...(previous ?? {}),
        routes: page
      }));
      setRuntimeDetailCursors((previous) => ({ ...previous, routes: page.cursor ?? 0 }));
      setConnectionChannel("http", "live");
    } catch (error) {
      setRuntimeDetailCursorErrors((previous) => ({
        ...previous,
        routes: runtimeApiErrorMessage(error)
      }));
      setConnectionChannel("http", "degraded");
    } finally {
      setRuntimeDetailCursorLoading((previous) => ({ ...previous, routes: false }));
    }
  }, [generatedConfig, runtimeDetailFilters.routes, setConnectionChannel]);

  const refreshRuntimeServiceDetailCursor = useCallback(async (
    cursor: number,
    filters: RuntimeDetailQueryFilters = runtimeDetailFilters.services
  ) => {
    const requestPlan = runtimeDetailRequestPlan(
      generatedConfig?.backend_summary?.large_detail_pagination_contract_v2
    );
    const safeCursor = normalizeRuntimeDetailCursor(cursor);
    const normalizedFilters = normalizeRuntimeDetailFilters(filters);
    setRuntimeDetailFilters((previous) => ({
      ...previous,
      services: normalizedFilters
    }));
    setRuntimeDetailCursorLoading((previous) => ({ ...previous, services: true }));
    setRuntimeDetailCursorErrors((previous) => ({ ...previous, services: null }));
    try {
      const page = await loadRuntimeServiceDetails(
        safeCursor,
        requestPlan.services.limit,
        requestPlan.services.endpoint,
        normalizedFilters
      );
      setRuntimeDetailPages((previous) => ({
        ...(previous ?? {}),
        services: page
      }));
      setRuntimeDetailCursors((previous) => ({ ...previous, services: page.cursor }));
      setConnectionChannel("http", "live");
    } catch (error) {
      setRuntimeDetailCursorErrors((previous) => ({
        ...previous,
        services: runtimeApiErrorMessage(error)
      }));
      setConnectionChannel("http", "degraded");
    } finally {
      setRuntimeDetailCursorLoading((previous) => ({ ...previous, services: false }));
    }
  }, [generatedConfig, runtimeDetailFilters.services, setConnectionChannel]);

  const refreshRuntimeServiceTraceDetailCursor = useCallback(async (
    cursor: number,
    filters: RuntimeDetailQueryFilters = runtimeDetailFilters.serviceTraces
  ) => {
    const requestPlan = runtimeDetailRequestPlan(
      generatedConfig?.backend_summary?.large_detail_pagination_contract_v2
    );
    const safeCursor = normalizeRuntimeDetailCursor(cursor);
    const normalizedFilters = normalizeRuntimeDetailFilters(filters);
    setRuntimeDetailFilters((previous) => ({
      ...previous,
      serviceTraces: normalizedFilters
    }));
    setRuntimeDetailCursorLoading((previous) => ({
      ...previous,
      serviceTraces: true
    }));
    setRuntimeDetailCursorErrors((previous) => ({
      ...previous,
      serviceTraces: null
    }));
    try {
      const page = await loadRuntimeServiceTraceDetails(
        safeCursor,
        requestPlan.serviceTraces.limit,
        requestPlan.serviceTraces.endpoint,
        normalizedFilters
      );
      setRuntimeDetailPages((previous) => ({
        ...(previous ?? {}),
        serviceTraces: page
      }));
      setRuntimeDetailCursors((previous) => ({
        ...previous,
        serviceTraces: page.cursor
      }));
      setConnectionChannel("http", "live");
    } catch (error) {
      setRuntimeDetailCursorErrors((previous) => ({
        ...previous,
        serviceTraces: runtimeApiErrorMessage(error)
      }));
      setConnectionChannel("http", "degraded");
    } finally {
      setRuntimeDetailCursorLoading((previous) => ({
        ...previous,
        serviceTraces: false
      }));
    }
  }, [generatedConfig, runtimeDetailFilters.serviceTraces, setConnectionChannel]);

  const refreshRuntimeComputeNodeDetailCursor = useCallback(async (
    cursor: number,
    filters: RuntimeDetailQueryFilters = runtimeDetailFilters.computeNodes
  ) => {
    const requestPlan = runtimeDetailRequestPlan(
      generatedConfig?.backend_summary?.large_detail_pagination_contract_v2
    );
    const safeCursor = normalizeRuntimeDetailCursor(cursor);
    const normalizedFilters = normalizeRuntimeDetailFilters(filters);
    setRuntimeDetailFilters((previous) => ({
      ...previous,
      computeNodes: normalizedFilters
    }));
    setRuntimeDetailCursorLoading((previous) => ({ ...previous, computeNodes: true }));
    setRuntimeDetailCursorErrors((previous) => ({ ...previous, computeNodes: null }));
    try {
      const page = await loadRuntimeComputeNodeDetails(
        safeCursor,
        requestPlan.computeNodes.limit,
        requestPlan.computeNodes.endpoint,
        normalizedFilters
      );
      setRuntimeDetailPages((previous) => ({
        ...(previous ?? {}),
        computeNodes: page
      }));
      setRuntimeDetailCursors((previous) => ({
        ...previous,
        computeNodes: page.cursor
      }));
      setConnectionChannel("http", "live");
    } catch (error) {
      setRuntimeDetailCursorErrors((previous) => ({
        ...previous,
        computeNodes: runtimeApiErrorMessage(error)
      }));
      setConnectionChannel("http", "degraded");
    } finally {
      setRuntimeDetailCursorLoading((previous) => ({
        ...previous,
        computeNodes: false
      }));
    }
  }, [generatedConfig, runtimeDetailFilters.computeNodes, setConnectionChannel]);

  const refreshRuntimeUserEntityDetail = useCallback(async (userId: string | null) => {
    const normalizedUserId = userId?.trim() ?? "";
    if (!normalizedUserId) {
      setRuntimeSelectedNodeDetails((previous) => ({ ...previous, user: null }));
      setRuntimeSelectedNodeDetailRequests((previous) => ({
        ...previous,
        user: defaultRuntimeExactDetailRequest()
      }));
      return;
    }
    setRuntimeSelectedNodeDetailRequests((previous) => ({
      ...previous,
      user: { entityId: normalizedUserId, loading: true, error: null }
    }));
    const requestPlan = runtimeDetailRequestPlan(
      generatedConfig?.backend_summary?.large_detail_pagination_contract_v2
    );
    try {
      const detail = await loadRuntimeUserDetail(
        normalizedUserId,
        requestPlan.users.endpoint
      );
      setRuntimeSelectedNodeDetails((previous) => ({
        ...previous,
        user: detail
      }));
      setRuntimeSelectedNodeDetailRequests((previous) => ({
        ...previous,
        user: { entityId: normalizedUserId, loading: false, error: null }
      }));
      setConnectionChannel("http", "live");
    } catch (error) {
      setRuntimeSelectedNodeDetails((previous) => ({ ...previous, user: null }));
      setRuntimeSelectedNodeDetailRequests((previous) => ({
        ...previous,
        user: {
          entityId: normalizedUserId,
          loading: false,
          error: runtimeApiErrorMessage(error)
        }
      }));
      setConnectionChannel("http", "degraded");
    }
  }, [generatedConfig, setConnectionChannel]);

  const refreshRuntimeSatelliteEntityDetail = useCallback(
    async (satelliteId: string | null) => {
      const normalizedSatelliteId = satelliteId?.trim() ?? "";
      if (!normalizedSatelliteId) {
        setRuntimeSelectedNodeDetails((previous) => ({
          ...previous,
          satellite: null
        }));
        setRuntimeSelectedNodeDetailRequests((previous) => ({
          ...previous,
          satellite: defaultRuntimeExactDetailRequest()
        }));
        return;
      }
      setRuntimeSelectedNodeDetailRequests((previous) => ({
        ...previous,
        satellite: { entityId: normalizedSatelliteId, loading: true, error: null }
      }));
      const requestPlan = runtimeDetailRequestPlan(
        generatedConfig?.backend_summary?.large_detail_pagination_contract_v2
      );
      try {
        const detail = await loadRuntimeSatelliteDetail(
          normalizedSatelliteId,
          requestPlan.satellites.endpoint
        );
        setRuntimeSelectedNodeDetails((previous) => ({
          ...previous,
          satellite: detail
        }));
        setRuntimeSelectedNodeDetailRequests((previous) => ({
          ...previous,
          satellite: { entityId: normalizedSatelliteId, loading: false, error: null }
        }));
        setConnectionChannel("http", "live");
      } catch (error) {
        setRuntimeSelectedNodeDetails((previous) => ({
          ...previous,
          satellite: null
        }));
        setRuntimeSelectedNodeDetailRequests((previous) => ({
          ...previous,
          satellite: {
            entityId: normalizedSatelliteId,
            loading: false,
            error: runtimeApiErrorMessage(error)
          }
        }));
        setConnectionChannel("http", "degraded");
      }
    },
    [generatedConfig, setConnectionChannel]
  );

  const refreshRuntimeRouteEntityDetail = useCallback(async (routeId: string | null) => {
    const normalizedRouteId = routeId?.trim() ?? "";
    if (!normalizedRouteId) {
      setRuntimeSelectedNodeDetails((previous) => ({ ...previous, route: null }));
      setRuntimeSelectedNodeDetailRequests((previous) => ({
        ...previous,
        route: defaultRuntimeExactDetailRequest()
      }));
      return;
    }
    setRuntimeSelectedNodeDetailRequests((previous) => ({
      ...previous,
      route: { entityId: normalizedRouteId, loading: true, error: null }
    }));
    const requestPlan = runtimeDetailRequestPlan(
      generatedConfig?.backend_summary?.large_detail_pagination_contract_v2
    );
    try {
      const detail = await loadRuntimeRouteDetail(
        normalizedRouteId,
        requestPlan.routes.endpoint
      );
      setRuntimeSelectedNodeDetails((previous) => ({
        ...previous,
        route: detail
      }));
      setRuntimeSelectedNodeDetailRequests((previous) => ({
        ...previous,
        route: { entityId: normalizedRouteId, loading: false, error: null }
      }));
      setConnectionChannel("http", "live");
    } catch (error) {
      setRuntimeSelectedNodeDetails((previous) => ({ ...previous, route: null }));
      setRuntimeSelectedNodeDetailRequests((previous) => ({
        ...previous,
        route: {
          entityId: normalizedRouteId,
          loading: false,
          error: runtimeApiErrorMessage(error)
        }
      }));
      setConnectionChannel("http", "degraded");
    }
  }, [generatedConfig, setConnectionChannel]);

  const refreshRuntimeServiceEntityDetail = useCallback(
    async (serviceId: string | null) => {
      const normalizedServiceId = serviceId?.trim() ?? "";
      if (!normalizedServiceId) {
        setRuntimeSelectedNodeDetails((previous) => ({ ...previous, service: null }));
        setRuntimeSelectedNodeDetailRequests((previous) => ({
          ...previous,
          service: defaultRuntimeExactDetailRequest()
        }));
        return;
      }
      setRuntimeSelectedNodeDetailRequests((previous) => ({
        ...previous,
        service: { entityId: normalizedServiceId, loading: true, error: null }
      }));
      const requestPlan = runtimeDetailRequestPlan(
        generatedConfig?.backend_summary?.large_detail_pagination_contract_v2
      );
      try {
        const detail = await loadRuntimeServiceDetail(
          normalizedServiceId,
          requestPlan.services.endpoint
        );
        setRuntimeSelectedNodeDetails((previous) => ({
          ...previous,
          service: detail
        }));
        setRuntimeSelectedNodeDetailRequests((previous) => ({
          ...previous,
          service: { entityId: normalizedServiceId, loading: false, error: null }
        }));
        setConnectionChannel("http", "live");
      } catch (error) {
        setRuntimeSelectedNodeDetails((previous) => ({ ...previous, service: null }));
        setRuntimeSelectedNodeDetailRequests((previous) => ({
          ...previous,
          service: {
            entityId: normalizedServiceId,
            loading: false,
            error: runtimeApiErrorMessage(error)
          }
        }));
        setConnectionChannel("http", "degraded");
      }
    },
    [generatedConfig, setConnectionChannel]
  );

  const refreshRuntimeServiceTraceEntityDetail = useCallback(
    async (traceId: string | null) => {
      const normalizedTraceId = traceId?.trim() ?? "";
      if (!normalizedTraceId) {
        setRuntimeSelectedNodeDetails((previous) => ({
          ...previous,
          serviceTrace: null
        }));
        setRuntimeSelectedNodeDetailRequests((previous) => ({
          ...previous,
          serviceTrace: defaultRuntimeExactDetailRequest()
        }));
        return;
      }
      setRuntimeSelectedNodeDetailRequests((previous) => ({
        ...previous,
        serviceTrace: { entityId: normalizedTraceId, loading: true, error: null }
      }));
      try {
        const detail = await loadRuntimeServiceTraceDetail(normalizedTraceId);
        setRuntimeSelectedNodeDetails((previous) => ({
          ...previous,
          serviceTrace: detail
        }));
        setRuntimeSelectedNodeDetailRequests((previous) => ({
          ...previous,
          serviceTrace: { entityId: normalizedTraceId, loading: false, error: null }
        }));
        setConnectionChannel("http", "live");
      } catch (error) {
        setRuntimeSelectedNodeDetails((previous) => ({
          ...previous,
          serviceTrace: null
        }));
        setRuntimeSelectedNodeDetailRequests((previous) => ({
          ...previous,
          serviceTrace: {
            entityId: normalizedTraceId,
            loading: false,
            error: runtimeApiErrorMessage(error)
          }
        }));
        setConnectionChannel("http", "degraded");
      }
    },
    [setConnectionChannel]
  );

  const refreshRuntimeComputeNodeEntityDetail = useCallback(
    async (nodeId: string | null) => {
      const normalizedNodeId = nodeId?.trim() ?? "";
      if (!normalizedNodeId) {
        setRuntimeSelectedNodeDetails((previous) => ({
          ...previous,
          computeNode: null
        }));
        setRuntimeSelectedNodeDetailRequests((previous) => ({
          ...previous,
          computeNode: defaultRuntimeExactDetailRequest()
        }));
        return;
      }
      setRuntimeSelectedNodeDetailRequests((previous) => ({
        ...previous,
        computeNode: { entityId: normalizedNodeId, loading: true, error: null }
      }));
      const requestPlan = runtimeDetailRequestPlan(
        generatedConfig?.backend_summary?.large_detail_pagination_contract_v2
      );
      try {
        const detail = await loadRuntimeComputeNodeDetail(
          normalizedNodeId,
          requestPlan.computeNodes.endpoint
        );
        setRuntimeSelectedNodeDetails((previous) => ({
          ...previous,
          computeNode: detail
        }));
        setRuntimeSelectedNodeDetailRequests((previous) => ({
          ...previous,
          computeNode: { entityId: normalizedNodeId, loading: false, error: null }
        }));
        setConnectionChannel("http", "live");
      } catch (error) {
        setRuntimeSelectedNodeDetails((previous) => ({
          ...previous,
          computeNode: null
        }));
        setRuntimeSelectedNodeDetailRequests((previous) => ({
          ...previous,
          computeNode: {
            entityId: normalizedNodeId,
            loading: false,
            error: runtimeApiErrorMessage(error)
          }
        }));
        setConnectionChannel("http", "degraded");
      }
    },
    [generatedConfig, setConnectionChannel]
  );

  const refreshRuntimeExportCompare = useCallback(async (
    packageId: string,
    catalogOverride: RuntimeExportCatalogV1 | null = null
  ) => {
    const exportCatalog = catalogOverride ?? runtimeExportCatalog;
    const shouldLoadReviewReport =
      runtimeExportCatalogHasRouteComparisonReviewReport(exportCatalog, packageId);
    const shouldLoadServiceTraceReviewReport =
      runtimeExportCatalogHasServiceTraceComparisonReviewReport(
        exportCatalog,
        packageId
      );
    const shouldLoadAuditIndex =
      runtimeExportCatalogHasPackageAuditIndex(exportCatalog, packageId);
    const shouldLoadScenarioReviewBundle =
      runtimeExportCatalogHasScenarioReviewBundle(exportCatalog, packageId);
    const shouldLoadScenarioReviewChecklist =
      runtimeExportCatalogHasScenarioReviewChecklist(exportCatalog, packageId);
    const shouldLoadServiceLifecycleTrace =
      runtimeExportCatalogHasServiceLifecycleTrace(exportCatalog, packageId);
    const shouldLoadUserServiceRequestSummary =
      runtimeExportCatalogHasUserServiceRequestSummary(exportCatalog, packageId);
    setRuntimeExportComparePackageId(packageId);
    setRuntimeExportCompareLoading(true);
    setRuntimeExportReviewSummaryLoading(true);
    setRuntimeExportManifestLoading(true);
    setRuntimeExportDiagnosticsBundleLoading(true);
    setRuntimeExportServiceLifecycleTraceLoading(shouldLoadServiceLifecycleTrace);
    setRuntimeExportUserServiceRequestPageLoading(
      shouldLoadUserServiceRequestSummary
    );
    setRuntimeExportRouteDetailIndexLoading(true);
    setRuntimeExportRouteComparisonReviewReportLoading(shouldLoadReviewReport);
    setRuntimeExportServiceTraceComparisonReviewReportLoading(
      shouldLoadServiceTraceReviewReport
    );
    setRuntimeExportPackageAuditIndexLoading(shouldLoadAuditIndex);
    setRuntimeExportScenarioReviewBundleLoading(shouldLoadScenarioReviewBundle);
    setRuntimeExportScenarioReviewChecklistLoading(shouldLoadScenarioReviewChecklist);
    setRuntimeExportRestorePreflightLoading(true);
    setRuntimeExportCompareError(null);
    setRuntimeExportReviewSummaryError(null);
    setRuntimeExportManifestError(null);
    setRuntimeExportDiagnosticsBundleError(null);
    setRuntimeExportServiceLifecycleTrace(null);
    setRuntimeExportServiceTracePage(null);
    setRuntimeExportServiceTraceItem(null);
    setRuntimeExportServiceTraceItemTraceId(null);
    setRuntimeExportServiceTraceItemLoading(false);
    setRuntimeExportServiceTraceItemError(null);
    setRuntimeExportServiceLifecycleTraceError(null);
    setRuntimeExportUserServiceRequestPage(null);
    setRuntimeExportUserServiceRequestPageError(null);
    setRuntimeExportRouteDetailIndexError(null);
    setRuntimeExportRouteComparisonReviewReport(null);
    setRuntimeExportRouteComparisonReviewReportError(null);
    setRuntimeExportServiceTraceComparisonReviewReport(null);
    setRuntimeExportServiceTraceComparisonReviewReportError(null);
    setRuntimeExportPackageAuditIndex(null);
    setRuntimeExportPackageAcceptanceReport(null);
    setRuntimeExportPackageAuditIndexError(null);
    setRuntimeExportScenarioReviewBundle(null);
    setRuntimeExportScenarioReviewBundleError(null);
    setRuntimeExportScenarioReviewChecklist(null);
    setRuntimeExportScenarioReviewChecklistTemplate(null);
    setRuntimeExportScenarioReviewChecklistTemplateComparison(null);
    setRuntimeExportScenarioReviewChecklistError(null);
    setRuntimeExportRouteDetailItem(null);
    setRuntimeExportRouteDetailItemRouteId(null);
    setRuntimeExportRouteDetailItemLoading(false);
    setRuntimeExportRouteDetailItemError(null);
    setRuntimeExportRouteComparisonReviewSavePendingRouteId(null);
    setRuntimeExportRouteComparisonReviewSaveError(null);
    setRuntimeExportRouteComparisonReviewSaveReportHash(null);
    setRuntimeExportServiceTraceComparisonReviewSavePendingTraceId(null);
    setRuntimeExportServiceTraceComparisonReviewSaveError(null);
    setRuntimeExportServiceTraceComparisonReviewSaveReportHash(null);
    setRuntimeExportScenarioReviewChecklistSavePending(false);
    setRuntimeExportScenarioReviewChecklistSaveError(null);
    setRuntimeExportScenarioReviewChecklistSaveHash(null);
    setRuntimeExportRestorePreflightError(null);
    setRuntimeExportRestoreCommandError(null);
    setRuntimeExportRestoreResult(null);
    const [
      compare,
      reviewSummary,
      manifest,
      diagnosticsBundle,
      serviceTracePage,
      userServiceRequestPage,
      routeDetailPage,
      routeComparisonReviewReport,
      serviceTraceComparisonReviewReport,
      packageAuditIndex,
      packageAcceptanceReport,
      scenarioReviewBundle,
      scenarioReviewChecklist,
      scenarioReviewChecklistTemplate,
      scenarioReviewChecklistTemplateComparison,
      preflight
    ] =
      await Promise.allSettled([
        loadRuntimeExportPackageCompare(packageId),
        loadRuntimeExportReviewSummary(packageId),
        loadRuntimeExportManifest(packageId),
        loadRuntimeExportDiagnosticsBundle(packageId),
        shouldLoadServiceLifecycleTrace
          ? loadRuntimeExportServiceTracePage(packageId, 0, 5)
          : Promise.resolve(null),
        shouldLoadUserServiceRequestSummary
          ? loadRuntimeExportUserServiceRequestPage(packageId, 0, 5)
          : Promise.resolve(null),
        loadRuntimeExportRouteDetailPage(packageId, 0, 5),
        shouldLoadReviewReport
          ? loadRuntimeExportRouteComparisonReviewReportPage(packageId, 0, 5)
          : Promise.resolve(null),
        shouldLoadServiceTraceReviewReport
          ? loadRuntimeExportServiceTraceComparisonReviewReportPage(packageId, 0, 5)
          : Promise.resolve(null),
        shouldLoadAuditIndex
          ? loadRuntimeExportPackageAuditIndex(packageId)
          : Promise.resolve(null),
        shouldLoadAuditIndex
          ? loadRuntimeExportPackageAcceptanceReport(packageId)
          : Promise.resolve(null),
        shouldLoadScenarioReviewBundle
          ? loadRuntimeExportScenarioReviewBundle(packageId)
          : Promise.resolve(null),
        shouldLoadScenarioReviewChecklist
          ? loadRuntimeExportScenarioReviewChecklist(packageId)
          : Promise.resolve(null),
        shouldLoadScenarioReviewBundle
          ? loadRuntimeExportScenarioReviewChecklistTemplate(packageId)
          : Promise.resolve(null),
        shouldLoadScenarioReviewBundle
          ? loadRuntimeExportScenarioReviewChecklistTemplateComparison(packageId)
          : Promise.resolve(null),
        loadRuntimeExportRestorePreflight(packageId)
      ]);
    if (compare.status === "fulfilled") {
      setRuntimeExportCompare(compare.value);
    } else {
      setRuntimeExportCompare(null);
      setRuntimeExportCompareError(runtimeExportCompareErrorMessage(compare.reason));
    }
    if (reviewSummary.status === "fulfilled") {
      setRuntimeExportReviewSummary(reviewSummary.value);
    } else {
      setRuntimeExportReviewSummary(null);
      setRuntimeExportReviewSummaryError(
        runtimeExportReviewSummaryErrorMessage(reviewSummary.reason)
      );
    }
    if (manifest.status === "fulfilled") {
      setRuntimeExportManifest(manifest.value);
    } else {
      setRuntimeExportManifest(null);
      setRuntimeExportManifestError(runtimeExportManifestErrorMessage(manifest.reason));
    }
    if (diagnosticsBundle.status === "fulfilled") {
      setRuntimeExportDiagnosticsBundle(diagnosticsBundle.value);
    } else {
      setRuntimeExportDiagnosticsBundle(null);
      setRuntimeExportDiagnosticsBundleError(
        runtimeExportDiagnosticsBundleErrorMessage(diagnosticsBundle.reason)
      );
    }
    if (serviceTracePage.status === "fulfilled") {
      setRuntimeExportServiceTracePage(serviceTracePage.value);
    } else {
      setRuntimeExportServiceTracePage(null);
      setRuntimeExportServiceLifecycleTrace(null);
      setRuntimeExportServiceLifecycleTraceError(
        runtimeExportServiceLifecycleTraceErrorMessage(serviceTracePage.reason)
      );
    }
    if (userServiceRequestPage.status === "fulfilled") {
      setRuntimeExportUserServiceRequestPage(userServiceRequestPage.value);
    } else {
      setRuntimeExportUserServiceRequestPage(null);
      setRuntimeExportUserServiceRequestPageError(
        runtimeExportUserServiceRequestSummaryErrorMessage(
          userServiceRequestPage.reason
        )
      );
    }
    if (routeDetailPage.status === "fulfilled") {
      setRuntimeExportRouteDetailPage(routeDetailPage.value);
    } else {
      setRuntimeExportRouteDetailPage(null);
      setRuntimeExportRouteDetailIndexError(
        runtimeExportRouteDetailIndexErrorMessage(routeDetailPage.reason)
      );
    }
    if (routeComparisonReviewReport.status === "fulfilled") {
      setRuntimeExportRouteComparisonReviewReport(
        routeComparisonReviewReport.value
      );
    } else {
      setRuntimeExportRouteComparisonReviewReport(null);
      setRuntimeExportRouteComparisonReviewReportError(
        runtimeExportRouteComparisonReviewReportErrorMessage(
          routeComparisonReviewReport.reason
        )
      );
    }
    if (serviceTraceComparisonReviewReport.status === "fulfilled") {
      setRuntimeExportServiceTraceComparisonReviewReport(
        serviceTraceComparisonReviewReport.value
      );
    } else {
      setRuntimeExportServiceTraceComparisonReviewReport(null);
      setRuntimeExportServiceTraceComparisonReviewReportError(
        runtimeExportServiceTraceComparisonReviewReportErrorMessage(
          serviceTraceComparisonReviewReport.reason
        )
      );
    }
    if (packageAuditIndex.status === "fulfilled") {
      setRuntimeExportPackageAuditIndex(packageAuditIndex.value);
    } else {
      setRuntimeExportPackageAuditIndex(null);
      setRuntimeExportPackageAuditIndexError(
        runtimeExportPackageAuditIndexErrorMessage(packageAuditIndex.reason)
      );
    }
    if (packageAcceptanceReport.status === "fulfilled") {
      setRuntimeExportPackageAcceptanceReport(packageAcceptanceReport.value);
    } else {
      setRuntimeExportPackageAcceptanceReport(null);
    }
    if (scenarioReviewBundle.status === "fulfilled") {
      setRuntimeExportScenarioReviewBundle(scenarioReviewBundle.value);
    } else {
      setRuntimeExportScenarioReviewBundle(null);
      setRuntimeExportScenarioReviewBundleError(
        runtimeExportScenarioReviewBundleErrorMessage(scenarioReviewBundle.reason)
      );
    }
    if (scenarioReviewChecklist.status === "fulfilled") {
      setRuntimeExportScenarioReviewChecklist(scenarioReviewChecklist.value);
    } else {
      setRuntimeExportScenarioReviewChecklist(null);
      setRuntimeExportScenarioReviewChecklistError(
        runtimeExportScenarioReviewChecklistErrorMessage(
          scenarioReviewChecklist.reason
        )
      );
    }
    if (scenarioReviewChecklistTemplate.status === "fulfilled") {
      setRuntimeExportScenarioReviewChecklistTemplate(
        scenarioReviewChecklistTemplate.value
      );
    } else {
      setRuntimeExportScenarioReviewChecklistTemplate(null);
    }
    if (scenarioReviewChecklistTemplateComparison.status === "fulfilled") {
      setRuntimeExportScenarioReviewChecklistTemplateComparison(
        scenarioReviewChecklistTemplateComparison.value
      );
    } else {
      setRuntimeExportScenarioReviewChecklistTemplateComparison(null);
    }
    if (preflight.status === "fulfilled") {
      setRuntimeExportRestorePreflight(preflight.value);
    } else {
      setRuntimeExportRestorePreflight(null);
      setRuntimeExportRestorePreflightError(
        runtimeExportRestorePreflightErrorMessage(preflight.reason)
      );
    }
    setRuntimeExportCompareLoading(false);
    setRuntimeExportReviewSummaryLoading(false);
    setRuntimeExportManifestLoading(false);
    setRuntimeExportDiagnosticsBundleLoading(false);
    setRuntimeExportServiceLifecycleTraceLoading(false);
    setRuntimeExportUserServiceRequestPageLoading(false);
    setRuntimeExportRouteDetailIndexLoading(false);
    setRuntimeExportRouteComparisonReviewReportLoading(false);
    setRuntimeExportServiceTraceComparisonReviewReportLoading(false);
    setRuntimeExportPackageAuditIndexLoading(false);
    setRuntimeExportScenarioReviewBundleLoading(false);
    setRuntimeExportScenarioReviewChecklistLoading(false);
    setRuntimeExportRestorePreflightLoading(false);
  }, [runtimeExportCatalog]);

  const refreshRuntimeExportRouteDetailPage = useCallback(
    async (request: DataPanelExportRouteDetailPageRequest) => {
      const packageId = runtimeExportComparePackageId;
      if (packageId === null) {
        return;
      }
      const cursor = Math.max(0, request.cursor);
      const limit = request.limit ?? 5;
      const filters: RuntimeDetailQueryFilters = request.filters ?? {};
      setRuntimeExportRouteDetailIndexLoading(true);
      setRuntimeExportRouteDetailIndexError(null);
      try {
        setRuntimeExportRouteDetailPage(
          await loadRuntimeExportRouteDetailPage(packageId, cursor, limit, filters)
        );
      } catch (error) {
        setRuntimeExportRouteDetailPage(null);
        setRuntimeExportRouteDetailIndexError(
          runtimeExportRouteDetailIndexErrorMessage(error)
        );
      } finally {
        setRuntimeExportRouteDetailIndexLoading(false);
      }
    },
    [runtimeExportComparePackageId]
  );

  const refreshRuntimeExportServiceTracePage = useCallback(
    async (request: DataPanelExportServiceTracePageRequest) => {
      const packageId = runtimeExportComparePackageId;
      if (packageId === null) {
        return;
      }
      const cursor = Math.max(0, request.cursor);
      const limit = request.limit ?? 5;
      const filters: RuntimeDetailQueryFilters = request.filters ?? {};
      setRuntimeExportServiceLifecycleTraceLoading(true);
      setRuntimeExportServiceLifecycleTraceError(null);
      try {
        setRuntimeExportServiceTracePage(
          await loadRuntimeExportServiceTracePage(packageId, cursor, limit, filters)
        );
      } catch (error) {
        setRuntimeExportServiceTracePage(null);
        setRuntimeExportServiceLifecycleTraceError(
          runtimeExportServiceLifecycleTraceErrorMessage(error)
        );
      } finally {
        setRuntimeExportServiceLifecycleTraceLoading(false);
      }
    },
    [runtimeExportComparePackageId]
  );

  const refreshRuntimeExportRouteComparisonReviewReportPage = useCallback(
    async (request: DataPanelExportRouteComparisonReviewReportPageRequest) => {
      const packageId = runtimeExportComparePackageId;
      if (packageId === null) {
        return;
      }
      const cursor = Math.max(0, request.cursor);
      const limit = request.limit ?? 5;
      const filters = request.filters ?? {};
      setRuntimeExportRouteComparisonReviewReportLoading(true);
      setRuntimeExportRouteComparisonReviewReportError(null);
      try {
        setRuntimeExportRouteComparisonReviewReport(
          await loadRuntimeExportRouteComparisonReviewReportPage(
            packageId,
            cursor,
            limit,
            filters
          )
        );
      } catch (error) {
        setRuntimeExportRouteComparisonReviewReport(null);
        setRuntimeExportRouteComparisonReviewReportError(
          runtimeExportRouteComparisonReviewReportErrorMessage(error)
        );
      } finally {
        setRuntimeExportRouteComparisonReviewReportLoading(false);
      }
    },
    [runtimeExportComparePackageId]
  );

  const refreshRuntimeExportServiceTraceComparisonReviewReportPage = useCallback(
    async (
      request: DataPanelExportServiceTraceComparisonReviewReportPageRequest
    ) => {
      const packageId = runtimeExportComparePackageId;
      if (packageId === null) {
        return;
      }
      const cursor = Math.max(0, request.cursor);
      const limit = request.limit ?? 5;
      const filters = request.filters ?? {};
      setRuntimeExportServiceTraceComparisonReviewReportLoading(true);
      setRuntimeExportServiceTraceComparisonReviewReportError(null);
      try {
        setRuntimeExportServiceTraceComparisonReviewReport(
          await loadRuntimeExportServiceTraceComparisonReviewReportPage(
            packageId,
            cursor,
            limit,
            filters
          )
        );
      } catch (error) {
        setRuntimeExportServiceTraceComparisonReviewReport(null);
        setRuntimeExportServiceTraceComparisonReviewReportError(
          runtimeExportServiceTraceComparisonReviewReportErrorMessage(error)
        );
      } finally {
        setRuntimeExportServiceTraceComparisonReviewReportLoading(false);
      }
    },
    [runtimeExportComparePackageId]
  );

  const refreshRuntimeExportServiceTraceItem = useCallback(
    async (traceId: string | null) => {
      const packageId = runtimeExportComparePackageId;
      const normalizedTraceId = traceId?.trim() ?? "";
      if (packageId === null || normalizedTraceId.length === 0) {
        setRuntimeExportServiceTraceItem(null);
        setRuntimeExportServiceTraceItemTraceId(null);
        setRuntimeExportServiceTraceItemLoading(false);
        setRuntimeExportServiceTraceItemError(null);
        return;
      }
      setRuntimeExportServiceTraceItemTraceId(normalizedTraceId);
      setRuntimeExportServiceTraceItem(null);
      setRuntimeExportServiceTraceItemLoading(true);
      setRuntimeExportServiceTraceItemError(null);
      try {
        setRuntimeExportServiceTraceItem(
          await loadRuntimeExportServiceTraceItem(packageId, normalizedTraceId)
        );
      } catch (error) {
        setRuntimeExportServiceTraceItem(null);
        setRuntimeExportServiceTraceItemError(
          runtimeExportServiceLifecycleTraceErrorMessage(error)
        );
      } finally {
        setRuntimeExportServiceTraceItemLoading(false);
      }
    },
    [runtimeExportComparePackageId]
  );

  const refreshRuntimeExportUserServiceRequestPage = useCallback(
    async (request: DataPanelExportUserServiceRequestPageRequest) => {
      const packageId = runtimeExportComparePackageId;
      if (packageId === null) {
        return;
      }
      const cursor = Math.max(0, request.cursor);
      const limit = request.limit ?? 5;
      const filters: RuntimeDetailQueryFilters = request.filters ?? {};
      setRuntimeExportUserServiceRequestPageLoading(true);
      setRuntimeExportUserServiceRequestPageError(null);
      try {
        setRuntimeExportUserServiceRequestPage(
          await loadRuntimeExportUserServiceRequestPage(
            packageId,
            cursor,
            limit,
            filters
          )
        );
      } catch (error) {
        setRuntimeExportUserServiceRequestPage(null);
        setRuntimeExportUserServiceRequestPageError(
          runtimeExportUserServiceRequestSummaryErrorMessage(error)
        );
      } finally {
        setRuntimeExportUserServiceRequestPageLoading(false);
      }
    },
    [runtimeExportComparePackageId]
  );

  const refreshRuntimeExportRouteDetailItem = useCallback(
    async (routeId: string | null) => {
      const packageId = runtimeExportComparePackageId;
      const normalizedRouteId = routeId?.trim() ?? "";
      if (packageId === null || normalizedRouteId.length === 0) {
        setRuntimeExportRouteDetailItem(null);
        setRuntimeExportRouteDetailItemRouteId(null);
        setRuntimeExportRouteDetailItemLoading(false);
        setRuntimeExportRouteDetailItemError(null);
        setRuntimeExportRouteComparisonReviewSavePendingRouteId(null);
        setRuntimeExportRouteComparisonReviewSaveError(null);
        setRuntimeExportRouteComparisonReviewSaveReportHash(null);
        return;
      }
      setRuntimeExportRouteDetailItemRouteId(normalizedRouteId);
      setRuntimeExportRouteDetailItem(null);
      setRuntimeExportRouteDetailItemLoading(true);
      setRuntimeExportRouteDetailItemError(null);
      setRuntimeExportRouteComparisonReviewSaveError(null);
      setRuntimeExportRouteComparisonReviewSaveReportHash(null);
      try {
        setRuntimeExportRouteDetailItem(
          await loadRuntimeExportRouteDetailItem(packageId, normalizedRouteId)
        );
      } catch (error) {
        setRuntimeExportRouteDetailItem(null);
        setRuntimeExportRouteDetailItemError(
          runtimeExportRouteDetailItemErrorMessage(error)
        );
      } finally {
        setRuntimeExportRouteDetailItemLoading(false);
      }
    },
    [runtimeExportComparePackageId]
  );

  const refreshRuntimeExportCatalog = useCallback(async () => {
    try {
      const catalog = await loadRuntimeExportCatalog();
      setRuntimeExportCatalog(catalog);
      const packageId = selectRuntimeExportComparePackageId(
        catalog,
        runtimeExportComparePackageId
      );
      if (packageId === null) {
        setRuntimeExportCompare(null);
        setRuntimeExportReviewSummary(null);
        setRuntimeExportManifest(null);
        setRuntimeExportDiagnosticsBundle(null);
        setRuntimeExportServiceLifecycleTrace(null);
        setRuntimeExportServiceTracePage(null);
        setRuntimeExportServiceTraceItem(null);
        setRuntimeExportServiceTraceItemTraceId(null);
        setRuntimeExportServiceTraceItemLoading(false);
        setRuntimeExportServiceTraceItemError(null);
        setRuntimeExportUserServiceRequestPage(null);
        setRuntimeExportRouteDetailPage(null);
        setRuntimeExportRouteDetailItem(null);
        setRuntimeExportRouteDetailItemRouteId(null);
        setRuntimeExportRouteDetailItemLoading(false);
        setRuntimeExportRouteDetailItemError(null);
        setRuntimeExportRouteComparisonReviewReport(null);
        setRuntimeExportRouteComparisonReviewReportLoading(false);
        setRuntimeExportRouteComparisonReviewReportError(null);
        setRuntimeExportServiceTraceComparisonReviewReport(null);
        setRuntimeExportServiceTraceComparisonReviewReportLoading(false);
        setRuntimeExportServiceTraceComparisonReviewReportError(null);
        setRuntimeExportPackageAuditIndex(null);
        setRuntimeExportPackageAuditIndexLoading(false);
        setRuntimeExportPackageAuditIndexError(null);
        setRuntimeExportScenarioReviewBundle(null);
        setRuntimeExportScenarioReviewBundleLoading(false);
        setRuntimeExportScenarioReviewBundleError(null);
        setRuntimeExportScenarioReviewChecklist(null);
        setRuntimeExportScenarioReviewChecklistLoading(false);
        setRuntimeExportScenarioReviewChecklistError(null);
        setRuntimeExportRouteComparisonReviewSavePendingRouteId(null);
        setRuntimeExportRouteComparisonReviewSaveError(null);
        setRuntimeExportRouteComparisonReviewSaveReportHash(null);
        setRuntimeExportServiceTraceComparisonReviewSavePendingTraceId(null);
        setRuntimeExportServiceTraceComparisonReviewSaveError(null);
        setRuntimeExportServiceTraceComparisonReviewSaveReportHash(null);
        setRuntimeExportScenarioReviewChecklistSavePending(false);
        setRuntimeExportScenarioReviewChecklistSaveError(null);
        setRuntimeExportScenarioReviewChecklistSaveHash(null);
        setRuntimeExportRestorePreflight(null);
        setRuntimeExportComparePackageId(null);
        setRuntimeExportCompareLoading(false);
        setRuntimeExportReviewSummaryLoading(false);
        setRuntimeExportManifestLoading(false);
        setRuntimeExportDiagnosticsBundleLoading(false);
        setRuntimeExportServiceLifecycleTraceLoading(false);
        setRuntimeExportUserServiceRequestPageLoading(false);
        setRuntimeExportRouteDetailIndexLoading(false);
        setRuntimeExportRouteComparisonReviewReportLoading(false);
        setRuntimeExportServiceTraceComparisonReviewReportLoading(false);
        setRuntimeExportPackageAuditIndexLoading(false);
        setRuntimeExportScenarioReviewBundleLoading(false);
        setRuntimeExportRestorePreflightLoading(false);
        setRuntimeExportCompareError(null);
        setRuntimeExportReviewSummaryError(null);
        setRuntimeExportManifestError(null);
        setRuntimeExportDiagnosticsBundleError(null);
        setRuntimeExportServiceLifecycleTraceError(null);
        setRuntimeExportServiceTraceItemError(null);
        setRuntimeExportUserServiceRequestPageError(null);
        setRuntimeExportRouteDetailIndexError(null);
        setRuntimeExportRouteComparisonReviewReportError(null);
        setRuntimeExportServiceTraceComparisonReviewReportError(null);
        setRuntimeExportPackageAuditIndexError(null);
        setRuntimeExportScenarioReviewBundleError(null);
        setRuntimeExportScenarioReviewChecklistError(null);
        setRuntimeExportRestorePreflightError(null);
        setRuntimeExportRestoreCommandPendingPackageId(null);
        setRuntimeExportRestoreCommandError(null);
        setRuntimeExportRestoreResult(null);
        return;
      }
      void refreshRuntimeExportCompare(packageId, catalog);
    } catch {
      setRuntimeExportCatalog(null);
      setRuntimeExportCompare(null);
      setRuntimeExportReviewSummary(null);
      setRuntimeExportManifest(null);
      setRuntimeExportDiagnosticsBundle(null);
      setRuntimeExportServiceLifecycleTrace(null);
      setRuntimeExportServiceTracePage(null);
      setRuntimeExportServiceTraceItem(null);
      setRuntimeExportServiceTraceItemTraceId(null);
      setRuntimeExportUserServiceRequestPage(null);
      setRuntimeExportRouteDetailPage(null);
      setRuntimeExportRouteComparisonReviewReport(null);
      setRuntimeExportServiceTraceComparisonReviewReport(null);
      setRuntimeExportPackageAuditIndex(null);
      setRuntimeExportScenarioReviewBundle(null);
      setRuntimeExportScenarioReviewChecklist(null);
      setRuntimeExportRestorePreflight(null);
      setRuntimeExportComparePackageId(null);
      setRuntimeExportRouteComparisonReviewSavePendingRouteId(null);
      setRuntimeExportRouteComparisonReviewSaveError(null);
      setRuntimeExportRouteComparisonReviewSaveReportHash(null);
      setRuntimeExportServiceTraceComparisonReviewSavePendingTraceId(null);
      setRuntimeExportServiceTraceComparisonReviewSaveError(null);
      setRuntimeExportServiceTraceComparisonReviewSaveReportHash(null);
      setRuntimeExportScenarioReviewChecklistSavePending(false);
      setRuntimeExportScenarioReviewChecklistSaveError(null);
      setRuntimeExportScenarioReviewChecklistSaveHash(null);
      setRuntimeExportCompareLoading(false);
      setRuntimeExportReviewSummaryLoading(false);
      setRuntimeExportManifestLoading(false);
      setRuntimeExportDiagnosticsBundleLoading(false);
      setRuntimeExportServiceLifecycleTraceLoading(false);
      setRuntimeExportServiceTraceItemLoading(false);
      setRuntimeExportUserServiceRequestPageLoading(false);
      setRuntimeExportRouteDetailIndexLoading(false);
      setRuntimeExportRouteComparisonReviewReportLoading(false);
      setRuntimeExportServiceTraceComparisonReviewReportLoading(false);
      setRuntimeExportPackageAuditIndexLoading(false);
      setRuntimeExportScenarioReviewBundleLoading(false);
      setRuntimeExportScenarioReviewChecklistLoading(false);
      setRuntimeExportRestorePreflightLoading(false);
      setRuntimeExportCompareError(null);
      setRuntimeExportReviewSummaryError(null);
      setRuntimeExportManifestError(null);
      setRuntimeExportDiagnosticsBundleError(null);
      setRuntimeExportServiceLifecycleTraceError(null);
      setRuntimeExportServiceTraceItemError(null);
      setRuntimeExportUserServiceRequestPageError(null);
      setRuntimeExportRouteDetailIndexError(null);
      setRuntimeExportRouteComparisonReviewReportError(null);
      setRuntimeExportServiceTraceComparisonReviewReportError(null);
      setRuntimeExportPackageAuditIndexError(null);
      setRuntimeExportScenarioReviewBundleError(null);
      setRuntimeExportScenarioReviewChecklistError(null);
      setRuntimeExportRestorePreflightError(null);
      setRuntimeExportRestoreCommandPendingPackageId(null);
      setRuntimeExportRestoreCommandError(null);
      setRuntimeExportRestoreResult(null);
    }
  }, [refreshRuntimeExportCompare, runtimeExportComparePackageId]);

  const saveRuntimeExportRouteComparisonReview = useCallback(
    async (request: DataPanelExportRouteComparisonReviewSaveRequest) => {
      const routeId = String(request.record.route_id ?? "").trim();
      if (!request.packageId.trim() || routeId.length === 0) {
        return;
      }
      setRuntimeExportRouteComparisonReviewSavePendingRouteId(routeId);
      setRuntimeExportRouteComparisonReviewSaveError(null);
      setRuntimeExportRouteComparisonReviewSaveReportHash(null);
      setRuntimeExportRouteComparisonReviewReportLoading(true);
      setRuntimeExportRouteComparisonReviewReportError(null);
      setRuntimeExportPackageAuditIndexLoading(true);
      setRuntimeExportPackageAuditIndexError(null);
      try {
        const report = await saveRuntimeExportRouteComparisonReviewReport(
          request.packageId,
          {
            records: [request.record]
          }
        );
        const [catalog, auditIndex] = await Promise.allSettled([
          loadRuntimeExportCatalog(),
          loadRuntimeExportPackageAuditIndex(request.packageId)
        ]);
        if (catalog.status === "fulfilled") {
          setRuntimeExportCatalog(catalog.value);
        }
        if (auditIndex.status === "fulfilled") {
          setRuntimeExportPackageAuditIndex(auditIndex.value);
        } else {
          setRuntimeExportPackageAuditIndex(null);
          setRuntimeExportPackageAuditIndexError(
            runtimeExportPackageAuditIndexErrorMessage(auditIndex.reason)
          );
        }
        const page = await loadRuntimeExportRouteComparisonReviewReportPage(
          request.packageId,
          0,
          5
        );
        setRuntimeExportRouteComparisonReviewReport(page);
        setRuntimeExportRouteComparisonReviewSaveReportHash(report.report_hash);
      } catch (error) {
        setRuntimeExportRouteComparisonReviewReport(null);
        setRuntimeExportPackageAuditIndex(null);
        setRuntimeExportRouteComparisonReviewReportError(
          runtimeExportRouteComparisonReviewReportErrorMessage(error)
        );
        setRuntimeExportRouteComparisonReviewSaveError(
          runtimeExportRouteComparisonReviewSaveErrorMessage(error)
        );
      } finally {
        setRuntimeExportRouteComparisonReviewSavePendingRouteId(null);
        setRuntimeExportRouteComparisonReviewReportLoading(false);
        setRuntimeExportPackageAuditIndexLoading(false);
      }
    },
    []
  );

  const saveRuntimeExportServiceTraceComparisonReview = useCallback(
    async (request: DataPanelExportServiceTraceComparisonReviewSaveRequest) => {
      const traceId = String(request.record.trace_id ?? "").trim();
      if (!request.packageId.trim() || traceId.length === 0) {
        return;
      }
      setRuntimeExportServiceTraceComparisonReviewSavePendingTraceId(traceId);
      setRuntimeExportServiceTraceComparisonReviewSaveError(null);
      setRuntimeExportServiceTraceComparisonReviewSaveReportHash(null);
      setRuntimeExportServiceTraceComparisonReviewReportLoading(true);
      setRuntimeExportServiceTraceComparisonReviewReportError(null);
      setRuntimeExportPackageAuditIndexLoading(true);
      setRuntimeExportPackageAuditIndexError(null);
      try {
        const report = await saveRuntimeExportServiceTraceComparisonReviewReport(
          request.packageId,
          {
            records: [request.record]
          }
        );
        const [catalog, auditIndex] = await Promise.allSettled([
          loadRuntimeExportCatalog(),
          loadRuntimeExportPackageAuditIndex(request.packageId)
        ]);
        if (catalog.status === "fulfilled") {
          setRuntimeExportCatalog(catalog.value);
        }
        if (auditIndex.status === "fulfilled") {
          setRuntimeExportPackageAuditIndex(auditIndex.value);
        } else {
          setRuntimeExportPackageAuditIndex(null);
          setRuntimeExportPackageAuditIndexError(
            runtimeExportPackageAuditIndexErrorMessage(auditIndex.reason)
          );
        }
        const page = await loadRuntimeExportServiceTraceComparisonReviewReportPage(
          request.packageId,
          0,
          5
        );
        setRuntimeExportServiceTraceComparisonReviewReport(page);
        setRuntimeExportServiceTraceComparisonReviewSaveReportHash(
          report.report_hash
        );
      } catch (error) {
        setRuntimeExportServiceTraceComparisonReviewReport(null);
        setRuntimeExportPackageAuditIndex(null);
        setRuntimeExportServiceTraceComparisonReviewReportError(
          runtimeExportServiceTraceComparisonReviewReportErrorMessage(error)
        );
        setRuntimeExportServiceTraceComparisonReviewSaveError(
          runtimeExportServiceTraceComparisonReviewSaveErrorMessage(error)
        );
      } finally {
        setRuntimeExportServiceTraceComparisonReviewSavePendingTraceId(null);
        setRuntimeExportServiceTraceComparisonReviewReportLoading(false);
        setRuntimeExportPackageAuditIndexLoading(false);
      }
    },
    []
  );

  const saveRuntimeExportScenarioReviewChecklist = useCallback(
    async (request: DataPanelExportScenarioReviewChecklistSaveRequest) => {
      if (!request.packageId.trim() || request.records.length === 0) {
        return;
      }
      setRuntimeExportScenarioReviewChecklistSavePending(true);
      setRuntimeExportScenarioReviewChecklistSaveError(null);
      setRuntimeExportScenarioReviewChecklistSaveHash(null);
      setRuntimeExportScenarioReviewChecklistLoading(true);
      setRuntimeExportScenarioReviewChecklistError(null);
      setRuntimeExportPackageAuditIndexLoading(true);
      setRuntimeExportPackageAuditIndexError(null);
      try {
        const checklist = await saveRuntimeExportScenarioReviewChecklistArtifact(
          request.packageId,
          {
            records: request.records
          }
        );
        const [catalog, auditIndex] = await Promise.allSettled([
          loadRuntimeExportCatalog(),
          loadRuntimeExportPackageAuditIndex(request.packageId)
        ]);
        if (catalog.status === "fulfilled") {
          setRuntimeExportCatalog(catalog.value);
        }
        if (auditIndex.status === "fulfilled") {
          setRuntimeExportPackageAuditIndex(auditIndex.value);
        } else {
          setRuntimeExportPackageAuditIndex(null);
          setRuntimeExportPackageAuditIndexError(
            runtimeExportPackageAuditIndexErrorMessage(auditIndex.reason)
          );
        }
        setRuntimeExportScenarioReviewChecklist(checklist);
        setRuntimeExportScenarioReviewChecklistSaveHash(checklist.checklist_hash);
      } catch (error) {
        setRuntimeExportScenarioReviewChecklist(null);
        setRuntimeExportPackageAuditIndex(null);
        setRuntimeExportScenarioReviewChecklistError(
          runtimeExportScenarioReviewChecklistErrorMessage(error)
        );
        setRuntimeExportScenarioReviewChecklistSaveError(
          runtimeExportScenarioReviewChecklistSaveErrorMessage(error)
        );
      } finally {
        setRuntimeExportScenarioReviewChecklistSavePending(false);
        setRuntimeExportScenarioReviewChecklistLoading(false);
        setRuntimeExportPackageAuditIndexLoading(false);
      }
    },
    []
  );

  const refreshUserConfigurationContract = useCallback(async () => {
    setUserConfigurationContractLoading(true);
    setUserConfigurationContractError(null);
    const [schema, templates, reference, exported] = await Promise.allSettled([
      loadUserConfigurationSchema(),
      loadUserConfigurationTemplates(),
      loadUserConfigurationReference(),
      loadUserConfigurationExport()
    ]);
    if (schema.status === "fulfilled") {
      setUserConfigurationSchema(schema.value);
    }
    if (templates.status === "fulfilled") {
      setUserConfigurationTemplates(templates.value);
    }
    if (reference.status === "fulfilled") {
      setUserConfigurationReference(reference.value);
    }
    if (exported.status === "fulfilled") {
      setUserConfigurationExport(exported.value);
    }
    const failures = [schema, templates, reference, exported].filter(
      (item) => item.status === "rejected"
    );
    if (failures.length === 4) {
      setUserConfigurationSchema(null);
      setUserConfigurationTemplates(null);
      setUserConfigurationReference(null);
      setUserConfigurationExport(null);
    }
    if (failures.length > 0) {
      const firstFailure = failures[0];
      if (firstFailure.status === "rejected") {
        setUserConfigurationContractError(userConfigurationContractErrorMessage(firstFailure.reason));
      }
    }
    setUserConfigurationContractLoading(false);
  }, []);

  const validateUserConfiguration = useCallback(
    async (candidate: unknown): Promise<UserConfigurationValidationReportV1> => {
      return validateUserConfigurationCandidate(candidate);
    },
    []
  );
  const validateUserConfigurationText = useCallback(
    async (
      text: string,
      format: "auto" | "json" | "yaml"
    ): Promise<UserConfigurationValidationReportV1> => {
      return validateUserConfigurationTextCandidate(text, format);
    },
    []
  );

  const loadControlState = useCallback(async () => {
    const [scenario, runtime, visibleSnapshot] = await Promise.all([
      loadScenarioConfig(),
      loadRuntimeState(),
      loadMetricsSnapshot()
    ]);
    const effectiveScenario = scenarioWithRuntimeConfig(scenario, runtime.config);
    setScenarioConfig(effectiveScenario);
    setGeneratedConfig(runtime.generated_config ?? null);
    setRuntimeStatus((previous) => ({
      ...previous,
      ...effectiveScenario.runtime,
      ...runtime.status
    }));
    snapshotEngine.applyScenarioConfig(effectiveScenario);
    snapshotEngine.applySnapshot(visibleSnapshot);
    snapshotEngine.publishNow();
    setConnectionChannel("http", "live");
    return { scenario: effectiveScenario, runtime };
  }, [
    setConnectionChannel,
    snapshotEngine
  ]);

  const handleRuntimeApiError = useCallback((error: unknown) => {
    setConnectionState("degraded");
    setConnectionChannel("http", "degraded");
    setControlError(runtimeApiErrorMessage(error));
  }, [setConnectionChannel]);

  const startStreams = useCallback(
    (
      scenario: ScenarioConfig | null,
      options: { resetBeforeConnect?: boolean } = {}
    ) => {
      closeStreams();
      if (options.resetBeforeConnect ?? true) {
        resetWorld(scenario);
      }
      const throttleLayer = new EventThrottleLayer(
        (events) => {
          snapshotEngine.applyEvents(events);
        },
        {
          flushIntervalMs: 20,
          maxEventsPerFlush: 10_000,
          dropRedundantUpdates: true
        }
      );
      const router = new EventRouter(snapshotEngine, { throttleLayer });
      setConnectionChannel("events", "connecting");
      setConnectionChannel("state", "connecting");
      const client = new WebSocketStreamClient(router, {
        batchSize: 500,
        flushIntervalMs: 40,
        stateStreamEnabled: true,
        onConnectionOpen: (channel) => {
          setConnectionChannel(channel, "live");
        },
        onConnectionIssue: (issue) => {
          setConnectionState("degraded");
          setConnectionChannel(issue.channel, "degraded");
          setControlError(runtimeWebSocketErrorMessage(issue.channel));
        },
        onCursorAdvance: (advance) => {
          setStreamConsumerCursors((previous) => ({
            ...previous,
            [advance.channel]: advance.nextCursor
          }));
        }
      });
      streamRouterRef.current = router;
      streamClientRef.current = client;
      client.connect();
    },
    [closeStreams, resetWorld, setConnectionChannel, snapshotEngine]
  );

  const controlClient = useMemo(
    () =>
      new ControlChannelClient({
        httpFallbackUrl: "/control",
        onMessage: (message) => {
          handleControlMessage(message, setRuntimeStatus);
          handleGeneratedConfig(message, setGeneratedConfig);
          if (message.ok === false) {
            if (message.command === "RESTORE_EXPORT_PACKAGE") {
              setRuntimeExportRestoreCommandPendingPackageId(null);
              setRuntimeExportRestoreCommandError(controlErrorMessage(message.error));
            }
            setControlError(controlErrorMessage(message.error));
            return;
          }
          if (message.ok === true) {
            setControlError(null);
            if (message.command === "RESTORE_EXPORT_PACKAGE") {
              setRuntimeExportRestoreCommandPendingPackageId(null);
              setRuntimeExportRestoreCommandError(null);
              if (message.restore_result !== undefined) {
                setRuntimeExportRestoreResult(message.restore_result);
              }
              if (message.restore_preflight !== undefined) {
                setRuntimeExportRestorePreflight(message.restore_preflight);
              }
              closeStreams();
              loadControlState()
                .then(({ scenario }) => resetWorld(scenario))
                .catch(handleRuntimeApiError);
              return;
            }
          }
          if (
            message.type === "RUNTIME_STATUS" &&
            runtimeStatusRequiresStreams(message.status) &&
            streamClientRef.current === null
          ) {
            loadControlState()
              .then(({ scenario }) =>
                startStreams(scenario, {
                  resetBeforeConnect: shouldResetWorldBeforeStreamConnect(
                    "ATTACH",
                    snapshotEngine.getSnapshot().event_count
                  )
                })
              )
              .catch(handleRuntimeApiError);
            return;
          }
          if (message.ok === true && message.type === "CONTROL_ACK") {
            const action = message.status?.last_action;
            if (action === "START") {
              loadControlState()
                .then(({ scenario }) =>
                  startStreams(scenario, {
                    resetBeforeConnect: shouldResetWorldBeforeStreamConnect(
                      "START",
                      snapshotEngine.getSnapshot().event_count
                    )
                  })
                )
                .catch(handleRuntimeApiError);
              return;
            }
            if (action === "RESUME") {
              loadControlState()
                .then(({ scenario }) => startStreams(scenario, { resetBeforeConnect: false }))
                .catch(handleRuntimeApiError);
              return;
            }
            if (action === "STOP" || action === "PAUSE") {
              closeStreams();
              return;
            }
            if (action === "RESET" || action === "INITIALIZE" || action === "CONFIG_UPDATE") {
              closeStreams();
              loadControlState()
                .then(({ scenario }) => resetWorld(scenario))
                .catch(handleRuntimeApiError);
            }
          }
        },
        onConnectionOpen: () => {
          setConnectionChannel("control", "live");
        },
        onConnectionIssue: () => {
          setConnectionState("degraded");
          setConnectionChannel("control", "degraded");
          setControlError(runtimeWebSocketErrorMessage("control"));
        }
      }),
    [
      closeStreams,
      handleRuntimeApiError,
      loadControlState,
      resetWorld,
      setConnectionChannel,
      snapshotEngine,
      startStreams
    ]
  );

  const applyValidatedUserConfiguration = useCallback(
    (normalizedConfig: Record<string, unknown>) => {
      setControlError(null);
      setRuntimeStatus((previous) => ({
        ...previous,
        last_action: "CONFIG_UPDATE_PENDING"
      }));
      controlClient.sendConfigUpdate(normalizedConfig);
    },
    [controlClient]
  );

  useEffect(() => {
    controlClient.connect();
    return () => controlClient.close();
  }, [controlClient]);

  useEffect(() => {
    setRuntimeProgressAnchor((previous) =>
      nextRuntimeProgressAnchor(previous, snapshot.last_sim_time, runtimeStatus, Date.now())
    );
  }, [runtimeStatus, snapshot.last_sim_time]);

  useEffect(() => {
    if (!runtimeStatusIsProgressing(runtimeStatus)) {
      setRuntimeProgressNowMs(Date.now());
      return;
    }
    const timer = window.setInterval(() => {
      setRuntimeProgressNowMs(Date.now());
    }, RUNTIME_PROGRESS_TICK_MS);
    return () => window.clearInterval(timer);
  }, [runtimeStatus]);

  useEffect(() => {
    if (!runtimeStatusRequiresStreams(runtimeStatus)) {
      return;
    }
    let closed = false;
    const refreshStatus = async () => {
      try {
        const runtime = await loadRuntimeState();
        if (closed) {
          return;
        }
        setRuntimeStatus((previous) => ({
          ...previous,
          ...runtime.status
        }));
        if (runtime.generated_config !== undefined) {
          setGeneratedConfig(runtime.generated_config);
        }
      } catch (error) {
        if (!closed) {
          handleRuntimeApiError(error);
        }
      }
    };
    const timer = window.setInterval(refreshStatus, RUNTIME_STATUS_POLL_MS);
    void refreshStatus();
    return () => {
      closed = true;
      window.clearInterval(timer);
    };
  }, [
    handleRuntimeApiError,
    runtimeStatus.status,
    runtimeStatus.lifecycle_state
  ]);

  useEffect(() => {
    if (surface !== "dashboard" || !advancedDashboardVisible) {
      return;
    }
    let closed = false;
    const refreshDetails = () => {
      if (!closed) {
        void refreshRuntimeDetails(generatedConfig);
      }
    };
    refreshDetails();
    const timer = window.setInterval(refreshDetails, 1000);
    return () => {
      closed = true;
      window.clearInterval(timer);
    };
  }, [advancedDashboardVisible, generatedConfig, refreshRuntimeDetails, surface]);

  useEffect(() => {
    if (surface !== "dashboard" || !advancedDashboardVisible) {
      return;
    }
    let closed = false;
    const refreshCatalog = () => {
      if (!closed) {
        void refreshRuntimeExportCatalog();
      }
    };
    refreshCatalog();
    const timer = window.setInterval(refreshCatalog, RUNTIME_EXPORT_CATALOG_POLL_MS);
    return () => {
      closed = true;
      window.clearInterval(timer);
    };
  }, [advancedDashboardVisible, refreshRuntimeExportCatalog, surface]);

  useEffect(() => {
    if (surface !== "dashboard" || !advancedDashboardVisible) {
      return;
    }
    let closed = false;
    const refreshContract = () => {
      if (!closed) {
        void refreshUserConfigurationContract();
      }
    };
    refreshContract();
    const timer = window.setInterval(
      refreshContract,
      USER_CONFIGURATION_CONTRACT_POLL_MS
    );
    return () => {
      closed = true;
      window.clearInterval(timer);
    };
  }, [advancedDashboardVisible, refreshUserConfigurationContract, surface]);

  useEffect(() => {
    let closed = false;
    loadControlState()
      .then(({ scenario, runtime }) => {
        if (closed) {
          return;
        }
        if (runtimeStatusRequiresStreams(runtime.status)) {
          startStreams(scenario, {
            resetBeforeConnect: shouldResetWorldBeforeStreamConnect(
              "ATTACH",
              snapshotEngine.getSnapshot().event_count
            )
          });
        } else {
          resetWorld(scenario);
        }
        setConnectionState("live");
        setControlError(null);
      })
      .catch((error) => {
        if (!closed) {
          handleRuntimeApiError(error);
        }
      });

    return () => {
      closed = true;
      closeStreams();
    };
  }, [closeStreams, handleRuntimeApiError, loadControlState, resetWorld, snapshotEngine, startStreams]);

  const scenarioControls = scenarioControlValues(scenarioConfig, snapshot.satellites.length);
  const displaySimTime = selectRuntimeDisplaySimTime(
    runtimeStatus,
    snapshot.last_sim_time,
    runtimeProgressAnchor,
    runtimeProgressNowMs
  );
  const displayEventCount = selectRuntimeDisplayEventCount(
    runtimeStatus,
    snapshot.event_count
  );
  const runtimeRibbon = buildRuntimeRibbonSummary({
    simTime: displaySimTime,
    eventCount: displayEventCount,
    runtimeStatus,
    scenario: scenarioControls
  });
  const surfaceSyncSummary = buildSurfaceSyncSummary({
    displaySimTime,
    snapshotSimTime: snapshot.last_sim_time,
    eventCount: displayEventCount,
    runtimeStatus
  });
  const connectionDiagnostics = connectionDiagnosticItems(
    connectionHealth,
    runtimeStatus.stream_diagnostics_v1,
    streamConsumerCursors
  );
  const fidelitySummary = selectFidelitySummary(runtimeStatus, generatedConfig, snapshot);
  const backpressureSummary = runtimeStatus.backpressure_summary ?? null;
  const showBackpressureNotice = shouldShowRuntimeBackpressureNotice(
    runtimeStatus,
    backpressureSummary
  );
  const backpressureNoticeKeyForStatus =
    backpressureSummary !== null && showBackpressureNotice
      ? backpressureNoticeDismissKey(backpressureSummary)
      : null;
  const backpressureNoticeDismissed =
    backpressureNoticeKeyForStatus !== null &&
    backpressureNoticeKeyForStatus === dismissedBackpressureNoticeKey;
  const showCompletionNotice = shouldShowRuntimeCompletionNotice(
    runtimeStatus,
    completionNoticeArmed
  );
  const completionNoticeKeyForStatus = showCompletionNotice
    ? completionNoticeDismissKey(runtimeStatus)
    : null;
  const completionNoticeDismissed =
    completionNoticeKeyForStatus !== null &&
    completionNoticeKeyForStatus === dismissedCompletionNoticeKey;

  useEffect(() => {
    if (backpressureNoticeKeyForStatus === null) {
      clearBackpressureNoticeDismissKey(browserSessionStorage());
      setDismissedBackpressureNoticeKey(null);
    }
  }, [backpressureNoticeKeyForStatus]);

  useEffect(() => {
    if (runtimeStatusArmsCompletionNotice(runtimeStatus)) {
      setCompletionNoticeArmed(true);
      clearCompletionNoticeDismissKey(browserSessionStorage());
      setDismissedCompletionNoticeKey(null);
    }
  }, [runtimeStatus.status, runtimeStatus.lifecycle_state]);

  const sendRuntimeControl = useCallback(
    (action: RuntimeAction, payload: Record<string, unknown> = {}) => {
      setControlError(null);
      setRuntimeStatus((previous) => ({
        ...previous,
        last_action: `${action}_PENDING`
      }));
      controlClient.sendRuntimeControl(action, payload);
    },
    [controlClient]
  );
  const restoreRuntimeExportPackage = useCallback(
    (packageId: string) => {
      setControlError(null);
      setRuntimeExportRestoreCommandError(null);
      setRuntimeExportRestoreResult(null);
      setRuntimeExportRestoreCommandPendingPackageId(packageId);
      setRuntimeStatus((previous) => ({
        ...previous,
        last_action: "RESTORE_EXPORT_PACKAGE_PENDING"
      }));
      controlClient.sendRuntimeControl("RESTORE_EXPORT_PACKAGE", {
        package_id: packageId,
        confirm_restore: true
      });
    },
    [controlClient]
  );
  const dismissBackpressureNotice = useCallback(() => {
    if (backpressureNoticeKeyForStatus !== null) {
      setDismissedBackpressureNoticeKey(backpressureNoticeKeyForStatus);
      writeBackpressureNoticeDismissKey(
        browserSessionStorage(),
        backpressureNoticeKeyForStatus
      );
    }
  }, [backpressureNoticeKeyForStatus]);
  const dismissCompletionNotice = useCallback(() => {
    if (completionNoticeKeyForStatus !== null) {
      setDismissedCompletionNoticeKey(completionNoticeKeyForStatus);
      writeCompletionNoticeDismissKey(
        browserSessionStorage(),
        completionNoticeKeyForStatus
      );
    }
  }, [completionNoticeKeyForStatus]);

  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="brand-block">
          <div className="brand-mark" aria-hidden="true">
            LT
          </div>
          <div className="brand-copy">
            <div className="brand-title">LEO-Twin</div>
            <div className="brand-subtitle">低轨卫星互联网通信-算力数字孪生平台</div>
          </div>
        </div>
        <div className="surface-tabs" aria-label="前端界面">
          <a
            className={`surface-tab ${surface === "control" ? "active" : ""}`}
            href="/"
            onClick={(event) => navigateWithinApp(event, "/")}
          >
            仿真控制
          </a>
          <a
            className={`surface-tab ${surface === "dashboard" ? "active" : ""}`}
            href="/dashboard"
            onClick={(event) => navigateWithinApp(event, "/dashboard")}
          >
            运行概览
          </a>
        </div>
        <div className="topbar-status-cluster" aria-label="前端运行同步状态">
          <div className="sync-pill">
            <span>{surfaceSyncSummary.statusLabel}</span>
            <strong>{surfaceSyncSummary.displayTimeLabel}</strong>
            <small>
              快照 {surfaceSyncSummary.snapshotTimeLabel} · {surfaceSyncSummary.deltaLabel} · 事件{" "}
              {surfaceSyncSummary.eventCountLabel}
            </small>
          </div>
          <div className={`connection-pill ${connectionState}`}>
            {connectionStateLabel(connectionState)}
          </div>
          <details className="connection-diagnostics" aria-label="连接诊断">
            <summary>连接详情</summary>
            <div className="connection-diagnostics-popover">
              {connectionDiagnostics.map((item) => (
                <span
                  aria-label={item.description ?? `${item.label}：${item.statusLabel}`}
                  className={`connection-diagnostic ${item.status}`}
                  key={item.channel}
                  title={item.description}
                >
                  <small>{item.detail === undefined ? item.label : `${item.label} · ${item.detail}`}</small>
                  <strong>{item.statusLabel}</strong>
                </span>
              ))}
            </div>
          </details>
        </div>
      </header>
      {surface === "dashboard" ? (
        <section className="dashboard-page" aria-label="独立数据态势面板">
          <FidelityNotice summary={fidelitySummary} surface="dashboard" />
          <CompletionNotice
            runtimeStatus={showCompletionNotice ? runtimeStatus : null}
            surface="dashboard"
            dismissed={completionNoticeDismissed}
            onDismiss={dismissCompletionNotice}
          />
          <BackpressureNotice
            summary={showBackpressureNotice ? backpressureSummary : null}
            surface="dashboard"
            dismissed={backpressureNoticeDismissed}
            onDismiss={dismissBackpressureNotice}
          />
          {!advancedDashboardVisible ? (
            <UserOverview
              snapshot={snapshot}
              runtimeStatus={runtimeStatus}
              generatedConfig={generatedConfig}
              displaySimTime={displaySimTime}
              displayEventCount={displayEventCount}
              onNavigateControl={(event) => navigateWithinApp(event, "/")}
              onShowAdvanced={() => setAdvancedDashboardVisible(true)}
            />
          ) : (
            <>
              <div className="advanced-dashboard-toolbar">
                <div>
                  <strong>高级诊断</strong>
                  <span>面向模型验证、配置审查和运行排障人员</span>
                </div>
                <button type="button" onClick={() => setAdvancedDashboardVisible(false)}>
                  返回运行概览
                </button>
              </div>
              <Suspense
            fallback={
              <div className="surface-loading" role="status">
                高级诊断加载中
              </div>
            }
          >
            <DataPanel
              snapshot={snapshot}
              runtimeStatus={runtimeStatus}
              generatedConfig={generatedConfig}
              runtimeDetailPages={runtimeDetailPages}
              runtimeDetailCursorControls={{
                users: {
                  loading: runtimeDetailCursorLoading.users,
                  error: runtimeDetailCursorErrors.users,
                  onCursorChange: refreshRuntimeUserDetailCursor,
                  onRefresh: (filters) =>
                    refreshRuntimeUserDetailCursor(
                      runtimeDetailPages?.users?.cursor ?? runtimeDetailCursors.users,
                      filters
                    )
                },
                satellites: {
                  loading: runtimeDetailCursorLoading.satellites,
                  error: runtimeDetailCursorErrors.satellites,
                  onCursorChange: refreshRuntimeSatelliteDetailCursor,
                  onRefresh: (filters) =>
                    refreshRuntimeSatelliteDetailCursor(
                      runtimeDetailPages?.satellites?.cursor ??
                        runtimeDetailCursors.satellites,
                      filters
                    )
                },
                routes: {
                  loading: runtimeDetailCursorLoading.routes,
                  error: runtimeDetailCursorErrors.routes,
                  onCursorChange: refreshRuntimeRouteDetailCursor,
                  onRefresh: (filters) =>
                    refreshRuntimeRouteDetailCursor(
                      runtimeDetailPages?.routes?.cursor ?? runtimeDetailCursors.routes,
                      filters
                    )
                },
                services: {
                  loading: runtimeDetailCursorLoading.services,
                  error: runtimeDetailCursorErrors.services,
                  onCursorChange: refreshRuntimeServiceDetailCursor,
                  onRefresh: (filters) =>
                    refreshRuntimeServiceDetailCursor(
                      runtimeDetailPages?.services?.cursor ?? runtimeDetailCursors.services,
                      filters
                    )
                },
                serviceTraces: {
                  loading: runtimeDetailCursorLoading.serviceTraces,
                  error: runtimeDetailCursorErrors.serviceTraces,
                  onCursorChange: refreshRuntimeServiceTraceDetailCursor,
                  onRefresh: (filters) =>
                    refreshRuntimeServiceTraceDetailCursor(
                      runtimeDetailPages?.serviceTraces?.cursor ??
                        runtimeDetailCursors.serviceTraces,
                      filters
                    )
                },
                computeNodes: {
                  loading: runtimeDetailCursorLoading.computeNodes,
                  error: runtimeDetailCursorErrors.computeNodes,
                  onCursorChange: refreshRuntimeComputeNodeDetailCursor,
                  onRefresh: (filters) =>
                    refreshRuntimeComputeNodeDetailCursor(
                      runtimeDetailPages?.computeNodes?.cursor ??
                        runtimeDetailCursors.computeNodes,
                      filters
                  )
                }
              }}
              runtimeSelectedNodeDetails={runtimeSelectedNodeDetails}
              runtimeSelectedNodeDetailRequests={runtimeSelectedNodeDetailRequests}
              runtimeExportCatalog={runtimeExportCatalog}
              runtimeExportCompare={runtimeExportCompare}
              runtimeExportReviewSummary={runtimeExportReviewSummary}
              runtimeExportManifest={runtimeExportManifest}
              runtimeExportDiagnosticsBundle={runtimeExportDiagnosticsBundle}
              runtimeExportServiceLifecycleTrace={runtimeExportServiceLifecycleTrace}
              runtimeExportServiceTracePage={runtimeExportServiceTracePage}
              runtimeExportServiceTraceItem={runtimeExportServiceTraceItem}
              runtimeExportUserServiceRequestPage={
                runtimeExportUserServiceRequestPage
              }
              runtimeExportRouteDetailPage={runtimeExportRouteDetailPage}
              runtimeExportRouteDetailItem={runtimeExportRouteDetailItem}
              runtimeExportServiceTraceItemTraceId={
                runtimeExportServiceTraceItemTraceId
              }
              runtimeExportRouteComparisonReviewReport={
                runtimeExportRouteComparisonReviewReport
              }
              runtimeExportServiceTraceComparisonReviewReport={
                runtimeExportServiceTraceComparisonReviewReport
              }
              runtimeExportPackageAuditIndex={runtimeExportPackageAuditIndex}
              runtimeExportPackageAcceptanceReport={
                runtimeExportPackageAcceptanceReport
              }
              runtimeExportScenarioReviewBundle={runtimeExportScenarioReviewBundle}
              runtimeExportScenarioReviewChecklist={
                runtimeExportScenarioReviewChecklist
              }
              runtimeExportScenarioReviewChecklistTemplate={
                runtimeExportScenarioReviewChecklistTemplate
              }
              runtimeExportScenarioReviewChecklistTemplateComparison={
                runtimeExportScenarioReviewChecklistTemplateComparison
              }
              runtimeExportRouteDetailItemRouteId={runtimeExportRouteDetailItemRouteId}
              runtimeExportComparePackageId={runtimeExportComparePackageId}
              runtimeExportCompareLoading={runtimeExportCompareLoading}
              runtimeExportCompareError={runtimeExportCompareError}
              runtimeExportReviewSummaryLoading={runtimeExportReviewSummaryLoading}
              runtimeExportReviewSummaryError={runtimeExportReviewSummaryError}
              runtimeExportManifestLoading={runtimeExportManifestLoading}
              runtimeExportManifestError={runtimeExportManifestError}
              runtimeExportDiagnosticsBundleLoading={
                runtimeExportDiagnosticsBundleLoading
              }
              runtimeExportDiagnosticsBundleError={runtimeExportDiagnosticsBundleError}
              runtimeExportServiceLifecycleTraceLoading={
                runtimeExportServiceLifecycleTraceLoading
              }
              runtimeExportServiceLifecycleTraceError={
                runtimeExportServiceLifecycleTraceError
              }
              runtimeExportUserServiceRequestPageLoading={
                runtimeExportUserServiceRequestPageLoading
              }
              runtimeExportUserServiceRequestPageError={
                runtimeExportUserServiceRequestPageError
              }
              runtimeExportRouteDetailIndexLoading={runtimeExportRouteDetailIndexLoading}
              runtimeExportRouteDetailIndexError={runtimeExportRouteDetailIndexError}
              runtimeExportRouteDetailItemLoading={runtimeExportRouteDetailItemLoading}
              runtimeExportRouteDetailItemError={runtimeExportRouteDetailItemError}
              runtimeExportServiceTraceItemLoading={
                runtimeExportServiceTraceItemLoading
              }
              runtimeExportServiceTraceItemError={
                runtimeExportServiceTraceItemError
              }
              runtimeExportRouteComparisonReviewReportLoading={
                runtimeExportRouteComparisonReviewReportLoading
              }
              runtimeExportRouteComparisonReviewReportError={
                runtimeExportRouteComparisonReviewReportError
              }
              runtimeExportServiceTraceComparisonReviewReportLoading={
                runtimeExportServiceTraceComparisonReviewReportLoading
              }
              runtimeExportServiceTraceComparisonReviewReportError={
                runtimeExportServiceTraceComparisonReviewReportError
              }
              runtimeExportPackageAuditIndexLoading={
                runtimeExportPackageAuditIndexLoading
              }
              runtimeExportPackageAuditIndexError={
                runtimeExportPackageAuditIndexError
              }
              runtimeExportScenarioReviewBundleLoading={
                runtimeExportScenarioReviewBundleLoading
              }
              runtimeExportScenarioReviewBundleError={
                runtimeExportScenarioReviewBundleError
              }
              runtimeExportScenarioReviewChecklistLoading={
                runtimeExportScenarioReviewChecklistLoading
              }
              runtimeExportScenarioReviewChecklistError={
                runtimeExportScenarioReviewChecklistError
              }
              runtimeExportRouteComparisonReviewSavePendingRouteId={
                runtimeExportRouteComparisonReviewSavePendingRouteId
              }
              runtimeExportRouteComparisonReviewSaveError={
                runtimeExportRouteComparisonReviewSaveError
              }
              runtimeExportRouteComparisonReviewSaveReportHash={
                runtimeExportRouteComparisonReviewSaveReportHash
              }
              runtimeExportServiceTraceComparisonReviewSavePendingTraceId={
                runtimeExportServiceTraceComparisonReviewSavePendingTraceId
              }
              runtimeExportServiceTraceComparisonReviewSaveError={
                runtimeExportServiceTraceComparisonReviewSaveError
              }
              runtimeExportServiceTraceComparisonReviewSaveReportHash={
                runtimeExportServiceTraceComparisonReviewSaveReportHash
              }
              runtimeExportScenarioReviewChecklistSavePending={
                runtimeExportScenarioReviewChecklistSavePending
              }
              runtimeExportScenarioReviewChecklistSaveError={
                runtimeExportScenarioReviewChecklistSaveError
              }
              runtimeExportScenarioReviewChecklistSaveHash={
                runtimeExportScenarioReviewChecklistSaveHash
              }
              runtimeExportRestorePreflight={runtimeExportRestorePreflight}
              runtimeExportRestorePreflightLoading={runtimeExportRestorePreflightLoading}
              runtimeExportRestorePreflightError={runtimeExportRestorePreflightError}
              runtimeExportRestoreCommandPendingPackageId={
                runtimeExportRestoreCommandPendingPackageId
              }
              runtimeExportRestoreCommandError={runtimeExportRestoreCommandError}
              runtimeExportRestoreResult={runtimeExportRestoreResult}
              userConfigurationSchema={userConfigurationSchema}
              userConfigurationTemplates={userConfigurationTemplates}
              userConfigurationReference={userConfigurationReference}
              userConfigurationExport={userConfigurationExport}
              userConfigurationContractLoading={userConfigurationContractLoading}
              userConfigurationContractError={userConfigurationContractError}
              onUserConfigurationValidate={validateUserConfiguration}
              onUserConfigurationValidateText={validateUserConfigurationText}
              onUserConfigurationApply={applyValidatedUserConfiguration}
              onRuntimeExportCompareSelect={refreshRuntimeExportCompare}
              onRuntimeExportRouteDetailPageQueryChange={
                refreshRuntimeExportRouteDetailPage
              }
              onRuntimeExportRouteComparisonReviewReportPageQueryChange={
                refreshRuntimeExportRouteComparisonReviewReportPage
              }
              onRuntimeExportServiceTracePageQueryChange={
                refreshRuntimeExportServiceTracePage
              }
              onRuntimeExportServiceTraceComparisonReviewReportPageQueryChange={
                refreshRuntimeExportServiceTraceComparisonReviewReportPage
              }
              onRuntimeExportUserServiceRequestPageQueryChange={
                refreshRuntimeExportUserServiceRequestPage
              }
              onRuntimeExportRouteDetailItemSelect={refreshRuntimeExportRouteDetailItem}
              onRuntimeExportServiceTraceItemSelect={
                refreshRuntimeExportServiceTraceItem
              }
              onRuntimeExportRouteComparisonReviewSave={
                saveRuntimeExportRouteComparisonReview
              }
              onRuntimeExportServiceTraceComparisonReviewSave={
                saveRuntimeExportServiceTraceComparisonReview
              }
              onRuntimeExportScenarioReviewChecklistSave={
                saveRuntimeExportScenarioReviewChecklist
              }
              onRuntimeExportRestore={restoreRuntimeExportPackage}
              onRuntimeUserDetailSelect={refreshRuntimeUserEntityDetail}
              onRuntimeSatelliteDetailSelect={refreshRuntimeSatelliteEntityDetail}
              onRuntimeRouteDetailSelect={refreshRuntimeRouteEntityDetail}
              onRuntimeServiceDetailSelect={refreshRuntimeServiceEntityDetail}
              onRuntimeServiceTraceDetailSelect={
                refreshRuntimeServiceTraceEntityDetail
              }
              onRuntimeComputeNodeDetailSelect={refreshRuntimeComputeNodeEntityDetail}
              displaySimTime={displaySimTime}
              displayEventCount={displayEventCount}
              onNavigateControl={(event) => navigateWithinApp(event, "/")}
            />
              </Suspense>
            </>
          )}
        </section>
      ) : (
        <section className="workspace control-workspace">
          <section className="simulation-surface control-only" aria-label="三维仿真控制台">
            <div className="surface-header">
              <div>
                <div className="surface-kicker">三维展示与运行控制</div>
                <h1>星座运行视图</h1>
              </div>
              <div className="surface-status-stack">
                <div className={`surface-status ${runtimeStatus.status.toLowerCase()}`}>
                  <span>{runtimeStatusLabel(runtimeStatus)}</span>
                  <strong>{runtimeSpeedFactorLabel(runtimeStatus)}</strong>
                </div>
                <a
                  className="surface-action-link"
                  href="/dashboard"
                  onClick={(event) => navigateWithinApp(event, "/dashboard")}
                >
                  查看数据面板
                </a>
              </div>
            </div>
            <div className="simulation-ribbon" aria-label="仿真进程">
              <div className="simulation-progress-block">
                <div className="summary-title-row">
                  <span>仿真进程</span>
                  <strong>{runtimeRibbon.percentLabel}</strong>
                </div>
                <progress
                  value={runtimeRibbon.percent}
                  max="100"
                  aria-label="三维控制台仿真进度"
                />
              </div>
              <div className="simulation-ribbon-metrics">
                <div>
                  <span>仿真时间</span>
                  <strong>
                    {runtimeRibbon.elapsedLabel} / {runtimeRibbon.durationLabel}
                  </strong>
                </div>
                <div>
                  <span>事件数</span>
                  <strong>{runtimeRibbon.eventCountLabel}</strong>
                </div>
                <div>
                  <span>卫星规模</span>
                  <strong>{runtimeRibbon.satelliteCountLabel}</strong>
                </div>
                <div>
                  <span>用户规模</span>
                  <strong>{runtimeRibbon.userCountLabel}</strong>
                </div>
              </div>
            </div>
            <FidelityNotice summary={fidelitySummary} surface="control" />
            <CompletionNotice
              runtimeStatus={showCompletionNotice ? runtimeStatus : null}
              surface="control"
              dismissed={completionNoticeDismissed}
              onDismiss={dismissCompletionNotice}
            />
            <BackpressureNotice
              summary={showBackpressureNotice ? backpressureSummary : null}
              surface="control"
              dismissed={backpressureNoticeDismissed}
              onDismiss={dismissBackpressureNotice}
            />
            <div className="globe-panel">
              <Suspense
                fallback={
                  <div className="globe-loading" role="status">
                    三维引擎加载中
                  </div>
                }
              >
                <CesiumGlobe
                  snapshot={snapshot}
                  displaySimTime={displaySimTime}
                  satelliteKpiSlices={runtimeStatus.satellite_kpi_slices_v1}
                  satelliteKpiHistory={runtimeStatus.satellite_kpi_history_v1}
                />
              </Suspense>
            </div>
            <div className="control-dock">
              <Suspense
                fallback={
                  <div className="control-panel-loading" role="status">
                    配置面板加载中
                  </div>
                }
              >
                <ConfigPanel
                  scenario={scenarioControls}
                  runtime={runtimeStatus}
                  progress={{
                    sim_time: displaySimTime,
                    duration: runtimeStatus.duration,
                    event_count: displayEventCount
                  }}
                  generatedConfig={generatedConfig}
                  controlError={controlError}
                  onRuntimeControl={sendRuntimeControl}
                />
              </Suspense>
            </div>
          </section>
        </section>
      )}
    </main>
  );
}

export type FrontendSurface = "control" | "dashboard";

export function surfaceFromPathname(pathname: string): FrontendSurface {
  return pathname === "/dashboard" || pathname.startsWith("/dashboard/")
    ? "dashboard"
    : "control";
}

export function bodySurfaceAttribute(surface: FrontendSurface): FrontendSurface {
  return surface;
}

export function standaloneDashboardHref(origin: string): string {
  const normalizedOrigin = origin.endsWith("/") ? origin.slice(0, -1) : origin;
  return `${normalizedOrigin}/dashboard`;
}

export function selectRuntimeExportComparePackageId(
  catalog: RuntimeExportCatalogV1 | null,
  selectedPackageId: string | null
): string | null {
  if (catalog === null || catalog.records.length === 0) {
    return null;
  }
  const packageIds = new Set(catalog.records.map((record) => record.package_id));
  if (selectedPackageId !== null && packageIds.has(selectedPackageId)) {
    return selectedPackageId;
  }
  return catalog.latest_export?.package_id ?? catalog.records[0]?.package_id ?? null;
}

export function runtimeExportCatalogHasRouteComparisonReviewReport(
  catalog: RuntimeExportCatalogV1 | null,
  packageId: string
): boolean {
  if (catalog === null) {
    return false;
  }
  return catalog.records.some(
    (record) =>
      record.package_id === packageId &&
      record.files.some(
        (file) => file.filename === ROUTE_COMPARISON_REVIEW_REPORT_FILENAME
      )
  );
}

export function runtimeExportCatalogHasServiceTraceComparisonReviewReport(
  catalog: RuntimeExportCatalogV1 | null,
  packageId: string
): boolean {
  if (catalog === null) {
    return false;
  }
  return catalog.records.some(
    (record) =>
      record.package_id === packageId &&
      record.files.some(
        (file) =>
          file.filename === SERVICE_TRACE_COMPARISON_REVIEW_REPORT_FILENAME
      )
  );
}

export function runtimeExportCatalogHasPackageAuditIndex(
  catalog: RuntimeExportCatalogV1 | null,
  packageId: string
): boolean {
  if (catalog === null) {
    return false;
  }
  return catalog.records.some(
    (record) =>
      record.package_id === packageId &&
      record.files.some(
        (file) => file.filename === EXPORT_PACKAGE_AUDIT_INDEX_FILENAME
      )
  );
}

export function runtimeExportCatalogHasScenarioReviewBundle(
  catalog: RuntimeExportCatalogV1 | null,
  packageId: string
): boolean {
  if (catalog === null) {
    return false;
  }
  return catalog.records.some(
    (record) =>
      record.package_id === packageId &&
      record.files.some((file) => file.filename === SCENARIO_REVIEW_BUNDLE_FILENAME)
  );
}

export function runtimeExportCatalogHasScenarioReviewChecklist(
  catalog: RuntimeExportCatalogV1 | null,
  packageId: string
): boolean {
  if (catalog === null) {
    return false;
  }
  return catalog.records.some(
    (record) =>
      record.package_id === packageId &&
      record.files.some(
        (file) => file.filename === SCENARIO_REVIEW_CHECKLIST_FILENAME
      )
  );
}

export function runtimeExportCatalogHasServiceLifecycleTrace(
  catalog: RuntimeExportCatalogV1 | null,
  packageId: string
): boolean {
  if (catalog === null) {
    return false;
  }
  return catalog.records.some(
    (record) =>
      record.package_id === packageId &&
      record.files.some((file) => file.filename === SERVICE_LIFECYCLE_TRACE_FILENAME)
  );
}

export function runtimeExportCatalogHasUserServiceRequestSummary(
  catalog: RuntimeExportCatalogV1 | null,
  packageId: string
): boolean {
  if (catalog === null) {
    return false;
  }
  return catalog.records.some(
    (record) =>
      record.package_id === packageId &&
      record.files.some(
        (file) => file.filename === USER_SERVICE_REQUEST_SUMMARY_FILENAME
      )
  );
}

export interface RuntimeDetailRequest {
  endpoint: string;
  limit: number;
}

export interface RuntimeDetailRequestPlan {
  users: RuntimeDetailRequest;
  satellites: RuntimeDetailRequest;
  nodes: RuntimeDetailRequest;
  routes: RuntimeDetailRequest;
  services: RuntimeDetailRequest;
  serviceTraces: RuntimeDetailRequest;
  computeNodes: RuntimeDetailRequest;
}

export function runtimeDetailRequestPlan(
  contract: LargeDetailPaginationContractV2 | null | undefined
): RuntimeDetailRequestPlan {
  const collections = new Map(
    (contract?.collections ?? []).map((collection) => [
      collection.collection,
      collection
    ])
  );
  const users = runtimeDetailCollectionRequest(
    collections.get("ground_users"),
    "/runtime/details/users"
  );
  const satellites = runtimeDetailCollectionRequest(
    collections.get("satellites"),
    "/runtime/details/satellites"
  );
  const routes = runtimeDetailCollectionRequest(
    collections.get("routes"),
    "/runtime/details/routes"
  );
  const services = runtimeDetailCollectionRequest(
    collections.get("services"),
    "/runtime/details/services"
  );
  const serviceTraces = runtimeDetailCollectionRequest(
    collections.get("service_traces"),
    "/runtime/details/service-traces"
  );
  const computeNodes = runtimeDetailCollectionRequest(
    collections.get("compute_nodes"),
    "/runtime/details/compute-nodes"
  );
  return {
    users,
    satellites,
    routes,
    services,
    serviceTraces,
    computeNodes,
    nodes: {
      endpoint: contract?.combined_node_endpoint?.endpoint ?? "/runtime/details/nodes",
      limit: runtimeDetailNodeLimit(contract, users.limit, satellites.limit)
    }
  };
}

function runtimeDetailCollectionRequest(
  collection: LargeDetailPaginationCollectionV2 | undefined,
  fallbackEndpoint: string
): RuntimeDetailRequest {
  return {
    endpoint: collection?.endpoint ?? fallbackEndpoint,
    limit: runtimeDetailLimit(
      collection?.recommended_limit,
      collection?.max_limit ?? RUNTIME_DETAIL_FALLBACK_LIMIT
    )
  };
}

function runtimeDetailNodeLimit(
  contract: LargeDetailPaginationContractV2 | null | undefined,
  userLimit: number,
  satelliteLimit: number
): number {
  if (contract === null || contract === undefined) {
    return RUNTIME_DETAIL_FALLBACK_LIMIT;
  }
  return runtimeDetailLimit(
    userLimit + satelliteLimit,
    contract.cursor_model?.max_limit ?? RUNTIME_DETAIL_FALLBACK_LIMIT
  );
}

function runtimeDetailLimit(value: number | undefined, maxLimit: number): number {
  const normalizedMax = Math.max(1, Math.floor(maxLimit));
  if (value === undefined || !Number.isFinite(value) || value <= 0) {
    return Math.min(RUNTIME_DETAIL_FALLBACK_LIMIT, normalizedMax);
  }
  return Math.min(Math.max(1, Math.floor(value)), normalizedMax);
}

function normalizeRuntimeDetailCursor(cursor: number): number {
  if (!Number.isFinite(cursor) || cursor <= 0) {
    return 0;
  }
  return Math.floor(cursor);
}

function normalizeRuntimeDetailFilters(
  filters: RuntimeDetailQueryFilters
): RuntimeDetailQueryFilters {
  const query = filters.query?.trim();
  const availability = filters.availability?.trim();
  const businessType = filters.businessType?.trim();
  const bottleneckComponent = filters.bottleneckComponent?.trim();
  const terminalState = filters.terminalState?.trim();
  const computeNodeId = filters.computeNodeId?.trim();
  const stageKind = filters.stageKind?.trim();
  const terminalReason = filters.terminalReason?.trim();
  return {
    ...(query ? { query } : {}),
    ...(availability && availability !== "ALL" ? { availability } : {}),
    ...(businessType && businessType !== "ALL" ? { businessType } : {}),
    ...(bottleneckComponent && bottleneckComponent !== "ALL"
      ? { bottleneckComponent }
      : {}),
    ...(terminalState && terminalState !== "ALL" ? { terminalState } : {}),
    ...(computeNodeId ? { computeNodeId } : {}),
    ...(stageKind && stageKind !== "ALL" ? { stageKind } : {}),
    ...(terminalReason && terminalReason !== "ALL" ? { terminalReason } : {})
  };
}

export interface RuntimeRibbonSummary {
  percent: number;
  percentLabel: string;
  elapsedLabel: string;
  durationLabel: string;
  eventCountLabel: string;
  satelliteCountLabel: string;
  userCountLabel: string;
}

export interface SurfaceSyncSummary {
  displayTimeLabel: string;
  snapshotTimeLabel: string;
  deltaLabel: string;
  eventCountLabel: string;
  statusLabel: string;
}

export interface RuntimeProgressAnchor {
  simTime: number;
  wallTimeMs: number;
  status: RuntimeStatusPayload["status"];
  lifecycleState?: RuntimeStatusPayload["lifecycle_state"];
  speedFactor: number;
  duration: number;
}

export type StreamConnectReason = "START" | "RESUME" | "ATTACH";

export function shouldResetWorldBeforeStreamConnect(
  reason: StreamConnectReason,
  snapshotEventCount: number
): boolean {
  return reason === "START" && snapshotEventCount <= 0;
}

export function selectFidelitySummary(
  runtimeStatus: RuntimeStatusPayload,
  generatedConfig: GeneratedScenarioConfig | null,
  snapshot: WorldSnapshot
): FidelitySummary | null {
  return (
    runtimeStatus.fidelity_summary ??
    generatedConfig?.backend_summary?.fidelity_summary ??
    snapshot.fidelity_summary ??
    snapshot.scenario_config?.backend_summary?.fidelity_summary ??
    null
  );
}

export function shouldShowFidelityNotice(summary: FidelitySummary | null): boolean {
  if (summary === null) {
    return false;
  }
  return (
    summary.orbit_update_mode !== "PER_SATELLITE" ||
    summary.metrics_mode !== "DETAILED" ||
    summary.space_link_mode !== "DETAILED_SMALL_SCALE" ||
    !summary.detailed_space_link_enabled ||
    summary.scale_limit_reason !== "none"
  );
}

export function fidelityNoticeText(summary: FidelitySummary): string {
  const details: string[] = [];
  if (summary.orbit_update_mode === "BATCH") {
    details.push("轨道更新采用批量模式。");
  } else {
    details.push(`轨道更新模式为 ${summary.orbit_update_mode}。`);
  }
  if (summary.metrics_mode === "AGGREGATED") {
    details.push("指标采用聚合模式。");
  } else {
    details.push(`指标模式为 ${summary.metrics_mode}。`);
  }
  if (summary.space_link_mode === "DISABLED") {
    details.push("星间链路更新已关闭。");
  } else if (summary.space_link_mode === "BOUNDED_CANDIDATE") {
    details.push("星间链路采用有界候选更新。");
  } else if (!summary.detailed_space_link_enabled) {
    details.push("星间链路使用降级精度。");
  } else {
    details.push("星间链路使用小规模详细更新。");
  }
  return `规模模式：${formatInteger(summary.satellite_count)} 颗卫星。${details.join("")}`;
}

function fidelityNoticeDetail(summary: FidelitySummary): string {
  if (summary.space_link_mode === "BOUNDED_CANDIDATE") {
    return [
      "后端策略：同轨邻近与相邻轨道有界候选；",
      `每星候选上限 ${formatInteger(summary.max_space_link_candidates_per_satellite)}，`,
      `详细批量阈值 ${formatInteger(summary.batch_space_link_update_limit)}。`
    ].join("");
  }
  if (summary.space_link_mode === "DISABLED") {
    return "后端策略：关闭星间链路更新以保持大规模控制响应。";
  }
  if (summary.scale_limit_reason !== "none") {
    return `后端策略：${summary.current_scale_mode}。`;
  }
  return `后端策略：${summary.space_link_candidate_policy}。`;
}

function FidelityNotice({
  summary,
  surface
}: {
  summary: FidelitySummary | null;
  surface: "control" | "dashboard";
}) {
  if (summary === null || !shouldShowFidelityNotice(summary)) {
    return null;
  }
  return (
    <div className={`fidelity-notice ${surface}`} role="status" aria-live="polite">
      <span>规模精度策略</span>
      <strong>{fidelityNoticeText(summary)}</strong>
      <small>{fidelityNoticeDetail(summary)}</small>
    </div>
  );
}

export function shouldShowCompletionNotice(
  runtimeStatus: RuntimeStatusPayload | null | undefined
): boolean {
  if (runtimeStatus === null || runtimeStatus === undefined) {
    return false;
  }
  return (
    runtimeStatus.status === "COMPLETED" ||
    runtimeStatus.lifecycle_state === "COMPLETED"
  );
}

export function runtimeStatusArmsCompletionNotice(
  runtimeStatus: RuntimeStatusPayload
): boolean {
  return (
    runtimeStatus.status === "RUNNING" ||
    runtimeStatus.status === "PAUSED" ||
    runtimeStatus.lifecycle_state === "RUNNING" ||
    runtimeStatus.lifecycle_state === "PAUSED"
  );
}

export function shouldShowRuntimeCompletionNotice(
  runtimeStatus: RuntimeStatusPayload,
  completionNoticeArmed: boolean
): boolean {
  return completionNoticeArmed && shouldShowCompletionNotice(runtimeStatus);
}

export function completionNoticeText(runtimeStatus: RuntimeStatusPayload): string {
  const elapsed = Math.max(
    0,
    finiteNumberOrZero(runtimeStatus.current_sim_time ?? runtimeStatus.duration)
  );
  const duration = Math.max(1, runtimeStatus.duration);
  return `仿真已完成：达到配置时长 ${formatDurationCompact(duration)}，最终仿真时间 ${formatDurationCompact(
    Math.min(elapsed, duration)
  )}。`;
}

export function completionNoticeDetail(runtimeStatus: RuntimeStatusPayload): string {
  const eventCount =
    typeof runtimeStatus.processed_event_count === "number"
      ? formatInteger(runtimeStatus.processed_event_count)
      : "0";
  return `后端推进循环已停止，事件流保持最终状态。事件数 ${eventCount}；重置后可重新初始化并开始下一轮仿真。`;
}

export function completionNoticeDismissKey(runtimeStatus: RuntimeStatusPayload): string {
  return [
    runtimeStatus.config_version,
    runtimeStatus.duration,
    runtimeStatus.current_sim_time ?? 0,
    runtimeStatus.processed_event_count ?? 0
  ].join("|");
}

export const COMPLETION_NOTICE_DISMISS_STORAGE_KEY =
  "leo_twin.completion_notice.dismissed_key";

type RuntimeNoticeStorage = {
  getItem: (key: string) => string | null;
  setItem: (key: string, value: string) => void;
  removeItem: (key: string) => void;
};

export function readCompletionNoticeDismissKey(
  storage: RuntimeNoticeStorage | null | undefined
): string | null {
  if (storage === null || storage === undefined) {
    return null;
  }
  try {
    return storage.getItem(COMPLETION_NOTICE_DISMISS_STORAGE_KEY);
  } catch {
    return null;
  }
}

export function writeCompletionNoticeDismissKey(
  storage: RuntimeNoticeStorage | null | undefined,
  dismissKey: string | null | undefined
): void {
  if (storage === null || storage === undefined || !dismissKey) {
    return;
  }
  try {
    storage.setItem(COMPLETION_NOTICE_DISMISS_STORAGE_KEY, dismissKey);
  } catch {
    // Ignore browser storage failures; the in-memory dismiss state still works.
  }
}

export function clearCompletionNoticeDismissKey(
  storage: RuntimeNoticeStorage | null | undefined
): void {
  if (storage === null || storage === undefined) {
    return;
  }
  try {
    storage.removeItem(COMPLETION_NOTICE_DISMISS_STORAGE_KEY);
  } catch {
    // Ignore browser storage failures; this is only a UI notice preference.
  }
}

function browserSessionStorage(): RuntimeNoticeStorage | null {
  if (typeof window === "undefined") {
    return null;
  }
  try {
    return window.sessionStorage;
  } catch {
    return null;
  }
}

function CompletionNotice({
  runtimeStatus,
  surface,
  dismissed,
  onDismiss
}: {
  runtimeStatus: RuntimeStatusPayload | null;
  surface: "control" | "dashboard";
  dismissed?: boolean;
  onDismiss?: () => void;
}) {
  if (
    runtimeStatus === null ||
    dismissed === true ||
    !shouldShowCompletionNotice(runtimeStatus)
  ) {
    return null;
  }
  return (
    <div
      className={`fidelity-notice completion ${surface}`}
      role="status"
      aria-live="polite"
    >
      <button
        type="button"
        className="fidelity-notice-dismiss"
        aria-label="关闭仿真完成提示"
        onClick={onDismiss}
      >
        x
      </button>
      <span>仿真完成</span>
      <strong>{completionNoticeText(runtimeStatus)}</strong>
      <small>{completionNoticeDetail(runtimeStatus)}</small>
    </div>
  );
}

export function shouldShowBackpressureNotice(
  summary: RuntimeBackpressureSummary | null | undefined
): boolean {
  if (summary === null || summary === undefined) {
    return false;
  }
  return summary.overloaded || summary.first_tick_heavy;
}

export function shouldShowRuntimeBackpressureNotice(
  runtimeStatus: RuntimeStatusPayload,
  summary: RuntimeBackpressureSummary | null | undefined
): boolean {
  if (!shouldShowBackpressureNotice(summary)) {
    return false;
  }
  const status = runtimeStatus.status;
  const lifecycleState = runtimeStatus.lifecycle_state;
  return (
    status !== "COMPLETED" &&
    status !== "STOPPED" &&
    lifecycleState !== "COMPLETED" &&
    lifecycleState !== "STOPPED"
  );
}

export function backpressureNoticeDismissKey(summary: RuntimeBackpressureSummary): string {
  return [
    String(summary.overloaded),
    String(summary.first_tick_heavy),
    summary.bottleneck_component,
    summary.recommended_action
  ].join("|");
}

export const BACKPRESSURE_NOTICE_DISMISS_STORAGE_KEY =
  "leo_twin.backpressure_notice.dismissed_key";

export function readBackpressureNoticeDismissKey(
  storage: RuntimeNoticeStorage | null | undefined
): string | null {
  if (storage === null || storage === undefined) {
    return null;
  }
  try {
    return storage.getItem(BACKPRESSURE_NOTICE_DISMISS_STORAGE_KEY);
  } catch {
    return null;
  }
}

export function writeBackpressureNoticeDismissKey(
  storage: RuntimeNoticeStorage | null | undefined,
  dismissKey: string | null | undefined
): void {
  if (storage === null || storage === undefined || !dismissKey) {
    return;
  }
  try {
    storage.setItem(BACKPRESSURE_NOTICE_DISMISS_STORAGE_KEY, dismissKey);
  } catch {
    // Ignore browser storage failures; the in-memory dismiss state still works.
  }
}

export function clearBackpressureNoticeDismissKey(
  storage: RuntimeNoticeStorage | null | undefined
): void {
  if (storage === null || storage === undefined) {
    return;
  }
  try {
    storage.removeItem(BACKPRESSURE_NOTICE_DISMISS_STORAGE_KEY);
  } catch {
    // Ignore browser storage failures; this is only a UI notice preference.
  }
}

export function backpressureNoticeText(summary: RuntimeBackpressureSummary): string {
  return [
    `运行压力：最近推进 ${formatMilliseconds(summary.tick_duration_ms)}，`,
    `预算 ${formatMilliseconds(summary.tick_budget_ms)}。`,
    `瓶颈组件：${summary.bottleneck_component}。`
  ].join("");
}

function backpressureNoticeDetail(summary: RuntimeBackpressureSummary): string {
  return [
    `队列深度 ${formatInteger(summary.queue_depth)}，`,
    `本 tick 处理事件 ${formatInteger(summary.processed_event_count)}，`,
    `建议：${summary.recommended_action}。`
  ].join("");
}

function BackpressureNotice({
  summary,
  surface,
  dismissed,
  onDismiss
}: {
  summary: RuntimeBackpressureSummary | null;
  surface: "control" | "dashboard";
  dismissed?: boolean;
  onDismiss?: () => void;
}) {
  if (summary === null || dismissed === true || !shouldShowBackpressureNotice(summary)) {
    return null;
  }
  return (
    <div className={`fidelity-notice backpressure ${surface}`} role="status" aria-live="polite">
      <button
        type="button"
        className="fidelity-notice-dismiss"
        aria-label="关闭运行压力提示"
        onClick={onDismiss}
      >
        x
      </button>
      <span>运行压力提示</span>
      <strong>{backpressureNoticeText(summary)}</strong>
      <small>{backpressureNoticeDetail(summary)}</small>
    </div>
  );
}

export function defaultRuntimeProgressAnchor(
  runtimeStatus: RuntimeStatusPayload,
  nowMs = Date.now()
): RuntimeProgressAnchor {
  return {
    simTime: runtimeStatus.current_sim_time ?? 0,
    wallTimeMs: nowMs,
    status: runtimeStatus.status,
    lifecycleState: runtimeStatus.lifecycle_state,
    speedFactor: runtimeStatus.speed_factor,
    duration: runtimeStatus.duration
  };
}

export function nextRuntimeProgressAnchor(
  previous: RuntimeProgressAnchor,
  snapshotSimTime: number,
  runtimeStatus: RuntimeStatusPayload,
  nowMs: number
): RuntimeProgressAnchor {
  const resetDisplayClock = runtimeStatusResetsDisplayClock(runtimeStatus);
  const observedSimTime = Math.max(
    0,
    resetDisplayClock ? 0 : snapshotSimTime,
    resetDisplayClock ? 0 : finiteNumberOrZero(runtimeStatus.current_sim_time)
  );
  const projectedSimTime = runtimeProgressSimTime(previous, nowMs);
  const statusChanged =
    previous.status !== runtimeStatus.status ||
    previous.lifecycleState !== runtimeStatus.lifecycle_state ||
    previous.speedFactor !== runtimeStatus.speed_factor ||
    previous.duration !== runtimeStatus.duration;
  if (resetDisplayClock) {
    return {
      simTime: Math.min(observedSimTime, runtimeStatus.duration),
      wallTimeMs: nowMs,
      status: runtimeStatus.status,
      lifecycleState: runtimeStatus.lifecycle_state,
      speedFactor: runtimeStatus.speed_factor,
      duration: runtimeStatus.duration
    };
  }

  if (
    runtimeStatusIsProgressing(runtimeStatus) &&
    !statusChanged &&
    observedSimTime <= projectedSimTime
  ) {
    return previous;
  }

  return {
    simTime: Math.min(Math.max(observedSimTime, projectedSimTime), runtimeStatus.duration),
    wallTimeMs: nowMs,
    status: runtimeStatus.status,
    lifecycleState: runtimeStatus.lifecycle_state,
    speedFactor: runtimeStatus.speed_factor,
    duration: runtimeStatus.duration
  };
}

export function selectRuntimeDisplaySimTime(
  runtimeStatus: RuntimeStatusPayload,
  snapshotSimTime: number,
  anchor: RuntimeProgressAnchor,
  nowMs: number
): number {
  if (runtimeStatusResetsDisplayClock(runtimeStatus)) {
    return 0;
  }
  return Math.max(snapshotSimTime, runtimeProgressSimTime(anchor, nowMs));
}

export function selectRuntimeDisplayEventCount(
  runtimeStatus: RuntimeStatusPayload,
  snapshotEventCount: number
): number {
  if (runtimeStatusResetsDisplayClock(runtimeStatus)) {
    return 0;
  }
  return runtimeStatus.processed_event_count ?? snapshotEventCount;
}

function runtimeStatusResetsDisplayClock(runtimeStatus: RuntimeStatusPayload): boolean {
  return [
    "RESET_PENDING",
    "RESET",
    "INITIALIZE_PENDING",
    "INITIALIZE",
    "CONFIG_UPDATE_PENDING",
    "CONFIG_UPDATE"
  ].includes(runtimeStatus.last_action);
}

export function runtimeProgressSimTime(
  anchor: RuntimeProgressAnchor,
  nowMs: number
): number {
  if (!runtimeProgressAnchorIsRunning(anchor)) {
    return Math.min(anchor.simTime, anchor.duration);
  }
  const elapsedSeconds = Math.max(0, (nowMs - anchor.wallTimeMs) / 1000);
  return Math.min(anchor.duration, anchor.simTime + elapsedSeconds * anchor.speedFactor);
}

export function buildRuntimeRibbonSummary({
  simTime,
  eventCount,
  runtimeStatus,
  scenario
}: {
  simTime: number;
  eventCount: number;
  runtimeStatus: RuntimeStatusPayload;
  scenario: ScenarioControlValues;
}): RuntimeRibbonSummary {
  const duration = Math.max(1, runtimeStatus.duration);
  const elapsed = Math.min(Math.max(0, simTime), duration);
  const percent = Math.min(100, Math.max(0, (elapsed / duration) * 100));
  return {
    percent,
    percentLabel: `${formatPercent(percent)}%`,
    elapsedLabel: formatDurationCompact(elapsed),
    durationLabel: formatDurationCompact(duration),
    eventCountLabel: formatInteger(eventCount),
    satelliteCountLabel: formatInteger(scenario.satellite_count),
    userCountLabel: formatInteger(scenario.user_count)
  };
}

export function buildSurfaceSyncSummary({
  displaySimTime,
  snapshotSimTime,
  eventCount,
  runtimeStatus
}: {
  displaySimTime: number;
  snapshotSimTime: number;
  eventCount: number;
  runtimeStatus: RuntimeStatusPayload;
}): SurfaceSyncSummary {
  const boundedDisplayTime = Math.max(0, displaySimTime);
  const boundedSnapshotTime = Math.max(0, snapshotSimTime);
  const deltaSeconds = boundedDisplayTime - boundedSnapshotTime;
  const statusLabel =
    runtimeStatus.status === "COMPLETED" || runtimeStatus.lifecycle_state === "COMPLETED"
      ? "同步完成"
      : runtimeStatus.status === "RUNNING"
        ? "同步运行"
        : runtimeStatus.status === "PAUSED"
          ? "同步暂停"
          : "同步待机";
  return {
    displayTimeLabel: `显示 ${formatDurationCompact(boundedDisplayTime)}`,
    snapshotTimeLabel: formatDurationCompact(boundedSnapshotTime),
    deltaLabel: formatSyncDelta(deltaSeconds),
    eventCountLabel: formatInteger(eventCount),
    statusLabel
  };
}

function formatSyncDelta(deltaSeconds: number): string {
  const magnitude = Math.abs(deltaSeconds);
  if (magnitude < 0.05) {
    return "同帧";
  }
  const label = formatDurationCompact(magnitude);
  return deltaSeconds > 0 ? `前端插值 +${label}` : `快照领先 ${label}`;
}

export function runtimeStatusRequiresStreams(
  status: RuntimeStatusPayload | undefined
): boolean {
  return status !== undefined && runtimeStatusIsProgressing(status);
}

export function scenarioWithRuntimeConfig(
  scenario: ScenarioConfig,
  runtimeConfig: unknown
): ScenarioConfig {
  if (!isRecord(runtimeConfig)) {
    return scenario;
  }
  const scenarioSection = isRecord(runtimeConfig.scenario)
    ? {
        ...scenario.scenario,
        compute_capacity:
          typeof runtimeConfig.scenario.compute_capacity === "number"
            ? runtimeConfig.scenario.compute_capacity
            : scenario.scenario?.compute_capacity,
        ...numberField(
          runtimeConfig.scenario,
          "compute_cpu_gflops_fp64",
          scenario.scenario?.compute_cpu_gflops_fp64
        ),
        ...numberField(
          runtimeConfig.scenario,
          "compute_gpu_tflops_fp32",
          scenario.scenario?.compute_gpu_tflops_fp32
        ),
        ...numberField(
          runtimeConfig.scenario,
          "compute_gpu_tflops_fp16",
          scenario.scenario?.compute_gpu_tflops_fp16
        ),
        ...numberField(
          runtimeConfig.scenario,
          "compute_npu_tops_int8",
          scenario.scenario?.compute_npu_tops_int8
        ),
        ...numberField(
          runtimeConfig.scenario,
          "compute_memory_gb",
          scenario.scenario?.compute_memory_gb
        ),
        ...numberField(
          runtimeConfig.scenario,
          "compute_storage_gb",
          scenario.scenario?.compute_storage_gb
        ),
        compute_scheduling_policy:
          typeof runtimeConfig.scenario.compute_scheduling_policy === "string"
            ? runtimeConfig.scenario.compute_scheduling_policy
            : scenario.scenario?.compute_scheduling_policy,
        orbit: isRecord(runtimeConfig.scenario.orbit)
          ? {
              ...scenario.scenario?.orbit,
              update_interval_seconds:
                typeof runtimeConfig.scenario.orbit.update_interval_seconds === "number"
                  ? runtimeConfig.scenario.orbit.update_interval_seconds
                  : scenario.scenario?.orbit?.update_interval_seconds,
              plane_count:
                typeof runtimeConfig.scenario.orbit.plane_count === "number"
                  ? runtimeConfig.scenario.orbit.plane_count
                  : scenario.scenario?.orbit?.plane_count,
              altitude_m:
                typeof runtimeConfig.scenario.orbit.altitude_m === "number"
                  ? runtimeConfig.scenario.orbit.altitude_m
                  : scenario.scenario?.orbit?.altitude_m,
              inclination_deg:
                typeof runtimeConfig.scenario.orbit.inclination_deg === "number"
                  ? runtimeConfig.scenario.orbit.inclination_deg
                  : scenario.scenario?.orbit?.inclination_deg
            }
          : scenario.scenario?.orbit,
        traffic_model: mergeTrafficModelConfig(
          scenario.scenario?.traffic_model,
          runtimeConfig.scenario
        )
      }
    : scenario.scenario;
  const network = isRecord(runtimeConfig.network)
    ? {
        ...scenario.network,
        application_protocol:
          typeof runtimeConfig.network.application_protocol === "string"
            ? runtimeConfig.network.application_protocol
            : scenario.network?.application_protocol,
        transport_protocol:
          typeof runtimeConfig.network.transport_protocol === "string"
            ? runtimeConfig.network.transport_protocol
            : scenario.network?.transport_protocol,
        transport_loss_rate:
          typeof runtimeConfig.network.transport_loss_rate === "number"
            ? runtimeConfig.network.transport_loss_rate
            : scenario.network?.transport_loss_rate,
        transport_congestion_window_segments:
          typeof runtimeConfig.network.transport_congestion_window_segments === "number"
            ? runtimeConfig.network.transport_congestion_window_segments
            : scenario.network?.transport_congestion_window_segments,
        routing_protocol:
          typeof runtimeConfig.network.routing_protocol === "string"
            ? runtimeConfig.network.routing_protocol
            : scenario.network?.routing_protocol,
        datalink_mac_protocol:
          typeof runtimeConfig.network.datalink_mac_protocol === "string"
            ? runtimeConfig.network.datalink_mac_protocol
            : scenario.network?.datalink_mac_protocol,
        routing_latency_weight:
          typeof runtimeConfig.network.routing_latency_weight === "number"
            ? runtimeConfig.network.routing_latency_weight
            : scenario.network?.routing_latency_weight,
        routing_inverse_capacity_weight:
          typeof runtimeConfig.network.routing_inverse_capacity_weight === "number"
            ? runtimeConfig.network.routing_inverse_capacity_weight
            : scenario.network?.routing_inverse_capacity_weight,
        routing_hop_weight:
          typeof runtimeConfig.network.routing_hop_weight === "number"
            ? runtimeConfig.network.routing_hop_weight
            : scenario.network?.routing_hop_weight,
        carrier_frequency_hz:
          typeof runtimeConfig.network.carrier_frequency_hz === "number"
            ? runtimeConfig.network.carrier_frequency_hz
            : scenario.network?.carrier_frequency_hz,
        channel_bandwidth_hz:
          typeof runtimeConfig.network.channel_bandwidth_hz === "number"
            ? runtimeConfig.network.channel_bandwidth_hz
            : scenario.network?.channel_bandwidth_hz,
        rain_rate_mm_h:
          typeof runtimeConfig.network.rain_rate_mm_h === "number"
            ? runtimeConfig.network.rain_rate_mm_h
            : scenario.network?.rain_rate_mm_h,
        rain_attenuation_coefficient_db_per_km_per_mm_h:
          typeof runtimeConfig.network.rain_attenuation_coefficient_db_per_km_per_mm_h ===
          "number"
            ? runtimeConfig.network.rain_attenuation_coefficient_db_per_km_per_mm_h
            : scenario.network?.rain_attenuation_coefficient_db_per_km_per_mm_h,
        rain_effective_path_km:
          typeof runtimeConfig.network.rain_effective_path_km === "number"
            ? runtimeConfig.network.rain_effective_path_km
            : scenario.network?.rain_effective_path_km,
        antenna_diameter_m:
          typeof runtimeConfig.network.antenna_diameter_m === "number"
            ? runtimeConfig.network.antenna_diameter_m
            : scenario.network?.antenna_diameter_m,
        antenna_aperture_efficiency:
          typeof runtimeConfig.network.antenna_aperture_efficiency === "number"
            ? runtimeConfig.network.antenna_aperture_efficiency
            : scenario.network?.antenna_aperture_efficiency,
        transmit_power_dbw:
          typeof runtimeConfig.network.transmit_power_dbw === "number"
            ? runtimeConfig.network.transmit_power_dbw
            : scenario.network?.transmit_power_dbw,
        system_loss_db:
          typeof runtimeConfig.network.system_loss_db === "number"
            ? runtimeConfig.network.system_loss_db
            : scenario.network?.system_loss_db,
        noise_temperature_k:
          typeof runtimeConfig.network.noise_temperature_k === "number"
            ? runtimeConfig.network.noise_temperature_k
            : scenario.network?.noise_temperature_k,
        space_link_mode:
          typeof runtimeConfig.network.space_link_mode === "string" ||
          runtimeConfig.network.space_link_mode === null
            ? runtimeConfig.network.space_link_mode
            : scenario.network?.space_link_mode,
        max_space_link_candidates_per_satellite:
          typeof runtimeConfig.network.max_space_link_candidates_per_satellite === "number"
            ? runtimeConfig.network.max_space_link_candidates_per_satellite
            : scenario.network?.max_space_link_candidates_per_satellite,
        batch_space_link_update_limit:
          typeof runtimeConfig.network.batch_space_link_update_limit === "number"
            ? runtimeConfig.network.batch_space_link_update_limit
            : scenario.network?.batch_space_link_update_limit
      }
    : scenario.network;
  const ui = isRecord(runtimeConfig.ui)
    ? {
        ...scenario.ui,
        visualization: isRecord(runtimeConfig.ui.visualization)
          ? {
              ...scenario.ui?.visualization,
              satellites:
                typeof runtimeConfig.ui.visualization.satellites === "boolean"
                  ? runtimeConfig.ui.visualization.satellites
                  : scenario.ui?.visualization?.satellites,
              links:
                typeof runtimeConfig.ui.visualization.links === "boolean"
                  ? runtimeConfig.ui.visualization.links
                  : scenario.ui?.visualization?.links,
              users:
                typeof runtimeConfig.ui.visualization.users === "boolean"
                  ? runtimeConfig.ui.visualization.users
                  : scenario.ui?.visualization?.users,
              metrics:
                typeof runtimeConfig.ui.visualization.metrics === "boolean"
                  ? runtimeConfig.ui.visualization.metrics
                  : scenario.ui?.visualization?.metrics
            }
          : scenario.ui?.visualization
      }
    : scenario.ui;
  return {
    ...scenario,
    scenario: scenarioSection,
    network,
    ui
  };
}

type TrafficModelConfig = NonNullable<NonNullable<ScenarioConfig["scenario"]>["traffic_model"]>;

function mergeTrafficModelConfig(
  base: TrafficModelConfig | undefined,
  runtimeScenario: Record<string, unknown>
): TrafficModelConfig | undefined {
  const rawTraffic = isRecord(runtimeScenario.traffic_model)
    ? runtimeScenario.traffic_model
    : null;
  const hasTopLevelSmoothing =
    "initial_workload_smoothing_enabled" in runtimeScenario ||
    "initial_workload_window_s" in runtimeScenario ||
    "max_initial_events_per_tick" in runtimeScenario ||
    "workload_smoothing_mode" in runtimeScenario;
  if (rawTraffic === null && !hasTopLevelSmoothing) {
    return base;
  }
  const traffic: Record<string, unknown> = rawTraffic ?? {};
  const merged: TrafficModelConfig = { ...base };
  for (const key of [
    "flow_interval_seconds",
    "task_interval_seconds",
    "flow_demand_capacity",
    "task_compute_demand",
    "task_data_size",
    "output_data_size",
    "initial_workload_window_s",
    "max_initial_events_per_tick"
  ] as const) {
    const value = numberFromRuntimeScenario(runtimeScenario, traffic, key);
    if (value !== undefined) {
      merged[key] = value;
    }
  }
  const smoothingEnabled = booleanFromRuntimeScenario(
    runtimeScenario,
    traffic,
    "initial_workload_smoothing_enabled"
  );
  if (smoothingEnabled !== undefined) {
    merged.initial_workload_smoothing_enabled = smoothingEnabled;
  }
  const smoothingMode = stringFromRuntimeScenario(
    runtimeScenario,
    traffic,
    "workload_smoothing_mode"
  );
  if (smoothingMode !== undefined) {
    merged.workload_smoothing_mode = smoothingMode;
  }
  for (const key of ["traffic_class", "destination_type"] as const) {
    const value = stringFromRuntimeScenario(runtimeScenario, traffic, key);
    if (value !== undefined) {
      merged[key] = value;
    }
  }
  return merged;
}

function numberFromRuntimeScenario(
  runtimeScenario: Record<string, unknown>,
  rawTraffic: Record<string, unknown>,
  key: string
): number | undefined {
  if (typeof runtimeScenario[key] === "number") {
    return runtimeScenario[key];
  }
  return typeof rawTraffic[key] === "number" ? rawTraffic[key] : undefined;
}

function booleanFromRuntimeScenario(
  runtimeScenario: Record<string, unknown>,
  rawTraffic: Record<string, unknown>,
  key: string
): boolean | undefined {
  if (typeof runtimeScenario[key] === "boolean") {
    return runtimeScenario[key];
  }
  return typeof rawTraffic[key] === "boolean" ? rawTraffic[key] : undefined;
}

function stringFromRuntimeScenario(
  runtimeScenario: Record<string, unknown>,
  rawTraffic: Record<string, unknown>,
  key: string
): string | undefined {
  if (typeof runtimeScenario[key] === "string") {
    return runtimeScenario[key];
  }
  return typeof rawTraffic[key] === "string" ? rawTraffic[key] : undefined;
}

function connectionStateLabel(state: "connecting" | "live" | "degraded"): string {
  if (state === "connecting") {
    return "连接中";
  }
  if (state === "live") {
    return "已连接";
  }
  return "连接异常";
}

export interface ConnectionDiagnosticItem {
  channel: RuntimeConnectionChannel;
  label: string;
  status: RuntimeConnectionStatus;
  statusLabel: string;
  detail?: string;
  description?: string;
}

export function connectionDiagnosticItems(
  health: RuntimeConnectionHealth,
  streamDiagnostics?: RuntimeStatusPayload["stream_diagnostics_v1"],
  consumerCursors?: RuntimeStreamConsumerCursors
): readonly ConnectionDiagnosticItem[] {
  return (["http", "control", "events", "state"] as const).map((channel) => {
    const detail = connectionDiagnosticDetail(channel, streamDiagnostics, consumerCursors);
    const description = connectionDiagnosticDescription(
      channel,
      health[channel],
      streamDiagnostics,
      consumerCursors
    );
    return {
      channel,
      label: connectionChannelLabel(channel),
      status: health[channel],
      statusLabel: connectionStatusLabel(health[channel]),
      ...(detail === undefined ? {} : { detail }),
      ...(description === undefined ? {} : { description })
    };
  });
}

function connectionChannelLabel(channel: RuntimeConnectionChannel): string {
  if (channel === "http") {
    return "HTTP";
  }
  if (channel === "control") {
    return "控制";
  }
  if (channel === "events") {
    return "事件";
  }
  return "状态";
}

function connectionStatusLabel(status: RuntimeConnectionStatus): string {
  if (status === "idle") {
    return "空闲";
  }
  if (status === "connecting") {
    return "连接中";
  }
  if (status === "live") {
    return "正常";
  }
  return "异常";
}

function connectionDiagnosticDetail(
  channel: RuntimeConnectionChannel,
  streamDiagnostics: RuntimeStatusPayload["stream_diagnostics_v1"] | undefined,
  consumerCursors: RuntimeStreamConsumerCursors | undefined
): string | undefined {
  if (streamDiagnostics === undefined) {
    return undefined;
  }
  if (channel === "control") {
    return `推进 ${formatInteger(streamDiagnostics.tick_count)} tick`;
  }
  const stream =
    channel === "events"
      ? streamDiagnostics.event_stream
      : channel === "state"
        ? streamDiagnostics.state_stream
        : undefined;
  if (stream === undefined) {
    return undefined;
  }
  const consumedCursor =
    channel === "events" || channel === "state" ? consumerCursors?.[channel] : undefined;
  const consumed =
    consumedCursor === undefined ? "" : ` / 已收 ${formatInteger(consumedCursor)}`;
  const lag =
    consumedCursor === undefined
      ? ""
      : ` / 滞后 ${formatInteger(Math.max(0, stream.next_cursor - consumedCursor))}`;
  const dropped =
    stream.total_dropped_count > 0
      ? ` / 丢弃 ${formatInteger(stream.total_dropped_count)}`
      : "";
  return `游标 ${formatInteger(stream.next_cursor)} / 留存 ${formatInteger(
    stream.retained_count
  )}${consumed}${lag}${dropped}`;
}

function connectionDiagnosticDescription(
  channel: RuntimeConnectionChannel,
  status: RuntimeConnectionStatus,
  streamDiagnostics: RuntimeStatusPayload["stream_diagnostics_v1"] | undefined,
  consumerCursors: RuntimeStreamConsumerCursors | undefined
): string | undefined {
  const label = connectionChannelLabel(channel);
  const statusLabel = connectionStatusLabel(status);
  if (channel === "control" && streamDiagnostics !== undefined) {
    return `控制通道诊断：连接${statusLabel}，服务端推进循环 ${streamDiagnostics.advance_loop_state}，累计推进 ${formatInteger(
      streamDiagnostics.tick_count
    )} tick。事件数只统计离散仿真事件，tick 表示后端实时推进心跳。`;
  }
  const stream =
    channel === "events"
      ? streamDiagnostics?.event_stream
      : channel === "state"
        ? streamDiagnostics?.state_stream
        : undefined;
  if (stream === undefined) {
    return undefined;
  }
  const consumedCursor =
    channel === "events" || channel === "state" ? consumerCursors?.[channel] : undefined;
  const lag =
    consumedCursor === undefined ? undefined : Math.max(0, stream.next_cursor - consumedCursor);
  const consumedText =
    consumedCursor === undefined
      ? "浏览器消费游标尚未上报"
      : `浏览器已消费到 ${formatInteger(consumedCursor)}，滞后 ${formatInteger(lag ?? 0)} 条`;
  const droppedText =
    stream.total_dropped_count > 0
      ? `累计丢弃 ${formatInteger(stream.total_dropped_count)} 条`
      : "未发生丢弃";
  const overflowText = stream.overflow_risk
    ? "当前接近缓冲区上限，可能需要降低刷新频率或检查后端推进速度"
    : "当前没有缓冲区溢出风险";
  return `${label}流诊断：连接${statusLabel}，后端下一游标 ${formatInteger(
    stream.next_cursor
  )}，留存 ${formatInteger(stream.retained_count)} 条，${consumedText}，${droppedText}。${overflowText}。`;
}

function runtimeStatusIsProgressing(status: RuntimeStatusPayload): boolean {
  return (
    status.status === "RUNNING" &&
    status.lifecycle_state !== "COMPLETED" &&
    status.lifecycle_state !== "ERROR" &&
    status.lifecycle_state !== "STOPPED"
  );
}

function runtimeProgressAnchorIsRunning(anchor: RuntimeProgressAnchor): boolean {
  return (
    anchor.status === "RUNNING" &&
    anchor.lifecycleState !== "COMPLETED" &&
    anchor.lifecycleState !== "ERROR" &&
    anchor.lifecycleState !== "STOPPED"
  );
}

function finiteNumberOrZero(value: unknown): number {
  return typeof value === "number" && Number.isFinite(value) ? value : 0;
}

function runtimeStatusLabel(runtimeStatus: RuntimeStatusPayload): string {
  if (
    runtimeStatus.status === "COMPLETED" ||
    runtimeStatus.lifecycle_state === "COMPLETED"
  ) {
    return "已完成";
  }
  if (runtimeStatus.status === "RUNNING") {
    return "运行中";
  }
  if (runtimeStatus.status === "PAUSED") {
    return "已暂停";
  }
  return "已停止";
}

function formatInteger(value: number): string {
  return Math.round(value).toLocaleString("zh-CN");
}

function formatPercent(value: number): string {
  return value.toLocaleString("zh-CN", {
    maximumFractionDigits: 1,
    minimumFractionDigits: 0
  });
}

function formatMilliseconds(value: number): string {
  return `${Math.max(0, value).toLocaleString("zh-CN", {
    maximumFractionDigits: 1,
    minimumFractionDigits: 0
  })} ms`;
}

function formatDurationCompact(seconds: number): string {
  if (seconds < 60) {
    return `${Math.round(seconds)}秒`;
  }
  if (seconds < 3600) {
    return `${Math.floor(seconds / 60)}分${Math.round(seconds % 60)}秒`;
  }
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  return `${hours}时${minutes}分`;
}

function defaultRuntimeStatus(): RuntimeStatusPayload {
  return {
    status: "STOPPED",
    mode: "REAL_TIME",
    speed_factor: 1,
    seed: 20260703,
    duration: 600,
    config_version: 0,
    last_action: "INIT"
  };
}

function handleControlMessage(
  message: ControlAck,
  setRuntimeStatus: (updater: (previous: RuntimeStatusPayload) => RuntimeStatusPayload) => void
): void {
  if (message.status === undefined) {
    return;
  }
  setRuntimeStatus((previous) => ({
    ...previous,
    ...message.status
  }));
}

function handleGeneratedConfig(
  message: ControlAck,
  setGeneratedConfig: (config: GeneratedScenarioConfig | null) => void
): void {
  if (message.generated_config !== undefined) {
    setGeneratedConfig(message.generated_config);
  }
}

export function controlErrorMessage(error: string | undefined): string {
  if (error === undefined || error.length === 0) {
    return "控制命令执行失败，请检查后端运行状态。";
  }
  if (error.includes("scale safety check failed")) {
    return [
      "当前配置超出实时交互演示安全上限。",
      "请缩短仿真时长、降低卫星/算力节点数量，或使用离线批处理模式。"
    ].join("");
  }
  return error;
}

export function runtimeExportCompareErrorMessage(error: unknown): string {
  const message = error instanceof Error ? error.message : String(error);
  return `复盘包配置对比加载失败：${message}`;
}

export function runtimeExportReviewSummaryErrorMessage(error: unknown): string {
  const message = error instanceof Error ? error.message : String(error);
  return `复盘包审阅摘要加载失败：${message}`;
}

export function runtimeExportManifestErrorMessage(error: unknown): string {
  const message = error instanceof Error ? error.message : String(error);
  return `复盘包 manifest 加载失败：${message}`;
}

export function runtimeExportDiagnosticsBundleErrorMessage(error: unknown): string {
  const message = error instanceof Error ? error.message : String(error);
  return `复盘包诊断包加载失败：${message}`;
}

export function runtimeExportServiceLifecycleTraceErrorMessage(error: unknown): string {
  const message = error instanceof Error ? error.message : String(error);
  return `runtime export service lifecycle trace load failed: ${message}`;
}

export function runtimeExportUserServiceRequestSummaryErrorMessage(
  error: unknown
): string {
  const message = error instanceof Error ? error.message : String(error);
  return `runtime export user service request summary load failed: ${message}`;
}

export function runtimeExportRouteDetailIndexErrorMessage(error: unknown): string {
  const message = error instanceof Error ? error.message : String(error);
  return `复盘包路由证据索引加载失败：${message}`;
}

export function runtimeExportRouteDetailItemErrorMessage(error: unknown): string {
  const message = error instanceof Error ? error.message : String(error);
  return `package route detail load failed: ${message}`;
}

export function runtimeExportRouteComparisonReviewReportErrorMessage(
  error: unknown
): string {
  const message = error instanceof Error ? error.message : String(error);
  return `route comparison review report load failed: ${message}`;
}

export function runtimeExportServiceTraceComparisonReviewReportErrorMessage(
  error: unknown
): string {
  const message = error instanceof Error ? error.message : String(error);
  return `service trace comparison review report load failed: ${message}`;
}

export function runtimeExportPackageAuditIndexErrorMessage(error: unknown): string {
  const message = error instanceof Error ? error.message : String(error);
  return `export package audit index load failed: ${message}`;
}

export function runtimeExportScenarioReviewBundleErrorMessage(error: unknown): string {
  const message = error instanceof Error ? error.message : String(error);
  return `scenario review bundle load failed: ${message}`;
}

export function runtimeExportScenarioReviewChecklistErrorMessage(error: unknown): string {
  const message = error instanceof Error ? error.message : String(error);
  return `scenario review checklist load failed: ${message}`;
}

export function runtimeExportRouteComparisonReviewSaveErrorMessage(
  error: unknown
): string {
  const message = error instanceof Error ? error.message : String(error);
  return `route comparison review report save failed: ${message}`;
}

export function runtimeExportServiceTraceComparisonReviewSaveErrorMessage(
  error: unknown
): string {
  const message = error instanceof Error ? error.message : String(error);
  return `service trace comparison review report save failed: ${message}`;
}

export function runtimeExportScenarioReviewChecklistSaveErrorMessage(
  error: unknown
): string {
  const message = error instanceof Error ? error.message : String(error);
  return `scenario review checklist save failed: ${message}`;
}

export function runtimeExportRestorePreflightErrorMessage(error: unknown): string {
  const message = error instanceof Error ? error.message : String(error);
  return `复盘包恢复预检加载失败：${message}`;
}

export function userConfigurationContractErrorMessage(error: unknown): string {
  const message = error instanceof Error ? error.message : String(error);
  return `用户配置契约加载失败：${message}`;
}

type RuntimeWebSocketChannel = "control" | "events" | "state";

export function runtimeWebSocketErrorMessage(channel: RuntimeWebSocketChannel): string {
  const channelLabel =
    channel === "control" ? "控制通道" : channel === "events" ? "事件流" : "状态流";
  return [
    `${channelLabel}连接中断。`,
    "请执行 scripts\\sees_launcher.ps1 status 检查后端和前端是否 HTTP healthy，",
    "必要时运行 restart_leo_twin.bat。"
  ].join("");
}

function numberField(
  record: Record<string, unknown>,
  key: string,
  fallback: number | undefined
): Record<string, number> {
  const value = record[key];
  if (typeof value === "number") {
    return { [key]: value };
  }
  if (fallback !== undefined) {
    return { [key]: fallback };
  }
  return {};
}

function scenarioControlValues(
  scenarioConfig: ScenarioConfig | null,
  renderedSatellites: number
): ScenarioControlValues {
  const visualization = scenarioConfig?.ui?.visualization;
  return {
    satellite_count:
      scenarioConfig?.scenario?.satellite_count ??
      scenarioConfig?.render?.max_satellites ??
      renderedSatellites,
    user_count:
      scenarioConfig?.scenario?.user_count ?? scenarioConfig?.ground_users?.length ?? 1000,
    compute_nodes: scenarioConfig?.scenario?.compute_nodes ?? 10,
    compute_capacity: scenarioConfig?.scenario?.compute_capacity ?? 10,
    compute_cpu_gflops_fp64: scenarioConfig?.scenario?.compute_cpu_gflops_fp64 ?? 0,
    compute_gpu_tflops_fp32: scenarioConfig?.scenario?.compute_gpu_tflops_fp32 ?? 0,
    compute_gpu_tflops_fp16: scenarioConfig?.scenario?.compute_gpu_tflops_fp16 ?? 0,
    compute_npu_tops_int8: scenarioConfig?.scenario?.compute_npu_tops_int8 ?? 0,
    compute_memory_gb: scenarioConfig?.scenario?.compute_memory_gb ?? 0,
    compute_storage_gb: scenarioConfig?.scenario?.compute_storage_gb ?? 0,
    compute_scheduling_policy:
      scenarioConfig?.scenario?.compute_scheduling_policy ?? "FIFO",
    orbit: {
      update_interval_seconds:
        scenarioConfig?.scenario?.orbit?.update_interval_seconds ?? 60,
      plane_count: scenarioConfig?.scenario?.orbit?.plane_count ?? 12,
      altitude_km: (scenarioConfig?.scenario?.orbit?.altitude_m ?? 550_000) / 1000,
      inclination_deg: scenarioConfig?.scenario?.orbit?.inclination_deg ?? 53
    },
    traffic_model: {
      flow_interval_seconds:
        scenarioConfig?.scenario?.traffic_model?.flow_interval_seconds ?? 60,
      task_interval_seconds:
        scenarioConfig?.scenario?.traffic_model?.task_interval_seconds ?? 60,
      flow_demand_capacity:
        scenarioConfig?.scenario?.traffic_model?.flow_demand_capacity ?? 25,
      task_compute_demand:
        scenarioConfig?.scenario?.traffic_model?.task_compute_demand ?? 20,
      task_data_size: scenarioConfig?.scenario?.traffic_model?.task_data_size ?? 2,
      traffic_class:
        scenarioConfig?.scenario?.traffic_model?.traffic_class ?? "COMPUTE_SERVICE",
      destination_type:
        scenarioConfig?.scenario?.traffic_model?.destination_type ?? "COMPUTE_NODE",
      output_data_size: scenarioConfig?.scenario?.traffic_model?.output_data_size ?? 0
    },
    visualization: {
      satellites: visualization?.satellites ?? true,
      links: visualization?.links ?? true,
      users: visualization?.users ?? true,
      metrics: visualization?.metrics ?? true
    },
    network: {
      application_protocol: scenarioConfig?.network?.application_protocol ?? "TASK_OFFLOAD_FLOW",
      transport_protocol: scenarioConfig?.network?.transport_protocol ?? "TCP",
      transport_loss_rate: scenarioConfig?.network?.transport_loss_rate ?? 0,
      transport_congestion_window_segments:
        scenarioConfig?.network?.transport_congestion_window_segments ?? 0,
      routing_protocol: scenarioConfig?.network?.routing_protocol ?? "LINK_STATE",
      datalink_mac_protocol: scenarioConfig?.network?.datalink_mac_protocol ?? "TDMA",
      routing_latency_weight: scenarioConfig?.network?.routing_latency_weight ?? 1,
      routing_inverse_capacity_weight:
        scenarioConfig?.network?.routing_inverse_capacity_weight ?? 0,
      routing_hop_weight: scenarioConfig?.network?.routing_hop_weight ?? 0,
      carrier_frequency_ghz:
        (scenarioConfig?.network?.carrier_frequency_hz ?? 20_000_000_000) / 1_000_000_000,
      channel_bandwidth_mhz:
        (scenarioConfig?.network?.channel_bandwidth_hz ?? 100_000_000) / 1_000_000,
      rain_rate_mm_h: scenarioConfig?.network?.rain_rate_mm_h ?? 0,
      rain_attenuation_coefficient_db_per_km_per_mm_h:
        scenarioConfig?.network?.rain_attenuation_coefficient_db_per_km_per_mm_h ?? 0,
      rain_effective_path_km: scenarioConfig?.network?.rain_effective_path_km ?? 0,
      antenna_diameter_m: scenarioConfig?.network?.antenna_diameter_m ?? 0.45,
      antenna_aperture_efficiency:
        scenarioConfig?.network?.antenna_aperture_efficiency ?? 0.65,
      transmit_power_dbw: scenarioConfig?.network?.transmit_power_dbw ?? 20,
      system_loss_db: scenarioConfig?.network?.system_loss_db ?? 1,
      noise_temperature_k: scenarioConfig?.network?.noise_temperature_k ?? 290
    }
  };
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
