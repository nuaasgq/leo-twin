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

import {
  ComputeResourceSummary,
  RuntimeSatelliteKpiSlicesV1,
  SatelliteState
} from "../../core/event_types";
import { ComputeNodeRenderState, WorldSnapshot } from "../../state/snapshot_engine";
import {
  CoverageBeamDisplaySummary,
  CoverageUserIntersectionSummary,
  coverageBeamDisplaySummary,
  coverageUserIntersectionSummary,
  pruneBeamEntities,
  resolveBeamGeometryOptions,
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
  GlobeVisualMode,
  applyGlobeVisualPolicy
} from "./globeVisualPolicy";
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
import {
  DEFAULT_LOCAL_VISUAL_LAYERS,
  LocalVisualLayerKey,
  LocalVisualLayerState,
  applyLocalVisualLayerLimits,
  visualLayerLimits,
  visualSatelliteModelRenderSatellites
} from "./renderLimits";
import {
  GlobeCameraMode,
  SatelliteInsetPoint,
  appendSatelliteInsetTrail,
  satelliteAltitudeKm,
  satelliteComputeSummary,
  selectedDisplaySatellite
} from "./satelliteFollow";
import {
  SelectedSatelliteDetailSummary,
  selectedSatelliteDetailSummary
} from "./satelliteDetailSummary";

export interface CesiumGlobeProps {
  snapshot: WorldSnapshot;
  displaySimTime: number;
  satelliteKpiSlices?: RuntimeSatelliteKpiSlicesV1 | null;
}

const LOCAL_VISUAL_LAYER_OPTIONS: readonly {
  key: LocalVisualLayerKey;
  label: string;
}[] = [
  { key: "countryOverlays", label: "国界" },
  { key: "satellitePoints", label: "点位" },
  { key: "satelliteIcons", label: "图标" },
  { key: "satelliteModels", label: "模型" },
  { key: "orbitTracks", label: "轨迹" },
  { key: "coverageBeams", label: "波束" },
  { key: "groundUsers", label: "用户" },
  { key: "links", label: "链路" },
  { key: "routes", label: "路由" }
];

