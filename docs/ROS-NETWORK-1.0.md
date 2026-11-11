# ROS Network 1.0 Preview — Cinnamon 6.6

Read-only visual network indicator with two distinct ROS root symbols:
- **Connected root** (green, joined branches): NetworkManager reports an active
  network link (`NM.State.CONNECTED_LOCAL` or higher).
- **Disconnected root** (gray, split/red roots): no NetworkManager connection,
  or the status is unavailable.

The indicator does not prove Internet connectivity and **does not modify
network configuration**. Clicking it shows the status and offers a shortcut
to Cinnamon's standard network settings. The native Cinnamon network
applet remains installed and functional during the preview.

## Test on ROS-Test

Take a Hyper-V checkpoint before changing panel applets. As `testuser`
on the graphical Cinnamon session:

```bash
cd ~/ROS-Source
git pull --ff-only
python3 -m py_compile scripts/install-ros-network.py
python3 scripts/install-ros-network.py --install
python3 scripts/install-ros-network.py --activate
```

The command prints a panel snapshot path. Keep it for rollback:

```bash
python3 scripts/install-ros-network.py --restore ~/.config/ros/backups/ros-network-TIMESTAMP
```

Confirm that the native network icon remains in the panel **and** the new
root icon is displayed next to it. Test status changes locally in the Hyper-V
console; disconnecting a network interface remotely can terminate SSH.
If no ROS icon appears, inspect `~/.xsession-errors` for
`ros-network@iamtherealroot`. Do not delete the native applet.

Only after a confirmed successful graphical test should we consider
replacing the original icon or integrating this applet into the ROS Desktop
Installer. The current installer and ISO overlays remain unchanged.
