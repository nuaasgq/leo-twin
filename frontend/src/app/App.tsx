import { useEffect, useMemo, useState } from "react";

import { CesiumGlobe } from "../3d/cesium/CesiumGlobe";
import { Dashboard } from "../dashboard/Dashboard";
import { SnapshotEngine, useWorldSnapshot } from "../state/snapshot_engine";
import { WorldStateReducer } from "../state/reducer";
import { EventRouter } from "../stream/event_router";
import { EventThrottleLayer } from "../stream/throttle_layer";
import { WebSocketStreamClient } from "../stream/websocket_client";
import { loadMetricsSnapshot, loadScenarioConfig } from "./api";
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

  useEffect(() => {
    snapshotEngine.start();
    return () => snapshotEngine.stop();
  }, [snapshotEngine]);

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

    Promise.allSettled([loadScenarioConfig(), loadMetricsSnapshot()])
      .then(([scenario, metrics]) => {
        if (closed) {
          return;
        }
        if (scenario.status === "fulfilled") {
          snapshotEngine.applyScenarioConfig(scenario.value);
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
        <Dashboard snapshot={snapshot} />
      </section>
    </main>
  );
}
