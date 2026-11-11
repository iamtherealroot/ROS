# ROS Login Installer 1.0 — Linux Mint 22.3 / LightDM GTK

Standalone preparation for ROS Desktop Installer 1.4.
This installs the **same** configuration already used on ROS-Development:
LightDM GTK Greeter, Mint-Y-Dark, Mint-Y-Teal, ROS background, ROS
avatar and clock/system indicators.

**It is separate from the per-user Desktop Installer 1.3.1.**
Installation is deliberately not automatic: a wrong LightDM config can
affect graphical login. Make a Hyper-V checkpoint first.

## 1. Collect the actual ROS graphics on ROS-Development

The files are NOT part of this commit yet. As normal desktop user
`ichbinroot`, within the Git working tree on ROS-Development:

```bash
cd ~/ROS-Source
mkdir -p desktop/login
cp /usr/share/backgrounds/ros/login.png desktop/login/login.png
cp /usr/share/pixmaps/ros/tree.png desktop/login/tree.png
file desktop/login/login.png desktop/login/tree.png
git add desktop/login/login.png desktop/login/tree.png
git commit -m "assets(login): bundle ROS greeter background and tree avatar"
git push origin develop
```

If the avatar file is missing, **do not invent a replacement**. Inspect
the source path and add the real ROS image. Ensure neither PNG includes
private photographs or sensitive data before pushing to a public repo.

## 2. Prepare fresh ROS-Test

```bash
cd ~/ROS-Source
git pull --ff-only
sudo apt install lightdm-gtk-greeter
python3 -m py_compile scripts/install-ros-login.py
python3 scripts/install-ros-login.py
```

The default mode is a **dry run**. It requires both source PNG files and
will fail safely if they are missing. Inspect its planned file changes.

## 3. Backed-up installation

Only on a disposable VM after a Hyper-V checkpoint:

```bash
cd ~/ROS-Source
sudo python3 scripts/install-ros-login.py --apply
```

It saves previous files under `/var/backups/ros-lightdm/login-...`.
It writes these four files, preserving any unrelated LightDM settings:

- `/etc/lightdm/lightdm.conf.d/90-ros.conf`
- `/etc/lightdm/lightdm-gtk-greeter.conf`
- `/usr/share/backgrounds/ros/login.png`
- `/usr/share/pixmaps/ros/tree.png`

It does **not** restart LightDM or automatically sign the user out.
Save all work, then use a normal graphical logout. Verify you can log
back in and the background + tree avatar are correct. Keep a local
TTY/Hyper-V console recovery option.

## 4. Rollback

The apply output prints the exact backup directory, for example:

```bash
sudo python3 scripts/install-ros-login.py --restore /var/backups/ros-lightdm/login-YYYYMMDD-HHMMSS-FFFFFF
```

Rollback only acts when the installed files still have their expected
checksums; it will not silently overwrite changes made since. Existing
files are restored and newly created files are removed.

## 5. Status

The script is committed on `develop`, but requires uploading the
original two images. Do not mark LightDM or the future ISO image as
fully tested until the actual login and rollback have passed.
