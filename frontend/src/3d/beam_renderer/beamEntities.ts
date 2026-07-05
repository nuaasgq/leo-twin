import { Cartesian3, Color, ConstantPositionProperty, Entity, EntityCollection } from "cesium";

import { GroundUserState, SatelliteState, ScenarioConfig } from "../../core/event_types";
import { satelliteCartesian, Vector3Tuple } from "../cesium/positions";

const EARTH_RADIUS_M = 6_371_000;
const DEFAULT_BEAM_CELL_COUNT = 7;
const DEFAULT_BEAM_LENGTH_METERS = 600_000;
const DEFAULT_BEAM_RADIUS_METERS = 160_000;
const BEAM_CELL_SPACING_RATIO = 0.52;
const BEAM_CELL_RADIUS_RATIO = 0.34;
const SELECTED_COVERAGE_VISUAL_POLICY_V2_ID =
  "leo_twin.selected_coverage_visual_policy.v2";

export interface BeamRenderOptions {
  beamLengthMeters: number;
  beamRadiusMeters: number;
  beamCellCount: number;
  enabled: boolean;
}

export type BeamGeometryOptions = Omit<BeamRenderOptions, "enabled">;

export interface CoverageBeamDisplaySummary {
  footprintRadiusLabel: string;
  beamLengthLabel: string;
  beamCountLabel: string;
  beamPatternLabel: string;
  fidelityLabel: string;
  intersectionPolicyLabel: string;
  modelLabel: string;
  note: string;
}

export interface CoverageUserIntersectionSummary {
  totalUserCount: number;
  positionedUserCount: number;
  coveredUserCount: number;
  coveredUserIds: readonly string[];
  label: string;
  coveredUserLabel: string;
  note: string;
}

export interface SelectedCoverageVisualPolicyV2Summary {
  version: "v2";
  policy_id: string;
  selected_satellite_detail_mode: string;
  coverage_model: string;
  fidelity_level: string;
  beam_pattern: string;
  footprint_intersection_policy: string;
  beam_cell_count: number;
  beam_radius_m: number;
  beam_length_m: number;
  global_beam_render_limit: number;
  local_layer_enabled: boolean;
  excluded_physics: readonly string[];
  visual_only: true;
  no_access_semantics: true;
}

export interface SelectedCoverageVisualPolicyV2LayerSummary {
  label: string;
  value: string;
  detail: string;
}

export interface BeamCellFootprint {
  id: string;
  position: Vector3Tuple;
  radiusMeters: number;
  ring: number;
}

export interface CoverageFootprint {
  id: string;
  position: Vector3Tuple;
  radiusMeters: number;
}

export function selectedCoverageBeamSatellites(
  satellites: readonly SatelliteState[],
  selectedSatelliteId: string,
  renderLimit: number
): readonly SatelliteState[] {
  if (renderLimit <= 0 || satellites.length === 0 || selectedSatelliteId.length === 0) {
    return [];
  }
  const selected = satellites.find(
    (satellite) => satellite.satellite_id === selectedSatelliteId
  );
  return selected ? [selected] : [];
}

