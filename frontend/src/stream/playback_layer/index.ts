import { SimEvent } from "../../core/event_types";

export interface PlaybackClock {
  now(): number;
  setTimeout(handler: () => void, delayMs: number): ReturnType<typeof setTimeout>;
  clearTimeout(timer: ReturnType<typeof setTimeout>): void;
}

export interface EventPlaybackLayerOptions {
  speedFactor?: number;
  maxEventsPerFrame?: number;
  clock?: PlaybackClock;
}

export class EventPlaybackLayer {
  private readonly speedFactor: number;
  private readonly maxEventsPerFrame: number;
  private readonly clock: PlaybackClock;
  private readonly queue: SimEvent[] = [];
  private timer: ReturnType<typeof setTimeout> | null = null;
  private baseSimTime: number | null = null;
  private baseWallTimeMs: number | null = null;

  constructor(
    private readonly sink: (events: readonly SimEvent[]) => void,
    options: EventPlaybackLayerOptions = {}
  ) {
    const speedFactor = options.speedFactor ?? 1;
    this.speedFactor = Number.isFinite(speedFactor) && speedFactor > 0 ? speedFactor : 1;
    this.maxEventsPerFrame = options.maxEventsPerFrame ?? 10_000;
    this.clock =
      options.clock ?? {
        now: () => Date.now(),
        setTimeout: (handler, delayMs) => globalThis.setTimeout(handler, delayMs),
        clearTimeout: (timer) => globalThis.clearTimeout(timer)
      };
  }

  pushEvents(events: readonly SimEvent[]): void {
    if (events.length === 0) {
      return;
    }
    this.queue.push(...events);
    this.queue.sort(compareEvent);
    if (this.baseSimTime === null || this.baseWallTimeMs === null) {
      this.baseSimTime = this.queue[0].sim_time;
      this.baseWallTimeMs = this.clock.now();
    }
    this.flushDueEvents();
    this.scheduleNextFrame();
  }

  close(): void {
    if (this.timer !== null) {
      this.clock.clearTimeout(this.timer);
      this.timer = null;
    }
    this.queue.splice(0, this.queue.length);
    this.baseSimTime = null;
    this.baseWallTimeMs = null;
  }

  pendingCount(): number {
    return this.queue.length;
  }

  private flushDueEvents(): void {
    if (this.baseSimTime === null || this.baseWallTimeMs === null || this.queue.length === 0) {
      return;
    }
    const dueSimTime =
      this.baseSimTime + ((this.clock.now() - this.baseWallTimeMs) / 1000) * this.speedFactor;
    const dueEvents: SimEvent[] = [];
    while (
      this.queue.length > 0 &&
      this.queue[0].sim_time <= dueSimTime &&
      dueEvents.length < this.maxEventsPerFrame
    ) {
      const event = this.queue.shift();
      if (event) {
        dueEvents.push(event);
      }
    }
    if (dueEvents.length > 0) {
      this.sink(dueEvents);
    }
  }

  private scheduleNextFrame(): void {
    if (this.timer !== null || this.queue.length === 0) {
      return;
    }
    if (this.baseSimTime === null || this.baseWallTimeMs === null) {
      return;
    }
    const nextEvent = this.queue[0];
    const targetWallTimeMs =
      this.baseWallTimeMs + ((nextEvent.sim_time - this.baseSimTime) / this.speedFactor) * 1000;
    const delayMs = Math.max(0, Math.round(targetWallTimeMs - this.clock.now()));
    this.timer = this.clock.setTimeout(() => {
      this.timer = null;
      this.flushDueEvents();
      this.scheduleNextFrame();
    }, delayMs);
  }
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
