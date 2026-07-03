import { Color, PointPrimitive, PointPrimitiveCollection } from "cesium";

import { SatelliteState } from "../../core/event_types";
import { satelliteCartesian } from "../cesium/positions";

const DEPTH_TEST_DISABLE_DISTANCE = 1_000_000_000_000;

export class SatellitePrimitiveBatch {
  private readonly pointsBySatelliteId = new Map<string, PointPrimitive>();

  constructor(private readonly collection: PointPrimitiveCollection) {}

  update(satellites: readonly SatelliteState[]): void {
    const activeIds = new Set<string>();
    for (const satellite of satellites) {
      activeIds.add(satellite.satellite_id);
      this.upsert(satellite);
    }
    for (const [satelliteId, point] of Array.from(this.pointsBySatelliteId.entries())) {
      if (!activeIds.has(satelliteId)) {
        this.collection.remove(point);
        this.pointsBySatelliteId.delete(satelliteId);
      }
    }
  }

  clear(): void {
    this.collection.removeAll();
    this.pointsBySatelliteId.clear();
  }

  size(): number {
    return this.pointsBySatelliteId.size;
  }

  private upsert(satellite: SatelliteState): void {
    const active = satellite.status.toLowerCase() !== "offline";
    const color = active ? Color.CYAN : Color.GRAY;
    let point = this.pointsBySatelliteId.get(satellite.satellite_id);
    if (!point) {
      point = this.collection.add({
        id: satellite.satellite_id,
        position: satelliteCartesian(satellite),
        pixelSize: 12,
        color,
        outlineColor: Color.BLACK,
        outlineWidth: 2,
        disableDepthTestDistance: DEPTH_TEST_DISABLE_DISTANCE
      });
      this.pointsBySatelliteId.set(satellite.satellite_id, point);
      return;
    }
    point.position = satelliteCartesian(satellite);
    point.color = color;
  }
}
