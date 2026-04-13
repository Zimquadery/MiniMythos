import os
from pathlib import Path

SKIP_DIRS = {
    ".git",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
    "dist",
    "build",
    ".tox",
    ".mypy_cache",
    ".pytest_cache",
}
SKIP_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".bmp",
    ".ico",
    ".svg",
    ".woff",
    ".woff2",
    ".ttf",
    ".eot",
    ".mp3",
    ".mp4",
    ".zip",
    ".tar",
    ".gz",
    ".rar",
    ".7z",
    ".pdf",
    ".lock",
}

SKIP_SUFFIXES = {
    ".min.js",
    ".min.css",
}


def discover_code_files(root: Path) -> list[Path]:
    result: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fname in filenames:
            lower = fname.lower()
            ext = Path(fname).suffix.lower()
            if ext in SKIP_EXTENSIONS:
                continue
            if any(lower.endswith(s) for s in SKIP_SUFFIXES):
                continue
            full = Path(dirpath) / fname
            result.append(full.relative_to(root))
    return sorted(result)


def group_by_directory(files: list[Path]) -> dict[Path, list[Path]]:
    groups: dict[Path, list[Path]] = {}
    for f in files:
        parent = f.parent
        groups.setdefault(parent, []).append(f)
    return groups


def batch_files(files: list[Path], batch_size: int) -> list[list[Path]]:
    groups = group_by_directory(files)
    ordered: list[Path] = []
    for dir_files in groups.values():
        ordered.extend(dir_files)
    batches: list[list[Path]] = []
    for i in range(0, len(ordered), batch_size):
        batches.append(ordered[i : i + batch_size])
    return batches
