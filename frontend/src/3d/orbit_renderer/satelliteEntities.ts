import {
  Cartesian2,
  Color,
  ConstantPositionProperty,
  ConstantProperty,
  Entity,
  EntityCollection,
  LabelStyle,
  PointPrimitive,
  PointPrimitiveCollection,
  PolylineGlowMaterialProperty,
  VerticalOrigin
} from "cesium";

import { SatelliteState } from "../../core/event_types";
import {
  satelliteCartesian,
  satelliteOrbitCartesianSamples
} from "../cesium/positions";

const DEPTH_TEST_DISABLE_DISTANCE = 1_000_000_000_000;
const SATELLITE_ICON_DATA_URI = `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(`
<svg xmlns="http://www.w3.org/2000/svg" width="72" height="72" viewBox="0 0 72 72">
  <defs>
    <filter id="glow" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="2" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
  <g fill="none" stroke-linecap="round" stroke-linejoin="round" filter="url(#glow)">
    <path d="M31 27h10l6 8-6 8H31l-6-8 6-8z" fill="#112d36" stroke="#dbfbff" stroke-width="3"/>
    <path d="M23 30 15 24M23 40 15 48M49 30l8-6M49 40l8 8" stroke="#9bf7ff" stroke-width="3"/>
    <rect x="5" y="16" width="16" height="11" rx="2" fill="#207d91" stroke="#dbfbff" stroke-width="2"/>
    <rect x="5" y="45" width="16" height="11" rx="2" fill="#207d91" stroke="#dbfbff" stroke-width="2"/>
    <rect x="51" y="16" width="16" height="11" rx="2" fill="#207d91" stroke="#dbfbff" stroke-width="2"/>
    <rect x="51" y="45" width="16" height="11" rx="2" fill="#207d91" stroke="#dbfbff" stroke-width="2"/>
    <circle cx="36" cy="35" r="2.8" fill="#9bffcb"/>
  </g>
</svg>
`)}`;

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

export function upsertSatelliteIconEntity(
  entities: EntityCollection,
  cache: Map<string, Entity>,
  satellite: SatelliteState
): void {
  const id = `satellite-icon:${satellite.satellite_id}`;
  const position = satelliteCartesian(satellite);
  const active = satellite.status.toLowerCase() !== "offline";
  let entity = cache.get(id);
  if (!entity) {
    entity = entities.add({
      id,
      name: satellite.satellite_id,
      position,
      billboard: {
        image: SATELLITE_ICON_DATA_URI,
        scale: 0.36,
        verticalOrigin: VerticalOrigin.CENTER,
        disableDepthTestDistance: DEPTH_TEST_DISABLE_DISTANCE
      },
      label: {
        text: satellite.satellite_id,
        font: "11px sans-serif",
        fillColor: active ? Color.WHITE : Color.LIGHTGRAY,
        outlineColor: Color.BLACK,
        outlineWidth: 2,
        style: LabelStyle.FILL_AND_OUTLINE,
        verticalOrigin: VerticalOrigin.TOP,
        pixelOffset: new Cartesian2(0, 18),
        disableDepthTestDistance: DEPTH_TEST_DISABLE_DISTANCE
      }
    });
    cache.set(id, entity);
  }
  entity.position = new ConstantPositionProperty(position);
  if (entity.billboard) {
    entity.billboard.scale = new ConstantProperty(active ? 0.36 : 0.28);
  }
  if (entity.label) {
    entity.label.fillColor = new ConstantProperty(active ? Color.WHITE : Color.LIGHTGRAY);
  }
}

export function upsertSatelliteOrbitEntity(
  entities: EntityCollection,
  cache: Map<string, Entity>,
  satellite: SatelliteState
): void {
  const id = `satellite-orbit:${satellite.satellite_id}`;
  const positions = satelliteOrbitCartesianSamples(satellite, 128);
  if (positions.length < 2) {
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
      name: `${satellite.satellite_id} orbit`,
      polyline: {
        width: 1.5,
        material: new PolylineGlowMaterialProperty({
          color: Color.fromCssColorString("#67d7ff").withAlpha(0.34),
          glowPower: 0.12
        })
      }
    });
    cache.set(id, entity);
  }
  if (entity.polyline) {
    entity.polyline.positions = new ConstantProperty(positions);
  }
}
