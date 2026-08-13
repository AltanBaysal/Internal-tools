"""Which producers this machine has, which of them are installed, and installing one."""
import pytest

from backend.features.producers.domain import model_groups
from backend.features.producers.domain.usecases.install_producer import Busy, install_producer
from backend.features.producers.domain.usecases.list_producers import list_producers
from backend.features.producers.runner import InstallRunner


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
    def __init__(self, fail=None, log=None):
        self.fetched = []
        self.fail = fail
        self.headers = None
        # Shared with FakeLibs when a test cares about the order of the two kinds of step.
        self.log = [] if log is None else log

    def fetch(self, url, path, headers=None, on_progress=None, cancelled=None):
        if self.fail and url == self.fail:
            raise RuntimeError("bağlantı yok")
        self.fetched.append((url, path))
        self.log.append(f"file:{url}")
        self.headers = headers
        if on_progress:
            on_progress(10, 10)


class FakeLibs:
    """A library port that remembers what it was asked to do.

    `stays_missing` is the case the restart sentence exists for: the install itself succeeded, and
    this process still cannot see the module.
    """

    def __init__(self, present=(), fail=None, stays_missing=(), log=None):
        self.have = set(present)
        self.installed = []
        self.fail = fail
        self.stays_missing = set(stays_missing)
        self.log = [] if log is None else log

    def present(self, module):
        return module in self.have

    def install(self, repo, folder, module):
        self.installed.append(module)
        self.log.append(f"lib:{module}")
        if self.fail == module:
            raise RuntimeError("pip: exit 1")
        if module not in self.stays_missing:
            self.have.add(module)


class SpyRunner:
    """Runs the job inline and keeps every progress report, so what the screen was told during the
    install is assertable -- the real runner only keeps the last one."""

    def __init__(self):
        self.reports = []
        self.state = {"status": "idle"}

    def start(self, kind, job):
        self.state = {"status": "running", "kind": kind}
        self.state = {**job(), "kind": kind}
        return True

    def report(self, patch):
        self.reports.append(patch)

    def cancelled(self):
        return False


GROUPS = {
    "photo": [],
    "video": [{"folder": "vae", "name": "wan_vae.safetensors", "url": "u1"},
              {"folder": "loras", "name": "high.safetensors", "url": "u2"}],
    "audio": [{"folder": "mmaudio", "name": "mm.pth", "url": "u4"}],
}

LIBS = {"audio": [{"module": "mmaudio", "name": "MMAudio kütüphanesi", "folder": "MMAudio",
                   "repo": "https://github.com/hkchengrex/MMAudio.git"}]}


def sync_installer():
    return InstallRunner(spawn=lambda fn: fn())


def gated_groups():
    """The shipped video group's shape: one row that needs a source's key."""
    return {**GROUPS, "video": GROUPS["video"] + [
        {"folder": "loras", "name": "smooth.safetensors", "url": "u3", "auth": "civitai"}]}


def test_all_three_are_listed_in_the_order_the_engine_works_in():
    rows = list_producers(GROUPS, FakeFiles())

    assert [row["id"] for row in rows] == ["photo", "video", "audio"]
    assert [row["name"] for row in rows] == [
        "Fotoğraf üreticisi", "Video üreticisi", "Ses üreticisi"]


def test_a_producer_with_a_group_is_installed_when_every_file_of_it_is_here():
    files = FakeFiles(present=[("vae", "wan_vae.safetensors"), ("loras", "high.safetensors")])

    assert list_producers(GROUPS, files)[1]["installed"] is True


def test_one_missing_file_means_not_installed():
    files = FakeFiles(present=[("vae", "wan_vae.safetensors")])

    assert list_producers(GROUPS, files)[1]["installed"] is False


def test_a_kind_with_no_group_is_not_installed():
    assert list_producers(GROUPS, FakeFiles())[0]["installed"] is False


def test_the_running_install_is_reported_on_its_own_row():
    rows = list_producers(GROUPS, FakeFiles(),
                          running={"status": "running", "kind": "video",
                                   "step": "wan.safetensors"})

    # The step being worked on, and nothing else: a percentage that restarts per file was movement
    # rather than information.
    assert rows[1]["installing"] == {"step": "wan.safetensors"}
    assert "installing" not in rows[0]


