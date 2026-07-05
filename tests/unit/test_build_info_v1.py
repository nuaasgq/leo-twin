from __future__ import annotations

import json
from pathlib import Path

from leo_twin.services.build_info import (
    VERSION_INFO_V1_ID,
    build_version_info_v1,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_build_version_info_v1_reads_project_and_frontend_versions() -> None:
    info = build_version_info_v1(
        PROJECT_ROOT,
        git_commit="abcdef1234567890",
        git_branch="feature/version",
        git_dirty=False,
    )

    assert info["type"] == "VERSION_INFO"
    assert info["version_info_id"] == VERSION_INFO_V1_ID
    assert info["project"]["name"] == "leo-twin"  # type: ignore[index]
    assert info["project"]["backend_version"] == "0.0.0"  # type: ignore[index]
    assert info["frontend"]["name"] == "leo-twin-observability-frontend"  # type: ignore[index]
    assert info["frontend"]["version"] == "0.0.0"  # type: ignore[index]
    assert info["git"] == {  # type: ignore[index]
        "commit": "abcdef1234567890",
        "short_commit": "abcdef1",
        "branch": "feature/version",
        "dirty": False,
        "source": "git command",
    }
    assert "/runtime/version" in info["diagnostic_endpoints"]
    assert info["constraints"]["event_kernel_frozen"] is True  # type: ignore[index]
    assert info["constraints"]["packet_level_simulation"] is False  # type: ignore[index]
    assert json.loads(json.dumps(info, sort_keys=True))["version_info_id"] == (
        VERSION_INFO_V1_ID
    )


def test_build_version_info_v1_handles_unknown_git_values() -> None:
    info = build_version_info_v1(
        PROJECT_ROOT,
        git_commit="unknown",
        git_branch="unknown",
        git_dirty=True,
    )

    assert info["git"]["commit"] == "unknown"  # type: ignore[index]
    assert info["git"]["short_commit"] == "unknown"  # type: ignore[index]
    assert info["git"]["dirty"] is True  # type: ignore[index]
