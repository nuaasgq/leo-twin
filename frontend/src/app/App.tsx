import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { CesiumGlobe } from "../3d/cesium/CesiumGlobe";
import { ConfigPanel, ScenarioControlValues } from "../config_panel/ConfigPanel";
import {
  ControlAck,
  ControlChannelClient,
  RuntimeAction
} from "../config_panel/controlClient";
import {
  GeneratedScenarioConfig,
  RuntimeStatusPayload,
  ScenarioConfig
} from "../core/event_types";
import { Dashboard } from "../dashboard/Dashboard";
import { SnapshotEngine, useWorldSnapshot } from "../state/snapshot_engine";
import { WorldStateReducer } from "../state/reducer";
import { EventRouter } from "../stream/event_router";
import { EventPlaybackLayer } from "../stream/playback_layer";
import { EventThrottleLayer } from "../stream/throttle_layer";
import { WebSocketStreamClient } from "../stream/websocket_client";
import { loadRuntimeState, loadScenarioConfig } from "./api";
import "./App.css";

export function App() {
  const surface = surfaceFromPathname(window.location.pathname);
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
  const [generatedConfig, setGeneratedConfig] = useState<GeneratedScenarioConfig | null>(null);
  const [runtimeStatus, setRuntimeStatus] = useState<RuntimeStatusPayload>(defaultRuntimeStatus());
  const runtimeStatusRef = useRef(runtimeStatus);
  const streamClientRef = useRef<WebSocketStreamClient | null>(null);
  const streamRouterRef = useRef<EventRouter | null>(null);

  useEffect(() => {
    runtimeStatusRef.current = runtimeStatus;
  }, [runtimeStatus]);

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
      loadRuntimeState()
    ]);
    setScenarioConfig(scenario);
    setGeneratedConfig(runtime.generated_config ?? null);
    setRuntimeStatus((previous) => ({
      ...previous,
      ...scenario.runtime,
      ...runtime.status
    }));
    snapshotEngine.applyScenarioConfig(scenario);
    snapshotEngine.publishNow();
    return { scenario, runtime };
  }, [snapshotEngine]);

  const startStreams = useCallback(
    (scenario: ScenarioConfig | null, speedFactorOverride?: number) => {
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
      const playbackLayer = new EventPlaybackLayer(
        (events) => {
          router.routeEvents(events);
        },
        {
          speedFactor: speedFactorOverride ?? runtimeStatusRef.current.speed_factor
        }
      );
      const client = new WebSocketStreamClient(router, {
        batchSize: 500,
        flushIntervalMs: 40,
        playbackLayer,
        stateStreamEnabled: false
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
          handleGeneratedConfig(message, setGeneratedConfig);
          if (
            message.type === "RUNTIME_STATUS" &&
            runtimeStatusRequiresStreams(message.status) &&
            streamClientRef.current === null
          ) {
            loadControlState()
              .then(({ scenario, runtime }) =>
                startStreams(scenario, message.status?.speed_factor ?? runtime.status.speed_factor)
              )
              .catch(() => setConnectionState("degraded"));
            return;
          }
          if (message.ok === true && message.type === "CONTROL_ACK") {
            const action = message.status?.last_action;
            if (action === "START" || action === "RESUME") {
              loadControlState()
                .then(({ scenario, runtime }) =>
                  startStreams(
                    scenario,
                    message.status?.speed_factor ?? runtime.status.speed_factor
                  )
                )
                .catch(() => setConnectionState("degraded"));
              return;
            }
            if (action === "STOP" || action === "PAUSE") {
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
      .then(({ scenario, runtime }) => {
        if (closed) {
          return;
        }
        if (runtimeStatusRequiresStreams(runtime.status)) {
          startStreams(scenario, runtime.status.speed_factor);
        } else {
          resetWorld(scenario);
        }
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
  }, [closeStreams, loadControlState, resetWorld, startStreams]);

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
          <a className={`surface-tab ${surface === "control" ? "active" : ""}`} href="/">
            三维仿真控制台
          </a>
          <a
            className={`surface-tab ${surface === "dashboard" ? "active" : ""}`}
            href="/dashboard"
          >
            数据态势面板
          </a>
        </div>
        <div className={`connection-pill ${connectionState}`}>
          {connectionStateLabel(connectionState)}
        </div>
      </header>
      {surface === "dashboard" ? (
        <section className="dashboard-page" aria-label="独立数据态势面板">
          <div className="dashboard-page-header">
            <div>
              <div className="surface-kicker">实时观测数据</div>
              <h1>数据态势面板</h1>
            </div>
            <div className="surface-status">
              <span>{runtimeStatusLabel(runtimeStatus.status)}</span>
              <strong>{runtimeStatus.speed_factor}x</strong>
            </div>
          </div>
          <Dashboard snapshot={snapshot} />
        </section>
      ) : (
        <section className="workspace control-workspace">
          <section className="simulation-surface control-only" aria-label="三维仿真控制台">
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
                progress={{
                  sim_time: snapshot.last_sim_time,
                  duration: runtimeStatus.duration,
                  event_count: snapshot.event_count
                }}
                generatedConfig={generatedConfig}
                onRuntimeControl={sendRuntimeControl}
              />
            </div>
          </section>
        </section>
      )}
    </main>
  );
}

export type FrontendSurface = "control" | "dashboard";

export function surfaceFromPathname(pathname: string): FrontendSurface {
  return pathname === "/dashboard" || pathname.startsWith("/dashboard/")
    ? "dashboard"
    : "control";
}

export function runtimeStatusRequiresStreams(
  status: RuntimeStatusPayload | undefined
): boolean {
  return status?.status === "RUNNING";
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

function handleGeneratedConfig(
  message: ControlAck,
  setGeneratedConfig: (config: GeneratedScenarioConfig | null) => void
): void {
  if (message.generated_config !== undefined) {
    setGeneratedConfig(message.generated_config);
  }
}

function scenarioControlValues(
  scenarioConfig: ScenarioConfig | null,
  renderedSatellites: number
): ScenarioControlValues {
  const visualization = scenarioConfig?.ui?.visualization;
  return {
    satellite_count:
      scenarioConfig?.scenario?.satellite_count ??
      scenarioConfig?.render?.max_satellites ??
      renderedSatellites,
    user_count:
      scenarioConfig?.scenario?.user_count ?? scenarioConfig?.ground_users?.length ?? 1000,
    compute_nodes: scenarioConfig?.scenario?.compute_nodes ?? 10,
    visualization: {
      satellites: visualization?.satellites ?? true,
      links: visualization?.links ?? true,
      users: visualization?.users ?? true,
      metrics: visualization?.metrics ?? true
    }
  };
}
