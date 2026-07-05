import { memo, useState, type MouseEvent } from "react";
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
  TrafficDemandSummary,
  RuntimeExportCatalogV1,
  RuntimeExportPackageCompareV1,
  RuntimeExportRestoreCommandResultV1,
  RuntimeExportRestorePreflightV1,
  RuntimeComputeTaskTimelineSummaryV1,
  RuntimeKpiSampleV1,
  RuntimeKpiTimeSeriesV1,
  RuntimeExportHistoryV1,
  RuntimeMetricsSummary,
  RuntimeNetworkKpiCredibilityV1,
  RuntimeNetworkQualityProvenanceV1,
  RuntimeNodeDetailCardV1,
  RuntimeNodeDetailPageV1,
  RuntimeNodeDetailSummaryV1,
  RuntimeReproducibilityManifestV1,
  RuntimeRouteExplanationSummaryV1,
  RuntimeSatelliteServiceItemV1,
  RuntimeSatelliteServiceSummaryV1,
  RuntimeSatelliteKpiHistoryV1,
  RuntimeSatelliteKpiSlicesV1,
  RuntimeServiceLatencyHistoryV1,
  RuntimeStatusPayload,
  RuntimeUserRequestHistoryV1,
  RuntimeUserRequestItemV1,
  RuntimeUserRequestSummaryV1,
  UserConfigurationExportV1,
  UserConfigurationSchemaV2,
  UserConfigurationTemplateCatalogV1,
  UserConfigurationValidationApplyCommandV1,
  UserConfigurationValidationReportV1
} from "../../core/event_types";
import {
  runtimeExportArchiveHref,
  runtimeExportPackageArchiveHref,
  runtimeExportPackageCompareHref,
  runtimeExportPackageManifestHref,
  runtimeExportPackageRecordHref,
  runtimeExportRestorePreflightHref,
  userConfigurationExportHref,
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
  users?: RuntimeUserRequestSummaryV1 | null;
  satellites?: RuntimeSatelliteServiceSummaryV1 | null;
  nodes?: RuntimeNodeDetailPageV1 | null;
}

const USER_DETAIL_PAGE_SIZE = 80;
const SATELLITE_DETAIL_PAGE_SIZE = 120;
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

