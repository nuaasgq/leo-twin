import { memo } from "react";

import { WorldSnapshot } from "../../state/snapshot_engine";
import { KpiPanel } from "../kpi_panel/KpiPanel";

export interface TopologyChangePanelSummary {
  activeSpaceLinks: number;
  activeAccessLinks: number;
  linkUpdateEvents: number;
  accessStartEvents: number;
  accessEndEvents: number;
  routeUpdateEvents: number;
  topologyEvents: number;
  churnBalance: number;
}

type TopologyChangeSnapshot = Pick<WorldSnapshot, "metrics_summary">;

export const TopologyChangePanel = memo(function TopologyChangePanel({
  snapshot
}: {
  snapshot: WorldSnapshot;
}) {
  const summary = buildTopologyChangeSummary(snapshot);

  return (
    <section className="dashboard-section topology-change-panel" aria-label="拓扑变化">
      <div className="section-title">拓扑变化</div>
      <div className="kpi-grid wide">
        <KpiPanel label="星间链路" value={String(summary.activeSpaceLinks)} />
        <KpiPanel label="接入/网关" value={String(summary.activeAccessLinks)} />
        <KpiPanel label="链路更新" value={String(summary.linkUpdateEvents)} />
        <KpiPanel label="接入开始" value={String(summary.accessStartEvents)} />
        <KpiPanel label="接入结束" value={String(summary.accessEndEvents)} />
        <KpiPanel label="路由更新" value={String(summary.routeUpdateEvents)} />
        <KpiPanel label="拓扑事件" value={String(summary.topologyEvents)} />
        <KpiPanel label="切换净值" value={String(summary.churnBalance)} />
      </div>
    </section>
  );
});

export function buildTopologyChangeSummary(
  snapshot: TopologyChangeSnapshot
): TopologyChangePanelSummary {
  const topology = snapshot.metrics_summary.network.topology;
  return {
    activeSpaceLinks: topology?.activeSpaceLinks ?? 0,
    activeAccessLinks: topology?.activeAccessLinks ?? 0,
    linkUpdateEvents: topology?.linkUpdateEvents ?? 0,
    accessStartEvents: topology?.accessStartEvents ?? 0,
    accessEndEvents: topology?.accessEndEvents ?? 0,
    routeUpdateEvents: topology?.routeUpdateEvents ?? 0,
    topologyEvents: topology?.topologyEvents ?? 0,
    churnBalance: (topology?.accessStartEvents ?? 0) - (topology?.accessEndEvents ?? 0)
  };
}
