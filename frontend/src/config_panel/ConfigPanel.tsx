import { useEffect, useState } from "react";

import { RuntimeStatusPayload } from "../core/event_types";
import { RuntimeAction } from "./controlClient";

export interface ScenarioControlValues {
  satellite_count: number;
  user_count: number;
}

export interface ConfigPanelProps {
  scenario: ScenarioControlValues;
  runtime: RuntimeStatusPayload;
  onConfigUpdate: (payload: Record<string, unknown>) => void;
  onRuntimeControl: (action: RuntimeAction, payload?: Record<string, unknown>) => void;
}

export function ConfigPanel({
  scenario,
  runtime,
  onConfigUpdate,
  onRuntimeControl
}: ConfigPanelProps) {
  const [satelliteCount, setSatelliteCount] = useState(scenario.satellite_count);
  const [userCount, setUserCount] = useState(scenario.user_count);
  const [speedFactor, setSpeedFactor] = useState(runtime.speed_factor);

  useEffect(() => {
    setSatelliteCount(scenario.satellite_count);
    setUserCount(scenario.user_count);
  }, [scenario.satellite_count, scenario.user_count]);

  useEffect(() => {
    setSpeedFactor(runtime.speed_factor);
  }, [runtime.speed_factor]);

  return (
    <section className="config-panel" aria-label="Configuration control panel">
      <div className="config-panel-header">
        <div className="section-title">Control Plane</div>
        <div className={`runtime-badge ${runtime.status.toLowerCase()}`}>{runtime.status}</div>
      </div>

      <div className="control-group">
        <label className="control-label" htmlFor="satellite-count">
          Satellites
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
            onBlur={() => onConfigUpdate({ satellite_count: satelliteCount })}
            onPointerUp={() => onConfigUpdate({ satellite_count: satelliteCount })}
          />
          <output>{satelliteCount}</output>
        </div>
      </div>

      <div className="control-group">
        <label className="control-label" htmlFor="user-count">
          Users
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
            onBlur={() => onConfigUpdate({ user_count: userCount })}
            onPointerUp={() => onConfigUpdate({ user_count: userCount })}
          />
          <output>{userCount}</output>
        </div>
      </div>

      <div className="control-group">
        <label className="control-label" htmlFor="runtime-mode">
          Mode
        </label>
        <select
          id="runtime-mode"
          value={runtime.mode === "PAUSED" ? "REAL_TIME" : runtime.mode}
          onChange={(event) =>
            onRuntimeControl("SET_MODE", {
              mode: event.currentTarget.value
            })
          }
        >
          <option value="REAL_TIME">REAL_TIME</option>
          <option value="ACCELERATED">ACCELERATED</option>
        </select>
      </div>

      <div className="control-group">
        <label className="control-label" htmlFor="speed-factor">
          Speed
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
            onBlur={() => onRuntimeControl("SET_SPEED", { speed_factor: speedFactor })}
            onPointerUp={() => onRuntimeControl("SET_SPEED", { speed_factor: speedFactor })}
          />
          <output>{speedFactor}x</output>
        </div>
      </div>

      <div className="runtime-actions" aria-label="Runtime actions">
        <button type="button" onClick={() => onRuntimeControl("START")}>
          START
        </button>
        <button type="button" onClick={() => onRuntimeControl("PAUSE")}>
          PAUSE
        </button>
        <button type="button" onClick={() => onRuntimeControl("STOP")}>
          STOP
        </button>
      </div>
    </section>
  );
}
