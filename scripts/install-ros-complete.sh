#!/usr/bin/env bash
# ROS Complete Setup 1.4 preview — on Linux Mint 22.3 Cinnamon 6.6.9.
# Run as the logged-in desktop user, not with sudo.
# --reboot: reboot only after all installation/verification commands succeed.
set -Eeuo pipefail

HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd -- "$HERE/.." && pwd)"
REBOOT=0
case "${1:-}" in
  "") ;;
  --reboot) REBOOT=1 ;;
  *) echo "Usage: bash scripts/install-ros-complete.sh [--reboot]" >&2; exit 2 ;;
esac

if (( EUID == 0 )); then
  echo "Run without sudo; the installer requests sudo only for system packages and LightDM." >&2
  exit 2
fi
if [[ "${XDG_CURRENT_DESKTOP:-}" != *Cinnamon* ]] && [[ "${DESKTOP_SESSION:-}" != *cinnamon* ]]; then
  echo "Please run inside a Cinnamon desktop session (no headless SSH)." >&2
  exit 2
fi
if ! cinnamon --version | grep -q '6.6.9'; then
  echo "ROS currently supports Cinnamon 6.6.9 only." >&2
  exit 2
fi
for p in "$REPO/scripts/install-ros-desktop-1.3.py" "$REPO/scripts/install-ros-login.py" "$REPO/scripts/audit-ros-desktop.py"; do
  [[ -f "$p" ]] || { echo "Missing installer component: $p" >&2; exit 2; }
done
for p in "$REPO/desktop/login/login.png" "$REPO/desktop/login/tree.png"; do
  [[ -s "$p" ]] || { echo "Missing ROS login artwork: $p" >&2; exit 2; }
done

echo "=== ROS Complete Setup 1.4 preview ==="
echo "Account: $(id -un)"
echo "Repository: $REPO"
echo "Will install Terminator and the GTK LightDM greeter if needed."
echo "Existing ROS themes, account credentials and network configuration are preserved."
if (( REBOOT )); then
  echo "After success, the computer WILL reboot without asking again."
fi
echo
echo "=== Packages ==="
sudo -v
sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y terminator lightdm-gtk-greeter
command -v terminator >/dev/null || { echo "Terminator installation failed" >&2; exit 1; }

cd "$REPO"
echo
echo "=== Desktop files ==="
# Avoid hot-swapping a live menu. On a fresh Mint install both applets
# are absent and stage is safe; on an existing ROS install skip staging.
if [[ ! -f "$HOME/.local/share/cinnamon/applets/ros-menu@iamtherealroot/applet.js" ]] ||
   [[ ! -f "$HOME/.local/share/cinnamon/applets/ros-network-native@iamtherealroot/applet.js" ]] ||
   [[ ! -f "$HOME/.local/share/cinnamon/applets/ros-power-tree@iamtherealroot/applet.js" ]]; then
  python3 scripts/install-ros-desktop-1.3.py --stage
else
  echo "ROS desktop applet files already installed; preserving live files."
fi
echo
echo "=== Panel ==="
python3 scripts/install-ros-desktop-1.3.py --activate
echo
echo "=== LightDM login (system-wide, backed up) ==="
sudo python3 scripts/install-ros-login.py --apply
echo
echo "=== Validation ==="
python3 scripts/audit-ros-desktop.py
# Audit warnings are informational. Fail the installation on actual
# mandatory command failures, but make missing checks visible to user.
echo
echo "Setup commands finished. Check the audit and ROS login after reboot."
echo "Original LightDM and panel backups are preserved in their respective paths."
if (( REBOOT )); then
  echo "Rebooting now..."
  sudo systemctl reboot
else
  echo "Reboot recommended to reload the GTK LightDM greeter."
  echo "After saving your work: sudo systemctl reboot"
fi
