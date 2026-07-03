import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { CesiumGlobe } from "../3d/cesium/CesiumGlobe";
import { ConfigPanel, ScenarioControlValues } from "../config_panel/ConfigPanel";
import {
  ControlAck,
  ControlChannelClient,
  RuntimeAction
} from "../config_panel/controlClient";
import { RuntimeStatusPayload, ScenarioConfig } from "../core/event_types";
import { Dashboard } from "../dashboard/Dashboard";
import { SnapshotEngine, useWorldSnapshot } from "../state/snapshot_engine";
import { WorldStateReducer } from "../state/reducer";
import { EventRouter } from "../stream/event_router";
import { EventThrottleLayer } from "../stream/throttle_layer";
import { WebSocketStreamClient } from "../stream/websocket_client";
import { loadRuntimeStatus, loadScenarioConfig } from "./api";
import "./App.css";

export function App() {
  const reducer = useMemo(
    () => new WorldStateReducer({ eventLogLimit: 10_000, metricSeriesLimit: 300 }),
    []
  );
  const snapshotEngine = useMemo(
    () =>
      new SnapshotEngine(reducer, {
        snapshotHz: 20
      }),
    [reducer]
  );
  const snapshot = useWorldSnapshot(snapshotEngine);
  const [connectionState, setConnectionState] = useState<"connecting" | "live" | "degraded">(
    "connecting"
  );
  const [scenarioConfig, setScenarioConfig] = useState<ScenarioConfig | null>(null);
  const [runtimeStatus, setRuntimeStatus] = useState<RuntimeStatusPayload>(defaultRuntimeStatus());
  const streamClientRef = useRef<WebSocketStreamClient | null>(null);
  const streamRouterRef = useRef<EventRouter | null>(null);

  useEffect(() => {
    snapshotEngine.start();
    return () => snapshotEngine.stop();
  }, [snapshotEngine]);

  const closeStreams = useCallback(() => {
    streamClientRef.current?.close();
    streamRouterRef.current?.close();
    streamClientRef.current = null;
    streamRouterRef.current = null;
  }, []);

  const resetWorld = useCallback(
    (scenario: ScenarioConfig | null) => {
      reducer.reset();
      if (scenario !== null) {
        snapshotEngine.applyScenarioConfig(scenario);
      }
      snapshotEngine.publishNow();
    },
    [reducer, snapshotEngine]
  );

  const loadControlState = useCallback(async () => {
    const [scenario, runtime] = await Promise.all([
      loadScenarioConfig(),
      loadRuntimeStatus()
    ]);
    setScenarioConfig(scenario);
    setRuntimeStatus((previous) => ({
      ...previous,
      ...scenario.runtime,
      ...runtime
    }));
    snapshotEngine.applyScenarioConfig(scenario);
    snapshotEngine.publishNow();
    return { scenario, runtime };
  }, [snapshotEngine]);

  const startStreams = useCallback(
    (scenario: ScenarioConfig | null) => {
      closeStreams();
      resetWorld(scenario);
      const throttleLayer = new EventThrottleLayer(
        (events) => {
          snapshotEngine.applyEvents(events);
        },
        {
          flushIntervalMs: 20,
          maxEventsPerFlush: 10_000,
          dropRedundantUpdates: true
        }
      );
      const router = new EventRouter(snapshotEngine, { throttleLayer });
      const client = new WebSocketStreamClient(router, {
        batchSize: 500,
        flushIntervalMs: 40
      });
      streamRouterRef.current = router;
      streamClientRef.current = client;
      client.connect();
    },
    [closeStreams, resetWorld, snapshotEngine]
  );

  const controlClient = useMemo(
    () =>
      new ControlChannelClient({
        onMessage: (message) => {
          handleControlMessage(message, setRuntimeStatus);
          if (message.ok === true && message.type === "CONTROL_ACK") {
            const action = message.status?.last_action;
            if (action === "START") {
              loadControlState()
                .then(({ scenario }) => startStreams(scenario))
                .catch(() => setConnectionState("degraded"));
              return;
            }
            if (action === "STOP") {
              closeStreams();
              return;
            }
            if (action === "RESET" || action === "INITIALIZE" || action === "CONFIG_UPDATE") {
              closeStreams();
              loadControlState()
                .then(({ scenario }) => resetWorld(scenario))
                .catch(() => setConnectionState("degraded"));
            }
          }
        }
      }),
    [closeStreams, loadControlState, resetWorld, startStreams]
  );

  useEffect(() => {
    controlClient.connect();
    return () => controlClient.close();
  }, [controlClient]);

  useEffect(() => {
    let closed = false;
    loadControlState()
      .then(({ scenario }) => {
        if (closed) {
          return;
        }
        resetWorld(scenario);
        setConnectionState("live");
      })
      .catch(() => {
        if (!closed) {
          setConnectionState("degraded");
        }
      });

    return () => {
      closed = true;
      closeStreams();
    };
  }, [closeStreams, loadControlState, resetWorld]);

  const scenarioControls = scenarioControlValues(scenarioConfig, snapshot.satellites.length);

  const sendRuntimeControl = useCallback(
    (action: RuntimeAction, payload: Record<string, unknown> = {}) => {
      controlClient.sendRuntimeControl(action, payload);
    },
    [controlClient]
  );

  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="brand-block">
          <div className="brand-title">LEO-Twin</div>
          <div className="brand-subtitle">低轨卫星互联网通信-算力数字孪生平台</div>
        </div>
        <div className="surface-tabs" aria-label="前端界面">
          <span className="surface-tab active">三维仿真控制台</span>
          <span className="surface-tab">数据态势面板</span>
        </div>
        <div className={`connection-pill ${connectionState}`}>
          {connectionStateLabel(connectionState)}
        </div>
      </header>
      <section className="workspace">
        <section className="simulation-surface" aria-label="三维仿真控制台">
          <div className="surface-header">
            <div>
              <div className="surface-kicker">三维展示与运行控制</div>
              <h1>星座运行视图</h1>
            </div>
            <div className="surface-status">
              <span>{runtimeStatusLabel(runtimeStatus.status)}</span>
              <strong>{runtimeStatus.speed_factor}x</strong>
            </div>
          </div>
          <div className="globe-panel">
            <CesiumGlobe snapshot={snapshot} />
          </div>
          <div className="control-dock">
            <ConfigPanel
              scenario={scenarioControls}
              runtime={runtimeStatus}
              onRuntimeControl={sendRuntimeControl}
            />
          </div>
        </section>
        <aside className="dashboard-surface" aria-label="数据态势面板">
          <div className="dashboard-header">
            <div className="surface-kicker">实时观测数据</div>
            <h2>数据态势面板</h2>
          </div>
          <Dashboard snapshot={snapshot} />
        </aside>
      </section>
    </main>
  );
}

