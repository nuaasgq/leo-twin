import { useEffect, useState } from "react";

import {
  GeneratedScenarioConfig,
  RuntimeMode,
  RuntimeStatusPayload
} from "../core/event_types";
import { RuntimeAction } from "./controlClient";

export interface ScenarioControlValues {
  satellite_count: number;
  user_count: number;
  compute_nodes: number;
  compute_capacity: number;
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
}

export interface VisualizationControlValues {
  satellites: boolean;
  links: boolean;
  users: boolean;
  metrics: boolean;
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

export interface ConfigPanelProps {
  scenario: ScenarioControlValues;
  runtime: RuntimeStatusPayload;
  progress: RuntimeProgressValues;
  generatedConfig: GeneratedScenarioConfig | null;
  onRuntimeControl: (action: RuntimeAction, payload?: Record<string, unknown>) => void;
}

export interface ConfigSummaryItem {
  label: string;
  value: string;
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
  runtime: "运行模式与可视化",
  network: "网络协议栈与路由",
  physical: "物理层与信道参数",
  activeScenario: "当前生效场景"
} as const;

export function configPanelSectionTitles(): readonly string[] {
  return Object.values(CONFIG_PANEL_SECTION_LABELS);
}

export function ConfigPanel({
  scenario,
  runtime,
  progress,
  generatedConfig,
  onRuntimeControl
}: ConfigPanelProps) {
  const [satelliteCount, setSatelliteCount] = useState(scenario.satellite_count);
  const [userCount, setUserCount] = useState(scenario.user_count);
  const [computeNodes, setComputeNodes] = useState(scenario.compute_nodes);
  const [computeCapacity, setComputeCapacity] = useState(scenario.compute_capacity);
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
  const [speedFactor, setSpeedFactor] = useState(runtime.speed_factor);
  const [durationSeconds, setDurationSeconds] = useState(runtime.duration);
  const [seed, setSeed] = useState(runtime.seed);

  useEffect(() => {
    setSatelliteCount(scenario.satellite_count);
    setUserCount(scenario.user_count);
    setComputeNodes(scenario.compute_nodes);
    setComputeCapacity(scenario.compute_capacity);
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
    if (runtime.mode !== "PAUSED") {
      setRuntimeMode(runtime.mode);
    }
    setSpeedFactor(runtime.speed_factor);
    setDurationSeconds(runtime.duration);
    setSeed(runtime.seed);
  }, [runtime.mode, runtime.speed_factor, runtime.duration, runtime.seed]);

  const summaryItems = generatedScenarioSummaryItems(generatedConfig);
  const pauseResume = pauseResumeControl(runtime);
  const startDisabled = startControlDisabled(runtime);
  const progressSummary = runtimeProgressSummary(progress);
  const handleInitialize = () =>
    onRuntimeControl("INITIALIZE", {
      satellite_count: satelliteCount,
      user_count: userCount,
      compute_nodes: computeNodes,
      compute_capacity: computeCapacity,
      compute_scheduling_policy: computeSchedulingPolicy,
      mode: runtimeMode,
      speed_factor: speedFactor,
      duration: durationSeconds,
      seed,
      orbit: orbitControlPayload({
        update_interval_seconds: orbitUpdateIntervalSeconds,
        plane_count: orbitPlaneCount,
        altitude_km: orbitAltitudeKm,
        inclination_deg: orbitInclinationDeg
      }),
      traffic_model: trafficControlPayload({
        flow_interval_seconds: flowIntervalSeconds,
        task_interval_seconds: taskIntervalSeconds,
        flow_demand_capacity: flowDemandCapacity,
        task_compute_demand: taskComputeDemand,
        task_data_size: taskDataSize
      }),
      visualization: visualizationControlPayload({
        satellites: showSatellites,
        users: showUsers,
        links: showLinks,
        metrics: showMetrics
      }),
      ...networkControlPayload({
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
      })
    });

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
            <button type="button" onClick={handleInitialize}>
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
            <button type="button" onClick={() => onRuntimeControl("STOP")}>
              停止
            </button>
            <button type="button" onClick={() => onRuntimeControl("RESET")}>
              重置
            </button>
          </div>

          <div className="execution-parameter-grid">
            <div className="control-group emphasized-control">
              <label className="control-label" htmlFor="duration-seconds">
                仿真时长
              </label>
              <div className="control-row">
                <input
                  id="duration-seconds"
                  type="range"
                  min="60"
                  max="86400"
                  step="60"
                  value={durationSeconds}
                  onChange={(event) =>
                    setDurationSeconds(Number(event.currentTarget.value))
                  }
                />
                <output>{formatDuration(durationSeconds)}</output>
              </div>
            </div>
          </div>

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

      <div className="control-group">
        <label className="control-label" htmlFor="satellite-count">
          卫星数量
        </label>
        <div className="control-row">
          <input
            id="satellite-count"
            type="range"
            min="12"
            max="10000"
            step="12"
            value={satelliteCount}
            onChange={(event) => setSatelliteCount(Number(event.currentTarget.value))}
          />
          <output>{satelliteCount}</output>
        </div>
      </div>

      <div className="control-group">
        <label className="control-label" htmlFor="user-count">
          用户数量
        </label>
        <div className="control-row">
          <input
            id="user-count"
            type="range"
            min="10"
            max="100000"
            step="10"
            value={userCount}
            onChange={(event) => setUserCount(Number(event.currentTarget.value))}
          />
          <output>{userCount}</output>
        </div>
      </div>

      <div className="control-group">
        <label className="control-label" htmlFor="compute-node-count">
          算力节点
        </label>
        <div className="control-row">
          <input
            id="compute-node-count"
            type="range"
            min="1"
            max="1000"
            step="1"
            value={computeNodes}
            onChange={(event) => setComputeNodes(Number(event.currentTarget.value))}
          />
          <output>{computeNodes}</output>
        </div>
      </div>

      <div className="control-group">
        <label className="control-label" htmlFor="compute-capacity">
          基准算力
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
        </section>

        <section className="config-section" aria-label={CONFIG_PANEL_SECTION_LABELS.traffic}>
          <div className="config-section-title">{CONFIG_PANEL_SECTION_LABELS.traffic}</div>
      <div className="channel-grid" aria-label="流量与任务需求">
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
            任务数据量
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
      </div>
        </section>

        <section className="config-section" aria-label={CONFIG_PANEL_SECTION_LABELS.runtime}>
          <div className="config-section-title">{CONFIG_PANEL_SECTION_LABELS.runtime}</div>
      <div className="control-group">
        <label className="control-label" htmlFor="runtime-mode">
          运行模式
        </label>
        <select
          id="runtime-mode"
          value={runtimeMode}
          onChange={(event) => setRuntimeMode(event.currentTarget.value as Exclude<RuntimeMode, "PAUSED">)}
        >
          <option value="REAL_TIME">实时运行</option>
          <option value="ACCELERATED">加速运行</option>
        </select>
      </div>

      <div className="control-group">
        <label className="control-label" htmlFor="speed-factor">
          仿真倍率
        </label>
        <div className="control-row">
          <input
            id="speed-factor"
            type="range"
            min="1"
            max="100"
            step="1"
            value={speedFactor}
            onChange={(event) => setSpeedFactor(Number(event.currentTarget.value))}
          />
          <output>{speedFactor}x</output>
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
          onChange={(event) => setSeed(Number(event.currentTarget.value))}
        />
      </div>

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
            <span>指标</span>
          </label>
        </div>
      </div>
        </section>

        <section className="config-section" aria-label={CONFIG_PANEL_SECTION_LABELS.network}>
          <div className="config-section-title">{CONFIG_PANEL_SECTION_LABELS.network}</div>
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
  return [
    { label: "生效卫星", value: formatInteger(config.satellite_count) },
    { label: "生效用户", value: formatInteger(config.user_count) },
    { label: "计算节点", value: formatInteger(config.compute_node_count) },
    { label: "业务流量", value: formatInteger(config.flow_count) },
    { label: "调度策略", value: formatComputeSchedulingPolicy(config.compute_scheduling_policy) },
    { label: "轨道面", value: formatInteger(config.orbit_plane_count) },
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
      value: `${formatInteger(config.semi_major_axis_km - config.earth_radius_km)} km`
    },
    { label: "倾角", value: `${formatDecimal(config.inclination_deg)}°` }
  ];
}

export interface PauseResumeControl {
  label: string;
  action: RuntimeAction;
  disabled: boolean;
}

export function pauseResumeControl(runtime: RuntimeStatusPayload): PauseResumeControl {
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
  return runtime.initialized !== true || runtime.status !== "STOPPED";
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
    task_data_size: traffic.task_data_size
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
  if (runtime.last_action === "INIT") {
    return "未初始化";
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
