import {
  Cartesian2,
  Cartesian3,
  Color,
  ConstantPositionProperty,
  Entity,
  EntityCollection,
  HeadingPitchRange,
  ImageryLayer,
  LabelStyle,
  Math as CesiumMath,
  Matrix4,
  PointPrimitiveCollection,
  TileMapServiceImageryProvider,
  VerticalOrigin,
  Viewer,
  buildModuleUrl
} from "cesium";
import "cesium/Build/Cesium/Widgets/widgets.css";
import { useEffect, useMemo, useRef, useState } from "react";

import { SatelliteState } from "../../core/event_types";
import { WorldSnapshot } from "../../state/snapshot_engine";
import {
  pruneBeamEntities,
  selectedCoverageBeamSatellites,
  upsertBeamEntity
} from "../beam_renderer/beamEntities";
import {
  NATURAL_EARTH_COUNTRY_SOURCE_URI,
  NaturalEarthCountryFeatureCollection,
  clearCountryOverlays,
  installCountryOverlays,
  installNaturalEarthCountryOverlays
} from "./countryOverlays";
import { groundUserCartesian, projectSatelliteStates } from "./positions";
import {
  pruneEntities,
  upsertLinkEntity,
  upsertRouteEntity
} from "../link_renderer/linkEntities";
import {
  upsertSatelliteModelEntities
} from "../orbit_renderer/satelliteModelEntities";
import {
  SatellitePrimitiveBatch,
  upsertSatelliteIconEntity,
  upsertSatelliteOrbitEntity
} from "../orbit_renderer/satelliteEntities";
import { visualLayerLimits } from "./renderLimits";
import {
  GlobeCameraMode,
  SatelliteInsetPoint,
  appendSatelliteInsetTrail,
  satelliteAltitudeKm,
  satelliteComputeSummary,
  selectedDisplaySatellite
} from "./satelliteFollow";

export interface CesiumGlobeProps {
  snapshot: WorldSnapshot;
  displaySimTime: number;
}

