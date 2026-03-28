import os
import tempfile
import time
import unittest

from driver.wx_api import WeChatAPI
from driver.wx import Wx


class WxLockTestCase(unittest.TestCase):
    def setUp(self):
        self.wx = Wx()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.wx.lock_file_path = os.path.join(self.temp_dir.name, "lock.lock")
        self.wx.wx_login_url = os.path.join(self.temp_dir.name, "wx_qrcode.png")

    def tearDown(self):
        self.wx._force_release_lock()
        self.temp_dir.cleanup()

    def test_check_lock_returns_true_when_lock_file_exists(self):
        self.wx.set_lock()
        self.assertTrue(self.wx.check_lock())

    def test_check_lock_clears_stale_lock(self):
        os.makedirs(os.path.dirname(self.wx.lock_file_path), exist_ok=True)
        with open(self.wx.lock_file_path, "w", encoding="utf-8") as f:
            f.write(f"999999|{time.time() - 3600}")

        self.assertFalse(self.wx.check_lock(timeout=10))
        self.assertFalse(os.path.exists(self.wx.lock_file_path))


if __name__ == "__main__":
    unittest.main()


class WeChatAPILockTestCase(unittest.TestCase):
    def setUp(self):
        self.wx_api = WeChatAPI()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.wx_api.lock_file_path = os.path.join(self.temp_dir.name, "lock.lock")
        self.wx_api.wx_login_url = os.path.join(self.temp_dir.name, "wx_qrcode.png")

    def tearDown(self):
        self.wx_api._force_release_lock()
        self.temp_dir.cleanup()

    def test_api_check_lock_returns_true_when_lock_file_exists(self):
        self.wx_api.set_lock()
        self.assertTrue(self.wx_api.check_lock())

    def test_api_check_lock_clears_stale_lock(self):
        os.makedirs(os.path.dirname(self.wx_api.lock_file_path), exist_ok=True)
        with open(self.wx_api.lock_file_path, "w", encoding="utf-8") as f:
            f.write(f"999999|{time.time() - 3600}")

        self.assertFalse(self.wx_api.check_lock(timeout=10))
        self.assertFalse(os.path.exists(self.wx_api.lock_file_path))
