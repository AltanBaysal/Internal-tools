"""The notebook's download machinery, run rather than read.

A Colab cell never runs under pytest, so while this code lived in the notebook the suite could only
check that the right words were written down (madde 310). Here it runs. The network is the one thing
faked -- Hugging Face's downloader and the curl/aria2c call are stand-ins that drop bytes on disk --
and the files are real: small safetensors written by the test.
"""
import importlib
import json
import os
import struct
import sys
import types

import pytest

STAMP = b"L2P_bypass_model.safetensors_1755000000"

# What H3 Eros Max beta5 dropped with at 97% on 2 Ekim (madde 432), its address made long enough to
# pass 4000 characters: a message cut anywhere on its way to the console shows.
DROP = ("Data processing error: File reconstruction error: CAS Client Error: Request middleware error: "
        "error sending request for url (https://us.gcp.cdn.hf.co/xorbs/default/" + "0f" * 32
        + "?X-Xet-Signed-Range=bytes%3D0-67108863&Signature=" + "A" * 4000 + ")")


class HfHubHTTPError(OSError):
    """What huggingface_hub raises when HF answered with an error: the response rides on it, with its
    status and its body."""

    def __init__(self, message, status, body=""):
        super().__init__(message)
        self.response = types.SimpleNamespace(status_code=status, text=body)


@pytest.fixture
def downloads(monkeypatch, tmp_path):
    """The module, its staging folder moved into the test's own tmp dir. Imported here rather than at
    the top: a module that is not there yet fails each test on its own instead of the whole file."""
    module = importlib.import_module("colab.downloads")
    monkeypatch.setattr(module, "STAGE", str(tmp_path / "stage"))
    return module


@pytest.fixture(autouse=True)
def waits(monkeypatch, downloads):
    """The seconds hf_fetch waited between attempts. The clock is faked in every test, so none waits a
    real second; a test that asks how long was waited takes this by name."""
    slept = []
    monkeypatch.setattr(downloads.time, "sleep", slept.append)
    return slept


def _safetensors(tail=b""):
    """A whole, tiny safetensors file -- one tensor of eight bytes -- and whatever tail is asked for."""
    header = json.dumps({"w": {"dtype": "F32", "shape": [2], "data_offsets": [0, 8]}}).encode()
    return struct.pack("<Q", len(header)) + header + b"\0" * 8 + tail


def _hub(monkeypatch, content, *, errors=()):
    """Hugging Face's downloader, faked: the first calls raise `errors`, one each, in order; after them
    `content` lands where the real one would put the file -- under local_dir, at its path in the repo.
    Every call is remembered."""
    calls = []
    errors = list(errors)

    def hf_hub_download(repo_id, filename, *, local_dir=None, **_):
        calls.append((repo_id, filename, local_dir))
        if errors:
            raise errors.pop(0)
        path = os.path.join(local_dir, filename)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as handle:
            handle.write(content)
        return path

    monkeypatch.setitem(sys.modules, "huggingface_hub",
                        types.SimpleNamespace(hf_hub_download=hf_hub_download))
    return calls


def _transfer(monkeypatch, downloads, content, *, append=False):
    """curl and aria2c, faked: whichever command fetch builds, `content` lands in the file it names."""
    commands = []

    def run(cmd, label, cwd=None, timeout=3600):
        commands.append(cmd)
        out = cmd[cmd.index("-o") + 1]
        if cmd[0] == "aria2c":
            out = os.path.join(cmd[cmd.index("-d") + 1], out)
        with open(out, "ab" if append else "wb") as handle:
            handle.write(content)
        return ""

    monkeypatch.setattr(downloads, "run", run)
    return commands


def _speed_lines(capsys):
    return [line for line in capsys.readouterr().out.splitlines() if "MB/s" in line]


def test_a_huggingface_file_comes_down_through_hugging_face_s_own_downloader(
        downloads, monkeypatch, tmp_path):
    """hf_xet, behind hf_hub_download, pulls the file's Xet chunks straight from storage in parallel;
    the address the notebook used before went through HF's bridge, which cuts a plain download to
    8.7 MB/s on most of its servers (xet-core #821). The file lands under the name the graph asks for,
    which is not always HF's: the WAN VAE is saved as Wan2_1_VAE_fp32."""
    calls = _hub(monkeypatch, _safetensors())

    downloads.hf_fetch("Comfy-Org/Wan_2.1_ComfyUI_repackaged", "split_files/vae/wan_2.1_vae.safetensors",
                       str(tmp_path), "Wan2_1_VAE_fp32.safetensors", "Wan2.1 VAE")

    assert calls == [("Comfy-Org/Wan_2.1_ComfyUI_repackaged",
                      "split_files/vae/wan_2.1_vae.safetensors", downloads.STAGE)], \
        f"HF'nin indiricisi böyle çağrılmadı: {calls}"
    assert (tmp_path / "Wan2_1_VAE_fp32.safetensors").read_bytes() == _safetensors(), \
        "Dosya hedefine kendi adıyla konmadı"


def test_a_huggingface_file_is_cut_of_its_quantizer_stamp_before_it_is_judged(
        downloads, monkeypatch, tmp_path):
    """The int4 text encoder H3 takes from HF arrives with a line of ASCII after its last tensor
    (NOTEBOOK-STANDARD, section 3). Judged uncut it reads as too long and stops the run."""
    _hub(monkeypatch, _safetensors(tail=STAMP))

    downloads.hf_fetch("Abiray/MiniMax-H3-GGUF", "text_encoders/qwen.safetensors",
                       str(tmp_path), "qwen.safetensors", "H3 Qwen3-VL")

    assert (tmp_path / "qwen.safetensors").read_bytes() == _safetensors(), "Damga kesilmedi"


def test_a_huggingface_download_prints_where_it_came_from_and_how_fast(
        downloads, monkeypatch, tmp_path, capsys):
    """The user compares the sources by reading the console (madde 310, "ama lütfen console
    basılsın"): one line per file."""
    _hub(monkeypatch, _safetensors())

    downloads.hf_fetch("Kijai/MiniMax-H3-TAE", "vae_approx/taeh3.safetensors",
                       str(tmp_path), "taeh3.safetensors", "H3 TAE")

    lines = _speed_lines(capsys)
    assert len(lines) == 1 and "HF" in lines[0], f"Satır kaynağı ya da hızı söylemiyor: {lines}"


