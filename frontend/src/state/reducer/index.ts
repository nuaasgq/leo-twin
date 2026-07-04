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

export interface ReducerDiff {
  satelliteIds: ReadonlySet<string>;
  linkIds: ReadonlySet<string>;
  taskIds: ReadonlySet<string>;
  metricIds: ReadonlySet<string>;
}

export interface ReducedWorldState {
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
  spatialCells: ReadonlyMap<string, readonly string[]>;
}

interface MutableWorldState {
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
  satelliteCellById: Map<string, string>;
  satelliteIdsByCell: Map<string, Set<string>>;
}

export interface WorldStateReducerOptions {
  eventLogLimit?: number;
  metricSeriesLimit?: number;
  spatialCellSizeMeters?: number;
}

export class WorldStateReducer {
  private readonly eventLogLimit: number;
  private readonly metricSeriesLimit: number;
  private readonly spatialCellSizeMeters: number;
  private readonly dirtySatelliteIds = new Set<string>();
  private readonly dirtyLinkIds = new Set<string>();
  private readonly dirtyTaskIds = new Set<string>();
  private readonly dirtyMetricIds = new Set<string>();
  private state = createMutableState();
  private version = 0;

  constructor(options: WorldStateReducerOptions = {}) {
    this.eventLogLimit = options.eventLogLimit ?? 4096;
    this.metricSeriesLimit = options.metricSeriesLimit ?? 240;
    this.spatialCellSizeMeters = options.spatialCellSizeMeters ?? 1_000_000;
  }

  getVersion(): number {
    return this.version;
  }

  getState(): ReducedWorldState {
    return freezeReducerState(this.state);
  }

  consumeDiff(): ReducerDiff {
    const diff = {
      satelliteIds: new Set(this.dirtySatelliteIds),
      linkIds: new Set(this.dirtyLinkIds),
      taskIds: new Set(this.dirtyTaskIds),
      metricIds: new Set(this.dirtyMetricIds)
    };
    this.dirtySatelliteIds.clear();
    this.dirtyLinkIds.clear();
    this.dirtyTaskIds.clear();
    this.dirtyMetricIds.clear();
    return diff;
  }

  applyScenarioConfig(config: ScenarioConfig): void {
    this.state.scenarioConfig = config;
    this.state.fidelitySummary = config.backend_summary?.fidelity_summary ?? null;
    for (const user of config.ground_users ?? []) {
      this.state.groundUsers.set(user.user_id, user);
    }
    this.version += 1;
  }

  applySnapshot(snapshot: StateSnapshot): void {
    if (snapshot.fidelity_summary !== undefined) {
      this.state.fidelitySummary = snapshot.fidelity_summary;
    }
    for (const satellite of snapshot.satellites ?? []) {
      if (this.upsertSatelliteIfFresh(satellite)) {
        this.state.lastSimTime = Math.max(this.state.lastSimTime, satellite.sim_time);
      }
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
      this.applyTaskIfFresh(task);
    }
    for (const node of snapshot.compute_nodes ?? []) {
      this.applyComputeNodeIfFresh(node);
    }
    for (const metric of snapshot.metrics ?? []) {
      this.applyMetric(metric);
      this.state.lastSimTime = Math.max(this.state.lastSimTime, metric.sim_time);
    }
    this.version += 1;
  }

  applyEvents(events: readonly SimEvent[]): void {
    if (events.length === 0) {
      return;
    }
    for (const event of events) {
      this.applyEvent(event);
    }
    this.version += 1;
  }

  reset(): void {
    this.state = createMutableState();
    this.dirtySatelliteIds.clear();
    this.dirtyLinkIds.clear();
    this.dirtyTaskIds.clear();
    this.dirtyMetricIds.clear();
    this.version += 1;
  }

  private applyEvent(event: SimEvent): void {
    this.state.eventCount += 1;
    this.state.lastSimTime = Math.max(this.state.lastSimTime, event.sim_time);
    this.state.eventLog.push(event);
    if (this.state.eventLog.length > this.eventLogLimit) {
      this.state.eventLog.splice(0, this.state.eventLog.length - this.eventLogLimit);
    }

    if (event.event_type === "ORBIT_UPDATE") {
      this.upsertSatelliteIfFresh(event.payload as SatelliteState);
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
      if (route.available) {
        this.state.activeRouteId = route.route_id;
      }
      return;
    }
    if (event.event_type === "TASK_START" || event.event_type === "TASK_FINISH") {
      this.applyTaskIfFresh(event.payload as TaskState);
      return;
    }
    if (event.event_type === "COMPUTE_NODE_UPDATE") {
      this.applyComputeNodeIfFresh(event.payload as ComputeNodeState);
      return;
    }
    this.applyMetric(event.payload as MetricRecord);
  }

