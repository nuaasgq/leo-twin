import { useEffect, useState } from "react";

import {
  FidelitySummary,
  GeneratedScenarioConfig,
  RuntimeMode,
  RuntimeStatusPayload
} from "../core/event_types";
import { runtimeEffectiveSpeedFactor } from "../runtime_display";
import { RuntimeAction } from "./controlClient";

export interface ScenarioControlValues {
  satellite_count: number;
  user_count: number;
  compute_nodes: number;
  compute_capacity: number;
  compute_cpu_gflops_fp64?: number;
  compute_gpu_tflops_fp32?: number;
  compute_gpu_tflops_fp16?: number;
  compute_npu_tops_int8?: number;
  compute_memory_gb?: number;
  compute_storage_gb?: number;
  compute_scheduling_policy: string;
  orbit: OrbitControlValues;
  traffic_model: TrafficControlValues;
  visualization: VisualizationControlValues;
  network: NetworkControlValues;
}

export interface OrbitControlValues {
  update_interval_seconds: number;
  plane_count: number;
  altitude_km: number;
  inclination_deg: number;
}

export interface TrafficControlValues {
  flow_interval_seconds: number;
  task_interval_seconds: number;
  flow_demand_capacity: number;
  task_compute_demand: number;
  task_data_size: number;
  traffic_class?: string;
  destination_type?: string;
  output_data_size?: number;
}

export interface VisualizationControlValues {
  satellites: boolean;
  links: boolean;
  users: boolean;
  metrics: boolean;
}

export interface VisualizationLayerEffectItem {
  label: string;
  stateLabel: string;
  detail: string;
}

export interface OrbitMotionExplanationItem {
  label: string;
  value: string;
  detail: string;
}

export interface NetworkControlValues {
  application_protocol: string;
  transport_protocol: string;
  transport_loss_rate: number;
  transport_congestion_window_segments: number;
  routing_protocol: string;
  datalink_mac_protocol: string;
  routing_latency_weight: number;
  routing_inverse_capacity_weight: number;
  routing_hop_weight: number;
  carrier_frequency_ghz: number;
  channel_bandwidth_mhz: number;
  rain_rate_mm_h: number;
  rain_attenuation_coefficient_db_per_km_per_mm_h: number;
  rain_effective_path_km: number;
  antenna_diameter_m: number;
  antenna_aperture_efficiency: number;
  transmit_power_dbw: number;
  system_loss_db: number;
  noise_temperature_k: number;
}

export interface InitializationControlValues extends ScenarioControlValues {
  mode: RuntimeMode;
  speed_factor: number;
  duration: number;
  seed: number;
}

export interface ConfigPanelProps {
  scenario: ScenarioControlValues;
  runtime: RuntimeStatusPayload;
  progress: RuntimeProgressValues;
  generatedConfig: GeneratedScenarioConfig | null;
  controlError?: string | null;
  onRuntimeControl: (action: RuntimeAction, payload?: Record<string, unknown>) => void;
}

export interface ConfigSummaryItem {
  label: string;
  value: string;
  detail?: string;
  templateId?: string;
}

export interface RuntimeProgressValues {
  sim_time: number;
  duration: number;
  event_count: number;
}

export interface RuntimeProgressSummary {
  elapsedLabel: string;
  totalLabel: string;
  eventCountLabel: string;
  percent: number;
  percentLabel: string;
}

export const CONFIG_PANEL_SECTION_LABELS = {
  execution: "仿真执行控制",
  resources: "场景规模与算力资源",
  orbit: "轨道参数",
  traffic: "业务流量与任务需求",
  runtime: "可视化图层",
  network: "网络协议栈与路由",
  physical: "物理层与信道参数",
  activeScenario: "当前生效场景"
} as const;

export interface ScenarioScalePreset {
  id: string;
  label: string;
  detail: string;
  expectedTopology: string;
  expectedFidelity: string;
  satelliteCount: number;
  userCount: number;
  computeNodeCount: number;
}

export interface NetworkQualityPreset {
  id: string;
  label: string;
  detail: string;
  flowDemandCapacity: number;
  applicationProtocol: string;
  transportProtocol: string;
  transportLossRate: number;
  transportCongestionWindowSegments: number;
  routingProtocol: string;
  datalinkMacProtocol: string;
  routingLatencyWeight: number;
  routingInverseCapacityWeight: number;
  routingHopWeight: number;
}

export const SCENARIO_SCALE_PRESETS: readonly ScenarioScalePreset[] = [
  {
    id: "demo-72",
    label: "72 星",
    detail: "详细演示",
    expectedTopology: "小规模详细演示，初始化后由后端确认轨道面与相位。",
    expectedFidelity: "预计保留逐星轨道更新和详细链路展示。",
    satelliteCount: 72,
    userCount: 1000,
    computeNodeCount: 72
  },
  {
    id: "medium-300",
    label: "300 星",
    detail: "中等规模",
    expectedTopology: "中等规模星座，初始化后由后端自动分配轨道面。",
    expectedFidelity: "预计启用批量轨道更新，保持交互响应。",
    satelliteCount: 300,
    userCount: 1000,
    computeNodeCount: 300
  },
  {
    id: "scale-1200",
    label: "1200 星",
    detail: "规模稳定",
    expectedTopology: "大规模稳定性场景，卫星同时作为算力节点。",
    expectedFidelity: "预计启用批量轨道、聚合指标和有界星间链路候选。",
    satelliteCount: 1200,
    userCount: 100,
    computeNodeCount: 1200
  }
];

export const NETWORK_QUALITY_PRESETS: readonly NetworkQualityPreset[] = [
  {
    id: "stable-low-load",
    label: "稳定低负载",
    detail: "TCP / TDMA / 低需求",
    flowDemandCapacity: 10,
    applicationProtocol: "TASK_OFFLOAD_FLOW",
    transportProtocol: "TCP",
    transportLossRate: 0,
    transportCongestionWindowSegments: 0,
    routingProtocol: "LINK_STATE",
    datalinkMacProtocol: "TDMA",
    routingLatencyWeight: 1,
    routingInverseCapacityWeight: 0,
    routingHopWeight: 0
  },
  {
    id: "congested-demand",
    label: "拥塞压力",
    detail: "高需求 / TCP 窗口",
    flowDemandCapacity: 450,
    applicationProtocol: "TASK_OFFLOAD_FLOW",
    transportProtocol: "TCP",
    transportLossRate: 0.02,
    transportCongestionWindowSegments: 24,
    routingProtocol: "LINK_STATE",
    datalinkMacProtocol: "TDMA",
    routingLatencyWeight: 1,
    routingInverseCapacityWeight: 200,
    routingHopWeight: 0.2
  },
  {
    id: "lossy-access",
    label: "有损接入",
    detail: "UDP / ALOHA / 损耗",
    flowDemandCapacity: 80,
    applicationProtocol: "MQTT",
    transportProtocol: "UDP",
    transportLossRate: 0.03,
    transportCongestionWindowSegments: 0,
    routingProtocol: "DISTANCE_VECTOR",
    datalinkMacProtocol: "SLOTTED_ALOHA",
    routingLatencyWeight: 0.2,
    routingInverseCapacityWeight: 400,
    routingHopWeight: 1
  },
  {
    id: "delay-variation",
    label: "高时延波动",
    detail: "容量偏好 / CSMA",
    flowDemandCapacity: 120,
    applicationProtocol: "HTTP",
    transportProtocol: "TCP",
    transportLossRate: 0.01,
    transportCongestionWindowSegments: 12,
    routingProtocol: "SHORTEST_PATH",
    datalinkMacProtocol: "CSMA_CA",
    routingLatencyWeight: 0.1,
    routingInverseCapacityWeight: 800,
    routingHopWeight: 3
  }
];

export interface ScenarioScaleSelection {
  satelliteCount: number;
  userCount: number;
  computeNodes: number;
}

export interface NetworkQualitySelection {
  flowDemandCapacity: number;
  applicationProtocol: string;
  transportProtocol: string;
  transportLossRate: number;
  transportCongestionWindowSegments: number;
  routingProtocol: string;
  datalinkMacProtocol: string;
  routingLatencyWeight: number;
  routingInverseCapacityWeight: number;
  routingHopWeight: number;
}

export function selectedScenarioScalePreset(
  selection: ScenarioScaleSelection
): ScenarioScalePreset | null {
  return (
    SCENARIO_SCALE_PRESETS.find(
      (preset) =>
        preset.satelliteCount === selection.satelliteCount &&
        preset.userCount === selection.userCount &&
        preset.computeNodeCount === selection.computeNodes
    ) ?? null
  );
}

export function selectedNetworkQualityPreset(
  selection: NetworkQualitySelection
): NetworkQualityPreset | null {
  return (
    NETWORK_QUALITY_PRESETS.find((preset) => networkQualityPresetMatches(preset, selection)) ??
    null
  );
}

export function scalePresetSummaryItems(
  selection: ScenarioScaleSelection,
  generatedConfig: GeneratedScenarioConfig | null | undefined
): readonly ConfigSummaryItem[] {
  const preset = selectedScenarioScalePreset(selection);
  if (preset === null) {
    return [
      { label: "规模选择", value: "自定义规模" },
      { label: "初始化后", value: "后端将重新推导轨道面、算力节点和保真策略。" }
    ];
  }

  if (generatedConfigMatchesSelection(selection, generatedConfig)) {
    const backendSummary = generatedConfig?.backend_summary;
    const constellation = backendSummary?.derived_constellation_summary;
    const fidelity = backendSummary?.fidelity_summary;
    return [
      {
        label: "后端轨道",
        value:
          constellation !== undefined
            ? `${formatInteger(constellation.plane_count)} 面 / 每面 ${formatInteger(
                constellation.satellites_per_plane
              )} 星`
            : "后端未返回轨道摘要"
      },
      {
        label: "后端保真",
        value: formatFidelityModeSummary(fidelity)
      },
      {
        label: "后端说明",
        value: formatModelAssumption(constellation?.model_note)
      }
    ];
  }

  return [
    { label: "规模预设", value: `${preset.label} · ${preset.detail}` },
    { label: "预计拓扑", value: preset.expectedTopology },
    { label: "预计保真", value: preset.expectedFidelity }
  ];
}

export function configPanelSectionTitles(): readonly string[] {
  return Object.values(CONFIG_PANEL_SECTION_LABELS);
}

