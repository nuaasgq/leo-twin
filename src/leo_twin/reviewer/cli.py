"""Command-line interface for the deterministic LEO-Twin reviewer."""

import argparse
import sys
from pathlib import Path

from leo_twin.reviewer.reviewer_engine import review_path, summary, to_json


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="leo-twin-review",
        description="Run deterministic structural review for LEO-Twin changes.",
    )
    parser.add_argument(
        "--diff",
        required=True,
        help="Path to a git diff file or a file-tree snapshot directory.",
    )
    parser.add_argument(
        "--commit-message",
        default="",
        help="Optional commit message text for future policy checks.",
    )
    args = parser.parse_args(argv)

    report = review_path(
        Path(args.diff),
        repository_root=Path.cwd(),
        commit_message=args.commit_message,
    )
    print(to_json(report))
    print(summary(report), file=sys.stderr)
    return 0 if report["decision"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
