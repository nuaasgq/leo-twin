import { LinkState, MetricRecord, SatelliteState, SimEvent, TaskState } from "../../core/event_types";

export interface EventThrottleLayerOptions {
  flushIntervalMs?: number;
  maxEventsPerFlush?: number;
  dropRedundantUpdates?: boolean;
}

export class EventThrottleLayer {
  private readonly flushIntervalMs: number;
  private readonly maxEventsPerFlush: number;
  private readonly dropRedundantUpdates: boolean;
  private readonly orderedEvents: SimEvent[] = [];
  private readonly foldedEvents = new Map<string, SimEvent>();
  private timer: ReturnType<typeof setTimeout> | null = null;

  constructor(
    private readonly sink: (events: readonly SimEvent[]) => void,
    options: EventThrottleLayerOptions = {}
  ) {
    this.flushIntervalMs = options.flushIntervalMs ?? 20;
    this.maxEventsPerFlush = options.maxEventsPerFlush ?? 10_000;
    this.dropRedundantUpdates = options.dropRedundantUpdates ?? true;
  }

  pushEvents(events: readonly SimEvent[]): void {
    for (const event of events) {
      const key = this.dropRedundantUpdates ? foldKey(event) : null;
      if (key) {
        this.foldedEvents.set(key, event);
      } else {
        this.orderedEvents.push(event);
      }
    }
    this.scheduleFlush();
  }

  flush(): void {
    if (this.timer !== null) {
      clearTimeout(this.timer);
      this.timer = null;
    }
    const events = this.drain();
    if (events.length > 0) {
      this.sink(events);
    }
  }

  close(): void {
    this.flush();
    if (this.timer !== null) {
      clearTimeout(this.timer);
    }
    this.timer = null;
    this.orderedEvents.splice(0, this.orderedEvents.length);
    this.foldedEvents.clear();
  }

  pendingCount(): number {
    return this.orderedEvents.length + this.foldedEvents.size;
  }

  private scheduleFlush(): void {
    if (this.timer !== null) {
      return;
    }
    this.timer = setTimeout(() => this.flush(), this.flushIntervalMs);
  }

  private drain(): readonly SimEvent[] {
    if (this.orderedEvents.length === 0 && this.foldedEvents.size === 0) {
      return [];
    }
    const folded = Array.from(this.foldedEvents.values()).sort(compareEvent);
    const ordered = this.orderedEvents.splice(0, this.orderedEvents.length);
    this.foldedEvents.clear();
    const drained = [...ordered, ...folded].sort(compareEvent);
    if (drained.length <= this.maxEventsPerFlush) {
      return drained;
    }
    return drained.slice(drained.length - this.maxEventsPerFlush);
  }
}

function foldKey(event: SimEvent): string | null {
  if (event.event_type === "ORBIT_UPDATE") {
    const satellite = event.payload as SatelliteState;
    return `orbit:${satellite.satellite_id}`;
  }
  if (event.event_type === "LINK_UPDATE") {
    const link = event.payload as LinkState;
    return `link:${link.source_id}->${link.target_id}`;
  }
  if (event.event_type === "TASK_START" || event.event_type === "TASK_FINISH") {
    const task = event.payload as TaskState;
    return `task:${task.task_id}`;
  }
  if (event.event_type === "METRIC_SAMPLE") {
    const metric = event.payload as MetricRecord;
    return `metric:${metric.metric_name}:${metric.entity_id}`;
  }
  return null;
}

function compareEvent(left: SimEvent, right: SimEvent): number {
  if (left.sim_time !== right.sim_time) {
    return left.sim_time - right.sim_time;
  }
  if (left.priority !== right.priority) {
    return right.priority - left.priority;
  }
  return String(left.event_id).localeCompare(String(right.event_id));
}
