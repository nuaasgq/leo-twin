import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import { memo } from "react";

import { WorldSnapshot } from "../../state/snapshot_engine";
import { KpiPanel } from "../kpi_panel/KpiPanel";

export const ComputeView = memo(function ComputeView({ snapshot }: { snapshot: WorldSnapshot }) {
  const kpis = snapshot.metrics_summary.compute;
  const chartData = [
    { name: "Running", value: kpis.runningTasks },
    { name: "Finished", value: kpis.finishedTasks }
  ];

  return (
    <section className="dashboard-section" aria-label="Compute KPI">
      <div className="section-title">Compute</div>
      <div className="kpi-grid">
        <KpiPanel label="Queue" value={String(kpis.taskQueueLength)} />
        <KpiPanel label="Success" value={`${(kpis.executionSuccessRate * 100).toFixed(1)}%`} />
      </div>
      <div className="chart-strip compact">
        <ResponsiveContainer width="100%" height={112}>
          <PieChart>
            <Pie data={chartData} dataKey="value" nameKey="name" outerRadius={42}>
              <Cell fill="#f5a623" />
              <Cell fill="#45d483" />
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
});
