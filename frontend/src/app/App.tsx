import { Suspense, lazy, useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { MouseEvent } from "react";

import type { ScenarioControlValues } from "../config_panel/ConfigPanel";
import {
  ControlAck,
  ControlChannelClient,
  RuntimeAction
} from "../config_panel/controlClient";
import {
  FidelitySummary,
  GeneratedScenarioConfig,
  RuntimeBackpressureSummary,
  RuntimeStatusPayload,
  ScenarioConfig
} from "../core/event_types";
import { SnapshotEngine, WorldSnapshot, useWorldSnapshot } from "../state/snapshot_engine";
import { runtimeSpeedFactorLabel } from "../runtime_display";
import { WorldStateReducer } from "../state/reducer";
import { EventRouter } from "../stream/event_router";
import { EventThrottleLayer } from "../stream/throttle_layer";
import { WebSocketStreamClient } from "../stream/websocket_client";
import {
  loadMetricsSnapshot,
  loadRuntimeState,
  loadScenarioConfig,
  runtimeApiErrorMessage
} from "./api";
import "./App.css";

const RUNTIME_STATUS_POLL_MS = 250;
const RUNTIME_PROGRESS_TICK_MS = 100;

type RuntimeConnectionChannel = "http" | "control" | "events" | "state";
type RuntimeConnectionStatus = "idle" | "connecting" | "live" | "degraded";
type RuntimeConnectionHealth = Record<RuntimeConnectionChannel, RuntimeConnectionStatus>;
type RuntimeStreamConsumerCursors = Record<"events" | "state", number>;

const DEFAULT_RUNTIME_CONNECTION_HEALTH: RuntimeConnectionHealth = {
  http: "connecting",
  control: "connecting",
  events: "idle",
  state: "idle"
};

const DEFAULT_RUNTIME_STREAM_CONSUMER_CURSORS: RuntimeStreamConsumerCursors = {
  events: 0,
  state: 0
};

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
  const [connectionHealth, setConnectionHealth] = useState<RuntimeConnectionHealth>(
    DEFAULT_RUNTIME_CONNECTION_HEALTH
  );
  const [streamConsumerCursors, setStreamConsumerCursors] =
    useState<RuntimeStreamConsumerCursors>(DEFAULT_RUNTIME_STREAM_CONSUMER_CURSORS);
  const [scenarioConfig, setScenarioConfig] = useState<ScenarioConfig | null>(null);
  const [generatedConfig, setGeneratedConfig] = useState<GeneratedScenarioConfig | null>(null);
  const [controlError, setControlError] = useState<string | null>(null);
  const [runtimeStatus, setRuntimeStatus] = useState<RuntimeStatusPayload>(defaultRuntimeStatus());
  const [dismissedBackpressureNoticeKey, setDismissedBackpressureNoticeKey] =
    useState<string | null>(null);
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

  useEffect(() => {
    document.body.dataset.frontendSurface = bodySurfaceAttribute(surface);
    return () => {
      delete document.body.dataset.frontendSurface;
    };
  }, [surface]);

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

  const setConnectionChannel = useCallback(
    (channel: RuntimeConnectionChannel, status: RuntimeConnectionStatus) => {
      setConnectionHealth((previous) =>
        previous[channel] === status ? previous : { ...previous, [channel]: status }
      );
    },
    []
  );

  const closeStreams = useCallback(() => {
    streamClientRef.current?.close();
    streamRouterRef.current?.close();
    streamClientRef.current = null;
    streamRouterRef.current = null;
    setConnectionChannel("events", "idle");
    setConnectionChannel("state", "idle");
    setStreamConsumerCursors(DEFAULT_RUNTIME_STREAM_CONSUMER_CURSORS);
  }, [setConnectionChannel]);

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
    const [scenario, runtime, visibleSnapshot] = await Promise.all([
      loadScenarioConfig(),
      loadRuntimeState(),
      loadMetricsSnapshot()
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
    snapshotEngine.applySnapshot(visibleSnapshot);
    snapshotEngine.publishNow();
    setConnectionChannel("http", "live");
    return { scenario: effectiveScenario, runtime };
  }, [setConnectionChannel, snapshotEngine]);

  const handleRuntimeApiError = useCallback((error: unknown) => {
    setConnectionState("degraded");
    setConnectionChannel("http", "degraded");
    setControlError(runtimeApiErrorMessage(error));
  }, [setConnectionChannel]);

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
      setConnectionChannel("events", "connecting");
      setConnectionChannel("state", "connecting");
      const client = new WebSocketStreamClient(router, {
        batchSize: 500,
        flushIntervalMs: 40,
        stateStreamEnabled: true,
        onConnectionOpen: (channel) => {
          setConnectionChannel(channel, "live");
        },
        onConnectionIssue: (issue) => {
          setConnectionState("degraded");
          setConnectionChannel(issue.channel, "degraded");
          setControlError(runtimeWebSocketErrorMessage(issue.channel));
        },
        onCursorAdvance: (advance) => {
          setStreamConsumerCursors((previous) => ({
            ...previous,
            [advance.channel]: advance.nextCursor
          }));
        }
      });
      streamRouterRef.current = router;
      streamClientRef.current = client;
      client.connect();
    },
    [closeStreams, resetWorld, setConnectionChannel, snapshotEngine]
  );

  const controlClient = useMemo(
    () =>
      new ControlChannelClient({
        onMessage: (message) => {
          handleControlMessage(message, setRuntimeStatus);
          handleGeneratedConfig(message, setGeneratedConfig);
          if (message.ok === false) {
            setControlError(controlErrorMessage(message.error));
            return;
          }
          if (message.ok === true) {
            setControlError(null);
          }
          if (
            message.type === "RUNTIME_STATUS" &&
            runtimeStatusRequiresStreams(message.status) &&
            streamClientRef.current === null
          ) {
            loadControlState()
              .then(({ scenario }) =>
                startStreams(scenario, {
                  resetBeforeConnect: shouldResetWorldBeforeStreamConnect(
                    "ATTACH",
                    snapshotEngine.getSnapshot().event_count
                  )
                })
              )
              .catch(handleRuntimeApiError);
            return;
          }
          if (message.ok === true && message.type === "CONTROL_ACK") {
            const action = message.status?.last_action;
            if (action === "START") {
              loadControlState()
                .then(({ scenario }) =>
                  startStreams(scenario, {
                    resetBeforeConnect: shouldResetWorldBeforeStreamConnect(
                      "START",
                      snapshotEngine.getSnapshot().event_count
                    )
                  })
                )
                .catch(handleRuntimeApiError);
              return;
            }
            if (action === "RESUME") {
              loadControlState()
                .then(({ scenario }) => startStreams(scenario, { resetBeforeConnect: false }))
                .catch(handleRuntimeApiError);
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
                .catch(handleRuntimeApiError);
            }
          }
        },
        onConnectionOpen: () => {
          setConnectionChannel("control", "live");
        },
        onConnectionIssue: () => {
          setConnectionState("degraded");
          setConnectionChannel("control", "degraded");
          setControlError(runtimeWebSocketErrorMessage("control"));
        }
      }),
    [
      closeStreams,
      handleRuntimeApiError,
      loadControlState,
      resetWorld,
      setConnectionChannel,
      snapshotEngine,
      startStreams
    ]
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
      } catch (error) {
        if (!closed) {
          handleRuntimeApiError(error);
        }
      }
    };
    const timer = window.setInterval(refreshStatus, RUNTIME_STATUS_POLL_MS);
    void refreshStatus();
    return () => {
      closed = true;
      window.clearInterval(timer);
    };
  }, [handleRuntimeApiError, runtimeStatus.status, runtimeStatus.lifecycle_state]);

  useEffect(() => {
    let closed = false;
    loadControlState()
      .then(({ scenario, runtime }) => {
        if (closed) {
          return;
        }
        if (runtimeStatusRequiresStreams(runtime.status)) {
          startStreams(scenario, {
            resetBeforeConnect: shouldResetWorldBeforeStreamConnect(
              "ATTACH",
              snapshotEngine.getSnapshot().event_count
            )
          });
        } else {
          resetWorld(scenario);
        }
        setConnectionState("live");
        setControlError(null);
      })
      .catch((error) => {
        if (!closed) {
          handleRuntimeApiError(error);
        }
      });

    return () => {
      closed = true;
      closeStreams();
    };
  }, [closeStreams, handleRuntimeApiError, loadControlState, resetWorld, snapshotEngine, startStreams]);

  const scenarioControls = scenarioControlValues(scenarioConfig, snapshot.satellites.length);
  const displaySimTime = selectRuntimeDisplaySimTime(
    runtimeStatus,
    snapshot.last_sim_time,
    runtimeProgressAnchor,
    runtimeProgressNowMs
  );
  const displayEventCount = selectRuntimeDisplayEventCount(
    runtimeStatus,
    snapshot.event_count
  );
  const runtimeRibbon = buildRuntimeRibbonSummary({
    simTime: displaySimTime,
    eventCount: displayEventCount,
    runtimeStatus,
    scenario: scenarioControls
  });
  const surfaceSyncSummary = buildSurfaceSyncSummary({
    displaySimTime,
    snapshotSimTime: snapshot.last_sim_time,
    eventCount: displayEventCount,
    runtimeStatus
  });
  const connectionDiagnostics = connectionDiagnosticItems(
    connectionHealth,
    runtimeStatus.stream_diagnostics_v1,
    streamConsumerCursors
  );
  const fidelitySummary = selectFidelitySummary(runtimeStatus, generatedConfig, snapshot);
  const backpressureSummary = runtimeStatus.backpressure_summary ?? null;
  const backpressureNoticeKeyForStatus =
    backpressureSummary !== null && shouldShowBackpressureNotice(backpressureSummary)
      ? backpressureNoticeDismissKey(backpressureSummary)
      : null;
  const backpressureNoticeDismissed =
    backpressureNoticeKeyForStatus !== null &&
    backpressureNoticeKeyForStatus === dismissedBackpressureNoticeKey;

  useEffect(() => {
    if (backpressureNoticeKeyForStatus === null) {
      setDismissedBackpressureNoticeKey(null);
    }
  }, [backpressureNoticeKeyForStatus]);

  const sendRuntimeControl = useCallback(
    (action: RuntimeAction, payload: Record<string, unknown> = {}) => {
      setControlError(null);
      setRuntimeStatus((previous) => ({
        ...previous,
        last_action: `${action}_PENDING`
      }));
      controlClient.sendRuntimeControl(action, payload);
    },
    [controlClient]
  );
  const dismissBackpressureNotice = useCallback(() => {
    if (backpressureNoticeKeyForStatus !== null) {
      setDismissedBackpressureNoticeKey(backpressureNoticeKeyForStatus);
    }
  }, [backpressureNoticeKeyForStatus]);

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
        <div className="topbar-status-cluster" aria-label="前端运行同步状态">
          <div className="sync-pill">
            <span>{surfaceSyncSummary.statusLabel}</span>
            <strong>{surfaceSyncSummary.displayTimeLabel}</strong>
            <small>
              快照 {surfaceSyncSummary.snapshotTimeLabel} · {surfaceSyncSummary.deltaLabel} · 事件{" "}
              {surfaceSyncSummary.eventCountLabel}
            </small>
          </div>
          <div className={`connection-pill ${connectionState}`}>
            {connectionStateLabel(connectionState)}
          </div>
          <div className="connection-diagnostics" aria-label="连接诊断">
            {connectionDiagnostics.map((item) => (
              <span
                aria-label={item.description ?? `${item.label}：${item.statusLabel}`}
                className={`connection-diagnostic ${item.status}`}
                key={item.channel}
                title={item.description}
              >
                <small>{item.detail === undefined ? item.label : `${item.label} · ${item.detail}`}</small>
                <strong>{item.statusLabel}</strong>
              </span>
            ))}
          </div>
        </div>
      </header>
      {surface === "dashboard" ? (
        <section className="dashboard-page" aria-label="独立数据态势面板">
          <FidelityNotice summary={fidelitySummary} surface="dashboard" />
          <CompletionNotice runtimeStatus={runtimeStatus} surface="dashboard" />
          <BackpressureNotice
            summary={backpressureSummary}
            surface="dashboard"
            dismissed={backpressureNoticeDismissed}
            onDismiss={dismissBackpressureNotice}
          />
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
                  <strong>{runtimeSpeedFactorLabel(runtimeStatus)}</strong>
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
            <FidelityNotice summary={fidelitySummary} surface="control" />
            <CompletionNotice runtimeStatus={runtimeStatus} surface="control" />
            <BackpressureNotice
              summary={backpressureSummary}
              surface="control"
              dismissed={backpressureNoticeDismissed}
              onDismiss={dismissBackpressureNotice}
            />
            <div className="globe-panel">
              <Suspense
                fallback={
                  <div className="globe-loading" role="status">
                    三维引擎加载中
                  </div>
                }
              >
                <CesiumGlobe
                  snapshot={snapshot}
                  displaySimTime={displaySimTime}
                  satelliteKpiSlices={runtimeStatus.satellite_kpi_slices_v1}
                  satelliteKpiHistory={runtimeStatus.satellite_kpi_history_v1}
                />
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
                  controlError={controlError}
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

export function bodySurfaceAttribute(surface: FrontendSurface): FrontendSurface {
  return surface;
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

export interface SurfaceSyncSummary {
  displayTimeLabel: string;
  snapshotTimeLabel: string;
  deltaLabel: string;
  eventCountLabel: string;
  statusLabel: string;
}

export interface RuntimeProgressAnchor {
  simTime: number;
  wallTimeMs: number;
  status: RuntimeStatusPayload["status"];
  lifecycleState?: RuntimeStatusPayload["lifecycle_state"];
  speedFactor: number;
  duration: number;
}

export type StreamConnectReason = "START" | "RESUME" | "ATTACH";

export function shouldResetWorldBeforeStreamConnect(
  reason: StreamConnectReason,
  snapshotEventCount: number
): boolean {
  return reason === "START" && snapshotEventCount <= 0;
}

export function selectFidelitySummary(
  runtimeStatus: RuntimeStatusPayload,
  generatedConfig: GeneratedScenarioConfig | null,
  snapshot: WorldSnapshot
): FidelitySummary | null {
  return (
    runtimeStatus.fidelity_summary ??
    generatedConfig?.backend_summary?.fidelity_summary ??
    snapshot.fidelity_summary ??
    snapshot.scenario_config?.backend_summary?.fidelity_summary ??
    null
  );
}

export function shouldShowFidelityNotice(summary: FidelitySummary | null): boolean {
  if (summary === null) {
    return false;
  }
  return (
    summary.orbit_update_mode !== "PER_SATELLITE" ||
    summary.metrics_mode !== "DETAILED" ||
    summary.space_link_mode !== "DETAILED_SMALL_SCALE" ||
    !summary.detailed_space_link_enabled ||
    summary.scale_limit_reason !== "none"
  );
}

export function fidelityNoticeText(summary: FidelitySummary): string {
  const details: string[] = [];
  if (summary.orbit_update_mode === "BATCH") {
    details.push("轨道更新采用批量模式。");
  } else {
    details.push(`轨道更新模式为 ${summary.orbit_update_mode}。`);
  }
  if (summary.metrics_mode === "AGGREGATED") {
    details.push("指标采用聚合模式。");
  } else {
    details.push(`指标模式为 ${summary.metrics_mode}。`);
  }
  if (summary.space_link_mode === "DISABLED") {
    details.push("星间链路更新已关闭。");
  } else if (summary.space_link_mode === "BOUNDED_CANDIDATE") {
    details.push("星间链路采用有界候选更新。");
  } else if (!summary.detailed_space_link_enabled) {
    details.push("星间链路使用降级精度。");
  } else {
    details.push("星间链路使用小规模详细更新。");
  }
  return `规模模式：${formatInteger(summary.satellite_count)} 颗卫星。${details.join("")}`;
}

function fidelityNoticeDetail(summary: FidelitySummary): string {
  if (summary.space_link_mode === "BOUNDED_CANDIDATE") {
    return [
      "后端策略：同轨邻近与相邻轨道有界候选；",
      `每星候选上限 ${formatInteger(summary.max_space_link_candidates_per_satellite)}，`,
      `详细批量阈值 ${formatInteger(summary.batch_space_link_update_limit)}。`
    ].join("");
  }
  if (summary.space_link_mode === "DISABLED") {
    return "后端策略：关闭星间链路更新以保持大规模控制响应。";
  }
  if (summary.scale_limit_reason !== "none") {
    return `后端策略：${summary.current_scale_mode}。`;
  }
  return `后端策略：${summary.space_link_candidate_policy}。`;
}

function FidelityNotice({
  summary,
  surface
}: {
  summary: FidelitySummary | null;
  surface: "control" | "dashboard";
}) {
  if (summary === null || !shouldShowFidelityNotice(summary)) {
    return null;
  }
  return (
    <div className={`fidelity-notice ${surface}`} role="status" aria-live="polite">
      <span>规模精度策略</span>
      <strong>{fidelityNoticeText(summary)}</strong>
      <small>{fidelityNoticeDetail(summary)}</small>
    </div>
  );
}

export function shouldShowCompletionNotice(
  runtimeStatus: RuntimeStatusPayload | null | undefined
): boolean {
  if (runtimeStatus === null || runtimeStatus === undefined) {
    return false;
  }
  return (
    runtimeStatus.status === "COMPLETED" ||
    runtimeStatus.lifecycle_state === "COMPLETED"
  );
}

export function completionNoticeText(runtimeStatus: RuntimeStatusPayload): string {
  const elapsed = Math.max(
    0,
    finiteNumberOrZero(runtimeStatus.current_sim_time ?? runtimeStatus.duration)
  );
  const duration = Math.max(1, runtimeStatus.duration);
  return `仿真已完成：达到配置时长 ${formatDurationCompact(duration)}，最终仿真时间 ${formatDurationCompact(
    Math.min(elapsed, duration)
  )}。`;
}

export function completionNoticeDetail(runtimeStatus: RuntimeStatusPayload): string {
  const eventCount =
    typeof runtimeStatus.processed_event_count === "number"
      ? formatInteger(runtimeStatus.processed_event_count)
      : "0";
  return `后端推进循环已停止，事件流保持最终状态。事件数 ${eventCount}；重置后可重新初始化并开始下一轮仿真。`;
}

function CompletionNotice({
  runtimeStatus,
  surface
}: {
  runtimeStatus: RuntimeStatusPayload;
  surface: "control" | "dashboard";
}) {
  if (!shouldShowCompletionNotice(runtimeStatus)) {
    return null;
  }
  return (
    <div
      className={`fidelity-notice completion ${surface}`}
      role="status"
      aria-live="polite"
    >
      <span>仿真完成</span>
      <strong>{completionNoticeText(runtimeStatus)}</strong>
      <small>{completionNoticeDetail(runtimeStatus)}</small>
    </div>
  );
}

export function shouldShowBackpressureNotice(
  summary: RuntimeBackpressureSummary | null | undefined
): boolean {
  if (summary === null || summary === undefined) {
    return false;
  }
  return summary.overloaded || summary.first_tick_heavy;
}

export function backpressureNoticeDismissKey(summary: RuntimeBackpressureSummary): string {
  return [
    String(summary.overloaded),
    String(summary.first_tick_heavy),
    summary.bottleneck_component,
    summary.recommended_action
  ].join("|");
}

export function backpressureNoticeText(summary: RuntimeBackpressureSummary): string {
  return [
    `运行压力：最近推进 ${formatMilliseconds(summary.tick_duration_ms)}，`,
    `预算 ${formatMilliseconds(summary.tick_budget_ms)}。`,
    `瓶颈组件：${summary.bottleneck_component}。`
  ].join("");
}

function backpressureNoticeDetail(summary: RuntimeBackpressureSummary): string {
  return [
    `队列深度 ${formatInteger(summary.queue_depth)}，`,
    `本 tick 处理事件 ${formatInteger(summary.processed_event_count)}，`,
    `建议：${summary.recommended_action}。`
  ].join("");
}

function BackpressureNotice({
  summary,
  surface,
  dismissed,
  onDismiss
}: {
  summary: RuntimeBackpressureSummary | null;
  surface: "control" | "dashboard";
  dismissed?: boolean;
  onDismiss?: () => void;
}) {
  if (summary === null || dismissed === true || !shouldShowBackpressureNotice(summary)) {
    return null;
  }
  return (
    <div className={`fidelity-notice backpressure ${surface}`} role="status" aria-live="polite">
      <button
        type="button"
        className="fidelity-notice-dismiss"
        aria-label="关闭运行压力提示"
        onClick={onDismiss}
      >
        x
      </button>
      <span>运行压力提示</span>
      <strong>{backpressureNoticeText(summary)}</strong>
      <small>{backpressureNoticeDetail(summary)}</small>
    </div>
  );
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
  const resetDisplayClock = runtimeStatusResetsDisplayClock(runtimeStatus);
  const observedSimTime = Math.max(
    0,
    resetDisplayClock ? 0 : snapshotSimTime,
    resetDisplayClock ? 0 : finiteNumberOrZero(runtimeStatus.current_sim_time)
  );
  const projectedSimTime = runtimeProgressSimTime(previous, nowMs);
  const statusChanged =
    previous.status !== runtimeStatus.status ||
    previous.lifecycleState !== runtimeStatus.lifecycle_state ||
    previous.speedFactor !== runtimeStatus.speed_factor ||
    previous.duration !== runtimeStatus.duration;
  if (resetDisplayClock) {
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

export function selectRuntimeDisplaySimTime(
  runtimeStatus: RuntimeStatusPayload,
  snapshotSimTime: number,
  anchor: RuntimeProgressAnchor,
  nowMs: number
): number {
  if (runtimeStatusResetsDisplayClock(runtimeStatus)) {
    return 0;
  }
  return Math.max(snapshotSimTime, runtimeProgressSimTime(anchor, nowMs));
}

export function selectRuntimeDisplayEventCount(
  runtimeStatus: RuntimeStatusPayload,
  snapshotEventCount: number
): number {
  if (runtimeStatusResetsDisplayClock(runtimeStatus)) {
    return 0;
  }
  return runtimeStatus.processed_event_count ?? snapshotEventCount;
}

function runtimeStatusResetsDisplayClock(runtimeStatus: RuntimeStatusPayload): boolean {
  return [
    "RESET_PENDING",
    "RESET",
    "INITIALIZE_PENDING",
    "INITIALIZE",
    "CONFIG_UPDATE_PENDING",
    "CONFIG_UPDATE"
  ].includes(runtimeStatus.last_action);
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

export function buildSurfaceSyncSummary({
  displaySimTime,
  snapshotSimTime,
  eventCount,
  runtimeStatus
}: {
  displaySimTime: number;
  snapshotSimTime: number;
  eventCount: number;
  runtimeStatus: RuntimeStatusPayload;
}): SurfaceSyncSummary {
  const boundedDisplayTime = Math.max(0, displaySimTime);
  const boundedSnapshotTime = Math.max(0, snapshotSimTime);
  const deltaSeconds = boundedDisplayTime - boundedSnapshotTime;
  const statusLabel =
    runtimeStatus.status === "RUNNING"
      ? "同步运行"
      : runtimeStatus.status === "PAUSED"
        ? "同步暂停"
        : runtimeStatus.status === "COMPLETED" || runtimeStatus.lifecycle_state === "COMPLETED"
          ? "同步完成"
          : "同步待机";
  return {
    displayTimeLabel: `显示 ${formatDurationCompact(boundedDisplayTime)}`,
    snapshotTimeLabel: formatDurationCompact(boundedSnapshotTime),
    deltaLabel: formatSyncDelta(deltaSeconds),
    eventCountLabel: formatInteger(eventCount),
    statusLabel
  };
}

function formatSyncDelta(deltaSeconds: number): string {
  const magnitude = Math.abs(deltaSeconds);
  if (magnitude < 0.05) {
    return "同帧";
  }
  const label = formatDurationCompact(magnitude);
  return deltaSeconds > 0 ? `前端插值 +${label}` : `快照领先 ${label}`;
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
        ...numberField(
          runtimeConfig.scenario,
          "compute_cpu_gflops_fp64",
          scenario.scenario?.compute_cpu_gflops_fp64
        ),
        ...numberField(
          runtimeConfig.scenario,
          "compute_gpu_tflops_fp32",
          scenario.scenario?.compute_gpu_tflops_fp32
        ),
        ...numberField(
          runtimeConfig.scenario,
          "compute_gpu_tflops_fp16",
          scenario.scenario?.compute_gpu_tflops_fp16
        ),
        ...numberField(
          runtimeConfig.scenario,
          "compute_npu_tops_int8",
          scenario.scenario?.compute_npu_tops_int8
        ),
        ...numberField(
          runtimeConfig.scenario,
          "compute_memory_gb",
          scenario.scenario?.compute_memory_gb
        ),
        ...numberField(
          runtimeConfig.scenario,
          "compute_storage_gb",
          scenario.scenario?.compute_storage_gb
        ),
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
        traffic_model: mergeTrafficModelConfig(
          scenario.scenario?.traffic_model,
          runtimeConfig.scenario
        )
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
            : scenario.network?.noise_temperature_k,
        space_link_mode:
          typeof runtimeConfig.network.space_link_mode === "string" ||
          runtimeConfig.network.space_link_mode === null
            ? runtimeConfig.network.space_link_mode
            : scenario.network?.space_link_mode,
        max_space_link_candidates_per_satellite:
          typeof runtimeConfig.network.max_space_link_candidates_per_satellite === "number"
            ? runtimeConfig.network.max_space_link_candidates_per_satellite
            : scenario.network?.max_space_link_candidates_per_satellite,
        batch_space_link_update_limit:
          typeof runtimeConfig.network.batch_space_link_update_limit === "number"
            ? runtimeConfig.network.batch_space_link_update_limit
            : scenario.network?.batch_space_link_update_limit
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

type TrafficModelConfig = NonNullable<NonNullable<ScenarioConfig["scenario"]>["traffic_model"]>;

function mergeTrafficModelConfig(
  base: TrafficModelConfig | undefined,
  runtimeScenario: Record<string, unknown>
): TrafficModelConfig | undefined {
  const rawTraffic = isRecord(runtimeScenario.traffic_model)
    ? runtimeScenario.traffic_model
    : null;
  const hasTopLevelSmoothing =
    "initial_workload_smoothing_enabled" in runtimeScenario ||
    "initial_workload_window_s" in runtimeScenario ||
    "max_initial_events_per_tick" in runtimeScenario ||
    "workload_smoothing_mode" in runtimeScenario;
  if (rawTraffic === null && !hasTopLevelSmoothing) {
    return base;
  }
  const traffic: Record<string, unknown> = rawTraffic ?? {};
  const merged: TrafficModelConfig = { ...base };
  for (const key of [
    "flow_interval_seconds",
    "task_interval_seconds",
    "flow_demand_capacity",
    "task_compute_demand",
    "task_data_size",
    "output_data_size",
    "initial_workload_window_s",
    "max_initial_events_per_tick"
  ] as const) {
    const value = numberFromRuntimeScenario(runtimeScenario, traffic, key);
    if (value !== undefined) {
      merged[key] = value;
    }
  }
  const smoothingEnabled = booleanFromRuntimeScenario(
    runtimeScenario,
    traffic,
    "initial_workload_smoothing_enabled"
  );
  if (smoothingEnabled !== undefined) {
    merged.initial_workload_smoothing_enabled = smoothingEnabled;
  }
  const smoothingMode = stringFromRuntimeScenario(
    runtimeScenario,
    traffic,
    "workload_smoothing_mode"
  );
  if (smoothingMode !== undefined) {
    merged.workload_smoothing_mode = smoothingMode;
  }
  for (const key of ["traffic_class", "destination_type"] as const) {
    const value = stringFromRuntimeScenario(runtimeScenario, traffic, key);
    if (value !== undefined) {
      merged[key] = value;
    }
  }
  return merged;
}

function numberFromRuntimeScenario(
  runtimeScenario: Record<string, unknown>,
  rawTraffic: Record<string, unknown>,
  key: string
): number | undefined {
  if (typeof runtimeScenario[key] === "number") {
    return runtimeScenario[key];
  }
  return typeof rawTraffic[key] === "number" ? rawTraffic[key] : undefined;
}

function booleanFromRuntimeScenario(
  runtimeScenario: Record<string, unknown>,
  rawTraffic: Record<string, unknown>,
  key: string
): boolean | undefined {
  if (typeof runtimeScenario[key] === "boolean") {
    return runtimeScenario[key];
  }
  return typeof rawTraffic[key] === "boolean" ? rawTraffic[key] : undefined;
}

function stringFromRuntimeScenario(
  runtimeScenario: Record<string, unknown>,
  rawTraffic: Record<string, unknown>,
  key: string
): string | undefined {
  if (typeof runtimeScenario[key] === "string") {
    return runtimeScenario[key];
  }
  return typeof rawTraffic[key] === "string" ? rawTraffic[key] : undefined;
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

export interface ConnectionDiagnosticItem {
  channel: RuntimeConnectionChannel;
  label: string;
  status: RuntimeConnectionStatus;
  statusLabel: string;
  detail?: string;
  description?: string;
}

export function connectionDiagnosticItems(
  health: RuntimeConnectionHealth,
  streamDiagnostics?: RuntimeStatusPayload["stream_diagnostics_v1"],
  consumerCursors?: RuntimeStreamConsumerCursors
): readonly ConnectionDiagnosticItem[] {
  return (["http", "control", "events", "state"] as const).map((channel) => {
    const detail = connectionDiagnosticDetail(channel, streamDiagnostics, consumerCursors);
    const description = connectionDiagnosticDescription(
      channel,
      health[channel],
      streamDiagnostics,
      consumerCursors
    );
    return {
      channel,
      label: connectionChannelLabel(channel),
      status: health[channel],
      statusLabel: connectionStatusLabel(health[channel]),
      ...(detail === undefined ? {} : { detail }),
      ...(description === undefined ? {} : { description })
    };
  });
}

function connectionChannelLabel(channel: RuntimeConnectionChannel): string {
  if (channel === "http") {
    return "HTTP";
  }
  if (channel === "control") {
    return "控制";
  }
  if (channel === "events") {
    return "事件";
  }
  return "状态";
}

function connectionStatusLabel(status: RuntimeConnectionStatus): string {
  if (status === "idle") {
    return "空闲";
  }
  if (status === "connecting") {
    return "连接中";
  }
  if (status === "live") {
    return "正常";
  }
  return "异常";
}

function connectionDiagnosticDetail(
  channel: RuntimeConnectionChannel,
  streamDiagnostics: RuntimeStatusPayload["stream_diagnostics_v1"] | undefined,
  consumerCursors: RuntimeStreamConsumerCursors | undefined
): string | undefined {
  if (streamDiagnostics === undefined) {
    return undefined;
  }
  const stream =
    channel === "events"
      ? streamDiagnostics.event_stream
      : channel === "state"
        ? streamDiagnostics.state_stream
        : undefined;
  if (stream === undefined) {
    return undefined;
  }
  const consumedCursor =
    channel === "events" || channel === "state" ? consumerCursors?.[channel] : undefined;
  const consumed =
    consumedCursor === undefined ? "" : ` / 已收 ${formatInteger(consumedCursor)}`;
  const lag =
    consumedCursor === undefined
      ? ""
      : ` / 滞后 ${formatInteger(Math.max(0, stream.next_cursor - consumedCursor))}`;
  const dropped =
    stream.total_dropped_count > 0
      ? ` / 丢弃 ${formatInteger(stream.total_dropped_count)}`
      : "";
  return `游标 ${formatInteger(stream.next_cursor)} / 留存 ${formatInteger(
    stream.retained_count
  )}${consumed}${lag}${dropped}`;
}

function connectionDiagnosticDescription(
  channel: RuntimeConnectionChannel,
  status: RuntimeConnectionStatus,
  streamDiagnostics: RuntimeStatusPayload["stream_diagnostics_v1"] | undefined,
  consumerCursors: RuntimeStreamConsumerCursors | undefined
): string | undefined {
  const label = connectionChannelLabel(channel);
  const statusLabel = connectionStatusLabel(status);
  const stream =
    channel === "events"
      ? streamDiagnostics?.event_stream
      : channel === "state"
        ? streamDiagnostics?.state_stream
        : undefined;
  if (stream === undefined) {
    return undefined;
  }
  const consumedCursor =
    channel === "events" || channel === "state" ? consumerCursors?.[channel] : undefined;
  const lag =
    consumedCursor === undefined ? undefined : Math.max(0, stream.next_cursor - consumedCursor);
  const consumedText =
    consumedCursor === undefined
      ? "浏览器消费游标尚未上报"
      : `浏览器已消费到 ${formatInteger(consumedCursor)}，滞后 ${formatInteger(lag ?? 0)} 条`;
  const droppedText =
    stream.total_dropped_count > 0
      ? `累计丢弃 ${formatInteger(stream.total_dropped_count)} 条`
      : "未发生丢弃";
  const overflowText = stream.overflow_risk
    ? "当前接近缓冲区上限，可能需要降低刷新频率或检查后端推进速度"
    : "当前没有缓冲区溢出风险";
  return `${label}流诊断：连接${statusLabel}，后端下一游标 ${formatInteger(
    stream.next_cursor
  )}，留存 ${formatInteger(stream.retained_count)} 条，${consumedText}，${droppedText}。${overflowText}。`;
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
  if (status === "COMPLETED") {
    return "已完成";
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

function formatMilliseconds(value: number): string {
  return `${Math.max(0, value).toLocaleString("zh-CN", {
    maximumFractionDigits: 1,
    minimumFractionDigits: 0
  })} ms`;
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

export function controlErrorMessage(error: string | undefined): string {
  if (error === undefined || error.length === 0) {
    return "控制命令执行失败，请检查后端运行状态。";
  }
  if (error.includes("scale safety check failed")) {
    return [
      "当前配置超出实时交互演示安全上限。",
      "请缩短仿真时长、降低卫星/算力节点数量，或使用离线批处理模式。"
    ].join("");
  }
  return error;
}

type RuntimeWebSocketChannel = "control" | "events" | "state";

export function runtimeWebSocketErrorMessage(channel: RuntimeWebSocketChannel): string {
  const channelLabel =
    channel === "control" ? "控制通道" : channel === "events" ? "事件流" : "状态流";
  return [
    `${channelLabel}连接中断。`,
    "请执行 scripts\\sees_launcher.ps1 status 检查后端和前端是否 HTTP healthy，",
    "必要时运行 restart_leo_twin.bat。"
  ].join("");
}

function numberField(
  record: Record<string, unknown>,
  key: string,
  fallback: number | undefined
): Record<string, number> {
  const value = record[key];
  if (typeof value === "number") {
    return { [key]: value };
  }
  if (fallback !== undefined) {
    return { [key]: fallback };
  }
  return {};
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
    compute_cpu_gflops_fp64: scenarioConfig?.scenario?.compute_cpu_gflops_fp64 ?? 0,
    compute_gpu_tflops_fp32: scenarioConfig?.scenario?.compute_gpu_tflops_fp32 ?? 0,
    compute_gpu_tflops_fp16: scenarioConfig?.scenario?.compute_gpu_tflops_fp16 ?? 0,
    compute_npu_tops_int8: scenarioConfig?.scenario?.compute_npu_tops_int8 ?? 0,
    compute_memory_gb: scenarioConfig?.scenario?.compute_memory_gb ?? 0,
    compute_storage_gb: scenarioConfig?.scenario?.compute_storage_gb ?? 0,
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
      task_data_size: scenarioConfig?.scenario?.traffic_model?.task_data_size ?? 2,
      traffic_class:
        scenarioConfig?.scenario?.traffic_model?.traffic_class ?? "COMPUTE_SERVICE",
      destination_type:
        scenarioConfig?.scenario?.traffic_model?.destination_type ?? "COMPUTE_NODE",
      output_data_size: scenarioConfig?.scenario?.traffic_model?.output_data_size ?? 0
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
