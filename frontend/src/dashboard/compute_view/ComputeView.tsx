import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import { memo } from "react";

import { MetricRecord } from "../../core/event_types";
import { WorldSnapshot } from "../../state/snapshot_engine";
import { KpiPanel } from "../kpi_panel/KpiPanel";

export interface ComputeDurationSummary {
  sampleCount: number;
  averageDuration: number;
  maxDuration: number;
}

export const ComputeView = memo(function ComputeView({ snapshot }: { snapshot: WorldSnapshot }) {
  const kpis = snapshot.metrics_summary.compute;
  const durations = buildComputeDurationSummary(snapshot.metrics);
  const chartData = [
    { name: "运行中", value: kpis.runningTasks },
    { name: "已完成", value: kpis.finishedTasks },
    { name: "超时", value: kpis.deadlineMissedTasks }
  ];

  return (
    <section className="dashboard-section" aria-label="算力指标">
      <div className="section-title">算力</div>
      <div className="kpi-grid wide">
        <KpiPanel label="队列" value={String(kpis.taskQueueLength)} />
        <KpiPanel label="成功率" value={`${(kpis.executionSuccessRate * 100).toFixed(1)}%`} />
        <KpiPanel label="超时" value={String(kpis.deadlineMissedTasks)} />
        <KpiPanel label="平均耗时" value={`${durations.averageDuration.toFixed(2)} s`} />
        <KpiPanel label="最长耗时" value={`${durations.maxDuration.toFixed(2)} s`} />
        <KpiPanel label="耗时样本" value={String(durations.sampleCount)} />
      </div>
      <div className="chart-strip compact">
        <ResponsiveContainer width="100%" height={112}>
          <PieChart>
            <Pie data={chartData} dataKey="value" nameKey="name" outerRadius={42}>
              <Cell fill="#f5a623" />
              <Cell fill="#45d483" />
              <Cell fill="#ef5b5b" />
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
});

export function buildComputeDurationSummary(
  metrics: readonly MetricRecord[]
): ComputeDurationSummary {
  const durations = metrics
    .filter(
      (metric) => metric.metric_name === "task.duration" && typeof metric.value === "number"
    )
    .map((metric) => metric.value as number);
  if (durations.length === 0) {
    return {
      sampleCount: 0,
      averageDuration: 0,
      maxDuration: 0
    };
  }
  return {
    sampleCount: durations.length,
    averageDuration: durations.reduce((total, value) => total + value, 0) / durations.length,
    maxDuration: Math.max(...durations)
  };
}
