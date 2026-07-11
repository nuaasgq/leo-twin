import { memo } from "react";
import type { MouseEvent } from "react";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";

import type {
  GeneratedScenarioConfig,
  RuntimeStatusPayload
} from "../../core/event_types";
import type { WorldSnapshot } from "../../state/snapshot_engine";

export interface UserOverviewSummary {
  statusLabel: string;
  progressPercent: number;
  satelliteCount: number;
  userCount: number;
  activeLinkCount: number;
  availableRouteCount: number;
  totalRouteCount: number;
  throughputMbps: number;
  latencyMs: number;
  lossPercent: number;
  jitterMs: number;
  computeUtilizationPercent: number;
  runningTaskCount: number;
  finishedTaskCount: number;
  networkSeries: readonly {
    simTime: number;
    throughputMbps: number;
    latencyMs: number;
    lossPercent: number;
    jitterMs: number;
  }[];
}

export const UserOverview = memo(function UserOverview({
  snapshot,
  runtimeStatus,
  generatedConfig,
  displaySimTime,
  displayEventCount,
  onNavigateControl,
  onShowAdvanced
}: {
  snapshot: WorldSnapshot;
  runtimeStatus: RuntimeStatusPayload;
  generatedConfig: GeneratedScenarioConfig | null;
  displaySimTime: number;
  displayEventCount: number;
  onNavigateControl: (event: MouseEvent<HTMLAnchorElement>) => void;
  onShowAdvanced: () => void;
}) {
  const summary = buildUserOverviewSummary(snapshot, runtimeStatus, generatedConfig);
  const duration = Math.max(0, runtimeStatus.duration);

  return (
    <section className="user-overview" aria-label="运行概览">
      <header className="user-overview-header">
        <div>
          <span className="surface-kicker">实时运行概览</span>
          <h1>卫星网络运行态势</h1>
          <p>集中查看仿真进度、网络质量、业务运行和算力使用情况。</p>
        </div>
        <div className="user-overview-actions">
          <a href="/" className="data-panel-action" onClick={onNavigateControl}>
            返回仿真控制
          </a>
          <button type="button" className="user-overview-secondary" onClick={onShowAdvanced}>
            高级诊断
          </button>
        </div>
      </header>

      <section className="user-overview-run" aria-label="仿真运行状态">
        <div className="user-overview-run-state">
          <span>当前状态</span>
          <strong>{summary.statusLabel}</strong>
        </div>
        <div className="user-overview-progress">
          <div>
            <span>仿真进度</span>
            <strong>{summary.progressPercent.toFixed(0)}%</strong>
          </div>
          <progress value={summary.progressPercent} max="100" />
          <small>
            {displaySimTime.toFixed(1)} / {duration.toFixed(1)} 秒
          </small>
        </div>
        <div className="user-overview-run-meta">
          <span>卫星 {summary.satelliteCount}</span>
          <span>用户 {summary.userCount}</span>
          <span>事件 {displayEventCount.toLocaleString("zh-CN")}</span>
        </div>
      </section>

      <div className="user-overview-kpis" aria-label="用户核心指标">
        <OverviewKpi label="全网吞吐量" value={`${summary.throughputMbps.toFixed(1)} Mbps`} />
        <OverviewKpi label="平均时延" value={`${summary.latencyMs.toFixed(1)} ms`} />
        <OverviewKpi label="丢包率" value={`${summary.lossPercent.toFixed(2)}%`} />
        <OverviewKpi label="网络抖动" value={`${summary.jitterMs.toFixed(1)} ms`} />
        <OverviewKpi
          label="可用路由"
          value={`${summary.availableRouteCount} / ${summary.totalRouteCount}`}
        />
        <OverviewKpi label="活动链路" value={String(summary.activeLinkCount)} />
        <OverviewKpi
          label="算力使用率"
          value={`${summary.computeUtilizationPercent.toFixed(1)}%`}
        />
        <OverviewKpi
          label="计算任务"
          value={`${summary.runningTaskCount} 运行`}
          detail={`${summary.finishedTaskCount} 已完成`}
        />
      </div>

      <div className="user-overview-charts">
        <OverviewTrend
          title="全网吞吐量"
          unit="Mbps"
          data={summary.networkSeries}
          lines={[{ dataKey: "throughputMbps", name: "吞吐量", color: "#64d6c1" }]}
        />
        <OverviewTrend
          title="网络质量变化"
          unit="时延与抖动（ms）"
          data={summary.networkSeries}
          lines={[
            { dataKey: "latencyMs", name: "时延", color: "#67b8ff" },
            { dataKey: "jitterMs", name: "抖动", color: "#f0bf65" }
          ]}
        />
      </div>

      <section className="user-overview-business" aria-label="业务与资源概况">
        <div>
          <span>通信业务</span>
          <strong>{summary.availableRouteCount > 0 ? "业务路径可用" : "等待可用路径"}</strong>
          <small>{summary.activeLinkCount} 条链路正在提供连接</small>
        </div>
        <div>
          <span>计算业务</span>
          <strong>{summary.runningTaskCount > 0 ? "任务执行中" : "当前无运行任务"}</strong>
          <small>{summary.finishedTaskCount} 个任务已完成</small>
        </div>
        <div>
          <span>资源池</span>
          <strong>{summary.computeUtilizationPercent.toFixed(1)}% 已使用</strong>
          <small>{snapshot.compute_nodes.length} 个卫星算力节点</small>
        </div>
      </section>
    </section>
  );
});