export function CesiumGlobe({ snapshot, displaySimTime }: CesiumGlobeProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const viewerRef = useRef<Viewer | null>(null);
  const latestSnapshotRef = useRef(snapshot);
  const satelliteBatchRef = useRef<SatellitePrimitiveBatch | null>(null);
  const beamCache = useRef(new Map<string, Entity>());
  const satelliteIconCache = useRef(new Map<string, Entity>());
  const satelliteModelCache = useRef(new Map<string, Entity>());
  const orbitTrackCache = useRef(new Map<string, Entity>());
  const countryOverlayCache = useRef(new Map<string, Entity>());
  const userCache = useRef(new Map<string, Entity>());
  const linkCache = useRef(new Map<string, Entity>());
  const routeCache = useRef(new Map<string, Entity>());
  const hasFocusedSatellites = useRef(false);
  const lastRenderedFrame = useRef("");
  const [renderError, setRenderError] = useState<string | null>(null);
  const [cameraMode, setCameraMode] = useState<GlobeCameraMode>("EARTH");
  const [selectedSatelliteId, setSelectedSatelliteId] = useState("");
  const [selectedTrail, setSelectedTrail] = useState<readonly SatelliteInsetPoint[]>([]);
  const displaySatellites = useMemo(
    () => projectSatelliteStates(snapshot.satellites, displaySimTime),
    [snapshot.satellites, displaySimTime]
  );
  const selectableSatellites = useMemo(
    () => displaySatellites.slice(0, 96),
    [displaySatellites]
  );
  const selectedSatellite = useMemo(
    () => selectedDisplaySatellite(selectableSatellites, selectedSatelliteId),
    [selectableSatellites, selectedSatelliteId]
  );
  const activeSelectedSatelliteId = selectedSatellite?.satellite_id ?? "";
  const selectedComputeNode = useMemo(
    () =>
      activeSelectedSatelliteId
        ? snapshot.compute_nodes.find((node) => node.node_id === activeSelectedSatelliteId) ??
          null
        : null,
    [activeSelectedSatelliteId, snapshot.compute_nodes]
  );

  useEffect(() => {
    latestSnapshotRef.current = snapshot;
  }, [snapshot]);

  useEffect(() => {
    if (!containerRef.current) {
      return;
    }
    let viewer: Viewer;
    let disposed = false;
    try {
      viewer = new Viewer(containerRef.current, {
        animation: false,
        timeline: false,
        geocoder: false,
        homeButton: false,
        sceneModePicker: false,
        baseLayer: ImageryLayer.fromProviderAsync(
          TileMapServiceImageryProvider.fromUrl(
            buildModuleUrl("Assets/Textures/NaturalEarthII")
          )
        ),
        baseLayerPicker: false,
        navigationHelpButton: false,
        fullscreenButton: false,
        infoBox: false,
        selectionIndicator: false,
        shouldAnimate: false,
        requestRenderMode: true,
        maximumRenderTimeChange: Number.POSITIVE_INFINITY
      });
    } catch (error) {
      setRenderError(renderErrorMessage(error));
      return;
    }
    viewer.scene.backgroundColor = Color.BLACK;
    viewer.scene.globe.baseColor = Color.fromCssColorString("#07141d");
    viewer.scene.globe.depthTestAgainstTerrain = true;
    viewer.scene.globe.showGroundAtmosphere = true;
    if (viewer.scene.skyAtmosphere) {
      viewer.scene.skyAtmosphere.show = true;
    }
    installCountryOverlays(viewer.entities, countryOverlayCache.current);
    void loadNaturalEarthCountryOverlays(
      viewer,
      countryOverlayCache.current,
      () => disposed
    );
    focusEarthOverview(viewer);
    const handleContextLost = (event: Event) => {
      event.preventDefault();
      setRenderError("WebGL context lost");
    };
    viewer.scene.canvas.addEventListener("webglcontextlost", handleContextLost);
    const satellitePrimitives = viewer.scene.primitives.add(
      new PointPrimitiveCollection()
    ) as PointPrimitiveCollection;
    const satelliteBatch = new SatellitePrimitiveBatch(satellitePrimitives);
    satelliteBatchRef.current = satelliteBatch;
    viewerRef.current = viewer;

    return () => {
      disposed = true;
      if (!viewer.isDestroyed()) {
        viewer.scene.canvas.removeEventListener("webglcontextlost", handleContextLost);
        satelliteBatch.clear();
        viewer.scene.primitives.remove(satellitePrimitives);
      }
      satelliteBatchRef.current = null;
      satelliteIconCache.current.clear();
      satelliteModelCache.current.clear();
      orbitTrackCache.current.clear();
      countryOverlayCache.current.clear();
      beamCache.current.clear();
      userCache.current.clear();
      linkCache.current.clear();
      routeCache.current.clear();
      if (!viewer.isDestroyed()) {
        viewer.destroy();
      }
      viewerRef.current = null;
    };
  }, []);

  useEffect(() => {
    const viewer = viewerRef.current;
    const satelliteBatch = satelliteBatchRef.current;
    if (!viewer || !satelliteBatch || viewer.isDestroyed()) {
      return;
    }
    const displayFrame = `${snapshot.reducer_version}:${Math.round(displaySimTime * 10)}`;
    if (displayFrame === lastRenderedFrame.current) {
      return;
    }
    latestSnapshotRef.current = snapshot;
    try {
      setRenderError(null);
      renderCesiumSnapshot(
        viewer.entities,
        snapshot,
        {
          satellites: satelliteBatch,
          satelliteIcons: satelliteIconCache.current,
          satelliteModels: satelliteModelCache.current,
          orbitTracks: orbitTrackCache.current,
          beams: beamCache.current,
          users: userCache.current,
          links: linkCache.current,
          routes: routeCache.current
        },
        displaySimTime,
        activeSelectedSatelliteId
      );
      lastRenderedFrame.current = displayFrame;
      if (
        cameraMode === "EARTH" &&
        !hasFocusedSatellites.current &&
        satelliteBatch.size() > 0
      ) {
        hasFocusedSatellites.current = true;
        focusEarthOverview(viewer);
      }
    } catch (error) {
      setRenderError(renderErrorMessage(error));
      console.error("Cesium snapshot render failed", error);
    }
    viewer.scene.requestRender();
  }, [snapshot, cameraMode, displaySimTime]);

  useEffect(() => {
    setSelectedTrail((trail) => appendSatelliteInsetTrail(trail, selectedSatellite));
  }, [
    selectedSatellite?.satellite_id,
    selectedSatellite?.sim_time,
    selectedSatellite?.position[0],
    selectedSatellite?.position[1],
    selectedSatellite?.position[2]
  ]);

  useEffect(() => {
    const viewer = viewerRef.current;
    if (!viewer || viewer.isDestroyed() || cameraMode !== "EARTH") {
      return;
    }
    focusEarthOverview(viewer);
    viewer.scene.requestRender();
  }, [cameraMode]);

  useEffect(() => {
    const viewer = viewerRef.current;
    if (
      !viewer ||
      viewer.isDestroyed() ||
      cameraMode !== "SATELLITE" ||
      !selectedSatellite
    ) {
      return;
    }
    focusSatelliteFollow(viewer, selectedSatellite);
    viewer.scene.requestRender();
  }, [
    cameraMode,
    selectedSatellite?.satellite_id,
    selectedSatellite?.sim_time,
    selectedSatellite?.position[0],
    selectedSatellite?.position[1],
    selectedSatellite?.position[2]
  ]);

  return (
    <div className="cesium-globe" ref={containerRef}>
      <div className="globe-view-controls" aria-label="三维视角控制">
        <div className="globe-view-mode" role="group" aria-label="视角模式">
          <button
            type="button"
            className={cameraMode === "EARTH" ? "active" : ""}
            aria-pressed={cameraMode === "EARTH"}
            onClick={() => setCameraMode("EARTH")}
          >
            地球视角
          </button>
          <button
            type="button"
            className={cameraMode === "SATELLITE" ? "active" : ""}
            aria-pressed={cameraMode === "SATELLITE"}
            disabled={selectableSatellites.length === 0}
            onClick={() => setCameraMode("SATELLITE")}
          >
            卫星跟随
          </button>
        </div>
        <label className="satellite-select-label" htmlFor="satellite-follow-target">
          <span>目标卫星</span>
          <select
            id="satellite-follow-target"
            value={activeSelectedSatelliteId}
            disabled={selectableSatellites.length === 0}
            onChange={(event) => setSelectedSatelliteId(event.currentTarget.value)}
          >
            {selectableSatellites.length === 0 ? (
              <option value="">暂无卫星</option>
            ) : null}
            {selectableSatellites.map((satellite) => (
              <option key={satellite.satellite_id} value={satellite.satellite_id}>
                {satellite.satellite_id}
              </option>
            ))}
          </select>
        </label>
      </div>
      {cameraMode === "SATELLITE" && selectedSatellite ? (
        <SatelliteInset
          satellite={selectedSatellite}
          trail={selectedTrail}
          computeNode={selectedComputeNode}
        />
      ) : null}
      {renderError ? <div className="globe-render-error">{renderError}</div> : null}
    </div>
  );
}

