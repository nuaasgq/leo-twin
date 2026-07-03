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
  visualization: VisualizationControlValues;
  network: NetworkControlValues;
}

export interface VisualizationControlValues {
  satellites: boolean;
  links: boolean;
  users: boolean;
  metrics: boolean;
}

export interface NetworkControlValues {
  transport_protocol: string;
  routing_protocol: string;
  carrier_frequency_ghz: number;
  channel_bandwidth_mhz: number;
  rain_rate_mm_h: number;
  rain_attenuation_coefficient_db_per_km_per_mm_h: number;
  rain_effective_path_km: number;
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
  const [showSatellites, setShowSatellites] = useState(scenario.visualization.satellites);
  const [showLinks, setShowLinks] = useState(scenario.visualization.links);
  const [showUsers, setShowUsers] = useState(scenario.visualization.users);
  const [showMetrics, setShowMetrics] = useState(scenario.visualization.metrics);
  const [transportProtocol, setTransportProtocol] = useState(
    scenario.network.transport_protocol
  );
  const [routingProtocol, setRoutingProtocol] = useState(scenario.network.routing_protocol);
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
    setShowSatellites(scenario.visualization.satellites);
    setShowLinks(scenario.visualization.links);
    setShowUsers(scenario.visualization.users);
    setShowMetrics(scenario.visualization.metrics);
    setTransportProtocol(scenario.network.transport_protocol);
    setRoutingProtocol(scenario.network.routing_protocol);
    setCarrierFrequencyGhz(scenario.network.carrier_frequency_ghz);
    setChannelBandwidthMhz(scenario.network.channel_bandwidth_mhz);
    setRainRate(scenario.network.rain_rate_mm_h);
    setRainCoefficient(scenario.network.rain_attenuation_coefficient_db_per_km_per_mm_h);
    setRainPathKm(scenario.network.rain_effective_path_km);
  }, [
    scenario.satellite_count,
    scenario.user_count,
    scenario.compute_nodes,
    scenario.visualization.satellites,
    scenario.visualization.links,
    scenario.visualization.users,
    scenario.visualization.metrics,
    scenario.network.transport_protocol,
    scenario.network.routing_protocol,
    scenario.network.carrier_frequency_ghz,
    scenario.network.channel_bandwidth_mhz,
    scenario.network.rain_rate_mm_h,
    scenario.network.rain_attenuation_coefficient_db_per_km_per_mm_h,
    scenario.network.rain_effective_path_km
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
  const progressSummary = runtimeProgressSummary(progress);

  return (
    <section className="config-panel" aria-label="仿真配置与控制面板">
      <div className="config-panel-header">
        <div className="section-title">仿真控制</div>
        <div className={`runtime-badge ${runtime.status.toLowerCase()}`}>
          {runtimeStatusLabel(runtime)}
        </div>
      </div>

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
            onChange={(event) => setDurationSeconds(Number(event.currentTarget.value))}
          />
          <output>{formatDuration(durationSeconds)}</output>
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
      </div>

      <div className="runtime-actions" aria-label="仿真运行控制">
        <button
          type="button"
          onClick={() =>
            onRuntimeControl("INITIALIZE", {
              satellite_count: satelliteCount,
              user_count: userCount,
              compute_nodes: computeNodes,
              mode: runtimeMode,
              speed_factor: speedFactor,
              duration: durationSeconds,
              seed,
              visualization: visualizationControlPayload({
                satellites: showSatellites,
                users: showUsers,
                links: showLinks,
                metrics: showMetrics
              }),
              ...networkControlPayload({
                transport_protocol: transportProtocol,
                routing_protocol: routingProtocol,
                carrier_frequency_ghz: carrierFrequencyGhz,
                channel_bandwidth_mhz: channelBandwidthMhz,
                rain_rate_mm_h: rainRate,
                rain_attenuation_coefficient_db_per_km_per_mm_h: rainCoefficient,
                rain_effective_path_km: rainPathKm
              })
            })
          }
        >
          初始化
        </button>
        <button type="button" onClick={() => onRuntimeControl("START")}>
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
    { label: "轨道面", value: formatInteger(config.orbit_plane_count) },
    { label: "随机种子", value: formatInteger(config.seed) },
    { label: "传输协议", value: config.transport_protocol ?? "TCP" },
    { label: "路由协议", value: config.routing_protocol ?? "LINK_STATE" },
    { label: "载波频率", value: formatFrequency(config.carrier_frequency_hz) },
    { label: "信道带宽", value: formatBandwidth(config.channel_bandwidth_hz) },
    { label: "雨强", value: formatRainRate(config.rain_rate_mm_h) },
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

export function networkControlPayload(network: NetworkControlValues): Record<string, unknown> {
  return {
    transport_protocol: network.transport_protocol,
    routing_protocol: network.routing_protocol,
    carrier_frequency_hz: network.carrier_frequency_ghz * 1_000_000_000,
    channel_bandwidth_hz: network.channel_bandwidth_mhz * 1_000_000,
    rain_rate_mm_h: network.rain_rate_mm_h,
    rain_attenuation_coefficient_db_per_km_per_mm_h:
      network.rain_attenuation_coefficient_db_per_km_per_mm_h,
    rain_effective_path_km: network.rain_effective_path_km
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
