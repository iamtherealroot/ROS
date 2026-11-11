# ROS panel provisioning (prototype)

- `scripts/configure-panel.py` is **read-only by default**.
- `--apply` changes the applet list only when the user's `/org/cinnamon/enabled-applets` dconf key is unset. Existing custom layouts are never overwritten.
- Only replaces the native power applet with `ros-power-tree@iamtherealroot` in its existing position, retaining networking, audio, system tray and clock.
- No existing pinned-app selection is overwritten. Provisioning Nemo, Firefox and ROS Terminal pins for a fully new Cinnamon profile needs a separately tested first-login mechanism.
- No global LightDM, login, live-session, or user-account settings are modified.
- Verify on a **fresh test user in a disposable VM**, not on the main development account.
- Test Cinnamon behavior on login and confirm unique applet instance IDs.

```bash
cd ~/ROS-Source
git pull --ff-only
python3 -m py_compile scripts/configure-panel.py
python3 scripts/configure-panel.py
```

Note: the tool deliberately does not force panel configuration on an already-configured account.