  private upsertSatelliteIfFresh(satellite: SatelliteState): boolean {
    const previous = this.state.satellites.get(satellite.satellite_id);
    if (previous !== undefined && satellite.sim_time < previous.sim_time) {
      return false;
    }
    this.state.satellites.set(satellite.satellite_id, satellite);
    this.dirtySatelliteIds.add(satellite.satellite_id);
    this.updateSatelliteCell(satellite);
    return true;
  }

  private updateSatelliteCell(satellite: SatelliteState): void {
    const nextCell = satelliteCellId(satellite, this.spatialCellSizeMeters);
    const previousCell = this.state.satelliteCellById.get(satellite.satellite_id);
    if (previousCell === nextCell) {
      return;
    }
    if (previousCell) {
      const previousSet = this.state.satelliteIdsByCell.get(previousCell);
      previousSet?.delete(satellite.satellite_id);
      if (previousSet?.size === 0) {
        this.state.satelliteIdsByCell.delete(previousCell);
      }
    }
    let nextSet = this.state.satelliteIdsByCell.get(nextCell);
    if (!nextSet) {
      nextSet = new Set<string>();
      this.state.satelliteIdsByCell.set(nextCell, nextSet);
    }
    nextSet.add(satellite.satellite_id);
    this.state.satelliteCellById.set(satellite.satellite_id, nextCell);
  }

  private applyLink(link: LinkState): void {
    const id = linkKey(link.source_id, link.target_id);
    if (link.availability) {
      this.state.links.set(id, link);
    } else {
      this.state.links.delete(id);
    }
    this.dirtyLinkIds.add(id);
  }

  private applyTaskIfFresh(task: TaskState): boolean {
    const previous = this.state.tasks.get(task.task_id);
    if (previous !== undefined && task.sim_time < previous.sim_time) {
      return false;
    }
    this.state.tasks.set(task.task_id, task);
    this.state.lastSimTime = Math.max(this.state.lastSimTime, task.sim_time);
    this.dirtyTaskIds.add(task.task_id);
    return true;
  }

  private applyComputeNodeIfFresh(node: ComputeNodeState): boolean {
    const previous = this.state.computeNodes.get(node.node_id);
    if (previous !== undefined && node.sim_time < previous.sim_time) {
      return false;
    }
    this.state.computeNodes.set(node.node_id, node);
    this.state.lastSimTime = Math.max(this.state.lastSimTime, node.sim_time);
    return true;
  }

  private applyMetric(record: MetricRecord): void {
    const id = `${record.metric_name}:${record.entity_id}`;
    this.state.metrics.set(id, record);
    this.dirtyMetricIds.add(id);
    const series = this.state.metricSeries.get(record.metric_name) ?? [];
    series.push(record);
    if (series.length > this.metricSeriesLimit) {
      series.splice(0, series.length - this.metricSeriesLimit);
    }
    this.state.metricSeries.set(record.metric_name, series);
  }
}

function createMutableState(): MutableWorldState {
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
    activeRouteId: null,
    satelliteCellById: new Map(),
    satelliteIdsByCell: new Map()
  };
}

function freezeReducerState(state: MutableWorldState): ReducedWorldState {
  return {
    satellites: state.satellites,
    groundUsers: state.groundUsers,
    links: state.links,
    routes: state.routes,
    computeNodes: state.computeNodes,
    tasks: state.tasks,
    metrics: state.metrics,
    metricSeries: state.metricSeries,
    eventLog: state.eventLog,
    eventCount: state.eventCount,
    lastSimTime: state.lastSimTime,
    scenarioConfig: state.scenarioConfig,
    fidelitySummary: state.fidelitySummary,
    activeRouteId: state.activeRouteId,
    spatialCells: new Map(
      Array.from(state.satelliteIdsByCell.entries()).map(([cellId, satelliteIds]) => [
        cellId,
        Array.from(satelliteIds).sort()
      ])
    )
  };
}

function satelliteCellId(satellite: SatelliteState, cellSizeMeters: number): string {
  const [x, y, z] = satellite.position;
  return [
    Math.floor(x / cellSizeMeters),
    Math.floor(y / cellSizeMeters),
    Math.floor(z / cellSizeMeters)
  ].join(":");
}

function linkKey(sourceId: string, targetId: string): string {
  return `${sourceId}->${targetId}`;
}
