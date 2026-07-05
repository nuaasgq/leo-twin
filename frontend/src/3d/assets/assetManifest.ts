import { NATURAL_EARTH_COUNTRY_SOURCE_URI } from "../cesium/countryOverlays";
import { SATELLITE_ICON_DATA_URI } from "../orbit_renderer/satelliteEntities";
import {
  NASA_SATELLITE_KIT_MODEL_PARTS,
  SatelliteModelAsset
} from "../orbit_renderer/satelliteModelEntities";

export const SCENE_3D_ASSET_MANIFEST_V1_ID = "leo_twin.3d_asset_manifest.v1";

export type Scene3dAssetRole =
  | "EARTH_TEXTURE"
  | "COUNTRY_BOUNDARIES"
  | "SATELLITE_MODEL"
  | "SATELLITE_ICON";

export type Scene3dAssetIntegrity =
  | "SHA256_VERIFIED"
  | "PACKAGE_LOCK_MANAGED"
  | "CODE_GENERATED";

export interface Scene3dAssetManifest {
  version: "v1";
  manifest_id: string;
  source: "FRONTEND_BUNDLED_ASSETS";
  policy: Scene3dAssetPolicy;
  assets: readonly Scene3dAsset[];
  follow_up_slots: readonly Scene3dAssetFollowUpSlot[];
}

export interface Scene3dAssetPolicy {
  simulation_semantics: "VISUAL_ONLY";
  deterministic_loading: true;
  external_runtime_fetches: false;
  license_review_required_before_replacement: true;
  no_stk_exata_afsim_dds: true;
}

export interface Scene3dAsset {
  id: string;
  role: Scene3dAssetRole;
  runtime_uri: string;
  source_name: string;
  source_uri: string;
  source_file?: string;
  sha256?: string;
  file_size_bytes?: number;
  integrity: Scene3dAssetIntegrity;
  license_note: string;
  render_surface: string;
  product_note: string;
}

export interface Scene3dAssetFollowUpSlot {
  slot: string;
  purpose: string;
  acceptance_note: string;
}

export interface Scene3dAssetManifestSummary {
  label: string;
  value: string;
  detail: string;
}

export const SCENE_3D_ASSET_MANIFEST_V1: Scene3dAssetManifest = {
  version: "v1",
  manifest_id: SCENE_3D_ASSET_MANIFEST_V1_ID,
  source: "FRONTEND_BUNDLED_ASSETS",
  policy: {
    simulation_semantics: "VISUAL_ONLY",
    deterministic_loading: true,
    external_runtime_fetches: false,
    license_review_required_before_replacement: true,
    no_stk_exata_afsim_dds: true
  },
  assets: [
    {
      id: "earth.texture.cesium.natural_earth_ii",
      role: "EARTH_TEXTURE",
      runtime_uri: "cesium://Assets/Textures/NaturalEarthII",
      source_name: "Cesium bundled NaturalEarthII tile map",
      source_uri: "cesium package Assets/Textures/NaturalEarthII",
      integrity: "PACKAGE_LOCK_MANAGED",
      license_note:
        "Bundled with the local Cesium package. Replacement must carry explicit source and license metadata.",
      render_surface: "Cesium base imagery layer",
      product_note:
        "Current deterministic Earth texture. It is a visual background and does not affect simulation state."
    },
    {
      id: "earth.boundaries.natural_earth_110m_admin_0",
      role: "COUNTRY_BOUNDARIES",
      runtime_uri: NATURAL_EARTH_COUNTRY_SOURCE_URI,
      source_name: "Natural Earth 1:110m Admin 0 Countries",
      source_uri: "https://www.naturalearthdata.com/",
      source_file: "ne_110m_admin_0_countries.geojson",
      sha256: "6866c877d39cba9c357620878839b336d569f8c662d3cfab4cb1dbe2d39c977f",
      file_size_bytes: 838_726,
      integrity: "SHA256_VERIFIED",
      license_note: "Natural Earth data is public domain.",
      render_surface: "Cesium country boundary and label overlay",
      product_note:
        "Country outlines are deterministic visual context only and are not used by domain models."
    },
    ...NASA_SATELLITE_KIT_MODEL_PARTS.map((asset) =>
      nasaSatelliteKitManifestAsset(asset)
    ),
    {
      id: "satellite.icon.inline_svg.v1",
      role: "SATELLITE_ICON",
      runtime_uri: "inline://SATELLITE_ICON_DATA_URI",
      source_name: "LEO-Twin generated satellite SVG icon",
      source_uri: "frontend/src/3d/orbit_renderer/satelliteEntities.ts",
      source_file: "SATELLITE_ICON_DATA_URI",
      file_size_bytes: SATELLITE_ICON_DATA_URI.length,
      integrity: "CODE_GENERATED",
      license_note: "Project-generated vector icon.",
      render_surface: "Cesium satellite billboard overlay",
      product_note:
        "Small-scale satellite glyph used with depth testing; not a physical spacecraft model."
    }
  ],
  follow_up_slots: [
    {
      slot: "earth.texture.high_resolution",
      purpose: "Replace or augment NaturalEarthII with a higher-resolution pinned Earth texture.",
      acceptance_note:
        "Must include bundled file path, SHA-256, license note, and screenshot regression before default use."
    },
    {
      slot: "satellite.model.production",
      purpose: "Replace or supplement the NASA Satellite Kit parts with a product-grade glTF/GLB model.",
      acceptance_note:
        "Must include source URL, local file hashes, license review, render budget, and selected-satellite visual test."
    },
    {
      slot: "coverage.beam.material",
      purpose: "Add deterministic material presets for selected-satellite footprint and beam cells.",
      acceptance_note:
        "Must remain visual-only and must not claim RF antenna-pattern or link-budget fidelity."
    }
  ]
};

