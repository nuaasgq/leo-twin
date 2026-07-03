import { memo } from "react";

import { LinkState, Route } from "../../core/event_types";
import { WorldSnapshot } from "../../state/snapshot_engine";
import { KpiPanel } from "../kpi_panel/KpiPanel";

export interface LinkProtocolSummary {
  activeLinks: number;
  availableRoutes: number;
  bestRouteId: string;
  bestPath: string;
  bestHopCount: number;
  averageHopCount: number;
  maxHopCount: number;
  gatewayRoutes: number;
  bestLatency: number;
  bottleneckCapacity: number;
  spaceLinks: number;
  accessLinks: number;
  transportProtocol: string;
  routingProtocol: string;
  transportProtocolLabel: string;
  routingProtocolLabel: string;
  stackLayers: number;
  carrierFrequencyGhz: number;
  bandwidthMhz: number;
  estimatedRainFadeDb: number;
  rows: readonly LinkProtocolRow[];
}

export interface LinkProtocolRow {
  linkId: string;
  latency: number;
  capacity: number;
  status: string;
}

type LinkProtocolSnapshot = Pick<
  WorldSnapshot,
  "links" | "routes" | "active_route_id" | "scenario_config"
>;

export const LinkProtocolPanel = memo(function LinkProtocolPanel({
  snapshot
}: {
  snapshot: WorldSnapshot;
}) {
  const summary = buildLinkProtocolSummary(snapshot);

  return (
    <section className="dashboard-section link-protocol-panel" aria-label="链路与协议">
      <div className="section-title">链路与协议</div>
      <div className="kpi-grid wide">
        <KpiPanel label="活动链路" value={String(summary.activeLinks)} />
        <KpiPanel label="可用路由" value={String(summary.availableRoutes)} />
        <KpiPanel label="最佳时延" value={`${summary.bestLatency.toFixed(3)} s`} />
        <KpiPanel label="瓶颈容量" value={`${summary.bottleneckCapacity.toFixed(1)} Mbps`} />
        <KpiPanel label="路径跳数" value={String(summary.bestHopCount)} />
        <KpiPanel label="平均跳数" value={summary.averageHopCount.toFixed(1)} />
        <KpiPanel label="最长跳数" value={String(summary.maxHopCount)} />
        <KpiPanel label="网关路由" value={String(summary.gatewayRoutes)} />
        <KpiPanel label="传输协议" value={summary.transportProtocolLabel} />
        <KpiPanel label="路由协议" value={summary.routingProtocolLabel} />
        <KpiPanel label="协议栈层数" value={String(summary.stackLayers)} />
        <KpiPanel label="载波频率" value={`${summary.carrierFrequencyGhz.toFixed(1)} GHz`} />
        <KpiPanel label="信道带宽" value={`${summary.bandwidthMhz.toFixed(0)} MHz`} />
        <KpiPanel label="估算雨衰" value={`${summary.estimatedRainFadeDb.toFixed(2)} dB`} />
        <KpiPanel label="星间链路" value={String(summary.spaceLinks)} />
        <KpiPanel label="接入链路" value={String(summary.accessLinks)} />
      </div>
      <div className="route-strip" aria-label="最佳路径">
        <span>最佳路径</span>
        <strong>{summary.bestPath}</strong>
      </div>
      <div className="link-table" aria-label="链路明细">
        {summary.rows.map((row) => (
          <div className="link-table-row" key={row.linkId}>
            <span>{row.linkId}</span>
            <span>{row.latency.toFixed(3)} s</span>
            <span>{row.capacity.toFixed(1)} Mbps</span>
            <strong>{row.status}</strong>
          </div>
        ))}
      </div>
    </section>
  );
});

