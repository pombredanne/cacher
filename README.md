[![Build Status](https://travis-ci.org/Fedorof/cacher.svg?branch=master)](https://travis-ci.org/Fedorof/cacher)
Provide caching object with expired values automatic removing.

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

        
Note: unit tests require mock for Python<3.3
