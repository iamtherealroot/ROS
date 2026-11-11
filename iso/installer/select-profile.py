#!/usr/bin/env python3
"""ROS ISO installer profile chooser (PREVIEW ONLY, never modifies disks).

Launch from a live Cinnamon session with python3-gi and GTK 3 installed.
Records user choices to a JSON plan; no partitioning/install commands yet.
"""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
PROFILE_FILE = ROOT / "iso/profiles.json"

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path.home() / "ros-install-plan.json")
    args = parser.parse_args()
    data = json.loads(PROFILE_FILE.read_text(encoding="utf-8"))
    paths = data["install_paths"]
    profiles = data["profiles"]
    try:
        import gi
        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk
    except (ImportError, ValueError) as e:
        print("GTK 3 / python3-gi unavailable:", e, file=sys.stderr)
        return 2

    dlg = Gtk.Dialog(title="ROS installieren — Vorschau", flags=0)
    dlg.set_default_size(560, 420)
    dlg.add_button("Abbrechen", Gtk.ResponseType.CANCEL)
    dlg.add_button("Auswahl speichern", Gtk.ResponseType.OK)
    panel = dlg.get_content_area()
    panel.set_spacing(15)
    panel.set_margin_top(24)
    panel.set_margin_bottom(24)
    panel.set_margin_start(24)
    panel.set_margin_end(24)
    title = Gtk.Label()
    title.set_markup("<big><b>Root Operating System</b></big>")
    title.set_xalign(0)
    panel.pack_start(title, False, False, 0)
    note = Gtk.Label(label="Vorschau der Installationsauswahl — diese Version verändert KEINE Datenträger.")
    note.set_xalign(0)
    note.set_line_wrap(True)
    panel.pack_start(note, False, False, 0)

    route_label = Gtk.Label(label="Installationsweg")
    route_label.set_xalign(0)
    panel.pack_start(route_label, False, False, 0)
    route = Gtk.ComboBoxText()
    for entry in paths:
        route.append(entry["id"], entry["label"])
    route.set_active_id("simple")
    panel.pack_start(route, False, False, 0)

    profile_label = Gtk.Label(label="Systemprofil")
    profile_label.set_xalign(0)
    panel.pack_start(profile_label, False, False, 0)
    choice = Gtk.ComboBoxText()
    for entry in profiles:
        choice.append(entry["id"], entry["label"])
    choice.set_active_id("minimal")
    panel.pack_start(choice, False, False, 0)

    info = Gtk.Label(label="Installationsdateien und vollständiges Offline-Paketarchiv werden noch entwickelt.")
    info.set_xalign(0)
    info.set_line_wrap(True)
    panel.pack_start(info, False, False, 0)
    dlg.show_all()
    try:
        response = dlg.run()
        if response != Gtk.ResponseType.OK:
            return 0
        result = {
            "schema_version": 1,
            "install_path": route.get_active_id(),
            "profile": choice.get_active_id(),
            "status": "preview-only",
            "disk_changes_allowed": False,
        }
    finally:
        dlg.destroy()
    target = args.output.expanduser()
    if target.is_symlink():
        raise RuntimeError("Refusing to overwrite symlink " + str(target))
    target.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("ROS profile selection saved:", target)
    print("No packages, accounts, partitions or bootloaders installed.")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, RuntimeError, ValueError) as exc:
        print("ERROR:", exc, file=sys.stderr)
        sys.exit(1)
