# ROS ISO Build — Phase 0.1: filesystem overlay (not yet an ISO)

**Base:** Official Linux Mint 22.3 Zena Cinnamon x86_64 `linuxmint-22.3-cinnamon-64bit.iso`.

## Status
- `iso/stage-rootfs.py` stages the existing ROS desktop into a **disposable extracted rootfs**.
- The overlay places ROS assets into `/etc/skel` for future ordinary users and adds a nonprivileged Cinnamon first-session helper.
- The helper preserves a chosen ROS theme and invokes the existing conservative first-login script for a clean account.
- No password, username, automatic login, sudoers rules, or LightDM configuration is baked in.
- **Not implemented:** authenticating the ISO inside this script, extracting squashfs, updating its manifest, recompressing, rebuilding the original hybrid BIOS/UEFI boot layout, installer provisioning, live-only autologin, or actually boot-testing an ISO.
- **Do not distribute or describe the result as a working ROS ISO yet.**

## Verify upstream before any later image build
Download the ISO, `sha256sum.txt`, and detached `sha256sum.txt.gpg` from the official Mint 22.3 release. Verify the signature using the *independently confirmed* Linux Mint ISO signing key, then run `sha256sum -c --ignore-missing sha256sum.txt` in the same directory. Do not use the overlay tool itself as a substitute for this authenticity check.

## Safe staging example (nonroot test)
```bash
cd ~/ROS-Source
python3 -m py_compile iso/stage-rootfs.py iso/session-init.py
mkdir -p ~/ros-rootfs-staging/{etc,usr}
python3 iso/stage-rootfs.py --rootfs ~/ros-rootfs-staging
```
This is a **structural dry run against an empty example tree**, not a fully functional Mint rootfs.

For an actual overlay stage, use a *copy* of the extracted Mint squashfs with user-owned permissions, with plenty of free disk space. Never target `/`, the running host root, or a production installation. `--apply` refuses overwrites; start with a fresh staging directory each attempt.

## Integration policy
The persistent OS must require a real user password and must never inherit a live account's automatic login. Live login will be configured later as an ephemeral live-only feature after verifying where Mint's installer sources installed user and LightDM settings.

## Next phase
1. Inspect the verified Mint 22.3 ISO layout and boot metadata.
2. Confirm how Mint's installer copies `/etc/skel` and handles autostart, then test the resulting user profile in Hyper-V.
3. Build a hybrid BIOS/UEFI ISO using preserved source boot parameters and verify both modes.
4. Add a CI static validation and a separate VM boot/install test matrix.
