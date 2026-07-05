import { GeneratedScenarioConfig, RuntimeStatusPayload } from "../core/event_types";
import { websocketUrl } from "../stream/websocket_client";

export type RuntimeAction =
  | "INITIALIZE"
  | "START"
  | "STOP"
  | "PAUSE"
  | "RESUME"
  | "RESET"
  | "SET_SPEED"
  | "SET_MODE";

export interface ControlAck {
  type: "CONTROL_ACK" | "RUNTIME_STATUS";
  ok?: boolean;
  error?: string;
  status?: RuntimeStatusPayload;
  config?: unknown;
  generated_config?: GeneratedScenarioConfig;
}

export interface ControlWebSocketLike {
  readyState?: number;
  onopen: ((event: Event) => void) | null;
  onmessage: ((event: MessageEvent<string>) => void) | null;
  onerror: ((event: Event) => void) | null;
  onclose: ((event: CloseEvent) => void) | null;
  send(data: string): void;
  close(): void;
}

export type ControlWebSocketFactory = (url: string) => ControlWebSocketLike;

export interface ControlConnectionIssue {
  type: "error" | "close";
  url: string;
  code?: number;
  reason?: string;
  wasClean?: boolean;
}

const OPEN_SOCKET_STATE = 1;

export interface ControlChannelClientOptions {
  url?: string;
  createWebSocket?: ControlWebSocketFactory;
  onMessage?: (message: ControlAck) => void;
  onConnectionOpen?: (url: string) => void;
  onConnectionIssue?: (issue: ControlConnectionIssue) => void;
}

export class ControlChannelClient {
  private readonly url: string;
  private readonly createWebSocket: ControlWebSocketFactory;
  private readonly onMessage: (message: ControlAck) => void;
  private readonly onConnectionOpen: (url: string) => void;
  private readonly onConnectionIssue: (issue: ControlConnectionIssue) => void;
  private socket: ControlWebSocketLike | null = null;
  private readonly pendingMessages: string[] = [];
  private closing = false;

  constructor(options: ControlChannelClientOptions = {}) {
    this.url = options.url ?? websocketUrl("/control");
    this.createWebSocket = options.createWebSocket ?? ((url) => new WebSocket(url));
    this.onMessage = options.onMessage ?? (() => undefined);
    this.onConnectionOpen = options.onConnectionOpen ?? (() => undefined);
    this.onConnectionIssue = options.onConnectionIssue ?? (() => undefined);
  }

  connect(): void {
    if (this.socket !== null) {
      return;
    }
    this.closing = false;
    const socket = this.createWebSocket(this.url);
    this.socket = socket;
    socket.onopen = () => {
      this.onConnectionOpen(this.url);
      this.flushPending();
    };
    socket.onmessage = (message) => {
      this.onMessage(decodeControlAck(message.data));
    };
    socket.onerror = () => {
      if (!this.closing) {
        this.onConnectionIssue({ type: "error", url: this.url });
      }
    };
    socket.onclose = (event) => {
      if (this.socket === socket) {
        this.socket = null;
      }
      if (!this.closing) {
        this.onConnectionIssue({
          type: "close",
          url: this.url,
          code: event.code,
          reason: event.reason,
          wasClean: event.wasClean
        });
      }
    };
  }

  sendConfigUpdate(payload: Record<string, unknown>): void {
    this.send({
      type: "CONFIG_UPDATE",
      payload
    });
  }

  sendRuntimeControl(action: RuntimeAction, payload: Record<string, unknown> = {}): void {
    this.send({
      type: "RUNTIME_CONTROL",
      action,
      payload
    });
  }

  close(): void {
    this.closing = true;
    this.socket?.close();
    this.socket = null;
    this.pendingMessages.splice(0, this.pendingMessages.length);
  }

  private send(message: Record<string, unknown>): void {
    const encoded = JSON.stringify(message);
    this.connect();
    if (this.socket?.readyState === OPEN_SOCKET_STATE) {
      this.socket.send(encoded);
      return;
    }
    this.pendingMessages.push(encoded);
  }

  private flushPending(): void {
    if (this.socket?.readyState !== OPEN_SOCKET_STATE) {
      return;
    }
    for (const message of this.pendingMessages.splice(0, this.pendingMessages.length)) {
      this.socket.send(message);
    }
  }
}

function decodeControlAck(data: string): ControlAck {
  const value = JSON.parse(data);
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new TypeError("control response must be an object");
  }
  return value as ControlAck;
}
