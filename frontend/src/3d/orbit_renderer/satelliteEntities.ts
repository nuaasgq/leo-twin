import {
  Cartesian2,
  Color,
  ConstantPositionProperty,
  ConstantProperty,
  Entity,
  EntityCollection,
  LabelStyle,
  VerticalOrigin
} from "cesium";

import { SatelliteState } from "../../core/event_types";
import { satelliteCartesian } from "../cesium/positions";

export function upsertSatelliteEntity(
  entities: EntityCollection,
  cache: Map<string, Entity>,
  satellite: SatelliteState
): void {
  const id = `satellite:${satellite.satellite_id}`;
  const position = satelliteCartesian(satellite);
  const active = satellite.status.toLowerCase() !== "offline";
  let entity = cache.get(id);
  if (!entity) {
    entity = entities.add({
      id,
      name: satellite.satellite_id,
      point: {
        pixelSize: 12,
        color: active ? Color.CYAN : Color.GRAY,
        outlineColor: Color.BLACK,
        outlineWidth: 2,
        disableDepthTestDistance: Number.POSITIVE_INFINITY
      },
      label: {
        text: satellite.satellite_id,
        font: "12px sans-serif",
        fillColor: Color.WHITE,
        outlineColor: Color.BLACK,
        outlineWidth: 2,
        style: LabelStyle.FILL_AND_OUTLINE,
        verticalOrigin: VerticalOrigin.BOTTOM,
        disableDepthTestDistance: Number.POSITIVE_INFINITY,
        pixelOffset: new Cartesian2(0, -12)
      }
    });
    cache.set(id, entity);
  }

  entity.position = new ConstantPositionProperty(position);
  if (entity.point) {
    entity.point.color = new ConstantProperty(active ? Color.CYAN : Color.GRAY);
  }
}

export function pruneSatelliteEntities(
  entities: EntityCollection,
  cache: Map<string, Entity>,
  activeIds: ReadonlySet<string>
): void {
  for (const [id, entity] of Array.from(cache.entries())) {
    if (!activeIds.has(id)) {
      entities.remove(entity);
      cache.delete(id);
    }
  }
}
