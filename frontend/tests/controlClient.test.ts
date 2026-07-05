import { describe, expect, it } from "vitest";

import {
  ControlChannelClient,
  ControlConnectionIssue,
  ControlWebSocketLike
} from "../src/config_panel/controlClient";

describe("ControlChannelClient", () => {
  it("sends config updates and runtime commands over websocket", () => {
    const sockets: MockControlSocket[] = [];
    const received: unknown[] = [];
    const client = new ControlChannelClient({
      url: "ws://test/control",
      createWebSocket: (url) => {
        const socket = new MockControlSocket(url);
        sockets.push(socket);
        return socket;
      },
      onMessage: (message) => received.push(message)
    });

    client.sendConfigUpdate({ satellite_count: 1000 });
    expect(sockets[0].sent).toHaveLength(0);

    sockets[0].open();
    client.sendRuntimeControl("SET_SPEED", { speed_factor: 25 });
    client.sendRuntimeControl("START");
    sockets[0].emit({
      type: "CONTROL_ACK",
      ok: true,
      status: {
        status: "RUNNING",
        mode: "ACCELERATED",
        speed_factor: 25,
        seed: 1,
        duration: 60,
        config_version: 1,
        last_action: "START"
      }
    });

    expect(sockets[0].url).toBe("ws://test/control");
    expect(sockets[0].sent.map((item) => JSON.parse(item))).toEqual([
      {
        type: "CONFIG_UPDATE",
        payload: {
          satellite_count: 1000
        }
      },
      {
        type: "RUNTIME_CONTROL",
        action: "SET_SPEED",
        payload: {
          speed_factor: 25
        }
      },
      {
        type: "RUNTIME_CONTROL",
        action: "START",
        payload: {}
      }
    ]);
    expect(received).toHaveLength(1);
    client.close();
    expect(sockets[0].closed).toBe(true);
  });

  it("reports unexpected control websocket issues", () => {
    const sockets: MockControlSocket[] = [];
    const opened: string[] = [];
    const issues: ControlConnectionIssue[] = [];
    const client = new ControlChannelClient({
      url: "ws://test/control",
      createWebSocket: (url) => {
        const socket = new MockControlSocket(url);
        sockets.push(socket);
        return socket;
      },
      onConnectionOpen: (url) => opened.push(url),
      onConnectionIssue: (issue) => issues.push(issue)
    });

    client.connect();
    sockets[0].open();
    sockets[0].error();
    sockets[0].closeUnexpected(1006, "network");

    expect(opened).toEqual(["ws://test/control"]);
    expect(issues).toEqual([
      { type: "error", url: "ws://test/control" },
      {
        type: "close",
        url: "ws://test/control",
        code: 1006,
        reason: "network",
        wasClean: false
      }
    ]);

    client.close();
    expect(issues).toHaveLength(2);
  });
});

class MockControlSocket implements ControlWebSocketLike {
  readyState = 0;
  onopen: ((event: Event) => void) | null = null;
  onmessage: ((event: MessageEvent<string>) => void) | null = null;
  onerror: ((event: Event) => void) | null = null;
  onclose: ((event: CloseEvent) => void) | null = null;
  closed = false;
  readonly sent: string[] = [];

  constructor(readonly url: string) {}

  open(): void {
    this.readyState = 1;
    this.onopen?.({} as Event);
  }

  emit(payload: unknown): void {
    this.onmessage?.({ data: JSON.stringify(payload) } as MessageEvent<string>);
  }

  error(): void {
    this.onerror?.({} as Event);
  }

  closeUnexpected(code: number, reason: string): void {
    this.closed = true;
    this.readyState = 3;
    this.onclose?.({ code, reason, wasClean: false } as CloseEvent);
  }

  send(data: string): void {
    this.sent.push(data);
  }

  close(): void {
    this.closed = true;
    this.readyState = 3;
    this.onclose?.({ code: 1000, reason: "client", wasClean: true } as CloseEvent);
  }
}
