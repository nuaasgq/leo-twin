import { describe, expect, it } from "vitest";

import { buildLinkProtocolSummary } from "../src/dashboard/link_protocol/LinkProtocolPanel";

describe("buildLinkProtocolSummary", () => {
  it("summarizes links and selects the lowest-latency route deterministically", () => {
    const summary = buildLinkProtocolSummary({
      active_route_id: null,
      scenario_config: {
        network: {
          application_protocol: "MQTT",
          transport_protocol: "UDP",
          transport_loss_rate: 0.025,
          transport_congestion_window_segments: 32,
          routing_protocol: "DISTANCE_VECTOR",
          datalink_mac_protocol: "SLOTTED_ALOHA",
          routing_latency_weight: 0.25,
          routing_inverse_capacity_weight: 300,
          routing_hop_weight: 1,
          carrier_frequency_hz: 22_000_000_000,
          channel_bandwidth_hz: 250_000_000,
          rain_rate_mm_h: 12.5,
          rain_attenuation_coefficient_db_per_km_per_mm_h: 0.015,
          rain_effective_path_km: 4,
          antenna_diameter_m: 0.55,
          antenna_aperture_efficiency: 0.7,
          transmit_power_dbw: 23,
          system_loss_db: 1.5,
          noise_temperature_k: 310
        }
      },
      links: [
        {
          source_id: "sat-b",
          target_id: "sat-c",
          latency: 0.4,
          capacity: 40,
          availability: true
        },
        {
          source_id: "sat-a",
          target_id: "sat-b",
          latency: 0.2,
          capacity: 80,
          availability: true
        },
        {
          source_id: "sat-a",
          target_id: "user-1",
          latency: 0.3,
          capacity: 30,
          availability: true
        },
        {
          source_id: "sat-x",
          target_id: "sat-y",
          latency: 0.1,
          capacity: 100,
          availability: false
        }
      ],
      routes: [
        {
          route_id: "route-slow",
          flow_id: "flow-a",
          path: ["user", "sat-b", "node"],
          latency: 2.0,
          capacity: 40,
          available: true
        },
        {
          route_id: "route-fast",
          flow_id: "flow-b",
          path: ["user", "sat-a", "sat-b", "node"],
          latency: 1.5,
          capacity: 60,
          available: true
        }
      ]
    });

    expect(summary).toEqual({
      activeLinks: 3,
      availableRoutes: 2,
      bestRouteId: "route-fast",
      bestPath: "user -> sat-a -> sat-b -> node",
      bestHopCount: 3,
      averageHopCount: 2.5,
      maxHopCount: 3,
      gatewayRoutes: 0,
      bestLatency: 1.5,
      bottleneckCapacity: 30,
      spaceLinks: 2,
      accessLinks: 1,
      applicationProtocol: "MQTT",
      transportProtocol: "UDP",
      routingProtocol: "DISTANCE_VECTOR",
      dataLinkProtocol: "SLOTTED_ALOHA",
      applicationProtocolLabel: "MQTT",
      transportProtocolLabel: "UDP 低时延",
      routingProtocolLabel: "距离向量",
      dataLinkProtocolLabel: "Slotted ALOHA",
      dataLinkMediumAccess: "时隙竞争",
      transportOverheadPercent: 1.866666666666667,
      transportEfficiencyPercent: 98,
      transportHandshakeRoundTrips: 0,
      transportLossPercent: 2.5,
      transportCongestionWindow: 32,
      routingCostLabel: "距离向量 / 时延0.25 容量300 跳数1",
      stackLayers: 6,
      carrierFrequencyGhz: 22,
      bandwidthMhz: 250,
      estimatedRainFadeDb: 0.75,
      antennaDiameterM: 0.55,
      antennaEfficiency: 0.7,
      antennaGainDbi: 40.5132712017957,
      antennaBeamWidthDeg: 1.7343365338842973,
      transmitPowerDbw: 23,
      systemLossDb: 1.5,
      noiseTemperatureK: 310,
      rows: [
        {
          linkId: "sat-a -> sat-b",
          latency: 0.2,
          capacity: 80,
          status: "可用"
        },
        {
          linkId: "sat-b -> sat-c",
          latency: 0.4,
          capacity: 40,
          status: "可用"
        },
        {
          linkId: "sat-a -> user-1",
          latency: 0.3,
          capacity: 30,
          status: "可用"
        }
      ]
    });
  });

  it("prefers the active route when it is available", () => {
    const summary = buildLinkProtocolSummary({
      active_route_id: "route-selected",
      scenario_config: null,
      links: [],
      routes: [
        {
          route_id: "route-fast",
          flow_id: "flow-a",
          path: ["a", "b"],
          latency: 1,
          capacity: 10,
          available: true
        },
        {
          route_id: "route-selected",
          flow_id: "flow-b",
          path: ["x", "y"],
          latency: 5,
          capacity: 20,
          available: true
        }
      ]
    });

    expect(summary.bestRouteId).toBe("route-selected");
    expect(summary.bestPath).toBe("x -> y");
    expect(summary.averageHopCount).toBe(1);
    expect(summary.maxHopCount).toBe(1);
    expect(summary.gatewayRoutes).toBe(0);
    expect(summary.transportProtocol).toBe("TCP");
    expect(summary.applicationProtocol).toBe("TASK_OFFLOAD_FLOW");
    expect(summary.routingProtocol).toBe("LINK_STATE");
    expect(summary.dataLinkProtocol).toBe("TDMA");
    expect(summary.transportProtocolLabel).toBe("TCP 可靠传输");
    expect(summary.applicationProtocolLabel).toBe("任务卸载");
    expect(summary.routingProtocolLabel).toBe("链路状态");
    expect(summary.dataLinkProtocolLabel).toBe("TDMA");
    expect(summary.dataLinkMediumAccess).toBe("时分调度");
    expect(summary.transportOverheadPercent).toBeCloseTo(2.666667, 6);
    expect(summary.transportEfficiencyPercent).toBe(92);
    expect(summary.transportHandshakeRoundTrips).toBe(1);
    expect(summary.transportLossPercent).toBe(0);
    expect(summary.transportCongestionWindow).toBe(0);
    expect(summary.routingCostLabel).toBe("链路状态 / 时延1 容量0 跳数0");
    expect(summary.stackLayers).toBe(6);
    expect(summary.carrierFrequencyGhz).toBe(20);
    expect(summary.bandwidthMhz).toBe(100);
    expect(summary.estimatedRainFadeDb).toBe(0);
    expect(summary.antennaDiameterM).toBe(0.45);
    expect(summary.antennaEfficiency).toBe(0.65);
    expect(summary.antennaGainDbi).toBeCloseTo(37.620567, 6);
    expect(summary.antennaBeamWidthDeg).toBeCloseTo(2.331719, 6);
    expect(summary.transmitPowerDbw).toBe(20);
    expect(summary.systemLossDb).toBe(1);
    expect(summary.noiseTemperatureK).toBe(290);
  });
});
