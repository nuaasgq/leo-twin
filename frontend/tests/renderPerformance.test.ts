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

  it("ignores stale state snapshots that arrive after newer stream events", () => {
    const reducer = new WorldStateReducer();
    const engine = new SnapshotEngine(reducer, { clock: () => 1 });

    reducer.applyEvents([
      orbitEvent("orbit-new", "sat-a", 10, [10, 0, 0]),
      taskEvent("task-a", "RUNNING", 10, 0.9),
      computeNodeEvent("node-a", 10, 10, 1)
    ]);
    reducer.applySnapshot({
      satellites: [
        {
          satellite_id: "sat-a",
          sim_time: 5,
          position: [5, 0, 0],
          velocity: [0, 0, 0],
          status: "stale"
        }
      ],
      tasks: [
        {
          task_id: "task-a",
          node_id: "node-a",
          sim_time: 5,
          progress: 0.1,
          status: "STALE"
        }
      ],
      compute_nodes: [
        {
          node_id: "node-a",
          sim_time: 5,
          capacity: 10,
          available_capacity: 8,
          status: "STALE"
        }
      ]
    });

    const snapshot = engine.publishNow();

    expect(snapshot.satellites[0]).toMatchObject({
      sim_time: 10,
      position: [10, 0, 0],
      status: "online"
    });
    expect(snapshot.active_tasks[0]).toMatchObject({
      sim_time: 10,
      progress: 0.9,
      status: "RUNNING"
    });
    expect(snapshot.compute_nodes[0]).toMatchObject({
      available_capacity: 1,
      status: "BUSY"
    });
  });

  it("hydrates snapshot counters without rolling back newer stream events", () => {
    const reducer = new WorldStateReducer();
    const engine = new SnapshotEngine(reducer, { clock: () => 1 });

    reducer.applySnapshot({
      event_count: 500,
      last_sim_time: 120
    });
    let snapshot = engine.publishNow();

    expect(snapshot.event_count).toBe(500);
    expect(snapshot.last_sim_time).toBe(120);

    reducer.applyEvents([orbitEvent("orbit-new", "sat-a", 130, [130, 0, 0])]);
    reducer.applySnapshot({
      event_count: 400,
      last_sim_time: 90
    });
    snapshot = engine.publishNow();

    expect(snapshot.event_count).toBe(501);
    expect(snapshot.last_sim_time).toBe(130);
    expect(snapshot.satellites[0].sim_time).toBe(130);
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

  it("builds backend network KPI series from metric samples", () => {
    const snapshot = snapshotFromEvents([
      metricEvent("throughput-1", "network.quality.effective_throughput_mbps", "system", 80, 1),
      metricEvent("latency-1", "network.quality.effective_latency_s", "system", 0.08, 1),
      metricEvent("loss-1", "network.quality.effective_loss_proxy_rate", "system", 0.01, 1),
      metricEvent("jitter-1", "network.quality.effective_delay_variation_s", "system", 0.002, 1),
      metricEvent("throughput-2", "network.quality.effective_throughput_mbps", "system", 120, 2),
      metricEvent("latency-2", "network.quality.effective_latency_s", "system", 0.12, 2),
      metricEvent("loss-2", "network.quality.effective_loss_proxy_rate", "system", 0.03, 2),
      metricEvent("jitter-2", "network.quality.effective_delay_variation_s", "system", 0.004, 2)
    ]);

    expect(snapshot.metrics_summary.network.kpiSeries).toEqual([
      {
        simTime: 1,
        throughputMbps: 80,
        latencyMs: 80,
        lossPercent: 1,
        jitterMs: 2
      },
      {
        simTime: 2,
        throughputMbps: 120,
        latencyMs: 120,
        lossPercent: 3,
        jitterMs: 4
      }
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
    return orbitEvent(
      `orbit:${index.toString().padStart(5, "0")}`,
      `sat-${satelliteIndex.toString().padStart(5, "0")}`,
      index / 20,
      [satelliteIndex, satelliteIndex + 1, satelliteIndex + 2]
    );
  });
}

function orbitEvent(
  eventId: string,
  satelliteId: string,
  simTime: number,
  position: readonly [number, number, number]
): SimEvent {
  return {
    event_id: eventId,
    sim_time: simTime,
    priority: 0,
    source: "orbit",
    target: "frontend",
    event_type: "ORBIT_UPDATE",
    payload: {
      satellite_id: satelliteId,
      sim_time: simTime,
      position,
      velocity: [0, 0, 0],
      status: "online"
    }
  };
}

function taskEvent(taskId: string, status: string, simTime = 1, progress = 1): SimEvent {
  return {
    event_id: `task:${taskId}`,
    sim_time: simTime,
    priority: 0,
    source: "compute",
    target: "frontend",
    event_type: "TASK_FINISH",
    payload: {
      task_id: taskId,
      node_id: "node-a",
      sim_time: simTime,
      progress,
      status
    }
  };
}

function computeNodeEvent(
  nodeId: string,
  simTime: number,
  capacity: number,
  availableCapacity: number
): SimEvent {
  return {
    event_id: `compute:${nodeId}`,
    sim_time: simTime,
    priority: 0,
    source: "compute",
    target: "frontend",
    event_type: "COMPUTE_NODE_UPDATE",
    payload: {
      node_id: nodeId,
      sim_time: simTime,
      capacity,
      available_capacity: availableCapacity,
      status: availableCapacity < capacity ? "BUSY" : "IDLE"
    }
  };
}

function metricEvent(
  eventId: string,
  metricName: string,
  entityId: string,
  value: number,
  simTime = 1
): SimEvent {
  return {
    event_id: eventId,
    sim_time: simTime,
    priority: 0,
    source: "metrics",
    target: "frontend",
    event_type: "METRIC_SAMPLE",
    payload: {
      metric_name: metricName,
      sim_time: simTime,
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
