#!/usr/bin/env python3
"""ROS Desktop Installer 1.3.1 — staged, reversible Cinnamon applet migration.

Default is a non-mutating plan. --stage installs desktop assets using the
existing backed-up v1.2 installer and safely stages ROS Menu / Network Native;
--activate updates only known panel applet UUIDs, backed up atomically;
--restore-panel BACKUP reverses only an unchanged panel transition.

Never run with sudo. LightDM, accounts, personal theme choice, and network
configuration are not modified here. Cinnamon 6.6.9 only.
"""
import argparse
import ast
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
HOME = Path.home()
APPLET_HOME = HOME / ".local/share/cinnamon/applets"
BACKUPS = HOME / ".config/ros/backups"
MENU = "ros-menu@iamtherealroot"
NET = "ros-network-native@iamtherealroot"
POWER = "ros-power-tree@iamtherealroot"
OLD_NET = {"network@cinnamon.org", "ros-network@iamtherealroot"}
STOCK_MENU = "menu@cinnamon.org"

def run(*cmd):
    proc = subprocess.run(cmd, text=True, capture_output=True, timeout=90)
    if proc.returncode:
        raise RuntimeError(f"{' '.join(str(x) for x in cmd)}: {proc.stderr.strip()}")
    return proc.stdout.strip()

def verify():
    if os.geteuid() == 0:
        raise RuntimeError("Never run as root/sudo")
    version = run("cinnamon", "--version")
    if "6.6.9" not in version:
        raise RuntimeError("Only Cinnamon 6.6.9 is supported; found " + version)
    for name in [MENU, POWER]:
        if not (ROOT / "desktop/applets" / name / "applet.js").is_file():
            raise RuntimeError("Missing source applet: " + name)
    if not (ROOT / "scripts/install-desktop.py").is_file():
        raise RuntimeError("Desktop asset installer missing")
    if not (ROOT / "scripts/install-ros-network-native.py").is_file():
        raise RuntimeError("Network native builder missing")

def panel():
    value = ast.literal_eval(run("gsettings", "get", "org.cinnamon", "enabled-applets"))
    if not isinstance(value, list) or not all(isinstance(x, str) and len(x.split(":")) == 5 for x in value):
        raise RuntimeError("Unknown Cinnamon panel format")
    return value

def uuid(item):
    return item.split(":")[3]

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def installed(name):
    directory = APPLET_HOME / name
    if directory.is_symlink():
        raise RuntimeError("Refusing symlink applet directory " + str(directory))
    file = directory / "applet.js"
    if file.is_symlink():
        raise RuntimeError("Refusing symlink applet JS " + str(file))
    return file.is_file()

def menu_current():
    path = APPLET_HOME / MENU / "applet.js"
    source = ROOT / "desktop/applets" / MENU / "applet.js"
    return installed(MENU) and digest(path) == digest(source)

def plan():
    current = panel()
    names = [uuid(x) for x in current]
    print("ROS Desktop Installer 1.3.1 — DRY RUN")
    print("Current account:", HOME.name)
    print("Cinnamon applets:")
    for name in (STOCK_MENU, MENU, "network@cinnamon.org", NET, "power@cinnamon.org", POWER):
        print(f"  {name}: {names.count(name)} active")
    print("ROS Menu code:", "up to date" if menu_current() else
          "installed but differs" if installed(MENU) else "not installed")
    print("ROS Native Network files:", "available" if installed(NET) else "not staged")
    print("ROS Power Tree files:", "available" if installed(POWER) else "not installed")
    print("Plan: --stage backs up and refreshes desktop assets; it never activates panel applets.")
    print("Plan: --activate backs up the complete applet list and changes only approved menu/network/power entries.")
    print("Existing personal theme remains selected; LightDM and accounts are untouched.")
    print("No changes made.")

