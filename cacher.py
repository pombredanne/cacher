"""Provide caching object with expired values automatic removing.

Current implementation uses threading module to schedule cleanup.

Usage:

    There are `set`, `get` and `delete` methods (in the example we
    pass None as a cleanup period to disable automatic cleanup):

        >>> cache = Cacher(None)
        >>> cache.set('name', 2)
        >>> cache.get('name')
        2
        >>> cache.delete('name')

    Each value expires in some time (60 seconds default). This time can be
    set explicitly:

        >>> cache.set('ephemera', 14, 1)  # The third argument is a timeout
        >>> cache.get('ephemera')
        14
        >>> import time; time.sleep(1)
        >>> cache.get('ephemera')
        Traceback (most recent call last):
            ...
        KeyError: 'ephemera'

    You can manipulate the values as long as they exist in the cache:

        >>> cache.set('name', 6)
        >>> cache.get('name')
        6
        >>> cache.set('name', 8)
        >>> cache.get('name')
        8
        >>> cache.delete('name')
        >>> cache.get('name')
        Traceback (most recent call last):
            ...
        KeyError: 'name'
        >>> cache.get('not_existing')
        Traceback (most recent call last):
            ...
        KeyError: 'not_existing'

"""

from time import time
from threading import Timer

DEFAULT_CLEANUP_PERIOD = 60


class Cacher:
    """Base caching class"""
    _start_group = None

    def __init__(self, cleanup_period=DEFAULT_CLEANUP_PERIOD):
        """Initialize the cache.

        :param cleanup_period: - how often (in seconds) remove expired
            values. If 0 or None, no checks will be performed at all.

        """
        self._inner_dict = {}
        self._outer_dict = {}
        self._cleanup_period = cleanup_period
        if cleanup_period:
            self._start_group = int(time() // cleanup_period)
            self._schedule_cleanup()

    def _schedule_cleanup(self):
        """Schedule a cleanup action after `cleanup_period`"""
        Timer(self._cleanup_period, self._cleanup).start()

    def _cleanup(self):
        """Remove expired entries"""
        cur_group = self._cleanup_period and \
                    int(time() // self._cleanup_period)
        if cur_group > self._start_group:
            for group in range(self._start_group, cur_group):
                try:
                    del self._inner_dict[group]
                except KeyError:
                    pass
            self._start_group = cur_group
        self._schedule_cleanup()

    def set(self, name, value, timeout=DEFAULT_CLEANUP_PERIOD):
        """Store a value by name

        :param timeout: - entry living time (seconds).

        """
        # outer_dict maps key to a group in inner_dict;
        # inner_dict contains groups (dicts) with similar expiration time;
        # each group maps key to a tuple of (value, expire_in);
        expire_in = time() + timeout
        group_num = self._cleanup_period and \
                    int(expire_in // self._cleanup_period)

        self._outer_dict[name] = group_num
        try:
            group = self._inner_dict[group_num]
        except KeyError:
            group = self._inner_dict[group_num] = {}

        group[name] = (value, expire_in)

    def get(self, name):
        """Retrieve a value by it's name.

        Raises KeyError if a value doesn't exist or has expired.

        """
        # expire_in allows more accurate expiration control.
        group_num = self._outer_dict[name]
        value, expire_in = self._inner_dict[group_num][name]
        if time() < expire_in:
            return value
        else:
            self.delete(name)
            raise KeyError(name)

    def delete(self, name):
        """Remove an entry"""
        group_num = self._outer_dict.pop(name)
        del self._inner_dict[group_num][name]
