import { describe, expect, it } from "vitest";

import { buildComputeDurationSummary } from "../src/dashboard/compute_view/ComputeView";

describe("buildComputeDurationSummary", () => {
  it("summarizes task duration metric records", () => {
    expect(
      buildComputeDurationSummary([
        metric("task-a", "task.duration", 1.5),
        metric("task-b", "task.duration", 3.5),
        metric("task-c", "task.progress", 1)
      ])
    ).toEqual({
      sampleCount: 2,
      averageDuration: 2.5,
      maxDuration: 3.5
    });
  });

  it("returns zero values when no duration metrics exist", () => {
    expect(buildComputeDurationSummary([])).toEqual({
      sampleCount: 0,
      averageDuration: 0,
      maxDuration: 0
    });
  });
});

function metric(entityId: string, metricName: string, value: number) {
  return {
    metric_name: metricName,
    sim_time: 1,
    entity_id: entityId,
    value
  };
}
