#!/usr/bin/env python3
"""ROS Desktop 1.1: safe, optional per-user terminal/panel setup.

Default: dry run. --apply: copy ROS Terminal launcher, make Terminator
Cinnamon's default terminal, and replace an existing Terminator pinned app.
Does not change panel applet order or power/network/update components.
"""
import argparse
import datetime
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
HOME = Path.home()
LAUNCHER_SOURCE = ROOT / "desktop/applications/ros-terminal.desktop"
LAUNCHER_TARGET = HOME / ".local/share/applications/ros-terminal.desktop"
PINS = HOME / ".config/cinnamon/spices/grouped-window-list@cinnamon.org/2.json"
BACKUPS = HOME / ".config/ros/backups"
SCHEMA = "org.cinnamon.desktop.default-applications.terminal"

def cmd(*args, check=True):
    return subprocess.run(args, check=check, text=True, capture_output=True)

def inspect():
    if os.geteuid() == 0:
        raise RuntimeError("Run as the desktop user, never with sudo")
    print("ROS Terminal & Panel Configuration")
    print("Terminator:", shutil.which("terminator") or "MISSING")
    print("ROS launcher source:", "OK" if LAUNCHER_SOURCE.is_file() else "MISSING")
    print("Launcher target:", LAUNCHER_TARGET, "(present)" if LAUNCHER_TARGET.exists() else "(missing)")
    p = cmd("gsettings", "get", SCHEMA, "exec", check=False)
    print("Terminal exec:", p.stdout.strip() if p.returncode == 0 else "unavailable")
    if PINS.exists():
        data = json.loads(PINS.read_text())
        print("Existing pins:", data.get("pinned-apps", {}).get("value", "not set"))
    else:
        print("Pinned apps: no Cinnamon grouped-window-list user configuration yet")
        print("The first-login panel-default task remains to be implemented separately.")

def apply():
    inspect()
    if not shutil.which("terminator"):
        raise RuntimeError("Terminator must be installed first; no package changes performed")
    if not LAUNCHER_SOURCE.is_file():
        raise RuntimeError("Missing ROS launcher source")
    for path in (LAUNCHER_TARGET, PINS):
        if path.is_symlink():
            raise RuntimeError(f"Refusing symlink: {path}")
    BACKUPS.mkdir(parents=True, exist_ok=True)
    backup = BACKUPS / ("terminal-" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f"))
    backup.mkdir()
    manifest = {"home": str(HOME), "launcher_existed": LAUNCHER_TARGET.exists(), "pins_existed": PINS.exists()}
    if LAUNCHER_TARGET.exists():
        shutil.copy2(LAUNCHER_TARGET, backup / "ros-terminal.desktop")
    if PINS.exists():
        shutil.copy2(PINS, backup / "2.json")
    old = cmd("gsettings", "get", SCHEMA, "exec", check=False)
    if old.returncode:
        raise RuntimeError("Cinnamon terminal GSettings schema unavailable")
    manifest["old_terminal"] = old.stdout.strip()
    (backup / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    LAUNCHER_TARGET.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(LAUNCHER_SOURCE, LAUNCHER_TARGET)
    cmd("gsettings", "set", SCHEMA, "exec", "terminator")
    if PINS.exists():
        data = json.loads(PINS.read_text())
        pins = data.get("pinned-apps", {}).get("value")
        if isinstance(pins, list):
            # Preserve all unrelated pins and ordering; do not inject a terminal
            # into an existing user-chosen layout if none was pinned.
            update = ["ros-terminal.desktop" if s == "terminator.desktop" else s for s in pins]
            if update != pins:
                data["pinned-apps"]["value"] = list(dict.fromkeys(update))
                PINS.write_text(json.dumps(data, ensure_ascii=False, indent=4) + "\n")
    print("Applied. Backup:", backup)
    print("Existing applet list was not changed. Log out and back into Cinnamon if needed.")

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--apply", action="store_true")
    a = p.parse_args()
    try:
        (apply if a.apply else inspect)()
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as e:
        print("ERROR:", e, file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
