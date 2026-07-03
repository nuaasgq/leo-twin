import { decodeSimEventBatch, decodeStateSnapshot } from "../../core/decoder";
import { SimEvent } from "../../core/event_types";
import { ObservabilityStore } from "../state_store";

export class EventRouter {
  constructor(private readonly store: ObservabilityStore) {}

  routeRawEventMessage(message: unknown): readonly SimEvent[] {
    const events = decodeSimEventBatch(message);
    this.routeEvents(events);
    return events;
  }

  routeEvents(events: readonly SimEvent[]): void {
    this.store.applyEvents(events);
  }

  routeRawStateMessage(message: unknown): void {
    this.store.applySnapshot(decodeStateSnapshot(message));
  }
}
