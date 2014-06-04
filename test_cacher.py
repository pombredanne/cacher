"""Unit tests for Cacher object"""
import unittest
import sys

try:
    from unittest import mock
except ImportError:
    # < Python 3.3
    import mock

import cacher


class CacherTests(unittest.TestCase):
    """Main test case for Cacher"""
    def setUp(self):
        """Patch the module"""
        self.time = mock.patch.object(cacher, 'time').start()
        self.time.return_value = self._clock = 0.0

        self.timer = mock.patch.object(cacher, 'Timer').start()
        self._callbacks = []
        self.timer.side_effect = self._mock_timer_init

    def _mock_timer_init(self, timeout, callback, *_, **__):
        """A side effect for Timer initialization"""
        self._callbacks.append((timeout, callback))
        return self.timer.return_value

    def _run_callbacks(self):
        """Run callbacks scheduled by Timer if self._clock value is enough.

        The clock value is ajusted each time

        """
        for timeout, callback in self._callbacks[:]:
            if timeout <= self._clock:
                self._callbacks.remove((timeout, callback))
                callback()

    def jump_clock(self, sec):
        """Move clock forward, run timer callbacks and switch back

        It allows testing memory cleanup instead of expiration checking in
        `get` method.

        """
        self._clock += sec
        cur_time = self.time.return_value
        self.time.return_value = self._clock
        self._run_callbacks()
        self.time.return_value = cur_time

    def test_expire_default(self):
        """Check value expiration for default timeout"""
        value = object()
        cache = cacher.Cacher()
        cache.set('data', value)

        self.jump_clock(cacher.DEFAULT_CLEANUP_PERIOD)
        self.assertEqual(cache.get('data'), value)

        self.jump_clock(cacher.DEFAULT_CLEANUP_PERIOD + 2)
        self.assertRaises(KeyError, cache.get, 'data')

    def test_expire_custom(self):
        """Check values expiration for a custom timeout"""
        cache = cacher.Cacher(1)
        cache.set('data1', 1, 0.5)
        cache.set('data2', 2, 1)

        self.assertEqual(cache.get('data1'), 1)
        self.jump_clock(1)
        self.assertRaises(KeyError, cache.get, 'data1')

        self.assertEqual(cache.get('data2'), 2)
        self.jump_clock(1)
        self.assertRaises(KeyError, cache.get, 'data2')

    def test_disabled_check(self):
        """If init parameter is 0 or None the cleanup should be disabled"""
        cache1 = cacher.Cacher(None)
        cache2 = cacher.Cacher(0)
        cache1.set('k', 1)
        cache2.set('kk', 2)

        self.jump_clock(sys.maxsize)

        self.assertEqual(cache1.get('k'), 1)
        self.assertEqual(cache2.get('kk'), 2)
