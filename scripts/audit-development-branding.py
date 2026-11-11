#!/usr/bin/env python3
"""Read-only ROS Development desktop comparison (no secrets or file copies).

Run as the normal user in the ROS Development VM. Output is a report to
stdout only; inspect before sharing. Never reads login credentials.
"""
import os
from pathlib import Path
import subprocess

HOME = Path.home()
def cmd(*args):
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=8)
        return p.stdout.strip() if p.returncode == 0 else f"unavailable ({p.returncode})"
    except (OSError, subprocess.TimeoutExpired):
        return "unavailable"

def filenames(path):
    try:
        return sorted(x.name for x in path.iterdir())
    except OSError:
        return ["unavailable"]

def main():
    print("=== ROS DEVELOPMENT DESKTOP AUDIT (READ-ONLY) ===")
    print("Cinnamon:", cmd("cinnamon", "--version"))
    print("Theme:", cmd("gsettings", "get", "org.cinnamon.theme", "name"))
    print("GTK:", cmd("gsettings", "get", "org.cinnamon.desktop.interface", "gtk-theme"))
    print("Icons:", cmd("gsettings", "get", "org.cinnamon.desktop.interface", "icon-theme"))
    print("Wallpaper:", cmd("gsettings", "get", "org.cinnamon.desktop.background", "picture-uri"))
    print("Wallpaper fit:", cmd("gsettings", "get", "org.cinnamon.desktop.background", "picture-options"))
    print("Panel applets:", cmd("gsettings", "get", "org.cinnamon", "enabled-applets"))
    print("Cinnamon menu applet directories:", filenames(HOME / ".local/share/cinnamon/applets"))
    print("User backgrounds:", filenames(HOME / ".local/share/backgrounds/ros"))
    print("User LightDM configuration names:", filenames(HOME / ".config/lightdm"))
    print("System LightDM drop-in names:", filenames(Path("/etc/lightdm/lightdm.conf.d")))
    print("System LightDM root filenames:", [x for x in filenames(Path("/etc/lightdm")) if x.endswith(".conf")])
    print("LightDM greeter theme folders:", filenames(Path("/usr/share/lightdm-webkit/themes")))
    print("LightDM greeter backgrounds:", filenames(Path("/usr/share/backgrounds")))
    print("ROS greeter-like assets in /usr/share (names only):")
    for rel in ("ros", "lightdm", "lightdm-webkit", "slick-greeter"):
        print("  /usr/share/" + rel + ":", filenames(Path("/usr/share") / rel))
    print("End of read-only audit. No passwords, keys or file contents were collected.")

if __name__ == "__main__":
    main()