export function ConfigPanel({
  scenario,
  runtime,
  progress,
  generatedConfig,
  controlError = null,
  onRuntimeControl
}: ConfigPanelProps) {
  const [satelliteCount, setSatelliteCount] = useState(scenario.satellite_count);
  const [userCount, setUserCount] = useState(scenario.user_count);
  const [computeNodes, setComputeNodes] = useState(scenario.compute_nodes);
  const [computeCapacity, setComputeCapacity] = useState(scenario.compute_capacity);
  const [computeCpuFp64, setComputeCpuFp64] = useState(
    scenario.compute_cpu_gflops_fp64 ?? 0
  );
  const [computeGpuFp32, setComputeGpuFp32] = useState(
    scenario.compute_gpu_tflops_fp32 ?? 0
  );
  const [computeGpuFp16, setComputeGpuFp16] = useState(
    scenario.compute_gpu_tflops_fp16 ?? 0
  );
  const [computeNpuInt8, setComputeNpuInt8] = useState(
    scenario.compute_npu_tops_int8 ?? 0
  );
  const [computeMemoryGb, setComputeMemoryGb] = useState(
    scenario.compute_memory_gb ?? 0
  );
  const [computeStorageGb, setComputeStorageGb] = useState(
    scenario.compute_storage_gb ?? 0
  );
  const [computeSchedulingPolicy, setComputeSchedulingPolicy] = useState(
    scenario.compute_scheduling_policy
  );
  const [orbitUpdateIntervalSeconds, setOrbitUpdateIntervalSeconds] = useState(
    scenario.orbit.update_interval_seconds
  );
  const [orbitPlaneCount, setOrbitPlaneCount] = useState(scenario.orbit.plane_count);
  const [orbitAltitudeKm, setOrbitAltitudeKm] = useState(scenario.orbit.altitude_km);
  const [orbitInclinationDeg, setOrbitInclinationDeg] = useState(
    scenario.orbit.inclination_deg
  );
  const [flowIntervalSeconds, setFlowIntervalSeconds] = useState(
    scenario.traffic_model.flow_interval_seconds
  );
  const [taskIntervalSeconds, setTaskIntervalSeconds] = useState(
    scenario.traffic_model.task_interval_seconds
  );
  const [flowDemandCapacity, setFlowDemandCapacity] = useState(
    scenario.traffic_model.flow_demand_capacity
  );
  const [taskComputeDemand, setTaskComputeDemand] = useState(
    scenario.traffic_model.task_compute_demand
  );
  const [taskDataSize, setTaskDataSize] = useState(scenario.traffic_model.task_data_size);
  const [trafficClass, setTrafficClass] = useState(
    scenario.traffic_model.traffic_class ?? "COMPUTE_SERVICE"
  );
  const [trafficDestinationType, setTrafficDestinationType] = useState(
    scenario.traffic_model.destination_type ?? "COMPUTE_NODE"
  );
  const [trafficOutputDataSize, setTrafficOutputDataSize] = useState(
    scenario.traffic_model.output_data_size ?? 0
  );
  const [showSatellites, setShowSatellites] = useState(scenario.visualization.satellites);
  const [showLinks, setShowLinks] = useState(scenario.visualization.links);
  const [showUsers, setShowUsers] = useState(scenario.visualization.users);
  const [showMetrics, setShowMetrics] = useState(scenario.visualization.metrics);
  const [applicationProtocol, setApplicationProtocol] = useState(
    scenario.network.application_protocol
  );
  const [transportProtocol, setTransportProtocol] = useState(
    scenario.network.transport_protocol
  );
  const [transportLossRate, setTransportLossRate] = useState(
    scenario.network.transport_loss_rate
  );
  const [transportCongestionWindow, setTransportCongestionWindow] = useState(
    scenario.network.transport_congestion_window_segments
  );
  const [routingProtocol, setRoutingProtocol] = useState(scenario.network.routing_protocol);
  const [dataLinkProtocol, setDataLinkProtocol] = useState(
    scenario.network.datalink_mac_protocol
  );
  const [routingLatencyWeight, setRoutingLatencyWeight] = useState(
    scenario.network.routing_latency_weight
  );
  const [routingInverseCapacityWeight, setRoutingInverseCapacityWeight] = useState(
    scenario.network.routing_inverse_capacity_weight
  );
  const [routingHopWeight, setRoutingHopWeight] = useState(
    scenario.network.routing_hop_weight
  );
  const [carrierFrequencyGhz, setCarrierFrequencyGhz] = useState(
    scenario.network.carrier_frequency_ghz
  );
  const [channelBandwidthMhz, setChannelBandwidthMhz] = useState(
    scenario.network.channel_bandwidth_mhz
  );
  const [rainRate, setRainRate] = useState(scenario.network.rain_rate_mm_h);
  const [rainCoefficient, setRainCoefficient] = useState(
    scenario.network.rain_attenuation_coefficient_db_per_km_per_mm_h
  );
  const [rainPathKm, setRainPathKm] = useState(scenario.network.rain_effective_path_km);
  const [antennaDiameterM, setAntennaDiameterM] = useState(
    scenario.network.antenna_diameter_m
  );
  const [antennaApertureEfficiency, setAntennaApertureEfficiency] = useState(
    scenario.network.antenna_aperture_efficiency
  );
  const [transmitPowerDbw, setTransmitPowerDbw] = useState(
    scenario.network.transmit_power_dbw
  );
  const [systemLossDb, setSystemLossDb] = useState(scenario.network.system_loss_db);
  const [noiseTemperatureK, setNoiseTemperatureK] = useState(
    scenario.network.noise_temperature_k
  );
  const [runtimeMode, setRuntimeMode] = useState<Exclude<RuntimeMode, "PAUSED">>(
    runtime.mode === "ACCELERATED" ? "ACCELERATED" : "REAL_TIME"
  );
  const [speedFactor, setSpeedFactor] = useState(() =>
    runtimeEffectiveSpeedFactor(
      runtime.mode === "PAUSED" ? "REAL_TIME" : runtime.mode,
      runtime.speed_factor
    )
  );
  const [durationSeconds, setDurationSeconds] = useState(runtime.duration);
  const [seed, setSeed] = useState(runtime.seed);

  useEffect(() => {
    setSatelliteCount(scenario.satellite_count);
    setUserCount(scenario.user_count);
    setComputeNodes(scenario.compute_nodes);
    setComputeCapacity(scenario.compute_capacity);
    setComputeCpuFp64(scenario.compute_cpu_gflops_fp64 ?? 0);
    setComputeGpuFp32(scenario.compute_gpu_tflops_fp32 ?? 0);
    setComputeGpuFp16(scenario.compute_gpu_tflops_fp16 ?? 0);
    setComputeNpuInt8(scenario.compute_npu_tops_int8 ?? 0);
    setComputeMemoryGb(scenario.compute_memory_gb ?? 0);
    setComputeStorageGb(scenario.compute_storage_gb ?? 0);
    setComputeSchedulingPolicy(scenario.compute_scheduling_policy);
    setOrbitUpdateIntervalSeconds(scenario.orbit.update_interval_seconds);
    setOrbitPlaneCount(scenario.orbit.plane_count);
    setOrbitAltitudeKm(scenario.orbit.altitude_km);
    setOrbitInclinationDeg(scenario.orbit.inclination_deg);
    setFlowIntervalSeconds(scenario.traffic_model.flow_interval_seconds);
    setTaskIntervalSeconds(scenario.traffic_model.task_interval_seconds);
    setFlowDemandCapacity(scenario.traffic_model.flow_demand_capacity);
    setTaskComputeDemand(scenario.traffic_model.task_compute_demand);
    setTaskDataSize(scenario.traffic_model.task_data_size);
    setTrafficClass(scenario.traffic_model.traffic_class ?? "COMPUTE_SERVICE");
    setTrafficDestinationType(
      scenario.traffic_model.destination_type ?? "COMPUTE_NODE"
    );
    setTrafficOutputDataSize(scenario.traffic_model.output_data_size ?? 0);
    setShowSatellites(scenario.visualization.satellites);
    setShowLinks(scenario.visualization.links);
    setShowUsers(scenario.visualization.users);
    setShowMetrics(scenario.visualization.metrics);
    setApplicationProtocol(scenario.network.application_protocol);
    setTransportProtocol(scenario.network.transport_protocol);
    setTransportLossRate(scenario.network.transport_loss_rate);
    setTransportCongestionWindow(scenario.network.transport_congestion_window_segments);
    setRoutingProtocol(scenario.network.routing_protocol);
    setDataLinkProtocol(scenario.network.datalink_mac_protocol);
    setRoutingLatencyWeight(scenario.network.routing_latency_weight);
    setRoutingInverseCapacityWeight(scenario.network.routing_inverse_capacity_weight);
    setRoutingHopWeight(scenario.network.routing_hop_weight);
    setCarrierFrequencyGhz(scenario.network.carrier_frequency_ghz);
    setChannelBandwidthMhz(scenario.network.channel_bandwidth_mhz);
    setRainRate(scenario.network.rain_rate_mm_h);
    setRainCoefficient(scenario.network.rain_attenuation_coefficient_db_per_km_per_mm_h);
    setRainPathKm(scenario.network.rain_effective_path_km);
    setAntennaDiameterM(scenario.network.antenna_diameter_m);
    setAntennaApertureEfficiency(scenario.network.antenna_aperture_efficiency);
    setTransmitPowerDbw(scenario.network.transmit_power_dbw);
    setSystemLossDb(scenario.network.system_loss_db);
    setNoiseTemperatureK(scenario.network.noise_temperature_k);
  }, [
    scenario.satellite_count,
    scenario.user_count,
    scenario.compute_nodes,
    scenario.compute_capacity,
    scenario.compute_cpu_gflops_fp64,
    scenario.compute_gpu_tflops_fp32,
    scenario.compute_gpu_tflops_fp16,
    scenario.compute_npu_tops_int8,
    scenario.compute_memory_gb,
    scenario.compute_storage_gb,
    scenario.compute_scheduling_policy,
    scenario.orbit.update_interval_seconds,
    scenario.orbit.plane_count,
    scenario.orbit.altitude_km,
    scenario.orbit.inclination_deg,
    scenario.traffic_model.flow_interval_seconds,
    scenario.traffic_model.task_interval_seconds,
    scenario.traffic_model.flow_demand_capacity,
    scenario.traffic_model.task_compute_demand,
    scenario.traffic_model.task_data_size,
    scenario.traffic_model.traffic_class,
    scenario.traffic_model.destination_type,
    scenario.traffic_model.output_data_size,
    scenario.visualization.satellites,
    scenario.visualization.links,
    scenario.visualization.users,
    scenario.visualization.metrics,
    scenario.network.application_protocol,
    scenario.network.transport_protocol,
    scenario.network.transport_loss_rate,
    scenario.network.transport_congestion_window_segments,
    scenario.network.routing_protocol,
    scenario.network.datalink_mac_protocol,
    scenario.network.routing_latency_weight,
    scenario.network.routing_inverse_capacity_weight,
    scenario.network.routing_hop_weight,
    scenario.network.carrier_frequency_ghz,
    scenario.network.channel_bandwidth_mhz,
    scenario.network.rain_rate_mm_h,
    scenario.network.rain_attenuation_coefficient_db_per_km_per_mm_h,
    scenario.network.rain_effective_path_km,
    scenario.network.antenna_diameter_m,
    scenario.network.antenna_aperture_efficiency,
    scenario.network.transmit_power_dbw,
    scenario.network.system_loss_db,
    scenario.network.noise_temperature_k
  ]);

  useEffect(() => {
    let nextRuntimeMode: Exclude<RuntimeMode, "PAUSED"> | null = null;
    if (runtime.mode !== "PAUSED") {
      nextRuntimeMode = runtime.mode;
      setRuntimeMode(nextRuntimeMode);
    }
    setSpeedFactor(
      runtimeEffectiveSpeedFactor(nextRuntimeMode ?? runtimeMode, runtime.speed_factor)
    );
    setDurationSeconds(runtime.duration);
    setSeed(runtime.seed);
  }, [runtime.mode, runtime.speed_factor, runtime.duration, runtime.seed]);

  const summaryItems = generatedScenarioSummaryItems(generatedConfig);
  const templateItems = configurationTemplateSummaryItems(generatedConfig);
  const constellationSummary =
    generatedConfig?.backend_summary?.derived_constellation_summary;
  const orbitMotionExplanations = orbitMotionExplanationItems({
    updateIntervalSeconds: orbitUpdateIntervalSeconds,
    altitudeM: orbitAltitudeKm * 1000,
    orbitalPeriodMinutes: constellationSummary?.orbital_period_minutes,
    orbitalVelocityKmS: constellationSummary?.orbital_velocity_km_s
  });
  const pauseResume = pauseResumeControl(runtime);
  const startDisabled = startControlDisabled(runtime);
  const runtimeBusy = runtimeControlBusy(runtime);
  const executionLockReason = runtimeExecutionParameterLockReason(runtime);
  const executionParameterLocked = executionLockReason !== null;
  const speedControlDisabled = executionParameterLocked || runtimeMode === "REAL_TIME";
  const effectiveSpeedFactor = runtimeEffectiveSpeedFactor(runtimeMode, speedFactor);
  const progressSummary = runtimeProgressSummary(progress);
  const visualizationLayerEffects = visualizationLayerEffectItems({
    satellites: showSatellites,
    users: showUsers,
    links: showLinks,
    metrics: showMetrics
  });
  const scaleSelection = {
    satelliteCount,
    userCount,
    computeNodes
  };
  const activeScalePreset = selectedScenarioScalePreset(scaleSelection);
  const scalePresetSummary = scalePresetSummaryItems(scaleSelection, generatedConfig);
  const networkQualitySelection = {
    flowDemandCapacity,
    applicationProtocol,
    transportProtocol,
    transportLossRate,
    transportCongestionWindowSegments: transportCongestionWindow,
    routingProtocol,
    datalinkMacProtocol: dataLinkProtocol,
    routingLatencyWeight,
    routingInverseCapacityWeight,
    routingHopWeight
  };
  const activeNetworkQualityPreset =
    selectedNetworkQualityPreset(networkQualitySelection);
  const handleSatelliteCountChange = (value: number) => {
    const nextCount = boundedInteger(value, 12, 10000);
    setSatelliteCount(nextCount);
    setComputeNodes(nextCount);
  };
  const handleUserCountChange = (value: number) =>
    setUserCount(boundedInteger(value, 10, 100000));
  const handleComputeNodesChange = (value: number) =>
    setComputeNodes(boundedInteger(value, 1, Math.max(1, satelliteCount)));
  const handleScalePreset = (preset: ScenarioScalePreset) => {
    setSatelliteCount(preset.satelliteCount);
    setUserCount(preset.userCount);
    setComputeNodes(preset.computeNodeCount);
  };
  const handleNetworkQualityPreset = (preset: NetworkQualityPreset) => {
    setFlowDemandCapacity(preset.flowDemandCapacity);
    setApplicationProtocol(preset.applicationProtocol);
    setTransportProtocol(preset.transportProtocol);
    setTransportLossRate(preset.transportLossRate);
    setTransportCongestionWindow(preset.transportCongestionWindowSegments);
    setRoutingProtocol(preset.routingProtocol);
    setDataLinkProtocol(preset.datalinkMacProtocol);
    setRoutingLatencyWeight(preset.routingLatencyWeight);
    setRoutingInverseCapacityWeight(preset.routingInverseCapacityWeight);
    setRoutingHopWeight(preset.routingHopWeight);
  };
  const handleRuntimeModeChange = (value: Exclude<RuntimeMode, "PAUSED">) => {
    setRuntimeMode(value);
    if (value === "REAL_TIME") {
      setSpeedFactor(1);
    }
  };
  const handleSpeedFactorChange = (value: number) => {
    if (runtimeMode === "REAL_TIME") {
      setSpeedFactor(1);
      return;
    }
    setSpeedFactor(boundedInteger(value, 1, 100));
  };
  const handleDurationSecondsChange = (value: number) =>
    setDurationSeconds(boundedInteger(value, 60, 86400));
  const handleTrafficClassChange = (value: string) => {
    setTrafficClass(value);
    if (value === "COMPUTE_SERVICE") {
      setTrafficDestinationType("COMPUTE_NODE");
    } else if (value === "TELEMETRY" || value === "BULK_DOWNLINK") {
      setTrafficDestinationType("GROUND_ENDPOINT");
    } else {
      setTrafficDestinationType("SERVICE_ENDPOINT");
    }
  };
  const computeServiceDestinationLocked = trafficClass === "COMPUTE_SERVICE";
  const effectiveTrafficDestinationType = computeServiceDestinationLocked
    ? "COMPUTE_NODE"
    : trafficDestinationType;
  const activeTrafficSummary = generatedConfig?.backend_summary?.traffic_demand_summary;
  const activeTrafficSummaryMatchesControls =
    activeTrafficSummary?.traffic_class === trafficClass &&
    activeTrafficSummary?.destination_type === effectiveTrafficDestinationType;
  const trafficCompatibilityNote = activeTrafficSummaryMatchesControls
    ? activeTrafficSummary?.compatibility_note ??
      activeTrafficSummary?.lifecycle_note ??
      "后端未声明业务约束摘要。"
    : generatedConfig
      ? "参数已修改，重新初始化后刷新后端业务约束摘要。"
      : "初始化后显示后端业务约束摘要。";
  const handleInitialize = () =>
    onRuntimeControl(
      "INITIALIZE",
      initializationControlPayload({
        satellite_count: satelliteCount,
        user_count: userCount,
        compute_nodes: computeNodes,
        compute_capacity: computeCapacity,
        compute_gpu_tflops_fp32: computeGpuFp32,
        compute_npu_tops_int8: computeNpuInt8,
        compute_scheduling_policy: computeSchedulingPolicy,
        mode: runtimeMode,
        speed_factor: effectiveSpeedFactor,
        duration: durationSeconds,
        seed,
        orbit: {
          update_interval_seconds: orbitUpdateIntervalSeconds,
          plane_count: orbitPlaneCount,
          altitude_km: orbitAltitudeKm,
          inclination_deg: orbitInclinationDeg
        },
        traffic_model: {
          flow_interval_seconds: flowIntervalSeconds,
          task_interval_seconds: taskIntervalSeconds,
          flow_demand_capacity: flowDemandCapacity,
          task_compute_demand: taskComputeDemand,
          task_data_size: taskDataSize,
          traffic_class: trafficClass,
          destination_type: effectiveTrafficDestinationType,
          output_data_size: trafficOutputDataSize
        },
        visualization: {
          satellites: showSatellites,
          users: showUsers,
          links: showLinks,
          metrics: showMetrics
        },
        network: {
          application_protocol: applicationProtocol,
          transport_protocol: transportProtocol,
          transport_loss_rate: transportLossRate,
          transport_congestion_window_segments: transportCongestionWindow,
          routing_protocol: routingProtocol,
          datalink_mac_protocol: dataLinkProtocol,
          routing_latency_weight: routingLatencyWeight,
          routing_inverse_capacity_weight: routingInverseCapacityWeight,
          routing_hop_weight: routingHopWeight,
          carrier_frequency_ghz: carrierFrequencyGhz,
          channel_bandwidth_mhz: channelBandwidthMhz,
          rain_rate_mm_h: rainRate,
          rain_attenuation_coefficient_db_per_km_per_mm_h: rainCoefficient,
          rain_effective_path_km: rainPathKm,
          antenna_diameter_m: antennaDiameterM,
          antenna_aperture_efficiency: antennaApertureEfficiency,
          transmit_power_dbw: transmitPowerDbw,
          system_loss_db: systemLossDb,
          noise_temperature_k: noiseTemperatureK
        }
      })
    );

  return (
    <section className="config-panel" aria-label="仿真配置与控制面板">
      <div className="config-panel-header">
        <div className="section-title">仿真控制</div>
        <div className={`runtime-badge ${runtime.status.toLowerCase()}`}>
          {runtimeStatusLabel(runtime)}
        </div>
      </div>

      <div className="config-panel-body">
        <section
          className="config-section command-config-section"
          aria-label={CONFIG_PANEL_SECTION_LABELS.execution}
        >
          <div className="config-section-title">{CONFIG_PANEL_SECTION_LABELS.execution}</div>

          <div className="runtime-actions" aria-label="仿真运行控制">
            <button type="button" disabled={runtimeBusy} onClick={handleInitialize}>
              初始化
            </button>
            <button
              type="button"
              disabled={startDisabled}
              onClick={() => onRuntimeControl("START")}
            >
              开始
            </button>
            <button
              type="button"
              disabled={pauseResume.disabled}
              onClick={() => onRuntimeControl(pauseResume.action)}
            >
              {pauseResume.label}
            </button>
            <button type="button" disabled={runtimeBusy} onClick={() => onRuntimeControl("STOP")}>
              停止
            </button>
            <button type="button" disabled={runtimeBusy} onClick={() => onRuntimeControl("RESET")}>
              重置
            </button>
          </div>
          {controlError !== null && controlError.length > 0 ? (
            <div className="control-feedback error" role="alert">
              {controlError}
            </div>
          ) : null}

          <div className="execution-parameter-grid">
            <div className="control-group emphasized-control priority-mode-control">
              <label className="control-label" htmlFor="runtime-mode">
                运行模式
              </label>
              <select
                id="runtime-mode"
                value={runtimeMode}
                disabled={executionParameterLocked}
                onChange={(event) =>
                  handleRuntimeModeChange(
                    event.currentTarget.value as Exclude<RuntimeMode, "PAUSED">
                  )
                }
              >
                <option value="REAL_TIME">实时运行</option>
                <option value="ACCELERATED">加速运行</option>
              </select>
            </div>

            <div className="control-group">
              <label className="control-label" htmlFor="speed-factor">
                仿真倍率
              </label>
              <div className="control-row numeric-control-row">
                <input
                  id="speed-factor"
                  type="range"
                  min="1"
                  max="100"
                  step="1"
                  value={effectiveSpeedFactor}
                  disabled={speedControlDisabled}
                  onChange={(event) => handleSpeedFactorChange(Number(event.currentTarget.value))}
                />
                <div className="unit-input">
                  <input
                    id="speed-factor-input"
                    type="number"
                    min="1"
                    max="100"
                    step="1"
                    value={effectiveSpeedFactor}
                    disabled={speedControlDisabled}
                    onChange={(event) =>
                      handleSpeedFactorChange(Number(event.currentTarget.value))
                    }
                  />
                  <span>x</span>
                </div>
              </div>
            </div>

            <div className="control-group">
              <label className="control-label" htmlFor="duration-seconds">
                仿真时长
              </label>
              <div className="control-row numeric-control-row">
                <input
                  id="duration-seconds"
                  type="range"
                  min="60"
                  max="86400"
                  step="60"
                  value={durationSeconds}
                  disabled={executionParameterLocked}
                  onChange={(event) =>
                    handleDurationSecondsChange(Number(event.currentTarget.value))
                  }
                />
                <div className="unit-input">
                  <input
                    id="duration-seconds-input"
                    type="number"
                    min="60"
                    max="86400"
                    step="60"
                    value={durationSeconds}
                    disabled={executionParameterLocked}
                    onChange={(event) =>
                      handleDurationSecondsChange(Number(event.currentTarget.value))
                    }
                  />
                  <span>s</span>
                </div>
              </div>
            </div>

            <div className="control-group">
              <label className="control-label" htmlFor="runtime-seed">
                随机种子
              </label>
              <input
                id="runtime-seed"
                type="number"
                min="0"
                step="1"
                value={seed}
                disabled={executionParameterLocked}
                onChange={(event) => setSeed(Number(event.currentTarget.value))}
              />
            </div>
          </div>
          {executionLockReason !== null ? (
            <div className="execution-lock-note" role="status">
              {executionLockReason}
            </div>
          ) : null}

          <div className="runtime-progress" aria-label="仿真进度">
            <div className="summary-title-row">
              <span>仿真进度</span>
              <strong>{progressSummary.percentLabel}</strong>
            </div>
            <progress value={progressSummary.percent} max="100" aria-label="仿真进度条" />
            <div className="runtime-progress-meta">
              <span>
                {progressSummary.elapsedLabel} / {progressSummary.totalLabel}
              </span>
              <span>事件 {progressSummary.eventCountLabel}</span>
            </div>
          </div>
        </section>

        <section className="config-section" aria-label={CONFIG_PANEL_SECTION_LABELS.resources}>
          <div className="config-section-title">{CONFIG_PANEL_SECTION_LABELS.resources}</div>

      <div className="scale-preset-grid" aria-label="场景规模预设">
        {SCENARIO_SCALE_PRESETS.map((preset) => (
          <button
            type="button"
            key={preset.id}
            className={activeScalePreset?.id === preset.id ? "active" : ""}
            onClick={() => handleScalePreset(preset)}
          >
            <span>{preset.label}</span>
            <small>{preset.detail}</small>
          </button>
        ))}
      </div>
      <div className="scale-preset-summary" aria-label="规模预设说明">
        {scalePresetSummary.map((item) => (
          <div className="scale-preset-summary-cell" key={item.label}>
            <span>{item.label}</span>
            <strong>{item.value}</strong>
          </div>
        ))}
      </div>

      <div className="control-group">
        <label className="control-label" htmlFor="satellite-count">
          卫星数量
        </label>
        <div className="control-row numeric-control-row">
          <input
            id="satellite-count"
            type="range"
            min="12"
            max="10000"
            step="12"
            value={satelliteCount}
            onChange={(event) => handleSatelliteCountChange(Number(event.currentTarget.value))}
          />
          <input
            id="satellite-count-input"
            type="number"
            min="12"
            max="10000"
            step="1"
            value={satelliteCount}
            onChange={(event) => handleSatelliteCountChange(Number(event.currentTarget.value))}
          />
        </div>
      </div>

      <div className="control-group">
        <label className="control-label" htmlFor="user-count">
          用户数量
        </label>
        <div className="control-row numeric-control-row">
          <input
            id="user-count"
            type="range"
            min="10"
            max="100000"
            step="10"
            value={userCount}
            onChange={(event) => handleUserCountChange(Number(event.currentTarget.value))}
          />
          <input
            id="user-count-input"
            type="number"
            min="10"
            max="100000"
            step="1"
            value={userCount}
            onChange={(event) => handleUserCountChange(Number(event.currentTarget.value))}
          />
        </div>
      </div>

      <div className="control-group">
        <label className="control-label" htmlFor="compute-node-count">
          算力卫星
        </label>
        <div className="control-row numeric-control-row">
          <input
            id="compute-node-count"
            type="range"
            min="1"
            max={satelliteCount}
            step="1"
            value={computeNodes}
            onChange={(event) => handleComputeNodesChange(Number(event.currentTarget.value))}
          />
          <input
            id="compute-node-count-input"
            type="number"
            min="1"
            max={satelliteCount}
            step="1"
            value={computeNodes}
            onChange={(event) => handleComputeNodesChange(Number(event.currentTarget.value))}
          />
        </div>
      </div>

      <div className="control-group">
        <label className="control-label" htmlFor="compute-capacity">
          CPU FP32（GFLOPS）
        </label>
        <input
          id="compute-capacity"
          type="number"
          min="0.1"
          step="0.1"
          value={computeCapacity}
          onChange={(event) => setComputeCapacity(Number(event.currentTarget.value))}
        />
      </div>

      <div className="control-group">
        <label className="control-label" htmlFor="compute-cpu-gflops-fp64">
          CPU FP64（GFLOPS）
        </label>
        <input
          id="compute-cpu-gflops-fp64"
          type="number"
          min="0"
          step="0.1"
          value={computeCpuFp64}
          onChange={(event) =>
            setComputeCpuFp64(nonNegativeNumber(Number(event.currentTarget.value)))
          }
        />
      </div>

      <div className="control-group">
        <label className="control-label" htmlFor="compute-gpu-tflops-fp32">
          GPU FP32（TFLOPS）
        </label>
        <input
          id="compute-gpu-tflops-fp32"
          type="number"
          min="0"
          step="0.1"
          value={computeGpuFp32}
          onChange={(event) =>
            setComputeGpuFp32(nonNegativeNumber(Number(event.currentTarget.value)))
          }
        />
      </div>

      <div className="control-group">
        <label className="control-label" htmlFor="compute-gpu-tflops-fp16">
          GPU FP16（TFLOPS）
        </label>
        <input
          id="compute-gpu-tflops-fp16"
          type="number"
          min="0"
          step="0.1"
          value={computeGpuFp16}
          onChange={(event) =>
            setComputeGpuFp16(nonNegativeNumber(Number(event.currentTarget.value)))
          }
        />
      </div>

      <div className="control-group">
        <label className="control-label" htmlFor="compute-npu-tops-int8">
          NPU INT8（TOPS）
        </label>
        <input
          id="compute-npu-tops-int8"
          type="number"
          min="0"
          step="0.1"
          value={computeNpuInt8}
          onChange={(event) =>
            setComputeNpuInt8(nonNegativeNumber(Number(event.currentTarget.value)))
          }
        />
      </div>

      <div className="control-group">
        <label className="control-label" htmlFor="compute-memory-gb">
          内存（GB）
        </label>
        <input
          id="compute-memory-gb"
          type="number"
          min="0"
          step="1"
          value={computeMemoryGb}
          onChange={(event) =>
            setComputeMemoryGb(nonNegativeNumber(Number(event.currentTarget.value)))
          }
        />
      </div>

      <div className="control-group">
        <label className="control-label" htmlFor="compute-storage-gb">
          存储（GB）
        </label>
        <input
          id="compute-storage-gb"
          type="number"
          min="0"
          step="1"
          value={computeStorageGb}
          onChange={(event) =>
            setComputeStorageGb(nonNegativeNumber(Number(event.currentTarget.value)))
          }
        />
      </div>

      <div className="control-group">
        <label className="control-label" htmlFor="compute-scheduling-policy">
          调度策略
        </label>
        <select
          id="compute-scheduling-policy"
          value={computeSchedulingPolicy}
          onChange={(event) => setComputeSchedulingPolicy(event.currentTarget.value)}
        >
          <option value="FIFO">先到先服务</option>
          <option value="SHORTEST_JOB_FIRST">短作业优先</option>
          <option value="EARLIEST_DEADLINE_FIRST">最早截止期优先</option>
        </select>
      </div>
        </section>

        <section className="config-section" aria-label={CONFIG_PANEL_SECTION_LABELS.orbit}>
          <div className="config-section-title">{CONFIG_PANEL_SECTION_LABELS.orbit}</div>
      <div className="channel-grid" aria-label="轨道参数">
        <div className="control-group">
          <label className="control-label" htmlFor="orbit-update-interval">
            轨道步长
          </label>
          <div className="unit-input">
            <input
              id="orbit-update-interval"
              type="number"
              min="1"
              step="1"
              value={orbitUpdateIntervalSeconds}
              onChange={(event) =>
                setOrbitUpdateIntervalSeconds(Number(event.currentTarget.value))
              }
            />
            <span>s</span>
          </div>
        </div>

        <div className="control-group">
          <label className="control-label" htmlFor="orbit-plane-count">
            轨道面数
          </label>
          <input
            id="orbit-plane-count"
            type="number"
            min="1"
            step="1"
            value={orbitPlaneCount}
            onChange={(event) => setOrbitPlaneCount(Number(event.currentTarget.value))}
          />
        </div>

        <div className="control-group">
          <label className="control-label" htmlFor="orbit-altitude">
            轨道高度
          </label>
          <div className="unit-input">
            <input
              id="orbit-altitude"
              type="number"
              min="160"
              step="10"
              value={orbitAltitudeKm}
              onChange={(event) => setOrbitAltitudeKm(Number(event.currentTarget.value))}
            />
            <span>km</span>
          </div>
        </div>

        <div className="control-group">
          <label className="control-label" htmlFor="orbit-inclination">
            轨道倾角
          </label>
          <div className="unit-input">
            <input
              id="orbit-inclination"
              type="number"
              min="0"
              max="180"
              step="0.1"
              value={orbitInclinationDeg}
              onChange={(event) => setOrbitInclinationDeg(Number(event.currentTarget.value))}
            />
            <span>°</span>
          </div>
        </div>
      </div>
      <div className="orbit-motion-explanation" aria-label="轨道运动说明">
        {orbitMotionExplanations.map((item) => (
          <div className="orbit-motion-row" key={item.label}>
            <span>{item.label}</span>
            <strong>{item.value}</strong>
            <small>{item.detail}</small>
          </div>
        ))}
      </div>
        </section>

        <section className="config-section" aria-label={CONFIG_PANEL_SECTION_LABELS.traffic}>
          <div className="config-section-title">{CONFIG_PANEL_SECTION_LABELS.traffic}</div>
      <div className="channel-grid" aria-label="流量与任务需求">
        <div className="control-group">
          <label className="control-label" htmlFor="traffic-class">
            业务类型
          </label>
          <select
            id="traffic-class"
            value={trafficClass}
            onChange={(event) => handleTrafficClassChange(event.currentTarget.value)}
          >
            <option value="COMPUTE_SERVICE">通信-计算服务</option>
            <option value="DATA_TRANSFER">数据传输</option>
            <option value="TELEMETRY">遥测</option>
            <option value="BULK_DOWNLINK">批量下传</option>
          </select>
        </div>

        <div className="control-group">
          <label className="control-label" htmlFor="traffic-destination-type">
            目的类型
          </label>
          <select
            id="traffic-destination-type"
            value={effectiveTrafficDestinationType}
            disabled={computeServiceDestinationLocked}
            onChange={(event) => setTrafficDestinationType(event.currentTarget.value)}
          >
            <option value="COMPUTE_NODE">星上算力节点</option>
            <option value="GROUND_ENDPOINT">地面端</option>
            <option value="SATELLITE">卫星节点</option>
            <option value="SERVICE_ENDPOINT">服务端点</option>
          </select>
        </div>

        <div className="traffic-compatibility-note">
          {trafficCompatibilityNote}
        </div>

        <div className="control-group">
          <label className="control-label" htmlFor="flow-interval">
            流量间隔
          </label>
          <div className="unit-input">
            <input
              id="flow-interval"
              type="number"
              min="1"
              step="1"
              value={flowIntervalSeconds}
              onChange={(event) => setFlowIntervalSeconds(Number(event.currentTarget.value))}
            />
            <span>s</span>
          </div>
        </div>

        <div className="control-group">
          <label className="control-label" htmlFor="task-interval">
            任务间隔
          </label>
          <div className="unit-input">
            <input
              id="task-interval"
              type="number"
              min="1"
              step="1"
              value={taskIntervalSeconds}
              onChange={(event) => setTaskIntervalSeconds(Number(event.currentTarget.value))}
            />
            <span>s</span>
          </div>
        </div>

        <div className="control-group">
          <label className="control-label" htmlFor="flow-demand">
            带宽需求
          </label>
          <div className="unit-input">
            <input
              id="flow-demand"
              type="number"
              min="0.1"
              step="0.1"
              value={flowDemandCapacity}
              onChange={(event) => setFlowDemandCapacity(Number(event.currentTarget.value))}
            />
            <span>Mbps</span>
          </div>
        </div>

        <div className="control-group">
          <label className="control-label" htmlFor="task-compute-demand">
            算力需求
          </label>
          <input
            id="task-compute-demand"
            type="number"
            min="0.1"
            step="0.1"
            value={taskComputeDemand}
            onChange={(event) => setTaskComputeDemand(Number(event.currentTarget.value))}
          />
        </div>

        <div className="control-group">
          <label className="control-label" htmlFor="task-data-size">
            输入数据量
          </label>
          <div className="unit-input">
            <input
              id="task-data-size"
              type="number"
              min="0.1"
              step="0.1"
              value={taskDataSize}
              onChange={(event) => setTaskDataSize(Number(event.currentTarget.value))}
            />
            <span>MB</span>
          </div>
        </div>

        <div className="control-group">
          <label className="control-label" htmlFor="traffic-output-data-size">
            输出数据量
          </label>
          <div className="unit-input">
            <input
              id="traffic-output-data-size"
              type="number"
              min="0"
              step="0.1"
              value={trafficOutputDataSize}
              onChange={(event) =>
                setTrafficOutputDataSize(nonNegativeNumber(Number(event.currentTarget.value)))
              }
            />
            <span>MB</span>
          </div>
        </div>
      </div>
        </section>

        <section className="config-section" aria-label={CONFIG_PANEL_SECTION_LABELS.runtime}>
          <div className="config-section-title">{CONFIG_PANEL_SECTION_LABELS.runtime}</div>
      <div className="control-group">
        <div className="control-label">可视化图层</div>
        <div className="toggle-grid" aria-label="可视化图层开关">
          <label>
            <input
              type="checkbox"
              checked={showSatellites}
              onChange={(event) => setShowSatellites(event.currentTarget.checked)}
            />
            <span>卫星</span>
          </label>
          <label>
            <input
              type="checkbox"
              checked={showUsers}
              onChange={(event) => setShowUsers(event.currentTarget.checked)}
            />
            <span>用户</span>
          </label>
          <label>
            <input
              type="checkbox"
              checked={showLinks}
              onChange={(event) => setShowLinks(event.currentTarget.checked)}
            />
            <span>链路</span>
          </label>
          <label>
            <input
              type="checkbox"
              checked={showMetrics}
              onChange={(event) => setShowMetrics(event.currentTarget.checked)}
            />
            <span>轨迹</span>
          </label>
        </div>
        <div className="layer-effect-list" aria-label="可视化图层作用">
          {visualizationLayerEffects.map((item) => (
            <div className="layer-effect-row" key={item.label}>
              <span>{item.label}</span>
              <strong>{item.stateLabel}</strong>
              <small>{item.detail}</small>
            </div>
          ))}
        </div>
      </div>
        </section>

        <section className="config-section" aria-label={CONFIG_PANEL_SECTION_LABELS.network}>
          <div className="config-section-title">{CONFIG_PANEL_SECTION_LABELS.network}</div>
      <div className="scale-preset-grid network-quality-preset-grid" aria-label="网络质量预设">
        {NETWORK_QUALITY_PRESETS.map((preset) => (
          <button
            type="button"
            key={preset.id}
            className={activeNetworkQualityPreset?.id === preset.id ? "active" : ""}
            onClick={() => handleNetworkQualityPreset(preset)}
          >
            <span>{preset.label}</span>
            <small>{preset.detail}</small>
          </button>
        ))}
      </div>
      <div className="control-group">
        <label className="control-label" htmlFor="application-protocol">
          应用协议
        </label>
        <select
          id="application-protocol"
          value={applicationProtocol}
          onChange={(event) => setApplicationProtocol(event.currentTarget.value)}
        >
          <option value="TASK_OFFLOAD_FLOW">任务卸载</option>
          <option value="HTTP">HTTP</option>
          <option value="MQTT">MQTT</option>
          <option value="TELEMETRY">遥测流</option>
        </select>
      </div>

      <div className="control-group">
        <label className="control-label" htmlFor="transport-protocol">
          传输协议
        </label>
        <select
          id="transport-protocol"
          value={transportProtocol}
          onChange={(event) => setTransportProtocol(event.currentTarget.value)}
        >
          <option value="TCP">TCP</option>
          <option value="UDP">UDP</option>
        </select>
      </div>

      <div className="channel-grid" aria-label="传输层参数">
        <div className="control-group">
          <label className="control-label" htmlFor="transport-loss-rate">
            传输丢包率
          </label>
          <input
            id="transport-loss-rate"
            type="number"
            min="0"
            max="0.99"
            step="0.001"
            value={transportLossRate}
            onChange={(event) => setTransportLossRate(Number(event.currentTarget.value))}
          />
        </div>

        <div className="control-group">
          <label className="control-label" htmlFor="transport-window">
            拥塞窗口
          </label>
          <div className="unit-input">
            <input
              id="transport-window"
              type="number"
              min="0"
              step="1"
              value={transportCongestionWindow}
              onChange={(event) =>
                setTransportCongestionWindow(Number(event.currentTarget.value))
              }
            />
            <span>段</span>
          </div>
        </div>
      </div>

      <div className="control-group">
        <label className="control-label" htmlFor="datalink-mac-protocol">
          链路层 MAC
        </label>
        <select
          id="datalink-mac-protocol"
          value={dataLinkProtocol}
          onChange={(event) => setDataLinkProtocol(event.currentTarget.value)}
        >
          <option value="TDMA">TDMA</option>
          <option value="SLOTTED_ALOHA">Slotted ALOHA</option>
          <option value="CSMA_CA">CSMA/CA</option>
        </select>
      </div>

      <div className="control-group">
        <label className="control-label" htmlFor="routing-protocol">
          路由协议
        </label>
        <select
          id="routing-protocol"
          value={routingProtocol}
          onChange={(event) => setRoutingProtocol(event.currentTarget.value)}
        >
          <option value="LINK_STATE">链路状态</option>
          <option value="SHORTEST_PATH">最短路径</option>
          <option value="DISTANCE_VECTOR">距离向量</option>
        </select>
      </div>

      <div className="channel-grid" aria-label="路由代价权重">
        <div className="control-group">
          <label className="control-label" htmlFor="routing-latency-weight">
            时延权重
          </label>
          <input
            id="routing-latency-weight"
            type="number"
            min="0"
            step="0.1"
            value={routingLatencyWeight}
            onChange={(event) => setRoutingLatencyWeight(Number(event.currentTarget.value))}
          />
        </div>

        <div className="control-group">
          <label className="control-label" htmlFor="routing-capacity-weight">
            容量偏好
          </label>
          <input
            id="routing-capacity-weight"
            type="number"
            min="0"
            step="1"
            value={routingInverseCapacityWeight}
            onChange={(event) =>
              setRoutingInverseCapacityWeight(Number(event.currentTarget.value))
            }
          />
        </div>

        <div className="control-group">
          <label className="control-label" htmlFor="routing-hop-weight">
            跳数权重
          </label>
          <input
            id="routing-hop-weight"
            type="number"
            min="0"
            step="0.1"
            value={routingHopWeight}
            onChange={(event) => setRoutingHopWeight(Number(event.currentTarget.value))}
          />
        </div>
      </div>
        </section>

        <section className="config-section" aria-label={CONFIG_PANEL_SECTION_LABELS.physical}>
          <div className="config-section-title">{CONFIG_PANEL_SECTION_LABELS.physical}</div>
      <div className="channel-grid" aria-label="信道参数">
        <div className="control-group">
          <label className="control-label" htmlFor="carrier-frequency">
            载波频率
          </label>
          <div className="unit-input">
            <input
              id="carrier-frequency"
              type="number"
              min="1"
              step="0.1"
              value={carrierFrequencyGhz}
              onChange={(event) => setCarrierFrequencyGhz(Number(event.currentTarget.value))}
            />
            <span>GHz</span>
          </div>
        </div>

        <div className="control-group">
          <label className="control-label" htmlFor="channel-bandwidth">
            信道带宽
          </label>
          <div className="unit-input">
            <input
              id="channel-bandwidth"
              type="number"
              min="1"
              step="1"
              value={channelBandwidthMhz}
              onChange={(event) => setChannelBandwidthMhz(Number(event.currentTarget.value))}
            />
            <span>MHz</span>
          </div>
        </div>

        <div className="control-group">
          <label className="control-label" htmlFor="rain-rate">
            雨强
          </label>
          <div className="unit-input">
            <input
              id="rain-rate"
              type="number"
              min="0"
              step="0.5"
              value={rainRate}
              onChange={(event) => setRainRate(Number(event.currentTarget.value))}
            />
            <span>mm/h</span>
          </div>
        </div>

        <div className="control-group">
          <label className="control-label" htmlFor="rain-coefficient">
            雨衰系数
          </label>
          <input
            id="rain-coefficient"
            type="number"
            min="0"
            step="0.001"
            value={rainCoefficient}
            onChange={(event) => setRainCoefficient(Number(event.currentTarget.value))}
          />
        </div>

        <div className="control-group">
          <label className="control-label" htmlFor="rain-path">
            等效雨区
          </label>
          <div className="unit-input">
            <input
              id="rain-path"
              type="number"
              min="0"
              step="0.5"
              value={rainPathKm}
              onChange={(event) => setRainPathKm(Number(event.currentTarget.value))}
            />
            <span>km</span>
          </div>
        </div>

        <div className="control-group">
          <label className="control-label" htmlFor="antenna-diameter">
            天线口径
          </label>
          <div className="unit-input">
            <input
              id="antenna-diameter"
              type="number"
              min="0.05"
              step="0.01"
              value={antennaDiameterM}
              onChange={(event) => setAntennaDiameterM(Number(event.currentTarget.value))}
            />
            <span>m</span>
          </div>
        </div>

        <div className="control-group">
          <label className="control-label" htmlFor="antenna-efficiency">
            孔径效率
          </label>
          <div className="unit-input">
            <input
              id="antenna-efficiency"
              type="number"
              min="0.05"
              max="1"
              step="0.01"
              value={antennaApertureEfficiency}
              onChange={(event) =>
                setAntennaApertureEfficiency(Number(event.currentTarget.value))
              }
            />
            <span>η</span>
          </div>
        </div>

        <div className="control-group">
          <label className="control-label" htmlFor="transmit-power">
            发射功率
          </label>
          <div className="unit-input">
            <input
              id="transmit-power"
              type="number"
              step="0.5"
              value={transmitPowerDbw}
              onChange={(event) => setTransmitPowerDbw(Number(event.currentTarget.value))}
            />
            <span>dBW</span>
          </div>
        </div>

        <div className="control-group">
          <label className="control-label" htmlFor="system-loss">
            系统损耗
          </label>
          <div className="unit-input">
            <input
              id="system-loss"
              type="number"
              min="0"
              step="0.1"
              value={systemLossDb}
              onChange={(event) => setSystemLossDb(Number(event.currentTarget.value))}
            />
            <span>dB</span>
          </div>
        </div>

        <div className="control-group">
          <label className="control-label" htmlFor="noise-temperature">
            噪声温度
          </label>
          <div className="unit-input">
            <input
              id="noise-temperature"
              type="number"
              min="1"
              step="1"
              value={noiseTemperatureK}
              onChange={(event) => setNoiseTemperatureK(Number(event.currentTarget.value))}
            />
            <span>K</span>
          </div>
        </div>
      </div>
        </section>

        <section
          className="config-section"
          aria-label={CONFIG_PANEL_SECTION_LABELS.activeScenario}
        >
          <div className="config-section-title">
            {CONFIG_PANEL_SECTION_LABELS.activeScenario}
          </div>
      <div className="generated-config-summary" aria-label="当前生效场景">
        <div className="summary-title-row">
          <span>当前生效场景</span>
          <strong>配置版本 {runtime.config_version}</strong>
        </div>
        <div className="summary-grid">
          {summaryItems.map((item) => (
            <div className="summary-cell" key={item.label}>
              <span>{item.label}</span>
              <strong>{item.value}</strong>
            </div>
          ))}
        </div>
        <div className="configuration-template-summary" aria-label="详细配置模板">
          <div className="summary-title-row">
            <span>详细配置模板</span>
            <strong>{templateItems.length > 0 ? "后端声明" : "等待初始化"}</strong>
          </div>
          <div className="configuration-template-list">
            {templateItems.length > 0 ? (
              templateItems.map((item) => (
                <div className="configuration-template-item" key={item.label}>
                  <span>{item.label}</span>
                  <strong>{item.value}</strong>
                  {item.detail ? <small>{item.detail}</small> : null}
                  {item.templateId ? (
                    <button
                      type="button"
                      aria-label={`加载${item.label}`}
                      data-template-id={item.templateId}
                      disabled={runtimeBusy || executionParameterLocked}
                      onClick={() =>
                        onRuntimeControl("LOAD_TEMPLATE", {
                          template_id: item.templateId
                        })
                      }
                    >
                      加载模板
                    </button>
                  ) : null}
                </div>
              ))
            ) : (
              <div className="configuration-template-item empty">
                <span>模板</span>
                <strong>初始化后显示完整 YAML 模板路径</strong>
              </div>
            )}
          </div>
        </div>
      </div>
        </section>
      </div>
    </section>
  );
}

