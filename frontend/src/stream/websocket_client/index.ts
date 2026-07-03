import { decodeSimEvent } from "../../core/decoder";
import { SimEvent } from "../../core/event_types";
import { EventRouter } from "../event_router";

export interface StreamClientOptions {
  eventUrl?: string;
  stateUrl?: string;
  batchSize?: number;
  flushIntervalMs?: number;
  createWebSocket?: WebSocketFactory;
}

export type WebSocketFactory = (url: string) => WebSocketLike;

export interface WebSocketLike {
  onopen: ((event: Event) => void) | null;
  onmessage: ((event: MessageEvent<string>) => void) | null;
  onerror: ((event: Event) => void) | null;
  onclose: ((event: CloseEvent) => void) | null;
  close(): void;
}

export class WebSocketStreamClient {
  private readonly eventUrl: string;
  private readonly stateUrl: string;
  private readonly batchSize: number;
  private readonly flushIntervalMs: number;
  private readonly createWebSocket: WebSocketFactory;
  private eventSocket: WebSocketLike | null = null;
  private stateSocket: WebSocketLike | null = null;
  private flushTimer: ReturnType<typeof setTimeout> | null = null;
  private readonly eventBuffer: SimEvent[] = [];

  constructor(
    private readonly router: EventRouter,
    options: StreamClientOptions = {}
  ) {
    this.eventUrl = options.eventUrl ?? websocketUrl("/stream/events");
    this.stateUrl = options.stateUrl ?? websocketUrl("/stream/state");
    this.batchSize = options.batchSize ?? 200;
    this.flushIntervalMs = options.flushIntervalMs ?? 50;
    this.createWebSocket = options.createWebSocket ?? ((url) => new WebSocket(url));
  }

  connect(): void {
    this.eventSocket = this.createWebSocket(this.eventUrl);
    this.eventSocket.onmessage = (message) => {
      const events = decodeStreamEvents(message.data);
      if (events.length === 0) {
        return;
      }
      for (const event of events) {
        this.eventBuffer.push(event);
      }
      if (this.eventBuffer.length >= this.batchSize) {
        this.flush();
      } else {
        this.scheduleFlush();
      }
    };

    this.stateSocket = this.createWebSocket(this.stateUrl);
    this.stateSocket.onmessage = (message) => {
      try {
        this.router.routeRawStateMessage(parseJsonMessage(message.data));
      } catch (error) {
        console.warn("ignored invalid state stream message", error);
      }
    };
  }

  flush(): void {
    if (this.flushTimer !== null) {
      clearTimeout(this.flushTimer);
      this.flushTimer = null;
    }
    if (this.eventBuffer.length === 0) {
      return;
    }
    const events = this.eventBuffer.splice(0, this.eventBuffer.length);
    this.router.routeEvents(events);
  }

  close(): void {
    if (this.flushTimer !== null) {
      clearTimeout(this.flushTimer);
      this.flushTimer = null;
    }
    this.eventSocket?.close();
    this.stateSocket?.close();
    this.eventSocket = null;
    this.stateSocket = null;
    this.eventBuffer.splice(0, this.eventBuffer.length);
  }

  private scheduleFlush(): void {
    if (this.flushTimer !== null) {
      return;
    }
    this.flushTimer = setTimeout(() => this.flush(), this.flushIntervalMs);
  }
}

export function websocketUrl(path: string): string {
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  return `${protocol}//${window.location.host}${path}`;
}

function parseJsonMessage(data: string): unknown {
  return JSON.parse(data);
}

function decodeStreamEvents(data: string): readonly SimEvent[] {
  try {
    const parsed = parseJsonMessage(data);
    const items = Array.isArray(parsed) ? parsed : [parsed];
    const events: SimEvent[] = [];
    for (const item of items) {
      try {
        events.push(decodeSimEvent(item));
      } catch (error) {
        console.warn("ignored invalid event stream message", error);
      }
    }
    return events;
  } catch (error) {
    console.warn("ignored malformed event stream payload", error);
    return [];
  }
}
