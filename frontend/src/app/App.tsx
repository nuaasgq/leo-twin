import { useCallback, useEffect, useMemo, useState } from "react";

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
import { loadMetricsSnapshot, loadRuntimeStatus, loadScenarioConfig } from "./api";
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

  useEffect(() => {
    snapshotEngine.start();
    return () => snapshotEngine.stop();
  }, [snapshotEngine]);

  const refreshSnapshot = useCallback(async () => {
    const [scenario, metrics, runtime] = await Promise.all([
      loadScenarioConfig(),
      loadMetricsSnapshot(),
      loadRuntimeStatus()
    ]);
    setScenarioConfig(scenario);
    setRuntimeStatus((previous) => ({
      ...previous,
      ...scenario.runtime,
      ...runtime
    }));
    snapshotEngine.applyScenarioConfig(scenario);
    snapshotEngine.applySnapshot(metrics);
    snapshotEngine.publishNow();
  }, [snapshotEngine]);

  const controlClient = useMemo(
    () =>
      new ControlChannelClient({
        onMessage: (message) => {
          handleControlMessage(message, setRuntimeStatus);
          if (message.ok === true && message.type === "CONTROL_ACK") {
            refreshSnapshot().catch(() => setConnectionState("degraded"));
          }
        }
      }),
    [refreshSnapshot]
  );

  useEffect(() => {
    controlClient.connect();
    return () => controlClient.close();
  }, [controlClient]);

  useEffect(() => {
    let closed = false;
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

    Promise.allSettled([loadScenarioConfig(), loadMetricsSnapshot(), loadRuntimeStatus()])
      .then(([scenario, metrics, runtime]) => {
        if (closed) {
          return;
        }
        if (scenario.status === "fulfilled") {
          snapshotEngine.applyScenarioConfig(scenario.value);
          setScenarioConfig(scenario.value);
          setRuntimeStatus((previous) => ({
            ...previous,
            ...scenario.value.runtime,
            status: scenario.value.runtime?.status ?? previous.status,
            mode: scenario.value.runtime?.mode ?? previous.mode,
            speed_factor: scenario.value.runtime?.speed_factor ?? previous.speed_factor,
            seed: scenario.value.runtime?.seed ?? previous.seed,
            duration: scenario.value.runtime?.duration ?? previous.duration
          }));
        }
        if (runtime.status === "fulfilled") {
          setRuntimeStatus(runtime.value);
        }
        if (metrics.status === "fulfilled") {
          snapshotEngine.applySnapshot(metrics.value);
        }
        snapshotEngine.publishNow();
        client.connect();
        setConnectionState("live");
      })
      .catch(() => {
        if (!closed) {
          setConnectionState("degraded");
        }
      });

    return () => {
      closed = true;
      client.close();
      router.close();
    };
  }, [snapshotEngine]);

  const scenarioControls = scenarioControlValues(scenarioConfig, snapshot.satellites.length);

  const sendConfigUpdate = useCallback(
    (payload: Record<string, unknown>) => {
      controlClient.sendConfigUpdate(payload);
    },
    [controlClient]
  );

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
          <div className="brand-subtitle">Observability Console</div>
        </div>
        <div className={`connection-pill ${connectionState}`}>{connectionState}</div>
      </header>
      <section className="workspace">
        <div className="globe-panel">
          <CesiumGlobe snapshot={snapshot} />
        </div>
        <aside className="side-panel">
          <ConfigPanel
            scenario={scenarioControls}
            runtime={runtimeStatus}
            onConfigUpdate={sendConfigUpdate}
            onRuntimeControl={sendRuntimeControl}
          />
          <Dashboard snapshot={snapshot} />
        </aside>
      </section>
    </main>
  );
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