def test_a_file_already_in_place_is_not_downloaded_again(downloads, monkeypatch, tmp_path, capsys):
    """Run all twice in one session and the second pass costs nothing."""
    calls = _hub(monkeypatch, _safetensors())
    (tmp_path / "taeh3.safetensors").write_bytes(_safetensors())

    downloads.hf_fetch("Kijai/MiniMax-H3-TAE", "vae_approx/taeh3.safetensors",
                       str(tmp_path), "taeh3.safetensors", "H3 TAE")

    assert calls == [], "Yerinde duran dosya yeniden indirildi"
    assert "zaten var" in capsys.readouterr().out, "Konsol dosyanın yerinde olduğunu söylemedi"


def test_a_failed_huggingface_download_says_what_hugging_face_said(downloads, monkeypatch, tmp_path):
    """Never invent a cause: the error carries the downloader's own sentence, and the label says
    which of a dozen files it was."""
    _hub(monkeypatch, b"", errors=[HfHubHTTPError(
        "404 Client Error. Entry Not Found for url: https://huggingface.co/x/resolve/main/y", 404)])

    with pytest.raises(RuntimeError) as failure:
        downloads.hf_fetch("x", "y", str(tmp_path), "y", "H3 video VAE")

    assert "H3 video VAE" in str(failure.value), "Hata hangi dosya olduğunu söylemiyor"
    assert "Entry Not Found" in str(failure.value), "Hata HF'nin kendi cümlesini taşımıyor"


def test_a_corrupt_download_stops_the_run_and_stays_for_inspection(downloads, monkeypatch, tmp_path):
    """A file shorter than its own header says never reaches the model folder, and nothing is
    deleted: what came down stays where it landed (NOTEBOOK-STANDARD, section 3)."""
    _hub(monkeypatch, _safetensors()[:-4])

    with pytest.raises(RuntimeError):
        downloads.hf_fetch("Kijai/MiniMax-H3-TAE", "vae_approx/taeh3.safetensors",
                           str(tmp_path), "taeh3.safetensors", "H3 TAE")

    assert not (tmp_path / "taeh3.safetensors").exists(), "Bozuk dosya model klasörüne kondu"
    assert os.path.exists(os.path.join(downloads.STAGE, "vae_approx", "taeh3.safetensors")), \
        "Bozuk dosya silindi"


def test_a_file_with_a_floor_is_judged_by_its_size_not_as_safetensors(downloads, monkeypatch, tmp_path):
    """The upscaler and the face detector are .pth and .pt, with no safetensors header to read. The
    floor is what tells a whole file from an error page or a stub."""
    _hub(monkeypatch, b"\x80\x02" + b"\0" * 98)

    downloads.hf_fetch("Bingsu/adetailer", "face_yolov9c.pt", str(tmp_path), "face_yolov9c.pt",
                       "Yuz dedektoru", floor=50)

    assert (tmp_path / "face_yolov9c.pt").stat().st_size == 100, "Tabanlı dosya yerine konmadı"


def _eros(downloads, tmp_path):
    return downloads.hf_fetch("TenStrip/10Eros-Max", "eros.safetensors", str(tmp_path),
                              "eros.safetensors", "H3 Eros Max beta5")


def test_a_huggingface_download_that_drops_is_tried_again_and_comes_down(
        downloads, monkeypatch, tmp_path, waits):
    """H3 Eros Max beta5 dropped at 97% (madde 432, "arada oluyor"). The next attempt, thirty seconds
    later, brings the file down, and its row goes to the summary as any other's."""
    calls = _hub(monkeypatch, _safetensors(), errors=[RuntimeError(DROP)])

    row = _eros(downloads, tmp_path)

    assert len(calls) == 2, f"Düşen indirme yeniden denenmedi: {len(calls)} çağrı"
    assert waits == [30], f"Yeniden denemeden önce 30 sn beklenmedi: {waits}"
    assert (tmp_path / "eros.safetensors").read_bytes() == _safetensors(), "Dosya inmedi"
    assert row and row[0] == "H3 Eros Max beta5", f"Satır bu inişi anlatmıyor: {row}"


def test_a_dropped_attempt_prints_the_error_as_it_was_raised(downloads, monkeypatch, tmp_path, capsys):
    """Not a sentence of ours but the error itself, its type and its whole message (madde 432, "bir
    uyarı mesajıda değil hatayı yada responsu direky tpaıştır abi görelim olru"). Which file, which
    attempt and when it is tried again are facts, and stand beside it."""
    _hub(monkeypatch, _safetensors(), errors=[RuntimeError(DROP)])

    _eros(downloads, tmp_path)

    out = capsys.readouterr().out
    assert f"RuntimeError: {DROP}" in out, "Konsol hatanın kendisini kısaltmadan basmadı"
    facts = [line for line in out.splitlines() if "deneme 1/3" in line]
    assert facts and "H3 Eros Max beta5" in facts[0] and "30 sn" in facts[0], \
        f"Satır dosyayı, denemeyi ya da yeniden denenecek zamanı söylemiyor: {facts}"


BAD_GATEWAY = ("<html>\n<head><title>502 Bad Gateway</title></head>\n"
               "<body><center><h1>502 Bad Gateway</h1></center></body>\n</html>")


def test_a_dropped_attempt_prints_hugging_face_s_response_as_sent(
        downloads, monkeypatch, tmp_path, capsys):
    """When HF answered, its answer is printed under the error the way it came: the status and the
    body (madde 432)."""
    error = HfHubHTTPError("502 Server Error: Bad Gateway for url: "
                           "https://huggingface.co/TenStrip/10Eros-Max/resolve/main/eros.safetensors",
                           502, BAD_GATEWAY)
    _hub(monkeypatch, _safetensors(), errors=[error])

    _eros(downloads, tmp_path)

    out = capsys.readouterr().out
    assert f"HfHubHTTPError: {error}" in out, "Konsol hatanın kendisini basmadı"
    assert "HTTP 502" in out and BAD_GATEWAY in out, f"Konsol HF'nin cevabını basmadı:\n{out}"


class ResponseNotRead(RuntimeError):
    """What httpx raises when a streamed response's body is asked for before it was read."""


class _Unread:
    """A streamed response nobody read: its status is there, and its body raises when asked for."""
    status_code = 502

    @property
    def text(self):
        raise ResponseNotRead("Attempted to access streaming response content, without having called "
                              "`read()`.")


