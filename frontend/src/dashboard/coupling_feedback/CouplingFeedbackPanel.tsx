import { memo } from "react";

import { WorldSnapshot } from "../../state/snapshot_engine";
import { KpiPanel } from "../kpi_panel/KpiPanel";

export interface CouplingFeedbackSummary {
  activeAccessLinks: number;
  activeSpaceLinks: number;
  availableRoutes: number;
  totalRoutes: number;
  waitingForNetwork: number;
  busyComputeNodes: number;
  computeNodes: number;
  averageComputeLoad: number;
  routeUpdateEvents: number;
  statusLabel: string;
  signalRows: readonly CouplingFeedbackRow[];
}

export interface CouplingFeedbackRow {
  label: string;
  value: string;
  detail: string;
}

type CouplingFeedbackSnapshot = Pick<
  WorldSnapshot,
  "active_tasks" | "compute_nodes" | "links" | "metrics_summary" | "routes"
>;

export const CouplingFeedbackPanel = memo(function CouplingFeedbackPanel({
  snapshot
}: {
  snapshot: WorldSnapshot;
}) {
  const summary = buildCouplingFeedbackSummary(snapshot);

  return (
    <section className="dashboard-section coupling-feedback-panel" aria-label="联动反馈">
      <div className="section-title">联动反馈</div>
      <div className="kpi-grid wide">
        <KpiPanel label="闭环状态" value={summary.statusLabel} />
        <KpiPanel
          label="算力负载"
          value={formatPercent(summary.averageComputeLoad)}
          detail={`${summary.busyComputeNodes}/${summary.computeNodes} 节点忙碌`}
        />
        <KpiPanel
          label="路由可达"
          value={`${summary.availableRoutes}/${summary.totalRoutes}`}
          detail={`${summary.waitingForNetwork} 个等待网络`}
        />
        <KpiPanel label="重路由事件" value={String(summary.routeUpdateEvents)} />
      </div>
      <div className="coupling-flow-list" aria-label="跨域联动链路">
        {summary.signalRows.map((row) => (
          <div className="coupling-flow-row" key={row.label}>
            <span>{row.label}</span>
            <strong>{row.value}</strong>
            <small>{row.detail}</small>
          </div>
        ))}
      </div>
    </section>
  );
});

export function buildCouplingFeedbackSummary(
  snapshot: CouplingFeedbackSnapshot
): CouplingFeedbackSummary {
  const activeLinks = snapshot.links.filter((link) => link.availability);
  const activeAccessLinks = activeLinks.filter(isAccessLink).length;
  const activeSpaceLinks = activeLinks.filter(isSpaceLink).length;
  const availableRoutes = snapshot.routes.filter((route) => route.available);
  const activeTaskIds = new Set(snapshot.active_tasks.map((task) => task.task_id));
  const availableRouteFlowIds = new Set(availableRoutes.map((route) => route.flow_id));
  const waitingForNetwork = snapshot.routes.filter(
    (route) =>
      !route.available &&
      !activeTaskIds.has(route.flow_id) &&
      !availableRouteFlowIds.has(route.flow_id)
  ).length;
  const busyComputeNodes = snapshot.compute_nodes.filter((node) => node.status === "BUSY")
    .length;
  const averageComputeLoad =
    snapshot.compute_nodes.length === 0
      ? 0
      : snapshot.compute_nodes.reduce((total, node) => total + node.load_ratio, 0) /
        snapshot.compute_nodes.length;
  const routeUpdateEvents = snapshot.metrics_summary.network.topology?.routeUpdateEvents ?? 0;
  const statusLabel = couplingStatusLabel({
    activeAccessLinks,
    availableRoutes: availableRoutes.length,
    busyComputeNodes,
    computeNodes: snapshot.compute_nodes.length,
    waitingForNetwork
  });

  return {
    activeAccessLinks,
    activeSpaceLinks,
    availableRoutes: availableRoutes.length,
    totalRoutes: snapshot.routes.length,
    waitingForNetwork,
    busyComputeNodes,
    computeNodes: snapshot.compute_nodes.length,
    averageComputeLoad,
    routeUpdateEvents,
    statusLabel,
    signalRows: [
      {
        label: "轨道 -> 网络",
        value: `${activeAccessLinks} 条接入`,
        detail: `${activeSpaceLinks} 条星间链路参与拓扑`
      },
      {
        label: "网络 -> 算力",
        value: `${availableRoutes.length}/${snapshot.routes.length} 条路由`,
        detail: `${waitingForNetwork} 个任务等待网络可达`
      },
      {
        label: "算力 -> 网络",
        value: formatPercent(averageComputeLoad),
        detail: `${busyComputeNodes} 个忙碌节点反馈容量`
      }
    ]
  };
}

function couplingStatusLabel(signals: {
  activeAccessLinks: number;
  availableRoutes: number;
  busyComputeNodes: number;
  computeNodes: number;
  waitingForNetwork: number;
}): string {
  if (signals.activeAccessLinks === 0 || signals.computeNodes === 0) {
    return "等待初始化";
  }
  if (signals.waitingForNetwork > 0) {
    return "网络等待";
  }
  if (signals.busyComputeNodes > 0) {
    return "负载反馈";
  }
  if (signals.availableRoutes > 0) {
    return "闭环稳定";
  }
  return "等待业务";
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

function formatPercent(value: number): string {
  return `${(value * 100).toFixed(0)}%`;
}
