import { Cartesian3 } from "cesium";

import { GroundUserState, SatelliteState } from "../../core/event_types";

export type RenderNode = SatelliteState | GroundUserState;
export type Vector3Tuple = readonly [number, number, number];

export function satelliteCartesian(state: SatelliteState): Cartesian3 {
  return Cartesian3.fromElements(state.position[0], state.position[1], state.position[2]);
}

export function projectSatelliteState(
  state: SatelliteState,
  displaySimTime: number,
  maxProjectionSeconds = 180
): SatelliteState {
  if (!state.velocity) {
    return state;
  }
  const deltaSeconds = Math.min(
    Math.max(0, displaySimTime - state.sim_time),
    Math.max(0, maxProjectionSeconds)
  );
  if (deltaSeconds <= 0) {
    return state;
  }
  return {
    ...state,
    sim_time: Math.max(state.sim_time, displaySimTime),
    position: [
      state.position[0] + state.velocity[0] * deltaSeconds,
      state.position[1] + state.velocity[1] * deltaSeconds,
      state.position[2] + state.velocity[2] * deltaSeconds
    ]
  };
}

export function projectSatelliteStates(
  states: readonly SatelliteState[],
  displaySimTime: number
): readonly SatelliteState[] {
  return states.map((state) => projectSatelliteState(state, displaySimTime));
}

export function satelliteMotionProjectionLabel(
  displaySimTime: number,
  snapshotSimTime: number
): string {
  const deltaSeconds = Math.max(0, displaySimTime - snapshotSimTime);
  if (deltaSeconds < 0.05) {
    return "快照同步";
  }
  return `显示外推 +${formatProjectionSeconds(deltaSeconds)}秒`;
}

export function satelliteOrbitCartesianSamples(
  state: SatelliteState,
  sampleCount = 96
): readonly Cartesian3[] {
  return buildOrbitTrackSamples(state, sampleCount).map((position) =>
    Cartesian3.fromElements(position[0], position[1], position[2])
  );
}

export function buildOrbitTrackSamples(
  state: SatelliteState,
  sampleCount = 96
): readonly Vector3Tuple[] {
  const radius = vectorLength(state.position);
  const boundedSampleCount = Math.max(8, Math.round(sampleCount));
  if (!Number.isFinite(radius) || radius <= 0) {
    return [];
  }

  const radial = normalize(state.position);
  const tangent = tangentBasis(radial, state.velocity);
  const samples: Vector3Tuple[] = [];

  for (let index = 0; index < boundedSampleCount; index += 1) {
    const angle = (Math.PI * 2 * index) / boundedSampleCount;
    const cos = Math.cos(angle);
    const sin = Math.sin(angle);
    samples.push([
      radius * (radial[0] * cos + tangent[0] * sin),
      radius * (radial[1] * cos + tangent[1] * sin),
      radius * (radial[2] * cos + tangent[2] * sin)
    ]);
  }

  samples.push(samples[0]);
  return samples;
}

export function groundUserCartesian(state: GroundUserState): Cartesian3 | null {
  if (!state.position) {
    return null;
  }
  const [longitude, latitude, height = 0] = state.position;
  return Cartesian3.fromDegrees(longitude, latitude, height);
}

export function nodeCartesian(node: RenderNode): Cartesian3 | null {
  if ("satellite_id" in node) {
    return satelliteCartesian(node);
  }
  return groundUserCartesian(node);
}

function tangentBasis(
  radial: Vector3Tuple,
  velocity: Vector3Tuple | undefined
): Vector3Tuple {
  if (velocity !== undefined) {
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

function formatProjectionSeconds(value: number): string {
  return value.toLocaleString("zh-CN", {
    maximumFractionDigits: 1,
    minimumFractionDigits: 0
  });
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
