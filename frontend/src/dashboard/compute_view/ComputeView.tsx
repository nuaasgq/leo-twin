import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import { memo } from "react";

import { WorldSnapshot } from "../../state/snapshot_engine";
import { KpiPanel } from "../kpi_panel/KpiPanel";

export const ComputeView = memo(function ComputeView({ snapshot }: { snapshot: WorldSnapshot }) {
  const kpis = snapshot.metrics_summary.compute;
  const chartData = [
    { name: "运行中", value: kpis.runningTasks },
    { name: "已完成", value: kpis.finishedTasks },
    { name: "超时", value: kpis.deadlineMissedTasks }
  ];

  return (
    <section className="dashboard-section" aria-label="算力指标">
      <div className="section-title">算力</div>
      <div className="kpi-grid">
        <KpiPanel label="队列" value={String(kpis.taskQueueLength)} />
        <KpiPanel label="成功率" value={`${(kpis.executionSuccessRate * 100).toFixed(1)}%`} />
        <KpiPanel label="超时" value={String(kpis.deadlineMissedTasks)} />
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