export function scene3dAssetManifestSummary(
  manifest: Scene3dAssetManifest = SCENE_3D_ASSET_MANIFEST_V1
): Scene3dAssetManifestSummary {
  const satelliteModelCount = manifest.assets.filter(
    (asset) => asset.role === "SATELLITE_MODEL"
  ).length;
  const verifiedHashCount = manifest.assets.filter(
    (asset) => asset.integrity === "SHA256_VERIFIED"
  ).length;
  return {
    label: "资产",
    value: `${manifest.version} / ${manifest.assets.length} 项`,
    detail: `地球底图 ${assetRoleCount(manifest, "EARTH_TEXTURE")} / 国界 ${assetRoleCount(
      manifest,
      "COUNTRY_BOUNDARIES"
    )} / 模型 ${satelliteModelCount} / 图标 ${assetRoleCount(
      manifest,
      "SATELLITE_ICON"
    )} / SHA ${verifiedHashCount}`
  };
}

function nasaSatelliteKitManifestAsset(asset: SatelliteModelAsset): Scene3dAsset {
  return {
    id: `satellite.model.nasa_kit.${asset.idSuffix}`,
    role: "SATELLITE_MODEL",
    runtime_uri: asset.uri,
    source_name: "NASA 3D Resources Satellite Kit",
    source_uri: "https://science.nasa.gov/3d-resources/",
    source_file: asset.sourceFile,
    sha256: asset.sha256,
    file_size_bytes: nasaSatelliteKitFileSize(asset.idSuffix),
    integrity: "SHA256_VERIFIED",
    license_note:
      "NASA 3D Resources assets are subject to NASA media and brand usage guidance.",
    render_surface: "Cesium selected and bounded satellite GLB model entities",
    product_note:
      "Generic satellite visual model. It does not imply exact Starlink or NASA mission fidelity."
  };
}

function nasaSatelliteKitFileSize(idSuffix: string): number {
  if (idSuffix === "body") {
    return 5_256;
  }
  if (idSuffix === "wings") {
    return 8_172;
  }
  if (idSuffix === "radio") {
    return 8_436;
  }
  return 0;
}

function assetRoleCount(
  manifest: Scene3dAssetManifest,
  role: Scene3dAssetRole
): number {
  return manifest.assets.filter((asset) => asset.role === role).length;
}