def test_a_body_that_cannot_be_read_does_not_hide_the_drop(downloads, monkeypatch, tmp_path, capsys,
                                                           waits):
    """Reading the body is part of printing the drop, and its own error is printed in the body's
    place: raised, it would stop the cell with the reader's error and the 502 would not be tried
    again (madde 432)."""
    error = HfHubHTTPError("502 Server Error: Bad Gateway for url: "
                           "https://huggingface.co/TenStrip/10Eros-Max/resolve/main/eros.safetensors", 502)
    error.response = _Unread()
    calls = _hub(monkeypatch, _safetensors(), errors=[error])

    _eros(downloads, tmp_path)

    out = capsys.readouterr().out
    assert len(calls) == 2 and waits == [30], \
        f"Gövdesi okunamayan 502 yeniden denenmedi: {len(calls)} çağrı, beklemeler {waits}"
    assert f"HfHubHTTPError: {error}" in out and "HTTP 502" in out, \
        f"Konsol hatayı ya da cevabın kodunu basmadı:\n{out}"
    assert "ResponseNotRead: Attempted to access streaming response content" in out, \
        f"Konsol gövdenin neden okunamadığını basmadı:\n{out}"


def test_a_download_is_given_up_after_three_attempts(downloads, monkeypatch, tmp_path, waits):
    """Three attempts in all, thirty seconds before each retry and none after the last (madde 432):
    once the last one drops there is nothing left to wait for. The error that stops the cell is that
    attempt's, as it was raised."""
    calls = _hub(monkeypatch, _safetensors(), errors=[RuntimeError(DROP) for _ in range(3)])

    with pytest.raises(RuntimeError) as failure:
        _eros(downloads, tmp_path)

    message = str(failure.value)
    assert len(calls) == 3, f"Üç kez denenmedi: {len(calls)} çağrı"
    assert waits == [30, 30], f"Denemeler arasında böyle beklenmedi: {waits}"
    assert "H3 Eros Max beta5" in message and "deneme 3/3" in message, \
        f"Hata dosyayı ya da denemeyi söylemiyor: {message[:300]}"
    assert f"RuntimeError: {DROP}" in message, "Hücreyi durduran hata hatanın kendisini taşımıyor"


def test_the_error_that_stops_the_cell_carries_hugging_face_s_response(downloads, monkeypatch, tmp_path):
    """The last attempt's answer from HF stops the cell as it came, status and body (madde 432)."""
    body = '{"error":"Internal Error - We\'re working hard to fix this as soon as possible!"}'
    _hub(monkeypatch, _safetensors(), errors=[
        HfHubHTTPError("500 Server Error: Internal Server Error for url: "
                       "https://huggingface.co/api/models/TenStrip/10Eros-Max/xet-read-token/main",
                       500, body)
        for _ in range(3)])

    with pytest.raises(RuntimeError) as failure:
        _eros(downloads, tmp_path)

    message = str(failure.value)
    assert "HTTP 500" in message and body in message, f"Hata HF'nin cevabını taşımıyor:\n{message}"


@pytest.mark.parametrize("status, body", [
    (401, '{"error":"Invalid credentials in Authorization header"}'),
    (403, '{"error":"Access to model TenStrip/10Eros-Max is restricted."}'),
    (404, '{"error":"Entry not found"}'),
])
def test_hugging_face_s_answer_about_the_file_is_not_asked_again(
        downloads, monkeypatch, tmp_path, waits, status, body):
    """401, 403 and 404 say the file is missing or not ours, and HF asked again answers the same
    (madde 432). The download stops at once, carrying the answer."""
    calls = _hub(monkeypatch, _safetensors(), errors=[HfHubHTTPError(
        f"{status} Client Error for url: https://huggingface.co/TenStrip/10Eros-Max/resolve/main/"
        f"eros.safetensors", status, body)])

    with pytest.raises(RuntimeError) as failure:
        _eros(downloads, tmp_path)

    message = str(failure.value)
    assert len(calls) == 1 and waits == [], \
        f"HF'nin {status} cevabı yeniden soruldu: {len(calls)} çağrı, beklemeler {waits}"
    assert f"HTTP {status}" in message and body in message, f"Hata HF'nin cevabını taşımıyor:\n{message}"


class LocalEntryNotFoundError(OSError):
    """What huggingface_hub raises when it could not locate the file on the Hub: a sentence of its own,
    with the error that stopped it -- and HF's response -- underneath, as its __cause__."""


def test_an_answer_under_hugging_face_s_own_sentence_is_read_and_printed_too(
        downloads, monkeypatch, tmp_path, waits):
    """huggingface_hub puts some of HF's answers under a sentence of its own, which carries no
    response. The error that stops the cell shows the whole chain, the raised one first, and HF's
    403 under it -- and the 403 is not asked again (madde 432)."""
    body = '{"error":"Access to model TenStrip/10Eros-Max is restricted."}'
    hidden = LocalEntryNotFoundError(
        "An error happened while trying to locate the file on the Hub and we cannot find the requested "
        "files in the local cache. Please check your connection and try again or make sure your "
        "Internet connection is on.")
    hidden.__cause__ = HfHubHTTPError(
        "403 Client Error for url: https://huggingface.co/TenStrip/10Eros-Max/resolve/main/"
        "eros.safetensors", 403, body)
    calls = _hub(monkeypatch, _safetensors(), errors=[hidden])

    with pytest.raises(RuntimeError) as failure:
        _eros(downloads, tmp_path)

    message = str(failure.value)
    outer, inner = f"LocalEntryNotFoundError: {hidden}", f"HfHubHTTPError: {hidden.__cause__}"
    assert outer in message and inner in message and message.index(outer) < message.index(inner), \
        f"Hata zinciri atılan hata başta olmak üzere basılmadı:\n{message}"
    assert "HTTP 403" in message and body in message, f"Hata HF'nin cevabını taşımıyor:\n{message}"
    assert len(calls) == 1 and waits == [], \
        f"Zincirdeki 403 yeniden soruldu: {len(calls)} çağrı, beklemeler {waits}"


def test_a_file_that_came_down_whole_but_bad_is_not_downloaded_again(
        downloads, monkeypatch, tmp_path, waits):
    """The download ended and the size check failed: that is the file HF gave, and asked again it
    gives the same (madde 432). It stops the run and stays where it landed."""
    calls = _hub(monkeypatch, _safetensors()[:-4])

    with pytest.raises(RuntimeError):
        _eros(downloads, tmp_path)

    assert len(calls) == 1 and waits == [], \
        f"Bozuk inen dosya yeniden indirildi: {len(calls)} çağrı, beklemeler {waits}"


