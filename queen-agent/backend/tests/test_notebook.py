"""What queenagent.ipynb says.

The notebook is read, never run: a Colab cell cannot execute here -- there is no google.colab, no
Drive, no tunnel. What text can still answer is the part that matters, which is whether each cell
does the thing it is there for, where each secret comes from, and whether a missing one is said out
loud.

Parsed rather than read raw: the file is JSON, so a raw read would be searching escaped quotes and
line breaks instead of the code the cell runs.
"""
import json
import os

TOOL = os.path.dirname(          # queen-agent
    os.path.dirname(             # backend
        os.path.dirname(os.path.abspath(__file__))))  # tests
NOTEBOOK = os.path.join(TOOL, "queenagent.ipynb")

CONFIG = "# === CONFIG ==="
CLONE = "# === Clone ==="
SERVE = "# === Serve ==="


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


def test_the_notebook_carries_the_tool_s_own_name():
    """Colab shows a notebook by its file name alone -- the title inside it never reaches the tab.
    Two tools open at once are told apart by that name and nothing else, and Run all in the wrong
    tab clones the wrong repo and starts the wrong app. Read from the folder rather than written
    down, so renaming a tool carries the rule with it.
    """
    found = sorted(name for name in os.listdir(TOOL) if name.endswith(".ipynb"))

    assert found == [os.path.basename(TOOL).replace("-", "") + ".ipynb"], \
        f"Defterin adı aracının adı değil: {found}"


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


def test_the_notebook_clones_main():
    """Released work lives on main. A notebook handed to someone else clones what is released --
    a feature branch is alive for as long as its madde is, and this one outlived its own."""
    assert 'BRANCH       = "main"' in _cell(CONFIG), "Defter main'den klonlamıyor"


def test_the_notebook_ships_pointing_at_no_feature_branch():
    """The wider rule, and the one that actually bites. Pointing BRANCH at your own branch while a
    madde is being run is ordinary; committing it that way is not, and it keeps working until the
    branch is deleted -- so nothing says it is wrong until long after it was done."""
    assert "feat/" not in _source(), (
        "Defterde bir özellik dalı adı kalmış — commit'lemeden önce BRANCH main'e çevrilmeli"
    )


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


def test_the_xai_key_comes_from_secrets():
    """Madde 62: the same panel the token comes from, the same way queen-editor has always read it.
    The Settings screen that used to hold it is gone -- it served the key back in plain text over a
    link with no password."""
    assert 'userdata.get("XAI_API_KEY")' in _source(), "xAI anahtarı Secrets'tan okunmuyor"


def test_a_missing_xai_key_says_what_to_do():
    """Colab has no second road for it: there is no screen to type it into later, so an app started
    without one can do nothing at all. Stopping here beats failing on the first message."""
    said = _cell("assert XAI_API_KEY")
    assert said, "xAI anahtarı yokken defter sessizce devam ediyor"
    assert "Secrets" in said and "XAI_API_KEY" in said, "Ne yapılacağı söylenmiyor"


def test_the_xai_key_travels_to_the_app_in_the_environment():
    """The same road QUEENAGENT_ROOT takes. config.py reads it at startup and nothing else does."""
    assert '"XAI_API_KEY": XAI_API_KEY' in _cell(SERVE), "Anahtar uygulamaya geçirilmiyor"


def test_the_deepseek_key_comes_from_secrets():
    """Madde 146: a second provider, and its key takes the road the first one's takes."""
    assert 'userdata.get("DEEPSEEK_API_KEY")' in _source(), "DeepSeek anahtarı Secrets'tan okunmuyor"


def test_a_missing_deepseek_key_says_what_to_do():
    """Both keys are required rather than one of them (kullanıcı kararı, 2 Eylül).

    The composer draws three rows, so a run opened on a single key promises two models it cannot
    answer with -- offering three is what obliges all three to work.
    """
    said = _cell("assert DEEPSEEK_API_KEY")
    assert said, "DeepSeek anahtarı yokken defter sessizce devam ediyor"
    assert "Secrets" in said and "DEEPSEEK_API_KEY" in said, "Ne yapılacağı söylenmiyor"


def test_the_deepseek_key_travels_to_the_app_in_the_environment():
    assert '"DEEPSEEK_API_KEY": DEEPSEEK_API_KEY' in _cell(SERVE), (
        "DeepSeek anahtarı uygulamaya geçirilmiyor"
    )


def test_the_notebook_no_longer_points_at_a_settings_screen():
    """It used to close by telling the user to open Settings and paste the key. That screen no
    longer exists, and an instruction pointing at a screen that is not there is worse than none."""
    assert "Settings" not in _source(), "Defter hâlâ bir Settings ekranını işaret ediyor"


def test_no_api_key_is_ever_printed():
    """The sibling of the rule that keeps the clone URL out of the output, and a lock rather than a
    test: nothing interpolates a key today, so it cannot fail yet.

    Asked about the value, not the name. The first version banned the string XAI_API_KEY from any
    print line and went red the moment the notebook told the user which secret to add -- which is a
    sentence the user needs. The name belongs in the output; only the value must never reach it, and
    it can only get there by interpolation or as the argument itself.

    Over both keys since Madde 146: a rule written for one of two is a rule the second one escapes.
    """
    for name in ("XAI_API_KEY", "DEEPSEEK_API_KEY"):
        for line in _source().splitlines():
            if "print(" not in line:
                continue
            assert "{" + name not in line, f"Anahtarın değeri basılıyor: {line.strip()}"
            assert f"print({name}" not in line, f"Anahtarın değeri basılıyor: {line.strip()}"


