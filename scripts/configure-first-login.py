#!/usr/bin/env python3
"""ROS first-login setup prototype for *fresh*, interactive Cinnamon accounts.

Dry-run by default. --apply changes only eligible new-profile settings.
Never uses sudo, changes LightDM, creates accounts, or changes a live login.
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
PINS = HOME / ".config/cinnamon/spices/grouped-window-list@cinnamon.org/2.json"
MARKER = HOME / ".config/ros/first-login-complete.json"
BACKUPS = HOME / ".config/ros/backups"
TREE_UUID = "ros-power-tree@iamtherealroot"
TARGET_PINS = ["nemo.desktop", "firefox.desktop", "ros-terminal.desktop"]
DEFAULT_PINS = [
    [],
    ["nemo.desktop", "firefox.desktop", "org.gnome.Terminal.desktop"],
    ["nemo.desktop", "firefox.desktop", "gnome-terminal.desktop"],
    ["nemo.desktop", "firefox.desktop", "terminator.desktop"],
]
THEMES = {"ROS-Dark", "ROS-Gaming", "ROS-IT", "ROS-Creator", "ROS-Stealth", "ROS-Nordic"}

def run(*argv):
    return subprocess.run(argv, text=True, capture_output=True)

def discover():
    if os.geteuid() == 0:
        raise RuntimeError("Run as normal user, never with sudo")
    if not (HOME / ".local/share/cinnamon/applets" / TREE_UUID / "applet.js").is_file():
        raise RuntimeError("ROS Power Tree is not installed")
    if not (HOME / ".local/share/applications/ros-terminal.desktop").is_file():
        raise RuntimeError("ROS Terminal desktop launcher is not installed")
    if not (HOME / ".themes/ROS-Dark/cinnamon/cinnamon.css").is_file():
        raise RuntimeError("ROS desktop assets are not installed")
    res = run("gsettings", "get", "org.cinnamon", "enabled-applets")
    if res.returncode:
        raise RuntimeError("Cinnamon GSettings not available in this session")
    applets = ast.literal_eval(res.stdout.strip())
    if not isinstance(applets, list) or not all(isinstance(x, str) for x in applets):
        raise RuntimeError("Unexpected applet list format")
    raw = run("dconf", "read", "/org/cinnamon/enabled-applets")
    if raw.returncode:
        raise RuntimeError("dconf is not available")
    custom_applets = bool(raw.stdout.strip())
    pin_info = None
    if PINS.is_symlink():
        raise RuntimeError("Refusing symlinked Cinnamon settings")
    if PINS.is_file():
        pin_info = json.loads(PINS.read_text())
    pins = pin_info.get("pinned-apps", {}).get("value") if pin_info else None
    return applets, custom_applets, pin_info, pins

def prepare_panel(applets, custom):
    if custom:
        return None, "Custom panel already saved; preserving it"
    if any(TREE_UUID in x for x in applets):
        return None, "Power Tree already active"
    native = next((x for x in applets if "power@cinnamon.org:" in x), None)
    if native is None:
        return None, "No native power applet; preserving panel"
    parts = native.split(":")
    if len(parts) != 5:
        return None, "Unknown panel format; preserving panel"
    used = []
    for a in applets:
        try:
            used.append(int(a.rsplit(":", 1)[1]))
        except (ValueError, IndexError):
            pass
    replacement = ":".join(parts[:3] + [TREE_UUID, str(max(used, default=0) + 1)])
    return [replacement if item == native else item for item in applets], "Replace stock battery with ROS Power Tree"

def prepare_pins(data, pins):
    if data is None:
        return None, "No Cinnamon grouped-window-list configuration; preserve until created"
    if not isinstance(pins, list):
        return None, "No pinned-apps list; preserve"
    if pins == TARGET_PINS:
        return None, "ROS default pins already applied"
    if pins not in DEFAULT_PINS:
        return None, "Custom pinned apps detected; preserve"
    if not isinstance(data.get("pinned-apps"), dict):
        return None, "Unexpected pinned-apps structure"
    changed = json.loads(json.dumps(data))
    changed["pinned-apps"]["value"] = TARGET_PINS
    return changed, "Set Nemo, Firefox and ROS Terminal on uncustomized panel"

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="apply only if profile has not already been customized")
    args = parser.parse_args()
    applets, custom, data, pins = discover()
    panel, panel_note = prepare_panel(applets, custom)
    pin_data, pin_note = prepare_pins(data, pins)
    theme = run("gsettings", "get", "org.cinnamon.theme", "name")
    name = theme.stdout.strip().strip("\"'") if theme.returncode == 0 else ""
    print("ROS first-login 1.2 —", "APPLY" if args.apply else "DRY RUN")
    print("User:", os.getuid(), HOME)
    print("Cinnamon theme:", name or "unknown")
    print("Panel:", panel_note)
    print("Pins:", pin_note)
    print("Existing marker:", MARKER.exists())
    if not args.apply:
        print("No changes made.")
        return 0
    if MARKER.exists():
        print("Skipped: this account has already run first-login setup.")
        return 0
    if panel is None and pin_data is None:
        print("Skipped: no eligible uncustomized settings.")
        return 0
    if theme.returncode or name not in THEMES:
        print("Skipped: ROS theme not active; install desktop and log into Cinnamon first.")
        return 0
    BACKUPS.mkdir(parents=True, exist_ok=True)
    backup = BACKUPS / ("first-login-" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f"))
    backup.mkdir()
    manifest = {"user_home": str(HOME), "original_panel": applets if panel is not None else None, "pins_existed": bool(data is not None), "changed_panel": False, "changed_pins": False}
    if pin_data is not None:
        shutil.copy2(PINS, backup / "2.json")
    (backup / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    if panel is not None:
        result = run("gsettings", "set", "org.cinnamon", "enabled-applets", str(panel))
        if result.returncode:
            raise RuntimeError("Could not update Cinnamon panel: " + result.stderr)
        manifest["changed_panel"] = True
    if pin_data is not None:
        PINS.write_text(json.dumps(pin_data, indent=2, ensure_ascii=False) + "\n")
        manifest["changed_pins"] = True
    (backup / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    MARKER.parent.mkdir(parents=True, exist_ok=True)
    MARKER.write_text(json.dumps({"version": "1.2", "backup": str(backup)}, indent=2) + "\n")
    print("Applied. Backup:", backup)
    print("Log out and back into Cinnamon to verify the panel.")

if __name__ == "__main__":
    try:
        sys.exit(main())
    except (RuntimeError, OSError, SyntaxError, ValueError, json.JSONDecodeError) as e:
        print("ERROR:", e, file=sys.stderr)
        sys.exit(1)
