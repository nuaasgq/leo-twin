import { describe, expect, it } from "vitest";

import { SimEvent } from "../src/core/event_types";
import { ObservabilityStore } from "../src/stream/state_store";

describe("1000 node observability stress", () => {
  it("handles 1000 satellite state updates with bounded event log", () => {
    const store = new ObservabilityStore({ eventLogLimit: 256 });
    const events: SimEvent[] = Array.from({ length: 1000 }, (_, index) => ({
      event_id: `orbit:${index.toString().padStart(4, "0")}`,
      sim_time: index / 10,
      priority: 0,
      source: "orbit",
      target: "frontend",
      event_type: "ORBIT_UPDATE",
      payload: {
        satellite_id: `sat-${index.toString().padStart(4, "0")}`,
        sim_time: index / 10,
        position: [index, index + 1, index + 2],
        velocity: [0, 0, 0],
        status: "online"
      }
    }));

    store.applyEvents(events);
    const state = store.getSnapshot();

    expect(state.satellites.size).toBe(1000);
    expect(state.eventCount).toBe(1000);
    expect(state.eventLog.length).toBe(256);
    expect(state.satellites.get("sat-0000")?.position).toEqual([0, 1, 2]);
    expect(state.satellites.get("sat-0999")?.position).toEqual([999, 1000, 1001]);
  });
});