def stage():
    current = panel()
    names = [uuid(x) for x in current]
    target = APPLET_HOME / MENU
    src = ROOT / "desktop/applets" / MENU
    # Fail before any mutation if the live menu would need a hot code reload.
    if MENU in names and installed(MENU) and not menu_current():
        raise RuntimeError(
            "Active ROS Menu differs from Git. Use scripts/prepare-ros-menu-1.1.py "
            "and a graphical logout/login before staging again."
        )
    if target.is_symlink():
        raise RuntimeError("Refusing symlink at ROS Menu destination")
    if target.exists() and not target.is_dir():
        raise RuntimeError("Invalid ROS Menu destination")
    if target.is_dir() and not installed(MENU):
        raise RuntimeError("Incomplete ROS Menu installation; inspect manually")
    if target.exists() and any(p.is_symlink() for p in target.iterdir()):
        raise RuntimeError("ROS Menu contains symlinks; inspect manually")
    if installed(NET) and (APPLET_HOME / NET / "metadata.json").is_symlink():
        raise RuntimeError("Refusing symlink in installed ROS Network")
    print("Step 1/3: Desktop assets (existing 1.2 installer creates its own full backup)")
    print(run(sys.executable, str(ROOT / "scripts/install-desktop.py"), "--apply"))
    print("Step 2/3: ROS Menu")
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(src, target, symlinks=False)
        print("Installed ROS Menu source:", target)
    elif not menu_current():
        BACKUPS.mkdir(parents=True, exist_ok=True)
        backup = BACKUPS / ("desktop-1.3-menu-" + datetime.now().strftime("%Y%m%d-%H%M%S-%f"))
        shutil.copytree(target, backup, symlinks=False)
        for file in ("applet.js", "metadata.json", "tree.svg"):
            shutil.copy2(src / file, target / file)
        print("Updated inactive ROS Menu. Old files:", backup)
    else:
        print("ROS Menu already current; unchanged")
    print("Step 3/3: ROS Network Native")
    if not installed(NET):
        print(run(sys.executable, str(ROOT / "scripts/install-ros-network-native.py"), "--install"))
    else:
        print("ROS Network Native already present; preserved")
    print("Staging done. Review --plan, then run --activate to adjust panel.")
    print("Log out/in after modifying an existing Cinnamon applet.")

def target_panel(before):
    counts = {name: sum(uuid(x) == name for x in before)
              for name in (MENU, NET, POWER, STOCK_MENU, "network@cinnamon.org", "ros-network@iamtherealroot")}
    if counts[MENU] > 1 or counts[NET] > 1 or counts[STOCK_MENU] > 1:
        raise RuntimeError("Duplicate menu/network applets detected; refusing automatic edit")
    if counts[MENU] and counts[STOCK_MENU]:
        raise RuntimeError("Both ROS and stock menus present; manual inspection required")
    if counts[MENU] == 0 and counts[STOCK_MENU] != 1:
        raise RuntimeError("No unique menu entry to replace")
    if counts[NET] == 0 and sum(counts[x] for x in OLD_NET) != 1:
        raise RuntimeError("Cannot find exactly one original network applet")
    if counts[POWER] > 1:
        raise RuntimeError("Duplicate ROS Power Tree applets detected")
    if counts[POWER] == 0 and sum(uuid(x) == "power@cinnamon.org" for x in before) > 1:
        raise RuntimeError("Duplicate stock power applets detected")
    for name in (MENU, NET, POWER):
        if not installed(name):
            raise RuntimeError(name + " missing; run --stage first")
    if not menu_current():
        raise RuntimeError("ROS Menu source differs from current Git, refusing activation")
    # Remove duplicate old network applets only when ROS native is installed.
    cleaned = []
    positions = []
    for index, item in enumerate(before):
        if uuid(item) in OLD_NET:
            positions.append((index, item))
        else:
            cleaned.append(item)
    if counts[NET] == 0:
        if len(positions) != 1:
            raise RuntimeError("Exactly one original network applet required")
        idx, base = positions[0]
        segments = base.split(":")
        used_ids = [int(x.split(":")[4]) for x in before if x.split(":")[4].isdigit()]
        segments[3] = NET
        segments[4] = str(max(used_ids, default=0) + 1)
        cleaned.insert(idx, ":".join(segments))
    # Keep the location of the original menu, using a new instance id.
    if counts[MENU] == 0:
        used_ids = [int(x.split(":")[4]) for x in before if x.split(":")[4].isdigit()]
        for i, item in enumerate(cleaned):
            if uuid(item) == STOCK_MENU:
                parts = item.split(":")
                parts[3] = MENU
                parts[4] = str(max(used_ids, default=0) + 2)
                cleaned[i] = ":".join(parts)
                break
    # New Mint accounts still have power@cinnamon.org. Convert it to
    # ROS Power Tree; if it is absent, add the ROS indicator after sound.
    # Never alter an already active Power Tree instance.
    if counts[POWER] == 0:
        used_ids = [int(x.split(":")[4]) for x in cleaned if x.split(":")[4].isdigit()]
        next_id = max(used_ids, default=0) + 1
        native = [x for x in cleaned if uuid(x) == "power@cinnamon.org"]
        if len(native) == 1:
            for i, item in enumerate(cleaned):
                if item == native[0]:
                    parts = item.split(":")
                    parts[3], parts[4] = POWER, str(next_id)
                    cleaned[i] = ":".join(parts)
                    break
        else:
            sound = [x for x in cleaned if uuid(x) == "sound@cinnamon.org"]
            if len(sound) != 1:
                raise RuntimeError("No unambiguous stock power or sound applet; panel unchanged")
            index = cleaned.index(sound[0]) + 1
            location = sound[0].split(":")
            location[2], location[3], location[4] = str(int(location[2]) + 1), POWER, str(next_id)
            cleaned.insert(index, ":".join(location))
            # Renumber right-side entries after the insertion to avoid
            # duplicate panel positions; retain every applet instance ID.
            side = location[:2]
            for i in range(index + 1, len(cleaned)):
                segments = cleaned[i].split(":")
                if segments[:2] == side:
                    segments[2] = str(int(segments[2]) + 1)
                    cleaned[i] = ":".join(segments)
    return cleaned

