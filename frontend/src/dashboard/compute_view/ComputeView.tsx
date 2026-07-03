import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

import { ObservabilityState, selectComputeKpis } from "../../stream/state_store";
import { KpiPanel } from "../kpi_panel/KpiPanel";

export function ComputeView({ state }: { state: ObservabilityState }) {
  const kpis = selectComputeKpis(state);
  const tasks = Array.from(state.tasks.values());
  const finished = tasks.filter((task) => task.status.toLowerCase() === "finished").length;
  const running = tasks.filter((task) => task.status.toLowerCase() !== "finished").length;
  const chartData = [
    { name: "Running", value: running },
    { name: "Finished", value: finished }
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
}
