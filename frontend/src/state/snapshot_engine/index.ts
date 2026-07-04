import { useSyncExternalStore } from "react";

import {
  ComputeNodeState,
  FidelitySummary,
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
  kpiSeries?: readonly NetworkKpiSample[];
  topology?: TopologyChangeSummary;
}

export interface NetworkKpiSample {
  simTime: number;
  throughputMbps: number;
  latencyMs: number;
  lossPercent: number;
  jitterMs: number;
}

export interface TopologyChangeSummary {
  activeSpaceLinks: number;
  activeAccessLinks: number;
  linkUpdateEvents: number;
  accessStartEvents: number;
  accessEndEvents: number;
  routeUpdateEvents: number;
  topologyEvents: number;
}

export interface ComputeMetricsSummary {
  taskQueueLength: number;
  executionSuccessRate: number;
  runningTasks: number;
  finishedTasks: number;
  deadlineMissedTasks: number;
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
  capacity: number;
  available_capacity: number;
  status: string;
  load_ratio: number;
  cpu_gflops_fp64?: number;
  gpu_tflops_fp32?: number;
  gpu_tflops_fp16?: number;
  npu_tops_int8?: number;
  memory_gb?: number;
  storage_gb?: number;
  resource_usage_mode?: string;
  available_cpu_gflops_fp32?: number;
  used_cpu_gflops_fp32?: number;
  available_cpu_gflops_fp64?: number;
  used_cpu_gflops_fp64?: number;
  available_gpu_tflops_fp32?: number;
  used_gpu_tflops_fp32?: number;
  available_gpu_tflops_fp16?: number;
  used_gpu_tflops_fp16?: number;
  available_npu_tops_int8?: number;
  used_npu_tops_int8?: number;
  available_memory_gb?: number;
  used_memory_gb?: number;
  available_storage_gb?: number;
  used_storage_gb?: number;
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
  metrics: readonly MetricRecord[];
  metrics_summary: MetricsSummary;
  scenario_config: ScenarioConfig | null;
  fidelity_summary: FidelitySummary | null;
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
    this.setIntervalFn =
      options.setIntervalFn ??
      ((handler, intervalMs) => globalThis.setInterval(handler, intervalMs));
    this.clearIntervalFn = options.clearIntervalFn ?? ((timer) => globalThis.clearInterval(timer));
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
  const activeTasks = tasks.filter((task) => !isTerminalTaskStatus(task.status));
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
    compute_nodes: computeNodeSummary(state.computeNodes, tasks),
    ground_users: Array.from(state.groundUsers.values()).sort((left, right) =>
      left.user_id.localeCompare(right.user_id)
    ),
    active_tasks: activeTasks,
    metrics,
    metrics_summary: {
      network: networkSummary(links, state.eventLog, state.metricSeries),
      compute: computeSummary(tasks),
      orbit: orbitSummary(satellites, state.groundUsers.size, links),
      system: systemSummary(state, metrics)
    },
    scenario_config: state.scenarioConfig,
    fidelity_summary: state.fidelitySummary,
    active_route_id: state.activeRouteId,
    spatial_index: state.spatialCells,
    indexes: {
      satellites: state.satellites,
      ground_users: state.groundUsers
    },
    diff
  };
}

function networkSummary(
  links: readonly LinkState[],
  eventLog: readonly SimEvent[],
  metricSeries: ReadonlyMap<string, readonly MetricRecord[]>
): NetworkMetricsSummary {
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
    })),
    kpiSeries: networkKpiSeries(metricSeries),
    topology: topologyChangeSummary(links, eventLog)
  };
}