export function buildLinkProtocolSummary(
  snapshot: LinkProtocolSnapshot
): LinkProtocolSummary {
  const activeLinks = snapshot.links.filter((link) => link.availability);
  const availableRoutes = snapshot.routes.filter((route) => route.available);
  const bestRoute = selectBestRoute(availableRoutes, snapshot.active_route_id);
  const hopCounts = availableRoutes.map(routeHopCount);
  const bottleneckCapacity =
    activeLinks.length === 0
      ? 0
      : Math.min(...activeLinks.map((link) => link.capacity));
  const linkClasses = classifyLinks(activeLinks);
  const network = snapshot.scenario_config?.network;
  const transportProtocol = network?.transport_protocol ?? "TCP";
  const routingProtocol = network?.routing_protocol ?? "LINK_STATE";
  const carrierFrequencyGhz = (network?.carrier_frequency_hz ?? 20_000_000_000) / 1_000_000_000;
  const bandwidthMhz = (network?.channel_bandwidth_hz ?? 100_000_000) / 1_000_000;
  const estimatedRainFadeDb =
    (network?.rain_rate_mm_h ?? 0) *
    (network?.rain_attenuation_coefficient_db_per_km_per_mm_h ?? 0) *
    (network?.rain_effective_path_km ?? 0);

  return {
    activeLinks: activeLinks.length,
    availableRoutes: availableRoutes.length,
    bestRouteId: bestRoute?.route_id ?? "无",
    bestPath: bestRoute?.path.join(" -> ") ?? "暂无可用路径",
    bestHopCount: bestRoute === undefined ? 0 : routeHopCount(bestRoute),
    averageHopCount:
      hopCounts.length === 0
        ? 0
        : hopCounts.reduce((total, hopCount) => total + hopCount, 0) /
          hopCounts.length,
    maxHopCount: hopCounts.length === 0 ? 0 : Math.max(...hopCounts),
    gatewayRoutes: availableRoutes.filter(routeEndsAtComputeNode).length,
    bestLatency: bestRoute?.latency ?? 0,
    bottleneckCapacity,
    spaceLinks: linkClasses.spaceLinks,
    accessLinks: linkClasses.accessLinks,
    transportProtocol,
    routingProtocol,
    transportProtocolLabel: formatTransportProtocol(transportProtocol),
    routingProtocolLabel: formatRoutingProtocol(routingProtocol),
    stackLayers: 6,
    carrierFrequencyGhz,
    bandwidthMhz,
    estimatedRainFadeDb,
    rows: activeLinks
      .slice()
      .sort(compareLinks)
      .slice(0, 5)
      .map(linkToRow)
  };
}

function routeHopCount(route: Route): number {
  return Math.max(0, route.path.length - 1);
}

function routeEndsAtComputeNode(route: Route): boolean {
  const lastNode = route.path[route.path.length - 1];
  return typeof lastNode === "string" && lastNode.startsWith("compute-");
}

function formatTransportProtocol(protocol: string): string {
  if (protocol === "TCP") {
    return "TCP 可靠传输";
  }
  if (protocol === "UDP") {
    return "UDP 低时延";
  }
  return protocol;
}

function formatRoutingProtocol(protocol: string): string {
  if (protocol === "LINK_STATE") {
    return "链路状态";
  }
  if (protocol === "DISTANCE_VECTOR") {
    return "距离向量";
  }
  if (protocol === "SHORTEST_PATH") {
    return "最短路径";
  }
  if (protocol === "STATIC") {
    return "静态路由";
  }
  return protocol;
}

function classifyLinks(links: readonly LinkState[]): {
  spaceLinks: number;
  accessLinks: number;
} {
  return links.reduce(
    (summary, link) => {
      const sourceIsSatellite = isSatelliteEndpoint(link.source_id);
      const targetIsSatellite = isSatelliteEndpoint(link.target_id);
      if (sourceIsSatellite && targetIsSatellite) {
        summary.spaceLinks += 1;
      } else if (sourceIsSatellite || targetIsSatellite) {
        summary.accessLinks += 1;
      }
      return summary;
    },
    { spaceLinks: 0, accessLinks: 0 }
  );
}

function isSatelliteEndpoint(endpointId: string): boolean {
  return endpointId.toLowerCase().startsWith("sat-");
}

function selectBestRoute(
  routes: readonly Route[],
  activeRouteId: string | null
): Route | undefined {
  const activeRoute = routes.find((route) => route.route_id === activeRouteId);
  if (activeRoute !== undefined) {
    return activeRoute;
  }
  return routes.slice().sort(compareRoutes)[0];
}

function compareRoutes(left: Route, right: Route): number {
  const latency = left.latency - right.latency;
  if (latency !== 0) {
    return latency;
  }
  return left.route_id.localeCompare(right.route_id);
}

function compareLinks(left: LinkState, right: LinkState): number {
  const capacity = right.capacity - left.capacity;
  if (capacity !== 0) {
    return capacity;
  }
  return `${left.source_id}->${left.target_id}`.localeCompare(
    `${right.source_id}->${right.target_id}`
  );
}

function linkToRow(link: LinkState): LinkProtocolRow {
  return {
    linkId: `${link.source_id} -> ${link.target_id}`,
    latency: link.latency,
    capacity: link.capacity,
    status: link.availability ? "可用" : "不可用"
  };
}
