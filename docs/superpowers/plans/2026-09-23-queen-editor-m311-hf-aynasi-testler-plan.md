# Madde 311 — HF aynası, test turunun planı

> **Koşum:** bu oturumda, satır satır. Alt ajan yok *(CLAUDE.md, Gotchas)*.

**Hedef:** `civitai_fetch`'in aynayı önce denediğini, düşüşte çerezi isteyip yokladığını, Civitai'den
indirip aynaya yüklediğini söyleyen testler, ve defterin bunu kullandığını söyleyen üç test —
kırmızı.

**Yaklaşım:** 310'un sahteleri genişliyor: `huggingface_hub` artık tuttuğu dosyalarla bir ayna ve
yüklemeleri kaydeden bir `HfApi`; yoklama da bir sahte, çağrıldığı an kaç indirme koştuğunu
hatırlıyor.

**Araçlar:** pytest (`monkeypatch`, `tmp_path`, `capsys`).

**Spec:** [m311 test turu](../specs/2026-09-23-queen-editor-m311-hf-aynasi-testler-design.md)

## Her yere geçerli kurallar

- Test adları ve docstring'ler **İngilizce**, assert mesajları **Türkçe**.
- Testler dört satırla koşulur; `skip` / `xfail` yok. Bu turda kaynak kod ve defter değişmiyor.

---

## Görev 1: `civitai_fetch` testleri

**Dosyalar:** Değiştir: `queen-editor/backend/tests/test_colab_downloads.py` — sonuna.

**Arayüz — uygulama turunun vereceği:** `civitai_fetch(mirror, version_id, target_dir, filename,
label, cookie)`; aynadaki yol `f"{version_id}/{filename}"`; `civitai_probe`'u modülün ad alanından
çağırıyor; yüklemeyi `huggingface_hub.HfApi().upload_file(path_or_fileobj=…, path_in_repo=…,
repo_id=…)` ile yapıyor.

- [ ] **Adım 1: Sabitler ve iki sahte.**

```python
MIRROR = "Test468735/queen-editor-models"
COOKIE = "c" * 420


def _mirror(monkeypatch, held, *, upload_error=None):
    """Hugging Face with a mirror repo holding `held` ({path in repo: bytes}). A path it does not hold
    is answered the way HF answers, with a sentence naming it; uploads are remembered, or refused
    with `upload_error`."""
    uploads = []

    def hf_hub_download(repo_id, filename, *, local_dir=None, **_):
        if filename not in held:
            raise OSError(f"404 Client Error. Entry Not Found for url: "
                          f"https://huggingface.co/{repo_id}/resolve/main/{filename}")
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
```

- [ ] **Adım 2: Altı test.**

```python
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
```

## Görev 2: Defter testleri

**Dosyalar:** Değiştir: `queen-editor/backend/tests/test_notebook_installs_the_producer_groups.py`

- [ ] **Adım 1: Sil** — `test_the_cookie_is_only_demanded_by_the_groups_that_are_gated`,
  `test_the_gated_files_are_probed_before_anything_comes_down`.

- [ ] **Adım 2: Üç test.**

```python
def test_civitai_files_come_down_through_the_mirror():
    """Each gated file is looked up in the user's own Hugging Face repo first (madde 311)."""
    assert re.search(r"for [^\n]+ in civitai_jobs:\n\s+civitai_fetch\(HF_MIRROR, ",
                     _cell("# === Target folders ===")), "Civitai dosyaları aynadan geçmiyor"


def test_the_mirror_is_named_once_in_config():
    """A repo is named where the Drive folder is: in CONFIG, once."""
    assert re.search(r'^HF_MIRROR\s*=\s*"[\w.-]+/[\w.-]+"', _cell("# === CONFIG ==="), re.M), \
        "Ayna CONFIG'de adlanmıyor"
    assert len(re.findall(r"^HF_MIRROR\s*=", _source(), re.M)) == 1, \
        "Ayna birden çok yerde adlanıyor"


def test_config_does_not_demand_the_cookie():
    """Only a file that falls back to Civitai needs the cookie (madde 311). Demanded in CONFIG, it
    would stop a run whose files are all mirrored, for nothing."""
    assert "len(COOKIE_VALUE" not in _cell("# === CONFIG ==="), "CONFIG çerezi hâlâ baştan istiyor"
```

- [ ] **Adım 3: Dört satırı koş.**

- [ ] **Adım 4: Kırmızı commit** — iki test dosyası, spec ve bu plan.

## Beklenen kırmızı

`queen-editor` pytest'inde dokuz test: altı modül testi `civitai_fetch` olmadığı için, üç defter testi
defter henüz aynayı bilmediği için. Başka hiçbir test kıpırdamaz; öteki üç satır yeşil.