def test_an_addressed_download_prints_its_server_and_speed(downloads, monkeypatch, tmp_path, capsys):
    """Civitai's files still come down by address, and their line reads like HF's -- the first run is
    where the two speeds sit side by side."""
    _transfer(monkeypatch, downloads, _safetensors())

    downloads.fetch("https://civitai.red/api/download/models/3314686", str(tmp_path),
                    "dasiwa.safetensors", "DaSiWa H3", parallel=False, headers="Cookie: x=y")

    lines = _speed_lines(capsys)
    assert len(lines) == 1 and "civitai.red" in lines[0], \
        f"Satır sunucuyu ya da hızı söylemiyor: {lines}"


def test_an_addressed_download_is_cut_of_its_stamp_too(downloads, monkeypatch, tmp_path):
    _transfer(monkeypatch, downloads, _safetensors(tail=STAMP))

    downloads.fetch("https://civitai.red/api/download/models/1", str(tmp_path), "m.safetensors",
                    "M", parallel=False)

    assert (tmp_path / "m.safetensors").read_bytes() == _safetensors(), "Damga kesilmedi"


def test_a_resumed_download_counts_only_what_came_down_this_time(
        downloads, monkeypatch, tmp_path, capsys):
    """A .part left by a dropped session is continued, not restarted. The bytes it already held did
    not come down now, and counting them would overstate the speed."""
    (tmp_path / "sam.pth.part").write_bytes(b"\0" * 100)
    _transfer(monkeypatch, downloads, b"\0" * 900, append=True)

    downloads.fetch("https://dl.fbaipublicfiles.com/segment_anything/sam.pth", str(tmp_path),
                    "sam.pth", "SAM", parallel=True, floor=500)

    lines = _speed_lines(capsys)
    assert len(lines) == 1 and "900.0B" in lines[0], f"Satır bu koşuda ineni saymıyor: {lines}"


def test_a_gated_file_goes_through_curl_so_the_cookie_stays_behind(downloads, monkeypatch, tmp_path):
    """Civitai redirects a download to its store, and the store answers 403 when the login cookie
    travels with the request. aria2c forwards the cookie across the redirect; curl drops it when the
    host changes. Learnt in a run, not guessable from the code (NOTEBOOK-STANDARD, section 4)."""
    commands = _transfer(monkeypatch, downloads, _safetensors())

    downloads.fetch("https://civitai.red/api/download/models/1", str(tmp_path), "m.safetensors",
                    "M", parallel=False, headers="Cookie: __Secure-civ-token=t")

    assert commands[0][0] == "curl", f"Kapılı dosya curl ile inmiyor: {commands[0][0]}"
    assert commands[0][commands[0].index("-H") + 1] == "Cookie: __Secure-civ-token=t", \
        "Çerez isteğe konmadı"


def test_civitai_is_asked_on_its_red_host(downloads):
    """civitai.red is same-origin with the login cookie; .com is cross-domain and answers with the
    login page (NOTEBOOK-STANDARD, section 4)."""
    assert downloads.civitai_url(3314686) == "https://civitai.red/api/download/models/3314686"


MIRROR = "Test468735/queen-editor-models"
COOKIE = "c" * 420


def _mirror(monkeypatch, held, *, upload_error=None):
    """Hugging Face with a mirror repo holding `held` ({path in repo: bytes}). A path it does not hold
    is answered the way HF answers: a 404, and a sentence naming it. Uploads are remembered, or
    refused with `upload_error`."""
    uploads = []

    def hf_hub_download(repo_id, filename, *, local_dir=None, **_):
        if filename not in held:
            raise HfHubHTTPError(f"404 Client Error. Entry Not Found for url: "
                                 f"https://huggingface.co/{repo_id}/resolve/main/{filename}", 404)
        path = os.path.join(local_dir, filename)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as handle:
            handle.write(held[filename])
        return path

    class HfApi:
        def upload_file(self, *, path_or_fileobj, path_in_repo, repo_id, **_):
            if upload_error:
                raise upload_error
            uploads.append((path_or_fileobj, path_in_repo, repo_id))

    monkeypatch.setitem(sys.modules, "huggingface_hub",
                        types.SimpleNamespace(hf_hub_download=hf_hub_download, HfApi=HfApi))
    return uploads


def _probe(monkeypatch, downloads, commands):
    """The 1 KB probe, faked: it remembers how many transfers had run when it was asked."""
    asked = []
    monkeypatch.setattr(downloads, "civitai_probe",
                        lambda version_id, label, cookie: asked.append(len(commands)))
    return asked


def test_a_civitai_file_in_the_mirror_comes_from_hugging_face(downloads, monkeypatch, tmp_path):
    """The mirror is the fast road: once a file is there, Civitai is never asked -- and neither is the
    cookie, so a run whose files are all mirrored opens without one (madde 311)."""
    uploads = _mirror(monkeypatch, {"3314686/m.safetensors": _safetensors()})
    commands = _transfer(monkeypatch, downloads, b"")
    asked = _probe(monkeypatch, downloads, commands)

    downloads.civitai_fetch(MIRROR, 3314686, str(tmp_path), "m.safetensors", "DaSiWa H3", "")

    assert (tmp_path / "m.safetensors").read_bytes() == _safetensors(), "Aynadaki dosya inmedi"
    assert commands == [] and asked == [], "Aynada duran dosya için Civitai'ye gidildi"
    assert uploads == [], "Aynadan inen dosya aynaya yeniden yüklendi"


def test_a_civitai_file_missing_from_the_mirror_comes_from_civitai_and_says_why(
        downloads, monkeypatch, tmp_path, capsys):
    """Asked for what it does not hold, the mirror answers with its own sentence and the console
    carries it: the user reads why this file took the slow road (madde 311, "yoksa console'a
    bassın")."""
    _mirror(monkeypatch, {})
    commands = _transfer(monkeypatch, downloads, _safetensors())
    _probe(monkeypatch, downloads, commands)

    downloads.civitai_fetch(MIRROR, 3314686, str(tmp_path), "m.safetensors", "DaSiWa H3", COOKIE)

    assert (tmp_path / "m.safetensors").read_bytes() == _safetensors(), "Dosya Civitai'den inmedi"
    assert "Entry Not Found" in capsys.readouterr().out, "Konsol HF'nin cümlesini basmadı"
    assert commands[0][0] == "curl", f"Civitai dosyası curl ile inmedi: {commands[0][0]}"
    assert f"__Secure-civ-token={COOKIE}" in commands[0][commands[0].index("-H") + 1], \
        "Çerez isteğe konmadı"


