import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { ObservabilityState, selectOrbitKpis } from "../../stream/state_store";
import { KpiPanel } from "../kpi_panel/KpiPanel";

export function OrbitPanel({ state }: { state: ObservabilityState }) {
  const kpis = selectOrbitKpis(state);
  const series = Array.from(state.satellites.values()).slice(0, 64).map((satellite, index) => ({
    index,
    active: satellite.status.toLowerCase() === "offline" ? 0 : 1
  }));

  return (
    <section className="dashboard-section" aria-label="Orbit KPI">
      <div className="section-title">Orbit</div>
      <div className="kpi-grid">
        <KpiPanel label="Active" value={String(kpis.activeSatellites)} />
        <KpiPanel label="Coverage" value={`${(kpis.coverageRatio * 100).toFixed(1)}%`} />
      </div>
      <div className="chart-strip compact">
        <ResponsiveContainer width="100%" height={112}>
          <LineChart data={series}>
            <XAxis dataKey="index" hide />
            <YAxis width={36} />
            <Tooltip />
            <Line type="stepAfter" dataKey="active" stroke="#7bdff2" dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
