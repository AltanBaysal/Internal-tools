import hashlib
from pathlib import Path

import pytest

from core.disk.cache import DiskCache

PLENTY = 10**12


def md5(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def cache(directory: Path, most: int = 100, free: int = PLENTY, keep_free: int = 0) -> DiskCache:
    return DiskCache(directory, most=most, keep_free=keep_free, free=lambda _: free)


def test_what_is_put_comes_back_by_its_md5(tmp_path: Path) -> None:
    store = cache(tmp_path)

    key = store.put(b"block one")

    assert key == md5(b"block one")
    assert store.get(key) == b"block one"
    assert store.get(md5(b"never put")) is None


def test_it_survives_a_restart_on_the_same_directory(tmp_path: Path) -> None:
    key = cache(tmp_path).put(b"kept")

    assert cache(tmp_path).get(key) == b"kept"


def test_a_file_whose_md5_no_longer_matches_is_a_miss_and_removed(tmp_path: Path) -> None:
    # A cached block is never trusted: a disk fault or a hand may have changed it.
    store = cache(tmp_path)
    key = store.put(b"good")
    (tmp_path / key).write_bytes(b"bad!")

    assert store.get(key) is None
    assert not (tmp_path / key).exists()


def test_the_least_recently_used_goes_first_past_the_byte_bound(tmp_path: Path) -> None:
    store = cache(tmp_path, most=10)
    one, two = store.put(b"1111"), store.put(b"2222")
    store.get(one)

    three = store.put(b"3333")

    assert store.get(two) is None
    assert store.get(one) == b"1111"
    assert store.get(three) == b"3333"


def test_a_file_past_the_whole_bound_is_not_kept(tmp_path: Path) -> None:
    store = cache(tmp_path, most=3)

    key = store.put(b"four")

    assert store.get(key) is None
    assert list(tmp_path.iterdir()) == []


def test_it_writes_nothing_when_the_disk_would_fall_below_its_room(tmp_path: Path) -> None:
    # CODE-STANDARD, Cost: every disk write looks at the free space first. A cache is a
    # convenience: with no room it keeps nothing, and the caller goes on.
    store = cache(tmp_path, free=10, keep_free=8)

    key = store.put(b"abc")

    assert store.get(key) is None
    assert list(tmp_path.iterdir()) == []


def test_nothing_is_evicted_for_a_file_that_would_not_fit_anyway(tmp_path: Path) -> None:
    # The disk's own room counts files outside the cache too: emptying the cache may not help.
    room = {"free": 100}
    store = DiskCache(tmp_path, most=100, keep_free=95, free=lambda _: room["free"])
    kept = store.put(b"12")
    room["free"] = 96

    store.put(b"1234567890")

    assert store.get(kept) == b"12"


def test_a_half_written_file_from_a_crash_is_removed_on_opening(tmp_path: Path) -> None:
    (tmp_path / "x.part").write_bytes(b"half")

    cache(tmp_path)

    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("key", ["../core.json", "ABCDEF0123456789abcdef0123456789", "short"])
def test_a_key_that_is_not_an_md5_is_refused_before_any_path(tmp_path: Path, key: str) -> None:
    # Keys come from Drive's head files: unchecked, one could name any file.
    with pytest.raises(ValueError, match="md5"):
        cache(tmp_path).get(key)
