#!/usr/bin/env python3
"""Stage ROS desktop files into an extracted Mint root filesystem.

This is an OVERLAY STAGER, NOT an ISO writer or an installer. It never executes
chroot, apt, mount, useradd, or LightDM configuration. Run against a disposable
copy of the extracted filesystem, never the host's / or a real installation.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
THEMES = ("Dark", "Gaming", "IT", "Creator", "Stealth", "Nordic")
ROUTES = (
    [(f"desktop/themes/ROS-{x}", f"etc/skel/.themes/ROS-{x}") for x in THEMES]
    + [
        ("desktop/icons/ROS-Icons", "etc/skel/.local/share/icons/ROS-Icons"),
        ("desktop/applets/ros-power-tree@iamtherealroot", "etc/skel/.local/share/cinnamon/applets/ros-power-tree@iamtherealroot"),
        ("apps/designs/assets", "etc/skel/.local/share/ros/designs/assets"),
        ("apps/designs/designs.py", "etc/skel/.local/share/ros/designs/designs.py"),
        ("apps/designs/launch.sh", "etc/skel/.local/bin/ros-designs"),
        ("apps/designs/designs.desktop", "etc/skel/.local/share/applications/ros-theme-selector.desktop"),
        ("desktop/bin/ros-theme", "etc/skel/.local/bin/ros-theme"),
        ("desktop/applications/ros-terminal.desktop", "etc/skel/.local/share/applications/ros-terminal.desktop"),
        ("desktop/config/theme-palettes.txt", "etc/skel/.config/ros/theme-palettes.txt"),
        ("scripts/configure-first-login.py", "usr/local/lib/ros/configure-first-login.py"),
        ("iso/session-init.py", "usr/local/lib/ros/session-init.py"),
        ("iso/ros-session-init.desktop", "etc/skel/.config/autostart/ros-session-init.desktop"),
    ]
    + [
        (f"desktop/backgrounds/ROS-{x}{'.png' if x == 'Dark' else '.jpg'}",
         f"etc/skel/.local/share/backgrounds/ros/ROS-{x}{'.png' if x == 'Dark' else '.jpg'}")
        for x in THEMES
    ]
)

def in_tree(base, rel):
    if Path(rel).is_absolute() or ".." in Path(rel).parts:
        raise ValueError("Unsafe relative path: " + rel)
    p = base / rel
    if any(x.is_symlink() for x in [p, *list(p.parents)[:len(Path(rel).parts)]]):
        raise ValueError("Symlink in destination path: " + str(p))
    if not p.resolve().is_relative_to(base.resolve()):
        raise ValueError("Destination escapes rootfs: " + str(p))
    return p

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--rootfs", type=Path, required=True, help="disposable EXTRACTED Mint filesystem directory")
    p.add_argument("--apply", action="store_true", help="write overlay into rootfs (dry run by default)")
    args = p.parse_args()
    target = args.rootfs.resolve()
    if os.geteuid() == 0:
        raise ValueError("Run as regular user against user-owned staging files")
    if target == Path("/") or target == Path.home().resolve() or target == ROOT.resolve():
        raise ValueError("Refusing dangerous destination")
    if not target.is_dir() or not (target / "etc").is_dir() or not (target / "usr").is_dir():
        raise ValueError("Target must be a pre-extracted filesystem with etc/ and usr/")
    if not os.access(target, os.W_OK):
        raise ValueError("Target not writable; use a separate user-owned staging directory")
    plan = []
    for src, dst in ROUTES:
        source = ROOT / src
        dest = in_tree(target, dst)
        if source.is_symlink() or not source.exists():
            raise ValueError("Missing or symlinked source: " + str(source))
        if dest.exists():
            raise ValueError("Target already exists; use a fresh staging rootfs: " + str(dest))
        plan.append((source, dest, src, dst))
    print("ROS ISO overlay stage 0.1 —", "APPLY" if args.apply else "DRY RUN")
    for _, _, src, dst in plan:
        print(src, "->", dst)
    if not args.apply:
        print("No files changed. This does NOT produce a bootable ISO.")
        return
    for src, dest, _, _ in plan:
        dest.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            shutil.copytree(src, dest, symlinks=False)
        else:
            shutil.copy2(src, dest)
    for rel in ("etc/skel/.local/bin/ros-designs", "etc/skel/.local/bin/ros-theme"):
        file = in_tree(target, rel)
        file.chmod(file.stat().st_mode | 0o111)
    checksums = {}
    for _, dest, _, dst in plan:
        if dest.is_file():
            checksums[dst] = hashlib.sha256(dest.read_bytes()).hexdigest()
        else:
            for file in sorted(dest.rglob("*")):
                if file.is_file():
                    checksums[str(file.relative_to(target))] = hashlib.sha256(file.read_bytes()).hexdigest()
    manifest = {"stage_version": "0.1", "iso_created": False, "boot_tested": False, "files": checksums}
    output = target / "var/lib/ros/overlay-manifest.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print("Staged", len(checksums), "files. No bootable ISO created.")
    print("Manifest:", output)

if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as exc:
        print("ERROR:", exc, file=sys.stderr)
        sys.exit(1)
