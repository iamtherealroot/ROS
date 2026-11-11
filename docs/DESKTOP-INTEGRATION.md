# ROS Desktop integration inventory

**Status:** ROS Desktop 0.7, 0.8, Status 0.9, Theme Pack 1.0 and Designs 1.1 have been installed and tested manually in the Hyper-V development VM. Their actual source files have **not yet been imported into this Git repository**. Do not treat the prototype ZIP packages as reproducible ROS releases.

## Agreed desktop baseline

- Cinnamon with six selectable themes: `ROS-Dark`, `ROS-Gaming`, `ROS-IT`, `ROS-Creator`, `ROS-Stealth`, `ROS-Nordic`.
- Themes restyle the taskbar, menu and wallpaper; default GTK/Mint themes remain available as fallbacks.
- Visible theme app is named **Designs** (v1.1), not “ROS Designs”.
- Custom Power Tree applet shows real UPower battery percentage, with VM demonstration mode; working prototype on the development VM.
- Network, volume and MintUpdate status icons are themed; MintUpdate functionality remains intact.
- Terminator is shown as **Terminal**.
- The Cinnamon theme picker menu entry is hidden for the development user; underlying Mint themes are not deleted.

## Next steps before versioned distribution

1. Run `bash scripts/audit-desktop.sh` **inside** the VM's local ROS checkout (read-only).
2. Inspect the locally installed source, licenses and icon-theme inheritance.
3. Copy only authored, redistributable ROS code/assets into `desktop/` and `apps/designs/`. Never commit real user home contents wholesale.
4. Add a tested, idempotent installer/uninstaller and a packaging manifest.
5. Verify each theme's Cinnamon menu selectors and application states after restart.
6. Rebuild from a clean Linux Mint VM and verify that the same results are reproducible.
7. Keep `main` untouched until reviewed and tested; integration work belongs on `develop`.

**Privacy:** The audit prints filenames and simple state only. It does not print network configuration, personal account data, credentials or user file contents.
