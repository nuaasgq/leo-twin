import { Cartesian3 } from "cesium";

import { GroundUserState, SatelliteState } from "../../core/event_types";

export type RenderNode = SatelliteState | GroundUserState;

export function satelliteCartesian(state: SatelliteState): Cartesian3 {
  return Cartesian3.fromElements(state.position[0], state.position[1], state.position[2]);
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
