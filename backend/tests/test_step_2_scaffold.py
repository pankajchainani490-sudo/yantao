from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

REQUIRED_DIRS = [
    "backend/app",
    "backend/app/api",
    "backend/app/api/routes",
    "backend/app/core",
    "backend/app/schemas",
    "backend/app/services",
    "backend/tests",
    "frontend/src",
    "frontend/src/pages",
    "frontend/src/components",
    "frontend/src/api",
    "frontend/src/layouts",
    "frontend/src/router",
    "frontend/src/hooks",
    "frontend/src/utils",
    "frontend/src/mock",
    "frontend/src/styles",
    "ml/data/raw",
    "ml/data/interim",
    "ml/data/processed",
    "ml/data/sample",
    "ml/models",
    "ml/reports",
    "ml/configs",
    "ml/notebooks",
    "deploy/nginx",
    "deploy/systemd",
    "deploy/docker",
    "deploy/ubuntu",
    "docs/architecture",
    "docs/dataset",
    "docs/test",
    "docs/deployment",
    "docs/demo",
    "docs/report",
    "ppt/assets",
    "ppt/charts",
    "ppt/script",
    "scripts/dev",
    "scripts/seed",
    "scripts/capture",
    "scripts/train",
    "scripts/replay",
]

REQUIRED_FILES = [
    "backend/app/main.py",
    "backend/requirements.txt",
    "backend/README.md",
    "frontend/package.json",
    "frontend/src/App.tsx",
    "frontend/src/main.tsx",
    "frontend/README.md",
]


def test_step_2_required_directories_exist() -> None:
    missing = [path for path in REQUIRED_DIRS if not (PROJECT_ROOT / path).is_dir()]
    assert not missing, f"Missing directories: {missing}"


def test_step_2_required_files_exist() -> None:
    missing = [path for path in REQUIRED_FILES if not (PROJECT_ROOT / path).is_file()]
    assert not missing, f"Missing files: {missing}"
