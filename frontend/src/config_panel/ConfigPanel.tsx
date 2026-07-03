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
  }, [scenario.satellite_count, scenario.user_count, scenario.compute_nodes]);

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
              seed
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