export function generatedScenarioSummaryItems(
  config: GeneratedScenarioConfig | null | undefined
): readonly ConfigSummaryItem[] {
  if (config === null || config === undefined) {
    return [{ label: "生成场景", value: "等待初始化" }];
  }
  const backendSummary = config.backend_summary;
  const constellation = backendSummary?.derived_constellation_summary;
  const traffic = backendSummary?.traffic_demand_summary;
  const compute = backendSummary?.compute_resource_summary;
  const coverage = backendSummary?.coverage_beam_summary;
  return [
    { label: "生效卫星", value: formatInteger(config.satellite_count) },
    { label: "生效用户", value: formatInteger(config.user_count) },
    { label: "算力卫星", value: formatInteger(config.compute_node_count) },
    {
      label: "星座剖面",
      value: formatConstellationProfile(constellation?.profile)
    },
    {
      label: "每面卫星",
      value: formatInteger(constellation?.satellites_per_plane ?? 0)
    },
    {
      label: "RAAN 间隔",
      value:
        constellation?.raan_spacing_deg !== undefined
          ? `${formatDecimal(constellation.raan_spacing_deg)}°`
          : "待初始化"
    },
    {
      label: "相位策略",
      value: formatPhasePolicy(constellation?.phase_policy)
    },
    {
      label: "业务类型",
      value: traffic?.traffic_class_label ?? formatTrafficClass(traffic?.traffic_class ?? config.application_protocol)
    },
    {
      label: "业务流量",
      value: formatInteger(traffic?.generated_flow_count ?? config.flow_count)
    },
    {
      label: "目的类型",
      value: traffic?.destination_type_label ?? formatTrafficDestination(traffic?.destination_type)
    },
    {
      label: "输入数据",
      value: formatDataMegabytes(traffic?.input_data_size_mb ?? config.task_data_size)
    },
    {
      label: "输出数据",
      value: formatDataMegabytes(
        traffic?.output_data_size_mb ?? config.traffic_output_data_size ?? 0
      )
    },
    {
      label: "执行形态",
      value: traffic?.execution_label ?? formatTrafficExecutionMode(traffic?.traffic_class)
    },
    {
      label: "业务约束",
      value: traffic?.compatibility_note ?? "待初始化"
    },
    {
      label: "FP32 算力",
      value: compute
        ? `${formatDecimal(compute.total_cpu_gflops_fp32)} GFLOPS`
        : `${formatDecimal(config.compute_capacity * config.compute_node_count)} GFLOPS`
    },
    {
      label: "模型假设",
      value: formatModelAssumption(backendSummary?.model_assumptions?.[0])
    },
    {
      label: "GPU FP32",
      value: `${formatDecimal(compute?.total_gpu_tflops_fp32 ?? 0)} TFLOPS`
    },
    {
      label: "GPU FP16",
      value: `${formatDecimal(compute?.total_gpu_tflops_fp16 ?? 0)} TFLOPS`
    },
    {
      label: "NPU INT8",
      value: `${formatDecimal(compute?.total_npu_tops_int8 ?? 0)} TOPS`
    },
    {
      label: "内存/存储",
      value: `${formatDecimal(compute?.total_memory_gb ?? 0)} / ${formatDecimal(
        compute?.total_storage_gb ?? 0
      )} GB`
    },
    {
      label: "波束模式",
      value: formatBeamPattern(coverage?.beam_pattern)
    },
    {
      label: "覆盖保真",
      value: formatCoverageFidelityLevel(coverage?.fidelity_level)
    },
    {
      label: "足迹交集",
      value: formatCoverageIntersectionPolicy(coverage?.footprint_intersection_policy)
    },
    {
      label: "默认波束",
      value: `${formatInteger(coverage?.default_beam_count ?? 7)} 个`
    },
    {
      label: "波束半径",
      value: `${formatInteger((coverage?.beam_radius_m ?? 160_000) / 1000)} km`
    },
    { label: "调度策略", value: formatComputeSchedulingPolicy(config.compute_scheduling_policy) },
    { label: "轨道面", value: formatInteger(constellation?.plane_count ?? config.orbit_plane_count) },
    { label: "随机种子", value: formatInteger(config.seed) },
    { label: "应用协议", value: formatApplicationProtocol(config.application_protocol) },
    { label: "传输协议", value: config.transport_protocol ?? "TCP" },
    { label: "传输丢包", value: formatLossRate(config.transport_loss_rate) },
    { label: "拥塞窗口", value: formatCongestionWindow(config.transport_congestion_window_segments) },
    { label: "路由协议", value: config.routing_protocol ?? "LINK_STATE" },
    { label: "路由权重", value: formatRoutingWeights(config) },
    { label: "载波频率", value: formatFrequency(config.carrier_frequency_hz) },
    { label: "信道带宽", value: formatBandwidth(config.channel_bandwidth_hz) },
    { label: "雨强", value: formatRainRate(config.rain_rate_mm_h) },
    { label: "天线口径", value: formatMeters(config.antenna_diameter_m) },
    { label: "孔径效率", value: formatEfficiency(config.antenna_aperture_efficiency) },
    { label: "发射功率", value: formatDbw(config.transmit_power_dbw) },
    { label: "系统损耗", value: formatDb(config.system_loss_db) },
    { label: "噪声温度", value: formatKelvin(config.noise_temperature_k) },
    {
      label: "轨道高度",
      value: `${formatInteger(
        (constellation?.altitude_m ?? (config.semi_major_axis_km - config.earth_radius_km) * 1000) /
          1000
      )} km`
    },
    {
      label: "轨道周期",
      value: `${formatDecimal(
        constellation?.orbital_period_minutes ??
          circularOrbitalPeriodMinutes(
            (config.semi_major_axis_km - config.earth_radius_km) * 1000
          )
      )} min`
    },
    {
      label: "轨道速度",
      value: `${formatDecimal(
        constellation?.orbital_velocity_km_s ??
          circularOrbitalVelocityKmS(
            (config.semi_major_axis_km - config.earth_radius_km) * 1000
          )
      )} km/s`
    },
    {
      label: "倾角",
      value: `${formatDecimal(constellation?.inclination_deg ?? config.inclination_deg)}°`
    }
  ];
}

