#!/usr/bin/env python3
"""ROS Menu 1.0 preview: conservative install, activate and restore.

--install copies applet for current user (does not touch panel).
--activate swaps exactly the stock menu applet for ROS Menu, saving the
original complete applet list. --restore restores a selected backup.
Run only in disposable ROS-Test, never with sudo.
"""
import argparse
import ast
import datetime
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

HOME = Path.home()
ROOT = Path(__file__).resolve().parents[1]
UUID = "ros-menu@iamtherealroot"
STOCK = "menu@cinnamon.org"
SOURCE = ROOT / "desktop/applets" / UUID
TARGET = HOME / ".local/share/cinnamon/applets" / UUID
BACKUPS = HOME / ".config/ros/backups"

def run(*cmd):
    return subprocess.run(cmd, text=True, capture_output=True)

def get_applets():
    r = run("gsettings", "get", "org.cinnamon", "enabled-applets")
    if r.returncode:
        raise RuntimeError(r.stderr.strip())
    value = ast.literal_eval(r.stdout.strip())
    if not isinstance(value, list) or not all(isinstance(x, str) for x in value):
        raise RuntimeError("Unexpected enabled-applets format")
    return value

def validate():
    if os.geteuid() == 0:
        raise RuntimeError("Do not run with sudo")
    if TARGET.is_symlink() or any(p.is_symlink() for p in TARGET.parents if HOME in p.parents):
        raise RuntimeError("Refusing symlink in applet destination")
    for filename in ("applet.js", "metadata.json", "tree.svg"):
        if not (SOURCE / filename).is_file():
            raise RuntimeError("Source missing: " + filename)
    if TARGET.exists():
        raise RuntimeError("ROS Menu destination already exists; refusing overwrite")

def install():
    validate()
    shutil.copytree(SOURCE, TARGET, symlinks=False)
    print("ROS Menu files installed:", TARGET)
    print("Panel unchanged. Review before activating using --activate.")

def activate():
    if os.geteuid() == 0:
        raise RuntimeError("Do not run with sudo")
    if not (TARGET / "applet.js").is_file():
        raise RuntimeError("First install applet with --install")
    current = get_applets()
    old = [a for a in current if a.split(":")[3] == STOCK]
    if len(old) != 1 or any(a.split(":")[3] == UUID for a in current):
        raise RuntimeError("Expected exactly one stock menu and no ROS Menu; panel unchanged")
    parts = old[0].split(":")
    if len(parts) != 5:
        raise RuntimeError("Unknown stock menu format; no changes")
    used = {int(a.rsplit(":", 1)[1]) for a in current if a.rsplit(":", 1)[-1].isdigit()}
    new_id = max(used, default=0) + 1
    replacement = ":".join(parts[:4][:3] + [UUID, str(new_id)])
    updated = [replacement if a == old[0] else a for a in current]
    BACKUPS.mkdir(parents=True, exist_ok=True)
    backup = BACKUPS / ("ros-menu-" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f"))
    backup.mkdir()
    (backup / "panel.json").write_text(json.dumps({"original": current, "ros_menu": updated}, indent=2) + "\n")
    result = run("gsettings", "set", "org.cinnamon", "enabled-applets", str(updated))
    if result.returncode:
        raise RuntimeError("Failed to activate ROS Menu: " + result.stderr.strip())
    print("ROS Menu activated. Original panel backup:", backup)
    print("To undo: python3 scripts/install-ros-menu.py --restore", backup)

def restore(backup):
    if os.geteuid() == 0:
        raise RuntimeError("Do not run with sudo")
    backup = backup.expanduser().resolve()
    if not backup.is_relative_to(BACKUPS.resolve()):
        raise RuntimeError("Restore must reference a ROS backup directory")
    data = json.loads((backup / "panel.json").read_text())
    current = get_applets()
    if current != data["ros_menu"]:
        raise RuntimeError("Panel was customized after activation; refusing overwrite")
    result = run("gsettings", "set", "org.cinnamon", "enabled-applets", str(data["original"]))
    if result.returncode:
        raise RuntimeError(result.stderr.strip())
    print("Original Cinnamon menu restored. ROS applet files were preserved.")

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--install", action="store_true")
    mode.add_argument("--activate", action="store_true")
    mode.add_argument("--restore", type=Path)
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
    except (OSError, ValueError, RuntimeError, SyntaxError, IndexError, json.JSONDecodeError) as exc:
        print("ERROR:", exc, file=sys.stderr)
        sys.exit(1)
