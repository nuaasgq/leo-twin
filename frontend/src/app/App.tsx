import { Suspense, lazy, useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { MouseEvent } from "react";

import type { ScenarioControlValues } from "../config_panel/ConfigPanel";
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
import { SnapshotEngine, useWorldSnapshot } from "../state/snapshot_engine";
import { WorldStateReducer } from "../state/reducer";
import { EventRouter } from "../stream/event_router";
import { EventThrottleLayer } from "../stream/throttle_layer";
import { WebSocketStreamClient } from "../stream/websocket_client";
import { loadRuntimeState, loadScenarioConfig } from "./api";
import "./App.css";

const RUNTIME_STATUS_POLL_MS = 250;
const RUNTIME_PROGRESS_TICK_MS = 100;

const CesiumGlobe = lazy(async () => {
  const module = await import("../3d/cesium/CesiumGlobe");
  return { default: module.CesiumGlobe };
});

const ConfigPanel = lazy(async () => {
  const module = await import("../config_panel/ConfigPanel");
  return { default: module.ConfigPanel };
});

const DataPanel = lazy(async () => {
  const module = await import("../dashboard/data_panel/DataPanel");
  return { default: module.DataPanel };
});

export function App() {
  const [surface, setSurface] = useState<FrontendSurface>(() =>
    surfaceFromPathname(window.location.pathname)
  );
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
  const [runtimeProgressAnchor, setRuntimeProgressAnchor] = useState<RuntimeProgressAnchor>(() =>
    defaultRuntimeProgressAnchor(defaultRuntimeStatus())
  );
  const [runtimeProgressNowMs, setRuntimeProgressNowMs] = useState(() => Date.now());
  const streamClientRef = useRef<WebSocketStreamClient | null>(null);
  const streamRouterRef = useRef<EventRouter | null>(null);

  useEffect(() => {
    snapshotEngine.start();
    return () => snapshotEngine.stop();
  }, [snapshotEngine]);

  useEffect(() => {
    const syncSurfaceFromLocation = () => {
      setSurface(surfaceFromPathname(window.location.pathname));
    };
    window.addEventListener("popstate", syncSurfaceFromLocation);
    return () => window.removeEventListener("popstate", syncSurfaceFromLocation);
  }, []);

  const navigateWithinApp = useCallback(
    (event: MouseEvent<HTMLAnchorElement>, pathname: string) => {
      if (
        event.defaultPrevented ||
        event.button !== 0 ||
        event.altKey ||
        event.ctrlKey ||
        event.metaKey ||
        event.shiftKey
      ) {
        return;
      }
      event.preventDefault();
      if (window.location.pathname !== pathname) {
        window.history.pushState(null, "", pathname);
      }
      setSurface(surfaceFromPathname(pathname));
    },
    []
  );

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
    (
      scenario: ScenarioConfig | null,
      options: { resetBeforeConnect?: boolean } = {}
    ) => {
      closeStreams();
      if (options.resetBeforeConnect ?? true) {
        resetWorld(scenario);
      }
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
        flushIntervalMs: 40,
        stateStreamEnabled: true
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
              .then(({ scenario }) =>
                startStreams(scenario, {
                  resetBeforeConnect: snapshotEngine.getSnapshot().event_count === 0
                })
              )
              .catch(() => setConnectionState("degraded"));
            return;
          }
          if (message.ok === true && message.type === "CONTROL_ACK") {
            const action = message.status?.last_action;
            if (action === "START") {
              loadControlState()
                .then(({ scenario }) => startStreams(scenario, { resetBeforeConnect: true }))
                .catch(() => setConnectionState("degraded"));
              return;
            }
            if (action === "RESUME") {
              loadControlState()
                .then(({ scenario }) => startStreams(scenario, { resetBeforeConnect: false }))
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
    [closeStreams, loadControlState, resetWorld, snapshotEngine, startStreams]
  );

  useEffect(() => {
    controlClient.connect();
    return () => controlClient.close();
  }, [controlClient]);

  useEffect(() => {
    setRuntimeProgressAnchor((previous) =>
      nextRuntimeProgressAnchor(previous, snapshot.last_sim_time, runtimeStatus, Date.now())
    );
  }, [runtimeStatus, snapshot.last_sim_time]);

  useEffect(() => {
    if (!runtimeStatusIsProgressing(runtimeStatus)) {
      setRuntimeProgressNowMs(Date.now());
      return;
    }
    const timer = window.setInterval(() => {
      setRuntimeProgressNowMs(Date.now());
    }, RUNTIME_PROGRESS_TICK_MS);
    return () => window.clearInterval(timer);
  }, [runtimeStatus]);

  useEffect(() => {
    if (!runtimeStatusRequiresStreams(runtimeStatus)) {
      return;
    }
    let closed = false;
    const refreshStatus = async () => {
      try {
        const runtime = await loadRuntimeState();
        if (closed) {
          return;
        }
        setRuntimeStatus((previous) => ({
          ...previous,
          ...runtime.status
        }));
        if (runtime.generated_config !== undefined) {
          setGeneratedConfig(runtime.generated_config);
        }
      } catch {
        if (!closed) {
          setConnectionState("degraded");
        }
      }
    };
    const timer = window.setInterval(refreshStatus, RUNTIME_STATUS_POLL_MS);
    void refreshStatus();
    return () => {
      closed = true;
      window.clearInterval(timer);
    };
  }, [runtimeStatus.status, runtimeStatus.lifecycle_state]);

  useEffect(() => {
    let closed = false;
    loadControlState()
      .then(({ scenario, runtime }) => {
        if (closed) {
          return;
        }
        if (runtimeStatusRequiresStreams(runtime.status)) {
          startStreams(scenario, {
            resetBeforeConnect: snapshotEngine.getSnapshot().event_count === 0
          });
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
  }, [closeStreams, loadControlState, resetWorld, snapshotEngine, startStreams]);

  const scenarioControls = scenarioControlValues(scenarioConfig, snapshot.satellites.length);
  const displaySimTime = Math.max(
    snapshot.last_sim_time,
    runtimeProgressSimTime(runtimeProgressAnchor, runtimeProgressNowMs)
  );
  const displayEventCount = runtimeStatus.processed_event_count ?? snapshot.event_count;
  const runtimeRibbon = buildRuntimeRibbonSummary({
    simTime: displaySimTime,
    eventCount: displayEventCount,
    runtimeStatus,
    scenario: scenarioControls
  });

  const sendRuntimeControl = useCallback(
    (action: RuntimeAction, payload: Record<string, unknown> = {}) => {
      setRuntimeStatus((previous) => ({
        ...previous,
        last_action: `${action}_PENDING`
      }));
      controlClient.sendRuntimeControl(action, payload);
    },
    [controlClient]
  );

  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="brand-block">
          <div className="brand-mark" aria-hidden="true">
            LT
          </div>
          <div className="brand-copy">
            <div className="brand-title">LEO-Twin</div>
            <div className="brand-subtitle">低轨卫星互联网通信-算力数字孪生平台</div>
          </div>
        </div>
        <div className="surface-tabs" aria-label="前端界面">
          <a
            className={`surface-tab ${surface === "control" ? "active" : ""}`}
            href="/"
            onClick={(event) => navigateWithinApp(event, "/")}
          >
            三维仿真控制台
          </a>
          <a
            className={`surface-tab ${surface === "dashboard" ? "active" : ""}`}
            href="/dashboard"
            onClick={(event) => navigateWithinApp(event, "/dashboard")}
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
          <Suspense
            fallback={
              <div className="surface-loading" role="status">
                数据面板加载中
              </div>
            }
          >
            <DataPanel
              snapshot={snapshot}
              runtimeStatus={runtimeStatus}
              generatedConfig={generatedConfig}
              displaySimTime={displaySimTime}
              displayEventCount={displayEventCount}
              onNavigateControl={(event) => navigateWithinApp(event, "/")}
            />
          </Suspense>
        </section>
      ) : (
        <section className="workspace control-workspace">
          <section className="simulation-surface control-only" aria-label="三维仿真控制台">
            <div className="surface-header">
              <div>
                <div className="surface-kicker">三维展示与运行控制</div>
                <h1>星座运行视图</h1>
              </div>
              <div className="surface-status-stack">
                <div className={`surface-status ${runtimeStatus.status.toLowerCase()}`}>
                  <span>{runtimeStatusLabel(runtimeStatus.status)}</span>
                  <strong>{runtimeStatus.speed_factor}x</strong>
                </div>
                <a
                  className="surface-action-link"
                  href="/dashboard"
                  onClick={(event) => navigateWithinApp(event, "/dashboard")}
                >
                  查看数据面板
                </a>
              </div>
            </div>
            <div className="simulation-ribbon" aria-label="仿真进程">
              <div className="simulation-progress-block">
                <div className="summary-title-row">
                  <span>仿真进程</span>
                  <strong>{runtimeRibbon.percentLabel}</strong>
                </div>
                <progress
                  value={runtimeRibbon.percent}
                  max="100"
                  aria-label="三维控制台仿真进度"
                />
              </div>
              <div className="simulation-ribbon-metrics">
                <div>
                  <span>仿真时间</span>
                  <strong>
                    {runtimeRibbon.elapsedLabel} / {runtimeRibbon.durationLabel}
                  </strong>
                </div>
                <div>
                  <span>事件数</span>
                  <strong>{runtimeRibbon.eventCountLabel}</strong>
                </div>
                <div>
                  <span>卫星规模</span>
                  <strong>{runtimeRibbon.satelliteCountLabel}</strong>
                </div>
                <div>
                  <span>用户规模</span>
                  <strong>{runtimeRibbon.userCountLabel}</strong>
                </div>
              </div>
            </div>
            <div className="globe-panel">
              <Suspense
                fallback={
                  <div className="globe-loading" role="status">
                    三维引擎加载中
                  </div>
                }
              >
                <CesiumGlobe snapshot={snapshot} displaySimTime={displaySimTime} />
              </Suspense>
            </div>
            <div className="control-dock">
              <Suspense
                fallback={
                  <div className="control-panel-loading" role="status">
                    配置面板加载中
                  </div>
                }
              >
                <ConfigPanel
                  scenario={scenarioControls}
                  runtime={runtimeStatus}
                  progress={{
                    sim_time: displaySimTime,
                    duration: runtimeStatus.duration,
                    event_count: displayEventCount
                  }}
                  generatedConfig={generatedConfig}
                  onRuntimeControl={sendRuntimeControl}
                />
              </Suspense>
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

export interface RuntimeRibbonSummary {
  percent: number;
  percentLabel: string;
  elapsedLabel: string;
  durationLabel: string;
  eventCountLabel: string;
  satelliteCountLabel: string;
  userCountLabel: string;
}

export interface RuntimeProgressAnchor {
  simTime: number;
  wallTimeMs: number;
  status: RuntimeStatusPayload["status"];
  lifecycleState?: RuntimeStatusPayload["lifecycle_state"];
  speedFactor: number;
  duration: number;
}

export function defaultRuntimeProgressAnchor(
  runtimeStatus: RuntimeStatusPayload,
  nowMs = Date.now()
): RuntimeProgressAnchor {
  return {
    simTime: runtimeStatus.current_sim_time ?? 0,
    wallTimeMs: nowMs,
    status: runtimeStatus.status,
    lifecycleState: runtimeStatus.lifecycle_state,
    speedFactor: runtimeStatus.speed_factor,
    duration: runtimeStatus.duration
  };
}

export function nextRuntimeProgressAnchor(
  previous: RuntimeProgressAnchor,
  snapshotSimTime: number,
  runtimeStatus: RuntimeStatusPayload,
  nowMs: number
): RuntimeProgressAnchor {
  const observedSimTime = Math.max(
    0,
    snapshotSimTime,
    finiteNumberOrZero(runtimeStatus.current_sim_time)
  );
  const projectedSimTime = runtimeProgressSimTime(previous, nowMs);
  const statusChanged =
    previous.status !== runtimeStatus.status ||
    previous.lifecycleState !== runtimeStatus.lifecycle_state ||
    previous.speedFactor !== runtimeStatus.speed_factor ||
    previous.duration !== runtimeStatus.duration;
  if (runtimeStatusResetsDisplayClock(runtimeStatus)) {
    return {
      simTime: Math.min(observedSimTime, runtimeStatus.duration),
      wallTimeMs: nowMs,
      status: runtimeStatus.status,
      lifecycleState: runtimeStatus.lifecycle_state,
      speedFactor: runtimeStatus.speed_factor,
      duration: runtimeStatus.duration
    };
  }

  if (
    runtimeStatusIsProgressing(runtimeStatus) &&
    !statusChanged &&
    observedSimTime <= projectedSimTime
  ) {
    return previous;
  }

  return {
    simTime: Math.min(Math.max(observedSimTime, projectedSimTime), runtimeStatus.duration),
    wallTimeMs: nowMs,
    status: runtimeStatus.status,
    lifecycleState: runtimeStatus.lifecycle_state,
    speedFactor: runtimeStatus.speed_factor,
    duration: runtimeStatus.duration
  };
}

function runtimeStatusResetsDisplayClock(runtimeStatus: RuntimeStatusPayload): boolean {
  return ["RESET", "INITIALIZE", "CONFIG_UPDATE"].includes(runtimeStatus.last_action);
}

export function runtimeProgressSimTime(
  anchor: RuntimeProgressAnchor,
  nowMs: number
): number {
  if (!runtimeProgressAnchorIsRunning(anchor)) {
    return Math.min(anchor.simTime, anchor.duration);
  }
  const elapsedSeconds = Math.max(0, (nowMs - anchor.wallTimeMs) / 1000);
  return Math.min(anchor.duration, anchor.simTime + elapsedSeconds * anchor.speedFactor);
}

export function buildRuntimeRibbonSummary({
  simTime,
  eventCount,
  runtimeStatus,
  scenario
}: {
  simTime: number;
  eventCount: number;
  runtimeStatus: RuntimeStatusPayload;
  scenario: ScenarioControlValues;
}): RuntimeRibbonSummary {
  const duration = Math.max(1, runtimeStatus.duration);
  const elapsed = Math.min(Math.max(0, simTime), duration);
  const percent = Math.min(100, Math.max(0, (elapsed / duration) * 100));
  return {
    percent,
    percentLabel: `${formatPercent(percent)}%`,
    elapsedLabel: formatDurationCompact(elapsed),
    durationLabel: formatDurationCompact(duration),
    eventCountLabel: formatInteger(eventCount),
    satelliteCountLabel: formatInteger(scenario.satellite_count),
    userCountLabel: formatInteger(scenario.user_count)
  };
}

export function runtimeStatusRequiresStreams(
  status: RuntimeStatusPayload | undefined
): boolean {
  return status !== undefined && runtimeStatusIsProgressing(status);
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
        compute_capacity:
          typeof runtimeConfig.scenario.compute_capacity === "number"
            ? runtimeConfig.scenario.compute_capacity
            : scenario.scenario?.compute_capacity,
        compute_scheduling_policy:
          typeof runtimeConfig.scenario.compute_scheduling_policy === "string"
            ? runtimeConfig.scenario.compute_scheduling_policy
            : scenario.scenario?.compute_scheduling_policy,
        orbit: isRecord(runtimeConfig.scenario.orbit)
          ? {
              ...scenario.scenario?.orbit,
              update_interval_seconds:
                typeof runtimeConfig.scenario.orbit.update_interval_seconds === "number"
                  ? runtimeConfig.scenario.orbit.update_interval_seconds
                  : scenario.scenario?.orbit?.update_interval_seconds,
              plane_count:
                typeof runtimeConfig.scenario.orbit.plane_count === "number"
                  ? runtimeConfig.scenario.orbit.plane_count
                  : scenario.scenario?.orbit?.plane_count,
              altitude_m:
                typeof runtimeConfig.scenario.orbit.altitude_m === "number"
                  ? runtimeConfig.scenario.orbit.altitude_m
                  : scenario.scenario?.orbit?.altitude_m,
              inclination_deg:
                typeof runtimeConfig.scenario.orbit.inclination_deg === "number"
                  ? runtimeConfig.scenario.orbit.inclination_deg
                  : scenario.scenario?.orbit?.inclination_deg
            }
          : scenario.scenario?.orbit,
        traffic_model: isRecord(runtimeConfig.scenario.traffic_model)
          ? {
              ...scenario.scenario?.traffic_model,
              flow_interval_seconds:
                typeof runtimeConfig.scenario.traffic_model.flow_interval_seconds === "number"
                  ? runtimeConfig.scenario.traffic_model.flow_interval_seconds
                  : scenario.scenario?.traffic_model?.flow_interval_seconds,
              task_interval_seconds:
                typeof runtimeConfig.scenario.traffic_model.task_interval_seconds === "number"
                  ? runtimeConfig.scenario.traffic_model.task_interval_seconds
                  : scenario.scenario?.traffic_model?.task_interval_seconds,
              flow_demand_capacity:
                typeof runtimeConfig.scenario.traffic_model.flow_demand_capacity === "number"
                  ? runtimeConfig.scenario.traffic_model.flow_demand_capacity
                  : scenario.scenario?.traffic_model?.flow_demand_capacity,
              task_compute_demand:
                typeof runtimeConfig.scenario.traffic_model.task_compute_demand === "number"
                  ? runtimeConfig.scenario.traffic_model.task_compute_demand
                  : scenario.scenario?.traffic_model?.task_compute_demand,
              task_data_size:
                typeof runtimeConfig.scenario.traffic_model.task_data_size === "number"
                  ? runtimeConfig.scenario.traffic_model.task_data_size
                  : scenario.scenario?.traffic_model?.task_data_size
            }
          : scenario.scenario?.traffic_model
      }
    : scenario.scenario;
  const network = isRecord(runtimeConfig.network)
    ? {
        ...scenario.network,
        application_protocol:
          typeof runtimeConfig.network.application_protocol === "string"
            ? runtimeConfig.network.application_protocol
            : scenario.network?.application_protocol,
        transport_protocol:
          typeof runtimeConfig.network.transport_protocol === "string"
            ? runtimeConfig.network.transport_protocol
            : scenario.network?.transport_protocol,
        transport_loss_rate:
          typeof runtimeConfig.network.transport_loss_rate === "number"
            ? runtimeConfig.network.transport_loss_rate
            : scenario.network?.transport_loss_rate,
        transport_congestion_window_segments:
          typeof runtimeConfig.network.transport_congestion_window_segments === "number"
            ? runtimeConfig.network.transport_congestion_window_segments
            : scenario.network?.transport_congestion_window_segments,
        routing_protocol:
          typeof runtimeConfig.network.routing_protocol === "string"
            ? runtimeConfig.network.routing_protocol
            : scenario.network?.routing_protocol,
        datalink_mac_protocol:
          typeof runtimeConfig.network.datalink_mac_protocol === "string"
            ? runtimeConfig.network.datalink_mac_protocol
            : scenario.network?.datalink_mac_protocol,
        routing_latency_weight:
          typeof runtimeConfig.network.routing_latency_weight === "number"
            ? runtimeConfig.network.routing_latency_weight
            : scenario.network?.routing_latency_weight,
        routing_inverse_capacity_weight:
          typeof runtimeConfig.network.routing_inverse_capacity_weight === "number"
            ? runtimeConfig.network.routing_inverse_capacity_weight
            : scenario.network?.routing_inverse_capacity_weight,
        routing_hop_weight:
          typeof runtimeConfig.network.routing_hop_weight === "number"
            ? runtimeConfig.network.routing_hop_weight
            : scenario.network?.routing_hop_weight,
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
            : scenario.network?.antenna_aperture_efficiency,
        transmit_power_dbw:
          typeof runtimeConfig.network.transmit_power_dbw === "number"
            ? runtimeConfig.network.transmit_power_dbw
            : scenario.network?.transmit_power_dbw,
        system_loss_db:
          typeof runtimeConfig.network.system_loss_db === "number"
            ? runtimeConfig.network.system_loss_db
            : scenario.network?.system_loss_db,
        noise_temperature_k:
          typeof runtimeConfig.network.noise_temperature_k === "number"
            ? runtimeConfig.network.noise_temperature_k
            : scenario.network?.noise_temperature_k
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

function runtimeStatusIsProgressing(status: RuntimeStatusPayload): boolean {
  return (
    status.status === "RUNNING" &&
    status.lifecycle_state !== "COMPLETED" &&
    status.lifecycle_state !== "ERROR" &&
    status.lifecycle_state !== "STOPPED"
  );
}

function runtimeProgressAnchorIsRunning(anchor: RuntimeProgressAnchor): boolean {
  return (
    anchor.status === "RUNNING" &&
    anchor.lifecycleState !== "COMPLETED" &&
    anchor.lifecycleState !== "ERROR" &&
    anchor.lifecycleState !== "STOPPED"
  );
}

function finiteNumberOrZero(value: unknown): number {
  return typeof value === "number" && Number.isFinite(value) ? value : 0;
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

function formatInteger(value: number): string {
  return Math.round(value).toLocaleString("zh-CN");
}

function formatPercent(value: number): string {
  return value.toLocaleString("zh-CN", {
    maximumFractionDigits: 1,
    minimumFractionDigits: 0
  });
}

function formatDurationCompact(seconds: number): string {
  if (seconds < 60) {
    return `${Math.round(seconds)}秒`;
  }
  if (seconds < 3600) {
    return `${Math.floor(seconds / 60)}分${Math.round(seconds % 60)}秒`;
  }
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  return `${hours}时${minutes}分`;
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
    compute_capacity: scenarioConfig?.scenario?.compute_capacity ?? 10,
    compute_scheduling_policy:
      scenarioConfig?.scenario?.compute_scheduling_policy ?? "FIFO",
    orbit: {
      update_interval_seconds:
        scenarioConfig?.scenario?.orbit?.update_interval_seconds ?? 60,
      plane_count: scenarioConfig?.scenario?.orbit?.plane_count ?? 12,
      altitude_km: (scenarioConfig?.scenario?.orbit?.altitude_m ?? 550_000) / 1000,
      inclination_deg: scenarioConfig?.scenario?.orbit?.inclination_deg ?? 53
    },
    traffic_model: {
      flow_interval_seconds:
        scenarioConfig?.scenario?.traffic_model?.flow_interval_seconds ?? 60,
      task_interval_seconds:
        scenarioConfig?.scenario?.traffic_model?.task_interval_seconds ?? 60,
      flow_demand_capacity:
        scenarioConfig?.scenario?.traffic_model?.flow_demand_capacity ?? 25,
      task_compute_demand:
        scenarioConfig?.scenario?.traffic_model?.task_compute_demand ?? 20,
      task_data_size: scenarioConfig?.scenario?.traffic_model?.task_data_size ?? 2
    },
    visualization: {
      satellites: visualization?.satellites ?? true,
      links: visualization?.links ?? true,
      users: visualization?.users ?? true,
      metrics: visualization?.metrics ?? true
    },
    network: {
      application_protocol: scenarioConfig?.network?.application_protocol ?? "TASK_OFFLOAD_FLOW",
      transport_protocol: scenarioConfig?.network?.transport_protocol ?? "TCP",
      transport_loss_rate: scenarioConfig?.network?.transport_loss_rate ?? 0,
      transport_congestion_window_segments:
        scenarioConfig?.network?.transport_congestion_window_segments ?? 0,
      routing_protocol: scenarioConfig?.network?.routing_protocol ?? "LINK_STATE",
      datalink_mac_protocol: scenarioConfig?.network?.datalink_mac_protocol ?? "TDMA",
      routing_latency_weight: scenarioConfig?.network?.routing_latency_weight ?? 1,
      routing_inverse_capacity_weight:
        scenarioConfig?.network?.routing_inverse_capacity_weight ?? 0,
      routing_hop_weight: scenarioConfig?.network?.routing_hop_weight ?? 0,
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
        scenarioConfig?.network?.antenna_aperture_efficiency ?? 0.65,
      transmit_power_dbw: scenarioConfig?.network?.transmit_power_dbw ?? 20,
      system_loss_db: scenarioConfig?.network?.system_loss_db ?? 1,
      noise_temperature_k: scenarioConfig?.network?.noise_temperature_k ?? 290
    }
  };
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
