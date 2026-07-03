import { memo } from "react";

import { LinkState, Route } from "../../core/event_types";
import { WorldSnapshot } from "../../state/snapshot_engine";
import { KpiPanel } from "../kpi_panel/KpiPanel";

export interface LinkProtocolSummary {
  activeLinks: number;
  availableRoutes: number;
  bestRouteId: string;
  bestPath: string;
  bestHopCount: number;
  averageHopCount: number;
  maxHopCount: number;
  gatewayRoutes: number;
  bestLatency: number;
  bottleneckCapacity: number;
  spaceLinks: number;
  accessLinks: number;
  applicationProtocol: string;
  transportProtocol: string;
  routingProtocol: string;
  dataLinkProtocol: string;
  applicationProtocolLabel: string;
  transportProtocolLabel: string;
  routingProtocolLabel: string;
  dataLinkProtocolLabel: string;
  dataLinkMediumAccess: string;
  transportOverheadPercent: number;
  transportEfficiencyPercent: number;
  transportHandshakeRoundTrips: number;
  routingCostLabel: string;
  stackLayers: number;
  carrierFrequencyGhz: number;
  bandwidthMhz: number;
  estimatedRainFadeDb: number;
  antennaDiameterM: number;
  antennaEfficiency: number;
  antennaGainDbi: number;
  antennaBeamWidthDeg: number;
  transmitPowerDbw: number;
  systemLossDb: number;
  noiseTemperatureK: number;
  rows: readonly LinkProtocolRow[];
}

export interface LinkProtocolRow {
  linkId: string;
  latency: number;
  capacity: number;
  status: string;
}

type LinkProtocolSnapshot = Pick<
  WorldSnapshot,
  "links" | "routes" | "active_route_id" | "scenario_config"
>;

