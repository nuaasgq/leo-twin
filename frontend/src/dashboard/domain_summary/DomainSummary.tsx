import { memo } from "react";

import { WorldSnapshot } from "../../state/snapshot_engine";
import { KpiPanel } from "../kpi_panel/KpiPanel";

export interface DomainSummaryValues {
  activeLinks: number;
  availableRoutes: number;
  routeLatency: number;
  routeCapacity: number;
  runningTasks: number;
  finishedTasks: number;
  computeNodes: number;
  couplingHealth: number;
}

type DomainSummarySnapshot = Pick<
  WorldSnapshot,
  "links" | "routes" | "active_tasks" | "compute_nodes"
>;

export const DomainSummary = memo(function DomainSummary({
  snapshot
}: {
  snapshot: WorldSnapshot;
}) {
  const summary = buildDomainSummary(snapshot);

  return (
    <section className="dashboard-section" aria-label="全链路态势">
      <div className="section-title">全链路态势</div>
      <div className="kpi-grid wide">
        <KpiPanel label="活动链路" value={String(summary.activeLinks)} />
        <KpiPanel label="可用路由" value={String(summary.availableRoutes)} />
        <KpiPanel label="路由时延" value={`${summary.routeLatency.toFixed(3)} s`} />
        <KpiPanel label="路由容量" value={`${summary.routeCapacity.toFixed(1)} Mbps`} />
        <KpiPanel label="运行任务" value={String(summary.runningTasks)} />
        <KpiPanel label="完成任务" value={String(summary.finishedTasks)} />
        <KpiPanel label="算力节点" value={String(summary.computeNodes)} />
        <KpiPanel label="耦合健康" value={`${summary.couplingHealth}%`} />
      </div>
    </section>
  );
});

export function buildDomainSummary(snapshot: DomainSummarySnapshot): DomainSummaryValues {
  const availableRoutes = snapshot.routes.filter((route) => route.available);
  const activeLinks = snapshot.links.filter((link) => link.availability).length;
  const runningTasks = snapshot.active_tasks.length;
  const finishedTasks = snapshot.compute_nodes.reduce(
    (total, node) => total + node.finished_tasks,
    0
  );
  const bestRoute = availableRoutes
    .slice()
    .sort((left, right) => {
      const byLatency = left.latency - right.latency;
      if (byLatency !== 0) {
        return byLatency;
      }
      return left.route_id.localeCompare(right.route_id);
    })[0];

  return {
    activeLinks,
    availableRoutes: availableRoutes.length,
    routeLatency: bestRoute?.latency ?? 0,
    routeCapacity: bestRoute?.capacity ?? 0,
    runningTasks,
    finishedTasks,
    computeNodes: snapshot.compute_nodes.length,
    couplingHealth: couplingHealthScore({
      hasLinks: activeLinks > 0,
      hasRoutes: availableRoutes.length > 0,
      hasCapacity: (bestRoute?.capacity ?? 0) > 0,
      hasCompute: snapshot.compute_nodes.length > 0
    })
  };
}

function couplingHealthScore(signals: {
  hasLinks: boolean;
  hasRoutes: boolean;
  hasCapacity: boolean;
  hasCompute: boolean;
}): number {
  const values = [
    signals.hasLinks,
    signals.hasRoutes,
    signals.hasCapacity,
    signals.hasCompute
  ];
  const active = values.filter(Boolean).length;
  return Math.round((active / values.length) * 100);
}