export function configurationTemplateSummaryItems(
  config: GeneratedScenarioConfig | null | undefined
): readonly ConfigSummaryItem[] {
  const surface = config?.backend_summary?.configuration_surface_summary;
  if (surface === undefined) {
    return [];
  }
  const profiles = surface.template_profiles ?? [];
  const fileOnlySections = surface.file_only_sections ?? [];
  return [
    {
      label: "详细配置文件",
      value: surface.detailed_config_file,
      detail: "运行态生成配置，不应作为产品提交。"
    },
    {
      label: "前端配置策略",
      value: surface.frontend_policy,
      detail: `${formatInteger(surface.key_field_count)} 个关键字段 / ${formatInteger(
        surface.detailed_field_count
      )} 个完整字段`
    },
    ...fileOnlySections.map((section) => ({
      label: `YAML 专用：${configurationSectionDisplayLabel(section.section)}`,
      value: `${formatInteger(section.field_count)} 个字段`,
      detail: `${section.purpose} 示例：${section.example_paths.slice(0, 3).join(", ")}`
    })),
    ...profiles.map((profile) => ({
      label: profile.label,
      value: profile.path,
      detail: configurationTemplateProfileDetail(profile),
      templateId: profile.id
    }))
  ];
}

export function configurationTemplateProfileDetail(
  profile: {
    purpose: string;
    scale?: string;
    expected_kpi_behavior?: string;
    fidelity_mode?: string;
    recommended_use?: string;
  }
): string {
  return [
    profile.purpose,
    profile.scale ? `规模: ${profile.scale}` : null,
    profile.fidelity_mode ? `保真: ${profile.fidelity_mode}` : null,
    profile.expected_kpi_behavior ? `KPI: ${profile.expected_kpi_behavior}` : null,
    profile.recommended_use ? `用途: ${profile.recommended_use}` : null
  ]
    .filter((item): item is string => typeof item === "string" && item.length > 0)
    .join(" | ");
}

