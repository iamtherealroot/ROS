# ROS Menu 1.4 Preview — Development

ROS Menu 1.4 updates the already working ROS Menu 1.3:

- Force left alignment in the scrollable application container, program
  row, and program button (Clutter.ActorAlign.START).
- Give session actions distinct accessible labels and colors:
  Sperren blue-gray (#304957), Abmelden amber (#645320),
  Neustart orange (#78441e), Ausschalten red (#773034).
- Preserve Cinnamon's existing confirmation-enabled
  `cinnamon-session-quit` commands.

The color change is implemented as **inline St.Button styling** rather
than depending on an external stylesheet loader.

## Development upgrade

Create a Hyper-V checkpoint. Then as `ichbinroot` without sudo:

```bash
cd ~/ROS-Source
git pull --ff-only
python3 scripts/prepare-ros-menu-1.1.py
```

The helper's filename is historical; it installs the latest checked-out
ROS Menu source. It backs up the current installation and switches
temporarily to the Cinnamon menu. Fully sign out and back in, then:

```bash
cd ~/ROS-Source
python3 scripts/install-ros-menu.py --activate
```

Verify visually that the application list is left aligned and all four
actions are correctly colored. Keep the activation backup path; if the
applet fails, restore it using `install-ros-menu.py --restore <backup>`.

ROS-Test and the ISO should only receive this version after a successful
Development VM graphical test.
