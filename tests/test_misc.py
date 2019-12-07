"""Tests miscellaneous utilities."""


import time
import concurrent.futures

import redis_lock

from truestory.misc import get_redis_client


redis_client = get_redis_client()


def _add_length(items, *, use_lock):
    if use_lock:
        lock_name = "test-redis-lock"
        lock = redis_lock.Lock(redis_client, lock_name)
        lock.acquire()

    length = len(items)
    time.sleep(0.01)
    items.add(length)

    if use_lock:
        lock.release()


def test_redis_lock():
    expect_dict = {
        False: {0},
        True: {0, 1}
    }

    for use_lock, content in expect_dict.items():
        items = set()
        futures = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            for _ in range(2):
                future = executor.submit(_add_length, items, use_lock=use_lock)
                futures.append(future)
            for future in concurrent.futures.as_completed(futures):
                future.result()

        assert items == content
