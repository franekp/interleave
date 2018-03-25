import unittest
import thread
import threading

from threadmock import patch_c_func


class TestPatchCFunc(unittest.TestCase):
    def test_patch_thread_lock(self):
        def assert_inactive():
            self.assertNotIsInstance(thread.allocate_lock(), FakeLock)
            self.assertIsInstance(thread.allocate_lock(), thread.LockType)
            self.assertNotIsInstance(threading.Lock(), FakeLock)
            self.assertIsInstance(threading.Lock(), thread.LockType)

        def assert_active():
            self.assertIsInstance(thread.allocate_lock(), FakeLock)
            self.assertNotIsInstance(thread.allocate_lock(), thread.LockType)
            self.assertIsInstance(threading.Lock(), FakeLock)
            self.assertNotIsInstance(threading.Lock(), thread.LockType)

        class FakeLock(object):
            pass

        assert_inactive()
        patch_c_func.patch(thread.allocate_lock, FakeLock)
        assert_active()
        patch_c_func.unpatch(thread.allocate_lock)
        assert_inactive()
