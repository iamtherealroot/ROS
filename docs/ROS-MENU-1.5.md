# ROS Menu 1.5 — Development preview

Patch against ROS Menu 1.4.

- The program list is arranged in two columns with dark green application tiles.
- Each tile displays its application icon and a left-aligned, ellipsized title.
- The four colored system actions share the full 465-pixel menu content width
  via a homogeneous St.BoxLayout and keep their existing Cinnamon
  logout/restart/shutdown confirmation handling.
- Search, category filtering, and favorites remain as before.
- No system files, NetworkManager settings, or ROS Power Tree changes.

## Upgrade (ROS-Development only)

First take a Hyper-V checkpoint. Run as desktop user `ichbinroot`, not sudo:

```bash
cd ~/ROS-Source
git pull --ff-only
python3 scripts/prepare-ros-menu-1.1.py
```

The updater's name is historical: it installs the current checked-out
version (1.5). It copies previous applet files to a backup and enables
the stock Cinnamon menu. Sign out and back in to clear Cinnamon's
JavaScript module cache. Then:

```bash
cd ~/ROS-Source
python3 scripts/install-ros-menu.py --activate
```

Keep the activation backup path to restore via
`python3 scripts/install-ros-menu.py --restore <path>`
if the applet fails. Verify application tiles, text truncation, scroll,
search and category filtering; check the system buttons' color and sizing
without invoking restart or shutdown unnecessarily.

**Status:** Code committed on develop; graphical approval pending.
Do not propagate this preview to ROS-Test or the ISO yet.
