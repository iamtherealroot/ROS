#!/usr/bin/env bash
# ROS desktop inventory. Read-only; prints metadata only, no secrets or file contents.
set -euo pipefail
export LC_ALL=C
printf 'ROS Desktop Audit 1.0\n'
printf '=====================\n'
printf 'User: %s\n' "$(id -un)"
printf 'OS: '
if [[ -r /etc/os-release ]]; then
  . /etc/os-release
  printf '%s\n' "${PRETTY_NAME:-unknown}"
else printf 'unknown\n'; fi
if command -v cinnamon --version >/dev/null 2>&1; then :; fi
if command -v cinnamon >/dev/null 2>&1; then
  cinnamon --version 2>/dev/null || true
fi
printf '\nThemes (read-only check)\n'
for theme in Dark Gaming IT Creator Stealth Nordic; do
  dir="$HOME/.themes/ROS-$theme"
  if [[ -f "$dir/cinnamon/cinnamon.css" ]]; then
    printf 'OK      ROS-%s\n' "$theme"
  else
    printf 'MISSING ROS-%s\n' "$theme"
  fi
done
printf '\nCinnamon settings\n'
for spec in 'org.cinnamon.theme name' 'org.cinnamon.desktop.interface icon-theme'; do
  read -r schema key <<< "$spec"
  if command -v gsettings >/dev/null 2>&1; then
    printf '%s %s: ' "$schema" "$key"
    gsettings get "$schema" "$key" 2>/dev/null || printf 'unavailable\n'
  fi
done
printf '\nComponents\n'
for path in \
  "$HOME/.local/bin/ros-theme" \
  "$HOME/.local/share/cinnamon/applets/ros-power-tree@iamtherealroot/applet.js" \
  "$HOME/.local/share/icons/ROS-Icons/index.theme"; do
  if [[ -f "$path" ]]; then printf 'OK      %s\n' "${path/#$HOME/\~}"
  else printf 'MISSING %s\n' "${path/#$HOME/\~}"; fi
done
printf '\nDesktop entry candidates (names only)\n'
if [[ -d "$HOME/.local/share/applications" ]]; then
  find "$HOME/.local/share/applications" -maxdepth 1 -type f \
    \( -iname '*ros*' -o -iname '*design*' \) -printf '%f\n' | sort
fi
printf '\nIMPORTANT: This audit does not upload or edit any files.\n'
