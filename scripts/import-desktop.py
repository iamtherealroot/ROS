#!/usr/bin/env python3
"""Import *local, reviewed* ROS desktop sources into a ROS checkout.

Default: report only. --apply: copy selected source assets to desktop/.
Never commits/pushes; never reads passwords, tokens or general home files.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
HOME = Path.home()

SOURCES = [
    ("desktop/themes/ROS-Dark", HOME / ".themes/ROS-Dark"),
    ("desktop/themes/ROS-Gaming", HOME / ".themes/ROS-Gaming"),
    ("desktop/themes/ROS-IT", HOME / ".themes/ROS-IT"),
    ("desktop/themes/ROS-Creator", HOME / ".themes/ROS-Creator"),
    ("desktop/themes/ROS-Stealth", HOME / ".themes/ROS-Stealth"),
    ("desktop/themes/ROS-Nordic", HOME / ".themes/ROS-Nordic"),
    ("desktop/icons/ROS-Icons", HOME / ".local/share/icons/ROS-Icons"),
    ("desktop/applets/ros-power-tree@iamtherealroot", HOME / ".local/share/cinnamon/applets/ros-power-tree@iamtherealroot"),
    ("desktop/bin/ros-theme", HOME / ".local/bin/ros-theme"),
    ("desktop/applications/ros-theme-selector.desktop", HOME / ".local/share/applications/ros-theme-selector.desktop"),
]
ALLOWED_SUFFIXES = {".css", ".svg", ".png", ".json", ".js", ".theme", ".desktop", ".sh", ".py"}
ALLOWED_NAMES = {"ros-theme", "index.theme", "metadata.json"}
MAX_FILE = 3 * 1024 * 1024
MAX_TOTAL = 30 * 1024 * 1024
BLOCKED_PARTS = {".git", ".ssh", ".gnupg", "node_modules", "__pycache__", ".cache"}
BLOCKED_SUFFIXES = {".key", ".pem", ".p12", ".pfx", ".db", ".sqlite", ".sqlite3", ".log", ".bak"}

def safe_file(p: Path, root: Path) -> bool:
    if p.is_symlink() or not p.is_file():
        return False
    try:
        relative = p.relative_to(root)
    except ValueError:
        return False
    if any(part in BLOCKED_PARTS or part.startswith(".") for part in relative.parts):
        return False
    if p.suffix.lower() in BLOCKED_SUFFIXES:
        return False
    return (p.suffix.lower() in ALLOWED_SUFFIXES or p.name in ALLOWED_NAMES) and p.stat().st_size <= MAX_FILE

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true", help="copy only selected source assets into checkout")
    args = ap.parse_args()
    if not (ROOT / ".git").exists():
        print("Error: expected a ROS Git checkout.", file=sys.stderr)
        return 2
    if subprocess.run(["git", "-C", str(ROOT), "diff", "--quiet"], check=False).returncode:
        print("Working tree contains changes: review those first.", file=sys.stderr)
        return 2
    candidates: list[tuple[Path, Path]] = []
    total = 0
    for destination, source in SOURCES:
        if source.is_symlink():
            print(f"SKIP symlink: {source.name}")
            continue
        if not source.exists():
            print(f"MISSING: {source}")
            continue
        files = [source] if source.is_file() else sorted(source.rglob("*"))
        count = 0
        for file in files:
            origin_root = source.parent if source.is_file() else source
            if not safe_file(file, origin_root):
                continue
            relative = Path(file.name) if source.is_file() else file.relative_to(source)
            target = ROOT / destination
            if source.is_dir():
                target = target / relative
            candidates.append((file, target))
            total += file.stat().st_size
            count += 1
        print(f"{destination}: {count} source files")
    print(f"Total: {len(candidates)} files, {total / (1024 * 1024):.2f} MiB")
    if total > MAX_TOTAL:
        print("Error: import size cap exceeded.", file=sys.stderr)
        return 2
    if not args.apply:
        print("DRY RUN ONLY. To copy: python3 scripts/import-desktop.py --apply")
        return 0
    collisions = [dest for _, dest in candidates if dest.exists()]
    if collisions:
        print(f"Refusing to overwrite {len(collisions)} existing repository files; inspect first:", file=sys.stderr)
        for p in collisions[:15]:
            print(f"  {p.relative_to(ROOT)}", file=sys.stderr)
        return 2
    for source, target in candidates:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target, follow_symlinks=False)
    print("Copied into local checkout only. Inspect before git add/commit/push:")
    print("  git status --short")
    print("  git diff --no-index /dev/null desktop/bin/ros-theme")
    print("  git add desktop && git diff --cached --stat")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
