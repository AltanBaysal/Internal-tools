# Madde 327 — Aynasız indirme, uygulama turunun planı

> **Koşum:** bu oturumda, satır satır. Alt ajan yok *(CLAUDE.md, Gotchas)*.

**Hedef:** `acf242e8`'in beş kırmızı testi yeşil, geri kalan her şey yeşil kalıyor.

**Spec:** [m327 uygulama turu](../specs/2026-09-24-queen-editor-m327-aynasiz-indirme-uygulama-design.md)

## Her yere geçerli kurallar

- Yorum ve docstring **İngilizce** ve yalnız *neden*; konsol cümlesi **Türkçe**.
- Kırmızı testlere dokunulmuyor; defter değişmiyor.

---

## Görev 1: `colab/downloads.py`

**Dosya:** Değiştir: `queen-editor/colab/downloads.py` — `_upload`'ın altı, `civitai_fetch`'in yerine.

- [ ] **Adım 1: Liste ve fonksiyon.**

```python
# Files on trial stay out of the mirror (madde 327): they come straight from Civitai and are never
# uploaded -- a file we may not keep has no business there. Keyed by file name, not by Civitai
# version: the version is the file's address, and addresses live in the notebook (FOUNDATION 9).
MIRRORLESS = set()


def civitai_fetch(mirror, version_id, target_dir, filename, label, cookie):
    """A Civitai file, from the user's Hugging Face mirror when it is there. When it is not -- or will
    not come down -- the mirror's own sentence is printed, the file comes from Civitai the way it
    always did, and it goes up to the mirror so the next run takes the fast road (madde 311). A file
    in MIRRORLESS skips the mirror both ways and comes straight from Civitai (madde 327). Either way
    the row is the download's; the upload has its own line. A file already in place asks nothing of
    anyone, the probe included."""
    path = f"{version_id}/{filename}"
    target = os.path.join(target_dir, filename)
    if os.path.exists(target):
        log(f"{label}: zaten var ({_settled(target, label, None)})")
        return
    mirrored = filename not in MIRRORLESS
    if mirrored:
        try:
            return hf_fetch(mirror, path, target_dir, filename, label)
        except RuntimeError as e:
            log(f"{label}: aynadan alınamadı, Civitai'den inecek — {e}", "WARN")
    else:
        log(f"{label}: aynası kapalı — Civitai'den aynasız iniyor (madde 327)")
    if len(cookie or "") <= 200:
        raise RuntimeError(
            f"❌ {label}: {'aynada yok' if mirrored else 'aynası kapalı'}, ve Civitai'den inmesi için "
            f"CIVITAI_COOKIE gerekiyor — Colab 🔑 Secrets'a 'CIVITAI_COOKIE' adıyla ekle: civitai.red → "
            f"giriş → F12 → Application → Cookies → __Secure-civ-token değeri (ES256 JWT)")
    civitai_probe(version_id, label, cookie)
    row = fetch(civitai_url(version_id), target_dir, filename, label, parallel=False,
                headers=cookie_header(cookie))
    if mirrored:
        _upload(mirror, path, target, label)
    return row
```

## Görev 2: Koşu ve yeşil commit

- [ ] **Adım 1: Dört satırı koş** — hepsi yeşil.
- [ ] **Adım 2: Yeşil commit** — kod, spec ve bu plan: `feat(m327): …`.