function configurationSectionDisplayLabel(section: string): string {
  const labels: Record<string, string> = {
    scenario: "场景",
    "scenario.orbit": "轨道",
    "scenario.traffic_model": "业务生成",
    network: "网络",
    runtime: "运行时",
    ui: "界面",
    "ui.visualization": "可视化"
  };
  return labels[section] ?? section;
}

export interface PauseResumeControl {
  label: string;
  action: RuntimeAction;
  disabled: boolean;
}

export function pauseResumeControl(runtime: RuntimeStatusPayload): PauseResumeControl {
  if (runtimeControlBusy(runtime)) {
    return {
      label: runtime.status === "PAUSED" ? "继续" : "暂停",
      action: runtime.status === "PAUSED" ? "RESUME" : "PAUSE",
      disabled: true
    };
  }
  if (runtime.status === "PAUSED") {
    return {
      label: "继续",
      action: "RESUME",
      disabled: false
    };
  }
  return {
    label: "暂停",
    action: "PAUSE",
    disabled: runtime.status !== "RUNNING"
  };
}

export function startControlDisabled(runtime: RuntimeStatusPayload): boolean {
  return (
    runtimeControlBusy(runtime) ||
    runtime.initialized !== true ||
    runtime.status !== "STOPPED"
  );
}

