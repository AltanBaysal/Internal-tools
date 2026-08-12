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
    def __init__(self, fail=None):
        self.fetched = []
        self.fail = fail
        self.headers = None

    def fetch(self, url, path, headers=None, on_progress=None, cancelled=None):
        if self.fail and url == self.fail:
            raise RuntimeError("bağlantı yok")
        self.fetched.append((url, path))
        self.headers = headers
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
                          running={"kind": "video", "done": 5, "total": 10, "file": "wan"})

    assert rows[1]["installing"] == {"done": 5, "total": 10, "file": "wan"}
    assert "installing" not in rows[0]


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


def test_a_file_the_app_cannot_fetch_stops_the_install_and_says_why():
    runner = sync_installer()

    install_producer(GROUPS, FakeFiles(), FakeFetcher(), runner, {}, "audio")

    assert runner.status()["status"] == "error"
    assert "defter" in runner.status()["error"]


def test_a_producer_the_notebook_owns_cannot_be_installed_from_here():
    runner = sync_installer()

    install_producer(GROUPS, FakeFiles(), FakeFetcher(), runner, {}, "photo")

    assert runner.status()["status"] == "error"
    assert "defter" in runner.status()["error"]


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
