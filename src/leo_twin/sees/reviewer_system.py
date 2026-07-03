"""SEES wrapper around the deterministic reviewer system."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from leo_twin.reviewer.reviewer_engine import review_path, to_json


class ReviewerSystem:
    """Run the static reviewer against a workspace or diff path."""

    def review_workspace(self, workspace: str | Path) -> dict[str, Any]:
        return review_path(Path(workspace), repository_root=Path(workspace))

    def review_diff(
        self,
        diff_path: str | Path,
        repository_root: str | Path,
    ) -> dict[str, Any]:
        return review_path(Path(diff_path), repository_root=Path(repository_root))

    def report_json(self, report: dict[str, Any]) -> str:
        return to_json(report)
