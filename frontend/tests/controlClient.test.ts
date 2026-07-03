import { describe, expect, it } from "vitest";

import {
  ControlChannelClient,
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

  send(data: string): void {
    this.sent.push(data);
  }

  close(): void {
    this.closed = true;
    this.readyState = 3;
    this.onclose?.({} as CloseEvent);
  }
}
