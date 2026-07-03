import { describe, expect, it } from "vitest";

import { EventRouter } from "../src/stream/event_router";
import { ObservabilityStore } from "../src/stream/state_store";
import { WebSocketLike, WebSocketStreamClient } from "../src/stream/websocket_client";

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
});

class MockSocket implements WebSocketLike {
  onopen: ((event: Event) => void) | null = null;
  onmessage: ((event: MessageEvent<string>) => void) | null = null;
  onerror: ((event: Event) => void) | null = null;
  onclose: ((event: CloseEvent) => void) | null = null;
  closed = false;

  constructor(readonly url: string) {}

  emit(payload: unknown): void {
    this.onmessage?.({ data: JSON.stringify(payload) } as MessageEvent<string>);
  }

  close(): void {
    this.closed = true;
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
