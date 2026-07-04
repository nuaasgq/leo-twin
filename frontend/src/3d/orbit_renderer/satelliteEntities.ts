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

export const SATELLITE_DEPTH_TEST_DISABLE_DISTANCE = 0;
export const SATELLITE_ICON_DATA_URI = `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(`
<svg xmlns="http://www.w3.org/2000/svg" width="96" height="72" viewBox="0 0 96 72">
  <defs>
    <filter id="glow" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="2" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    <linearGradient id="panel" x1="0" x2="1" y1="0" y2="1">
      <stop offset="0" stop-color="#58d8ff"/>
      <stop offset="0.48" stop-color="#145ba8"/>
      <stop offset="1" stop-color="#062b66"/>
    </linearGradient>
    <linearGradient id="bus" x1="0" x2="1" y1="0" y2="1">
      <stop offset="0" stop-color="#ffffff"/>
      <stop offset="0.55" stop-color="#a9b9c0"/>
      <stop offset="1" stop-color="#52666f"/>
    </linearGradient>
  </defs>
  <g fill="none" stroke-linecap="round" stroke-linejoin="round" filter="url(#glow)" transform="rotate(-12 48 36)">
    <path d="M20 28h20M56 28h20M20 44h20M56 44h20" stroke="#bff7ff" stroke-width="3"/>
    <rect x="5" y="18" width="30" height="18" rx="2" fill="url(#panel)" stroke="#d7fbff" stroke-width="2"/>
    <path d="M15 18v18M25 18v18" stroke="#8cecff" stroke-width="1.2" opacity=".85"/>
    <rect x="61" y="18" width="30" height="18" rx="2" fill="url(#panel)" stroke="#d7fbff" stroke-width="2"/>
    <path d="M71 18v18M81 18v18" stroke="#8cecff" stroke-width="1.2" opacity=".85"/>
    <rect x="5" y="38" width="30" height="18" rx="2" fill="url(#panel)" stroke="#d7fbff" stroke-width="2"/>
    <path d="M15 38v18M25 38v18" stroke="#8cecff" stroke-width="1.2" opacity=".85"/>
    <rect x="61" y="38" width="30" height="18" rx="2" fill="url(#panel)" stroke="#d7fbff" stroke-width="2"/>
    <path d="M71 38v18M81 38v18" stroke="#8cecff" stroke-width="1.2" opacity=".85"/>
    <path d="M42 24h12l8 12-8 12H42l-8-12 8-12z" fill="url(#bus)" stroke="#ffffff" stroke-width="2.4"/>
    <circle cx="48" cy="36" r="4" fill="#84f6ff" stroke="#e8feff" stroke-width="1.4"/>
    <g id="antenna">
      <path d="M54 24l9-10M57 29l12-3M54 48l10 9" stroke="#ffe59c" stroke-width="2.3"/>
      <circle cx="64" cy="13" r="3.2" fill="#ffe59c" stroke="#fff7d6" stroke-width="1.4"/>
    </g>
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
    const color = active
      ? Color.fromCssColorString("#7cefff").withAlpha(0.28)
      : Color.GRAY.withAlpha(0.22);
    let point = this.pointsBySatelliteId.get(satellite.satellite_id);
    if (!point) {
      point = this.collection.add({
        id: satellite.satellite_id,
        position: satelliteCartesian(satellite),
        pixelSize: active ? 6 : 4,
        color,
        outlineColor: Color.BLACK,
        outlineWidth: 1,
        disableDepthTestDistance: SATELLITE_DEPTH_TEST_DISABLE_DISTANCE
      });
      this.pointsBySatelliteId.set(satellite.satellite_id, point);
      return;
    }
    point.position = satelliteCartesian(satellite);
    point.color = color;
    point.pixelSize = active ? 6 : 4;
    point.disableDepthTestDistance = SATELLITE_DEPTH_TEST_DISABLE_DISTANCE;
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
        scale: 0.58,
        verticalOrigin: VerticalOrigin.CENTER,
        disableDepthTestDistance: SATELLITE_DEPTH_TEST_DISABLE_DISTANCE
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
        disableDepthTestDistance: SATELLITE_DEPTH_TEST_DISABLE_DISTANCE
      }
    });
    cache.set(id, entity);
  }
  entity.position = new ConstantPositionProperty(position);
  if (entity.billboard) {
    entity.billboard.scale = new ConstantProperty(active ? 0.58 : 0.42);
    entity.billboard.disableDepthTestDistance = new ConstantProperty(
      SATELLITE_DEPTH_TEST_DISABLE_DISTANCE
    );
  }
  if (entity.label) {
    entity.label.fillColor = new ConstantProperty(active ? Color.WHITE : Color.LIGHTGRAY);
    entity.label.disableDepthTestDistance = new ConstantProperty(
      SATELLITE_DEPTH_TEST_DISABLE_DISTANCE
    );
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
