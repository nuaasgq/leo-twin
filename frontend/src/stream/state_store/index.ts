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

export interface ObservabilityState {
  satellites: ReadonlyMap<string, SatelliteState>;
  groundUsers: ReadonlyMap<string, GroundUserState>;
  links: ReadonlyMap<string, LinkState>;
  routes: ReadonlyMap<string, Route>;
  computeNodes: ReadonlyMap<string, ComputeNodeState>;
  tasks: ReadonlyMap<string, TaskState>;
  metrics: ReadonlyMap<string, MetricRecord>;
  metricSeries: ReadonlyMap<string, readonly MetricRecord[]>;
  eventLog: readonly SimEvent[];
  eventCount: number;
  lastSimTime: number;
  scenarioConfig: ScenarioConfig | null;
  fidelitySummary: FidelitySummary | null;
  activeRouteId: string | null;
}

export type StateListener = (state: ObservabilityState) => void;

interface MutableState {
  satellites: Map<string, SatelliteState>;
  groundUsers: Map<string, GroundUserState>;
  links: Map<string, LinkState>;
  routes: Map<string, Route>;
  computeNodes: Map<string, ComputeNodeState>;
  tasks: Map<string, TaskState>;
  metrics: Map<string, MetricRecord>;
  metricSeries: Map<string, MetricRecord[]>;
  eventLog: SimEvent[];
  eventCount: number;
  lastSimTime: number;
  scenarioConfig: ScenarioConfig | null;
  fidelitySummary: FidelitySummary | null;
  activeRouteId: string | null;
}

export interface ObservabilityStoreOptions {
  eventLogLimit?: number;
  metricSeriesLimit?: number;
}

export class ObservabilityStore {
  private readonly eventLogLimit: number;
  private readonly metricSeriesLimit: number;
  private readonly listeners = new Set<StateListener>();
  private state: MutableState;

  constructor(options: ObservabilityStoreOptions = {}) {
    this.eventLogLimit = options.eventLogLimit ?? 2000;
    this.metricSeriesLimit = options.metricSeriesLimit ?? 300;
    this.state = createEmptyState();
  }

  getSnapshot(): ObservabilityState {
    return freezeState(this.state);
  }

  subscribe(listener: StateListener): () => void {
    this.listeners.add(listener);
    listener(this.getSnapshot());
    return () => {
      this.listeners.delete(listener);
    };
  }

  applyScenarioConfig(config: ScenarioConfig): void {
    this.state.scenarioConfig = config;
    this.state.fidelitySummary = config.backend_summary?.fidelity_summary ?? null;
    for (const user of config.ground_users ?? []) {
      this.state.groundUsers.set(user.user_id, user);
    }
    this.publish();
  }

  applySnapshot(snapshot: StateSnapshot): void {
    if (snapshot.fidelity_summary !== undefined) {
      this.state.fidelitySummary = snapshot.fidelity_summary;
    }
    for (const satellite of snapshot.satellites ?? []) {
      this.state.satellites.set(satellite.satellite_id, satellite);
      this.state.lastSimTime = Math.max(this.state.lastSimTime, satellite.sim_time);
    }
    for (const user of snapshot.ground_users ?? []) {
      this.state.groundUsers.set(user.user_id, user);
    }
    for (const link of snapshot.links ?? []) {
      this.applyLink(link);
    }
    for (const route of snapshot.routes ?? []) {
      this.state.routes.set(route.route_id, route);
      if (route.available) {
        this.state.activeRouteId = route.route_id;
      }
    }
    for (const task of snapshot.tasks ?? []) {
      this.state.tasks.set(task.task_id, task);
      this.state.lastSimTime = Math.max(this.state.lastSimTime, task.sim_time);
    }
    for (const node of snapshot.compute_nodes ?? []) {
      this.state.computeNodes.set(node.node_id, node);
      this.state.lastSimTime = Math.max(this.state.lastSimTime, node.sim_time);
    }
    for (const metric of snapshot.metrics ?? []) {
      this.applyMetric(metric);
      this.state.lastSimTime = Math.max(this.state.lastSimTime, metric.sim_time);
    }
    this.publish();
  }

  applyEvents(events: readonly SimEvent[]): void {
    if (events.length === 0) {
      return;
    }
    for (const event of events) {
      this.applyEventInternal(event);
    }
    this.publish();
  }

  applyEvent(event: SimEvent): void {
    this.applyEvents([event]);
  }

  reset(): void {
    this.state = createEmptyState();
    this.publish();
  }

