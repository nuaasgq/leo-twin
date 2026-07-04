import {
  Cartesian3,
  Color,
  ConstantPositionProperty,
  DistanceDisplayCondition,
  Entity,
  EntityCollection
} from "cesium";

import { SatelliteState } from "../../core/event_types";
import { Vector3Tuple } from "../cesium/positions";

const MODEL_DISPLAY_DISTANCE = new DistanceDisplayCondition(0, 22_000_000);
const BUS_DIMENSIONS = new Cartesian3(120_000, 72_000, 72_000);
const PANEL_DIMENSIONS = new Cartesian3(168_000, 9_000, 88_000);
const SENSOR_RADII = new Cartesian3(38_000, 38_000, 22_000);

export type SatelliteModelPartKind =
  | "bus"
  | "panel-left"
  | "panel-right"
  | "antenna"
  | "sensor";

export interface SatelliteModelPart {
  id: string;
  kind: SatelliteModelPartKind;
  position: Vector3Tuple;
}

export function buildSatelliteModelParts(
  satellite: SatelliteState
): readonly SatelliteModelPart[] {
  const radial = normalize(satellite.position);
  const tangent = tangentBasis(radial, satellite.velocity);
  const panelAxis = normalize(cross(radial, tangent));
  const center = satellite.position;

  return [
    {
      id: satelliteModelPartId(satellite.satellite_id, "bus"),
      kind: "bus",
      position: center
    },
    {
      id: satelliteModelPartId(satellite.satellite_id, "panel-left"),
      kind: "panel-left",
      position: offset(center, panelAxis, -126_000)
    },
    {
      id: satelliteModelPartId(satellite.satellite_id, "panel-right"),
      kind: "panel-right",
      position: offset(center, panelAxis, 126_000)
    },
    {
      id: satelliteModelPartId(satellite.satellite_id, "antenna"),
      kind: "antenna",
      position: offset(center, radial, 82_000)
    },
    {
      id: satelliteModelPartId(satellite.satellite_id, "sensor"),
      kind: "sensor",
      position: offset(center, radial, -66_000)
    }
  ];
}

export function satelliteModelEntityIds(satellite: SatelliteState): readonly string[] {
  return buildSatelliteModelParts(satellite).map((part) => part.id);
}

export function upsertSatelliteModelEntities(
  entities: EntityCollection,
  cache: Map<string, Entity>,
  satellite: SatelliteState
): readonly string[] {
  const active = satellite.status.toLowerCase() !== "offline";
  const activeIds: string[] = [];
  for (const part of buildSatelliteModelParts(satellite)) {
    activeIds.push(part.id);
    const position = Cartesian3.fromElements(
      part.position[0],
      part.position[1],
      part.position[2]
    );
    let entity = cache.get(part.id);
    if (!entity) {
      entity = entities.add(satelliteModelEntityOptions(satellite, part, position));
      cache.set(part.id, entity);
    }
    entity.position = new ConstantPositionProperty(position);
    entity.show = active || part.kind === "bus";
  }
  return activeIds;
}

function satelliteModelEntityOptions(
  satellite: SatelliteState,
  part: SatelliteModelPart,
  position: Cartesian3
): Entity.ConstructorOptions {
  const name = `${satellite.satellite_id} ${part.kind}`;
  switch (part.kind) {
    case "panel-left":
    case "panel-right":
      return {
        id: part.id,
        name,
        position,
        box: {
          dimensions: PANEL_DIMENSIONS,
          material: Color.fromCssColorString("#143d77").withAlpha(0.92),
          outline: true,
          outlineColor: Color.fromCssColorString("#9be7ff"),
          distanceDisplayCondition: MODEL_DISPLAY_DISTANCE
        }
      };
    case "antenna":
      return {
        id: part.id,
        name,
        position,
        cylinder: {
          length: 58_000,
          topRadius: 5_000,
          bottomRadius: 24_000,
          material: Color.fromCssColorString("#f0d27a").withAlpha(0.9),
          outline: true,
          outlineColor: Color.fromCssColorString("#fff0b8"),
          distanceDisplayCondition: MODEL_DISPLAY_DISTANCE
        }
      };
    case "sensor":
      return {
        id: part.id,
        name,
        position,
        ellipsoid: {
          radii: SENSOR_RADII,
          material: Color.fromCssColorString("#79f2ff").withAlpha(0.62),
          outline: true,
          outlineColor: Color.fromCssColorString("#e5feff"),
          distanceDisplayCondition: MODEL_DISPLAY_DISTANCE
        }
      };
    case "bus":
    default:
      return {
        id: part.id,
        name,
        position,
        box: {
          dimensions: BUS_DIMENSIONS,
          material: Color.fromCssColorString("#dfe8ed").withAlpha(0.94),
          outline: true,
          outlineColor: Color.fromCssColorString("#ffffff"),
          distanceDisplayCondition: MODEL_DISPLAY_DISTANCE
        }
      };
  }
}

function satelliteModelPartId(
  satelliteId: string,
  kind: SatelliteModelPartKind
): string {
  return `satellite-model:${satelliteId}:${kind}`;
}

function tangentBasis(
  radial: Vector3Tuple,
  velocity: Vector3Tuple | undefined
): Vector3Tuple {
  if (velocity) {
    const projection = dot(velocity, radial);
    const tangent: Vector3Tuple = [
      velocity[0] - projection * radial[0],
      velocity[1] - projection * radial[1],
      velocity[2] - projection * radial[2]
    ];
    if (vectorLength(tangent) > 0) {
      return normalize(tangent);
    }
  }

  const reference: Vector3Tuple = Math.abs(radial[2]) < 0.9 ? [0, 0, 1] : [0, 1, 0];
  return normalize(cross(reference, radial));
}

function offset(
  origin: Vector3Tuple,
  axis: Vector3Tuple,
  distanceMeters: number
): Vector3Tuple {
  return [
    origin[0] + axis[0] * distanceMeters,
    origin[1] + axis[1] * distanceMeters,
    origin[2] + axis[2] * distanceMeters
  ];
}

function normalize(vector: Vector3Tuple): Vector3Tuple {
  const length = vectorLength(vector);
  if (length <= 0) {
    return [1, 0, 0];
  }
  return [vector[0] / length, vector[1] / length, vector[2] / length];
}

function vectorLength(vector: Vector3Tuple): number {
  return Math.hypot(vector[0], vector[1], vector[2]);
}

function dot(left: Vector3Tuple, right: Vector3Tuple): number {
  return left[0] * right[0] + left[1] * right[1] + left[2] * right[2];
}

function cross(left: Vector3Tuple, right: Vector3Tuple): Vector3Tuple {
  return [
    left[1] * right[2] - left[2] * right[1],
    left[2] * right[0] - left[0] * right[2],
    left[0] * right[1] - left[1] * right[0]
  ];
}