def test_a_file_that_came_from_civitai_goes_up_to_the_mirror(downloads, monkeypatch, tmp_path, capsys):
    """The first run pays for the slow road once: what came from Civitai goes up to the mirror under
    its Civitai version and name, and the next run takes it from Hugging Face."""
    uploads = _mirror(monkeypatch, {})
    commands = _transfer(monkeypatch, downloads, _safetensors())
    _probe(monkeypatch, downloads, commands)

    downloads.civitai_fetch(MIRROR, 3314686, str(tmp_path), "m.safetensors", "DaSiWa H3", COOKIE)

    assert uploads == [(str(tmp_path / "m.safetensors"), "3314686/m.safetensors", MIRROR)], \
        f"Aynaya böyle yüklenmedi: {uploads}"
    assert "yüklendi" in capsys.readouterr().out, "Konsol yüklemeyi söylemedi"


def test_a_failed_upload_warns_and_keeps_the_file(downloads, monkeypatch, tmp_path, capsys):
    """The file is already down and usable; a refused upload is worth a line, not the run. The next
    run tries again."""
    _mirror(monkeypatch, {}, upload_error=OSError("403 Forbidden: this token has no write access"))
    commands = _transfer(monkeypatch, downloads, _safetensors())
    _probe(monkeypatch, downloads, commands)

    downloads.civitai_fetch(MIRROR, 3314686, str(tmp_path), "m.safetensors", "DaSiWa H3", COOKIE)

    assert (tmp_path / "m.safetensors").exists(), "Yüklenemeyen dosya yerinde değil"
    assert "403 Forbidden" in capsys.readouterr().out, "Konsol HF'nin cümlesini basmadı"


def test_a_fallback_without_a_cookie_stops_before_civitai(downloads, monkeypatch, tmp_path):
    """The cookie is asked for only when a file has to come from Civitai. Missing then, the run stops
    before anything is asked of Civitai, and says which file needed it."""
    _mirror(monkeypatch, {})
    commands = _transfer(monkeypatch, downloads, _safetensors())
    asked = _probe(monkeypatch, downloads, commands)

    with pytest.raises(RuntimeError) as failure:
        downloads.civitai_fetch(MIRROR, 3314686, str(tmp_path), "m.safetensors", "DaSiWa H3", "")

    assert "CIVITAI_COOKIE" in str(failure.value) and "DaSiWa H3" in str(failure.value), \
        f"Cümle eksik olanı söylemiyor: {failure.value}"
    assert commands == [] and asked == [], "Çerezsiz Civitai'ye gidildi"


def test_a_fallback_is_probed_before_it_comes_down(downloads, monkeypatch, tmp_path):
    """A dead cookie is heard from a 1 KB probe that prints Civitai's own answer, before anything
    heavy starts."""
    _mirror(monkeypatch, {})
    commands = _transfer(monkeypatch, downloads, _safetensors())
    asked = _probe(monkeypatch, downloads, commands)

    downloads.civitai_fetch(MIRROR, 3314686, str(tmp_path), "m.safetensors", "DaSiWa H3", COOKIE)

    assert asked == [0], f"Yoklama inmeden önce yapılmadı: {asked}"


def test_a_file_missing_from_the_mirror_goes_to_civitai_without_waiting(
        downloads, monkeypatch, tmp_path, capsys, waits):
    """The mirror's 404 is how civitai_fetch learns a file is not there (madde 311), and asked again
    the mirror answers the same: Civitai is next at once (madde 432). The console carries the
    mirror's answer as it came, and a body that came empty is said to be empty, not left blank."""
    _mirror(monkeypatch, {})
    commands = _transfer(monkeypatch, downloads, _safetensors())
    _probe(monkeypatch, downloads, commands)

    downloads.civitai_fetch(MIRROR, 3314686, str(tmp_path), "m.safetensors", "DaSiWa H3", COOKIE)

    out = capsys.readouterr().out
    assert waits == [], f"Aynada olmayan dosya için beklendi: {waits}"
    assert "HTTP 404" in out and "(boş gövde)" in out, f"Konsol aynanın cevabını basmadı:\n{out}"


def test_hugging_face_s_downloader_is_taken_with_high_performance_left_off(
        downloads, monkeypatch, tmp_path):
    """High-performance mode had HF's chunk server answer 429 on its first run, and the run died;
    with it off, two full runs never saw one (madde 316). hf_fetch leaves the switch to the
    environment, where a fresh Colab machine has nothing -- it comes back with 313, from the
    backlog, once the 429 is solved."""
    monkeypatch.setenv("HF_XET_HIGH_PERFORMANCE", "0")
    _hub(monkeypatch, _safetensors())

    downloads.hf_fetch("Kijai/MiniMax-H3-TAE", "vae_approx/taeh3.safetensors",
                       str(tmp_path), "taeh3.safetensors", "H3 TAE")

    assert os.environ["HF_XET_HIGH_PERFORMANCE"] == "0", \
        "hf_fetch HF'nin yüksek hız ayarını açtı"


def test_a_download_hands_back_its_row_for_the_summary(downloads, monkeypatch, tmp_path):
    """The models cell collects one row per file that came down and ends with a table of them
    (madde 312): the label, the bytes that came down and the seconds they took."""
    _hub(monkeypatch, _safetensors())

    row = downloads.hf_fetch("Kijai/MiniMax-H3-TAE", "vae_approx/taeh3.safetensors",
                             str(tmp_path), "taeh3.safetensors", "H3 TAE")

    assert row and row[:2] == ("H3 TAE", len(_safetensors())), f"Satır bu inişi anlatmıyor: {row}"
    assert row[2] > 0, f"Satırda süre yok: {row}"


def test_a_file_already_in_place_stays_out_of_the_summary(downloads, monkeypatch, tmp_path, capsys):
    """The table is this run's downloads: a file that was already there came down in an earlier one."""
    _hub(monkeypatch, _safetensors())
    _transfer(monkeypatch, downloads, b"")
    (tmp_path / "old.safetensors").write_bytes(_safetensors())
    (tmp_path / "sam.pth").write_bytes(b"\0" * 1000)

    rows = [downloads.hf_fetch("r/old", "old.safetensors", str(tmp_path), "old.safetensors", "Eski"),
            downloads.fetch("https://dl.fbaipublicfiles.com/segment_anything/sam.pth", str(tmp_path),
                            "sam.pth", "SAM", parallel=True, floor=500),
            downloads.hf_fetch("r/new", "new.safetensors", str(tmp_path), "new.safetensors", "Yeni")]
    capsys.readouterr()
    downloads.download_summary(rows)

    table = capsys.readouterr().out
    assert "Yeni" in table, f"Tabloda inen dosya yok:\n{table}"
    assert "Eski" not in table and "SAM" not in table, f"Tabloda yerinde duran dosya var:\n{table}"


