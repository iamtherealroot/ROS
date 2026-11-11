# Desktop source import

The development VM has confirmed all six Cinnamon ROS themes, the ROS icon theme and the Power Tree applet. Run locally in the checked-out `develop` branch:

```bash
cd ~/ROS-Source
git pull --ff-only
python3 scripts/import-desktop.py
```

This is a **dry run**. To import the locally installed source into `desktop/`:

```bash
python3 scripts/import-desktop.py --apply
git status --short
git diff --stat
```

The import does **not** commit or upload files. **Review all files**, including possible licensed third-party assets, before pushing to private GitHub or publishing source. The importer uses a strict allowlist and size caps and refuses to overwrite existing files; it is not a full secret scanner. Check particularly `desktop/bin/ros-theme` and desktop entries for hardcoded paths or personal details.

Designs v1.1 executable sources may live elsewhere and are deliberately **not** guessed/imported. Inspect their launcher to identify exact paths before adding them.

Never import `~/.config`, `~/.ssh`, user secrets, VPN profiles, or entire home directories. All changes should remain on `develop` until tested on a clean VM.
