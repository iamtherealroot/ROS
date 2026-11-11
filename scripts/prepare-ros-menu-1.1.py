#!/usr/bin/env python3
"""Prepare a ROS Menu 1.1 update on ROS-Development with the stock menu as fallback.

This script does not activate the preview. It replaces the active ROS Menu
panel entry temporarily with stock Cinnamon menu, backs up old applet files,
and copies new files. Then log out and in, run install-ros-menu.py --activate.
"""
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
UUID = "ros-menu@iamtherealroot"
STOCK = "menu@cinnamon.org"
SOURCE = ROOT / "desktop/applets" / UUID
TARGET = HOME / ".local/share/cinnamon/applets" / UUID
BACKUPS = HOME / ".config/ros/backups"

def read_panel():
    p = subprocess.run(["gsettings", "get", "org.cinnamon", "enabled-applets"], capture_output=True, text=True, check=True)
    current = ast.literal_eval(p.stdout.strip())
    if not isinstance(current, list) or not all(isinstance(a, str) and len(a.split(":")) == 5 for a in current):
        raise ValueError("Unexpected Cinnamon panel layout")
    return current

def write_panel(values):
    subprocess.run(["gsettings", "set", "org.cinnamon", "enabled-applets", str(values)], check=True)

def main():
    if os.geteuid() == 0:
        raise ValueError("Never run with sudo")
    current = read_panel()
    old = [a for a in current if a.split(":")[3] == UUID]
    stock = [a for a in current if a.split(":")[3] == STOCK]
    if len(old) != 1 or stock:
        raise ValueError("Expected one active ROS Menu and no Cinnamon menu; no changes made")
    if TARGET.is_symlink() or not TARGET.is_dir():
        raise ValueError("ROS Menu install not found or is symlinked")
    for name in ("applet.js", "metadata.json", "tree.svg"):
        if not (SOURCE / name).is_file() or (SOURCE / name).is_symlink():
            raise ValueError("Missing source: " + name)
    parts = old[0].split(":")
    parts[3] = STOCK
    replacement = ":".join(parts)
    changed = [replacement if a == old[0] else a for a in current]
    BACKUPS.mkdir(parents=True, exist_ok=True)
    backup = BACKUPS / ("ros-menu-upgrade-" + datetime.now().strftime("%Y%m%d-%H%M%S-%f"))
    shutil.copytree(TARGET, backup / "applet")
    (backup / "panel.json").write_text(json.dumps({"before": current, "stock": changed}, indent=2) + "\n")
    write_panel(changed)
    for name in ("applet.js", "metadata.json", "tree.svg"):
        shutil.copy2(SOURCE / name, TARGET / name)
    print("ROS Menu 1.1 files installed, Cinnamon stock menu temporarily active")
    print("Backup:", backup)
    print("Sign out and sign back in before activating the new menu")
    print("Then: python3 scripts/install-ros-menu.py --activate")
    print("If new version fails, restore stock menu with install-ros-menu.py --restore and its activation backup")

if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, SyntaxError, subprocess.CalledProcessError) as exc:
        print("ERROR:", exc, file=sys.stderr)
        sys.exit(1)