  private applyEventInternal(event: SimEvent): void {
    this.state.eventCount += 1;
    this.state.lastSimTime = Math.max(this.state.lastSimTime, event.sim_time);
    this.state.eventLog.push(event);
    if (this.state.eventLog.length > this.eventLogLimit) {
      this.state.eventLog.splice(0, this.state.eventLog.length - this.eventLogLimit);
    }

    if (event.event_type === "ORBIT_UPDATE") {
      const satellite = event.payload as SatelliteState;
      this.state.satellites.set(satellite.satellite_id, satellite);
      return;
    }
    if (
      event.event_type === "LINK_UPDATE" ||
      event.event_type === "ACCESS_START" ||
      event.event_type === "ACCESS_END"
    ) {
      this.applyLink(event.payload as LinkState);
      return;
    }
    if (event.event_type === "ROUTE_UPDATE") {
      const route = event.payload as Route;
      this.state.routes.set(route.route_id, route);
      this.state.activeRouteId = route.available ? route.route_id : this.state.activeRouteId;
      return;
    }
    if (event.event_type === "TASK_START" || event.event_type === "TASK_FINISH") {
      const task = event.payload as TaskState;
      this.state.tasks.set(task.task_id, task);
      return;
    }
    if (event.event_type === "COMPUTE_NODE_UPDATE") {
      const node = event.payload as ComputeNodeState;
      this.state.computeNodes.set(node.node_id, node);
      return;
    }
    this.applyMetric(event.payload as MetricRecord);
  }

  private applyLink(link: LinkState): void {
    const linkId = linkKey(link.source_id, link.target_id);
    if (link.availability) {
      this.state.links.set(linkId, link);
    } else {
      this.state.links.delete(linkId);
    }
  }

  private applyMetric(record: MetricRecord): void {
    const metricId = `${record.metric_name}:${record.entity_id}`;
    this.state.metrics.set(metricId, record);
    const series = this.state.metricSeries.get(record.metric_name) ?? [];
    series.push(record);
    if (series.length > this.metricSeriesLimit) {
      series.splice(0, series.length - this.metricSeriesLimit);
    }
    this.state.metricSeries.set(record.metric_name, series);
  }

  private publish(): void {
    const snapshot = this.getSnapshot();
    for (const listener of Array.from(this.listeners)) {
      listener(snapshot);
    }
  }
}

export function linkKey(sourceId: string, targetId: string): string {
  return `${sourceId}->${targetId}`;
}

export function selectNetworkKpis(state: ObservabilityState): {
  latency: number;
  throughput: number;
  linkUtilization: number;
} {
  const links = Array.from(state.links.values());
  const latency =
    links.length === 0 ? 0 : links.reduce((total, link) => total + link.latency, 0) / links.length;
  const throughput = links.reduce((total, link) => total + link.capacity, 0);
  const utilization =
    links.length === 0
      ? 0
      : links.reduce((total, link) => total + (link.utilization ?? 0), 0) / links.length;
  return { latency, throughput, linkUtilization: utilization };
}

export function selectComputeKpis(state: ObservabilityState): {
  taskQueueLength: number;
  executionSuccessRate: number;
} {
  const tasks = Array.from(state.tasks.values());
  const finished = tasks.filter((task) => task.status.toLowerCase() === "finished");
  const failed = tasks.filter((task) => task.status.toLowerCase() === "failed");
  const running = tasks.filter((task) => task.status.toLowerCase() !== "finished");
  const completedTotal = finished.length + failed.length;
  return {
    taskQueueLength: running.length,
    executionSuccessRate: completedTotal === 0 ? 1 : finished.length / completedTotal
  };
}

export function selectOrbitKpis(state: ObservabilityState): {
  activeSatellites: number;
  coverageRatio: number;
} {
  const satellites = Array.from(state.satellites.values());
  const active = satellites.filter((satellite) => satellite.status.toLowerCase() !== "offline");
  const configuredUsers = state.groundUsers.size;
  const linkedUsers = new Set(Array.from(state.links.values()).map((link) => link.target_id));
  return {
    activeSatellites: active.length,
    coverageRatio: configuredUsers === 0 ? 0 : linkedUsers.size / configuredUsers
  };
}

export function selectSystemHealth(state: ObservabilityState): {
  eventRate: number;
  systemLoad: number;
} {
  const eventRate =
    state.lastSimTime <= 0 ? state.eventCount : state.eventCount / Math.max(state.lastSimTime, 1);
  const load = Array.from(state.metrics.values()).find((metric) => metric.metric_name === "system.load");
  return {
    eventRate,
    systemLoad: typeof load?.value === "number" ? load.value : 0
  };
}

function createEmptyState(): MutableState {
  return {
    satellites: new Map(),
    groundUsers: new Map(),
    links: new Map(),
    routes: new Map(),
    computeNodes: new Map(),
    tasks: new Map(),
    metrics: new Map(),
    metricSeries: new Map(),
    eventLog: [],
    eventCount: 0,
    lastSimTime: 0,
    scenarioConfig: null,
    fidelitySummary: null,
    activeRouteId: null
  };
}

function freezeState(state: MutableState): ObservabilityState {
  return {
    satellites: new Map(state.satellites),
    groundUsers: new Map(state.groundUsers),
    links: new Map(state.links),
    routes: new Map(state.routes),
    computeNodes: new Map(state.computeNodes),
    tasks: new Map(state.tasks),
    metrics: new Map(state.metrics),
    metricSeries: new Map(
      Array.from(state.metricSeries.entries()).map(([name, records]) => [name, [...records]])
    ),
    eventLog: [...state.eventLog],
    eventCount: state.eventCount,
    lastSimTime: state.lastSimTime,
    scenarioConfig: state.scenarioConfig,
    fidelitySummary: state.fidelitySummary,
    activeRouteId: state.activeRouteId
  };
}