async function loadNaturalEarthCountryOverlays(
  viewer: Viewer,
  cache: Map<string, Entity>,
  isDisposed: () => boolean
): Promise<void> {
  try {
    const response = await fetch(NATURAL_EARTH_COUNTRY_SOURCE_URI);
    if (!response.ok) {
      return;
    }
    const collection =
      (await response.json()) as NaturalEarthCountryFeatureCollection;
    if (isDisposed() || viewer.isDestroyed()) {
      return;
    }
    clearCountryOverlays(viewer.entities, cache);
    installNaturalEarthCountryOverlays(viewer.entities, cache, collection);
    viewer.scene.requestRender();
  } catch (error) {
    console.warn("Natural Earth country overlay load failed", error);
  }
}

function renderErrorMessage(error: unknown): string {
  return error instanceof Error ? error.message : String(error);
}

function focusEarthOverview(viewer: Viewer): void {
  viewer.camera.lookAtTransform(Matrix4.IDENTITY);
  viewer.camera.setView({
    destination: Cartesian3.fromDegrees(35, 18, 18_000_000),
    orientation: {
      heading: CesiumMath.toRadians(0),
      pitch: CesiumMath.toRadians(-90),
      roll: 0
    }
  });
}

function focusSatelliteFollow(viewer: Viewer, satellite: SatelliteState): void {
  viewer.camera.lookAtTransform(Matrix4.IDENTITY);
  viewer.camera.lookAt(
    Cartesian3.fromElements(
      satellite.position[0],
      satellite.position[1],
      satellite.position[2]
    ),
    new HeadingPitchRange(CesiumMath.toRadians(28), CesiumMath.toRadians(-18), 980_000)
  );
}

