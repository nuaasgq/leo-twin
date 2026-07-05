from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ASSET_MANIFEST = ROOT / "frontend" / "src" / "3d" / "assets" / "assetManifest.ts"
SATELLITE_MODEL_ENTITIES = (
    ROOT / "frontend" / "src" / "3d" / "orbit_renderer" / "satelliteModelEntities.ts"
)
PUBLIC_ASSETS = ROOT / "frontend" / "public" / "assets"


def test_scene_3d_asset_manifest_records_local_file_hashes() -> None:
    manifest_text = ASSET_MANIFEST.read_text(encoding="utf-8")
    satellite_model_entities_text = SATELLITE_MODEL_ENTITIES.read_text(encoding="utf-8")
    expected_hashes = {
        "nasa-satellite-kit/satellite-kit-body-2.glb": (
            "175936434483f7b4d83d47fb36f8a2f900bea68b5ec231aa9ca84967432475b7"
        ),
        "nasa-satellite-kit/satellite-kit-wings-2.glb": (
            "b4b6d84ad0356a83dcbe640fda5a1c603c024e84591a65f650f662d3ef34bed1"
        ),
        "nasa-satellite-kit/satellite-kit-radio-1.glb": (
            "9b09e045fa455de38338748d66d12bee6a5d604427f33144cc39e8ff212b73d9"
        ),
        "natural-earth/ne_110m_admin_0_countries.geojson": (
            "6866c877d39cba9c357620878839b336d569f8c662d3cfab4cb1dbe2d39c977f"
        ),
    }

    for relative_path, expected_hash in expected_hashes.items():
        asset_path = PUBLIC_ASSETS / relative_path
        assert asset_path.exists(), relative_path
        assert sha256(asset_path) == expected_hash
        if relative_path.startswith("nasa-satellite-kit/"):
            assert "NASA_SATELLITE_KIT_MODEL_PARTS" in manifest_text
            assert expected_hash in satellite_model_entities_text
        else:
            assert expected_hash in manifest_text


def test_scene_3d_asset_manifest_is_visual_only() -> None:
    manifest_text = ASSET_MANIFEST.read_text(encoding="utf-8")

    assert 'manifest_id: SCENE_3D_ASSET_MANIFEST_V1_ID' in manifest_text
    assert 'simulation_semantics: "VISUAL_ONLY"' in manifest_text
    assert "external_runtime_fetches: false" in manifest_text
    assert "no_stk_exata_afsim_dds: true" in manifest_text
    assert "license_review_required_before_replacement: true" in manifest_text


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
