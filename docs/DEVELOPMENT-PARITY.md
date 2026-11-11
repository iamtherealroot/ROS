# ROS development parity — Desktop, Login and Start Menu

This checklist intentionally treats the existing ROS Development VM as the
visual reference, **not** a newly invented login mockup.

## Confirmed from source control
- The six ROS backgrounds, icons, themes, Designs and Power Tree are versioned.
- `scripts/install-desktop.py` installs the ROS Dark wallpaper and GTK theme
  on **first install only**. Existing ROS themes/wallpapers are not overwritten.
- `iso/session-init.py` chooses the wallpaper corresponding to the active
  ROS theme on the first graphical Cinnamon session. Existing completed
  accounts are not modified.
- The ISO is **not bootable yet**. Two preparation approaches currently exist:
  `scripts/prepare-iso-overlay.py` and `iso/stage-rootfs.py`; these must be
  consolidated before a remastering build.
- The custom ROS start menu **does not yet exist as an installed applet** in
  this repository. Do not ship the stock Mint menu claiming it is ROS Menu.

## Gather the missing development references

Run **only on ROS Development**, as its ordinary user:

```bash
cd ~/ROS-Source
git pull --ff-only
python3 scripts/audit-development-branding.py
```

The audit is read-only, prints the wallpaper and relevant names, not
credential-bearing LightDM file contents. Review the output before sharing.
A separate, deliberately reviewed extraction/import of verified LightDM
assets, menu code, and branding graphics is required.

## Acceptance tests
1. New user receives ROS Dark wallpaper, theme and ROS Icons.
2. User switching to Gaming, IT, Creator, Stealth or Nordic also changes the
   background appropriately. Subsequent re-login does not reset the choice.
3. Login greeter matches the audited Development LightDM configuration.
4. The installed greeter always requires the selected user's password;
   only a distinct ephemeral Live ISO session may auto-login.
5. Full ROS Menu is an independent Cinnamon applet with a restore path to
   the stock menu, not a destructive system-menu patch.
6. Boot and login are visually checked on Hyper-V after integrating binaries;
   code compilation alone is insufficient.

## Important
Never copy Development VM /etc/lightdm/ wholesale. It might contain
host-specific usernames, auto-login, session settings, or paths. Import only
explicitly reviewed branding settings and greeter artwork, omitting account,
secret and host-specific fields.
