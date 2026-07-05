from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_dashboard_information_architecture_css_hook_is_present() -> None:
    app_css = (ROOT / "frontend" / "src" / "app" / "App.css").read_text(
        encoding="utf-8"
    )
    data_panel = (
        ROOT / "frontend" / "src" / "dashboard" / "data_panel" / "DataPanel.tsx"
    ).read_text(encoding="utf-8")

    assert ".data-panel-grid .data-panel-configuration-explanation" in app_css
    assert ".data-panel-grid .data-panel-information-architecture" in app_css
    assert "grid-column: span 2" in app_css
    assert "data-panel-information-architecture" in data_panel
