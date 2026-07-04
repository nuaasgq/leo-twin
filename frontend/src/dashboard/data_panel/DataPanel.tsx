import { memo, type MouseEvent } from "react";
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
  GeneratedScenarioConfig,
  TrafficDemandSummary,
  RuntimeKpiTimeSeriesV1,
  RuntimeMetricsSummary,
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
  generatedConfig,
  displaySimTime,
  displayEventCount,
  onNavigateControl
}: {
  snapshot: WorldSnapshot;
  runtimeStatus: RuntimeStatusPayload;
  generatedConfig: GeneratedScenarioConfig | null;
  displaySimTime: number;
  displayEventCount: number;
  onNavigateControl: (event: MouseEvent<HTMLAnchorElement>) => void;
}) {
  const summary = buildDataPanelDisplaySummary(
    buildDataPanelSummary(snapshot),
    displaySimTime,
    displayEventCount
  );
  const constellation = generatedConfig?.backend_summary?.derived_constellation_summary;
  const configuredScale = generatedConfig
    ? constellation
      ? `${generatedConfig.satellite_count} 星 / ${constellation.plane_count} 面 / ${generatedConfig.user_count} 用户`
      : `${generatedConfig.satellite_count} 星 / ${generatedConfig.user_count} 用户`
    : "等待初始化";
  const trafficSummary = generatedConfig?.backend_summary?.traffic_demand_summary;
  const trafficDisplay = buildDataPanelTrafficDisplay(trafficSummary);
  const runtimeProgress = buildDataPanelRuntimeProgress(summary.simTime, runtimeStatus.duration);
  const telemetry = buildDataPanelTelemetry(
    snapshot,
    summary.simTime,
    runtimeStatus.metrics_summary,
    runtimeStatus.kpi_time_series_v1
  );
  const networkKpiSource = buildDataPanelNetworkKpiSource(
    snapshot,
    runtimeStatus.metrics_summary,
    runtimeStatus.kpi_time_series_v1
  );
  const networkFormulaInputs = buildDataPanelNetworkFormulaInputs(
    runtimeStatus.metrics_summary
  );
  const routeConstraints = buildDataPanelRouteConstraints(
    snapshot,
    runtimeStatus.metrics_summary
  );
  const latestTelemetry = telemetry[telemetry.length - 1];
  const computePool = buildComputeResourcePool(
    snapshot,
    runtimeStatus.metrics_summary
  );
  const topComputeNodes = buildTopComputeNodeRows(snapshot);

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
          <div>
            <span>业务类型</span>
            <strong>{trafficDisplay.label}</strong>
            {trafficDisplay.note ? (
              <small className="data-panel-runtime-note">{trafficDisplay.note}</small>
            ) : null}
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
        </section>

        <section className="dashboard-section data-panel-chart" aria-label="算力消耗曲线">
          <div className="section-title">FP32 算力消耗</div>
          <div className="data-panel-chart-kpis compact">
            <KpiPanel
              label="已消耗"
              value={`${latestTelemetry.computeUsedTflops.toFixed(1)} TFLOPS`}
            />
            <KpiPanel
              label="资源池"
              value={`${computePool.totalTflops.toFixed(1)} TFLOPS`}
              detail={`单精度 FP32 / ${computePool.usedPercent.toFixed(1)}%`}
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
                  dataKey="computeUsedTflops"
                  name="已消耗 TFLOPS"
                  stroke="#f2bd45"
                  fill="#f2bd4540"
                  strokeWidth={2}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </section>

        <section className="dashboard-section data-panel-chart" aria-label="算力资源池消耗饼图">
          <div className="section-title">FP32 资源池</div>
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

export interface DataPanelTelemetryPoint {
  timeLabel: string;
  simTime: number;
  throughputMbps: number;
  latencyMs: number;
  lossPercent: number;
  jitterMs: number;
  computeUsedTflops: number;
}

export interface NetworkQualityKpis {
  source: DataPanelNetworkKpiSource["sourceLabel"];
  throughputMbps: number;
  latencyMs: number;
  lossPercent: number;
  jitterMs: number;
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
  const computePool = buildComputeResourcePool(snapshot);
  const computeUsedTflops =
    backendComputeUsedGflops !== undefined
      ? backendComputeUsedGflops / 1000
      : computePool.usedTflops;
  const runtimeKpiSeries = backendKpiTimeSeries?.samples ?? [];
  if (runtimeKpiSeries.length > 0) {
    return runtimeKpiSeries.slice(-24).map((point) => ({
      timeLabel: formatDurationCompact(point.sim_time),
      simTime: point.sim_time,
      throughputMbps: roundMetric(point.network_effective_throughput_mbps),
      latencyMs: roundMetric(point.network_effective_latency_s * 1000),
      lossPercent: roundMetric(point.network_effective_loss_proxy_rate * 100),
      jitterMs: roundMetric(point.network_effective_delay_variation_s * 1000),
      computeUsedTflops: roundMetric(point.compute_resource_used_gflops_fp32 / 1000)
    }));
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
        computeUsedTflops: roundMetric(computeUsedTflops * envelope)
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
      computeUsedTflops: roundMetric(computeUsedTflops * envelope)
    };
  });
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

