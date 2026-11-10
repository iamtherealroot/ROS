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
