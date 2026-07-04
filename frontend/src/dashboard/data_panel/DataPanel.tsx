import { memo } from "react";

import {
  GeneratedScenarioConfig,
  RuntimeStatusPayload
} from "../../core/event_types";
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

export const DataPanel = memo(function DataPanel({
  snapshot,
  runtimeStatus,
  generatedConfig
}: {
  snapshot: WorldSnapshot;
  runtimeStatus: RuntimeStatusPayload;
  generatedConfig: GeneratedScenarioConfig | null;
}) {
  const summary = buildDataPanelSummary(snapshot);
  const configuredScale = generatedConfig
    ? `${generatedConfig.satellite_count} 星 / ${generatedConfig.user_count} 用户`
    : "等待初始化";
  const runtimeProgress = buildDataPanelRuntimeProgress(
    Math.max(summary.simTime, runtimeStatus.current_sim_time ?? 0),
    runtimeStatus.duration
  );

  return (
    <section className="data-panel" aria-label="独立数据态势面板">
      <div className="data-panel-hero">
        <div className="data-panel-title-block">
          <div className="surface-kicker">全链路实时观测</div>
          <h1>数据态势面板</h1>
          <p>轨道、网络、算力与事件流联动状态。该页面独立承载数据分析，不与三维控制台混排。</p>
          <div className="data-panel-actions">
            <a href="/" className="data-panel-action">
              返回三维控制台
            </a>
          </div>
        </div>
        <div className="data-panel-runtime">
          <div>
            <span>运行状态</span>
            <strong>{runtimeStatusLabel(runtimeStatus.status)}</strong>
          </div>
          <div>
            <span>仿真模式</span>
            <strong>{runtimeModeLabel(runtimeStatus.mode)}</strong>
          </div>
          <div>
            <span>速度</span>
            <strong>{runtimeStatus.speed_factor}x</strong>
          </div>
          <div>
            <span>配置规模</span>
            <strong>{configuredScale}</strong>
          </div>
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

      <div className="data-panel-section-title">跨域联动分析</div>
      <div className="data-panel-grid">
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

function average(values: readonly number[]): number {
  if (values.length === 0) {
    return 0;
  }
  return values.reduce((total, value) => total + value, 0) / values.length;
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

function runtimeStatusLabel(status: RuntimeStatusPayload["status"]): string {
  if (status === "RUNNING") {
    return "运行中";
  }
  if (status === "PAUSED") {
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
