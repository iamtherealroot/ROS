#!/usr/bin/env python3
"""Unit tests for staging the ROS ISO overlay without a Mint ISO."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/prepare-iso-overlay.py"
spec = importlib.util.spec_from_file_location("ros_iso_staging", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class ISOOverlayTests(unittest.TestCase):
    def test_overlay_can_be_staged_without_root(self):
        with tempfile.TemporaryDirectory(prefix="ros-iso-test-") as temp:
            target = Path(temp) / "new-overlay"
            manifest = mod.create_overlay(target)
            skel = target / "rootfs/etc/skel"
            self.assertGreaterEqual(manifest["source_routes"], 20)
            self.assertTrue((skel / ".themes/ROS-Dark/cinnamon/cinnamon.css").is_file())
            self.assertTrue((skel / ".local/share/ros/first-login/configure-first-login.py").is_file())
            entry = (skel / ".config/autostart/ros-first-login.desktop").read_text()
            self.assertIn("Exec=/usr/local/bin/ros-first-login", entry)
            self.assertNotIn("testuser", entry)
            self.assertNotIn("@ROS_FIRST_LOGIN_EXEC@", entry)
            launcher = target / "rootfs/usr/local/bin/ros-first-login"
            self.assertTrue(launcher.stat().st_mode & 0o111)
            self.assertIn('"$HOME/', launcher.read_text())
            stored = json.loads((target / "manifest.json").read_text())
            self.assertFalse(stored["live_autologin_configured"])
            self.assertFalse(stored["installed_autologin_configured"])

    def test_refuse_overwriting_overlay(self):
        with tempfile.TemporaryDirectory(prefix="ros-iso-test-") as temp:
            target = Path(temp) / "overlay"
            target.mkdir()
            with self.assertRaises(FileExistsError):
                mod.create_overlay(target)

if __name__ == "__main__":
    unittest.main()
