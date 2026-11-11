# ROS Menu 1.0 Preview (Cinnamon 6.6)

Independent Cinnamon applet UUID: `ros-menu@iamtherealroot`.

**Scope:** ROS tree button, app search, category selection, a small favorites
group, and Cinnamon's standard confirmation dialogs for log out, reboot and
power off. This is original menu code; it is **not** a modified Mint menu.
"Recently used" history and a two-column polished layout are **not yet
implemented**. No keyboard Super-key binding is changed in this preview.

## Test on ROS-Test only

Create a Hyper-V checkpoint before panel changes. As `testuser`:

```bash
cd ~/ROS-Source
git pull --ff-only
python3 -m py_compile scripts/install-ros-menu.py
python3 scripts/install-ros-menu.py --install
```

The install step copies files but **does not alter the panel**.

To switch the panel after verifying the files are installed:

```bash
python3 scripts/install-ros-menu.py --activate
```

The script prints a backup path. Save it! If the new menu crashes or fails to
open, restore with:

```bash
python3 scripts/install-ros-menu.py --restore ~/.config/ros/backups/ros-menu-TIMESTAMP
```

If Cinnamon cannot show a panel, use an SSH or TTY session to restore; both
operations only change the logged-in user's `org.cinnamon enabled-applets`.

Do not execute the installer or menu activation with sudo. The preview is
not automatically enabled by Desktop Installer 1.2 or the current ISO overlay.
It must pass graphical testing on a disposable Cinnamon 6.6 machine first.

## Test cases
1. Click tree icon and see the ROS heading and search field.
2. Type part of an application's name; check matching rows.
3. Select categories and launch an application.
4. Check favorites (Nemo, Firefox, ROS Terminal where installed).
5. Confirm logout/shutdown/reboot actions *present* Cinnamon confirmation
   dialogs; do not execute a destructive action to test a menu renderer.
6. Confirm no duplicate Start button and panel layout unchanged.
7. Restore and verify original Cinnamon menu returns.
8. Inspect Cinnamon logs if applet fails to load:
   `journalctl --user -b | grep -i -E 'ros-menu|cinnamon'`.

A failed applet prototype is not a finished feature. Prefer reverting rather
than forcing a Cinnamon restart or deleting system applets.
