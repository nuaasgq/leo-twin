import { describe, expect, it } from "vitest";

import { SimEvent } from "../src/core/event_types";
import { ObservabilityStore, selectNetworkKpis } from "../src/stream/state_store";

describe("ObservabilityStore", () => {
  it("updates centralized rendering state from event stream", () => {
    const store = new ObservabilityStore({ eventLogLimit: 4 });
    store.applyScenarioConfig({
      ground_users: [{ user_id: "user-1", position: [120, 30, 0] }]
    });

    store.applyEvents([
      event("sat:1", "ORBIT_UPDATE", {
        satellite_id: "sat-1",
        sim_time: 1,
        position: [1, 2, 3],
        velocity: [0, 1, 0],
        status: "online"
      }),
      event("link:1", "ACCESS_START", {
        source_id: "sat-1",
        target_id: "user-1",
        latency: 12,
        capacity: 40,
        availability: true
      })
    ]);

    const state = store.getSnapshot();
    expect(state.satellites.get("sat-1")?.position).toEqual([1, 2, 3]);
    expect(state.groundUsers.get("user-1")?.position).toEqual([120, 30, 0]);
    expect(state.links.size).toBe(1);
    expect(selectNetworkKpis(state)).toEqual({
      latency: 12,
      throughput: 40,
      linkUtilization: 0
    });
  });
});

function event(eventId: string, eventType: SimEvent["event_type"], payload: unknown): SimEvent {
  return {
    event_id: eventId,
    sim_time: 1,
    priority: 0,
    source: "test",
    target: "frontend",
    event_type: eventType,
    payload
  };
}
