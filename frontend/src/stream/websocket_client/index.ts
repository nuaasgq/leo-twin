import { decodeSimEvent } from "../../core/decoder";
import { SimEvent } from "../../core/event_types";
import { EventRouter } from "../event_router";
import { EventPlaybackLayer } from "../playback_layer";

export interface StreamClientOptions {
  eventUrl?: string;
  stateUrl?: string;
  batchSize?: number;
  flushIntervalMs?: number;
  playbackLayer?: EventPlaybackLayer;
  stateStreamEnabled?: boolean;
  createWebSocket?: WebSocketFactory;
  onConnectionOpen?: (channel: WebSocketChannel, url: string) => void;
  onConnectionIssue?: (issue: WebSocketConnectionIssue) => void;
  onCursorAdvance?: (advance: WebSocketCursorAdvance) => void;
}

export type WebSocketFactory = (url: string) => WebSocketLike;
export type WebSocketChannel = "events" | "state";

export interface WebSocketConnectionIssue {
  channel: WebSocketChannel;
  type: "error" | "close";
  url: string;
  code?: number;
  reason?: string;
  wasClean?: boolean;
}

export interface WebSocketCursorAdvance {
  channel: WebSocketChannel;
  cursor?: number;
  nextCursor: number;
  overflow?: boolean;
  droppedCount?: number;
}

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
  private readonly onConnectionOpen: (channel: WebSocketChannel, url: string) => void;
  private readonly onConnectionIssue: (issue: WebSocketConnectionIssue) => void;
  private readonly onCursorAdvance: (advance: WebSocketCursorAdvance) => void;
  private readonly playbackLayer: EventPlaybackLayer | null;
  private readonly stateStreamEnabled: boolean;
  private eventSocket: WebSocketLike | null = null;
  private stateSocket: WebSocketLike | null = null;
  private flushTimer: ReturnType<typeof setTimeout> | null = null;
  private readonly eventBuffer: SimEvent[] = [];
  private closing = false;

  constructor(
    private readonly router: EventRouter,
    options: StreamClientOptions = {}
  ) {
    this.eventUrl = options.eventUrl ?? websocketUrl("/stream/events");
    this.stateUrl = options.stateUrl ?? websocketUrl("/stream/state");
    this.batchSize = options.batchSize ?? 200;
    this.flushIntervalMs = options.flushIntervalMs ?? 50;
    this.playbackLayer = options.playbackLayer ?? null;
    this.stateStreamEnabled = options.stateStreamEnabled ?? true;
    this.createWebSocket = options.createWebSocket ?? ((url) => new WebSocket(url));
    this.onConnectionOpen = options.onConnectionOpen ?? (() => undefined);
    this.onConnectionIssue = options.onConnectionIssue ?? (() => undefined);
    this.onCursorAdvance = options.onCursorAdvance ?? (() => undefined);
  }

  connect(): void {
    this.closing = false;
    this.eventSocket = this.createWebSocket(this.eventUrl);
    this.attachDiagnostics(this.eventSocket, "events", this.eventUrl);
    this.eventSocket.onmessage = (message) => {
      const decoded = decodeStreamEventMessage(message.data);
      if (decoded.cursorAdvance !== undefined) {
        this.onCursorAdvance({ channel: "events", ...decoded.cursorAdvance });
      }
      const events = decoded.events;
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

    if (this.stateStreamEnabled) {
      this.stateSocket = this.createWebSocket(this.stateUrl);
      this.attachDiagnostics(this.stateSocket, "state", this.stateUrl);
      this.stateSocket.onmessage = (message) => {
        try {
          const decoded = decodeStateStreamMessage(message.data);
          if (decoded.cursorAdvance !== undefined) {
            this.onCursorAdvance({ channel: "state", ...decoded.cursorAdvance });
          }
          for (const item of decoded.items) {
            this.router.routeRawStateMessage(item);
          }
        } catch (error) {
          console.warn("ignored invalid state stream message", error);
        }
      };
    }
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
    if (this.playbackLayer !== null) {
      this.playbackLayer.pushEvents(events);
      return;
    }
    this.router.routeEvents(events);
  }

  close(): void {
    this.closing = true;
    if (this.flushTimer !== null) {
      clearTimeout(this.flushTimer);
      this.flushTimer = null;
    }
    this.eventSocket?.close();
    this.stateSocket?.close();
    this.eventSocket = null;
    this.stateSocket = null;
    this.eventBuffer.splice(0, this.eventBuffer.length);
    this.playbackLayer?.close();
  }

  private attachDiagnostics(
    socket: WebSocketLike,
    channel: WebSocketChannel,
    url: string
  ): void {
    socket.onopen = () => {
      if (!this.closing) {
        this.onConnectionOpen(channel, url);
      }
    };
    socket.onerror = () => {
      if (!this.closing) {
        this.onConnectionIssue({ channel, type: "error", url });
      }
    };
    socket.onclose = (event) => {
      if (!this.closing) {
        this.onConnectionIssue({
          channel,
          type: "close",
          url,
          code: event.code,
          reason: event.reason,
          wasClean: event.wasClean
        });
      }
    };
  }

  private scheduleFlush(): void {
    if (this.flushTimer !== null) {
      return;
    }
    this.flushTimer = setTimeout(() => this.flush(), this.flushIntervalMs);
  }
}

