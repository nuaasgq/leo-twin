import { describe, expect, it } from "vitest";

import { SimEvent } from "../src/core/event_types";
import { EventPlaybackLayer, PlaybackClock } from "../src/stream/playback_layer";

describe("EventPlaybackLayer", () => {
  it("releases events deterministically according to simulation time and speed", () => {
    const clock = new ManualPlaybackClock();
    const batches: string[][] = [];
    const layer = new EventPlaybackLayer(
      (events) => batches.push(events.map((event) => String(event.event_id))),
      {
        speedFactor: 10,
        clock
      }
    );

    layer.pushEvents([
      orbitEvent("late", 20),
      orbitEvent("first", 0),
      orbitEvent("middle", 10)
    ]);

    expect(batches).toEqual([["first"]]);
    expect(layer.pendingCount()).toBe(2);

    clock.advance(999);
    expect(batches).toEqual([["first"]]);

    clock.advance(1);
    expect(batches).toEqual([["first"], ["middle"]]);

    clock.advance(1000);
    expect(batches).toEqual([["first"], ["middle"], ["late"]]);
    expect(layer.pendingCount()).toBe(0);
  });

  it("clears queued playback when closed", () => {
    const clock = new ManualPlaybackClock();
    const batches: string[][] = [];
    const layer = new EventPlaybackLayer(
      (events) => batches.push(events.map((event) => String(event.event_id))),
      {
        speedFactor: 1,
        clock
      }
    );

    layer.pushEvents([orbitEvent("first", 0), orbitEvent("future", 10)]);
    layer.close();
    clock.advance(10_000);

    expect(batches).toEqual([["first"]]);
    expect(layer.pendingCount()).toBe(0);
  });
});

class ManualPlaybackClock implements PlaybackClock {
  private currentTimeMs = 0;
  private nextTimerId = 1;
  private readonly timers = new Map<number, { dueAtMs: number; handler: () => void }>();

  now(): number {
    return this.currentTimeMs;
  }

  setTimeout(handler: () => void, delayMs: number): ReturnType<typeof setTimeout> {
    const timerId = this.nextTimerId;
    this.nextTimerId += 1;
    this.timers.set(timerId, {
      dueAtMs: this.currentTimeMs + delayMs,
      handler
    });
    return timerId as ReturnType<typeof setTimeout>;
  }

  clearTimeout(timer: ReturnType<typeof setTimeout>): void {
    this.timers.delete(Number(timer));
  }

  advance(deltaMs: number): void {
    this.currentTimeMs += deltaMs;
    while (true) {
      const dueTimers = Array.from(this.timers.entries())
        .filter(([, timer]) => timer.dueAtMs <= this.currentTimeMs)
        .sort((left, right) => left[1].dueAtMs - right[1].dueAtMs || left[0] - right[0]);
      if (dueTimers.length === 0) {
        return;
      }
      const [timerId, timer] = dueTimers[0];
      this.timers.delete(timerId);
      timer.handler();
    }
  }
}

function orbitEvent(eventId: string, simTime: number): SimEvent {
  return {
    event_id: eventId,
    sim_time: simTime,
    priority: 0,
    source: "orbit",
    target: "frontend",
    event_type: "ORBIT_UPDATE",
    payload: {
      satellite_id: `sat-${eventId}`,
      sim_time: simTime,
      position: [simTime, simTime + 1, simTime + 2],
      velocity: [0, 0, 0],
      status: "online"
    }
  };
}
