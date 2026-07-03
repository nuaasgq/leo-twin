import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { ObservabilityState, selectNetworkKpis } from "../../stream/state_store";
import { KpiPanel } from "../kpi_panel/KpiPanel";

export function NetworkView({ state }: { state: ObservabilityState }) {
  const kpis = selectNetworkKpis(state);
  const chartData = Array.from(state.links.values()).slice(0, 24).map((link) => ({
    id: `${link.source_id}->${link.target_id}`,
    latency: link.latency,
    capacity: link.capacity
  }));

  return (
    <section className="dashboard-section" aria-label="Network KPI">
      <div className="section-title">Network</div>
      <div className="kpi-grid">
        <KpiPanel label="Latency" value={`${kpis.latency.toFixed(2)} ms`} />
        <KpiPanel label="Throughput" value={`${kpis.throughput.toFixed(1)}`} />
        <KpiPanel label="Utilization" value={`${(kpis.linkUtilization * 100).toFixed(1)}%`} />
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
}