export function runtimeControlBusy(runtime: RuntimeStatusPayload): boolean {
  return typeof runtime.last_action === "string" && runtime.last_action.endsWith("_PENDING");
}

export function runtimeExecutionParametersLocked(runtime: RuntimeStatusPayload): boolean {
  return runtimeExecutionParameterLockReason(runtime) !== null;
}

export function runtimeExecutionParameterLockReason(
  runtime: RuntimeStatusPayload
): string | null {
  if (runtimeControlBusy(runtime)) {
    return "控制命令处理中，暂时锁定运行模式、倍率、时长和种子。";
  }
  if (runtime.status === "COMPLETED" || runtime.lifecycle_state === "COMPLETED") {
    return "仿真已完成，运行模式、倍率、时长和种子已锁定；如需重新配置请先重置，再重新初始化。";
  }
  if (runtime.status === "RUNNING" || runtime.lifecycle_state === "RUNNING") {
    return "仿真运行中，运行模式、倍率、时长和种子已锁定。";
  }
  if (runtime.initialized === true) {
    return "当前仿真 session 已初始化，运行模式、倍率、时长和种子已绑定；如需修改请先重置，再重新初始化。";
  }
  return null;
}

export function runtimeProgressSummary(
  progress: RuntimeProgressValues
): RuntimeProgressSummary {
  const duration = Math.max(1, progress.duration);
  const elapsed = Math.min(Math.max(0, progress.sim_time), duration);
  const percent = Math.min(100, Math.max(0, (elapsed / duration) * 100));
  return {
    elapsedLabel: formatDurationCompact(elapsed),
    totalLabel: formatDurationCompact(duration),
    eventCountLabel: formatInteger(progress.event_count),
    percent,
    percentLabel: `${formatDecimal(percent)}%`
  };
}

