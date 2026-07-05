import {
  ComputeResourceSummary,
  GroundUserState,
  LinkState,
  Route,
  RuntimeSatelliteKpiHistoryV1,
  RuntimeSatelliteKpiSlicesV1,
  RuntimeSatelliteKpiSliceV1,
  SatelliteState,
  ScenarioConfig
} from "../../core/event_types";
import type { ComputeNodeRenderState } from "../../state/snapshot_engine";
import { coverageUserIntersectionSummary } from "../beam_renderer/beamEntities";
import {
  SatelliteComputeSummary,
  satelliteAltitudeKm,
  satelliteComputeSummary
} from "./satelliteFollow";

export interface SelectedSatelliteDetailSummary {
  satelliteId: string;
  statusLabel: string;
  simTimeLabel: string;
  altitudeLabel: string;
  speedLabel: string;
  activeLinksLabel: string;
  routeLabel: string;
  routeLatencyLabel: string;
  routeCapacityLabel: string;
  routeLossLabel: string;
  routeJitterLabel: string;
  linkUtilizationLabel: string;
  coverageLabel: string;
  computeLoadLabel: string;
  computeCapacityLabel: string;
  runningTaskLabel: string;
  resourceModelLabel: string;
  routeIds: readonly string[];
  computeSummary: SatelliteComputeSummary | null;
  note: string;
}

export interface SelectedSatelliteResourceUsageRow {
  label: string;
  usedLabel: string;
  capacityLabel: string;
  utilizationPercent: number;
  utilizationLabel: string;
}

export interface SelectedSatelliteResourceHistoryPoint {
  satelliteId: string;
  simTime: number;
  utilizationPercent: number;
}

export function selectedSatelliteDetailSummary({
  satellite,
  computeNode,
  computeResourceSummary,
  links,
  routes,
  groundUsers,
  scenarioConfig,
  satelliteKpiSlices
}: {
  satellite: SatelliteState;
  computeNode?: ComputeNodeRenderState | null;
  computeResourceSummary?: ComputeResourceSummary | null;
  links: readonly LinkState[];
  routes: readonly Route[];
  groundUsers: readonly GroundUserState[];
  scenarioConfig: ScenarioConfig | null;
  satelliteKpiSlices?: RuntimeSatelliteKpiSlicesV1 | null;
}): SelectedSatelliteDetailSummary {
  const backendSlice = satelliteKpiSlices?.slices.find(
    (slice) => slice.satellite_id === satellite.satellite_id
  );
  const relatedLinks = links.filter((link) => linkTouchesSatellite(link, satellite.satellite_id));
  const activeLinks = relatedLinks.filter((link) => link.availability);
  const activeSpaceLinks = activeLinks.filter(isSpaceLink);
  const activeAccessLinks = activeLinks.filter(isAccessLink);
  const relatedRoutes = routes.filter((route) => route.path.includes(satellite.satellite_id));
  const availableRoutes = relatedRoutes.filter((route) => route.available);
  const averageRouteLatencySeconds = average(
    availableRoutes.map((route) => route.latency)
  );
  const totalRouteCapacity = availableRoutes.reduce(
    (total, route) => total + Math.max(0, finiteNumber(route.capacity)),
    0
  );
  const routeLossProxy = average(
    availableRoutes
      .map((route) => route.loss_rate)
      .filter((value): value is number => value !== undefined)
  );
  const routeJitterProxy = latencySpreadSeconds(
    availableRoutes.map((route) => route.latency)
  );
  const averageLinkUtilization = average(
    activeLinks
      .map((link) => link.utilization)
      .filter((value): value is number => value !== undefined)
  );
  const coverageSummary = coverageUserIntersectionSummary(
    satellite,
    groundUsers,
    scenarioConfig
  );
  const computeSummary = satelliteComputeSummary(
    computeNode ?? computeNodeFromBackendSlice(backendSlice),
    computeResourceSummary
  );
  const activeLinkCount = backendSlice?.active_link_count ?? activeLinks.length;
  const activeAccessLinkCount =
    backendSlice?.active_access_link_count ?? activeAccessLinks.length;
  const activeSpaceLinkCount =
    backendSlice?.active_space_link_count ?? activeSpaceLinks.length;
  const routeCount = backendSlice?.route_count ?? relatedRoutes.length;
  const availableRouteCount =
    backendSlice?.available_route_count ?? availableRoutes.length;
  const routeLatencySeconds = backendRouteValue(
    backendSlice,
    "route_latency_avg_s",
    averageRouteLatencySeconds,
    availableRouteCount > 0
  );
  const routeCapacityMbps = backendSlice?.route_capacity_mbps ?? totalRouteCapacity;
  const routeLossRate = backendRouteValue(
    backendSlice,
    "route_loss_proxy_rate",
    routeLossProxy,
    availableRouteCount > 0
  );
  const routeJitterSeconds = backendRouteValue(
    backendSlice,
    "route_delay_variation_proxy_s",
    routeJitterProxy,
    availableRouteCount > 1
  );
  const computeLoadLabel = backendSlice
    ? `算力负载 ${formatNumber(backendSlice.compute_load_ratio * 100)}%`
    : computeSummary
      ? `算力负载 ${computeSummary.utilizationLabel}`
      : "算力节点未同步";
  const computeCapacityLabel = backendSlice
    ? `容量 ${formatNumber(backendSlice.compute_used_gflops_fp32)} / ${formatNumber(
        backendSlice.compute_capacity_gflops_fp32
      )} GFLOPS FP32`
    : computeSummary
      ? `容量 ${computeSummary.capacityLabel}`
      : "容量 --";
  const runningTaskLabel = backendSlice
    ? `任务 运行 ${backendSlice.running_task_count} / 完成 ${backendSlice.finished_task_count}`
    : computeNode
      ? `任务 运行 ${computeNode.running_tasks} / 完成 ${computeNode.finished_tasks}`
      : "任务 --";

  return {
    satelliteId: satellite.satellite_id,
    statusLabel: `状态 ${satellite.status}`,
    simTimeLabel: `t=${formatNumber(satellite.sim_time)}s`,
    altitudeLabel: `高度 ${formatNumber(satelliteAltitudeKm(satellite))} km`,
    speedLabel: `速度 ${formatNumber(satelliteSpeedKmPerSecond(satellite))} km/s`,
    activeLinksLabel: `链路 ${activeLinkCount} 条（接入 ${activeAccessLinkCount} / 星间 ${activeSpaceLinkCount}）`,
    routeLabel: `相关路由 ${routeCount} 条 / 可用 ${availableRouteCount} 条`,
    routeLatencyLabel:
      routeLatencySeconds === null
        ? "平均路由时延 --"
        : `平均路由时延 ${formatNumber(routeLatencySeconds * 1000)} ms`,
    routeCapacityLabel: `可用路由容量 ${formatNumber(routeCapacityMbps)} Mbps`,
    routeLossLabel:
      routeLossRate === null
        ? "路由丢包代理 --"
        : `路由丢包代理 ${formatNumber(routeLossRate * 100)}%`,
    routeJitterLabel:
      routeJitterSeconds === null
        ? "路由抖动代理 --"
        : `路由抖动代理 ${formatNumber(routeJitterSeconds * 1000)} ms`,
    linkUtilizationLabel:
      averageLinkUtilization === null
        ? "平均链路利用率 --"
        : `平均链路利用率 ${formatNumber(averageLinkUtilization * 100)}%`,
    coverageLabel: coverageSummary.coveredUserLabel,
    computeLoadLabel,
    computeCapacityLabel,
    runningTaskLabel,
    resourceModelLabel:
      backendSlice !== undefined
        ? "RuntimeSatelliteKpiSlicesV1"
        : computeSummary?.resourceModelLabel ?? "资源模型未同步",
    routeIds: relatedRoutes.slice(0, 4).map((route) => route.route_id),
    computeSummary,
    note:
      backendSlice !== undefined
        ? "链路、路由和算力优先来自后端 runtime satellite KPI 切片；不是 packet-level 仿真。"
        : "链路、路由和算力为后端 snapshot 的流级聚合态势；不是 packet-level 仿真。"
  };
}

