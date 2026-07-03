import {
  Cartesian2,
  Color,
  ConstantPositionProperty,
  Entity,
  EntityCollection,
  LabelStyle,
  VerticalOrigin,
  Viewer
} from "cesium";
import "cesium/Build/Cesium/Widgets/widgets.css";
import { useEffect, useRef } from "react";

import { createFrameScheduler, FrameScheduler } from "../../core/sync_engine";
import { ObservabilityState } from "../../stream/state_store";
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
  pruneSatelliteEntities,
  upsertSatelliteEntity
} from "../orbit_renderer/satelliteEntities";

export interface CesiumGlobeProps {
  state: ObservabilityState;
}

export function CesiumGlobe({ state }: CesiumGlobeProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const viewerRef = useRef<Viewer | null>(null);
  const schedulerRef = useRef<FrameScheduler | null>(null);
  const satelliteCache = useRef(new Map<string, Entity>());
  const beamCache = useRef(new Map<string, Entity>());
  const userCache = useRef(new Map<string, Entity>());
  const linkCache = useRef(new Map<string, Entity>());
  const routeCache = useRef(new Map<string, Entity>());

  useEffect(() => {
    if (!containerRef.current) {
      return;
    }
    const viewer = new Viewer(containerRef.current, {
      animation: false,
      timeline: false,
      geocoder: false,
      homeButton: false,
      sceneModePicker: false,
      baseLayerPicker: false,
      navigationHelpButton: false,
      fullscreenButton: false,
      infoBox: false,
      selectionIndicator: false,
      shouldAnimate: false
    });
    viewerRef.current = viewer;
    schedulerRef.current = createFrameScheduler();
    return () => {
      schedulerRef.current?.cancel();
      schedulerRef.current = null;
      viewer.destroy();
      viewerRef.current = null;
    };
  }, []);

  useEffect(() => {
    const viewer = viewerRef.current;
    const scheduler = schedulerRef.current;
    if (!viewer || !scheduler) {
      return;
    }
    scheduler.schedule(() => {
      renderCesiumState(viewer.entities, state, {
        satellites: satelliteCache.current,
        beams: beamCache.current,
        users: userCache.current,
        links: linkCache.current,
        routes: routeCache.current
      });
      viewer.scene.requestRender();
    });
  }, [state]);

  return <div className="cesium-globe" ref={containerRef} />;
}

interface RenderCaches {
  satellites: Map<string, Entity>;
  beams: Map<string, Entity>;
  users: Map<string, Entity>;
  links: Map<string, Entity>;
  routes: Map<string, Entity>;
}

export function renderCesiumState(
  entities: EntityCollection,
  state: ObservabilityState,
  caches: RenderCaches
): void {
  const beamLengthMeters = state.scenarioConfig?.render?.beam_length_m ?? 600_000;
  const beamRadiusMeters = state.scenarioConfig?.render?.beam_radius_m ?? 160_000;
  const satelliteEntityIds = new Set<string>();
  const beamEntityIds = new Set<string>();

  for (const satellite of state.satellites.values()) {
    const satelliteId = `satellite:${satellite.satellite_id}`;
    const beamId = `beam:${satellite.satellite_id}`;
    satelliteEntityIds.add(satelliteId);
    beamEntityIds.add(beamId);
    upsertSatelliteEntity(entities, caches.satellites, satellite);
    upsertBeamEntity(entities, caches.beams, satellite, {
      beamLengthMeters,
      beamRadiusMeters,
      enabled: satellite.status.toLowerCase() !== "offline"
    });
  }
  pruneSatelliteEntities(entities, caches.satellites, satelliteEntityIds);
  pruneBeamEntities(entities, caches.beams, beamEntityIds);

  const userEntityIds = new Set<string>();
  for (const user of state.groundUsers.values()) {
    const id = `user:${user.user_id}`;
    userEntityIds.add(id);
    upsertGroundUserEntity(entities, caches.users, user);
  }
  pruneEntities(entities, caches.users, userEntityIds);

  const linkEntityIds = new Set<string>();
  for (const link of state.links.values()) {
    const id = `link:${link.source_id}->${link.target_id}`;
    linkEntityIds.add(id);
    upsertLinkEntity(entities, caches.links, link, state);
  }
  pruneEntities(entities, caches.links, linkEntityIds);

  const routeEntityIds = new Set<string>();
  for (const route of state.routes.values()) {
    const id = `route:${route.route_id}`;
    routeEntityIds.add(id);
    upsertRouteEntity(entities, caches.routes, route, state);
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
        pixelSize: 6,
        color: Color.ORANGE,
        outlineColor: Color.BLACK,
        outlineWidth: 1
      },
      label: {
        text: user.user_id,
        font: "11px sans-serif",
        fillColor: Color.WHITE,
        outlineColor: Color.BLACK,
        outlineWidth: 2,
        style: LabelStyle.FILL_AND_OUTLINE,
        verticalOrigin: VerticalOrigin.TOP,
        pixelOffset: new Cartesian2(0, 10)
      }
    });
    cache.set(id, entity);
  }
  entity.position = new ConstantPositionProperty(position);
}
