# ROS first-login 1.2 — test-only prototype

The script `scripts/configure-first-login.py` is a **user-session prototype**, not a system installer, not an ISO autologin implementation and not enabled for automatic startup.

## Scope
- Runs without sudo as the actual desktop user; never hardcodes an account.
- Detects a saved/custom Cinnamon panel and leaves it alone.
- Only when Cinnamon's applet list was not customized, replaces its native power applet with ROS Power Tree.
- Pins Nemo, Firefox, ROS Terminal **only** when the grouped-window-list JSON exists and uses an explicitly recognized baseline.
- Does not invent a Cinnamon JSON layout when its settings file does not exist.
- Saves a backup and marker for applied changes. Repeated execution is a no-op.
- Does not edit LightDM, user passwords, GDM, MintUpdate, network or global system settings.

## Test on a separate disposable VM
1. Create a Hyper-V checkpoint.
2. Create a fresh non-admin test account with an arbitrary name. Sign in graphically to Cinnamon as **that account**. Do not copy the main user's Cinnamon configuration wholesale.
3. Make the ROS Desktop repository available without copying credentials. Ensure prerequisites and ROS Desktop 1.1 were installed for that test account.
4. From its Cinnamon terminal:
   ```bash
   cd ~/ROS-Source
   python3 scripts/configure-first-login.py
   ```
5. Review the dry-run notes, then run `python3 scripts/configure-first-login.py --apply` only if the user is clearly a fresh test account and a Hyper-V checkpoint exists.
6. Log out and back in. Verify each panel applet, Nemo/Firefox/ROS Terminal pins, Power Tree and six theme selection.
7. Run again and confirm idempotence. Repeat with an existing customized account and confirm no changes.

## Known gaps
- On some Cinnamon builds the `pinned-apps` settings file is created only after desktop login. This script intentionally skips it if absent. This needs a more reliable factory-default mechanism.
- Cinnamon 6.6 applet instance format and ordering must be tested in the separate VM.
- This script does not yet provide an automated restore CLI; backups exist under `~/.config/ros/backups/first-login-*` and should be restored through a reviewed procedure.
- Actual autostart at first login is **not enabled** until the test passes.
- Live ISO's passwordless login is a separate, explicitly live-only build concern. Installed systems must never inherit it.
