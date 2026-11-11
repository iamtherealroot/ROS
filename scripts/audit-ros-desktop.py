#!/usr/bin/env python3
"""ROS desktop 1.3 read-only readiness audit for Development and Test.

No mutation, no network access, no sudo. All observations concern the
current logged-in user's profile. Emits PASS/WARN and concise next steps.
"""
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

HOME = Path.home()
ROOT = Path(__file__).resolve().parents[1]
APPLET_DIR = HOME / ".local/share/cinnamon/applets"
MENU = "ros-menu@iamtherealroot"
NETWORK = "ros-network-native@iamtherealroot"
POWER = "ros-power-tree@iamtherealroot"
NATIVE_MENU = "menu@cinnamon.org"
NATIVE_NETWORK = "network@cinnamon.org"

def command(*args):
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=8)
        return p.stdout.strip() if p.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        return None

def output(kind, message):
    print(f"{kind:5} {message}")

def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()

def main():
    if os.geteuid() == 0:
        print("Run as the logged-in desktop user, never with sudo.", file=sys.stderr)
        return 2
    print("ROS Desktop 1.3 — read-only preflight")
    print("User:", HOME.name)
    print("Cinnamon:", command("cinnamon", "--version") or "unavailable")
    branch = command("git", "-C", str(ROOT), "branch", "--show-current")
    output("PASS" if branch == "develop" else "WARN", f"Repository branch: {branch or 'not detected'}")
    raw = command("gsettings", "get", "org.cinnamon", "enabled-applets")
    if raw is None:
        output("WARN", "Panel configuration unavailable (run inside Cinnamon session)")
        applets = []
    else:
        try:
            items = ast.literal_eval(raw)
            if not isinstance(items, list) or not all(isinstance(x, str) and len(x.split(":")) == 5 for x in items):
                raise ValueError("unexpected format")
            applets = [x.split(":")[3] for x in items]
        except (ValueError, SyntaxError, TypeError):
            output("WARN", "Could not parse org.cinnamon enabled-applets")
            applets = []
    for uuid, title in [(MENU, "ROS Menu"), (NETWORK, "ROS Network Native"), (POWER, "ROS Power Tree")]:
        count = applets.count(uuid)
        output("PASS" if count == 1 else "WARN", f"{title}: {count} active panel instance(s)")
        installed = APPLET_DIR / uuid / "applet.js"
        if installed.is_file() and not installed.is_symlink():
            output("PASS", f"Applet files installed: {uuid}")
        else:
            output("WARN", f"Applet files missing: {uuid}")
    output("PASS" if NATIVE_MENU not in applets or MENU not in applets else "WARN",
           "No duplicate Cinnamon menu alongside ROS Menu")
    output("PASS" if NATIVE_NETWORK not in applets or NETWORK not in applets else "WARN",
           "No duplicate Cinnamon network icon alongside ROS Network")
    for uuid in (MENU, POWER):
        repository = ROOT / "desktop/applets" / uuid / "applet.js"
        installed = APPLET_DIR / uuid / "applet.js"
        if repository.is_file() and installed.is_file():
            output("PASS" if digest(repository) == digest(installed) else "WARN",
                   f"{uuid}: installed JS matches checked-out Git revision" if digest(repository) == digest(installed)
                   else f"{uuid}: installed JS differs from checked-out Git revision")
    theme = command("gsettings", "get", "org.cinnamon.theme", "name")
    icons = command("gsettings", "get", "org.cinnamon.desktop.interface", "icon-theme")
    output("PASS" if theme and "ROS-" in theme else "WARN", f"Current Cinnamon theme: {theme or 'unknown'}")
    output("PASS" if icons and "ROS-Icons" in icons else "WARN", f"Icon theme: {icons or 'unknown'}")
    lightdm = command("lightdm", "--show-config")
    greeter = bool(lightdm and "greeter-session=lightdm-gtk-greeter" in lightdm)
    output("PASS" if greeter else "WARN", "ROS-compatible GTK LightDM greeter configured"
           if greeter else "Cannot confirm GTK LightDM greeter configuration")
    print()
    print("Read-only audit finished. WARN is a review item, not necessarily a failure.")
    print("Confirm actual menu category clicks and network status visually before deployment.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