export function visualizationControlPayload(
  visualization: VisualizationControlValues
): VisualizationControlValues {
  return {
    satellites: visualization.satellites,
    links: visualization.links,
    users: visualization.users,
    metrics: visualization.metrics
  };
}

export function orbitMotionExplanationItems({
  updateIntervalSeconds,
  altitudeM,
  orbitalPeriodMinutes,
  orbitalVelocityKmS
}: {
  updateIntervalSeconds: number;
  altitudeM: number;
  orbitalPeriodMinutes?: number;
  orbitalVelocityKmS?: number;
}): readonly OrbitMotionExplanationItem[] {
  const boundedUpdateIntervalSeconds = Math.max(1, Math.round(updateIntervalSeconds));
  const periodMinutes = orbitalPeriodMinutes ?? circularOrbitalPeriodMinutes(altitudeM);
  const velocityKmS = orbitalVelocityKmS ?? circularOrbitalVelocityKmS(altitudeM);
  const samplesPerOrbit = Math.max(
    1,
    Math.round((periodMinutes * 60) / boundedUpdateIntervalSeconds)
  );

  return [
    {
      label: "采样步长",
      value: `${formatInteger(boundedUpdateIntervalSeconds)} s`,
      detail: "控制后端轨道状态刷新频率，不代表卫星绕行周期"
    },
    {
      label: "近圆轨道",
      value: `${formatDecimal(velocityKmS)} km/s`,
      detail: `约 ${formatDecimal(periodMinutes)} min 完成一圈，低轨卫星不是几分钟绕地一圈`
    },
    {
      label: "显示运动",
      value: `${formatInteger(samplesPerOrbit)} 点/圈`,
      detail: "前端在轨道样本之间插值/跟随，流畅度还受直播批量与渲染帧率影响"
    }
  ];
}

export function visualizationLayerEffectItems(
  visualization: VisualizationControlValues
): readonly VisualizationLayerEffectItem[] {
  return [
    {
      label: "卫星",
      stateLabel: visualization.satellites ? "显示" : "隐藏",
      detail: "控制卫星点、卫星图标和三维卫星模型"
    },
    {
      label: "用户",
      stateLabel: visualization.users ? "显示" : "隐藏",
      detail: "控制地面用户与地面站点"
    },
    {
      label: "链路",
      stateLabel: visualization.links ? "显示" : "隐藏",
      detail: "控制接入链路、星间链路和路由线"
    },
    {
      label: "轨迹",
      stateLabel: visualization.metrics ? "显示" : "隐藏",
      detail: "控制轨道轨迹、覆盖波束和路由辅助层"
    }
  ];
}

export function orbitControlPayload(orbit: OrbitControlValues): Record<string, unknown> {
  return {
    update_interval_seconds: orbit.update_interval_seconds,
    plane_count: orbit.plane_count,
    altitude_m: orbit.altitude_km * 1000,
    inclination_deg: orbit.inclination_deg
  };
}

export function trafficControlPayload(traffic: TrafficControlValues): Record<string, unknown> {
  return {
    flow_interval_seconds: traffic.flow_interval_seconds,
    task_interval_seconds: traffic.task_interval_seconds,
    flow_demand_capacity: traffic.flow_demand_capacity,
    task_compute_demand: traffic.task_compute_demand,
    task_data_size: traffic.task_data_size,
    traffic_class: traffic.traffic_class ?? "COMPUTE_SERVICE",
    destination_type: traffic.destination_type ?? "COMPUTE_NODE",
    output_data_size: traffic.output_data_size ?? 0
  };
}

export function initializationControlPayload(
  values: InitializationControlValues
): Record<string, unknown> {
  const payload: Record<string, unknown> = {
    satellite_count: values.satellite_count,
    user_count: values.user_count,
    compute_nodes: values.compute_nodes,
    compute_capacity: values.compute_capacity,
    compute_scheduling_policy: values.compute_scheduling_policy,
    mode: values.mode,
    speed_factor: runtimeEffectiveSpeedFactor(values.mode, values.speed_factor),
    duration: values.duration,
    seed: values.seed,
    orbit: orbitControlPayload(values.orbit),
    traffic_model: trafficControlPayload(values.traffic_model),
    visualization: visualizationControlPayload(values.visualization),
    ...networkKeyControlPayload(values.network)
  };
  if (values.compute_cpu_gflops_fp64 !== undefined) {
    payload.compute_cpu_gflops_fp64 = values.compute_cpu_gflops_fp64;
  }
  if (values.compute_gpu_tflops_fp32 !== undefined) {
    payload.compute_gpu_tflops_fp32 = values.compute_gpu_tflops_fp32;
  }
  if (values.compute_gpu_tflops_fp16 !== undefined) {
    payload.compute_gpu_tflops_fp16 = values.compute_gpu_tflops_fp16;
  }
  if (values.compute_npu_tops_int8 !== undefined) {
    payload.compute_npu_tops_int8 = values.compute_npu_tops_int8;
  }
  if (values.compute_memory_gb !== undefined) {
    payload.compute_memory_gb = values.compute_memory_gb;
  }
  if (values.compute_storage_gb !== undefined) {
    payload.compute_storage_gb = values.compute_storage_gb;
  }
  return payload;
}

export function networkKeyControlPayload(
  network: NetworkControlValues
): Record<string, unknown> {
  return {
    application_protocol: network.application_protocol,
    transport_protocol: network.transport_protocol,
    transport_loss_rate: network.transport_loss_rate,
    transport_congestion_window_segments: network.transport_congestion_window_segments,
    routing_protocol: network.routing_protocol,
    datalink_mac_protocol: network.datalink_mac_protocol
  };
}

export function networkControlPayload(network: NetworkControlValues): Record<string, unknown> {
  return {
    application_protocol: network.application_protocol,
    transport_protocol: network.transport_protocol,
    transport_loss_rate: network.transport_loss_rate,
    transport_congestion_window_segments: network.transport_congestion_window_segments,
    routing_protocol: network.routing_protocol,
    datalink_mac_protocol: network.datalink_mac_protocol,
    routing_latency_weight: network.routing_latency_weight,
    routing_inverse_capacity_weight: network.routing_inverse_capacity_weight,
    routing_hop_weight: network.routing_hop_weight,
    carrier_frequency_hz: network.carrier_frequency_ghz * 1_000_000_000,
    channel_bandwidth_hz: network.channel_bandwidth_mhz * 1_000_000,
    rain_rate_mm_h: network.rain_rate_mm_h,
    rain_attenuation_coefficient_db_per_km_per_mm_h:
      network.rain_attenuation_coefficient_db_per_km_per_mm_h,
    rain_effective_path_km: network.rain_effective_path_km,
    antenna_diameter_m: network.antenna_diameter_m,
    antenna_aperture_efficiency: network.antenna_aperture_efficiency,
    transmit_power_dbw: network.transmit_power_dbw,
    system_loss_db: network.system_loss_db,
    noise_temperature_k: network.noise_temperature_k
  };
}

