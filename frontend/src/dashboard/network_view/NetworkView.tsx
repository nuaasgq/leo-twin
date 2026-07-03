import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { memo } from "react";

import { WorldSnapshot } from "../../state/snapshot_engine";
import { KpiPanel } from "../kpi_panel/KpiPanel";

export const NetworkView = memo(function NetworkView({ snapshot }: { snapshot: WorldSnapshot }) {
  const kpis = snapshot.metrics_summary.network;
  const chartData = kpis.series;

  return (
    <section className="dashboard-section" aria-label="网络指标">
      <div className="section-title">网络</div>
      <div className="kpi-grid">
        <KpiPanel label="时延" value={`${kpis.latency.toFixed(2)} ms`} />
        <KpiPanel label="吞吐量" value={`${kpis.throughput.toFixed(1)}`} />
        <KpiPanel label="利用率" value={`${(kpis.linkUtilization * 100).toFixed(1)}%`} />
      </div>
      <div className="chart-strip">
        <ResponsiveContainer width="100%" height={128}>
          <BarChart data={chartData}>
            <XAxis dataKey="id" hide />
            <YAxis width={36} />
            <Tooltip />
            <Bar dataKey="latency" fill="#39a7ff" radius={[2, 2, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
});
