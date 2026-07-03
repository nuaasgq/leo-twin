import { memo } from "react";

import { MetricRecord } from "../../core/event_types";
import { WorldSnapshot } from "../../state/snapshot_engine";
import { KpiPanel } from "../kpi_panel/KpiPanel";

export interface GroundTrackSummary {
  observedSatellites: number;
  averageAltitudeKm: number;
  maxAltitudeKm: number;
  latitudeSpanDeg: number;
  rows: readonly GroundTrackRow[];
}

export interface GroundTrackRow {
  satelliteId: string;
  latitudeDeg: number;
  longitudeDeg: number;
  altitudeKm: number;
}

type GroundTrackSnapshot = Pick<WorldSnapshot, "metrics">;

export const GroundTrackPanel = memo(function GroundTrackPanel({
  snapshot
}: {
  snapshot: WorldSnapshot;
}) {
  const summary = buildGroundTrackSummary(snapshot);

  return (
    <section className="dashboard-section ground-track-panel" aria-label="轨道地面投影">
      <div className="section-title">轨道地面投影</div>
      <div className="kpi-grid wide">
        <KpiPanel label="观测卫星" value={String(summary.observedSatellites)} />
        <KpiPanel label="平均高度" value={`${summary.averageAltitudeKm.toFixed(1)} km`} />
        <KpiPanel label="最高高度" value={`${summary.maxAltitudeKm.toFixed(1)} km`} />
        <KpiPanel label="纬度跨度" value={`${summary.latitudeSpanDeg.toFixed(1)}°`} />
      </div>
      <div className="ground-track-table" aria-label="地面投影明细">
        {summary.rows.map((row) => (
          <div className="ground-track-row" key={row.satelliteId}>
            <span>{row.satelliteId}</span>
            <span>{row.latitudeDeg.toFixed(2)}°</span>
            <span>{row.longitudeDeg.toFixed(2)}°</span>
            <strong>{row.altitudeKm.toFixed(1)} km</strong>
          </div>
        ))}
      </div>
    </section>
  );
});

export function buildGroundTrackSummary(
  snapshot: GroundTrackSnapshot
): GroundTrackSummary {
  const rows = groundTrackRows(snapshot.metrics);
  const altitudes = rows.map((row) => row.altitudeKm);
  const latitudes = rows.map((row) => row.latitudeDeg);
  return {
    observedSatellites: rows.length,
    averageAltitudeKm: average(altitudes),
    maxAltitudeKm: Math.max(...altitudes, 0),
    latitudeSpanDeg:
      latitudes.length === 0 ? 0 : Math.max(...latitudes) - Math.min(...latitudes),
    rows: rows.slice(0, 6)
  };
}

function groundTrackRows(metrics: readonly MetricRecord[]): GroundTrackRow[] {
  const bySatellite = new Map<string, Partial<GroundTrackRow>>();
  for (const metric of metrics) {
    if (!isGroundTrackMetric(metric) || typeof metric.value !== "number") {
      continue;
    }
    const row = bySatellite.get(metric.entity_id) ?? { satelliteId: metric.entity_id };
    if (metric.metric_name === "satellite.latitude_deg") {
      row.latitudeDeg = metric.value;
    } else if (metric.metric_name === "satellite.longitude_deg") {
      row.longitudeDeg = metric.value;
    } else {
      row.altitudeKm = metric.value;
    }
    bySatellite.set(metric.entity_id, row);
  }
  return Array.from(bySatellite.values())
    .filter(isCompleteRow)
    .sort((left, right) => left.satelliteId.localeCompare(right.satelliteId));
}

function isGroundTrackMetric(metric: MetricRecord): boolean {
  return (
    metric.metric_name === "satellite.latitude_deg" ||
    metric.metric_name === "satellite.longitude_deg" ||
    metric.metric_name === "satellite.altitude_km"
  );
}

function isCompleteRow(row: Partial<GroundTrackRow>): row is GroundTrackRow {
  return (
    row.satelliteId !== undefined &&
    row.latitudeDeg !== undefined &&
    row.longitudeDeg !== undefined &&
    row.altitudeKm !== undefined
  );
}

function average(values: readonly number[]): number {
  if (values.length === 0) {
    return 0;
  }
  return values.reduce((total, value) => total + value, 0) / values.length;
}
