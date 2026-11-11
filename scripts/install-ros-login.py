#!/usr/bin/env python3
"""ROS LightDM Login 1.0 — preview, backed-up installation and safe rollback.

Run with sudo ONLY for --apply or --restore. This script never restarts
LightDM or logs the user out. Install image assets in desktop/login/ first.
"""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "desktop/login"
BACKUP_ROOT = Path("/var/backups/ros-lightdm")
SEAT = Path("/etc/lightdm/lightdm.conf.d/90-ros.conf")
GREETER = Path("/etc/lightdm/lightdm-gtk-greeter.conf")
BACKGROUND = Path("/usr/share/backgrounds/ros/login.png")
AVATAR = Path("/usr/share/pixmaps/ros/tree.png")
TARGETS = (SEAT, GREETER, BACKGROUND, AVATAR)
IMAGE_SOURCES = (ASSETS / "login.png", ASSETS / "tree.png")
PNG_SIG = b"\x89PNG\r\n\x1a\n"

SEAT_TEXT = "[Seat:*]\ngreeter-session=lightdm-gtk-greeter\n"
GREETER_TEXT = """[greeter]
background = /usr/share/backgrounds/ros/login.png
user-background = false
theme-name = Mint-Y-Dark
icon-theme-name = Mint-Y-Teal
font-name = Sans 11
position = 75%,center 50%,center
panel-position = bottom
clock-format = %H:%M
indicators = ~host;~spacer;~clock;~layout;~power
default-user-image = /usr/share/pixmaps/ros/tree.png
round-user-image = false
screensaver-timeout = 0
"""

def require_regular(path):
    if path.is_symlink() or (path.exists() and not path.is_file()):
        raise RuntimeError("Refusing non-regular or symlinked file: " + str(path))
    for parent in path.parents:
        if parent == Path("/"):
            break
        if parent.is_symlink():
            raise RuntimeError("Refusing symlink parent: " + str(parent))

def checksum(data):
    return hashlib.sha256(data).hexdigest()

def desired():
    for path in IMAGE_SOURCES:
        require_regular(path)
        if not path.is_file():
            raise RuntimeError("Missing ROS image: " + str(path) +
                               " (copy originals from ROS-Development into desktop/login/)")
        if not path.read_bytes().startswith(PNG_SIG):
            raise RuntimeError("Not a PNG file: " + str(path))
    return (SEAT_TEXT.encode(), GREETER_TEXT.encode(),
            IMAGE_SOURCES[0].read_bytes(), IMAGE_SOURCES[1].read_bytes())

def check_greeter():
    check = subprocess.run(["dpkg-query", "-W", "-f=${Status}",
                            "lightdm-gtk-greeter"], capture_output=True, text=True)
    if check.returncode or "install ok installed" not in check.stdout:
        raise RuntimeError("lightdm-gtk-greeter is not installed. Install it before applying.")

def write_atomic(path, data):
    require_regular(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".ros-", delete=False) as f:
            temp = Path(f.name)
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.chmod(temp, 0o644)
        os.replace(temp, path)
    finally:
        if temp is not None and temp.exists():
            temp.unlink()

def preview():
    print("ROS LightDM Login 1.0 — DRY RUN (no changes)")
    check_greeter()
    payloads = desired()
    for dst, data in zip(TARGETS, payloads):
        require_regular(dst)
        if not dst.exists():
            status = "create"
        elif dst.read_bytes() == data:
            status = "already identical"
        else:
            status = "backup + replace"
        print(f"  {status:18} {dst}")
    print("No LightDM restart; next graphical login will use these settings.")

def apply():
    if os.geteuid() != 0:
        raise RuntimeError("Use sudo for --apply")
    check_greeter()
    payloads = desired()
    for dst in TARGETS:
        require_regular(dst)
    changes = [(dst, data) for dst, data in zip(TARGETS, payloads)
               if not dst.exists() or dst.read_bytes() != data]
    if not changes:
        print("ROS Login already matches requested configuration. No changes.")
        return
    BACKUP_ROOT.mkdir(parents=True, exist_ok=True)
    os.chmod(BACKUP_ROOT, 0o700)
    backup = BACKUP_ROOT / ("login-" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f"))
    backup.mkdir(mode=0o700)
    record = {"version": 1, "changes": []}
    for i, (dst, data) in enumerate(changes):
        existed = dst.exists()
        if existed:
            shutil.copy2(dst, backup / ("before-" + str(i)))
        record["changes"].append({
            "destination": str(dst), "existed": existed, "slot": i,
            "after_sha256": checksum(data)
        })
    (backup / "manifest.json").write_text(json.dumps(record, indent=2) + "\n")
    for dst, data in changes:
        write_atomic(dst, data)
        print("Installed:", dst)
    print("Backup:", backup)
    print("Rollback: sudo python3 scripts/install-ros-login.py --restore", backup)
    print("Do NOT restart LightDM from a live session. Test on next normal logout/login.")

def restore(backup):
    if os.geteuid() != 0:
        raise RuntimeError("Use sudo for --restore")
    backup = backup.resolve(strict=True)
    if not backup.is_relative_to(BACKUP_ROOT.resolve()):
        raise RuntimeError("Backup is outside " + str(BACKUP_ROOT))
    if backup.is_symlink() or not backup.is_dir():
        raise RuntimeError("Invalid backup")
    record = json.loads((backup / "manifest.json").read_text())
    allowed = {str(path) for path in TARGETS}
    for item in record["changes"]:
        dst = Path(item["destination"])
        if str(dst) not in allowed:
            raise RuntimeError("Unexpected backup destination: " + str(dst))
        require_regular(dst)
        if not dst.is_file() or checksum(dst.read_bytes()) != item["after_sha256"]:
            raise RuntimeError("File changed after install, refusing rollback: " + str(dst))
        if item["existed"] and not (backup / ("before-" + str(item["slot"]))).is_file():
            raise RuntimeError("Missing backup data for " + str(dst))
    for item in reversed(record["changes"]):
        dst = Path(item["destination"])
        if item["existed"]:
            write_atomic(dst, (backup / ("before-" + str(item["slot"]))).read_bytes())
            print("Restored:", dst)
        else:
            dst.unlink()
            print("Removed:", dst)
    print("ROS LightDM rollback finished. Changes take effect at the next login.")

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument("--apply", action="store_true")
    actions.add_argument("--restore", type=Path, metavar="BACKUP_DIRECTORY")
    args = parser.parse_args()
    if args.restore:
        restore(args.restore)
    elif args.apply:
        apply()
    else:
        preview()

if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, ValueError, subprocess.SubprocessError,
            json.JSONDecodeError) as err:
        print("ERROR:", err, file=sys.stderr)
        sys.exit(1)
