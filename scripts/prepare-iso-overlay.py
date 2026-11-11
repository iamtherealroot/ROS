#!/usr/bin/env python3
"""Prepare ROS files for an eventual Linux Mint 22.3 Cinnamon ISO.

No ISO is built by this command. Writes only below --output, never needs sudo.
Source files are taken from the reviewed Desktop Installer ROUTES.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
INSTALLER_PATH = ROOT / "scripts/install-desktop.py"
MINT_ISO = "linuxmint-22.3-cinnamon-64bit.iso"
SIGNER_FINGERPRINT = "27DEB15644C6B3CF3BD7D291300F846BA25BAE09"

def load_routes():
    spec = importlib.util.spec_from_file_location("ros_desktop_installer", INSTALLER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.ROUTES

def verify_mint_image(iso, checksums, signature):
    if iso.name != MINT_ISO:
        raise ValueError(f"Expected the official Mint 22.3 Cinnamon ISO name: {MINT_ISO}")
    if not iso.is_file() or not checksums.is_file() or not signature.is_file():
        raise FileNotFoundError("ISO, sha256sum.txt and sha256sum.txt.gpg are required")
    result = subprocess.run(
        ["gpg", "--status-fd", "1", "--verify", str(signature), str(checksums)],
        capture_output=True, text=True,
    )
    if result.returncode:
        raise ValueError("Linux Mint SHA256 manifest has an INVALID signature: " + result.stderr)
    valid_signers = [
        line for line in result.stdout.splitlines()
        if line.startswith("[GNUPG:] VALIDSIG ")
    ]
    if not any(line.split()[2].upper() == SIGNER_FINGERPRINT for line in valid_signers):
        raise ValueError("Checksum signature not made by the expected official Linux Mint key")
    expected = None
    for line in checksums.read_text().splitlines():
        fields = line.strip().split(maxsplit=1)
        if len(fields) == 2 and fields[1].lstrip("*") == MINT_ISO:
            expected = fields[0].lower()
            break
    if expected is None or len(expected) != 64:
        raise ValueError("Official checksum for Cinnamon 22.3 not found")
    digest = hashlib.sha256()
    with iso.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    if digest.hexdigest() != expected:
        raise ValueError("ISO SHA256 differs from the signed Linux Mint manifest")
    return expected

def create_overlay(output):
    output = output.expanduser().resolve()
    if output == ROOT.resolve() or output == Path.home().resolve() or output == Path("/"):
        raise ValueError("Refusing to use a repository, home or root directory as output")
    if output.exists():
        raise FileExistsError(f"Output already exists: {output}")
    routes = load_routes()
    for source, rel in routes:
        src = ROOT / source
        if not src.exists() or src.is_symlink():
            raise ValueError(f"Missing or unsupported source: {src}")
        if not rel.startswith(".") or ".." in Path(rel).parts:
            raise ValueError(f"Unsafe target route: {rel}")
    output.mkdir(parents=True)
    skel = output / "rootfs/etc/skel"
    count = 0
    for source, rel in routes:
        src = ROOT / source
        dest = skel / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            shutil.copytree(src, dest, symlinks=False)
        else:
            shutil.copy2(src, dest)
        count += 1
    # The desktop installer uses a per-user absolute Exec path; /etc/skel does
    # not know a future username. The ISO instead calls a fixed system wrapper
    # that resolves HOME at user login time.
    autostart = skel / ".config/autostart/ros-first-login.desktop"
    content = autostart.read_text()
    token = "@ROS_FIRST_LOGIN_EXEC@"
    if token not in content:
        raise ValueError("First-login desktop template changed unexpectedly")
    autostart.write_text(content.replace(token, "/usr/local/bin/ros-first-login"))
    wrapper = output / "rootfs/usr/local/bin/ros-first-login"
    wrapper.parent.mkdir(parents=True, exist_ok=True)
    wrapper.write_text(
        "#!/bin/sh\n"
        "# Per-user session helper; never run as root.\n"
        'test "$(id -u)" -ne 0 || exit 1\n'
        'exec /usr/bin/python3 "$HOME/.local/share/ros/first-login/configure-first-login.py" --apply\n'
    )
    wrapper.chmod(0o755)
    # Dconf system defaults apply only to accounts that have not selected
    # their own themes. The dconf database MUST be compiled with dconf update
    # inside the future ISO rootfs build, not on the build host.
    defaults = output / "rootfs/etc/dconf/db/local.d/00-ros-desktop"
    defaults.parent.mkdir(parents=True, exist_ok=True)
    defaults.write_text(
        "[org/cinnamon/theme]\nname='ROS-Dark'\n"
        "[org/cinnamon/desktop/interface]\nicon-theme='ROS-Icons'\n"
    )
    manifest = {
        "phase": "staging-only; NOT a bootable ISO",
        "base": "Linux Mint 22.3 Zena Cinnamon amd64",
        "user_independent": True,
        "live_autologin_configured": False,
        "installed_autologin_configured": False,
        "dconf_update_required_inside_rootfs": True,
        "source_routes": count,
        "run_first_login_during_session": True,
        "validation_required": ["Mint ISO signed checksums", "UEFI and BIOS boot", "Live session", "installed username/password", "skel propagation", "first login applet"],
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="New folder to populate with ROS rootfs overlay")
    parser.add_argument("--verify-iso", type=Path, help="Original Mint 22.3 Cinnamon ISO")
    parser.add_argument("--checksums", type=Path, help="Official sha256sum.txt")
    parser.add_argument("--signature", type=Path, help="Official sha256sum.txt.gpg")
    args = parser.parse_args()
    if args.verify_iso or args.checksums or args.signature:
        if not (args.verify_iso and args.checksums and args.signature):
            parser.error("Use --verify-iso, --checksums and --signature together")
        digest = verify_mint_image(args.verify_iso, args.checksums, args.signature)
        print("Verified official Linux Mint 22.3 Cinnamon ISO:", digest)
    if args.output:
        manifest = create_overlay(args.output)
        print("ROS ISO overlay staged:", args.output)
        print("Copied routes:", manifest["source_routes"])
        print("NOT a bootable ISO. No live-autologin or remastering has been performed.")
    if not args.output and not args.verify_iso:
        parser.print_help()

if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError) as exc:
        print("ERROR:", exc, file=sys.stderr)
        sys.exit(1)