def test_a_finished_install_leaves_no_row_claiming_to_be_running():
    rows = list_producers(GROUPS, FakeFiles(), running={"status": "done", "kind": "video"})

    assert all("installing" not in row for row in rows)


def test_a_failed_install_shows_its_own_words_instead_of_running_forever():
    rows = list_producers(GROUPS, FakeFiles(),
                          running={"status": "error", "kind": "video", "error": "bağlantı yok"})

    assert "installing" not in rows[1]
    assert rows[1]["error"] == "bağlantı yok"


def test_it_fetches_only_what_is_missing():
    files = FakeFiles(present=[("vae", "wan_vae.safetensors")])
    fetcher = FakeFetcher()

    install_producer(GROUPS, files, fetcher, sync_installer(), {}, "video")

    assert [url for url, _path in fetcher.fetched] == ["u2"]


def test_a_second_install_is_refused_while_one_runs():
    runner = InstallRunner(spawn=lambda fn: None)      # claimed, never finishes
    install_producer(GROUPS, FakeFiles(), FakeFetcher(), runner, {}, "video")

    with pytest.raises(Busy):
        install_producer(GROUPS, FakeFiles(), FakeFetcher(), runner, {}, "audio")


def test_a_producer_with_no_files_declared_cannot_be_installed():
    # Not silently "done": a kind whose group is empty has nothing to install, and saying it
    # finished would leave the panel claiming an installed producer that has no files at all.
    runner = sync_installer()

    install_producer(GROUPS, FakeFiles(), FakeFetcher(), runner, {}, "photo")

    assert runner.status()["status"] == "error"
    assert "Fotoğraf üreticisi" in runner.status()["error"]
    assert "defter" not in runner.status()["error"]


def test_the_library_is_installed_before_the_weights():
    """A library is what makes the producer usable at all, and its failure is worth seeing before
    minutes of downloading."""
    steps = []
    libs = FakeLibs(log=steps)

    install_producer(GROUPS, FakeFiles(), FakeFetcher(log=steps), sync_installer(), {}, "audio",
                     libraries=LIBS, lib=libs)

    assert steps == ["lib:mmaudio", "file:u4"]


def test_a_library_that_is_already_here_is_not_installed_again():
    libs = FakeLibs(present=["mmaudio"])

    install_producer(GROUPS, FakeFiles(), FakeFetcher(), sync_installer(), {}, "audio",
                     libraries=LIBS, lib=libs)

    assert libs.installed == []


def test_a_failed_library_install_stops_before_the_weights():
    runner, fetcher = sync_installer(), FakeFetcher()

    install_producer(GROUPS, FakeFiles(), fetcher, runner, {}, "audio",
                     libraries=LIBS, lib=FakeLibs(fail="mmaudio"))

    assert fetcher.fetched == []
    assert runner.status()["status"] == "error"
    assert "pip: exit 1" in runner.status()["error"]


def test_a_library_this_process_still_cannot_see_asks_for_a_restart():
    runner, fetcher = sync_installer(), FakeFetcher()

    install_producer(GROUPS, FakeFiles(), fetcher, runner, {}, "audio",
                     libraries=LIBS, lib=FakeLibs(stays_missing=["mmaudio"]))

    assert fetcher.fetched == []
    assert "yeniden başlat" in runner.status()["error"]


def test_the_library_step_is_named_before_it_starts():
    runner = SpyRunner()

    install_producer(GROUPS, FakeFiles(), FakeFetcher(), runner, {}, "audio",
                     libraries=LIBS, lib=FakeLibs())

    assert runner.reports[0]["step"] == "MMAudio kütüphanesi"


def test_a_producer_with_neither_a_file_nor_a_library_cannot_be_installed():
    runner = sync_installer()

    install_producer(GROUPS, FakeFiles(), FakeFetcher(), runner, {}, "photo",
                     libraries=LIBS, lib=FakeLibs())

    assert runner.status()["status"] == "error"
    assert "Fotoğraf üreticisi" in runner.status()["error"]


def test_a_producer_whose_library_is_missing_is_not_installed():
    """The one case the panel used to lie about: the weights are here, the engine is not."""
    files = FakeFiles(present=[("mmaudio", "mm.pth")])

    rows = list_producers(GROUPS, files, libraries=LIBS, lib=FakeLibs())

    assert rows[2]["installed"] is False


