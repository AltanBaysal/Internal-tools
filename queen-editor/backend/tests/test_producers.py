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

    def has_any(self, folder, suffix):
        # Answered from the same set as exists(): a fake with two stores could describe a machine
        # where a file is there and not there at once, and pass a test the real one would fail.
        return any(at == folder and name.endswith(suffix) for at, name in self.present)

    def path(self, folder, name):
        return f"/models/{folder}/{name}"


GROUPS = {
    "photo": [],
    "video": [{"folder": "vae", "name": "wan_vae.safetensors"},
              {"folder": "loras", "name": "high.safetensors"}],
    "audio": [{"folder": "mmaudio", "name": "mm.pth"}],
}

# A group shaped the way the photo one is since Madde 140: the checkpoint names a kind of file
# rather than one file, because which model is on the machine is the user's pick.
PICKED = {"photo": [{"folder": "checkpoints", "suffix": ".safetensors"},
                    {"folder": "loras", "name": "style.safetensors"}]}


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


def test_the_photo_producer_is_installed_with_whichever_model_was_picked():
    """Madde 140 turned every checkpoint into a box of its own, so the panel cannot ask for one by
    name any more -- a user who ticked only the second model renders fine and must read as
    installed."""
    files = FakeFiles(present=[("checkpoints", "novaOrangeXL_rexV10.safetensors"),
                               ("loras", "style.safetensors")])

    assert list_producers(PICKED, files)[0]["installed"] is True


def test_a_checkpoint_folder_with_nothing_in_it_is_not_installed():
    """The other half of the same claim: any is not none."""
    files = FakeFiles(present=[("loras", "style.safetensors")])

    assert list_producers(PICKED, files)[0]["installed"] is False


def test_a_half_written_download_is_not_a_model():
    """The notebook fetches into <name>.part and renames only once it has validated the file, so an
    interrupted run leaves one behind. Counting it would make the panel lie the other way round --
    ready over a checkpoint ComfyUI cannot load."""
    files = FakeFiles(present=[("checkpoints", "novaOrangeXL_rexV10.safetensors.part"),
                               ("loras", "style.safetensors")])

    assert list_producers(PICKED, files)[0]["installed"] is False


def test_a_row_says_nothing_about_installing_because_the_app_does_not():
    row = list_producers(GROUPS, FakeFiles())[0]

    assert set(row) == {"id", "name", "installed"}


# The shipped groups: what the panel really counts has to be what the graphs really load.


def test_the_photo_group_carries_everything_the_graph_reads():
    """The checkpoint is the one row naming a kind rather than a file: which model is on the machine
    is the user's pick since Madde 140, and the graph renders with whichever it was handed. The
    other four are branches of the graph, and each is loaded by its own name."""
    rows = model_groups.GROUPS["photo"]

    assert rows[0] == {"folder": "checkpoints", "suffix": ".safetensors"}
    assert [(row["folder"], row["name"]) for row in rows[1:]] == [
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
    """Addresses live in the notebook now. One left here would be a second truth nobody reads.

    Two shapes are allowed and no third: a row names a file, or it names a kind of file.
    """
    for group in model_groups.GROUPS.values():
        for row in group:
            assert set(row) in ({"folder", "name"}, {"folder", "suffix"}), row
