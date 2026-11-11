# ROS ISO — Phase 1: Prepare a root filesystem overlay

**Status:** Source code and staging only. This is **NOT** an ISO builder and
does not yet create a bootable image. Use `develop` and a disposable build VM.

## Base image
- Linux Mint **22.3 Zena Cinnamon 64-bit**.
- Download the ISO, `sha256sum.txt`, and `sha256sum.txt.gpg` from official
  Linux Mint mirrors listed at https://linuxmint.com/edition.php?id=326 .
- Verify the fingerprint of the Mint ISO signing key **independently** at
  https://linuxmint.com/verify.php :
  `27DE B156 44C6 B3CF 3BD7 D291 300F 846B A25B AE09`.
- The prepare tool checks both a cryptographically valid manifest signature
  from that exact key and the ISO's SHA256 (it does not download any file).

### Install build prerequisites

```bash
sudo apt update
sudo apt install -y git python3 gnupg xorriso squashfs-tools
gpg --keyserver hkps://keyserver.ubuntu.com --recv-keys 27DEB15644C6B3CF3BD7D291300F846BA25BAE09
gpg --fingerprint 27DEB15644C6B3CF3BD7D291300F846BA25BAE09
```

Importing a key from a keyserver **does not** establish authenticity; check
its fingerprint using the independently consulted official Mint instructions.

### Verify a local ISO

Put the three unmodified files in `~/ISO-Original`, then run:

```bash
cd ~/ROS-Source
python3 scripts/prepare-iso-overlay.py \
  --verify-iso ~/ISO-Original/linuxmint-22.3-cinnamon-64bit.iso \
  --checksums ~/ISO-Original/sha256sum.txt \
  --signature ~/ISO-Original/sha256sum.txt.gpg
```

The verification stops on mismatched signatures and checksums.

### Produce the ROS overlay

```bash
python3 scripts/prepare-iso-overlay.py --output ~/ROS-Build/overlay-v1
find ~/ROS-Build/overlay-v1/rootfs -maxdepth 5 -type f | head -30
cat ~/ROS-Build/overlay-v1/manifest.json
```

**No root access required.** Refuses overwriting an existing output.
The staging directory includes:
- `rootfs/etc/skel/` ROS themes, icons, Power Tree, Designs, backgrounds
  and per-user first-login assets.
- A generic `rootfs/usr/local/bin/ros-first-login` shim resolving `$HOME`
  for an arbitrary future username, rather than embedding `testuser`.
- `rootfs/etc/dconf/db/local.d/00-ros-desktop` proposed default values.

## Not done yet — must be validated before an ISO release

1. Audit a stock Mint 22.3 ISO's `casper` live user, bootloader metadata,
   compression parameters, `filesystem.squashfs`, and Ubiquity installer.
2. Implement reproducible extraction/remastering in a disposable build VM.
   Preserve BIOS+UEFI boot assets, original boot entries, partition structure,
   image checksums, `filesystem.size`, and installer metadata.
3. Ensure `/etc/dconf/profile/user` includes `system-db:local`, compile the
   database **inside the image root** via `dconf update`, and confirm first
   login gets ROS Dark. Do not overwrite an existing non-ROS user theme.
4. Ensure new accounts inherit `/etc/skel` and live user creation does too.
   If Mint's live user is created differently, adapt **live only**.
5. Ensure the stock live session's automatic login works, but that installed
   LightDM requires the user-selected password. Never install a hardcoded live
   password or autologin configuration into the installed OS.
6. Test VM boot on **Hyper-V Generation 2 (UEFI)** and a BIOS-capable VM,
   and test a full installation including reboot and user creation.
7. Add tests for safe restore, installer metadata, theme selector, Cinnamon
   applets, first-login completion, and an upgrade path.

**Important:** The overlay alone does not alter the host or produce an ISO.
Do **not** directly copy the `rootfs` folder into your installed system.