export function buildTopComputeNodeRows(
  snapshot: WorldSnapshot,
  limit = 5
): readonly TopComputeNodeRow[] {
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
    })
    .sort(compareTopComputeNodeRows)
    .slice(0, Math.max(0, limit));
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

function formatMetricMbps(value: number): string {
  return `${formatMetricValue(value)} Mbps`;
}

function formatRatioPercent(value: number): string {
  return `${formatMetricValue(value * 100)}%`;
}

function formatMetricValue(value: number): string {
  return value.toLocaleString("zh-CN", {
    maximumFractionDigits: 1,
    minimumFractionDigits: 0
  });
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
  metrics: RuntimeMetricsSummary | null | undefined
): string {
  const note = metrics?.network_quality_proxy_note;
  const provenance = formatNetworkQualityProvenanceNote(metrics);
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
  metrics: RuntimeMetricsSummary | null | undefined
): string {
  const throughput = metricString(metrics, "network_quality_throughput_source_label");
  const latency = metricString(metrics, "network_quality_latency_source_label");
  const loss = metricString(metrics, "network_quality_loss_source_label");
  const jitter = metricString(
    metrics,
    "network_quality_delay_variation_source_label"
  );
  if (!throughput && !latency && !loss && !jitter) {
    return "";
  }
  return `来源：吞吐量 ${throughput ?? "未声明"}；时延 ${
    latency ?? "未声明"
  }；丢包 ${loss ?? "未声明"}；抖动 ${jitter ?? "未声明"}。`;
}

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
    note: traffic.lifecycle_note ?? traffic.compatibility_note ?? null
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

type SnapshotRoute = WorldSnapshot["routes"][number];
type SnapshotLink = WorldSnapshot["links"][number];

export function buildDataPanelNetworkKpiSource(
  snapshot: WorldSnapshot,
  backendMetrics: RuntimeMetricsSummary | null | undefined = undefined,
  backendKpiTimeSeries: RuntimeKpiTimeSeriesV1 | null | undefined = undefined
): DataPanelNetworkKpiSource {
  const backendNote = formatNetworkQualityProxyNote(backendMetrics);
  if ((backendKpiTimeSeries?.samples ?? []).length > 0) {
    return {
      sourceLabel: "后端实时 KPI 序列",
      modelNote: backendNote,
      caveats: buildDataPanelNetworkKpiCaveats(backendMetrics, backendKpiTimeSeries)
    };
  }
  if ((snapshot.metrics_summary.network.kpiSeries ?? []).length > 0) {
    return {
      sourceLabel: "状态快照 KPI 序列",
      modelNote: backendNote,
      caveats: buildDataPanelNetworkKpiCaveats(backendMetrics)
    };
  }
  if (hasBackendNetworkQualityMetrics(backendMetrics)) {
    return {
      sourceLabel: "后端指标摘要",
      modelNote: backendNote,
      caveats: buildDataPanelNetworkKpiCaveats(backendMetrics)
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
  backendKpiTimeSeries: RuntimeKpiTimeSeriesV1 | null | undefined = undefined
): readonly string[] {
  if (metrics === null || metrics === undefined) {
    return buildDataPanelKpiTailCaveats(backendKpiTimeSeries);
  }
  const caveats: string[] = [];
  if (metricString(metrics, "network_quality_metric_model") === "FLOW_LEVEL_PROXY") {
    caveats.push("指标模型：后端流级代理");
  }
  const lossReason = metricString(metrics, "network_quality_loss_zero_reason_label");
  if (lossReason && lossReason !== "当前代理指标为正值") {
    caveats.push(`丢包率：${lossReason}`);
  }
  const jitterReason = metricString(
    metrics,
    "network_quality_delay_variation_zero_reason_label"
  );
  if (jitterReason && jitterReason !== "当前代理指标为正值") {
    caveats.push(`抖动：${jitterReason}`);
  }
  caveats.push(...buildDataPanelKpiTailCaveats(backendKpiTimeSeries));
  return caveats;
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