export function upsertBeamEntity(
  entities: EntityCollection,
  cache: Map<string, Entity>,
  satellite: SatelliteState,
  options: BeamRenderOptions
): readonly string[] {
  const id = `beam:${satellite.satellite_id}`;
  if (!options.enabled) {
    const existing = cache.get(id);
    if (existing) {
      entities.remove(existing);
      cache.delete(id);
    }
    return [];
  }

  const activeIds = [id];
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
  const footprint = buildCoverageFootprint(satellite, options.beamRadiusMeters);
  activeIds.push(footprint.id);
  upsertCoverageFootprintEntity(entities, cache, satellite, footprint);
  for (const cell of buildBeamCellFootprints(
    satellite,
    options.beamRadiusMeters,
    options.beamCellCount
  )) {
    activeIds.push(cell.id);
    upsertBeamCellEntity(entities, cache, satellite, cell);
  }
  return activeIds;
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

export function resolveBeamGeometryOptions(
  scenarioConfig: ScenarioConfig | null | undefined
): BeamGeometryOptions {
  const coverage = scenarioConfig?.backend_summary?.coverage_beam_summary;
  return {
    beamLengthMeters: positiveNumber(
      coverage?.beam_length_m,
      positiveNumber(scenarioConfig?.render?.beam_length_m, DEFAULT_BEAM_LENGTH_METERS)
    ),
    beamRadiusMeters: positiveNumber(
      coverage?.beam_radius_m,
      positiveNumber(scenarioConfig?.render?.beam_radius_m, DEFAULT_BEAM_RADIUS_METERS)
    ),
    beamCellCount: boundedInteger(
      coverage?.default_beam_count,
      DEFAULT_BEAM_CELL_COUNT,
      1,
      DEFAULT_BEAM_CELL_COUNT
    )
  };
}

export function coverageBeamDisplaySummary(
  scenarioConfig: ScenarioConfig | null | undefined
): CoverageBeamDisplaySummary {
  const geometry = resolveBeamGeometryOptions(scenarioConfig);
  const coverage = scenarioConfig?.backend_summary?.coverage_beam_summary;
  return {
    footprintRadiusLabel: `覆盖半径 ${formatKilometers(geometry.beamRadiusMeters)} km`,
    beamLengthLabel: `波束长度 ${formatKilometers(geometry.beamLengthMeters)} km`,
    beamCountLabel: `蜂窝波束 ${geometry.beamCellCount} 个`,
    beamPatternLabel: `波束模式 ${formatBeamPattern(coverage?.beam_pattern)}`,
    fidelityLabel: `覆盖保真 ${formatCoverageFidelityLevel(coverage?.fidelity_level)}`,
    intersectionPolicyLabel: `判定策略 ${formatCoverageIntersectionPolicy(
      coverage?.footprint_intersection_policy
    )}`,
    modelLabel: coverage?.coverage_model ?? "DETERMINISTIC_GEOMETRIC_FOOTPRINT",
    note:
      coverage?.model_note ??
      "确定性几何可视化足迹；未进行 RF 传播、天线方向图或链路预算仿真。"
  };
}

export function selectedCoverageVisualPolicyV2Summary(
  scenarioConfig: ScenarioConfig | null | undefined,
  localLayerEnabled = true
): SelectedCoverageVisualPolicyV2Summary {
  const coverage = scenarioConfig?.backend_summary?.coverage_beam_summary;
  const geometry = resolveBeamGeometryOptions(scenarioConfig);
  return {
    version: "v2",
    policy_id: SELECTED_COVERAGE_VISUAL_POLICY_V2_ID,
    selected_satellite_detail_mode:
      coverage?.selected_satellite_detail_mode ?? "SELECTED_SATELLITE_ONLY",
    coverage_model: coverage?.coverage_model ?? "DETERMINISTIC_GEOMETRIC_FOOTPRINT",
    fidelity_level: coverage?.fidelity_level ?? "DISPLAY_APPROXIMATION",
    beam_pattern:
      coverage?.beam_pattern ?? "CENTER_PLUS_HEX_RING_VISUAL_APPROXIMATION",
    footprint_intersection_policy:
      coverage?.footprint_intersection_policy ??
      "VISUAL_GEOMETRIC_CONTAINMENT_ONLY",
    beam_cell_count: geometry.beamCellCount,
    beam_radius_m: geometry.beamRadiusMeters,
    beam_length_m: geometry.beamLengthMeters,
    global_beam_render_limit: boundedInteger(
      coverage?.global_beam_render_limit,
      1,
      0,
      1
    ),
    local_layer_enabled: localLayerEnabled,
    excluded_physics: coverage?.excluded_physics ?? [
      "RF_PROPAGATION",
      "ANTENNA_PATTERN",
      "LINK_BUDGET",
      "INTERFERENCE"
    ],
    visual_only: true,
    no_access_semantics: true
  };
}

export function selectedCoverageVisualPolicyV2LayerSummary(
  scenarioConfig: ScenarioConfig | null | undefined,
  localLayerEnabled = true
): SelectedCoverageVisualPolicyV2LayerSummary {
  const summary = selectedCoverageVisualPolicyV2Summary(
    scenarioConfig,
    localLayerEnabled
  );
  return {
    label: "覆盖",
    value: `${localLayerEnabled ? "选中卫星" : "隐藏"} / ${summary.version}`,
    detail: `蜂窝 ${summary.beam_cell_count} / 半径 ${formatKilometers(
      summary.beam_radius_m
    )} km / RF排除 / 接入无语义`
  };
}

export function coverageUserIntersectionSummary(
  satellite: SatelliteState | null | undefined,
  users: readonly GroundUserState[],
  scenarioConfig: ScenarioConfig | null | undefined
): CoverageUserIntersectionSummary {
  const positionedUsers = users.filter((user) => user.position !== undefined);
  if (!satellite) {
    return coverageUserSummary(0, users.length, positionedUsers.length, []);
  }
  const footprint = buildCoverageFootprint(
    satellite,
    resolveBeamGeometryOptions(scenarioConfig).beamRadiusMeters
  );
  const coveredUserIds = positionedUsers
    .filter((user) =>
      user.position
        ? vectorDistance(geoPositionToEcef(user.position), footprint.position) <=
          footprint.radiusMeters
        : false
    )
    .map((user) => user.user_id)
    .sort();
  return coverageUserSummary(
    coveredUserIds.length,
    users.length,
    positionedUsers.length,
    coveredUserIds
  );
}

export function buildBeamCellFootprints(
  satellite: SatelliteState,
  beamRadiusMeters: number,
  cellCount = DEFAULT_BEAM_CELL_COUNT
): readonly BeamCellFootprint[] {
  const count = Math.max(1, Math.min(DEFAULT_BEAM_CELL_COUNT, Math.round(cellCount)));
  const radial = normalize(satellite.position);
  const tangent = tangentBasis(radial, satellite.velocity);
  const bitangent = normalize(cross(radial, tangent));
  const center = scale(radial, EARTH_RADIUS_M + 6_000);
  const spacing = Math.max(1, beamRadiusMeters * BEAM_CELL_SPACING_RATIO);
  const radius = Math.max(1, beamRadiusMeters * BEAM_CELL_RADIUS_RATIO);
  const cells: BeamCellFootprint[] = [
    {
      id: beamCellId(satellite.satellite_id, 0),
      position: center,
      radiusMeters: radius,
      ring: 0
    }
  ];
  for (let index = 1; index < count; index += 1) {
    const angle = ((index - 1) / 6) * Math.PI * 2;
    const localOffset = add(
      scale(tangent, Math.cos(angle) * spacing),
      scale(bitangent, Math.sin(angle) * spacing)
    );
    cells.push({
      id: beamCellId(satellite.satellite_id, index),
      position: add(center, localOffset),
      radiusMeters: radius,
      ring: 1
    });
  }
  return cells;
}

export function buildCoverageFootprint(
  satellite: SatelliteState,
  beamRadiusMeters: number
): CoverageFootprint {
  const radial = normalize(satellite.position);
  return {
    id: coverageFootprintId(satellite.satellite_id),
    position: scale(radial, EARTH_RADIUS_M + 4_500),
    radiusMeters: Math.max(1, beamRadiusMeters)
  };
}

function upsertCoverageFootprintEntity(
  entities: EntityCollection,
  cache: Map<string, Entity>,
  satellite: SatelliteState,
  footprint: CoverageFootprint
): void {
  let entity = cache.get(footprint.id);
  if (!entity) {
    entity = entities.add({
      id: footprint.id,
      name: `${satellite.satellite_id} coverage footprint`,
      ellipse: {
        semiMajorAxis: footprint.radiusMeters,
        semiMinorAxis: footprint.radiusMeters,
        height: 4_500,
        material: Color.fromCssColorString("#2ed7ff").withAlpha(0.08),
        outline: true,
        outlineColor: Color.fromCssColorString("#9bf4ff").withAlpha(0.62)
      }
    });
    cache.set(footprint.id, entity);
  }
  entity.position = new ConstantPositionProperty(
    Cartesian3.fromElements(
      footprint.position[0],
      footprint.position[1],
      footprint.position[2]
    )
  );
}

function upsertBeamCellEntity(
  entities: EntityCollection,
  cache: Map<string, Entity>,
  satellite: SatelliteState,
  cell: BeamCellFootprint
): void {
  let entity = cache.get(cell.id);
  if (!entity) {
    entity = entities.add({
      id: cell.id,
      name: `${satellite.satellite_id} beam cell ${cell.ring}`,
      ellipse: {
        semiMajorAxis: cell.radiusMeters,
        semiMinorAxis: cell.radiusMeters * 0.86,
        height: 5_000,
        material: Color.fromCssColorString("#44d7ff").withAlpha(
          cell.ring === 0 ? 0.2 : 0.12
        ),
        outline: true,
        outlineColor: Color.fromCssColorString("#dff9ff").withAlpha(0.48)
      }
    });
    cache.set(cell.id, entity);
  }
  entity.position = new ConstantPositionProperty(
    Cartesian3.fromElements(cell.position[0], cell.position[1], cell.position[2])
  );
}

function beamCellId(satelliteId: string, index: number): string {
  return `beam-cell:${satelliteId}:${index}`;
}

function coverageFootprintId(satelliteId: string): string {
  return `beam-footprint:${satelliteId}`;
}

function tangentBasis(radial: Vector3Tuple, velocity: Vector3Tuple | undefined): Vector3Tuple {
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

function scale(vector: Vector3Tuple, value: number): Vector3Tuple {
  return [vector[0] * value, vector[1] * value, vector[2] * value];
}

function add(left: Vector3Tuple, right: Vector3Tuple): Vector3Tuple {
  return [left[0] + right[0], left[1] + right[1], left[2] + right[2]];
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

function vectorDistance(left: Vector3Tuple, right: Vector3Tuple): number {
  return vectorLength([left[0] - right[0], left[1] - right[1], left[2] - right[2]]);
}

function geoPositionToEcef(position: GroundUserState["position"]): Vector3Tuple {
  if (!position) {
    return [0, 0, 0];
  }
  const longitude = (position[0] * Math.PI) / 180;
  const latitude = (position[1] * Math.PI) / 180;
  const radius = EARTH_RADIUS_M + (position[2] ?? 0);
  const cosLatitude = Math.cos(latitude);
  return [
    radius * cosLatitude * Math.cos(longitude),
    radius * cosLatitude * Math.sin(longitude),
    radius * Math.sin(latitude)
  ];
}

function coverageUserSummary(
  coveredUserCount: number,
  totalUserCount: number,
  positionedUserCount: number,
  coveredUserIds: readonly string[]
): CoverageUserIntersectionSummary {
  const preview = coveredUserIds.slice(0, 4).join("、");
  const remaining = Math.max(0, coveredUserIds.length - 4);
  return {
    totalUserCount,
    positionedUserCount,
    coveredUserCount,
    coveredUserIds,
    label: `覆盖内用户 ${coveredUserCount}/${positionedUserCount}`,
    coveredUserLabel:
      coveredUserIds.length === 0
        ? "覆盖用户 暂无"
        : `覆盖用户 ${preview}${remaining > 0 ? ` 等 ${coveredUserIds.length} 个` : ""}`,
    note: `基于 ${totalUserCount} 个地面用户中的 ${positionedUserCount} 个定位用户做几何足迹包含统计；不是 RF 覆盖或接入判定。`
  };
}

function positiveNumber(value: number | undefined, fallback: number): number {
  return value !== undefined && Number.isFinite(value) && value > 0 ? value : fallback;
}

function boundedInteger(
  value: number | undefined,
  fallback: number,
  min: number,
  max: number
): number {
  if (value === undefined || !Number.isFinite(value)) {
    return fallback;
  }
  return Math.max(min, Math.min(max, Math.round(value)));
}

function formatKilometers(valueMeters: number): string {
  return (valueMeters / 1000).toLocaleString("zh-CN", {
    maximumFractionDigits: 1,
    minimumFractionDigits: 0
  });
}

function formatBeamPattern(value: string | undefined): string {
  if (value === "CENTER_PLUS_HEX_RING_VISUAL_APPROXIMATION") {
    return "中心 + 六邻区蜂窝";
  }
  return value ?? "中心 + 六邻区蜂窝";
}

function formatCoverageFidelityLevel(value: string | undefined): string {
  if (value === "DISPLAY_APPROXIMATION") {
    return "显示近似";
  }
  return value ?? "显示近似";
}

function formatCoverageIntersectionPolicy(value: string | undefined): string {
  if (value === "VISUAL_GEOMETRIC_CONTAINMENT_ONLY") {
    return "仅视觉几何包含";
  }
  return value ?? "仅视觉几何包含";
}
