#!/usr/bin/env python3
"""First Cinnamon session of a *new* ROS user, no privileges required."""
import os
from pathlib import Path
import subprocess
import sys

HOME = Path.home()
MARKER = HOME / ".config/ros/first-login-complete.json"
HELPER = Path("/usr/local/lib/ros/configure-first-login.py")
THEMES = {"ROS-Dark", "ROS-Gaming", "ROS-IT", "ROS-Creator", "ROS-Stealth", "ROS-Nordic"}

def setting(schema, key, value=None):
    cmd = ["gsettings", "get" if value is None else "set", schema, key]
    if value is not None:
        cmd.append(value)
    return subprocess.run(cmd, capture_output=True, text=True)

def main():
    if os.geteuid() == 0 or MARKER.exists():
        return
    # Keep a user-selected ROS theme. For a newly created account, ROS-Dark is default.
    current = setting("org.cinnamon.theme", "name")
    if current.returncode != 0:
        return
    if current.stdout.strip().strip("'\"") not in THEMES:
        if setting("org.cinnamon.theme", "name", "ROS-Dark").returncode:
            return
    setting("org.cinnamon.desktop.interface", "icon-theme", "ROS-Icons")
    # First-session wallpaper; existing accounts with a completion marker are untouched.
    selected = current.stdout.strip().strip("\'\\"")
    if selected not in THEMES:
        selected = "ROS-Dark"
    suffix = selected.removeprefix("ROS-")
    extension = "png" if suffix == "Dark" else "jpg"
    wallpaper = HOME / ".local/share/backgrounds/ros" / f"ROS-{suffix}.{extension}"
    if wallpaper.is_file():
        setting("org.cinnamon.desktop.background", "picture-uri", wallpaper.as_uri())
        setting("org.cinnamon.desktop.background", "picture-options", "zoom")
    theme_cli = HOME / ".local/bin/ros-theme"
    if theme_cli.is_file():
        subprocess.run(["/bin/bash", str(theme_cli), "apply", suffix],
                       check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if HELPER.is_file():
        subprocess.run(["/usr/bin/python3", str(HELPER), "--apply"], check=False)

if __name__ == "__main__":
    main()
