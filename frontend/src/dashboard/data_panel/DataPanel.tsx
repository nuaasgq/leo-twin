import { memo, useEffect, useState, type MouseEvent } from "react";
import {
  Area,
  AreaChart,
  Cell,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";

import {
  ConfigurationExplanationV2,
  DashboardInformationArchitectureV3,
  FidelitySummary,
  GeneratedScenarioConfig,
  LargeDetailPaginationCollectionV2,
  LargeDetailPaginationContractV2,
  RuntimeComputeNodeDetailPageV1,
  TrafficDemandSummary,
  RuntimeExportCatalogV1,
  RuntimeExportCatalogFileV1,
  RuntimeExportCatalogRecordV1,
  RuntimeExportDiagnosticsBundleV1,
  RuntimeExportPackageCompareV1,
  RuntimeExportRouteComparisonReviewV1,
  RuntimeExportRouteComparisonReviewReportV1,
  RuntimeExportRouteComparisonReviewReportRecordV1,
  RuntimeExportRouteDetailItemV1,
  RuntimeExportRouteDetailIndexRouteV1,
  RuntimeExportRouteDetailIndexV1,
  RuntimeExportRouteDetailPageV1,
  RuntimeExportReproducibilityBoundaryV1,
  RuntimeExportScenarioReviewBundleV1,
  RuntimeExportScenarioReviewChecklistRecordV1,
  RuntimeExportScenarioReviewChecklistV1,
  RuntimeExportServiceTracePageV1,
  RuntimeExportReviewSummaryV1,
  RuntimeExportRestoreCommandResultV1,
  RuntimeExportRestorePreflightV1,
  RuntimeComputeTaskTimelineSummaryV1,
  RuntimeExportUserServiceRequestPageV1,
  RuntimeExportUserServiceRequestEvidenceV2,
  RuntimeKpiSampleV1,
  RuntimeKpiTimeSeriesV1,
  RuntimeExportHistoryV1,
  RuntimeMetricsSummary,
  RuntimeExportNetworkKpiBenchmarkValidationEvidenceV1,
  RuntimeNetworkKpiCredibilityV1,
  RuntimeNetworkKpiBenchmarkValidationV1,
  RuntimeNetworkKpiProvenanceV2,
  RuntimeNetworkQualityProvenanceV1,
  RuntimeExportPackageAuditIndexV1,
  RuntimeComputeNodeDetailItemV1,
  RuntimeNodeDetailCardV1,
  RuntimeNodeDetailPageV1,
  RuntimeNodeDetailSummaryV1,
  RuntimeRouteExplanationItemV1,
  RuntimeReproducibilityManifestV1,
  RuntimeRouteExplanationSummaryV1,
  RuntimeRouteProvenanceTrustSummaryV1,
  RuntimeSatelliteServiceItemV1,
  RuntimeSatelliteServiceSummaryV1,
  RuntimeSatelliteKpiHistoryV1,
  RuntimeSatelliteKpiSlicesV1,
  RuntimeServiceDetailItemV1,
  RuntimeServiceDetailPageV1,
  RuntimeServiceLatencyHistoryV1,
  RuntimeServiceLifecycleTraceV2,
  RuntimeServiceTraceDetailV2,
  RuntimeStatusPayload,
  RuntimeUserRequestHistoryV1,
  RuntimeUserRequestItemV1,
  RuntimeUserRequestSummaryV1,
  RuntimeUserServiceRequestSummaryV2,
  UserConfigurationExportV1,
  UserConfigurationReferenceFieldV1,
  UserConfigurationReferenceV1,
  UserConfigurationSchemaV2,
  UserConfigurationTemplateCatalogV1,
  UserConfigurationValidationApplyCommandV1,
  UserConfigurationValidationReportV1
} from "../../core/event_types";
import {
  runtimeExportArchiveHref,
  runtimeExportPackageArchiveHref,
  runtimeExportPackageCompareHref,
  runtimeExportPackageFileHref,
  runtimeExportPackageHandoffReportHref,
  runtimeExportPackageManifestHref,
  runtimeExportPackageRecordHref,
  runtimeExportPackageRouteDetailHref,
  runtimeExportPackageReviewSummaryHref,
  runtimeExportRestorePreflightHref,
  userConfigurationExportHref,
  userConfigurationReferenceHref,
  userConfigurationSchemaHref,
  userConfigurationTemplatesHref,
  userConfigurationValidateHref,
  userConfigurationValidateTextHref
} from "../../app/api";
import { runtimeSpeedFactorLabel } from "../../runtime_display";
import { WorldSnapshot } from "../../state/snapshot_engine";
import { ChannelHealthPanel } from "../channel_health/ChannelHealthPanel";
import { CouplingFeedbackPanel } from "../coupling_feedback/CouplingFeedbackPanel";
import { ComputeQueuePanel } from "../compute_queue/ComputeQueuePanel";
import { ComputeView } from "../compute_view/ComputeView";
import { DomainSummary } from "../domain_summary/DomainSummary";
import { GroundTrackPanel } from "../ground_track/GroundTrackPanel";
import { KpiPanel } from "../kpi_panel/KpiPanel";
import { LinkProtocolPanel } from "../link_protocol/LinkProtocolPanel";
import { NetworkView } from "../network_view/NetworkView";
import { OrbitPanel } from "../orbit_panel/OrbitPanel";
import { SystemHealth } from "../system_health/SystemHealth";
import { TopologyChangePanel } from "../topology_change/TopologyChangePanel";

export interface DataPanelSummary {
  simTime: number;
  eventCount: number;
  eventRate: number;
  satelliteCount: number;
  groundUserCount: number;
  activeLinks: number;
  spaceLinks: number;
  accessLinks: number;
  availableRoutes: number;
  totalRoutes: number;
  routeAvailabilityPercent: number;
  averageRouteLatency: number;
  averageRouteCapacity: number;
  averageRouteHops: number;
  maxRouteHops: number;
  runningTasks: number;
  finishedTasks: number;
  deadlineMissedTasks: number;
  computeNodes: number;
  networkWaiting: number;
  couplingHealth: number;
}

export interface RuntimeDetailPages {
  users?: RuntimeUserRequestSummaryV1 | RuntimeUserServiceRequestSummaryV2 | null;
  satellites?: RuntimeSatelliteServiceSummaryV1 | null;
  nodes?: RuntimeNodeDetailPageV1 | null;
  routes?: RuntimeRouteExplanationSummaryV1 | null;
  services?: RuntimeServiceDetailPageV1 | null;
  serviceTraces?: RuntimeServiceLifecycleTraceV2 | null;
  computeNodes?: RuntimeComputeNodeDetailPageV1 | null;
}

export interface RuntimeDetailCursorControls {
  users?: RuntimeDetailCursorControl | null;
  satellites?: RuntimeDetailCursorControl | null;
  routes?: RuntimeDetailCursorControl | null;
  services?: RuntimeDetailCursorControl | null;
  serviceTraces?: RuntimeDetailCursorControl | null;
  computeNodes?: RuntimeDetailCursorControl | null;
}

export interface RuntimeDetailCursorControl {
  loading?: boolean;
  error?: string | null;
  onCursorChange?: (cursor: number, filters?: RuntimeDetailCursorFilters) => void;
  onRefresh?: (filters?: RuntimeDetailCursorFilters) => void;
}

export interface RuntimeDetailCursorFilters {
  query?: string;
  availability?: string;
  businessType?: string;
  bottleneckComponent?: string;
  terminalState?: string;
  computeNodeId?: string;
  stageKind?: string;
  terminalReason?: string;
}

export interface RuntimeSelectedNodeDetails {
  user?: RuntimeNodeDetailCardV1 | null;
  satellite?: RuntimeNodeDetailCardV1 | null;
  route?: RuntimeRouteExplanationItemV1 | null;
  service?: RuntimeServiceDetailItemV1 | null;
  serviceTrace?: RuntimeServiceTraceDetailV2 | null;
  computeNode?: RuntimeComputeNodeDetailItemV1 | null;
}

export interface RuntimeExactDetailRequestState {
  entityId?: string | null;
  loading?: boolean;
  error?: string | null;
}

export interface RuntimeSelectedNodeDetailRequests {
  user?: RuntimeExactDetailRequestState | null;
  satellite?: RuntimeExactDetailRequestState | null;
  route?: RuntimeExactDetailRequestState | null;
  service?: RuntimeExactDetailRequestState | null;
  serviceTrace?: RuntimeExactDetailRequestState | null;
  computeNode?: RuntimeExactDetailRequestState | null;
}

const FALLBACK_USER_DETAIL_PAGE_SIZE = 80;
const FALLBACK_SATELLITE_DETAIL_PAGE_SIZE = 120;
const ROUTE_COMPARISON_REVIEW_REPORT_FILENAME =
  "route_comparison_review_report_v1.json";
const EXPORT_PACKAGE_AUDIT_INDEX_FILENAME = "export_package_audit_index_v1.json";
const PACKAGE_HANDOFF_REPORT_FILENAME = "package_handoff_report_v1.md";
const SCENARIO_REVIEW_BUNDLE_FILENAME = "scenario_review_bundle_v1.json";
const DEFAULT_USER_CONFIGURATION_VALIDATE_TEXT = `{
  "scenario": {
    "satellite_count": 72,
    "compute_nodes": 72
  },
  "runtime": {
    "duration": 600,
    "seed": 20260703
  }
}`;
const DEFAULT_USER_CONFIGURATION_VALIDATE_YAML_TEXT = `scenario:
  satellite_count: 72
  compute_nodes: 72
runtime:
  duration: 600
  seed: 20260703
`;
export type UserConfigurationPreflightMode =
  | "json_mapping"
  | "auto_text"
  | "yaml_text"
  | "json_text";
type DataPanelRouteComparisonReviewReportStatusFilter =
  | "ALL"
  | "MATCH"
  | "DIFFERENT"
  | "UNAVAILABLE"
  | "ERROR";

export const DataPanel = memo(function DataPanel({
  snapshot,
  runtimeStatus,
  generatedConfig,
  runtimeDetailPages,
  runtimeDetailCursorControls,
  runtimeSelectedNodeDetails,
  runtimeSelectedNodeDetailRequests,
  runtimeExportCatalog,
  runtimeExportCompare,
  runtimeExportReviewSummary,
  runtimeExportManifest,
  runtimeExportDiagnosticsBundle,
  runtimeExportServiceLifecycleTrace,
  runtimeExportServiceTracePage,
  runtimeExportUserServiceRequestPage,
  runtimeExportRouteDetailIndex,
  runtimeExportRouteDetailPage,
  runtimeExportRouteDetailItem,
  runtimeExportRouteComparisonReviewReport,
  runtimeExportPackageAuditIndex,
  runtimeExportScenarioReviewBundle,
  runtimeExportScenarioReviewChecklist,
  runtimeExportRouteDetailItemRouteId,
  runtimeExportComparePackageId,
  runtimeExportCompareLoading,
  runtimeExportCompareError,
  runtimeExportReviewSummaryLoading,
  runtimeExportReviewSummaryError,
  runtimeExportManifestLoading,
  runtimeExportManifestError,
  runtimeExportDiagnosticsBundleLoading,
  runtimeExportDiagnosticsBundleError,
  runtimeExportServiceLifecycleTraceLoading,
  runtimeExportServiceLifecycleTraceError,
  runtimeExportUserServiceRequestPageLoading,
  runtimeExportUserServiceRequestPageError,
  runtimeExportRouteDetailIndexLoading,
  runtimeExportRouteDetailIndexError,
  runtimeExportRouteDetailItemLoading,
  runtimeExportRouteDetailItemError,
  runtimeExportRouteComparisonReviewReportLoading,
  runtimeExportRouteComparisonReviewReportError,
  runtimeExportPackageAuditIndexLoading,
  runtimeExportPackageAuditIndexError,
  runtimeExportScenarioReviewBundleLoading,
  runtimeExportScenarioReviewBundleError,
  runtimeExportScenarioReviewChecklistLoading,
  runtimeExportScenarioReviewChecklistError,
  runtimeExportRouteComparisonReviewSavePendingRouteId,
  runtimeExportRouteComparisonReviewSaveError,
  runtimeExportRouteComparisonReviewSaveReportHash,
  runtimeExportScenarioReviewChecklistSavePending,
  runtimeExportScenarioReviewChecklistSaveError,
  runtimeExportScenarioReviewChecklistSaveHash,
  runtimeExportRestorePreflight,
  runtimeExportRestorePreflightLoading,
  runtimeExportRestorePreflightError,
  runtimeExportRestoreCommandPendingPackageId,
  runtimeExportRestoreCommandError,
  runtimeExportRestoreResult,
  userConfigurationSchema,
  userConfigurationTemplates,
  userConfigurationReference,
  userConfigurationExport,
  userConfigurationContractLoading,
  userConfigurationContractError,
  onUserConfigurationValidate,
  onUserConfigurationValidateText,
  onUserConfigurationApply,
  onRuntimeExportCompareSelect,
  onRuntimeExportRouteDetailPageQueryChange,
  onRuntimeExportServiceTracePageQueryChange,
  onRuntimeExportUserServiceRequestPageQueryChange,
  onRuntimeExportRouteDetailItemSelect,
  onRuntimeExportRouteComparisonReviewSave,
  onRuntimeExportScenarioReviewChecklistSave,
  onRuntimeExportRestore,
  onRuntimeUserDetailSelect,
  onRuntimeSatelliteDetailSelect,
  onRuntimeRouteDetailSelect,
  onRuntimeServiceDetailSelect,
  onRuntimeServiceTraceDetailSelect,
  onRuntimeComputeNodeDetailSelect,
  displaySimTime,
  displayEventCount,
  onNavigateControl
}: {
  snapshot: WorldSnapshot;
  runtimeStatus: RuntimeStatusPayload;
  generatedConfig: GeneratedScenarioConfig | null;
  runtimeDetailPages?: RuntimeDetailPages | null;
  runtimeDetailCursorControls?: RuntimeDetailCursorControls | null;
  runtimeSelectedNodeDetails?: RuntimeSelectedNodeDetails | null;
  runtimeSelectedNodeDetailRequests?: RuntimeSelectedNodeDetailRequests | null;
  runtimeExportCatalog?: RuntimeExportCatalogV1 | null;
  runtimeExportCompare?: RuntimeExportPackageCompareV1 | null;
  runtimeExportReviewSummary?: RuntimeExportReviewSummaryV1 | null;
  runtimeExportManifest?: RuntimeReproducibilityManifestV1 | null;
  runtimeExportDiagnosticsBundle?: RuntimeExportDiagnosticsBundleV1 | null;
  runtimeExportServiceLifecycleTrace?: RuntimeServiceLifecycleTraceV2 | null;
  runtimeExportServiceTracePage?: RuntimeExportServiceTracePageV1 | null;
  runtimeExportUserServiceRequestPage?: RuntimeExportUserServiceRequestPageV1 | null;
  runtimeExportRouteDetailIndex?: RuntimeExportRouteDetailIndexV1 | null;
  runtimeExportRouteDetailPage?: RuntimeExportRouteDetailPageV1 | null;
  runtimeExportRouteDetailItem?: RuntimeExportRouteDetailItemV1 | null;
  runtimeExportRouteComparisonReviewReport?: RuntimeExportRouteComparisonReviewReportV1 | null;
  runtimeExportPackageAuditIndex?: RuntimeExportPackageAuditIndexV1 | null;
  runtimeExportScenarioReviewBundle?: RuntimeExportScenarioReviewBundleV1 | null;
  runtimeExportScenarioReviewChecklist?: RuntimeExportScenarioReviewChecklistV1 | null;
  runtimeExportRouteDetailItemRouteId?: string | null;
  runtimeExportComparePackageId?: string | null;
  runtimeExportCompareLoading?: boolean;
  runtimeExportCompareError?: string | null;
  runtimeExportReviewSummaryLoading?: boolean;
  runtimeExportReviewSummaryError?: string | null;
  runtimeExportManifestLoading?: boolean;
  runtimeExportManifestError?: string | null;
  runtimeExportDiagnosticsBundleLoading?: boolean;
  runtimeExportDiagnosticsBundleError?: string | null;
  runtimeExportServiceLifecycleTraceLoading?: boolean;
  runtimeExportServiceLifecycleTraceError?: string | null;
  runtimeExportUserServiceRequestPageLoading?: boolean;
  runtimeExportUserServiceRequestPageError?: string | null;
  runtimeExportRouteDetailIndexLoading?: boolean;
  runtimeExportRouteDetailIndexError?: string | null;
  runtimeExportRouteDetailItemLoading?: boolean;
  runtimeExportRouteDetailItemError?: string | null;
  runtimeExportRouteComparisonReviewReportLoading?: boolean;
  runtimeExportRouteComparisonReviewReportError?: string | null;
  runtimeExportPackageAuditIndexLoading?: boolean;
  runtimeExportPackageAuditIndexError?: string | null;
  runtimeExportScenarioReviewBundleLoading?: boolean;
  runtimeExportScenarioReviewBundleError?: string | null;
  runtimeExportScenarioReviewChecklistLoading?: boolean;
  runtimeExportScenarioReviewChecklistError?: string | null;
  runtimeExportRouteComparisonReviewSavePendingRouteId?: string | null;
  runtimeExportRouteComparisonReviewSaveError?: string | null;
  runtimeExportRouteComparisonReviewSaveReportHash?: string | null;
  runtimeExportScenarioReviewChecklistSavePending?: boolean;
  runtimeExportScenarioReviewChecklistSaveError?: string | null;
  runtimeExportScenarioReviewChecklistSaveHash?: string | null;
  runtimeExportRestorePreflight?: RuntimeExportRestorePreflightV1 | null;
  runtimeExportRestorePreflightLoading?: boolean;
  runtimeExportRestorePreflightError?: string | null;
  runtimeExportRestoreCommandPendingPackageId?: string | null;
  runtimeExportRestoreCommandError?: string | null;
  runtimeExportRestoreResult?: RuntimeExportRestoreCommandResultV1 | null;
  userConfigurationSchema?: UserConfigurationSchemaV2 | null;
  userConfigurationTemplates?: UserConfigurationTemplateCatalogV1 | null;
  userConfigurationReference?: UserConfigurationReferenceV1 | null;
  userConfigurationExport?: UserConfigurationExportV1 | null;
  userConfigurationContractLoading?: boolean;
  userConfigurationContractError?: string | null;
  onUserConfigurationValidate?: (
    candidate: unknown
  ) => Promise<UserConfigurationValidationReportV1>;
  onUserConfigurationValidateText?: (
    text: string,
    format: "auto" | "json" | "yaml"
  ) => Promise<UserConfigurationValidationReportV1>;
  onUserConfigurationApply?: (
    normalizedConfig: Record<string, unknown>,
    command: UserConfigurationValidationApplyCommandV1
  ) => void;
  onRuntimeExportCompareSelect?: (packageId: string) => void;
  onRuntimeExportRouteDetailPageQueryChange?: (
    request: DataPanelExportRouteDetailPageRequest
  ) => void;
  onRuntimeExportServiceTracePageQueryChange?: (
    request: DataPanelExportServiceTracePageRequest
  ) => void;
  onRuntimeExportUserServiceRequestPageQueryChange?: (
    request: DataPanelExportUserServiceRequestPageRequest
  ) => void;
  onRuntimeExportRouteDetailItemSelect?: (routeId: string | null) => void;
  onRuntimeExportRouteComparisonReviewSave?: (
    request: DataPanelExportRouteComparisonReviewSaveRequest
  ) => void;
  onRuntimeExportScenarioReviewChecklistSave?: (
    request: DataPanelExportScenarioReviewChecklistSaveRequest
  ) => void;
  onRuntimeExportRestore?: (packageId: string) => void;
  onRuntimeUserDetailSelect?: (userId: string | null) => void;
  onRuntimeSatelliteDetailSelect?: (satelliteId: string | null) => void;
  onRuntimeRouteDetailSelect?: (routeId: string | null) => void;
  onRuntimeServiceDetailSelect?: (serviceId: string | null) => void;
  onRuntimeServiceTraceDetailSelect?: (traceId: string | null) => void;
  onRuntimeComputeNodeDetailSelect?: (nodeId: string | null) => void;
  displaySimTime: number;
  displayEventCount: number;
  onNavigateControl: (event: MouseEvent<HTMLAnchorElement>) => void;
}) {
  const [computeSeriesKey, setComputeSeriesKey] =
    useState<DataPanelComputeSeriesKey>("computeUsedTflops");
  const [detailFilter, setDetailFilter] = useState("");
  const [routeExplanationFilter, setRouteExplanationFilter] = useState("");
  const [exportRouteDetailIndexFilter, setExportRouteDetailIndexFilter] =
    useState("");
  const [
    exportRouteDetailIndexAvailabilityFilter,
    setExportRouteDetailIndexAvailabilityFilter
  ] = useState<DataPanelRouteExplanationAvailabilityFilter>("ALL");
  const [exportRouteDetailIndexBusinessFilter, setExportRouteDetailIndexBusinessFilter] =
    useState("ALL");
  const [
    exportRouteDetailIndexBottleneckFilter,
    setExportRouteDetailIndexBottleneckFilter
  ] = useState("ALL");
  const [
    exportRouteReviewReportFilter,
    setExportRouteReviewReportFilter
  ] = useState("");
  const [
    exportRouteReviewReportStatusFilter,
    setExportRouteReviewReportStatusFilter
  ] = useState<DataPanelRouteComparisonReviewReportStatusFilter>("ALL");
  const [exportRouteReviewReportPage, setExportRouteReviewReportPage] = useState(0);
  const [
    exportScenarioReviewChecklistDraft,
    setExportScenarioReviewChecklistDraft
  ] = useState<DataPanelScenarioReviewChecklistDraft>({});
  const [exportServiceTraceFilter, setExportServiceTraceFilter] = useState("");
  const [exportUserServiceRequestFilter, setExportUserServiceRequestFilter] =
    useState("");
  const [
    exportUserServiceRequestClassFilter,
    setExportUserServiceRequestClassFilter
  ] = useState("ALL");
  const [
    exportUserServiceRequestTerminalFilter,
    setExportUserServiceRequestTerminalFilter
  ] = useState("ALL");
  const [
    exportUserServiceRequestWaitingFilter,
    setExportUserServiceRequestWaitingFilter
  ] = useState("ALL");
  const [exportServiceTraceTerminalFilter, setExportServiceTraceTerminalFilter] =
    useState<DataPanelServiceTraceTerminalFilter>("ALL");
  const [exportServiceTraceComputeNodeFilter, setExportServiceTraceComputeNodeFilter] =
    useState("");
  const [exportServiceTraceStageFilter, setExportServiceTraceStageFilter] =
    useState<DataPanelServiceTraceStageFilter>("ALL");
  const [
    exportServiceTraceTerminalReasonFilter,
    setExportServiceTraceTerminalReasonFilter
  ] = useState<DataPanelServiceTraceTerminalReasonFilter>("ALL");
  const [exportServiceTracePageCursor, setExportServiceTracePageCursor] = useState(0);
  const [routeExplanationAvailabilityFilter, setRouteExplanationAvailabilityFilter] =
    useState<DataPanelRouteExplanationAvailabilityFilter>("ALL");
  const [routeExplanationBusinessFilter, setRouteExplanationBusinessFilter] =
    useState("ALL");
  const [routeExplanationBottleneckFilter, setRouteExplanationBottleneckFilter] =
    useState("ALL");
  const [serviceDetailFilter, setServiceDetailFilter] = useState("");
  const [serviceTraceFilter, setServiceTraceFilter] = useState("");
  const [serviceTraceTerminalFilter, setServiceTraceTerminalFilter] =
    useState<DataPanelServiceTraceTerminalFilter>("ALL");
  const [serviceTraceComputeNodeFilter, setServiceTraceComputeNodeFilter] =
    useState("");
  const [serviceTraceStageFilter, setServiceTraceStageFilter] =
    useState<DataPanelServiceTraceStageFilter>("ALL");
  const [serviceTraceTerminalReasonFilter, setServiceTraceTerminalReasonFilter] =
    useState<DataPanelServiceTraceTerminalReasonFilter>("ALL");
  const [computeNodeDetailFilter, setComputeNodeDetailFilter] = useState("");
  const [userDetailPage, setUserDetailPage] = useState(0);
  const [satelliteDetailPage, setSatelliteDetailPage] = useState(0);
  const [selectedHistorySatelliteId, setSelectedHistorySatelliteId] = useState<string | null>(
    null
  );
  const [selectedHistoryUserId, setSelectedHistoryUserId] = useState<string | null>(null);
  const [selectedDetailUserId, setSelectedDetailUserId] = useState<string | null>(null);
  const [selectedDetailSatelliteId, setSelectedDetailSatelliteId] = useState<string | null>(
    null
  );
  const [selectedRouteDetailId, setSelectedRouteDetailId] = useState<string | null>(null);
  const [selectedServiceDetailId, setSelectedServiceDetailId] = useState<string | null>(
    null
  );
  const [selectedServiceTraceId, setSelectedServiceTraceId] = useState<string | null>(
    null
  );
  const [selectedComputeNodeDetailId, setSelectedComputeNodeDetailId] = useState<
    string | null
  >(null);
  const [restoreConfirmPackageId, setRestoreConfirmPackageId] = useState<string | null>(
    null
  );
  const [userConfigurationValidateText, setUserConfigurationValidateText] = useState(
    DEFAULT_USER_CONFIGURATION_VALIDATE_TEXT
  );
  const [userConfigurationPreflightMode, setUserConfigurationPreflightMode] =
    useState<UserConfigurationPreflightMode>("json_mapping");
  const [userConfigurationValidateReport, setUserConfigurationValidateReport] =
    useState<UserConfigurationValidationReportV1 | null>(null);
  const [userConfigurationValidatePending, setUserConfigurationValidatePending] =
    useState(false);
  const [userConfigurationValidateError, setUserConfigurationValidateError] =
    useState<string | null>(null);
  const [userConfigurationApplyStatus, setUserConfigurationApplyStatus] =
    useState<string | null>(null);
  useEffect(() => {
    setExportRouteDetailIndexFilter("");
    setExportRouteDetailIndexAvailabilityFilter("ALL");
    setExportRouteDetailIndexBusinessFilter("ALL");
    setExportRouteDetailIndexBottleneckFilter("ALL");
    setExportRouteReviewReportFilter("");
    setExportRouteReviewReportStatusFilter("ALL");
    setExportRouteReviewReportPage(0);
    setExportScenarioReviewChecklistDraft({});
    setExportServiceTraceFilter("");
    setExportUserServiceRequestFilter("");
    setExportUserServiceRequestClassFilter("ALL");
    setExportUserServiceRequestTerminalFilter("ALL");
    setExportUserServiceRequestWaitingFilter("ALL");
    setExportServiceTraceTerminalFilter("ALL");
    setExportServiceTraceComputeNodeFilter("");
    setExportServiceTraceStageFilter("ALL");
    setExportServiceTraceTerminalReasonFilter("ALL");
    setExportServiceTracePageCursor(0);
  }, [runtimeExportComparePackageId]);
  useEffect(() => {
    setExportRouteReviewReportPage(0);
  }, [
    exportRouteReviewReportFilter,
    exportRouteReviewReportStatusFilter,
    runtimeExportRouteComparisonReviewReport?.report_hash
  ]);
  useEffect(() => {
    setExportScenarioReviewChecklistDraft(
      buildDataPanelScenarioReviewChecklistDraft(
        runtimeExportScenarioReviewBundle,
        runtimeExportScenarioReviewChecklist
      )
    );
  }, [
    runtimeExportScenarioReviewBundle?.scenario_review_hash,
    runtimeExportScenarioReviewChecklist?.checklist_hash
  ]);
  useEffect(() => {
    setExportServiceTracePageCursor(0);
  }, [
    exportServiceTraceFilter,
    exportServiceTraceTerminalFilter,
    exportServiceTraceComputeNodeFilter,
    exportServiceTraceStageFilter,
    exportServiceTraceTerminalReasonFilter,
    runtimeExportServiceLifecycleTrace?.source_summary,
    runtimeExportServiceLifecycleTrace?.trace_count,
    runtimeExportServiceLifecycleTrace?.cursor,
    runtimeExportServiceLifecycleTrace?.next_cursor,
    runtimeExportServiceTracePage?.page_hash
  ]);
  const summary = buildDataPanelDisplaySummary(
    buildDataPanelSummary(snapshot),
    displaySimTime,
    displayEventCount
  );
  const fidelitySummary =
    runtimeStatus.fidelity_summary ??
    generatedConfig?.backend_summary?.fidelity_summary ??
    snapshot.fidelity_summary ??
    null;
  const configuredScale = buildDataPanelConfiguredScale(generatedConfig, fidelitySummary);
  const trafficSummary = generatedConfig?.backend_summary?.traffic_demand_summary;
  const trafficDisplay = buildDataPanelTrafficDisplay(trafficSummary);
  const reproducibilityDisplay = buildDataPanelReproducibilityDisplay(
    runtimeStatus.reproducibility_manifest_v1
  );
  const exportHistoryDisplay = buildDataPanelExportHistoryDisplay(
    runtimeStatus.runtime_export_history_v1
  );
  const userConfigurationContractDisplay = buildDataPanelUserConfigurationContractDisplay(
    userConfigurationSchema,
    userConfigurationTemplates,
    userConfigurationReference,
    userConfigurationExport,
    userConfigurationContractLoading,
    userConfigurationContractError
  );
  const userConfigurationValidationDisplay =
    buildDataPanelUserConfigurationValidationDisplay(
      userConfigurationValidateReport,
      userConfigurationValidatePending,
      userConfigurationValidateError,
      userConfigurationApplyStatus
    );
  const configurationExplanationDisplay = buildDataPanelConfigurationExplanationDisplay(
    generatedConfig?.backend_summary?.configuration_explanation_v2
  );
  const informationArchitectureDisplay =
    buildDataPanelInformationArchitectureDisplay(
      generatedConfig?.backend_summary?.dashboard_information_architecture_v3
    );
  const detailPaginationContract =
    generatedConfig?.backend_summary?.large_detail_pagination_contract_v2;
  const detailPageSizes = buildDataPanelDetailPageSizes(detailPaginationContract);
  const exportCatalogDisplay = buildDataPanelExportCatalogDisplay(runtimeExportCatalog);
  const exportReviewSummaryDisplay = buildDataPanelExportReviewSummaryDisplay(
    runtimeExportReviewSummary
  );
  const exportReviewSummaryStatus = buildDataPanelExportReviewSummaryStatus(
    exportReviewSummaryDisplay,
    runtimeExportComparePackageId,
    runtimeExportReviewSummaryLoading,
    runtimeExportReviewSummaryError
  );
  const exportArtifactHealthDisplay = buildDataPanelExportArtifactHealthDisplay(
    runtimeExportCatalog,
    runtimeExportComparePackageId,
    runtimeExportReviewSummary
  );
  const exportDiagnosticsDisplay = buildDataPanelExportDiagnosticsDisplay(
    runtimeExportDiagnosticsBundle
  );
  const exportDiagnosticsStatus = buildDataPanelExportDiagnosticsStatus(
    exportDiagnosticsDisplay,
    runtimeExportComparePackageId,
    runtimeExportDiagnosticsBundleLoading,
    runtimeExportDiagnosticsBundleError
  );
  const exportServiceTraceForDisplay =
    runtimeExportServiceTracePage === null ||
    runtimeExportServiceTracePage === undefined
      ? runtimeExportServiceLifecycleTrace
      : runtimeExportServiceTracePageToLifecycleTrace(runtimeExportServiceTracePage);
  const exportServiceLifecycleTraceStatus =
    buildDataPanelExportServiceLifecycleTraceStatus(
      exportServiceTraceForDisplay
        ? buildDataPanelServiceLifecycleTraceDisplay(
            exportServiceTraceForDisplay,
            exportServiceTraceForDisplay.items.length
          )
        : null,
      exportServiceTraceForDisplay,
      runtimeExportComparePackageId,
      runtimeExportServiceLifecycleTraceLoading,
      runtimeExportServiceLifecycleTraceError,
      {
        query:
          runtimeExportServiceTracePage === null ||
          runtimeExportServiceTracePage === undefined
            ? exportServiceTraceFilter
            : "",
        terminalState:
          runtimeExportServiceTracePage === null ||
          runtimeExportServiceTracePage === undefined
            ? exportServiceTraceTerminalFilter
            : "ALL",
        computeNodeId:
          runtimeExportServiceTracePage === null ||
          runtimeExportServiceTracePage === undefined
            ? exportServiceTraceComputeNodeFilter
            : "",
        stageKind:
          runtimeExportServiceTracePage === null ||
          runtimeExportServiceTracePage === undefined
            ? exportServiceTraceStageFilter
            : "ALL",
        terminalReason:
          runtimeExportServiceTracePage === null ||
          runtimeExportServiceTracePage === undefined
            ? exportServiceTraceTerminalReasonFilter
            : "ALL",
        cursor:
          runtimeExportServiceTracePage === null ||
          runtimeExportServiceTracePage === undefined
            ? exportServiceTracePageCursor
            : runtimeExportServiceTracePage.cursor,
        limit:
          runtimeExportServiceTracePage === null ||
          runtimeExportServiceTracePage === undefined
            ? 5
            : runtimeExportServiceTracePage.limit,
        backendPage: runtimeExportServiceTracePage ?? undefined
      }
    );
  const exportUserServiceRequestStatus =
    buildDataPanelExportUserServiceRequestStatus(
      runtimeExportUserServiceRequestPage,
      runtimeExportComparePackageId,
      runtimeExportUserServiceRequestPageLoading,
      runtimeExportUserServiceRequestPageError,
      {
        query: exportUserServiceRequestFilter,
        serviceClass: exportUserServiceRequestClassFilter,
        terminalState: exportUserServiceRequestTerminalFilter,
        networkWaiting: exportUserServiceRequestWaitingFilter
      }
    );
  const exportRouteDetailIndexDisplay =
    buildDataPanelExportRouteDetailPageDisplay(runtimeExportRouteDetailPage) ??
    buildDataPanelExportRouteDetailIndexDisplay(runtimeExportRouteDetailIndex, {
      query: exportRouteDetailIndexFilter
    });
  const exportRouteDetailIndexStatus = buildDataPanelExportRouteDetailIndexStatus(
    exportRouteDetailIndexDisplay,
    runtimeExportComparePackageId,
    runtimeExportRouteDetailIndexLoading,
    runtimeExportRouteDetailIndexError
  );
  const exportRouteDetailItemStatus = buildDataPanelExportRouteDetailItemStatus(
    buildDataPanelExportRouteDetailItemDisplay(runtimeExportRouteDetailItem),
    runtimeExportComparePackageId,
    runtimeExportRouteDetailItemRouteId,
    runtimeExportRouteDetailItemLoading,
    runtimeExportRouteDetailItemError
  );
  const requestRuntimeExportRouteDetailPage = (
    cursor: number,
    filterOverrides: DataPanelRouteExplanationFilter = {}
  ) => {
    onRuntimeExportRouteDetailPageQueryChange?.({
      cursor,
      limit: exportRouteDetailIndexStatus?.pageLimit ?? 5,
      filters: {
        query: filterOverrides.query ?? exportRouteDetailIndexFilter,
        availability:
          filterOverrides.availability ?? exportRouteDetailIndexAvailabilityFilter,
        businessType:
          filterOverrides.businessType ?? exportRouteDetailIndexBusinessFilter,
        bottleneckComponent:
          filterOverrides.bottleneckComponent ??
          exportRouteDetailIndexBottleneckFilter
      }
    });
  };
  const requestRuntimeExportServiceTracePage = (
    cursor: number,
    filterOverrides: DataPanelServiceTraceFilter = {}
  ) => {
    if (onRuntimeExportServiceTracePageQueryChange) {
      onRuntimeExportServiceTracePageQueryChange({
        cursor,
        limit: exportServiceLifecycleTraceStatus?.pageLimit ?? 5,
        filters: {
          query: filterOverrides.query ?? exportServiceTraceFilter,
          terminalState:
            filterOverrides.terminalState ?? exportServiceTraceTerminalFilter,
          computeNodeId:
            filterOverrides.computeNodeId ?? exportServiceTraceComputeNodeFilter,
          stageKind: filterOverrides.stageKind ?? exportServiceTraceStageFilter,
          terminalReason:
            filterOverrides.terminalReason ??
            exportServiceTraceTerminalReasonFilter
        }
      });
      return;
    }
    setExportServiceTracePageCursor(cursor);
  };
  const requestRuntimeExportUserServiceRequestPage = (
    cursor: number,
    filterOverrides: DataPanelUserServiceRequestFilter = {}
  ) => {
    onRuntimeExportUserServiceRequestPageQueryChange?.({
      cursor,
      limit: exportUserServiceRequestStatus?.pageLimit ?? 5,
      filters: {
        query: filterOverrides.query ?? exportUserServiceRequestFilter,
        serviceClass:
          filterOverrides.serviceClass ?? exportUserServiceRequestClassFilter,
        terminalState:
          filterOverrides.terminalState ?? exportUserServiceRequestTerminalFilter,
        networkWaiting:
          filterOverrides.networkWaiting ?? exportUserServiceRequestWaitingFilter
      }
    });
  };
  const openRuntimeExportUserServiceRequestEvidence = (
    row: UserBusinessRequestRow
  ) => {
    const userId = linkedReviewId(row.userId);
    if (userId) {
      setSelectedDetailUserId(userId);
      onRuntimeUserDetailSelect?.(userId);
    }
    const satelliteId = linkedReviewId(row.selectedSatelliteId);
    if (satelliteId && satelliteId.startsWith("sat-")) {
      setSelectedDetailSatelliteId(satelliteId);
      onRuntimeSatelliteDetailSelect?.(satelliteId);
    }
    const computeNodeId = linkedReviewId(row.computeNodeId);
    if (computeNodeId) {
      setSelectedComputeNodeDetailId(computeNodeId);
      onRuntimeComputeNodeDetailSelect?.(computeNodeId);
      if (computeNodeId.startsWith("sat-")) {
        setSelectedDetailSatelliteId(computeNodeId);
        onRuntimeSatelliteDetailSelect?.(computeNodeId);
      }
    }
    const routeId = linkedReviewId(row.routeId);
    if (routeId) {
      setSelectedRouteDetailId(routeId);
      setExportRouteDetailIndexFilter(routeId);
      setExportRouteDetailIndexAvailabilityFilter("ALL");
      setExportRouteDetailIndexBusinessFilter("ALL");
      setExportRouteDetailIndexBottleneckFilter("ALL");
      onRuntimeExportRouteDetailItemSelect?.(routeId);
      onRuntimeRouteDetailSelect?.(routeId);
      requestRuntimeExportRouteDetailPage(0, {
        query: routeId,
        availability: "ALL",
        businessType: "ALL",
        bottleneckComponent: "ALL"
      });
    }
    const serviceQuery = userBusinessRequestServiceTraceQuery(row);
    if (serviceQuery) {
      setExportServiceTraceFilter(serviceQuery);
      setExportServiceTraceTerminalFilter("ALL");
      setExportServiceTraceComputeNodeFilter("");
      setExportServiceTraceStageFilter("ALL");
      setExportServiceTraceTerminalReasonFilter("ALL");
      requestRuntimeExportServiceTracePage(0, {
        query: serviceQuery,
        terminalState: "ALL",
        computeNodeId: "",
        stageKind: "ALL",
        terminalReason: "ALL"
      });
    }
  };
  const exportManifestInspectorDisplay = buildDataPanelExportManifestInspectorDisplay(
    runtimeExportManifest,
    runtimeExportComparePackageId,
    runtimeExportCatalog,
    runtimeExportDiagnosticsBundle
  );
  const exportManifestInspectorStatus = buildDataPanelExportManifestInspectorStatus(
    exportManifestInspectorDisplay,
    runtimeExportComparePackageId,
    runtimeExportManifestLoading,
    runtimeExportManifestError
  );
  const exportReproducibilityBoundaryDisplay =
    buildDataPanelExportReproducibilityBoundaryDisplay(
      runtimeExportManifest,
      runtimeExportReviewSummary,
      runtimeExportDiagnosticsBundle,
      runtimeExportComparePackageId
    );
  const exportCompareDisplay = buildDataPanelExportCompareDisplay(runtimeExportCompare);
  const exportCompareStatus = buildDataPanelExportCompareStatus(
    exportCompareDisplay,
    runtimeExportComparePackageId,
    runtimeExportCompareLoading,
    runtimeExportCompareError
  );
  const exportRestorePreflightDisplay = buildDataPanelExportRestorePreflightDisplay(
    runtimeExportRestorePreflight
  );
  const exportRestorePreflightStatus = buildDataPanelExportRestorePreflightStatus(
    exportRestorePreflightDisplay,
    runtimeExportComparePackageId,
    runtimeExportRestorePreflightLoading,
    runtimeExportRestorePreflightError
  );
  const exportBoundaryAlignmentDisplay =
    buildDataPanelExportBoundaryAlignmentDisplay(
      runtimeExportManifest,
      runtimeExportReviewSummary,
      runtimeExportDiagnosticsBundle,
      runtimeExportCompare,
      runtimeExportRestorePreflight,
      runtimeExportComparePackageId
    );
  const exportRestoreActionDisplay = buildDataPanelExportRestoreActionDisplay(
    exportRestorePreflightStatus,
    {
      selectedPackageId: runtimeExportComparePackageId,
      armedPackageId: restoreConfirmPackageId,
      pendingPackageId: runtimeExportRestoreCommandPendingPackageId,
      commandError: runtimeExportRestoreCommandError,
      result: runtimeExportRestoreResult
    }
  );
  const runtimeProgress = buildDataPanelRuntimeProgress(summary.simTime, runtimeStatus.duration);
  const telemetry = buildDataPanelTelemetry(
    snapshot,
    summary.simTime,
    runtimeStatus.metrics_summary,
    runtimeStatus.kpi_time_series_v1
  );
  const computeVectorTail = buildDataPanelComputeVectorTail(
    runtimeStatus.kpi_time_series_v1
  );
  const computeBottleneck = buildDataPanelComputeBottleneckDisplay(
    runtimeStatus.metrics_summary
  );
  const networkKpiSource = buildDataPanelNetworkKpiSource(
    snapshot,
    runtimeStatus.metrics_summary,
    runtimeStatus.kpi_time_series_v1,
    runtimeStatus.network_quality_provenance_v1
  );
  const networkKpiProvenanceItems = buildDataPanelNetworkKpiProvenanceItems(
    runtimeStatus.metrics_summary,
    runtimeStatus.kpi_time_series_v1,
    runtimeStatus.network_quality_provenance_v1
  );
  const networkKpiCredibilityDisplay = buildDataPanelNetworkKpiCredibilityDisplay(
    runtimeStatus.network_kpi_credibility_v1
  );
  const networkKpiBenchmarkValidationDisplay =
    buildDataPanelNetworkKpiBenchmarkValidationDisplay(
      runtimeStatus.network_kpi_benchmark_validation_v1
    );
  const networkKpiFormulaInspector = buildDataPanelNetworkKpiFormulaInspector(
    runtimeStatus.network_kpi_provenance_v2,
    runtimeStatus.network_kpi_credibility_v1
  );
  const modelAssumptionsDisplay = buildDataPanelModelAssumptionsDisplay(
    generatedConfig?.backend_summary?.model_assumptions,
    fidelitySummary,
    networkKpiCredibilityDisplay,
    configurationExplanationDisplay
  );
  const routeProvenanceTrustDisplay = buildDataPanelRouteProvenanceTrustDisplay(
    runtimeStatus.route_provenance_trust_summary_v1
  );
  const modelTrustEvidenceWorkspace = buildDataPanelModelTrustEvidenceWorkspace({
    configurationExplanation: configurationExplanationDisplay,
    modelAssumptions: modelAssumptionsDisplay,
    networkKpiCredibility: networkKpiCredibilityDisplay,
    networkKpiBenchmarkValidation: networkKpiBenchmarkValidationDisplay,
    networkKpiFormulaInspector,
    routeProvenanceTrust: routeProvenanceTrustDisplay,
    fidelitySummary,
    reproducibilityManifest: runtimeStatus.reproducibility_manifest_v1,
    exportCatalog: runtimeExportCatalog,
    exportReviewSummary: runtimeExportReviewSummary,
    exportDiagnosticsBundle: runtimeExportDiagnosticsBundle,
    runtimeStatus
  });
  const networkFormulaInputs = buildDataPanelNetworkFormulaInputs(
    runtimeStatus.metrics_summary
  );
  const networkComponentTail = buildDataPanelNetworkComponentTail(
    runtimeStatus.kpi_time_series_v1
  );
  const serviceLatency = buildDataPanelServiceLatencyDisplay(
    runtimeStatus.metrics_summary
  );
  const serviceLatencyRows = buildDataPanelServiceLatencyRows(
    runtimeStatus.service_latency_history_v1
  );
  const serviceLifecycleTraceDisplay = buildDataPanelServiceLifecycleTraceDisplay(
    selectRuntimeServiceTracePage(runtimeStatus, runtimeDetailPages)
  );
  const serviceTracePage = selectRuntimeServiceTracePage(
    runtimeStatus,
    runtimeDetailPages
  );
  const serviceTraceCursorFilters = serviceTraceDetailCursorFilters(
    serviceTraceFilter,
    serviceTraceTerminalFilter,
    serviceTraceComputeNodeFilter,
    serviceTraceStageFilter,
    serviceTraceTerminalReasonFilter
  );
  const filteredServiceLifecycleTraceDisplay = filterServiceLifecycleTraceDisplay(
    serviceLifecycleTraceDisplay,
    serviceTraceCursorFilters
  );
  const selectedServiceTraceRow = selectServiceLifecycleTraceRow(
    filteredServiceLifecycleTraceDisplay.items,
    selectedServiceTraceId
  );
  const serviceDetailPage = selectRuntimeServiceDetailPage(runtimeDetailPages);
  const serviceDetailRows = buildDataPanelServiceDetailRows(
    serviceDetailPage,
    detailPageSizes.services
  );
  const selectedServiceDetailRow = selectServiceDetailRow(
    serviceDetailRows.items,
    selectedServiceDetailId
  );
  const computeTaskTimeline = buildDataPanelComputeTaskTimelineDisplay(
    runtimeStatus.compute_task_timeline_summary_v1
  );
  const computeNodeDetailPage = selectRuntimeComputeNodeDetailPage(runtimeDetailPages);
  const computeNodeDetailRows = buildDataPanelComputeNodeDetailRows(
    computeNodeDetailPage,
    detailPageSizes.computeNodes
  );
  const selectedComputeNodeDetailRow = selectComputeNodeDetailRow(
    computeNodeDetailRows.items,
    selectedComputeNodeDetailId
  );
  const routeConstraints = buildDataPanelRouteConstraints(
    snapshot,
    runtimeStatus.metrics_summary
  );
  const routeExplanationSummary = selectRuntimeRouteExplanationSummary(
    runtimeStatus,
    runtimeDetailPages
  );
  const routeExplanations = buildDataPanelRouteExplanationRows(routeExplanationSummary);
  const filteredRouteExplanations = filterRouteExplanationRows(
    routeExplanations,
    {
      query: routeExplanationFilter,
      availability: routeExplanationAvailabilityFilter,
      businessType: routeExplanationBusinessFilter,
      bottleneckComponent: routeExplanationBottleneckFilter
    }
  );
  const selectedRouteDetailRow = selectRouteExplanationRow(
    filteredRouteExplanations.items,
    selectedRouteDetailId
  );
  const latestTelemetry = telemetry[telemetry.length - 1];
  const computeSeries = computeSeriesOption(computeSeriesKey);
  const latestComputeValue = latestTelemetry[computeSeriesKey];
  const computePool = buildComputeResourcePoolFromRuntime(
    snapshot,
    runtimeStatus.metrics_summary,
    runtimeStatus.kpi_time_series_v1
  );
  const computePoolModeNote = buildComputeResourcePoolModeNote(computePool);
  const topComputeNodes = buildTopComputeNodeRows(
    snapshot,
    runtimeStatus.satellite_kpi_slices_v1
  );
  const userRequestSummary = selectRuntimeUserRequestSummary(
    runtimeStatus,
    runtimeDetailPages
  );
  const satelliteServiceSummary = selectRuntimeSatelliteServiceSummary(
    runtimeStatus,
    runtimeDetailPages
  );
  const userBusinessRequests = buildUserBusinessRequestRows(
    snapshot,
    runtimeStatus.service_latency_history_v1,
    userRequestSummary
  );
  const userRequestHistory = buildDataPanelUserRequestHistory(
    runtimeStatus.user_request_history_v1,
    selectedHistoryUserId
  );
  const latestUserRequestHistoryPoint =
    userRequestHistory.points[userRequestHistory.points.length - 1];
  const satelliteResourceRows = buildSatelliteResourceRows(
    snapshot,
    runtimeStatus.satellite_kpi_slices_v1,
    satelliteServiceSummary
  );
  const userDetailWindowNote = buildRuntimeDetailWindowNote(
    userRequestSummary,
    "users"
  );
  const satelliteDetailWindowNote = buildRuntimeDetailWindowNote(
    satelliteServiceSummary,
    "satellites"
  );
  const satelliteResourceHistory = buildDataPanelSatelliteResourceHistory(
    runtimeStatus.satellite_kpi_history_v1,
    selectedHistorySatelliteId
  );
  const latestSatelliteResourceHistoryPoint =
    satelliteResourceHistory.points[satelliteResourceHistory.points.length - 1];
  const filteredUserBusinessRequests = filterUserBusinessRequestRows(
    userBusinessRequests,
    detailFilter
  );
  const filteredSatelliteResourceRows = filterSatelliteResourceRows(
    satelliteResourceRows,
    detailFilter
  );
  const userDetailWindow = paginateDetailRows(
    filteredUserBusinessRequests.items,
    userDetailPage,
    detailPageSizes.users
  );
  const satelliteDetailWindow = paginateDetailRows(
    filteredSatelliteResourceRows.items,
    satelliteDetailPage,
    detailPageSizes.satellites
  );
  const selectedUserDetailRow = selectUserBusinessRequestRow(
    userDetailWindow.items,
    selectedDetailUserId
  );
  const selectedSatelliteDetailRow = selectSatelliteResourceRow(
    satelliteDetailWindow.items,
    selectedDetailSatelliteId
  );
  const nodeDetailSummary = selectRuntimeNodeDetailSummary(
    runtimeStatus,
    runtimeDetailPages
  );
  const selectedUserBackendDetail =
    runtimeSelectedNodeDetails?.user?.entity_id === selectedDetailUserId
      ? runtimeSelectedNodeDetails.user
      : null;
  const selectedSatelliteBackendDetail =
    runtimeSelectedNodeDetails?.satellite?.entity_id === selectedDetailSatelliteId
      ? runtimeSelectedNodeDetails.satellite
      : null;
  const selectedRouteBackendDetail =
    runtimeSelectedNodeDetails?.route?.route_id === selectedRouteDetailId
      ? runtimeSelectedNodeDetails.route
      : null;
  const selectedServiceBackendDetail =
    runtimeSelectedNodeDetails?.service?.service_id === selectedServiceDetailId
      ? runtimeSelectedNodeDetails.service
      : null;
  const selectedServiceTraceBackendDetail =
    selectedServiceTraceRow !== null &&
    serviceTraceDetailMatchesRow(
      runtimeSelectedNodeDetails?.serviceTrace,
      selectedServiceTraceRow
    )
      ? runtimeSelectedNodeDetails?.serviceTrace ?? null
      : null;
  const selectedComputeNodeBackendDetail =
    runtimeSelectedNodeDetails?.computeNode?.node_id === selectedComputeNodeDetailId
      ? runtimeSelectedNodeDetails.computeNode
      : null;
  const serviceTraceCorrelationInspector = buildServiceTraceCorrelationInspector(
    selectedServiceTraceRow,
    userBusinessRequests,
    routeExplanations,
    satelliteResourceRows,
    computeNodeDetailRows,
    selectedServiceTraceBackendDetail
  );
  const userDetailRequestStatus = selectExactDetailRequestStatus(
    runtimeSelectedNodeDetailRequests?.user,
    selectedDetailUserId
  );
  const satelliteDetailRequestStatus = selectExactDetailRequestStatus(
    runtimeSelectedNodeDetailRequests?.satellite,
    selectedDetailSatelliteId
  );
  const routeDetailRequestStatus = selectExactDetailRequestStatus(
    runtimeSelectedNodeDetailRequests?.route,
    selectedRouteDetailId
  );
  const serviceDetailRequestStatus = selectExactDetailRequestStatus(
    runtimeSelectedNodeDetailRequests?.service,
    selectedServiceDetailId
  );
  const serviceTraceDetailRequestStatus = selectExactDetailRequestStatus(
    runtimeSelectedNodeDetailRequests?.serviceTrace,
    selectedServiceTraceRow?.traceId ?? null
  );
  const computeNodeDetailRequestStatus = selectExactDetailRequestStatus(
    runtimeSelectedNodeDetailRequests?.computeNode,
    selectedComputeNodeDetailId
  );
  const userDetailInspector = buildUserBusinessRequestInspector(
    selectedUserDetailRow,
    nodeDetailSummary,
    selectedUserBackendDetail
  );
  const displayedUserDetailInspector = appendExactDetailStatusToInspector(
    userDetailInspector,
    userDetailRequestStatus
  );
  const satelliteDetailInspector = buildSatelliteResourceInspector(
    selectedSatelliteDetailRow,
    nodeDetailSummary,
    selectedSatelliteBackendDetail
  );
  const displayedSatelliteDetailInspector = appendExactDetailStatusToInspector(
    satelliteDetailInspector,
    satelliteDetailRequestStatus
  );
  const routeDetailInspector = buildRouteExplanationDetailInspector(
    selectedRouteDetailRow,
    selectedRouteBackendDetail
  );
  const displayedRouteDetailInspector = appendExactDetailStatusToInspector(
    routeDetailInspector,
    routeDetailRequestStatus
  );
  const exportRouteLiveComparison =
    buildDataPanelExportRouteLiveComparisonDisplay(
      runtimeExportRouteDetailItem,
      selectedRouteBackendDetail
    );
  const exportRouteLiveComparisonStatus =
    buildDataPanelExportRouteLiveComparisonStatus(
      exportRouteLiveComparison,
      runtimeExportRouteDetailItem,
      exportRouteDetailItemStatus,
      selectedRouteBackendDetail,
      routeDetailRequestStatus
    );
  const exportRouteComparisonReviewRecord =
    buildDataPanelExportRouteComparisonReviewRecord(
      runtimeExportRouteDetailItem,
      selectedRouteBackendDetail,
      exportRouteLiveComparison
    );
  const exportRouteComparisonReviewSaveStatus =
    buildDataPanelExportRouteComparisonReviewSaveStatus(
      exportRouteLiveComparison,
      runtimeExportRouteDetailItem,
      {
        pendingRouteId: runtimeExportRouteComparisonReviewSavePendingRouteId,
        error: runtimeExportRouteComparisonReviewSaveError,
        reportHash: runtimeExportRouteComparisonReviewSaveReportHash
      }
    );
  const exportRouteComparisonReviewArtifactDisplay =
    buildDataPanelExportRouteComparisonReviewArtifactDisplay(
      runtimeExportCatalog,
      runtimeExportComparePackageId,
      runtimeExportRouteComparisonReviewSaveReportHash
    );
  const exportPackageAuditIndexArtifactDisplay =
    buildDataPanelExportPackageAuditIndexArtifactDisplay(
      runtimeExportCatalog,
      runtimeExportComparePackageId,
      runtimeExportRouteComparisonReviewSaveReportHash
    );
  const exportPackageHandoffReportArtifactDisplay =
    buildDataPanelExportPackageHandoffReportArtifactDisplay(
      runtimeExportCatalog,
      runtimeExportComparePackageId,
      runtimeExportPackageAuditIndex?.package_review_completion_hash ??
        runtimeExportPackageAuditIndex?.package_review_completion_v1?.completion_hash ??
        runtimeExportScenarioReviewChecklistSaveHash ??
        null
    );
  const exportPackageAuditIndexStatus = buildDataPanelExportPackageAuditIndexStatus(
    buildDataPanelExportPackageAuditIndexDisplay(runtimeExportPackageAuditIndex),
    runtimeExportComparePackageId,
    runtimeExportPackageAuditIndexLoading,
    runtimeExportPackageAuditIndexError
  );
  const exportScenarioReviewBundleStatus =
    buildDataPanelExportScenarioReviewBundleStatus(
      buildDataPanelExportScenarioReviewBundleDisplay(
        runtimeExportScenarioReviewBundle
      ),
      runtimeExportComparePackageId,
      runtimeExportScenarioReviewBundleLoading,
      runtimeExportScenarioReviewBundleError
    );
  const exportScenarioReviewChecklistStatus =
    buildDataPanelExportScenarioReviewChecklistStatus(
      runtimeExportScenarioReviewChecklist,
      {
        loading: runtimeExportScenarioReviewChecklistLoading,
        error: runtimeExportScenarioReviewChecklistError,
        savePending: runtimeExportScenarioReviewChecklistSavePending,
        saveError: runtimeExportScenarioReviewChecklistSaveError,
        latestSaveHash: runtimeExportScenarioReviewChecklistSaveHash
      }
    );
  const exportScenarioReviewChecklistSaveRequest =
    buildDataPanelScenarioReviewChecklistSaveRequest(
      runtimeExportScenarioReviewBundle,
      exportScenarioReviewBundleStatus?.workflowRows ?? [],
      exportScenarioReviewChecklistDraft,
      runtimeExportPackageAuditIndex
    );
  const exportReviewCompletionSummary =
    buildDataPanelExportReviewCompletionSummary({
      auditIndex: runtimeExportPackageAuditIndex,
      routeReport: runtimeExportRouteComparisonReviewReport,
      scenarioReviewBundle: runtimeExportScenarioReviewBundle,
      scenarioReviewChecklist: runtimeExportScenarioReviewChecklist
    });
  const exportRouteComparisonReviewReportStatus =
    buildDataPanelExportRouteComparisonReviewReportStatus(
      buildDataPanelExportRouteComparisonReviewReportDisplay(
        runtimeExportRouteComparisonReviewReport,
        {
          cursor: exportRouteReviewReportPage,
          limit: 5,
          query: exportRouteReviewReportFilter,
          status: exportRouteReviewReportStatusFilter
        }
      ),
      runtimeExportComparePackageId,
      runtimeExportRouteComparisonReviewReportLoading,
      runtimeExportRouteComparisonReviewReportError
    );
  const serviceDetailInspector = buildServiceLifecycleDetailInspector(
    selectedServiceDetailRow,
    selectedServiceBackendDetail
  );
  const displayedServiceDetailInspector = appendExactDetailStatusToInspector(
    serviceDetailInspector,
    serviceDetailRequestStatus
  );
  const displayedServiceTraceCorrelationInspector =
    appendExactDetailStatusToInspector(
      serviceTraceCorrelationInspector,
      serviceTraceDetailRequestStatus
    );
  const computeNodeDetailInspector = buildComputeNodeExactDetailInspector(
    selectedComputeNodeDetailRow,
    selectedComputeNodeBackendDetail
  );
  const displayedComputeNodeDetailInspector = appendExactDetailStatusToInspector(
    computeNodeDetailInspector,
    computeNodeDetailRequestStatus
  );
  const nodeDetailDrawerItems = buildDataPanelNodeDetailDrawerItems(
    displayedUserDetailInspector,
    displayedSatelliteDetailInspector,
    buildServiceTraceDetailDrawerItem(
      selectedServiceTraceBackendDetail,
      displayedServiceTraceCorrelationInspector
    )
  );
  const userSourceBadge = buildRuntimeDetailSourceBadge(userBusinessRequests.sourceLabel);
  const satelliteSourceBadge = buildRuntimeDetailSourceBadge(satelliteResourceRows.sourceLabel);
  const detailScopeNotes = [
    ...buildDataPanelDetailScopeNotes(
      userBusinessRequests,
      satelliteResourceRows,
      userRequestSummary,
      satelliteServiceSummary,
      runtimeStatus.satellite_kpi_slices_v1,
      runtimeStatus.satellite_kpi_history_v1
    ),
    ...buildDataPanelFilterScopeNotes(
      userRequestSummary,
      satelliteServiceSummary,
      routeExplanationSummary
    ),
    ...buildDataPanelPaginationContractNotes(detailPaginationContract),
    buildDataPanelDetailWindowPolicyNote(
      userDetailWindow,
      satelliteDetailWindow,
      detailPaginationContract
    )
  ];
  const submitUserConfigurationValidation = async () => {
    if (
      userConfigurationValidatePending ||
      !userConfigurationPreflightModeEnabled(
        userConfigurationPreflightMode,
        onUserConfigurationValidate,
        onUserConfigurationValidateText
      )
    ) {
      return;
    }
    setUserConfigurationValidatePending(true);
    setUserConfigurationValidateError(null);
    setUserConfigurationApplyStatus(null);
    try {
      const report =
        userConfigurationPreflightMode === "json_mapping"
          ? await onUserConfigurationValidate!(
              JSON.parse(userConfigurationValidateText) as unknown
            )
          : await onUserConfigurationValidateText!(
              userConfigurationValidateText,
              userConfigurationTextEndpointFormat(userConfigurationPreflightMode)
            );
      setUserConfigurationValidateReport(report);
    } catch (error) {
      setUserConfigurationValidateReport(null);
      const message = error instanceof Error ? error.message : String(error);
      setUserConfigurationValidateError(`配置预检失败：${message}`);
    } finally {
      setUserConfigurationValidatePending(false);
    }
  };
  const applyUserConfigurationValidation = () => {
    if (onUserConfigurationApply === undefined) {
      return;
    }
    const payload = selectUserConfigurationApplyPayload(userConfigurationValidateReport);
    if (payload === null || userConfigurationValidateReport === null) {
      return;
    }
    onUserConfigurationApply(payload, userConfigurationValidateReport.apply_command);
    setUserConfigurationApplyStatus(
      `已发送 ${userConfigurationValidateReport.apply_command.type}/${userConfigurationValidateReport.apply_command.action}，后端将重建仿真 session`
    );
  };
  const userConfigurationApplyPayload = selectUserConfigurationApplyPayload(
    userConfigurationValidateReport
  );
  const userConfigurationPreflightDisabled =
    userConfigurationValidatePending ||
    !userConfigurationPreflightModeEnabled(
      userConfigurationPreflightMode,
      onUserConfigurationValidate,
      onUserConfigurationValidateText
    );

  return (
    <section className="data-panel" aria-label="独立数据态势面板">
      <div className="data-panel-hero">
        <div className="data-panel-title-block">
          <div className="surface-kicker">全链路实时观测</div>
          <h1>数据态势面板</h1>
          <p>轨道、网络、算力与事件流联动状态。该页面独立承载数据分析，不与三维控制台混排。</p>
          <div className="data-panel-actions">
            <a href="/" className="data-panel-action" onClick={onNavigateControl}>
              返回三维控制台
            </a>
            <a href={runtimeExportArchiveHref()} className="data-panel-action" download>
              导出复盘包
            </a>
          </div>
        </div>
        <div className="data-panel-runtime">
          <div>
            <span>运行状态</span>
            <strong>{runtimeStatusLabel(runtimeStatus)}</strong>
          </div>
          <div>
            <span>仿真模式</span>
            <strong>{runtimeModeLabel(runtimeStatus.mode)}</strong>
          </div>
          <div>
            <span>速度</span>
            <strong>{runtimeSpeedFactorLabel(runtimeStatus)}</strong>
          </div>
          <div>
            <span>配置规模</span>
            <strong>{configuredScale}</strong>
          </div>
          <div>
            <span>业务类型</span>
            <strong>{trafficDisplay.label}</strong>
            {trafficDisplay.note ? (
              <small className="data-panel-runtime-note">{trafficDisplay.note}</small>
            ) : null}
          </div>
          {reproducibilityDisplay ? (
            <div className="data-panel-runtime-wide">
              <span>复现清单</span>
              <strong>{reproducibilityDisplay.primaryLabel}</strong>
              <small className="data-panel-runtime-note">
                {reproducibilityDisplay.secondaryLabel}
              </small>
            </div>
          ) : null}
          {exportHistoryDisplay ? (
            <div className="data-panel-runtime-wide">
              <span>最近导出</span>
              <strong>{exportHistoryDisplay.primaryLabel}</strong>
              <small className="data-panel-runtime-note">
                {exportHistoryDisplay.secondaryLabel}
              </small>
            </div>
          ) : null}
        </div>
      </div>

      <div className="data-panel-progress" aria-label="仿真进度概览">
        <div className="summary-title-row">
          <span>仿真进度</span>
          <strong>{runtimeProgress.percentLabel}</strong>
        </div>
        <progress value={runtimeProgress.percent} max="100" aria-label="数据面板仿真进度" />
        <div className="runtime-progress-meta">
          <span>
            {runtimeProgress.elapsedLabel} / {runtimeProgress.durationLabel}
          </span>
          <span>{summary.eventCount} 个离散事件</span>
        </div>
      </div>

      {userConfigurationContractDisplay ? (
        <section
          className="dashboard-section data-panel-config-contract"
          aria-label="用户配置契约"
        >
          <div className="section-title">用户配置契约</div>
          <div className="data-panel-source-note">
            <span>{userConfigurationContractDisplay.sourceLabel}</span>
            <small>{userConfigurationContractDisplay.summaryLabel}</small>
          </div>
          <div
            className={`data-panel-export-compare ${userConfigurationContractDisplay.tone}`}
          >
            <div>
              <span>配置 schema v2</span>
              <strong>{userConfigurationContractDisplay.statusLabel}</strong>
              <small>{userConfigurationContractDisplay.detailLabel}</small>
            </div>
            <div className="data-panel-export-compare-meta">
              {userConfigurationContractDisplay.metaLabels.map((label) => (
                <span key={label}>{label}</span>
              ))}
            </div>
            <div className="data-panel-export-catalog-actions">
              <a href={userConfigurationContractDisplay.schemaHref}>schema</a>
              <a href={userConfigurationContractDisplay.templatesHref}>templates</a>
              <a href={userConfigurationContractDisplay.referenceHref}>reference</a>
              <a href={userConfigurationContractDisplay.exportHref} download>
                export
              </a>
            </div>
          </div>
          <div className="data-panel-config-validate" aria-label="用户配置预检">
            <div className="data-panel-config-validate-head">
              <div>
                <span>配置预检</span>
                <strong>预检通过后可显式应用</strong>
              </div>
              <div className="data-panel-config-validate-actions">
                <select
                  aria-label="用户配置预检格式"
                  value={userConfigurationPreflightMode}
                  disabled={userConfigurationValidatePending}
                  onChange={(event) => {
                    const nextMode = event.target.value as UserConfigurationPreflightMode;
                    setUserConfigurationPreflightMode(nextMode);
                    if (
                      nextMode === "yaml_text" &&
                      userConfigurationValidateText === DEFAULT_USER_CONFIGURATION_VALIDATE_TEXT
                    ) {
                      setUserConfigurationValidateText(
                        DEFAULT_USER_CONFIGURATION_VALIDATE_YAML_TEXT
                      );
                    }
                    if (
                      nextMode === "json_mapping" &&
                      userConfigurationValidateText ===
                        DEFAULT_USER_CONFIGURATION_VALIDATE_YAML_TEXT
                    ) {
                      setUserConfigurationValidateText(
                        DEFAULT_USER_CONFIGURATION_VALIDATE_TEXT
                      );
                    }
                  }}
                >
                  <option value="json_mapping">JSON 映射</option>
                  <option value="auto_text">自动文本</option>
                  <option value="yaml_text">YAML 文本</option>
                  <option value="json_text">JSON 文本</option>
                </select>
                <button
                  type="button"
                  disabled={userConfigurationPreflightDisabled}
                  onClick={() => {
                    void submitUserConfigurationValidation();
                  }}
                >
                  {userConfigurationValidatePending ? "预检中" : "预检"}
                </button>
                <button
                  type="button"
                  disabled={
                    userConfigurationValidatePending ||
                    onUserConfigurationApply === undefined ||
                    userConfigurationApplyPayload === null
                  }
                  onClick={applyUserConfigurationValidation}
                >
                  应用配置
                </button>
              </div>
            </div>
            <textarea
              aria-label="待预检用户配置文本"
              spellCheck={false}
              value={userConfigurationValidateText}
              onChange={(event) => setUserConfigurationValidateText(event.target.value)}
            />
            {userConfigurationValidationDisplay ? (
              <div
                className={`data-panel-config-validate-result ${userConfigurationValidationDisplay.tone}`}
              >
                <div>
                  <span>{userConfigurationValidationDisplay.statusLabel}</span>
                  <strong>{userConfigurationValidationDisplay.detailLabel}</strong>
                </div>
                <div className="data-panel-config-validate-meta">
                  {userConfigurationValidationDisplay.metaLabels.map((label) => (
                    <span key={label}>{label}</span>
                  ))}
                </div>
                {userConfigurationValidationDisplay.readinessLabels.length > 0 ? (
                  <div
                    className="data-panel-config-readiness-tags"
                    aria-label="配置应用运行态就绪说明"
                  >
                    {userConfigurationValidationDisplay.readinessLabels.map((label) => (
                      <span key={label}>{label}</span>
                    ))}
                  </div>
                ) : null}
                {userConfigurationValidationDisplay.changeLabels.length > 0 ? (
                  <div className="data-panel-config-change-summary">
                    <div className="data-panel-config-change-tags">
                      {userConfigurationValidationDisplay.changeLabels.map((label) => (
                        <span key={label}>{label}</span>
                      ))}
                    </div>
                    {userConfigurationValidationDisplay.changeRows.length > 0 ? (
                      <div className="data-panel-config-change-list">
                        {userConfigurationValidationDisplay.changeRows.map((row) => (
                          <div key={row.path} className="data-panel-config-change-row">
                            <span>{row.path}</span>
                            <strong>{row.valueLabel}</strong>
                            <small>{row.changeType}</small>
                          </div>
                        ))}
                      </div>
                    ) : null}
                  </div>
                ) : null}
                {userConfigurationValidationDisplay.errorLabels.length > 0 ? (
                  <div className="data-panel-config-validate-errors">
                    {userConfigurationValidationDisplay.errorLabels.map((label) => (
                      <span key={label}>{label}</span>
                    ))}
                  </div>
                ) : null}
              </div>
            ) : null}
          </div>
          {userConfigurationContractDisplay.fieldSections.length > 0 ? (
            <div
              className="data-panel-config-field-browser"
              aria-label="用户配置字段分组"
            >
              {userConfigurationContractDisplay.fieldSections.map((section) => (
                <div className="data-panel-config-field-section" key={section.sectionPath}>
                  <div className="data-panel-config-field-section-head">
                    <strong>{section.sectionPath}</strong>
                    <small>{section.purpose}</small>
                  </div>
                  <div className="data-panel-config-field-section-meta">
                    {section.metaLabels.map((label) => (
                      <span key={label}>{label}</span>
                    ))}
                  </div>
                  <div className="data-panel-config-field-list">
                    {section.sampleFields.map((field) => (
                      <span key={field.path} title={field.description}>
                        {field.label}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          ) : null}
          {userConfigurationContractDisplay.referenceRows.length > 0 ? (
            <details
              className="data-panel-config-reference-browser"
              aria-label="完整用户配置参考浏览"
              open
            >
              <summary>
                <div>
                  <strong>完整配置参考</strong>
                  <small>后端 reference 驱动，展示关键控件与文件专属字段</small>
                </div>
                <span>{userConfigurationContractDisplay.referenceRows.length} 字段</span>
              </summary>
              <div className="data-panel-config-reference-meta">
                {userConfigurationContractDisplay.referenceSummaryLabels.map((label) => (
                  <span key={label}>{label}</span>
                ))}
              </div>
              {userConfigurationContractDisplay.referenceBoundaryLabels.length > 0 ? (
                <div
                  className="data-panel-config-reference-meta"
                  aria-label="配置参考模型边界"
                >
                  {userConfigurationContractDisplay.referenceBoundaryLabels.map((label) => (
                    <span key={label}>{label}</span>
                  ))}
                </div>
              ) : null}
              {userConfigurationContractDisplay.referenceWorkflowLabels.length > 0 ? (
                <div
                  className="data-panel-config-reference-meta"
                  aria-label="配置参考操作流程"
                >
                  {userConfigurationContractDisplay.referenceWorkflowLabels.map((label) => (
                    <span key={label}>{label}</span>
                  ))}
                </div>
              ) : null}
              {userConfigurationContractDisplay.referenceSections.length > 0 ? (
                <div
                  className="data-panel-config-reference-sections"
                  aria-label="配置参考分区摘要"
                >
                  {userConfigurationContractDisplay.referenceSections.map((section) => (
                    <div
                      className="data-panel-config-reference-section"
                      key={section.sectionPath}
                    >
                      <strong>{section.sectionPath}</strong>
                      <small>{section.purpose}</small>
                      <span>{section.metaLabels.join(" / ")}</span>
                    </div>
                  ))}
                </div>
              ) : null}
              <div
                className="data-panel-config-reference-table"
                role="table"
                aria-label="完整用户配置字段表"
              >
                <div className="data-panel-config-reference-row header" role="row">
                  <span role="columnheader">路径</span>
                  <span role="columnheader">分区</span>
                  <span role="columnheader">名称</span>
                  <span role="columnheader">类型</span>
                  <span role="columnheader">编辑面</span>
                  <span role="columnheader">当前值</span>
                  <span role="columnheader">默认值</span>
                  <span role="columnheader">校验</span>
                </div>
                {userConfigurationContractDisplay.referenceRows.map((field) => (
                  <div
                    className="data-panel-config-reference-row"
                    key={field.path}
                    role="row"
                    title={field.description}
                  >
                    <span role="cell">{field.path}</span>
                    <span role="cell">{field.section}</span>
                    <span role="cell">{field.label}</span>
                    <span role="cell">{field.typeLabel}</span>
                    <span role="cell">{field.surfaceLabel}</span>
                    <span role="cell">{field.currentValueLabel}</span>
                    <span role="cell">{field.defaultValueLabel}</span>
                    <span role="cell">{field.validationLabel}</span>
                  </div>
                ))}
              </div>
            </details>
          ) : null}
        </section>
      ) : null}

      {exportCatalogDisplay ? (
        <section className="dashboard-section data-panel-export-catalog" aria-label="复盘包目录">
          <div className="section-title">复盘包目录</div>
          <div className="data-panel-source-note">
            <span>{exportCatalogDisplay.sourceLabel}</span>
            <small>{exportCatalogDisplay.summaryLabel}</small>
          </div>
          {exportReviewSummaryStatus ? (
            <div
              className={`data-panel-export-compare ${exportReviewSummaryStatus.tone}`}
              aria-label="复盘包审阅摘要"
            >
              <div>
                <span>审阅摘要</span>
                <strong>{exportReviewSummaryStatus.statusLabel}</strong>
                <small>{exportReviewSummaryStatus.summaryLabel}</small>
              </div>
              <div className="data-panel-export-compare-meta">
                {exportReviewSummaryStatus.metaLabels.map((label) => (
                  <span key={label}>{label}</span>
                ))}
              </div>
              {exportReviewSummaryStatus.artifactLabels.length > 0 ? (
                <div className="data-panel-export-compare-diffs">
                  {exportReviewSummaryStatus.artifactLabels.map((label) => (
                    <span key={label}>{label}</span>
                  ))}
                </div>
              ) : null}
            </div>
          ) : null}
          {exportArtifactHealthDisplay ? (
            <div
              className="data-panel-export-artifact-health"
              aria-label="复盘包文件健康"
            >
              <div className="data-panel-source-note">
                <span>{exportArtifactHealthDisplay.sourceLabel}</span>
                <small>{exportArtifactHealthDisplay.summaryLabel}</small>
              </div>
              <div className="data-panel-export-artifact-health-grid">
                {exportArtifactHealthDisplay.rows.map((row) =>
                  row.href ? (
                    <a href={row.href} key={row.filename} title={row.title}>
                      <span>{row.filename}</span>
                      <strong className={row.present ? "present" : "missing"}>
                        {row.statusLabel}
                      </strong>
                      <small>
                        {row.roleLabel} / {row.sizeLabel} / {row.hashLabel}
                      </small>
                    </a>
                  ) : (
                    <span key={row.filename} title={row.title}>
                      <span>{row.filename}</span>
                      <strong className={row.present ? "present" : "missing"}>
                        {row.statusLabel}
                      </strong>
                      <small>
                        {row.roleLabel} / {row.sizeLabel} / {row.hashLabel}
                      </small>
                    </span>
                  )
                )}
              </div>
            </div>
          ) : null}
          {exportDiagnosticsStatus ? (
            <div
              className={`data-panel-export-diagnostics-drawer ${exportDiagnosticsStatus.tone}`}
              aria-label="复盘包诊断抽屉"
            >
              <div className="data-panel-export-diagnostics-header">
                <div>
                  <span>诊断包</span>
                  <strong>{exportDiagnosticsStatus.statusLabel}</strong>
                  <small>{exportDiagnosticsStatus.summaryLabel}</small>
                </div>
                {exportDiagnosticsStatus.diagnosticsHref ? (
                  <a href={exportDiagnosticsStatus.diagnosticsHref}>
                    diagnostics JSON
                  </a>
                ) : null}
              </div>
              <div className="data-panel-export-compare-meta">
                {exportDiagnosticsStatus.metaLabels.map((label) => (
                  <span key={label}>{label}</span>
                ))}
              </div>
              {exportDiagnosticsStatus.modelBoundaryLabels.length > 0 ? (
                <div className="data-panel-export-diagnostics-boundaries">
                  {exportDiagnosticsStatus.modelBoundaryLabels.map((label) => (
                    <span key={label}>{label}</span>
                  ))}
                </div>
              ) : null}
              {exportDiagnosticsStatus.findingRows.length > 0 ? (
                <div className="data-panel-export-diagnostics-findings">
                  {exportDiagnosticsStatus.findingRows.map((row) => (
                    <span
                      className={row.tone}
                      key={`${row.severity}:${row.code}:${row.message}`}
                      title={row.message}
                    >
                      <strong>{row.severity}</strong>
                      {row.code}
                      <small>{row.message}</small>
                    </span>
                  ))}
                </div>
              ) : null}
              {exportDiagnosticsStatus.actionLabels.length > 0 ? (
                <div className="data-panel-export-diagnostics-actions">
                  {exportDiagnosticsStatus.actionLabels.map((label) => (
                    <span key={label}>{label}</span>
                  ))}
                </div>
              ) : null}
            </div>
          ) : null}
          {exportServiceLifecycleTraceStatus ? (
            <div
              className={`data-panel-export-diagnostics-drawer ${exportServiceLifecycleTraceStatus.tone}`}
              aria-label="复盘包服务链路 trace"
            >
              <div className="data-panel-export-diagnostics-header">
                <div>
                  <span>Service lifecycle trace</span>
                  <strong>{exportServiceLifecycleTraceStatus.statusLabel}</strong>
                  <small>{exportServiceLifecycleTraceStatus.summaryLabel}</small>
                </div>
                {exportServiceLifecycleTraceStatus.traceHref ? (
                  <a href={exportServiceLifecycleTraceStatus.traceHref}>
                    service trace JSON
                  </a>
                ) : null}
              </div>
              <div className="data-panel-export-compare-meta">
                {exportServiceLifecycleTraceStatus.metaLabels.map((label) => (
                  <span key={label}>{label}</span>
                ))}
              </div>
              {exportServiceLifecycleTraceStatus.display ? (
                <div className="data-panel-export-route-index-tools">
                  <ServiceTraceFilterControls
                    filterValue={exportServiceTraceFilter}
                    terminalFilter={exportServiceTraceTerminalFilter}
                    computeNodeFilter={exportServiceTraceComputeNodeFilter}
                    stageFilter={exportServiceTraceStageFilter}
                    terminalReasonFilter={exportServiceTraceTerminalReasonFilter}
                    onFilterChange={(value) => {
                      setExportServiceTraceFilter(value);
                      requestRuntimeExportServiceTracePage(0, { query: value });
                    }}
                    onTerminalFilterChange={(value) => {
                      setExportServiceTraceTerminalFilter(value);
                      requestRuntimeExportServiceTracePage(0, {
                        terminalState: value
                      });
                    }}
                    onComputeNodeFilterChange={(value) => {
                      setExportServiceTraceComputeNodeFilter(value);
                      requestRuntimeExportServiceTracePage(0, {
                        computeNodeId: value
                      });
                    }}
                    onStageFilterChange={(value) => {
                      setExportServiceTraceStageFilter(value);
                      requestRuntimeExportServiceTracePage(0, { stageKind: value });
                    }}
                    onTerminalReasonFilterChange={(value) => {
                      setExportServiceTraceTerminalReasonFilter(value);
                      requestRuntimeExportServiceTracePage(0, {
                        terminalReason: value
                      });
                    }}
                  />
                  <div className="data-panel-export-route-index-pager">
                    <button
                      type="button"
                      disabled={!exportServiceLifecycleTraceStatus.canPreviousPage}
                      onClick={() =>
                        requestRuntimeExportServiceTracePage(
                          exportServiceLifecycleTraceStatus.previousCursor
                        )
                      }
                    >
                      Previous
                    </button>
                    <button
                      type="button"
                      disabled={!exportServiceLifecycleTraceStatus.canNextPage}
                      onClick={() =>
                        requestRuntimeExportServiceTracePage(
                          exportServiceLifecycleTraceStatus.nextCursor
                        )
                      }
                    >
                      Next
                    </button>
                  </div>
                  <span>{exportServiceLifecycleTraceStatus.filterLabel}</span>
                </div>
              ) : null}
              {exportServiceLifecycleTraceStatus.display ? (
                <ServiceLifecycleTracePanel
                  display={exportServiceLifecycleTraceStatus.display}
                />
              ) : null}
            </div>
          ) : null}
          {exportUserServiceRequestStatus ? (
            <div
              className={`data-panel-export-diagnostics-drawer ${exportUserServiceRequestStatus.tone}`}
              aria-label="复盘包用户业务请求artifact"
            >
              <div className="data-panel-export-diagnostics-header">
                <div>
                  <span>User service requests</span>
                  <strong>{exportUserServiceRequestStatus.statusLabel}</strong>
                  <small>{exportUserServiceRequestStatus.summaryLabel}</small>
                </div>
                {exportUserServiceRequestStatus.artifactHref ? (
                  <a href={exportUserServiceRequestStatus.artifactHref}>
                    user services JSON
                  </a>
                ) : null}
              </div>
              <div className="data-panel-export-compare-meta">
                {exportUserServiceRequestStatus.metaLabels.map((label) => (
                  <span key={label}>{label}</span>
                ))}
              </div>
              <div className="data-panel-export-route-index-tools">
                <BackendTextFilter
                  label="User service filter"
                  value={exportUserServiceRequestFilter}
                  placeholder="user / service / sat / compute"
                  onChange={(query) => {
                    setExportUserServiceRequestFilter(query);
                    requestRuntimeExportUserServiceRequestPage(0, { query });
                  }}
                />
                <label
                  className="data-panel-export-route-index-search"
                  htmlFor="data-panel-export-user-service-class"
                >
                  <span>service class</span>
                  <select
                    id="data-panel-export-user-service-class"
                    value={exportUserServiceRequestClassFilter}
                    onChange={(event) => {
                      const serviceClass = event.currentTarget.value;
                      setExportUserServiceRequestClassFilter(serviceClass);
                      requestRuntimeExportUserServiceRequestPage(0, {
                        serviceClass
                      });
                    }}
                  >
                    <option value="ALL">ALL</option>
                    <option value="DATA_TRANSFER">DATA_TRANSFER</option>
                    <option value="TELEMETRY">TELEMETRY</option>
                    <option value="BULK_DOWNLINK">BULK_DOWNLINK</option>
                    <option value="COMPUTE_SERVICE">COMPUTE_SERVICE</option>
                  </select>
                </label>
                <label
                  className="data-panel-export-route-index-search"
                  htmlFor="data-panel-export-user-terminal-state"
                >
                  <span>terminal state</span>
                  <select
                    id="data-panel-export-user-terminal-state"
                    value={exportUserServiceRequestTerminalFilter}
                    onChange={(event) => {
                      const terminalState = event.currentTarget.value;
                      setExportUserServiceRequestTerminalFilter(terminalState);
                      requestRuntimeExportUserServiceRequestPage(0, {
                        terminalState
                      });
                    }}
                  >
                    <option value="ALL">ALL</option>
                    <option value="ACTIVE">ACTIVE</option>
                    <option value="RUNNING">RUNNING</option>
                    <option value="WAITING_NETWORK">WAITING_NETWORK</option>
                    <option value="COMPLETED">COMPLETED</option>
                    <option value="FAILED">FAILED</option>
                    <option value="IDLE">IDLE</option>
                  </select>
                </label>
                <label
                  className="data-panel-export-route-index-search"
                  htmlFor="data-panel-export-user-network-waiting"
                >
                  <span>network waiting</span>
                  <select
                    id="data-panel-export-user-network-waiting"
                    value={exportUserServiceRequestWaitingFilter}
                    onChange={(event) => {
                      const networkWaiting = event.currentTarget.value;
                      setExportUserServiceRequestWaitingFilter(networkWaiting);
                      requestRuntimeExportUserServiceRequestPage(0, {
                        networkWaiting
                      });
                    }}
                  >
                    <option value="ALL">ALL</option>
                    <option value="WAITING">WAITING</option>
                    <option value="READY">READY</option>
                  </select>
                </label>
                <div className="data-panel-export-route-index-pager">
                  <button
                    type="button"
                    disabled={!exportUserServiceRequestStatus.canPreviousPage}
                    onClick={() =>
                      requestRuntimeExportUserServiceRequestPage(
                        exportUserServiceRequestStatus.previousCursor
                      )
                    }
                  >
                    Previous
                  </button>
                  <button
                    type="button"
                    disabled={!exportUserServiceRequestStatus.canNextPage}
                    onClick={() =>
                      requestRuntimeExportUserServiceRequestPage(
                        exportUserServiceRequestStatus.nextCursor
                      )
                    }
                  >
                    Next
                  </button>
                </div>
                <span>{exportUserServiceRequestStatus.filterLabel}</span>
              </div>
              <UserBusinessRequestTable
                rows={exportUserServiceRequestStatus.rows}
                selectedUserId={selectedDetailUserId}
                onSelect={openRuntimeExportUserServiceRequestEvidence}
              />
            </div>
          ) : null}
          {exportRouteDetailIndexStatus ? (
            <div
              className={`data-panel-export-diagnostics-drawer ${exportRouteDetailIndexStatus.tone}`}
              aria-label="复盘包路由证据索引"
            >
              <div className="data-panel-export-diagnostics-header">
                <div>
                  <span>路由证据索引</span>
                  <strong>{exportRouteDetailIndexStatus.statusLabel}</strong>
                  <small>{exportRouteDetailIndexStatus.summaryLabel}</small>
                </div>
                {exportRouteDetailIndexStatus.indexHref ? (
                  <a href={exportRouteDetailIndexStatus.indexHref}>
                    route index JSON
                  </a>
                ) : null}
              </div>
              <div className="data-panel-export-compare-meta">
                {exportRouteDetailIndexStatus.metaLabels.map((label) => (
                  <span key={label}>{label}</span>
                ))}
              </div>
              {exportRouteDetailIndexStatus.boundaryLabels.length > 0 ? (
                <div className="data-panel-export-diagnostics-boundaries">
                  {exportRouteDetailIndexStatus.boundaryLabels.map((label) => (
                    <span key={label}>{label}</span>
                  ))}
                </div>
              ) : null}
              {exportRouteDetailIndexStatus.indexHref ? (
                <div className="data-panel-export-route-index-tools">
                  <label
                    className="data-panel-export-route-index-search"
                    htmlFor="data-panel-export-route-index-filter"
                  >
                    <span>route evidence search</span>
                    <input
                      id="data-panel-export-route-index-filter"
                      type="search"
                      value={exportRouteDetailIndexFilter}
                      onChange={(event) => {
                        const query = event.currentTarget.value;
                        setExportRouteDetailIndexFilter(query);
                        requestRuntimeExportRouteDetailPage(0, { query });
                      }}
                      placeholder="route / user / satellite / service / bottleneck"
                    />
                  </label>
                  <label
                    className="data-panel-export-route-index-search"
                    htmlFor="data-panel-export-route-index-availability"
                  >
                    <span>availability</span>
                    <select
                      id="data-panel-export-route-index-availability"
                      value={exportRouteDetailIndexAvailabilityFilter}
                      onChange={(event) => {
                        const availability = event.currentTarget
                          .value as DataPanelRouteExplanationAvailabilityFilter;
                        setExportRouteDetailIndexAvailabilityFilter(availability);
                        requestRuntimeExportRouteDetailPage(0, { availability });
                      }}
                    >
                      <option value="ALL">ALL</option>
                      <option value="AVAILABLE">AVAILABLE</option>
                      <option value="BLOCKED">BLOCKED</option>
                    </select>
                  </label>
                  <label
                    className="data-panel-export-route-index-search"
                    htmlFor="data-panel-export-route-index-business"
                  >
                    <span>business</span>
                    <select
                      id="data-panel-export-route-index-business"
                      value={exportRouteDetailIndexBusinessFilter}
                      onChange={(event) => {
                        const businessType = event.currentTarget.value;
                        setExportRouteDetailIndexBusinessFilter(businessType);
                        requestRuntimeExportRouteDetailPage(0, { businessType });
                      }}
                    >
                      <option value="ALL">ALL</option>
                      <option value="COMPUTE_SERVICE">COMPUTE_SERVICE</option>
                      <option value="DATA_TRANSFER">DATA_TRANSFER</option>
                      <option value="BULK_DOWNLINK">BULK_DOWNLINK</option>
                    </select>
                  </label>
                  <label
                    className="data-panel-export-route-index-search"
                    htmlFor="data-panel-export-route-index-bottleneck"
                  >
                    <span>bottleneck</span>
                    <select
                      id="data-panel-export-route-index-bottleneck"
                      value={exportRouteDetailIndexBottleneckFilter}
                      onChange={(event) => {
                        const bottleneckComponent = event.currentTarget.value;
                        setExportRouteDetailIndexBottleneckFilter(bottleneckComponent);
                        requestRuntimeExportRouteDetailPage(0, {
                          bottleneckComponent
                        });
                      }}
                    >
                      <option value="ALL">ALL</option>
                      <option value="CAPACITY">CAPACITY</option>
                      <option value="AVAILABILITY">AVAILABILITY</option>
                      <option value="LOSS_PROXY">LOSS_PROXY</option>
                      <option value="PATH">PATH</option>
                      <option value="NONE">NONE</option>
                    </select>
                  </label>
                  <div className="data-panel-export-route-index-pager">
                    <button
                      type="button"
                      disabled={
                        !exportRouteDetailIndexStatus.canPreviousPage ||
                        !onRuntimeExportRouteDetailPageQueryChange
                      }
                      onClick={() =>
                        requestRuntimeExportRouteDetailPage(
                          exportRouteDetailIndexStatus.previousCursor
                        )
                      }
                    >
                      Previous
                    </button>
                    <button
                      type="button"
                      disabled={
                        !exportRouteDetailIndexStatus.canNextPage ||
                        !onRuntimeExportRouteDetailPageQueryChange
                      }
                      onClick={() =>
                        requestRuntimeExportRouteDetailPage(
                          exportRouteDetailIndexStatus.nextCursor
                        )
                      }
                    >
                      Next
                    </button>
                  </div>
                  <span>{exportRouteDetailIndexStatus.filterLabel}</span>
                </div>
              ) : null}
              {exportRouteDetailIndexStatus.routeRows.length > 0 ? (
                <div className="data-panel-export-diagnostics-findings">
                  {exportRouteDetailIndexStatus.routeRows.map((row) => (
                    <span
                      className={row.available ? "info" : "warn"}
                      key={row.routeId}
                      title={row.title}
                    >
                      <strong>{row.routeId}</strong>
                      {row.pathLabel}
                      <small>{row.metricLabel}</small>
                      <a href={row.packageDetailHref}>package route JSON</a>
                      <button
                        type="button"
                        disabled={!onRuntimeExportRouteDetailItemSelect}
                        onClick={() => {
                          onRuntimeExportRouteDetailItemSelect?.(row.routeId);
                        }}
                      >
                        package route detail
                      </button>
                      <button
                        type="button"
                        disabled={
                          !onRuntimeExportRouteDetailItemSelect ||
                          !onRuntimeRouteDetailSelect
                        }
                        onClick={() => {
                          onRuntimeExportRouteDetailItemSelect?.(row.routeId);
                          setSelectedRouteDetailId(row.routeId);
                          onRuntimeRouteDetailSelect?.(row.routeId);
                        }}
                      >
                        {row.compareActionLabel}
                      </button>
                      <button
                        type="button"
                        onClick={() => {
                          setSelectedRouteDetailId(row.routeId);
                          onRuntimeRouteDetailSelect?.(row.routeId);
                        }}
                      >
                        {row.liveDetailActionLabel}
                      </button>
                    </span>
                  ))}
                </div>
              ) : null}
              {exportRouteDetailItemStatus ? (
                <div
                  className={`data-panel-export-route-detail-card ${exportRouteDetailItemStatus.tone}`}
                >
                  <div className="data-panel-export-diagnostics-header">
                    <div>
                      <span>Package route detail</span>
                      <strong>{exportRouteDetailItemStatus.statusLabel}</strong>
                      <small>{exportRouteDetailItemStatus.summaryLabel}</small>
                    </div>
                    {exportRouteDetailItemStatus.detailHref ? (
                      <a href={exportRouteDetailItemStatus.detailHref}>
                        route detail JSON
                      </a>
                    ) : null}
                  </div>
                  {exportRouteDetailItemStatus.fields.length > 0 ? (
                    <dl className="data-panel-export-route-detail-fields">
                      {exportRouteDetailItemStatus.fields.map((field) => (
                        <div
                          className={field.tone ?? "normal"}
                          key={field.label}
                        >
                          <dt>{field.label}</dt>
                          <dd title={field.value}>{field.value}</dd>
                        </div>
                      ))}
                    </dl>
                  ) : null}
                </div>
              ) : null}
              {exportRouteLiveComparison ? (
                <div
                  className={`data-panel-export-route-compare-card ${exportRouteLiveComparison.tone}`}
                >
                  <div className="data-panel-export-diagnostics-header">
                    <div>
                      <span>Package vs live route</span>
                      <strong>{exportRouteLiveComparison.statusLabel}</strong>
                      <small>{exportRouteLiveComparison.summaryLabel}</small>
                    </div>
                    {exportRouteComparisonReviewSaveStatus &&
                    exportRouteComparisonReviewRecord ? (
                      <div className="data-panel-export-restore-actions">
                        <button
                          type="button"
                          disabled={
                            exportRouteComparisonReviewSaveStatus.disabled ||
                            !onRuntimeExportRouteComparisonReviewSave
                          }
                          onClick={() => {
                            const packageId = runtimeExportRouteDetailItem?.package_id;
                            if (!packageId) {
                              return;
                            }
                            onRuntimeExportRouteComparisonReviewSave?.({
                              packageId,
                              record: exportRouteComparisonReviewRecord
                            });
                          }}
                        >
                          {exportRouteComparisonReviewSaveStatus.buttonLabel}
                        </button>
                        <small>{exportRouteComparisonReviewSaveStatus.detailLabel}</small>
                      </div>
                    ) : null}
                  </div>
                  <div className="data-panel-export-route-compare-rows">
                    {exportRouteLiveComparison.rows.map((row) => (
                      <div
                        className={row.matches ? "match" : "different"}
                        key={row.field}
                      >
                        <span>{row.field}</span>
                        <strong>{row.statusLabel}</strong>
                        <small title={row.packageValue}>
                          package: {row.packageValue}
                        </small>
                        <small title={row.liveValue}>live: {row.liveValue}</small>
                      </div>
                    ))}
                  </div>
                </div>
              ) : null}
              {exportRouteLiveComparisonStatus ? (
                <div
                  className={`data-panel-export-route-compare-card ${exportRouteLiveComparisonStatus.tone}`}
                >
                  <div className="data-panel-export-diagnostics-header">
                    <div>
                      <span>Package vs live route</span>
                      <strong>{exportRouteLiveComparisonStatus.statusLabel}</strong>
                      <small>{exportRouteLiveComparisonStatus.summaryLabel}</small>
                    </div>
                  </div>
                  <div className="data-panel-export-route-compare-note">
                    {exportRouteLiveComparisonStatus.notes.map((note) => (
                      <span key={note}>{note}</span>
                    ))}
                  </div>
                </div>
              ) : null}
              {exportRouteComparisonReviewArtifactDisplay ? (
                <div
                  className={`data-panel-export-route-compare-card ${exportRouteComparisonReviewArtifactDisplay.tone}`}
                >
                  <div className="data-panel-export-diagnostics-header">
                    <div>
                      <span>Route comparison review report</span>
                      <strong>
                        {exportRouteComparisonReviewArtifactDisplay.statusLabel}
                      </strong>
                      <small>
                        {exportRouteComparisonReviewArtifactDisplay.summaryLabel}
                      </small>
                    </div>
                    {exportRouteComparisonReviewArtifactDisplay.artifactHref ? (
                      <a
                        href={exportRouteComparisonReviewArtifactDisplay.artifactHref}
                        title={
                          exportRouteComparisonReviewArtifactDisplay.artifactTitle
                        }
                      >
                        review report JSON
                      </a>
                    ) : null}
                  </div>
                  <div className="data-panel-export-compare-meta">
                    {exportRouteComparisonReviewArtifactDisplay.hashLabels.map(
                      (label) => (
                        <span key={label}>{label}</span>
                      )
                    )}
                  </div>
                </div>
              ) : null}
              {exportPackageAuditIndexArtifactDisplay ? (
                <div
                  className={`data-panel-export-route-compare-card ${exportPackageAuditIndexArtifactDisplay.tone}`}
                >
                  <div className="data-panel-export-diagnostics-header">
                    <div>
                      <span>Export package audit index</span>
                      <strong>
                        {exportPackageAuditIndexArtifactDisplay.statusLabel}
                      </strong>
                      <small>
                        {exportPackageAuditIndexArtifactDisplay.summaryLabel}
                      </small>
                    </div>
                    {exportPackageAuditIndexArtifactDisplay.artifactHref ? (
                      <a
                        href={exportPackageAuditIndexArtifactDisplay.artifactHref}
                        title={exportPackageAuditIndexArtifactDisplay.artifactTitle}
                      >
                        audit index JSON
                      </a>
                    ) : null}
                  </div>
                  <div className="data-panel-export-compare-meta">
                    {exportPackageAuditIndexArtifactDisplay.hashLabels.map(
                      (label) => (
                        <span key={label}>{label}</span>
                      )
                    )}
                  </div>
                </div>
              ) : null}
              {exportReviewCompletionSummary ? (
                <div
                  className={`data-panel-export-route-compare-card ${exportReviewCompletionSummary.tone}`}
                >
                  <div className="data-panel-export-diagnostics-header">
                    <div>
                      <span>Package review completion</span>
                      <strong>
                        {exportReviewCompletionSummary.statusLabel}
                      </strong>
                      <small>
                        {exportReviewCompletionSummary.summaryLabel}
                      </small>
                    </div>
                  </div>
                  <div className="data-panel-export-compare-meta">
                    {exportReviewCompletionSummary.evidenceLabels.map((label) => (
                      <span key={label}>{label}</span>
                    ))}
                  </div>
                  {exportReviewCompletionSummary.warningLabels.length > 0 ? (
                    <div className="data-panel-export-diagnostics-findings">
                      {exportReviewCompletionSummary.warningLabels.map((label) => (
                        <span className="warn" key={label}>
                          <strong>{label}</strong>
                        </span>
                      ))}
                    </div>
                  ) : null}
                </div>
              ) : null}
              {exportPackageHandoffReportArtifactDisplay ? (
                <div
                  className={`data-panel-export-route-compare-card ${exportPackageHandoffReportArtifactDisplay.tone}`}
                >
                  <div className="data-panel-export-diagnostics-header">
                    <div>
                      <span>Package handoff report</span>
                      <strong>
                        {exportPackageHandoffReportArtifactDisplay.statusLabel}
                      </strong>
                      <small>
                        {exportPackageHandoffReportArtifactDisplay.summaryLabel}
                      </small>
                    </div>
                    {exportPackageHandoffReportArtifactDisplay.artifactHref ? (
                      <a
                        href={exportPackageHandoffReportArtifactDisplay.artifactHref}
                        title={
                          exportPackageHandoffReportArtifactDisplay.artifactTitle
                        }
                      >
                        handoff report MD
                      </a>
                    ) : null}
                  </div>
                  <div className="data-panel-export-compare-meta">
                    {exportPackageHandoffReportArtifactDisplay.hashLabels.map(
                      (label) => (
                        <span key={label}>{label}</span>
                      )
                    )}
                  </div>
                </div>
              ) : null}
              {exportScenarioReviewBundleStatus ? (
                <div
                  className={`data-panel-export-diagnostics-drawer ${exportScenarioReviewBundleStatus.tone}`}
                >
                  <div className="data-panel-export-diagnostics-header">
                    <div>
                      <span>Scenario review bundle</span>
                      <strong>
                        {exportScenarioReviewBundleStatus.statusLabel}
                      </strong>
                      <small>
                        {exportScenarioReviewBundleStatus.summaryLabel}
                      </small>
                    </div>
                    {exportScenarioReviewBundleStatus.bundleHref ? (
                      <a href={exportScenarioReviewBundleStatus.bundleHref}>
                        scenario review JSON
                      </a>
                    ) : null}
                  </div>
                  <div className="data-panel-export-compare-meta">
                    {exportScenarioReviewBundleStatus.scenarioLabels.map(
                      (label) => (
                        <span key={label}>{label}</span>
                      )
                    )}
                  </div>
                  <div className="data-panel-export-diagnostics-actions">
                    {exportScenarioReviewBundleStatus.configurationLabels.map(
                      (label) => (
                        <span key={label}>{label}</span>
                      )
                    )}
                  </div>
                  <div className="data-panel-export-diagnostics-boundaries">
                    {exportScenarioReviewBundleStatus.evidenceLabels.map(
                      (label) => (
                        <span key={label}>{label}</span>
                      )
                    )}
                  </div>
                  <div className="data-panel-export-compare-meta">
                    {exportScenarioReviewBundleStatus.boundaryLabels.map(
                      (label) => (
                        <span key={label}>{label}</span>
                      )
                    )}
                  </div>
                  <div className="data-panel-export-manifest-artifacts">
                    {exportScenarioReviewBundleStatus.workflowRows.map((row) => (
                      <span
                        className={row.tone}
                        key={`${row.stepLabel}:${row.detailLabel}`}
                        title={row.title}
                      >
                        <span>{row.stepLabel}</span>
                        <strong>{row.statusLabel}</strong>
                        {row.href ? (
                          <a href={row.href}>{row.detailLabel}</a>
                        ) : (
                          <small>{row.detailLabel}</small>
                        )}
                      </span>
                    ))}
                  </div>
                  <div className="data-panel-export-scenario-checklist">
                    <div className="data-panel-export-diagnostics-header">
                      <div>
                        <span>审核清单</span>
                        <strong>
                          {exportScenarioReviewChecklistStatus.statusLabel}
                        </strong>
                        <small>
                          {exportScenarioReviewChecklistStatus.summaryLabel}
                        </small>
                      </div>
                      <button
                        type="button"
                        disabled={
                          exportScenarioReviewChecklistSaveRequest === null ||
                          runtimeExportScenarioReviewChecklistSavePending === true ||
                          onRuntimeExportScenarioReviewChecklistSave === undefined
                        }
                        onClick={() => {
                          if (
                            exportScenarioReviewChecklistSaveRequest !== null &&
                            onRuntimeExportScenarioReviewChecklistSave !== undefined
                          ) {
                            onRuntimeExportScenarioReviewChecklistSave(
                              exportScenarioReviewChecklistSaveRequest
                            );
                          }
                        }}
                      >
                        保存审核清单
                      </button>
                    </div>
                    <div className="data-panel-export-scenario-checklist-rows">
                      {exportScenarioReviewBundleStatus.workflowRows.map((row) => {
                        const draft =
                          exportScenarioReviewChecklistDraft[row.detailLabel] ??
                          defaultDataPanelScenarioReviewChecklistDraftEntry(row);
                        return (
                          <label
                            className={row.tone}
                            key={`checklist:${row.stepLabel}:${row.detailLabel}`}
                          >
                            <span>{row.stepLabel}</span>
                            <select
                              value={draft.reviewStatus}
                              onChange={(event) =>
                                setExportScenarioReviewChecklistDraft((previous) =>
                                  updateDataPanelScenarioReviewChecklistDraft(
                                    previous,
                                    row.detailLabel,
                                    {
                                      reviewStatus: event.target
                                        .value as DataPanelScenarioReviewChecklistStatus
                                    }
                                  )
                                )
                              }
                            >
                              <option value="REVIEWED">已审核</option>
                              <option value="SKIPPED">跳过</option>
                              <option value="NEEDS_FOLLOWUP">需跟进</option>
                              <option value="ERROR">异常</option>
                            </select>
                            <input
                              value={draft.operatorNote}
                              onChange={(event) =>
                                setExportScenarioReviewChecklistDraft((previous) =>
                                  updateDataPanelScenarioReviewChecklistDraft(
                                    previous,
                                    row.detailLabel,
                                    { operatorNote: event.target.value }
                                  )
                                )
                              }
                              placeholder="审核备注"
                            />
                            <small>{row.detailLabel}</small>
                          </label>
                        );
                      })}
                    </div>
                    {exportScenarioReviewChecklistStatus.warningLabels.length > 0 ? (
                      <div className="data-panel-export-diagnostics-findings">
                        {exportScenarioReviewChecklistStatus.warningLabels.map(
                          (label) => (
                            <span className="warn" key={label}>
                              <strong>{label}</strong>
                            </span>
                          )
                        )}
                      </div>
                    ) : null}
                  </div>
                  {exportScenarioReviewBundleStatus.warningLabels.length > 0 ? (
                    <div className="data-panel-export-diagnostics-findings">
                      {exportScenarioReviewBundleStatus.warningLabels.map((label) => (
                        <span className="warn" key={label}>
                          <strong>REVIEW</strong>
                          {label}
                        </span>
                      ))}
                    </div>
                  ) : null}
                </div>
              ) : null}
              {exportPackageAuditIndexStatus ? (
                <div
                  className={`data-panel-export-diagnostics-drawer ${exportPackageAuditIndexStatus.tone}`}
                >
                  <div className="data-panel-export-diagnostics-header">
                    <div>
                      <span>Export package audit</span>
                      <strong>{exportPackageAuditIndexStatus.statusLabel}</strong>
                      <small>{exportPackageAuditIndexStatus.summaryLabel}</small>
                    </div>
                    {exportPackageAuditIndexStatus.auditHref ? (
                      <a href={exportPackageAuditIndexStatus.auditHref}>
                        audit JSON
                      </a>
                    ) : null}
                  </div>
                  <div className="data-panel-export-compare-meta">
                    {exportPackageAuditIndexStatus.manifestLabels.map((label) => (
                      <span key={label}>{label}</span>
                    ))}
                  </div>
                  <div className="data-panel-export-diagnostics-actions">
                    {exportPackageAuditIndexStatus.configurationLabels.map(
                      (label) => (
                        <span key={label}>{label}</span>
                      )
                    )}
                  </div>
                  <div className="data-panel-export-diagnostics-boundaries">
                    {exportPackageAuditIndexStatus.boundaryLabels.map((label) => (
                      <span key={label}>{label}</span>
                    ))}
                  </div>
                  <div className="data-panel-export-diagnostics-actions">
                    {exportPackageAuditIndexStatus.diagnosticsLabels.map((label) => (
                      <span key={label}>{label}</span>
                    ))}
                    {exportPackageAuditIndexStatus.routeReviewLabels.map((label) => (
                      <span key={label}>{label}</span>
                    ))}
                  </div>
                  <div className="data-panel-export-manifest-artifacts">
                    {exportPackageAuditIndexStatus.artifactRows.map((row) => (
                      <span key={row.filename} title={row.hashLabel}>
                        <span>{row.filename}</span>
                        <strong>{row.hashLabel}</strong>
                        <small>{row.sizeLabel}</small>
                      </span>
                    ))}
                  </div>
                  <div className="data-panel-export-compare-meta">
                    <span>{exportPackageAuditIndexStatus.artifactSummaryLabel}</span>
                  </div>
                  {exportPackageAuditIndexStatus.warningLabels.length > 0 ? (
                    <div className="data-panel-export-diagnostics-findings">
                      {exportPackageAuditIndexStatus.warningLabels.map((label) => (
                        <span className="warn" key={label}>
                          <strong>AUDIT</strong>
                          {label}
                        </span>
                      ))}
                    </div>
                  ) : null}
                </div>
              ) : null}
              {exportRouteComparisonReviewReportStatus ? (
                <div
                  className={`data-panel-export-route-compare-card ${exportRouteComparisonReviewReportStatus.tone}`}
                >
                  <div className="data-panel-export-diagnostics-header">
                    <div>
                      <span>Saved review report</span>
                      <strong>
                        {exportRouteComparisonReviewReportStatus.statusLabel}
                      </strong>
                      <small>
                        {exportRouteComparisonReviewReportStatus.summaryLabel}
                      </small>
                    </div>
                    {exportRouteComparisonReviewReportStatus.reportHref ? (
                      <a href={exportRouteComparisonReviewReportStatus.reportHref}>
                        report JSON
                      </a>
                    ) : null}
                  </div>
                  <div className="data-panel-export-compare-meta">
                    {exportRouteComparisonReviewReportStatus.metaLabels.map(
                      (label) => (
                        <span key={label}>{label}</span>
                      )
                    )}
                  </div>
                  {exportRouteComparisonReviewReportStatus.reportHref ? (
                    <div className="data-panel-export-route-index-tools">
                      <label
                        className="data-panel-export-route-index-search"
                        htmlFor="data-panel-export-review-report-filter"
                      >
                        <span>review record search</span>
                        <input
                          id="data-panel-export-review-report-filter"
                          type="search"
                          value={exportRouteReviewReportFilter}
                          onChange={(event) => {
                            setExportRouteReviewReportFilter(
                              event.currentTarget.value
                            );
                          }}
                          placeholder="route / status / hash / note"
                        />
                      </label>
                      <label
                        className="data-panel-export-route-index-search"
                        htmlFor="data-panel-export-review-report-status"
                      >
                        <span>status</span>
                        <select
                          id="data-panel-export-review-report-status"
                          value={exportRouteReviewReportStatusFilter}
                          onChange={(event) => {
                            setExportRouteReviewReportStatusFilter(
                              event.currentTarget
                                .value as DataPanelRouteComparisonReviewReportStatusFilter
                            );
                          }}
                        >
                          <option value="ALL">ALL</option>
                          <option value="MATCH">MATCH</option>
                          <option value="DIFFERENT">DIFFERENT</option>
                          <option value="UNAVAILABLE">UNAVAILABLE</option>
                          <option value="ERROR">ERROR</option>
                        </select>
                      </label>
                      <div className="data-panel-export-route-index-pager">
                        <button
                          type="button"
                          disabled={
                            !exportRouteComparisonReviewReportStatus
                              .canPreviousPage
                          }
                          onClick={() => {
                            setExportRouteReviewReportPage(
                              exportRouteComparisonReviewReportStatus.previousCursor
                            );
                          }}
                        >
                          Previous
                        </button>
                        <button
                          type="button"
                          disabled={
                            !exportRouteComparisonReviewReportStatus.canNextPage
                          }
                          onClick={() => {
                            setExportRouteReviewReportPage(
                              exportRouteComparisonReviewReportStatus.nextCursor
                            );
                          }}
                        >
                          Next
                        </button>
                      </div>
                      <span>
                        {exportRouteComparisonReviewReportStatus.filterLabel}
                      </span>
                    </div>
                  ) : null}
                  {exportRouteComparisonReviewReportStatus.recordRows.length > 0 ? (
                    <div className="data-panel-export-route-compare-rows">
                      {exportRouteComparisonReviewReportStatus.recordRows.map(
                        (row) => (
                          <div className={row.tone} key={row.routeId}>
                            <span>{row.routeId}</span>
                            <strong>{row.statusLabel}</strong>
                            <small>{row.hashLabel}</small>
                            <small title={row.noteLabel}>{row.noteLabel}</small>
                          </div>
                        )
                      )}
                    </div>
                  ) : null}
                </div>
              ) : null}
            </div>
          ) : null}
          {exportReproducibilityBoundaryDisplay ? (
            <div
              className={`data-panel-export-diagnostics-drawer ${exportReproducibilityBoundaryDisplay.tone}`}
              aria-label="结果包复现边界"
            >
              <div className="data-panel-export-diagnostics-header">
                <div>
                  <span>复现边界</span>
                  <strong>{exportReproducibilityBoundaryDisplay.statusLabel}</strong>
                  <small>{exportReproducibilityBoundaryDisplay.summaryLabel}</small>
                </div>
                {exportReproducibilityBoundaryDisplay.boundaryHref ? (
                  <a href={exportReproducibilityBoundaryDisplay.boundaryHref}>
                    boundary source
                  </a>
                ) : null}
              </div>
              <div className="data-panel-export-compare-meta">
                {exportReproducibilityBoundaryDisplay.scopeLabels.map((label) => (
                  <span key={label}>{label}</span>
                ))}
              </div>
              <div className="data-panel-export-diagnostics-boundaries">
                {exportReproducibilityBoundaryDisplay.boundaryLabels.map((label) => (
                  <span key={label}>{label}</span>
                ))}
              </div>
              <div className="data-panel-export-diagnostics-actions">
                {exportReproducibilityBoundaryDisplay.windowLabels.map((label) => (
                  <span key={label}>{label}</span>
                ))}
              </div>
              <div className="data-panel-export-diagnostics-findings">
                {exportReproducibilityBoundaryDisplay.conditionLabels.map((label) => (
                  <span className="info" key={label}>
                    <strong>BOUNDARY</strong>
                    {label}
                  </span>
                ))}
              </div>
            </div>
          ) : null}
          {exportManifestInspectorStatus ? (
            <div
              className={`data-panel-export-manifest-inspector ${exportManifestInspectorStatus.tone}`}
              aria-label="复盘包 manifest 检查器"
            >
              <div className="data-panel-export-diagnostics-header">
                <div>
                  <span>Manifest 检查器</span>
                  <strong>{exportManifestInspectorStatus.statusLabel}</strong>
                  <small>{exportManifestInspectorStatus.summaryLabel}</small>
                </div>
                {exportManifestInspectorStatus.manifestHref ? (
                  <a href={exportManifestInspectorStatus.manifestHref}>
                    manifest JSON
                  </a>
                ) : null}
              </div>
              <div className="data-panel-export-compare-meta">
                {exportManifestInspectorStatus.hashLabels.map((label) => (
                  <span key={label}>{label}</span>
                ))}
              </div>
              {exportManifestInspectorStatus.integrityLabels.length > 0 ? (
                <div className="data-panel-export-manifest-integrity">
                  {exportManifestInspectorStatus.integrityLabels.map((label) => (
                    <span key={label}>{label}</span>
                  ))}
                </div>
              ) : null}
              {exportManifestInspectorStatus.artifactRows.length > 0 ? (
                <div className="data-panel-export-manifest-artifacts">
                  {exportManifestInspectorStatus.artifactRows.map((row) => (
                    <a
                      href={row.href}
                      key={row.name}
                      title={row.title}
                      className={row.catalogPresent ? "present" : "missing"}
                    >
                      <span>{row.name}</span>
                      <strong>{row.statusLabel}</strong>
                      <small>{row.sourceLabel}</small>
                    </a>
                  ))}
                </div>
              ) : null}
            </div>
          ) : null}
          {exportBoundaryAlignmentDisplay ? (
            <div
              className={`data-panel-export-diagnostics-drawer ${exportBoundaryAlignmentDisplay.tone}`}
              aria-label="复现边界与恢复判断一致性"
            >
              <div className="data-panel-export-diagnostics-header">
                <div>
                  <span>边界一致性</span>
                  <strong>{exportBoundaryAlignmentDisplay.statusLabel}</strong>
                  <small>{exportBoundaryAlignmentDisplay.summaryLabel}</small>
                </div>
              </div>
              <div className="data-panel-export-compare-meta">
                {exportBoundaryAlignmentDisplay.evidenceLabels.map((label) => (
                  <span key={label}>{label}</span>
                ))}
              </div>
              <div className="data-panel-export-diagnostics-boundaries">
                {exportBoundaryAlignmentDisplay.compareLabels.map((label) => (
                  <span key={label}>{label}</span>
                ))}
              </div>
              <div className="data-panel-export-diagnostics-actions">
                {exportBoundaryAlignmentDisplay.restoreLabels.map((label) => (
                  <span key={label}>{label}</span>
                ))}
              </div>
              {exportBoundaryAlignmentDisplay.warningLabels.length > 0 ? (
                <div className="data-panel-export-diagnostics-findings">
                  {exportBoundaryAlignmentDisplay.warningLabels.map((label) => (
                    <span className="warn" key={label}>
                      <strong>CHECK</strong>
                      {label}
                    </span>
                  ))}
                </div>
              ) : null}
            </div>
          ) : null}
          {exportCompareStatus ? (
            <div
              className={`data-panel-export-compare ${exportCompareStatus.tone}`}
              aria-label="复盘包配置对比摘要"
            >
              <div>
                <span>配置对比</span>
                <strong>{exportCompareStatus.statusLabel}</strong>
                <small>{exportCompareStatus.summaryLabel}</small>
              </div>
              <div className="data-panel-export-compare-meta">
                {exportCompareStatus.metaLabels.map((label) => (
                  <span key={label}>{label}</span>
                ))}
              </div>
              {exportCompareStatus.diffRows.length > 0 ? (
                <div className="data-panel-export-compare-diffs">
                  {exportCompareStatus.diffRows.map((row) => (
                    <span key={`${row.section}:${row.path}`} title={row.title}>
                      {row.section} {row.path} <strong>{row.valueLabel}</strong>
                    </span>
                  ))}
                </div>
              ) : null}
            </div>
          ) : null}
          {exportRestorePreflightStatus ? (
            <div
              className={`data-panel-export-compare ${exportRestorePreflightStatus.tone}`}
              aria-label="复盘包恢复预检摘要"
            >
              <div>
                <span>恢复预检</span>
                <strong>{exportRestorePreflightStatus.statusLabel}</strong>
                <small>{exportRestorePreflightStatus.summaryLabel}</small>
              </div>
              <div className="data-panel-export-compare-meta">
                {exportRestorePreflightStatus.metaLabels.map((label) => (
                  <span key={label}>{label}</span>
                ))}
              </div>
              {exportRestorePreflightStatus.warningRows.length > 0 ? (
                <div className="data-panel-export-compare-diffs">
                  {exportRestorePreflightStatus.warningRows.map((warning) => (
                    <span key={warning}>{warning}</span>
                  ))}
                </div>
              ) : null}
              {exportRestoreActionDisplay ? (
                <div
                  className={`data-panel-export-restore-actions ${exportRestoreActionDisplay.tone}`}
                >
                  <button
                    type="button"
                    disabled={exportRestoreActionDisplay.disabled}
                    onClick={() => {
                      if (exportRestoreActionDisplay.disabled) {
                        return;
                      }
                      if (exportRestoreActionDisplay.requiresSecondClick) {
                        setRestoreConfirmPackageId(exportRestoreActionDisplay.packageId);
                        return;
                      }
                      setRestoreConfirmPackageId(null);
                      onRuntimeExportRestore?.(exportRestoreActionDisplay.packageId);
                    }}
                  >
                    {exportRestoreActionDisplay.buttonLabel}
                  </button>
                  <small>{exportRestoreActionDisplay.detailLabel}</small>
                </div>
              ) : null}
            </div>
          ) : null}
          <div
            className="data-panel-export-catalog-table"
            role="table"
            aria-label="后端持久化复盘包目录"
          >
            <div className="data-panel-export-catalog-row header" role="row">
              <span>类型</span>
              <span>包 ID</span>
              <span>仿真时间</span>
              <span>事件数</span>
              <span>归档</span>
              <span>哈希</span>
              <span>操作</span>
            </div>
            {exportCatalogDisplay.rows.length > 0 ? (
              exportCatalogDisplay.rows.map((row) => (
                <div className="data-panel-export-catalog-row" role="row" key={row.key}>
                  <span>{row.typeLabel}</span>
                  <span title={row.packageId}>{row.packageId}</span>
                  <span>{row.simTimeLabel}</span>
                  <span>{row.eventCountLabel}</span>
                  <span title={row.archiveLabel}>{row.archiveLabel}</span>
                  <span title={row.hashLabel}>{row.hashLabel}</span>
                  <span className="data-panel-export-catalog-actions">
                    <a href={row.recordHref}>记录</a>
                    <a href={row.manifestHref} download>
                      清单
                    </a>
                    <a href={row.reviewSummaryHref}>审阅</a>
                    {row.archiveHref ? (
                      <a href={row.archiveHref} download>
                        归档
                      </a>
                    ) : (
                      <em>无归档</em>
                    )}
                    <button
                      type="button"
                      className={
                        row.packageId === runtimeExportComparePackageId ? "selected" : ""
                      }
                      onClick={() => onRuntimeExportCompareSelect?.(row.packageId)}
                    >
                      对比
                    </button>
                    <a href={row.compareHref}>JSON</a>
                    <a href={row.restorePreflightHref}>预检</a>
                  </span>
                </div>
              ))
            ) : (
              <div className="data-panel-export-catalog-empty" role="row">
                后端 catalog 已连接，暂无已登记复盘包
              </div>
            )}
          </div>
        </section>
      ) : null}

      <div className="data-panel-section-title">核心运行指标</div>
      <div className="data-panel-summary">
        <KpiPanel
          label="仿真时间"
          value={`${summary.simTime.toFixed(1)} s`}
          detail={`${summary.eventCount} 个事件`}
        />
        <KpiPanel
          label="事件速率"
          value={`${summary.eventRate.toFixed(1)}/s`}
          detail="离散事件推进"
        />
        <KpiPanel
          label="卫星 / 用户"
          value={`${summary.satelliteCount} / ${summary.groundUserCount}`}
          detail="轨道与接入对象"
        />
        <KpiPanel
          label="活动链路"
          value={String(summary.activeLinks)}
          detail={`${summary.spaceLinks} 星间 / ${summary.accessLinks} 接入`}
        />
        <KpiPanel
          label="可用路由"
          value={`${summary.availableRoutes}/${summary.totalRoutes}`}
          detail={`${summary.routeAvailabilityPercent}% 可达`}
        />
        <KpiPanel
          label="平均路径"
          value={`${summary.averageRouteHops.toFixed(1)} 跳`}
          detail={`${summary.averageRouteLatency.toFixed(3)} s / ${summary.averageRouteCapacity.toFixed(1)} Mbps`}
        />
        <KpiPanel
          label="算力任务"
          value={`${summary.runningTasks} 运行`}
          detail={`${summary.finishedTasks} 完成 / ${summary.deadlineMissedTasks} 超期`}
        />
        <KpiPanel
          label="耦合健康"
          value={`${summary.couplingHealth}%`}
          detail={`${summary.networkWaiting} 个任务等待网络`}
        />
      </div>

      <div className="data-panel-section-title">动态态势曲线</div>
      <div className="data-panel-chart-grid">
        <section
          className="dashboard-section data-panel-chart wide"
          aria-label="全网平均吞吐量时延丢包率抖动"
        >
          <div className="section-title">全网平均指标</div>
          <div className="data-panel-source-note">
            <span>{networkKpiSource.sourceLabel}</span>
            <small>{networkKpiSource.modelNote}</small>
          </div>
          {networkKpiProvenanceItems.length > 0 ? (
            <div className="data-panel-kpi-provenance" aria-label="网络KPI曲线来源">
              {networkKpiProvenanceItems.map((item) => (
                <span key={item.label} title={item.title}>
                  {item.label} <strong>{item.value}</strong>
                </span>
              ))}
            </div>
          ) : null}
          {networkKpiCredibilityDisplay ? (
            <div
              className={`data-panel-kpi-credibility ${networkKpiCredibilityDisplay.tone}`}
              aria-label="网络KPI可信度摘要"
            >
              <div>
                <span>后端可信度</span>
                <strong>{networkKpiCredibilityDisplay.statusLabel}</strong>
                <small>{networkKpiCredibilityDisplay.summaryLabel}</small>
              </div>
              <div className="data-panel-kpi-credibility-meta">
                {networkKpiCredibilityDisplay.metaLabels.map((label) => (
                  <span key={label}>{label}</span>
                ))}
              </div>
              {networkKpiCredibilityDisplay.caveats.length > 0 ? (
                <div className="data-panel-kpi-credibility-caveats">
                  {networkKpiCredibilityDisplay.caveats.map((caveat) => (
                    <span key={caveat}>{caveat}</span>
                  ))}
                </div>
              ) : null}
            </div>
          ) : null}
          {networkKpiBenchmarkValidationDisplay ? (
            <div
              className={`data-panel-kpi-credibility ${networkKpiBenchmarkValidationDisplay.tone}`}
              aria-label="网络KPI基准验证"
            >
              <div>
                <span>基准验证</span>
                <strong>{networkKpiBenchmarkValidationDisplay.statusLabel}</strong>
                <small>{networkKpiBenchmarkValidationDisplay.summaryLabel}</small>
              </div>
              <div className="data-panel-kpi-credibility-meta">
                {networkKpiBenchmarkValidationDisplay.metaLabels.map((label) => (
                  <span key={label}>{label}</span>
                ))}
              </div>
              {networkKpiBenchmarkValidationDisplay.issueLabels.length > 0 ? (
                <div className="data-panel-kpi-credibility-caveats">
                  {networkKpiBenchmarkValidationDisplay.issueLabels.map((label) => (
                    <span key={label}>{label}</span>
                  ))}
                </div>
              ) : null}
            </div>
          ) : null}
          {networkKpiFormulaInspector ? (
            <div
              className={`data-panel-kpi-formula-inspector ${networkKpiFormulaInspector.tone}`}
              aria-label="网络KPI公式检查器"
            >
              <div className="data-panel-kpi-formula-header">
                <div>
                  <span>{networkKpiFormulaInspector.sourceLabel}</span>
                  <strong>{networkKpiFormulaInspector.statusLabel}</strong>
                  <small>{networkKpiFormulaInspector.summaryLabel}</small>
                </div>
              </div>
              <div className="data-panel-kpi-formula-meta">
                {networkKpiFormulaInspector.metaLabels.map((label) => (
                  <span key={label}>{label}</span>
                ))}
              </div>
              <div className="data-panel-kpi-formula-rows">
                {networkKpiFormulaInspector.rows.map((row) => (
                  <span className={row.tone} key={row.metric} title={row.title}>
                    <strong>{row.displayName}</strong>
                    <em>{row.valueLabel}</em>
                    <small>{row.layerLabel}</small>
                    <small>{row.sourceLabel}</small>
                    <small>{row.formulaLabel}</small>
                    <small>{row.sourceFieldsLabel}</small>
                    {row.formulaInputsLabel ? (
                      <small>{row.formulaInputsLabel}</small>
                    ) : null}
                    {row.formulaTraceLabel ? <small>{row.formulaTraceLabel}</small> : null}
                    {row.zeroReasonLabel ? <small>{row.zeroReasonLabel}</small> : null}
                  </span>
                ))}
              </div>
            </div>
          ) : null}
          {networkKpiSource.caveats.length > 0 ? (
            <div className="data-panel-kpi-caveats" aria-label="网络KPI语义说明">
              {networkKpiSource.caveats.map((caveat) => (
                <span key={caveat}>{caveat}</span>
              ))}
            </div>
          ) : null}
          {networkFormulaInputs.length > 0 ? (
            <div className="data-panel-formula-inputs" aria-label="网络KPI公式输入">
              {networkFormulaInputs.map((input) => (
                <span key={input.label}>
                  {input.label} <strong>{input.value}</strong>
                </span>
              ))}
            </div>
          ) : null}
          {networkComponentTail.length > 0 ? (
            <div className="data-panel-formula-inputs" aria-label="网络KPI时间序列分解尾点">
              {networkComponentTail.map((input) => (
                <span key={input.label}>
                  {input.label} <strong>{input.value}</strong>
                </span>
              ))}
            </div>
          ) : null}
          <div className="data-panel-chart-kpis">
            <KpiPanel
              label="吞吐量"
              value={`${latestTelemetry.throughputMbps.toFixed(1)} Mbps`}
            />
            <KpiPanel label="时延" value={`${latestTelemetry.latencyMs.toFixed(2)} ms`} />
            <KpiPanel
              label="丢包率"
              value={`${latestTelemetry.lossPercent.toFixed(2)}%`}
            />
            <KpiPanel label="抖动" value={`${latestTelemetry.jitterMs.toFixed(2)} ms`} />
          </div>
          <div className="data-panel-chart-body">
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={telemetry}>
                <XAxis dataKey="timeLabel" minTickGap={18} />
                <YAxis yAxisId="network" width={42} />
                <YAxis yAxisId="quality" orientation="right" width={42} />
                <Tooltip />
                <Line
                  yAxisId="network"
                  type="monotone"
                  dataKey="throughputMbps"
                  name="吞吐量 Mbps"
                  stroke="#4fd37a"
                  strokeWidth={2}
                  dot={false}
                />
                <Line
                  yAxisId="network"
                  type="monotone"
                  dataKey="latencyMs"
                  name="时延 ms"
                  stroke="#56a6ff"
                  strokeWidth={2}
                  dot={false}
                />
                <Line
                  yAxisId="quality"
                  type="monotone"
                  dataKey="lossPercent"
                  name="丢包率 %"
                  stroke="#f2bd45"
                  strokeWidth={2}
                  dot={false}
                />
                <Line
                  yAxisId="quality"
                  type="monotone"
                  dataKey="jitterMs"
                  name="抖动 ms"
                  stroke="#ef6f6c"
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <RouteConstraintTable rows={routeConstraints} />
          <RouteExplanationTable
            rows={filteredRouteExplanations}
            page={routeExplanationSummary}
            control={runtimeDetailCursorControls?.routes}
            selectedRouteId={selectedRouteDetailRow?.routeId ?? null}
            cursorFilters={{
              query: routeExplanationFilter,
              availability: routeExplanationAvailabilityFilter,
              businessType: routeExplanationBusinessFilter,
              bottleneckComponent: routeExplanationBottleneckFilter
            }}
            filterValue={routeExplanationFilter}
            onFilterChange={(value) => {
              setRouteExplanationFilter(value);
              setSelectedRouteDetailId(null);
              onRuntimeRouteDetailSelect?.(null);
            }}
            availabilityFilter={routeExplanationAvailabilityFilter}
            onAvailabilityFilterChange={(value) => {
              setRouteExplanationAvailabilityFilter(value);
              setSelectedRouteDetailId(null);
              onRuntimeRouteDetailSelect?.(null);
            }}
            businessFilter={routeExplanationBusinessFilter}
            onBusinessFilterChange={(value) => {
              setRouteExplanationBusinessFilter(value);
              setSelectedRouteDetailId(null);
              onRuntimeRouteDetailSelect?.(null);
            }}
            bottleneckFilter={routeExplanationBottleneckFilter}
            onBottleneckFilterChange={(value) => {
              setRouteExplanationBottleneckFilter(value);
              setSelectedRouteDetailId(null);
              onRuntimeRouteDetailSelect?.(null);
            }}
            onSelect={(row) => {
              setSelectedRouteDetailId(row.routeId);
              onRuntimeRouteDetailSelect?.(row.routeId);
            }}
          />
          <ExactDetailInspectorGrid items={[displayedRouteDetailInspector]} />
        </section>

        <section className="dashboard-section data-panel-chart" aria-label="算力资源消耗曲线">
          <div className="section-title">算力资源消耗</div>
          <div className="data-panel-source-note">
            <span>曲线指标 {computeSeries.label}</span>
            <small>{computePoolModeNote}</small>
          </div>
          <div className="data-panel-series-selector" role="group" aria-label="算力曲线指标">
            {COMPUTE_SERIES_OPTIONS.map((option) => (
              <button
                type="button"
                className={computeSeriesKey === option.key ? "active" : ""}
                aria-pressed={computeSeriesKey === option.key}
                key={option.key}
                onClick={() => setComputeSeriesKey(option.key)}
              >
                {option.shortLabel}
              </button>
            ))}
          </div>
          {computeVectorTail.length > 0 ? (
            <div className="data-panel-resource-vector" aria-label="算力资源时序尾点">
              {computeVectorTail.map((item) => (
                <span key={item.label}>
                  {item.label} {item.value}
                </span>
              ))}
            </div>
          ) : null}
          {computeBottleneck ? (
            <div className="data-panel-compute-bottleneck" aria-label="算力资源瓶颈摘要">
              <span>瓶颈 {computeBottleneck.label}</span>
              <strong>{computeBottleneck.utilizationLabel}</strong>
              <small>
                {computeBottleneck.statusLabel} / {computeBottleneck.detailLabel}
              </small>
            </div>
          ) : null}
          <div className="data-panel-chart-kpis compact">
            <KpiPanel
              label="已消耗"
              value={formatComputeSeriesValue(latestComputeValue, computeSeries.unit)}
            />
            <KpiPanel
              label="资源池"
              value={`${computePool.totalTflops.toFixed(1)} TFLOPS`}
              detail={`FP32 主容量 / ${computePool.usedPercent.toFixed(1)}%`}
            />
          </div>
          <div className="data-panel-chart-body compact">
            <ResponsiveContainer width="100%" height={160}>
              <AreaChart data={telemetry}>
                <XAxis dataKey="timeLabel" hide />
                <YAxis width={38} />
                <Tooltip />
                <Area
                  type="monotone"
                  dataKey={computeSeriesKey}
                  name={`${computeSeries.label} ${computeSeries.unit}`}
                  stroke="#f2bd45"
                  fill="#f2bd4540"
                  strokeWidth={2}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </section>

        <section className="dashboard-section data-panel-chart" aria-label="算力资源池消耗饼图">
          <div className="section-title">算力资源向量池</div>
          <div className="data-panel-source-note">
            <span>饼图 FP32</span>
            <small>下方同步展示 FP64、GPU FP32/FP16、NPU INT8、内存和存储。</small>
          </div>
          <div className="data-panel-chart-kpis compact">
            <KpiPanel
              label="可用"
              value={`${computePool.availableTflops.toFixed(1)} TFLOPS`}
            />
            <KpiPanel label="消耗率" value={`${computePool.usedPercent.toFixed(1)}%`} />
          </div>
          <div className="data-panel-resource-vector">
            <span>
              GPU FP32 {computePool.vectorSummary.usedGpuFp32Tflops.toFixed(1)} /{" "}
              {computePool.vectorSummary.gpuFp32Tflops.toFixed(1)} TFLOPS
            </span>
            <span>
              GPU FP16 {computePool.vectorSummary.usedGpuFp16Tflops.toFixed(1)} /{" "}
              {computePool.vectorSummary.gpuFp16Tflops.toFixed(1)} TFLOPS
            </span>
            <span>
              NPU INT8 {computePool.vectorSummary.usedNpuInt8Tops.toFixed(1)} /{" "}
              {computePool.vectorSummary.npuInt8Tops.toFixed(1)} TOPS
            </span>
            <span>
              内存 {computePool.vectorSummary.usedMemoryGb.toFixed(1)} /{" "}
              {computePool.vectorSummary.memoryGb.toFixed(1)} GB · 存储{" "}
              {computePool.vectorSummary.usedStorageGb.toFixed(1)} /{" "}
              {computePool.vectorSummary.storageGb.toFixed(1)} GB
            </span>
          </div>
          {serviceLatency.items.length > 0 ? (
            <>
              <div className="data-panel-source-note">
                <span>{serviceLatency.sourceLabel}</span>
                <small>
                  {serviceLatency.modelLabel} / {serviceLatency.taskCountLabel} /{" "}
                  {serviceLatency.completeCountLabel}
                </small>
              </div>
              <div className="data-panel-formula-inputs" aria-label="通信计算服务延迟组件">
                <span>
                  总延迟 <strong>{serviceLatency.totalLatencyLabel}</strong>
                </span>
                {serviceLatency.items.map((item) => (
                  <span key={item.label}>
                    {item.label} <strong>{item.value}</strong>
                  </span>
                ))}
              </div>
              {computeTaskTimeline.items.length > 0 ? (
                <>
                  <div className="data-panel-source-note">
                    <span>{computeTaskTimeline.sourceLabel}</span>
                    <small>{computeTaskTimeline.summaryLabel}</small>
                  </div>
                  <div className="data-panel-formula-inputs" aria-label="计算任务队列执行摘要">
                    <span>
                      排队任务 <strong>{computeTaskTimeline.queuedTaskLabel}</strong>
                    </span>
                    <span>
                      排队总量 <strong>{computeTaskTimeline.totalQueueDelayLabel}</strong>
                    </span>
                    <span>
                      执行总量 <strong>{computeTaskTimeline.totalExecutionDelayLabel}</strong>
                    </span>
                  </div>
                  <div className="data-panel-service-timeline" aria-label="计算任务队列执行时间线">
                    {computeTaskTimeline.items.map((item) => (
                      <span
                        className="data-panel-service-segment"
                        key={item.taskId}
                        title={item.traceTitle}
                      >
                        <small>{item.taskLabel}</small>
                        <strong>{item.queueExecutionLabel}</strong>
                        <em>{item.nodeLabel}</em>
                      </span>
                    ))}
                  </div>
                </>
              ) : null}
              {serviceLatencyRows.length > 0 ? (
                <div className="data-panel-formula-inputs" aria-label="通信计算服务轨迹">
                  {serviceLatencyRows.map((row) => (
                    <span key={row.taskId} title={row.traceTitle}>
                      {row.taskLabel} <strong>{row.totalLatencyLabel}</strong>{" "}
                      {row.statusLabel}
                      {row.placementLabel !== "无计算放置" ? ` / ${row.placementLabel}` : ""}
                    </span>
                  ))}
                </div>
              ) : null}
              {serviceLatencyRows.some((row) => row.timeline.length > 0) ? (
                <div className="data-panel-service-timeline" aria-label="服务阶段时间线">
                  {serviceLatencyRows.map((row) =>
                    row.timeline.map((segment) => (
                      <span
                        key={`${row.taskId}:${segment.component}`}
                        className="data-panel-service-segment"
                        title={segment.traceTitle}
                      >
                        <small>{segment.label}</small>
                        <strong>{segment.durationLabel}</strong>
                        <em>{segment.timeLabel}</em>
                      </span>
                    ))
                  )}
                </div>
              ) : null}
            </>
          ) : null}
          <ServiceDetailPageTable
            rows={serviceDetailRows}
            page={serviceDetailPage}
            control={runtimeDetailCursorControls?.services}
            selectedServiceId={selectedServiceDetailRow?.serviceId ?? null}
            filterValue={serviceDetailFilter}
            onFilterChange={(value) => {
              setServiceDetailFilter(value);
              setSelectedServiceDetailId(null);
              setSelectedServiceTraceId(null);
              onRuntimeServiceDetailSelect?.(null);
              onRuntimeServiceTraceDetailSelect?.(null);
            }}
            onSelect={(row) => {
              setSelectedServiceDetailId(row.serviceId);
              setSelectedServiceTraceId(null);
              onRuntimeServiceDetailSelect?.(row.serviceId);
              onRuntimeServiceTraceDetailSelect?.(null);
            }}
          />
          <ServiceTraceFilterControls
            filterValue={serviceTraceFilter}
            terminalFilter={serviceTraceTerminalFilter}
            computeNodeFilter={serviceTraceComputeNodeFilter}
            stageFilter={serviceTraceStageFilter}
            terminalReasonFilter={serviceTraceTerminalReasonFilter}
            onFilterChange={(value) => {
              setServiceTraceFilter(value);
              setSelectedServiceTraceId(null);
              onRuntimeServiceTraceDetailSelect?.(null);
              runtimeDetailCursorControls?.serviceTraces?.onCursorChange?.(
                0,
                serviceTraceDetailCursorFilters(
                  value,
                  serviceTraceTerminalFilter,
                  serviceTraceComputeNodeFilter,
                  serviceTraceStageFilter,
                  serviceTraceTerminalReasonFilter
                )
              );
            }}
            onTerminalFilterChange={(value) => {
              setServiceTraceTerminalFilter(value);
              setSelectedServiceTraceId(null);
              onRuntimeServiceTraceDetailSelect?.(null);
              runtimeDetailCursorControls?.serviceTraces?.onCursorChange?.(
                0,
                serviceTraceDetailCursorFilters(
                  serviceTraceFilter,
                  value,
                  serviceTraceComputeNodeFilter,
                  serviceTraceStageFilter,
                  serviceTraceTerminalReasonFilter
                )
              );
            }}
            onComputeNodeFilterChange={(value) => {
              setServiceTraceComputeNodeFilter(value);
              setSelectedServiceTraceId(null);
              onRuntimeServiceTraceDetailSelect?.(null);
              runtimeDetailCursorControls?.serviceTraces?.onCursorChange?.(
                0,
                serviceTraceDetailCursorFilters(
                  serviceTraceFilter,
                  serviceTraceTerminalFilter,
                  value,
                  serviceTraceStageFilter,
                  serviceTraceTerminalReasonFilter
                )
              );
            }}
            onStageFilterChange={(value) => {
              setServiceTraceStageFilter(value);
              setSelectedServiceTraceId(null);
              onRuntimeServiceTraceDetailSelect?.(null);
              runtimeDetailCursorControls?.serviceTraces?.onCursorChange?.(
                0,
                serviceTraceDetailCursorFilters(
                  serviceTraceFilter,
                  serviceTraceTerminalFilter,
                  serviceTraceComputeNodeFilter,
                  value,
                  serviceTraceTerminalReasonFilter
                )
              );
            }}
            onTerminalReasonFilterChange={(value) => {
              setServiceTraceTerminalReasonFilter(value);
              setSelectedServiceTraceId(null);
              onRuntimeServiceTraceDetailSelect?.(null);
              runtimeDetailCursorControls?.serviceTraces?.onCursorChange?.(
                0,
                serviceTraceDetailCursorFilters(
                  serviceTraceFilter,
                  serviceTraceTerminalFilter,
                  serviceTraceComputeNodeFilter,
                  serviceTraceStageFilter,
                  value
                )
              );
            }}
          />
          <BackendCursorPager
            label="服务 trace"
            page={serviceTracePage}
            totalCount={serviceTracePage?.service_count ?? 0}
            control={runtimeDetailCursorControls?.serviceTraces}
            filters={serviceTraceCursorFilters}
          />
          <ServiceLifecycleTracePanel
            display={filteredServiceLifecycleTraceDisplay}
            selectedTraceId={selectedServiceTraceRow?.traceId ?? null}
            onSelect={(row) => {
              setSelectedServiceTraceId(row.traceId);
              setSelectedServiceDetailId(row.serviceId);
              onRuntimeServiceTraceDetailSelect?.(row.traceId);
              onRuntimeServiceDetailSelect?.(row.serviceId);
              if (row.primaryRouteId) {
                setSelectedRouteDetailId(row.primaryRouteId);
                onRuntimeRouteDetailSelect?.(row.primaryRouteId);
              }
              if (row.computeNodeId) {
                setSelectedComputeNodeDetailId(row.computeNodeId);
                onRuntimeComputeNodeDetailSelect?.(row.computeNodeId);
                if (row.computeNodeId.startsWith("sat-")) {
                  setSelectedDetailSatelliteId(row.computeNodeId);
                  onRuntimeSatelliteDetailSelect?.(row.computeNodeId);
                }
              }
            }}
          />
          <TopComputeNodeTable rows={topComputeNodes} />
          <ComputeNodeDetailPageTable
            rows={computeNodeDetailRows}
            page={computeNodeDetailPage}
            control={runtimeDetailCursorControls?.computeNodes}
            selectedNodeId={selectedComputeNodeDetailRow?.nodeId ?? null}
            filterValue={computeNodeDetailFilter}
            onFilterChange={(value) => {
              setComputeNodeDetailFilter(value);
              setSelectedComputeNodeDetailId(null);
              onRuntimeComputeNodeDetailSelect?.(null);
            }}
            onSelect={(row) => {
              setSelectedComputeNodeDetailId(row.nodeId);
              onRuntimeComputeNodeDetailSelect?.(row.nodeId);
            }}
          />
          <ExactDetailInspectorGrid
            items={[
              displayedServiceDetailInspector,
              displayedServiceTraceCorrelationInspector,
              displayedComputeNodeDetailInspector
            ]}
          />
          <div className="data-panel-chart-body compact">
            {computePool.totalTflops > 0 ? (
              <ResponsiveContainer width="100%" height={160}>
                <PieChart>
                  <Pie
                    data={computePool.slices}
                    dataKey="value"
                    nameKey="name"
                    innerRadius={38}
                    outerRadius={62}
                  >
                    {computePool.slices.map((slice) => (
                      <Cell key={slice.name} fill={slice.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="data-panel-empty-chart">等待算力快照</div>
            )}
          </div>
        </section>

        <section className="dashboard-section data-panel-chart" aria-label="用户业务历史曲线">
          <div className="section-title">用户业务历史</div>
          <div className="data-panel-source-note">
            <span>{userRequestHistory.sourceLabel}</span>
            <small>{userRequestHistory.summaryLabel}</small>
          </div>
          <div className="data-panel-history-selector">
            <label htmlFor="data-panel-history-user">用户</label>
            <select
              id="data-panel-history-user"
              value={userRequestHistory.selectedUserId ?? ""}
              disabled={userRequestHistory.availableUserIds.length === 0}
              onChange={(event) => setSelectedHistoryUserId(event.currentTarget.value)}
            >
              {userRequestHistory.availableUserIds.length === 0 ? (
                <option value="">等待后端历史</option>
              ) : (
                userRequestHistory.availableUserIds.map((userId) => (
                  <option key={userId} value={userId}>
                    {userId}
                  </option>
                ))
              )}
            </select>
          </div>
          {latestUserRequestHistoryPoint !== undefined ? (
            <div className="data-panel-chart-kpis compact">
              <KpiPanel
                label="可用路由"
                value={`${latestUserRequestHistoryPoint.availableRouteCount}/${latestUserRequestHistoryPoint.communicationRouteCount}`}
              />
              <KpiPanel
                label="时延"
                value={`${latestUserRequestHistoryPoint.latencyMs.toFixed(2)} ms`}
              />
            </div>
          ) : null}
          {latestUserRequestHistoryPoint !== undefined ? (
            <div className="data-panel-resource-vector">
              <span>目标 {latestUserRequestHistoryPoint.selectedSatelliteId}</span>
              <span>流 {latestUserRequestHistoryPoint.primaryFlowId}</span>
              <span>队列 {latestUserRequestHistoryPoint.networkQueueCount}</span>
              <span>丢包代理 {latestUserRequestHistoryPoint.lossPercent.toFixed(2)}%</span>
            </div>
          ) : null}
          <div className="data-panel-chart-body compact">
            {userRequestHistory.points.length > 0 ? (
              <ResponsiveContainer width="100%" height={160}>
                <LineChart data={userRequestHistory.points}>
                  <XAxis dataKey="timeLabel" hide />
                  <YAxis yAxisId="route" width={38} />
                  <YAxis yAxisId="latency" orientation="right" width={42} />
                  <Tooltip />
                  <Line
                    yAxisId="route"
                    type="monotone"
                    dataKey="availableRouteCount"
                    name="可用路由"
                    stroke="#4fd37a"
                    strokeWidth={2}
                    dot={false}
                  />
                  <Line
                    yAxisId="route"
                    type="monotone"
                    dataKey="networkQueueCount"
                    name="网络队列"
                    stroke="#ef6f6c"
                    strokeWidth={2}
                    dot={false}
                  />
                  <Line
                    yAxisId="latency"
                    type="monotone"
                    dataKey="latencyMs"
                    name="时延 ms"
                    stroke="#56a6ff"
                    strokeWidth={2}
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="data-panel-empty-chart">等待后端用户业务历史</div>
            )}
          </div>
        </section>

        <section className="dashboard-section data-panel-chart" aria-label="单星资源历史曲线">
          <div className="section-title">单星资源历史</div>
          <div className="data-panel-source-note">
            <span>{satelliteResourceHistory.sourceLabel}</span>
            <small>{satelliteResourceHistory.summaryLabel}</small>
          </div>
          <div className="data-panel-history-selector">
            <label htmlFor="data-panel-history-satellite">卫星</label>
            <select
              id="data-panel-history-satellite"
              value={satelliteResourceHistory.selectedSatelliteId ?? ""}
              disabled={satelliteResourceHistory.availableSatelliteIds.length === 0}
              onChange={(event) => setSelectedHistorySatelliteId(event.currentTarget.value)}
            >
              {satelliteResourceHistory.availableSatelliteIds.length === 0 ? (
                <option value="">等待后端历史</option>
              ) : (
                satelliteResourceHistory.availableSatelliteIds.map((satelliteId) => (
                  <option key={satelliteId} value={satelliteId}>
                    {satelliteId}
                  </option>
                ))
              )}
            </select>
          </div>
          {latestSatelliteResourceHistoryPoint !== undefined ? (
            <div className="data-panel-chart-kpis compact">
              <KpiPanel
                label="负载"
                value={`${latestSatelliteResourceHistoryPoint.loadPercent.toFixed(1)}%`}
              />
              <KpiPanel
                label="FP32"
                value={`${latestSatelliteResourceHistoryPoint.usedFp32Gflops.toFixed(
                  1
                )} GFLOPS`}
              />
            </div>
          ) : null}
          {latestSatelliteResourceHistoryPoint !== undefined ? (
            <div className="data-panel-resource-vector">
              <span>
                内存 {latestSatelliteResourceHistoryPoint.usedMemoryGb.toFixed(1)} GB
              </span>
              <span>
                存储 {latestSatelliteResourceHistoryPoint.usedStorageGb.toFixed(1)} GB
              </span>
              <span>
                GPU FP32{" "}
                {latestSatelliteResourceHistoryPoint.usedGpuFp32Tflops.toFixed(2)} TFLOPS
              </span>
              <span>
                NPU INT8 {latestSatelliteResourceHistoryPoint.usedNpuInt8Tops.toFixed(1)} TOPS
              </span>
            </div>
          ) : null}
          <div className="data-panel-chart-body compact">
            {satelliteResourceHistory.points.length > 0 ? (
              <ResponsiveContainer width="100%" height={160}>
                <LineChart data={satelliteResourceHistory.points}>
                  <XAxis dataKey="timeLabel" hide />
                  <YAxis yAxisId="load" width={38} />
                  <YAxis yAxisId="resource" orientation="right" width={42} />
                  <Tooltip />
                  <Line
                    yAxisId="load"
                    type="monotone"
                    dataKey="loadPercent"
                    name="负载 %"
                    stroke="#56a6ff"
                    strokeWidth={2}
                    dot={false}
                  />
                  <Line
                    yAxisId="resource"
                    type="monotone"
                    dataKey="usedFp32Gflops"
                    name="CPU FP32 GFLOPS"
                    stroke="#f2bd45"
                    strokeWidth={2}
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="data-panel-empty-chart">等待后端单星资源历史</div>
            )}
          </div>
        </section>
      </div>

      <div className="data-panel-section-title">用户节点与卫星运行明细</div>
      <div className="data-panel-detail-toolbar">
        <label htmlFor="data-panel-detail-filter">节点筛选</label>
        <input
          id="data-panel-detail-filter"
          type="search"
          value={detailFilter}
          placeholder="user-0 / sat-0 / compute"
          onChange={(event) => {
            setDetailFilter(event.currentTarget.value);
            setUserDetailPage(0);
            setSatelliteDetailPage(0);
            setSelectedDetailUserId(null);
            setSelectedDetailSatelliteId(null);
            onRuntimeUserDetailSelect?.(null);
            onRuntimeSatelliteDetailSelect?.(null);
          }}
        />
        <span>
          {filteredUserBusinessRequests.items.length} 个用户 /{" "}
          {filteredSatelliteResourceRows.items.length} 个卫星
        </span>
      </div>
      <div className="data-panel-observability-notes" aria-label="明细观测范围说明">
        {detailScopeNotes.map((note) => (
          <div className={`data-panel-observability-note ${note.tone}`} key={note.label}>
            <span>{note.label}</span>
            <strong>{note.value}</strong>
            <small>{note.detail}</small>
          </div>
        ))}
      </div>
      <DetailInspectorGrid
        user={displayedUserDetailInspector}
        satellite={displayedSatelliteDetailInspector}
      />
      <DetailInspectorDrawer items={nodeDetailDrawerItems} />
      <div className="data-panel-detail-grid">
        <section className="dashboard-section data-panel-detail-table" aria-label="用户节点状态明细">
          <div className="section-title">用户节点状态</div>
          <div className="data-panel-source-note">
            <div className="data-panel-source-main">
              <span>{userBusinessRequests.sourceLabel}</span>
              <span
                className={`data-panel-source-badge ${userSourceBadge.tone}`}
                title={userSourceBadge.title}
              >
                {userSourceBadge.label}
              </span>
            </div>
            <small>{userBusinessRequests.summaryLabel}</small>
          </div>
          <BackendCursorPager
            label="用户后端页"
            page={userRequestSummary}
            totalCount={userRequestSummary?.user_count ?? filteredUserBusinessRequests.items.length}
            control={runtimeDetailCursorControls?.users}
            filters={detailFilter ? { query: detailFilter } : undefined}
          />
          <DetailPaginationControls
            page={userDetailWindow}
            label="用户明细"
            windowNote={userDetailWindowNote}
            onPrevious={() => setUserDetailPage(Math.max(0, userDetailWindow.pageIndex - 1))}
            onNext={() => setUserDetailPage(userDetailWindow.pageIndex + 1)}
          />
          <UserBusinessRequestTable
            rows={userDetailWindow.items}
            selectedUserId={selectedUserDetailRow?.userId ?? null}
            onSelect={(row) => {
              setSelectedDetailUserId(row.userId);
              onRuntimeUserDetailSelect?.(row.userId);
            }}
          />
        </section>
        <section className="dashboard-section data-panel-detail-table" aria-label="卫星资源消耗明细">
          <div className="section-title">卫星资源消耗</div>
          <div className="data-panel-source-note">
            <div className="data-panel-source-main">
              <span>{satelliteResourceRows.sourceLabel}</span>
              <span
                className={`data-panel-source-badge ${satelliteSourceBadge.tone}`}
                title={satelliteSourceBadge.title}
              >
                {satelliteSourceBadge.label}
              </span>
            </div>
            <small>{satelliteResourceRows.summaryLabel}</small>
          </div>
          <BackendCursorPager
            label="卫星后端页"
            page={satelliteServiceSummary}
            totalCount={
              satelliteServiceSummary?.satellite_count ??
              filteredSatelliteResourceRows.items.length
            }
            control={runtimeDetailCursorControls?.satellites}
            filters={detailFilter ? { query: detailFilter } : undefined}
          />
          <DetailPaginationControls
            page={satelliteDetailWindow}
            label="卫星明细"
            windowNote={satelliteDetailWindowNote}
            onPrevious={() =>
              setSatelliteDetailPage(Math.max(0, satelliteDetailWindow.pageIndex - 1))
            }
            onNext={() => setSatelliteDetailPage(satelliteDetailWindow.pageIndex + 1)}
          />
          <SatelliteResourceTable
            rows={satelliteDetailWindow.items}
            selectedSatelliteId={selectedSatelliteDetailRow?.satelliteId ?? null}
            onSelect={(row) => {
              setSelectedDetailSatelliteId(row.satelliteId);
              onRuntimeSatelliteDetailSelect?.(row.satelliteId);
            }}
          />
        </section>
      </div>

      <div className="data-panel-section-title secondary">辅助模型分析</div>
      <div className="data-panel-grid">
        {informationArchitectureDisplay ? (
          <section
            className="dashboard-section data-panel-configuration-explanation data-panel-information-architecture"
            aria-label="后端数据态势信息架构"
          >
            <div className="section-title">数据态势信息架构</div>
            <div className="data-panel-source-note">
              <span>{informationArchitectureDisplay.sourceLabel}</span>
              <small>{informationArchitectureDisplay.summaryLabel}</small>
            </div>
            <div className="data-panel-config-explanation-meta">
              <span>{informationArchitectureDisplay.policyLabel}</span>
              <span>{informationArchitectureDisplay.layoutLabel}</span>
            </div>
            <div className="data-panel-config-explanation-sections">
              {informationArchitectureDisplay.sections.map((section) => (
                <div
                  className="data-panel-config-explanation-section"
                  key={section.section}
                >
                  <div>
                    <strong>{section.title}</strong>
                    <small>{section.purpose}</small>
                  </div>
                  <span title={section.sourcesLabel}>
                    {section.surfacesLabel}
                  </span>
                </div>
              ))}
            </div>
          </section>
        ) : null}
        {modelAssumptionsDisplay ? (
          <section
            className="dashboard-section data-panel-configuration-explanation data-panel-model-assumptions"
            aria-label="后端模型假设与边界"
          >
            <div className="section-title">模型假设与边界</div>
            <div className="data-panel-source-note">
              <span>{modelAssumptionsDisplay.sourceLabel}</span>
              <small>{modelAssumptionsDisplay.summaryLabel}</small>
            </div>
            <div className="data-panel-config-explanation-meta">
              <span>{modelAssumptionsDisplay.boundaryLabel}</span>
              <span>{modelAssumptionsDisplay.fidelityLabel}</span>
            </div>
            <div className="data-panel-config-explanation-sections">
              {modelAssumptionsDisplay.rows.map((row) => (
                <div
                  className="data-panel-config-explanation-section"
                  key={`${row.kind}:${row.label}`}
                >
                  <div>
                    <strong>{row.label}</strong>
                    <small>{row.detail}</small>
                  </div>
                  <span>{row.source}</span>
                </div>
              ))}
            </div>
          </section>
        ) : null}
        {modelTrustEvidenceWorkspace ? (
          <section
            className={`dashboard-section data-panel-model-trust-evidence ${modelTrustEvidenceWorkspace.tone}`}
            aria-label="模型可信证据工作台"
          >
            <div className="section-title">模型可信证据</div>
            <div className="data-panel-source-note">
              <span>{modelTrustEvidenceWorkspace.sourceLabel}</span>
              <small>{modelTrustEvidenceWorkspace.summaryLabel}</small>
            </div>
            <div className="data-panel-model-trust-headline">
              <strong>{modelTrustEvidenceWorkspace.statusLabel}</strong>
              <span>{modelTrustEvidenceWorkspace.scoreLabel}</span>
            </div>
            <div className="data-panel-model-trust-meta">
              {modelTrustEvidenceWorkspace.metaLabels.map((label) => (
                <span key={label}>{label}</span>
              ))}
            </div>
            <div className="data-panel-model-trust-grid">
              {modelTrustEvidenceWorkspace.rows.map((row) => (
                <span
                  key={`${row.kind}:${row.label}`}
                  className={row.tone}
                  title={row.title}
                >
                  <small>{row.source}</small>
                  <strong>{row.label}</strong>
                  <em>{row.statusLabel}</em>
                  <span>{row.detail}</span>
                </span>
              ))}
            </div>
            {modelTrustEvidenceWorkspace.actionLabels.length > 0 ? (
              <div className="data-panel-model-trust-actions">
                {modelTrustEvidenceWorkspace.actionLabels.map((label) => (
                  <span key={label}>{label}</span>
                ))}
              </div>
            ) : null}
          </section>
        ) : null}
        {configurationExplanationDisplay ? (
          <section
            className="dashboard-section data-panel-configuration-explanation"
            aria-label="后端配置语义解释"
          >
            <div className="section-title">配置语义解释</div>
            <div className="data-panel-source-note">
              <span>{configurationExplanationDisplay.sourceLabel}</span>
              <small>{configurationExplanationDisplay.summaryLabel}</small>
            </div>
            <div className="data-panel-config-explanation-meta">
              <span>{configurationExplanationDisplay.determinismLabel}</span>
              <span>{configurationExplanationDisplay.boundaryLabel}</span>
            </div>
            <div className="data-panel-config-explanation-surfaces">
              {configurationExplanationDisplay.surfaces.map((surface) => (
                <span key={surface.surface} title={surface.purpose}>
                  {surface.label}
                </span>
              ))}
            </div>
            <div className="data-panel-config-explanation-sections">
              {configurationExplanationDisplay.sections.map((section) => (
                <div
                  className="data-panel-config-explanation-section"
                  key={section.section}
                >
                  <div>
                    <strong>{section.title}</strong>
                    <small>{section.currentValueLabel}</small>
                  </div>
                  <span title={section.sourceFieldsLabel}>
                    {section.excludedSemanticsLabel}
                  </span>
                </div>
              ))}
            </div>
          </section>
        ) : null}
        <DomainSummary snapshot={snapshot} />
        <TopologyChangePanel snapshot={snapshot} />
        <LinkProtocolPanel snapshot={snapshot} />
        <CouplingFeedbackPanel snapshot={snapshot} />
        <ChannelHealthPanel snapshot={snapshot} />
        <NetworkView snapshot={snapshot} />
        <ComputeQueuePanel snapshot={snapshot} />
        <ComputeView snapshot={snapshot} />
        <OrbitPanel snapshot={snapshot} />
        <GroundTrackPanel snapshot={snapshot} />
        <SystemHealth snapshot={snapshot} />
      </div>
    </section>
  );
});

export function selectRuntimeUserRequestSummary(
  runtimeStatus: RuntimeStatusPayload,
  runtimeDetailPages: RuntimeDetailPages | null | undefined
): RuntimeUserRequestSummaryV1 | RuntimeUserServiceRequestSummaryV2 | null | undefined {
  return (
    runtimeDetailPages?.users ??
    runtimeStatus.user_service_request_summary_v2 ??
    runtimeStatus.user_request_summary_v1
  );
}

export function selectRuntimeSatelliteServiceSummary(
  runtimeStatus: RuntimeStatusPayload,
  runtimeDetailPages: RuntimeDetailPages | null | undefined
): RuntimeSatelliteServiceSummaryV1 | null | undefined {
  return runtimeDetailPages?.satellites ?? runtimeStatus.satellite_service_summary_v1;
}

export function selectRuntimeNodeDetailSummary(
  runtimeStatus: RuntimeStatusPayload,
  runtimeDetailPages: RuntimeDetailPages | null | undefined
): RuntimeNodeDetailSummaryV1 | null | undefined {
  if (runtimeDetailPages?.nodes !== null && runtimeDetailPages?.nodes !== undefined) {
    return runtimeNodeDetailPageToSummary(runtimeDetailPages.nodes);
  }
  return runtimeStatus.node_detail_summary_v1;
}

export function selectRuntimeRouteExplanationSummary(
  runtimeStatus: RuntimeStatusPayload,
  runtimeDetailPages: RuntimeDetailPages | null | undefined
): RuntimeRouteExplanationSummaryV1 | null | undefined {
  return runtimeDetailPages?.routes ?? runtimeStatus.route_explanation_summary_v1;
}

export function selectRuntimeServiceDetailPage(
  runtimeDetailPages: RuntimeDetailPages | null | undefined
): RuntimeServiceDetailPageV1 | null | undefined {
  return runtimeDetailPages?.services;
}

export function selectRuntimeServiceTracePage(
  runtimeStatus: RuntimeStatusPayload,
  runtimeDetailPages: RuntimeDetailPages | null | undefined
): RuntimeServiceLifecycleTraceV2 | null | undefined {
  return runtimeDetailPages?.serviceTraces ?? runtimeStatus.service_lifecycle_trace_v2;
}

export function selectRuntimeComputeNodeDetailPage(
  runtimeDetailPages: RuntimeDetailPages | null | undefined
): RuntimeComputeNodeDetailPageV1 | null | undefined {
  return runtimeDetailPages?.computeNodes;
}

export function runtimeNodeDetailPageToSummary(
  page: RuntimeNodeDetailPageV1
): RuntimeNodeDetailSummaryV1 {
  const users = page.items.filter(
    (card) => card.entity_type === "USER"
  );
  const satellites = page.items.filter(
    (card) => card.entity_type === "SATELLITE"
  );
  return {
    version: page.version,
    source: page.source,
    summary_scope: page.summary_scope,
    user_detail_count: page.window_user_detail_count ?? users.length,
    satellite_detail_count: page.window_satellite_detail_count ?? satellites.length,
    users,
    satellites
  };
}

type RuntimeDetailWindowKind = "users" | "satellites";

export function buildRuntimeDetailWindowNote(
  summary:
    | RuntimeUserRequestSummaryV1
    | RuntimeSatelliteServiceSummaryV1
    | null
    | undefined,
  kind: RuntimeDetailWindowKind
): string | null {
  if (summary === null || summary === undefined) {
    return null;
  }
  if (typeof summary.cursor !== "number" || typeof summary.item_count !== "number") {
    return null;
  }
  const cursor = Math.max(0, Math.floor(summary.cursor));
  const itemCount = Math.max(0, Math.floor(summary.item_count));
  const totalCount =
    kind === "users"
      ? (summary as RuntimeUserRequestSummaryV1).user_count
      : (summary as RuntimeSatelliteServiceSummaryV1).satellite_count;
  const hiddenCount =
    kind === "users"
      ? (summary as RuntimeUserRequestSummaryV1).hidden_user_count
      : (summary as RuntimeSatelliteServiceSummaryV1).hidden_satellite_count;
  const startIndex = itemCount === 0 ? 0 : cursor + 1;
  const endIndex = cursor + itemCount;
  const windowText = `后端窗口 ${formatCount(startIndex)}-${formatCount(endIndex)} / ${formatCount(
    Math.max(itemCount, totalCount, endIndex)
  )}`;
  if (summary.has_more === true || hiddenCount > 0) {
    return `${windowText}；仍有 ${formatCount(Math.max(0, hiddenCount))} 行可通过游标继续读取`;
  }
  return `${windowText}；当前窗口覆盖全部明细`;
}

function RouteConstraintTable({ rows }: { rows: DataPanelRouteConstraintRows }) {
  if (rows.items.length === 0) {
    return <div className="data-panel-route-empty">等待路由快照</div>;
  }
  return (
    <div className="data-panel-route-table" aria-label="路由KPI约束明细">
      <div className="data-panel-route-source">{rows.sourceLabel}</div>
      <div className="data-panel-route-row header">
        <span>路由</span>
        <span>状态</span>
        <span>跳数</span>
        <span>时延</span>
        <span>容量</span>
        <span>需求/损耗</span>
        <span>瓶颈解释</span>
      </div>
      {rows.items.map((row) => (
        <div className="data-panel-route-row" key={row.routeId} title={row.pathLabel}>
          <span>{row.routeId}</span>
          <span>{row.statusLabel}</span>
          <span>{row.hopCount}</span>
          <span>{row.latencyLabel}</span>
          <span>{row.capacityLabel}</span>
          <span>{row.demandLossLabel}</span>
          <span>{row.bottleneckLabel}</span>
        </div>
      ))}
    </div>
  );
}

function RouteExplanationTable({
  rows,
  page,
  control,
  selectedRouteId,
  cursorFilters,
  filterValue,
  onFilterChange,
  availabilityFilter,
  onAvailabilityFilterChange,
  businessFilter,
  onBusinessFilterChange,
  bottleneckFilter,
  onBottleneckFilterChange,
  onSelect
}: {
  rows: DataPanelRouteExplanationRows;
  page: RuntimeRouteExplanationSummaryV1 | null | undefined;
  control?: RuntimeDetailCursorControl | null;
  selectedRouteId?: string | null;
  cursorFilters?: RuntimeDetailCursorFilters;
  filterValue: string;
  onFilterChange: (value: string) => void;
  availabilityFilter: DataPanelRouteExplanationAvailabilityFilter;
  onAvailabilityFilterChange: (
    value: DataPanelRouteExplanationAvailabilityFilter
  ) => void;
  businessFilter: string;
  onBusinessFilterChange: (value: string) => void;
  bottleneckFilter: string;
  onBottleneckFilterChange: (value: string) => void;
  onSelect?: (row: DataPanelRouteExplanationRow) => void;
}) {
  const controls = (
    <RouteExplanationFilterControls
      filterValue={filterValue}
      onFilterChange={onFilterChange}
      availabilityFilter={availabilityFilter}
      onAvailabilityFilterChange={onAvailabilityFilterChange}
      businessFilter={businessFilter}
      onBusinessFilterChange={onBusinessFilterChange}
      bottleneckFilter={bottleneckFilter}
      onBottleneckFilterChange={onBottleneckFilterChange}
    />
  );
  if (rows.items.length === 0) {
    const emptyLabel = rows.sourceLabel.includes("筛选")
      ? "没有匹配的路由解释"
      : "等待后端路由解释";
    return (
      <div className="data-panel-route-explanations">
        {controls}
        <div className="data-panel-route-source">{rows.sourceLabel}</div>
        <BackendCursorPager
          label="路由后端页"
          page={page}
          totalCount={page?.route_count ?? rows.items.length}
          control={control}
          filters={cursorFilters}
        />
        <div className="data-panel-route-empty">{emptyLabel}</div>
      </div>
    );
  }
  return (
    <div className="data-panel-route-explanations">
      {controls}
      <div className="data-panel-route-table explanations" aria-label="后端路由解释明细">
        <div className="data-panel-route-source">{rows.sourceLabel}</div>
        <BackendCursorPager
          label="路由后端页"
          page={page}
          totalCount={page?.route_count ?? rows.items.length}
          control={control}
          filters={cursorFilters}
        />
        <div className="data-panel-route-row header">
          <span>路由</span>
          <span>业务</span>
          <span>下一跳</span>
          <span>容量/需求</span>
          <span>压力</span>
          <span>瓶颈</span>
          <span>解释</span>
        </div>
        {rows.items.map((row) => (
          <button
            type="button"
            className={`data-panel-route-row ${
              row.routeId === selectedRouteId ? "selected" : ""
            }`}
            key={row.routeId}
            title={row.pathLabel}
            onClick={() => onSelect?.(row)}
          >
            <span>{row.routeId}</span>
            <span>{row.businessLabel}</span>
            <span>{row.nextHopLabel}</span>
            <span>{row.capacityDemandLabel}</span>
            <span>{row.pressureLabel}</span>
            <span>{row.bottleneckLabel}</span>
            <span>{row.explanationLabel}</span>
          </button>
        ))}
      </div>
    </div>
  );
}

function RouteExplanationFilterControls({
  filterValue,
  onFilterChange,
  availabilityFilter,
  onAvailabilityFilterChange,
  businessFilter,
  onBusinessFilterChange,
  bottleneckFilter,
  onBottleneckFilterChange
}: {
  filterValue: string;
  onFilterChange: (value: string) => void;
  availabilityFilter: DataPanelRouteExplanationAvailabilityFilter;
  onAvailabilityFilterChange: (
    value: DataPanelRouteExplanationAvailabilityFilter
  ) => void;
  businessFilter: string;
  onBusinessFilterChange: (value: string) => void;
  bottleneckFilter: string;
  onBottleneckFilterChange: (value: string) => void;
}) {
  return (
    <div className="data-panel-route-filter">
      <label className="data-panel-route-filter-field" htmlFor="data-panel-route-explanation-filter">
        <span>路由筛选</span>
        <input
          id="data-panel-route-explanation-filter"
          type="search"
          value={filterValue}
          onChange={(event) => onFilterChange(event.currentTarget.value)}
          placeholder="用户 / 卫星 / 下一跳 / 路径"
        />
      </label>
      <label
        className="data-panel-route-filter-field"
        htmlFor="data-panel-route-availability-filter"
      >
        <span>可用性</span>
        <select
          id="data-panel-route-availability-filter"
          value={availabilityFilter}
          onChange={(event) =>
            onAvailabilityFilterChange(
              event.currentTarget.value as DataPanelRouteExplanationAvailabilityFilter
            )
          }
        >
          <option value="ALL">全部</option>
          <option value="AVAILABLE">可用</option>
          <option value="BLOCKED">阻塞</option>
        </select>
      </label>
      <label className="data-panel-route-filter-field" htmlFor="data-panel-route-business-filter">
        <span>业务</span>
        <select
          id="data-panel-route-business-filter"
          value={businessFilter}
          onChange={(event) => onBusinessFilterChange(event.currentTarget.value)}
        >
          <option value="ALL">全部</option>
          <option value="COMPUTE_SERVICE">通信-计算</option>
          <option value="DATA_TRANSFER">数据传输</option>
          <option value="BULK_DOWNLINK">批量下传</option>
        </select>
      </label>
      <label
        className="data-panel-route-filter-field"
        htmlFor="data-panel-route-bottleneck-filter"
      >
        <span>瓶颈</span>
        <select
          id="data-panel-route-bottleneck-filter"
          value={bottleneckFilter}
          onChange={(event) => onBottleneckFilterChange(event.currentTarget.value)}
        >
          <option value="ALL">全部</option>
          <option value="CAPACITY">容量</option>
          <option value="AVAILABILITY">可用性</option>
          <option value="LOSS_PROXY">损耗代理</option>
          <option value="PATH">路径</option>
          <option value="NONE">无瓶颈</option>
        </select>
      </label>
    </div>
  );
}

function TopComputeNodeTable({ rows }: { rows: readonly TopComputeNodeRow[] }) {
  if (rows.length === 0) {
    return <div className="data-panel-compute-empty">等待算力节点快照</div>;
  }
  return (
    <div className="data-panel-compute-node-table" aria-label="高负载卫星算力节点">
      <div className="data-panel-compute-node-row header">
        <span>节点</span>
        <span>状态</span>
        <span>负载</span>
        <span>FP32</span>
        <span>任务</span>
      </div>
      {rows.map((row) => (
        <div className="data-panel-compute-node-row" key={row.nodeId}>
          <span title={row.nodeId}>{row.nodeId}</span>
          <span>{row.statusLabel}</span>
          <span>{row.loadLabel}</span>
          <span>{row.fp32Label}</span>
          <span>{row.taskLabel}</span>
        </div>
      ))}
    </div>
  );
}

function ServiceDetailPageTable({
  rows,
  page,
  control,
  selectedServiceId,
  filterValue,
  onFilterChange,
  onSelect
}: {
  rows: DataPanelServiceDetailRows;
  page: RuntimeServiceDetailPageV1 | null | undefined;
  control?: RuntimeDetailCursorControl | null;
  selectedServiceId?: string | null;
  filterValue: string;
  onFilterChange: (value: string) => void;
  onSelect?: (row: DataPanelServiceDetailRow) => void;
}) {
  const filters = filterValue ? { query: filterValue } : undefined;
  if (rows.items.length === 0) {
    return (
      <div className="data-panel-route-empty">
        {rows.summaryLabel}
        <BackendTextFilter
          label="服务筛选"
          value={filterValue}
          placeholder="task / sat / route / queue"
          onChange={onFilterChange}
        />
        <BackendCursorPager
          label="服务生命周期"
          page={page}
          totalCount={page?.service_count ?? 0}
          control={control}
          filters={filters}
        />
      </div>
    );
  }
  return (
    <div
      className="data-panel-route-table service-detail"
      aria-label="服务生命周期游标明细"
    >
      <div className="data-panel-route-source">{rows.sourceLabel}</div>
      <BackendTextFilter
        label="服务筛选"
        value={filterValue}
        placeholder="task / sat / route / queue"
        onChange={onFilterChange}
      />
      <BackendCursorPager
        label="服务生命周期"
        page={page}
        totalCount={page?.service_count ?? rows.items.length}
        control={control}
        filters={filters}
      />
      <div className="data-panel-route-row header">
        <span>服务</span>
        <span>状态</span>
        <span>放置</span>
        <span>网络</span>
        <span>计算</span>
        <span>总延迟</span>
      </div>
      {rows.items.map((row) => (
        <button
          type="button"
          className={`data-panel-route-row ${
            row.serviceId === selectedServiceId ? "selected" : ""
          }`}
          key={row.serviceId}
          title={row.traceTitle}
          onClick={() => onSelect?.(row)}
        >
          <span>{row.taskLabel}</span>
          <span>{row.stateLabel}</span>
          <span>{row.placementLabel}</span>
          <span>{row.networkLatencyLabel}</span>
          <span>{row.computeLatencyLabel}</span>
          <span>{row.totalLatencyLabel}</span>
        </button>
      ))}
    </div>
  );
}

function ServiceLifecycleTracePanel({
  display,
  selectedTraceId,
  onSelect
}: {
  display: DataPanelServiceLifecycleTraceDisplay;
  selectedTraceId?: string | null;
  onSelect?: (row: DataPanelServiceLifecycleTraceRow) => void;
}) {
  if (display.items.length === 0) {
    return (
      <div className="data-panel-route-empty">
        {display.summaryLabel}
        <div className="data-panel-route-source">{display.sourceLabel}</div>
      </div>
    );
  }
  return (
    <div
      className="data-panel-route-table service-trace"
      aria-label="服务生命周期 trace v2"
    >
      <div className="data-panel-route-source">{display.sourceLabel}</div>
      <div className="data-panel-source-note">
        <span>后端 service_lifecycle_trace_v2</span>
        <small>{display.summaryLabel}</small>
      </div>
      <div className="data-panel-route-row header">
        <span>服务</span>
        <span>终态</span>
        <span>节点</span>
        <span>网络</span>
        <span>计算</span>
        <span>总时延</span>
      </div>
      {display.items.map((row) => (
        <button
          type="button"
          className={`data-panel-route-row ${
            row.traceId === selectedTraceId ? "selected" : ""
          }`}
          key={row.traceId}
          title={row.traceTitle}
          onClick={() => onSelect?.(row)}
        >
          <span>{row.serviceLabel}</span>
          <span>{row.terminalStateLabel}</span>
          <span>{row.computeNodeLabel}</span>
          <span>{row.networkLatencyLabel}</span>
          <span>{row.computeLatencyLabel}</span>
          <span>{row.totalLatencyLabel}</span>
        </button>
      ))}
      <div className="data-panel-service-timeline" aria-label="服务生命周期阶段">
        {display.items.flatMap((row) =>
          row.stages.map((stage) => (
            <span
              className="data-panel-service-segment"
              key={`${row.traceId}:${stage.stageId}`}
              title={stage.traceTitle}
            >
              <small>{stage.label}</small>
              <strong>{stage.durationLabel}</strong>
              <em>{stage.statusLabel}</em>
            </span>
          ))
        )}
      </div>
    </div>
  );
}

function ServiceTraceFilterControls({
  filterValue,
  terminalFilter,
  computeNodeFilter,
  stageFilter,
  terminalReasonFilter,
  onFilterChange,
  onTerminalFilterChange,
  onComputeNodeFilterChange,
  onStageFilterChange,
  onTerminalReasonFilterChange
}: {
  filterValue: string;
  terminalFilter: DataPanelServiceTraceTerminalFilter;
  computeNodeFilter: string;
  stageFilter: DataPanelServiceTraceStageFilter;
  terminalReasonFilter: DataPanelServiceTraceTerminalReasonFilter;
  onFilterChange: (value: string) => void;
  onTerminalFilterChange: (value: DataPanelServiceTraceTerminalFilter) => void;
  onComputeNodeFilterChange: (value: string) => void;
  onStageFilterChange: (value: DataPanelServiceTraceStageFilter) => void;
  onTerminalReasonFilterChange: (
    value: DataPanelServiceTraceTerminalReasonFilter
  ) => void;
}) {
  return (
    <div className="data-panel-service-trace-filters" role="group" aria-label="服务 trace 筛选">
      <label>
        <span>trace</span>
        <input
          type="search"
          value={filterValue}
          placeholder="service / task / flow / route / stage"
          onChange={(event) => onFilterChange(event.currentTarget.value)}
        />
      </label>
      <label>
        <span>终态</span>
        <select
          value={terminalFilter}
          onChange={(event) =>
            onTerminalFilterChange(
              event.currentTarget.value as DataPanelServiceTraceTerminalFilter
            )
          }
        >
          <option value="ALL">全部</option>
          <option value="RUNNING">运行中</option>
          <option value="COMPLETE">完成</option>
          <option value="INCOMPLETE">不完整</option>
        </select>
      </label>
      <label>
        <span>算力节点</span>
        <input
          type="search"
          value={computeNodeFilter}
          placeholder="sat-00002"
          onChange={(event) => onComputeNodeFilterChange(event.currentTarget.value)}
        />
      </label>
      <label>
        <span>阶段</span>
        <select
          value={stageFilter}
          onChange={(event) =>
            onStageFilterChange(
              event.currentTarget.value as DataPanelServiceTraceStageFilter
            )
          }
        >
          <option value="ALL">全部阶段</option>
          <option value="INPUT_NETWORK">输入网络</option>
          <option value="COMPUTE_QUEUE">算力排队</option>
          <option value="COMPUTE_EXECUTION">算力执行</option>
          <option value="OUTPUT_NETWORK">输出网络</option>
        </select>
      </label>
      <label>
        <span>终态原因</span>
        <select
          value={terminalReasonFilter}
          onChange={(event) =>
            onTerminalReasonFilterChange(
              event.currentTarget
                .value as DataPanelServiceTraceTerminalReasonFilter
            )
          }
        >
          <option value="ALL">全部原因</option>
          <option value="TOTAL_LATENCY_OBSERVED">总时延已观测</option>
          <option value="OUTPUT_NETWORK_PENDING">输出网络待完成</option>
          <option value="COMPONENTS_OBSERVED_BUT_TOTAL_MISSING">
            部分阶段已观测
          </option>
          <option value="NO_COMPONENT_OBSERVATIONS">无阶段观测</option>
        </select>
      </label>
    </div>
  );
}

function ComputeNodeDetailPageTable({
  rows,
  page,
  control,
  selectedNodeId,
  filterValue,
  onFilterChange,
  onSelect
}: {
  rows: DataPanelComputeNodeDetailRows;
  page: RuntimeComputeNodeDetailPageV1 | null | undefined;
  control?: RuntimeDetailCursorControl | null;
  selectedNodeId?: string | null;
  filterValue: string;
  onFilterChange: (value: string) => void;
  onSelect?: (row: DataPanelComputeNodeDetailRow) => void;
}) {
  const filters = filterValue ? { query: filterValue } : undefined;
  if (rows.items.length === 0) {
    return (
      <div className="data-panel-compute-empty">
        {rows.summaryLabel}
        <BackendTextFilter
          label="算力节点筛选"
          value={filterValue}
          placeholder="sat / busy / GPU / memory"
          onChange={onFilterChange}
        />
        <BackendCursorPager
          label="算力节点"
          page={page}
          totalCount={page?.compute_node_count ?? 0}
          control={control}
          filters={filters}
        />
      </div>
    );
  }
  return (
    <div className="data-panel-compute-node-table detail" aria-label="算力节点游标明细">
      <div className="data-panel-route-source">{rows.sourceLabel}</div>
      <BackendTextFilter
        label="算力节点筛选"
        value={filterValue}
        placeholder="sat / busy / GPU / memory"
        onChange={onFilterChange}
      />
      <BackendCursorPager
        label="算力节点"
        page={page}
        totalCount={page?.compute_node_count ?? rows.items.length}
        control={control}
        filters={filters}
      />
      <div className="data-panel-compute-node-row header">
        <span>节点</span>
        <span>状态</span>
        <span>负载</span>
        <span>FP32</span>
        <span>GPU/NPU</span>
        <span>内存/存储</span>
        <span>任务</span>
      </div>
      {rows.items.map((row) => (
        <button
          type="button"
          className={`data-panel-compute-node-row ${
            row.nodeId === selectedNodeId ? "selected" : ""
          }`}
          key={row.nodeId}
          title={row.traceTitle}
          onClick={() => onSelect?.(row)}
        >
          <span>{row.nodeId}</span>
          <span>{row.statusLabel}</span>
          <span>{row.loadLabel}</span>
          <span>{row.fp32Label}</span>
          <span>{row.acceleratorLabel}</span>
          <span>{row.memoryStorageLabel}</span>
          <span>{row.taskLabel}</span>
        </button>
      ))}
    </div>
  );
}

function BackendTextFilter({
  label,
  value,
  placeholder,
  onChange
}: {
  label: string;
  value: string;
  placeholder: string;
  onChange: (value: string) => void;
}) {
  return (
    <label className="data-panel-backend-filter">
      <span>{label}</span>
      <input
        type="search"
        value={value}
        placeholder={placeholder}
        onChange={(event) => onChange(event.currentTarget.value)}
      />
    </label>
  );
}

function BackendCursorPager({
  label,
  page,
  totalCount,
  control,
  filters
}: {
  label: string;
  page:
    | RuntimeUserRequestSummaryV1
    | RuntimeSatelliteServiceSummaryV1
    | RuntimeRouteExplanationSummaryV1
    | RuntimeServiceDetailPageV1
    | RuntimeServiceLifecycleTraceV2
    | RuntimeComputeNodeDetailPageV1
    | null
    | undefined;
  totalCount: number;
  control?: RuntimeDetailCursorControl | null;
  filters?: RuntimeDetailCursorFilters;
}) {
  if (
    page === null ||
    page === undefined ||
    page.cursor === undefined ||
    page.limit === undefined ||
    page.next_cursor === undefined ||
    page.has_more === undefined
  ) {
    return null;
  }
  const display = buildDataPanelBackendCursorDisplay(page, totalCount);
  const loading = control?.loading === true;
  const canUseControls = typeof control?.onCursorChange === "function";
  return (
    <div className="data-panel-detail-pager backend-cursor" aria-label={`${label}后端游标`}>
      <span>{label}</span>
      <strong>{display.rangeLabel}</strong>
      <button
        type="button"
        disabled={!display.canPrevious || loading || !canUseControls}
        onClick={() => control?.onCursorChange?.(display.previousCursor, filters)}
      >
        上一页
      </button>
      <button
        type="button"
        disabled={!display.canNext || loading || !canUseControls}
        onClick={() => control?.onCursorChange?.(display.nextCursor, filters)}
      >
        下一页
      </button>
      <button
        type="button"
        disabled={loading || !control?.onRefresh}
        onClick={() => control?.onRefresh?.(filters)}
      >
        刷新
      </button>
      <small>
        {loading ? "正在读取后端页" : display.statusLabel}
        {control?.error ? ` / ${control.error}` : ""}
      </small>
    </div>
  );
}

function DetailPaginationControls<T>({
  page,
  label,
  windowNote,
  onPrevious,
  onNext
}: {
  page: DetailRowPage<T>;
  label: string;
  windowNote?: string | null;
  onPrevious: () => void;
  onNext: () => void;
}) {
  if (page.totalCount <= page.pageSize) {
    return (
      <div className="data-panel-detail-pager">
        <span>{label}</span>
        <strong>显示全部 {formatCount(page.totalCount)} 行</strong>
        {windowNote ? <small>{windowNote}</small> : null}
      </div>
    );
  }
  return (
    <div className="data-panel-detail-pager">
      <span>{label}</span>
      <strong>
        {formatCount(page.startIndex + 1)}-{formatCount(page.endIndex)} /{" "}
        {formatCount(page.totalCount)}
      </strong>
      <button type="button" disabled={page.pageIndex <= 0} onClick={onPrevious}>
        上一页
      </button>
      <button
        type="button"
        disabled={page.pageIndex >= page.pageCount - 1}
        onClick={onNext}
      >
        下一页
      </button>
      {windowNote ? <small>{windowNote}</small> : null}
    </div>
  );
}

function DetailInspectorGrid({
  user,
  satellite
}: {
  user: DataPanelDetailInspector;
  satellite: DataPanelDetailInspector;
}) {
  return (
    <div className="data-panel-detail-inspector-grid" aria-label="选中节点详情">
      <DetailInspectorCard title={user.title} subtitle={user.subtitle} fields={user.fields} />
      <DetailInspectorCard
        title={satellite.title}
        subtitle={satellite.subtitle}
        fields={satellite.fields}
      />
    </div>
  );
}

function ExactDetailInspectorGrid({
  items
}: {
  items: readonly DataPanelDetailInspector[];
}) {
  return (
    <div className="data-panel-detail-inspector-grid exact" aria-label="后端精确行详情">
      {items.map((item) => (
        <DetailInspectorCard
          title={item.title}
          subtitle={item.subtitle}
          fields={item.fields}
          key={item.title}
        />
      ))}
    </div>
  );
}

function DetailInspectorDrawer({
  items
}: {
  items: readonly DataPanelNodeDetailDrawerItem[];
}) {
  return (
    <section className="data-panel-node-detail-drawer" aria-label="选中节点完整详情">
      <div className="data-panel-node-detail-drawer-header">
        <div>
          <span>选中节点详情</span>
          <small>后端节点详情页优先，旧运行时状态自动回退</small>
        </div>
      </div>
      <div className="data-panel-node-detail-drawer-grid">
        {items.map((item) => (
          <div className="data-panel-node-detail-drawer-card" key={item.kind}>
            <div className="data-panel-node-detail-drawer-title">
              <span>{item.title}</span>
              <small>{item.subtitle}</small>
            </div>
            {item.fields.length === 0 ? (
              <div className="data-panel-node-detail-drawer-empty">{item.emptyLabel}</div>
            ) : (
              <div className="data-panel-node-detail-drawer-sections">
                {(item.sections.length > 0
                  ? item.sections
                  : [{ sectionId: "fields", title: "节点详情", fields: item.fields }]
                ).map((section) => (
                  <section
                    className="data-panel-node-detail-drawer-section"
                    key={section.sectionId}
                  >
                    <div className="data-panel-node-detail-drawer-section-title">
                      {section.title}
                    </div>
                    <dl className="data-panel-node-detail-drawer-fields">
                      {section.fields.map((field) => (
                        <div
                          className={`data-panel-node-detail-drawer-field ${
                            field.tone ?? "normal"
                          }`}
                          key={`${section.sectionId}:${field.label}`}
                        >
                          <dt>{field.label}</dt>
                          <dd title={field.value}>{field.value}</dd>
                        </div>
                      ))}
                    </dl>
                  </section>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </section>
  );
}

function DetailInspectorCard({ title, subtitle, fields }: DataPanelDetailInspector) {
  if (fields.length === 0) {
    return (
      <section className="data-panel-detail-inspector empty">
        <div>
          <span>{title}</span>
          <small>{subtitle}</small>
        </div>
      </section>
    );
  }
  return (
    <section className="data-panel-detail-inspector">
      <div className="data-panel-detail-inspector-title">
        <span>{title}</span>
        <small>{subtitle}</small>
      </div>
      <div className="data-panel-detail-inspector-fields">
        {fields.map((field) => (
          <span
            className={`data-panel-detail-inspector-field ${field.tone ?? "normal"}`}
            key={field.label}
            title={`${field.label}: ${field.value}`}
          >
            <small>{field.label}</small>
            <strong>{field.value}</strong>
          </span>
        ))}
      </div>
    </section>
  );
}

function UserBusinessRequestTable({
  rows,
  selectedUserId,
  onSelect
}: {
  rows: readonly UserBusinessRequestRow[];
  selectedUserId?: string | null;
  onSelect?: (row: UserBusinessRequestRow) => void;
}) {
  if (rows.length === 0) {
    return <div className="data-panel-detail-empty">等待用户节点快照</div>;
  }
  return (
    <div className="data-panel-table-scroll">
      <div className="data-panel-business-row header">
        <span>节点编号</span>
        <span>平台类型</span>
        <span>通信业务</span>
        <span>计算业务</span>
        <span>网络队列</span>
        <span>目标卫星</span>
        <span>目标节点</span>
        <span>放置节点</span>
        <span>状态</span>
        <span>时延/容量</span>
        <span>服务链路</span>
      </div>
      {rows.map((row) => (
        <button
          type="button"
          className={`data-panel-business-row ${
            row.userId === selectedUserId ? "selected" : ""
          }`}
          key={row.rowId ?? row.userId}
          title={[row.pathLabel, row.correlationLabel].filter(Boolean).join(" / ")}
          onClick={() => onSelect?.(row)}
        >
          <span>{row.userId}</span>
          <span>{row.platformTypeLabel}</span>
          <span>{row.communicationLabel}</span>
          <span>{row.computeLabel}</span>
          <span>{row.networkQueueLabel}</span>
          <span>{row.selectedSatelliteId}</span>
          <span>{row.destinationId}</span>
          <span>{row.placementLabel}</span>
          <span>{row.statusLabel}</span>
          <span>{row.latencyCapacityLabel}</span>
          <span>{row.serviceLabel}</span>
        </button>
      ))}
    </div>
  );
}

function SatelliteResourceTable({
  rows,
  selectedSatelliteId,
  onSelect
}: {
  rows: readonly SatelliteResourceRow[];
  selectedSatelliteId?: string | null;
  onSelect?: (row: SatelliteResourceRow) => void;
}) {
  if (rows.length === 0) {
    return <div className="data-panel-detail-empty">等待卫星算力快照</div>;
  }
  return (
    <div className="data-panel-table-scroll">
      <div className="data-panel-satellite-resource-row header">
        <span>卫星</span>
        <span>状态</span>
        <span>负载</span>
        <span>服务对象</span>
        <span>下一跳</span>
        <span>CPU FP32</span>
        <span>CPU FP64</span>
        <span>GPU</span>
        <span>NPU</span>
        <span>内存/存储</span>
        <span>业务</span>
        <span>网络</span>
      </div>
      {rows.map((row) => (
        <button
          type="button"
          className={`data-panel-satellite-resource-row ${
            row.satelliteId === selectedSatelliteId ? "selected" : ""
          }`}
          key={row.satelliteId}
          onClick={() => onSelect?.(row)}
        >
          <span>{row.satelliteId}</span>
          <span>{row.statusLabel}</span>
          <span>{row.loadLabel}</span>
          <span>{row.serviceObjectLabel}</span>
          <span>{row.nextHopLabel}</span>
          <span>{row.cpuFp32Label}</span>
          <span>{row.cpuFp64Label}</span>
          <span>{row.gpuLabel}</span>
          <span>{row.npuLabel}</span>
          <span>{row.memoryStorageLabel}</span>
          <span>{row.taskLabel}</span>
          <span>{row.networkLabel}</span>
        </button>
      ))}
    </div>
  );
}

export function buildDataPanelSummary(snapshot: WorldSnapshot): DataPanelSummary {
  const activeLinks = snapshot.links.filter((link) => link.availability);
  const availableRoutes = snapshot.routes.filter((route) => route.available);
  const routeHops = availableRoutes.map((route) => Math.max(0, route.path.length - 1));
  const availableRouteFlowIds = new Set(availableRoutes.map((route) => route.flow_id));
  const activeTaskIds = new Set(snapshot.active_tasks.map((task) => task.task_id));
  const networkWaiting = snapshot.routes.filter(
    (route) =>
      !route.available &&
      !activeTaskIds.has(route.flow_id) &&
      !availableRouteFlowIds.has(route.flow_id)
  ).length;

  return {
    simTime: snapshot.last_sim_time,
    eventCount: snapshot.event_count,
    eventRate: snapshot.metrics_summary.system.eventRate,
    satelliteCount: snapshot.satellites.length,
    groundUserCount: snapshot.ground_users.length,
    activeLinks: activeLinks.length,
    spaceLinks: activeLinks.filter(isSpaceLink).length,
    accessLinks: activeLinks.filter(isAccessLink).length,
    availableRoutes: availableRoutes.length,
    totalRoutes: snapshot.routes.length,
    routeAvailabilityPercent:
      snapshot.routes.length === 0
        ? 0
        : Math.round((availableRoutes.length / snapshot.routes.length) * 100),
    averageRouteLatency: average(availableRoutes.map((route) => route.latency)),
    averageRouteCapacity: average(availableRoutes.map((route) => route.capacity)),
    averageRouteHops: average(routeHops),
    maxRouteHops: routeHops.length === 0 ? 0 : Math.max(...routeHops),
    runningTasks: snapshot.metrics_summary.compute.runningTasks,
    finishedTasks: snapshot.metrics_summary.compute.finishedTasks,
    deadlineMissedTasks: snapshot.metrics_summary.compute.deadlineMissedTasks,
    computeNodes: snapshot.compute_nodes.length,
    networkWaiting,
    couplingHealth: couplingHealthScore({
      hasOrbit: snapshot.satellites.length > 0,
      hasGroundUsers: snapshot.ground_users.length > 0,
      hasLinks: activeLinks.length > 0,
      hasRoutes: availableRoutes.length > 0,
      hasCompute: snapshot.compute_nodes.length > 0,
      hasEvents: snapshot.event_count > 0
    })
  };
}

export function buildDataPanelDisplaySummary(
  summary: DataPanelSummary,
  displaySimTime: number,
  displayEventCount: number
): DataPanelSummary {
  return {
    ...summary,
    simTime: Math.max(summary.simTime, displaySimTime),
    eventCount: Math.max(summary.eventCount, Math.round(displayEventCount))
  };
}

export interface DataPanelRuntimeProgress {
  percent: number;
  percentLabel: string;
  elapsedLabel: string;
  durationLabel: string;
}

export function buildDataPanelRuntimeProgress(
  simTime: number,
  durationSeconds: number
): DataPanelRuntimeProgress {
  const duration = Math.max(1, durationSeconds);
  const elapsed = Math.min(Math.max(0, simTime), duration);
  const percent = Math.min(100, Math.max(0, (elapsed / duration) * 100));
  return {
    percent,
    percentLabel: `${formatPercent(percent)}%`,
    elapsedLabel: formatDurationCompact(elapsed),
    durationLabel: formatDurationCompact(duration)
  };
}

export function buildDataPanelConfiguredScale(
  generatedConfig: GeneratedScenarioConfig | null,
  fidelitySummary?: FidelitySummary | null
): string {
  const constellation = generatedConfig?.backend_summary?.derived_constellation_summary;
  const satelliteCount =
    constellation?.satellite_count ??
    generatedConfig?.satellite_count ??
    fidelitySummary?.satellite_count;
  const userCount = generatedConfig?.user_count ?? fidelitySummary?.user_count;
  if (satelliteCount === undefined && userCount === undefined) {
    return "等待初始化";
  }

  const parts: string[] = [];
  if (satelliteCount !== undefined) {
    parts.push(`${formatCount(satelliteCount)} 星`);
  }
  if (constellation !== undefined) {
    parts.push(`${formatCount(constellation.plane_count)} 面`);
    parts.push(`${formatCount(constellation.satellites_per_plane)} 星/面`);
  } else if (generatedConfig !== null && generatedConfig.orbit_plane_count > 0) {
    parts.push(`${formatCount(generatedConfig.orbit_plane_count)} 面`);
  }
  if (userCount !== undefined) {
    parts.push(`${formatCount(userCount)} 用户`);
  }

  const scaleMode = dataPanelScaleModeLabel(fidelitySummary?.current_scale_mode);
  if (scaleMode !== null) {
    parts.push(scaleMode);
  }
  return parts.join(" / ");
}

function dataPanelScaleModeLabel(mode: string | undefined): string | null {
  if (mode === undefined || mode === "none" || mode === "NONE") {
    return null;
  }
  if (mode === "LARGE_SCALE_AGGREGATED") {
    return "大规模聚合";
  }
  if (mode === "MEDIUM_SCALE_BATCHED") {
    return "中规模批量";
  }
  if (mode === "SMALL_SCALE_DETAILED") {
    return "小规模详细";
  }
  return mode;
}

export interface DataPanelTelemetryPoint {
  timeLabel: string;
  simTime: number;
  throughputMbps: number;
  latencyMs: number;
  lossPercent: number;
  jitterMs: number;
  computeUsedTflops: number;
  computeCpuFp64Gflops: number;
  computeGpuFp32Tflops: number;
  computeGpuFp16Tflops: number;
  computeNpuInt8Tops: number;
  computeMemoryGb: number;
  computeStorageGb: number;
}

export type DataPanelComputeSeriesKey =
  | "computeUsedTflops"
  | "computeCpuFp64Gflops"
  | "computeGpuFp32Tflops"
  | "computeGpuFp16Tflops"
  | "computeNpuInt8Tops"
  | "computeMemoryGb"
  | "computeStorageGb";

interface DataPanelComputeSeriesOption {
  key: DataPanelComputeSeriesKey;
  label: string;
  shortLabel: string;
  unit: string;
}

export const COMPUTE_SERIES_OPTIONS: readonly DataPanelComputeSeriesOption[] = [
  {
    key: "computeUsedTflops",
    label: "FP32 主容量",
    shortLabel: "FP32",
    unit: "TFLOPS"
  },
  {
    key: "computeCpuFp64Gflops",
    label: "CPU FP64",
    shortLabel: "FP64",
    unit: "GFLOPS"
  },
  {
    key: "computeGpuFp32Tflops",
    label: "GPU FP32",
    shortLabel: "GPU32",
    unit: "TFLOPS"
  },
  {
    key: "computeGpuFp16Tflops",
    label: "GPU FP16",
    shortLabel: "GPU16",
    unit: "TFLOPS"
  },
  {
    key: "computeNpuInt8Tops",
    label: "NPU INT8",
    shortLabel: "INT8",
    unit: "TOPS"
  },
  {
    key: "computeMemoryGb",
    label: "内存",
    shortLabel: "内存",
    unit: "GB"
  },
  {
    key: "computeStorageGb",
    label: "存储",
    shortLabel: "存储",
    unit: "GB"
  }
];

export interface NetworkQualityKpis {
  source: DataPanelNetworkKpiSource["sourceLabel"];
  throughputMbps: number;
  latencyMs: number;
  lossPercent: number;
  jitterMs: number;
}

export interface DataPanelComputeVectorTailItem {
  label: string;
  value: string;
}

export interface DataPanelComputeBottleneckDisplay {
  label: string;
  utilizationLabel: string;
  statusLabel: string;
  detailLabel: string;
}

export interface ComputeResourcePoolSlice {
  name: string;
  value: number;
  color: string;
}

export interface ComputeResourcePool {
  totalTflops: number;
  usedTflops: number;
  availableTflops: number;
  usedPercent: number;
  vectorSummary: ComputeResourceVectorPoolSummary;
  slices: readonly ComputeResourcePoolSlice[];
}

export interface ComputeResourceVectorPoolSummary {
  cpuFp64Gflops: number;
  usedCpuFp32Gflops: number;
  availableCpuFp32Gflops: number;
  usedCpuFp64Gflops: number;
  availableCpuFp64Gflops: number;
  gpuFp32Tflops: number;
  usedGpuFp32Tflops: number;
  availableGpuFp32Tflops: number;
  gpuFp16Tflops: number;
  usedGpuFp16Tflops: number;
  availableGpuFp16Tflops: number;
  npuInt8Tops: number;
  usedNpuInt8Tops: number;
  availableNpuInt8Tops: number;
  memoryGb: number;
  usedMemoryGb: number;
  availableMemoryGb: number;
  storageGb: number;
  usedStorageGb: number;
  availableStorageGb: number;
  utilizationMode: string;
}

export interface TopComputeNodeRow {
  nodeId: string;
  statusLabel: string;
  loadPercent: number;
  usedFp32Gflops: number;
  runningTasks: number;
  loadLabel: string;
  fp32Label: string;
  taskLabel: string;
}

export interface UserBusinessRequestRows {
  sourceLabel: string;
  summaryLabel: string;
  items: readonly UserBusinessRequestRow[];
}

export interface UserBusinessRequestRow {
  rowId?: string;
  userId: string;
  requestId?: string;
  serviceRequestId?: string;
  routeId?: string;
  flowId?: string;
  taskId?: string;
  computeNodeId?: string;
  nextHopId?: string;
  platformTypeLabel: string;
  communicationLabel: string;
  computeLabel: string;
  networkQueueLabel: string;
  selectedSatelliteId: string;
  destinationId: string;
  placementLabel: string;
  statusLabel: string;
  latencyCapacityLabel: string;
  serviceLabel: string;
  pathLabel: string;
  correlationLabel?: string;
}

export interface DataPanelUserRequestHistory {
  sourceLabel: string;
  summaryLabel: string;
  selectedUserId: string | null;
  availableUserIds: readonly string[];
  points: readonly DataPanelUserRequestHistoryPoint[];
}

export interface DataPanelUserRequestHistoryPoint {
  timeLabel: string;
  simTime: number;
  communicationRouteCount: number;
  availableRouteCount: number;
  computeServiceCount: number;
  networkQueueCount: number;
  latencyMs: number;
  capacityMbps: number;
  lossPercent: number;
  selectedSatelliteId: string;
  destinationId: string;
  statusLabel: string;
  primaryRouteId: string;
  primaryFlowId: string;
  serviceLabel: string;
}

export interface SatelliteResourceRows {
  sourceLabel: string;
  summaryLabel: string;
  items: readonly SatelliteResourceRow[];
}

export interface SatelliteResourceRow {
  satelliteId: string;
  statusLabel: string;
  loadPercent: number;
  loadLabel: string;
  serviceObjectLabel: string;
  nextHopLabel: string;
  cpuFp32Label: string;
  cpuFp64Label: string;
  gpuLabel: string;
  npuLabel: string;
  memoryStorageLabel: string;
  taskLabel: string;
  networkLabel: string;
}

export interface DataPanelSatelliteResourceHistory {
  sourceLabel: string;
  summaryLabel: string;
  selectedSatelliteId: string | null;
  availableSatelliteIds: readonly string[];
  points: readonly DataPanelSatelliteResourceHistoryPoint[];
}

export interface DataPanelSatelliteResourceHistoryPoint {
  timeLabel: string;
  simTime: number;
  loadPercent: number;
  usedFp32Gflops: number;
  usedFp64Gflops: number;
  usedGpuFp32Tflops: number;
  usedGpuFp16Tflops: number;
  usedNpuInt8Tops: number;
  usedMemoryGb: number;
  usedStorageGb: number;
}

export interface DetailRowPage<T> {
  items: readonly T[];
  totalCount: number;
  pageIndex: number;
  pageSize: number;
  pageCount: number;
  startIndex: number;
  endIndex: number;
}

export type RuntimeDetailSourceTone = "backend" | "mixed" | "snapshot";

export interface DataPanelDetailPageSizes {
  users: number;
  satellites: number;
  routes: number;
  services: number;
  serviceTraces: number;
  computeNodes: number;
}

export interface RuntimeDetailSourceBadge {
  label: string;
  title: string;
  tone: RuntimeDetailSourceTone;
}

export interface DataPanelDetailScopeNote {
  label: string;
  value: string;
  detail: string;
  tone: "backend" | "limit" | "history";
}

export function buildDataPanelDetailPageSizes(
  contract: LargeDetailPaginationContractV2 | null | undefined
): DataPanelDetailPageSizes {
  const collections = detailPaginationCollections(contract);
  return {
    users: detailPaginationLimit(
      collections.get("ground_users"),
      FALLBACK_USER_DETAIL_PAGE_SIZE
    ),
    satellites: detailPaginationLimit(
      collections.get("satellites"),
      FALLBACK_SATELLITE_DETAIL_PAGE_SIZE
    ),
    routes: detailPaginationLimit(collections.get("routes"), 96),
    services: detailPaginationLimit(collections.get("services"), 120),
    serviceTraces: detailPaginationLimit(collections.get("service_traces"), 120),
    computeNodes: detailPaginationLimit(collections.get("compute_nodes"), 120)
  };
}

export interface DataPanelDetailInspector {
  title: string;
  subtitle: string;
  sections?: readonly DataPanelNodeDetailSection[];
  fields: readonly DataPanelDetailInspectorField[];
}

export interface DataPanelDetailInspectorField {
  label: string;
  value: string;
  tone?: "normal" | "warning" | "resource";
}

export interface DataPanelNodeDetailDrawerItem {
  kind: "user" | "satellite" | "service_trace";
  title: string;
  subtitle: string;
  emptyLabel: string;
  sections: readonly DataPanelNodeDetailSection[];
  fields: readonly DataPanelDetailInspectorField[];
}

export interface DataPanelNodeDetailSection {
  sectionId: string;
  title: string;
  fields: readonly DataPanelDetailInspectorField[];
}

export function buildDataPanelTelemetry(
  snapshot: WorldSnapshot,
  displaySimTime = snapshot.last_sim_time,
  backendMetrics: RuntimeMetricsSummary | null | undefined = undefined,
  backendKpiTimeSeries: RuntimeKpiTimeSeriesV1 | null | undefined = undefined
): readonly DataPanelTelemetryPoint[] {
  const backendComputeUsedGflops = metricNumber(
    backendMetrics,
    "compute_resource_used_gflops_fp32"
  );
  const baseKpis = resolveNetworkQualityKpis(snapshot, backendMetrics);
  const computePool = buildComputeResourcePool(snapshot, backendMetrics);
  const computeUsedTflops =
    backendComputeUsedGflops !== undefined
      ? backendComputeUsedGflops / 1000
      : computePool.usedTflops;
  const runtimeKpiSeries = buildRuntimeKpiTelemetrySamples(
    backendKpiTimeSeries,
    displaySimTime
  );
  if (runtimeKpiSeries.length > 0) {
    return runtimeKpiSeries.map((point) => {
      const useRecentWindow = runtimeKpiSampleHasRecentFlowSamples(point);
      const throughputMbps =
        useRecentWindow && point.network_recent_delivered_throughput_mbps !== undefined
          ? point.network_recent_delivered_throughput_mbps
          : point.network_effective_throughput_mbps;
      const latencySeconds =
        useRecentWindow && point.network_recent_latency_s !== undefined
          ? point.network_recent_latency_s
          : point.network_effective_latency_s;
      const lossRate =
        useRecentWindow && point.network_recent_loss_proxy_rate !== undefined
          ? point.network_recent_loss_proxy_rate
          : point.network_effective_loss_proxy_rate;
      const delayVariationSeconds =
        useRecentWindow && point.network_recent_delay_variation_s !== undefined
          ? point.network_recent_delay_variation_s
          : point.network_effective_delay_variation_s;
      return {
        timeLabel: formatDurationCompact(point.sim_time),
        simTime: point.sim_time,
        throughputMbps: roundMetric(throughputMbps),
        latencyMs: roundMetric(latencySeconds * 1000),
        lossPercent: roundMetric(lossRate * 100),
        jitterMs: roundMetric(delayVariationSeconds * 1000),
        computeUsedTflops: roundMetric(point.compute_resource_used_gflops_fp32 / 1000),
        computeCpuFp64Gflops: roundMetric(point.compute_resource_used_gflops_fp64 ?? 0),
        computeGpuFp32Tflops: roundMetric(point.compute_resource_used_gpu_tflops_fp32 ?? 0),
        computeGpuFp16Tflops: roundMetric(point.compute_resource_used_gpu_tflops_fp16 ?? 0),
        computeNpuInt8Tops: roundMetric(point.compute_resource_used_npu_tops_int8 ?? 0),
        computeMemoryGb: roundMetric(point.compute_resource_used_memory_gb ?? 0),
        computeStorageGb: roundMetric(point.compute_resource_used_storage_gb ?? 0)
      };
    });
  }
  const backendKpiSeries = snapshot.metrics_summary.network.kpiSeries ?? [];
  if (backendKpiSeries.length > 0) {
    const points = backendKpiSeries.slice(-24);
    const lastIndex = Math.max(1, points.length - 1);
    return points.map((point, index) => {
      const sequenceProgress = points.length === 1 ? 1 : index / lastIndex;
      const envelope = 0.65 + sequenceProgress * 0.35;
      return {
        timeLabel: formatDurationCompact(point.simTime),
        simTime: point.simTime,
        throughputMbps: roundMetric(point.throughputMbps),
        latencyMs: roundMetric(point.latencyMs),
      lossPercent: roundMetric(point.lossPercent),
      jitterMs: roundMetric(point.jitterMs),
      computeUsedTflops: roundMetric(computeUsedTflops * envelope),
      computeCpuFp64Gflops: roundMetric(
        computePool.vectorSummary.usedCpuFp64Gflops * envelope
      ),
      computeGpuFp32Tflops: roundMetric(
        computePool.vectorSummary.usedGpuFp32Tflops * envelope
      ),
      computeGpuFp16Tflops: roundMetric(
        computePool.vectorSummary.usedGpuFp16Tflops * envelope
      ),
      computeNpuInt8Tops: roundMetric(computePool.vectorSummary.usedNpuInt8Tops * envelope),
      computeMemoryGb: roundMetric(computePool.vectorSummary.usedMemoryGb * envelope),
      computeStorageGb: roundMetric(computePool.vectorSummary.usedStorageGb * envelope)
    };
  });
}
  const eventSeries =
    snapshot.metrics_summary.system.eventSeries.length > 0
      ? snapshot.metrics_summary.system.eventSeries
      : [
          {
            index: 0,
            simTime: Math.max(snapshot.last_sim_time, displaySimTime)
          }
        ];
  const points = eventSeries.slice(-24);
  const lastSimTime = Math.max(
    1,
    displaySimTime,
    snapshot.last_sim_time,
    ...points.map((point) => point.simTime)
  );
  const lastIndex = Math.max(1, points.length - 1);

  return points.map((point, index) => {
    const sequenceProgress = points.length === 1 ? 1 : index / lastIndex;
    const timeProgress = Math.min(1, Math.max(0, point.simTime / lastSimTime));
    const envelope = 0.65 + Math.max(sequenceProgress, timeProgress) * 0.35;
    return {
      timeLabel: formatDurationCompact(point.simTime),
      simTime: point.simTime,
      throughputMbps: roundMetric(baseKpis.throughputMbps * envelope),
      latencyMs: roundMetric(baseKpis.latencyMs * (0.92 + envelope * 0.08)),
      lossPercent: roundMetric(baseKpis.lossPercent * (0.7 + envelope * 0.3)),
      jitterMs: roundMetric(baseKpis.jitterMs * (0.75 + envelope * 0.25)),
      computeUsedTflops: roundMetric(computeUsedTflops * envelope),
      computeCpuFp64Gflops: roundMetric(
        computePool.vectorSummary.usedCpuFp64Gflops * envelope
      ),
      computeGpuFp32Tflops: roundMetric(
        computePool.vectorSummary.usedGpuFp32Tflops * envelope
      ),
      computeGpuFp16Tflops: roundMetric(
        computePool.vectorSummary.usedGpuFp16Tflops * envelope
      ),
      computeNpuInt8Tops: roundMetric(computePool.vectorSummary.usedNpuInt8Tops * envelope),
      computeMemoryGb: roundMetric(computePool.vectorSummary.usedMemoryGb * envelope),
      computeStorageGb: roundMetric(computePool.vectorSummary.usedStorageGb * envelope)
    };
  });
}

function runtimeKpiSampleHasRecentFlowSamples(point: RuntimeKpiSampleV1): boolean {
  const recentFlowCount = point.network_recent_flow_count;
  return (
    typeof recentFlowCount === "number" &&
    Number.isFinite(recentFlowCount) &&
    recentFlowCount > 0
  );
}

export function buildDataPanelComputeVectorTail(
  backendKpiTimeSeries: RuntimeKpiTimeSeriesV1 | null | undefined
): readonly DataPanelComputeVectorTailItem[] {
  const tail = backendKpiTimeSeries?.samples.at(-1);
  if (tail === undefined) {
    return [];
  }
  return [
    computeVectorTailItem("CPU FP64", tail.compute_resource_used_gflops_fp64, "GFLOPS"),
    computeVectorTailItem(
      "GPU FP32",
      tail.compute_resource_used_gpu_tflops_fp32,
      "TFLOPS"
    ),
    computeVectorTailItem(
      "GPU FP16",
      tail.compute_resource_used_gpu_tflops_fp16,
      "TFLOPS"
    ),
    computeVectorTailItem("NPU INT8", tail.compute_resource_used_npu_tops_int8, "TOPS"),
    computeVectorTailItem("内存", tail.compute_resource_used_memory_gb, "GB"),
    computeVectorTailItem("存储", tail.compute_resource_used_storage_gb, "GB")
  ].filter((item): item is DataPanelComputeVectorTailItem => item !== null);
}

export function buildDataPanelComputeBottleneckDisplay(
  backendMetrics: RuntimeMetricsSummary | null | undefined
): DataPanelComputeBottleneckDisplay | null {
  const resource = metricString(backendMetrics, "compute_resource_bottleneck_resource");
  const label = metricString(backendMetrics, "compute_resource_bottleneck_label");
  if (!resource || resource === "none" || !label) {
    return null;
  }
  const utilization =
    metricNumber(backendMetrics, "compute_resource_bottleneck_utilization") ?? 0;
  const used = metricNumber(backendMetrics, "compute_resource_bottleneck_used") ?? 0;
  const total = metricNumber(backendMetrics, "compute_resource_bottleneck_total") ?? 0;
  const available =
    metricNumber(backendMetrics, "compute_resource_bottleneck_available") ?? 0;
  const status = metricString(backendMetrics, "compute_resource_bottleneck_status");
  return {
    label,
    utilizationLabel: formatRatioPercent(clampRatio(utilization)),
    statusLabel: formatComputeBottleneckStatus(status),
    detailLabel: `已用 ${formatMetricValue(used)} / 总量 ${formatMetricValue(
      total
    )}，可用 ${formatMetricValue(available)}`
  };
}

export function buildComputeResourcePoolFromRuntime(
  snapshot: WorldSnapshot,
  backendMetrics: RuntimeMetricsSummary | null | undefined = undefined,
  backendKpiTimeSeries: RuntimeKpiTimeSeriesV1 | null | undefined = undefined
): ComputeResourcePool {
  return buildComputeResourcePool(
    snapshot,
    metricsWithRuntimeKpiTail(backendMetrics, backendKpiTimeSeries)
  );
}

export function buildRuntimeKpiTelemetrySamples(
  backendKpiTimeSeries: RuntimeKpiTimeSeriesV1 | null | undefined,
  displaySimTime: number
): readonly RuntimeKpiSampleV1[] {
  const samples = backendKpiTimeSeries?.samples ?? [];
  if (samples.length === 0) {
    return [];
  }
  const tail = samples[samples.length - 1];
  const boundedDisplayTime = Math.max(0, displaySimTime);
  if (
    !Number.isFinite(boundedDisplayTime) ||
    boundedDisplayTime <= tail.sim_time
  ) {
    return samples.slice(-24);
  }
  return [...samples.slice(-23), { ...tail, sim_time: boundedDisplayTime }];
}

function metricsWithRuntimeKpiTail(
  backendMetrics: RuntimeMetricsSummary | null | undefined,
  backendKpiTimeSeries: RuntimeKpiTimeSeriesV1 | null | undefined
): RuntimeMetricsSummary | null | undefined {
  const tail = backendKpiTimeSeries?.samples.at(-1);
  if (tail === undefined) {
    return backendMetrics;
  }
  const merged: RuntimeMetricsSummary = { ...(backendMetrics ?? {}) };
  mergeUsedMetric(
    merged,
    "compute_resource_used_gflops_fp32",
    "compute_resource_total_gflops_fp32",
    "compute_resource_available_gflops_fp32",
    tail.compute_resource_used_gflops_fp32
  );
  mergeUsedMetric(
    merged,
    "compute_resource_used_gflops_fp64",
    "compute_resource_total_gflops_fp64",
    "compute_resource_available_gflops_fp64",
    tail.compute_resource_used_gflops_fp64
  );
  mergeUsedMetric(
    merged,
    "compute_resource_used_gpu_tflops_fp32",
    "compute_resource_total_gpu_tflops_fp32",
    "compute_resource_available_gpu_tflops_fp32",
    tail.compute_resource_used_gpu_tflops_fp32
  );
  mergeUsedMetric(
    merged,
    "compute_resource_used_gpu_tflops_fp16",
    "compute_resource_total_gpu_tflops_fp16",
    "compute_resource_available_gpu_tflops_fp16",
    tail.compute_resource_used_gpu_tflops_fp16
  );
  mergeUsedMetric(
    merged,
    "compute_resource_used_npu_tops_int8",
    "compute_resource_total_npu_tops_int8",
    "compute_resource_available_npu_tops_int8",
    tail.compute_resource_used_npu_tops_int8
  );
  mergeUsedMetric(
    merged,
    "compute_resource_used_memory_gb",
    "compute_resource_total_memory_gb",
    "compute_resource_available_memory_gb",
    tail.compute_resource_used_memory_gb
  );
  mergeUsedMetric(
    merged,
    "compute_resource_used_storage_gb",
    "compute_resource_total_storage_gb",
    "compute_resource_available_storage_gb",
    tail.compute_resource_used_storage_gb
  );
  return merged;
}

function mergeUsedMetric(
  metrics: RuntimeMetricsSummary,
  usedKey: string,
  totalKey: string,
  availableKey: string,
  usedValue: number | undefined
): void {
  if (usedValue === undefined || !Number.isFinite(usedValue)) {
    return;
  }
  const used = Math.max(0, usedValue);
  metrics[usedKey] = used;
  const total = metricNumber(metrics, totalKey);
  if (total !== undefined) {
    metrics[availableKey] = Math.max(0, total - used);
  }
}

function computeVectorTailItem(
  label: string,
  value: number | undefined,
  unit: string
): DataPanelComputeVectorTailItem | null {
  if (value === undefined || !Number.isFinite(value)) {
    return null;
  }
  return {
    label,
    value: `${formatMetricValue(Math.max(0, value))} ${unit}`
  };
}

export function resolveNetworkQualityKpis(
  snapshot: WorldSnapshot,
  backendMetrics: RuntimeMetricsSummary | null | undefined = undefined
): NetworkQualityKpis {
  const activeLinks = snapshot.links.filter((link) => link.availability);
  const linkLatencies = activeLinks.map((link) => link.latency);
  const backendThroughput = metricNumber(
    backendMetrics,
    "network_quality_effective_throughput_mbps"
  ) ?? metricNumber(
    backendMetrics,
    "network_quality_estimated_delivered_throughput_mbps"
  );
  const backendAvailableThroughput = metricNumber(
    backendMetrics,
    "network_quality_estimated_available_throughput_mbps"
  );
  const backendOfferedThroughput = metricNumber(
    backendMetrics,
    "network_quality_offered_route_capacity_mbps"
  );
  const backendLatencySeconds = metricNumber(
    backendMetrics,
    "network_quality_effective_latency_avg_s"
  ) ?? metricNumber(
    backendMetrics,
    "network_quality_route_latency_avg_s"
  );
  const backendLossRate = metricNumber(
    backendMetrics,
    "network_quality_effective_loss_proxy_rate"
  ) ?? metricNumber(
    backendMetrics,
    "network_quality_loss_proxy_rate"
  );
  const backendJitterSeconds = metricNumber(
    backendMetrics,
    "network_quality_effective_delay_variation_proxy_s"
  ) ?? metricNumber(
    backendMetrics,
    "network_quality_delay_variation_proxy_s"
  );
  const snapshotThroughput =
    snapshot.metrics_summary.network.throughput ||
    activeLinks.reduce((total, link) => total + link.capacity, 0);
  const throughputMbps =
    positiveMetric(backendThroughput) ??
    backendAvailableThroughput ??
    backendOfferedThroughput ??
    snapshotThroughput;
  const latencyMs =
    backendLatencySeconds !== undefined
      ? backendLatencySeconds * 1000
      : snapshot.metrics_summary.network.latency || average(linkLatencies);
  const lossPercent = (backendLossRate ?? resolveTransportLossRate(snapshot)) * 100;
  const jitterMs =
    backendJitterSeconds !== undefined
      ? backendJitterSeconds * 1000
      : standardDeviation(linkLatencies) || latencyMs * 0.08;
  return {
    source: buildDataPanelNetworkKpiSource(snapshot, backendMetrics).sourceLabel,
    throughputMbps: roundMetric(throughputMbps),
    latencyMs: roundMetric(latencyMs),
    lossPercent: roundMetric(lossPercent),
    jitterMs: roundMetric(jitterMs)
  };
}

export function buildComputeResourcePool(
  snapshot: WorldSnapshot,
  backendMetrics: RuntimeMetricsSummary | null | undefined = undefined
): ComputeResourcePool {
  const total =
    metricNumber(backendMetrics, "compute_resource_total_gflops_fp32") ??
    snapshot.compute_nodes.reduce((sum, node) => sum + Math.max(0, node.capacity), 0);
  const snapshotUsed = snapshot.compute_nodes.reduce((sum, node) => {
    const capacity = Math.max(0, node.capacity);
    const available = Math.max(0, Math.min(capacity, node.available_capacity));
    return sum + Math.max(0, capacity - available);
  }, 0);
  const used = Math.max(
    0,
    metricNumber(backendMetrics, "compute_resource_used_gflops_fp32") ?? snapshotUsed
  );
  const available = Math.max(
    0,
    metricNumber(backendMetrics, "compute_resource_available_gflops_fp32") ??
      total - used
  );
  const usedPercent = total <= 0 ? 0 : (used / total) * 100;

  return {
    totalTflops: roundMetric(total),
    usedTflops: roundMetric(used),
    availableTflops: roundMetric(available),
    usedPercent: roundMetric(usedPercent),
    vectorSummary: buildComputeResourceVectorPoolSummary(snapshot, backendMetrics),
    slices: [
      {
        name: "已消耗 FP32",
        value: roundMetric(used),
        color: "#f2bd45"
      },
      {
        name: "可用 FP32",
        value: roundMetric(available),
        color: "#4fd37a"
      }
    ]
  };
}

export function buildComputeResourcePoolModeNote(pool: ComputeResourcePool): string {
  if (pool.vectorSummary.utilizationMode === "RESOURCE_VECTOR_ESTIMATED") {
    return "后端资源向量：CPU FP32/FP64、GPU FP32/FP16、NPU INT8、内存、存储。";
  }
  return "兼容模式：FP32 主容量来自旧标量；其他资源向量来自节点快照或默认值。";
}

export function buildTopComputeNodeRows(
  snapshot: WorldSnapshot,
  backendSlices: RuntimeSatelliteKpiSlicesV1 | null | undefined = undefined,
  limit = 5
): readonly TopComputeNodeRow[] {
  const backendRows = (backendSlices?.slices ?? []).map((slice) => {
    const node = snapshot.compute_nodes.find((item) => item.node_id === slice.satellite_id);
    const capacity = Math.max(0, finiteMetric(slice.compute_capacity_gflops_fp32));
    const usedFp32 = Math.max(0, finiteMetric(slice.compute_used_gflops_fp32));
    const loadRatio = clampRatio(finiteMetric(slice.compute_load_ratio));
    return {
      nodeId: slice.satellite_id,
      statusLabel: node?.status ?? "BACKEND_SLICE",
      loadPercent: roundMetric(loadRatio * 100),
      usedFp32Gflops: roundMetric(usedFp32),
      runningTasks: Math.max(0, slice.running_task_count),
      loadLabel: `${formatMetricValue(loadRatio * 100)}%`,
      fp32Label: `${formatMetricValue(usedFp32)} / ${formatMetricValue(
        capacity
      )} GFLOPS`,
      taskLabel: `${Math.max(0, slice.running_task_count)} 运行 / ${Math.max(
        0,
        slice.finished_task_count
      )} 完成`
    };
  });
  const sourceRows =
    backendRows.length > 0 ? backendRows : buildSnapshotTopComputeNodeRows(snapshot);
  return Array.from(sourceRows)
    .sort(compareTopComputeNodeRows)
    .slice(0, Math.max(0, limit));
}

export function buildUserBusinessRequestRows(
  snapshot: WorldSnapshot,
  serviceHistory: RuntimeServiceLatencyHistoryV1 | null | undefined = undefined,
  backendSummary: RuntimeUserRequestSummaryV1 | null | undefined = undefined,
  limit = 1000
): UserBusinessRequestRows {
  if (backendSummary?.items?.length) {
    return mergeUserBusinessRequestRows(
      buildBackendUserBusinessRequestRows(backendSummary, limit),
      buildSnapshotUserBusinessRequestRows(snapshot, serviceHistory, limit),
      limit
    );
  }
  return buildSnapshotUserBusinessRequestRows(snapshot, serviceHistory, limit);
}

function buildSnapshotUserBusinessRequestRows(
  snapshot: WorldSnapshot,
  serviceHistory: RuntimeServiceLatencyHistoryV1 | null | undefined = undefined,
  limit = 1000
): UserBusinessRequestRows {
  const serviceLookup = buildServiceFlowLookup(serviceHistory);
  const placementLookup = buildServicePlacementLookup(serviceHistory);
  const routesByUser = buildRoutesByUser(snapshot.routes);
  const userIds = Array.from(
    new Set([
      ...snapshot.ground_users.map((user) => user.user_id),
      ...Array.from(routesByUser.keys())
    ])
  ).sort(compareEntityId);
  const groundUserById = new Map(snapshot.ground_users.map((user) => [user.user_id, user]));
  const items = userIds.slice(0, Math.max(0, limit)).map((userId) => {
    const user = groundUserById.get(userId);
    const routes = (routesByUser.get(userId) ?? []).slice().sort(compareUserBusinessRoute);
    const availableRoutes = routes.filter((route) => route.available);
    const computeRoutes = routes.filter((route) => routeIsComputeService(route, serviceLookup));
    const waitingRoutes = routes.filter((route) => !route.available);
    const selectedRoute = selectUserPrimaryRoute(routes, serviceLookup);
    const routeId = selectedRoute?.route_id ?? "";
    const flowId = selectedRoute?.flow_id ?? "";
    const taskId = "";
    const computeNodeId = "";
    const nextHopId = selectedRoute?.path[1] ?? "";
    const requestId = flowId;
    const serviceRequestId = flowId;
    const correlationLabel = userBusinessRequestCorrelationLabel({
      requestId,
      serviceRequestId,
      routeId,
      flowId,
      taskId,
      computeNodeId,
      nextHopId
    });
    const selectedSatelliteId = selectedRoute ? routeFirstSatellite(selectedRoute) : null;
    const destinationId = selectedRoute?.path[selectedRoute.path.length - 1] ?? "未选择";
    const serviceLabel =
      selectedRoute !== null
        ? serviceLookup.get(selectedRoute.flow_id) ?? selectedRoute.flow_id
        : "无业务";
    const placementLabel =
      selectedRoute !== null
        ? placementLookup.get(selectedRoute.flow_id) ?? "无计算放置"
        : "无计算放置";
    const latencyCapacityLabel =
      selectedRoute !== null
        ? `${formatPreciseMetricValue(selectedRoute.latency)} s / ${formatMetricValue(
            selectedRoute.capacity
          )} Mbps`
        : "无链路";
    return {
      rowId: userBusinessRequestRowId(userId, requestId, routeId, flowId),
      userId,
      requestId,
      serviceRequestId,
      routeId,
      flowId,
      taskId,
      computeNodeId,
      nextHopId,
      platformTypeLabel: userPlatformTypeLabel(user),
      communicationLabel:
        routes.length > 0
          ? `${formatCount(availableRoutes.length)} / ${formatCount(routes.length)} 条`
          : "无通信业务",
      computeLabel:
        computeRoutes.length > 0 ? `${formatCount(computeRoutes.length)} 条计算业务` : "无计算业务",
      networkQueueLabel:
        waitingRoutes.length > 0 ? `${formatCount(waitingRoutes.length)} 条等待` : "队列空",
      selectedSatelliteId: selectedSatelliteId ?? "未选择",
      destinationId,
      placementLabel,
      statusLabel: userRouteStatusLabel(user?.status, routes, availableRoutes),
      latencyCapacityLabel,
      serviceLabel,
      pathLabel:
        selectedRoute !== null && selectedRoute.path.length > 0
          ? `${selectedRoute.route_id}: ${selectedRoute.path.join(" -> ")}`
          : `${userId}: no active route`,
      correlationLabel
    };
  });
  const hiddenCount = Math.max(0, userIds.length - items.length);
  const usersWithTraffic = items.filter((row) => row.communicationLabel !== "无通信业务").length;
  const usersWithCompute = items.filter((row) => row.computeLabel !== "无计算业务").length;
  return {
    sourceLabel: serviceHistory?.items?.length
      ? "快照用户/路由 + 后端服务延迟历史"
      : "快照用户/路由",
    summaryLabel: `${formatCount(items.length)} 个用户节点 / 通信 ${formatCount(
      usersWithTraffic
    )} / 计算 ${formatCount(usersWithCompute)}${
      hiddenCount > 0 ? ` / 另有 ${formatCount(hiddenCount)} 个未显示` : ""
    }`,
    items
  };
}

export function buildDataPanelUserRequestHistory(
  history: RuntimeUserRequestHistoryV1 | null | undefined,
  selectedUserId: string | null | undefined = undefined,
  sampleLimit = 24
): DataPanelUserRequestHistory {
  const orderedSeries = (history?.series ?? [])
    .filter((series) => series.samples.length > 0)
    .slice()
    .sort((left, right) =>
      left.user_id.localeCompare(right.user_id, "zh-CN", { numeric: true })
    );
  if (orderedSeries.length === 0) {
    return {
      sourceLabel: "等待后端 user_request_history_v1",
      summaryLabel: "暂无用户业务历史",
      selectedUserId: null,
      availableUserIds: [],
      points: []
    };
  }

  const availableUserIds = orderedSeries.map((series) => series.user_id);
  const requestedId = selectedUserId ?? "";
  const selectedSeries =
    orderedSeries.find((series) => series.user_id === requestedId) ?? orderedSeries[0];
  const normalizedLimit = Math.max(1, Math.floor(sampleLimit));
  const points = selectedSeries.samples.slice(-normalizedLimit).map((sample) => ({
    timeLabel: formatDurationCompact(sample.sim_time),
    simTime: roundMetric(sample.sim_time),
    communicationRouteCount: Math.max(
      0,
      Math.round(finiteMetric(sample.communication_route_count))
    ),
    availableRouteCount: Math.max(
      0,
      Math.round(finiteMetric(sample.available_route_count))
    ),
    computeServiceCount: Math.max(
      0,
      Math.round(finiteMetric(sample.compute_service_count))
    ),
    networkQueueCount: Math.max(
      0,
      Math.round(finiteMetric(sample.network_queue_count))
    ),
    latencyMs: roundMetric(finiteOptionalMetric(sample.latency_s, 0) * 1000),
    capacityMbps: roundMetric(finiteOptionalMetric(sample.capacity_mbps, 0)),
    lossPercent: roundMetric(finiteOptionalMetric(sample.loss_proxy_rate, 0) * 100),
    selectedSatelliteId: sample.selected_satellite_id || "未选择",
    destinationId: sample.destination_id || "未声明",
    statusLabel: sample.status || "UNKNOWN",
    primaryRouteId: sample.primary_route_id || "none",
    primaryFlowId: sample.primary_flow_id || "none",
    serviceLabel: sample.service_state || "无服务状态"
  }));

  return {
    sourceLabel: "后端 user_request_history_v1",
    summaryLabel: userRequestHistorySummaryLabel(
      selectedSeries.user_id,
      points.length,
      history
    ),
    selectedUserId: selectedSeries.user_id,
    availableUserIds,
    points
  };
}

function userRequestHistorySummaryLabel(
  selectedUserId: string,
  pointCount: number,
  history: RuntimeUserRequestHistoryV1 | null | undefined
): string {
  const parts = [
    selectedUserId,
    `${formatCount(pointCount)} 个样本`,
    history?.mode ?? "UNKNOWN"
  ];
  if (history?.history_scope === "STATUS_POLL_SAMPLED_VISIBLE_USERS") {
    parts.push("状态轮询采样");
  }
  if (
    typeof history?.hidden_user_count === "number" &&
    Number.isFinite(history.hidden_user_count) &&
    history.hidden_user_count > 0
  ) {
    parts.push(`${formatCount(history.hidden_user_count)} 个用户未进入历史窗口`);
  }
  if (
    typeof history?.sample_limit === "number" &&
    Number.isFinite(history.sample_limit)
  ) {
    parts.push(`单用户上限 ${formatCount(history.sample_limit)} 点`);
  }
  return parts.join(" / ");
}

export function buildSatelliteResourceRows(
  snapshot: WorldSnapshot,
  backendSlices: RuntimeSatelliteKpiSlicesV1 | null | undefined = undefined,
  backendSummary: RuntimeSatelliteServiceSummaryV1 | null | undefined = undefined,
  limit = 1500
): SatelliteResourceRows {
  if (backendSummary?.items?.length) {
    return mergeSatelliteResourceRows(
      buildBackendSatelliteResourceRows(backendSummary, limit),
      buildSnapshotSatelliteResourceRows(snapshot, backendSlices, limit),
      limit
    );
  }
  return buildSnapshotSatelliteResourceRows(snapshot, backendSlices, limit);
}

function buildSnapshotSatelliteResourceRows(
  snapshot: WorldSnapshot,
  backendSlices: RuntimeSatelliteKpiSlicesV1 | null | undefined = undefined,
  limit = 1500
): SatelliteResourceRows {
  const satelliteById = new Map(snapshot.satellites.map((satellite) => [satellite.satellite_id, satellite]));
  const nodeById = new Map(snapshot.compute_nodes.map((node) => [node.node_id, node]));
  const sliceById = new Map(
    (backendSlices?.slices ?? []).map((slice) => [slice.satellite_id, slice])
  );
  const networkById = buildSatelliteNetworkFallbacks(snapshot);
  const routeContextBySatellite = buildSatelliteRouteContexts(snapshot.routes);
  const satelliteIds = Array.from(
    new Set([
      ...snapshot.satellites.map((satellite) => satellite.satellite_id),
      ...snapshot.compute_nodes.map((node) => node.node_id),
      ...(backendSlices?.slices ?? []).map((slice) => slice.satellite_id)
    ])
  ).sort(compareEntityId);
  const items = satelliteIds.slice(0, Math.max(0, limit)).map((satelliteId) => {
    const satellite = satelliteById.get(satelliteId);
    const node = nodeById.get(satelliteId);
    const slice = sliceById.get(satelliteId);
    const network = networkById.get(satelliteId);
    const routeContext = routeContextBySatellite.get(satelliteId);
    const cpuFp32Capacity = Math.max(
      0,
      finiteOptionalMetric(slice?.compute_capacity_gflops_fp32, node?.capacity)
    );
    const cpuFp32Used = Math.max(
      0,
      finiteOptionalMetric(
        slice?.compute_used_gflops_fp32,
        node?.used_cpu_gflops_fp32,
        cpuFp32Capacity - finiteOptionalMetric(node?.available_capacity, cpuFp32Capacity)
      )
    );
    const loadRatio = clampRatio(
      finiteOptionalMetric(
        slice?.compute_load_ratio,
        node?.load_ratio,
        cpuFp32Capacity > 0 ? cpuFp32Used / cpuFp32Capacity : 0
      )
    );
    const runningTasks = Math.max(
      0,
      Math.round(finiteOptionalMetric(slice?.running_task_count, node?.running_tasks, 0))
    );
    const finishedTasks = Math.max(
      0,
      Math.round(finiteOptionalMetric(slice?.finished_task_count, node?.finished_tasks, 0))
    );
    return {
      satelliteId,
      statusLabel: node?.status ?? satellite?.status ?? "ACTIVE",
      loadPercent: roundMetric(loadRatio * 100),
      loadLabel: `${formatMetricValue(loadRatio * 100)}%`,
      serviceObjectLabel: routeContext?.serviceObjectLabel ?? "无服务对象",
      nextHopLabel: routeContext?.nextHopLabel ?? "无下一跳",
      cpuFp32Label: resourceUsageLabel(cpuFp32Used, cpuFp32Capacity, "GFLOPS"),
      cpuFp64Label: resourceUsageLabel(
        finiteOptionalMetric(slice?.compute_used_gflops_fp64, node?.used_cpu_gflops_fp64, 0),
        finiteOptionalMetric(slice?.compute_capacity_gflops_fp64, node?.cpu_gflops_fp64, 0),
        "GFLOPS"
      ),
      gpuLabel: `FP32 ${resourceUsageLabel(
        finiteOptionalMetric(slice?.compute_used_gpu_tflops_fp32, node?.used_gpu_tflops_fp32, 0),
        finiteOptionalMetric(slice?.compute_capacity_gpu_tflops_fp32, node?.gpu_tflops_fp32, 0),
        "TFLOPS"
      )} / FP16 ${resourceUsageLabel(
        finiteOptionalMetric(slice?.compute_used_gpu_tflops_fp16, node?.used_gpu_tflops_fp16, 0),
        finiteOptionalMetric(slice?.compute_capacity_gpu_tflops_fp16, node?.gpu_tflops_fp16, 0),
        "TFLOPS"
      )}`,
      npuLabel: resourceUsageLabel(
        finiteOptionalMetric(slice?.compute_used_npu_tops_int8, node?.used_npu_tops_int8, 0),
        finiteOptionalMetric(slice?.compute_capacity_npu_tops_int8, node?.npu_tops_int8, 0),
        "TOPS"
      ),
      memoryStorageLabel: `内存 ${resourceUsageLabel(
        finiteOptionalMetric(slice?.compute_used_memory_gb, node?.used_memory_gb, 0),
        finiteOptionalMetric(slice?.compute_capacity_memory_gb, node?.memory_gb, 0),
        "GB"
      )} / 存储 ${resourceUsageLabel(
        finiteOptionalMetric(slice?.compute_used_storage_gb, node?.used_storage_gb, 0),
        finiteOptionalMetric(slice?.compute_capacity_storage_gb, node?.storage_gb, 0),
        "GB"
      )}`,
      taskLabel: `${runningTasks} 运行 / ${finishedTasks} 完成`,
      networkLabel: satelliteNetworkLabel(slice, network)
    };
  });
  const hiddenCount = Math.max(0, satelliteIds.length - items.length);
  return {
    sourceLabel: backendSlices?.slices?.length
      ? "后端卫星KPI切片 + 快照算力节点"
      : "快照算力节点",
    summaryLabel: `${formatCount(items.length)} / ${formatCount(
      satelliteIds.length
    )} 颗卫星${hiddenCount > 0 ? ` / 另有 ${formatCount(hiddenCount)} 颗未显示` : ""}`,
    items
  };
}

export function buildDataPanelSatelliteResourceHistory(
  history: RuntimeSatelliteKpiHistoryV1 | null | undefined,
  selectedSatelliteId: string | null | undefined = undefined,
  sampleLimit = 24
): DataPanelSatelliteResourceHistory {
  const orderedSeries = (history?.series ?? [])
    .filter((series) => series.samples.length > 0)
    .slice()
    .sort((left, right) =>
      left.satellite_id.localeCompare(right.satellite_id, "zh-CN", { numeric: true })
    );
  if (orderedSeries.length === 0) {
    return {
      sourceLabel: "等待后端 satellite_kpi_history_v1",
      summaryLabel: "暂无单星资源历史",
      selectedSatelliteId: null,
      availableSatelliteIds: [],
      points: []
    };
  }

  const availableSatelliteIds = orderedSeries.map((series) => series.satellite_id);
  const requestedId = selectedSatelliteId ?? "";
  const selectedSeries =
    orderedSeries.find((series) => series.satellite_id === requestedId) ?? orderedSeries[0];
  const normalizedLimit = Math.max(1, Math.floor(sampleLimit));
  const points = selectedSeries.samples.slice(-normalizedLimit).map((sample) => ({
    timeLabel: formatDurationCompact(sample.sim_time),
    simTime: roundMetric(sample.sim_time),
    loadPercent: roundMetric(clampRatio(finiteMetric(sample.compute_load_ratio)) * 100),
    usedFp32Gflops: roundMetric(finiteOptionalMetric(sample.compute_used_gflops_fp32, 0)),
    usedFp64Gflops: roundMetric(finiteOptionalMetric(sample.compute_used_gflops_fp64, 0)),
    usedGpuFp32Tflops: roundMetric(
      finiteOptionalMetric(sample.compute_used_gpu_tflops_fp32, 0)
    ),
    usedGpuFp16Tflops: roundMetric(
      finiteOptionalMetric(sample.compute_used_gpu_tflops_fp16, 0)
    ),
    usedNpuInt8Tops: roundMetric(finiteOptionalMetric(sample.compute_used_npu_tops_int8, 0)),
    usedMemoryGb: roundMetric(finiteOptionalMetric(sample.compute_used_memory_gb, 0)),
    usedStorageGb: roundMetric(finiteOptionalMetric(sample.compute_used_storage_gb, 0))
  }));

  return {
    sourceLabel: "后端 satellite_kpi_history_v1",
    summaryLabel: `${selectedSeries.satellite_id} / ${formatCount(points.length)} 个样本 / ${
      history?.mode ?? "UNKNOWN"
    }`,
    selectedSatelliteId: selectedSeries.satellite_id,
    availableSatelliteIds,
    points
  };
}

export function buildDataPanelDetailScopeNotes(
  userRows: UserBusinessRequestRows,
  satelliteRows: SatelliteResourceRows,
  userSummary: RuntimeUserRequestSummaryV1 | null | undefined = undefined,
  satelliteSummary: RuntimeSatelliteServiceSummaryV1 | null | undefined = undefined,
  satelliteKpiSlices: RuntimeSatelliteKpiSlicesV1 | null | undefined = undefined,
  satelliteKpiHistory: RuntimeSatelliteKpiHistoryV1 | null | undefined = undefined
): readonly DataPanelDetailScopeNote[] {
  const notes: DataPanelDetailScopeNote[] = [];
  if (userSummary !== null && userSummary !== undefined) {
    const hiddenUsers = Math.max(0, userSummary.hidden_user_count);
    const backendItems = Math.max(
      0,
      userSummary.window_user_count ?? userSummary.item_count
    );
    const totalUsers = Math.max(0, userSummary.user_count);
    const fullCountDetail = `全量活跃 ${formatCount(
      userSummary.active_user_count
    )} / 算力业务 ${formatCount(
      userSummary.compute_service_user_count
    )} / 排队 ${formatCount(userSummary.waiting_user_count)}。`;
    notes.push({
      label: "用户明细",
      value: `${formatCount(userRows.items.length)} / ${formatCount(totalUsers)} 行`,
      detail:
        hiddenUsers > 0
          ? `${fullCountDetail} 后端窗口返回 ${formatCount(backendItems)} 行，隐藏 ${formatCount(
              hiddenUsers
            )} 行；表格已用快照补齐可见用户。`
          : `${fullCountDetail} 后端摘要覆盖 ${formatCount(backendItems)} 个用户节点。`,
      tone: hiddenUsers > 0 ? "limit" : "backend"
    });
  }
  if (satelliteSummary !== null && satelliteSummary !== undefined) {
    const hiddenSatellites = Math.max(0, satelliteSummary.hidden_satellite_count);
    const backendItems = Math.max(
      0,
      satelliteSummary.window_satellite_count ?? satelliteSummary.item_count
    );
    const totalSatellites = Math.max(0, satelliteSummary.satellite_count);
    notes.push({
      label: "卫星明细",
      value: `${formatCount(satelliteRows.items.length)} / ${formatCount(
        totalSatellites
      )} 行`,
      detail:
        hiddenSatellites > 0
          ? `后端窗口返回 ${formatCount(backendItems)} 行，隐藏 ${formatCount(
              hiddenSatellites
            )} 行；表格已用快照补齐卫星与算力节点。`
          : `后端服务摘要覆盖 ${formatCount(backendItems)} 颗卫星。`,
      tone: hiddenSatellites > 0 ? "limit" : "backend"
    });
  }
  if (satelliteKpiSlices !== null && satelliteKpiSlices !== undefined) {
    const sliceCount = Math.max(
      0,
      satelliteKpiSlices.slice_count ?? satelliteKpiSlices.slices.length
    );
    const satelliteCount = Math.max(0, satelliteKpiSlices.satellite_count ?? sliceCount);
    const sliceLimit = satelliteKpiSlices.slice_limit;
    const limitNote =
      typeof sliceLimit === "number" && Number.isFinite(sliceLimit)
        ? `，上限 ${formatCount(sliceLimit)}`
        : "";
    notes.push({
      label: "卫星KPI切片",
      value: `${formatCount(sliceCount)} / ${formatCount(satelliteCount)} 切片`,
      detail: `后端 ${satelliteKpiSlices.mode}${limitNote}；用于高负载榜和资源补充，不等同于全量卫星明细。`,
      tone: satelliteCount > sliceCount ? "limit" : "backend"
    });
  }
  if (satelliteKpiHistory !== null && satelliteKpiHistory !== undefined) {
    const seriesCount = Math.max(
      0,
      satelliteKpiHistory.series_count ?? satelliteKpiHistory.series.length
    );
    const satelliteCount = Math.max(
      0,
      satelliteKpiHistory.satellite_count ?? seriesCount
    );
    const sliceLimit = satelliteKpiHistory.slice_limit;
    const sampleLimit = satelliteKpiHistory.sample_limit;
    const parts = [
      typeof sliceLimit === "number" && Number.isFinite(sliceLimit)
        ? `卫星上限 ${formatCount(sliceLimit)}`
        : null,
      typeof sampleLimit === "number" && Number.isFinite(sampleLimit)
        ? `单星样本上限 ${formatCount(sampleLimit)}`
        : null
    ].filter((part): part is string => part !== null);
    notes.push({
      label: "单星历史",
      value: `${formatCount(seriesCount)} / ${formatCount(satelliteCount)} 条序列`,
      detail: `后端 ${satelliteKpiHistory.mode}${
        parts.length > 0 ? `，${parts.join(" / ")}` : ""
      }；历史曲线是代表性窗口，不代表每颗卫星都有历史曲线。`,
      tone: satelliteCount > seriesCount ? "history" : "backend"
    });
  }
  if (notes.length > 0) {
    return notes;
  }
  return [
    {
      label: "明细来源",
      value: "等待后端摘要",
      detail: "暂时使用快照回退行，后端 runtime observability 到达后会显示覆盖范围。",
      tone: "history"
    }
  ];
}

export function buildDataPanelFilterScopeNotes(
  userSummary: RuntimeUserRequestSummaryV1 | null | undefined = undefined,
  satelliteSummary: RuntimeSatelliteServiceSummaryV1 | null | undefined = undefined,
  routeSummary: RuntimeRouteExplanationSummaryV1 | null | undefined = undefined
): readonly DataPanelDetailScopeNote[] {
  const cursorScopes = [
    backendCursorScopeLabel("用户", userSummary, userSummary?.user_count),
    backendCursorScopeLabel("卫星", satelliteSummary, satelliteSummary?.satellite_count),
    backendCursorScopeLabel("路由", routeSummary, routeSummary?.route_count)
  ].filter((scope): scope is string => scope !== null);
  if (cursorScopes.length === 0) {
    return [];
  }
  return [
    {
      label: "筛选作用域",
      value: "当前后端页",
      detail: `${cursorScopes.join(
        "；"
      )}。刷新或翻页会把当前筛选条件发送到后端详情端点；表格仍只渲染当前后端页与本地窗口。`,
      tone: "limit"
    }
  ];
}

function backendCursorScopeLabel(
  label: string,
  summary:
    | RuntimeUserRequestSummaryV1
    | RuntimeSatelliteServiceSummaryV1
    | RuntimeRouteExplanationSummaryV1
    | null
    | undefined,
  totalCount: number | null | undefined
): string | null {
  if (
    summary === null ||
    summary === undefined ||
    summary.cursor === undefined ||
    summary.limit === undefined ||
    summary.next_cursor === undefined ||
    summary.has_more === undefined
  ) {
    return null;
  }
  const display = buildDataPanelBackendCursorDisplay(
    {
      cursor: summary.cursor,
      limit: summary.limit,
      next_cursor: summary.next_cursor,
      has_more: summary.has_more,
      item_count: summary.item_count
    },
    totalCount ?? summary.item_count
  );
  return `${label} ${display.rangeLabel}${display.canNext ? "，可继续翻页" : ""}`;
}

export function buildDataPanelPaginationContractNotes(
  contract: LargeDetailPaginationContractV2 | null | undefined
): readonly DataPanelDetailScopeNote[] {
  if (contract === null || contract === undefined) {
    return [
      {
        label: "后端分页契约",
        value: "兼容模式",
        detail:
          "当前 backend_summary 未提供 large_detail_pagination_contract_v2，表格使用前端兼容窗口。",
        tone: "limit"
      }
    ];
  }
  const collections = detailPaginationCollections(contract);
  const labels = [
    detailPaginationCollectionLabel(collections.get("ground_users"), "用户"),
    detailPaginationCollectionLabel(collections.get("satellites"), "卫星"),
    detailPaginationCollectionLabel(collections.get("routes"), "路由"),
    detailPaginationCollectionLabel(collections.get("services"), "服务"),
    detailPaginationCollectionLabel(collections.get("compute_nodes"), "算力")
  ];
  const hiddenCount = Array.from(collections.values()).reduce(
    (total, collection) => total + Math.max(0, collection.hidden_count_estimate),
    0
  );
  return [
    {
      label: "后端分页契约",
      value: `${contract.active_profile_id} / ${contract.cursor_model.cursor_type}`,
      detail: [
        labels.join("；"),
        `统一上限 ${formatCount(contract.cursor_model.max_limit)}`,
        hiddenCount > 0
          ? `估计隐藏 ${formatCount(hiddenCount)} 行通过后端游标读取`
          : "当前估计规模不需要隐藏行"
      ].join("；"),
      tone: hiddenCount > 0 ? "limit" : "backend"
    }
  ];
}

export function filterUserBusinessRequestRows(
  rows: UserBusinessRequestRows,
  query: string
): UserBusinessRequestRows {
  const normalized = normalizeDetailFilter(query);
  if (normalized.length === 0) {
    return rows;
  }
  const items = rows.items.filter((item) =>
    [
      item.userId,
      item.requestId,
      item.serviceRequestId,
      item.routeId,
      item.flowId,
      item.taskId,
      item.computeNodeId,
      item.nextHopId,
      item.platformTypeLabel,
      item.communicationLabel,
      item.computeLabel,
      item.networkQueueLabel,
      item.selectedSatelliteId,
      item.destinationId,
      item.placementLabel,
      item.statusLabel,
      item.latencyCapacityLabel,
      item.serviceLabel,
      item.pathLabel,
      item.correlationLabel
    ].some((value) => String(value ?? "").toLowerCase().includes(normalized))
  );
  return {
    ...rows,
    summaryLabel: `${rows.summaryLabel} / 筛选 ${formatCount(items.length)}`,
    items
  };
}

export function filterSatelliteResourceRows(
  rows: SatelliteResourceRows,
  query: string
): SatelliteResourceRows {
  const normalized = normalizeDetailFilter(query);
  if (normalized.length === 0) {
    return rows;
  }
  const items = rows.items.filter((item) =>
    [
      item.satelliteId,
      item.statusLabel,
      item.loadLabel,
      item.serviceObjectLabel,
      item.nextHopLabel,
      item.cpuFp32Label,
      item.cpuFp64Label,
      item.gpuLabel,
      item.npuLabel,
      item.memoryStorageLabel,
      item.taskLabel,
      item.networkLabel
    ].some((value) => value.toLowerCase().includes(normalized))
  );
  return {
    ...rows,
    summaryLabel: `${rows.summaryLabel} / 筛选 ${formatCount(items.length)}`,
    items
  };
}

export function selectUserBusinessRequestRow(
  rows: readonly UserBusinessRequestRow[],
  selectedUserId: string | null | undefined
): UserBusinessRequestRow | null {
  return rows.find((row) => row.userId === selectedUserId) ?? rows[0] ?? null;
}

export function selectSatelliteResourceRow(
  rows: readonly SatelliteResourceRow[],
  selectedSatelliteId: string | null | undefined
): SatelliteResourceRow | null {
  return rows.find((row) => row.satelliteId === selectedSatelliteId) ?? rows[0] ?? null;
}

export function selectRouteExplanationRow(
  rows: readonly DataPanelRouteExplanationRow[],
  selectedRouteId: string | null | undefined
): DataPanelRouteExplanationRow | null {
  return rows.find((row) => row.routeId === selectedRouteId) ?? rows[0] ?? null;
}

export function selectServiceDetailRow(
  rows: readonly DataPanelServiceDetailRow[],
  selectedServiceId: string | null | undefined
): DataPanelServiceDetailRow | null {
  return rows.find((row) => row.serviceId === selectedServiceId) ?? rows[0] ?? null;
}

export function selectServiceLifecycleTraceRow(
  rows: readonly DataPanelServiceLifecycleTraceRow[],
  selectedTraceId: string | null | undefined
): DataPanelServiceLifecycleTraceRow | null {
  return (
    rows.find(
      (row) => row.traceId === selectedTraceId || row.serviceId === selectedTraceId
    ) ??
    rows[0] ??
    null
  );
}

export function selectComputeNodeDetailRow(
  rows: readonly DataPanelComputeNodeDetailRow[],
  selectedNodeId: string | null | undefined
): DataPanelComputeNodeDetailRow | null {
  return rows.find((row) => row.nodeId === selectedNodeId) ?? rows[0] ?? null;
}

export function selectExactDetailRequestStatus(
  status: RuntimeExactDetailRequestState | null | undefined,
  selectedEntityId: string | null | undefined
): RuntimeExactDetailRequestState | null {
  if (status === null || status === undefined) {
    return null;
  }
  const statusEntityId = (status.entityId ?? "").trim();
  const selectedId = (selectedEntityId ?? "").trim();
  if (!statusEntityId || statusEntityId !== selectedId) {
    return null;
  }
  return {
    entityId: statusEntityId,
    loading: status.loading === true,
    error: status.error ?? null
  };
}

export function appendExactDetailStatusToInspector(
  inspector: DataPanelDetailInspector,
  status: RuntimeExactDetailRequestState | null | undefined
): DataPanelDetailInspector {
  const field = exactDetailStatusField(status);
  if (field === null) {
    return inspector;
  }
  return {
    ...inspector,
    fields: [field, ...inspector.fields]
  };
}

function exactDetailStatusField(
  status: RuntimeExactDetailRequestState | null | undefined
): DataPanelDetailInspectorField | null {
  if (status === null || status === undefined) {
    return null;
  }
  if (status.loading === true) {
    return {
      label: "精确详情",
      value: "正在读取后端精确详情",
      tone: "resource"
    };
  }
  if (status.error) {
    return {
      label: "精确详情",
      value: status.error,
      tone: "warning"
    };
  }
  if ((status.entityId ?? "").trim()) {
    return {
      label: "精确详情",
      value: "后端精确详情已同步",
      tone: "resource"
    };
  }
  return null;
}

export function selectRuntimeUserDetailCard(
  summary: RuntimeNodeDetailSummaryV1 | null | undefined,
  userId: string | null | undefined
): RuntimeNodeDetailCardV1 | null {
  if (!userId) {
    return null;
  }
  return summary?.users.find((card) => card.entity_id === userId) ?? null;
}

export function selectRuntimeSatelliteDetailCard(
  summary: RuntimeNodeDetailSummaryV1 | null | undefined,
  satelliteId: string | null | undefined
): RuntimeNodeDetailCardV1 | null {
  if (!satelliteId) {
    return null;
  }
  return summary?.satellites.find((card) => card.entity_id === satelliteId) ?? null;
}

export function buildUserBusinessRequestInspector(
  row: UserBusinessRequestRow | null | undefined,
  backendDetailSummary: RuntimeNodeDetailSummaryV1 | null | undefined = undefined,
  backendDetailCard: RuntimeNodeDetailCardV1 | null | undefined = undefined
): DataPanelDetailInspector {
  if (backendDetailCard !== null && backendDetailCard !== undefined) {
    return buildRuntimeNodeDetailInspector(backendDetailCard);
  }
  if (row === null || row === undefined) {
    return {
      title: "用户详情",
      subtitle: "当前窗口暂无用户节点",
      fields: []
    };
  }
  const backendCard = selectRuntimeUserDetailCard(backendDetailSummary, row.userId);
  if (backendCard !== null) {
    return buildRuntimeNodeDetailInspector(backendCard);
  }
  return {
    title: `用户 ${row.userId}`,
    subtitle: row.statusLabel,
    sections: buildUserDetailDrawerSectionsV1(row),
    fields: [
      { label: "平台", value: row.platformTypeLabel },
      { label: "通信", value: row.communicationLabel },
      { label: "计算", value: row.computeLabel, tone: "resource" },
      { label: "网络队列", value: row.networkQueueLabel, tone: "warning" },
      { label: "目标卫星", value: row.selectedSatelliteId },
      { label: "目标节点", value: row.destinationId },
      { label: "服务放置", value: row.placementLabel, tone: "resource" },
      { label: "时延/容量", value: row.latencyCapacityLabel },
      { label: "服务链路", value: row.serviceLabel },
      { label: "路径", value: row.pathLabel }
    ]
  };
}

export function buildUserDetailDrawerSectionsV1(
  row: UserBusinessRequestRow
): readonly DataPanelNodeDetailSection[] {
  return [
    {
      sectionId: "business_request",
      title: "业务请求",
      fields: [
        { label: "用户节点", value: row.userId },
        { label: "平台类型", value: row.platformTypeLabel },
        { label: "活跃业务", value: row.serviceLabel },
        { label: "请求状态", value: row.statusLabel },
        { label: "目标卫星", value: row.selectedSatelliteId },
        { label: "目标节点", value: row.destinationId }
      ]
    },
    {
      sectionId: "network_path_queue",
      title: "网络与队列",
      fields: [
        { label: "通信路由", value: row.communicationLabel },
        {
          label: "网络队列",
          value: row.networkQueueLabel,
          tone: userNetworkQueueTone(row.networkQueueLabel)
        },
        { label: "路径", value: row.pathLabel },
        { label: "时延/容量", value: row.latencyCapacityLabel }
      ]
    },
    {
      sectionId: "compute_service",
      title: "计算服务",
      fields: [
        { label: "计算业务", value: row.computeLabel, tone: "resource" },
        { label: "服务放置", value: row.placementLabel, tone: "resource" }
      ]
    }
  ];
}

function userNetworkQueueTone(
  queueLabel: string
): DataPanelDetailInspectorField["tone"] {
  const normalized = queueLabel.trim().toLowerCase();
  if (
    normalized.length === 0 ||
    normalized === "empty" ||
    normalized === "no network queue"
  ) {
    return "normal";
  }
  return "warning";
}

export function buildSatelliteResourceInspector(
  row: SatelliteResourceRow | null | undefined,
  backendDetailSummary: RuntimeNodeDetailSummaryV1 | null | undefined = undefined,
  backendDetailCard: RuntimeNodeDetailCardV1 | null | undefined = undefined
): DataPanelDetailInspector {
  if (backendDetailCard !== null && backendDetailCard !== undefined) {
    return buildRuntimeNodeDetailInspector(backendDetailCard);
  }
  if (row === null || row === undefined) {
    return {
      title: "卫星详情",
      subtitle: "当前窗口暂无卫星节点",
      fields: []
    };
  }
  const backendCard = selectRuntimeSatelliteDetailCard(
    backendDetailSummary,
    row.satelliteId
  );
  if (backendCard !== null) {
    return buildRuntimeNodeDetailInspector(backendCard);
  }
  return {
    title: `卫星 ${row.satelliteId}`,
    subtitle: row.statusLabel,
    sections: buildSatelliteDetailDrawerSectionsV1(row),
    fields: [
      { label: "负载", value: row.loadLabel, tone: "resource" },
      { label: "服务对象", value: row.serviceObjectLabel },
      { label: "下一跳", value: row.nextHopLabel },
      { label: "CPU FP32", value: row.cpuFp32Label, tone: "resource" },
      { label: "CPU FP64", value: row.cpuFp64Label, tone: "resource" },
      { label: "GPU", value: row.gpuLabel, tone: "resource" },
      { label: "NPU", value: row.npuLabel, tone: "resource" },
      { label: "内存/存储", value: row.memoryStorageLabel, tone: "resource" },
      { label: "任务", value: row.taskLabel },
      { label: "网络", value: row.networkLabel }
    ]
  };
}

export function buildSatelliteDetailDrawerSectionsV1(
  row: SatelliteResourceRow
): readonly DataPanelNodeDetailSection[] {
  return [
    {
      sectionId: "service_routing",
      title: "服务与路由",
      fields: [
        { label: "卫星节点", value: row.satelliteId },
        { label: "运行状态", value: row.statusLabel },
        { label: "服务对象", value: row.serviceObjectLabel },
        { label: "下一跳节点", value: row.nextHopLabel }
      ]
    },
    {
      sectionId: "compute_resource_pool",
      title: "算力资源池",
      fields: [
        { label: "负载", value: row.loadLabel, tone: "resource" },
        { label: "CPU FP32", value: row.cpuFp32Label, tone: "resource" },
        { label: "CPU FP64", value: row.cpuFp64Label, tone: "resource" },
        { label: "GPU", value: row.gpuLabel, tone: "resource" },
        { label: "NPU", value: row.npuLabel, tone: "resource" },
        { label: "内存/存储", value: row.memoryStorageLabel, tone: "resource" }
      ]
    },
    {
      sectionId: "network_task_context",
      title: "网络与任务",
      fields: [
        { label: "任务队列", value: row.taskLabel },
        {
          label: "网络KPI",
          value: row.networkLabel,
          tone: satelliteNetworkContextTone(row.networkLabel)
        }
      ]
    }
  ];
}

function satelliteNetworkContextTone(
  networkLabel: string
): DataPanelDetailInspectorField["tone"] {
  const normalized = networkLabel.trim().toLowerCase();
  if (
    normalized.includes("queued") ||
    normalized.includes("blocked") ||
    normalized.includes("loss") ||
    normalized.includes("不可达")
  ) {
    return "warning";
  }
  return "normal";
}

export function buildRouteExplanationDetailInspector(
  row: DataPanelRouteExplanationRow | null | undefined,
  backendDetail: RuntimeRouteExplanationItemV1 | null | undefined = undefined
): DataPanelDetailInspector {
  if (backendDetail !== null && backendDetail !== undefined) {
    return {
      title: `路由 ${backendDetail.route_id}`,
      subtitle: `${backendDetail.business_label} / ${
        backendDetail.available ? "可用" : "阻塞"
      }`,
      fields: [
        { label: "流", value: backendDetail.flow_id },
        { label: "源/目的", value: `${backendDetail.source_id} -> ${backendDetail.destination_id}` },
        { label: "下一跳", value: backendDetail.primary_next_hop_id || "无" },
        {
          label: "容量/需求",
          value: routeExplanationCapacityDemandLabel(
            backendDetail.capacity_mbps,
            backendDetail.demand_mbps
          )
        },
        {
          label: "时延/损耗",
          value: `${formatMetricMilliseconds(backendDetail.latency_s ?? 0)} / ${formatRatioPercent(
            backendDetail.loss_proxy_rate ?? 0
          )}`,
          tone: backendDetail.available ? "normal" : "warning"
        },
        {
          label: "压力",
          value: formatRatioPercent(Math.max(0, backendDetail.route_pressure_proxy)),
          tone: backendDetail.route_pressure_proxy > 1 ? "warning" : "normal"
        },
        {
          label: "瓶颈",
          value: backendDetail.bottleneck_reason_label,
          tone: backendDetail.bottleneck_component === "NONE" ? "normal" : "warning"
        },
        { label: "路径", value: backendDetail.path_label }
      ]
    };
  }
  if (row === null || row === undefined) {
    return {
      title: "路由详情",
      subtitle: "当前窗口暂无路由",
      fields: []
    };
  }
  return {
    title: `路由 ${row.routeId}`,
    subtitle: `${row.businessLabel} / ${row.availabilityLabel}`,
    fields: [
      { label: "流", value: row.flowId },
      { label: "下一跳", value: row.nextHopLabel },
      { label: "容量/需求", value: row.capacityDemandLabel },
      { label: "压力", value: row.pressureLabel },
      {
        label: "瓶颈",
        value: row.bottleneckLabel,
        tone: row.bottleneckComponent === "NONE" ? "normal" : "warning"
      },
      { label: "解释", value: row.explanationLabel },
      { label: "路径", value: row.pathLabel }
    ]
  };
}

export function buildServiceLifecycleDetailInspector(
  row: DataPanelServiceDetailRow | null | undefined,
  backendDetail: RuntimeServiceDetailItemV1 | null | undefined = undefined
): DataPanelDetailInspector {
  if (backendDetail !== null && backendDetail !== undefined) {
    return {
      title: `服务 ${backendDetail.service_id}`,
      subtitle: backendDetail.service_state_label || backendDetail.service_state,
      fields: [
        { label: "任务", value: backendDetail.task_id || backendDetail.service_id },
        { label: "算力节点", value: backendDetail.compute_node_id || "无" },
        { label: "输入路由", value: backendDetail.input_route_id || "无" },
        { label: "输出路由", value: backendDetail.output_route_id || "无" },
        {
          label: "放置",
          value: serviceDetailPlacementLabel(backendDetail),
          tone: "resource"
        },
        {
          label: "网络",
          value: `${formatMetricMilliseconds(
            backendDetail.input_network_latency_s
          )} / ${formatMetricMilliseconds(backendDetail.output_network_latency_s)}`
        },
        {
          label: "计算",
          value: `${formatMetricMilliseconds(
            backendDetail.compute_queue_delay_s
          )} / ${formatMetricMilliseconds(backendDetail.compute_execution_delay_s)}`,
          tone: backendDetail.compute_queue_delay_s > 0 ? "warning" : "resource"
        },
        {
          label: "总时延",
          value: formatMetricMilliseconds(backendDetail.total_latency_s)
        },
        { label: "阶段数", value: formatCount(backendDetail.stage_count) }
      ]
    };
  }
  if (row === null || row === undefined) {
    return {
      title: "服务详情",
      subtitle: "当前窗口暂无服务",
      fields: []
    };
  }
  return {
    title: `服务 ${row.serviceId}`,
    subtitle: row.stateLabel,
    fields: [
      { label: "任务", value: row.taskLabel },
      { label: "放置", value: row.placementLabel, tone: "resource" },
      { label: "网络", value: row.networkLatencyLabel },
      { label: "计算", value: row.computeLatencyLabel, tone: "resource" },
      { label: "总时延", value: row.totalLatencyLabel }
    ]
  };
}

export function buildServiceTraceCorrelationInspector(
  trace: DataPanelServiceLifecycleTraceRow | null | undefined,
  users: UserBusinessRequestRows,
  routes: DataPanelRouteExplanationRows,
  satellites: SatelliteResourceRows,
  computeNodes: DataPanelComputeNodeDetailRows,
  backendDetail: RuntimeServiceTraceDetailV2 | null | undefined = undefined
): DataPanelDetailInspector {
  if (trace === null || trace === undefined) {
    return {
      title: "服务 trace 关联",
      subtitle: "选择一条 service_lifecycle_trace_v2",
      fields: []
    };
  }
  if (backendDetail !== null && backendDetail !== undefined) {
    const backendTrace = backendDetail.trace;
    const correlation = backendDetail.correlation;
    const computeNodeId =
      backendDetail.compute_node?.node_id ?? correlation.compute_node_id;
    return {
      title: `Service trace ${compactTaskId(correlation.service_id)}`,
      subtitle: serviceLifecycleTerminalLabel(
        backendTrace.terminal_state,
        backendTrace.terminal_state_reason
      ),
      fields: [
        { label: "source", value: "backend exact detail", tone: "resource" },
        { label: "service", value: correlation.service_id },
        { label: "task", value: correlation.task_id || "no task id" },
        {
          label: "flows",
          value:
            correlation.flow_ids.length > 0
              ? correlation.flow_ids.join(" / ")
              : "no flow ids"
        },
        {
          label: "routes",
          value:
            correlation.route_ids.length > 0
              ? correlation.route_ids.join(" / ")
              : "no route ids",
          tone: correlation.route_count > 0 ? "resource" : "warning"
        },
        {
          label: "users",
          value:
            correlation.user_ids.length > 0
              ? correlation.user_ids.join(" / ")
              : "no correlated users",
          tone: correlation.user_count > 0 ? "resource" : "warning"
        },
        {
          label: "satellites",
          value:
            correlation.satellite_ids.length > 0
              ? correlation.satellite_ids.join(" / ")
              : "no correlated satellites",
          tone: correlation.satellite_count > 0 ? "resource" : "warning"
        },
        {
          label: "compute node",
          value: computeNodeId || "not placed",
          tone: computeNodeId ? "resource" : "warning"
        },
        {
          label: "network",
          value: `${formatMetricMilliseconds(
            backendTrace.input_network_latency_s
          )} / ${formatMetricMilliseconds(backendTrace.output_network_latency_s)}`
        },
        {
          label: "compute",
          value: `${formatMetricMilliseconds(
            backendTrace.compute_queue_delay_s
          )} / ${formatMetricMilliseconds(backendTrace.compute_execution_delay_s)}`,
          tone: computeNodeId ? "resource" : "warning"
        },
        {
          label: "total latency",
          value: formatMetricMilliseconds(backendTrace.total_latency_s)
        },
        {
          label: "stages",
          value:
            backendTrace.stages.length > 0
              ? backendTrace.stages
                  .map((stage) => `${stage.stage_label}:${stage.stage_status}`)
                  .join(" / ")
              : "no stage samples"
        }
      ]
    };
  }
  const matchedRoutes = routes.items.filter((route) =>
    routeMatchesServiceTrace(route, trace)
  );
  const matchedUsers = users.items.filter((user) =>
    userMatchesServiceTrace(user, trace, matchedRoutes)
  );
  const matchedSatellites = satellites.items.filter((satellite) =>
    satelliteMatchesServiceTrace(satellite, trace, matchedRoutes, matchedUsers)
  );
  const computeNode =
    computeNodes.items.find((node) => node.nodeId === trace.computeNodeId) ?? null;
  const primaryRoute = matchedRoutes[0] ?? null;
  const primaryUser = matchedUsers[0] ?? null;
  const primarySatellite = matchedSatellites[0] ?? null;
  return {
    title: `服务 trace ${trace.serviceLabel}`,
    subtitle: trace.terminalStateLabel,
    fields: [
      { label: "服务", value: trace.serviceId },
      { label: "任务", value: trace.taskId || "无任务 id" },
      {
        label: "流",
        value: trace.flowIds.length > 0 ? trace.flowIds.join(" / ") : "无流 id"
      },
      {
        label: "路由",
        value:
          matchedRoutes.length > 0
            ? matchedRoutes.map((route) => route.routeId).join(" / ")
            : trace.routeIds.join(" / ") || "无路由",
        tone: matchedRoutes.length > 0 ? "resource" : "warning"
      },
      {
        label: "用户",
        value: primaryUser
          ? `${primaryUser.userId} / ${primaryUser.serviceLabel}`
          : "未在当前用户窗口匹配",
        tone: primaryUser ? "resource" : "warning"
      },
      {
        label: "卫星",
        value: primarySatellite
          ? `${primarySatellite.satelliteId} / ${primarySatellite.loadLabel}`
          : "未在当前卫星窗口匹配",
        tone: primarySatellite ? "resource" : "warning"
      },
      {
        label: "算力节点",
        value: computeNode
          ? `${computeNode.nodeId} / ${computeNode.loadLabel}`
          : trace.computeNodeId || "未放置",
        tone: computeNode || trace.computeNodeId ? "resource" : "warning"
      },
      {
        label: "下一跳",
        value: primaryRoute?.nextHopLabel ?? primarySatellite?.nextHopLabel ?? "未知"
      },
      {
        label: "网络",
        value: trace.networkLatencyLabel
      },
      {
        label: "计算",
        value: trace.computeLatencyLabel,
        tone: trace.computeNodeId ? "resource" : "warning"
      },
      {
        label: "阶段",
        value: trace.stages
          .map((stage) => `${stage.label}:${stage.statusLabel}`)
          .join(" / ")
      }
    ]
  };
}

export function serviceTraceDetailMatchesRow(
  detail: RuntimeServiceTraceDetailV2 | null | undefined,
  row: DataPanelServiceLifecycleTraceRow | null | undefined
): boolean {
  if (detail === null || detail === undefined || row === null || row === undefined) {
    return false;
  }
  const trace = detail.trace;
  const correlation = detail.correlation;
  const detailIds = new Set(
    uniqueStrings([
      trace.trace_id,
      trace.service_id,
      trace.task_id,
      trace.input_flow_id ?? "",
      trace.output_flow_id ?? "",
      trace.input_route_id ?? "",
      trace.output_route_id ?? "",
      trace.compute_node_id ?? "",
      correlation.trace_id,
      correlation.service_id,
      correlation.task_id,
      correlation.compute_node_id,
      ...correlation.flow_ids,
      ...correlation.route_ids
    ])
  );
  const rowIds = uniqueStrings([
    row.traceId,
    row.serviceId,
    row.taskId,
    row.inputFlowId,
    row.outputFlowId,
    row.inputRouteId,
    row.outputRouteId,
    row.computeNodeId,
    row.primaryRouteId,
    ...row.routeIds,
    ...row.flowIds
  ]);
  return rowIds.some((id) => detailIds.has(id));
}

function routeMatchesServiceTrace(
  route: DataPanelRouteExplanationRow,
  trace: DataPanelServiceLifecycleTraceRow
): boolean {
  return (
    trace.routeIds.includes(route.routeId) ||
    trace.flowIds.includes(route.flowId) ||
    traceMatchValues(trace).some((value) =>
      [route.routeId, route.flowId, route.pathLabel].some((candidate) =>
        candidate.includes(value)
      )
    )
  );
}

function userMatchesServiceTrace(
  user: UserBusinessRequestRow,
  trace: DataPanelServiceLifecycleTraceRow,
  matchedRoutes: readonly DataPanelRouteExplanationRow[]
): boolean {
  const routeIds = matchedRoutes.map((route) => route.routeId);
  const flowIds = matchedRoutes.map((route) => route.flowId);
  const candidates = [
    user.serviceLabel,
    user.pathLabel,
    user.selectedSatelliteId,
    user.destinationId,
    ...routeIds,
    ...flowIds
  ];
  return traceMatchValues(trace).some((value) =>
    candidates.some((candidate) => candidate.includes(value))
  );
}

function satelliteMatchesServiceTrace(
  satellite: SatelliteResourceRow,
  trace: DataPanelServiceLifecycleTraceRow,
  matchedRoutes: readonly DataPanelRouteExplanationRow[],
  matchedUsers: readonly UserBusinessRequestRow[]
): boolean {
  if (satellite.satelliteId === trace.computeNodeId) {
    return true;
  }
  const candidates = [
    satellite.satelliteId,
    satellite.serviceObjectLabel,
    satellite.nextHopLabel,
    satellite.taskLabel,
    ...matchedRoutes.map((route) => route.pathLabel),
    ...matchedUsers.map((user) => user.selectedSatelliteId)
  ];
  return traceMatchValues(trace).some((value) =>
    candidates.some((candidate) => candidate.includes(value))
  );
}

function traceMatchValues(trace: DataPanelServiceLifecycleTraceRow): readonly string[] {
  return uniqueStrings([
    trace.serviceId,
    trace.taskId,
    trace.computeNodeId,
    trace.inputFlowId,
    trace.outputFlowId,
    trace.inputRouteId,
    trace.outputRouteId,
    ...trace.routeIds,
    ...trace.flowIds
  ]);
}

export function buildComputeNodeExactDetailInspector(
  row: DataPanelComputeNodeDetailRow | null | undefined,
  backendDetail: RuntimeComputeNodeDetailItemV1 | null | undefined = undefined
): DataPanelDetailInspector {
  if (backendDetail !== null && backendDetail !== undefined) {
    return {
      title: `算力节点 ${backendDetail.node_id}`,
      subtitle: backendDetail.status,
      fields: [
        {
          label: "负载",
          value: formatRatioPercent(backendDetail.compute_load_ratio),
          tone: "resource"
        },
        {
          label: "CPU FP32",
          value: resourceUsageLabel(
            backendDetail.compute_used_gflops_fp32,
            backendDetail.compute_capacity_gflops_fp32,
            "GFLOPS"
          ),
          tone: "resource"
        },
        {
          label: "CPU FP64",
          value: resourceUsageLabel(
            backendDetail.compute_used_gflops_fp64,
            backendDetail.compute_capacity_gflops_fp64,
            "GFLOPS"
          ),
          tone: "resource"
        },
        {
          label: "GPU",
          value: `FP32 ${resourceUsageLabel(
            backendDetail.compute_used_gpu_tflops_fp32,
            backendDetail.compute_capacity_gpu_tflops_fp32,
            "TFLOPS"
          )} / FP16 ${resourceUsageLabel(
            backendDetail.compute_used_gpu_tflops_fp16,
            backendDetail.compute_capacity_gpu_tflops_fp16,
            "TFLOPS"
          )}`,
          tone: "resource"
        },
        {
          label: "NPU",
          value: resourceUsageLabel(
            backendDetail.compute_used_npu_tops_int8,
            backendDetail.compute_capacity_npu_tops_int8,
            "TOPS"
          ),
          tone: "resource"
        },
        {
          label: "内存/存储",
          value: `内存 ${resourceUsageLabel(
            backendDetail.compute_used_memory_gb,
            backendDetail.compute_capacity_memory_gb,
            "GB"
          )} / 存储 ${resourceUsageLabel(
            backendDetail.compute_used_storage_gb,
            backendDetail.compute_capacity_storage_gb,
            "GB"
          )}`,
          tone: "resource"
        },
        {
          label: "任务",
          value: `${formatCount(backendDetail.running_task_count)} 运行 / ${formatCount(
            backendDetail.finished_task_count
          )} 完成`
        }
      ]
    };
  }
  if (row === null || row === undefined) {
    return {
      title: "算力节点详情",
      subtitle: "当前窗口暂无算力节点",
      fields: []
    };
  }
  return {
    title: `算力节点 ${row.nodeId}`,
    subtitle: row.statusLabel,
    fields: [
      { label: "负载", value: row.loadLabel, tone: "resource" },
      { label: "FP32", value: row.fp32Label, tone: "resource" },
      { label: "GPU/NPU", value: row.acceleratorLabel, tone: "resource" },
      { label: "内存/存储", value: row.memoryStorageLabel, tone: "resource" },
      { label: "任务", value: row.taskLabel }
    ]
  };
}

export function buildDataPanelNodeDetailDrawerItems(
  user: DataPanelDetailInspector,
  satellite: DataPanelDetailInspector,
  serviceTrace: DataPanelNodeDetailDrawerItem | null | undefined = undefined
): readonly DataPanelNodeDetailDrawerItem[] {
  const items: DataPanelNodeDetailDrawerItem[] = [
    {
      kind: "user",
      title: user.title,
      subtitle: user.subtitle,
      emptyLabel: "当前窗口暂无选中用户节点",
      sections: user.sections ?? [],
      fields: user.fields
    },
    {
      kind: "satellite",
      title: satellite.title,
      subtitle: satellite.subtitle,
      emptyLabel: "当前窗口暂无选中卫星节点",
      sections: satellite.sections ?? [],
      fields: satellite.fields
    }
  ];
  if (serviceTrace !== null && serviceTrace !== undefined) {
    items.push(serviceTrace);
  }
  return items;
}

export function buildServiceTraceDetailDrawerItem(
  detail: RuntimeServiceTraceDetailV2 | null | undefined,
  fallback: DataPanelDetailInspector
): DataPanelNodeDetailDrawerItem {
  if (detail === null || detail === undefined) {
    return {
      kind: "service_trace",
      title: fallback.title,
      subtitle: fallback.subtitle,
      emptyLabel: "选择一条服务 trace 后显示后端精确详情",
      sections: fallback.sections ?? [],
      fields: fallback.fields
    };
  }
  const trace = detail.trace;
  const correlation = detail.correlation;
  const computeNodeId = detail.compute_node?.node_id ?? correlation.compute_node_id;
  const sections: DataPanelNodeDetailSection[] = [
    {
      sectionId: "service_trace_lifecycle",
      title: "服务生命周期",
      fields: [
        { label: "trace", value: trace.trace_id },
        { label: "服务", value: trace.service_id },
        { label: "任务", value: trace.task_id || "无任务 id" },
        {
          label: "终态",
          value: serviceLifecycleTerminalLabel(
            trace.terminal_state,
            trace.terminal_state_reason
          )
        },
        {
          label: "总时延",
          value: formatMetricMilliseconds(trace.total_latency_s),
          tone: "resource"
        },
        {
          label: "输入网络",
          value: formatMetricMilliseconds(trace.input_network_latency_s)
        },
        {
          label: "计算排队",
          value: formatMetricMilliseconds(trace.compute_queue_delay_s),
          tone: "warning"
        },
        {
          label: "计算执行",
          value: formatMetricMilliseconds(trace.compute_execution_delay_s),
          tone: "resource"
        },
        {
          label: "输出网络",
          value: formatMetricMilliseconds(trace.output_network_latency_s)
        },
        {
          label: "阶段",
          value: `${formatCount(trace.observed_stage_count)} observed / ${formatCount(
            trace.pending_stage_count
          )} pending / ${formatCount(trace.stage_count)} total`
        }
      ]
    },
    {
      sectionId: "service_trace_correlation",
      title: "关联对象",
      fields: [
        {
          label: "用户",
          value: formatLimitedIds(correlation.user_ids),
          tone: correlation.user_count > 0 ? "resource" : "warning"
        },
        {
          label: "卫星",
          value: formatLimitedIds(correlation.satellite_ids),
          tone: correlation.satellite_count > 0 ? "resource" : "warning"
        },
        {
          label: "路由",
          value: formatLimitedIds(correlation.route_ids),
          tone: correlation.route_count > 0 ? "resource" : "warning"
        },
        {
          label: "流",
          value: formatLimitedIds(correlation.flow_ids)
        },
        {
          label: "算力节点",
          value: computeNodeId || "未放置",
          tone: computeNodeId ? "resource" : "warning"
        }
      ]
    }
  ];
  if (detail.routes.length > 0) {
    sections.push({
      sectionId: "service_trace_routes",
      title: "路由解释",
      fields: buildServiceTraceRouteFields(detail.routes)
    });
  }
  sections.push(...buildServiceTraceNodeCardSections("user", detail.users));
  sections.push(...buildServiceTraceNodeCardSections("satellite", detail.satellites));
  if (detail.compute_node !== null && detail.compute_node !== undefined) {
    sections.push({
      sectionId: "service_trace_compute_node",
      title: `算力节点 ${detail.compute_node.node_id}`,
      fields: [
        { label: "状态", value: detail.compute_node.status },
        {
          label: "负载",
          value: formatRatioPercent(detail.compute_node.compute_load_ratio),
          tone: "resource"
        },
        {
          label: "CPU FP32",
          value: resourceUsageLabel(
            detail.compute_node.compute_used_gflops_fp32,
            detail.compute_node.compute_capacity_gflops_fp32,
            "GFLOPS"
          ),
          tone: "resource"
        },
        {
          label: "GPU FP32",
          value: resourceUsageLabel(
            detail.compute_node.compute_used_gpu_tflops_fp32,
            detail.compute_node.compute_capacity_gpu_tflops_fp32,
            "TFLOPS"
          ),
          tone: "resource"
        },
        {
          label: "内存",
          value: resourceUsageLabel(
            detail.compute_node.compute_used_memory_gb,
            detail.compute_node.compute_capacity_memory_gb,
            "GB"
          ),
          tone: "resource"
        },
        {
          label: "任务",
          value: `${formatCount(detail.compute_node.running_task_count)} 运行 / ${formatCount(
            detail.compute_node.finished_task_count
          )} 完成`
        }
      ]
    });
  }
  return {
    kind: "service_trace",
    title: `服务 trace ${compactTaskId(correlation.service_id)}`,
    subtitle: serviceLifecycleTerminalLabel(
      trace.terminal_state,
      trace.terminal_state_reason
    ),
    emptyLabel: "当前服务 trace 暂无后端精确详情",
    sections,
    fields: [
      { label: "服务", value: correlation.service_id },
      { label: "用户", value: formatLimitedIds(correlation.user_ids) },
      { label: "卫星", value: formatLimitedIds(correlation.satellite_ids) },
      {
        label: "总时延",
        value: formatMetricMilliseconds(trace.total_latency_s),
        tone: "resource"
      }
    ]
  };
}

function buildServiceTraceRouteFields(
  routes: readonly RuntimeRouteExplanationItemV1[]
): readonly DataPanelDetailInspectorField[] {
  const visibleRoutes = routes.slice(0, 4);
  const fields: DataPanelDetailInspectorField[] = visibleRoutes.map((route) => {
    const tone: DataPanelDetailInspectorField["tone"] = route.available
      ? "resource"
      : "warning";
    return {
      label: route.route_id,
      value: [
        route.available ? "available" : "blocked",
        route.path_label,
        route.latency_s === null || route.latency_s === undefined
          ? null
          : formatMetricMilliseconds(route.latency_s),
        `${formatMetricValue(route.route_pressure_proxy * 100)}% pressure`,
        route.bottleneck_reason_label || route.explanation_label
      ]
        .filter((part): part is string => part !== null && part.length > 0)
        .join(" / "),
      tone
    };
  });
  if (routes.length > visibleRoutes.length) {
    return [
      ...fields,
      {
        label: "更多路由",
        value: `另有 ${formatCount(routes.length - visibleRoutes.length)} 条未展开`
      }
    ];
  }
  return fields;
}

function buildServiceTraceNodeCardSections(
  prefix: "user" | "satellite",
  cards: readonly RuntimeNodeDetailCardV1[]
): readonly DataPanelNodeDetailSection[] {
  const visibleCards = cards.slice(0, 3);
  const sections = visibleCards.flatMap((card, index) => {
    const inspector = buildRuntimeNodeDetailInspector(card);
    const prefixLabel = prefix === "user" ? "用户" : "卫星";
    return [
      {
        sectionId: `service_trace_${prefix}_${index}_summary`,
        title: `${prefixLabel} ${card.entity_id}`,
        fields:
          inspector.fields.length > 0
            ? inspector.fields
            : [{ label: "状态", value: inspector.subtitle }]
      },
      ...(inspector.sections ?? []).map((section) => ({
        sectionId: `service_trace_${prefix}_${index}_${section.sectionId}`,
        title: section.title,
        fields: section.fields
      }))
    ];
  });
  if (cards.length > visibleCards.length) {
    const prefixLabel = prefix === "user" ? "用户" : "卫星";
    return [
      ...sections,
      {
        sectionId: `service_trace_${prefix}_hidden`,
        title: `${prefixLabel}未展开`,
        fields: [
          {
            label: "数量",
            value: `另有 ${formatCount(cards.length - visibleCards.length)} 个节点`
          }
        ]
      }
    ];
  }
  return sections;
}

function formatLimitedIds(ids: readonly string[], limit = 6): string {
  const normalizedIds = uniqueStrings(ids);
  if (normalizedIds.length === 0) {
    return "无";
  }
  const visibleIds = normalizedIds.slice(0, limit).join(" / ");
  const hiddenCount = normalizedIds.length - Math.min(normalizedIds.length, limit);
  return hiddenCount > 0 ? `${visibleIds} / +${formatCount(hiddenCount)}` : visibleIds;
}

function buildRuntimeNodeDetailInspector(
  card: RuntimeNodeDetailCardV1
): DataPanelDetailInspector {
  return {
    title: card.title,
    subtitle: card.subtitle,
    sections: (card.sections ?? []).map((section) => ({
      sectionId: section.section_id,
      title: section.title,
      fields: section.fields.map((field) => ({
        label: field.label,
        value: field.value,
        tone: runtimeNodeDetailFieldTone(field.tone)
      }))
    })),
    fields: card.fields.map((field) => ({
      label: field.label,
      value: field.value,
      tone: runtimeNodeDetailFieldTone(field.tone)
    }))
  };
}

function runtimeNodeDetailFieldTone(
  tone: RuntimeNodeDetailCardV1["fields"][number]["tone"]
): DataPanelDetailInspectorField["tone"] {
  if (tone === "warning" || tone === "resource") {
    return tone;
  }
  return "normal";
}

export function paginateDetailRows<T>(
  items: readonly T[],
  pageIndex: number,
  pageSize: number
): DetailRowPage<T> {
  if (!Number.isFinite(pageSize) || pageSize <= 0) {
    throw new RangeError("pageSize must be a positive finite number");
  }
  const normalizedPageSize = Math.max(1, Math.floor(pageSize));
  const totalCount = items.length;
  const pageCount = Math.max(1, Math.ceil(totalCount / normalizedPageSize));
  const requestedPage = Number.isFinite(pageIndex) ? Math.floor(pageIndex) : 0;
  const clampedPage = Math.min(Math.max(0, requestedPage), pageCount - 1);
  const startIndex = totalCount === 0 ? 0 : clampedPage * normalizedPageSize;
  const endIndex = Math.min(totalCount, startIndex + normalizedPageSize);
  return {
    items: items.slice(startIndex, endIndex),
    totalCount,
    pageIndex: clampedPage,
    pageSize: normalizedPageSize,
    pageCount,
    startIndex,
    endIndex
  };
}

export function buildDataPanelDetailWindowPolicyNote(
  userPage: DetailRowPage<unknown>,
  satellitePage: DetailRowPage<unknown>,
  contract: LargeDetailPaginationContractV2 | null | undefined = undefined
): DataPanelDetailScopeNote {
  const renderedRows = userPage.items.length + satellitePage.items.length;
  const totalRows = userPage.totalCount + satellitePage.totalCount;
  const hiddenRows = Math.max(0, totalRows - renderedRows);
  const configuredWindowRows = userPage.pageSize + satellitePage.pageSize;
  const budgetSource =
    contract === null || contract === undefined
      ? "前端兼容窗口"
      : `后端契约 ${contract.contract_id}`;
  return {
    label: "表格窗口化",
    value: `${formatCount(renderedRows)} / ${formatCount(totalRows)} 行渲染`,
    detail: [
      `用户窗口 ${detailWindowRangeLabel(userPage)}`,
      `卫星窗口 ${detailWindowRangeLabel(satellitePage)}`,
      `渲染预算 ${formatCount(configuredWindowRows)} 行`,
      `预算来源 ${budgetSource}`,
      hiddenRows > 0
        ? `隐藏 ${formatCount(hiddenRows)} 行等待翻页，避免大规模场景一次性展开 DOM。`
        : "当前筛选结果可在一屏窗口内完整渲染。"
    ].join("；"),
    tone: hiddenRows > 0 ? "limit" : "backend"
  };
}

function detailPaginationCollections(
  contract: LargeDetailPaginationContractV2 | null | undefined
): Map<string, LargeDetailPaginationCollectionV2> {
  return new Map(
    (contract?.collections ?? []).map((collection) => [
      collection.collection,
      collection
    ])
  );
}

function detailPaginationLimit(
  collection: LargeDetailPaginationCollectionV2 | undefined,
  fallback: number
): number {
  const recommended = collection?.recommended_limit;
  const maxLimit = collection?.max_limit;
  if (recommended === undefined || !Number.isFinite(recommended) || recommended <= 0) {
    return fallback;
  }
  if (maxLimit === undefined || !Number.isFinite(maxLimit) || maxLimit <= 0) {
    return Math.max(1, Math.floor(recommended));
  }
  return Math.max(1, Math.min(Math.floor(recommended), Math.floor(maxLimit)));
}

function detailPaginationCollectionLabel(
  collection: LargeDetailPaginationCollectionV2 | undefined,
  fallbackLabel: string
): string {
  if (collection === undefined) {
    return `${fallbackLabel}未声明`;
  }
  return `${collection.label_zh} ${formatCount(collection.recommended_limit)} 行 @ ${collection.endpoint}`;
}

function detailWindowRangeLabel(page: DetailRowPage<unknown>): string {
  if (page.totalCount === 0) {
    return `0 / 0，上限 ${formatCount(page.pageSize)}`;
  }
  return `${formatCount(page.startIndex + 1)}-${formatCount(
    page.endIndex
  )} / ${formatCount(page.totalCount)}，上限 ${formatCount(page.pageSize)}`;
}

function mergeUserBusinessRequestRows(
  backendRows: UserBusinessRequestRows,
  snapshotRows: UserBusinessRequestRows,
  limit: number
): UserBusinessRequestRows {
  const mergedItems = mergeRowsByEntityId(
    backendRows.items,
    snapshotRows.items,
    (row) => row.userId,
    limit
  );
  const addedCount = Math.max(0, mergedItems.length - backendRows.items.length);
  if (addedCount === 0) {
    return {
      ...backendRows,
      items: mergedItems
    };
  }
  return {
    sourceLabel: `${backendRows.sourceLabel} + 快照补齐`,
    summaryLabel: `${backendRows.summaryLabel} / 补齐 ${formatCount(
      addedCount
    )} / 显示 ${formatCount(mergedItems.length)}`,
    items: mergedItems
  };
}

function mergeSatelliteResourceRows(
  backendRows: SatelliteResourceRows,
  snapshotRows: SatelliteResourceRows,
  limit: number
): SatelliteResourceRows {
  const mergedItems = mergeRowsByEntityId(
    backendRows.items,
    snapshotRows.items,
    (row) => row.satelliteId,
    limit
  );
  const addedCount = Math.max(0, mergedItems.length - backendRows.items.length);
  if (addedCount === 0) {
    return {
      ...backendRows,
      items: mergedItems
    };
  }
  return {
    sourceLabel: `${backendRows.sourceLabel} + 快照补齐`,
    summaryLabel: `${backendRows.summaryLabel} / 补齐 ${formatCount(
      addedCount
    )} / 显示 ${formatCount(mergedItems.length)}`,
    items: mergedItems
  };
}

function mergeRowsByEntityId<T>(
  backendItems: readonly T[],
  snapshotItems: readonly T[],
  entityId: (item: T) => string,
  limit: number
): readonly T[] {
  const merged = new Map<string, T>();
  for (const item of snapshotItems) {
    merged.set(entityId(item), item);
  }
  for (const item of backendItems) {
    merged.set(entityId(item), item);
  }
  return Array.from(merged.values())
    .sort((left, right) => compareEntityId(entityId(left), entityId(right)))
    .slice(0, Math.max(0, limit));
}

export function buildRuntimeDetailSourceBadge(sourceLabel: string): RuntimeDetailSourceBadge {
  const normalized = sourceLabel.toLowerCase();
  const hasBackend = normalized.includes("backend") || sourceLabel.includes("后端");
  const hasSnapshot = normalized.includes("snapshot") || sourceLabel.includes("快照");
  if (hasBackend && !hasSnapshot) {
    return {
      label: "后端摘要",
      title: "明细来自后端运行态摘要字段",
      tone: "backend"
    };
  }
  if (hasBackend && hasSnapshot) {
    return {
      label: "后端增强",
      title: "后端运行态摘要与状态快照共同生成明细",
      tone: "mixed"
    };
  }
  return {
    label: "快照回退",
    title: "后端运行态摘要暂缺，明细由当前状态快照推导",
    tone: "snapshot"
  };
}

function normalizeDetailFilter(query: string): string {
  return query.trim().toLowerCase();
}

function userBusinessRequestRowId(
  userId: string,
  requestId: string,
  routeId: string,
  flowId: string
): string {
  return [userId, requestId, routeId, flowId]
    .map((value) => value.trim())
    .filter((value) => value.length > 0)
    .join(":") || userId;
}

function userBusinessRequestCorrelationLabel({
  requestId,
  serviceRequestId,
  routeId,
  flowId,
  taskId,
  computeNodeId,
  nextHopId
}: {
  requestId: string;
  serviceRequestId: string;
  routeId: string;
  flowId: string;
  taskId: string;
  computeNodeId: string;
  nextHopId: string;
}): string {
  return [
    requestId ? `request ${requestId}` : "",
    serviceRequestId && serviceRequestId !== requestId
      ? `service ${serviceRequestId}`
      : "",
    routeId ? `route ${routeId}` : "",
    flowId ? `flow ${flowId}` : "",
    taskId ? `task ${taskId}` : "",
    computeNodeId ? `compute ${computeNodeId}` : "",
    nextHopId ? `next ${nextHopId}` : ""
  ]
    .filter((value) => value.length > 0)
    .join(" / ");
}

function linkedReviewId(value: string | null | undefined): string | null {
  const normalized = value?.trim() ?? "";
  if (normalized.length === 0) {
    return null;
  }
  const lowered = normalized.toLowerCase();
  if (
    lowered === "none" ||
    lowered === "unknown" ||
    lowered === "idle" ||
    lowered === "no route" ||
    lowered === "no service"
  ) {
    return null;
  }
  return normalized;
}

function userBusinessRequestServiceTraceQuery(
  row: UserBusinessRequestRow
): string {
  return (
    linkedReviewId(row.serviceRequestId) ??
    linkedReviewId(row.requestId) ??
    linkedReviewId(row.taskId) ??
    linkedReviewId(row.flowId) ??
    ""
  );
}

function buildBackendUserBusinessRequestRows(
  summary: RuntimeUserRequestSummaryV1,
  limit: number
): UserBusinessRequestRows {
  const items = summary.items.slice(0, Math.max(0, limit)).map((item) => {
    const requestId = item.request_id ?? item.primary_flow_id ?? item.service_task_id ?? "";
    const serviceRequestId = item.service_request_id ?? requestId;
    const routeId =
      item.route_id ?? item.primary_route_id ?? item.input_route_id ?? item.output_route_id ?? "";
    const flowId = item.flow_id ?? item.primary_flow_id ?? "";
    const taskId = item.task_id ?? item.service_task_id ?? "";
    const computeNodeId = item.compute_node_id ?? "";
    const nextHopId = item.next_hop_id ?? item.primary_next_hop_id ?? "";
    const correlationLabel = userBusinessRequestCorrelationLabel({
      requestId,
      serviceRequestId,
      routeId,
      flowId,
      taskId,
      computeNodeId,
      nextHopId
    });
    const latencyCapacityLabel =
      typeof item.latency_s === "number" && typeof item.capacity_mbps === "number"
        ? `${formatPreciseMetricValue(item.latency_s)} s / ${formatMetricValue(
            item.capacity_mbps
          )} Mbps`
        : "no route";
    const cellLabel = item.cell_id ? ` / ${item.cell_id}` : "";
    const businessLabel =
      item.active_business_label || trafficClassLabel(item.active_business_type ?? "NONE");
    const requestState =
      item.request_state_label ||
      (item.request_state ? dataPanelRequestStateLabel(item.request_state) : "");
    const queueReason = item.network_queue_reason_label || "";
    const serviceLatencyLabel = backendUserServiceLatencyLabel(item);
    const placementLabel = backendUserPlacementLabel(item);
    const serviceLabel = [
      businessLabel,
      requestState,
      serviceLatencyLabel || item.service_state || item.primary_flow_id
    ]
      .filter((value) => value !== "")
      .join(" / ") || "no service";
    const queueLabel =
      item.network_queue_count > 0
        ? `${formatCount(item.network_queue_count)} waiting${
            queueReason ? ` / ${queueReason}` : ""
          }`
        : queueReason && queueReason !== "No network queue"
          ? queueReason
          : "empty";
    const nextHopDetail = item.primary_next_hop_id
      ? ` / next ${item.primary_next_hop_id}`
      : "";
    return {
      rowId: userBusinessRequestRowId(item.user_id, requestId, routeId, flowId),
      userId: item.user_id,
      requestId,
      serviceRequestId,
      routeId,
      flowId,
      taskId,
      computeNodeId,
      nextHopId,
      platformTypeLabel: `${item.platform_type_label || item.platform_type}${cellLabel}`,
      communicationLabel:
        item.communication_route_count > 0
          ? `${formatCount(item.available_route_count)} / ${formatCount(
              item.communication_route_count
            )} routes${nextHopDetail}`
          : "idle",
      computeLabel:
        item.compute_service_count > 0
          ? `${formatCount(item.compute_service_count)} compute`
          : "no compute",
      networkQueueLabel: queueLabel,
      selectedSatelliteId: item.selected_satellite_id || "none",
      destinationId: item.destination_id || "none",
      placementLabel,
      statusLabel: item.status || "IDLE",
      latencyCapacityLabel,
      serviceLabel,
      pathLabel:
        item.route_path_label ||
        (item.path.length > 0
          ? `${item.primary_route_id || item.primary_flow_id || item.user_id}: ${item.path.join(
              " -> "
            )}`
          : `${item.user_id}: no active route`),
      correlationLabel
    };
  });
  const hiddenCount = Math.max(
    summary.hidden_user_count,
    Math.max(0, summary.items.length - items.length)
  );
  const windowCount = Math.max(0, summary.window_user_count ?? summary.item_count);
  const windowActiveCount = Math.max(
    0,
    summary.window_active_user_count ?? summary.active_user_count
  );
  const sourceLabel =
    summary.version === "v2"
      ? "backend user_service_request_summary_v2"
      : "backend user_request_summary_v1";
  return {
    sourceLabel,
    summaryLabel: `${formatCount(items.length)} shown / ${formatCount(
      summary.user_count
    )} total / active ${formatCount(
      summary.active_user_count
    )} total / window active ${formatCount(windowActiveCount)} / window ${formatCount(
      windowCount
    )} / compute ${formatCount(summary.compute_service_user_count)}${
      hiddenCount > 0 ? ` / hidden ${formatCount(hiddenCount)}` : ""
    }`,
    items
  };
}

function backendUserServiceLatencyLabel(item: RuntimeUserRequestItemV1): string {
  const totalLatency = finiteOptionalMetric(item.service_total_latency_s);
  const componentValues: readonly [string, number | null | undefined][] = [
    ["in", item.input_network_latency_s],
    ["queue", item.compute_queue_delay_s],
    ["exec", item.compute_execution_delay_s],
    ["out", item.output_network_latency_s]
  ];
  const components = componentValues
    .map(([label, value]) => {
      const parsed = finiteOptionalMetric(value);
      return parsed > 0 ? `${label} ${formatMetricMilliseconds(parsed)}` : null;
    })
    .filter((value): value is string => value !== null);
  if (totalLatency <= 0 && components.length === 0) {
    return "";
  }
  const stateLabel = item.service_complete === true ? "complete" : "active";
  const taskLabel = item.service_task_id ? `${item.service_task_id} ${stateLabel}` : stateLabel;
  const routeParts = [
    item.input_route_id ? `input ${item.input_route_id}` : null,
    item.output_route_id ? `output ${item.output_route_id}` : null
  ].filter((value): value is string => value !== null);
  return [
    taskLabel,
    totalLatency > 0 ? `total ${formatMetricMilliseconds(totalLatency)}` : null,
    components.length > 0 ? components.join(" + ") : null,
    routeParts.length > 0 ? routeParts.join(" / ") : null
  ]
    .filter((value): value is string => value !== null)
    .join(" / ");
}

function backendUserPlacementLabel(item: RuntimeUserRequestItemV1): string {
  return servicePlacementLabel({
    computeNodeId: item.compute_node_id,
    status: item.service_placement_status,
    policy: item.service_placement_policy,
    bottleneckResource: item.service_placement_bottleneck_resource,
    candidateCount: item.service_placement_candidate_count,
    capableCandidateCount: item.service_placement_capable_candidate_count,
    candidateQueueLabel: item.service_placement_candidate_queue_label
  });
}

function buildBackendSatelliteResourceRows(
  summary: RuntimeSatelliteServiceSummaryV1,
  limit: number
): SatelliteResourceRows {
  const items = summary.items.slice(0, Math.max(0, limit)).map((item) => {
    const loadRatio = clampRatio(finiteMetric(item.compute_load_ratio));
    return {
      satelliteId: item.satellite_id,
      statusLabel: item.resource_role_label
        ? `${item.status} / ${item.resource_role_label}`
        : item.status,
      loadPercent: roundMetric(loadRatio * 100),
      loadLabel: `${formatMetricValue(loadRatio * 100)}%`,
      serviceObjectLabel: compactBackendEntityLabel(
        item.service_user_ids ?? [],
        item.service_user_count ?? item.route_count,
        "users"
      ),
      nextHopLabel: compactBackendEntityLabel(
        item.next_hop_ids ?? [],
        item.next_hop_count ?? item.route_count,
        "hops"
      ),
      cpuFp32Label: resourceUsageLabel(
        item.compute_used_gflops_fp32,
        item.compute_capacity_gflops_fp32,
        "GFLOPS"
      ),
      cpuFp64Label: resourceUsageLabel(
        item.compute_used_gflops_fp64,
        item.compute_capacity_gflops_fp64,
        "GFLOPS"
      ),
      gpuLabel: `FP32 ${resourceUsageLabel(
        item.compute_used_gpu_tflops_fp32,
        item.compute_capacity_gpu_tflops_fp32,
        "TFLOPS"
      )} / FP16 ${resourceUsageLabel(
        item.compute_used_gpu_tflops_fp16,
        item.compute_capacity_gpu_tflops_fp16,
        "TFLOPS"
      )}`,
      npuLabel: resourceUsageLabel(
        item.compute_used_npu_tops_int8,
        item.compute_capacity_npu_tops_int8,
        "TOPS"
      ),
      memoryStorageLabel: `memory ${resourceUsageLabel(
        item.compute_used_memory_gb,
        item.compute_capacity_memory_gb,
        "GB"
      )} / storage ${resourceUsageLabel(
        item.compute_used_storage_gb,
        item.compute_capacity_storage_gb,
        "GB"
      )}`,
      taskLabel: `${formatCount(item.running_task_count)} running / ${formatCount(
        item.finished_task_count
      )} done / ${
        item.route_mix_label ??
        `compute ${formatCount(item.compute_service_route_count ?? 0)} / network ${formatCount(
          item.network_service_route_count ?? 0
        )}`
      }`,
      networkLabel: [
        `links ${formatCount(item.active_link_count)} / access ${formatCount(
          item.active_access_link_count
        )} / space ${formatCount(item.active_space_link_count)} / routes ${formatCount(
          item.route_count
        )}`,
        item.network_queue_route_count !== undefined
          ? `queued ${formatCount(item.network_queue_route_count)}`
          : null,
        backendSatelliteRouteKpiLabel(item),
        item.primary_route_id ? `primary ${item.primary_route_id}` : null
      ]
        .filter((value): value is string => value !== null && value !== "")
        .join(" / ")
    };
  });
  const hiddenCount = Math.max(
    summary.hidden_satellite_count,
    Math.max(0, summary.items.length - items.length)
  );
  const windowCount = Math.max(
    0,
    summary.window_satellite_count ?? summary.item_count
  );
  return {
    sourceLabel: "backend satellite_service_summary_v1",
    summaryLabel: `${formatCount(items.length)} shown / ${formatCount(
      summary.satellite_count
    )} total / window ${formatCount(windowCount)}${
      hiddenCount > 0 ? ` / hidden ${formatCount(hiddenCount)}` : ""
    }`,
    items
  };
}

function backendSatelliteRouteKpiLabel(item: RuntimeSatelliteServiceItemV1): string {
  const capacity = finiteOptionalMetric(item.route_capacity_mbps);
  const demand = finiteOptionalMetric(item.route_demand_mbps);
  const latency = finiteOptionalMetric(item.route_latency_avg_s);
  const loss = finiteOptionalMetric(item.route_loss_proxy_rate);
  const parts = [
    capacity > 0 ? `cap ${formatMetricValue(capacity)} Mbps` : null,
    demand > 0 ? `demand ${formatMetricValue(demand)} Mbps` : null,
    latency > 0 ? `lat ${formatMetricMilliseconds(latency)}` : null,
    loss > 0 ? `loss ${formatMetricValue(loss * 100)}%` : null
  ].filter((value): value is string => value !== null);
  return parts.join(" / ");
}

function compactBackendEntityLabel(
  values: readonly string[],
  totalCount: number,
  emptyLabel: string,
  limit = 3
): string {
  if (values.length === 0) {
    return `${emptyLabel} 0`;
  }
  const ordered = values.slice().sort(compareEntityId);
  const visible = ordered.slice(0, Math.max(1, limit)).join(", ");
  const hiddenCount = Math.max(0, ordered.length - limit);
  const suffix = hiddenCount > 0 ? ` +${formatCount(hiddenCount)}` : "";
  return `${visible}${suffix} / ${formatCount(totalCount)} routes`;
}

function buildSnapshotTopComputeNodeRows(snapshot: WorldSnapshot): readonly TopComputeNodeRow[] {
  return snapshot.compute_nodes
    .map((node) => {
      const capacity = Math.max(0, finiteMetric(node.capacity));
      const available = Math.max(
        0,
        Math.min(capacity, finiteMetric(node.available_capacity))
      );
      const usedFp32 =
        typeof node.used_cpu_gflops_fp32 === "number" &&
        Number.isFinite(node.used_cpu_gflops_fp32)
          ? Math.max(0, node.used_cpu_gflops_fp32)
          : Math.max(0, capacity - available);
      const loadRatio =
        typeof node.load_ratio === "number" && Number.isFinite(node.load_ratio)
          ? clampRatio(node.load_ratio)
          : capacity <= 0
            ? 0
            : clampRatio(usedFp32 / capacity);
      return {
        nodeId: node.node_id,
        statusLabel: node.status,
        loadPercent: roundMetric(loadRatio * 100),
        usedFp32Gflops: roundMetric(usedFp32),
        runningTasks: node.running_tasks,
        loadLabel: `${formatMetricValue(loadRatio * 100)}%`,
        fp32Label: `${formatMetricValue(usedFp32)} / ${formatMetricValue(
          capacity
        )} GFLOPS`,
        taskLabel: `${node.running_tasks} 运行 / ${node.finished_tasks} 完成`
      };
    });
}

function compareTopComputeNodeRows(
  left: TopComputeNodeRow,
  right: TopComputeNodeRow
): number {
  const loadDelta = right.loadPercent - left.loadPercent;
  if (loadDelta !== 0) {
    return loadDelta;
  }
  const fp32Delta = right.usedFp32Gflops - left.usedFp32Gflops;
  if (fp32Delta !== 0) {
    return fp32Delta;
  }
  const taskDelta = right.runningTasks - left.runningTasks;
  if (taskDelta !== 0) {
    return taskDelta;
  }
  return left.nodeId.localeCompare(right.nodeId);
}

function buildServiceFlowLookup(
  history: RuntimeServiceLatencyHistoryV1 | null | undefined
): ReadonlyMap<string, string> {
  const lookup = new Map<string, string>();
  for (const item of history?.items ?? []) {
    const label = `${compactTaskId(item.task_id)} / ${formatMetricMilliseconds(
      item.total_latency_s
    )} / ${item.complete ? "闭环" : "进行中"}`;
    if (item.input_flow_id) {
      lookup.set(item.input_flow_id, label);
    }
    if (item.output_flow_id) {
      lookup.set(item.output_flow_id, label);
    }
  }
  return lookup;
}

function buildServicePlacementLookup(
  history: RuntimeServiceLatencyHistoryV1 | null | undefined
): ReadonlyMap<string, string> {
  const lookup = new Map<string, string>();
  for (const item of history?.items ?? []) {
    const label = serviceLatencyPlacementLabel(item);
    if (label === "无计算放置") {
      continue;
    }
    if (item.input_flow_id) {
      lookup.set(item.input_flow_id, label);
    }
    if (item.output_flow_id) {
      lookup.set(item.output_flow_id, label);
    }
  }
  return lookup;
}

function buildRoutesByUser(
  routes: readonly SnapshotRoute[]
): ReadonlyMap<string, readonly SnapshotRoute[]> {
  const mutable = new Map<string, SnapshotRoute[]>();
  for (const route of routes) {
    const userId = routeUserId(route);
    if (userId === null) {
      continue;
    }
    const rows = mutable.get(userId) ?? [];
    rows.push(route);
    mutable.set(userId, rows);
  }
  return mutable;
}

function routeUserId(route: SnapshotRoute): string | null {
  return route.path.find((item) => item.startsWith("user-")) ?? null;
}

function routeFirstSatellite(route: SnapshotRoute): string | null {
  return route.path.find((item) => item.startsWith("sat-")) ?? null;
}

function routeIsComputeService(
  route: SnapshotRoute,
  serviceLookup: ReadonlyMap<string, string>
): boolean {
  if (serviceLookup.has(route.flow_id)) {
    return true;
  }
  return route.path.some(
    (item) => item.startsWith("compute-") || item.includes("compute")
  );
}

function selectUserPrimaryRoute(
  routes: readonly SnapshotRoute[],
  serviceLookup: ReadonlyMap<string, string>
): SnapshotRoute | null {
  if (routes.length === 0) {
    return null;
  }
  return routes.slice().sort((left, right) => {
    const leftCompute = routeIsComputeService(left, serviceLookup) ? 1 : 0;
    const rightCompute = routeIsComputeService(right, serviceLookup) ? 1 : 0;
    if (leftCompute !== rightCompute) {
      return rightCompute - leftCompute;
    }
    if (left.available !== right.available) {
      return Number(right.available) - Number(left.available);
    }
    const latencyDelta = left.latency - right.latency;
    if (latencyDelta !== 0) {
      return latencyDelta;
    }
    return left.route_id.localeCompare(right.route_id, "zh-CN", { numeric: true });
  })[0];
}

function userPlatformTypeLabel(
  user: WorldSnapshot["ground_users"][number] | undefined
): string {
  if (user?.cell_id) {
    return `地面用户终端 / ${user.cell_id}`;
  }
  return "地面用户终端";
}

function userRouteStatusLabel(
  userStatus: string | undefined,
  routes: readonly SnapshotRoute[],
  availableRoutes: readonly SnapshotRoute[]
): string {
  if (routes.length === 0) {
    return userStatus ?? "空闲";
  }
  if (availableRoutes.length > 0) {
    return userStatus ? `${userStatus} / 业务可达` : "业务可达";
  }
  return userStatus ? `${userStatus} / 等待路由` : "等待路由";
}

function compareUserBusinessRoute(left: SnapshotRoute, right: SnapshotRoute): number {
  const userDelta = (routeUserId(left) ?? "").localeCompare(routeUserId(right) ?? "", "zh-CN", {
    numeric: true
  });
  if (userDelta !== 0) {
    return userDelta;
  }
  return left.route_id.localeCompare(right.route_id, "zh-CN", { numeric: true });
}

interface SatelliteRouteContext {
  serviceObjectLabel: string;
  nextHopLabel: string;
}

function buildSatelliteRouteContexts(
  routes: readonly SnapshotRoute[]
): ReadonlyMap<string, SatelliteRouteContext> {
  const mutable = new Map<
    string,
    {
      users: Set<string>;
      nextHops: Set<string>;
      routeCount: number;
    }
  >();
  const ensure = (satelliteId: string) => {
    let entry = mutable.get(satelliteId);
    if (entry === undefined) {
      entry = {
        users: new Set<string>(),
        nextHops: new Set<string>(),
        routeCount: 0
      };
      mutable.set(satelliteId, entry);
    }
    return entry;
  };
  for (const route of routes.slice().sort(compareUserBusinessRoute)) {
    const userId = routeUserId(route);
    route.path.forEach((nodeId, index) => {
      if (!nodeId.startsWith("sat-")) {
        return;
      }
      const entry = ensure(nodeId);
      entry.routeCount += 1;
      if (userId !== null) {
        entry.users.add(userId);
      }
      const nextHop = route.path[index + 1] ?? "终点";
      entry.nextHops.add(nextHop);
    });
  }
  return new Map(
    Array.from(mutable.entries()).map(([satelliteId, entry]) => [
      satelliteId,
      {
        serviceObjectLabel: compactEntitySetLabel(entry.users, "用户", entry.routeCount),
        nextHopLabel: compactEntitySetLabel(entry.nextHops, "下一跳", entry.routeCount)
      }
    ])
  );
}

function compactEntitySetLabel(
  values: ReadonlySet<string>,
  emptyLabel: string,
  totalCount: number,
  limit = 3
): string {
  if (values.size === 0) {
    return `${emptyLabel} 0`;
  }
  const ordered = Array.from(values).sort(compareEntityId);
  const visible = ordered.slice(0, Math.max(1, limit)).join(", ");
  const hiddenCount = Math.max(0, ordered.length - limit);
  const suffix = hiddenCount > 0 ? ` +${formatCount(hiddenCount)}` : "";
  return `${visible}${suffix} / 关联 ${formatCount(totalCount)} 条`;
}

interface SatelliteNetworkFallback {
  activeLinkCount: number;
  routeCount: number;
  routeCapacityMbps: number;
  routeLatencyAvgS: number;
  routeLossProxyRate: number;
}

function buildSatelliteNetworkFallbacks(
  snapshot: WorldSnapshot
): ReadonlyMap<string, SatelliteNetworkFallback> {
  const mutable = new Map<
    string,
    {
      activeLinkCount: number;
      routeCount: number;
      routeCapacityMbps: number;
      routeLatencies: number[];
      routeLossRates: number[];
    }
  >();
  const ensure = (satelliteId: string) => {
    let entry = mutable.get(satelliteId);
    if (entry === undefined) {
      entry = {
        activeLinkCount: 0,
        routeCount: 0,
        routeCapacityMbps: 0,
        routeLatencies: [],
        routeLossRates: []
      };
      mutable.set(satelliteId, entry);
    }
    return entry;
  };
  for (const link of snapshot.links) {
    if (!link.availability) {
      continue;
    }
    if (link.source_id.startsWith("sat-")) {
      ensure(link.source_id).activeLinkCount += 1;
    }
    if (link.target_id.startsWith("sat-")) {
      ensure(link.target_id).activeLinkCount += 1;
    }
  }
  for (const route of snapshot.routes) {
    const satelliteIds = new Set(route.path.filter((item) => item.startsWith("sat-")));
    for (const satelliteId of satelliteIds) {
      const entry = ensure(satelliteId);
      entry.routeCount += 1;
      if (route.available) {
        entry.routeCapacityMbps += Math.max(0, route.capacity);
        entry.routeLatencies.push(Math.max(0, route.latency));
        entry.routeLossRates.push(clampRatio(route.loss_rate ?? 0));
      }
    }
  }
  return new Map(
    Array.from(mutable.entries()).map(([satelliteId, entry]) => [
      satelliteId,
      {
        activeLinkCount: entry.activeLinkCount,
        routeCount: entry.routeCount,
        routeCapacityMbps: roundMetric(entry.routeCapacityMbps),
        routeLatencyAvgS: roundMetric(average(entry.routeLatencies)),
        routeLossProxyRate: roundMetric(average(entry.routeLossRates))
      }
    ])
  );
}

function satelliteNetworkLabel(
  slice: RuntimeSatelliteKpiSlicesV1["slices"][number] | undefined,
  fallback: SatelliteNetworkFallback | undefined
): string {
  if (slice !== undefined) {
    return `链路 ${slice.active_link_count} / 路由 ${slice.route_count} / ${formatMetricValue(
      slice.route_capacity_mbps
    )} Mbps / ${formatMetricMilliseconds(slice.route_latency_avg_s)} / 损耗 ${formatMetricValue(
      slice.route_loss_proxy_rate * 100
    )}%`;
  }
  if (fallback === undefined) {
    return "链路 0 / 路由 0";
  }
  return `链路 ${fallback.activeLinkCount} / 路由 ${fallback.routeCount} / ${formatMetricValue(
    fallback.routeCapacityMbps
  )} Mbps / ${formatMetricMilliseconds(fallback.routeLatencyAvgS)} / 损耗 ${formatMetricValue(
    fallback.routeLossProxyRate * 100
  )}%`;
}

function resourceUsageLabel(used: number, capacity: number, unit: string): string {
  return `${formatMetricValue(Math.max(0, used))} / ${formatMetricValue(
    Math.max(0, capacity)
  )} ${unit}`;
}

function finiteOptionalMetric(
  ...values: readonly (number | null | undefined)[]
): number {
  for (const value of values) {
    if (typeof value === "number" && Number.isFinite(value)) {
      return value;
    }
  }
  return 0;
}

function compareEntityId(left: string, right: string): number {
  return left.localeCompare(right, "zh-CN", { numeric: true });
}

function buildComputeResourceVectorPoolSummary(
  snapshot: WorldSnapshot,
  backendMetrics: RuntimeMetricsSummary | null | undefined
): ComputeResourceVectorPoolSummary {
  return {
    cpuFp64Gflops: roundMetric(
      metricNumber(backendMetrics, "compute_resource_total_gflops_fp64") ??
        sumComputeNodeField(snapshot, "cpu_gflops_fp64")
    ),
    usedCpuFp32Gflops: metricOrNodeSum(
      snapshot,
      backendMetrics,
      "compute_resource_used_cpu_gflops_fp32",
      "used_cpu_gflops_fp32"
    ),
    availableCpuFp32Gflops: metricOrNodeSum(
      snapshot,
      backendMetrics,
      "compute_resource_available_cpu_gflops_fp32",
      "available_cpu_gflops_fp32"
    ),
    usedCpuFp64Gflops: metricOrNodeSum(
      snapshot,
      backendMetrics,
      "compute_resource_used_gflops_fp64",
      "used_cpu_gflops_fp64"
    ),
    availableCpuFp64Gflops: metricOrNodeSum(
      snapshot,
      backendMetrics,
      "compute_resource_available_gflops_fp64",
      "available_cpu_gflops_fp64"
    ),
    gpuFp32Tflops: roundMetric(
      metricNumber(backendMetrics, "compute_resource_total_gpu_tflops_fp32") ??
        sumComputeNodeField(snapshot, "gpu_tflops_fp32")
    ),
    usedGpuFp32Tflops: metricOrNodeSum(
      snapshot,
      backendMetrics,
      "compute_resource_used_gpu_tflops_fp32",
      "used_gpu_tflops_fp32"
    ),
    availableGpuFp32Tflops: metricOrNodeSum(
      snapshot,
      backendMetrics,
      "compute_resource_available_gpu_tflops_fp32",
      "available_gpu_tflops_fp32"
    ),
    gpuFp16Tflops: roundMetric(
      metricNumber(backendMetrics, "compute_resource_total_gpu_tflops_fp16") ??
        sumComputeNodeField(snapshot, "gpu_tflops_fp16")
    ),
    usedGpuFp16Tflops: metricOrNodeSum(
      snapshot,
      backendMetrics,
      "compute_resource_used_gpu_tflops_fp16",
      "used_gpu_tflops_fp16"
    ),
    availableGpuFp16Tflops: metricOrNodeSum(
      snapshot,
      backendMetrics,
      "compute_resource_available_gpu_tflops_fp16",
      "available_gpu_tflops_fp16"
    ),
    npuInt8Tops: roundMetric(
      metricNumber(backendMetrics, "compute_resource_total_npu_tops_int8") ??
        sumComputeNodeField(snapshot, "npu_tops_int8")
    ),
    usedNpuInt8Tops: metricOrNodeSum(
      snapshot,
      backendMetrics,
      "compute_resource_used_npu_tops_int8",
      "used_npu_tops_int8"
    ),
    availableNpuInt8Tops: metricOrNodeSum(
      snapshot,
      backendMetrics,
      "compute_resource_available_npu_tops_int8",
      "available_npu_tops_int8"
    ),
    memoryGb: roundMetric(
      metricNumber(backendMetrics, "compute_resource_total_memory_gb") ??
        sumComputeNodeField(snapshot, "memory_gb")
    ),
    usedMemoryGb: metricOrNodeSum(
      snapshot,
      backendMetrics,
      "compute_resource_used_memory_gb",
      "used_memory_gb"
    ),
    availableMemoryGb: metricOrNodeSum(
      snapshot,
      backendMetrics,
      "compute_resource_available_memory_gb",
      "available_memory_gb"
    ),
    storageGb: roundMetric(
      metricNumber(backendMetrics, "compute_resource_total_storage_gb") ??
        sumComputeNodeField(snapshot, "storage_gb")
    ),
    usedStorageGb: metricOrNodeSum(
      snapshot,
      backendMetrics,
      "compute_resource_used_storage_gb",
      "used_storage_gb"
    ),
    availableStorageGb: metricOrNodeSum(
      snapshot,
      backendMetrics,
      "compute_resource_available_storage_gb",
      "available_storage_gb"
    ),
    utilizationMode:
      typeof backendMetrics?.compute_resource_vector_utilization_mode === "string"
        ? backendMetrics.compute_resource_vector_utilization_mode
        : "SNAPSHOT_SCALAR_FP32_AVAILABLE_ONLY"
  };
}

function metricOrNodeSum(
  snapshot: WorldSnapshot,
  backendMetrics: RuntimeMetricsSummary | null | undefined,
  metricKey: string,
  nodeField: ComputeNodeNumericField
): number {
  return roundMetric(
    metricNumber(backendMetrics, metricKey) ?? sumComputeNodeField(snapshot, nodeField)
  );
}

type ComputeNodeNumericField =
  | "cpu_gflops_fp64"
  | "gpu_tflops_fp32"
  | "gpu_tflops_fp16"
  | "npu_tops_int8"
  | "memory_gb"
  | "storage_gb"
  | "available_cpu_gflops_fp32"
  | "used_cpu_gflops_fp32"
  | "available_cpu_gflops_fp64"
  | "used_cpu_gflops_fp64"
  | "available_gpu_tflops_fp32"
  | "used_gpu_tflops_fp32"
  | "available_gpu_tflops_fp16"
  | "used_gpu_tflops_fp16"
  | "available_npu_tops_int8"
  | "used_npu_tops_int8"
  | "available_memory_gb"
  | "used_memory_gb"
  | "available_storage_gb"
  | "used_storage_gb";

function sumComputeNodeField(
  snapshot: WorldSnapshot,
  field: ComputeNodeNumericField
): number {
  return snapshot.compute_nodes.reduce((sum, node) => {
    const value = node[field];
    return sum + (typeof value === "number" && Number.isFinite(value) ? Math.max(0, value) : 0);
  }, 0);
}

function average(values: readonly number[]): number {
  if (values.length === 0) {
    return 0;
  }
  return values.reduce((total, value) => total + value, 0) / values.length;
}

function standardDeviation(values: readonly number[]): number {
  if (values.length <= 1) {
    return 0;
  }
  const mean = average(values);
  const variance = average(values.map((value) => (value - mean) ** 2));
  return Math.sqrt(variance);
}

function resolveTransportLossRate(snapshot: WorldSnapshot): number {
  const configured = snapshot.scenario_config?.network?.transport_loss_rate;
  if (typeof configured === "number" && Number.isFinite(configured)) {
    return clampRatio(configured);
  }
  if (snapshot.links.length === 0) {
    return 0;
  }
  const unavailableLinks = snapshot.links.filter((link) => !link.availability).length;
  return clampRatio((unavailableLinks / snapshot.links.length) * 0.1);
}

function roundMetric(value: number): number {
  if (!Number.isFinite(value)) {
    return 0;
  }
  return Math.round(value * 1000) / 1000;
}

function finiteMetric(value: number): number {
  return Number.isFinite(value) ? value : 0;
}

function clampRatio(value: number): number {
  return Math.max(0, Math.min(1, value));
}

function metricNumber(
  metrics: RuntimeMetricsSummary | null | undefined,
  key: string
): number | undefined {
  const value = metrics?.[key];
  return typeof value === "number" && Number.isFinite(value) ? value : undefined;
}

function metricInput(
  metrics: RuntimeMetricsSummary | null | undefined,
  key: string,
  label: string,
  format: (value: number) => string
): DataPanelNetworkFormulaInput | null {
  const value = metricNumber(metrics, key);
  return value === undefined
    ? null
    : {
        label,
        value: format(value)
      };
}

function sampleMetricInput(
  value: number | undefined,
  label: string,
  format: (value: number) => string
): DataPanelNetworkFormulaInput | null {
  return typeof value === "number" && Number.isFinite(value)
    ? {
        label,
        value: format(value)
      }
    : null;
}

function formatMetricMbps(value: number): string {
  return `${formatMetricValue(value)} Mbps`;
}

function formatMetricMilliseconds(value: number): string {
  return `${formatMetricValue(value * 1000)} ms`;
}

function computeSeriesOption(key: DataPanelComputeSeriesKey): DataPanelComputeSeriesOption {
  return COMPUTE_SERIES_OPTIONS.find((option) => option.key === key) ?? COMPUTE_SERIES_OPTIONS[0];
}

function formatComputeSeriesValue(value: number, unit: string): string {
  return `${formatMetricValue(value)} ${unit}`;
}

function formatRatioPercent(value: number): string {
  return `${formatMetricValue(value * 100)}%`;
}

function formatComputeBottleneckStatus(status: string | undefined): string {
  switch (status) {
    case "SATURATED":
      return "饱和";
    case "PRESSURED":
      return "受压";
    case "NORMAL":
      return "正常";
    case "IDLE":
      return "空闲";
    default:
      return "状态未知";
  }
}

function formatMetricValue(value: number): string {
  return value.toLocaleString("zh-CN", {
    maximumFractionDigits: 1,
    minimumFractionDigits: 0
  });
}

function formatCount(value: number): string {
  return Math.round(value).toLocaleString("zh-CN");
}

function normalizeNonNegativeInteger(value: number): number {
  if (!Number.isFinite(value) || value <= 0) {
    return 0;
  }
  return Math.floor(value);
}

function compactTaskId(taskId: string): string {
  if (taskId.length <= 18) {
    return taskId;
  }
  return `...${taskId.slice(-15)}`;
}

function uniqueStrings(values: readonly string[]): readonly string[] {
  const seen = new Set<string>();
  const result: string[] = [];
  for (const value of values) {
    const normalized = value.trim();
    if (!normalized || seen.has(normalized)) {
      continue;
    }
    seen.add(normalized);
    result.push(normalized);
  }
  return result;
}

function serviceLatencyTraceTitle(
  item: RuntimeServiceLatencyHistoryV1["items"][number]
): string {
  const parts = [
    `task=${item.task_id}`,
    item.input_flow_id ? `input=${item.input_flow_id}` : "",
    item.output_flow_id ? `output=${item.output_flow_id}` : "",
    item.input_route_id ? `input_route=${item.input_route_id}` : "",
    item.output_route_id ? `output_route=${item.output_route_id}` : "",
    serviceLatencyPlacementTrace(item),
    typeof item.first_sample_sim_time === "number"
      ? `first=${formatMetricValue(item.first_sample_sim_time)}s`
      : "",
    typeof item.last_sample_sim_time === "number"
      ? `last=${formatMetricValue(item.last_sample_sim_time)}s`
      : "",
    serviceLatencyComponentTimeline(item)
  ].filter((part) => part.length > 0);
  return parts.join(" / ");
}

function computeTaskTimelineTraceTitle(
  item: RuntimeComputeTaskTimelineSummaryV1["items"][number]
): string {
  const stages = item.stages
    .map((stage) => {
      const time =
        typeof stage.sample_sim_time === "number"
          ? `@${formatMetricValue(stage.sample_sim_time)}s`
          : "";
      return `${stage.component}${time}=${formatMetricMilliseconds(stage.duration_s)}`;
    })
    .join(", ");
  return [
    `task=${item.task_id}`,
    item.compute_node_id ? `node=${item.compute_node_id}` : "",
    item.placement_status ? `placement=${item.placement_status}` : "",
    item.placement_bottleneck_resource
      ? `bottleneck=${item.placement_bottleneck_resource}`
      : "",
    `queue=${formatMetricMilliseconds(item.queue_delay_s)}`,
    `execution=${formatMetricMilliseconds(item.execution_delay_s)}`,
    `state=${item.queue_state}`,
    stages ? `stages=${stages}` : ""
  ]
    .filter((part) => part.length > 0)
    .join(" / ");
}

function serviceLatencyPlacementTrace(
  item: RuntimeServiceLatencyHistoryV1["items"][number]
): string {
  const parts = [
    item.compute_node_id ? `placement_node=${item.compute_node_id}` : "",
    item.service_placement_status ? `placement_status=${item.service_placement_status}` : "",
    item.service_placement_policy ? `placement_policy=${item.service_placement_policy}` : "",
    item.service_placement_bottleneck_resource
      ? `placement_bottleneck=${item.service_placement_bottleneck_resource}`
      : "",
    typeof item.service_placement_candidate_count === "number"
      ? `placement_candidates=${formatCount(
          item.service_placement_capable_candidate_count ?? 0
        )}/${formatCount(item.service_placement_candidate_count)}`
      : "",
    item.service_placement_candidate_queue_label
      ? `placement_queue=${item.service_placement_candidate_queue_label}`
      : ""
  ].filter((part) => part.length > 0);
  return parts.join(" / ");
}

function serviceLatencyPlacementLabel(
  item: RuntimeServiceLatencyHistoryV1["items"][number]
): string {
  return servicePlacementLabel({
    computeNodeId: item.compute_node_id,
    status: item.service_placement_status,
    policy: item.service_placement_policy,
    bottleneckResource: item.service_placement_bottleneck_resource,
    candidateCount: item.service_placement_candidate_count,
    capableCandidateCount: item.service_placement_capable_candidate_count,
    candidateQueueLabel: item.service_placement_candidate_queue_label
  });
}

function serviceDetailPlacementLabel(
  item: RuntimeServiceDetailPageV1["items"][number]
): string {
  return servicePlacementLabel({
    computeNodeId: item.compute_node_id,
    status: item.placement_status,
    policy: item.placement_policy,
    bottleneckResource: item.placement_bottleneck_resource,
    candidateCount: item.placement_candidate_count,
    capableCandidateCount: item.placement_capable_candidate_count,
    candidateQueueLabel: item.placement_candidate_queue_label
  });
}

function serviceDetailTraceTitle(
  item: RuntimeServiceDetailPageV1["items"][number]
): string {
  const stageLabels = item.stages
    .map((stage) => {
      const simTime =
        typeof stage.sample_sim_time === "number"
          ? `@${formatMetricValue(stage.sample_sim_time)}s`
          : "";
      return `${stage.component}${simTime}=${formatMetricMilliseconds(stage.duration_s)}`;
    })
    .join(", ");
  return [
    `service=${item.service_id}`,
    item.task_id ? `task=${item.task_id}` : "",
    item.input_flow_id ? `input=${item.input_flow_id}` : "",
    item.output_flow_id ? `output=${item.output_flow_id}` : "",
    item.input_route_id ? `input_route=${item.input_route_id}` : "",
    item.output_route_id ? `output_route=${item.output_route_id}` : "",
    item.compute_node_id ? `node=${item.compute_node_id}` : "",
    item.placement_status ? `placement=${item.placement_status}` : "",
    item.placement_bottleneck_resource
      ? `bottleneck=${item.placement_bottleneck_resource}`
      : "",
    `input_network=${formatMetricMilliseconds(item.input_network_latency_s)}`,
    `compute_queue=${formatMetricMilliseconds(item.compute_queue_delay_s)}`,
    `compute_execution=${formatMetricMilliseconds(item.compute_execution_delay_s)}`,
    `output_network=${formatMetricMilliseconds(item.output_network_latency_s)}`,
    `total=${formatMetricMilliseconds(item.total_latency_s)}`,
    stageLabels ? `stages=${stageLabels}` : ""
  ]
    .filter((part) => part.length > 0)
    .join(" / ");
}

function serviceLifecycleTerminalLabel(state: string, reason: string): string {
  const stateLabel =
    state === "COMPLETE"
      ? "完成"
      : state === "RUNNING"
        ? "运行中"
        : state === "INCOMPLETE"
          ? "未完整"
          : state;
  return reason ? `${stateLabel} / ${reason}` : stateLabel;
}

function serviceLifecycleStageStatusLabel(status: string): string {
  if (status === "OBSERVED") {
    return "已观测";
  }
  if (status === "PENDING") {
    return "等待";
  }
  if (status === "NOT_APPLICABLE") {
    return "不适用";
  }
  if (status === "UNKNOWN") {
    return "未知";
  }
  return status;
}

function serviceLifecycleStageLabel(label: string, component: string): string {
  if (label && label !== component) {
    return label;
  }
  if (component === "input_network") {
    return "输入网络";
  }
  if (component === "compute_queue") {
    return "计算排队";
  }
  if (component === "compute_execution") {
    return "计算执行";
  }
  if (component === "output_network") {
    return "输出网络";
  }
  return component;
}

function serviceLifecycleTraceTitle(
  item: RuntimeServiceLifecycleTraceV2["items"][number]
): string {
  const stages = item.stages.map(serviceLifecycleStageTitle).join(", ");
  return [
    `trace=${item.trace_id}`,
    `service=${item.service_id}`,
    item.task_id ? `task=${item.task_id}` : "",
    item.service_class ? `class=${item.service_class}` : "",
    item.input_flow_id ? `input=${item.input_flow_id}` : "",
    item.output_flow_id ? `output=${item.output_flow_id}` : "",
    item.compute_node_id ? `node=${item.compute_node_id}` : "",
    item.placement_status ? `placement=${item.placement_status}` : "",
    item.placement_bottleneck_resource
      ? `bottleneck=${item.placement_bottleneck_resource}`
      : "",
    `terminal=${item.terminal_state}`,
    item.terminal_state_reason ? `reason=${item.terminal_state_reason}` : "",
    `observed=${formatCount(item.observed_stage_count)}`,
    `pending=${formatCount(item.pending_stage_count)}`,
    stages ? `stages=${stages}` : ""
  ]
    .filter((part) => part.length > 0)
    .join(" / ");
}

function serviceLifecycleStageTitle(
  stage: RuntimeServiceLifecycleTraceV2["items"][number]["stages"][number]
): string {
  const simTime =
    typeof stage.sample_sim_time === "number"
      ? `@${formatMetricValue(stage.sample_sim_time)}s`
      : "";
  const route = stage.route_id ? ` route=${stage.route_id}` : "";
  const flow = stage.flow_id ? ` flow=${stage.flow_id}` : "";
  const node = stage.compute_node_id ? ` node=${stage.compute_node_id}` : "";
  return `${stage.component}${simTime}=${formatMetricMilliseconds(
    stage.duration_s
  )} ${stage.stage_status}${route}${flow}${node}`.trim();
}

function computeNodeDetailTraceTitle(
  item: RuntimeComputeNodeDetailPageV1["items"][number]
): string {
  return [
    `node=${item.node_id}`,
    `status=${item.status}`,
    `load=${formatRatioPercent(item.compute_load_ratio)}`,
    `fp32=${resourceUsageLabel(
      item.compute_used_gflops_fp32,
      item.compute_capacity_gflops_fp32,
      "GFLOPS"
    )}`,
    `gpu_fp32=${resourceUsageLabel(
      item.compute_used_gpu_tflops_fp32,
      item.compute_capacity_gpu_tflops_fp32,
      "TFLOPS"
    )}`,
    `npu_int8=${resourceUsageLabel(
      item.compute_used_npu_tops_int8,
      item.compute_capacity_npu_tops_int8,
      "TOPS"
    )}`,
    `memory=${resourceUsageLabel(
      item.compute_used_memory_gb,
      item.compute_capacity_memory_gb,
      "GB"
    )}`,
    `storage=${resourceUsageLabel(
      item.compute_used_storage_gb,
      item.compute_capacity_storage_gb,
      "GB"
    )}`,
    `tasks=${formatCount(item.running_task_count)}/${formatCount(
      item.finished_task_count
    )}`
  ].join(" / ");
}

function servicePlacementLabel(fields: {
  computeNodeId?: string;
  status?: string;
  policy?: string;
  bottleneckResource?: string;
  candidateCount?: number | null;
  capableCandidateCount?: number | null;
  candidateQueueLabel?: string;
}): string {
  if (
    !fields.computeNodeId &&
    !fields.status &&
    !fields.policy &&
    !fields.bottleneckResource &&
    typeof fields.candidateCount !== "number" &&
    !fields.candidateQueueLabel
  ) {
    return "无计算放置";
  }
  const parts = [
    fields.computeNodeId ? `节点 ${fields.computeNodeId}` : null,
    fields.status ? dataPanelPlacementStatusLabel(fields.status) : null,
    fields.bottleneckResource ? `瓶颈 ${fields.bottleneckResource}` : null,
    typeof fields.candidateCount === "number"
      ? `候选 ${formatCount(fields.capableCandidateCount ?? 0)}/${formatCount(
          fields.candidateCount
        )}`
      : null,
    fields.candidateQueueLabel ? `队列 ${fields.candidateQueueLabel}` : null
  ].filter((value): value is string => value !== null);
  return parts.length > 0 ? parts.join(" / ") : "无计算放置";
}

function dataPanelPlacementStatusLabel(status: string): string {
  switch (status) {
    case "PLACED":
      return "已放置";
    case "QUEUED":
      return "排队";
    case "REJECTED":
      return "拒绝";
    default:
      return status;
  }
}

function serviceLatencyComponentTimeline(
  item: RuntimeServiceLatencyHistoryV1["items"][number]
): string {
  const components = item.component_timeline ?? [];
  if (components.length === 0) {
    return "";
  }
  const labels = components.map((component) => {
    const simTime =
      typeof component.sample_sim_time === "number"
        ? `@${formatMetricValue(component.sample_sim_time)}s`
        : "";
    return `${component.component}${simTime}=${formatMetricMilliseconds(component.duration_s)}`;
  });
  return `timeline=${labels.join(", ")}`;
}

function serviceLatencyTimelineItems(
  item: RuntimeServiceLatencyHistoryV1["items"][number]
): readonly DataPanelServiceLatencyTimelineItem[] {
  return (item.component_timeline ?? []).map((component) => {
    const timeLabel =
      typeof component.sample_sim_time === "number"
        ? `${formatMetricValue(component.sample_sim_time)}s`
        : "n/a";
    const durationLabel = formatMetricMilliseconds(component.duration_s);
    const routeLabel = component.route_id ? `route=${component.route_id}` : "";
    const metricLabel = component.metric_name ? `metric=${component.metric_name}` : "";
    return {
      component: component.component,
      label: serviceLatencyComponentLabel(component.component),
      timeLabel,
      durationLabel,
      traceTitle: [
        `component=${component.component}`,
        metricLabel,
        `time=${timeLabel}`,
        `duration=${durationLabel}`,
        routeLabel
      ]
        .filter((part) => part.length > 0)
        .join(" / ")
    };
  });
}

function serviceLatencyComponentLabel(component: string): string {
  switch (component) {
    case "input_network":
      return "输入网络";
    case "compute_queue":
      return "计算排队";
    case "compute_execution":
      return "计算执行";
    case "output_network":
      return "输出网络";
    case "total":
      return "总延迟";
    default:
      return component;
  }
}

function formatPreciseMetricValue(value: number): string {
  return value.toLocaleString("zh-CN", {
    maximumFractionDigits: 3,
    minimumFractionDigits: 0
  });
}

function hasBackendNetworkQualityMetrics(
  metrics: RuntimeMetricsSummary | null | undefined
): boolean {
  return (
    metricNumber(metrics, "network_quality_effective_throughput_mbps") !== undefined ||
    metricNumber(metrics, "network_quality_estimated_delivered_throughput_mbps") !==
      undefined ||
    metricNumber(metrics, "network_quality_effective_latency_avg_s") !== undefined ||
    metricNumber(metrics, "network_quality_route_latency_avg_s") !== undefined ||
    metricNumber(metrics, "network_quality_effective_loss_proxy_rate") !== undefined ||
    metricNumber(metrics, "network_quality_loss_proxy_rate") !== undefined ||
    metricNumber(metrics, "network_quality_effective_delay_variation_proxy_s") !==
      undefined ||
    metricNumber(metrics, "network_quality_delay_variation_proxy_s") !== undefined
  );
}

function formatNetworkQualityProxyNote(
  metrics: RuntimeMetricsSummary | null | undefined,
  networkProvenance: RuntimeNetworkQualityProvenanceV1 | null | undefined = undefined
): string {
  const note = networkProvenance?.proxy_note || metrics?.network_quality_proxy_note;
  const provenance = formatNetworkQualityProvenanceNote(metrics, networkProvenance);
  const suffix = provenance ? ` ${provenance}` : "";
  if (typeof note === "string" && note.trim().length > 0) {
    if (note === "Flow-level proxy only; no packet-level simulation is performed.") {
      return `后端流级代理指标；未进行包级仿真。${suffix}`;
    }
    return `${note}${suffix}`;
  }
  return `后端网络质量指标为流级代理模型；未进行包级仿真。${suffix}`;
}

function formatNetworkQualityProvenanceNote(
  metrics: RuntimeMetricsSummary | null | undefined,
  networkProvenance: RuntimeNetworkQualityProvenanceV1 | null | undefined = undefined
): string {
  const throughput =
    networkProvenance?.sources.throughput?.label ||
    metricString(metrics, "network_quality_throughput_source_label");
  const latency =
    networkProvenance?.sources.latency?.label ||
    metricString(metrics, "network_quality_latency_source_label");
  const loss =
    networkProvenance?.sources.loss?.label ||
    metricString(metrics, "network_quality_loss_source_label");
  const jitter =
    networkProvenance?.sources.delay_variation?.label ||
    metricString(metrics, "network_quality_delay_variation_source_label");
  if (!throughput && !latency && !loss && !jitter) {
    return "";
  }
  return `来源：吞吐量 ${throughput ?? "未声明"}；时延 ${
    latency ?? "未声明"
  }；丢包 ${loss ?? "未声明"}；抖动 ${jitter ?? "未声明"}。`;
}

const POSITIVE_PROXY_REASON_LABEL = "当前代理指标为正值";

function positiveMetric(value: number | undefined): number | undefined {
  return value !== undefined && value > 0 ? value : undefined;
}

function metricString(
  metrics: RuntimeMetricsSummary | null | undefined,
  key: string
): string | undefined {
  const value = metrics?.[key];
  return typeof value === "string" && value.trim().length > 0 ? value : undefined;
}

function metricBoolean(
  metrics: RuntimeMetricsSummary | null | undefined,
  key: string
): boolean | undefined {
  const value = metrics?.[key];
  return typeof value === "boolean" ? value : undefined;
}

function isSpaceLink(link: { source_id: string; target_id: string }): boolean {
  return link.source_id.startsWith("sat-") && link.target_id.startsWith("sat-");
}

function isAccessLink(link: { source_id: string; target_id: string }): boolean {
  return (
    (link.source_id.startsWith("sat-") && link.target_id.startsWith("user-")) ||
    (link.source_id.startsWith("user-") && link.target_id.startsWith("sat-"))
  );
}

function couplingHealthScore(signals: {
  hasOrbit: boolean;
  hasGroundUsers: boolean;
  hasLinks: boolean;
  hasRoutes: boolean;
  hasCompute: boolean;
  hasEvents: boolean;
}): number {
  const values = [
    signals.hasOrbit,
    signals.hasGroundUsers,
    signals.hasLinks,
    signals.hasRoutes,
    signals.hasCompute,
    signals.hasEvents
  ];
  return Math.round((values.filter(Boolean).length / values.length) * 100);
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

function runtimeModeLabel(mode: RuntimeStatusPayload["mode"]): string {
  if (mode === "ACCELERATED") {
    return "加速模式";
  }
  if (mode === "PAUSED") {
    return "暂停模式";
  }
  return "实时模式";
}

export interface DataPanelReproducibilityDisplay {
  primaryLabel: string;
  secondaryLabel: string;
}

export function buildDataPanelReproducibilityDisplay(
  manifest: RuntimeReproducibilityManifestV1 | null | undefined
): DataPanelReproducibilityDisplay | null {
  if (manifest === null || manifest === undefined) {
    return null;
  }
  const shortHash = shortRuntimeHash(manifest.manifest_hash);
  const artifactCount =
    typeof manifest.artifact_count === "number"
      ? manifest.artifact_count
      : manifest.artifacts.length;
  return {
    primaryLabel: `${manifest.session_id} / ${shortHash}`,
    secondaryLabel: `${manifest.artifact_policy} / ${artifactCount} artifacts`
  };
}

export interface DataPanelUserConfigurationContractDisplay {
  tone: "match" | "pending" | "error";
  sourceLabel: string;
  summaryLabel: string;
  statusLabel: string;
  detailLabel: string;
  metaLabels: readonly string[];
  fieldSections: readonly DataPanelUserConfigurationFieldSectionDisplay[];
  referenceSections: readonly DataPanelUserConfigurationFieldSectionDisplay[];
  referenceRows: readonly DataPanelUserConfigurationReferenceRowDisplay[];
  referenceSummaryLabels: readonly string[];
  referenceBoundaryLabels: readonly string[];
  referenceWorkflowLabels: readonly string[];
  schemaHref: string;
  templatesHref: string;
  referenceHref: string;
  exportHref: string;
}

export interface DataPanelUserConfigurationFieldSectionDisplay {
  sectionPath: string;
  purpose: string;
  metaLabels: readonly string[];
  sampleFields: readonly DataPanelUserConfigurationFieldDisplay[];
}

export interface DataPanelUserConfigurationFieldDisplay {
  path: string;
  label: string;
  description: string;
}

export interface DataPanelUserConfigurationReferenceRowDisplay {
  path: string;
  section: string;
  label: string;
  description: string;
  typeLabel: string;
  surfaceLabel: string;
  defaultValueLabel: string;
  currentValueLabel: string;
  validationLabel: string;
}

export function buildDataPanelUserConfigurationContractDisplay(
  schema: UserConfigurationSchemaV2 | null | undefined,
  templates: UserConfigurationTemplateCatalogV1 | null | undefined,
  reference: UserConfigurationReferenceV1 | null | undefined,
  exported: UserConfigurationExportV1 | null | undefined,
  loading = false,
  error: string | null | undefined = null
): DataPanelUserConfigurationContractDisplay | null {
  if (
    loading &&
    schema == null &&
    templates == null &&
    reference == null &&
    exported == null
  ) {
    return {
      tone: "pending",
      sourceLabel: "BACKEND_USER_CONFIGURATION",
      summaryLabel: "正在加载 schema、模板目录和当前配置导出",
      statusLabel: "加载中",
      detailLabel: "只读接口，不会修改当前配置",
      metaLabels: [
        "schema pending",
        "templates pending",
        "reference pending",
        "export pending"
      ],
      fieldSections: [],
      referenceSections: [],
      referenceRows: [],
      referenceSummaryLabels: [],
      referenceBoundaryLabels: [],
      referenceWorkflowLabels: [],
      schemaHref: userConfigurationSchemaHref(),
      templatesHref: userConfigurationTemplatesHref(),
      referenceHref: userConfigurationReferenceHref(),
      exportHref: userConfigurationExportHref()
    };
  }
  if (
    error !== null &&
    error !== undefined &&
    schema == null &&
    reference == null &&
    exported == null
  ) {
    return {
      tone: "error",
      sourceLabel: "BACKEND_USER_CONFIGURATION",
      summaryLabel: error,
      statusLabel: "配置契约加载失败",
      detailLabel: "请检查后端 /scenario/user-config/* 只读接口",
      metaLabels: [error],
      fieldSections: [],
      referenceSections: [],
      referenceRows: [],
      referenceSummaryLabels: [],
      referenceBoundaryLabels: [],
      referenceWorkflowLabels: [],
      schemaHref: userConfigurationSchemaHref(),
      templatesHref: userConfigurationTemplatesHref(),
      referenceHref: userConfigurationReferenceHref(),
      exportHref: userConfigurationExportHref()
    };
  }
  if (schema == null && templates == null && reference == null && exported == null) {
    return null;
  }
  const schemaId =
    reference?.schema_id ??
    schema?.schema_id ??
    templates?.schema_id ??
    exported?.schema_id ??
    "unknown";
  const fieldCount = reference?.field_count ?? schema?.field_count ?? 0;
  const keyFieldCount = reference?.key_field_count ?? schema?.key_field_count ?? 0;
  const fileOnlyFieldCount =
    reference?.file_only_field_count ?? schema?.file_only_field_count ?? 0;
  const templateCount = templates?.template_count ?? schema?.templates.length ?? 0;
  const configHash = exported?.config_hash ?? "";
  const validationOk = exported?.validation_ok ?? false;
  const source =
    reference?.source ??
    exported?.source ??
    templates?.source ??
    schema?.source ??
    "BACKEND_USER_CONFIGURATION";
  return {
    tone: validationOk || exported == null ? "match" : "error",
    sourceLabel: `${source} / ${schemaId}`,
    summaryLabel: `字段 ${formatCount(fieldCount)} / 关键 ${formatCount(
      keyFieldCount
    )} / 模板 ${formatCount(templateCount)}`,
    statusLabel: validationOk || exported == null ? "当前配置可复现" : "当前配置校验异常",
    detailLabel: exported
      ? `config ${shortRuntimeHash(configHash)} / ${exported.export_scope}`
      : "等待当前配置导出",
    metaLabels: [
      `unknown ${schema?.unknown_key_policy ?? exported?.unknown_key_policy ?? "REJECT"}`,
      `default ${schema?.defaulting_policy ?? exported?.defaulting_policy ?? "BACKEND"}`,
      `validation ${validationOk ? "ok" : exported == null ? "pending" : "failed"}`,
      `format ${reference?.format ?? schema?.format ?? exported?.format ?? "YAML_OR_JSON_MAPPING"}`,
      `file-only ${formatCount(fileOnlyFieldCount)}`,
      `reference ${shortRuntimeHash(reference?.reference_hash ?? "")}`
    ],
    fieldSections: buildDataPanelUserConfigurationFieldSections(schema),
    referenceSections: buildDataPanelUserConfigurationReferenceFieldSections(reference),
    referenceRows: buildDataPanelUserConfigurationReferenceFieldRows(reference),
    referenceSummaryLabels: buildDataPanelUserConfigurationReferenceSummaryLabels(reference),
    referenceBoundaryLabels: buildDataPanelUserConfigurationReferenceBoundaryLabels(reference),
    referenceWorkflowLabels: buildDataPanelUserConfigurationReferenceWorkflowLabels(reference),
    schemaHref: userConfigurationSchemaHref(),
    templatesHref: userConfigurationTemplatesHref(),
    referenceHref: userConfigurationReferenceHref(),
    exportHref: userConfigurationExportHref()
  };
}

export function buildDataPanelUserConfigurationFieldSections(
  schema: UserConfigurationSchemaV2 | null | undefined
): readonly DataPanelUserConfigurationFieldSectionDisplay[] {
  if (schema === null || schema === undefined || schema.fields.length === 0) {
    return [];
  }
  const fieldsBySection = new Map<string, typeof schema.fields>();
  schema.fields.forEach((field) => {
    const sectionPath = field.section || field.path.split(".")[0] || "root";
    fieldsBySection.set(sectionPath, [...(fieldsBySection.get(sectionPath) ?? []), field]);
  });
  const declaredSectionPaths = new Set(schema.root_sections.map((section) => section.path));
  const extraSections = [...fieldsBySection.keys()]
    .filter((sectionPath) => !declaredSectionPaths.has(sectionPath))
    .sort((left, right) => left.localeCompare(right));
  const sections = [
    ...schema.root_sections.map((section) => ({
      sectionPath: section.path,
      purpose: section.purpose
    })),
    ...extraSections.map((sectionPath) => ({
      sectionPath,
      purpose: "后端 schema 字段分组"
    }))
  ];
  const sectionDisplays: DataPanelUserConfigurationFieldSectionDisplay[] = [];
  sections.forEach(({ sectionPath, purpose }) => {
    const fields = fieldsBySection.get(sectionPath) ?? [];
    if (fields.length === 0) {
      return;
    }
    const keyFieldCount = fields.filter(
      (field) => field.editable_surface === "CONTROL_PANEL_KEY_FIELD"
    ).length;
    const fileOnlyFieldCount = fields.filter(
      (field) => field.editable_surface === "DETAILED_CONFIG_FILE_ONLY"
    ).length;
    sectionDisplays.push({
      sectionPath,
      purpose,
      metaLabels: [
        `字段 ${formatCount(fields.length)}`,
        `关键 ${formatCount(keyFieldCount)}`,
        `文件 ${formatCount(fileOnlyFieldCount)}`
      ],
      sampleFields: fields.slice(0, 4).map((field) => ({
        path: field.path,
        label: `${field.path} · ${field.label}`,
        description: field.description
      }))
    });
  });
  return sectionDisplays;
}

export function buildDataPanelUserConfigurationReferenceFieldSections(
  reference: UserConfigurationReferenceV1 | null | undefined
): readonly DataPanelUserConfigurationFieldSectionDisplay[] {
  if (
    reference === null ||
    reference === undefined ||
    reference.sections.length === 0
  ) {
    return [];
  }
  const fieldsByPath = new Map(
    reference.fields.map((field) => [field.path, field])
  );
  return reference.sections
    .filter((section) => section.field_count > 0)
    .map((section) => {
      const samplePaths = [
        ...section.key_paths.slice(0, 2),
        ...section.file_only_paths.slice(0, 2)
      ];
      return {
        sectionPath: section.section,
        purpose: section.purpose,
        metaLabels: [
          `字段 ${formatCount(section.field_count)}`,
          `关键 ${formatCount(section.key_field_count)}`,
          `文件 ${formatCount(section.file_only_field_count)}`
        ],
        sampleFields: samplePaths.map((path) => {
          const field = fieldsByPath.get(path);
          return {
            path,
            label: `${path} / ${field?.label ?? path}`,
            description:
              field?.description ??
              "Backend-owned user configuration reference field."
          };
        })
      };
    });
}

export function buildDataPanelUserConfigurationReferenceFieldRows(
  reference: UserConfigurationReferenceV1 | null | undefined
): readonly DataPanelUserConfigurationReferenceRowDisplay[] {
  if (
    reference === null ||
    reference === undefined ||
    reference.fields.length === 0
  ) {
    return [];
  }
  const sectionOrder = new Map(
    reference.sections.map((section, index) => [section.section, index])
  );
  return [...reference.fields]
    .sort((left, right) => {
      const leftSection = sectionOrder.get(left.section) ?? Number.MAX_SAFE_INTEGER;
      const rightSection = sectionOrder.get(right.section) ?? Number.MAX_SAFE_INTEGER;
      if (leftSection !== rightSection) {
        return leftSection - rightSection;
      }
      return left.path.localeCompare(right.path);
    })
    .map((field) => ({
      path: field.path,
      section: field.section || field.path.split(".")[0] || "root",
      label: field.label,
      description: field.description,
      typeLabel: formatUserConfigurationReferenceType(field),
      surfaceLabel: formatUserConfigurationReferenceSurface(field),
      defaultValueLabel: formatUserConfigurationReferenceValue(field.default_value),
      currentValueLabel: formatUserConfigurationReferenceValue(field.current_value),
      validationLabel:
        field.validation_rules.length > 0
          ? field.validation_rules.join(" / ")
          : "无额外规则"
    }));
}

export function buildDataPanelUserConfigurationReferenceSummaryLabels(
  reference: UserConfigurationReferenceV1 | null | undefined
): readonly string[] {
  if (reference === null || reference === undefined) {
    return [];
  }
  return [
    `reference ${shortRuntimeHash(reference.reference_hash)}`,
    `分区 ${formatCount(reference.section_count)}`,
    `字段 ${formatCount(reference.field_count)}`,
    `关键 ${formatCount(reference.key_field_count)}`,
    `文件 ${formatCount(reference.file_only_field_count)}`,
    `模板 ${formatCount(reference.template_profiles.length)}`
  ];
}

export function buildDataPanelUserConfigurationReferenceBoundaryLabels(
  reference: UserConfigurationReferenceV1 | null | undefined
): readonly string[] {
  if (reference === null || reference === undefined) {
    return [];
  }
  const boundaries = reference.model_boundaries;
  return [
    `语义源 ${boundaries.frontend_semantics_source}`,
    `Event Kernel ${boundaries.event_kernel_policy}`,
    boundaries.packet_level_simulation ? "包级仿真开启" : "无包级仿真",
    boundaries.external_simulators ? "外部仿真器开启" : "无外部仿真器",
    `禁用 ${boundaries.forbidden_integrations.join("/")}`
  ];
}

export function buildDataPanelUserConfigurationReferenceWorkflowLabels(
  reference: UserConfigurationReferenceV1 | null | undefined
): readonly string[] {
  if (reference === null || reference === undefined) {
    return [];
  }
  return [
    `UI ${reference.mutation_policy.ui_surface}`,
    `完整文件 ${reference.mutation_policy.full_file_surface}`,
    `校验 ${reference.mutation_policy.validate_endpoint}`,
    `应用 ${reference.mutation_policy.apply_commands.join("/")}`,
    ...reference.operator_workflow,
    ...reference.notes
  ];
}

function formatUserConfigurationReferenceType(
  field: UserConfigurationReferenceFieldV1
): string {
  return [field.value_type, field.unit].filter(Boolean).join(" / ");
}

function formatUserConfigurationReferenceSurface(
  field: UserConfigurationReferenceFieldV1
): string {
  const surface =
    field.ui_key_field || field.editable_surface === "CONTROL_PANEL_KEY_FIELD"
      ? "关键控件"
      : "详细配置文件";
  const required = field.required_in_user_file ? "文件必填" : "可省略";
  return `${surface} / ${required}`;
}

function formatUserConfigurationReferenceValue(value: unknown): string {
  if (value === undefined) {
    return "未提供";
  }
  if (value === null) {
    return "null";
  }
  if (typeof value === "number") {
    return Number.isInteger(value) ? formatCount(value) : formatPreciseMetricValue(value);
  }
  if (typeof value === "boolean") {
    return value ? "true" : "false";
  }
  if (typeof value === "string") {
    return value.length > 0 ? value : "\"\"";
  }
  const encoded = JSON.stringify(value);
  if (encoded === undefined) {
    return String(value);
  }
  return encoded.length > 96 ? `${encoded.slice(0, 93)}...` : encoded;
}

export interface DataPanelUserConfigurationValidationDisplay {
  tone: "match" | "pending" | "error";
  statusLabel: string;
  detailLabel: string;
  metaLabels: readonly string[];
  readinessLabels: readonly string[];
  changeLabels: readonly string[];
  changeRows: readonly DataPanelUserConfigurationChangeRow[];
  errorLabels: readonly string[];
}

export interface DataPanelUserConfigurationChangeRow {
  path: string;
  changeType: string;
  valueLabel: string;
}

export function buildDataPanelUserConfigurationValidationDisplay(
  report: UserConfigurationValidationReportV1 | null | undefined,
  pending = false,
  error: string | null | undefined = null,
  applyStatus: string | null | undefined = null
): DataPanelUserConfigurationValidationDisplay | null {
  if (pending) {
    return {
      tone: "pending",
      statusLabel: "后端预检中",
      detailLabel: "正在校验 JSON 映射，不会应用配置",
      metaLabels: ["mutation VALIDATE_ONLY_NO_APPLY"],
      readinessLabels: [],
      changeLabels: [],
      changeRows: [],
      errorLabels: []
    };
  }
  if (error !== null && error !== undefined) {
    return {
      tone: "error",
      statusLabel: "预检请求失败",
      detailLabel: error,
      metaLabels: ["mutation none", `endpoint ${userConfigurationValidateHref()}`],
      readinessLabels: [],
      changeLabels: [],
      changeRows: [],
      errorLabels: [error]
    };
  }
  if (report === null || report === undefined) {
    return null;
  }
  const normalizedHash = report.normalized_config_hash ?? "";
  const applyCommand = report.apply_command;
  const applyLabels =
    report.ok && selectUserConfigurationApplyPayload(report) !== null
      ? [
          `apply ${applyCommand.type}/${applyCommand.action}`,
          applyCommand.payload_source
            ? `payload ${applyCommand.payload_source}`
            : "payload unspecified",
          applyCommand.runtime_effect ? `effect ${applyCommand.runtime_effect}` : null,
          applyStatus
        ].filter((label): label is string => label !== null && label !== undefined)
      : [];
  const changeDisplay = buildUserConfigurationChangeDisplay(report);
  const textParseLabels = buildUserConfigurationTextParseLabels(report);
  return {
    tone: report.ok ? "match" : "error",
    statusLabel: report.ok ? "配置可通过预检" : "配置预检未通过",
    detailLabel: report.ok
      ? `normalized ${shortRuntimeHash(normalizedHash)}`
      : `${formatCount(report.error_count)} 个错误`,
    metaLabels: [
      `scope ${report.validation_scope}`,
      `mutation ${report.mutation_policy}`,
      `unknown ${report.unknown_key_policy}`,
      `default ${report.defaulting_policy}`,
      ...textParseLabels,
      ...applyLabels
    ],
    readinessLabels: buildUserConfigurationApplyReadinessLabels(report),
    changeLabels: changeDisplay.labels,
    changeRows: changeDisplay.rows,
    errorLabels: report.errors.map((item) => `${item.source}: ${item.message}`)
  };
}

export function userConfigurationTextEndpointFormat(
  mode: UserConfigurationPreflightMode
): "auto" | "json" | "yaml" {
  if (mode === "yaml_text") {
    return "yaml";
  }
  if (mode === "json_text") {
    return "json";
  }
  return "auto";
}

export function userConfigurationPreflightModeEnabled(
  mode: UserConfigurationPreflightMode,
  mappingValidator:
    | ((candidate: unknown) => Promise<UserConfigurationValidationReportV1>)
    | undefined,
  textValidator:
    | ((text: string, format: "auto" | "json" | "yaml") => Promise<UserConfigurationValidationReportV1>)
    | undefined
): boolean {
  if (mode === "json_mapping") {
    return mappingValidator !== undefined;
  }
  return textValidator !== undefined;
}

function buildUserConfigurationTextParseLabels(
  report: UserConfigurationValidationReportV1
): readonly string[] {
  const textParse = report.text_parse;
  if (textParse === null || textParse === undefined) {
    return [];
  }
  const detected = textParse.detected_format ?? "none";
  return [
    `text ${textParse.ok ? "parsed" : "parse_failed"}`,
    `format ${detected}`,
    `requested ${textParse.requested_format}`,
    `endpoint ${userConfigurationValidateTextHref(textParse.requested_format as "auto" | "json" | "yaml")}`
  ];
}

function buildUserConfigurationApplyReadinessLabels(
  report: UserConfigurationValidationReportV1
): readonly string[] {
  const readiness = report.apply_readiness;
  if (!report.ok || readiness === null || readiness === undefined) {
    return [];
  }
  return [
    readiness.can_apply ? `可应用 ${readiness.readiness}` : `不可应用 ${readiness.readiness}`,
    `runtime ${readiness.controller_status}/${readiness.lifecycle_state}`,
    `建议 ${readiness.recommended_action}`,
    readiness.requires_confirmation ? "需要确认" : "无需额外确认",
    `session ${readiness.session_effect}`,
    `stream ${readiness.stream_effect}`,
    readiness.reason
  ];
}

function buildUserConfigurationChangeDisplay(
  report: UserConfigurationValidationReportV1
): {
  labels: readonly string[];
  rows: readonly DataPanelUserConfigurationChangeRow[];
} {
  const summary = report.change_summary;
  if (!report.ok || summary === null || summary === undefined) {
    return { labels: [], rows: [] };
  }
  const sectionLabels = Object.entries(summary.section_counts)
    .sort(([left], [right]) => left.localeCompare(right))
    .map(([section, count]) => `${section} ${formatCount(count)}`);
  const hiddenLabel =
    summary.hidden_change_count > 0
      ? `隐藏 ${formatCount(summary.hidden_change_count)} 项`
      : null;
  return {
    labels: [
      `变更 ${formatCount(summary.changed_field_count)} 字段`,
      `预览 ${formatCount(summary.change_count)} / ${formatCount(summary.preview_limit)}`,
      hiddenLabel,
      ...sectionLabels
    ].filter((label): label is string => label !== null),
    rows: summary.changes.slice(0, 8).map((item) => ({
      path: item.path,
      changeType: item.change_type,
      valueLabel: `${formatUserConfigurationChangeValue(
        item.current_value
      )} -> ${formatUserConfigurationChangeValue(item.candidate_value)}`
    }))
  };
}

function formatUserConfigurationChangeValue(value: unknown): string {
  if (value === null || value === undefined) {
    return "null";
  }
  if (typeof value === "string") {
    return value;
  }
  if (typeof value === "number") {
    return Number.isInteger(value) ? formatCount(value) : formatPreciseMetricValue(value);
  }
  if (typeof value === "boolean") {
    return value ? "true" : "false";
  }
  const encoded = JSON.stringify(value);
  if (typeof encoded !== "string") {
    return String(value);
  }
  return encoded.length > 96 ? `${encoded.slice(0, 93)}...` : encoded;
}

export function selectUserConfigurationApplyPayload(
  report: UserConfigurationValidationReportV1 | null | undefined
): Record<string, unknown> | null {
  if (report === null || report === undefined || !report.ok) {
    return null;
  }
  if (report.apply_command.requires_preflight_ok === false) {
    return null;
  }
  if (report.apply_command.requires_explicit_user_action !== true) {
    return null;
  }
  const payloadSource = report.apply_command.payload_source ?? "normalized_config";
  if (payloadSource !== "normalized_config") {
    return null;
  }
  if (
    report.normalized_config === null ||
    typeof report.normalized_config !== "object" ||
    Array.isArray(report.normalized_config)
  ) {
    return null;
  }
  return report.normalized_config;
}

export interface DataPanelConfigurationExplanationDisplay {
  sourceLabel: string;
  summaryLabel: string;
  determinismLabel: string;
  boundaryLabel: string;
  surfaces: readonly DataPanelConfigurationExplanationSurfaceDisplay[];
  sections: readonly DataPanelConfigurationExplanationSectionDisplay[];
}

export interface DataPanelConfigurationExplanationSurfaceDisplay {
  surface: string;
  label: string;
  purpose: string;
}

export interface DataPanelConfigurationExplanationSectionDisplay {
  section: string;
  title: string;
  currentValueLabel: string;
  sourceFieldsLabel: string;
  excludedSemanticsLabel: string;
}

export interface DataPanelInformationArchitectureDisplay {
  sourceLabel: string;
  summaryLabel: string;
  policyLabel: string;
  layoutLabel: string;
  sections: readonly DataPanelInformationArchitectureSectionDisplay[];
}

export interface DataPanelInformationArchitectureSectionDisplay {
  section: string;
  title: string;
  purpose: string;
  sourcesLabel: string;
  surfacesLabel: string;
}

export function buildDataPanelInformationArchitectureDisplay(
  architecture: DashboardInformationArchitectureV3 | null | undefined
): DataPanelInformationArchitectureDisplay | null {
  if (architecture === null || architecture === undefined) {
    return null;
  }
  const sections = [...architecture.sections].sort(
    (left, right) =>
      left.priority - right.priority || left.section.localeCompare(right.section)
  );
  return {
    sourceLabel: `${architecture.source} / ${architecture.architecture_id}`,
    summaryLabel: `${formatCount(sections.length)} 个态势分区 / ${architecture.frontend_policy}`,
    policyLabel: architecture.backend_source_of_truth
      ? "后端为语义源；前端只做格式化"
      : "前端需要校验语义来源",
    layoutLabel: `${architecture.layout_policy.page_scroll ? "整页滚动" : "固定视窗"} / ${
      architecture.layout_policy.large_scale_policy
    }`,
    sections: sections.map((section) => ({
      section: section.section,
      title: `${section.section} · ${section.title_zh}`,
      purpose: section.purpose,
      sourcesLabel: section.primary_data_sources.join(" / "),
      surfacesLabel: `${section.detail_surfaces.slice(0, 3).join(" / ")} · ${
        section.scale_behavior
      }`
    }))
  };
}

export function buildDataPanelConfigurationExplanationDisplay(
  explanation: ConfigurationExplanationV2 | null | undefined
): DataPanelConfigurationExplanationDisplay | null {
  if (explanation === null || explanation === undefined) {
    return null;
  }
  const forbidden = explanation.forbidden_integrations.join("/");
  return {
    sourceLabel: `${explanation.source} / ${explanation.schema_id}`,
    summaryLabel: `${formatCount(explanation.configuration_surfaces.length)} 个配置入口 / ${formatCount(
      explanation.section_explanations.length
    )} 个语义分组 / ${explanation.mutation_policy}`,
    determinismLabel: `seed ${explanation.determinism.seed_source} / unknown ${explanation.determinism.unknown_key_policy} / default ${explanation.determinism.defaulting_policy}`,
    boundaryLabel: `${forbidden} 禁止；${
      explanation.packet_level_simulation ? "含包级仿真" : "无包级仿真"
    }`,
    surfaces: explanation.configuration_surfaces.map((surface) => ({
      surface: surface.surface,
      label: `${surface.surface} · ${surface.source}`,
      purpose: surface.purpose
    })),
    sections: explanation.section_explanations.map((section) => ({
      section: section.section,
      title: `${section.section} · ${section.title}`,
      currentValueLabel: formatConfigurationExplanationCurrentValues(
        section.current_values
      ),
      sourceFieldsLabel: section.source_fields.join(" / "),
      excludedSemanticsLabel:
        section.excluded_semantics.length > 0
          ? `排除 ${section.excluded_semantics.join(" / ")}`
          : "无额外排除项"
    }))
  };
}

function formatConfigurationExplanationCurrentValues(
  values: ConfigurationExplanationV2["section_explanations"][number]["current_values"]
): string {
  const entries = Object.entries(values).filter(([, value]) => value !== null);
  if (entries.length === 0) {
    return "当前值等待后端同步";
  }
  return entries
    .slice(0, 4)
    .map(([key, value]) => `${key}=${formatConfigurationExplanationValue(value)}`)
    .join(" / ");
}

function formatConfigurationExplanationValue(
  value: string | number | boolean | readonly string[] | null
): string {
  if (Array.isArray(value)) {
    return value.join(",");
  }
  if (value !== null && typeof value === "object") {
    return [...value].join(",");
  }
  if (typeof value === "number") {
    return Number.isInteger(value) ? formatCount(value) : formatPreciseMetricValue(value);
  }
  if (typeof value === "boolean") {
    return value ? "true" : "false";
  }
  return value ?? "null";
}

export interface DataPanelExportHistoryDisplay {
  primaryLabel: string;
  secondaryLabel: string;
}

export function buildDataPanelExportHistoryDisplay(
  history: RuntimeExportHistoryV1 | null | undefined
): DataPanelExportHistoryDisplay | null {
  const latest = history?.latest_export;
  if (latest === null || latest === undefined) {
    return null;
  }
  const exportName = latest.archive_filename || latest.package_id;
  const exportHash = latest.archive_sha256 || latest.manifest_hash;
  return {
    primaryLabel: `${latest.export_type} / ${exportName}`,
    secondaryLabel: `t=${formatPreciseMetricValue(
      latest.current_sim_time
    )}s / events=${formatCount(latest.processed_event_count)} / ${shortRuntimeHash(exportHash)}`
  };
}

export interface DataPanelExportCatalogDisplay {
  sourceLabel: string;
  summaryLabel: string;
  rows: readonly DataPanelExportCatalogRow[];
}

export interface DataPanelExportCatalogRow {
  key: string;
  typeLabel: string;
  packageId: string;
  simTimeLabel: string;
  eventCountLabel: string;
  archiveLabel: string;
  hashLabel: string;
  recordHref: string;
  manifestHref: string;
  reviewSummaryHref: string;
  archiveHref: string | null;
  compareHref: string;
  restorePreflightHref: string;
}

export interface DataPanelExportArtifactHealthDisplay {
  packageId: string;
  sourceLabel: string;
  summaryLabel: string;
  rows: readonly DataPanelExportArtifactHealthRow[];
}

export interface DataPanelExportArtifactHealthRow {
  filename: string;
  roleLabel: string;
  statusLabel: string;
  sizeLabel: string;
  hashLabel: string;
  href: string | null;
  required: boolean;
  present: boolean;
  title: string;
}

export interface DataPanelExportRouteComparisonReviewArtifactDisplay {
  packageId: string;
  tone: "match" | "different";
  statusLabel: string;
  summaryLabel: string;
  hashLabels: readonly string[];
  artifactHref: string | null;
  artifactTitle: string;
}

export interface DataPanelExportPackageAuditIndexArtifactDisplay {
  packageId: string;
  tone: "match" | "different";
  statusLabel: string;
  summaryLabel: string;
  hashLabels: readonly string[];
  artifactHref: string | null;
  artifactTitle: string;
}

export interface DataPanelExportPackageHandoffReportArtifactDisplay {
  packageId: string;
  tone: "match" | "different";
  statusLabel: string;
  summaryLabel: string;
  hashLabels: readonly string[];
  artifactHref: string | null;
  artifactTitle: string;
}

export interface DataPanelExportScenarioReviewBundleDisplay {
  packageId: string;
  tone: "match" | "different";
  statusLabel: string;
  summaryLabel: string;
  bundleHref: string;
  scenarioLabels: readonly string[];
  configurationLabels: readonly string[];
  evidenceLabels: readonly string[];
  boundaryLabels: readonly string[];
  workflowRows: readonly DataPanelExportScenarioReviewWorkflowRow[];
  warningLabels: readonly string[];
}

export interface DataPanelExportScenarioReviewBundleStatus {
  tone: "match" | "different" | "pending" | "error";
  statusLabel: string;
  summaryLabel: string;
  bundleHref: string | null;
  scenarioLabels: readonly string[];
  configurationLabels: readonly string[];
  evidenceLabels: readonly string[];
  boundaryLabels: readonly string[];
  workflowRows: readonly DataPanelExportScenarioReviewWorkflowRow[];
  warningLabels: readonly string[];
}

export interface DataPanelExportScenarioReviewWorkflowRow {
  stepLabel: string;
  statusLabel: string;
  detailLabel: string;
  href: string | null;
  title: string;
  tone: "match" | "different" | "pending";
}

export interface DataPanelExportScenarioReviewChecklistStatusDisplay {
  tone: "match" | "different" | "pending" | "error";
  statusLabel: string;
  summaryLabel: string;
  warningLabels: readonly string[];
}

export interface DataPanelExportReviewCompletionSummaryDisplay {
  tone: "match" | "different" | "pending" | "error";
  statusLabel: string;
  summaryLabel: string;
  evidenceLabels: readonly string[];
  warningLabels: readonly string[];
}

export interface DataPanelExportPackageAuditIndexDisplay {
  packageId: string;
  tone: "match" | "different";
  statusLabel: string;
  summaryLabel: string;
  auditHref: string;
  manifestLabels: readonly string[];
  configurationLabels: readonly string[];
  boundaryLabels: readonly string[];
  diagnosticsLabels: readonly string[];
  routeReviewLabels: readonly string[];
  artifactRows: readonly DataPanelExportPackageAuditIndexArtifactRow[];
  artifactSummaryLabel: string;
  warningLabels: readonly string[];
}

export interface DataPanelExportPackageAuditIndexStatus {
  tone: "match" | "different" | "pending" | "error";
  statusLabel: string;
  summaryLabel: string;
  auditHref: string | null;
  manifestLabels: readonly string[];
  configurationLabels: readonly string[];
  boundaryLabels: readonly string[];
  diagnosticsLabels: readonly string[];
  routeReviewLabels: readonly string[];
  artifactRows: readonly DataPanelExportPackageAuditIndexArtifactRow[];
  artifactSummaryLabel: string;
  warningLabels: readonly string[];
}

export interface DataPanelExportPackageAuditIndexArtifactRow {
  filename: string;
  sizeLabel: string;
  hashLabel: string;
}

export interface DataPanelExportRouteComparisonReviewReportDisplay {
  packageId: string;
  tone: "match" | "different";
  statusLabel: string;
  summaryLabel: string;
  metaLabels: readonly string[];
  recordRows: readonly DataPanelExportRouteComparisonReviewReportRow[];
  reportHref: string;
  filterLabel: string;
  pageCursor: number;
  pageLimit: number;
  previousCursor: number;
  nextCursor: number;
  canPreviousPage: boolean;
  canNextPage: boolean;
}

export interface DataPanelExportRouteComparisonReviewReportStatus {
  tone: "match" | "different" | "pending" | "error";
  statusLabel: string;
  summaryLabel: string;
  metaLabels: readonly string[];
  recordRows: readonly DataPanelExportRouteComparisonReviewReportRow[];
  reportHref: string | null;
  filterLabel: string;
  pageCursor: number;
  pageLimit: number;
  previousCursor: number;
  nextCursor: number;
  canPreviousPage: boolean;
  canNextPage: boolean;
}

export interface DataPanelExportRouteComparisonReviewReportRow {
  routeId: string;
  tone: "match" | "different";
  statusLabel: string;
  hashLabel: string;
  noteLabel: string;
}

export interface DataPanelExportRouteComparisonReviewReportOptions {
  cursor?: number;
  limit?: number;
  query?: string;
  status?: DataPanelRouteComparisonReviewReportStatusFilter;
}

export function buildDataPanelExportCatalogDisplay(
  catalog: RuntimeExportCatalogV1 | null | undefined,
  limit = 6
): DataPanelExportCatalogDisplay | null {
  if (catalog === null || catalog === undefined) {
    return null;
  }
  const rows = [...catalog.records]
    .sort((left, right) => {
      if (right.current_sim_time !== left.current_sim_time) {
        return right.current_sim_time - left.current_sim_time;
      }
      if (right.processed_event_count !== left.processed_event_count) {
        return right.processed_event_count - left.processed_event_count;
      }
      if (left.catalog_key < right.catalog_key) {
        return -1;
      }
      if (left.catalog_key > right.catalog_key) {
        return 1;
      }
      return 0;
    })
    .slice(0, Math.max(0, limit))
    .map((record) => {
      const exportHash = record.archive_sha256 || record.manifest_hash;
      return {
        key: record.catalog_key,
        typeLabel: record.export_type,
        packageId: record.package_id,
        simTimeLabel: `${formatPreciseMetricValue(record.current_sim_time)} s`,
        eventCountLabel: formatCount(record.processed_event_count),
        archiveLabel: record.archive_filename || "未生成归档",
        hashLabel: shortRuntimeHash(exportHash),
        recordHref: runtimeExportPackageRecordHref(record.package_id),
        manifestHref: runtimeExportPackageManifestHref(record.package_id),
        reviewSummaryHref: runtimeExportPackageReviewSummaryHref(record.package_id),
        archiveHref: record.archive_filename
          ? runtimeExportPackageArchiveHref(record.package_id)
          : null,
        compareHref: runtimeExportPackageCompareHref(record.package_id),
        restorePreflightHref: runtimeExportRestorePreflightHref(record.package_id)
      };
    });
  return {
    sourceLabel: `${catalog.source} / ${catalog.catalog_scope}`,
    summaryLabel: `已登记 ${formatCount(catalog.record_count)} 条 / 显示 ${formatCount(
      rows.length
    )} 条 / catalog ${shortRuntimeHash(catalog.catalog_hash)}`,
    rows
  };
}

export function buildDataPanelExportRouteComparisonReviewArtifactDisplay(
  catalog: RuntimeExportCatalogV1 | null | undefined,
  selectedPackageId: string | null | undefined,
  latestSavedReportHash: string | null | undefined = null
): DataPanelExportRouteComparisonReviewArtifactDisplay | null {
  if (
    catalog === null ||
    catalog === undefined ||
    selectedPackageId === null ||
    selectedPackageId === undefined
  ) {
    return null;
  }
  const record = selectRuntimeExportCatalogRecordForPackage(catalog, selectedPackageId);
  if (record === null) {
    return null;
  }
  const reportFile =
    record.files.find(
      (file) =>
        file.filename === ROUTE_COMPARISON_REVIEW_REPORT_FILENAME ||
        file.name === "route_comparison_review_report_v1"
    ) ?? null;
  const reportHashLabel =
    latestSavedReportHash !== null && latestSavedReportHash !== undefined
      ? `report ${shortRuntimeHash(latestSavedReportHash)}`
      : "report hash waiting";
  if (reportFile === null) {
    return {
      packageId: selectedPackageId,
      tone: "different",
      statusLabel: "review report not saved",
      summaryLabel: `${selectedPackageId} / catalog file missing / ${reportHashLabel}`,
      hashLabels: [
        `catalog ${shortRuntimeHash(catalog.catalog_hash)}`,
        `package ${record.export_type}`,
        reportHashLabel
      ],
      artifactHref: null,
      artifactTitle: `${ROUTE_COMPARISON_REVIEW_REPORT_FILENAME} is not present in the selected package catalog.`
    };
  }
  return {
    packageId: selectedPackageId,
    tone: "match",
    statusLabel: "review report artifact present",
    summaryLabel: `${selectedPackageId} / ${formatRuntimeExportFileBytes(
      reportFile.bytes
    )} / file ${shortRuntimeHash(reportFile.sha256)}`,
    hashLabels: [
      `catalog ${shortRuntimeHash(catalog.catalog_hash)}`,
      `file ${shortRuntimeHash(reportFile.sha256)}`,
      reportHashLabel
    ],
    artifactHref: runtimeExportPackageFileHref(selectedPackageId, reportFile.filename),
    artifactTitle: `${reportFile.filename} / ${formatRuntimeExportFileBytes(
      reportFile.bytes
    )} / ${reportFile.sha256}`
  };
}

export function buildDataPanelExportPackageAuditIndexArtifactDisplay(
  catalog: RuntimeExportCatalogV1 | null | undefined,
  selectedPackageId: string | null | undefined,
  latestSavedReportHash: string | null | undefined = null
): DataPanelExportPackageAuditIndexArtifactDisplay | null {
  if (
    catalog === null ||
    catalog === undefined ||
    selectedPackageId === null ||
    selectedPackageId === undefined
  ) {
    return null;
  }
  const record = selectRuntimeExportCatalogRecordForPackage(catalog, selectedPackageId);
  if (record === null) {
    return null;
  }
  const auditFile =
    record.files.find(
      (file) =>
        file.filename === EXPORT_PACKAGE_AUDIT_INDEX_FILENAME ||
        file.name === "export_package_audit_index_v1"
    ) ?? null;
  const reportHashLabel =
    latestSavedReportHash !== null && latestSavedReportHash !== undefined
      ? `route report ${shortRuntimeHash(latestSavedReportHash)}`
      : "route report hash waiting";
  if (auditFile === null) {
    return {
      packageId: selectedPackageId,
      tone: "different",
      statusLabel: "audit index not saved",
      summaryLabel: `${selectedPackageId} / audit file missing / ${reportHashLabel}`,
      hashLabels: [
        `catalog ${shortRuntimeHash(catalog.catalog_hash)}`,
        `package ${record.export_type}`,
        reportHashLabel
      ],
      artifactHref: null,
      artifactTitle: `${EXPORT_PACKAGE_AUDIT_INDEX_FILENAME} is not present in the selected package catalog.`
    };
  }
  return {
    packageId: selectedPackageId,
    tone: "match",
    statusLabel: "audit index artifact present",
    summaryLabel: `${selectedPackageId} / ${formatRuntimeExportFileBytes(
      auditFile.bytes
    )} / file ${shortRuntimeHash(auditFile.sha256)}`,
    hashLabels: [
      `catalog ${shortRuntimeHash(catalog.catalog_hash)}`,
      `audit ${shortRuntimeHash(auditFile.sha256)}`,
      reportHashLabel
    ],
    artifactHref: runtimeExportPackageFileHref(selectedPackageId, auditFile.filename),
    artifactTitle: `${auditFile.filename} / ${formatRuntimeExportFileBytes(
      auditFile.bytes
    )} / ${auditFile.sha256}`
  };
}

export function buildDataPanelExportPackageHandoffReportArtifactDisplay(
  catalog: RuntimeExportCatalogV1 | null | undefined,
  selectedPackageId: string | null | undefined,
  completionHash: string | null | undefined = null
): DataPanelExportPackageHandoffReportArtifactDisplay | null {
  if (
    catalog === null ||
    catalog === undefined ||
    selectedPackageId === null ||
    selectedPackageId === undefined
  ) {
    return null;
  }
  const record = selectRuntimeExportCatalogRecordForPackage(catalog, selectedPackageId);
  if (record === null) {
    return null;
  }
  const handoffFile =
    record.files.find(
      (file) =>
        file.filename === PACKAGE_HANDOFF_REPORT_FILENAME ||
        file.name === "package_handoff_report_v1"
    ) ?? null;
  const completionHashLabel =
    completionHash !== null && completionHash !== undefined && completionHash !== ""
      ? `completion ${shortRuntimeHash(completionHash)}`
      : "completion hash waiting";
  if (handoffFile === null) {
    return {
      packageId: selectedPackageId,
      tone: "different",
      statusLabel: "handoff report not saved",
      summaryLabel: `${selectedPackageId} / handoff file missing / ${completionHashLabel}`,
      hashLabels: [
        `catalog ${shortRuntimeHash(catalog.catalog_hash)}`,
        `package ${record.export_type}`,
        completionHashLabel
      ],
      artifactHref: null,
      artifactTitle: `${PACKAGE_HANDOFF_REPORT_FILENAME} is not present in the selected package catalog.`
    };
  }
  return {
    packageId: selectedPackageId,
    tone: "match",
    statusLabel: "handoff report artifact present",
    summaryLabel: `${selectedPackageId} / ${formatRuntimeExportFileBytes(
      handoffFile.bytes
    )} / file ${shortRuntimeHash(handoffFile.sha256)}`,
    hashLabels: [
      `catalog ${shortRuntimeHash(catalog.catalog_hash)}`,
      `report ${shortRuntimeHash(handoffFile.sha256)}`,
      completionHashLabel
    ],
    artifactHref: runtimeExportPackageHandoffReportHref(selectedPackageId),
    artifactTitle: `${handoffFile.filename} / ${formatRuntimeExportFileBytes(
      handoffFile.bytes
    )} / ${handoffFile.sha256}`
  };
}

export function buildDataPanelExportScenarioReviewBundleDisplay(
  bundle: RuntimeExportScenarioReviewBundleV1 | null | undefined
): DataPanelExportScenarioReviewBundleDisplay | null {
  if (bundle === null || bundle === undefined) {
    return null;
  }
  const ready =
    bundle.scenario_review_status === "SCENARIO_REVIEW_READY" &&
    bundle.scenario_review_warnings.length === 0 &&
    bundle.user_configuration.validation_ok === true &&
    bundle.model_boundaries.event_replay_restore === false &&
    bundle.model_boundaries.model_recomputation === false &&
    bundle.model_boundaries.packet_level_simulation === false &&
    bundle.model_boundaries.external_simulators === false;
  return {
    packageId: bundle.package_id,
    tone: ready ? "match" : "different",
    statusLabel: ready ? "scenario review ready" : "scenario review needs check",
    summaryLabel: `${bundle.package_id} / ${bundle.scenario_review_status} / review ${shortRuntimeHash(
      bundle.scenario_review_hash
    )}`,
    bundleHref: runtimeExportPackageFileHref(
      bundle.package_id,
      SCENARIO_REVIEW_BUNDLE_FILENAME
    ),
    scenarioLabels: [
      `satellites ${formatCount(bundle.scenario.satellite_count)}`,
      `users ${formatCount(bundle.scenario.user_count)}`,
      `compute ${formatCount(bundle.scenario.compute_node_count)}`,
      `duration ${formatPreciseMetricValue(bundle.scenario.duration_seconds)} s`,
      `sim ${formatPreciseMetricValue(bundle.runtime.current_sim_time)} s`
    ],
    configurationLabels: [
      `schema ${bundle.user_configuration.schema_id}`,
      `config ${shortRuntimeHash(bundle.user_configuration.config_hash)}`,
      `binding ${shortRuntimeHash(bundle.user_configuration.binding_hash)}`,
      `validation ${bundle.user_configuration.validation_ok ? "ok" : "check"}`
    ],
    evidenceLabels: [
      `manifest ${shortRuntimeHash(bundle.reproducibility.manifest_hash)}`,
      `boundary ${shortRuntimeHash(
        bundle.reproducibility.runtime_export_boundary_hash
      )}`,
      `review ${shortRuntimeHash(bundle.review_summary.summary_hash)}`,
      `diagnostics ${shortRuntimeHash(bundle.diagnostics.diagnostics_hash)}`,
      ...(bundle.network_kpi_benchmark_validation
        ? [
            `KPI benchmark ${bundle.network_kpi_benchmark_validation.validation_status}`,
            `KPI benchmark ${shortRuntimeHash(
              bundle.network_kpi_benchmark_validation.validation_hash
            )}`
          ]
        : []),
      ...(bundle.user_service_requests
        ? [
            `user services ${formatCount(
              bundle.user_service_requests.exported_request_count
            )} / ${formatCount(bundle.user_service_requests.request_count)}`,
            `user services ${shortRuntimeHash(
              bundle.user_service_requests.summary_hash
            )}`
          ]
        : []),
      `audit ${bundle.audit_index.filename}`
    ],
    boundaryLabels: [
      `event kernel ${bundle.model_boundaries.event_kernel_policy}`,
      `event replay ${bundle.model_boundaries.event_replay_restore ? "yes" : "no"}`,
      `recompute ${bundle.model_boundaries.model_recomputation ? "yes" : "no"}`,
      `packet ${bundle.model_boundaries.packet_level_simulation ? "yes" : "no"}`,
      `external ${bundle.model_boundaries.external_simulators ? "yes" : "no"}`
    ],
    workflowRows: buildDataPanelScenarioReviewWorkflowRows(bundle),
    warningLabels: [
      ...bundle.scenario_review_warnings,
      ...bundle.diagnostics.finding_labels
        .filter((finding) => finding.severity === "ERROR" || finding.severity === "WARN")
        .map((finding) => `${finding.severity}:${finding.code}`)
    ]
  };
}

export function buildDataPanelExportScenarioReviewBundleStatus(
  display: DataPanelExportScenarioReviewBundleDisplay | null,
  selectedPackageId: string | null | undefined,
  loading = false,
  error: string | null | undefined = null
): DataPanelExportScenarioReviewBundleStatus | null {
  if (loading) {
    return {
      tone: "pending",
      statusLabel: "loading scenario review",
      summaryLabel: selectedPackageId ?? "waiting for package selection",
      bundleHref: null,
      scenarioLabels: ["backend scenario review artifact"],
      configurationLabels: [],
      evidenceLabels: [],
      boundaryLabels: [],
      workflowRows: [],
      warningLabels: []
    };
  }
  if (error !== null && error !== undefined) {
    return {
      tone: "error",
      statusLabel: "scenario review load failed",
      summaryLabel: selectedPackageId ?? "unknown package",
      bundleHref: null,
      scenarioLabels: [error],
      configurationLabels: [],
      evidenceLabels: [],
      boundaryLabels: [],
      workflowRows: [],
      warningLabels: [error]
    };
  }
  if (display === null) {
    return null;
  }
  return {
    tone: display.tone,
    statusLabel: display.statusLabel,
    summaryLabel: display.summaryLabel,
    bundleHref: display.bundleHref,
    scenarioLabels: display.scenarioLabels,
    configurationLabels: display.configurationLabels,
    evidenceLabels: display.evidenceLabels,
    boundaryLabels: display.boundaryLabels,
    workflowRows: display.workflowRows,
    warningLabels: display.warningLabels
  };
}

function buildDataPanelScenarioReviewWorkflowRows(
  bundle: RuntimeExportScenarioReviewBundleV1
): readonly DataPanelExportScenarioReviewWorkflowRow[] {
  const exported = new Set(bundle.artifact_review.artifact_filenames);
  const orderedFilenames = [
    ...bundle.recommended_review_order,
    "route_detail_index_v1.json",
    "service_lifecycle_trace_v2.json",
    "user_service_request_summary_v2.json"
  ];
  const seen = new Set<string>();
  return orderedFilenames
    .filter((filename) => {
      if (seen.has(filename)) {
        return false;
      }
      seen.add(filename);
      return scenarioReviewWorkflowStepLabel(filename) !== null;
    })
    .map((filename) => {
      const stepLabel = scenarioReviewWorkflowStepLabel(filename) ?? filename;
      const available =
        exported.has(filename) ||
        filename === SCENARIO_REVIEW_BUNDLE_FILENAME ||
        filename === bundle.audit_index.filename;
      const href = available
        ? runtimeExportPackageFileHref(bundle.package_id, filename)
        : null;
      return {
        stepLabel,
        statusLabel: available ? "available" : "missing",
        detailLabel: filename,
        href,
        title: `${stepLabel} / ${filename} / ${
          available ? "package artifact available" : "not listed in scenario review bundle"
        }`,
        tone: available ? "match" : "different"
      };
    });
}

function scenarioReviewWorkflowStepLabel(filename: string): string | null {
  switch (filename) {
    case "scenario_review_bundle_v1.json":
      return "1 scenario entry";
    case "export_package_audit_index_v1.json":
      return "2 audit index";
    case "review_summary_v1.json":
      return "3 review summary";
    case "diagnostics_bundle_v1.json":
      return "4 diagnostics";
    case "manifest.json":
      return "5 manifest";
    case "config_snapshot.json":
      return "6 configuration";
    case "route_detail_index_v1.json":
      return "7 route evidence";
    case "service_lifecycle_trace_v2.json":
      return "8 service trace";
    case "user_service_request_summary_v2.json":
      return "9 user services";
    case "events.jsonl":
      return "10 event evidence";
    case "metrics.csv":
      return "11 metrics";
    case "summary.json":
      return "12 summary";
    default:
      return null;
  }
}

export function buildDataPanelScenarioReviewChecklistDraft(
  bundle: RuntimeExportScenarioReviewBundleV1 | null | undefined,
  checklist: RuntimeExportScenarioReviewChecklistV1 | null | undefined
): DataPanelScenarioReviewChecklistDraft {
  if (bundle === null || bundle === undefined) {
    return {};
  }
  const savedRecords = new Map(
    (checklist?.records ?? []).map((record) => [record.artifact_filename, record])
  );
  return Object.fromEntries(
    buildDataPanelScenarioReviewWorkflowRows(bundle).map((row) => {
      const saved = savedRecords.get(row.detailLabel);
      return [
        row.detailLabel,
        {
          reviewStatus: normalizeDataPanelScenarioReviewChecklistStatus(
            saved?.review_status,
            row.tone === "match" ? "REVIEWED" : "NEEDS_FOLLOWUP"
          ),
          operatorNote: saved?.operator_note ?? ""
        }
      ];
    })
  );
}

export function defaultDataPanelScenarioReviewChecklistDraftEntry(
  row: DataPanelExportScenarioReviewWorkflowRow
): DataPanelScenarioReviewChecklistDraftEntry {
  return {
    reviewStatus: row.tone === "match" ? "REVIEWED" : "NEEDS_FOLLOWUP",
    operatorNote: ""
  };
}

export function updateDataPanelScenarioReviewChecklistDraft(
  draft: DataPanelScenarioReviewChecklistDraft,
  artifactFilename: string,
  patch: Partial<DataPanelScenarioReviewChecklistDraftEntry>
): DataPanelScenarioReviewChecklistDraft {
  const previous = draft[artifactFilename] ?? {
    reviewStatus: "NEEDS_FOLLOWUP",
    operatorNote: ""
  };
  return {
    ...draft,
    [artifactFilename]: {
      reviewStatus: patch.reviewStatus ?? previous.reviewStatus,
      operatorNote: patch.operatorNote ?? previous.operatorNote
    }
  };
}

export function buildDataPanelScenarioReviewChecklistSaveRequest(
  bundle: RuntimeExportScenarioReviewBundleV1 | null | undefined,
  workflowRows: readonly DataPanelExportScenarioReviewWorkflowRow[],
  draft: DataPanelScenarioReviewChecklistDraft,
  auditIndex: RuntimeExportPackageAuditIndexV1 | null | undefined = null
): DataPanelExportScenarioReviewChecklistSaveRequest | null {
  if (bundle === null || bundle === undefined || workflowRows.length === 0) {
    return null;
  }
  return {
    packageId: bundle.package_id,
    records: workflowRows.map((row) => {
      const entry =
        draft[row.detailLabel] ??
        defaultDataPanelScenarioReviewChecklistDraftEntry(row);
      return {
        artifact_filename: row.detailLabel,
        step_label: row.stepLabel,
        review_status: entry.reviewStatus,
        operator_note: entry.operatorNote.trim(),
        status_reason:
          row.tone === "match" ? "" : "ARTIFACT_MISSING_OR_DEGRADED_IN_PACKAGE",
        evidence_hash: scenarioReviewWorkflowEvidenceHash(
          bundle,
          auditIndex,
          row.detailLabel
        )
      };
    })
  };
}

export function buildDataPanelExportScenarioReviewChecklistStatus(
  checklist: RuntimeExportScenarioReviewChecklistV1 | null | undefined,
  options: {
    loading?: boolean;
    error?: string | null;
    savePending?: boolean;
    saveError?: string | null;
    latestSaveHash?: string | null;
  } = {}
): DataPanelExportScenarioReviewChecklistStatusDisplay {
  if (options.savePending === true) {
    return {
      tone: "pending",
      statusLabel: "审核清单保存中",
      summaryLabel: "waiting for backend checklist persistence",
      warningLabels: []
    };
  }
  if (options.saveError) {
    return {
      tone: "error",
      statusLabel: "审核清单保存失败",
      summaryLabel: options.saveError,
      warningLabels: [options.saveError]
    };
  }
  if (options.loading === true) {
    return {
      tone: "pending",
      statusLabel: "审核清单加载中",
      summaryLabel: "waiting for scenario_review_checklist_v1.json",
      warningLabels: []
    };
  }
  if (options.error) {
    return {
      tone: "error",
      statusLabel: "审核清单加载失败",
      summaryLabel: options.error,
      warningLabels: [options.error]
    };
  }
  if (checklist === null || checklist === undefined) {
    return {
      tone: "different",
      statusLabel: "审核清单未保存",
      summaryLabel: options.latestSaveHash
        ? `last save ${shortRuntimeHash(options.latestSaveHash)}`
        : "operator checklist has not been persisted",
      warningLabels: ["scenario_review_checklist_v1.json missing"]
    };
  }
  const complete = checklist.checklist_status === "CHECKLIST_COMPLETE";
  return {
    tone: complete ? "match" : "different",
    statusLabel: complete ? "审核清单已完成" : "审核清单需检查",
    summaryLabel: `${checklist.checklist_status} / records ${formatCount(
      checklist.record_count
    )} / checklist ${shortRuntimeHash(checklist.checklist_hash)}`,
    warningLabels: complete ? [] : [checklist.checklist_status]
  };
}

function normalizeDataPanelScenarioReviewChecklistStatus(
  value: string | null | undefined,
  fallback: DataPanelScenarioReviewChecklistStatus
): DataPanelScenarioReviewChecklistStatus {
  switch (String(value ?? "").toUpperCase()) {
    case "REVIEWED":
      return "REVIEWED";
    case "SKIPPED":
      return "SKIPPED";
    case "NEEDS_FOLLOWUP":
      return "NEEDS_FOLLOWUP";
    case "ERROR":
      return "ERROR";
    default:
      return fallback;
  }
}

function scenarioReviewWorkflowEvidenceHash(
  bundle: RuntimeExportScenarioReviewBundleV1,
  auditIndex: RuntimeExportPackageAuditIndexV1 | null | undefined,
  filename: string
): string {
  switch (filename) {
    case SCENARIO_REVIEW_BUNDLE_FILENAME:
      return bundle.scenario_review_hash;
    case EXPORT_PACKAGE_AUDIT_INDEX_FILENAME:
      return auditIndex?.audit_hash ?? "";
    case "review_summary_v1.json":
      return bundle.review_summary.summary_hash;
    case "diagnostics_bundle_v1.json":
      return bundle.diagnostics.diagnostics_hash;
    case "manifest.json":
      return bundle.reproducibility.manifest_hash;
    case "config_snapshot.json":
      return bundle.user_configuration.config_hash;
    default:
      return "";
  }
}

export function buildDataPanelExportReviewCompletionSummary({
  auditIndex,
  routeReport,
  scenarioReviewBundle,
  scenarioReviewChecklist
}: {
  auditIndex?: RuntimeExportPackageAuditIndexV1 | null;
  routeReport?: RuntimeExportRouteComparisonReviewReportV1 | null;
  scenarioReviewBundle?: RuntimeExportScenarioReviewBundleV1 | null;
  scenarioReviewChecklist?: RuntimeExportScenarioReviewChecklistV1 | null;
}): DataPanelExportReviewCompletionSummaryDisplay | null {
  if (
    auditIndex == null &&
    routeReport == null &&
    scenarioReviewBundle == null &&
    scenarioReviewChecklist == null
  ) {
    return null;
  }
  const backendCompletion = auditIndex?.package_review_completion_v1;
  if (backendCompletion !== undefined) {
    return {
      tone: backendCompletion.handoff_ready ? "match" : "different",
      statusLabel: backendCompletion.handoff_ready
        ? "review package complete"
        : "review package needs action",
      summaryLabel: `${backendCompletion.completion_status} / audit ${
        backendCompletion.audit_status
      } / completion ${shortRuntimeHash(backendCompletion.completion_hash)}`,
      evidenceLabels: [
        ...backendCompletion.evidence_labels,
        `completion ${shortRuntimeHash(backendCompletion.completion_hash)}`
      ],
      warningLabels: backendCompletion.missing_or_warning_evidence
    };
  }
  const auditReady = auditIndex?.audit_status === "AUDIT_READY";
  const routeReportPresent =
    auditIndex?.route_comparison_review_report_present === true ||
    routeReport !== null && routeReport !== undefined;
  const routeReportReady =
    routeReportPresent &&
    (routeReport === null ||
      routeReport === undefined ||
      routeReport.error_count === 0);
  const scenarioReady =
    scenarioReviewBundle?.scenario_review_status === "SCENARIO_REVIEW_READY" &&
    (scenarioReviewBundle?.scenario_review_warnings.length ?? 0) === 0;
  const checklistPresent =
    auditIndex?.scenario_review_checklist_present === true ||
    scenarioReviewChecklist !== null && scenarioReviewChecklist !== undefined;
  const checklistStatus =
    scenarioReviewChecklist?.checklist_status ??
    auditIndex?.scenario_review_checklist_status ??
    "";
  const checklistComplete = checklistStatus === "CHECKLIST_COMPLETE";
  const warningLabels: string[] = [];
  if (!auditReady) {
    warningLabels.push("audit index not ready");
  }
  if (!routeReportPresent) {
    warningLabels.push("route comparison review report missing");
  } else if (!routeReportReady) {
    warningLabels.push("route comparison review report has errors");
  }
  if (!scenarioReady) {
    warningLabels.push("scenario review bundle not ready");
  }
  if (!checklistPresent) {
    warningLabels.push("scenario review checklist missing");
  } else if (!checklistComplete) {
    warningLabels.push(`scenario review checklist ${checklistStatus || "not complete"}`);
  }
  const complete =
    auditReady &&
    routeReportReady &&
    scenarioReady &&
    checklistPresent &&
    checklistComplete;
  const tone = complete ? "match" : routeReportPresent || checklistPresent ? "different" : "pending";
  return {
    tone,
    statusLabel: complete
      ? "review package complete"
      : "review package needs action",
    summaryLabel: `${complete ? "ready" : "incomplete"} / audit ${
      auditIndex?.audit_status ?? "missing"
    } / checklist ${checklistStatus || "missing"}`,
    evidenceLabels: [
      `audit ${auditIndex?.audit_status ?? "missing"}`,
      `route report ${routeReportPresent ? "saved" : "missing"}`,
      `route records ${formatCount(routeReport?.record_count ?? 0)}`,
      `scenario ${scenarioReviewBundle?.scenario_review_status ?? "missing"}`,
      `checklist ${checklistStatus || "missing"}`,
      `checklist records ${formatCount(
        scenarioReviewChecklist?.record_count ??
          auditIndex?.scenario_review_checklist_record_count ??
          0
      )}`
    ],
    warningLabels
  };
}

export function buildDataPanelExportPackageAuditIndexDisplay(
  auditIndex: RuntimeExportPackageAuditIndexV1 | null | undefined,
  limit = 8
): DataPanelExportPackageAuditIndexDisplay | null {
  if (auditIndex === null || auditIndex === undefined) {
    return null;
  }
  const displayLimit = Math.max(0, Math.floor(limit));
  const artifactRows = auditIndex.artifact_hashes
    .slice(0, displayLimit)
    .map((artifact) => ({
      filename: artifact.filename,
      sizeLabel: formatRuntimeExportFileBytes(artifact.bytes),
      hashLabel: shortRuntimeHash(artifact.sha256)
    }));
  const hiddenArtifacts = Math.max(
    0,
    auditIndex.artifact_hashes.length - artifactRows.length
  );
  const warningLabels = [
    ...auditIndex.audit_warnings,
    ...auditIndex.boundary_alignment_warnings
  ];
  const userConfigBinding = auditIndex.user_configuration_binding_v1;
  const ready =
    auditIndex.audit_status === "AUDIT_READY" &&
    warningLabels.length === 0 &&
    auditIndex.packet_level_simulation === false &&
    auditIndex.event_replay_restore === false &&
    auditIndex.model_recomputation === false &&
    auditIndex.package_mutation_on_read === false;
  return {
    packageId: auditIndex.package_id,
    tone: ready ? "match" : "different",
    statusLabel: ready ? "audit ready" : "audit needs review",
    summaryLabel: `${auditIndex.package_id} / ${auditIndex.audit_status} / audit ${shortRuntimeHash(
      auditIndex.audit_hash
    )} / artifacts ${formatCount(auditIndex.artifact_count)}`,
    auditHref: runtimeExportPackageFileHref(
      auditIndex.package_id,
      EXPORT_PACKAGE_AUDIT_INDEX_FILENAME
    ),
    manifestLabels: [
      `manifest ${shortRuntimeHash(auditIndex.manifest_hash)}`,
      `control ${shortRuntimeHash(auditIndex.control_config_hash)}`,
      `generated ${shortRuntimeHash(auditIndex.generated_config_hash)}`,
      `runtime ${shortRuntimeHash(auditIndex.runtime_state_hash)}`
    ],
    configurationLabels: [
      `schema ${auditIndex.user_configuration_schema_id ?? userConfigBinding?.schema_id ?? "-"}`,
      `config ${shortRuntimeHash(
        auditIndex.user_configuration_config_hash ?? userConfigBinding?.config_hash ?? ""
      )}`,
      `export ${shortRuntimeHash(
        auditIndex.user_configuration_export_hash ?? userConfigBinding?.export_hash ?? ""
      )}`,
      `binding ${shortRuntimeHash(userConfigBinding?.binding_hash ?? "")}`,
      `validation ${
        auditIndex.user_configuration_validation_ok ?? userConfigBinding?.validation_ok
          ? "ok"
          : "check"
      }`
    ],
    boundaryLabels: [
      `boundary ${shortRuntimeHash(auditIndex.runtime_export_boundary_hash)}`,
      `alignment ${shortRuntimeHash(auditIndex.boundary_alignment_hash)}`,
      `status ${auditIndex.boundary_alignment_status || "-"}`,
      `self hash excluded ${auditIndex.self_artifact_excluded_from_hashes ? "yes" : "no"}`
    ],
    diagnosticsLabels: [
      `review ${shortRuntimeHash(auditIndex.review_summary_hash)}`,
      `diagnostics ${shortRuntimeHash(auditIndex.diagnostics_hash)}`,
      ...(auditIndex.network_kpi_benchmark_validation_present !== undefined
        ? [
            `KPI benchmark ${
              auditIndex.network_kpi_benchmark_validation_status ?? "-"
            }`,
            `KPI failed ${formatCount(
              auditIndex.network_kpi_benchmark_validation_failed_check_count ?? 0
            )}`,
            `KPI benchmark ${shortRuntimeHash(
              auditIndex.network_kpi_benchmark_validation_hash ?? ""
            )}`
          ]
        : []),
      ...(auditIndex.user_service_request_summary_present !== undefined
        ? [
            `user services ${
              auditIndex.user_service_request_summary_present ? "present" : "missing"
            }`,
            `user service requests ${formatCount(
              auditIndex.user_service_request_summary_request_count ?? 0
            )}`,
            `user services exported ${formatCount(
              auditIndex.user_service_request_summary_exported_request_count ?? 0
            )}`,
            `user services hidden ${formatCount(
              auditIndex.user_service_request_summary_hidden_request_count ?? 0
            )}`,
            `user services ${shortRuntimeHash(
              auditIndex.user_service_request_summary_hash ?? ""
            )}`
          ]
        : []),
      `packet ${auditIndex.packet_level_simulation ? "yes" : "no"}`,
      `recompute ${auditIndex.model_recomputation ? "yes" : "no"}`
    ],
    routeReviewLabels: [
      `route report ${
        auditIndex.route_comparison_review_report_present ? "present" : "missing"
      }`,
      `route report ${shortRuntimeHash(
        auditIndex.route_comparison_review_report_hash
      )}`,
      `event replay restore ${auditIndex.event_replay_restore ? "yes" : "no"}`,
      `package mutation ${auditIndex.package_mutation_on_read ? "yes" : "no"}`
    ],
    artifactRows,
    artifactSummaryLabel: `showing ${formatCount(artifactRows.length)} of ${formatCount(
      auditIndex.artifact_hashes.length
    )} artifact hashes${hiddenArtifacts > 0 ? ` / hidden ${formatCount(hiddenArtifacts)}` : ""}`,
    warningLabels
  };
}

export function buildDataPanelExportPackageAuditIndexStatus(
  display: DataPanelExportPackageAuditIndexDisplay | null,
  selectedPackageId: string | null | undefined,
  loading = false,
  error: string | null | undefined = null
): DataPanelExportPackageAuditIndexStatus | null {
  if (loading) {
    return {
      tone: "pending",
      statusLabel: "loading audit index",
      summaryLabel: selectedPackageId ?? "waiting for package selection",
      auditHref: null,
      manifestLabels: ["read-only audit artifact"],
      configurationLabels: [],
      boundaryLabels: [],
      diagnosticsLabels: [],
      routeReviewLabels: [],
      artifactRows: [],
      artifactSummaryLabel: "waiting for audit index",
      warningLabels: []
    };
  }
  if (error !== null && error !== undefined) {
    return {
      tone: "error",
      statusLabel: "audit index load failed",
      summaryLabel: selectedPackageId ?? "unknown package",
      auditHref: null,
      manifestLabels: [error],
      configurationLabels: [],
      boundaryLabels: [],
      diagnosticsLabels: [],
      routeReviewLabels: [],
      artifactRows: [],
      artifactSummaryLabel: "audit index unavailable",
      warningLabels: [error]
    };
  }
  if (display === null) {
    return null;
  }
  return {
    tone: display.tone,
    statusLabel: display.statusLabel,
    summaryLabel: display.summaryLabel,
    auditHref: display.auditHref,
    manifestLabels: display.manifestLabels,
    configurationLabels: display.configurationLabels,
    boundaryLabels: display.boundaryLabels,
    diagnosticsLabels: display.diagnosticsLabels,
    routeReviewLabels: display.routeReviewLabels,
    artifactRows: display.artifactRows,
    artifactSummaryLabel: display.artifactSummaryLabel,
    warningLabels: display.warningLabels
  };
}

export function buildDataPanelExportRouteComparisonReviewReportDisplay(
  report: RuntimeExportRouteComparisonReviewReportV1 | null | undefined,
  options: DataPanelExportRouteComparisonReviewReportOptions = {}
): DataPanelExportRouteComparisonReviewReportDisplay | null {
  if (report === null || report === undefined) {
    return null;
  }
  const pageLimit = Math.max(1, Math.floor(options.limit ?? 5));
  const requestedCursor = Math.max(0, Math.floor(options.cursor ?? 0));
  const statusFilter = options.status ?? "ALL";
  const query = options.query?.trim() ?? "";
  const normalizedQuery = query.toLowerCase();
  const filteredRecords = report.records.filter((record) => {
    if (statusFilter !== "ALL" && record.comparison_status !== statusFilter) {
      return false;
    }
    if (normalizedQuery.length === 0) {
      return true;
    }
    return routeComparisonReviewReportRecordMatchesQuery(record, normalizedQuery);
  });
  const maxStart =
    filteredRecords.length === 0
      ? 0
      : Math.floor((filteredRecords.length - 1) / pageLimit) * pageLimit;
  const pageCursor = Math.min(requestedCursor, maxStart);
  const pageRecords = filteredRecords.slice(pageCursor, pageCursor + pageLimit);
  const reviewReady =
    report.error_count === 0 &&
    report.unavailable_count === 0 &&
    report.different_count === 0;
  const boundaryAlignmentLabels =
    report.boundary_alignment_hash !== undefined &&
    report.boundary_alignment_hash.length > 0
      ? [
          `boundary alignment ${shortRuntimeHash(report.boundary_alignment_hash)}`,
          `alignment status ${report.boundary_alignment_status ?? "-"}`,
          `boundary ${shortRuntimeHash(report.runtime_export_boundary_hash ?? "")}`
        ]
      : ["boundary alignment not recorded"];
  const rows: DataPanelExportRouteComparisonReviewReportRow[] = pageRecords
    .map((record) => ({
      routeId: record.route_id,
      tone: record.comparison_status === "MATCH" ? "match" : "different",
      statusLabel: record.comparison_status,
      hashLabel: `package ${shortRuntimeHash(
        record.package_route_detail_hash
      )} / live ${shortRuntimeHash(record.live_route_detail_hash)}`,
      noteLabel:
        record.operator_note.trim().length > 0
          ? record.operator_note
          : record.status_reason
    }));
  const hiddenCount = Math.max(0, filteredRecords.length - rows.length);
  const hiddenLabel = hiddenCount > 0 ? ` / hidden ${formatCount(hiddenCount)}` : "";
  const visibleStart = rows.length === 0 ? 0 : pageCursor + 1;
  const visibleEnd = pageCursor + rows.length;
  const queryLabel = query.length > 0 ? ` / query ${query}` : "";
  return {
    packageId: report.package_id,
    tone: reviewReady ? "match" : "different",
    statusLabel: reviewReady
      ? "saved comparisons match"
      : "saved comparisons need review",
    summaryLabel: `${report.package_id} / records ${formatCount(
      report.record_count
    )} / different ${formatCount(report.different_count)} / error ${formatCount(
      report.error_count
    )} / ${shortRuntimeHash(report.report_hash)}${hiddenLabel}`,
    metaLabels: [
      `match ${formatCount(report.match_count)}`,
      `different ${formatCount(report.different_count)}`,
      `unavailable ${formatCount(report.unavailable_count)}`,
      `error ${formatCount(report.error_count)}`,
      ...boundaryAlignmentLabels,
      `ordering ${report.ordering}`
    ],
    recordRows: rows,
    reportHref: runtimeExportPackageFileHref(
      report.package_id,
      ROUTE_COMPARISON_REVIEW_REPORT_FILENAME
    ),
    filterLabel: `showing ${formatCount(visibleStart)}-${formatCount(
      visibleEnd
    )} of ${formatCount(filteredRecords.length)} filtered / total ${formatCount(
      report.record_count
    )} / status ${statusFilter}${queryLabel}`,
    pageCursor,
    pageLimit,
    previousCursor: Math.max(0, pageCursor - pageLimit),
    nextCursor: pageCursor + pageLimit,
    canPreviousPage: pageCursor > 0,
    canNextPage: pageCursor + pageLimit < filteredRecords.length
  };
}

function routeComparisonReviewReportRecordMatchesQuery(
  record: RuntimeExportRouteComparisonReviewReportRecordV1,
  normalizedQuery: string
): boolean {
  return [
    record.route_id,
    record.comparison_status,
    record.package_route_detail_hash,
    record.live_route_detail_hash,
    record.status_reason,
    record.operator_note,
    ...record.compared_fields,
    ...record.different_fields
  ].some((value) => value.toLowerCase().includes(normalizedQuery));
}

export function buildDataPanelExportRouteComparisonReviewReportStatus(
  display: DataPanelExportRouteComparisonReviewReportDisplay | null,
  selectedPackageId: string | null | undefined,
  loading = false,
  error: string | null | undefined = null
): DataPanelExportRouteComparisonReviewReportStatus | null {
  if (loading) {
    return {
      tone: "pending",
      statusLabel: "loading saved review report",
      summaryLabel: selectedPackageId ?? "waiting for package selection",
      metaLabels: ["read-only artifact", "no route recomputation"],
      recordRows: [],
      reportHref: null,
      filterLabel: "waiting for report artifact",
      pageCursor: 0,
      pageLimit: 0,
      previousCursor: 0,
      nextCursor: 0,
      canPreviousPage: false,
      canNextPage: false
    };
  }
  if (error !== null && error !== undefined) {
    return {
      tone: "error",
      statusLabel: "saved review report load failed",
      summaryLabel: selectedPackageId ?? "unknown package",
      metaLabels: [error],
      recordRows: [],
      reportHref: null,
      filterLabel: "report load failed",
      pageCursor: 0,
      pageLimit: 0,
      previousCursor: 0,
      nextCursor: 0,
      canPreviousPage: false,
      canNextPage: false
    };
  }
  if (display === null) {
    return null;
  }
  if (
    selectedPackageId !== null &&
    selectedPackageId !== undefined &&
    display.packageId !== selectedPackageId
  ) {
    return {
      tone: "pending",
      statusLabel: "waiting for selected package report",
      summaryLabel: selectedPackageId,
      metaLabels: [`loaded package ${display.packageId}`],
      recordRows: [],
      reportHref: null,
      filterLabel: "selected package mismatch",
      pageCursor: 0,
      pageLimit: 0,
      previousCursor: 0,
      nextCursor: 0,
      canPreviousPage: false,
      canNextPage: false
    };
  }
  return display;
}

export function buildDataPanelExportArtifactHealthDisplay(
  catalog: RuntimeExportCatalogV1 | null | undefined,
  selectedPackageId: string | null | undefined,
  reviewSummary: RuntimeExportReviewSummaryV1 | null | undefined
): DataPanelExportArtifactHealthDisplay | null {
  if (
    catalog === null ||
    catalog === undefined ||
    selectedPackageId === null ||
    selectedPackageId === undefined
  ) {
    return null;
  }
  const record = selectRuntimeExportCatalogRecordForPackage(catalog, selectedPackageId);
  if (record === null) {
    return null;
  }
  const files = [...record.files].sort(compareRuntimeExportCatalogFiles);
  const filesByName = new Map(files.map((file) => [file.filename, file]));
  const requiredFilenames = new Set(
    reviewSummary?.package_id === selectedPackageId
      ? reviewSummary.artifacts.required_filenames
      : []
  );
  const missingRequiredFilenames = new Set(
    reviewSummary?.package_id === selectedPackageId
      ? reviewSummary.artifacts.missing_required_filenames
      : []
  );
  const orderedFilenames = [
    ...new Set([
      ...Array.from(requiredFilenames),
      ...files.map((file) => file.filename),
      ...Array.from(missingRequiredFilenames)
    ])
  ].sort((left, right) => left.localeCompare(right));
  const rows = orderedFilenames.map((filename) => {
    const file = filesByName.get(filename) ?? null;
    const required = requiredFilenames.has(filename);
    const missing = missingRequiredFilenames.has(filename) || (required && file === null);
    const present = file !== null && !missing;
    return {
      filename,
      roleLabel: required ? "必需" : "附加",
      statusLabel: missing ? "缺失" : required ? "必需已登记" : "附加已登记",
      sizeLabel: file ? formatRuntimeExportFileBytes(file.bytes) : "-",
      hashLabel: file ? shortRuntimeHash(file.sha256) : "-",
      href: file ? runtimeExportPackageFileHref(selectedPackageId, filename) : null,
      required,
      present,
      title: `${filename} / ${missing ? "缺失" : "已登记"} / ${
        file ? file.sha256 : "no file hash"
      }`
    };
  });
  const missingCount = rows.filter((row) => !row.present).length;
  return {
    packageId: selectedPackageId,
    sourceLabel: `${catalog.source} / ${record.export_type} / files`,
    summaryLabel: `${selectedPackageId} / 登记 ${formatCount(
      files.length
    )} 个文件 / 缺失 ${formatCount(missingCount)} 个`,
    rows
  };
}

function selectRuntimeExportCatalogRecordForPackage(
  catalog: RuntimeExportCatalogV1,
  packageId: string
): RuntimeExportCatalogRecordV1 | null {
  return (
    [...catalog.records]
      .filter((record) => record.package_id === packageId)
      .sort((left, right) => {
        const leftRank = left.export_type === "ARCHIVE" ? 0 : 1;
        const rightRank = right.export_type === "ARCHIVE" ? 0 : 1;
        if (leftRank !== rightRank) {
          return leftRank - rightRank;
        }
        return left.catalog_key.localeCompare(right.catalog_key);
      })[0] ?? null
  );
}

function compareRuntimeExportCatalogFiles(
  left: RuntimeExportCatalogFileV1,
  right: RuntimeExportCatalogFileV1
): number {
  return left.filename.localeCompare(right.filename);
}

function formatRuntimeExportFileBytes(bytes: number): string {
  if (!Number.isFinite(bytes) || bytes <= 0) {
    return "0 B";
  }
  if (bytes < 1024) {
    return `${formatCount(Math.round(bytes))} B`;
  }
  if (bytes < 1024 * 1024) {
    return `${formatPreciseMetricValue(bytes / 1024)} KiB`;
  }
  return `${formatPreciseMetricValue(bytes / (1024 * 1024))} MiB`;
}

export interface DataPanelExportCompareDisplay {
  packageId: string;
  tone: "match" | "different";
  statusLabel: string;
  summaryLabel: string;
  configLabel: string;
  generatedConfigLabel: string;
  hashLabel: string;
  diffRows: readonly DataPanelExportCompareDiffRow[];
}

export interface DataPanelExportCompareStatus {
  tone: "match" | "different" | "pending" | "error";
  statusLabel: string;
  summaryLabel: string;
  metaLabels: readonly string[];
  diffRows: readonly DataPanelExportCompareDiffRow[];
}

export interface DataPanelExportReviewSummaryDisplay {
  packageId: string;
  tone: "match" | "different";
  statusLabel: string;
  summaryLabel: string;
  metaLabels: readonly string[];
  artifactLabels: readonly string[];
}

export interface DataPanelExportReviewSummaryStatus {
  tone: "match" | "different" | "pending" | "error";
  statusLabel: string;
  summaryLabel: string;
  metaLabels: readonly string[];
  artifactLabels: readonly string[];
}

export interface DataPanelExportDiagnosticsDisplay {
  packageId: string;
  tone: "match" | "different";
  statusLabel: string;
  summaryLabel: string;
  metaLabels: readonly string[];
  modelBoundaryLabels: readonly string[];
  findingRows: readonly DataPanelExportDiagnosticsFindingRow[];
  actionLabels: readonly string[];
  diagnosticsHref: string;
}

export interface DataPanelExportDiagnosticsStatus {
  tone: "match" | "different" | "pending" | "error";
  statusLabel: string;
  summaryLabel: string;
  metaLabels: readonly string[];
  modelBoundaryLabels: readonly string[];
  findingRows: readonly DataPanelExportDiagnosticsFindingRow[];
  actionLabels: readonly string[];
  diagnosticsHref: string | null;
}

export interface DataPanelExportServiceLifecycleTraceStatus {
  tone: "match" | "different" | "pending" | "error";
  statusLabel: string;
  summaryLabel: string;
  metaLabels: readonly string[];
  traceHref: string | null;
  display: DataPanelServiceLifecycleTraceDisplay | null;
  filterLabel: string;
  pageCursor: number;
  pageLimit: number;
  previousCursor: number;
  nextCursor: number;
  canPreviousPage: boolean;
  canNextPage: boolean;
}

export interface DataPanelExportUserServiceRequestStatus {
  tone: "match" | "different" | "pending" | "error";
  statusLabel: string;
  summaryLabel: string;
  metaLabels: readonly string[];
  artifactHref: string | null;
  rows: readonly UserBusinessRequestRow[];
  filterLabel: string;
  pageCursor: number;
  pageLimit: number;
  previousCursor: number;
  nextCursor: number;
  canPreviousPage: boolean;
  canNextPage: boolean;
}

export interface DataPanelExportServiceLifecycleTraceStatusOptions
  extends DataPanelServiceTraceFilter {
  cursor?: number;
  limit?: number;
  backendPage?: RuntimeExportServiceTracePageV1 | null;
}

export interface DataPanelExportDiagnosticsFindingRow {
  severity: string;
  code: string;
  message: string;
  tone: "info" | "warn" | "error";
}

export interface DataPanelExportRouteDetailIndexDisplay {
  packageId: string;
  tone: "match" | "different";
  statusLabel: string;
  summaryLabel: string;
  metaLabels: readonly string[];
  boundaryLabels: readonly string[];
  routeRows: readonly DataPanelExportRouteDetailIndexRouteRow[];
  filterLabel: string;
  pageCursor: number;
  pageLimit: number;
  previousCursor: number;
  nextCursor: number;
  canPreviousPage: boolean;
  canNextPage: boolean;
  indexHref: string;
}

export interface DataPanelExportRouteDetailIndexStatus {
  tone: "match" | "different" | "pending" | "error";
  statusLabel: string;
  summaryLabel: string;
  metaLabels: readonly string[];
  boundaryLabels: readonly string[];
  routeRows: readonly DataPanelExportRouteDetailIndexRouteRow[];
  filterLabel: string;
  pageCursor: number;
  pageLimit: number;
  previousCursor: number;
  nextCursor: number;
  canPreviousPage: boolean;
  canNextPage: boolean;
  indexHref: string | null;
}

export interface DataPanelExportRouteDetailIndexRouteRow {
  routeId: string;
  pathLabel: string;
  metricLabel: string;
  available: boolean;
  title: string;
  packageDetailHref: string;
  compareActionLabel: string;
  liveDetailActionLabel: string;
}

export interface DataPanelExportRouteDetailIndexDisplayOptions {
  routeLimit?: number;
  query?: string;
}

export interface DataPanelExportRouteDetailPageRequest {
  cursor: number;
  limit?: number;
  filters?: DataPanelRouteExplanationFilter;
}

export interface DataPanelExportServiceTracePageRequest {
  cursor: number;
  limit?: number;
  filters?: DataPanelServiceTraceFilter;
}

export interface DataPanelExportUserServiceRequestPageRequest {
  cursor: number;
  limit?: number;
  filters?: DataPanelUserServiceRequestFilter;
}

export interface DataPanelExportRouteDetailItemDisplay {
  packageId: string;
  routeId: string;
  tone: "match" | "different";
  statusLabel: string;
  summaryLabel: string;
  fields: readonly DataPanelDetailInspectorField[];
  detailHref: string;
}

export interface DataPanelExportRouteDetailItemStatus {
  packageId: string | null;
  routeId: string | null;
  tone: "match" | "different" | "pending" | "error";
  statusLabel: string;
  summaryLabel: string;
  fields: readonly DataPanelDetailInspectorField[];
  detailHref: string | null;
}

export interface DataPanelExportRouteLiveComparisonDisplay {
  routeId: string;
  tone: "match" | "different";
  statusLabel: string;
  summaryLabel: string;
  rows: readonly DataPanelExportRouteLiveComparisonRow[];
}

export interface DataPanelExportRouteLiveComparisonRow {
  field: string;
  packageValue: string;
  liveValue: string;
  matches: boolean;
  statusLabel: string;
}

export interface DataPanelExportRouteLiveComparisonStatus {
  tone: "pending" | "error" | "different";
  statusLabel: string;
  summaryLabel: string;
  notes: readonly string[];
}

export interface DataPanelExportRouteComparisonReviewSaveRequest {
  packageId: string;
  record: Partial<RuntimeExportRouteComparisonReviewReportRecordV1>;
}

export type DataPanelScenarioReviewChecklistStatus =
  | "REVIEWED"
  | "SKIPPED"
  | "NEEDS_FOLLOWUP"
  | "ERROR";

export interface DataPanelScenarioReviewChecklistDraftEntry {
  reviewStatus: DataPanelScenarioReviewChecklistStatus;
  operatorNote: string;
}

export type DataPanelScenarioReviewChecklistDraft = Record<
  string,
  DataPanelScenarioReviewChecklistDraftEntry
>;

export interface DataPanelExportScenarioReviewChecklistSaveRequest {
  packageId: string;
  records: readonly Partial<RuntimeExportScenarioReviewChecklistRecordV1>[];
}

export interface DataPanelExportRouteComparisonReviewSaveStatus {
  routeId: string;
  tone: "ready" | "pending" | "error" | "success";
  buttonLabel: string;
  detailLabel: string;
  disabled: boolean;
}

export interface DataPanelExportManifestInspectorDisplay {
  packageId: string;
  tone: "match" | "different";
  statusLabel: string;
  summaryLabel: string;
  hashLabels: readonly string[];
  integrityLabels: readonly string[];
  artifactRows: readonly DataPanelExportManifestArtifactRow[];
  manifestHref: string;
}

export interface DataPanelExportManifestInspectorStatus {
  tone: "match" | "different" | "pending" | "error";
  statusLabel: string;
  summaryLabel: string;
  hashLabels: readonly string[];
  integrityLabels: readonly string[];
  artifactRows: readonly DataPanelExportManifestArtifactRow[];
  manifestHref: string | null;
}

export interface DataPanelExportManifestArtifactRow {
  name: string;
  statusLabel: string;
  sourceLabel: string;
  href: string;
  catalogPresent: boolean;
  title: string;
}

export interface DataPanelExportReproducibilityBoundaryDisplay {
  packageId: string;
  tone: "match" | "different";
  statusLabel: string;
  summaryLabel: string;
  scopeLabels: readonly string[];
  boundaryLabels: readonly string[];
  windowLabels: readonly string[];
  conditionLabels: readonly string[];
  boundaryHref: string;
}

export interface DataPanelExportBoundaryAlignmentDisplay {
  packageId: string;
  tone: "match" | "different" | "pending";
  statusLabel: string;
  summaryLabel: string;
  evidenceLabels: readonly string[];
  compareLabels: readonly string[];
  restoreLabels: readonly string[];
  warningLabels: readonly string[];
}

export interface DataPanelExportRestorePreflightDisplay {
  packageId: string;
  readiness: string;
  canRestore: boolean;
  tone: "match" | "different" | "error";
  statusLabel: string;
  summaryLabel: string;
  metaLabels: readonly string[];
  warningRows: readonly string[];
}

export interface DataPanelExportRestorePreflightStatus {
  tone: "match" | "different" | "pending" | "error";
  packageId: string | null;
  readiness: string | null;
  canRestore: boolean;
  statusLabel: string;
  summaryLabel: string;
  metaLabels: readonly string[];
  warningRows: readonly string[];
}

export interface DataPanelExportRestoreActionDisplay {
  packageId: string;
  tone: "ready" | "confirm" | "pending" | "disabled" | "error" | "success";
  buttonLabel: string;
  detailLabel: string;
  disabled: boolean;
  requiresSecondClick: boolean;
}

export interface DataPanelExportCompareDiffRow {
  section: string;
  path: string;
  valueLabel: string;
  title: string;
}

function runtimeExportRouteComparisonReviewLabels(
  review: RuntimeExportRouteComparisonReviewV1 | null | undefined
): readonly string[] {
  if (review === null || review === undefined) {
    return [];
  }
  return [
    `route compare ${review.compare_action}`,
    `compare fields ${formatCount(review.compared_fields.length)}`,
    review.comparison_requires_live_runtime
      ? "live runtime required"
      : "offline route comparison",
    review.review_report_type ? `report ${review.review_report_type}` : ""
  ].filter((label) => label.length > 0);
}

function runtimeExportNetworkKpiBenchmarkValidationLabels(
  validation: RuntimeExportNetworkKpiBenchmarkValidationEvidenceV1 | null | undefined
): readonly string[] {
  if (validation === null || validation === undefined) {
    return [];
  }
  return [
    `KPI benchmark ${validation.validation_status}`,
    `KPI failed ${formatCount(validation.failed_check_count)}`,
    `KPI checks ${formatCount(validation.check_count)}`,
    `KPI benchmark ${shortRuntimeHash(validation.validation_hash)}`
  ];
}

function runtimeExportUserServiceRequestLabels(
  evidence: RuntimeExportUserServiceRequestEvidenceV2 | null | undefined
): readonly string[] {
  if (evidence === null || evidence === undefined) {
    return [];
  }
  return [
    `user services ${evidence.evidence_present ? "present" : "missing"}`,
    `user service requests ${formatCount(evidence.request_count)}`,
    `user services exported ${formatCount(evidence.exported_request_count)}`,
    `user services hidden ${formatCount(evidence.hidden_request_count)}`,
    `compute requests ${formatCount(evidence.compute_request_count)}`,
    `network waiting ${formatCount(evidence.network_waiting_request_count)}`,
    `user services ${shortRuntimeHash(evidence.summary_hash)}`
  ];
}

export function buildDataPanelExportReviewSummaryDisplay(
  summary: RuntimeExportReviewSummaryV1 | null | undefined
): DataPanelExportReviewSummaryDisplay | null {
  if (summary === null || summary === undefined) {
    return null;
  }
  const reviewReady = summary.review_status === "REVIEW_READY";
  const missing = summary.artifacts.missing_required_filenames;
  return {
    packageId: summary.package_id,
    tone: reviewReady ? "match" : "different",
    statusLabel: reviewReady ? "可审阅" : "审阅不完整",
    summaryLabel: `${summary.package_id} / ${formatCount(
      summary.artifacts.artifact_count
    )} 个文件 / ${formatPreciseMetricValue(
      summary.runtime.current_sim_time
    )} s / ${formatCount(summary.runtime.processed_event_count)} 事件`,
    metaLabels: [
      `seed ${summary.scenario.seed}`,
      `卫星 ${formatCount(Number(summary.scenario.satellite_count) || 0)}`,
      `用户 ${formatCount(Number(summary.scenario.user_count) || 0)}`,
      `算力 ${formatCount(Number(summary.scenario.compute_node_count) || 0)}`,
      `manifest ${shortRuntimeHash(summary.reproducibility.manifest_hash)}`,
      `summary ${shortRuntimeHash(summary.summary_hash)}`,
      ...runtimeExportNetworkKpiBenchmarkValidationLabels(
        summary.network_kpi_benchmark_validation
      ),
      ...runtimeExportUserServiceRequestLabels(summary.user_service_requests),
      ...runtimeExportRouteComparisonReviewLabels(summary.route_comparison_review)
    ],
    artifactLabels: [
      `必需文件缺失 ${formatCount(missing.length)}`,
      `service trace ${
        summary.artifacts.service_lifecycle_trace_exported ? "已导出" : "缺失"
      }`,
      `review summary ${
        summary.artifacts.review_summary_exported ? "已导出" : "缺失"
      }`,
      ...(summary.artifacts.user_service_request_summary_exported !== undefined
        ? [
            `user services ${
              summary.artifacts.user_service_request_summary_exported
                ? "exported"
                : "missing"
            }`
          ]
        : []),
      ...missing.map((filename) => `缺失 ${filename}`)
    ]
  };
}

export function buildDataPanelExportReviewSummaryStatus(
  display: DataPanelExportReviewSummaryDisplay | null,
  selectedPackageId: string | null | undefined,
  loading = false,
  error: string | null | undefined = null
): DataPanelExportReviewSummaryStatus | null {
  if (loading) {
    return {
      tone: "pending",
      statusLabel: "正在加载审阅摘要",
      summaryLabel: selectedPackageId ?? "等待复盘包选择",
      metaLabels: ["只读摘要", "不生成新导出包"],
      artifactLabels: []
    };
  }
  if (error !== null && error !== undefined) {
    return {
      tone: "error",
      statusLabel: "审阅摘要加载失败",
      summaryLabel: selectedPackageId ?? "未知复盘包",
      metaLabels: [error],
      artifactLabels: []
    };
  }
  if (display === null) {
    return null;
  }
  return display;
}

export function buildDataPanelExportDiagnosticsDisplay(
  diagnostics: RuntimeExportDiagnosticsBundleV1 | null | undefined
): DataPanelExportDiagnosticsDisplay | null {
  if (diagnostics === null || diagnostics === undefined) {
    return null;
  }
  const packageId = diagnostics.package.package_id;
  const errorCount = diagnostics.findings.filter(
    (finding) => finding.severity === "ERROR"
  ).length;
  const warnCount = diagnostics.findings.filter(
    (finding) => finding.severity === "WARN"
  ).length;
  const complete = diagnostics.package.package_complete && errorCount === 0;
  const missingRequired =
    diagnostics.artifact_health.missing_required_filenames.length;
  const missingRecommended =
    diagnostics.artifact_health.missing_recommended_filenames.length;
  return {
    packageId,
    tone: complete ? "match" : "different",
    statusLabel: complete ? "诊断通过" : "需要处理",
    summaryLabel: `${packageId} / findings ${formatCount(
      diagnostics.finding_count
    )} / artifacts ${formatCount(
      diagnostics.artifact_health.artifact_count
    )} / ${shortRuntimeHash(diagnostics.diagnostics_hash)}`,
    metaLabels: [
      `manifest ${diagnostics.reproducibility.manifest_ok ? "OK" : "异常"}`,
      `必需缺失 ${formatCount(missingRequired)}`,
      `推荐缺失 ${formatCount(missingRecommended)}`,
      `ERROR ${formatCount(errorCount)}`,
      `WARN ${formatCount(warnCount)}`,
      `events ${formatCount(diagnostics.runtime.processed_event_count)}`
    ],
    modelBoundaryLabels: [
      diagnostics.model_boundaries.event_kernel_policy,
      diagnostics.model_boundaries.packet_level_simulation
        ? "含包级仿真"
        : "无包级仿真",
      `禁用 ${diagnostics.model_boundaries.forbidden_external_integrations.join("/")}`,
      diagnostics.model_boundaries.diagnostics_policy,
      ...runtimeExportNetworkKpiBenchmarkValidationLabels(
        diagnostics.network_kpi_benchmark_validation
      ),
      ...runtimeExportUserServiceRequestLabels(diagnostics.user_service_requests),
      ...runtimeExportRouteComparisonReviewLabels(
        diagnostics.route_comparison_review
      )
    ],
    findingRows: diagnostics.findings.map((finding) => ({
      severity: finding.severity,
      code: finding.code,
      message: finding.message,
      tone:
        finding.severity === "ERROR"
          ? "error"
          : finding.severity === "WARN"
            ? "warn"
            : "info"
    })),
    actionLabels: diagnostics.recommended_next_actions,
    diagnosticsHref: runtimeExportPackageFileHref(packageId, "diagnostics_bundle_v1.json")
  };
}

export function buildDataPanelExportDiagnosticsStatus(
  display: DataPanelExportDiagnosticsDisplay | null,
  selectedPackageId: string | null | undefined,
  loading = false,
  error: string | null | undefined = null
): DataPanelExportDiagnosticsStatus | null {
  if (loading) {
    return {
      tone: "pending",
      statusLabel: "正在加载诊断包",
      summaryLabel: selectedPackageId ?? "等待复盘包选择",
      metaLabels: ["只读诊断", "不执行恢复或重放"],
      modelBoundaryLabels: [],
      findingRows: [],
      actionLabels: [],
      diagnosticsHref: null
    };
  }
  if (error !== null && error !== undefined) {
    return {
      tone: "error",
      statusLabel: "诊断包加载失败",
      summaryLabel: selectedPackageId ?? "未知复盘包",
      metaLabels: [error],
      modelBoundaryLabels: [],
      findingRows: [],
      actionLabels: [],
      diagnosticsHref: null
    };
  }
  if (display === null) {
    return null;
  }
  return display;
}

export function buildDataPanelExportServiceLifecycleTraceStatus(
  display: DataPanelServiceLifecycleTraceDisplay | null,
  trace: RuntimeServiceLifecycleTraceV2 | null | undefined,
  selectedPackageId: string | null | undefined,
  loading = false,
  error: string | null | undefined = null,
  options: DataPanelExportServiceLifecycleTraceStatusOptions = {}
): DataPanelExportServiceLifecycleTraceStatus | null {
  const emptyPage = dataPanelExportServiceTracePageFields(0, 5, 0);
  if (loading) {
    return {
      tone: "pending",
      statusLabel: "loading service trace artifact",
      summaryLabel: selectedPackageId ?? "waiting for package selection",
      metaLabels: ["read-only artifact", "no service replay"],
      traceHref: null,
      display: null,
      filterLabel: "all service traces / local artifact page 0 / 0",
      ...emptyPage
    };
  }
  if (error !== null && error !== undefined) {
    return {
      tone: "error",
      statusLabel: "service trace artifact load failed",
      summaryLabel: selectedPackageId ?? "unknown package",
      metaLabels: [error],
      traceHref: null,
      display: null,
      filterLabel: "all service traces / local artifact page 0 / 0",
      ...emptyPage
    };
  }
  if (display === null || trace === null || trace === undefined) {
    return null;
  }
  const packageId = selectedPackageId ?? "selected-package";
  const complete = trace.incomplete_trace_count === 0 && trace.running_trace_count === 0;
  const backendPage = options.backendPage ?? null;
  const filter = {
    query: options.query ?? "",
    terminalState: normalizeServiceTraceTerminalFilter(options.terminalState),
    computeNodeId: options.computeNodeId ?? "",
    stageKind: normalizeServiceTraceStageFilter(options.stageKind),
    terminalReason: normalizeServiceTraceTerminalReasonFilter(options.terminalReason)
  };
  const filteredDisplay =
    backendPage === null ? filterServiceLifecycleTraceDisplay(display, filter) : display;
  const page =
    backendPage === null
      ? dataPanelExportServiceTracePageFields(
          options.cursor,
          options.limit,
          filteredDisplay.items.length
        )
      : dataPanelExportServiceTraceBackendPageFields(backendPage);
  const pageEnd =
    backendPage === null
      ? Math.min(page.pageCursor + page.pageLimit, filteredDisplay.items.length)
      : Math.min(backendPage.cursor + backendPage.item_count, backendPage.trace_count);
  const pageDisplay = {
    ...filteredDisplay,
    summaryLabel: `${filteredDisplay.summaryLabel} / ${
      backendPage === null ? "artifact page" : "backend artifact page"
    } ${
      trace.service_count === 0 ? 0 : page.pageCursor + 1
    }-${pageEnd} of ${formatCount(trace.service_count)}`,
    items:
      backendPage === null
        ? filteredDisplay.items.slice(page.pageCursor, pageEnd)
        : filteredDisplay.items
  };
  const metaLabels = [
    `service ${formatCount(trace.service_count)}`,
    `hidden ${formatCount(trace.hidden_trace_count)}`,
    `cursor ${formatCount(trace.cursor)} -> ${formatCount(trace.next_cursor)}`,
    trace.has_more ? "has more" : "complete window",
    trace.trace_model ? `model ${trace.trace_model}` : "model unspecified"
  ];
  if (backendPage !== null) {
    metaLabels.push(
      backendPage.artifact_window_only ? "artifact window only" : "full trace window",
      `page hash ${shortRuntimeHash(backendPage.page_hash)}`
    );
  }
  return {
    tone: complete ? "match" : "different",
    statusLabel: complete
      ? "service traces complete"
      : "service traces need review",
    summaryLabel: `${packageId} / traces ${formatCount(
      trace.trace_count
    )} / complete ${formatCount(trace.complete_trace_count)} / running ${formatCount(
      trace.running_trace_count
    )} / incomplete ${formatCount(trace.incomplete_trace_count)}`,
    metaLabels,
    traceHref:
      selectedPackageId === null || selectedPackageId === undefined
        ? null
        : runtimeExportPackageFileHref(
            selectedPackageId,
            "service_lifecycle_trace_v2.json"
          ),
    display: pageDisplay,
    filterLabel:
      backendPage === null
        ? dataPanelExportServiceTraceFilterLabel(
            filter,
            filteredDisplay.items.length,
            page
          )
        : dataPanelExportServiceTraceBackendFilterLabel(backendPage),
    ...page
  };
}

export function buildDataPanelExportUserServiceRequestStatus(
  page: RuntimeExportUserServiceRequestPageV1 | null | undefined,
  selectedPackageId: string | null | undefined,
  loading = false,
  error: string | null | undefined = null,
  _filter: DataPanelUserServiceRequestFilter = {}
): DataPanelExportUserServiceRequestStatus | null {
  const emptyPage = dataPanelExportUserServiceRequestPageFields(0, 5, 0);
  if (loading) {
    return {
      tone: "pending",
      statusLabel: "loading user service requests",
      summaryLabel: selectedPackageId ?? "waiting for package selection",
      metaLabels: ["server-side artifact page", "no service recompute"],
      artifactHref: null,
      rows: [],
      filterLabel: "all user services / backend artifact page 0 / 0",
      ...emptyPage
    };
  }
  if (error !== null && error !== undefined) {
    return {
      tone: "error",
      statusLabel: "user service request page load failed",
      summaryLabel: selectedPackageId ?? "unknown package",
      metaLabels: [error],
      artifactHref: null,
      rows: [],
      filterLabel: "all user services / backend artifact page 0 / 0",
      ...emptyPage
    };
  }
  if (page === null || page === undefined) {
    return null;
  }
  const summary = runtimeExportUserServiceRequestPageToSummary(page);
  const rows = buildBackendUserBusinessRequestRows(summary, page.items.length).items;
  const policy = page.user_service_request_export_policy ?? {};
  const policyLabel =
    typeof policy.policy === "string"
      ? policy.policy
      : "EXPORT_USER_SERVICE_REQUEST_WINDOW";
  const tone =
    page.packet_level_simulation || page.frontend_inference_required
      ? "different"
      : "match";
  const packageId = selectedPackageId ?? page.package_id;
  const pageFields = dataPanelExportUserServiceRequestBackendPageFields(page);
  return {
    tone,
    statusLabel:
      page.hidden_request_count > 0
        ? "user services windowed"
        : "user services paged",
    summaryLabel: `${page.package_id} / requests ${formatCount(
      page.request_count
    )} / page ${formatCount(page.item_count)} / active ${formatCount(
      page.active_request_count
    )}`,
    metaLabels: [
      `model ${page.request_model}`,
      `compute ${formatCount(page.compute_request_count)}`,
      `network waiting ${formatCount(page.network_waiting_request_count)}`,
      `hidden ${formatCount(page.hidden_request_count)}`,
      page.artifact_window_only ? "artifact window only" : "full artifact",
      `policy ${policyLabel}`,
      `artifact ${shortRuntimeHash(page.artifact_hash)}`,
      `summary ${shortRuntimeHash(page.summary_hash)}`,
      `page ${shortRuntimeHash(page.page_hash)}`,
      "row click links user/route/service evidence"
    ].filter((label) => label.length > 0),
    artifactHref: runtimeExportPackageFileHref(
      packageId,
      "user_service_request_summary_v2.json"
    ),
    rows,
    filterLabel: dataPanelExportUserServiceRequestBackendFilterLabel(page),
    ...pageFields
  };
}

function runtimeExportUserServiceRequestPageToSummary(
  page: RuntimeExportUserServiceRequestPageV1
): RuntimeUserServiceRequestSummaryV2 {
  return {
    version: "v2",
    source: page.source,
    summary_scope: page.summary_scope,
    cursor: page.cursor,
    limit: page.limit,
    next_cursor: page.next_cursor,
    has_more: page.has_more,
    user_count: page.request_count,
    unfiltered_user_count: page.unfiltered_request_count,
    item_count: page.item_count,
    active_user_count: page.active_request_count,
    compute_service_user_count: page.compute_request_count,
    waiting_user_count: page.network_waiting_request_count,
    window_user_count: page.item_count,
    window_active_user_count: page.items.filter((item) => item.request_active).length,
    window_compute_service_user_count: page.items.filter(
      (item) => item.compute_request_active
    ).length,
    window_waiting_user_count: page.items.filter((item) => item.network_waiting)
      .length,
    hidden_user_count: page.hidden_request_count,
    filter_query: page.filters.query,
    filter_applied: page.filter_applied,
    request_model: page.request_model,
    route_model: page.route_model,
    compute_model: page.compute_model,
    packet_level_simulation: page.packet_level_simulation,
    frontend_inference_required: page.frontend_inference_required,
    request_count: page.request_count,
    active_request_count: page.active_request_count,
    communication_request_count: page.communication_request_count,
    compute_request_count: page.compute_request_count,
    network_waiting_request_count: page.network_waiting_request_count,
    completed_request_count: Math.max(0, page.request_count - page.active_request_count),
    hidden_request_count: page.hidden_request_count,
    window_request_count: page.item_count,
    window_active_request_count: page.items.filter((item) => item.request_active)
      .length,
    window_compute_request_count: page.items.filter(
      (item) => item.compute_request_active
    ).length,
    window_network_waiting_request_count: page.items.filter(
      (item) => item.network_waiting
    ).length,
    unfiltered_request_count: page.unfiltered_request_count,
    items: page.items
  };
}

function dataPanelExportUserServiceRequestBackendPageFields(
  page: RuntimeExportUserServiceRequestPageV1
): Pick<
  DataPanelExportUserServiceRequestStatus,
  | "pageCursor"
  | "pageLimit"
  | "previousCursor"
  | "nextCursor"
  | "canPreviousPage"
  | "canNextPage"
> {
  const pageLimit = Math.max(1, Math.floor(page.limit));
  const pageCursor = Math.max(0, Math.floor(page.cursor));
  return {
    pageCursor,
    pageLimit,
    previousCursor: Math.max(0, pageCursor - pageLimit),
    nextCursor: Math.max(page.next_cursor, pageCursor),
    canPreviousPage: pageCursor > 0,
    canNextPage: page.has_more
  };
}

function dataPanelExportUserServiceRequestPageFields(
  cursor: number | null | undefined,
  limit: number | null | undefined,
  totalCount: number
): Pick<
  DataPanelExportUserServiceRequestStatus,
  | "pageCursor"
  | "pageLimit"
  | "previousCursor"
  | "nextCursor"
  | "canPreviousPage"
  | "canNextPage"
> {
  const pageLimit = Math.max(1, Math.floor(limit ?? 5));
  const boundedTotal = Math.max(0, Math.floor(totalCount));
  const maxCursor =
    boundedTotal === 0 ? 0 : Math.floor((boundedTotal - 1) / pageLimit) * pageLimit;
  const pageCursor = Math.min(Math.max(0, Math.floor(cursor ?? 0)), maxCursor);
  return {
    pageCursor,
    pageLimit,
    previousCursor: Math.max(0, pageCursor - pageLimit),
    nextCursor: Math.min(pageCursor + pageLimit, maxCursor),
    canPreviousPage: pageCursor > 0,
    canNextPage: pageCursor + pageLimit < boundedTotal
  };
}

function dataPanelExportUserServiceRequestBackendFilterLabel(
  page: RuntimeExportUserServiceRequestPageV1
): string {
  const filters = [
    page.filters.query ? `query ${page.filters.query}` : "",
    page.filters.service_class !== "ALL"
      ? `class ${page.filters.service_class}`
      : "",
    page.filters.terminal_state !== "ALL"
      ? `state ${page.filters.terminal_state}`
      : "",
    page.filters.network_waiting !== "ALL"
      ? `network ${page.filters.network_waiting}`
      : ""
  ].filter((item) => item.length > 0);
  const pageStart = page.request_count === 0 ? 0 : page.cursor + 1;
  const pageEnd = Math.min(page.cursor + page.item_count, page.request_count);
  return `${filters.length > 0 ? filters.join(" / ") : "all user services"} / backend artifact page ${formatCount(
    pageStart
  )}-${formatCount(pageEnd)} / ${formatCount(page.request_count)}`;
}

export function runtimeExportServiceTracePageToLifecycleTrace(
  page: RuntimeExportServiceTracePageV1
): RuntimeServiceLifecycleTraceV2 {
  return {
    version: "v2",
    contract_id: page.trace_contract_id,
    source: page.source,
    source_summary: `${page.source_summary} -> package service-traces page`,
    summary_scope: page.summary_scope,
    trace_model: page.trace_model,
    cursor: page.cursor,
    limit: page.limit,
    next_cursor: page.next_cursor,
    has_more: page.has_more,
    service_count: page.trace_count,
    trace_count: page.trace_count,
    complete_trace_count: page.complete_trace_count,
    running_trace_count: page.running_trace_count,
    incomplete_trace_count: page.incomplete_trace_count,
    hidden_trace_count: page.hidden_trace_count,
    unfiltered_service_count: page.unfiltered_trace_count,
    filter_query: page.filters.query || undefined,
    filter_terminal_state:
      page.filters.terminal_state !== "ALL"
        ? page.filters.terminal_state
        : undefined,
    filter_compute_node_id: page.filters.compute_node_id || undefined,
    filter_stage_kind:
      page.filters.stage_kind !== "ALL" ? page.filters.stage_kind : undefined,
    filter_terminal_reason:
      page.filters.terminal_reason !== "ALL"
        ? page.filters.terminal_reason
        : undefined,
    filter_applied: page.filter_applied,
    items: page.items
  };
}

function dataPanelExportServiceTraceBackendPageFields(
  page: RuntimeExportServiceTracePageV1
): Pick<
  DataPanelExportServiceLifecycleTraceStatus,
  | "pageCursor"
  | "pageLimit"
  | "previousCursor"
  | "nextCursor"
  | "canPreviousPage"
  | "canNextPage"
> {
  const pageLimit = Math.max(1, Math.floor(page.limit));
  const pageCursor = Math.max(0, Math.floor(page.cursor));
  return {
    pageCursor,
    pageLimit,
    previousCursor: Math.max(0, pageCursor - pageLimit),
    nextCursor: Math.max(page.next_cursor, pageCursor),
    canPreviousPage: pageCursor > 0,
    canNextPage: page.has_more
  };
}

function dataPanelExportServiceTraceBackendFilterLabel(
  page: RuntimeExportServiceTracePageV1
): string {
  const filters = [
    page.filters.query ? `query ${page.filters.query}` : "",
    page.filters.terminal_state !== "ALL"
      ? `state ${page.filters.terminal_state}`
      : "",
    page.filters.compute_node_id ? `compute ${page.filters.compute_node_id}` : "",
    page.filters.stage_kind !== "ALL" ? `stage ${page.filters.stage_kind}` : "",
    page.filters.terminal_reason !== "ALL"
      ? `reason ${page.filters.terminal_reason}`
      : ""
  ].filter((item) => item.length > 0);
  const pageStart = page.trace_count === 0 ? 0 : page.cursor + 1;
  const pageEnd = Math.min(page.cursor + page.item_count, page.trace_count);
  return `${filters.length > 0 ? filters.join(" / ") : "all service traces"} / backend artifact page ${formatCount(
    pageStart
  )}-${formatCount(pageEnd)} / ${formatCount(page.trace_count)}`;
}

function dataPanelExportServiceTracePageFields(
  cursor: number | null | undefined,
  limit: number | null | undefined,
  totalCount: number
): Pick<
  DataPanelExportServiceLifecycleTraceStatus,
  | "pageCursor"
  | "pageLimit"
  | "previousCursor"
  | "nextCursor"
  | "canPreviousPage"
  | "canNextPage"
> {
  const pageLimit = Math.max(1, Math.floor(limit ?? 5));
  const boundedTotal = Math.max(0, Math.floor(totalCount));
  const maxCursor =
    boundedTotal === 0 ? 0 : Math.floor((boundedTotal - 1) / pageLimit) * pageLimit;
  const pageCursor = Math.min(
    Math.max(0, Math.floor(cursor ?? 0)),
    maxCursor
  );
  const nextCursor = Math.min(pageCursor + pageLimit, maxCursor);
  return {
    pageCursor,
    pageLimit,
    previousCursor: Math.max(0, pageCursor - pageLimit),
    nextCursor,
    canPreviousPage: pageCursor > 0,
    canNextPage: pageCursor + pageLimit < boundedTotal
  };
}

function dataPanelExportServiceTraceFilterLabel(
  filter: Required<DataPanelServiceTraceFilter>,
  totalCount: number,
  page: Pick<
    DataPanelExportServiceLifecycleTraceStatus,
    "pageCursor" | "pageLimit"
  >
): string {
  const filters = [
    normalizeDetailFilter(filter.query ?? "").length > 0
      ? `query ${filter.query?.trim()}`
      : "",
    filter.terminalState !== "ALL" ? `state ${filter.terminalState}` : "",
    normalizeDetailFilter(filter.computeNodeId ?? "").length > 0
      ? `compute ${filter.computeNodeId?.trim()}`
      : "",
    filter.stageKind !== "ALL" ? `stage ${filter.stageKind}` : "",
    filter.terminalReason !== "ALL" ? `reason ${filter.terminalReason}` : ""
  ].filter((item) => item.length > 0);
  const pageStart = totalCount === 0 ? 0 : page.pageCursor + 1;
  const pageEnd = Math.min(page.pageCursor + page.pageLimit, totalCount);
  return `${filters.length > 0 ? filters.join(" / ") : "all service traces"} / local artifact page ${formatCount(
    pageStart
  )}-${formatCount(pageEnd)} / ${formatCount(totalCount)}`;
}

export function buildDataPanelExportRouteDetailIndexDisplay(
  index: RuntimeExportRouteDetailIndexV1 | null | undefined,
  options: DataPanelExportRouteDetailIndexDisplayOptions = {}
): DataPanelExportRouteDetailIndexDisplay | null {
  if (index === null || index === undefined) {
    return null;
  }
  const routeLimit = Math.max(0, options.routeLimit ?? 5);
  const query = normalizeRouteDetailIndexQuery(options.query ?? "");
  const summary = index.route_summary;
  const sampleCount = index.sample_route_ids.length;
  const indexedSampleCount = index.indexed_sample_route_ids.length;
  const missingSampleCount = index.missing_sample_route_ids.length;
  const evidenceComplete =
    index.packet_level_simulation === false &&
    index.all_pairs_computation === false &&
    missingSampleCount === 0;
  const filteredRoutes = filterRuntimeExportRouteDetailIndexRoutes(index.routes, query);
  const routeRows = filteredRoutes
    .slice(0, routeLimit)
    .map((route) =>
      buildDataPanelExportRouteDetailIndexRouteRow(index.package_id, route)
    );
  return {
    packageId: index.package_id,
    tone: evidenceComplete ? "match" : "different",
    statusLabel: evidenceComplete ? "路由证据可复盘" : "路由证据需核对",
    summaryLabel: `${index.package_id} / indexed ${formatCount(
      summary.indexed_route_count
    )}/${formatCount(summary.route_count)} / hidden ${formatCount(
      summary.hidden_route_count
    )} / ${shortRuntimeHash(index.route_detail_index_hash)}`,
    metaLabels: [
      `samples ${formatCount(indexedSampleCount)}/${formatCount(sampleCount)}`,
      `missing samples ${formatCount(missingSampleCount)}`,
      index.route_detail_export_policy
        ? `export limit ${formatCount(index.route_detail_export_policy.route_detail_limit)}`
        : "export limit legacy",
      `available ${formatCount(summary.available_route_count)}`,
      `blocked ${formatCount(summary.blocked_route_count)}`,
      `compute ${formatCount(summary.compute_service_route_count)}`,
      `network ${formatCount(summary.network_service_route_count)}`,
      ...runtimeExportRouteComparisonReviewLabels(index.route_comparison_review)
    ],
    boundaryLabels: [
      index.route_model || "UNKNOWN_ROUTE_MODEL",
      index.packet_level_simulation ? "包含包级仿真" : "无包级仿真",
      index.all_pairs_computation ? "包含全对全计算" : "无全对全路由计算",
      index.source_order_policy
    ],
    routeRows,
    filterLabel: buildRuntimeExportRouteDetailIndexFilterLabel(
      query,
      filteredRoutes.length,
      index.routes.length,
      routeRows.length,
      routeLimit
    ),
    pageCursor: 0,
    pageLimit: routeLimit,
    previousCursor: 0,
    nextCursor: routeRows.length,
    canPreviousPage: false,
    canNextPage: filteredRoutes.length > routeRows.length,
    indexHref: runtimeExportPackageFileHref(index.package_id, "route_detail_index_v1.json")
  };
}

export function buildDataPanelExportRouteDetailPageDisplay(
  page: RuntimeExportRouteDetailPageV1 | null | undefined
): DataPanelExportRouteDetailIndexDisplay | null {
  if (page === null || page === undefined) {
    return null;
  }
  const policy = page.route_detail_export_policy;
  const evidenceComplete =
    policy === undefined ||
    (policy.packet_level_simulation === false && policy.all_pairs_computation === false);
  const routeRows = page.items.map((route) =>
    buildDataPanelExportRouteDetailIndexRouteRow(page.package_id, route)
  );
  return {
    packageId: page.package_id,
    tone: evidenceComplete ? "match" : "different",
    statusLabel: evidenceComplete
      ? "package route evidence ready"
      : "package route evidence needs review",
    summaryLabel: `${page.package_id} / page ${formatCount(
      page.item_count
    )}/${formatCount(page.route_count)} / total ${formatCount(
      page.unfiltered_route_count
    )} / ${shortRuntimeHash(page.route_detail_index_hash)}`,
    metaLabels: [
      `server page ${formatCount(page.cursor)}-${formatCount(page.next_cursor)}`,
      `matched ${formatCount(page.route_count)}`,
      policy
        ? `export limit ${formatCount(policy.route_detail_limit)}`
        : "export limit legacy",
      `available ${formatCount(page.available_route_count)}`,
      `blocked ${formatCount(page.blocked_route_count)}`,
      `compute ${formatCount(page.compute_service_route_count)}`,
      `network ${formatCount(page.network_service_route_count)}`,
      ...runtimeExportRouteComparisonReviewLabels(page.route_comparison_review)
    ],
    boundaryLabels: [
      page.index_scope || "ROUTE_DETAIL_PAGE",
      page.source,
      page.filter_applied ? "server filter applied" : "server page unfiltered",
      policy?.policy ?? "LEGACY_ROUTE_DETAIL_INDEX",
      policy?.route_summary_source ?? "route_detail_index_v1.routes"
    ],
    routeRows,
    filterLabel: buildRuntimeExportRouteDetailPageFilterLabel(page),
    pageCursor: page.cursor,
    pageLimit: page.limit,
    previousCursor: Math.max(0, page.cursor - page.limit),
    nextCursor: page.next_cursor,
    canPreviousPage: page.cursor > 0,
    canNextPage: page.has_more,
    indexHref: runtimeExportPackageFileHref(page.package_id, "route_detail_index_v1.json")
  };
}

export function buildDataPanelExportRouteDetailItemDisplay(
  item: RuntimeExportRouteDetailItemV1 | null | undefined
): DataPanelExportRouteDetailItemDisplay | null {
  if (item === null || item === undefined) {
    return null;
  }
  const route = item.route;
  const available = route.available;
  return {
    packageId: item.package_id,
    routeId: item.route_id,
    tone: available ? "match" : "different",
    statusLabel: available
      ? "package route detail ready"
      : "package route detail blocked",
    summaryLabel: `${item.package_id} / ${item.route_id} / ${shortRuntimeHash(
      item.item_hash
    )}`,
    fields: [
      { label: "source", value: item.source },
      { label: "index hash", value: shortRuntimeHash(item.route_detail_index_hash) },
      { label: "flow", value: route.flow_id },
      { label: "business", value: route.business_label || route.business_type },
      { label: "source -> destination", value: `${route.source_id} -> ${route.destination_id}` },
      { label: "selected satellite", value: route.selected_satellite_id || "-" },
      {
        label: "next hops",
        value:
          route.next_hop_ids.length > 0
            ? route.next_hop_ids.join(" / ")
            : route.primary_next_hop_id || "-"
      },
      {
        label: "capacity / demand",
        value: routeExplanationCapacityDemandLabel(
          route.capacity_mbps,
          route.demand_mbps
        )
      },
      {
        label: "latency / loss",
        value: `${formatMetricMilliseconds(route.latency_s)} / ${formatRatioPercent(
          route.loss_proxy_rate
        )}`,
        tone: available ? "normal" : "warning"
      },
      {
        label: "pressure",
        value: formatRatioPercent(Math.max(0, route.route_pressure_proxy)),
        tone: route.route_pressure_proxy > 1 ? "warning" : "normal"
      },
      {
        label: "bottleneck",
        value: route.bottleneck_reason_label || route.bottleneck_component,
        tone: route.bottleneck_component === "NONE" ? "normal" : "warning"
      },
      { label: "path", value: route.path_label || route.path.join(" -> ") }
    ],
    detailHref: runtimeExportPackageRouteDetailHref(item.package_id, item.route_id)
  };
}

export function buildDataPanelExportRouteDetailItemStatus(
  display: DataPanelExportRouteDetailItemDisplay | null,
  selectedPackageId: string | null | undefined,
  selectedRouteId: string | null | undefined,
  loading = false,
  error: string | null | undefined = null
): DataPanelExportRouteDetailItemStatus | null {
  if (loading) {
    return {
      packageId: selectedPackageId ?? null,
      routeId: selectedRouteId ?? null,
      tone: "pending",
      statusLabel: "loading package route detail",
      summaryLabel: `${selectedPackageId ?? "package"} / ${
        selectedRouteId ?? "route"
      }`,
      fields: [],
      detailHref: null
    };
  }
  if (error !== null && error !== undefined) {
    return {
      packageId: selectedPackageId ?? null,
      routeId: selectedRouteId ?? null,
      tone: "error",
      statusLabel: "package route detail load failed",
      summaryLabel: `${selectedPackageId ?? "package"} / ${
        selectedRouteId ?? "route"
      }`,
      fields: [{ label: "error", value: error, tone: "warning" }],
      detailHref:
        selectedPackageId && selectedRouteId
          ? runtimeExportPackageRouteDetailHref(selectedPackageId, selectedRouteId)
          : null
    };
  }
  if (display === null) {
    return null;
  }
  if (selectedPackageId && display.packageId !== selectedPackageId) {
    return null;
  }
  if (selectedRouteId && display.routeId !== selectedRouteId) {
    return null;
  }
  return display;
}

export function buildDataPanelExportRouteLiveComparisonDisplay(
  packageItem: RuntimeExportRouteDetailItemV1 | null | undefined,
  liveDetail: RuntimeRouteExplanationItemV1 | null | undefined
): DataPanelExportRouteLiveComparisonDisplay | null {
  if (
    packageItem === null ||
    packageItem === undefined ||
    liveDetail === null ||
    liveDetail === undefined ||
    packageItem.route_id !== liveDetail.route_id
  ) {
    return null;
  }
  const packageRoute = packageItem.route;
  const rows = [
    routeComparisonRow("availability", packageRoute.available ? "available" : "blocked", liveDetail.available ? "available" : "blocked"),
    routeComparisonRow("business", packageRoute.business_type, liveDetail.business_type),
    routeComparisonRow("flow", packageRoute.flow_id, liveDetail.flow_id),
    routeComparisonRow("source -> destination", `${packageRoute.source_id} -> ${packageRoute.destination_id}`, `${liveDetail.source_id} -> ${liveDetail.destination_id}`),
    routeComparisonRow("selected satellite", packageRoute.selected_satellite_id || "-", liveDetail.selected_satellite_id || "-"),
    routeComparisonRow("primary next hop", packageRoute.primary_next_hop_id || "-", liveDetail.primary_next_hop_id || "-"),
    routeComparisonRow("path", routePathComparisonLabel(packageRoute), routePathComparisonLabel(liveDetail)),
    routeComparisonRow("capacity / demand", routeExplanationCapacityDemandLabel(packageRoute.capacity_mbps, packageRoute.demand_mbps), routeExplanationCapacityDemandLabel(liveDetail.capacity_mbps, liveDetail.demand_mbps)),
    routeComparisonRow("latency", formatMetricMilliseconds(packageRoute.latency_s), formatMetricMilliseconds(liveDetail.latency_s ?? 0)),
    routeComparisonRow("loss", formatRatioPercent(packageRoute.loss_proxy_rate), formatRatioPercent(liveDetail.loss_proxy_rate ?? 0)),
    routeComparisonRow("pressure", formatRatioPercent(Math.max(0, packageRoute.route_pressure_proxy)), formatRatioPercent(Math.max(0, liveDetail.route_pressure_proxy))),
    routeComparisonRow("bottleneck", packageRoute.bottleneck_component || "NONE", liveDetail.bottleneck_component || "NONE")
  ];
  const differentCount = rows.filter((row) => !row.matches).length;
  return {
    routeId: packageItem.route_id,
    tone: differentCount === 0 ? "match" : "different",
    statusLabel:
      differentCount === 0
        ? "package and live route match"
        : "package and live route differ",
    summaryLabel: `${packageItem.route_id} / matched ${formatCount(
      rows.length - differentCount
    )}/${formatCount(rows.length)} / differences ${formatCount(differentCount)}`,
    rows
  };
}

export function buildDataPanelExportRouteLiveComparisonStatus(
  comparison: DataPanelExportRouteLiveComparisonDisplay | null | undefined,
  packageItem: RuntimeExportRouteDetailItemV1 | null | undefined,
  packageStatus: DataPanelExportRouteDetailItemStatus | null | undefined,
  liveDetail: RuntimeRouteExplanationItemV1 | null | undefined,
  liveStatus: RuntimeExactDetailRequestState | null | undefined
): DataPanelExportRouteLiveComparisonStatus | null {
  if (comparison !== null && comparison !== undefined) {
    return null;
  }
  const packageRouteId = packageItem?.route_id ?? packageStatus?.routeId ?? null;
  const liveRouteId = liveDetail?.route_id ?? liveStatus?.entityId ?? null;
  if (packageStatus?.tone === "pending") {
    return routeComparisonStatus(
      "pending",
      "waiting for package route detail",
      packageRouteId,
      liveRouteId,
      ["Package route detail is still loading."]
    );
  }
  if (packageStatus?.tone === "error") {
    return routeComparisonStatus(
      "error",
      "package route detail unavailable",
      packageRouteId,
      liveRouteId,
      [packageStatus.fields[0]?.value ?? "Package route detail request failed."]
    );
  }
  if (liveStatus?.loading === true) {
    return routeComparisonStatus(
      "pending",
      "waiting for live route detail",
      packageRouteId,
      liveRouteId,
      ["Live runtime route detail is still loading."]
    );
  }
  if (liveStatus?.error) {
    return routeComparisonStatus(
      "error",
      "live route detail unavailable",
      packageRouteId,
      liveRouteId,
      [liveStatus.error]
    );
  }
  if (packageItem !== null && packageItem !== undefined && liveDetail === null) {
    return routeComparisonStatus(
      "pending",
      "live route detail not loaded",
      packageRouteId,
      liveRouteId,
      ["Use compare with live or live route detail to load the current runtime route."]
    );
  }
  if (liveDetail !== null && liveDetail !== undefined && packageItem === null) {
    return routeComparisonStatus(
      "pending",
      "package route detail not loaded",
      packageRouteId,
      liveRouteId,
      ["Use compare with live or package route detail to load the exported route."]
    );
  }
  if (
    packageItem !== null &&
    packageItem !== undefined &&
    liveDetail !== null &&
    liveDetail !== undefined &&
    packageItem.route_id !== liveDetail.route_id
  ) {
    return routeComparisonStatus(
      "different",
      "route id mismatch",
      packageRouteId,
      liveRouteId,
      ["Package and live details refer to different route ids."]
    );
  }
  return null;
}

export function buildDataPanelExportRouteComparisonReviewRecord(
  packageItem: RuntimeExportRouteDetailItemV1 | null | undefined,
  liveDetail: RuntimeRouteExplanationItemV1 | null | undefined,
  comparison: DataPanelExportRouteLiveComparisonDisplay | null | undefined
): Partial<RuntimeExportRouteComparisonReviewReportRecordV1> | null {
  if (
    packageItem === null ||
    packageItem === undefined ||
    liveDetail === null ||
    liveDetail === undefined ||
    comparison === null ||
    comparison === undefined ||
    packageItem.route_id !== liveDetail.route_id ||
    packageItem.route_id !== comparison.routeId
  ) {
    return null;
  }
  const comparedFields = comparison.rows.map((row) =>
    routeComparisonReportField(row.field)
  );
  const differentFields = comparison.rows
    .filter((row) => !row.matches)
    .map((row) => routeComparisonReportField(row.field));
  return {
    route_id: comparison.routeId,
    comparison_status: differentFields.length === 0 ? "MATCH" : "DIFFERENT",
    package_route_detail_hash: packageItem.item_hash,
    live_route_detail_hash: liveDetail.detail_hash ?? "",
    matched_field_count: comparedFields.length - differentFields.length,
    different_field_count: differentFields.length,
    compared_fields: comparedFields,
    different_fields: differentFields,
    status_reason: differentFields.length === 0 ? "MATCHED" : "FIELDS_DIFFER",
    operator_note: "Saved from dashboard package-vs-live route comparison."
  };
}

export function buildDataPanelExportRouteComparisonReviewSaveStatus(
  comparison: DataPanelExportRouteLiveComparisonDisplay | null | undefined,
  packageItem: RuntimeExportRouteDetailItemV1 | null | undefined,
  state: {
    pendingRouteId?: string | null;
    error?: string | null;
    reportHash?: string | null;
  } = {}
): DataPanelExportRouteComparisonReviewSaveStatus | null {
  if (
    comparison === null ||
    comparison === undefined ||
    packageItem === null ||
    packageItem === undefined ||
    packageItem.route_id !== comparison.routeId
  ) {
    return null;
  }
  if (state.pendingRouteId === comparison.routeId) {
    return {
      routeId: comparison.routeId,
      tone: "pending",
      buttonLabel: "saving report",
      detailLabel: "writing selected route comparison report",
      disabled: true
    };
  }
  if (state.error) {
    return {
      routeId: comparison.routeId,
      tone: "error",
      buttonLabel: "save review report",
      detailLabel: state.error,
      disabled: false
    };
  }
  if (state.reportHash) {
    return {
      routeId: comparison.routeId,
      tone: "success",
      buttonLabel: "save review report",
      detailLabel: `saved ${shortRuntimeHash(state.reportHash)}`,
      disabled: false
    };
  }
  return {
    routeId: comparison.routeId,
    tone: "ready",
    buttonLabel: "save review report",
    detailLabel: "persist selected comparison outcome into package report",
    disabled: false
  };
}

function routeComparisonStatus(
  tone: DataPanelExportRouteLiveComparisonStatus["tone"],
  statusLabel: string,
  packageRouteId: string | null,
  liveRouteId: string | null,
  notes: readonly string[]
): DataPanelExportRouteLiveComparisonStatus {
  return {
    tone,
    statusLabel,
    summaryLabel: `package ${packageRouteId ?? "-"} / live ${liveRouteId ?? "-"}`,
    notes
  };
}

function routeComparisonReportField(field: string): string {
  switch (field) {
    case "source -> destination":
      return "source_destination";
    case "selected satellite":
      return "selected_satellite";
    case "primary next hop":
      return "primary_next_hop";
    case "capacity / demand":
      return "capacity_demand";
    default:
      return field
        .trim()
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, "_")
        .replace(/^_+|_+$/g, "");
  }
}

function routeComparisonRow(
  field: string,
  packageValue: string,
  liveValue: string
): DataPanelExportRouteLiveComparisonRow {
  const matches = packageValue === liveValue;
  return {
    field,
    packageValue,
    liveValue,
    matches,
    statusLabel: matches ? "match" : "different"
  };
}

function routePathComparisonLabel(
  route: RuntimeExportRouteDetailIndexRouteV1 | RuntimeRouteExplanationItemV1
): string {
  const pathLabel = route.path_label;
  if (typeof pathLabel === "string" && pathLabel.length > 0) {
    return pathLabel;
  }
  if ("path" in route && Array.isArray(route.path)) {
    return route.path.join(" -> ");
  }
  return "-";
}

export function filterRuntimeExportRouteDetailIndexRoutes(
  routes: readonly RuntimeExportRouteDetailIndexRouteV1[],
  query: string
): readonly RuntimeExportRouteDetailIndexRouteV1[] {
  const normalizedQuery = normalizeRouteDetailIndexQuery(query);
  if (normalizedQuery.length === 0) {
    return routes;
  }
  const queryParts = normalizedQuery.split(" ").filter((part) => part.length > 0);
  return routes.filter((route) => {
    const haystack = runtimeExportRouteDetailIndexRouteSearchText(route);
    return queryParts.every((part) => haystack.includes(part));
  });
}

function buildRuntimeExportRouteDetailPageFilterLabel(
  page: RuntimeExportRouteDetailPageV1
): string {
  const query = page.filters.query.trim();
  const shownLabel = `shown ${formatCount(page.item_count)}/${formatCount(page.route_count)}`;
  const filterLabels = [
    query ? `query ${query}` : "",
    page.filters.availability !== "ALL" ? page.filters.availability : "",
    page.filters.business_type !== "ALL" ? page.filters.business_type : "",
    page.filters.bottleneck_component !== "ALL"
      ? page.filters.bottleneck_component
      : ""
  ].filter((label) => label.length > 0);
  if (filterLabels.length === 0) {
    return `${shownLabel} / total ${formatCount(page.unfiltered_route_count)} / server page`;
  }
  return `${shownLabel} / ${filterLabels.join(" / ")} / server page`;
}

function buildDataPanelExportRouteDetailIndexRouteRow(
  packageId: string,
  route: RuntimeExportRouteDetailIndexRouteV1
): DataPanelExportRouteDetailIndexRouteRow {
  return {
    routeId: route.route_id,
    pathLabel: route.path_label || `${route.source_id} -> ${route.destination_id}`,
    metricLabel: `${route.available ? "available" : "blocked"} / ${formatPreciseMetricValue(
      route.latency_s
    )} s / ${formatPreciseMetricValue(route.capacity_mbps)} Mbps / loss ${formatPreciseMetricValue(
      route.loss_proxy_rate
    )}`,
    available: route.available,
    title: `${route.flow_id} / ${route.business_type} / ${route.bottleneck_component} / ${route.explanation_label}`,
    packageDetailHref: runtimeExportPackageRouteDetailHref(packageId, route.route_id),
    compareActionLabel: "compare with live",
    liveDetailActionLabel: "live route detail"
  };
}

function normalizeRouteDetailIndexQuery(query: string): string {
  return query.trim().toLowerCase().replace(/\s+/g, " ");
}

function runtimeExportRouteDetailIndexRouteSearchText(
  route: RuntimeExportRouteDetailIndexRouteV1
): string {
  return [
    route.route_id,
    route.flow_id,
    route.user_id,
    route.source_id,
    route.destination_id,
    route.selected_satellite_id,
    route.primary_next_hop_id,
    route.business_type,
    route.business_label,
    route.bottleneck_component,
    route.bottleneck_reason,
    route.bottleneck_reason_label,
    route.explanation_label,
    route.path_label,
    ...route.next_hop_ids,
    ...route.path
  ]
    .join(" ")
    .toLowerCase();
}

function buildRuntimeExportRouteDetailIndexFilterLabel(
  query: string,
  filteredCount: number,
  totalCount: number,
  shownCount: number,
  routeLimit: number
): string {
  const shownLabel = `shown ${formatCount(shownCount)}/${formatCount(filteredCount)}`;
  const totalLabel = `indexed ${formatCount(totalCount)}`;
  const limitLabel = `limit ${formatCount(routeLimit)}`;
  if (query.length === 0) {
    return `${shownLabel} / ${totalLabel} / ${limitLabel}`;
  }
  return `${shownLabel} / matched ${formatCount(filteredCount)}/${formatCount(
    totalCount
  )} / query ${query}`;
}

export function buildDataPanelExportRouteDetailIndexStatus(
  display: DataPanelExportRouteDetailIndexDisplay | null,
  selectedPackageId: string | null | undefined,
  loading = false,
  error: string | null | undefined = null
): DataPanelExportRouteDetailIndexStatus | null {
  if (loading) {
    return {
      tone: "pending",
      statusLabel: "正在加载路由证据索引",
      summaryLabel: selectedPackageId ?? "等待复盘包选择",
      metaLabels: ["只读索引", "不重算路由"],
      boundaryLabels: [],
      routeRows: [],
      filterLabel: "loading route evidence index",
      pageCursor: 0,
      pageLimit: 5,
      previousCursor: 0,
      nextCursor: 0,
      canPreviousPage: false,
      canNextPage: false,
      indexHref: null
    };
  }
  if (error !== null && error !== undefined) {
    return {
      tone: "error",
      statusLabel: "路由证据索引加载失败",
      summaryLabel: selectedPackageId ?? "未知复盘包",
      metaLabels: [error],
      boundaryLabels: [],
      routeRows: [],
      filterLabel: "route evidence index unavailable",
      pageCursor: 0,
      pageLimit: 5,
      previousCursor: 0,
      nextCursor: 0,
      canPreviousPage: false,
      canNextPage: false,
      indexHref: null
    };
  }
  if (display === null) {
    return null;
  }
  return display;
}

export function buildDataPanelExportManifestInspectorDisplay(
  manifest: RuntimeReproducibilityManifestV1 | null | undefined,
  selectedPackageId: string | null | undefined,
  catalog: RuntimeExportCatalogV1 | null | undefined,
  diagnostics: RuntimeExportDiagnosticsBundleV1 | null | undefined
): DataPanelExportManifestInspectorDisplay | null {
  if (
    manifest === null ||
    manifest === undefined ||
    selectedPackageId === null ||
    selectedPackageId === undefined
  ) {
    return null;
  }
  const record =
    catalog === null || catalog === undefined
      ? null
      : selectRuntimeExportCatalogRecordForPackage(catalog, selectedPackageId);
  const filesByName = new Map(
    (record?.files ?? []).map((file) => [file.filename, file])
  );
  const manifestFile = filesByName.get("manifest.json") ?? null;
  const diagnosticsManifestHash = diagnostics?.reproducibility.manifest_hash ?? "";
  const diagnosticsMatch =
    diagnosticsManifestHash === "" || diagnosticsManifestHash === manifest.manifest_hash;
  const manifestIdOk =
    manifest.manifest_id === "leo_twin.runtime_reproducibility_manifest.v1";
  const artifactRows = [...manifest.artifacts]
    .sort((left, right) => left.name.localeCompare(right.name))
    .map((artifact) => {
      const file = filesByName.get(artifact.name) ?? null;
      const catalogHash = file ? ` / file ${shortRuntimeHash(file.sha256)}` : "";
      return {
        name: artifact.name,
        statusLabel: `${artifact.format} / ${artifact.status}`,
        sourceLabel: `${artifact.source}${catalogHash}`,
        href: runtimeExportPackageFileHref(selectedPackageId, artifact.name),
        catalogPresent: file !== null,
        title: `${artifact.name} / ${artifact.status} / ${artifact.source}${
          file ? ` / ${file.sha256}` : " / catalog missing"
        }`
      };
    });
  const catalogMissingCount = artifactRows.filter((row) => !row.catalogPresent).length;
  const artifactCount =
    typeof manifest.artifact_count === "number"
      ? manifest.artifact_count
      : manifest.artifacts.length;
  const matched =
    manifestIdOk && diagnosticsMatch && manifestFile !== null && catalogMissingCount === 0;
  return {
    packageId: selectedPackageId,
    tone: matched ? "match" : "different",
    statusLabel: matched ? "manifest 一致" : "manifest 需复核",
    summaryLabel: `${selectedPackageId} / ${manifest.artifact_policy} / ${formatCount(
      artifactCount
    )} artifacts / ${shortRuntimeHash(manifest.manifest_hash)}`,
    hashLabels: [
      `manifest ${shortRuntimeHash(manifest.manifest_hash)}`,
      `scenario ${shortRuntimeHash(manifest.scenario_hash)}`,
      `config ${shortRuntimeHash(manifest.control_config_hash)}`,
      `generated ${shortRuntimeHash(manifest.generated_config_hash)}`,
      `metrics ${shortRuntimeHash(manifest.metrics_summary_hash)}`,
      `runtime ${shortRuntimeHash(manifest.runtime_state_hash)}`
    ],
    integrityLabels: [
      `manifest id ${manifestIdOk ? "OK" : "异常"}`,
      `diagnostics ${diagnosticsMatch ? "一致" : "不一致"}`,
      `catalog manifest ${manifestFile ? shortRuntimeHash(manifestFile.sha256) : "缺失"}`,
      `catalog artifact 缺失 ${formatCount(catalogMissingCount)}`
    ],
    artifactRows,
    manifestHref: runtimeExportPackageManifestHref(selectedPackageId)
  };
}

export function buildDataPanelExportManifestInspectorStatus(
  display: DataPanelExportManifestInspectorDisplay | null,
  selectedPackageId: string | null | undefined,
  loading = false,
  error: string | null | undefined = null
): DataPanelExportManifestInspectorStatus | null {
  if (loading) {
    return {
      tone: "pending",
      statusLabel: "正在加载 manifest",
      summaryLabel: selectedPackageId ?? "等待复盘包选择",
      hashLabels: ["只读 manifest", "不执行重放"],
      integrityLabels: [],
      artifactRows: [],
      manifestHref: null
    };
  }
  if (error !== null && error !== undefined) {
    return {
      tone: "error",
      statusLabel: "manifest 加载失败",
      summaryLabel: selectedPackageId ?? "未知复盘包",
      hashLabels: [error],
      integrityLabels: [],
      artifactRows: [],
      manifestHref: null
    };
  }
  if (display === null) {
    return null;
  }
  return display;
}

export function buildDataPanelExportReproducibilityBoundaryDisplay(
  manifest: RuntimeReproducibilityManifestV1 | null | undefined,
  reviewSummary: RuntimeExportReviewSummaryV1 | null | undefined,
  diagnostics: RuntimeExportDiagnosticsBundleV1 | null | undefined,
  selectedPackageId: string | null | undefined
): DataPanelExportReproducibilityBoundaryDisplay | null {
  if (selectedPackageId === null || selectedPackageId === undefined) {
    return null;
  }
  const boundary = selectRuntimeExportReproducibilityBoundary(
    manifest,
    reviewSummary,
    diagnostics
  );
  if (boundary === null) {
    return null;
  }
  const boundaryHash = boundary.boundary_hash;
  const knownHashes = [
    manifest?.runtime_export_reproducibility_boundary_v1?.boundary_hash,
    reviewSummary?.reproducibility_boundary?.boundary_hash,
    reviewSummary?.reproducibility.boundary_hash,
    diagnostics?.reproducibility_boundary?.boundary_hash,
    diagnostics?.reproducibility.boundary_hash
  ].filter((value): value is string => typeof value === "string" && value.length > 0);
  const hashAgreement =
    boundaryHash.length > 0 && knownHashes.every((hash) => hash === boundaryHash);
  const forbiddenInactive =
    boundary.event_replay_restore === false &&
    boundary.live_event_replay_restore === false &&
    boundary.recompute_on_read === false &&
    boundary.route_recomputation === false &&
    boundary.service_recomputation === false &&
    boundary.package_mutation_on_read === false &&
    boundary.packet_capture === false &&
    boundary.packet_level_simulation === false &&
    boundary.external_simulators === false;
  const boundaryIdOk =
    boundary.boundary_id === "leo_twin.runtime_export_reproducibility_boundary.v1";
  const matched = boundaryIdOk && hashAgreement && forbiddenInactive;
  const routeWindow = boundary.route_detail_export;
  const serviceWindow = boundary.service_trace_export;
  return {
    packageId: selectedPackageId,
    tone: matched ? "match" : "different",
    statusLabel: matched ? "复现边界一致" : "复现边界需复核",
    summaryLabel: `${selectedPackageId} / ${boundary.restore_scope} / ${boundary.compare_scope} / ${shortRuntimeHash(
      boundaryHash
    )}`,
    scopeLabels: [
      `restore ${boundary.restore_scope}`,
      `compare ${boundary.compare_scope}`,
      `read ${boundary.read_scope}`,
      `manifest ${boundary.manifest_id || "-"}`,
      `boundary ${shortRuntimeHash(boundaryHash)}`,
      `hash ${hashAgreement ? "一致" : "不一致"}`
    ],
    boundaryLabels: [
      boundary.event_kernel_policy,
      boundary.deterministic_replay_evidence
        ? "deterministic artifact evidence"
        : "deterministic evidence missing",
      boundary.event_replay_restore ? "event replay restore enabled" : "no event replay restore",
      boundary.recompute_on_read ? "read recomputes model state" : "no recompute on read",
      boundary.package_mutation_on_read ? "read mutates package" : "no package mutation on read",
      boundary.packet_level_simulation ? "packet-level simulation" : "no packet-level simulation",
      boundary.external_simulators ? "external simulators present" : "no external simulator artifacts"
    ],
    windowLabels: [
      `route policy ${routeWindow.policy || "-"}`,
      `routes ${formatCount(routeWindow.indexed_route_count ?? 0)}/${formatCount(
        routeWindow.route_count ?? 0
      )}`,
      `hidden routes ${formatCount(routeWindow.hidden_route_count ?? 0)}`,
      `service policy ${serviceWindow.policy || "-"}`,
      `service traces ${formatCount(
        serviceWindow.exported_trace_count ?? 0
      )}/${formatCount(serviceWindow.service_count ?? 0)}`,
      `hidden traces ${formatCount(serviceWindow.hidden_trace_count ?? 0)}`
    ],
    conditionLabels: boundary.boundary_conditions,
    boundaryHref: runtimeExportPackageManifestHref(selectedPackageId)
  };
}

function selectRuntimeExportReproducibilityBoundary(
  manifest: RuntimeReproducibilityManifestV1 | null | undefined,
  reviewSummary: RuntimeExportReviewSummaryV1 | null | undefined,
  diagnostics: RuntimeExportDiagnosticsBundleV1 | null | undefined
): RuntimeExportReproducibilityBoundaryV1 | null {
  return (
    manifest?.runtime_export_reproducibility_boundary_v1 ??
    reviewSummary?.reproducibility_boundary ??
    diagnostics?.reproducibility_boundary ??
    null
  );
}

function selectRuntimeExportBoundaryAlignment(
  compare: RuntimeExportPackageCompareV1 | null | undefined,
  preflight: RuntimeExportRestorePreflightV1 | null | undefined
) {
  return (
    preflight?.runtime_export_boundary_alignment_v1 ??
    compare?.runtime_export_boundary_alignment_v1 ??
    null
  );
}

export function buildDataPanelExportBoundaryAlignmentDisplay(
  manifest: RuntimeReproducibilityManifestV1 | null | undefined,
  reviewSummary: RuntimeExportReviewSummaryV1 | null | undefined,
  diagnostics: RuntimeExportDiagnosticsBundleV1 | null | undefined,
  compare: RuntimeExportPackageCompareV1 | null | undefined,
  preflight: RuntimeExportRestorePreflightV1 | null | undefined,
  selectedPackageId: string | null | undefined
): DataPanelExportBoundaryAlignmentDisplay | null {
  if (selectedPackageId === null || selectedPackageId === undefined) {
    return null;
  }
  const boundary = selectRuntimeExportReproducibilityBoundary(
    manifest,
    reviewSummary,
    diagnostics
  );
  const backendAlignment = selectRuntimeExportBoundaryAlignment(compare, preflight);
  const backendEvidenceLabels =
    backendAlignment === null
      ? []
      : [
          `backend ${backendAlignment.alignment_status}`,
          `alignment ${shortRuntimeHash(backendAlignment.alignment_hash)}`,
          `backend boundary ${shortRuntimeHash(backendAlignment.boundary_hash)}`
        ];
  const warnings: string[] = [...(backendAlignment?.warnings ?? [])];
  const compareLabels =
    compare === null || compare === undefined
      ? ["compare not loaded"]
      : [
          `compare ${compare.comparison_scope}`,
          `package ${compare.package_id}`,
          `same config ${compare.same_config ? "yes" : "no"}`,
          `same generated ${compare.same_generated_config ? "yes" : "no"}`,
          `compare ${shortRuntimeHash(compare.compare_hash)}`
        ];
  const restoreLabels =
    preflight === null || preflight === undefined
      ? ["restore preflight not loaded"]
      : [
          `preflight ${preflight.preflight_scope}`,
          `readiness ${preflight.readiness}`,
          `can restore ${preflight.can_restore ? "yes" : "no"}`,
          `mutate current ${preflight.would_mutate_current_runtime ? "yes" : "no"}`,
          `write config ${preflight.would_write_config_files ? "yes" : "no"}`
        ];

  if (boundary === null) {
    if (backendAlignment !== null) {
      const backendAligned =
        backendAlignment.alignment_status === "ALIGNED" && warnings.length === 0;
      return {
        packageId: selectedPackageId,
        tone: backendAligned ? "match" : "different",
        statusLabel: backendAligned ? "后端边界证据一致" : "后端边界证据需复核",
        summaryLabel: `${selectedPackageId} / backend boundary ${shortRuntimeHash(
          backendAlignment.boundary_hash
        )} / warnings ${formatCount(warnings.length)}`,
        evidenceLabels: [
          `source ${backendAlignment.source}`,
          ...backendEvidenceLabels,
          `restore ${backendAlignment.restore_scope || "-"}`,
          `compare ${backendAlignment.compare_scope || "-"}`,
          `read ${backendAlignment.read_scope || "-"}`
        ],
        compareLabels,
        restoreLabels,
        warningLabels: warnings
      };
    }
    warnings.push("runtime_export_reproducibility_boundary_v1 missing");
    return {
      packageId: selectedPackageId,
      tone: "different",
      statusLabel: "缺少复现边界",
      summaryLabel: `${selectedPackageId} / compare+restore 缺少统一边界证据`,
      evidenceLabels: ["manifest/review/diagnostics boundary missing"],
      compareLabels,
      restoreLabels,
      warningLabels: warnings
    };
  }

  const hashAgreement = runtimeExportBoundaryHashAgreement(
    boundary,
    manifest,
    reviewSummary,
    diagnostics
  );
  if (!hashAgreement) {
    warnings.push("boundary hash mismatch across loaded artifacts");
  }
  if (
    boundary.boundary_id !== "leo_twin.runtime_export_reproducibility_boundary.v1"
  ) {
    warnings.push("unexpected reproducibility boundary id");
  }
  if (boundary.restore_scope !== "CONFIG_ONLY") {
    warnings.push(`restore scope is ${boundary.restore_scope}`);
  }
  if (boundary.compare_scope !== "CONFIG_AND_GENERATED_CONFIG") {
    warnings.push(`compare scope is ${boundary.compare_scope}`);
  }
  if (boundary.read_scope !== "PERSISTED_ARTIFACTS_ONLY") {
    warnings.push(`read scope is ${boundary.read_scope}`);
  }
  if (
    boundary.event_replay_restore ||
    boundary.live_event_replay_restore ||
    boundary.recompute_on_read ||
    boundary.route_recomputation ||
    boundary.service_recomputation ||
    boundary.package_mutation_on_read ||
    boundary.packet_capture ||
    boundary.packet_level_simulation ||
    boundary.external_simulators
  ) {
    warnings.push("boundary enables replay, recompute, mutation, packet, or external simulator behavior");
  }
  if (compare === null || compare === undefined) {
    warnings.push("package compare not loaded");
  } else {
    if (compare.package_id !== selectedPackageId) {
      warnings.push("compare package does not match selected package");
    }
    if (compare.comparison_scope !== boundary.compare_scope) {
      warnings.push("compare scope does not match boundary compare scope");
    }
  }
  if (preflight === null || preflight === undefined) {
    warnings.push("restore preflight not loaded");
  } else {
    if (preflight.package_id !== selectedPackageId) {
      warnings.push("restore preflight package does not match selected package");
    }
    if (preflight.preflight_scope !== "CONFIG_RESTORE_PREVIEW_ONLY") {
      warnings.push("restore preflight is not config restore preview only");
    }
    if (preflight.would_mutate_current_runtime) {
      warnings.push("restore preflight would mutate current runtime during preview");
    }
  }

  const pending =
    compare === null ||
    compare === undefined ||
    preflight === null ||
    preflight === undefined;
  const tone = warnings.length === 0 ? "match" : pending ? "pending" : "different";
  return {
    packageId: selectedPackageId,
    tone,
    statusLabel:
      warnings.length === 0
        ? "恢复判断有边界证据"
        : pending
          ? "等待边界关联证据"
          : "恢复判断需复核",
    summaryLabel: `${selectedPackageId} / boundary ${shortRuntimeHash(
      boundary.boundary_hash
    )} / warnings ${formatCount(warnings.length)}`,
    evidenceLabels: [
      ...backendEvidenceLabels,
      `boundary ${shortRuntimeHash(boundary.boundary_hash)}`,
      `hash ${hashAgreement ? "一致" : "不一致"}`,
      `restore ${boundary.restore_scope}`,
      `compare ${boundary.compare_scope}`,
      `read ${boundary.read_scope}`
    ],
    compareLabels,
    restoreLabels,
    warningLabels: warnings
  };
}

function runtimeExportBoundaryHashAgreement(
  boundary: RuntimeExportReproducibilityBoundaryV1,
  manifest: RuntimeReproducibilityManifestV1 | null | undefined,
  reviewSummary: RuntimeExportReviewSummaryV1 | null | undefined,
  diagnostics: RuntimeExportDiagnosticsBundleV1 | null | undefined
): boolean {
  const boundaryHash = boundary.boundary_hash;
  const knownHashes = [
    manifest?.runtime_export_reproducibility_boundary_v1?.boundary_hash,
    reviewSummary?.reproducibility_boundary?.boundary_hash,
    reviewSummary?.reproducibility.boundary_hash,
    diagnostics?.reproducibility_boundary?.boundary_hash,
    diagnostics?.reproducibility.boundary_hash
  ].filter((value): value is string => typeof value === "string" && value.length > 0);
  return boundaryHash.length > 0 && knownHashes.every((hash) => hash === boundaryHash);
}

export function buildDataPanelExportCompareDisplay(
  compare: RuntimeExportPackageCompareV1 | null | undefined,
  limit = 4
): DataPanelExportCompareDisplay | null {
  if (compare === null || compare === undefined) {
    return null;
  }
  const displayLimit = Math.max(0, limit);
  const diffRows = compare.differences.slice(0, displayLimit).map((item) => {
    const valueLabel = `${formatRuntimeExportDiffValue(
      item.package_value
    )} -> ${formatRuntimeExportDiffValue(item.current_value)}`;
    return {
      section: item.section,
      path: item.path,
      valueLabel,
      title: `${item.section} ${item.path}: ${valueLabel}`
    };
  });
  const match = compare.compatibility === "MATCH" && compare.diff_count === 0;
  const visibleDiffLabel =
    compare.diff_count > diffRows.length ? ` / 显示 ${formatCount(diffRows.length)} 项` : "";
  return {
    packageId: compare.package_id,
    tone: match ? "match" : "different",
    statusLabel: match ? "配置一致" : "配置不同",
    summaryLabel: `${compare.package_id} / 差异 ${formatCount(
      compare.diff_count
    )} 项${visibleDiffLabel}`,
    configLabel: `config ${compare.same_config ? "一致" : "不同"}`,
    generatedConfigLabel: `generated ${compare.same_generated_config ? "一致" : "不同"}`,
    hashLabel: `compare ${shortRuntimeHash(compare.compare_hash)}`,
    diffRows
  };
}

export function buildDataPanelExportCompareStatus(
  display: DataPanelExportCompareDisplay | null,
  selectedPackageId: string | null | undefined,
  loading = false,
  error: string | null | undefined = null
): DataPanelExportCompareStatus | null {
  if (loading) {
    return {
      tone: "pending",
      statusLabel: "正在加载对比",
      summaryLabel: selectedPackageId ?? "等待复盘包选择",
      metaLabels: ["只读预览", "不修改当前配置"],
      diffRows: []
    };
  }
  if (error !== null && error !== undefined) {
    return {
      tone: "error",
      statusLabel: "对比加载失败",
      summaryLabel: selectedPackageId ?? "未知复盘包",
      metaLabels: [error],
      diffRows: []
    };
  }
  if (display === null) {
    return null;
  }
  return {
    tone: display.tone,
    statusLabel: display.statusLabel,
    summaryLabel: display.summaryLabel,
    metaLabels: [display.configLabel, display.generatedConfigLabel, display.hashLabel],
    diffRows: display.diffRows
  };
}

export function buildDataPanelExportRestorePreflightDisplay(
  preflight: RuntimeExportRestorePreflightV1 | null | undefined
): DataPanelExportRestorePreflightDisplay | null {
  if (preflight === null || preflight === undefined) {
    return null;
  }
  const readiness = preflight.readiness;
  const tone =
    readiness === "NO_CHANGE" ? "match" : readiness === "BLOCKED" ? "error" : "different";
  const statusLabel =
    readiness === "NO_CHANGE"
      ? "无需恢复"
      : readiness === "BLOCKED"
        ? "预检阻塞"
        : "可恢复，需确认";
  const warningRows = [
    ...preflight.blocked_reasons.map((reason) => `阻塞: ${reason}`),
    ...preflight.warnings.map((warning) => `警告: ${warning}`)
  ];
  return {
    packageId: preflight.package_id,
    readiness,
    canRestore: preflight.can_restore,
    tone,
    statusLabel,
    summaryLabel: `${preflight.package_id} / config差异 ${formatCount(
      preflight.config_diff_count
    )} / generated差异 ${formatCount(preflight.generated_config_diff_count)}`,
    metaLabels: [
      `确认 ${preflight.requires_user_confirmation ? "需要" : "不需要"}`,
      `写配置 ${preflight.would_write_config_files ? "会" : "不会"}`,
      `重置runtime ${preflight.would_reset_runtime_session ? "会" : "不会"}`,
      `当前 ${preflight.current_lifecycle_state}`,
      `preflight ${shortRuntimeHash(preflight.preflight_hash)}`
    ],
    warningRows
  };
}

export function buildDataPanelExportRestorePreflightStatus(
  display: DataPanelExportRestorePreflightDisplay | null,
  selectedPackageId: string | null | undefined,
  loading = false,
  error: string | null | undefined = null
): DataPanelExportRestorePreflightStatus | null {
  if (loading) {
    return {
      tone: "pending",
      packageId: selectedPackageId ?? null,
      readiness: null,
      canRestore: false,
      statusLabel: "正在加载预检",
      summaryLabel: selectedPackageId ?? "等待复盘包选择",
      metaLabels: ["只读预检", "不会修改当前配置"],
      warningRows: []
    };
  }
  if (error !== null && error !== undefined) {
    return {
      tone: "error",
      packageId: selectedPackageId ?? null,
      readiness: "ERROR",
      canRestore: false,
      statusLabel: "预检加载失败",
      summaryLabel: selectedPackageId ?? "未知复盘包",
      metaLabels: [error],
      warningRows: []
    };
  }
  if (display === null) {
    return null;
  }
  return {
    tone: display.tone,
    packageId: display.packageId,
    readiness: display.readiness,
    canRestore: display.canRestore,
    statusLabel: display.statusLabel,
    summaryLabel: display.summaryLabel,
    metaLabels: display.metaLabels,
    warningRows: display.warningRows
  };
}

export function buildDataPanelExportRestoreActionDisplay(
  status: DataPanelExportRestorePreflightStatus | null,
  options: {
    selectedPackageId?: string | null;
    armedPackageId?: string | null;
    pendingPackageId?: string | null;
    commandError?: string | null;
    result?: RuntimeExportRestoreCommandResultV1 | null;
  } = {}
): DataPanelExportRestoreActionDisplay | null {
  if (status === null) {
    return null;
  }
  const packageId = status.packageId ?? options.selectedPackageId ?? "";
  if (packageId.length === 0) {
    return null;
  }
  if (options.pendingPackageId === packageId) {
    return {
      packageId,
      tone: "pending",
      buttonLabel: "恢复中",
      detailLabel: "正在通过控制通道恢复配置并重建运行时会话",
      disabled: true,
      requiresSecondClick: false
    };
  }
  if (options.result?.package_id === packageId && options.result.restored) {
    const rollbackLabel = options.result.rollback_package_id
      ? `回滚包 ${shortRuntimeHash(options.result.rollback_package_id)}`
      : "已生成回滚包";
    return {
      packageId,
      tone: "success",
      buttonLabel: "已恢复",
      detailLabel: rollbackLabel,
      disabled: true,
      requiresSecondClick: false
    };
  }
  if (options.commandError !== null && options.commandError !== undefined) {
    return {
      packageId,
      tone: "error",
      buttonLabel: "重试恢复",
      detailLabel: options.commandError,
      disabled: !status.canRestore || status.readiness !== "READY",
      requiresSecondClick: true
    };
  }
  if (!status.canRestore || status.readiness === "BLOCKED") {
    return {
      packageId,
      tone: "disabled",
      buttonLabel: "不可恢复",
      detailLabel: "恢复预检未通过，请先选择其他复盘包或修复包内容",
      disabled: true,
      requiresSecondClick: false
    };
  }
  if (status.readiness === "NO_CHANGE") {
    return {
      packageId,
      tone: "disabled",
      buttonLabel: "无需恢复",
      detailLabel: "当前配置已经与该复盘包一致",
      disabled: true,
      requiresSecondClick: false
    };
  }
  if (options.armedPackageId === packageId) {
    return {
      packageId,
      tone: "confirm",
      buttonLabel: "确认恢复并生成回滚包",
      detailLabel: "将写入配置文件、停止当前流并重新初始化运行时",
      disabled: false,
      requiresSecondClick: false
    };
  }
  return {
    packageId,
    tone: "ready",
    buttonLabel: "恢复此复盘包",
    detailLabel: "需要再次点击确认；后端会先生成当前配置回滚包",
    disabled: false,
    requiresSecondClick: true
  };
}

function formatRuntimeExportDiffValue(value: unknown): string {
  if (value === null) {
    return "null";
  }
  if (value === undefined) {
    return "undefined";
  }
  if (typeof value === "string") {
    return value.length > 36 ? `${value.slice(0, 33)}...` : value;
  }
  if (typeof value === "number" || typeof value === "boolean") {
    return String(value);
  }
  const serialized = JSON.stringify(value);
  if (serialized === undefined) {
    return String(value);
  }
  return serialized.length > 36 ? `${serialized.slice(0, 33)}...` : serialized;
}

export interface DataPanelTrafficDisplay {
  label: string;
  note: string | null;
}

export function buildDataPanelTrafficDisplay(
  traffic: TrafficDemandSummary | null | undefined
): DataPanelTrafficDisplay {
  if (traffic === null || traffic === undefined) {
    return {
      label: "等待初始化",
      note: null
    };
  }
  return {
    label: dataPanelTrafficLabel(traffic),
    note: buildDataPanelTrafficNote(traffic)
  };
}

export interface DataPanelNetworkKpiSource {
  sourceLabel: string;
  modelNote: string;
  caveats: readonly string[];
}

export interface DataPanelNetworkFormulaInput {
  label: string;
  value: string;
}

export interface DataPanelNetworkKpiProvenanceItem {
  label: string;
  value: string;
  title: string;
}

export type DataPanelNetworkKpiCredibilityTone =
  | "match"
  | "different"
  | "pending"
  | "error";

export interface DataPanelNetworkKpiCredibilityDisplay {
  tone: DataPanelNetworkKpiCredibilityTone;
  statusLabel: string;
  summaryLabel: string;
  metaLabels: readonly string[];
  caveats: readonly string[];
}

export interface DataPanelNetworkKpiFormulaInspectorDisplay {
  tone: DataPanelNetworkKpiCredibilityTone;
  sourceLabel: string;
  statusLabel: string;
  summaryLabel: string;
  metaLabels: readonly string[];
  rows: readonly DataPanelNetworkKpiFormulaRow[];
}

export interface DataPanelNetworkKpiBenchmarkValidationDisplay {
  tone: DataPanelNetworkKpiCredibilityTone;
  statusLabel: string;
  summaryLabel: string;
  metaLabels: readonly string[];
  issueLabels: readonly string[];
  caveats: readonly string[];
}

export interface DataPanelNetworkKpiFormulaRow {
  metric: string;
  displayName: string;
  valueLabel: string;
  layerLabel: string;
  sourceLabel: string;
  formulaLabel: string;
  sourceFieldsLabel: string;
  formulaInputsLabel: string | null;
  formulaTraceLabel: string | null;
  zeroReasonLabel: string | null;
  tone: "observed" | "missing" | "invalid";
  title: string;
}

export interface DataPanelRouteProvenanceTrustDisplay {
  tone: DataPanelNetworkKpiCredibilityTone;
  sourceLabel: string;
  statusLabel: string;
  summaryLabel: string;
  metaLabels: readonly string[];
  caveats: readonly string[];
}

export interface DataPanelModelAssumptionsDisplay {
  sourceLabel: string;
  summaryLabel: string;
  boundaryLabel: string;
  fidelityLabel: string;
  rows: readonly DataPanelModelAssumptionRow[];
}

export interface DataPanelModelAssumptionRow {
  kind: "assumption" | "fidelity" | "kpi";
  label: string;
  detail: string;
  source: string;
}

export interface DataPanelModelTrustEvidenceWorkspaceInput {
  configurationExplanation?: DataPanelConfigurationExplanationDisplay | null;
  modelAssumptions?: DataPanelModelAssumptionsDisplay | null;
  networkKpiCredibility?: DataPanelNetworkKpiCredibilityDisplay | null;
  networkKpiBenchmarkValidation?: DataPanelNetworkKpiBenchmarkValidationDisplay | null;
  networkKpiFormulaInspector?: DataPanelNetworkKpiFormulaInspectorDisplay | null;
  routeProvenanceTrust?: DataPanelRouteProvenanceTrustDisplay | null;
  fidelitySummary?: FidelitySummary | null;
  reproducibilityManifest?: RuntimeReproducibilityManifestV1 | null;
  exportCatalog?: RuntimeExportCatalogV1 | null;
  exportReviewSummary?: RuntimeExportReviewSummaryV1 | null;
  exportDiagnosticsBundle?: RuntimeExportDiagnosticsBundleV1 | null;
  runtimeStatus?: RuntimeStatusPayload | null;
}

export interface DataPanelModelTrustEvidenceWorkspaceDisplay {
  tone: DataPanelNetworkKpiCredibilityTone;
  sourceLabel: string;
  statusLabel: string;
  summaryLabel: string;
  scoreLabel: string;
  metaLabels: readonly string[];
  rows: readonly DataPanelModelTrustEvidenceRow[];
  actionLabels: readonly string[];
}

export interface DataPanelModelTrustEvidenceRow {
  kind:
    | "configuration"
    | "fidelity"
    | "kpi"
    | "benchmark"
    | "formula"
    | "route"
    | "replay"
    | "runtime";
  label: string;
  statusLabel: string;
  detail: string;
  source: string;
  tone: DataPanelNetworkKpiCredibilityTone;
  title: string;
}

export interface DataPanelServiceLatencyDisplay {
  sourceLabel: string;
  modelLabel: string;
  taskCountLabel: string;
  completeCountLabel: string;
  totalLatencyLabel: string;
  items: readonly DataPanelNetworkFormulaInput[];
}

export interface DataPanelServiceLatencyRow {
  taskId: string;
  taskLabel: string;
  traceTitle: string;
  statusLabel: string;
  placementLabel: string;
  totalLatencyLabel: string;
  timeline: readonly DataPanelServiceLatencyTimelineItem[];
}

export interface DataPanelServiceLatencyTimelineItem {
  component: string;
  label: string;
  timeLabel: string;
  durationLabel: string;
  traceTitle: string;
}

export interface DataPanelServiceDetailRows {
  sourceLabel: string;
  summaryLabel: string;
  items: readonly DataPanelServiceDetailRow[];
}

export interface DataPanelServiceDetailRow {
  serviceId: string;
  taskLabel: string;
  stateLabel: string;
  placementLabel: string;
  networkLatencyLabel: string;
  computeLatencyLabel: string;
  totalLatencyLabel: string;
  traceTitle: string;
}

export interface DataPanelServiceLifecycleTraceDisplay {
  sourceLabel: string;
  summaryLabel: string;
  items: readonly DataPanelServiceLifecycleTraceRow[];
}

export interface DataPanelServiceLifecycleTraceRow {
  traceId: string;
  serviceId: string;
  taskId: string;
  inputFlowId: string;
  outputFlowId: string;
  inputRouteId: string;
  outputRouteId: string;
  computeNodeId: string;
  primaryRouteId: string;
  routeIds: readonly string[];
  flowIds: readonly string[];
  serviceLabel: string;
  terminalState: string;
  terminalStateReason: string;
  terminalStateLabel: string;
  computeNodeLabel: string;
  networkLatencyLabel: string;
  computeLatencyLabel: string;
  totalLatencyLabel: string;
  traceTitle: string;
  stages: readonly DataPanelServiceLifecycleTraceStageRow[];
}

export type DataPanelServiceTraceTerminalFilter =
  | "ALL"
  | "RUNNING"
  | "COMPLETE"
  | "INCOMPLETE";

export type DataPanelServiceTraceStageFilter =
  | "ALL"
  | "INPUT_NETWORK"
  | "COMPUTE_QUEUE"
  | "COMPUTE_EXECUTION"
  | "OUTPUT_NETWORK";

export type DataPanelServiceTraceTerminalReasonFilter =
  | "ALL"
  | "TOTAL_LATENCY_OBSERVED"
  | "OUTPUT_NETWORK_PENDING"
  | "COMPONENTS_OBSERVED_BUT_TOTAL_MISSING"
  | "NO_COMPONENT_OBSERVATIONS";

export interface DataPanelServiceTraceFilter {
  query?: string;
  terminalState?: DataPanelServiceTraceTerminalFilter | string;
  computeNodeId?: string;
  stageKind?: DataPanelServiceTraceStageFilter | string;
  terminalReason?: DataPanelServiceTraceTerminalReasonFilter | string;
}

export interface DataPanelUserServiceRequestFilter {
  query?: string;
  serviceClass?: string;
  terminalState?: string;
  networkWaiting?: string;
}

export interface DataPanelServiceLifecycleTraceStageRow {
  stageId: string;
  component: string;
  stageKind: string;
  stageStatus: string;
  label: string;
  statusLabel: string;
  durationLabel: string;
  traceTitle: string;
}

export interface DataPanelComputeTaskTimelineDisplay {
  sourceLabel: string;
  summaryLabel: string;
  queuedTaskLabel: string;
  totalQueueDelayLabel: string;
  totalExecutionDelayLabel: string;
  items: readonly DataPanelComputeTaskTimelineRow[];
}

export interface DataPanelComputeTaskTimelineRow {
  taskId: string;
  taskLabel: string;
  nodeLabel: string;
  queueExecutionLabel: string;
  traceTitle: string;
}

export interface DataPanelComputeNodeDetailRows {
  sourceLabel: string;
  summaryLabel: string;
  items: readonly DataPanelComputeNodeDetailRow[];
}

export interface DataPanelComputeNodeDetailRow {
  nodeId: string;
  statusLabel: string;
  loadLabel: string;
  fp32Label: string;
  acceleratorLabel: string;
  memoryStorageLabel: string;
  taskLabel: string;
  traceTitle: string;
}

export interface DataPanelBackendCursorDisplay {
  rangeLabel: string;
  statusLabel: string;
  previousCursor: number;
  nextCursor: number;
  canPrevious: boolean;
  canNext: boolean;
}

export interface DataPanelRouteConstraint {
  routeId: string;
  flowId: string;
  statusLabel: string;
  hopCount: number;
  latencyLabel: string;
  capacityLabel: string;
  demandLossLabel: string;
  bottleneckLabel: string;
  pathLabel: string;
}

export interface DataPanelRouteConstraintRows {
  sourceLabel: string;
  items: readonly DataPanelRouteConstraint[];
}

export interface DataPanelRouteExplanationRow {
  routeId: string;
  flowId: string;
  available: boolean;
  availabilityLabel: string;
  businessType: string;
  businessLabel: string;
  nextHopLabel: string;
  capacityDemandLabel: string;
  pressureLabel: string;
  bottleneckComponent: string;
  bottleneckLabel: string;
  explanationLabel: string;
  pathLabel: string;
}

export type DataPanelRouteExplanationAvailabilityFilter =
  | "ALL"
  | "AVAILABLE"
  | "BLOCKED";

export interface DataPanelRouteExplanationFilter {
  query?: string;
  availability?: DataPanelRouteExplanationAvailabilityFilter;
  businessType?: string;
  bottleneckComponent?: string;
}

export interface DataPanelRouteExplanationRows {
  sourceLabel: string;
  items: readonly DataPanelRouteExplanationRow[];
}

type SnapshotRoute = WorldSnapshot["routes"][number];
type SnapshotLink = WorldSnapshot["links"][number];

export function buildDataPanelNetworkKpiSource(
  snapshot: WorldSnapshot,
  backendMetrics: RuntimeMetricsSummary | null | undefined = undefined,
  backendKpiTimeSeries: RuntimeKpiTimeSeriesV1 | null | undefined = undefined,
  networkProvenance: RuntimeNetworkQualityProvenanceV1 | null | undefined = undefined
): DataPanelNetworkKpiSource {
  const backendNote = formatNetworkQualityProxyNote(backendMetrics, networkProvenance);
  if ((backendKpiTimeSeries?.samples ?? []).length > 0) {
    return {
      sourceLabel: "后端实时 KPI 序列",
      modelNote: backendNote,
      caveats: buildDataPanelNetworkKpiCaveats(
        backendMetrics,
        backendKpiTimeSeries,
        networkProvenance
      )
    };
  }
  if ((snapshot.metrics_summary.network.kpiSeries ?? []).length > 0) {
    return {
      sourceLabel: "状态快照 KPI 序列",
      modelNote: backendNote,
      caveats: buildDataPanelNetworkKpiCaveats(
        backendMetrics,
        undefined,
        networkProvenance
      )
    };
  }
  if (hasBackendNetworkQualityMetrics(backendMetrics)) {
    return {
      sourceLabel: "后端指标摘要",
      modelNote: backendNote,
      caveats: buildDataPanelNetworkKpiCaveats(
        backendMetrics,
        undefined,
        networkProvenance
      )
    };
  }
  return {
    sourceLabel: "前端快照估算",
    modelNote: "未收到后端网络质量指标时，根据快照链路与路由做显示估算。",
    caveats: []
  };
}

export function buildDataPanelNetworkKpiCaveats(
  metrics: RuntimeMetricsSummary | null | undefined,
  backendKpiTimeSeries: RuntimeKpiTimeSeriesV1 | null | undefined = undefined,
  networkProvenance: RuntimeNetworkQualityProvenanceV1 | null | undefined = undefined
): readonly string[] {
  const latestSample = latestRuntimeKpiSample(backendKpiTimeSeries);
  if (
    (metrics === null || metrics === undefined) &&
    (networkProvenance === null || networkProvenance === undefined) &&
    latestSample === null
  ) {
    return buildDataPanelKpiTailCaveats(backendKpiTimeSeries);
  }
  const caveats: string[] = [];
  const metricModel =
    networkProvenance?.metric_model ||
    metricString(metrics, "network_quality_metric_model");
  if (metricModel === "FLOW_LEVEL_PROXY") {
    caveats.push("指标模型：后端流级代理");
  }
  const lossReason =
    networkProvenance?.zero_reasons.loss?.label ||
    metricString(metrics, "network_quality_loss_zero_reason_label");
  if (lossReason && lossReason !== POSITIVE_PROXY_REASON_LABEL) {
    caveats.push(`丢包率：${lossReason}`);
  }
  const jitterReason =
    networkProvenance?.zero_reasons.delay_variation?.label ||
    metricString(metrics, "network_quality_delay_variation_zero_reason_label");
  if (jitterReason && jitterReason !== POSITIVE_PROXY_REASON_LABEL) {
    caveats.push(`抖动：${jitterReason}`);
  }
  const recentLossReason = latestSample?.network_recent_loss_zero_reason_label;
  if (recentLossReason && recentLossReason !== POSITIVE_PROXY_REASON_LABEL) {
    caveats.push(`最近窗口丢包率：${recentLossReason}`);
  }
  const recentJitterReason =
    latestSample?.network_recent_delay_variation_zero_reason_label;
  if (recentJitterReason && recentJitterReason !== POSITIVE_PROXY_REASON_LABEL) {
    caveats.push(`最近窗口抖动：${recentJitterReason}`);
  }
  caveats.push(...buildDataPanelKpiTailCaveats(backendKpiTimeSeries));
  return caveats;
}

export function buildDataPanelNetworkKpiProvenanceItems(
  metrics: RuntimeMetricsSummary | null | undefined,
  backendKpiTimeSeries: RuntimeKpiTimeSeriesV1 | null | undefined = undefined,
  networkProvenance: RuntimeNetworkQualityProvenanceV1 | null | undefined = undefined
): readonly DataPanelNetworkKpiProvenanceItem[] {
  const items: DataPanelNetworkKpiProvenanceItem[] = [];
  const latestSample = latestRuntimeKpiSample(backendKpiTimeSeries);
  const recentWindowSeconds = latestSample?.network_recent_window_s;
  const hasRecentWindow =
    typeof recentWindowSeconds === "number" && Number.isFinite(recentWindowSeconds);
  items.push({
    label: "曲线窗口",
    value: hasRecentWindow
      ? `最近 ${formatDurationCompact(Math.max(0, recentWindowSeconds))} 完成流`
      : "累计有效指标",
    title: hasRecentWindow
      ? "图表优先使用后端最近窗口内完成流的吞吐、时延、丢包代理和抖动代理。"
      : "图表使用后端累计有效指标或快照估算值。"
  });
  if (latestSample !== null && hasRecentWindow) {
    const recentFlowCount = latestSample.network_recent_flow_count;
    if (typeof recentFlowCount === "number" && Number.isFinite(recentFlowCount)) {
      items.push({
        label: "窗口样本",
        value: `${formatPreciseMetricValue(Math.max(0, recentFlowCount))} 条完成流`,
        title: "最近窗口 KPI 只统计该时间窗内已经完成的流；窗口内无完成流时曲线可能保持 0。"
      });
    }
    if (
      latestSample.network_recent_loss_zero_reason_label &&
      latestSample.network_recent_loss_zero_reason_label !== POSITIVE_PROXY_REASON_LABEL
    ) {
      items.push({
        label: "窗口丢包",
        value: latestSample.network_recent_loss_zero_reason_label,
        title: "该说明来自后端最近窗口 KPI 样本，不代表包级丢包。"
      });
    }
    if (
      latestSample.network_recent_delay_variation_zero_reason_label &&
      latestSample.network_recent_delay_variation_zero_reason_label !==
        POSITIVE_PROXY_REASON_LABEL
    ) {
      items.push({
        label: "窗口抖动",
        value: latestSample.network_recent_delay_variation_zero_reason_label,
        title: "该说明来自后端最近窗口 KPI 样本，不代表包级抖动。"
      });
    }
  }

  const sourceItems = (
    [
      [
        "吞吐",
        networkProvenance?.sources.throughput?.label ||
          metricString(metrics, "network_quality_throughput_source_label")
      ],
      [
        "时延",
        networkProvenance?.sources.latency?.label ||
          metricString(metrics, "network_quality_latency_source_label")
      ],
      [
        "丢包",
        networkProvenance?.sources.loss?.label ||
          metricString(metrics, "network_quality_loss_source_label")
      ],
      [
        "抖动",
        networkProvenance?.sources.delay_variation?.label ||
          metricString(metrics, "network_quality_delay_variation_source_label")
      ]
    ] as const
  )
    .filter(([, value]) => typeof value === "string" && value.trim().length > 0)
    .map(([label, value]) => ({
      label,
      value: value as string,
      title: `${label}指标来源由后端运行态指标摘要声明。`
    }));
  items.push(...sourceItems);

  const metricModel =
    networkProvenance?.metric_model || metricString(metrics, "network_quality_metric_model");
  if (metricModel !== undefined || networkProvenance?.packet_level_simulation === false) {
    items.push({
      label: "语义",
      value:
        networkProvenance?.packet_level_simulation === false || metricModel === "FLOW_LEVEL_PROXY"
          ? "流级代理 / 非包级"
          : metricModel ?? "后端声明",
      title: "该说明来自后端网络质量 provenance，不代表包级仿真。"
    });
  }
  return items;
}

export function buildDataPanelNetworkKpiCredibilityDisplay(
  credibility: RuntimeNetworkKpiCredibilityV1 | null | undefined
): DataPanelNetworkKpiCredibilityDisplay | null {
  if (credibility === null || credibility === undefined) {
    return null;
  }
  const kpiCount = Math.max(0, credibility.kpi_count);
  const observedKpiCount = clampCount(credibility.observed_kpi_count, kpiCount);
  const sourceFieldCount = Math.max(0, credibility.source_field_count);
  const observedSourceFieldCount = clampCount(
    credibility.observed_source_field_count,
    sourceFieldCount
  );
  const zeroValueKpiCount = Math.max(0, credibility.zero_value_kpi_count);
  const zeroValueExplainedCount = clampCount(
    credibility.zero_value_explained_count,
    zeroValueKpiCount
  );
  const packetLevelMetricCount = Math.max(0, credibility.packet_level_metric_count);
  const flowLevelProxyMetricCount = Math.max(0, credibility.flow_level_proxy_metric_count);
  return {
    tone: networkKpiCredibilityTone(credibility.credibility_status),
    statusLabel: networkKpiCredibilityStatusLabel(credibility.credibility_status),
    summaryLabel: `KPI ${formatCount(observedKpiCount)}/${formatCount(
      kpiCount
    )} 有运行值；来源字段 ${formatCount(observedSourceFieldCount)}/${formatCount(
      sourceFieldCount
    )} 可观测`,
    metaLabels: [
      `模型 ${networkKpiMetricModelLabel(credibility.metric_model)}`,
      `流级代理 ${formatCount(flowLevelProxyMetricCount)}`,
      packetLevelMetricCount === 0
        ? "无包级指标"
        : `包级指标 ${formatCount(packetLevelMetricCount)}`,
      `零值解释 ${formatCount(zeroValueExplainedCount)}/${formatCount(
        zeroValueKpiCount
      )}`,
      `缺失 KPI ${formatCount(Math.max(0, credibility.missing_kpi_count))}`
    ],
    caveats: [
      ...credibility.caveats.slice(0, 3),
      ...networkKpiCredibilityIssueLabels(credibility)
    ]
  };
}

export function buildDataPanelNetworkKpiBenchmarkValidationDisplay(
  validation: RuntimeNetworkKpiBenchmarkValidationV1 | null | undefined
): DataPanelNetworkKpiBenchmarkValidationDisplay | null {
  if (validation === null || validation === undefined) {
    return null;
  }
  const checkCount = Math.max(0, validation.check_count);
  const passedCount = clampCount(validation.passed_check_count, checkCount);
  const warningCount = Math.max(0, validation.warning_check_count);
  const failedCount = Math.max(0, validation.failed_check_count);
  const missingCount = Math.max(0, validation.missing_check_count);
  const issueLabels = validation.checks
    .filter((check) => check.status !== "PASS")
    .slice(0, 4)
    .map(
      (check) =>
        `${check.status} ${check.metric}: ${formatNetworkKpiValue(
          check.current_value
        )} / ${check.expectation}`
    );
  return {
    tone: networkKpiBenchmarkValidationTone(validation.validation_status),
    statusLabel: networkKpiBenchmarkValidationStatusLabel(
      validation.validation_status
    ),
    summaryLabel: `检查 ${formatCount(passedCount)}/${formatCount(
      checkCount
    )} 通过；WARN ${formatCount(warningCount)} / FAIL ${formatCount(
      failedCount
    )} / 缺数据 ${formatCount(missingCount)}`,
    metaLabels: [
      `profile ${validation.benchmark_profile}`,
      `模型 ${networkKpiMetricModelLabel(validation.metric_model)}`,
      validation.packet_level_simulation ? "含包级仿真" : "无包级仿真",
      `provenance ${shortRuntimeHash(validation.provenance_id)}`
    ],
    issueLabels,
    caveats: validation.caveats.slice(0, 3)
  };
}

export function buildDataPanelNetworkKpiFormulaInspector(
  provenance: RuntimeNetworkKpiProvenanceV2 | null | undefined,
  credibility: RuntimeNetworkKpiCredibilityV1 | null | undefined,
  limit = 6
): DataPanelNetworkKpiFormulaInspectorDisplay | null {
  if (provenance === null || provenance === undefined) {
    return null;
  }
  const displayLimit = Math.max(0, limit);
  const orderedKpis = [...provenance.kpis].sort((left, right) =>
    left.metric.localeCompare(right.metric)
  );
  const rows = orderedKpis.slice(0, displayLimit).map((kpi) => {
    const observedFields = kpi.source_fields.filter(
      (field) => field.value_source === "METRICS_SUMMARY"
    );
    const sourceFieldsLabel = `来源字段 ${formatCount(
      observedFields.length
    )}/${formatCount(kpi.source_fields.length)}：${kpi.source_fields
      .slice(0, 4)
      .map((field) => `${field.field}=${formatNetworkKpiValue(field.current_value)}`)
      .join(" / ")}`;
    const formulaInputsLabel = formatNetworkKpiFormulaInputsLabel(kpi);
    const formulaTraceLabel = formatNetworkKpiFormulaTraceLabel(kpi);
    const zeroReasonLabel =
      kpi.zero_reason && kpi.zero_reason.label
        ? `零值原因：${kpi.zero_reason.label}`
        : kpi.zero_value_semantics
          ? `零值语义：${kpi.zero_value_semantics}`
          : null;
    const tone: DataPanelNetworkKpiFormulaRow["tone"] = kpi.packet_level_metric
      ? "invalid"
      : kpi.status === "OBSERVED"
        ? "observed"
        : "missing";
    return {
      metric: kpi.metric,
      displayName: `${kpi.display_name} / ${kpi.metric}`,
      valueLabel: `${formatNetworkKpiValue(kpi.current_value)} ${kpi.unit}`.trim(),
      layerLabel: `${kpi.layer} / ${kpi.status}`,
      sourceLabel: `${kpi.observed_source.label || kpi.observed_source.source}`,
      formulaLabel: kpi.formula_summary,
      sourceFieldsLabel,
      formulaInputsLabel,
      formulaTraceLabel,
      zeroReasonLabel,
      tone,
      title: `${kpi.metric}: ${kpi.interpretation}`
    };
  });
  const credibilityStatus = credibility?.credibility_status ?? "";
  const tone =
    credibility === null || credibility === undefined
      ? "pending"
      : networkKpiCredibilityTone(credibilityStatus);
  const hiddenCount = Math.max(0, orderedKpis.length - rows.length);
  return {
    tone,
    sourceLabel: `${provenance.provenance_id} / ${provenance.network_model_contract_id}`,
    statusLabel:
      credibility === null || credibility === undefined
        ? "等待可信度摘要"
        : networkKpiCredibilityStatusLabel(credibility.credibility_status),
    summaryLabel: `${networkKpiMetricModelLabel(
      provenance.metric_model
    )} / 公式 ${formatCount(rows.length)}/${formatCount(provenance.kpi_count)}${
      hiddenCount > 0 ? ` / 隐藏 ${formatCount(hiddenCount)}` : ""
    }`,
    metaLabels: [
      `contract ${provenance.network_model_contract_version}`,
      provenance.packet_level_simulation ? "含包级仿真" : "无包级仿真",
      `KPI ${formatCount(provenance.kpi_count)}`,
      `展示 ${formatCount(rows.length)}`
    ],
    rows
  };
}

function formatNetworkKpiFormulaInputsLabel(
  kpi: RuntimeNetworkKpiProvenanceV2["kpis"][number]
): string | null {
  const inputs = kpi.formula_inputs ?? [];
  if (inputs.length === 0) {
    return null;
  }
  const selected = inputs.filter((input) => input.selected_for_current_value);
  const observed = inputs.filter((input) => input.observed);
  const visible = (selected.length > 0 ? selected : inputs).slice(0, 4);
  const inputText = visible
    .map((input) => {
      const marker = input.selected_for_current_value ? "*" : "";
      return `${marker}${input.field}=${formatNetworkKpiValue(input.current_value)}`;
    })
    .join(" / ");
  return `输入审计 ${formatCount(selected.length)} 选中 / ${formatCount(
    observed.length
  )}/${formatCount(inputs.length)} 可观测：${inputText}`;
}

function formatNetworkKpiFormulaTraceLabel(
  kpi: RuntimeNetworkKpiProvenanceV2["kpis"][number]
): string | null {
  const trace = kpi.formula_trace;
  if (trace === undefined || trace === null) {
    return null;
  }
  const sourceLabel = trace.observed_source_label || trace.observed_source || "未声明来源";
  return `选择 ${sourceLabel}；选中可观测 ${formatCount(
    Math.max(0, trace.selected_observed_input_count)
  )}/${formatCount(Math.max(0, trace.selected_input_count))}；缺失输入 ${formatCount(
    Math.max(0, trace.missing_input_count)
  )}；${trace.selection_policy}`;
}

export function buildDataPanelRouteProvenanceTrustDisplay(
  trust: RuntimeRouteProvenanceTrustSummaryV1 | null | undefined
): DataPanelRouteProvenanceTrustDisplay | null {
  if (trust === null || trust === undefined) {
    return null;
  }
  const routeCount = Math.max(0, trust.route_count);
  const explainedRouteCount = clampCount(trust.explained_route_count, routeCount);
  const coreFieldCount = Math.max(0, trust.core_field_count);
  const contextFieldCount = Math.max(0, trust.context_field_count);
  const observedCoreFieldCount = clampCount(
    trust.observed_core_field_count,
    coreFieldCount
  );
  const observedContextFieldCount = clampCount(
    trust.observed_context_field_count,
    contextFieldCount
  );
  const hiddenRouteCount = Math.max(0, trust.hidden_route_count);
  return {
    tone: routeProvenanceTrustTone(trust.trust_status),
    sourceLabel: `${trust.trust_id} / ${trust.source}`,
    statusLabel: routeProvenanceTrustStatusLabel(trust.trust_status),
    summaryLabel: `路由 ${formatCount(explainedRouteCount)}/${formatCount(
      routeCount
    )} 已解释；核心字段 ${formatCount(observedCoreFieldCount)}/${formatCount(
      coreFieldCount
    )}；上下文 ${formatCount(observedContextFieldCount)}/${formatCount(
      contextFieldCount
    )}`,
    metaLabels: [
      `模型 ${routeProvenanceTrustModelLabel(trust.route_model)}`,
      trust.packet_level_simulation ? "含包级仿真" : "无包级仿真",
      trust.all_pairs_computation ? "含全对链路计算" : "无全对链路计算",
      `可用 ${formatCount(trust.available_route_count)} / 阻塞 ${formatCount(
        trust.blocked_route_count
      )}`,
      `瓶颈 ${trust.bottleneck_components.length > 0 ? trust.bottleneck_components.join(", ") : "NONE"}`,
      hiddenRouteCount > 0
        ? `隐藏 ${formatCount(hiddenRouteCount)} 路由`
        : `窗口 ${formatCount(trust.window_item_count)} 路由`
    ],
    caveats: [
      ...trust.caveats.slice(0, 3),
      ...routeProvenanceTrustIssueLabels(trust)
    ]
  };
}

export function buildDataPanelModelAssumptionsDisplay(
  modelAssumptions: readonly string[] | null | undefined,
  fidelitySummary: FidelitySummary | null | undefined,
  networkKpiCredibility: DataPanelNetworkKpiCredibilityDisplay | null | undefined,
  configurationExplanation: DataPanelConfigurationExplanationDisplay | null | undefined
): DataPanelModelAssumptionsDisplay | null {
  const assumptions = (modelAssumptions ?? [])
    .map((assumption) => assumption.trim())
    .filter((assumption) => assumption.length > 0);
  const fidelityWarnings = fidelitySummary?.fidelity_warnings ?? [];
  const rows: DataPanelModelAssumptionRow[] = [
    ...assumptions.map((assumption, index) => ({
      kind: "assumption" as const,
      label: `模型假设 ${formatCount(index + 1)}`,
      detail: assumption,
      source: "backend_summary.model_assumptions"
    }))
  ];
  if (fidelitySummary !== null && fidelitySummary !== undefined) {
    rows.push({
      kind: "fidelity",
      label: "规模保真策略",
      detail: [
        `orbit=${fidelitySummary.orbit_update_mode}`,
        `metrics=${fidelitySummary.metrics_mode}`,
        `space=${fidelitySummary.space_link_mode}`,
        fidelitySummary.scale_limit_reason
      ]
        .filter((value) => value !== "")
        .join(" / "),
      source: "fidelity_summary"
    });
    rows.push(
      ...fidelityWarnings.map((warning, index) => ({
        kind: "fidelity" as const,
        label: `规模提示 ${formatCount(index + 1)}`,
        detail: warning,
        source: "fidelity_summary.fidelity_warnings"
      }))
    );
  }
  if (networkKpiCredibility !== null && networkKpiCredibility !== undefined) {
    rows.push({
      kind: "kpi",
      label: "KPI可信度",
      detail: `${networkKpiCredibility.statusLabel} / ${networkKpiCredibility.summaryLabel}`,
      source: "network_kpi_credibility_v1"
    });
    rows.push(
      ...networkKpiCredibility.caveats.map((caveat, index) => ({
        kind: "kpi" as const,
        label: `KPI边界 ${formatCount(index + 1)}`,
        detail: caveat,
        source: "network_kpi_credibility_v1.caveats"
      }))
    );
  }
  if (
    rows.length === 0 &&
    (configurationExplanation === null || configurationExplanation === undefined)
  ) {
    return null;
  }
  const fidelityCount =
    fidelitySummary === null || fidelitySummary === undefined
      ? 0
      : 1 + fidelityWarnings.length;
  const kpiCount =
    networkKpiCredibility === null || networkKpiCredibility === undefined
      ? 0
      : 1 + networkKpiCredibility.caveats.length;
  return {
    sourceLabel: "backend_summary.model_assumptions + runtime credibility",
    summaryLabel: `${formatCount(assumptions.length)} 条假设 / ${formatCount(
      fidelityCount
    )} 条规模边界 / ${formatCount(kpiCount)} 条KPI边界`,
    boundaryLabel: configurationExplanation?.boundaryLabel ?? "等待后端配置边界",
    fidelityLabel:
      fidelitySummary !== null && fidelitySummary !== undefined
        ? `${fidelitySummary.current_scale_mode} / ${formatCount(
            fidelitySummary.satellite_count
          )} 星 / ${formatCount(fidelitySummary.user_count)} 用户`
        : "等待后端保真策略",
    rows
  };
}

export function buildDataPanelModelTrustEvidenceWorkspace(
  input: DataPanelModelTrustEvidenceWorkspaceInput
): DataPanelModelTrustEvidenceWorkspaceDisplay | null {
  const runtimeStatus = input.runtimeStatus ?? null;
  if (
    (input.configurationExplanation === null ||
      input.configurationExplanation === undefined) &&
    (input.modelAssumptions === null || input.modelAssumptions === undefined) &&
    (input.networkKpiCredibility === null || input.networkKpiCredibility === undefined) &&
    (input.networkKpiBenchmarkValidation === null ||
      input.networkKpiBenchmarkValidation === undefined) &&
    (input.networkKpiFormulaInspector === null ||
      input.networkKpiFormulaInspector === undefined) &&
    (input.routeProvenanceTrust === null || input.routeProvenanceTrust === undefined) &&
    (input.fidelitySummary === null || input.fidelitySummary === undefined) &&
    (input.reproducibilityManifest === null ||
      input.reproducibilityManifest === undefined) &&
    (input.exportCatalog === null || input.exportCatalog === undefined) &&
    (input.exportReviewSummary === null || input.exportReviewSummary === undefined) &&
    (input.exportDiagnosticsBundle === null ||
      input.exportDiagnosticsBundle === undefined) &&
    runtimeStatus === null
  ) {
    return null;
  }

  const rows: DataPanelModelTrustEvidenceRow[] = [
    buildModelTrustConfigurationRow(input.configurationExplanation),
    buildModelTrustFidelityRow(input.fidelitySummary, input.modelAssumptions),
    buildModelTrustKpiRow(input.networkKpiCredibility),
    buildModelTrustKpiBenchmarkRow(input.networkKpiBenchmarkValidation),
    buildModelTrustFormulaRow(input.networkKpiFormulaInspector),
    buildModelTrustRouteProvenanceRow(input.routeProvenanceTrust),
    buildModelTrustReplayRow(
      input.reproducibilityManifest,
      input.exportCatalog,
      input.exportReviewSummary,
      input.exportDiagnosticsBundle
    )
  ];
  if (runtimeStatus !== null) {
    rows.push(buildModelTrustRuntimeRow(runtimeStatus));
  }

  const readyCount = rows.filter((row) => row.tone === "match" || row.tone === "different")
    .length;
  const warningCount = rows.filter((row) => row.tone === "different").length;
  const errorCount = rows.filter((row) => row.tone === "error").length;
  const pendingCount = rows.filter((row) => row.tone === "pending").length;
  const tone =
    errorCount > 0
      ? "error"
      : warningCount > 0
        ? "different"
        : pendingCount > 0
          ? "pending"
          : "match";
  const statusLabel =
    tone === "match"
      ? "证据链完整"
      : tone === "different"
        ? "证据链有降级"
        : tone === "pending"
          ? "证据链待补齐"
          : "证据链存在错误";
  const actionLabels = buildModelTrustActionLabels(rows, input.exportDiagnosticsBundle);
  return {
    tone,
    sourceLabel: "runtime status + backend summary + export diagnostics",
    statusLabel,
    summaryLabel: `${formatCount(rows.length)} 类证据 / ${formatCount(
      readyCount
    )} 类可用 / ${formatCount(pendingCount)} 类待补齐`,
    scoreLabel: `可用 ${formatCount(readyCount)}/${formatCount(
      rows.length
    )} / 警告 ${formatCount(warningCount)} / 错误 ${formatCount(errorCount)}`,
    metaLabels: [
      input.configurationExplanation ? "配置语义已声明" : "配置语义待声明",
      input.networkKpiBenchmarkValidation ? "KPI基准已验证" : "KPI基准待验证",
      input.networkKpiFormulaInspector ? "KPI公式可追踪" : "KPI公式待补齐",
      input.routeProvenanceTrust ? "路由证据可追踪" : "路由证据待补齐",
      input.reproducibilityManifest ? "manifest已生成" : "manifest待生成",
      input.exportDiagnosticsBundle ? "诊断包已加载" : "诊断包待选择"
    ],
    rows,
    actionLabels
  };
}

function buildModelTrustConfigurationRow(
  configurationExplanation: DataPanelConfigurationExplanationDisplay | null | undefined
): DataPanelModelTrustEvidenceRow {
  if (configurationExplanation === null || configurationExplanation === undefined) {
    return {
      kind: "configuration",
      label: "配置语义",
      statusLabel: "等待后端解释",
      detail: "未收到 configuration_explanation_v2，界面只能展示运行值，不能完整解释配置边界。",
      source: "backend_summary.configuration_explanation_v2",
      tone: "pending",
      title: "配置语义证据必须由后端生成，前端不本地推断业务边界。"
    };
  }
  return {
    kind: "configuration",
    label: "配置语义",
    statusLabel: "已声明",
    detail: `${configurationExplanation.summaryLabel} / ${configurationExplanation.boundaryLabel}`,
    source: configurationExplanation.sourceLabel,
    tone: "match",
    title: configurationExplanation.determinismLabel
  };
}

function buildModelTrustFidelityRow(
  fidelitySummary: FidelitySummary | null | undefined,
  modelAssumptions: DataPanelModelAssumptionsDisplay | null | undefined
): DataPanelModelTrustEvidenceRow {
  if (fidelitySummary === null || fidelitySummary === undefined) {
    return {
      kind: "fidelity",
      label: "保真边界",
      statusLabel: "等待规模策略",
      detail: modelAssumptions?.boundaryLabel ?? "未收到 fidelity_summary。",
      source: "fidelity_summary",
      tone: "pending",
      title: "大规模场景的轨道、指标和星间链路保真策略需要后端显式声明。"
    };
  }
  const warningCount = fidelitySummary.fidelity_warnings.length;
  return {
    kind: "fidelity",
    label: "保真边界",
    statusLabel:
      warningCount > 0
        ? `降级 ${formatCount(warningCount)} 项`
        : fidelitySummary.current_scale_mode,
    detail: [
      `orbit=${fidelitySummary.orbit_update_mode}`,
      `metrics=${fidelitySummary.metrics_mode}`,
      `space=${fidelitySummary.space_link_mode}`,
      fidelitySummary.scale_limit_reason
    ]
      .filter((value) => value.length > 0)
      .join(" / "),
    source: "fidelity_summary",
    tone: warningCount > 0 ? "different" : "match",
    title: modelAssumptions?.fidelityLabel ?? fidelitySummary.current_scale_mode
  };
}

function buildModelTrustKpiRow(
  networkKpiCredibility: DataPanelNetworkKpiCredibilityDisplay | null | undefined
): DataPanelModelTrustEvidenceRow {
  if (networkKpiCredibility === null || networkKpiCredibility === undefined) {
    return {
      kind: "kpi",
      label: "KPI可信度",
      statusLabel: "等待可信度摘要",
      detail: "未收到 network_kpi_credibility_v1。",
      source: "network_kpi_credibility_v1",
      tone: "pending",
      title: "KPI可信度摘要必须来自后端 provenance 覆盖率。"
    };
  }
  return {
    kind: "kpi",
    label: "KPI可信度",
    statusLabel: networkKpiCredibility.statusLabel,
    detail: networkKpiCredibility.summaryLabel,
    source: "network_kpi_credibility_v1",
    tone: networkKpiCredibility.tone,
    title: networkKpiCredibility.caveats.join(" / ") || networkKpiCredibility.summaryLabel
  };
}

function buildModelTrustKpiBenchmarkRow(
  validation: DataPanelNetworkKpiBenchmarkValidationDisplay | null | undefined
): DataPanelModelTrustEvidenceRow {
  if (validation === null || validation === undefined) {
    return {
      kind: "benchmark",
      label: "KPI基准验证",
      statusLabel: "等待基准验证",
      detail: "未收到 network_kpi_benchmark_validation_v1。",
      source: "network_kpi_benchmark_validation_v1",
      tone: "pending",
      title: "KPI基准验证必须由后端根据 metrics_summary 和 KPI provenance 生成。"
    };
  }
  return {
    kind: "benchmark",
    label: "KPI基准验证",
    statusLabel: validation.statusLabel,
    detail: validation.summaryLabel,
    source: "network_kpi_benchmark_validation_v1",
    tone: validation.tone,
    title: [...validation.issueLabels, ...validation.caveats].join(" / ")
  };
}

function buildModelTrustFormulaRow(
  networkKpiFormulaInspector:
    | DataPanelNetworkKpiFormulaInspectorDisplay
    | null
    | undefined
): DataPanelModelTrustEvidenceRow {
  if (networkKpiFormulaInspector === null || networkKpiFormulaInspector === undefined) {
    return {
      kind: "formula",
      label: "KPI公式来源",
      statusLabel: "等待公式证据",
      detail: "未收到 network_kpi_provenance_v2.kpis。",
      source: "network_kpi_provenance_v2",
      tone: "pending",
      title: "公式、运行值和来源字段应由后端 KPI provenance 合同声明。"
    };
  }
  return {
    kind: "formula",
    label: "KPI公式来源",
    statusLabel: networkKpiFormulaInspector.statusLabel,
    detail: networkKpiFormulaInspector.summaryLabel,
    source: networkKpiFormulaInspector.sourceLabel,
    tone: networkKpiFormulaInspector.tone,
    title: networkKpiFormulaInspector.rows.map((row) => row.title).join(" / ")
  };
}

function buildModelTrustRouteProvenanceRow(
  routeProvenanceTrust: DataPanelRouteProvenanceTrustDisplay | null | undefined
): DataPanelModelTrustEvidenceRow {
  if (routeProvenanceTrust === null || routeProvenanceTrust === undefined) {
    return {
      kind: "route",
      label: "路由解释可信度",
      statusLabel: "等待路由证据",
      detail: "未收到 route_provenance_trust_summary_v1。",
      source: "route_provenance_trust_summary_v1",
      tone: "pending",
      title: "路由解释可信摘要必须来自后端 route_explanation_summary_v1。"
    };
  }
  return {
    kind: "route",
    label: "路由解释可信度",
    statusLabel: routeProvenanceTrust.statusLabel,
    detail: routeProvenanceTrust.summaryLabel,
    source: routeProvenanceTrust.sourceLabel,
    tone: routeProvenanceTrust.tone,
    title: routeProvenanceTrust.caveats.join(" / ") || routeProvenanceTrust.summaryLabel
  };
}

function buildModelTrustReplayRow(
  reproducibilityManifest: RuntimeReproducibilityManifestV1 | null | undefined,
  exportCatalog: RuntimeExportCatalogV1 | null | undefined,
  exportReviewSummary: RuntimeExportReviewSummaryV1 | null | undefined,
  exportDiagnosticsBundle: RuntimeExportDiagnosticsBundleV1 | null | undefined
): DataPanelModelTrustEvidenceRow {
  if (exportDiagnosticsBundle !== null && exportDiagnosticsBundle !== undefined) {
    const errorCount = exportDiagnosticsBundle.findings.filter(
      (finding) => finding.severity === "ERROR"
    ).length;
    const warnCount = exportDiagnosticsBundle.findings.filter(
      (finding) => finding.severity === "WARN"
    ).length;
    const missingRequired =
      exportDiagnosticsBundle.artifact_health.missing_required_filenames.length;
    const tone =
      errorCount > 0
        ? "error"
        : warnCount > 0 || missingRequired > 0
          ? "different"
          : "match";
    return {
      kind: "replay",
      label: "复盘证据",
      statusLabel: exportDiagnosticsBundle.package.review_status,
      detail: `${exportDiagnosticsBundle.package.package_id} / findings ${formatCount(
        exportDiagnosticsBundle.finding_count
      )} / 必需缺失 ${formatCount(missingRequired)} / ${shortRuntimeHash(
        exportDiagnosticsBundle.diagnostics_hash
      )}`,
      source: "runtime_export_diagnostics_bundle_v1",
      tone,
      title: exportDiagnosticsBundle.recommended_next_actions.join(" / ")
    };
  }
  if (exportReviewSummary !== null && exportReviewSummary !== undefined) {
    const missingRequired = exportReviewSummary.artifacts.missing_required_filenames.length;
    const tone =
      exportReviewSummary.review_status === "REVIEW_READY" && missingRequired === 0
        ? "match"
        : "different";
    return {
      kind: "replay",
      label: "复盘证据",
      statusLabel: exportReviewSummary.review_status,
      detail: `${exportReviewSummary.package_id} / artifacts ${formatCount(
        exportReviewSummary.artifacts.artifact_count
      )} / 必需缺失 ${formatCount(missingRequired)} / ${shortRuntimeHash(
        exportReviewSummary.summary_hash
      )}`,
      source: "runtime_export_review_summary_v1",
      tone,
      title: exportReviewSummary.review_notes.join(" / ")
    };
  }
  if (reproducibilityManifest !== null && reproducibilityManifest !== undefined) {
    const artifactCount =
      typeof reproducibilityManifest.artifact_count === "number"
        ? reproducibilityManifest.artifact_count
        : reproducibilityManifest.artifacts.length;
    return {
      kind: "replay",
      label: "复盘证据",
      statusLabel: `manifest ${shortRuntimeHash(reproducibilityManifest.manifest_hash)}`,
      detail: `${reproducibilityManifest.artifact_policy} / artifacts ${formatCount(
        artifactCount
      )} / seed ${String(reproducibilityManifest.seed ?? "-")}`,
      source: "reproducibility_manifest_v1",
      tone: "match",
      title: reproducibilityManifest.notes?.join(" / ") ?? reproducibilityManifest.manifest_id
    };
  }
  if (exportCatalog?.latest_export) {
    const latest = exportCatalog.latest_export;
    return {
      kind: "replay",
      label: "复盘证据",
      statusLabel: "已有导出记录",
      detail: `${latest.package_id} / files ${formatCount(
        latest.file_count
      )} / ${shortRuntimeHash(latest.archive_sha256 || latest.manifest_hash)}`,
      source: "runtime_export_catalog_v1.latest_export",
      tone: "different",
      title: "已存在导出记录，但当前未加载 manifest 或 diagnostics 证据。"
    };
  }
  return {
    kind: "replay",
    label: "复盘证据",
    statusLabel: "等待结果包",
    detail: "尚未选择或生成复盘包，无法证明结果可复现。",
    source: "runtime export package",
    tone: "pending",
    title: "完成仿真后应导出 events、metrics、summary、manifest 和 diagnostics。"
  };
}

function buildModelTrustRuntimeRow(
  runtimeStatus: RuntimeStatusPayload
): DataPanelModelTrustEvidenceRow {
  const isError =
    runtimeStatus.status === "ERROR" || runtimeStatus.lifecycle_state === "ERROR";
  const isReady =
    runtimeStatus.initialized === true ||
    runtimeStatus.status === "RUNNING" ||
    runtimeStatus.status === "PAUSED" ||
    runtimeStatus.status === "COMPLETED";
  return {
    kind: "runtime",
    label: "运行证据",
    statusLabel: runtimeStatusLabel(runtimeStatus),
    detail: `t=${formatPreciseMetricValue(
      runtimeStatus.current_sim_time ?? 0
    )}s / events=${formatCount(runtimeStatus.processed_event_count ?? 0)} / ${runtimeModeLabel(
      runtimeStatus.mode
    )}`,
    source: "runtime/status",
    tone: isError ? "error" : isReady ? "match" : "pending",
    title: runtimeStatus.last_error ?? runtimeStatus.last_action
  };
}

function buildModelTrustActionLabels(
  rows: readonly DataPanelModelTrustEvidenceRow[],
  exportDiagnosticsBundle: RuntimeExportDiagnosticsBundleV1 | null | undefined
): readonly string[] {
  const labels = rows
    .filter((row) => row.tone === "pending" || row.tone === "error")
    .map((row) => `${row.label}：${row.statusLabel}`);
  if (exportDiagnosticsBundle !== null && exportDiagnosticsBundle !== undefined) {
    labels.push(
      ...exportDiagnosticsBundle.findings
        .filter((finding) => finding.severity === "ERROR" || finding.severity === "WARN")
        .slice(0, 3)
        .map((finding) => `${finding.severity} ${finding.code}`)
    );
  }
  return labels.length > 0 ? labels : ["证据链可用于导出结果包并进入复盘验收。"];
}

function clampCount(value: number, maxValue: number): number {
  if (!Number.isFinite(value)) {
    return 0;
  }
  return Math.min(Math.max(0, value), Math.max(0, maxValue));
}

function networkKpiCredibilityTone(status: string): DataPanelNetworkKpiCredibilityTone {
  if (status === "COMPLETE_FLOW_LEVEL_PROXY") {
    return "match";
  }
  if (status === "PARTIAL_RUNTIME_VALUES") {
    return "different";
  }
  if (status === "MISSING_RUNTIME_VALUES") {
    return "pending";
  }
  return "error";
}

function networkKpiCredibilityStatusLabel(status: string): string {
  if (status === "COMPLETE_FLOW_LEVEL_PROXY") {
    return "完整流级代理";
  }
  if (status === "PARTIAL_RUNTIME_VALUES") {
    return "部分运行值";
  }
  if (status === "MISSING_RUNTIME_VALUES") {
    return "运行值缺失";
  }
  if (status === "INVALID_PACKET_LEVEL_METRIC") {
    return "包级指标越界";
  }
  return "可信度未知";
}

function networkKpiBenchmarkValidationTone(
  status: string
): DataPanelNetworkKpiCredibilityTone {
  if (status === "PASS") {
    return "match";
  }
  if (status === "WARN") {
    return "different";
  }
  if (status === "INSUFFICIENT_DATA") {
    return "pending";
  }
  return "error";
}

function networkKpiBenchmarkValidationStatusLabel(status: string): string {
  if (status === "PASS") {
    return "基准通过";
  }
  if (status === "WARN") {
    return "基准告警";
  }
  if (status === "INSUFFICIENT_DATA") {
    return "数据不足";
  }
  if (status === "FAIL") {
    return "基准失败";
  }
  return "基准未知";
}

function networkKpiMetricModelLabel(metricModel: string): string {
  if (metricModel === "FLOW_LEVEL_PROXY") {
    return "流级代理";
  }
  return metricModel || "未知";
}

function routeProvenanceTrustTone(status: string): DataPanelNetworkKpiCredibilityTone {
  if (status === "COMPLETE_FLOW_LEVEL_ROUTE_PROXY") {
    return "match";
  }
  if (status === "PARTIAL_ROUTE_EXPLANATIONS") {
    return "different";
  }
  if (status === "MISSING_ROUTE_EXPLANATIONS") {
    return "pending";
  }
  return "error";
}

function routeProvenanceTrustStatusLabel(status: string): string {
  if (status === "COMPLETE_FLOW_LEVEL_ROUTE_PROXY") {
    return "完整流级路由代理";
  }
  if (status === "PARTIAL_ROUTE_EXPLANATIONS") {
    return "路由解释部分覆盖";
  }
  if (status === "MISSING_ROUTE_EXPLANATIONS") {
    return "路由解释缺失";
  }
  return "路由可信度未知";
}

function routeProvenanceTrustModelLabel(routeModel: string): string {
  if (routeModel === "FLOW_LEVEL_ROUTE_PROXY") {
    return "流级路由代理";
  }
  return routeModel || "未知";
}

function routeProvenanceTrustIssueLabels(
  trust: RuntimeRouteProvenanceTrustSummaryV1
): readonly string[] {
  const labels: string[] = [];
  if (trust.missing_explanation_count > 0) {
    labels.push(`缺少解释 ${formatCount(trust.missing_explanation_count)} 条`);
  }
  if (trust.hidden_route_count > 0) {
    labels.push(`未评估路由 ${formatCount(trust.hidden_route_count)} 条`);
  }
  if (trust.missing_context_field_count > 0) {
    labels.push(`缺少上下文字段 ${formatCount(trust.missing_context_field_count)} 个`);
  }
  if (trust.over_demand_route_count > 0) {
    labels.push(`超需求路由 ${formatCount(trust.over_demand_route_count)} 条`);
  }
  return labels;
}

function formatNetworkKpiValue(value: string | number | boolean | null): string {
  if (value === null) {
    return "-";
  }
  if (typeof value === "number") {
    return Number.isInteger(value) ? formatCount(value) : formatPreciseMetricValue(value);
  }
  if (typeof value === "boolean") {
    return value ? "true" : "false";
  }
  return value;
}

function networkKpiCredibilityIssueLabels(
  credibility: RuntimeNetworkKpiCredibilityV1
): readonly string[] {
  const labels: string[] = [];
  if (credibility.missing_metrics.length > 0) {
    labels.push(`缺失指标：${credibility.missing_metrics.slice(0, 4).join(", ")}`);
  }
  if (credibility.zero_unexplained_metrics.length > 0) {
    labels.push(
      `零值未解释：${credibility.zero_unexplained_metrics.slice(0, 4).join(", ")}`
    );
  }
  return labels;
}

function buildDataPanelKpiTailCaveats(
  backendKpiTimeSeries: RuntimeKpiTimeSeriesV1 | null | undefined
): readonly string[] {
  if ((backendKpiTimeSeries?.samples ?? []).length === 0) {
    return [];
  }
  const tailLabel = backendKpiTimeSeries?.tail_sample_source_label;
  if (typeof tailLabel !== "string" || tailLabel.trim().length === 0) {
    return [];
  }
  return [`尾点：${tailLabel}`];
}

function latestRuntimeKpiSample(
  backendKpiTimeSeries: RuntimeKpiTimeSeriesV1 | null | undefined
): RuntimeKpiSampleV1 | null {
  const samples = backendKpiTimeSeries?.samples ?? [];
  return samples.length === 0 ? null : samples[samples.length - 1];
}

export function buildDataPanelNetworkFormulaInputs(
  metrics: RuntimeMetricsSummary | null | undefined
): readonly DataPanelNetworkFormulaInput[] {
  return [
    metricInput(
      metrics,
      "network_quality_requested_route_demand_mbps",
      "请求需求",
      formatMetricMbps
    ),
    metricInput(
      metrics,
      "network_quality_offered_route_capacity_mbps",
      "路由容量",
      formatMetricMbps
    ),
    metricInput(
      metrics,
      "network_quality_flow_delivered_capacity_mbps",
      "完成流容量",
      formatMetricMbps
    ),
    metricInput(metrics, "network_quality_route_loss_proxy_rate", "路由损耗", formatRatioPercent),
    metricInput(metrics, "network_quality_congestion_proxy", "拥塞代理", formatRatioPercent),
    metricInput(metrics, "network_quality_demand_pressure_proxy", "业务压力", formatRatioPercent)
  ].filter((input): input is DataPanelNetworkFormulaInput => input !== null);
}

export function buildDataPanelNetworkComponentTail(
  backendKpiTimeSeries: RuntimeKpiTimeSeriesV1 | null | undefined
): readonly DataPanelNetworkFormulaInput[] {
  const sample = latestRuntimeKpiSample(backendKpiTimeSeries);
  if (sample === null) {
    return [];
  }
  return [
    sampleMetricInput(sample.network_offered_route_capacity_mbps, "样本路由容量", formatMetricMbps),
    sampleMetricInput(
      sample.network_requested_route_demand_mbps,
      "样本请求需求",
      formatMetricMbps
    ),
    sampleMetricInput(sample.network_demand_pressure_proxy, "样本需求压力", formatRatioPercent),
    sampleMetricInput(sample.network_route_loss_proxy_rate, "样本路由损耗", formatRatioPercent),
    sampleMetricInput(
      sample.network_pressure_loss_proxy_rate,
      "样本压力损耗",
      formatRatioPercent
    ),
    sampleMetricInput(
      sample.network_route_delay_variation_s,
      "样本路由抖动",
      formatMetricMilliseconds
    ),
    sampleMetricInput(
      sample.network_pressure_delay_variation_s,
      "样本压力抖动",
      formatMetricMilliseconds
    ),
    sampleMetricInput(sample.network_time_pressure_factor, "样本时间压力", formatRatioPercent),
    sampleMetricInput(
      sample.network_time_pressure_loss_proxy_rate,
      "样本时间损耗",
      formatRatioPercent
    ),
    sampleMetricInput(
      sample.network_time_pressure_delay_variation_s,
      "样本时间抖动",
      formatMetricMilliseconds
    )
  ].filter((input): input is DataPanelNetworkFormulaInput => input !== null);
}

export function buildDataPanelServiceLatencyDisplay(
  metrics: RuntimeMetricsSummary | null | undefined
): DataPanelServiceLatencyDisplay {
  const taskCount = Math.max(0, metricNumber(metrics, "service_latency_task_count") ?? 0);
  const completeCount = Math.max(
    0,
    metricNumber(metrics, "service_latency_complete_count") ?? 0
  );
  const model =
    metricString(metrics, "service_latency_model") ??
    "COMMUNICATION_COMPUTE_COMPONENT_PROXY";
  const items = [
    metricInput(
      metrics,
      "service_latency_input_network_avg_s",
      "输入网络",
      formatMetricMilliseconds
    ),
    metricInput(
      metrics,
      "service_latency_compute_queue_avg_s",
      "计算排队",
      formatMetricMilliseconds
    ),
    metricInput(
      metrics,
      "service_latency_compute_execution_avg_s",
      "计算执行",
      formatMetricMilliseconds
    ),
    metricInput(
      metrics,
      "service_latency_output_network_avg_s",
      "输出网络",
      formatMetricMilliseconds
    )
  ].filter((input): input is DataPanelNetworkFormulaInput => input !== null);
  return {
    sourceLabel: "通信-计算服务延迟",
    modelLabel:
      model === "COMMUNICATION_COMPUTE_COMPONENT_PROXY"
        ? "后端服务组件代理"
        : model,
    taskCountLabel: `${formatCount(taskCount)} 个服务`,
    completeCountLabel: `${formatCount(completeCount)} 个完整闭环`,
    totalLatencyLabel: formatMetricMilliseconds(
      metricNumber(metrics, "service_latency_total_avg_s") ?? 0
    ),
    items: taskCount > 0 ? items : []
  };
}

export function buildDataPanelServiceLatencyRows(
  history: RuntimeServiceLatencyHistoryV1 | null | undefined,
  limit = 3
): readonly DataPanelServiceLatencyRow[] {
  const rowLimit = Math.max(0, Math.floor(limit));
  return (history?.items ?? []).slice(0, rowLimit).map((item) => ({
    taskId: item.task_id,
    taskLabel: compactTaskId(item.task_id),
    traceTitle: serviceLatencyTraceTitle(item),
    statusLabel: item.complete ? "完整闭环" : "未闭环",
    placementLabel: serviceLatencyPlacementLabel(item),
    totalLatencyLabel: formatMetricMilliseconds(item.total_latency_s),
    timeline: serviceLatencyTimelineItems(item)
  }));
}

export function buildDataPanelServiceDetailRows(
  page: RuntimeServiceDetailPageV1 | null | undefined,
  limit = 8
): DataPanelServiceDetailRows {
  if (page === null || page === undefined) {
    return {
      sourceLabel: "等待后端服务详情页",
      summaryLabel: "暂无服务生命周期游标明细",
      items: []
    };
  }
  const boundedLimit = Math.max(0, Math.floor(limit));
  const items = page.items.slice(0, boundedLimit).map((item) => ({
    serviceId: item.service_id,
    taskLabel: compactTaskId(item.task_id || item.service_id),
    stateLabel: item.service_state_label || item.service_state,
    placementLabel: serviceDetailPlacementLabel(item),
    networkLatencyLabel: `${formatMetricMilliseconds(
      item.input_network_latency_s
    )} / ${formatMetricMilliseconds(item.output_network_latency_s)}`,
    computeLatencyLabel: `${formatMetricMilliseconds(
      item.compute_queue_delay_s
    )} / ${formatMetricMilliseconds(item.compute_execution_delay_s)}`,
    totalLatencyLabel: formatMetricMilliseconds(item.total_latency_s),
    traceTitle: serviceDetailTraceTitle(item)
  }));
  return {
    sourceLabel: `后端服务详情页 ${formatCount(page.item_count)} / ${formatCount(
      page.service_count
    )}`,
    summaryLabel: `${formatCount(items.length)} 行 / 完成 ${formatCount(
      page.complete_service_count
    )} / 排队 ${formatCount(page.queued_service_count)}${
      page.has_more ? " / 可继续游标读取" : ""
    }`,
    items
  };
}

export function buildDataPanelServiceLifecycleTraceDisplay(
  trace: RuntimeServiceLifecycleTraceV2 | null | undefined,
  limit = 6
): DataPanelServiceLifecycleTraceDisplay {
  if (trace === null || trace === undefined) {
    return {
      sourceLabel: "等待后端 service_lifecycle_trace_v2",
      summaryLabel: "暂无通信-计算服务 trace",
      items: []
    };
  }
  const boundedLimit = Math.max(0, Math.floor(limit));
  const items = trace.items.slice(0, boundedLimit).map((item) => {
    const stageRouteIds = item.stages
      .map((stage) => stage.route_id ?? "")
      .filter((routeId) => routeId.length > 0);
    const stageFlowIds = item.stages
      .map((stage) => stage.flow_id ?? "")
      .filter((flowId) => flowId.length > 0);
    const routeIds = uniqueStrings([
      item.input_route_id ?? "",
      item.output_route_id ?? "",
      ...stageRouteIds
    ]);
    const flowIds = uniqueStrings([
      item.input_flow_id ?? "",
      item.output_flow_id ?? "",
      ...stageFlowIds
    ]);
    return {
      traceId: item.trace_id || `trace:${item.service_id}`,
      serviceId: item.service_id,
      taskId: item.task_id,
      inputFlowId: item.input_flow_id ?? "",
      outputFlowId: item.output_flow_id ?? "",
      inputRouteId: item.input_route_id ?? "",
      outputRouteId: item.output_route_id ?? "",
      computeNodeId: item.compute_node_id ?? "",
      primaryRouteId: routeIds[0] ?? "",
      routeIds,
      flowIds,
      serviceLabel: compactTaskId(item.service_id || item.task_id),
      terminalState: item.terminal_state,
      terminalStateReason: item.terminal_state_reason,
      terminalStateLabel: serviceLifecycleTerminalLabel(
        item.terminal_state,
        item.terminal_state_reason
      ),
      computeNodeLabel: item.compute_node_id ? `算力 ${item.compute_node_id}` : "未放置",
      networkLatencyLabel: `${formatMetricMilliseconds(
        item.input_network_latency_s
      )} / ${formatMetricMilliseconds(item.output_network_latency_s)}`,
      computeLatencyLabel: `${formatMetricMilliseconds(
        item.compute_queue_delay_s
      )} / ${formatMetricMilliseconds(item.compute_execution_delay_s)}`,
      totalLatencyLabel: formatMetricMilliseconds(item.total_latency_s),
      traceTitle: serviceLifecycleTraceTitle(item),
      stages: item.stages.map((stage) => ({
        stageId: stage.stage_id,
        component: stage.component,
        stageKind: stage.stage_kind,
        stageStatus: stage.stage_status,
        label: serviceLifecycleStageLabel(stage.stage_label, stage.component),
        statusLabel: serviceLifecycleStageStatusLabel(stage.stage_status),
        durationLabel: formatMetricMilliseconds(stage.duration_s),
        traceTitle: serviceLifecycleStageTitle(stage)
      }))
    };
  });
  return {
    sourceLabel: `${trace.source_summary} -> service_lifecycle_trace_v2`,
    summaryLabel: `${formatCount(trace.trace_count)} trace / ${formatCount(
      trace.service_count
    )} service / 完成 ${formatCount(trace.complete_trace_count)} / 运行 ${formatCount(
      trace.running_trace_count
    )}${trace.has_more ? " / 可继续游标读取" : ""}`,
    items
  };
}

export function filterServiceLifecycleTraceDisplay(
  display: DataPanelServiceLifecycleTraceDisplay,
  filter: string | DataPanelServiceTraceFilter
): DataPanelServiceLifecycleTraceDisplay {
  const query = typeof filter === "string" ? filter : (filter.query ?? "");
  const terminalState =
    typeof filter === "string"
      ? "ALL"
      : normalizeServiceTraceTerminalFilter(filter.terminalState);
  const computeNodeFilter =
    typeof filter === "string" ? "" : (filter.computeNodeId ?? "");
  const stageKind =
    typeof filter === "string"
      ? "ALL"
      : normalizeServiceTraceStageFilter(filter.stageKind);
  const terminalReason =
    typeof filter === "string"
      ? "ALL"
      : normalizeServiceTraceTerminalReasonFilter(filter.terminalReason);
  const normalizedQuery = normalizeDetailFilter(query);
  const normalizedComputeNode = normalizeDetailFilter(computeNodeFilter);
  if (
    normalizedQuery.length === 0 &&
    terminalState === "ALL" &&
    normalizedComputeNode.length === 0 &&
    stageKind === "ALL" &&
    terminalReason === "ALL"
  ) {
    return display;
  }
  const items = display.items.filter((row) =>
    serviceLifecycleTraceMatchesFilter(
      row,
      normalizedQuery,
      terminalState,
      normalizedComputeNode,
      stageKind,
      terminalReason
    )
  );
  return {
    ...display,
    summaryLabel: `${display.summaryLabel} / 筛选 ${formatCount(items.length)}`,
    items
  };
}

export function serviceTraceDetailCursorFilters(
  query: string,
  terminalState: DataPanelServiceTraceTerminalFilter,
  computeNodeId: string,
  stageKind: DataPanelServiceTraceStageFilter = "ALL",
  terminalReason: DataPanelServiceTraceTerminalReasonFilter = "ALL"
): RuntimeDetailCursorFilters {
  const normalizedQuery = query.trim();
  const normalizedComputeNodeId = computeNodeId.trim();
  return {
    ...(normalizedQuery ? { query: normalizedQuery } : {}),
    ...(terminalState !== "ALL" ? { terminalState } : {}),
    ...(normalizedComputeNodeId ? { computeNodeId: normalizedComputeNodeId } : {}),
    ...(stageKind !== "ALL" ? { stageKind } : {}),
    ...(terminalReason !== "ALL" ? { terminalReason } : {})
  };
}

function normalizeServiceTraceTerminalFilter(
  value: string | null | undefined
): DataPanelServiceTraceTerminalFilter {
  if (
    value === "RUNNING" ||
    value === "COMPLETE" ||
    value === "INCOMPLETE" ||
    value === "ALL"
  ) {
    return value;
  }
  return "ALL";
}

function normalizeServiceTraceStageFilter(
  value: string | null | undefined
): DataPanelServiceTraceStageFilter {
  const normalized = normalizeServiceTraceCode(value);
  if (
    normalized === "INPUT_NETWORK" ||
    normalized === "COMPUTE_QUEUE" ||
    normalized === "COMPUTE_EXECUTION" ||
    normalized === "OUTPUT_NETWORK" ||
    normalized === "ALL"
  ) {
    return normalized;
  }
  return "ALL";
}

function normalizeServiceTraceTerminalReasonFilter(
  value: string | null | undefined
): DataPanelServiceTraceTerminalReasonFilter {
  const normalized = normalizeServiceTraceCode(value);
  if (
    normalized === "TOTAL_LATENCY_OBSERVED" ||
    normalized === "OUTPUT_NETWORK_PENDING" ||
    normalized === "COMPONENTS_OBSERVED_BUT_TOTAL_MISSING" ||
    normalized === "NO_COMPONENT_OBSERVATIONS" ||
    normalized === "ALL"
  ) {
    return normalized;
  }
  return "ALL";
}

function normalizeServiceTraceCode(value: string | null | undefined): string {
  const normalized = (value ?? "")
    .replace(/[_-]+/g, " ")
    .trim()
    .toUpperCase()
    .split(/\s+/)
    .filter(Boolean)
    .join("_");
  return normalized || "ALL";
}

function serviceLifecycleTraceMatchesFilter(
  row: DataPanelServiceLifecycleTraceRow,
  normalizedQuery: string,
  terminalState: DataPanelServiceTraceTerminalFilter,
  normalizedComputeNode: string,
  stageKind: DataPanelServiceTraceStageFilter,
  terminalReason: DataPanelServiceTraceTerminalReasonFilter
): boolean {
  if (terminalState !== "ALL" && row.terminalState !== terminalState) {
    return false;
  }
  if (
    terminalReason !== "ALL" &&
    normalizeServiceTraceCode(row.terminalStateReason) !== terminalReason
  ) {
    return false;
  }
  if (
    normalizedComputeNode.length > 0 &&
    normalizeDetailFilter(row.computeNodeId) !== normalizedComputeNode
  ) {
    return false;
  }
  if (
    stageKind !== "ALL" &&
    !row.stages.some(
      (stage) =>
        (normalizeServiceTraceCode(stage.stageKind) === stageKind ||
          normalizeServiceTraceCode(stage.component) === stageKind) &&
        normalizeServiceTraceCode(stage.stageStatus) !== "UNKNOWN"
    )
  ) {
    return false;
  }
  if (normalizedQuery.length === 0) {
    return true;
  }
  const candidates = [
    row.traceId,
    row.serviceId,
    row.taskId,
    row.inputFlowId,
    row.outputFlowId,
    row.inputRouteId,
    row.outputRouteId,
    row.computeNodeId,
    row.primaryRouteId,
    row.serviceLabel,
    row.terminalState,
    row.terminalStateReason,
    row.terminalStateLabel,
    row.computeNodeLabel,
    row.networkLatencyLabel,
    row.computeLatencyLabel,
    row.totalLatencyLabel,
    row.traceTitle,
    ...row.routeIds,
    ...row.flowIds,
    ...row.stages.flatMap((stage) => [
      stage.stageId,
      stage.label,
      stage.statusLabel,
      stage.durationLabel,
      stage.traceTitle
    ])
  ];
  return candidates.some((candidate) =>
    normalizeDetailFilter(candidate).includes(normalizedQuery)
  );
}

export function buildDataPanelComputeTaskTimelineDisplay(
  summary: RuntimeComputeTaskTimelineSummaryV1 | null | undefined,
  limit = 4
): DataPanelComputeTaskTimelineDisplay {
  const items = (summary?.items ?? []).slice(0, Math.max(0, Math.floor(limit)));
  return {
    sourceLabel: "后端计算任务时间线",
    summaryLabel:
      summary === null || summary === undefined
        ? "等待服务时间线"
        : `${formatCount(summary.item_count)} shown / ${formatCount(
            summary.task_count
          )} total / ${formatCount(summary.complete_task_count)} complete`,
    queuedTaskLabel: formatCount(summary?.queued_task_count ?? 0),
    totalQueueDelayLabel: formatMetricMilliseconds(
      summary?.total_compute_queue_delay_s ?? 0
    ),
    totalExecutionDelayLabel: formatMetricMilliseconds(
      summary?.total_compute_execution_delay_s ?? 0
    ),
    items: items.map((item) => ({
      taskId: item.task_id,
      taskLabel: compactTaskId(item.task_id),
      nodeLabel: item.compute_node_id ? `节点 ${item.compute_node_id}` : "无节点",
      queueExecutionLabel: `${formatMetricMilliseconds(
        item.queue_delay_s
      )} / ${formatMetricMilliseconds(item.execution_delay_s)}`,
      traceTitle: computeTaskTimelineTraceTitle(item)
    }))
  };
}

export function buildDataPanelComputeNodeDetailRows(
  page: RuntimeComputeNodeDetailPageV1 | null | undefined,
  limit = 12
): DataPanelComputeNodeDetailRows {
  if (page === null || page === undefined) {
    return {
      sourceLabel: "等待后端算力节点详情页",
      summaryLabel: "暂无算力节点游标明细",
      items: []
    };
  }
  const boundedLimit = Math.max(0, Math.floor(limit));
  const items = page.items.slice(0, boundedLimit).map((item) => ({
    nodeId: item.node_id,
    statusLabel: item.status,
    loadLabel: formatRatioPercent(item.compute_load_ratio),
    fp32Label: resourceUsageLabel(
      item.compute_used_gflops_fp32,
      item.compute_capacity_gflops_fp32,
      "GFLOPS"
    ),
    acceleratorLabel: `GPU ${resourceUsageLabel(
      item.compute_used_gpu_tflops_fp32,
      item.compute_capacity_gpu_tflops_fp32,
      "TFLOPS"
    )} / NPU ${resourceUsageLabel(
      item.compute_used_npu_tops_int8,
      item.compute_capacity_npu_tops_int8,
      "TOPS"
    )}`,
    memoryStorageLabel: `内存 ${resourceUsageLabel(
      item.compute_used_memory_gb,
      item.compute_capacity_memory_gb,
      "GB"
    )} / 存储 ${resourceUsageLabel(
      item.compute_used_storage_gb,
      item.compute_capacity_storage_gb,
      "GB"
    )}`,
    taskLabel: `${formatCount(item.running_task_count)} 运行 / ${formatCount(
      item.finished_task_count
    )} 完成`,
    traceTitle: computeNodeDetailTraceTitle(item)
  }));
  return {
    sourceLabel: `后端算力节点详情页 ${formatCount(page.item_count)} / ${formatCount(
      page.compute_node_count
    )}`,
    summaryLabel: `${formatCount(items.length)} 行 / 忙碌 ${formatCount(
      page.busy_compute_node_count
    )}${page.has_more ? " / 可继续游标读取" : ""}`,
    items
  };
}

export function buildDataPanelBackendCursorDisplay(
  page: {
    cursor?: number;
    limit?: number;
    next_cursor?: number;
    has_more?: boolean;
    item_count?: number;
    trace_count?: number;
  },
  totalCount: number
): DataPanelBackendCursorDisplay {
  const cursor = normalizeNonNegativeInteger(page.cursor ?? 0);
  const limit = Math.max(1, normalizeNonNegativeInteger(page.limit ?? 1));
  const itemCount = normalizeNonNegativeInteger(page.item_count ?? page.trace_count ?? 0);
  const total = normalizeNonNegativeInteger(totalCount);
  const start = itemCount === 0 ? 0 : cursor + 1;
  const end = Math.min(total, cursor + itemCount);
  const rangeLabel =
    itemCount === 0
      ? `0 / ${formatCount(total)}`
      : `${formatCount(start)}-${formatCount(end)} / ${formatCount(total)}`;
  const nextCursor = normalizeNonNegativeInteger(page.next_cursor ?? 0);
  return {
    rangeLabel,
    statusLabel: page.has_more === true
      ? `下一游标 ${formatCount(nextCursor)}`
      : "当前已到最后一页",
    previousCursor: Math.max(0, cursor - limit),
    nextCursor,
    canPrevious: cursor > 0,
    canNext: page.has_more === true
  };
}

export function buildDataPanelRouteConstraints(
  snapshot: WorldSnapshot,
  backendMetrics: RuntimeMetricsSummary | null | undefined = undefined,
  limit = 6
): DataPanelRouteConstraintRows {
  const backendRow = buildBackendRouteConstraint(backendMetrics);
  if (backendRow !== null) {
    return {
      sourceLabel: "后端约束摘要",
      items: [backendRow]
    };
  }
  const linkLookup = buildRouteLinkLookup(snapshot.links);
  const items = snapshot.routes
    .map((route) => ({
      route,
      row: {
        routeId: route.route_id,
        flowId: route.flow_id,
        statusLabel: route.available ? "可用" : "不可用",
        hopCount: Math.max(0, route.path.length - 1),
        latencyLabel: `${formatPreciseMetricValue(route.latency)} s`,
        capacityLabel: `${formatMetricValue(route.capacity)} Mbps`,
        demandLossLabel: routeDemandLossLabel(route),
        bottleneckLabel: routeBottleneckLabel(route, linkLookup),
        pathLabel: route.path.length > 0 ? route.path.join(" → ") : "无路径"
      }
    }))
    .sort((left, right) => compareRouteConstraint(left.route, right.route))
    .slice(0, Math.max(0, limit))
    .map((entry) => entry.row);
  return {
    sourceLabel: "快照路由明细",
    items
  };
}

export function buildDataPanelRouteExplanationRows(
  summary: RuntimeRouteExplanationSummaryV1 | null | undefined,
  limit = 6
): DataPanelRouteExplanationRows {
  if (summary === null || summary === undefined) {
    return {
      sourceLabel: "等待后端路由解释",
      items: []
    };
  }
  const rowLimit = Math.max(0, Math.floor(limit));
  const visibleCount = Math.min(rowLimit, summary.items.length);
  const hiddenLabel =
    summary.route_count > visibleCount
      ? ` / 显示 ${formatCount(visibleCount)} 条`
      : "";
  return {
    sourceLabel: `后端路由解释 ${formatCount(summary.item_count)}/${formatCount(
      summary.route_count
    )} 条；阻塞 ${formatCount(summary.blocked_route_count)} / 超需求 ${formatCount(
      summary.over_demand_route_count
    )}${hiddenLabel}`,
    items: summary.items.slice(0, rowLimit).map((item) => ({
      routeId: item.route_id || "未声明",
      flowId: item.flow_id || "未声明",
      available: item.available,
      availabilityLabel: item.available ? "可用" : "阻塞",
      businessType: item.business_type || "UNKNOWN",
      businessLabel: item.business_label || item.business_type || "未声明",
      nextHopLabel: item.primary_next_hop_id || "无",
      capacityDemandLabel: routeExplanationCapacityDemandLabel(
        item.capacity_mbps,
        item.demand_mbps
      ),
      pressureLabel: formatRatioPercent(Math.max(0, item.route_pressure_proxy)),
      bottleneckComponent: item.bottleneck_component || "UNKNOWN",
      bottleneckLabel:
        item.bottleneck_reason_label || item.bottleneck_component || "未声明",
      explanationLabel: item.explanation_label || "后端未提供解释",
      pathLabel: item.path_label || item.next_hop_ids.join(" -> ")
    }))
  };
}

function routeExplanationCapacityDemandLabel(
  capacity: number | null | undefined,
  demand: number | null | undefined
): string {
  const capacityLabel =
    typeof capacity === "number" && Number.isFinite(capacity)
      ? formatMetricMbps(Math.max(0, capacity))
      : "未声明";
  const demandLabel =
    typeof demand === "number" && Number.isFinite(demand)
      ? formatMetricMbps(Math.max(0, demand))
      : "未声明";
  return `${capacityLabel} / ${demandLabel}`;
}

export function filterRouteExplanationRows(
  rows: DataPanelRouteExplanationRows,
  filter: string | DataPanelRouteExplanationFilter
): DataPanelRouteExplanationRows {
  const criteria =
    typeof filter === "string"
      ? { query: filter }
      : filter;
  const normalizedQuery = (criteria.query ?? "").trim().toLowerCase();
  const availability = criteria.availability ?? "ALL";
  const businessType = criteria.businessType ?? "ALL";
  const bottleneckComponent = criteria.bottleneckComponent ?? "ALL";
  if (
    normalizedQuery.length === 0 &&
    availability === "ALL" &&
    businessType === "ALL" &&
    bottleneckComponent === "ALL"
  ) {
    return rows;
  }
  const items = rows.items.filter((item) => {
    const availabilityMatches =
      availability === "ALL" ||
      (availability === "AVAILABLE" && item.available) ||
      (availability === "BLOCKED" && !item.available);
    const businessMatches =
      businessType === "ALL" || item.businessType === businessType;
    const bottleneckMatches =
      bottleneckComponent === "ALL" ||
      item.bottleneckComponent === bottleneckComponent;
    const textMatches =
      normalizedQuery.length === 0 ||
      [
        item.routeId,
        item.flowId,
        item.availabilityLabel,
        item.businessType,
        item.businessLabel,
        item.nextHopLabel,
        item.capacityDemandLabel,
        item.pressureLabel,
        item.bottleneckComponent,
        item.bottleneckLabel,
        item.explanationLabel,
        item.pathLabel
      ].some((value) => value.toLowerCase().includes(normalizedQuery));
    return availabilityMatches && businessMatches && bottleneckMatches && textMatches;
  });
  return {
    sourceLabel: `${rows.sourceLabel} / 筛选 ${formatCount(items.length)}`,
    items
  };
}

function buildBackendRouteConstraint(
  metrics: RuntimeMetricsSummary | null | undefined
): DataPanelRouteConstraint | null {
  const source = metricString(metrics, "network_constraint_summary_source");
  const routeId = metricString(metrics, "network_constraint_top_route_id");
  if (source !== "BACKEND_METRICS_COLLECTOR" || !routeId) {
    return null;
  }
  const available = metricBoolean(metrics, "network_constraint_top_route_available");
  const flowId = metricString(metrics, "network_constraint_top_route_flow_id") ?? "未声明";
  const hopCount = metricNumber(metrics, "network_constraint_top_route_hop_count") ?? 0;
  const latency = metricNumber(metrics, "network_constraint_top_route_latency_s") ?? 0;
  const capacity = metricNumber(metrics, "network_constraint_top_route_capacity_mbps") ?? 0;
  const demand = metricNumber(metrics, "network_constraint_top_route_demand_mbps") ?? 0;
  const lossRate = metricNumber(metrics, "network_constraint_top_route_loss_rate") ?? 0;
  const pressure =
    metricNumber(metrics, "network_constraint_top_route_pressure_proxy") ?? 0;
  const topLink = metricString(metrics, "network_constraint_top_link_id");
  const topLinkCapacity = metricNumber(
    metrics,
    "network_constraint_top_link_capacity_mbps"
  );
  const topLinkLatency = metricNumber(metrics, "network_constraint_top_link_latency_s");
  const topLinkUtilization = metricNumber(
    metrics,
    "network_constraint_top_link_utilization"
  );
  return {
    routeId,
    flowId,
    statusLabel: available === false ? "不可用" : "可用",
    hopCount: Math.max(0, Math.round(hopCount)),
    latencyLabel: `${formatPreciseMetricValue(latency)} s`,
    capacityLabel: `${formatMetricValue(capacity)} Mbps`,
    demandLossLabel: `需求${formatMetricValue(demand)} Mbps / 损耗${formatMetricValue(
      lossRate * 100
    )}% / 压力${formatMetricValue(pressure * 100)}%`,
    bottleneckLabel: backendLinkConstraintLabel(
      topLink,
      topLinkCapacity,
      topLinkLatency,
      topLinkUtilization
    ),
    pathLabel: metricString(metrics, "network_constraint_top_route_path") ?? "未声明"
  };
}

function compareRouteConstraint(left: SnapshotRoute, right: SnapshotRoute): number {
  if (left.available !== right.available) {
    return Number(left.available) - Number(right.available);
  }
  const capacityDelta = left.capacity - right.capacity;
  if (capacityDelta !== 0) {
    return capacityDelta;
  }
  const latencyDelta = right.latency - left.latency;
  if (latencyDelta !== 0) {
    return latencyDelta;
  }
  const hopDelta = Math.max(0, right.path.length - 1) - Math.max(0, left.path.length - 1);
  if (hopDelta !== 0) {
    return hopDelta;
  }
  return left.route_id.localeCompare(right.route_id);
}

function buildRouteLinkLookup(links: readonly SnapshotLink[]): ReadonlyMap<string, SnapshotLink> {
  const lookup = new Map<string, SnapshotLink>();
  for (const link of links) {
    if (!link.availability) {
      continue;
    }
    const directKey = routeLinkKey(link.source_id, link.target_id);
    if (!lookup.has(directKey)) {
      lookup.set(directKey, link);
    }
    const reverseKey = routeLinkKey(link.target_id, link.source_id);
    if (!lookup.has(reverseKey)) {
      lookup.set(reverseKey, link);
    }
  }
  return lookup;
}

function routeBottleneckLabel(
  route: SnapshotRoute,
  linkLookup: ReadonlyMap<string, SnapshotLink>
): string {
  if (route.path.length < 2) {
    return route.available ? "无跳段" : "无可用路径";
  }
  let bottleneck:
    | {
        edgeLabel: string;
        capacity: number;
        latency: number;
      }
    | null = null;
  for (let index = 0; index < route.path.length - 1; index += 1) {
    const source = route.path[index];
    const target = route.path[index + 1];
    const link = linkLookup.get(routeLinkKey(source, target));
    if (!link) {
      continue;
    }
    const edgeLabel = `${source} → ${target}`;
    if (
      bottleneck === null ||
      link.capacity < bottleneck.capacity ||
      (link.capacity === bottleneck.capacity && link.latency > bottleneck.latency) ||
      (link.capacity === bottleneck.capacity &&
        link.latency === bottleneck.latency &&
        edgeLabel.localeCompare(bottleneck.edgeLabel) < 0)
    ) {
      bottleneck = {
        edgeLabel,
        capacity: link.capacity,
        latency: link.latency
      };
    }
  }
  if (bottleneck !== null) {
    return `${bottleneck.edgeLabel} / ${formatMetricValue(
      bottleneck.capacity
    )} Mbps / ${formatPreciseMetricValue(bottleneck.latency)} s`;
  }
  return route.available ? "未匹配链路明细" : "未收到可用链路";
}

function routeDemandLossLabel(route: SnapshotRoute): string {
  const demand =
    typeof route.demand_capacity === "number" && Number.isFinite(route.demand_capacity)
      ? `需求${formatMetricValue(route.demand_capacity)} Mbps`
      : null;
  const loss =
    typeof route.loss_rate === "number" && Number.isFinite(route.loss_rate)
      ? `损耗${formatMetricValue(route.loss_rate * 100)}%`
      : null;
  return [demand, loss].filter((value): value is string => value !== null).join(" / ") || "未声明";
}

function backendLinkConstraintLabel(
  linkId: string | undefined,
  capacity: number | undefined,
  latency: number | undefined,
  utilization: number | undefined
): string {
  if (!linkId) {
    return "后端未声明瓶颈链路";
  }
  const details = [
    capacity === undefined ? null : `${formatMetricValue(capacity)} Mbps`,
    latency === undefined ? null : `${formatPreciseMetricValue(latency)} s`,
    utilization === undefined ? null : `利用率${formatMetricValue(utilization * 100)}%`
  ].filter((value): value is string => value !== null);
  return details.length === 0 ? linkId : `${linkId} / ${details.join(" / ")}`;
}

function routeLinkKey(sourceId: string, targetId: string): string {
  return `${sourceId}\u0000${targetId}`;
}

function dataPanelTrafficLabel(traffic: TrafficDemandSummary): string {
  const trafficClass = traffic.traffic_class;
  const destinationType = traffic.destination_type;
  const classLabel =
    traffic.traffic_class_label ??
    (trafficClass === "COMPUTE_SERVICE" || trafficClass === "TASK_OFFLOAD_FLOW"
      ? "通信-计算服务"
      : trafficClass === "DATA_TRANSFER"
        ? "数据传输"
      : trafficClass === "TELEMETRY"
        ? "遥测"
        : trafficClass === "BULK_DOWNLINK"
          ? "批量下传"
          : trafficClass);
  const executionLabel =
    traffic.execution_label ??
    (trafficClass === "COMPUTE_SERVICE" || trafficClass === "TASK_OFFLOAD_FLOW"
      ? "通信+计算"
      : trafficClass === "DATA_TRANSFER" ||
          trafficClass === "TELEMETRY" ||
          trafficClass === "BULK_DOWNLINK"
        ? "仅网络流"
        : traffic.execution_shape ?? "执行形态未声明");
  const destinationLabel =
    traffic.destination_type_label ??
    (destinationType === "COMPUTE_NODE"
      ? "星上算力"
      : destinationType === "GROUND_ENDPOINT"
        ? "地面端"
        : destinationType === "SATELLITE"
          ? "卫星"
          : destinationType === "SERVICE_ENDPOINT"
            ? "服务端点"
            : destinationType);
  return `${classLabel} / ${destinationLabel} / ${executionLabel}`;
}

function buildDataPanelTrafficNote(traffic: TrafficDemandSummary): string | null {
  const parts: string[] = [];
  const serviceMixNote = buildTrafficServiceMixNote(traffic);
  if (serviceMixNote) {
    parts.push(serviceMixNote);
  }
  const semanticNote = traffic.lifecycle_note ?? traffic.compatibility_note;
  if (semanticNote) {
    parts.push(semanticNote);
  }
  const taskCount = traffic.generated_task_count;
  const outputFlowCount = traffic.generated_output_flow_metadata_count;
  if (typeof taskCount === "number" || typeof outputFlowCount === "number") {
    parts.push(
      `生成 ${formatCount(traffic.generated_flow_count)} 流 / ${formatCount(
        Math.max(0, taskCount ?? 0)
      )} 任务 / ${formatCount(Math.max(0, outputFlowCount ?? 0))} 结果流元数据`
    );
  }
  if (
    typeof traffic.total_input_data_mb === "number" ||
    typeof traffic.total_output_data_mb === "number"
  ) {
    parts.push(
      `数据 ${formatMetricValue(Math.max(0, traffic.total_input_data_mb ?? 0))} MB 输入 / ${formatMetricValue(
        Math.max(0, traffic.total_output_data_mb ?? 0)
      )} MB 输出`
    );
  }
  if (typeof traffic.system_request_rate_per_minute === "number") {
    parts.push(
      `速率 ${formatPreciseMetricValue(
        Math.max(0, traffic.system_request_rate_per_minute)
      )} 次/分钟 / 单用户 ${formatPreciseMetricValue(
        Math.max(0, traffic.average_user_request_rate_per_minute ?? 0)
      )} 次/分钟`
    );
  }
  if (traffic.source_selection_policy || traffic.destination_selection_policy) {
    parts.push(
      `源/目的 ${traffic.source_selection_policy ?? "未声明"} -> ${
        traffic.destination_selection_policy ?? "未声明"
      }`
    );
  }
  return parts.length === 0 ? null : parts.join("；");
}

function buildTrafficServiceMixNote(traffic: TrafficDemandSummary): string | null {
  const activeClasses = traffic.active_service_classes ?? [];
  const normalizedWeights = traffic.service_mix_normalized_weights;
  if (activeClasses.length === 0 || !normalizedWeights) {
    return null;
  }
  const modeLabel =
    traffic.service_mix_mode === "WEIGHTED_MIX" ? "业务组合" : "单业务";
  const counts = traffic.service_mix_generated_request_counts ?? {};
  const classParts = activeClasses.map((trafficClass) => {
    const share = Math.max(0, normalizedWeights[trafficClass] ?? 0);
    const requestCount = counts[trafficClass];
    const countText =
      typeof requestCount === "number" ? ` / ${formatCount(requestCount)} 请求` : "";
    return `${trafficClassLabel(trafficClass)} ${formatMetricValue(share * 100)}%${countText}`;
  });
  return `${modeLabel}: ${classParts.join(" + ")}`;
}

function trafficClassLabel(trafficClass: string): string {
  if (trafficClass === "COMPUTE_SERVICE" || trafficClass === "TASK_OFFLOAD_FLOW") {
    return "通信-计算服务";
  }
  if (trafficClass === "DATA_TRANSFER") {
    return "数据传输";
  }
  if (trafficClass === "TELEMETRY") {
    return "遥测";
  }
  if (trafficClass === "BULK_DOWNLINK") {
    return "批量下传";
  }
  return trafficClass;
}

function dataPanelRequestStateLabel(requestState: string): string {
  if (requestState === "IDLE") {
    return "空闲";
  }
  if (requestState === "NETWORK_WAITING") {
    return "等待网络路径";
  }
  if (requestState === "COMPUTE_SERVICE_ACTIVE") {
    return "计算服务进行中";
  }
  if (requestState === "COMPUTE_SERVICE_READY") {
    return "计算服务可达";
  }
  if (requestState === "NETWORK_SERVICE_READY") {
    return "网络业务可达";
  }
  return requestState;
}

function shortRuntimeHash(hash: string): string {
  const normalized = hash.startsWith("sha256:") ? hash.slice("sha256:".length) : hash;
  return normalized.length <= 12 ? normalized : normalized.slice(0, 12);
}

function formatPercent(value: number): string {
  return value.toLocaleString("zh-CN", {
    maximumFractionDigits: 1,
    minimumFractionDigits: 0
  });
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
