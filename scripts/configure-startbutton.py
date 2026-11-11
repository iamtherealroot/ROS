#!/usr/bin/env python3
"""ROS Start button branding for Cinnamon 6.6 (safe interim until ROS Menu exists).

Dry run by default. Only edits stock menu applet's icon settings and stores
a backup. Does NOT replace the stock menu with a custom menu implementation.
"""
import argparse
import datetime
import json
import os
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
HOME = Path.home()
ICON_SOURCE = ROOT / "branding/lightdm/tree.svg"
ICON_TARGET = HOME / ".local/share/ros/menu/tree.svg"
CONF_DIR = HOME / ".config/cinnamon/spices/menu@cinnamon.org"
BACKUP_ROOT = HOME / ".config/ros/backups"

def resolve_config():
    if not CONF_DIR.is_dir():
        raise ValueError("Cinnamon menu configuration not found: " + str(CONF_DIR))
    files = sorted(CONF_DIR.glob("*.json"))
    if len(files) != 1 or files[0].is_symlink():
        raise ValueError("Expected exactly one non-symlinked Cinnamon menu config; found " + str(len(files)))
    return files[0]

def ensure_safe(path):
    if path.is_symlink():
        raise ValueError("Refusing symlink: " + str(path))
    for parent in path.parents:
        if parent == HOME:
            break
        if parent.is_symlink():
            raise ValueError("Refusing symlink parent: " + str(parent))

def prepare(data):
    for key in ("menu-custom", "menu-icon", "menu-label"):
        if not isinstance(data.get(key), dict) or "value" not in data[key]:
            raise ValueError(f"Unexpected Cinnamon menu schema; missing {key}.value")
    result = json.loads(json.dumps(data))
    result["menu-custom"]["value"] = True
    result["menu-icon"]["value"] = str(ICON_TARGET)
    result["menu-label"]["value"] = ""
    if "menu-icon-size" in result:
        result["menu-icon-size"]["value"] = 28
    return result

def apply():
    if os.geteuid() == 0:
        raise ValueError("Do not run with sudo")
    config = resolve_config()
    for path in (config, ICON_TARGET, ICON_SOURCE, BACKUP_ROOT):
        ensure_safe(path)
    if not ICON_SOURCE.is_file():
        raise ValueError("ROS Development tree.svg is missing")
    data = json.loads(config.read_text())
    target = prepare(data)
    print("ROS Start Button 1.3 — DRY RUN")
    print("Cinnamon menu file:", config)
    print("Icon source:", ICON_SOURCE)
    print("Icon destination:", ICON_TARGET)
    print("Will keep menu@cinnamon.org and all its current functionality")
    if not args.apply:
        print("No changes made. Use --apply to change the icon.")
        return
    backup = BACKUP_ROOT / ("startbutton-" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f"))
    backup.mkdir(parents=True)
    shutil.copy2(config, backup / "menu.json")
    old_icon = ICON_TARGET.is_file()
    if old_icon:
        shutil.copy2(ICON_TARGET, backup / "tree.svg")
    (backup / "manifest.json").write_text(json.dumps({
        "config": str(config),
        "icon": str(ICON_TARGET),
        "had_icon": old_icon,
    }, indent=2) + "\n")
    ICON_TARGET.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ICON_SOURCE, ICON_TARGET)
    tmp = config.with_name(config.name + ".ros-new")
    try:
        tmp.write_text(json.dumps(target, indent=2, ensure_ascii=False) + "\n")
        tmp.replace(config)
    finally:
        tmp.unlink(missing_ok=True)
    print("Applied. Backup:", backup)
    print("Graphically log out and back in if Cinnamon does not refresh the icon immediately.")

def restore(path):
    backup = path.expanduser().resolve()
    if not backup.is_relative_to(BACKUP_ROOT.resolve()):
        raise ValueError("Backup must be inside ~/.config/ros/backups")
    manifest = json.loads((backup / "manifest.json").read_text())
    config, icon = Path(manifest["config"]), Path(manifest["icon"])
    if config.parent != CONF_DIR or icon != ICON_TARGET:
        raise ValueError("Backup belongs to a different Cinnamon profile")
    ensure_safe(config)
    ensure_safe(icon)
    shutil.copy2(backup / "menu.json", config)
    if manifest["had_icon"]:
        shutil.copy2(backup / "tree.svg", icon)
    else:
        icon.unlink(missing_ok=True)
    print("Restored original Cinnamon button. Log out and in if needed.")

if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--restore", type=Path)
    args = p.parse_args()
    try:
        if args.restore:
            restore(args.restore)
        else:
            apply()
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print("ERROR:", exc, file=sys.stderr)
        sys.exit(1)
