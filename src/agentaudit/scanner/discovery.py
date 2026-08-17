from pathlib import Path


IGNORED_DIRECTORIES = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".tox",
    "node_modules",
    "*.egg-info"
}

IGNORED_FILES = {
    ".DS_Store",
}

IGNORED_SUFFIXES = {
    ".pyc",
    ".pyo",
}


def discover_files(root: Path) -> list[Path]:
    """Discover relevant repository files.

    The function returns deterministic, recursively discovered files while
    excluding generated artifacts, virtual environments, caches, and
    compiled Python files.
    """

    if not root.exists():
        raise FileNotFoundError(f"Repository path does not exist: {root}")

    if not root.is_dir():
        raise NotADirectoryError(f"Expected a directory: {root}")

    files: list[Path] = []

    for path in root.rglob("*"):
        if not path.is_file():
            continue

        if any(part in IGNORED_DIRECTORIES for part in path.parts):
            continue

        if any(part.endswith(".egg-info") for part in path.parts):
            continue

        if path.name in IGNORED_FILES:
            continue

        if path.suffix in IGNORED_SUFFIXES:
            continue

        files.append(path)

    return sorted(files)