function SatelliteInset({
  satellite,
  trail,
  computeNode
}: {
  satellite: SatelliteState;
  trail: readonly SatelliteInsetPoint[];
  computeNode?: {
    capacity: number;
    available_capacity: number;
    load_ratio?: number;
    status: string;
  } | null;
}) {
  const latestPoint = trail[trail.length - 1] ?? {
    satelliteId: satellite.satellite_id,
    simTime: satellite.sim_time,
    x: 50,
    y: 50
  };
  const trailPoints = trail.map((point) => `${point.x.toFixed(2)},${point.y.toFixed(2)}`);
  const computeSummary = satelliteComputeSummary(computeNode);
  return (
    <aside className="satellite-inset" aria-label="卫星局部放大">
      <div className="satellite-inset-header">
        <span>卫星局部</span>
        <strong>{satellite.satellite_id}</strong>
      </div>
      <div className="satellite-inset-scene">
        <svg viewBox="0 0 100 100" role="img" aria-label="卫星局部轨迹">
          <polyline points={trailPoints.join(" ")} />
          {trail.map((point) => (
            <circle
              key={`${point.satelliteId}:${point.simTime}:${point.x}:${point.y}`}
              cx={point.x}
              cy={point.y}
              r="1.3"
            />
          ))}
        </svg>
        <div
          className="satellite-mini-model"
          aria-hidden="true"
          style={{ left: `${latestPoint.x}%`, top: `${latestPoint.y}%` }}
        >
          <span className="mini-panel left" />
          <span className="mini-bus" />
          <span className="mini-panel right" />
          <span className="mini-antenna" />
        </div>
      </div>
      <div className="satellite-inset-meta">
        <span>高度 {satelliteAltitudeKm(satellite).toFixed(0)} km</span>
        <span>t={satellite.sim_time.toFixed(1)}s</span>
        {computeSummary ? (
          <>
            <span>算力 {computeSummary.capacityLabel}</span>
            <span>可用 {computeSummary.availableLabel}</span>
            <span>负载 {computeSummary.utilizationLabel}</span>
            <span>状态 {computeSummary.statusLabel}</span>
          </>
        ) : (
          <span>算力节点未同步</span>
        )}
      </div>
    </aside>
  );
}

interface RenderCaches {
  satellites: SatellitePrimitiveBatch;
  satelliteIcons: Map<string, Entity>;
  satelliteModels: Map<string, Entity>;
  orbitTracks: Map<string, Entity>;
  beams: Map<string, Entity>;
  users: Map<string, Entity>;
  links: Map<string, Entity>;
  routes: Map<string, Entity>;
}

