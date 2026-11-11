#!/usr/bin/env python3
"""ROS Cinnamon panel first-use assistant (preview by default).

Applies ONLY to an uncustomized Cinnamon profile when --apply is explicitly
requested. Does not touch installed applications, passwords or LightDM.
"""
import argparse
import ast
import datetime
import json
import os
from pathlib import Path
import re
import subprocess
import sys

HOME = Path.home()
SCHEMA, KEY = "org.cinnamon", "enabled-applets"
TREE = "ros-power-tree@iamtherealroot"
APPLET = HOME / ".local/share/cinnamon/applets" / TREE / "applet.js"
PINS = HOME / ".config/cinnamon/spices/grouped-window-list@cinnamon.org/2.json"

def call(*cmd, check=True):
    return subprocess.run(cmd, check=check, capture_output=True, text=True)

def existing():
    proc = call("gsettings", "get", SCHEMA, KEY)
    try:
        value = ast.literal_eval(proc.stdout.strip())
    except (ValueError, SyntaxError) as exc:
        raise RuntimeError("Cannot parse Cinnamon applet list") from exc
    if not isinstance(value, list) or not all(isinstance(x, str) for x in value):
        raise RuntimeError("Unexpected Cinnamon applet list")
    return value

def plan(applets):
    if any(TREE in part for part in applets):
        return applets, "Power Tree already present"
    power = next((a for a in applets if "power@cinnamon.org:" in a), None)
    if power is None:
        return applets, "No built-in power applet found; manual review required"
    fields = power.split(":")
    if len(fields) != 5:
        return applets, "Unexpected power applet format; manual review required"
    used = []
    for item in applets:
        try:
            used.append(int(item.rsplit(":", 1)[1]))
        except (ValueError, IndexError):
            pass
    instance = max(used, default=0) + 1
    # Reuse the native power applet's position; keep other applets intact.
    replacement = ":".join(fields[:3] + [TREE, str(instance)])
    result = [replacement if a == power else a for a in applets]
    return result, f"Replace power applet at {fields[0]}:{fields[1]}:{fields[2]} with {TREE}"

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--apply", action="store_true", help="configure only a fresh uncustomized Cinnamon profile")
    args = p.parse_args()
    if os.geteuid() == 0:
        raise RuntimeError("Run as the desktop user without sudo")
    old = existing()
    new, note = plan(old)
    user_customized = call("dconf", "read", "/org/cinnamon/enabled-applets", check=False)
    if user_customized.returncode != 0:
        raise RuntimeError("dconf is unavailable")
    explicit = bool(user_customized.stdout.strip())
    print("ROS panel first-login assistant")
    print("Existing applets:", len(old))
    print("Power Tree source:", "OK" if APPLET.is_file() else "MISSING")
    print("Applet plan:", note)
    print("Explicit user applet config:", "YES — preserve" if explicit else "NO — candidate for first-use")
    if PINS.exists():
        try:
            pins = json.loads(PINS.read_text()).get("pinned-apps", {}).get("value")
            print("Current pinned apps:", pins)
            print("Pinned apps are preserved; default pin provisioning is not yet implemented.")
        except (ValueError, OSError):
            print("Pinned apps could not be read; not modified.")
    else:
        print("Grouped-window-list settings not created yet; preserving Cinnamon defaults.")
    if not args.apply:
        print("DRY RUN: no files or settings modified.")
        return
    if explicit:
        print("Skipped: existing user's panel customization must not be overwritten.")
        return
    if not APPLET.is_file():
        raise RuntimeError("Install the ROS Power Tree before configuring panel")
    if old == new:
        print("Skipped:", note)
        return
    if "manual review required" in note:
        raise RuntimeError(note)
    backup = HOME / ".config/ros/backups" / ("panel-first-use-" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f"))
    backup.mkdir(parents=True, exist_ok=False)
    (backup / "original.json").write_text(json.dumps({"enabled-applets": old, "dconf-raw": user_customized.stdout.strip()}, indent=2) + "\n")
    call("gsettings", "set", SCHEMA, KEY, str(new))
    print("Power Tree substituted for stock power applet; other applets preserved.")
    print("Backup:", backup)
    print("To restore: gsettings reset org.cinnamon enabled-applets")
    print("Only use reset if this was a new profile with no prior custom applet configuration.")

if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
        print("ERROR:", exc, file=sys.stderr)
        sys.exit(1)