def test_it_is_installed_when_both_the_library_and_the_weights_are_here():
    files = FakeFiles(present=[("mmaudio", "mm.pth")])

    rows = list_producers(GROUPS, files, libraries=LIBS, lib=FakeLibs(present=["mmaudio"]))

    assert rows[2]["installed"] is True


def test_a_gated_row_is_fetched_with_its_sources_headers():
    fetcher = FakeFetcher()

    install_producer(gated_groups(), FakeFiles(), fetcher, sync_installer(),
                     {"civitai": {"Cookie": "k=v"}}, "video")

    assert fetcher.headers == {"Cookie": "k=v"}


def test_a_gated_row_with_no_key_stops_the_install_and_names_the_source():
    runner = sync_installer()

    install_producer(gated_groups(), FakeFiles(), FakeFetcher(), runner, {}, "video")

    assert runner.status()["status"] == "error"
    assert "smooth.safetensors" in runner.status()["error"]
    assert "civitai" in runner.status()["error"]


# The shipped group, not the fixture above: what the panel really counts for sound has to be the
# one file the sampler really loads.


def test_the_sound_group_names_the_weights_the_sampler_loads():
    rows = model_groups.GROUPS["audio"]
    assert len(rows) == 1, "Örnekleyici tek ağırlık dosyası yüklüyor"
    assert rows[0]["name"] == "mmaudio_large_44k_nsfw_gold_8.5k_final_fp16.safetensors"


def test_the_sound_weights_can_be_fetched_by_the_app_itself():
    """No token stands in front of this one, unlike the Civitai rows -- so the panel's Kur button
    is enough and the user is not sent off to download a file by hand."""
    url = model_groups.GROUPS["audio"][0]["url"]
    assert url and "phazei/NSFW_MMaudio" in url


def test_the_weights_path_is_built_from_the_group_row():
    class FakeFiles:
        def path(self, folder, name):
            return f"/root/models/{folder}/{name}"

    path = model_groups.audio_weights(FakeFiles())

    assert path == ("/root/models/mmaudio/"
                    "mmaudio_large_44k_nsfw_gold_8.5k_final_fp16.safetensors")


def test_the_video_group_has_nothing_the_app_cannot_fetch():
    assert all(row["url"] for row in model_groups.GROUPS["video"])


def test_every_gated_row_says_which_source_it_needs():
    gated = [row for row in model_groups.GROUPS["video"] if row.get("auth")]

    assert len(gated) == 4                                   # the two SmoothMix pairs
    assert all(row["auth"] == model_groups.CIVITAI for row in gated)
    assert all(row["url"].startswith(model_groups.CIVITAI_DOWNLOAD) for row in gated)


def test_the_civitai_header_carries_the_cookie_under_its_own_name():
    assert model_groups.civitai_headers("abc") == {"Cookie": "__Secure-civ-token=abc"}


def test_the_photo_group_carries_everything_the_graph_reads():
    rows = model_groups.GROUPS["photo"]

    assert [(row["folder"], row["name"]) for row in rows] == [
        ("checkpoints", "nova3DCGXL_ilV90.safetensors"),
        ("loras", "USNR_STYLE_ILL_V1_lokr3-000024.safetensors"),
        ("upscale_models", "4x_foolhardy_Remacri.pth"),
        ("ultralytics/bbox", "face_yolov9c.pt"),
        ("sams", "sam_vit_b_01ec64.pth"),
    ]
    assert all(row["url"] for row in rows)


def test_only_the_civitai_rows_of_the_photo_group_need_a_key():
    gated = [row["name"] for row in model_groups.GROUPS["photo"] if row.get("auth")]

    assert gated == ["nova3DCGXL_ilV90.safetensors",
                     "USNR_STYLE_ILL_V1_lokr3-000024.safetensors"]


def test_the_sound_producer_declares_the_engine_it_runs_in_this_process():
    rows = model_groups.LIBRARIES["audio"]

    assert len(rows) == 1, "Ses motoru tek kütüphane"
    assert rows[0]["module"] == "mmaudio"
    assert "hkchengrex/MMAudio" in rows[0]["repo"]


def test_the_graph_producers_need_no_library_of_their_own():
    """Photo and video run in ComfyUI, which the notebook still installs."""
    assert set(model_groups.LIBRARIES) == {"audio"}
