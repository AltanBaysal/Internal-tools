"""Which producers this machine has, and which of them are installed.

Installing is the notebook's job (FOUNDATION 9): nothing here downloads, so nothing here fakes a
download either.
"""
from backend.features.producers.domain import model_groups
from backend.features.producers.domain.usecases.list_producers import list_producers


class FakeFiles:
    def __init__(self, present=()):
        self.present = set(present)

    def exists(self, folder, name):
        return (folder, name) in self.present

    def path(self, folder, name):
        return f"/models/{folder}/{name}"


GROUPS = {
    "photo": [],
    "video": [{"folder": "vae", "name": "wan_vae.safetensors"},
              {"folder": "loras", "name": "high.safetensors"}],
    "audio": [{"folder": "mmaudio", "name": "mm.pth"}],
}


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


def test_a_row_says_nothing_about_installing_because_the_app_does_not():
    row = list_producers(GROUPS, FakeFiles())[0]

    assert set(row) == {"id", "name", "installed"}


# The shipped groups: what the panel really counts has to be what the graphs really load.


def test_the_photo_group_carries_everything_the_graph_reads():
    rows = model_groups.GROUPS["photo"]

    assert [(row["folder"], row["name"]) for row in rows] == [
        ("checkpoints", "nova3DCGXL_ilV90.safetensors"),
        ("loras", "USNR_STYLE_ILL_V1_lokr3-000024.safetensors"),
        ("upscale_models", "4x_foolhardy_Remacri.pth"),
        ("ultralytics/bbox", "face_yolov9c.pt"),
        ("sams", "sam_vit_b_01ec64.pth"),
    ]


def test_the_sound_group_names_the_weights_the_sampler_loads():
    rows = model_groups.GROUPS["audio"]

    assert len(rows) == 1, "Örnekleyici tek ağırlık dosyası yüklüyor"
    assert rows[0]["name"] == "mmaudio_large_44k_nsfw_gold_8.5k_final_fp16.safetensors"


def test_the_weights_path_is_built_from_the_group_row():
    path = model_groups.audio_weights(FakeFiles())

    assert path == "/models/mmaudio/mmaudio_large_44k_nsfw_gold_8.5k_final_fp16.safetensors"


def test_no_group_carries_an_address_the_app_would_have_to_fetch():
    """Addresses live in the notebook now. One left here would be a second truth nobody reads."""
    for group in model_groups.GROUPS.values():
        for row in group:
            assert set(row) == {"folder", "name"}
