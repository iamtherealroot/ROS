#!/usr/bin/env python3
"""Build a ROS-styled copy of the locally installed Cinnamon network applet.

Cinnamon 6.6.9 only. Original system applet and existing ROS Network indicator
are untouched. Preview/install/activate/restore are explicit and reversible.
"""
import argparse
import ast
from datetime import datetime
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

UUID = "ros-network-native@iamtherealroot"
NATIVE = "network@cinnamon.org"
HOME = Path.home()
ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path("/usr/share/cinnamon/applets") / NATIVE
ICONS = ROOT / "desktop/applets/ros-network@iamtherealroot"
TARGET = HOME / ".local/share/cinnamon/applets" / UUID
BACKUPS = HOME / ".config/ros/backups"
PATTERN = "this.set_applet_icon_symbolic_name(name);"

def enabled():
    proc = subprocess.run(["gsettings", "get", "org.cinnamon", "enabled-applets"], capture_output=True, text=True, check=True)
    value = ast.literal_eval(proc.stdout.strip())
    if not isinstance(value, list) or not all(isinstance(v, str) and len(v.split(":")) == 5 for v in value):
        raise ValueError("Unrecognized Cinnamon enabled-applets format")
    return value

def uid(item):
    return item.split(":")[3]

def set_enabled(value):
    subprocess.run(["gsettings", "set", "org.cinnamon", "enabled-applets", str(value)], check=True)

def create():
    if TARGET.exists() or TARGET.is_symlink():
        raise ValueError("ROS Native Network already installed; will not overwrite it")
    if not SOURCE.is_dir() or not (SOURCE / "applet.js").is_file():
        raise ValueError("System Cinnamon network applet missing")
    for file in ("connected.svg", "disconnected.svg"):
        if not (ICONS / file).is_file():
            raise ValueError("Missing ROS icon " + file)
    version = subprocess.run(["cinnamon", "--version"], capture_output=True, text=True, check=True).stdout
    if "6.6.9" not in version:
        raise ValueError("Only locally tested source layout Cinnamon 6.6.9 is supported: " + version.strip())
    source = (SOURCE / "applet.js").read_text()
    if source.count(PATTERN) != 1 or not re.search(r"_setIcon\s*\(\s*name\s*\)", source):
        raise ValueError("Unexpected native network icon implementation; refusing patch")
    # Keep the original menu/control code intact; replace just the *panel icon*
    # assignment. All native updates continue to pass through _setIcon().
    target_prefix = json.dumps(str(TARGET) + "/")
    change = (
        "const rosDisconnected = /offline|no-route|acquiring|error/.test(name);\n"
        f"            this.set_applet_icon_path({target_prefix} + "
        "(rosDisconnected ? 'disconnected.svg' : 'connected.svg'));"
    )
    patched = source.replace(PATTERN, change, 1)
    metadata = json.loads((SOURCE / "metadata.json").read_text())
    metadata["uuid"] = UUID
    metadata["name"] = "ROS Network Native (Preview)"
    metadata["description"] = "Native Cinnamon networking menu, ROS connected/disconnected root symbols"
    metadata["max-instances"] = 1
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(SOURCE, TARGET, symlinks=False)
    (TARGET / "applet.js").write_text(patched)
    (TARGET / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n")
    for file in ("connected.svg", "disconnected.svg"):
        shutil.copy2(ICONS / file, TARGET / file)
    print("ROS Native Network built from Cinnamon 6.6.9 and installed:", TARGET)
    print("Stock network and ROS Network Status remain unchanged.")
    print("Now activate with --activate")

def activate():
    if not (TARGET / "applet.js").is_file():
        raise ValueError("Run --install first")
    cur = enabled()
    if any(uid(v) == UUID for v in cur):
        raise ValueError("ROS Native Network already activated")
    old = [(i, item) for i, item in enumerate(cur) if uid(item) == NATIVE]
    if len(old) != 1:
        raise ValueError("Exactly one original Cinnamon network applet required")
    idx, item = old[0]
    parts = item.split(":")
    ids = [int(v.split(":")[4]) for v in cur if v.split(":")[4].isdigit()]
    parts[3] = UUID
    parts[4] = str(max(ids, default=0) + 1)
    modified = cur[:idx+1] + [":".join(parts)] + cur[idx+1:]
    BACKUPS.mkdir(parents=True, exist_ok=True)
    backup = BACKUPS / ("ros-network-native-" + datetime.now().strftime("%Y%m%d-%H%M%S-%f"))
    backup.mkdir()
    (backup / "panel.json").write_text(json.dumps({"original": cur, "modified": modified}, indent=2) + "\n")
    set_enabled(modified)
    print("Preview added beside ORIGINAL Cinnamon network control")
    print("Rollback:", "python3 scripts/install-ros-network-native.py --restore", backup)

def restore(path):
    backup = path.expanduser().resolve()
    if not backup.is_relative_to(BACKUPS.resolve()):
        raise ValueError("Unrecognized backup directory")
    data = json.loads((backup / "panel.json").read_text())
    if enabled() != data["modified"]:
        raise ValueError("Panel modified since preview; refusing to overwrite")
    set_enabled(data["original"])
    print("Original panel restored. No system files touched.")

def main():
    if os.geteuid() == 0:
        raise ValueError("Do not use sudo")
    parser = argparse.ArgumentParser(description=__doc__)
    choice = parser.add_mutually_exclusive_group(required=True)
    choice.add_argument("--install", action="store_true")
    choice.add_argument("--activate", action="store_true")
    choice.add_argument("--restore", type=Path)
    args = parser.parse_args()
    if args.install:
        create()
    elif args.activate:
        activate()
    else:
        restore(args.restore)

if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError, SyntaxError, subprocess.CalledProcessError, json.JSONDecodeError) as e:
        print("ERROR:", e, file=sys.stderr)
        sys.exit(1)
