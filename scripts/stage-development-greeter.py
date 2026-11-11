#!/usr/bin/env python3
"""Stage the exact reviewed ROS Development LightDM greeter files.

No sudo, LightDM edits, restarts or account changes. Output is a new,
disposable directory containing paths relative to a future ISO rootfs.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
ARTWORK = {
    "login.png": "usr/share/backgrounds/ros/login.png",
    "desktop.png": "usr/share/backgrounds/ros/desktop.png",
    "wallpaper.png": "usr/share/backgrounds/ros/wallpaper.png",
    "logo.png": "usr/share/pixmaps/ros/logo.png",
    "tree.png": "usr/share/pixmaps/ros/tree.png",
    "tree.svg": "usr/share/pixmaps/ros/tree.svg",
}
GREETER = "etc/lightdm/lightdm-gtk-greeter.conf"
# The entry is greeter-only: no account, session, password or autologin keys.
FORBIDDEN = ("autologin-user", "autologin-user-timeout", "greeter-hide-users",
             "allow-guest", "pam-", "password", "user-session", "session-wrapper")

def stage(output):
    output = output.expanduser().resolve()
    if output.exists() or output == Path("/") or output == Path.home().resolve():
        raise ValueError("Use a NEW output directory, never a live system folder")
    config = ROOT / "branding/lightdm/lightdm-gtk-greeter.conf"
    data = config.read_text()
    for line in data.splitlines():
        stripped = line.strip().lower()
        if stripped.startswith(("#", ";", "[")) or not stripped:
            continue
        key = stripped.split("=", 1)[0].strip()
        if any(word in key for word in FORBIDDEN):
            raise ValueError("Refusing account or authentication settings in greeter config")
    if "[greeter]" not in data or "background = /usr/share/backgrounds/ros/login.png" not in data:
        raise ValueError("Missing reviewed greeter section or artwork reference")
    sources = [(config, GREETER)]
    for name, rel in ARTWORK.items():
        p = ROOT / "branding/lightdm" / name
        if not p.is_file() or p.is_symlink():
            raise ValueError("Missing or symlinked artwork: " + str(p))
        sources.append((p, rel))
    output.mkdir(parents=True)
    hashes = {}
    for src, rel in sources:
        dest = output / "rootfs" / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        hashes[rel] = hashlib.sha256(dest.read_bytes()).hexdigest()
    manifest = {
        "artifact": "ROS Development LightDM GTK greeter branding",
        "status": "staged only; no live LightDM configuration changed",
        "login_autostart": False,
        "files": hashes,
        "pending": ["Inspect existing Mint greeter files for conflicts",
                    "Integrate into verified ISO rootfs",
                    "Test installed password login on disposable Hyper-V VM"],
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = stage(args.output)
    print("ROS greeter payload staged:", args.output)
    print("Files:", len(result["files"]))
    print("LightDM untouched. No bootable ISO created.")

if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as exc:
        print("ERROR:", exc, file=sys.stderr)
        sys.exit(1)