function OverviewTrend({
  title,
  unit,
  data,
  lines
}: {
  title: string;
  unit: string;
  data: UserOverviewSummary["networkSeries"];
  lines: readonly { dataKey: string; name: string; color: string }[];
}) {
  return (
    <section className="user-overview-chart" aria-label={`${title}趋势`}>
      <div className="user-overview-chart-title">
        <strong>{title}</strong>
        <span>{unit}</span>
      </div>
      <ResponsiveContainer width="100%" height={230}>
        <LineChart data={data}>
          <CartesianGrid stroke="#24313a" vertical={false} />
          <XAxis dataKey="simTime" tick={{ fill: "#8ea0aa", fontSize: 10 }} />
          <YAxis tick={{ fill: "#8ea0aa", fontSize: 10 }} width={46} />
          <Tooltip />
          {lines.map((line) => (
            <Line
              key={line.dataKey}
              type="monotone"
              dataKey={line.dataKey}
              name={line.name}
              stroke={line.color}
              strokeWidth={2}
              dot={false}
              isAnimationActive={false}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </section>
  );
}

function OverviewKpi({ label, value, detail }: { label: string; value: string; detail?: string }) {
  return (
    <section className="user-overview-kpi" aria-label={label}>
      <span>{label}</span>
      <strong>{value}</strong>
      {detail ? <small>{detail}</small> : null}
    </section>
  );
}

export function buildUserOverviewSummary(
  snapshot: WorldSnapshot,
  runtimeStatus: RuntimeStatusPayload,
  generatedConfig: GeneratedScenarioConfig | null
): UserOverviewSummary {
  const metrics = runtimeStatus.metrics_summary ?? {};
  const latestSeries = snapshot.metrics_summary.network.kpiSeries?.at(-1);
  const computeUtilizationPercent =
    snapshot.compute_nodes.length === 0
      ? 0
      : (snapshot.compute_nodes.reduce((sum, node) => sum + clamp(node.load_ratio, 0, 1), 0) /
          snapshot.compute_nodes.length) *
        100;
  const duration = Math.max(0, runtimeStatus.duration);
  const simTime = Math.max(0, runtimeStatus.current_sim_time ?? snapshot.last_sim_time);

  return {
    statusLabel: runtimeStatusLabel(runtimeStatus.status),
    progressPercent: duration > 0 ? clamp((simTime / duration) * 100, 0, 100) : 0,
    satelliteCount: generatedConfig?.satellite_count ?? snapshot.satellites.length,
    userCount: generatedConfig?.user_count ?? snapshot.ground_users.length,
    activeLinkCount: snapshot.links.filter((link) => link.availability).length,
    availableRouteCount: snapshot.routes.filter((route) => route.available).length,
    totalRouteCount: snapshot.routes.length,
    throughputMbps: metricNumber(
      metrics,
      "network_quality_effective_throughput_mbps",
      latestSeries?.throughputMbps ?? snapshot.metrics_summary.network.throughput
    ),
    latencyMs:
      metricNumber(
        metrics,
        "network_quality_effective_latency_avg_s",
        (latestSeries?.latencyMs ?? snapshot.metrics_summary.network.latency) / 1000
      ) * 1000,
    lossPercent:
      metricNumber(
        metrics,
        "network_quality_effective_loss_proxy_rate",
        (latestSeries?.lossPercent ?? 0) / 100
      ) * 100,
    jitterMs:
      metricNumber(
        metrics,
        "network_quality_effective_delay_variation_proxy_s",
        (latestSeries?.jitterMs ?? 0) / 1000
      ) * 1000,
    computeUtilizationPercent,
    runningTaskCount: snapshot.metrics_summary.compute.runningTasks,
    finishedTaskCount: snapshot.metrics_summary.compute.finishedTasks,
    networkSeries: (snapshot.metrics_summary.network.kpiSeries ?? []).slice(-60)
  };
}

function metricNumber(
  metrics: RuntimeStatusPayload["metrics_summary"],
  key: string,
  fallback: number
): number {
  const value = metrics?.[key];
  return typeof value === "number" && Number.isFinite(value) ? value : fallback;
}

function runtimeStatusLabel(status: RuntimeStatusPayload["status"]): string {
  const labels: Record<RuntimeStatusPayload["status"], string> = {
    UNINITIALIZED: "未初始化",
    INITIALIZED: "准备就绪",
    STOPPED: "已停止",
    RUNNING: "运行中",
    PAUSED: "已暂停",
    COMPLETED: "已完成",
    ERROR: "运行异常"
  };
  return labels[status];
}

function clamp(value: number, minimum: number, maximum: number): number {
  return Math.min(maximum, Math.max(minimum, value));
}
