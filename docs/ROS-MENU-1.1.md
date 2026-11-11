# ROS Menu 1.1 — ROS-Development Preview

Two-column Cinnamon applet: categories on left, scrollable application names
and real installed application icons on right. Keeps program search, favorites
(Nemo/Firefox/ROS Terminal), session controls and the ROS tree button.
Search queries span all categories; selecting a category clears the query.

## Upgrade from functional ROS Menu 1.0 on ROS-Development

Make a Hyper-V checkpoint. Never use sudo for these commands.

```bash
cd ~/ROS-Source
git pull --ff-only
python3 -m py_compile scripts/cleanup-ros-network.py scripts/prepare-ros-menu-1.1.py
python3 scripts/prepare-ros-menu-1.1.py
```

The preparation script archives the installed previous applet and panel config,
temporarily activates the native Cinnamon menu, then copies ROS Menu 1.1 files.
**Sign out and sign back in** before activating 1.1 to avoid Cinnamon GJS
module caching:

```bash
cd ~/ROS-Source
python3 scripts/install-ros-menu.py --activate
```

Save the backup path from activation. Sign out/in again if the old in-memory
code continues running. Check graphical search, category selection, scroll,
app launch, favorites and session submenu. If the ROS icon vanishes, restore
the activation panel backup with
`python3 scripts/install-ros-menu.py --restore <activation-backup-dir>`.
This leaves the known-working Cinnamon menu on the panel.

This is a **source preview**, not a claim of successful Cinnamon 6.6.9
graphical testing. Do not deploy to ROS-Test or bake into an ISO until tested.

## Network panel cleanup (separate, safe)

The complete native network menu with ROS connection roots remains
`ros-network-native@iamtherealroot`. After checkpoint, inspect
`python3 scripts/cleanup-ros-network.py` (dry run) and apply
`python3 scripts/cleanup-ros-network.py --apply` to remove only duplicated
`network@cinnamon.org` and old `ros-network@iamtherealroot`. The
command saves the entire panel state and prints a precise restore command.
