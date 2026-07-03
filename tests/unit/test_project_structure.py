from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_required_project_directories_exist() -> None:
    required_directories = [
        "src/leo_twin/core",
        "src/leo_twin/schema",
        "src/leo_twin/models",
        "src/leo_twin/services",
        "src/leo_twin/adapters",
        "src/leo_twin/examples",
        "tests/unit",
        "tests/integration",
        "tests/scale",
        "docs",
        "configs",
    ]

    missing = [
        path
        for path in required_directories
        if not (PROJECT_ROOT / path).is_dir()
    ]

    assert missing == []
