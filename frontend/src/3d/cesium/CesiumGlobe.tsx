import {
  Cartesian2,
  Cartesian3,
  Color,
  ConstantPositionProperty,
  Entity,
  EntityCollection,
  LabelStyle,
  Math as CesiumMath,
  PointPrimitiveCollection,
  VerticalOrigin,
  Viewer
} from "cesium";
import "cesium/Build/Cesium/Widgets/widgets.css";
import { useEffect, useRef, useState } from "react";

import { WorldSnapshot } from "../../state/snapshot_engine";
import {
  pruneBeamEntities,
  upsertBeamEntity
} from "../beam_renderer/beamEntities";
import { groundUserCartesian } from "./positions";
import {
  pruneEntities,
  upsertLinkEntity,
  upsertRouteEntity
} from "../link_renderer/linkEntities";
import {
  SatellitePrimitiveBatch,
  upsertSatelliteIconEntity,
  upsertSatelliteOrbitEntity
} from "../orbit_renderer/satelliteEntities";
import { visualLayerLimits } from "./renderLimits";

export interface CesiumGlobeProps {
  snapshot: WorldSnapshot;
}

export function CesiumGlobe({ snapshot }: CesiumGlobeProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const viewerRef = useRef<Viewer | null>(null);
  const latestSnapshotRef = useRef(snapshot);
  const satelliteBatchRef = useRef<SatellitePrimitiveBatch | null>(null);
  const beamCache = useRef(new Map<string, Entity>());
  const satelliteIconCache = useRef(new Map<string, Entity>());
  const orbitTrackCache = useRef(new Map<string, Entity>());
  const userCache = useRef(new Map<string, Entity>());
  const linkCache = useRef(new Map<string, Entity>());
  const routeCache = useRef(new Map<string, Entity>());
  const hasFocusedSatellites = useRef(false);
  const lastRenderedVersion = useRef(-1);
  const [renderError, setRenderError] = useState<string | null>(null);

  useEffect(() => {
    latestSnapshotRef.current = snapshot;
  }, [snapshot]);

  useEffect(() => {
    if (!containerRef.current) {
      return;
    }
    let viewer: Viewer;
    try {
      viewer = new Viewer(containerRef.current, {
        animation: false,
        timeline: false,
        geocoder: false,
        homeButton: false,
        sceneModePicker: false,
        baseLayer: false,
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
    viewer.scene.globe.baseColor = Color.fromCssColorString("#1d465f");
    viewer.scene.globe.depthTestAgainstTerrain = false;
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
      if (!viewer.isDestroyed()) {
        viewer.scene.canvas.removeEventListener("webglcontextlost", handleContextLost);
        satelliteBatch.clear();
        viewer.scene.primitives.remove(satellitePrimitives);
      }
      satelliteBatchRef.current = null;
      satelliteIconCache.current.clear();
      orbitTrackCache.current.clear();
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
    if (snapshot.reducer_version === lastRenderedVersion.current) {
      return;
    }
    latestSnapshotRef.current = snapshot;
    try {
      setRenderError(null);
      renderCesiumSnapshot(viewer.entities, snapshot, {
        satellites: satelliteBatch,
        satelliteIcons: satelliteIconCache.current,
        orbitTracks: orbitTrackCache.current,
        beams: beamCache.current,
        users: userCache.current,
        links: linkCache.current,
        routes: routeCache.current
      });
      lastRenderedVersion.current = snapshot.reducer_version;
      if (!hasFocusedSatellites.current && satelliteBatch.size() > 0) {
        hasFocusedSatellites.current = true;
        focusEarthOverview(viewer);
      }
    } catch (error) {
      setRenderError(renderErrorMessage(error));
      console.error("Cesium snapshot render failed", error);
    }
    viewer.scene.requestRender();
  }, [snapshot]);

  return (
    <div className="cesium-globe" ref={containerRef}>
      {renderError ? <div className="globe-render-error">{renderError}</div> : null}
    </div>
  );
}

function renderErrorMessage(error: unknown): string {
  return error instanceof Error ? error.message : String(error);
}

function focusEarthOverview(viewer: Viewer): void {
  viewer.camera.setView({
    destination: Cartesian3.fromDegrees(35, 18, 18_000_000),
    orientation: {
      heading: CesiumMath.toRadians(0),
      pitch: CesiumMath.toRadians(-90),
      roll: 0
    }
  });
}

interface RenderCaches {
  satellites: SatellitePrimitiveBatch;
  satelliteIcons: Map<string, Entity>;
  orbitTracks: Map<string, Entity>;
  beams: Map<string, Entity>;
  users: Map<string, Entity>;
  links: Map<string, Entity>;
  routes: Map<string, Entity>;
}

export function renderCesiumSnapshot(
  entities: EntityCollection,
  snapshot: WorldSnapshot,
  caches: RenderCaches
): void {
  const limits = visualLayerLimits(snapshot.scenario_config);
  const beamLengthMeters = snapshot.scenario_config?.render?.beam_length_m ?? 600_000;
  const beamRadiusMeters = snapshot.scenario_config?.render?.beam_radius_m ?? 160_000;
  const beamEntityIds = new Set<string>();

  caches.satellites.update(limits.showSatellites ? snapshot.satellites : []);

  const satelliteIconEntityIds = new Set<string>();
  for (const satellite of snapshot.satellites.slice(0, limits.satelliteIconRenderLimit)) {
    const id = `satellite-icon:${satellite.satellite_id}`;
    satelliteIconEntityIds.add(id);
    upsertSatelliteIconEntity(entities, caches.satelliteIcons, satellite);
  }
  pruneEntities(entities, caches.satelliteIcons, satelliteIconEntityIds);

  const orbitTrackEntityIds = new Set<string>();
  for (const satellite of snapshot.satellites.slice(0, limits.orbitTrackRenderLimit)) {
    const id = `satellite-orbit:${satellite.satellite_id}`;
    orbitTrackEntityIds.add(id);
    upsertSatelliteOrbitEntity(entities, caches.orbitTracks, satellite);
  }
  pruneEntities(entities, caches.orbitTracks, orbitTrackEntityIds);

  for (const satellite of snapshot.satellites.slice(0, limits.beamRenderLimit)) {
    const beamId = `beam:${satellite.satellite_id}`;
    beamEntityIds.add(beamId);
    upsertBeamEntity(entities, caches.beams, satellite, {
      beamLengthMeters,
      beamRadiusMeters,
      enabled: satellite.status.toLowerCase() !== "offline"
    });
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
    satellites: snapshot.indexes.satellites,
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
