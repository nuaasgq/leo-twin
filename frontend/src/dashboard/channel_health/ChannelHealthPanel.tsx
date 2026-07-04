import { memo } from "react";

import { LinkState } from "../../core/event_types";
import { WorldSnapshot } from "../../state/snapshot_engine";
import { KpiPanel } from "../kpi_panel/KpiPanel";

export interface ChannelHealthSummary {
  carrierFrequencyGhz: number;
  bandwidthMhz: number;
  rainRate: number;
  estimatedRainFadeDb: number;
  availableLinks: number;
  averageCapacity: number;
  weakestCapacity: number;
  averageRangeKm: number;
  freeSpacePathLossDb: number;
  estimatedSnrDb: number;
  spectralEfficiency: number;
  healthScore: number;
  rows: readonly ChannelLinkRow[];
}

export interface ChannelLinkRow {
  linkId: string;
  latency: number;
  capacity: number;
  status: string;
}

type ChannelHealthSnapshot = Pick<WorldSnapshot, "links" | "scenario_config">;

export const ChannelHealthPanel = memo(function ChannelHealthPanel({
  snapshot
}: {
  snapshot: WorldSnapshot;
}) {
  const summary = buildChannelHealthSummary(snapshot);

  return (
    <section className="dashboard-section channel-health-panel" aria-label="物理层与信道健康">
      <div className="section-title">物理层与信道</div>
      <div className="kpi-grid wide">
        <KpiPanel label="载波频率" value={`${summary.carrierFrequencyGhz.toFixed(1)} GHz`} />
        <KpiPanel label="信道带宽" value={`${summary.bandwidthMhz.toFixed(0)} MHz`} />
        <KpiPanel label="雨强" value={`${summary.rainRate.toFixed(1)} mm/h`} />
        <KpiPanel label="估算雨衰" value={`${summary.estimatedRainFadeDb.toFixed(2)} dB`} />
        <KpiPanel label="平均容量" value={`${summary.averageCapacity.toFixed(1)} Mbps`} />
        <KpiPanel label="估算距离" value={`${summary.averageRangeKm.toFixed(0)} km`} />
        <KpiPanel label="自由空间损耗" value={`${summary.freeSpacePathLossDb.toFixed(1)} dB`} />
        <KpiPanel label="估算SNR" value={`${summary.estimatedSnrDb.toFixed(1)} dB`} />
        <KpiPanel label="健康度" value={`${summary.healthScore}%`} />
      </div>
      <div className="channel-health-strip" aria-label="信道预算">
        <span>可用链路</span>
        <strong>{summary.availableLinks}</strong>
        <span>最低容量</span>
        <strong>{summary.weakestCapacity.toFixed(1)} Mbps</strong>
        <span>频谱效率</span>
        <strong>{summary.spectralEfficiency.toFixed(2)} bps/Hz</strong>
      </div>
      <div className="channel-table" aria-label="薄弱链路">
        {summary.rows.map((row) => (
          <div className="channel-table-row" key={row.linkId}>
            <span>{row.linkId}</span>
            <span>{row.latency.toFixed(3)} s</span>
            <span>{row.capacity.toFixed(1)} Mbps</span>
            <strong>{row.status}</strong>
          </div>
        ))}
      </div>
    </section>
  );
});

export function buildChannelHealthSummary(
  snapshot: ChannelHealthSnapshot
): ChannelHealthSummary {
  const channel = snapshot.scenario_config?.network;
  const carrierFrequencyGhz = (channel?.carrier_frequency_hz ?? 20_000_000_000) / 1_000_000_000;
  const bandwidthMhz = (channel?.channel_bandwidth_hz ?? 100_000_000) / 1_000_000;
  const rainRate = channel?.rain_rate_mm_h ?? 0;
  const rainCoefficient =
    channel?.rain_attenuation_coefficient_db_per_km_per_mm_h ?? 0;
  const rainPathKm = channel?.rain_effective_path_km ?? 0;
  const estimatedRainFadeDb = rainRate * rainCoefficient * rainPathKm;
  const availableLinks = snapshot.links.filter((link) => link.availability);
  const averageCapacity =
    availableLinks.length === 0
      ? 0
      : availableLinks.reduce((total, link) => total + link.capacity, 0) /
        availableLinks.length;
  const weakestCapacity =
    availableLinks.length === 0
      ? 0
      : Math.min(...availableLinks.map((link) => link.capacity));
  const averageLatency =
    availableLinks.length === 0
      ? 0
      : availableLinks.reduce((total, link) => total + link.latency, 0) /
        availableLinks.length;
  const averageRangeKm = averageLatency * 299_792.458;
  const spectralEfficiency = bandwidthMhz <= 0 ? 0 : averageCapacity / bandwidthMhz;
  const freeSpacePathLossDb =
    averageRangeKm <= 0
      ? 0
      : 92.45 + 20 * Math.log10(carrierFrequencyGhz) + 20 * Math.log10(averageRangeKm);
  const estimatedSnrDb =
    spectralEfficiency <= 0 ? 0 : 10 * Math.log10(Math.pow(2, spectralEfficiency) - 1);

  return {
    carrierFrequencyGhz,
    bandwidthMhz,
    rainRate,
    estimatedRainFadeDb,
    availableLinks: availableLinks.length,
    averageCapacity,
    weakestCapacity,
    averageRangeKm,
    freeSpacePathLossDb,
    estimatedSnrDb,
    spectralEfficiency,
    healthScore: channelHealthScore({
      hasLinks: availableLinks.length > 0,
      spectralEfficiency,
      estimatedRainFadeDb
    }),
    rows: availableLinks
      .slice()
      .sort(compareWeakLinks)
      .slice(0, 5)
      .map(linkToRow)
  };
}

function channelHealthScore(signals: {
  hasLinks: boolean;
  spectralEfficiency: number;
  estimatedRainFadeDb: number;
}): number {
  if (!signals.hasLinks) {
    return 0;
  }
  const efficiencyScore = Math.min(1, Math.max(0, signals.spectralEfficiency / 1.5));
  const rainScore = Math.min(1, Math.max(0, 1 - signals.estimatedRainFadeDb / 20));
  return Math.round((0.45 + 0.35 * efficiencyScore + 0.2 * rainScore) * 100);
}

function compareWeakLinks(left: LinkState, right: LinkState): number {
  const byCapacity = left.capacity - right.capacity;
  if (byCapacity !== 0) {
    return byCapacity;
  }
  const byLatency = right.latency - left.latency;
  if (byLatency !== 0) {
    return byLatency;
  }
  return `${left.source_id}->${left.target_id}`.localeCompare(
    `${right.source_id}->${right.target_id}`
  );
}

function linkToRow(link: LinkState): ChannelLinkRow {
  return {
    linkId: `${link.source_id} -> ${link.target_id}`,
    latency: link.latency,
    capacity: link.capacity,
    status: link.availability ? "可用" : "不可用"
  };
}
