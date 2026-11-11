#!/usr/bin/env python3
"""Install ROS Network alongside stock Cinnamon network indicator.

--install only copies files; --activate adds an additional indicator to the
same panel zone as the native network applet; --restore restores exact snapshot.
No sudo. No deletion of existing network controls.
"""
import argparse
import ast
from datetime import datetime
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

HOME = Path.home()
ROOT = Path(__file__).resolve().parents[1]
UUID = "ros-network@iamtherealroot"
SOURCE = ROOT / "desktop/applets" / UUID
TARGET = HOME / ".local/share/cinnamon/applets" / UUID
BACKUPS = HOME / ".config/ros/backups"

def applets():
    result = subprocess.run(["gsettings", "get", "org.cinnamon", "enabled-applets"], capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stderr)
    value = ast.literal_eval(result.stdout.strip())
    if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
        raise RuntimeError("Unexpected enabled-applets format")
    return value

def uuid_of(value):
    parts = value.split(":")
    if len(parts) != 5:
        raise RuntimeError("Unknown Cinnamon applet format: " + value)
    return parts[3]

def write_applets(values):
    result = subprocess.run(["gsettings", "set", "org.cinnamon", "enabled-applets", str(values)], capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stderr)

def install():
    if TARGET.is_symlink():
        raise RuntimeError("Applet install target is a symlink")
    if TARGET.exists():
        raise RuntimeError("Already installed; no files changed")
    for file in ["applet.js", "metadata.json", "connected.svg", "disconnected.svg"]:
        if not (SOURCE / file).is_file():
            raise RuntimeError("Missing source: " + file)
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(SOURCE, TARGET, symlinks=False)
    print("Installed applet files. Panel not changed.")
    print("Next: python3 scripts/install-ros-network.py --activate")

def activate():
    if not (TARGET / "applet.js").is_file():
        raise RuntimeError("Applet not installed; first use --install")
    current = applets()
    if any(uuid_of(a) == UUID for a in current):
        raise RuntimeError("ROS Network is already in the panel")
    native = [(i, a.split(":")) for i, a in enumerate(current) if uuid_of(a) == "network@cinnamon.org"]
    if len(native) != 1:
        raise RuntimeError("Expected exactly one stock network applet; no changes made")
    idx, parts = native[0]
    used_ids = [int(a.split(":")[4]) for a in current if a.split(":")[4].isdigit()]
    unique = max(used_ids, default=0) + 1
    new = ":".join(parts[:3] + [UUID, str(unique)])
    changed = current[:idx+1] + [new] + current[idx+1:]
    BACKUPS.mkdir(parents=True, exist_ok=True)
    backup = BACKUPS / ("ros-network-" + datetime.now().strftime("%Y%m%d-%H%M%S-%f"))
    backup.mkdir()
    (backup / "panel.json").write_text(json.dumps({"original": current, "installed": changed}, indent=2) + "\n")
    write_applets(changed)
    print("ROS Network added alongside the original network indicator.")
    print("Backup:", backup)
    print("Restore with: python3 scripts/install-ros-network.py --restore", backup)

def restore(path):
    path = path.expanduser().resolve()
    if not path.is_relative_to(BACKUPS.resolve()):
        raise RuntimeError("Backup is outside ROS backup directory")
    data = json.loads((path / "panel.json").read_text())
    current = applets()
    if current != data["installed"]:
        raise RuntimeError("Panel changed since this backup; refusing to overwrite")
    write_applets(data["original"])
    print("Original panel restored; ROS Network applet files retained.")

def main():
    if os.geteuid() == 0:
        raise RuntimeError("Do not run this program with sudo")
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--install", action="store_true")
    group.add_argument("--activate", action="store_true")
    group.add_argument("--restore", type=Path)
    args = parser.parse_args()
    if args.install:
        install()
    elif args.activate:
        activate()
    else:
        restore(args.restore)

if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, SyntaxError, RuntimeError, KeyError, json.JSONDecodeError) as e:
        print("ERROR:", e, file=sys.stderr)
        sys.exit(1)
