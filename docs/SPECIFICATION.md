# ROS 1.0 – Requirements (planned, not implemented)

## Foundation
- Linux Mint 22.3 Cinnamon x86-64; German default, English selectable.
- Black/mint-green brand, shield with living roots, slogan **Sei wie Root!**, wave wallpaper.
- LightDM split login; branded Plymouth splash and LUKS password display with text fallback.
- Secure Boot, UEFI, encrypted install, recovery and Windows dual-boot require dedicated tests.
- Terminator is the only featured graphical terminal, displayed as **Terminal** with **cmd** as a search keyword; retain emergency TTY.

## Installer
- **Simple** and **Expert** setup flows.
- Profiles: **Minimal**, **IT**, **Gaming**, **Complete**.
- Shared baseline: Cinnamon, Firefox, LibreOffice, Bitwarden, Timeshift, GParted, ROS branding, ROS Welcome and ROS Have-To.
- IT adds QEMU/KVM, libvirt, virt-manager, OVMF, SPICE, graphical WireGuard, SSH client, Wireshark, Git/GitHub CLI.
- Gaming adds Steam, Heroic, GameMode, Vulkan and Ubisoft Connect setup assistant (not bundled native Ubisoft client).
- Complete combines IT and Gaming.
- Drivers/firmware chosen by hardware, not arbitrarily hardcoded.
- Optional multimedia: Spotify desktop client, Deezer and Apple Music web apps.
- Optional gaming broadcasting: OBS, other recording/screen tools, account links for Twitch, YouTube Live, Kick, optional TikTok LIVE and custom RTMP.
- Offline install should not promise online services are immediately usable. Offline repositories/assets need design and testing.
- Sensitive keys/accounts must **never** be baked into the ISO.

## Live ISO and user accounts (required)
- The **live ISO must boot directly into the ROS Cinnamon desktop without a password prompt**; use a dedicated ephemeral live-session user and an explicit LightDM autologin configuration that applies **only** to the live environment.
- The live username is a configurable build-time setting (for example `ros-live`), **not a fixed installed-system user**. The live account must not be migrated into the installed system.
- Do not create a generic shared password for the live user. If the live installer needs privileges, follow the upstream Mint live-session model and limit any passwordless authorization to the live environment.
- **After installation, do not enable autologin by default.** The installed system must use the username chosen in the installer, with a normal password-protected graphical login and separate LUKS unlock if encryption is selected.
- All per-user ROS files must be installed for the **actual target user**, without hardcoding `ichbinroot`, numeric UIDs, home directories or machine-specific paths. Prefer `$HOME`, `getent passwd`, target-user resolution, and installer-provided account metadata as appropriate; never assume the installing live user is the eventual account.
- Boot/installer tests must verify that Live ISO autologin works, installed machines require credentials, no live account or live-only autologin rule remains after install, and two differently named user accounts receive correct ROS settings.
- Do not bake VPN private keys, access tokens, hostnames, passwords or reference-VM identity into the image.

## Core apps
- ROS WireGuard: import, connect, disconnect, view and delete NetworkManager profiles.
- ROS Have-To: optional applications, progress, removal and categorized catalog.
- ROS Welcome: first-boot configuration wizard.
- ROS Update: brand-specific update feed alongside Mint's security infrastructure.

## Release gates
- VM boot and installation tested on Hyper-V UEFI.
- Encrypted and unencrypted installs, text fallback, bootloader and installer verified.
- Every profile installed in a clean VM.
- Package availability and offline installer behavior validated.
- Avoid reusing user-specific IDs, secrets or passwords from the reference VM.
- Distribute only after attribution, licensing, package redistribution and trademark review.
