from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_launcher_script_exposes_one_click_acceptance_summary() -> None:
    script = PROJECT_ROOT / "scripts" / "sees_launcher.ps1"
    text = script.read_text(encoding="utf-8")

    assert "one_click_acceptance_v1" in text
    assert "leo_twin.launcher_one_click_acceptance.v1" in text
    assert "blocking_services" in text
    assert "scripts\\smoke_runtime_health.ps1" in text
    assert "One-click acceptance:" in text


def test_launcher_script_discovers_bundled_node_and_pnpm() -> None:
    script = PROJECT_ROOT / "scripts" / "sees_launcher.ps1"
    text = script.read_text(encoding="utf-8")

    assert "Add-KnownToolchainPaths" in text
    assert "LEO_TWIN_DEPENDENCIES_ROOT" in text
    assert ".cache\\codex-runtimes\\codex-primary-runtime\\dependencies" in text
    assert "bin\\fallback" in text
    assert "node\\bin" in text
    assert "corepack enable" in text