def test_a_resumed_download_s_row_counts_only_what_came_down_this_time(downloads, monkeypatch, tmp_path):
    """The row says what the line says: bytes the .part already held did not come down in this run."""
    (tmp_path / "sam.pth.part").write_bytes(b"\0" * 100)
    _transfer(monkeypatch, downloads, b"\0" * 900, append=True)

    row = downloads.fetch("https://dl.fbaipublicfiles.com/segment_anything/sam.pth", str(tmp_path),
                          "sam.pth", "SAM", parallel=True, floor=500)

    assert row and row[:2] == ("SAM", 900), f"Satır bu koşuda ineni saymıyor: {row}"


def test_a_civitai_file_hands_back_the_row_of_the_road_it_took(downloads, monkeypatch, tmp_path):
    """From the mirror or from Civitai, the file came down and is counted. The upload after a Civitai
    download has its own line and is not part of the row."""
    _mirror(monkeypatch, {"3314686/a.safetensors": _safetensors()})
    commands = _transfer(monkeypatch, downloads, _safetensors())
    _probe(monkeypatch, downloads, commands)

    mirrored = downloads.civitai_fetch(MIRROR, 3314686, str(tmp_path), "a.safetensors", "Aynadan", "")
    fell_back = downloads.civitai_fetch(MIRROR, 3228867, str(tmp_path), "b.safetensors", "Civitai'den",
                                        COOKIE)

    assert mirrored and mirrored[:2] == ("Aynadan", len(_safetensors())), \
        f"Aynadan inen dosyanın satırı yok: {mirrored}"
    assert fell_back and fell_back[:2] == ("Civitai'den", len(_safetensors())), \
        f"Civitai'den inen dosyanın satırı yok: {fell_back}"


def test_the_summary_lists_each_download_and_a_total(downloads, capsys):
    """One line per file that came down, and a Toplam line under them: the whole download's size, its
    seconds and the average speed -- "ortalama indirme hızını yazalım" (madde 312). The per-file lines
    say the same, scattered between the progress bars; the table is where they are read together."""
    downloads.download_summary([("Kısa", 60 * 2**20, 20.0), None, ("Uzun", 2 * 2**30, 100.0)])

    lines = capsys.readouterr().out.splitlines()
    expected = [("Kısa", "60.0MB", "20 sn", "3.0 MB/s"),
                ("Uzun", "2.0GB", "1 dk 40 sn", "20.5 MB/s"),
                ("Toplam", "2.1GB", "2 dk 0 sn", "17.6 MB/s")]
    found = [next((i for i, line in enumerate(lines) if all(part in line for part in row)), None)
             for row in expected]

    assert any("İndirme özeti" in line for line in lines), f"Tablonun başlığı yok: {lines}"
    assert None not in found and found == sorted(found), "Tablo böyle değil:\n" + "\n".join(lines)


def test_a_run_with_nothing_downloaded_says_so(downloads, capsys):
    """Run all a second time in one session and every file is already there: a Toplam of nothing would
    read like a download that took no time."""
    downloads.download_summary([None, None])

    out = capsys.readouterr().out
    assert "inen dosya yok" in out and "Toplam" not in out, f"Özet boş koşuyu söylemiyor:\n{out}"


def test_a_file_whose_mirror_is_off_comes_from_civitai_even_when_the_mirror_holds_it(
        downloads, monkeypatch, tmp_path):
    """A file on trial has no business in the mirror (madde 327, "kullanamayacağımız bir şeyi
    mirrorlamak mantıklı olmaz"). Switched off, the mirror is not asked at all: the list decides,
    not what the mirror happens to hold. The file still comes down and is counted."""
    monkeypatch.setattr(downloads, "MIRRORLESS", {"mystic.safetensors"})
    _mirror(monkeypatch, {"3266628/mystic.safetensors": _safetensors()})
    commands = _transfer(monkeypatch, downloads, _safetensors())
    _probe(monkeypatch, downloads, commands)

    row = downloads.civitai_fetch(MIRROR, 3266628, str(tmp_path), "mystic.safetensors", "Mystic XXX",
                                  COOKIE)

    assert [cmd[0] for cmd in commands] == ["curl"], f"Dosya Civitai'den inmedi: {commands}"
    assert f"__Secure-civ-token={COOKIE}" in commands[0][commands[0].index("-H") + 1], \
        "Çerez isteğe konmadı"
    assert row and row[:2] == ("Mystic XXX", len(_safetensors())), f"Satır bu inişi anlatmıyor: {row}"


def test_a_file_whose_mirror_is_off_is_not_uploaded_to_it(downloads, monkeypatch, tmp_path):
    """What came from Civitai goes up to the mirror so the next run is fast (madde 311) -- except a
    file whose mirror is off: the point of the switch is that it never lands there."""
    monkeypatch.setattr(downloads, "MIRRORLESS", {"mystic.safetensors"})
    uploads = _mirror(monkeypatch, {})
    commands = _transfer(monkeypatch, downloads, _safetensors())
    _probe(monkeypatch, downloads, commands)

    downloads.civitai_fetch(MIRROR, 3266628, str(tmp_path), "mystic.safetensors", "Mystic XXX", COOKIE)

    assert uploads == [], f"Aynası kapalı dosya aynaya yüklendi: {uploads}"


def test_a_file_whose_mirror_is_off_says_so_on_the_console(downloads, monkeypatch, tmp_path, capsys):
    """The user reads the setup's output to see which road each file took: this one says it came
    down without the mirror, and nothing on the console says the mirror was asked."""
    monkeypatch.setattr(downloads, "MIRRORLESS", {"mystic.safetensors"})
    _mirror(monkeypatch, {})
    commands = _transfer(monkeypatch, downloads, _safetensors())
    _probe(monkeypatch, downloads, commands)

    downloads.civitai_fetch(MIRROR, 3266628, str(tmp_path), "mystic.safetensors", "Mystic XXX", COOKIE)

    out = capsys.readouterr().out
    assert any("Mystic XXX" in line and "aynasız" in line for line in out.splitlines()), \
        f"Konsol dosyanın aynasız indiğini söylemedi:\n{out}"
    assert "Entry Not Found" not in out, f"Aynası kapalı dosya için aynaya soruldu:\n{out}"


