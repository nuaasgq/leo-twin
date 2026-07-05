import { describe, expect, it } from "vitest";

import {
  SCENE_3D_ASSET_MANIFEST_V1,
  SCENE_3D_ASSET_MANIFEST_V1_ID,
  scene3dAssetManifestSummary
} from "../src/3d/assets/assetManifest";
import { NATURAL_EARTH_COUNTRY_SOURCE_URI } from "../src/3d/cesium/countryOverlays";
import { SATELLITE_ICON_DATA_URI } from "../src/3d/orbit_renderer/satelliteEntities";
import { NASA_SATELLITE_KIT_MODEL_PARTS } from "../src/3d/orbit_renderer/satelliteModelEntities";

describe("3D asset manifest v1", () => {
  it("records deterministic visual-only asset policy", () => {
    expect(SCENE_3D_ASSET_MANIFEST_V1).toMatchObject({
      version: "v1",
      manifest_id: SCENE_3D_ASSET_MANIFEST_V1_ID,
      source: "FRONTEND_BUNDLED_ASSETS",
      policy: {
        simulation_semantics: "VISUAL_ONLY",
        deterministic_loading: true,
        external_runtime_fetches: false,
        license_review_required_before_replacement: true,
        no_stk_exata_afsim_dds: true
      }
    });
  });

  it("covers Earth texture, country boundaries, satellite GLB parts, and icons", () => {
    expect(SCENE_3D_ASSET_MANIFEST_V1.assets.map((asset) => asset.role)).toEqual([
      "EARTH_TEXTURE",
      "COUNTRY_BOUNDARIES",
      "SATELLITE_MODEL",
      "SATELLITE_MODEL",
      "SATELLITE_MODEL",
      "SATELLITE_ICON"
    ]);

    expect(scene3dAssetManifestSummary()).toEqual({
      label: "资产",
      value: "v1 / 6 项",
      detail: "地球底图 1 / 国界 1 / 模型 3 / 图标 1 / SHA 4"
    });
  });

  it("keeps bundled file hashes aligned with renderer constants", () => {
    const modelAssets = SCENE_3D_ASSET_MANIFEST_V1.assets.filter(
      (asset) => asset.role === "SATELLITE_MODEL"
    );

    expect(modelAssets.map((asset) => asset.runtime_uri)).toEqual(
      NASA_SATELLITE_KIT_MODEL_PARTS.map((asset) => asset.uri)
    );
    expect(modelAssets.map((asset) => asset.sha256)).toEqual(
      NASA_SATELLITE_KIT_MODEL_PARTS.map((asset) => asset.sha256)
    );
    expect(modelAssets.every((asset) => asset.integrity === "SHA256_VERIFIED")).toBe(
      true
    );
  });

  it("pins Natural Earth and generated satellite icon sources", () => {
    const countryAsset = SCENE_3D_ASSET_MANIFEST_V1.assets.find(
      (asset) => asset.role === "COUNTRY_BOUNDARIES"
    );
    const iconAsset = SCENE_3D_ASSET_MANIFEST_V1.assets.find(
      (asset) => asset.role === "SATELLITE_ICON"
    );

    expect(countryAsset).toMatchObject({
      runtime_uri: NATURAL_EARTH_COUNTRY_SOURCE_URI,
      sha256: "6866c877d39cba9c357620878839b336d569f8c662d3cfab4cb1dbe2d39c977f",
      integrity: "SHA256_VERIFIED",
      license_note: "Natural Earth data is public domain."
    });
    expect(iconAsset).toMatchObject({
      runtime_uri: "inline://SATELLITE_ICON_DATA_URI",
      file_size_bytes: SATELLITE_ICON_DATA_URI.length,
      integrity: "CODE_GENERATED",
      license_note: "Project-generated vector icon."
    });
  });
});
