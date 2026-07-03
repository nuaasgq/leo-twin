import { useSyncExternalStore } from "react";

import {
  GroundUserState,
  LinkState,
  MetricRecord,
  Route,
  SatelliteState,
  ScenarioConfig,
  SimEvent,
  StateSnapshot,
  TaskState
} from "../../core/event_types";
import { ReducedWorldState, WorldStateReducer } from "../reducer";

export interface NetworkMetricsSummary {
  latency: number;
  throughput: number;
  linkUtilization: number;
  series: readonly { id: string; latency: number; capacity: number }[];
}

export interface ComputeMetricsSummary {
  taskQueueLength: number;
  executionSuccessRate: number;
  runningTasks: number;
  finishedTasks: number;
}

export interface OrbitMetricsSummary {
  activeSatellites: number;
  coverageRatio: number;
  series: readonly { index: number; active: number }[];
}

export interface SystemHealthSummary {
  eventRate: number;
  systemLoad: number;
  eventSeries: readonly { index: number; simTime: number }[];
}

export interface MetricsSummary {
  network: NetworkMetricsSummary;
  compute: ComputeMetricsSummary;
  orbit: OrbitMetricsSummary;
  system: SystemHealthSummary;
}

export interface ComputeNodeRenderState {
  node_id: string;
  running_tasks: number;
  finished_tasks: number;
}

export interface SnapshotDiff {
  satellite_ids: readonly string[];
  link_ids: readonly string[];
  task_ids: readonly string[];
  metric_ids: readonly string[];
}

export interface WorldSnapshot {
  timestamp: number;
  reducer_version: number;
  last_sim_time: number;
  event_count: number;
  satellites: readonly SatelliteState[];
  links: readonly LinkState[];
  routes: readonly Route[];
  compute_nodes: readonly ComputeNodeRenderState[];
  ground_users: readonly GroundUserState[];
  active_tasks: readonly TaskState[];
  metrics_summary: MetricsSummary;
  scenario_config: ScenarioConfig | null;
  active_route_id: string | null;
  spatial_index: ReadonlyMap<string, readonly string[]>;
  indexes: {
    satellites: ReadonlyMap<string, SatelliteState>;
    ground_users: ReadonlyMap<string, GroundUserState>;
  };
  diff: SnapshotDiff;
}

export interface SnapshotEngineOptions {
  snapshotHz?: number;
  clock?: () => number;
  setIntervalFn?: (handler: () => void, intervalMs: number) => ReturnType<typeof setInterval>;
  clearIntervalFn?: (timer: ReturnType<typeof setInterval>) => void;
}

export type SnapshotListener = (snapshot: WorldSnapshot) => void;

export class SnapshotEngine {
  private readonly snapshotIntervalMs: number;
  private readonly clock: () => number;
  private readonly setIntervalFn: NonNullable<SnapshotEngineOptions["setIntervalFn"]>;
  private readonly clearIntervalFn: NonNullable<SnapshotEngineOptions["clearIntervalFn"]>;
  private readonly listeners = new Set<SnapshotListener>();
  private timer: ReturnType<typeof setInterval> | null = null;
  private lastPublishedVersion = -1;
  private snapshot: WorldSnapshot;

  constructor(
    private readonly reducer: WorldStateReducer,
    options: SnapshotEngineOptions = {}
  ) {
    const snapshotHz = options.snapshotHz ?? 20;
    if (!Number.isFinite(snapshotHz) || snapshotHz <= 0 || snapshotHz > 60) {
      throw new RangeError("snapshotHz must be in the range (0, 60]");
    }
    this.snapshotIntervalMs = Math.round(1000 / snapshotHz);
    this.clock = options.clock ?? (() => Date.now());
    this.setIntervalFn = options.setIntervalFn ?? setInterval;
    this.clearIntervalFn = options.clearIntervalFn ?? clearInterval;
    this.snapshot = buildWorldSnapshot(
      reducer.getState(),
      reducer.getVersion(),
      this.clock(),
      emptyDiff()
    );
  }

  start(): void {
    if (this.timer !== null) {
      return;
    }
    this.timer = this.setIntervalFn(() => this.publishIfChanged(), this.snapshotIntervalMs);
  }

  stop(): void {
    if (this.timer !== null) {
      this.clearIntervalFn(this.timer);
    }
    this.timer = null;
  }

  subscribe(listener: SnapshotListener): () => void {
    this.listeners.add(listener);
    return () => {
      this.listeners.delete(listener);
    };
  }

  getSnapshot(): WorldSnapshot {
    return this.snapshot;
  }

  applyScenarioConfig(config: ScenarioConfig): void {
    this.reducer.applyScenarioConfig(config);
  }

  applySnapshot(snapshot: StateSnapshot): void {
    this.reducer.applySnapshot(snapshot);
  }

  applyEvents(events: readonly SimEvent[]): void {
    this.reducer.applyEvents(events);
  }

  publishNow(): WorldSnapshot {
    const diff = this.reducer.consumeDiff();
    this.snapshot = buildWorldSnapshot(
      this.reducer.getState(),
      this.reducer.getVersion(),
      this.clock(),
      {
        satellite_ids: Array.from(diff.satelliteIds).sort(),
        link_ids: Array.from(diff.linkIds).sort(),
        task_ids: Array.from(diff.taskIds).sort(),
        metric_ids: Array.from(diff.metricIds).sort()
      }
    );
    this.lastPublishedVersion = this.reducer.getVersion();
    for (const listener of Array.from(this.listeners)) {
      listener(this.snapshot);
    }
    return this.snapshot;
  }

  publishIfChanged(): WorldSnapshot {
    if (this.reducer.getVersion() === this.lastPublishedVersion) {
      return this.snapshot;
    }
    return this.publishNow();
  }
}

