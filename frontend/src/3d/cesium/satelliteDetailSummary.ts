import {
  ComputeResourceSummary,
  GroundUserState,
  LinkState,
  Route,
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

export function selectedSatelliteDetailSummary({
  satellite,
  computeNode,
  computeResourceSummary,
  links,
  routes,
  groundUsers,
  scenarioConfig
}: {
  satellite: SatelliteState;
  computeNode?: ComputeNodeRenderState | null;
  computeResourceSummary?: ComputeResourceSummary | null;
  links: readonly LinkState[];
  routes: readonly Route[];
  groundUsers: readonly GroundUserState[];
  scenarioConfig: ScenarioConfig | null;
}): SelectedSatelliteDetailSummary {
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
  const computeSummary = satelliteComputeSummary(computeNode, computeResourceSummary);

  return {
    satelliteId: satellite.satellite_id,
    statusLabel: `状态 ${satellite.status}`,
    simTimeLabel: `t=${formatNumber(satellite.sim_time)}s`,
    altitudeLabel: `高度 ${formatNumber(satelliteAltitudeKm(satellite))} km`,
    speedLabel: `速度 ${formatNumber(satelliteSpeedKmPerSecond(satellite))} km/s`,
    activeLinksLabel: `链路 ${activeLinks.length} 条（接入 ${activeAccessLinks.length} / 星间 ${activeSpaceLinks.length}）`,
    routeLabel: `相关路由 ${relatedRoutes.length} 条 / 可用 ${availableRoutes.length} 条`,
    routeLatencyLabel:
      averageRouteLatencySeconds === null
        ? "平均路由时延 --"
        : `平均路由时延 ${formatNumber(averageRouteLatencySeconds * 1000)} ms`,
    routeCapacityLabel: `可用路由容量 ${formatNumber(totalRouteCapacity)} Mbps`,
    routeLossLabel:
      routeLossProxy === null
        ? "路由丢包代理 --"
        : `路由丢包代理 ${formatNumber(routeLossProxy * 100)}%`,
    routeJitterLabel:
      routeJitterProxy === null
        ? "路由抖动代理 --"
        : `路由抖动代理 ${formatNumber(routeJitterProxy * 1000)} ms`,
    linkUtilizationLabel:
      averageLinkUtilization === null
        ? "平均链路利用率 --"
        : `平均链路利用率 ${formatNumber(averageLinkUtilization * 100)}%`,
    coverageLabel: coverageSummary.coveredUserLabel,
    computeLoadLabel: computeSummary
      ? `算力负载 ${computeSummary.utilizationLabel}`
      : "算力节点未同步",
    computeCapacityLabel: computeSummary ? `容量 ${computeSummary.capacityLabel}` : "容量 --",
    runningTaskLabel: computeNode
      ? `任务 运行 ${computeNode.running_tasks} / 完成 ${computeNode.finished_tasks}`
      : "任务 --",
    resourceModelLabel: computeSummary?.resourceModelLabel ?? "资源模型未同步",
    routeIds: relatedRoutes.slice(0, 4).map((route) => route.route_id),
    computeSummary,
    note: "链路、路由和算力为后端 snapshot 的流级聚合态势；不是 packet-level 仿真。"
  };
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

function formatNumber(value: number): string {
  return value.toLocaleString("zh-CN", {
    maximumFractionDigits: 1,
    minimumFractionDigits: 0
  });
}
