from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_browser_acceptance_smoke_scripts_are_documented_and_wired() -> None:
    wrapper = PROJECT_ROOT / "browser_smoke_leo_twin.bat"
    powershell_script = PROJECT_ROOT / "scripts/smoke_browser_acceptance.ps1"
    node_script = PROJECT_ROOT / "scripts/smoke_browser_acceptance.mjs"
    acceptance = PROJECT_ROOT / "scripts/verify_product_acceptance.ps1"
    user_guide = PROJECT_ROOT / "docs/user_guide_v2.md"
    current_status = PROJECT_ROOT / "docs/current_product_status.md"

    assert wrapper.exists()
    assert powershell_script.exists()
    assert node_script.exists()

    assert "smoke_browser_acceptance.ps1" in wrapper.read_text(encoding="utf-8")
    assert "smoke_browser_acceptance.mjs" in powershell_script.read_text(
        encoding="utf-8"
    )
    assert "--frontend-url" in node_script.read_text(encoding="utf-8")
    assert "--backend-url" in node_script.read_text(encoding="utf-8")
    assert "pageerror" in node_script.read_text(encoding="utf-8")

    acceptance_text = acceptance.read_text(encoding="utf-8")
    assert "$RunBrowserSmoke" in acceptance_text
    assert "smoke_browser_acceptance.ps1" in acceptance_text

    guide_text = user_guide.read_text(encoding="utf-8")
    status_text = current_status.read_text(encoding="utf-8")
    assert ".\\browser_smoke_leo_twin.bat" in guide_text
    assert ".\\scripts\\smoke_browser_acceptance.ps1 -JsonSummary" in guide_text
    assert "-RunBrowserSmoke" in guide_text
    assert "Browser acceptance smoke" in status_text
