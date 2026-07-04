from __future__ import annotations

from pathlib import Path
import tomllib


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_project_metadata_describes_full_system_platform() -> None:
    pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    description = pyproject["project"]["description"]

    assert "communication-computing digital twin simulation platform" in description
    assert "MVP-0 skeleton" not in description


def test_readme_declares_full_system_engineering_phase() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    assert "full-system engineering iteration" in readme
    assert "Chinese frontend surfaces" in readme
    assert "The current phase is **MVP-0**" not in readme