export interface WebSocketUrlOptions {
  location?: WebSocketLocationLike;
  backendOrigin?: string;
  developmentBackendPort?: string | number;
}

interface WebSocketLocationLike {
  protocol: string;
  host: string;
  hostname: string;
  port: string;
}

export function websocketUrl(path: string, options: WebSocketUrlOptions = {}): string {
  const location = options.location ?? window.location;
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  const configuredOrigin = normalizeWebSocketOrigin(
    options.backendOrigin ??
      import.meta.env.VITE_BACKEND_WS_ORIGIN ??
      import.meta.env.VITE_BACKEND_ORIGIN
  );
  if (configuredOrigin !== null) {
    return `${configuredOrigin}${normalizedPath}`;
  }
  const protocol = location.protocol === "https:" ? "wss:" : "ws:";
  const host = localDevFrontendNeedsBackendPort(location)
    ? hostWithPort(
        location.hostname,
        String(options.developmentBackendPort ?? import.meta.env.VITE_BACKEND_PORT ?? 8765)
      )
    : location.host;
  return `${protocol}//${host}${normalizedPath}`;
}

function localDevFrontendNeedsBackendPort(location: WebSocketLocationLike): boolean {
  return location.port === "5173" && isLocalHostname(location.hostname);
}

function isLocalHostname(hostname: string): boolean {
  return hostname === "localhost" || hostname === "127.0.0.1" || hostname === "::1";
}

function hostWithPort(hostname: string, port: string): string {
  const normalizedHostname =
    hostname.includes(":") && !hostname.startsWith("[") ? `[${hostname}]` : hostname;
  return `${normalizedHostname}:${port}`;
}

function normalizeWebSocketOrigin(origin: string | undefined): string | null {
  if (origin === undefined) {
    return null;
  }
  const trimmed = origin.trim();
  if (trimmed.length === 0) {
    return null;
  }
  const withoutTrailingSlash = trimmed.endsWith("/") ? trimmed.slice(0, -1) : trimmed;
  if (withoutTrailingSlash.startsWith("https://")) {
    return `wss://${withoutTrailingSlash.slice("https://".length)}`;
  }
  if (withoutTrailingSlash.startsWith("http://")) {
    return `ws://${withoutTrailingSlash.slice("http://".length)}`;
  }
  if (
    withoutTrailingSlash.startsWith("ws://") ||
    withoutTrailingSlash.startsWith("wss://")
  ) {
    return withoutTrailingSlash;
  }
  return `ws://${withoutTrailingSlash}`;
}

function parseJsonMessage(data: string): unknown {
  return JSON.parse(data);
}

interface DecodedEventStreamMessage {
  events: readonly SimEvent[];
  cursorAdvance?: Omit<WebSocketCursorAdvance, "channel">;
}

interface DecodedStateStreamMessage {
  items: readonly unknown[];
  cursorAdvance?: Omit<WebSocketCursorAdvance, "channel">;
}

function decodeStreamEventMessage(data: string): DecodedEventStreamMessage {
  try {
    const parsed = parseJsonMessage(data);
    const envelope = streamCursorEnvelope(parsed);
    const rawItems = envelope?.items ?? (Array.isArray(parsed) ? parsed : [parsed]);
    const events: SimEvent[] = [];
    for (const item of rawItems) {
      try {
        events.push(decodeSimEvent(item));
      } catch (error) {
        console.warn("ignored invalid event stream message", error);
      }
    }
    return {
      events,
      ...(envelope?.cursorAdvance === undefined ? {} : { cursorAdvance: envelope.cursorAdvance })
    };
  } catch (error) {
    console.warn("ignored malformed event stream payload", error);
    return { events: [] };
  }
}

function decodeStateStreamMessage(data: string): DecodedStateStreamMessage {
  const parsed = parseJsonMessage(data);
  const envelope = streamCursorEnvelope(parsed);
  const items = envelope?.items ?? [parsed];
  return {
    items,
    ...(envelope?.cursorAdvance === undefined ? {} : { cursorAdvance: envelope.cursorAdvance })
  };
}

function streamCursorEnvelope(
  value: unknown
): { items: readonly unknown[]; cursorAdvance?: Omit<WebSocketCursorAdvance, "channel"> } | null {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    return null;
  }
  const record = value as Record<string, unknown>;
  if (!Array.isArray(record.items)) {
    return null;
  }
  const nextCursor =
    typeof record.next_cursor === "number" && Number.isFinite(record.next_cursor)
      ? record.next_cursor
      : undefined;
  const cursorAdvance =
    nextCursor === undefined
      ? undefined
      : {
          ...(typeof record.cursor === "number" && Number.isFinite(record.cursor)
            ? { cursor: record.cursor }
            : {}),
          nextCursor,
          ...(typeof record.overflow === "boolean" ? { overflow: record.overflow } : {}),
          ...(typeof record.dropped_count === "number" && Number.isFinite(record.dropped_count)
            ? { droppedCount: record.dropped_count }
            : {})
        };
  return {
    items: record.items,
    ...(cursorAdvance === undefined ? {} : { cursorAdvance })
  };
}
