import { useEffect, useState } from "react";

import { RuntimeMode, RuntimeStatusPayload } from "../core/event_types";
import { RuntimeAction } from "./controlClient";

export interface ScenarioControlValues {
  satellite_count: number;
  user_count: number;
}

export interface ConfigPanelProps {
  scenario: ScenarioControlValues;
  runtime: RuntimeStatusPayload;
  onRuntimeControl: (action: RuntimeAction, payload?: Record<string, unknown>) => void;
}

export function ConfigPanel({
  scenario,
  runtime,
  onRuntimeControl
}: ConfigPanelProps) {
  const [satelliteCount, setSatelliteCount] = useState(scenario.satellite_count);
  const [userCount, setUserCount] = useState(scenario.user_count);
  const [runtimeMode, setRuntimeMode] = useState<Exclude<RuntimeMode, "PAUSED">>(
    runtime.mode === "ACCELERATED" ? "ACCELERATED" : "REAL_TIME"
  );
  const [speedFactor, setSpeedFactor] = useState(runtime.speed_factor);

  useEffect(() => {
    setSatelliteCount(scenario.satellite_count);
    setUserCount(scenario.user_count);
  }, [scenario.satellite_count, scenario.user_count]);

  useEffect(() => {
    if (runtime.mode !== "PAUSED") {
      setRuntimeMode(runtime.mode);
    }
    setSpeedFactor(runtime.speed_factor);
  }, [runtime.mode, runtime.speed_factor]);

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

      <div className="runtime-actions" aria-label="仿真运行控制">
        <button
          type="button"
          onClick={() =>
            onRuntimeControl("INITIALIZE", {
              satellite_count: satelliteCount,
              user_count: userCount,
              mode: runtimeMode,
              speed_factor: speedFactor
            })
          }
        >
          初始化
        </button>
        <button type="button" onClick={() => onRuntimeControl("START")}>
          开始
        </button>
        <button type="button" onClick={() => onRuntimeControl("STOP")}>
          停止
        </button>
        <button type="button" onClick={() => onRuntimeControl("RESET")}>
          重置
        </button>
      </div>
    </section>
  );
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
