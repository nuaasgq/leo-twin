import { describe, expect, it } from "vitest";

import { SimEvent } from "../src/core/event_types";
import { RenderLoop, RenderLoopClock } from "../src/render/render_loop";
import { WorldStateReducer } from "../src/state/reducer";
import { SnapshotEngine } from "../src/state/snapshot_engine";
import { EventThrottleLayer } from "../src/stream/throttle_layer";

describe("frontend render performance architecture", () => {
  it("generates stable snapshots for 1000+ satellites without per-event publishing", () => {
    let timestamp = 1;
    const reducer = new WorldStateReducer({ eventLogLimit: 128 });
    const engine = new SnapshotEngine(reducer, {
      snapshotHz: 20,
      clock: () => timestamp++
    });

    reducer.applyEvents(orbitEvents(1500));
    expect(engine.getSnapshot().satellites.length).toBe(0);

    const started = Date.now();
    const snapshot = engine.publishNow();
    const elapsedMs = Date.now() - started;

    expect(snapshot.satellites.length).toBe(1500);
    expect(snapshot.event_count).toBe(1500);
    expect(snapshot.diff.satellite_ids.length).toBe(1500);
    expect(elapsedMs).toBeLessThan(250);
  });

  it("folds redundant high-rate orbit updates before reducer ingestion", () => {
    const reducer = new WorldStateReducer();
    const throttle = new EventThrottleLayer((events) => reducer.applyEvents(events), {
      flushIntervalMs: 10_000,
      maxEventsPerFlush: 10_000,
      dropRedundantUpdates: true
    });

    throttle.pushEvents(orbitEvents(10_000, 1000));
    expect(throttle.pendingCount()).toBe(1000);
    throttle.flush();

    const snapshot = new SnapshotEngine(reducer).publishNow();
    expect(snapshot.satellites.length).toBe(1000);
    expect(snapshot.event_count).toBe(1000);
    expect(snapshot.satellites[999].sim_time).toBeGreaterThan(0);
  });

  it("produces deterministic snapshots from identical event input", () => {
    const events = orbitEvents(128);
    const first = snapshotFromEvents(events);
    const second = snapshotFromEvents(events);

    expect(first.satellites).toEqual(second.satellites);
    expect(first.metrics_summary.orbit).toEqual(second.metrics_summary.orbit);
    expect(first.spatial_index).toEqual(second.spatial_index);
  });

  it("treats deadline missed tasks as terminal compute outcomes", () => {
    const snapshot = snapshotFromEvents([
      taskEvent("task-finished", "FINISHED"),
      taskEvent("task-timeout", "DEADLINE_MISSED")
    ]);

    expect(snapshot.active_tasks).toEqual([]);
    expect(snapshot.compute_nodes).toEqual([
      {
        node_id: "node-a",
        running_tasks: 0,
        finished_tasks: 2,
        capacity: 0,
        available_capacity: 0,
        status: "UNKNOWN",
        load_ratio: 0
      }
    ]);
    expect(snapshot.metrics_summary.compute).toEqual({
      taskQueueLength: 0,
      executionSuccessRate: 0.5,
      runningTasks: 0,
      finishedTasks: 1,
      deadlineMissedTasks: 1
    });
  });

  it("exposes metric records in deterministic snapshot order", () => {
    const snapshot = snapshotFromEvents([
      metricEvent("metric-b", "satellite.longitude_deg", "sat-b", 45),
      metricEvent("metric-a", "satellite.altitude_km", "sat-a", 629)
    ]);

    expect(snapshot.metrics.map((metric) => `${metric.metric_name}:${metric.entity_id}`)).toEqual([
      "satellite.altitude_km:sat-a",
      "satellite.longitude_deg:sat-b"
    ]);
    expect(snapshot.diff.metric_ids).toEqual([
      "satellite.altitude_km:sat-a",
      "satellite.longitude_deg:sat-b"
    ]);
  });

  it("counts topology changes from the bounded event log", () => {
    const snapshot = snapshotFromEvents([
      linkEvent("access-start", "ACCESS_START", "sat-a", "user-a", true),
      linkEvent("space-link", "LINK_UPDATE", "sat-a", "sat-b", true),
      routeEvent("route-a"),
      linkEvent("access-end", "ACCESS_END", "sat-a", "user-a", false)
    ]);

    expect(snapshot.metrics_summary.network.topology).toEqual({
      activeSpaceLinks: 1,
      activeAccessLinks: 0,
      linkUpdateEvents: 1,
      accessStartEvents: 1,
      accessEndEvents: 1,
      routeUpdateEvents: 1,
      topologyEvents: 4
    });
  });

  it("keeps the render loop independent of snapshot publication cadence", () => {
    const clock = new FakeRenderClock();
    const frames: number[] = [];
    const loop = new RenderLoop((frame) => frames.push(frame.fps), clock);

    loop.start();
    for (let index = 1; index <= 60; index += 1) {
      clock.step(index * 16.67);
    }
    loop.stop();

    expect(frames).toHaveLength(60);
    expect(frames.every((fps) => fps > 59)).toBe(true);
  });

  it("starts and stops with browser-safe timer invocation", () => {
    const originalSetInterval = globalThis.setInterval;
    const originalClearInterval = globalThis.clearInterval;
    const timer = 7 as ReturnType<typeof setInterval>;
    const intervals: number[] = [];

    Object.defineProperty(globalThis, "setInterval", {
      configurable: true,
      value(this: typeof globalThis, _handler: () => void, intervalMs?: number) {
        expect(this).toBe(globalThis);
        intervals.push(intervalMs ?? 0);
        return timer;
      }
    });
    Object.defineProperty(globalThis, "clearInterval", {
      configurable: true,
      value(this: typeof globalThis, receivedTimer: ReturnType<typeof setInterval>) {
        expect(this).toBe(globalThis);
        expect(receivedTimer).toBe(timer);
      }
    });

    try {
      const engine = new SnapshotEngine(new WorldStateReducer(), { snapshotHz: 20 });
      engine.start();
      engine.stop();
      expect(intervals).toEqual([50]);
    } finally {
      Object.defineProperty(globalThis, "setInterval", {
        configurable: true,
        value: originalSetInterval
      });
      Object.defineProperty(globalThis, "clearInterval", {
        configurable: true,
        value: originalClearInterval
      });
    }
  });
});

