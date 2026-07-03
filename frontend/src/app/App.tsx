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
import { DataPanel } from "../dashboard/data_panel/DataPanel";
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
    const effectiveScenario = scenarioWithRuntimeConfig(scenario, runtime.config);
    setScenarioConfig(effectiveScenario);
    setGeneratedConfig(runtime.generated_config ?? null);
    setRuntimeStatus((previous) => ({
      ...previous,
      ...effectiveScenario.runtime,
      ...runtime.status
    }));
    snapshotEngine.applyScenarioConfig(effectiveScenario);
    snapshotEngine.publishNow();
    return { scenario: effectiveScenario, runtime };
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
          <a
            className="surface-tab surface-tab-external"
            href={standaloneDashboardHref(window.location.origin)}
            target="_blank"
            rel="noreferrer"
          >
            弹出数据屏
          </a>
        </div>
        <div className={`connection-pill ${connectionState}`}>
          {connectionStateLabel(connectionState)}
        </div>
      </header>
      {surface === "dashboard" ? (
        <section className="dashboard-page" aria-label="独立数据态势面板">
          <DataPanel
            snapshot={snapshot}
            runtimeStatus={runtimeStatus}
            generatedConfig={generatedConfig}
          />
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

export function standaloneDashboardHref(origin: string): string {
  const normalizedOrigin = origin.endsWith("/") ? origin.slice(0, -1) : origin;
  return `${normalizedOrigin}/dashboard`;
}

export function runtimeStatusRequiresStreams(
  status: RuntimeStatusPayload | undefined
): boolean {
  return status?.status === "RUNNING";
}

export function scenarioWithRuntimeConfig(
  scenario: ScenarioConfig,
  runtimeConfig: unknown
): ScenarioConfig {
  if (!isRecord(runtimeConfig)) {
    return scenario;
  }
  const scenarioSection = isRecord(runtimeConfig.scenario)
    ? {
        ...scenario.scenario,
        compute_scheduling_policy:
          typeof runtimeConfig.scenario.compute_scheduling_policy === "string"
            ? runtimeConfig.scenario.compute_scheduling_policy
            : scenario.scenario?.compute_scheduling_policy
      }
    : scenario.scenario;
  const network = isRecord(runtimeConfig.network)
    ? {
        ...scenario.network,
        transport_protocol:
          typeof runtimeConfig.network.transport_protocol === "string"
            ? runtimeConfig.network.transport_protocol
            : scenario.network?.transport_protocol,
        routing_protocol:
          typeof runtimeConfig.network.routing_protocol === "string"
            ? runtimeConfig.network.routing_protocol
            : scenario.network?.routing_protocol,
        carrier_frequency_hz:
          typeof runtimeConfig.network.carrier_frequency_hz === "number"
            ? runtimeConfig.network.carrier_frequency_hz
            : scenario.network?.carrier_frequency_hz,
        channel_bandwidth_hz:
          typeof runtimeConfig.network.channel_bandwidth_hz === "number"
            ? runtimeConfig.network.channel_bandwidth_hz
            : scenario.network?.channel_bandwidth_hz,
        rain_rate_mm_h:
          typeof runtimeConfig.network.rain_rate_mm_h === "number"
            ? runtimeConfig.network.rain_rate_mm_h
            : scenario.network?.rain_rate_mm_h,
        rain_attenuation_coefficient_db_per_km_per_mm_h:
          typeof runtimeConfig.network.rain_attenuation_coefficient_db_per_km_per_mm_h ===
          "number"
            ? runtimeConfig.network.rain_attenuation_coefficient_db_per_km_per_mm_h
            : scenario.network?.rain_attenuation_coefficient_db_per_km_per_mm_h,
        rain_effective_path_km:
          typeof runtimeConfig.network.rain_effective_path_km === "number"
            ? runtimeConfig.network.rain_effective_path_km
            : scenario.network?.rain_effective_path_km,
        antenna_diameter_m:
          typeof runtimeConfig.network.antenna_diameter_m === "number"
            ? runtimeConfig.network.antenna_diameter_m
            : scenario.network?.antenna_diameter_m,
        antenna_aperture_efficiency:
          typeof runtimeConfig.network.antenna_aperture_efficiency === "number"
            ? runtimeConfig.network.antenna_aperture_efficiency
            : scenario.network?.antenna_aperture_efficiency
      }
    : scenario.network;
  const ui = isRecord(runtimeConfig.ui)
    ? {
        ...scenario.ui,
        visualization: isRecord(runtimeConfig.ui.visualization)
          ? {
              ...scenario.ui?.visualization,
              satellites:
                typeof runtimeConfig.ui.visualization.satellites === "boolean"
                  ? runtimeConfig.ui.visualization.satellites
                  : scenario.ui?.visualization?.satellites,
              links:
                typeof runtimeConfig.ui.visualization.links === "boolean"
                  ? runtimeConfig.ui.visualization.links
                  : scenario.ui?.visualization?.links,
              users:
                typeof runtimeConfig.ui.visualization.users === "boolean"
                  ? runtimeConfig.ui.visualization.users
                  : scenario.ui?.visualization?.users,
              metrics:
                typeof runtimeConfig.ui.visualization.metrics === "boolean"
                  ? runtimeConfig.ui.visualization.metrics
                  : scenario.ui?.visualization?.metrics
            }
          : scenario.ui?.visualization
      }
    : scenario.ui;
  return {
    ...scenario,
    scenario: scenarioSection,
    network,
    ui
  };
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
    compute_scheduling_policy:
      scenarioConfig?.scenario?.compute_scheduling_policy ?? "FIFO",
    visualization: {
      satellites: visualization?.satellites ?? true,
      links: visualization?.links ?? true,
      users: visualization?.users ?? true,
      metrics: visualization?.metrics ?? true
    },
    network: {
      transport_protocol: scenarioConfig?.network?.transport_protocol ?? "TCP",
      routing_protocol: scenarioConfig?.network?.routing_protocol ?? "LINK_STATE",
      datalink_mac_protocol: scenarioConfig?.network?.datalink_mac_protocol ?? "TDMA",
      carrier_frequency_ghz:
        (scenarioConfig?.network?.carrier_frequency_hz ?? 20_000_000_000) / 1_000_000_000,
      channel_bandwidth_mhz:
        (scenarioConfig?.network?.channel_bandwidth_hz ?? 100_000_000) / 1_000_000,
      rain_rate_mm_h: scenarioConfig?.network?.rain_rate_mm_h ?? 0,
      rain_attenuation_coefficient_db_per_km_per_mm_h:
        scenarioConfig?.network?.rain_attenuation_coefficient_db_per_km_per_mm_h ?? 0,
      rain_effective_path_km: scenarioConfig?.network?.rain_effective_path_km ?? 0,
      antenna_diameter_m: scenarioConfig?.network?.antenna_diameter_m ?? 0.45,
      antenna_aperture_efficiency:
        scenarioConfig?.network?.antenna_aperture_efficiency ?? 0.65
    }
  };
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