export function CesiumGlobe({
  snapshot,
  displaySimTime,
  satelliteKpiSlices
}: CesiumGlobeProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const viewerRef = useRef<Viewer | null>(null);
  const latestSnapshotRef = useRef(snapshot);
  const countryOverlayVisibleRef = useRef(
    DEFAULT_LOCAL_VISUAL_LAYERS.countryOverlays
  );
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
  const [globeVisualMode, setGlobeVisualMode] = useState<GlobeVisualMode>("OPAQUE");
  const [localLayers, setLocalLayers] = useState<LocalVisualLayerState>(
    DEFAULT_LOCAL_VISUAL_LAYERS
  );
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
  const computeResourceSummary =
    snapshot.scenario_config?.backend_summary?.compute_resource_summary ?? null;
  const coverageDisplaySummary = useMemo(
    () => coverageBeamDisplaySummary(snapshot.scenario_config),
    [snapshot.scenario_config]
  );
  const coverageUserSummary = useMemo(
    () =>
      coverageUserIntersectionSummary(
        selectedSatellite,
        snapshot.ground_users,
        snapshot.scenario_config
      ),
    [
      selectedSatellite?.satellite_id,
      selectedSatellite?.position[0],
      selectedSatellite?.position[1],
      selectedSatellite?.position[2],
      snapshot.ground_users,
      snapshot.scenario_config
    ]
  );
  const selectedDetailSummary = useMemo(
    () =>
      selectedSatellite
        ? selectedSatelliteDetailSummary({
            satellite: selectedSatellite,
            computeNode: selectedComputeNode,
            computeResourceSummary,
            links: snapshot.links,
            routes: snapshot.routes,
            groundUsers: snapshot.ground_users,
            scenarioConfig: snapshot.scenario_config,
            satelliteKpiSlices
          })
        : null,
    [
      selectedSatellite?.satellite_id,
      selectedSatellite?.sim_time,
      selectedSatellite?.position[0],
      selectedSatellite?.position[1],
      selectedSatellite?.position[2],
      selectedSatellite?.velocity?.[0],
      selectedSatellite?.velocity?.[1],
      selectedSatellite?.velocity?.[2],
      selectedSatellite?.status,
      selectedComputeNode,
      computeResourceSummary,
      snapshot.links,
      snapshot.routes,
      snapshot.ground_users,
      snapshot.scenario_config,
      satelliteKpiSlices
    ]
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
    applyGlobeVisualPolicy(viewer.scene, "OPAQUE");
    installCountryOverlays(viewer.entities, countryOverlayCache.current);
    void loadNaturalEarthCountryOverlays(
      viewer,
      countryOverlayCache.current,
      () => disposed,
      () => countryOverlayVisibleRef.current
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
    const layerFrame = localVisualLayerFrame(localLayers);
    const selectedFrame = activeSelectedSatelliteId || "none";
    const displayFrame = `${snapshot.reducer_version}:${Math.round(
      displaySimTime * 10
    )}:${selectedFrame}:${layerFrame}`;
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
        activeSelectedSatelliteId,
        localLayers
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
  }, [snapshot, cameraMode, displaySimTime, activeSelectedSatelliteId, localLayers]);

  useEffect(() => {
    const viewer = viewerRef.current;
    if (!viewer || viewer.isDestroyed()) {
      return;
    }
    applyGlobeVisualPolicy(viewer.scene, globeVisualMode);
    viewer.scene.requestRender();
  }, [globeVisualMode]);

  useEffect(() => {
    countryOverlayVisibleRef.current = localLayers.countryOverlays;
    const viewer = viewerRef.current;
    if (!viewer || viewer.isDestroyed()) {
      return;
    }
    setEntityCacheVisibility(
      countryOverlayCache.current,
      localLayers.countryOverlays
    );
    viewer.scene.requestRender();
  }, [localLayers.countryOverlays]);

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
        <div className="globe-visual-mode" role="group" aria-label="地球显示模式">
          <button
            type="button"
            className={globeVisualMode === "OPAQUE" ? "active" : ""}
            aria-pressed={globeVisualMode === "OPAQUE"}
            onClick={() => setGlobeVisualMode("OPAQUE")}
          >
            不透明地球
          </button>
          <button
            type="button"
            className={globeVisualMode === "TRANSLUCENT" ? "active" : ""}
            aria-pressed={globeVisualMode === "TRANSLUCENT"}
            onClick={() => setGlobeVisualMode("TRANSLUCENT")}
          >
            透明观察
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
        <div className="globe-layer-toggles" role="group" aria-label="即时图层">
          {LOCAL_VISUAL_LAYER_OPTIONS.map((option) => (
            <label
              className={localLayers[option.key] ? "active" : ""}
              key={option.key}
            >
              <input
                type="checkbox"
                checked={localLayers[option.key]}
                onChange={(event) =>
                  setLocalLayers((current) => ({
                    ...current,
                    [option.key]: event.currentTarget.checked
                  }))
                }
              />
              <span>{option.label}</span>
            </label>
          ))}
        </div>
        {selectedDetailSummary ? (
          <SelectedSatelliteDetailStrip summary={selectedDetailSummary} />
        ) : null}
      </div>
      {cameraMode === "SATELLITE" && selectedSatellite ? (
        <SatelliteInset
          satellite={selectedSatellite}
          trail={selectedTrail}
          computeNode={selectedComputeNode}
          computeResourceSummary={computeResourceSummary}
          coverageSummary={coverageDisplaySummary}
          coverageUserSummary={coverageUserSummary}
        />
      ) : null}
      {renderError ? <div className="globe-render-error">{renderError}</div> : null}
    </div>
  );
}

function SelectedSatelliteDetailStrip({
  summary
}: {
  summary: SelectedSatelliteDetailSummary;
}) {
  const utilization = summary.computeSummary?.utilizationPercent ?? 0;
  return (
    <section className="selected-satellite-strip" aria-label="选中卫星态势">
      <div className="selected-satellite-strip-header">
        <span>选中卫星</span>
        <strong>{summary.satelliteId}</strong>
        <small>{summary.resourceModelLabel}</small>
      </div>
      <div className="selected-satellite-strip-grid">
        <span>{summary.statusLabel}</span>
        <span>{summary.simTimeLabel}</span>
        <span>{summary.altitudeLabel}</span>
        <span>{summary.speedLabel}</span>
        <span>{summary.activeLinksLabel}</span>
        <span>{summary.routeLabel}</span>
        <span>{summary.routeLatencyLabel}</span>
        <span>{summary.routeCapacityLabel}</span>
        <span>{summary.routeLossLabel}</span>
        <span>{summary.routeJitterLabel}</span>
        <span>{summary.linkUtilizationLabel}</span>
        <span>{summary.coverageLabel}</span>
        <span>{summary.computeLoadLabel}</span>
        <span>{summary.runningTaskLabel}</span>
      </div>
      <div className="selected-satellite-resource">
        <div className="selected-satellite-resource-row">
          <span>{summary.computeCapacityLabel}</span>
          <strong>{summary.computeSummary?.utilizationLabel ?? "--"}</strong>
        </div>
        <div className="selected-satellite-resource-track" aria-hidden="true">
          <span style={{ width: `${Math.max(0, Math.min(100, utilization))}%` }} />
        </div>
      </div>
      {summary.routeIds.length > 0 ? (
        <div className="selected-satellite-routes">
          <span>路由</span>
          <strong>{summary.routeIds.join(" / ")}</strong>
        </div>
      ) : null}
      <p>{summary.note}</p>
    </section>
  );
}

