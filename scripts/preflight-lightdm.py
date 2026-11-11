#!/usr/bin/env python3
"""Prepare a safe ROS LightDM greeter deployment without modifying the active login.

Default read-only. --stage writes a NEW standalone deployment directory in
user home with source artwork, a config, and a rollback-oriented manifest.
The actual /etc/lightdm installation is intentionally NOT automatic.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "branding/lightdm"
MAP = {
    "login.png": "/usr/share/backgrounds/ros/login.png",
    "desktop.png": "/usr/share/backgrounds/ros/desktop.png",
    "wallpaper.png": "/usr/share/backgrounds/ros/wallpaper.png",
    "tree.png": "/usr/share/pixmaps/ros/tree.png",
    "tree.svg": "/usr/share/pixmaps/ros/tree.svg",
    "logo.png": "/usr/share/pixmaps/ros/logo.png",
    "lightdm-gtk-greeter.conf": "/etc/lightdm/lightdm-gtk-greeter.conf",
}
def run(*args):
    try:
        r = subprocess.run(args, capture_output=True, text=True, timeout=8)
        return (r.returncode, (r.stdout or r.stderr).strip())
    except (OSError, subprocess.TimeoutExpired):
        return (None, "unavailable")

def audit():
    print("ROS LightDM greeter preflight (READ-ONLY)")
    print("Running uid:", os.geteuid())
    print("LightDM:", run("lightdm", "--version"))
    rc, config = run("lightdm", "--show-config")
    print("Effective LightDM configuration:")
    print(config if rc == 0 else "Unavailable: use sudo lightdm --show-config (redact sensitive values before sharing)")
    for path in ("/etc/lightdm/lightdm-gtk-greeter.conf",
                 "/etc/lightdm/slick-greeter.conf",
                 "/etc/lightdm/lightdm.conf.d/90-ros.conf"):
        p = Path(path)
        print(f"{path}: {'exists' if p.is_file() else 'absent'}")
    for name, path in MAP.items():
        p = SRC / name
        if not p.is_file() or p.is_symlink():
            raise ValueError("Missing or symlinked ROS branding file: " + str(p))
        print("SOURCE", name, p.stat().st_size, "bytes ->", path)
    print("No changes made. Do not restart LightDM during an SSH session.")

def stage(dest):
    dest = dest.expanduser().resolve()
    home = Path.home().resolve()
    if not dest.is_relative_to(home) or dest == home or dest.exists():
        raise ValueError("Choose a NEW directory inside your home")
    audit()
    dest.mkdir(parents=True)
    hashes = {}
    for name, dst in MAP.items():
        source = SRC / name
        target = dest / "payload" / dst.lstrip("/")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        hashes[dst] = hashlib.sha256(target.read_bytes()).hexdigest()
    manifest = {
        "purpose": "ROS Development greeter backup-and-restore pilot",
        "status": "stage only: no active system settings modified",
        "greeter_session_expected": "lightdm-gtk-greeter",
        "changes_applied": False,
        "file_hashes": hashes,
        "next_steps": [
            "Create Hyper-V checkpoint",
            "Confirm lightdm --show-config greeter-session=lightdm-gtk-greeter",
            "Review any existing /etc/lightdm/lightdm-gtk-greeter.conf overrides",
            "Back up all destination files before editing as root",
            "Test login graphically with a recovery console available"
        ],
    }
    (dest / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print("Deployment files staged:", dest)
    print("Active LightDM configuration NOT modified.")

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--stage", type=Path, metavar="NEW_DIR")
    args = p.parse_args()
    if args.stage:
        if os.geteuid() == 0:
            raise ValueError("Do not stage as root")
        stage(args.stage)
    else:
        audit()

if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as e:
        print("ERROR:", e, file=sys.stderr)
        sys.exit(1)