export function renderCesiumSnapshot(
  entities: EntityCollection,
  snapshot: WorldSnapshot,
  caches: RenderCaches,
  displaySimTime = snapshot.last_sim_time,
  selectedSatelliteId = ""
): void {
  const limits = visualLayerLimits(snapshot.scenario_config);
  const beamLengthMeters = snapshot.scenario_config?.render?.beam_length_m ?? 600_000;
  const beamRadiusMeters = snapshot.scenario_config?.render?.beam_radius_m ?? 160_000;
  const beamEntityIds = new Set<string>();
  const satellites = projectSatelliteStates(snapshot.satellites, displaySimTime);

  caches.satellites.update(limits.showSatellites ? satellites : []);

  const satelliteIconEntityIds = new Set<string>();
  for (const satellite of satellites.slice(0, limits.satelliteIconRenderLimit)) {
    const id = `satellite-icon:${satellite.satellite_id}`;
    satelliteIconEntityIds.add(id);
    upsertSatelliteIconEntity(entities, caches.satelliteIcons, satellite);
  }
  pruneEntities(entities, caches.satelliteIcons, satelliteIconEntityIds);

  const satelliteModelEntityIds = new Set<string>();
  for (const satellite of satellites.slice(
    0,
    Math.min(limits.satelliteIconRenderLimit, 32)
  )) {
    for (const id of upsertSatelliteModelEntities(
      entities,
      caches.satelliteModels,
      satellite
    )) {
      satelliteModelEntityIds.add(id);
    }
  }
  pruneEntities(entities, caches.satelliteModels, satelliteModelEntityIds);

  const orbitTrackEntityIds = new Set<string>();
  for (const satellite of satellites.slice(0, limits.orbitTrackRenderLimit)) {
    const id = `satellite-orbit:${satellite.satellite_id}`;
    orbitTrackEntityIds.add(id);
    upsertSatelliteOrbitEntity(entities, caches.orbitTracks, satellite);
  }
  pruneEntities(entities, caches.orbitTracks, orbitTrackEntityIds);

  for (const satellite of selectedCoverageBeamSatellites(
    satellites,
    selectedSatelliteId,
    limits.beamRenderLimit
  )) {
    for (const beamId of upsertBeamEntity(entities, caches.beams, satellite, {
      beamLengthMeters,
      beamRadiusMeters,
      enabled: satellite.status.toLowerCase() !== "offline"
    })) {
      beamEntityIds.add(beamId);
    }
  }
  pruneBeamEntities(entities, caches.beams, beamEntityIds);

  const userEntityIds = new Set<string>();
  for (const user of snapshot.ground_users.slice(0, limits.groundUserRenderLimit)) {
    const id = `user:${user.user_id}`;
    userEntityIds.add(id);
    upsertGroundUserEntity(entities, caches.users, user);
  }
  pruneEntities(entities, caches.users, userEntityIds);

  const linkEntityIds = new Set<string>();
  const nodeIndex = {
    satellites: new Map(satellites.map((satellite) => [satellite.satellite_id, satellite])),
    groundUsers: snapshot.indexes.ground_users
  };
  for (const link of snapshot.links.slice(0, limits.linkRenderLimit)) {
    const id = `link:${link.source_id}->${link.target_id}`;
    linkEntityIds.add(id);
    upsertLinkEntity(entities, caches.links, link, nodeIndex);
  }
  pruneEntities(entities, caches.links, linkEntityIds);

  const routeEntityIds = new Set<string>();
  for (const route of snapshot.routes.slice(0, limits.routeRenderLimit)) {
    const id = `route:${route.route_id}`;
    routeEntityIds.add(id);
    upsertRouteEntity(entities, caches.routes, route, nodeIndex);
  }
  pruneEntities(entities, caches.routes, routeEntityIds);
}

function upsertGroundUserEntity(
  entities: EntityCollection,
  cache: Map<string, Entity>,
  user: { user_id: string; position?: readonly [number, number, number?]; status?: string }
): void {
  const id = `user:${user.user_id}`;
  const position = groundUserCartesian(user);
  const isGroundStation = user.status?.toUpperCase() === "GROUND_STATION";
  if (!position) {
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
      name: user.user_id,
      position,
      point: {
        pixelSize: isGroundStation ? 6 : 3,
        color: isGroundStation ? Color.ORANGE : Color.ORANGE.withAlpha(0.58),
        outlineColor: Color.BLACK,
        outlineWidth: 1
      },
      label: isGroundStation
        ? {
            text: user.user_id,
            font: "11px sans-serif",
            fillColor: Color.WHITE,
            outlineColor: Color.BLACK,
            outlineWidth: 2,
            style: LabelStyle.FILL_AND_OUTLINE,
            verticalOrigin: VerticalOrigin.TOP,
            pixelOffset: new Cartesian2(0, 10)
          }
        : undefined
    });
    cache.set(id, entity);
  }
  entity.position = new ConstantPositionProperty(position);
}
