import { useEffect, useMemo, useState } from "react";

import { CesiumGlobe } from "../3d/cesium/CesiumGlobe";
import { Dashboard } from "../dashboard/Dashboard";
import { EventRouter } from "../stream/event_router";
import { ObservabilityStore } from "../stream/state_store";
import { useObservabilityState } from "../stream/state_store/useObservabilityState";
import { WebSocketStreamClient } from "../stream/websocket_client";
import { loadMetricsSnapshot, loadScenarioConfig } from "./api";
import "./App.css";

export function App() {
  const store = useMemo(() => new ObservabilityStore({ eventLogLimit: 10_000 }), []);
  const state = useObservabilityState(store);
  const [connectionState, setConnectionState] = useState<"connecting" | "live" | "degraded">(
    "connecting"
  );

  useEffect(() => {
    let closed = false;
    const router = new EventRouter(store);
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
          store.applyScenarioConfig(scenario.value);
        }
        if (metrics.status === "fulfilled") {
          store.applySnapshot(metrics.value);
        }
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
    };
  }, [store]);

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
          <CesiumGlobe state={state} />
        </div>
        <Dashboard state={state} />
      </section>
    </main>
  );
}
