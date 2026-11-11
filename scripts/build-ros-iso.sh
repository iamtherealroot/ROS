#!/usr/bin/env bash
# ROS ISO Builder 0.1 — preserves Mint boot catalog with xorriso replay.
# This is a bootable LIVE ISO preview, NOT a completed offline OS installer.
set -Eeuo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
BASE=""
OUT=""
DRY=0
usage() {
  echo "Usage: bash scripts/build-ros-iso.sh --base /path/linuxmint-22.3-cinnamon-64bit.iso --output /path/ROS-0.1-preview.iso [--dry-run]"
}
while (($#)); do
  case "$1" in
    --base) BASE="${2:-}"; shift 2 ;;
    --output) OUT="${2:-}"; shift 2 ;;
    --dry-run) DRY=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) usage >&2; exit 2 ;;
  esac
done
[[ -n "$BASE" && -n "$OUT" ]] || { usage >&2; exit 2; }
for cmd in xorriso git tar sha256sum python3; do
  command -v "$cmd" >/dev/null || { echo "Required command missing: $cmd" >&2; exit 2; }
done
BASE="$(realpath -e -- "$BASE")"
OUT="$(realpath -m -- "$OUT")"
[[ -f "$BASE" ]] || { echo "Input ISO not found" >&2; exit 2; }
[[ "$BASE" != "$OUT" ]] || { echo "Refusing to overwrite source ISO" >&2; exit 2; }
[[ ! -e "$OUT" ]] || { echo "Output exists; choose a new path: $OUT" >&2; exit 2; }
[[ -d "$(dirname -- "$OUT")" ]] || { echo "Output directory does not exist" >&2; exit 2; }
if [[ "$(id -u)" == 0 ]]; then
  echo "Do not build as root. No sudo is needed." >&2
  exit 2
fi
python3 - "$ROOT/iso/profiles.json" <<'PY'
import json, sys
data=json.load(open(sys.argv[1],encoding="utf-8"))
assert [p["id"] for p in data["profiles"]] == ["minimal","it","gaming","complete"]
assert [p["id"] for p in data["install_paths"]] == ["simple","expert"]
assert data["installable_offline"] is False
print("ROS profiles: 4, install paths: 2 (preview only)")
PY

echo "=== ROS ISO Builder 0.1 ==="
echo "Base: $BASE"
echo "Output: $OUT"
echo "ISO content: untouched Mint live environment + /ros/source overlay"
echo "Note: this does NOT install ROS automatically onto a disk."
xorriso -indev "$BASE" -report_el_torito plain 2>&1 | tail -35
echo "Base sha256:"
sha256sum -- "$BASE"
if (( DRY )); then
  echo "Dry run completed; no ISO was written."
  exit 0
fi

STAGING="$(mktemp -d)"
cleanup() { rm -rf -- "$STAGING"; }
trap cleanup EXIT
mkdir -p "$STAGING/ros/source"
# Package only committed source: excludes local passwords, git config, and
# build files from the developer's machine. No GitHub clone is required.
git -C "$ROOT" archive --format=tar HEAD | tar -xf - -C "$STAGING/ros/source"
[[ -s "$STAGING/ros/source/iso/profiles.json" ]] || {
  echo "Missing committed profile manifest. Commit and pull newest develop first." >&2
  exit 2
}
cp "$STAGING/ros/source/iso/profiles.json" "$STAGING/ros/selected-profiles.json"
cat > "$STAGING/ros/README.txt" <<'EOF'
ROS ISO 0.1 — bootable Linux Mint 22.3 Live ISO preview.
Base Mint installer still installs ordinary Linux Mint unless explicitly
configured otherwise. No automatic ROS installation and NO offline
Gaming/IT bundle yet. Do not distribute as finished ROS OS.
Run the ROS profile selection preview inside a live session via:
  python3 /cdrom/ros/source/iso/installer/select-profile.py
That chooser saves a JSON plan only and never partitions a disk.
EOF

# xorriso replay retains the source ISO's BIOS/UEFI boot equipment.
# It is intentionally based on a pristine official Mint ISO and should
# be validated with both UEFI and BIOS boots.
xorriso \
  -indev "$BASE" \
  -outdev "$OUT" \
  -map "$STAGING/ros" /ros \
  -boot_image any replay \
  -commit \
  -end

[[ -s "$OUT" ]] || { echo "ISO build failed" >&2; exit 1; }
sha256sum -- "$OUT" | tee "$OUT.sha256"
echo "Created: $OUT"
echo "Next: test UEFI + BIOS VM boot and profile chooser in LIVE session."
echo "No target disk installation has been performed or validated."