export function useWorldSnapshot(engine: SnapshotEngine): WorldSnapshot {
  return useSyncExternalStore(
    (listener) => engine.subscribe(listener),
    () => engine.getSnapshot(),
    () => engine.getSnapshot()
  );
}

export function buildWorldSnapshot(
  state: ReducedWorldState,
  reducerVersion: number,
  timestamp: number,
  diff: SnapshotDiff
): WorldSnapshot {
  const satellites = Array.from(state.satellites.values()).sort(compareSatellite);
  const links = Array.from(state.links.values()).sort(compareLink);
  const tasks = Array.from(state.tasks.values()).sort(compareTask);
  const metrics = Array.from(state.metrics.values()).sort(compareMetric);
  const activeTasks = tasks.filter((task) => task.status.toLowerCase() !== "finished");
  const routes = Array.from(state.routes.values()).sort((left, right) =>
    left.route_id.localeCompare(right.route_id)
  );

  return {
    timestamp,
    reducer_version: reducerVersion,
    last_sim_time: state.lastSimTime,
    event_count: state.eventCount,
    satellites,
    links,
    routes,
    compute_nodes: computeNodeSummary(tasks),
    ground_users: Array.from(state.groundUsers.values()).sort((left, right) =>
      left.user_id.localeCompare(right.user_id)
    ),
    active_tasks: activeTasks,
    metrics_summary: {
      network: networkSummary(links),
      compute: computeSummary(tasks),
      orbit: orbitSummary(satellites, state.groundUsers.size, links),
      system: systemSummary(state, metrics)
    },
    scenario_config: state.scenarioConfig,
    active_route_id: state.activeRouteId,
    spatial_index: state.spatialCells,
    indexes: {
      satellites: state.satellites,
      ground_users: state.groundUsers
    },
    diff
  };
}

function networkSummary(links: readonly LinkState[]): NetworkMetricsSummary {
  const latency =
    links.length === 0 ? 0 : links.reduce((total, link) => total + link.latency, 0) / links.length;
  const throughput = links.reduce((total, link) => total + link.capacity, 0);
  const utilization =
    links.length === 0
      ? 0
      : links.reduce((total, link) => total + (link.utilization ?? 0), 0) / links.length;
  return {
    latency,
    throughput,
    linkUtilization: utilization,
    series: links.slice(0, 24).map((link) => ({
      id: `${link.source_id}->${link.target_id}`,
      latency: link.latency,
      capacity: link.capacity
    }))
  };
}

function computeSummary(tasks: readonly TaskState[]): ComputeMetricsSummary {
  const finished = tasks.filter((task) => task.status.toLowerCase() === "finished").length;
  const failed = tasks.filter((task) => task.status.toLowerCase() === "failed").length;
  const running = tasks.length - finished;
  const completedTotal = finished + failed;
  return {
    taskQueueLength: running,
    executionSuccessRate: completedTotal === 0 ? 1 : finished / completedTotal,
    runningTasks: running,
    finishedTasks: finished
  };
}

function orbitSummary(
  satellites: readonly SatelliteState[],
  groundUserCount: number,
  links: readonly LinkState[]
): OrbitMetricsSummary {
  const active = satellites.filter((satellite) => satellite.status.toLowerCase() !== "offline");
  const linkedUsers = new Set(links.map((link) => link.target_id));
  return {
    activeSatellites: active.length,
    coverageRatio: groundUserCount === 0 ? 0 : linkedUsers.size / groundUserCount,
    series: satellites.slice(0, 64).map((satellite, index) => ({
      index,
      active: satellite.status.toLowerCase() === "offline" ? 0 : 1
    }))
  };
}

function systemSummary(
  state: ReducedWorldState,
  metrics: readonly MetricRecord[]
): SystemHealthSummary {
  const load = metrics.find((metric) => metric.metric_name === "system.load");
  return {
    eventRate:
      state.lastSimTime <= 0 ? state.eventCount : state.eventCount / Math.max(state.lastSimTime, 1),
    systemLoad: typeof load?.value === "number" ? load.value : 0,
    eventSeries: state.eventLog.slice(-80).map((event, index) => ({
      index,
      simTime: event.sim_time
    }))
  };
}

function computeNodeSummary(tasks: readonly TaskState[]): readonly ComputeNodeRenderState[] {
  const nodes = new Map<string, { running_tasks: number; finished_tasks: number }>();
  for (const task of tasks) {
    const entry = nodes.get(task.node_id) ?? { running_tasks: 0, finished_tasks: 0 };
    if (task.status.toLowerCase() === "finished") {
      entry.finished_tasks += 1;
    } else {
      entry.running_tasks += 1;
    }
    nodes.set(task.node_id, entry);
  }
  return Array.from(nodes.entries())
    .sort(([left], [right]) => left.localeCompare(right))
    .map(([node_id, entry]) => ({ node_id, ...entry }));
}

function compareSatellite(left: SatelliteState, right: SatelliteState): number {
  return left.satellite_id.localeCompare(right.satellite_id);
}

function compareLink(left: LinkState, right: LinkState): number {
  return `${left.source_id}->${left.target_id}`.localeCompare(`${right.source_id}->${right.target_id}`);
}

function compareTask(left: TaskState, right: TaskState): number {
  return left.task_id.localeCompare(right.task_id);
}

function compareMetric(left: MetricRecord, right: MetricRecord): number {
  return `${left.metric_name}:${left.entity_id}`.localeCompare(
    `${right.metric_name}:${right.entity_id}`
  );
}

function emptyDiff(): SnapshotDiff {
  return {
    satellite_ids: [],
    link_ids: [],
    task_ids: [],
    metric_ids: []
  };
}
