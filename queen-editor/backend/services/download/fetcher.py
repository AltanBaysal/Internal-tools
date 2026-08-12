"""One file, from a URL to a path, in pieces.

A service: it knows no producer, no model and no folder layout -- only how to move bytes and how to
be stopped. `open_url` is injected so tests never touch the network.

The file is written under a .part name and renamed at the end: a run that dies leaves nothing that
looks finished, so "is this file here?" stays a question about the real name.
"""
import os
import urllib.request

CHUNK = 1 << 20     # 1 MiB: big enough that progress is not a syscall storm, small enough to stop


class Cancelled(Exception):
    """The user asked for the download to stop (message is user-facing)."""


class _Streamed:
    """urlopen's response behind the one method the fetcher uses."""

    def __init__(self, response):
        self._response = response
        self.headers = response.headers

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self._response.close()
        return False

    def iter(self, size):
        while True:
            chunk = self._response.read(size)
            if not chunk:
                return
            yield chunk


def _open(url):
    return _Streamed(urllib.request.urlopen(url))


class HttpFetcher:
    def __init__(self, open_url=None):
        self._open = open_url or _open

    def fetch(self, url, path, on_progress=None, cancelled=None):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        partial = f"{path}.part"
        done = 0
        try:
            with self._open(url) as response:
                total = self._length(response)
                with open(partial, "wb") as out:
                    for chunk in response.iter(CHUNK):
                        if cancelled and cancelled():
                            raise Cancelled("Kurulum iptal edildi.")
                        out.write(chunk)
                        done += len(chunk)
                        if on_progress:
                            on_progress(done, total)
            os.replace(partial, path)
        except BaseException:
            # Whatever went wrong -- a cancel, the network, the disk -- the half file goes with it.
            if os.path.exists(partial):
                os.remove(partial)
            raise

    @staticmethod
    def _length(response):
        raw = response.headers.get("Content-Length")
        return int(raw) if raw else None