function snapshotFromEvents(events: readonly SimEvent[]) {
  const reducer = new WorldStateReducer();
  const engine = new SnapshotEngine(reducer, { clock: () => 1 });
  reducer.applyEvents(events);
  return engine.publishNow();
}

function orbitEvents(count: number, uniqueSatellites = count): SimEvent[] {
  return Array.from({ length: count }, (_, index) => {
    const satelliteIndex = index % uniqueSatellites;
    return {
      event_id: `orbit:${index.toString().padStart(5, "0")}`,
      sim_time: index / 20,
      priority: 0,
      source: "orbit",
      target: "frontend",
      event_type: "ORBIT_UPDATE",
      payload: {
        satellite_id: `sat-${satelliteIndex.toString().padStart(5, "0")}`,
        sim_time: index / 20,
        position: [satelliteIndex, satelliteIndex + 1, satelliteIndex + 2],
        velocity: [0, 0, 0],
        status: "online"
      }
    };
  });
}

function taskEvent(taskId: string, status: string): SimEvent {
  return {
    event_id: `task:${taskId}`,
    sim_time: 1,
    priority: 0,
    source: "compute",
    target: "frontend",
    event_type: "TASK_FINISH",
    payload: {
      task_id: taskId,
      node_id: "node-a",
      sim_time: 1,
      progress: 1,
      status
    }
  };
}

function metricEvent(
  eventId: string,
  metricName: string,
  entityId: string,
  value: number
): SimEvent {
  return {
    event_id: eventId,
    sim_time: 1,
    priority: 0,
    source: "metrics",
    target: "frontend",
    event_type: "METRIC_SAMPLE",
    payload: {
      metric_name: metricName,
      sim_time: 1,
      entity_id: entityId,
      value
    }
  };
}

function linkEvent(
  eventId: string,
  eventType: "ACCESS_START" | "ACCESS_END" | "LINK_UPDATE",
  sourceId: string,
  targetId: string,
  availability: boolean
): SimEvent {
  return {
    event_id: eventId,
    sim_time: 1,
    priority: 0,
    source: "network",
    target: "frontend",
    event_type: eventType,
    payload: {
      source_id: sourceId,
      target_id: targetId,
      latency: 0.1,
      capacity: 10,
      availability
    }
  };
}

function routeEvent(eventId: string): SimEvent {
  return {
    event_id: eventId,
    sim_time: 1,
    priority: 0,
    source: "network",
    target: "frontend",
    event_type: "ROUTE_UPDATE",
    payload: {
      route_id: eventId,
      flow_id: "flow-a",
      path: ["user-a", "sat-a", "sat-b", "compute-a"],
      latency: 1,
      capacity: 10,
      available: true
    }
  };
}

class FakeRenderClock implements RenderLoopClock {
  private callbacks = new Map<number, FrameRequestCallback>();
  private nextId = 1;

  requestAnimationFrame(callback: FrameRequestCallback): number {
    const id = this.nextId;
    this.nextId += 1;
    this.callbacks.set(id, callback);
    return id;
  }

  cancelAnimationFrame(frameId: number): void {
    this.callbacks.delete(frameId);
  }

  step(timestamp: number): void {
    const [id, callback] = this.callbacks.entries().next().value as [
      number,
      FrameRequestCallback
    ];
    this.callbacks.delete(id);
    callback(timestamp);
  }
}
