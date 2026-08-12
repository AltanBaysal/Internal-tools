"""Streaming one file to disk: progress while it lands, and a way to stop it."""
import pytest

from backend.services.download.fetcher import Cancelled, HttpFetcher


class FakeResponse:
    def __init__(self, chunks, total=None):
        self.chunks = list(chunks)
        self.headers = {"Content-Length": str(total)} if total is not None else {}

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def iter(self, size):
        return iter(self.chunks)


def opener(response):
    return lambda url: response


def test_it_writes_the_whole_file_and_reports_as_it_goes(tmp_path):
    seen = []
    fetcher = HttpFetcher(opener(FakeResponse([b"ab", b"cd"], total=4)))
    target = tmp_path / "deep" / "model.safetensors"

    fetcher.fetch("http://x", str(target), on_progress=lambda d, t: seen.append((d, t)))

    assert target.read_bytes() == b"abcd"
    assert seen == [(2, 4), (4, 4)]


def test_a_server_that_gives_no_length_reports_an_unknown_total(tmp_path):
    seen = []
    fetcher = HttpFetcher(opener(FakeResponse([b"ab"])))

    fetcher.fetch("http://x", str(tmp_path / "m"), on_progress=lambda d, t: seen.append((d, t)))

    assert seen == [(2, None)]


def test_cancelling_stops_the_download_and_leaves_no_half_file(tmp_path):
    target = tmp_path / "m"
    fetcher = HttpFetcher(opener(FakeResponse([b"ab", b"cd"], total=4)))

    with pytest.raises(Cancelled):
        fetcher.fetch("http://x", str(target), cancelled=lambda: True)

    assert not target.exists()
    assert not (tmp_path / "m.part").exists()


def test_a_download_that_dies_leaves_nothing_that_looks_finished(tmp_path):
    class Exploding(FakeResponse):
        def iter(self, size):
            yield b"ab"
            raise RuntimeError("bağlantı koptu")

    target = tmp_path / "m"
    fetcher = HttpFetcher(opener(Exploding([], total=4)))

    with pytest.raises(RuntimeError):
        fetcher.fetch("http://x", str(target))

    assert not target.exists()
