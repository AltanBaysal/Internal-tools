# Madde 327 — Aynasız indirme, test turunun planı

> **Koşum:** bu oturumda, satır satır. Alt ajan yok *(CLAUDE.md, Gotchas)*.

**Hedef:** Aynası kapalı bir Civitai dosyasının aynaya hiç uğramadan Civitai'den indiğini, bunu
konsolda söylediğini, çerezsiz durduğunu ve öteki dosyalara dokunmadığını söyleyen beş test —
kırmızı.

**Yaklaşım:** 311'in sahteleri olduğu gibi: `_mirror`, `_transfer`, `_probe`. Aynasız dosyaların
listesi `MIRRORLESS` testte `monkeypatch.setattr` ile dosya adlarından bir kümeye kuruluyor; bugün o
ad olmadığı için `setattr` `AttributeError` veriyor.

**Araçlar:** pytest (`monkeypatch`, `tmp_path`, `capsys`).

**Spec:** [m327 test turu](../specs/2026-09-24-queen-editor-m327-aynasiz-indirme-testler-design.md)

## Her yere geçerli kurallar

- Test adları ve docstring'ler **İngilizce**, assert mesajları **Türkçe**.
- Testler dört satırla koşulur; `skip` / `xfail` yok. Bu turda kaynak kod ve defter değişmiyor.

---

## Görev 1: Beş test

**Dosya:** Değiştir: `queen-editor/backend/tests/test_colab_downloads.py` — sonuna.

**Arayüz — uygulama turunun vereceği:** `colab.downloads.MIRRORLESS`, Civitai dosya adlarının
listesi; `civitai_fetch`'in imzası değişmiyor. Bir dosya `filename in MIRRORLESS` ise aynası kapalı.

- [ ] **Adım 1: Testler.**

```python
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
```

## Görev 2: Koşu

- [ ] **Adım 1: Dört satırı koş.**
- [ ] **Adım 2: Kırmızı commit** — test dosyası, spec ve bu plan: `test(m327): …(red)`.

## Beklenen kırmızı

`queen-editor` pytest'inde beş test, hepsi `MIRRORLESS` olmadığı için —
`AttributeError: <module 'colab.downloads' …> has no attribute 'MIRRORLESS'`. Başka hiçbir test
kıpırdamaz; öteki üç satır yeşil.
