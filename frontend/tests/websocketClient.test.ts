import { describe, expect, it } from "vitest";

import { EventRouter } from "../src/stream/event_router";
import { ObservabilityStore } from "../src/stream/state_store";
import {
  WebSocketCursorAdvance,
  WebSocketConnectionIssue,
  WebSocketLike,
  WebSocketStreamClient,
  websocketUrl
} from "../src/stream/websocket_client";

describe("WebSocketStreamClient", () => {
  it("batches event stream messages from a mock websocket", () => {
    const sockets: MockSocket[] = [];
    const store = new ObservabilityStore();
    const router = new EventRouter(store);
    const client = new WebSocketStreamClient(router, {
      eventUrl: "ws://test/events",
      stateUrl: "ws://test/state",
      batchSize: 2,
      flushIntervalMs: 10_000,
      createWebSocket: (url) => {
        const socket = new MockSocket(url);
        sockets.push(socket);
        return socket;
      }
    });

    client.connect();
    sockets[0].emit(orbitEvent("sat-1", 1));
    expect(store.getSnapshot().satellites.size).toBe(0);
    sockets[0].emit(orbitEvent("sat-2", 2));

    expect(store.getSnapshot().satellites.size).toBe(2);
    expect(sockets.map((socket) => socket.url)).toEqual(["ws://test/events", "ws://test/state"]);
    client.close();
  });

  it("can disable the state snapshot stream for paced event playback", () => {
    const sockets: MockSocket[] = [];
    const store = new ObservabilityStore();
    const router = new EventRouter(store);
    const client = new WebSocketStreamClient(router, {
      eventUrl: "ws://test/events",
      stateUrl: "ws://test/state",
      stateStreamEnabled: false,
      createWebSocket: (url) => {
        const socket = new MockSocket(url);
        sockets.push(socket);
        return socket;
      }
    });

    client.connect();

    expect(sockets.map((socket) => socket.url)).toEqual(["ws://test/events"]);
    client.close();
  });

  it("consumes cursor envelopes from event and state websocket streams", () => {
    const sockets: MockSocket[] = [];
    const cursorAdvances: WebSocketCursorAdvance[] = [];
    const store = new ObservabilityStore();
    const router = new EventRouter(store);
    const client = new WebSocketStreamClient(router, {
      eventUrl: "ws://test/events",
      stateUrl: "ws://test/state",
      batchSize: 2,
      flushIntervalMs: 10_000,
      createWebSocket: (url) => {
        const socket = new MockSocket(url);
        sockets.push(socket);
        return socket;
      },
      onCursorAdvance: (advance) => cursorAdvances.push(advance)
    });

    client.connect();
    sockets[0].emit({
      cursor: 0,
      next_cursor: 2,
      overflow: false,
      dropped_count: 0,
      items: [orbitEvent("sat-1", 1), orbitEvent("sat-2", 2)]
    });
    sockets[1].emit({
      cursor: 0,
      next_cursor: 1,
      overflow: false,
      dropped_count: 0,
      items: []
    });

    expect(store.getSnapshot().satellites.size).toBe(2);
    expect(cursorAdvances).toEqual([
      {
        channel: "events",
        cursor: 0,
        nextCursor: 2,
        overflow: false,
        droppedCount: 0
      },
      {
        channel: "state",
        cursor: 0,
        nextCursor: 1,
        overflow: false,
        droppedCount: 0
      }
    ]);
    client.close();
  });

  it("reports unexpected event and state stream socket issues", () => {
    const sockets: MockSocket[] = [];
    const opened: string[] = [];
    const issues: WebSocketConnectionIssue[] = [];
    const store = new ObservabilityStore();
    const router = new EventRouter(store);
    const client = new WebSocketStreamClient(router, {
      eventUrl: "ws://test/events",
      stateUrl: "ws://test/state",
      createWebSocket: (url) => {
        const socket = new MockSocket(url);
        sockets.push(socket);
        return socket;
      },
      onConnectionOpen: (channel, url) => opened.push(`${channel}:${url}`),
      onConnectionIssue: (issue) => issues.push(issue)
    });

    client.connect();
    sockets[0].open();
    sockets[1].open();
    sockets[0].error();
    sockets[1].closeUnexpected(1006, "network");

    expect(opened).toEqual(["events:ws://test/events", "state:ws://test/state"]);
    expect(issues).toEqual([
      { channel: "events", type: "error", url: "ws://test/events" },
      {
        channel: "state",
        type: "close",
        url: "ws://test/state",
        code: 1006,
        reason: "network",
        wasClean: false
      }
    ]);

    client.close();
    expect(issues).toHaveLength(2);
  });
});

describe("websocketUrl", () => {
  it("uses the backend port for the local Vite development frontend", () => {
    expect(
      websocketUrl("/control", {
        location: {
          protocol: "http:",
          host: "127.0.0.1:5173",
          hostname: "127.0.0.1",
          port: "5173"
        }
      })
    ).toBe("ws://127.0.0.1:8765/control");
  });

  it("keeps same-origin websocket URLs outside the local development frontend", () => {
    expect(
      websocketUrl("/stream/events", {
        location: {
          protocol: "https:",
          host: "leo.example.test",
          hostname: "leo.example.test",
          port: ""
        }
      })
    ).toBe("wss://leo.example.test/stream/events");
  });

  it("allows an explicit backend websocket origin override", () => {
    expect(
      websocketUrl("stream/state", {
        backendOrigin: "http://127.0.0.1:9000/",
        location: {
          protocol: "http:",
          host: "127.0.0.1:5173",
          hostname: "127.0.0.1",
          port: "5173"
        }
      })
    ).toBe("ws://127.0.0.1:9000/stream/state");
  });
});

class MockSocket implements WebSocketLike {
  onopen: ((event: Event) => void) | null = null;
  onmessage: ((event: MessageEvent<string>) => void) | null = null;
  onerror: ((event: Event) => void) | null = null;
  onclose: ((event: CloseEvent) => void) | null = null;
  closed = false;

  constructor(readonly url: string) {}

  open(): void {
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
    this.onclose?.({ code, reason, wasClean: false } as CloseEvent);
  }

  close(): void {
    this.closed = true;
    this.onclose?.({ code: 1000, reason: "client", wasClean: true } as CloseEvent);
  }
}

function orbitEvent(satelliteId: string, index: number) {
  return {
    event_id: `orbit:${index}`,
    sim_time: index,
    priority: 0,
    source: "orbit",
    target: "frontend",
    event_type: "ORBIT_UPDATE",
    payload: {
      satellite_id: satelliteId,
      sim_time: index,
      position: [index, index + 1, index + 2],
      velocity: [0, 0, 0],
      status: "online"
    }
  };
}
