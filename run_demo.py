"""Run the LEO-Twin full-system integration demo."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from examples.integration_demo.server import main


if __name__ == "__main__":
    raise SystemExit(main())
