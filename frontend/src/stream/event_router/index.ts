import { decodeSimEventBatch, decodeStateSnapshot } from "../../core/decoder";
import { SimEvent, StateSnapshot } from "../../core/event_types";
import { EventThrottleLayer } from "../throttle_layer";

export interface EventRouteTarget {
  applyEvents(events: readonly SimEvent[]): void;
  applySnapshot(snapshot: StateSnapshot): void;
}

export interface EventRouterOptions {
  throttleLayer?: EventThrottleLayer;
}

export class EventRouter {
  constructor(
    private readonly store: EventRouteTarget,
    private readonly options: EventRouterOptions = {}
  ) {}

  routeRawEventMessage(message: unknown): readonly SimEvent[] {
    const events = decodeSimEventBatch(message);
    this.routeEvents(events);
    return events;
  }

  routeEvents(events: readonly SimEvent[]): void {
    if (this.options.throttleLayer) {
      this.options.throttleLayer.pushEvents(events);
      return;
    }
    this.store.applyEvents(events);
  }

  routeRawStateMessage(message: unknown): void {
    this.store.applySnapshot(decodeStateSnapshot(message));
  }

  flush(): void {
    this.options.throttleLayer?.flush();
  }

  close(): void {
    this.options.throttleLayer?.close();
  }
}
