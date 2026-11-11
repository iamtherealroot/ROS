#!/usr/bin/env python3
"""Regression checks for ROS first-login 1.2.1 panel detection; no GUI required."""
import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/configure-first-login.py"
spec = importlib.util.spec_from_file_location("ros_first_login", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class FirstLoginPanelTests(unittest.TestCase):
    def test_saved_stock_is_safe_to_convert(self):
        result, note = mod.prepare_panel(list(mod.MINT_223_STOCK_APPLETS), True)
        self.assertIsNotNone(result)
        self.assertIn(mod.TREE_UUID, " ".join(result))
        self.assertNotIn("power@cinnamon.org:", " ".join(result))
        self.assertEqual(len(result), len(mod.MINT_223_STOCK_APPLETS))
        self.assertIn("Verified", note)

    def test_existing_custom_panel_is_preserved(self):
        altered = list(mod.MINT_223_STOCK_APPLETS)
        altered.pop(3)
        result, _ = mod.prepare_panel(altered, True)
        self.assertIsNone(result)

    def test_existing_ros_tree_not_duplicated(self):
        applets = list(mod.MINT_223_STOCK_APPLETS)
        applets[-3] = "panel1:right:9:ros-power-tree@iamtherealroot:15"
        result, _ = mod.prepare_panel(applets, True)
        self.assertIsNone(result)

    def test_recognized_pin_baseline(self):
        data = {"pinned-apps": {"value": ["nemo.desktop", "firefox.desktop", "terminator.desktop"]}}
        result, _ = mod.prepare_pins(data, data["pinned-apps"]["value"])
        self.assertEqual(result["pinned-apps"]["value"], mod.TARGET_PINS)

    def test_custom_pins_are_preserved(self):
        data = {"pinned-apps": {"value": ["custom-app.desktop"]}}
        result, _ = mod.prepare_pins(data, data["pinned-apps"]["value"])
        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()
