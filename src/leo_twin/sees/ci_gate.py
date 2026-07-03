"""CI gate for deterministic reviewer decisions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from leo_twin.reviewer.reviewer_engine import review_path


class CIGate:
    """Block merge unless the reviewer decision is PASS."""

    def evaluate_report(self, report: dict[str, Any]) -> int:
        return 0 if report["decision"] == "PASS" else 1

    def review_workspace(self, workspace: str | Path) -> tuple[int, dict[str, Any]]:
        root = Path(workspace)
        report = review_path(root, repository_root=root)
        return self.evaluate_report(report), report