async function loadNaturalEarthCountryOverlays(
  viewer: Viewer,
  cache: Map<string, Entity>,
  isDisposed: () => boolean,
  isVisible: () => boolean
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
    setEntityCacheVisibility(cache, isVisible());
    viewer.scene.requestRender();
  } catch (error) {
    console.warn("Natural Earth country overlay load failed", error);
  }
}

function setEntityCacheVisibility(cache: Map<string, Entity>, visible: boolean): void {
  for (const entity of cache.values()) {
    entity.show = visible;
  }
}

function localVisualLayerFrame(layers: LocalVisualLayerState): string {
  return [
    layers.countryOverlays,
    layers.satellitePoints,
    layers.satelliteIcons,
    layers.satelliteModels,
    layers.orbitTracks,
    layers.coverageBeams,
    layers.groundUsers,
    layers.links,
    layers.routes
  ]
    .map((enabled) => (enabled ? "1" : "0"))
    .join("");
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
  computeNode,
  computeResourceSummary,
  coverageSummary,
  coverageUserSummary
}: {
  satellite: SatelliteState;
  trail: readonly SatelliteInsetPoint[];
  computeNode?: ComputeNodeRenderState | null;
  computeResourceSummary?: ComputeResourceSummary | null;
  coverageSummary: CoverageBeamDisplaySummary;
  coverageUserSummary: CoverageUserIntersectionSummary;
}) {
  const latestPoint = trail[trail.length - 1] ?? {
    satelliteId: satellite.satellite_id,
    simTime: satellite.sim_time,
    x: 50,
    y: 50
  };
  const trailPoints = trail.map((point) => `${point.x.toFixed(2)},${point.y.toFixed(2)}`);
  const computeSummary = satelliteComputeSummary(computeNode, computeResourceSummary);
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
        <span>{coverageSummary.footprintRadiusLabel}</span>
        <span>{coverageSummary.beamLengthLabel}</span>
        <span>{coverageSummary.beamCountLabel}</span>
        <span>{coverageSummary.modelLabel}</span>
        <span className="coverage-note">{coverageSummary.note}</span>
        <span>{coverageUserSummary.label}</span>
        <span>{coverageUserSummary.coveredUserLabel}</span>
        <span className="coverage-note">{coverageUserSummary.note}</span>
        {computeSummary ? (
          <>
            <span>{computeSummary.resourceRoleLabel}</span>
            <span>{computeSummary.resourceModelLabel}</span>
            <span>算力 {computeSummary.capacityLabel}</span>
            <span>可用 {computeSummary.availableLabel}</span>
            <span>负载 {computeSummary.utilizationLabel}</span>
            <span>状态 {computeSummary.statusLabel}</span>
            <div className="satellite-resource-meter" aria-label="选中卫星算力资源使用">
              <div className="satellite-resource-meter-row">
                <span>算力负载</span>
                <strong>{computeSummary.utilizationLabel}</strong>
              </div>
              <div className="satellite-resource-track">
                <span
                  className="satellite-resource-fill"
                  style={{ width: `${computeSummary.utilizationPercent}%` }}
                />
              </div>
              <div className="satellite-resource-meter-row muted">
                <span>可用比例</span>
                <strong>{computeSummary.availablePercent.toFixed(1)}%</strong>
              </div>
              <div className="satellite-resource-breakdown" aria-label="选中卫星资源向量">
                {computeSummary.resourceBreakdown.map((item) => (
                  <div className="satellite-resource-breakdown-row" key={item.label}>
                    <span>{item.label}</span>
                    <strong>{item.usedLabel}</strong>
                    <small>{item.capacityLabel}</small>
                    <div className="satellite-resource-mini-track" aria-hidden="true">
                      <span style={{ width: `${item.utilizationPercent}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <span>{computeSummary.cpuVectorLabel}</span>
            <span>{computeSummary.gpuVectorLabel}</span>
            <span>{computeSummary.npuVectorLabel}</span>
            <span>{computeSummary.memoryStorageLabel}</span>
            <span>{computeSummary.processingUsageLabel}</span>
            <span>{computeSummary.memoryUsageLabel}</span>
            <span>{computeSummary.compatibilityNote}</span>
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
  selectedSatelliteId = "",
  localLayers: LocalVisualLayerState = DEFAULT_LOCAL_VISUAL_LAYERS
): void {
  const limits = applyLocalVisualLayerLimits(
    visualLayerLimits(snapshot.scenario_config),
    localLayers
  );
  const beamGeometry = resolveBeamGeometryOptions(snapshot.scenario_config);
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
  for (const satellite of visualSatelliteModelRenderSatellites(
    satellites,
    limits.satelliteModelRenderLimit,
    selectedSatelliteId
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
      ...beamGeometry,
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
