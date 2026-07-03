import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { ObservabilityState, selectSystemHealth } from "../../stream/state_store";
import { KpiPanel } from "../kpi_panel/KpiPanel";

export function SystemHealth({ state }: { state: ObservabilityState }) {
  const health = selectSystemHealth(state);
  const eventSeries = state.eventLog.slice(-80).map((event, index) => ({
    index,
    simTime: event.sim_time
  }));

  return (
    <section className="dashboard-section" aria-label="System health">
      <div className="section-title">System Health</div>
      <div className="kpi-grid">
        <KpiPanel label="Event Rate" value={health.eventRate.toFixed(2)} />
        <KpiPanel label="Load" value={`${(health.systemLoad * 100).toFixed(1)}%`} />
      </div>
      <div className="chart-strip compact">
        <ResponsiveContainer width="100%" height={112}>
          <AreaChart data={eventSeries}>
            <XAxis dataKey="index" hide />
            <YAxis width={36} />
            <Tooltip />
            <Area type="monotone" dataKey="simTime" stroke="#9bffcb" fill="#9bffcb33" />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
