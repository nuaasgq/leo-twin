import { SatelliteState } from "../../core/event_types";

const EARTH_RADIUS_M = 6_371_000;

export type GlobeCameraMode = "EARTH" | "SATELLITE";

export interface SatelliteInsetPoint {
  satelliteId: string;
  simTime: number;
  x: number;
  y: number;
}

export interface SatelliteComputeSummary {
  capacityLabel: string;
  availableLabel: string;
  utilizationLabel: string;
  statusLabel: string;
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
  const velocityMagnitude = satellite.velocity
    ? Math.hypot(satellite.velocity[0], satellite.velocity[1], satellite.velocity[2])
    : 0;
  const phaseDrift =
    Number.isFinite(velocityMagnitude) && velocityMagnitude > 0
      ? satellite.sim_time * (velocityMagnitude / radius)
      : 0;
  const phase = Math.atan2(y, x) + phaseDrift;
  const inclinationOffset = clamp(z / radius, -1, 1) * 8;
  return {
    satelliteId: satellite.satellite_id,
    simTime: satellite.sim_time,
    x: clamp(50 + Math.cos(phase) * 34, 8, 92),
    y: clamp(50 + Math.sin(phase) * 24 - inclinationOffset, 8, 92)
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

export function satelliteComputeSummary(
  node:
    | {
        capacity: number;
        available_capacity: number;
        load_ratio?: number;
        status: string;
      }
    | null
    | undefined
): SatelliteComputeSummary | null {
  if (!node) {
    return null;
  }
  const capacity = Math.max(0, finiteNumber(node.capacity));
  const available = Math.max(0, Math.min(capacity, finiteNumber(node.available_capacity)));
  const utilization =
    node.load_ratio !== undefined
      ? clamp(finiteNumber(node.load_ratio), 0, 1)
      : capacity <= 0
        ? 0
        : clamp((capacity - available) / capacity, 0, 1);
  return {
    capacityLabel: `${formatNumber(capacity)} GFLOPS FP32`,
    availableLabel: `${formatNumber(available)} GFLOPS`,
    utilizationLabel: `${formatNumber(utilization * 100)}%`,
    statusLabel: node.status
  };
}

function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}

function finiteNumber(value: number): number {
  return Number.isFinite(value) ? value : 0;
}

function formatNumber(value: number): string {
  return value.toLocaleString("zh-CN", {
    maximumFractionDigits: 1,
    minimumFractionDigits: 0
  });
}
