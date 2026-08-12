"""Which producers this machine has, which of them are installed, and installing one."""
import pytest

from backend.features.producers.domain.usecases.install_producer import Busy, install_producer
from backend.features.producers.domain.usecases.list_producers import list_producers
from backend.features.producers.runner import InstallRunner


class FakeProducer:
    def __init__(self, installed=True, boom=None):
        self._installed = installed
        self._boom = boom

    def installed(self):
        if self._boom:
            raise RuntimeError(self._boom)
        return self._installed


class FakeFiles:
    def __init__(self, present=()):
        self.present = set(present)
        self.removed = []

    def exists(self, folder, name):
        return (folder, name) in self.present

    def path(self, folder, name):
        return f"/models/{folder}/{name}"

    def remove(self, folder, name):
        self.removed.append((folder, name))
        self.present.discard((folder, name))


class FakeFetcher:
    def __init__(self, fail=None):
        self.fetched = []
        self.fail = fail

    def fetch(self, url, path, on_progress=None, cancelled=None):
        if self.fail and url == self.fail:
            raise RuntimeError("bağlantı yok")
        self.fetched.append((url, path))
        if on_progress:
            on_progress(10, 10)


GROUPS = {
    "photo": [],
    "video": [{"folder": "vae", "name": "wan_vae.safetensors", "url": "u1"},
              {"folder": "loras", "name": "high.safetensors", "url": "u2"}],
    "audio": [{"folder": "mmaudio", "name": "mm.pth", "url": None}],
}


def sync_installer():
    return InstallRunner(spawn=lambda fn: fn())


def test_all_three_are_listed_in_the_order_the_engine_works_in():
    rows = list_producers(GROUPS, FakeFiles(), {})

    assert [row["id"] for row in rows] == ["photo", "video", "audio"]
    assert [row["name"] for row in rows] == [
        "Fotoğraf üreticisi", "Video üreticisi", "Ses üreticisi"]


def test_a_producer_with_a_group_is_installed_when_every_file_of_it_is_here():
    files = FakeFiles(present=[("vae", "wan_vae.safetensors"), ("loras", "high.safetensors")])

    assert list_producers(GROUPS, files, {})[1]["installed"] is True


def test_one_missing_file_means_not_installed():
    files = FakeFiles(present=[("vae", "wan_vae.safetensors")])

    assert list_producers(GROUPS, files, {})[1]["installed"] is False


def test_a_producer_with_no_group_answers_for_itself():
    # The notebook sets the photo producer up, and which checkpoint it holds is the user's choice --
    # so the renderer is asked instead of a list of file names we do not own.
    rows = list_producers(GROUPS, FakeFiles(), {"photo": FakeProducer(installed=True)})

    assert rows[0]["installed"] is True


def test_a_kind_with_neither_a_group_nor_a_producer_is_not_installed():
    assert list_producers(GROUPS, FakeFiles(), {})[0]["installed"] is False


def test_a_producer_that_cannot_answer_is_not_quietly_called_missing():
    # Saying "not installed" would invite a download nobody needs; the caller has to hear the
    # renderer's own words instead.
    with pytest.raises(RuntimeError):
        list_producers(GROUPS, FakeFiles(), {"photo": FakeProducer(boom="Bağlantı yok")})


def test_the_running_install_is_reported_on_its_own_row():
    rows = list_producers(GROUPS, FakeFiles(), {},
                          running={"kind": "video", "done": 5, "total": 10, "file": "wan"})

    assert rows[1]["installing"] == {"done": 5, "total": 10, "file": "wan"}
    assert "installing" not in rows[0]


def test_it_fetches_only_what_is_missing():
    files = FakeFiles(present=[("vae", "wan_vae.safetensors")])
    fetcher = FakeFetcher()

    install_producer(GROUPS, files, fetcher, sync_installer(), "video")

    assert [url for url, _path in fetcher.fetched] == ["u2"]


def test_a_second_install_is_refused_while_one_runs():
    runner = InstallRunner(spawn=lambda fn: None)      # claimed, never finishes
    install_producer(GROUPS, FakeFiles(), FakeFetcher(), runner, "video")

    with pytest.raises(Busy):
        install_producer(GROUPS, FakeFiles(), FakeFetcher(), runner, "audio")


def test_a_file_the_app_cannot_fetch_stops_the_install_and_says_why():
    runner = sync_installer()

    install_producer(GROUPS, FakeFiles(), FakeFetcher(), runner, "audio")

    assert runner.status()["status"] == "error"
    assert "defter" in runner.status()["error"]


def test_a_producer_the_notebook_owns_cannot_be_installed_from_here():
    runner = sync_installer()

    install_producer(GROUPS, FakeFiles(), FakeFetcher(), runner, "photo")

    assert runner.status()["status"] == "error"
    assert "defter" in runner.status()["error"]
