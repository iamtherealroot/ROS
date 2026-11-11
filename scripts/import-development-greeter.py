#!/usr/bin/env python3
"""Import reviewed ROS Development greeter artwork into the source checkout.

Run as the ordinary account on the Development VM. Dry-run by default.
Copies ONLY the explicitly allowlisted public artwork, never /etc credentials.
Does not modify LightDM or make a git commit.
"""
import argparse
import hashlib
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
FILES = {
    "/usr/share/backgrounds/ros/login.png": "branding/lightdm/login.png",
    "/usr/share/backgrounds/ros/desktop.png": "branding/lightdm/desktop.png",
    "/usr/share/backgrounds/ros/wallpaper.png": "branding/lightdm/wallpaper.png",
    "/usr/share/pixmaps/ros/logo.png": "branding/lightdm/logo.png",
    "/usr/share/pixmaps/ros/tree.png": "branding/lightdm/tree.png",
    "/usr/share/pixmaps/ros/tree.svg": "branding/lightdm/tree.svg",
}

def validate(src, name):
    if not src.is_file() or src.is_symlink():
        raise ValueError(f"Missing or symlinked source: {src}")
    if src.stat().st_size > 15_000_000:
        raise ValueError(f"Artwork unexpectedly large: {src}")
    with src.open("rb") as f:
        start = f.read(100)
    if name.endswith(".png") and not start.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError(f"Not a PNG: {src}")
    if name.endswith(".svg") and not (b"<svg" in start or b"<?xml" in start):
        raise ValueError(f"Not an SVG: {src}")

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    print("ROS Development greeter artwork import —", "APPLY" if args.apply else "DRY RUN")
    for source, relative in FILES.items():
        src, dest = Path(source), ROOT / relative
        validate(src, relative)
        if dest.exists() or dest.is_symlink():
            raise ValueError(f"Already exists; refusing overwrite: {dest}")
        print(f"{src} -> {dest.relative_to(ROOT)}  SHA256:{hashlib.sha256(src.read_bytes()).hexdigest()[:12]}")
    if not args.apply:
        print("No changes made. Re-run with --apply on ROS Development.")
        return
    for source, relative in FILES.items():
        dest = ROOT / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest)
        dest.chmod(0o644)
    print("Imported 6 artworks into working tree. Review with git status before committing.")
    print("No system settings or login behavior changed.")

if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as exc:
        print("ERROR:", exc, file=sys.stderr)
        sys.exit(1)