# --- Madde 56: the clone -------------------------------------------------------------------------


def test_the_clone_deletes_and_starts_again():
    """A disposable tree with one behaviour. A pull can stop on a merge conflict, and a user staring
    at that has no way to know what it means or what to do."""
    clone = _cell(CLONE)
    assert "shutil.rmtree" in clone, "Klon, eski ağacı silmiyor"
    assert "git pull" not in _source(), "Defterde pull var — klon tek davranışlı olmalı"


def test_the_token_never_reaches_the_shell():
    """Asked as what the cell DOES rather than only what it avoids: a rule written as an absence
    alone can never fail before the code exists, and a test that cannot fail has proved nothing."""
    clone = _cell(CLONE)
    assert '["git", "clone"' in clone, "Klon bir argüman listesiyle çalıştırılmıyor"
    # A URL that goes through a shell lands in its history and in log lines.
    assert "shell=True" not in _source(), "Kabuk üzerinden çalıştırma var — token oraya sızar"


def test_the_clone_url_is_never_printed():
    """The one string carrying the token. The cell has to report something -- otherwise this walks
    over an empty list and passes without looking at anything."""
    printed = [line for line in _cell(CLONE).splitlines() if "print(" in line]
    assert printed, "Klon hücresi hiçbir şey söylemiyor"
    for line in printed:
        assert "clone_url" not in line, f"Token taşıyan URL basılıyor: {line.strip()}"


def test_a_failed_clone_shows_git_own_words_masked():
    """A 403 has a dozen causes and the notebook knows none of them, so it prints what git said --
    with the token taken out of it."""
    clone = _cell(CLONE)
    assert "_mask" in clone, "Maskeleme yok — hata metni token taşıyabilir"
    assert "result.stderr" in clone, "git'in kendi sözleri basılmıyor"


def test_flask_is_installed_rather_than_assumed():
    """The app's only third-party dependency. Colab already has it, so this costs nothing -- but a
    notebook that quietly leans on what Colab happens to ship is one that breaks silently.

    Asked as "a pip line that names flask" rather than the exact string `pip install`: it was written
    that way at first and pinned a spelling instead of the rule, which `["pip", "install", …]` fails
    while doing exactly what the rule asks.
    """
    installs = [
        line for line in _cell(CLONE).splitlines()
        if "pip" in line and "flask" in line.lower()
    ]
    assert installs, "Flask kurulmuyor — defter Colab'da var olduğuna güveniyor"


def test_the_built_frontend_is_looked_for_after_the_clone():
    """The repo side of Madde 54. There it is asked whether the bundle was committed; here, whether
    it arrived -- so a forgotten rebuild stops the cell rather than reaching the user as a blank
    page."""
    clone = _cell(CLONE)
    assert "frontend/dist/index.html" in clone or "dist" in clone
    assert "assert" in clone, "Derlenmiş arayüz yoksa hücre durmuyor"


def test_the_clone_cell_refuses_to_run_before_config():
    """Its paths are defined in CONFIG. Without this gate a CONFIG that failed stays invisible until
    something much later breaks for a reason nobody can trace back."""
    assert 'assert "CLONE_DIR" in globals()' in _cell(CLONE)


# --- Madde 57: serving it ------------------------------------------------------------------------


def test_the_root_travels_to_the_app_in_the_environment():
    """The app learns where to write from QUEENAGENT_ROOT. Unset, it falls back to a home directory
    -- on Colab that is local disk, which dies with the runtime while the user believes it worked."""
    assert '"QUEENAGENT_ROOT": DRIVE_ROOT' in _cell(SERVE)


def test_the_server_starts_in_the_background():
    # run() would block the cell until the server dies, and nothing below it would ever happen.
    assert "Popen" in _cell(SERVE), "Sunucu arka planda başlatılmıyor"


def test_a_server_that_never_came_up_shows_its_own_log():
    """A Flask process dies for a dozen reasons and the notebook knows none of them. What it does
    know is whether /api/health answered, and what the server itself wrote."""
    serve = _cell(SERVE)
    assert "/api/health" in serve, "Sunucunun kalktığı doğrulanmıyor"
    assert "readlines()" in serve or "read()" in serve, "Düşerse sunucunun kendi log'u basılmıyor"


def test_the_address_comes_from_cloudflared():
    """Colab's own proxy forwards only GET, and this app creates, sends and deletes."""
    serve = _cell(SERVE)
    assert "cloudflared" in serve
    assert "trycloudflare" in serve, "Link cloudflared çıktısından okunmuyor"


def test_the_link_is_printed_saying_it_has_no_password():
    """There is no login, by the owner's decision, so whoever holds the link holds everything. The
    warning belongs beside the link: written anywhere else it never reaches the person copying it."""
    printed = "\n".join(
        line for line in _cell(SERVE).splitlines() if "print(" in line
    ).lower()
    assert printed, "Sunucu hücresi hiçbir şey söylemiyor"
    assert "parola" in printed, "Linkin yanında parolasız olduğu söylenmiyor"


def test_the_cell_stays_open():
    """A finished cell tells Colab there is nothing left to do here, and the runtime is called idle
    and shut down -- taking the tunnel with it."""
    serve = _cell(SERVE)
    assert "tail" in serve and "-f" in serve


def test_running_it_twice_is_safe():
    """It happened in this very session: an older server kept answering every request while a new
    one believed it had the port."""
    assert "pkill" in _cell(SERVE), "İkinci koşuda eski süreçler öldürülmüyor"


def test_the_serve_cell_refuses_to_run_before_config():
    assert 'assert "APP_DIR" in globals()' in _cell(SERVE)