export const DataPanel = memo(function DataPanel({
  snapshot,
  runtimeStatus,
  generatedConfig,
  runtimeDetailPages,
  runtimeExportCatalog,
  runtimeExportCompare,
  runtimeExportComparePackageId,
  runtimeExportCompareLoading,
  runtimeExportCompareError,
  runtimeExportRestorePreflight,
  runtimeExportRestorePreflightLoading,
  runtimeExportRestorePreflightError,
  runtimeExportRestoreCommandPendingPackageId,
  runtimeExportRestoreCommandError,
  runtimeExportRestoreResult,
  userConfigurationSchema,
  userConfigurationTemplates,
  userConfigurationExport,
  userConfigurationContractLoading,
  userConfigurationContractError,
  onUserConfigurationValidate,
  onUserConfigurationValidateText,
  onUserConfigurationApply,
  onRuntimeExportCompareSelect,
  onRuntimeExportRestore,
  displaySimTime,
  displayEventCount,
  onNavigateControl
}: {
  snapshot: WorldSnapshot;
  runtimeStatus: RuntimeStatusPayload;
  generatedConfig: GeneratedScenarioConfig | null;
  runtimeDetailPages?: RuntimeDetailPages | null;
  runtimeExportCatalog?: RuntimeExportCatalogV1 | null;
  runtimeExportCompare?: RuntimeExportPackageCompareV1 | null;
  runtimeExportComparePackageId?: string | null;
  runtimeExportCompareLoading?: boolean;
  runtimeExportCompareError?: string | null;
  runtimeExportRestorePreflight?: RuntimeExportRestorePreflightV1 | null;
  runtimeExportRestorePreflightLoading?: boolean;
  runtimeExportRestorePreflightError?: string | null;
  runtimeExportRestoreCommandPendingPackageId?: string | null;
  runtimeExportRestoreCommandError?: string | null;
  runtimeExportRestoreResult?: RuntimeExportRestoreCommandResultV1 | null;
  userConfigurationSchema?: UserConfigurationSchemaV2 | null;
  userConfigurationTemplates?: UserConfigurationTemplateCatalogV1 | null;
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
  onRuntimeExportRestore?: (packageId: string) => void;
  displaySimTime: number;
  displayEventCount: number;
  onNavigateControl: (event: MouseEvent<HTMLAnchorElement>) => void;
}) {
  const [computeSeriesKey, setComputeSeriesKey] =
    useState<DataPanelComputeSeriesKey>("computeUsedTflops");
  const [detailFilter, setDetailFilter] = useState("");
  const [routeExplanationFilter, setRouteExplanationFilter] = useState("");
  const [routeExplanationAvailabilityFilter, setRouteExplanationAvailabilityFilter] =
    useState<DataPanelRouteExplanationAvailabilityFilter>("ALL");
  const [routeExplanationBusinessFilter, setRouteExplanationBusinessFilter] =
    useState("ALL");
  const [routeExplanationBottleneckFilter, setRouteExplanationBottleneckFilter] =
    useState("ALL");
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
  const exportCatalogDisplay = buildDataPanelExportCatalogDisplay(runtimeExportCatalog);
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
  const computeTaskTimeline = buildDataPanelComputeTaskTimelineDisplay(
    runtimeStatus.compute_task_timeline_summary_v1
  );
  const routeConstraints = buildDataPanelRouteConstraints(
    snapshot,
    runtimeStatus.metrics_summary
  );
  const routeExplanations = buildDataPanelRouteExplanationRows(
    runtimeStatus.route_explanation_summary_v1
  );
  const filteredRouteExplanations = filterRouteExplanationRows(
    routeExplanations,
    {
      query: routeExplanationFilter,
      availability: routeExplanationAvailabilityFilter,
      businessType: routeExplanationBusinessFilter,
      bottleneckComponent: routeExplanationBottleneckFilter
    }
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
    USER_DETAIL_PAGE_SIZE
  );
  const satelliteDetailWindow = paginateDetailRows(
    filteredSatelliteResourceRows.items,
    satelliteDetailPage,
    SATELLITE_DETAIL_PAGE_SIZE
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
  const userDetailInspector = buildUserBusinessRequestInspector(
    selectedUserDetailRow,
    nodeDetailSummary
  );
  const satelliteDetailInspector = buildSatelliteResourceInspector(
    selectedSatelliteDetailRow,
    nodeDetailSummary
  );
  const nodeDetailDrawerItems = buildDataPanelNodeDetailDrawerItems(
    userDetailInspector,
    satelliteDetailInspector
  );
  const userSourceBadge = buildRuntimeDetailSourceBadge(userBusinessRequests.sourceLabel);
  const satelliteSourceBadge = buildRuntimeDetailSourceBadge(satelliteResourceRows.sourceLabel);
  const detailScopeNotes = buildDataPanelDetailScopeNotes(
    userBusinessRequests,
    satelliteResourceRows,
    userRequestSummary,
    satelliteServiceSummary,
    runtimeStatus.satellite_kpi_slices_v1,
    runtimeStatus.satellite_kpi_history_v1
  );
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
        </section>
      ) : null}

      {exportCatalogDisplay ? (
        <section className="dashboard-section data-panel-export-catalog" aria-label="复盘包目录">
          <div className="section-title">复盘包目录</div>
          <div className="data-panel-source-note">
            <span>{exportCatalogDisplay.sourceLabel}</span>
            <small>{exportCatalogDisplay.summaryLabel}</small>
          </div>
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
            filterValue={routeExplanationFilter}
            onFilterChange={setRouteExplanationFilter}
            availabilityFilter={routeExplanationAvailabilityFilter}
            onAvailabilityFilterChange={setRouteExplanationAvailabilityFilter}
            businessFilter={routeExplanationBusinessFilter}
            onBusinessFilterChange={setRouteExplanationBusinessFilter}
            bottleneckFilter={routeExplanationBottleneckFilter}
            onBottleneckFilterChange={setRouteExplanationBottleneckFilter}
          />
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
          <TopComputeNodeTable rows={topComputeNodes} />
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
        user={userDetailInspector}
        satellite={satelliteDetailInspector}
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
            onSelect={(row) => setSelectedDetailUserId(row.userId)}
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
            onSelect={(row) => setSelectedDetailSatelliteId(row.satelliteId)}
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
): RuntimeUserRequestSummaryV1 | null | undefined {
  return runtimeDetailPages?.users ?? runtimeStatus.user_request_summary_v1;
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
  filterValue,
  onFilterChange,
  availabilityFilter,
  onAvailabilityFilterChange,
  businessFilter,
  onBusinessFilterChange,
  bottleneckFilter,
  onBottleneckFilterChange
}: {
  rows: DataPanelRouteExplanationRows;
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
        <div className="data-panel-route-empty">{emptyLabel}</div>
      </div>
    );
  }
  return (
    <div className="data-panel-route-explanations">
      {controls}
      <div className="data-panel-route-table explanations" aria-label="后端路由解释明细">
        <div className="data-panel-route-source">{rows.sourceLabel}</div>
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
          <div className="data-panel-route-row" key={row.routeId} title={row.pathLabel}>
            <span>{row.routeId}</span>
            <span>{row.businessLabel}</span>
            <span>{row.nextHopLabel}</span>
            <span>{row.capacityDemandLabel}</span>
            <span>{row.pressureLabel}</span>
            <span>{row.bottleneckLabel}</span>
            <span>{row.explanationLabel}</span>
          </div>
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
          key={row.userId}
          title={row.pathLabel}
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
  userId: string;
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
  kind: "user" | "satellite";
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
      userId,
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
          : `${userId}: no active route`
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
      item.pathLabel
    ].some((value) => value.toLowerCase().includes(normalized))
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
  backendDetailSummary: RuntimeNodeDetailSummaryV1 | null | undefined = undefined
): DataPanelDetailInspector {
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
  backendDetailSummary: RuntimeNodeDetailSummaryV1 | null | undefined = undefined
): DataPanelDetailInspector {
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

export function buildDataPanelNodeDetailDrawerItems(
  user: DataPanelDetailInspector,
  satellite: DataPanelDetailInspector
): readonly DataPanelNodeDetailDrawerItem[] {
  return [
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

function buildBackendUserBusinessRequestRows(
  summary: RuntimeUserRequestSummaryV1,
  limit: number
): UserBusinessRequestRows {
  const items = summary.items.slice(0, Math.max(0, limit)).map((item) => {
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
      userId: item.user_id,
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
          : `${item.user_id}: no active route`)
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
  return {
    sourceLabel: "backend user_request_summary_v1",
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

function compactTaskId(taskId: string): string {
  if (taskId.length <= 18) {
    return taskId;
  }
  return `...${taskId.slice(-15)}`;
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
  schemaHref: string;
  templatesHref: string;
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

export function buildDataPanelUserConfigurationContractDisplay(
  schema: UserConfigurationSchemaV2 | null | undefined,
  templates: UserConfigurationTemplateCatalogV1 | null | undefined,
  exported: UserConfigurationExportV1 | null | undefined,
  loading = false,
  error: string | null | undefined = null
): DataPanelUserConfigurationContractDisplay | null {
  if (loading && schema == null && templates == null && exported == null) {
    return {
      tone: "pending",
      sourceLabel: "BACKEND_USER_CONFIGURATION",
      summaryLabel: "正在加载 schema、模板目录和当前配置导出",
      statusLabel: "加载中",
      detailLabel: "只读接口，不会修改当前配置",
      metaLabels: ["schema pending", "templates pending", "export pending"],
      fieldSections: [],
      schemaHref: userConfigurationSchemaHref(),
      templatesHref: userConfigurationTemplatesHref(),
      exportHref: userConfigurationExportHref()
    };
  }
  if (error !== null && error !== undefined && schema == null && exported == null) {
    return {
      tone: "error",
      sourceLabel: "BACKEND_USER_CONFIGURATION",
      summaryLabel: error,
      statusLabel: "配置契约加载失败",
      detailLabel: "请检查后端 /scenario/user-config/* 只读接口",
      metaLabels: [error],
      fieldSections: [],
      schemaHref: userConfigurationSchemaHref(),
      templatesHref: userConfigurationTemplatesHref(),
      exportHref: userConfigurationExportHref()
    };
  }
  if (schema == null && templates == null && exported == null) {
    return null;
  }
  const schemaId = schema?.schema_id ?? templates?.schema_id ?? exported?.schema_id ?? "unknown";
  const fieldCount = schema?.field_count ?? 0;
  const keyFieldCount = schema?.key_field_count ?? 0;
  const templateCount = templates?.template_count ?? schema?.templates.length ?? 0;
  const configHash = exported?.config_hash ?? "";
  const validationOk = exported?.validation_ok ?? false;
  const source = exported?.source ?? templates?.source ?? schema?.source ?? "BACKEND_USER_CONFIGURATION";
  return {
    tone: validationOk || exported === null ? "match" : "error",
    sourceLabel: `${source} / ${schemaId}`,
    summaryLabel: `字段 ${formatCount(fieldCount)} / 关键 ${formatCount(
      keyFieldCount
    )} / 模板 ${formatCount(templateCount)}`,
    statusLabel: validationOk || exported === null ? "当前配置可复现" : "当前配置校验异常",
    detailLabel: exported
      ? `config ${shortRuntimeHash(configHash)} / ${exported.export_scope}`
      : "等待当前配置导出",
    metaLabels: [
      `unknown ${schema?.unknown_key_policy ?? exported?.unknown_key_policy ?? "REJECT"}`,
      `default ${schema?.defaulting_policy ?? exported?.defaulting_policy ?? "BACKEND"}`,
      `validation ${validationOk ? "ok" : exported === null ? "pending" : "failed"}`,
      `format ${schema?.format ?? exported?.format ?? "YAML_OR_JSON_MAPPING"}`
    ],
    fieldSections: buildDataPanelUserConfigurationFieldSections(schema),
    schemaHref: userConfigurationSchemaHref(),
    templatesHref: userConfigurationTemplatesHref(),
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
  archiveHref: string | null;
  compareHref: string;
  restorePreflightHref: string;
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

function networkKpiMetricModelLabel(metricModel: string): string {
  if (metricModel === "FLOW_LEVEL_PROXY") {
    return "流级代理";
  }
  return metricModel || "未知";
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