function connectionStateLabel(state: "connecting" | "live" | "degraded"): string {
  if (state === "connecting") {
    return "连接中";
  }
  if (state === "live") {
    return "已连接";
  }
  return "连接异常";
}

function runtimeStatusLabel(status: RuntimeStatusPayload["status"]): string {
  if (status === "RUNNING") {
    return "运行中";
  }
  if (status === "PAUSED") {
    return "已暂停";
  }
  return "已停止";
}

function defaultRuntimeStatus(): RuntimeStatusPayload {
  return {
    status: "STOPPED",
    mode: "REAL_TIME",
    speed_factor: 1,
    seed: 20260703,
    duration: 600,
    config_version: 0,
    last_action: "INIT"
  };
}

function handleControlMessage(
  message: ControlAck,
  setRuntimeStatus: (updater: (previous: RuntimeStatusPayload) => RuntimeStatusPayload) => void
): void {
  if (message.status === undefined) {
    return;
  }
  setRuntimeStatus((previous) => ({
    ...previous,
    ...message.status
  }));
}

function scenarioControlValues(
  scenarioConfig: ScenarioConfig | null,
  renderedSatellites: number
): ScenarioControlValues {
  return {
    satellite_count:
      scenarioConfig?.scenario?.satellite_count ??
      scenarioConfig?.render?.max_satellites ??
      renderedSatellites,
    user_count:
      scenarioConfig?.scenario?.user_count ?? scenarioConfig?.ground_users?.length ?? 1000
  };
}
