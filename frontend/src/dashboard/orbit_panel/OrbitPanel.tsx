import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { memo } from "react";

import { WorldSnapshot } from "../../state/snapshot_engine";
import { KpiPanel } from "../kpi_panel/KpiPanel";

export const OrbitPanel = memo(function OrbitPanel({ snapshot }: { snapshot: WorldSnapshot }) {
  const kpis = snapshot.metrics_summary.orbit;

  return (
    <section className="dashboard-section" aria-label="轨道指标">
      <div className="section-title">轨道</div>
      <div className="kpi-grid">
        <KpiPanel label="活跃卫星" value={String(kpis.activeSatellites)} />
        <KpiPanel label="覆盖率" value={`${(kpis.coverageRatio * 100).toFixed(1)}%`} />
      </div>
      <div className="chart-strip compact">
        <ResponsiveContainer width="100%" height={112}>
          <LineChart data={kpis.series}>
            <XAxis dataKey="index" hide />
            <YAxis width={36} />
            <Tooltip />
            <Line type="stepAfter" dataKey="active" stroke="#7bdff2" dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
});