function networkKpiSeries(
  metricSeries: ReadonlyMap<string, readonly MetricRecord[]>
): readonly NetworkKpiSample[] {
  type DraftSample = Partial<NetworkKpiSample> & { simTime: number };
  const samples = new Map<number, DraftSample>();

  function add(metricName: string, assign: (sample: DraftSample, value: number) => void): void {
    for (const record of metricSeries.get(metricName) ?? []) {
      const value = metricRecordNumber(record);
      if (value === undefined) {
        continue;
      }
      const sample = samples.get(record.sim_time) ?? { simTime: record.sim_time };
      assign(sample, value);
      samples.set(record.sim_time, sample);
    }
  }

  add("network.quality.effective_throughput_mbps", (sample, value) => {
    sample.throughputMbps = value;
  });
  add("network.quality.effective_latency_s", (sample, value) => {
    sample.latencyMs = value * 1000;
  });
  add("network.quality.effective_loss_proxy_rate", (sample, value) => {
    sample.lossPercent = value * 100;
  });
  add("network.quality.effective_delay_variation_s", (sample, value) => {
    sample.jitterMs = value * 1000;
  });

  return Array.from(samples.values())
    .filter(
      (sample): sample is NetworkKpiSample =>
        sample.throughputMbps !== undefined &&
        sample.latencyMs !== undefined &&
        sample.lossPercent !== undefined &&
        sample.jitterMs !== undefined
    )
    .sort((left, right) => left.simTime - right.simTime)
    .slice(-24);
}

function topologyChangeSummary(
  links: readonly LinkState[],
  eventLog: readonly SimEvent[]
): TopologyChangeSummary {
  const eventCounts = eventLog.reduce(
    (counts, event) => {
      if (event.event_type === "LINK_UPDATE") {
        counts.linkUpdateEvents += 1;
      } else if (event.event_type === "ACCESS_START") {
        counts.accessStartEvents += 1;
      } else if (event.event_type === "ACCESS_END") {
        counts.accessEndEvents += 1;
      } else if (event.event_type === "ROUTE_UPDATE") {
        counts.routeUpdateEvents += 1;
      }
      return counts;
    },
    {
      linkUpdateEvents: 0,
      accessStartEvents: 0,
      accessEndEvents: 0,
      routeUpdateEvents: 0
    }
  );
  return {
    activeSpaceLinks: links.filter(isSpaceLink).length,
    activeAccessLinks: links.filter(isAccessLink).length,
    ...eventCounts,
    topologyEvents:
      eventCounts.linkUpdateEvents +
      eventCounts.accessStartEvents +
      eventCounts.accessEndEvents +
      eventCounts.routeUpdateEvents
  };
}

function isSpaceLink(link: LinkState): boolean {
  return isSatelliteEndpoint(link.source_id) && isSatelliteEndpoint(link.target_id);
}

function isAccessLink(link: LinkState): boolean {
  return isSatelliteEndpoint(link.source_id) !== isSatelliteEndpoint(link.target_id);
}

function isSatelliteEndpoint(endpointId: string): boolean {
  return endpointId.toLowerCase().startsWith("sat-");
}

