import { SatelliteState } from "../../core/event_types";

const EARTH_RADIUS_M = 6_371_000;

export type GlobeCameraMode = "EARTH" | "SATELLITE";

export interface SatelliteInsetPoint {
  satelliteId: string;
  simTime: number;
  x: number;
  y: number;
}

export function selectedDisplaySatellite(
  satellites: readonly SatelliteState[],
  selectedSatelliteId: string
): SatelliteState | null {
  if (satellites.length === 0) {
    return null;
  }
  return (
    satellites.find((satellite) => satellite.satellite_id === selectedSatelliteId) ??
    satellites[0]
  );
}

export function appendSatelliteInsetTrail(
  currentTrail: readonly SatelliteInsetPoint[],
  satellite: SatelliteState | null,
  maxPoints = 28
): readonly SatelliteInsetPoint[] {
  if (!satellite) {
    return [];
  }
  const nextPoint = satelliteInsetPoint(satellite);
  const previousPoint = currentTrail[currentTrail.length - 1];
  const retainedTrail =
    previousPoint?.satelliteId === satellite.satellite_id ? currentTrail : [];
  if (
    previousPoint?.satelliteId === satellite.satellite_id &&
    previousPoint.simTime === nextPoint.simTime &&
    previousPoint.x === nextPoint.x &&
    previousPoint.y === nextPoint.y
  ) {
    return currentTrail;
  }
  return [...retainedTrail, nextPoint].slice(-Math.max(2, maxPoints));
}

export function satelliteInsetPoint(satellite: SatelliteState): SatelliteInsetPoint {
  const [x, y, z] = satellite.position;
  const radius = Math.hypot(x, y, z);
  if (!Number.isFinite(radius) || radius <= 0) {
    return {
      satelliteId: satellite.satellite_id,
      simTime: satellite.sim_time,
      x: 50,
      y: 50
    };
  }
  const longitude = Math.atan2(y, x);
  const latitude = Math.asin(z / radius);
  return {
    satelliteId: satellite.satellite_id,
    simTime: satellite.sim_time,
    x: clamp(8 + ((longitude + Math.PI) / (Math.PI * 2)) * 84, 8, 92),
    y: clamp(8 + (0.5 - latitude / Math.PI) * 84, 8, 92)
  };
}

export function satelliteAltitudeKm(satellite: SatelliteState): number {
  const radius = Math.hypot(
    satellite.position[0],
    satellite.position[1],
    satellite.position[2]
  );
  if (!Number.isFinite(radius)) {
    return 0;
  }
  return Math.max(0, (radius - EARTH_RADIUS_M) / 1000);
}

function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}
