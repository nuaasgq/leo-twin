import { memo } from "react";

import { LinkState, Route } from "../../core/event_types";
import { WorldSnapshot } from "../../state/snapshot_engine";
import { KpiPanel } from "../kpi_panel/KpiPanel";

export interface LinkProtocolSummary {
  activeLinks: number;
  availableRoutes: number;
  bestRouteId: string;
  bestPath: string;
  bestLatency: number;
  bottleneckCapacity: number;
  rows: readonly LinkProtocolRow[];
}

export interface LinkProtocolRow {
  linkId: string;
  latency: number;
  capacity: number;
  status: string;
}

type LinkProtocolSnapshot = Pick<WorldSnapshot, "links" | "routes" | "active_route_id">;

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
  const bottleneckCapacity =
    activeLinks.length === 0
      ? 0
      : Math.min(...activeLinks.map((link) => link.capacity));

  return {
    activeLinks: activeLinks.length,
    availableRoutes: availableRoutes.length,
    bestRouteId: bestRoute?.route_id ?? "无",
    bestPath: bestRoute?.path.join(" -> ") ?? "暂无可用路径",
    bestLatency: bestRoute?.latency ?? 0,
    bottleneckCapacity,
    rows: activeLinks
      .slice()
      .sort(compareLinks)
      .slice(0, 5)
      .map(linkToRow)
  };
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
