#!/usr/bin/env python3
"""ROS Development panel cleanup: keep ROS Network Native, remove duplicate indicators.

--check is read-only. --apply creates a complete panel backup before changing
org.cinnamon enabled-applets. --restore refuses to overwrite later edits.
Intentionally does not touch NetworkManager, connectivity, or applet files.
"""
import argparse
import ast
from datetime import datetime
import json
import os
from pathlib import Path
import subprocess
import sys

HOME = Path.home()
BACKUPS = HOME / ".config/ros/backups"
KEEP = "ros-network-native@iamtherealroot"
REMOVE = {"network@cinnamon.org", "ros-network@iamtherealroot"}
KEY = ["org.cinnamon", "enabled-applets"]

def get_applets():
    p = subprocess.run(["gsettings", "get", *KEY], check=True, capture_output=True, text=True)
    values = ast.literal_eval(p.stdout.strip())
    if not isinstance(values, list) or not all(isinstance(v, str) and len(v.split(":")) == 5 for v in values):
        raise ValueError("Unrecognized Cinnamon panel configuration")
    return values

def put_applets(values):
    subprocess.run(["gsettings", "set", *KEY, str(values)], check=True)

def key_id(value):
    return value.split(":")[3]

def check():
    old = get_applets()
    native = [x for x in old if key_id(x) == KEEP]
    if len(native) != 1:
        raise ValueError("Exactly one ROS Network Native applet required; no change made")
    if not (HOME / ".local/share/cinnamon/applets" / KEEP / "applet.js").is_file():
        raise ValueError("ROS Network Native code not installed")
    removed = [x for x in old if key_id(x) in REMOVE]
    updated = [x for x in old if key_id(x) not in REMOVE]
    print("Keeping:", native[0])
    print("Removing only duplicate indicators:")
    for item in removed:
        print(" -", item)
    print("Other panel applets unchanged:", len(old) - len(removed))
    return old, updated, removed

def apply():
    old, updated, removed = check()
    if not removed:
        print("No duplicate network indicators; nothing to do")
        return
    BACKUPS.mkdir(parents=True, exist_ok=True)
    backup = BACKUPS / ("ros-network-cleanup-" + datetime.now().strftime("%Y%m%d-%H%M%S-%f"))
    backup.mkdir()
    (backup / "panel.json").write_text(json.dumps({"before": old, "after": updated}, indent=2) + "\n")
    put_applets(updated)
    print("Panel cleaned. Backup:", backup)
    print("Restore:", "python3 scripts/cleanup-ros-network.py --restore", backup)

def restore(path):
    backup = path.expanduser().resolve()
    if not backup.is_relative_to(BACKUPS.resolve()):
        raise ValueError("Backup must be inside ~/.config/ros/backups")
    record = json.loads((backup / "panel.json").read_text())
    if get_applets() != record["after"]:
        raise ValueError("Current panel differs from backup target; refusing to overwrite later changes")
    put_applets(record["before"])
    print("Original panel restored")

def main():
    if os.geteuid() == 0:
        raise ValueError("Run as desktop user, not root")
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--restore", type=Path)
    args = parser.parse_args()
    if args.restore:
        restore(args.restore)
    elif args.apply:
        apply()
    else:
        check()
        print("Dry run: no panel changes. Use --apply.")

if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, SyntaxError, KeyError, subprocess.CalledProcessError, json.JSONDecodeError) as e:
        print("ERROR:", e, file=sys.stderr)
        sys.exit(1)
