#!/usr/bin/env python3
"""ROS Desktop Installer 1.1 (per-user only).

Default mode prints a plan. --apply installs ROS desktop assets with backup.
--restore BACKUP_DIR restores only paths and GSettings values that were managed.
Never edits LightDM/autologin, creates accounts, installs packages or uses sudo.
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
THEMES = ("Dark", "Gaming", "IT", "Creator", "Stealth", "Nordic")
ROUTES = [
    ("desktop/themes/ROS-" + t, ".themes/ROS-" + t) for t in THEMES
] + [
    ("desktop/icons/ROS-Icons", ".local/share/icons/ROS-Icons"),
    ("desktop/applets/ros-power-tree@iamtherealroot", ".local/share/cinnamon/applets/ros-power-tree@iamtherealroot"),
    ("apps/designs/assets", ".local/share/ros/designs/assets"),
    ("apps/designs/designs.py", ".local/share/ros/designs/designs.py"),
    ("apps/designs/launch.sh", ".local/bin/ros-designs"),
    ("apps/designs/designs.desktop", ".local/share/applications/ros-theme-selector.desktop"),
    ("desktop/bin/ros-theme", ".local/bin/ros-theme"),
    ("desktop/applications/ros-terminal.desktop", ".local/share/applications/ros-terminal.desktop"),
    ("desktop/config/theme-palettes.txt", ".config/ros/theme-palettes.txt"),
] + [
    ("desktop/backgrounds/ROS-" + t + (".png" if t == "Dark" else ".jpg"),
     ".local/share/backgrounds/ros/ROS-" + t + (".png" if t == "Dark" else ".jpg"))
    for t in THEMES
]
SETTINGS = [
    ("org.cinnamon.theme", "name"),
    ("org.cinnamon.desktop.interface", "icon-theme"),
    ("org.cinnamon.desktop.interface", "gtk-theme"),
    ("org.cinnamon.desktop.wm.preferences", "theme"),
    ("org.cinnamon.desktop.background", "picture-uri"),
    ("org.cinnamon.desktop.background", "picture-options"),
    ("org.cinnamon.desktop.default-applications.terminal", "exec"),
]

def invoke(*args, check=True):
    return subprocess.run(args, text=True, capture_output=True, check=check)

def asset_path(path):
    p = (ROOT / path).resolve()
    if not p.is_relative_to(ROOT.resolve()):
        raise ValueError("Source escaped repository")
    return p

def dest_path(rel):
    p = HOME / rel
    if p.is_symlink() or any(x.is_symlink() for x in list(p.parents) if x != HOME and HOME in x.parents):
        raise ValueError(f"Refusing symlink destination: {p}")
    if not p.resolve().is_relative_to(HOME.resolve()):
        raise ValueError("Target escaped home")
    return p

def read_settings():
    data = {}
    for schema, key in SETTINGS:
        result = invoke("gsettings", "get", schema, key, check=False)
        if result.returncode == 0:
            data[f"{schema}|{key}"] = result.stdout.strip()
    return data

def save_backup(backup, mapping):
    backup.mkdir(parents=True)
    old = backup / "files"
    old.mkdir()
    saved = []
    for i, (_, dstrel) in enumerate(mapping):
        dest = dest_path(dstrel)
        existed = dest.exists()
        if existed:
            target = old / str(i)
            if dest.is_dir():
                shutil.copytree(dest, target, symlinks=True)
            else:
                shutil.copy2(dest, target)
        saved.append({"path": dstrel, "existed": existed, "slot": str(i)})
    (backup / "manifest.json").write_text(json.dumps({
        "version": 1,
        "home": str(HOME),
        "paths": saved,
        "gsettings": read_settings(),
    }, indent=2) + "\n")
    return saved

def copy_asset(source, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        if dest.is_dir():
            shutil.rmtree(dest)
        else:
            dest.unlink()
    if source.is_dir():
        shutil.copytree(source, dest)
    else:
        shutil.copy2(source, dest)
        if dest.name in ("ros-designs", "ros-theme"):
            dest.chmod(dest.stat().st_mode | 0o111)

def set_setting(schema, key, value):
    result = invoke("gsettings", "set", schema, key, value, check=False)
    if result.returncode:
        print(f"WARN: could not set {schema} {key}: {result.stderr.strip()}")

def apply():
    if os.geteuid() == 0:
        raise ValueError("Do not run as root or with sudo")
    mapping = [(asset_path(src), dst) for src, dst in ROUTES]
    for source, dst in mapping:
        if not source.exists():
            raise FileNotFoundError(f"Missing project asset: {source}")
        dest_path(dst)
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    backup = HOME / ".config/ros/backups" / f"desktop-installer-{stamp}"
    save_backup(backup, mapping)
    print(f"Backup: {backup}")
    try:
        for source, dst in mapping:
            copy_asset(source, dest_path(dst))
            print(f"Installed: {dst}")
    except Exception:
        print(f"Installation interrupted. Restore with: python3 scripts/install-desktop.py --restore '{backup}'", file=sys.stderr)
        raise
    current = invoke("gsettings", "get", "org.cinnamon.theme", "name", check=False)
    name = current.stdout.strip().strip("\"'")
    if name not in [f"ROS-{t}" for t in THEMES]:
        set_setting("org.cinnamon.theme", "name", "ROS-Dark")
    set_setting("org.cinnamon.desktop.interface", "icon-theme", "ROS-Icons")
    if shutil.which("terminator"):
        set_setting("org.cinnamon.desktop.default-applications.terminal", "exec", "terminator")
    else:
        print("WARN: Terminator is not installed; terminal preference preserved.")
    print("\nInstalled per-user ROS themes, icons, Power Tree source and Designs app.")
    print("Existing panel applet layout was deliberately preserved.")
    print("No autologin or user accounts were changed.")
    print("Log out and log back into Cinnamon to refresh the theme.")
    print(f"Restore: python3 scripts/install-desktop.py --restore '{backup}'")

def restore(backup):
    if os.geteuid() == 0:
        raise ValueError("Do not run as root or with sudo")
    base = Path(backup).expanduser().resolve()
    root = (HOME / ".config/ros/backups").resolve()
    if not base.is_relative_to(root):
        raise ValueError("Restore path must be below ~/.config/ros/backups")
    manifest = json.loads((base / "manifest.json").read_text())
    if manifest.get("home") != str(HOME):
        raise ValueError("Backup belongs to a different home directory")
    for item in manifest["paths"]:
        dest = dest_path(item["path"])
        if dest.is_dir():
            shutil.rmtree(dest)
        elif dest.exists():
            dest.unlink()
        if item["existed"]:
            source = base / "files" / item["slot"]
            copy_asset(source, dest)
        print("Restored:", item["path"])
    for compound, value in manifest.get("gsettings", {}).items():
        schema, key = compound.split("|", 1)
        result = invoke("gsettings", "set", schema, key, value, check=False)
        if result.returncode:
            print("WARN: could not restore:", compound)
    print("Restore completed. Log out and back in to refresh Cinnamon.")

def main():
    p = argparse.ArgumentParser(description=__doc__)
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--restore", metavar="BACKUP_DIR")
    args = p.parse_args()
    if args.restore:
        restore(args.restore)
    elif args.apply:
        apply()
    else:
        print("ROS Desktop Installer 1.1 — DRY RUN")
        print("Target account:", os.environ.get("USER", "<current user>"))
        for src, dst in ROUTES:
            source = asset_path(src)
            target = dest_path(dst)
            status = "replace + backup" if target.exists() else "create"
            print(f"{status:17} {dst} {'OK' if source.exists() else 'MISSING SOURCE'}")
        print("No files or settings changed. Use --apply to install.")
        print("Note: panel applets and global Mint settings will not be changed.")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
