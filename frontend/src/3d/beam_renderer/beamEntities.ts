import { Color, ConstantPositionProperty, Entity, EntityCollection } from "cesium";

import { SatelliteState } from "../../core/event_types";
import { satelliteCartesian } from "../cesium/positions";

export interface BeamRenderOptions {
  beamLengthMeters: number;
  beamRadiusMeters: number;
  enabled: boolean;
}

export function upsertBeamEntity(
  entities: EntityCollection,
  cache: Map<string, Entity>,
  satellite: SatelliteState,
  options: BeamRenderOptions
): void {
  const id = `beam:${satellite.satellite_id}`;
  if (!options.enabled) {
    const existing = cache.get(id);
    if (existing) {
      entities.remove(existing);
      cache.delete(id);
    }
    return;
  }

  let entity = cache.get(id);
  if (!entity) {
    entity = entities.add({
      id,
      name: `${satellite.satellite_id} beam`,
      cylinder: {
        length: options.beamLengthMeters,
        topRadius: 0,
        bottomRadius: options.beamRadiusMeters,
        material: Color.CYAN.withAlpha(0.14),
        outline: true,
        outlineColor: Color.CYAN.withAlpha(0.32)
      }
    });
    cache.set(id, entity);
  }

  entity.position = new ConstantPositionProperty(satelliteCartesian(satellite));
}

export function pruneBeamEntities(
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