function computeSummary(tasks: readonly TaskState[]): ComputeMetricsSummary {
  const finished = tasks.filter((task) => normalizeStatus(task.status) === "finished").length;
  const failed = tasks.filter((task) => normalizeStatus(task.status) === "failed").length;
  const deadlineMissed = tasks.filter(
    (task) => normalizeStatus(task.status) === "deadline_missed"
  ).length;
  const running = tasks.length - finished - failed - deadlineMissed;
  const completedTotal = finished + failed + deadlineMissed;
  return {
    taskQueueLength: running,
    executionSuccessRate: completedTotal === 0 ? 1 : finished / completedTotal,
    runningTasks: running,
    finishedTasks: finished,
    deadlineMissedTasks: deadlineMissed
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

function computeNodeSummary(
  computeNodes: ReadonlyMap<string, ComputeNodeState>,
  tasks: readonly TaskState[]
): readonly ComputeNodeRenderState[] {
  const nodes = new Map<string, { running_tasks: number; finished_tasks: number }>();
  for (const task of tasks) {
    const entry = nodes.get(task.node_id) ?? { running_tasks: 0, finished_tasks: 0 };
    if (isTerminalTaskStatus(task.status)) {
      entry.finished_tasks += 1;
    } else {
      entry.running_tasks += 1;
    }
    nodes.set(task.node_id, entry);
  }
  for (const node of computeNodes.values()) {
    if (!nodes.has(node.node_id)) {
      nodes.set(node.node_id, { running_tasks: 0, finished_tasks: 0 });
    }
  }
  return Array.from(nodes.entries())
    .sort(([left], [right]) => left.localeCompare(right))
    .map(([node_id, entry]) => {
      const node = computeNodes.get(node_id);
      return {
        node_id,
        ...entry,
        capacity: node?.capacity ?? 0,
        available_capacity: node?.available_capacity ?? 0,
        status: node?.status ?? "UNKNOWN",
        load_ratio: computeLoadRatio(node),
        ...computeResourceVectorFields(node)
      };
    });
}

function computeResourceVectorFields(
  node: ComputeNodeState | undefined
): Partial<ComputeNodeRenderState> {
  if (!node) {
    return {};
  }
  return {
    ...(node.cpu_gflops_fp64 === undefined
      ? {}
      : { cpu_gflops_fp64: node.cpu_gflops_fp64 }),
    ...(node.gpu_tflops_fp32 === undefined
      ? {}
      : { gpu_tflops_fp32: node.gpu_tflops_fp32 }),
    ...(node.gpu_tflops_fp16 === undefined
      ? {}
      : { gpu_tflops_fp16: node.gpu_tflops_fp16 }),
    ...(node.npu_tops_int8 === undefined ? {} : { npu_tops_int8: node.npu_tops_int8 }),
    ...(node.memory_gb === undefined ? {} : { memory_gb: node.memory_gb }),
    ...(node.storage_gb === undefined ? {} : { storage_gb: node.storage_gb }),
    ...(node.resource_usage_mode === undefined
      ? {}
      : { resource_usage_mode: node.resource_usage_mode }),
    ...optionalRenderNumber(node, "available_cpu_gflops_fp32"),
    ...optionalRenderNumber(node, "used_cpu_gflops_fp32"),
    ...optionalRenderNumber(node, "available_cpu_gflops_fp64"),
    ...optionalRenderNumber(node, "used_cpu_gflops_fp64"),
    ...optionalRenderNumber(node, "available_gpu_tflops_fp32"),
    ...optionalRenderNumber(node, "used_gpu_tflops_fp32"),
    ...optionalRenderNumber(node, "available_gpu_tflops_fp16"),
    ...optionalRenderNumber(node, "used_gpu_tflops_fp16"),
    ...optionalRenderNumber(node, "available_npu_tops_int8"),
    ...optionalRenderNumber(node, "used_npu_tops_int8"),
    ...optionalRenderNumber(node, "available_memory_gb"),
    ...optionalRenderNumber(node, "used_memory_gb"),
    ...optionalRenderNumber(node, "available_storage_gb"),
    ...optionalRenderNumber(node, "used_storage_gb")
  };
}

function optionalRenderNumber(
  node: ComputeNodeState,
  field: keyof ComputeNodeState
): Partial<ComputeNodeRenderState> {
  const value = node[field];
  return typeof value === "number" ? { [field]: value } : {};
}

function metricRecordNumber(record: MetricRecord): number | undefined {
  return typeof record.value === "number" && Number.isFinite(record.value)
    ? record.value
    : undefined;
}

function computeLoadRatio(node: ComputeNodeState | undefined): number {
  if (!node) {
    return 0;
  }
  if (node.load_ratio !== undefined) {
    return clampRatio(node.load_ratio);
  }
  if (node.capacity <= 0) {
    return 1;
  }
  return clampRatio(1 - node.available_capacity / node.capacity);
}

function clampRatio(value: number): number {
  if (!Number.isFinite(value)) {
    return 0;
  }
  return Math.max(0, Math.min(1, value));
}

function isTerminalTaskStatus(status: string): boolean {
  return ["deadline_missed", "failed", "finished"].includes(normalizeStatus(status));
}

function normalizeStatus(status: string): string {
  return status.toLowerCase();
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
