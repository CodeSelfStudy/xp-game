"""
This module contains functions to manage assets.
"""
from time import time


def cache_buster():
    """Return a query string that will bust the cache.

    It's based on the current timestamp, converted to hex.

    Example output: '?rnd=5d61d4e1'
    """
    uniq = hex(int(time()))[2:]
    return f'?cache={uniq}'
