# Madde 310 — HF indiricisi, test turunun planı

> **Koşum:** bu oturumda, satır satır. Alt ajan yok *(CLAUDE.md, Gotchas)*.

**Hedef:** İndirme kodunun modülde koşularak sınandığı testler ve defterle modülün dikişini tutan
testler — kırmızı.

**Yaklaşım:** Modül testleri ağı sahteler: `huggingface_hub` `sys.modules`'a sahte bir modülle,
`curl`/`aria2c` de `downloads.run`'ın yerine geçen bir sahteyle. Dosyalar gerçek, test içinde
yazılıyor. Defter testleri import satırlarını okuyor ve modülü gerçekten import ediyor.

**Araçlar:** pytest (`monkeypatch`, `tmp_path`, `capsys`).

**Spec:** [m310 test turu](../specs/2026-09-23-queen-editor-m310-hf-indirici-testler-design.md)

## Her yere geçerli kurallar

- Test adları ve docstring'ler **İngilizce**, assert mesajları **Türkçe** *(CODE-STANDARD, Language)*.
- Testler **dört satırla** koşulur, [CLAUDE.md](../../../CLAUDE.md)'de yazıldığı gibi.
- `skip` / `xfail` yok. Bu turda defter ve kaynak kod değişmiyor.

---

## Görev 1: Modül testleri

**Dosyalar:** Oluştur: `queen-editor/backend/tests/test_colab_downloads.py`

**Arayüzler — uygulama turunun vereceği:**
- `colab/downloads.py`: `STAGE` *(str)*, `check_safetensors`, `check_binary`,
  `strip_unreferenced_tail`, `fetch(url, target_dir, filename, label, *, parallel, headers=None,
  floor=None)`, `hf_fetch(repo, path, target_dir, filename, label, *, floor=None)`,
  `civitai_url(version_id)`, `cookie_header(cookie)`, `civitai_probe(version_id, label, cookie)`.
- `downloads` `run`'ı `colab.console`'dan kendi ad alanına alıyor; test onu orada değiştiriyor.
- `hf_fetch`, `hf_hub_download(repo, path, local_dir=STAGE)` çağırıyor ve `huggingface_hub`'ı
  fonksiyonun içinde import ediyor.

- [ ] **Adım 1: Dosyanın tamamı.**

```python
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


@pytest.fixture
def downloads(monkeypatch, tmp_path):
    """The module, its staging folder moved into the test's own tmp dir. Imported here rather than at
    the top: a module that is not there yet fails each test on its own instead of the whole file."""
    module = importlib.import_module("colab.downloads")
    monkeypatch.setattr(module, "STAGE", str(tmp_path / "stage"))
    return module


def _safetensors(tail=b""):
    """A whole, tiny safetensors file -- one tensor of eight bytes -- and whatever tail is asked for."""
    header = json.dumps({"w": {"dtype": "F32", "shape": [2], "data_offsets": [0, 8]}}).encode()
    return struct.pack("<Q", len(header)) + header + b"\0" * 8 + tail


def _hub(monkeypatch, content):
    """Hugging Face's downloader, faked: `content` lands where the real one would put the file -- under
    local_dir, at its path in the repo -- and every call is remembered."""
    calls = []

    def hf_hub_download(repo_id, filename, *, local_dir=None, **_):
        calls.append((repo_id, filename, local_dir))
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
    def hf_hub_download(repo_id, filename, **_):
        raise OSError("404 Client Error. Entry Not Found for url: https://huggingface.co/x/resolve/main/y")

    monkeypatch.setitem(sys.modules, "huggingface_hub",
                        types.SimpleNamespace(hf_hub_download=hf_hub_download))

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
```

## Görev 2: Defterle kodun dikişi

**Dosyalar:** Değiştir: `queen-editor/backend/tests/test_notebook_installs_the_producer_groups.py`

- [ ] **Adım 1: Sil** — `_between`, `test_the_gated_files_are_fetched_the_way_that_works`,
  `test_the_quantizer_stamp_is_cut_before_a_file_is_judged`,
  `test_huggingface_files_come_down_through_hugging_face_s_own_downloader`,
  `test_the_quantizer_stamp_is_cut_before_a_huggingface_file_is_judged`,
  `test_every_download_prints_where_it_came_from_and_how_fast`. Yerlerini alanlar spec'in tablosunda.

