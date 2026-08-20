"""What app.ipynb says.

The notebook is read, never run: a Colab cell cannot execute here -- there is no google.colab, no
Drive, no tunnel. What text can still answer is the part that matters, which is whether each cell
does the thing it is there for, where each secret comes from, and whether a missing one is said out
loud.

Parsed rather than read raw: the file is JSON, so a raw read would be searching escaped quotes and
line breaks instead of the code the cell runs.
"""
import json
import os

NOTEBOOK = os.path.join(
    os.path.dirname(          # queen-agent
        os.path.dirname(      # backend
            os.path.dirname(os.path.abspath(__file__)))),  # tests
    "app.ipynb",
)

CONFIG = "# === CONFIG ==="


def _cells():
    if not os.path.exists(NOTEBOOK):
        return []
    with open(NOTEBOOK, encoding="utf-8") as handle:
        return json.load(handle).get("cells", [])


def _source():
    """Every cell's source as one blob -- for questions about whether something is there at all."""
    return "\n".join("".join(cell.get("source", "")) for cell in _cells())


def _cell(marker):
    """The source of the first cell carrying `marker`, or "".

    Some questions are about WHERE something is rather than whether it exists, and the blob above
    cannot tell one cell from another.
    """
    for cell in _cells():
        source = "".join(cell.get("source", ""))
        if marker in source:
            return source
    return ""


def test_the_notebook_is_there_and_parses():
    """Asked on its own so the rest fail for their own reasons. Without it a missing file makes
    every test below fail identically and none of them says why."""
    assert os.path.exists(NOTEBOOK), f"Defter yok: {NOTEBOOK}"
    assert _cells(), "Defterde hiç hücre yok"


def test_drive_is_mounted_before_anything_else():
    """The permission window has to appear in the first second (NOTEBOOK-STANDARD). One that shows
    up forty seconds in waits on a user who has already walked away."""
    config = _cell(CONFIG)
    assert "drive.mount" in config, "CONFIG hücresinde Drive bağlanmıyor"

    before = config.split("drive.mount")[0].splitlines()
    working = [
        line for line in before
        if line.strip() and not line.strip().startswith("#")
        and not line.strip().startswith(("import ", "from "))
    ]
    assert working == [], f"Drive bağlanmadan önce iş yapan satırlar var: {working}"


def test_the_drive_folder_is_named_once():
    # Two copies of a name become a lie the first time one of them changes.
    assert _source().count("queenAgent") == 1, "queenAgent adı bir kereden fazla geçiyor"
    assert 'DRIVE_FOLDER = "queenAgent"' in _source()


def test_an_unmounted_drive_does_not_pass_quietly():
    """Writing under /content/drive without a mount lands on Colab's local disk, and that folder dies
    with the runtime -- the user believes it worked and loses everything later."""
    assert "os.path.isdir(DRIVE_ROOT)" in _cell(CONFIG), "Kök gerçekten orada mı diye bakılmıyor"


def test_the_token_comes_from_secrets_not_the_source():
    source = _source()
    assert 'userdata.get("GITHUB_TOKEN")' in source, "Token Colab Secrets'tan okunmuyor"
    # The notebook is in git; a token pasted into it would sit inside the repo it opens.
    for leak in ("github_pat_", "ghp_"):
        assert leak not in source, f"Deftere bir token yapıştırılmış ({leak}…)"


def test_a_missing_token_says_what_to_do():
    said = _cell("assert GITHUB_TOKEN")
    assert said, "Token yokken defter sessizce devam ediyor"
    assert "Secrets" in said and "GITHUB_TOKEN" in said, "Ne yapılacağı söylenmiyor"


def test_the_xai_key_is_not_asked_for_here():
    """queen-editor reads it from Secrets. QueenAgent has its own Settings screen and the key lands
    in settings.json on Drive -- written once, kept forever. Deliberate, and without this test
    someone reads the difference as an omission and adds it back."""
    assert "XAI_API_KEY" not in _source(), "xAI anahtarı defterde sorulmamalı — Settings'e giriliyor"
