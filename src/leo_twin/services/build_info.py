"""Version and build information helpers for operator diagnostics."""

from __future__ import annotations

import json
import platform
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import Any


VERSION_INFO_V1_ID = "leo_twin.version_info.v1"
PROJECT_ROOT = Path(__file__).resolve().parents[3]


def build_version_info_v1(
    project_root: Path | None = None,
    *,
    git_commit: str | None = None,
    git_branch: str | None = None,
    git_dirty: bool | None = None,
) -> dict[str, object]:
    """Return backend-owned version/build information for diagnostics."""

    root = PROJECT_ROOT if project_root is None else Path(project_root)
    pyproject = _pyproject_metadata(root / "pyproject.toml")
    frontend = _frontend_metadata(root / "frontend" / "package.json")
    commit = git_commit if git_commit is not None else _git_output(root, "rev-parse", "HEAD")
    branch = (
        git_branch
        if git_branch is not None
        else _git_output(root, "rev-parse", "--abbrev-ref", "HEAD")
    )
    dirty = git_dirty if git_dirty is not None else _git_dirty(root)
    return {
        "type": "VERSION_INFO",
        "version_info_id": VERSION_INFO_V1_ID,
        "version": "v1",
        "project": {
            "name": pyproject.get("name", "leo-twin"),
            "backend_version": pyproject.get("version", "0.0.0"),
            "description": pyproject.get("description", ""),
        },
        "frontend": {
            "name": frontend.get("name", ""),
            "version": frontend.get("version", ""),
            "private": frontend.get("private", False),
        },
        "git": {
            "commit": commit,
            "short_commit": commit[:7] if commit and commit != "unknown" else "unknown",
            "branch": branch,
            "dirty": dirty,
            "source": "git command" if commit != "unknown" or branch != "unknown" else "unknown",
        },
        "runtime": {
            "python_version": platform.python_version(),
            "python_executable": Path(sys.executable).name,
            "platform": platform.system(),
        },
        "diagnostic_endpoints": (
            "/health",
            "/runtime/status",
            "/runtime/version",
            "/runtime/export",
            "/runtime/export/catalog",
        ),
        "constraints": {
            "event_kernel_frozen": True,
            "packet_level_simulation": False,
            "forbidden_integrations": ("STK", "EXATA", "AFSIM", "DDS"),
        },
    }


def _pyproject_metadata(path: Path) -> dict[str, Any]:
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except OSError:
        return {}
    project = data.get("project", {})
    return dict(project) if isinstance(project, dict) else {}


def _frontend_metadata(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _git_output(root: Path, *args: str) -> str:
    try:
        completed = subprocess.run(
            ("git", *args),
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return "unknown"
    return completed.stdout.strip() or "unknown"


def _git_dirty(root: Path) -> bool:
    try:
        completed = subprocess.run(
            ("git", "status", "--short"),
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return bool(completed.stdout.strip())