def test_a_file_whose_mirror_is_off_stops_without_a_cookie_before_civitai(
        downloads, monkeypatch, tmp_path):
    """With its mirror off the file can only come from Civitai, so the cookie is needed, as for any
    fallback (madde 311). The sentence names what is missing -- and not the mirror, which was never
    asked: a cause that did not happen is not written."""
    monkeypatch.setattr(downloads, "MIRRORLESS", {"mystic.safetensors"})
    _mirror(monkeypatch, {})
    commands = _transfer(monkeypatch, downloads, _safetensors())
    asked = _probe(monkeypatch, downloads, commands)

    with pytest.raises(RuntimeError) as failure:
        downloads.civitai_fetch(MIRROR, 3266628, str(tmp_path), "mystic.safetensors", "Mystic XXX", "")

    message = str(failure.value)
    assert "CIVITAI_COOKIE" in message and "Mystic XXX" in message, \
        f"Cümle eksik olanı söylemiyor: {message}"
    assert "aynada yok" not in message, f"Cümle aynaya sorulmuş gibi konuşuyor: {message}"
    assert commands == [] and asked == [], "Çerezsiz Civitai'ye gidildi"


def test_turning_one_file_s_mirror_off_leaves_the_others_on_it(downloads, monkeypatch, tmp_path):
    """The switch is per file (madde 327): turning one file's mirror off leaves every other Civitai
    file on the fast road."""
    monkeypatch.setattr(downloads, "MIRRORLESS", {"mystic.safetensors"})
    _mirror(monkeypatch, {"3314686/m.safetensors": _safetensors()})
    commands = _transfer(monkeypatch, downloads, b"")
    asked = _probe(monkeypatch, downloads, commands)

    downloads.civitai_fetch(MIRROR, 3314686, str(tmp_path), "m.safetensors", "DaSiWa H3", "")

    assert (tmp_path / "m.safetensors").read_bytes() == _safetensors(), "Aynadaki dosya inmedi"
    assert commands == [] and asked == [], "Aynası açık dosya için Civitai'ye gidildi"


TOKEN = "hf_" + "t" * 34


class SecretNotFoundError(Exception):
    """What Colab's userdata.get raises for a secret the vault does not hold."""


def test_the_hf_token_is_read_into_the_environment_and_never_printed(downloads, monkeypatch, capsys):
    """Madde 437: the notebook reads the token itself, before anything downloads -- trimmed, as the
    paste carries the newline."""
    monkeypatch.delenv("HF_TOKEN", raising=False)
    asked = []

    downloads.use_hf_token(lambda name: asked.append(name) or f"{TOKEN}\n")

    out = capsys.readouterr().out
    assert asked == ["HF_TOKEN"], f"Kasadan böyle okunmadı: {asked}"
    assert os.environ.get("HF_TOKEN") == TOKEN, "Token ortama kırpılarak konmadı"
    assert "HF_TOKEN okundu" in out, f"Konsol token'ın okunduğunu söylemedi:\n{out}"
    assert TOKEN not in out, "Token konsola basıldı"


def test_a_token_that_cannot_be_read_says_what_the_read_raised(downloads, monkeypatch, capsys):
    """Not silence and not a guessed cause: the read's own error, and what the run does without the
    token. A token left in the environment by an earlier run in the same kernel goes, so the line
    saying the run goes without one is true."""
    monkeypatch.setenv("HF_TOKEN", "hf_old")

    def read(name):
        raise SecretNotFoundError("Secret HF_TOKEN does not exist.")

    downloads.use_hf_token(read)

    out = capsys.readouterr().out
    assert "HF_TOKEN okunamadı — SecretNotFoundError: Secret HF_TOKEN does not exist." in out, \
        f"Konsol okumanın attığı hatayı basmadı:\n{out}"
    assert "token'sız" in out, f"Konsol token'sız gidileceğini söylemedi:\n{out}"
    assert "HF_TOKEN" not in os.environ, "Önceki koşunun token'ı ortamda kaldı"


@pytest.mark.parametrize("value", ["", "  \n", None])
def test_an_empty_token_is_said_to_be_empty(downloads, monkeypatch, capsys, value):
    monkeypatch.setenv("HF_TOKEN", "hf_old")

    downloads.use_hf_token(lambda name: value)

    out = capsys.readouterr().out
    assert "HF_TOKEN boş" in out and "token'sız" in out, f"Konsol token'ın boş olduğunu söylemedi:\n{out}"
    assert "HF_TOKEN" not in os.environ, "Boş token'da ortamda token kaldı"


def _handed(monkeypatch, owner, name):
    """The fake `owner.name` -- one _hub or _mirror put in place -- wrapped to remember the token each
    call was handed, and otherwise left to do what it does."""
    tokens = []
    fake = getattr(owner, name)

    def recording(*args, **kwargs):
        tokens.append(kwargs.get("token", "verilmedi"))
        return fake(*args, **kwargs)

    monkeypatch.setattr(owner, name, recording)
    return tokens


@pytest.mark.parametrize("env, handed", [(TOKEN, TOKEN), (None, False)])
def test_a_huggingface_download_hands_its_token_over_outright(downloads, monkeypatch, tmp_path,
                                                              env, handed):
    """The token in the environment, or False -- huggingface_hub's word for none -- so it looks for
    no token of its own (madde 437, _token)."""
    if env:
        monkeypatch.setenv("HF_TOKEN", env)
    else:
        monkeypatch.delenv("HF_TOKEN", raising=False)
    _hub(monkeypatch, _safetensors())
    tokens = _handed(monkeypatch, sys.modules["huggingface_hub"], "hf_hub_download")

    _eros(downloads, tmp_path)

    assert tokens == [handed], f"İndirmeye token böyle verildi: {tokens}"


@pytest.mark.parametrize("env, handed", [(TOKEN, TOKEN), (None, False)])
def test_an_upload_to_the_mirror_hands_its_token_over_outright(downloads, monkeypatch, tmp_path,
                                                               env, handed):
    """The upload takes the token the way the download does."""
    if env:
        monkeypatch.setenv("HF_TOKEN", env)
    else:
        monkeypatch.delenv("HF_TOKEN", raising=False)
    _mirror(monkeypatch, {})
    tokens = _handed(monkeypatch, sys.modules["huggingface_hub"].HfApi, "upload_file")
    commands = _transfer(monkeypatch, downloads, _safetensors())
    _probe(monkeypatch, downloads, commands)

    downloads.civitai_fetch(MIRROR, 3314686, str(tmp_path), "m.safetensors", "DaSiWa H3", COOKIE)

    assert tokens == [handed], f"Yüklemeye token böyle verildi: {tokens}"