function computeNodeFromBackendSlice(
  slice: RuntimeSatelliteKpiSliceV1 | undefined
): Parameters<typeof satelliteComputeSummary>[0] | null {
  if (slice === undefined) {
    return null;
  }
  const fp32Capacity = Math.max(0, finiteNumber(slice.compute_capacity_gflops_fp32));
  const fp32Used = Math.max(0, finiteNumber(slice.compute_used_gflops_fp32));
  return {
    capacity: fp32Capacity,
    available_capacity: Math.max(0, fp32Capacity - fp32Used),
    load_ratio: clamp(finiteNumber(slice.compute_load_ratio), 0, 1),
    status: slice.running_task_count > 0 || fp32Used > 0 ? "BUSY" : "IDLE",
    cpu_gflops_fp64: slice.compute_capacity_gflops_fp64 ?? 0,
    gpu_tflops_fp32: slice.compute_capacity_gpu_tflops_fp32 ?? 0,
    gpu_tflops_fp16: slice.compute_capacity_gpu_tflops_fp16 ?? 0,
    npu_tops_int8: slice.compute_capacity_npu_tops_int8 ?? 0,
    memory_gb: slice.compute_capacity_memory_gb ?? 0,
    storage_gb: slice.compute_capacity_storage_gb ?? 0,
    used_cpu_gflops_fp32: fp32Used,
    used_cpu_gflops_fp64: slice.compute_used_gflops_fp64 ?? 0,
    used_gpu_tflops_fp32: slice.compute_used_gpu_tflops_fp32 ?? 0,
    used_gpu_tflops_fp16: slice.compute_used_gpu_tflops_fp16 ?? 0,
    used_npu_tops_int8: slice.compute_used_npu_tops_int8 ?? 0,
    used_memory_gb: slice.compute_used_memory_gb ?? 0,
    used_storage_gb: slice.compute_used_storage_gb ?? 0
  };
}