def activate():
    before = panel()
    after = target_panel(before)
    if before == after:
        print("Panel already configured. No changes made.")
        return
    BACKUPS.mkdir(parents=True, exist_ok=True)
    backup = BACKUPS / ("desktop-1.3-panel-" + datetime.now().strftime("%Y%m%d-%H%M%S-%f"))
    backup.mkdir()
    (backup / "panel.json").write_text(json.dumps({
        "home": str(HOME), "before": before, "after": after,
    }, indent=2) + "\n")
    run("gsettings", "set", "org.cinnamon", "enabled-applets", str(after))
    print("ROS menu, native network and Power Tree configured; unrelated applets unchanged.")
    print("Panel backup:", backup)
    print("Rollback: python3 scripts/install-ros-desktop-1.3.py --restore-panel", backup)
    print("Log out/in if icons or cached code look stale.")

def restore_panel(backup):
    backup = backup.expanduser().resolve()
    if not backup.is_relative_to(BACKUPS.resolve()):
        raise RuntimeError("Backup must be below ~/.config/ros/backups")
    record = json.loads((backup / "panel.json").read_text())
    if record["home"] != str(HOME):
        raise RuntimeError("Backup belongs to another user")
    if panel() != record["after"]:
        raise RuntimeError("Panel has changed since activation; refusing to override edits")
    run("gsettings", "set", "org.cinnamon", "enabled-applets", str(record["before"]))
    print("Previous panel restored. Applet files remain staged.")

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--stage", action="store_true", help="backup and install applet/desktop assets")
    mode.add_argument("--activate", action="store_true", help="backup and safely switch menu/network panel IDs")
    mode.add_argument("--restore-panel", type=Path, metavar="BACKUP_DIR")
    args = parser.parse_args()
    verify()
    if args.stage:
        stage()
    elif args.activate:
        activate()
    elif args.restore_panel:
        restore_panel(args.restore_panel)
    else:
        plan()

if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, RuntimeError, ValueError, SyntaxError, TypeError, KeyError,
            json.JSONDecodeError, subprocess.TimeoutExpired) as exc:
        print("ERROR:", exc, file=sys.stderr)
        sys.exit(1)
