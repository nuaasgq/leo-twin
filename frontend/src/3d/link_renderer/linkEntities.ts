import {
  Cartesian3,
  Color,
  ColorMaterialProperty,
  ConstantProperty,
  Entity,
  EntityCollection,
  PolylineGlowMaterialProperty
} from "cesium";

import { GroundUserState, LinkState, Route, SatelliteState } from "../../core/event_types";
import { groundUserCartesian, satelliteCartesian } from "../cesium/positions";

export interface NodeIndex {
  satellites: ReadonlyMap<string, SatelliteState>;
  groundUsers: ReadonlyMap<string, GroundUserState>;
}

export function upsertLinkEntity(
  entities: EntityCollection,
  cache: Map<string, Entity>,
  link: LinkState,
  nodes: NodeIndex
): void {
  const source = nodePosition(link.source_id, nodes);
  const target = nodePosition(link.target_id, nodes);
  const id = `link:${link.source_id}->${link.target_id}`;
  if (!source || !target || !link.availability) {
    removeEntity(entities, cache, id);
    return;
  }

  let entity = cache.get(id);
  if (!entity) {
    entity = entities.add({
      id,
      name: id,
      polyline: {
        width: 2,
        material: Color.LIME.withAlpha(0.34)
      }
    });
    cache.set(id, entity);
  }
  if (entity.polyline) {
    const highUtilization = (link.utilization ?? 0) > 0.8;
    entity.polyline.positions = new ConstantProperty([source, target]);
    entity.polyline.material = new ColorMaterialProperty(
      Color.LIME.withAlpha(highUtilization ? 0.78 : 0.34)
    );
  }
}

export function upsertRouteEntity(
  entities: EntityCollection,
  cache: Map<string, Entity>,
  route: Route,
  nodes: NodeIndex
): void {
  const id = `route:${route.route_id}`;
  if (!route.available) {
    removeEntity(entities, cache, id);
    return;
  }
  const positions = route.path
    .map((nodeId) => nodePosition(nodeId, nodes))
    .filter((position): position is Cartesian3 => position !== null);
  if (positions.length < 2) {
    removeEntity(entities, cache, id);
    return;
  }

  let entity = cache.get(id);
  if (!entity) {
    entity = entities.add({
      id,
      name: route.route_id,
      polyline: {
        width: 5,
        material: new PolylineGlowMaterialProperty({
          color: Color.YELLOW.withAlpha(0.86),
          glowPower: 0.18
        })
      }
    });
    cache.set(id, entity);
  }
  if (entity.polyline) {
    entity.polyline.positions = new ConstantProperty(positions);
  }
}

export function pruneEntities(
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

function nodePosition(nodeId: string, nodes: NodeIndex) {
  const satellite = nodes.satellites.get(nodeId);
  if (satellite) {
    return satelliteCartesian(satellite);
  }
  const user = nodes.groundUsers.get(nodeId);
  return user ? groundUserCartesian(user) : null;
}

function removeEntity(
  entities: EntityCollection,
  cache: Map<string, Entity>,
  id: string
): void {
  const entity = cache.get(id);
  if (entity) {
    entities.remove(entity);
    cache.delete(id);
  }
}