export const LinkProtocolPanel = memo(function LinkProtocolPanel({
  snapshot
}: {
  snapshot: WorldSnapshot;
}) {
  const summary = buildLinkProtocolSummary(snapshot);

  return (
    <section className="dashboard-section link-protocol-panel" aria-label="链路与协议">
      <div className="section-title">链路与协议</div>
      <div className="kpi-grid wide">
        <KpiPanel label="活动链路" value={String(summary.activeLinks)} />
        <KpiPanel label="可用路由" value={String(summary.availableRoutes)} />
        <KpiPanel label="最佳时延" value={`${summary.bestLatency.toFixed(3)} s`} />
        <KpiPanel label="瓶颈容量" value={`${summary.bottleneckCapacity.toFixed(1)} Mbps`} />
        <KpiPanel label="路径跳数" value={String(summary.bestHopCount)} />
        <KpiPanel label="平均跳数" value={summary.averageHopCount.toFixed(1)} />
        <KpiPanel label="最长跳数" value={String(summary.maxHopCount)} />
        <KpiPanel label="网关路由" value={String(summary.gatewayRoutes)} />
        <KpiPanel label="应用协议" value={summary.applicationProtocolLabel} />
        <KpiPanel label="传输协议" value={summary.transportProtocolLabel} />
        <KpiPanel label="路由协议" value={summary.routingProtocolLabel} />
        <KpiPanel label="链路层MAC" value={summary.dataLinkProtocolLabel} />
        <KpiPanel label="接入方式" value={summary.dataLinkMediumAccess} />
        <KpiPanel
          label="传输开销"
          value={`${summary.transportOverheadPercent.toFixed(2)}%`}
          detail={`效率 ${summary.transportEfficiencyPercent.toFixed(1)}%`}
        />
        <KpiPanel label="握手RTT" value={String(summary.transportHandshakeRoundTrips)} />
        <KpiPanel label="路由代价" value={summary.routingCostLabel} />
        <KpiPanel label="协议栈层数" value={String(summary.stackLayers)} />
        <KpiPanel label="载波频率" value={`${summary.carrierFrequencyGhz.toFixed(1)} GHz`} />
        <KpiPanel label="信道带宽" value={`${summary.bandwidthMhz.toFixed(0)} MHz`} />
        <KpiPanel
          label="天线增益"
          value={`${summary.antennaGainDbi.toFixed(1)} dBi`}
          detail={`${summary.antennaDiameterM.toFixed(2)} m / η ${summary.antennaEfficiency.toFixed(2)}`}
        />
        <KpiPanel label="波束宽度" value={`${summary.antennaBeamWidthDeg.toFixed(2)}°`} />
        <KpiPanel label="发射功率" value={`${summary.transmitPowerDbw.toFixed(1)} dBW`} />
        <KpiPanel label="系统损耗" value={`${summary.systemLossDb.toFixed(1)} dB`} />
        <KpiPanel label="噪声温度" value={`${summary.noiseTemperatureK.toFixed(0)} K`} />
        <KpiPanel label="估算雨衰" value={`${summary.estimatedRainFadeDb.toFixed(2)} dB`} />
        <KpiPanel label="星间链路" value={String(summary.spaceLinks)} />
        <KpiPanel label="接入链路" value={String(summary.accessLinks)} />
      </div>
      <div className="route-strip" aria-label="最佳路径">
        <span>最佳路径</span>
        <strong>{summary.bestPath}</strong>
      </div>
      <div className="link-table" aria-label="链路明细">
        {summary.rows.map((row) => (
          <div className="link-table-row" key={row.linkId}>
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

export function buildLinkProtocolSummary(
  snapshot: LinkProtocolSnapshot
): LinkProtocolSummary {
  const activeLinks = snapshot.links.filter((link) => link.availability);
  const availableRoutes = snapshot.routes.filter((route) => route.available);
  const bestRoute = selectBestRoute(availableRoutes, snapshot.active_route_id);
  const hopCounts = availableRoutes.map(routeHopCount);
  const bottleneckCapacity =
    activeLinks.length === 0
      ? 0
      : Math.min(...activeLinks.map((link) => link.capacity));
  const linkClasses = classifyLinks(activeLinks);
  const network = snapshot.scenario_config?.network;
  const applicationProtocol = network?.application_protocol ?? "TASK_OFFLOAD_FLOW";
  const transportProtocol = network?.transport_protocol ?? "TCP";
  const routingProtocol = network?.routing_protocol ?? "LINK_STATE";
  const dataLinkProtocol = network?.datalink_mac_protocol ?? "TDMA";
  const transportProfile = transportProfileFor(transportProtocol);
  const routingCostProfile = routingCostProfileFor(routingProtocol, {
    latencyWeight: network?.routing_latency_weight,
    inverseCapacityWeight: network?.routing_inverse_capacity_weight,
    hopWeight: network?.routing_hop_weight
  });
  const dataLinkProfile = dataLinkProfileFor(dataLinkProtocol);
  const carrierFrequencyGhz = (network?.carrier_frequency_hz ?? 20_000_000_000) / 1_000_000_000;
  const bandwidthMhz = (network?.channel_bandwidth_hz ?? 100_000_000) / 1_000_000;
  const antennaDiameterM = network?.antenna_diameter_m ?? 0.45;
  const antennaEfficiency = network?.antenna_aperture_efficiency ?? 0.65;
  const transmitPowerDbw = network?.transmit_power_dbw ?? 20;
  const systemLossDb = network?.system_loss_db ?? 1;
  const noiseTemperatureK = network?.noise_temperature_k ?? 290;
  const estimatedRainFadeDb =
    (network?.rain_rate_mm_h ?? 0) *
    (network?.rain_attenuation_coefficient_db_per_km_per_mm_h ?? 0) *
    (network?.rain_effective_path_km ?? 0);

  return {
    activeLinks: activeLinks.length,
    availableRoutes: availableRoutes.length,
    bestRouteId: bestRoute?.route_id ?? "无",
    bestPath: bestRoute?.path.join(" -> ") ?? "暂无可用路径",
    bestHopCount: bestRoute === undefined ? 0 : routeHopCount(bestRoute),
    averageHopCount:
      hopCounts.length === 0
        ? 0
        : hopCounts.reduce((total, hopCount) => total + hopCount, 0) /
          hopCounts.length,
    maxHopCount: hopCounts.length === 0 ? 0 : Math.max(...hopCounts),
    gatewayRoutes: availableRoutes.filter(routeEndsAtComputeNode).length,
    bestLatency: bestRoute?.latency ?? 0,
    bottleneckCapacity,
    spaceLinks: linkClasses.spaceLinks,
    accessLinks: linkClasses.accessLinks,
    applicationProtocol,
    transportProtocol,
    routingProtocol,
    dataLinkProtocol,
    applicationProtocolLabel: formatApplicationProtocol(applicationProtocol),
    transportProtocolLabel: formatTransportProtocol(transportProtocol),
    routingProtocolLabel: formatRoutingProtocol(routingProtocol),
    dataLinkProtocolLabel: dataLinkProfile.label,
    dataLinkMediumAccess: dataLinkProfile.mediumAccess,
    transportOverheadPercent: transportProfile.overheadRatio * 100,
    transportEfficiencyPercent: transportProfile.efficiency * 100,
    transportHandshakeRoundTrips: transportProfile.handshakeRoundTrips,
    routingCostLabel: routingCostProfile.label,
    stackLayers: 6,
    carrierFrequencyGhz,
    bandwidthMhz,
    estimatedRainFadeDb,
    antennaDiameterM,
    antennaEfficiency,
    antennaGainDbi: apertureAntennaGainDbi(
      antennaDiameterM,
      carrierFrequencyGhz * 1_000_000_000,
      antennaEfficiency
    ),
    antennaBeamWidthDeg: apertureAntennaBeamWidthDeg(
      antennaDiameterM,
      carrierFrequencyGhz * 1_000_000_000
    ),
    transmitPowerDbw,
    systemLossDb,
    noiseTemperatureK,
    rows: activeLinks
      .slice()
      .sort(compareLinks)
      .slice(0, 5)
      .map(linkToRow)
  };
}

function routeHopCount(route: Route): number {
  return Math.max(0, route.path.length - 1);
}

function routeEndsAtComputeNode(route: Route): boolean {
  const lastNode = route.path[route.path.length - 1];
  return typeof lastNode === "string" && lastNode.startsWith("compute-");
}

function transportProfileFor(protocol: string): {
  overheadRatio: number;
  efficiency: number;
  handshakeRoundTrips: number;
} {
  if (protocol === "UDP") {
    return {
      overheadRatio: 28 / (1472 + 28),
      efficiency: 0.98,
      handshakeRoundTrips: 0
    };
  }
  return {
    overheadRatio: 40 / (1460 + 40),
    efficiency: 0.92,
    handshakeRoundTrips: 1
  };
}

function formatApplicationProtocol(protocol: string): string {
  if (protocol === "HTTP") {
    return "HTTP";
  }
  if (protocol === "MQTT") {
    return "MQTT";
  }
  if (protocol === "TELEMETRY") {
    return "遥测流";
  }
  return "任务卸载";
}

function routingCostProfileFor(
  protocol: string,
  weights: {
    latencyWeight?: number;
    inverseCapacityWeight?: number;
    hopWeight?: number;
  }
): { label: string } {
  const defaults =
    protocol === "DISTANCE_VECTOR"
      ? { latencyWeight: 0, inverseCapacityWeight: 0, hopWeight: 1 }
      : { latencyWeight: 1, inverseCapacityWeight: 0, hopWeight: 0 };
  const latencyWeight = weights.latencyWeight ?? defaults.latencyWeight;
  const inverseCapacityWeight =
    weights.inverseCapacityWeight ?? defaults.inverseCapacityWeight;
  const hopWeight = weights.hopWeight ?? defaults.hopWeight;
  const weightLabel = `时延${formatWeight(latencyWeight)} 容量${formatWeight(
    inverseCapacityWeight
  )} 跳数${formatWeight(hopWeight)}`;
  if (protocol === "DISTANCE_VECTOR") {
    return { label: `距离向量 / ${weightLabel}` };
  }
  if (protocol === "STATIC") {
    return { label: `静态路径 / ${weightLabel}` };
  }
  return { label: `链路状态 / ${weightLabel}` };
}

function formatWeight(value: number): string {
  return Number.isInteger(value) ? value.toFixed(0) : value.toFixed(2);
}

function dataLinkProfileFor(protocol: string): {
  label: string;
  mediumAccess: string;
} {
  if (protocol === "SLOTTED_ALOHA") {
    return { label: "Slotted ALOHA", mediumAccess: "时隙竞争" };
  }
  if (protocol === "CSMA_CA") {
    return { label: "CSMA/CA", mediumAccess: "侦听避碰" };
  }
  return { label: "TDMA", mediumAccess: "时分调度" };
}

function apertureAntennaGainDbi(
  diameterM: number,
  carrierFrequencyHz: number,
  apertureEfficiency: number
): number {
  const wavelengthM = 299_792_458 / carrierFrequencyHz;
  const gainLinear = apertureEfficiency * Math.pow((Math.PI * diameterM) / wavelengthM, 2);
  return 10 * Math.log10(gainLinear);
}

function apertureAntennaBeamWidthDeg(
  diameterM: number,
  carrierFrequencyHz: number
): number {
  const wavelengthM = 299_792_458 / carrierFrequencyHz;
  return (70 * wavelengthM) / diameterM;
}

function formatTransportProtocol(protocol: string): string {
  if (protocol === "TCP") {
    return "TCP 可靠传输";
  }
  if (protocol === "UDP") {
    return "UDP 低时延";
  }
  return protocol;
}

function formatRoutingProtocol(protocol: string): string {
  if (protocol === "LINK_STATE") {
    return "链路状态";
  }
  if (protocol === "DISTANCE_VECTOR") {
    return "距离向量";
  }
  if (protocol === "SHORTEST_PATH") {
    return "最短路径";
  }
  if (protocol === "STATIC") {
    return "静态路由";
  }
  return protocol;
}

function classifyLinks(links: readonly LinkState[]): {
  spaceLinks: number;
  accessLinks: number;
} {
  return links.reduce(
    (summary, link) => {
      const sourceIsSatellite = isSatelliteEndpoint(link.source_id);
      const targetIsSatellite = isSatelliteEndpoint(link.target_id);
      if (sourceIsSatellite && targetIsSatellite) {
        summary.spaceLinks += 1;
      } else if (sourceIsSatellite || targetIsSatellite) {
        summary.accessLinks += 1;
      }
      return summary;
    },
    { spaceLinks: 0, accessLinks: 0 }
  );
}

function isSatelliteEndpoint(endpointId: string): boolean {
  return endpointId.toLowerCase().startsWith("sat-");
}

function selectBestRoute(
  routes: readonly Route[],
  activeRouteId: string | null
): Route | undefined {
  const activeRoute = routes.find((route) => route.route_id === activeRouteId);
  if (activeRoute !== undefined) {
    return activeRoute;
  }
  return routes.slice().sort(compareRoutes)[0];
}

function compareRoutes(left: Route, right: Route): number {
  const latency = left.latency - right.latency;
  if (latency !== 0) {
    return latency;
  }
  return left.route_id.localeCompare(right.route_id);
}

function compareLinks(left: LinkState, right: LinkState): number {
  const capacity = right.capacity - left.capacity;
  if (capacity !== 0) {
    return capacity;
  }
  return `${left.source_id}->${left.target_id}`.localeCompare(
    `${right.source_id}->${right.target_id}`
  );
}

function linkToRow(link: LinkState): LinkProtocolRow {
  return {
    linkId: `${link.source_id} -> ${link.target_id}`,
    latency: link.latency,
    capacity: link.capacity,
    status: link.availability ? "可用" : "不可用"
  };
}
