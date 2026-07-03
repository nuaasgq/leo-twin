export interface KpiPanelProps {
  label: string;
  value: string;
  detail?: string;
}

export function KpiPanel({ label, value, detail }: KpiPanelProps) {
  return (
    <section className="kpi-panel" aria-label={label}>
      <div className="kpi-label">{label}</div>
      <div className="kpi-value">{value}</div>
      {detail ? <div className="kpi-detail">{detail}</div> : null}
    </section>
  );
}