export function selectedSatelliteResourceUsageRows(
  summary: SelectedSatelliteDetailSummary,
  limit = 7
): readonly SelectedSatelliteResourceUsageRow[] {
  const rows = summary.computeSummary?.resourceBreakdown ?? [];
  const rowLimit = Math.max(0, Math.floor(limit));
  return rows.slice(0, rowLimit).map((row) => {
    const utilizationPercent = clamp(row.utilizationPercent, 0, 100);
    return {
      label: row.label,
      usedLabel: row.usedLabel,
      capacityLabel: row.capacityLabel,
      utilizationPercent,
      utilizationLabel: `${formatNumber(utilizationPercent)}%`
    };
  });
}

export function appendSelectedSatelliteResourceHistory(
  currentHistory: readonly SelectedSatelliteResourceHistoryPoint[],
  summary: SelectedSatelliteDetailSummary | null,
  simTime: number,
  maxPoints = 32
): readonly SelectedSatelliteResourceHistoryPoint[] {
  if (!summary?.computeSummary) {
    return [];
  }
  const nextPoint = {
    satelliteId: summary.satelliteId,
    simTime,
    utilizationPercent: clamp(summary.computeSummary.utilizationPercent, 0, 100)
  };
  const retainedHistory =
    currentHistory[currentHistory.length - 1]?.satelliteId === summary.satelliteId
      ? currentHistory
      : [];
  const previousPoint = retainedHistory[retainedHistory.length - 1];
  if (
    previousPoint?.simTime === nextPoint.simTime &&
    previousPoint.utilizationPercent === nextPoint.utilizationPercent
  ) {
    return retainedHistory;
  }
  return [...retainedHistory, nextPoint].slice(-Math.max(2, Math.floor(maxPoints)));
}

export function selectedSatelliteResourceHistoryPoints(
  history: readonly SelectedSatelliteResourceHistoryPoint[],
  width = 100,
  height = 36
): string {
  if (history.length === 0) {
    return "";
  }
  const safeWidth = Math.max(1, width);
  const safeHeight = Math.max(1, height);
  return history
    .map((point, index) => {
      const x =
        history.length === 1 ? safeWidth / 2 : (index * safeWidth) / (history.length - 1);
      const y = safeHeight - (clamp(point.utilizationPercent, 0, 100) / 100) * safeHeight;
      return `${formatSvgNumber(x)},${formatSvgNumber(y)}`;
    })
    .join(" ");
}

export function selectedSatelliteResourceHistoryFromBackend(
  history: RuntimeSatelliteKpiHistoryV1 | null | undefined,
  satelliteId: string
): readonly SelectedSatelliteResourceHistoryPoint[] {
  if (!satelliteId) {
    return [];
  }
  const series = history?.series.find((item) => item.satellite_id === satelliteId);
  if (!series) {
    return [];
  }
  return series.samples.map((sample) => ({
    satelliteId,
    simTime: finiteNumber(sample.sim_time),
    utilizationPercent: clamp(
      finiteNumber(sample.compute_load_ratio) * 100,
      0,
      100
    )
  }));
}

function backendRouteValue(
  slice: RuntimeSatelliteKpiSliceV1 | undefined,
  key: "route_latency_avg_s" | "route_loss_proxy_rate" | "route_delay_variation_proxy_s",
  fallback: number | null,
  hasBackendSample: boolean
): number | null {
  if (slice === undefined || !hasBackendSample) {
    return fallback;
  }
  const value = slice[key];
  return Number.isFinite(value) ? value : fallback;
}

function linkTouchesSatellite(link: LinkState, satelliteId: string): boolean {
  return link.source_id === satelliteId || link.target_id === satelliteId;
}

function isSpaceLink(link: LinkState): boolean {
  return isSatelliteEndpoint(link.source_id) && isSatelliteEndpoint(link.target_id);
}

function isAccessLink(link: LinkState): boolean {
  return isSatelliteEndpoint(link.source_id) !== isSatelliteEndpoint(link.target_id);
}

function isSatelliteEndpoint(endpointId: string): boolean {
  return endpointId.toLowerCase().startsWith("sat-");
}

function satelliteSpeedKmPerSecond(satellite: SatelliteState): number {
  if (!satellite.velocity) {
    return 0;
  }
  return (
    Math.hypot(satellite.velocity[0], satellite.velocity[1], satellite.velocity[2]) /
    1000
  );
}

function average(values: readonly number[]): number | null {
  const finiteValues = values.filter(Number.isFinite);
  if (finiteValues.length === 0) {
    return null;
  }
  return finiteValues.reduce((total, value) => total + value, 0) / finiteValues.length;
}

function latencySpreadSeconds(values: readonly number[]): number | null {
  const finiteValues = values.filter(Number.isFinite);
  if (finiteValues.length < 2) {
    return null;
  }
  return Math.max(...finiteValues) - Math.min(...finiteValues);
}

function finiteNumber(value: number): number {
  return Number.isFinite(value) ? value : 0;
}

function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, finiteNumber(value)));
}

function formatNumber(value: number): string {
  return value.toLocaleString("zh-CN", {
    maximumFractionDigits: 1,
    minimumFractionDigits: 0
  });
}

function formatSvgNumber(value: number): string {
  return String(Math.round(value * 100) / 100);
}