function generatedConfigMatchesSelection(
  selection: ScenarioScaleSelection,
  generatedConfig: GeneratedScenarioConfig | null | undefined
): generatedConfig is GeneratedScenarioConfig {
  return (
    generatedConfig !== null &&
    generatedConfig !== undefined &&
    generatedConfig.satellite_count === selection.satelliteCount &&
    generatedConfig.user_count === selection.userCount &&
    generatedConfig.compute_node_count === selection.computeNodes
  );
}

function networkQualityPresetMatches(
  preset: NetworkQualityPreset,
  selection: NetworkQualitySelection
): boolean {
  return (
    preset.flowDemandCapacity === selection.flowDemandCapacity &&
    preset.applicationProtocol === selection.applicationProtocol &&
    preset.transportProtocol === selection.transportProtocol &&
    nearlyEqual(preset.transportLossRate, selection.transportLossRate) &&
    preset.transportCongestionWindowSegments ===
      selection.transportCongestionWindowSegments &&
    preset.routingProtocol === selection.routingProtocol &&
    preset.datalinkMacProtocol === selection.datalinkMacProtocol &&
    nearlyEqual(preset.routingLatencyWeight, selection.routingLatencyWeight) &&
    nearlyEqual(
      preset.routingInverseCapacityWeight,
      selection.routingInverseCapacityWeight
    ) &&
    nearlyEqual(preset.routingHopWeight, selection.routingHopWeight)
  );
}

function nearlyEqual(left: number, right: number): boolean {
  return Math.abs(left - right) < 1e-9;
}

function boundedInteger(value: number, min: number, max: number): number {
  if (!Number.isFinite(value)) {
    return min;
  }
  return Math.min(max, Math.max(min, Math.round(value)));
}

function nonNegativeNumber(value: number): number {
  if (!Number.isFinite(value)) {
    return 0;
  }
  return Math.max(0, value);
}

function circularOrbitalPeriodMinutes(altitudeM: number): number {
  const earthRadiusKm = 6371;
  const earthMuKm3S2 = 398600.4418;
  const semiMajorAxisKm = earthRadiusKm + altitudeM / 1000;
  return (2 * Math.PI * Math.sqrt(semiMajorAxisKm ** 3 / earthMuKm3S2)) / 60;
}

function circularOrbitalVelocityKmS(altitudeM: number): number {
  const earthRadiusKm = 6371;
  const earthMuKm3S2 = 398600.4418;
  const semiMajorAxisKm = earthRadiusKm + altitudeM / 1000;
  return Math.sqrt(earthMuKm3S2 / semiMajorAxisKm);
}

function formatInteger(value: number): string {
  return Math.round(value).toLocaleString("zh-CN");
}

function formatDecimal(value: number): string {
  return value.toLocaleString("zh-CN", {
    maximumFractionDigits: 2,
    minimumFractionDigits: 0
  });
}

function formatDuration(seconds: number): string {
  if (seconds < 3600) {
    return `${Math.round(seconds / 60)} 分钟`;
  }
  return `${(seconds / 3600).toFixed(1)} 小时`;
}

function formatDurationCompact(seconds: number): string {
  if (seconds < 60) {
    return `${Math.round(seconds)} 秒`;
  }
  if (seconds < 3600) {
    return `${Math.floor(seconds / 60)}分${Math.round(seconds % 60)}秒`;
  }
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  return `${hours}时${minutes}分`;
}

function formatFrequency(value: number | undefined): string {
  if (value === undefined) {
    return "20 GHz";
  }
  return `${formatDecimal(value / 1_000_000_000)} GHz`;
}

function formatBandwidth(value: number | undefined): string {
  if (value === undefined) {
    return "100 MHz";
  }
  return `${formatDecimal(value / 1_000_000)} MHz`;
}

function formatRainRate(value: number | undefined): string {
  if (value === undefined) {
    return "0 mm/h";
  }
  return `${formatDecimal(value)} mm/h`;
}

function formatApplicationProtocol(value: string | undefined): string {
  if (value === "HTTP") {
    return "HTTP";
  }
  if (value === "MQTT") {
    return "MQTT";
  }
  if (value === "TELEMETRY") {
    return "遥测流";
  }
  return "任务卸载";
}

function formatConstellationProfile(value: string | undefined): string {
  if (value === "STARLINK_SHELL_1_LIKE") {
    return "近似 Starlink Shell 1";
  }
  if (value === "CUSTOM_MULTI_SHELL") {
    return "自定义多壳层";
  }
  return "自定义 Walker";
}

function formatTrafficClass(value: string | undefined): string {
  if (value === "COMPUTE_SERVICE" || value === "TASK_OFFLOAD_FLOW") {
    return "通信-计算服务";
  }
  if (value === "DATA_TRANSFER" || value === "HTTP" || value === "MQTT") {
    return "数据传输";
  }
  if (value === "TELEMETRY") {
    return "遥测";
  }
  if (value === "BULK_DOWNLINK") {
    return "批量下传";
  }
  return value ?? "待初始化";
}

function formatTrafficDestination(value: string | undefined): string {
  if (value === "COMPUTE_NODE") {
    return "星上算力节点";
  }
  if (value === "GROUND_ENDPOINT") {
    return "地面端";
  }
  if (value === "SATELLITE") {
    return "卫星节点";
  }
  if (value === "SERVICE_ENDPOINT") {
    return "服务端点";
  }
  return value ?? "后端默认";
}

function formatTrafficExecutionMode(value: string | undefined): string {
  if (value === "COMPUTE_SERVICE" || value === "TASK_OFFLOAD_FLOW") {
    return "通信 + 计算任务";
  }
  if (
    value === "DATA_TRANSFER" ||
    value === "TELEMETRY" ||
    value === "BULK_DOWNLINK"
  ) {
    return "仅网络流";
  }
  return value ?? "待初始化";
}

function formatDataMegabytes(value: number): string {
  return `${formatDecimal(value)} MB`;
}

function formatPhasePolicy(value: string | undefined): string {
  if (value === "SLOT_INDEX_PHASE_WITH_PLANE_OFFSET") {
    return "槽位相位 + 面偏置";
  }
  if (value === "SEEDED_RAAN_AND_MEAN_ANOMALY_OFFSETS") {
    return "种子偏置相位";
  }
  if (value === "DETERMINISTIC_PLANE_SLOT_PHASE") {
    return "确定性面槽相位";
  }
  return value ?? "待初始化";
}

function formatBeamPattern(value: string | undefined): string {
  if (value === "CENTER_PLUS_HEX_RING_VISUAL_APPROXIMATION") {
    return "中心 + 六邻区蜂窝";
  }
  return value ?? "中心 + 六邻区蜂窝";
}

function formatCoverageFidelityLevel(value: string | undefined): string {
  if (value === "DISPLAY_APPROXIMATION") {
    return "显示近似";
  }
  return value ?? "显示近似";
}

function formatCoverageIntersectionPolicy(value: string | undefined): string {
  if (value === "VISUAL_GEOMETRIC_CONTAINMENT_ONLY") {
    return "仅视觉几何包含";
  }
  return value ?? "仅视觉几何包含";
}

function formatModelAssumption(value: string | undefined): string {
  if (value === undefined || value.length === 0) {
    return "后端确定性简化模型";
  }
  return value.length > 42 ? `${value.slice(0, 42)}...` : value;
}

function formatFidelityModeSummary(summary: FidelitySummary | undefined): string {
  if (summary === undefined) {
    return "后端未返回保真摘要";
  }
  return [
    `轨道 ${summary.orbit_update_mode}`,
    `指标 ${summary.metrics_mode}`,
    `链路 ${summary.space_link_mode}`
  ].join(" / ");
}

function formatRoutingWeights(config: GeneratedScenarioConfig): string {
  return [
    `时延 ${formatDecimal(config.routing_latency_weight ?? 1)}`,
    `容量 ${formatDecimal(config.routing_inverse_capacity_weight ?? 0)}`,
    `跳数 ${formatDecimal(config.routing_hop_weight ?? 0)}`
  ].join(" / ");
}

function formatLossRate(value: number | undefined): string {
  return `${formatDecimal((value ?? 0) * 100)}%`;
}

function formatCongestionWindow(value: number | undefined): string {
  if (value === undefined || value === 0) {
    return "未限制";
  }
  return `${formatInteger(value)} 段`;
}

function formatComputeSchedulingPolicy(value: string | undefined): string {
  if (value === "SHORTEST_JOB_FIRST") {
    return "短作业优先";
  }
  if (value === "EARLIEST_DEADLINE_FIRST") {
    return "最早截止期优先";
  }
  return "先到先服务";
}

function formatMeters(value: number | undefined): string {
  if (value === undefined) {
    return "0.45 m";
  }
  return `${formatDecimal(value)} m`;
}

function formatEfficiency(value: number | undefined): string {
  if (value === undefined) {
    return "0.65";
  }
  return formatDecimal(value);
}

function formatDbw(value: number | undefined): string {
  if (value === undefined) {
    return "20 dBW";
  }
  return `${formatDecimal(value)} dBW`;
}

function formatDb(value: number | undefined): string {
  if (value === undefined) {
    return "1 dB";
  }
  return `${formatDecimal(value)} dB`;
}

function formatKelvin(value: number | undefined): string {
  if (value === undefined) {
    return "290 K";
  }
  return `${formatDecimal(value)} K`;
}

function runtimeStatusLabel(runtime: RuntimeStatusPayload): string {
  if (runtime.last_action === "INITIALIZE_PENDING") {
    return "初始化中";
  }
  if (runtime.last_action === "START_PENDING") {
    return "启动中";
  }
  if (runtime.last_action === "PAUSE_PENDING") {
    return "暂停中";
  }
  if (runtime.last_action === "RESUME_PENDING") {
    return "恢复中";
  }
  if (runtime.last_action === "STOP_PENDING") {
    return "停止中";
  }
  if (runtime.last_action === "RESET_PENDING") {
    return "重置中";
  }
  if (runtime.last_action === "INIT") {
    return "未初始化";
  }
  if (runtime.status === "COMPLETED" || runtime.lifecycle_state === "COMPLETED") {
    return "已完成";
  }
  if (runtime.status === "RUNNING") {
    return "运行中";
  }
  if (runtime.status === "PAUSED") {
    return "已暂停";
  }
  if (runtime.last_action === "INITIALIZE") {
    return "已初始化";
  }
  if (runtime.last_action === "RESET") {
    return "初始状态";
  }
  return "已停止";
}