def test_mystic_xxx_is_kept_out_of_the_mirror(downloads):
    """Madde 328, the list's first entry: the lora is on trial ("şimdilik hugging face gitmesin, önce
    test edeyim"). What the list does is asked by 327's tests above; this asks that the file is on it,
    under the name the notebook downloads it by."""
    assert "MysticXXX_MMH3-V4.safetensors" in downloads.MIRRORLESS, \
        f"Mystic XXX aynasız listede değil: {downloads.MIRRORLESS}"


# The models cell's run around the downloads: hf_xet, the disk, the two lists, the folders.

def test_hf_xet_is_installed_for_hugging_face_s_downloader(downloads, monkeypatch):
    """Without hf_xet, huggingface_hub goes back to HF's bridge with nothing but a log line, and the
    bridge cuts a plain download to 8.7 MB/s (xet-core #821)."""
    commands = []
    monkeypatch.setattr(downloads, "run", lambda cmd, label, cwd=None, timeout=3600:
                        commands.append(cmd))

    downloads.install_hf_xet()

    assert commands == [["pip", "install", "-q", "-U", "hf_xet"]], f"hf_xet böyle kurulmadı: {commands}"


GIB = 1024 ** 3
# Photo and sound ticked, video not: 10 + 9 GiB, and 5 GiB of headroom.
SIZES = [(True, 10, "fotoğraf"), (False, 37, "video (H3)"), (True, 9, "ses")]


def _free(monkeypatch, downloads, free):
    asked = []
    monkeypatch.setattr(downloads.shutil, "disk_usage",
                        lambda path: asked.append(path) or types.SimpleNamespace(free=free))
    return asked


def test_the_disk_check_says_what_was_chosen_and_what_is_free(downloads, monkeypatch, capsys):
    asked = _free(monkeypatch, downloads, 30 * GIB)

    downloads.check_disk(SIZES)

    assert asked == ["/content"], f"Disk böyle ölçülmedi: {asked}"
    assert "Seçim: fotoğraf, ses — ~19 GiB | Diskte boş: 30.0 GiB" in capsys.readouterr().out, \
        "Konsol seçimi ve boş yeri söylemedi"


def test_a_disk_with_room_for_the_headroom_too_lets_the_run_go_on(downloads, monkeypatch):
    _free(monkeypatch, downloads, 24 * GIB)

    downloads.check_disk(SIZES)


def test_a_disk_short_of_the_headroom_stops_the_run_before_anything_downloads(downloads,
                                                                              monkeypatch):
    """All three together are ~54 GiB. Finding out the disk was too small halfway through leaves
    half-written files and no explanation."""
    _free(monkeypatch, downloads, 24 * GIB - 1)

    with pytest.raises(RuntimeError) as failure:
        downloads.check_disk(SIZES)

    assert str(failure.value).startswith(
        "❌ Disk yetmiyor: ~19 GiB model + 5 GiB pay gerekiyor, 24.0 GiB boş."), \
        f"Hata böyle: {failure.value}"


def test_the_chosen_files_come_down_huggingface_first_then_civitai(downloads, monkeypatch,
                                                                   tmp_path):
    """Each file through its own fetcher, with the mirror and the cookie for the Civitai ones, and
    every row handed back in order for the table."""
    calls = []

    def hf_fetch(repo, path, target_dir, filename, label, *, floor=None):
        calls.append(("hf", repo, path, target_dir, filename, floor))
        return label, 1, 1.0

    def civitai_fetch(mirror, version_id, target_dir, filename, label, cookie):
        calls.append(("civitai", mirror, version_id, target_dir, filename, cookie))
        return None

    monkeypatch.setattr(downloads, "hf_fetch", hf_fetch)
    monkeypatch.setattr(downloads, "civitai_fetch", civitai_fetch)
    upsc, lora = str(tmp_path / "upscale_models"), str(tmp_path / "loras")

    rows = downloads.download_models(
        [("FacehugmanIII/4x_foolhardy_Remacri", "4x.pth", upsc, "4x.pth", "Remacri", 50_000_000)],
        [(1552087, lora, "USNR.safetensors", "USNR")], MIRROR, COOKIE)

    assert calls == [
        ("hf", "FacehugmanIII/4x_foolhardy_Remacri", "4x.pth", upsc, "4x.pth", 50_000_000),
        ("civitai", MIRROR, 1552087, lora, "USNR.safetensors", COOKIE)], \
        f"Dosyalar böyle inmedi: {calls}"
    assert rows == [("Remacri", 1, 1.0), None], f"Satırlar böyle döndü: {rows}"


def test_a_huggingface_file_makes_the_folder_it_lands_in(downloads, monkeypatch, tmp_path):
    """A folder is made as its first file comes down, so an unticked group's folders are not made
    at all."""
    _hub(monkeypatch, _safetensors())
    folder = tmp_path / "models" / "vae" / "MiniMaxH3"

    downloads.hf_fetch("Kijai/MiniMax-H3-TAE", "taeh3.safetensors", str(folder), "taeh3.safetensors",
                       "H3 TAE")

    assert (folder / "taeh3.safetensors").read_bytes() == _safetensors(), "Dosya klasörüne inmedi"


def test_an_addressed_file_makes_the_folder_its_part_is_written_in(downloads, monkeypatch, tmp_path):
    """curl writes the .part straight into the folder, so it has to be there first."""
    _transfer(monkeypatch, downloads, _safetensors())
    folder = tmp_path / "models" / "loras"

    downloads.fetch("https://civitai.red/api/download/models/1", str(folder), "m.safetensors", "M",
                    parallel=False)

    assert (folder / "m.safetensors").read_bytes() == _safetensors(), "Dosya klasörüne inmedi"


def test_the_folders_of_the_chosen_groups_are_listed_with_their_files(downloads, tmp_path, capsys):
    """Subfolders too: H3's files sit under MiniMaxH3/."""
    diff, mmau = tmp_path / "diffusion_models", tmp_path / "mmaudio"
    (diff / "MiniMaxH3").mkdir(parents=True)
    (diff / "MiniMaxH3" / "eros.safetensors").write_bytes(b"\0" * 2048)
    mmau.mkdir()
    (mmau / "nsfw.safetensors").write_bytes(b"\0" * 8)

    downloads.show_folders([(True, "diffusion_models", str(diff), "**/*.safetensors"),
                            (False, "mmaudio", str(mmau), "*.safetensors")])

    out = capsys.readouterr().out
    eros = os.path.join("MiniMaxH3", "eros.safetensors")
    assert out == f"\n📂 diffusion_models/\n   2.0KB  {eros}\n", f"Klasörler böyle listelendi:\n{out}"