- [ ] **Adım 2: Dosyanın docstring'ine bir paragraf** ve `import importlib`:

```python
The download machinery left the notebook for colab/ in madde 310 and is run in
test_colab_downloads.py. What stays here is the seam: the notebook imports names the module gives,
finds the module in its clone, and defines none of it again.
```

- [ ] **Adım 3: Yardımcı ve altı test**, `_cell`'in altına ve dosyanın sonuna:

```python
def _imports_from_code():
    """(module, names) for every line the notebook imports its own code with."""
    return [(module, [name.strip() for name in names.split(",")])
            for module, names in re.findall(r"^from (colab\.\w+) import ([\w, ]+)$", _source(), re.M)]


def test_every_name_the_notebook_imports_from_its_code_exists():
    """The notebook cannot run here, but its import lines can: a name the module does not give is an
    ImportError on the machine, after the clone and before a single model comes down."""
    imports = _imports_from_code()

    assert imports, "Defter kendi kodunu import etmiyor"
    for module, names in imports:
        found = importlib.import_module(module)
        missing = [name for name in names if not hasattr(found, name)]
        assert missing == [], f"{module} bu adları vermiyor: {missing}"


def test_the_notebook_reaches_its_code_through_the_clone():
    """The module lives in the clone, which is not on the kernel's path until the notebook puts it
    there -- and it has to be there before the first import."""
    helpers = _cell("# === Shared helpers ===")
    path, first = helpers.find("sys.path.insert(0, APP_DIR)"), helpers.find("from colab.")

    assert -1 < path < first, "Yardımcılar hücresi klonu yola import'tan önce koymuyor"


def test_a_rerun_imports_the_code_it_just_cloned():
    """The clone cell deletes and clones the repo on every run, so a re-run picks up a push without a
    new runtime. Python keeps a module it imported for as long as the kernel lives: unless the cell
    drops it, a re-run clones the new code and keeps running the old."""
    assert "del sys.modules[" in _cell("# === Shared helpers ==="), \
        "Yardımcılar hücresi önceki koşunun modülünü bırakmıyor"


def test_the_notebook_defines_none_of_the_code_it_imports():
    """One home per function: a copy left in a cell would run instead of the tested one."""
    source = _source()
    names = [name for _module, names in _imports_from_code() for name in names]

    assert names, "Defter kendi kodunu import etmiyor"
    assert [name for name in names if f"def {name}(" in source] == [], \
        "Defter import ettiği kodu kendisi tanımlıyor"


def test_huggingface_files_come_down_through_hf_fetch():
    """hf_fetch is the path around HF's bridge. Without hf_xet installed, huggingface_hub goes back to
    the bridge with nothing but a log line, so installing it is half of the rule."""
    assert re.search(r"for [^\n]+ in hf_jobs:\n\s+hf_fetch\(", _cell("# === Target folders ===")), \
        "HF dosyaları hf_fetch ile inmiyor"
    assert re.search(r"pip install[^\n]*hf_xet", _source()), "Defter hf_xet'i kurmuyor"


def test_the_gated_files_are_probed_before_anything_comes_down():
    """A dead cookie heard after the open files came down costs their whole download; the 1 KB probe
    asks first."""
    cell = _cell("# === Target folders ===")
    probe, first = cell.find("civitai_probe("), cell.find("fetch(")

    assert -1 < probe < first, "Kapılı dosyalar indirmeden önce yoklanmıyor"
```

- [ ] **Adım 4: Dört satırı koş.**

- [ ] **Adım 5: Kırmızı commit** — iki test dosyası, spec ve bu plan.

## Beklenen kırmızı

`queen-editor` pytest'inde: modül testlerinin on ikisi `ModuleNotFoundError: No module named 'colab'`
ile *(fixture'da)*; dikiş testlerinin altısı defter henüz import etmediği için; ve `bdc683be`'den
beri kırmızı iki test. Öteki üç satır yeşil; başka hiçbir test kıpırdamaz.
